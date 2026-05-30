#!/usr/bin/env python3
"""Validate documentation size budgets and modularization pressure."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIMIT = 500
WARN_RATIO = 0.85
LIMITS = {
    "docs/roadmap/README.md": 140,
    "docs/roadmap/TES-TTS-SKILL-ROADMAP.md": 120,
    "docs/roadmap/TES-TTS-SKILL-ROADMAP-REGISTRY.md": 160,
    "docs/roadmap/TES-TTS-SKILL-ROADMAP-HISTORY.md": 140,
    "docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md": 1000,
    "docs/evals/EXAMPLES.md": 600,
    "docs/install/USER-MANUAL.html": 2210,
    "docs/index.html": 2800,
}
WARN_RATIOS = {
    "docs/roadmap/README.md": 0.75,
    "docs/roadmap/TES-TTS-SKILL-ROADMAP.md": 0.75,
    "docs/roadmap/TES-TTS-SKILL-ROADMAP-REGISTRY.md": 0.75,
    "docs/roadmap/TES-TTS-SKILL-ROADMAP-HISTORY.md": 0.75,
}
SCAN_PATTERNS = (
    "README.md",
    "AGENTS.md",
    "docs/**/*.md",
    "docs/**/*.html",
    "src/**/*.md",
    "src/**/*.mdc",
)


def iter_docs() -> list[Path]:
    paths: set[Path] = set()
    for pattern in SCAN_PATTERNS:
        paths.update(ROOT.glob(pattern))
    return sorted(path for path in paths if path.is_file())


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def limit_for(path: Path) -> int:
    relpath = path.relative_to(ROOT).as_posix()
    return LIMITS.get(relpath, DEFAULT_LIMIT)


def warn_ratio_for(path: Path) -> float:
    relpath = path.relative_to(ROOT).as_posix()
    return WARN_RATIOS.get(relpath, WARN_RATIO)


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []
    checked = 0
    for path in iter_docs():
        checked += 1
        relpath = path.relative_to(ROOT).as_posix()
        count = line_count(path)
        limit = limit_for(path)
        warn_at = int(limit * warn_ratio_for(path))
        if count > limit:
            failures.append(f"{relpath} has {count} lines; limit is {limit}. Modularize before adding more.")
        elif count >= warn_at:
            warnings.append(f"{relpath} has {count} lines; partition review starts at {warn_at}; limit is {limit}.")

    print(json.dumps(
        {
            "status": "FAIL" if failures else "PASS",
            "checked_files": checked,
            "default_limit": DEFAULT_LIMIT,
            "overrides": LIMITS,
            "warn_ratios": WARN_RATIOS,
            "warnings": warnings,
            "failures": failures,
        },
        indent=2,
    ))
    if failures:
        print("[doc-size] FAIL")
        return 1
    print("[doc-size] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
