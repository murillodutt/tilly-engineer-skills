#!/usr/bin/env python3
"""Scripted host transcript canary loop helper.

This helper wraps the source transcript oracle with a loop ledger that stores
only sanitized evidence: command fingerprints, transcript hashes, event counts,
return codes, output hashes, blockers, and the next required action.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA = "tes-host-canary-loop@1"
SKILL_CONTRACT = "tes.host_transcript_canary@0.1.2"
FAILURE_CLASSES = {
    "host_execution_gap",
    "transcript_gap",
    "oracle_gap",
    "product_gap",
    "evidence_gap",
    "false_green",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def find_repo_root(start: Path) -> Path:
    for candidate in (start.expanduser().resolve(), *start.expanduser().resolve().parents):
        if (candidate / "scripts" / "canary_transcript_oracle.py").is_file():
            return candidate
    raise SystemExit("cannot find scripts/canary_transcript_oracle.py; pass --repo")


def default_ledger_path(repo_root: Path) -> Path:
    return repo_root / ".tes" / "runs" / "host-canary-loop.jsonl"


def load_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            if not raw_line.strip():
                continue
            try:
                event = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict) and event.get("schema") == SCHEMA:
                records.append(event)
    return records


def latest_for_target(records: list[dict[str, Any]], target_fingerprint: str | None) -> dict[str, Any] | None:
    if not target_fingerprint:
        return records[-1] if records else None
    for record in reversed(records):
        if record.get("target_fingerprint") == target_fingerprint:
            return record
    return None


def latest_for_command(records: list[dict[str, Any]], command_fingerprint: str | None) -> dict[str, Any] | None:
    if not command_fingerprint:
        return None
    for record in reversed(records):
        if record.get("command_fingerprint") == command_fingerprint:
            return record
    return None


def run_host_command(*, command: str | None, execute: bool, cwd: Path, timeout: int) -> dict[str, Any]:
    if not command:
        return {"requested": False, "ran": False}

    result: dict[str, Any] = {
        "requested": True,
        "ran": False,
        "cwd": str(cwd.expanduser().resolve()),
        "command_fingerprint": sha256_text(command),
    }
    if not execute:
        result["reason"] = "command fingerprint recorded; pass --execute to run it"
        return result

    started = utc_now()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=False,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, bytes) else (exc.stdout or "").encode("utf-8")
        stderr = exc.stderr if isinstance(exc.stderr, bytes) else (exc.stderr or "").encode("utf-8")
        result.update(
            {
                "ran": True,
                "started_at": started,
                "completed_at": utc_now(),
                "timed_out": True,
                "timeout_seconds": timeout,
                "returncode": None,
                "stdout_bytes": len(stdout),
                "stdout_sha256": sha256_bytes(stdout),
                "stderr_bytes": len(stderr),
                "stderr_sha256": sha256_bytes(stderr),
            }
        )
        return result

    stdout = completed.stdout or b""
    stderr = completed.stderr or b""
    result.update(
        {
            "ran": True,
            "started_at": started,
            "completed_at": utc_now(),
            "timed_out": False,
            "returncode": completed.returncode,
            "stdout_bytes": len(stdout),
            "stdout_sha256": sha256_bytes(stdout),
            "stderr_bytes": len(stderr),
            "stderr_sha256": sha256_bytes(stderr),
        }
    )
    return result


def run_transcript_oracle(args: argparse.Namespace, repo_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    oracle = repo_root / "scripts" / "canary_transcript_oracle.py"
    argv = [sys.executable, str(oracle), "--json-only"]
    if args.transcript:
        argv.extend(["--transcript", str(args.transcript)])
    if args.target:
        argv.extend(["--target", str(args.target)])
    if args.session_id:
        argv.extend(["--session-id", args.session_id])
    if args.projects_root:
        argv.extend(["--projects-root", str(args.projects_root)])
    if args.include_subagents:
        argv.append("--include-subagents")
    if args.require_tool_use:
        argv.append("--require-tool-use")

    completed = subprocess.run(argv, cwd=repo_root, check=False, capture_output=True, text=True)
    process = {
        "returncode": completed.returncode,
        "stdout_bytes": len(completed.stdout.encode("utf-8")),
        "stdout_sha256": sha256_text(completed.stdout),
        "stderr_bytes": len(completed.stderr.encode("utf-8")),
        "stderr_sha256": sha256_text(completed.stderr),
    }
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError:
        result = {
            "status": "FAIL",
            "blockers": ["transcript oracle did not emit parseable JSON"],
        }
    return result, process


def summarize_oracle(result: dict[str, Any], process: dict[str, Any]) -> dict[str, Any]:
    main = result.get("main") if isinstance(result.get("main"), dict) else {}
    subagents = result.get("subagents") if isinstance(result.get("subagents"), dict) else None
    summary: dict[str, Any] = {
        "process": process,
        "status": result.get("status", "NEEDS_EVIDENCE"),
        "resolution_mode": (result.get("resolution") or {}).get("mode") if isinstance(result.get("resolution"), dict) else None,
        "transcript_path": main.get("path"),
        "transcript_sha256": main.get("sha256"),
        "parsed_lines": main.get("parsed_lines"),
        "tool_use_count": main.get("tool_use_count", 0),
        "tool_result_count": main.get("tool_result_count", 0),
        "blockers": result.get("blockers", []),
    }
    if subagents is not None:
        summary["subagents"] = {
            "status": subagents.get("status"),
            "jsonl_count": subagents.get("jsonl_count", 0),
            "meta_count": subagents.get("meta_count", 0),
        }
    return summary


def decide(
    *,
    args: argparse.Namespace,
    host_execution: dict[str, Any],
    oracle: dict[str, Any],
    previous_target: dict[str, Any] | None,
    previous_command: dict[str, Any] | None,
    command_fingerprint: str | None,
) -> dict[str, Any]:
    blockers: list[str] = []
    failure_class = args.failure_class
    loop_status = str(oracle.get("status", "NEEDS_EVIDENCE"))
    next_action = "run_related_gates"

    if args.enforce_same_command and previous_target and not args.allow_command_change:
        previous_fingerprint = previous_target.get("command_fingerprint")
        if previous_fingerprint and command_fingerprint and previous_fingerprint != command_fingerprint:
            blockers.append("same-command replay required; command fingerprint changed")
            failure_class = failure_class or "evidence_gap"
            loop_status = "NEEDS_EVIDENCE"
            next_action = "replay_original_command"

    if host_execution.get("timed_out") or (
        host_execution.get("ran") and host_execution.get("returncode") not in (0, None)
    ):
        blockers.append("host command did not complete successfully")
        failure_class = failure_class or "host_execution_gap"
        loop_status = "FAIL"
        next_action = "fix_host_execution"

    stale_transcript = False
    transcript_hash = oracle.get("transcript_sha256")
    if args.require_fresh and transcript_hash and previous_command:
        stale_transcript = previous_command.get("oracle", {}).get("transcript_sha256") == transcript_hash
        if stale_transcript:
            blockers.append("same command resolved to a previously recorded transcript hash")
            failure_class = failure_class or "false_green"
            loop_status = "NEEDS_EVIDENCE"
            next_action = "rerun_host_command"

    if loop_status == "FAIL" and failure_class is None:
        failure_class = "transcript_gap"
        next_action = "classify_and_patch"
    elif loop_status == "NEEDS_EVIDENCE" and failure_class is None:
        failure_class = "transcript_gap"
        next_action = "rerun_host_command"
    elif loop_status == "PASS" and args.related_gates_passed:
        next_action = "certified"
    elif loop_status == "PASS":
        next_action = "run_related_gates"

    return {
        "loop_status": loop_status,
        "failure_class": failure_class,
        "next_action": next_action,
        "stale_transcript": stale_transcript,
        "blockers": [*oracle.get("blockers", []), *blockers],
    }


def write_ledger(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def run_loop(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    repo_root = args.repo.expanduser().resolve() if args.repo else find_repo_root(Path.cwd())
    ledger_path = args.ledger.expanduser().resolve() if args.ledger else default_ledger_path(repo_root)
    target_path = args.target.expanduser().resolve() if args.target else None
    command_fingerprint = sha256_text(args.command) if args.command else None
    target_fingerprint = sha256_text(str(target_path)) if target_path else None
    records = [] if args.no_ledger else load_ledger(ledger_path)
    previous_target = latest_for_target(records, target_fingerprint)
    previous_command = latest_for_command(records, command_fingerprint)
    command_cwd = args.command_cwd or target_path or Path.cwd()

    host_execution = run_host_command(
        command=args.command,
        execute=args.execute,
        cwd=command_cwd.expanduser().resolve(),
        timeout=args.timeout,
    )
    oracle_result, oracle_process = run_transcript_oracle(args, repo_root)
    oracle = summarize_oracle(oracle_result, oracle_process)
    decision = decide(
        args=args,
        host_execution=host_execution,
        oracle=oracle,
        previous_target=previous_target,
        previous_command=previous_command,
        command_fingerprint=command_fingerprint,
    )

    entry: dict[str, Any] = {
        "schema": SCHEMA,
        "skill_contract": SKILL_CONTRACT,
        "timestamp": utc_now(),
        "loop_id": sha256_text(f"{utc_now()}:{command_fingerprint}:{oracle.get('transcript_sha256')}")[:16],
        "repo": str(repo_root),
        "target": str(target_path) if target_path else None,
        "target_fingerprint": target_fingerprint,
        "command_fingerprint": command_fingerprint,
        "command_label": args.command_label,
        "host_execution": host_execution,
        "oracle": oracle,
        "fix_commit": args.fix_commit,
        "related_gates_passed": args.related_gates_passed,
        **decision,
    }

    if args.no_ledger:
        entry["ledger"] = {"written": False, "reason": "--no-ledger"}
    else:
        write_ledger(ledger_path, entry)
        entry["ledger"] = {"written": True, "path": str(ledger_path)}

    return (0 if entry["loop_status"] == "PASS" else 1), entry


def write_jsonl(path: Path, events: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(event, sort_keys=True) for event in events) + "\n", encoding="utf-8")


def self_test(repo_root: Path | None) -> dict[str, Any]:
    failures: list[str] = []
    secret = "SECRET_VALUE_SHOULD_NOT_LEAK"
    root = repo_root or find_repo_root(Path.cwd())
    with tempfile.TemporaryDirectory(prefix="tes-host-loop-") as tmp:
        temp = Path(tmp)
        target = temp / "target-project"
        projects_root = temp / ".claude" / "projects"
        slug = str(target.resolve()).replace("/", "-")
        transcript = projects_root / slug / "11111111-2222-3333-4444-555555555555.jsonl"
        ledger = temp / "host-loop.jsonl"
        write_jsonl(
            transcript,
            [
                {"type": "user", "sessionId": "s1", "message": {"role": "user", "content": secret}},
                {
                    "type": "assistant",
                    "sessionId": "s1",
                    "message": {
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": secret},
                            {"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {"cmd": secret}},
                        ],
                    },
                },
            ],
        )

        base = argparse.Namespace(
            repo=root,
            target=target,
            transcript=transcript,
            session_id=None,
            projects_root=projects_root,
            include_subagents=False,
            require_tool_use=True,
            command="claude --print /tes-map",
            command_label="self-test-host-command",
            execute=False,
            command_cwd=target,
            timeout=60,
            ledger=ledger,
            no_ledger=False,
            require_fresh=True,
            enforce_same_command=True,
            allow_command_change=False,
            failure_class=None,
            fix_commit=None,
            related_gates_passed=False,
        )
        code1, result1 = run_loop(base)
        code2, result2 = run_loop(base)
        serialized = json.dumps([result1, result2], sort_keys=True)
        if code1 != 0 or result1.get("loop_status") != "PASS":
            failures.append("first loop should pass with a valid transcript")
        if code2 == 0 or result2.get("failure_class") != "false_green":
            failures.append("second loop should reject a stale same-command transcript")
        if secret in serialized:
            failures.append("loop output leaked raw transcript or command output content")
        if len(ledger.read_text(encoding="utf-8").splitlines()) != 2:
            failures.append("ledger should contain one JSONL record per loop")

    return {
        "schema": SCHEMA,
        "skill_contract": SKILL_CONTRACT,
        "status": "PASS" if not failures else "FAIL",
        "coverage": [
            "sanitized ledger",
            "same-command fingerprint",
            "fresh transcript enforcement",
            "oracle wrapper",
        ],
        "failures": failures,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one sanitized host transcript canary loop step.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo", type=Path, help="TES package root containing scripts/canary_transcript_oracle.py.")
    parser.add_argument("--target", type=Path, help="Target project whose Claude transcript should be audited.")
    parser.add_argument("--transcript", type=Path, help="Explicit Claude Code JSONL transcript.")
    parser.add_argument("--session-id", help="Claude Code session id under the target slug.")
    parser.add_argument("--projects-root", type=Path, default=Path.home() / ".claude" / "projects")
    parser.add_argument("--include-subagents", action="store_true")
    parser.add_argument("--require-tool-use", action="store_true")
    parser.add_argument("--command", help="Host command to fingerprint and optionally execute. Raw command is not written.")
    parser.add_argument("--command-label", help="Optional sanitized label for the host command.")
    parser.add_argument("--execute", action="store_true", help="Actually run --command with captured output hashes only.")
    parser.add_argument("--command-cwd", type=Path, help="Working directory for --command. Defaults to --target or cwd.")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--ledger", type=Path, help="JSONL ledger path. Defaults to .tes/runs/host-canary-loop.jsonl.")
    parser.add_argument("--no-ledger", action="store_true")
    parser.add_argument("--require-fresh", action="store_true", help="Reject same-command replay with the same transcript hash.")
    parser.add_argument("--enforce-same-command", action="store_true", help="Reject command changes for the target unless allowed.")
    parser.add_argument("--allow-command-change", action="store_true")
    parser.add_argument("--failure-class", choices=sorted(FAILURE_CLASSES))
    parser.add_argument("--fix-commit", help="Optional local source commit hash that produced this replay.")
    parser.add_argument("--related-gates-passed", action="store_true")
    parser.add_argument("--json-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.execute and not args.command:
        parser.error("--execute requires --command")

    if args.self_test:
        result = self_test(args.repo.expanduser().resolve() if args.repo else None)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "PASS" else 1

    code, result = run_loop(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json_only:
        print(
            "[host-canary-loop] "
            f"{result['loop_status']} next_action={result['next_action']} "
            f"failure_class={result.get('failure_class') or 'none'}"
        )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
