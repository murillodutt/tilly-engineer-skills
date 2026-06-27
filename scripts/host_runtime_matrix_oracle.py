#!/usr/bin/env python3
"""Installed-target host runtime matrix oracle for TES hooks.

This oracle closes the gap between source-only PreToolUse simulation and an
installed target. It installs TES into a temporary project with hooks attached,
inspects the generated host configs, drives the installed `.tes/bin/tes_install.py`
hook entrypoint, and verifies host-specific output contracts plus ledger proof.

It intentionally does not claim native editor execution for every host. Native
smoke remains the per-host audit step in `docs/install/HOOK-AUDIT-PROMPT.md`.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
TES_INSTALL = SCRIPTS / "tes_install.py"
sys.path.insert(0, str(SCRIPTS))
import mantra_gate  # noqa: E402
import tes_install  # noqa: E402

EXPECTED_MARKER = mantra_gate.MARKER
EXPECTED_MATCHER = tes_install.CLAUDE_PRETOOLUSE_MATCHER
HOOK_SENTINEL = Path(".tes/runtime/hooks/executed.jsonl")
LEGACY_SENTINEL = Path(".tes/hooks/executed.jsonl")
EXPECTED_HEALTH_INFO = {
    ("codex", "SessionStart"),
    ("claude", "SessionStart"),
    ("cursor", "sessionStart"),
    ("cursor", "beforeSubmitPrompt"),
}
HOST_FIXTURES = (
    "claude-code.json",
    "codex.json",
    "cursor.json",
    "negative-flat-contract.json",
)


def _parse_first_json(text: str) -> dict[str, Any]:
    stripped = text.lstrip()
    if not stripped:
        return {}
    try:
        payload, _ = json.JSONDecoder().raw_decode(stripped)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _run(command: list[str], *, cwd: Path | None = None, stdin: dict[str, Any] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        input=json.dumps(stdin) if stdin is not None else None,
        text=True,
        capture_output=True,
        check=False,
    )


def _run_hook(target: Path, agent: str, payload: dict[str, Any]) -> tuple[int, str, str]:
    proc = _run(
        [
            sys.executable,
            str(target / ".tes/bin/tes_install.py"),
            "hook",
            "--agent",
            agent,
            "--target",
            str(target),
        ],
        stdin=payload,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _snake(tool: str, session: str, **tool_input: Any) -> dict[str, Any]:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": tool_input,
        "session_id": session,
    }


def _camel(tool: str, session: str, **tool_input: Any) -> dict[str, Any]:
    return {
        "hookEventName": "PreToolUse",
        "toolName": tool,
        "toolInput": tool_input,
        "sessionId": session,
    }


def _assert_marker(label: str, text: str, failures: list[str]) -> None:
    if EXPECTED_MARKER not in text:
        failures.append(f"{label}: missing {EXPECTED_MARKER}")


def _assert_no_marker(label: str, text: str, failures: list[str]) -> None:
    if EXPECTED_MARKER in text:
        failures.append(f"{label}: routine path must not surface {EXPECTED_MARKER}")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _read_ledger(target: Path) -> list[dict[str, Any]]:
    path = target / HOOK_SENTINEL
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            records.append(item)
    return records


def _event_state(health: dict[str, Any], agent: str, event: str) -> str:
    agent_payload = health.get("agents", {}).get(agent, {})
    for item in agent_payload.get("events", []):
        if isinstance(item, dict) and item.get("event") == event:
            return str(item.get("state") or "")
    return ""


def _write_fixture_project(target: Path) -> None:
    (target / "README.md").write_text("# Host Runtime Matrix Fixture\n", encoding="utf-8")
    (target / "src").mkdir()
    (target / "src/app.py").write_text("print('fixture')\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=target, capture_output=True, check=False)


def _install_hooks(target: Path, failures: list[str]) -> dict[str, Any]:
    proc = _run(
        [
            sys.executable,
            str(TES_INSTALL),
            "install",
            "--target",
            str(target),
            "--agent",
            "all",
            "--attach",
            "hooks",
            "--yes",
        ]
    )
    payload = _parse_first_json(proc.stdout)
    if proc.returncode != 0:
        failures.append(f"install: expected rc=0, got {proc.returncode}: {proc.stderr.strip()}")
    if payload.get("status") not in {"INSTALLED", "PARTIAL"}:
        failures.append(f"install: unexpected status {payload.get('status')!r}")
    if "hooks" not in payload.get("attached_surfaces", []):
        failures.append("install: hooks attachment surface must be reported")
    return payload


def _assert_install_scope(payload: dict[str, Any], failures: list[str]) -> None:
    certification = _as_dict(payload.get("certification"))
    cert_status = certification.get("status")
    if cert_status not in {"PASS", "PARTIAL"}:
        failures.append(f"install: unexpected certification status {cert_status!r}")

    components = _as_dict(certification.get("components"))
    for component, status in components.items():
        if component == "mcp_registration":
            continue
        if status in {"FAIL", "PARTIAL"}:
            failures.append(f"install: unexpected {component} certification status {status!r}")

    for finding in _as_list(certification.get("findings")):
        item = _as_dict(finding)
        detail = " ".join(str(part) for part in _as_list(item.get("detail")))
        if item.get("component") == "mcp_registration" and "missing tes-cortex" in detail:
            continue
        failures.append(f"install: unexpected certification finding {item!r}")


def _assert_installed_configs(target: Path, failures: list[str]) -> None:
    codex_path = target / ".codex/config.toml"
    try:
        codex_text = codex_path.read_text(encoding="utf-8")
        codex_data = tomllib.loads(codex_text)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        failures.append(f"codex config: unreadable TOML: {exc}")
        codex_text = ""
        codex_data = {}
    if codex_data.get("features", {}).get("hooks") is not True:
        failures.append("codex config: [features].hooks must be true")
    if "codex_hooks" in codex_text:
        failures.append("codex config: deprecated codex_hooks flag must not be emitted")
    codex_hooks = _as_dict(codex_data.get("hooks"))
    codex_pre = _as_list(codex_hooks.get("PreToolUse"))
    codex_start = _as_list(codex_hooks.get("SessionStart"))
    if len(codex_pre) != 1 or not isinstance(codex_pre[0], dict) or codex_pre[0].get("matcher") != EXPECTED_MATCHER:
        failures.append("codex config: PreToolUse matcher must be complete and singular")
    if len(codex_start) != 1 or not isinstance(codex_start[0], dict):
        failures.append("codex config: SessionStart hook must be singular")

    claude = _read_json(target / ".claude/settings.json")
    claude_hooks = _as_dict(claude.get("hooks"))
    claude_pre = _as_list(claude_hooks.get("PreToolUse"))
    claude_start = _as_list(claude_hooks.get("SessionStart"))
    if not any(isinstance(group, dict) and group.get("matcher") == EXPECTED_MATCHER for group in claude_pre):
        failures.append("claude config: PreToolUse matcher must be complete")
    if not any(isinstance(group, dict) and group.get("matcher") == tes_install.CLAUDE_SESSIONSTART_MATCHER for group in claude_start):
        failures.append("claude config: SessionStart matcher must use official sources")

    cursor = _read_json(target / ".cursor/hooks.json")
    cursor_hooks = _as_dict(cursor.get("hooks"))
    for event in ("sessionStart", "beforeSubmitPrompt", "preToolUse"):
        if not isinstance(cursor_hooks.get(event), list) or not cursor_hooks[event]:
            failures.append(f"cursor config: missing {event} hook")


def _assert_fixture_completeness(target: Path, failures: list[str]) -> None:
    fixture_root = target / ".tes/bin/fixtures/cortex_host_contracts"
    missing = [name for name in HOST_FIXTURES if not (fixture_root / name).is_file()]
    if missing:
        failures.append(f"fixtures: missing cortex_host_contracts files: {', '.join(missing)}")


def _assert_hook_contracts(target: Path, failures: list[str]) -> None:
    patch_body = (
        "*** Begin Patch\n"
        "*** Add File: .tes/runtime/hook-smoke/codex/SKILL.md\n"
        "+# Smoke\n"
        "*** End Patch\n"
    )

    code, out, err = _run_hook(target, "codex", _camel("apply_patch", "matrix-codex-apply", command=patch_body))
    if code != 0 or out.strip():
        failures.append(f"codex apply_patch: expected allow with stderr context only, got rc={code}")
    _assert_marker("codex apply_patch", err, failures)
    if ".tes/runtime/hook-smoke/codex/SKILL.md" not in err:
        failures.append("codex apply_patch: path extracted from patch body must surface")
    code, out, err = _run_hook(target, "codex", _camel("apply_patch", "matrix-codex-apply", command=patch_body))
    if code != 0 or out.strip() or err.strip():
        failures.append("codex apply_patch: second same-session governed mutation must be silent")

    for tool in ("Bash", "Shell", "shell"):
        code, out, err = _run_hook(target, "codex", _camel(tool, f"matrix-codex-{tool}", command="git push --force origin main"))
        if code != 2 or out.strip():
            failures.append(f"codex {tool}: forbidden command must block with exit 2 + stderr")
        _assert_marker(f"codex {tool} forbidden", err, failures)

    code, out, err = _run_hook(
        target,
        "claude",
        _snake("Edit", "matrix-claude-governed", file_path="docs/governance/MATRIX.md"),
    )
    claude_payload = _parse_first_json(out)
    claude_context = claude_payload.get("hookSpecificOutput", {}).get("additionalContext")
    if code != 0 or err.strip() or not isinstance(claude_context, str):
        failures.append("claude governed: must allow with JSON additionalContext")
    _assert_marker("claude governed", str(claude_context or ""), failures)

    code, out, err = _run_hook(
        target,
        "claude",
        _snake("Bash", "matrix-claude-forbidden", command="git push --force origin main"),
    )
    if code != 2 or out.strip():
        failures.append("claude forbidden: must block with exit 2 + stderr")
    _assert_marker("claude forbidden", err, failures)

    code, out, err = _run_hook(
        target,
        "cursor",
        _camel("MultiEdit", "matrix-cursor-governed", filePath=".cursor/rules/matrix.mdc"),
    )
    cursor_payload = _parse_first_json(out)
    if code != 0 or err.strip() or cursor_payload.get("permission") != "allow" or cursor_payload.get("continue") is not True:
        failures.append("cursor governed: must allow with JSON permission contract")
    _assert_marker("cursor governed", str(cursor_payload.get("user_message") or ""), failures)

    code, out, err = _run_hook(
        target,
        "cursor",
        _snake("Bash", "matrix-cursor-forbidden", command="sudo rm -rf / --no-preserve-root"),
    )
    cursor_forbidden = _parse_first_json(out)
    if code != 0 or err.strip() or cursor_forbidden.get("permission") != "deny":
        failures.append("cursor forbidden: must deny with JSON permission and rc=0")
    _assert_marker("cursor forbidden", str(cursor_forbidden.get("agent_message") or ""), failures)

    code, out, err = _run_hook(target, "cursor", _snake("Read", "matrix-cursor-read", file_path="src/app.py"))
    cursor_read = _parse_first_json(out)
    if code != 0 or err.strip() or cursor_read.get("permission") != "allow":
        failures.append("cursor read: must allow with JSON permission")
    _assert_no_marker("cursor read", out + err, failures)

    code, out, err = _run_hook(target, "codex", _camel("Edit", "matrix-codex-routine", path="src/app.py"))
    if code != 0 or out.strip() or err.strip():
        failures.append("codex ordinary edit: must allow silently")


def _assert_runtime_ledger(target: Path, failures: list[str]) -> dict[str, Any]:
    records = _read_ledger(target)
    if not records:
        failures.append("ledger: current runtime hook ledger must exist")
    if (target / LEGACY_SENTINEL).exists():
        failures.append("ledger: legacy .tes/hooks/executed.jsonl must not be written by matrix")

    expected = [
        ("codex", "apply_patch", ".tes/runtime/hook-smoke/codex/SKILL.md"),
        ("claude", "Edit", "docs/governance/MATRIX.md"),
        ("cursor", "MultiEdit", ".cursor/rules/matrix.mdc"),
        ("cursor", "Read", "src/app.py"),
    ]
    for agent, tool, path in expected:
        if not any(item.get("agent") == agent and item.get("tool") == tool and item.get("path") == path for item in records):
            failures.append(f"ledger: missing {agent}/{tool}/{path} record")

    health_proc = _run(
        [
            sys.executable,
            str(target / ".tes/bin/tes_install.py"),
            "hook-health",
            "--target",
            str(target),
            "--json-only",
        ]
    )
    health = _parse_first_json(health_proc.stdout)
    if health_proc.returncode != 0:
        failures.append(f"hook-health: expected rc=0, got {health_proc.returncode}")
    for agent, event in (("codex", "PreToolUse"), ("claude", "PreToolUse"), ("cursor", "preToolUse")):
        if _event_state(health, agent, event) != "OBSERVED":
            failures.append(f"hook-health: {agent} {event} must be OBSERVED after matrix")
    _assert_hook_health_contract(health, failures)
    return health


def _assert_hook_health_contract(health: dict[str, Any], failures: list[str]) -> None:
    if health.get("status") != "NEEDS_EVIDENCE":
        failures.append(f"hook-health: expected NEEDS_EVIDENCE for non-native matrix, got {health.get('status')!r}")

    counts = _as_dict(health.get("finding_counts"))
    if counts.get("error", 0) != 0:
        failures.append(f"hook-health: unexpected error findings count {counts.get('error')!r}")
    if counts.get("warning", 0) != 0:
        failures.append(f"hook-health: unexpected warning findings count {counts.get('warning')!r}")

    for finding in _as_list(health.get("findings")):
        item = _as_dict(finding)
        expected_info = (
            item.get("severity") == "info"
            and item.get("type") == "configured_without_runtime_observation"
            and (item.get("agent"), item.get("event")) in EXPECTED_HEALTH_INFO
        )
        if not expected_info:
            failures.append(f"hook-health: unexpected finding {item!r}")


def _assert_cortex_no_write(target: Path, failures: list[str]) -> None:
    cortex_runtime = target / ".tes/bin/cortex_runtime.py"
    if not cortex_runtime.is_file():
        failures.append("cortex runtime: installed helper missing")
        return
    proc = _run([sys.executable, str(cortex_runtime), "--self-test"], cwd=target)
    payload = _parse_first_json(proc.stdout)
    if proc.returncode != 0 or payload.get("status") != "PASS":
        failures.append(f"cortex runtime: self-test must pass, got rc={proc.returncode}")
    if payload.get("filesystem_changed") is not False:
        failures.append("cortex runtime: self-test must report filesystem_changed=false")


def evaluate() -> dict[str, Any]:
    failures: list[str] = []
    install_payload: dict[str, Any] = {}
    health: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="tes-host-runtime-matrix-") as tmp:
        target = Path(tmp)
        _write_fixture_project(target)
        install_payload = _install_hooks(target, failures)
        _assert_install_scope(install_payload, failures)
        _assert_installed_configs(target, failures)
        _assert_fixture_completeness(target, failures)
        _assert_hook_contracts(target, failures)
        health = _assert_runtime_ledger(target, failures)
        _assert_cortex_no_write(target, failures)

    return {
        "oracle": "host-runtime-matrix",
        "status": "PASS" if not failures else "FAIL",
        "coverage": "installed-target-hook-runtime-matrix",
        "install_status": install_payload.get("status"),
        "install_certification_status": install_payload.get("certification", {}).get("status"),
        "hook_health_status": health.get("status"),
        "native_smoke_scope": "manual-per-host; see docs/install/HOOK-AUDIT-PROMPT.md",
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    result = evaluate()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[host-runtime-matrix] " + str(result["status"]))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
