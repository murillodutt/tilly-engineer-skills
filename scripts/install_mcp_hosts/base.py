"""HostAdapter base contract for project-scoped Cortex MCP install."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

SERVER_NAME = "tes-cortex"


class HostAdapter(ABC):
    """Base contract for per-host MCP config builders and validators."""

    name: str = ""
    config_path: Path = Path()
    server_key: str = "mcpServers"
    supports_cwd: bool = False
    supports_http: bool = False
    supports_sse: bool = False
    supports_timeouts: bool = False
    supports_auth_block: bool = False

    @abstractmethod
    def build_stdio(
        self,
        target: Path,
        target_script: str,
        python: str,
        read_only: bool,
    ) -> Any:
        """Return the host-native server entry for stdio transport."""

    @abstractmethod
    def build_http(
        self,
        target: Path,
        url: str,
        bearer_token_env_var: str | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Any:
        """Return the host-native server entry for HTTP transport."""

    @abstractmethod
    def merge_into_existing(
        self,
        target: Path,
        dry_run: bool,
        overwrite: bool,
        backup: bool,
        read_only: bool,
        transport: str = "stdio",
        url: str | None = None,
        bearer_token_env_var: str | None = None,
    ) -> tuple[dict[str, str] | None, str | None]:
        """Merge the desired server entry into the host-specific config file."""

    @abstractmethod
    def validate_registered(
        self,
        target: Path,
        read_only: bool,
        transport: str = "stdio",
        url: str | None = None,
        bearer_token_env_var: str | None = None,
    ) -> tuple[dict[str, str], str | None]:
        """Validate the registered server entry on disk."""

    def allowed_fields(self, transport: str = "stdio") -> set[str]:
        """Return the closed set of fields the host accepts for the given transport."""
        return set()

    def forbidden_fields(self, transport: str = "stdio") -> set[str]:
        """Return the set of fields that must never appear for the given transport."""
        return set()

    def assert_entry_valid(self, entry: Any, transport: str = "stdio") -> list[str]:
        """Return a list of validation failures for the given entry shape."""
        failures: list[str] = []
        if isinstance(entry, dict):
            keys = set(entry.keys())
            allowed = self.allowed_fields(transport)
            if allowed:
                extras = keys - allowed
                if extras:
                    failures.append(
                        f"{self.name} {transport} entry has unknown fields: {sorted(extras)}"
                    )
            forbidden = self.forbidden_fields(transport) & keys
            if forbidden:
                failures.append(
                    f"{self.name} {transport} entry has forbidden fields: {sorted(forbidden)}"
                )
        return failures


def merge_json_server(
    adapter_name: str,
    target: Path,
    config_path: Path,
    server_key: str,
    desired_server: dict[str, Any],
    dry_run: bool,
    overwrite: bool,
    backup: bool,
) -> tuple[dict[str, str] | None, str | None]:
    from install_mcp import rel, write_text_file  # type: ignore

    path = target / config_path
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

    servers = data.setdefault(server_key, {})
    if not isinstance(servers, dict):
        return None, f"{rel(path, target)} {server_key} must be an object"
    existing = servers.get(SERVER_NAME)
    if existing == desired_server:
        return {"path": rel(path, target), "action": "skip-identical"}, None
    if existing is not None and not overwrite:
        return None, f"conflicting {adapter_name} MCP config: {rel(path, target)}"

    servers[SERVER_NAME] = desired_server
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    action = write_text_file(path, text, dry_run, backup)
    action["path"] = rel(path, target)
    return action, None


def validate_json_server(
    adapter_name: str,
    target: Path,
    config_path: Path,
    server_key: str,
    expected: dict[str, Any],
) -> tuple[dict[str, str], str | None]:
    from install_mcp import rel  # type: ignore

    path = target / config_path
    if not path.exists():
        return (
            {"adapter": adapter_name, "path": rel(path, target), "status": "FAIL"},
            f"missing {adapter_name} MCP config: {rel(path, target)}",
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return (
            {"adapter": adapter_name, "path": rel(path, target), "status": "FAIL"},
            f"invalid JSON in {rel(path, target)}: {exc}",
        )
    if not isinstance(data, dict):
        return (
            {"adapter": adapter_name, "path": rel(path, target), "status": "FAIL"},
            f"{rel(path, target)} must contain a JSON object",
        )
    servers = data.get(server_key)
    if not isinstance(servers, dict):
        return (
            {"adapter": adapter_name, "path": rel(path, target), "status": "FAIL"},
            f"{rel(path, target)} {server_key} must be an object",
        )
    actual = servers.get(SERVER_NAME)
    if actual != expected:
        return (
            {"adapter": adapter_name, "path": rel(path, target), "status": "FAIL"},
            f"{rel(path, target)} missing expected tes-cortex server registration",
        )
    return (
        {
            "adapter": adapter_name,
            "path": rel(path, target),
            "status": "PASS",
            "server": SERVER_NAME,
            "server_key": server_key,
        },
        None,
    )
