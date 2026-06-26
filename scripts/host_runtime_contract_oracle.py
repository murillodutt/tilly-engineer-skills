#!/usr/bin/env python3
"""Executable host-aware runtime contract oracle.

This oracle keeps ADR 0008 honest: TES runtime intent can be shared, but hook
contracts are projected per host. It validates the existing Cortex agent-host
fixtures, then executes Git hook-manager fixtures against field_reports.py so a
config-only or wrong-hook install cannot pass as runtime delivery.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_SCHEMA = "tes.host-runtime-contract.v1"
FIXTURE_DIR = ROOT / "scripts" / "fixtures" / "host_runtime_contracts"
HOOK_MARKER = "TES_FIELD_REPORTS_PRE_PUSH"

sys.path.insert(0, str(ROOT / "scripts"))
import cortex_host_contract_oracle  # noqa: E402
import field_reports  # noqa: E402


REQUIRED_GIT_HOSTS = {
    "git-native",
    "git-core-hooks-path",
    "git-husky",
    "git-lefthook",
    "git-project-owned",
    "git-hooks-disabled",
}


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def load_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"{rel(path)}: invalid JSON: {exc}"]
    if not isinstance(payload, dict):
        return None, [f"{rel(path)}: fixture must be a JSON object"]
    return payload, []


def marker_in(path: Path) -> bool:
    return path.exists() and HOOK_MARKER in path.read_text(encoding="utf-8", errors="replace")


def write_fixture_files(target: Path, setup: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    files = setup.get("files", {})
    if not isinstance(files, dict):
        return ["setup.files must be an object"]
    executable = set(setup.get("executable") or [])
    for relpath, content in files.items():
        if not isinstance(relpath, str) or not isinstance(content, str):
            failures.append("setup.files entries must map string paths to string content")
            continue
        path = target / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        if relpath in executable:
            path.chmod(0o755)
    return failures


def validate_fixture_shape(path: Path, fixture: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if fixture.get("fixture_schema") != FIXTURE_SCHEMA:
        failures.append(f"{rel(path)}: fixture_schema must be {FIXTURE_SCHEMA}")
    if not isinstance(fixture.get("host"), str) or not fixture.get("host"):
        failures.append(f"{rel(path)}: missing host")
    if fixture.get("host_family") != "git-hook-manager" and fixture.get("negative") is not True:
        failures.append(f"{rel(path)}: host_family must be git-hook-manager")
    source_refs = fixture.get("source_refs")
    if not isinstance(source_refs, list) or not source_refs:
        failures.append(f"{rel(path)}: missing source_refs")
    for section in ("setup", "contract", "expected_install"):
        if not isinstance(fixture.get(section), dict):
            failures.append(f"{rel(path)}: missing {section} object")
    contract = fixture.get("contract") if isinstance(fixture.get("contract"), dict) else {}
    for key in ("config_owner", "output_style", "idempotency", "observable_proof"):
        if not contract.get(key):
            failures.append(f"{rel(path)}: contract.{key} is required")
    if "blocks_delivery" not in contract:
        failures.append(f"{rel(path)}: contract.blocks_delivery is required")
    negative_cases = fixture.get("negative_cases")
    if fixture.get("negative") is not True and (not isinstance(negative_cases, list) or not negative_cases):
        failures.append(f"{rel(path)}: missing negative_cases")
    return failures


def validate_negative_fixture(path: Path, fixture: dict[str, Any]) -> list[str]:
    failures = validate_fixture_shape(path, fixture)
    contract = fixture.get("contract") if isinstance(fixture.get("contract"), dict) else {}
    flattened_signals = [
        fixture.get("host_family") == "flattened",
        str(contract.get("config_owner")) == "universal",
        "for-all-hosts" in str(contract.get("output_style")),
        str(fixture.get("host")) == "universal-hook",
    ]
    if any(flattened_signals):
        failures.append(f"{rel(path)}: rejected flattened-host contract")
    else:
        failures.append(f"{rel(path)}: negative fixture must encode a rejected flattened-host contract")
    return failures


def run_git_fixture(path: Path, fixture: dict[str, Any]) -> list[str]:
    failures = validate_fixture_shape(path, fixture)
    if failures or fixture.get("negative") is True:
        return failures

    setup = fixture["setup"]
    contract = fixture["contract"]
    expected = fixture["expected_install"]
    with tempfile.TemporaryDirectory(prefix=f"tes-host-contract-{fixture['host']}-") as tempdir:
        target = Path(tempdir)
        init = subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)
        if init.returncode != 0:
            return [f"{rel(path)}: git init failed: {init.stderr.strip()}"]
        configured = setup.get("core_hooks_path")
        if configured is not None:
            subprocess.run(["git", "config", "core.hooksPath", str(configured)], cwd=target, text=True, capture_output=True, check=False)
        failures.extend(write_fixture_files(target, setup))

        first = field_reports.install_hook(target)
        second = field_reports.install_hook(target)
        if first.get("status") != expected.get("status"):
            failures.append(f"{rel(path)}: expected status {expected.get('status')}, got {first.get('status')}")
        if first.get("hook") != expected.get("hook"):
            failures.append(f"{rel(path)}: expected hook {expected.get('hook')}, got {first.get('hook')}")
        if first.get("hook_mode") != expected.get("hook_mode"):
            failures.append(f"{rel(path)}: expected hook_mode {expected.get('hook_mode')}, got {first.get('hook_mode')}")
        if second.get("status") != first.get("status") or second.get("hook") != first.get("hook"):
            failures.append(f"{rel(path)}: install_hook must be idempotent for status and hook")

        hook = expected.get("hook")
        if expected.get("status") == "PASS" and isinstance(hook, str):
            hook_path = target / hook
            if not marker_in(hook_path):
                failures.append(f"{rel(path)}: expected active hook marker at {hook}")
        for forbidden in expected.get("forbidden_marker_paths") or []:
            if isinstance(forbidden, str) and marker_in(target / forbidden):
                failures.append(f"{rel(path)}: wrote TES marker to forbidden hook path {forbidden}")

        active = contract.get("active_entrypoint")
        if expected.get("status") == "PASS" and isinstance(active, str):
            entrypoint = target / active
            if not entrypoint.exists():
                failures.append(f"{rel(path)}: active entrypoint missing: {active}")
            else:
                entrypoint.chmod(0o755)
                run = subprocess.run([str(entrypoint)], cwd=target, text=True, capture_output=True, check=False)
                if run.returncode != 0:
                    failures.append(f"{rel(path)}: active entrypoint returned {run.returncode}")
        if expected.get("status") == "BLOCKED":
            for probe in (".git/hooks/pre-push", ".githooks/pre-push", ".husky/pre-push", ".husky/_/pre-push"):
                if marker_in(target / probe):
                    failures.append(f"{rel(path)}: blocked fixture wrote marker to {probe}")
    return failures


def validate_agent_host_contracts() -> tuple[set[str], list[str]]:
    failures: list[str] = []
    result = cortex_host_contract_oracle.analyze()
    if result.get("status") != "PASS":
        failures.extend(f"cortex host contract: {item}" for item in result.get("failures", []))
    output_styles: set[str] = set()
    event_cases: set[str] = set()
    hosts: set[str] = set()
    for relpath in result.get("fixtures", []):
        path = ROOT / str(relpath)
        fixture, load_failures = load_json(path)
        failures.extend(load_failures)
        if fixture is None or fixture.get("negative") is True:
            continue
        contract = fixture.get("contract") if isinstance(fixture.get("contract"), dict) else {}
        hosts.add(str(fixture.get("host")))
        output_styles.add(str(contract.get("output_style")))
        event_cases.add(str(contract.get("event_case")))
    if {"claude-code", "codex", "cursor"} - hosts:
        failures.append("agent host fixtures must cover claude-code, codex, and cursor")
    if len(output_styles) < 2:
        failures.append("agent hosts must not collapse into one output_style")
    if len(event_cases) < 2:
        failures.append("agent hosts must not collapse into one event_case")
    return hosts, failures


def analyze() -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    loaded: list[str] = []
    negative_proofs: list[str] = []
    git_hosts: set[str] = set()

    agent_hosts, agent_failures = validate_agent_host_contracts()
    failures.extend(agent_failures)

    if not FIXTURE_DIR.exists():
        failures.append(f"missing fixture directory: {rel(FIXTURE_DIR)}")
    else:
        for path in sorted(FIXTURE_DIR.glob("*.json")):
            loaded.append(rel(path))
            fixture, load_failures = load_json(path)
            failures.extend(load_failures)
            if fixture is None:
                continue
            if fixture.get("negative") is True:
                negative_failures = validate_negative_fixture(path, fixture)
                if negative_failures:
                    negative_proofs.append(rel(path))
                else:
                    failures.append(f"{rel(path)}: negative fixture was accepted")
                continue
            failures.extend(run_git_fixture(path, fixture))
            git_hosts.add(str(fixture.get("host")))
    missing_git = sorted(REQUIRED_GIT_HOSTS - git_hosts)
    if missing_git:
        failures.append("missing Git hook-manager fixtures: " + ", ".join(missing_git))
    if not negative_proofs:
        failures.append("missing negative flattened-host fixture proof")

    return {
        "status": "PASS" if not failures else "FAIL",
        "fixture_schema": FIXTURE_SCHEMA,
        "agent_hosts": sorted(agent_hosts),
        "git_hook_manager_hosts": sorted(git_hosts),
        "fixtures": loaded,
        "negative_proofs": sorted(negative_proofs),
        "warnings": warnings,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.parse_args()

    result = analyze()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[host-runtime-contract] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
