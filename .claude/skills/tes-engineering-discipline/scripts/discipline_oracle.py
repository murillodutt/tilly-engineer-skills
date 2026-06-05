#!/usr/bin/env python3
"""Small deterministic oracle for Tilly Engineering Discipline."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


REQUIRED_TERMS = (
    "Assumptions visible",
    "Scope smaller",
    "Edits surgical",
    "Success falsifiable",
    "E = A * S * C * V",
    "Maturity Layer Gate",
    "Birth",
    "Consolidation",
    "Evolution",
    "Platform",
    "Fit First",
    "promotion evidence",
    "protected baseline",
    "allowed complexity",
    "forbidden complexity",
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
    "maturity_layer",
    "promotion_evidence",
    "protected_baseline",
    "stack_surface",
    "simplest_path",
    "allowed_complexity",
    "forbidden_complexity",
    "deleted_scope",
    "oracle",
)

VALID_LAYERS = ("birth", "consolidation", "evolution", "platform")
GENERIC_VALUES = {
    "as needed",
    "as appropriate",
    "everything",
    "good system",
    "later",
    "n/a",
    "na",
    "none",
    "ok",
    "oracle",
    "relevant",
    "same",
    "test",
    "tests",
    "the whole thing",
    "tbd",
    "todo",
    "unknown",
}
ORACLE_SIGNALS = (
    "build",
    "bun ",
    "check",
    "fixture",
    "lint",
    "npm ",
    "oracle",
    "pytest",
    "python",
    "reproducer",
    "run ",
    "test",
    "typecheck",
)


def normalize(value: str) -> str:
    return " ".join(value.lower().strip().split())


def parse_plan_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    current: str | None = None
    field_names = set(PLAN_FIELDS)
    pattern = re.compile(r"^\s*([A-Za-z_]+)\s*:\s*(.*)$")

    for line in text.splitlines():
        match = pattern.match(line)
        if match and match.group(1).lower() in field_names:
            current = match.group(1).lower()
            fields[current] = match.group(2).strip()
            continue

        if current and (line.startswith(" ") or line.strip().startswith(("-", "*"))):
            value = line.strip().lstrip("-*").strip()
            if value:
                fields[current] = f"{fields[current]} {value}".strip()
            continue

        if line.strip() and not line.startswith(" "):
            current = None

    return fields


def is_generic(value: str, *, allow_birth_none: bool = False) -> bool:
    normalized = normalize(value)
    if not normalized:
        return True
    if allow_birth_none and normalized in {"none", "no higher-layer evidence", "default birth"}:
        return False
    if normalized in GENERIC_VALUES:
        return True
    return False


def selected_layer(value: str) -> str | None:
    normalized = normalize(value)
    matches = [layer for layer in VALID_LAYERS if layer in normalized.split()]
    if len(matches) == 1:
        return matches[0]
    if normalized in VALID_LAYERS:
        return normalized
    return None


def validate_plan_text(text: str) -> list[str]:
    failures: list[str] = []
    lowered = text.lower()
    fields = parse_plan_fields(text)

    for field in PLAN_FIELDS:
        if field not in lowered:
            failures.append(f"plan missing field: {field}")
        if field not in fields:
            failures.append(f"plan missing structured value: {field}")

    if failures:
        return failures

    layer = selected_layer(fields["maturity_layer"])
    if layer is None:
        failures.append("maturity_layer must be exactly one of Birth, Consolidation, Evolution, or Platform")
        layer = "unknown"

    for field in PLAN_FIELDS:
        allow_birth_none = field == "promotion_evidence" and layer == "birth"
        if is_generic(fields[field], allow_birth_none=allow_birth_none):
            failures.append(f"plan field is empty or generic: {field}")

    if layer != "birth":
        for field in (
            "promotion_evidence",
            "protected_baseline",
            "allowed_complexity",
            "forbidden_complexity",
        ):
            if normalize(fields[field]) in {"none", "no higher-layer evidence", "default birth"}:
                failures.append(f"{field} cannot be none outside Birth")

    oracle = normalize(fields["oracle"])
    if not any(signal in f" {oracle} " for signal in ORACLE_SIGNALS):
        failures.append("oracle must name a falsifiable command, test, fixture, or check")

    return failures


def semantic_self_test() -> list[str]:
    valid_plan = """
engineering_discipline:
  assumptions: adapter contract already exists
  ambiguity: no unresolved authority conflict
  maturity_layer: Evolution
  promotion_evidence: accepted adapter contract used by existing installs
  protected_baseline: compatibility interface behavior
  stack_surface: adapter source and parity oracle
  simplest_path: keep the interface and simplify internals behind it
  allowed_complexity: compatibility wrapper stays in place
  forbidden_complexity: deleting the interface or adding a plugin framework
  deleted_scope: broad adapter redesign
  oracle: python3 scripts/adapter_parity_readiness.py
"""
    vague_plan = """
engineering_discipline:
  assumptions: ok
  ambiguity: ok
  maturity_layer: Evolution
  promotion_evidence: good system
  protected_baseline: the whole thing
  stack_surface: relevant
  simplest_path: as needed
  allowed_complexity: as needed
  forbidden_complexity: same
  deleted_scope: later
  oracle: maybe
"""
    failures: list[str] = []
    if validate_plan_text(valid_plan):
        failures.append("semantic self-test rejected a valid Evolution plan")
    if not validate_plan_text(vague_plan):
        failures.append("semantic self-test accepted a vague promoted plan")
    return failures


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
        failures.extend(semantic_self_test())

    if args.plan:
        text = args.plan.read_text(encoding="utf-8")
        failures.extend(validate_plan_text(text))

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
