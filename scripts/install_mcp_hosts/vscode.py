"""VS Code MCP host adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import HostAdapter, merge_json_server, validate_json_server


class VSCodeHost(HostAdapter):
    name = "vscode"
    config_path = Path(".vscode/mcp.json")
    server_key = "servers"
    supports_cwd = True
    supports_http = True
    supports_sse = True
    supports_timeouts = False
    supports_auth_block = False

    def allowed_fields(self, transport="stdio"):  # type: ignore[override]
        # Reference: VS Code workspace MCP schema.
        if transport == "http":
            return {"type", "url", "headers"}
        return {"type", "command", "args", "env", "cwd"}

    def forbidden_fields(self, transport="stdio"):  # type: ignore[override]
        if transport == "http":
            return {"command", "args", "env", "cwd"}
        return {"url", "headers"}

    @staticmethod
    def input_id(bearer_token_env_var: str) -> str:
        return f"{bearer_token_env_var.lower().replace('_', '-')}-token"

    @classmethod
    def input_entry(cls, bearer_token_env_var: str) -> dict[str, Any]:
        # VS Code workspace MCP inputs[] schema, type: promptString.
        # Reference: code.visualstudio.com/docs/copilot/reference/mcp-configuration.
        return {
            "id": cls.input_id(bearer_token_env_var),
            "type": "promptString",
            "description": f"Bearer token for tes-cortex MCP ({bearer_token_env_var})",
            "password": True,
        }

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
        if auth_block:
            raise ValueError("VS Code MCP does not support an 'auth' block; use bearer-env inputs")
        # VS Code workspace MCP http server entry.
        headers: dict[str, str] = dict(extra_headers or {})
        if bearer_token_env_var:
            headers["Authorization"] = f"Bearer ${{input:{self.input_id(bearer_token_env_var)}}}"
        entry: dict[str, Any] = {"type": "http", "url": url}
        if headers:
            entry["headers"] = headers
        return entry

    def _desired(self, target, read_only, transport, url, bearer_token_env_var, auth_block=None):
        from install_mcp import python_command, target_script  # type: ignore

        if transport == "http":
            if not url:
                raise ValueError("VS Code HTTP install requires --url")
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

    def _extra_top_level(self, transport, bearer_token_env_var):
        if transport == "http" and bearer_token_env_var:
            return {"inputs": [self.input_entry(bearer_token_env_var)]}
        return None

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
            extra_top_level=self._extra_top_level(transport, bearer_token_env_var),
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
            expected_top_level=self._extra_top_level(transport, bearer_token_env_var),
            adapter=self, transport=transport,
        )
