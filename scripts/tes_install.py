#!/usr/bin/env python3
"""Thin mechanical TES installer with first-session post-install bootstrap."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pretooluse_kernel import (
    decide_pretooluse,
    hook_event_name as kernel_hook_event_name,
    hook_patch_paths as kernel_hook_patch_paths,
    hook_tool_command as kernel_hook_tool_command,
    hook_tool_input as kernel_hook_tool_input,
    hook_tool_name as kernel_hook_tool_name,
    hook_tool_path as kernel_hook_tool_path,
)
from pretooluse_session import coordinate_pretooluse_context


VERSION = "0.3.237"
SELF_TEST_SUBPROCESS_TIMEOUT = 180.0
MIN_PYTHON = (3, 11)
LOCK_PATH = Path(".tes/tes-install-lock.json")
POSTINSTALL_PATH = Path(".tes/postinstall.json")
POSTINSTALL_RUN_ROOT = Path(".tes/postinstall-runs")
POSTINSTALL_RUN_INDEX = POSTINSTALL_RUN_ROOT / "index.json"
PRETOOLUSE_CONTRACT_PACKAGE_PATH = Path("docs/architecture/PRETOOLUSE-CONTRACT.md")
PRETOOLUSE_CONTRACT_INSTALLED_PATH = Path(".tes/docs/architecture/PRETOOLUSE-CONTRACT.md")
POSTINSTALL_SENTINEL_RUN_LIMIT = 20
AGENTS = ("codex", "claude", "cursor")
POSTINSTALL_STATES = {"pending", "running", "complete", "needs_review"}
CLAUDE_SESSIONSTART_MATCHER = "startup|resume|clear|compact"
# PreToolUse (senior-manager pre-action) matcher: the mutating tools the gate supervises.
CLAUDE_PRETOOLUSE_MATCHER = "Write|Edit|MultiEdit|NotebookEdit|Bash|Shell|shell|apply_patch"
DEFAULT_POSTINSTALL_COMMANDS = (
    ("tes_init.py", ("--target", "{target}", "--yes")),
    ("project_context_oracle.py", ("--target", "{target}")),
    ("project_alignment_oracle.py", ("--target", "{target}")),
)
HOOK_RUNTIME_HELPERS = ("cortex_runtime.py", "pretooluse_kernel.py", "pretooluse_session.py")
OPERATING_MESH_PRETOOLUSE_HINTS = (
    "docs/agents/PROJECT-STATE.md",
    "docs/agents/PROJECT-ROADMAP.md",
    "docs/agents/EXECUTION-LINE.md",
    "docs/agents/QUALITY-GATES.md",
    "docs/agents/DECISIONS/",
)
PRETOOLUSE_LEDGER_SCHEMA_VERSION = "pretooluse_decision@2"
PRETOOLUSE_CEILING_AGGREGATION_POLICY = "per_host_no_cross_fill"
PRETOOLUSE_CEILING_HOST_ORDER = ("claude", "codex", "cursor")
PRETOOLUSE_LEGACY_POLICY = "historical_context_only"
HOOK_DEDUPE_CONTRACT_SCHEMA = "tes-hook-dedupe@1"
HOOK_HEALTH_SCHEMA_VERSION = "tes-hook-health@2"
HOOK_HEALTH_LEGACY_SCHEMA_VERSION = "tes-hook-health@1"
STALE_DISCIPLINE_PATH = ".agents/skills/tilly-engineer-skills/scripts/discipline_oracle.py"
CANONICAL_DISCIPLINE_PATH = ".agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py"


def python_executable() -> str:
    return os.environ.get("TES_PYTHON") or sys.executable or "python3"


def python_command_token() -> str:
    return shlex.quote(python_executable())


def command_literal(command: str) -> str:
    return json.dumps(command)


def python_runtime_block(command: Any) -> int:
    message = (
        "TES requires Python 3.11+ for local setup oracles. "
        f"Detected Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}. "
        "Install Python 3.11+ or set PYTHON=/path/to/python3.11, then rerun TES."
    )
    if command == "hook":
        print(
            json.dumps(
                {
                    "systemMessage": message,
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "permissionDecision": "allow",
                        "additionalContext": message,
                    },
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps({"version": VERSION, "status": "FAIL", "failures": [message]}, indent=2, sort_keys=True))
    print("[tes-install] FAIL")
    return 1


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def file_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def write_json(path: Path, data: dict[str, Any], dry_run: bool = False) -> dict[str, str]:
    if dry_run:
        return {"path": str(path), "action": "would-write-json"}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"path": str(path), "action": "write-json"}


def selected_agents(agent: str) -> list[str]:
    if agent == "all":
        return list(AGENTS)
    return [agent]


def normalize_agent_scope(values: list[Any]) -> list[str]:
    selected = {str(value) for value in values if str(value) in AGENTS}
    return [agent for agent in AGENTS if agent in selected]


def merged_agent_scope(existing: dict[str, Any], agents: list[str]) -> list[str]:
    existing_agents = existing.get("agents") if isinstance(existing.get("agents"), list) else []
    merged = normalize_agent_scope([*existing_agents, *agents])
    return merged or normalize_agent_scope(agents)


# Certified MCP consumers that bare `all` does NOT auto-install during
# bootstrap. VS Code's MCP config is a shared, user-owned `.vscode/mcp.json`;
# auto-writing it under bare `all` would clobber a user's existing servers.
# Absence here is a policy decision, not an oversight: F11 requires it to
# surface as a visible NOT_INSTALLED_BY_POLICY verdict (see
# policy_deferred_mcp_adapters / mcp_summary_from_results), not a silent drop.
MCP_POLICY_DEFERRED_ADAPTERS = ("vscode",)


def certified_mcp_consumers() -> tuple[str, ...]:
    # Source of truth for certified MCP consumer configs is install_mcp.ADAPTERS,
    # not a literal mirrored here (regression_guard: avoid narrow literal lists).
    try:
        import install_mcp  # type: ignore

        adapters = tuple(install_mcp.ADAPTERS)
        if adapters:
            return adapters
    except Exception:
        pass
    # Soft fallback if install_mcp is unavailable: the bootstrap install set
    # plus the policy-deferred consumers.
    return ("codex", "claude", "cursor", *MCP_POLICY_DEFERRED_ADAPTERS)


def selected_mcp_adapters(agent: str) -> list[str]:
    # VS Code is a certified MCP consumer config, not a TES adapter. Under bare
    # `all` it is policy-deferred (see policy_deferred_mcp_adapters), so the
    # install set excludes it to avoid clobbering a user's .vscode/mcp.json.
    if agent == "all":
        return [
            adapter
            for adapter in certified_mcp_consumers()
            if adapter not in MCP_POLICY_DEFERRED_ADAPTERS
        ]
    return [agent]


def policy_deferred_mcp_adapters(agent: str) -> list[str]:
    """Certified MCP consumers withheld under this agent scope by policy.

    Bare `all` defers VS Code: its MCP config is the user-owned shared
    `.vscode/mcp.json`, so bootstrap must not auto-write it. An explicit
    `--adapter vscode` install opts the user in; bare `all` instead emits a
    visible NOT_INSTALLED_BY_POLICY verdict (F11) so absence speaks.
    """
    if agent != "all":
        return []
    consumers = set(certified_mcp_consumers())
    return [adapter for adapter in MCP_POLICY_DEFERRED_ADAPTERS if adapter in consumers]


def source_root() -> Path:
    return Path(__file__).resolve().parents[1]


def target_root(path: Path) -> Path:
    return path.expanduser().resolve()


def package_source_block(target: Path, command: str) -> dict[str, Any] | None:
    import tes_bundle

    return tes_bundle.package_source_block(target, command)


def require_confirmation(args: argparse.Namespace, label: str) -> bool:
    if args.dry_run or args.yes:
        return True
    if not sys.stdin.isatty():
        print(f"[{label}] FAIL")
        print("- write mode requires --yes when stdin is not interactive")
        return False
    answer = input(f"{label} will write TES files into the target project. Type 'yes' to continue: ")
    if answer.strip().lower() != "yes":
        print(f"[{label}] CANCELLED")
        return False
    return True


def replace_or_insert_toml_feature(text: str, key: str, value: str) -> str:
    lines = text.splitlines()
    feature_header = None
    for index, line in enumerate(lines):
        if line.strip() == "[features]":
            feature_header = index
            break
    if feature_header is None:
        prefix = f"[features]\n{key} = {value}\n\n"
        return prefix + (text if text.endswith("\n") or not text else text + "\n")

    end = len(lines)
    for index in range(feature_header + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            end = index
            break
    for index in range(feature_header + 1, end):
        if lines[index].strip().startswith(f"{key} "):
            lines[index] = f"{key} = {value}"
            return "\n".join(lines).rstrip() + "\n"
    lines.insert(feature_header + 1, f"{key} = {value}")
    return "\n".join(lines).rstrip() + "\n"


def remove_toml_feature_line(text: str, key: str) -> str:
    lines = [
        line for line in text.splitlines()
        if not line.strip().startswith(f"{key} ")
    ]
    return "\n".join(lines).rstrip() + ("\n" if lines else "")


def write_text_if_changed(path: Path, text: str, target: Path, dry_run: bool, backup: bool = True) -> dict[str, str]:
    encoded = text.encode("utf-8")
    if path.exists() and path.read_bytes() == encoded:
        return {"path": rel(path, target), "action": "skip-identical"}
    had_existing = path.exists()
    if dry_run:
        return {"path": rel(path, target), "action": "would-update" if had_existing else "would-create"}
    backup_path = None
    if had_existing and backup:
        backup_path = path.with_name(f"{path.name}.bak-{file_stamp()}")
        shutil.copy2(path, backup_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    result = {"path": rel(path, target), "action": "update" if had_existing else "create"}
    if backup_path:
        result["backup"] = rel(backup_path, target)
    return result


def codex_hook_command(target: Path) -> str:
    """Return a Codex hook command safe in Git and non-Git targets."""
    resolved = str(target.resolve())
    script = f"{resolved}/.tes/bin/tes_install.py"
    return (
        f"{python_command_token()} {shlex.quote(script)} "
        f"hook --agent codex --target {shlex.quote(resolved)}"
    )


def codex_hook_snippet(target: Path) -> str:
    command = codex_hook_command(target)
    return f"""# TES first-session post-install hook.
[[hooks.SessionStart]]
matcher = "startup|resume"

[[hooks.SessionStart.hooks]]
type = "command"
command = {command_literal(command)}
timeout = 120
statusMessage = "Checking TES post-install"
"""


def codex_pretooluse_snippet(target: Path) -> str:
    command = codex_hook_command(target)
    return f"""# TES PreToolUse senior-manager gate.
[[hooks.PreToolUse]]
matcher = "{CLAUDE_PRETOOLUSE_MATCHER}"

[[hooks.PreToolUse.hooks]]
type = "command"
command = {command_literal(command)}
timeout = 10
"""


def install_codex_hook(target: Path, dry_run: bool) -> dict[str, str]:
    path = target / ".codex/config.toml"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    updated = replace_or_insert_toml_feature(existing, "hooks", "true")
    updated = remove_toml_feature_line(updated, "codex_hooks")
    updated = refresh_codex_tes_hook_blocks(updated)
    snippet = codex_hook_snippet(target).strip()
    pretooluse = codex_pretooluse_snippet(target).strip()
    updated = updated.rstrip() + "\n\n" + snippet + "\n\n" + pretooluse + "\n"
    backup = not is_codex_tes_only_mcp_config(existing)
    return write_text_if_changed(path, updated, target, dry_run, backup=backup)


def is_codex_tes_only_mcp_config(text: str) -> bool:
    stripped = text.strip()
    if not stripped or "[mcp_servers.tes-cortex]" not in stripped:
        return False
    lines = [line.strip() for line in stripped.splitlines() if line.strip() and not line.strip().startswith("#")]
    headers = [line for line in lines if line.startswith("[") and line.endswith("]")]
    return headers == ["[mcp_servers.tes-cortex]"]


CLAUDE_SETUP_RUNNING_MESSAGE = "IMPORTANT: TES setup is running. Please wait; do not start project work."
CLAUDE_SETUP_COMPLETED_MESSAGE = "TES setup completed. Please, run /tes-setup for the report."


def claude_notice_hook_entry() -> dict[str, Any]:
    return {
        "type": "command",
        "command": (
            f'{python_command_token()} "${{CLAUDE_PROJECT_DIR}}/.tes/bin/tes_install.py" '
            'hook --agent claude --target "${CLAUDE_PROJECT_DIR}" --announce-start'
        ),
        "timeout": 5,
    }


def claude_setup_hook_entry() -> dict[str, Any]:
    return {
        "type": "command",
        "command": (
            f'{python_command_token()} "${{CLAUDE_PROJECT_DIR}}/.tes/bin/tes_install.py" '
            'hook --agent claude --target "${CLAUDE_PROJECT_DIR}" --rewake-on-complete'
        ),
        "async": True,
        "asyncRewake": True,
        "statusMessage": CLAUDE_SETUP_RUNNING_MESSAGE,
        "timeout": 120,
    }


def hook_entry(agent: str) -> dict[str, Any]:
    if agent == "claude":
        return claude_setup_hook_entry()
    if agent == "cursor":
        return {
            "command": f"{python_command_token()} .tes/bin/tes_install.py hook --agent cursor --target .",
            "timeout": 120,
        }
    raise ValueError(f"unsupported hook entry agent: {agent}")


def hook_entries(agent: str) -> list[dict[str, Any]]:
    if agent == "claude":
        return [claude_notice_hook_entry(), claude_setup_hook_entry()]
    return [hook_entry(agent)]


def pretooluse_hook_entry(agent: str) -> dict[str, Any]:
    """A PreToolUse entry — runs the same hook command; the host injects the
    PreToolUse event on stdin, so no --rewake-on-complete (that is SessionStart-only).
    Synchronous so the gate decision lands before the tool call proceeds."""
    if agent == "claude":
        return {
            "type": "command",
            "command": (
                f'{python_command_token()} "${{CLAUDE_PROJECT_DIR}}/.tes/bin/tes_install.py" '
                'hook --agent claude --target "${CLAUDE_PROJECT_DIR}"'
            ),
            "timeout": 10,
        }
    if agent == "cursor":
        return {
            "command": f"{python_command_token()} .tes/bin/tes_install.py hook --agent cursor --target .",
            "timeout": 10,
        }
    raise ValueError(f"unsupported pretooluse entry agent: {agent}")


def ensure_hook_group(data: dict[str, Any], event: str, matcher: str, entry: dict[str, Any]) -> None:
    hooks = data.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        data["hooks"] = {}
        hooks = data["hooks"]
    groups = hooks.setdefault(event, [])
    if not isinstance(groups, list):
        hooks[event] = []
        groups = hooks[event]
    marker = json.dumps(entry, sort_keys=True)
    candidate_group: dict[str, Any] | None = None
    for group in groups:
        if not isinstance(group, dict):
            continue
        if matcher and str(group.get("matcher", "")) != matcher:
            continue
        handlers = group.get("hooks", [])
        if not isinstance(handlers, list):
            continue
        if candidate_group is None:
            candidate_group = group
        if any(json.dumps(handler, sort_keys=True) == marker for handler in handlers if isinstance(handler, dict)):
            return
    if candidate_group is not None:
        handlers = candidate_group.get("hooks")
        if not isinstance(handlers, list):
            candidate_group["hooks"] = []
            handlers = candidate_group["hooks"]
        handlers.append(entry)
        return
    groups.append({"matcher": matcher, "hooks": [entry]})


def is_tes_claude_hook_entry(entry: Any) -> bool:
    if not isinstance(entry, dict):
        return False
    marker = json.dumps(entry, sort_keys=True)
    return ".tes/bin/tes_install.py" in marker and "--agent" in marker and "claude" in marker


def remove_tes_claude_sessionstart_hooks(data: dict[str, Any]) -> None:
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return
    groups = hooks.get("SessionStart")
    if not isinstance(groups, list):
        return
    retained_groups: list[Any] = []
    for group in groups:
        if not isinstance(group, dict):
            retained_groups.append(group)
            continue
        handlers = group.get("hooks")
        if not isinstance(handlers, list):
            retained_groups.append(group)
            continue
        retained_handlers = [handler for handler in handlers if not is_tes_claude_hook_entry(handler)]
        if retained_handlers:
            group["hooks"] = retained_handlers
            retained_groups.append(group)
        elif len(retained_handlers) == len(handlers):
            retained_groups.append(group)
    hooks["SessionStart"] = retained_groups


def is_tes_hook_command(value: Any) -> bool:
    """True for a hook command string that invokes the TES hook entrypoint."""
    text = value if isinstance(value, str) else json.dumps(value, sort_keys=True)
    return ".tes/bin/tes_install.py" in text and "hook" in text


def remove_tes_cursor_hooks(data: dict[str, Any]) -> None:
    """Inverse of install_cursor_hook (ADR 0004 L3 SPEC-002).

    Remove only TES handlers from each event array, preserving non-TES hooks.
    """
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return
    for event, items in list(hooks.items()):
        if not isinstance(items, list):
            continue
        hooks[event] = [
            item for item in items
            if not (isinstance(item, dict) and is_tes_hook_command(item.get("command")))
        ]


def remove_tes_codex_json_hooks(data: dict[str, Any]) -> None:
    """Remove TES command handlers from Codex hooks.json, preserving foreign hooks."""
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return
    for event, groups in list(hooks.items()):
        if not isinstance(groups, list):
            continue
        retained_groups: list[Any] = []
        for group in groups:
            if not isinstance(group, dict):
                retained_groups.append(group)
                continue
            if is_tes_hook_command(group.get("command")):
                continue
            handlers = group.get("hooks")
            if not isinstance(handlers, list):
                retained_groups.append(group)
                continue
            retained_handlers = [
                handler for handler in handlers
                if not (isinstance(handler, dict) and is_tes_hook_command(handler.get("command")))
            ]
            if retained_handlers:
                updated_group = dict(group)
                updated_group["hooks"] = retained_handlers
                retained_groups.append(updated_group)
            elif len(retained_handlers) == len(handlers):
                retained_groups.append(group)
        hooks[event] = retained_groups


def _remove_codex_marked_block(lines: list[str], marker: str, section_prefix: str) -> list[str]:
    """Remove one marked TES TOML block (marker comment -> next block boundary).

    The block ends at the first header that does not belong to this block's
    section, OR at the next TES marker comment (so removing one block never eats
    the following TES block's marker comment), OR EOF.
    """
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == marker)
    except StopIteration:
        return lines
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        stripped = lines[idx].strip()
        if stripped.startswith("# TES ") and stripped != marker:
            end = idx
            break
        if (stripped.startswith("[") and stripped.endswith("]")
                and not stripped.lstrip("[").startswith(section_prefix)
                and not stripped.lstrip("[").startswith(f"{section_prefix}.hooks")):
            end = idx
            break
    return [*lines[:start], *lines[end:]]


def _remove_codex_legacy_tes_hook_block(lines: list[str], section_prefix: str) -> list[str]:
    """Remove an unmarked TES-owned Codex hook block for one TOML hook section."""
    header = f"[[{section_prefix}]]"
    index = 0
    while index < len(lines):
        if lines[index].strip() != header:
            index += 1
            continue
        end = len(lines)
        for idx in range(index + 1, len(lines)):
            stripped = lines[idx].strip()
            if stripped.startswith("# TES "):
                end = idx
                break
            if (
                stripped.startswith("[")
                and stripped.endswith("]")
                and not stripped.lstrip("[").startswith(section_prefix)
                and not stripped.lstrip("[").startswith(f"{section_prefix}.hooks")
            ):
                end = idx
                break
        block = "\n".join(lines[index:end])
        if ".tes/bin/tes_install.py" in block and " hook" in block and "--agent codex" in block:
            lines = [*lines[:index], *lines[end:]]
            continue
        index += 1
    return lines


def refresh_codex_tes_hook_blocks(text: str) -> str:
    """Replace TES-owned Codex hook blocks with the current source templates."""
    lines = text.splitlines()
    for marker, section_prefix in (
        ("# TES first-session post-install hook.", "hooks.SessionStart"),
        ("# TES PreToolUse senior-manager gate.", "hooks.PreToolUse"),
    ):
        lines = _remove_codex_marked_block(lines, marker, section_prefix)
        lines = _remove_codex_legacy_tes_hook_block(lines, section_prefix)
    body = "\n".join(lines).strip()
    return (body + "\n") if body else ""


def remove_tes_codex_hook_text(text: str) -> str:
    """Inverse of install_codex_hook: drop the TES SessionStart AND PreToolUse hook
    blocks and the TES-managed hooks feature flag, preserving any other Codex config.
    """
    lines = text.splitlines()
    lines = _remove_codex_marked_block(
        lines, "# TES first-session post-install hook.", "hooks.SessionStart"
    )
    lines = _remove_codex_marked_block(
        lines, "# TES PreToolUse senior-manager gate.", "hooks.PreToolUse"
    )
    # Legacy fallback: a SessionStart block whose marker comment was lost.
    for index, line in enumerate(lines):
        if line.strip() != "[[hooks.SessionStart]]":
            continue
        end = len(lines)
        for idx in range(index + 1, len(lines)):
            next_stripped = lines[idx].strip()
            if (
                next_stripped.startswith("[")
                and next_stripped.endswith("]")
                and not next_stripped.lstrip("[").startswith("hooks.SessionStart")
                and not next_stripped.lstrip("[").startswith("hooks.SessionStart.hooks")
            ):
                end = idx
                break
        block = "\n".join(lines[index:end])
        if ".tes/bin/tes_install.py" in block and " hook" in block:
            lines = [*lines[:index], *lines[end:]]
            break
    # Remove TES-managed feature flag lines. `hooks` is the canonical Codex key;
    # `codex_hooks` is kept here only as legacy cleanup for older TES installs.
    lines = [
        line for line in lines
        if line.strip() not in {"hooks = true", "codex_hooks = true"}
    ]
    body = "\n".join(lines).strip()
    return (body + "\n") if body else ""


def remove_tes_hooks(target: Path, agent: str, dry_run: bool = False, backup: bool = True) -> dict[str, str]:
    """Unified hook remover (ADR 0004 L3 SPEC-002). Writer-inverse per agent;
    preserves non-TES hooks; removes a TES-only file when it becomes empty."""
    if agent == "claude":
        path = target / ".claude/settings.json"
        if not path.exists():
            return {"agent": agent, "action": "already-absent"}
        data = read_json(path)
        remove_tes_claude_sessionstart_hooks(data)
        remove_tes_claude_event_hooks(data, "PreToolUse")
        text = json.dumps(data, indent=2, sort_keys=True) + "\n"
        return {**write_text_if_changed(path, text, target, dry_run, backup=backup), "agent": agent}
    if agent == "cursor":
        path = target / ".cursor/hooks.json"
        if not path.exists():
            return {"agent": agent, "action": "already-absent"}
        data = read_json(path)
        remove_tes_cursor_hooks(data)
        hooks = data.get("hooks")
        # If only TES hooks existed and all event arrays are now empty, and the
        # file holds nothing but version+hooks, remove the TES-only file.
        only_empty = isinstance(hooks, dict) and all(not v for v in hooks.values())
        if only_empty and set(data.keys()) <= {"version", "hooks"}:
            if not dry_run:
                path.unlink()
            return {"agent": agent, "path": rel(path, target), "action": "would-remove-file" if dry_run else "remove-file"}
        text = json.dumps(data, indent=2, sort_keys=True) + "\n"
        return {**write_text_if_changed(path, text, target, dry_run, backup=backup), "agent": agent}
    if agent == "codex":
        actions: list[str] = []
        touched: list[str] = []
        path = target / ".codex/config.toml"
        if path.exists():
            stripped = remove_tes_codex_hook_text(path.read_text(encoding="utf-8"))
            touched.append(rel(path, target))
            if not stripped.strip():
                if not dry_run:
                    path.unlink()
                actions.append("would-remove-config" if dry_run else "remove-config")
            else:
                result = write_text_if_changed(path, stripped, target, dry_run, backup=backup)
                actions.append(result.get("action", "update-config"))
        hooks_path = target / ".codex/hooks.json"
        if hooks_path.exists():
            data = read_json(hooks_path)
            remove_tes_codex_json_hooks(data)
            hooks = data.get("hooks")
            only_empty = isinstance(hooks, dict) and all(not v for v in hooks.values())
            touched.append(rel(hooks_path, target))
            if only_empty and set(data.keys()) <= {"version", "hooks"}:
                if not dry_run:
                    hooks_path.unlink()
                actions.append("would-remove-hooks-json" if dry_run else "remove-hooks-json")
            else:
                text = json.dumps(data, indent=2, sort_keys=True) + "\n"
                result = write_text_if_changed(hooks_path, text, target, dry_run, backup=backup)
                actions.append(result.get("action", "update-hooks-json"))
        return {
            "agent": agent,
            "path": ",".join(touched) if touched else ".codex/config.toml,.codex/hooks.json",
            "action": "+".join(actions) if actions else "already-absent",
        }
    return {"agent": agent, "action": "unsupported"}


def install_claude_hook(target: Path, dry_run: bool) -> dict[str, str]:
    path = target / ".claude/settings.json"
    data = read_json(path)
    remove_tes_claude_sessionstart_hooks(data)
    for entry in hook_entries("claude"):
        ensure_hook_group(data, "SessionStart", CLAUDE_SESSIONSTART_MATCHER, entry)
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    return write_text_if_changed(path, text, target, dry_run)


def install_cursor_hook(target: Path, dry_run: bool) -> dict[str, str]:
    path = target / ".cursor/hooks.json"
    data = read_json(path)
    data.setdefault("version", 1)
    hooks = data.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        data["hooks"] = {}
        hooks = data["hooks"]
    entry = hook_entry("cursor")
    for event in ("sessionStart", "beforeSubmitPrompt"):
        items = hooks.setdefault(event, [])
        if not isinstance(items, list):
            hooks[event] = []
            items = hooks[event]
        marker = json.dumps(entry, sort_keys=True)
        if not any(json.dumps(item, sort_keys=True) == marker for item in items if isinstance(item, dict)):
            items.append(entry)
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    return write_text_if_changed(path, text, target, dry_run)


def remove_tes_claude_event_hooks(data: dict[str, Any], event: str) -> None:
    """Strip TES-owned handlers from any Claude hook event (ownership-marker based).

    Mirrors remove_tes_claude_sessionstart_hooks but parameterized by event, so the
    PreToolUse install is idempotent and uninstall removes only TES entries while
    preserving foreign hooks under the same event.
    """
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return
    groups = hooks.get(event)
    if not isinstance(groups, list):
        return
    retained_groups: list[Any] = []
    for group in groups:
        if not isinstance(group, dict):
            retained_groups.append(group)
            continue
        handlers = group.get("hooks")
        if not isinstance(handlers, list):
            retained_groups.append(group)
            continue
        retained_handlers = [handler for handler in handlers if not is_tes_claude_hook_entry(handler)]
        if retained_handlers:
            group["hooks"] = retained_handlers
            retained_groups.append(group)
        elif not handlers:
            retained_groups.append(group)
    if retained_groups:
        hooks[event] = retained_groups
    else:
        hooks.pop(event, None)


def install_claude_pretooluse_hook(target: Path, dry_run: bool) -> dict[str, str]:
    path = target / ".claude/settings.json"
    data = read_json(path)
    remove_tes_claude_event_hooks(data, "PreToolUse")
    ensure_hook_group(data, "PreToolUse", CLAUDE_PRETOOLUSE_MATCHER, pretooluse_hook_entry("claude"))
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    return write_text_if_changed(path, text, target, dry_run)


def install_cursor_pretooluse_hook(target: Path, dry_run: bool) -> dict[str, str]:
    path = target / ".cursor/hooks.json"
    data = read_json(path)
    data.setdefault("version", 1)
    hooks = data.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        data["hooks"] = {}
        hooks = data["hooks"]
    entry = pretooluse_hook_entry("cursor")
    items = hooks.setdefault("preToolUse", [])
    if not isinstance(items, list):
        hooks["preToolUse"] = []
        items = hooks["preToolUse"]
    marker = json.dumps(entry, sort_keys=True)
    if not any(json.dumps(item, sort_keys=True) == marker for item in items if isinstance(item, dict)):
        items.append(entry)
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    return write_text_if_changed(path, text, target, dry_run)


def source_helper_path(script_name: str) -> Path | None:
    package = source_root() / "scripts" / script_name
    if package.exists():
        return package
    sibling = Path(__file__).resolve().with_name(script_name)
    if sibling.exists():
        return sibling
    return None


def install_hook_runtime_helpers(target: Path, dry_run: bool) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for script_name in HOOK_RUNTIME_HELPERS:
        destination = target / ".tes/bin" / script_name
        source = source_helper_path(script_name)
        if source is None:
            actions.append({"path": rel(destination, target), "action": "missing-source", "helper": script_name})
            continue
        if destination.exists() and destination.read_bytes() == source.read_bytes():
            actions.append({"path": rel(destination, target), "action": "skip-identical", "helper": script_name})
            continue
        if dry_run:
            actions.append({"path": rel(destination, target), "action": "would-copy-helper", "helper": script_name})
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        actions.append({"path": rel(destination, target), "action": "copy-helper", "helper": script_name})
    return actions


def install_hooks(target: Path, agents: list[str], dry_run: bool) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = install_hook_runtime_helpers(target, dry_run)
    for agent in agents:
        if agent == "codex":
            actions.append({**install_codex_hook(target, dry_run), "agent": agent})
        elif agent == "claude":
            actions.append({**install_claude_hook(target, dry_run), "agent": agent})
            actions.append({**install_claude_pretooluse_hook(target, dry_run), "agent": agent, "event": "PreToolUse"})
        elif agent == "cursor":
            actions.append({**install_cursor_hook(target, dry_run), "agent": agent})
            actions.append({**install_cursor_pretooluse_hook(target, dry_run), "agent": agent, "event": "preToolUse"})
    return actions


def sentinel_payload(agent: str, agents: list[str], mode: str, existing: dict[str, Any] | None = None) -> dict[str, Any]:
    existing = existing or {}
    runs = existing.get("runs") if isinstance(existing.get("runs"), list) else []
    requested_by = existing.get("requested_by")
    return {
        "schema": "tes-postinstall@1",
        "version": VERSION,
        "state": "pending",
        "created_at": existing.get("created_at") or utc_stamp(),
        "updated_at": utc_stamp(),
        "requested_by": str(requested_by) if isinstance(requested_by, str) and requested_by else agent,
        "executed_by": agent,
        "agents": merged_agent_scope(existing, agents),
        "mode": mode,
        "runs": bounded_sentinel_runs(runs),
    }


def bounded_sentinel_runs(runs: list[Any]) -> list[str]:
    normalized = [str(item) for item in runs if isinstance(item, str) and item]
    return normalized[-POSTINSTALL_SENTINEL_RUN_LIMIT:]


def unique_postinstall_run_path(target: Path, agent: str) -> Path:
    root = target / POSTINSTALL_RUN_ROOT
    base = f"{file_stamp()}-{agent}"
    path = root / f"{base}.json"
    counter = 1
    while path.exists():
        counter += 1
        path = root / f"{base}-{counter}.json"
    return path


def postinstall_run_index(target: Path, run_rel: str, dry_run: bool) -> dict[str, Any]:
    index_path = target / POSTINSTALL_RUN_INDEX
    existing = read_json(index_path)
    runs = existing.get("runs") if isinstance(existing.get("runs"), list) else []
    normalized = [str(item) for item in runs if isinstance(item, str) and item]
    if run_rel not in normalized:
        normalized.append(run_rel)
    payload = {
        "schema": "tes-postinstall-run-index@1",
        "version": VERSION,
        "updated_at": utc_stamp(),
        "total_runs": len(normalized),
        "latest_run": run_rel,
        "runs": normalized,
    }
    write_json(index_path, payload, dry_run=dry_run)
    return {
        "path": rel(index_path, target),
        "total_runs": payload["total_runs"],
        "latest_run": run_rel,
    }


def write_pending_sentinel(target: Path, agent: str, agents: list[str], mode: str, dry_run: bool) -> dict[str, str]:
    existing = read_json(target / POSTINSTALL_PATH)
    state = str(existing.get("state") or "")
    if state == "complete":
        payload = {
            **existing,
            "state": "pending",
            "updated_at": utc_stamp(),
            "requested_by": agent,
            "executed_by": agent,
            "agents": merged_agent_scope(existing, agents),
        }
    elif state in POSTINSTALL_STATES:
        payload = {
            **sentinel_payload(agent, agents, mode, existing),
            "requested_by": agent,
            "state": state if state == "running" else "pending",
        }
    else:
        payload = sentinel_payload(agent, agents, mode, existing)
    return write_json(target / POSTINSTALL_PATH, payload, dry_run=dry_run)


def derive_sentinel_reason(
    apply_result: dict[str, Any],
    certification_result: dict[str, Any] | None,
) -> str:
    """Name the gate that actually blocks. The review sentinel previously always
    said "obsolete runtime artifacts need review", but the trigger is two
    distinct conditions (apply NEEDS_REVIEW from obsolete cleanup, OR a
    non-passing post-install certification). When obsolete cleanup is clean and
    certification is the blocker, that boilerplate sent operators down the wrong
    path — so derive the reason from whichever condition is genuinely non-passing,
    naming the failing oracle component when it is certification."""
    obsolete = apply_result.get("obsolete_cleanup") if isinstance(apply_result, dict) else None
    review_items = obsolete.get("review_items") if isinstance(obsolete, dict) else None
    if apply_result.get("status") == "NEEDS_REVIEW" and review_items:
        return "obsolete runtime artifacts need review"

    # Tolerate both shapes of certification result: the raw run_installed_
    # certification dict (components live under "payload") and the summarized
    # dict (components at top level). The call site passes the RAW result, so
    # reading only the top level silently lost the component names in production.
    cert = certification_result if isinstance(certification_result, dict) else {}
    cert_status = str(cert.get("status") or "")
    # Guard against an absent/empty certification result: an empty status must
    # not rank as a blocker (rank("") defaults to NEEDS_REVIEW) and falsely
    # report a certification gate when none ran.
    cert_blocks = bool(cert_status) and certification_status_rank(cert_status) >= certification_status_rank("NEEDS_REVIEW")
    if cert_blocks:
        components = cert.get("components")
        if not isinstance(components, dict) or not components:
            payload = cert.get("payload") if isinstance(cert.get("payload"), dict) else {}
            raw_components = payload.get("components") if isinstance(payload.get("components"), dict) else {}
            components = {
                name: (value.get("status") if isinstance(value, dict) else value)
                for name, value in raw_components.items()
            }
        blocking = [
            name for name, status in components.items()
            if certification_status_rank(str(status or "")) >= certification_status_rank("NEEDS_REVIEW")
        ]
        if blocking:
            return f"installed certification: {', '.join(sorted(blocking))} needs review"
        return f"installed certification status {cert_status.lower()} (component detail unavailable)"

    if review_items:
        return "obsolete runtime artifacts need review"
    return "post-install review required"


def write_review_sentinel(
    target: Path,
    agent: str,
    agents: list[str],
    mode: str,
    apply_result: dict[str, Any],
    dry_run: bool,
    certification_result: dict[str, Any] | None = None,
) -> dict[str, str]:
    existing = read_json(target / POSTINSTALL_PATH)
    payload = {
        **sentinel_payload(agent, agents, mode, existing),
        "state": "needs_review",
        "reason": derive_sentinel_reason(apply_result, certification_result),
        "apply": summarize_result(apply_result),
    }
    return write_json(target / POSTINSTALL_PATH, payload, dry_run=dry_run)


def pretooluse_contract_lock_reference(target: Path) -> dict[str, Any]:
    installed = target / PRETOOLUSE_CONTRACT_INSTALLED_PATH
    return {
        "package_path": PRETOOLUSE_CONTRACT_PACKAGE_PATH.as_posix(),
        "installed_path": PRETOOLUSE_CONTRACT_INSTALLED_PATH.as_posix(),
        "sha256": sha256_file(installed) if installed.is_file() else None,
        "version": VERSION,
    }


def write_install_lock(
    target: Path,
    agent: str,
    agents: list[str],
    mode: str,
    stage: dict[str, Any],
    legacy_retirement_result: dict[str, Any],
    apply_result: dict[str, Any],
    hook_actions: list[dict[str, str]],
    mcp_result: dict[str, Any],
    certification_result: dict[str, Any],
    dry_run: bool,
    attached_surfaces: list[str] | None = None,
) -> dict[str, str]:
    manifest = read_json(target / ".tes/manifest.json")
    metadata = manifest.get("metadata") if isinstance(manifest.get("metadata"), dict) else {}
    lock = {
        "schema": "tes-install-lock@1",
        "version": VERSION,
        "installed_at": utc_stamp(),
        "target": str(target),
        "agent": agent,
        "agents": agents,
        "mode": mode,
        "source_repository": metadata.get("source_repository"),
        "source_commit": metadata.get("source_commit"),
        "pretooluse_contract": pretooluse_contract_lock_reference(target),
        "stage": summarize_result(stage),
        "legacy_retirement": summarize_legacy_retirement_result(legacy_retirement_result),
        "attached_surfaces": attached_surfaces or ["capsule"],
        "apply": summarize_result(apply_result),
        "hooks": hook_actions,
        "mcp": summarize_mcp_result(mcp_result),
        "certification": summarize_certification_result(certification_result),
    }
    return write_json(target / LOCK_PATH, lock, dry_run=dry_run)


def transact_lock_surface(
    target: Path,
    surface: str,
    *,
    attach: bool,
    certification_result: dict[str, Any] | None,
    dry_run: bool,
) -> dict[str, Any]:
    """Ceiling F27: attach/detach must re-transact the install lock.

    A full `install` is not the only operation that mutates which surfaces are
    materialized — `attach`/`detach` do too, yet historically left the lock's
    `attached_surfaces` (read by hook_surface_attached / admission) pointing at
    the install-time set. This narrowly patches that one field plus the lock's
    version/installed_at and certification summary, additively: attach merges the
    surface in, detach removes it but never drops the capsule. Honors --dry-run.
    """
    if dry_run:
        return {"action": "would-transact-lock", "surface": surface, "attach": attach}
    lock = read_json(target / LOCK_PATH)
    if not lock:
        # No prior install lock to transact (e.g. capsule written without a lock):
        # nothing to keep in sync, report rather than fabricate a partial lock.
        return {"action": "no-install-lock", "surface": surface, "attach": attach}
    surfaces = lock.get("attached_surfaces")
    current = {str(s) for s in surfaces if isinstance(s, str)} if isinstance(surfaces, list) else set()
    current.add("capsule")  # the capsule is always present and never detachable
    if attach:
        current.add(surface)
    else:
        current.discard(surface)
        current.add("capsule")  # detach must never drop the capsule
    lock["attached_surfaces"] = sorted(current)
    lock["version"] = VERSION
    lock["installed_at"] = utc_stamp()
    if isinstance(certification_result, dict):
        lock["certification"] = summarize_certification_result(certification_result)
    write_action = write_json(target / LOCK_PATH, lock, dry_run=False)
    return {
        "action": "transact-lock",
        "surface": surface,
        "attach": attach,
        "attached_surfaces": lock["attached_surfaces"],
        "write": write_action,
    }


def summarize_result(result: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key in ("version", "status", "source", "stage_dir", "manifest", "entries", "mode", "backup_id", "installed_manifest"):
        if key in result:
            summary[key] = result[key]
    if isinstance(result.get("obsolete_cleanup"), dict):
        cleanup = result["obsolete_cleanup"]
        summary["obsolete_cleanup"] = {
            "status": cleanup.get("status"),
            "review_items": cleanup.get("review_items", []),
            "review_backup": cleanup.get("review_backup"),
        }
    if result.get("failures"):
        summary["failures"] = result["failures"]
    return summary


def parse_json_output(text: str) -> dict[str, Any]:
    start = text.find("{")
    if start < 0:
        return {}
    depth = 0
    in_string = False
    escaping = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaping:
                escaping = False
            elif char == "\\":
                escaping = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                try:
                    data = json.loads(text[start:index + 1])
                except json.JSONDecodeError:
                    return {}
                return data if isinstance(data, dict) else {}
    try:
        data = json.loads(text[start:])
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def mcp_command_result(target: Path, adapter: str, dry_run: bool, timeout: float) -> dict[str, Any]:
    script = helper_path(target, "install_mcp.py")
    command = [
        sys.executable,
        str(script),
        "--target",
        str(target),
        "--adapter",
        adapter,
        "--overwrite",
        "--json-only",
    ]
    if dry_run:
        command.append("--dry-run")
    else:
        command.append("--yes")
    try:
        result = subprocess.run(
            command,
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "adapter": adapter,
            "command": " ".join(command),
            "returncode": 124,
            "status": "BLOCKED",
            "stdout": stdout.strip(),
            "stderr": (stderr.strip() + f"\ncommand timed out after {timeout:g}s").strip(),
            "payload": {},
        }
    payload = parse_json_output(result.stdout)
    return {
        "adapter": adapter,
        "command": " ".join(command),
        "returncode": result.returncode,
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "payload": payload,
    }


def mcp_policy_verdicts(agent: str) -> list[dict[str, Any]]:
    """Visible per-consumer policy verdicts for certified MCP consumers that
    bootstrap deliberately did not install under this agent scope (F11).

    Bare `all` defers VS Code; surfacing NOT_INSTALLED_BY_POLICY here keeps the
    absence a documented signal instead of an invisible drop. The hint tells the
    user how to opt in explicitly.
    """
    verdicts: list[dict[str, Any]] = []
    for adapter in policy_deferred_mcp_adapters(agent):
        verdicts.append(
            {
                "adapter": adapter,
                "verdict": "NOT_INSTALLED_BY_POLICY",
                "reason": (
                    "shared user-owned config; bare 'all' does not auto-write it "
                    "to avoid clobbering existing servers"
                ),
                "hint": f"--adapter {adapter}",
            }
        )
    return verdicts


def mcp_summary_from_results(agent: str, adapters: list[str], results: list[dict[str, Any]], dry_run: bool) -> dict[str, Any]:
    failures: list[str] = []
    configs: list[dict[str, Any]] = []
    registrations: list[dict[str, Any]] = []
    server_files: list[dict[str, Any]] = []
    for item in results:
        payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
        failures.extend(str(failure) for failure in payload.get("failures", []) if failure)
        if item.get("returncode") != 0 and not payload.get("failures"):
            detail = item.get("stderr") or item.get("stdout") or "MCP installer failed"
            failures.append(f"{item.get('adapter')}: {str(detail).splitlines()[-1]}")
        for action in payload.get("configs", []) if isinstance(payload.get("configs"), list) else []:
            if isinstance(action, dict):
                configs.append(action)
        for action in payload.get("config_registrations", []) if isinstance(payload.get("config_registrations"), list) else []:
            if isinstance(action, dict):
                registrations.append(action)
        for action in payload.get("server_files", []) if isinstance(payload.get("server_files"), list) else []:
            if isinstance(action, dict):
                server_files.append(action)
    status = "FAIL" if failures else ("DRY-RUN" if dry_run else "INSTALLED")
    return {
        "status": status,
        "agent": agent,
        "adapters": adapters,
        "server": "tes-cortex",
        "configs": configs,
        "config_registrations": registrations,
        "server_files": server_files,
        "policy_verdicts": mcp_policy_verdicts(agent),
        "commands": [
            {
                "adapter": item["adapter"],
                "command": item["command"],
                "status": item["status"],
                "returncode": item["returncode"],
            }
            for item in results
        ],
        "failures": failures,
    }


def run_mcp_bootstrap(target: Path, agent: str, dry_run: bool, timeout: float) -> dict[str, Any]:
    adapters = selected_mcp_adapters(agent)
    results = [mcp_command_result(target, adapter, dry_run, timeout) for adapter in adapters]
    return mcp_summary_from_results(agent, adapters, results, dry_run)


def summarize_mcp_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result.get("status"),
        "adapters": result.get("adapters", []),
        "server": result.get("server"),
        "configs": result.get("configs", []),
        "config_registrations": result.get("config_registrations", []),
        # F11: policy-deferred consumers (e.g. VS Code under bare 'all') stay
        # visible as NOT_INSTALLED_BY_POLICY rather than dropping silently.
        "policy_verdicts": result.get("policy_verdicts", []),
        "failures": result.get("failures", []),
    }


def certification_status_rank(status: str) -> int:
    return {"PASS": 0, "DRY-RUN": 0, "PARTIAL": 1, "NEEDS_REVIEW": 2, "BLOCKED": 3, "FAIL": 3}.get(status, 2)


def run_installed_certification(target: Path, dry_run: bool, timeout: float) -> dict[str, Any]:
    script = helper_path(target, "installed_certification_oracle.py")
    command = [sys.executable, str(script), "--target", str(target), "--json-only"]
    if dry_run:
        return {
            "status": "DRY-RUN",
            "command": " ".join(command),
            "returncode": 0,
            "payload": {},
            "failures": [],
        }
    try:
        result = subprocess.run(
            command,
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "status": "BLOCKED",
            "command": " ".join(command),
            "returncode": 124,
            "stdout": stdout.strip(),
            "stderr": (stderr.strip() + f"\ncommand timed out after {timeout:g}s").strip(),
            "payload": {},
            "failures": [f"installed certification timed out after {timeout:g}s"],
        }
    payload = parse_json_output(result.stdout)
    status = str(payload.get("status") or ("PASS" if result.returncode == 0 else "FAIL"))
    failures = [str(item) for item in payload.get("failures", []) if item] if isinstance(payload.get("failures"), list) else []
    # Derive human-readable failures from the structured certification payload,
    # never from raw stdout. The oracle prints its full result as indented JSON
    # on stdout; appending result.stdout here injected that whole blob as a
    # single failures[] string, which the bin then leaked line-by-line as `],`
    # `},` fragments. Prefer the payload's findings (component + repair route);
    # fall back to a one-line message only when there is nothing structured.
    if result.returncode != 0 and not failures:
        findings = payload.get("findings") if isinstance(payload.get("findings"), list) else []
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            component = str(finding.get("component") or "certification")
            repair = str(finding.get("repair") or finding.get("status") or "needs review").strip()
            failures.append(f"{component}: {repair}")
        if not failures:
            stderr_line = result.stderr.strip().splitlines()[0] if result.stderr.strip() else ""
            failures.append(stderr_line or "installed certification reported a non-passing status")
    return {
        "status": status,
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "payload": payload,
        "failures": failures,
    }


def summarize_certification_result(result: dict[str, Any]) -> dict[str, Any]:
    payload = result.get("payload") if isinstance(result.get("payload"), dict) else {}
    components = payload.get("components") if isinstance(payload.get("components"), dict) else {}
    return {
        "status": result.get("status"),
        "components": {
            name: value.get("status")
            for name, value in components.items()
            if isinstance(value, dict) and "status" in value
        },
        "findings": payload.get("findings", []),
        "negative_checks": payload.get("negative_checks", {}),
        "failures": result.get("failures", []),
    }


def run_legacy_retirement(target: Path, dry_run: bool) -> dict[str, Any]:
    """Retire closed-catalog legacy runtime before installing fresh assets."""
    try:
        import tes_legacy_retirement  # type: ignore
    except ModuleNotFoundError as exc:
        return {
            "version": VERSION,
            "status": "FAIL",
            "failures": [f"tes_legacy_retirement.py unavailable: {exc}"],
        }
    if dry_run:
        plan = tes_legacy_retirement.build_plan(target)
        return {**plan, "dry_run": True}
    return tes_legacy_retirement.apply_plan(target, yes=True)


def summarize_legacy_retirement_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result.get("status"),
        "legacy_retirement_required": result.get("legacy_retirement_required"),
        "counts": result.get("counts", {}),
        "writes": result.get("writes", []),
        "failures": result.get("failures", []),
    }


def is_git_work_tree(target: Path) -> bool:
    """True when target is inside a Git work tree (the Git-eligibility predicate)."""
    result = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "--is-inside-work-tree"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def git_readiness(target: Path, hooks_attached: bool) -> dict[str, Any]:
    """Typed Git readiness for the install headline (ceiling: never hide BLOCKED).

    When hooks are attached but the target is not a Git work tree, the Git gates
    (pre-push, strict pre-commit, field reports) cannot be installed — readiness
    is NEEDS_GIT, surfaced in the headline rather than buried in a payload detail.
    The install itself is still reversible (capsule on disk), so this is not FAIL;
    the headline says NEEDS_GIT and the operator knows proof is pending Git.
    """
    if not hooks_attached:
        return {"status": "NOT_APPLICABLE", "git_work_tree": None}
    eligible = is_git_work_tree(target)
    return {
        "status": "READY" if eligible else "NEEDS_GIT",
        "git_work_tree": eligible,
        "reason": None if eligible else "target is not a Git work tree; Git gates (pre-push, strict pre-commit) cannot be installed",
    }


# Certification findings that do not represent an installed-target DEFECT, only
# readiness pending something outside the just-written files:
#  - mcp_registration / hook_runtime_health pending = the host has not yet
#    (re)spawned the server / fired the hook (expected on a fresh, not-reopened
#    target);
#  - release_claim = the BUNDLE/source the adopter installed from was not
#    provably sealed. That is a release-identity advisory about the artifact, not
#    a defect of the reversible on-disk install, so it does not block the install
#    headline (it still surfaces, and it DOES gate a real release-seal claim).
HOST_PENDING_FINDING_COMPONENTS = {"mcp_registration", "hook_runtime_health"}
RELEASE_IDENTITY_FINDING_COMPONENTS = {"release_claim"}
# Ceiling F24: a floor-green hook whose PreToolUse ceiling has not yet been
# observed surfaces a non-gating INFO ceiling_evidence finding. On a fresh
# install that is readiness (the ceiling is proven by exercising the host),
# exactly like host-pending evidence — it must not turn the headline into a
# review item.
CEILING_READINESS_FINDING_COMPONENTS = {"ceiling_evidence"}


def certification_is_host_pending_only(certification_result: dict[str, Any]) -> bool:
    """True when every non-pass certification finding is readiness, not a defect.

    A clean install whose only open findings are host-pending (MCP/host not yet
    restarted, hooks not yet fired) or a release-identity advisory (installed
    from an unsealed bundle) is READY_PENDING_HOST, not NEEDS_REVIEW: the surfaces
    are written and reversible. Any other finding (a stale gate, a real FAIL)
    means a genuine review item.
    """
    payload = certification_result.get("payload") if isinstance(certification_result.get("payload"), dict) else {}
    findings = payload.get("findings") if isinstance(payload.get("findings"), list) else []
    if not findings:
        return False
    for finding in findings:
        if not isinstance(finding, dict):
            return False
        component = str(finding.get("component") or "")
        status = str(finding.get("status") or "")
        if component in HOST_PENDING_FINDING_COMPONENTS and status in {"NEEDS_EVIDENCE", "PENDING_HOST_RESTART", "PENDING_TRUST", "HOST_UNOBSERVABLE"}:
            continue
        if component in RELEASE_IDENTITY_FINDING_COMPONENTS:
            continue
        if component in CEILING_READINESS_FINDING_COMPONENTS and status in {"INFO", "NEEDS_EVIDENCE"}:
            continue
        return False
    return True


def certification_findings_are_host_pending_only(findings: list[Any]) -> bool:
    """Like certification_is_host_pending_only, for a summarized cert dict.

    summarize_certification_result() lifts findings to the top level (not under
    a nested payload), which is the shape install/postinstall payloads expose.
    A fresh install's certification legitimately reports NEEDS_REVIEW whose only
    open findings are host-readiness pending (mcp_registration / hook_runtime
    _health NEEDS_EVIDENCE — host not yet restarted / hook not yet fired) or a
    release-identity advisory (release_claim — installed from an unsealed dev
    bundle). Returns True when every finding is one of those non-defect kinds —
    i.e. the install is the ceiling's READY_PENDING_HOST, not a real review item.
    """
    if not isinstance(findings, list) or not findings:
        return False
    for finding in findings:
        if not isinstance(finding, dict):
            return False
        component = str(finding.get("component") or "")
        status = str(finding.get("status") or "")
        if component in HOST_PENDING_FINDING_COMPONENTS and status in {
            "NEEDS_EVIDENCE", "PENDING_HOST_RESTART", "PENDING_TRUST", "HOST_UNOBSERVABLE",
        }:
            continue
        if component in RELEASE_IDENTITY_FINDING_COMPONENTS:
            continue
        if component in CEILING_READINESS_FINDING_COMPONENTS and status in {"INFO", "NEEDS_EVIDENCE"}:
            continue
        return False
    return True


def aggregate_install_status(
    dry_run: bool,
    apply_status: str,
    certification_status: str,
    git_readiness_status: str | None = None,
    certification_host_pending_only: bool = False,
) -> str:
    if dry_run:
        return "DRY-RUN"
    if apply_status == "NEEDS_REVIEW":
        return "NEEDS_REVIEW"
    # Ceiling: a Git-ineligible target with hooks attached must surface NEEDS_GIT
    # in the headline, never an INSTALLED/PASS that hides the field-reports BLOCKED
    # one layer down. NEEDS_GIT is a readiness verdict, not a process failure, so
    # the install stays reversible (exit 0) — it is folded BEFORE the green path.
    if git_readiness_status == "NEEDS_GIT":
        return "NEEDS_GIT"
    if certification_status in {"PASS", "DRY-RUN"}:
        return "INSTALLED"
    # Ceiling: a clean install whose only open certification findings are
    # host-readiness pending (MCP configured but host not yet restarted; hooks
    # configured but not yet fired) is READY_PENDING_HOST — surfaces written,
    # awaiting the host's first (re)spawn to prove them. Exit 0. This is neither a
    # false PASS (nothing host-side is proven yet) nor a NEEDS_REVIEW defect.
    if certification_status in {"NEEDS_REVIEW", "PARTIAL"} and certification_host_pending_only:
        return "READY_PENDING_HOST"
    if certification_status == "PARTIAL":
        return "PARTIAL"
    # The apply succeeded (files written, reversible via uninstall/detach). A
    # post-apply certification verdict of NEEDS_REVIEW or BLOCKED is a review
    # item about the *installed* target — a stale historical gate record, a
    # surface that wants /tes-setup — not a failed install. Degrade it to
    # NEEDS_REVIEW so the bin shows the preserved-and-reversible review notice
    # instead of crashing with "failed". Reserve FAIL for a certification
    # process that actually broke (timeout, crash, unparseable output): that is
    # a real install-process failure the operator must see as an error.
    if certification_status in {"NEEDS_REVIEW", "BLOCKED"}:
        return "NEEDS_REVIEW"
    if certification_status == "FAIL":
        return "FAIL"
    return "NEEDS_REVIEW"


# ADR 0004 capsule-first install. The capsule (.tes/**) is always written.
# Project-visible surfaces are attached only when explicitly requested.
ALL_ATTACH_SURFACES = ("mcp", "docs-mesh", "root-context", "skills", "hooks", "field-reports", "gps", "goals", "mantra")


def resolve_attach(attach: list[str] | None) -> set[str]:
    """Translate the --attach flag into the set of attachment surfaces to write.

    None -> capsule-only (default). 'all' -> capsule plus every project-visible
    surface (legacy install-all). Otherwise capsule plus the named surfaces.
    """
    requested = set(attach or [])
    if "all" in requested:
        return {"capsule", *ALL_ATTACH_SURFACES}
    return {"capsule", *(s for s in requested if s in ALL_ATTACH_SURFACES)}


def uninstall(args: argparse.Namespace) -> int:
    """ADR 0004 SPEC-003: reverse a TES installation and certify zero residue."""
    target = target_root(args.target)
    if not target.exists() or not target.is_dir():
        print(json.dumps({"version": VERSION, "status": "FAIL", "failures": [f"target is not a directory: {target}"]}, indent=2))
        print("[tes-uninstall] FAIL")
        return 1
    blocked = package_source_block(target, "uninstall")
    if blocked:
        print(json.dumps(blocked, indent=2, sort_keys=True))
        print("[tes-uninstall] BLOCKED")
        return 2

    import tes_bundle
    residue_oracle: Any = None
    residue_import_failure: str | None = None
    if not args.dry_run:
        try:
            import capsule_residue_oracle
        except ModuleNotFoundError as exc:
            residue_import_failure = str(exc)
        else:
            residue_oracle = capsule_residue_oracle

    result = tes_bundle.uninstall_capsule(target, dry_run=args.dry_run, yes=args.yes)

    # Fold the residue oracle verdict in (skip on dry-run; nothing was removed).
    residue: dict[str, Any] = {"status": "SKIP", "reason": "dry-run"}
    if not args.dry_run and result.get("status") in {"UNINSTALLED", "NEEDS_REVIEW"}:
        if residue_oracle is None:
            residue = {
                "status": "FAIL",
                "active_residue": [f"capsule_residue_oracle.py unavailable before uninstall: {residue_import_failure}"],
                "surfaces": {},
            }
        else:
            residue = residue_oracle.evaluate(target)
    result["residue"] = residue

    status = str(result.get("status") or "")
    if status == "FAIL":
        verdict = "FAIL"
    elif status == "SKIP":
        verdict = "SKIP"
    elif status == "DRY-RUN":
        verdict = "DRY-RUN"
    elif status == "NEEDS_REVIEW" or residue.get("status") == "FAIL":
        # Either modified files were preserved, or active residue remains.
        verdict = "NEEDS_REVIEW"
        result["status"] = "NEEDS_REVIEW"
    else:
        verdict = "PASS"
        result["status"] = "PASS"

    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-uninstall] " + verdict)
    return 0 if verdict in {"PASS", "DRY-RUN", "SKIP"} else 1


def attach(args: argparse.Namespace) -> int:
    """ADR 0004 SPEC-002: attach one project-visible surface to an installed capsule."""
    target = target_root(args.target)
    if not target.exists() or not target.is_dir():
        print(json.dumps({"version": VERSION, "status": "FAIL", "failures": [f"target is not a directory: {target}"]}, indent=2))
        print("[tes-attach] FAIL")
        return 1
    blocked = package_source_block(target, "attach")
    if blocked:
        print(json.dumps(blocked, indent=2, sort_keys=True))
        print("[tes-attach] BLOCKED")
        return 2
    surface = args.surface
    if surface == "capsule" or surface not in ALL_ATTACH_SURFACES:
        print(json.dumps({"version": VERSION, "status": "FAIL", "failures": [f"attach surface must be one of {', '.join(ALL_ATTACH_SURFACES)}"]}, indent=2))
        print("[tes-attach] FAIL")
        return 1

    import tes_bundle

    # Runtime-writer surfaces (mcp, hooks, docs-mesh) are not bundle-applied; run
    # their writers, then verify via the attach-health oracle (ADR 0004 L3 SPEC-005).
    if surface in {"mcp", "hooks", "docs-mesh", "field-reports"}:
        if surface == "mcp":
            import install_mcp  # type: ignore
            actions, failures = install_mcp.install_configs(
                target, selected_agents(args.agent), args.dry_run, False, True, False,
            )
            writer = {"actions": actions, "failures": failures}
        elif surface == "hooks":
            writer = {"actions": install_hooks(target, selected_agents(args.agent), args.dry_run)}
        elif surface == "field-reports":
            if args.dry_run:
                writer = {"status": "DRY-RUN", "action": "would-install-field-reports-git-hooks"}
            else:
                import field_reports  # type: ignore

                writer = field_reports.install_hook(target)
        else:  # docs-mesh
            if args.dry_run:
                writer = {"status": "DRY-RUN", "action": "would-run-tes-init"}
            else:
                writer = run_helper(target, "tes_init.py", ("--target", "{target}", "--yes"), args.timeout)
        health = {"status": "SKIP", "reason": "dry-run"}
        if surface == "field-reports" and not args.dry_run:
            health = {"status": writer.get("status"), "reason": writer.get("reason")}
        elif not args.dry_run:
            import attach_health_oracle  # type: ignore
            health = attach_health_oracle.evaluate(target, surface)
        health_status = str(health.get("status") or "")
        status = "DRY-RUN" if args.dry_run else (
            "ATTACHED" if health_status in {"PASS", "PENDING_TRUST", "PENDING_HOST_RESTART", "HOST_UNOBSERVABLE"}
            else health_status
        )
        # Ceiling F17: a PENDING_* health verdict must SURFACE in the closeout,
        # not be flattened silently to ATTACHED. The surface is written (ATTACHED)
        # but readiness is pending host trust / a host restart — the operator
        # needs that line, with the reason, to act (trust the server, reopen the
        # host). HOST_UNOBSERVABLE is surfaced too: configured, not yet observed.
        readiness = None
        readiness_line = ""
        if status == "ATTACHED" and health_status in {"PENDING_TRUST", "PENDING_HOST_RESTART", "HOST_UNOBSERVABLE"}:
            reason = str(health.get("reason") or "")
            hint = {
                "PENDING_TRUST": "trust the MCP server in the host, then re-verify",
                "PENDING_HOST_RESTART": "reopen/restart the host so it spawns the server, then re-verify",
                "HOST_UNOBSERVABLE": "configured; the host has not yet been observed running the surface",
            }[health_status]
            readiness = {"status": health_status, "reason": reason, "hint": hint}
            readiness_line = f" ({health_status}: {hint})"
        # Ceiling F27: a successful attach (ATTACHED, including PENDING_* readiness)
        # must transact the install lock so attached_surfaces reflects reality, then
        # recertify so the closeout folds the installed-target verdict.
        lock_txn = None
        certification = None
        if status == "ATTACHED":
            certification = run_installed_certification(target, args.dry_run, args.timeout)
            lock_txn = transact_lock_surface(
                target, surface, attach=True, certification_result=certification, dry_run=args.dry_run
            )
        result = {
            "version": VERSION, "status": status, "target": str(target), "surface": surface,
            "writer": writer, "health": health, "readiness": readiness,
            "lock": lock_txn,
            "certification": summarize_certification_result(certification) if certification else None,
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        print("[tes-attach] " + status + readiness_line)
        return 0 if status in {"ATTACHED", "DRY-RUN"} else 1

    if not tes_bundle.read_staged_manifest(target):
        if tes_bundle.source_package_available():
            stage = tes_bundle.stage_source_bundle(target, adapter=args.agent)
        else:
            stage = tes_bundle.stage_preferred_bundle(target, adapter=args.agent, timeout=args.timeout)
        if stage.get("status") not in {"STAGED", "DRY-RUN"}:
            print(json.dumps({"version": VERSION, "status": "FAIL", "stage": stage, "failures": stage.get("failures", ["bundle stage failed"])}, indent=2))
            print("[tes-attach] FAIL")
            return 1

    apply_result = tes_bundle.apply_staged_bundle(
        target, dry_run=args.dry_run, yes=args.yes, mode="preserve", adapter=args.agent, surfaces={"capsule", surface},
    )
    status = "DRY-RUN" if args.dry_run else ("ATTACHED" if apply_result.get("status") in {"APPLIED", "CLEAN_APPLIED"} else str(apply_result.get("status")))
    # Ceiling F27: transact the lock + recertify on a successful bundle attach too.
    lock_txn = None
    certification = None
    if status == "ATTACHED":
        certification = run_installed_certification(target, args.dry_run, args.timeout)
        lock_txn = transact_lock_surface(
            target, surface, attach=True, certification_result=certification, dry_run=args.dry_run
        )
    result = {
        "version": VERSION, "status": status, "target": str(target), "surface": surface, "apply": apply_result,
        "lock": lock_txn,
        "certification": summarize_certification_result(certification) if certification else None,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-attach] " + status)
    return 0 if status in {"ATTACHED", "DRY-RUN"} else 1


def detach(args: argparse.Namespace) -> int:
    """ADR 0004 SPEC-002: detach one surface, keep the capsule and other surfaces."""
    target = target_root(args.target)
    if not target.exists() or not target.is_dir():
        print(json.dumps({"version": VERSION, "status": "FAIL", "failures": [f"target is not a directory: {target}"]}, indent=2))
        print("[tes-detach] FAIL")
        return 1
    blocked = package_source_block(target, "detach")
    if blocked:
        print(json.dumps(blocked, indent=2, sort_keys=True))
        print("[tes-detach] BLOCKED")
        return 2

    import tes_bundle

    result = tes_bundle.detach_surface(target, args.surface, dry_run=args.dry_run, yes=args.yes)
    status = str(result.get("status") or "")
    verdict = "PASS" if status == "DETACHED" else status
    # Ceiling F27: a successful detach must remove the surface from the lock and
    # recertify, so the lock never claims a surface that was just removed (the
    # capsule is never dropped). Honors --dry-run (no write).
    if status == "DETACHED":
        certification = run_installed_certification(target, args.dry_run, args.timeout)
        result["lock"] = transact_lock_surface(
            target, args.surface, attach=False, certification_result=certification, dry_run=args.dry_run
        )
        result["certification"] = summarize_certification_result(certification)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-detach] " + verdict)
    return 0 if verdict in {"PASS", "DRY-RUN", "SKIP"} else 1


def doctor(args: argparse.Namespace) -> int:
    """ADR 0004 installer model: report capsule health and per-surface attachment
    health separately. Read-only — doctor reports, it never mutates the target.

    This is the diagnostic counterpart to the `/tes-doctor` repair skill: this
    command observes and reports; repair routes stay a separate concern.
    """
    target = target_root(args.target)
    if not target.exists() or not target.is_dir():
        print(json.dumps({"version": VERSION, "status": "FAIL", "failures": [f"target is not a directory: {target}"]}, indent=2))
        print("[tes-doctor] FAIL")
        return 1

    import capsule_residue_oracle  # type: ignore
    import attach_health_oracle  # type: ignore

    capsule_present = bool(capsule_residue_oracle.detect_capsule(target))
    capsule_health = {"status": "PASS" if capsule_present else "NOT_APPLIED", "present": capsule_present}

    # Per-surface attachment health, read-only. Surfaces not materialized report
    # NOT_APPLIED; mcp/hooks carry real PENDING_*/HOST_UNOBSERVABLE evidence.
    attachments: dict[str, Any] = {}
    for surface in attach_health_oracle.SURFACES:
        attachments[surface] = attach_health_oracle.evaluate(target, surface)

    attached = sorted(s for s, h in attachments.items() if str(h.get("status")) not in {"NOT_APPLIED", "FAIL"})
    # Ceiling F28: separate report_status from readiness_status. report_status is
    # the capsule-presence report (a green capsule is genuinely installed). But a
    # green capsule must NOT imply ready: readiness_status folds the WORST
    # materialized attachment health (PENDING_*/HOST_UNOBSERVABLE/DEGRADED/FAIL),
    # so a pending or degraded surface cannot hide inside the per-surface payload
    # behind an unqualified PASS headline.
    report_status = "PASS" if capsule_present else "NOT_INSTALLED"
    materialized = [str(h.get("status") or "") for s, h in attachments.items() if str(h.get("status")) != "NOT_APPLIED"]
    readiness_status = _fold_attachment_readiness(report_status, materialized)
    result = {
        "version": VERSION,
        # status stays the capsule report (back-compat headline / exit contract);
        # readiness_status is the folded worst-attachment readiness verdict.
        "status": report_status,
        "report_status": report_status,
        "readiness_status": readiness_status,
        "target": str(target),
        "capsule": capsule_health,
        "attachments": attachments,
        "attached_surfaces": attached,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    # Surface the readiness verdict on the headline line when it differs from the
    # capsule report, so PENDING_*/DEGRADED is never silent.
    suffix = "" if readiness_status == report_status else f" (readiness: {readiness_status})"
    print("[tes-doctor] " + report_status + suffix)
    return 0


# Worst-wins readiness ladder over materialized attachment health (ceiling F28).
DOCTOR_READINESS_RANK = {
    "PASS": 0,
    "READY_PENDING_HOST": 1,
    "HOST_UNOBSERVABLE": 2,
    "PENDING_TRUST": 3,
    "PENDING_HOST_RESTART": 3,
    "NEEDS_REVIEW": 4,
    "DEGRADED": 5,
    "FAIL": 6,
}


def _fold_attachment_readiness(report_status: str, materialized_statuses: list[str]) -> str:
    """Fold the worst materialized attachment health into a readiness verdict.

    A green capsule with a pending/degraded surface is not ready; the readiness
    verdict reflects the worst surface so nothing hides in the payload.
    """
    if report_status == "NOT_INSTALLED":
        return "NOT_INSTALLED"
    worst = "PASS"
    worst_rank = 0
    for status in materialized_statuses:
        rank = DOCTOR_READINESS_RANK.get(status, 4)  # unknown statuses are review-worthy
        if rank > worst_rank:
            worst_rank = rank
            worst = status
    return worst


def install(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    if not target.exists() or not target.is_dir():
        print("[tes-install] FAIL")
        print(f"- target is not a directory: {target}")
        return 1
    blocked = package_source_block(target, "install")
    if blocked:
        print(json.dumps(blocked, indent=2, sort_keys=True))
        print("[tes-install] BLOCKED")
        return 2
    if not require_confirmation(args, "tes-install"):
        return 1

    agents = selected_agents(args.agent)
    surfaces = resolve_attach(getattr(args, "attach", None))
    attached = sorted(surfaces - {"capsule"})
    legacy_retirement_result = run_legacy_retirement(target, args.dry_run)
    legacy_status = str(legacy_retirement_result.get("status") or "")
    if not args.dry_run and legacy_status in {"FAIL", "NEEDS_REVIEW"}:
        result = {
            "version": VERSION,
            "status": legacy_status,
            "target": str(target),
            "agent": args.agent,
            "agents": agents,
            "legacy_retirement": summarize_legacy_retirement_result(legacy_retirement_result),
            "failures": legacy_retirement_result.get("failures", ["legacy retirement failed"]),
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        print("[tes-install] " + legacy_status)
        return 1 if legacy_status == "FAIL" else 0
    stage: dict[str, Any]
    apply_result: dict[str, Any]
    if args.dry_run:
        stage = {
            "version": VERSION,
            "status": "DRY-RUN",
            "action": "would-stage-bundle",
            "stage_dir": rel(target / ".tes/setup" / VERSION, target),
        }
        apply_result = {
            "version": VERSION,
            "status": "DRY-RUN",
            "action": "would-apply-runtime-capabilities",
            "mode": args.mode,
        }
    else:
        import tes_bundle

        if args.bundle:
            stage = tes_bundle.stage_bundle(args.bundle, target)
        elif args.url:
            stage = tes_bundle.stage_public_bundle(
                target,
                url=args.url,
                expected_sha256=args.sha256,
                timeout=args.timeout,
            )
        elif not (source_root() / ".git").exists():
            stage = tes_bundle.stage_preferred_bundle(target, adapter=args.agent, timeout=args.timeout)
        elif tes_bundle.source_package_available():
            stage = tes_bundle.stage_source_bundle(target, adapter=args.agent)
        else:
            stage = tes_bundle.stage_preferred_bundle(target, adapter=args.agent, timeout=args.timeout)
        if stage.get("status") not in {"STAGED", "DRY-RUN"}:
            result = {
                "version": VERSION,
                "status": "FAIL",
                "stage": stage,
                "legacy_retirement": summarize_legacy_retirement_result(legacy_retirement_result),
                "failures": stage.get("failures", ["bundle stage failed"]),
            }
            print(json.dumps(result, indent=2, sort_keys=True))
            print("[tes-install] FAIL")
            return 1
        apply_result = tes_bundle.apply_staged_bundle(
            target,
            yes=True,
            mode=args.mode,
            adapter=args.agent,
            surfaces=surfaces,
        )
        if apply_result.get("status") not in {"APPLIED", "CLEAN_APPLIED", "DRY-RUN", "NEEDS_REVIEW"}:
            result = {
                "version": VERSION,
                "status": "FAIL",
                "stage": stage,
                "legacy_retirement": summarize_legacy_retirement_result(legacy_retirement_result),
                "apply": apply_result,
                "failures": apply_result.get("failures", ["bundle apply failed"]),
            }
            print(json.dumps(result, indent=2, sort_keys=True))
            print("[tes-install] FAIL")
            return 1

    # ADR 0004: hooks and MCP are project-visible attachments. Capsule-only
    # install leaves them off. --no-hooks still forces hooks off when attached.
    hooks_attached = "hooks" in surfaces
    mcp_attached = "mcp" in surfaces
    mcp_result = (
        run_mcp_bootstrap(target, args.agent, args.dry_run, args.timeout)
        if mcp_attached
        else {"status": "SKIP", "reason": "capsule-only: mcp not attached", "surface": "mcp"}
    )
    hook_actions = (
        install_hooks(target, agents, args.dry_run)
        if hooks_attached and not args.no_hooks
        else [{"action": "skip-capsule-only" if not hooks_attached else "skip-disabled", "surface": "hooks"}]
    )
    field_reports_result: dict[str, Any] = (
        {"status": "SKIP", "reason": "field-reports not attached", "surface": "field-reports"}
        if "field-reports" not in surfaces or args.dry_run
        else __import__("field_reports").install_hook(target)
    )
    if mcp_result.get("status") == "FAIL":
        result = {
            "version": VERSION,
            "status": "FAIL",
            "target": str(target),
            "agent": args.agent,
            "agents": agents,
            "mode": args.mode,
            "stage": summarize_result(stage),
            "legacy_retirement": summarize_legacy_retirement_result(legacy_retirement_result),
            "apply": summarize_result(apply_result),
            "hooks": hook_actions,
            "mcp": summarize_mcp_result(mcp_result),
            "failures": mcp_result.get("failures", ["MCP bootstrap failed"]),
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        print("[tes-install] FAIL")
        return 1
    # Installed certification reads the installed lock, so write the reference
    # once before certification and overwrite it with the final summary below.
    pending_certification_result = {"status": "PENDING", "payload": {}, "failures": []}
    write_install_lock(
        target,
        args.agent,
        agents,
        args.mode,
        stage,
        legacy_retirement_result,
        apply_result,
        hook_actions,
        mcp_result,
        pending_certification_result,
        args.dry_run,
        sorted(surfaces),
    )
    certification_result = run_installed_certification(target, args.dry_run, args.timeout)
    # The first-session post-install sentinel (.tes/postinstall.json) is what the
    # installed SessionStart hook reads to announce setup and trigger first-run
    # work. It must be written whenever the hook surface is attached — otherwise
    # the hook fires into an empty state and does nothing. It is gated on `hooks`,
    # not on docs-mesh: the sentinel records install state for the hook; it does
    # not by itself materialize docs/agents (that stays the docs-mesh attachment).
    postinstall_disabled = args.no_postinstall or "hooks" not in surfaces
    # Ceiling (F5/F9 → READY_PENDING_HOST): a host-pending-only certification
    # (MCP configured/host not restarted; hooks configured/not fired; unsealed dev
    # bundle) is NOT a review item — it is expected readiness awaiting the first
    # host run. The pending sentinel is precisely what that first hook picks up to
    # run postinstall and prove the host, so host-pending-only must keep writing a
    # PENDING sentinel, not a review sentinel. Only a real defect (a non-host-
    # pending cert review, or an apply NEEDS_REVIEW) writes a review sentinel.
    cert_needs_review = (
        certification_status_rank(str(certification_result.get("status") or "")) >= certification_status_rank("NEEDS_REVIEW")
        and not certification_is_host_pending_only(certification_result)
    )
    sentinel_action = (
        {"path": rel(target / POSTINSTALL_PATH, target), "action": "skip-capsule-only" if not args.no_postinstall else "skip-disabled"}
        if postinstall_disabled
        else (
            write_review_sentinel(target, args.agent, agents, args.postinstall_mode, apply_result, args.dry_run, certification_result)
            if apply_result.get("status") == "NEEDS_REVIEW" or cert_needs_review
            else write_pending_sentinel(target, args.agent, agents, args.postinstall_mode, args.dry_run)
        )
    )
    lock_action = write_install_lock(
        target,
        args.agent,
        agents,
        args.mode,
        stage,
        legacy_retirement_result,
        apply_result,
        hook_actions,
        mcp_result,
        certification_result,
        args.dry_run,
        sorted(surfaces),
    )
    readiness = git_readiness(target, hooks_attached and not args.dry_run)
    host_pending_only = certification_is_host_pending_only(certification_result)
    status = aggregate_install_status(
        args.dry_run,
        str(apply_result.get("status") or ""),
        str(certification_result.get("status") or ""),
        str(readiness.get("status") or ""),
        host_pending_only,
    )
    result = {
        "version": VERSION,
        "status": status,
        "target": str(target),
        "agent": args.agent,
        "agents": agents,
        "mode": args.mode,
        # Typed Git readiness in the headline payload: when hooks are attached but
        # the target is not a Git work tree, status is NEEDS_GIT, never a green
        # that hides the field-reports BLOCKED one layer down.
        "git_readiness": readiness,
        # Project-visible surfaces actually materialized this run (capsule is the
        # always-present runtime authority, not a project-visible attachment).
        # The bin renderer reads this to describe the install truthfully instead
        # of inferring materialization from the docs-mesh postinstall sentinel.
        "attached_surfaces": sorted(surfaces - {"capsule"}),
        "stage": summarize_result(stage),
        "legacy_retirement": summarize_legacy_retirement_result(legacy_retirement_result),
        "apply": summarize_result(apply_result),
        "hooks": hook_actions,
        "field_reports": summarize_result(field_reports_result),
        "mcp": summarize_mcp_result(mcp_result),
        "certification": summarize_certification_result(certification_result),
        "postinstall": sentinel_action,
        "lock": lock_action,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-install] " + result["status"])
    # Only a broken certification *process* (FAIL) is a non-zero install. A
    # successful apply with a post-install review verdict aggregates to
    # NEEDS_REVIEW (exit 0); a Git-ineligible target with hooks attached
    # aggregates to NEEDS_GIT (exit 0) — both are readiness verdicts on a
    # reversible on-disk install, not process failures. The bin renders the
    # preserved-review / pending-Git notice. aggregate yields BLOCKED never.
    return 1 if status == "FAIL" else 0


def parse_hook_input() -> dict[str, Any]:
    if sys.stdin is None or sys.stdin.closed:
        return {}
    try:
        if sys.stdin.isatty():
            return {}
        if not sys.stdin.readable():
            return {}
        import select

        if select.select([sys.stdin], [], [], 0)[0]:
            raw = sys.stdin.read()
        else:
            return {}
    except (OSError, ValueError):
        return {}
    else:
        if not raw.strip():
            return {}
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}


def helper_path(target: Path, script_name: str) -> Path:
    installed = target / ".tes/bin" / script_name
    if installed.exists():
        return installed
    package = source_root() / "scripts" / script_name
    return package


def run_helper(target: Path, script_name: str, args: tuple[str, ...], timeout: float) -> dict[str, Any]:
    script = helper_path(target, script_name)
    expanded = [str(target) if item == "{target}" else item for item in args]
    command = [sys.executable, str(script), *expanded]
    try:
        result = subprocess.run(
            command,
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "command": " ".join(command),
            "returncode": 124,
            "status": "BLOCKED",
            "stdout": stdout.strip(),
            "stderr": (stderr.strip() + f"\ncommand timed out after {timeout:g}s").strip(),
        }
    payload = parse_json_output(result.stdout)
    failures = payload.get("failures") if isinstance(payload.get("failures"), list) else []
    command_result = {
        "command": " ".join(command),
        "returncode": result.returncode,
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        # Keep the parsed payload so downstream consumers (advisory collection)
        # can read inner gate signals without re-parsing or re-running helpers.
        "payload": payload,
    }
    if result.returncode != 0 and failures:
        command_result["oracle_failures"] = [str(item) for item in failures if item]
    return command_result


def append_run_record(target: Path, payload: dict[str, Any], dry_run: bool) -> dict[str, str]:
    path = unique_postinstall_run_path(target, str(payload["agent"]))
    action = write_json(path, payload, dry_run=dry_run)
    run_rel = rel(path, target)
    index = postinstall_run_index(target, run_rel, dry_run)
    return {**action, "path": str(path), "run_index": str(index["path"]), "total_runs": str(index["total_runs"])}


def postinstall(args: argparse.Namespace, hook_input: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    target = target_root(args.target)
    blocked = package_source_block(target, "postinstall")
    if blocked:
        return 2, blocked
    sentinel_path = target / POSTINSTALL_PATH
    sentinel = read_json(sentinel_path)
    state = str(sentinel.get("state") or "")
    recover_needs_review = bool(getattr(args, "recover_needs_review", False))
    rerun_requested = bool(args.force or recover_needs_review)
    if recover_needs_review and state != "needs_review":
        result = {
            "version": VERSION,
            "status": "SKIP",
            "reason": "postinstall recovery only runs when the sentinel is needs_review",
            "target": str(target),
            "state": state or "missing",
        }
        return 0, result
    if state not in POSTINSTALL_STATES and not rerun_requested:
        result = {"version": VERSION, "status": "SKIP", "reason": "no postinstall sentinel", "target": str(target)}
        return 0, result
    if state == "complete" and not rerun_requested:
        result = {"version": VERSION, "status": "SKIP", "reason": "postinstall already complete", "target": str(target)}
        return 0, result
    if state == "needs_review" and not rerun_requested:
        result = {
            "version": VERSION,
            "status": "NEEDS_REVIEW",
            "reason": "previous postinstall needs review",
            "target": str(target),
            "recovery": "run /tes-init, repair reported blockers, then rerun postinstall recovery",
        }
        return 0, result
    if state == "running" and not rerun_requested:
        result = {"version": VERSION, "status": "RUNNING", "reason": "postinstall already running", "target": str(target)}
        return 0, result
    if args.dry_run:
        action = "would-run-postinstall-recovery" if recover_needs_review else "would-run-postinstall"
        result = {"version": VERSION, "status": "DRY-RUN", "target": str(target), "actions": [action]}
        return 0, result

    running = {
        **sentinel_payload(args.agent, selected_agents(args.agent) if args.agent != "all" else list(AGENTS), args.mode, sentinel),
        "state": "running",
        "updated_at": utc_stamp(),
        "requested_by": str(sentinel.get("requested_by") or args.agent),
        "executed_by": args.agent,
    }
    if recover_needs_review:
        running["recovery"] = "needs_review"
    write_json(sentinel_path, running)
    commands = [] if args.skip_project_init else list(DEFAULT_POSTINSTALL_COMMANDS)
    results = [run_helper(target, script, script_args, args.timeout) for script, script_args in commands]
    mcp_result = run_mcp_bootstrap(target, args.agent, False, args.timeout)
    results.extend(
        {
            "command": command["command"],
            "returncode": command["returncode"],
            "status": command["status"],
            "stdout": "",
            "stderr": "\n".join(mcp_result.get("failures", [])) if command["returncode"] != 0 else "",
        }
        for command in mcp_result.get("commands", [])
    )
    certification_result = run_installed_certification(target, False, args.timeout)
    certification_command = {
        "command": certification_result["command"],
        "returncode": certification_result["returncode"],
        "status": certification_result["status"],
        "stdout": "",
        "stderr": "\n".join(certification_result.get("failures", [])),
    }
    results.append(certification_command)
    certification_status = str(certification_result.get("status") or "NEEDS_REVIEW")
    # Ceiling: a certification whose only open findings are host-readiness pending
    # (MCP configured/host not restarted; hooks configured/not yet fired) is a
    # terminal READY_PENDING_HOST success at postinstall, not a review item — the
    # surfaces are written and only the host's first (re)spawn remains. Any other
    # non-PASS certification stays a genuine review.
    host_pending_only = certification_is_host_pending_only(certification_result)
    # The certification CLI exits non-zero for a host-pending NEEDS_REVIEW (that
    # is correct for the standalone oracle — it is not a clean PASS). But at the
    # postinstall layer a host-pending-only certification is READY_PENDING_HOST,
    # not a failure, so its non-zero exit must NOT count toward `failed` — else it
    # would force NEEDS_REVIEW and mask the ceiling tier. Exclude exactly the
    # certification command when it is host-pending-only; every other non-zero
    # command (a real broken gate) still counts.
    failed = [
        item
        for item in results
        if item["returncode"] != 0 and not (item is certification_command and host_pending_only)
    ]
    if certification_status in {"PASS", "DRY-RUN"}:
        needs_cert_review = False
    elif host_pending_only:
        needs_cert_review = False
    else:
        needs_cert_review = True
    final_state = "needs_review" if failed or needs_cert_review else "complete"
    if failed:
        status = "NEEDS_REVIEW"
    elif needs_cert_review:
        status = certification_status
    elif host_pending_only and certification_status not in {"PASS", "DRY-RUN"}:
        status = "READY_PENDING_HOST"
    else:
        status = "PASS"
    advisory_stamp = utc_stamp()
    advisories = collect_advisories(results, derived_at=advisory_stamp) if status == "PASS" else []
    run_payload = {
        "schema": "tes-postinstall-run@1",
        "version": VERSION,
        "agent": args.agent,
        "target": str(target),
        "started_at": running["updated_at"],
        "completed_at": utc_stamp(),
        "status": status,
        # The parsed gate payload is consumed in-memory by collect_advisories;
        # it must not bloat the persisted run record (drop it from each command).
        "commands": [{k: v for k, v in item.items() if k != "payload"} for item in results],
        "mcp": summarize_mcp_result(mcp_result),
        "certification": summarize_certification_result(certification_result),
        "hook_input_keys": sorted((hook_input or {}).keys()),
    }
    if recover_needs_review:
        run_payload["recovery"] = "needs_review"
    run_record = append_run_record(target, run_payload, dry_run=False)
    run_record_rel = rel(Path(run_record["path"]), target)
    runs = running.get("runs") if isinstance(running.get("runs"), list) else []
    sentinel_runs = bounded_sentinel_runs([*runs, run_record_rel])
    total_runs = int(str(run_record.get("total_runs") or len(sentinel_runs)))
    complete_payload = {
        **running,
        "state": final_state,
        "updated_at": utc_stamp(),
        "completed_at": utc_stamp() if final_state == "complete" else None,
        "last_status": status,
        "last_run": run_record_rel,
        "runs": sentinel_runs,
        "run_index": run_record.get("run_index"),
        "run_count": total_runs,
        "retained_run_count": len(sentinel_runs),
        "archived_run_count": max(0, total_runs - len(sentinel_runs)),
    }
    if failed or needs_cert_review:
        complete_payload["failures"] = [
            {
                "command": item["command"],
                "returncode": item["returncode"],
                "stderr": item["stderr"][:1000],
                **({"oracle_failures": item["oracle_failures"][:8]} if item.get("oracle_failures") else {}),
            }
            for item in failed
        ]
        if needs_cert_review:
            complete_payload["failures"].append(
                {
                    "command": certification_result["command"],
                    "returncode": certification_result["returncode"],
                    "stderr": json.dumps(summarize_certification_result(certification_result), sort_keys=True)[:1000],
                }
            )
    else:
        complete_payload.pop("failures", None)
    if advisories:
        complete_payload["advisories"] = advisories
    else:
        complete_payload.pop("advisories", None)
    # Record when advisories were last derived (Gap 3). On a PASS run this is the
    # current-state proof: an empty advisory list with a fresh advisories_derived_at
    # is positive evidence that scaffold-era advisories (mesh.scaffold_only) were
    # re-evaluated against the aligned mesh and cleared — not merely missing.
    if status == "PASS":
        complete_payload["advisories_derived_at"] = advisory_stamp
    else:
        complete_payload.pop("advisories_derived_at", None)
    write_json(sentinel_path, complete_payload)
    result = {
        "version": VERSION,
        "status": status,
        "target": str(target),
        "agent": args.agent,
        "state": final_state,
        "run_record": run_record_rel,
        "commands": [{"command": item["command"], "status": item["status"], "returncode": item["returncode"]} for item in results],
        "mcp": summarize_mcp_result(mcp_result),
        "certification": summarize_certification_result(certification_result),
    }
    if advisories:
        result["advisories"] = advisories
    if recover_needs_review:
        result["recovery"] = "needs_review"
    return (0 if not failed and not needs_cert_review else 1), result


def _tes_init_payload(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Return the parsed payload of the tes_init.py gate, or {} when absent."""
    for item in results:
        if isinstance(item, dict) and "tes_init.py" in str(item.get("command") or ""):
            payload = item.get("payload")
            return payload if isinstance(payload, dict) else {}
    return {}


def _gate_stdout_json(payload: dict[str, Any], needle: str) -> dict[str, Any]:
    """Parse the JSON stdout of an inner gate whose command contains `needle`."""
    gates = payload.get("gates")
    if not isinstance(gates, list):
        return {}
    for gate in gates:
        if isinstance(gate, dict) and needle in str(gate.get("command") or ""):
            stdout = gate.get("stdout")
            if isinstance(stdout, str) and stdout:
                return parse_json_output(stdout)
            inner = gate.get("payload")
            if isinstance(inner, dict):
                return inner
    return {}


def collect_advisories(
    results: list[dict[str, Any]], *, derived_at: str | None = None
) -> list[dict[str, str]]:
    """Derive post-PASS advisories from the tes_init payload already in `results`.

    Advisories are non-blocking nudges (GAP-1/2/4/5). They never change status;
    each rule is isolated so a malformed payload degrades to fewer advisories
    rather than raising and breaking the hook.

    Each advisory is scoped to the run that produced it via `derived_at`, so a
    historical scaffold-era advisory can never be read as current-state evidence
    (Gap 3). The whole list is re-derived from THIS run's alignment oracle, so a
    target that has since transitioned scaffold -> aligned drops mesh.scaffold_only
    rather than carrying it forward.
    """
    advisories: list[dict[str, str]] = []
    payload = _tes_init_payload(results)
    if not payload:
        return advisories

    # GAP-1 + GAP-2: alignment oracle stdout (freshness drift, scaffold-only mesh).
    try:
        alignment = _gate_stdout_json(payload, "project_alignment_oracle.py")
        freshness = alignment.get("freshness") if isinstance(alignment.get("freshness"), dict) else {}
        notes = freshness.get("notes") if isinstance(freshness.get("notes"), list) else []
        if any(str(note).startswith("newest ADR") for note in notes):
            advisories.append(
                {
                    "code": "freshness.adr_drift",
                    "message": "O ADR mais recente introduz termos ausentes do mesh ativo — rode /tes-align para reconciliar.",
                }
            )
        if freshness.get("mesh_scaffold_only") is True:
            advisories.append(
                {
                    "code": "mesh.scaffold_only",
                    "message": "O mesh é apenas scaffold inicial — rode /tes-align para refinamento semântico.",
                }
            )
    except Exception:
        pass

    # GAP-4: empty Cortex. Target the audit gate specifically — `cortex.py verify`
    # runs first and carries no cell_count; only `cortex.py audit` does.
    try:
        audit = _gate_stdout_json(payload, "cortex.py audit")
        if audit.get("cell_count") == 0:
            advisories.append(
                {
                    "code": "cortex.empty",
                    "message": "Cortex vazio — capacidade de memória durável não está sendo usada.",
                }
            )
    except Exception:
        pass

    # GAP-5: field-reports outbox backlog over threshold.
    try:
        fr = _gate_stdout_json(payload, "field_reports.py")
        pending_advisory = fr.get("pending_advisory")
        if isinstance(pending_advisory, str) and pending_advisory:
            advisories.append({"code": "field_reports.pending_high", "message": pending_advisory})
    except Exception:
        pass

    # Scope every advisory to the producing run so a stale advisory can never be
    # presented as current-state evidence (Gap 3 truthfulness).
    if derived_at:
        for advisory in advisories:
            advisory["derived_at"] = derived_at

    return advisories


def claude_postinstall_context(result: dict[str, Any], hook_input: dict[str, Any]) -> str:
    status = str(result.get("status") or "UNKNOWN")
    target = str(result.get("target") or "unknown target")
    source = str(hook_input.get("source") or "manual")
    version = str(result.get("version") or VERSION)
    lines = [
        f"TES SessionStart hook ran for source `{source}`.",
        f"Target: {target}",
        f"TES version: {version}",
        f"Status: {status}",
    ]
    reason = result.get("reason")
    if reason:
        lines.append(f"Reason: {reason}")
    state = result.get("state")
    if state:
        lines.append(f"Postinstall state: {state}")
    run_record = result.get("run_record")
    if run_record:
        lines.append(f"Run record: {run_record}")
    commands = result.get("commands")
    if isinstance(commands, list) and commands:
        passed = sum(1 for item in commands if isinstance(item, dict) and item.get("status") == "PASS")
        lines.append(f"Postinstall gates: {passed}/{len(commands)} PASS")
    if status == "PASS":
        lines.append("Project context and alignment setup completed before the first prompt.")
        lines.append(
            "If the user immediately asks `/tes-init`, summarize this completed run from "
            "`.tes/postinstall.json` and the run record unless they explicitly request recertification."
        )
        advisories = result.get("advisories")
        if isinstance(advisories, list):
            for advisory in advisories:
                if isinstance(advisory, dict) and advisory.get("message"):
                    lines.append(f"Advisory: {advisory['message']}")
    elif status == "RUNNING":
        lines.append("TES setup was already running before this hook returned.")
        lines.append("Ask the user to wait a moment, then run `/tes-setup` for the setup report.")
    elif status == "SKIP":
        lines.append("Postinstall did not run again because no pending work was required.")
    else:
        lines.append("TES postinstall needs review. Use `/tes-init` to inspect and recover before claiming GO.")
    cortex = result.get("cortex") if isinstance(result.get("cortex"), dict) else {}
    cortex_context = cortex.get("additional_context")
    if isinstance(cortex_context, str) and cortex_context:
        lines.append(cortex_context)
    return "\n".join(lines)


def hook_event_name(hook_input: dict[str, Any], default: str = "SessionStart") -> str:
    return kernel_hook_event_name(hook_input, default)


def hook_tool_name(hook_input: dict[str, Any]) -> str:
    return kernel_hook_tool_name(hook_input)


def hook_tool_input(hook_input: dict[str, Any]) -> dict[str, Any]:
    return kernel_hook_tool_input(hook_input)


def hook_tool_path(hook_input: dict[str, Any], tool_input: dict[str, Any]) -> str:
    return kernel_hook_tool_path(hook_input, tool_input)


def hook_patch_paths(command: str) -> list[str]:
    return kernel_hook_patch_paths(command)


def hook_tool_command(hook_input: dict[str, Any], tool_input: dict[str, Any]) -> str:
    return kernel_hook_tool_command(hook_input, tool_input)


def hook_command_category(command: str) -> str:
    """Return a redaction-safe command class for PreToolUse ledger rows."""
    normalized = " ".join(command.strip().lower().split())
    if not normalized:
        return "no_command"
    if hook_patch_paths(command):
        return "patch_body"
    if "push --force" in normalized or "--force-with-lease" in normalized:
        return "forbidden_git_force_push"
    if "git push" in normalized and (" --force" in normalized or " -f" in normalized):
        return "forbidden_git_force_push"
    if "--no-preserve-root" in normalized or "rm -rf /" in normalized or "rm -fr /" in normalized:
        return "forbidden_root_wipe"
    return "shell_command"


def hook_reason_codes(*values: Any) -> list[str]:
    """Normalize kernel/session reason codes before writing runtime evidence."""
    reason_codes: list[str] = []
    for value in values:
        if isinstance(value, str):
            items: tuple[Any, ...] = (value,)
        elif isinstance(value, (list, tuple, set)):
            items = tuple(value)
        else:
            continue
        for item in items:
            code = str(item)
            if code and code not in reason_codes:
                reason_codes.append(code)
    return reason_codes


def pretooluse_renderer_trace(agent: str, *, block: bool, context: str = "", cortex_context: str = "") -> dict[str, str]:
    """Name the host renderer contract without duplicating rendered output."""
    if block:
        output_contract = "json_permission_deny" if agent == "cursor" else "exit_2_stderr_block"
    elif context or cortex_context:
        if agent == "cursor":
            if context and cortex_context:
                output_contract = "json_permission_allow_user_agent_message"
            elif context:
                output_contract = "json_permission_allow_user_message"
            else:
                output_contract = "json_permission_allow_agent_message"
        elif agent == "claude":
            output_contract = "json_hookSpecificOutput_allow"
        else:
            output_contract = "stderr_context"
    else:
        output_contract = "json_permission_allow_silent" if agent == "cursor" else "silent_allow"
    return {"renderer": f"{agent}_pretooluse", "output_contract": output_contract}


def claude_hook_output(result: dict[str, Any], hook_input: dict[str, Any]) -> dict[str, Any]:
    event_name = hook_event_name(hook_input)
    output: dict[str, Any] = {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": claude_postinstall_context(result, hook_input),
        }
    }
    # Ceiling: READY_PENDING_HOST is a terminal SUCCESS — surfaces written,
    # reversible, awaiting only the host's first (re)spawn to prove MCP/hooks. It
    # routes to the completed message (not "needs review").
    if result.get("status") in {"PASS", "READY_PENDING_HOST"}:
        output["systemMessage"] = "TES first-session setup completed. Please, run /tes-setup for the report."
    elif result.get("status") == "RUNNING":
        output["systemMessage"] = "TES first-session setup is still running. Please wait, then run /tes-setup."
    elif result.get("status") not in {"SKIP", "DRY-RUN"}:
        output["systemMessage"] = "TES first-session setup needs review. Run /tes-init for recovery."
    return output


def claude_start_notice_output(target: Path, hook_input: dict[str, Any]) -> dict[str, Any]:
    event_name = hook_event_name(hook_input)
    sentinel = read_json(target / POSTINSTALL_PATH)
    state = str(sentinel.get("state") or "")
    if state in {"pending", "running"}:
        return {
            "systemMessage": CLAUDE_SETUP_RUNNING_MESSAGE,
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": (
                    "TES first-session setup is starting. Do not begin project work or "
                    "run duplicate setup while the completion notice is pending."
                ),
            },
        }
    if state == "needs_review":
        return {
            "systemMessage": "TES first-session setup needs review. Run /tes-init for recovery.",
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": "TES postinstall is marked needs_review. Inspect `.tes/postinstall.json` before project work.",
            },
        }
    return {}


def claude_rewake_message(result: dict[str, Any]) -> str:
    status = str(result.get("status") or "UNKNOWN")
    # Ceiling: READY_PENDING_HOST is a terminal success (surfaces written,
    # awaiting the host's first restart to prove MCP/hooks), so it wakes with the
    # completed message — not the needs-review path.
    if status in {"PASS", "READY_PENDING_HOST"}:
        return "TES first-session setup completed.\nTell the user: " + CLAUDE_SETUP_COMPLETED_MESSAGE
    if status == "RUNNING":
        return (
            "TES first-session setup is still running.\n"
            "Tell the user: please wait for TES setup to complete."
        )
    if status not in {"SKIP", "DRY-RUN"}:
        return (
            "TES first-session setup needs review.\n"
            f"Status: {status}.\n"
            "Tell the user: TES setup needs review. Run /tes-init for recovery "
            "before starting project work."
        )
    return ""


HOOK_SENTINEL_PATH = Path(".tes/runtime/hooks/executed.jsonl")
LEGACY_HOOK_SENTINEL_PATH = Path(".tes/hooks/executed.jsonl")
HOOK_RUNTIME_EXCLUDE_COMMENT = "# TES runtime hook ledgers"
HOOK_RUNTIME_EXCLUDE_PATTERNS = (".tes/runtime/", ".tes/hooks/executed.jsonl")
HOOK_HEALTH_CONTRACTS: dict[str, tuple[dict[str, str], ...]] = {
    "codex": (
        {"event": "SessionStart", "event_canonical": "SessionStart", "config": ".codex/config.toml"},
        {"event": "PreToolUse", "event_canonical": "PreToolUse", "config": ".codex/config.toml"},
    ),
    "claude": (
        {"event": "SessionStart", "event_canonical": "SessionStart", "config": ".claude/settings.json"},
        {"event": "PreToolUse", "event_canonical": "PreToolUse", "config": ".claude/settings.json"},
    ),
    "cursor": (
        {"event": "sessionStart", "event_canonical": "sessionStart", "config": ".cursor/hooks.json"},
        {"event": "beforeSubmitPrompt", "event_canonical": "beforeSubmitPrompt", "config": ".cursor/hooks.json"},
        {"event": "preToolUse", "event_canonical": "PreToolUse", "config": ".cursor/hooks.json"},
    ),
}


def canonical_hook_event(event: str) -> str:
    return "PreToolUse" if event in {"PreToolUse", "preToolUse"} else event


def _git_info_exclude_path(target: Path) -> Path | None:
    git = target / ".git"
    if git.is_dir():
        return git / "info" / "exclude"
    if git.is_file():
        try:
            text = git.read_text(encoding="utf-8", errors="ignore").strip()
        except OSError:
            return None
        if not text.startswith("gitdir:"):
            return None
        raw = text.split(":", 1)[1].strip()
        git_dir = Path(raw)
        if not git_dir.is_absolute():
            git_dir = (target / git_dir).resolve()
        return git_dir / "info" / "exclude"
    return None


def ensure_hook_runtime_excluded(target: Path) -> None:
    exclude = _git_info_exclude_path(target)
    if exclude is None:
        return
    try:
        existing = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
        lines = {line.strip() for line in existing.splitlines()}
        missing = [pattern for pattern in HOOK_RUNTIME_EXCLUDE_PATTERNS if pattern not in lines]
        if not missing:
            return
        exclude.parent.mkdir(parents=True, exist_ok=True)
        prefix = "" if not existing or existing.endswith("\n") else "\n"
        comment = "" if HOOK_RUNTIME_EXCLUDE_COMMENT in existing else HOOK_RUNTIME_EXCLUDE_COMMENT + "\n"
        with exclude.open("a", encoding="utf-8") as handle:
            handle.write(prefix + comment + "\n".join(missing) + "\n")
    except OSError:
        return


def record_hook_execution(
    target: Path,
    agent: str,
    hook_input: dict[str, Any],
    *,
    mode: str,
    pretooluse_decision: dict[str, Any] | None = None,
) -> None:
    """ADR 0004 SPEC-005: prove the hook actually fired.

    Append a capsule-scoped sentinel record on every real hook invocation. The
    attach-health oracle reads this to certify a hook fired (vs config-written
    only) and to detect duplicate handlers per (agent, event, session). Best
    effort: a sentinel write must never break the hook itself.
    """
    try:
        event = hook_event_name(hook_input)
        event_canonical = canonical_hook_event(event)
        session = str(hook_input.get("session_id") or hook_input.get("sessionId") or os.getpid())
        ensure_hook_runtime_excluded(target)
        sentinel = target / HOOK_SENTINEL_PATH
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "agent": agent,
            "event": event,
            "event_canonical": event_canonical,
            "mode": mode,
            "session": session,
            "ts": utc_stamp(),
            # Ceiling F18: a record written by a real in-host hook invocation is
            # tagged host-real provenance. Only host-real evidence may authorize a
            # native PASS_CEILING claim; fixture/seeded rows (which carry no such
            # tag, or an explicit "fixture") can never read as native execution.
            "provenance": "host-real",
        }
        if event_canonical == "PreToolUse":
            tool_input = hook_tool_input(hook_input)
            tool = hook_tool_name(hook_input)
            path = hook_tool_path(hook_input, tool_input)
            command = hook_tool_command(hook_input, tool_input)
            invocation = hook_input.get("tool_use_id") or hook_input.get("toolUseId")
            record["schema_version"] = PRETOOLUSE_LEDGER_SCHEMA_VERSION
            record["command_category"] = hook_command_category(command)
            record["command_redacted"] = bool(command)
            if tool:
                record["tool"] = tool
            if path:
                record["path"] = path
            if invocation:
                record["invocation"] = str(invocation)
            if pretooluse_decision:
                reason_codes = hook_reason_codes(pretooluse_decision.get("reason_codes"))
                if reason_codes:
                    record["reason_codes"] = reason_codes
                for key in (
                    "raw_tool_label",
                    "normalized_tool",
                    "payload_source",
                    "classifier_trace",
                    "renderer_trace",
                    "risk",
                    "outcome",
                    "block",
                    "decision",
                    "permission_decision",
                    "marker_emitted",
                    "context_suppressed",
                    "cortex_context_emitted",
                    "surface_context",
                ):
                    if key in pretooluse_decision:
                        record[key] = pretooluse_decision[key]
            if not record.get("invocation"):
                record["invocation"] = pretooluse_synthetic_invocation(record)
        if not hook_record_already_written(sentinel, record):
            with sentinel.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        pass


def pretooluse_synthetic_invocation(record: dict[str, Any]) -> str:
    """Create a privacy-preserving invocation id when a host omits tool ids."""
    parts = {
        "agent": record.get("agent"),
        "event": record.get("event_canonical"),
        "mode": record.get("mode"),
        "session": record.get("session"),
        "tool": record.get("tool"),
        "path": record.get("path"),
        "command_category": record.get("command_category"),
        "risk": record.get("risk"),
        "outcome": record.get("outcome"),
        "decision": record.get("decision"),
        "permission_decision": record.get("permission_decision"),
        "marker_emitted": record.get("marker_emitted"),
        "context_suppressed": record.get("context_suppressed"),
    }
    digest = hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]
    agent = str(record.get("agent") or "agent")
    session = str(record.get("session") or "session")
    tool = str(record.get("tool") or "tool")
    return f"synthetic:{agent}:{session}:{tool}:{digest}"


HOOK_RECORD_DEDUPE_FIELDS = (
    "schema_version",
    "agent",
    "event_canonical",
    "mode",
    "session",
    "tool",
    "path",
    "command_category",
    "command_redacted",
    "invocation",
    "raw_tool_label",
    "normalized_tool",
    "payload_source",
    "classifier_trace",
    "renderer_trace",
    "risk",
    "outcome",
    "reason_codes",
    "block",
    "decision",
    "permission_decision",
    "marker_emitted",
    "context_suppressed",
    "cortex_context_emitted",
    "surface_context",
)
PRETOOLUSE_CONTRADICTION_FIELDS = (
    "decision",
    "permission_decision",
    "risk",
    "renderer_output_contract",
    "command_redacted",
    "marker_contract",
)


def hook_record_dedupe_value(value: Any) -> Any:
    if isinstance(value, list | tuple):
        return tuple(hook_record_dedupe_value(item) for item in value)
    if isinstance(value, dict):
        return tuple(sorted((str(key), hook_record_dedupe_value(item)) for key, item in value.items()))
    return value


def hook_record_dedupe_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(hook_record_dedupe_value(record.get(field)) for field in HOOK_RECORD_DEDUPE_FIELDS)


def hook_dedupe_contract() -> dict[str, Any]:
    """Expose the runtime dedupe identity for auditors and hook-health callers."""
    return {
        "schema": HOOK_DEDUPE_CONTRACT_SCHEMA,
        "fields": list(HOOK_RECORD_DEDUPE_FIELDS),
        "timestamp_rule": "same_semantic_different_timestamp_is_replay_history",
        "cursor_batch_rule": "same_invocation_timestamp_different_tool_path_risk_marker_is_not_duplicate",
        "ceiling_noise_rule": "historical_duplicate_replay_and_cursor_batch_noise_is_non_blocking_without_current_v2_contradiction",
        "current_v2_contradiction_rule": "same_host_scope_unexplained_decision_risk_renderer_redaction_marker_contradiction_blocks_ceiling",
    }


def hook_record_identity(record: dict[str, Any]) -> dict[str, Any]:
    """Return a compact explanation of the fields that made a hook row distinct."""
    return {
        "agent": str(record.get("agent") or ""),
        "event_canonical": str(record.get("event_canonical") or canonical_hook_event(str(record.get("event") or ""))),
        "mode": str(record.get("mode") or ""),
        "session": str(record.get("session") or ""),
        "invocation": str(record.get("invocation") or ""),
        "tool": str(record.get("tool") or ""),
        "risk": str(record.get("risk") or ""),
        "path_or_command": str(record.get("path") or record.get("command_category") or ""),
        "decision": str(record.get("decision") or record.get("permission_decision") or ""),
        "marker_emitted": record.get("marker_emitted"),
        "context_suppressed": record.get("context_suppressed"),
    }


def hook_record_already_written(sentinel: Path, record: dict[str, Any]) -> bool:
    if not sentinel.is_file():
        return False
    expected = hook_record_dedupe_key(record)
    try:
        lines = sentinel.read_text(encoding="utf-8").splitlines()[-50:]
    except OSError:
        return False
    for line in reversed(lines):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and hook_record_dedupe_key(payload) == expected:
            return True
    return False


def _command_mentions_tes_hook(command: Any, agent: str) -> bool:
    if isinstance(command, dict):
        text = json.dumps(command, sort_keys=True)
    else:
        text = str(command or "")
    return (
        "tes_install.py" in text
        and " hook" in text
        and (f"--agent {agent}" in text or f'"--agent", "{agent}"' in text)
    )


def _claude_event_configured(data: dict[str, Any], event: str) -> bool:
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return False
    groups = hooks.get(event)
    if not isinstance(groups, list):
        return False
    for group in groups:
        if not isinstance(group, dict):
            continue
        handlers = group.get("hooks")
        if not isinstance(handlers, list):
            continue
        if any(_command_mentions_tes_hook(handler, "claude") for handler in handlers):
            return True
    return False


def _cursor_event_configured(data: dict[str, Any], event: str) -> bool:
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return False
    handlers = hooks.get(event)
    if not isinstance(handlers, list):
        return False
    return any(_command_mentions_tes_hook(handler, "cursor") for handler in handlers)


def configured_hook_events(target: Path) -> dict[str, set[str]]:
    configured: dict[str, set[str]] = {agent: set() for agent in AGENTS}
    codex_config = read_text(target / ".codex/config.toml")
    if "tes_install.py" in codex_config and " hook" in codex_config and "--agent codex" in codex_config:
        if "hooks.SessionStart" in codex_config:
            configured["codex"].add("SessionStart")
        if "hooks.PreToolUse" in codex_config:
            configured["codex"].add("PreToolUse")

    claude_settings = read_json(target / ".claude/settings.json")
    for event in ("SessionStart", "PreToolUse"):
        if _claude_event_configured(claude_settings, event):
            configured["claude"].add(event)

    cursor_hooks = read_json(target / ".cursor/hooks.json")
    for event in ("sessionStart", "beforeSubmitPrompt", "preToolUse"):
        if _cursor_event_configured(cursor_hooks, event):
            configured["cursor"].add(event)
    return configured


def read_hook_execution_records(target: Path, relpath: Path) -> list[dict[str, Any]]:
    path = target / relpath
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    for line in lines:
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            payload.setdefault("sentinel_path", relpath.as_posix())
            records.append(payload)
    return records


def hook_record_matches(record: dict[str, Any], agent: str, event: str, event_canonical: str) -> bool:
    if record.get("agent") != agent:
        return False
    record_event = str(record.get("event") or "")
    record_canonical = str(record.get("event_canonical") or canonical_hook_event(record_event))
    return record_event == event or record_canonical == event_canonical


def duplicate_hook_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[tuple[Any, ...], dict[str, Any]] = {}
    duplicates: list[dict[str, Any]] = []
    for record in records:
        event = str(record.get("event_canonical") or canonical_hook_event(str(record.get("event") or "")))
        key = hook_record_dedupe_key({**record, "event_canonical": event})
        # Repeated audit harnesses may intentionally reuse stable session ids
        # across separate runs. Only same-timestamp semantic repeats indicate an
        # exact double append; later replays are history, not hook duplication.
        ts = str(record.get("ts") or "")
        exact_key = (*key, ts) if ts else key
        if key in seen:
            previous_ts = str(seen[key].get("ts") or "")
            if previous_ts and ts and previous_ts != ts and exact_key not in seen:
                seen[exact_key] = record
                continue
            session = str(record.get("invocation") or record.get("session") or "")
            duplicates.append(
                {
                    "agent": str(record.get("agent") or ""),
                    "event_canonical": event,
                    "mode": str(record.get("mode") or ""),
                    "session_or_invocation": session,
                    "identity": hook_record_identity(record),
                    "count": 2,
                }
            )
        else:
            seen[key] = record
            if exact_key != key:
                seen[exact_key] = record
    return duplicates


def pretooluse_marker_contract(record: dict[str, Any]) -> str:
    """Normalize marker state so anti-cry-wolf suppression is not a contradiction."""
    risk = str(record.get("risk") or "")
    if record.get("marker_emitted") is True or record.get("context_suppressed") is True:
        return "accounted"
    if risk in {"material", "forbidden", "needs-discoverability"}:
        return "missing"
    return "silent"


def pretooluse_contradiction_key(record: dict[str, Any]) -> tuple[Any, ...]:
    event = canonical_hook_event(str(record.get("event_canonical") or record.get("event") or ""))
    return (
        str(record.get("agent") or ""),
        event,
        str(record.get("mode") or ""),
        str(record.get("session") or ""),
        str(record.get("invocation") or ""),
        str(record.get("tool") or record.get("normalized_tool") or record.get("raw_tool_label") or ""),
        str(record.get("path") or ""),
        str(record.get("command_category") or ""),
        str(record.get("payload_source") or ""),
    )


def pretooluse_contradiction_signature(record: dict[str, Any]) -> dict[str, Any]:
    renderer_trace = record.get("renderer_trace") if isinstance(record.get("renderer_trace"), dict) else {}
    return {
        "decision": str(record.get("decision") or ""),
        "permission_decision": str(record.get("permission_decision") or ""),
        "risk": str(record.get("risk") or ""),
        "renderer_output_contract": str(renderer_trace.get("output_contract") or ""),
        "command_redacted": record.get("command_redacted"),
        "marker_contract": pretooluse_marker_contract(record),
    }


def pretooluse_expected_anti_crywolf_renderer_transition(
    fields: list[str], previous_record: dict[str, Any], current_record: dict[str, Any]
) -> bool:
    """Allow the documented first-marker to suppressed-repeat renderer transition."""
    if fields != ["renderer_output_contract"]:
        return False
    records = (previous_record, current_record)
    return any(record.get("marker_emitted") is True for record in records) and any(
        record.get("context_suppressed") is True
        and "anti_crywolf_suppressed" in hook_reason_codes(record.get("reason_codes"))
        for record in records
    )


def pretooluse_current_v2_contradictions(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find same-host current v2 contradictions while allowing stable replay noise."""
    seen: dict[tuple[Any, ...], tuple[dict[str, Any], dict[str, Any]]] = {}
    contradictions: list[dict[str, Any]] = []
    for record in records:
        if record.get("schema_version") != PRETOOLUSE_LEDGER_SCHEMA_VERSION:
            continue
        key = pretooluse_contradiction_key(record)
        signature = pretooluse_contradiction_signature(record)
        previous = seen.get(key)
        if previous is None:
            seen[key] = (record, signature)
            continue
        previous_record, previous_signature = previous
        if previous_signature == signature:
            continue
        fields = [
            field
            for field in PRETOOLUSE_CONTRADICTION_FIELDS
            if previous_signature.get(field) != signature.get(field)
        ]
        if pretooluse_expected_anti_crywolf_renderer_transition(fields, previous_record, record):
            continue
        contradictions.append(
            {
                "fields": fields,
                "first": hook_record_identity(previous_record),
                "current": hook_record_identity(record),
            }
        )
    return contradictions


def hook_floor_status(status_value: str, current_records: list[dict[str, Any]]) -> str:
    """Translate functional hook-health status into the ADR 0009 floor band."""
    if status_value in {"PASS", "PASS_WITH_FINDINGS"} and current_records:
        return "PASS_BASIC"
    if status_value in {"PASS", "PASS_WITH_FINDINGS"}:
        return "NEEDS_EVIDENCE"
    return status_value


def pretooluse_runtime_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        record
        for record in records
        if canonical_hook_event(str(record.get("event_canonical") or record.get("event") or "")) == "PreToolUse"
    ]


def pretooluse_required_hosts(
    records: list[dict[str, Any]],
    configured: dict[str, set[str]] | None = None,
    current_host: str | None = None,
) -> list[str]:
    if current_host:
        return [current_host]

    hosts: list[str] = []
    if configured:
        for agent in AGENTS:
            if any(canonical_hook_event(event) == "PreToolUse" for event in configured.get(agent, set())):
                hosts.append(agent)
        if not hosts:
            hosts.extend(agent for agent in AGENTS if configured.get(agent))

    for record in pretooluse_runtime_records(records):
        agent = str(record.get("agent") or "")
        if agent and agent not in hosts:
            hosts.append(agent)

    ordered = [agent for agent in PRETOOLUSE_CEILING_HOST_ORDER if agent in hosts]
    ordered.extend(sorted(agent for agent in hosts if agent not in PRETOOLUSE_CEILING_HOST_ORDER))
    return ordered


def pretooluse_considered_timestamps(records: list[dict[str, Any]]) -> tuple[str | None, str | None]:
    values = sorted(str(record.get("ts") or "") for record in records if record.get("ts"))
    if not values:
        return None, None
    return values[0], values[-1]


def pretooluse_host_ceiling_gaps(
    records: list[dict[str, Any]],
    *,
    ignored_legacy_records: int = 0,
) -> list[str]:
    """Evaluate ADR 0009 ceiling evidence inside one host scope only."""
    gaps: list[str] = []
    if not records:
        if ignored_legacy_records:
            return ["missing_pretooluse_decision_v2_schema"]
        return ["missing_pretooluse_runtime_rows"]

    has_discoverability = False
    has_redacted_command = False
    has_renderer_projection = False
    for record in records:
        reason_codes = record.get("reason_codes") if isinstance(record.get("reason_codes"), list) else []
        classifier_trace = record.get("classifier_trace") if isinstance(record.get("classifier_trace"), dict) else {}
        renderer_trace = record.get("renderer_trace") if isinstance(record.get("renderer_trace"), dict) else {}
        if not reason_codes:
            gaps.append("missing_reason_codes")
        if not classifier_trace:
            gaps.append("missing_classifier_trace")
        if not renderer_trace.get("output_contract"):
            gaps.append("missing_renderer_trace")
        if "command" in record:
            gaps.append("raw_command_not_redacted")
        if not record.get("command_category"):
            gaps.append("missing_command_category")
        if not record.get("payload_source"):
            gaps.append("missing_payload_source")
        if not record.get("decision") or not record.get("permission_decision"):
            gaps.append("missing_decision_projection")
        if record.get("outcome") == "needs_discoverability" and "needs_discoverability_unknown_mutation" in reason_codes:
            has_discoverability = True
        if record.get("command_redacted") is True and record.get("command_category") not in {"", "no_command", None}:
            has_redacted_command = True
        if "renderer_contract_projected" in reason_codes and renderer_trace.get("output_contract"):
            has_renderer_projection = True

    if not has_discoverability:
        gaps.append("missing_discoverability_runtime_row")
    if not has_redacted_command:
        gaps.append("missing_redacted_command_evidence")
    if not has_renderer_projection:
        gaps.append("missing_renderer_projection_reason")
    if pretooluse_current_v2_contradictions(records):
        gaps.append("current_v2_contradiction")
    return sorted(set(gaps))


def pretooluse_ceiling_evidence(
    records: list[dict[str, Any]],
    *,
    configured: dict[str, set[str]] | None = None,
    current_host: str | None = None,
    required_hosts: list[str] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    pretooluse_records = pretooluse_runtime_records(records)
    hosts = list(required_hosts) if required_hosts is not None else pretooluse_required_hosts(records, configured, current_host)
    scoped_gaps: list[str] = []
    per_host: dict[str, dict[str, Any]] = {}

    for host in hosts:
        host_records = [record for record in pretooluse_records if str(record.get("agent") or "") == host]
        considered_records = [
            record
            for record in host_records
            if record.get("schema_version") == PRETOOLUSE_LEDGER_SCHEMA_VERSION
        ]
        ignored_legacy_records = len(host_records) - len(considered_records)
        # Ceiling F18: partition considered records by provenance. A row is
        # fixture ONLY when it is explicitly tagged provenance="fixture"; an
        # untagged row is treated as host-real for back-compat (records on already
        # installed targets predate the tag and are genuine host executions). A
        # test that wants to prove the fixture-vs-host-real distinction seeds an
        # explicit provenance="fixture" row, which can never read as native.
        fixture_records = [r for r in considered_records if str(r.get("provenance") or "") == "fixture"]
        host_real_records = [r for r in considered_records if str(r.get("provenance") or "") != "fixture"]
        gaps = pretooluse_host_ceiling_gaps(
            considered_records,
            ignored_legacy_records=ignored_legacy_records,
        )
        scoped_gaps.extend(gaps)
        oldest_ts, newest_ts = pretooluse_considered_timestamps(considered_records)
        if not considered_records:
            status = "NEEDS_EVIDENCE"
            native_evidence = "not_available"
        elif not host_real_records:
            # Records exist but none are host-real: the harness ran, the host did
            # not. This is configured-but-unobserved, never a native pass.
            status = "NEEDS_EVIDENCE"
            native_evidence = "fixture_only"
        elif gaps:
            status = "PASS_BASIC_WITH_CEILING_GAPS"
            native_evidence = "host_real"
        else:
            status = "PASS_CEILING"
            native_evidence = "host_real"
        per_host[host] = {
            "agent": host,
            "native_evidence": native_evidence,
            "considered_records": len(considered_records),
            "host_real_records": len(host_real_records),
            "fixture_records": len(fixture_records),
            "ignored_legacy_records": ignored_legacy_records,
            "oldest_considered_ts": oldest_ts,
            "newest_considered_ts": newest_ts,
            "gaps": gaps,
            "current_v2_contradictions": pretooluse_current_v2_contradictions(considered_records),
            "status": status,
        }

    if not hosts and not pretooluse_records:
        scoped_gaps.append("missing_pretooluse_runtime_rows")

    return (
        {
            "schema_version": PRETOOLUSE_LEDGER_SCHEMA_VERSION,
            "claim_scope": "current_host" if current_host else "all_configured_hosts",
            "aggregation_policy": PRETOOLUSE_CEILING_AGGREGATION_POLICY,
            "current_host": current_host,
            "required_hosts": hosts,
            "per_host": per_host,
            "legacy_policy": PRETOOLUSE_LEGACY_POLICY,
        },
        sorted(set(scoped_gaps)),
    )


def pretooluse_ceiling_gaps(
    records: list[dict[str, Any]],
    *,
    required_hosts: list[str] | None = None,
) -> list[str]:
    """Return missing ADR 0009 ceiling evidence from current v2 rows by host."""
    _, gaps = pretooluse_ceiling_evidence(records, required_hosts=required_hosts)
    return gaps


def hook_ceiling_status(floor_status: str, ceiling_gaps: list[str]) -> str:
    if floor_status != "PASS_BASIC":
        return "NEEDS_FLOOR"
    return "PASS_CEILING" if not ceiling_gaps else "NEEDS_CEILING_EVIDENCE"


def installed_pretooluse_helper_contract_status(target: Path) -> str:
    """Verify the installed PreToolUse helper contract without source imports."""
    bin_dir = target / ".tes/bin"
    helper_paths = [bin_dir / helper for helper in HOOK_RUNTIME_HELPERS]
    if not all(path.is_file() for path in helper_paths):
        return "MISSING"

    probe = r'''
import importlib
import json
from pathlib import Path
import sys

failures = []
bin_dir = Path(".tes/bin").resolve()
sys.path.insert(0, str(bin_dir))
try:
    kernel = importlib.import_module("pretooluse_kernel")
    session = importlib.import_module("pretooluse_session")
    if Path(kernel.__file__).resolve().parent != bin_dir:
        failures.append("pretooluse_kernel not imported from .tes/bin")
    if Path(session.__file__).resolve().parent != bin_dir:
        failures.append("pretooluse_session not imported from .tes/bin")
    for name in ("decide_pretooluse", "hook_event_name", "hook_tool_input", "hook_tool_name", "hook_tool_path"):
        if not callable(getattr(kernel, name, None)):
            failures.append(f"pretooluse_kernel missing callable {name}")
    for name in ("coordinate_pretooluse_context", "pretooluse_session_id", "pretooluse_sentinel_path"):
        if not callable(getattr(session, name, None)):
            failures.append(f"pretooluse_session missing callable {name}")
    cortex_runtime_text = (bin_dir / "cortex_runtime.py").read_text(encoding="utf-8", errors="ignore")
    if "def evaluate_runtime_event" not in cortex_runtime_text:
        failures.append("cortex_runtime missing evaluate_runtime_event definition")
    hook_input = {
        "hook_event_name": "PreToolUse",
        "tool_name": "PatchFile",
        "tool_input": {"file_path": "docs/adr/0010-future.md"},
        "session_id": "installed-hook-health-helper-probe",
    }
    decision = kernel.decide_pretooluse(
        hook_input,
        risk_classifier=lambda action, paths: "routine",
        marker="`installed-hook-health-helper-probe`",
    )
    reason_codes = decision.get("reason_codes") if isinstance(decision.get("reason_codes"), list) else []
    classifier_trace = decision.get("classifier_trace") if isinstance(decision.get("classifier_trace"), dict) else {}
    if decision.get("outcome") != "needs_discoverability":
        failures.append("kernel did not preserve needs_discoverability outcome")
    if decision.get("risk") != "needs-discoverability":
        failures.append("kernel did not preserve needs-discoverability risk")
    if "needs_discoverability_unknown_mutation" not in reason_codes:
        failures.append("kernel missing discoverability reason code")
    if classifier_trace.get("unknown_mutating") is not True:
        failures.append("kernel missing unknown_mutating classifier trace")
    session_context = session.coordinate_pretooluse_context(Path("."), hook_input, "")
    if session_context.context != "" or session_context.context_suppressed is not False:
        failures.append("session helper did not preserve empty-context no-write contract")
except Exception as exc:
    failures.append(f"{type(exc).__name__}: {exc}")

print(json.dumps({"status": "PASS" if not failures else "FAIL", "failures": failures}, sort_keys=True))
'''
    try:
        proc = subprocess.run(
            [python_executable(), "-c", probe],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return "FAIL"
    payload = parse_json_output(proc.stdout)
    if proc.returncode != 0 or payload.get("status") != "PASS":
        return "FAIL"
    return "PASS"


def pretooluse_discoverability_status(records: list[dict[str, Any]]) -> str:
    """Report installed discoverability proof from current v2 hook ledger rows."""
    has_v2_pretooluse = False
    for record in pretooluse_runtime_records(records):
        if record.get("schema_version") != PRETOOLUSE_LEDGER_SCHEMA_VERSION:
            continue
        has_v2_pretooluse = True
        reason_codes = record.get("reason_codes") if isinstance(record.get("reason_codes"), list) else []
        renderer_trace = record.get("renderer_trace") if isinstance(record.get("renderer_trace"), dict) else {}
        if (
            record.get("outcome") == "needs_discoverability"
            and record.get("risk") == "needs-discoverability"
            and "needs_discoverability_unknown_mutation" in reason_codes
            and bool(renderer_trace.get("output_contract"))
        ):
            return "NEEDS_DISCOVERABILITY"
    return "NEEDS_EVIDENCE" if has_v2_pretooluse else "MISSING"


def attached_surfaces_from_lock(target: Path) -> set[str]:
    """Read the install lock's declared surfaces for health/admission checks."""
    lock = read_json(target / LOCK_PATH)
    surfaces = lock.get("attached_surfaces")
    if not isinstance(surfaces, list):
        return set()
    return {str(surface) for surface in surfaces if isinstance(surface, str)}


def hook_surface_attached(target: Path) -> bool:
    return "hooks" in attached_surfaces_from_lock(target)


def hook_health_payload(target: Path, *, current_host: str | None = None) -> dict[str, Any]:
    target = target_root(target)
    configured = configured_hook_events(target)
    attached_surfaces = attached_surfaces_from_lock(target)
    hooks_attached = "hooks" in attached_surfaces
    current_records = read_hook_execution_records(target, HOOK_SENTINEL_PATH)
    legacy_records = read_hook_execution_records(target, LEGACY_HOOK_SENTINEL_PATH)
    duplicate_records = duplicate_hook_records(current_records)
    findings: list[dict[str, Any]] = []
    agents: dict[str, Any] = {}

    for agent, contracts in HOOK_HEALTH_CONTRACTS.items():
        event_results: list[dict[str, Any]] = []
        for contract in contracts:
            event = contract["event"]
            event_canonical = contract["event_canonical"]
            is_configured = event in configured.get(agent, set())
            observed_records = [
                record
                for record in current_records
                if hook_record_matches(record, agent, event, event_canonical)
            ]
            legacy_observed = any(
                hook_record_matches(record, agent, event, event_canonical)
                for record in legacy_records
            )
            if is_configured and observed_records:
                state = "OBSERVED"
            elif is_configured:
                state = "CONFIGURED"
                findings.append(
                    {
                        "severity": "info",
                        "type": "configured_without_runtime_observation",
                        "agent": agent,
                        "event": event,
                    }
                )
            elif observed_records:
                state = "STALE/UNEXPECTED"
                findings.append(
                    {
                        "severity": "error",
                        "type": "runtime_observed_without_config",
                        "agent": agent,
                        "event": event,
                    }
                )
            else:
                state = "NOT_CONFIGURED"
            event_results.append(
                {
                    "event": event,
                    "event_canonical": event_canonical,
                    "config": contract["config"],
                    "state": state,
                    "runtime_records": len(observed_records),
                    "legacy_observed": legacy_observed,
                }
            )
        agents[agent] = {"events": event_results}

    if legacy_records:
        findings.append(
            {
                "severity": "info",
                "type": "legacy_hook_ledger_present",
                "path": LEGACY_HOOK_SENTINEL_PATH.as_posix(),
                "records": len(legacy_records),
                "status": "STALE/RESIDUE",
            }
        )
    if duplicate_records:
        findings.append(
            {
                "severity": "warning",
                "type": "duplicate_runtime_hook_records",
                "dedupe_fields": list(HOOK_RECORD_DEDUPE_FIELDS),
                "records": duplicate_records,
            }
        )
    unexpected = any(
        event["state"] == "STALE/UNEXPECTED"
        for agent in agents.values()
        for event in agent["events"]
    )
    any_configured = any(
        event["state"] == "CONFIGURED" or event["state"] == "OBSERVED"
        for agent in agents.values()
        for event in agent["events"]
    )
    all_not_configured = all(
        event["state"] == "NOT_CONFIGURED"
        for agent in agents.values()
        for event in agent["events"]
    )
    if hooks_attached and all_not_configured:
        findings.append(
            {
                "severity": "error",
                "type": "attached_hooks_without_config",
                "lock_path": LOCK_PATH.as_posix(),
                "attached_surfaces": sorted(attached_surfaces),
            }
        )
    configured_only = any(
        event["state"] == "CONFIGURED"
        for agent in agents.values()
        for event in agent["events"]
    )
    helper_contract_status = installed_pretooluse_helper_contract_status(target)
    if hooks_attached and helper_contract_status != "PASS":
        findings.append(
            {
                "severity": "error",
                "type": "installed_hook_helper_contract_invalid",
                "helper_contract_status": helper_contract_status,
                "expected_helpers": list(HOOK_RUNTIME_HELPERS),
            }
        )
    finding_counts = {
        "error": sum(1 for finding in findings if finding.get("severity") == "error"),
        "warning": sum(1 for finding in findings if finding.get("severity") == "warning"),
        "info": sum(1 for finding in findings if finding.get("severity") == "info"),
    }
    if not hooks_attached and not any_configured and not current_records and not legacy_records:
        status_value = "NOT_APPLIED"
    elif unexpected or finding_counts["error"]:
        status_value = "DEGRADED"
    elif configured_only:
        status_value = "NEEDS_EVIDENCE"
    elif not any_configured and (current_records or legacy_records):
        status_value = "DEGRADED"
    elif findings:
        status_value = "PASS_WITH_FINDINGS"
    else:
        status_value = "PASS"

    floor_status_value = hook_floor_status(status_value, current_records)
    ceiling_evidence_scope, ceiling_gaps = pretooluse_ceiling_evidence(
        current_records,
        configured=configured,
        current_host=current_host if current_host in AGENTS else None,
    )
    ceiling_status_value = hook_ceiling_status(floor_status_value, ceiling_gaps)
    discoverability_status = pretooluse_discoverability_status(current_records)

    return {
        "schema": HOOK_HEALTH_SCHEMA_VERSION,
        "legacy_schema": HOOK_HEALTH_LEGACY_SCHEMA_VERSION,
        "version": VERSION,
        "status": status_value,
        "attached_surfaces": sorted(attached_surfaces),
        "helper_contract_status": helper_contract_status,
        "discoverability_status": discoverability_status,
        "floor_status": floor_status_value,
        "ceiling_status": ceiling_status_value,
        "ceiling_gaps": ceiling_gaps,
        "ceiling_evidence_scope": ceiling_evidence_scope,
        "target": str(target),
        "dedupe_contract": hook_dedupe_contract(),
        "sentinels": {
            "current": {
                "path": HOOK_SENTINEL_PATH.as_posix(),
                "records": len(current_records),
                "status": "OBSERVED" if current_records else "MISSING",
            },
            "legacy": {
                "path": LEGACY_HOOK_SENTINEL_PATH.as_posix(),
                "records": len(legacy_records),
                "status": "STALE/RESIDUE" if legacy_records else "ABSENT",
            },
        },
        "agents": agents,
        "finding_counts": finding_counts,
        "findings": findings,
    }


def _classify_pretooluse_risk(action: str, paths: list[str]) -> str:
    """Project the bootloader criterion onto a tool call via mantra_gate.classify_risk.

    classify_risk is the executable form of the <mantra_gate> rule (Pillar 0), but
    it keys on intent vocabulary, not raw shell — so the hook combines it with the
    reliable structural signal (a mutating tool touching a governed artifact) rather
    than trusting the regex on a raw command alone. Import defensively: in an adopter
    both tes_install.py and mantra_gate.py live under .tes/bin/, but if the module is
    absent the gate degrades to routine (never block on an import error).
    """
    try:
        import mantra_gate  # noqa: PLC0415 - delivered sibling under .tes/bin/
    except Exception:
        return "routine"
    try:
        return str(mantra_gate.classify_risk(action=action, paths=paths).get("risk", "routine"))
    except Exception:
        return "routine"


def _mantra_gate_marker() -> str:
    """Return the delivered Mantra Gate marker without making the hook brittle."""
    try:
        import mantra_gate  # noqa: PLC0415 - delivered sibling under .tes/bin/
    except Exception:
        return "`🍳 Flash-Fry`"
    marker = getattr(mantra_gate, "MARKER", "`🍳 Flash-Fry`")
    return str(marker or "`🍳 Flash-Fry`")


def _join_context(*parts: str) -> str:
    return "\n".join(part for part in parts if part)


def _evaluate_cortex_runtime(target: Path, agent: str, hook_input: dict[str, Any]) -> dict[str, Any]:
    try:
        import cortex_runtime  # noqa: PLC0415 - delivered sibling under .tes/bin/
    except Exception:
        return {}
    try:
        result = cortex_runtime.evaluate_runtime_event(target, {"host": agent, "input": hook_input})
    except Exception:
        return {}
    return result if isinstance(result, dict) else {}


def _cortex_runtime_context(result: dict[str, Any], *, include_capture: bool = True) -> str:
    lines: list[str] = []
    signal = result.get("alignment_signal") if isinstance(result.get("alignment_signal"), dict) else {}
    if signal.get("status") == "NEEDS_ALIGN":
        refs = signal.get("evidence_refs") if isinstance(signal.get("evidence_refs"), list) else []
        refs_text = ",".join(str(item) for item in refs if item)
        reason = str(signal.get("reason") or "Operating mesh drift detected.")
        next_action = str(signal.get("next_action") or "Run /tes-align before claiming operating-mesh alignment.")
        lines.append(
            f"Cortex runtime: status=NEEDS_ALIGN evidence_refs={refs_text} "
            f"reason={reason} next_action={next_action}"
        )
    capture = result.get("capture_proposal") if isinstance(result.get("capture_proposal"), dict) else {}
    if include_capture and capture.get("status") == "PROPOSED":
        refs = capture.get("evidence_refs") if isinstance(capture.get("evidence_refs"), list) else []
        refs_text = ",".join(str(item) for item in refs if item)
        lines.append(
            "Cortex runtime: capture_proposal=PROPOSED "
            f"evidence_refs={refs_text} next_action=request explicit authorization before any durable Cortex write."
        )
    return "\n".join(lines)


def _append_cortex_result(result: dict[str, Any], context: str) -> dict[str, Any]:
    if not context:
        return result
    return {**result, "cortex": {"additional_context": context}}


def _append_claude_additional_context(output: dict[str, Any], event_name: str, context: str) -> dict[str, Any]:
    if not context:
        return output
    updated = dict(output)
    hook_specific = updated.get("hookSpecificOutput")
    if not isinstance(hook_specific, dict):
        hook_specific = {"hookEventName": event_name}
        updated["hookSpecificOutput"] = hook_specific
    hook_specific["hookEventName"] = str(hook_specific.get("hookEventName") or event_name)
    hook_specific["additionalContext"] = _join_context(str(hook_specific.get("additionalContext") or ""), context)
    return updated


def _pretooluse_decision(hook_input: dict[str, Any]) -> dict[str, Any]:
    """Compatibility wrapper around the host-neutral PreToolUse kernel."""
    return decide_pretooluse(
        hook_input,
        risk_classifier=_classify_pretooluse_risk,
        marker=_mantra_gate_marker(),
    )


def _pretooluse_may_touch_operating_mesh(hook_input: dict[str, Any]) -> bool:
    tool_input = hook_tool_input(hook_input)
    values = [
        hook_tool_path(hook_input, tool_input),
        hook_tool_command(hook_input, tool_input),
        json.dumps(tool_input, sort_keys=True),
    ]
    text = "\n".join(value for value in values if value).replace("\\", "/")
    return any(hint in text for hint in OPERATING_MESH_PRETOOLUSE_HINTS)


def hook_pretooluse(args: argparse.Namespace, hook_input: dict[str, Any]) -> int:
    """PreToolUse handler — the per-host pre-action projection of the senior manager.

    Output contract is NOT uniform (verified against the reference study):
      - Claude/Codex: exit 2 + stderr blocks; exit 0 allows. additionalContext
        injects the supervision obligation without blocking.
      - Cursor: JSON-permission — {"permission":"deny","agent_message":...} blocks,
        {"continue":true,"user_message":...} / {"permission":"allow"} allows.
        Deny messages are the reliable visible channel; governed allow messages
        are best-effort and the runtime ledger is the canonical proof.
    A materializer that assumed exit-2 everywhere would break silently on Cursor.
    """
    target = target_root(args.target)
    decision = _pretooluse_decision(hook_input)

    if decision["block"]:
        reason_codes = hook_reason_codes(decision.get("reason_codes"), "renderer_contract_projected")
        record_hook_execution(
            target,
            args.agent,
            hook_input,
            mode="pretooluse",
            pretooluse_decision={
                **decision,
                "reason_codes": reason_codes,
                "renderer_trace": pretooluse_renderer_trace(args.agent, block=True),
                "decision": "block",
                "permission_decision": "deny",
                "marker_emitted": True,
                "context_suppressed": False,
                "cortex_context_emitted": False,
                "surface_context": True,
            },
        )
        reason = decision["reason"]
        if args.agent == "cursor":
            print(json.dumps({"permission": "deny", "agent_message": reason}, ensure_ascii=False, sort_keys=True))
            return 0
        print(reason, file=sys.stderr)
        return 2

    session_context = coordinate_pretooluse_context(target, hook_input, str(decision.get("context") or ""))
    context = session_context.context
    context_suppressed = session_context.context_suppressed
    cortex_context = ""
    if _pretooluse_may_touch_operating_mesh(hook_input):
        cortex_context = _cortex_runtime_context(
            _evaluate_cortex_runtime(target, args.agent, hook_input),
            include_capture=False,
        )
    combined_context = _join_context(context, cortex_context)
    reason_codes = hook_reason_codes(decision.get("reason_codes"), session_context.reason_codes)
    if cortex_context:
        reason_codes = hook_reason_codes(reason_codes, "cortex_advisory_no_write")
    reason_codes = hook_reason_codes(reason_codes, "renderer_contract_projected")
    record_hook_execution(
        target,
        args.agent,
        hook_input,
        mode="pretooluse",
        pretooluse_decision={
            **decision,
            "reason_codes": reason_codes,
            "renderer_trace": pretooluse_renderer_trace(
                args.agent,
                block=False,
                context=context,
                cortex_context=cortex_context,
            ),
            "decision": "allow",
            "permission_decision": "allow",
            "marker_emitted": bool(context),
            "context_suppressed": context_suppressed,
            "cortex_context_emitted": bool(cortex_context),
            "surface_context": bool(combined_context),
        },
    )
    if combined_context:
        if args.agent == "cursor":
            payload: dict[str, Any] = {"continue": True, "permission": "allow"}
            if context:
                payload["user_message"] = context
            if cortex_context:
                payload["agent_message"] = cortex_context
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            return 0
        if args.agent == "claude":
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "allow",
                            "additionalContext": combined_context,
                        }
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 0
        print(combined_context, file=sys.stderr)
        return 0

    # Supervision-only, nothing to surface -> allow silently (no cry-wolf).
    if args.agent == "cursor":
        print(json.dumps({"permission": "allow"}, sort_keys=True))
    return 0


def hook(args: argparse.Namespace) -> int:
    hook_input = parse_hook_input()
    if args.target == Path("."):
        inferred = hook_input.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR")
        if inferred:
            args.target = Path(str(inferred))
    if hook_event_name(hook_input, "") in {"PreToolUse", "preToolUse"}:
        return hook_pretooluse(args, hook_input)
    target = target_root(args.target)
    blocked = package_source_block(target, "hook")
    if blocked:
        if args.agent == "claude":
            if args.rewake_on_complete:
                print("TES install is blocked for the TES package source root.", file=sys.stderr)
                return 2
            print(json.dumps(claude_hook_output(blocked, hook_input), sort_keys=True))
            return 0
        if args.agent == "cursor":
            print("{}")
            return 2
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 2
    # SPEC-005: the hook fired for real — record the execution sentinel.
    mode = "session_start"
    if args.announce_start:
        mode = "announce_start"
    elif args.rewake_on_complete:
        mode = "rewake_on_complete"
    record_hook_execution(target, args.agent, hook_input, mode=mode)
    cortex_context = _cortex_runtime_context(_evaluate_cortex_runtime(target, args.agent, hook_input))
    if args.agent == "claude" and args.announce_start:
        event_name = hook_event_name(hook_input)
        output = _append_claude_additional_context(claude_start_notice_output(target, hook_input), event_name, cortex_context)
        print(json.dumps(output, sort_keys=True))
        return 0
    code, result = postinstall(args, hook_input=hook_input)
    result = _append_cortex_result(result, cortex_context)
    if args.agent == "claude":
        if args.rewake_on_complete:
            message = claude_rewake_message(result)
            if message:
                print(_join_context(message, cortex_context), file=sys.stderr)
                return 2
            return 0
        print(json.dumps(claude_hook_output(result, hook_input), sort_keys=True))
        return 0
    if args.agent == "cursor":
        if cortex_context:
            print(json.dumps({"continue": True, "agent_message": cortex_context}, ensure_ascii=False, sort_keys=True))
        else:
            print("{}")
    elif result.get("status") not in {"SKIP"}:
        print(json.dumps(result, indent=2, sort_keys=True))
    return code


def status(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    result = {
        "version": VERSION,
        "status": "PASS",
        "target": str(target),
        "lock": read_json(target / LOCK_PATH),
        "postinstall": read_json(target / POSTINSTALL_PATH),
        "manifest": read_json(target / ".tes/manifest.json"),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def hook_health(args: argparse.Namespace) -> int:
    result = hook_health_payload(args.target, current_host=getattr(args, "agent", None))
    print(json.dumps(result, indent=2, sort_keys=True))
    # Ceiling F23: query vs gate exit codes. The DEFAULT (query) mode preserves
    # the pending-host install contract — a fresh install legitimately reports
    # NEEDS_EVIDENCE (hooks configured, host not yet observed) and must exit 0 so
    # the installer flow does not treat it as failure. Opt-in --gate mode makes
    # the exit code certify the JSON: NEEDS_EVIDENCE (missing proof) exits
    # non-zero, so a shell caller cannot read success where the JSON says
    # evidence is absent.
    gate = getattr(args, "gate", False)
    if gate:
        return 0 if result["status"] in {"PASS", "PASS_WITH_FINDINGS"} else 1
    return 0 if result["status"] in {"PASS", "PASS_WITH_FINDINGS", "NEEDS_EVIDENCE"} else 1


def self_test() -> int:
    failures: list[str] = []

    # Ceiling F27 (attach/detach transact the install lock): a narrow attach or
    # detach must re-transact lock.attached_surfaces additively (attach merges in,
    # detach removes but never drops the capsule), bump the lock version, and
    # honor --dry-run. Red-capable: removing the transact_lock_surface calls or
    # regressing the merge turns these assertions red.
    with tempfile.TemporaryDirectory(prefix="tes-f27-lock-") as _f27_dir:
        _f27_target = Path(_f27_dir)
        _lock_path = _f27_target / LOCK_PATH
        _lock_path.parent.mkdir(parents=True, exist_ok=True)
        _lock_path.write_text(
            json.dumps({"version": "0.0.0", "attached_surfaces": ["capsule", "mcp"]}, sort_keys=True),
            encoding="utf-8",
        )
        # dry-run must not write the lock.
        transact_lock_surface(_f27_target, "hooks", attach=True, certification_result=None, dry_run=True)
        if "hooks" in (read_json(_lock_path).get("attached_surfaces") or []):
            failures.append("F27: dry-run attach must not write the lock")
        # attach merges the surface in, keeps existing surfaces, bumps version.
        transact_lock_surface(_f27_target, "hooks", attach=True, certification_result=None, dry_run=False)
        _after_attach = read_json(_lock_path)
        if "hooks" not in (_after_attach.get("attached_surfaces") or []):
            failures.append("F27: attach must merge the surface into lock.attached_surfaces")
        if "mcp" not in (_after_attach.get("attached_surfaces") or []):
            failures.append("F27: attach must be additive (must not drop existing surfaces)")
        if _after_attach.get("version") != VERSION:
            failures.append("F27: attach must bump the lock version to the current VERSION")
        # detach removes the surface but never drops the capsule.
        transact_lock_surface(_f27_target, "hooks", attach=False, certification_result=None, dry_run=False)
        _after_detach = read_json(_lock_path)
        if "hooks" in (_after_detach.get("attached_surfaces") or []):
            failures.append("F27: detach must remove the surface from lock.attached_surfaces")
        if "capsule" not in (_after_detach.get("attached_surfaces") or []):
            failures.append("F27: detach must never drop the capsule from the lock")

    # Ceiling F28 (doctor readiness fold): a green capsule with a pending or
    # degraded attachment must NOT read as ready — readiness folds the worst
    # materialized surface. Pure-function red-capable check: collapsing the fold
    # to always-PASS turns these red.
    if _fold_attachment_readiness("PASS", ["PASS", "PASS"]) != "PASS":
        failures.append("F28: all-healthy attachments must fold to PASS readiness")
    if _fold_attachment_readiness("PASS", ["PASS", "PENDING_HOST_RESTART"]) != "PENDING_HOST_RESTART":
        failures.append("F28: a pending attachment must surface in readiness, not hide behind a PASS capsule")
    if _fold_attachment_readiness("PASS", ["PASS", "DEGRADED"]) != "DEGRADED":
        failures.append("F28: a degraded attachment must surface in readiness")
    if _fold_attachment_readiness("NOT_INSTALLED", []) != "NOT_INSTALLED":
        failures.append("F28: no capsule must read NOT_INSTALLED readiness")

    def run(
        args: list[str] | tuple[str, ...],
        *,
        cwd: Path | str | None = None,
        input: str | None = None,
        timeout: float = SELF_TEST_SUBPROCESS_TIMEOUT,
    ) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                args,
                cwd=cwd,
                input="" if input is None else input,
                text=True,
                capture_output=True,
                check=False,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            command = " ".join(shlex.quote(str(part)) for part in args)
            failures.append(f"self-test subprocess timed out after {timeout:g}s: {command}")
            stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace")
            stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", errors="replace")
            return subprocess.CompletedProcess(
                list(args),
                124,
                stdout,
                stderr.strip() or f"timed out after {timeout:g}s",
            )

    def ceiling_record(
        agent: str,
        session: str,
        *,
        reason_codes: list[str] | None = None,
        command_redacted: bool = True,
        command_category: str = "shell_command",
        outcome: str = "needs_discoverability",
        risk: str = "needs-discoverability",
        tool: str = "PatchFile",
        path: str = "docs/adr/0010-future.md",
        invocation: str | None = None,
        marker_emitted: bool = True,
        context_suppressed: bool = False,
    ) -> dict[str, Any]:
        return {
            "schema_version": PRETOOLUSE_LEDGER_SCHEMA_VERSION,
            "agent": agent,
            "event_canonical": "PreToolUse",
            "mode": "pretooluse",
            "session": session,
            "invocation": invocation or session,
            "ts": "2026-06-27T00:00:00Z",
            "tool": tool,
            "path": path,
            "reason_codes": reason_codes
            if reason_codes is not None
            else ["needs_discoverability_unknown_mutation", "renderer_contract_projected"],
            "classifier_trace": {"payload_source": "tool_input", "path_source": "tool_input.file_path"},
            "renderer_trace": {"renderer": f"{agent}_pretooluse", "output_contract": "stderr_context"},
            "command_category": command_category,
            "command_redacted": command_redacted,
            "payload_source": "tool_input",
            "risk": risk,
            "decision": "allow",
            "permission_decision": "allow",
            "outcome": outcome,
            "marker_emitted": marker_emitted,
            "context_suppressed": context_suppressed,
        }

    complete_codex = ceiling_record("codex", "complete-v2")
    legacy_codex = {
        "agent": "codex",
        "event_canonical": "PreToolUse",
        "mode": "pretooluse",
        "session": "legacy-pre-v2",
        "ts": "2026-06-26T00:00:00Z",
    }
    mixed_scope, mixed_gaps = pretooluse_ceiling_evidence([complete_codex, legacy_codex])
    mixed_codex = mixed_scope.get("per_host", {}).get("codex", {})
    if mixed_gaps:
        failures.append(f"PreToolUse ceiling scope must ignore legacy gaps when same-host v2 evidence is complete: {mixed_gaps}")
    if mixed_codex.get("ignored_legacy_records") != 1 or mixed_codex.get("considered_records") != 1:
        failures.append("PreToolUse ceiling scope must report same-host ignored legacy counts")
    if mixed_scope.get("schema_version") != PRETOOLUSE_LEDGER_SCHEMA_VERSION:
        failures.append("PreToolUse ceiling scope must expose pretooluse_decision@2 schema")
    if mixed_scope.get("aggregation_policy") != PRETOOLUSE_CEILING_AGGREGATION_POLICY:
        failures.append("PreToolUse ceiling scope must use per_host_no_cross_fill aggregation")
    if mixed_scope.get("legacy_policy") != PRETOOLUSE_LEGACY_POLICY:
        failures.append("PreToolUse ceiling scope must mark legacy rows as historical context only")
    duplicate_legacy = duplicate_hook_records([legacy_codex, legacy_codex])
    if not duplicate_legacy:
        failures.append("PreToolUse ceiling legacy scoping must preserve exact duplicate warnings")
    historical_noise_scope, historical_noise_gaps = pretooluse_ceiling_evidence(
        [complete_codex, legacy_codex, legacy_codex],
        required_hosts=["codex"],
    )
    historical_noise_codex = historical_noise_scope.get("per_host", {}).get("codex", {})
    if historical_noise_gaps or historical_noise_codex.get("status") != "PASS_CEILING":
        failures.append("PreToolUse ceiling scope must keep historical duplicate noise non-blocking")

    replayed_codex = {**complete_codex, "ts": "2026-06-27T00:05:00Z"}
    replay_scope, replay_gaps = pretooluse_ceiling_evidence([complete_codex, replayed_codex], required_hosts=["codex"])
    replay_codex = replay_scope.get("per_host", {}).get("codex", {})
    if replay_gaps or replay_codex.get("status") != "PASS_CEILING":
        failures.append("PreToolUse ceiling scope must treat stable current v2 replay rows as non-blocking")

    cursor_batch_write = ceiling_record(
        "cursor",
        "cursor-batch",
        tool="Write",
        path=".cursor/rules/a.mdc",
        invocation="cursor-batch-invocation",
    )
    cursor_batch_multiedit = ceiling_record(
        "cursor",
        "cursor-batch",
        reason_codes=["governed_surface_mutation", "renderer_contract_projected"],
        outcome="allow",
        risk="material",
        tool="MultiEdit",
        path=".cursor/rules/b.mdc",
        invocation="cursor-batch-invocation",
        marker_emitted=False,
        context_suppressed=True,
    )
    cursor_batch_scope, cursor_batch_gaps = pretooluse_ceiling_evidence(
        [cursor_batch_write, cursor_batch_multiedit],
        required_hosts=["cursor"],
    )
    cursor_batch_cursor = cursor_batch_scope.get("per_host", {}).get("cursor", {})
    if cursor_batch_gaps or cursor_batch_cursor.get("status") != "PASS_CEILING":
        failures.append("PreToolUse ceiling scope must keep distinct Cursor batch rows non-blocking")

    partial_v2 = {**complete_codex, "session": "partial-v2", "classifier_trace": {}}
    partial_gaps = pretooluse_ceiling_gaps([partial_v2], required_hosts=["codex"])
    if "missing_classifier_trace" not in partial_gaps:
        failures.append("PreToolUse ceiling scope must still fail current v2 rows with missing required fields")

    complete_claude = ceiling_record("claude", "complete-v2-claude")
    contradictory_codex = {**complete_codex, "decision": "block", "permission_decision": "deny"}
    contradiction_scope, contradiction_gaps = pretooluse_ceiling_evidence(
        [complete_codex, contradictory_codex, complete_claude],
        required_hosts=["codex", "claude"],
    )
    contradiction_codex = contradiction_scope.get("per_host", {}).get("codex", {})
    contradiction_claude = contradiction_scope.get("per_host", {}).get("claude", {})
    if "current_v2_contradiction" not in contradiction_gaps:
        failures.append("PreToolUse ceiling scope must block current v2 contradictions")
    if "current_v2_contradiction" not in contradiction_codex.get("gaps", []):
        failures.append("PreToolUse ceiling contradiction must be scoped to the affected host")
    if contradiction_claude.get("status") != "PASS_CEILING" or contradiction_claude.get("gaps"):
        failures.append("PreToolUse ceiling contradiction must not block unaffected hosts")
    current_host_scope, current_host_gaps = pretooluse_ceiling_evidence(
        [complete_codex, contradictory_codex, complete_claude],
        current_host="claude",
    )
    current_host_claude = current_host_scope.get("per_host", {}).get("claude", {})
    if current_host_gaps or current_host_claude.get("status") != "PASS_CEILING":
        failures.append("PreToolUse current-host ceiling scope must ignore other-host v2 contradictions")

    anti_crywolf_first = ceiling_record(
        "claude",
        "anti-crywolf-renderer",
        reason_codes=["governed_surface_mutation", "renderer_contract_projected"],
        outcome="allow",
        risk="material",
        tool="Edit",
        path=".tes/runtime/hook-smoke/claude/SKILL.md",
        invocation="anti-crywolf-renderer",
        marker_emitted=True,
        context_suppressed=False,
    )
    anti_crywolf_first["renderer_trace"] = {"renderer": "claude_pretooluse", "output_contract": "json_hookSpecificOutput_allow"}
    anti_crywolf_repeat = {
        **anti_crywolf_first,
        "reason_codes": ["governed_surface_mutation", "anti_crywolf_suppressed", "renderer_contract_projected"],
        "marker_emitted": False,
        "context_suppressed": True,
        "renderer_trace": {"renderer": "claude_pretooluse", "output_contract": "silent_allow"},
    }
    anti_crywolf_scope, anti_crywolf_gaps = pretooluse_ceiling_evidence(
        [complete_claude, anti_crywolf_first, anti_crywolf_repeat],
        required_hosts=["claude"],
    )
    anti_crywolf_claude = anti_crywolf_scope.get("per_host", {}).get("claude", {})
    if anti_crywolf_gaps or anti_crywolf_claude.get("status") != "PASS_CEILING":
        failures.append("PreToolUse ceiling contradiction must ignore anti-cry-wolf renderer suppression transitions")

    claude_discoverability = ceiling_record(
        "claude",
        "claude-discoverability-only",
        reason_codes=["needs_discoverability_unknown_mutation"],
        command_redacted=False,
        command_category="no_command",
    )
    codex_redaction = ceiling_record(
        "codex",
        "codex-redaction-only",
        reason_codes=["governed_surface_mutation"],
        outcome="allow",
    )
    cursor_renderer = ceiling_record(
        "cursor",
        "cursor-renderer-only",
        reason_codes=["renderer_contract_projected"],
        command_redacted=False,
        command_category="no_command",
        outcome="allow",
    )
    cross_scope, cross_gaps = pretooluse_ceiling_evidence(
        [claude_discoverability, codex_redaction, cursor_renderer],
        required_hosts=list(PRETOOLUSE_CEILING_HOST_ORDER),
    )
    cross_statuses = {
        str(agent): str(entry.get("status"))
        for agent, entry in cross_scope.get("per_host", {}).items()
        if isinstance(entry, dict)
    }
    if not cross_gaps or any(status == "PASS_CEILING" for status in cross_statuses.values()):
        failures.append("PreToolUse ceiling scope must not borrow evidence fields across hosts")

    # derive_sentinel_reason: the review reason must name the gate that actually
    # blocks, not always the obsolete-cleanup boilerplate. Exercise BOTH the
    # summarized shape (components at top level) AND the RAW run_installed_
    # certification shape (components under payload) — the call site passes the
    # raw shape, so testing only the summarized one hid the component name loss.
    summarized_reason = derive_sentinel_reason(
        {"status": "APPLIED", "obsolete_cleanup": {"status": "PASS", "review_items": []}},
        {"status": "NEEDS_REVIEW", "components": {"mantra_gate_adoption": "NEEDS_REVIEW", "mcp_registration": "PASS"}},
    )
    if "mantra_gate_adoption" not in summarized_reason or "certification" not in summarized_reason:
        failures.append("sentinel reason must name the blocking component from a summarized certification result")
    raw_reason = derive_sentinel_reason(
        {"status": "APPLIED", "obsolete_cleanup": {"status": "PASS", "review_items": []}},
        {"status": "NEEDS_REVIEW", "returncode": 1,
         "payload": {"components": {"mantra_gate_adoption": {"status": "NEEDS_REVIEW"},
                                     "mcp_registration": {"status": "PASS"}}}},
    )
    if "mantra_gate_adoption" not in raw_reason:
        failures.append("sentinel reason must name the blocking component from a RAW certification result (payload.components)")
    obsolete_reason = derive_sentinel_reason(
        {"status": "NEEDS_REVIEW", "obsolete_cleanup": {"status": "NEEDS_REVIEW", "review_items": [{"path": "x"}]}},
        {"status": "PASS", "components": {}},
    )
    if "obsolete" not in obsolete_reason:
        failures.append("sentinel reason must keep the obsolete-artifacts message when there are real review items")
    none_reason = derive_sentinel_reason(
        {"status": "NEEDS_REVIEW", "obsolete_cleanup": {"status": "NEEDS_REVIEW", "review_items": [{"path": "x"}]}},
        None,
    )
    if "certification" in none_reason:
        failures.append("sentinel reason must not invent a certification blocker when certification_result is None")

    with tempfile.TemporaryDirectory(prefix="tes-postinstall-oracle-failure-") as tempdir:
        target = Path(tempdir)
        script = target / ".tes/bin/project_context_oracle.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text(
            "import json, sys\n"
            "print(json.dumps({'status': 'FAIL', 'failures': ['neutral oracle failure']}))\n"
            "sys.exit(1)\n",
            encoding="utf-8",
        )
        result = run_helper(target, "project_context_oracle.py", (), 10)
        if result.get("oracle_failures") != ["neutral oracle failure"]:
            failures.append("postinstall helper results must preserve structured oracle failures")

    with tempfile.TemporaryDirectory(prefix="tes-postinstall-retention-") as tempdir:
        target = Path(tempdir)
        recorded: list[str] = []
        for index in range(POSTINSTALL_SENTINEL_RUN_LIMIT + 5):
            record = append_run_record(
                target,
                {
                    "schema": "tes-postinstall-run@1",
                    "version": VERSION,
                    "agent": "codex",
                    "status": "PASS",
                    "sequence": index,
                },
                dry_run=False,
            )
            recorded.append(rel(Path(record["path"]), target))
        index_payload = read_json(target / POSTINSTALL_RUN_INDEX)
        if index_payload.get("total_runs") != len(recorded):
            failures.append("postinstall run index must retain the full run count")
        if index_payload.get("runs") != recorded:
            failures.append("postinstall run index must preserve run order")
        if len(set(recorded)) != len(recorded):
            failures.append("postinstall run records must not collide within the same second")
        sentinel = sentinel_payload("codex", ["codex"], "first-session", {"runs": recorded})
        if len(sentinel.get("runs", [])) != POSTINSTALL_SENTINEL_RUN_LIMIT:
            failures.append("postinstall sentinel runs must be bounded")
        if sentinel.get("runs", [None])[0] != recorded[-POSTINSTALL_SENTINEL_RUN_LIMIT]:
            failures.append("postinstall sentinel must retain the most recent run window")

    with tempfile.TemporaryDirectory(prefix="tes-thin-install-") as tempdir:
        target = Path(tempdir)
        (target / "README.md").write_text("# Thin Installer Fixture\n\nA test project.\n", encoding="utf-8")
        (target / "package.json").write_text(
            json.dumps({"name": "tes-thin-fixture", "scripts": {"test": "echo test"}}, indent=2) + "\n",
            encoding="utf-8",
        )
        (target / "src").mkdir()
        (target / "src/app.py").write_text("print('thin')\n", encoding="utf-8")
        (target / ".claude").mkdir()
        (target / ".claude/settings.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "SessionStart": [
                            {
                                "matcher": "startup|resume",
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": "python3",
                                        "args": [
                                            "${CLAUDE_PROJECT_DIR}/.tes/bin/tes_install.py",
                                            "hook",
                                            "--agent",
                                            "claude",
                                            "--target",
                                            "${CLAUDE_PROJECT_DIR}",
                                        ],
                                        "timeout": 120,
                                    }
                                ],
                            },
                            {
                                "matcher": "compact",
                                "hooks": [{"type": "command", "command": "echo keep"}],
                            },
                        ]
                    }
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (target / LEGACY_HOOK_SENTINEL_PATH).parent.mkdir(parents=True)
        (target / LEGACY_HOOK_SENTINEL_PATH).write_text(
            json.dumps({"agent": "codex", "event": "PreToolUse", "session": "legacy", "ts": "2026-06-26T00:00:00Z"}) + "\n",
            encoding="utf-8",
        )
        (target / HOOK_SENTINEL_PATH).parent.mkdir(parents=True)
        seeded_duplicate = {
            "agent": "codex",
            "event": "PreToolUse",
            "event_canonical": "PreToolUse",
            "mode": "pretooluse",
            "session": "seeded-duplicate",
            "tool": "apply_patch",
            "path": ".tes/runtime/hook-smoke/codex/SKILL.md",
            "decision": "allow",
            "permission_decision": "allow",
            "marker_emitted": True,
            "ts": "2026-06-27T00:00:00Z",
        }
        (target / HOOK_SENTINEL_PATH).write_text(
            json.dumps(seeded_duplicate, sort_keys=True)
            + "\n"
            + json.dumps(seeded_duplicate, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        (target / ".tes/runtime/hook-smoke/codex").mkdir(parents=True)
        (target / ".tes/runtime/hook-smoke/codex/SKILL.md").write_text("# Codex Smoke\n", encoding="utf-8")
        (target / ".tes/runtime/hook-smoke/run_sim.py").write_text("print('audit residue')\n", encoding="utf-8")
        (target / ".tes/runtime/hook-smoke/forbidden-executed.txt").write_text("EXECUTED\n", encoding="utf-8")
        run(["git", "init"], cwd=target)
        install_result = run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "install",
                "--attach",
                "all",
                "--target",
                str(target),
                "--agent",
                "all",
                "--yes",
            ],
            cwd=source_root(),
        )
        if install_result.returncode != 0:
            failures.append("thin install failed")
            failures.extend(install_result.stdout.splitlines())
            failures.extend(install_result.stderr.splitlines())
        install_payload = parse_json_output(install_result.stdout)
        install_mcp = install_payload.get("mcp") if isinstance(install_payload.get("mcp"), dict) else {}
        install_legacy = install_payload.get("legacy_retirement") if isinstance(install_payload.get("legacy_retirement"), dict) else {}
        if install_legacy.get("status") != "PASS":
            failures.append("thin install must run legacy retirement before bundle apply")
        if (target / LEGACY_HOOK_SENTINEL_PATH).exists():
            failures.append("thin install must archive legacy hook ledger before certification")
        if not (target / ".tes/legacy-retirement/hooks/executed.jsonl").exists():
            failures.append("thin install must preserve archived legacy hook ledger")
        if (target / ".tes/runtime/hook-smoke/run_sim.py").exists():
            failures.append("thin install must remove legacy hook audit harness scripts")
        if (target / ".tes/runtime/hook-smoke/forbidden-executed.txt").exists():
            failures.append("thin install must remove forbidden-shell audit residue")
        if not (target / ".tes/runtime/hook-smoke/codex/SKILL.md").exists():
            failures.append("thin install must preserve hook smoke evidence files")
        seeded_records = [
            record for record in read_hook_execution_records(target, HOOK_SENTINEL_PATH)
            if record.get("session") == "seeded-duplicate"
        ]
        if len(seeded_records) != 1:
            failures.append("thin install must compact exact duplicate hook ledger rows")
        if install_mcp.get("status") != "INSTALLED":
            failures.append("thin install must report MCP status INSTALLED")
        install_certification = install_payload.get("certification") if isinstance(install_payload.get("certification"), dict) else {}
        # Ceiling (F5/F9): a fresh install's certification reports host-pending
        # NEEDS_REVIEW (MCP configured/host not restarted; hooks configured/not
        # fired; installed from an unsealed dev bundle). The install HEADLINE
        # aggregates that to READY_PENDING_HOST. Assert the ceiling-correct
        # outcome: headline READY_PENDING_HOST (or INSTALLED if already proven),
        # and every open certification finding is host-pending / release-identity
        # only (no stale gate, no real FAIL).
        if install_payload.get("status") not in {"INSTALLED", "READY_PENDING_HOST"}:
            failures.append(
                f"thin install headline must be INSTALLED or READY_PENDING_HOST, got {install_payload.get('status')}"
            )
        if install_certification.get("status") not in {"PASS", "NEEDS_REVIEW"}:
            failures.append(
                f"thin install certification must be PASS or host-pending NEEDS_REVIEW, got {install_certification.get('status')}"
            )
        if install_certification.get("status") == "NEEDS_REVIEW" and not certification_findings_are_host_pending_only(
            install_certification.get("findings", [])
        ):
            failures.append("thin install NEEDS_REVIEW must be host-pending/release-identity only, not a real defect")
        if install_mcp.get("adapters") != ["codex", "claude", "cursor"]:
            failures.append("thin install --agent all must map MCP adapters to codex, claude, cursor only")
        for relpath in (
            ".tes/bin/tes_install.py",
            ".tes/bin/cortex_runtime.py",
            ".tes/tes-install-lock.json",
            ".tes/docs/architecture/PRETOOLUSE-CONTRACT.md",
            ".tes/postinstall.json",
            ".codex/config.toml",
            ".mcp.json",
            ".cursor/mcp.json",
            ".claude/settings.json",
            ".claude/skills/tes-setup/SKILL.md",
            ".cursor/hooks.json",
            ".tes/manifest.json",
        ):
            if not (target / relpath).exists():
                failures.append(f"missing installed path: {relpath}")
        canonical_contract = source_root() / PRETOOLUSE_CONTRACT_PACKAGE_PATH
        installed_contract = target / PRETOOLUSE_CONTRACT_INSTALLED_PATH
        if canonical_contract.is_file() and installed_contract.is_file():
            canonical_hash = sha256_file(canonical_contract)
            installed_hash = sha256_file(installed_contract)
            if installed_hash != canonical_hash:
                failures.append("thin install must copy the canonical PreToolUse contract byte-for-byte")
        else:
            canonical_hash = None
        install_lock = read_json(target / LOCK_PATH)
        contract_ref = install_lock.get("pretooluse_contract") if isinstance(install_lock.get("pretooluse_contract"), dict) else {}
        expected_contract_ref = {
            "package_path": PRETOOLUSE_CONTRACT_PACKAGE_PATH.as_posix(),
            "installed_path": PRETOOLUSE_CONTRACT_INSTALLED_PATH.as_posix(),
            "version": VERSION,
        }
        for key, expected in expected_contract_ref.items():
            if contract_ref.get(key) != expected:
                failures.append(f"install lock pretooluse_contract.{key} must be {expected!r}")
        if canonical_hash and contract_ref.get("sha256") != canonical_hash:
            failures.append("install lock pretooluse_contract.sha256 must match the canonical contract")
        if (target / ".vscode/mcp.json").exists():
            failures.append("thin install --agent all must not create VS Code MCP config")
        codex_config = (target / ".codex/config.toml").read_text(encoding="utf-8") if (target / ".codex/config.toml").exists() else ""
        if "[mcp_servers.tes-cortex]" not in codex_config:
            failures.append("thin install must register Codex tes-cortex MCP server")
        if "hooks = true" not in codex_config:
            failures.append("thin install must enable Codex hooks with canonical features.hooks")
        if "codex_hooks = true" in codex_config:
            failures.append("thin install must not emit deprecated codex_hooks feature flag")
        try:
            codex_data = tomllib.loads(codex_config)
            codex_pretooluse = codex_data.get("hooks", {}).get("PreToolUse", [])
            codex_matchers = [
                group.get("matcher")
                for group in codex_pretooluse
                if isinstance(group, dict) and ".tes/bin/tes_install.py" in json.dumps(group, sort_keys=True)
            ]
            if codex_matchers != [CLAUDE_PRETOOLUSE_MATCHER]:
                failures.append(f"thin install must emit complete Codex PreToolUse matcher, got {codex_matchers!r}")
        except tomllib.TOMLDecodeError as exc:
            failures.append(f"thin install Codex config must parse as TOML: {exc}")
        for relpath, server_key in ((".mcp.json", "mcpServers"), (".cursor/mcp.json", "mcpServers")):
            data = read_json(target / relpath)
            servers = data.get(server_key) if isinstance(data.get(server_key), dict) else {}
            if "tes-cortex" not in servers:
                failures.append(f"thin install must register tes-cortex in {relpath}")

        legacy_codex_target = Path(tempdir) / "legacy-codex-matcher-target"
        (legacy_codex_target / ".codex").mkdir(parents=True)
        old_codex_command = (
            f'{python_command_token()} "$(git rev-parse --show-toplevel)/.tes/bin/tes_install.py" '
            'hook --agent codex --target "$(git rev-parse --show-toplevel)"'
        )
        (legacy_codex_target / ".codex/config.toml").write_text(
            "\n".join(
                [
                    "[features]",
                    "hooks = true",
                    "",
                    "# TES first-session post-install hook.",
                    "[[hooks.SessionStart]]",
                    'matcher = "startup|resume"',
                    "",
                    "[[hooks.SessionStart.hooks]]",
                    'type = "command"',
                    f"command = {command_literal(old_codex_command)}",
                    "timeout = 120",
                    'statusMessage = "Checking TES post-install"',
                    "",
                    "# TES PreToolUse senior-manager gate.",
                    "[[hooks.PreToolUse]]",
                    'matcher = "Write|Edit|MultiEdit"',
                    "",
                    "[[hooks.PreToolUse.hooks]]",
                    'type = "command"',
                    f"command = {command_literal(old_codex_command)}",
                    "timeout = 10",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        legacy_codex_result = install_codex_hook(legacy_codex_target, dry_run=False)
        try:
            legacy_codex = tomllib.loads((legacy_codex_target / ".codex/config.toml").read_text(encoding="utf-8"))
            legacy_pretooluse = legacy_codex.get("hooks", {}).get("PreToolUse", [])
            legacy_matchers = [
                group.get("matcher")
                for group in legacy_pretooluse
                if isinstance(group, dict) and ".tes/bin/tes_install.py" in json.dumps(group, sort_keys=True)
            ]
            if legacy_matchers != [CLAUDE_PRETOOLUSE_MATCHER]:
                failures.append(
                    "Codex hook reinstall must migrate legacy PreToolUse matcher "
                    f"(action={legacy_codex_result.get('action')!r}, matchers={legacy_matchers!r})"
                )
        except tomllib.TOMLDecodeError as exc:
            failures.append(f"Codex legacy matcher migration must keep TOML parseable: {exc}")
        legacy_config_text = (legacy_codex_target / ".codex/config.toml").read_text(encoding="utf-8")
        if "git rev-parse --show-toplevel" in legacy_config_text:
            failures.append("Codex hook reinstall must replace git rev-parse paths with target-safe paths")
        resolved_legacy = str(legacy_codex_target.resolve())
        if resolved_legacy not in legacy_config_text:
            failures.append("Codex hook reinstall must embed absolute target path")

        partial_target = Path(tempdir) / "partial-target"
        partial_target.mkdir()
        (partial_target / "docs/agents").mkdir(parents=True)
        (partial_target / "docs/agents/QUALITY-GATES.md").write_text(
            "Run `.agents/skills/tilly-engineer-skills/scripts/discipline_oracle.py`.\n",
            encoding="utf-8",
        )
        run(["git", "init"], cwd=partial_target)
        partial_install = run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "install",
                "--attach",
                "all",
                "--target",
                str(partial_target),
                "--agent",
                "all",
                "--yes",
            ],
            cwd=source_root(),
        )
        partial_payload = parse_json_output(partial_install.stdout)
        partial_mcp = partial_payload.get("mcp") if isinstance(partial_payload.get("mcp"), dict) else {}
        partial_certification = (
            partial_payload.get("certification") if isinstance(partial_payload.get("certification"), dict) else {}
        )
        if partial_mcp.get("status") != "INSTALLED":
            failures.append("partial install fixture must still install MCP")
        partial_legacy = partial_payload.get("legacy_retirement") if isinstance(partial_payload.get("legacy_retirement"), dict) else {}
        if partial_legacy.get("status") != "PASS":
            failures.append("partial install fixture must retire legacy quality-gate residue before certification")
        partial_quality = read_text(partial_target / "docs/agents/QUALITY-GATES.md")
        if STALE_DISCIPLINE_PATH in partial_quality or CANONICAL_DISCIPLINE_PATH not in partial_quality:
            failures.append("partial install fixture must migrate stale quality-gate discipline path")
        # Ceiling: after legacy retirement repairs the stale residue, the only
        # remaining open findings are host-pending / release-identity, so the
        # headline is READY_PENDING_HOST (or INSTALLED) and the certification is
        # PASS or host-pending NEEDS_REVIEW — never a stale-residue review.
        if partial_payload.get("status") not in {"INSTALLED", "READY_PENDING_HOST"}:
            failures.append(
                f"installer headline after legacy-retirement repair must be INSTALLED or READY_PENDING_HOST, got {partial_payload.get('status')}"
            )
        if partial_certification.get("status") not in {"PASS", "NEEDS_REVIEW"} or (
            partial_certification.get("status") == "NEEDS_REVIEW"
            and not certification_findings_are_host_pending_only(partial_certification.get("findings", []))
        ):
            failures.append("installer must allow clean PASS / host-pending readiness after legacy retirement repairs stale certification residue")
        sentinel = read_json(target / POSTINSTALL_PATH)
        if sentinel.get("state") != "pending":
            failures.append("postinstall sentinel must be pending after install")
        claude_settings = read_json(target / ".claude/settings.json")
        session_groups = claude_settings.get("hooks", {}).get("SessionStart", [])
        if not isinstance(session_groups, list):
            failures.append("Claude SessionStart hooks must be a list")
            session_groups = []
        matching_groups = [
            group
            for group in session_groups
            if isinstance(group, dict) and group.get("matcher") == CLAUDE_SESSIONSTART_MATCHER
        ]
        if len(matching_groups) != 1:
            failures.append("Claude hook must use the official SessionStart matcher sources")
        claude_handlers = []
        for group in matching_groups:
            handlers = group.get("hooks")
            if isinstance(handlers, list):
                claude_handlers.extend(handler for handler in handlers if isinstance(handler, dict))
        claude_tes_handlers = [handler for handler in claude_handlers if is_tes_claude_hook_entry(handler)]
        if len(claude_tes_handlers) != 2:
            failures.append("Claude hook must install notice + asyncRewake TES handlers")
        elif claude_tes_handlers != hook_entries("claude"):
            failures.append("Claude hook must use notice + asyncRewake shell command entries without args")
        if any(
            is_tes_claude_hook_entry(handler)
            for group in session_groups
            if isinstance(group, dict) and group.get("matcher") == "startup|resume"
            for handler in (group.get("hooks") if isinstance(group.get("hooks"), list) else [])
        ):
            failures.append("Claude hook migration must remove legacy startup|resume TES entries")
        if not any(
            isinstance(handler, dict) and handler.get("command") == "echo keep"
            for group in session_groups
            if isinstance(group, dict)
            for handler in (group.get("hooks") if isinstance(group.get("hooks"), list) else [])
        ):
            failures.append("Claude hook migration must preserve unrelated SessionStart hooks")
        # PreToolUse senior-manager gate (Pillar 2): installed, idempotent, correct matcher.
        pretooluse_groups = claude_settings.get("hooks", {}).get("PreToolUse", [])
        if not isinstance(pretooluse_groups, list):
            failures.append("Claude PreToolUse hooks must be a list")
            pretooluse_groups = []
        pretooluse_tes = [
            handler
            for group in pretooluse_groups
            if isinstance(group, dict) and group.get("matcher") == CLAUDE_PRETOOLUSE_MATCHER
            for handler in (group.get("hooks") if isinstance(group.get("hooks"), list) else [])
            if is_tes_claude_hook_entry(handler)
        ]
        if len(pretooluse_tes) != 1:
            failures.append(
                f"Claude PreToolUse gate must install exactly one TES handler, got {len(pretooluse_tes)} "
                "(idempotency: reinstall must not duplicate)"
            )
        start_notice = run(
            [
                sys.executable,
                str(target / ".tes/bin/tes_install.py"),
                "hook",
                "--agent",
                "claude",
                "--target",
                str(target),
                "--announce-start",
            ],
            cwd=target,
            input=json.dumps({"hook_event_name": "SessionStart", "source": "startup", "cwd": str(target)}),
        )
        if start_notice.returncode != 0:
            failures.append("Claude start notice hook failed")
            failures.extend(start_notice.stdout.splitlines())
            failures.extend(start_notice.stderr.splitlines())
        try:
            start_payload = json.loads(start_notice.stdout)
        except json.JSONDecodeError:
            start_payload = {}
            failures.append("Claude start notice hook must return structured JSON")
        if start_payload.get("systemMessage") != CLAUDE_SETUP_RUNNING_MESSAGE:
            failures.append("Claude start notice must show the visible running message")
        start_context = start_payload.get("hookSpecificOutput") if isinstance(start_payload, dict) else None
        if not isinstance(start_context, dict) or start_context.get("hookEventName") != "SessionStart":
            failures.append("Claude start notice must include SessionStart hook context")
        sentinel = read_json(target / POSTINSTALL_PATH)
        if sentinel.get("state") != "pending":
            failures.append("Claude start notice must not run postinstall")
        hook_result = run(
            [
                sys.executable,
                str(target / ".tes/bin/tes_install.py"),
                "hook",
                "--agent",
                "codex",
                "--target",
                str(target),
            ],
            cwd=target,
        )
        if hook_result.returncode != 0:
            failures.append("first hook postinstall failed")
            failures.extend(hook_result.stdout.splitlines())
            failures.extend(hook_result.stderr.splitlines())
        sentinel = read_json(target / POSTINSTALL_PATH)
        if sentinel.get("state") != "complete":
            failures.append("postinstall sentinel must be complete after hook")
        # Ceiling: after the hook fires from a host-pending install (MCP host not
        # restarted; unsealed dev bundle), postinstall completes as
        # READY_PENDING_HOST — the terminal ceiling success — not PASS. (It records
        # PASS only when the host has actually proven the surfaces.)
        if sentinel.get("last_status") not in {"PASS", "READY_PENDING_HOST"}:
            failures.append(
                f"postinstall sentinel must record PASS or READY_PENDING_HOST after hook, got {sentinel.get('last_status')}"
            )
        if sentinel.get("agents") != list(AGENTS):
            failures.append("postinstall sentinel must preserve the installed multi-agent scope after host-specific execution")
        if sentinel.get("requested_by") != "all":
            failures.append("postinstall sentinel must preserve the original install request scope")
        if sentinel.get("executed_by") != "codex":
            failures.append("postinstall sentinel must record the host that executed postinstall separately")
        last_run = sentinel.get("last_run")
        if isinstance(last_run, str) and (target / last_run).exists():
            run_record = read_json(target / last_run)
            run_mcp = run_record.get("mcp") if isinstance(run_record.get("mcp"), dict) else {}
            if run_mcp.get("status") != "INSTALLED":
                failures.append("postinstall run record must include MCP status INSTALLED")
        else:
            failures.append("postinstall sentinel must point to an existing run record")
        for relpath in (
            "docs/agents/PROJECT-CONTEXT.md",
            "docs/agents/PROJECT-REGISTER.md",
            "docs/agents/QUALITY-GATES.md",
        ):
            if not (target / relpath).exists():
                failures.append(f"postinstall missing path: {relpath}")
        mesh_path = target / "docs/agents/PROJECT-STATE.md"
        mesh_relpaths = (
            "docs/agents/PROJECT-STATE.md",
            "docs/agents/PROJECT-ROADMAP.md",
            "docs/agents/EXECUTION-LINE.md",
            "docs/agents/QUALITY-GATES.md",
        )
        mesh_before = {
            relpath: ((target / relpath).read_text(encoding="utf-8") if (target / relpath).exists() else None)
            for relpath in mesh_relpaths
        }
        claude_mesh = run(
            [
                sys.executable,
                str(target / ".tes/bin/tes_install.py"),
                "hook",
                "--agent",
                "claude",
                "--target",
                str(target),
            ],
            cwd=target,
            input=json.dumps(
                {
                    "hook_event_name": "PreToolUse",
                    "session_id": "cortex-claude-mesh",
                    "tool_name": "Edit",
                    "tool_input": {
                        "file_path": str(mesh_path),
                        "old_string": "Fixture baseline.",
                        "new_string": "Fixture updated.",
                    },
                }
            ),
        )
        if claude_mesh.returncode != 0:
            failures.append(f"Claude Cortex PreToolUse mesh advisory must allow, got {claude_mesh.returncode}")
        try:
            claude_mesh_payload = json.loads(claude_mesh.stdout)
        except json.JSONDecodeError:
            claude_mesh_payload = {}
            failures.append("Claude Cortex PreToolUse mesh advisory must emit JSON")
        claude_specific = claude_mesh_payload.get("hookSpecificOutput") if isinstance(claude_mesh_payload, dict) else {}
        claude_context = claude_specific.get("additionalContext") if isinstance(claude_specific, dict) else None
        if not isinstance(claude_context, str) or "NEEDS_ALIGN" not in claude_context:
            failures.append("Claude Cortex PreToolUse mesh advisory must surface NEEDS_ALIGN additionalContext")
        if isinstance(claude_specific, dict) and claude_specific.get("permissionDecision") != "allow":
            failures.append("Claude Cortex PreToolUse mesh advisory must keep permissionDecision allow")

        codex_mesh = run(
            [
                sys.executable,
                str(target / ".tes/bin/tes_install.py"),
                "hook",
                "--agent",
                "codex",
                "--target",
                str(target),
            ],
            cwd=target,
            input=json.dumps(
                {
                    "hookEventName": "PreToolUse",
                    "sessionId": "cortex-codex-mesh",
                    "toolName": "apply_patch",
                    "toolInput": {
                        "command": (
                            "*** Begin Patch\n"
                            "*** Update File: docs/agents/PROJECT-STATE.md\n"
                            "@@\n"
                            "-Fixture baseline.\n"
                            "+Fixture updated.\n"
                            "*** End Patch\n"
                        )
                    },
                }
            ),
        )
        if codex_mesh.returncode != 0:
            failures.append(f"Codex Cortex PreToolUse mesh advisory must allow, got {codex_mesh.returncode}")
        if "NEEDS_ALIGN" not in codex_mesh.stderr or codex_mesh.stdout.strip():
            failures.append("Codex Cortex PreToolUse mesh advisory must surface NEEDS_ALIGN on stderr only")

        cursor_mesh = run(
            [
                sys.executable,
                str(target / ".tes/bin/tes_install.py"),
                "hook",
                "--agent",
                "cursor",
                "--target",
                str(target),
            ],
            cwd=target,
            input=json.dumps(
                {
                    "hook_event_name": "preToolUse",
                    "session_id": "cortex-cursor-mesh",
                    "tool_name": "Write",
                    "tool_input": {"file_path": str(mesh_path), "content": "Fixture updated."},
                }
            ),
        )
        if cursor_mesh.returncode != 0:
            failures.append(f"Cursor Cortex PreToolUse mesh advisory must allow with exit 0, got {cursor_mesh.returncode}")
        try:
            cursor_mesh_payload = json.loads(cursor_mesh.stdout)
        except json.JSONDecodeError:
            cursor_mesh_payload = {}
            failures.append("Cursor Cortex PreToolUse mesh advisory must emit native JSON")
        if cursor_mesh_payload.get("permission") != "allow" or cursor_mesh_payload.get("continue") is not True:
            failures.append("Cursor Cortex PreToolUse mesh advisory must use native allow/continue output")
        if "hookSpecificOutput" in cursor_mesh_payload:
            failures.append("Cursor Cortex PreToolUse mesh advisory must not use Claude/Codex JSON fields")
        if "NEEDS_ALIGN" not in str(cursor_mesh_payload.get("agent_message") or ""):
            failures.append("Cursor Cortex PreToolUse mesh advisory must surface NEEDS_ALIGN in native context")
        hook_records: list[dict[str, Any]] = []
        hook_sentinel = target / HOOK_SENTINEL_PATH
        if hook_sentinel.exists():
            for line in hook_sentinel.read_text(encoding="utf-8").splitlines():
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict):
                    hook_records.append(record)
        cursor_records = [
            record for record in hook_records
            if record.get("agent") == "cursor" and record.get("session") == "cortex-cursor-mesh"
        ]
        if not cursor_records:
            failures.append("Cursor PreToolUse must record runtime hook execution in the ignored sentinel")
        else:
            cursor_record = cursor_records[-1]
            if cursor_record.get("event") != "preToolUse" or cursor_record.get("event_canonical") != "PreToolUse":
                failures.append("Cursor PreToolUse sentinel must preserve host event and canonical event")
            if cursor_record.get("mode") != "pretooluse":
                failures.append("Cursor PreToolUse sentinel must record mode=pretooluse")
            if cursor_record.get("tool") != "Write" or str(cursor_record.get("path") or "") != str(mesh_path):
                failures.append("Cursor PreToolUse sentinel must record tool and path details")
            reason_codes = cursor_record.get("reason_codes") if isinstance(cursor_record.get("reason_codes"), list) else []
            if "cortex_advisory_no_write" not in reason_codes:
                failures.append("Cursor PreToolUse Cortex row must persist cortex_advisory_no_write reason code")

        dedupe_input = {
            "hook_event_name": "PreToolUse",
            "session_id": "dedupe-routine",
            "tool_name": "Read",
            "tool_use_id": "dedupe-routine-tool",
            "tool_input": {"file_path": "src/app.py"},
        }
        dedupe_decision = {
            "risk": "routine",
            "block": False,
            "decision": "allow",
            "permission_decision": "allow",
            "marker_emitted": False,
            "context_suppressed": False,
            "cortex_context_emitted": False,
            "surface_context": False,
        }
        record_hook_execution(target, "cursor", dedupe_input, mode="pretooluse", pretooluse_decision=dedupe_decision)
        record_hook_execution(target, "cursor", dedupe_input, mode="pretooluse", pretooluse_decision=dedupe_decision)
        dedupe_records = [
            record for record in read_hook_execution_records(target, HOOK_SENTINEL_PATH)
            if record.get("agent") == "cursor" and record.get("session") == "dedupe-routine"
        ]
        if len(dedupe_records) != 1:
            failures.append("runtime hook ledger must skip exact duplicate PreToolUse records")

        synthetic_invocation_input = {
            "hook_event_name": "PreToolUse",
            "session_id": "synthetic-invocation",
            "tool_name": "Read",
            "tool_input": {"file_path": "src/app.py"},
        }
        record_hook_execution(
            target,
            "codex",
            synthetic_invocation_input,
            mode="pretooluse",
            pretooluse_decision=dedupe_decision,
        )
        synthetic_invocation_records = [
            record for record in read_hook_execution_records(target, HOOK_SENTINEL_PATH)
            if record.get("agent") == "codex" and record.get("session") == "synthetic-invocation"
        ]
        if len(synthetic_invocation_records) != 1:
            failures.append("runtime hook ledger must record the synthetic invocation fixture")
        elif not str(synthetic_invocation_records[0].get("invocation") or "").startswith(
            "synthetic:codex:synthetic-invocation:Read:"
        ):
            failures.append("runtime hook ledger must stamp a stable synthetic invocation when hosts omit tool ids")

        anti_input = {
            "hook_event_name": "PreToolUse",
            "session_id": "dedupe-anti-cry-wolf",
            "tool_name": "Write",
            "tool_use_id": "dedupe-anti-tool",
            "tool_input": {"file_path": ".tes/runtime/hook-smoke/dedupe/SKILL.md"},
        }
        first_anti = {**dedupe_decision, "risk": "material", "marker_emitted": True, "surface_context": True}
        second_anti = {**dedupe_decision, "risk": "material", "context_suppressed": True}
        record_hook_execution(target, "cursor", anti_input, mode="pretooluse", pretooluse_decision=first_anti)
        record_hook_execution(target, "cursor", anti_input, mode="pretooluse", pretooluse_decision=second_anti)
        anti_records = [
            record for record in read_hook_execution_records(target, HOOK_SENTINEL_PATH)
            if record.get("agent") == "cursor" and record.get("session") == "dedupe-anti-cry-wolf"
        ]
        if len(anti_records) != 2:
            failures.append("runtime hook ledger must preserve anti-cry-wolf decision changes")
        redaction_input = {
            "hook_event_name": "PreToolUse",
            "session_id": "ledger-redaction",
            "tool_name": "Bash",
            "tool_use_id": "ledger-redaction-tool",
            "tool_input": {"command": "git push --force origin main"},
        }
        redaction_decision = {
            **dedupe_decision,
            "risk": "forbidden",
            "block": True,
            "reason_codes": ["forbidden_class"],
            "decision": "block",
            "permission_decision": "deny",
            "marker_emitted": True,
            "surface_context": True,
        }
        record_hook_execution(target, "codex", redaction_input, mode="pretooluse", pretooluse_decision=redaction_decision)
        redaction_records = [
            record for record in read_hook_execution_records(target, HOOK_SENTINEL_PATH)
            if record.get("agent") == "codex" and record.get("session") == "ledger-redaction"
        ]
        if len(redaction_records) != 1:
            failures.append("runtime hook ledger must record the PreToolUse redaction fixture")
        else:
            redaction_record = redaction_records[0]
            if "command" in redaction_record:
                failures.append("runtime hook ledger must not persist raw PreToolUse command text")
            if redaction_record.get("command_category") != "forbidden_git_force_push":
                failures.append("runtime hook ledger must persist a redacted command_category")
            if redaction_record.get("schema_version") != "pretooluse_decision@2":
                failures.append("runtime hook ledger must identify the pretooluse_decision@2 schema")
            if redaction_record.get("command_redacted") is not True:
                failures.append("runtime hook ledger must mark command text as redacted")
        codex_discoverability = run(
            [
                sys.executable,
                str(target / ".tes/bin/tes_install.py"),
                "hook",
                "--agent",
                "codex",
                "--target",
                str(target),
            ],
            cwd=target,
            input=json.dumps(
                {
                    "hookEventName": "PreToolUse",
                    "sessionId": "hook-health-discoverability",
                    "toolName": "PatchFile",
                    "toolInput": {"filePath": "docs/adr/0010-future.md"},
                }
            ),
        )
        if codex_discoverability.returncode != 0 or codex_discoverability.stdout.strip():
            failures.append("hook-health discoverability fixture must allow with stderr context only")
        if (
            "outcome=needs_discoverability" not in codex_discoverability.stderr
            or "risk=needs-discoverability" not in codex_discoverability.stderr
        ):
            failures.append("hook-health discoverability fixture must surface installed discoverability output")
        if (target / LEGACY_HOOK_SENTINEL_PATH).exists():
            failures.append("new hook runtime must not write the legacy tracked hook sentinel")
        ignore_probe = run(["git", "check-ignore", HOOK_SENTINEL_PATH.as_posix()], cwd=target)
        if ignore_probe.returncode != 0:
            failures.append("hook runtime sentinel must be excluded from target git status")
        for cursor_event in ("sessionStart", "beforeSubmitPrompt"):
            cursor_lifecycle = run(
                [
                    sys.executable,
                    str(target / ".tes/bin/tes_install.py"),
                    "hook",
                    "--agent",
                    "cursor",
                    "--target",
                    str(target),
                ],
                cwd=target,
                input=json.dumps(
                    {
                        "hook_event_name": cursor_event,
                        "session_id": f"health-{cursor_event}",
                        "cwd": str(target),
                    }
                ),
            )
            if cursor_lifecycle.returncode != 0:
                failures.append(f"Cursor {cursor_event} hook-health fixture must allow")
                failures.extend(cursor_lifecycle.stdout.splitlines())
                failures.extend(cursor_lifecycle.stderr.splitlines())
        hook_health_result = run(
            [
                sys.executable,
                str(target / ".tes/bin/tes_install.py"),
                "hook-health",
                "--target",
                str(target),
                "--json-only",
            ],
            cwd=target,
        )
        if hook_health_result.returncode != 0:
            failures.append("hook-health must pass when configured host events have runtime evidence")
            failures.extend(hook_health_result.stdout.splitlines())
            failures.extend(hook_health_result.stderr.splitlines())
        hook_health_payload_result = parse_json_output(hook_health_result.stdout)
        if hook_health_payload_result.get("schema") != HOOK_HEALTH_SCHEMA_VERSION:
            failures.append("hook-health must report tes-hook-health@2 schema")
        if hook_health_payload_result.get("legacy_schema") != HOOK_HEALTH_LEGACY_SCHEMA_VERSION:
            failures.append("hook-health must preserve the v1 schema migration marker")
        if hook_health_payload_result.get("status") != "PASS":
            failures.append(f"hook-health complete fixture must report PASS, got {hook_health_payload_result.get('status')}")
        if hook_health_payload_result.get("floor_status") != "PASS_BASIC":
            failures.append(
                f"hook-health complete fixture must report floor_status=PASS_BASIC, got {hook_health_payload_result.get('floor_status')}"
            )
        if hook_health_payload_result.get("helper_contract_status") != "PASS":
            failures.append(
                "hook-health complete fixture must report helper_contract_status=PASS from installed .tes/bin helpers"
            )
        if hook_health_payload_result.get("discoverability_status") != "NEEDS_DISCOVERABILITY":
            failures.append(
                "hook-health complete fixture must report discoverability_status=NEEDS_DISCOVERABILITY from installed ledger evidence"
            )
        if hook_health_payload_result.get("ceiling_status") == "PASS_CEILING":
            failures.append("hook-health must not report PASS_CEILING while ADR 0009 ceiling evidence is incomplete")
        ceiling_gaps = hook_health_payload_result.get("ceiling_gaps")
        if not isinstance(ceiling_gaps, list) or not ceiling_gaps:
            failures.append("hook-health must list ceiling_gaps when ceiling_status is not PASS_CEILING")
        ceiling_scope = hook_health_payload_result.get("ceiling_evidence_scope")
        ceiling_scope = ceiling_scope if isinstance(ceiling_scope, dict) else {}
        if ceiling_scope.get("schema_version") != PRETOOLUSE_LEDGER_SCHEMA_VERSION:
            failures.append("hook-health must expose the PreToolUse ceiling evidence schema version")
        if ceiling_scope.get("aggregation_policy") != PRETOOLUSE_CEILING_AGGREGATION_POLICY:
            failures.append("hook-health must expose per-host no-cross-fill ceiling aggregation")
        if ceiling_scope.get("legacy_policy") != PRETOOLUSE_LEGACY_POLICY:
            failures.append("hook-health must expose historical-only legacy ceiling policy")
        if ceiling_scope.get("current_host") is not None:
            failures.append("hook-health all-host scope must expose current_host=null")
        if ceiling_scope.get("required_hosts") != list(PRETOOLUSE_CEILING_HOST_ORDER):
            failures.append(f"hook-health all-host scope must require all installed hosts, got {ceiling_scope.get('required_hosts')!r}")
        per_host_scope = ceiling_scope.get("per_host") if isinstance(ceiling_scope.get("per_host"), dict) else {}
        for agent in AGENTS:
            entry = per_host_scope.get(agent) if isinstance(per_host_scope.get(agent), dict) else {}
            for field in (
                "agent",
                "native_evidence",
                "considered_records",
                "ignored_legacy_records",
                "oldest_considered_ts",
                "newest_considered_ts",
                "status",
            ):
                if field not in entry:
                    failures.append(f"hook-health ceiling evidence scope must expose {agent}.{field}")
        hook_health_claude_result = run(
            [
                sys.executable,
                str(target / ".tes/bin/tes_install.py"),
                "hook-health",
                "--target",
                str(target),
                "--json-only",
                "--agent",
                "claude",
            ],
            cwd=target,
        )
        if hook_health_claude_result.returncode != 0:
            failures.append("hook-health --agent claude must pass when current-host evidence exists")
            failures.extend(hook_health_claude_result.stdout.splitlines())
            failures.extend(hook_health_claude_result.stderr.splitlines())
        hook_health_claude_payload = parse_json_output(hook_health_claude_result.stdout)
        claude_scope = hook_health_claude_payload.get("ceiling_evidence_scope")
        claude_scope = claude_scope if isinstance(claude_scope, dict) else {}
        if claude_scope.get("claim_scope") != "current_host":
            failures.append("hook-health --agent must scope ceiling_evidence_scope.claim_scope=current_host")
        if claude_scope.get("current_host") != "claude":
            failures.append("hook-health --agent claude must expose ceiling_evidence_scope.current_host=claude")
        if claude_scope.get("required_hosts") != ["claude"]:
            failures.append(
                f"hook-health --agent claude must require only claude evidence, got {claude_scope.get('required_hosts')!r}"
            )
        claude_per_host = claude_scope.get("per_host") if isinstance(claude_scope.get("per_host"), dict) else {}
        if sorted(claude_per_host) != ["claude"]:
            failures.append("hook-health --agent claude must expose only claude per-host ceiling evidence")
        dedupe_contract = hook_health_payload_result.get("dedupe_contract")
        dedupe_contract = dedupe_contract if isinstance(dedupe_contract, dict) else {}
        dedupe_fields = dedupe_contract.get("fields") if isinstance(dedupe_contract.get("fields"), list) else []
        if dedupe_contract.get("schema") != "tes-hook-dedupe@1":
            failures.append("hook-health must expose the v2 ledger dedupe analytics contract")
        if (
            dedupe_contract.get("ceiling_noise_rule")
            != "historical_duplicate_replay_and_cursor_batch_noise_is_non_blocking_without_current_v2_contradiction"
        ):
            failures.append("hook-health dedupe contract must expose the non-blocking ceiling noise rule")
        if (
            dedupe_contract.get("current_v2_contradiction_rule")
            != "same_host_scope_unexplained_decision_risk_renderer_redaction_marker_contradiction_blocks_ceiling"
        ):
            failures.append("hook-health dedupe contract must expose the scoped current v2 contradiction rule")
        for field in ("agent", "tool", "risk", "path", "command_category", "session", "mode", "marker_emitted"):
            if field not in dedupe_fields:
                failures.append(f"hook-health dedupe contract must include {field}")
        health_agents = hook_health_payload_result.get("agents") if isinstance(hook_health_payload_result.get("agents"), dict) else {}
        for agent, expected_events in {
            "codex": ("SessionStart", "PreToolUse"),
            "claude": ("SessionStart", "PreToolUse"),
            "cursor": ("sessionStart", "beforeSubmitPrompt", "preToolUse"),
        }.items():
            agent_payload = health_agents.get(agent) if isinstance(health_agents.get(agent), dict) else {}
            events = agent_payload.get("events") if isinstance(agent_payload.get("events"), list) else []
            states = {
                str(item.get("event")): str(item.get("state"))
                for item in events
                if isinstance(item, dict)
            }
            for event in expected_events:
                if states.get(event) != "OBSERVED":
                    failures.append(f"hook-health must report {agent} {event} OBSERVED, got {states.get(event)}")

        benign_mesh = run(
            [
                sys.executable,
                str(target / ".tes/bin/tes_install.py"),
                "hook",
                "--agent",
                "codex",
                "--target",
                str(target),
            ],
            cwd=target,
            input=json.dumps(
                {
                    "hook_event_name": "PreToolUse",
                    "session_id": "cortex-codex-benign",
                    "tool_name": "Edit",
                    "tool_input": {"file_path": str(target / "src/app.py"), "new_string": "print('thin')"},
                }
            ),
        )
        if benign_mesh.returncode != 0 or benign_mesh.stdout.strip() or benign_mesh.stderr.strip():
            failures.append("benign non-mesh Cortex PreToolUse path must remain quiet/allow for Codex")
        mesh_after = {
            relpath: ((target / relpath).read_text(encoding="utf-8") if (target / relpath).exists() else None)
            for relpath in mesh_relpaths
        }
        if mesh_after != mesh_before:
            failures.append("Cortex PreToolUse advisory must not write operating mesh files")
        configured_only_target = target / "configured-only-health"
        configured_only_target.mkdir()
        run(["git", "init"], cwd=configured_only_target)
        (configured_only_target / ".codex").mkdir()
        (configured_only_target / ".codex/config.toml").write_text(
            '[features]\nhooks = true\n\n[[hooks.SessionStart]]\ncommand = "python3 .tes/bin/tes_install.py hook --agent codex --target ."\n',
            encoding="utf-8",
        )
        configured_only_health = run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "hook-health",
                "--target",
                str(configured_only_target),
                "--json-only",
            ],
            cwd=source_root(),
        )
        configured_only_payload = parse_json_output(configured_only_health.stdout)
        if configured_only_health.returncode != 0 or configured_only_payload.get("status") != "NEEDS_EVIDENCE":
            failures.append("hook-health must keep configured-only hooks as NEEDS_EVIDENCE with exit 0")
        if configured_only_payload.get("floor_status") != "NEEDS_EVIDENCE":
            failures.append("hook-health configured-only fixture must report floor_status=NEEDS_EVIDENCE")
        if configured_only_payload.get("ceiling_status") != "NEEDS_FLOOR":
            failures.append("hook-health configured-only fixture must report ceiling_status=NEEDS_FLOOR")
        if configured_only_payload.get("helper_contract_status") != "MISSING":
            failures.append("hook-health configured-only fixture must not fill helper_contract_status from source imports")
        if configured_only_payload.get("discoverability_status") != "MISSING":
            failures.append("hook-health configured-only fixture must explicitly report missing discoverability evidence")
        # Ceiling F23 red-capable proof: the SAME configured-only fixture
        # (NEEDS_EVIDENCE) must keep exit 0 in default/query mode but exit
        # non-zero under --gate, so a shell caller's exit code can never certify
        # success where the JSON reports missing proof.
        configured_only_gate = run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "hook-health",
                "--target",
                str(configured_only_target),
                "--json-only",
                "--gate",
            ],
            cwd=source_root(),
        )
        if configured_only_gate.returncode == 0:
            failures.append("hook-health --gate must exit non-zero on NEEDS_EVIDENCE (F23)")
        configured_only_query = run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "hook-health",
                "--target",
                str(configured_only_target),
                "--json-only",
                "--query",
            ],
            cwd=source_root(),
        )
        if configured_only_query.returncode != 0:
            failures.append("hook-health --query must exit 0 on NEEDS_EVIDENCE (F23 back-compat)")
        duplicate_health_target = target / "duplicate-health"
        duplicate_health_target.mkdir()
        run(["git", "init"], cwd=duplicate_health_target)
        (duplicate_health_target / ".codex").mkdir()
        (duplicate_health_target / ".codex/config.toml").write_text(
            '[features]\nhooks = true\n\n[[hooks.SessionStart]]\ncommand = "python3 .tes/bin/tes_install.py hook --agent codex --target ."\n',
            encoding="utf-8",
        )
        duplicate_sentinel = duplicate_health_target / HOOK_SENTINEL_PATH
        duplicate_sentinel.parent.mkdir(parents=True)
        duplicate_record = {
            "agent": "codex",
            "event": "SessionStart",
            "event_canonical": "SessionStart",
            "mode": "session_start",
            "session": "dup",
            "ts": utc_stamp(),
        }
        duplicate_sentinel.write_text(
            json.dumps(duplicate_record, sort_keys=True) + "\n" + json.dumps(duplicate_record, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        duplicate_health = run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "hook-health",
                "--target",
                str(duplicate_health_target),
                "--json-only",
            ],
            cwd=source_root(),
        )
        duplicate_payload = parse_json_output(duplicate_health.stdout)
        if duplicate_health.returncode != 0 or duplicate_payload.get("status") != "PASS_WITH_FINDINGS":
            failures.append("hook-health must keep duplicate runtime hook records as non-blocking findings")
        duplicate_findings = duplicate_payload.get("findings") if isinstance(duplicate_payload.get("findings"), list) else []
        if not any(
            isinstance(finding, dict) and finding.get("type") == "duplicate_runtime_hook_records"
            for finding in duplicate_findings
        ):
            failures.append("hook-health duplicate fixture must report duplicate_runtime_hook_records finding")
        if not any(
            isinstance(finding, dict)
            and finding.get("type") == "duplicate_runtime_hook_records"
            and isinstance(finding.get("dedupe_fields"), list)
            and "tool" in finding.get("dedupe_fields", [])
            and "risk" in finding.get("dedupe_fields", [])
            and isinstance(finding.get("records"), list)
            and finding["records"]
            and isinstance(finding["records"][0], dict)
            and finding["records"][0].get("identity", {}).get("session") == "dup"
            for finding in duplicate_findings
        ):
            failures.append("hook-health duplicate finding must include diagnostic dedupe fields and record identity")
        replay_health_target = target / "replay-health"
        replay_health_target.mkdir()
        run(["git", "init"], cwd=replay_health_target)
        (replay_health_target / ".codex").mkdir()
        (replay_health_target / ".codex/config.toml").write_text(
            '[features]\nhooks = true\n\n[[hooks.SessionStart]]\ncommand = "python3 .tes/bin/tes_install.py hook --agent codex --target ."\n',
            encoding="utf-8",
        )
        replay_sentinel = replay_health_target / HOOK_SENTINEL_PATH
        replay_sentinel.parent.mkdir(parents=True)
        replay_first = {**duplicate_record, "session": "replay", "ts": "2026-06-27T00:00:00Z"}
        replay_second = {**duplicate_record, "session": "replay", "ts": "2026-06-27T00:05:00Z"}
        replay_sentinel.write_text(
            json.dumps(replay_first, sort_keys=True) + "\n" + json.dumps(replay_second, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        replay_health = run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "hook-health",
                "--target",
                str(replay_health_target),
                "--json-only",
            ],
            cwd=source_root(),
        )
        replay_payload = parse_json_output(replay_health.stdout)
        replay_findings = replay_payload.get("findings") if isinstance(replay_payload.get("findings"), list) else []
        if replay_health.returncode != 0 or replay_payload.get("status") != "PASS":
            failures.append("hook-health must treat same semantic record with different timestamps as replay history")
        if any(
            isinstance(finding, dict) and finding.get("type") == "duplicate_runtime_hook_records"
            for finding in replay_findings
        ):
            failures.append("hook-health must not report replayed historical records as duplicate runtime hooks")
        cursor_batch_target = target / "cursor-batch-health"
        cursor_batch_target.mkdir()
        run(["git", "init"], cwd=cursor_batch_target)
        (cursor_batch_target / ".cursor").mkdir()
        (cursor_batch_target / ".cursor/hooks.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "preToolUse": [
                            {
                                "command": "python3 .tes/bin/tes_install.py hook --agent cursor --target .",
                            }
                        ]
                    }
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        cursor_batch_sentinel = cursor_batch_target / HOOK_SENTINEL_PATH
        cursor_batch_sentinel.parent.mkdir(parents=True)
        cursor_batch_base = {
            "agent": "cursor",
            "event": "preToolUse",
            "event_canonical": "PreToolUse",
            "mode": "pretooluse",
            "schema_version": PRETOOLUSE_LEDGER_SCHEMA_VERSION,
            "session": "cursor-batch",
            "invocation": "cursor-batch-invocation",
            "ts": "2026-06-27T00:10:00Z",
            "risk": "material",
            "decision": "allow",
            "permission_decision": "allow",
            "marker_emitted": True,
        }
        cursor_batch_first = {**cursor_batch_base, "tool": "Write", "path": ".cursor/rules/a.mdc"}
        cursor_batch_second = {**cursor_batch_base, "tool": "MultiEdit", "path": ".cursor/rules/b.mdc"}
        cursor_batch_sentinel.write_text(
            json.dumps(cursor_batch_first, sort_keys=True)
            + "\n"
            + json.dumps(cursor_batch_second, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        cursor_batch_health = run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "hook-health",
                "--target",
                str(cursor_batch_target),
                "--json-only",
            ],
            cwd=source_root(),
        )
        cursor_batch_payload = parse_json_output(cursor_batch_health.stdout)
        cursor_batch_findings = cursor_batch_payload.get("findings") if isinstance(cursor_batch_payload.get("findings"), list) else []
        if cursor_batch_health.returncode != 0 or cursor_batch_payload.get("status") != "PASS":
            failures.append("hook-health must not collapse distinct Cursor batch records into duplicates")
        if any(
            isinstance(finding, dict) and finding.get("type") == "duplicate_runtime_hook_records"
            for finding in cursor_batch_findings
        ):
            failures.append("Cursor batch rows with different tool/path/risk/marker fields must not be duplicate findings")
        unexpected_health_target = target / "unexpected-health"
        unexpected_health_target.mkdir()
        run(["git", "init"], cwd=unexpected_health_target)
        unexpected_sentinel = unexpected_health_target / HOOK_SENTINEL_PATH
        unexpected_sentinel.parent.mkdir(parents=True)
        unexpected_sentinel.write_text(json.dumps(duplicate_record, sort_keys=True) + "\n", encoding="utf-8")
        unexpected_health = run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "hook-health",
                "--target",
                str(unexpected_health_target),
                "--json-only",
            ],
            cwd=source_root(),
        )
        unexpected_payload = parse_json_output(unexpected_health.stdout)
        if unexpected_health.returncode == 0 or unexpected_payload.get("status") != "DEGRADED":
            failures.append("hook-health must degrade runtime records observed without matching config")
        second_hook = run(
            [
                sys.executable,
                str(target / ".tes/bin/tes_install.py"),
                "hook",
                "--agent",
                "claude",
                "--target",
                str(target),
            ],
            cwd=target,
        )
        if second_hook.returncode != 0:
            failures.append("idempotent hook retry failed")
            failures.extend(second_hook.stdout.splitlines())
            failures.extend(second_hook.stderr.splitlines())
        try:
            claude_hook_payload = json.loads(second_hook.stdout)
        except json.JSONDecodeError:
            claude_hook_payload = {}
            failures.append("Claude hook retry must return structured hook JSON")
        hook_specific = claude_hook_payload.get("hookSpecificOutput") if isinstance(claude_hook_payload, dict) else None
        if not isinstance(hook_specific, dict):
            failures.append("Claude hook output must include hookSpecificOutput")
        else:
            if hook_specific.get("hookEventName") != "SessionStart":
                failures.append("Claude hook output must name SessionStart")
            context = hook_specific.get("additionalContext")
            if not isinstance(context, str) or "TES SessionStart hook ran" not in context:
                failures.append("Claude hook output must pass concise additionalContext")
            if isinstance(context, str) and '"commands"' in context:
                failures.append("Claude hook additionalContext must not leak raw postinstall JSON")
        if "systemMessage" in claude_hook_payload:
            failures.append("Claude idempotent hook retry must stay quiet after postinstall is complete")

        recovery_sentinel = {
            **read_json(target / POSTINSTALL_PATH),
            "state": "needs_review",
            "last_status": "NEEDS_REVIEW",
            "completed_at": None,
            "failures": [{"command": "fixture", "returncode": 1, "stderr": "fixture blocker repaired"}],
        }
        write_json(target / POSTINSTALL_PATH, recovery_sentinel)
        recovery_result = run(
            [
                sys.executable,
                str(target / ".tes/bin/tes_install.py"),
                "postinstall",
                "--agent",
                "codex",
                "--target",
                str(target),
                "--recover-needs-review",
            ],
            cwd=target,
        )
        if recovery_result.returncode != 0:
            failures.append("needs_review recovery postinstall failed")
            failures.extend(recovery_result.stdout.splitlines())
            failures.extend(recovery_result.stderr.splitlines())
        recovered_sentinel = read_json(target / POSTINSTALL_PATH)
        if recovered_sentinel.get("state") != "complete":
            failures.append("needs_review recovery must clear the postinstall sentinel")
        # Ceiling: recovery re-certifies; the synthetic blocker is gone, so the
        # only remaining findings are host-pending/release-identity and recovery
        # completes as READY_PENDING_HOST (or PASS if the host has proven itself).
        if recovered_sentinel.get("last_status") not in {"PASS", "READY_PENDING_HOST"}:
            failures.append(
                f"needs_review recovery must record PASS or READY_PENDING_HOST, got {recovered_sentinel.get('last_status')}"
            )
        if recovered_sentinel.get("recovery") != "needs_review":
            failures.append("needs_review recovery must record recovery mode")
        if "failures" in recovered_sentinel:
            failures.append("needs_review recovery must clear stale failure records after PASS")
        recovery_skip = run(
            [
                sys.executable,
                str(target / ".tes/bin/tes_install.py"),
                "postinstall",
                "--agent",
                "codex",
                "--target",
                str(target),
                "--recover-needs-review",
            ],
            cwd=target,
        )
        if recovery_skip.returncode != 0 or "postinstall recovery only runs when the sentinel is needs_review" not in recovery_skip.stdout:
            failures.append("needs_review recovery must skip clean sentinels")
            failures.extend(recovery_skip.stdout.splitlines())
            failures.extend(recovery_skip.stderr.splitlines())

        with tempfile.TemporaryDirectory(prefix="tes-thin-install-claude-") as claude_tempdir:
            claude_target = Path(claude_tempdir)
            (claude_target / "README.md").write_text("# Claude Hook Fixture\n", encoding="utf-8")
            (claude_target / "package.json").write_text('{"name":"tes-claude-hook-fixture"}\n', encoding="utf-8")
            run(["git", "init"], cwd=claude_target)
            claude_install = run(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "install",
                    "--attach",
                    "all",
                    "--target",
                    str(claude_target),
                    "--agent",
                    "claude",
                    "--yes",
                ],
                cwd=source_root(),
            )
            if claude_install.returncode != 0:
                failures.append("Claude-only install failed")
                failures.extend(claude_install.stdout.splitlines())
                failures.extend(claude_install.stderr.splitlines())
            if not (claude_target / ".claude/skills/tes-setup/SKILL.md").exists():
                failures.append("Claude-only install must deliver /tes-setup as a project skill")
            claude_start_notice = run(
                [
                    sys.executable,
                    str(claude_target / ".tes/bin/tes_install.py"),
                    "hook",
                    "--agent",
                    "claude",
                    "--target",
                    str(claude_target),
                    "--announce-start",
                ],
                cwd=claude_target,
                input=json.dumps({"hook_event_name": "SessionStart", "source": "startup", "cwd": str(claude_target)}),
            )
            if claude_start_notice.returncode != 0:
                failures.append("Claude-only start notice hook failed")
                failures.extend(claude_start_notice.stdout.splitlines())
                failures.extend(claude_start_notice.stderr.splitlines())
            try:
                claude_start_payload = json.loads(claude_start_notice.stdout)
            except json.JSONDecodeError:
                claude_start_payload = {}
                failures.append("Claude-only start notice hook must return structured JSON")
            if claude_start_payload.get("systemMessage") != CLAUDE_SETUP_RUNNING_MESSAGE:
                failures.append("Claude-only start notice must show the visible running message")
            claude_first_hook = run(
                [
                    sys.executable,
                    str(claude_target / ".tes/bin/tes_install.py"),
                    "hook",
                    "--agent",
                    "claude",
                    "--target",
                    str(claude_target),
                    "--rewake-on-complete",
                ],
                cwd=claude_target,
                input=json.dumps({"hook_event_name": "SessionStart", "source": "startup", "cwd": str(claude_target)}),
            )
            if claude_first_hook.returncode != 2:
                failures.append("Claude first SessionStart hook failed")
                failures.extend(claude_first_hook.stdout.splitlines())
                failures.extend(claude_first_hook.stderr.splitlines())
            if claude_first_hook.stdout.strip():
                failures.append("Claude asyncRewake completion must not emit JSON stdout on exit 2")
            if (
                "TES first-session setup completed." not in claude_first_hook.stderr
                or "Please, run /tes-setup for the report." not in claude_first_hook.stderr
            ):
                failures.append("Claude asyncRewake completion must wake with visible /tes-setup guidance")
            claude_sentinel = read_json(claude_target / POSTINSTALL_PATH)
            if claude_sentinel.get("state") != "complete":
                failures.append("Claude asyncRewake postinstall must complete before completion message")
            # Ceiling: a host-pending install completes as READY_PENDING_HOST.
            if claude_sentinel.get("last_status") not in {"PASS", "READY_PENDING_HOST"}:
                failures.append(
                    f"Claude asyncRewake postinstall must record PASS or READY_PENDING_HOST before completion message, got {claude_sentinel.get('last_status')}"
                )
            claude_complete_notice = run(
                [
                    sys.executable,
                    str(claude_target / ".tes/bin/tes_install.py"),
                    "hook",
                    "--agent",
                    "claude",
                    "--target",
                    str(claude_target),
                    "--announce-start",
                ],
                cwd=claude_target,
                input=json.dumps({"hook_event_name": "SessionStart", "source": "startup", "cwd": str(claude_target)}),
            )
            if claude_complete_notice.returncode != 0:
                failures.append("Claude complete start notice hook failed")
            try:
                claude_complete_payload = json.loads(claude_complete_notice.stdout)
            except json.JSONDecodeError:
                claude_complete_payload = {}
                failures.append("Claude complete start notice hook must return structured JSON")
            if "systemMessage" in claude_complete_payload:
                failures.append("Claude start notice must stay quiet after postinstall is complete")

        with tempfile.TemporaryDirectory(prefix="tes-thin-install-claude-partial-") as claude_partial_tempdir:
            claude_partial_target = Path(claude_partial_tempdir)
            (claude_partial_target / "README.md").write_text("# Claude Partial Hook Fixture\n", encoding="utf-8")
            (claude_partial_target / "package.json").write_text(
                '{"name":"tes-claude-partial-hook-fixture"}\n',
                encoding="utf-8",
            )
            run(["git", "init"], cwd=claude_partial_target)
            claude_partial_install = run(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "install",
                    "--attach",
                    "all",
                    "--target",
                    str(claude_partial_target),
                    "--agent",
                    "claude",
                    "--yes",
                ],
                cwd=source_root(),
            )
            if claude_partial_install.returncode != 0:
                failures.append("Claude partial fixture install failed")
                failures.extend(claude_partial_install.stdout.splitlines())
                failures.extend(claude_partial_install.stderr.splitlines())
            (claude_partial_target / ".tes/bin").mkdir(parents=True, exist_ok=True)
            (claude_partial_target / ".tes/bin/.DS_Store").write_text("neutral residue\n", encoding="utf-8")
            claude_partial_hook = run(
                [
                    sys.executable,
                    str(claude_partial_target / ".tes/bin/tes_install.py"),
                    "hook",
                    "--agent",
                    "claude",
                    "--target",
                    str(claude_partial_target),
                    "--rewake-on-complete",
                ],
                cwd=claude_partial_target,
                input=json.dumps(
                    {"hook_event_name": "SessionStart", "source": "startup", "cwd": str(claude_partial_target)}
                ),
            )
            if claude_partial_hook.returncode != 2:
                failures.append("Claude asyncRewake partial certification must wake the CLI")
                failures.extend(claude_partial_hook.stdout.splitlines())
                failures.extend(claude_partial_hook.stderr.splitlines())
            if "TES first-session setup needs review." not in claude_partial_hook.stderr:
                failures.append("Claude asyncRewake partial certification must report needs review")
            # Ceiling (F9): the planted OS residue makes artifact_hygiene a real
            # defect (PARTIAL). Combined with the host-pending findings, the strict
            # fold (NEEDS_REVIEW > PARTIAL) surfaces the aggregate as NEEDS_REVIEW —
            # the genuine review the fixture exists to prove. The status line must
            # name a non-clean review (PARTIAL or NEEDS_REVIEW), never a green.
            if not (
                "Status: PARTIAL." in claude_partial_hook.stderr
                or "Status: NEEDS_REVIEW." in claude_partial_hook.stderr
            ):
                failures.append("Claude asyncRewake partial certification must expose a non-clean (PARTIAL/NEEDS_REVIEW) status")
            claude_partial_sentinel = read_json(claude_partial_target / POSTINSTALL_PATH)
            if claude_partial_sentinel.get("state") != "needs_review":
                failures.append("Claude asyncRewake partial certification must leave needs_review sentinel")
            # The real artifact_hygiene defect keeps this a genuine review (not a
            # host-pending READY_PENDING_HOST): last_status is PARTIAL or the
            # stricter NEEDS_REVIEW, never PASS/READY_PENDING_HOST.
            if claude_partial_sentinel.get("last_status") not in {"PARTIAL", "NEEDS_REVIEW"}:
                failures.append(
                    f"Claude asyncRewake partial certification must retain a review (PARTIAL/NEEDS_REVIEW) last_status, got {claude_partial_sentinel.get('last_status')}"
                )

    with tempfile.TemporaryDirectory(prefix="tes-thin-install-dry-") as tempdir:
        target = Path(tempdir)
        dry_result = run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "install",
                "--attach",
                "all",
                "--target",
                str(target),
                "--agent",
                "codex",
                "--dry-run",
            ],
            cwd=source_root(),
        )
        if dry_result.returncode != 0:
            failures.append("thin dry-run failed")
        if (target / ".tes").exists() or (target / ".codex").exists():
            failures.append("thin dry-run wrote target files")

    with tempfile.TemporaryDirectory(prefix="tes-source-target-block-") as tempdir:
        target = Path(tempdir)
        (target / "package.json").write_text(
            json.dumps({"name": "tilly-engineer-skills"}, indent=2) + "\n",
            encoding="utf-8",
        )
        for marker in (
            Path("src/adapters/codex/AGENTS.md"),
            Path("scripts/tes_install.py"),
            Path("scripts/tes_bundle.py"),
        ):
            marker_path = target / marker
            marker_path.parent.mkdir(parents=True, exist_ok=True)
            marker_path.write_text("source marker\n", encoding="utf-8")
        blocked_result = run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "install",
                "--attach",
                "all",
                "--target",
                str(target),
                "--agent",
                "all",
                "--dry-run",
            ],
            cwd=source_root(),
        )
        blocked_payload = parse_json_output(blocked_result.stdout)
        if blocked_result.returncode != 2:
            failures.append("source package target install must return BLOCKED")
            failures.extend(blocked_result.stdout.splitlines())
            failures.extend(blocked_result.stderr.splitlines())
        if blocked_payload.get("status") != "BLOCKED":
            failures.append("source package target install must report BLOCKED status")
        if "TES package source" not in str(blocked_payload.get("reason", "")):
            failures.append("source package target install must explain package-source boundary")

        blocked_entrypoints = [
            (
                "source package target postinstall",
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "postinstall",
                    "--target",
                    str(target),
                    "--dry-run",
                ],
            ),
            (
                "source package target hook",
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "hook",
                    "--agent",
                    "codex",
                    "--target",
                    str(target),
                ],
            ),
            (
                "source package target update planner",
                [
                    sys.executable,
                    str(source_root() / "scripts/tes_update.py"),
                    "plan",
                    "--target",
                    str(target),
                    "--offline",
                    "--json-only",
                ],
            ),
            (
                "source package target MCP installer",
                [
                    sys.executable,
                    str(source_root() / "scripts/install_mcp.py"),
                    "--target",
                    str(target),
                    "--adapter",
                    "all",
                    "--dry-run",
                    "--json-only",
                ],
            ),
            (
                "source package target adapter installer",
                [
                    sys.executable,
                    str(source_root() / "scripts/install_adapter.py"),
                    "--target",
                    str(target),
                    "--adapter",
                    "all",
                    "--dry-run",
                ],
            ),
        ]
        for label, command in blocked_entrypoints:
            entrypoint_result = run(
                command,
                cwd=source_root(),
            )
            entrypoint_payload = parse_json_output(entrypoint_result.stdout)
            if entrypoint_result.returncode != 2:
                failures.append(f"{label} must return BLOCKED")
                failures.extend(entrypoint_result.stdout.splitlines())
                failures.extend(entrypoint_result.stderr.splitlines())
            if entrypoint_payload.get("status") != "BLOCKED":
                failures.append(f"{label} must report BLOCKED status")
        if any(
            (target / relpath).exists()
            for relpath in (".tes", ".codex", ".claude", ".cursor", ".mcp.json")
        ):
            failures.append("source package target block must not create install artifacts")

    # Advisories collector (GAP-1/2/4/5): signals already ride the tes_init
    # payload, so no oracle is re-run. Each rule is isolated and never changes
    # status. Prove fire-when-present, silent-when-absent, and safe degradation.
    def _tes_init_result(payload: dict[str, Any]) -> list[dict[str, Any]]:
        return [{"command": ".tes/bin/tes_init.py --target . --yes", "payload": payload}]

    def _gate(command: str, stdout_obj: dict[str, Any]) -> dict[str, Any]:
        return {"command": command, "stdout": json.dumps(stdout_obj)}

    firing_payload = {
        "gates": [
            _gate(
                ".tes/bin/project_alignment_oracle.py --target .",
                {
                    "freshness": {
                        "notes": ["newest ADR docs/agents/DECISIONS/002.md introduces tokens absent"],
                        "mesh_scaffold_only": True,
                    }
                },
            ),
            _gate(".tes/bin/cortex.py audit --target .", {"cell_count": 0}),
            _gate(
                ".tes/bin/field_reports.py status --target .",
                {"pending": 42, "pending_advisory": "42 field reports pendentes (>30) — sincronize o outbox"},
            ),
        ]
    }
    firing = {a["code"] for a in collect_advisories(_tes_init_result(firing_payload))}
    for code in ("freshness.adr_drift", "mesh.scaffold_only", "cortex.empty", "field_reports.pending_high"):
        if code not in firing:
            failures.append(f"collect_advisories must emit {code} when its signal is present")

    quiet_payload = {
        "gates": [
            _gate(".tes/bin/project_alignment_oracle.py --target .", {"freshness": {"notes": [], "mesh_scaffold_only": False}}),
            _gate(".tes/bin/cortex.py audit --target .", {"cell_count": 7}),
            _gate(".tes/bin/field_reports.py status --target .", {"pending": 3, "pending_advisory": None}),
        ]
    }
    if collect_advisories(_tes_init_result(quiet_payload)):
        failures.append("collect_advisories must stay empty when no signal is present")

    # Gap 3 truthfulness: a target that transitions scaffold -> aligned must drop
    # mesh.scaffold_only, and advisories must be scoped to the producing run so a
    # historical scaffold advisory can never read as current-state evidence.
    scaffold_run = collect_advisories(_tes_init_result(firing_payload), derived_at="2026-01-01T00:00:00Z")
    if not any(a["code"] == "mesh.scaffold_only" for a in scaffold_run):
        failures.append("scaffold-era run must emit mesh.scaffold_only advisory")
    if any(a.get("derived_at") != "2026-01-01T00:00:00Z" for a in scaffold_run):
        failures.append("scaffold-era advisories must be stamped with the producing run's derived_at")
    aligned_run = collect_advisories(_tes_init_result(quiet_payload), derived_at="2026-06-30T00:00:00Z")
    if any(a["code"] == "mesh.scaffold_only" for a in aligned_run):
        failures.append(
            "after scaffold -> aligned transition, mesh.scaffold_only must NOT remain as current-state advisory"
        )

    # Adversarial: missing payload / missing gates must degrade to [] (never raise).
    if collect_advisories([]) != []:
        failures.append("collect_advisories must return [] when tes_init payload is absent")
    if collect_advisories(_tes_init_result({})) != []:
        failures.append("collect_advisories must return [] when gates are absent")

    # F11: bare `all` MCP bootstrap must NOT install vscode (protected baseline:
    # never clobber a user's .vscode/mcp.json) AND must surface its absence as a
    # visible NOT_INSTALLED_BY_POLICY verdict instead of dropping it silently.
    all_install_set = selected_mcp_adapters("all")
    if "vscode" in all_install_set:
        failures.append("bare 'all' MCP bootstrap must not auto-install vscode (clobber risk)")
    if not {"codex", "claude", "cursor"}.issubset(set(all_install_set)):
        failures.append("bare 'all' MCP bootstrap must still install codex/claude/cursor")
    all_verdicts = mcp_policy_verdicts("all")
    vscode_verdict = next((v for v in all_verdicts if v.get("adapter") == "vscode"), None)
    if vscode_verdict is None:
        failures.append("bare 'all' MCP bootstrap must emit a policy verdict for vscode")
    elif vscode_verdict.get("verdict") != "NOT_INSTALLED_BY_POLICY":
        failures.append("vscode policy verdict under 'all' must be NOT_INSTALLED_BY_POLICY")
    elif "--adapter vscode" not in str(vscode_verdict.get("hint", "")):
        failures.append("vscode policy verdict must carry the explicit --adapter vscode opt-in hint")
    # An explicit single-adapter scope carries no policy-deferred verdicts.
    if mcp_policy_verdicts("vscode"):
        failures.append("explicit --adapter vscode scope must not emit policy-deferred verdicts")
    if mcp_policy_verdicts("claude"):
        failures.append("single-adapter scope must not emit policy-deferred verdicts")
    # The summary surface must carry the verdict (not just the raw bootstrap dict).
    summary_with_policy = mcp_summary_from_results("all", all_install_set, [], dry_run=True)
    if not any(v.get("adapter") == "vscode" for v in summary_with_policy.get("policy_verdicts", [])):
        failures.append("mcp_summary_from_results must expose the vscode policy verdict")

    result = {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "coverage": "thin-installer-first-session-postinstall",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-install:self-test] " + result["status"])
    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    install_parser = subparsers.add_parser("install")
    install_parser.add_argument("--target", type=Path, default=Path.cwd())
    install_parser.add_argument("--agent", default="all", choices=["all", *AGENTS])
    install_parser.add_argument("--mode", default="preserve", choices=["preserve", "clean-runtime"])
    install_parser.add_argument("--bundle", type=Path)
    install_parser.add_argument("--url")
    install_parser.add_argument("--sha256")
    install_parser.add_argument("--timeout", type=float, default=120.0)
    install_parser.add_argument("--postinstall-mode", default="first-session", choices=["first-session"])
    install_parser.add_argument("--dry-run", action="store_true")
    install_parser.add_argument("--yes", action="store_true")
    install_parser.add_argument("--no-hooks", action="store_true")
    install_parser.add_argument("--no-postinstall", action="store_true")
    # ADR 0004: capsule-first install. Default writes only .tes/** (the capsule).
    # Project-visible surfaces are explicit reversible attachments. Pass
    # --attach <surface> (repeatable) or --attach all for legacy install-all.
    install_parser.add_argument(
        "--attach",
        action="append",
        default=None,
        # Derive choices from ALL_ATTACH_SURFACES so the parser and resolve_attach
        # can never diverge; "all" is the install-all meta-selection and "capsule"
        # is the explicit minimal/isolation selection (capsule-only, no
        # project-visible surface).
        choices=["all", "capsule", *ALL_ATTACH_SURFACES],
        help="attach a project-visible surface; default is capsule-only",
    )

    postinstall_parser = subparsers.add_parser("postinstall")
    postinstall_parser.add_argument("--target", type=Path, default=Path.cwd())
    postinstall_parser.add_argument("--agent", default="codex", choices=["all", *AGENTS])
    postinstall_parser.add_argument("--mode", default="first-session")
    postinstall_parser.add_argument("--timeout", type=float, default=120.0)
    postinstall_parser.add_argument("--dry-run", action="store_true")
    postinstall_parser.add_argument("--force", action="store_true")
    postinstall_parser.add_argument("--recover-needs-review", action="store_true")
    postinstall_parser.add_argument("--skip-project-init", action="store_true")

    hook_parser = subparsers.add_parser("hook")
    hook_parser.add_argument("--target", type=Path, default=Path.cwd())
    hook_parser.add_argument("--agent", default="codex", choices=AGENTS)
    hook_parser.add_argument("--mode", default="first-session")
    hook_parser.add_argument("--timeout", type=float, default=120.0)
    hook_parser.add_argument("--dry-run", action="store_true")
    hook_parser.add_argument("--force", action="store_true")
    hook_parser.add_argument("--skip-project-init", action="store_true")
    hook_parser.add_argument("--announce-start", action="store_true")
    hook_parser.add_argument("--rewake-on-complete", action="store_true")

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--target", type=Path, default=Path.cwd())

    hook_health_parser = subparsers.add_parser("hook-health")
    hook_health_parser.add_argument("--target", type=Path, default=Path.cwd())
    hook_health_parser.add_argument("--agent", choices=AGENTS)
    hook_health_parser.add_argument("--json-only", action="store_true")
    # Ceiling F23: --query (default) exits 0 on NEEDS_EVIDENCE to preserve the
    # pending-host install contract; --gate exits non-zero on NEEDS_EVIDENCE so a
    # shell caller's exit code never certifies success where proof is absent.
    hook_health_mode = hook_health_parser.add_mutually_exclusive_group()
    hook_health_mode.add_argument("--gate", action="store_true", help="exit non-zero on NEEDS_EVIDENCE (missing proof)")
    hook_health_mode.add_argument("--query", action="store_true", help="exit 0 on NEEDS_EVIDENCE (default)")

    # ADR 0004 SPEC-003: reverse a TES installation and prove zero active residue.
    uninstall_parser = subparsers.add_parser("uninstall")
    uninstall_parser.add_argument("--target", type=Path, default=Path.cwd())
    uninstall_parser.add_argument("--dry-run", action="store_true")
    uninstall_parser.add_argument("--yes", action="store_true")

    # ADR 0004 SPEC-002: attach/detach one project-visible surface.
    attach_parser = subparsers.add_parser("attach")
    attach_parser.add_argument("surface", choices=list(ALL_ATTACH_SURFACES))
    attach_parser.add_argument("--target", type=Path, default=Path.cwd())
    attach_parser.add_argument("--agent", default="all", choices=["all", *AGENTS])
    attach_parser.add_argument("--timeout", type=float, default=120.0)
    attach_parser.add_argument("--dry-run", action="store_true")
    attach_parser.add_argument("--yes", action="store_true")

    detach_parser = subparsers.add_parser("detach")
    detach_parser.add_argument("surface", choices=list(ALL_ATTACH_SURFACES))
    detach_parser.add_argument("--target", type=Path, default=Path.cwd())
    detach_parser.add_argument("--timeout", type=float, default=120.0)
    detach_parser.add_argument("--dry-run", action="store_true")
    detach_parser.add_argument("--yes", action="store_true")

    # ADR 0004 installer model: read-only capsule + attachment health report.
    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("--target", type=Path, default=Path.cwd())

    args = parser.parse_args()
    if sys.version_info < MIN_PYTHON:
        return python_runtime_block(args.command)
    if args.self_test:
        return self_test()
    if args.command == "install":
        return install(args)
    if args.command == "postinstall":
        code, result = postinstall(args)
        print(json.dumps(result, indent=2, sort_keys=True))
        print("[tes-postinstall] " + result["status"])
        return code
    if args.command == "uninstall":
        return uninstall(args)
    if args.command == "attach":
        return attach(args)
    if args.command == "detach":
        return detach(args)
    if args.command == "doctor":
        return doctor(args)
    if args.command == "hook":
        return hook(args)
    if args.command == "status":
        return status(args)
    if args.command == "hook-health":
        return hook_health(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
