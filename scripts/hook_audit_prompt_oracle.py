#!/usr/bin/env python3
"""Certify the installed hook-audit prompt contract."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = ROOT / "docs/install/HOOK-AUDIT-PROMPT.md"
VERSION = "0.3.211"


REQUIRED_TERMS = (
    "This is a per-host native audit",
    "Do not fail the current run only because\nanother platform's native tool is unavailable",
    "CONFIGURED, OBSERVED from prior ledger records, CONTRACT_SIMULATED, or",
    "If this is an adopter target, mark that source gate\nN/A",
    "Edit/MultiEdit/StrReplace coverage is optional",
    "marker_emitted: true",
    "Before any native forbidden-shell test",
    "verify `apply_patch`, `Bash`,\n  `Shell`, and `shell`",
    "Codex `tool_input.command` is the canonical patch-body field",
    "defensive aliases `input`, `patch`, and `arguments.*`",
    "alias-key failures are findings",
    "parallel host projections unless the same agent/event/invocation/decision is\n  repeated identically",
    "CONTRACT_SIMULATED: host-specific contract was proven",
    "PASS_WITH_FINDINGS allowance is closed and narrow",
    "Missing current-host native\nPreToolUse, matcher gaps, or execution of a forbidden command is FAIL",
)

FORBIDDEN_TERMS = (
    "all hosts must be native in one execution",
    "Mark FAIL if Codex, Claude, and Cursor are not all OBSERVED natively in this execution.",
    "fail the current run because another platform's native tool is unavailable",
)


@dataclass(frozen=True)
class Mutation:
    name: str
    text: str
    expected_fragment: str


def validate_text(text: str) -> list[str]:
    failures: list[str] = []
    for term in REQUIRED_TERMS:
        if term not in text:
            failures.append(f"missing required hook-audit prompt term: {term!r}")
    for term in FORBIDDEN_TERMS:
        if term in text:
            failures.append(f"forbidden hook-audit prompt term present: {term!r}")
    return failures


def _remove(text: str, term: str) -> str:
    if term not in text:
        return text
    return text.replace(term, "", 1)


def red_capability_mutations(text: str) -> list[Mutation]:
    return [
        Mutation(
            "without_per_host_native_contract",
            _remove(text, "This is a per-host native audit"),
            "per-host native audit",
        ),
        Mutation(
            "without_contract_simulated_evidence_class",
            _remove(text, "CONTRACT_SIMULATED: host-specific contract was proven"),
            "CONTRACT_SIMULATED",
        ),
        Mutation(
            "without_codex_shell_matcher_terms",
            _remove(text, "verify `apply_patch`, `Bash`,\n  `Shell`, and `shell`"),
            "apply_patch",
        ),
        Mutation(
            "without_marker_ledger_proof",
            _remove(text, "marker_emitted: true"),
            "marker_emitted",
        ),
        Mutation(
            "without_codex_patch_alias_contract",
            _remove(text, "defensive aliases `input`, `patch`, and `arguments.*`"),
            "defensive aliases",
        ),
        Mutation(
            "without_dual_projection_contract",
            _remove(text, "parallel host projections unless the same agent/event/invocation/decision is\n  repeated identically"),
            "parallel host projections",
        ),
        Mutation(
            "cursor_edit_made_mandatory",
            text.replace(
                "Edit/MultiEdit/StrReplace coverage is optional",
                "Edit/MultiEdit/StrReplace coverage is mandatory",
                1,
            ),
            "Edit/MultiEdit/StrReplace coverage is optional",
        ),
        Mutation(
            "open_pass_with_findings_allowance",
            _remove(text, "PASS_WITH_FINDINGS allowance is closed and narrow"),
            "PASS_WITH_FINDINGS allowance",
        ),
        Mutation(
            "all_hosts_native_false_fail",
            text
            + "\nMark FAIL if Codex, Claude, and Cursor are not all OBSERVED natively in this execution.\n",
            "forbidden hook-audit prompt term present",
        ),
    ]


def self_test() -> dict[str, object]:
    text = PROMPT_PATH.read_text(encoding="utf-8")
    failures = validate_text(text)
    red_failures: list[str] = []
    for mutation in red_capability_mutations(text):
        mutated_failures = validate_text(mutation.text)
        if not mutated_failures:
            red_failures.append(f"{mutation.name}: mutant unexpectedly passed")
            continue
        if not any(mutation.expected_fragment in failure for failure in mutated_failures):
            red_failures.append(
                f"{mutation.name}: expected failure containing {mutation.expected_fragment!r}, "
                f"got {mutated_failures!r}"
            )
    status = "PASS" if not failures and not red_failures else "FAIL"
    return {
        "version": VERSION,
        "status": status,
        "prompt": str(PROMPT_PATH.relative_to(ROOT)),
        "failures": failures,
        "red_capability_failures": red_failures,
        "mutants_checked": len(red_capability_mutations(text)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    report = self_test()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
