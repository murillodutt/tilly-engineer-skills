#!/usr/bin/env python3
"""Validate the TES TTS fixture schema contract without loading a corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "benchmarks/tes-tts/normalization-fixture.schema.json"
VERSION = "0.3.147"

REQUIRED_FIELDS = {
    "id",
    "class",
    "selector",
    "source_text",
    "expected_target_language",
    "protected_terms",
    "redaction",
    "provider_state",
    "expected_status",
    "no_summary",
}

FIRST_CLASS_LANGUAGES = {"pt-BR", "en", "es", "fr", "it", "de", "he"}
PROVIDER_STATES = {
    "provider_available",
    "provider_not_available",
    "provider_needs_review",
    "normalization_degraded",
    "tts_not_available",
}
EXPECTED_STATUSES = {"PASS", "DEGRADED", "NEEDS_REVIEW", "BLOCKED"}


def enum_at(schema: dict[str, Any], *path: str) -> set[str]:
    node: Any = schema
    for key in path:
        node = node[key]
    return set(node["enum"])


def validate_schema(schema: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    required = set(schema.get("required", []))
    properties = set(schema.get("properties", {}).keys())

    missing_required = sorted(REQUIRED_FIELDS - required)
    if missing_required:
        failures.append(f"missing required fields: {missing_required}")

    missing_properties = sorted(REQUIRED_FIELDS - properties)
    if missing_properties:
        failures.append(f"missing properties: {missing_properties}")

    if schema.get("additionalProperties") is not False:
        failures.append("top-level additionalProperties must be false")

    selector = schema.get("properties", {}).get("selector", {})
    selector_required = set(selector.get("required", []))
    expected_selector = {
        "explicit_user_language",
        "declared_adapter_default",
        "request_language",
        "dominant_text_language",
    }
    if selector_required != expected_selector:
        failures.append(
            "selector required fields mismatch: "
            f"expected {sorted(expected_selector)}, got {sorted(selector_required)}"
        )

    languages = enum_at(schema, "$defs", "language")
    if languages != FIRST_CLASS_LANGUAGES:
        failures.append(
            "first-class language enum mismatch: "
            f"expected {sorted(FIRST_CLASS_LANGUAGES)}, got {sorted(languages)}"
        )

    target_languages = enum_at(schema, "$defs", "target_language")
    expected_targets = FIRST_CLASS_LANGUAGES | {"preserve_original"}
    if target_languages != expected_targets:
        failures.append(
            "target language enum mismatch: "
            f"expected {sorted(expected_targets)}, got {sorted(target_languages)}"
        )

    provider_states = enum_at(schema, "$defs", "provider_state")
    if provider_states != PROVIDER_STATES:
        failures.append(
            "provider state enum mismatch: "
            f"expected {sorted(PROVIDER_STATES)}, got {sorted(provider_states)}"
        )

    expected_statuses = enum_at(schema, "$defs", "expected_status")
    if expected_statuses != EXPECTED_STATUSES:
        failures.append(
            "expected status enum mismatch: "
            f"expected {sorted(EXPECTED_STATUSES)}, got {sorted(expected_statuses)}"
        )

    no_summary = schema.get("properties", {}).get("no_summary", {})
    if no_summary.get("const") is not True:
        failures.append("no_summary must be const true")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if not args.self_test:
        parser.error("only --self-test is supported")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    failures = validate_schema(schema)
    status = "FAIL" if failures else "PASS"
    print(
        json.dumps(
            {
                "status": status,
                "version": VERSION,
                "schema": str(SCHEMA_PATH.relative_to(ROOT)),
                "failures": failures,
            },
            indent=2,
        )
    )
    print(f"[tes-tts-fixture-schema] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
