#!/usr/bin/env python3
"""Validate dependency-free fast-path spoken rendering for TES TTS."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
import sys
from time import perf_counter_ns
from typing import Any

import tes_tts_runtime


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "benchmarks/tes-tts/fast-path-spoken-rendering-fixtures.json"
VERSION = "0.3.150"
REPEAT_COUNT = 9
FORBIDDEN_RUNTIME_SURFACES = ("ipa", "phoneme", "ssml", "pls", "provider_lexicon", "g2p")


def load_fixtures() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def render_fast_path(source_text: str, locale: str) -> dict[str, Any]:
    prepared = tes_tts_runtime.prepare_spoken_text(source_text, locale)
    return {
        "source_text_immutable": True,
        "spoken_text": prepared["spoken_text"],
        "redacted_text": prepared["redacted_text"],
        "span_kinds": prepared["span_kinds"],
        "redaction_count": prepared["redaction_count"],
        "provider_timing": "out_of_scope",
        "runtime_output": False,
        "summary_behavior": "none",
        "command_execution": "not_performed",
        "runtime_pronunciation_output": "none",
    }


def render_once(case: dict[str, Any]) -> tuple[dict[str, Any], float]:
    started = perf_counter_ns()
    result = render_fast_path(case["source_text"], case["locale"])
    elapsed_ms = (perf_counter_ns() - started) / 1_000_000
    return result, elapsed_ms


def validate_shape(fixtures: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if fixtures.get("version") != VERSION:
        failures.append("fixture version drifted")
    if fixtures.get("usage") != "fast_path_spoken_rendering_contract":
        failures.append("fixture usage must be fast_path_spoken_rendering_contract")
    if fixtures.get("runtime_output") is not False:
        failures.append("fast-path fixture must not claim runtime output")
    if fixtures.get("provider_timing") != "out_of_scope":
        failures.append("provider timing must remain out_of_scope")
    cases = fixtures.get("cases")
    if not isinstance(cases, list) or len(cases) < 4:
        failures.append("fast-path fixtures must include at least four cases")
        return failures
    required = {
        "id",
        "source_text",
        "locale",
        "expected_spoken_text",
        "expected_contains",
        "expected_absent_text",
        "expected_span_kinds",
        "expected_redaction_count",
        "max_text_prepare_ms_p50",
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
    first_result: dict[str, Any] | None = None
    for _ in range(REPEAT_COUNT):
        result, elapsed_ms = render_once(case)
        timings.append(elapsed_ms)
        if first_result is None:
            first_result = result

    assert first_result is not None
    p50 = median(timings)
    spoken_text = first_result["spoken_text"]
    if spoken_text != case["expected_spoken_text"]:
        failures.append(f"{case['id']}: spoken_text drifted")
    if first_result["span_kinds"] != case["expected_span_kinds"]:
        failures.append(f"{case['id']}: span kinds drifted")
    if first_result["redaction_count"] != case["expected_redaction_count"]:
        failures.append(f"{case['id']}: redaction count drifted")
    for expected in case["expected_contains"]:
        if expected not in spoken_text:
            failures.append(f"{case['id']}: expected text {expected!r} missing")
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
    if first_result["provider_timing"] != "out_of_scope":
        failures.append(f"{case['id']}: provider timing entered fast path")
    if first_result["runtime_output"] is not False:
        failures.append(f"{case['id']}: fast path claimed runtime output")
    if first_result["runtime_pronunciation_output"] != "none":
        failures.append(f"{case['id']}: pronunciation runtime output was emitted")
    if p50 > case["max_text_prepare_ms_p50"]:
        failures.append(f"{case['id']}: p50 text preparation {p50:.3f}ms exceeded threshold")

    observed = {
        "id": case["id"],
        "spoken_text": spoken_text,
        "span_kinds": first_result["span_kinds"],
        "redaction_count": first_result["redaction_count"],
        "text_prepare_ms_p50": round(p50, 3),
        "provider_timing": first_result["provider_timing"],
        "summary_behavior": first_result["summary_behavior"],
        "runtime_pronunciation_output": first_result["runtime_pronunciation_output"],
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
    print(f"[tes-tts-fast-path-spoken-rendering] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
