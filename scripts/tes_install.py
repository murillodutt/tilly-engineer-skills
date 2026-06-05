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


VERSION = "0.3.166"
MIN_PYTHON = (3, 11)
LOCK_PATH = Path(".tes/tes-install-lock.json")
POSTINSTALL_PATH = Path(".tes/postinstall.json")
POSTINSTALL_RUN_ROOT = Path(".tes/postinstall-runs")
POSTINSTALL_RUN_INDEX = POSTINSTALL_RUN_ROOT / "index.json"
POSTINSTALL_SENTINEL_RUN_LIMIT = 20
AGENTS = ("codex", "claude", "cursor")
POSTINSTALL_STATES = {"pending", "running", "complete", "needs_review"}
CLAUDE_SESSIONSTART_MATCHER = "startup|resume|clear|compact"
DEFAULT_POSTINSTALL_COMMANDS = (
    ("tes_init.py", ("--target", "{target}", "--yes")),
    ("project_context_oracle.py", ("--target", "{target}")),
    ("project_alignment_oracle.py", ("--target", "{target}")),
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


def install_codex_hook(target: Path, dry_run: bool) -> dict[str, str]:
    path = target / ".codex/config.toml"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    updated = replace_or_insert_toml_feature(existing, "codex_hooks", "true")
    snippet = codex_hook_snippet().strip()
    if "TES first-session post-install hook" not in updated:
        updated = updated.rstrip() + "\n\n" + snippet + "\n"
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


def remove_tes_codex_hook_text(text: str) -> str:
    """Inverse of install_codex_hook: drop the TES SessionStart hook block and the
    codex_hooks feature flag, preserving any other Codex config (L3 SPEC-002).
    """
    lines = text.splitlines()
    # Remove the marked TES hook block: from the marker comment to the next
    # top-level section header (or EOF).
    marker = "# TES first-session post-install hook."
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == marker)
    except StopIteration:
        start = None
    if start is not None:
        end = len(lines)
        for idx in range(start + 1, len(lines)):
            stripped = lines[idx].strip()
            # Next top-level [section] or [[array.table]] that is not part of the
            # TES hook block ends the block. The TES block's own sub-tables start
            # with [[hooks.SessionStart...]]; stop at the first header that does
            # not belong to hooks.SessionStart.
            if (stripped.startswith("[") and stripped.endswith("]")
                    and not stripped.lstrip("[").startswith("hooks.SessionStart")
                    and not stripped.lstrip("[").startswith("hooks.SessionStart.hooks")):
                end = idx
                break
        lines = [*lines[:start], *lines[end:]]
    else:
        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped != "[[hooks.SessionStart]]":
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
    # Remove the codex_hooks feature flag line.
    lines = [line for line in lines if line.strip() != "codex_hooks = true"]
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
        path = target / ".codex/config.toml"
        if not path.exists():
            return {"agent": agent, "action": "already-absent"}
        stripped = remove_tes_codex_hook_text(path.read_text(encoding="utf-8"))
        if not stripped.strip():
            if not dry_run:
                path.unlink()
            return {"agent": agent, "path": rel(path, target), "action": "would-remove-file" if dry_run else "remove-file"}
        return {**write_text_if_changed(path, stripped, target, dry_run, backup=backup), "agent": agent}
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


def install_hooks(target: Path, agents: list[str], dry_run: bool) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for agent in agents:
        if agent == "codex":
            actions.append({**install_codex_hook(target, dry_run), "agent": agent})
        elif agent == "claude":
            actions.append({**install_claude_hook(target, dry_run), "agent": agent})
        elif agent == "cursor":
            actions.append({**install_cursor_hook(target, dry_run), "agent": agent})
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


def write_review_sentinel(
    target: Path,
    agent: str,
    agents: list[str],
    mode: str,
    apply_result: dict[str, Any],
    dry_run: bool,
) -> dict[str, str]:
    existing = read_json(target / POSTINSTALL_PATH)
    payload = {
        **sentinel_payload(agent, agents, mode, existing),
        "state": "needs_review",
        "reason": "obsolete runtime artifacts need review",
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
    if result.returncode != 0 and not failures:
        failures.append(result.stderr.strip() or result.stdout.strip() or "installed certification failed")
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
    if certification_status in {"NEEDS_REVIEW", "BLOCKED", "FAIL"}:
        return certification_status
    return "NEEDS_REVIEW"


# ADR 0004 capsule-first install. The capsule (.tes/**) is always written.
# Project-visible surfaces are attached only when explicitly requested.
ALL_ATTACH_SURFACES = ("mcp", "docs-mesh", "root-context", "hooks", "field-reports", "gps", "goals", "mantra")


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
    # ADR 0004: postinstall materializes project-visible docs/agents context via
    # tes_init. MCP and hooks are tool integrations and must not implicitly
    # promote the project into a TES-governed workspace.
    postinstall_disabled = args.no_postinstall or "docs-mesh" not in surfaces
    sentinel_action = (
        {"path": rel(target / POSTINSTALL_PATH, target), "action": "skip-capsule-only" if not args.no_postinstall else "skip-disabled"}
        if postinstall_disabled
        else (
            write_review_sentinel(target, args.agent, agents, args.postinstall_mode, apply_result, args.dry_run)
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
    return 1 if status in {"BLOCKED", "FAIL"} else 0


def parse_hook_input() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
    except OSError:
        return {}
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
    run_payload = {
        "schema": "tes-postinstall-run@1",
        "version": VERSION,
        "agent": args.agent,
        "target": str(target),
        "started_at": running["updated_at"],
        "completed_at": utc_stamp(),
        "status": status,
        "commands": results,
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
    if recover_needs_review:
        result["recovery"] = "needs_review"
    return (0 if not failed and not needs_cert_review else 1), result


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
    elif status == "RUNNING":
        lines.append("TES setup was already running before this hook returned.")
        lines.append("Ask the user to wait a moment, then run `/tes-setup` for the setup report.")
    elif status == "SKIP":
        lines.append("Postinstall did not run again because no pending work was required.")
    else:
        lines.append("TES postinstall needs review. Use `/tes-init` to inspect and recover before claiming GO.")
    return "\n".join(lines)


def claude_hook_output(result: dict[str, Any], hook_input: dict[str, Any]) -> dict[str, Any]:
    event_name = str(hook_input.get("hook_event_name") or "SessionStart")
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
    event_name = str(hook_input.get("hook_event_name") or "SessionStart")
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


HOOK_SENTINEL_PATH = Path(".tes/hooks/executed.jsonl")


def record_hook_execution(target: Path, agent: str, hook_input: dict[str, Any]) -> None:
    """ADR 0004 SPEC-005: prove the hook actually fired.

    Append a capsule-scoped sentinel record on every real hook invocation. The
    attach-health oracle reads this to certify a hook fired (vs config-written
    only) and to detect duplicate handlers per (agent, event, session). Best
    effort: a sentinel write must never break the hook itself.
    """
    try:
        event = str(hook_input.get("hookEventName") or hook_input.get("event") or "SessionStart")
        session = str(hook_input.get("session_id") or hook_input.get("sessionId") or os.getpid())
        sentinel = target / HOOK_SENTINEL_PATH
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        record = {"agent": agent, "event": event, "session": session, "ts": utc_stamp()}
        with sentinel.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        pass


def hook(args: argparse.Namespace) -> int:
    hook_input = parse_hook_input()
    if args.target == Path("."):
        inferred = hook_input.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR")
        if inferred:
            args.target = Path(str(inferred))
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
    record_hook_execution(target, args.agent, hook_input)
    if args.agent == "claude" and args.announce_start:
        print(json.dumps(claude_start_notice_output(target, hook_input), sort_keys=True))
        return 0
    code, result = postinstall(args, hook_input=hook_input)
    if args.agent == "claude":
        if args.rewake_on_complete:
            message = claude_rewake_message(result)
            if message:
                print(message, file=sys.stderr)
                return 2
            return 0
        print(json.dumps(claude_hook_output(result, hook_input), sort_keys=True))
        return 0
    if args.agent == "cursor":
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
        subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)
        install_result = subprocess.run(
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
            text=True,
            capture_output=True,
            check=False,
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
        subprocess.run(["git", "init"], cwd=partial_target, text=True, capture_output=True, check=False)
        partial_install = subprocess.run(
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
            text=True,
            capture_output=True,
            check=False,
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
        start_notice = subprocess.run(
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
            text=True,
            capture_output=True,
            check=False,
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
        hook_result = subprocess.run(
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
            text=True,
            capture_output=True,
            check=False,
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
        second_hook = subprocess.run(
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
            text=True,
            capture_output=True,
            check=False,
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
        recovery_result = subprocess.run(
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
            text=True,
            capture_output=True,
            check=False,
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
        recovery_skip = subprocess.run(
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
            text=True,
            capture_output=True,
            check=False,
        )
        if recovery_skip.returncode != 0 or "postinstall recovery only runs when the sentinel is needs_review" not in recovery_skip.stdout:
            failures.append("needs_review recovery must skip clean sentinels")
            failures.extend(recovery_skip.stdout.splitlines())
            failures.extend(recovery_skip.stderr.splitlines())

        with tempfile.TemporaryDirectory(prefix="tes-thin-install-claude-") as claude_tempdir:
            claude_target = Path(claude_tempdir)
            (claude_target / "README.md").write_text("# Claude Hook Fixture\n", encoding="utf-8")
            (claude_target / "package.json").write_text('{"name":"tes-claude-hook-fixture"}\n', encoding="utf-8")
            claude_install = subprocess.run(
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
                text=True,
                capture_output=True,
                check=False,
            )
            if claude_install.returncode != 0:
                failures.append("Claude-only install failed")
                failures.extend(claude_install.stdout.splitlines())
                failures.extend(claude_install.stderr.splitlines())
            if not (claude_target / ".claude/skills/tes-setup/SKILL.md").exists():
                failures.append("Claude-only install must deliver /tes-setup as a project skill")
            claude_start_notice = subprocess.run(
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
                text=True,
                capture_output=True,
                check=False,
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
            claude_first_hook = subprocess.run(
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
                text=True,
                capture_output=True,
                check=False,
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
            claude_complete_notice = subprocess.run(
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
                text=True,
                capture_output=True,
                check=False,
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
            claude_partial_install = subprocess.run(
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
                text=True,
                capture_output=True,
                check=False,
            )
            if claude_partial_install.returncode != 0:
                failures.append("Claude partial fixture install failed")
                failures.extend(claude_partial_install.stdout.splitlines())
                failures.extend(claude_partial_install.stderr.splitlines())
            (claude_partial_target / ".tes/bin/.DS_Store").write_text("neutral residue\n", encoding="utf-8")
            claude_partial_hook = subprocess.run(
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
                text=True,
                capture_output=True,
                check=False,
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
        dry_result = subprocess.run(
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
            text=True,
            capture_output=True,
            check=False,
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
        blocked_result = subprocess.run(
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
            text=True,
            capture_output=True,
            check=False,
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
            entrypoint_result = subprocess.run(
                command,
                cwd=source_root(),
                text=True,
                capture_output=True,
                check=False,
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
        choices=["all", "mcp", "docs-mesh", "root-context", "hooks", "field-reports", "gps", "goals", "mantra"],
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
    if args.command == "hook":
        return hook(args)
    if args.command == "status":
        return status(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
