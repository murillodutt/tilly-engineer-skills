"""Codex CLI MCP host adapter."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

from .base import HostAdapter

SERVER_NAME = "tes-cortex"
APPROVAL_MODES = {"auto", "prompt", "approve"}


class CodexHost(HostAdapter):
    name = "codex"
    config_path = Path(".codex/config.toml")
    supports_cwd = True
    supports_http = True
    supports_sse = False
    supports_timeouts = True
    supports_auth_block = False

    def allowed_fields(self, transport="stdio"):  # type: ignore[override]
        # Mirrors Codex config.toml MCP keys documented by OpenAI. Keep this
        # strict because Codex rejects unknown fields, but do not reject
        # supported per-tool policy subtables.
        shared = {
            "startup_timeout_sec", "tool_timeout_sec", "enabled", "required",
            "enabled_tools", "disabled_tools", "default_tools_approval_mode",
            "tools",
        }
        if transport == "http":
            return shared | {
                "url", "bearer_token_env_var", "http_headers", "env_http_headers",
            }
        return shared | {
            "command", "args", "env", "env_vars", "cwd", "experimental_environment",
        }

    def forbidden_fields(self, transport="stdio"):  # type: ignore[override]
        if transport == "http":
            return {"command", "args", "env", "cwd"}
        return {"url", "bearer_token_env_var", "http_headers", "env_http_headers"}

    def assert_entry_valid(self, entry, transport="stdio"):  # type: ignore[override]
        failures: list[str] = []
        if not isinstance(entry, dict):
            return failures
        keys = set(entry.keys())
        allowed = self.allowed_fields(transport)
        extras = keys - allowed
        if extras:
            failures.append(f"codex {transport} entry has unknown fields: {sorted(extras)}")
        forbidden = self.forbidden_fields(transport) & keys
        if forbidden:
            failures.append(f"codex {transport} entry has forbidden fields: {sorted(forbidden)}")
        mode = entry.get("default_tools_approval_mode")
        if mode is not None and mode not in APPROVAL_MODES:
            failures.append(
                "codex MCP default_tools_approval_mode must be one of "
                f"{sorted(APPROVAL_MODES)}"
            )
        tools = entry.get("tools")
        if tools is not None:
            failures.extend(self._validate_tools(tools))
        return failures

    def _validate_tools(self, tools):
        failures: list[str] = []
        if not isinstance(tools, dict):
            return ["codex MCP tools must be a table"]
        for tool_name, tool_config in tools.items():
            if not isinstance(tool_config, dict):
                failures.append(f"codex MCP tools.{tool_name} must be a table")
                continue
            extra = set(tool_config) - {"approval_mode"}
            if extra:
                failures.append(
                    f"codex MCP tools.{tool_name} has unknown fields: {sorted(extra)}"
                )
            mode = tool_config.get("approval_mode")
            if mode is not None and mode not in APPROVAL_MODES:
                failures.append(
                    f"codex MCP tools.{tool_name}.approval_mode must be one of "
                    f"{sorted(APPROVAL_MODES)}"
                )
        return failures

    def build_stdio(self, target, target_script, python, read_only):  # type: ignore[override]
        args = [
            json.dumps(target_script),
            json.dumps("--target"),
            json.dumps(str(target)),
        ]
        if read_only:
            args.append(json.dumps("--read-only"))
        return f"""[mcp_servers.tes-cortex]
command = {json.dumps(python)}
args = [{", ".join(args)}]
cwd = {json.dumps(str(target))}
startup_timeout_sec = 10
tool_timeout_sec = 60
enabled = true
"""

    def build_http(self, target, url, bearer_token_env_var=None, extra_headers=None, auth_block=None):  # type: ignore[override]
        if auth_block:
            raise ValueError("Codex MCP does not support an 'auth' block; use bearer_token_env_var")
        lines = [
            "[mcp_servers.tes-cortex]",
            f"url = {json.dumps(url)}",
            "startup_timeout_sec = 10",
            "tool_timeout_sec = 60",
            "enabled = true",
        ]
        if bearer_token_env_var:
            lines.insert(2, f"bearer_token_env_var = {json.dumps(bearer_token_env_var)}")
        snippet = "\n".join(lines) + "\n"
        if extra_headers:
            header_lines = [f"  {json.dumps(k)} = {json.dumps(v)}" for k, v in sorted(extra_headers.items())]
            snippet += "[mcp_servers.tes-cortex.http_headers]\n" + "\n".join(header_lines) + "\n"
        return snippet

    def merge_into_existing(  # type: ignore[override]
        self, target, dry_run, overwrite, backup, read_only,
        transport="stdio", url=None, bearer_token_env_var=None, auth_block=None,
    ):
        if auth_block:
            return None, "Codex MCP does not support an 'auth' block; use bearer_token_env_var"
        from install_mcp import (  # type: ignore
            python_command,
            rel,
            target_script,
            write_text_file,
        )

        if transport == "http":
            if not url:
                return None, "Codex HTTP install requires --url"
            snippet = self.build_http(target, url, bearer_token_env_var=bearer_token_env_var)
        else:
            snippet = self.build_stdio(
                target,
                target_script(target, "cortex_mcp.py"),
                python_command(),
                read_only,
            )
        path = target / self.config_path
        if not path.exists():
            action = write_text_file(path, snippet, dry_run, backup)
            action["path"] = rel(path, target)
            return action, None

        text = path.read_text(encoding="utf-8")
        if "[mcp_servers.tes-cortex]" in text:
            if snippet.strip() in text:
                return {"path": rel(path, target), "action": "skip-identical"}, None
            if not overwrite:
                return None, "conflicting Codex MCP config: .codex/config.toml"
            updated = _replace_toml_section(text, "[mcp_servers.tes-cortex]", snippet)
        else:
            updated = text.rstrip() + "\n\n" + snippet
        action = write_text_file(path, updated, dry_run, backup)
        action["path"] = rel(path, target)
        return action, None

    def remove_registration(self, target, dry_run=False, backup=True):  # type: ignore[override]
        """Inverse of the TOML merge: remove the [mcp_servers.tes-cortex] section,
        preserving other servers and the rest of config.toml (ADR 0004 L3 SPEC-001).
        """
        from install_mcp import rel, write_text_file  # type: ignore

        path = target / self.config_path
        if not path.exists():
            return {"path": rel(path, target), "action": "already-absent"}, None
        text = path.read_text(encoding="utf-8")
        if "[mcp_servers.tes-cortex]" in text:
            stripped = _remove_toml_section(text, "[mcp_servers.tes-cortex]")
        elif "[mcp_servers.tes-cortex]" not in text:
            return {"path": rel(path, target), "action": "no-tes-server"}, None
        else:
            stripped = text
        # If the file is now effectively empty (TES-only), remove it.
        if not stripped.strip():
            if not dry_run:
                path.unlink()
            return {"path": rel(path, target), "action": "would-remove-file" if dry_run else "remove-file"}, None
        action = write_text_file(path, stripped, dry_run, backup)
        action["path"] = rel(path, target)
        action["action"] = "would-remove-server" if dry_run else "remove-server"
        return action, None

    def validate_registered(  # type: ignore[override]
        self, target, read_only,
        transport="stdio", url=None, bearer_token_env_var=None, auth_block=None,
    ):
        from install_mcp import python_command, rel, target_script  # type: ignore

        adapter = self.name
        path = target / self.config_path
        if not path.exists():
            return (
                {"adapter": adapter, "path": rel(path, target), "status": "FAIL"},
                "missing Codex MCP config: .codex/config.toml",
            )
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            return (
                {"adapter": adapter, "path": rel(path, target), "status": "FAIL"},
                f"invalid TOML in .codex/config.toml: {exc}",
            )
        server = data.get("mcp_servers", {}).get(SERVER_NAME) if isinstance(data.get("mcp_servers"), dict) else None
        if not isinstance(server, dict):
            return (
                {"adapter": adapter, "path": rel(path, target), "status": "FAIL"},
                "Codex MCP config missing tes-cortex server",
            )
        # Apply deny_unknown_fields parity on the registered dict.
        drift_failures = self.assert_entry_valid(server, transport=transport)
        if drift_failures:
            return (
                {"adapter": adapter, "path": rel(path, target), "status": "FAIL"},
                "; ".join(drift_failures),
            )
        if transport == "http":
            if server.get("url") != url:
                return (
                    {"adapter": adapter, "path": rel(path, target), "status": "FAIL"},
                    "Codex HTTP MCP config has wrong url",
                )
            if bearer_token_env_var and server.get("bearer_token_env_var") != bearer_token_env_var:
                return (
                    {"adapter": adapter, "path": rel(path, target), "status": "FAIL"},
                    "Codex HTTP MCP config missing bearer_token_env_var",
                )
            return (
                {"adapter": adapter, "path": rel(path, target), "status": "PASS", "server": SERVER_NAME},
                None,
            )
        args = server.get("args")
        if (
            server.get("command") != python_command()
            or server.get("cwd") != str(target)
            or not isinstance(args, list)
            or target_script(target, "cortex_mcp.py") not in args
            or str(target) not in args
        ):
            return (
                {"adapter": adapter, "path": rel(path, target), "status": "FAIL"},
                "Codex MCP config has invalid tes-cortex command or args",
            )
        if read_only and "--read-only" not in args:
            return (
                {"adapter": adapter, "path": rel(path, target), "status": "FAIL"},
                "Codex read-only MCP config missing --read-only",
            )
        if not read_only and "--read-only" in args:
            return (
                {"adapter": adapter, "path": rel(path, target), "status": "FAIL"},
                "Codex default MCP config must expose governed remember tools",
            )
        return (
            {"adapter": adapter, "path": rel(path, target), "status": "PASS", "server": SERVER_NAME},
            None,
        )


def _replace_toml_section(text: str, header: str, replacement: str) -> str:
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == header)
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("[") and lines[idx].endswith("]"):
            end = idx
            break
    return "\n".join([*lines[:start], replacement.rstrip(), *lines[end:]]).rstrip() + "\n"


def _remove_toml_section(text: str, header: str) -> str:
    """Remove a TOML section (header through the line before the next section).

    Inverse of _replace_toml_section: drop the section entirely, preserving every
    other section and the file's leading content (ADR 0004 L3 SPEC-001).
    """
    lines = text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == header)
    except StopIteration:
        return text
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("[") and lines[idx].endswith("]"):
            end = idx
            break
    remaining = [*lines[:start], *lines[end:]]
    body = "\n".join(remaining).strip()
    return (body + "\n") if body else ""
