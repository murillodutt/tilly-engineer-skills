#!/usr/bin/env python3
"""Report and audit the TES namespace migration surface."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.88"

ACTIVE_PREFIXES = (
    ".github/",
    ".githooks/",
    "docs/adapters/",
    "docs/governance/",
    "docs/install/",
    "docs/mesh/",
    "scripts/",
    "src/",
)
ACTIVE_FILES = {
    "AGENTS.md",
    "README.md",
    "package.json",
}
CATALOG_PATH = "docs/architecture/TES-NAMING-MIGRATION-CATALOG.md"
DEFAULT_SKIPPED_PREFIXES = (
    ".git/",
    ".tes/field-reports/",
    ".tes/legacy-retirement/",
    "dist/",
    "node_modules/",
    "docs/evidence/reports/",
)
SEARCH_PATTERN = (
    r"(/tilly:|tilly:|tilly-|tilly_|tilly\.|\.tilly/|\.tilly\b|"
    r"tilly-cortex|tilly-field-report|tilly-engineering-discipline|tilly-guidelines|"
    r"tilly-version|tilly-skills|tilly-root|tilly-reference|tilly-discipline|"
    r"tilly-navigation|tilly-root-context|tilly-install-smoke|tilly-engineer-skills-|"
    r"tilly update|update Tilly|atualizar Tilly|initialize Tilly|install Tilly|recertify Tilly|"
    r"inicializar Tilly|instalar Tilly|recertificar Tilly|"
    r"Tilly (Init|Cortex|MCP|Doctor|Adapter|Bench|Field Report|Field Reports)|"
    r"Atualizar a Tilly|Tilly, initialize this project|Tilly, inicialize este projeto|"
    r"tilly init|TILLY_FIELD_REPORTS_PRE_PUSH)"
)
SKIPPED_PARTS = {
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
}
TEXT_SUFFIXES = {
    "",
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".mdc",
    ".mjs",
    ".prompt",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yml",
    ".yaml",
}


@dataclass(frozen=True)
class Replacement:
    old: str
    new: str
    category: str


@dataclass(frozen=True)
class PathRename:
    path: str
    target: str
    category: str
    scope: str


@dataclass(frozen=True)
class ContentRename:
    path: str
    line: int
    old: str
    new: str
    category: str
    scope: str
    snippet: str


@dataclass(frozen=True)
class ScriptRename:
    key: str
    target_key: str
    value: str
    target_value: str
    category: str


@dataclass(frozen=True)
class RawLocation:
    source: str
    path: str
    line: int
    column: int | None
    scope: str
    text: str


PATH_REPLACEMENTS = (
    Replacement("tilly-engineering-discipline", "tes-engineering-discipline", "codex skill"),
    Replacement("tilly-guidelines", "tes-guidelines", "adapter guideline"),
    Replacement("tilly-field-report", "tes-field-report", "github field report"),
    Replacement("tilly_init", "tes_init", "python script"),
    Replacement("tilly_update", "tes_update", "python script"),
    Replacement("tilly-cortex", "tes-cortex", "mcp or skill"),
    Replacement("tilly-align", "tes-align", "alignment skill"),
    Replacement("tilly-adapter", "tes-adapter", "adapter skill"),
    Replacement("tilly-bench", "tes-bench", "bench skill"),
    Replacement("tilly-doctor", "tes-doctor", "doctor skill"),
    Replacement("tilly-init", "tes-init", "init skill"),
    Replacement("tilly-mcp", "tes-mcp", "mcp skill"),
)

PROMPT_REPLACEMENTS = (
    Replacement("/tilly:adapter", "/tes-adapter", "prompt command"),
    Replacement("/tilly:align", "/tes-align", "prompt command"),
    Replacement("/tilly:bench", "/tes-bench", "prompt command"),
    Replacement("/tilly:certify", "/tes-doctor", "prompt command"),
    Replacement("/tilly:check", "/tes-doctor", "prompt command"),
    Replacement("/tilly:cortex", "/tes-cortex", "prompt command"),
    Replacement("/tilly:curate", "/tes-curate", "prompt command"),
    Replacement("/tilly:doctor", "/tes-doctor", "prompt command"),
    Replacement("/tilly:field-reports", "/tes-field-reports", "prompt command"),
    Replacement("/tilly:init", "/tes-init", "prompt command"),
    Replacement("/tilly:learn", "/tes-cortex learn", "prompt command"),
    Replacement("/tilly:mcp", "/tes-mcp", "prompt command"),
    Replacement("/tilly:recall", "/tes-cortex recall", "prompt command"),
    Replacement("/tilly:reflect", "/tes-cortex reflect", "prompt command"),
    Replacement("/tilly:update", "/tes-update", "prompt command"),
)

CONTENT_REPLACEMENTS = (
    *PROMPT_REPLACEMENTS,
    Replacement("/tilly:", "/tes-", "prompt namespace"),
    Replacement("tilly:init:self-test", "tes:init:self-test", "npm command"),
    Replacement("tilly:update:self-test", "tes:update:self-test", "npm command"),
    Replacement("tilly:init", "tes:init", "npm command"),
    Replacement("tilly:update", "tes:update", "npm command"),
    Replacement("scripts/tilly_init.py", "scripts/tes_init.py", "python script"),
    Replacement("scripts/tilly_update.py", "scripts/tes_update.py", "python script"),
    Replacement("tilly_init.py", "tes_init.py", "python script"),
    Replacement("tilly_update.py", "tes_update.py", "python script"),
    Replacement("tilly_init", "tes_init", "python script"),
    Replacement("tilly_update", "tes_update", "python script"),
    Replacement(".agents/skills/tilly-*/", ".agents/skills/tes-*/", "skill wildcard"),
    Replacement(".agents/skills/tilly-*/**", ".agents/skills/tes-*/**", "skill wildcard"),
    Replacement("src/adapters/codex/skills/tilly-*/", "src/adapters/codex/skills/tes-*/", "skill wildcard"),
    Replacement("src/adapters/claude/skills/tilly-*/", "src/adapters/claude/skills/tes-*/", "skill wildcard"),
    Replacement("src/adapters/claude/skills/tilly-*/SKILL.md", "src/adapters/claude/skills/tes-*/SKILL.md", "skill wildcard"),
    Replacement(".tilly/bin", ".tes/bin", "installed runtime path"),
    Replacement(".tilly/field-reports", ".tes/field-reports", "field reports runtime path"),
    Replacement(".tilly/cortex", ".tes/cortex", "cortex derived cache path"),
    Replacement(".tilly/**", ".tes/**", "installed runtime path"),
    Replacement(".tilly/", ".tes/", "installed runtime path"),
    Replacement(".tilly", ".tes", "installed runtime path"),
    Replacement("tilly-cortex-mcp", "tes-cortex-mcp", "mcp server title"),
    Replacement("mcp_servers.tilly-cortex", "mcp_servers.tes-cortex", "mcp config"),
    Replacement("tilly-cortex", "tes-cortex", "mcp server or skill"),
    Replacement("Tilly Field Reports", "TES Field Reports", "field reports name"),
    Replacement("Tilly Field Report", "TES Field Report", "field report name"),
    Replacement("tilly-field-report@1", "tes-field-report@2", "field report schema"),
    Replacement("tilly-field-report", "tes-field-report", "field report issue template"),
    Replacement("tilly-engineering-discipline", "tes-engineering-discipline", "codex skill"),
    Replacement("tilly-guidelines", "tes-guidelines", "adapter guideline"),
    Replacement("tilly-adapter", "tes-adapter", "adapter skill"),
    Replacement("tilly-bench", "tes-bench", "bench skill"),
    Replacement("tilly-cortex", "tes-cortex", "cortex skill"),
    Replacement("tilly-doctor", "tes-doctor", "doctor skill"),
    Replacement("tilly-init", "tes-init", "init skill"),
    Replacement("tilly-mcp", "tes-mcp", "mcp skill"),
    Replacement("Tilly Adapter", "TES Adapter", "skill display name"),
    Replacement("Tilly Bench", "TES Bench", "skill display name"),
    Replacement("Tilly Cortex", "TES Cortex", "skill display name"),
    Replacement("Tilly Doctor", "TES Doctor", "skill display name"),
    Replacement("Tilly Init", "TES Init", "skill display name"),
    Replacement("Tilly MCP", "TES MCP", "skill display name"),
    Replacement("Atualizar a Tilly", "Atualizar TES", "natural language trigger"),
    Replacement("tilly update", "tes update", "natural language trigger"),
    Replacement("update Tilly", "update TES", "natural language trigger"),
    Replacement("atualizar Tilly", "atualizar TES", "natural language trigger"),
    Replacement("initialize Tilly", "initialize TES", "natural language trigger"),
    Replacement("install Tilly", "install TES", "natural language trigger"),
    Replacement("recertify Tilly", "recertify TES", "natural language trigger"),
    Replacement("inicializar Tilly", "inicializar TES", "natural language trigger"),
    Replacement("instalar Tilly", "instalar TES", "natural language trigger"),
    Replacement("recertificar Tilly", "recertificar TES", "natural language trigger"),
    Replacement("Tilly, initialize this project", "TES, initialize this project", "natural language trigger"),
    Replacement("Tilly, inicialize este projeto", "TES, inicialize este projeto", "natural language trigger"),
    Replacement("tilly init", "tes init", "natural language trigger"),
    Replacement("TILLY_FIELD_REPORTS_PRE_PUSH", "TES_FIELD_REPORTS_PRE_PUSH", "environment flag"),
    Replacement("[tilly-discipline]", "[tes-discipline]", "oracle label"),
    Replacement("[tilly-reference]", "[tes-reference]", "oracle label"),
    Replacement("[tilly-update]", "[tes-update]", "oracle label"),
    Replacement("tilly-version", "tes-version", "issue field id"),
    Replacement("tilly-skills", "tes-skills", "plugin id"),
    Replacement("current-tilly-root", "current-tes-root", "root context state"),
    Replacement("tilly-root-drift", "tes-root-drift", "root context state"),
    Replacement("has_tilly", "has_tes", "python identifier"),
    Replacement("-tilly-project-manifest", "-tes-project-manifest", "evidence filename"),
    Replacement("-tilly-project-register", "-tes-project-register", "evidence filename"),
    Replacement("-tilly-initialization", "-tes-initialization", "evidence filename"),
    Replacement("tilly-context-installation", "tes-context-installation", "evidence filename"),
    Replacement("tilly-lexical-curation-v1", "tes-lexical-curation-v1", "cortex model id"),
    Replacement("<tilly-package>", "<tes-package>", "package placeholder"),
    Replacement("tilly-manual-lang", "tes-manual-lang", "manual storage key"),
    Replacement("tilly-navigation", "tes-navigation", "navigation library id"),
    Replacement("pre-push.before-tilly-", "pre-push.before-tes-", "hook backup filename"),
    Replacement('prefix="tilly-platform-surface-', 'prefix="tes-platform-surface-', "tempdir prefix"),
    Replacement('prefix="tilly-field-github-', 'prefix="tes-field-github-', "tempdir prefix"),
    Replacement('prefix="tilly-install-smoke-', 'prefix="tes-install-smoke-', "tempdir prefix"),
    Replacement('prefix="tilly-claude-plugin-oracle-', 'prefix="tes-claude-plugin-oracle-', "tempdir prefix"),
    Replacement('prefix="tilly-codex-context-mesh-', 'prefix="tes-codex-context-mesh-', "tempdir prefix"),
    Replacement('prefix="tilly-update-', 'prefix="tes-update-', "tempdir prefix"),
    Replacement('prefix="tilly-install-', 'prefix="tes-install-', "tempdir prefix"),
    Replacement('prefix=f"tilly-install-smoke-', 'prefix=f"tes-install-smoke-', "tempdir prefix"),
    Replacement('prefix="tilly-root-context-', 'prefix="tes-root-context-', "tempdir prefix"),
    Replacement('prefix="tilly-engineer-skills-', 'prefix="tes-engineer-skills-', "tempdir prefix"),
    Replacement("tilly_", "tes_", "python identifier"),
    Replacement("tilly.", "tes.", "dotted namespace"),
)


def relpath(path: Path, target: Path) -> str:
    return path.relative_to(target).as_posix()


def classify_scope(rel: str) -> str:
    if rel == "scripts/tes_namespace.py":
        return "namespace_oracle"
    if rel == CATALOG_PATH:
        return "migration_catalog"
    if rel == ".tilly" or rel.startswith(".tilly/"):
        return "local_runtime"
    if rel.startswith("docs/evidence/"):
        return "historical_evidence"
    if rel in ACTIVE_FILES or rel.startswith(ACTIVE_PREFIXES):
        return "active_surface"
    if rel.startswith("docs/"):
        return "governed_doc"
    return "supporting_file"


def classify_content_scope(rel: str, line: str) -> str:
    if rel in {"scripts/field_reports.py", "scripts/tes_legacy_retirement.py"} and (
        ".tilly/field-reports" in line or "legacy .tilly field reports" in line
    ):
        return "migration_bridge"
    if rel in {
        "docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md",
        "scripts/install_smoke.py",
        "scripts/tes_update.py",
        "scripts/tes_legacy_retirement.py",
        ".tes/bin/tes_legacy_retirement.py",
    } and (
        "tilly-" in line or "tilly_" in line or "tilly-cortex" in line or ".tilly" in line
    ):
        return "migration_bridge"
    return classify_scope(rel)


def is_active_scope(scope: str) -> bool:
    return scope in {"active_surface", "governed_doc", "supporting_file"}


def should_skip(path: Path, target: Path, include_historical: bool) -> bool:
    rel = relpath(path, target)
    if any(part in SKIPPED_PARTS for part in path.parts):
        return True
    for prefix in DEFAULT_SKIPPED_PREFIXES:
        if not rel.startswith(prefix):
            continue
        if prefix == "docs/evidence/reports/" and include_historical:
            continue
        if prefix == "docs/evidence/reports/" and not include_historical:
            return True
        return True
    if path.suffix not in TEXT_SUFFIXES:
        return True
    return False


def read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def iter_files(target: Path, include_historical: bool) -> list[Path]:
    return sorted(
        path
        for path in target.rglob("*")
        if path.is_file() and not should_skip(path, target, include_historical)
    )


def apply_replacements(value: str, replacements: tuple[Replacement, ...]) -> tuple[str, str | None]:
    result = value
    categories: list[str] = []
    for replacement in replacements:
        if replacement.old in result:
            result = result.replace(replacement.old, replacement.new)
            categories.append(replacement.category)
    return result, ", ".join(dict.fromkeys(categories)) if categories else None


def scan_paths(files: list[Path], target: Path) -> list[PathRename]:
    renames: list[PathRename] = []
    for path in files:
        rel = relpath(path, target)
        target_rel, category = apply_replacements(rel, PATH_REPLACEMENTS)
        if category and target_rel != rel:
            renames.append(PathRename(rel, target_rel, category, classify_scope(rel)))
    return renames


def scan_content(files: list[Path], target: Path) -> list[ContentRename]:
    hits: list[ContentRename] = []
    for path in files:
        text = read_text(path)
        if text is None:
            continue
        rel = relpath(path, target)
        for line_no, line in enumerate(text.splitlines(), start=1):
            scope = classify_content_scope(rel, line)
            matched_positions: set[tuple[int, str]] = set()
            for replacement in CONTENT_REPLACEMENTS:
                start = 0
                while True:
                    index = line.find(replacement.old, start)
                    if index == -1:
                        break
                    key = (index, replacement.old)
                    if key not in matched_positions:
                        snippet = " ".join(line.strip().split())
                        if len(snippet) > 180:
                            snippet = snippet[:177] + "..."
                        hits.append(
                            ContentRename(
                                rel,
                                line_no,
                                replacement.old,
                                replacement.new,
                                replacement.category,
                                scope,
                                snippet,
                            )
                        )
                        matched_positions.add(key)
                    start = index + len(replacement.old)
    return hits


def scan_package_scripts(target: Path) -> list[ScriptRename]:
    package_json = target / "package.json"
    text = read_text(package_json)
    if text is None:
        return []
    try:
        package = json.loads(text)
    except json.JSONDecodeError:
        return []
    renames: list[ScriptRename] = []
    for key, value in sorted((package.get("scripts") or {}).items()):
        if not isinstance(value, str):
            continue
        target_key = key.replace("tilly:", "tes:")
        target_value, category = apply_replacements(value, CONTENT_REPLACEMENTS)
        if target_key != key or target_value != value:
            renames.append(
                ScriptRename(
                    key,
                    target_key,
                    value,
                    target_value,
                    category or "npm command",
                )
            )
    return renames


def active_items(items: list[Any]) -> list[Any]:
    return [item for item in items if is_active_scope(getattr(item, "scope", "active_surface"))]


def remove_empty_parents(path: Path, target: Path) -> list[str]:
    removed: list[str] = []
    current = path.parent
    while current != target and target in current.parents:
        try:
            current.rmdir()
        except OSError:
            break
        removed.append(relpath(current, target))
        current = current.parent
    return removed


def apply_namespace(target: Path, dry_run: bool = True) -> dict[str, Any]:
    target = target.resolve()
    before = build_report(target)
    files = iter_files(target, include_historical=False)
    content_writes: list[dict[str, Any]] = []
    for path in files:
        rel = relpath(path, target)
        if not is_active_scope(classify_scope(rel)):
            continue
        text = read_text(path)
        if text is None:
            continue
        new_text, categories = apply_replacements(text, CONTENT_REPLACEMENTS)
        if new_text == text:
            continue
        content_writes.append({"path": rel, "categories": categories})
        if not dry_run:
            path.write_text(new_text, encoding="utf-8")

    files_after_content = iter_files(target, include_historical=False)
    path_renames = active_items(scan_paths(files_after_content, target))
    moved: list[dict[str, Any]] = []
    removed_dirs: list[str] = []
    failures: list[str] = []
    for item in sorted(path_renames, key=lambda rename: rename.path.count("/"), reverse=True):
        source = target / item.path
        destination = target / item.target
        if not source.exists():
            failures.append(f"source path missing before rename: {item.path}")
            continue
        if destination.exists():
            failures.append(f"target path already exists before rename: {item.target}")
            continue
        moved.append(asdict(item))
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.rename(destination)
            removed_dirs.extend(remove_empty_parents(source, target))

    after = build_report(target) if not dry_run else before
    return {
        "version": VERSION,
        "status": "FAIL" if failures else "PASS",
        "mode": "dry-run" if dry_run else "apply",
        "target": str(target),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "failures": failures,
        "content_writes": content_writes,
        "path_renames": moved,
        "removed_empty_dirs": removed_dirs,
        "before_counts": before["counts"],
        "after_counts": after["counts"],
        "writes": [] if dry_run else [item["path"] for item in content_writes] + [item["target"] for item in moved],
    }


def run_tool(command: list[str], target: Path) -> dict[str, Any]:
    executable = command[0]
    if shutil.which(executable) is None:
        return {"tool": executable, "status": "MISSING", "returncode": None, "stdout": "", "stderr": ""}
    result = subprocess.run(command, cwd=target, text=True, capture_output=True, check=False)
    status = "PASS" if result.returncode in {0, 1} else "FAIL"
    return {
        "tool": executable,
        "status": status,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def normalize_tool_path(raw_path: str) -> str:
    path = raw_path.strip()
    if path.startswith("./"):
        path = path[2:]
    return path


def parse_rg_locations(stdout: str) -> list[RawLocation]:
    locations: list[RawLocation] = []
    for line in stdout.splitlines():
        parts = line.split(":", 3)
        if len(parts) < 4:
            continue
        path, line_no, column, text = parts
        try:
            parsed_line = int(line_no)
            parsed_column = int(column)
        except ValueError:
            continue
        rel = normalize_tool_path(path)
        locations.append(
            RawLocation(
                "rg",
                rel,
                parsed_line,
                parsed_column,
                classify_scope(rel),
                text.strip(),
            )
        )
    return locations


def parse_grep_locations(stdout: str) -> list[RawLocation]:
    locations: list[RawLocation] = []
    for line in stdout.splitlines():
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue
        path, line_no, text = parts
        try:
            parsed_line = int(line_no)
        except ValueError:
            continue
        rel = normalize_tool_path(path)
        locations.append(
            RawLocation(
                "grep",
                rel,
                parsed_line,
                None,
                classify_scope(rel),
                text.strip(),
            )
        )
    return locations


def build_raw_inventory(target: Path, include_historical: bool = False, no_ignore: bool = False) -> dict[str, Any]:
    target = target.resolve()
    find_result = run_tool(
        [
            "find",
            ".",
            "(",
            "-path",
            "./.git",
            "-o",
            "-path",
            "./node_modules",
            "-o",
            "-path",
            "./dist",
            ")",
            "-prune",
            "-o",
            "(",
            "-name",
            "*tilly*",
            "-o",
            "-name",
            "*Tilly*",
            "-o",
            "-name",
            "*TILLY*",
            ")",
            "-print",
        ],
        target,
    )
    rg_command = [
        "rg",
        "--line-number",
        "--column",
        "--no-heading",
        "--hidden",
        "--glob",
        "!node_modules/**",
        "--glob",
        "!dist/**",
        "--glob",
        "!.git/**",
    ]
    if no_ignore:
        rg_command.insert(1, "-uuu")
    if not include_historical:
        rg_command.extend(["--glob", "!docs/evidence/reports/**"])
    rg_command.extend([SEARCH_PATTERN, "."])
    rg_result = run_tool(rg_command, target)
    grep_command = [
        "grep",
        "-RInE",
        "--exclude-dir=.git",
        "--exclude-dir=node_modules",
        "--exclude-dir=dist",
    ]
    if not include_historical:
        grep_command.append("--exclude-dir=reports")
    grep_command.extend([SEARCH_PATTERN, "."])
    grep_result = run_tool(grep_command, target)

    find_paths = sorted(normalize_tool_path(line) for line in find_result["stdout"].splitlines() if line.strip())
    rg_locations = parse_rg_locations(rg_result["stdout"])
    grep_locations = parse_grep_locations(grep_result["stdout"])
    return {
        "target": str(target),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "include_historical": include_historical,
        "no_ignore": no_ignore,
        "pattern": SEARCH_PATTERN,
        "tool_status": {
            "find": {key: find_result[key] for key in ("status", "returncode", "stderr")},
            "rg": {key: rg_result[key] for key in ("status", "returncode", "stderr")},
            "grep": {key: grep_result[key] for key in ("status", "returncode", "stderr")},
        },
        "counts": {
            "find_paths": len(find_paths),
            "rg_locations": len(rg_locations),
            "grep_locations": len(grep_locations),
            "rg_unique_files": len({item.path for item in rg_locations}),
            "grep_unique_files": len({item.path for item in grep_locations}),
        },
        "find_paths": find_paths,
        "rg_locations": [asdict(item) for item in rg_locations],
        "grep_locations": [asdict(item) for item in grep_locations],
        "writes": [],
    }


def build_report(target: Path, include_historical: bool = False, with_raw_inventory: bool = False, no_ignore: bool = False) -> dict[str, Any]:
    target = target.resolve()
    files = iter_files(target, include_historical)
    path_renames = scan_paths(files, target)
    content_renames = scan_content(files, target)
    script_renames = scan_package_scripts(target)
    active_path_renames = active_items(path_renames)
    active_content_renames = active_items(content_renames)
    active_count = len(active_path_renames) + len(active_content_renames) + len(script_renames)
    replacement_fingerprint = hashlib.sha256(
        json.dumps(
            {
                "path": [asdict(item) for item in PATH_REPLACEMENTS],
                "content": [asdict(item) for item in CONTENT_REPLACEMENTS],
            },
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    report = {
        "version": VERSION,
        "status": "FAIL" if active_count else "PASS",
        "target": str(target),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "include_historical": include_historical,
        "replacement_fingerprint": replacement_fingerprint,
        "counts": {
            "scanned_files": len(files),
            "path_renames": len(path_renames),
            "active_path_renames": len(active_path_renames),
            "content_renames": len(content_renames),
            "active_content_renames": len(active_content_renames),
            "package_script_renames": len(script_renames),
            "active_total": active_count,
        },
        "path_renames": [asdict(item) for item in path_renames],
        "package_script_renames": [asdict(item) for item in script_renames],
        "content_renames": [asdict(item) for item in content_renames],
        "allowed_scopes": [
            "namespace_oracle",
            "migration_catalog",
            "historical_evidence",
            "local_runtime",
            "migration_bridge",
        ],
        "skipped_prefixes": list(DEFAULT_SKIPPED_PREFIXES),
        "writes": [],
    }
    if with_raw_inventory:
        report["raw_inventory"] = build_raw_inventory(target, include_historical=include_historical, no_ignore=no_ignore)
    return report


def group_by_path(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        grouped.setdefault(str(item["path"]), []).append(item)
    return dict(sorted(grouped.items()))


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TES Namespace Migration Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        f"Status: `{report['status']}`",
        f"Target: `{report['target']}`",
        f"Replacement fingerprint: `{report['replacement_fingerprint']}`",
        "Writes: none",
        "",
        "## Counts",
        "",
    ]
    for key, value in report["counts"].items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(["", "## Path Renames", ""])
    if report["path_renames"]:
        for item in report["path_renames"]:
            lines.append(
                f"- `{item['path']}` -> `{item['target']}` "
                f"({item['category']}; {item['scope']})"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Package Script Renames", ""])
    if report["package_script_renames"]:
        for item in report["package_script_renames"]:
            lines.append(
                f"- `{item['key']}` -> `{item['target_key']}` "
                f"({item['category']})"
            )
            if item["value"] != item["target_value"]:
                lines.append(f"  - value: `{item['value']}` -> `{item['target_value']}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Content Renames", ""])
    grouped = group_by_path(report["content_renames"])
    if grouped:
        for path, items in grouped.items():
            lines.append(f"### `{path}`")
            for item in items:
                lines.append(
                    f"- line {item['line']}: `{item['old']}` -> `{item['new']}` "
                    f"({item['category']}; {item['scope']})"
                )
                lines.append(f"  - current: `{item['snippet']}`")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Audit Semantics",
            "",
            "- `report` is no-write and exits successfully so maintainers can inspect the blast radius.",
            "- `audit` is no-write and exits non-zero when active surfaces still expose old names.",
            "- `migration_catalog` and `historical_evidence` are recorded but are not active violations.",
        ]
    )
    if "raw_inventory" in report:
        inventory = report["raw_inventory"]
        lines.extend(["", "## Raw Inventory", ""])
        for key, value in inventory["counts"].items():
            lines.append(f"- `{key}`: {value}")
        lines.extend(["", "### Find Paths", ""])
        for path in inventory["find_paths"]:
            lines.append(f"- `{path}`")
        lines.extend(["", "### Ripgrep Locations", ""])
        for item in inventory["rg_locations"]:
            column = item["column"] if item["column"] is not None else "n/a"
            lines.append(f"- `{item['path']}:{item['line']}:{column}` ({item['scope']}): `{item['text']}`")
        lines.extend(["", "### Grep Cross-Check Locations", ""])
        for item in inventory["grep_locations"]:
            lines.append(f"- `{item['path']}:{item['line']}` ({item['scope']}): `{item['text']}`")
    return "\n".join(lines) + "\n"


def render_inventory_markdown(inventory: dict[str, Any]) -> str:
    lines = [
        "# TES Namespace Raw Inventory",
        "",
        f"Generated: `{inventory['generated_at']}`",
        f"Target: `{inventory['target']}`",
        "Writes: none",
        "",
        "## Counts",
        "",
    ]
    for key, value in inventory["counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Tool Status", ""])
    for tool, status in inventory["tool_status"].items():
        lines.append(f"- `{tool}`: {status['status']} returncode={status['returncode']}")
    lines.extend(["", "## Find Paths", ""])
    for path in inventory["find_paths"]:
        lines.append(f"- `{path}`")
    lines.extend(["", "## Ripgrep Locations", ""])
    for item in inventory["rg_locations"]:
        column = item["column"] if item["column"] is not None else "n/a"
        lines.append(f"- `{item['path']}:{item['line']}:{column}` ({item['scope']}): `{item['text']}`")
    lines.extend(["", "## Grep Cross-Check Locations", ""])
    for item in inventory["grep_locations"]:
        lines.append(f"- `{item['path']}:{item['line']}` ({item['scope']}): `{item['text']}`")
    return "\n".join(lines) + "\n"


def emit(report: dict[str, Any], fmt: str, output: Path | None) -> None:
    if fmt == "json":
        text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    elif "path_renames" in report:
        text = render_markdown(report)
    else:
        text = render_inventory_markdown(report)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def run_self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-namespace-") as tempdir:
        target = Path(tempdir)
        (target / "src/adapters/codex/skills/tilly-init").mkdir(parents=True)
        (target / "scripts").mkdir()
        (target / "docs/architecture").mkdir(parents=True)
        (target / "docs/evidence/reports/old").mkdir(parents=True)
        (target / "src/adapters/codex/skills/tilly-init/SKILL.md").write_text(
            "---\nname: tilly-init\n---\nUse /tilly:init and Tilly Init.\n",
            encoding="utf-8",
        )
        (target / "scripts/tilly_init.py").write_text("print('tilly init')\n", encoding="utf-8")
        (target / "package.json").write_text(
            json.dumps(
                {
                    "scripts": {
                        "tilly:init": "python3 scripts/tilly_init.py",
                        "cortex:verify": "python3 scripts/cortex.py verify",
                    }
                }
            ),
            encoding="utf-8",
        )
        (target / CATALOG_PATH).write_text(
            "The old /tilly:init command becomes /tes-init.\n",
            encoding="utf-8",
        )
        (target / "docs/evidence/reports/old/REPORT.md").write_text(
            "Historical report mentioning /tilly:init.\n",
            encoding="utf-8",
        )

        report = build_report(target)
        inventory = build_raw_inventory(target, no_ignore=True)
        if report["status"] != "FAIL":
            failures.append("dirty fixture must fail audit status")
        if not any(item["path"] == "scripts/tilly_init.py" for item in report["path_renames"]):
            failures.append("script path rename was not reported")
        if not any(item["key"] == "tilly:init" and item["target_key"] == "tes:init" for item in report["package_script_renames"]):
            failures.append("package script rename was not reported")
        if not any(item["old"] == "/tilly:init" and item["scope"] == "active_surface" for item in report["content_renames"]):
            failures.append("active prompt command rename was not reported")
        if any(item["scope"] == "historical_evidence" for item in report["content_renames"]):
            failures.append("historical evidence should be skipped by default")
        rendered = render_markdown(report)
        if "TES Namespace Migration Report" not in rendered or "Writes: none" not in rendered:
            failures.append("markdown report missing required heading or no-write claim")
        if not any(path.endswith("scripts/tilly_init.py") for path in inventory["find_paths"]):
            failures.append("find inventory did not report script path")
        if not any(item["path"].endswith("SKILL.md") and item["column"] for item in inventory["rg_locations"]):
            failures.append("rg inventory did not report line and column")
        if not inventory["grep_locations"]:
            failures.append("grep cross-check did not report locations")
        dry_run = apply_namespace(target, dry_run=True)
        if dry_run["status"] != "PASS" or not dry_run["path_renames"] or not dry_run["content_writes"]:
            failures.append("dry-run apply must report planned writes and path renames")
        applied = apply_namespace(target, dry_run=False)
        if applied["status"] != "PASS":
            failures.append("apply fixture must pass")
        post_apply = build_report(target)
        if post_apply["status"] != "PASS":
            failures.append("post-apply fixture must pass namespace audit")

        clean = target / "clean"
        clean.mkdir()
        (clean / "package.json").write_text(json.dumps({"scripts": {"tes:init": "python3 scripts/tes_init.py"}}), encoding="utf-8")
        clean_report = build_report(clean)
        if clean_report["status"] != "PASS":
            failures.append("clean fixture must pass audit status")

    if failures:
        print("[tes-namespace] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("[tes-namespace] PASS")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    def add_report_args(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--target", type=Path, default=ROOT)
        subparser.add_argument("--format", choices=("markdown", "json"), default="markdown")
        subparser.add_argument("--output", type=Path)
        subparser.add_argument("--include-historical", action="store_true")
        subparser.add_argument("--with-raw-inventory", action="store_true")
        subparser.add_argument("--no-ignore", action="store_true")

    report_parser = subparsers.add_parser("report", help="Generate a no-write namespace migration report.")
    add_report_args(report_parser)
    audit_parser = subparsers.add_parser("audit", help="Fail when active old namespace surfaces remain.")
    add_report_args(audit_parser)
    inventory_parser = subparsers.add_parser("inventory", help="Run find, rg, and grep no-write inventory.")
    inventory_parser.add_argument("--target", type=Path, default=ROOT)
    inventory_parser.add_argument("--format", choices=("markdown", "json"), default="json")
    inventory_parser.add_argument("--output", type=Path)
    inventory_parser.add_argument("--include-historical", action="store_true")
    inventory_parser.add_argument("--no-ignore", action="store_true")
    apply_parser = subparsers.add_parser("apply", help="Apply active TES namespace renames after review.")
    apply_parser.add_argument("--target", type=Path, default=ROOT)
    apply_parser.add_argument("--dry-run", action="store_true")
    apply_parser.add_argument("--yes", action="store_true")
    apply_parser.add_argument("--format", choices=("json",), default="json")
    apply_parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        return run_self_test()
    if args.command == "inventory":
        inventory = build_raw_inventory(args.target, include_historical=args.include_historical, no_ignore=args.no_ignore)
        emit(inventory, args.format, args.output)
        return 0
    if args.command == "apply":
        if not args.dry_run and not args.yes:
            print("apply requires --yes unless --dry-run is used", file=sys.stderr)
            return 2
        result = apply_namespace(args.target, dry_run=args.dry_run)
        emit(result, args.format, args.output)
        return 0 if result["status"] == "PASS" else 1
    if args.command not in {"report", "audit"}:
        print("usage: tes_namespace.py [--self-test] {report,audit,inventory,apply}", file=sys.stderr)
        return 2

    report = build_report(
        args.target,
        include_historical=args.include_historical,
        with_raw_inventory=args.with_raw_inventory,
        no_ignore=args.no_ignore,
    )
    emit(report, args.format, args.output)
    if args.command == "audit" and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
