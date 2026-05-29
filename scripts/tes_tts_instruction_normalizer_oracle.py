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


@dataclass(frozen=True)
class PreparedSpeech:
    cache: list[dict[str, Any]]
    speech_text: str


def load_fixtures() -> list[dict[str, Any]]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


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


def pronunciation_hints(terms: list[str]) -> list[str]:
    return [term for term in terms if term.isupper() and len(term) > 1]


def prepare_instruction_level_speech(fixture: dict[str, Any]) -> PreparedSpeech:
    redacted_text, redactions = redact_secret_like_values(fixture["source_text"])
    chunks = chunk_without_summary(redacted_text, fixture["max_chunk_chars"])
    protected_terms = fixture["protected_terms"]
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
    return PreparedSpeech(cache=cache, speech_text=" ".join(entry["normalized_text"] for entry in cache))


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

    if "no_summary" in fixture["checks"]:
        source_terms = set(redact_secret_like_values(fixture["source_text"])[0].split())
        speech_terms = set(prepared.speech_text.split())
        missing_terms = sorted(source_terms - speech_terms)
        if missing_terms:
            failures.append(f"{fixture_id}: speech text dropped terms {missing_terms}")

    return failures


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
    fixtures = load_fixtures()
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
