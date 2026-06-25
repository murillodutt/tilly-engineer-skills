#!/usr/bin/env python3
"""Validate documentation size budgets and modularization pressure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIMIT = 500
WARN_RATIO = 0.85
LIMITS = {
    "docs/roadmap/README.md": 140,
    "docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md": 1000,
    "docs/evals/EXAMPLES.md": 600,
    # Raised from 2300 to 2500 (2026-06-06): the user manual gained Requirements,
    # Updating, Removing, and Troubleshooting/FAQ sections so it answers real
    # user questions (Diataxis getting-started queue) as one coherent document.
    # Content was already trimmed of governance/architecture leakage; the growth
    # is legitimate per-section overhead x3 languages, not padding.
    "docs/install/USER-MANUAL.html": 2500,
    "docs/index.html": 2800,
    # Carries the COMPLETE LITERAL solution (paste-ready blocks L1-L6 in its
    # "Literal Solution" appendix) so the execution window applies embedded text
    # by id instead of re-designing. The length is the embedded solution, not
    # padding — the same rationale as the assisted-context installer prompt.
    "docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-declared-contract-arbiter-and-effort-gate.md": 800,
}
WARN_RATIOS = {
    "docs/roadmap/README.md": 0.75,
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


def path_in_scope(path: Path) -> bool:
    try:
        relpath = path.relative_to(ROOT).as_posix()
    except ValueError:
        return False
    if relpath in {"README.md", "AGENTS.md"}:
        return True
    if relpath.startswith("docs/") and path.suffix.lower() in {".md", ".html", ".mdc"}:
        return True
    if relpath.startswith("src/") and path.suffix.lower() in {".md", ".mdc"}:
        return True
    return False


def resolve_paths(raw_paths: list[str]) -> list[Path]:
    selected: list[Path] = []
    for raw in raw_paths:
        path = Path(raw).resolve()
        if path.is_file() and path_in_scope(path):
            selected.append(path)
    return sorted(set(selected))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", nargs="+", help="validate only these staged doc paths")
    args = parser.parse_args()

    failures: list[str] = []
    warnings: list[str] = []
    checked = 0
    targets = resolve_paths(args.paths) if args.paths else iter_docs()
    for path in targets:
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
