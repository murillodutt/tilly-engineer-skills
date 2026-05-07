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

import materialize_adapter


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.20"
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
    "claude_plugins": "https://code.claude.com/docs/en/plugins-reference",
    "claude_hooks": "https://code.claude.com/docs/en/hooks",
    "cursor_rules": "https://docs.cursor.com/context/rules",
    "cursor_mcp": "https://docs.cursor.com/context/model-context-protocol",
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
    with tempfile.TemporaryDirectory(prefix="tilly-platform-surface-") as tempdir:
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
                ".agents/skills/tilly-engineering-discipline/scripts/discipline_oracle.py",
                *(f".agents/skills/{skill}/SKILL.md" for skill in CODEX_SKILLS),
            ),
            "claude": (
                "CLAUDE.md",
                ".claude-plugin/plugin.json",
                ".claude-plugin/marketplace.json",
                *(f"skills/{skill}/SKILL.md" for skill in CLAUDE_SKILLS),
            ),
            "cursor": (
                "CURSOR.md",
                ".cursor/rules/tilly-guidelines.mdc",
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
        for term in ("Think Before Coding", "Simplicity First", "cortex_reflex", "/tilly:init", "tilly init", "Tilly, inicialize este projeto", "/tilly:cortex", "/tilly:field-reports"):
            if term not in text:
                failures.append(f"{codex_agent} missing {term}")
    for skill in CODEX_SKILLS:
        failures.extend(check_skill(
            f"src/adapters/codex/skills/{skill}/SKILL.md",
            skill,
        ))
    if not exists("src/adapters/codex/skills/tilly-engineering-discipline/agents/openai.yaml"):
        failures.append("missing Codex skill agent metadata")
    surface("codex", "agent", "certified", codex_agent)
    surface("codex", "skill", "certified", "; ".join(f"src/adapters/codex/skills/{skill}/SKILL.md" for skill in CODEX_SKILLS))
    surface("codex", "plugin", "deferred", "Codex plugins are native, but Tilly v0.3.20 ships local skills first.")
    surface("codex", "hook", "git-governed", ".githooks/pre-commit; .githooks/pre-push")
    surface("codex", "rules", "not-packaged", "No sandbox escalation rule is required for this reference package.")
    surface("codex", "mcp", "certified", "scripts/install_mcp.py writes .codex/config.toml")

    # Claude
    claude_agent = "src/adapters/claude/CLAUDE.md"
    if not exists(claude_agent):
        failures.append(f"missing Claude bootloader: {claude_agent}")
    else:
        text = read(claude_agent)
        for term in ("Think Before Coding", "Simplicity First", "Cortex Reflection", "/tilly:init", "tilly init", "Tilly, inicialize este projeto", "/tilly:cortex", "/tilly:field-reports"):
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
    surface("claude", "skill", "certified", "; ".join(f"src/adapters/claude/skills/{skill}/SKILL.md" for skill in CLAUDE_SKILLS))
    surface("claude", "plugin", "certified", "src/adapters/claude/plugin/plugin.json")
    surface("claude", "hook", "deferred", "Claude plugin hooks are native, but not claimed by this package.")
    surface("claude", "rules", "not-native", "Claude uses CLAUDE.md, permissions, hooks, skills, plugins, and MCP.")
    surface("claude", "mcp", "certified", "scripts/install_mcp.py writes .mcp.json")

    # Cursor
    cursor_rule = "src/adapters/cursor/rules/tilly-guidelines.mdc"
    if not exists(cursor_rule):
        failures.append(f"missing Cursor rule: {cursor_rule}")
    else:
        text = read(cursor_rule)
        if "alwaysApply: true" not in text:
            failures.append(f"{cursor_rule} must keep alwaysApply: true")
        if "description:" not in text:
            failures.append(f"{cursor_rule} missing description")
        for term in ("/tilly:init", "tilly init", "Tilly, inicialize este projeto", "/tilly:cortex", "/tilly:field-reports"):
            if term not in text:
                failures.append(f"{cursor_rule} missing {term} shortcut routing")
    for relpath in (
        "src/adapters/codex/skills/tilly-init/SKILL.md",
        "src/adapters/claude/skills/tilly-init/SKILL.md",
    ):
        if exists(relpath):
            text = read(relpath)
            for term in ("/tilly:init", "tilly init", "natural init command/prompt", "Tilly, inicialize este projeto"):
                if term not in text:
                    failures.append(f"{relpath} missing {term}")
    if not exists("src/adapters/cursor/CURSOR.md"):
        failures.append("missing Cursor bootloader: src/adapters/cursor/CURSOR.md")
    surface("cursor", "agent", "certified", "src/adapters/cursor/CURSOR.md")
    surface("cursor", "skill", "not-native", "Cursor rules are the portable instruction surface.")
    surface("cursor", "plugin", "not-native", "No Cursor plugin packaging is claimed.")
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
        for term in ("field_reports.py drain", "TILLY_FIELD_REPORTS_PRE_PUSH"):
            if term not in text:
                failures.append(f"{pre_push} missing {term}")

    install_text = read("scripts/install_mcp.py")
    for term in ("[mcp_servers.tilly-cortex]", ".mcp.json", ".cursor/mcp.json", "field_reports.py"):
        if term not in install_text:
            failures.append(f"scripts/install_mcp.py missing {term}")
    field_reports_text = read("scripts/field_reports.py")
    for term in ("DESTINATION_REPO", "murillodutt/tilly-engineer-skills", "DISABLED", "gh issue create"):
        if term not in field_reports_text:
            failures.append(f"scripts/field_reports.py missing {term}")

    github_oracle = "scripts/field_reports_github_oracle.py"
    if not exists(github_oracle):
        failures.append(f"missing GitHub receiver oracle: {github_oracle}")
    else:
        text = read(github_oracle)
        for term in ("tilly-field-report@1", "field-report-quarantine", "validate_body"):
            if term not in text:
                failures.append(f"{github_oracle} missing {term}")

    issue_form = ".github/ISSUE_TEMPLATE/tilly-field-report.yml"
    if not exists(issue_form):
        failures.append(f"missing Field Reports issue form: {issue_form}")
    else:
        text = read(issue_form)
        for term in ("Tilly Field Report", "tilly-field-report@1", "privacy-sanitized", "Never include code"):
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
