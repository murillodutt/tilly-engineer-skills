#!/usr/bin/env python3
"""Host-neutral PreToolUse decision kernel.

This module owns only the input normalization and decision contract for the
senior-manager PreToolUse gate. It deliberately does not render Claude/Codex/
Cursor output, write hook ledgers, evaluate Cortex, or install/update hooks;
those integration concerns stay in `tes_install.py` so host-specific contracts
cannot leak into the decision core.
"""

from __future__ import annotations

import re
from typing import Any, Callable


PATCH_FILE_HEADER_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$")
GOVERNED_ARTIFACT_HINTS = (
    "AGENTS.md",
    "CLAUDE.md",
    "docs/adr/",
    "docs/governance/",
    "/SKILL.md",
    ".cursor/rules/",
)
# Keep host-emitted mutation names here, not in renderers, so governed-path
# supervision stays host-neutral while each adapter keeps its own output shape.
MUTATING_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit", "StrReplace", "Bash", "Shell", "shell", "apply_patch")
MUTATING_TOOL_NAME_HINTS = (
    "patch",
    "write",
    "edit",
    "replace",
    "delete",
    "remove",
    "create",
    "update",
    "move",
    "rename",
    "insert",
    "append",
    "modify",
)
NORMALIZED_TOOL_NAMES = {
    "shell": "Shell",
}
RiskClassifier = Callable[[str, list[str]], str]


def hook_event_name(hook_input: dict[str, Any], default: str = "SessionStart") -> str:
    value = hook_input.get("hook_event_name") or hook_input.get("hookEventName") or hook_input.get("event")
    return str(value or default)


def hook_tool_name(hook_input: dict[str, Any]) -> str:
    value = hook_input.get("tool_name") or hook_input.get("toolName")
    if isinstance(value, str):
        return value
    tool = hook_input.get("tool")
    return tool if isinstance(tool, str) else ""


def normalized_tool_name(tool_name: str) -> str:
    return NORMALIZED_TOOL_NAMES.get(tool_name, tool_name)


def hook_tool_input(hook_input: dict[str, Any]) -> dict[str, Any]:
    value = hook_input.get("tool_input")
    if value is None:
        value = hook_input.get("toolInput")
    return value if isinstance(value, dict) else {}


def hook_patch_paths(command: str) -> list[str]:
    paths: list[str] = []
    for line in command.splitlines():
        match = PATCH_FILE_HEADER_RE.match(line.strip())
        if match:
            paths.append(match.group(1).strip())
    return paths


def _first_string_value(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value:
            return value
    return ""


def _first_string_value_with_source(*pairs: tuple[str, Any]) -> tuple[str, str]:
    for source, value in pairs:
        if isinstance(value, str) and value:
            return value, source
    return "", "none"


def _tool_command_from_payload(payload: dict[str, Any]) -> str:
    command = _first_string_value(
        payload.get("command"),
        payload.get("input"),
        payload.get("patch"),
    )
    if command:
        return command
    arguments = payload.get("arguments")
    if isinstance(arguments, str) and arguments:
        return arguments
    if isinstance(arguments, dict):
        return _first_string_value(
            arguments.get("command"),
            arguments.get("input"),
            arguments.get("patch"),
        )
    return ""


def _tool_command_from_payload_with_source(prefix: str, payload: dict[str, Any]) -> tuple[str, str]:
    command, source = _first_string_value_with_source(
        (f"{prefix}.command", payload.get("command")),
        (f"{prefix}.input", payload.get("input")),
        (f"{prefix}.patch", payload.get("patch")),
    )
    if command:
        return command, source
    arguments = payload.get("arguments")
    if isinstance(arguments, str) and arguments:
        return arguments, f"{prefix}.arguments"
    if isinstance(arguments, dict):
        return _first_string_value_with_source(
            (f"{prefix}.arguments.command", arguments.get("command")),
            (f"{prefix}.arguments.input", arguments.get("input")),
            (f"{prefix}.arguments.patch", arguments.get("patch")),
        )
    return "", "none"


def hook_tool_command(hook_input: dict[str, Any], tool_input: dict[str, Any]) -> str:
    return _tool_command_from_payload(tool_input) or _tool_command_from_payload(hook_input)


def hook_tool_command_source(hook_input: dict[str, Any], tool_input: dict[str, Any]) -> tuple[str, str]:
    command, source = _tool_command_from_payload_with_source("tool_input", tool_input)
    if command:
        return command, source
    return _tool_command_from_payload_with_source("hook_input", hook_input)


def hook_tool_path(hook_input: dict[str, Any], tool_input: dict[str, Any]) -> str:
    value = (
        tool_input.get("file_path")
        or tool_input.get("path")
        or tool_input.get("filePath")
        or hook_input.get("file_path")
        or hook_input.get("path")
        or hook_input.get("filePath")
    )
    if value:
        return str(value)
    command = hook_tool_command(hook_input, tool_input)
    patch_paths = hook_patch_paths(command)
    return patch_paths[0] if patch_paths else ""


def hook_tool_path_source(hook_input: dict[str, Any], tool_input: dict[str, Any]) -> tuple[str, str, str]:
    value, source = _first_string_value_with_source(
        ("tool_input.file_path", tool_input.get("file_path")),
        ("tool_input.path", tool_input.get("path")),
        ("tool_input.filePath", tool_input.get("filePath")),
        ("hook_input.file_path", hook_input.get("file_path")),
        ("hook_input.path", hook_input.get("path")),
        ("hook_input.filePath", hook_input.get("filePath")),
    )
    if value:
        return value, source, "none"
    command, command_source = hook_tool_command_source(hook_input, tool_input)
    patch_paths = hook_patch_paths(command)
    if patch_paths:
        return patch_paths[0], "patch_body", command_source
    return "", "none", "none"


def looks_like_mutating_tool(tool_name: str) -> bool:
    """Return whether an unknown host tool name appears to mutate state."""
    normalized = tool_name.lower()
    return bool(normalized) and any(hint in normalized for hint in MUTATING_TOOL_NAME_HINTS)


def decide_pretooluse(
    hook_input: dict[str, Any],
    *,
    risk_classifier: RiskClassifier,
    marker: str,
) -> dict[str, Any]:
    """Return the host-neutral PreToolUse decision for a normalized tool call.

    The returned shape is intentionally small: `block` decides allow vs hard
    gate, `risk` records the classifier result, and `context`/`reason` carry the
    host-neutral message that renderers may project into their own protocol.
    """
    tool_name = hook_tool_name(hook_input)
    normalized_tool = normalized_tool_name(tool_name)
    tool_input = hook_tool_input(hook_input)
    file_path, path_source, patch_body_source = hook_tool_path_source(hook_input, tool_input)
    command, command_source = hook_tool_command_source(hook_input, tool_input)
    payload_source = command_source if command_source != "none" else path_source
    action = " ".join(part for part in (tool_name, command, file_path) if part).strip()
    paths = [file_path] if file_path else []
    patch_paths = hook_patch_paths(command)
    for patch_path in patch_paths:
        if patch_path and patch_path not in paths:
            paths.append(patch_path)

    risk = risk_classifier(action, paths)
    governed_paths = [path for path in paths if any(hint in path for hint in GOVERNED_ARTIFACT_HINTS)]
    governed = bool(governed_paths)
    mutating = tool_name in MUTATING_TOOLS or normalized_tool in MUTATING_TOOLS
    unknown_mutating = bool(tool_name) and not mutating and looks_like_mutating_tool(tool_name)
    reason_codes: list[str] = []
    if patch_paths:
        reason_codes.append("patch_body_path_extracted")
    if tool_name != normalized_tool:
        reason_codes.append("host_payload_labeling")
    if risk == "routine" and governed and mutating:
        risk = "material"
    classifier_trace = {
        "normalized_tool": normalized_tool,
        "payload_source": payload_source,
        "path_source": path_source,
        "path_match": "governed_surface" if governed else "none",
        "patch_body_source": patch_body_source,
        "forbidden_class": risk == "forbidden",
        "governed_surface": governed,
        "mutating_tool": mutating,
        "unknown_mutating": unknown_mutating,
    }
    base_decision = {
        "raw_tool_label": tool_name,
        "normalized_tool": normalized_tool,
        "payload_source": payload_source,
        "classifier_trace": classifier_trace,
    }

    if risk == "forbidden":
        return {
            **base_decision,
            "block": True,
            "risk": risk,
            "outcome": "block",
            "reason_codes": reason_codes + ["forbidden_class"],
            "reason": (
                f"{marker} Mantra Gate (senior manager): forbidden-class action "
                f"({action or tool_name}). Run the hard gate (VERIFY/SCOPE/BEST_PATH/"
                "DOCUMENT/ORACLE/RESOLVE/STATUS) and get explicit authorization before proceeding."
            ),
        }
    if risk == "routine" and governed and unknown_mutating:
        return {
            **base_decision,
            "block": False,
            "risk": "needs-discoverability",
            "outcome": "needs_discoverability",
            "reason_codes": reason_codes + ["needs_discoverability_unknown_mutation"],
            "context": (
                f"{marker} Mantra Gate discoverability: unknown mutating-looking tool "
                f"{tool_name} touched governed artifact {governed_paths[0]}. "
                "outcome=needs_discoverability risk=needs-discoverability. "
                "Add host fixture/native evidence before treating this as routine."
            ),
        }
    if governed and mutating and risk in ("material", "high-risk"):
        return {
            **base_decision,
            "block": False,
            "risk": risk,
            "outcome": "supervise",
            "reason_codes": reason_codes + ["governed_surface_mutation"],
            "context": (
                f"{marker} Mantra Gate supervising: {risk} change to governed artifact "
                f"{governed_paths[0] if governed_paths else file_path}. "
                "Confirm the contract obligation (ADR/SPEC) and bind a falsifiable oracle before closure."
            ),
        }
    if mutating:
        reason_codes.append("routine_non_governed")
    else:
        reason_codes.append("routine_non_mutating")
    return {**base_decision, "block": False, "risk": risk, "outcome": "allow", "reason_codes": reason_codes, "context": ""}
