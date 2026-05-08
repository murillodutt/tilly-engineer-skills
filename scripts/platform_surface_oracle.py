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
import materialize_adapter
import project_context_oracle


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.57"
CODEX_SKILLS = materialize_adapter.CODEX_SKILLS
CLAUDE_SKILLS = materialize_adapter.CLAUDE_SKILLS

DOCS = {
    "codex_agents": "https://developers.openai.com/codex/guides/agents-md",
    "codex_skills": "https://developers.openai.com/codex/skills",
    "codex_plugins": "https://developers.openai.com/codex/plugins",
    "codex_hooks": "https://developers.openai.com/codex/hooks",
    "codex_rules": "https://developers.openai.com/codex/rules",
    "codex_mcp": "https://developers.openai.com/codex/mcp",
    "claude_features": "https://code.claude.com/docs/en/features-overview",
    "claude_skills": "https://code.claude.com/docs/en/skills",
    "claude_plugins": "https://code.claude.com/docs/en/plugins",
    "claude_hooks": "https://code.claude.com/docs/en/hooks",
    "cursor_rules": "https://cursor.com/docs/rules",
    "cursor_mcp": "https://cursor.com/docs/mcp",
    "mcp_spec": "https://modelcontextprotocol.io/specification/latest",
    "github_issue_forms": "https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms",
    "github_actions": "https://docs.github.com/actions/reference/workflows-and-actions/workflow-syntax",
}


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
                ".claude-plugin/plugin.json",
                ".claude-plugin/marketplace.json",
                *(f"skills/{skill}/SKILL.md" for skill in CLAUDE_SKILLS),
                *(f".claude/skills/{skill}/SKILL.md" for skill in CLAUDE_SKILLS),
            ),
            "cursor": (
                "CURSOR.md",
                ".cursor/rules/tes-guidelines.mdc",
            ),
        }
        for adapter, paths in required.items():
            root = Path(str(by_adapter[adapter]["root"]))
            for path in paths:
                if not (root / path).exists():
                    failures.append(f"{adapter}: missing materialized {path}")

    return {"adapters": sorted(materialize_adapter.ADAPTERS)}, failures


def analyze() -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    surfaces: list[dict[str, str]] = []

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
    codex_agent = "src/adapters/codex/AGENTS.md"
    if not exists(codex_agent):
        failures.append(f"missing Codex agent bootloader: {codex_agent}")
    else:
        text = read(codex_agent)
        for term in ("Think Before Coding", "Simplicity First", "cortex_reflex"):
            if term not in text:
                failures.append(f"{codex_agent} missing {term}")
    for skill in CODEX_SKILLS:
        failures.extend(check_skill(
            f"src/adapters/codex/skills/{skill}/SKILL.md",
            skill,
        ))
    if not exists("src/adapters/codex/skills/tes-engineering-discipline/agents/openai.yaml"):
        failures.append("missing Codex skill agent metadata")
    surface("codex", "agent", "certified", codex_agent)
    surface("codex", "skill", "certified", "; ".join(f"src/adapters/codex/skills/{skill}/SKILL.md" for skill in CODEX_SKILLS))
    surface("codex", "plugin", "deferred", "Codex plugins are native, but TES v0.3.57 ships local skills first.")
    surface("codex", "hook", "git-governed", ".githooks/pre-commit; .githooks/pre-push")
    surface("codex", "rules", "not-packaged", "No sandbox escalation rule is required for this reference package.")
    surface("codex", "mcp", "certified", "scripts/install_mcp.py writes .codex/config.toml")

    # Claude
    claude_agent = "src/adapters/claude/CLAUDE.md"
    if not exists(claude_agent):
        failures.append(f"missing Claude bootloader: {claude_agent}")
    else:
        text = read(claude_agent)
        for term in ("Think Before Coding", "Simplicity First", "Cortex Reflection"):
            if term not in text:
                failures.append(f"{claude_agent} missing {term}")
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
    surface("claude", "skill", "certified", ".claude/skills/** project skills and skills/** plugin copies sourced from src/adapters/claude/skills/**")
    surface("claude", "plugin", "certified", "src/adapters/claude/plugin/plugin.json")
    surface("claude", "hook", "deferred", "Claude plugin hooks are native, but not claimed by this package.")
    surface("claude", "rules", "not-native", "Claude uses CLAUDE.md, permissions, hooks, skills, plugins, and MCP.")
    surface("claude", "mcp", "certified", "scripts/install_mcp.py writes .mcp.json")

    # Cursor
    cursor_rule = "src/adapters/cursor/rules/tes-guidelines.mdc"
    if not exists(cursor_rule):
        failures.append(f"missing Cursor rule: {cursor_rule}")
    else:
        text = read(cursor_rule)
        if "alwaysApply: true" not in text:
            failures.append(f"{cursor_rule} must keep alwaysApply: true")
        if "description:" not in text:
            failures.append(f"{cursor_rule} missing description")
    if not exists("src/adapters/cursor/CURSOR.md"):
        failures.append("missing Cursor bootloader: src/adapters/cursor/CURSOR.md")
    surface("cursor", "agent", "certified", "src/adapters/cursor/CURSOR.md")
    surface("cursor", "skill", "deferred", "Cursor plugin skills exist officially, but TES v0.3.57 ships Cursor rules first.")
    surface("cursor", "plugin", "deferred", "Cursor plugins are native, but no TES .cursor-plugin package is claimed.")
    surface("cursor", "hook", "git-governed", ".githooks/pre-commit; .githooks/pre-push")
    surface("cursor", "rules", "certified", cursor_rule)
    surface("cursor", "mcp", "certified", "scripts/install_mcp.py writes .cursor/mcp.json")

    hook = ".githooks/pre-commit"
    if not exists(hook):
        failures.append("missing repository pre-commit hook")
    else:
        text = read(hook)
        for term in ("validate_doc_size.py", "cortex.py reflect", "cortex.py curate-plan"):
            if term not in text:
                failures.append(f"{hook} missing {term}")

    pre_push = ".githooks/pre-push"
    if not exists(pre_push):
        failures.append("missing repository pre-push hook")
    else:
        text = read(pre_push)
        for term in ("field_reports.py drain", "TES_FIELD_REPORTS_PRE_PUSH"):
            if term not in text:
                failures.append(f"{pre_push} missing {term}")

    install_text = read("scripts/install_mcp.py")
    for term in (
        "[mcp_servers.tes-cortex]",
        ".mcp.json",
        ".cursor/mcp.json",
        "field_reports.py",
        "tes_update.py",
        "tes_legacy_retirement.py",
        "root_context.py",
        "helpers_only",
        "--json-only",
    ):
        if term not in install_text:
            failures.append(f"scripts/install_mcp.py missing {term}")
    adapter_text = read("scripts/install_adapter.py")
    for term in (
        "preserve-conflict",
        "INSTALLED_WITH_PRESERVED_CONFLICTS",
        "DRY-RUN-WITH-PRESERVED-CONFLICTS",
        "preserved_conflicts",
    ):
        if term not in adapter_text:
            failures.append(f"scripts/install_adapter.py missing {term}")
    root_text = read("scripts/root_context.py")
    root_gate_text = root_text + "\n" + read("scripts/tes_init.py")
    for term in ("AGENTS.md", "CLAUDE.md", ".cursor/rules", "NEEDS_REVIEW", "PRESERVED", "self_test_mode"):
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
    for relpath in (
        "src/adapters/codex/skills/tes-init/SKILL.md",
        "src/adapters/claude/skills/tes-init/SKILL.md",
        "src/adapters/cursor/rules/tes-guidelines.mdc",
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
