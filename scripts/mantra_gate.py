#!/usr/bin/env python3
"""Validate and record the TES Mantra Gate micro-gate."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Any


VERSION = "0.3.126"
SCHEMA = "tes-mantra-gate@1"
MARKER = "[🍳 Flash-Fry]"
STATUSES = ("PROCEED", "BLOCKED", "NEEDS_REVIEW")
STATUS_WEIGHT = {"PROCEED": 0, "NEEDS_REVIEW": 1, "BLOCKED": 2}
RISK_LEVELS = ("routine", "material", "high-risk", "forbidden")
START_MARKER = "<!-- TES-MANTRA-GATE:START -->"
END_MARKER = "<!-- TES-MANTRA-GATE:END -->"

FIELD_ALIASES = {
    "BEST PATH": "BEST_PATH",
    "BEST-PATH": "BEST_PATH",
}
STATE_CHANGING_FIELDS = ("VERIFY", "SCOPE", "BEST_PATH", "DOCUMENT", "RESOLVE", "STATUS")
SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|authorization|bearer|credential|password|secret|token)\s*[:=]\s*[A-Za-z0-9._:/+=-]+"
)
ABSOLUTE_PATH_RE = re.compile(r"(/Users|/home|/private|/var/folders|[A-Za-z]:\\)[^\s`\"')]+")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

HIGH_RISK_PATTERNS: tuple[tuple[str, str], ...] = (
    ("remote or push", r"\b(git\s+push|push|remote|origin/|upstream)\b"),
    ("secrets or env", r"\b(secret|token|credential|password|api[_-]?key|authorization|bearer|\.env)\b"),
    ("database or migration", r"\b(database|db|schema|migration|persistent|persistence|drizzle|prisma|sql)\b"),
    ("auth or rbac", r"\b(auth|oauth|rbac|permission|role|session|jwt)\b"),
    ("customer data", r"\b(customer|tenant|personal data|pii|real data)\b"),
    ("production", r"\b(production|prod|deploy|release|cutover)\b"),
    ("compliance or legal", r"\b(compliance|legal|privacy|gdpr|hipaa|soc2|sox)\b"),
    ("public surface", r"\b(public api|api surface|breaking change|sdk|cli|npm|package|published)\b"),
    ("destructive git", r"\b(reset --hard|git clean|force push|--force|checkout --|restore --staged)\b"),
    ("generated runtime packaging", r"\b(bundle|runtime package|generated runtime|dist/|docs/dist|packaging)\b"),
)

FORBIDDEN_PATTERNS: tuple[tuple[str, str], ...] = (
    ("destructive git without explicit contract", r"\b(reset --hard|git clean -fd|git clean -xdf|push --force|--force-with-lease)\b"),
    ("secret disclosure", r"\b(print|echo|log|paste|expose|leak)\b.*\b(secret|token|password|api[_-]?key|authorization|bearer)\b"),
    ("production without contract", r"\b(production|prod)\b.*\b(without contract|without approval|no approval|skip approval)\b"),
)
MATERIAL_PATTERNS: tuple[tuple[str, str], ...] = (
    ("write or edit", r"\b(write|edit|patch|modify|create|delete|remove|rename|move)\b"),
    ("commit", r"\b(commit|stage|staged)\b"),
    ("generated artifact", r"\b(generate|generated|materialize|build)\b"),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def normalize_key(key: str) -> str:
    normalized = key.strip().replace("-", "_").replace(" ", "_").upper()
    return FIELD_ALIASES.get(normalized, normalized)


def normalize_gate(raw: dict[str, Any]) -> dict[str, Any]:
    return {normalize_key(str(key)): value for key, value in raw.items()}


def escalate(current: str, candidate: str) -> str:
    if STATUS_WEIGHT[candidate] > STATUS_WEIGHT[current]:
        return candidate
    return current


def visible_mode(gate: dict[str, Any], visible_full: bool) -> str:
    if visible_full:
        return "full"
    raw = str(gate.get("VISIBLE") or gate.get("DISPLAY") or "compact").strip().lower()
    return "full" if raw in {"full", "visible_full", "visible-full"} else "compact"


def resolve_is_clear(value: Any) -> bool:
    if is_blank(value):
        return False
    text = str(value).strip().lower()
    return text == "none found" or text.startswith("resolved")


def _risk_text(action: str = "", scope: Any = None, paths: list[str] | None = None, changed_files: list[str] | None = None) -> str:
    chunks: list[str] = [action]
    if scope is not None:
        chunks.append(json.dumps(scope, ensure_ascii=False, sort_keys=True, default=str))
    chunks.extend(paths or [])
    chunks.extend(changed_files or [])
    return " ".join(chunk for chunk in chunks if chunk).lower()


def _matches(patterns: tuple[tuple[str, str], ...], text: str) -> list[str]:
    return [label for label, pattern in patterns if re.search(pattern, text, flags=re.IGNORECASE)]


def classify_risk(
    action: str = "",
    *,
    scope: Any = None,
    paths: list[str] | None = None,
    changed_files: list[str] | None = None,
    explicit: str | None = None,
) -> dict[str, Any]:
    """Classify Mantra Gate operational risk without reading sensitive content."""
    normalized = (explicit or "").strip().lower()
    if normalized in RISK_LEVELS:
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "risk": normalized,
            "reasons": ["explicit"],
            "matched_terms": [],
        }

    text = _risk_text(action, scope=scope, paths=paths, changed_files=changed_files)
    forbidden = _matches(FORBIDDEN_PATTERNS, text)
    high = _matches(HIGH_RISK_PATTERNS, text)
    material = _matches(MATERIAL_PATTERNS, text)

    if forbidden:
        risk = "forbidden"
        reasons = forbidden
    elif high:
        risk = "high-risk"
        reasons = high
    elif material:
        risk = "material"
        reasons = material
    else:
        risk = "routine"
        reasons = ["no state-changing risk terms detected"]

    return sanitize(
        {
            "schema": SCHEMA,
            "version": VERSION,
            "risk": risk,
            "reasons": sorted(set(reasons)),
            "matched_terms": sorted(set(forbidden + high + material)),
        }
    )


def validate_gate(
    raw_gate: dict[str, Any],
    *,
    state_changing: bool = False,
    closure_claim: bool = False,
    high_risk: bool = False,
    risk: str | None = None,
    visible_full: bool = False,
) -> dict[str, Any]:
    gate = normalize_gate(raw_gate)
    failures: list[str] = []
    status = "PROCEED"
    declared_risk = str(gate.get("RISK") or risk or "").strip().lower()
    if high_risk and declared_risk not in {"forbidden", "high-risk"}:
        declared_risk = "high-risk"
    if declared_risk and declared_risk not in RISK_LEVELS:
        failures.append(f"invalid RISK: {declared_risk}")
        status = escalate(status, "NEEDS_REVIEW")

    declared = str(gate.get("STATUS") or "").strip().upper()
    if not declared:
        failures.append("missing STATUS")
        status = escalate(status, "BLOCKED")
    elif declared not in STATUSES:
        failures.append(f"invalid STATUS: {declared}")
        status = escalate(status, "BLOCKED")
    else:
        status = escalate(status, declared)

    verify_missing = is_blank(gate.get("VERIFY"))
    if verify_missing:
        failures.append("missing VERIFY")
        status = escalate(status, "BLOCKED")

    if state_changing:
        for field in STATE_CHANGING_FIELDS:
            if field == "VERIFY" and verify_missing:
                continue
            if is_blank(gate.get(field)):
                failures.append(f"missing {field}")
                status = escalate(status, "NEEDS_REVIEW")

    if state_changing and is_blank(gate.get("SCOPE")):
        status = escalate(status, "NEEDS_REVIEW")

    if state_changing and is_blank(gate.get("DOCUMENT")):
        status = escalate(status, "NEEDS_REVIEW")

    if closure_claim and is_blank(gate.get("ORACLE")):
        failures.append("missing ORACLE for closure claim")
        status = escalate(status, "BLOCKED")

    if state_changing and not resolve_is_clear(gate.get("RESOLVE")):
        failures.append("RESOLVE is missing or unresolved")
        status = escalate(status, "BLOCKED")

    mode = visible_mode(gate, visible_full)
    if declared_risk == "forbidden":
        failures.append("forbidden risk class requires stop")
        status = escalate(status, "BLOCKED")

    valid = not failures and status == declared
    if failures and declared == "PROCEED":
        valid = False

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "marker": MARKER,
        "status": status,
        "declared_status": declared or "MISSING",
        "risk": declared_risk or "unclassified",
        "valid": valid,
        "visible": mode,
        "failures": failures,
        "gate": gate,
    }


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): sanitize(child) for key, child in value.items()}
    if isinstance(value, list):
        return [sanitize(child) for child in value]
    if isinstance(value, str):
        text = SECRET_RE.sub("[REDACTED_SECRET]", value)
        text = ABSOLUTE_PATH_RE.sub("[REDACTED_PATH]", text)
        return EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    return value


def default_record_path(target: Path) -> Path:
    field_reports_root = target / ".tes/field-reports"
    if field_reports_root.exists():
        return field_reports_root / "mantra-gates.jsonl"
    return target / ".tes/mantra-gates/records.jsonl"


def record_gate(target: Path, action: str, result: dict[str, Any], *, record_path: Path | None = None) -> Path:
    destination = record_path or default_record_path(target)
    if not destination.is_absolute():
        destination = target / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "schema": SCHEMA,
        "recorded_at": utc_now(),
        "action": action,
        "marker": MARKER,
        "status": result["status"],
        "visible": result["visible"],
        "result": {
            "valid": result["valid"],
            "failures": result["failures"],
            "declared_status": result["declared_status"],
        },
        "gate": result["gate"],
    }
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(sanitize(event), ensure_ascii=False, sort_keys=True) + "\n")
    return destination


def load_gate(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("gate file must contain a JSON object")
    return data


def sample_gate(**overrides: Any) -> dict[str, Any]:
    gate = {
        "VERIFY": "git status, relevant file, and requested action checked",
        "SCOPE": "only the requested local state-changing action",
        "BEST_PATH": "smallest safe local change",
        "DOCUMENT": "local evidence record",
        "ORACLE": "focused deterministic gate",
        "RESOLVE": "none found",
        "STATUS": "PROCEED",
    }
    gate.update(overrides)
    return gate


def self_test() -> dict[str, Any]:
    failures: list[str] = []

    complete = validate_gate(sample_gate(), state_changing=True, closure_claim=True)
    if complete["status"] != "PROCEED" or not complete["valid"]:
        failures.append("complete gate must pass")

    missing_verify = validate_gate(sample_gate(VERIFY=""), state_changing=True)
    if missing_verify["status"] != "BLOCKED" or "missing VERIFY" not in missing_verify["failures"]:
        failures.append("missing VERIFY must block")

    missing_scope = validate_gate(sample_gate(SCOPE=""), state_changing=True)
    if missing_scope["status"] != "NEEDS_REVIEW":
        failures.append("missing SCOPE on state-changing action must need review")

    missing_oracle = validate_gate(sample_gate(ORACLE=""), state_changing=True, closure_claim=True)
    if missing_oracle["status"] != "BLOCKED":
        failures.append("missing ORACLE on closure claim must block")

    high_risk_compact = validate_gate(sample_gate(), state_changing=True, high_risk=True)
    if high_risk_compact["status"] != "PROCEED" or high_risk_compact["visible"] != "compact":
        failures.append("compact display with a complete high-risk gate must pass")

    high_risk_full = validate_gate(sample_gate(VISIBLE="full"), state_changing=True, high_risk=True)
    if high_risk_full["status"] != "PROCEED" or high_risk_full["visible"] != "full":
        failures.append("high-risk full gate must proceed when otherwise complete")

    routine = classify_risk("read docs and report")
    if routine["risk"] != "routine":
        failures.append("read-only analysis must classify as routine")

    push = classify_risk("commit and git push to origin")
    if push["risk"] != "high-risk":
        failures.append("push must classify as high-risk")

    forbidden = classify_risk("git reset --hard and echo token=abc123")
    if forbidden["risk"] != "forbidden":
        failures.append("destructive git or secret disclosure must classify as forbidden")

    forbidden_gate = validate_gate(sample_gate(RISK="forbidden", VISIBLE="full"), state_changing=True)
    if forbidden_gate["status"] != "BLOCKED":
        failures.append("forbidden risk class must block")

    with tempfile.TemporaryDirectory(prefix="tes-mantra-gate-") as tmp:
        target = Path(tmp)
        (target / ".tes/field-reports").mkdir(parents=True)
        result = validate_gate(
            sample_gate(VERIFY="checked /Users/example/project and token=abc123"),
            state_changing=True,
            closure_claim=True,
        )
        record = record_gate(target, "self-test", result)
        text = record.read_text(encoding="utf-8")
        if MARKER not in text or "VERIFY" not in text:
            failures.append("compact marker record must retain full gate evidence")
        if "/Users/example/project" in text or "token=abc123" in text:
            failures.append("record must sanitize paths and secrets")
        if "owner@example.com" in json.dumps(sanitize({"email": "owner@example.com"})):
            failures.append("record must sanitize emails")

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "FAIL" if failures else "PASS",
        "marker": MARKER,
        "failures": failures,
    }


def exit_code(status: str, valid: bool) -> int:
    if status == "PROCEED" and valid:
        return 0
    if status == "NEEDS_REVIEW":
        return 2
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate or record a TES Mantra Gate.")
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    emit = subparsers.add_parser("emit-marker")
    emit.set_defaults(command="emit-marker")

    validate = subparsers.add_parser("validate")
    validate.add_argument("--gate", required=True, type=Path)
    validate.add_argument("--target", type=Path, default=Path("."))
    validate.add_argument("--action", default="state-changing action")
    validate.add_argument("--record", action="store_true")
    validate.add_argument("--record-path", type=Path)
    validate.add_argument("--emit-marker", action="store_true")
    validate.add_argument("--state-changing", action="store_true")
    validate.add_argument("--closure-claim", action="store_true")
    validate.add_argument("--high-risk", action="store_true")
    validate.add_argument("--risk", choices=RISK_LEVELS)
    validate.add_argument("--visible-full", action="store_true")
    validate.set_defaults(command="validate")

    classify = subparsers.add_parser("classify-risk")
    classify.add_argument("--action", default="")
    classify.add_argument("--scope", default="")
    classify.add_argument("--path", action="append", default=[])
    classify.add_argument("--changed-file", action="append", default=[])
    classify.add_argument("--explicit", choices=RISK_LEVELS)
    classify.set_defaults(command="classify-risk")

    args = parser.parse_args(argv)

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "PASS" else 1

    if args.command == "emit-marker":
        print(MARKER)
        return 0

    if args.command == "validate":
        result = validate_gate(
            load_gate(args.gate),
            state_changing=args.state_changing,
            closure_claim=args.closure_claim,
            high_risk=args.high_risk,
            risk=args.risk,
            visible_full=args.visible_full,
        )
        if args.record:
            record_path = record_gate(args.target, args.action, result, record_path=args.record_path)
            result["record"] = str(record_path)
        if args.emit_marker and result["status"] == "PROCEED":
            print(MARKER)
        else:
            print(json.dumps(sanitize(result), indent=2, sort_keys=True))
        return exit_code(result["status"], bool(result["valid"]))

    if args.command == "classify-risk":
        print(
            json.dumps(
                classify_risk(
                    args.action,
                    scope=args.scope,
                    paths=args.path,
                    changed_files=args.changed_file,
                    explicit=args.explicit,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
