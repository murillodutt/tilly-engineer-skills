#!/usr/bin/env python3
"""Certify TES agent-hook audit findings one by one.

This local harness sits above the aggregate agent hook certification matrix. It
does not define product behavior; it maps each retained audit finding to the
source, installed-target, host-real, and focused-oracle evidence needed before
the finding can be called certified or refuted.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import agent_hooks_certification_matrix as aggregate


SCHEMA = "tes-agent-hook-finding-matrix@1"
SKILL_CONTRACT = "tes.host_transcript_canary@0.1.8"
MANIFEST_SCHEMA = "tes-agent-hook-findings@1"
DEFAULT_MANIFEST = Path(__file__).resolve().parents[1] / "references" / "agent-hook-findings.json"

SOURCE_CERTIFIED = "SOURCE_CERTIFIED"
TARGET_CERTIFIED = "TARGET_CERTIFIED"
HOST_CERTIFIED = "HOST_CERTIFIED"
HOST_NOT_APPLICABLE = "HOST_NOT_APPLICABLE"
REFUTED = "REFUTED"
NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
FAIL = "FAIL"
BLOCKED = "BLOCKED"

VALID_MINIMUM_LANES = {"source", "target", "host"}
VALID_HOST_APPLICABILITY = {"required", "not_applicable"}
VALID_DISPOSITIONS = {"active", "refuted"}

KNOWN_TARGET_ROWS = {
    "target-config-codex",
    "target-config-claude",
    "target-config-cursor",
    "target-helper-cortex_runtime.py",
    "target-helper-pretooluse_kernel.py",
    "target-helper-pretooluse_session.py",
    "target-hook-health-schema",
    "target-helper-contract",
    "target-floor-ceiling-visible",
    "target-runtime-ledger",
}
KNOWN_HOST_ROWS = {
    "host-transcript-evidence",
    "host-loop-pass",
    "host-loop-oracle",
    "host-transcript-oracle",
    "host-runtime-session-correlated",
    "host-runtime-governed-supervision",
    "host-runtime-shell-redaction",
}

GATE_COMMANDS: dict[str, tuple[str, ...]] = {
    "tes-install-self-test": (sys.executable, "scripts/tes_install.py", "--self-test"),
    "tes-update-self-test": (sys.executable, "scripts/tes_update.py", "--self-test"),
    "install-smoke-audit": (sys.executable, "scripts/install_smoke.py", "--route", "audit"),
    "pretooluse-kernel": (sys.executable, "scripts/pretooluse_kernel_oracle.py"),
    "pretooluse-session": (sys.executable, "scripts/pretooluse_session_oracle.py"),
    "pretooluse-contract": (sys.executable, "scripts/pretooluse_contract_oracle.py", "--self-test"),
    "hook-audit-prompt": (sys.executable, "scripts/hook_audit_prompt_oracle.py", "--self-test"),
    "host-runtime-matrix": (sys.executable, "scripts/host_runtime_matrix_oracle.py"),
    "canary-admission-self-test": (sys.executable, "scripts/canary_admission_oracle.py", "--self-test"),
    "installed-certification-self-test": (
        sys.executable,
        "scripts/installed_certification_oracle.py",
        "--self-test",
    ),
}


def parse_json_prefix(stdout: str) -> dict[str, Any] | None:
    """Parse the first JSON object from command stdout, tolerating trailing text."""

    text = stdout.lstrip()
    if not text:
        return None
    decoder = json.JSONDecoder()
    try:
        payload, _ = decoder.raw_decode(text)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def run_process(argv: tuple[str, ...], cwd: Path, timeout: int) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            list(argv),
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "argv": list(argv),
            "returncode": None,
            "timed_out": True,
            "stdout_bytes": len((exc.stdout or "").encode("utf-8")) if isinstance(exc.stdout, str) else 0,
            "stderr_bytes": len((exc.stderr or "").encode("utf-8")) if isinstance(exc.stderr, str) else 0,
            "status": BLOCKED,
            "json": None,
        }

    payload = parse_json_prefix(completed.stdout)
    status = payload.get("status") if isinstance(payload, dict) else None
    return {
        "argv": list(argv),
        "returncode": completed.returncode,
        "timed_out": False,
        "stdout_bytes": len(completed.stdout.encode("utf-8")),
        "stderr_bytes": len(completed.stderr.encode("utf-8")),
        "status": status,
        "json": payload,
    }


def gate_passed(result: dict[str, Any] | None) -> bool:
    if not result:
        return False
    if result.get("timed_out") is True:
        return False
    if result.get("returncode") != 0:
        return False
    status = result.get("status")
    return status in (None, "PASS", "OK", "SOURCE_CERTIFIED", "TARGET_CERTIFIED", "HOST_CERTIFIED")


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"manifest is not readable JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"manifest root must be an object: {path}")
    if payload.get("schema") != MANIFEST_SCHEMA:
        raise SystemExit(f"manifest schema mismatch: expected {MANIFEST_SCHEMA}, got {payload.get('schema')!r}")
    findings = payload.get("findings")
    if not isinstance(findings, list) or not findings:
        raise SystemExit("manifest must contain a non-empty findings list")
    return payload


def source_row_ids() -> set[str]:
    return {check.row_id for check in aggregate.SOURCE_CHECKS}


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    seen: set[str] = set()
    known_source = source_row_ids()
    for item in manifest.get("findings", []):
        if not isinstance(item, dict):
            failures.append("finding entry is not an object")
            continue
        finding_id = str(item.get("id") or "")
        if not finding_id:
            failures.append("finding entry missing id")
        elif finding_id in seen:
            failures.append(f"duplicate finding id: {finding_id}")
        seen.add(finding_id)
        if item.get("minimum_lane") not in VALID_MINIMUM_LANES:
            failures.append(f"{finding_id}: invalid minimum_lane")
        if item.get("host_applicability") not in VALID_HOST_APPLICABILITY:
            failures.append(f"{finding_id}: invalid host_applicability")
        if item.get("disposition") not in VALID_DISPOSITIONS:
            failures.append(f"{finding_id}: invalid disposition")
        for row_id in item.get("source_rows", []):
            if row_id not in known_source:
                failures.append(f"{finding_id}: unknown source row {row_id}")
        for row_id in item.get("target_rows", []):
            if row_id not in KNOWN_TARGET_ROWS:
                failures.append(f"{finding_id}: unknown target row {row_id}")
        for row_id in item.get("host_rows", []):
            if row_id not in KNOWN_HOST_ROWS:
                failures.append(f"{finding_id}: unknown host row {row_id}")
        for gate in item.get("gates", []):
            if gate not in GATE_COMMANDS:
                failures.append(f"{finding_id}: unknown gate {gate}")
    if not any(item.get("host_applicability") == "required" for item in manifest.get("findings", [])):
        failures.append("manifest must include at least one host-required finding")
    if not any(item.get("disposition") == "refuted" for item in manifest.get("findings", [])):
        failures.append("manifest must include at least one refuted finding")
    return failures


def build_aggregate(args: argparse.Namespace) -> dict[str, Any]:
    matrix_args = argparse.Namespace(
        repo=args.repo,
        target=args.target,
        current_host=args.current_host,
        host_loop_json=args.host_loop_json,
        transcript_oracle_json=args.transcript_oracle_json,
        run_related_gates=args.run_related_gates,
        require_target=args.require_target,
        require_host_transcript=args.require_host_transcript,
    )
    return aggregate.build_matrix(matrix_args)


def row_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("id")): row for row in rows if row.get("id")}


def row_status(rows_by_id: dict[str, dict[str, Any]], row_id: str) -> str:
    row = rows_by_id.get(row_id)
    if row is None:
        return "NOT_RUN"
    return str(row.get("status") or FAIL)


def run_finding_gates(manifest: dict[str, Any], repo: Path, *, run: bool, timeout: int) -> dict[str, Any]:
    required = sorted(
        {
            gate
            for item in manifest.get("findings", [])
            for gate in item.get("gates", [])
            if gate in GATE_COMMANDS
        }
    )
    if not run:
        return {"status": "NOT_RUN", "gates": {gate: {"status": "NOT_RUN"} for gate in required}}

    gates: dict[str, Any] = {}
    for gate in required:
        gates[gate] = run_process(GATE_COMMANDS[gate], repo, timeout)
    failed = [name for name, result in gates.items() if not gate_passed(result)]
    return {
        "status": "PASS" if not failed else FAIL,
        "gates": gates,
        "failed": failed,
    }


def classify_finding(
    item: dict[str, Any],
    rows_by_id: dict[str, dict[str, Any]],
    gates: dict[str, Any],
) -> dict[str, Any]:
    finding_id = str(item["id"])
    if item.get("disposition") == "refuted":
        return {
            "id": finding_id,
            "severity": item.get("severity"),
            "title": item.get("title"),
            "status": REFUTED,
            "host_status": HOST_NOT_APPLICABLE,
            "minimum_lane": item.get("minimum_lane"),
            "host_applicability": item.get("host_applicability"),
            "blockers": [],
            "evidence": {"source_rows": {}, "target_rows": {}, "host_rows": {}, "gates": {}},
        }

    source_rows = {row_id: row_status(rows_by_id, row_id) for row_id in item.get("source_rows", [])}
    target_rows = {row_id: row_status(rows_by_id, row_id) for row_id in item.get("target_rows", [])}
    host_rows = {row_id: row_status(rows_by_id, row_id) for row_id in item.get("host_rows", [])}
    gate_rows = {
        gate: ("PASS" if gate_passed(gates.get(gate)) else str((gates.get(gate) or {}).get("status") or "NOT_RUN"))
        for gate in item.get("gates", [])
    }

    blockers: list[str] = []
    for lane_name, lane_rows in (("source", source_rows), ("target", target_rows), ("host", host_rows)):
        for row_id, status in lane_rows.items():
            if status != "PASS":
                blockers.append(f"{lane_name}:{row_id}:{status}")
    for gate, status in gate_rows.items():
        if status != "PASS":
            blockers.append(f"gate:{gate}:{status}")

    if any(blocker.endswith(f":{FAIL}") for blocker in blockers):
        status = FAIL
    elif blockers:
        status = NEEDS_EVIDENCE
    elif item.get("minimum_lane") == "host":
        status = HOST_CERTIFIED
    elif item.get("minimum_lane") == "target":
        status = TARGET_CERTIFIED
    else:
        status = SOURCE_CERTIFIED

    host_status = HOST_NOT_APPLICABLE
    if item.get("host_applicability") == "required":
        host_status = HOST_CERTIFIED if status == HOST_CERTIFIED else NEEDS_EVIDENCE

    return {
        "id": finding_id,
        "severity": item.get("severity"),
        "title": item.get("title"),
        "status": status,
        "host_status": host_status,
        "minimum_lane": item.get("minimum_lane"),
        "host_applicability": item.get("host_applicability"),
        "blockers": blockers,
        "evidence": {
            "source_rows": source_rows,
            "target_rows": target_rows,
            "host_rows": host_rows,
            "gates": gate_rows,
        },
    }


def summarize(findings: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for item in findings:
        status = str(item.get("status") or FAIL)
        counts[status] = counts.get(status, 0) + 1
    blockers = [item["id"] for item in findings if item.get("status") in {FAIL, NEEDS_EVIDENCE, BLOCKED}]
    host_required = [item["id"] for item in findings if item.get("host_applicability") == "required"]
    host_certified = [item["id"] for item in findings if item.get("status") == HOST_CERTIFIED]
    if any(item.get("status") == FAIL for item in findings):
        status = FAIL
    elif any(item.get("status") == BLOCKED for item in findings):
        status = BLOCKED
    elif any(item.get("status") == NEEDS_EVIDENCE for item in findings):
        status = NEEDS_EVIDENCE
    else:
        status = "PASS"
    return {
        "status": status,
        "counts": counts,
        "blockers": blockers,
        "host_required": host_required,
        "host_certified": host_certified,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo.expanduser().resolve()
    manifest = load_manifest(args.manifest.expanduser().resolve())
    manifest_failures = validate_manifest(manifest)
    aggregate_matrix = build_aggregate(args)
    rows_by_id = row_map(aggregate_matrix.get("rows", []))
    finding_gates = run_finding_gates(manifest, repo, run=args.run_finding_gates, timeout=args.timeout)
    gates = finding_gates.get("gates", {}) if isinstance(finding_gates.get("gates"), dict) else {}
    findings = [classify_finding(item, rows_by_id, gates) for item in manifest.get("findings", [])]
    summary = summarize(findings)
    status = FAIL if manifest_failures else summary["status"]
    return {
        "schema": SCHEMA,
        "skill_contract": SKILL_CONTRACT,
        "status": status,
        "repo": str(repo),
        "target": str(args.target.expanduser().resolve()) if args.target else None,
        "current_host": args.current_host,
        "manifest": {
            "path": str(args.manifest.expanduser().resolve()),
            "schema": manifest.get("schema"),
            "finding_count": len(manifest.get("findings", [])),
            "validation_failures": manifest_failures,
        },
        "aggregate_matrix": {
            "status": aggregate_matrix.get("status"),
            "decision": aggregate_matrix.get("decision"),
            "summary": aggregate_matrix.get("summary"),
        },
        "finding_gates": finding_gates,
        "summary": summary,
        "findings": findings,
    }


def self_test(repo: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    failures = validate_manifest(manifest)
    args = argparse.Namespace(
        repo=repo,
        target=None,
        current_host=None,
        host_loop_json=None,
        transcript_oracle_json=None,
        run_related_gates=False,
        require_target=False,
        require_host_transcript=False,
        manifest=manifest_path,
        run_finding_gates=False,
        timeout=30,
    )
    report = build_report(args)
    by_id = {item["id"]: item for item in report.get("findings", [])}
    if by_id.get("H-03", {}).get("status") != NEEDS_EVIDENCE:
        failures.append("H-03 must need evidence without host replay")
    if by_id.get("LEDGER-02", {}).get("status") != REFUTED:
        failures.append("LEDGER-02 must remain REFUTED")
    if report.get("manifest", {}).get("finding_count", 0) < 20:
        failures.append("finding manifest should cover the retained audit set")
    return {
        "schema": SCHEMA,
        "skill_contract": SKILL_CONTRACT,
        "status": "PASS" if not failures else FAIL,
        "manifest_findings": report.get("manifest", {}).get("finding_count"),
        "coverage": [
            "finding manifest validation",
            "aggregate matrix row binding",
            "focused gate binding",
            "host-required downgrade without transcript",
            "refuted finding state",
        ],
        "failures": failures,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a TES agent-hook finding certification matrix.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--target", type=Path)
    parser.add_argument("--current-host", choices=("codex", "claude", "cursor"))
    parser.add_argument("--host-loop-json", type=Path)
    parser.add_argument("--transcript-oracle-json", type=Path)
    parser.add_argument("--run-related-gates", action="store_true")
    parser.add_argument("--require-target", action="store_true")
    parser.add_argument("--require-host-transcript", action="store_true")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--run-finding-gates", action="store_true")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--json-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo = args.repo.expanduser().resolve()
    if args.self_test:
        result = self_test(repo, args.manifest.expanduser().resolve())
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "PASS" else 1

    result = build_report(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json_only:
        print(f"[agent-hook-finding-matrix] {result['status']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
