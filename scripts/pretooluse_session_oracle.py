#!/usr/bin/env python3
"""Parity oracle for PreToolUse session marker repetition.

The decision kernel proves allow/supervise/block classification. This oracle
proves the sibling session coordinator preserves the installed host behavior:
every governed context surfaces the Mantra Gate marker, repeated same-session
context is tracked in the ledger, and forbidden blocks always keep the marker.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import mantra_gate  # noqa: E402
import tes_install  # noqa: E402
import pretooluse_session  # noqa: E402


def _invoke(agent: str, target: Path, payload: dict[str, Any]) -> tuple[int, str, str]:
    args = argparse.Namespace(agent=agent, target=target)
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = tes_install.hook_pretooluse(args, payload)
    return code, stdout.getvalue(), stderr.getvalue()


def _governed_payload(agent: str) -> dict[str, Any]:
    return {
        "hook_event_name": "PreToolUse",
        "session_id": f"session-oracle-{agent}-governed",
        "tool_name": "Edit",
        "tool_input": {"file_path": f"docs/governance/session/{agent}/SKILL.md"},
    }


def _forbidden_payload(agent: str) -> dict[str, Any]:
    command = " ".join(("git", "push", "--force", "origin", "main"))
    return {
        "hook_event_name": "PreToolUse",
        "session_id": f"session-oracle-{agent}-forbidden",
        "tool_name": "Shell",
        "tool_input": {"command": command},
    }


def _records(target: Path) -> list[dict[str, Any]]:
    ledger = target / ".tes" / "runtime" / "hooks" / "executed.jsonl"
    if not ledger.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def _assert(condition: bool, failures: list[str], message: str) -> None:
    if not condition:
        failures.append(message)


def _reason_codes(row: dict[str, Any]) -> list[str]:
    value = row.get("reason_codes")
    return [str(item) for item in value] if isinstance(value, list) else []


def _contains_marker(*parts: str) -> bool:
    return mantra_gate.MARKER in "".join(parts)


def evaluate() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-pretooluse-session-") as tmp:
        target = Path(tmp)
        for agent in ("claude", "codex", "cursor"):
            governed = _governed_payload(agent)
            first_code, first_out, first_err = _invoke(agent, target, governed)
            second_code, second_out, second_err = _invoke(agent, target, governed)
            _assert(first_code == 0, failures, f"{agent}: first governed call must allow")
            _assert(second_code == 0, failures, f"{agent}: second governed call must allow")
            _assert(_contains_marker(first_out, first_err), failures, f"{agent}: first governed call must surface marker")
            _assert(
                _contains_marker(second_out, second_err),
                failures,
                f"{agent}: second governed call must surface marker",
            )

            forbidden = _forbidden_payload(agent)
            first_forbidden = {**forbidden, "tool_use_id": f"session-oracle-{agent}-forbidden-1"}
            second_forbidden = {**forbidden, "tool_use_id": f"session-oracle-{agent}-forbidden-2"}
            block_one = _invoke(agent, target, first_forbidden)
            block_two = _invoke(agent, target, second_forbidden)
            expected_code = 0 if agent == "cursor" else 2
            for index, (code, out, err) in enumerate((block_one, block_two), start=1):
                _assert(code == expected_code, failures, f"{agent}: forbidden block #{index} exit code")
                _assert(_contains_marker(out, err), failures, f"{agent}: forbidden block #{index} must keep marker")
                if agent == "cursor":
                    _assert('"permission": "deny"' in out, failures, f"{agent}: forbidden block #{index} must deny in JSON")

            rows = _records(target)
            session = governed["session_id"]
            governed_rows = [row for row in rows if row.get("agent") == agent and row.get("session") == session]
            _assert(len(governed_rows) == 2, failures, f"{agent}: governed session must write two ledger rows")
            if len(governed_rows) == 2:
                _assert(governed_rows[0].get("marker_emitted") is True, failures, f"{agent}: first ledger marker")
                _assert(governed_rows[1].get("marker_emitted") is True, failures, f"{agent}: second ledger marker")
                _assert(governed_rows[1].get("context_repeated") is True, failures, f"{agent}: second ledger repeated state")
                _assert("context_suppressed" not in governed_rows[1], failures, f"{agent}: current ledger must not write context_suppressed")
                _assert(
                    "governed_surface_mutation" in _reason_codes(governed_rows[0]),
                    failures,
                    f"{agent}: first governed row must persist governed_surface_mutation reason code",
                )
                _assert(
                    "anti_crywolf_repeated_context" in _reason_codes(governed_rows[1]),
                    failures,
                    f"{agent}: repeated governed row must persist anti_crywolf_repeated_context reason code",
                )

            forbidden_session = forbidden["session_id"]
            forbidden_rows = [row for row in rows if row.get("agent") == agent and row.get("session") == forbidden_session]
            _assert(len(forbidden_rows) == 2, failures, f"{agent}: forbidden session must write two ledger rows")
            for index, row in enumerate(forbidden_rows, start=1):
                _assert(row.get("block") is True, failures, f"{agent}: forbidden row #{index} must block")
                _assert(row.get("marker_emitted") is True, failures, f"{agent}: forbidden row #{index} marker")
                _assert(
                    "forbidden_class" in _reason_codes(row),
                    failures,
                    f"{agent}: forbidden row #{index} must persist forbidden_class reason code",
                )

        corrupt_target = target / "corrupt-sentinel"
        corrupt_path = pretooluse_session.pretooluse_sentinel_path(corrupt_target, {"session_id": "corrupt"})
        corrupt_path.parent.mkdir(parents=True, exist_ok=True)
        corrupt_path.write_bytes(b"\xff\xfe")
        corrupt_context = pretooluse_session.coordinate_pretooluse_context(corrupt_target, {"session_id": "corrupt"}, "ctx")
        _assert(corrupt_context.context == "ctx", failures, "corrupt sentinel must fail open with context")
        _assert(
            "anti_crywolf_sentinel_unavailable" in tuple(corrupt_context.reason_codes),
            failures,
            "corrupt sentinel must record unavailable reason code",
        )

    return {
        "oracle": "pretooluse-session",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def main() -> int:
    result = evaluate()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[pretooluse-session] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
