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
VERSION = "0.3.240"
CODEX_SKILLS = (
    "tes-engineering-discipline",
    "tes-init",
    "tes-setup",
    "tes-context-distill",
    "tes-update",
    "tes-align",
    "tes-map",
    "tes-goal-maestro",
    "tes-prospect",
    "tes-mine",
    "tes-open-obsidian",
    "tes-cortex",
    "tes-mcp",
    "tes-field-reports",
    "tes-doctor",
    "tes-adapter",
    "tes-bench",
    "tes-bump",
    "tes-upstream-first",
)
CLAUDE_SKILLS = (
    "tes-engineering-discipline",
    "tes-init",
    "tes-setup",
    "tes-context-distill",
    "tes-update",
    "tes-align",
    "tes-map",
    "tes-goal-maestro",
    "tes-prospect",
    "tes-mine",
    "tes-open-obsidian",
    "tes-cortex",
    "tes-mcp",
    "tes-field-reports",
    "tes-doctor",
    "tes-adapter",
    "tes-bench",
    "tes-bump",
    "tes-upstream-first",
)
CLAUDE_PROJECT_SKILL_ROOT = ".claude/skills"
FORBIDDEN_OUTPUT_REFS = (
    "src/adapters/",
    "docs/adapters/",
    "docs/evals/",
    "docs/mesh/",
    "scripts/materialize_adapter.py",
    "scripts/validate_reference_package.py",
)
RETIRED_LOCAL_GATE_MARKERS = (
    "retired local gate",
    "legacy local gate",
    "local pre-action gate",
    "project-local pre-action gate",
    "retired Claude marker",
)
BOOTLOADER_DUPLICATED_MANTRA_GATE_FRAGMENTS = (
    "Full gate fields are",
    "the full gate is still retained as evidence",
)
MANTRA_GATE_SKILL_TERMS = (
    "## Mantra Gate",
    "TES Mantra Gate",
    "destructive, remote, release, sync",
    "high-impact",
    "local edits",
)
DOCTOR_REPAIR_ROUTE_TERMS = (
    "context oracle mismatch",
    "stale quality-gate path",
    "missing Mantra Gate route",
    "trigger parity drift",
    "residue",
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
            "src/adapters/cursor/rules/tes-engineering-discipline.mdc",
            ".cursor/rules/tes-engineering-discipline.mdc",
        ),
        CopyRule(
            "src/adapters/cursor/rules/tes-runtime-capabilities.mdc",
            ".cursor/rules/tes-runtime-capabilities.mdc",
        ),
    ),
    "claude": (
        CopyRule("src/adapters/claude/CLAUDE.md", "CLAUDE.md"),
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


def read_output_text(adapter_root: Path, relpath: str) -> str:
    path = adapter_root / relpath
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def forbidden_gate_marker_failures(adapter: str, adapter_root: Path) -> list[str]:
    failures: list[str] = []
    active_surface_globs = ("AGENTS.md", "CLAUDE.md", "CURSOR.md", ".cursor/rules/*.mdc")
    for pattern in active_surface_globs:
        for path in sorted(adapter_root.glob(pattern)):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for marker in RETIRED_LOCAL_GATE_MARKERS:
                if marker.lower() in text.lower():
                    relpath = path.relative_to(adapter_root)
                    failures.append(f"{adapter}: active surface {relpath} contains retired local gate marker: {marker}")
    return failures


def thin_bootloader_failures(
    adapter: str,
    adapter_root: Path,
    relpath: str,
    route: str,
) -> list[str]:
    text = read_output_text(adapter_root, relpath)
    failures: list[str] = []
    if not text:
        return [f"{adapter}: missing bootloader {relpath}"]
    for term in ("TES Mantra Gate", route, "Do not reintroduce"):
        if term not in text:
            failures.append(f"{adapter}: {relpath} must route Mantra Gate ownership through {route}")
    for fragment in BOOTLOADER_DUPLICATED_MANTRA_GATE_FRAGMENTS:
        if fragment in text:
            failures.append(f"{adapter}: {relpath} duplicates Mantra Gate protocol instead of routing to the skill")
    return failures


def mantra_gate_skill_failures(adapter: str, adapter_root: Path, relpath: str) -> list[str]:
    text = read_output_text(adapter_root, relpath)
    failures: list[str] = []
    if not text:
        return [f"{adapter}: missing Mantra Gate owner surface {relpath}"]
    for term in MANTRA_GATE_SKILL_TERMS:
        if term not in text:
            failures.append(f"{adapter}: {relpath} missing Mantra Gate term: {term}")
    return failures


def doctor_repair_route_failures(adapter: str, adapter_root: Path, relpath: str) -> list[str]:
    text = read_output_text(adapter_root, relpath).lower()
    if not text:
        return [f"{adapter}: missing doctor skill {relpath}"]
    return [
        f"{adapter}: {relpath} missing repair route term: {term}"
        for term in DOCTOR_REPAIR_ROUTE_TERMS
        if term.lower() not in text
    ]


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

    failures.extend(forbidden_gate_marker_failures(adapter, adapter_root))

    if adapter == "codex":
        failures.extend(thin_bootloader_failures(
            adapter,
            adapter_root,
            "AGENTS.md",
            ".agents/skills/tes-engineering-discipline/SKILL.md",
        ))
        failures.extend(mantra_gate_skill_failures(
            adapter,
            adapter_root,
            ".agents/skills/tes-engineering-discipline/SKILL.md",
        ))
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
        failures.extend(doctor_repair_route_failures(
            adapter,
            adapter_root,
            ".agents/skills/tes-doctor/SKILL.md",
        ))
        for relpath in (
            ".agents/plugins/marketplace.json",
            "plugins/tilly-engineer-skills/.codex-plugin/plugin.json",
            "plugins/tilly-engineer-skills/skills",
        ):
            if (adapter_root / relpath).exists():
                failures.append(f"codex: plugin artifact must remain source-only, not materialized: {relpath}")

    if adapter == "cursor":
        failures.extend(mantra_gate_skill_failures(
            adapter,
            adapter_root,
            ".cursor/rules/tes-engineering-discipline.mdc",
        ))
        # Rule-mode contract (bootloader-to-skill migration): the discipline
        # anchor is always-on; the capability rule is the Cursor-native lazy
        # layer (Apply Intelligently), so it must be alwaysApply:false with a
        # description, per the official Cursor rule-loading model.
        cursor_rule_modes = {
            ".cursor/rules/tes-engineering-discipline.mdc": "true",
            ".cursor/rules/tes-runtime-capabilities.mdc": "false",
        }
        for relpath, mode in cursor_rule_modes.items():
            rule = adapter_root / relpath
            text = rule.read_text(encoding="utf-8") if rule.exists() else ""
            if not rule.exists():
                failures.append(f"cursor: missing {relpath}")
                continue
            if "description:" not in text:
                failures.append(f"cursor: {relpath} must keep description frontmatter")
            if f"alwaysApply: {mode}" not in text:
                failures.append(f"cursor: {relpath} must be alwaysApply: {mode}")

    if adapter == "claude":
        failures.extend(thin_bootloader_failures(
            adapter,
            adapter_root,
            "CLAUDE.md",
            ".claude/skills/tes-engineering-discipline/SKILL.md",
        ))
        failures.extend(mantra_gate_skill_failures(
            adapter,
            adapter_root,
            ".claude/skills/tes-engineering-discipline/SKILL.md",
        ))
        for skill in CLAUDE_SKILLS:
            if not (adapter_root / f"{CLAUDE_PROJECT_SKILL_ROOT}/{skill}/SKILL.md").exists():
                failures.append(f"claude: missing project skill {skill}")
        failures.extend(doctor_repair_route_failures(
            adapter,
            adapter_root,
            f"{CLAUDE_PROJECT_SKILL_ROOT}/tes-doctor/SKILL.md",
        ))
        for relpath in (
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            "skills",
        ):
            if (adapter_root / relpath).exists():
                failures.append(f"claude: plugin artifact must remain source-only, not materialized: {relpath}")

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
