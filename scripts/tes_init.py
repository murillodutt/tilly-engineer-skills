#!/usr/bin/env python3
"""Initialize, recertify, and register a target Tilly project."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cortex
import field_reports
import root_context


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.36"
REGISTER = Path("docs/agents/PROJECT-REGISTER.md")
EVIDENCE_DIR = Path("docs/agents/evidence")
PASSING_GATE_STATUSES = {"PASS", "PRESERVED"}
DEFAULT_COMMAND_TIMEOUT_SECONDS = 60.0
DEFAULT_GIT_LIST_TIMEOUT_SECONDS = 15.0

EXCLUDED_PARTS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".next",
    ".nuxt",
    "dist",
    "build",
    "coverage",
}
EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".sqlite",
    ".sqlite-shm",
    ".sqlite-wal",
    ".db",
    ".DS_Store",
}
MAX_HASH_BYTES = 10 * 1024 * 1024


def timeout_from_env(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def date_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def file_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def run(command: list[str], cwd: Path) -> dict[str, Any]:
    timeout = timeout_from_env("TES_INIT_COMMAND_TIMEOUT_SECONDS", DEFAULT_COMMAND_TIMEOUT_SECONDS)
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "command": " ".join(command),
            "returncode": 124,
            "stdout": stdout.strip(),
            "stderr": (stderr.strip() + f"\ncommand timed out after {timeout:g}s").strip(),
            "status": "BLOCKED",
        }
    return {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "status": "PASS" if result.returncode == 0 else "FAIL",
    }


def gate_passed(gate: dict[str, Any]) -> bool:
    return gate.get("status") in PASSING_GATE_STATUSES


def root_context_gate(target: Path) -> dict[str, Any]:
    command = [sys.executable, str(ROOT / "scripts/root_context.py"), "analyze", "--target", str(target)]
    result = root_context.analyze(target)
    status = result["status"]
    resolution = None
    if status == "NEEDS_REVIEW":
        status = "PRESERVED"
        resolution = "project-owned root context detected and preserved; overwrite remains blocked without review"
    return {
        "command": " ".join(command),
        "returncode": 2 if result["status"] == "NEEDS_REVIEW" else (0 if result["status"] == "PASS" else 1),
        "stdout": json.dumps(result, indent=2, sort_keys=True),
        "stderr": "",
        "status": status,
        "root_context_status": result["status"],
        "resolution": resolution,
    }


def git_head(target: Path) -> str:
    result = run(["git", "rev-parse", "HEAD"], target)
    return result["stdout"] if result["returncode"] == 0 else "unknown"


def git_status(target: Path) -> str:
    result = run(["git", "status", "--short", "--branch", "--untracked-files=all"], target)
    return result["stdout"] if result["returncode"] == 0 else "not-a-git-repo"


def is_excluded(relpath: Path) -> bool:
    if len(relpath.parts) >= 2 and relpath.parts[0] == ".tes" and relpath.parts[1] == "field-reports":
        return True
    if len(relpath.parts) >= 3 and relpath.parts[0] == ".tes" and relpath.parts[1] == "bin" and ".bak-" in relpath.name:
        return True
    if any(part in EXCLUDED_PARTS for part in relpath.parts):
        return True
    if relpath.suffix in EXCLUDED_SUFFIXES:
        return True
    if relpath.as_posix() == cortex.RECALL_DB.as_posix():
        return True
    return False


def git_files(target: Path) -> list[Path] | None:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=target,
            capture_output=True,
            check=False,
            timeout=timeout_from_env("TES_INIT_GIT_LIST_TIMEOUT_SECONDS", DEFAULT_GIT_LIST_TIMEOUT_SECONDS),
        )
    except subprocess.TimeoutExpired:
        return []
    if result.returncode != 0:
        return None
    files: list[Path] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        relpath = Path(raw.decode("utf-8"))
        path = target / relpath
        if path.is_file() and not is_excluded(relpath):
            files.append(path)
    return sorted(files)


def all_files(target: Path) -> list[Path]:
    from_git = git_files(target)
    if from_git is not None:
        return from_git
    files: list[Path] = []
    for path in target.rglob("*"):
        if not path.is_file():
            continue
        relpath = path.relative_to(target)
        if not is_excluded(relpath):
            files.append(path)
    return sorted(files)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_record(path: Path, target: Path) -> dict[str, Any] | None:
    try:
        stat = path.stat()
    except OSError:
        return None
    record: dict[str, Any] = {
        "path": rel(path, target),
        "bytes": stat.st_size,
        "suffix": path.suffix,
    }
    if stat.st_size <= MAX_HASH_BYTES:
        try:
            record["sha256"] = sha256_file(path)
        except OSError:
            record["sha256"] = "skipped:unreadable"
    else:
        record["sha256"] = "skipped:large-file"
    return record


def surface_inventory(target: Path) -> dict[str, Any]:
    paths = {
        "docs_agents": "docs/agents",
        "cortex_contract": "docs/agents/cortex/CONTRACT.md",
        "codex_agents": "AGENTS.md",
        "codex_skill": ".agents/skills/tes-engineering-discipline/SKILL.md",
        "claude_md": "CLAUDE.md",
        "claude_plugin": ".claude-plugin/plugin.json",
        "claude_skill": "skills/tes-guidelines/SKILL.md",
        "cursor_bootloader": "CURSOR.md",
        "cursor_rules": ".cursor/rules",
        "codex_mcp": ".codex/config.toml",
        "claude_mcp": ".mcp.json",
        "cursor_mcp": ".cursor/mcp.json",
        "tes_mcp_server": ".tes/bin/cortex_mcp.py",
        "tes_mcp_embed_helper": ".tes/bin/cortex_embed.mjs",
        "tes_field_reports_helper": ".tes/bin/field_reports.py",
        "tes_update_helper": ".tes/bin/tes_update.py",
        "tes_legacy_retirement_helper": ".tes/bin/tes_legacy_retirement.py",
        "tes_root_context_helper": ".tes/bin/root_context.py",
        "tes_field_reports_outbox": ".tes/field-reports/outbox.jsonl",
        "tes_field_reports_disabled": ".tes/field-reports/DISABLED",
        "tes_field_reports_pre_push": ".git/hooks/pre-push",
    }
    return {name: (target / relpath).exists() for name, relpath in paths.items()}


def scan_project(target: Path) -> dict[str, Any]:
    files = all_files(target)
    records = [record for path in files if (record := file_record(path, target)) is not None]
    suffixes = Counter(record["suffix"] or "[none]" for record in records)
    dirs = Counter(Path(record["path"]).parts[0] if Path(record["path"]).parts else "." for record in records)
    return {
        "generated_at": utc_stamp(),
        "target": str(target),
        "git_head": git_head(target),
        "git_status": git_status(target),
        "file_count": len(records),
        "total_bytes": sum(int(record["bytes"]) for record in records),
        "suffixes": dict(sorted(suffixes.items())),
        "top_level": dict(sorted(dirs.items())),
        "surfaces": surface_inventory(target),
        "files": records,
    }


def bootstrap_scan(target: Path, manifest_rel: str) -> dict[str, Any]:
    return {
        "generated_at": utc_stamp(),
        "target": str(target),
        "git_head": git_head(target),
        "git_status": git_status(target),
        "file_count": 0,
        "total_bytes": 0,
        "suffixes": {},
        "top_level": {},
        "surfaces": surface_inventory(target),
        "files": [],
        "bootstrap": True,
        "manifest": manifest_rel,
    }


def package_gates() -> list[dict[str, Any]]:
    gates = [
        [sys.executable, "scripts/install_smoke.py", "--self-test"],
        [sys.executable, "scripts/platform_surface_oracle.py", "--self-test"],
    ]
    return [run(command, ROOT) for command in gates]


def target_gates(target: Path) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = [run(["git", "diff", "--check"], target)]
    gates.append(root_context_gate(target))
    gates.append(run([sys.executable, str(ROOT / "scripts/field_reports.py"), "status", "--target", str(target)], ROOT))
    cortex_root = cortex.cortex_path(target)
    if (cortex_root / "CONTRACT.md").exists():
        for command in ("verify", "audit", "rebuild", "curate-plan"):
            extra_args = ["--backend", "lexical"] if command == "curate-plan" else []
            gates.append(
                run(
                    [sys.executable, str(ROOT / "scripts/cortex.py"), command, "--target", str(target), *extra_args],
                    ROOT,
                )
            )
    mcp = target / ".tes/bin/cortex_mcp.py"
    if mcp.exists():
        gates.append(run([sys.executable, str(mcp), "--self-test"], target))
    codex_oracle = target / ".agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py"
    if codex_oracle.exists():
        gates.append(run([sys.executable, str(codex_oracle), "--self-test"], target))
    return gates


def write_register(target: Path, scan: dict[str, Any], gates: list[dict[str, Any]], manifest_rel: str) -> str:
    suffix_rows = "\n".join(
        f"| `{suffix}` | {count} |" for suffix, count in sorted(scan["suffixes"].items())
    )
    surface_rows = "\n".join(
        f"| `{name}` | {'present' if present else 'missing'} |"
        for name, present in sorted(scan["surfaces"].items())
    )
    gate_rows = "\n".join(
        f"| `{gate['command']}` | `{gate['status']}` |"
        for gate in gates
    )
    return f"""# Tilly Project Register

Generated: `{scan['generated_at']}`

This register is a deterministic project inventory for Tilly agents. It records
the project shape; it is not compiled Cortex knowledge and it is not a
replacement for Git history.

## Identity

| Field | Value |
|-------|-------|
| Target | `{scan['target']}` |
| Git HEAD | `{scan['git_head']}` |
| File count | `{scan['file_count']}` |
| Total bytes | `{scan['total_bytes']}` |
| Manifest | `{manifest_rel}` |

## Tilly Surfaces

| Surface | Status |
|---------|--------|
{surface_rows}

## File Types

| Suffix | Count |
|--------|-------|
{suffix_rows}

## Recertification Gates

| Command | Result |
|---------|--------|
{gate_rows}

## Governance

- Re-run `python3 scripts/tes_init.py --target <project> --yes` after major
  project reshapes.
- Do not treat this inventory as memory. Promote durable knowledge through
  Cortex `learn` and authorized `apply`.
- Keep generated manifests in `docs/agents/evidence/**` so Git preserves the
  lineage.
- TES Field Reports are operational transport only; Git and local governed
  artifacts remain project truth.
- Root context result `PRESERVED` means project-owned bootloader context was
  detected and intentionally left untouched. It remains a blocker only for
  overwrite attempts.
"""


def write_evidence(
    target: Path,
    scan: dict[str, Any],
    gates: list[dict[str, Any]],
    writes: list[str],
    manifest_rel: str,
) -> str:
    gate_rows = "\n".join(
        f"| `{gate['command']}` | `{gate['status']}` | `{gate['returncode']}` |"
        for gate in gates
    )
    write_rows = "\n".join(f"- `{path}`" for path in writes) or "- none"
    return f"""# TES Initialization Evidence

Generated: `{scan['generated_at']}`

## Decision

Status: `{'PASS' if all(gate_passed(gate) for gate in gates) else 'NEEDS_REVIEW'}`

## Scope

This initialization recertified TES package health, scanned the target
project, and wrote a project register plus full manifest.

## Target

| Field | Value |
|-------|-------|
| Target | `{target}` |
| Git HEAD | `{scan['git_head']}` |
| File count | `{scan['file_count']}` |
| Manifest | `{manifest_rel}` |

## Gates

| Command | Status | Code |
|---------|--------|------|
{gate_rows}

## Writes

{write_rows}

## Non-Claims

- This does not bulk-absorb project history into Cortex.
- This does not write to `sources/**`.
- This does not publish, push, tag, or install dependencies.
- This does not replace local project governance.
- This does not send project code or file contents through Field Reports.
"""


def initialize(target: Path, *, yes: bool, ensure_cortex: bool) -> dict[str, Any]:
    target = target.resolve()
    if not target.exists() or not target.is_dir():
        return {"status": "FAIL", "failures": [f"target must be a directory: {target}"], "writes": []}

    stamp = file_stamp()
    planned_writes = [
        REGISTER.as_posix(),
        f"{EVIDENCE_DIR.as_posix()}/{stamp}-tes-initialization.md",
        f"{EVIDENCE_DIR.as_posix()}/{stamp}-tes-project-manifest.json",
        ".tes/bin/field_reports.py",
        ".tes/field-reports/outbox.jsonl",
        ".git/hooks/pre-push",
        ".git/info/exclude",
    ]
    if not yes:
        return {
            "version": VERSION,
            "status": "NEEDS_AUTH",
            "target": str(target),
            "writes": planned_writes,
            "message": "tes init writes a project register and evidence manifest; rerun with --yes",
        }

    evidence_dir = target / EVIDENCE_DIR
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (target / REGISTER).parent.mkdir(parents=True, exist_ok=True)

    manifest_path = evidence_dir / f"{stamp}-tes-project-manifest.json"
    evidence_path = evidence_dir / f"{stamp}-tes-initialization.md"
    manifest_rel = rel(manifest_path, target)

    bootstrap = bootstrap_scan(target, manifest_rel)
    bootstrap_gate = {
        "command": "tes_init bootstrap",
        "returncode": 2,
        "stdout": "",
        "stderr": "final gates not completed yet",
        "status": "NEEDS_REVIEW",
    }
    manifest_path.write_text(json.dumps(bootstrap, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target / REGISTER).write_text(write_register(target, bootstrap, [bootstrap_gate], manifest_rel), encoding="utf-8")
    evidence_path.write_text(
        write_evidence(target, bootstrap, [bootstrap_gate], planned_writes, manifest_rel),
        encoding="utf-8",
    )

    cortex_result: dict[str, Any] | None = None
    if ensure_cortex:
        cortex_result = cortex.init(target)
    field_report_result = field_reports.install_hook(target)
    root_context_result = root_context.analyze(target)
    if root_context_result["status"] == "NEEDS_REVIEW":
        root_context_result = {
            **root_context_result,
            "certification_status": "PRESERVED",
            "resolution": "project-owned root context preserved; overwrite remains blocked without review",
        }

    scan = scan_project(target)
    gates = [*package_gates(), *target_gates(target)]
    status = "PASS" if all(gate_passed(gate) for gate in gates) else "NEEDS_REVIEW"

    register_text = write_register(target, scan, gates, manifest_rel)
    evidence_text = write_evidence(target, scan, gates, planned_writes, manifest_rel)

    manifest_path.write_text(json.dumps(scan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target / REGISTER).write_text(register_text, encoding="utf-8")
    evidence_path.write_text(evidence_text, encoding="utf-8")

    actual_writes = [
        REGISTER.as_posix(),
        rel(evidence_path, target),
        rel(manifest_path, target),
        *[str(item) for item in field_report_result.get("writes", [])],
    ]
    field_reports.safe_record_event(
        target,
        "tes_init",
        status,
        "installer",
        "cli",
        details={
            "file_count": scan["file_count"],
            "gate_failures": sum(1 for gate in gates if not gate_passed(gate)),
            "field_reports": field_report_result.get("status", "UNKNOWN"),
        },
    )

    return {
        "version": VERSION,
        "status": status,
        "target": str(target),
        "git_head": scan["git_head"],
        "file_count": scan["file_count"],
        "writes": actual_writes,
        "cortex": cortex_result,
        "field_reports": field_report_result,
        "root_context": root_context_result,
        "gates": gates,
    }


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-init-") as tempdir:
        target = Path(tempdir)
        (target / "README.md").write_text("# Fixture\n", encoding="utf-8")
        (target / "AGENTS.md").write_text(
            "# Project Agent Rules\n\nUse local project governance before package defaults.\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)
        subprocess.run(["git", "add", "README.md"], cwd=target, text=True, capture_output=True, check=False)
        subprocess.run(
            ["git", "commit", "-m", "fixture"],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "GIT_AUTHOR_NAME": "Tilly", "GIT_AUTHOR_EMAIL": "tilly@example.test",
                 "GIT_COMMITTER_NAME": "Tilly", "GIT_COMMITTER_EMAIL": "tilly@example.test"},
        )
        needs_auth = initialize(target, yes=False, ensure_cortex=True)
        result = initialize(target, yes=True, ensure_cortex=True)
        if needs_auth["status"] != "NEEDS_AUTH":
            failures.append("init without --yes must require authorization")
        for relpath in result["writes"]:
            if not (target / relpath).exists():
                failures.append(f"missing write: {relpath}")
        if result["status"] != "PASS":
            failures.append(f"expected PASS, got {result['status']}")
        if not any(gate["status"] == "PRESERVED" for gate in result["gates"]):
            failures.append("project-owned root context must close as PRESERVED during init")

    with tempfile.TemporaryDirectory(prefix="tes-init-timeout-") as tempdir:
        target = Path(tempdir)
        (target / "README.md").write_text("# Timeout fixture\n", encoding="utf-8")
        (target / ".tes/bin").mkdir(parents=True)
        (target / ".tes/bin/cortex_mcp.py").write_text(
            "import time\n"
            "time.sleep(5)\n",
            encoding="utf-8",
        )
        previous = os.environ.get("TES_INIT_COMMAND_TIMEOUT_SECONDS")
        os.environ["TES_INIT_COMMAND_TIMEOUT_SECONDS"] = "0.1"
        try:
            timeout_result = initialize(target, yes=True, ensure_cortex=False)
        finally:
            if previous is None:
                os.environ.pop("TES_INIT_COMMAND_TIMEOUT_SECONDS", None)
            else:
                os.environ["TES_INIT_COMMAND_TIMEOUT_SECONDS"] = previous
        if not (target / REGISTER).exists():
            failures.append("register must exist even when a later gate times out")
        if timeout_result["status"] != "NEEDS_REVIEW":
            failures.append("timeout fixture must return NEEDS_REVIEW")
        if not any(gate["status"] == "BLOCKED" for gate in timeout_result["gates"]):
            failures.append("timeout fixture must expose a BLOCKED gate")

    return {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=Path("."))
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--no-cortex-init", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result = self_test() if args.self_test else initialize(
        args.target,
        yes=args.yes,
        ensure_cortex=not args.no_cortex_init,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-init] " + result["status"])
    return 0 if result["status"] in {"PASS", "NEEDS_AUTH"} else 1


if __name__ == "__main__":
    sys.exit(main())
