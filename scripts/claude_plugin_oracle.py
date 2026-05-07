#!/usr/bin/env python3
"""Certify the local Claude adapter/plugin installation shape."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import materialize_adapter


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.15"
CLAUDE_SKILLS = materialize_adapter.CLAUDE_SKILLS


def run(command: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def read_json(path: Path, failures: list[str]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"cannot read JSON {path}: {exc}")
        return {}
    if not isinstance(data, dict):
        failures.append(f"JSON root must be object: {path}")
        return {}
    return data


def validate_plugin(target: Path) -> list[str]:
    target = target.resolve()
    failures: list[str] = []
    required = (
        "CLAUDE.md",
        ".claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
        *(f"skills/{skill}/SKILL.md" for skill in CLAUDE_SKILLS),
    )
    for relpath in required:
        if not (target / relpath).exists():
            failures.append(f"missing installed path: {relpath}")

    plugin = read_json(target / ".claude-plugin/plugin.json", failures)
    marketplace = read_json(target / ".claude-plugin/marketplace.json", failures)
    if plugin.get("version") != VERSION:
        failures.append(f"plugin.json version must be {VERSION}")
    if plugin.get("name") != "tilly-engineer-skills":
        failures.append("plugin.json name must be tilly-engineer-skills")

    skills = plugin.get("skills", [])
    if not isinstance(skills, list) or not skills:
        failures.append("plugin.json must declare at least one skill")
    if isinstance(skills, list):
        expected_skills = {f"skills/{skill}" for skill in CLAUDE_SKILLS}
        declared_skills = {str(item.get("path", "")) if isinstance(item, dict) else str(item) for item in skills}
        for skill in sorted(expected_skills - declared_skills):
            failures.append(f"plugin.json must declare {skill}")
    for item in skills if isinstance(skills, list) else []:
        path = str(item.get("path", "")) if isinstance(item, dict) else str(item)
        if not path or path.startswith("/") or ".." in Path(path).parts:
            failures.append(f"plugin skill path must be relative and contained: {path}")
        elif not (target / path).exists():
            failures.append(f"plugin skill path does not exist: {path}")

    plugins = marketplace.get("plugins", [])
    if not isinstance(plugins, list) or not plugins:
        failures.append("marketplace.json must declare plugins")
    else:
        package = plugins[0] if isinstance(plugins[0], dict) else {}
        if package.get("version") != VERSION:
            failures.append(f"marketplace package version must be {VERSION}")
        source = str(package.get("source", ""))
        resolved = (target / ".claude-plugin" / source).resolve()
        try:
            resolved.relative_to(target)
        except ValueError:
            failures.append(f"marketplace source must resolve inside target: {source}")
        if not (resolved / ".claude-plugin/plugin.json").exists():
            failures.append(f"marketplace source does not resolve to plugin root: {source}")

    return failures


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="tilly-claude-plugin-oracle-") as tempdir:
        target = Path(tempdir)
        code, stdout, stderr = run(
            [
                sys.executable,
                str(ROOT / "scripts/install_adapter.py"),
                "--target",
                str(target),
                "--adapter",
                "claude",
                "--yes",
            ]
        )
        failures: list[str] = []
        if code != 0:
            failures.extend(["claude adapter install failed", *stdout.splitlines(), *stderr.splitlines()])
        failures.extend(validate_plugin(target))

    print(json.dumps({"version": VERSION, "status": "FAIL" if failures else "PASS", "failures": failures}, indent=2))
    if failures:
        print("[claude-plugin-oracle] FAIL")
        return 1
    print("[claude-plugin-oracle] PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test or not args.target:
        return self_test()

    failures = validate_plugin(args.target.resolve())
    print(json.dumps({"version": VERSION, "status": "FAIL" if failures else "PASS", "target": str(args.target), "failures": failures}, indent=2))
    if failures:
        print("[claude-plugin-oracle] FAIL")
        return 1
    print("[claude-plugin-oracle] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
