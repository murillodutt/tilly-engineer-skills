#!/usr/bin/env python3
"""Certify that Codex plugin metadata is source-only, not target-installed."""

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
VERSION = "0.3.154"
PLUGIN_SOURCE_ROOT = ROOT / "src/adapters/codex/plugin"
TARGET_PLUGIN_PATHS = (
    ".agents/plugins",
    "plugins/tilly-engineer-skills",
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
    manifest = read_json(PLUGIN_SOURCE_ROOT / "plugin.json", failures)
    marketplace = read_json(PLUGIN_SOURCE_ROOT / "marketplace.json", failures)

    if manifest.get("name") != "tilly-engineer-skills":
        failures.append("source plugin.json name must be tilly-engineer-skills")
    if manifest.get("version") != VERSION:
        failures.append(f"source plugin.json version must be {VERSION}")
    if manifest.get("skills") != "./skills/":
        failures.append("source plugin.json must retain package-template skills path ./skills/")
    if "hooks" in manifest:
        failures.append("source Codex plugin template must not declare hooks without a safety contract")
    if "mcpServers" in manifest:
        failures.append("source Codex plugin template must not claim bundled MCP")

    if marketplace.get("name") != "tes-skills":
        failures.append("source marketplace name must be tes-skills")
    metadata = marketplace.get("metadata")
    if not isinstance(metadata, dict) or metadata.get("version") != VERSION:
        failures.append(f"source marketplace metadata.version must be {VERSION}")
    plugins = marketplace.get("plugins", [])
    if not isinstance(plugins, list) or len(plugins) != 1:
        failures.append("source marketplace must declare exactly one template plugin")
        plugins = []
    package = plugins[0] if plugins and isinstance(plugins[0], dict) else {}
    if package.get("name") != "tilly-engineer-skills":
        failures.append("source marketplace plugin name must be tilly-engineer-skills")
    if package.get("version") != VERSION:
        failures.append(f"source marketplace plugin version must be {VERSION}")
    source = package.get("source")
    if not isinstance(source, dict) or source.get("source") != "local":
        failures.append("source marketplace plugin must stay local-template only")
    return failures


def validate_target_omits_plugin(target: Path) -> list[str]:
    failures: list[str] = []
    target = target.resolve()
    for relpath in (
        "AGENTS.md",
        ".agents/skills/tes-engineering-discipline/SKILL.md",
        ".agents/skills/tes-init/SKILL.md",
    ):
        if not (target / relpath).exists():
            failures.append(f"missing Codex runtime path: {relpath}")
    for relpath in TARGET_PLUGIN_PATHS:
        if (target / relpath).exists():
            failures.append(f"Codex plugin artifact must not be target-installed: {relpath}")
    return failures


def installed_fixture() -> tuple[Path, tempfile.TemporaryDirectory[str], list[str]]:
    temp = tempfile.TemporaryDirectory(prefix="tes-codex-plugin-source-only-")
    target = Path(temp.name)
    code, stdout, stderr = run(
        [
            sys.executable,
            str(ROOT / "scripts/install_adapter.py"),
            "--target",
            str(target),
            "--adapter",
            "codex",
            "--yes",
        ]
    )
    failures: list[str] = []
    if code != 0:
        failures.extend(["codex adapter install failed", *stdout.splitlines(), *stderr.splitlines()])
    return target, temp, failures


def self_test_result() -> dict[str, Any]:
    failures = validate_source_plugin()
    with tempfile.TemporaryDirectory(prefix="tes-codex-materialize-source-only-") as tempdir:
        out_root = Path(tempdir) / "adapters"
        result = materialize_adapter.materialize("codex", out_root)
        failures.extend(str(item) for item in result["failures"])
        root = Path(str(result["root"]))
        for relpath in TARGET_PLUGIN_PATHS:
            if (root / relpath).exists():
                failures.append(f"Codex plugin artifact materialized: {relpath}")

    target, temp, setup_failures = installed_fixture()
    try:
        failures.extend(setup_failures)
        if not setup_failures:
            failures.extend(validate_target_omits_plugin(target))
    finally:
        temp.cleanup()

    return {
        "version": VERSION,
        "status": "FAIL" if failures else "PASS",
        "scope": "source-only-plugin",
        "failures": failures,
    }


def self_test() -> int:
    result = self_test_result()
    print(json.dumps(result, indent=2))
    print("[codex-plugin-oracle] " + result["status"])
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
    print("[codex-plugin-oracle] " + result["status"])
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
