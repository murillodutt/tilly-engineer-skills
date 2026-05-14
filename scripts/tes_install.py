#!/usr/bin/env python3
"""Thin mechanical TES installer with first-session post-install bootstrap."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "0.3.92"
LOCK_PATH = Path(".tes/tes-install-lock.json")
POSTINSTALL_PATH = Path(".tes/postinstall.json")
POSTINSTALL_RUN_ROOT = Path(".tes/postinstall-runs")
AGENTS = ("codex", "claude", "cursor")
POSTINSTALL_STATES = {"pending", "running", "complete", "needs_review"}
DEFAULT_POSTINSTALL_COMMANDS = (
    ("tes_init.py", ("--target", "{target}", "--yes")),
    ("project_context_oracle.py", ("--target", "{target}")),
    ("project_alignment_oracle.py", ("--target", "{target}")),
)


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


def source_root() -> Path:
    return Path(__file__).resolve().parents[1]


def target_root(path: Path) -> Path:
    return path.expanduser().resolve()


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
    if dry_run:
        return {"path": rel(path, target), "action": "would-update" if path.exists() else "would-create"}
    backup_path = None
    if path.exists() and backup:
        backup_path = path.with_name(f"{path.name}.bak-{file_stamp()}")
        shutil.copy2(path, backup_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    result = {"path": rel(path, target), "action": "update" if backup_path else "create"}
    if backup_path:
        result["backup"] = rel(backup_path, target)
    return result


def codex_hook_snippet() -> str:
    return """# TES first-session post-install hook.
[[hooks.SessionStart]]
matcher = "startup|resume"

[[hooks.SessionStart.hooks]]
type = "command"
command = 'python3 "$(git rev-parse --show-toplevel)/.tes/bin/tes_install.py" hook --agent codex --target "$(git rev-parse --show-toplevel)"'
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
    return write_text_if_changed(path, updated, target, dry_run)


def hook_entry(agent: str) -> dict[str, Any]:
    if agent == "claude":
        return {
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
    if agent == "cursor":
        return {
            "command": "python3 .tes/bin/tes_install.py hook --agent cursor --target .",
            "timeout": 120,
        }
    raise ValueError(f"unsupported hook entry agent: {agent}")


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
    for group in groups:
        if not isinstance(group, dict):
            continue
        if matcher and str(group.get("matcher", "")) != matcher:
            continue
        handlers = group.get("hooks", [])
        if not isinstance(handlers, list):
            continue
        if any(json.dumps(handler, sort_keys=True) == marker for handler in handlers if isinstance(handler, dict)):
            return
    groups.append({"matcher": matcher, "hooks": [entry]})


def install_claude_hook(target: Path, dry_run: bool) -> dict[str, str]:
    path = target / ".claude/settings.json"
    data = read_json(path)
    ensure_hook_group(data, "SessionStart", "startup|resume", hook_entry("claude"))
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
        "runs": runs,
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


def write_install_lock(
    target: Path,
    agent: str,
    agents: list[str],
    mode: str,
    stage: dict[str, Any],
    apply_result: dict[str, Any],
    hook_actions: list[dict[str, str]],
    dry_run: bool,
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
        "apply": summarize_result(apply_result),
        "hooks": hook_actions,
    }
    return write_json(target / LOCK_PATH, lock, dry_run=dry_run)


def summarize_result(result: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key in ("version", "status", "source", "stage_dir", "manifest", "entries", "mode", "backup_id", "installed_manifest"):
        if key in result:
            summary[key] = result[key]
    if result.get("failures"):
        summary["failures"] = result["failures"]
    return summary


def install(args: argparse.Namespace) -> int:
    target = target_root(args.target)
    if not target.exists() or not target.is_dir():
        print("[tes-install] FAIL")
        print(f"- target is not a directory: {target}")
        return 1
    if not require_confirmation(args, "tes-install"):
        return 1

    agents = selected_agents(args.agent)
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
        )
        if apply_result.get("status") not in {"APPLIED", "CLEAN_APPLIED", "DRY-RUN"}:
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

    hook_actions = [] if args.no_hooks else install_hooks(target, agents, args.dry_run)
    sentinel_action = (
        {"path": rel(target / POSTINSTALL_PATH, target), "action": "skip-disabled"}
        if args.no_postinstall
        else write_pending_sentinel(target, args.agent, agents, args.postinstall_mode, args.dry_run)
    )
    lock_action = write_install_lock(target, args.agent, agents, args.mode, stage, apply_result, hook_actions, args.dry_run)
    result = {
        "version": VERSION,
        "status": "DRY-RUN" if args.dry_run else "INSTALLED",
        "target": str(target),
        "agent": args.agent,
        "agents": agents,
        "mode": args.mode,
        "stage": summarize_result(stage),
        "apply": summarize_result(apply_result),
        "hooks": hook_actions,
        "postinstall": sentinel_action,
        "lock": lock_action,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-install] " + result["status"])
    return 0


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
    return {
        "command": " ".join(command),
        "returncode": result.returncode,
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def append_run_record(target: Path, payload: dict[str, Any], dry_run: bool) -> dict[str, str]:
    path = target / POSTINSTALL_RUN_ROOT / f"{file_stamp()}-{payload['agent']}.json"
    return write_json(path, payload, dry_run=dry_run)


def postinstall(args: argparse.Namespace, hook_input: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    target = target_root(args.target)
    sentinel_path = target / POSTINSTALL_PATH
    sentinel = read_json(sentinel_path)
    state = str(sentinel.get("state") or "")
    if state not in POSTINSTALL_STATES and not args.force:
        result = {"version": VERSION, "status": "SKIP", "reason": "no postinstall sentinel", "target": str(target)}
        return 0, result
    if state == "complete" and not args.force:
        result = {"version": VERSION, "status": "SKIP", "reason": "postinstall already complete", "target": str(target)}
        return 0, result
    if state == "needs_review" and not args.force:
        result = {"version": VERSION, "status": "NEEDS_REVIEW", "reason": "previous postinstall needs review", "target": str(target)}
        return 0, result
    if args.dry_run:
        result = {"version": VERSION, "status": "DRY-RUN", "target": str(target), "actions": ["would-run-postinstall"]}
        return 0, result

    running = {
        **sentinel_payload(args.agent, selected_agents(args.agent) if args.agent != "all" else list(AGENTS), args.mode, sentinel),
        "state": "running",
        "updated_at": utc_stamp(),
    }
    write_json(sentinel_path, running)
    commands = [] if args.skip_project_init else list(DEFAULT_POSTINSTALL_COMMANDS)
    results = [run_helper(target, script, script_args, args.timeout) for script, script_args in commands]
    failed = [item for item in results if item["returncode"] != 0]
    final_state = "needs_review" if failed else "complete"
    status = "NEEDS_REVIEW" if failed else "PASS"
    run_payload = {
        "schema": "tes-postinstall-run@1",
        "version": VERSION,
        "agent": args.agent,
        "target": str(target),
        "started_at": running["updated_at"],
        "completed_at": utc_stamp(),
        "status": status,
        "commands": results,
        "hook_input_keys": sorted((hook_input or {}).keys()),
    }
    run_record = append_run_record(target, run_payload, dry_run=False)
    run_record_rel = rel(Path(run_record["path"]), target)
    runs = running.get("runs") if isinstance(running.get("runs"), list) else []
    complete_payload = {
        **running,
        "state": final_state,
        "updated_at": utc_stamp(),
        "completed_at": utc_stamp() if final_state == "complete" else None,
        "last_status": status,
        "last_run": run_record_rel,
        "runs": [*runs, run_record_rel],
    }
    if failed:
        complete_payload["failures"] = [
            {"command": item["command"], "returncode": item["returncode"], "stderr": item["stderr"][:1000]}
            for item in failed
        ]
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
    }
    return (0 if not failed else 1), result


def hook(args: argparse.Namespace) -> int:
    hook_input = parse_hook_input()
    if args.target == Path("."):
        inferred = hook_input.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR")
        if inferred:
            args.target = Path(str(inferred))
    code, result = postinstall(args, hook_input=hook_input)
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
    with tempfile.TemporaryDirectory(prefix="tes-thin-install-") as tempdir:
        target = Path(tempdir)
        (target / "README.md").write_text("# Thin Installer Fixture\n\nA test project.\n", encoding="utf-8")
        (target / "package.json").write_text(
            json.dumps({"name": "tes-thin-fixture", "scripts": {"test": "echo test"}}, indent=2) + "\n",
            encoding="utf-8",
        )
        (target / "src").mkdir()
        (target / "src/app.py").write_text("print('thin')\n", encoding="utf-8")
        subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)
        install_result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "install",
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
        for relpath in (
            ".tes/bin/tes_install.py",
            ".tes/tes-install-lock.json",
            ".tes/postinstall.json",
            ".codex/config.toml",
            ".claude/settings.json",
            ".cursor/hooks.json",
            ".tes/manifest.json",
        ):
            if not (target / relpath).exists():
                failures.append(f"missing installed path: {relpath}")
        sentinel = read_json(target / POSTINSTALL_PATH)
        if sentinel.get("state") != "pending":
            failures.append("postinstall sentinel must be pending after install")
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

    with tempfile.TemporaryDirectory(prefix="tes-thin-install-dry-") as tempdir:
        target = Path(tempdir)
        dry_result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "install",
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

    postinstall_parser = subparsers.add_parser("postinstall")
    postinstall_parser.add_argument("--target", type=Path, default=Path.cwd())
    postinstall_parser.add_argument("--agent", default="codex", choices=["all", *AGENTS])
    postinstall_parser.add_argument("--mode", default="first-session")
    postinstall_parser.add_argument("--timeout", type=float, default=120.0)
    postinstall_parser.add_argument("--dry-run", action="store_true")
    postinstall_parser.add_argument("--force", action="store_true")
    postinstall_parser.add_argument("--skip-project-init", action="store_true")

    hook_parser = subparsers.add_parser("hook")
    hook_parser.add_argument("--target", type=Path, default=Path.cwd())
    hook_parser.add_argument("--agent", default="codex", choices=AGENTS)
    hook_parser.add_argument("--mode", default="first-session")
    hook_parser.add_argument("--timeout", type=float, default=120.0)
    hook_parser.add_argument("--dry-run", action="store_true")
    hook_parser.add_argument("--force", action="store_true")
    hook_parser.add_argument("--skip-project-init", action="store_true")

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--target", type=Path, default=Path.cwd())

    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.command == "install":
        return install(args)
    if args.command == "postinstall":
        code, result = postinstall(args)
        print(json.dumps(result, indent=2, sort_keys=True))
        print("[tes-postinstall] " + result["status"])
        return code
    if args.command == "hook":
        return hook(args)
    if args.command == "status":
        return status(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
