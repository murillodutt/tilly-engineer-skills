#!/usr/bin/env python3
"""Initialize, recertify, and register a target Tilly project."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
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


SCRIPT_PATH = Path(__file__).resolve()
HELPER_ROOT = SCRIPT_PATH.parent
ROOT = SCRIPT_PATH.parents[1]
SOURCE_ROOT = ROOT / "scripts" if (ROOT / "scripts").exists() else HELPER_ROOT
PACKAGE_MODE = SOURCE_ROOT.name == "scripts"
VERSION = "0.3.49"
REGISTER = Path("docs/agents/PROJECT-REGISTER.md")
PROJECT_CONTEXT = Path("docs/agents/PROJECT-CONTEXT.md")
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
MAX_CONTEXT_ANCHORS = 40
MAX_README_SUMMARY_CHARS = 320
MANIFEST_NAMES = {
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "requirements.txt",
    "Gemfile",
    "composer.json",
    "deno.json",
    "bun.lockb",
}
ROOT_CONFIG_ANCHOR_NAMES = {
    "nuxt.config.ts",
    "nuxt.config.js",
    "vite.config.ts",
    "vite.config.js",
    "next.config.js",
    "tsconfig.json",
    "vitest.config.ts",
    "eslint.config.mjs",
    "drizzle.config.ts",
    "docker-compose.yml",
    "docker-compose.dev.yml",
}
DOC_ANCHOR_NAMES = {
    "README.md",
    "README",
    "ARCHITECTURE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "AGENTS.md",
    "CLAUDE.md",
    "CURSOR.md",
}
SOURCE_DIR_HINTS = {
    "app",
    "apps",
    "src",
    "server",
    "client",
    "web",
    "api",
    "lib",
    "packages",
    "modules",
    "components",
    "pages",
    "routes",
    "tests",
    "test",
    "spec",
    "scripts",
    "docs",
}
QUALITY_SCRIPT_TERMS = (
    "lint",
    "typecheck",
    "test",
    "spec",
    "check",
    "build",
    "contract",
    "validate",
)


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


def helper_script(name: str) -> Path:
    package_path = ROOT / "scripts" / name
    if package_path.exists():
        return package_path
    return HELPER_ROOT / name


def gate_passed(gate: dict[str, Any]) -> bool:
    return gate.get("status") in PASSING_GATE_STATUSES


def root_context_gate(target: Path) -> dict[str, Any]:
    command = [sys.executable, str(helper_script("root_context.py")), "analyze", "--target", str(target)]
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
    if relpath.as_posix() in {
        REGISTER.as_posix(),
        PROJECT_CONTEXT.as_posix(),
    }:
        return True
    if len(relpath.parts) >= 3 and relpath.parts[:3] == ("docs", "agents", "evidence"):
        return True
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
        "claude_project_skill": ".claude/skills/tes-guidelines/SKILL.md",
        "claude_plugin_skill": "skills/tes-guidelines/SKILL.md",
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


def safe_read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


def first_markdown_heading(path: Path) -> str | None:
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip()
    except OSError:
            return None
    return None


def clean_markdown_inline(text: str) -> str:
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_`>#]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def trim_summary(text: str, limit: int = MAX_README_SUMMARY_CHARS) -> str:
    if len(text) <= limit:
        return text
    trimmed = text[:limit].rsplit(" ", 1)[0].strip()
    return f"{trimmed}..." if trimmed else text[:limit].strip()


def readme_signal(target: Path) -> dict[str, str] | None:
    for relpath in ("README.md", "README"):
        path = target / relpath
        if not path.exists():
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        heading: str | None = None
        paragraph: list[str] = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if paragraph:
                    break
                continue
            if stripped.startswith("# "):
                heading = stripped[2:].strip()
                continue
            if stripped.startswith(("##", "|", "-", "* ", "!", "<", "```")):
                if paragraph:
                    break
                continue
            if set(stripped) <= {"-", "_", "="}:
                continue
            paragraph.append(stripped)
        summary = trim_summary(clean_markdown_inline(" ".join(paragraph))) if paragraph else ""
        return {
            "source": relpath,
            "heading": heading or "",
            "summary": summary,
        }
    return None


def detect_project_identity(target: Path) -> dict[str, str]:
    readme = readme_signal(target)
    package = safe_read_json(target / "package.json")
    if package:
        name = str(package.get("name") or target.name)
        description = str(package.get("description") or "").strip()
        if not description and readme and readme.get("summary"):
            description = readme["summary"]
        return {
            "name": name,
            "description": description or "unknown",
            "source": "package.json + README" if readme and readme.get("summary") and not package.get("description") else "package.json",
        }

    if readme and readme.get("heading"):
        return {
            "name": readme["heading"],
            "description": readme.get("summary") or "unknown",
            "source": readme["source"],
        }
    for relpath in ("README.md", "README"):
        heading = first_markdown_heading(target / relpath)
        if heading:
            return {
                "name": heading,
                "description": "unknown",
                "source": relpath,
            }

    return {
        "name": target.name,
        "description": "unknown",
        "source": "directory-name",
    }


def dependency_names(target: Path) -> set[str]:
    package = safe_read_json(target / "package.json")
    if not package:
        return set()
    names: set[str] = set()
    for field in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        deps = package.get(field)
        if isinstance(deps, dict):
            names.update(str(name) for name in deps)
    return names


def stack_signals(target: Path) -> list[str]:
    deps = dependency_names(target)
    signals: list[str] = []
    checks = (
        ("nuxt", "Nuxt application"),
        ("@nuxt/ui", "Nuxt UI interface"),
        ("drizzle-orm", "Drizzle ORM persistence"),
        ("pg", "PostgreSQL integration"),
        ("vitest", "Vitest test suite"),
        ("typescript", "TypeScript codebase"),
        ("vue-tsc", "Vue typechecking"),
        ("zod", "Zod validation"),
    )
    for dep, label in checks:
        if dep in deps:
            signals.append(label)
    file_checks = (
        ("docker-compose.yml", "Docker Compose services"),
        ("docker-compose.dev.yml", "Docker Compose dev services"),
        ("pyproject.toml", "Python package metadata"),
        ("go.mod", "Go module"),
        ("Cargo.toml", "Rust crate"),
    )
    for relpath, label in file_checks:
        if (target / relpath).exists():
            signals.append(label)
    return sorted(dict.fromkeys(signals))


def semantic_signals(target: Path) -> list[dict[str, str]]:
    signals: list[dict[str, str]] = []
    readme = readme_signal(target)
    if readme:
        if readme.get("heading"):
            signals.append({"signal": "README heading", "value": readme["heading"], "source": readme["source"]})
        if readme.get("summary"):
            signals.append({"signal": "README summary", "value": readme["summary"], "source": readme["source"]})
    stack = stack_signals(target)
    if stack:
        signals.append({"signal": "Detected stack", "value": ", ".join(stack[:10]), "source": "package/config files"})
    return signals


def package_scripts(target: Path) -> dict[str, str]:
    package = safe_read_json(target / "package.json")
    if not package:
        return {}
    scripts = package.get("scripts")
    if not isinstance(scripts, dict):
        return {}
    return {
        str(name): str(command)
        for name, command in sorted(scripts.items())
        if isinstance(name, str)
    }


def quality_scripts(scripts: dict[str, str]) -> dict[str, str]:
    return {
        name: command
        for name, command in scripts.items()
        if any(term in name.lower() for term in QUALITY_SCRIPT_TERMS)
    }


def anchor_score(record: dict[str, Any]) -> tuple[int, str]:
    relpath = Path(str(record["path"]))
    name = relpath.name
    first = relpath.parts[0] if relpath.parts else ""
    second = relpath.parts[1] if len(relpath.parts) > 1 else ""
    suffix = str(record.get("suffix") or "")
    score = 0
    is_root = len(relpath.parts) == 1
    if is_root and name in DOC_ANCHOR_NAMES:
        score -= 220
    elif name in DOC_ANCHOR_NAMES:
        score -= 60
    if is_root and name in MANIFEST_NAMES:
        score -= 210
    elif name in MANIFEST_NAMES:
        score -= 80
    if is_root and name in ROOT_CONFIG_ANCHOR_NAMES:
        score -= 160
    if first in {"src", "app", "server", "client", "api", "lib", "packages"}:
        score -= 80
    if first in {"docs", ".github", ".agents", ".claude", ".cursor"}:
        score -= 40
    if first in SOURCE_DIR_HINTS:
        score -= 40
    if suffix in {".md", ".mdc", ".json", ".toml", ".yaml", ".yml"}:
        score -= 20
    if "test" in relpath.parts or "tests" in relpath.parts:
        score -= 10
    if first == "docs" and second in {"evidence", "agents"}:
        score += 70
    return (score, str(record["path"]))


def context_anchors(scan: dict[str, Any]) -> list[dict[str, Any]]:
    records = [
        record
        for record in scan["files"]
        if str(record.get("suffix") or "") in {".md", ".mdc", ".json", ".toml", ".yaml", ".yml", ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs"}
    ]
    return sorted(records, key=anchor_score)[:MAX_CONTEXT_ANCHORS]


def territory_summary(scan: dict[str, Any]) -> list[dict[str, Any]]:
    territories: list[dict[str, Any]] = []
    territory_names = {
        Path(str(record["path"])).parts[0]
        for record in scan["files"]
        if len(Path(str(record["path"])).parts) > 1
    }
    for name, count in sorted(scan["top_level"].items(), key=lambda item: (-int(item[1]), item[0])):
        if name in {".git", ".tes"} or name not in territory_names:
            continue
        paths = [
            str(record["path"])
            for record in scan["files"]
            if Path(str(record["path"])).parts and Path(str(record["path"])).parts[0] == name
        ][:6]
        territories.append(
            {
                "name": name,
                "file_count": count,
                "sample_paths": paths,
                "role": infer_territory_role(name, paths),
            }
        )
    return territories[:20]


def infer_territory_role(name: str, paths: list[str]) -> str:
    lowered = name.lower()
    if lowered in {"docs", "doc"}:
        return "documentation and durable explanation"
    if lowered in {".agents", ".claude", ".cursor", ".codex", ".claude-plugin", "skills"}:
        return "agent runtime surface"
    if lowered in {"drizzle", "migrations", "migration"}:
        return "database schema and migration territory"
    if lowered in {"shared", "contracts", "schemas", "types"}:
        return "shared contracts and cross-runtime types"
    if lowered in {"infra", "infrastructure", "ops"}:
        return "infrastructure and environment bootstrap"
    if lowered in {"public", "static", "assets"}:
        return "static assets and public files"
    if lowered in {"labs", "examples", "fixtures"}:
        return "experiments, reproductions, and fixtures"
    if lowered in {"tests", "test", "spec"} or any("/test" in path or "/spec" in path for path in paths):
        return "test or verification territory"
    if lowered in {"scripts", "tools"}:
        return "local automation and oracles"
    if lowered in {"src", "app", "server", "client", "api", "lib", "packages"}:
        return "product/source code territory"
    if lowered in {".github"}:
        return "repository automation and collaboration"
    return "project territory to inspect"


def project_context(scan: dict[str, Any], target: Path, manifest_rel: str) -> dict[str, Any]:
    scripts = package_scripts(target)
    anchors = context_anchors(scan)
    return {
        "identity": detect_project_identity(target),
        "semantic_signals": semantic_signals(target),
        "manifest": manifest_rel,
        "anchors": anchors,
        "territories": territory_summary(scan),
        "package_scripts": scripts,
        "quality_scripts": quality_scripts(scripts),
    }


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
    if not PACKAGE_MODE:
        project_context = helper_script("project_context_oracle.py")
        if project_context.exists():
            return [run([sys.executable, str(project_context), "--self-test"], HELPER_ROOT)]
        return [
            {
                "command": "installed TES package gates",
                "returncode": 0,
                "stdout": "",
                "stderr": "package-only gates unavailable in installed helper mode",
                "status": "PRESERVED",
            }
        ]
    gates = [
        [sys.executable, "scripts/install_smoke.py", "--self-test"],
        [sys.executable, "scripts/platform_surface_oracle.py", "--self-test"],
    ]
    return [run(command, ROOT) for command in gates]


def target_gates(target: Path) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = [run(["git", "diff", "--check"], target)]
    gates.append(root_context_gate(target))
    gate_cwd = ROOT if PACKAGE_MODE else HELPER_ROOT
    gates.append(run([sys.executable, str(helper_script("field_reports.py")), "status", "--target", str(target)], gate_cwd))
    cortex_root = cortex.cortex_path(target)
    if (cortex_root / "CONTRACT.md").exists():
        for command in ("verify", "audit", "rebuild", "curate-plan"):
            extra_args = ["--backend", "lexical"] if command == "curate-plan" else []
            gates.append(
                run(
                    [sys.executable, str(helper_script("cortex.py")), command, "--target", str(target), *extra_args],
                    gate_cwd,
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
| Project context | `{PROJECT_CONTEXT.as_posix()}` |

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
- Treat `docs/agents/PROJECT-CONTEXT.md` as the initial project map for agents:
  update it when major architecture, product, or operational meaning changes.
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


def markdown_table(rows: list[tuple[str, ...]], headers: tuple[str, ...]) -> str:
    if not rows:
        return "| " + " | ".join(headers) + " |\n| " + " | ".join("---" for _ in headers) + " |\n"
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell.replace("\n", " ").replace("|", "\\|") for cell in row) + " |")
    return "\n".join(lines) + "\n"


def write_project_context(target: Path, scan: dict[str, Any], gates: list[dict[str, Any]], manifest_rel: str) -> str:
    context = project_context(scan, target, manifest_rel)
    identity = context["identity"]
    signals = context["semantic_signals"]
    anchors = context["anchors"]
    territories = context["territories"]
    scripts = context["package_scripts"]
    qscripts = context["quality_scripts"]
    surface_rows = [
        (name, "present" if present else "missing")
        for name, present in sorted(scan["surfaces"].items())
    ]
    anchor_rows = [
        (str(anchor["path"]), str(anchor.get("suffix") or "[none]"), str(anchor["bytes"]))
        for anchor in anchors
    ]
    territory_rows = [
        (
            str(territory["name"]),
            str(territory["role"]),
            str(territory["file_count"]),
            ", ".join(f"`{path}`" for path in territory["sample_paths"]) or "none",
        )
        for territory in territories
    ]
    script_rows = [(name, command) for name, command in scripts.items()]
    quality_rows = [(name, command) for name, command in qscripts.items()]
    gate_rows = [(gate["command"], gate["status"]) for gate in gates]
    signal_rows = [(item["signal"], item["value"], item["source"]) for item in signals]
    deep_reads = "\n".join(f"- `{anchor['path']}`" for anchor in anchors[:12]) or "- none"

    return f"""# Tilly Project Context

Generated: `{scan['generated_at']}`

This is the initial project context compiled by `/tes-init`. It is a durable
starting map for agents, not a substitute for the source files. Agents should
read this before broad project work, then open the cited anchors and update the
context when new durable understanding is learned.

## Identity

| Field | Value |
|-------|-------|
| Name | `{identity['name']}` |
| Description | `{identity['description']}` |
| Identity source | `{identity['source']}` |
| Target | `{scan['target']}` |
| Git HEAD | `{scan['git_head']}` |
| Manifest | `{manifest_rel}` |

## Initial Semantic Signals

These signals are deterministic extracts from high-signal project files. They
are starting evidence for the active agent, not a final semantic analysis.

{markdown_table(signal_rows, ("Signal", "Value", "Source"))}
## Maximum-Depth Initialization Contract

- `/tes-init` must initialize the project, not only install TES runtime files.
- The project was inventoried through tracked and unignored files.
- Raw project files remain the source of truth; this context cites anchors
  instead of copying code or secrets.
- Unknowns stay explicit. Do not invent product, architecture, compliance, or
  deployment claims not supported by project files.

## Active Agent Refinement Contract

- Deterministic scaffold: `tes_init.py` creates the inventory, anchors,
  scripts, runtime surfaces, evidence manifest, and initial gaps.
- Semantic refinement: the active agent must open the strongest listed anchors
  before claiming deep project understanding for non-trivial projects.
- After reading anchors, refine this file with supported product domain,
  architecture, operational boundaries, validation gates, and durable unknowns.
- If anchor reading or local tools are blocked, report
  `Project context: NEEDS_REVIEW` with the blocker instead of claiming depth.

## Coverage

| Field | Value |
|-------|-------|
| File count | `{scan['file_count']}` |
| Total bytes | `{scan['total_bytes']}` |
| Anchor count | `{len(anchors)}` |
| Gate status | `{'PASS' if all(gate_passed(gate) for gate in gates) else 'NEEDS_REVIEW'}` |

## Project Territories

{markdown_table(territory_rows, ("Territory", "Initial role", "Files", "Sample anchors"))}
## Source Anchors Read First

{markdown_table(anchor_rows, ("Path", "Kind", "Bytes"))}
## Runtime And Governance Surfaces

{markdown_table(surface_rows, ("Surface", "Status"))}
## Package Scripts

{markdown_table(script_rows, ("Script", "Command"))}
## Quality And Certification Scripts

{markdown_table(quality_rows, ("Script", "Command"))}
## Recertification Gates

{markdown_table(gate_rows, ("Command", "Status"))}
## Recommended Deep Reads

{deep_reads}

## Open Context Questions

- What is the project domain in one sentence, based on product docs and source
  entrypoints?
- Which directories define the runtime boundary, persistence boundary, and
  external integration boundary?
- Which commands are the smallest safe quality gates before commit?
- Which facts should be promoted into Cortex cells after human review?

## Maintenance Rule

Update this file when project meaning changes: architecture reshapes, new
runtime surfaces, major scripts, public API boundaries, test strategy,
deployment model, or agent governance. Keep detailed file inventories in
`docs/agents/evidence/**`; keep durable memory in `docs/agents/cortex/**`.
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
project, and wrote a project register, project context, and full manifest.

## Target

| Field | Value |
|-------|-------|
| Target | `{target}` |
| Git HEAD | `{scan['git_head']}` |
| File count | `{scan['file_count']}` |
| Manifest | `{manifest_rel}` |
| Project context | `{PROJECT_CONTEXT.as_posix()}` |

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
        PROJECT_CONTEXT.as_posix(),
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
            "message": "tes init writes a project register, project context, and evidence manifest; rerun with --yes",
        }

    evidence_dir = target / EVIDENCE_DIR
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (target / REGISTER).parent.mkdir(parents=True, exist_ok=True)

    manifest_path = evidence_dir / f"{stamp}-tes-project-manifest.json"
    evidence_path = evidence_dir / f"{stamp}-tes-initialization.md"
    manifest_rel = rel(manifest_path, target)
    (target / PROJECT_CONTEXT).parent.mkdir(parents=True, exist_ok=True)

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
    (target / PROJECT_CONTEXT).write_text(
        write_project_context(target, bootstrap, [bootstrap_gate], manifest_rel),
        encoding="utf-8",
    )
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
    project_context_text = write_project_context(target, scan, gates, manifest_rel)
    evidence_text = write_evidence(target, scan, gates, planned_writes, manifest_rel)

    manifest_path.write_text(json.dumps(scan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target / REGISTER).write_text(register_text, encoding="utf-8")
    (target / PROJECT_CONTEXT).write_text(project_context_text, encoding="utf-8")
    evidence_path.write_text(evidence_text, encoding="utf-8")

    actual_writes = [
        REGISTER.as_posix(),
        PROJECT_CONTEXT.as_posix(),
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
            "project_context": PROJECT_CONTEXT.as_posix(),
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
        (target / "package.json").write_text(
            json.dumps(
                {
                    "name": "tes-init-fixture",
                    "description": "fixture package for project context",
                    "scripts": {
                        "lint": "echo lint",
                        "test": "echo test",
                        "build": "echo build",
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (target / "src").mkdir()
        (target / "src/app.py").write_text("print('fixture')\n", encoding="utf-8")
        (target / "AGENTS.md").write_text(
            "# Project Agent Rules\n\nUse local project governance before package defaults.\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)
        subprocess.run(["git", "add", "README.md", "package.json", "src/app.py"], cwd=target, text=True, capture_output=True, check=False)
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
        context_text = (target / PROJECT_CONTEXT).read_text(encoding="utf-8") if (target / PROJECT_CONTEXT).exists() else ""
        for term in (
            "Maximum-Depth Initialization Contract",
            "Active Agent Refinement Contract",
            "tes-init-fixture",
            "package.json",
            "src/app.py",
            "lint",
            "Recommended Deep Reads",
        ):
            if term not in context_text:
                failures.append(f"project context missing term: {term}")
        if result["status"] != "PASS":
            failures.append(f"expected PASS, got {result['status']}")
        if not any(gate["status"] == "PRESERVED" for gate in result["gates"]):
            failures.append("project-owned root context must close as PRESERVED during init")

    with tempfile.TemporaryDirectory(prefix="tes-init-readme-identity-") as tempdir:
        target = Path(tempdir)
        (target / "README.md").write_text(
            "# README Identity Fixture\n\nA portable project whose package manifest omits a description.\n",
            encoding="utf-8",
        )
        (target / "package.json").write_text('{"name":"readme-identity-fixture"}\n', encoding="utf-8")
        identity = detect_project_identity(target)
        if identity["description"] == "unknown":
            failures.append("project identity must derive README prose when package description is absent")
        if "README" not in identity["source"]:
            failures.append("project identity source must mention README when README prose supplies description")

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
        "self_test_mode": "package" if PACKAGE_MODE else "installed",
        "coverage": "source-package-contract" if PACKAGE_MODE else "installed-helper-contract",
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
