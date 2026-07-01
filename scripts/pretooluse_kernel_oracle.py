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


def _trace(decision: dict[str, Any]) -> dict[str, Any]:
    value = decision.get("classifier_trace")
    return value if isinstance(value, dict) else {}


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
    _assert(
        "routine_non_mutating" in routine.get("reason_codes", []),
        failures,
        "routine Read must carry routine_non_mutating reason code",
    )
    _assert(routine.get("raw_tool_label") == "Read", failures, "routine Read must preserve raw_tool_label")
    _assert(routine.get("normalized_tool") == "Read", failures, "routine Read must persist normalized_tool")
    _assert(routine.get("payload_source") == "tool_input.file_path", failures, "routine Read must persist payload_source")
    _assert(_trace(routine).get("path_source") == "tool_input.file_path", failures, "routine trace must name path source")

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
    _assert(
        "governed_surface_mutation" in governed.get("reason_codes", []),
        failures,
        "governed Edit must carry governed_surface_mutation reason code",
    )
    _assert(
        _trace(governed).get("path_match") == "governed_surface",
        failures,
        "governed trace must name governed path match",
    )

    bare_skill = _decision(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Edit",
            "tool_input": {"file_path": "SKILL.md"},
        }
    )
    _assert(bare_skill.get("outcome") == "supervise", failures, "bare SKILL.md Edit must supervise")
    _assert(
        pretooluse_kernel.is_governed_path("MYSKILL.md") is False
        and pretooluse_kernel.is_governed_path("SKILLS.md") is False
        and pretooluse_kernel.is_governed_path("./SKILL.md") is True
        and pretooluse_kernel.is_governed_path("/tmp/target/docs/x/SKILL.md") is True,
        failures,
        "SKILL.md governed matching must be segment-exact",
    )

    shell_cases = [
        ("append-root", {"command": "echo x >> CLAUDE.md"}, "root_agent_bootloader"),
        ("sed-root", {"command": "sed -i s/a/b/ AGENTS.md"}, "root_agent_bootloader"),
        ("redirect-cursor", {"command": "cat payload > .cursor/rules/x.mdc"}, "cursor_rule"),
        ("tee-governance", {"command": "printf x | tee -a docs/governance/policy.md"}, "governance"),
    ]
    for name, tool_input, expected_class in shell_cases:
        shell_decision = _decision(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": tool_input,
            }
        )
        _assert(shell_decision.get("outcome") == "supervise", failures, f"{name}: shell governed mutation must supervise")
        _assert(shell_decision.get("risk") == "material", failures, f"{name}: shell routine risk must escalate")
        _assert(
            "shell_command_path_extracted" in shell_decision.get("reason_codes", []),
            failures,
            f"{name}: shell extraction must be traceable",
        )
        _assert(
            _trace(shell_decision).get("governed_surface_class") == expected_class,
            failures,
            f"{name}: trace must classify governed surface",
        )
        _assert(
            str(tool_input["command"]) not in str(shell_decision.get("context")),
            failures,
            f"{name}: context must not leak raw shell command",
        )

    unknown_shell = _decision(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "PatchFile",
            "tool_input": {"command": "cat payload > docs/adr/0010-future.md"},
        }
    )
    _assert(
        unknown_shell.get("outcome") == "needs_discoverability",
        failures,
        "unknown mutating-looking tool with shell governed payload must need discoverability",
    )
    _assert(
        "needs_discoverability_unknown_mutation" in unknown_shell.get("reason_codes", []),
        failures,
        "unknown shell discoverability must carry reason code",
    )

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

    discoverability = _decision(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "PatchFile",
            "tool_input": {"file_path": "docs/adr/0010-future.md"},
        }
    )
    _assert(
        discoverability.get("outcome") == "needs_discoverability",
        failures,
        "unknown mutating-looking tool on governed path must need discoverability",
    )
    _assert(
        discoverability.get("risk") == "needs-discoverability",
        failures,
        "unknown mutating-looking tool must not remain routine",
    )
    _assert(
        "needs_discoverability_unknown_mutation" in discoverability.get("reason_codes", []),
        failures,
        "discoverability decision must carry needs_discoverability_unknown_mutation reason code",
    )
    _assert(
        _trace(discoverability).get("unknown_mutating") is True,
        failures,
        "discoverability trace must name unknown mutating evidence",
    )
    _assert(
        mantra_gate.MARKER in str(discoverability.get("context")),
        failures,
        "discoverability context must include marker",
    )
    _assert(
        "outcome=needs_discoverability" in str(discoverability.get("context")),
        failures,
        "discoverability context must surface needs_discoverability outcome",
    )
    _assert(
        "risk=needs-discoverability" in str(discoverability.get("context")),
        failures,
        "discoverability context must surface needs-discoverability risk",
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
    _assert(
        "forbidden_class" in forbidden.get("reason_codes", []),
        failures,
        "forbidden Bash must carry forbidden_class reason code",
    )
    _assert(_trace(forbidden).get("forbidden_class") is True, failures, "forbidden trace must name forbidden evidence")

    secret = "token=" + "abc123"
    secret_forbidden = _decision(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": f"git push --force https://{secret}@example.invalid/repo main"},
        }
    )
    forbidden_reason = str(secret_forbidden.get("reason") or "")
    _assert(secret_forbidden.get("outcome") == "block", failures, "secret-bearing forbidden Bash must block")
    _assert(secret not in forbidden_reason, failures, "forbidden reason must redact token-like command text")
    _assert("https://" not in forbidden_reason, failures, "forbidden reason must not include raw URL command text")
    _assert(
        _trace(secret_forbidden).get("command_category") == "forbidden_git_force_push",
        failures,
        "forbidden trace must preserve safe command category",
    )

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
    expected_sources = {
        "command": "tool_input.command",
        "input": "tool_input.input",
        "patch": "tool_input.patch",
        "arguments.command": "tool_input.arguments.command",
        "arguments.input": "tool_input.arguments.input",
        "arguments.patch": "tool_input.arguments.patch",
        "top-level-input": "hook_input.input",
    }
    for name, payload in alias_payloads.items():
        hook_input = {"hookEventName": "PreToolUse", "toolName": "apply_patch", **payload}
        tool_input = pretooluse_kernel.hook_tool_input(hook_input)
        path = pretooluse_kernel.hook_tool_path(hook_input, tool_input)
        _assert(path.endswith("/SKILL.md"), failures, f"{name}: patch path must be extracted")
        decision = _decision(hook_input)
        _assert(decision.get("outcome") == "supervise", failures, f"{name}: apply_patch must supervise")
        _assert(path in str(decision.get("context")), failures, f"{name}: context must name extracted path")
        _assert(
            "patch_body_path_extracted" in decision.get("reason_codes", []),
            failures,
            f"{name}: apply_patch must carry patch_body_path_extracted reason code",
        )
        _assert(
            decision.get("payload_source") == expected_sources[name],
            failures,
            f"{name}: payload_source must identify the host payload field",
        )
        _assert(
            _trace(decision).get("patch_body_source") == decision.get("payload_source"),
            failures,
            f"{name}: classifier_trace must identify patch body source",
        )
        _assert(
            _trace(decision).get("path_source") == "patch_body",
            failures,
            f"{name}: classifier_trace must identify patch body path source",
        )

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
