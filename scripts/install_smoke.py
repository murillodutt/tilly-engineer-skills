#!/usr/bin/env python3
"""Run deterministic assisted-install smoke probes in temporary projects."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import field_reports
import project_context_oracle
import tes_init


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.79"
ROUTES = ("current", "codex", "claude", "cursor", "all", "mcp", "audit")
PROJECT_CONTEXT_FIXTURES = (
    "fixture-minimal",
    "fixture-docs-only",
    "fixture-npm-app",
    "fixture-python-package",
    "fixture-terraform-docs",
    "fixture-monorepo",
    "fixture-meshed",
    "fixture-owned-bootloaders",
)
CODEX_LOCAL_BOOTLOADER = "Local product governance. Preserve this file.\n"
CLAUDE_LOCAL_BOOTLOADER = "Local product governance. Preserve this file.\n"
HOSTILE_CURSOR_RULE = """---
description: Hostile local Cursor rule for TES governance canary.
alwaysApply: true
---

# Hostile Project Cursor Rule

This file is intentionally project-owned canary setup. TES must not overwrite
or merge it automatically.

Hostile marker: `cursor-local-governance-must-survive`.
"""
STALE_TES_CURSOR_BOOTLOADER = """# Using This Repo With Cursor

This target repository includes a Cursor project rule for Tilly Engineering
Discipline.

## In This Repository

Cursor loads `.cursor/rules/tes-guidelines.mdc`.

## Behavioral Source Of Truth

Keep Cursor, Claude, and Codex variants synchronized at the behavioral level.
"""


def run(command: list[str], cwd: Path = ROOT) -> tuple[int, str, str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def require_paths(target: Path, relpaths: tuple[str, ...]) -> list[str]:
    failures: list[str] = []
    for relpath in relpaths:
        if not (target / relpath).exists():
            failures.append(f"missing path: {relpath}")
    return failures


def init_git(target: Path) -> list[str]:
    code, stdout, stderr = run(["git", "init"], cwd=target)
    if code == 0:
        return []
    return ["git init failed", *stdout.splitlines(), *stderr.splitlines()]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def init_cortex(target: Path) -> list[str]:
    code, stdout, stderr = run(
        [sys.executable, str(ROOT / "scripts/cortex.py"), "init", "--target", str(target)]
    )
    if code == 0:
        return []
    return ["cortex init failed", *stdout.splitlines(), *stderr.splitlines()]


def install_adapter(target: Path, adapter: str, dry_run: bool = False) -> list[str]:
    command = [
        sys.executable,
        str(ROOT / "scripts/install_adapter.py"),
        "--target",
        str(target),
        "--adapter",
        adapter,
        "--yes",
    ]
    if dry_run:
        command.append("--dry-run")
    code, stdout, stderr = run(command)
    if code == 0:
        return []
    return [f"adapter install failed: {adapter}", *stdout.splitlines(), *stderr.splitlines()]


def install_mcp(target: Path, adapter: str, dry_run: bool = False) -> list[str]:
    command = [
        sys.executable,
        str(ROOT / "scripts/install_mcp.py"),
        "--target",
        str(target),
        "--adapter",
        adapter,
        "--yes",
    ]
    if dry_run:
        command.append("--dry-run")
    code, stdout, stderr = run(command)
    if code == 0:
        return []
    return [f"mcp install failed: {adapter}", *stdout.splitlines(), *stderr.splitlines()]


def cortex_gate(target: Path) -> list[str]:
    failures: list[str] = []
    for command in ("verify", "audit", "rebuild", "curate-plan"):
        extra_args = ["--backend", "lexical"] if command == "curate-plan" else []
        code, stdout, stderr = run(
            [sys.executable, str(ROOT / "scripts/cortex.py"), command, "--target", str(target), *extra_args]
        )
        if code != 0:
            failures.extend([f"cortex {command} failed", *stdout.splitlines(), *stderr.splitlines()])
    return failures


def mcp_gate(target: Path) -> list[str]:
    code, stdout, stderr = run(
        [sys.executable, str(target / ".tes/bin/cortex_mcp.py"), "--self-test"],
        cwd=target,
    )
    if code == 0:
        return []
    return ["installed cortex_mcp.py --self-test failed", *stdout.splitlines(), *stderr.splitlines()]


def install_field_reports(target: Path) -> list[str]:
    code, stdout, stderr = run(
        [sys.executable, str(ROOT / "scripts/field_reports.py"), "install-hook", "--target", str(target)]
    )
    failures: list[str] = []
    if code != 0:
        failures.extend(["field reports hook install failed", *stdout.splitlines(), *stderr.splitlines()])
    failures.extend(require_paths(target, (
        ".tes/bin/field_reports.py",
        ".tes/field-reports/outbox.jsonl",
        ".git/hooks/pre-push",
        ".git/info/exclude",
    )))
    exclude_text = (target / ".git/info/exclude").read_text(encoding="utf-8") if (target / ".git/info/exclude").exists() else ""
    for line in field_reports.GIT_EXCLUDE_LINES:
        if line not in exclude_text.splitlines():
            failures.append(f"missing local git hygiene exclude: {line}")
    if (target / ".tes/field-reports/DISABLED").exists():
        failures.append("field reports must be active by default")
    return failures


def expected_adapter_paths(adapter: str) -> tuple[str, ...]:
    if adapter == "codex":
        return (
            "AGENTS.md",
            f".tes/setup/{VERSION}/tes-bundle-manifest.json",
            ".agents/skills/tes-engineering-discipline/SKILL.md",
            ".agents/skills/tes-align/SKILL.md",
            ".agents/skills/tes-open-obsidian/SKILL.md",
        )
    if adapter == "claude":
        return (
            "CLAUDE.md",
            f".tes/setup/{VERSION}/tes-bundle-manifest.json",
            ".claude-plugin/plugin.json",
            "skills/tes-guidelines/SKILL.md",
            ".claude/skills/tes-guidelines/SKILL.md",
            ".claude/skills/tes-init/SKILL.md",
            ".claude/skills/tes-align/SKILL.md",
            ".claude/skills/tes-open-obsidian/SKILL.md",
            "skills/tes-align/SKILL.md",
            "skills/tes-open-obsidian/SKILL.md",
        )
    if adapter == "cursor":
        return (
            "CURSOR.md",
            f".tes/setup/{VERSION}/tes-bundle-manifest.json",
            ".cursor/rules/tes-guidelines.mdc",
            ".cursor/rules/tes-runtime-capabilities.mdc",
        )
    raise ValueError(f"unknown adapter: {adapter}")


def expected_mcp_paths(adapter: str) -> tuple[str, ...]:
    base = (
        ".tes/bin/cortex.py",
        ".tes/bin/cortex_mcp.py",
        ".tes/bin/cortex_embed.mjs",
        ".tes/bin/field_reports.py",
        ".tes/bin/tes_update.py",
        ".tes/bin/tes_legacy_retirement.py",
        ".tes/bin/root_context.py",
        ".tes/bin/tes_init.py",
            ".tes/bin/project_context_oracle.py",
            ".tes/bin/project_alignment_oracle.py",
            ".tes/bin/tes_open_obsidian.py",
            ".tes/bin/command_trigger_oracle.py",
            ".tes/bin/tes_bundle.py",
            ".tes/bin/materialize_adapter.py",
            f".tes/setup/{VERSION}/tes-bundle-manifest.json",
        )
    if adapter == "codex":
        return (*base, ".codex/config.toml")
    if adapter == "claude":
        return (*base, ".mcp.json")
    if adapter == "cursor":
        return (*base, ".cursor/mcp.json")
    if adapter == "all":
        return (*base, ".codex/config.toml", ".mcp.json", ".cursor/mcp.json")
    raise ValueError(f"unknown MCP adapter: {adapter}")


def route_adapters(route: str) -> list[str]:
    if route == "current":
        return ["codex"]
    if route == "all":
        return ["codex", "claude", "cursor"]
    if route in {"codex", "claude", "cursor"}:
        return [route]
    return []


def probe_route(route: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"tes-install-smoke-{route}-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))

        def finish() -> dict[str, Any]:
            status = "FAIL" if failures else "PASS"
            field_reports.safe_record_event(
                target,
                "install_smoke",
                status,
                "installer",
                "self-test",
                details={"route": route, "failures": len(failures)},
            )
            return {"route": route, "status": status, "failures": failures}

        if route == "audit":
            failures.extend(install_adapter(target, "all", dry_run=True))
            failures.extend(install_mcp(target, "all", dry_run=True))
            for unexpected in ("AGENTS.md", "CLAUDE.md", ".tes/bin/cortex_mcp.py"):
                if (target / unexpected).exists():
                    failures.append(f"audit route wrote unexpected path: {unexpected}")
            return finish()

        failures.extend(init_cortex(target))
        failures.extend(install_field_reports(target))

        if route == "mcp":
            failures.extend(install_mcp(target, "all"))
            failures.extend(require_paths(target, expected_mcp_paths("all")))
            failures.extend(mcp_gate(target))
            failures.extend(cortex_gate(target))
            return finish()

        adapters = route_adapters(route)
        adapter_arg = "all" if route == "all" else adapters[0]
        failures.extend(install_adapter(target, adapter_arg))
        failures.extend(install_mcp(target, adapter_arg))
        failures.extend(cortex_gate(target))
        failures.extend(mcp_gate(target))
        for adapter in adapters:
            failures.extend(require_paths(target, expected_adapter_paths(adapter)))
            failures.extend(require_paths(target, expected_mcp_paths(adapter)))

        return finish()


def legacy_retirement_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-legacy-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))
        (target / ".agents/skills/tilly-init").mkdir(parents=True)
        (target / ".agents/skills/tilly-init/SKILL.md").write_text("name: tilly-init\n", encoding="utf-8")
        (target / ".tilly/bin").mkdir(parents=True)
        (target / ".tilly/bin/tilly_update.py").write_text("VERSION = '0.3.1'\n", encoding="utf-8")
        (target / ".tilly/field-reports").mkdir(parents=True)
        (target / ".tilly/field-reports/outbox.jsonl").write_text('{"event":"legacy","status":"PASS"}\n', encoding="utf-8")
        (target / ".codex").mkdir()
        (target / ".codex/config.toml").write_text("[mcp_servers.tilly-cortex]\ncommand = \"python3\"\n", encoding="utf-8")

        code, stdout, stderr = run(
            [sys.executable, str(ROOT / "scripts/tes_legacy_retirement.py"), "audit", "--target", str(target)]
        )
        if code == 0:
            failures.append("legacy retirement audit must fail before apply")
        code, stdout, stderr = run(
            [sys.executable, str(ROOT / "scripts/tes_legacy_retirement.py"), "apply", "--target", str(target), "--yes"]
        )
        if code != 0:
            failures.extend(["legacy retirement apply failed", *stdout.splitlines(), *stderr.splitlines()])
        code, stdout, stderr = run(
            [sys.executable, str(ROOT / "scripts/tes_legacy_retirement.py"), "audit", "--target", str(target)]
        )
        if code != 0:
            failures.extend(["legacy retirement audit failed after apply", *stdout.splitlines(), *stderr.splitlines()])
        for relpath in (".agents/skills/tilly-init", ".tilly/bin", ".tilly/field-reports"):
            if (target / relpath).exists():
                failures.append(f"legacy path still active after retirement: {relpath}")
        if not (target / ".tes/field-reports/outbox.jsonl").exists():
            failures.append("legacy Field Reports outbox was not migrated")
        return {"route": "legacy-retirement", "status": "FAIL" if failures else "PASS", "failures": failures}


def claude_preserved_bootloader_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-claude-preserve-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))
        (target / "CLAUDE.md").write_text(CLAUDE_LOCAL_BOOTLOADER, encoding="utf-8")

        code, stdout, stderr = run(
            [
                sys.executable,
                str(ROOT / "scripts/install_adapter.py"),
                "--target",
                str(target),
                "--adapter",
                "claude",
                "--yes",
            ]
        )
        if code != 0:
            failures.extend(["claude preserve install failed", *stdout.splitlines(), *stderr.splitlines()])
            return {"route": "claude-preserved-bootloader", "status": "FAIL", "failures": failures}

        try:
            payload = json.loads(stdout[stdout.index("{"):stdout.rindex("}") + 1])
        except (ValueError, json.JSONDecodeError) as exc:
            failures.append(f"claude preserve install returned invalid JSON: {exc}")
            payload = {}
        if payload.get("status") != "INSTALLED_WITH_PRESERVED_CONTEXT":
            failures.append("claude preserve install must report INSTALLED_WITH_PRESERVED_CONTEXT")
        preserved = payload.get("preserved_conflicts") or []
        if not any(str(item.get("relpath")) == "CLAUDE.md" for item in preserved):
            failures.append("claude preserve install must preserve conflicting CLAUDE.md")
        if (target / "CLAUDE.md").read_text(encoding="utf-8") != CLAUDE_LOCAL_BOOTLOADER:
            failures.append("claude preserve install overwrote local CLAUDE.md")
        failures.extend(require_paths(target, (
            ".claude/skills/tes-guidelines/SKILL.md",
            ".claude/skills/tes-init/SKILL.md",
            ".claude/skills/tes-align/SKILL.md",
            ".claude/skills/tes-open-obsidian/SKILL.md",
            ".claude/skills/tes-cortex/SKILL.md",
            "skills/tes-guidelines/SKILL.md",
            "skills/tes-init/SKILL.md",
            "skills/tes-align/SKILL.md",
            "skills/tes-open-obsidian/SKILL.md",
            ".claude-plugin/plugin.json",
            f".tes/setup/{VERSION}/tes-bundle-manifest.json",
        )))

        code, stdout, stderr = run(
            [
                sys.executable,
                str(ROOT / "scripts/command_trigger_oracle.py"),
                "--target",
                str(target),
            ]
        )
        if code != 0:
            failures.extend(["installed Claude trigger oracle failed", *stdout.splitlines(), *stderr.splitlines()])

        return {"route": "claude-preserved-bootloader", "status": "FAIL" if failures else "PASS", "failures": failures}


def codex_preserved_bootloader_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-codex-preserve-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))
        (target / "AGENTS.md").write_text(CODEX_LOCAL_BOOTLOADER, encoding="utf-8")
        (target / ".agents/skills/tes-init").mkdir(parents=True)
        (target / ".agents/skills/tes-init/SKILL.md").write_text(
            "# Stale TES Init\n\nMissing current trigger vocabulary.\n",
            encoding="utf-8",
        )

        code, stdout, stderr = run(
            [
                sys.executable,
                str(ROOT / "scripts/install_adapter.py"),
                "--target",
                str(target),
                "--adapter",
                "codex",
                "--yes",
            ]
        )
        if code != 0:
            failures.extend(["codex preserve install failed", *stdout.splitlines(), *stderr.splitlines()])
            return {"route": "codex-preserved-bootloader", "status": "FAIL", "failures": failures}

        try:
            payload = json.loads(stdout[stdout.index("{"):stdout.rindex("}") + 1])
        except (ValueError, json.JSONDecodeError) as exc:
            failures.append(f"codex preserve install returned invalid JSON: {exc}")
            payload = {}
        if payload.get("status") != "INSTALLED_WITH_PRESERVED_CONTEXT":
            failures.append("codex preserve install must report INSTALLED_WITH_PRESERVED_CONTEXT")
        preserved = payload.get("preserved_conflicts") or []
        if not any(str(item.get("relpath")) == "AGENTS.md" for item in preserved):
            failures.append("codex preserve install must preserve conflicting AGENTS.md")
        if (target / "AGENTS.md").read_text(encoding="utf-8") != CODEX_LOCAL_BOOTLOADER:
            failures.append("codex preserve install overwrote local AGENTS.md")
        installed_init = (target / ".agents/skills/tes-init/SKILL.md").read_text(encoding="utf-8")
        if "Missing current trigger vocabulary" in installed_init:
            failures.append("codex preserve install did not repair stale TES-owned skill")
        if "/tes-field-reports" not in installed_init:
            failures.append("repaired Codex tes-init skill must include field reports trigger")
        failures.extend(require_paths(target, (
            ".agents/skills/tes-engineering-discipline/SKILL.md",
            ".agents/skills/tes-init/SKILL.md",
            ".agents/skills/tes-align/SKILL.md",
            ".agents/skills/tes-open-obsidian/SKILL.md",
            ".agents/skills/tes-cortex/SKILL.md",
            ".agents/skills/tes-mcp/SKILL.md",
            f".tes/setup/{VERSION}/tes-bundle-manifest.json",
        )))

        code, stdout, stderr = run(
            [
                sys.executable,
                str(ROOT / "scripts/command_trigger_oracle.py"),
                "--target",
                str(target),
            ]
        )
        if code != 0:
            failures.extend(["installed Codex trigger oracle failed", *stdout.splitlines(), *stderr.splitlines()])

        return {"route": "codex-preserved-bootloader", "status": "FAIL" if failures else "PASS", "failures": failures}


def hostile_governance_conflict_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-hostile-governance-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))
        (target / "AGENTS.md").write_text(CODEX_LOCAL_BOOTLOADER, encoding="utf-8")
        (target / "CLAUDE.md").write_text(CLAUDE_LOCAL_BOOTLOADER, encoding="utf-8")
        (target / "CURSOR.md").write_text(STALE_TES_CURSOR_BOOTLOADER, encoding="utf-8")
        write(target / ".cursor/rules/tes-guidelines.mdc", HOSTILE_CURSOR_RULE)

        code, stdout, stderr = run(
            [
                sys.executable,
                str(ROOT / "scripts/install_adapter.py"),
                "--target",
                str(target),
                "--adapter",
                "all",
                "--yes",
            ]
        )
        if code != 0:
            failures.extend(["hostile governance install failed", *stdout.splitlines(), *stderr.splitlines()])
            return {"route": "hostile-governance-conflict", "status": "FAIL", "failures": failures}

        try:
            payload = json.loads(stdout[stdout.index("{"):stdout.rindex("}") + 1])
        except (ValueError, json.JSONDecodeError) as exc:
            failures.append(f"hostile governance install returned invalid JSON: {exc}")
            payload = {}
        preserved = payload.get("preserved_conflicts") or []
        if payload.get("status") != "INSTALLED_WITH_PRESERVED_CONTEXT":
            failures.append("hostile governance install must report INSTALLED_WITH_PRESERVED_CONTEXT")
        for relpath in ("AGENTS.md", "CLAUDE.md", ".cursor/rules/tes-guidelines.mdc"):
            if not any(str(item.get("relpath")) == relpath for item in preserved):
                failures.append(f"hostile governance install must preserve conflict: {relpath}")
        if any(str(item.get("relpath")) == "CURSOR.md" for item in preserved):
            failures.append("hostile governance install must update TES-owned CURSOR.md")
        if (target / "AGENTS.md").read_text(encoding="utf-8") != CODEX_LOCAL_BOOTLOADER:
            failures.append("hostile governance install overwrote AGENTS.md")
        if (target / "CLAUDE.md").read_text(encoding="utf-8") != CLAUDE_LOCAL_BOOTLOADER:
            failures.append("hostile governance install overwrote CLAUDE.md")
        if (target / ".cursor/rules/tes-guidelines.mdc").read_text(encoding="utf-8") != HOSTILE_CURSOR_RULE:
            failures.append("hostile governance install overwrote Cursor rule")
        cursor_bootloader = (target / "CURSOR.md").read_text(encoding="utf-8")
        if cursor_bootloader == STALE_TES_CURSOR_BOOTLOADER or "/tes-init" not in cursor_bootloader:
            failures.append("hostile governance install did not refresh TES-owned CURSOR.md")
        failures.extend(require_paths(target, (
            ".agents/skills/tes-init/SKILL.md",
            ".agents/skills/tes-align/SKILL.md",
            ".agents/skills/tes-open-obsidian/SKILL.md",
            ".claude/skills/tes-init/SKILL.md",
            ".claude/skills/tes-align/SKILL.md",
            ".claude/skills/tes-open-obsidian/SKILL.md",
            "skills/tes-init/SKILL.md",
            "skills/tes-align/SKILL.md",
            "skills/tes-open-obsidian/SKILL.md",
            "CURSOR.md",
            ".cursor/rules/tes-runtime-capabilities.mdc",
            f".tes/setup/{VERSION}/tes-bundle-manifest.json",
        )))
        return {"route": "hostile-governance-conflict", "status": "FAIL" if failures else "PASS", "failures": failures}


def minimal_fixture(target: Path) -> None:
    write(target / "README.md", "# Minimal Fixture\n")


def docs_only_fixture(target: Path) -> None:
    write(target / "README.md", "# Docs Fixture\n")
    write(target / "docs/overview.md", "# Overview\n\nA docs-only project fixture.\n")
    write(target / "docs/decisions/0001-record-context.md", "# Record Context\n\nUse durable Markdown context.\n")


def npm_app_fixture(target: Path) -> None:
    write(
        target / "package.json",
        json.dumps(
            {
                "name": "tes-npm-fixture",
                "description": "portable npm fixture",
                "scripts": {
                    "lint": "echo lint",
                    "typecheck": "echo typecheck",
                    "test": "echo test",
                    "build": "echo build",
                },
            },
            indent=2,
        )
        + "\n",
    )
    write(target / "README.md", "# TES NPM Fixture\n")
    write(target / "src/index.ts", "export const answer = 42;\n")
    write(target / "tests/index.test.ts", "import { answer } from '../src/index';\nconsole.log(answer);\n")


def python_package_fixture(target: Path) -> None:
    write(target / "README.md", "# TES Python Fixture\n")
    write(
        target / "pyproject.toml",
        "[project]\nname = \"tes-python-fixture\"\nversion = \"0.1.0\"\ndescription = \"portable python fixture\"\n",
    )
    write(target / "src/tes_python_fixture/__init__.py", "__all__ = ['meaning']\n\ndef meaning():\n    return 42\n")
    write(target / "tests/test_meaning.py", "from tes_python_fixture import meaning\n\ndef test_meaning():\n    assert meaning() == 42\n")


def terraform_docs_fixture(target: Path) -> None:
    write(
        target / "README.md",
        "## Learn Terraform Import\n\n"
        "Learn how to import existing resources under Terraform's management.\n\n"
        "```hcl\n# docker_container.web:\nresource \"docker_container\" \"web\" {}\n```\n",
    )
    write(target / "main.tf", 'resource "null_resource" "example" {}\n')
    write(target / "versions.tf", 'terraform { required_version = ">= 1.6.0" }\n')


def monorepo_fixture(target: Path) -> None:
    write(
        target / "package.json",
        json.dumps(
            {
                "name": "tes-monorepo-fixture",
                "private": True,
                "workspaces": ["apps/*", "packages/*"],
                "scripts": {
                    "lint": "echo lint",
                    "test": "echo test",
                    "build": "echo build",
                },
            },
            indent=2,
        )
        + "\n",
    )
    write(target / "README.md", "# TES Monorepo Fixture\n")
    write(target / "apps/web/package.json", '{"name":"web"}\n')
    write(target / "apps/web/src/main.ts", "console.log('web');\n")
    write(target / "packages/core/src/index.ts", "export function core() { return 'core'; }\n")


def meshed_fixture(target: Path) -> None:
    write(target / "README.md", "# Existing Meshed Fixture\n")
    write(target / "docs/agents/PROJECT-REGISTER.md", "# Existing Register\n")
    write(target / "docs/agents/PROJECT-CONTEXT.md", "# Existing Context\n")
    write(target / "src/app.py", "print('meshed')\n")


def owned_bootloaders_fixture(target: Path) -> None:
    write(target / "README.md", "# Owned Bootloaders Fixture\n")
    write(target / "package.json", '{"name":"tes-owned-bootloaders","scripts":{"test":"echo test"}}\n')
    write(target / "AGENTS.md", CODEX_LOCAL_BOOTLOADER)
    write(target / "CLAUDE.md", CLAUDE_LOCAL_BOOTLOADER)
    write(target / "CURSOR.md", "Local Cursor governance. Preserve this file.\n")
    write(target / "src/main.js", "console.log('owned bootloaders');\n")


FIXTURE_BUILDERS = {
    "fixture-minimal": minimal_fixture,
    "fixture-docs-only": docs_only_fixture,
    "fixture-npm-app": npm_app_fixture,
    "fixture-python-package": python_package_fixture,
    "fixture-terraform-docs": terraform_docs_fixture,
    "fixture-monorepo": monorepo_fixture,
    "fixture-meshed": meshed_fixture,
    "fixture-owned-bootloaders": owned_bootloaders_fixture,
}


def project_context_fixture_probe(name: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"tes-install-smoke-{name}-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))
        FIXTURE_BUILDERS[name](target)

        # Avoid recursive install_smoke.py --self-test while this smoke test
        # exercises tes_init's target scan and project-context output.
        original_package_gates = tes_init.package_gates
        tes_init.package_gates = lambda: []
        try:
            init_result = tes_init.initialize(target, yes=True, ensure_cortex=True)
        finally:
            tes_init.package_gates = original_package_gates

        if init_result["status"] != "PASS":
            failures.append(f"tes_init expected PASS, got {init_result['status']}")
            for gate in init_result.get("gates", []):
                if gate.get("status") not in tes_init.PASSING_GATE_STATUSES:
                    failures.append(f"blocked gate: {gate.get('command')} -> {gate.get('status')}")

        context_result = project_context_oracle.analyze(target)
        if context_result["status"] != "PASS":
            failures.extend(f"project context oracle: {failure}" for failure in context_result["failures"])

        for relpath in (
            "docs/agents/PROJECT-REGISTER.md",
            "docs/agents/PROJECT-CONTEXT.md",
            "docs/agents/cortex/CONTRACT.md",
        ):
            if not (target / relpath).exists():
                failures.append(f"fixture missing initialized path: {relpath}")

        return {"route": name, "status": "FAIL" if failures else "PASS", "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=ROUTES, default="all")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    routes = ROUTES if args.self_test else (args.route,)
    results = [probe_route(route) for route in routes]
    if args.self_test:
        results.append(legacy_retirement_probe())
        results.append(codex_preserved_bootloader_probe())
        results.append(claude_preserved_bootloader_probe())
        results.append(hostile_governance_conflict_probe())
        results.extend(project_context_fixture_probe(name) for name in PROJECT_CONTEXT_FIXTURES)
    failures = [
        failure
        for result in results
        for failure in result["failures"]
    ]
    print(json.dumps({"version": VERSION, "status": "FAIL" if failures else "PASS", "routes": results}, indent=2))
    if failures:
        print("[install-smoke] FAIL")
        return 1
    print("[install-smoke] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
