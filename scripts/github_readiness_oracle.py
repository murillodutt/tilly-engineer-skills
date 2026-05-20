#!/usr/bin/env python3
"""Validate GitHub automation readiness before commits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.118"

NPM_MANIFESTS = {
    "package.json",
    "package-lock.json",
    "npm-shrinkwrap.json",
    "yarn.lock",
    "pnpm-lock.yaml",
}
WORKFLOW_SUFFIXES = {".yml", ".yaml"}


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def strip_scalar(value: str) -> str:
    value = value.split("#", 1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_dependabot_updates(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    if not path.exists():
        return [], failures

    text = path.read_text(encoding="utf-8")
    updates: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if re.search(r"\bversion\s*:\s*\d+\s+updates\s*:", stripped):
            failures.append(
                f"{display_path(path)} appears collapsed onto one line at line {line_no}; "
                "Dependabot YAML must be structured"
            )

        if stripped.startswith("- package-ecosystem:") or stripped.startswith("package-ecosystem:"):
            if current:
                updates.append(current)
            _, value = stripped.split(":", 1)
            current = {"package-ecosystem": strip_scalar(value), "line": str(line_no)}
            continue

        if current is not None and stripped.startswith("directory:"):
            _, value = stripped.split(":", 1)
            current["directory"] = strip_scalar(value)

    if current:
        updates.append(current)

    if "updates:" not in text:
        failures.append(f"{display_path(path)} missing updates section")
    if "version:" not in text:
        failures.append(f"{display_path(path)} missing version field")
    if not updates:
        failures.append(f"{display_path(path)} has no package-ecosystem entries")

    for update in updates:
        if not update.get("directory"):
            failures.append(
                f"{display_path(path)} package-ecosystem={update.get('package-ecosystem')} "
                f"at line {update.get('line')} missing directory"
            )

    return updates, failures


def validate_dependabot(root: Path) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    config = root / ".github" / "dependabot.yml"
    if not config.exists():
        return {"present": False, "updates": []}, failures

    updates, parse_failures = parse_dependabot_updates(config)
    failures.extend(parse_failures)
    normalized: list[dict[str, object]] = []

    for update in updates:
        ecosystem = update.get("package-ecosystem", "")
        directory = update.get("directory", "")
        rel_dir = directory.lstrip("/") or "."
        target = root / rel_dir
        record: dict[str, object] = {
            "package_ecosystem": ecosystem,
            "directory": directory,
            "exists": target.exists(),
        }

        if not target.exists():
            failures.append(f"Dependabot {ecosystem} directory does not exist: {directory}")
            normalized.append(record)
            continue

        if ecosystem in {"npm", "npm_and_yarn"}:
            manifests = sorted(name for name in NPM_MANIFESTS if (target / name).exists())
            record["manifests"] = manifests
            if not manifests:
                failures.append(
                    f"Dependabot npm update points at {directory}, "
                    "but no npm/yarn/pnpm manifest or lockfile exists there"
                )
        elif ecosystem == "github-actions":
            workflow_dir = target / ".github" / "workflows" if directory in {"/", "."} else target
            workflows = sorted(
                path.relative_to(root).as_posix()
                for path in workflow_dir.glob("*")
                if path.is_file() and path.suffix in WORKFLOW_SUFFIXES
            ) if workflow_dir.exists() else []
            record["workflows"] = workflows
            if not workflows:
                failures.append(
                    f"Dependabot github-actions update points at {directory}, but no workflow files were found"
                )
        else:
            record["validation"] = "ecosystem-shape-only"

        normalized.append(record)

    return {"present": True, "updates": normalized}, failures


def validate_workflows(root: Path) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    workflow_dir = root / ".github" / "workflows"
    workflows = sorted(
        path for path in workflow_dir.glob("*") if path.is_file() and path.suffix in WORKFLOW_SUFFIXES
    ) if workflow_dir.exists() else []

    for workflow in workflows:
        text = workflow.read_text(encoding="utf-8")
        if "uses: github/dependabot-action@main" in text:
            failures.append(
                f"{workflow.relative_to(root)} uses github/dependabot-action@main; "
                "do not pin repository workflows to the moving Dependabot action"
            )

    return {
        "workflow_count": len(workflows),
        "workflows": [path.relative_to(root).as_posix() for path in workflows],
    }, failures


def validate(root: Path) -> dict[str, object]:
    failures: list[str] = []
    dependabot, dependabot_failures = validate_dependabot(root)
    workflows, workflow_failures = validate_workflows(root)
    failures.extend(dependabot_failures)
    failures.extend(workflow_failures)
    return {
        "version": VERSION,
        "status": "FAIL" if failures else "PASS",
        "dependabot": dependabot,
        "workflows": workflows,
        "failures": failures,
    }


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def self_test() -> dict[str, object]:
    failures: list[str] = []
    cases: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory(prefix="tes-github-readiness-") as tmp:
        root = Path(tmp)

        absent = validate(root)
        cases.append({"case": "absent-dependabot", "status": absent["status"]})
        if absent["status"] != "PASS":
            failures.append("absent dependabot config should pass")

        good = root / "good"
        write(good / "package.json", '{"name":"fixture","version":"0.0.0"}\n')
        write(good / ".github" / "workflows" / "ci.yml", "name: ci\non: [push]\njobs: {}\n")
        write(
            good / ".github" / "dependabot.yml",
            """version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
""",
        )
        good_result = validate(good)
        cases.append({"case": "valid-config", "status": good_result["status"]})
        if good_result["status"] != "PASS":
            failures.append("valid dependabot config should pass")

        collapsed = root / "collapsed"
        write(
            collapsed / ".github" / "dependabot.yml",
            'version: 2 updates: - package-ecosystem: "npm" directory: "/" schedule: interval: "weekly"\n',
        )
        collapsed_result = validate(collapsed)
        cases.append({"case": "collapsed-config", "status": collapsed_result["status"]})
        if collapsed_result["status"] != "FAIL":
            failures.append("collapsed dependabot config should fail")

        missing_manifest = root / "missing-manifest"
        write(
            missing_manifest / ".github" / "dependabot.yml",
            """version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
""",
        )
        missing_result = validate(missing_manifest)
        cases.append({"case": "missing-npm-manifest", "status": missing_result["status"]})
        if missing_result["status"] != "FAIL":
            failures.append("npm dependabot config without manifest should fail")

    return {
        "version": VERSION,
        "status": "FAIL" if failures else "PASS",
        "cases": cases,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=str(ROOT))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result = self_test() if args.self_test else validate(Path(args.target).resolve())
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
