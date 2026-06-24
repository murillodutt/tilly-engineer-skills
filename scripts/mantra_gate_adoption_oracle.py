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
MANTRA_GATE_OWNER_TERMS = (
    "## Mantra Gate",
    "TES Mantra Gate",
    "destructive, remote, release, sync",
    "high-impact",
    "local edits",
)
RETIRED_LOCAL_GATE_MARKERS = (
    "retired local gate",
    "legacy local gate",
    "local pre-action gate",
    "project-local pre-action gate",
    "retired Claude marker",
)
BOOTLOADER_DUPLICATED_MANTRA_GATE_FRAGMENTS = (
    "Full gate fields are",
    "the full gate is still retained as evidence",
)


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


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def surface_candidates(target: Path) -> list[dict[str, str]]:
    source_root = target / "src/adapters"
    if source_root.exists():
        return [
            {
                "adapter": "codex",
                "kind": "bootloader",
                "path": "src/adapters/codex/AGENTS.md",
                "route": ".agents/skills/tes-engineering-discipline/SKILL.md",
            },
            {
                "adapter": "codex",
                "kind": "owner",
                "path": "src/adapters/codex/skills/tes-engineering-discipline/SKILL.md",
            },
            {
                "adapter": "claude",
                "kind": "bootloader",
                "path": "src/adapters/claude/CLAUDE.md",
                "route": ".claude/skills/tes-engineering-discipline/SKILL.md",
            },
            {
                "adapter": "claude",
                "kind": "owner",
                "path": "src/adapters/claude/skills/tes-engineering-discipline/SKILL.md",
            },
            {
                "adapter": "cursor",
                "kind": "owner",
                "path": "src/adapters/cursor/rules/tes-engineering-discipline.mdc",
            },
        ]
    return [
        {
            "adapter": "codex",
            "kind": "bootloader",
            "path": "AGENTS.md",
            "route": ".agents/skills/tes-engineering-discipline/SKILL.md",
        },
        {
            "adapter": "codex",
            "kind": "owner",
            "path": ".agents/skills/tes-engineering-discipline/SKILL.md",
        },
        {
            "adapter": "claude",
            "kind": "bootloader",
            "path": "CLAUDE.md",
            "route": ".claude/skills/tes-engineering-discipline/SKILL.md",
        },
        {
            "adapter": "claude",
            "kind": "owner",
            "path": ".claude/skills/tes-engineering-discipline/SKILL.md",
        },
        {
            "adapter": "cursor",
            "kind": "owner",
            "path": ".cursor/rules/tes-engineering-discipline.mdc",
        },
    ]


def hook_health(target: Path) -> dict[str, Any]:
    hooks = []
    checks = (
        ("codex", ".codex/config.toml", ("TES first-session post-install hook", ".tes/bin/tes_install.py")),
        ("claude", ".claude/settings.json", (".tes/bin/tes_install.py", "--agent claude")),
        ("cursor", ".cursor/hooks.json", (".tes/bin/tes_install.py", "--agent cursor")),
    )
    for adapter, relpath, terms in checks:
        path = target / relpath
        text = read_text(path)
        if not path.exists():
            status = "NOT_APPLIED"
        elif all(term in text for term in terms):
            status = "PRESENT"
        else:
            status = "DEGRADED"
        hooks.append({"adapter": adapter, "path": relpath, "status": status})
    return {
        "status": "DEGRADED" if any(item["status"] == "DEGRADED" for item in hooks) else "OK",
        "hooks": hooks,
    }


def surface_health(target: Path) -> dict[str, Any]:
    surfaces = []
    findings: list[dict[str, Any]] = []
    existing = 0

    for item in surface_candidates(target):
        path = target / item["path"]
        text = read_text(path)
        present = path.exists()
        if present:
            existing += 1
        surface = {
            "adapter": item["adapter"],
            "kind": item["kind"],
            "path": item["path"],
            "present": present,
            "status": "OK" if present else "NOT_APPLIED",
        }

        if not present:
            surfaces.append(surface)
            continue

        if item["kind"] == "owner":
            missing = [term for term in MANTRA_GATE_OWNER_TERMS if term not in text]
            if missing:
                surface["status"] = "DEGRADED"
                findings.append(
                    {
                        "type": "mantra_gate_owner_missing_terms",
                        "path": item["path"],
                        "missing": missing,
                    }
                )
        elif item["kind"] == "bootloader":
            route = str(item.get("route") or "")
            missing = [term for term in ("TES Mantra Gate", route) if term not in text]
            duplicated = [fragment for fragment in BOOTLOADER_DUPLICATED_MANTRA_GATE_FRAGMENTS if fragment in text]
            if missing or duplicated:
                surface["status"] = "DEGRADED"
                findings.append(
                    {
                        "type": "bootloader_must_route_to_skill",
                        "path": item["path"],
                        "missing": missing,
                        "duplicated_fragments": duplicated,
                    }
                )

        retired = [marker for marker in RETIRED_LOCAL_GATE_MARKERS if marker.lower() in text.lower()]
        if retired:
            surface["status"] = "DEGRADED"
            findings.append(
                {
                    "type": "retired_local_gate_marker_active",
                    "path": item["path"],
                    "markers": retired,
                }
            )
        surfaces.append(surface)

    status = "NOT_APPLIED" if existing == 0 else ("DEGRADED" if findings else "OK")
    return {
        "status": status,
        "surfaces": surfaces,
        "findings": findings,
        "historical_evidence_policy": "retired text is allowed in docs/evidence and archived records, not active bootloaders/rules",
        "hooks": hook_health(target),
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


def operation_mode(*, state_changing: bool, closure_claim: bool, commit_push: bool, audit_history: bool) -> str:
    if commit_push:
        return "commit-push"
    if closure_claim:
        return "closure-claim"
    if state_changing:
        return "state-changing"
    if audit_history:
        return "audit-history"
    return "health"


def current_action_changes_state(mode: str) -> bool:
    return mode in {"state-changing", "closure-claim", "commit-push"}


def is_state_changing(action: str, explicit: bool, commit_push: bool, state: dict[str, Any], risk: str) -> bool:
    if explicit or commit_push:
        return True
    if state["diff_files"] or state["staged_files"]:
        return True
    if action and risk != "routine":
        return True
    return False


def historical_risk(record: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    raw = mantra_gate.normalize_gate(gate)
    return mantra_gate.classify_risk(
        str(record.get("action") or ""),
        scope=raw.get("SCOPE"),
        changed_files=[
            str(raw.get("VERIFY") or ""),
            str(raw.get("BEST_PATH") or ""),
            str(raw.get("DOCUMENT") or ""),
            str(raw.get("ORACLE") or ""),
        ],
        explicit=str(raw.get("RISK") or "").lower() or None,
    )


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
    audit_history: bool = False,
) -> dict[str, Any]:
    target = target.resolve()
    state = git_state(target)
    changed_files = list(dict.fromkeys(state["diff_files"] + state["staged_files"] + state["last_commit_files"]))
    effective_action = f"{action} git push" if commit_push else action
    mode = operation_mode(
        state_changing=state_changing,
        closure_claim=closure_claim,
        commit_push=commit_push,
        audit_history=audit_history,
    )
    risk_files = changed_files if current_action_changes_state(mode) else []
    risk_info = mantra_gate.classify_risk(effective_action, changed_files=risk_files)
    risk = str(risk_info["risk"])
    action_changes_state = current_action_changes_state(mode)
    records = load_records(target)

    status = "OK"
    findings: list[dict[str, Any]] = []
    validations: list[dict[str, Any]] = []
    surfaces = surface_health(target)
    if surfaces["status"] == "DEGRADED":
        status = escalate(status, "DEGRADED")
        findings.append({"type": "mantra_gate_surface_health", "detail": "active Mantra Gate runtime surfaces need repair"})

    if risk == "forbidden":
        status = escalate(status, "BLOCKED")
        findings.append({"type": "forbidden_risk", "detail": "forbidden risk class requires an explicit stop"})

    if action_changes_state and not records:
        status = escalate(status, "BYPASS_SUSPECTED")
        findings.append({"type": "missing_gate_record", "detail": "state-changing signal has no nearby Mantra Gate record"})

    for record in records:
        gate = gate_from_record(record)
        visible = visible_from_record(record, gate)
        record_risk = historical_risk(record, gate)

        if mode == "health":
            health_gate = dict(gate)
            health_gate.pop("RISK", None)
            health_gate.pop("risk", None)
            result = mantra_gate.validate_gate(
                health_gate,
                state_changing=False,
                closure_claim=False,
                risk=None,
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
                    "historical_risk": record_risk.get("risk"),
                }
            )
            # Health mode is a read-only audit of *historical* gate records, not
            # an active gate on the current action. A malformed or stale record
            # (e.g. an old STATUS vocabulary like "PASS") is a review item, not a
            # hard stop: it must never escalate the adoption status to BLOCKED and
            # bring down installed certification. Reserve BLOCKED for the active
            # gate (state-changing / closure / commit-push modes); here cap a bad
            # historical record at NEEDS_REVIEW so the record stays traceable
            # (its own validation still reads BLOCKED) without failing the install.
            if result["status"] == "BLOCKED" or not result["valid"]:
                # Surface the offending historical record as a finding so the
                # cause is visible at the certification summary level, not only
                # when the adoption oracle is run directly. Without this, the
                # wrapping certification finding fell through to surface_health
                # (status OK) and disagreed with the NEEDS_REVIEW verdict. The
                # path/line let `field_reports prune-invalid-mantra-gates` and a
                # local-diagnostic operator point straight at the record.
                findings.append(
                    {
                        "type": "invalid_historical_record",
                        "path": record.get("path"),
                        "line": record.get("line"),
                        "record_status": result["status"],
                        "failures": result["failures"],
                        "detail": "stale or schema-invalid Mantra Gate record in the ledger; "
                        "prune it with `field_reports prune-invalid-mantra-gates`",
                    }
                )
            if result["status"] == "BLOCKED":
                status = escalate(status, "NEEDS_REVIEW")
            elif not result["valid"]:
                status = escalate(status, "DEGRADED")
            continue

        active_risk = str(record_risk.get("risk") or "routine") if mode == "audit-history" else risk
        result = mantra_gate.validate_gate(
            gate,
            state_changing=action_changes_state or mode == "audit-history",
            closure_claim=closure_claim,
            risk=active_risk,
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
                "historical_risk": record_risk.get("risk"),
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

    metrics = summarize_metrics(records, validations, status)
    metrics["time_between_gate_and_action_seconds"] = gate_action_delta_seconds(records, state)
    field_report_outbox = target / ".tes/field-reports/outbox.jsonl"

    return mantra_gate.sanitize(
        {
            "schema": SCHEMA,
            "version": VERSION,
            "status": status,
            "target": str(target),
            "mode": mode,
            "action": effective_action or "read-only analysis",
            "state_changing": action_changes_state,
            "dirty_worktree_present": bool(state["diff_files"] or state["staged_files"]),
            "closure_claim": closure_claim,
            "commit_push": commit_push,
            "audit_history": audit_history,
            "risk": risk_info,
            "git": state,
            "records": {
                "count": len(records),
                "paths_checked": [str(path) for path in record_paths(target)],
                "field_reports_outbox_present": field_report_outbox.exists(),
            },
            "validations": validations,
            "findings": findings,
            "surface_health": surfaces,
            "metrics": metrics,
            "recovery": recovery(status),
        },
        # On-target operator output: under TES_LOCAL_DIAGNOSTIC=1 the ledger
        # paths in validations/findings render target-relative so the operator
        # can act on them. Default (and all shipped/persisted content) stays
        # fully redacted because this kwarg is only passed here, not at write.
        local_target=target,
    )


def recovery(status: str) -> str:
    if status == "OK":
        return "continue; compact marker is sufficient when the full internal record exists"
    if status == "DEGRADED":
        return "repair the gate record or rerun the action with a complete gate"
    if status == "BYPASS_SUSPECTED":
        return "stop closure; reconstruct evidence and record a Mantra Gate before claiming progress"
    if status == "NEEDS_REVIEW":
        return "resolve ambiguity, request approval, or report audit detail when explicitly needed"
    return "stop; resolve the blocker or forbidden risk before acting"


def write_record(target: Path, gate: dict[str, Any], *, visible: str = "compact", action: str = "self-test") -> None:
    result = mantra_gate.validate_gate(gate, state_changing=True, visible_full=visible == "full")
    if visible == "full":
        result["gate"]["VISIBLE"] = "full"
        result["visible"] = "full"
    mantra_gate.record_gate(target, action, result)


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
        if high_compact["status"] != "OK" or high_compact["metrics"]["compact"] != 1:
            failures.append("compact display with a complete high-risk gate record must pass")

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
        synthetic_path = "/" + "Users/example/project"
        synthetic_email = "owner" + "@example.com"
        synthetic_secret = "token=" + "abc" + "123"
        write_record(
            target,
            mantra_gate.sample_gate(
                VERIFY="checked " + synthetic_path + ", " + synthetic_email + ", " + synthetic_secret,
            ),
            visible="compact",
        )
        report = evaluate(target, action="edit docs", state_changing=True)
        encoded = json.dumps(report, ensure_ascii=False)
        if synthetic_path in encoded or synthetic_email in encoded or synthetic_secret in encoded:
            failures.append("adoption report must sanitize path, email, and secret content")

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-") as tmp:
        target = Path(tmp)
        readonly = evaluate(target, action="read docs and report")
        if readonly["status"] != "OK" or readonly["state_changing"]:
            failures.append("read-only analysis must not produce a bypass false positive")

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-") as tmp:
        target = Path(tmp)
        (target / ".agents/skills/tes-engineering-discipline").mkdir(parents=True)
        (target / "AGENTS.md").write_text(
            "Use the TES Mantra Gate defined in "
            "`.agents/skills/tes-engineering-discipline/SKILL.md` for destructive, remote, "
            "release, sync, secret-bearing, or high-impact state changes. Do not reintroduce.\n",
            encoding="utf-8",
        )
        (target / ".agents/skills/tes-engineering-discipline/SKILL.md").write_text(
            "## Mantra Gate\n\nUse the TES Mantra Gate for destructive, remote, release, sync, "
            "secret-bearing, or high-impact state changes. Ordinary local edits do not block "
            "on gate artifacts, markers, or skill loading.\n",
            encoding="utf-8",
        )
        (target / "docs/evidence").mkdir(parents=True)
        (target / "docs/evidence/retired.md").write_text(
            "Historical note: retired local gate text is preserved here.\n",
            encoding="utf-8",
        )
        healthy_surface = evaluate(target)
        if healthy_surface["status"] != "OK":
            failures.append("active surface health must ignore historical retired text")

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-") as tmp:
        target = Path(tmp)
        (target / ".agents/skills/tes-engineering-discipline").mkdir(parents=True)
        (target / "AGENTS.md").write_text(
            "TES Mantra Gate\n\nFull gate fields are VERIFY, SCOPE, BEST_PATH.\n",
            encoding="utf-8",
        )
        (target / ".agents/skills/tes-engineering-discipline/SKILL.md").write_text(
            "## Mantra Gate\n\nUse the TES Mantra Gate for destructive, remote, release, sync, "
            "secret-bearing, or high-impact state changes. Ordinary local edits do not block "
            "on gate artifacts, markers, or skill loading.\n",
            encoding="utf-8",
        )
        degraded_surface = evaluate(target)
        if degraded_surface["status"] != "DEGRADED":
            failures.append("bootloader duplicated Mantra Gate protocol must degrade surface health")

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-") as tmp:
        target = Path(tmp)
        subprocess.run(["git", "init"], cwd=target, capture_output=True, text=True, check=False)
        subprocess.run(["git", "config", "user.email", "tes@example.invalid"], cwd=target, check=False)
        subprocess.run(["git", "config", "user.name", "TES"], cwd=target, check=False)
        (target / "package.json").write_text('{"name":"fixture"}\n', encoding="utf-8")
        subprocess.run(["git", "add", "package.json"], cwd=target, check=False)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=target, capture_output=True, text=True, check=False)
        (target / "package.json").write_text('{"name":"fixture","version":"0.0.1"}\n', encoding="utf-8")
        (target / ".tes/field-reports").mkdir(parents=True)
        write_record(
            target,
            mantra_gate.sample_gate(RISK="high-risk"),
            visible="compact",
            action="generated runtime packaging historical record",
        )
        doctor_health = evaluate(target)
        if doctor_health["status"] == "NEEDS_REVIEW" or doctor_health["state_changing"]:
            failures.append("read-only doctor health must not need review for dirty tree plus completed compact gate record")

        audit = evaluate(target, audit_history=True)
        if audit["status"] != "OK":
            failures.append("audit-history must pass when compact display has a complete gate record")

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-dirty-") as tmp:
        target = Path(tmp)
        subprocess.run(["git", "init"], cwd=target, capture_output=True, text=True, check=False)
        subprocess.run(["git", "config", "user.email", "tes@example.invalid"], cwd=target, check=False)
        subprocess.run(["git", "config", "user.name", "TES"], cwd=target, check=False)
        (target / ".gitignore").write_text(".tes/local-only.txt\n", encoding="utf-8")
        (target / "tracked.txt").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "add", ".gitignore", "tracked.txt"], cwd=target, check=False)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=target, capture_output=True, text=True, check=False)
        (target / ".tes").mkdir()
        (target / ".tes/local-only.txt").write_text("ignored\n", encoding="utf-8")
        ignored = evaluate(target)
        if ignored["dirty_worktree_present"] or ignored["git"]["status_short"]:
            failures.append("ignored local files must not create dirty-worktree closure noise")
        (target / "tracked.txt").write_text("changed\n", encoding="utf-8")
        tracked = evaluate(target)
        if not tracked["dirty_worktree_present"] or tracked["git"]["diff_files"] != ["tracked.txt"]:
            failures.append("tracked file changes must remain visible in dirty-worktree reporting")

    with tempfile.TemporaryDirectory(prefix="tes-mg-adoption-invalid-record-") as tmp:
        target = Path(tmp)
        (target / "AGENTS.md").write_text("route to the TES Mantra Gate\n", encoding="utf-8")
        ledger = target / ".tes/field-reports/mantra-gates.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        invalid = {"gate": {"VERIFY": "x", "SCOPE": "s", "BEST_PATH": "d", "DOCUMENT": "n",
                            "RESOLVE": "done", "STATUS": "PASS"}, "visible": "full"}
        ledger.write_text(json.dumps(invalid) + "\n", encoding="utf-8")
        report = evaluate(target)
        # A schema-invalid historical record must (a) surface a finding naming it
        # so installed certification can show the cause, and (b) still cap status
        # at NEEDS_REVIEW — never BLOCKED (the shipped D-fix invariant).
        invalid_findings = [f for f in report.get("findings", []) if f.get("type") == "invalid_historical_record"]
        if not invalid_findings:
            failures.append("invalid historical record must produce an invalid_historical_record finding")
        elif invalid_findings[0].get("failures") != ["invalid STATUS: PASS"]:
            failures.append("invalid_historical_record finding must carry the record's validation failures")
        if report.get("status") == "BLOCKED":
            failures.append("invalid historical record must cap status at NEEDS_REVIEW, not BLOCKED (D-fix invariant)")

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
    parser.add_argument("--audit-history", action="store_true")
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
        audit_history=args.audit_history,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] in {"OK", "DEGRADED"} else 1


if __name__ == "__main__":
    sys.exit(main())
