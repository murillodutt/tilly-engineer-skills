#!/usr/bin/env python3
"""Validate migrated TES TTS pronunciation catalog fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "benchmarks/tes-tts/pronunciation-catalog-fixtures.json"
VERSION = "0.3.150"
REQUIRED_ENTRY_KEYS = {
    "id",
    "term",
    "class",
    "default_language",
    "spoken_rendering",
    "preserve_written_identity",
    "exact_request_behavior",
    "runtime_claim",
}
REQUIRED_CLASSES = {"acronym", "technical_noun", "proper_noun", "url", "path", "command"}
FORBIDDEN_RUNTIME_CLAIMS = {"ipa", "phoneme", "ssml", "provider_backed", "g2p"}


def load_fixtures() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def validate_catalog(catalog: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if catalog.get("version") != VERSION:
        failures.append("catalog version drifted")
    if catalog.get("usage") != "evidence_only":
        failures.append("catalog usage must remain evidence_only")
    if catalog.get("runtime_output") is not False:
        failures.append("catalog must not claim runtime output")
    if not str(catalog.get("source_reference", "")).endswith("#technical-term-handling"):
        failures.append("catalog must preserve source reference to the Markdown guidance")

    entries = catalog.get("entries")
    if not isinstance(entries, list) or len(entries) < 7:
        failures.append("catalog must include at least seven representative entries")
        return failures

    ids: set[str] = set()
    classes: set[str] = set()
    terms: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            failures.append("catalog entry must be an object")
            continue
        if set(entry) != REQUIRED_ENTRY_KEYS:
            failures.append(f"{entry.get('id', '<missing-id>')}: entry fields drifted")
            continue
        if entry["id"] in ids:
            failures.append(f"{entry['id']}: duplicate id")
        ids.add(entry["id"])
        classes.add(entry["class"])
        terms[entry["term"]] = entry
        if entry["default_language"] != "pt-BR":
            failures.append(f"{entry['id']}: default_language must remain pt-BR")
        if not entry["term"] or not entry["spoken_rendering"]:
            failures.append(f"{entry['id']}: term and spoken_rendering must be non-empty")
        if entry["exact_request_behavior"] != "preserve_raw":
            failures.append(f"{entry['id']}: exact requests must preserve raw text")
        if entry["runtime_claim"] != "none":
            failures.append(f"{entry['id']}: runtime_claim must remain none")
        lower_rendering = str(entry["spoken_rendering"]).lower()
        if any(claim in lower_rendering for claim in FORBIDDEN_RUNTIME_CLAIMS):
            failures.append(f"{entry['id']}: spoken rendering leaks a forbidden runtime claim")

    missing_classes = REQUIRED_CLASSES - classes
    if missing_classes:
        failures.append(f"catalog missing representative classes: {sorted(missing_classes)}")

    expected_renderings = {
        "ADR": "A D R",
        "MCP": "M C P",
        "SPEC": "spec",
        "https://github.com/example/project": "pagina do GitHub",
        ".agents/skills/tes-tts": "pasta tes tts",
        "tes tts --voice default": "tes tts --voice default",
    }
    for term, expected in expected_renderings.items():
        if term not in terms:
            failures.append(f"catalog missing migrated term {term}")
            continue
        if terms[term]["spoken_rendering"] != expected:
            failures.append(f"{term}: spoken rendering drifted")

    if terms.get("GitHub", {}).get("preserve_written_identity") is not True:
        failures.append("GitHub must preserve written identity as a proper noun")
    if terms.get("https://github.com/example/project", {}).get("preserve_written_identity") is not False:
        failures.append("GitHub URL non-exact rendering should use destination phrase")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is supported")

    failures = validate_catalog(load_fixtures())
    status = "FAIL" if failures else "PASS"
    print(
        json.dumps(
            {
                "status": status,
                "version": VERSION,
                "fixtures": str(FIXTURE_PATH.relative_to(ROOT)),
                "failures": failures,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    print(f"[tes-tts-pronunciation-catalog] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
