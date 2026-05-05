#!/usr/bin/env python3
"""Validate the portable Tilly Engineering Discipline package."""

from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "README.md",
    "package.json",
    "LICENSE",
    "NOTICE.md",
    "PRINCIPLES.md",
    "METHOD.md",
    "EVALS.md",
    "AGENTS.md",
    "CODEX.md",
    "SCORECARD.md",
    "CLAUDE.md",
    "CURSOR.md",
    ".cursor/rules/tilly-guidelines.mdc",
    "skills/tilly-guidelines/SKILL.md",
    ".agents/skills/tilly-engineering-discipline/SKILL.md",
    ".agents/skills/tilly-engineering-discipline/agents/openai.yaml",
    ".agents/skills/tilly-engineering-discipline/references/failure-patterns.md",
    ".agents/skills/tilly-engineering-discipline/references/source-portability.md",
    ".agents/skills/tilly-engineering-discipline/scripts/discipline_oracle.py",
    "benchmarks/context-mesh/eval-dataset.json",
    "scripts/context_mesh_plan.py",
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
    "PRINCIPLES.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".cursor/rules/tilly-guidelines.mdc",
    "skills/tilly-guidelines/SKILL.md",
    ".agents/skills/tilly-engineering-discipline/SKILL.md",
)


def main() -> int:
    failures: list[str] = []

    for relpath in REQUIRED_PATHS:
        if not (ROOT / relpath).exists():
            failures.append(f"missing required path: {relpath}")

    for path in ROOT.rglob(".DS_Store"):
        if ".git" in path.relative_to(ROOT).parts:
            continue
        failures.append(f"local artifact present: {path.relative_to(ROOT)}")

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
        if package.get("version") != "0.1.0":
            failures.append("package.json version must be 0.1.0")

    for relpath in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
        path = ROOT / relpath
        if path.exists() and "0.1.0" not in path.read_text(encoding="utf-8"):
            failures.append(f"{relpath} must declare 0.1.0")

    oracle = ROOT / ".agents/skills/tilly-engineering-discipline/scripts/discipline_oracle.py"
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
