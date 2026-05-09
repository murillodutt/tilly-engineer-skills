#!/usr/bin/env python3
"""Certify the local Codex adapter/plugin package shape."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

import materialize_adapter


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.71"
CODEX_SKILLS = materialize_adapter.CODEX_SKILLS
PLUGIN_ROOT = Path("plugins/tilly-engineer-skills")
TRIGGER_TERMS = (
    "/tes-init",
    "/tes-update",
    "/tes:init",
    "/tes:update",
    "tes init",
    "tes update",
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


def validate_relative_path(value: str, root: Path, label: str, failures: list[str]) -> Path | None:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        failures.append(f"{label} must stay inside plugin root: {value}")
        return None
    if not value.startswith("./"):
        failures.append(f"{label} must start with ./: {value}")
        return None
    resolved = (root / path).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        failures.append(f"{label} escapes plugin root: {value}")
        return None
    return resolved


def validate_plugin(target: Path) -> list[str]:
    target = target.resolve()
    failures: list[str] = []
    plugin_root = target / PLUGIN_ROOT
    manifest_path = plugin_root / ".codex-plugin/plugin.json"
    marketplace_path = target / ".agents/plugins/marketplace.json"

    required = (
        "AGENTS.md",
        ".agents/plugins/marketplace.json",
        "plugins/tilly-engineer-skills/.codex-plugin/plugin.json",
        *(f".agents/skills/{skill}/SKILL.md" for skill in CODEX_SKILLS),
        *(f"plugins/tilly-engineer-skills/skills/{skill}/SKILL.md" for skill in CODEX_SKILLS),
    )
    for relpath in required:
        if not (target / relpath).exists():
            failures.append(f"missing installed path: {relpath}")

    manifest = read_json(manifest_path, failures)
    if manifest.get("name") != "tilly-engineer-skills":
        failures.append("plugin.json name must be tilly-engineer-skills")
    if manifest.get("version") != VERSION:
        failures.append(f"plugin.json version must be {VERSION}")
    if manifest.get("skills") != "./skills/":
        failures.append("plugin.json must point skills to ./skills/")
    if "hooks" in manifest:
        failures.append("Codex plugin must not declare hooks without a safety contract")
    if "mcpServers" in manifest:
        failures.append("Codex plugin must not claim bundled MCP before a plugin MCP oracle exists")

    skills_path = validate_relative_path(str(manifest.get("skills", "")), plugin_root, "plugin skills path", failures)
    if skills_path and not skills_path.exists():
        failures.append("plugin skills path does not exist: ./skills/")

    marketplace = read_json(marketplace_path, failures)
    if marketplace.get("name") != "tes-skills":
        failures.append("marketplace name must be tes-skills")
    metadata = marketplace.get("metadata")
    if not isinstance(metadata, dict) or metadata.get("version") != VERSION:
        failures.append(f"marketplace metadata.version must be {VERSION}")
    plugins = marketplace.get("plugins", [])
    if not isinstance(plugins, list) or len(plugins) != 1:
        failures.append("marketplace.json must declare exactly one TES plugin")
        plugins = []
    package = plugins[0] if plugins and isinstance(plugins[0], dict) else {}
    if package.get("name") != "tilly-engineer-skills":
        failures.append("marketplace plugin name must be tilly-engineer-skills")
    if package.get("version") != VERSION:
        failures.append(f"marketplace plugin version must be {VERSION}")
    source = package.get("source")
    if not isinstance(source, dict):
        failures.append("marketplace source must be an object")
        source = {}
    if source.get("source") != "local":
        failures.append("marketplace source.source must be local")
    source_path = str(source.get("path", ""))
    if source_path != "./plugins/tilly-engineer-skills":
        failures.append("marketplace source.path must be ./plugins/tilly-engineer-skills")
    policy = package.get("policy")
    if not isinstance(policy, dict):
        failures.append("marketplace policy must be an object")
        policy = {}
    if policy.get("installation") != "AVAILABLE":
        failures.append("marketplace policy.installation must be AVAILABLE")
    if not policy.get("authentication"):
        failures.append("marketplace policy.authentication must be explicit")
    if not package.get("category"):
        failures.append("marketplace plugin must declare category")
    resolved_source = (target / source_path).resolve()
    try:
        resolved_source.relative_to(target)
    except ValueError:
        failures.append(f"marketplace source must resolve inside target: {source_path}")
    if not (resolved_source / ".codex-plugin/plugin.json").exists():
        failures.append("marketplace source does not resolve to a Codex plugin root")

    forbidden_plugin_root_paths = (
        "AGENTS.md",
        "CLAUDE.md",
        "CURSOR.md",
        ".agents",
        ".claude",
        ".claude-plugin",
        ".cursor",
        "src",
    )
    for relpath in forbidden_plugin_root_paths:
        if (plugin_root / relpath).exists():
            failures.append(f"plugin package must not contain root governance or source path: {relpath}")

    for skill in CODEX_SKILLS:
        project_skill = target / f".agents/skills/{skill}/SKILL.md"
        plugin_skill = plugin_root / f"skills/{skill}/SKILL.md"
        if not project_skill.exists() or not plugin_skill.exists():
            continue
        plugin_text = plugin_skill.read_text(encoding="utf-8")
        if "name:" not in plugin_text or "description:" not in plugin_text:
            failures.append(f"plugin skill missing frontmatter fields: {skill}")
        if skill == "tes-init":
            if not any(term in plugin_text for term in TRIGGER_TERMS):
                failures.append(f"plugin skill missing TES trigger vocabulary: {skill}")
        if plugin_text != project_skill.read_text(encoding="utf-8"):
            failures.append(f"project skill and plugin skill diverge: {skill}")

    for path in sorted(plugin_root.rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".json", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8")
        for forbidden in materialize_adapter.FORBIDDEN_OUTPUT_REFS:
            if forbidden in text:
                failures.append(f"plugin package references source-only path {forbidden}: {path.relative_to(plugin_root)}")

    return failures


def installed_fixture() -> tuple[Path, tempfile.TemporaryDirectory[str], list[str]]:
    temp = tempfile.TemporaryDirectory(prefix="tes-codex-plugin-oracle-")
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


def expect_failure(name: str, mutate: Callable[[Path], None]) -> list[str]:
    target, temp, setup_failures = installed_fixture()
    try:
        if setup_failures:
            return [f"{name}: fixture setup failed", *setup_failures]
        mutate(target)
        failures = validate_plugin(target)
        if not failures:
            return [f"{name}: negative fixture unexpectedly passed"]
        return []
    finally:
        temp.cleanup()


def self_test_result() -> dict[str, Any]:
    target, temp, failures = installed_fixture()
    try:
        failures.extend(validate_plugin(target))
    finally:
        temp.cleanup()

    negative_failures: list[str] = []
    negative_failures.extend(expect_failure(
        "missing manifest",
        lambda target: (target / PLUGIN_ROOT / ".codex-plugin/plugin.json").unlink(),
    ))
    negative_failures.extend(expect_failure(
        "stale version",
        lambda target: (target / PLUGIN_ROOT / ".codex-plugin/plugin.json").write_text(
            (target / PLUGIN_ROOT / ".codex-plugin/plugin.json")
            .read_text(encoding="utf-8")
            .replace(VERSION, "0.0.1"),
            encoding="utf-8",
        ),
    ))
    negative_failures.extend(expect_failure(
        "missing skill payload",
        lambda target: shutil.rmtree(target / PLUGIN_ROOT / "skills/tes-init"),
    ))
    negative_failures.extend(expect_failure(
        "missing trigger vocabulary",
        lambda target: (target / PLUGIN_ROOT / "skills/tes-init/SKILL.md").write_text(
            "---\nname: tes-init\ndescription: initialize something\n---\n\nNo TES triggers here.\n",
            encoding="utf-8",
        ),
    ))
    negative_failures.extend(expect_failure(
        "source duplication",
        lambda target: (target / PLUGIN_ROOT / "src/adapters/codex").mkdir(parents=True),
    ))
    negative_failures.extend(expect_failure(
        "unexpected root governance overwrite",
        lambda target: (target / PLUGIN_ROOT / "AGENTS.md").write_text("unexpected package AGENTS\n", encoding="utf-8"),
    ))

    failures.extend(negative_failures)
    return {
        "version": VERSION,
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
        "negative_fixtures": [
            "missing manifest",
            "stale version",
            "missing skill payload",
            "missing trigger vocabulary",
            "source duplication",
            "unexpected root governance overwrite",
        ],
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

    failures = validate_plugin(args.target.resolve())
    result = {
        "version": VERSION,
        "status": "FAIL" if failures else "PASS",
        "target": str(args.target),
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    print("[codex-plugin-oracle] " + result["status"])
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
