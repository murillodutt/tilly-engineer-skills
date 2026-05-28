"""Cursor MCP host adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import HostAdapter, merge_json_server, validate_json_server


class CursorHost(HostAdapter):
    name = "cursor"
    config_path = Path(".cursor/mcp.json")
    server_key = "mcpServers"
    supports_cwd = True
    supports_http = True
    supports_sse = True
    supports_timeouts = False
    supports_auth_block = True

    def allowed_fields(self, transport="stdio"):  # type: ignore[override]
        # Reference: McpServerConfig in cursor.com/docs/sdk/typescript.
        if transport == "http":
            return {"type", "url", "headers", "auth"}
        return {"type", "command", "args", "env", "cwd"}

    def forbidden_fields(self, transport="stdio"):  # type: ignore[override]
        # cwd is rejected by Cursor cloud in any HTTP-style scenario.
        if transport == "http":
            return {"command", "args", "env", "cwd"}
        return {"url", "headers", "auth"}

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

    def build_http(self, target, url, bearer_token_env_var=None, extra_headers=None, auth_block=None):  # type: ignore[override]
        # Cursor McpServerConfig http variant.
        # Reference: cursor.com/docs/sdk/typescript.
        headers: dict[str, str] = dict(extra_headers or {})
        if bearer_token_env_var:
            headers["Authorization"] = f"Bearer ${{env:{bearer_token_env_var}}}"
        entry: dict[str, Any] = {"type": "http", "url": url}
        if headers:
            entry["headers"] = headers
        if auth_block:
            # Sensitive fields are redacted by Cursor backend before VM sees them.
            entry["auth"] = dict(auth_block)
        return entry

    def _desired(self, target, read_only, transport, url, bearer_token_env_var, auth_block=None):
        from install_mcp import python_command, target_script  # type: ignore

        if transport == "http":
            if not url:
                raise ValueError("Cursor HTTP install requires --url")
            entry = self.build_http(
                target, url, bearer_token_env_var=bearer_token_env_var, auth_block=auth_block
            )
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
        transport="stdio", url=None, bearer_token_env_var=None, auth_block=None,
    ):
        try:
            desired = self._desired(target, read_only, transport, url, bearer_token_env_var, auth_block)
        except ValueError as exc:
            return None, str(exc)
        return merge_json_server(
            self.name, target, self.config_path, self.server_key,
            desired, dry_run, overwrite, backup,
        )

    def validate_registered(  # type: ignore[override]
        self, target, read_only,
        transport="stdio", url=None, bearer_token_env_var=None, auth_block=None,
    ):
        try:
            expected = self._desired(target, read_only, transport, url, bearer_token_env_var, auth_block)
        except ValueError as exc:
            return (
                {"adapter": self.name, "path": str(self.config_path), "status": "FAIL"},
                str(exc),
            )
        return validate_json_server(
            self.name, target, self.config_path, self.server_key, expected,
            adapter=self, transport=transport,
        )
