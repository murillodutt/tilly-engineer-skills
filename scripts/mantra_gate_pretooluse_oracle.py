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
sys.path.insert(0, str(ROOT / "scripts"))
import mantra_gate  # noqa: E402

EXPECTED_MARKER = mantra_gate.MARKER
OLD_BRACKET_MARKER = "[" + EXPECTED_MARKER.strip("`") + "]"
HOOK_SENTINEL_PATH = Path(".tes/runtime/hooks/executed.jsonl")
LEGACY_HOOK_SENTINEL_PATH = Path(".tes/hooks/executed.jsonl")


def _assert_marker(label: str, text: str, failures: list[str]) -> None:
    if EXPECTED_MARKER not in text:
        failures.append(f"{label}: must render {EXPECTED_MARKER} in host context output")
    if OLD_BRACKET_MARKER in text:
        failures.append(f"{label}: must not render the old square-bracket marker")


def _assert_no_visible_marker(label: str, text: str, failures: list[str]) -> None:
    if EXPECTED_MARKER in text or OLD_BRACKET_MARKER in text:
        failures.append(f"{label}: benign path must stay quiet and marker-free")


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


def _pre_camel(event_tool: str, session: str, **tool_input) -> dict:
    return {
        "hookEventName": "PreToolUse",
        "toolName": event_tool,
        "toolInput": tool_input,
        "sessionId": session,
    }


def _read_sentinel(target: Path) -> list[dict]:
    sentinel = target / HOOK_SENTINEL_PATH
    if not sentinel.is_file():
        return []
    records: list[dict] = []
    for line in sentinel.read_text(encoding="utf-8").splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            payload.setdefault("sentinel_path", str(HOOK_SENTINEL_PATH))
            records.append(payload)
    return records


def evaluate() -> dict[str, object]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-pretooluse-oracle-") as tmp:
        target = Path(tmp)
        subprocess.run(["git", "init"], cwd=target, capture_output=True, check=False)

        forbidden = _pre("Bash", command="git push --force origin main")
        governed = _pre("Edit", file_path="docs/adr/0005-decision.md")
        governed_multi_codex = _pre_camel("MultiEdit", "oracle-multiedit-camel", filePath="docs/adr/0005-decision.md")
        governed_multi_cursor = _pre_camel("MultiEdit", "oracle-multiedit-cursor", filePath="docs/adr/0005-decision.md")
        benign_read = _pre("Read", file_path="scripts/foo.py")
        benign_code = _pre("Edit", file_path="scripts/foo.py")
        forbidden_camel = _pre_camel("Bash", "oracle-forbidden-camel", command="git push --force origin main")
        benign_camel = _pre_camel("Edit", "oracle-benign-camel", path="scripts/foo.py")

        # --- Claude/Codex: forbidden -> exit 2 + stderr ---
        for agent in ("claude", "codex"):
            payload = forbidden_camel if agent == "codex" else forbidden
            code, _out, err = _run(agent, payload, target)
            if code != 2:
                failures.append(f"{agent}: forbidden action must BLOCK with exit 2, got {code}")
            if "Mantra Gate" not in err:
                failures.append(f"{agent}: forbidden block must write a readable reason to stderr")
            _assert_marker(f"{agent}: forbidden stderr", err, failures)

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
        _assert_marker("cursor: forbidden agent_message", str(payload.get("agent_message") or ""), failures)
        _assert_marker("cursor: forbidden raw stdout", out, failures)

        # --- governed + mutating -> supervise (allow + host-shaped context), not block ---
        matrix = {
            "claude": ("stdout-json", governed),
            "codex": ("stderr-text", governed_multi_codex),
            "cursor": ("stdout-json", governed_multi_cursor),
        }
        for agent, (shape, payload_in) in matrix.items():
            code, out, err = _run(agent, payload_in, target)
            if code != 0:
                failures.append(f"{agent}: governed-artifact edit must SUPERVISE (allow), got exit {code}")
            if agent == "claude":
                try:
                    claude_payload = json.loads(out)
                except json.JSONDecodeError:
                    claude_payload = {}
                    failures.append("claude: governed-artifact edit must emit JSON")
                hook_specific = claude_payload.get("hookSpecificOutput") if isinstance(claude_payload, dict) else {}
                context = hook_specific.get("additionalContext") if isinstance(hook_specific, dict) else None
                if not isinstance(context, str) or "Mantra Gate supervising" not in context:
                    failures.append("claude: governed-artifact edit must surface additionalContext")
                _assert_marker("claude: governed additionalContext", str(context or ""), failures)
                _assert_marker("claude: governed raw stdout", out, failures)
            if agent == "codex" and ("Mantra Gate supervising" not in err or out.strip()):
                failures.append("codex: governed-artifact edit must surface stderr context only")
            if agent == "codex":
                _assert_marker("codex: governed stderr", err, failures)
            if agent == "cursor":
                try:
                    cursor_payload = json.loads(out)
                except json.JSONDecodeError:
                    cursor_payload = {}
                    failures.append("cursor: governed-artifact edit must emit JSON")
                user_message = str(cursor_payload.get("user_message") or "")
                if user_message.find("Mantra Gate supervising") < 0:
                    failures.append("cursor: governed-artifact edit must surface user_message")
                _assert_marker("cursor: governed user_message", user_message, failures)
                _assert_marker("cursor: governed raw stdout", out, failures)
            if shape == "stdout-json" and agent != "codex" and not out.strip():
                failures.append(f"{agent}: supervised output must not be empty")

        # --- benign Read -> allow, silent ---
        for agent in ("claude", "codex", "cursor"):
            code, out, err = _run(agent, benign_read, target)
            if code != 0:
                failures.append(f"{agent}: benign Read must allow (exit 0), got {code}")
            if agent == "cursor":
                try:
                    allow_payload = json.loads(out)
                except json.JSONDecodeError:
                    allow_payload = {}
                    failures.append("cursor: benign Read must emit JSON permission output")
                if allow_payload.get("permission") != "allow":
                    failures.append('cursor: benign Read must emit {"permission":"allow"}')
            elif out.strip() or err.strip():
                failures.append(f"{agent}: benign Read must be silent")
            _assert_no_visible_marker(f"{agent}: benign Read", out + err, failures)

        # --- benign code edit (mutating but not governed) -> allow, silent ---
        for agent in ("claude", "codex", "cursor"):
            payload = benign_camel if agent == "codex" else benign_code
            code, out, err = _run(agent, payload, target)
            if code != 0:
                failures.append(f"{agent}: ordinary code edit must allow (exit 0), got {code}")
            if agent == "cursor":
                try:
                    allow_payload = json.loads(out)
                except json.JSONDecodeError:
                    allow_payload = {}
                    failures.append("cursor: ordinary code edit must emit JSON permission output")
                if allow_payload.get("permission") != "allow":
                    failures.append('cursor: ordinary code edit must emit {"permission":"allow"}')
            elif out.strip() or err.strip():
                failures.append(f"{agent}: ordinary code edit must be silent")
            _assert_no_visible_marker(f"{agent}: ordinary code edit", out + err, failures)

        sentinel_records = _read_sentinel(target)
        codex_multiedit = next(
            (
                rec
                for rec in sentinel_records
                if rec.get("agent") == "codex"
                and rec.get("event") == "PreToolUse"
                and rec.get("event_canonical") == "PreToolUse"
                and rec.get("mode") == "pretooluse"
                and rec.get("session") == "oracle-multiedit-camel"
                and rec.get("tool") == "MultiEdit"
                and rec.get("path") == "docs/adr/0005-decision.md"
            ),
            None,
        )
        if codex_multiedit is None:
            failures.append("PreToolUse sentinel must record canonical Codex MultiEdit execution with tool/path details")
        if (target / LEGACY_HOOK_SENTINEL_PATH).exists():
            failures.append("PreToolUse hook must not write the legacy tracked hook sentinel")
        if not any(
            rec.get("agent") == "codex"
            and rec.get("event_canonical") == "PreToolUse"
            and rec.get("session") == "oracle-multiedit-camel"
            for rec in sentinel_records
        ):
            failures.append("PreToolUse sentinel must record camelCase Codex MultiEdit execution")

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
