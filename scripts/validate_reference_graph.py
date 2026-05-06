#!/usr/bin/env python3
"""Validate conservative local Markdown links in the governed reference graph."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
FENCE = re.compile(r"```.*?```", re.DOTALL)
IGNORED_PREFIXES = ("http://", "https://", "mailto:", "app://", "plugin://", "file://")
SCANNED_GLOBS = ("*.md", "docs/**/*.md", "src/**/*.md")


def strip_fences(text: str) -> str:
    return FENCE.sub("", text)


def should_check(target: str) -> bool:
    target = target.strip()
    if not target or target.startswith("#") or target.startswith(IGNORED_PREFIXES):
        return False
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = target.split("#", 1)[0]
    return bool(target) and Path(target).suffix in {".md", ".yml", ".yaml", ".json", ".html", ".py"}


def iter_markdown_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in SCANNED_GLOBS:
        files.update(ROOT.glob(pattern))
    return sorted(path for path in files if path.is_file())


def validate_file(path: Path) -> list[str]:
    failures: list[str] = []
    text = strip_fences(path.read_text(encoding="utf-8"))
    for match in LINK.finditer(text):
        raw = match.group(1).strip()
        if raw.startswith("<") and raw.endswith(">"):
            raw = raw[1:-1]
        if not should_check(raw):
            continue
        target = unquote(raw.split("#", 1)[0])
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(ROOT)
        except ValueError:
            failures.append(f"{path.relative_to(ROOT)} links outside repo: {raw}")
            continue
        if not resolved.exists():
            failures.append(f"{path.relative_to(ROOT)} broken local link: {raw}")
    return failures


def main() -> int:
    failures: list[str] = []
    files = iter_markdown_files()
    for path in files:
        failures.extend(validate_file(path))
    print(json.dumps({"status": "FAIL" if failures else "PASS", "checked_files": len(files), "failures": failures}, indent=2))
    if failures:
        print("[reference-graph] FAIL")
        return 1
    print("[reference-graph] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
