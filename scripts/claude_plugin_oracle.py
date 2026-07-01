#!/usr/bin/env python3
"""Certify that Claude plugin metadata is source-only, not target-installed."""

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
VERSION = "0.3.238"
CLAUDE_SKILLS = materialize_adapter.CLAUDE_SKILLS
PLUGIN_SOURCE_ROOT = ROOT / "src/adapters/claude/plugin"
TARGET_PLUGIN_PATHS = (
    ".claude-plugin",
    "skills",
)


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


def validate_source_plugin() -> list[str]:
    failures: list[str] = []
    plugin = read_json(PLUGIN_SOURCE_ROOT / "plugin.json", failures)
    marketplace = read_json(PLUGIN_SOURCE_ROOT / "marketplace.json", failures)

    if plugin.get("version") != VERSION:
        failures.append(f"source plugin.json version must be {VERSION}")
    if plugin.get("name") != "tilly-engineer-skills":
        failures.append("source plugin.json name must be tilly-engineer-skills")
    skills = plugin.get("skills", [])
    if not isinstance(skills, list) or "./skills/" not in {str(item) for item in skills}:
        failures.append("source plugin.json must retain package-template ./skills/ path")

    plugins = marketplace.get("plugins", [])
    if not isinstance(plugins, list) or not plugins:
        failures.append("source marketplace.json must declare template plugins")
    else:
        package = plugins[0] if isinstance(plugins[0], dict) else {}
        if package.get("version") != VERSION:
            failures.append(f"source marketplace package version must be {VERSION}")

    for skill in CLAUDE_SKILLS:
        if not (ROOT / f"src/adapters/claude/skills/{skill}/SKILL.md").exists():
            failures.append(f"missing Claude source skill: {skill}")
    return failures


def validate_target_omits_plugin(target: Path) -> list[str]:
    failures: list[str] = []
    target = target.resolve()
    for relpath in (
        "CLAUDE.md",
        ".claude/skills/tes-engineering-discipline/SKILL.md",
        ".claude/skills/tes-init/SKILL.md",
    ):
        if not (target / relpath).exists():
            failures.append(f"missing Claude runtime path: {relpath}")
    for relpath in TARGET_PLUGIN_PATHS:
        if (target / relpath).exists():
            failures.append(f"Claude plugin artifact must not be target-installed: {relpath}")
    return failures


def self_test_result() -> dict[str, Any]:
    failures = validate_source_plugin()
    with tempfile.TemporaryDirectory(prefix="tes-claude-materialize-source-only-") as tempdir:
        out_root = Path(tempdir) / "adapters"
        result = materialize_adapter.materialize("claude", out_root)
        failures.extend(str(item) for item in result["failures"])
        root = Path(str(result["root"]))
        for relpath in TARGET_PLUGIN_PATHS:
            if (root / relpath).exists():
                failures.append(f"Claude plugin artifact materialized: {relpath}")

    with tempfile.TemporaryDirectory(prefix="tes-claude-plugin-source-only-") as tempdir:
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
        if code != 0:
            failures.extend(["claude adapter install failed", *stdout.splitlines(), *stderr.splitlines()])
        else:
            failures.extend(validate_target_omits_plugin(target))

    return {
        "version": VERSION,
        "status": "FAIL" if failures else "PASS",
        "scope": "source-only-plugin",
        "failures": failures,
    }


def self_test() -> int:
    result = self_test_result()
    print(json.dumps(result, indent=2))
    print("[claude-plugin-oracle] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test or not args.target:
        return self_test()

    failures = validate_source_plugin()
    failures.extend(validate_target_omits_plugin(args.target.resolve()))
    result = {
        "version": VERSION,
        "status": "FAIL" if failures else "PASS",
        "target": str(args.target),
        "scope": "source-only-plugin",
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    print("[claude-plugin-oracle] " + result["status"])
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
