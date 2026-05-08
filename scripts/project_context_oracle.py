#!/usr/bin/env python3
"""Validate TES project-context quality for installed targets."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.49"
PROJECT_CONTEXT = Path("docs/agents/PROJECT-CONTEXT.md")
PACKAGE_MODE = (ROOT / "scripts").exists()
REQUIRED_SECTIONS = (
    "# Tilly Project Context",
    "## Identity",
    "## Initial Semantic Signals",
    "## Maximum-Depth Initialization Contract",
    "## Active Agent Refinement Contract",
    "## Coverage",
    "## Project Territories",
    "## Source Anchors Read First",
    "## Runtime And Governance Surfaces",
    "## Recommended Deep Reads",
    "## Open Context Questions",
    "## Maintenance Rule",
)
QUALITY_SCRIPT_TERMS = ("lint", "typecheck", "test", "spec", "check", "build", "contract", "validate")
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
ANCHOR_NAMES = (
    "README.md",
    "README",
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "AGENTS.md",
    "CLAUDE.md",
    "CURSOR.md",
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
    if from_git is not None:
        return sorted(path for path in from_git if path.is_file() and not is_excluded(path, target))
    return sorted(
        path
        for path in target.rglob("*")
        if path.is_file() and not is_excluded(path, target)
    )


def is_excluded(path: Path, target: Path) -> bool:
    try:
        relpath = path.relative_to(target)
    except ValueError:
        return True
    if relpath.as_posix() in {
        "docs/agents/PROJECT-CONTEXT.md",
        "docs/agents/PROJECT-REGISTER.md",
    }:
        return True
    if len(relpath.parts) >= 3 and relpath.parts[:3] == ("docs", "agents", "evidence"):
        return True
    parts = relpath.parts
    return any(part in EXCLUDED_PARTS for part in parts)


def read_context(target: Path) -> tuple[str | None, list[str]]:
    path = target / PROJECT_CONTEXT
    if not path.exists():
        return None, [f"missing project context: {PROJECT_CONTEXT.as_posix()}"]
    try:
        return path.read_text(encoding="utf-8"), []
    except UnicodeDecodeError as exc:
        return None, [f"invalid UTF-8 project context: {exc}"]


def package_scripts(target: Path) -> dict[str, str]:
    package = load_json(target / "package.json")
    if not package:
        return {}
    scripts = package.get("scripts")
    if not isinstance(scripts, dict):
        return {}
    return {str(key): str(value) for key, value in scripts.items()}


def quality_scripts(target: Path) -> dict[str, str]:
    return {
        name: command
        for name, command in package_scripts(target).items()
        if any(term in name.lower() for term in QUALITY_SCRIPT_TERMS)
    }


def identity_terms(target: Path) -> list[str]:
    terms: list[str] = []
    package = load_json(target / "package.json")
    if package and package.get("name"):
        terms.append(str(package["name"]))
    readme = target / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("# "):
                terms.append(line[2:].strip())
                break
    if not terms:
        terms.append(target.name)
    return terms


def readme_summary(target: Path) -> str:
    readme = target / "README.md"
    if not readme.exists():
        readme = target / "README"
    if not readme.exists():
        return ""
    paragraph: list[str] = []
    try:
        lines = readme.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return ""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if paragraph:
                break
            continue
        if stripped.startswith(("# ", "##", "|", "-", "* ", "!", "<", "```")):
            if paragraph:
                break
            continue
        if set(stripped) <= {"-", "_", "="}:
            continue
        paragraph.append(stripped)
    return re.sub(r"\s+", " ", " ".join(paragraph)).strip()


def package_has_description(target: Path) -> bool:
    package = load_json(target / "package.json")
    if not package:
        return False
    description = package.get("description")
    return isinstance(description, str) and bool(description.strip())


def expected_anchors(target: Path) -> list[str]:
    files = iter_project_files(target)
    anchors: list[str] = []
    for name in ANCHOR_NAMES:
        path = target / name
        if path.exists() and path.is_file() and not is_excluded(path, target):
            anchors.append(name)
    for dirname in ("src", "app", "server", "client", "tests", "test", "docs", "scripts"):
        root = target / dirname
        if root.exists():
            for path in files:
                try:
                    relpath = path.relative_to(target)
                except ValueError:
                    continue
                if relpath.parts and relpath.parts[0] == dirname:
                    anchors.append(relpath.as_posix())
                    break
    return sorted(dict.fromkeys(anchors))


def expected_territories(target: Path) -> list[str]:
    territories: set[str] = set()
    for path in iter_project_files(target):
        relpath = path.relative_to(target)
        if len(relpath.parts) > 1:
            territories.add(relpath.parts[0])
    return sorted(name for name in territories if name not in {".git", ".tes"})


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

    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"PROJECT-CONTEXT.md missing section: {section}")

    if "docs/agents/evidence/" not in text or "-tes-project-manifest.json" not in text:
        failures.append("PROJECT-CONTEXT.md must link the project manifest evidence")

    identities = identity_terms(target)
    if not any(term and term in text for term in identities):
        failures.append(f"PROJECT-CONTEXT.md missing project identity term: one of {identities}")

    if readme_summary(target) and not package_has_description(target) and "| Description | `unknown` |" in text:
        failures.append("PROJECT-CONTEXT.md must derive a non-unknown description from README prose when package description is absent")

    anchors = expected_anchors(target)
    missing_anchors = [anchor for anchor in anchors if anchor not in text]
    if missing_anchors:
        failures.append(f"PROJECT-CONTEXT.md missing source anchors: {', '.join(missing_anchors[:8])}")

    territories = expected_territories(target)
    missing_territories = [name for name in territories if name not in text]
    if missing_territories:
        failures.append(f"PROJECT-CONTEXT.md missing territories: {', '.join(missing_territories[:8])}")

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
