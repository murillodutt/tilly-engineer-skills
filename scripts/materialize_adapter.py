#!/usr/bin/env python3
"""Materialize installable adapter trees from canonical src sources."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "dist" / "adapters"
VERSION = "0.3.93"
CODEX_SKILLS = (
    "tes-engineering-discipline",
    "tes-init",
    "tes-align",
    "tes-prospect",
    "tes-mine",
    "tes-open-obsidian",
    "tes-cortex",
    "tes-mcp",
    "tes-field-reports",
    "tes-doctor",
    "tes-adapter",
    "tes-bench",
)
CLAUDE_SKILLS = (
    "tes-guidelines",
    "tes-init",
    "tes-align",
    "tes-prospect",
    "tes-mine",
    "tes-open-obsidian",
    "tes-cortex",
    "tes-mcp",
    "tes-field-reports",
    "tes-doctor",
    "tes-adapter",
    "tes-bench",
)
CLAUDE_PLUGIN_SKILL_ROOT = "skills"
CLAUDE_PROJECT_SKILL_ROOT = ".claude/skills"
CODEX_PLUGIN_ROOT = "plugins/tilly-engineer-skills"
CODEX_PLUGIN_SKILL_ROOT = f"{CODEX_PLUGIN_ROOT}/skills"
FORBIDDEN_OUTPUT_REFS = (
    "src/adapters/",
    "docs/adapters/",
    "docs/evals/",
    "docs/mesh/",
    "scripts/materialize_adapter.py",
    "scripts/validate_reference_package.py",
)


@dataclass(frozen=True)
class CopyRule:
    source: str
    target: str
    kind: str = "file"


ADAPTERS: dict[str, tuple[CopyRule, ...]] = {
    "codex": (
        CopyRule("src/adapters/codex/AGENTS.md", "AGENTS.md"),
        CopyRule("src/adapters/codex/plugin/plugin.json", f"{CODEX_PLUGIN_ROOT}/.codex-plugin/plugin.json"),
        CopyRule("src/adapters/codex/plugin/marketplace.json", ".agents/plugins/marketplace.json"),
        *(
            CopyRule(
                f"src/adapters/codex/skills/{skill}",
                f".agents/skills/{skill}",
                "tree",
            )
            for skill in CODEX_SKILLS
        ),
        *(
            CopyRule(
                f"src/adapters/codex/skills/{skill}",
                f"{CODEX_PLUGIN_SKILL_ROOT}/{skill}",
                "tree",
            )
            for skill in CODEX_SKILLS
        ),
    ),
    "cursor": (
        CopyRule("src/adapters/cursor/CURSOR.md", "CURSOR.md"),
        CopyRule(
            "src/adapters/cursor/rules/tes-guidelines.mdc",
            ".cursor/rules/tes-guidelines.mdc",
        ),
        CopyRule(
            "src/adapters/cursor/rules/tes-runtime-capabilities.mdc",
            ".cursor/rules/tes-runtime-capabilities.mdc",
        ),
    ),
    "claude": (
        CopyRule("src/adapters/claude/CLAUDE.md", "CLAUDE.md"),
        CopyRule("src/adapters/claude/plugin/plugin.json", ".claude-plugin/plugin.json"),
        CopyRule("src/adapters/claude/plugin/marketplace.json", ".claude-plugin/marketplace.json"),
        *(
            CopyRule(
                f"src/adapters/claude/skills/{skill}",
                f"{CLAUDE_PLUGIN_SKILL_ROOT}/{skill}",
                "tree",
            )
            for skill in CLAUDE_SKILLS
        ),
        *(
            CopyRule(
                f"src/adapters/claude/skills/{skill}",
                f"{CLAUDE_PROJECT_SKILL_ROOT}/{skill}",
                "tree",
            )
            for skill in CLAUDE_SKILLS
        ),
    ),
}


def copy_rule(rule: CopyRule, adapter_root: Path) -> list[str]:
    source = ROOT / rule.source
    target = adapter_root / rule.target
    if not source.exists():
        raise FileNotFoundError(f"missing source: {rule.source}")

    target.parent.mkdir(parents=True, exist_ok=True)
    if rule.kind == "tree":
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
        return [
            str(path.relative_to(adapter_root))
            for path in sorted(target.rglob("*"))
            if path.is_file()
        ]

    if rule.kind != "file":
        raise ValueError(f"unknown copy kind for {rule.source}: {rule.kind}")

    shutil.copy2(source, target)
    return [rule.target]


def run_oracle(adapter_root: Path, relpath: str) -> str | None:
    result = subprocess.run(
        [sys.executable, relpath, "--self-test"],
        cwd=adapter_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return None
    return "\n".join([result.stdout.strip(), result.stderr.strip()]).strip()


def validate_adapter(adapter: str, adapter_root: Path) -> list[str]:
    failures: list[str] = []

    for rule in ADAPTERS[adapter]:
        target = adapter_root / rule.target
        if not target.exists():
            failures.append(f"{adapter}: missing target {rule.target}")

    if (adapter_root / "src").exists():
        failures.append(f"{adapter}: output leaked source directory")

    for path in sorted(adapter_root.rglob("*")):
        if path.name == ".cursorrules":
            failures.append(f"{adapter}: legacy Cursor rules file is forbidden: {path.relative_to(adapter_root)}")
        if not path.is_file() or path.suffix not in {".md", ".mdc", ".json", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_OUTPUT_REFS:
            if forbidden in text:
                relpath = path.relative_to(adapter_root)
                failures.append(f"{adapter}: materialized {relpath} references source-only path {forbidden}")

    if adapter == "codex":
        oracle = ".agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py"
        if not (adapter_root / oracle).exists():
            failures.append(f"codex: missing oracle {oracle}")
        else:
            oracle_failure = run_oracle(adapter_root, oracle)
            if oracle_failure:
                failures.append(f"codex oracle failed: {oracle_failure}")
        for skill in CODEX_SKILLS:
            if not (adapter_root / f".agents/skills/{skill}/SKILL.md").exists():
                failures.append(f"codex: missing {skill} skill")
            if not (adapter_root / f"{CODEX_PLUGIN_SKILL_ROOT}/{skill}/SKILL.md").exists():
                failures.append(f"codex: missing plugin skill {skill}")
        plugin = adapter_root / f"{CODEX_PLUGIN_ROOT}/.codex-plugin/plugin.json"
        marketplace = adapter_root / ".agents/plugins/marketplace.json"
        if plugin.exists():
            data = json.loads(plugin.read_text(encoding="utf-8"))
            if data.get("version") != VERSION:
                failures.append(f"codex: plugin version must be {VERSION}")
            if data.get("skills") != "./skills/":
                failures.append("codex: plugin must declare ./skills/")
        else:
            failures.append("codex: missing plugin.json")
        if marketplace.exists():
            data = json.loads(marketplace.read_text(encoding="utf-8"))
            metadata = data.get("metadata", {})
            if not isinstance(metadata, dict) or metadata.get("version") != VERSION:
                failures.append(f"codex: marketplace metadata version must be {VERSION}")
            plugins = data.get("plugins", [])
            if not isinstance(plugins, list) or not plugins:
                failures.append("codex: marketplace must declare plugins")
            else:
                if isinstance(plugins[0], dict) and plugins[0].get("version") != VERSION:
                    failures.append(f"codex: marketplace plugin version must be {VERSION}")
                source = plugins[0].get("source") if isinstance(plugins[0], dict) else None
                if not isinstance(source, dict):
                    failures.append("codex: marketplace source must be object")
                else:
                    path = source.get("path")
                    if path != f"./{CODEX_PLUGIN_ROOT}":
                        failures.append(f"codex: marketplace source.path must be ./{CODEX_PLUGIN_ROOT}")
                    resolved = (adapter_root / str(path)).resolve()
                    resolved_adapter_root = adapter_root.resolve()
                    try:
                        resolved.relative_to(resolved_adapter_root)
                    except ValueError:
                        failures.append(f"codex: marketplace source must resolve inside adapter root: {path}")
                    if not (resolved / ".codex-plugin/plugin.json").exists():
                        failures.append("codex: marketplace source does not resolve to plugin root")
        else:
            failures.append("codex: missing marketplace.json")

    if adapter == "cursor":
        for relpath in (
            ".cursor/rules/tes-guidelines.mdc",
            ".cursor/rules/tes-runtime-capabilities.mdc",
        ):
            rule = adapter_root / relpath
            text = rule.read_text(encoding="utf-8") if rule.exists() else ""
            if not rule.exists():
                failures.append(f"cursor: missing {relpath}")
                continue
            if "description:" not in text:
                failures.append(f"cursor: {relpath} must keep description frontmatter")
            if "alwaysApply: true" not in text:
                failures.append(f"cursor: {relpath} must keep alwaysApply: true")

    if adapter == "claude":
        plugin = adapter_root / ".claude-plugin/plugin.json"
        marketplace = adapter_root / ".claude-plugin/marketplace.json"
        if plugin.exists():
            data = json.loads(plugin.read_text(encoding="utf-8"))
            if data.get("version") != VERSION:
                failures.append(f"claude: plugin version must be {VERSION}")
            declared_paths = data.get("skills", [])
            if not isinstance(declared_paths, list):
                failures.append("claude: plugin skills must be a list")
                declared_paths = []
            for skill in declared_paths:
                skill_path = Path(str(skill))
                if skill_path.is_absolute() or ".." in skill_path.parts:
                    failures.append(f"claude: plugin skill path must stay inside plugin root: {skill}")
                    continue
                if not str(skill).startswith("./"):
                    failures.append(f"claude: plugin skill path must start with ./: {skill}")
                    continue
                plugin_root = plugin.parent.parent
                resolved = (plugin_root / skill_path).resolve()
                if not resolved.exists():
                    failures.append(f"claude: plugin skill path does not exist: {skill}")
            if "./skills/" not in {str(skill) for skill in declared_paths}:
                failures.append("claude: plugin must declare ./skills/")
            for skill in CLAUDE_SKILLS:
                if not (adapter_root / f"{CLAUDE_PLUGIN_SKILL_ROOT}/{skill}/SKILL.md").exists():
                    failures.append(f"claude: missing plugin skill {skill}")
                if not (adapter_root / f"{CLAUDE_PROJECT_SKILL_ROOT}/{skill}/SKILL.md").exists():
                    failures.append(f"claude: missing project skill {skill}")
        else:
            failures.append("claude: missing plugin.json")
        if marketplace.exists():
            data = json.loads(marketplace.read_text(encoding="utf-8"))
            for plugin_entry in data.get("plugins", []):
                source = plugin_entry.get("source")
                if not source:
                    failures.append("claude: marketplace plugin missing source")
                    continue
                resolved = (marketplace.parent / source).resolve()
                if not (resolved / ".claude-plugin/plugin.json").exists():
                    failures.append(f"claude: marketplace source does not resolve to adapter root: {source}")

    return failures


def materialize(adapter: str, out_root: Path) -> dict[str, object]:
    adapter_root = out_root / adapter
    if adapter_root.exists():
        shutil.rmtree(adapter_root)
    adapter_root.mkdir(parents=True)

    files: list[str] = []
    for rule in ADAPTERS[adapter]:
        files.extend(copy_rule(rule, adapter_root))

    failures = validate_adapter(adapter, adapter_root)
    return {
        "adapter": adapter,
        "root": str(adapter_root),
        "files": sorted(files),
        "file_count": len(files),
        "failures": failures,
    }


def selected_adapters(adapter: str) -> list[str]:
    if adapter == "all":
        return sorted(ADAPTERS)
    return [adapter]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("adapter", choices=["all", *sorted(ADAPTERS)])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    failures: list[str] = []

    if args.check:
        with tempfile.TemporaryDirectory(prefix="tes-engineer-skills-") as tempdir:
            out_root = Path(tempdir) / "adapters"
            results = [materialize(adapter, out_root) for adapter in selected_adapters(args.adapter)]
            for result in results:
                failures.extend(result["failures"])
            print_result(results, check=True)
    else:
        out_root = args.out
        results = [materialize(adapter, out_root) for adapter in selected_adapters(args.adapter)]
        for result in results:
            failures.extend(result["failures"])
        print_result(results, check=False)

    if failures:
        print("[materialize] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("[materialize] PASS")
    return 0


def print_result(results: list[dict[str, object]], check: bool) -> None:
    print(json.dumps({
        "version": VERSION,
        "mode": "check" if check else "write",
        "adapters": [
            {
                "adapter": result["adapter"],
                "root": result["root"],
                "file_count": result["file_count"],
            }
            for result in results
        ],
    }, indent=2))


if __name__ == "__main__":
    sys.exit(main())
