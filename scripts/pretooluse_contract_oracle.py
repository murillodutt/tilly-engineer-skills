#!/usr/bin/env python3
"""Certify the canonical PreToolUse contract document.

This oracle protects the source contract, not installed runtime behavior. Runtime
behavior remains covered by the kernel/session oracles and per-host hook audits.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/architecture/PRETOOLUSE-CONTRACT.md"
PROMPT_PATH = ROOT / "docs/install/HOOK-AUDIT-PROMPT.md"
FRAMEWORK_PATH = ROOT / "docs/architecture/INSTALLATION-FRAMEWORK.md"
DOCS_INDEX_PATH = ROOT / "docs/INDEX.md"
TDS_INDEX_PATH = ROOT / "docs/tds/DOCS-INDEX.yml"
VERSION = "0.3.254"


CONTRACT_TERMS = (
    "PreToolUse is the host-real projection of the Mantra Gate before a tool executes.",
    "host-neutral PreToolUse decision kernel",
    "session/repetition coordinator",
    "host-specific output renderer",
    "runtime ledger writer",
    "PASS_BASIC",
    "PASS_CEILING",
    "NEEDS_DISCOVERABILITY",
    "decision reason codes",
    "classifier trace",
    "host payload evidence",
    "discoverability gate",
    "shell_command_path_extracted",
    "raw shell commands",
    "redacted path class/hash",
    "renderer parity",
    "ledger analytics contract",
    "stable synthetic invocation",
    "current-host provenance",
    "ceiling_evidence_scope.current_host",
    "drift detection",
    "red-capable oracle coverage",
    "Do not call it `PASS_CEILING`.",
    "Ceiling does not mean moving installer logic into the kernel",
)

PROMPT_TERMS = (
    "docs/architecture/PRETOOLUSE-CONTRACT.md",
    "floor contract (`PASS_BASIC`)",
    "ceiling contract (`PASS_CEILING`)",
    "Do not collapse `PASS` into `PASS_CEILING`.",
    "## Ceiling Assessment",
)

FRAMEWORK_TERMS = (
    "PreToolUse's canonical behavioral contract is `docs/architecture/PRETOOLUSE-CONTRACT.md`.",
)

INDEX_TERMS = (
    "architecture/PRETOOLUSE-CONTRACT.md",
)

TDS_TERMS = (
    "docs/architecture/PRETOOLUSE-CONTRACT.md",
    "architecture.pretooluse_contract",
)


@dataclass(frozen=True)
class Mutation:
    name: str
    text: str
    expected_fragment: str


def _missing_terms(text: str, terms: tuple[str, ...], label: str) -> list[str]:
    return [f"{label} missing required term: {term!r}" for term in terms if term not in text]


def validate() -> list[str]:
    failures: list[str] = []
    failures.extend(_missing_terms(CONTRACT_PATH.read_text(encoding="utf-8"), CONTRACT_TERMS, "contract"))
    failures.extend(_missing_terms(PROMPT_PATH.read_text(encoding="utf-8"), PROMPT_TERMS, "prompt"))
    failures.extend(_missing_terms(FRAMEWORK_PATH.read_text(encoding="utf-8"), FRAMEWORK_TERMS, "framework"))
    failures.extend(_missing_terms(DOCS_INDEX_PATH.read_text(encoding="utf-8"), INDEX_TERMS, "docs index"))
    failures.extend(_missing_terms(TDS_INDEX_PATH.read_text(encoding="utf-8"), TDS_TERMS, "tds index"))
    return failures


def _remove(text: str, term: str) -> str:
    if term not in text:
        return text
    return text.replace(term, "")


def red_capability_mutations(contract_text: str) -> list[Mutation]:
    return [
        Mutation("without_pass_basic", _remove(contract_text, "PASS_BASIC"), "PASS_BASIC"),
        Mutation("without_pass_ceiling", _remove(contract_text, "PASS_CEILING"), "PASS_CEILING"),
        Mutation(
            "without_needs_discoverability",
            _remove(contract_text, "NEEDS_DISCOVERABILITY"),
            "NEEDS_DISCOVERABILITY",
        ),
        Mutation("without_reason_codes", _remove(contract_text, "decision reason codes"), "decision reason codes"),
        Mutation("without_classifier_trace", _remove(contract_text, "classifier trace"), "classifier trace"),
        Mutation("without_host_payload_evidence", _remove(contract_text, "host payload evidence"), "host payload evidence"),
        Mutation(
            "without_shell_command_path_extracted",
            _remove(contract_text, "shell_command_path_extracted"),
            "shell_command_path_extracted",
        ),
        Mutation("without_renderer_parity", _remove(contract_text, "renderer parity"), "renderer parity"),
        Mutation("without_drift_detection", _remove(contract_text, "drift detection"), "drift detection"),
    ]


def self_test() -> dict[str, object]:
    failures = validate()
    red_failures: list[str] = []
    original = CONTRACT_PATH.read_text(encoding="utf-8")
    for mutation in red_capability_mutations(original):
        mutated_failures = _missing_terms(mutation.text, CONTRACT_TERMS, "contract")
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
        "contract": str(CONTRACT_PATH.relative_to(ROOT)),
        "failures": failures,
        "red_capability_failures": red_failures,
        "mutants_checked": len(red_capability_mutations(original)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("--self-test is required")

    report = self_test()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
