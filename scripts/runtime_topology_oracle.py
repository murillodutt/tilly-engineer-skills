#!/usr/bin/env python3
"""Host-aware runtime topology probe.

ADR 0008 requires one semantic runtime contract with host-specific projections.
This oracle fails if the Cortex semantic core starts emitting host output
protocol, if host projections collapse into one shape, or if bootloaders absorb
the full hook contract instead of pointing to focused runtime surfaces.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AGENT_FIXTURE_DIR = ROOT / "scripts" / "fixtures" / "cortex_host_contracts"
GIT_FIXTURE_DIR = ROOT / "scripts" / "fixtures" / "host_runtime_contracts"
SEMANTIC_INTENTS = {"advisory_recall", "capture_proposal", "needs_align"}
CORE_FORBIDDEN_OUTPUT_TOKENS = (
    "hookSpecificOutput",
    "permissionDecision",
    "agent_message",
    "user_message",
    "followup_message",
    "exit_code",
    "\"stdout\"",
    "\"stderr\"",
)
BOOTLOADER_PROTOCOL_TOKENS = (
    "hookSpecificOutput",
    "permissionDecision",
    "agent_message",
    "followup_message",
    "HOST_UNOBSERVABLE",
    "core.hooksPath",
    "git-husky",
    "git-lefthook",
)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_self_test(script: str) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(ROOT / script), "--self-test"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return []
    return [f"{script} --self-test failed", *result.stdout.splitlines(), *result.stderr.splitlines()]


def agent_fixture_failures() -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    hosts: dict[str, Any] = {}
    output_styles: set[str] = set()
    event_cases: set[str] = set()
    lifecycle_shapes: set[tuple[str, ...]] = set()

    for path in sorted(AGENT_FIXTURE_DIR.glob("*.json")):
        fixture = load_json(path)
        if fixture.get("negative") is True:
            continue
        host = str(fixture.get("host"))
        contract = fixture.get("contract") if isinstance(fixture.get("contract"), dict) else {}
        lifecycle = contract.get("lifecycle_events") if isinstance(contract.get("lifecycle_events"), dict) else {}
        intents = set(lifecycle)
        if intents != SEMANTIC_INTENTS:
            failures.append(f"{rel(path)}: lifecycle intents must be {sorted(SEMANTIC_INTENTS)}")
        output_styles.add(str(contract.get("output_style")))
        event_cases.add(str(contract.get("event_case")))
        lifecycle_shapes.add(tuple(sorted(str(value) for value in lifecycle.values())))
        hosts[host] = {
            "event_case": contract.get("event_case"),
            "output_style": contract.get("output_style"),
            "blocks_with_exit_code_2": contract.get("blocks_with_exit_code_2"),
        }

    if set(hosts) != {"claude-code", "codex", "cursor"}:
        failures.append("agent host topology must cover exactly claude-code, codex, and cursor")
    if len(output_styles) < 3:
        failures.append("agent host output styles must remain independently projected")
    if len(event_cases) < 2:
        failures.append("agent host event casing must not collapse")
    if len(lifecycle_shapes) < 2:
        failures.append("agent host lifecycle event names must not collapse")
    if hosts.get("cursor", {}).get("blocks_with_exit_code_2") is not False:
        failures.append("Cursor projection must not use exit-code-2 blocking")
    for host in ("claude-code", "codex"):
        if hosts.get(host, {}).get("blocks_with_exit_code_2") is not True:
            failures.append(f"{host} projection must retain exit-code-2 blocking")
    return hosts, failures


def git_fixture_failures() -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    hosts: dict[str, Any] = {}
    active_entrypoints: set[str] = set()
    install_paths: set[str] = set()

    for path in sorted(GIT_FIXTURE_DIR.glob("*.json")):
        fixture = load_json(path)
        if fixture.get("negative") is True:
            continue
        host = str(fixture.get("host"))
        contract = fixture.get("contract") if isinstance(fixture.get("contract"), dict) else {}
        expected = fixture.get("expected_install") if isinstance(fixture.get("expected_install"), dict) else {}
        active = contract.get("active_entrypoint")
        install = contract.get("install_path")
        if isinstance(active, str):
            active_entrypoints.add(active)
        if isinstance(install, str):
            install_paths.add(install)
        hosts[host] = {
            "install_path": install,
            "active_entrypoint": active,
            "hook": expected.get("hook"),
            "hook_mode": expected.get("hook_mode"),
            "status": expected.get("status"),
        }

    required = {"git-native", "git-core-hooks-path", "git-husky", "git-lefthook", "git-project-owned", "git-hooks-disabled"}
    if set(hosts) != required:
        failures.append("Git hook-manager topology must cover native, core.hooksPath, Husky, Lefthook, and disabled hooks")
    if len(active_entrypoints) < 3:
        failures.append("Git hook-manager active entrypoints must remain distinct")
    if len(install_paths) < 3:
        failures.append("Git hook-manager install paths must remain distinct")
    disabled = hosts.get("git-hooks-disabled", {})
    if disabled.get("status") != "BLOCKED" or disabled.get("install_path") is not None:
        failures.append("disabled Git hooks must report BLOCKED without an install path")
    if hosts.get("git-husky", {}).get("active_entrypoint") == hosts.get("git-husky", {}).get("install_path"):
        failures.append("Husky projection must distinguish internal wrapper from user hook")
    return hosts, failures


def source_topology_failures() -> list[str]:
    failures: list[str] = []
    core_path = ROOT / "scripts" / "cortex_runtime.py"
    core_text = core_path.read_text(encoding="utf-8")
    for token in CORE_FORBIDDEN_OUTPUT_TOKENS:
        if token in core_text:
            failures.append(f"{rel(core_path)} must not emit host output token {token}")

    for relpath in (
        "src/adapters/codex/AGENTS.md",
        "src/adapters/claude/CLAUDE.md",
        "src/adapters/cursor/CURSOR.md",
    ):
        path = ROOT / relpath
        text = path.read_text(encoding="utf-8")
        for token in BOOTLOADER_PROTOCOL_TOKENS:
            if token in text:
                failures.append(f"{relpath} must not duplicate runtime hook protocol token {token}")
    return failures


def analyze() -> dict[str, Any]:
    failures: list[str] = []
    failures.extend(run_self_test("scripts/cortex_runtime.py"))
    failures.extend(run_self_test("scripts/host_runtime_contract_oracle.py"))
    failures.extend(run_self_test("scripts/mantra_gate_pretooluse_oracle.py"))
    agent_hosts, agent_failures = agent_fixture_failures()
    git_hosts, git_failures = git_fixture_failures()
    failures.extend(agent_failures)
    failures.extend(git_failures)
    failures.extend(source_topology_failures())

    return {
        "status": "PASS" if not failures else "FAIL",
        "semantic_intents": sorted(SEMANTIC_INTENTS),
        "agent_hosts": agent_hosts,
        "git_hook_manager_hosts": git_hosts,
        "core_forbidden_output_tokens": list(CORE_FORBIDDEN_OUTPUT_TOKENS),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.parse_args()

    result = analyze()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[runtime-topology] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
