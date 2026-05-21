#!/usr/bin/env python3
"""Small deterministic oracle for Tilly Engineering Discipline."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


REQUIRED_TERMS = (
    "Assumptions visible",
    "Scope smaller",
    "Edits surgical",
    "Success falsifiable",
    "E = A * S * C * V",
    "Mantra Gate",
    "[🍳 Flash-Fry]",
    "VERIFY -> SCOPE -> BEST_PATH -> DOCUMENT -> ORACLE -> RESOLVE -> STATUS",
    "Infrastructure Decision Gate",
    "Stack Surface Scan",
    "Context7 or official documentation",
    "runtime-bound dependencies",
)

PLAN_FIELDS = (
    "assumptions",
    "ambiguity",
    "stack_surface",
    "simplest_path",
    "deleted_scope",
    "oracle",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--plan", type=Path)
    args = parser.parse_args()

    failures: list[str] = []

    if args.self_test:
        root = Path(__file__).resolve().parents[1]
        skill = root / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        for term in REQUIRED_TERMS:
            if term not in text:
                failures.append(f"missing skill term: {term}")

    if args.plan:
        text = args.plan.read_text(encoding="utf-8").lower()
        for field in PLAN_FIELDS:
            if field not in text:
                failures.append(f"plan missing field: {field}")

    if not args.self_test and not args.plan:
        failures.append("choose --self-test or --plan <file>")

    if failures:
        print("[tes-discipline] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("[tes-discipline] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
