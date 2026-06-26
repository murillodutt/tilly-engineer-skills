#!/usr/bin/env python3
"""Focused smoke oracle for delivered agent-host runtime projections.

This drives the real tes_install.py hook handler as a subprocess for Claude,
Codex, and Cursor. It proves the shared Cortex runtime signal is projected into
each host's output contract without changing the operating mesh.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TES_INSTALL = ROOT / "scripts" / "tes_install.py"
MESH_FILES = (
    "docs/agents/PROJECT-STATE.md",
    "docs/agents/PROJECT-ROADMAP.md",
    "docs/agents/EXECUTION-LINE.md",
    "docs/agents/QUALITY-GATES.md",
)


def write_mesh(target: Path) -> None:
    agents = target / "docs" / "agents"
    decisions = agents / "DECISIONS"
    decisions.mkdir(parents=True)
    for relpath in MESH_FILES:
        path = target / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {path.stem}\n\nFixture baseline.\n", encoding="utf-8")
    (decisions / "projection.md").write_text("# Projection\n\nFixture baseline.\n", encoding="utf-8")


def snapshot_mesh(target: Path) -> dict[str, str]:
    paths = [*(target / relpath for relpath in MESH_FILES), target / "docs/agents/DECISIONS/projection.md"]
    return {
        path.relative_to(target).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
    }


def run_hook(agent: str, target: Path, payload: dict[str, Any]) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, str(TES_INSTALL), "hook", "--agent", agent, "--target", str(target)],
        input=json.dumps(payload),
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def mesh_payload(target: Path, *, camel: bool = False) -> dict[str, Any]:
    mesh_path = str(target / "docs" / "agents" / "PROJECT-STATE.md")
    if camel:
        return {
            "hookEventName": "PreToolUse",
            "sessionId": "projection-camel",
            "toolName": "Edit",
            "toolInput": {"filePath": mesh_path, "newString": "next"},
        }
    return {
        "hook_event_name": "PreToolUse",
        "session_id": "projection-snake",
        "tool_name": "Edit",
        "tool_input": {"file_path": mesh_path, "new_string": "next"},
    }


def benign_payload(target: Path, *, camel: bool = False) -> dict[str, Any]:
    code_path = str(target / "src" / "code.py")
    (target / "src").mkdir(exist_ok=True)
    (target / "src" / "code.py").write_text("print('fixture')\n", encoding="utf-8")
    if camel:
        return {
            "hookEventName": "PreToolUse",
            "sessionId": "projection-benign-camel",
            "toolName": "Edit",
            "toolInput": {"filePath": code_path, "newString": "next"},
        }
    return {
        "hook_event_name": "PreToolUse",
        "session_id": "projection-benign",
        "tool_name": "Edit",
        "tool_input": {"file_path": code_path, "new_string": "next"},
    }


def evaluate() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-agent-host-projection-") as tempdir:
        target = Path(tempdir)
        subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)
        write_mesh(target)
        before = snapshot_mesh(target)

        claude_code, claude_out, claude_err = run_hook("claude", target, mesh_payload(target))
        if claude_code != 0 or claude_err.strip():
            failures.append(f"claude mesh advisory must allow silently on stderr, got code={claude_code}")
        try:
            claude_payload = json.loads(claude_out)
        except json.JSONDecodeError:
            claude_payload = {}
            failures.append("claude mesh advisory must emit JSON")
        claude_specific = claude_payload.get("hookSpecificOutput") if isinstance(claude_payload, dict) else {}
        claude_context = claude_specific.get("additionalContext") if isinstance(claude_specific, dict) else ""
        if "NEEDS_ALIGN" not in str(claude_context):
            failures.append("claude mesh advisory must surface NEEDS_ALIGN in additionalContext")
        if isinstance(claude_specific, dict) and claude_specific.get("permissionDecision") != "allow":
            failures.append("claude mesh advisory must keep permissionDecision=allow")

        codex_code, codex_out, codex_err = run_hook("codex", target, mesh_payload(target, camel=True))
        if codex_code != 0:
            failures.append(f"codex mesh advisory must allow, got code={codex_code}")
        if codex_out.strip():
            failures.append("codex mesh advisory must not emit stdout JSON")
        if "NEEDS_ALIGN" not in codex_err:
            failures.append("codex mesh advisory must surface NEEDS_ALIGN on stderr")

        cursor_code, cursor_out, cursor_err = run_hook("cursor", target, mesh_payload(target))
        if cursor_code != 0 or cursor_err.strip():
            failures.append(f"cursor mesh advisory must allow with stdout JSON only, got code={cursor_code}")
        try:
            cursor_payload = json.loads(cursor_out)
        except json.JSONDecodeError:
            cursor_payload = {}
            failures.append("cursor mesh advisory must emit native JSON")
        if cursor_payload.get("continue") is not True or cursor_payload.get("permission") != "allow":
            failures.append("cursor mesh advisory must use continue=true and permission=allow")
        if "hookSpecificOutput" in cursor_payload:
            failures.append("cursor mesh advisory must not use Claude/Codex hookSpecificOutput")
        if "NEEDS_ALIGN" not in str(cursor_payload.get("agent_message") or ""):
            failures.append("cursor mesh advisory must surface NEEDS_ALIGN in agent_message")

        benign_code, benign_out, benign_err = run_hook("codex", target, benign_payload(target, camel=True))
        if benign_code != 0 or benign_out.strip() or benign_err.strip():
            failures.append("codex benign non-mesh PreToolUse path must stay quiet")

        after = snapshot_mesh(target)
        if after != before:
            failures.append("agent host projection hooks must not write operating mesh files")

    return {
        "oracle": "agent-host-projection",
        "status": "PASS" if not failures else "FAIL",
        "hosts": ["claude", "codex", "cursor"],
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.parse_args()

    result = evaluate()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[agent-host-projection] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
