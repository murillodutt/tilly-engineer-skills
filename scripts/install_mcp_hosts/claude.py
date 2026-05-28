"""Claude Code CLI MCP host adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import HostAdapter, merge_json_server, validate_json_server


class ClaudeHost(HostAdapter):
    name = "claude"
    config_path = Path(".mcp.json")
    server_key = "mcpServers"
    supports_cwd = False
    supports_http = True
    supports_sse = False
    supports_timeouts = False
    supports_auth_block = False

    def allowed_fields(self, transport="stdio"):  # type: ignore[override]
        # Reference: McpStdioServerConfig / McpHttpServerConfig in
        # code.claude.com/docs/en/agent-sdk/python.
        if transport == "http":
            return {"type", "url", "headers"}
        return {"type", "command", "args", "env"}

    def forbidden_fields(self, transport="stdio"):  # type: ignore[override]
        # Claude Code does not support cwd in either transport.
        if transport == "http":
            return {"command", "args", "env", "cwd"}
        return {"url", "headers", "cwd"}

    def build_stdio(self, target, target_script, python, read_only):  # type: ignore[override]
        args = [target_script, "--target", str(target)]
        if read_only:
            args.append("--read-only")
        return {
            "type": "stdio",
            "command": python,
            "args": args,
            "env": {},
        }

    def build_http(self, target, url, bearer_token_env_var=None, extra_headers=None):  # type: ignore[override]
        # Claude Code McpHttpServerConfig.
        # Reference: code.claude.com/docs/en/agent-sdk/python.
        headers: dict[str, str] = dict(extra_headers or {})
        if bearer_token_env_var:
            headers["Authorization"] = f"Bearer ${{env:{bearer_token_env_var}}}"
        entry: dict[str, Any] = {"type": "http", "url": url}
        if headers:
            entry["headers"] = headers
        return entry

    def _desired(self, target, read_only, transport, url, bearer_token_env_var):
        from install_mcp import python_command, target_script  # type: ignore

        if transport == "http":
            if not url:
                raise ValueError("Claude HTTP install requires --url")
            entry = self.build_http(target, url, bearer_token_env_var=bearer_token_env_var)
        else:
            entry = self.build_stdio(
                target, target_script(target, "cortex_mcp.py"), python_command(), read_only
            )
        validation_failures = self.assert_entry_valid(entry, transport=transport)
        if validation_failures:
            raise ValueError("; ".join(validation_failures))
        return entry

    def merge_into_existing(  # type: ignore[override]
        self, target, dry_run, overwrite, backup, read_only,
        transport="stdio", url=None, bearer_token_env_var=None,
    ):
        try:
            desired = self._desired(target, read_only, transport, url, bearer_token_env_var)
        except ValueError as exc:
            return None, str(exc)
        return merge_json_server(
            self.name, target, self.config_path, self.server_key,
            desired, dry_run, overwrite, backup,
        )

    def validate_registered(  # type: ignore[override]
        self, target, read_only,
        transport="stdio", url=None, bearer_token_env_var=None,
    ):
        try:
            expected = self._desired(target, read_only, transport, url, bearer_token_env_var)
        except ValueError as exc:
            return (
                {"adapter": self.name, "path": str(self.config_path), "status": "FAIL"},
                str(exc),
            )
        return validate_json_server(
            self.name, target, self.config_path, self.server_key, expected
        )
