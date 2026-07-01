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
import shlex
import shutil
import subprocess
import sys
import tempfile
import uuid
from typing import Any

import scope_contract


VERSION = "0.3.255"
DESTINATION_REPO = "murillodutt/tilly-engineer-skills"
DEFAULT_OUTBOX_PENDING_THRESHOLD = 30
SCHEMA = "tes-field-report@2"
LEGACY_SCHEMAS = ("tes-field-report@1", "tilly-field-report@1")
FIELD_ROOT = Path(".tes/field-reports")
OUTBOX = FIELD_ROOT / "outbox.jsonl"
RECEIPTS = FIELD_ROOT / "receipts"
DISABLED = FIELD_ROOT / "DISABLED"
INSTALL_ID = FIELD_ROOT / "install_id"
LEGACY_FIELD_ROOT = Path(".tilly/field-reports")
BIN_HELPER = Path(".tes/bin/field_reports.py")
SCOPE_HELPER = Path(".tes/bin/scope_contract.py")
HOOK_MARKER = "TES_FIELD_REPORTS_PRE_PUSH"
# Strict pre-commit gate marker. The canary_admission_oracle.precommit_evidence
# contract recognizes this wrapper only when one of its gate commands resolves in
# the installed target; marker/token presence alone is never enforcement proof.
PRECOMMIT_MARKER = "TES_STRICT_PRE_COMMIT"
CANONICAL_DISCIPLINE_ORACLE = ".agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py"
CLAUDE_DISCIPLINE_ORACLE = ".claude/skills/tes-engineering-discipline/scripts/discipline_oracle.py"
BACKUP_HOOK_RE = re.compile(r"^BACKUP_HOOK=(?P<value>.+)$", re.MULTILINE)
BACKUP_PRECOMMIT_RE = re.compile(r"^BACKUP_PRECOMMIT=(?P<value>.+)$", re.MULTILINE)
GIT_ENV_BLOCKLIST = {
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_DIR",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_PREFIX",
    "GIT_WORK_TREE",
}

# Deterministic hook-manager selection (ceiling decision, never random).
# Priority: an existing manager config is respected first (defer); otherwise
# husky for Node/TS/npm-first trees, pre-commit when .pre-commit-config.yaml is
# present (Python/data/tooling), lefthook as the polyglot/monorepo default, and
# Makefile/CI only as a fallback integrator — never the sole local proof when
# Git hooks are possible. Mechanics verified against upstream docs:
#   - lefthook writes wrappers into .git/hooks (lefthook.dev)
#   - husky sets core.hooksPath=.husky/_ (typicode.github.io/husky)
#   - pre-commit installs via --hook-type into .git/hooks (pre-commit.com)
HOOK_MANAGER_LEFTHOOK = "lefthook"
HOOK_MANAGER_HUSKY = "husky"
HOOK_MANAGER_PRECOMMIT = "pre-commit"
HOOK_MANAGER_NATIVE = "git-native"
MAX_ISSUE_BODY_CHARS = 48000
SIGNAL_STATUSES = {"FAIL", "BLOCKED", "DEGRADED", "NEEDS_REVIEW", "STALE_SOURCE"}
SUCCESS_INSTALL_EVENTS = {
    "install_adapter",
    "install_mcp",
    "tes_init",
}
CAPABILITY_SURFACES = {"adapter", "cortex", "field-reports", "installer", "mcp"}
OWNER_SURFACE_BY_CLASS = {
    "adapter-drift": "adapter",
    "cortex-certification": "cortex",
    "failure-or-blocker": "maintainer-triage",
    "helper-contract-failure": "installer",
    "installation-signal": "installer",
    "legacy-migration": "legacy-retirement",
    "low-signal-heartbeat": "none",
    "mcp-activation-failure": "mcp",
    "multi-surface-operation": "maintainer-triage",
    "version-drift": "release",
}


def isolated_git_env(overrides: dict[str, str] | None = None) -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if key not in GIT_ENV_BLOCKLIST}
    if overrides:
        env.update(overrides)
    return env


NEXT_ACTION_BY_CLASS = {
    "adapter-drift": "review adapter materialization and trigger parity",
    "cortex-certification": "review Cortex certification batch evidence",
    "failure-or-blocker": "triage failing surface and reproduce with a neutral fixture",
    "helper-contract-failure": "repair Layer Zero helper contract before adapter convergence",
    "installation-signal": "correlate install signal with installer certification",
    "legacy-migration": "run legacy retirement review before clean certification",
    "low-signal-heartbeat": "suppress locally and keep receipt",
    "mcp-activation-failure": "repair project-scoped MCP config or helper route",
    "multi-surface-operation": "split findings by owner surface and certify each gate",
    "version-drift": "review update scope and release identity",
}
PRODUCT_CLASSES_BY_CLASS = {
    "adapter-drift": ("ADAPTER_DRIFT",),
    "cortex-certification": ("CERTIFICATION_GAP",),
    "failure-or-blocker": ("CERTIFICATION_GAP", "PRODUCT_BUG"),
    "helper-contract-failure": ("CERTIFICATION_GAP", "PRODUCT_BUG"),
    "installation-signal": ("CERTIFICATION_GAP",),
    "legacy-migration": ("PRODUCT_BUG",),
    "low-signal-heartbeat": ("LOW_SIGNAL_SUPPRESSED",),
    "mcp-activation-failure": ("CERTIFICATION_GAP",),
    "multi-surface-operation": ("CERTIFICATION_GAP",),
    "version-drift": ("RELEASE_HYGIENE",),
}
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
    "certification_status",
    "installed_certification_status",
    "update_available",
    "update_reasons",
    "update_scope",
)
GIT_EXCLUDE_LINES = (
    ".tes/bin/*.bak-*",
    ".tes/bin/__pycache__/",
    "*.pyc",
    ".tes/field-reports/",
    ".tes/checkpoints/",
    ".tes/mantra-gates/",
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
SYNTHETIC_PRIVATE_PATH = "/" + "Users/private/project/" + "sec" + "ret.py"
SYNTHETIC_EMAIL = "person" + "@example.com"
SYNTHETIC_SECRET_VALUE = "abc" + "123"
SYNTHETIC_SECRET_ASSIGNMENT = "token=" + SYNTHETIC_SECRET_VALUE
SYNTHETIC_PRIVATE_URL = "https://" + "private." + "example.test/repo"
SYNTHETIC_USER_PREFIX = "/" + "Users"
SYNTHETIC_PRIVATE_URL_PREFIX = "https://" + "private"


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
    raw_details = details or {}
    safe_details = dict(sanitize_fact(key, value) for key, value in (details or {}).items())
    if duration_bucket:
        safe_details["duration_bucket"] = sanitize_value(duration_bucket)
    created_at = utc_stamp()
    scope_result = scope_contract.normalize_scope(
        target,
        adapter=raw_details.get("adapter", surface),
        agent=trigger,
        parent_agent=raw_details.get("parent_agent"),
        run=raw_details.get("run"),
        source="field-reports",
        evidence_ref=raw_details.get("evidence_ref", ".tes/field-reports/outbox.jsonl"),
        timestamp=created_at,
        status=status_slug(status),
    )
    scope_status = str(scope_result.get("status", "FAIL"))
    return {
        "schema": SCHEMA,
        "tes_version": VERSION,
        "created_at": created_at,
        "install_id": ensure_install_id(target),
        "event": safe_slug(event, "unknown-event"),
        "status": status_slug(status),
        "surface": safe_slug(surface, "unknown"),
        "trigger": safe_slug(trigger, "cli"),
        "scope": scope_result.get("scope", {}),
        "scope_status": scope_status,
        "scope_failures": [sanitize_value(item) for item in scope_result.get("failures", [])],
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
    if payload.get("scope_status") != "PASS":
        return {
            "version": VERSION,
            "status": "BLOCKED",
            "reason": "invalid scope",
            "failures": payload.get("scope_failures", []),
            "writes": [],
        }
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
    severity = "critical" if any(status in statuses for status in ("BLOCKED", "FAIL")) and score >= 6 else actionability
    owner_surface = OWNER_SURFACE_BY_CLASS.get(report_class, "maintainer-triage")
    certification_impact = (
        "none"
        if report_class == "low-signal-heartbeat"
        else "blocks-clean-pass"
        if any(status in statuses for status in ("BLOCKED", "FAIL", "NEEDS_REVIEW", "DEGRADED"))
        else "partial-certification"
        if score >= 2
        else "monitor-only"
    )
    fingerprint_payload = {
        "events": [compact_event_signature(event) for event in material],
        "report_class": report_class,
        "owner_surface": owner_surface,
    }
    dedupe_fingerprint = sha256_text(json.dumps(fingerprint_payload, sort_keys=True))[:16]
    product_classes = PRODUCT_CLASSES_BY_CLASS.get(report_class, ("PRODUCT_BUG",))
    return {
        "actionability": actionability,
        "adapters": sorted(adapters),
        "cloud_versions": sorted(cloud_versions),
        "certification_impact": certification_impact,
        "dedupe_fingerprint": dedupe_fingerprint,
        "event_count": len(events),
        "findings": findings,
        "install_fingerprints": sorted({install_fingerprint(event.get("install_id", "unknown")) for event in material}),
        "installed_versions": sorted(installed_versions),
        "material_event_count": len(material),
        "next_action": NEXT_ACTION_BY_CLASS.get(report_class, "triage sanitized operational facts"),
        "owner_surface": owner_surface,
        "privacy_state": "sanitized",
        "product_class": report_class,
        "product_classes": list(product_classes),
        "report_class": report_class,
        "report_fingerprint": dedupe_fingerprint,
        "routes": sorted(routes),
        "schemas": sorted(schemas),
        "score": score,
        "severity": severity,
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
        f"- Severity: {summary['severity']}",
        f"- Product class: {summary['product_class']}",
        "- Product classes: " + summary_values(summary, "product_classes"),
        f"- Certification impact: {summary['certification_impact']}",
        f"- Owner surface: {summary['owner_surface']}",
        f"- Next action: {summary['next_action']}",
        f"- Privacy state: {summary['privacy_state']}",
        f"- Signal score: {summary['score']}",
        f"- Report fingerprint: {summary['report_fingerprint']}",
        f"- Dedupe fingerprint: {summary['dedupe_fingerprint']}",
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
        "certification_impact": summary.get("certification_impact"),
        "dedupe_fingerprint": summary.get("dedupe_fingerprint"),
        "issue_url": sanitize_issue_url(issue_url),
        "event_count": len(events),
        "next_action": summary.get("next_action"),
        "owner_surface": summary.get("owner_surface"),
        "payload_sha256": sha256_text(body),
        "privacy_state": summary.get("privacy_state"),
        "product_class": summary.get("product_class"),
        "product_classes": summary.get("product_classes"),
        "report_class": summary.get("report_class"),
        "report_fingerprint": summary.get("report_fingerprint"),
        "severity": summary.get("severity"),
        "sent_at": utc_stamp(),
    }
    path = receipts_path(target) / f"{file_stamp()}-{chunk:02d}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return rel(path, target)


def write_suppression_receipt(target: Path, events: list[dict[str, object]], summary: dict[str, object]) -> str:
    receipts_path(target).mkdir(parents=True, exist_ok=True)
    payload = {
        "actionability": summary.get("actionability"),
        "certification_impact": summary.get("certification_impact"),
        "dedupe_fingerprint": summary.get("dedupe_fingerprint"),
        "event_count": len(events),
        "next_action": summary.get("next_action"),
        "owner_surface": summary.get("owner_surface"),
        "privacy_state": summary.get("privacy_state"),
        "product_class": summary.get("product_class"),
        "product_classes": summary.get("product_classes"),
        "reason": "low-signal-heartbeat",
        "report_class": summary.get("report_class"),
        "report_fingerprint": summary.get("report_fingerprint"),
        "severity": summary.get("severity"),
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
                "certification_impact": summary.get("certification_impact"),
                "dedupe_fingerprint": summary.get("dedupe_fingerprint"),
                "next_action": summary.get("next_action"),
                "owner_surface": summary.get("owner_surface"),
                "privacy_state": summary.get("privacy_state"),
                "product_class": summary.get("product_class"),
                "product_classes": summary.get("product_classes"),
                "report_class": summary.get("report_class"),
                "report_fingerprint": summary.get("report_fingerprint"),
                "severity": summary.get("severity"),
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


def copy_scope_helper(target: Path) -> str | None:
    source = Path(__file__).with_name("scope_contract.py").resolve()
    if not source.exists():
        return None
    destination = target / SCOPE_HELPER
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source != destination.resolve():
        shutil.copy2(source, destination)
    return rel(destination, target)


def git_config_get(target: Path, key: str) -> str | None:
    result = subprocess.run(
        ["git", "config", "--path", "--get", key],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
        env=isolated_git_env(),
    )
    if result.returncode != 0:
        return None
    values = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return values[-1] if values else None


def resolve_pre_push_hook(target: Path, git_dir: Path) -> dict[str, Any]:
    configured = git_config_get(target, "core.hooksPath")
    if configured == "/dev/null":
        return {"status": "BLOCKED", "reason": "Git hooks are disabled by core.hooksPath=/dev/null"}

    hooks_dir = git_dir / "hooks"
    mode = "git-default"
    if configured:
        configured_path = Path(configured).expanduser()
        hooks_dir = configured_path if configured_path.is_absolute() else target / configured_path
        mode = "core.hooksPath"

    # Husky sets core.hooksPath to .husky/_; that is an internal wrapper dir.
    # The user-composable hook file is the sibling .husky/pre-push.
    if hooks_dir.name == "_" and hooks_dir.parent.name == ".husky":
        return {"status": "PASS", "hook": hooks_dir.parent / "pre-push", "mode": "husky", "hooksPath": configured}
    return {"status": "PASS", "hook": hooks_dir / "pre-push", "mode": mode, "hooksPath": configured}


def backup_hook_shell(backup_rel: str) -> str:
    return f"""
BACKUP_HOOK={shlex.quote(backup_rel)}
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


def has_gate_pre_git_push(text: str) -> bool:
    return "gate-pre-git" in text and re.search(r"(^|[^A-Za-z0-9_-])push([^A-Za-z0-9_-]|$)", text) is not None


def gate_pre_git_push_shell(backup_rel: str | None = None) -> str:
    backup_note = ""
    if backup_rel:
        backup_note = (
            f"BACKUP_HOOK={shlex.quote(backup_rel)}\n"
            "# BACKUP_HOOK preserved for audit; gate-pre-git is composed explicitly.\n"
        )
    return f"""
{backup_note}repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
push_base="$(git rev-parse --abbrev-ref --symbolic-full-name @{{u}} 2>/dev/null || printf '%s' origin/main)"
"$repo_root/.gate-pre-git/bin/gate-pre-git" push --target "$repo_root" --base "$push_base"
"""


def strict_pre_push_shell() -> str:
    """Strict pre-push quality fallback; Field Reports drain is added separately."""
    return f"""
run_tes_strict_pre_push() {{
  if [ -f "package.json" ] && command -v npm >/dev/null 2>&1; then
    if python3 - <<'PY'
import json
import sys

try:
    data = json.load(open("package.json", encoding="utf-8"))
except Exception:
    sys.exit(1)
scripts = data.get("scripts") if isinstance(data, dict) else None
sys.exit(0 if isinstance(scripts, dict) and "prepush:check" in scripts else 1)
PY
    then
      npm run --silent prepush:check
      return $?
    fi
    if python3 - <<'PY'
import json
import sys

try:
    data = json.load(open("package.json", encoding="utf-8"))
except Exception:
    sys.exit(1)
scripts = data.get("scripts") if isinstance(data, dict) else None
sys.exit(0 if isinstance(scripts, dict) and "commit:check" in scripts else 1)
PY
    then
      npm run --silent commit:check
      return $?
    fi
  fi
  if [ -f "{CANONICAL_DISCIPLINE_ORACLE}" ]; then
    python3 "{CANONICAL_DISCIPLINE_ORACLE}" --self-test
    return $?
  fi
  if [ -f "{CLAUDE_DISCIPLINE_ORACLE}" ]; then
    python3 "{CLAUDE_DISCIPLINE_ORACLE}" --self-test
    return $?
  fi
  printf '%s\\n' "TES strict pre-push: no resolvable gate found; expected package.json scripts.prepush:check, scripts.commit:check, or {CANONICAL_DISCIPLINE_ORACLE}" >&2
  return 1
}}
run_tes_strict_pre_push
"""


def existing_backup_path(current_hook: str, target: Path) -> Path | None:
    match = BACKUP_HOOK_RE.search(current_hook)
    if not match:
        return None
    raw = match.group("value").strip()
    try:
        value = shlex.split(raw)[0]
    except (IndexError, ValueError):
        value = raw.strip("\"'")
    path = Path(value)
    return path if path.is_absolute() else target / path


def select_hook_manager(target: Path) -> dict[str, Any]:
    """Deterministically pick the Git hook manager for this target (ceiling rule).

    Selection is never random. An existing manager config is respected first so
    TES defers instead of colliding; otherwise the project type decides:
      1. an existing manager config (husky / lefthook / pre-commit / native
         core.hooksPath) -> defer to that owner;
      2. husky        -> Node/TS/npm-first (package.json present, no stronger
                         signal of another manager);
      3. pre-commit   -> a .pre-commit-config.yaml is present (Python/data/tooling);
      4. lefthook     -> the polyglot/monorepo default when nothing else matches.

    Makefile/CI is never selected here: it is a fallback integrator, never the
    sole local proof while Git hooks are installable. The returned manager is the
    owner whose hook paths TES writes its strict pre-commit + pre-push gates into.
    """
    configured = git_config_get(target, "core.hooksPath")
    has_husky = (target / ".husky").is_dir() or (configured or "").startswith(".husky")
    has_lefthook = any(
        (target / name).is_file()
        for name in ("lefthook.yml", "lefthook.yaml", "lefthook.toml", "lefthook.json", ".lefthook.yml", ".lefthook.yaml")
    )
    has_precommit = (target / ".pre-commit-config.yaml").is_file() or (target / ".pre-commit-config.yml").is_file()

    # 1. Respect an existing manager — defer, do not introduce a second owner.
    if has_husky:
        return {"manager": HOOK_MANAGER_HUSKY, "reason": "existing husky config", "deferred": True}
    if has_lefthook:
        return {"manager": HOOK_MANAGER_LEFTHOOK, "reason": "existing lefthook config", "deferred": True}
    if has_precommit:
        return {"manager": HOOK_MANAGER_PRECOMMIT, "reason": "existing .pre-commit-config.yaml", "deferred": True}

    # 2-4. No existing manager: choose by project type, write into native paths.
    is_node = (target / "package.json").is_file()
    if is_node:
        return {"manager": HOOK_MANAGER_HUSKY, "reason": "Node/TS/npm-first project (package.json)", "deferred": False}
    # pre-commit only auto-selected when its config exists (handled above); a bare
    # Python tree without config falls through to the polyglot default so TES still
    # writes a strict gate rather than depending on an absent framework.
    return {"manager": HOOK_MANAGER_LEFTHOOK, "reason": "polyglot/monorepo default", "deferred": False}


def resolve_pre_commit_hook(target: Path, git_dir: Path) -> dict[str, Any]:
    """Resolve the pre-commit hook path, mirroring resolve_pre_push_hook.

    Honors core.hooksPath and the husky .husky/_ wrapper convention so the strict
    pre-commit gate lands on the same owner surface as the pre-push gate.
    """
    configured = git_config_get(target, "core.hooksPath")
    if configured == "/dev/null":
        return {"status": "BLOCKED", "reason": "Git hooks are disabled by core.hooksPath=/dev/null"}
    hooks_dir = git_dir / "hooks"
    mode = "git-default"
    if configured:
        configured_path = Path(configured).expanduser()
        hooks_dir = configured_path if configured_path.is_absolute() else target / configured_path
        mode = "core.hooksPath"
    if hooks_dir.name == "_" and hooks_dir.parent.name == ".husky":
        return {"status": "PASS", "hook": hooks_dir.parent / "pre-commit", "mode": "husky", "hooksPath": configured}
    return {"status": "PASS", "hook": hooks_dir / "pre-commit", "mode": mode, "hooksPath": configured}


def backup_precommit_shell(backup_rel: str) -> str:
    """Chain a backed-up foreign pre-commit before the TES strict gate, like pre-push."""
    return f"""
BACKUP_PRECOMMIT={shlex.quote(backup_rel)}
if [ -f "$BACKUP_PRECOMMIT" ]; then
  if [ -x "$BACKUP_PRECOMMIT" ]; then
    "$BACKUP_PRECOMMIT" "$@"
  else
    sh "$BACKUP_PRECOMMIT" "$@"
  fi
  rc=$?
  if [ "$rc" -ne 0 ]; then
    exit "$rc"
  fi
fi
"""


def existing_precommit_backup_path(current_hook: str, target: Path) -> Path | None:
    match = BACKUP_PRECOMMIT_RE.search(current_hook)
    if not match:
        return None
    raw = match.group("value").strip()
    try:
        value = shlex.split(raw)[0]
    except (IndexError, ValueError):
        value = raw.strip("\"'")
    path = Path(value)
    return path if path.is_absolute() else target / path


def install_pre_commit_hook(target: Path, git_dir: Path) -> dict[str, Any]:
    """Install a strict TES pre-commit gate, deferring/chaining a foreign hook.

    Mirrors the pre-push installer: idempotent, single foreign backup chained
    before the TES gate, never an orphan, BLOCKED when hooks are disabled. The
    written gate invokes the TES commit:check gate so canary_admission_oracle
    .precommit_evidence recognizes it as strict. This is the delivered behavior
    that overturns the prior 'TES never auto-installs strict pre-commit' rule:
    when Git is eligible, TES installs and verifies the strict gate.
    """
    hook_info = resolve_pre_commit_hook(target, git_dir)
    if hook_info["status"] != "PASS":
        return {"status": "BLOCKED", "reason": hook_info["reason"]}
    hook = hook_info["hook"]
    hook.parent.mkdir(parents=True, exist_ok=True)
    backup_rel: str | None = None
    backup_shell = ""
    if hook.exists():
        current = hook.read_text(encoding="utf-8", errors="replace")
        if PRECOMMIT_MARKER in current:
            backup_path = existing_precommit_backup_path(current, target)
            if backup_path and backup_path.exists():
                backup_rel = rel(backup_path, target)
                backup_shell = backup_precommit_shell(backup_rel)
        else:
            backup = hook.with_name(f"pre-commit.before-tes-{file_stamp()}")
            shutil.copy2(hook, backup)
            backup.chmod(0o755)
            backup_rel = rel(backup, target)
            backup_shell = backup_precommit_shell(backup_rel)

    hook_text = f"""#!/bin/sh
# {PRECOMMIT_MARKER}
set -eu
{backup_shell}
run_tes_strict_pre_commit() {{
  if [ -f "package.json" ] && command -v npm >/dev/null 2>&1; then
    if python3 - <<'PY'
import json
import sys

try:
    data = json.load(open("package.json", encoding="utf-8"))
except Exception:
    sys.exit(1)
scripts = data.get("scripts") if isinstance(data, dict) else None
sys.exit(0 if isinstance(scripts, dict) and "commit:check" in scripts else 1)
PY
    then
      npm run --silent commit:check
      return $?
    fi
  fi
  if [ -f "{CANONICAL_DISCIPLINE_ORACLE}" ]; then
    python3 "{CANONICAL_DISCIPLINE_ORACLE}" --self-test
    return $?
  fi
  if [ -f "{CLAUDE_DISCIPLINE_ORACLE}" ]; then
    python3 "{CLAUDE_DISCIPLINE_ORACLE}" --self-test
    return $?
  fi
  printf '%s\\n' "TES strict pre-commit: no resolvable gate found; expected package.json scripts.commit:check or {CANONICAL_DISCIPLINE_ORACLE}" >&2
  return 1
}}
run_tes_strict_pre_commit
"""
    hook.write_text(hook_text, encoding="utf-8")
    hook.chmod(0o755)
    return {
        "status": "PASS",
        "hook": rel(hook, target),
        "hook_mode": hook_info["mode"],
        "backup": backup_rel,
    }


def install_hook(target: Path) -> dict[str, object]:
    target = target.expanduser().resolve()
    git_dir = target / ".git"
    if not git_dir.exists() or not git_dir.is_dir():
        return {"version": VERSION, "status": "BLOCKED", "reason": "target is not a Git repository", "writes": []}

    hook_info = resolve_pre_push_hook(target, git_dir)
    if hook_info["status"] != "PASS":
        return {"version": VERSION, "status": "BLOCKED", "reason": hook_info["reason"], "writes": []}

    ensure_layout(target)
    install_id = ensure_install_id(target)
    helper = copy_helper(target)
    scope_helper = copy_scope_helper(target)
    exclude = ensure_git_exclude(target)
    hook = hook_info["hook"]
    hooks = hook.parent
    hooks.mkdir(parents=True, exist_ok=True)
    backup_rel: str | None = None
    backup_shell = ""
    gate_pre_git_shell = ""
    if hook.exists():
        current = hook.read_text(encoding="utf-8", errors="replace")
        if HOOK_MARKER in current:
            backup_path = existing_backup_path(current, target)
            if backup_path and backup_path.exists():
                backup_rel = rel(backup_path, target)
                backup_text = backup_path.read_text(encoding="utf-8", errors="replace")
                if has_gate_pre_git_push(current) or has_gate_pre_git_push(backup_text):
                    gate_pre_git_shell = gate_pre_git_push_shell(backup_rel)
                else:
                    backup_shell = backup_hook_shell(backup_rel)
        else:
            backup = hook.with_name(f"pre-push.before-tes-{file_stamp()}")
            shutil.copy2(hook, backup)
            backup.chmod(0o755)
            backup_rel = rel(backup, target)
            if has_gate_pre_git_push(current):
                gate_pre_git_shell = gate_pre_git_push_shell(backup_rel)
            else:
                backup_shell = backup_hook_shell(backup_rel)

    # The strict quality gate is blocking. Field Reports drain remains
    # best-effort and runs only after the quality gate succeeds.
    quality_gate_shell = gate_pre_git_shell or strict_pre_push_shell()
    hook_text = f"""#!/bin/sh
# {HOOK_MARKER}
set -eu
{backup_shell}
{quality_gate_shell}
if [ -f ".tes/bin/field_reports.py" ]; then
  python3 ".tes/bin/field_reports.py" drain --target . --trigger pre-push >/dev/null 2>&1 || true
elif [ -f "scripts/field_reports.py" ]; then
  python3 "scripts/field_reports.py" drain --target . --trigger pre-push >/dev/null 2>&1 || true
fi
exit 0
"""
    hook.write_text(hook_text, encoding="utf-8")
    hook.chmod(0o755)

    # Strict pre-commit gate: when Git is eligible TES installs AND verifies it,
    # selecting the manager deterministically (ceiling: never advisory-only when
    # Git hooks are installable). The selection is recorded so canary admission
    # and doctor read it as a contract field, not a cosmetic flag.
    manager = select_hook_manager(target)
    pre_commit = install_pre_commit_hook(target, git_dir)

    writes = [helper, rel(hook, target), rel(outbox_path(target), target), rel(install_id_path(target), target)]
    if scope_helper:
        writes.insert(1, scope_helper)
    if exclude:
        writes.append(exclude)
    if backup_rel:
        writes.append(backup_rel)
    if pre_commit.get("status") == "PASS" and pre_commit.get("hook"):
        writes.append(str(pre_commit["hook"]))
    if pre_commit.get("backup"):
        writes.append(str(pre_commit["backup"]))
    return {
        "version": VERSION,
        "status": "PASS",
        "install_id": install_id,
        "hook": rel(hook, target),
        "hook_mode": hook_info["mode"],
        "hooksPath": hook_info.get("hooksPath"),
        "backup": backup_rel,
        "hook_manager": manager.get("manager"),
        "hook_manager_reason": manager.get("reason"),
        "hook_manager_deferred": manager.get("deferred"),
        "pre_commit": pre_commit,
        "pre_commit_installed": pre_commit.get("status") == "PASS",
        "writes": writes,
    }


def outbox_pending_threshold() -> int:
    """Backlog size above which status() surfaces a non-blocking advisory.

    Configurable via TES_FIELD_REPORTS_PENDING_THRESHOLD; falls back to the
    default on any unset/invalid value. Never affects gate status.
    """
    raw = os.environ.get("TES_FIELD_REPORTS_PENDING_THRESHOLD")
    if raw is None:
        return DEFAULT_OUTBOX_PENDING_THRESHOLD
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return DEFAULT_OUTBOX_PENDING_THRESHOLD
    return value if value > 0 else DEFAULT_OUTBOX_PENDING_THRESHOLD


def status(target: Path) -> dict[str, object]:
    target = target.expanduser().resolve()
    ensure_layout(target)
    events, failures = read_outbox(target)
    receipts = sorted(receipts_path(target).glob("*.json")) if receipts_path(target).exists() else []
    last_receipt = rel(receipts[-1], target) if receipts else None
    pending = len(events)
    threshold = outbox_pending_threshold()
    pending_advisory = (
        f"{pending} field reports pendentes (>{threshold}) — sincronize ou limpe o outbox."
        if pending > threshold
        else None
    )
    return {
        "version": VERSION,
        "status": "PASS" if not failures else "BLOCKED",
        "disabled": field_reports_disabled(target),
        "pending": pending,
        "pending_advisory": pending_advisory,
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


MANTRA_GATES_LEDGER = FIELD_ROOT / "mantra-gates.jsonl"
MANTRA_GATES_QUARANTINE = FIELD_ROOT / "mantra-gates.quarantine.jsonl"


def _load_gate_helpers():
    """Lazy import of the sibling Mantra Gate helpers. Both are delivered next to
    field_reports.py in .tes/bin/ (see tes_bundle.py). Importing here (not at
    module top) keeps the rest of field_reports usable if they are ever absent,
    and reusing the adoption oracle's own gate_from_record guarantees prune and
    certification extract the SAME gate from a record — they must agree on what
    is invalid, so they share one extraction, not two parallel field lists."""
    import mantra_gate  # noqa: PLC0415 — intentional lazy, sibling-delivered helper
    import mantra_gate_adoption_oracle  # noqa: PLC0415 — same, shared gate extraction

    return mantra_gate, mantra_gate_adoption_oracle


def _ledger_line_is_invalid(line: str, mantra_gate, adoption) -> bool:
    """A ledger line is invalid when it is not parseable JSON, or its gate fails
    mantra_gate schema validation in health mode (e.g. a retired STATUS like
    PASS). Valid PROCEED/BLOCKED/NEEDS_REVIEW records are never invalid. Gate
    extraction reuses the adoption oracle's gate_from_record so this matches
    exactly what installed certification validates."""
    try:
        record = json.loads(line)
    except json.JSONDecodeError:
        return True
    if not isinstance(record, dict):
        return True
    gate = adoption.gate_from_record(record)
    health_gate = {k: v for k, v in gate.items() if str(k).upper() not in ("RISK",)}
    result = mantra_gate.validate_gate(health_gate, state_changing=False, closure_claim=False, risk=None)
    return not result["valid"]


def prune_invalid_mantra_gates(target: Path) -> dict[str, object]:
    """Sanctioned repair for the append-only Mantra Gate ledger.

    Schema-invalid records (a retired STATUS vocabulary like PASS, or unparseable
    lines) keep installed certification stuck at NEEDS_REVIEW with no governed way
    to clear them — the only prior fix was hand-editing a git-ignored evidence
    file. This MOVES invalid lines to a quarantine sidecar (never deletes — the
    audit trail is preserved), keeps every valid PROCEED/BLOCKED/NEEDS_REVIEW
    record in place and in order, records the prune as a field-report event, and
    is idempotent (a second run with nothing invalid is a clean no-op)."""
    target = target.expanduser().resolve()
    ledger = target / MANTRA_GATES_LEDGER
    quarantine = target / MANTRA_GATES_QUARANTINE
    if not ledger.exists():
        return {"version": VERSION, "status": "PASS", "invalid_count": 0,
                "reason": "no mantra-gates ledger", "writes": []}

    try:
        mantra_gate, adoption = _load_gate_helpers()
    except ImportError:
        return {"version": VERSION, "status": "BLOCKED", "invalid_count": 0,
                "reason": "Mantra Gate helpers not available alongside field_reports", "writes": []}

    lines = [line for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
    kept: list[str] = []
    quarantined: list[str] = []
    for line in lines:
        (quarantined if _ledger_line_is_invalid(line, mantra_gate, adoption) else kept).append(line)

    if not quarantined:
        # Idempotent no-op: nothing invalid, do not rewrite or re-record.
        return {"version": VERSION, "status": "PASS", "invalid_count": 0,
                "kept": len(kept), "writes": []}

    # Append (not overwrite) quarantined lines so repeated prunes accumulate the
    # full forensic record; rewrite the ledger to only the valid records.
    with quarantine.open("a", encoding="utf-8") as handle:
        for line in quarantined:
            handle.write(line + "\n")
    ledger.write_text(("".join(line + "\n" for line in kept)), encoding="utf-8")

    writes = [rel(ledger, target), rel(quarantine, target)]
    record_event(
        target,
        "field_reports.mantra_gate_prune",
        "PASS",
        surface="mantra-gates",
        trigger="cli",
        details={
            "invalid_count": len(quarantined),
            "kept_count": len(kept),
            "quarantine": rel(quarantine, target),
        },
    )
    return {
        "version": VERSION,
        "status": "PASS",
        "invalid_count": len(quarantined),
        "kept": len(kept),
        "quarantine": rel(quarantine, target),
        "writes": writes,
    }


def self_test() -> dict[str, object]:
    failures: list[str] = []

    def write_prepush_quality_oracle(fixture: Path) -> None:
        oracle = fixture / CANONICAL_DISCIPLINE_ORACLE
        oracle.parent.mkdir(parents=True, exist_ok=True)
        oracle.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n", encoding="utf-8")
        oracle.chmod(0o755)

    with tempfile.TemporaryDirectory(prefix="tes-field-reports-") as tempdir:
        target = Path(tempdir)
        subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False, env=isolated_git_env())

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
        for relpath in (
            ".tes/bin/field_reports.py",
            ".tes/bin/scope_contract.py",
            ".tes/field-reports/outbox.jsonl",
            ".git/hooks/pre-push",
        ):
            if not (target / relpath).exists():
                failures.append(f"missing installed path: {relpath}")
        if hook_result["status"] != "PASS":
            failures.append("install-hook did not pass in a Git fixture")
        pre_commit_hook = target / ".git/hooks/pre-commit"
        if not pre_commit_hook.exists():
            failures.append("install-hook must write a strict pre-commit hook")
        else:
            pre_commit_run = subprocess.run(
                [str(pre_commit_hook)],
                cwd=target,
                text=True,
                capture_output=True,
                check=False,
                env=isolated_git_env(),
            )
            if pre_commit_run.returncode == 0:
                failures.append("strict pre-commit must fail closed when no real gate is available")
        installed = target / "installed-helper"
        installed.mkdir()
        subprocess.run(["git", "init"], cwd=installed, text=True, capture_output=True, check=False, env=isolated_git_env())
        installed_helper = installed / BIN_HELPER
        installed_helper.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(__file__).resolve(), installed_helper)
        shutil.copy2(Path(__file__).with_name("scope_contract.py").resolve(), installed / SCOPE_HELPER)
        installed_result = subprocess.run(
            [sys.executable, str(installed_helper), "install-hook", "--target", str(installed), "--json-only"],
            cwd=installed,
            text=True,
            capture_output=True,
            check=False,
            env=isolated_git_env(),
        )
        if installed_result.returncode != 0:
            failures.append("installed field_reports helper install-hook must be idempotent")
            failures.extend(installed_result.stdout.splitlines())
            failures.extend(installed_result.stderr.splitlines())

        githooks_target = target / "core-hooks-path-githooks"
        githooks_target.mkdir()
        subprocess.run(["git", "init"], cwd=githooks_target, text=True, capture_output=True, check=False, env=isolated_git_env())
        subprocess.run(
            ["git", "config", "core.hooksPath", ".githooks"],
            cwd=githooks_target,
            text=True,
            capture_output=True,
            check=False,
            env=isolated_git_env(),
        )
        githooks_result = install_hook(githooks_target)
        githooks_hook = githooks_target / ".githooks/pre-push"
        dormant_githook = githooks_target / ".git/hooks/pre-push"
        if githooks_result.get("status") != "PASS" or githooks_result.get("hook") != ".githooks/pre-push":
            failures.append("core.hooksPath=.githooks install must target the active pre-push hook")
        if not githooks_hook.exists() or HOOK_MARKER not in githooks_hook.read_text(encoding="utf-8", errors="replace"):
            failures.append("core.hooksPath=.githooks active hook must contain Field Reports drain")
        if dormant_githook.exists() and HOOK_MARKER in dormant_githook.read_text(encoding="utf-8", errors="replace"):
            failures.append("core.hooksPath=.githooks install must not write an orphan .git/hooks/pre-push")
        write_prepush_quality_oracle(githooks_target)
        githooks_run = subprocess.run(
            [str(githooks_hook)],
            cwd=githooks_target,
            text=True,
            capture_output=True,
            check=False,
            env=isolated_git_env(),
        )
        if githooks_run.returncode != 0:
            failures.append("core.hooksPath=.githooks pre-push hook must execute when a quality gate resolves")

        husky_target = target / "core-hooks-path-husky"
        husky_target.mkdir()
        subprocess.run(["git", "init"], cwd=husky_target, text=True, capture_output=True, check=False, env=isolated_git_env())
        (husky_target / ".husky/_").mkdir(parents=True)
        husky_wrapper = husky_target / ".husky/_/pre-push"
        husky_wrapper.write_text(
            """#!/usr/bin/env sh
hook_dir="$(dirname "$0")"
if [ -f "$hook_dir/../pre-push" ]; then
  sh "$hook_dir/../pre-push" "$@"
fi
exit 0
""",
            encoding="utf-8",
        )
        husky_wrapper.chmod(0o755)
        subprocess.run(
            ["git", "config", "core.hooksPath", ".husky/_"],
            cwd=husky_target,
            text=True,
            capture_output=True,
            check=False,
            env=isolated_git_env(),
        )
        husky_result = install_hook(husky_target)
        husky_hook = husky_target / ".husky/pre-push"
        if husky_result.get("status") != "PASS" or husky_result.get("hook") != ".husky/pre-push":
            failures.append("core.hooksPath=.husky/_ install must target the Husky user hook")
        if not husky_hook.exists() or HOOK_MARKER not in husky_hook.read_text(encoding="utf-8", errors="replace"):
            failures.append("Husky user pre-push hook must contain Field Reports drain")
        if HOOK_MARKER in husky_wrapper.read_text(encoding="utf-8", errors="replace"):
            failures.append("install-hook must not overwrite Husky internal wrapper")
        write_prepush_quality_oracle(husky_target)
        husky_run = subprocess.run(
            [str(husky_wrapper)],
            cwd=husky_target,
            text=True,
            capture_output=True,
            check=False,
            env=isolated_git_env(),
        )
        if husky_run.returncode != 0:
            failures.append("Husky wrapper must execute the Field Reports user hook when a quality gate resolves")

        disabled_hooks_target = target / "core-hooks-path-disabled"
        disabled_hooks_target.mkdir()
        subprocess.run(
            ["git", "init"], cwd=disabled_hooks_target, text=True, capture_output=True, check=False, env=isolated_git_env()
        )
        subprocess.run(
            ["git", "config", "core.hooksPath", "/dev/null"],
            cwd=disabled_hooks_target,
            text=True,
            capture_output=True,
            check=False,
            env=isolated_git_env(),
        )
        disabled_hooks_result = install_hook(disabled_hooks_target)
        if disabled_hooks_result.get("status") != "BLOCKED":
            failures.append("core.hooksPath=/dev/null must block Field Reports hook installation")

        chained_target = target / "pre-existing-pre-push"
        chained_target.mkdir()
        subprocess.run(["git", "init"], cwd=chained_target, text=True, capture_output=True, check=False, env=isolated_git_env())
        chained_hook = chained_target / ".git/hooks/pre-push"
        chained_hook.write_text(
            """#!/usr/bin/env sh
set -eu
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
"$repo_root/.gate-pre-git/bin/gate-pre-git" push --target "$repo_root"
""",
            encoding="utf-8",
        )
        chained_hook.chmod(0o755)
        gate_pre_git_bin = chained_target / ".gate-pre-git/bin/gate-pre-git"
        gate_pre_git_bin.parent.mkdir(parents=True)
        gate_pre_git_bin.write_text(
            """#!/usr/bin/env sh
printf '%s\\n' "$*" > gate-pre-git.log
""",
            encoding="utf-8",
        )
        gate_pre_git_bin.chmod(0o755)
        first_chain_result = install_hook(chained_target)
        first_chain_text = chained_hook.read_text(encoding="utf-8")
        second_chain_result = install_hook(chained_target)
        second_chain_text = chained_hook.read_text(encoding="utf-8")
        backups = sorted((chained_target / ".git/hooks").glob("pre-push.before-tes-*"))
        if first_chain_result["status"] != "PASS" or second_chain_result["status"] != "PASS":
            failures.append("install-hook must pass when a pre-existing pre-push hook is present")
        if len(backups) != 1:
            failures.append("pre-existing pre-push hook must be backed up exactly once")
        elif "gate-pre-git" not in backups[0].read_text(encoding="utf-8", errors="replace"):
            failures.append("pre-existing pre-push backup must preserve gate-pre-git")
        if "gate-pre-git" not in first_chain_text or " push " not in first_chain_text:
            failures.append("active pre-push hook must expose gate-pre-git push for target doctor")
        if "gate-pre-git" not in second_chain_text or " push " not in second_chain_text:
            failures.append("second install-hook must preserve active gate-pre-git push composition")
        if '"$BACKUP_HOOK" "$@"' in first_chain_text or 'sh "$BACKUP_HOOK" "$@"' in first_chain_text:
            failures.append("gate-pre-git composition must not execute backup hook recursively")
        if "field_reports.py\" drain" not in first_chain_text:
            failures.append("active pre-push hook must retain Field Reports drain")
        elif first_chain_text.find("gate-pre-git") > first_chain_text.find("field_reports.py\" drain"):
            failures.append("active pre-push hook must run gate-pre-git before Field Reports drain")
        if first_chain_text != second_chain_text:
            failures.append("second install-hook must not drop or rewrite the pre-existing hook chain")
        chained_hook_run = subprocess.run(
            [str(chained_hook)],
            cwd=chained_target,
            text=True,
            capture_output=True,
            check=False,
            env=isolated_git_env(),
        )
        gate_log = chained_target / "gate-pre-git.log"
        if chained_hook_run.returncode != 0:
            failures.append("composed gate-pre-git pre-push hook must pass with a passing project gate")
        if not gate_log.exists() or "push --target" not in gate_log.read_text(encoding="utf-8", errors="replace"):
            failures.append("composed pre-push hook must execute gate-pre-git push explicitly")
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
            ".tes/mantra-gates/records.jsonl",
            ".tes/legacy-retirement/backup.json",
            ".tes/cortex/recall.sqlite",
            ".tes/cortex/semantic.sqlite-wal",
            "root.pyc",
        ):
            probe = target / relpath
            probe.parent.mkdir(parents=True, exist_ok=True)
            probe.write_text("probe\n", encoding="utf-8")
            ignored = subprocess.run(
                ["git", "check-ignore", relpath],
                cwd=target,
                text=True,
                capture_output=True,
                check=False,
                env=isolated_git_env(),
            )
            if ignored.returncode != 0:
                failures.append(f"local git hygiene did not ignore: {relpath}")
        helper_ignored = subprocess.run(
            ["git", "check-ignore", ".tes/bin/field_reports.py"],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
            env=isolated_git_env(),
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
                "unsafe_path": SYNTHETIC_PRIVATE_PATH,
                "unsafe_email": SYNTHETIC_EMAIL,
                "unsafe_token": SYNTHETIC_SECRET_ASSIGNMENT,
                "unsafe_url": SYNTHETIC_PRIVATE_URL,
                "unsafe_stack": "Traceback (most recent call last):\nFile x",
                "returncode": 1,
            },
        )
        write_prepush_quality_oracle(target)
        events, event_failures = read_outbox(target)
        failures.extend(event_failures)
        if len(events) != 1:
            failures.append("capture must append exactly one event before drain")
        elif events[0].get("scope_status") != "PASS" or not isinstance(events[0].get("scope"), dict):
            failures.append("captured event must include a normalized PASS runtime scope")

        scope_target = target / "scope-rejection"
        scope_target.mkdir()
        subprocess.run(["git", "init"], cwd=scope_target, text=True, capture_output=True, check=False, env=isolated_git_env())
        install_hook(scope_target)
        unsafe_scope = record_event(
            scope_target,
            "cortex.audit",
            "FAIL",
            "cortex",
            "self-test",
            details={"evidence_ref": "/absolute/unsafe/evidence.md"},
        )
        if unsafe_scope.get("status") != "BLOCKED" or unsafe_scope.get("writes") != []:
            failures.append("unsafe runtime scope evidence refs must be rejected without outbox writes")
        scope_events, scope_failures = read_outbox(scope_target)
        failures.extend(scope_failures)
        if scope_events:
            failures.append("unsafe scope rejection must not append an event")

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
        env = isolated_git_env({"PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}", "GH_BODY_CAPTURE": str(body_capture)})
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
        for forbidden in (
            "```",
            "|",
            SYNTHETIC_USER_PREFIX,
            SYNTHETIC_EMAIL,
            SYNTHETIC_SECRET_VALUE,
            SYNTHETIC_PRIVATE_URL_PREFIX,
            "Traceback",
        ):
            if forbidden in body:
                failures.append(f"issue body leaked prohibited token: {forbidden}")

        quiet_target = target / "quiet-heartbeat"
        quiet_target.mkdir()
        subprocess.run(["git", "init"], cwd=quiet_target, text=True, capture_output=True, check=False, env=isolated_git_env())
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
        quiet_drain = drain(quiet_target, "self-test", env=isolated_git_env({"PATH": str(quiet_target / "missing-gh")}))
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
        missing_env = isolated_git_env({"PATH": str(python_only)})
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

        # GAP-5: outbox backlog over threshold surfaces a non-blocking advisory.
        # Status must stay PASS; the advisory is purely additive.
        threshold_target = target / "threshold"
        threshold_target.mkdir()
        ensure_layout(threshold_target)
        empty_status = status(threshold_target)
        if empty_status.get("pending_advisory") is not None:
            failures.append("empty outbox must not raise a pending advisory")
        if empty_status.get("status") != "PASS":
            failures.append("empty outbox status must be PASS")
        backlog = "".join(
            json.dumps({"schema": SCHEMA, "event": f"e{i}", "status": "PASS"}) + "\n" for i in range(5)
        )
        outbox_path(threshold_target).write_text(backlog, encoding="utf-8")
        prior = os.environ.get("TES_FIELD_REPORTS_PENDING_THRESHOLD")
        os.environ["TES_FIELD_REPORTS_PENDING_THRESHOLD"] = "3"
        try:
            over = status(threshold_target)
        finally:
            if prior is None:
                os.environ.pop("TES_FIELD_REPORTS_PENDING_THRESHOLD", None)
            else:
                os.environ["TES_FIELD_REPORTS_PENDING_THRESHOLD"] = prior
        if over.get("pending") != 5:
            failures.append("status must count backlog events")
        if not over.get("pending_advisory"):
            failures.append("backlog over threshold must raise a pending advisory")
        if over.get("status") != "PASS":
            failures.append("pending advisory must not change PASS status")

        # prune-invalid-mantra-gates: a stale STATUS:PASS record followed by a
        # valid PROCEED retry must leave only the valid record, quarantine the
        # invalid one, record the prune, and be idempotent.
        prune_target = Path(tempdir) / "prune"
        ledger = prune_target / MANTRA_GATES_LEDGER
        ledger.parent.mkdir(parents=True, exist_ok=True)
        invalid_rec = {"gate": {"VERIFY": "x", "SCOPE": "s", "BEST_PATH": "d",
                                "DOCUMENT": "n", "RESOLVE": "done", "STATUS": "PASS"}, "visible": "full"}
        valid_rec = {"gate": {"VERIFY": "x", "SCOPE": "s", "BEST_PATH": "d",
                              "DOCUMENT": "n", "RESOLVE": "done", "STATUS": "PROCEED"}, "visible": "full"}
        ledger.write_text(json.dumps(invalid_rec) + "\n" + json.dumps(valid_rec) + "\n", encoding="utf-8")
        prune_res = prune_invalid_mantra_gates(prune_target)
        if prune_res.get("status") != "PASS":
            failures.append("prune-invalid-mantra-gates must report PASS")
        if prune_res.get("invalid_count") != 1:
            failures.append(f"prune must detect 1 invalid record, got {prune_res.get('invalid_count')}")
        remaining = [line for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(remaining) != 1 or "PROCEED" not in remaining[0]:
            failures.append("prune must keep only the valid PROCEED record in the ledger")
        quarantine = prune_target / MANTRA_GATES_QUARANTINE
        if not quarantine.exists() or "PASS" not in quarantine.read_text(encoding="utf-8"):
            failures.append("prune must quarantine the invalid PASS record")
        prune_events = [
            line for line in outbox_path(prune_target).read_text(encoding="utf-8").splitlines()
            if "mantra_gate_prune" in line
        ] if outbox_path(prune_target).exists() else []
        if not prune_events:
            failures.append("prune must record a field-report event in the outbox")
        second = prune_invalid_mantra_gates(prune_target)
        if second.get("invalid_count") != 0:
            failures.append("prune must be idempotent (second run finds nothing invalid)")

        # Legacy record agreement: a record with gate fields at the TOP level
        # (no nested "gate") and an ORACLE field must be classified the SAME by
        # prune and by the adoption oracle — both reuse gate_from_record, so a
        # valid legacy PROCEED record is kept, not quarantined.
        legacy_target = Path(tempdir) / "prune-legacy"
        legacy_ledger = legacy_target / MANTRA_GATES_LEDGER
        legacy_ledger.parent.mkdir(parents=True, exist_ok=True)
        legacy_valid = {"VERIFY": "x", "SCOPE": "s", "BEST_PATH": "d", "DOCUMENT": "n",
                        "ORACLE": "ran", "RESOLVE": "done", "STATUS": "PROCEED"}
        legacy_ledger.write_text(json.dumps(legacy_valid) + "\n", encoding="utf-8")
        legacy_res = prune_invalid_mantra_gates(legacy_target)
        if legacy_res.get("invalid_count") != 0:
            failures.append("prune must keep a valid legacy record with a top-level ORACLE field (parity with adoption oracle)")

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
    parser.add_argument("command", nargs="?", choices=("capture", "drain", "status", "disable", "enable", "install-hook", "prune-invalid-mantra-gates"))
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
    elif args.command == "prune-invalid-mantra-gates":
        result = prune_invalid_mantra_gates(args.target)
    else:
        parser.error("command is required unless --self-test is used")
    return print_result(result, str(args.command), args.json_only)


if __name__ == "__main__":
    sys.exit(main())
