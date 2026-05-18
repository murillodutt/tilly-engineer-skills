#!/usr/bin/env python3
"""Read-only adoption oracle for TES Mantra Gate records."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

import mantra_gate


VERSION = mantra_gate.VERSION
SCHEMA = "tes-mantra-gate-adoption@1"
STATUSES = ("OK", "DEGRADED", "BYPASS_SUSPECTED", "BLOCKED", "NEEDS_REVIEW")
STATUS_WEIGHT = {"OK": 0, "DEGRADED": 1, "BYPASS_SUSPECTED": 2, "NEEDS_REVIEW": 3, "BLOCKED": 4}
GATE_FIELDS = ("VERIFY", "SCOPE", "BEST_PATH", "DOCUMENT", "ORACLE", "RESOLVE", "STATUS")


def escalate(current: str, candidate: str) -> str:
    if STATUS_WEIGHT[candidate] > STATUS_WEIGHT[current]:
        return candidate
    return current


def run_git(target: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=target, capture_output=True, text=True, check=False)


def lines(output: str) -> list[str]:
    return [line.strip() for line in output.splitlines() if line.strip()]


def git_state(target: Path) -> dict[str, Any]:
    root = run_git(target, ["rev-parse", "--show-toplevel"])
    if root.returncode != 0:
        return {
            "available": False,
            "reason": "not a git repository",
            "diff_files": [],
            "staged_files": [],
            "last_commit_files": [],
            "status_short": [],
            "last_commit": None,
            "last_commit_time": None,
        }

    diff_files = lines(run_git(target, ["diff", "--name-only"]).stdout)
    staged_files = lines(run_git(target, ["diff", "--cached", "--name-only"]).stdout)
    status_short = lines(run_git(target, ["status", "--short"]).stdout)
    last_commit = run_git(target, ["rev-parse", "--short", "HEAD"])
    last_commit_time = run_git(target, ["log", "-1", "--format=%cI"])
    commit_files = run_git(target, ["show", "--name-only", "--format=", "--no-renames", "HEAD"])
    return {
        "available": True,
        "root": root.stdout.strip(),
        "diff_files": diff_files,
        "staged_files": staged_files,
        "last_commit_files": lines(commit_files.stdout) if commit_files.returncode == 0 else [],
        "status_short": status_short,
        "last_commit": last_commit.stdout.strip() if last_commit.returncode == 0 else None,
        "last_commit_time": last_commit_time.stdout.strip() if last_commit_time.returncode == 0 else None,
    }


def record_paths(target: Path) -> list[Path]:
    return [
        target / ".tes/field-reports/mantra-gates.jsonl",
        target / ".tes/mantra-gates/records.jsonl",
    ]


def load_records(target: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in record_paths(target):
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                records.append(
                    {
                        "path": str(path),
                        "line": line_number,
                        "decode_error": True,
                        "gate": {},
                        "visible": "unknown",
                    }
                )
                continue
            if isinstance(event, dict):
                event.setdefault("path", str(path))
                event.setdefault("line", line_number)
                records.append(event)
    return records


def gate_from_record(record: dict[str, Any]) -> dict[str, Any]:
    gate = record.get("gate")
    if isinstance(gate, dict):
        return gate
    return {key: value for key, value in record.items() if key.upper() in GATE_FIELDS}


def visible_from_record(record: dict[str, Any], gate: dict[str, Any]) -> str:
    visible = str(record.get("visible") or gate.get("VISIBLE") or gate.get("DISPLAY") or "compact").lower()
    return "full" if visible in {"full", "visible_full", "visible-full"} else "compact"


def is_state_changing(action: str, explicit: bool, commit_push: bool, state: dict[str, Any], risk: str) -> bool:
    if explicit or commit_push:
        return True
    if state["diff_files"] or state["staged_files"]:
        return True
    if action and risk != "routine":
        return True
    return False


def summarize_metrics(records: list[dict[str, Any]], validations: list[dict[str, Any]], status: str) -> dict[str, Any]:
    visible_counts = Counter()
    declared_counts = Counter()
    missing_fields = Counter()
    without_closure_oracle = 0

    for record in records:
        gate = mantra_gate.normalize_gate(gate_from_record(record))
        visible_counts[visible_from_record(record, gate)] += 1
        declared_counts[str(gate.get("STATUS") or "MISSING")] += 1
        for field in GATE_FIELDS:
            if mantra_gate.is_blank(gate.get(field)):
                missing_fields[field] += 1
        if mantra_gate.is_blank(gate.get("ORACLE")):
            without_closure_oracle += 1

    return {
        "records": len(records),
        "compact": visible_counts.get("compact", 0),
        "full": visible_counts.get("full", 0),
        "status_counts": dict(sorted(declared_counts.items())),
        "needs_review": sum(1 for item in validations if item.get("status") == "NEEDS_REVIEW"),
        "blocked": sum(1 for item in validations if item.get("status") == "BLOCKED"),
        "bypass_suspected": 1 if status == "BYPASS_SUSPECTED" else 0,
        "missing_field_counts": dict(sorted(missing_fields.items())),
        "actions_without_closure_oracle": without_closure_oracle,
        "time_between_gate_and_action_seconds": None,
    }


def parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def gate_action_delta_seconds(records: list[dict[str, Any]], state: dict[str, Any]) -> int | None:
    if not records:
        return None
    gate_time = parse_time(records[-1].get("recorded_at"))
    action_time = parse_time(state.get("last_commit_time"))
    if gate_time is None or action_time is None:
        return None
    return int(abs((action_time - gate_time).total_seconds()))


def evaluate(
    target: Path,
    *,
    action: str = "",
    state_changing: bool = False,
    closure_claim: bool = False,
    commit_push: bool = False,
) -> dict[str, Any]:
    target = target.resolve()
    state = git_state(target)
    changed_files = list(dict.fromkeys(state["diff_files"] + state["staged_files"] + state["last_commit_files"]))
    effective_action = f"{action} git push" if commit_push else action
    risk_info = mantra_gate.classify_risk(effective_action, changed_files=changed_files)
    risk = str(risk_info["risk"])
    action_changes_state = is_state_changing(effective_action, state_changing, commit_push, state, risk)
    records = load_records(target)

    status = "OK"
    findings: list[dict[str, Any]] = []
    validations: list[dict[str, Any]] = []

    if risk == "forbidden":
        status = escalate(status, "BLOCKED")
        findings.append({"type": "forbidden_risk", "detail": "forbidden risk class requires an explicit stop"})

    if action_changes_state and not records:
        status = escalate(status, "BYPASS_SUSPECTED")
        findings.append({"type": "missing_gate_record", "detail": "state-changing signal has no nearby Mantra Gate record"})

    for record in records:
        gate = gate_from_record(record)
        visible = visible_from_record(record, gate)
        result = mantra_gate.validate_gate(
            gate,
            state_changing=action_changes_state,
            closure_claim=closure_claim,
            risk=risk,
            visible_full=visible == "full",
        )
        validations.append(
            {
                "path": record.get("path"),
                "line": record.get("line"),
                "status": result["status"],
                "visible": result["visible"],
                "valid": result["valid"],
                "failures": result["failures"],
            }
        )
        if result["status"] == "BLOCKED":
            status = escalate(status, "BLOCKED")
        elif result["status"] == "NEEDS_REVIEW":
            status = escalate(status, "NEEDS_REVIEW")
        elif not result["valid"]:
            status = escalate(status, "DEGRADED")

    if closure_claim and records:
        latest_gate = mantra_gate.normalize_gate(gate_from_record(records[-1]))
        if mantra_gate.is_blank(latest_gate.get("ORACLE")):
            status = escalate(status, "BLOCKED")
            findings.append({"type": "missing_closure_oracle", "detail": "closure claim requires ORACLE"})

    if risk == "high-risk" and records:
        latest_visible = visible_from_record(records[-1], gate_from_record(records[-1]))
        if latest_visible != "full":
            status = escalate(status, "NEEDS_REVIEW")
            findings.append({"type": "compact_high_risk", "detail": "high-risk action requires visible full gate"})

    metrics = summarize_metrics(records, validations, status)
    metrics["time_between_gate_and_action_seconds"] = gate_action_delta_seconds(records, state)
    field_report_outbox = target / ".tes/field-reports/outbox.jsonl"

    return mantra_gate.sanitize(
        {
            "schema": SCHEMA,
            "version": VERSION,
            "status": status,
            "target": str(target),
            "action": effective_action or "read-only analysis",
            "state_changing": action_changes_state,
            "closure_claim": closure_claim,
            "commit_push": commit_push,
            "risk": risk_info,
            "git": state,
            "records": {
                "count": len(records),
                "paths_checked": [str(path) for path in record_paths(target)],
                "field_reports_outbox_present": field_report_outbox.exists(),
            },
            "validations": validations,
            "findings": findings,
            "metrics": metrics,
            "recovery": recovery(status),
        }
    )


def recovery(status: str) -> str:
    if status == "OK":
        return "continue; compact marker is sufficient when the full internal record exists"
    if status == "DEGRADED":
        return "repair the gate record or rerun the action with a complete gate"
    if status == "BYPASS_SUSPECTED":
        return "stop closure; reconstruct evidence and record a Mantra Gate before claiming progress"
    if status == "NEEDS_REVIEW":
        return "show the full gate, resolve ambiguity, or request approval"
    return "stop; resolve the blocker or forbidden risk before acting"


def write_record(target: Path, gate: dict[str, Any], *, visible: str = "compact") -> None:
    result = mantra_gate.validate_gate(gate, state_changing=True, visible_full=visible == "full")
    if visible == "full":
        result["gate"]["VISIBLE"] = "full"
        result["visible"] = "full"
    mantra_gate.record_gate(target, "self-test", result)


def self_test() -> dict[str, Any]:
    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-") as tmp:
        target = Path(tmp)
        (target / ".tes/field-reports").mkdir(parents=True)
        write_record(target, mantra_gate.sample_gate(), visible="compact")
        routine = evaluate(target, action="edit docs", state_changing=True)
        if routine["status"] != "OK" or routine["metrics"]["compact"] != 1:
            failures.append("routine compact gate with full internal record must pass")

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-") as tmp:
        target = Path(tmp)
        (target / ".tes/field-reports").mkdir(parents=True)
        write_record(target, mantra_gate.sample_gate(), visible="compact")
        high_compact = evaluate(target, action="git push to origin", state_changing=True)
        if high_compact["status"] != "NEEDS_REVIEW":
            failures.append("high-risk compact gate must need review")

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-") as tmp:
        target = Path(tmp)
        (target / ".tes/field-reports").mkdir(parents=True)
        write_record(target, mantra_gate.sample_gate(VISIBLE="full"), visible="full")
        high_full = evaluate(target, action="git push to origin", state_changing=True)
        if high_full["status"] != "OK" or high_full["metrics"]["full"] != 1:
            failures.append("high-risk full gate must pass")

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-") as tmp:
        target = Path(tmp)
        (target / ".tes/field-reports").mkdir(parents=True)
        write_record(target, mantra_gate.sample_gate(VERIFY=""), visible="compact")
        missing_verify = evaluate(target, action="edit docs", state_changing=True)
        if missing_verify["status"] != "BLOCKED":
            failures.append("missing VERIFY must block adoption")

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-") as tmp:
        target = Path(tmp)
        (target / ".tes/field-reports").mkdir(parents=True)
        write_record(target, mantra_gate.sample_gate(ORACLE=""), visible="compact")
        missing_oracle = evaluate(target, action="claim closure", state_changing=True, closure_claim=True)
        if missing_oracle["status"] != "BLOCKED":
            failures.append("missing ORACLE on closure claim must block")

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-") as tmp:
        target = Path(tmp)
        state_change = evaluate(target, action="edit file", state_changing=True)
        if state_change["status"] != "BYPASS_SUSPECTED":
            failures.append("state-changing action without a gate must be bypass suspected")

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-") as tmp:
        target = Path(tmp)
        push = evaluate(target, action="commit release", commit_push=True)
        if push["status"] not in {"BYPASS_SUSPECTED", "BLOCKED"}:
            failures.append("commit/push without a gate must be bypass suspected or blocked")

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-") as tmp:
        target = Path(tmp)
        (target / ".tes/field-reports").mkdir(parents=True)
        write_record(
            target,
            mantra_gate.sample_gate(
                VERIFY="checked /Users/example/project, owner@example.com, token=abc123",
            ),
            visible="compact",
        )
        report = evaluate(target, action="edit docs", state_changing=True)
        encoded = json.dumps(report, ensure_ascii=False)
        if "/Users/example/project" in encoded or "owner@example.com" in encoded or "token=abc123" in encoded:
            failures.append("adoption report must sanitize path, email, and secret content")

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-") as tmp:
        target = Path(tmp)
        readonly = evaluate(target, action="read docs and report")
        if readonly["status"] != "OK" or readonly["state_changing"]:
            failures.append("read-only analysis must not produce a bypass false positive")

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check TES Mantra Gate adoption health without changing state.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--target", type=Path, default=Path("."))
    parser.add_argument("--action", default="")
    parser.add_argument("--state-changing", action="store_true")
    parser.add_argument("--closure-claim", action="store_true")
    parser.add_argument("--commit-push", action="store_true")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "PASS" else 1

    result = evaluate(
        args.target,
        action=args.action,
        state_changing=args.state_changing,
        closure_claim=args.closure_claim,
        commit_push=args.commit_push,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] in {"OK", "DEGRADED"} else 1


if __name__ == "__main__":
    sys.exit(main())
