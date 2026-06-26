#!/usr/bin/env python3
"""Falsifiable multi-host idempotency oracle for the senior-manager hook install (Pillar 3).

The agent pillar (PLANTAO Slice 5) is the idempotent multi-host materializer that
strips-then-merges TES hook entries by ownership marker across Claude, Cursor, and
Codex — for ALL TES events (SessionStart + PreToolUse), not just SessionStart. This
oracle proves the three idempotency invariants per host by driving tes_install.py's
install/remove functions on real temp targets:

  1. INSTALL is idempotent: install twice -> exactly one TES handler per event
     (no duplication).
  2. UNINSTALL is complete: after remove, zero TES handlers remain under any event
     (no orphan — the bug a SessionStart-only remover would leave behind).
  3. FOREIGN hooks are preserved: a non-TES hook planted under the same event
     survives both install and uninstall.

Falsifiable (ADR 0006): a remover that misses an event (orphan) fails invariant 2;
an installer that appends without dedup fails invariant 1; a remover that strips
foreign hooks fails invariant 3. Installing is not proof — the round trip is.

Exit 0 = all invariants hold on all hosts. Exit 1 = an invariant broke.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tes_install


def _tes_count(text: str) -> int:
    return text.count("hook --agent")


def _evaluate_claude() -> list[str]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / ".claude").mkdir(parents=True)
        # Plant a foreign hook under PreToolUse and SessionStart.
        (t / ".claude/settings.json").write_text(json.dumps({
            "hooks": {
                "PreToolUse": [{"matcher": "Bash", "hooks": [{"command": "echo foreign-pre"}]}],
                "SessionStart": [{"matcher": "x", "hooks": [{"command": "echo foreign-ss"}]}],
            }
        }))
        tes_install.install_hooks(t, ["claude"], dry_run=False)
        tes_install.install_hooks(t, ["claude"], dry_run=False)  # idempotent reinstall
        data = json.loads((t / ".claude/settings.json").read_text())
        pre_tes = [h for g in data["hooks"].get("PreToolUse", []) for h in g.get("hooks", [])
                   if tes_install.is_tes_claude_hook_entry(h)]
        if len(pre_tes) != 1:
            failures.append(f"claude: PreToolUse TES handlers after double install = {len(pre_tes)} (want 1)")
        all_text = json.dumps(data)
        if "echo foreign-pre" not in all_text or "echo foreign-ss" not in all_text:
            failures.append("claude: foreign hooks not preserved across install")
        tes_install.remove_tes_hooks(t, "claude", dry_run=False)
        after = json.loads((t / ".claude/settings.json").read_text())
        if _tes_count(json.dumps(after)) != 0:
            failures.append("claude: TES handlers orphaned after uninstall (want 0)")
        if "echo foreign-pre" not in json.dumps(after) or "echo foreign-ss" not in json.dumps(after):
            failures.append("claude: foreign hooks not preserved across uninstall")
    return failures


def _evaluate_cursor() -> list[str]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / ".cursor").mkdir(parents=True)
        (t / ".cursor/hooks.json").write_text(json.dumps({
            "version": 1,
            "hooks": {"preToolUse": [{"command": "echo foreign-pre"}]},
        }))
        tes_install.install_hooks(t, ["cursor"], dry_run=False)
        tes_install.install_hooks(t, ["cursor"], dry_run=False)
        data = json.loads((t / ".cursor/hooks.json").read_text())
        pre_tes = [i for i in data["hooks"].get("preToolUse", []) if "hook --agent cursor" in json.dumps(i)]
        if len(pre_tes) != 1:
            failures.append(f"cursor: preToolUse TES handlers after double install = {len(pre_tes)} (want 1)")
        if "echo foreign-pre" not in json.dumps(data):
            failures.append("cursor: foreign hook not preserved across install")
        tes_install.remove_tes_hooks(t, "cursor", dry_run=False)
        after = (t / ".cursor/hooks.json").read_text() if (t / ".cursor/hooks.json").exists() else ""
        if "hook --agent" in after:
            failures.append("cursor: TES handlers orphaned after uninstall")
        if "echo foreign-pre" not in after:
            failures.append("cursor: foreign hook not preserved across uninstall")
    return failures


def _evaluate_codex() -> list[str]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / ".codex").mkdir(parents=True)
        (t / ".codex/config.toml").write_text('[mcp_servers.other]\ncommand = "keep"\n')
        tes_install.install_hooks(t, ["codex"], dry_run=False)
        tes_install.install_hooks(t, ["codex"], dry_run=False)
        toml = (t / ".codex/config.toml").read_text()
        if toml.count("[[hooks.SessionStart]]") != 1:
            failures.append(f"codex: SessionStart blocks after double install = {toml.count('[[hooks.SessionStart]]')} (want 1)")
        if toml.count("[[hooks.PreToolUse]]") != 1:
            failures.append(f"codex: PreToolUse blocks after double install = {toml.count('[[hooks.PreToolUse]]')} (want 1)")
        if "mcp_servers.other" not in toml:
            failures.append("codex: foreign config not preserved across install")
        tes_install.remove_tes_hooks(t, "codex", dry_run=False)
        after = (t / ".codex/config.toml").read_text() if (t / ".codex/config.toml").exists() else ""
        if "hook --agent" in after:
            failures.append("codex: TES hook orphaned after uninstall")
        if "mcp_servers.other" not in after:
            failures.append("codex: foreign config not preserved across uninstall")
    return failures


def evaluate() -> dict[str, object]:
    failures = _evaluate_claude() + _evaluate_cursor() + _evaluate_codex()
    return {
        "oracle": "mantra-gate-agent-idempotency",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    result = evaluate()
    print(json.dumps(result, indent=2))
    print("[agent-idempotency-oracle] " + str(result["status"]))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
