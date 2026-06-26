#!/usr/bin/env python3
"""Falsifiable oracle for the PreToolUse senior-manager handler (Pillar 2, Hook).

The PreToolUse handler in tes_install.py is the per-host pre-action projection of
the <mantra_gate> criterion. This oracle proves the handler DISCRIMINATES and
honors the per-host output contract, by driving tes_install.py as a subprocess
with crafted hook_input on stdin and asserting the real output/exit per host:

  - forbidden action (e.g. `git push --force`):
      Claude/Codex -> exit 2 + stderr message (block);
      Cursor       -> exit 0 + {"permission":"deny"} (block, JSON-permission).
  - mutating tool on a governed artifact at material+ risk:
      -> allow (exit 0) AND surface additionalContext / user_message (supervise).
  - benign (Read, or ordinary code edit):
      -> allow, silent (no cry-wolf).

Falsifiable (ADR 0006): the self-test asserts the discrimination holds AND that
the per-host contract is not collapsed (Cursor must NOT use exit 2; Claude must).
A handler that always-blocks or always-allows fails these assertions. The contract
is the whole point — a materializer that assumed exit-2 everywhere would break
silently on Cursor, and this oracle catches exactly that.

Exit 0 = the handler discriminates and honors the per-host contract. Exit 1 = it
does not (a case landed on the wrong side, or a host contract collapsed).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TES_INSTALL = ROOT / "scripts" / "tes_install.py"


def _run(agent: str, hook_input: dict, target: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, str(TES_INSTALL), "hook", "--agent", agent, "--target", str(target)],
        input=json.dumps(hook_input),
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _pre(event_tool: str, **tool_input) -> dict:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": event_tool,
        "tool_input": tool_input,
        "session_id": f"oracle-{event_tool}-{tool_input.get('file_path') or tool_input.get('command') or 'x'}",
    }


def evaluate() -> dict[str, object]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-pretooluse-oracle-") as tmp:
        target = Path(tmp)
        subprocess.run(["git", "init"], cwd=target, capture_output=True, check=False)

        forbidden = _pre("Bash", command="git push --force origin main")
        governed = _pre("Edit", file_path="docs/adr/0005-decision.md")
        benign_read = _pre("Read", file_path="scripts/foo.py")
        benign_code = _pre("Edit", file_path="scripts/foo.py")

        # --- Claude/Codex: forbidden -> exit 2 + stderr ---
        for agent in ("claude", "codex"):
            code, _out, err = _run(agent, forbidden, target)
            if code != 2:
                failures.append(f"{agent}: forbidden action must BLOCK with exit 2, got {code}")
            if "Mantra Gate" not in err:
                failures.append(f"{agent}: forbidden block must write a readable reason to stderr")

        # --- Cursor: forbidden -> JSON permission:deny, NOT exit 2 (contract divergence) ---
        code, out, _err = _run("cursor", forbidden, target)
        if code == 2:
            failures.append("cursor: forbidden must NOT use exit 2 — Cursor is JSON-permission")
        try:
            payload = json.loads(out)
        except json.JSONDecodeError:
            payload = {}
            failures.append("cursor: forbidden output must be valid JSON-permission")
        if payload.get("permission") != "deny":
            failures.append('cursor: forbidden must emit {"permission":"deny"}')

        # --- governed + mutating -> supervise (allow + surfaced context), not block ---
        code, out, _err = _run("claude", governed, target)
        if code != 0:
            failures.append(f"claude: governed-artifact edit must SUPERVISE (allow), got exit {code}")
        if "additionalContext" not in out:
            failures.append("claude: governed-artifact edit must surface additionalContext")

        # --- benign Read -> allow, silent ---
        code, out, err = _run("claude", benign_read, target)
        if code != 0:
            failures.append(f"claude: benign Read must allow (exit 0), got {code}")
        if "Mantra Gate" in out or "Mantra Gate" in err:
            failures.append("claude: benign Read must be SILENT (no cry-wolf)")

        # --- benign code edit (mutating but not governed) -> allow, silent ---
        code, out, err = _run("claude", benign_code, target)
        if code != 0:
            failures.append(f"claude: ordinary code edit must allow (exit 0), got {code}")
        if "Mantra Gate" in out or "Mantra Gate" in err:
            failures.append("claude: ordinary code edit must be SILENT (no cry-wolf on non-governed)")

    return {
        "oracle": "mantra-gate-pretooluse",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def self_test() -> int:
    result = evaluate()
    print(json.dumps(result, indent=2))
    print("[pretooluse-oracle] " + str(result["status"]))
    return 0 if result["status"] == "PASS" else 1


def main(argv: list[str]) -> int:
    return self_test() if "--self-test" in argv else self_test()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
