#!/usr/bin/env python3
"""Enforce direct or associated Markdown documentation for code files."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.247"

CODE_SUFFIXES = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".sh", ".ps1"}
DOC_SUFFIXES = {".md", ".mdc"}
EXCLUDED_PARTS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "tmp",
    "dist",
    "build",
}


@dataclass(frozen=True)
class Finding:
    path: str
    code: str
    message: str


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def is_code_path(path: Path) -> bool:
    return path.suffix.lower() in CODE_SUFFIXES and not is_excluded(path)


def normalize_path(root: Path, path: Path) -> Path:
    resolved = path if path.is_absolute() else root / path
    try:
        return resolved.resolve().relative_to(root.resolve())
    except ValueError:
        return path


def first_significant_line(path: Path) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line in lines[:20]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#!") or stripped.startswith("# -*-"):
            continue
        return stripped
    return ""


def has_python_module_doc(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return False
    return bool(ast.get_docstring(tree))


def has_top_level_comment(path: Path) -> bool:
    line = first_significant_line(path)
    return line.startswith(("#", "//", "/*", "/**"))


def has_direct_documentation(root: Path, relpath: Path) -> bool:
    path = root / relpath
    if relpath.suffix.lower() == ".py" and has_python_module_doc(path):
        return True
    return has_top_level_comment(path)


def markdown_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in DOC_SUFFIXES and not is_excluded(path.relative_to(root)):
            paths.append(path.relative_to(root))
    return paths


def has_associated_markdown(root: Path, relpath: Path, docs: list[Path]) -> bool:
    needle = relpath.as_posix()
    backticked = f"`{needle}`"
    for doc in docs:
        try:
            text = (root / doc).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = (root / doc).read_text(encoding="utf-8", errors="ignore")
        if needle in text or backticked in text:
            return True
    return False


def git_paths(args: list[str], root: Path) -> list[Path]:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=False)
    if result.returncode != 0:
        return []
    return [Path(raw.decode("utf-8")) for raw in result.stdout.split(b"\0") if raw]


def tracked_code_paths(root: Path) -> list[Path]:
    paths = git_paths(["ls-files", "-z"], root)
    if not paths:
        paths = [path.relative_to(root) for path in root.rglob("*") if path.is_file()]
    return sorted(path for path in paths if is_code_path(path))


def staged_code_paths(root: Path) -> list[Path]:
    paths = git_paths(["diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"], root)
    return sorted(path for path in paths if is_code_path(path))


def validate(root: Path, paths: list[Path]) -> list[Finding]:
    docs = markdown_paths(root)
    findings: list[Finding] = []
    for relpath in sorted({normalize_path(root, path) for path in paths}):
        if not is_code_path(relpath):
            continue
        if not (root / relpath).is_file():
            findings.append(Finding(relpath.as_posix(), "missing_file", "code path does not exist"))
            continue
        if has_direct_documentation(root, relpath) or has_associated_markdown(root, relpath, docs):
            continue
        findings.append(
            Finding(
                relpath.as_posix(),
                "missing_code_documentation",
                "code must have a module/top-level doc comment or an associated Markdown reference",
            )
        )
    return findings


def self_test() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="tes-code-docs-") as temp:
        root = Path(temp)
        (root / "scripts").mkdir()
        (root / "docs").mkdir()
        direct = root / "scripts" / "direct.py"
        direct.write_text('"""Documented script."""\n\nprint("ok")\n', encoding="utf-8")
        associated = root / "scripts" / "associated.py"
        associated.write_text("print('ok')\n", encoding="utf-8")
        (root / "docs" / "associated.md").write_text("Covers `scripts/associated.py`.\n", encoding="utf-8")
        missing = root / "scripts" / "missing.py"
        missing.write_text("print('missing')\n", encoding="utf-8")
        js = root / "scripts" / "direct.js"
        js.write_text("#!/usr/bin/env node\n// Documented JavaScript entrypoint.\nconsole.log('ok');\n", encoding="utf-8")
        findings = validate(root, [direct, associated, missing, js])
        missing_paths = {finding.path for finding in findings}
        failures: list[str] = []
        if missing_paths != {"scripts/missing.py"}:
            failures.append(f"expected only scripts/missing.py to fail, got {sorted(missing_paths)}")
        return {
            "version": VERSION,
            "status": "PASS" if not failures else "FAIL",
            "failures": failures,
            "fixtures_checked": 4,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate code documentation coverage.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--staged-only", action="store_true")
    parser.add_argument("--paths", nargs="*")
    args = parser.parse_args()

    if args.self_test:
        report = self_test()
    else:
        if args.paths is not None and args.paths:
            paths = [Path(path) for path in args.paths]
        elif args.staged_only:
            paths = staged_code_paths(ROOT)
        else:
            paths = tracked_code_paths(ROOT)
        findings = validate(ROOT, paths)
        report = {
            "version": VERSION,
            "status": "PASS" if not findings else "FAIL",
            "checked_files": len([path for path in paths if is_code_path(normalize_path(ROOT, path))]),
            "findings": [finding.__dict__ for finding in findings],
        }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
