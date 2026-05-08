#!/usr/bin/env python3
"""Certify TES command-trigger parity across adapter surfaces."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.57"

PREFERRED_TRIGGERS = (
    "/tes-init",
    "/tes-update",
    "/tes-cortex",
    "/tes-curate",
    "/tes-mcp",
    "/tes-field-reports",
    "/tes-doctor",
    "/tes-adapter",
    "/tes-bench",
)

COMPATIBLE_ALIASES = (
    "/tes:init",
    "/tes:update",
    "/tes:cortex",
    "/tes:mcp",
    "/tes:field-reports",
    "/tes:doctor",
    "/tes:adapter",
    "/tes:bench",
    "/tes:check",
    "/tes:certify",
    "/tes:recall",
    "/tes:learn",
    "/tes:reflect",
    "/tes:curate",
)

NATURAL_INTENTS = (
    "tes init",
    "tes update",
    "Atualizar TES",
    "atualizar TES",
    "initialize TES",
    "install TES",
    "recertify TES",
    "inicializar TES",
    "instalar TES",
    "recertificar TES",
)

CLAUDE_INVALID_SLASH_TERMS = (
    "/tes:*",
    "invalid slash",
    "TES intent",
    "do not stop to ask",
)

DOC_SOURCE_GROUPS = {
    "command_triggers_doc": ("docs/install/COMMAND-TRIGGERS.md",),
    "platform_differences_doc": ("docs/adapters/PLATFORM-DIFFERENCES.md",),
}

PLATFORM_SOURCE_GROUPS = {
    "codex": (
        "src/adapters/codex/AGENTS.md",
        "src/adapters/codex/skills/tes-init/SKILL.md",
        "src/adapters/codex/skills/tes-cortex/SKILL.md",
        "src/adapters/codex/skills/tes-mcp/SKILL.md",
        "src/adapters/codex/skills/tes-doctor/SKILL.md",
        "src/adapters/codex/skills/tes-adapter/SKILL.md",
        "src/adapters/codex/skills/tes-bench/SKILL.md",
    ),
    "claude": (
        "src/adapters/claude/CLAUDE.md",
        "src/adapters/claude/skills/tes-init/SKILL.md",
        "src/adapters/claude/skills/tes-cortex/SKILL.md",
        "src/adapters/claude/skills/tes-mcp/SKILL.md",
        "src/adapters/claude/skills/tes-doctor/SKILL.md",
        "src/adapters/claude/skills/tes-adapter/SKILL.md",
        "src/adapters/claude/skills/tes-bench/SKILL.md",
    ),
    "cursor": (
        "src/adapters/cursor/rules/tes-guidelines.mdc",
    ),
}


CLAUDE_PROJECT_SKILLS = (
    "tes-guidelines",
    "tes-init",
    "tes-cortex",
    "tes-mcp",
    "tes-doctor",
    "tes-adapter",
    "tes-bench",
)
CODEX_PROJECT_SKILLS = (
    "tes-engineering-discipline",
    "tes-init",
    "tes-cortex",
    "tes-mcp",
    "tes-doctor",
    "tes-adapter",
    "tes-bench",
)


def read_group(root: Path, paths: tuple[str, ...]) -> tuple[str, list[str]]:
    chunks: list[str] = []
    failures: list[str] = []
    for relpath in paths:
        path = root / relpath
        if not path.exists():
            failures.append(f"missing trigger source: {relpath}")
            continue
        chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks), failures


def missing_exact(text: str, terms: tuple[str, ...]) -> list[str]:
    return [term for term in terms if term not in text]


def missing_natural(text: str) -> list[str]:
    folded = text.casefold()
    return [term for term in NATURAL_INTENTS if term.casefold() not in folded]


def check_text(name: str, text: str) -> list[str]:
    failures: list[str] = []
    for term in missing_exact(text, PREFERRED_TRIGGERS):
        failures.append(f"{name} missing preferred trigger: {term}")
    for term in missing_exact(text, COMPATIBLE_ALIASES):
        failures.append(f"{name} missing compatible alias: {term}")
    for term in missing_natural(text):
        failures.append(f"{name} missing natural intent: {term}")
    return failures


def check_claude_invalid_slash(text: str) -> list[str]:
    failures: list[str] = []
    for term in CLAUDE_INVALID_SLASH_TERMS:
        if term not in text:
            failures.append(f"claude missing invalid-slash fallback term: {term}")
    return failures


def installed_platform_paths(root: Path, platform: str) -> tuple[str, ...]:
    if platform == "codex":
        return (
            "AGENTS.md",
            *(f".agents/skills/{skill}/SKILL.md" for skill in CODEX_PROJECT_SKILLS),
        )
    if platform == "claude":
        return (
            "CLAUDE.md",
            *(f".claude/skills/{skill}/SKILL.md" for skill in CLAUDE_PROJECT_SKILLS),
            *(f"skills/{skill}/SKILL.md" for skill in CLAUDE_PROJECT_SKILLS),
        )
    if platform == "cursor":
        cursor_rules = tuple(
            path.relative_to(root).as_posix()
            for path in sorted((root / ".cursor/rules").glob("*.mdc"))
            if path.is_file()
        )
        return ("CURSOR.md", *cursor_rules)
    return ()


def installed_platform_detected(root: Path, platform: str) -> bool:
    if platform == "codex":
        return (root / "AGENTS.md").exists() or (root / ".agents/skills").exists()
    if platform == "claude":
        return (
            (root / "CLAUDE.md").exists()
            or (root / ".claude/skills").exists()
            or (root / "skills").exists()
            or (root / ".claude-plugin/plugin.json").exists()
        )
    if platform == "cursor":
        return (root / "CURSOR.md").exists() or (root / ".cursor/rules").exists()
    return False


def required_installed_files(platform: str) -> tuple[str, ...]:
    if platform == "codex":
        return (
            "AGENTS.md",
            ".agents/skills/tes-engineering-discipline/SKILL.md",
            ".agents/skills/tes-init/SKILL.md",
        )
    if platform == "claude":
        return (
            "CLAUDE.md",
            ".claude/skills/tes-guidelines/SKILL.md",
            ".claude/skills/tes-init/SKILL.md",
        )
    if platform == "cursor":
        return (".cursor/rules/*.mdc",)
    return ()


def check_installed_target(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    checked: list[dict[str, Any]] = []

    for platform in ("codex", "claude", "cursor"):
        if not installed_platform_detected(root, platform):
            checked.append({"group": platform, "paths": [], "status": "NOT_APPLIED"})
            continue

        paths = installed_platform_paths(root, platform)
        existing_paths = tuple(path for path in paths if (root / path).exists())
        text, group_failures = read_group(root, existing_paths)
        missing_required = []
        for relpath in required_installed_files(platform):
            if relpath.endswith("*.mdc"):
                if not any((root / ".cursor/rules").glob("*.mdc")):
                    missing_required.append(relpath)
                continue
            if not (root / relpath).exists():
                missing_required.append(relpath)
        group_failures.extend(f"missing installed trigger surface: {relpath}" for relpath in missing_required)
        group_failures.extend(check_text(platform, text))
        if platform == "claude":
            group_failures.extend(check_claude_invalid_slash(text))
        failures.extend(group_failures)
        checked.append(
            {
                "group": platform,
                "paths": list(existing_paths),
                "status": "PASS" if not group_failures else "FAIL",
            }
        )

    return {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "mode": "installed-target",
        "target": str(root),
        "preferred_triggers": list(PREFERRED_TRIGGERS),
        "compatible_aliases": list(COMPATIBLE_ALIASES),
        "natural_intents": list(NATURAL_INTENTS),
        "checked": checked,
        "failures": failures,
    }


def analyze(root: Path = ROOT) -> dict[str, Any]:
    failures: list[str] = []
    checked: list[dict[str, Any]] = []

    for group, paths in DOC_SOURCE_GROUPS.items():
        text, group_failures = read_group(root, paths)
        failures.extend(group_failures)
        group_failures.extend(check_text(group, text))
        failures.extend(item for item in group_failures if item not in failures)
        checked.append({"group": group, "paths": list(paths), "status": "PASS" if not group_failures else "FAIL"})

    for platform, paths in PLATFORM_SOURCE_GROUPS.items():
        text, group_failures = read_group(root, paths)
        failures.extend(group_failures)
        group_failures.extend(check_text(platform, text))
        if platform == "claude":
            group_failures.extend(check_claude_invalid_slash(text))
        failures.extend(item for item in group_failures if item not in failures)
        checked.append({"group": platform, "paths": list(paths), "status": "PASS" if not group_failures else "FAIL"})

    return {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "preferred_triggers": list(PREFERRED_TRIGGERS),
        "compatible_aliases": list(COMPATIBLE_ALIASES),
        "natural_intents": list(NATURAL_INTENTS),
        "checked": checked,
        "failures": failures,
    }


def run_fixture_tests() -> list[str]:
    failures: list[str] = []
    good_text = "\n".join(
        [
            *PREFERRED_TRIGGERS,
            *COMPATIBLE_ALIASES,
            *NATURAL_INTENTS,
            *CLAUDE_INVALID_SLASH_TERMS,
        ]
    )
    if check_text("fixture_good", good_text) or check_claude_invalid_slash(good_text):
        failures.append("good fixture must pass trigger and Claude fallback checks")

    bad_claude = good_text.replace("invalid slash", "invalid command")
    if not any("invalid-slash fallback" in item for item in check_claude_invalid_slash(bad_claude)):
        failures.append("bad Claude fixture must fail without invalid-slash fallback")

    bad_trigger = good_text.replace("/tes-bench", "")
    if not any("/tes-bench" in item for item in check_text("fixture_bad_trigger", bad_trigger)):
        failures.append("bad trigger fixture must fail when a preferred trigger is absent")

    bad_natural = good_text.replace("recertificar TES", "")
    if not any("recertificar TES" in item for item in check_text("fixture_bad_natural", bad_natural)):
        failures.append("bad natural fixture must fail when a natural intent is absent")

    import tempfile

    with tempfile.TemporaryDirectory(prefix="tes-trigger-oracle-good-") as tempdir:
        target = Path(tempdir)
        (target / ".claude/skills/tes-guidelines").mkdir(parents=True)
        (target / ".claude/skills/tes-init").mkdir(parents=True)
        (target / "CLAUDE.md").write_text(good_text, encoding="utf-8")
        (target / ".claude/skills/tes-guidelines/SKILL.md").write_text(good_text, encoding="utf-8")
        (target / ".claude/skills/tes-init/SKILL.md").write_text(good_text, encoding="utf-8")
        if check_installed_target(target)["status"] != "PASS":
            failures.append("good installed Claude fixture must pass")

    with tempfile.TemporaryDirectory(prefix="tes-trigger-oracle-bad-") as tempdir:
        target = Path(tempdir)
        (target / "CLAUDE.md").write_text(good_text, encoding="utf-8")
        result = check_installed_target(target)
        if result["status"] != "FAIL" or not any(".claude/skills/tes-init/SKILL.md" in item for item in result["failures"]):
            failures.append("bad installed Claude fixture must fail without project skills")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--target", type=Path, help="validate installed trigger surfaces in a target project")
    args = parser.parse_args()

    result = check_installed_target(args.target.resolve()) if args.target else analyze()
    fixture_failures = run_fixture_tests() if args.self_test else []
    if fixture_failures:
        result["status"] = "FAIL"
        result["fixture_failures"] = fixture_failures
        result["failures"] = [*result["failures"], *fixture_failures]

    print(json.dumps(result, indent=2, sort_keys=True))
    print("[command-triggers] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
