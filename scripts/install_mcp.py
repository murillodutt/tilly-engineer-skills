#!/usr/bin/env python3
"""Install project-scoped TES Cortex MCP activation files."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import field_reports
import tes_bundle

SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[1]

if str(SCRIPT_PATH.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT_PATH.parent))

from install_mcp_hosts import HOSTS  # noqa: E402
VERSION = "0.3.251"
SERVER_NAME = "tes-cortex"
BIN_DIR = Path(".tes/bin")
SERVER_FILES = (
    "install_mcp.py",
    "install_mcp_hosts/__init__.py",
    "install_mcp_hosts/base.py",
    "install_mcp_hosts/codex.py",
    "install_mcp_hosts/claude.py",
    "install_mcp_hosts/cursor.py",
    "install_mcp_hosts/vscode.py",
    "cortex.py",
    "cortex_runtime.py",
    "tes_codex_policy.py",
    "pretooluse_kernel.py",
    "pretooluse_session.py",
    "cortex_mcp.py",
    "cortex_embed.mjs",
    "scope_contract.py",
    "event_ledger.py",
    "checkpoint.py",
    "consolidation_gate.py",
    "field_reports.py",
    "git_gate_contract.py",
    "mantra_gate.py",
    "mantra_gate_adoption_oracle.py",
    "tes_install.py",
    "tes_update.py",
    "tes_legacy_retirement.py",
    "root_context.py",
    "root_context_sanctioned_oracle.py",
    "context_distill_coverage_oracle.py",
    "tes_init.py",
    "verify_documentation_inventory.py",
    "project_context_oracle.py",
    "project_alignment_oracle.py",
    "tes_project_atlas.py",
    "tes_map.py",
    "tes_map_oracle.py",
    "tes_open_obsidian.py",
    "command_trigger_oracle.py",
    "tes_bundle.py",
    "materialize_adapter.py",
)
ADAPTERS = ("codex", "claude", "cursor", "vscode")
# Helper-adjacent assets copied beside .tes/bin helpers (mirrors tes_bundle bundled_assets).
HELPER_BUNDLED_ASSETS = (
    "fixtures/INVENTORY-HYGIENE.minimal.yml",
    "fixtures/cortex_host_contracts/claude-code.json",
    "fixtures/cortex_host_contracts/codex.json",
    "fixtures/cortex_host_contracts/cursor.json",
    "fixtures/cortex_host_contracts/negative-flat-contract.json",
)


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
        path = SCRIPT_PATH.parent / name
    if not path.exists():
        raise FileNotFoundError(f"missing source script/helper: {name}")
    return path


def source_package_mode() -> bool:
    # Source package mode requires both the install script and the adapter
    # source tree the bundle needs to materialize. The public bundle ships
    # only scripts/**, so the extracted target stays in installed-helper mode.
    return (ROOT / "scripts/install_mcp.py").exists() and (ROOT / "src/adapters").exists()


def python_command() -> str:
    executable = Path(sys.executable)
    if executable.is_absolute() and executable.exists():
        return str(executable)
    resolved = shutil.which(sys.executable) or shutil.which("python3")
    return resolved or "python3"


def target_script(target: Path, name: str) -> str:
    return str((target / BIN_DIR / name).resolve())


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
        try:
            source = source_script(name)
        except FileNotFoundError as exc:
            failures.append(str(exc))
            continue
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

    for relpath in HELPER_BUNDLED_ASSETS:
        try:
            source = source_script(relpath)
        except FileNotFoundError as exc:
            failures.append(str(exc))
            continue
        target_path = target / BIN_DIR / relpath
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
                failures.append(f"conflicting MCP helper asset: {rel(target_path, target)}")
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


def validate_config_registrations(
    target: Path,
    adapters: list[str],
    read_only: bool,
    transport: str = "stdio",
    url: str | None = None,
    bearer_token_env_var: str | None = None,
    auth_block: dict[str, Any] | None = None,
) -> tuple[list[dict[str, str]], list[str]]:
    registrations: list[dict[str, str]] = []
    failures: list[str] = []
    for adapter in adapters:
        registration, failure = HOSTS[adapter].validate_registered(
            target, read_only,
            transport=transport, url=url, bearer_token_env_var=bearer_token_env_var,
            auth_block=auth_block if adapter == "cursor" else None,
        )
        registrations.append(registration)
        if failure:
            failures.append(failure)
    return registrations, failures


def install_configs(
    target: Path,
    adapters: list[str],
    dry_run: bool,
    overwrite: bool,
    backup: bool,
    read_only: bool,
    transport: str = "stdio",
    url: str | None = None,
    bearer_token_env_var: str | None = None,
    auth_block: dict[str, Any] | None = None,
) -> tuple[list[dict[str, str]], list[str]]:
    actions: list[dict[str, str]] = []
    failures: list[str] = []
    for adapter in adapters:
        action, failure = HOSTS[adapter].merge_into_existing(
            target, dry_run, overwrite, backup, read_only,
            transport=transport, url=url, bearer_token_env_var=bearer_token_env_var,
            auth_block=auth_block if adapter == "cursor" else None,
        )
        if failure:
            failures.append(failure)
        if action:
            action["adapter"] = adapter
            actions.append(action)
    return actions, failures


def remove_configs(
    target: Path,
    adapters: list[str],
    dry_run: bool,
    backup: bool,
) -> tuple[list[dict[str, str]], list[str]]:
    """Inverse of install_configs (ADR 0004 L3 SPEC-001): remove the TES MCP
    server entry from each adapter, preserving user-owned servers and config."""
    actions: list[dict[str, str]] = []
    failures: list[str] = []
    for adapter in adapters:
        action, failure = HOSTS[adapter].remove_registration(target, dry_run, backup)
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
    answer = input("Install TES Cortex MCP into target project? Type 'yes' to continue: ")
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
    blocked = tes_bundle.package_source_block(target, "install_mcp")
    if blocked:
        print(json.dumps(blocked, indent=2))
        if not args.json_only:
            print("[install-mcp] BLOCKED")
        return 2

    if not require_confirmation(args):
        return 1

    if not args.dry_run:
        field_reports.ensure_git_exclude(target)

    read_only = bool(args.read_only or args.disable_writes)
    adapters = selected_adapters(args.adapter)
    transport = args.transport
    bearer_env = args.bearer_env
    url = args.url
    auth_block: dict[str, Any] | None = None
    if args.auth_client_id_env:
        auth_block = {"CLIENT_ID": f"${{env:{args.auth_client_id_env}}}"}
        if args.auth_client_secret_env:
            auth_block["CLIENT_SECRET"] = f"${{env:{args.auth_client_secret_env}}}"
        if args.auth_scope:
            auth_block["scopes"] = list(args.auth_scope)
    elif args.auth_client_secret_env or args.auth_scope:
        print("[install-mcp] FAIL")
        print("- --auth-client-secret-env and --auth-scope require --auth-client-id-env")
        return 1
    if transport == "http" and not url:
        url = f"http://{args.host}:{args.port}/mcp"
    if transport == "http" and not args.allow_non_localhost:
        host_part = ""
        if url:
            from urllib.parse import urlparse
            host_part = urlparse(url).hostname or ""
        if host_part and host_part not in {"127.0.0.1", "localhost", "::1"}:
            print("[install-mcp] FAIL")
            print(f"- HTTP install binds to localhost by default; pass --allow-non-localhost to use {host_part}")
            return 1
    bundle_adapter = "all" if args.adapter == "vscode" else args.adapter
    bundle_stage = (
        tes_bundle.stage_preferred_bundle(target, dry_run=args.dry_run, adapter=bundle_adapter)
        if source_package_mode()
        else {
            "version": VERSION,
            "status": "SKIP",
            "source": "installed-helper",
            "reason": "source package unavailable; using installed .tes/bin helpers",
        }
    )
    server_actions, server_failures = install_server_files(target, args.dry_run, args.overwrite, not args.no_backup)
    config_actions, config_failures = (
        ([], [])
        if args.helpers_only
        else install_configs(
            target, adapters, args.dry_run, args.overwrite, not args.no_backup, read_only,
            transport=transport, url=url, bearer_token_env_var=bearer_env, auth_block=auth_block,
        )
    )
    config_registrations, registration_failures = (
        ([], [])
        if args.helpers_only or args.dry_run or config_failures
        else validate_config_registrations(
            target, adapters, read_only,
            transport=transport, url=url, bearer_token_env_var=bearer_env, auth_block=auth_block,
        )
    )
    bundle_failures = bundle_stage.get("failures", []) if bundle_stage.get("status") == "FAIL" else []
    failures = [*bundle_failures, *server_failures, *config_failures, *registration_failures]
    status = "FAIL" if failures else ("DRY-RUN" if args.dry_run else "INSTALLED")
    result = {
        "version": VERSION,
        "status": status,
        "target": str(target),
        "adapter": args.adapter,
        "route": args.adapter,
        "helpers_only": args.helpers_only,
        "governed_writes": not read_only,
        "write_capable": not read_only,
        "read_only": read_only,
        "transport": transport,
        "url": url,
        "bearer_env": bearer_env,
        "auth_client_id_env": args.auth_client_id_env,
        "auth_client_secret_env": args.auth_client_secret_env,
        "auth_scopes": args.auth_scope,
        "bundle_stage": bundle_stage,
        "server": SERVER_NAME,
        "server_files": server_actions,
        "configs": config_actions,
        "config_registrations": config_registrations,
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    if not args.dry_run:
        field_reports.safe_record_event(
            target,
            "install_mcp",
            status,
            "mcp",
            "cli",
            details={
                "adapter": args.adapter,
                "route": args.adapter,
                "helpers_only": args.helpers_only,
                "governed_writes": not read_only,
                "write_capable": not read_only,
                "read_only": read_only,
                "transport": transport,
                "bearer_env": bearer_env,
                "auth_client_id_env": args.auth_client_id_env,
                "auth_client_secret_env": args.auth_client_secret_env,
                "dry_run": args.dry_run,
                "failures": len(failures),
            },
        )
    if failures:
        if not args.json_only:
            print("[install-mcp] FAIL")
        return 2
    if not args.json_only:
        print("[install-mcp] PASS")
    return 0


def _golden_stdio_failures() -> list[str]:
    """Golden assertions for per-host stdio builders against fixed inputs."""
    failures: list[str] = []
    fixture_target = Path("/abs/target")
    fixture_python = "/abs/python"
    fixture_script = "/abs/target/.tes/bin/cortex_mcp.py"

    codex_default = HOSTS["codex"].build_stdio(fixture_target, fixture_script, fixture_python, False)
    expected_codex_default = (
        '[mcp_servers.tes-cortex]\n'
        'command = "/abs/python"\n'
        'args = ["/abs/target/.tes/bin/cortex_mcp.py", "--target", "/abs/target"]\n'
        'cwd = "/abs/target"\n'
        'startup_timeout_sec = 10\n'
        'tool_timeout_sec = 60\n'
        'enabled = true\n'
    )
    if codex_default != expected_codex_default:
        failures.append("codex golden stdio default drift")
    codex_read_only = HOSTS["codex"].build_stdio(fixture_target, fixture_script, fixture_python, True)
    expected_codex_read_only = (
        '[mcp_servers.tes-cortex]\n'
        'command = "/abs/python"\n'
        'args = ["/abs/target/.tes/bin/cortex_mcp.py", "--target", "/abs/target", "--read-only"]\n'
        'cwd = "/abs/target"\n'
        'startup_timeout_sec = 10\n'
        'tool_timeout_sec = 60\n'
        'enabled = true\n'
    )
    if codex_read_only != expected_codex_read_only:
        failures.append("codex golden stdio read-only drift")

    expected_json_default = {
        "type": "stdio",
        "command": "/abs/python",
        "args": ["/abs/target/.tes/bin/cortex_mcp.py", "--target", "/abs/target"],
        "env": {},
    }
    expected_json_read_only = {
        "type": "stdio",
        "command": "/abs/python",
        "args": ["/abs/target/.tes/bin/cortex_mcp.py", "--target", "/abs/target", "--read-only"],
        "env": {},
    }
    for host_name in ("claude", "cursor", "vscode"):
        actual_default = HOSTS[host_name].build_stdio(fixture_target, fixture_script, fixture_python, False)
        if actual_default != expected_json_default:
            failures.append(f"{host_name} golden stdio default drift: {actual_default}")
        actual_read_only = HOSTS[host_name].build_stdio(fixture_target, fixture_script, fixture_python, True)
        if actual_read_only != expected_json_read_only:
            failures.append(f"{host_name} golden stdio read-only drift: {actual_read_only}")

    if HOSTS["vscode"].server_key != "servers":
        failures.append("vscode adapter must use server_key='servers' per VS Code workspace MCP schema")
    if HOSTS["claude"].server_key != "mcpServers":
        failures.append("claude adapter must use server_key='mcpServers'")
    if HOSTS["cursor"].server_key != "mcpServers":
        failures.append("cursor adapter must use server_key='mcpServers'")
    if HOSTS["claude"].supports_cwd is not False:
        failures.append("claude adapter must declare supports_cwd=False per Claude Code MCP schema")

    fixture_url = "http://127.0.0.1:8765/mcp"
    codex_http = HOSTS["codex"].build_http(fixture_target, fixture_url)
    expected_codex_http = (
        '[mcp_servers.tes-cortex]\n'
        'url = "http://127.0.0.1:8765/mcp"\n'
        'startup_timeout_sec = 10\n'
        'tool_timeout_sec = 60\n'
        'enabled = true\n'
    )
    if codex_http != expected_codex_http:
        failures.append(f"codex golden http drift: {codex_http!r}")
    expected_json_http = {"type": "http", "url": fixture_url}
    for host_name in ("claude", "cursor", "vscode"):
        actual_http = HOSTS[host_name].build_http(fixture_target, fixture_url)
        if actual_http != expected_json_http:
            failures.append(f"{host_name} golden http drift: {actual_http}")

    codex_http_bearer = HOSTS["codex"].build_http(fixture_target, fixture_url, bearer_token_env_var="TES_TOKEN")
    if 'bearer_token_env_var = "TES_TOKEN"' not in codex_http_bearer:
        failures.append("codex bearer_token_env_var missing from http snippet")
    claude_http_bearer = HOSTS["claude"].build_http(fixture_target, fixture_url, bearer_token_env_var="TES_TOKEN")
    if claude_http_bearer.get("headers", {}).get("Authorization") != "Bearer ${env:TES_TOKEN}":
        failures.append("claude bearer Authorization header missing")
    cursor_http_bearer = HOSTS["cursor"].build_http(fixture_target, fixture_url, bearer_token_env_var="TES_TOKEN")
    if cursor_http_bearer.get("headers", {}).get("Authorization") != "Bearer ${env:TES_TOKEN}":
        failures.append("cursor bearer Authorization header missing")
    vscode_http_bearer = HOSTS["vscode"].build_http(fixture_target, fixture_url, bearer_token_env_var="TES_TOKEN")
    if "${input:" not in str(vscode_http_bearer.get("headers", {}).get("Authorization", "")):
        failures.append("vscode bearer Authorization must use ${input:...} interpolation")

    # Negative validation: forbidden/unknown fields per host.
    codex_tool_policy = HOSTS["codex"].assert_entry_valid(
        {
            "command": "/x",
            "args": [],
            "tools": {"cortex_health": {"approval_mode": "approve"}},
            "enabled_tools": ["cortex_health"],
            "disabled_tools": ["cortex_apply"],
            "default_tools_approval_mode": "prompt",
            "required": True,
            "env_vars": ["LOCAL_TOKEN"],
            "experimental_environment": "remote",
        },
        "stdio",
    )
    if codex_tool_policy:
        failures.append(f"codex valid tool policy fields rejected: {codex_tool_policy}")
    codex_unknown = HOSTS["codex"].assert_entry_valid({"command": "/x", "args": [], "secret": "boom"}, "stdio")
    if not codex_unknown:
        failures.append("codex strict validation must reject unknown field (deny_unknown_fields parity)")
    codex_bad_tool_policy = HOSTS["codex"].assert_entry_valid(
        {"command": "/x", "args": [], "tools": {"cortex_health": {"approval_mode": "always"}}},
        "stdio",
    )
    if not codex_bad_tool_policy:
        failures.append("codex tool policy validation must reject invalid approval mode")
    codex_http_forbidden = HOSTS["codex"].assert_entry_valid({"url": "u", "command": "/x"}, "http")
    if not codex_http_forbidden:
        failures.append("codex http must forbid command in StreamableHttp variant")
    claude_cwd = HOSTS["claude"].assert_entry_valid({"type": "stdio", "command": "/x", "cwd": "/y"}, "stdio")
    if not claude_cwd:
        failures.append("claude must forbid cwd (Claude Code MCP schema)")
    cursor_http_cwd = HOSTS["cursor"].assert_entry_valid({"type": "http", "url": "u", "cwd": "/y"}, "http")
    if not cursor_http_cwd:
        failures.append("cursor http must forbid cwd (Cursor cloud rejects cwd)")
    vscode_unknown = HOSTS["vscode"].assert_entry_valid({"type": "stdio", "command": "/x", "bogus": 1}, "stdio")
    if not vscode_unknown:
        failures.append("vscode must reject unknown field")
    return failures


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="tes-mcp-install-") as tempdir:
        target = Path(tempdir).resolve()
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/cortex.py"), "init", "--target", str(target)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        failures: list[str] = _golden_stdio_failures()
        if result.returncode != 0:
            failures.append("cortex init failed")
        (target / ".vscode").mkdir(parents=True, exist_ok=True)
        (target / ".vscode/mcp.json").write_text(
            json.dumps(
                {
                    "servers": {
                        "existing-server": {
                            "type": "http",
                            "url": "https://example.invalid/mcp",
                        }
                    }
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
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
        required_paths = [
            ".tes/bin/install_mcp.py",
            ".tes/bin/cortex.py",
            ".tes/bin/cortex_runtime.py",
            ".tes/bin/cortex_mcp.py",
            ".tes/bin/cortex_embed.mjs",
            ".tes/bin/field_reports.py",
            ".tes/bin/tes_install.py",
            ".tes/bin/tes_update.py",
            ".tes/bin/tes_legacy_retirement.py",
            ".tes/bin/root_context.py",
            ".tes/bin/tes_init.py",
            ".tes/bin/project_context_oracle.py",
            ".tes/bin/project_alignment_oracle.py",
            ".tes/bin/tes_project_atlas.py",
            ".tes/bin/tes_map.py",
            ".tes/bin/tes_map_oracle.py",
            ".tes/bin/tes_open_obsidian.py",
            ".tes/bin/command_trigger_oracle.py",
            ".tes/bin/tes_bundle.py",
            ".tes/bin/materialize_adapter.py",
            ".codex/config.toml",
            ".mcp.json",
            ".cursor/mcp.json",
            ".vscode/mcp.json",
        ]
        # Source-package mode stages a bundle manifest; installed-helper mode does not.
        if source_package_mode():
            required_paths.append(f".tes/setup/{VERSION}/tes-bundle-manifest.json")
        for relpath in required_paths:
            if not (target / relpath).exists():
                failures.append(f"missing installed path: {relpath}")
        mcp_self_test = subprocess.run(
            [sys.executable, str(target / ".tes/bin/cortex_mcp.py"), "--self-test"],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
        )
        if mcp_self_test.returncode != 0:
            failures.append("installed cortex_mcp.py --self-test failed")
            failures.extend(mcp_self_test.stdout.splitlines())
            failures.extend(mcp_self_test.stderr.splitlines())
        codex_config = (target / ".codex/config.toml").read_text(encoding="utf-8")
        if "--read-only" in codex_config:
            failures.append("default Codex MCP install must expose governed remember tools")
        if "--enable-writes" in codex_config:
            failures.append("default Codex MCP install must not need legacy --enable-writes")
        codex_data = tomllib.loads(codex_config)
        codex_server = codex_data.get("mcp_servers", {}).get(SERVER_NAME)
        if not isinstance(codex_server, dict):
            failures.append("default Codex MCP install must create mcp_servers.tes-cortex")
        else:
            codex_args = codex_server.get("args")
            if codex_server.get("command") != python_command():
                failures.append("default Codex MCP install must use the active Python executable")
            if codex_server.get("cwd") != str(target):
                failures.append("default Codex MCP install must use absolute target cwd")
            if not isinstance(codex_args, list) or target_script(target, "cortex_mcp.py") not in codex_args or str(target) not in codex_args:
                failures.append("default Codex MCP install must use absolute target args")
        codex_policy_config = codex_config.rstrip() + (
            "\n\n[mcp_servers.tes-cortex.tools.cortex_health]\n"
            "approval_mode = \"approve\"\n"
        )
        (target / ".codex/config.toml").write_text(codex_policy_config, encoding="utf-8")
        _, codex_policy_err = HOSTS["codex"].validate_registered(target, read_only=False)
        if codex_policy_err:
            failures.append(f"codex validate_registered must accept per-tool policy: {codex_policy_err}")
        (target / ".codex/config.toml").write_text(codex_config, encoding="utf-8")
        for relpath in (".mcp.json", ".cursor/mcp.json", ".vscode/mcp.json"):
            data = json.loads((target / relpath).read_text(encoding="utf-8"))
            server_key = "servers" if relpath == ".vscode/mcp.json" else "mcpServers"
            server = data[server_key][SERVER_NAME]
            args = server["args"]
            if server.get("command") != python_command():
                failures.append(f"default {relpath} MCP install must use the active Python executable")
            if target_script(target, "cortex_mcp.py") not in args or str(target) not in args:
                failures.append(f"default {relpath} MCP install must use absolute target args")
            if any(str(arg).startswith("${workspaceFolder}") or str(arg) in {".", ".tes/bin/cortex_mcp.py"} for arg in args):
                failures.append(f"default {relpath} MCP install must not depend on host cwd or workspace interpolation")
            if "--read-only" in args:
                failures.append(f"default {relpath} MCP install must expose governed remember tools")
            if "--enable-writes" in args:
                failures.append(f"default {relpath} MCP install must not need legacy --enable-writes")
            if relpath == ".vscode/mcp.json" and "existing-server" not in data["servers"]:
                failures.append("VS Code MCP install must preserve existing servers")

        (target / ".vscode/mcp.json").unlink()
        installed_repair_result = subprocess.run(
            [
                sys.executable,
                str(target / ".tes/bin/install_mcp.py"),
                "--target",
                str(target),
                "--adapter",
                "vscode",
                "--yes",
                "--json-only",
            ],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
        )
        if installed_repair_result.returncode != 0:
            failures.append("installed helper MCP repair failed")
            failures.extend(installed_repair_result.stdout.splitlines())
            failures.extend(installed_repair_result.stderr.splitlines())
        else:
            try:
                repair_payload = json.loads(installed_repair_result.stdout)
            except json.JSONDecodeError as exc:
                failures.append(f"installed helper MCP repair returned invalid JSON: {exc}")
            else:
                registrations = repair_payload.get("config_registrations")
                registration_items = registrations if isinstance(registrations, list) else []
                if repair_payload.get("status") != "INSTALLED":
                    failures.append("installed helper MCP repair must return INSTALLED")
                if repair_payload.get("bundle_stage", {}).get("source") != "installed-helper":
                    failures.append("installed helper MCP repair must use installed-helper source")
                if not any(
                    isinstance(item, dict)
                    and item.get("adapter") == "vscode"
                    and item.get("status") == "PASS"
                    and item.get("server_key") == "servers"
                    for item in registration_items
                ):
                    failures.append("installed helper MCP repair must validate VS Code server registration")
            repaired = target / ".vscode/mcp.json"
            if not repaired.exists():
                failures.append("installed helper MCP repair did not recreate .vscode/mcp.json")

    with tempfile.TemporaryDirectory(prefix="tes-mcp-read-only-install-") as tempdir:
        target = Path(tempdir).resolve()
        init_result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/cortex.py"), "init", "--target", str(target)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if init_result.returncode != 0:
            failures.append("read-only cortex init failed")
        read_only_install_result = subprocess.run(
            [
                sys.executable,
                __file__,
                "--target",
                str(target),
                "--adapter",
                "all",
                "--read-only",
                "--yes",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if read_only_install_result.returncode != 0:
            failures.append("read-only install all failed")
            failures.extend(read_only_install_result.stdout.splitlines())
            failures.extend(read_only_install_result.stderr.splitlines())
        elif "--read-only" not in (target / ".codex/config.toml").read_text(encoding="utf-8"):
            failures.append("read-only Codex MCP install must include --read-only")
        for relpath in (".mcp.json", ".cursor/mcp.json", ".vscode/mcp.json"):
            if not (target / relpath).exists():
                failures.append(f"read-only install missing config: {relpath}")
                continue
            data = json.loads((target / relpath).read_text(encoding="utf-8"))
            server_key = "servers" if relpath == ".vscode/mcp.json" else "mcpServers"
            args = data[server_key][SERVER_NAME]["args"]
            if "--read-only" not in args:
                failures.append(f"read-only {relpath} MCP install must include --read-only")

    with tempfile.TemporaryDirectory(prefix="tes-mcp-http-install-") as tempdir:
        target = Path(tempdir).resolve()
        init_result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/cortex.py"), "init", "--target", str(target)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        if init_result.returncode != 0:
            failures.append("http cortex init failed")
        http_install_result = subprocess.run(
            [sys.executable, __file__, "--target", str(target), "--adapter", "all",
             "--transport", "http", "--port", "8765", "--yes"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        if http_install_result.returncode != 0:
            failures.append("http install all failed")
            failures.extend(http_install_result.stdout.splitlines())
            failures.extend(http_install_result.stderr.splitlines())
        else:
            codex_http_text = (target / ".codex/config.toml").read_text(encoding="utf-8")
            if 'url = "http://127.0.0.1:8765/mcp"' not in codex_http_text:
                failures.append("http codex install missing StreamableHttp url")
            if "command =" in codex_http_text.split("[mcp_servers.tes-cortex]", 1)[1]:
                failures.append("http codex install must not emit command for StreamableHttp variant")
            for relpath in (".mcp.json", ".cursor/mcp.json", ".vscode/mcp.json"):
                if not (target / relpath).exists():
                    failures.append(f"http install missing config: {relpath}")
                    continue
                data = json.loads((target / relpath).read_text(encoding="utf-8"))
                server_key = "servers" if relpath == ".vscode/mcp.json" else "mcpServers"
                entry = data[server_key][SERVER_NAME]
                if entry.get("type") != "http":
                    failures.append(f"http {relpath} install must register type=http")
                if entry.get("url") != "http://127.0.0.1:8765/mcp":
                    failures.append(f"http {relpath} install must register expected url")
                if "command" in entry or "args" in entry:
                    failures.append(f"http {relpath} install must not emit command/args")

        non_local_result = subprocess.run(
            [sys.executable, __file__, "--target", str(target), "--adapter", "claude",
             "--transport", "http", "--url", "https://remote.example.invalid/mcp",
             "--overwrite", "--yes"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        if non_local_result.returncode == 0:
            failures.append("non-localhost http install was not rejected")
        if "allow-non-localhost" not in non_local_result.stdout + non_local_result.stderr:
            failures.append("non-localhost http install must hint about --allow-non-localhost")

    # SPEC-007: bearer-env authenticated HTTP install with privacy self-test.
    with tempfile.TemporaryDirectory(prefix="tes-mcp-bearer-install-") as tempdir:
        target = Path(tempdir).resolve()
        init_result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/cortex.py"), "init", "--target", str(target)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        if init_result.returncode != 0:
            failures.append("bearer cortex init failed")
        bearer_secret = "super-secret-not-stored"
        env = {**dict(__import__("os").environ), "TES_BEARER_TOKEN": bearer_secret}
        bearer_result = subprocess.run(
            [sys.executable, __file__, "--target", str(target), "--adapter", "all",
             "--transport", "http", "--port", "8765", "--bearer-env", "TES_BEARER_TOKEN", "--yes"],
            cwd=ROOT, text=True, capture_output=True, check=False, env=env,
        )
        if bearer_result.returncode != 0:
            failures.append("bearer-env http install all failed")
            failures.extend(bearer_result.stdout.splitlines())
            failures.extend(bearer_result.stderr.splitlines())
        else:
            combined_output = bearer_result.stdout + bearer_result.stderr
            if bearer_secret in combined_output:
                failures.append("bearer-env install leaked secret value in stdout/stderr")
            codex_text = (target / ".codex/config.toml").read_text(encoding="utf-8")
            if 'bearer_token_env_var = "TES_BEARER_TOKEN"' not in codex_text:
                failures.append("codex bearer install must emit bearer_token_env_var")
            if bearer_secret in codex_text:
                failures.append("codex bearer install leaked secret value to TOML")
            for relpath, host_key in (
                (".mcp.json", "mcpServers"),
                (".cursor/mcp.json", "mcpServers"),
                (".vscode/mcp.json", "servers"),
            ):
                data_text = (target / relpath).read_text(encoding="utf-8")
                if bearer_secret in data_text:
                    failures.append(f"{relpath} bearer install leaked secret value")
                data = json.loads(data_text)
                entry = data[host_key][SERVER_NAME]
                authorization = entry.get("headers", {}).get("Authorization", "")
                if "Bearer ${" not in authorization:
                    failures.append(f"{relpath} bearer install must interpolate Authorization header")
                if bearer_secret in authorization:
                    failures.append(f"{relpath} bearer install must not embed secret value")
                if relpath == ".vscode/mcp.json":
                    inputs = data.get("inputs")
                    if not isinstance(inputs, list) or not inputs:
                        failures.append(".vscode/mcp.json bearer install must emit top-level inputs[]")
                    else:
                        input_ids = [i.get("id") for i in inputs]
                        expected_id = "tes-bearer-token-token"
                        if expected_id not in input_ids:
                            failures.append(f".vscode/mcp.json inputs must include {expected_id}, got {input_ids}")
                        if not any(i.get("type") == "promptString" for i in inputs):
                            failures.append(".vscode/mcp.json inputs must declare type=promptString")
                        if f"${{input:{expected_id}}}" not in authorization:
                            failures.append(f".vscode/mcp.json Authorization must reference ${{input:{expected_id}}}")
            event_path = target / ".tes/events/ledger.jsonl"
            if event_path.exists() and bearer_secret in event_path.read_text(encoding="utf-8"):
                failures.append("bearer-env install leaked secret value into event ledger")

    # SPEC-007 supplement: Cursor auth block via --auth-client-id-env.
    with tempfile.TemporaryDirectory(prefix="tes-mcp-cursor-auth-") as tempdir:
        target = Path(tempdir).resolve()
        init_result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/cortex.py"), "init", "--target", str(target)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        if init_result.returncode != 0:
            failures.append("cursor-auth cortex init failed")
        client_secret = "client-secret-must-not-leak"
        env = {**dict(__import__("os").environ),
               "TES_CURSOR_CLIENT_ID": "cid", "TES_CURSOR_CLIENT_SECRET": client_secret}
        auth_result = subprocess.run(
            [sys.executable, __file__, "--target", str(target), "--adapter", "cursor",
             "--transport", "http", "--port", "8765",
             "--auth-client-id-env", "TES_CURSOR_CLIENT_ID",
             "--auth-client-secret-env", "TES_CURSOR_CLIENT_SECRET",
             "--auth-scope", "read:cortex", "--auth-scope", "write:cortex",
             "--yes"],
            cwd=ROOT, text=True, capture_output=True, check=False, env=env,
        )
        if auth_result.returncode != 0:
            failures.append("cursor auth install failed")
            failures.extend(auth_result.stdout.splitlines())
            failures.extend(auth_result.stderr.splitlines())
        else:
            if client_secret in auth_result.stdout + auth_result.stderr:
                failures.append("cursor auth install leaked client secret in stdout/stderr")
            data = json.loads((target / ".cursor/mcp.json").read_text(encoding="utf-8"))
            entry = data["mcpServers"][SERVER_NAME]
            auth = entry.get("auth")
            if not isinstance(auth, dict):
                failures.append("cursor auth install must emit auth block")
            else:
                if auth.get("CLIENT_ID") != "${env:TES_CURSOR_CLIENT_ID}":
                    failures.append(f"cursor auth.CLIENT_ID must interpolate env var, got {auth.get('CLIENT_ID')}")
                if auth.get("CLIENT_SECRET") != "${env:TES_CURSOR_CLIENT_SECRET}":
                    failures.append(f"cursor auth.CLIENT_SECRET must interpolate env var, got {auth.get('CLIENT_SECRET')}")
                if auth.get("scopes") != ["read:cortex", "write:cortex"]:
                    failures.append(f"cursor auth.scopes mismatch, got {auth.get('scopes')}")
            if client_secret in (target / ".cursor/mcp.json").read_text(encoding="utf-8"):
                failures.append("cursor auth install leaked client secret to config file")

        # Negative: auth flags rejected on non-Cursor adapters silently (auth ignored).
        # Codex must fail loud if auth is passed.
        codex_auth = HOSTS["codex"].merge_into_existing(
            target, dry_run=True, overwrite=True, backup=False, read_only=False,
            transport="http", url="http://127.0.0.1:8765/mcp",
            auth_block={"CLIENT_ID": "x"},
        )
        if codex_auth[1] is None:
            failures.append("codex must reject auth_block; got success")

    # SPEC-006 supplement: on-disk drift detection per host.
    with tempfile.TemporaryDirectory(prefix="tes-mcp-drift-") as tempdir:
        target = Path(tempdir).resolve()
        init_result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/cortex.py"), "init", "--target", str(target)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        if init_result.returncode != 0:
            failures.append("drift cortex init failed")
        baseline = subprocess.run(
            [sys.executable, __file__, "--target", str(target), "--adapter", "all",
             "--transport", "http", "--port", "8765", "--yes"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        if baseline.returncode != 0:
            failures.append("drift baseline http install failed")

        # Inject drift into Codex TOML.
        codex_path = target / ".codex/config.toml"
        codex_text = codex_path.read_text(encoding="utf-8")
        drifted_codex = codex_text.replace(
            "enabled = true\n",
            "enabled = true\nunexpected_field = \"drift\"\n",
            1,
        )
        codex_path.write_text(drifted_codex, encoding="utf-8")
        reg, err = HOSTS["codex"].validate_registered(
            target, read_only=False, transport="http", url="http://127.0.0.1:8765/mcp",
        )
        if err is None:
            failures.append("codex validate_registered must detect unknown_field drift in TOML")

        # Inject drift into Claude JSON.
        claude_path = target / ".mcp.json"
        claude_data = json.loads(claude_path.read_text(encoding="utf-8"))
        claude_data["mcpServers"][SERVER_NAME]["cwd"] = "/forbidden"
        claude_path.write_text(json.dumps(claude_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        reg, err = HOSTS["claude"].validate_registered(
            target, read_only=False, transport="http", url="http://127.0.0.1:8765/mcp",
        )
        if err is None:
            failures.append("claude validate_registered must detect cwd drift in JSON")

        # Inject drift into VS Code JSON (unknown field in server entry).
        vscode_path = target / ".vscode/mcp.json"
        vscode_data = json.loads(vscode_path.read_text(encoding="utf-8"))
        vscode_data["servers"][SERVER_NAME]["bogus_field"] = 1
        vscode_path.write_text(json.dumps(vscode_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        reg, err = HOSTS["vscode"].validate_registered(
            target, read_only=False, transport="http", url="http://127.0.0.1:8765/mcp",
        )
        if err is None:
            failures.append("vscode validate_registered must detect bogus_field drift in JSON")

    with tempfile.TemporaryDirectory(prefix="tes-mcp-legacy-enable-install-") as tempdir:
        target = Path(tempdir).resolve()
        init_result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/cortex.py"), "init", "--target", str(target)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if init_result.returncode != 0:
            failures.append("legacy-enable cortex init failed")
        legacy_install_result = subprocess.run(
            [
                sys.executable,
                __file__,
                "--target",
                str(target),
                "--adapter",
                "all",
                "--enable-writes",
                "--yes",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if legacy_install_result.returncode != 0:
            failures.append("legacy --enable-writes install failed")
            failures.extend(legacy_install_result.stdout.splitlines())
            failures.extend(legacy_install_result.stderr.splitlines())
        else:
            if "--read-only" in (target / ".codex/config.toml").read_text(encoding="utf-8"):
                failures.append("legacy --enable-writes install must not create read-only config")
            vscode_args = json.loads((target / ".vscode/mcp.json").read_text(encoding="utf-8"))["servers"][SERVER_NAME]["args"]
            if "--read-only" in vscode_args:
                failures.append("legacy --enable-writes install must not create read-only VS Code config")

    with tempfile.TemporaryDirectory(prefix="tes-mcp-helpers-only-") as tempdir:
        target = Path(tempdir).resolve()
        helpers_only_result = subprocess.run(
            [sys.executable, __file__, "--target", str(target), "--adapter", "all", "--helpers-only", "--yes", "--json-only"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if helpers_only_result.returncode != 0:
            failures.append("helpers-only install failed")
            failures.extend(helpers_only_result.stdout.splitlines())
            failures.extend(helpers_only_result.stderr.splitlines())
        else:
            try:
                payload = json.loads(helpers_only_result.stdout)
            except json.JSONDecodeError as exc:
                failures.append(f"helpers-only --json-only returned invalid JSON: {exc}")
            else:
                if payload.get("helpers_only") is not True:
                    failures.append("helpers-only install must mark helpers_only=true")
                if payload.get("configs"):
                    failures.append("helpers-only install must not write MCP configs")
        for relpath in SERVER_FILES:
            if not (target / BIN_DIR / relpath).exists():
                failures.append(f"helpers-only install missing helper: {relpath}")
        for relpath in (".codex/config.toml", ".mcp.json", ".cursor/mcp.json", ".vscode/mcp.json"):
            if (target / relpath).exists():
                failures.append(f"helpers-only install wrote config: {relpath}")
        for relpath in (
            "root_context.py",
            "tes_update.py",
            "tes_init.py",
            "project_context_oracle.py",
            "project_alignment_oracle.py",
            "tes_project_atlas.py",
            "tes_map.py",
            "tes_map_oracle.py",
            "tes_open_obsidian.py",
            "command_trigger_oracle.py",
        ):
            helper_self_test = subprocess.run(
                [sys.executable, str(target / BIN_DIR / relpath), "--self-test"],
                cwd=target,
                text=True,
                capture_output=True,
                check=False,
            )
            if helper_self_test.returncode != 0:
                failures.append(f"installed helper self-test failed: {relpath}")
                failures.extend(helper_self_test.stdout.splitlines())
                failures.extend(helper_self_test.stderr.splitlines())
                continue
            json_text = "\n".join(
                line for line in helper_self_test.stdout.splitlines()
                if not line.startswith("[")
            )
            try:
                payload = json.loads(json_text)
            except json.JSONDecodeError as exc:
                failures.append(f"installed helper self-test returned invalid JSON: {relpath}: {exc}")
                continue
            if payload.get("self_test_mode") != "installed":
                failures.append(f"installed helper self-test must report installed mode: {relpath}")
            if payload.get("coverage") != "installed-helper-contract":
                failures.append(f"installed helper self-test must report installed coverage: {relpath}")

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
    parser.add_argument("--overwrite", action="store_true", help="replace existing tes-cortex MCP entries")
    parser.add_argument(
        "--enable-writes",
        action="store_true",
        help="compatibility flag; governed Cortex remember MCP tools are enabled by default",
    )
    parser.add_argument("--read-only", action="store_true", help="install MCP config with governed remember tools hidden")
    parser.add_argument("--disable-writes", action="store_true", help="alias for --read-only")
    parser.add_argument("--helpers-only", action="store_true", help="copy only TES helper files under .tes/bin/**")
    parser.add_argument("--no-backup", action="store_true", help="do not create .bak-* files before overwrite")
    parser.add_argument("--transport", choices=("stdio", "http"), default="stdio", help="MCP transport to register")
    parser.add_argument("--host", default="127.0.0.1", help="HTTP host for the registered URL (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="HTTP port for the registered URL (default 8765)")
    parser.add_argument("--url", default=None, help="explicit HTTP URL; overrides --host/--port")
    parser.add_argument("--allow-non-localhost", action="store_true", help="allow HTTP URLs outside localhost")
    parser.add_argument("--bearer-env", default=None, help="environment variable name for HTTP bearer token")
    parser.add_argument("--auth-client-id-env", default=None,
                        help="env var name for OAuth CLIENT_ID (Cursor auth block); never read by installer")
    parser.add_argument("--auth-client-secret-env", default=None,
                        help="env var name for OAuth CLIENT_SECRET (Cursor auth block); never read by installer")
    parser.add_argument("--auth-scope", action="append", default=None,
                        help="OAuth scope for Cursor auth block; repeat to add multiple scopes")
    parser.add_argument("--json-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if args.enable_writes and (args.read_only or args.disable_writes):
        parser.error("--enable-writes cannot be combined with --read-only/--disable-writes")
    return install(args)


if __name__ == "__main__":
    sys.exit(main())
