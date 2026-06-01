#!/usr/bin/env python3
"""Validate the TES TTS fixture schema contract and dependency-free corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "benchmarks/tes-tts/normalization-fixture.schema.json"
CORPUS_PATH = ROOT / "benchmarks/tes-tts/normalization-fixtures.json"
VERSION = "0.3.150"

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
FIXTURE_CLASSES = {
    "default_language_selector",
    "language_normalization",
    "protected_terms",
    "redaction",
    "markdown_transform",
    "provider_fallback",
    "pronunciation_hint",
}
PROTECTED_TERM_KINDS = {
    "acronym",
    "technical_term",
    "proper_noun",
    "command",
    "path",
    "code_identifier",
    "model_name",
    "package_name",
}
REQUIRED_DLS_TARGETS = {
    "tts-dls-001": "en",
    "tts-dls-002": "pt-BR",
    "tts-dls-003": "pt-BR",
    "tts-dls-004": "de",
    "tts-dls-005": "preserve_original",
    "tts-dls-006": "pt-BR",
}
REQUIRED_LANGUAGE_FIXTURES = {
    "tts-lang-pt-br": "pt-BR",
    "tts-lang-en": "en",
    "tts-lang-es": "es",
    "tts-lang-fr": "fr",
    "tts-lang-it": "it",
    "tts-lang-de": "de",
    "tts-lang-he": "he",
}
REQUIRED_NEGATIVE_FIXTURES = {
    "tts-negative-markdown": {
        "class": "markdown_transform",
        "contains": ["##", "- ", "`MCP`"],
    },
    "tts-negative-url": {
        "class": "markdown_transform",
        "contains": ["https://", "ADR-0004"],
    },
    "tts-negative-path": {
        "class": "markdown_transform",
        "contains": ["/Users/example/project/docs/SPEC.md"],
    },
    "tts-negative-code-fence": {
        "class": "markdown_transform",
        "contains": ["```bash", "tes tts --voice default"],
    },
    "tts-negative-long-hash": {
        "class": "protected_terms",
        "contains": ["4f9c2a8b7d6e5f40123456789abcdef0123456789abcdef0123456789abcdef0"],
    },
    "tts-negative-secret-redaction": {
        "class": "redaction",
        "contains": ["OPENAI_API_KEY", "sk-proj-example1234567890"],
    },
    "tts-negative-provider-unavailable": {
        "class": "provider_fallback",
        "provider_state": "provider_not_available",
        "expected_status": "DEGRADED",
    },
    "tts-negative-voice-unavailable": {
        "class": "provider_fallback",
        "provider_state": "tts_not_available",
        "expected_status": "DEGRADED",
    },
    "tts-negative-hebrew-degraded": {
        "class": "pronunciation_hint",
        "provider_state": "normalization_degraded",
        "expected_status": "DEGRADED",
        "expected_target_language": "he",
        "contains": ["בלי ניקוד"],
    },
}
ADAPTERS = {"codex", "claude", "cursor", "unknown"}
SELECTOR_FIELDS = {
    "active_adapter",
    "explicit_user_language",
    "declared_adapter_default",
    "codex_default",
    "claude_default",
    "request_language",
    "dominant_text_language",
}


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
    expected_selector = SELECTOR_FIELDS
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


def fail(failures: list[str], fixture_id: str, message: str) -> None:
    failures.append(f"{fixture_id}: {message}")


def validate_selector(fixture: dict[str, Any], failures: list[str]) -> None:
    fixture_id = str(fixture.get("id", "<unknown>"))
    selector = fixture.get("selector")
    if not isinstance(selector, dict):
        fail(failures, fixture_id, "selector must be an object")
        return
    if set(selector) != SELECTOR_FIELDS:
        fail(failures, fixture_id, f"selector keys mismatch: {sorted(selector)}")
        return
    if selector["active_adapter"] not in ADAPTERS:
        fail(failures, fixture_id, "active_adapter has invalid value")
    if selector["explicit_user_language"] not in FIRST_CLASS_LANGUAGES | {"absent"}:
        fail(failures, fixture_id, "explicit_user_language has invalid value")
    for key in ("declared_adapter_default", "codex_default", "claude_default"):
        if selector[key] not in FIRST_CLASS_LANGUAGES | {"unknown"}:
            fail(failures, fixture_id, f"{key} has invalid value")
    for key in ("request_language", "dominant_text_language"):
        if selector[key] not in FIRST_CLASS_LANGUAGES | {"unclear"}:
            fail(failures, fixture_id, f"{key} has invalid value")


def validate_protected_terms(fixture: dict[str, Any], failures: list[str]) -> None:
    fixture_id = str(fixture.get("id", "<unknown>"))
    terms = fixture.get("protected_terms")
    if not isinstance(terms, list):
        fail(failures, fixture_id, "protected_terms must be an array")
        return
    for index, term in enumerate(terms):
        if not isinstance(term, dict):
            fail(failures, fixture_id, f"protected_terms[{index}] must be an object")
            continue
        if not isinstance(term.get("term"), str) or not term["term"]:
            fail(failures, fixture_id, f"protected_terms[{index}].term must be non-empty")
        if term.get("kind") not in PROTECTED_TERM_KINDS:
            fail(failures, fixture_id, f"protected_terms[{index}].kind has invalid value")
        if term.get("must_preserve") is not True:
            fail(failures, fixture_id, f"protected_terms[{index}].must_preserve must be true")


def validate_redaction(fixture: dict[str, Any], failures: list[str]) -> None:
    fixture_id = str(fixture.get("id", "<unknown>"))
    redaction = fixture.get("redaction")
    if not isinstance(redaction, dict):
        fail(failures, fixture_id, "redaction must be an object")
        return
    if set(redaction) != {"contains_secret_like_value", "expected_redactions"}:
        fail(failures, fixture_id, f"redaction keys mismatch: {sorted(redaction)}")
    if not isinstance(redaction.get("contains_secret_like_value"), bool):
        fail(failures, fixture_id, "contains_secret_like_value must be boolean")
    if not isinstance(redaction.get("expected_redactions"), list):
        fail(failures, fixture_id, "expected_redactions must be an array")


def validate_fixture(fixture: Any) -> list[str]:
    failures: list[str] = []
    if not isinstance(fixture, dict):
        return ["fixture entry must be an object"]

    fixture_id = str(fixture.get("id", "<unknown>"))
    unknown_keys = sorted(set(fixture) - (REQUIRED_FIELDS | {"notes"}))
    missing_keys = sorted(REQUIRED_FIELDS - set(fixture))
    if unknown_keys:
        fail(failures, fixture_id, f"unknown fields: {unknown_keys}")
    if missing_keys:
        fail(failures, fixture_id, f"missing required fields: {missing_keys}")
        return failures

    if not isinstance(fixture["id"], str) or not fixture["id"].startswith("tts-"):
        fail(failures, fixture_id, "id must start with tts-")
    if fixture["class"] not in FIXTURE_CLASSES:
        fail(failures, fixture_id, "class has invalid value")
    if not isinstance(fixture["source_text"], str) or not fixture["source_text"]:
        fail(failures, fixture_id, "source_text must be non-empty")
    if fixture["expected_target_language"] not in FIRST_CLASS_LANGUAGES | {"preserve_original"}:
        fail(failures, fixture_id, "expected_target_language has invalid value")
    if fixture["provider_state"] not in PROVIDER_STATES:
        fail(failures, fixture_id, "provider_state has invalid value")
    if fixture["expected_status"] not in EXPECTED_STATUSES:
        fail(failures, fixture_id, "expected_status has invalid value")
    if fixture["no_summary"] is not True:
        fail(failures, fixture_id, "no_summary must be true")

    validate_selector(fixture, failures)
    validate_protected_terms(fixture, failures)
    validate_redaction(fixture, failures)
    return failures


def validate_corpus(corpus: Any) -> list[str]:
    failures: list[str] = []
    if not isinstance(corpus, list):
        return ["corpus root must be an array"]

    seen_ids: set[str] = set()
    for fixture in corpus:
        fixture_id = fixture.get("id", "<unknown>") if isinstance(fixture, dict) else "<unknown>"
        if fixture_id in seen_ids:
            fail(failures, str(fixture_id), "duplicate fixture id")
        seen_ids.add(str(fixture_id))
        failures.extend(validate_fixture(fixture))

    missing_dls = sorted(set(REQUIRED_DLS_TARGETS) - seen_ids)
    if missing_dls:
        failures.append(f"missing required DLS fixtures: {missing_dls}")

    by_id = {fixture.get("id"): fixture for fixture in corpus if isinstance(fixture, dict)}
    for fixture_id, expected_target in REQUIRED_DLS_TARGETS.items():
        fixture = by_id.get(fixture_id)
        if not fixture:
            continue
        if fixture.get("class") != "default_language_selector":
            fail(failures, fixture_id, "DLS fixture class must be default_language_selector")
        if fixture.get("expected_target_language") != expected_target:
            fail(
                failures,
                fixture_id,
                f"expected target {expected_target}, got {fixture.get('expected_target_language')}",
            )

    missing_language = sorted(set(REQUIRED_LANGUAGE_FIXTURES) - seen_ids)
    if missing_language:
        failures.append(f"missing required language fixtures: {missing_language}")

    for fixture_id, expected_target in REQUIRED_LANGUAGE_FIXTURES.items():
        fixture = by_id.get(fixture_id)
        if not fixture:
            continue
        if fixture.get("class") != "language_normalization":
            fail(failures, fixture_id, "language fixture class must be language_normalization")
        if fixture.get("expected_target_language") != expected_target:
            fail(
                failures,
                fixture_id,
                f"expected language target {expected_target}, got {fixture.get('expected_target_language')}",
            )

    missing_negative = sorted(set(REQUIRED_NEGATIVE_FIXTURES) - seen_ids)
    if missing_negative:
        failures.append(f"missing required negative fixtures: {missing_negative}")

    for fixture_id, expectations in REQUIRED_NEGATIVE_FIXTURES.items():
        fixture = by_id.get(fixture_id)
        if not fixture:
            continue
        expected_class = expectations.get("class")
        if fixture.get("class") != expected_class:
            fail(failures, fixture_id, f"expected class {expected_class}, got {fixture.get('class')}")
        for key in ("provider_state", "expected_status", "expected_target_language"):
            if key in expectations and fixture.get(key) != expectations[key]:
                fail(failures, fixture_id, f"expected {key} {expectations[key]}, got {fixture.get(key)}")
        source_text = str(fixture.get("source_text", ""))
        for needle in expectations.get("contains", []):
            if needle not in source_text:
                fail(failures, fixture_id, f"source_text must contain {needle!r}")
        if fixture_id == "tts-negative-secret-redaction":
            redactions = fixture.get("redaction", {}).get("expected_redactions", [])
            if "sk-proj-example1234567890" not in redactions:
                fail(failures, fixture_id, "secret-like value must be listed in expected_redactions")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if not args.self_test:
        parser.error("only --self-test is supported")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    failures = validate_schema(schema)
    failures.extend(validate_corpus(corpus))
    status = "FAIL" if failures else "PASS"
    print(
        json.dumps(
            {
                "status": status,
                "version": VERSION,
                "schema": str(SCHEMA_PATH.relative_to(ROOT)),
                "corpus": str(CORPUS_PATH.relative_to(ROOT)),
                "failures": failures,
            },
            indent=2,
        )
    )
    print(f"[tes-tts-fixture-schema] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
