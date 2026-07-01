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
VERSION = "0.3.241"

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
    "--recover-needs-review",
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
        "MCP Fallback",
        "python3 .tes/bin/install_mcp.py --target . --adapter all --overwrite --yes",
        "config_registrations",
        "host recognition",
        "codex mcp list",
        "session_restart_required",
        "Do not edit global MCP config",
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
        "src/adapters/codex/skills/tes-context-distill/SKILL.md",
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
        "src/adapters/claude/skills/tes-engineering-discipline/SKILL.md",
        "src/adapters/claude/skills/tes-init/SKILL.md",
        "src/adapters/claude/skills/tes-setup/SKILL.md",
        "src/adapters/claude/skills/tes-context-distill/SKILL.md",
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
        "src/adapters/cursor/rules/tes-engineering-discipline.mdc",
        "src/adapters/cursor/rules/tes-runtime-capabilities.mdc",
    ),
}

# Lazy surfaces own the full init-router protocol (the dense 8 terms). The
# always-on bootloaders only need a short init anchor + route to the lazy
# surface (bootloader-to-skill migration, three-layer contract): anchor in the
# bootloader, expansion in the lazy skill/rule, oracle proves both.
INIT_ROUTER_SOURCE_PATHS = (
    "docs/install/COMMAND-TRIGGERS.md",
    "docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md",
    "src/adapters/codex/skills/tes-init/SKILL.md",
    "src/adapters/claude/skills/tes-init/SKILL.md",
    "src/adapters/cursor/rules/tes-runtime-capabilities.mdc",
)

# Each always-on bootloader must carry a short init anchor that routes to its
# lazy init surface. It must NOT restate the full gate protocol (that is the
# dense detail the migration moved to the lazy layer).
INIT_ROUTER_BOOTLOADERS = (
    "src/adapters/codex/AGENTS.md",
    "src/adapters/claude/CLAUDE.md",
    "src/adapters/cursor/rules/tes-engineering-discipline.mdc",
)
INIT_ROUTER_ANCHOR_TERMS = ("/tes-init",)

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

GOAL_MAESTRO_LOOP_CONTRACT_PATHS = {
    "codex": (
        "src/adapters/codex/skills/tes-goal-maestro/SKILL.md",
        "src/adapters/codex/skills/tes-goal-maestro/references/execution-loop-runner.md",
        "src/adapters/codex/skills/tes-goal-maestro/references/quality-gates.md",
        "src/adapters/codex/skills/tes-goal-maestro/references/maestral-goal-prompt.md",
        "src/adapters/codex/skills/tes-goal-maestro/references/structural-method.md",
        "src/adapters/codex/skills/tes-goal-maestro/references/materialization-tree.md",
        "src/adapters/codex/skills/tes-goal-maestro/references/subagents-and-oracles.md",
        "src/adapters/codex/skills/tes-goal-maestro/templates/maestral-goal-prompt.template.md",
    ),
    "claude": (
        "src/adapters/claude/skills/tes-goal-maestro/SKILL.md",
        "src/adapters/claude/skills/tes-goal-maestro/references/execution-loop-runner.md",
        "src/adapters/claude/skills/tes-goal-maestro/references/quality-gates.md",
        "src/adapters/claude/skills/tes-goal-maestro/references/maestral-goal-prompt.md",
        "src/adapters/claude/skills/tes-goal-maestro/references/structural-method.md",
        "src/adapters/claude/skills/tes-goal-maestro/references/materialization-tree.md",
        "src/adapters/claude/skills/tes-goal-maestro/references/subagents-and-oracles.md",
        "src/adapters/claude/skills/tes-goal-maestro/templates/maestral-goal-prompt.template.md",
    ),
}

GOAL_MAESTRO_LOOP_TERMS = (
    "--execute-loop",
    "--execute-loop-parent-fallback",
    "takes precedence",
    "strict sequential replay",
    "baseline-only comparison",
    "reference implementation",
    "loop-state block",
    "baseline worktree",
    "canonical SPEC artifact",
    "Pre-Edit Gate",
    "EXECUTE_LOOP_REQUESTED=",
    "READY_GOAL_PROMPT=present",
    "FIRST_UNEXECUTED_UNIT",
    "BASELINE_ONLY_COMMITS",
    "MAY_EDIT=yes",
    "Super SPEC materialization",
    "Engineering Method Profile",
    "STRUCTURAL_METHOD=",
    "structural source probes",
    "structural handoff",
    "bug_vs_architecture",
    "structural_repair",
    "Cloud Query Redaction Block",
    "Failed Attempt Recovery",
    "GOAL-EXECUTION-LOOP-LEDGER",
    "owner approval",
    "bounded audit",
    "NEEDS_MORE_LOOPS",
    "NEEDS_OWNER_DECISION",
    "SAFETY_BLOCKED",
    "NEEDS_STRUCTURAL_METHOD",
)

GOAL_MAESTRO_LEDGER_FIELDS = (
    "spec_id:",
    "spec_version:",
    "attempt:",
    "repair_count:",
    "audit_repair_cycle:",
    "first_unexecuted_unit:",
    "failed_attempt_recovery_decision:",
    "commit:",
    "oracle_status:",
    "structural_method_id:",
    "topology_decision:",
    "structural_debt:",
    "next_structural_constraint:",
    "stop_state:",
    "next_allowed_action:",
)

GOAL_MAESTRO_LEDGER_FORBIDDEN_PATTERNS = (
    r"full prompt\s*:",
    r"raw diff\s*:",
    r"secret\s*:",
    r"credential\s*:",
    r"private path\s*:",
    r"chat transcript\s*:",
)

GOAL_MAESTRO_EXECUTION_CREDIT_FORBIDDEN_PATTERNS = (
    r"reference (?:implementation|build|smoke|audit)[^\n]{0,120}(?:counts as|satisfies|certifies|validates|replaces)[^\n]{0,120}(?:loop|execution|ACTIVE_SPEC|SPEC)",
    r"(?:manual build|browser smoke|post-facto audit|run record)[^\n]{0,120}(?:counts as|satisfies|certifies|validates|replaces)[^\n]{0,120}(?:loop|execution|ACTIVE_SPEC|SPEC)",
)

GOAL_MAESTRO_LOOP_FILE_TERMS = {
        "SKILL.md": (
            "--execute-loop",
            "--execute-loop-parent-fallback",
            "Execution Cost Draft",
            "Pre-Edit Gate",
            "FIRST_UNEXECUTED_UNIT",
            "MAY_EDIT=yes",
            "Engineering Method Profile",
            "STRUCTURAL_METHOD=",
            "bug_vs_architecture",
        "NEEDS_STRUCTURAL_METHOD",
        "Failed Attempt Recovery",
        "Routing Realignment Mantra",
        "Load the owner before using owned behavior",
        "repair routing first",
        "Do not inline owned behavior",
        "GOAL-EXECUTION-LOOP-LEDGER",
        "strict sequential replay",
        "reference implementation",
        "Executive Stop Audit",
        "exact `--execute-loop-parent-fallback` flag",
    ),
        "references/execution-loop-runner.md": (
            "The parent runner owns the loop",
            "Reference Baseline Credit Gate",
            "Pre-Edit Gate",
            "EXECUTE_LOOP_REQUESTED=yes",
            "READY_GOAL_PROMPT=present",
            "FIRST_UNEXECUTED_UNIT",
            "BASELINE_ONLY_COMMITS",
            "MAY_EDIT=<yes|no>",
            "Super SPEC",
            "baseline-only comparison",
            "Engineering Method Profile",
            "STRUCTURAL_METHOD=",
            "bug_vs_architecture",
            "NEEDS_STRUCTURAL_METHOD",
            "SPEC-AUDIT-STRUCTURE",
            "strict sequential replay",
        "post-facto audit",
        "Failed Attempt Recovery",
        "Ledger Schema",
        "exact `--execute-loop-parent-fallback` flag",
        *GOAL_MAESTRO_LEDGER_FIELDS,
    ),
        "references/quality-gates.md": (
            "Execution Cost Draft",
            "Pre-Edit Gate",
            "FIRST_UNEXECUTED_UNIT",
            "MAY_EDIT=yes",
            "Engineering Method Profile",
            "STRUCTURAL_METHOD=",
            "structural handoff",
            "bug_vs_architecture",
            "NEEDS_STRUCTURAL_METHOD",
            "failed-attempt recovery",
        "persistent ledger",
        "strict sequential replay",
        "reference implementations",
        "exact `--execute-loop-parent-fallback` flag",
        "Executive Stop Audit",
    ),
        "references/maestral-goal-prompt.md": (
            "templates/maestral-goal-prompt.template.md",
            "Template Load Contract",
            "READY_GOAL_PROMPT",
            "Execution Loop:",
            "Pre-Edit Gate",
            "FIRST_UNEXECUTED_UNIT",
            "MAY_EDIT=yes",
            "Engineering Method Profile",
            "STRUCTURAL_METHOD=",
            "Structural method result",
            "Structural handoff",
            "bug_vs_architecture",
            "failed-attempt residue",
        "GOAL-EXECUTION-LOOP-LEDGER",
        "strict sequential replay",
        "reference implementations",
        "exact `--execute-loop-parent-fallback` flag",
        "Executive Stop Audit",
    ),
    "references/structural-method.md": (
        "Engineering Method Profile",
        "Method Enforcement Packet",
        "STRUCTURAL_METHOD=",
        "topology budget",
        "allowed modules/internal sections",
        "structural debt budget",
        "structural source probes",
        "structural handoff",
        "bug_vs_architecture",
        "structural_repair",
        "single-file exception",
        "SPEC-AUDIT-STRUCTURE",
        "GOAL-EXECUTION-LOOP-LEDGER",
    ),
        "references/materialization-tree.md": (
            "Execution Loop Boundary",
            "Pre-Edit Gate",
            "Structural Method Gate",
            "Engineering Method Profile",
            "STRUCTURAL_METHOD=",
            "structural handoff",
            "bug_vs_architecture",
            "failed-attempt recovery",
        "GOAL-EXECUTION-LOOP-LEDGER",
        "strict sequential replay",
        "reference implementations",
        "exact",
        "--execute-loop-parent-fallback",
    ),
    "references/subagents-and-oracles.md": (
        "one fresh worker subagent per `ACTIVE_SPEC`",
        "unresolved failed-attempt residue",
        "required persistent ledger",
        "strict sequential replay",
        "STRUCTURAL_METHOD=",
        "bug_vs_architecture",
        "Reference implementations",
        "exact `--execute-loop-parent-fallback` flag",
        "Executive Stop Audit",
    ),
    "templates/maestral-goal-prompt.template.md": (
        "/goal",
        "Main SPEC:",
        "SPEC-000 Preflight And Baseline",
        "Execution unit fidelity:",
        "git show --stat --oneline <commit>",
        "Sync status:",
        "Engineering Method Profile",
        "STRUCTURAL_METHOD=",
        "Structural method result:",
        "Structural handoff:",
        "Full Oracle And Closeout",
        "Stop criteria:",
        "Final delivery:",
        "Execution Loop:",
        "ACTIVE_SPEC",
        "Pre-Edit Gate",
        "FIRST_UNEXECUTED_UNIT",
        "MAY_EDIT=yes",
        "Failed Attempt Recovery",
        "GOAL-EXECUTION-LOOP-LEDGER",
        "bug_vs_architecture",
        "Executive Stop Audit",
    ),
}

GOAL_MAESTRO_MATURE_SPEC_REQUIRED_TERMS = (
    "Canonical Artifact:",
    "Capability:",
    "Certified Context:",
    "Phase Boundary:",
    "Non-Objectives:",
    "Central Rule:",
    "Forbidden Moves:",
    "Acceptance Criteria:",
    "Negative Grep:",
    "Stop States:",
    "Commit Strategy:",
    "Final Delivery Contract:",
)

GOAL_MAESTRO_GENERATED_PROMPT_REQUIRED_TERMS = (
    "/goal",
    "Main SPEC:",
    "SPEC-000 Preflight And Baseline",
    "Execution unit fidelity:",
    "git show --stat --oneline <commit>",
    "Sync status:",
    "Engineering Method Profile",
    "STRUCTURAL_METHOD=",
    "Structural method result:",
    "Structural handoff:",
    "Full Oracle And Closeout",
    "Stop criteria:",
    "Final delivery:",
)


CLAUDE_PROJECT_SKILLS = (
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
            "generate a maestral /goal prompt",
            "gerar um /goal maestral",
            "NEEDS_SPEC_MATURITY",
            "NEEDS_EXECUTION_UNIT_FIDELITY",
            "DRAFT_MATERIALIZATION_TREE",
            "NEEDS_TREE_ACCEPTANCE",
            "READY_GOAL_PROMPT",
            "NEEDS_STRUCTURAL_METHOD",
            "Engineering Method Profile",
            "Goal Maestro owns prompt enrichment",
            "next_prompt_handoff",
            "--next-prompt-handoff",
            "--execute-loop",
            "--execute-loop-parent-fallback",
            "--audit-heartbeat-prompt",
            "audit_heartbeat=true",
            "adversarial_audit_heartbeat: requested",
            "direct request to generate or create an adversarial audit heartbeat prompt",
            "copy-ready English heartbeat prompt",
            "same-response read-only sidecar",
            "second `/tes-goal-maestro` command",
            "not execution, scheduling, sharing, or Goal Maestro stop-state authority",
            "Execution Cost Draft",
            "Executive Stop Audit",
            "SPEC_REPAIR_BY_LLM",
            "NEEDS_MORE_LOOPS",
            "NEEDS_OWNER_DECISION",
            "SAFETY_BLOCKED",
            "EXECUTION_LOOP_COMPLETE",
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
            "generate a maestral /goal prompt",
            "gerar um /goal maestral",
            "NEEDS_SPEC_MATURITY",
            "NEEDS_EXECUTION_UNIT_FIDELITY",
            "DRAFT_MATERIALIZATION_TREE",
            "NEEDS_TREE_ACCEPTANCE",
            "READY_GOAL_PROMPT",
            "NEEDS_STRUCTURAL_METHOD",
            "Engineering Method Profile",
            "Goal Maestro owns prompt enrichment",
            "next_prompt_handoff",
            "--next-prompt-handoff",
            "--execute-loop",
            "--execute-loop-parent-fallback",
            "--audit-heartbeat-prompt",
            "audit_heartbeat=true",
            "adversarial_audit_heartbeat: requested",
            "direct request to generate or create an adversarial audit heartbeat prompt",
            "copy-ready English heartbeat prompt",
            "same-response read-only sidecar",
            "second `/tes-goal-maestro` command",
            "not execution, scheduling, sharing, or Goal Maestro stop-state authority",
            "Execution Cost Draft",
            "Executive Stop Audit",
            "SPEC_REPAIR_BY_LLM",
            "NEEDS_MORE_LOOPS",
            "NEEDS_OWNER_DECISION",
            "SAFETY_BLOCKED",
            "EXECUTION_LOOP_COMPLETE",
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

PRESSURE_CONTRACT_TERMS = (
    "one decision branch at a time",
    "exactly one next question",
    "exactly one recommended answer",
    "repository evidence can answer",
    "before asking the user",
    "cognitive brake",
)

PRESSURE_AGENT_TERMS = (
    "one decision branch at a time",
    "exactly one next question",
    "exactly one recommended answer",
    "repository evidence can answer",
)

PRESSURE_FIXTURE_DATASET = "benchmarks/pressure/eval-dataset.json"
PRESSURE_FIXTURE_REQUIRED_TERMS = (
    "several questions",
    "repository evidence",
    "one decision branch at a time",
    "exactly one next question",
    "exactly one recommended answer",
)
ROUTE_TARGET_RE = re.compile(r"/tes[-:][a-z-]+")
ROUTE_CASES = (
    {
        "id": "R1-map-intent-single-flow",
        "intents": ("tes map", "map this project", "mapear projeto"),
        "expected_route": "/tes-map",
        "forbidden_routes": ("/tes-align", "/tes-doctor"),
    },
)

GOAL_MAESTRO_OPTION_DOC_TERMS = {
    "docs/install/COMMAND-TRIGGERS.md": (
        "--execute-loop",
        "--audit-heartbeat-prompt",
        "audit_heartbeat=true",
        "adversarial_audit_heartbeat: requested",
        "direct request to generate/create an adversarial audit heartbeat prompt",
        "same-response",
        "second Goal Maestro command",
        "Broad words",
        "Goal Maestro stop states",
    ),
    "docs/install/AGENT-MANUAL.md": (
        "--execute-loop",
        "--audit-heartbeat-prompt",
        "audit_heartbeat=true",
        "adversarial_audit_heartbeat: requested",
        "not the execution loop parameter",
        "combined form",
        "same-response",
        "Goal Maestro stop states",
    ),
    "docs/install/MINI-PROMPT.md": (
        "--execute-loop",
        "--audit-heartbeat-prompt",
        "audit_heartbeat=true",
        "adversarial_audit_heartbeat: requested",
        "same-response",
        "Goal Maestro stop states",
    ),
    "docs/adapters/CODEX.md": (
        "--execute-loop",
        "--audit-heartbeat-prompt",
        "audit_heartbeat=true",
        "adversarial_audit_heartbeat: requested",
        "broad audit/monitor/heartbeat wording does not activate it",
        "same-response",
        "Goal Maestro stop states",
    ),
    "docs/adapters/CLAUDE.md": (
        "--execute-loop",
        "--audit-heartbeat-prompt",
        "audit_heartbeat=true",
        "adversarial_audit_heartbeat: requested",
        "broad audit/monitor/heartbeat wording does not activate it",
        "same-response",
        "Goal Maestro stop states",
    ),
    "docs/adapters/PLATFORM-DIFFERENCES.md": (
        "--execute-loop",
        "--audit-heartbeat-prompt",
        "audit_heartbeat=true",
        "adversarial_audit_heartbeat: requested",
        "same-response",
        "Goal Maestro stop states",
    ),
    "docs/i18n/tes-public.content.json": (
        "--execute-loop",
        "--audit-heartbeat-prompt",
        "audit_heartbeat=true",
        "adversarial_audit_heartbeat: requested",
        "same-response",
        "broad words",
    ),
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
    folded = normalized(text).casefold()
    return [term for term in NATURAL_INTENTS if normalized(term).casefold() not in folded]


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


def route_case_failures(name: str, text: str, cases: tuple[dict[str, Any], ...]) -> list[str]:
    failures: list[str] = []
    lines = [
        normalized(line)
        for line in text.splitlines()
        if "->" in line
    ]
    folded_lines = [line.casefold() for line in lines]
    for case in cases:
        case_id = str(case["id"])
        expected_route = str(case["expected_route"])
        forbidden_routes = tuple(str(route) for route in case.get("forbidden_routes", ()))
        for intent in tuple(str(item) for item in case["intents"]):
            folded_intent = normalized(intent).casefold()
            matches = [
                lines[index]
                for index, folded in enumerate(folded_lines)
                if folded_intent in folded
            ]
            if not matches:
                failures.append(f"{name} missing route case {case_id}: {intent}")
                continue
            for line in matches:
                routes = set(ROUTE_TARGET_RE.findall(line))
                if expected_route not in routes:
                    failures.append(
                        f"{name} route case {case_id} must route {intent} to {expected_route}"
                    )
                unexpected = sorted(route for route in routes if route != expected_route)
                for route in unexpected:
                    failures.append(
                        f"{name} route case {case_id} exposes route inventory for {intent}: {route}"
                    )
                for route in forbidden_routes:
                    if route in routes:
                        failures.append(
                            f"{name} route case {case_id} must not route {intent} to {route}"
                        )
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
    # Lazy surfaces and docs own the full init-router protocol.
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
    # Always-on bootloaders carry only a short init anchor + route, never the
    # full protocol. Missing anchor is FAIL (no route to the lazy surface);
    # restating the full dense protocol would be the bloat the migration cured.
    for relpath in INIT_ROUTER_BOOTLOADERS:
        path = root / relpath
        if not path.exists():
            failures.append(f"missing init bootloader: {relpath}")
            checked.append({"path": relpath, "status": "MISSING"})
            continue
        text = path.read_text(encoding="utf-8")
        normalized_text = normalized(text).casefold()
        missing_anchor = [t for t in INIT_ROUTER_ANCHOR_TERMS if t.casefold() not in normalized_text]
        failures.extend(
            f"{relpath} missing init anchor term: {term}" for term in missing_anchor
        )
        checked.append(
            {"path": relpath, "kind": "bootloader-anchor",
             "status": "PASS" if not missing_anchor else "FAIL"}
        )
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


def check_goal_maestro_option_docs(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    checked: list[dict[str, Any]] = []
    failures: list[str] = []
    for relpath, terms in GOAL_MAESTRO_OPTION_DOC_TERMS.items():
        path = root / relpath
        if not path.exists():
            failures.append(f"missing goal-maestro option doc: {relpath}")
            checked.append({"path": relpath, "status": "MISSING"})
            continue
        text = normalized(path.read_text(encoding="utf-8"))
        missing = [term for term in terms if term not in text]
        failures.extend(f"{relpath} missing goal-maestro option doc term: {term}" for term in missing)
        checked.append({"path": relpath, "status": "PASS" if not missing else "FAIL"})
    return checked, failures


def goal_maestro_loop_failures(name: str, text: str) -> list[str]:
    normalized_text = normalized(text)
    return [
        f"{name} missing goal-maestro loop contract term: {term}"
        for term in GOAL_MAESTRO_LOOP_TERMS
        if term not in normalized_text
    ]


def goal_maestro_loop_file_key(relpath: str) -> str:
    marker = "tes-goal-maestro/"
    if marker in relpath:
        return relpath.split(marker, 1)[1]
    return relpath


def goal_maestro_loop_file_failures(relpath: str, text: str) -> list[str]:
    key = goal_maestro_loop_file_key(relpath)
    normalized_text = normalized(text)
    failures = [
        f"{relpath} missing goal-maestro file contract term: {term}"
        for term in GOAL_MAESTRO_LOOP_FILE_TERMS.get(key, ())
        if term not in normalized_text
    ]
    if "--execute-loop-parent-fallback" in normalized_text and "direct equivalent" in normalized_text:
        failures.append(f"{relpath} weakens parent fallback with direct-equivalent wording")
    return failures


def goal_maestro_ledger_failures(name: str, text: str) -> list[str]:
    folded = normalized(text).casefold()
    failures = [
        f"{name} ledger missing field: {field}"
        for field in GOAL_MAESTRO_LEDGER_FIELDS
        if field not in text
    ]
    if not re.search(r"\bSPEC-(?:\d{3}|AUDIT-\d{3})\b", text):
        failures.append(f"{name} ledger missing SPEC id")
    for pattern in GOAL_MAESTRO_LEDGER_FORBIDDEN_PATTERNS:
        if re.search(pattern, folded):
            failures.append(f"{name} ledger contains forbidden payload pattern: {pattern}")
    return failures


def goal_maestro_declared_spec_units(text: str) -> list[str]:
    units = re.findall(r"\bSPEC-\d{3}\b", text)
    ordered: list[str] = []
    for unit in units:
        if unit == "SPEC-000" or unit in ordered:
            continue
        ordered.append(unit)
    return ordered


def goal_maestro_generated_prompt_failures(
    name: str,
    text: str,
    *,
    execute_loop_requested: bool,
    next_prompt_handoff_requested: bool = False,
) -> list[str]:
    normalized_text = normalized(text)
    failures: list[str] = []
    loop_markers = (
        "Execution Cost Draft",
        "ACTIVE_SPEC=",
        "loop-state block",
        "Failed Attempt Recovery",
        "Cloud Query Redaction Block",
        "Executive Stop Audit",
        "GOAL-EXECUTION-LOOP-LEDGER",
        "--execute-loop-parent-fallback",
        "strict sequential replay",
        "Pre-Edit Gate",
        "FIRST_UNEXECUTED_UNIT",
        "MAY_EDIT=yes",
        "reference implementation",
        "baseline-only comparison",
        "STRUCTURAL_METHOD=",
        "bug_vs_architecture",
        "Structural handoff:",
    )
    if execute_loop_requested:
        for term in loop_markers:
            if term not in normalized_text:
                failures.append(f"{name} generated prompt missing execute-loop term: {term}")
        for pattern in GOAL_MAESTRO_EXECUTION_CREDIT_FORBIDDEN_PATTERNS:
            if re.search(pattern, normalized_text, re.IGNORECASE):
                failures.append(f"{name} generated prompt credits reference evidence as loop execution")
        if next_prompt_handoff_requested and "Do not execute the next prompt automatically" in normalized_text:
            failures.append(
                f"{name} generated prompt conflicts handoff no-execute text with execute-loop continuation"
            )
        return failures

    for term in loop_markers:
        if term in normalized_text:
            failures.append(f"{name} generated prompt includes execute-loop term without trigger: {term}")
    if next_prompt_handoff_requested and "Do not execute the next prompt automatically" not in normalized_text:
        failures.append(f"{name} generated prompt missing handoff no-execute guard")
    return failures


def goal_maestro_generated_prompt_e2e_failures(
    name: str,
    spec_text: str,
    prompt_text: str,
    *,
    execute_loop_requested: bool,
    next_prompt_handoff_requested: bool = False,
) -> list[str]:
    failures: list[str] = []
    normalized_spec = normalized(spec_text)
    normalized_prompt = normalized(prompt_text)
    for term in GOAL_MAESTRO_MATURE_SPEC_REQUIRED_TERMS:
        if term not in normalized_spec:
            failures.append(f"{name} mature SPEC missing term: {term}")
    for term in GOAL_MAESTRO_GENERATED_PROMPT_REQUIRED_TERMS:
        if term not in normalized_prompt:
            failures.append(f"{name} generated prompt missing base term: {term}")

    declared_units = goal_maestro_declared_spec_units(spec_text)
    if not declared_units:
        failures.append(f"{name} mature SPEC declares no SPEC units")
    for unit in declared_units:
        if not re.search(rf"(?m)^{re.escape(unit)}\b", prompt_text):
            failures.append(f"{name} generated prompt missing declared unit entry: {unit}")
    positions = [
        match.start()
        for unit in declared_units
        for match in [re.search(rf"(?m)^{re.escape(unit)}\b", prompt_text)]
        if match
    ]
    if positions != sorted(positions):
        failures.append(f"{name} generated prompt reorders declared SPEC units")

    failures.extend(
        goal_maestro_generated_prompt_failures(
            name,
            prompt_text,
            execute_loop_requested=execute_loop_requested,
            next_prompt_handoff_requested=next_prompt_handoff_requested,
        )
    )
    return failures


def check_goal_maestro_loop_contracts(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    checked: list[dict[str, Any]] = []
    failures: list[str] = []
    for platform, paths in GOAL_MAESTRO_LOOP_CONTRACT_PATHS.items():
        chunks: list[str] = []
        platform_failures: list[str] = []
        files: list[dict[str, Any]] = []
        for relpath in paths:
            path = root / relpath
            if not path.exists():
                failure = f"missing trigger source: {relpath}"
                platform_failures.append(failure)
                files.append({"path": relpath, "status": "MISSING"})
                continue
            text = path.read_text(encoding="utf-8")
            chunks.append(text)
            file_failures = goal_maestro_loop_file_failures(relpath, text)
            platform_failures.extend(file_failures)
            files.append({"path": relpath, "status": "PASS" if not file_failures else "FAIL"})
        group_text = "\n".join(chunks)
        platform_failures.extend(
            goal_maestro_loop_failures(f"{platform} tes-goal-maestro loop", group_text)
        )
        failures.extend(platform_failures)
        checked.append(
            {
                "platform": platform,
                "paths": list(paths),
                "status": "PASS" if not platform_failures else "FAIL",
                "files": files,
            }
        )
    return checked, failures


def pressure_contract_failures(name: str, text: str, terms: tuple[str, ...]) -> list[str]:
    return [
        f"{name} missing pressure contract term: {term}"
        for term in terms
        if term not in text
    ]


def check_pressure_skill_contracts(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    checked: list[dict[str, Any]] = []
    failures: list[str] = []
    for platform in ("codex", "claude"):
        skill_root = "src/adapters/codex/skills" if platform == "codex" else "src/adapters/claude/skills"
        for skill in ("tes-prospect", "tes-mine"):
            relpath = f"{skill_root}/{skill}/SKILL.md"
            path = root / relpath
            if not path.exists():
                failures.append(f"{platform} missing pressure skill contract: {relpath}")
                checked.append({"platform": platform, "skill": skill, "path": relpath, "status": "MISSING"})
                continue
            missing = pressure_contract_failures(
                f"{relpath}",
                normalized(path.read_text(encoding="utf-8")),
                PRESSURE_CONTRACT_TERMS,
            )
            failures.extend(missing)
            checked.append({"platform": platform, "skill": skill, "path": relpath, "status": "PASS" if not missing else "FAIL"})

            agent_relpath = f"{skill_root}/{skill}/agents/openai.yaml"
            agent_path = root / agent_relpath
            if not agent_path.exists():
                failures.append(f"{platform} missing pressure agent prompt: {agent_relpath}")
                checked.append({"platform": platform, "skill": skill, "path": agent_relpath, "status": "MISSING"})
                continue
            agent_missing = pressure_contract_failures(
                f"{agent_relpath}",
                normalized(agent_path.read_text(encoding="utf-8")),
                PRESSURE_AGENT_TERMS,
            )
            failures.extend(agent_missing)
            checked.append({"platform": platform, "skill": skill, "path": agent_relpath, "status": "PASS" if not agent_missing else "FAIL"})
    return checked, failures


def check_pressure_fixture_dataset(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    path = root / PRESSURE_FIXTURE_DATASET
    if not path.exists():
        return [{"path": PRESSURE_FIXTURE_DATASET, "status": "MISSING"}], [
            f"missing pressure fixture dataset: {PRESSURE_FIXTURE_DATASET}"
        ]

    failures: list[str] = []
    checked: list[dict[str, Any]] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [{"path": PRESSURE_FIXTURE_DATASET, "status": "FAIL"}], [
            f"invalid pressure fixture dataset JSON: {exc}"
        ]

    evals = data.get("evals")
    if not isinstance(evals, list) or not evals:
        failures.append("pressure fixture dataset must contain evals")
        evals = []

    dataset_text = normalized(json.dumps(data, ensure_ascii=False))
    for term in PRESSURE_FIXTURE_REQUIRED_TERMS:
        if term not in dataset_text:
            failures.append(f"pressure fixture dataset missing term: {term}")

    for item in evals:
        fixture_id = item.get("id", "(unknown)") if isinstance(item, dict) else "(invalid)"
        if not isinstance(item, dict):
            failures.append("pressure fixture item must be an object")
            checked.append({"path": PRESSURE_FIXTURE_DATASET, "fixture": fixture_id, "status": "FAIL"})
            continue
        for key in ("id", "kind", "prompt", "expected_any", "forbidden"):
            if key not in item:
                failures.append(f"pressure fixture missing {key}: {fixture_id}")
        if not item.get("expected_any"):
            failures.append(f"pressure fixture has no expected assertions: {fixture_id}")
        if not item.get("forbidden"):
            failures.append(f"pressure fixture has no forbidden assertions: {fixture_id}")
        checked.append({"path": PRESSURE_FIXTURE_DATASET, "fixture": fixture_id, "status": "PASS"})

    if not any(
        isinstance(item, dict)
        and item.get("kind") == "pressure-drift"
        and "several questions" in normalized(str(item.get("prompt", "")))
        for item in evals
    ):
        failures.append("pressure fixture dataset must include a several-questions drift prompt")

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
            ".claude/skills/tes-engineering-discipline/SKILL.md",
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

    route_case_text, route_case_read_failures = read_group(root, DOC_SOURCE_GROUPS["command_triggers_doc"])
    route_case_failures_list = [
        *route_case_read_failures,
        *route_case_failures("command_triggers_doc", route_case_text, ROUTE_CASES),
    ]
    failures.extend(route_case_failures_list)
    checked.append(
        {
            "group": "route_cases",
            "paths": list(DOC_SOURCE_GROUPS["command_triggers_doc"]),
            "status": "PASS" if not route_case_failures_list else "FAIL",
        }
    )

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

    goal_maestro_option_docs_checked, goal_maestro_option_docs_failures = check_goal_maestro_option_docs(root)
    failures.extend(goal_maestro_option_docs_failures)
    checked.append(
        {
            "group": "goal_maestro_option_docs",
            "status": "PASS" if not goal_maestro_option_docs_failures else "FAIL",
            "files": goal_maestro_option_docs_checked,
        }
    )

    goal_maestro_loop_checked, goal_maestro_loop_failures_list = check_goal_maestro_loop_contracts(root)
    failures.extend(goal_maestro_loop_failures_list)
    checked.append(
        {
            "group": "goal_maestro_loop_contracts",
            "status": "PASS" if not goal_maestro_loop_failures_list else "FAIL",
            "files": goal_maestro_loop_checked,
        }
    )

    pressure_checked, pressure_failures = check_pressure_skill_contracts(root)
    failures.extend(pressure_failures)
    checked.append(
        {
            "group": "pressure_skill_contracts",
            "status": "PASS" if not pressure_failures else "FAIL",
            "files": pressure_checked,
        }
    )

    pressure_fixture_checked, pressure_fixture_failures = check_pressure_fixture_dataset(root)
    failures.extend(pressure_fixture_failures)
    checked.append(
        {
            "group": "pressure_fixture_dataset",
            "paths": [PRESSURE_FIXTURE_DATASET],
            "status": "PASS" if not pressure_fixture_failures else "FAIL",
            "files": pressure_fixture_checked,
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

    wrapped_natural = (
        good_text.replace("gerar um /goal maestral", "gerar um /goal\nmaestral")
        .replace("mapa TES", "mapa\nTES")
        .replace("tes open obsidian", "tes open\nobsidian")
    )
    wrapped_failures = check_text("fixture_wrapped_natural", wrapped_natural)
    if any("natural intent" in item for item in wrapped_failures):
        failures.append("wrapped natural intents must tolerate formatting line breaks")

    map_route_cases = (
        {
            "id": "fixture-map-next-flow",
            "intents": ("map this project",),
            "expected_route": "/tes-map",
            "forbidden_routes": ("/tes-align", "/tes-doctor"),
        },
    )
    if route_case_failures("route_good", "map this project -> /tes-map", map_route_cases):
        failures.append("good route fixture must pass with one expected next flow")
    route_inventory = "map this project -> /tes-map /tes-align /tes-doctor"
    if not any("exposes route inventory" in item for item in route_case_failures("route_inventory", route_inventory, map_route_cases)):
        failures.append("route inventory fixture must fail when extra routes are exposed")
    wrong_route = "map this project -> /tes-align"
    if not any("must route map this project to /tes-map" in item for item in route_case_failures("route_wrong", wrong_route, map_route_cases)):
        failures.append("wrong route fixture must fail without the expected next flow")

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
        (target / ".claude/skills/tes-engineering-discipline").mkdir(parents=True)
        (target / ".claude/skills/tes-init").mkdir(parents=True)
        (target / ".claude/skills/tes-setup").mkdir(parents=True)
        (target / ".claude/skills/tes-update").mkdir(parents=True)
        (target / ".claude/skills/tes-goal-maestro").mkdir(parents=True)
        (target / ".claude/skills/tes-prospect").mkdir(parents=True)
        (target / ".claude/skills/tes-mine").mkdir(parents=True)
        (target / ".claude/skills/tes-field-reports").mkdir(parents=True)
        (target / ".claude/skills/tes-bump").mkdir(parents=True)
        (target / "CLAUDE.md").write_text(good_text, encoding="utf-8")
        (target / ".claude/skills/tes-engineering-discipline/SKILL.md").write_text(good_text, encoding="utf-8")
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

    good_pressure = "\n".join(PRESSURE_CONTRACT_TERMS)
    if pressure_contract_failures("pressure_good", good_pressure, PRESSURE_CONTRACT_TERMS):
        failures.append("good pressure fixture must pass one-branch pressure terms")

    broad_pressure = good_pressure.replace("one decision branch at a time", "several branches at once")
    if not any("one decision branch at a time" in item for item in pressure_contract_failures("pressure_broad", broad_pressure, PRESSURE_CONTRACT_TERMS)):
        failures.append("broad pressure fixture must fail without one-branch pressure")

    multi_question_pressure = good_pressure.replace("exactly one next question", "several next questions")
    if not any("exactly one next question" in item for item in pressure_contract_failures("pressure_multi_question", multi_question_pressure, PRESSURE_CONTRACT_TERMS)):
        failures.append("multi-question pressure fixture must fail without exactly-one question")

    no_recommendation_pressure = good_pressure.replace("exactly one recommended answer", "a list of options")
    if not any("exactly one recommended answer" in item for item in pressure_contract_failures("pressure_no_recommendation", no_recommendation_pressure, PRESSURE_CONTRACT_TERMS)):
        failures.append("pressure fixture must fail without exactly-one recommendation")

    no_evidence_pressure = good_pressure.replace("repository evidence can answer", "ask the user what evidence exists")
    if not any("repository evidence can answer" in item for item in pressure_contract_failures("pressure_no_evidence", no_evidence_pressure, PRESSURE_CONTRACT_TERMS)):
        failures.append("pressure fixture must fail without codebase-before-question evidence")

    good_goal_loop = "\n".join(GOAL_MAESTRO_LOOP_TERMS)
    if goal_maestro_loop_failures("goal_loop_good", good_goal_loop):
        failures.append("good goal-maestro loop fixture must pass hardened loop terms")

    no_execute_loop = good_goal_loop.replace("--execute-loop", "--plain-goal")
    if not any("--execute-loop" in item for item in goal_maestro_loop_failures("goal_loop_no_trigger", no_execute_loop)):
        failures.append("goal-maestro loop fixture must fail without execute-loop trigger")

    no_loop_state = good_goal_loop.replace("loop-state block", "attempt notes")
    if not any("loop-state block" in item for item in goal_maestro_loop_failures("goal_loop_no_state", no_loop_state)):
        failures.append("goal-maestro loop fixture must fail without loop-state evidence")

    no_cloud_redaction = good_goal_loop.replace("Cloud Query Redaction Block", "cloud notes")
    if not any("Cloud Query Redaction Block" in item for item in goal_maestro_loop_failures("goal_loop_no_redaction", no_cloud_redaction)):
        failures.append("goal-maestro loop fixture must fail without cloud redaction block")

    good_root_file = "\n".join(GOAL_MAESTRO_LOOP_FILE_TERMS["SKILL.md"])
    if goal_maestro_loop_file_failures(
        "src/adapters/codex/skills/tes-goal-maestro/SKILL.md",
        good_root_file,
    ):
        failures.append("good goal-maestro root file fixture must pass file-level terms")

    root_without_mantra = good_root_file.replace("Routing Realignment Mantra", "Routing Notes")
    if not any(
        "Routing Realignment Mantra" in item
        for item in goal_maestro_loop_file_failures(
            "src/adapters/codex/skills/tes-goal-maestro/SKILL.md",
            root_without_mantra,
        )
    ):
        failures.append("goal-maestro root file fixture must fail without routing mantra")

    good_runner_file = "\n".join(GOAL_MAESTRO_LOOP_FILE_TERMS["references/execution-loop-runner.md"])
    if goal_maestro_loop_file_failures(
        "src/adapters/codex/skills/tes-goal-maestro/references/execution-loop-runner.md",
        good_runner_file,
    ):
        failures.append("good goal-maestro runner file fixture must pass file-level terms")

    runner_without_schema = good_runner_file.replace("Ledger Schema", "Ledger Notes")
    if not any(
        "Ledger Schema" in item
        for item in goal_maestro_loop_file_failures(
            "src/adapters/codex/skills/tes-goal-maestro/references/execution-loop-runner.md",
            runner_without_schema,
        )
    ):
        failures.append("goal-maestro runner file fixture must fail without ledger schema")

    runner_with_weak_fallback = good_runner_file + "\n--execute-loop-parent-fallback or a direct equivalent"
    if not any(
        "direct-equivalent" in item
        for item in goal_maestro_loop_file_failures(
            "src/adapters/codex/skills/tes-goal-maestro/references/execution-loop-runner.md",
            runner_with_weak_fallback,
        )
    ):
        failures.append("goal-maestro runner file fixture must fail on weak parent fallback wording")

    good_structural_method_file = "\n".join(
        GOAL_MAESTRO_LOOP_FILE_TERMS["references/structural-method.md"]
    )
    if goal_maestro_loop_file_failures(
        "src/adapters/codex/skills/tes-goal-maestro/references/structural-method.md",
        good_structural_method_file,
    ):
        failures.append("good goal-maestro structural-method fixture must pass file-level terms")

    structural_method_without_repair = good_structural_method_file.replace("structural_repair", "repair")
    if not any(
        "structural_repair" in item
        for item in goal_maestro_loop_file_failures(
            "src/adapters/codex/skills/tes-goal-maestro/references/structural-method.md",
            structural_method_without_repair,
        )
    ):
        failures.append("goal-maestro structural-method fixture must fail without structural_repair")

    good_template_file = "\n".join(
        GOAL_MAESTRO_LOOP_FILE_TERMS["templates/maestral-goal-prompt.template.md"]
    )
    if goal_maestro_loop_file_failures(
        "src/adapters/codex/skills/tes-goal-maestro/templates/maestral-goal-prompt.template.md",
        good_template_file,
    ):
        failures.append("good goal-maestro prompt template fixture must pass file-level terms")

    template_without_spec000 = good_template_file.replace("SPEC-000 Preflight And Baseline", "Baseline")
    if not any(
        "SPEC-000 Preflight And Baseline" in item
        for item in goal_maestro_loop_file_failures(
            "src/adapters/codex/skills/tes-goal-maestro/templates/maestral-goal-prompt.template.md",
            template_without_spec000,
        )
    ):
        failures.append("goal-maestro prompt template fixture must fail without SPEC-000")

    good_generated_loop_prompt = "\n".join(
        (
            "Execution Cost Draft",
            "ACTIVE_SPEC=SPEC-001",
            "Pre-Edit Gate",
            "EXECUTE_LOOP_REQUESTED=yes",
            "READY_GOAL_PROMPT=present",
            "DECLARED_UNITS=SPEC-001,SPEC-002",
            "FIRST_UNEXECUTED_UNIT=SPEC-001",
            "BASELINE_ONLY_COMMITS=none",
            "MAY_EDIT=yes",
            "loop-state block",
            "Failed Attempt Recovery",
            "Cloud Query Redaction Block",
            "Executive Stop Audit",
            "GOAL-EXECUTION-LOOP-LEDGER-example.md",
            "--execute-loop-parent-fallback",
            "strict sequential replay",
            "reference implementation",
            "baseline-only comparison",
            "STRUCTURAL_METHOD=web-app",
            "bug_vs_architecture=behavior_bug",
            "Structural handoff:",
        )
    )
    if goal_maestro_generated_prompt_failures(
        "generated_loop_good",
        good_generated_loop_prompt,
        execute_loop_requested=True,
        next_prompt_handoff_requested=True,
    ):
        failures.append("good generated execute-loop prompt fixture must pass")

    generated_loop_missing_recovery = good_generated_loop_prompt.replace("Failed Attempt Recovery", "retry notes")
    if not any(
        "Failed Attempt Recovery" in item
        for item in goal_maestro_generated_prompt_failures(
            "generated_loop_missing_recovery",
            generated_loop_missing_recovery,
            execute_loop_requested=True,
        )
    ):
        failures.append("generated execute-loop prompt fixture must fail without failed-attempt recovery")

    generated_loop_missing_pre_edit = good_generated_loop_prompt.replace("Pre-Edit Gate", "preflight note")
    if not any(
        "Pre-Edit Gate" in item
        for item in goal_maestro_generated_prompt_failures(
            "generated_loop_missing_pre_edit",
            generated_loop_missing_pre_edit,
            execute_loop_requested=True,
        )
    ):
        failures.append("generated execute-loop prompt fixture must fail without Pre-Edit Gate")

    generated_loop_missing_first_unexecuted = good_generated_loop_prompt.replace(
        "FIRST_UNEXECUTED_UNIT=SPEC-001", ""
    )
    if not any(
        "FIRST_UNEXECUTED_UNIT" in item
        for item in goal_maestro_generated_prompt_failures(
            "generated_loop_missing_first_unexecuted",
            generated_loop_missing_first_unexecuted,
            execute_loop_requested=True,
        )
    ):
        failures.append("generated execute-loop prompt fixture must fail without FIRST_UNEXECUTED_UNIT")

    generated_loop_missing_structural_method = good_generated_loop_prompt.replace("STRUCTURAL_METHOD=web-app", "")
    if not any(
        "STRUCTURAL_METHOD=" in item
        for item in goal_maestro_generated_prompt_failures(
            "generated_loop_missing_structural_method",
            generated_loop_missing_structural_method,
            execute_loop_requested=True,
        )
    ):
        failures.append("generated execute-loop prompt fixture must fail without STRUCTURAL_METHOD")

    generated_loop_missing_structural_handoff = good_generated_loop_prompt.replace("Structural handoff:", "")
    if not any(
        "Structural handoff:" in item
        for item in goal_maestro_generated_prompt_failures(
            "generated_loop_missing_structural_handoff",
            generated_loop_missing_structural_handoff,
            execute_loop_requested=True,
        )
    ):
        failures.append("generated execute-loop prompt fixture must fail without structural handoff")

    if not any(
        "without trigger" in item
        for item in goal_maestro_generated_prompt_failures(
            "generated_loop_without_trigger",
            good_generated_loop_prompt,
            execute_loop_requested=False,
        )
    ):
        failures.append("generated prompt fixture must fail when execute-loop terms appear without trigger")

    generated_loop_conflicting_handoff = good_generated_loop_prompt + "\nDo not execute the next prompt automatically."
    if not any(
        "conflicts handoff" in item
        for item in goal_maestro_generated_prompt_failures(
            "generated_loop_conflicting_handoff",
            generated_loop_conflicting_handoff,
            execute_loop_requested=True,
            next_prompt_handoff_requested=True,
        )
    ):
        failures.append("generated execute-loop prompt fixture must fail on contradictory handoff no-execute text")

    generated_loop_reference_credit = (
        good_generated_loop_prompt
        + "\nreference implementation validates loop execution for SPEC-001"
    )
    if not any(
        "credits reference evidence" in item
        for item in goal_maestro_generated_prompt_failures(
            "generated_loop_reference_credit",
            generated_loop_reference_credit,
            execute_loop_requested=True,
        )
    ):
        failures.append("generated execute-loop prompt fixture must fail when reference implementation is credited as execution")

    good_handoff_prompt = "GO certification complete. Do not execute the next prompt automatically."
    if goal_maestro_generated_prompt_failures(
        "generated_handoff_good",
        good_handoff_prompt,
        execute_loop_requested=False,
        next_prompt_handoff_requested=True,
    ):
        failures.append("good generated handoff prompt fixture must pass without execute-loop terms")

    good_ledger = "\n".join(
        (
            "# GOAL-EXECUTION-LOOP-LEDGER-example",
            "## SPEC-001",
            "spec_id: SPEC-001",
            "spec_version: source-v1",
            "attempt: 1",
            "repair_count: 0",
            "audit_repair_cycle: 0",
            "first_unexecuted_unit: SPEC-001",
            "failed_attempt_recovery_decision: none",
            "commit: abc1234",
            "oracle_status: PASS",
            "structural_method_id: web-app",
            "topology_decision: split-modules",
            "structural_debt: none",
            "next_structural_constraint: preserve split",
            "stop_state: next",
            "next_allowed_action: worker_attempt",
        )
    )
    if goal_maestro_ledger_failures("ledger_good", good_ledger):
        failures.append("good execution-loop ledger fixture must pass")

    ledger_missing_field = good_ledger.replace("next_allowed_action: worker_attempt", "")
    if not any(
        "next_allowed_action:" in item
        for item in goal_maestro_ledger_failures("ledger_missing_field", ledger_missing_field)
    ):
        failures.append("ledger fixture must fail without next_allowed_action")

    ledger_with_raw_payload = good_ledger + "\nraw diff: leaked implementation patch"
    if not any(
        "raw diff" in item
        for item in goal_maestro_ledger_failures("ledger_with_raw_payload", ledger_with_raw_payload)
    ):
        failures.append("ledger fixture must fail when raw diff payload is stored")

    mature_spec = "\n".join(
        (
            "Canonical Artifact: docs/roadmap/goals/super-specs/example.md",
            "Capability: example loop convergence",
            "Certified Context: existing goal-maestro contract",
            "Phase Boundary: instruction and oracle hardening only",
            "Non-Objectives: no remote push",
            "Central Rule: preserve declared units",
            "Forbidden Moves: no broad merged unit",
            "Acceptance Criteria: prompt validates against command trigger oracle",
            "Negative Grep: no direct equivalent fallback",
            "Stop States: GO, NEEDS_OWNER_DECISION, SAFETY_BLOCKED",
            "Commit Strategy: one commit per SPEC",
            "Final Delivery Contract: certified local closeout",
            "Execution Units:",
            "SPEC-001 Harden prompt fixture",
            "SPEC-002 Harden ledger fixture",
        )
    )
    generated_e2e_prompt = "\n".join(
        (
            "/goal",
            "Main SPEC:",
            "docs/roadmap/goals/super-specs/example.md",
            "SPEC-000 Preflight And Baseline",
            "SPEC-001 Harden prompt fixture",
            "SPEC-002 Harden ledger fixture",
            "Execution unit fidelity:",
            "git show --stat --oneline <commit>",
            "Sync status:",
            "Engineering Method Profile",
            "STRUCTURAL_METHOD=web-app",
            "Structural method result:",
            "Structural handoff:",
            "Full Oracle And Closeout",
            "Stop criteria:",
            "Final delivery:",
            "Execution Cost Draft",
            "ACTIVE_SPEC=SPEC-001",
            "Pre-Edit Gate",
            "EXECUTE_LOOP_REQUESTED=yes",
            "READY_GOAL_PROMPT=present",
            "DECLARED_UNITS=SPEC-001,SPEC-002",
            "FIRST_UNEXECUTED_UNIT=SPEC-001",
            "BASELINE_ONLY_COMMITS=none",
            "MAY_EDIT=yes",
            "loop-state block",
            "Failed Attempt Recovery",
            "Cloud Query Redaction Block",
            "Executive Stop Audit",
            "GOAL-EXECUTION-LOOP-LEDGER-example.md",
            "--execute-loop-parent-fallback",
            "strict sequential replay",
            "reference implementation",
            "baseline-only comparison",
            "bug_vs_architecture=behavior_bug",
        )
    )
    if goal_maestro_generated_prompt_e2e_failures(
        "generated_e2e_good",
        mature_spec,
        generated_e2e_prompt,
        execute_loop_requested=True,
        next_prompt_handoff_requested=True,
    ):
        failures.append("good generated prompt E2E fixture must pass from mature SPEC to prompt")

    e2e_missing_method = generated_e2e_prompt.replace("Engineering Method Profile", "")
    if not any(
        "Engineering Method Profile" in item
        for item in goal_maestro_generated_prompt_e2e_failures(
            "generated_e2e_missing_method",
            mature_spec,
            e2e_missing_method,
            execute_loop_requested=True,
            next_prompt_handoff_requested=True,
        )
    ):
        failures.append("generated prompt E2E fixture must fail without Engineering Method Profile")

    e2e_missing_structural_handoff = generated_e2e_prompt.replace("Structural handoff:", "")
    if not any(
        "Structural handoff:" in item
        for item in goal_maestro_generated_prompt_e2e_failures(
            "generated_e2e_missing_structural_handoff",
            mature_spec,
            e2e_missing_structural_handoff,
            execute_loop_requested=True,
            next_prompt_handoff_requested=True,
        )
    ):
        failures.append("generated prompt E2E fixture must fail without Structural handoff")

    e2e_missing_unit = generated_e2e_prompt.replace("SPEC-002 Harden ledger fixture", "")
    if not any(
        "SPEC-002" in item
        for item in goal_maestro_generated_prompt_e2e_failures(
            "generated_e2e_missing_unit",
            mature_spec,
            e2e_missing_unit,
            execute_loop_requested=True,
            next_prompt_handoff_requested=True,
        )
    ):
        failures.append("generated prompt E2E fixture must fail when a declared unit is missing")

    e2e_reordered_units = generated_e2e_prompt.replace(
        "SPEC-001 Harden prompt fixture\nSPEC-002 Harden ledger fixture",
        "SPEC-002 Harden ledger fixture\nSPEC-001 Harden prompt fixture",
    )
    if not any(
        "reorders declared SPEC units" in item
        for item in goal_maestro_generated_prompt_e2e_failures(
            "generated_e2e_reordered_units",
            mature_spec,
            e2e_reordered_units,
            execute_loop_requested=True,
            next_prompt_handoff_requested=True,
        )
    ):
        failures.append("generated prompt E2E fixture must fail when declared units are reordered")

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
