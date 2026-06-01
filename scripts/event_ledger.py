#!/usr/bin/env python3
"""Inspect TES lifecycle event ledgers without writing project memory."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Any

import scope_contract


VERSION = "0.3.151"
SCHEMA = "tes-event-ledger@1"
LEDGER = Path(".tes/events/ledger.jsonl")
ALLOWED_STATUSES = {
    "PASS",
    "FAIL",
    "BLOCKED",
    "DEGRADED",
    "NEEDS_REVIEW",
    "SKIP",
    "CERTIFIED",
}
LIFECYCLE_MAP = {
    "scope": "scope-normalization",
    "recall": "recall",
    "event": "event",
    "checkpoint": "checkpoint",
    "review": "review",
    "authorized_write": "authorized-write",
    "evidence": "evidence",
    "closeout": "closeout",
    "subagent_return": "subagent-return",
}
SAFE_TOKEN = re.compile(r"[^a-zA-Z0-9_.:-]+")
ISO_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
ABSOLUTE_PATH = re.compile(r"(/Users|/home|/private|/var/folders|/absolute|[A-Za-z]:\\)[^\s`\"')]+")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL = re.compile(r"https?://[^\s`\"')]+")
SECRET = re.compile(
    r"(?i)(api[_-]?key|authorization|bearer|credential|password|secret|token)\s*[:=]?\s*[A-Za-z0-9._:/+=-]+"
)
STACK_TRACE = re.compile(r"(?i)(traceback \(most recent call last\)|\bat .+:\d+:\d+|exception: .+)")
SYNTHETIC_EMAIL = "person" + "@example.com"
SYNTHETIC_SECRET_VALUE = "abc" + "123"
SYNTHETIC_BEARER_SECRET = "Bearer " + SYNTHETIC_SECRET_VALUE
SYNTHETIC_SECRET_ASSIGNMENT = "token=" + SYNTHETIC_SECRET_VALUE
SYNTHETIC_PRIVATE_URL = "https://" + "private." + "example.test"
SYNTHETIC_PRIVATE_REPO_URL = SYNTHETIC_PRIVATE_URL + "/repo"
FORBIDDEN_OUTPUT = (
    "/absolute/unsafe",
    "/Users/",
    SYNTHETIC_EMAIL,
    SYNTHETIC_BEARER_SECRET,
    SYNTHETIC_SECRET_ASSIGNMENT,
    SYNTHETIC_PRIVATE_URL,
    "Traceback (most recent call last):",
)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def ledger_path(target: Path) -> Path:
    return target / LEDGER


def safe_token(value: object, default: str) -> str:
    token = SAFE_TOKEN.sub("-", str(value or "").strip()).strip("-._:")
    return token[:80] if token else default


def sanitize_value(value: object) -> str:
    raw = str(value or "")
    if "\n" in raw or STACK_TRACE.search(raw):
        return f"redacted:{sha256_text(raw)[:12]}"
    sanitized = raw
    for pattern in (SECRET, EMAIL, URL, ABSOLUTE_PATH):
        sanitized = pattern.sub("[redacted]", sanitized)
    sanitized = sanitized.replace("`", "'").replace("|", "/").strip()
    if len(sanitized) > 180:
        return f"redacted:{sha256_text(sanitized)[:12]}"
    return sanitized or "none"


def unsafe_value(value: object) -> bool:
    raw = str(value or "")
    return any(pattern.search(raw) for pattern in (SECRET, EMAIL, URL, ABSOLUTE_PATH, STACK_TRACE)) or "\n" in raw


def sanitize_facts(facts: object, failures: list[str]) -> dict[str, str]:
    if facts in (None, ""):
        return {}
    if not isinstance(facts, dict):
        failures.append("facts must be an object")
        return {}
    sanitized: dict[str, str] = {}
    for key, value in sorted(facts.items()):
        safe_key = safe_token(key, "field").lower()
        if unsafe_value(key) or unsafe_value(value):
            failures.append(f"unsafe fact redacted: {safe_key}")
        sanitized[safe_key] = sanitize_value(value)
    return sanitized


def validate_scope(target: Path, raw_scope: object, raw_event: dict[str, object], failures: list[str]) -> dict[str, object]:
    if not isinstance(raw_scope, dict):
        failures.append("event scope must be an object")
        raw_scope = {}
    scope_result = scope_contract.normalize_scope(
        target,
        project=raw_scope.get("project"),
        adapter=raw_scope.get("adapter", raw_event.get("surface", "event-ledger")),
        agent=raw_scope.get("agent", "event-ledger"),
        parent_agent=raw_scope.get("parent_agent"),
        run=raw_scope.get("run", raw_event.get("id")),
        source=raw_scope.get("source", "event-ledger"),
        evidence_ref=raw_scope.get("evidence_ref", raw_event.get("evidence_ref", "none")),
        timestamp=raw_scope.get("timestamp", raw_event.get("created_at")),
        status=raw_scope.get("status", raw_event.get("status")),
        trust_level=raw_scope.get("trust_level"),
    )
    if scope_result.get("status") != "PASS":
        failures.extend(str(item) for item in scope_result.get("failures", []))
    scope = scope_result.get("scope", {})
    return scope if isinstance(scope, dict) else {}


def validate_event(target: Path, raw: dict[str, object], line: int) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    if raw.get("schema") != SCHEMA:
        failures.append("event schema mismatch")
    event_id = safe_token(raw.get("id"), f"line-{line}")
    created_at = str(raw.get("created_at", "")).strip()
    if not ISO_UTC.match(created_at):
        failures.append("event created_at must be UTC ISO-8601 seconds with Z suffix")
        created_at = "1970-01-01T00:00:00Z"
    status = str(raw.get("status", "UNKNOWN")).upper()
    if status not in ALLOWED_STATUSES:
        failures.append("event status is outside the allowed enum")
        status = "FAIL"
    lifecycle = str(raw.get("lifecycle", "")).strip()
    if lifecycle not in LIFECYCLE_MAP:
        failures.append("event lifecycle is outside the allowed map")
        lifecycle = "event"
    evidence_ref, evidence_failures = scope_contract.normalize_evidence_ref(raw.get("evidence_ref", "none"))
    failures.extend(evidence_failures)
    if evidence_failures:
        evidence_ref = "invalid"
    summary = sanitize_value(raw.get("summary", "none"))
    if unsafe_value(raw.get("summary", "")):
        failures.append("summary contained unsafe private context")
    facts = sanitize_facts(raw.get("facts", {}), failures)
    scope = validate_scope(target, raw.get("scope"), raw, failures)
    event = {
        "schema": SCHEMA,
        "id": event_id,
        "created_at": created_at,
        "lifecycle": lifecycle,
        "lifecycle_stage": LIFECYCLE_MAP[lifecycle],
        "status": status,
        "surface": safe_token(raw.get("surface"), "unknown").lower(),
        "summary": summary,
        "evidence_ref": evidence_ref,
        "scope": scope,
        "facts": facts,
        "valid": not failures,
    }
    return event, failures


def read_events(target: Path) -> tuple[list[dict[str, object]], list[str]]:
    path = ledger_path(target)
    if not path.exists():
        return [], []
    events: list[dict[str, object]] = []
    failures: list[str] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            failures.append(f"invalid json line: {line_no}")
            continue
        if not isinstance(raw, dict):
            failures.append(f"invalid event payload line: {line_no}")
            continue
        event, event_failures = validate_event(target, raw, line_no)
        events.append(event)
        failures.extend(f"line {line_no}: {failure}" for failure in event_failures)
    return events, failures


def list_events(target: Path) -> dict[str, object]:
    target = target.expanduser().resolve()
    events, failures = read_events(target)
    return {
        "version": VERSION,
        "schema": SCHEMA,
        "status": "FAIL" if failures else "PASS",
        "ledger": rel(ledger_path(target), target),
        "event_count": len(events),
        "events": events,
        "failures": failures,
        "writes": [],
    }


def status(target: Path) -> dict[str, object]:
    target = target.expanduser().resolve()
    events, failures = read_events(target)
    statuses = Counter(str(event.get("status", "UNKNOWN")) for event in events)
    lifecycles = Counter(str(event.get("lifecycle", "event")) for event in events)
    invalid = sum(1 for event in events if not event.get("valid"))
    return {
        "version": VERSION,
        "schema": SCHEMA,
        "status": "FAIL" if failures else "PASS",
        "ledger": rel(ledger_path(target), target),
        "event_count": len(events),
        "invalid_event_count": invalid,
        "status_counts": dict(sorted(statuses.items())),
        "lifecycle_counts": dict(sorted(lifecycles.items())),
        "failures": failures,
        "writes": [],
    }


def inspect_schema() -> dict[str, object]:
    return {
        "version": VERSION,
        "schema": SCHEMA,
        "status": "PASS",
        "ledger": LEDGER.as_posix(),
        "allowed_statuses": sorted(ALLOWED_STATUSES),
        "lifecycle_map": LIFECYCLE_MAP,
        "required_fields": [
            "schema",
            "id",
            "created_at",
            "lifecycle",
            "status",
            "surface",
            "summary",
            "evidence_ref",
            "scope",
        ],
        "writes": [],
    }


def snapshot(target: Path) -> dict[str, str]:
    if not target.exists():
        return {}
    return {
        rel(path, target): sha256_text(path.read_text(encoding="utf-8", errors="replace"))
        for path in sorted(target.rglob("*"))
        if path.is_file()
    }


def append_fixture_event(target: Path, payload: dict[str, object]) -> None:
    path = ledger_path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text(current + json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def scoped(target: Path, *, status_value: str = "PASS", evidence_ref: str = "none") -> dict[str, object]:
    result = scope_contract.normalize_scope(
        target,
        adapter="codex",
        agent="event-ledger",
        run="event-ledger-self-test",
        source="event-ledger",
        evidence_ref=evidence_ref,
        timestamp="2026-05-26T12:00:00Z",
        status=status_value,
    )
    scope = result.get("scope", {})
    return scope if isinstance(scope, dict) else {}


def forbidden_output_failures(payload: object) -> list[str]:
    text = json.dumps(payload, sort_keys=True)
    return [f"unsafe output leaked: {item}" for item in FORBIDDEN_OUTPUT if item in text]


def self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-event-ledger-") as tempdir:
        root = Path(tempdir)
        clean = root / "clean"
        hostile = root / "hostile"
        clean.mkdir()
        hostile.mkdir()
        valid_event = {
            "schema": SCHEMA,
            "id": "evt-001",
            "created_at": "2026-05-26T12:00:00Z",
            "lifecycle": "event",
            "status": "PASS",
            "surface": "cortex",
            "summary": "Cortex audit event inspected without writing memory.",
            "evidence_ref": "docs/agents/cortex/MAP.md",
            "scope": scoped(clean, evidence_ref="docs/agents/cortex/MAP.md"),
            "facts": {"count": 1},
        }
        append_fixture_event(clean, valid_event)
        before_clean = snapshot(clean)
        clean_list = list_events(clean)
        clean_status = status(clean)
        schema_result = inspect_schema()
        after_clean = snapshot(clean)
        if clean_list.get("status") != "PASS" or clean_status.get("status") != "PASS":
            failures.append("clean ledger should pass list and status")
        if clean_status.get("event_count") != 1 or clean_status.get("status_counts", {}).get("PASS") != 1:
            failures.append("clean ledger status counts are wrong")
        if clean_list.get("schema") == "tes-field-report@2":
            failures.append("event ledger must not use the Field Reports schema")
        if "install_id" in json.dumps(clean_list, sort_keys=True):
            failures.append("event ledger must not expose Field Reports install identity")
        if before_clean != after_clean:
            failures.append("event ledger commands must not write during clean inspection")

        append_fixture_event(hostile, valid_event | {"scope": scoped(hostile, evidence_ref="docs/agents/cortex/MAP.md")})
        append_fixture_event(
            hostile,
            {
                "schema": SCHEMA,
                "id": "evt-unsafe",
                "created_at": "2026-05-26T12:01:00Z",
                "lifecycle": "checkpoint",
                "status": "FAIL",
                "surface": "event-ledger",
                "summary": "Traceback (most recent call last): /absolute/unsafe/source.py "
                + SYNTHETIC_SECRET_ASSIGNMENT,
                "evidence_ref": "/absolute/unsafe/evidence.md",
                "scope": scoped(hostile, status_value="FAIL", evidence_ref="none"),
                "facts": {
                    "unsafe_path": "/absolute/unsafe/source.py",
                    "unsafe_email": SYNTHETIC_EMAIL,
                    "unsafe_secret": SYNTHETIC_BEARER_SECRET,
                    "unsafe_url": SYNTHETIC_PRIVATE_REPO_URL,
                },
            },
        )
        (ledger_path(hostile)).write_text(ledger_path(hostile).read_text(encoding="utf-8") + "{not-json}\n", encoding="utf-8")
        before_hostile = snapshot(hostile)
        hostile_list = list_events(hostile)
        hostile_status = status(hostile)
        after_hostile = snapshot(hostile)
        if hostile_list.get("status") != "FAIL" or hostile_status.get("status") != "FAIL":
            failures.append("unsafe or malformed ledger must fail inspection")
        if not hostile_status.get("invalid_event_count"):
            failures.append("unsafe ledger must count invalid events")
        if before_hostile != after_hostile:
            failures.append("event ledger commands must not write during hostile inspection")
        failures.extend(forbidden_output_failures(hostile_list))
        failures.extend(forbidden_output_failures(hostile_status))
        if (hostile / "docs/agents/cortex/TRAIL.md").exists():
            failures.append("event ledger inspection must not write Cortex TRAIL")
        if (hostile / ".tes/field-reports/outbox.jsonl").exists():
            failures.append("event ledger inspection must not write Field Reports outbox")
        if schema_result.get("writes") != []:
            failures.append("schema inspection must report no writes")

    result = {"version": VERSION, "schema": SCHEMA, "status": "FAIL" if failures else "PASS", "failures": failures}
    print(json.dumps(result, indent=2, sort_keys=True))
    if failures:
        print("[event-ledger] FAIL")
        return 1
    print("[event-ledger] PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=("list", "status", "inspect-schema"))
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.command == "list":
        result = list_events(args.target)
    elif args.command == "status":
        result = status(args.target)
    elif args.command == "inspect-schema":
        result = inspect_schema()
    else:
        parser.error("command is required unless --self-test is used")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
