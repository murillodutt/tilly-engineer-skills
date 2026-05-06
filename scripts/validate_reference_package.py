#!/usr/bin/env python3
"""Validate the portable Tilly Engineering Discipline package."""

from __future__ import annotations

import argparse
from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "README.md",
    "AGENTS.md",
    "package.json",
    "LICENSE",
    "NOTICE.md",
    "install.sh",
    "install.ps1",
    "docs/INDEX.md",
    "docs/architecture/PROJECT-STRUCTURE.md",
    "docs/install/USER-MANUAL.html",
    "docs/install/MINI-PROMPT.md",
    "docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md",
    "docs/install/navigation/NAVIGATION-LIBRARY.md",
    "docs/install/navigation/common.prompt.md",
    "docs/install/navigation/codex.prompt.md",
    "docs/install/navigation/codex-cli.prompt.md",
    "docs/install/navigation/claude-code.prompt.md",
    "docs/install/navigation/claude-desktop.prompt.md",
    "docs/install/navigation/cursor.prompt.md",
    "docs/install/navigation/cursor-acp.prompt.md",
    "docs/install/navigation/anthropic-api.prompt.md",
    "docs/install/navigation/generic.prompt.md",
    "docs/governance/AGENTIC-ALIGNMENT-GOVERNANCE.md",
    "docs/mesh/PRINCIPLES.md",
    "docs/mesh/CONTEXT-MESH-METHOD.md",
    "docs/mesh/CORTEX.md",
    "docs/mesh/SCORECARD.md",
    "docs/evals/EVALS.md",
    "docs/evals/EXAMPLES.md",
    "docs/adapters/CODEX.md",
    "docs/adapters/CLAUDE.md",
    "docs/adapters/CURSOR.md",
    "docs/adapters/MATERIALIZATION.md",
    "docs/tds/DOCS-INDEX.yml",
    "docs/tds/TDS-SPEC.md",
    "src/adapters/codex/AGENTS.md",
    "src/adapters/codex/skills/tilly-engineering-discipline/SKILL.md",
    "src/adapters/codex/skills/tilly-engineering-discipline/agents/openai.yaml",
    "src/adapters/codex/skills/tilly-engineering-discipline/references/failure-patterns.md",
    "src/adapters/codex/skills/tilly-engineering-discipline/references/source-portability.md",
    "src/adapters/codex/skills/tilly-engineering-discipline/scripts/discipline_oracle.py",
    "src/adapters/claude/CLAUDE.md",
    "src/adapters/claude/plugin/plugin.json",
    "src/adapters/claude/plugin/marketplace.json",
    "src/adapters/claude/skills/tilly-guidelines/SKILL.md",
    "src/adapters/cursor/CURSOR.md",
    "src/adapters/cursor/rules/tilly-guidelines.mdc",
    "benchmarks/context-mesh/eval-dataset.json",
    "scripts/context_mesh_plan.py",
    "scripts/context_mesh_run.py",
    "scripts/cortex.py",
    "scripts/install_adapter.py",
    "scripts/adapter_parity_readiness.py",
    "scripts/materialize_adapter.py",
    "scripts/validate_tds.py",
    ".githooks/pre-commit",
)

REQUIRED_TERMS = (
    "Think Before Coding",
    "Simplicity First",
    "Surgical Changes",
    "Goal-Driven Execution",
    "E = A * S * C * V",
)

SYNCED_FILES = (
    "AGENTS.md",
    "docs/mesh/PRINCIPLES.md",
    "src/adapters/codex/AGENTS.md",
    "src/adapters/claude/CLAUDE.md",
    "src/adapters/cursor/rules/tilly-guidelines.mdc",
    "src/adapters/claude/skills/tilly-guidelines/SKILL.md",
    "src/adapters/codex/skills/tilly-engineering-discipline/SKILL.md",
)

FORBIDDEN_ROOT_PATHS = (
    ".agents",
    ".claude-plugin",
    ".cursor",
    "skills",
    "CLAUDE.md",
    "CODEX.md",
    "CURSOR.md",
    "PRINCIPLES.md",
    "METHOD.md",
    "EVALS.md",
    "EXAMPLES.md",
    "SCORECARD.md",
    "CHANGELOG.md",
)

REQUIRED_PACKAGE_SCRIPTS = (
    "validate",
    "install:adapter",
    "install:dry-run",
    "materialize:all",
    "materialize:codex",
    "materialize:cursor",
    "materialize:claude",
    "materialize:check",
    "tds:validate",
    "cortex:init",
    "cortex:verify",
    "cortex:audit",
    "cortex:rebuild",
    "cortex:self-test",
    "oracle:self-test",
    "benchmark:plan",
    "benchmark:run",
    "commit:check",
    "adapter:parity:check",
)


def package_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        text=False,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return [
            path.relative_to(ROOT)
            for path in ROOT.rglob("*")
            if path.is_file() and ".git" not in path.relative_to(ROOT).parts
        ]

    return [
        Path(raw.decode("utf-8"))
        for raw in result.stdout.split(b"\0")
        if raw
    ]


def git_path_list(*args: str) -> set[Path]:
    result = subprocess.run(
        ["git", *args, "-z"],
        cwd=ROOT,
        text=False,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return set()
    return {
        Path(raw.decode("utf-8"))
        for raw in result.stdout.split(b"\0")
        if raw
    }


def staged_ready_failures() -> list[str]:
    failures: list[str] = []
    indexed = git_path_list("ls-files", "--cached")
    untracked = git_path_list("ls-files", "--others", "--exclude-standard")

    for path in sorted(untracked):
        failures.append(f"untracked package path before commit: {path}")

    for relpath in REQUIRED_PATHS:
        path = Path(relpath)
        if path not in indexed:
            failures.append(f"required path is not staged/tracked: {relpath}")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged-ready", action="store_true")
    args = parser.parse_args()

    failures: list[str] = []

    for relpath in REQUIRED_PATHS:
        if not (ROOT / relpath).exists():
            failures.append(f"missing required path: {relpath}")

    for relpath in FORBIDDEN_ROOT_PATHS:
        if (ROOT / relpath).exists():
            failures.append(f"source leaked back into root: {relpath}")

    for path in package_paths():
        if path.name == ".DS_Store":
            failures.append(f"package artifact present: {path}")
        if path.name == "CHANGELOG.md":
            failures.append(f"changelog must remain in Git history, not a file: {path}")
        if path.name == ".cursorrules":
            failures.append(f"legacy Cursor rules file is forbidden: {path}")

    if args.staged_ready:
        failures.extend(staged_ready_failures())

    for relpath in SYNCED_FILES:
        path = ROOT / relpath
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for term in REQUIRED_TERMS:
            if term not in text:
                failures.append(f"{relpath} missing term: {term}")

    package_json = ROOT / "package.json"
    if package_json.exists():
        package = json.loads(package_json.read_text(encoding="utf-8"))
        if package.get("version") != "0.2.7":
            failures.append("package.json version must be 0.2.7")
        scripts = package.get("scripts", {})
        for script in REQUIRED_PACKAGE_SCRIPTS:
            if script not in scripts:
                failures.append(f"package.json missing script: {script}")

    for relpath in ("src/adapters/claude/plugin/plugin.json", "src/adapters/claude/plugin/marketplace.json"):
        path = ROOT / relpath
        if path.exists() and "0.2.7" not in path.read_text(encoding="utf-8"):
            failures.append(f"{relpath} must declare 0.2.7")

    oracle = ROOT / "src/adapters/codex/skills/tilly-engineering-discipline/scripts/discipline_oracle.py"
    if oracle.exists():
        result = subprocess.run(
            [sys.executable, str(oracle), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("discipline_oracle.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    plan = ROOT / "scripts/context_mesh_plan.py"
    if plan.exists():
        result = subprocess.run(
            [sys.executable, str(plan)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("context_mesh_plan.py failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    cortex = ROOT / "scripts/cortex.py"
    if cortex.exists():
        result = subprocess.run(
            [sys.executable, str(cortex), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("cortex.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    materializer = ROOT / "scripts/materialize_adapter.py"
    if materializer.exists():
        result = subprocess.run(
            [sys.executable, str(materializer), "all", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("materialize_adapter.py all --check failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    adapter_parity = ROOT / "scripts/adapter_parity_readiness.py"
    if adapter_parity.exists():
        result = subprocess.run(
            [sys.executable, str(adapter_parity)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("adapter_parity_readiness.py failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    tds_validator = ROOT / "scripts/validate_tds.py"
    if tds_validator.exists():
        result = subprocess.run(
            [sys.executable, str(tds_validator)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("validate_tds.py failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    if failures:
        print("[tilly-reference] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("[tilly-reference] PASS")
    print(f"root={ROOT}")
    print(f"checked_files={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
