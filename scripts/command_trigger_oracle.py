#!/usr/bin/env python3
"""Certify TES command-trigger parity across adapter surfaces."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.131"

PREFERRED_TRIGGERS = (
    "/tes-init",
    "/tes-setup",
    "/tes-update",
    "/tes-align",
    "/tes-map",
    "/tes-goal-maestro",
    "/tes-prospect",
    "/tes-mine",
    "/tes-open-obsidian",
    "/tes-cortex",
    "/tes-curate",
    "/tes-mcp",
    "/tes-field-reports",
    "/tes-doctor",
    "/tes-adapter",
    "/tes-bench",
    "/tes-bump",
)

COMPATIBLE_ALIASES = (
    "/tes:init",
    "/tes:update",
    "/tes:align",
    "/tes:gps",
    "/tes:goal-maestro",
    "/tes:prospect",
    "/tes:mine",
    "/tes:open-obsidian",
    "/tes:cortex",
    "/tes:mcp",
    "/tes:field-reports",
    "/tes:doctor",
    "/tes:adapter",
    "/tes:bench",
    "/tes:bump",
    "/tes:check",
    "/tes:certify",
    "/tes:recall",
    "/tes:learn",
    "/tes:reflect",
    "/tes:curate",
)

NATURAL_INTENTS = (
    "tes init",
    "tes setup",
    "tes update",
    "tes align",
    "tes map",
    "generate a maestral /goal prompt",
    "gerar um /goal maestral",
    "project GPS",
    "mapa TES",
    "tes open obsidian",
    "tes bump",
    "align TES",
    "align this project",
    "map this project",
    "open Obsidian",
    "open this project in Obsidian",
    "Atualizar TES",
    "atualizar TES",
    "alinhar TES",
    "alinhar projeto",
    "mapear TES",
    "mapear projeto",
    "abrir Obsidian",
    "abrir no Obsidian",
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

INIT_ROUTER_TERMS = (
    "Install/Update Gate",
    "Project Context Gate",
    "Project-Start Gate",
    "Step Zero protects installer/update writes",
    "must not block project-context initialization",
    "preflight context PASS does not replace project-start execution",
    "after helper-only",
)

REPORT_GOVERNANCE_TERMS = (
    "Project quality gates",
    "lint",
    "typecheck",
    "test",
    "BLOCKED",
    "NEEDS_REVIEW",
)

TARGET_SOURCE_GATE_TERMS = {
    "doctor": (
        "installed-target",
        "package-source",
        "Read `package.json`",
        "python3 .tes/bin/tes_install.py status --target .",
        "python3 .tes/bin/project_context_oracle.py --target .",
        "python3 .tes/bin/project_alignment_oracle.py --target .",
        "python3 .tes/bin/mantra_gate_adoption_oracle.py --target .",
        "BYPASS_SUSPECTED",
        "gate:doctor",
        "gate:staged",
        "gate:push",
        "Do not certify unavailable commands",
    ),
    "bench": (
        "package-source evidence",
        "current workspace exposes",
        "benchmark:plan",
        "benchmark:run",
        "benchmark:converge",
        "NEEDS_SOURCE",
        "Do not invent benchmark scripts",
        "Do not certify installed-target health",
    ),
}

DOC_SOURCE_GROUPS = {
    "command_triggers_doc": ("docs/install/COMMAND-TRIGGERS.md",),
    "platform_differences_doc": ("docs/adapters/PLATFORM-DIFFERENCES.md",),
}

PLATFORM_SOURCE_GROUPS = {
    "codex": (
        "src/adapters/codex/AGENTS.md",
        "src/adapters/codex/skills/tes-init/SKILL.md",
        "src/adapters/codex/skills/tes-setup/SKILL.md",
        "src/adapters/codex/skills/tes-update/SKILL.md",
        "src/adapters/codex/skills/tes-align/SKILL.md",
        "src/adapters/codex/skills/tes-map/SKILL.md",
        "src/adapters/codex/skills/tes-goal-maestro/SKILL.md",
        "src/adapters/codex/skills/tes-prospect/SKILL.md",
        "src/adapters/codex/skills/tes-mine/SKILL.md",
        "src/adapters/codex/skills/tes-open-obsidian/SKILL.md",
        "src/adapters/codex/skills/tes-cortex/SKILL.md",
        "src/adapters/codex/skills/tes-mcp/SKILL.md",
        "src/adapters/codex/skills/tes-field-reports/SKILL.md",
        "src/adapters/codex/skills/tes-doctor/SKILL.md",
        "src/adapters/codex/skills/tes-adapter/SKILL.md",
        "src/adapters/codex/skills/tes-bench/SKILL.md",
        "src/adapters/codex/skills/tes-bump/SKILL.md",
    ),
    "claude": (
        "src/adapters/claude/CLAUDE.md",
        "src/adapters/claude/skills/tes-init/SKILL.md",
        "src/adapters/claude/skills/tes-setup/SKILL.md",
        "src/adapters/claude/skills/tes-update/SKILL.md",
        "src/adapters/claude/skills/tes-align/SKILL.md",
        "src/adapters/claude/skills/tes-map/SKILL.md",
        "src/adapters/claude/skills/tes-goal-maestro/SKILL.md",
        "src/adapters/claude/skills/tes-prospect/SKILL.md",
        "src/adapters/claude/skills/tes-mine/SKILL.md",
        "src/adapters/claude/skills/tes-open-obsidian/SKILL.md",
        "src/adapters/claude/skills/tes-cortex/SKILL.md",
        "src/adapters/claude/skills/tes-mcp/SKILL.md",
        "src/adapters/claude/skills/tes-field-reports/SKILL.md",
        "src/adapters/claude/skills/tes-doctor/SKILL.md",
        "src/adapters/claude/skills/tes-adapter/SKILL.md",
        "src/adapters/claude/skills/tes-bench/SKILL.md",
        "src/adapters/claude/skills/tes-bump/SKILL.md",
    ),
    "cursor": (
        "src/adapters/cursor/rules/tes-guidelines.mdc",
        "src/adapters/cursor/rules/tes-runtime-capabilities.mdc",
    ),
}

INIT_ROUTER_SOURCE_PATHS = (
    "docs/install/COMMAND-TRIGGERS.md",
    "docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md",
    "src/adapters/codex/AGENTS.md",
    "src/adapters/codex/skills/tes-init/SKILL.md",
    "src/adapters/claude/CLAUDE.md",
    "src/adapters/claude/skills/tes-init/SKILL.md",
    "src/adapters/cursor/rules/tes-guidelines.mdc",
    "src/adapters/cursor/rules/tes-runtime-capabilities.mdc",
)

REPORT_GOVERNANCE_SOURCE_PATHS = (
    "docs/install/COMMAND-TRIGGERS.md",
    "docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md",
    "docs/install/INSTALL.md",
    "docs/install/AGENT-MANUAL.md",
    "docs/install/MINI-PROMPT.md",
)

TARGET_SOURCE_GATE_SOURCE_PATHS = {
    "doctor": (
        "src/adapters/codex/skills/tes-doctor/SKILL.md",
        "src/adapters/claude/skills/tes-doctor/SKILL.md",
    ),
    "bench": (
        "src/adapters/codex/skills/tes-bench/SKILL.md",
        "src/adapters/claude/skills/tes-bench/SKILL.md",
    ),
    "docs": (
        "docs/install/AGENT-MANUAL.md",
        "docs/install/COMMAND-TRIGGERS.md",
    ),
}


CLAUDE_PROJECT_SKILLS = (
    "tes-guidelines",
    "tes-init",
    "tes-setup",
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
)
CODEX_PROJECT_SKILLS = (
    "tes-engineering-discipline",
    "tes-init",
    "tes-setup",
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
)

VISIBLE_SKILL_ROUTES = {
    "codex": {
        "tes-prospect": ("/tes-prospect", "/tes:prospect", "cognitive brake"),
        "tes-goal-maestro": (
            "/tes-goal-maestro",
            "/tes:goal-maestro",
            "NEEDS_SPEC_MATURITY",
            "NEEDS_EXECUTION_UNIT_FIDELITY",
            "DRAFT_MATERIALIZATION_TREE",
            "NEEDS_TREE_ACCEPTANCE",
            "READY_GOAL_PROMPT",
        ),
        "tes-mine": ("/tes-mine", "/tes:mine", "cognitive brake"),
        "tes-map": (
            "/tes-map",
            "/tes:gps",
            "tes_map.py",
            "map this project",
            "mapear TES",
            "mapear projeto",
        ),
        "tes-update": (
            "/tes-update",
            "/tes:update",
            "tes_update.py",
            "No project work started",
            "recommended_update_scope",
        ),
        "tes-field-reports": ("/tes-field-reports", "/tes:field-reports", "field_reports.py"),
        "tes-bump": ("/tes-bump", "/tes:bump", "tes_bump.py", "governance-check", "NEEDS_VERSION_DECISION"),
    },
    "claude": {
        "tes-prospect": ("/tes-prospect", "/tes:prospect", "cognitive brake"),
        "tes-goal-maestro": (
            "/tes-goal-maestro",
            "/tes:goal-maestro",
            "NEEDS_SPEC_MATURITY",
            "NEEDS_EXECUTION_UNIT_FIDELITY",
            "DRAFT_MATERIALIZATION_TREE",
            "NEEDS_TREE_ACCEPTANCE",
            "READY_GOAL_PROMPT",
        ),
        "tes-mine": ("/tes-mine", "/tes:mine", "cognitive brake"),
        "tes-map": (
            "/tes-map",
            "/tes:gps",
            "tes_map.py",
            "map this project",
            "mapear TES",
            "mapear projeto",
        ),
        "tes-update": (
            "/tes-update",
            "/tes:update",
            "tes_update.py",
            "No project work started",
            "recommended_update_scope",
        ),
        "tes-field-reports": ("/tes-field-reports", "/tes:field-reports", "field_reports.py"),
        "tes-bump": ("/tes-bump", "/tes:bump", "tes_bump.py", "governance-check", "NEEDS_VERSION_DECISION"),
    },
}

GROUPED_INTENT_ROUTES = {
    "codex": {
        "tes-cortex": ("/tes-curate", "/tes:curate"),
    },
    "claude": {
        "tes-cortex": ("/tes-curate", "/tes:curate"),
    },
}


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


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text)


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


def check_init_router(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    checked: list[dict[str, Any]] = []
    failures: list[str] = []
    for relpath in INIT_ROUTER_SOURCE_PATHS:
        path = root / relpath
        if not path.exists():
            failures.append(f"missing init router source: {relpath}")
            checked.append({"path": relpath, "status": "MISSING"})
            continue
        text = path.read_text(encoding="utf-8")
        normalized_text = normalized(text).casefold()
        missing = [term for term in INIT_ROUTER_TERMS if term.casefold() not in normalized_text]
        failures.extend(f"{relpath} missing init router term: {term}" for term in missing)
        checked.append({"path": relpath, "status": "PASS" if not missing else "FAIL"})
    return checked, failures


def check_report_governance(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    checked: list[dict[str, Any]] = []
    failures: list[str] = []
    for relpath in REPORT_GOVERNANCE_SOURCE_PATHS:
        path = root / relpath
        if not path.exists():
            failures.append(f"missing report governance source: {relpath}")
            checked.append({"path": relpath, "status": "MISSING"})
            continue
        text = normalized(path.read_text(encoding="utf-8")).casefold()
        missing = [term for term in REPORT_GOVERNANCE_TERMS if term.casefold() not in text]
        failures.extend(f"{relpath} missing report governance term: {term}" for term in missing)
        checked.append({"path": relpath, "status": "PASS" if not missing else "FAIL"})
    return checked, failures


def check_target_source_gate_contract(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    checked: list[dict[str, Any]] = []
    failures: list[str] = []

    for group in ("doctor", "bench"):
        terms = TARGET_SOURCE_GATE_TERMS[group]
        for relpath in TARGET_SOURCE_GATE_SOURCE_PATHS[group]:
            path = root / relpath
            if not path.exists():
                failures.append(f"missing target/source gate source: {relpath}")
                checked.append({"group": group, "path": relpath, "status": "MISSING"})
                continue
            text = normalized(path.read_text(encoding="utf-8"))
            missing = [term for term in terms if term not in text]
            failures.extend(f"{relpath} missing target/source gate term: {term}" for term in missing)
            checked.append({"group": group, "path": relpath, "status": "PASS" if not missing else "FAIL"})

    docs_expectations = {
        "docs/install/AGENT-MANUAL.md": (
            "package-source conveniences",
            "not target-project guarantees",
            "Do not certify an",
            "unless that command exists",
        ),
        "docs/install/COMMAND-TRIGGERS.md": (
            "package-source alias",
            "not a target-project guarantee",
        ),
    }
    for relpath in TARGET_SOURCE_GATE_SOURCE_PATHS["docs"]:
        path = root / relpath
        if not path.exists():
            failures.append(f"missing target/source gate doc: {relpath}")
            checked.append({"group": "docs", "path": relpath, "status": "MISSING"})
            continue
        text = normalized(path.read_text(encoding="utf-8"))
        missing = [term for term in docs_expectations[relpath] if term not in text]
        failures.extend(f"{relpath} missing target/source gate doc term: {term}" for term in missing)
        checked.append({"group": "docs", "path": relpath, "status": "PASS" if not missing else "FAIL"})

    return checked, failures


def check_skill_route_contracts(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    checked: list[dict[str, Any]] = []
    failures: list[str] = []
    for platform, skills in VISIBLE_SKILL_ROUTES.items():
        skill_root = "src/adapters/codex/skills" if platform == "codex" else "src/adapters/claude/skills"
        for skill, terms in skills.items():
            relpath = f"{skill_root}/{skill}/SKILL.md"
            path = root / relpath
            if not path.exists():
                failures.append(f"{platform} missing visible skill route: {relpath}")
                checked.append({"platform": platform, "skill": skill, "path": relpath, "status": "MISSING"})
                continue
            text = path.read_text(encoding="utf-8")
            missing = [term for term in terms if term not in text]
            failures.extend(f"{relpath} missing visible route term: {term}" for term in missing)
            checked.append({"platform": platform, "skill": skill, "path": relpath, "status": "PASS" if not missing else "FAIL"})

    for platform, skills in GROUPED_INTENT_ROUTES.items():
        skill_root = "src/adapters/codex/skills" if platform == "codex" else "src/adapters/claude/skills"
        for skill, terms in skills.items():
            relpath = f"{skill_root}/{skill}/SKILL.md"
            path = root / relpath
            if not path.exists():
                failures.append(f"{platform} missing grouped intent router: {relpath}")
                checked.append({"platform": platform, "skill": skill, "path": relpath, "status": "MISSING"})
                continue
            text = path.read_text(encoding="utf-8")
            missing = [term for term in terms if term not in text]
            failures.extend(f"{relpath} missing grouped route term: {term}" for term in missing)
            checked.append({"platform": platform, "skill": skill, "path": relpath, "status": "PASS" if not missing else "FAIL"})
    return checked, failures


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
            ".agents/skills/tes-setup/SKILL.md",
            ".agents/skills/tes-update/SKILL.md",
            ".agents/skills/tes-goal-maestro/SKILL.md",
            ".agents/skills/tes-prospect/SKILL.md",
            ".agents/skills/tes-mine/SKILL.md",
            ".agents/skills/tes-field-reports/SKILL.md",
            ".agents/skills/tes-bump/SKILL.md",
        )
    if platform == "claude":
        return (
            "CLAUDE.md",
            ".claude/skills/tes-guidelines/SKILL.md",
            ".claude/skills/tes-init/SKILL.md",
            ".claude/skills/tes-setup/SKILL.md",
            ".claude/skills/tes-update/SKILL.md",
            ".claude/skills/tes-goal-maestro/SKILL.md",
            ".claude/skills/tes-prospect/SKILL.md",
            ".claude/skills/tes-mine/SKILL.md",
            ".claude/skills/tes-field-reports/SKILL.md",
            ".claude/skills/tes-bump/SKILL.md",
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

    init_router_checked, init_router_failures = check_init_router(root)
    failures.extend(init_router_failures)
    checked.append(
        {
            "group": "init_router",
            "paths": list(INIT_ROUTER_SOURCE_PATHS),
            "status": "PASS" if not init_router_failures else "FAIL",
            "files": init_router_checked,
        }
    )

    report_governance_checked, report_governance_failures = check_report_governance(root)
    failures.extend(report_governance_failures)
    checked.append(
        {
            "group": "report_governance",
            "paths": list(REPORT_GOVERNANCE_SOURCE_PATHS),
            "status": "PASS" if not report_governance_failures else "FAIL",
            "files": report_governance_checked,
        }
    )

    target_source_checked, target_source_failures = check_target_source_gate_contract(root)
    failures.extend(target_source_failures)
    checked.append(
        {
            "group": "target_source_gate_contracts",
            "status": "PASS" if not target_source_failures else "FAIL",
            "files": target_source_checked,
        }
    )

    skill_route_checked, skill_route_failures = check_skill_route_contracts(root)
    failures.extend(skill_route_failures)
    checked.append(
        {
            "group": "skill_route_contracts",
            "status": "PASS" if not skill_route_failures else "FAIL",
            "files": skill_route_checked,
        }
    )

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
    import tempfile

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

    bad_trigger = good_text.replace("/tes-align", "")
    if not any("/tes-align" in item for item in check_text("fixture_bad_trigger", bad_trigger)):
        failures.append("bad trigger fixture must fail when a preferred trigger is absent")

    bad_natural = good_text.replace("recertificar TES", "")
    if not any("recertificar TES" in item for item in check_text("fixture_bad_natural", bad_natural)):
        failures.append("bad natural fixture must fail when a natural intent is absent")

    with tempfile.TemporaryDirectory(prefix="tes-trigger-oracle-target-source-") as tempdir:
        target = Path(tempdir)
        for paths in TARGET_SOURCE_GATE_SOURCE_PATHS.values():
            for relpath in paths:
                (target / relpath).parent.mkdir(parents=True, exist_ok=True)
                (target / relpath).write_text("", encoding="utf-8")
        checked, gate_failures = check_target_source_gate_contract(target)
        if not gate_failures or not any("tes-doctor" in item for item in gate_failures):
            failures.append("empty target/source gate fixture must fail doctor contract")
        if not any("tes-bench" in item for item in gate_failures):
            failures.append("empty target/source gate fixture must fail bench contract")
        if not any("AGENT-MANUAL" in item for item in gate_failures):
            failures.append("empty target/source gate fixture must fail docs contract")
        if not checked:
            failures.append("target/source gate fixture must report checked files")

    with tempfile.TemporaryDirectory(prefix="tes-trigger-oracle-good-") as tempdir:
        target = Path(tempdir)
        (target / ".claude/skills/tes-guidelines").mkdir(parents=True)
        (target / ".claude/skills/tes-init").mkdir(parents=True)
        (target / ".claude/skills/tes-setup").mkdir(parents=True)
        (target / ".claude/skills/tes-update").mkdir(parents=True)
        (target / ".claude/skills/tes-goal-maestro").mkdir(parents=True)
        (target / ".claude/skills/tes-prospect").mkdir(parents=True)
        (target / ".claude/skills/tes-mine").mkdir(parents=True)
        (target / ".claude/skills/tes-field-reports").mkdir(parents=True)
        (target / ".claude/skills/tes-bump").mkdir(parents=True)
        (target / "CLAUDE.md").write_text(good_text, encoding="utf-8")
        (target / ".claude/skills/tes-guidelines/SKILL.md").write_text(good_text, encoding="utf-8")
        (target / ".claude/skills/tes-init/SKILL.md").write_text(good_text, encoding="utf-8")
        (target / ".claude/skills/tes-setup/SKILL.md").write_text(good_text, encoding="utf-8")
        (target / ".claude/skills/tes-update/SKILL.md").write_text(good_text, encoding="utf-8")
        (target / ".claude/skills/tes-goal-maestro/SKILL.md").write_text(good_text, encoding="utf-8")
        (target / ".claude/skills/tes-prospect/SKILL.md").write_text(good_text, encoding="utf-8")
        (target / ".claude/skills/tes-mine/SKILL.md").write_text(good_text, encoding="utf-8")
        (target / ".claude/skills/tes-field-reports/SKILL.md").write_text(good_text, encoding="utf-8")
        (target / ".claude/skills/tes-bump/SKILL.md").write_text(good_text, encoding="utf-8")
        if check_installed_target(target)["status"] != "PASS":
            failures.append("good installed Claude fixture must pass")

    with tempfile.TemporaryDirectory(prefix="tes-trigger-oracle-bad-") as tempdir:
        target = Path(tempdir)
        (target / "CLAUDE.md").write_text(good_text, encoding="utf-8")
        result = check_installed_target(target)
        if result["status"] != "FAIL" or not any(".claude/skills/tes-init/SKILL.md" in item for item in result["failures"]):
            failures.append("bad installed Claude fixture must fail without project skills")

    return failures


def installed_helper_target() -> Path | None:
    if ROOT.name == ".tes" and Path(__file__).resolve().parent.name == "bin":
        return ROOT.parent
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--target", type=Path, help="validate installed trigger surfaces in a target project")
    parser.add_argument("--json-only", action="store_true", help="emit only the JSON result without the status trailer")
    args = parser.parse_args()

    installed_target = installed_helper_target()
    if args.target:
        result = check_installed_target(args.target.resolve())
    elif args.self_test and installed_target is not None:
        result = check_installed_target(installed_target)
        result["self_test_mode"] = "installed"
        result["coverage"] = "installed-helper-contract"
    else:
        result = analyze()
    fixture_failures = run_fixture_tests() if args.self_test else []
    if fixture_failures:
        result["status"] = "FAIL"
        result["fixture_failures"] = fixture_failures
        result["failures"] = [*result["failures"], *fixture_failures]

    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json_only:
        print("[command-triggers] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
