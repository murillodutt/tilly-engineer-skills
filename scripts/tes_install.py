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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "0.3.204"
SELF_TEST_SUBPROCESS_TIMEOUT = 180.0
MIN_PYTHON = (3, 11)
LOCK_PATH = Path(".tes/tes-install-lock.json")
POSTINSTALL_PATH = Path(".tes/postinstall.json")
POSTINSTALL_RUN_ROOT = Path(".tes/postinstall-runs")
POSTINSTALL_RUN_INDEX = POSTINSTALL_RUN_ROOT / "index.json"
POSTINSTALL_SENTINEL_RUN_LIMIT = 20
AGENTS = ("codex", "claude", "cursor")
POSTINSTALL_STATES = {"pending", "running", "complete", "needs_review"}
CLAUDE_SESSIONSTART_MATCHER = "startup|resume|clear|compact"
# PreToolUse (senior-manager pre-action) matcher: the mutating tools the gate supervises.
CLAUDE_PRETOOLUSE_MATCHER = "Write|Edit|MultiEdit"
DEFAULT_POSTINSTALL_COMMANDS = (
    ("tes_init.py", ("--target", "{target}", "--yes")),
    ("project_context_oracle.py", ("--target", "{target}")),
    ("project_alignment_oracle.py", ("--target", "{target}")),
)
HOOK_RUNTIME_HELPERS = ("cortex_runtime.py",)
OPERATING_MESH_PRETOOLUSE_HINTS = (
    "docs/agents/PROJECT-STATE.md",
    "docs/agents/PROJECT-ROADMAP.md",
    "docs/agents/EXECUTION-LINE.md",
    "docs/agents/QUALITY-GATES.md",
    "docs/agents/DECISIONS/",
)


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


def selected_mcp_adapters(agent: str) -> list[str]:
    # VS Code is a certified MCP consumer config, not a TES adapter.
    if agent == "all":
        return ["codex", "claude", "cursor"]
    return [agent]


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


def codex_hook_snippet() -> str:
    command = (
        f'{python_command_token()} "$(git rev-parse --show-toplevel)/.tes/bin/tes_install.py" '
        'hook --agent codex --target "$(git rev-parse --show-toplevel)"'
    )
    return f"""# TES first-session post-install hook.
[[hooks.SessionStart]]
matcher = "startup|resume"

[[hooks.SessionStart.hooks]]
type = "command"
command = {command_literal(command)}
timeout = 120
statusMessage = "Checking TES post-install"
"""


def codex_pretooluse_snippet() -> str:
    command = (
        f'{python_command_token()} "$(git rev-parse --show-toplevel)/.tes/bin/tes_install.py" '
        'hook --agent codex --target "$(git rev-parse --show-toplevel)"'
    )
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
    snippet = codex_hook_snippet().strip()
    if "TES first-session post-install hook" not in updated:
        updated = updated.rstrip() + "\n\n" + snippet + "\n"
    pretooluse = codex_pretooluse_snippet().strip()
    if "TES PreToolUse senior-manager gate" not in updated:
        updated = updated.rstrip() + "\n\n" + pretooluse + "\n"
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
    return {
        "schema": "tes-postinstall@1",
        "version": VERSION,
        "state": "pending",
        "created_at": existing.get("created_at") or utc_stamp(),
        "updated_at": utc_stamp(),
        "requested_by": agent,
        "agents": agents,
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
        payload = {**existing, "state": "pending", "updated_at": utc_stamp(), "requested_by": agent, "agents": agents}
    elif state in POSTINSTALL_STATES:
        payload = {**sentinel_payload(agent, agents, mode, existing), "state": state if state == "running" else "pending"}
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


def write_install_lock(
    target: Path,
    agent: str,
    agents: list[str],
    mode: str,
    stage: dict[str, Any],
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
        "stage": summarize_result(stage),
        "attached_surfaces": attached_surfaces or ["capsule"],
        "apply": summarize_result(apply_result),
        "hooks": hook_actions,
        "mcp": summarize_mcp_result(mcp_result),
        "certification": summarize_certification_result(certification_result),
    }
    return write_json(target / LOCK_PATH, lock, dry_run=dry_run)


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


def aggregate_install_status(dry_run: bool, apply_status: str, certification_status: str) -> str:
    if dry_run:
        return "DRY-RUN"
    if apply_status == "NEEDS_REVIEW":
        return "NEEDS_REVIEW"
    if certification_status in {"PASS", "DRY-RUN"}:
        return "INSTALLED"
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
    if surface in {"mcp", "hooks", "docs-mesh"}:
        if surface == "mcp":
            import install_mcp  # type: ignore
            actions, failures = install_mcp.install_configs(
                target, selected_agents(args.agent), args.dry_run, False, True, False,
            )
            writer = {"actions": actions, "failures": failures}
        elif surface == "hooks":
            writer = {"actions": install_hooks(target, selected_agents(args.agent), args.dry_run)}
        else:  # docs-mesh
            if args.dry_run:
                writer = {"status": "DRY-RUN", "action": "would-run-tes-init"}
            else:
                writer = run_helper(target, "tes_init.py", ("--target", "{target}", "--yes"), args.timeout)
        health = {"status": "SKIP", "reason": "dry-run"}
        if not args.dry_run:
            import attach_health_oracle  # type: ignore
            health = attach_health_oracle.evaluate(target, surface)
        status = "DRY-RUN" if args.dry_run else (
            "ATTACHED" if health.get("status") in {"PASS", "PENDING_TRUST", "PENDING_HOST_RESTART", "HOST_UNOBSERVABLE", "NOT_APPLIED"}
            else str(health.get("status"))
        )
        result = {"version": VERSION, "status": status, "target": str(target), "surface": surface, "writer": writer, "health": health}
        print(json.dumps(result, indent=2, sort_keys=True))
        print("[tes-attach] " + status)
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
    result = {"version": VERSION, "status": status, "target": str(target), "surface": surface, "apply": apply_result}
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
    # doctor is a report, never a failure verdict on its own; FAIL is reserved for
    # a bad invocation (handled above). An unhealthy attachment surfaces in its
    # own per-surface status, not by failing the whole report.
    status = "PASS" if capsule_present else "NOT_INSTALLED"
    result = {
        "version": VERSION,
        "status": status,
        "target": str(target),
        "capsule": capsule_health,
        "attachments": attachments,
        "attached_surfaces": attached,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-doctor] " + status)
    return 0


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
    if mcp_result.get("status") == "FAIL":
        result = {
            "version": VERSION,
            "status": "FAIL",
            "target": str(target),
            "agent": args.agent,
            "agents": agents,
            "mode": args.mode,
            "stage": summarize_result(stage),
            "apply": summarize_result(apply_result),
            "hooks": hook_actions,
            "mcp": summarize_mcp_result(mcp_result),
            "failures": mcp_result.get("failures", ["MCP bootstrap failed"]),
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        print("[tes-install] FAIL")
        return 1
    certification_result = run_installed_certification(target, args.dry_run, args.timeout)
    # The first-session post-install sentinel (.tes/postinstall.json) is what the
    # installed SessionStart hook reads to announce setup and trigger first-run
    # work. It must be written whenever the hook surface is attached — otherwise
    # the hook fires into an empty state and does nothing. It is gated on `hooks`,
    # not on docs-mesh: the sentinel records install state for the hook; it does
    # not by itself materialize docs/agents (that stays the docs-mesh attachment).
    postinstall_disabled = args.no_postinstall or "hooks" not in surfaces
    sentinel_action = (
        {"path": rel(target / POSTINSTALL_PATH, target), "action": "skip-capsule-only" if not args.no_postinstall else "skip-disabled"}
        if postinstall_disabled
        else (
            write_review_sentinel(target, args.agent, agents, args.postinstall_mode, apply_result, args.dry_run, certification_result)
            if apply_result.get("status") == "NEEDS_REVIEW"
            or certification_status_rank(str(certification_result.get("status") or "")) >= certification_status_rank("NEEDS_REVIEW")
            else write_pending_sentinel(target, args.agent, agents, args.postinstall_mode, args.dry_run)
        )
    )
    lock_action = write_install_lock(
        target,
        args.agent,
        agents,
        args.mode,
        stage,
        apply_result,
        hook_actions,
        mcp_result,
        certification_result,
        args.dry_run,
        sorted(surfaces),
    )
    status = aggregate_install_status(
        args.dry_run,
        str(apply_result.get("status") or ""),
        str(certification_result.get("status") or ""),
    )
    result = {
        "version": VERSION,
        "status": status,
        "target": str(target),
        "agent": args.agent,
        "agents": agents,
        "mode": args.mode,
        # Project-visible surfaces actually materialized this run (capsule is the
        # always-present runtime authority, not a project-visible attachment).
        # The bin renderer reads this to describe the install truthfully instead
        # of inferring materialization from the docs-mesh postinstall sentinel.
        "attached_surfaces": sorted(surfaces - {"capsule"}),
        "stage": summarize_result(stage),
        "apply": summarize_result(apply_result),
        "hooks": hook_actions,
        "mcp": summarize_mcp_result(mcp_result),
        "certification": summarize_certification_result(certification_result),
        "postinstall": sentinel_action,
        "lock": lock_action,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-install] " + result["status"])
    # Only a broken certification *process* (FAIL) is a non-zero install. A
    # successful apply with a post-install review verdict aggregates to
    # NEEDS_REVIEW (exit 0): TES is on disk and reversible, the bin renders the
    # preserved-review notice. aggregate_install_status no longer yields BLOCKED.
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
    failed = [item for item in results if item["returncode"] != 0]
    certification_status = str(certification_result.get("status") or "NEEDS_REVIEW")
    needs_cert_review = certification_status not in {"PASS", "DRY-RUN"}
    final_state = "needs_review" if failed or needs_cert_review else "complete"
    if failed:
        status = "NEEDS_REVIEW"
    elif needs_cert_review:
        status = certification_status
    else:
        status = "PASS"
    advisories = collect_advisories(results) if status == "PASS" else []
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


def collect_advisories(results: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Derive post-PASS advisories from the tes_init payload already in `results`.

    Advisories are non-blocking nudges (GAP-1/2/4/5). They never change status;
    each rule is isolated so a malformed payload degrades to fewer advisories
    rather than raising and breaking the hook.
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
    value = hook_input.get("hook_event_name") or hook_input.get("hookEventName") or hook_input.get("event")
    return str(value or default)


def hook_tool_name(hook_input: dict[str, Any]) -> str:
    value = hook_input.get("tool_name") or hook_input.get("toolName")
    if isinstance(value, str):
        return value
    tool = hook_input.get("tool")
    return tool if isinstance(tool, str) else ""


def hook_tool_input(hook_input: dict[str, Any]) -> dict[str, Any]:
    value = hook_input.get("tool_input")
    if value is None:
        value = hook_input.get("toolInput")
    return value if isinstance(value, dict) else {}


def hook_tool_path(hook_input: dict[str, Any], tool_input: dict[str, Any]) -> str:
    value = (
        tool_input.get("file_path")
        or tool_input.get("path")
        or tool_input.get("filePath")
        or hook_input.get("file_path")
        or hook_input.get("path")
        or hook_input.get("filePath")
    )
    return str(value or "")


def hook_tool_command(hook_input: dict[str, Any], tool_input: dict[str, Any]) -> str:
    return str(tool_input.get("command") or hook_input.get("command") or "")


def claude_hook_output(result: dict[str, Any], hook_input: dict[str, Any]) -> dict[str, Any]:
    event_name = hook_event_name(hook_input)
    output: dict[str, Any] = {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": claude_postinstall_context(result, hook_input),
        }
    }
    if result.get("status") == "PASS":
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
    if status == "PASS":
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


def record_hook_execution(target: Path, agent: str, hook_input: dict[str, Any], *, mode: str) -> None:
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
        }
        if event_canonical == "PreToolUse":
            tool_input = hook_tool_input(hook_input)
            tool = hook_tool_name(hook_input)
            path = hook_tool_path(hook_input, tool_input)
            command = hook_tool_command(hook_input, tool_input)
            invocation = hook_input.get("tool_use_id") or hook_input.get("toolUseId")
            if tool:
                record["tool"] = tool
            if path:
                record["path"] = path
            if command:
                record["command"] = command
            if invocation:
                record["invocation"] = str(invocation)
        with sentinel.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        pass


GOVERNED_ARTIFACT_HINTS = (
    "AGENTS.md",
    "CLAUDE.md",
    "docs/adr/",
    "docs/governance/",
    "/SKILL.md",
    ".cursor/rules/",
)
# Tools that change state. A non-mutating tool (Read/Grep/Glob) is never gated.
MUTATING_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit", "Bash")


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
    """Decide supervise-vs-block for a PreToolUse tool call, faithful to the bootloader.

    Two registers (mirrors the <mantra_gate> two-register rule), anchored on the
    reliable tool+path signal and reinforced by classify_risk:
      - forbidden by intent (e.g. `push --force`, secret disclosure) -> BLOCK.
      - a MUTATING tool touching a GOVERNED artifact at material+ risk -> SUPERVISE
        (allow, surface the contract obligation as context once per session).
      - everything else (non-mutating tool, ordinary code, routine) -> ALLOW silently.
    The agent still reasons over the surfaced context — the hook injects, it does not
    decide the agent's intent (the inject-not-decide form). Ordinary local work is
    never blocked; only the unambiguous forbidden class wakes the hard gate.
    """
    tool_name = hook_tool_name(hook_input)
    tool_input = hook_tool_input(hook_input)
    file_path = hook_tool_path(hook_input, tool_input)
    command = hook_tool_command(hook_input, tool_input)
    action = " ".join(part for part in (tool_name, command, file_path) if part).strip()
    paths = [file_path] if file_path else []

    risk = _classify_pretooluse_risk(action, paths)
    governed = any(hint in file_path for hint in GOVERNED_ARTIFACT_HINTS)
    mutating = tool_name in MUTATING_TOOLS
    if risk == "routine" and governed and mutating:
        risk = "material"

    if risk == "forbidden":
        return {
            "block": True,
            "risk": risk,
            "reason": (
                f"{_mantra_gate_marker()} Mantra Gate (senior manager): forbidden-class action "
                f"({action or tool_name}). Run the hard gate (VERIFY/SCOPE/BEST_PATH/"
                "DOCUMENT/ORACLE/RESOLVE/STATUS) and get explicit authorization before proceeding."
            ),
        }
    if governed and mutating and risk in ("material", "high-risk"):
        return {
            "block": False,
            "risk": risk,
            "context": (
                f"{_mantra_gate_marker()} Mantra Gate supervising: {risk} change to governed artifact {file_path}. "
                "Confirm the contract obligation (ADR/SPEC) and bind a falsifiable oracle before closure."
            ),
        }
    return {"block": False, "risk": risk, "context": ""}


def _pretooluse_seen_this_session(target: Path, hook_input: dict[str, Any], key: str) -> bool:
    """Anti-cry-wolf: surface a given supervision context at most once per session."""
    session = str(hook_input.get("session_id") or hook_input.get("sessionId") or hook_input.get("session") or "default")
    sentinel = target / ".tes" / "mantra-gates" / f"pretooluse-{session}.seen"
    try:
        seen = set()
        if sentinel.exists():
            seen = set(sentinel.read_text(encoding="utf-8").splitlines())
        if key in seen:
            return True
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        with sentinel.open("a", encoding="utf-8") as handle:
            handle.write(key + "\n")
    except OSError:
        return False
    return False


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
    A materializer that assumed exit-2 everywhere would break silently on Cursor.
    """
    target = target_root(args.target)
    record_hook_execution(target, args.agent, hook_input, mode="pretooluse")
    decision = _pretooluse_decision(hook_input)

    if decision["block"]:
        reason = decision["reason"]
        if args.agent == "cursor":
            print(json.dumps({"permission": "deny", "agent_message": reason}, ensure_ascii=False, sort_keys=True))
            return 0
        print(reason, file=sys.stderr)
        return 2

    context = decision.get("context") or ""
    if context and _pretooluse_seen_this_session(target, hook_input, context):
        context = ""
    cortex_context = ""
    if _pretooluse_may_touch_operating_mesh(hook_input):
        cortex_context = _cortex_runtime_context(
            _evaluate_cortex_runtime(target, args.agent, hook_input),
            include_capture=False,
        )
    combined_context = _join_context(context, cortex_context)
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


def self_test() -> int:
    failures: list[str] = []

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
        if install_mcp.get("status") != "INSTALLED":
            failures.append("thin install must report MCP status INSTALLED")
        install_certification = install_payload.get("certification") if isinstance(install_payload.get("certification"), dict) else {}
        if install_certification.get("status") != "PASS":
            failures.append("thin install must report installed certification PASS")
        if install_mcp.get("adapters") != ["codex", "claude", "cursor"]:
            failures.append("thin install --agent all must map MCP adapters to codex, claude, cursor only")
        for relpath in (
            ".tes/bin/tes_install.py",
            ".tes/bin/cortex_runtime.py",
            ".tes/tes-install-lock.json",
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
        if (target / ".vscode/mcp.json").exists():
            failures.append("thin install --agent all must not create VS Code MCP config")
        codex_config = (target / ".codex/config.toml").read_text(encoding="utf-8") if (target / ".codex/config.toml").exists() else ""
        if "[mcp_servers.tes-cortex]" not in codex_config:
            failures.append("thin install must register Codex tes-cortex MCP server")
        if "hooks = true" not in codex_config:
            failures.append("thin install must enable Codex hooks with canonical features.hooks")
        if "codex_hooks = true" in codex_config:
            failures.append("thin install must not emit deprecated codex_hooks feature flag")
        for relpath, server_key in ((".mcp.json", "mcpServers"), (".cursor/mcp.json", "mcpServers")):
            data = read_json(target / relpath)
            servers = data.get(server_key) if isinstance(data.get(server_key), dict) else {}
            if "tes-cortex" not in servers:
                failures.append(f"thin install must register tes-cortex in {relpath}")

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
        if partial_payload.get("status") == "INSTALLED" or partial_certification.get("status") == "PASS":
            failures.append("installer must not claim clean INSTALLED/PASS from MCP success when installed certification fails")
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
        if sentinel.get("last_status") != "PASS":
            failures.append("postinstall sentinel must record PASS after hook")
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
        if (target / LEGACY_HOOK_SENTINEL_PATH).exists():
            failures.append("new hook runtime must not write the legacy tracked hook sentinel")
        ignore_probe = run(["git", "check-ignore", HOOK_SENTINEL_PATH.as_posix()], cwd=target)
        if ignore_probe.returncode != 0:
            failures.append("hook runtime sentinel must be excluded from target git status")

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
        if recovered_sentinel.get("last_status") != "PASS":
            failures.append("needs_review recovery must record PASS")
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
            if claude_sentinel.get("last_status") != "PASS":
                failures.append("Claude asyncRewake postinstall must record PASS before completion message")
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
            if "Status: PARTIAL." not in claude_partial_hook.stderr:
                failures.append("Claude asyncRewake partial certification must expose PARTIAL status")
            claude_partial_sentinel = read_json(claude_partial_target / POSTINSTALL_PATH)
            if claude_partial_sentinel.get("state") != "needs_review":
                failures.append("Claude asyncRewake partial certification must leave needs_review sentinel")
            if claude_partial_sentinel.get("last_status") != "PARTIAL":
                failures.append("Claude asyncRewake partial certification must retain PARTIAL last_status")

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

    # Adversarial: missing payload / missing gates must degrade to [] (never raise).
    if collect_advisories([]) != []:
        failures.append("collect_advisories must return [] when tes_init payload is absent")
    if collect_advisories(_tes_init_result({})) != []:
        failures.append("collect_advisories must return [] when gates are absent")

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
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
