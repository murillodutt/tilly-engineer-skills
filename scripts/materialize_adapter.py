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
VERSION = "0.3.12"
CODEX_SKILLS = (
    "tilly-engineering-discipline",
    "tilly-init",
    "tilly-cortex",
    "tilly-mcp",
    "tilly-doctor",
    "tilly-adapter",
    "tilly-bench",
)
CLAUDE_SKILLS = (
    "tilly-guidelines",
    "tilly-init",
    "tilly-cortex",
    "tilly-mcp",
    "tilly-doctor",
    "tilly-adapter",
    "tilly-bench",
)
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
        *(
            CopyRule(
                f"src/adapters/codex/skills/{skill}",
                f".agents/skills/{skill}",
                "tree",
            )
            for skill in CODEX_SKILLS
        ),
    ),
    "cursor": (
        CopyRule("src/adapters/cursor/CURSOR.md", "CURSOR.md"),
        CopyRule(
            "src/adapters/cursor/rules/tilly-guidelines.mdc",
            ".cursor/rules/tilly-guidelines.mdc",
        ),
    ),
    "claude": (
        CopyRule("src/adapters/claude/CLAUDE.md", "CLAUDE.md"),
        CopyRule("src/adapters/claude/plugin/plugin.json", ".claude-plugin/plugin.json"),
        CopyRule("src/adapters/claude/plugin/marketplace.json", ".claude-plugin/marketplace.json"),
        *(
            CopyRule(
                f"src/adapters/claude/skills/{skill}",
                f"skills/{skill}",
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
        oracle = ".agents/skills/tilly-engineering-discipline/scripts/discipline_oracle.py"
        if not (adapter_root / oracle).exists():
            failures.append(f"codex: missing oracle {oracle}")
        else:
            oracle_failure = run_oracle(adapter_root, oracle)
            if oracle_failure:
                failures.append(f"codex oracle failed: {oracle_failure}")
        for skill in CODEX_SKILLS:
            if not (adapter_root / f".agents/skills/{skill}/SKILL.md").exists():
                failures.append(f"codex: missing {skill} skill")

    if adapter == "cursor":
        rule = adapter_root / ".cursor/rules/tilly-guidelines.mdc"
        text = rule.read_text(encoding="utf-8") if rule.exists() else ""
        if "description:" not in text:
            failures.append("cursor: rule must keep description frontmatter")
        if "alwaysApply: true" not in text:
            failures.append("cursor: rule must keep alwaysApply: true")

    if adapter == "claude":
        plugin = adapter_root / ".claude-plugin/plugin.json"
        marketplace = adapter_root / ".claude-plugin/marketplace.json"
        if plugin.exists():
            data = json.loads(plugin.read_text(encoding="utf-8"))
            if data.get("version") != VERSION:
                failures.append(f"claude: plugin version must be {VERSION}")
            for skill in data.get("skills", []):
                skill_path = Path(skill)
                if skill_path.is_absolute() or ".." in skill_path.parts:
                    failures.append(f"claude: plugin skill path must stay inside plugin root: {skill}")
                    continue
                plugin_root = plugin.parent.parent
                resolved = (plugin_root / skill_path).resolve()
                if not resolved.exists():
                    failures.append(f"claude: plugin skill path does not exist: {skill}")
            expected_skills = {f"skills/{skill}" for skill in CLAUDE_SKILLS}
            declared_skills = {str(skill) for skill in data.get("skills", [])}
            missing_skills = sorted(expected_skills - declared_skills)
            for skill in missing_skills:
                failures.append(f"claude: plugin must declare {skill}")
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
        with tempfile.TemporaryDirectory(prefix="tilly-engineer-skills-") as tempdir:
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
