#!/usr/bin/env python3
"""Validate the portable Tilly Engineering Discipline package."""

from __future__ import annotations

import argparse
from pathlib import Path
import json
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.134"

REQUIRED_PATHS = (
    "README.md",
    "AGENTS.md",
    "package.json",
    "bin/tes.js",
    "LICENSE",
    "NOTICE.md",
    ".github/CODE_OF_CONDUCT.md",
    ".github/CONTRIBUTING.md",
    "docs/INDEX.md",
    "docs/index.html",
    "docs/architecture/PROJECT-STRUCTURE.md",
    "docs/architecture/TES-NAMING-MIGRATION-CATALOG.md",
    "docs/adr/0001-tes-memory-lifecycle.md",
    "docs/install/USER-MANUAL.html",
    "docs/dist/0.3.134/index.json",
    "docs/dist/0.3.134/tilly-engineer-skills-0.3.134.zip",
    "docs/dist/0.3.134/tilly-engineer-skills-0.3.134.zip.sha256",
    "docs/install/MINI-PROMPT.md",
    "docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md",
    "docs/install/COMMAND-TRIGGERS.md",
    "docs/adapters/ADAPTER-CAPABILITY-MATRIX.md",
    "docs/adapters/PLATFORM-DIFFERENCES.md",
    "docs/install/navigation/NAVIGATION-LIBRARY.md",
    "docs/install/navigation/common.prompt.md",
    "docs/install/navigation/codex.prompt.md",
    "docs/install/navigation/codex-cli.prompt.md",
    "docs/install/navigation/claude-code.prompt.md",
    "docs/install/navigation/claude-desktop.prompt.md",
    "docs/install/navigation/cursor.prompt.md",
    "docs/install/navigation/cursor-acp.prompt.md",
    "docs/install/navigation/anthropic-api.prompt.md",
    "docs/install/navigation/generic.prompt.md",
    "docs/governance/AGENTIC-ALIGNMENT-GOVERNANCE.md",
    "docs/governance/MAINTAINER-CORRELATION-RULE.md",
    "docs/governance/SYNC-AUDIT-CHECKLIST.md",
    "docs/mesh/PRINCIPLES.md",
    "docs/mesh/CONTEXT-MESH-METHOD.md",
    "docs/mesh/TES-ALIGN-SKILL-SOURCE-OF-TRUTH.md",
    "docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md",
    "docs/mesh/CORTEX.md",
    "docs/mesh/SCOPE-CONTRACT.md",
    "docs/mesh/EVENT-LEDGER.md",
    "docs/mesh/CHECKPOINTS.md",
    "docs/mesh/CORTEX-MCP.md",
    "docs/mesh/FIELD-REPORTS.md",
    "docs/mesh/MANTRA-GATE.md",
    "docs/mesh/GIT-SAFETY.md",
    "docs/mesh/SCORECARD.md",
    "docs/roadmap/README.md",
    "docs/roadmap/RC1-READINESS-ROADMAP.md",
    "docs/evals/EVALS.md",
    "docs/evals/EXAMPLES.md",
    "docs/evidence/INDEX.md",
    "docs/evidence/current/INDEX.md",
    "docs/evidence/current/CLAIMS.md",
    "docs/evidence/current/RISKS.md",
    "docs/evidence/archive/INDEX.md",
    "docs/adapters/CODEX.md",
    "docs/adapters/CLAUDE.md",
    "docs/adapters/CURSOR.md",
    "docs/adapters/MATERIALIZATION.md",
    "docs/tds/DOCS-INDEX.yml",
    "docs/tds/TDS-SPEC.md",
    ".github/ISSUE_TEMPLATE/tes-field-report.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/SECURITY.md",
    ".github/SUPPORT.md",
    ".github/workflows/field-report-governance.yml",
    "src/adapters/codex/AGENTS.md",
    "src/adapters/codex/plugin/plugin.json",
    "src/adapters/codex/plugin/marketplace.json",
    "src/adapters/codex/skills/tes-engineering-discipline/SKILL.md",
    "src/adapters/codex/skills/tes-engineering-discipline/agents/openai.yaml",
    "src/adapters/codex/skills/tes-engineering-discipline/references/failure-patterns.md",
    "src/adapters/codex/skills/tes-engineering-discipline/references/source-portability.md",
    "src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py",
    "src/adapters/codex/skills/tes-init/SKILL.md",
    "src/adapters/codex/skills/tes-setup/SKILL.md",
    "src/adapters/codex/skills/tes-update/SKILL.md",
    "src/adapters/codex/skills/tes-align/SKILL.md",
    "src/adapters/codex/skills/tes-align/agents/openai.yaml",
    "src/adapters/codex/skills/tes-align/references/alignment-procedure.md",
    "src/adapters/codex/skills/tes-align/docs/CONTRACT-HISTORY.md",
    "src/adapters/codex/skills/tes-map/SKILL.md",
    "src/adapters/codex/skills/tes-goal-maestro/SKILL.md",
    "src/adapters/codex/skills/tes-goal-maestro/agents/openai.yaml",
    "src/adapters/codex/skills/tes-goal-maestro/references/maestral-goal-prompt.md",
    "src/adapters/codex/skills/tes-goal-maestro/references/materialization-tree.md",
    "src/adapters/codex/skills/tes-goal-maestro/references/quality-gates.md",
    "src/adapters/codex/skills/tes-goal-maestro/references/subagents-and-oracles.md",
    "src/adapters/codex/skills/tes-goal-maestro/docs/CONTRACT-HISTORY.md",
    "src/adapters/codex/skills/tes-prospect/SKILL.md",
    "src/adapters/codex/skills/tes-prospect/agents/openai.yaml",
    "src/adapters/codex/skills/tes-prospect/docs/CONTRACT-HISTORY.md",
    "src/adapters/codex/skills/tes-mine/SKILL.md",
    "src/adapters/codex/skills/tes-mine/agents/openai.yaml",
    "src/adapters/codex/skills/tes-mine/references/ADR-FORMAT.md",
    "src/adapters/codex/skills/tes-mine/references/CONTEXT-FORMAT.md",
    "src/adapters/codex/skills/tes-mine/docs/CONTRACT-HISTORY.md",
    "src/adapters/codex/skills/tes-open-obsidian/SKILL.md",
    "src/adapters/codex/skills/tes-open-obsidian/agents/openai.yaml",
    "src/adapters/codex/skills/tes-open-obsidian/docs/CONTRACT-HISTORY.md",
    "src/adapters/codex/skills/tes-cortex/SKILL.md",
    "src/adapters/codex/skills/tes-mcp/SKILL.md",
    "src/adapters/codex/skills/tes-field-reports/SKILL.md",
    "src/adapters/codex/skills/tes-field-reports/agents/openai.yaml",
    "src/adapters/codex/skills/tes-field-reports/docs/CONTRACT-HISTORY.md",
    "src/adapters/codex/skills/tes-doctor/SKILL.md",
    "src/adapters/codex/skills/tes-adapter/SKILL.md",
    "src/adapters/codex/skills/tes-bench/SKILL.md",
    "src/adapters/codex/skills/tes-bench/agents/openai.yaml",
    "src/adapters/codex/skills/tes-bench/docs/CONTRACT-HISTORY.md",
    "src/adapters/codex/skills/tes-bump/SKILL.md",
    "src/adapters/codex/skills/tes-bump/agents/openai.yaml",
    "src/adapters/codex/skills/tes-bump/docs/CONTRACT-HISTORY.md",
    "src/adapters/claude/CLAUDE.md",
    "src/adapters/claude/plugin/plugin.json",
    "src/adapters/claude/plugin/marketplace.json",
    "src/adapters/claude/skills/tes-guidelines/SKILL.md",
    "src/adapters/claude/skills/tes-init/SKILL.md",
    "src/adapters/claude/skills/tes-setup/SKILL.md",
    "src/adapters/claude/skills/tes-update/SKILL.md",
    "src/adapters/claude/skills/tes-align/SKILL.md",
    "src/adapters/claude/skills/tes-align/agents/openai.yaml",
    "src/adapters/claude/skills/tes-align/references/alignment-procedure.md",
    "src/adapters/claude/skills/tes-align/docs/CONTRACT-HISTORY.md",
    "src/adapters/claude/skills/tes-map/SKILL.md",
    "src/adapters/claude/skills/tes-goal-maestro/SKILL.md",
    "src/adapters/claude/skills/tes-goal-maestro/agents/openai.yaml",
    "src/adapters/claude/skills/tes-goal-maestro/references/maestral-goal-prompt.md",
    "src/adapters/claude/skills/tes-goal-maestro/references/materialization-tree.md",
    "src/adapters/claude/skills/tes-goal-maestro/references/quality-gates.md",
    "src/adapters/claude/skills/tes-goal-maestro/references/subagents-and-oracles.md",
    "src/adapters/claude/skills/tes-goal-maestro/docs/CONTRACT-HISTORY.md",
    "src/adapters/claude/skills/tes-prospect/SKILL.md",
    "src/adapters/claude/skills/tes-prospect/agents/openai.yaml",
    "src/adapters/claude/skills/tes-prospect/docs/CONTRACT-HISTORY.md",
    "src/adapters/claude/skills/tes-mine/SKILL.md",
    "src/adapters/claude/skills/tes-mine/agents/openai.yaml",
    "src/adapters/claude/skills/tes-mine/references/ADR-FORMAT.md",
    "src/adapters/claude/skills/tes-mine/references/CONTEXT-FORMAT.md",
    "src/adapters/claude/skills/tes-mine/docs/CONTRACT-HISTORY.md",
    "src/adapters/claude/skills/tes-open-obsidian/SKILL.md",
    "src/adapters/claude/skills/tes-open-obsidian/agents/openai.yaml",
    "src/adapters/claude/skills/tes-open-obsidian/docs/CONTRACT-HISTORY.md",
    "src/adapters/claude/skills/tes-cortex/SKILL.md",
    "src/adapters/claude/skills/tes-mcp/SKILL.md",
    "src/adapters/claude/skills/tes-field-reports/SKILL.md",
    "src/adapters/claude/skills/tes-field-reports/agents/openai.yaml",
    "src/adapters/claude/skills/tes-field-reports/docs/CONTRACT-HISTORY.md",
    "src/adapters/claude/skills/tes-doctor/SKILL.md",
    "src/adapters/claude/skills/tes-adapter/SKILL.md",
    "src/adapters/claude/skills/tes-bench/SKILL.md",
    "src/adapters/claude/skills/tes-bench/agents/openai.yaml",
    "src/adapters/claude/skills/tes-bench/docs/CONTRACT-HISTORY.md",
    "src/adapters/claude/skills/tes-bump/SKILL.md",
    "src/adapters/claude/skills/tes-bump/agents/openai.yaml",
    "src/adapters/claude/skills/tes-bump/docs/CONTRACT-HISTORY.md",
    "src/adapters/cursor/CURSOR.md",
    "src/adapters/cursor/rules/tes-guidelines.mdc",
    "src/adapters/cursor/rules/tes-runtime-capabilities.mdc",
    "benchmarks/context-mesh/eval-dataset.json",
    "scripts/context_mesh_plan.py",
    "scripts/context_mesh_run.py",
    "scripts/cortex.py",
    "scripts/cortex_embed.mjs",
    "scripts/cortex_mcp.py",
    "scripts/cortex_operator_oracle.py",
    "scripts/cortex_quality_oracle.py",
    "scripts/scope_contract.py",
    "scripts/event_ledger.py",
    "scripts/checkpoint.py",
    "scripts/consolidation_gate.py",
    "scripts/field_reports.py",
    "scripts/field_reports_github_oracle.py",
    "scripts/field_reports_quality_oracle.py",
    "scripts/mantra_gate.py",
    "scripts/mantra_gate_adoption_oracle.py",
    "scripts/github_readiness_oracle.py",
    "scripts/tes_install.py",
    "scripts/tes_npx_oracle.py",
    "scripts/tes_bundle.py",
    "scripts/public_bundle_oracle.py",
    "scripts/install_smoke.py",
    "scripts/install_mcp.py",
    "scripts/install_adapter.py",
    "scripts/tes_init.py",
    "scripts/project_context_oracle.py",
    "scripts/private_vocabulary_oracle.py",
    "scripts/project_alignment_oracle.py",
    "scripts/tes_map.py",
    "scripts/tes_map_oracle.py",
    "scripts/tes_open_obsidian.py",
    "scripts/tes_bump.py",
    "scripts/tes_update.py",
    "scripts/tes_legacy_retirement.py",
    "scripts/tes_namespace.py",
    "scripts/root_context.py",
    "scripts/codex_plugin_oracle.py",
    "scripts/claude_plugin_oracle.py",
    "scripts/platform_surface_oracle.py",
    "scripts/command_trigger_oracle.py",
    "scripts/retention_metadata.py",
    "scripts/validate_reference_graph.py",
    "scripts/validate_doc_size.py",
    "scripts/adapter_parity_readiness.py",
    "scripts/bootstrap/install.ps1",
    "scripts/bootstrap/install.sh",
    "scripts/materialize_adapter.py",
    "scripts/validate_tds.py",
    ".githooks/pre-commit",
    ".githooks/pre-push",
)

REQUIRED_TERMS = (
    "Think Before Coding",
    "Simplicity First",
    "Surgical Changes",
    "Goal-Driven Execution",
    "E = A * S * C * V",
)

SYNCED_FILES = (
    "AGENTS.md",
    "docs/mesh/PRINCIPLES.md",
    "src/adapters/codex/AGENTS.md",
    "src/adapters/claude/CLAUDE.md",
    "src/adapters/cursor/rules/tes-guidelines.mdc",
    "src/adapters/claude/skills/tes-guidelines/SKILL.md",
    "src/adapters/codex/skills/tes-engineering-discipline/SKILL.md",
)

FORBIDDEN_ROOT_PATHS = (
    ".claude-plugin",
    ".cursor",
    "skills",
    "CLAUDE.md",
    "CODEX.md",
    "CURSOR.md",
    "install.ps1",
    "install.sh",
    "PRINCIPLES.md",
    "METHOD.md",
    "EVALS.md",
    "EXAMPLES.md",
    "SCORECARD.md",
    "CHANGELOG.md",
)

GENERATED_ADAPTER_OUTPUT = ROOT / "dist" / "adapters"

LOCAL_DEVELOPMENT_SKILL_PARITY = (
    "tes-high-agency-pattern",
    "tes-predictive-operations",
    "tes-sync",
)

LOCAL_DEVELOPMENT_SKILL_DESCRIPTION_TERMS = {
    "tes-high-agency-pattern": (
        "Local-only self-consumed",
        "one local development-layer skill/workflow operating pattern",
        "agency",
        "question budget",
        "verbosity",
        "evidence posture",
        "output shape",
        "packaging discipline",
        "Prefer tes-predictive-operations",
        "prospect/mine/alternate/package modes",
        "Do not present as user-invoked",
    ),
    "tes-predictive-operations": (
        "Local-only self-consumed",
        "next reasoning mode during active project work",
        "prospect, mine, alternate, or package",
        "planning pressure",
        "evidence mining",
        "packaging timing",
        "Prefer tes-high-agency-pattern",
        "one local development-layer skill/workflow operating pattern",
        "Do not present as user-invoked",
    ),
    "tes-sync": (
        "Local-only self-consumed",
        "complete sync routine on the TES source package",
        "identity bump",
        "public bundle",
        "validate, commit, push, tag, release certification",
        "sync completo",
        "/tes-sync",
        "Do not present as a user-facing TES product skill",
    ),
}

REQUIRED_PACKAGE_SCRIPTS = (
    "validate",
    "install:adapter",
    "install:dry-run",
    "install:smoke",
    "tes:bundle:self-test",
    "tes:bundle:publish",
    "tes:bundle:public-oracle",
    "tes:init",
    "tes:init:self-test",
    "tes:install",
    "tes:install:self-test",
    "tes:npx:self-test",
    "tes:npx:github-self-test",
    "project-context:self-test",
    "project-alignment:self-test",
    "tes-open-obsidian:self-test",
    "tes:update",
    "tes:update:self-test",
    "tes:legacy:plan",
    "tes:legacy:apply",
    "tes:legacy:audit",
    "tes:legacy:self-test",
    "tes:namespace:report",
    "tes:namespace:audit",
    "tes:namespace:inventory",
    "tes:namespace:self-test",
    "root-context:check",
    "root-context:self-test",
    "scope:contract:self-test",
    "event-ledger:self-test",
    "checkpoint:self-test",
    "consolidation:lock",
    "consolidation:certify",
    "consolidation:self-test",
    "mcp:install",
    "mcp:dry-run",
    "mcp:self-test",
    "field-reports:self-test",
    "field-reports:quality:self-test",
    "field-reports:github-oracle",
    "mantra-gate:self-test",
    "mantra-gate:adoption:self-test",
    "github:readiness:self-test",
    "field-reports:status",
    "field-reports:drain",
    "codex:plugin:oracle",
    "claude:plugin:oracle",
    "materialize:all",
    "materialize:codex",
    "materialize:cursor",
    "materialize:claude",
    "materialize:check",
    "tds:validate",
    "cortex:init",
    "cortex:verify",
    "cortex:audit",
    "cortex:rebuild",
    "cortex:curate-plan",
    "cortex:recall",
    "cortex:read-cell",
    "cortex:absorb-plan",
    "cortex:learn",
    "cortex:reflect",
    "cortex:apply",
    "cortex:health",
    "cortex:peek",
    "cortex:review",
    "cortex:checkpoint",
    "cortex:remember",
    "cortex:forget",
    "cortex:self-test",
    "cortex:operator:self-test",
    "cortex:quality:self-test",
    "cortex:mcp:self-test",
    "oracle:self-test",
    "benchmark:plan",
    "benchmark:run",
    "commit:check",
    "adapter:parity:check",
    "platform:surface:check",
    "command-triggers:self-test",
    "retention:check",
    "reference:graph",
    "docs:size",
    "private-vocabulary:self-test",
    "private-vocabulary:check",
)

MAINTAINER_CORRELATION_REQUIRED_TERMS = (
    "This rule governs agents developing the Tilly Engineer Skills package.",
    "installed project rule",
    "`scripts/**` is not a layer by itself.",
    "A validator-only change is maintainer layer.",
    "If a change alters behavior observed by adopters or installing agents",
    "If a change touches both layers, state both impacts separately",
    "If the layer cannot be classified in one sentence, stop with `NEEDS_REVIEW`",
    "Do not update `src/**` merely to teach agents how to maintain this repository.",
    "Do not update the user manual with maintainer-only coordination rules.",
)

MAINTAINER_CORRELATION_FORBIDDEN_TERMS = (
    "user-facing behavior belongs in `docs/install/**`, `src/adapters/**`, scripts,",
)

AGENTS_BOOTLOADER_REQUIRED_TERMS = (
    "Repository bootloader for the independent Tilly Engineer Skills reference",
    "Classify `scripts/**` by consumer",
    "Maintainer correlation rule",
    "Closure gate",
    "`npm run commit:check`",
    "This file governs agents working on the Tilly Engineer Skills package itself.",
    "It is not an installed target-project rule.",
)

AGENTS_BOOTLOADER_FORBIDDEN_TERMS = (
    "Treat `src/**` as source, `docs/**` as explanation, and scripts as gates.",
)

PROJECT_STRUCTURE_REQUIRED_TERMS = (
    "| `AGENTS.md` | Thin repository bootloader for agents working here |",
    "| `scripts/**` | Deterministic oracles and package helpers |",
    "`scripts/**` is classified by consumer, not by directory.",
    "Validator-only",
    "scripts are maintainer gates.",
    "Installer, Cortex, MCP, Field Reports, and adapter",
    "delivered behavior",
)

PROJECT_STRUCTURE_FORBIDDEN_TERMS = (
    "| `scripts/**` | Deterministic package checks |",
)

INSTALLER_REPORT_REQUIRED_TERMS = (
    "`source_package_commit`",
    "`source_remote_head`",
    "`source_freshness`",
    "`STALE_SOURCE`",
    "current public bundle",
    ".tes/setup/",
    "target-local Git exclude",
    "snapshot certification",
    "full changed-file inventory",
    "`git status --short --untracked-files=all`",
    "short factual prose",
    "Do not use Markdown tables unless",
    "Updated existing mesh files",
    "Clean backup",
    "Installed helper set",
    "Field Reports: PASS | BLOCKED | DISABLED | SKIP",
    "outbox pending count",
    "`/tes-update` routine",
    "Rollback",
    "Summary: reset baseline plus clean installer-created files",
)

USER_MANUAL_REPORT_REQUIRED_TERMS = (
    "source snapshot freshness",
    "STALE_SOURCE",
    "Current public bundles",
    ".tes/setup/&lt;version&gt;/",
    "certified against the recorded snapshot",
    "frescor do snapshot fonte",
    "certificado contra o snapshot registrado",
    "installed helper set",
    "Field Reports state",
    "helper set instalado",
    "estado do Field Reports",
    "rollback summary",
    "resumo de rollback",
    "root context gate",
    "gate de contexto raiz",
    "RECOVERED",
    ".tes/bk/&lt;timestamp&gt;",
    "backup",
    "semântica útil",
)

UPDATE_ROUTINE_REQUIRED_TERMS = (
    "/tes-update",
    "/tes:update",
    "tes_update.py",
    "installed and cloud versions",
    "helper contract parity",
    "helper-only Layer Zero",
    "--record-field-report",
    "recommended_update_scope",
    "adapter-config",
    "post-Layer Zero",
    "helper_contract_status=PASS",
    "runtime_trigger_status",
    "update_available=False",
    "recommended_update_scope=none",
    "final Field Reports `tes_update` event",
    "STALE_HELPERS",
    "versão instalada e versão na nuvem",
    "paridade de contrato dos helpers",
    "recommended_route",
    "self_test_mode",
    "legacy_retirement_required",
)

ROOT_CONTEXT_REQUIRED_TERMS = (
    "root_context.py",
    "Root context gate",
    "AGENTS.md",
    "CLAUDE.md",
    ".cursor/rules/**",
    "docs/agents/**",
    "RECOVERED",
    "self_test_mode",
)

INIT_CONTEXT_REQUIRED_TERMS = (
    "PROJECT-CONTEXT.md",
    "Maximum-Depth Initialization Contract",
    "write_project_context",
    "project context",
    "Recommended Deep Reads",
)

GIT_SAFETY_REQUIRED_TERMS = (
    ".tes/bin/*.bak-*",
    ".tes/bin/__pycache__/",
    "*.pyc",
    ".tes/field-reports/",
    ".tes/legacy-retirement/",
    ".tes/cortex/*.sqlite",
    "must not ignore `.tes/bin/*.py`",
)

CANONICAL_USER_MANUAL_WEB_URL = "https://murillodutt.github.io/tilly-engineer-skills/install/USER-MANUAL.html"
FORBIDDEN_USER_MANUAL_WEB_URL = "https://github.com/murillodutt/tilly-engineer-skills/blob/main/docs/install/USER-MANUAL.html"

VERSION_LOCKED_SURFACES = (
    "README.md",
    "docs/adapters/CODEX.md",
    "docs/install/USER-MANUAL.html",
    "docs/tds/DOCS-INDEX.yml",
    "src/adapters/codex/plugin/plugin.json",
    "src/adapters/codex/plugin/marketplace.json",
    "src/adapters/claude/plugin/plugin.json",
    "src/adapters/claude/plugin/marketplace.json",
)
SEMVER_RE = re.compile(r"\b0\.3\.\d+\b")


def package_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        text=False,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return [
            path.relative_to(ROOT)
            for path in ROOT.rglob("*")
            if path.is_file() and ".git" not in path.relative_to(ROOT).parts
        ]

    return [
        Path(raw.decode("utf-8"))
        for raw in result.stdout.split(b"\0")
        if raw
    ]


def git_path_list(*args: str) -> set[Path]:
    result = subprocess.run(
        ["git", *args, "-z"],
        cwd=ROOT,
        text=False,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return set()
    return {
        Path(raw.decode("utf-8"))
        for raw in result.stdout.split(b"\0")
        if raw
    }


def staged_ready_failures() -> list[str]:
    failures: list[str] = []
    indexed = git_path_list("ls-files", "--cached")
    untracked = git_path_list("ls-files", "--others", "--exclude-standard")

    for path in sorted(untracked):
        failures.append(f"untracked package path before commit: {path}")

    for relpath in REQUIRED_PATHS:
        path = Path(relpath)
        if path not in indexed:
            failures.append(f"required path is not staged/tracked: {relpath}")

    return failures


def generated_adapter_output_failures() -> list[str]:
    if not GENERATED_ADAPTER_OUTPUT.exists():
        return []
    return [
        "generated adapter output must not remain in the source package: "
        "purge dist/adapters after inspection; src/adapters is the only "
        "local canonical adapter source"
    ]


def local_development_skill_parity_failures() -> list[str]:
    failures: list[str] = []
    for skill in LOCAL_DEVELOPMENT_SKILL_PARITY:
        codex_root = ROOT / ".agents" / "skills" / skill
        claude_root = ROOT / ".claude" / "skills" / skill
        if not codex_root.is_dir():
            failures.append(f"missing Codex development skill: {codex_root.relative_to(ROOT)}")
            continue
        if not claude_root.is_dir():
            failures.append(f"missing Claude development skill: {claude_root.relative_to(ROOT)}")
            continue

        codex_files = {
            path.relative_to(codex_root): path
            for path in codex_root.rglob("*")
            if path.is_file() and path.name != ".DS_Store"
        }
        claude_files = {
            path.relative_to(claude_root): path
            for path in claude_root.rglob("*")
            if path.is_file() and path.name != ".DS_Store"
        }

        for relpath in sorted(codex_files.keys() - claude_files.keys()):
            failures.append(f"{skill}: missing Claude parity file: {relpath}")
        for relpath in sorted(claude_files.keys() - codex_files.keys()):
            failures.append(f"{skill}: missing Codex parity file: {relpath}")
        for relpath in sorted(codex_files.keys() & claude_files.keys()):
            if codex_files[relpath].read_bytes() != claude_files[relpath].read_bytes():
                failures.append(f"{skill}: Codex/Claude development skill drift: {relpath}")

    return failures


def skill_frontmatter_description(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    frontmatter = text.split("---\n", 2)[1]
    for line in frontmatter.splitlines():
        if line.startswith("description: "):
            return line.removeprefix("description: ").strip()
    return None


def local_development_skill_description_failures() -> list[str]:
    failures: list[str] = []
    roots = (
        ("Codex", ROOT / ".agents" / "skills"),
        ("Claude", ROOT / ".claude" / "skills"),
    )
    for label, skills_root in roots:
        for skill, required_terms in LOCAL_DEVELOPMENT_SKILL_DESCRIPTION_TERMS.items():
            path = skills_root / skill / "SKILL.md"
            if not path.exists():
                continue
            description = skill_frontmatter_description(path)
            if description is None:
                failures.append(f"{label} {skill}: missing frontmatter description")
                continue
            for term in required_terms:
                if term not in description:
                    failures.append(f"{label} {skill}: description missing trigger term: {term}")
    return failures


def maintainer_correlation_failures() -> list[str]:
    path = ROOT / "docs/governance/MAINTAINER-CORRELATION-RULE.md"
    if not path.exists():
        return ["missing maintainer correlation rule"]

    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for term in MAINTAINER_CORRELATION_REQUIRED_TERMS:
        if term not in text:
            failures.append(f"maintainer correlation rule missing term: {term}")
    for term in MAINTAINER_CORRELATION_FORBIDDEN_TERMS:
        if term in text:
            failures.append(f"maintainer correlation rule contains ambiguous term: {term}")
    return failures


def agents_bootloader_failures() -> list[str]:
    path = ROOT / "AGENTS.md"
    if not path.exists():
        return ["missing AGENTS.md"]

    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for term in AGENTS_BOOTLOADER_REQUIRED_TERMS:
        if term not in text:
            failures.append(f"AGENTS.md missing alignment term: {term}")
    for term in AGENTS_BOOTLOADER_FORBIDDEN_TERMS:
        if term in text:
            failures.append(f"AGENTS.md contains ambiguous term: {term}")
    return failures


def project_structure_failures() -> list[str]:
    path = ROOT / "docs/architecture/PROJECT-STRUCTURE.md"
    if not path.exists():
        return ["missing project structure document"]

    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for term in PROJECT_STRUCTURE_REQUIRED_TERMS:
        if term not in text:
            failures.append(f"project structure missing alignment term: {term}")
    for term in PROJECT_STRUCTURE_FORBIDDEN_TERMS:
        if term in text:
            failures.append(f"project structure contains ambiguous term: {term}")
    return failures


def installer_report_contract_failures() -> list[str]:
    failures: list[str] = []
    installer = ROOT / "docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md"
    if not installer.exists():
        return ["missing assisted installer prompt"]
    installer_text = installer.read_text(encoding="utf-8")
    for term in INSTALLER_REPORT_REQUIRED_TERMS:
        if term not in installer_text:
            failures.append(f"assisted installer missing report-hardening term: {term}")
    manual_link_sources = {
        "docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md": installer_text,
        "docs/install/INSTALL.md": (ROOT / "docs/install/INSTALL.md").read_text(encoding="utf-8"),
    }
    for relpath, text in manual_link_sources.items():
        if FORBIDDEN_USER_MANUAL_WEB_URL in text:
            failures.append(f"{relpath} points user manual web link at GitHub blob URL")
        if CANONICAL_USER_MANUAL_WEB_URL not in text:
            failures.append(f"{relpath} missing canonical GitHub Pages user manual URL")

    manual = ROOT / "docs/install/USER-MANUAL.html"
    if not manual.exists():
        return [*failures, "missing user manual"]
    manual_text = manual.read_text(encoding="utf-8")
    for term in USER_MANUAL_REPORT_REQUIRED_TERMS:
        if term not in manual_text:
            failures.append(f"user manual missing report-hardening term: {term}")
    update_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            ROOT / "docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md",
            ROOT / "docs/install/COMMAND-TRIGGERS.md",
            ROOT / "docs/install/USER-MANUAL.html",
            ROOT / "scripts/tes_update.py",
        )
        if path.exists()
    )
    for term in UPDATE_ROUTINE_REQUIRED_TERMS:
        if term not in update_sources:
            failures.append(f"update routine missing term: {term}")
    root_context_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            ROOT / "docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md",
            ROOT / "docs/install/COMMAND-TRIGGERS.md",
            ROOT / "docs/install/USER-MANUAL.html",
            ROOT / "scripts/root_context.py",
        )
        if path.exists()
    )
    for term in ROOT_CONTEXT_REQUIRED_TERMS:
        if term not in root_context_sources:
            failures.append(f"root context gate missing term: {term}")
    init_context_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            ROOT / "docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md",
            ROOT / "docs/install/COMMAND-TRIGGERS.md",
            ROOT / "docs/install/INSTALL.md",
            ROOT / "docs/install/USER-MANUAL.html",
            ROOT / "scripts/tes_init.py",
            ROOT / "src/adapters/codex/skills/tes-init/SKILL.md",
            ROOT / "src/adapters/claude/skills/tes-init/SKILL.md",
            ROOT / "src/adapters/cursor/rules/tes-guidelines.mdc",
        )
        if path.exists()
    )
    for term in INIT_CONTEXT_REQUIRED_TERMS:
        if term not in init_context_sources:
            failures.append(f"init project context missing term: {term}")
    git_safety_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            ROOT / "docs/mesh/GIT-SAFETY.md",
            ROOT / "scripts/field_reports.py",
            ROOT / "docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md",
            ROOT / "docs/install/USER-MANUAL.html",
        )
        if path.exists()
    )
    for term in GIT_SAFETY_REQUIRED_TERMS:
        if term not in git_safety_sources:
            failures.append(f"Git safety contract missing term: {term}")
    return failures


def version_drift_failures() -> list[str]:
    failures: list[str] = []
    for relpath in VERSION_LOCKED_SURFACES:
        path = ROOT / relpath
        if not path.exists():
            continue
        versions = sorted(set(SEMVER_RE.findall(path.read_text(encoding="utf-8"))))
        stale = [version for version in versions if version != VERSION]
        for version in stale:
            failures.append(f"{relpath} contains stale package version {version}; expected {VERSION}")
    return failures


def yaml_surface_failures() -> list[str]:
    try:
        import yaml  # type: ignore[import-untyped]
    except Exception as exc:  # pragma: no cover - depends on maintainer env
        return [f"PyYAML is required to validate delivered YAML surfaces: {exc}"]

    failures: list[str] = []
    yaml_paths = sorted(
        path for path in package_paths()
        if path.suffix in {".yaml", ".yml"}
        and "docs/evidence" not in path.parts
    )
    for relpath in yaml_paths:
        path = ROOT / relpath
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"invalid YAML surface: {relpath}: {type(exc).__name__}: {exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged-ready", action="store_true")
    args = parser.parse_args()

    failures: list[str] = []

    for relpath in REQUIRED_PATHS:
        if not (ROOT / relpath).exists():
            failures.append(f"missing required path: {relpath}")

    for relpath in FORBIDDEN_ROOT_PATHS:
        if (ROOT / relpath).exists():
            failures.append(f"source leaked back into root: {relpath}")

    for path in package_paths():
        if path.name == ".DS_Store":
            failures.append(f"package artifact present: {path}")
        if path.name == "CHANGELOG.md":
            failures.append(f"changelog must remain in Git history, not a file: {path}")
        if path.name == ".cursorrules":
            failures.append(f"legacy Cursor rules file is forbidden: {path}")

    if args.staged_ready:
        failures.extend(staged_ready_failures())

    failures.extend(maintainer_correlation_failures())
    failures.extend(agents_bootloader_failures())
    failures.extend(project_structure_failures())
    failures.extend(installer_report_contract_failures())
    failures.extend(version_drift_failures())
    failures.extend(yaml_surface_failures())
    failures.extend(generated_adapter_output_failures())
    failures.extend(local_development_skill_parity_failures())
    failures.extend(local_development_skill_description_failures())

    for relpath in SYNCED_FILES:
        path = ROOT / relpath
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for term in REQUIRED_TERMS:
            if term not in text:
                failures.append(f"{relpath} missing term: {term}")

    package_json = ROOT / "package.json"
    if package_json.exists():
        package = json.loads(package_json.read_text(encoding="utf-8"))
        if package.get("version") != VERSION:
            failures.append(f"package.json version must be {VERSION}")
        bin_field = package.get("bin")
        if not isinstance(bin_field, dict):
            failures.append("package.json must declare bin object")
        elif bin_field.get("tilly-engineer-skills") != "./bin/tes.js":
            failures.append("package.json bin.tilly-engineer-skills must be ./bin/tes.js")
        scripts = package.get("scripts", {})
        for script in REQUIRED_PACKAGE_SCRIPTS:
            if script not in scripts:
                failures.append(f"package.json missing script: {script}")

    for relpath in (
        "src/adapters/codex/plugin/plugin.json",
        "src/adapters/codex/plugin/marketplace.json",
        "src/adapters/claude/plugin/plugin.json",
        "src/adapters/claude/plugin/marketplace.json",
    ):
        path = ROOT / relpath
        if path.exists() and VERSION not in path.read_text(encoding="utf-8"):
            failures.append(f"{relpath} must declare {VERSION}")

    oracle = ROOT / "src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py"
    if oracle.exists():
        result = subprocess.run(
            [sys.executable, str(oracle), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("discipline_oracle.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    plan = ROOT / "scripts/context_mesh_plan.py"
    if plan.exists():
        result = subprocess.run(
            [sys.executable, str(plan)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("context_mesh_plan.py failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    cortex = ROOT / "scripts/cortex.py"
    if cortex.exists():
        result = subprocess.run(
            [sys.executable, str(cortex), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("cortex.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    cortex_mcp = ROOT / "scripts/cortex_mcp.py"
    if cortex_mcp.exists():
        result = subprocess.run(
            [sys.executable, str(cortex_mcp), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("cortex_mcp.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    cortex_quality = ROOT / "scripts/cortex_quality_oracle.py"
    if cortex_quality.exists():
        result = subprocess.run(
            [sys.executable, str(cortex_quality), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("cortex_quality_oracle.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    field_reports = ROOT / "scripts/field_reports.py"
    if field_reports.exists():
        result = subprocess.run(
            [sys.executable, str(field_reports), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("field_reports.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    field_reports_quality = ROOT / "scripts/field_reports_quality_oracle.py"
    if field_reports_quality.exists():
        result = subprocess.run(
            [sys.executable, str(field_reports_quality), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("field_reports_quality_oracle.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    field_reports_github = ROOT / "scripts/field_reports_github_oracle.py"
    if field_reports_github.exists():
        result = subprocess.run(
            [sys.executable, str(field_reports_github), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("field_reports_github_oracle.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    mantra_gate = ROOT / "scripts/mantra_gate.py"
    if mantra_gate.exists():
        result = subprocess.run(
            [sys.executable, str(mantra_gate), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("mantra_gate.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    mantra_gate_adoption = ROOT / "scripts/mantra_gate_adoption_oracle.py"
    if mantra_gate_adoption.exists():
        result = subprocess.run(
            [sys.executable, str(mantra_gate_adoption), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("mantra_gate_adoption_oracle.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    root_context = ROOT / "scripts/root_context.py"
    if root_context.exists():
        result = subprocess.run(
            [sys.executable, str(root_context), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("root_context.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    mcp_installer = ROOT / "scripts/install_mcp.py"
    if mcp_installer.exists():
        result = subprocess.run(
            [sys.executable, str(mcp_installer), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("install_mcp.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    legacy_retirement = ROOT / "scripts/tes_legacy_retirement.py"
    if legacy_retirement.exists():
        result = subprocess.run(
            [sys.executable, str(legacy_retirement), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("tes_legacy_retirement.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    install_smoke = ROOT / "scripts/install_smoke.py"
    if install_smoke.exists():
        result = subprocess.run(
            [sys.executable, str(install_smoke), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("install_smoke.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    project_context = ROOT / "scripts/project_context_oracle.py"
    if project_context.exists():
        result = subprocess.run(
            [sys.executable, str(project_context), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("project_context_oracle.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    codex_oracle = ROOT / "scripts/codex_plugin_oracle.py"
    if codex_oracle.exists():
        result = subprocess.run(
            [sys.executable, str(codex_oracle), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("codex_plugin_oracle.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    claude_oracle = ROOT / "scripts/claude_plugin_oracle.py"
    if claude_oracle.exists():
        result = subprocess.run(
            [sys.executable, str(claude_oracle), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("claude_plugin_oracle.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    command_trigger_oracle = ROOT / "scripts/command_trigger_oracle.py"
    if command_trigger_oracle.exists():
        result = subprocess.run(
            [sys.executable, str(command_trigger_oracle), "--self-test"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("command_trigger_oracle.py --self-test failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    retention = ROOT / "scripts/retention_metadata.py"
    if retention.exists():
        result = subprocess.run(
            [sys.executable, str(retention), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("retention_metadata.py --check failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    reference_graph = ROOT / "scripts/validate_reference_graph.py"
    if reference_graph.exists():
        result = subprocess.run(
            [sys.executable, str(reference_graph)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("validate_reference_graph.py failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    doc_size = ROOT / "scripts/validate_doc_size.py"
    if doc_size.exists():
        result = subprocess.run(
            [sys.executable, str(doc_size)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("validate_doc_size.py failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    materializer = ROOT / "scripts/materialize_adapter.py"
    if materializer.exists():
        result = subprocess.run(
            [sys.executable, str(materializer), "all", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("materialize_adapter.py all --check failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    adapter_parity = ROOT / "scripts/adapter_parity_readiness.py"
    if adapter_parity.exists():
        result = subprocess.run(
            [sys.executable, str(adapter_parity)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("adapter_parity_readiness.py failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    tds_validator = ROOT / "scripts/validate_tds.py"
    if tds_validator.exists():
        result = subprocess.run(
            [sys.executable, str(tds_validator)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append("validate_tds.py failed")
            failures.extend(result.stdout.splitlines())
            failures.extend(result.stderr.splitlines())

    if failures:
        print("[tes-reference] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("[tes-reference] PASS")
    print(f"root={ROOT}")
    print(f"checked_files={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
