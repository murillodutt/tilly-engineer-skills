"""Per-host adapter registry for TES Cortex MCP install."""

from __future__ import annotations

from .base import HostAdapter
from .claude import ClaudeHost
from .codex import CodexHost
from .cursor import CursorHost
from .vscode import VSCodeHost

HOSTS: dict[str, HostAdapter] = {
    "codex": CodexHost(),
    "claude": ClaudeHost(),
    "cursor": CursorHost(),
    "vscode": VSCodeHost(),
}

__all__ = ["HOSTS", "HostAdapter", "CodexHost", "ClaudeHost", "CursorHost", "VSCodeHost"]
