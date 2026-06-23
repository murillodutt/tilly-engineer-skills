#!/usr/bin/env python3
"""Prove a target has zero active TES residue (ADR 0004, SPEC-004).

After `tes_install uninstall`, no live TES surface may remain: no capsule
(`.tes/**`), no TES:CORE block in a root bootloader, no TES hook entry in a host
config, and no `tes-cortex` MCP server registration. The oracle distinguishes
*active* residue (a live route or capsule state) from *inert retained* exports
the user explicitly chose to keep. Active residue fails; inert retained exports
are reported, not failed.

Detectors reuse the governed markers the installer writes, not brittle literal
lists: TES:CORE block markers from root_context, the MCP server name, and the
hook command token. Returns the ADR 0003.1 vocabulary
(PASS / PARTIAL / NEEDS_REVIEW / BLOCKED).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

import root_context


VERSION = "0.3.185"

# Governed surface markers (kept in sync with the installer writers).
MCP_SERVER_NAME = "tes-cortex"
HOOK_COMMAND_TOKENS = ("tes_install.py hook", ".tes/bin/tes_install.py")
ROOT_BOOTLOADERS = ("AGENTS.md", "CLAUDE.md", "CURSOR.md")
MCP_CONFIG_PATHS = (".mcp.json", ".cursor/mcp.json", ".vscode/mcp.json", ".codex/config.toml")
HOOK_CONFIG_PATHS = (".codex/config.toml", ".claude/settings.json", ".cursor/hooks.json")
PROJECT_VISIBLE_RUNTIME_ROOTS = (
    ".agents/skills",
    ".claude/skills",
    ".cursor/rules",
)
SHELL_DIRS = (".agents", ".claude", ".cursor", ".codex")
# docs-mesh is the only project-visible surface outside the capsule besides root
# bootloaders. field-reports and mantra-gates live inside .tes/** (covered by the
# capsule detector). gps/goals are not yet produced by any writer.
DOCS_MESH_ROOT = "docs/agents"
# A user may keep a generated export and mark it inert with this sentinel file.
RETENTION_MARKER = ".tes-retained-exports.json"


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _json_is_empty_hooks(text: str) -> bool:
    try:
        data = json.loads(text or "{}")
    except json.JSONDecodeError:
        return False
    if not isinstance(data, dict):
        return False
    hooks = data.get("hooks")
    if hooks in ({}, None):
        return set(data.keys()) <= {"hooks", "version"}
    if not isinstance(hooks, dict):
        return False
    return set(data.keys()) <= {"hooks", "version"} and all(
        (not value) or (isinstance(value, list) and not value)
        for value in hooks.values()
    )


def retained_exports(target: Path) -> set[str]:
    """Paths the user explicitly chose to retain after uninstall (inert exports).

    Read from an optional retention marker the uninstall flow writes when the
    user keeps generated docs. Absent marker means nothing is retained.
    """
    marker = target / RETENTION_MARKER
    if not marker.is_file():
        return set()
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    retained = data.get("retained") if isinstance(data, dict) else None
    return {str(item) for item in retained} if isinstance(retained, list) else set()


def detect_capsule(target: Path) -> list[str]:
    capsule = target / ".tes"
    if not capsule.exists():
        return []
    # Any file under .tes/** is active capsule state.
    files = [p for p in capsule.rglob("*") if p.is_file()]
    return [".tes/** (capsule state present)"] if files or capsule.is_dir() else []


def detect_bootloader_blocks(target: Path) -> list[str]:
    found: list[str] = []
    for name in ROOT_BOOTLOADERS:
        text = read_text(target / name)
        if text and root_context.extract_core(text):
            found.append(f"{name} (TES:CORE block)")
    return found


def detect_mcp(target: Path) -> list[str]:
    found: list[str] = []
    for rel in MCP_CONFIG_PATHS:
        text = read_text(target / rel)
        if text and MCP_SERVER_NAME in text:
            found.append(f"{rel} ({MCP_SERVER_NAME} server)")
    return found


def detect_hooks(target: Path) -> list[str]:
    found: list[str] = []
    for rel in HOOK_CONFIG_PATHS:
        text = read_text(target / rel)
        if text and any(token in text for token in HOOK_COMMAND_TOKENS) and " hook" in text:
            found.append(f"{rel} (TES hook entry)")
    git_pre_push = target / ".git/hooks/pre-push"
    text = read_text(git_pre_push)
    if text and "TES_FIELD_REPORTS_PRE_PUSH" in text:
        found.append(".git/hooks/pre-push (TES field reports hook)")
    return found


SKILLS_ROOTS = (".agents/skills", ".claude/skills")


def detect_skills(target: Path) -> list[str]:
    """Detect materialized TES project skills (the /tes-* command set).

    Skills are their own attachment surface (ADR 0004 amendment), distinct from
    the root bootloaders. This detector lets attach-health and detach agree on
    exactly what the `skills` surface owns.
    """
    found: list[str] = []
    for rel in SKILLS_ROOTS:
        root = target / rel
        if not root.exists():
            continue
        skill_files = [
            path
            for path in root.rglob("SKILL.md")
            if path.is_file() and ("/tes-" in path.as_posix() or path.parent.name.startswith("tes-"))
        ]
        if skill_files:
            found.append(f"{rel}/** (TES project skills, {len(skill_files)} skills)")
    return found


def detect_project_visible_runtime(target: Path) -> list[str]:
    found: list[str] = []
    for rel in PROJECT_VISIBLE_RUNTIME_ROOTS:
        root = target / rel
        if not root.exists():
            continue
        files = [
            path
            for path in root.rglob("*")
            if path.is_file() and (path.name.startswith("tes-") or "/tes-" in path.as_posix() or "TES" in read_text(path))
        ]
        if files:
            found.append(f"{rel}/** (TES project-visible runtime, {len(files)} files)")
    return found


def detect_hygiene_residue(target: Path) -> list[str]:
    found: list[str] = []
    for root_rel in SHELL_DIRS:
        root = target / root_rel
        if not root.exists():
            continue
        backup_files = sorted(path for path in root.rglob("*.bak-*") if path.is_file())
        if backup_files:
            found.extend(f"{rel(path, target)} (TES backup residue)" for path in backup_files)
        if root.is_dir() and not any(path.is_file() for path in root.rglob("*")):
            found.append(f"{root_rel}/ (empty TES shell directory)")
    for relpath in (".codex/config.toml", ".claude/settings.json", ".cursor/hooks.json"):
        path = target / relpath
        if not path.is_file():
            continue
        text = read_text(path)
        if relpath == ".codex/config.toml" and text.strip() in {"", "[features]"}:
            found.append(f"{relpath} (empty TES shell config)")
        if relpath in {".claude/settings.json", ".cursor/hooks.json"} and _json_is_empty_hooks(text):
            found.append(f"{relpath} (empty TES shell config)")
    return found


def detect_docs_mesh(target: Path) -> list[str]:
    # docs/agents/** is generated by tes_init when docs-mesh is attached. It is
    # project-visible and owned by the project (uninstall preserves it), so it is
    # an inert export, not active residue — but detect it so attach/detach and
    # residue agree on what the surface owns.
    root = target / DOCS_MESH_ROOT
    if not root.exists():
        return []
    files = [p for p in root.rglob("*") if p.is_file()]
    return [f"{DOCS_MESH_ROOT}/** (docs mesh, {len(files)} files)"] if files else []


def evaluate(target: Path) -> dict[str, Any]:
    target = target.resolve()
    retained = retained_exports(target)
    # Active surfaces (live routes / capsule state) can be residue. docs-mesh is
    # project-owned content that uninstall intentionally preserves, so it is
    # always an inert export, never active residue.
    active_surfaces = {
        "capsule": detect_capsule(target),
        "bootloader": detect_bootloader_blocks(target),
        "mcp": detect_mcp(target),
        "hooks": detect_hooks(target),
        "project-visible-runtime": detect_project_visible_runtime(target),
        "hygiene": detect_hygiene_residue(target),
    }
    inert_surfaces = {
        "docs-mesh": detect_docs_mesh(target),
    }
    active: list[str] = []
    inert: list[str] = []
    for items in active_surfaces.values():
        for item in items:
            path = item.split(" ", 1)[0]
            (inert if path in retained else active).append(item)
    for items in inert_surfaces.values():
        inert.extend(items)
    status = "PASS" if not active else "FAIL"
    surfaces = {**active_surfaces, **inert_surfaces}
    return {
        "version": VERSION,
        "status": status,
        "target": str(target),
        "active_residue": sorted(active),
        "retained_exports": sorted(inert),
        "surfaces": {key: sorted(value) for key, value in surfaces.items()},
    }


def self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-residue-self-test-") as tempdir:
        root = Path(tempdir)

        # Fixture 1: clean target -> PASS.
        clean = root / "clean"
        clean.mkdir()
        (clean / "README.md").write_text("# Project\n", encoding="utf-8")
        r1 = evaluate(clean)
        if r1["status"] != "PASS" or r1["active_residue"]:
            failures.append(f"clean target must PASS with no residue: {r1['status']} {r1['active_residue']}")

        # Fixture 2: leftover .tes/** -> FAIL.
        capsule = root / "capsule"
        (capsule / ".tes/bin").mkdir(parents=True)
        (capsule / ".tes/bin/cortex.py").write_text("VERSION='x'\n", encoding="utf-8")
        r2 = evaluate(capsule)
        if r2["status"] != "FAIL" or not any("capsule" in item for item in r2["active_residue"]):
            failures.append(f"leftover .tes/** must FAIL: {r2['status']}")

        # Fixture 3: stale hook entry -> FAIL.
        hook = root / "hook"
        (hook / ".claude").mkdir(parents=True)
        (hook / ".claude/settings.json").write_text(
            json.dumps({"hooks": {"SessionStart": [{"command": "python3 .tes/bin/tes_install.py hook"}]}}),
            encoding="utf-8",
        )
        r3 = evaluate(hook)
        if r3["status"] != "FAIL" or not any("hook" in item.lower() for item in r3["active_residue"]):
            failures.append(f"stale hook entry must FAIL: {r3['status']}")

        # Fixture 4: a TES:CORE bootloader retained as inert export -> PASS (reported).
        retained = root / "retained"
        retained.mkdir()
        core_text = (
            "<!-- TES:CORE BEGIN version=0.0.0 sha256=abc adapter=claude path=CLAUDE.md -->\n"
            "core body\n"
            "<!-- TES:CORE END -->\n"
        )
        (retained / "CLAUDE.md").write_text(core_text, encoding="utf-8")
        (retained / RETENTION_MARKER).write_text(
            json.dumps({"retained": ["CLAUDE.md"]}), encoding="utf-8"
        )
        r4 = evaluate(retained)
        if r4["status"] != "PASS":
            failures.append(f"retained inert export must PASS: {r4['status']} active={r4['active_residue']}")
        if not any("CLAUDE.md" in item for item in r4["retained_exports"]):
            failures.append("retained inert export must be reported under retained_exports")

        # Guard: the same bootloader WITHOUT retention marker must FAIL (active).
        not_retained = root / "not-retained"
        not_retained.mkdir()
        (not_retained / "CLAUDE.md").write_text(core_text, encoding="utf-8")
        r5 = evaluate(not_retained)
        if r5["status"] != "FAIL":
            failures.append(f"un-retained TES:CORE bootloader must FAIL: {r5['status']}")

        # Fixture 6: docs-mesh (docs/agents/**) is project-owned -> inert, PASS.
        docs = root / "docs-mesh"
        (docs / "docs/agents").mkdir(parents=True)
        (docs / "docs/agents/PROJECT-CONTEXT.md").write_text("# Context\n", encoding="utf-8")
        r6 = evaluate(docs)
        if r6["status"] != "PASS":
            failures.append(f"docs-mesh must be inert (PASS), not active residue: {r6['status']}")
        if not any("docs/agents" in item for item in r6["retained_exports"]):
            failures.append("docs-mesh must be reported under retained_exports")

        # Fixture 7: project-visible TES skills/rules are active residue.
        runtime = root / "project-visible-runtime"
        (runtime / ".agents/skills/tes-map").mkdir(parents=True)
        (runtime / ".agents/skills/tes-map/SKILL.md").write_text("# TES Map\n", encoding="utf-8")
        r7 = evaluate(runtime)
        if r7["status"] != "FAIL" or not any("project-visible" in item for item in r7["active_residue"]):
            failures.append(f"project-visible TES runtime must FAIL: {r7['status']} {r7['active_residue']}")

        # Fixture 8: uninstall backup/shell residue is not clean.
        hygiene = root / "hygiene"
        (hygiene / ".codex").mkdir(parents=True)
        (hygiene / ".codex/config.toml").write_text("[features]\n", encoding="utf-8")
        (hygiene / ".codex/config.toml.bak-20260604T000000Z").write_text("tes\n", encoding="utf-8")
        r8 = evaluate(hygiene)
        if r8["status"] != "FAIL" or not any("backup residue" in item or "shell config" in item for item in r8["active_residue"]):
            failures.append(f"backup/shell residue must FAIL: {r8['status']} {r8['active_residue']}")

        # Fixture 9: Codex hook command can survive without the marker comment.
        codex_hook = root / "codex-hook"
        (codex_hook / ".codex").mkdir(parents=True)
        (codex_hook / ".codex/config.toml").write_text(
            "[features]\n\n"
            "[[hooks.SessionStart]]\n"
            "matcher = \"startup|resume\"\n\n"
            "[[hooks.SessionStart.hooks]]\n"
            "type = \"command\"\n"
            "command = \"python3 \\\"$(git rev-parse --show-toplevel)/.tes/bin/tes_install.py\\\" hook --agent codex\"\n",
            encoding="utf-8",
        )
        r9 = evaluate(codex_hook)
        if r9["status"] != "FAIL" or not any(".codex/config.toml" in item for item in r9["active_residue"]):
            failures.append(f"unmarked Codex TES hook must FAIL: {r9['status']} {r9['active_residue']}")

    result = {"version": VERSION, "status": "FAIL" if failures else "PASS", "failures": failures}
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[capsule-residue:self-test] " + result["status"])
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--target", type=Path, default=Path.cwd())
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    result = evaluate(args.target)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[capsule-residue] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
