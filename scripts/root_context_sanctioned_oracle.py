#!/usr/bin/env python3
"""Root-Context Sanctioned-Drift Oracle.

Lets a project declare that specific root-context files (`CLAUDE.md`,
`AGENTS.md`, `CURSOR.md`, `.cursor/rules/*.mdc`, `.cursorrules`) are
intentionally customized, so `root_context.py` stops re-flagging them as
`NEEDS_REVIEW` on every postinstall. Without an attestation, a project that
owns its root bootloaders sees a perpetual `NEEDS_REVIEW -> RECOVERED` cycle;
this is recurring noise, not a real defect.

The sanctioned list is a local, gitignored file. It is never tracked. The
oracle and `root_context.py` only know that the file exists and read it at run
time — the same posture as the private-vocabulary allowlist.

Usage:

    python3 scripts/root_context_sanctioned_oracle.py
    python3 scripts/root_context_sanctioned_oracle.py --self-test

The default path is `.tes/root-context-sanctioned.txt`. One entry per line.
Lines starting with `#` are comments. Each entry is a repo-relative root-file
path matched literally (`AGENTS.md`, `.cursor/rules/tes-guidelines.mdc`); prefix
with `re:` for an explicit regex against the relpath.

When the file does not exist, the oracle exits PASS with a single
informational note and `sanctioned_loaded` False. This preserves the current
behavior exactly: with no attestation declared, nothing is suppressed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.185"
DEFAULT_SANCTIONED_PATH = Path(".tes/root-context-sanctioned.txt")


def load_allowlist(path: Path) -> list[tuple[str, re.Pattern[str] | None]]:
    """Read the local sanctioned-drift file and compile each entry.

    Returns a list of (label, pattern) tuples. For a literal path entry the
    pattern is None and matching is an exact relpath comparison against the
    label; for a `re:` entry the pattern is a compiled regex.
    """
    entries: list[tuple[str, re.Pattern[str] | None]] = []
    if not path.is_file():
        return entries
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("re:"):
            pattern_src = line[3:].strip()
            try:
                compiled: re.Pattern[str] | None = re.compile(pattern_src)
            except re.error as exc:
                raise ValueError(
                    f"invalid regex in {path.as_posix()}: {pattern_src}: {exc}"
                ) from exc
            entries.append((line, compiled))
        else:
            entries.append((line, None))
    return entries


def is_sanctioned(relpath: str, allowlist: list[tuple[str, re.Pattern[str] | None]]) -> bool:
    """True when `relpath` matches a sanctioned-drift entry."""
    for label, pattern in allowlist:
        if pattern is None:
            if relpath == label:
                return True
        elif pattern.search(relpath):
            return True
    return False


def load_sanctioned(target: Path) -> list[tuple[str, re.Pattern[str] | None]]:
    """Convenience wrapper used by root_context.py to resolve the default path."""
    return load_allowlist(target / DEFAULT_SANCTIONED_PATH)


def analyze(target: Path, sanctioned_path: Path) -> dict[str, Any]:
    try:
        allowlist = load_allowlist(sanctioned_path)
    except ValueError as exc:
        return {
            "version": VERSION,
            "status": "FAIL",
            "sanctioned_path": sanctioned_path.as_posix(),
            "sanctioned_loaded": False,
            "entries": [],
            "error": str(exc),
        }
    if not allowlist:
        return {
            "version": VERSION,
            "status": "PASS",
            "sanctioned_path": sanctioned_path.as_posix(),
            "sanctioned_loaded": False,
            "note": (
                "no root-context sanctioned-drift attestation declared; "
                "oracle is informational only and suppresses nothing"
            ),
            "entries": [],
        }
    return {
        "version": VERSION,
        "status": "PASS",
        "sanctioned_path": sanctioned_path.as_posix(),
        "sanctioned_loaded": True,
        "entries": [label for label, _ in allowlist],
    }


def self_test() -> dict[str, Any]:
    failures: list[str] = []

    # Fixture 1: no file → PASS, nothing loaded (current behavior preserved).
    with tempfile.TemporaryDirectory(prefix="root-sanctioned-absent-") as tempdir:
        root = Path(tempdir)
        result = analyze(root, root / DEFAULT_SANCTIONED_PATH)
        if result["status"] != "PASS" or result["sanctioned_loaded"]:
            failures.append("absent attestation must PASS and load nothing")

    # Fixture 2: comments-only file → PASS, nothing loaded.
    with tempfile.TemporaryDirectory(prefix="root-sanctioned-empty-") as tempdir:
        root = Path(tempdir)
        path = root / DEFAULT_SANCTIONED_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# only comments\n\n", encoding="utf-8")
        result = analyze(root, path)
        if result["status"] != "PASS" or result["sanctioned_loaded"]:
            failures.append("comments-only attestation must PASS without enforcement")

    # Fixture 3: literal path entry matches exactly, not as a substring.
    with tempfile.TemporaryDirectory(prefix="root-sanctioned-literal-") as tempdir:
        root = Path(tempdir)
        path = root / DEFAULT_SANCTIONED_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("AGENTS.md\n.cursor/rules/tes-guidelines.mdc\n", encoding="utf-8")
        allow = load_allowlist(path)
        if not is_sanctioned("AGENTS.md", allow):
            failures.append("literal entry must match its exact relpath")
        if not is_sanctioned(".cursor/rules/tes-guidelines.mdc", allow):
            failures.append("nested literal entry must match its exact relpath")
        if is_sanctioned("CLAUDE.md", allow):
            failures.append("unlisted relpath must not be sanctioned")
        if is_sanctioned("docs/AGENTS.md", allow):
            failures.append("literal entry must not match as a path suffix")

    # Fixture 4: regex entry matches by pattern.
    with tempfile.TemporaryDirectory(prefix="root-sanctioned-regex-") as tempdir:
        root = Path(tempdir)
        path = root / DEFAULT_SANCTIONED_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("re:^\\.cursor/rules/.*\\.mdc$\n", encoding="utf-8")
        allow = load_allowlist(path)
        if not is_sanctioned(".cursor/rules/tes-runtime-capabilities.mdc", allow):
            failures.append("regex entry must match a conforming relpath")
        if is_sanctioned("AGENTS.md", allow):
            failures.append("regex entry must not match a non-conforming relpath")

    # Fixture 5: invalid regex → structured FAIL.
    with tempfile.TemporaryDirectory(prefix="root-sanctioned-bad-regex-") as tempdir:
        root = Path(tempdir)
        path = root / DEFAULT_SANCTIONED_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("re:(unclosed\n", encoding="utf-8")
        result = analyze(root, path)
        if result["status"] != "FAIL" or "error" not in result:
            failures.append("invalid regex attestation must FAIL with a structured error")

    return {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=ROOT)
    parser.add_argument("--sanctioned", type=Path, default=ROOT / DEFAULT_SANCTIONED_PATH)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
    else:
        result = analyze(args.target.resolve(), args.sanctioned.resolve())

    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json:
        print("[root-context-sanctioned] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
