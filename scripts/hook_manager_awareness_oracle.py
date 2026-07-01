#!/usr/bin/env python3
"""Focused Field Reports Git hook-manager oracle.

This proves two contracts:

1. Deference: install-hook respects the active Git hook owner instead of writing
   a dormant `.git/hooks/pre-push` — native Git, core.hooksPath, Husky, Lefthook,
   project-owned hooks, and disabled hook routing are exercised in temp repos.
2. Selection + strict pre-commit install (ceiling: TES installs, chooses and
   verifies Git gates when the project is eligible): the deterministic
   hook-manager selection picks husky for Node/TS, pre-commit when its config is
   present, lefthook as the polyglot default, and defers to any existing manager;
   a strict pre-commit gate is installed on an eligible Git target and chained
   over a foreign hook idempotently; no-Git and core.hooksPath=/dev/null block.
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
    subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False, env=field_reports.isolated_git_env())
    setup = fixture.get("setup") if isinstance(fixture.get("setup"), dict) else {}
    configured = setup.get("core_hooks_path")
    if configured is not None:
        subprocess.run(
            ["git", "config", "core.hooksPath", str(configured)],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
            env=field_reports.isolated_git_env(),
        )
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
        if fixture.get("expected_install", {}).get("status") == "PASS":
            _write_installed_discipline_oracle(target)
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
                run = subprocess.run(
                    [str(entrypoint)],
                    cwd=target,
                    text=True,
                    capture_output=True,
                    check=False,
                    env=field_reports.isolated_git_env(),
                )
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


def _init_git(target: Path) -> None:
    git_env = field_reports.isolated_git_env()
    subprocess.run(["git", "init", "-q"], cwd=target, text=True, capture_output=True, check=False, env=git_env)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=target, text=True, capture_output=True, check=False, env=git_env)
    subprocess.run(["git", "config", "user.name", "t"], cwd=target, text=True, capture_output=True, check=False, env=git_env)


def _write_installed_discipline_oracle(target: Path) -> None:
    """Materialize the canonical installed TES oracle path for hook fixtures."""
    oracle = target / field_reports.CANONICAL_DISCIPLINE_ORACLE
    oracle.parent.mkdir(parents=True, exist_ok=True)
    oracle.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n", encoding="utf-8")
    oracle.chmod(0o755)


def validate_selection_and_precommit() -> list[str]:
    """Red-capable proof of deterministic selection + strict pre-commit install.

    Turns RED if selection becomes non-deterministic (random/missing), if a
    strict pre-commit is no longer installed on an eligible Git target, if a
    foreign pre-commit is not chained idempotently, or if no-Git / disabled hooks
    stop blocking. Imports the canary admission evidence helpers as the contract
    the installer must satisfy.
    """
    import canary_admission_oracle as cao  # noqa: E402

    failures: list[str] = []

    # 1. Deterministic selection by project type / existing owner.
    cases = [
        ({".husky": "dir"}, "husky", True, "existing husky owner"),
        ({"lefthook.yml": "pre-commit:\n  jobs:\n    - run: echo\n"}, "lefthook", True, "existing lefthook owner"),
        ({".pre-commit-config.yaml": "repos: []\n"}, "pre-commit", True, "existing pre-commit owner"),
        ({"package.json": '{"name":"x"}'}, "husky", False, "Node/TS project"),
        ({}, "lefthook", False, "polyglot default"),
    ]
    for files, expected_mgr, expected_deferred, label in cases:
        with tempfile.TemporaryDirectory(prefix="tes-hm-select-") as d:
            t = Path(d)
            _init_git(t)
            for name, content in files.items():
                if content == "dir":
                    (t / name).mkdir(parents=True, exist_ok=True)
                else:
                    (t / name).write_text(str(content), encoding="utf-8")
            sel = field_reports.select_hook_manager(t)
            if sel.get("manager") != expected_mgr:
                failures.append(f"selection[{label}]: expected manager {expected_mgr}, got {sel.get('manager')}")
            if bool(sel.get("deferred")) != expected_deferred:
                failures.append(f"selection[{label}]: expected deferred={expected_deferred}, got {sel.get('deferred')}")

    # 2. No real gate: TES may install the wrapper, but it must fail closed and
    #    admission must not recognize enforcement.
    with tempfile.TemporaryDirectory(prefix="tes-hm-precommit-no-gate-") as d:
        t = Path(d)
        _init_git(t)
        res = field_reports.install_hook(t)
        if res.get("status") != "PASS":
            failures.append(f"precommit-no-gate: install_hook status {res.get('status')} on eligible Git target")
        hp = t / ".git/hooks/pre-commit"
        run = subprocess.run([str(hp)], cwd=t, text=True, capture_output=True, check=False, env=field_reports.isolated_git_env())
        if run.returncode == 0:
            failures.append("precommit-no-gate: installed pre-commit must fail closed without a real gate")
        pc = cao.precommit_evidence(t)
        if pc.get("precommit_enforced"):
            failures.append("precommit-no-gate: canary admission falsely recognized enforcement without a real gate")

    # 3. Strict pre-commit installed + recognized on an eligible Git target with
    #    the canonical TES oracle materialized.
    with tempfile.TemporaryDirectory(prefix="tes-hm-precommit-") as d:
        t = Path(d)
        _init_git(t)
        _write_installed_discipline_oracle(t)
        res = field_reports.install_hook(t)
        if res.get("status") != "PASS":
            failures.append(f"precommit: install_hook status {res.get('status')} on eligible Git target")
        if not res.get("pre_commit_installed"):
            failures.append("precommit: pre_commit_installed is falsy after install on eligible Git target")
        hook_run = subprocess.run(
            [str(t / ".git/hooks/pre-commit")], cwd=t, text=True, capture_output=True, check=False, env=field_reports.isolated_git_env()
        )
        if hook_run.returncode != 0:
            failures.append(f"precommit: canonical installed oracle hook returned {hook_run.returncode}")
        pc = cao.precommit_evidence(t)
        if not pc.get("precommit_enforced"):
            failures.append(f"precommit: canary admission does not recognize strict gate: {pc.get('reason')}")
        pp = cao.prepush_evidence(t)
        if not (pp.get("prepush_installed") and pp.get("field_reports_prepush_drain") and pp.get("prepush_enforced")):
            failures.append(f"precommit: canary admission does not recognize strict pre-push gate: {pp.get('reason')}")
        # Idempotent reinstall: no duplicate pre-commit backups.
        field_reports.install_hook(t)
        backups = sorted((t / ".git" / "hooks").glob("pre-commit.before-tes-*"))
        if len(backups) > 1:
            failures.append("precommit: reinstall created duplicate pre-commit backups")

    # 4. Foreign pre-commit chained over, backed up exactly once.
    with tempfile.TemporaryDirectory(prefix="tes-hm-foreign-") as d:
        t = Path(d)
        _init_git(t)
        _write_installed_discipline_oracle(t)
        hp = t / ".git" / "hooks" / "pre-commit"
        hp.parent.mkdir(parents=True, exist_ok=True)
        hp.write_text("#!/bin/sh\necho FOREIGN > foreign.log\n", encoding="utf-8")
        hp.chmod(0o755)
        field_reports.install_hook(t)
        text = hp.read_text(encoding="utf-8")
        backups = sorted(hp.parent.glob("pre-commit.before-tes-*"))
        if field_reports.PRECOMMIT_MARKER not in text:
            failures.append("foreign-precommit: TES strict marker missing after chaining")
        if "BACKUP_PRECOMMIT" not in text:
            failures.append("foreign-precommit: foreign hook not chained")
        if len(backups) != 1:
            failures.append(f"foreign-precommit: expected exactly one backup, got {len(backups)}")

    # 5. No-Git and disabled hooks block (absence never becomes PASS).
    with tempfile.TemporaryDirectory(prefix="tes-hm-nogit-") as d:
        t = Path(d)
        if field_reports.install_hook(t).get("status") != "BLOCKED":
            failures.append("no-git: install_hook did not BLOCK on a non-Git target")
        if cao.git_admission(t).get("status") != "BLOCKED":
            failures.append("no-git: canary admission did not BLOCK on a non-Git target")
    with tempfile.TemporaryDirectory(prefix="tes-hm-disabled-") as d:
        t = Path(d)
        _init_git(t)
        subprocess.run(
            ["git", "config", "core.hooksPath", "/dev/null"],
            cwd=t,
            text=True,
            capture_output=True,
            check=False,
            env=field_reports.isolated_git_env(),
        )
        if field_reports.install_hook(t).get("status") != "BLOCKED":
            failures.append("disabled-hooks: install_hook did not BLOCK on core.hooksPath=/dev/null")

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
    selection_failures = validate_selection_and_precommit()
    failures.extend(selection_failures)
    return {
        "status": "PASS" if not failures else "FAIL",
        "fixtures": [rel(path) for path, _ in fixtures],
        "hosts": sorted(hosts),
        "selection_precommit": "PASS" if not selection_failures else "FAIL",
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
