#!/usr/bin/env python3
"""Validate dependency-free hot-path span matching for TES TTS."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any

import tes_tts_runtime


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "benchmarks/tes-tts/hot-path-span-matcher-fixtures.json"
VERSION = "0.3.150"

INLINE_CODE_PATTERN = re.compile(r"`([^`]+)`")
URL_PATTERN = re.compile(r"https?://[^\s),;]+")
PATH_PATTERN = re.compile(
    r"(?<!\w)(?:\.{1,2}/|\.[A-Za-z0-9_-]+/|/)"
    r"[A-Za-z0-9._~@%+:-]+(?:/[A-Za-z0-9._~@%+:-]+)*"
)
HASH_PATTERN = re.compile(r"\b[0-9a-fA-F]{16,}\b")
REDACTED_SECRET_PATTERN = re.compile(re.escape(tes_tts_runtime.REDACTION_TOKEN))
EXACT_MARKERS = ("exatamente", "literalmente", "exact", "literal", "verbatim", "raw")


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    kind: str
    text: str
    rendering: str
    source: str
    priority: int
    executable: bool = False


def load_fixtures() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def overlaps(span: Span, accepted: list[Span]) -> bool:
    return any(span.start < existing.end and existing.start < span.end for existing in accepted)


def has_exact_marker_before(text: str, start: int) -> bool:
    prefix = text[max(0, start - 40) : start].casefold()
    return any(marker in prefix for marker in EXACT_MARKERS)


def literal_spans(redacted_text: str) -> list[Span]:
    spans: list[Span] = []
    for match in REDACTED_SECRET_PATTERN.finditer(redacted_text):
        spans.append(
            Span(
                start=match.start(),
                end=match.end(),
                kind="secret",
                text=match.group(0),
                rendering=match.group(0),
                source="redaction",
                priority=1000,
            )
        )
    for match in INLINE_CODE_PATTERN.finditer(redacted_text):
        content = match.group(1)
        kind = "exact_island" if has_exact_marker_before(redacted_text, match.start()) else "code"
        spans.append(
            Span(
                start=match.start(),
                end=match.end(),
                kind=kind,
                text=content,
                rendering=content,
                source="inline_code",
                priority=900 if kind == "exact_island" else 850,
            )
        )
    for match in URL_PATTERN.finditer(redacted_text):
        spans.append(
            Span(
                start=match.start(),
                end=match.end(),
                kind="url",
                text=match.group(0),
                rendering="pagina do GitHub" if "github.com" in match.group(0).casefold() else "endereco web",
                source="url_regex",
                priority=800,
            )
        )
    for match in PATH_PATTERN.finditer(redacted_text):
        text = match.group(0).rstrip(".,;")
        spans.append(
            Span(
                start=match.start(),
                end=match.start() + len(text),
                kind="path",
                text=text,
                rendering="pasta tes tts" if text.endswith("tes-tts") else text,
                source="path_regex",
                priority=780,
            )
        )
    for match in HASH_PATTERN.finditer(redacted_text):
        spans.append(
            Span(
                start=match.start(),
                end=match.end(),
                kind="hash",
                text=match.group(0),
                rendering=match.group(0),
                source="hash_regex",
                priority=700,
            )
        )
    return spans


def protected_spans(redacted_text: str, locale: str, index: dict[str, Any]) -> list[Span]:
    spans: list[Span] = []
    entries = list(index["phrase"].get(locale, []))
    entries.extend(index["exact"].get(locale, {}).values())
    entries.sort(key=lambda entry: (-entry.priority, -len(entry.term), entry.insertion_order))
    for entry in entries:
        if not entry.spoken_rendering:
            continue
        escaped = re.escape(entry.term)
        pattern = re.compile(rf"(?<![\w/-]){escaped}(?![\w/-])", re.IGNORECASE)
        for match in pattern.finditer(redacted_text):
            if redacted_text[match.end() :].startswith("=" + normalizer.REDACTION_TOKEN):
                continue
            kind = "command" if entry.source == "pronunciation_catalog" and " --" in entry.term else (
                "protected_phrase" if entry.match_scope == "phrase" else "protected_term"
            )
            match_priority = entry.priority + (250 if kind == "protected_phrase" else 0)
            spans.append(
                Span(
                    start=match.start(),
                    end=match.end(),
                    kind=kind,
                    text=match.group(0),
                    rendering=entry.spoken_rendering,
                    source=entry.source,
                    priority=match_priority,
                )
            )
    return spans


def match_hot_path_spans(source_text: str, locale: str) -> dict[str, Any]:
    runtime_result = tes_tts_runtime.match_spans(source_text, locale)
    runtime_spans = runtime_result["spans"]
    return {
        "redacted_text": runtime_result["redacted_text"],
        "source_text_immutable": True,
        "provider_timing": "out_of_scope",
        "runtime_output": False,
        "command_execution": "not_performed",
        "redaction_count": runtime_result["redaction_count"],
        "spans": [
            {
                "start": span.start,
                "end": span.end,
                "kind": span.kind,
                "text": span.text,
                "rendering": span.rendering,
                "source": span.source,
                "executable": span.executable,
            }
            for span in runtime_spans
        ],
    }


def validate_fixture_shape(fixtures: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if fixtures.get("version") != VERSION:
        failures.append("fixture version drifted")
    if fixtures.get("usage") != "hot_path_span_matcher_contract":
        failures.append("fixture usage must be hot_path_span_matcher_contract")
    if fixtures.get("runtime_output") is not False:
        failures.append("matcher fixture must not claim runtime output")
    if fixtures.get("provider_timing") != "out_of_scope":
        failures.append("provider timing must remain out_of_scope")
    cases = fixtures.get("cases")
    if not isinstance(cases, list) or len(cases) < 5:
        failures.append("matcher fixtures must include at least five cases")
        return failures
    required = {
        "id",
        "source_text",
        "locale",
        "expected_order",
        "expected_spans",
        "expected_absent_text",
        "expected_redaction_count",
    }
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            failures.append("case must be an object")
            continue
        if set(case) != required:
            failures.append(f"{case.get('id', '<missing-id>')}: case fields drifted")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            failures.append("case id is required")
        elif case_id in seen:
            failures.append(f"{case_id}: duplicate case id")
        else:
            seen.add(case_id)
    return failures


def validate_case(case: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    failures: list[str] = []
    result = match_hot_path_spans(case["source_text"], case["locale"])
    observed_spans = result["spans"]
    observed_order = [span["kind"] for span in observed_spans]
    expected_order = case["expected_order"]
    if observed_order != expected_order:
        failures.append(f"{case['id']}: expected order {expected_order}, got {observed_order}")

    expected_spans = case["expected_spans"]
    if len(observed_spans) != len(expected_spans):
        failures.append(f"{case['id']}: expected {len(expected_spans)} spans, got {len(observed_spans)}")
    for expected, observed in zip(expected_spans, observed_spans):
        for key in ("kind", "text", "rendering"):
            if observed.get(key) != expected.get(key):
                failures.append(f"{case['id']}: expected {key}={expected.get(key)!r}, got {observed.get(key)!r}")

    if result["redaction_count"] != case["expected_redaction_count"]:
        failures.append(f"{case['id']}: redaction count drifted")
    if not result["source_text_immutable"]:
        failures.append(f"{case['id']}: source text was mutated")
    if result["provider_timing"] != "out_of_scope":
        failures.append(f"{case['id']}: provider timing entered matcher output")
    if result["runtime_output"] is not False:
        failures.append(f"{case['id']}: matcher claimed runtime output")
    if result["command_execution"] != "not_performed":
        failures.append(f"{case['id']}: command execution was not explicitly blocked")
    if any(span["executable"] for span in observed_spans):
        failures.append(f"{case['id']}: span marked executable")

    combined_output = json.dumps(result, ensure_ascii=False)
    for absent in case["expected_absent_text"]:
        if absent in combined_output:
            failures.append(f"{case['id']}: absent text {absent!r} leaked")
    for forbidden in ("ipa", "phoneme", "ssml", "pls", "provider_lexicon", "g2p"):
        if forbidden in combined_output.casefold():
            failures.append(f"{case['id']}: forbidden runtime surface {forbidden} leaked")

    return failures, result


def validate_fixtures(fixtures: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    failures = validate_fixture_shape(fixtures)
    observed: list[dict[str, Any]] = []
    if failures:
        return failures, observed
    proved_kinds: set[str] = set()
    for case in fixtures["cases"]:
        case_failures, result = validate_case(case)
        failures.extend(case_failures)
        observed.append(
            {
                "id": case["id"],
                "redaction_count": result["redaction_count"],
                "spans": result["spans"],
                "provider_timing": result["provider_timing"],
            }
        )
        proved_kinds.update(span["kind"] for span in result["spans"])

    required_kinds = {"secret", "protected_term", "protected_phrase", "path", "url", "code", "hash", "exact_island", "command"}
    missing = sorted(required_kinds - proved_kinds)
    if missing:
        failures.append(f"matcher fixtures did not prove span kinds: {missing}")
    return failures, observed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is supported")

    failures, observed = validate_fixtures(load_fixtures())
    status = "FAIL" if failures else "PASS"
    print(
        json.dumps(
            {
                "status": status,
                "version": VERSION,
                "fixtures": str(FIXTURE_PATH.relative_to(ROOT)),
                "observed": observed,
                "failures": failures,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    print(f"[tes-tts-hot-path-span-matcher] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
