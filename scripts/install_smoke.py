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
VERSION = "0.3.243"
ROUTES = ("current", "codex", "claude", "cursor", "vscode", "all", "mcp", "audit")
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

Cursor loads `.cursor/rules/tes-engineering-discipline.mdc`.

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


def parse_json_stdout(stdout: str) -> dict[str, Any]:
    try:
        return json.loads(stdout[stdout.index("{"):stdout.rindex("}") + 1])
    except (ValueError, json.JSONDecodeError):
        return {}


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
        ".tes/bin/scope_contract.py",
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
            ".agents/skills/tes-update/SKILL.md",
            ".agents/skills/tes-align/SKILL.md",
            ".agents/skills/tes-map/SKILL.md",
            ".agents/skills/tes-open-obsidian/SKILL.md",
            ".agents/skills/tes-field-reports/SKILL.md",
        )
    if adapter == "claude":
        return (
            "CLAUDE.md",
            f".tes/setup/{VERSION}/tes-bundle-manifest.json",
            ".claude/skills/tes-engineering-discipline/SKILL.md",
            ".claude/skills/tes-init/SKILL.md",
            ".claude/skills/tes-update/SKILL.md",
            ".claude/skills/tes-align/SKILL.md",
            ".claude/skills/tes-map/SKILL.md",
            ".claude/skills/tes-open-obsidian/SKILL.md",
            ".claude/skills/tes-field-reports/SKILL.md",
        )
    if adapter == "cursor":
        return (
            "CURSOR.md",
            f".tes/setup/{VERSION}/tes-bundle-manifest.json",
            ".cursor/rules/tes-engineering-discipline.mdc",
            ".cursor/rules/tes-runtime-capabilities.mdc",
        )
    raise ValueError(f"unknown adapter: {adapter}")


def expected_mcp_paths(adapter: str) -> tuple[str, ...]:
    base = (
        ".tes/bin/install_mcp.py",
        ".tes/bin/install_mcp_hosts/__init__.py",
        ".tes/bin/install_mcp_hosts/base.py",
        ".tes/bin/install_mcp_hosts/codex.py",
        ".tes/bin/install_mcp_hosts/claude.py",
        ".tes/bin/install_mcp_hosts/cursor.py",
        ".tes/bin/install_mcp_hosts/vscode.py",
        ".tes/bin/cortex.py",
        ".tes/bin/cortex_runtime.py",
        ".tes/bin/cortex_mcp.py",
        ".tes/bin/cortex_embed.mjs",
        ".tes/bin/scope_contract.py",
        ".tes/bin/event_ledger.py",
        ".tes/bin/checkpoint.py",
        ".tes/bin/consolidation_gate.py",
        ".tes/bin/field_reports.py",
        ".tes/bin/mantra_gate.py",
        ".tes/bin/mantra_gate_adoption_oracle.py",
        ".tes/bin/tes_install.py",
        ".tes/bin/tes_update.py",
        ".tes/bin/tes_legacy_retirement.py",
        ".tes/bin/root_context.py",
            ".tes/bin/tes_init.py",
            ".tes/bin/project_context_oracle.py",
            ".tes/bin/project_alignment_oracle.py",
            ".tes/bin/tes_project_atlas.py",
            ".tes/bin/tes_map.py",
            ".tes/bin/tes_map_oracle.py",
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
    if adapter == "vscode":
        return (*base, ".vscode/mcp.json")
    if adapter == "all":
        return (*base, ".codex/config.toml", ".mcp.json", ".cursor/mcp.json", ".vscode/mcp.json")
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
            for unexpected in ("AGENTS.md", "CLAUDE.md", ".tes/bin/cortex_mcp.py", ".tes/bin/cortex_runtime.py"):
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

        if route == "vscode":
            failures.extend(install_mcp(target, "vscode"))
            failures.extend(require_paths(target, expected_mcp_paths("vscode")))
            failures.extend(mcp_gate(target))
            failures.extend(cortex_gate(target))
            return finish()

        adapters = route_adapters(route)
        adapter_arg = "all" if route == "all" else adapters[0]
        failures.extend(install_adapter(target, adapter_arg))
        failures.extend(install_mcp(target, adapter_arg))
        failures.extend(cortex_gate(target))
        failures.extend(mcp_gate(target))
        if route == "all":
            failures.extend(require_paths(target, expected_mcp_paths("all")))
        for adapter in adapters:
            failures.extend(require_paths(target, expected_adapter_paths(adapter)))
            failures.extend(require_paths(target, expected_mcp_paths(adapter)))

        return finish()


def capsule_install_probe() -> dict[str, Any]:
    """ADR 0004 SPEC-002/005: a default (capsule-only) install writes only .tes/**.

    Build the source bundle, stage it, apply with surfaces={"capsule"}, and assert
    that no project-visible surface (root bootloaders, MCP configs, docs/agents,
    hooks) was written, while the capsule helpers and manifest were.
    """
    import tes_bundle

    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-capsule-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))
        with tempfile.TemporaryDirectory(prefix="tes-capsule-bundle-") as bundle_dir:
            bundle = Path(bundle_dir) / "bundle.zip"
            built = tes_bundle.build_bundle(bundle)
            if built.get("status") not in {"PASS", "BUILT", None} and not bundle.exists():
                failures.append(f"capsule probe could not build bundle: {built.get('status')}")
                return {"route": "capsule-install", "status": "FAIL", "failures": failures}
            stage = tes_bundle.stage_bundle(bundle, target)
            if stage.get("status") != "STAGED":
                failures.append(f"capsule probe stage failed: {stage.get('status')}")
                return {"route": "capsule-install", "status": "FAIL", "failures": failures}
            apply_result = tes_bundle.apply_staged_bundle(
                target, yes=True, mode="preserve", surfaces={"capsule"}
            )
        if apply_result.get("status") not in {"APPLIED", "CLEAN_APPLIED"}:
            failures.append(f"capsule apply unexpected status: {apply_result.get('status')}")

        # Capsule must be present.
        if not (target / ".tes").exists():
            failures.append("capsule-only install did not write .tes/**")

        # No project-visible surface may be written by a capsule-only install.
        forbidden = ("AGENTS.md", "CLAUDE.md", "CURSOR.md", ".mcp.json", ".cursor/mcp.json",
                     ".vscode/mcp.json", ".codex/config.toml", ".claude/settings.json",
                     ".cursor/hooks.json", "docs/agents", ".claude/skills", ".agents/skills")
        for relpath in forbidden:
            if (target / relpath).exists():
                failures.append(f"capsule-only install leaked project-visible surface: {relpath}")

        # Every applied write must resolve inside the target (inbound isolation guard).
        for action in apply_result.get("actions", []):
            path = str(action.get("path") or "")
            if path and (Path(path).is_absolute() or ".." in Path(path).parts):
                failures.append(f"capsule apply wrote outside target: {path}")

        status = "FAIL" if failures else "PASS"
        field_reports.safe_record_event(
            target, "install_smoke", status, "installer", "self-test",
            details={"route": "capsule-install", "failures": len(failures)},
        )
        return {"route": "capsule-install", "status": status, "failures": failures}


def reversibility_roundtrip_probe() -> dict[str, Any]:
    """ADR 0004 SPEC-005: install (all surfaces) then uninstall returns to pre-install.

    Snapshot project-owned files, install with every surface attached, uninstall,
    then assert: project-owned files are byte-identical, the residue oracle reports
    PASS (zero active residue), .tes/** is gone, and no write resolved outside the
    target (inbound isolation guard).
    """
    import tes_bundle
    import capsule_residue_oracle

    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-roundtrip-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))

        # Project-owned files, including a pre-existing bootloader with project content.
        owned = {
            "README.md": "# Roundtrip Project\nimportant project content\n",
            "src/app.py": "print('hello')\n",
            "AGENTS.md": "# Project AGENTS\nproject-owned governance must survive\n",
        }
        for relpath, text in owned.items():
            write(target / relpath, text)
        snapshot = {relpath: (target / relpath).read_text(encoding="utf-8") for relpath in owned}

        all_surfaces = {"capsule", "mcp", "docs-mesh", "root-context", "skills", "hooks",
                        "field-reports", "gps", "goals", "mantra"}
        with tempfile.TemporaryDirectory(prefix="tes-roundtrip-bundle-") as bundle_dir:
            bundle = Path(bundle_dir) / "bundle.zip"
            tes_bundle.build_bundle(bundle)
            stage = tes_bundle.stage_bundle(bundle, target)
            if stage.get("status") != "STAGED":
                failures.append(f"roundtrip stage failed: {stage.get('status')}")
                return {"route": "reversibility-roundtrip", "status": "FAIL", "failures": failures}
            tes_bundle.apply_staged_bundle(target, yes=True, mode="preserve", surfaces=all_surfaces)

        uninstall = tes_bundle.uninstall_capsule(target, yes=True)
        if uninstall.get("status") not in {"UNINSTALLED"}:
            failures.append(f"roundtrip uninstall status: {uninstall.get('status')}; review={uninstall.get('review_items')}")

        # No write resolved outside the target.
        for action in uninstall.get("actions", []):
            path = str(action.get("path") or "")
            if path and (Path(path).is_absolute() or ".." in Path(path).parts):
                failures.append(f"uninstall acted outside target: {path}")

        # Project-owned files byte-identical (AGENTS.md keeps project content, no TES block).
        for relpath in ("README.md", "src/app.py"):
            if not (target / relpath).exists() or (target / relpath).read_text(encoding="utf-8") != snapshot[relpath]:
                failures.append(f"roundtrip did not restore project-owned file byte-identical: {relpath}")
        agents_text = (target / "AGENTS.md").read_text(encoding="utf-8") if (target / "AGENTS.md").exists() else ""
        if "TES:CORE" in agents_text:
            failures.append("roundtrip left a TES:CORE block in AGENTS.md")
        if "project-owned governance must survive" not in agents_text:
            failures.append("roundtrip destroyed project content in AGENTS.md")

        # Zero active residue and capsule removed.
        residue = capsule_residue_oracle.evaluate(target)
        if residue["status"] != "PASS":
            failures.append(f"roundtrip left active residue: {residue['active_residue']}")
        if (target / ".tes").exists():
            failures.append("roundtrip did not remove the capsule (.tes/**)")

        status = "FAIL" if failures else "PASS"
        field_reports.safe_record_event(
            target, "install_smoke", status, "installer", "self-test",
            details={"route": "reversibility-roundtrip", "failures": len(failures)},
        )
        return {"route": "reversibility-roundtrip", "status": status, "failures": failures}


def attach_detach_roundtrip_probe() -> dict[str, Any]:
    """ADR 0004 L2 SPEC-006: attach a surface then detach it returns to prior state.

    Capsule install, attach root-context (a manifest-backed surface), assert the
    TES:CORE block is present and attach-health/residue agree, detach it, then
    assert the surface is gone, the project's bootloader content survives, and the
    capsule plus residue are intact.
    """
    import tes_bundle
    import capsule_residue_oracle
    import attach_health_oracle

    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-attach-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))
        write(target / "AGENTS.md", "# Project AGENTS\nproject governance survives\n")
        snapshot = (target / "AGENTS.md").read_text(encoding="utf-8")

        # Capsule-only install (no project-visible surface yet).
        with tempfile.TemporaryDirectory(prefix="tes-attach-bundle-") as bundle_dir:
            bundle = Path(bundle_dir) / "bundle.zip"
            tes_bundle.build_bundle(bundle)
            stage = tes_bundle.stage_bundle(bundle, target)
            if stage.get("status") != "STAGED":
                failures.append(f"attach probe stage failed: {stage.get('status')}")
                return {"route": "attach-detach-roundtrip", "status": "FAIL", "failures": failures}
            tes_bundle.apply_staged_bundle(target, yes=True, mode="preserve", surfaces={"capsule"})
        if (target / "AGENTS.md").read_text(encoding="utf-8") != snapshot:
            failures.append("capsule-only install must not touch the project bootloader")

        # Attach root-context.
        tes_bundle.apply_staged_bundle(target, yes=True, mode="preserve", surfaces={"capsule", "root-context"})
        if "TES:CORE" not in (target / "AGENTS.md").read_text(encoding="utf-8"):
            failures.append("attach root-context must compose the TES:CORE block")
        rc_health = attach_health_oracle.evaluate(target, "root-context")
        if rc_health["status"] != "PASS":
            failures.append(f"attached root-context health must be PASS: {rc_health['status']}")

        # Detach root-context.
        detach = tes_bundle.detach_surface(target, "root-context", yes=True)
        if detach.get("status") != "DETACHED":
            failures.append(f"detach root-context status: {detach.get('status')}")
        agents_text = (target / "AGENTS.md").read_text(encoding="utf-8") if (target / "AGENTS.md").exists() else ""
        if "TES:CORE" in agents_text:
            failures.append("detach must remove the TES:CORE block")
        if "project governance survives" not in agents_text:
            failures.append("detach must keep the project's bootloader content")
        if not (target / ".tes").exists():
            failures.append("detach must keep the capsule")

        # No action resolved outside the target.
        for action in detach.get("actions", []):
            path = str(action.get("path") or "")
            if path and (Path(path).is_absolute() or ".." in Path(path).parts):
                failures.append(f"detach acted outside target: {path}")

        status = "FAIL" if failures else "PASS"
        field_reports.safe_record_event(
            target, "install_smoke", status, "installer", "self-test",
            details={"route": "attach-detach-roundtrip", "failures": len(failures)},
        )
        return {"route": "attach-detach-roundtrip", "status": status, "failures": failures}


def skills_surface_probe() -> dict[str, Any]:
    """ADR 0004 (skills-surface line) SPEC-005: skills are a decoupled, reversible
    surface.

    Three proofs in one round-trip:
    1. Decoupling: attaching only `skills` materializes the project skill command
       set but NOT the root bootloaders (skills are not root-context).
    2. Health: the skills surface reports PASS once materialized.
    3. Reversibility: detaching `skills` removes the skill tree residue-clean
       (no empty directory shells) and keeps the capsule and other surfaces.
    """
    import tes_bundle
    import capsule_residue_oracle
    import attach_health_oracle

    skill_marker = ".claude/skills/tes-map/SKILL.md"
    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-skills-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))

        with tempfile.TemporaryDirectory(prefix="tes-skills-bundle-") as bundle_dir:
            bundle = Path(bundle_dir) / "bundle.zip"
            tes_bundle.build_bundle(bundle)
            stage = tes_bundle.stage_bundle(bundle, target)
            if stage.get("status") != "STAGED":
                failures.append(f"skills probe stage failed: {stage.get('status')}")
                return {"route": "skills-surface", "status": "FAIL", "failures": failures}
            # Attach ONLY skills (plus the always-present capsule).
            tes_bundle.apply_staged_bundle(target, yes=True, mode="preserve", surfaces={"capsule", "skills"})

        # 1. Decoupling: skills present, bootloaders/rules absent.
        if not (target / skill_marker).exists():
            failures.append("attach skills must materialize the project skill command set")
        for bootloader in ("CLAUDE.md", "AGENTS.md", "CURSOR.md", ".cursor/rules/tes-engineering-discipline.mdc"):
            if (target / bootloader).exists():
                failures.append(f"attach skills must NOT materialize a root-context surface: {bootloader}")

        # 2. Health: skills surface reports PASS.
        sk_health = attach_health_oracle.evaluate(target, "skills")
        if sk_health["status"] != "PASS":
            failures.append(f"attached skills health must be PASS: {sk_health['status']}")

        # 3. Reversibility: detach skills, residue-clean, capsule kept.
        detach = tes_bundle.detach_surface(target, "skills", yes=True)
        if detach.get("status") != "DETACHED":
            failures.append(f"detach skills status: {detach.get('status')}")
        for skills_root in (".claude/skills", ".agents/skills"):
            root = target / skills_root
            if root.exists() and any(p.is_file() for p in root.rglob("*")):
                failures.append(f"detach skills left files under {skills_root}")
            if root.exists():
                failures.append(f"detach skills left an empty directory shell: {skills_root}")
        if not (target / ".tes").exists():
            failures.append("detach skills must keep the capsule")
        sk_health_after = attach_health_oracle.evaluate(target, "skills")
        if sk_health_after["status"] != "NOT_APPLIED":
            failures.append(f"detached skills health must be NOT_APPLIED: {sk_health_after['status']}")

        # No action resolved outside the target.
        for action in detach.get("actions", []):
            path = str(action.get("path") or "")
            if path and (Path(path).is_absolute() or ".." in Path(path).parts):
                failures.append(f"detach skills acted outside target: {path}")

        status = "FAIL" if failures else "PASS"
        field_reports.safe_record_event(
            target, "install_smoke", status, "installer", "self-test",
            details={"route": "skills-surface", "failures": len(failures)},
        )
        return {"route": "skills-surface", "status": status, "failures": failures}


def runtime_surface_roundtrip_probe() -> dict[str, Any]:
    """ADR 0004 L3 SPEC-006: attach then detach each runtime surface returns to prior state.

    For mcp and hooks: install the writer alongside a user-owned neighbor, detach
    via detach_surface, assert the TES surface is gone and the neighbor survived.
    For docs-mesh: attach (tes_init), detach (preserve), assert project content
    survives.
    """
    import tes_bundle
    import tes_install
    import install_mcp

    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-runtime-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))
        (target / ".tes/bin").mkdir(parents=True)
        (target / ".tes/bin/cortex_mcp.py").write_text("# server\n", encoding="utf-8")
        write(target / ".tes/manifest.json",
              json.dumps({"schema": "tes-bundle-manifest@2", "entries": []}))

        # MCP: install alongside a user server, detach, assert neighbor survives.
        write(target / ".mcp.json", json.dumps({"mcpServers": {"user-srv": {"command": "u"}}}))
        install_mcp.install_configs(target, ["claude"], False, True, True, False)
        if "tes-cortex" not in (target / ".mcp.json").read_text(encoding="utf-8"):
            failures.append("mcp attach did not write tes-cortex")
        d_mcp = tes_bundle.detach_surface(target, "mcp", yes=True)
        if d_mcp.get("status") != "DETACHED":
            failures.append(f"mcp detach status: {d_mcp.get('status')}")
        mcp_text = (target / ".mcp.json").read_text(encoding="utf-8") if (target / ".mcp.json").exists() else ""
        if "tes-cortex" in mcp_text:
            failures.append("mcp detach left tes-cortex")
        if "user-srv" not in mcp_text:
            failures.append("mcp detach dropped the user server (not writer-inverse)")

        # Hooks: install alongside a user cursor hook, detach, assert it survives.
        tes_install.install_cursor_hook(target, False)
        cj = json.loads((target / ".cursor/hooks.json").read_text(encoding="utf-8"))
        cj["hooks"].setdefault("sessionStart", []).append({"command": "user-hook", "timeout": 5})
        write(target / ".cursor/hooks.json", json.dumps(cj, indent=2, sort_keys=True) + "\n")
        d_hooks = tes_bundle.detach_surface(target, "hooks", yes=True)
        if d_hooks.get("status") != "DETACHED":
            failures.append(f"hooks detach status: {d_hooks.get('status')}")
        cj_text = (target / ".cursor/hooks.json").read_text(encoding="utf-8") if (target / ".cursor/hooks.json").exists() else ""
        if "tes_install.py hook --agent cursor" in cj_text:
            failures.append("hooks detach left the TES cursor hook")
        if "user-hook" not in cj_text:
            failures.append("hooks detach dropped the user hook (not writer-inverse)")

        # docs-mesh: a project-authored file plus a generated file; detach preserves
        # by default; purge removes only generated.
        (target / "docs/agents/evidence").mkdir(parents=True)
        write(target / "docs/agents/PROJECT-CONTEXT.md", "# ctx\n")
        write(target / "docs/agents/MY-NOTES.md", "# project authored\n")
        d_docs = tes_bundle.detach_surface(target, "docs-mesh", yes=True)
        if d_docs.get("status") != "DETACHED":
            failures.append(f"docs-mesh detach status: {d_docs.get('status')}")
        if not (target / "docs/agents/MY-NOTES.md").exists():
            failures.append("docs-mesh default detach removed project content")
        purged = tes_bundle.detach_docs_mesh(target, yes=True, purge=True)
        if not (target / "docs/agents/MY-NOTES.md").exists():
            failures.append("docs-mesh purge removed project-authored content")
        if (target / "docs/agents/PROJECT-CONTEXT.md").exists():
            failures.append("docs-mesh purge did not remove the generated file")

        status = "FAIL" if failures else "PASS"
        field_reports.safe_record_event(
            target, "install_smoke", status, "installer", "self-test",
            details={"route": "runtime-surface-roundtrip", "failures": len(failures)},
        )
        return {"route": "runtime-surface-roundtrip", "status": status, "failures": failures}


def gps_capsule_mode_probe() -> dict[str, Any]:
    """ADR 0004 L4 SPEC-006: GPS works in capsule mode and exports when attached.

    Capsule-only: map yields a useful CAPSULE_PASS position and writes .tes/gps/**
    with no docs/agents export. Attach docs-mesh (a populated docs/agents): export
    the managed block. Detach docs/agents: capsule projection still works.
    """
    import tes_map

    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-gps-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))
        write(target / ".tes/postinstall.json",
              json.dumps({"state": "complete", "last_status": "PASS", "version": tes_map.VERSION}))

        # Capsule-only: useful position, .tes/gps written, no docs export.
        model = tes_map.build_model(target)
        if model.get("mode") != "capsule" or model["status"] != tes_map.STATUS_CAPSULE_PASS:
            failures.append(f"capsule-only map not CAPSULE_PASS: mode={model.get('mode')} status={model['status']}")
        if not model["position"]:
            failures.append("capsule-only map produced no position")
        tes_map.write_capsule_projection(target, tes_map.build_capsule_projection(target))
        if not (target / tes_map.GPS_STATE_REL).exists():
            failures.append("capsule map did not write .tes/gps/state.json")
        if (target / "docs/agents").exists():
            failures.append("capsule map leaked docs/agents (export must be gated)")

        # Attached: populated docs/agents -> attached mode + export the block.
        tes_map.create_fixture(target)  # writes docs/agents + roadmap
        attached_model = tes_map.build_model(target)
        if attached_model.get("mode") != "attached":
            failures.append("populated docs/agents did not switch to attached mode")
        export = tes_map.update_roadmap(target, attached_model)
        roadmap_text = (target / tes_map.ROADMAP_REL).read_text(encoding="utf-8")
        if tes_map.START_MARKER not in roadmap_text:
            failures.append("attached export did not write the managed TES-MAP block")

        # Detach docs/agents: capsule projection still produces a useful position.
        import shutil as _shutil
        _shutil.rmtree(target / "docs/agents")
        after_detach = tes_map.build_model(target)
        if after_detach.get("mode") != "capsule" or after_detach["status"] != tes_map.STATUS_CAPSULE_PASS:
            failures.append("after docs detach, capsule map did not stay useful")

        status = "FAIL" if failures else "PASS"
        field_reports.safe_record_event(
            target, "install_smoke", status, "installer", "self-test",
            details={"route": "gps-capsule-mode", "failures": len(failures)},
        )
        return {"route": "gps-capsule-mode", "status": status, "failures": failures}


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
        (target / ".tes/hooks").mkdir(parents=True)
        (target / ".tes/hooks/executed.jsonl").write_text(
            '{"agent":"codex","event":"PreToolUse","session":"legacy","ts":"2026-06-26T00:00:00Z"}\n',
            encoding="utf-8",
        )
        (target / ".tes/runtime/hooks").mkdir(parents=True)
        duplicate_record = '{"agent":"codex","decision":"allow","event":"PreToolUse","mode":"pretooluse","session":"smoke-duplicate","ts":"2026-06-27T00:00:00Z"}'
        (target / ".tes/runtime/hooks/executed.jsonl").write_text(
            duplicate_record + "\n" + duplicate_record + "\n",
            encoding="utf-8",
        )
        (target / ".tes/runtime/hook-smoke/cursor").mkdir(parents=True)
        (target / ".tes/runtime/hook-smoke/cursor/SKILL.md").write_text("# Cursor Smoke\n", encoding="utf-8")
        (target / ".tes/runtime/hook-smoke/run_contract_sim.py").write_text("print('residue')\n", encoding="utf-8")
        (target / ".tes/runtime/hook-smoke/forbidden-executed.txt").write_text("EXECUTED\n", encoding="utf-8")

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
        if (target / ".tes/hooks/executed.jsonl").exists():
            failures.append("legacy hook ledger was not archived")
        if not (target / ".tes/legacy-retirement/hooks/executed.jsonl").exists():
            failures.append("legacy hook ledger archive is missing")
        hook_rows = (target / ".tes/runtime/hooks/executed.jsonl").read_text(encoding="utf-8").splitlines()
        if len(hook_rows) != 1:
            failures.append("runtime hook ledger exact duplicates were not compacted")
        if (target / ".tes/runtime/hook-smoke/run_contract_sim.py").exists():
            failures.append("legacy hook audit harness script was not removed")
        if (target / ".tes/runtime/hook-smoke/forbidden-executed.txt").exists():
            failures.append("legacy forbidden shell residue was not removed")
        if not (target / ".tes/runtime/hook-smoke/cursor/SKILL.md").exists():
            failures.append("hook smoke evidence file must be preserved")
        return {"route": "legacy-retirement", "status": "FAIL" if failures else "PASS", "failures": failures}


def claude_clean_bootloader_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-claude-clean-") as tempdir:
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
            failures.extend(["claude clean install failed", *stdout.splitlines(), *stderr.splitlines()])
            return {"route": "claude-clean-bootloader", "status": "FAIL", "failures": failures}

        try:
            payload = json.loads(stdout[stdout.index("{"):stdout.rindex("}") + 1])
        except (ValueError, json.JSONDecodeError) as exc:
            failures.append(f"claude clean install returned invalid JSON: {exc}")
            payload = {}
        if payload.get("status") != "INSTALLED_CLEAN_RUNTIME":
            failures.append("claude clean install must report INSTALLED_CLEAN_RUNTIME")
        backup = payload.get("clean_backup") or {}
        backup_id = str(backup.get("backup_id") or "")
        if not backup_id or not (target / ".tes/bk" / backup_id / "manifest.json").exists():
            failures.append("claude clean install must create central backup")
        if CLAUDE_LOCAL_BOOTLOADER in (target / "CLAUDE.md").read_text(encoding="utf-8"):
            failures.append("claude clean install did not replace local CLAUDE.md")
        recovery = payload.get("semantic_recovery") or {}
        if recovery.get("status") not in {"RECOVERED", "NEEDS_REVIEW"}:
            failures.append("claude clean install must emit semantic recovery")
        failures.extend(require_paths(target, (
            ".claude/skills/tes-engineering-discipline/SKILL.md",
            ".claude/skills/tes-init/SKILL.md",
            ".claude/skills/tes-update/SKILL.md",
            ".claude/skills/tes-align/SKILL.md",
            ".claude/skills/tes-open-obsidian/SKILL.md",
            ".claude/skills/tes-cortex/SKILL.md",
            ".claude/skills/tes-field-reports/SKILL.md",
            f".tes/setup/{VERSION}/tes-bundle-manifest.json",
        )))
        for relpath in ("skills", ".claude-plugin"):
            if (target / relpath).exists():
                failures.append(f"claude clean install wrote source-only plugin artifact: {relpath}")

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

        return {"route": "claude-clean-bootloader", "status": "FAIL" if failures else "PASS", "failures": failures}


def codex_clean_bootloader_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-codex-clean-") as tempdir:
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
            failures.extend(["codex clean install failed", *stdout.splitlines(), *stderr.splitlines()])
            return {"route": "codex-clean-bootloader", "status": "FAIL", "failures": failures}

        try:
            payload = json.loads(stdout[stdout.index("{"):stdout.rindex("}") + 1])
        except (ValueError, json.JSONDecodeError) as exc:
            failures.append(f"codex clean install returned invalid JSON: {exc}")
            payload = {}
        if payload.get("status") != "INSTALLED_CLEAN_RUNTIME":
            failures.append("codex clean install must report INSTALLED_CLEAN_RUNTIME")
        backup = payload.get("clean_backup") or {}
        backup_id = str(backup.get("backup_id") or "")
        if not backup_id or not (target / ".tes/bk" / backup_id / "manifest.json").exists():
            failures.append("codex clean install must create central backup")
        if CODEX_LOCAL_BOOTLOADER in (target / "AGENTS.md").read_text(encoding="utf-8"):
            failures.append("codex clean install did not replace local AGENTS.md")
        recovery = payload.get("semantic_recovery") or {}
        if recovery.get("status") not in {"RECOVERED", "NEEDS_REVIEW"}:
            failures.append("codex clean install must emit semantic recovery")
        installed_init = (target / ".agents/skills/tes-init/SKILL.md").read_text(encoding="utf-8")
        if "Missing current trigger vocabulary" in installed_init:
            failures.append("codex clean install did not repair stale TES-owned skill")
        if "/tes-field-reports" not in installed_init:
            failures.append("repaired Codex tes-init skill must include field reports trigger")
        failures.extend(require_paths(target, (
            ".agents/skills/tes-engineering-discipline/SKILL.md",
            ".agents/skills/tes-init/SKILL.md",
            ".agents/skills/tes-update/SKILL.md",
            ".agents/skills/tes-align/SKILL.md",
            ".agents/skills/tes-open-obsidian/SKILL.md",
            ".agents/skills/tes-cortex/SKILL.md",
            ".agents/skills/tes-mcp/SKILL.md",
            ".agents/skills/tes-field-reports/SKILL.md",
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

        return {"route": "codex-clean-bootloader", "status": "FAIL" if failures else "PASS", "failures": failures}


def hostile_governance_conflict_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-hostile-governance-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))
        (target / "AGENTS.md").write_text(CODEX_LOCAL_BOOTLOADER, encoding="utf-8")
        (target / "CLAUDE.md").write_text(CLAUDE_LOCAL_BOOTLOADER, encoding="utf-8")
        (target / "CURSOR.md").write_text(STALE_TES_CURSOR_BOOTLOADER, encoding="utf-8")
        write(target / ".cursor/rules/tes-engineering-discipline.mdc", HOSTILE_CURSOR_RULE)

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
        if payload.get("status") != "INSTALLED_CLEAN_RUNTIME":
            failures.append("hostile governance install must report INSTALLED_CLEAN_RUNTIME")
        backup = payload.get("clean_backup") or {}
        backup_id = str(backup.get("backup_id") or "")
        if not backup_id or not (target / ".tes/bk" / backup_id / "files/AGENTS.md").exists():
            failures.append("hostile governance install must backup AGENTS.md centrally")
        if CODEX_LOCAL_BOOTLOADER in (target / "AGENTS.md").read_text(encoding="utf-8"):
            failures.append("hostile governance install did not replace AGENTS.md")
        if CLAUDE_LOCAL_BOOTLOADER in (target / "CLAUDE.md").read_text(encoding="utf-8"):
            failures.append("hostile governance install did not replace CLAUDE.md")
        if HOSTILE_CURSOR_RULE in (target / ".cursor/rules/tes-engineering-discipline.mdc").read_text(encoding="utf-8"):
            failures.append("hostile governance install did not replace Cursor rule")
        cursor_bootloader = (target / "CURSOR.md").read_text(encoding="utf-8")
        if cursor_bootloader == STALE_TES_CURSOR_BOOTLOADER or "/tes-init" not in cursor_bootloader:
            failures.append("hostile governance install did not refresh TES-owned CURSOR.md")
        failures.extend(require_paths(target, (
            ".agents/skills/tes-init/SKILL.md",
            ".agents/skills/tes-update/SKILL.md",
            ".agents/skills/tes-align/SKILL.md",
            ".agents/skills/tes-open-obsidian/SKILL.md",
            ".agents/skills/tes-field-reports/SKILL.md",
            ".claude/skills/tes-init/SKILL.md",
            ".claude/skills/tes-update/SKILL.md",
            ".claude/skills/tes-align/SKILL.md",
            ".claude/skills/tes-open-obsidian/SKILL.md",
            ".claude/skills/tes-field-reports/SKILL.md",
            "CURSOR.md",
            ".cursor/rules/tes-runtime-capabilities.mdc",
            f".tes/setup/{VERSION}/tes-bundle-manifest.json",
        )))
        for relpath in ("skills", ".claude-plugin", ".agents/plugins", "plugins/tilly-engineer-skills"):
            if (target / relpath).exists():
                failures.append(f"all install wrote source-only plugin artifact: {relpath}")
        return {"route": "hostile-governance-conflict", "status": "FAIL" if failures else "PASS", "failures": failures}


def legacy_obsolete_cleanup_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-obsolete-clean-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        retired_guidelines = "tes-" + "guidelines"
        failures.extend(init_git(target))
        write(target / "README.md", "# Legacy TES Install\n")
        write(target / "skills/tes-init/SKILL.md", "# TES Init\n\nTilly Engineering /tes-init legacy root skill.\n")
        write(target / f"skills/{retired_guidelines}/SKILL.md", "# Tilly Guidelines\n\nTES legacy root discipline skill.\n")
        write(target / f".claude/skills/{retired_guidelines}/SKILL.md", "# Tilly Guidelines\n\nTES legacy Claude discipline skill.\n")
        write(target / f".cursor/rules/{retired_guidelines}.mdc", "---\nalwaysApply: true\n---\n# TES legacy Cursor guideline rule\n")
        write(target / ".claude-plugin/plugin.json", '{"name":"tilly-engineer-skills","version":"0.3.112","skills":["./skills/"]}\n')
        write(target / ".agents/plugins/marketplace.json", '{"plugins":[{"id":"tilly-engineer-skills","version":"0.3.112"}]}\n')
        write(target / "plugins/tilly-engineer-skills/.codex-plugin/plugin.json", '{"name":"tilly-engineer-skills","version":"0.3.112","skills":"./skills/"}\n')

        # ADR 0004: this probe certifies the legacy install-all obsolete-cleanup
        # flow, which is now the explicit --attach all profile.
        code, stdout, stderr = run(
            [
                sys.executable,
                str(ROOT / "scripts/tes_install.py"),
                "install",
                "--target",
                str(target),
                "--agent",
                "all",
                "--attach",
                "all",
                "--yes",
            ]
        )
        if code != 0:
            failures.extend(["legacy obsolete cleanup install failed", *stdout.splitlines(), *stderr.splitlines()])
            return {"route": "legacy-obsolete-cleanup", "status": "FAIL", "failures": failures}
        payload = parse_json_stdout(stdout)
        # Ceiling: a clean install whose only open findings are host-readiness
        # pending (MCP/host not restarted, hooks not yet fired) reports the typed
        # tier READY_PENDING_HOST instead of INSTALLED — both are a successful,
        # reversible on-disk install (exit 0).
        if payload.get("status") not in {"INSTALLED", "READY_PENDING_HOST"}:
            failures.append(f"legacy obsolete cleanup expected INSTALLED/READY_PENDING_HOST, got {payload.get('status')}")
        cleanup = ((payload.get("apply") or {}).get("obsolete_cleanup") or {})
        if cleanup.get("status") not in {"PASS", "DRY-RUN"}:
            failures.append(f"legacy obsolete cleanup expected PASS cleanup, got {cleanup.get('status')}")
        for relpath in ("skills", ".claude-plugin", ".agents/plugins", "plugins/tilly-engineer-skills", f".claude/skills/{retired_guidelines}", f".cursor/rules/{retired_guidelines}.mdc"):
            if (target / relpath).exists():
                failures.append(f"legacy TES-owned obsolete path was not removed: {relpath}")
        failures.extend(require_paths(target, (
            ".agents/skills/tes-init/SKILL.md",
            ".claude/skills/tes-init/SKILL.md",
            ".cursor/rules/tes-runtime-capabilities.mdc",
            ".tes/manifest.json",
        )))
        return {"route": "legacy-obsolete-cleanup", "status": "FAIL" if failures else "PASS", "failures": failures}


def ambiguous_obsolete_review_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tes-install-smoke-obsolete-review-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))
        write(target / "README.md", "# Ambiguous Legacy TES Install\n")
        write(target / "skills/custom/SKILL.md", "# Custom Skill\n\n" + "USER_" + "TOKEN=keep-me\n")

        # ADR 0004: certifies the legacy install-all ambiguous-obsolete review
        # flow (sentinel + review backup), now the explicit --attach all profile.
        code, stdout, stderr = run(
            [
                sys.executable,
                str(ROOT / "scripts/tes_install.py"),
                "install",
                "--target",
                str(target),
                "--agent",
                "all",
                "--attach",
                "all",
                "--yes",
            ]
        )
        if code != 0:
            failures.extend(["ambiguous obsolete review install failed", *stdout.splitlines(), *stderr.splitlines()])
            return {"route": "ambiguous-obsolete-review", "status": "FAIL", "failures": failures}
        payload = parse_json_stdout(stdout)
        if payload.get("status") != "NEEDS_REVIEW":
            failures.append(f"ambiguous obsolete cleanup expected NEEDS_REVIEW, got {payload.get('status')}")
        if not (target / "skills/custom/SKILL.md").exists():
            failures.append("ambiguous root skills content was deleted")
        sentinel = json.loads((target / ".tes/postinstall.json").read_text(encoding="utf-8"))
        if sentinel.get("state") != "needs_review":
            failures.append("ambiguous obsolete cleanup must mark postinstall needs_review")
        cleanup = ((payload.get("apply") or {}).get("obsolete_cleanup") or {})
        backup = cleanup.get("review_backup") if isinstance(cleanup.get("review_backup"), dict) else {}
        backup_id = str(backup.get("backup_id") or "")
        if not backup_id or not (target / ".tes/bk" / backup_id / "manifest.json").exists():
            failures.append("ambiguous obsolete cleanup did not create review backup")
        if backup_id and not (target / f".tes/bk/{backup_id}/files/skills/custom/SKILL.md").exists():
            failures.append("ambiguous obsolete cleanup backup missing custom skill")
        failures.extend(require_paths(target, (
            ".agents/skills/tes-init/SKILL.md",
            ".claude/skills/tes-init/SKILL.md",
            ".tes/manifest.json",
        )))
        return {"route": "ambiguous-obsolete-review", "status": "FAIL" if failures else "PASS", "failures": failures}


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
        results.append(capsule_install_probe())
        results.append(reversibility_roundtrip_probe())
        results.append(attach_detach_roundtrip_probe())
        results.append(skills_surface_probe())
        results.append(runtime_surface_roundtrip_probe())
        results.append(gps_capsule_mode_probe())
        results.append(legacy_retirement_probe())
        results.append(codex_clean_bootloader_probe())
        results.append(claude_clean_bootloader_probe())
        results.append(hostile_governance_conflict_probe())
        results.append(legacy_obsolete_cleanup_probe())
        results.append(ambiguous_obsolete_review_probe())
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
