#!/usr/bin/env python3
"""Collect and drain sanitized TES operational field reports."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from typing import Any


VERSION = "0.3.86"
DESTINATION_REPO = "murillodutt/tilly-engineer-skills"
SCHEMA = "tes-field-report@2"
LEGACY_SCHEMAS = ("tes-field-report@1", "tilly-field-report@1")
FIELD_ROOT = Path(".tes/field-reports")
OUTBOX = FIELD_ROOT / "outbox.jsonl"
RECEIPTS = FIELD_ROOT / "receipts"
DISABLED = FIELD_ROOT / "DISABLED"
INSTALL_ID = FIELD_ROOT / "install_id"
LEGACY_FIELD_ROOT = Path(".tilly/field-reports")
BIN_HELPER = Path(".tes/bin/field_reports.py")
HOOK_MARKER = "TES_FIELD_REPORTS_PRE_PUSH"
MAX_ISSUE_BODY_CHARS = 48000
SIGNAL_STATUSES = {"FAIL", "BLOCKED", "DEGRADED", "NEEDS_REVIEW", "STALE_SOURCE"}
SUCCESS_INSTALL_EVENTS = {
    "install_adapter",
    "install_mcp",
    "tes_init",
}
CAPABILITY_SURFACES = {"adapter", "cortex", "field-reports", "installer", "mcp"}
SUMMARY_FACT_KEYS = (
    "adapter",
    "cloud_version",
    "duration_bucket",
    "failures",
    "helper_contract_status",
    "helpers_only",
    "legacy_retirement_required",
    "post_layer_zero_final_probe_status",
    "recommended_update_scope",
    "returncode",
    "route",
    "surface_count",
    "update_available",
    "update_reasons",
    "update_scope",
)
GIT_EXCLUDE_LINES = (
    ".tes/bin/*.bak-*",
    ".tes/bin/__pycache__/",
    "*.pyc",
    ".tes/field-reports/",
    ".tes/legacy-retirement/",
    ".tes/cortex/*.sqlite",
    ".tes/cortex/*.sqlite-*",
)

SAFE_SLUG = re.compile(r"[^a-zA-Z0-9_.:-]+")
ABSOLUTE_PATH = re.compile(r"(/Users|/home|/private|/var/folders|[A-Za-z]:\\)[^\s`\"')]+")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL = re.compile(r"https?://[^\s`\"')]+")
SECRET = re.compile(
    r"(?i)(api[_-]?key|authorization|bearer|credential|password|secret|token)\s*[:=]?\s*[A-Za-z0-9._:/+=-]+"
)
STACK_TRACE = re.compile(r"(?i)(traceback \(most recent call last\)|\bat .+:\d+:\d+|exception: .+)")
CODE_FENCE = re.compile(r"```")
GIT_REMOTE = re.compile(r"(?i)(github\.com[:/][^\s]+\.git|git@[^:\s]+:[^\s]+)")
BRANCH_NAME = re.compile(r"(?i)\b(branch|ref)\s*[:=]\s*[^\s]+")
PROHIBITED_KEY = re.compile(
    r"(?i)(api|auth|branch|code|command|content|diff|email|file|path|prompt|remote|secret|shell|stack|token|url)"
)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def file_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def root(target: Path) -> Path:
    return target / FIELD_ROOT


def outbox_path(target: Path) -> Path:
    return target / OUTBOX


def receipts_path(target: Path) -> Path:
    return target / RECEIPTS


def disabled_path(target: Path) -> Path:
    return target / DISABLED


def install_id_path(target: Path) -> Path:
    return target / INSTALL_ID


def legacy_root(target: Path) -> Path:
    return target / LEGACY_FIELD_ROOT


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return path.name


def safe_slug(value: str, default: str) -> str:
    slug = SAFE_SLUG.sub("-", value.strip()).strip("-._:")
    return slug[:64] if slug else default


def status_slug(value: str) -> str:
    return safe_slug(value.upper(), "UNKNOWN")


def field_reports_disabled(target: Path) -> bool:
    migrate_legacy_layout(target)
    return disabled_path(target).exists()


def merge_legacy_outbox(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    legacy_text = source.read_text(encoding="utf-8", errors="replace").strip()
    if legacy_text:
        current_text = destination.read_text(encoding="utf-8") if destination.exists() else ""
        prefix = current_text if current_text.endswith("\n") or not current_text else current_text + "\n"
        destination.write_text(prefix + legacy_text + "\n", encoding="utf-8")
    elif not destination.exists():
        destination.touch()
    source.unlink()


def move_legacy_file(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        source.unlink()
        return
    source.replace(destination)


def migrate_legacy_layout(target: Path) -> None:
    legacy = legacy_root(target)
    if not legacy.exists():
        return
    root(target).mkdir(parents=True, exist_ok=True)
    receipts_path(target).mkdir(parents=True, exist_ok=True)
    merge_legacy_outbox(legacy / "outbox.jsonl", outbox_path(target))
    move_legacy_file(legacy / "install_id", install_id_path(target))
    move_legacy_file(legacy / "DISABLED", disabled_path(target))
    legacy_receipts = legacy / "receipts"
    if legacy_receipts.exists():
        for receipt in sorted(legacy_receipts.glob("*.json")):
            destination = receipts_path(target) / receipt.name
            if destination.exists():
                destination = receipts_path(target) / f"legacy-{sha256_text(receipt.read_text(encoding='utf-8', errors='replace'))[:8]}-{receipt.name}"
            receipt.replace(destination)
        try:
            legacy_receipts.rmdir()
        except OSError:
            pass
    try:
        legacy.rmdir()
    except OSError:
        pass
    try:
        legacy.parent.rmdir()
    except OSError:
        pass


def ensure_layout(target: Path) -> None:
    migrate_legacy_layout(target)
    root(target).mkdir(parents=True, exist_ok=True)
    receipts_path(target).mkdir(parents=True, exist_ok=True)
    outbox_path(target).touch(exist_ok=True)


def ensure_install_id(target: Path) -> str:
    ensure_layout(target)
    path = install_id_path(target)
    if path.exists():
        value = path.read_text(encoding="utf-8").strip()
        if value:
            return safe_slug(value, "unknown-install")
    value = str(uuid.uuid4())
    path.write_text(value + "\n", encoding="utf-8")
    return value


def redaction_label(text: str) -> str:
    return f"redacted:{sha256_text(text)[:12]}"


def sanitize_key(key: str) -> str:
    raw = str(key).strip()
    if PROHIBITED_KEY.search(raw):
        return f"field_{sha256_text(raw)[:8]}"
    return safe_slug(raw.lower(), "field")


def sanitize_value(value: object) -> str:
    raw = str(value)
    if not raw:
        return ""
    if "\n" in raw or CODE_FENCE.search(raw) or STACK_TRACE.search(raw):
        return redaction_label(raw)
    sanitized = raw
    for pattern in (SECRET, EMAIL, URL, ABSOLUTE_PATH, GIT_REMOTE, BRANCH_NAME):
        sanitized = pattern.sub("[redacted]", sanitized)
    sanitized = sanitized.replace("`", "'").replace("|", "/").strip()
    if len(sanitized) > 160:
        return redaction_label(sanitized)
    if not sanitized:
        return "[redacted]"
    return sanitized


def sanitize_fact(key: object, value: object) -> tuple[str, str]:
    raw_key = str(key)
    safe_key = sanitize_key(raw_key)
    if PROHIBITED_KEY.search(raw_key):
        return safe_key, redaction_label(str(value))
    return safe_key, sanitize_value(value)


def parse_detail(items: list[str]) -> dict[str, str]:
    details: dict[str, str] = {}
    for item in items:
        key, sep, value = item.partition("=")
        if not sep:
            key, value = "note", item
        safe_key, safe_value = sanitize_fact(key, value)
        details[safe_key] = safe_value
    return details


def system_facts() -> dict[str, str]:
    return {
        "os": sanitize_value(platform.system() or "unknown"),
        "python": sanitize_value(platform.python_version()),
        "runtime": "python",
    }


def build_event(
    target: Path,
    event: str,
    status: str,
    surface: str = "unknown",
    trigger: str = "cli",
    duration_bucket: str | None = None,
    details: dict[str, object] | None = None,
) -> dict[str, object]:
    safe_details = dict(sanitize_fact(key, value) for key, value in (details or {}).items())
    if duration_bucket:
        safe_details["duration_bucket"] = sanitize_value(duration_bucket)
    return {
        "schema": SCHEMA,
        "tes_version": VERSION,
        "created_at": utc_stamp(),
        "install_id": ensure_install_id(target),
        "event": safe_slug(event, "unknown-event"),
        "status": status_slug(status),
        "surface": safe_slug(surface, "unknown"),
        "trigger": safe_slug(trigger, "cli"),
        "facts": {**system_facts(), **safe_details},
    }


def append_event(target: Path, event: dict[str, object]) -> None:
    ensure_layout(target)
    with outbox_path(target).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")


def record_event(
    target: Path,
    event: str,
    status: str,
    surface: str = "unknown",
    trigger: str = "cli",
    duration_bucket: str | None = None,
    details: dict[str, object] | None = None,
) -> dict[str, object]:
    target = target.expanduser().resolve()
    if field_reports_disabled(target):
        return {"version": VERSION, "status": "SKIP", "reason": "field reports disabled", "writes": []}
    payload = build_event(target, event, status, surface, trigger, duration_bucket, details)
    append_event(target, payload)
    ensure_git_exclude(target)
    return {
        "version": VERSION,
        "status": "PASS",
        "event": payload["event"],
        "outbox": rel(outbox_path(target), target),
        "writes": [rel(outbox_path(target), target)],
    }


def safe_record_event(
    target: Path,
    event: str,
    status: str,
    surface: str = "unknown",
    trigger: str = "cli",
    duration_bucket: str | None = None,
    details: dict[str, object] | None = None,
) -> None:
    try:
        record_event(target, event, status, surface, trigger, duration_bucket, details)
    except Exception:
        return


def read_outbox(target: Path) -> tuple[list[dict[str, object]], list[str]]:
    path = outbox_path(target)
    if not path.exists():
        return [], []
    events: list[dict[str, object]] = []
    failures: list[str] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            failures.append(f"invalid outbox json line: {idx}")
            continue
        if isinstance(item, dict):
            events.append(item)
        else:
            failures.append(f"invalid outbox payload line: {idx}")
    return events, failures


def sanitize_issue_text(text: str) -> str:
    sanitized = text
    for pattern in (SECRET, EMAIL, URL, ABSOLUTE_PATH, GIT_REMOTE, BRANCH_NAME, STACK_TRACE):
        sanitized = pattern.sub("[redacted]", sanitized)
    sanitized = sanitized.replace("```", "'''").replace("|", "/")
    return sanitized


def sanitize_issue_url(value: str) -> str:
    cleaned = value.strip().splitlines()[-1] if value.strip() else ""
    prefix = f"https://github.com/{DESTINATION_REPO}/issues/"
    if cleaned.startswith(prefix):
        suffix = cleaned.removeprefix(prefix)
        if suffix.isdigit():
            return cleaned
    return sanitize_value(cleaned)


def valid_issue_url(value: str) -> bool:
    prefix = f"https://github.com/{DESTINATION_REPO}/issues/"
    cleaned = value.strip()
    return cleaned.startswith(prefix) and cleaned.removeprefix(prefix).isdigit()


def facts_for(event: dict[str, object]) -> dict[str, object]:
    facts = event.get("facts")
    return facts if isinstance(facts, dict) else {}


def event_name(event: dict[str, object]) -> str:
    return sanitize_value(event.get("event", "unknown"))


def event_status(event: dict[str, object]) -> str:
    return status_slug(str(event.get("status", "UNKNOWN")))


def event_surface(event: dict[str, object]) -> str:
    return safe_slug(str(event.get("surface", "unknown")), "unknown")


def non_drain_events(events: list[dict[str, object]]) -> list[dict[str, object]]:
    return [event for event in events if event_name(event) != "field_reports.drain"]


def install_fingerprint(value: object) -> str:
    return f"install:{sha256_text(str(value))[:12]}"


def sorted_values(values: set[str], fallback: str = "none") -> str:
    return ", ".join(sorted(values)) if values else fallback


def count_by(events: list[dict[str, object]], getter: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in events:
        key = str(getter(event))
        counts[key] = counts.get(key, 0) + 1
    return counts


def rendered_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items())) or "none"


def truthy_text(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def compact_event_signature(event: dict[str, object]) -> dict[str, object]:
    facts = facts_for(event)
    return {
        "event": event_name(event),
        "status": event_status(event),
        "surface": event_surface(event),
        "schema": sanitize_value(event.get("schema", "unknown")),
        "tes_version": sanitize_value(event.get("tes_version", event.get("tilly_version", "unknown"))),
        "facts": {
            key: sanitize_value(facts.get(key, ""))
            for key in SUMMARY_FACT_KEYS
            if key in facts
        },
    }


def classify_report(events: list[dict[str, object]]) -> dict[str, object]:
    material = non_drain_events(events)
    statuses = count_by(events, event_status)
    surfaces = count_by(events, event_surface)
    names = count_by(material, event_name)

    failure_events = [
        f"{event_name(event)}:{event_status(event)}"
        for event in material
        if event_status(event) in SIGNAL_STATUSES
    ]
    routes = {
        sanitize_value(facts_for(event).get("route", ""))
        for event in material
        if facts_for(event).get("route")
    }
    adapters = {
        sanitize_value(facts_for(event).get("adapter", ""))
        for event in material
        if facts_for(event).get("adapter")
    }
    installed_versions = {
        sanitize_value(facts_for(event).get("installed_version", ""))
        for event in material
        if facts_for(event).get("installed_version")
    }
    cloud_versions = {
        sanitize_value(facts_for(event).get("cloud_version", ""))
        for event in material
        if facts_for(event).get("cloud_version")
    }
    schemas = {
        sanitize_value(event.get("schema", "unknown"))
        for event in material
        if event.get("schema")
    }
    version_drift = any(
        truthy_text(facts_for(event).get("update_available", "false"))
        or (
            bool(facts_for(event).get("cloud_version"))
            and str(facts_for(event).get("cloud_version")) != "unknown"
            and bool(facts_for(event).get("installed_version"))
            and str(facts_for(event).get("cloud_version")) != str(facts_for(event).get("installed_version"))
        )
        for event in material
    )
    helper_contract_failure = any(
        str(facts_for(event).get("helper_contract_status", "")).upper() == "FAIL"
        or str(facts_for(event).get("helper_contract_status", "")).upper() == "BLOCKED"
        for event in material
    )
    adapter_drift = any(
        str(facts_for(event).get("runtime_trigger_status", "")).upper() in {"DRIFT", "FAIL", "BLOCKED"}
        or (
            event_surface(event) == "adapter"
            and event_status(event) in {"FAIL", "BLOCKED", "DEGRADED", "NEEDS_REVIEW"}
        )
        for event in material
    )
    mcp_activation_failure = any(
        event_surface(event) == "mcp"
        and event_status(event) in {"FAIL", "BLOCKED", "DEGRADED", "NEEDS_REVIEW"}
        for event in material
    )
    legacy_signal = any(
        str(event.get("schema", "")) in LEGACY_SCHEMAS
        or "tilly_version" in event
        or truthy_text(facts_for(event).get("legacy_retirement_required", "false"))
        for event in material
    )
    install_signal = any(
        event_name(event) in SUCCESS_INSTALL_EVENTS
        and (event_status(event) == "INSTALLED" or event_surface(event) in {"adapter", "installer", "mcp"})
        for event in material
    )
    capability_signal = any(event_surface(event) in CAPABILITY_SURFACES for event in material)
    multi_surface_signal = len([surface for surface in surfaces if surface != "field-reports"]) >= 2
    cortex_batch_signal = (
        sum(1 for event in material if event_surface(event) == "cortex") >= 2
        or any(
            event_surface(event) == "cortex"
            and int(str(facts_for(event).get("surface_count", "0")) or "0") >= 2
            for event in material
        )
    )

    score = 0
    findings: list[str] = []
    report_class = "low-signal-heartbeat"

    if helper_contract_failure:
        score += 6
        report_class = "helper-contract-failure"
        findings.append("Helper contract failure requires Layer Zero or helper parity review.")
    if adapter_drift:
        score += 6
        report_class = "adapter-drift" if report_class == "low-signal-heartbeat" else report_class
        findings.append("Adapter/runtime trigger drift requires adapter-surface review.")
    if mcp_activation_failure:
        score += 6
        report_class = "mcp-activation-failure" if report_class == "low-signal-heartbeat" else report_class
        findings.append("MCP activation failure requires local config or helper inspection.")
    if failure_events:
        score += 5
        if report_class == "low-signal-heartbeat":
            report_class = "failure-or-blocker"
        findings.append("Failure or blocked events require review: " + ", ".join(failure_events[:6]))
    if version_drift:
        score += 4
        if report_class == "low-signal-heartbeat":
            report_class = "version-drift"
        findings.append(
            "Version drift observed: installed="
            + sorted_values(installed_versions)
            + ", cloud="
            + sorted_values(cloud_versions)
        )
    if legacy_signal:
        score += 3
        if report_class == "low-signal-heartbeat":
            report_class = "legacy-migration"
        findings.append("Legacy namespace or retirement signal observed.")
    if install_signal:
        score += 2
        if report_class == "low-signal-heartbeat":
            report_class = "installation-signal"
        findings.append("Install or update surface changed: " + rendered_counts(names))
    if cortex_batch_signal:
        score += 2
        if report_class == "low-signal-heartbeat":
            report_class = "cortex-certification"
        findings.append("Cortex certification batch observed.")
    if multi_surface_signal and capability_signal:
        score += 2
        if report_class == "low-signal-heartbeat":
            report_class = "multi-surface-operation"
        findings.append("Multiple TES surfaces reported in one drain.")

    if not findings:
        findings.append("Suppressed because the drain contained only successful low-signal heartbeat events.")

    actionability = "high" if score >= 4 else "medium" if score >= 2 else "low"
    fingerprint_payload = {
        "events": [compact_event_signature(event) for event in material],
        "report_class": report_class,
    }
    return {
        "actionability": actionability,
        "adapters": sorted(adapters),
        "cloud_versions": sorted(cloud_versions),
        "event_count": len(events),
        "findings": findings,
        "install_fingerprints": sorted({install_fingerprint(event.get("install_id", "unknown")) for event in material}),
        "installed_versions": sorted(installed_versions),
        "material_event_count": len(material),
        "report_class": report_class,
        "report_fingerprint": sha256_text(json.dumps(fingerprint_payload, sort_keys=True))[:16],
        "routes": sorted(routes),
        "schemas": sorted(schemas),
        "score": score,
        "status_counts": statuses,
        "surface_counts": surfaces,
        "suppressed": actionability == "low",
    }


def summary_values(summary: dict[str, object], key: str) -> str:
    value = summary.get(key)
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "none"
    return sanitize_value(value if value is not None else "none")


def build_issue_body(events: list[dict[str, object]], chunk_index: int, chunk_count: int) -> str:
    summary = classify_report(events)
    statuses = summary.get("status_counts") if isinstance(summary.get("status_counts"), dict) else {}
    surfaces = summary.get("surface_counts") if isinstance(summary.get("surface_counts"), dict) else {}
    lines = [
        f"<!-- {SCHEMA} -->",
        "TES Field Report",
        "",
        f"- Schema: {SCHEMA}",
        f"- TES version: {VERSION}",
        f"- Destination: {DESTINATION_REPO}",
        f"- Sent at: {utc_stamp()}",
        f"- Chunk: {chunk_index} of {chunk_count}",
        f"- Event count: {summary['event_count']}",
        f"- Material event count: {summary['material_event_count']}",
        f"- Report class: {summary['report_class']}",
        f"- Actionability: {summary['actionability']}",
        f"- Signal score: {summary['score']}",
        f"- Report fingerprint: {summary['report_fingerprint']}",
        "- Status counts: " + rendered_counts({str(key): int(value) for key, value in statuses.items()}),
        "- Surface counts: " + rendered_counts({str(key): int(value) for key, value in surfaces.items()}),
        "- Routes: " + summary_values(summary, "routes"),
        "- Adapters: " + summary_values(summary, "adapters"),
        "- Installed versions: " + summary_values(summary, "installed_versions"),
        "- Cloud versions: " + summary_values(summary, "cloud_versions"),
        "- Schemas seen: " + summary_values(summary, "schemas"),
        "- Install fingerprints: " + summary_values(summary, "install_fingerprints"),
        "",
        "Actionable findings",
    ]
    lines.extend(f"- {sanitize_value(finding)}" for finding in summary.get("findings", []))
    lines.extend([
        "",
        "Events",
    ])
    for event in events:
        facts = facts_for(event)
        fact_bits = ", ".join(
            f"{sanitize_key(str(key))}={sanitize_value(value)}"
            for key, value in sorted(facts.items())
        )
        lines.append(
            "- "
            + f"time={sanitize_value(event.get('created_at', 'unknown'))}, "
            + f"install_fp={install_fingerprint(event.get('install_id', 'unknown'))}, "
            + f"event={sanitize_value(event.get('event', 'unknown'))}, "
            + f"status={sanitize_value(event.get('status', 'UNKNOWN'))}, "
            + f"surface={sanitize_value(event.get('surface', 'unknown'))}, "
            + f"trigger={sanitize_value(event.get('trigger', 'cli'))}, "
            + f"facts={fact_bits}"
        )
    return sanitize_issue_text("\n".join(lines).strip() + "\n")


def chunk_events(events: list[dict[str, object]]) -> list[list[dict[str, object]]]:
    chunks: list[list[dict[str, object]]] = []
    current: list[dict[str, object]] = []
    for event in events:
        trial = [*current, event]
        body = build_issue_body(trial, len(chunks) + 1, 1)
        if current and len(body) > MAX_ISSUE_BODY_CHARS:
            chunks.append(current)
            current = [event]
        else:
            current = trial
    if current:
        chunks.append(current)
    return chunks


def gh_issue_create(title: str, body: str, env: dict[str, str] | None = None) -> tuple[bool, str]:
    gh = shutil.which("gh", path=(env or os.environ).get("PATH"))
    if not gh:
        return False, "gh unavailable"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        handle.write(body)
        body_file = handle.name
    try:
        result = subprocess.run(
            ["gh", "issue", "create", "--repo", DESTINATION_REPO, "--title", title, "--body-file", body_file],
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )
    finally:
        Path(body_file).unlink(missing_ok=True)
    if result.returncode != 0:
        return False, "gh issue create failed"
    output = result.stdout.strip() or result.stderr.strip()
    issue_url = sanitize_issue_url(output)
    if not valid_issue_url(issue_url):
        return False, "gh issue create returned unsafe output"
    return True, issue_url


def write_receipt(target: Path, issue_url: str, events: list[dict[str, object]], body: str, chunk: int) -> str:
    receipts_path(target).mkdir(parents=True, exist_ok=True)
    summary = classify_report(events)
    payload = {
        "actionability": summary.get("actionability"),
        "issue_url": sanitize_issue_url(issue_url),
        "event_count": len(events),
        "payload_sha256": sha256_text(body),
        "report_class": summary.get("report_class"),
        "report_fingerprint": summary.get("report_fingerprint"),
        "sent_at": utc_stamp(),
    }
    path = receipts_path(target) / f"{file_stamp()}-{chunk:02d}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return rel(path, target)


def write_suppression_receipt(target: Path, events: list[dict[str, object]], summary: dict[str, object]) -> str:
    receipts_path(target).mkdir(parents=True, exist_ok=True)
    payload = {
        "actionability": summary.get("actionability"),
        "event_count": len(events),
        "reason": "low-signal-heartbeat",
        "report_class": summary.get("report_class"),
        "report_fingerprint": summary.get("report_fingerprint"),
        "sent_at": utc_stamp(),
        "suppressed": True,
    }
    path = receipts_path(target) / f"{file_stamp()}-suppressed.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return rel(path, target)


def write_transport_receipt(
    target: Path,
    outcome: str,
    reason: str,
    events: list[dict[str, object]] | None = None,
) -> str:
    receipts_path(target).mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "event_count": len(events or []),
        "outcome": outcome,
        "reason": sanitize_value(reason),
        "sent_at": utc_stamp(),
    }
    if events:
        summary = classify_report(events)
        payload.update(
            {
                "actionability": summary.get("actionability"),
                "report_class": summary.get("report_class"),
                "report_fingerprint": summary.get("report_fingerprint"),
            }
        )
    path = receipts_path(target) / f"{file_stamp()}-{safe_slug(outcome, 'transport')}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return rel(path, target)


def drain(target: Path, trigger: str = "manual", env: dict[str, str] | None = None) -> dict[str, object]:
    target = target.expanduser().resolve()
    if field_reports_disabled(target):
        return {
            "version": VERSION,
            "status": "SKIP",
            "transport_state": "disabled",
            "reason": "field reports disabled",
            "writes": [],
        }

    ensure_layout(target)
    events, failures = read_outbox(target)
    if events:
        append_event(
            target,
            build_event(
                target,
                "field_reports.drain",
                "PASS",
                "field-reports",
                trigger,
                details={"pending_before": len(events)},
            ),
        )
        events, more_failures = read_outbox(target)
        failures.extend(more_failures)
    if failures:
        receipt = write_transport_receipt(target, "invalid-outbox", "outbox contains invalid records", events)
        return {
            "version": VERSION,
            "status": "BLOCKED",
            "transport_state": "invalid",
            "reason": "outbox contains invalid records",
            "failures": failures,
            "receipt": receipt,
            "writes": [receipt],
        }
    if not events:
        return {
            "version": VERSION,
            "status": "PASS",
            "transport_state": "empty",
            "pending": 0,
            "writes": [],
        }

    summary = classify_report(events)
    if summary.get("suppressed"):
        receipt_path = write_suppression_receipt(target, events, summary)
        outbox_path(target).write_text("", encoding="utf-8")
        return {
            "version": VERSION,
            "status": "PASS",
            "transport_state": "suppressed",
            "pending": 0,
            "suppressed": True,
            "reason": "low-signal-heartbeat",
            "receipt": receipt_path,
            "writes": [rel(outbox_path(target), target), receipt_path],
        }

    chunks = chunk_events(events)
    issue_urls: list[str] = []
    receipt_paths: list[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        body = build_issue_body(chunk, idx, len(chunks))
        title = f"TES Field Report {datetime.now(timezone.utc).strftime('%Y-%m-%d')} ({idx}/{len(chunks)})"
        ok, value = gh_issue_create(title, body, env=env)
        if not ok:
            receipt = write_transport_receipt(target, "transport-blocked", value, events)
            return {
                "version": VERSION,
                "status": "BLOCKED",
                "transport_state": "blocked",
                "reason": value,
                "pending": len(events),
                "receipt": receipt,
                "writes": [receipt],
            }
        issue_urls.append(value)
        receipt_paths.append(write_receipt(target, value, chunk, body, idx))

    outbox_path(target).write_text("", encoding="utf-8")
    return {
        "version": VERSION,
        "status": "PASS",
        "transport_state": "sent",
        "pending": 0,
        "issues": issue_urls,
        "receipts": receipt_paths,
        "writes": [rel(outbox_path(target), target), *receipt_paths],
    }


def ensure_git_exclude(target: Path) -> str | None:
    info = target / ".git/info"
    if not info.exists():
        return None
    exclude = info / "exclude"
    exclude.touch(exist_ok=True)
    text = exclude.read_text(encoding="utf-8")
    seen: set[str] = set()
    lines: list[str] = []
    for line in text.splitlines():
        if line in GIT_EXCLUDE_LINES:
            if line in seen:
                continue
            seen.add(line)
        lines.append(line)
    missing = [line for line in GIT_EXCLUDE_LINES if line not in seen]
    body = "\n".join([*lines, *missing]).rstrip() + "\n"
    if body != text:
        exclude.write_text(body, encoding="utf-8")
    return rel(exclude, target)


def copy_helper(target: Path) -> str:
    destination = target / BIN_HELPER
    destination.parent.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve()
    if source != destination.resolve():
        shutil.copy2(source, destination)
    return rel(destination, target)


def install_hook(target: Path) -> dict[str, object]:
    target = target.expanduser().resolve()
    git_dir = target / ".git"
    if not git_dir.exists() or not git_dir.is_dir():
        return {"version": VERSION, "status": "BLOCKED", "reason": "target is not a Git repository", "writes": []}

    ensure_layout(target)
    install_id = ensure_install_id(target)
    helper = copy_helper(target)
    exclude = ensure_git_exclude(target)
    hooks = git_dir / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "pre-push"
    backup_rel: str | None = None
    backup_shell = ""
    if hook.exists():
        current = hook.read_text(encoding="utf-8", errors="replace")
        if HOOK_MARKER not in current:
            backup = hook.with_name(f"pre-push.before-tes-{file_stamp()}")
            shutil.copy2(hook, backup)
            backup.chmod(0o755)
            backup_rel = rel(backup, target)
            backup_shell = f"""
BACKUP_HOOK=".git/hooks/{backup.name}"
if [ -f "$BACKUP_HOOK" ]; then
  if [ -x "$BACKUP_HOOK" ]; then
    "$BACKUP_HOOK" "$@"
  else
    sh "$BACKUP_HOOK" "$@"
  fi
  rc=$?
  if [ "$rc" -ne 0 ]; then
    exit "$rc"
  fi
fi
"""

    hook_text = f"""#!/bin/sh
# {HOOK_MARKER}
set -u
{backup_shell}
if [ -f ".tes/bin/field_reports.py" ]; then
  python3 ".tes/bin/field_reports.py" drain --target . --trigger pre-push >/dev/null 2>&1 || true
elif [ -f "scripts/field_reports.py" ]; then
  python3 "scripts/field_reports.py" drain --target . --trigger pre-push >/dev/null 2>&1 || true
fi
exit 0
"""
    hook.write_text(hook_text, encoding="utf-8")
    hook.chmod(0o755)

    writes = [helper, rel(hook, target), rel(outbox_path(target), target), rel(install_id_path(target), target)]
    if exclude:
        writes.append(exclude)
    if backup_rel:
        writes.append(backup_rel)
    return {
        "version": VERSION,
        "status": "PASS",
        "install_id": install_id,
        "hook": rel(hook, target),
        "backup": backup_rel,
        "writes": writes,
    }


def status(target: Path) -> dict[str, object]:
    target = target.expanduser().resolve()
    ensure_layout(target)
    events, failures = read_outbox(target)
    receipts = sorted(receipts_path(target).glob("*.json")) if receipts_path(target).exists() else []
    last_receipt = rel(receipts[-1], target) if receipts else None
    return {
        "version": VERSION,
        "status": "PASS" if not failures else "BLOCKED",
        "disabled": field_reports_disabled(target),
        "pending": len(events),
        "last_receipt": last_receipt,
        "outbox": rel(outbox_path(target), target),
        "failures": failures,
        "writes": [],
    }


def disable(target: Path) -> dict[str, object]:
    target = target.expanduser().resolve()
    ensure_layout(target)
    disabled_path(target).write_text("TES Field Reports disabled by local user intent.\n", encoding="utf-8")
    ensure_git_exclude(target)
    return {"version": VERSION, "status": "PASS", "disabled": True, "writes": [rel(disabled_path(target), target)]}


def enable(target: Path) -> dict[str, object]:
    target = target.expanduser().resolve()
    disabled_path(target).unlink(missing_ok=True)
    ensure_layout(target)
    ensure_install_id(target)
    ensure_git_exclude(target)
    return {"version": VERSION, "status": "PASS", "disabled": False, "writes": [rel(outbox_path(target), target)]}


def self_test() -> dict[str, object]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-field-reports-") as tempdir:
        target = Path(tempdir)
        subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)

        legacy = legacy_root(target)
        (legacy / "receipts").mkdir(parents=True)
        (legacy / "install_id").write_text("legacy-install-id\n", encoding="utf-8")
        (legacy / "receipts/legacy.json").write_text('{"issue_url":"legacy"}\n', encoding="utf-8")
        hook_result = install_hook(target)
        if legacy.exists():
            failures.append("install-hook must migrate legacy .tilly field reports state")
        if install_id_path(target).read_text(encoding="utf-8").strip() != "legacy-install-id":
            failures.append("legacy install_id must be preserved during migration")
        if not (receipts_path(target) / "legacy.json").exists():
            failures.append("legacy receipts must be moved into .tes")
        for relpath in (".tes/bin/field_reports.py", ".tes/field-reports/outbox.jsonl", ".git/hooks/pre-push"):
            if not (target / relpath).exists():
                failures.append(f"missing installed path: {relpath}")
        if hook_result["status"] != "PASS":
            failures.append("install-hook did not pass in a Git fixture")
        installed = target / "installed-helper"
        installed.mkdir()
        subprocess.run(["git", "init"], cwd=installed, text=True, capture_output=True, check=False)
        installed_helper = installed / BIN_HELPER
        installed_helper.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(__file__).resolve(), installed_helper)
        installed_result = subprocess.run(
            [sys.executable, str(installed_helper), "install-hook", "--target", str(installed), "--json-only"],
            cwd=installed,
            text=True,
            capture_output=True,
            check=False,
        )
        if installed_result.returncode != 0:
            failures.append("installed field_reports helper install-hook must be idempotent")
            failures.extend(installed_result.stdout.splitlines())
            failures.extend(installed_result.stderr.splitlines())
        exclude_text = (target / ".git/info/exclude").read_text(encoding="utf-8")
        for line in GIT_EXCLUDE_LINES:
            if line not in exclude_text.splitlines():
                failures.append(f"missing local git hygiene exclude: {line}")
        with (target / ".git/info/exclude").open("a", encoding="utf-8") as handle:
            handle.write("\n" + "\n".join(GIT_EXCLUDE_LINES[:3]) + "\n")
        ensure_git_exclude(target)
        deduped_exclude = (target / ".git/info/exclude").read_text(encoding="utf-8").splitlines()
        for line in GIT_EXCLUDE_LINES[:3]:
            if deduped_exclude.count(line) != 1:
                failures.append(f"local git hygiene must deduplicate exclude: {line}")
        for relpath in (
            ".tes/bin/cortex.py.bak-20260507T000000Z",
            ".tes/bin/__pycache__/field_reports.cpython-314.pyc",
            ".tes/field-reports/probe.jsonl",
            ".tes/legacy-retirement/backup.json",
            ".tes/cortex/recall.sqlite",
            ".tes/cortex/semantic.sqlite-wal",
            "root.pyc",
        ):
            probe = target / relpath
            probe.parent.mkdir(parents=True, exist_ok=True)
            probe.write_text("probe\n", encoding="utf-8")
            ignored = subprocess.run(["git", "check-ignore", relpath], cwd=target, text=True, capture_output=True, check=False)
            if ignored.returncode != 0:
                failures.append(f"local git hygiene did not ignore: {relpath}")
        helper_ignored = subprocess.run(
            ["git", "check-ignore", ".tes/bin/field_reports.py"],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
        )
        if helper_ignored.returncode == 0:
            failures.append("local git hygiene must not ignore installed helper .tes/bin/field_reports.py")

        record_event(
            target,
            "install_adapter",
            "FAIL",
            "adapter",
            "self-test",
            details={
                "unsafe_path": "/Users/private/project/secret.py",
                "unsafe_email": "person@example.com",
                "unsafe_token": "token=abc123",
                "unsafe_url": "https://private.example.test/repo",
                "unsafe_stack": "Traceback (most recent call last):\nFile x",
                "returncode": 1,
            },
        )
        events, event_failures = read_outbox(target)
        failures.extend(event_failures)
        if len(events) != 1:
            failures.append("capture must append exactly one event before drain")

        disabled = disable(target)
        skipped = record_event(target, "cortex.verify", "PASS", "cortex", "self-test")
        skipped_drain = drain(target, "self-test")
        if disabled["status"] != "PASS" or skipped["status"] != "SKIP" or skipped_drain["status"] != "SKIP":
            failures.append("disable must stop collection and drain")
        enabled = enable(target)
        if enabled["status"] != "PASS" or field_reports_disabled(target):
            failures.append("enable must remove the disabled sentinel")

        fake_bin = target / "fake-bin"
        fake_bin.mkdir()
        body_capture = target / "issue-body.txt"
        fake_gh = fake_bin / "gh"
        fake_gh.write_text(
            """#!/bin/sh
body=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "--body-file" ]; then
    shift
    body="$1"
  fi
  shift
done
cp "$body" "$GH_BODY_CAPTURE"
echo "https://github.com/murillodutt/tilly-engineer-skills/issues/999"
""",
            encoding="utf-8",
        )
        fake_gh.chmod(0o755)
        env = {**os.environ, "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}", "GH_BODY_CAPTURE": str(body_capture)}
        hook_run = subprocess.run(
            [str(target / ".git/hooks/pre-push")],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )
        if hook_run.returncode != 0:
            failures.append(f"pre-push hook must not fail: {hook_run.returncode}")
        if outbox_path(target).read_text(encoding="utf-8").strip():
            failures.append("pre-push drain must clear outbox after confirmed issue")
        issue_receipts = sorted(
            receipt
            for receipt in receipts_path(target).glob("*.json")
            if receipt.name[0].isdigit()
        )
        if not issue_receipts:
            failures.append("drain must write a receipt")
        else:
            receipt = json.loads(issue_receipts[-1].read_text(encoding="utf-8"))
            if not str(receipt.get("issue_url", "")).endswith("/issues/999"):
                failures.append("receipt must preserve the confirmed issue URL")
        body = body_capture.read_text(encoding="utf-8") if body_capture.exists() else ""
        if f"<!-- {SCHEMA} -->" not in body:
            failures.append("issue body must carry the field report schema marker")
        if f"- Schema: {SCHEMA}" not in body:
            failures.append("issue body must carry the visible field report schema")
        for required in ("Actionable findings", "Report class:", "Actionability:", "Report fingerprint:", "install_fp="):
            if required not in body:
                failures.append(f"issue body must carry signal quality field: {required}")
        for forbidden in ("```", "|", "/Users", "person@example.com", "abc123", "https://private", "Traceback"):
            if forbidden in body:
                failures.append(f"issue body leaked prohibited token: {forbidden}")

        quiet_target = target / "quiet-heartbeat"
        quiet_target.mkdir()
        subprocess.run(["git", "init"], cwd=quiet_target, text=True, capture_output=True, check=False)
        install_hook(quiet_target)
        record_event(
            quiet_target,
            "tes_update",
            "PASS",
            "installer",
            "self-test",
            details={
                "cloud_version": "unknown",
                "installed_version": VERSION,
                "route": "codex",
                "surface_count": 1,
                "update_available": False,
            },
        )
        quiet_drain = drain(quiet_target, "self-test", env={**os.environ, "PATH": str(quiet_target / "missing-gh")})
        if quiet_drain.get("status") != "PASS" or quiet_drain.get("suppressed") is not True:
            failures.append("low-signal update heartbeat must be suppressed instead of opening an issue")
        if outbox_path(quiet_target).read_text(encoding="utf-8").strip():
            failures.append("suppressed low-signal heartbeat must clear outbox")
        quiet_receipts = sorted(receipts_path(quiet_target).glob("*suppressed.json"))
        if not quiet_receipts:
            failures.append("suppressed low-signal heartbeat must write a suppression receipt")

        record_event(target, "cortex.audit", "FAIL", "cortex", "self-test", details={"returncode": 2})
        python_only = target / "python-only-bin"
        python_only.mkdir()
        (python_only / "python3").symlink_to(sys.executable)
        missing_env = {**os.environ, "PATH": str(python_only)}
        hook_missing = subprocess.run(
            [str(target / ".git/hooks/pre-push")],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
            env=missing_env,
        )
        if hook_missing.returncode != 0:
            failures.append("missing gh pre-push hook must not block")
        missing_gh = drain(target, "self-test", env=missing_env)
        if missing_gh["status"] != "BLOCKED":
            failures.append("missing gh must return BLOCKED")
        if not outbox_path(target).read_text(encoding="utf-8").strip():
            failures.append("missing gh must keep outbox pending")

        legacy_target = target / "legacy-status"
        legacy_target.mkdir()
        legacy_status_root = legacy_root(legacy_target)
        legacy_status_root.mkdir(parents=True)
        (legacy_status_root / "outbox.jsonl").write_text(
            json.dumps({"schema": SCHEMA, "event": "legacy", "status": "PASS"}) + "\n",
            encoding="utf-8",
        )
        legacy_status = status(legacy_target)
        if legacy_status.get("pending") != 1:
            failures.append("status must read migrated legacy outbox entries")
        if legacy_root(legacy_target).exists():
            failures.append("status must remove migrated legacy field reports root")

    return {"version": VERSION, "status": "PASS" if not failures else "FAIL", "failures": failures}


def print_result(result: dict[str, object], label: str, json_only: bool = False) -> int:
    print(json.dumps(result, indent=2, sort_keys=True))
    status_value = str(result.get("status", "FAIL"))
    if not json_only:
        print(f"[field-reports] {status_value}")
    if status_value == "FAIL":
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=("capture", "drain", "status", "disable", "enable", "install-hook"))
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--event")
    parser.add_argument("--status")
    parser.add_argument("--surface", default="unknown")
    parser.add_argument("--trigger", default="cli")
    parser.add_argument("--duration-bucket")
    parser.add_argument("--detail", action="append", default=[])
    parser.add_argument("--json-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return print_result(self_test(), "self-test", args.json_only)
    if args.command == "capture":
        if not args.event or not args.status:
            parser.error("capture requires --event and --status")
        result = record_event(
            args.target,
            args.event,
            args.status,
            args.surface,
            args.trigger,
            args.duration_bucket,
            parse_detail(args.detail),
        )
    elif args.command == "drain":
        result = drain(args.target, args.trigger)
    elif args.command == "status":
        result = status(args.target)
    elif args.command == "disable":
        result = disable(args.target)
    elif args.command == "enable":
        result = enable(args.target)
    elif args.command == "install-hook":
        result = install_hook(args.target)
    else:
        parser.error("command is required unless --self-test is used")
    return print_result(result, str(args.command), args.json_only)


if __name__ == "__main__":
    sys.exit(main())
