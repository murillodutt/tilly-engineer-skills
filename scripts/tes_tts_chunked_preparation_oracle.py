#!/usr/bin/env python3
"""Validate chunked request-local preparation for TES TTS."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from statistics import median
import sys
from time import perf_counter_ns
from typing import Any

import tes_tts_hot_path_span_matcher_oracle as span_matcher
import tes_tts_request_local_memoization_oracle as memoization


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "benchmarks/tes-tts/chunked-preparation-fixtures.json"
VERSION = "0.3.147"
REPEAT_COUNT = 9
FORBIDDEN_RUNTIME_SURFACES = ("ipa", "phoneme", "ssml", "pls", "provider_lexicon", "g2p")
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def load_fixtures() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def source_chunks(source_text: str, max_chars: int) -> list[str]:
    sentences = [part.strip() for part in SENTENCE_BOUNDARY.split(source_text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip() if current else sentence
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def render_chunk_with_memo(source_text: str, locale: str, memo: dict[str, str]) -> dict[str, Any]:
    match_result = span_matcher.match_hot_path_spans(source_text, locale)
    redacted_text = match_result["redacted_text"]
    spans = sorted(match_result["spans"], key=lambda span: span["start"])
    hits = 0
    misses = 0
    parts: list[str] = []
    cursor = 0
    for span in spans:
        key = memoization.memo_key(span)
        if key in memo:
            hits += 1
            rendering = memo[key]
        else:
            misses += 1
            rendering = span["rendering"]
            memo[key] = rendering
        parts.append(redacted_text[cursor : span["start"]])
        parts.append(rendering)
        cursor = span["end"]
    parts.append(redacted_text[cursor:])
    return {
        "spoken_text": "".join(parts).replace("`", ""),
        "redaction_count": match_result["redaction_count"],
        "span_kinds": [span["kind"] for span in spans],
        "cache_hits": hits,
        "cache_misses": misses,
        "command_execution": "not_performed",
    }


def prepare_chunks(source_text: str, locale: str, max_chars: int) -> dict[str, Any]:
    memo: dict[str, str] = {}
    chunks = source_chunks(source_text, max_chars)
    prepared_chunks: list[dict[str, Any]] = []
    total_redactions = 0
    total_hits = 0
    total_misses = 0
    first_started = perf_counter_ns()
    first_chunk_ready_ms = 0.0
    for index, chunk in enumerate(chunks):
        chunk_result = render_chunk_with_memo(chunk, locale, memo)
        if index == 0:
            first_chunk_ready_ms = (perf_counter_ns() - first_started) / 1_000_000
        total_redactions += chunk_result["redaction_count"]
        total_hits += chunk_result["cache_hits"]
        total_misses += chunk_result["cache_misses"]
        prepared_chunks.append(
            {
                "index": index,
                "spoken_text": chunk_result["spoken_text"],
                "span_kinds": chunk_result["span_kinds"],
                "cache_hits": chunk_result["cache_hits"],
                "cache_misses": chunk_result["cache_misses"],
                "command_execution": chunk_result["command_execution"],
            }
        )
    return {
        "source_text_immutable": True,
        "spoken_text": " ".join(chunk["spoken_text"] for chunk in prepared_chunks),
        "chunks": prepared_chunks,
        "first_chunk_ready_ms": first_chunk_ready_ms,
        "redaction_count": total_redactions,
        "cache_hits": total_hits,
        "cache_misses": total_misses,
        "resolved_once_keys": sorted(memo),
        "chunk_scope": "request_local_ordered",
        "memo_scope": "request_local",
        "provider_timing": "out_of_scope",
        "runtime_output": False,
        "summary_behavior": "none",
        "command_execution": "not_performed",
        "runtime_pronunciation_output": "none",
    }


def prepare_once(case: dict[str, Any]) -> tuple[dict[str, Any], float]:
    started = perf_counter_ns()
    result = prepare_chunks(case["source_text"], case["locale"], case["max_source_chunk_chars"])
    elapsed_ms = (perf_counter_ns() - started) / 1_000_000
    return result, elapsed_ms


def validate_shape(fixtures: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if fixtures.get("version") != VERSION:
        failures.append("fixture version drifted")
    if fixtures.get("usage") != "chunked_preparation_boundary_contract":
        failures.append("fixture usage must be chunked_preparation_boundary_contract")
    if fixtures.get("runtime_output") is not False:
        failures.append("chunked preparation fixture must not claim runtime output")
    if fixtures.get("provider_timing") != "out_of_scope":
        failures.append("provider timing must remain out_of_scope")
    if fixtures.get("chunk_scope") != "request_local_ordered":
        failures.append("chunk scope must be request_local_ordered")
    cases = fixtures.get("cases")
    if not isinstance(cases, list) or len(cases) < 3:
        failures.append("chunked preparation fixtures must include at least three cases")
        return failures
    required = {
        "id",
        "source_text",
        "locale",
        "max_source_chunk_chars",
        "expected_chunk_texts",
        "expected_first_chunk_text",
        "expected_total_cache_hits",
        "expected_total_cache_misses",
        "expected_redaction_count",
        "expected_absent_text",
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
    timings: list[float] = []
    first_chunk_timings: list[float] = []
    first_result: dict[str, Any] | None = None
    for _ in range(REPEAT_COUNT):
        result, elapsed_ms = prepare_once(case)
        timings.append(elapsed_ms)
        first_chunk_timings.append(result["first_chunk_ready_ms"])
        if first_result is None:
            first_result = result

    assert first_result is not None
    chunk_texts = [chunk["spoken_text"] for chunk in first_result["chunks"]]
    if chunk_texts != case["expected_chunk_texts"]:
        failures.append(f"{case['id']}: chunk texts drifted")
    if not first_result["chunks"] or first_result["chunks"][0]["spoken_text"] != case["expected_first_chunk_text"]:
        failures.append(f"{case['id']}: first speakable chunk drifted")
    if [chunk["index"] for chunk in first_result["chunks"]] != list(range(len(first_result["chunks"]))):
        failures.append(f"{case['id']}: chunk ordering drifted")
    if first_result["cache_hits"] != case["expected_total_cache_hits"]:
        failures.append(f"{case['id']}: total cache hits drifted")
    if first_result["cache_misses"] != case["expected_total_cache_misses"]:
        failures.append(f"{case['id']}: total cache misses drifted")
    if first_result["redaction_count"] != case["expected_redaction_count"]:
        failures.append(f"{case['id']}: redaction count drifted")
    if first_result["first_chunk_ready_ms"] > 100:
        failures.append(f"{case['id']}: first chunk exceeded 100ms")

    combined_output = json.dumps(first_result, ensure_ascii=False)
    for absent in case["expected_absent_text"]:
        if absent in combined_output:
            failures.append(f"{case['id']}: absent text {absent!r} leaked")
    for forbidden in FORBIDDEN_RUNTIME_SURFACES:
        if forbidden in combined_output.casefold():
            failures.append(f"{case['id']}: forbidden runtime surface {forbidden} leaked")
    if not first_result["source_text_immutable"]:
        failures.append(f"{case['id']}: source text was mutated")
    if first_result["summary_behavior"] != "none":
        failures.append(f"{case['id']}: summary behavior changed")
    if first_result["command_execution"] != "not_performed":
        failures.append(f"{case['id']}: command execution was not blocked")
    if any(chunk["command_execution"] != "not_performed" for chunk in first_result["chunks"]):
        failures.append(f"{case['id']}: a chunk was executable")
    if first_result["provider_timing"] != "out_of_scope":
        failures.append(f"{case['id']}: provider timing entered chunked output")
    if first_result["runtime_output"] is not False:
        failures.append(f"{case['id']}: chunked preparation claimed runtime output")
    if first_result["runtime_pronunciation_output"] != "none":
        failures.append(f"{case['id']}: pronunciation runtime output was emitted")
    if first_result["memo_scope"] != "request_local":
        failures.append(f"{case['id']}: memo scope drifted")
    if first_result["chunk_scope"] != "request_local_ordered":
        failures.append(f"{case['id']}: chunk scope drifted")

    observed = {
        "id": case["id"],
        "chunk_count": len(first_result["chunks"]),
        "first_chunk_text": first_result["chunks"][0]["spoken_text"] if first_result["chunks"] else "",
        "cache_hits": first_result["cache_hits"],
        "cache_misses": first_result["cache_misses"],
        "redaction_count": first_result["redaction_count"],
        "text_prepare_ms_p50": round(median(timings), 3),
        "first_chunk_ready_ms_p50": round(median(first_chunk_timings), 3),
        "provider_timing": first_result["provider_timing"],
        "chunk_scope": first_result["chunk_scope"],
    }
    return failures, observed


def validate_fixtures(fixtures: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    failures = validate_shape(fixtures)
    observed: list[dict[str, Any]] = []
    if failures:
        return failures, observed
    for case in fixtures["cases"]:
        case_failures, result = validate_case(case)
        failures.extend(case_failures)
        observed.append(result)
    if not any(item["chunk_count"] > 1 for item in observed):
        failures.append("fixtures did not prove multi-chunk preparation")
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
                "repeat_count": REPEAT_COUNT,
                "observed": observed,
                "failures": failures,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    print(f"[tes-tts-chunked-preparation] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
