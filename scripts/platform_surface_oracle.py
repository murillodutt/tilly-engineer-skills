#!/usr/bin/env python3
"""Certify platform surface alignment for adapters and automation hooks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import command_trigger_oracle
import codex_plugin_oracle
import materialize_adapter
import project_alignment_oracle
import project_context_oracle


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.207"
CODEX_SKILLS = materialize_adapter.CODEX_SKILLS
CLAUDE_SKILLS = materialize_adapter.CLAUDE_SKILLS

DOCS = {
    "codex_agents": "https://developers.openai.com/codex/guides/agents-md",
    "codex_skills": "https://developers.openai.com/codex/skills",
    "codex_plugins": "https://developers.openai.com/codex/plugins",
    "codex_hooks": "https://developers.openai.com/codex/hooks",
    "codex_config": "https://developers.openai.com/codex/config-reference",
    "codex_rules": "https://developers.openai.com/codex/rules",
    "codex_mcp": "https://developers.openai.com/codex/mcp",
    "claude_features": "https://docs.anthropic.com/en/docs/claude-code/overview",
    "claude_skills": "https://docs.anthropic.com/en/docs/claude-code/skills",
    "claude_plugins": "https://docs.anthropic.com/en/docs/claude-code/plugins",
    "claude_hooks": "https://docs.anthropic.com/en/docs/claude-code/hooks",
    "claude_subagents": "https://docs.anthropic.com/en/docs/claude-code/sub-agents",
    "cursor_rules": "https://docs.cursor.com/en/context/rules",
    "cursor_plugins": "https://cursor.com/docs/plugins",
    "cursor_hooks": "https://cursor.com/docs/hooks",
    "cursor_agents": "https://cursor.com/docs/sdk/typescript",
    "cursor_mcp": "https://docs.cursor.com/en/tools/mcp",
    "vscode_mcp": "https://code.visualstudio.com/docs/copilot/reference/mcp-configuration",
    "mcp_spec": "https://modelcontextprotocol.io/specification/latest",
    "github_issue_forms": "https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms",
    "github_actions": "https://docs.github.com/actions/reference/workflows-and-actions/workflow-syntax",
}

LIFECYCLE_BOUNDARY_TERMS = (
    "TES Memory Lifecycle Boundary",
    "recall",
    "scope normalization",
    "write gate",
    "checkpoint",
    "closeout",
    "subagent return",
    "Parent owns durable memory",
    "durable Cortex writes",
    "evidence return only",
)
ADR_LIFECYCLE_TERMS = (
    "recall",
    "scope normalization",
    "write gate",
    "checkpoint",
    "closeout",
    "subagent return",
)
MATRIX_LIFECYCLE_TERMS = (
    "Memory Lifecycle Matrix",
    *ADR_LIFECYCLE_TERMS,
    "certified",
    "blocked",
    "deferred",
    "not available",
    "git-governed",
)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def exists(relpath: str) -> bool:
    return (ROOT / relpath).exists()


def read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def check_skill(relpath: str, expected_name: str) -> list[str]:
    if not exists(relpath):
        return [f"missing skill: {relpath}"]
    data = parse_frontmatter(read(relpath))
    failures: list[str] = []
    if data.get("name") != expected_name:
        failures.append(f"{relpath} name must be {expected_name}")
    if not data.get("description"):
        failures.append(f"{relpath} missing description")
    return failures


def check_lifecycle_boundary(relpath: str) -> list[str]:
    text = read(relpath)
    return [
        f"{relpath} missing lifecycle boundary term: {term}"
        for term in LIFECYCLE_BOUNDARY_TERMS
        if term not in text
    ]


def check_memory_lifecycle_matrix() -> list[str]:
    failures: list[str] = []
    adr = "docs/adr/0001-tes-memory-lifecycle.md"
    if not exists(adr):
        failures.append(f"missing memory lifecycle contract: {adr}")
    else:
        text = read(adr)
        for term in ADR_LIFECYCLE_TERMS:
            if term not in text:
                failures.append(f"{adr} missing lifecycle term: {term}")

    matrix = "docs/adapters/ADAPTER-CAPABILITY-MATRIX.md"
    if not exists(matrix):
        failures.append(f"missing memory lifecycle matrix: {matrix}")
    else:
        text = read(matrix)
        for term in MATRIX_LIFECYCLE_TERMS:
            if term not in text:
                failures.append(f"{matrix} missing lifecycle matrix term: {term}")
    return failures


def materialized_results() -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-platform-surface-") as tempdir:
        out_root = Path(tempdir) / "adapters"
        results = [
            materialize_adapter.materialize(adapter, out_root)
            for adapter in materialize_adapter.selected_adapters("all")
        ]
        for result in results:
            failures.extend(str(item) for item in result["failures"])
        by_adapter = {str(result["adapter"]): result for result in results}

        required = {
            "codex": (
                "AGENTS.md",
                ".agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py",
                *(f".agents/skills/{skill}/SKILL.md" for skill in CODEX_SKILLS),
            ),
            "claude": (
                "CLAUDE.md",
                *(f".claude/skills/{skill}/SKILL.md" for skill in CLAUDE_SKILLS),
            ),
            "cursor": (
                "CURSOR.md",
                ".cursor/rules/tes-engineering-discipline.mdc",
                ".cursor/rules/tes-runtime-capabilities.mdc",
            ),
        }
        for adapter, paths in required.items():
            root = Path(str(by_adapter[adapter]["root"]))
            for path in paths:
                if not (root / path).exists():
                    failures.append(f"{adapter}: missing materialized {path}")
        forbidden = {
            "codex": (".agents/plugins", "plugins/tilly-engineer-skills"),
            "claude": (".claude-plugin", "skills"),
        }
        for adapter, paths in forbidden.items():
            root = Path(str(by_adapter[adapter]["root"]))
            for path in paths:
                if (root / path).exists():
                    failures.append(f"{adapter}: source-only plugin artifact was materialized: {path}")

    return {"adapters": sorted(materialize_adapter.ADAPTERS)}, failures


def analyze() -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    surfaces: list[dict[str, str]] = []
    failures.extend(check_memory_lifecycle_matrix())
    if not exists("scripts/cortex_host_contract_oracle.py"):
        failures.append("missing Cortex host contract oracle: scripts/cortex_host_contract_oracle.py")
    if not exists("scripts/tes_install.py"):
        failures.append("missing TES installer hook writer: scripts/tes_install.py")

    def surface(platform: str, name: str, status: str, evidence: str) -> None:
        surfaces.append(
            {
                "platform": platform,
                "surface": name,
                "status": status,
                "evidence": evidence,
            }
        )

    # Codex
    # Bootloader keeps the behavioral anchors always-on; the dense Cortex reflex
    # and memory lifecycle boundary live in the lazy skill (three-layer
    # contract). The bootloader is not required to restate them.
    codex_agent = "src/adapters/codex/AGENTS.md"
    codex_discipline_skill = "src/adapters/codex/skills/tes-engineering-discipline/SKILL.md"
    if not exists(codex_agent):
        failures.append(f"missing Codex agent bootloader: {codex_agent}")
    else:
        text = read(codex_agent)
        for term in ("Think Before Coding", "Maturity Layer Gate", "Simplicity First"):
            if term not in text:
                failures.append(f"{codex_agent} missing {term}")
    if exists(codex_discipline_skill):
        if "cortex_reflect" not in read(codex_discipline_skill):
            failures.append(f"{codex_discipline_skill} missing Cortex reflex (lazy owner)")
        failures.extend(check_lifecycle_boundary(codex_discipline_skill))
    for skill in CODEX_SKILLS:
        failures.extend(check_skill(
            f"src/adapters/codex/skills/{skill}/SKILL.md",
            skill,
        ))
    if not exists("src/adapters/codex/skills/tes-engineering-discipline/agents/openai.yaml"):
        failures.append("missing Codex skill agent metadata")
    surface("codex", "agent", "certified", codex_agent)
    surface("codex", "skill", "certified", "; ".join(f"src/adapters/codex/skills/{skill}/SKILL.md" for skill in CODEX_SKILLS))
    for relpath in (
        "src/adapters/codex/plugin/plugin.json",
        "src/adapters/codex/plugin/marketplace.json",
    ):
        if not exists(relpath):
            failures.append(f"missing Codex plugin manifest: {relpath}")
        elif VERSION not in read(relpath):
            failures.append(f"{relpath} must declare {VERSION}")
    codex_plugin_result = codex_plugin_oracle.self_test_result()
    if codex_plugin_result["status"] != "PASS":
        failures.extend(
            f"codex plugin oracle: {failure}"
            for failure in codex_plugin_result["failures"]
        )
    surface(
        "codex",
        "plugin",
        "source-only" if codex_plugin_result["status"] == "PASS" else "fail",
        "src/adapters/codex/plugin/plugin.json is retained in Git but omitted from target installs",
    )
    surface(
        "codex",
        "hook",
        "certified",
        "scripts/tes_install.py writes .codex/config.toml project hooks; scripts/cortex_host_contract_oracle.py proves Codex hook contracts",
    )
    surface("codex", "memory-lifecycle", "certified", codex_agent)
    surface("codex", "rules", "not-packaged", "No sandbox escalation rule is required for this reference package.")
    surface("codex", "mcp", "certified", "scripts/install_mcp.py writes .codex/config.toml")

    # Claude
    # Bootloader keeps the behavioral anchors always-on; the dense Cortex reflex
    # and memory lifecycle boundary live in the lazy tes-engineering-discipline skill.
    claude_agent = "src/adapters/claude/CLAUDE.md"
    claude_guidelines_skill = "src/adapters/claude/skills/tes-engineering-discipline/SKILL.md"
    if not exists(claude_agent):
        failures.append(f"missing Claude bootloader: {claude_agent}")
    else:
        text = read(claude_agent)
        for term in ("Think Before Coding", "Maturity Layer Gate", "Simplicity First"):
            if term not in text:
                failures.append(f"{claude_agent} missing {term}")
    if exists(claude_guidelines_skill):
        if "cortex_reflect" not in read(claude_guidelines_skill):
            failures.append(f"{claude_guidelines_skill} missing Cortex reflex (lazy owner)")
        failures.extend(check_lifecycle_boundary(claude_guidelines_skill))
    for skill in CLAUDE_SKILLS:
        failures.extend(check_skill(f"src/adapters/claude/skills/{skill}/SKILL.md", skill))
    for relpath in (
        "src/adapters/claude/plugin/plugin.json",
        "src/adapters/claude/plugin/marketplace.json",
    ):
        if not exists(relpath):
            failures.append(f"missing Claude plugin manifest: {relpath}")
        elif VERSION not in read(relpath):
            failures.append(f"{relpath} must declare {VERSION}")
    surface("claude", "agent", "certified", claude_agent)
    surface("claude", "skill", "certified", ".claude/skills/** project skills sourced from src/adapters/claude/skills/**")
    surface("claude", "plugin", "source-only", "src/adapters/claude/plugin/plugin.json is retained in Git but omitted from target installs")
    surface(
        "claude",
        "hook",
        "certified",
        "scripts/tes_install.py writes .claude/settings.json project hooks; scripts/cortex_host_contract_oracle.py proves Claude hook contracts",
    )
    surface("claude", "memory-lifecycle", "certified", claude_agent)
    surface("claude", "rules", "not-native", "Claude uses CLAUDE.md, permissions, hooks, skills, plugins, and MCP.")
    surface("claude", "mcp", "certified", "scripts/install_mcp.py writes .mcp.json")

    # Cursor: the discipline anchor is always-on; the capability rule is the
    # Cursor-native lazy layer (Apply Intelligently), so it is alwaysApply:false
    # with a description (official Cursor rule-loading model). The memory
    # lifecycle boundary moved with the capability detail into the lazy rule.
    cursor_rule = "src/adapters/cursor/rules/tes-engineering-discipline.mdc"
    cursor_runtime_rule = "src/adapters/cursor/rules/tes-runtime-capabilities.mdc"
    cursor_rule_modes = {cursor_rule: "true", cursor_runtime_rule: "false"}
    for rule, mode in cursor_rule_modes.items():
        if not exists(rule):
            failures.append(f"missing Cursor rule: {rule}")
            continue
        text = read(rule)
        if f"alwaysApply: {mode}" not in text:
            failures.append(f"{rule} must be alwaysApply: {mode}")
        if "description:" not in text:
            failures.append(f"{rule} missing description")
    if exists(cursor_runtime_rule):
        failures.extend(check_lifecycle_boundary(cursor_runtime_rule))
    if not exists("src/adapters/cursor/CURSOR.md"):
        failures.append("missing Cursor bootloader: src/adapters/cursor/CURSOR.md")
    surface("cursor", "agent", "certified", "src/adapters/cursor/CURSOR.md")
    surface("cursor", "skill", "certified", "src/adapters/cursor/rules/tes-runtime-capabilities.mdc provides command capability routing after clean runtime install and semantic recovery.")
    surface("cursor", "plugin", "deferred", "Cursor plugins are native, but no TES .cursor-plugin package is claimed.")
    surface(
        "cursor",
        "hook",
        "certified",
        "scripts/tes_install.py writes .cursor/hooks.json project hooks; scripts/cortex_host_contract_oracle.py proves Cursor hook contracts",
    )
    surface("cursor", "memory-lifecycle", "certified", cursor_rule)
    surface("cursor", "rules", "certified", cursor_rule)
    surface("cursor", "mcp", "certified", "scripts/install_mcp.py writes .cursor/mcp.json")
    surface("vscode", "mcp", "certified", "scripts/install_mcp.py writes .vscode/mcp.json servers.tes-cortex")

    lefthook = "lefthook.yml"
    if not exists(lefthook):
        failures.append("missing lefthook configuration")
    else:
        text = read(lefthook)
        for term in ("staged_commit_gate.py",):
            if term not in text:
                failures.append(f"{lefthook} missing {term}")
        gate = "scripts/staged_commit_gate.py"
        if not exists(gate):
            failures.append(f"missing staged commit gate: {gate}")
        else:
            gate_text = read(gate)
            for term in ("pre_commit_cortex.py", "staged_surface_check.py", "validate_doc_size.py"):
                if term not in gate_text:
                    failures.append(f"{gate} missing routed gate {term}")

    hook = ".githooks/pre-commit"
    if not exists(hook):
        failures.append("missing repository pre-commit hook")
    elif "lefthook run pre-commit" not in read(hook):
        failures.append(f"{hook} must delegate to lefthook run pre-commit")

    pre_push = ".githooks/pre-push"
    if not exists(pre_push):
        failures.append("missing repository pre-push hook")
    else:
        text = read(pre_push)
        for term in ("TES_FIELD_REPORTS_PRE_PUSH", "pre_push_field_reports.py"):
            if term not in text:
                failures.append(f"{pre_push} missing {term}")

    install_text = read("scripts/install_mcp.py")
    for term in (
        "install_mcp_hosts",
        "field_reports.py",
        "tes_update.py",
        "tes_legacy_retirement.py",
        "root_context.py",
        "helpers_only",
        "--json-only",
        "--transport",
        "--bearer-env",
        "--allow-non-localhost",
    ):
        if term not in install_text:
            failures.append(f"scripts/install_mcp.py missing {term}")
    codex_host_text = read("scripts/install_mcp_hosts/codex.py")
    if "[mcp_servers.tes-cortex]" not in codex_host_text:
        failures.append("scripts/install_mcp_hosts/codex.py missing [mcp_servers.tes-cortex]")
    claude_host_text = read("scripts/install_mcp_hosts/claude.py")
    if ".mcp.json" not in claude_host_text:
        failures.append("scripts/install_mcp_hosts/claude.py missing .mcp.json")
    cursor_host_text = read("scripts/install_mcp_hosts/cursor.py")
    if ".cursor/mcp.json" not in cursor_host_text:
        failures.append("scripts/install_mcp_hosts/cursor.py missing .cursor/mcp.json")
    vscode_host_text = read("scripts/install_mcp_hosts/vscode.py")
    if ".vscode/mcp.json" not in vscode_host_text:
        failures.append("scripts/install_mcp_hosts/vscode.py missing .vscode/mcp.json")
    if 'server_key = "servers"' not in vscode_host_text:
        failures.append("scripts/install_mcp_hosts/vscode.py missing server_key='servers'")
    adapter_text = read("scripts/install_adapter.py")
    for term in (
        "INSTALLED_CLEAN_RUNTIME",
        "clean_backup",
        "semantic_recovery",
        "preserve_context",
    ):
        if term not in adapter_text:
            failures.append(f"scripts/install_adapter.py missing {term}")
    root_text = read("scripts/root_context.py")
    root_gate_text = root_text + "\n" + read("scripts/tes_init.py")
    for term in ("AGENTS.md", "CLAUDE.md", ".cursor/rules", "NEEDS_REVIEW", "RECOVERED", "self_test_mode"):
        if term not in root_gate_text:
            failures.append(f"root context gate missing {term}")
    init_text = read("scripts/tes_init.py")
    for term in (
        "PROJECT-CONTEXT.md",
        "write_project_context",
        "Maximum-Depth Initialization Contract",
        "Recommended Deep Reads",
    ):
        if term not in init_text:
            failures.append(f"scripts/tes_init.py missing project context term: {term}")
    # Init-context detail lives in the lazy surfaces (tes-init skills and the
    # Cursor capability rule), not the always-on Cursor discipline anchor.
    for relpath in (
        "src/adapters/codex/skills/tes-init/SKILL.md",
        "src/adapters/claude/skills/tes-init/SKILL.md",
        "src/adapters/cursor/rules/tes-runtime-capabilities.mdc",
    ):
        text = read(relpath)
        for term in ("PROJECT-CONTEXT.md", "analyze"):
            if term not in text:
                failures.append(f"{relpath} missing init context term: {term}")
    project_context_result = project_context_oracle.self_test()
    if project_context_result["status"] != "PASS":
        failures.extend(
            f"project context oracle: {failure}"
            for failure in project_context_result["failures"]
        )
    surface(
        "shared",
        "project-context",
        "certified" if project_context_result["status"] == "PASS" else "fail",
        "scripts/project_context_oracle.py",
    )
    project_alignment_result = project_alignment_oracle.self_test()
    if project_alignment_result["status"] != "PASS":
        failures.extend(
            f"project alignment oracle: {failure}"
            for failure in project_alignment_result["failures"]
        )
    surface(
        "shared",
        "project-alignment",
        "certified" if project_alignment_result["status"] == "PASS" else "fail",
        "scripts/project_alignment_oracle.py",
    )
    update_text = read("scripts/tes_update.py")
    for term in (
        "recommended_route",
        "update_available",
        "remote_version",
        "/tes-update",
        "/tes:update",
        "legacy_retirement_required",
        "helper_contract_status",
        "STALE_HELPERS",
        "recommended_update_scope",
        "adapter-config",
        "post-Layer Zero",
        "project_start_gate",
        "Project-Start Gate",
        "preflight_context_pass_replaces_execution",
        "required_when_active_intent",
        "helper_contract_status=PASS",
        "runtime_trigger_status",
        "update_available=False",
        "recommended_update_scope=none",
        "record_field_report",
        "--record-field-report",
        "--json-only",
    ):
        if term not in update_text:
            failures.append(f"scripts/tes_update.py missing {term}")
    field_reports_text = read("scripts/field_reports.py")
    for term in ("DESTINATION_REPO", "murillodutt/tilly-engineer-skills", "DISABLED", "gh issue create"):
        if term not in field_reports_text:
            failures.append(f"scripts/field_reports.py missing {term}")

    command_trigger_result = command_trigger_oracle.analyze(ROOT)
    if command_trigger_result["status"] != "PASS":
        failures.extend(
            f"command trigger oracle: {failure}"
            for failure in command_trigger_result["failures"]
        )
    surface(
        "shared",
        "command-triggers",
        "certified" if command_trigger_result["status"] == "PASS" else "fail",
        "scripts/command_trigger_oracle.py",
    )
    surface(
        "shared",
        "memory-lifecycle-matrix",
        "certified",
        "docs/adr/0001-tes-memory-lifecycle.md; docs/adapters/ADAPTER-CAPABILITY-MATRIX.md",
    )

    github_oracle = "scripts/field_reports_github_oracle.py"
    if not exists(github_oracle):
        failures.append(f"missing GitHub receiver oracle: {github_oracle}")
    else:
        text = read(github_oracle)
        for term in ("tes-field-report@2", "field-report-quarantine", "validate_body", "state_reason=not_planned"):
            if term not in text:
                failures.append(f"{github_oracle} missing {term}")

    issue_form = ".github/ISSUE_TEMPLATE/tes-field-report.yml"
    if not exists(issue_form):
        failures.append(f"missing Field Reports issue form: {issue_form}")
    else:
        text = read(issue_form)
        for term in ("TES Field Report", "tes-field-report@2", "privacy-sanitized", "Actionability", "Never include code"):
            if term not in text:
                failures.append(f"{issue_form} missing {term}")

    governance_workflow = ".github/workflows/field-report-governance.yml"
    if not exists(governance_workflow):
        failures.append(f"missing Field Reports governance workflow: {governance_workflow}")
    else:
        text = read(governance_workflow)
        for term in ("issues:", "issues: write", "field_reports_github_oracle.py validate-body", "field-report-quarantine"):
            if term not in text:
                failures.append(f"{governance_workflow} missing {term}")
    surface("github", "issue-template", "certified", issue_form)
    surface("github", "receiver-workflow", "certified", governance_workflow)
    surface("github", "receiver-oracle", "certified", github_oracle)

    materialized, materialize_failures = materialized_results()
    failures.extend(materialize_failures)

    return {
        "version": VERSION,
        "git_head": git_head(),
        "status": "PASS" if not failures else "FAIL",
        "documents": DOCS,
        "surfaces": surfaces,
        "materialized": materialized,
        "warnings": warnings,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.parse_args()

    result = analyze()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[platform-surface] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
