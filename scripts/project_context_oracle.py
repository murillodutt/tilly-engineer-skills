#!/usr/bin/env python3
"""Validate TES project-context quality for installed targets."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.247"
PROJECT_CONTEXT = Path("docs/agents/PROJECT-CONTEXT.md")
TES_AGENT_MESH_RELPATHS = {
    "docs/agents/PROJECT-CONTEXT.md",
    "docs/agents/PROJECT-REGISTER.md",
    "docs/agents/PROJECT-STATE.md",
    "docs/agents/PROJECT-ROADMAP.md",
    "docs/agents/EXECUTION-LINE.md",
    "docs/agents/QUALITY-GATES.md",
    "docs/agents/BOUNDARIES-AND-CONSTRAINTS.md",
    "docs/agents/KNOWLEDGE-LIFECYCLE.md",
    "docs/agents/GLOSSARY.md",
}
PACKAGE_MODE = (ROOT / "scripts").exists()
MARKDOWN_HEADING_RE = re.compile(r"^#{1,3}\s+(.+?)\s*$")
REQUIRED_SECTIONS = (
    "# Tilly Project Context",
    "## Identity",
    "## Initial Semantic Signals",
    "## Maximum-Depth Initialization Contract",
    "## Active Agent Refinement Contract",
    "## Coverage",
    "## Project Territories",
    "## Semantic Territory Guide",
    "## Weak Anchor Triage",
    "## Caution Zones",
    "## Workspace Boundaries",
    "## Source Anchors Read First",
    "## Runtime And Governance Surfaces",
    "## Recommended Deep Reads",
    "## Next Work Guidance",
    "## Open Context Questions",
    "## Maintenance Rule",
)
QUALITY_SCRIPT_TERMS = ("ci", "doc", "fmt", "gen", "lint", "typecheck", "test", "spec", "check", "build", "contract", "validate", "website")
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
ROOT_DEPENDENCY_LOCKFILES = (
    "pnpm-lock.yaml",
    "npm-shrinkwrap.json",
    "package-lock.json",
    "yarn.lock",
    "uv.lock",
    "Cargo.lock",
    "composer.lock",
    "Gemfile.lock",
    "poetry.lock",
    "Pipfile.lock",
)
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
    "__MACOSX",
}
OS_RESIDUE_NAMES = {".DS_Store", "__MACOSX", "Thumbs.db", ".AppleDouble", ".LSOverride"}
OS_RESIDUE_PREFIXES = ("._",)
TES_RUNTIME_PREFIXES = (
    (".agents", "skills", "tes-"),
    (".claude", "skills", "tes-"),
    ("skills", "tes-"),
    (".claude-plugin",),
    ("docs", "agents", "cortex"),
)
TES_RUNTIME_RELPATHS = {
    ".cursor/rules/tes-engineering-discipline.mdc",
    ".cursor/rules/tes-runtime-capabilities.mdc",
}
TES_ROOT_BOOTLOADER_MARKERS = {
    "AGENTS.md": "Portable Codex bootloader for repositories adopting Tilly Engineering",
    "CLAUDE.md": "Behavioral engineering discipline for reducing common LLM coding mistakes.",
    "CURSOR.md": "# Using This Repo With Cursor",
}
ANCHOR_NAMES = (
    "README.md",
    "readme.md",
    "README.rst",
    "readme.rst",
    "README.txt",
    "README.TXT",
    "README",
    "INDEX.md",
    "index.md",
    "INDEX.rst",
    "index.rst",
    "INDEX.txt",
    "index.txt",
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "GNUmakefile",
    "Makefile",
    "AGENTS.md",
    "CLAUDE.md",
    "CURSOR.md",
    "main.tf",
    "versions.tf",
    "providers.tf",
    "variables.tf",
    "outputs.tf",
    "terraform.tfvars",
    "docker.tf",
)


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def load_toml(path: Path) -> dict[str, Any] | None:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return None
    return data if isinstance(data, dict) else None


def git_files(target: Path) -> list[Path] | None:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=target,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return [
        target / raw.decode("utf-8")
        for raw in result.stdout.split(b"\0")
        if raw
    ]


def iter_project_files(target: Path) -> list[Path]:
    from_git = git_files(target)
    if from_git:
        return sorted(path for path in from_git if path.is_file() and not is_excluded(path, target))
    return sorted(
        path
        for path in target.rglob("*")
        if path.is_file() and not is_excluded(path, target)
    )


def is_os_residue_relpath(relpath: Path) -> bool:
    return any(
        part in OS_RESIDUE_NAMES or part.startswith(OS_RESIDUE_PREFIXES) for part in relpath.parts
    )


def is_excluded(path: Path, target: Path) -> bool:
    try:
        relpath = path.relative_to(target)
    except ValueError:
        return True
    if relpath.as_posix() in TES_AGENT_MESH_RELPATHS:
        return True
    if len(relpath.parts) >= 3 and relpath.parts[:3] == ("docs", "agents", "DECISIONS"):
        return True
    if is_tes_runtime_relpath(relpath) or is_generated_root_bootloader(relpath, path):
        return True
    if len(relpath.parts) >= 3 and relpath.parts[:3] == ("docs", "agents", "evidence"):
        return True
    parts = relpath.parts
    if is_os_residue_relpath(path.relative_to(target)):
        return True
    return any(part in EXCLUDED_PARTS for part in parts)


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


def is_generated_root_bootloader(relpath: Path, path: Path) -> bool:
    marker = TES_ROOT_BOOTLOADER_MARKERS.get(relpath.as_posix())
    if not marker or not path.exists():
        return False
    try:
        return marker in path.read_text(encoding="utf-8", errors="ignore")[:1200]
    except OSError:
        return False


def read_context(target: Path) -> tuple[str | None, list[str]]:
    path = target / PROJECT_CONTEXT
    if not path.exists():
        return None, [f"missing project context: {PROJECT_CONTEXT.as_posix()}"]
    try:
        return path.read_text(encoding="utf-8"), []
    except UnicodeDecodeError as exc:
        return None, [f"invalid UTF-8 project context: {exc}"]


def context_manifest(target: Path, text: str) -> dict[str, Any] | None:
    match = re.search(r"docs/agents/evidence/[0-9T]+Z-tes-project-manifest\.json", text)
    if not match:
        return None
    return load_json(target / match.group(0))


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
        underline = lines[index + 1].strip() if index + 1 < len(lines) else ""
        if len(underline) >= 3 and len(set(underline)) == 1 and underline[0] in "=-~^":
            return clean_markdown_inline(stripped)
    return None


def package_scripts(target: Path) -> dict[str, str]:
    package = load_json(target / "package.json")
    if not package:
        return {}
    scripts = package.get("scripts")
    if not isinstance(scripts, dict):
        return {}
    return {str(key): str(value) for key, value in scripts.items()}


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


def quality_scripts(target: Path) -> dict[str, str]:
    scripts = {
        name: command
        for name, command in package_scripts(target).items()
        if any(term in name.lower() for term in QUALITY_SCRIPT_TERMS)
    }
    scripts.update(
        {
            name: command
            for name, command in makefile_scripts(target).items()
            if name in MAKEFILE_QUALITY_TARGETS
            or any(term in name.lower() for term in QUALITY_SCRIPT_TERMS)
        }
    )
    pyproject = load_toml(target / "pyproject.toml") or {}
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
        for name, command in (
            ("pytest", "pytest"),
            ("ruff", "ruff check ."),
            ("mypy", "mypy"),
            ("pyright", "pyright"),
        ):
            if name in tools:
                scripts[name] = command
    if isinstance(dependency_groups, dict):
        group_text = json.dumps(dependency_groups)
        for name, command in (
            ("pytest", "pytest"),
            ("ruff", "ruff check ."),
            ("mypy", "mypy"),
            ("pyright", "pyright"),
            ("sphinx", "sphinx-build docs docs/_build"),
        ):
            if name in group_text:
                scripts.setdefault(name, command)
    return scripts


def identity_terms(target: Path) -> list[str]:
    terms: list[str] = []
    package = load_json(target / "package.json")
    if package and package.get("name"):
        terms.append(str(package["name"]))
    pyproject = load_toml(target / "pyproject.toml")
    project = pyproject.get("project") if pyproject else None
    if isinstance(project, dict) and project.get("name"):
        terms.append(str(project["name"]))
    for readme in readme_paths(target):
        in_fence = False
        lines = readme.read_text(encoding="utf-8", errors="ignore").splitlines()
        heading = first_readme_heading(lines)
        if heading:
            terms.append(heading)
            continue
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            match = MARKDOWN_HEADING_RE.match(stripped)
            if match:
                terms.append(clean_markdown_inline(match.group(1)))
                break
    if not terms:
        terms.append(target.name)
    return terms


def readme_summary(target: Path) -> str:
    readmes = readme_paths(target)
    if not readmes:
        return ""
    readme = readmes[0]
    paragraph: list[str] = []
    try:
        lines = readme.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return ""
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
        if stripped.startswith(">"):
            quote = stripped.lstrip("> ").strip()
            if quote.startswith("[!"):
                if paragraph:
                    break
                continue
            paragraph.append(quote)
            continue
        if MARKDOWN_HEADING_RE.match(stripped):
            continue
        underline = lines[index + 1].strip() if index + 1 < len(lines) else ""
        if len(underline) >= 3 and len(set(underline)) == 1 and underline[0] in "=-~^":
            continue
        if stripped.startswith(("|", "-", "* ", "!", "[![", "<", "```")):
            if paragraph:
                break
            continue
        if set(stripped) <= {"-", "_", "="}:
            continue
        paragraph.append(stripped)
    return clean_markdown_inline(" ".join(paragraph))


def project_has_description(target: Path) -> bool:
    package = load_json(target / "package.json")
    if package:
        description = package.get("description")
        if isinstance(description, str) and bool(description.strip()):
            return True
    pyproject = load_toml(target / "pyproject.toml")
    project = pyproject.get("project") if pyproject else None
    if isinstance(project, dict):
        description = project.get("description")
        if isinstance(description, str) and bool(description.strip()):
            return True
    return False


def project_description_terms(target: Path) -> list[str]:
    terms: list[str] = []
    package = load_json(target / "package.json")
    if package:
        description = package.get("description")
        if isinstance(description, str) and description.strip():
            terms.append(clean_markdown_inline(description.strip()))
    pyproject = load_toml(target / "pyproject.toml")
    project = pyproject.get("project") if pyproject else None
    if isinstance(project, dict):
        description = project.get("description")
        if isinstance(description, str) and description.strip():
            terms.append(clean_markdown_inline(description.strip()))
    return terms


def expected_anchors(target: Path) -> list[str]:
    files = iter_project_files(target)
    anchors: list[str] = []
    for path in readme_paths(target):
        if not is_excluded(path, target):
            anchors.append(path.name)
    for name in ANCHOR_NAMES:
        if name.casefold() in {"readme", "readme.md", "readme.rst", "readme.txt"}:
            continue
        path = target / name
        if path.exists() and path.is_file() and not is_excluded(path, target):
            # A root bootloader carrying TES markers is a TES-installed surface,
            # not a project anchor. After inherited-context install it is a thin
            # TES-rendered root, so it must not be expected in PROJECT-CONTEXT
            # (F1 canary finding: CURSOR.md showed up as a missing anchor).
            if name in TES_ROOT_BOOTLOADER_MARKERS:
                try:
                    head = path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    head = ""
                if TES_ROOT_BOOTLOADER_MARKERS[name] in head or "<!-- TES:CORE BEGIN" in head:
                    continue
            anchors.append(name)
    for path in files:
        try:
            relpath = path.relative_to(target)
        except ValueError:
            continue
        if len(relpath.parts) == 1 and relpath.suffix in {".tf", ".tfvars", ".hcl"}:
            anchors.append(relpath.as_posix())
    for dirname in ("src", "app", "server", "client", "tests", "test", "docs", "scripts"):
        root = target / dirname
        if root.exists():
            for path in files:
                try:
                    relpath = path.relative_to(target)
                except ValueError:
                    continue
                if relpath.parts and relpath.parts[0] == dirname:
                    if is_os_residue_relpath(relpath):
                        continue
                    anchors.append(relpath.as_posix())
                    break
    return sorted(dict.fromkeys(anchors))


# Top-level directories that are wholly TES-installed runtime surfaces, never
# project territory. `.cursor` is intentionally NOT here: a project may own its
# own `.cursor/rules/*.mdc`. TES cursor surfaces are excluded per-file via
# TES_RUNTIME_RELPATHS instead, so `.cursor` only disappears as a territory when
# it contains nothing but TES files (F1 canary finding: the missing exclusion of
# tes-runtime-capabilities.mdc was the real cause, not the directory itself).
TES_RUNTIME_TERRITORIES = {".claude", ".codex", ".agents", ".claude-plugin"}


def expected_territories(target: Path) -> list[str]:
    territories: set[str] = set()
    for path in iter_project_files(target):
        relpath = path.relative_to(target)
        if len(relpath.parts) > 1:
            territories.add(relpath.parts[0])
    return sorted(
        name
        for name in territories
        if name not in {".git", ".tes"} and name not in TES_RUNTIME_TERRITORIES
    )


def is_large_context_target(target: Path) -> bool:
    files = iter_project_files(target)
    top_level = {path.relative_to(target).parts[0] for path in files if len(path.relative_to(target).parts) > 1}
    return len(files) >= 500 or len(top_level) >= 12


def expected_semantic_terms(target: Path) -> list[str]:
    terms: list[str] = []
    if (target / "Cargo.toml").exists() and (target / "crates").exists():
        terms.append("Rust Cargo workspace boundary")
        terms.append("CLI, resolver, distribution, and package-manager domain ownership")
    if (target / "python").exists() and (target / "pyproject.toml").exists():
        terms.append("Python package/shim boundary")
    if (target / "src").exists():
        terms.append("likely Python backend/domain application boundary" if (target / "src/sentry").exists() else "product/source code")
    if (target / "static/app").exists():
        terms.append("likely frontend UI/client application boundary")
    if (target / "tests").exists():
        terms.append("verification boundary")
    if (target / "api-docs").exists():
        terms.append("documentation/API contract boundary")
    if (target / "self-hosted").exists() or (target / "devservices").exists() or (target / "devenv").exists():
        terms.append("operational or local-environment boundary")
    if (target / "AGENTS.md").exists() or (target / "CLAUDE.md").exists():
        terms.append("project-owned agent governance")
    return terms


def expected_caution_terms(target: Path) -> list[str]:
    terms: list[str] = []
    if (target / "AGENTS.md").exists() or (target / "CLAUDE.md").exists():
        terms.append("project-owned agent governance")
    if root_dependency_lockfile(target) is not None:
        terms.append("dependency locks")
    if (target / "self-hosted").exists() or (target / "devservices").exists() or (target / "devenv").exists() or (target / "config").exists():
        terms.append("self-hosted or environment config")
    if any("/migrations/" in rel(path, target) for path in iter_project_files(target)[:5000]):
        terms.append("migrations and schema history")
    return terms


def root_dependency_lockfile(target: Path) -> Path | None:
    for name in ROOT_DEPENDENCY_LOCKFILES:
        path = target / name
        if path.is_file():
            return path
    return None


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
    cargo = load_toml(target / "Cargo.toml")
    workspace = cargo.get("workspace") if cargo else None
    if not isinstance(workspace, dict):
        return []
    members = workspace.get("members")
    if not isinstance(members, list):
        return []
    return [str(item) for item in members]


def expected_workspace_boundaries(target: Path) -> list[str]:
    expected: list[str] = []
    package = load_json(target / "package.json")
    if package:
        expected.extend(package_workspace_patterns(package))
    expected.extend(pnpm_workspace_patterns(target))
    expected.extend(cargo_workspace_patterns(target))
    if (target / "go.mod").exists():
        for path in sorted(target.rglob("go.mod")):
            if path == target / "go.mod":
                continue
            try:
                relpath = path.parent.relative_to(target).as_posix()
            except ValueError:
                continue
            if relpath:
                expected.append(relpath)
    provider_services = target / "internal" / "service"
    if provider_services.is_dir() and any(path.is_dir() for path in provider_services.iterdir()):
        expected.append("internal/service/*")
    return sorted(dict.fromkeys(expected))


def code_fence_failures(text: str) -> list[str]:
    failures: list[str] = []
    for match in re.finditer(r"```[^\n]*\n(.*?)```", text, flags=re.DOTALL):
        body = match.group(1)
        lines = [line for line in body.splitlines() if line.strip()]
        code_like = sum(
            1
            for line in lines
            if re.search(r"\b(def|class|function|const|let|var|import|export|return)\b|[{};]$", line.strip())
        )
        if len(lines) > 20 or code_like >= 5:
            failures.append("project context appears to contain bulk copied source code")
    return failures


def analyze(target: Path) -> dict[str, Any]:
    target = target.resolve()
    failures: list[str] = []
    warnings: list[str] = []
    text, read_failures = read_context(target)
    failures.extend(read_failures)

    if text is None:
        return {
            "version": VERSION,
            "target": str(target),
            "status": "FAIL",
            "failures": failures,
            "warnings": warnings,
        }

    manifest = context_manifest(target, text)
    bootstrap_partial = False
    if manifest and manifest.get("bootstrap") is True:
        bootstrap_partial = True
    if manifest and int(manifest.get("file_count") or 0) == 0 and "tes_init bootstrap" in text:
        bootstrap_partial = True
    if bootstrap_partial:
        return {
            "version": VERSION,
            "target": str(target),
            "status": "FAIL",
            "failures": ["PROJECT-CONTEXT.md is bootstrap-only; rerun /tes-init after fixing blocked gates"],
            "warnings": warnings,
            "anchors_checked": [],
            "territories_checked": [],
            "quality_scripts_checked": [],
        }

    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"PROJECT-CONTEXT.md missing section: {section}")

    if "docs/agents/evidence/" not in text or "-tes-project-manifest.json" not in text:
        failures.append("PROJECT-CONTEXT.md must link the project manifest evidence")

    identities = identity_terms(target)
    if not any(term and term in text for term in identities):
        failures.append(f"PROJECT-CONTEXT.md missing project identity term: one of {identities}")

    if readme_summary(target) and not project_has_description(target) and "| Description | `unknown` |" in text:
        failures.append("PROJECT-CONTEXT.md must derive a non-unknown description from README prose when package description is absent")
    if project_has_description(target) and "| Description | `unknown` |" in text:
        failures.append("PROJECT-CONTEXT.md must derive a non-unknown description from package metadata when available")
    description_terms = project_description_terms(target)
    if description_terms and not any(term in text for term in description_terms):
        failures.append("PROJECT-CONTEXT.md missing package metadata description")

    anchors = expected_anchors(target)
    missing_anchors = [anchor for anchor in anchors if anchor not in text]
    if missing_anchors:
        failures.append(f"PROJECT-CONTEXT.md missing source anchors: {', '.join(missing_anchors[:8])}")

    if (target / "README.rst").exists() and "README.rst" not in text:
        failures.append("PROJECT-CONTEXT.md must include README.rst as a strong source anchor")
    if (target / "pyproject.toml").exists() and (target / "package.json").exists():
        identity_block = text.split("## Identity", 1)[1].split("## Initial Semantic Signals", 1)[0] if "## Identity" in text and "## Initial Semantic Signals" in text else ""
        if "pyproject.toml" not in identity_block:
            failures.append("PROJECT-CONTEXT.md must prefer pyproject identity over package.json when Python project metadata is present")

    territories = expected_territories(target)
    missing_territories = [name for name in territories if name not in text]
    if missing_territories:
        failures.append(f"PROJECT-CONTEXT.md missing territories: {', '.join(missing_territories[:8])}")

    if is_large_context_target(target):
        for section in ("## Semantic Territory Guide", "## Weak Anchor Triage", "## Caution Zones", "## Next Work Guidance"):
            if section not in text:
                failures.append(f"large PROJECT-CONTEXT.md missing anti-generic section: {section}")
        missing_semantic = [term for term in expected_semantic_terms(target) if term not in text]
        if missing_semantic:
            failures.append(
                "large PROJECT-CONTEXT.md missing semantic territory guidance in ## Semantic Territory Guide: "
                f"{', '.join(missing_semantic[:6])}; suggested row text includes "
                "`project-owned agent governance boundary` when AGENTS.md or CLAUDE.md exists"
            )
        missing_cautions = [term for term in expected_caution_terms(target) if term not in text]
        if missing_cautions:
            failures.append(
                "large PROJECT-CONTEXT.md missing caution zones in ## Caution Zones: "
                f"{', '.join(missing_cautions[:6])}; suggested zone text includes "
                "`project-owned agent governance` when AGENTS.md or CLAUDE.md exists"
            )
        if "unclassified territory" not in text and "likely " not in text:
            failures.append("large PROJECT-CONTEXT.md must separate deterministic interpretation from raw inventory")
        if "fixtures" in territories and "good for repros, weak evidence for product architecture" not in text:
            failures.append("large PROJECT-CONTEXT.md must mark fixtures/examples as weak architecture evidence")

    workspace_boundaries = expected_workspace_boundaries(target)
    missing_workspaces = [pattern for pattern in workspace_boundaries if pattern not in text]
    if missing_workspaces:
        failures.append(f"PROJECT-CONTEXT.md missing workspace boundaries: {', '.join(missing_workspaces[:8])}")

    qscripts = quality_scripts(target)
    missing_scripts = [name for name in qscripts if name not in text]
    if missing_scripts:
        failures.append(f"PROJECT-CONTEXT.md missing quality scripts: {', '.join(missing_scripts[:8])}")

    if "## Open Context Questions" in text and "?" not in text.split("## Open Context Questions", 1)[1]:
        failures.append("PROJECT-CONTEXT.md must keep explicit open context questions")

    if not any(term in text.lower() for term in ("unknown", "not found", "needs deeper read", "open context questions")):
        failures.append("PROJECT-CONTEXT.md must make unknowns or open context gaps explicit")

    failures.extend(code_fence_failures(text))

    return {
        "version": VERSION,
        "target": str(target),
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "warnings": warnings,
        "anchors_checked": anchors,
        "territories_checked": territories,
        "workspace_boundaries_checked": workspace_boundaries,
        "quality_scripts_checked": sorted(qscripts),
    }


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def good_context(target: Path) -> str:
    return """# Tilly Project Context

## Identity

| Field | Value |
|-------|-------|
| Name | `fixture-app` |
| Description | `Fixture app for oracle validation.` |
| Manifest | `docs/agents/evidence/20260508T000000Z-tes-project-manifest.json` |

## Initial Semantic Signals

| Signal | Value | Source |
|---|---|---|
| README heading | fixture-app | README.md |
| README summary | Fixture app for oracle validation. | README.md |

## Maximum-Depth Initialization Contract

- Unknowns remain explicit.

## Active Agent Refinement Contract

- Deterministic scaffold: inventory, anchors, scripts, surfaces, and gaps.
- Semantic refinement: the active agent must open strong anchors before
  claiming deep project understanding.
- If anchor reading is blocked, report `Project context: NEEDS_REVIEW`.

## Coverage

| Field | Value |
|-------|-------|
| File count | `5` |

## Project Territories

| Territory | Initial role | Files | Sample anchors |
|---|---|---|---|
| docs | documentation and durable explanation | 1 | `docs/architecture.md` |
| src | product/source code territory | 1 | `src/app.py` |
| tests | test or verification territory | 1 | `tests/test_app.py` |

## Semantic Territory Guide

| Territory | Likely boundary | Evidence | Next move |
|---|---|---|---|
| docs | documentation/API contract boundary | `docs/architecture.md` | cross-check claims against source anchors before editing behavior |
| src | product/source code territory | `src/app.py` | open the listed anchors before claiming ownership or runtime role |
| tests | verification boundary | `tests/test_app.py` | start with local test governance and smallest related test command |

## Weak Anchor Triage

| Category | Sample | Handling |
|---|---|---|
| none detected | n/a | no weak-anchor category was detected by the deterministic scanner |

## Caution Zones

| Zone | Evidence | Guidance |
|---|---|---|
| none detected | n/a | no caution zone was detected by the deterministic scanner |

## Workspace Boundaries

| Source | Kind | Pattern |
|---|---|---|
| package.json | npm workspace | packages/* |

## Source Anchors Read First

| Path | Kind | Bytes |
|---|---|---|
| README.md | .md | 14 |
| package.json | .json | 100 |
| docs/architecture.md | .md | 20 |
| src/app.py | .py | 10 |
| tests/test_app.py | .py | 10 |

## Runtime And Governance Surfaces

| Surface | Status |
|---|---|
| codex_agents | missing |

## Package Scripts

| Script | Command |
|---|---|
| lint | echo lint |
| test | echo test |

## Quality And Certification Scripts

| Script | Command |
|---|---|
| lint | echo lint |
| test | echo test |

## Recertification Gates

| Command | Status |
|---|---|
| git diff --check | PASS |

## Recommended Deep Reads

- `README.md`
- `package.json`
- `docs/architecture.md`
- `src/app.py`
- `tests/test_app.py`

## Next Work Guidance

- For `src`, open the listed anchors before claiming ownership or runtime role.
- For `tests`, start with local test governance and smallest related test command.

## Open Context Questions

- What is the product domain?

## Maintenance Rule

Update this file when project meaning changes.
"""


def make_fixture(target: Path) -> None:
    write(target / "README.md", "# fixture-app\n\nFixture app for oracle validation.\n")
    write(target / "VERSION", "0.1.0\n")
    write(target / ".nvmrc", "20\n")
    write(
        target / "package.json",
        json.dumps(
            {
                "name": "fixture-app",
                "scripts": {"lint": "echo lint", "test": "echo test"},
            },
            indent=2,
        )
        + "\n",
    )
    write(target / "docs/architecture.md", "# Architecture\n")
    write(target / "src/app.py", "print('ok')\n")
    write(target / "tests/test_app.py", "def test_ok(): pass\n")
    write(target / PROJECT_CONTEXT, good_context(target))


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-project-context-") as tempdir:
        target = Path(tempdir)
        make_fixture(target)
        result = analyze(target)
        if result["status"] != "PASS":
            failures.extend(f"good fixture failed: {item}" for item in result["failures"])

        text = (target / PROJECT_CONTEXT).read_text(encoding="utf-8")
        (target / PROJECT_CONTEXT).write_text(text.replace("Fixture app for oracle validation.", "unknown", 1), encoding="utf-8")
        unknown_description = analyze(target)
        if unknown_description["status"] != "FAIL" or not any("non-unknown description" in item for item in unknown_description["failures"]):
            failures.append("oracle must fail when README prose exists but description remains unknown")

        (target / PROJECT_CONTEXT).write_text(text.replace("src/app.py", "src/missing.py"), encoding="utf-8")
        bad_anchor = analyze(target)
        if bad_anchor["status"] != "FAIL" or not any("missing source anchors" in item for item in bad_anchor["failures"]):
            failures.append("oracle must fail when a source anchor is missing")

        (target / PROJECT_CONTEXT).write_text(
            text + "\n```python\n" + "\n".join(f"def copied_{i}(): return {i}" for i in range(8)) + "\n```\n",
            encoding="utf-8",
        )
        copied_code = analyze(target)
        if copied_code["status"] != "FAIL" or not any("bulk copied source code" in item for item in copied_code["failures"]):
            failures.append("oracle must fail when project context bulk-copies source code")

    with tempfile.TemporaryDirectory(prefix="tes-project-context-large-") as tempdir:
        target = Path(tempdir)
        make_fixture(target)
        write(target / "AGENTS.md", "# Local rules\n")
        write(target / "static/app/index.tsx", "export const App = null;\n")
        write(target / "api-docs/schema.json", "{}\n")
        write(target / "self-hosted/config.yml", "service: fixture\n")
        write(target / "fixtures/example.json", "{}\n")
        write(target / "pnpm-lock.yaml", "lockfileVersion: '9.0'\n")
        for index in range(520):
            write(target / "src/generated" / f"file_{index}.py", "VALUE = 1\n")
        generic = good_context(target).replace("## Semantic Territory Guide", "## Missing Semantic Territory Guide")
        write(target / PROJECT_CONTEXT, generic)
        large_generic = analyze(target)
        if large_generic["status"] != "FAIL" or not any("anti-generic section" in item for item in large_generic["failures"]):
            failures.append("oracle must fail large contexts missing anti-generic semantic sections")

    with tempfile.TemporaryDirectory(prefix="tes-project-context-ignored-lock-") as tempdir:
        target = Path(tempdir)
        write(target / ".gitignore", "package-lock.json\n")
        write(target / "AGENTS.md", "# Local rules\n")
        write(target / "package-lock.json", "{\"lockfileVersion\":3}\n")
        subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)
        subprocess.run(["git", "add", ".gitignore", "AGENTS.md"], cwd=target, text=True, capture_output=True, check=False)
        terms = expected_caution_terms(target)
        if "dependency locks" not in terms:
            failures.append("oracle must detect root dependency lockfiles even when ignored by git")

    with tempfile.TemporaryDirectory(prefix="tes-project-context-bootstrap-") as tempdir:
        target = Path(tempdir)
        write(target / "README.md", "# Bootstrap fixture\n")
        write(
            target / "docs/agents/evidence/20260508T000000Z-tes-project-manifest.json",
            json.dumps({"bootstrap": True, "file_count": 0}) + "\n",
        )
        write(
            target / PROJECT_CONTEXT,
            good_context(target).replace("fixture-app", "Bootstrap fixture") + "\n`tes_init bootstrap`\n",
        )
        bootstrap = analyze(target)
        if bootstrap["status"] != "FAIL" or not any("bootstrap-only" in item for item in bootstrap["failures"]):
            failures.append("oracle must fail a bootstrap-only partial PROJECT-CONTEXT.md")

    with tempfile.TemporaryDirectory(prefix="tes-project-context-py-") as tempdir:
        target = Path(tempdir)
        write(target / "README.md", "# README Heading\n\nREADME fallback prose.\n")
        write(target / "pyproject.toml", "[project]\nname = \"py-oracle\"\ndescription = \"Canonical pyproject description.\"\n[tool.pytest.ini_options]\naddopts = \"-q\"\n[tool.ruff]\nline-length = 100\n")
        qscripts = quality_scripts(target)
        if "pytest" not in qscripts or "ruff" not in qscripts:
            failures.append("oracle must derive Python quality scripts from pyproject.toml")
        if not project_has_description(target):
            failures.append("oracle must treat pyproject project.description as a known description")
        if "py-oracle" not in identity_terms(target):
            failures.append("oracle must derive identity terms from pyproject project.name")

    with tempfile.TemporaryDirectory(prefix="tes-project-context-rst-py-") as tempdir:
        target = Path(tempdir)
        write(target / "README.rst", "Django\n======\n\nDjango is a high-level Python web framework.\n")
        write(target / "package.json", json.dumps({"name": "Django", "scripts": {"test": "grunt test"}}) + "\n")
        write(
            target / "pyproject.toml",
            "[project]\n"
            "name = \"Django\"\n"
            "description = \"A high-level Python web framework.\"\n"
            "[tool.tox]\nlegacy_tox_ini = \"\"\n",
        )
        write(target / "tests/runtests.py", "#!/usr/bin/env python\n")
        write(target / "docs/Makefile", "html:\n\t@echo docs\n")
        bad_context = good_context(target).replace("fixture-app", "Django").replace(
            "| Description | `Fixture app for oracle validation.` |",
            "| Description | `unknown` |\n| Identity source | `package.json` |",
        )
        write(target / PROJECT_CONTEXT, bad_context)
        bad = analyze(target)
        if bad["status"] != "FAIL" or not any("package metadata" in item or "prefer pyproject" in item for item in bad["failures"]):
            failures.append("oracle must fail Python projects whose context ignores pyproject description or identity source")
        good = bad_context.replace("| Description | `unknown` |", "| Description | `A high-level Python web framework.` |").replace(
            "| Identity source | `package.json` |",
            "| Identity source | `pyproject.toml` |",
        )
        good = good.replace("| README.md | .md | 14 |", "| README.rst | .rst | 60 |\n| pyproject.toml | .toml | 90 |\n| package.json | .json | 50 |\n| docs/Makefile | [none] | 20 |\n| tests/runtests.py | .py | 20 |")
        good = good.replace("- `README.md`", "- `README.rst`\n- `pyproject.toml`\n- `tests/runtests.py`")
        good = good.replace("| test | echo test |", "| test | grunt test |\n| tox | tox |\n| runtests | cd tests && ./runtests.py |\n| docs | make -C docs html |")
        write(target / PROJECT_CONTEXT, good)
        rst_good = analyze(target)
        if rst_good["status"] != "PASS":
            failures.extend(f"RST Python fixture failed: {item}" for item in rst_good["failures"])

    with tempfile.TemporaryDirectory(prefix="tes-project-context-generated-") as tempdir:
        target = Path(tempdir)
        write(target / "README.md", "# Generated-surface fixture\n\nProject prose.\n")
        write(target / "src/app.py", "print('project')\n")
        write(target / ".agents/skills/tes-init/SKILL.md", "# TES skill\n")
        write(target / ".claude/skills/tes-init/SKILL.md", "# TES skill\n")
        write(target / "skills/tes-init/SKILL.md", "# TES skill\n")
        write(target / ".claude-plugin/plugin.json", "{}\n")
        write(target / ".cursor/rules/tes-engineering-discipline.mdc", "# TES Cursor rule\n")
        write(target / "docs/agents/cortex/CONTRACT.md", "# Cortex\n")
        write(target / "AGENTS.md", "Portable Codex bootloader for repositories adopting Tilly Engineering\n")
        write(target / "CLAUDE.md", "Behavioral engineering discipline for reducing common LLM coding mistakes.\n")
        write(target / "CURSOR.md", "# Using This Repo With Cursor\n\nThin pointer to the Cursor rule layer.\n")
        territories = expected_territories(target)
        anchors = expected_anchors(target)
        # Both TES cursor surfaces, as the real adapter install writes them. A
        # .cursor directory containing ONLY TES files must not surface as project
        # territory (F1: tes-runtime-capabilities.mdc was the missed exclusion).
        write(target / ".cursor/rules/tes-engineering-discipline.mdc", "# TES Cursor rule\n")
        write(target / ".cursor/rules/tes-runtime-capabilities.mdc", "# TES Cursor capability rule\n")
        territories = expected_territories(target)
        for generated in (".agents", ".claude", ".cursor", "skills", ".claude-plugin", "docs"):
            if generated in territories:
                failures.append(f"oracle must exclude generated TES territory: {generated}")
        for generated in ("AGENTS.md", "CLAUDE.md", "CURSOR.md", ".cursor/rules/tes-engineering-discipline.mdc"):
            if generated in anchors:
                failures.append(f"oracle must exclude generated TES anchor: {generated}")
        if "src" not in territories or "src/app.py" not in anchors:
            failures.append("oracle must keep real project territory while excluding TES runtime surfaces")

    with tempfile.TemporaryDirectory(prefix="tes-project-context-ignored-parent-") as tempdir:
        parent = Path(tempdir)
        subprocess.run(["git", "init"], cwd=parent, text=True, capture_output=True, check=False)
        write(parent / ".gitignore", "runs/\n")
        target = parent / "runs" / "canary"
        write(target / "AGENTS.md", "project-owned AGENTS\n")
        write(target / "CLAUDE.md", "project-owned CLAUDE\n")
        anchors = expected_anchors(target)
        if "AGENTS.md" not in anchors or "CLAUDE.md" not in anchors:
            failures.append("oracle must fall back to local anchors when parent Git ignores target")

    with tempfile.TemporaryDirectory(prefix="tes-project-context-monorepo-") as tempdir:
        target = Path(tempdir)
        write(target / "README.md", "# Monorepo fixture\n\nWorkspace prose.\n")
        write(target / "package.json", json.dumps({"name": "monorepo-fixture", "workspaces": ["packages/*"]}) + "\n")
        write(target / "pnpm-workspace.yaml", "packages:\n  - 'apps/*'\n  - 'crates/*/js'\n")
        write(target / "Cargo.toml", "[workspace]\nmembers = [\"crates/*\"]\n")
        write(target / "crates/uv/Cargo.toml", "[package]\nname = \"uv\"\n")
        write(target / "crates/uv/src/lib.rs", "pub fn run() {}\n")
        expected = expected_workspace_boundaries(target)
        for pattern in ("packages/*", "apps/*", "crates/*/js", "crates/*"):
            if pattern not in expected:
                failures.append(f"oracle must expect workspace boundary: {pattern}")
        write(target / PROJECT_CONTEXT, good_context(target).replace("| package.json | npm workspace | packages/* |\n", ""))
        bad = analyze(target)
        if bad["status"] != "FAIL" or not any(
            "missing workspace boundaries" in item or "Rust Cargo workspace boundary" in item for item in bad["failures"]
        ):
            failures.append("oracle must fail when workspace boundaries or Cargo workspace semantics are missing")

    with tempfile.TemporaryDirectory(prefix="tes-project-context-go-provider-") as tempdir:
        target = Path(tempdir)
        write(
            target / "README.md",
            "# Terraform AWS Provider\n\n"
            "[discuss-badge]: https://example.test/badge.svg\n"
            "[discuss]: https://example.test/discuss\n\n"
            "The Terraform AWS Provider maps AWS APIs into Terraform resources and data sources.\n",
        )
        write(target / "go.mod", "module github.com/hashicorp/terraform-provider-aws\n")
        write(
            target / "GNUmakefile",
            "build: prereq-go fmt-check ## Build provider\n"
            "ci-quick: tools go-build testacc-lint ## Run quicker CI checks\n"
            "fmt: ## Fix Go source formatting\n"
            "gen: ## Run generators\n"
            "test: prereq-go ## Run unit tests\n"
            "testacc: prereq-go fmt-check ## Run acceptance tests\n",
        )
        write(target / "docs/README.md", "# Docs\n")
        write(target / "internal/service/s3/bucket.go", "package s3\n")
        write(target / "skaff/go.mod", "module skaff\n")
        if "discuss-badge" in readme_summary(target) or "maps AWS APIs" not in readme_summary(target):
            failures.append("oracle README summary must skip markdown reference definitions before prose")
        qscripts = quality_scripts(target)
        for name in ("build", "ci-quick", "fmt", "gen", "test", "testacc"):
            if name not in qscripts:
                failures.append(f"oracle must derive GNUmakefile quality target: {name}")
        expected = expected_workspace_boundaries(target)
        for pattern in ("internal/service/*", "skaff"):
            if pattern not in expected:
                failures.append(f"oracle must expect Go provider boundary: {pattern}")
        bad_context = good_context(target).replace("fixture-app", "Terraform AWS Provider").replace(
            "| Description | `Fixture app for oracle validation.` |",
            "| Description | `unknown` |",
        )
        write(target / PROJECT_CONTEXT, bad_context)
        bad = analyze(target)
        if bad["status"] != "FAIL" or not any(
            "missing workspace boundaries" in item or "missing quality scripts" in item for item in bad["failures"]
        ):
            failures.append("oracle must fail Go provider contexts without Makefile gates and service boundaries")
        good = bad_context.replace(
            "| Description | `unknown` |",
            "| Description | `The Terraform AWS Provider maps AWS APIs into Terraform resources and data sources.` |",
        )
        good = good.replace(
            "| src | product/source code territory | 1 | `src/app.py` |",
            "| internal | provider internals and service ownership | 1 | `internal/service/s3/bucket.go` |\n"
            "| docs | documentation and durable explanation | 1 | `docs/README.md` |\n"
            "| skaff | local automation and oracles | 1 | `skaff/go.mod` |",
        )
        good = good.replace(
            "| package.json | npm workspace | packages/* |",
            "| go.mod | nested Go module | skaff |\n"
            "| internal/service | provider service packages | internal/service/* |",
        )
        good = good.replace(
            "| package.json | .json | 100 |",
            "| go.mod | .mod | 80 |\n| GNUmakefile | [none] | 120 |\n| docs/README.md | .md | 20 |\n| internal/service/s3/bucket.go | .go | 20 |\n| skaff/go.mod | .mod | 20 |",
        )
        good = good.replace(
            "| lint | echo lint |\n| test | echo test |",
            "| build | make build |\n| ci-quick | make ci-quick |\n| fmt | make fmt |\n| gen | make gen |\n| test | make test |\n| testacc | make testacc |",
        )
        good = good.replace(
            "- `package.json`\n- `docs/architecture.md`\n- `src/app.py`\n- `tests/test_app.py`",
            "- `go.mod`\n- `GNUmakefile`\n- `docs/README.md`\n- `internal/service/s3/bucket.go`\n- `skaff/go.mod`",
        )
        write(target / PROJECT_CONTEXT, good)
        go_good = analyze(target)
        if go_good["status"] != "PASS":
            failures.extend(f"Go provider fixture failed: {item}" for item in go_good["failures"])

    with tempfile.TemporaryDirectory(prefix="tes-project-context-lower-readme-") as tempdir:
        target = Path(tempdir)
        write(target / "readme.md", "# lowercase\n\nLowercase README prose.\n")
        if "lowercase" not in identity_terms(target):
            failures.append("oracle must read lowercase readme.md headings")
        if "Lowercase README prose" not in readme_summary(target):
            failures.append("oracle must read lowercase readme.md prose")

    with tempfile.TemporaryDirectory(prefix="tes-project-context-terraform-") as tempdir:
        target = Path(tempdir)
        write(
            target / "README.md",
            "## Learn Terraform Import\n\n"
            "Learn how to import existing resources under Terraform's management.\n\n"
            "```hcl\n# docker_container.web:\nresource \"docker_container\" \"web\" {}\n```\n",
        )
        write(target / "main.tf", 'resource "null_resource" "example" {}\n')
        if "Learn Terraform Import" not in identity_terms(target):
            failures.append("oracle must accept README level-2 headings outside fenced code")
        if "docker_container.web" in identity_terms(target):
            failures.append("oracle must ignore headings inside fenced code")
        if "main.tf" not in expected_anchors(target):
            failures.append("oracle must expect Terraform root files as source anchors")

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
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    result = self_test() if args.self_test else analyze(args.target)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json_only:
        print("[project-context] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
