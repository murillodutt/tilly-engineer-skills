#!/usr/bin/env python3
"""Validate TES TTS provider candidate review without probing providers."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "benchmarks/tes-tts/provider-candidate-review.json"
DOC_PATH = ROOT / "docs/roadmap/tes-tts/TES-TTS-PROVIDER-CANDIDATE-REVIEW.md"
VERSION = "0.3.155"

REQUIRED_FIELDS = {
    "rank",
    "layer",
    "candidate",
    "decision",
    "probe_required",
    "no_install",
    "no_download",
    "no_bundle",
    "no_certification",
    "license_note",
    "offline_note",
    "maintenance_note",
    "language_coverage_note",
    "reason",
}
ALLOWED_DECISIONS = {
    "selected",
    "deferred",
    "degraded",
    "rejected",
}
REQUIRED_LAYERS = {
    "unicode_cleanup",
    "locale_normalization",
    "language_detection",
    "translation",
    "pronunciation_g2p_ipa",
    "hebrew_enrichment",
    "tts_text_normalization",
}
REQUIRED_CANDIDATES = {
    "ftfy",
    "ICU / CLDR",
    "Babel",
    "Lingua",
    "CLD3",
    "fastText lid.176",
    "Argos Translate",
    "eSpeak NG",
    "phonemizer",
    "gruut",
    "Epitran",
    "eSpeak NG he",
    "Phonikud",
    "NVIDIA NeMo text processing",
}
FORBIDDEN_IMPORT_ROOTS = {
    "http",
    "urllib",
    "requests",
    "socket",
    "subprocess",
    "pip",
    "venv",
}
FORBIDDEN_CALL_NAMES = {
    "open",
    "system",
    "popen",
    "run",
    "call",
    "check_call",
    "check_output",
    "urlopen",
    "request",
    "NamedTemporaryFile",
    "mkstemp",
}
FORBIDDEN_ATTRIBUTE_CALLS = {
    "write_text",
    "write_bytes",
    "mkdir",
    "touch",
    "unlink",
    "rename",
    "replace",
}


def load_review() -> list[dict[str, Any]]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def validate_no_side_effect_surface() -> list[str]:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    failures: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in FORBIDDEN_IMPORT_ROOTS:
                    failures.append(f"forbidden import: {alias.name}")
        if isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".", 1)[0]
            if root in FORBIDDEN_IMPORT_ROOTS:
                failures.append(f"forbidden import: {node.module}")
        if isinstance(node, ast.Call):
            function = node.func
            if isinstance(function, ast.Name) and function.id in FORBIDDEN_CALL_NAMES:
                failures.append(f"forbidden call: {function.id}")
            if isinstance(function, ast.Attribute) and function.attr in FORBIDDEN_ATTRIBUTE_CALLS:
                failures.append(f"forbidden attribute call: {function.attr}")
    return failures


def validate_review(review: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    ranks: list[int] = []
    layers: set[str] = set()
    candidates: set[str] = set()
    decisions: set[str] = set()
    selected_layers: set[str] = set()
    for item in review:
        missing = sorted(REQUIRED_FIELDS - set(item))
        if missing:
            failures.append(f"{item.get('candidate', '<unknown>')}: missing fields {missing}")
            continue
        ranks.append(item["rank"])
        layers.add(item["layer"])
        candidates.add(item["candidate"])
        decisions.add(item["decision"])
        if item["decision"] == "selected":
            selected_layers.add(item["layer"])
        if item["decision"] not in ALLOWED_DECISIONS:
            failures.append(f"{item['candidate']}: invalid decision {item['decision']}")
        if item["probe_required"] is not True:
            failures.append(f"{item['candidate']}: probe_required must be true")
        if item["no_install"] is not True:
            failures.append(f"{item['candidate']}: no_install must be true")
        if item["no_download"] is not True:
            failures.append(f"{item['candidate']}: no_download must be true")
        if item["no_bundle"] is not True:
            failures.append(f"{item['candidate']}: no_bundle must be true")
        if item["no_certification"] is not True:
            failures.append(f"{item['candidate']}: no_certification must be true")
        for field in (
            "license_note",
            "offline_note",
            "maintenance_note",
            "language_coverage_note",
            "reason",
        ):
            if not item[field]:
                failures.append(f"{item['candidate']}: {field} must be non-empty")

    expected_ranks = list(range(1, len(review) + 1))
    if sorted(ranks) != expected_ranks:
        failures.append(f"ranks must be contiguous from 1: got {sorted(ranks)}")

    missing_layers = sorted(REQUIRED_LAYERS - layers)
    if missing_layers:
        failures.append(f"missing layers: {missing_layers}")

    missing_candidates = sorted(REQUIRED_CANDIDATES - candidates)
    if missing_candidates:
        failures.append(f"missing candidates: {missing_candidates}")

    missing_decisions = sorted(ALLOWED_DECISIONS - decisions)
    if missing_decisions:
        failures.append(f"missing decisions: {missing_decisions}")

    if not selected_layers:
        failures.append("at least one candidate must be selected")
    if not ({"unicode_cleanup", "locale_normalization"} & selected_layers):
        failures.append("at least one low-risk cleanup or locale helper must be selected")

    return failures


def validate_doc_mentions(review: list[dict[str, Any]]) -> list[str]:
    text = DOC_PATH.read_text(encoding="utf-8")
    failures: list[str] = []
    for item in review:
        if item["candidate"] not in text:
            failures.append(f"doc missing candidate {item['candidate']}")
        if item["decision"] not in text:
            failures.append(f"doc missing decision {item['decision']}")
    forbidden_claims = (
        "certified provider",
        "provider is certified",
        "install with",
        "download model",
    )
    for claim in forbidden_claims:
        if claim in text.lower():
            failures.append(f"doc contains forbidden claim: {claim}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is supported")

    review = load_review()
    failures = validate_no_side_effect_surface()
    failures.extend(validate_review(review))
    failures.extend(validate_doc_mentions(review))

    status = "FAIL" if failures else "PASS"
    print(
        json.dumps(
            {
                "status": status,
                "version": VERSION,
                "review": str(REVIEW_PATH.relative_to(ROOT)),
                "checked_candidates": len(review),
                "failures": failures,
            },
            indent=2,
        )
    )
    print(f"[tes-tts-provider-candidate-review] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
