#!/usr/bin/env python3
"""Self-test instruction-level TES TTS normalization without providers."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "benchmarks/tes-tts/instruction-normalizer-fixtures.json"
NORMALIZATION_FIXTURE_PATH = ROOT / "benchmarks/tes-tts/normalization-fixtures.json"
VERSION = "0.3.147"

SECRET_PATTERN = re.compile(r"\b(?:api_key|token|password)=([A-Za-z0-9_./:-]+)")
REDACTION_TOKEN = "[REDACTED_SECRET]"
REQUIRED_CACHE_KEYS = {
    "source_span",
    "detected_language",
    "target_language",
    "normalized_text",
    "preserved_terms",
    "pronunciation_hints",
    "redactions",
}
FIRST_CLASS_LANGUAGES = {"pt-BR", "en", "es", "fr", "it", "de", "he"}
LETTER_SPELLED_TERMS = {"ADR", "MCP", "API", "SDK", "CLI"}
COMMON_LOCAL_PRONUNCIATION_TERMS = {"JSON", "YAML", "SQL"}
FORBIDDEN_HINT_CLAIMS = {
    "ipa",
    "ssml",
    "phoneme",
    "phonetic",
    "provider",
    "translate",
    "translation",
}


@dataclass(frozen=True)
class PreparedSpeech:
    cache: list[dict[str, Any]]
    speech_text: str
    translation_plan: dict[str, Any]
    pronunciation_plan: dict[str, Any]


def load_fixtures() -> list[dict[str, Any]]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def load_normalization_fixtures() -> list[dict[str, Any]]:
    return json.loads(NORMALIZATION_FIXTURE_PATH.read_text(encoding="utf-8"))


def redact_secret_like_values(text: str) -> tuple[str, list[str]]:
    redactions: list[str] = []

    def replace(match: re.Match[str]) -> str:
        redactions.append(match.group(0))
        return match.group(0).split("=", 1)[0] + "=" + REDACTION_TOKEN

    return SECRET_PATTERN.sub(replace, text), redactions


def chunk_without_summary(text: str, max_chars: int) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) > max_chars and current:
            chunks.append(current)
            current = word
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def clean_markdown_for_speech(text: str) -> str:
    cleaned = text
    cleaned = re.sub(r"```[A-Za-z0-9_-]*\n?", "", cleaned)
    cleaned = cleaned.replace("```", "")
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"\1 \2", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 \2", cleaned)
    cleaned = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", cleaned)
    cleaned = re.sub(r"(?m)^\s*[-*+]\s+", "", cleaned)
    cleaned = re.sub(r"(?m)^\s*\d+[.)]\s+", "", cleaned)
    cleaned = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def pronunciation_hint(term: str) -> str:
    if term in LETTER_SPELLED_TERMS:
        return f"{term} -> spell letters"
    if term == "SPEC":
        return "SPEC -> read as technical noun"
    if term in COMMON_LOCAL_PRONUNCIATION_TERMS:
        return f"{term} -> common local pronunciation"
    if "/" in term:
        return f"{term} -> preserve path exactly"
    if " --" in term or term.startswith("tes "):
        return f"{term} -> preserve command exactly"
    return f"{term} -> preserve written identity"


def pronunciation_hints(terms: list[str]) -> list[str]:
    return [pronunciation_hint(term) for term in terms]


def plan_optional_translation(
    fixture: dict[str, Any],
    redacted_text: str,
    protected_terms: list[str],
) -> dict[str, Any]:
    provider_state = fixture.get("translation_provider_state", "provider_not_available")
    language_pair_state = fixture.get("language_pair_state", "unknown")
    status = (
        "translation_ready"
        if provider_state == "provider_available" and language_pair_state == "available"
        else "normalization_degraded"
    )
    return {
        "mode": "speech_preparation_only",
        "status": status,
        "provider_state": provider_state,
        "language_pair_state": language_pair_state,
        "source_text_unchanged": fixture["source_text"],
        "redacted_text": redacted_text,
        "detected_language": fixture["detected_language"],
        "target_language": fixture["target_language"],
        "protected_terms": protected_terms,
        "actions": [
            "redaction_before_translation",
            "protected_terms_before_translation",
            "span_level_translation_only",
            "no_summary",
            "preserve_source_text",
        ],
    }


def plan_optional_pronunciation(
    fixture: dict[str, Any],
    protected_terms: list[str],
) -> dict[str, Any]:
    provider_state = fixture.get("pronunciation_provider_state", "provider_not_available")
    language_support_state = fixture.get("pronunciation_language_state", "unknown")
    status = "normalization_degraded"
    return {
        "mode": "instruction_hints_baseline",
        "status": status,
        "provider_state": provider_state,
        "language_support_state": language_support_state,
        "target_language": fixture["target_language"],
        "protected_terms": protected_terms,
        "emitted_outputs": ["instruction_level_hints"],
        "blocked_outputs": [
            "ipa",
            "ssml",
            "phoneme",
            "lexicon",
            "provider_backed_pronunciation",
        ],
        "hebrew_posture": "degraded" if fixture["target_language"] == "he" else "not_applicable",
    }


def select_target_language(selector: dict[str, str]) -> str:
    explicit = selector["explicit_user_language"]
    if explicit in FIRST_CLASS_LANGUAGES:
        return explicit

    declared = selector["declared_adapter_default"]
    if declared in FIRST_CLASS_LANGUAGES:
        return declared

    if selector["active_adapter"] == "cursor":
        codex_default = selector["codex_default"]
        if codex_default in FIRST_CLASS_LANGUAGES:
            return codex_default
        claude_default = selector["claude_default"]
        if claude_default in FIRST_CLASS_LANGUAGES:
            return claude_default

    request_language = selector["request_language"]
    if request_language in FIRST_CLASS_LANGUAGES:
        return request_language

    dominant_text_language = selector["dominant_text_language"]
    if dominant_text_language in FIRST_CLASS_LANGUAGES:
        return dominant_text_language

    return "preserve_original"


def prepare_instruction_level_speech(fixture: dict[str, Any]) -> PreparedSpeech:
    redacted_text, redactions = redact_secret_like_values(fixture["source_text"])
    cleaned_text = clean_markdown_for_speech(redacted_text)
    chunks = chunk_without_summary(cleaned_text, fixture["max_chunk_chars"])
    protected_terms = fixture["protected_terms"]
    translation_plan = plan_optional_translation(fixture, redacted_text, protected_terms)
    pronunciation_plan = plan_optional_pronunciation(fixture, protected_terms)
    cache = [
        {
            "source_span": chunk,
            "detected_language": fixture["detected_language"],
            "target_language": fixture["target_language"],
            "normalized_text": chunk,
            "preserved_terms": [term for term in protected_terms if term in chunk],
            "pronunciation_hints": pronunciation_hints([term for term in protected_terms if term in chunk]),
            "redactions": redactions,
        }
        for chunk in chunks
    ]
    return PreparedSpeech(
        cache=cache,
        speech_text=" ".join(entry["normalized_text"] for entry in cache),
        translation_plan=translation_plan,
        pronunciation_plan=pronunciation_plan,
    )


def validate_fixture_shape(fixture: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    required = {
        "id",
        "target_language",
        "detected_language",
        "source_text",
        "protected_terms",
        "expected_redactions",
        "forbidden_terms",
        "max_chunk_chars",
        "expected_min_chunks",
        "no_summary",
        "checks",
    }
    missing = sorted(required - set(fixture))
    if missing:
        failures.append(f"{fixture.get('id', '<unknown>')}: missing fields {missing}")
        return failures
    if fixture["no_summary"] is not True:
        failures.append(f"{fixture['id']}: no_summary must be true")
    if not fixture["source_text"]:
        failures.append(f"{fixture['id']}: source_text must be non-empty")
    if not isinstance(fixture["protected_terms"], list):
        failures.append(f"{fixture['id']}: protected_terms must be a list")
    if "expected_speech_contains" in fixture and not isinstance(
        fixture["expected_speech_contains"], list
    ):
        failures.append(f"{fixture['id']}: expected_speech_contains must be a list when present")
    if "expected_pronunciation_hints" in fixture and not isinstance(
        fixture["expected_pronunciation_hints"], list
    ):
        failures.append(f"{fixture['id']}: expected_pronunciation_hints must be a list when present")
    if "translation_boundary" in fixture["checks"]:
        for field in (
            "translation_provider_state",
            "language_pair_state",
            "expected_translation_status",
        ):
            if field not in fixture:
                failures.append(f"{fixture['id']}: {field} is required for translation_boundary")
    if "pronunciation_provider_boundary" in fixture["checks"]:
        for field in (
            "pronunciation_provider_state",
            "pronunciation_language_state",
            "expected_pronunciation_status",
        ):
            if field not in fixture:
                failures.append(
                    f"{fixture['id']}: {field} is required for pronunciation_provider_boundary"
                )
    return failures


def validate_prepared_fixture(fixture: dict[str, Any]) -> list[str]:
    failures: list[str] = validate_fixture_shape(fixture)
    if failures:
        return failures

    prepared = prepare_instruction_level_speech(fixture)
    fixture_id = fixture["id"]

    if len(prepared.cache) < fixture["expected_min_chunks"]:
        failures.append(
            f"{fixture_id}: expected at least {fixture['expected_min_chunks']} chunks, "
            f"got {len(prepared.cache)}"
        )

    for index, entry in enumerate(prepared.cache):
        missing_keys = sorted(REQUIRED_CACHE_KEYS - set(entry))
        if missing_keys:
            failures.append(f"{fixture_id}: cache[{index}] missing keys {missing_keys}")
        if len(entry["normalized_text"]) > fixture["max_chunk_chars"]:
            failures.append(f"{fixture_id}: cache[{index}] exceeds max_chunk_chars")
        if entry["target_language"] != fixture["target_language"]:
            failures.append(f"{fixture_id}: cache[{index}] target language drifted")

    for term in fixture["protected_terms"]:
        if term not in prepared.speech_text:
            failures.append(f"{fixture_id}: protected term {term} missing from speech text")

    for expected in fixture["expected_redactions"]:
        if not any(expected in entry["redactions"] for entry in prepared.cache):
            failures.append(f"{fixture_id}: expected redaction {expected} not recorded")
        if expected in prepared.speech_text:
            failures.append(f"{fixture_id}: secret-like value {expected} leaked to speech text")

    for forbidden in fixture["forbidden_terms"]:
        if forbidden in prepared.speech_text:
            failures.append(f"{fixture_id}: forbidden term {forbidden} leaked to speech text")

    for expected in fixture.get("expected_speech_contains", []):
        if expected not in prepared.speech_text:
            failures.append(f"{fixture_id}: expected speech text {expected!r} missing")

    actual_hints = [
        hint
        for entry in prepared.cache
        for hint in entry["pronunciation_hints"]
    ]
    for expected in fixture.get("expected_pronunciation_hints", []):
        if expected not in actual_hints:
            failures.append(f"{fixture_id}: expected pronunciation hint {expected!r} missing")

    if "pronunciation_hints" in fixture["checks"]:
        lowered_hints = " ".join(actual_hints).lower()
        leaked_claims = sorted(claim for claim in FORBIDDEN_HINT_CLAIMS if claim in lowered_hints)
        if leaked_claims:
            failures.append(f"{fixture_id}: pronunciation hints contain forbidden claims {leaked_claims}")
        for term in fixture["protected_terms"]:
            if term not in prepared.speech_text:
                failures.append(f"{fixture_id}: pronunciation hint changed visible term {term}")

    if "markdown_cleanup" in fixture["checks"]:
        markdown_markers = ["```", "[", "](", "##", "`"]
        leaked = [marker for marker in markdown_markers if marker in prepared.speech_text]
        if leaked:
            failures.append(f"{fixture_id}: markdown markers leaked to speech text {leaked}")

    if "translation_boundary" in fixture["checks"]:
        plan = prepared.translation_plan
        if plan["mode"] != "speech_preparation_only":
            failures.append(f"{fixture_id}: translation mode must be speech_preparation_only")
        if plan["status"] != fixture["expected_translation_status"]:
            failures.append(
                f"{fixture_id}: expected translation status {fixture['expected_translation_status']}, "
                f"got {plan['status']}"
            )
        if plan["source_text_unchanged"] != fixture["source_text"]:
            failures.append(f"{fixture_id}: source text changed during translation planning")
        required_actions = {
            "redaction_before_translation",
            "protected_terms_before_translation",
            "span_level_translation_only",
            "no_summary",
            "preserve_source_text",
        }
        missing_actions = sorted(required_actions - set(plan["actions"]))
        if missing_actions:
            failures.append(f"{fixture_id}: translation plan missing actions {missing_actions}")
        for expected in fixture["expected_redactions"]:
            if expected in plan["redacted_text"]:
                failures.append(f"{fixture_id}: translation plan kept unredacted secret {expected}")
        for term in fixture["protected_terms"]:
            if term not in plan["protected_terms"]:
                failures.append(f"{fixture_id}: translation plan lost protected term {term}")
        if plan["status"] == "normalization_degraded" and plan["redacted_text"] != redact_secret_like_values(
            fixture["source_text"]
        )[0]:
            failures.append(f"{fixture_id}: degraded translation plan must preserve redacted source text")

    if "pronunciation_provider_boundary" in fixture["checks"]:
        plan = prepared.pronunciation_plan
        if plan["mode"] != "instruction_hints_baseline":
            failures.append(f"{fixture_id}: pronunciation mode must keep instruction hints as baseline")
        if plan["status"] != fixture["expected_pronunciation_status"]:
            failures.append(
                f"{fixture_id}: expected pronunciation status {fixture['expected_pronunciation_status']}, "
                f"got {plan['status']}"
            )
        if plan["emitted_outputs"] != ["instruction_level_hints"]:
            failures.append(f"{fixture_id}: pronunciation plan must emit only instruction-level hints")
        forbidden_outputs = {"ipa", "ssml", "phoneme", "lexicon", "provider_backed_pronunciation"}
        missing_blocked = sorted(forbidden_outputs - set(plan["blocked_outputs"]))
        if missing_blocked:
            failures.append(f"{fixture_id}: pronunciation plan missing blocked outputs {missing_blocked}")
        for term in fixture["protected_terms"]:
            if term not in plan["protected_terms"]:
                failures.append(f"{fixture_id}: pronunciation plan lost protected term {term}")
        if fixture["target_language"] == "he" and plan["hebrew_posture"] != "degraded":
            failures.append(f"{fixture_id}: Hebrew pronunciation posture must remain degraded")

    if "no_summary" in fixture["checks"]:
        source_terms = set(clean_markdown_for_speech(redact_secret_like_values(fixture["source_text"])[0]).split())
        speech_terms = set(prepared.speech_text.split())
        missing_terms = sorted(source_terms - speech_terms)
        if missing_terms:
            failures.append(f"{fixture_id}: speech text dropped terms {missing_terms}")

    return failures


def validate_selector_corpus() -> list[str]:
    failures: list[str] = []
    for fixture in load_normalization_fixtures():
        fixture_id = fixture.get("id", "<unknown>")
        selector = fixture.get("selector")
        if not isinstance(selector, dict):
            failures.append(f"{fixture_id}: missing selector object")
            continue
        selected = select_target_language(selector)
        expected = fixture.get("expected_target_language")
        if selected != expected:
            failures.append(f"{fixture_id}: selector selected {selected}, expected {expected}")
    return failures


def validate_translation_boundary_fixtures(fixtures: list[dict[str, Any]]) -> list[str]:
    required = {
        "tts-translation-redaction-first",
        "tts-translation-protected-terms-first",
        "tts-translation-unclear-pair-degraded",
    }
    seen = {fixture["id"] for fixture in fixtures if "translation_boundary" in fixture["checks"]}
    missing = sorted(required - seen)
    if missing:
        return [f"missing translation boundary fixtures: {missing}"]
    return []


def validate_pronunciation_boundary_fixtures(fixtures: list[dict[str, Any]]) -> list[str]:
    required = {
        "tts-pronunciation-provider-boundary",
        "tts-pronunciation-hebrew-degraded",
        "tts-pronunciation-provider-unclear-degraded",
    }
    seen = {
        fixture["id"]
        for fixture in fixtures
        if "pronunciation_provider_boundary" in fixture["checks"]
    }
    missing = sorted(required - seen)
    if missing:
        return [f"missing pronunciation boundary fixtures: {missing}"]
    return []


def validate_no_disk_write_surface() -> list[str]:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    failures: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Attribute) and function.attr in {"write_text", "write_bytes"}:
            failures.append(f"oracle contains disk write call: {function.attr}")
        if isinstance(function, ast.Name) and function.id in {"open", "NamedTemporaryFile", "mkstemp"}:
            failures.append(f"oracle contains disk write surface call: {function.id}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is supported")

    failures = validate_no_disk_write_surface()
    failures.extend(validate_selector_corpus())
    fixtures = load_fixtures()
    failures.extend(validate_translation_boundary_fixtures(fixtures))
    failures.extend(validate_pronunciation_boundary_fixtures(fixtures))
    for fixture in fixtures:
        failures.extend(validate_prepared_fixture(fixture))

    status = "FAIL" if failures else "PASS"
    print(
        json.dumps(
            {
                "status": status,
                "version": VERSION,
                "fixtures": str(FIXTURE_PATH.relative_to(ROOT)),
                "checked_fixtures": len(fixtures),
                "failures": failures,
            },
            indent=2,
        )
    )
    print(f"[tes-tts-instruction-normalizer] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
