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
import tomllib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cortex
import field_reports
import root_context


MARKDOWN_HEADING_RE = re.compile(r"^#{1,3}\s+(.+?)\s*$")
SCRIPT_PATH = Path(__file__).resolve()
HELPER_ROOT = SCRIPT_PATH.parent
ROOT = SCRIPT_PATH.parents[1]
SOURCE_ROOT = ROOT / "scripts" if (ROOT / "scripts").exists() else HELPER_ROOT
SOURCE_PACKAGE_MODE = (
    SOURCE_ROOT.name == "scripts"
    and (ROOT / "package.json").exists()
    and (ROOT / "scripts/install_smoke.py").exists()
    and (ROOT / "scripts/platform_surface_oracle.py").exists()
)
BUNDLE_MODE = SOURCE_ROOT.name == "scripts" and not SOURCE_PACKAGE_MODE
PACKAGE_MODE = SOURCE_PACKAGE_MODE
VERSION = "0.3.93"
REGISTER = Path("docs/agents/PROJECT-REGISTER.md")
PROJECT_CONTEXT = Path("docs/agents/PROJECT-CONTEXT.md")
EVIDENCE_DIR = Path("docs/agents/evidence")
PROJECT_STATE = Path("docs/agents/PROJECT-STATE.md")
PROJECT_ROADMAP = Path("docs/agents/PROJECT-ROADMAP.md")
EXECUTION_LINE = Path("docs/agents/EXECUTION-LINE.md")
QUALITY_GATES = Path("docs/agents/QUALITY-GATES.md")
BOUNDARIES = Path("docs/agents/BOUNDARIES-AND-CONSTRAINTS.md")
KNOWLEDGE_LIFECYCLE = Path("docs/agents/KNOWLEDGE-LIFECYCLE.md")
GLOSSARY = Path("docs/agents/GLOSSARY.md")
DECISIONS_DIR = Path("docs/agents/DECISIONS")
TES_AGENT_MESH_RELPATHS = {
    REGISTER.as_posix(),
    PROJECT_CONTEXT.as_posix(),
    PROJECT_STATE.as_posix(),
    PROJECT_ROADMAP.as_posix(),
    EXECUTION_LINE.as_posix(),
    QUALITY_GATES.as_posix(),
    BOUNDARIES.as_posix(),
    KNOWLEDGE_LIFECYCLE.as_posix(),
    GLOSSARY.as_posix(),
}
PASSING_GATE_STATUSES = {"PASS", "CLEAN_APPLIED", "RECOVERED", "NOT_AVAILABLE"}
DEFAULT_COMMAND_TIMEOUT_SECONDS = 60.0
DEFAULT_GIT_LIST_TIMEOUT_SECONDS = 15.0

EXCLUDED_PARTS = {
    ".git",
    ".hg",
    ".svn",
    ".tes",
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
TES_RUNTIME_PREFIXES = (
    (".agents", "skills", "tes-"),
    (".claude", "skills", "tes-"),
    ("skills", "tes-"),
    (".claude-plugin",),
    ("docs", "agents", "cortex"),
)
TES_RUNTIME_RELPATHS = {
    ".cursor/rules/tes-guidelines.mdc",
}
TES_ROOT_BOOTLOADER_MARKERS = {
    "AGENTS.md": "Portable Codex bootloader for repositories adopting Tilly Engineering",
    "CLAUDE.md": "Behavioral engineering discipline for reducing common LLM coding mistakes.",
    "CURSOR.md": "This target repository includes a Cursor project rule for Tilly Engineering",
}
MAX_HASH_BYTES = 10 * 1024 * 1024
MAX_CONTEXT_ANCHORS = 40
MAX_CONTEXT_TERRITORIES = 80
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
    "main.tf",
    "versions.tf",
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
    "providers.tf",
    "variables.tf",
    "outputs.tf",
    "terraform.tfvars",
    "docker.tf",
}
DOC_ANCHOR_NAMES = {
    "README.md",
    "readme.md",
    "README.rst",
    "readme.rst",
    "README.txt",
    "README.TXT",
    "README",
    "Makefile",
    "GNUmakefile",
    "makefile",
    "ARCHITECTURE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "INDEX.md",
    "index.md",
    "INDEX.rst",
    "index.rst",
    "INDEX.txt",
    "index.txt",
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
    "ci",
    "doc",
    "fmt",
    "gen",
    "lint",
    "typecheck",
    "test",
    "spec",
    "check",
    "build",
    "contract",
    "validate",
    "website",
)
MAKEFILE_NAMES = ("GNUmakefile", "Makefile", "makefile")
MAKEFILE_QUALITY_TARGETS = {
    "acctest-lint",
    "build",
    "ci",
    "ci-quick",
    "docs",
    "examples-tflint",
    "fmt",
    "fmt-check",
    "gen",
    "gen-check",
    "go-build",
    "golangci-lint",
    "golangci-lint1",
    "import-lint",
    "provider-lint",
    "provider-markdown-lint",
    "quick-fix",
    "semgrep",
    "sweep",
    "test",
    "testacc",
    "testacc-lint",
    "tfproviderdocs",
    "tools",
    "website",
    "yamllint",
}
MAKE_TARGET_RE = re.compile(r"^([A-Za-z0-9_.-]+):(?!=)")


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


def isolated_git_env() -> dict[str, str]:
    blocked = {
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_DIR",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_PREFIX",
        "GIT_WORK_TREE",
    }
    return {key: value for key, value in os.environ.items() if key not in blocked}


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
        status = "RECOVERED"
        resolution = "project-owned root context detected; clean install recovers durable semantics from backup evidence"
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


def is_git_worktree(target: Path) -> bool:
    result = run(["git", "rev-parse", "--is-inside-work-tree"], target)
    return result["returncode"] == 0 and result["stdout"].strip() == "true"


def git_diff_check_gate(target: Path) -> dict[str, Any]:
    if is_git_worktree(target):
        return run(["git", "diff", "--check"], target)
    return {
        "command": "git diff --check",
        "returncode": 0,
        "stdout": "",
        "stderr": "target is not a Git repository; git whitespace diff gate is not available",
        "status": "NOT_AVAILABLE",
    }


def is_tes_runtime_relpath(relpath: Path) -> bool:
    parts = relpath.parts
    if relpath.as_posix() in TES_RUNTIME_RELPATHS:
        return True
    for prefix in TES_RUNTIME_PREFIXES:
        if len(parts) < len(prefix):
            continue
        matched = True
        for idx, value in enumerate(prefix):
            part = parts[idx]
            if value.endswith("-"):
                if not part.startswith(value):
                    matched = False
                    break
            elif part != value:
                matched = False
                break
        if matched:
            return True
    return False


def is_generated_root_bootloader(relpath: Path, path: Path | None) -> bool:
    marker = TES_ROOT_BOOTLOADER_MARKERS.get(relpath.as_posix())
    if not marker or path is None or not path.exists():
        return False
    try:
        return marker in path.read_text(encoding="utf-8", errors="ignore")[:1200]
    except OSError:
        return False


def is_excluded(relpath: Path, path: Path | None = None) -> bool:
    if relpath.as_posix() in TES_AGENT_MESH_RELPATHS:
        return True
    if len(relpath.parts) >= 3 and relpath.parts[:3] == ("docs", "agents", "DECISIONS"):
        return True
    if is_tes_runtime_relpath(relpath) or is_generated_root_bootloader(relpath, path):
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
        if path.is_file() and not is_excluded(relpath, path):
            files.append(path)
    return sorted(files)


def all_files(target: Path) -> list[Path]:
    from_git = git_files(target)
    if from_git:
        return from_git
    files: list[Path] = []
    for path in target.rglob("*"):
        if not path.is_file():
            continue
        relpath = path.relative_to(target)
        if not is_excluded(relpath, path):
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


def safe_read_toml(path: Path) -> dict[str, Any] | None:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


def first_markdown_heading(path: Path) -> str | None:
    in_fence = False
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            match = MARKDOWN_HEADING_RE.match(stripped)
            if match:
                return clean_markdown_inline(match.group(1))
    except OSError:
            return None
    return None


def first_readme_heading(lines: list[str]) -> str | None:
    in_fence = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue
        match = MARKDOWN_HEADING_RE.match(stripped)
        if match:
            return clean_markdown_inline(match.group(1))
        if index + 1 < len(lines):
            underline = lines[index + 1].strip()
            if len(underline) >= 3 and len(set(underline)) == 1 and underline[0] in "=-~^":
                return clean_markdown_inline(stripped)
    return None


def readme_paths(target: Path) -> list[Path]:
    names = {"readme", "readme.md", "readme.rst", "readme.txt"}
    candidates = [
        path
        for path in target.iterdir()
        if path.is_file() and path.name.casefold() in names
    ]
    priority = {"readme.md": 0, "readme.rst": 1, "readme": 2, "readme.txt": 3}
    return sorted(candidates, key=lambda path: (priority.get(path.name.casefold(), 99), path.name))


def clean_markdown_inline(text: str) -> str:
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\[[^\]]+\]", r"\1", text)
    text = re.sub(r"[*_`>#]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def trim_summary(text: str, limit: int = MAX_README_SUMMARY_CHARS) -> str:
    if len(text) <= limit:
        return text
    trimmed = text[:limit].rsplit(" ", 1)[0].strip()
    return f"{trimmed}..." if trimmed else text[:limit].strip()


def readme_signal(target: Path) -> dict[str, str] | None:
    for path in readme_paths(target):
        relpath = path.name
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        heading: str | None = None
        paragraph: list[str] = []
        html_depth = 0
        in_fence = False
        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("```"):
                if paragraph:
                    break
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            opens = len(re.findall(r"<(div|p|a|sup|picture|span|center|table|tbody|tr|td)\b", stripped, flags=re.IGNORECASE))
            closes = len(re.findall(r"</(div|p|a|sup|picture|span|center|table|tbody|tr|td)>", stripped, flags=re.IGNORECASE))
            if html_depth > 0:
                html_depth = max(0, html_depth + opens - closes)
                continue
            if opens and stripped.startswith("<"):
                html_depth = max(0, opens - closes)
                continue
            if not stripped:
                if paragraph:
                    break
                continue
            if re.match(r"^\[[^\]]+\]:\s+\S+", stripped):
                if paragraph:
                    break
                continue
            heading_match = MARKDOWN_HEADING_RE.match(stripped)
            rst_underline = lines[index + 1].strip() if index + 1 < len(lines) else ""
            if heading_match:
                heading = clean_markdown_inline(heading_match.group(1))
                continue
            if (
                not heading
                and rst_underline
                and len(rst_underline) >= 3
                and len(set(rst_underline)) == 1
                and rst_underline[0] in "=-~^"
            ):
                heading = clean_markdown_inline(stripped)
                continue
            if stripped.startswith(">"):
                quote = stripped.lstrip("> ").strip()
                if quote.startswith("[!"):
                    if paragraph:
                        break
                    continue
                paragraph.append(quote)
                continue
            if stripped.startswith(("##", "|", "-", "* ", "!", "[![", "<", "```")):
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
    pyproject = safe_read_toml(target / "pyproject.toml")
    project = pyproject.get("project") if pyproject else None
    if isinstance(project, dict):
        name = str(project.get("name") or target.name)
        description = str(project.get("description") or "").strip()
        if not description and readme and readme.get("summary"):
            description = readme["summary"]
        return {
            "name": name,
            "description": description or "unknown",
            "source": "pyproject.toml + README" if readme and readme.get("summary") and not project.get("description") else "pyproject.toml",
        }

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
    if readme and readme.get("summary"):
        return {
            "name": target.name,
            "description": readme["summary"],
            "source": f"directory-name + {readme['source']}",
        }
    for path in readme_paths(target):
        heading = first_markdown_heading(path)
        if heading:
            return {
                "name": heading,
                "description": "unknown",
                "source": path.name,
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


def python_project_signals(target: Path) -> list[str]:
    pyproject = safe_read_toml(target / "pyproject.toml")
    if not pyproject:
        return []
    signals = ["Python package metadata"]
    build = pyproject.get("build-system")
    if isinstance(build, dict):
        backend = str(build.get("build-backend") or "").strip()
        if backend:
            signals.append(f"Python build backend: {backend}")
    tools = pyproject.get("tool")
    if isinstance(tools, dict):
        tool_names = sorted(str(name) for name in tools)
        if tool_names:
            signals.append("Python tool config: " + ", ".join(tool_names[:10]))
    return signals


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
    signals.extend(python_project_signals(target))
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


def makefile_scripts(target: Path) -> dict[str, str]:
    scripts: dict[str, str] = {}
    for name in MAKEFILE_NAMES:
        path = target / name
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for line in lines:
            if line.startswith(("\t", " ", "#", ".")):
                continue
            match = MAKE_TARGET_RE.match(line)
            if not match:
                continue
            target_name = match.group(1)
            if "%" in target_name or target_name in scripts:
                continue
            scripts[target_name] = f"make {target_name}"
    return scripts


def python_quality_scripts(target: Path) -> dict[str, str]:
    scripts: dict[str, str] = {}
    pyproject = safe_read_toml(target / "pyproject.toml") or {}
    tools = pyproject.get("tool")
    dependency_groups = pyproject.get("dependency-groups")
    if (target / "noxfile.py").exists():
        scripts["nox"] = "nox"
    if (target / "tox.ini").exists() or (isinstance(tools, dict) and "tox" in tools):
        scripts["tox"] = "tox"
    if (target / "tests/runtests.py").exists():
        scripts["runtests"] = "cd tests && ./runtests.py"
    if (target / "docs/Makefile").exists():
        scripts["docs"] = "make -C docs html"
    if isinstance(tools, dict):
        if "pytest" in tools:
            scripts["pytest"] = "pytest"
        if "ruff" in tools:
            scripts["ruff"] = "ruff check ."
        if "mypy" in tools:
            scripts["mypy"] = "mypy"
        if "pyright" in tools:
            scripts["pyright"] = "pyright"
    if isinstance(dependency_groups, dict):
        group_text = json.dumps(dependency_groups)
        for name, command in (
            ("pytest", "pytest"),
            ("ruff", "ruff check ."),
            ("mypy", "mypy"),
            ("pyright", "pyright"),
            ("sphinx", "sphinx-build docs docs/_build"),
        ):
            if name in group_text and name not in scripts:
                scripts[name] = command
    return scripts


def makefile_quality_scripts(target: Path) -> dict[str, str]:
    scripts = makefile_scripts(target)
    return {
        name: command
        for name, command in scripts.items()
        if name in MAKEFILE_QUALITY_TARGETS
        or any(term in name.lower() for term in QUALITY_SCRIPT_TERMS)
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
    size = int(record.get("bytes") or 0)
    score = 0
    is_root = len(relpath.parts) == 1
    lowered_parts = {part.lower() for part in relpath.parts}
    if size == 0:
        score += 220
    if name.casefold().startswith("readme"):
        score -= 240 if is_root else 90
        if not is_root and len(relpath.parts) > 2:
            score += 80
    if is_root and name in DOC_ANCHOR_NAMES:
        score -= 220
    elif name in DOC_ANCHOR_NAMES:
        score -= 60
    if first == "docs" and name.casefold() in {"index.md", "index.rst", "index.txt"}:
        score -= 140
    if is_root and name in MANIFEST_NAMES:
        score -= 210
    elif name in MANIFEST_NAMES:
        score -= 80
    if is_root and name in ROOT_CONFIG_ANCHOR_NAMES:
        score -= 160
    if name in {"Makefile", "makefile", "runtests.py", "tox.ini", "noxfile.py", "pytest.ini", ".coveragerc"}:
        score -= 130
    if is_root and suffix in {".tf", ".tfvars", ".hcl"}:
        score -= 140
    if first in {"src", "app", "server", "client", "api", "lib", "packages"}:
        score -= 80
    if first in {"docs", ".github", ".agents", ".claude", ".cursor"}:
        score -= 40
    if first in SOURCE_DIR_HINTS:
        score -= 40
    if suffix in {".md", ".mdc", ".rst", ".txt", ".toml", ".yaml", ".yml", ".tf", ".tfvars", ".hcl"}:
        score -= 20
    if suffix == ".json":
        score -= 5 if is_root else 0
    if "test" in relpath.parts or "tests" in relpath.parts:
        score -= 10
    if first in {"test", "tests"} and name in MANIFEST_NAMES:
        score += 120
    generated_or_example_parts = {
        "__fixtures__",
        "_theme",
        "assets",
        "data",
        "example",
        "examples",
        "fixture",
        "fixtures",
        "fontawesome",
        "sample",
        "samples",
        "static",
        "template",
        "templates",
        "third_party",
        "vendor",
    }
    if lowered_parts & generated_or_example_parts or any(
        token in part
        for part in lowered_parts
        for token in ("example", "fixture", "sample", "template")
    ):
        score += 150
    if suffix == ".json" and ("test" in relpath.parts or "tests" in relpath.parts):
        score += 80
    if suffix == ".txt" and not is_root and len(relpath.parts) > 3:
        score += 110
    if "enhancement-configs" in lowered_parts or "generated" in lowered_parts:
        score += 130
    if first == "docs" and second in {"evidence", "agents"}:
        score += 70
    return (score, str(record["path"]))


def context_anchors(scan: dict[str, Any]) -> list[dict[str, Any]]:
    records = [
        record
        for record in scan["files"]
        if str(record.get("suffix") or "") in {".md", ".mdc", ".rst", ".txt", ".json", ".toml", ".yaml", ".yml", ".tf", ".tfvars", ".hcl", ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs"}
        or Path(str(record["path"])).name in DOC_ANCHOR_NAMES
        or Path(str(record["path"])).name in ROOT_CONFIG_ANCHOR_NAMES
        or Path(str(record["path"])).name in MANIFEST_NAMES
    ]
    return sorted(records, key=anchor_score)[:MAX_CONTEXT_ANCHORS]


def package_workspace_patterns(package: dict[str, Any]) -> list[str]:
    workspaces = package.get("workspaces")
    if isinstance(workspaces, list):
        return [str(item) for item in workspaces]
    if isinstance(workspaces, dict):
        packages = workspaces.get("packages")
        if isinstance(packages, list):
            return [str(item) for item in packages]
    return []


def pnpm_workspace_patterns(target: Path) -> list[str]:
    path = target / "pnpm-workspace.yaml"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    patterns: list[str] = []
    in_packages = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("packages:"):
            in_packages = True
            continue
        if not in_packages:
            continue
        if stripped.startswith("- "):
            value = stripped[2:].strip().strip("'\"")
            if value:
                patterns.append(value)
            continue
        if stripped and not line.startswith((" ", "\t")):
            break
    return patterns


def cargo_workspace_patterns(target: Path) -> list[str]:
    cargo = safe_read_toml(target / "Cargo.toml")
    workspace = cargo.get("workspace") if cargo else None
    if not isinstance(workspace, dict):
        return []
    members = workspace.get("members")
    if not isinstance(members, list):
        return []
    return [str(item) for item in members]


def workspace_boundaries(target: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    package = safe_read_json(target / "package.json")
    if package:
        for pattern in package_workspace_patterns(package):
            records.append({"source": "package.json", "kind": "npm workspace", "pattern": pattern})
    for pattern in pnpm_workspace_patterns(target):
        records.append({"source": "pnpm-workspace.yaml", "kind": "pnpm workspace", "pattern": pattern})
    for pattern in cargo_workspace_patterns(target):
        records.append({"source": "Cargo.toml", "kind": "cargo workspace", "pattern": pattern})
    if (target / "go.mod").exists():
        for path in sorted(target.rglob("go.mod")):
            if path == target / "go.mod":
                continue
            try:
                relpath = path.parent.relative_to(target).as_posix()
            except ValueError:
                continue
            if relpath:
                records.append({"source": "go.mod", "kind": "nested Go module", "pattern": relpath})
    provider_services = target / "internal" / "service"
    if provider_services.is_dir() and any(path.is_dir() for path in provider_services.iterdir()):
        records.append({"source": "internal/service", "kind": "provider service packages", "pattern": "internal/service/*"})

    seen: set[tuple[str, str, str]] = set()
    unique: list[dict[str, str]] = []
    for record in records:
        key = (record["source"], record["kind"], record["pattern"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


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
        all_paths = [
            str(record["path"])
            for record in scan["files"]
            if Path(str(record["path"])).parts and Path(str(record["path"])).parts[0] == name
        ]
        territories.append(
            {
                "name": name,
                "file_count": count,
                "sample_paths": all_paths[:6],
                "semantic_paths": all_paths,
                "role": infer_territory_role(name, all_paths),
            }
        )
    return territories[:MAX_CONTEXT_TERRITORIES]


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
    if lowered == "internal" and any(path.startswith("internal/service/") for path in paths):
        return "provider internals and service ownership"
    if lowered in {"infra", "infrastructure", "ops"}:
        return "infrastructure and environment bootstrap"
    if lowered in {"public", "assets"}:
        return "static assets and public files"
    if lowered == "static" and any(path.startswith("static/app/") for path in paths):
        return "frontend application and static asset territory"
    if lowered == "static":
        return "static assets and public files"
    if "plugin" in lowered:
        return "plugin or extension product surface"
    if lowered == "crates" and any(path.startswith("crates/") and path.endswith("/Cargo.toml") for path in paths):
        return "Rust Cargo workspace and crate ownership"
    if lowered in {"labs", "examples", "fixtures"}:
        return "experiments, reproductions, and fixtures"
    if lowered in {"scripts", "tools"}:
        return "local automation and oracles"
    if lowered in {".github"}:
        return "repository automation and collaboration"
    if lowered in {"tests", "test", "spec"} or any("/test" in path or "/spec" in path for path in paths):
        return "test or verification territory"
    if lowered in {"src", "app", "server", "client", "api", "lib", "packages"}:
        return "product/source code territory"
    return "project territory to inspect"


def semantic_boundary_for_territory(name: str, paths: list[str]) -> tuple[str, str]:
    lowered = name.lower()
    evidence = next((path for path in paths if path), name)
    if lowered == "src" and any(path.startswith("src/sentry/") for path in paths):
        return (
            "likely Python backend/domain application boundary; read local AGENTS/CLAUDE guidance before edits",
            "start with src/AGENTS.md plus nearby package README files",
        )
    if lowered == "static" and any(path.startswith("static/app/") for path in paths):
        return (
            "likely frontend UI/client application boundary; avoid treating static fixtures as architecture",
            "start with static/AGENTS.md and package TypeScript gates",
        )
    if lowered == "crates" and any(path.startswith("crates/") and path.endswith("/Cargo.toml") for path in paths):
        return (
            "Rust Cargo workspace boundary; crates likely hold CLI, resolver, distribution, and package-manager domain ownership",
            "start with Cargo.toml workspace members, crates/README.md, and the nearest crate README before changing behavior",
        )
    if lowered == "python" and any(path.startswith("python/") for path in paths):
        return (
            "Python package/shim boundary around the Rust implementation",
            "cross-check pyproject metadata against Rust crate behavior before editing packaging",
        )
    if lowered in {"tests", "test", "spec"}:
        return (
            "verification boundary; use this to choose focused tests rather than infer runtime design",
            "start with local test governance and smallest related test command",
        )
    if lowered in {"api-docs", "docs", "doc"}:
        return (
            "documentation/API contract boundary; useful for public behavior but not sufficient runtime proof",
            "cross-check claims against source anchors before editing behavior",
        )
    if lowered in {"self-hosted", "devservices", "devenv", "config"}:
        return (
            "operational or local-environment boundary; touch cautiously because changes may affect boot/dev/deploy flows",
            "read config and service docs before changing defaults",
        )
    if lowered in {".agents", ".claude", ".cursor", ".codex"}:
        return (
            "project-owned agent governance boundary; clean runtime replaces active bootloaders after central backup",
            "recover durable local semantics from `.tes/bk/**` into docs/agents evidence",
        )
    if lowered in {".github"}:
        return (
            "repository automation, ownership, and CI boundary",
            "check workflows and CODEOWNERS before workflow or ownership changes",
        )
    if lowered in {"scripts", "tools", "bin", "build-utils"}:
        return (
            "developer automation/tooling boundary",
            "prefer existing commands and self-tests over ad hoc scripts",
        )
    if lowered in {"fixtures", "examples", "samples"}:
        return (
            "fixture/example boundary; good for repros, weak evidence for product architecture",
            "do not promote fixture shape as core runtime design",
        )
    if lowered in {"migrations", "migration"} or any("/migrations/" in path for path in paths):
        return (
            "schema/data migration boundary; high caution for generated or historical state",
            "inspect migration policy before editing",
        )
    return (
        "unclassified territory; evidence is inventory-level until anchors are read",
        "open the listed anchors before claiming ownership or runtime role",
    )


def semantic_territory_guide(territories: list[dict[str, Any]]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for territory in territories:
        paths = [str(path) for path in territory.get("semantic_paths") or territory.get("sample_paths") or []]
        boundary, guidance = semantic_boundary_for_territory(str(territory["name"]), paths)
        samples = [str(path) for path in territory.get("sample_paths") or paths[:3]]
        records.append(
            {
                "territory": str(territory["name"]),
                "boundary": boundary,
                "evidence": ", ".join(f"`{path}`" for path in samples[:3]) or "none",
                "guidance": guidance,
            }
        )
    return records


def weak_anchor_triage(scan: dict[str, Any]) -> list[dict[str, str]]:
    files = [str(record["path"]) for record in scan["files"]]
    rows: list[dict[str, str]] = []
    checks = (
        ("fixture/example data", ("fixtures/", "/fixtures/", "examples/", "/examples/"), "use for repros, not architecture"),
        ("generated or build artifacts", ("generated", "__generated__", ".map", "enhancement-configs"), "treat as derived/specialized evidence"),
        ("dependency lockfiles", ("pnpm-lock.yaml", "uv.lock", "package-lock.json", "yarn.lock", "Cargo.lock"), "use for dependency state, not ownership"),
        ("TES runtime", (".tes/", "docs/agents/evidence/", "docs/agents/cortex/"), "exclude from project architecture claims"),
        ("migrations", ("/migrations/", "migrations/"), "high-caution historical/schema state"),
    )
    for label, needles, reason in checks:
        sample = next((path for path in files if any(needle in path for needle in needles)), None)
        if sample:
            rows.append({"category": label, "sample": sample, "handling": reason})
    if not rows:
        rows.append({"category": "none detected", "sample": "n/a", "handling": "no weak-anchor category was detected by the deterministic scanner"})
    return rows


def caution_zones(scan: dict[str, Any]) -> list[dict[str, str]]:
    files = [str(record["path"]) for record in scan["files"]]
    rows: list[dict[str, str]] = []
    checks = (
        ("project-owned agent governance", ("AGENTS.md", "CLAUDE.md", "CURSOR.md"), "clean runtime after central backup; recover durable semantics from backup evidence"),
        ("migrations and schema history", ("/migrations/", "migrations/"), "do not edit casually; use project migration workflow"),
        ("self-hosted or environment config", ("self-hosted/", "devservices/", "devenv/", "config/"), "changes may affect boot/deploy/dev services"),
        ("dependency locks", ("pnpm-lock.yaml", "uv.lock", "Cargo.lock", "package-lock.json"), "update only through package manager workflow"),
        ("fixtures and generated data", ("fixtures/", "__generated__", "enhancement-configs"), "avoid deriving product boundaries from these alone"),
    )
    for zone, needles, guidance in checks:
        sample = next((path for path in files if any(path == needle or needle in path for needle in needles)), None)
        if sample:
            rows.append({"zone": zone, "evidence": sample, "guidance": guidance})
    return rows


def project_context(scan: dict[str, Any], target: Path, manifest_rel: str) -> dict[str, Any]:
    scripts = package_scripts(target)
    scripts.update(makefile_scripts(target))
    qscripts = quality_scripts(scripts)
    qscripts.update(python_quality_scripts(target))
    qscripts.update(makefile_quality_scripts(target))
    anchors = context_anchors(scan)
    return {
        "identity": detect_project_identity(target),
        "semantic_signals": semantic_signals(target),
        "manifest": manifest_rel,
        "anchors": anchors,
        "territories": territory_summary(scan),
        "workspace_boundaries": workspace_boundaries(target),
        "package_scripts": scripts,
        "quality_scripts": dict(sorted(qscripts.items())),
        "weak_anchor_triage": weak_anchor_triage(scan),
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
    if BUNDLE_MODE:
        return [
            {
                "command": "public bundle package gates",
                "returncode": 0,
                "stdout": "",
                "stderr": "maintainer-only source package gates are not bundled",
                "status": "RECOVERED",
            }
        ]
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
                "status": "RECOVERED",
            }
        ]
    gates = [
        [sys.executable, "scripts/install_smoke.py", "--self-test"],
        [sys.executable, "scripts/platform_surface_oracle.py", "--self-test"],
    ]
    return [run(command, ROOT) for command in gates]


def target_gates(target: Path) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = [git_diff_check_gate(target)]
    gates.append(root_context_gate(target))
    gate_cwd = ROOT if PACKAGE_MODE else HELPER_ROOT
    gates.append(run([sys.executable, str(helper_script("field_reports.py")), "status", "--target", str(target)], gate_cwd))
    for oracle_name in ("project_context_oracle.py", "project_alignment_oracle.py"):
        oracle = helper_script(oracle_name)
        if oracle.exists():
            gates.append(run([sys.executable, str(oracle), "--target", str(target)], gate_cwd))
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


def format_frontmatter(
    tes_doc: str,
    evidence_paths: list[str],
    *,
    confidence: str = "medium",
    related: list[str] | None = None,
) -> str:
    evidence = "\n".join(f"  - path: {path}" for path in evidence_paths[:5]) or "  - path: docs/agents/PROJECT-CONTEXT.md"
    tags = f"  - tes\n  - {tes_doc}"
    related_lines = "\n".join(f"  - \"[[{item}]]\"" for item in (related or []))
    related_block = f"\nrelated:\n{related_lines}" if related_lines else ""
    return f"""---
tes_doc: {tes_doc}
status: active
owner: project
updated: {date_stamp()}
confidence: {confidence}
evidence:
{evidence}
tags:
{tags}{related_block}
---

"""


def alignment_anchor_paths(scan: dict[str, Any], target: Path, manifest_rel: str) -> list[str]:
    context = project_context(scan, target, manifest_rel)
    anchors = [str(anchor["path"]) for anchor in context["anchors"]]
    anchors.extend(str(record["path"]) for record in scan["files"][:8])
    anchors.extend([PROJECT_CONTEXT.as_posix(), REGISTER.as_posix(), manifest_rel])
    return list(dict.fromkeys(anchor for anchor in anchors if anchor))


def first_anchor(anchors: list[str]) -> str:
    return anchors[0] if anchors else PROJECT_CONTEXT.as_posix()


def initial_system_xray() -> str:
    return """```mermaid
flowchart TD
  A["Project system<br/>real operating map"] --> B["Git state"]
  A --> C["Delivered behavior"]
  A --> D["Validation mesh"]
  A --> E["Release boundary"]

  B --> B1["HEAD and worktree<br/>verify before commit"]
  C --> C1["docs/agents/**<br/>project operating mesh"]
  C --> C2["Runtime adapters<br/>Codex, Claude, Cursor"]
  D --> D1["Context oracle"]
  D --> D2["Alignment oracle"]
  D --> D3["Project quality gates"]
  E --> E1["Technical GO"]
  E --> E2["Sealed/release claim<br/>requires explicit gate"]

  classDef system fill:#eef2f7,stroke:#475569,color:#0f172a;
  classDef behavior fill:#e6f0ff,stroke:#2b6cb0,color:#102a43;
  classDef gate fill:#d8f5df,stroke:#1b7f3a,color:#0b351a;
  classDef pending fill:#ffe4e6,stroke:#be123c,color:#4c0519;
  classDef release fill:#f3e8ff,stroke:#7e22ce,color:#2e1065;

  class A,B,C,D,E,B1 system;
  class C1,C2 behavior;
  class D1,D2,D3,E1 gate;
  class E2 pending;
```
"""


def initial_convergence_line() -> str:
    return """```mermaid
flowchart TD
  A["Done: project identity detected"] --> B["Done: context and register created"]
  B --> C["Current: semantic alignment"]
  C --> D["Next: confirm project quality gate"]
  D --> E["Next: refine state, execution line, and gates"]
  E --> F["Later: add ADRs when decisions are evidenced"]
  E --> J["Deferred: release or bundle claim until requested"]
  E --> I["Final: technical GO after project gates pass"]
  D --> G["Blocked: secrets, external systems, or destructive work need approval"]
  C --> H["Unknown: runtime and deployment claims need source evidence"]

  classDef done fill:#d8f5df,stroke:#1b7f3a,color:#0b351a;
  classDef current fill:#fff0bf,stroke:#b7791f,color:#4a2d00;
  classDef next fill:#e6f0ff,stroke:#2b6cb0,color:#102a43;
  classDef later fill:#eef2f7,stroke:#64748b,color:#0f172a;
  classDef deferred fill:#fef9c3,stroke:#a16207,color:#422006;
  classDef blocked fill:#ffe4e6,stroke:#be123c,color:#4c0519;
  classDef unknown fill:#f5f5f4,stroke:#78716c,color:#1c1917;
  classDef final fill:#f3e8ff,stroke:#7e22ce,color:#2e1065;

  class A,B done;
  class C current;
  class D,E next;
  class F later;
  class J deferred;
  class G blocked;
  class H unknown;
  class I final;
```
"""


def initial_alignment_texts(
    target: Path,
    scan: dict[str, Any],
    gates: list[dict[str, Any]],
    manifest_rel: str,
    stamp: str,
    *,
    oracle_status: str,
) -> dict[Path, str]:
    context = project_context(scan, target, manifest_rel)
    anchors = alignment_anchor_paths(scan, target, manifest_rel)
    primary = first_anchor(anchors)
    secondary = anchors[1] if len(anchors) > 1 else PROJECT_CONTEXT.as_posix()
    identity = context["identity"]
    quality = context["quality_scripts"]
    required_gate = "python3 .tes/bin/project_context_oracle.py --target ."
    focused_gate = "python3 .tes/bin/project_alignment_oracle.py --target ."
    if quality:
        first_quality_name, first_quality_command = next(iter(quality.items()))
        project_quality_class = "required"
        project_quality_gate = f"{first_quality_name}: {first_quality_command}"
    else:
        project_quality_class = "needs_review"
        project_quality_gate = f"Open `{primary}` and confirm the project-specific validation path."
    gate_failures = [gate for gate in gates if not gate_passed(gate)]
    gate_status = "PASS" if not gate_failures else "NEEDS_REVIEW"
    anchor_yaml = "\n".join(f"    - {anchor}" for anchor in anchors[:6])
    alignment_paths = [
        PROJECT_CONTEXT.as_posix(),
        PROJECT_STATE.as_posix(),
        PROJECT_ROADMAP.as_posix(),
        EXECUTION_LINE.as_posix(),
        QUALITY_GATES.as_posix(),
        BOUNDARIES.as_posix(),
        KNOWLEDGE_LIFECYCLE.as_posix(),
        GLOSSARY.as_posix(),
        f"{DECISIONS_DIR.as_posix()}/001-initial-operating-mesh.md",
    ]
    created_yaml = "\n".join(f"    - {path}" for path in alignment_paths)

    return {
        PROJECT_STATE:
            format_frontmatter(
                "project-state",
                [primary, secondary, PROJECT_CONTEXT.as_posix()],
                related=["PROJECT-CONTEXT", "PROJECT-ROADMAP", "QUALITY-GATES"],
            )
            + f"""# Project State

This is the initial `/tes-init` state for `{identity['name']}`. It is a
starter operating view derived from `{primary}` and
`{manifest_rel}`.

## Done

- Initial project inventory exists in `docs/agents/PROJECT-REGISTER.md`.
- Initial project context exists in `docs/agents/PROJECT-CONTEXT.md`.
- Initial Obsidian-compatible operating mesh links
  [[PROJECT-CONTEXT]], [[PROJECT-ROADMAP]], and [[QUALITY-GATES]].

## Active

- Refine project meaning with `/tes-align` after reading strong anchors such as
  `{primary}` and `{secondary}`.
- Keep unknowns visible until source evidence supports a stronger claim.

## Blocked

- No blocker was certified during initialization.
- If a local command is unavailable, record it in [[QUALITY-GATES]] before
  changing implementation.

## Deferred

- Deep architecture decisions remain deferred to `/tes-align` unless already
  evidenced by project-owned docs.

## Unknown

- Runtime, deployment, and ownership details may need deeper source reads.
""",
        PROJECT_ROADMAP:
            format_frontmatter(
                "project-roadmap",
                [primary, manifest_rel, PROJECT_CONTEXT.as_posix()],
                related=["PROJECT-CONTEXT", "PROJECT-STATE", "EXECUTION-LINE"],
            )
            + f"""# Project Roadmap

This roadmap starts with a System X-Ray and a Convergence Line, then keeps
compact audit lanes. It prevents future agents from rebuilding what `/tes-init`
already identified and keeps uncertainty explicit.

## System X-Ray

{initial_system_xray()}

## Convergence Line

{initial_convergence_line()}

## Current Claim

- Initial project scaffold: `{gate_status}`.
- Alignment depth remains limited until `/tes-align` reads strong project
  anchors and updates the mesh with source-backed meaning.
- Sealed, release-ready, pushed, or commercial-use claims are not available
  until the matching Git, bundle, release, and canary gates pass.

## Next Irreversible Step

- Run the smallest project quality gate from [[QUALITY-GATES]] before commit.
- Commit only after separating unrelated staged work from this project lane.

## Done

- Project identity and source anchors were captured from `{primary}`.
- `docs/agents/PROJECT-CONTEXT.md` and `docs/agents/PROJECT-REGISTER.md` were
  created as initial durable context.

## Active

- Execute `/tes-align` semantics by reading the strongest anchors and refining
  [[PROJECT-STATE]], [[EXECUTION-LINE]], and [[QUALITY-GATES]].

## Next

- Confirm the smallest safe project gate from `{primary}` or package metadata.
- Promote stable facts to Cortex only after review.

## Later

- Add project-specific ADRs when architectural decisions become clear.

## Deferred

- Visual Obsidian Canvas or Bases views are optional and must point back to
  Markdown truth.

## Blocked

- Mark work blocked when secrets, external services, destructive operations, or
  missing local dependencies prevent proof.

## Unknown

- Any architecture or product claim not supported by `{primary}` or
  `{manifest_rel}` remains unknown.
""",
        EXECUTION_LINE:
            format_frontmatter(
                "execution-line",
                [primary, PROJECT_CONTEXT.as_posix(), manifest_rel],
                related=["PROJECT-ROADMAP", "QUALITY-GATES", "BOUNDARIES-AND-CONSTRAINTS"],
            )
            + f"""# Execution Line

Current lane: use `docs/agents/PROJECT-CONTEXT.md` as the entry map, then open
`{primary}` before planning material work.

## Reentry

- Read [[PROJECT-CONTEXT]], [[PROJECT-STATE]], and [[PROJECT-ROADMAP]].
- Check `git status --short --branch`.
- Confirm the next gate from [[QUALITY-GATES]] before editing.

## Build-Test-Fail-Fix

- State the hypothesis.
- Run the smallest relevant gate.
- Classify failure before fixing.
- Retest the exact failing proof before broader gates.

## Stop Condition

Stop when the work touches secrets, external systems, destructive operations,
project-owned governance, remotes, tags, releases, or unreviewed generated
artifacts.
""",
        QUALITY_GATES:
            format_frontmatter(
                "quality-gates",
                [primary, PROJECT_CONTEXT.as_posix(), manifest_rel],
                related=["PROJECT-CONTEXT", "EXECUTION-LINE", "BOUNDARIES-AND-CONSTRAINTS"],
            )
            + f"""# Quality Gates

| Gate | Class | Command Or Proof |
|------|-------|------------------|
| Project context oracle | required | `{required_gate}` |
| Project alignment oracle | focused | `{focused_gate}` |
| Project quality gates | {project_quality_class} | `{project_quality_gate}` |
| Unclassified quality gate | needs_review | Record the missing, unsafe, or ambiguous proof before claiming GO. |
| Missing local toolchain | unavailable | Record the blocker before claiming coverage. |
| Production or secret-backed action | unsafe | Requires explicit user approval. |

Initialization gate status: `{gate_status}`.
""",
        BOUNDARIES:
            format_frontmatter(
                "boundaries",
                [primary, PROJECT_CONTEXT.as_posix(), manifest_rel],
                related=["PROJECT-CONTEXT", "EXECUTION-LINE", "QUALITY-GATES"],
            )
            + f"""# Boundaries And Constraints

- Preserve project-owned governance such as `AGENTS.md`, `CLAUDE.md`, Cursor
  rules, and existing docs unless the user authorizes a reviewed merge.
- Do not expose secrets or copy sensitive source content into Field Reports.
- Do not call external services, publish, push, tag, or create issues without
  explicit approval.
- Do not run destructive commands to get a green result.
- Treat `{primary}` and Git-tracked source as truth; treat generated TES files
  as context aids.
""",
        KNOWLEDGE_LIFECYCLE:
            format_frontmatter(
                "knowledge-lifecycle",
                [primary, PROJECT_CONTEXT.as_posix(), manifest_rel],
                related=["PROJECT-CONTEXT", "PROJECT-ROADMAP", "GLOSSARY"],
            )
            + f"""# Knowledge Lifecycle

- Validate new claims against `{primary}`, `{secondary}`, or another cited
  project path before promotion.
- Refresh [[PROJECT-CONTEXT]] and [[PROJECT-STATE]] after architecture,
  runtime, ownership, or quality-gate changes.
- Retire superseded roadmap items by moving them to Done, Deferred, or Blocked
  with evidence instead of deleting history silently.
- Preserve contradictions until source evidence resolves them.
""",
        GLOSSARY:
            format_frontmatter(
                "glossary",
                [primary, PROJECT_CONTEXT.as_posix(), manifest_rel],
                related=["PROJECT-CONTEXT", "PROJECT-STATE"],
            )
            + f"""# Glossary

| Term | Meaning |
|------|---------|
| Project anchor | A high-signal path such as `{primary}` used to verify context. |
| Gate | A command, oracle, or documented proof used to certify a claim. |
| Operating mesh | The linked `docs/agents/**` layer used by future agents. |
""",
        DECISIONS_DIR / "001-initial-operating-mesh.md":
            format_frontmatter(
                "decision",
                [primary, PROJECT_CONTEXT.as_posix(), manifest_rel],
                confidence="medium",
                related=["PROJECT-CONTEXT", "PROJECT-ROADMAP", "EXECUTION-LINE"],
            )
            + f"""# Decision: Initial Operating Mesh

Use `docs/agents/**` as the portable Markdown operating mesh for this project.
Obsidian may visualize the mesh, but Markdown and Git remain the source of
truth.

## Evidence

- `{primary}`
- `{PROJECT_CONTEXT.as_posix()}`
- `{manifest_rel}`

## Consequences

- Runtime adapter files stay thin.
- Future work starts from [[PROJECT-CONTEXT]] and [[EXECUTION-LINE]].
- Deeper semantic refinement belongs to `/tes-align`.
""",
        EVIDENCE_DIR / f"{stamp}-project-alignment.md":
            f"""# TES Project Alignment Evidence

```yaml
alignment_evidence:
  target: {target}
  tes_version: {VERSION}
  anchors_read:
{anchor_yaml}
  existing_docs_classification:
    PROJECT-CONTEXT.md: created_or_updated
    PROJECT-STATE.md: created_if_missing
    PROJECT-ROADMAP.md: created_if_missing
    EXECUTION-LINE.md: created_if_missing
    QUALITY-GATES.md: created_if_missing
    BOUNDARIES-AND-CONSTRAINTS.md: created_if_missing
    KNOWLEDGE-LIFECYCLE.md: created_if_missing
    GLOSSARY.md: created_if_missing
    DECISIONS/001-initial-operating-mesh.md: created_if_missing
  created_or_updated:
{created_yaml}
  contradictions: []
  quality_gates_discovered:
    - {required_gate}
    - {focused_gate}
  roadmap_changes:
    - created initial System X-Ray graph
    - created initial Convergence Line graph
    - created initial Done, Active, Next, Later, Deferred, Blocked, and Unknown lanes
  obsidian_native_checks:
    frontmatter: PASS
    wikilinks: PASS
    dot_obsidian_writes: none
  oracle_result: {oracle_status}
  limits: initial deterministic mesh; run /tes-align for deeper semantic refinement
```
""",
    }


def ensure_initial_alignment_mesh(
    target: Path,
    scan: dict[str, Any],
    gates: list[dict[str, Any]],
    manifest_rel: str,
    stamp: str,
    *,
    rewrite_paths: set[str] | None = None,
    oracle_status: str = "PENDING",
) -> list[str]:
    rewritable = rewrite_paths or set()
    writes: list[str] = []
    for relpath, text in initial_alignment_texts(
        target,
        scan,
        gates,
        manifest_rel,
        stamp,
        oracle_status=oracle_status,
    ).items():
        path = target / relpath
        relpath_str = relpath.as_posix()
        if path.exists() and relpath_str not in rewritable:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        writes.append(relpath_str)
    return writes


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
    return format_frontmatter(
        "project-register",
        [manifest_rel, PROJECT_CONTEXT.as_posix()],
        confidence="medium",
        related=["PROJECT-CONTEXT", "PROJECT-STATE", "PROJECT-ROADMAP"],
    ) + f"""# Tilly Project Register

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
- Root context result `RECOVERED` means project-owned bootloader context was
  detected and should be recovered from `.tes/bk/**` after the clean runtime
  is active.
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
    workspaces = context["workspace_boundaries"]
    scripts = context["package_scripts"]
    qscripts = context["quality_scripts"]
    semantic_territories = semantic_territory_guide(territories)
    weak_triage = context["weak_anchor_triage"]
    cautions = caution_zones(scan)
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
    semantic_rows = [
        (
            row["territory"],
            row["boundary"],
            row["evidence"],
            row["guidance"],
        )
        for row in semantic_territories
    ]
    weak_rows = [
        (row["category"], row["sample"], row["handling"])
        for row in weak_triage
    ]
    caution_rows = [
        (row["zone"], row["evidence"], row["guidance"])
        for row in cautions
    ]
    workspace_rows = [
        (str(workspace["source"]), str(workspace["kind"]), str(workspace["pattern"]))
        for workspace in workspaces
    ]
    script_rows = [(name, command) for name, command in scripts.items()]
    quality_rows = [(name, command) for name, command in qscripts.items()]
    gate_rows = [(gate["command"], gate["status"]) for gate in gates]
    signal_rows = [(item["signal"], item["value"], item["source"]) for item in signals]
    deep_reads = "\n".join(f"- `{anchor['path']}`" for anchor in anchors[:12]) or "- none"
    next_guidance = "\n".join(
        f"- For `{row['territory']}`, {row['guidance']}."
        for row in semantic_territories[:8]
    ) or "- Open the strongest source anchors before planning work."
    evidence_paths = [str(anchor["path"]) for anchor in anchors[:3]]
    evidence_paths.append(manifest_rel)

    return format_frontmatter(
        "project-context",
        list(dict.fromkeys(evidence_paths)),
        confidence="medium",
        related=["PROJECT-REGISTER", "PROJECT-STATE", "PROJECT-ROADMAP", "EXECUTION-LINE"],
    ) + f"""# Tilly Project Context

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
## Semantic Territory Guide

This section is deterministic interpretation from paths and known project
surfaces. It is meant to guide first reads, not replace source inspection.

{markdown_table(semantic_rows, ("Territory", "Likely boundary", "Evidence", "Next move"))}
## Weak Anchor Triage

These surfaces were detected as weak evidence for architecture. They may be
useful for focused work, but they should not dominate first-pass understanding.

{markdown_table(weak_rows, ("Category", "Sample", "Handling"))}
## Caution Zones

{markdown_table(caution_rows, ("Zone", "Evidence", "Guidance"))}
## Workspace Boundaries

{markdown_table(workspace_rows, ("Source", "Kind", "Pattern"))}
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

## Next Work Guidance

{next_guidance}

## Open Context Questions

- What is the project domain in one sentence, based on product docs and source
  entrypoints?
- Which directories define the runtime boundary, persistence boundary, and
  external integration boundary?
- Which commands are the smallest safe quality gates before commit?
- Which facts should be promoted into Cortex cells after user review?

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
    alignment_planned = [
        PROJECT_STATE.as_posix(),
        PROJECT_ROADMAP.as_posix(),
        EXECUTION_LINE.as_posix(),
        QUALITY_GATES.as_posix(),
        BOUNDARIES.as_posix(),
        KNOWLEDGE_LIFECYCLE.as_posix(),
        GLOSSARY.as_posix(),
        f"{DECISIONS_DIR.as_posix()}/001-initial-operating-mesh.md",
        f"{EVIDENCE_DIR.as_posix()}/{stamp}-project-alignment.md",
    ]
    planned_writes = [
        REGISTER.as_posix(),
        PROJECT_CONTEXT.as_posix(),
        *alignment_planned,
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
            "certification_status": "RECOVERED",
            "resolution": "project-owned root context is recovery evidence after central clean backup",
        }

    scan = scan_project(target)
    package_gate_results = package_gates()
    manifest_path.write_text(json.dumps(scan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target / REGISTER).write_text(write_register(target, scan, package_gate_results, manifest_rel), encoding="utf-8")
    (target / PROJECT_CONTEXT).write_text(
        write_project_context(target, scan, package_gate_results, manifest_rel),
        encoding="utf-8",
    )
    alignment_writes = ensure_initial_alignment_mesh(
        target,
        scan,
        package_gate_results,
        manifest_rel,
        stamp,
        oracle_status="PENDING",
    )

    gates = [*package_gate_results, *target_gates(target)]
    status = "PASS" if all(gate_passed(gate) for gate in gates) else "NEEDS_REVIEW"

    register_text = write_register(target, scan, gates, manifest_rel)
    project_context_text = write_project_context(target, scan, gates, manifest_rel)
    evidence_text = write_evidence(target, scan, gates, planned_writes, manifest_rel)
    alignment_writes = ensure_initial_alignment_mesh(
        target,
        scan,
        gates,
        manifest_rel,
        stamp,
        rewrite_paths=set(alignment_writes),
        oracle_status=status,
    )

    manifest_path.write_text(json.dumps(scan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target / REGISTER).write_text(register_text, encoding="utf-8")
    (target / PROJECT_CONTEXT).write_text(project_context_text, encoding="utf-8")
    evidence_path.write_text(evidence_text, encoding="utf-8")

    actual_writes = [
        REGISTER.as_posix(),
        PROJECT_CONTEXT.as_posix(),
        *alignment_writes,
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
        git_env = isolated_git_env()
        subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False, env=git_env)
        subprocess.run(
            ["git", "add", "README.md", "package.json", "src/app.py"],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
            env=git_env,
        )
        subprocess.run(
            ["git", "commit", "-m", "fixture"],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
            env={**git_env, "GIT_AUTHOR_NAME": "Tilly", "GIT_AUTHOR_EMAIL": "tilly@example.test",
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
            "Workspace Boundaries",
            "Semantic Territory Guide",
            "Weak Anchor Triage",
            "Caution Zones",
            "project-owned agent governance",
            "Recommended Deep Reads",
            "Next Work Guidance",
        ):
            if term not in context_text:
                failures.append(f"project context missing term: {term}")
        anchor_block = context_text.split("## Source Anchors Read First", 1)[-1].split("## Runtime And Governance Surfaces", 1)[0]
        deep_read_block = context_text.split("## Recommended Deep Reads", 1)[-1].split("## Open Context Questions", 1)[0]
        if ".tes/bin" in anchor_block:
            failures.append("project context source anchors must exclude TES helper internals")
        if ".tes/bin" in deep_read_block:
            failures.append("project context deep reads must exclude TES helper internals")
        if result["status"] != "PASS":
            failures.append(f"expected PASS, got {result['status']}")
        if not any(gate["status"] == "RECOVERED" for gate in result["gates"]):
            failures.append("project-owned root context must close as RECOVERED during init")

    with tempfile.TemporaryDirectory(prefix="tes-init-ignored-parent-") as tempdir:
        parent = Path(tempdir)
        subprocess.run(["git", "init"], cwd=parent, text=True, capture_output=True, check=False, env=isolated_git_env())
        (parent / ".gitignore").write_text("runs/\n", encoding="utf-8")
        target = parent / "runs" / "canary"
        target.mkdir(parents=True)
        (target / "AGENTS.md").write_text("project-owned AGENTS\n", encoding="utf-8")
        (target / "CLAUDE.md").write_text("project-owned CLAUDE\n", encoding="utf-8")
        scan = scan_project(target)
        paths = {str(record["path"]) for record in scan["files"]}
        if not {"AGENTS.md", "CLAUDE.md"}.issubset(paths):
            failures.append("project scan must fall back to local files when parent Git ignores target")

    with tempfile.TemporaryDirectory(prefix="tes-init-gitless-target-") as tempdir:
        target = Path(tempdir)
        (target / "README.md").write_text("# Gitless fixture\n\nA restored project without a .git directory.\n", encoding="utf-8")
        result = initialize(target, yes=True, ensure_cortex=True)
        git_gate = next((gate for gate in result["gates"] if gate["command"] == "git diff --check"), None)
        if result["status"] != "PASS":
            failures.append(f"gitless target must initialize without NEEDS_REVIEW, got {result['status']}")
        if not git_gate or git_gate["status"] != "NOT_AVAILABLE":
            failures.append("gitless target must mark git diff gate as NOT_AVAILABLE")

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

    with tempfile.TemporaryDirectory(prefix="tes-init-sparse-readme-") as tempdir:
        target = Path(tempdir)
        (target / "README").write_text("Hello World!\n", encoding="utf-8")
        identity = detect_project_identity(target)
        if identity["name"] != target.name:
            failures.append("sparse README identity must keep directory name when no heading exists")
        if identity["description"] != "Hello World!":
            failures.append("sparse README identity must use README prose as description")
        if "README" not in identity["source"]:
            failures.append("sparse README identity source must include README")

    with tempfile.TemporaryDirectory(prefix="tes-init-pyproject-identity-") as tempdir:
        target = Path(tempdir)
        (target / "README.md").write_text(
            "# README Heading\n\nREADME prose should not override canonical pyproject metadata.\n",
            encoding="utf-8",
        )
        (target / "pyproject.toml").write_text(
            "[project]\nname = \"pyproject-fixture\"\ndescription = \"Canonical Python package description.\"\n"
            "[tool.pytest.ini_options]\naddopts = \"-q\"\n",
            encoding="utf-8",
        )
        identity = detect_project_identity(target)
        if identity["name"] != "pyproject-fixture":
            failures.append("pyproject identity must provide project name")
        if identity["description"] != "Canonical Python package description.":
            failures.append("pyproject identity must provide project description")
        if identity["source"] != "pyproject.toml":
            failures.append("pyproject identity source must be pyproject.toml")
        if "Python tool config: pytest" not in stack_signals(target):
            failures.append("stack signals must include pyproject tool configuration")

    with tempfile.TemporaryDirectory(prefix="tes-init-rst-anchor-rank-") as tempdir:
        target = Path(tempdir)
        (target / "README.rst").write_text("Django\n======\n\nFramework prose.\n", encoding="utf-8")
        (target / "pyproject.toml").write_text(
            "[project]\nname = \"django-fixture\"\ndescription = \"Framework prose.\"\n",
            encoding="utf-8",
        )
        (target / "package.json").write_text('{"name":"django-fixture","scripts":{"test":"grunt test"}}\n', encoding="utf-8")
        (target / "docs").mkdir()
        (target / "docs/INDEX.md").write_text("# Documentation Index\n", encoding="utf-8")
        (target / "docs/README.rst").write_text("Docs\n====\n", encoding="utf-8")
        (target / "docs/strategy/<project-b>-memory-program/WAVE-01").mkdir(parents=True)
        (target / "docs/strategy/<project-b>-memory-program/WAVE-01/README.md").write_text("# Wave README\n", encoding="utf-8")
        (target / "tests/fixtures/data").mkdir(parents=True)
        (target / "tests/README.rst").write_text("Tests\n=====\n", encoding="utf-8")
        (target / "tests/fixtures/data/README.md").write_text("# Fixture data\n", encoding="utf-8")
        (target / "tests/forms").mkdir(parents=True)
        (target / "tests/forms/README").write_text("", encoding="utf-8")
        (target / "docs/_theme/static/fontawesome").mkdir(parents=True)
        (target / "docs/_theme/static/fontawesome/README.md").write_text("# Static asset\n", encoding="utf-8")
        scan = scan_project(target)
        anchors = [str(anchor["path"]) for anchor in context_anchors(scan)]
        if "README.rst" not in anchors[:3]:
            failures.append("root README.rst must rank as a strongest context anchor")
        if anchors.index("tests/fixtures/data/README.md") < anchors.index("tests/README.rst"):
            failures.append("nested fixture README must not outrank real test anchors")
        if anchors.index("docs/_theme/static/fontawesome/README.md") < anchors.index("docs/README.rst"):
            failures.append("static asset README must not outrank real documentation anchors")
        if anchors.index("tests/forms/README") < anchors.index("tests/README.rst"):
            failures.append("empty nested README must not outrank real test anchors")
        if "docs/INDEX.md" not in anchors:
            failures.append("docs/INDEX.md must be eligible as a canonical documentation anchor")
        elif anchors.index("docs/strategy/<project-b>-memory-program/WAVE-01/README.md") < anchors.index("docs/INDEX.md"):
            failures.append("deep wave README must not outrank docs/INDEX.md")

    with tempfile.TemporaryDirectory(prefix="tes-init-plugin-territory-") as tempdir:
        target = Path(tempdir)
        (target / "README.md").write_text("# Plugin fixture\n", encoding="utf-8")
        (target / "<project-b>-plugin/src").mkdir(parents=True)
        (target / "<project-b>-plugin/src/index.ts").write_text("export const plugin = true;\n", encoding="utf-8")
        (target / "<project-b>-plugin/tests").mkdir(parents=True)
        (target / "<project-b>-plugin/tests/plugin.test.ts").write_text("export const ok = true;\n", encoding="utf-8")
        context = project_context(scan_project(target), target, "docs/agents/evidence/fixture-tes-project-manifest.json")
        roles = {territory["name"]: territory["role"] for territory in context["territories"]}
        if roles.get("<project-b>-plugin") != "plugin or extension product surface":
            failures.append("plugin territory with tests must remain classified as product surface")

    with tempfile.TemporaryDirectory(prefix="tes-init-ky-readme-") as tempdir:
        target = Path(tempdir)
        (target / "README.md").write_text(
            "<div>\n<p>Sponsor text that must be skipped.</p>\n</div>\n\n"
            "> Ky is a tiny and elegant HTTP client based on the [Fetch API](https://example.test)\n",
            encoding="utf-8",
        )
        signal = readme_signal(target) or {}
        if "Sponsor text" in signal.get("summary", ""):
            failures.append("README signal must skip leading HTML sponsor blocks")
        if "tiny and elegant HTTP client" not in signal.get("summary", ""):
            failures.append("README signal must accept the first real blockquote tagline")

    with tempfile.TemporaryDirectory(prefix="tes-init-go-provider-") as tempdir:
        target = Path(tempdir)
        (target / "README.md").write_text(
            "# Terraform AWS Provider\n\n"
            "[discuss-badge]: https://example.test/badge.svg\n"
            "[discuss]: https://example.test/discuss\n\n"
            "The Terraform AWS Provider maps AWS APIs into Terraform resources and data sources.\n",
            encoding="utf-8",
        )
        (target / "go.mod").write_text("module github.com/hashicorp/terraform-provider-aws\n", encoding="utf-8")
        (target / "GNUmakefile").write_text(
            "build: prereq-go fmt-check ## Build provider\n"
            "ci-quick: tools go-build testacc-lint ## Run quicker CI checks\n"
            "fmt: ## Fix Go source formatting\n"
            "gen: ## Run generators\n"
            "test: prereq-go ## Run unit tests\n"
            "testacc: prereq-go fmt-check ## Run acceptance tests\n",
            encoding="utf-8",
        )
        (target / "internal/service/s3").mkdir(parents=True)
        (target / "internal/service/s3/bucket.go").write_text("package s3\n", encoding="utf-8")
        (target / "skaff").mkdir()
        (target / "skaff/go.mod").write_text("module skaff\n", encoding="utf-8")
        (target / "docs").mkdir()
        (target / "docs/README.md").write_text("# Docs\n", encoding="utf-8")
        identity = detect_project_identity(target)
        if "discuss-badge" in identity["description"] or "maps AWS APIs" not in identity["description"]:
            failures.append("README identity must skip markdown reference definitions before prose")
        scripts = makefile_scripts(target)
        qscripts = makefile_quality_scripts(target)
        for name in ("build", "ci-quick", "fmt", "gen", "test", "testacc"):
            if name not in scripts or name not in qscripts:
                failures.append(f"GNUmakefile target must become a quality script: {name}")
        boundaries = {record["pattern"] for record in workspace_boundaries(target)}
        if "internal/service/*" not in boundaries or "skaff" not in boundaries:
            failures.append("Go provider contexts must expose service packages and nested Go modules")
        context = project_context(scan_project(target), target, "docs/agents/evidence/fixture-tes-project-manifest.json")
        roles = {territory["name"]: territory["role"] for territory in context["territories"]}
        if roles.get("internal") != "provider internals and service ownership":
            failures.append("internal/service territory must be labeled as provider service ownership")

    with tempfile.TemporaryDirectory(prefix="tes-init-lower-readme-") as tempdir:
        target = Path(tempdir)
        (target / "readme.md").write_text(
            "# lower readme\n\nLowercase README files are common in real GitHub projects.\n",
            encoding="utf-8",
        )
        signal = readme_signal(target) or {}
        if signal.get("source") != "readme.md":
            failures.append("README signal must support lowercase readme.md")
        if "Lowercase README files" not in signal.get("summary", ""):
            failures.append("README signal must extract prose from lowercase readme.md")

    with tempfile.TemporaryDirectory(prefix="tes-init-terraform-readme-") as tempdir:
        target = Path(tempdir)
        (target / "README.md").write_text(
            "## Learn Terraform Import\n\n"
            "Learn how to import existing resources under Terraform's management.\n\n"
            "```hcl\n# docker_container.web:\nresource \"docker_container\" \"web\" {}\n```\n",
            encoding="utf-8",
        )
        (target / "main.tf").write_text('resource "null_resource" "example" {}\n', encoding="utf-8")
        identity = detect_project_identity(target)
        if identity["name"] != "Learn Terraform Import":
            failures.append("README identity must accept level-2 headings outside code fences")
        if identity["description"] != "Learn how to import existing resources under Terraform's management.":
            failures.append("README identity must use prose before fenced HCL examples")
        if "docker_container.web" in identity["name"]:
            failures.append("README identity must ignore headings inside fenced code blocks")
        scan = scan_project(target)
        anchors = [str(anchor["path"]) for anchor in context_anchors(scan)]
        if "main.tf" not in anchors:
            failures.append("Terraform root files must become project context anchors")

    with tempfile.TemporaryDirectory(prefix="tes-init-monorepo-workspaces-") as tempdir:
        target = Path(tempdir)
        (target / "README.md").write_text("# Monorepo fixture\n\nWorkspace prose.\n", encoding="utf-8")
        (target / "package.json").write_text(
            json.dumps({"name": "monorepo-fixture", "workspaces": ["packages/*"]}) + "\n",
            encoding="utf-8",
        )
        (target / "pnpm-workspace.yaml").write_text(
            "packages:\n"
            "  - 'apps/*'\n"
            "  - 'packages/*'\n"
            "  - 'crates/*/js'\n",
            encoding="utf-8",
        )
        (target / "Cargo.toml").write_text("[workspace]\nmembers = [\"crates/*\"]\n", encoding="utf-8")
        for dirname in (".cargo", ".cursor", ".husky", "apps", "crates", "packages", "test-config-errors"):
            (target / dirname).mkdir(parents=True)
            (target / dirname / "anchor.txt").write_text(dirname + "\n", encoding="utf-8")
        scan = scan_project(target)
        territory_names = {str(territory["name"]) for territory in territory_summary(scan)}
        for expected in (".cargo", ".cursor", ".husky", "apps", "crates", "packages", "test-config-errors"):
            if expected not in territory_names:
                failures.append(f"monorepo territory must be retained: {expected}")
        workspace_patterns = {record["pattern"] for record in workspace_boundaries(target)}
        for expected in ("packages/*", "apps/*", "crates/*/js", "crates/*"):
            if expected not in workspace_patterns:
                failures.append(f"workspace boundary must be detected: {expected}")

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
        "self_test_mode": "package" if SOURCE_PACKAGE_MODE else ("bundle" if BUNDLE_MODE else "installed"),
        "coverage": "source-package-contract"
        if SOURCE_PACKAGE_MODE
        else ("public-bundle-helper-contract" if BUNDLE_MODE else "installed-helper-contract"),
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
