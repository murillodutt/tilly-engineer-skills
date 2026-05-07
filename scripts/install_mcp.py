#!/usr/bin/env python3
"""Install project-scoped Tilly Cortex MCP activation files."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.12"
SERVER_NAME = "tilly-cortex"
BIN_DIR = Path(".tilly/bin")
SERVER_FILES = ("cortex.py", "cortex_mcp.py")
ADAPTERS = ("codex", "claude", "cursor")


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def selected_adapters(adapter: str) -> list[str]:
    if adapter == "all":
        return list(ADAPTERS)
    return [adapter]


def source_script(name: str) -> Path:
    path = ROOT / "scripts" / name
    if not path.exists():
        raise FileNotFoundError(f"missing source script: scripts/{name}")
    return path


def backup_file(path: Path) -> Path:
    backup = path.with_name(f"{path.name}.bak-{utc_stamp()}")
    shutil.copy2(path, backup)
    return backup


def write_text_file(path: Path, text: str, dry_run: bool, backup: bool) -> dict[str, str]:
    encoded = text.encode("utf-8")
    existed = path.exists()
    if path.exists():
        current = path.read_bytes()
        if current == encoded:
            return {"path": str(path), "action": "skip-identical", "sha": sha256_bytes(encoded)}
        if dry_run:
            return {"path": str(path), "action": "would-update", "sha": sha256_bytes(encoded)}
        backup_path = backup_file(path) if backup else None
    else:
        if dry_run:
            return {"path": str(path), "action": "would-create", "sha": sha256_bytes(encoded)}
        backup_path = None

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    action = "update" if existed else "create"
    result = {"path": str(path), "action": action, "sha": sha256_bytes(encoded)}
    if backup_path:
        result["backup"] = str(backup_path)
    return result


def install_server_files(target: Path, dry_run: bool, overwrite: bool, backup: bool) -> tuple[list[dict[str, str]], list[str]]:
    actions: list[dict[str, str]] = []
    failures: list[str] = []
    for name in SERVER_FILES:
        source = source_script(name)
        target_path = target / BIN_DIR / name
        source_sha = sha256_file(source)
        if target_path.exists():
            target_sha = sha256_file(target_path)
            if target_sha == source_sha:
                actions.append(
                    {
                        "path": rel(target_path, target),
                        "source": str(source),
                        "action": "skip-identical",
                        "sha": source_sha,
                    }
                )
                continue
            if not overwrite:
                failures.append(f"conflicting MCP helper: {rel(target_path, target)}")
                continue
            if dry_run:
                actions.append(
                    {
                        "path": rel(target_path, target),
                        "source": str(source),
                        "action": "would-overwrite",
                        "sha": source_sha,
                    }
                )
                continue
            backup_path = backup_file(target_path) if backup else None
        else:
            if dry_run:
                actions.append(
                    {
                        "path": rel(target_path, target),
                        "source": str(source),
                        "action": "would-copy",
                        "sha": source_sha,
                    }
                )
                continue
            backup_path = None

        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target_path)
        action = {
            "path": rel(target_path, target),
            "source": str(source),
            "action": "overwrite" if backup_path else "copy",
            "sha": source_sha,
        }
        if backup_path:
            action["backup"] = rel(backup_path, target)
        actions.append(action)
    return actions, failures


def codex_snippet() -> str:
    return """[mcp_servers.tilly-cortex]
command = "python3"
args = [".tilly/bin/cortex_mcp.py", "--target", "."]
cwd = "."
startup_timeout_sec = 10
tool_timeout_sec = 60
enabled = true
"""


def merge_codex_config(target: Path, dry_run: bool, overwrite: bool, backup: bool) -> tuple[dict[str, str] | None, str | None]:
    path = target / ".codex/config.toml"
    snippet = codex_snippet()
    if not path.exists():
        action = write_text_file(path, snippet, dry_run, backup)
        action["path"] = rel(path, target)
        return action, None

    text = path.read_text(encoding="utf-8")
    if "[mcp_servers.tilly-cortex]" in text:
        if snippet.strip() in text:
            return {"path": rel(path, target), "action": "skip-identical"}, None
        if not overwrite:
            return None, "conflicting Codex MCP config: .codex/config.toml"
        updated = replace_toml_section(text, "[mcp_servers.tilly-cortex]", snippet)
    else:
        updated = text.rstrip() + "\n\n" + snippet
    action = write_text_file(path, updated, dry_run, backup)
    action["path"] = rel(path, target)
    return action, None


def replace_toml_section(text: str, header: str, replacement: str) -> str:
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == header)
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("[") and lines[idx].endswith("]"):
            end = idx
            break
    return "\n".join([*lines[:start], replacement.rstrip(), *lines[end:]]).rstrip() + "\n"


def json_config(adapter: str) -> dict[str, Any]:
    if adapter == "cursor":
        args = ["${workspaceFolder}/.tilly/bin/cortex_mcp.py", "--target", "${workspaceFolder}"]
    else:
        args = [".tilly/bin/cortex_mcp.py", "--target", "."]
    return {
        "type": "stdio",
        "command": "python3",
        "args": args,
        "env": {},
    }


def merge_json_config(
    target: Path,
    adapter: str,
    dry_run: bool,
    overwrite: bool,
    backup: bool,
) -> tuple[dict[str, str] | None, str | None]:
    path = target / (".mcp.json" if adapter == "claude" else ".cursor/mcp.json")
    desired_server = json_config(adapter)
    data: dict[str, Any]
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return None, f"invalid JSON in {rel(path, target)}: {exc}"
        if not isinstance(data, dict):
            return None, f"{rel(path, target)} must contain a JSON object"
    else:
        data = {}

    servers = data.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        return None, f"{rel(path, target)} mcpServers must be an object"
    existing = servers.get(SERVER_NAME)
    if existing == desired_server:
        return {"path": rel(path, target), "action": "skip-identical"}, None
    if existing is not None and not overwrite:
        return None, f"conflicting {adapter} MCP config: {rel(path, target)}"

    servers[SERVER_NAME] = desired_server
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    action = write_text_file(path, text, dry_run, backup)
    action["path"] = rel(path, target)
    return action, None


def install_configs(
    target: Path,
    adapters: list[str],
    dry_run: bool,
    overwrite: bool,
    backup: bool,
) -> tuple[list[dict[str, str]], list[str]]:
    actions: list[dict[str, str]] = []
    failures: list[str] = []
    for adapter in adapters:
        if adapter == "codex":
            action, failure = merge_codex_config(target, dry_run, overwrite, backup)
        else:
            action, failure = merge_json_config(target, adapter, dry_run, overwrite, backup)
        if failure:
            failures.append(failure)
        if action:
            action["adapter"] = adapter
            actions.append(action)
    return actions, failures


def require_confirmation(args: argparse.Namespace) -> bool:
    if args.dry_run or args.yes:
        return True
    if not sys.stdin.isatty():
        print("[install-mcp] FAIL")
        print("- write mode requires --yes when stdin is not interactive")
        return False
    answer = input("Install Tilly Cortex MCP into target project? Type 'yes' to continue: ")
    if answer.strip().lower() != "yes":
        print("[install-mcp] CANCELLED")
        return False
    return True


def install(args: argparse.Namespace) -> int:
    target = args.target.expanduser().resolve()
    if not target.exists() or not target.is_dir():
        print("[install-mcp] FAIL")
        print(f"- target is not a directory: {target}")
        return 1

    if not require_confirmation(args):
        return 1

    adapters = selected_adapters(args.adapter)
    server_actions, server_failures = install_server_files(target, args.dry_run, args.overwrite, not args.no_backup)
    config_actions, config_failures = install_configs(target, adapters, args.dry_run, args.overwrite, not args.no_backup)
    failures = [*server_failures, *config_failures]
    status = "FAIL" if failures else ("DRY-RUN" if args.dry_run else "INSTALLED")
    result = {
        "version": VERSION,
        "status": status,
        "target": str(target),
        "adapter": args.adapter,
        "server": SERVER_NAME,
        "server_files": server_actions,
        "configs": config_actions,
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    if failures:
        print("[install-mcp] FAIL")
        return 2
    print("[install-mcp] PASS")
    return 0


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="tilly-mcp-install-") as tempdir:
        target = Path(tempdir)
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/cortex.py"), "init", "--target", str(target)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        failures: list[str] = []
        if result.returncode != 0:
            failures.append("cortex init failed")
        install_result = subprocess.run(
            [sys.executable, __file__, "--target", str(target), "--adapter", "all", "--yes"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if install_result.returncode != 0:
            failures.append("install all failed")
            failures.extend(install_result.stdout.splitlines())
            failures.extend(install_result.stderr.splitlines())
        for relpath in (
            ".tilly/bin/cortex.py",
            ".tilly/bin/cortex_mcp.py",
            ".codex/config.toml",
            ".mcp.json",
            ".cursor/mcp.json",
        ):
            if not (target / relpath).exists():
                failures.append(f"missing installed path: {relpath}")
        mcp_self_test = subprocess.run(
            [sys.executable, str(target / ".tilly/bin/cortex_mcp.py"), "--self-test"],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
        )
        if mcp_self_test.returncode != 0:
            failures.append("installed cortex_mcp.py --self-test failed")
            failures.extend(mcp_self_test.stdout.splitlines())
            failures.extend(mcp_self_test.stderr.splitlines())

    print(json.dumps({"status": "FAIL" if failures else "PASS", "failures": failures}, indent=2))
    if failures:
        print("[install-mcp] FAIL")
        return 1
    print("[install-mcp] PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", default="all", choices=["all", *ADAPTERS])
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true", help="confirm writes without an interactive prompt")
    parser.add_argument("--overwrite", action="store_true", help="replace existing tilly-cortex MCP entries")
    parser.add_argument("--no-backup", action="store_true", help="do not create .bak-* files before overwrite")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    return install(args)


if __name__ == "__main__":
    sys.exit(main())
