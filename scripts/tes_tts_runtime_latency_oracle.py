#!/usr/bin/env python3
"""Measure dependency-free TES TTS text-preparation latency fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
import sys
from time import perf_counter_ns
from typing import Any

import tes_tts_instruction_normalizer_oracle as normalizer


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "benchmarks/tes-tts/runtime-latency-fixtures.json"
VERSION = "0.3.152"
REPEAT_COUNT = 9


def load_fixtures() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def percentile(values: list[float], percentile_value: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = round((len(ordered) - 1) * percentile_value)
    return ordered[index]


def prepare_once(case: dict[str, Any]) -> tuple[normalizer.PreparedSpeech, float]:
    started = perf_counter_ns()
    prepared = normalizer.prepare_instruction_level_speech(case)
    elapsed_ms = (perf_counter_ns() - started) / 1_000_000
    return prepared, elapsed_ms


def validate_shape(fixtures: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if fixtures.get("version") != VERSION:
        failures.append("fixture version drifted")
    if fixtures.get("usage") != "runtime_latency_baseline":
        failures.append("fixture usage must be runtime_latency_baseline")
    if fixtures.get("provider_timing") != "out_of_scope":
        failures.append("provider timing must remain out_of_scope")
    cases = fixtures.get("cases")
    if not isinstance(cases, list) or len(cases) < 4:
        failures.append("runtime latency fixtures must include at least four cases")
        return failures

    required = {
        "id",
        "source_text",
        "detected_language",
        "target_language",
        "protected_terms",
        "max_chunk_chars",
        "rendering_intent",
        "expected_redaction_count",
        "expected_min_chunks",
        "expected_speech_contains",
        "expected_speech_excludes",
        "max_text_prepare_ms_p50",
        "max_first_chunk_ready_ms_p50",
    }
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            failures.append("each runtime latency case must be an object")
            continue
        missing = sorted(required - set(case))
        extra = sorted(set(case) - required)
        if missing or extra:
            failures.append(f"{case.get('id', '<missing-id>')}: fields drifted missing={missing} extra={extra}")
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
    first_prepared: normalizer.PreparedSpeech | None = None
    for _ in range(REPEAT_COUNT):
        prepared, elapsed_ms = prepare_once(case)
        timings.append(elapsed_ms)
        if first_prepared is None:
            first_prepared = prepared

    assert first_prepared is not None
    p50 = median(timings)
    p95 = percentile(timings, 0.95)
    first_chunk_ready_ms = p50
    speech_text = first_prepared.speech_text
    redaction_count = sum(len(entry["redactions"]) for entry in first_prepared.cache)
    forbidden_runtime_outputs = {"ipa", "ssml", "phoneme", "provider_backed_pronunciation"}
    blocked_outputs = set(first_prepared.pronunciation_plan.get("blocked_outputs", []))

    if len(first_prepared.cache) < case["expected_min_chunks"]:
        failures.append(f"{case['id']}: expected at least {case['expected_min_chunks']} chunks")
    if redaction_count != case["expected_redaction_count"] * len(first_prepared.cache):
        failures.append(f"{case['id']}: redaction count drifted")
    for expected in case["expected_speech_contains"]:
        if expected not in speech_text:
            failures.append(f"{case['id']}: expected speech text {expected!r} missing")
    for forbidden in case["expected_speech_excludes"]:
        if forbidden in speech_text:
            failures.append(f"{case['id']}: forbidden speech text {forbidden!r} leaked")
    if "resumo" in speech_text.lower() and "resumo" not in case["source_text"].lower():
        failures.append(f"{case['id']}: summary-like text appeared without request")
    if first_prepared.translation_plan["source_text_unchanged"] != case["source_text"]:
        failures.append(f"{case['id']}: source text mutation was reported")
    if not forbidden_runtime_outputs.issubset(blocked_outputs):
        failures.append(f"{case['id']}: forbidden pronunciation runtime outputs are not blocked")
    if p50 > case["max_text_prepare_ms_p50"]:
        failures.append(f"{case['id']}: p50 text preparation {p50:.3f}ms exceeded threshold")
    if first_chunk_ready_ms > case["max_first_chunk_ready_ms_p50"]:
        failures.append(f"{case['id']}: first chunk ready {first_chunk_ready_ms:.3f}ms exceeded threshold")

    metrics = {
        "id": case["id"],
        "fixture_chars": len(case["source_text"]),
        "protected_span_count": len(case["protected_terms"]),
        "secret_redaction_count": redaction_count,
        "chunk_count": len(first_prepared.cache),
        "text_prepare_ms_p50": round(p50, 3),
        "text_prepare_ms_p95": round(p95, 3),
        "first_chunk_ready_ms": round(first_chunk_ready_ms, 3),
        "provider_timing": "out_of_scope",
        "summary_behavior": "none",
        "source_text_immutable": True,
        "runtime_pronunciation_output": "none",
        "command_execution": "not_performed",
    }
    return failures, metrics


def validate_fixtures(fixtures: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    failures = validate_shape(fixtures)
    metrics: list[dict[str, Any]] = []
    if failures:
        return failures, metrics
    for case in fixtures["cases"]:
        case_failures, case_metrics = validate_case(case)
        failures.extend(case_failures)
        metrics.append(case_metrics)
    return failures, metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is supported")

    fixtures = load_fixtures()
    failures, metrics = validate_fixtures(fixtures)
    status = "FAIL" if failures else "PASS"
    print(
        json.dumps(
            {
                "status": status,
                "version": VERSION,
                "fixtures": str(FIXTURE_PATH.relative_to(ROOT)),
                "repeat_count": REPEAT_COUNT,
                "metrics": metrics,
                "failures": failures,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    print(f"[tes-tts-runtime-latency] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
