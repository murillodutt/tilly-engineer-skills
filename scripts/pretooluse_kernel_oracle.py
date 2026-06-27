#!/usr/bin/env python3
"""Self-test for the host-neutral PreToolUse decision kernel.

The host matrix proves rendered behavior through `tes_install.py`; this oracle
guards the internal boundary: the kernel may classify allow/supervise/block and
extract paths, but it must not learn Claude, Codex, or Cursor output protocols.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import mantra_gate  # noqa: E402
import pretooluse_kernel  # noqa: E402


HOST_PROTOCOL_TOKENS = (
    "hookSpecificOutput",
    "permissionDecision",
    "agent_message",
    "user_message",
    "\"permission\"",
    "exit 2",
    "stderr",
)


def _classify(action: str, paths: list[str]) -> str:
    return str(mantra_gate.classify_risk(action=action, paths=paths).get("risk", "routine"))


def _decision(payload: dict[str, Any]) -> dict[str, Any]:
    return pretooluse_kernel.decide_pretooluse(
        payload,
        risk_classifier=_classify,
        marker=mantra_gate.MARKER,
    )


def _patch(path: str) -> str:
    return "\n".join(
        (
            "*** Begin Patch",
            f"*** Add File: {path}",
            "+# Smoke",
            "*** End Patch",
        )
    )


def _assert(condition: bool, failures: list[str], message: str) -> None:
    if not condition:
        failures.append(message)


def evaluate() -> dict[str, Any]:
    failures: list[str] = []

    routine = _decision(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Read",
            "tool_input": {"file_path": "src/app.py"},
        }
    )
    _assert(routine.get("outcome") == "allow", failures, "routine Read must allow")
    _assert(routine.get("context") == "", failures, "routine Read must stay silent")

    governed = _decision(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Edit",
            "tool_input": {"file_path": "docs/governance/policy/SKILL.md"},
        }
    )
    _assert(governed.get("outcome") == "supervise", failures, "governed Edit must supervise")
    _assert("docs/governance/policy/SKILL.md" in str(governed.get("context")), failures, "governed context must name path")
    _assert(mantra_gate.MARKER in str(governed.get("context")), failures, "governed context must include marker")

    cursor_replace = _decision(
        {
            "hook_event_name": "preToolUse",
            "tool_name": "StrReplace",
            "tool_input": {"file_path": ".tes/runtime/hook-smoke/cursor/SKILL.md"},
        }
    )
    _assert(
        cursor_replace.get("outcome") == "supervise",
        failures,
        "Cursor StrReplace on governed paths must supervise",
    )
    _assert(
        ".tes/runtime/hook-smoke/cursor/SKILL.md" in str(cursor_replace.get("context")),
        failures,
        "Cursor StrReplace context must name governed path",
    )

    forbidden = _decision(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "git push --force origin main"},
        }
    )
    _assert(forbidden.get("outcome") == "block", failures, "forbidden Bash must block")
    _assert(forbidden.get("block") is True, failures, "forbidden Bash must set block=true")
    _assert(mantra_gate.MARKER in str(forbidden.get("reason")), failures, "forbidden reason must include marker")

    alias_payloads = {
        "command": {"tool_input": {"command": _patch(".tes/runtime/hook-smoke/codex/command/SKILL.md")}},
        "input": {"tool_input": {"input": _patch(".tes/runtime/hook-smoke/codex/input/SKILL.md")}},
        "patch": {"tool_input": {"patch": _patch(".tes/runtime/hook-smoke/codex/patch/SKILL.md")}},
        "arguments.command": {
            "tool_input": {"arguments": {"command": _patch(".tes/runtime/hook-smoke/codex/arguments-command/SKILL.md")}}
        },
        "arguments.input": {
            "tool_input": {"arguments": {"input": _patch(".tes/runtime/hook-smoke/codex/arguments-input/SKILL.md")}}
        },
        "arguments.patch": {
            "tool_input": {"arguments": {"patch": _patch(".tes/runtime/hook-smoke/codex/arguments-patch/SKILL.md")}}
        },
        "top-level-input": {"input": _patch(".tes/runtime/hook-smoke/codex/top-level-input/SKILL.md")},
    }
    for name, payload in alias_payloads.items():
        hook_input = {"hookEventName": "PreToolUse", "toolName": "apply_patch", **payload}
        tool_input = pretooluse_kernel.hook_tool_input(hook_input)
        path = pretooluse_kernel.hook_tool_path(hook_input, tool_input)
        _assert(path.endswith("/SKILL.md"), failures, f"{name}: patch path must be extracted")
        decision = _decision(hook_input)
        _assert(decision.get("outcome") == "supervise", failures, f"{name}: apply_patch must supervise")
        _assert(path in str(decision.get("context")), failures, f"{name}: context must name extracted path")

    source_text = (ROOT / "scripts" / "pretooluse_kernel.py").read_text(encoding="utf-8")
    for token in HOST_PROTOCOL_TOKENS:
        _assert(token not in source_text, failures, f"kernel must not contain host protocol token {token!r}")

    return {
        "oracle": "pretooluse-kernel",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def main() -> int:
    result = evaluate()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[pretooluse-kernel] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
