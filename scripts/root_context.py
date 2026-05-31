#!/usr/bin/env python3
"""Detect durable agent context hidden in root runtime bootloaders."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.149"
EVIDENCE_DIR = Path("docs/agents/evidence")
BACKUP_ROOT = Path(".tes/bk")
ROOT_FILES = (
    ("codex", "AGENTS.md", "src/adapters/codex/AGENTS.md"),
    ("claude", "CLAUDE.md", "src/adapters/claude/CLAUDE.md"),
    ("cursor", "CURSOR.md", "src/adapters/cursor/CURSOR.md"),
    ("cursor", ".cursor/rules/tes-guidelines.mdc", "src/adapters/cursor/rules/tes-guidelines.mdc"),
    ("cursor", ".cursorrules", None),
)
IGNORE_TERMS = (
    "tilly",
    "cortex",
    "field reports",
    "/tilly",
    "docs/agents",
    ".agents/skills",
    "assumptions visible",
    "think before coding",
    "simplicity first",
    "surgical changes",
    "goal-driven execution",
    "diamond build",
    "success formula",
    "codex",
    "claude",
    "cursor",
    "mcp",
    "bootloader",
    "runtime",
    "shortcuts",
    "do not claim",
)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def source_sha(source_rel: str | None) -> str | None:
    if source_rel is None:
        return None
    source = ROOT / source_rel
    return sha256(source) if source.exists() else None


def package_source_available() -> bool:
    return (ROOT / "src/adapters/codex/AGENTS.md").exists()


def packaged_codex_bootloader() -> str:
    source = ROOT / "src/adapters/codex/AGENTS.md"
    if source.exists():
        return source.read_text(encoding="utf-8")
    return "# Tilly Codex Bootloader\n\nRoute to `docs/agents/**`.\nTilly applies.\n"


def root_candidates(target: Path) -> list[tuple[str, Path, str | None]]:
    candidates = [(adapter, target / relpath, source) for adapter, relpath, source in ROOT_FILES]
    rules = sorted((target / ".cursor/rules").glob("*.mdc"))
    known = {path for _, path, _ in candidates}
    for path in rules:
        if path not in known:
            candidates.append(("cursor", path, None))
    return candidates


def backup_root_candidates(target: Path, backup_id: str) -> list[tuple[str, Path, str | None]]:
    backup_files = target / BACKUP_ROOT / backup_id / "files"
    candidates = [(adapter, backup_files / relpath, source) for adapter, relpath, source in ROOT_FILES]
    rules = sorted((backup_files / ".cursor/rules").glob("*.mdc"))
    known = {path for _, path, _ in candidates}
    for path in rules:
        if path not in known:
            candidates.append(("cursor", path, None))
    return candidates


def meaningful_lines(text: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line in {"---", "```", "```text", "<instructions>", "</instructions>"}:
            continue
        compact = re.sub(r"^[#>*\-\d\.\s`]+", "", line).strip()
        if len(compact) < 6:
            continue
        lines.append((lineno, line))
    return lines


def project_context_lines(text: str) -> list[dict[str, Any]]:
    snippets: list[dict[str, Any]] = []
    for lineno, line in meaningful_lines(text):
        lower = line.lower()
        if any(term in lower for term in IGNORE_TERMS):
            continue
        snippets.append({"line": lineno, "excerpt": line[:160]})
        if len(snippets) >= 5:
            break
    return snippets


def classify_file(target: Path, adapter: str, path: Path, source_rel: str | None) -> dict[str, Any]:
    relpath = rel(path, target)
    if not path.exists():
        return {"adapter": adapter, "path": relpath, "state": "missing", "requires_structure_gate": False}
    if not path.is_file():
        return {"adapter": adapter, "path": relpath, "state": "not-file", "requires_structure_gate": True}

    text = read(path)
    current_sha = sha256(path)
    expected_sha = source_sha(source_rel)
    line_count = len(text.splitlines())
    snippets = project_context_lines(text)
    has_tes = any(term in text.lower() for term in ("tilly", "docs/agents", ".agents/skills", "/tilly"))

    if expected_sha and current_sha == expected_sha:
        state = "current-tes-root"
        requires = False
    elif snippets:
        state = "mixed-or-project-root-context" if has_tes else "project-root-context"
        requires = True
    elif has_tes:
        state = "tes-root-drift"
        requires = False
    elif line_count == 0:
        state = "empty"
        requires = False
    else:
        state = "project-root-context"
        requires = True

    return {
        "adapter": adapter,
        "path": relpath,
        "state": state,
        "requires_structure_gate": requires,
        "line_count": line_count,
        "sha256": current_sha,
        "source": source_rel,
        "source_sha256": expected_sha,
        "signals": snippets,
    }


def analyze(target: Path, *, write_plan: bool = False, backup_id: str | None = None) -> dict[str, Any]:
    target = target.expanduser().resolve()
    if not target.exists() or not target.is_dir():
        return {"version": VERSION, "status": "FAIL", "failures": [f"target is not a directory: {target}"]}

    candidate_root = target if backup_id is None else target / BACKUP_ROOT / backup_id / "files"
    candidates = root_candidates(target) if backup_id is None else backup_root_candidates(target, backup_id)
    roots = [classify_file(candidate_root, adapter, path, source) for adapter, path, source in candidates]
    required = [item for item in roots if item.get("requires_structure_gate")]
    result: dict[str, Any] = {
        "version": VERSION,
        "status": "NEEDS_REVIEW" if required else "PASS",
        "target": str(target),
        "source": "active-root" if backup_id is None else f"backup:{backup_id}",
        "structure_gate": "required" if required else "not_required",
        "root_count": len([item for item in roots if item["state"] != "missing"]),
        "requires_structure_count": len(required),
        "roots": roots,
        "writes": [],
        "failures": [],
    }
    if write_plan and required:
        plan = write_structure_plan(target, required)
        result["writes"].append(plan)
    return result


def write_structure_plan(target: Path, required: list[dict[str, Any]]) -> str:
    evidence = target / EVIDENCE_DIR
    evidence.mkdir(parents=True, exist_ok=True)
    path = evidence / f"{utc_stamp()}-root-context-structure-plan.md"
    sections = []
    for item in required:
        signals = "\n".join(f"- line {signal['line']}: {signal['excerpt']}" for signal in item.get("signals", []))
        sections.append(
            "\n".join(
                [
                    f"## {item['path']}",
                    "",
                    f"State: `{item['state']}`",
                    f"SHA-256: `{item.get('sha256', '')}`",
                    "",
                    "Signals:",
                    signals or "- present root context",
                    "",
                    "Required action: migrate durable instructions into `docs/agents/**`",
                    "or a project-owned adapter note before rewriting this root file.",
                ]
            )
        )
    path.write_text(
        "\n\n".join(
            [
                "# Tilly Root Context Structure Plan",
                "",
                "Root runtime files may contain project-owned instructions.",
                "Back them up centrally before clean runtime overwrite, then recover",
                "durable semantics into docs/agents evidence.",
                "",
                *sections,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path.relative_to(target).as_posix()


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    mode = "package" if package_source_available() else "installed"
    coverage = "source-package-contract" if mode == "package" else "installed-helper-contract"
    with tempfile.TemporaryDirectory(prefix="tes-root-context-") as tempdir:
        target = Path(tempdir)
        clean = analyze(target)
        if clean["status"] != "PASS":
            failures.append("empty project must pass")

        (target / "AGENTS.md").write_text(packaged_codex_bootloader(), encoding="utf-8")
        current = analyze(target)
        if current["status"] != "PASS":
            failures.append("current Tilly AGENTS.md must pass")

        (target / "AGENTS.md").write_text("# Project Agent Rules\n\nUse `bun run gate:closure` before final answers.\n", encoding="utf-8")
        project = analyze(target)
        if project["status"] != "NEEDS_REVIEW" or project["structure_gate"] != "required":
            failures.append("project root context must require structure gate")

        (target / "CLAUDE.md").write_text("# CLAUDE.md\n\nTilly applies.\n\nProduction deploys require owner approval.\n", encoding="utf-8")
        mixed = analyze(target, write_plan=True)
        if not mixed["writes"] or not (target / mixed["writes"][0]).exists():
            failures.append("write_plan must create local evidence")

        (target / ".cursor/rules").mkdir(parents=True, exist_ok=True)
        (target / ".cursor/rules/project.mdc").write_text("Always use the internal emulator fixture.\n", encoding="utf-8")
        cursor = analyze(target)
        if cursor["requires_structure_count"] < 3:
            failures.append("custom Cursor root rule must be detected")

        backup_files = target / ".tes/bk/selftest/files"
        backup_files.mkdir(parents=True, exist_ok=True)
        (backup_files / "AGENTS.md").write_text("# Legacy\n\nRun `npm test` before release.\n", encoding="utf-8")
        backup = analyze(target, backup_id="selftest")
        if backup["source"] != "backup:selftest" or backup["status"] != "NEEDS_REVIEW":
            failures.append("backup root context analysis must inspect .tes/bk/<id>/files")

    return {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "self_test_mode": mode,
        "coverage": coverage,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=["analyze"], default="analyze")
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--write-plan", action="store_true")
    parser.add_argument("--backup-id")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result = self_test() if args.self_test else analyze(args.target, write_plan=args.write_plan, backup_id=args.backup_id)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[root-context] " + result["status"])
    if result["status"] == "PASS":
        return 0
    if result["status"] == "NEEDS_REVIEW":
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
