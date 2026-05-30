#!/usr/bin/env python3
"""Validate the durable TES TTS runtime IR contract."""

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
FIXTURE_PATH = ROOT / "benchmarks/tes-tts/runtime-ir-fixtures.json"
VERSION = "0.3.147"
REPEAT_COUNT = 9
FORBIDDEN_SPOKEN_OUTPUTS = ("ssml", "<speak", "<phoneme", "<lexicon", ".pls")
EXPECTED_PIPELINE = ["classify", "verbalize", "adapt_plain_text"]


def load_fixtures() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def validate_shape(fixtures: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if fixtures.get("version") != VERSION:
        failures.append("fixture version drifted")
    if fixtures.get("usage") != "runtime_ir_contract":
        failures.append("fixture usage must be runtime_ir_contract")
    if fixtures.get("provider_timing") != "out_of_scope":
        failures.append("provider timing must remain out_of_scope")
    if fixtures.get("output_format") != "plain_text":
        failures.append("runtime IR fixtures must target plain_text output")
    cases = fixtures.get("cases")
    if not isinstance(cases, list) or len(cases) < 3:
        failures.append("runtime IR fixtures must include at least three cases")
        return failures
    required = {
        "id",
        "source_text",
        "locale",
        "expected_spoken_text",
        "expected_span_types",
        "expected_aliases",
        "expected_absent_spoken_text",
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


def run_case(case: dict[str, Any]) -> tuple[dict[str, Any], float]:
    started = perf_counter_ns()
    result = tes_tts_runtime.prepare_spoken_text(case["source_text"], case["locale"])
    elapsed_ms = (perf_counter_ns() - started) / 1_000_000
    return result, elapsed_ms


def validate_case(case: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    failures: list[str] = []
    timings: list[float] = []
    first_result: dict[str, Any] | None = None
    for _ in range(REPEAT_COUNT):
        result, elapsed_ms = run_case(case)
        timings.append(elapsed_ms)
        if first_result is None:
            first_result = result

    assert first_result is not None
    spoken_text = first_result["spoken_text"]
    ir = first_result["ir"]
    span_types = [span["span_type"] for span in ir]
    aliases = [span["spoken_alias"] for span in ir]

    if first_result["source_text_immutable"] is not True:
        failures.append(f"{case['id']}: source text immutability changed")
    if first_result.get("pipeline") != EXPECTED_PIPELINE:
        failures.append(f"{case['id']}: pipeline boundary drifted")
    if spoken_text != case["expected_spoken_text"]:
        failures.append(f"{case['id']}: spoken_text drifted")
    if span_types != case["expected_span_types"]:
        failures.append(f"{case['id']}: span types drifted")
    if aliases != case["expected_aliases"]:
        failures.append(f"{case['id']}: aliases drifted")
    if first_result["redaction_count"] != case["expected_redaction_count"]:
        failures.append(f"{case['id']}: redaction count drifted")
    if first_result["provider_timing"] != "out_of_scope":
        failures.append(f"{case['id']}: provider timing entered runtime preparation")
    if first_result["output_format"] != "plain_text":
        failures.append(f"{case['id']}: runtime output format drifted")
    if first_result["summary_behavior"] != "none":
        failures.append(f"{case['id']}: summary behavior changed")
    if first_result["command_execution"] != "not_performed":
        failures.append(f"{case['id']}: command execution changed")
    if first_result["runtime_pronunciation_output"] != "none":
        failures.append(f"{case['id']}: pronunciation runtime surface leaked")
    index_strategy = first_result.get("index_strategy", {})
    if index_strategy.get("strategy") != "regex_union":
        failures.append(f"{case['id']}: protected matcher strategy drifted")
    if index_strategy.get("runtime_dependency") != "none":
        failures.append(f"{case['id']}: protected matcher gained runtime dependency")
    if not isinstance(index_strategy.get("entry_count"), int) or index_strategy["entry_count"] < 10:
        failures.append(f"{case['id']}: protected matcher did not compile enough entries")
    if not isinstance(index_strategy.get("trie_recommended"), bool):
        failures.append(f"{case['id']}: trie recommendation must be boolean")
    if not isinstance(index_strategy.get("aho_corasick_recommended"), bool):
        failures.append(f"{case['id']}: aho-corasick recommendation must be boolean")
    if any("runtime_class" not in span for span in ir):
        failures.append(f"{case['id']}: structured span catalog metadata missing")
    if any(span["executable"] for span in ir):
        failures.append(f"{case['id']}: IR span marked executable")
    for absent in case["expected_absent_spoken_text"]:
        if absent in spoken_text:
            failures.append(f"{case['id']}: absent spoken text {absent!r} leaked")
    spoken_lower = spoken_text.casefold()
    for forbidden in FORBIDDEN_SPOKEN_OUTPUTS:
        if forbidden in spoken_lower:
            failures.append(f"{case['id']}: forbidden spoken output {forbidden!r} leaked")

    observed = {
        "id": case["id"],
        "spoken_text": spoken_text,
        "span_types": span_types,
        "aliases": aliases,
        "redaction_count": first_result["redaction_count"],
        "index_strategy": index_strategy.get("strategy"),
        "protected_entry_count": index_strategy.get("entry_count"),
        "text_prepare_ms_p50": round(median(timings), 3),
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
    print(f"[tes-tts-runtime-ir] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
