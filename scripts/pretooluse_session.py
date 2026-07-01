#!/usr/bin/env python3
"""Session coordinator for TES PreToolUse supervision.

This helper owns only the anti-cry-wolf sentinel contract: a governed
PreToolUse context records whether the same session/context was already seen,
while the Mantra Gate marker still surfaces for every governed supervision.
It deliberately does not classify tools, render host protocols, write runtime
ledgers, evaluate Cortex, or install hooks; those concerns stay in the decision
kernel and host adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PreToolUseSessionContext:
    """Resolved supervision context after session-level repetition tracking."""

    context: str
    context_suppressed: bool
    session_id: str
    sentinel_path: Path
    reason_codes: tuple[str, ...] = ()
    context_repeated: bool = False


def pretooluse_session_id(hook_input: dict[str, Any]) -> str:
    value = hook_input.get("session_id") or hook_input.get("sessionId") or hook_input.get("session")
    return str(value or "default")


def pretooluse_sentinel_path(target: Path, hook_input: dict[str, Any]) -> Path:
    return target / ".tes" / "mantra-gates" / f"pretooluse-{pretooluse_session_id(hook_input)}.seen"


def coordinate_pretooluse_context(
    target: Path,
    hook_input: dict[str, Any],
    context: str,
) -> PreToolUseSessionContext:
    """Return the context that should be surfaced for this session.

    Filesystem and decode errors preserve the fail-open behavior: supervision
    is still surfaced because hiding a real governed obligation is riskier than
    repeating a marker when the sentinel cannot be read or written.
    """
    sentinel = pretooluse_sentinel_path(target, hook_input)
    session_id = pretooluse_session_id(hook_input)
    if not context:
        return PreToolUseSessionContext("", False, session_id, sentinel)
    try:
        seen: set[str] = set()
        if sentinel.exists():
            seen = set(sentinel.read_text(encoding="utf-8").splitlines())
        if context in seen:
            return PreToolUseSessionContext(
                context,
                False,
                session_id,
                sentinel,
                ("anti_crywolf_repeated_context",),
                True,
            )
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        with sentinel.open("a", encoding="utf-8") as handle:
            handle.write(context + "\n")
    except (OSError, UnicodeError):
        return PreToolUseSessionContext(
            context,
            False,
            session_id,
            sentinel,
            ("anti_crywolf_sentinel_unavailable",),
        )
    return PreToolUseSessionContext(context, False, session_id, sentinel)
