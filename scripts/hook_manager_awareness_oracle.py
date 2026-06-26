#!/usr/bin/env python3
"""Focused Field Reports Git hook-manager oracle.

This proves install-hook respects the active Git hook owner instead of writing a
dormant `.git/hooks/pre-push`: native Git, core.hooksPath, Husky, Lefthook,
project-owned hooks, and disabled hook routing are exercised in temp repos.
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
FIXTURE_DIR = ROOT / "scripts" / "fixtures" / "host_runtime_contracts"

sys.path.insert(0, str(ROOT / "scripts"))
import field_reports  # noqa: E402


REQUIRED_HOSTS = {
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


def marker_in(path: Path) -> bool:
    return path.exists() and field_reports.HOOK_MARKER in path.read_text(encoding="utf-8", errors="replace")


def load_fixtures() -> list[tuple[Path, dict[str, Any]]]:
    fixtures: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(FIXTURE_DIR.glob("*.json")):
        fixture = json.loads(path.read_text(encoding="utf-8"))
        if fixture.get("host_family") == "git-hook-manager" and fixture.get("negative") is not True:
            fixtures.append((path, fixture))
    return fixtures


def write_setup_files(target: Path, setup: dict[str, Any]) -> None:
    executable = set(setup.get("executable") or [])
    files = setup.get("files") if isinstance(setup.get("files"), dict) else {}
    for relpath, content in files.items():
        path = target / str(relpath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(content), encoding="utf-8")
        if relpath in executable:
            path.chmod(0o755)


def configure_target(target: Path, fixture: dict[str, Any]) -> None:
    subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)
    setup = fixture.get("setup") if isinstance(fixture.get("setup"), dict) else {}
    configured = setup.get("core_hooks_path")
    if configured is not None:
        subprocess.run(["git", "config", "core.hooksPath", str(configured)], cwd=target, text=True, capture_output=True, check=False)
    write_setup_files(target, setup)


def existing_hook_text(target: Path, fixture: dict[str, Any]) -> str:
    expected = fixture.get("expected_install") if isinstance(fixture.get("expected_install"), dict) else {}
    hook = expected.get("hook")
    if not isinstance(hook, str):
        return ""
    path = target / hook
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def backup_paths(target: Path, hook_rel: str) -> list[Path]:
    hook = target / hook_rel
    return sorted(hook.parent.glob("pre-push.before-tes-*"))


def validate_fixture(path: Path, fixture: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    host = str(fixture.get("host"))
    expected = fixture.get("expected_install") if isinstance(fixture.get("expected_install"), dict) else {}
    contract = fixture.get("contract") if isinstance(fixture.get("contract"), dict) else {}
    with tempfile.TemporaryDirectory(prefix=f"tes-hook-manager-{host}-") as tempdir:
        target = Path(tempdir)
        configure_target(target, fixture)
        original_hook = existing_hook_text(target, fixture)
        first = field_reports.install_hook(target)
        second = field_reports.install_hook(target)

        if first.get("status") != expected.get("status"):
            failures.append(f"{rel(path)}: expected status {expected.get('status')}, got {first.get('status')}")
        if first.get("hook") != expected.get("hook"):
            failures.append(f"{rel(path)}: expected hook {expected.get('hook')}, got {first.get('hook')}")
        if first.get("hook_mode") != expected.get("hook_mode"):
            failures.append(f"{rel(path)}: expected hook_mode {expected.get('hook_mode')}, got {first.get('hook_mode')}")
        if second.get("status") != first.get("status") or second.get("hook") != first.get("hook"):
            failures.append(f"{rel(path)}: reinstall must be idempotent for status and hook")

        hook = expected.get("hook")
        if expected.get("status") == "PASS" and isinstance(hook, str):
            hook_path = target / hook
            if not marker_in(hook_path):
                failures.append(f"{rel(path)}: active hook lacks TES Field Reports marker")
            backups = backup_paths(target, hook)
            if original_hook and field_reports.HOOK_MARKER not in original_hook:
                if len(backups) != 1:
                    failures.append(f"{rel(path)}: foreign hook must be backed up exactly once")
                elif original_hook.strip() not in backups[0].read_text(encoding="utf-8", errors="replace"):
                    failures.append(f"{rel(path)}: backup must preserve original foreign hook")
            if len(backups) > 1:
                failures.append(f"{rel(path)}: reinstall created duplicate backups")

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
        if host == "git-project-owned" and not (target / "project-owned.log").exists():
            failures.append(f"{rel(path)}: project-owned foreign hook was not chained")
        if expected.get("status") == "BLOCKED":
            probes = (".git/hooks/pre-push", ".githooks/pre-push", ".husky/pre-push", ".husky/_/pre-push", ".project-hooks/pre-push")
            for probe in probes:
                if marker_in(target / probe):
                    failures.append(f"{rel(path)}: blocked fixture wrote marker to {probe}")
    return failures


def analyze() -> dict[str, Any]:
    failures: list[str] = []
    fixtures = load_fixtures()
    hosts = {str(fixture.get("host")) for _, fixture in fixtures}
    missing = sorted(REQUIRED_HOSTS - hosts)
    if missing:
        failures.append("missing hook-manager fixtures: " + ", ".join(missing))
    for path, fixture in fixtures:
        failures.extend(validate_fixture(path, fixture))
    return {
        "status": "PASS" if not failures else "FAIL",
        "fixtures": [rel(path) for path, _ in fixtures],
        "hosts": sorted(hosts),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.parse_args()

    result = analyze()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[hook-manager-awareness] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
