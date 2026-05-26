#!/usr/bin/env python3
"""Private Vocabulary Oracle.

Enforces the TES private-project-confidentiality contract: any names the
maintainer wants to keep out of TES tracked content are listed in a local
allowlist file, and this oracle fails the gate if any of them appear in
tracked source.

The allowlist file is local and gitignored. It is never tracked. This
keeps the names themselves out of TES — the oracle only knows that the
file exists and reads it at run time.

Usage:

    python3 scripts/private_vocabulary_oracle.py
    python3 scripts/private_vocabulary_oracle.py --self-test

The default allowlist path is `.tes/private-vocabulary.txt`. One entry
per line. Lines starting with `#` are comments. Entries are matched as
case-insensitive whole-word tokens by default; prefix with `re:` to use
an explicit regex pattern.

Scope (scanned by default):

- Tracked `*.md`, `*.mdc`, `*.py`, `*.json`, `*.yml`, `*.yaml`, `*.html`,
  `*.txt`, `*.js`, `*.ts` under the repository root.
- Excluded: `.git/`, `node_modules/`, `.tes/`, `docs/dist/`,
  `dist/`, `<workspace>/tes-sync-workspace/` and other workspace dirs.
- Non-Git fixture roots fall back to scanning the filesystem with the same
  suffix and exclusion rules.

When the allowlist file does not exist, the oracle exits PASS with a
single informational note. This keeps CI green for forks and adopters
who do not declare a private vocabulary.
"""

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
VERSION = "0.3.136"
DEFAULT_ALLOWLIST_PATH = Path(".tes/private-vocabulary.txt")
SCAN_SUFFIXES = {
    ".md",
    ".mdc",
    ".py",
    ".json",
    ".yml",
    ".yaml",
    ".html",
    ".txt",
    ".js",
    ".ts",
}
EXCLUDE_DIR_NAMES = {
    ".git",
    "node_modules",
    ".tes",
    "dist",
    "docs-archive",
}
EXCLUDE_PATH_PREFIXES = (
    "docs/dist/",
    ".claude/skills/tes-sync-workspace/",
)


def load_allowlist(path: Path) -> list[tuple[str, re.Pattern[str]]]:
    """Read the local allowlist file and compile each entry to a pattern.

    Returns a list of (label, compiled_pattern) tuples. `label` is the
    raw entry as written so failures can reference it without echoing
    additional context.
    """
    entries: list[tuple[str, re.Pattern[str]]] = []
    if not path.is_file():
        return entries
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("re:"):
            pattern_src = line[3:].strip()
            try:
                compiled = re.compile(pattern_src, re.IGNORECASE)
            except re.error as exc:
                raise ValueError(
                    f"invalid regex in {path.as_posix()}: {pattern_src}: {exc}"
                ) from exc
        else:
            compiled = re.compile(
                rf"(?<![A-Za-z0-9_]){re.escape(line)}(?![A-Za-z0-9_])",
                re.IGNORECASE,
            )
        entries.append((line, compiled))
    return entries


def _should_scan(path: Path, root: Path) -> bool:
    if path.suffix not in SCAN_SUFFIXES:
        return False
    try:
        relpath = path.relative_to(root).as_posix()
    except ValueError:
        return False
    for prefix in EXCLUDE_PATH_PREFIXES:
        if relpath.startswith(prefix):
            return False
    for part in path.relative_to(root).parts:
        if part in EXCLUDE_DIR_NAMES:
            return False
    return True


def scan_paths(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        paths = [
            root / raw.decode("utf-8", errors="replace")
            for raw in result.stdout.split(b"\0")
            if raw
        ]
    else:
        paths = [path for path in root.rglob("*") if path.is_file()]
    return [path for path in paths if path.is_file() and _should_scan(path, root)]


def scan(
    root: Path,
    allowlist: list[tuple[str, re.Pattern[str]]],
) -> list[dict[str, Any]]:
    """Walk the tree and report any match against the allowlist patterns."""
    findings: list[dict[str, Any]] = []
    if not allowlist:
        return findings
    for path in sorted(scan_paths(root)):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for label, pattern in allowlist:
                if pattern.search(line):
                    findings.append(
                        {
                            "code": "private_vocabulary.match",
                            "severity": "fail",
                            "path": path.relative_to(root).as_posix(),
                            "line": lineno,
                            "label": label,
                        }
                    )
    return findings


def analyze(root: Path, allowlist_path: Path) -> dict[str, Any]:
    try:
        allowlist = load_allowlist(allowlist_path)
    except ValueError as exc:
        return {
            "version": VERSION,
            "status": "FAIL",
            "allowlist_path": allowlist_path.as_posix(),
            "allowlist_loaded": False,
            "findings": [],
            "error": str(exc),
        }
    if not allowlist:
        return {
            "version": VERSION,
            "status": "PASS",
            "allowlist_path": allowlist_path.as_posix(),
            "allowlist_loaded": False,
            "note": (
                "no private-vocabulary allowlist declared; "
                "oracle is informational only"
            ),
            "findings": [],
        }
    findings = scan(root, allowlist)
    return {
        "version": VERSION,
        "status": "FAIL" if findings else "PASS",
        "allowlist_path": allowlist_path.as_posix(),
        "allowlist_loaded": True,
        "entries": len(allowlist),
        "findings": findings,
    }


def self_test() -> dict[str, Any]:
    failures: list[str] = []

    # Fixture 1: empty allowlist file → PASS, allowlist_loaded False.
    with tempfile.TemporaryDirectory(prefix="priv-vocab-empty-") as tempdir:
        root = Path(tempdir)
        allow = root / DEFAULT_ALLOWLIST_PATH
        allow.parent.mkdir(parents=True, exist_ok=True)
        allow.write_text("# only comments\n\n", encoding="utf-8")
        result = analyze(root, allow)
        if result["status"] != "PASS" or result["allowlist_loaded"]:
            failures.append("empty allowlist fixture must PASS without enforcement")

    # Fixture 2: allowlist with a token that does not appear → PASS.
    with tempfile.TemporaryDirectory(prefix="priv-vocab-clean-") as tempdir:
        root = Path(tempdir)
        allow = root / DEFAULT_ALLOWLIST_PATH
        allow.parent.mkdir(parents=True, exist_ok=True)
        allow.write_text("absent-token\n", encoding="utf-8")
        (root / "README.md").write_text("# clean content\nno banned words.\n", encoding="utf-8")
        result = analyze(root, allow)
        if result["status"] != "PASS":
            failures.append("clean fixture must PASS")

    # Fixture 3: token appears in tracked content → FAIL with structured finding.
    with tempfile.TemporaryDirectory(prefix="priv-vocab-leak-") as tempdir:
        root = Path(tempdir)
        allow = root / DEFAULT_ALLOWLIST_PATH
        allow.parent.mkdir(parents=True, exist_ok=True)
        allow.write_text("banned-word\n", encoding="utf-8")
        (root / "leak.md").write_text("This file mentions banned-word inline.\n", encoding="utf-8")
        result = analyze(root, allow)
        if result["status"] != "FAIL" or not result["findings"]:
            failures.append("leak fixture must FAIL with findings")
        elif result["findings"][0]["path"] != "leak.md":
            failures.append("leak fixture must name the offending file")

    # Fixture 4: word-boundary — short token must not match a longer unrelated word.
    with tempfile.TemporaryDirectory(prefix="priv-vocab-boundary-") as tempdir:
        root = Path(tempdir)
        allow = root / DEFAULT_ALLOWLIST_PATH
        allow.parent.mkdir(parents=True, exist_ok=True)
        allow.write_text("port\n", encoding="utf-8")
        (root / "report.md").write_text("# Report\nThis report is unrelated.\n", encoding="utf-8")
        result = analyze(root, allow)
        if result["status"] != "PASS":
            failures.append(
                "word-boundary fixture must PASS; short token must not match longer word"
            )

    # Fixture 5: regex entry compiles and matches.
    with tempfile.TemporaryDirectory(prefix="priv-vocab-regex-") as tempdir:
        root = Path(tempdir)
        allow = root / DEFAULT_ALLOWLIST_PATH
        allow.parent.mkdir(parents=True, exist_ok=True)
        allow.write_text("re:\\bsecret-\\d+\\b\n", encoding="utf-8")
        (root / "code.py").write_text("# token secret-42 here\n", encoding="utf-8")
        result = analyze(root, allow)
        if result["status"] != "FAIL":
            failures.append("regex entry fixture must FAIL when the pattern matches")

    # Fixture 6: invalid regex returns structured error.
    with tempfile.TemporaryDirectory(prefix="priv-vocab-bad-regex-") as tempdir:
        root = Path(tempdir)
        allow = root / DEFAULT_ALLOWLIST_PATH
        allow.parent.mkdir(parents=True, exist_ok=True)
        allow.write_text("re:(unclosed\n", encoding="utf-8")
        result = analyze(root, allow)
        if result["status"] != "FAIL" or "error" not in result:
            failures.append("invalid regex fixture must FAIL with a structured error")

    # Fixture 7: excluded paths do not produce findings even when they
    # contain a banned token. This is what lets historical evidence
    # under docs/dist/ stay reachable without breaking the gate.
    with tempfile.TemporaryDirectory(prefix="priv-vocab-exclude-") as tempdir:
        root = Path(tempdir)
        allow = root / DEFAULT_ALLOWLIST_PATH
        allow.parent.mkdir(parents=True, exist_ok=True)
        allow.write_text("banned-word\n", encoding="utf-8")
        excluded = root / "docs" / "dist" / "0.0.0"
        excluded.mkdir(parents=True, exist_ok=True)
        (excluded / "note.md").write_text("banned-word inside an excluded path\n", encoding="utf-8")
        result = analyze(root, allow)
        if result["status"] != "PASS":
            failures.append("excluded-path fixture must PASS; bundle archives must not break the gate")

    # Fixture 8: in a Git worktree, only tracked source participates. Ignored
    # local scratch content must not fail a package-source confidentiality gate.
    with tempfile.TemporaryDirectory(prefix="priv-vocab-git-ignore-") as tempdir:
        root = Path(tempdir)
        subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
        allow = root / DEFAULT_ALLOWLIST_PATH
        allow.parent.mkdir(parents=True, exist_ok=True)
        allow.write_text("banned-word\n", encoding="utf-8")
        (root / ".gitignore").write_text("tmp/\n", encoding="utf-8")
        (root / "README.md").write_text("# clean tracked content\n", encoding="utf-8")
        subprocess.run(["git", "add", ".gitignore", "README.md"], cwd=root, text=True, capture_output=True, check=True)
        scratch = root / "tmp" / "scratch.md"
        scratch.parent.mkdir(parents=True, exist_ok=True)
        scratch.write_text("banned-word in ignored scratch\n", encoding="utf-8")
        result = analyze(root, allow)
        if result["status"] != "PASS":
            failures.append("git-ignored scratch fixture must PASS")

        (root / "tracked.md").write_text("banned-word in tracked source\n", encoding="utf-8")
        subprocess.run(["git", "add", "tracked.md"], cwd=root, text=True, capture_output=True, check=True)
        result = analyze(root, allow)
        if result["status"] != "FAIL" or not result["findings"]:
            failures.append("git-tracked leak fixture must FAIL")

    return {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=ROOT)
    parser.add_argument(
        "--allowlist",
        type=Path,
        default=ROOT / DEFAULT_ALLOWLIST_PATH,
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
    else:
        result = analyze(args.target.resolve(), args.allowlist.resolve())

    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json:
        print("[private-vocabulary] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
