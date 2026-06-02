#!/usr/bin/env python3
"""Validate dependency-free PT-BR lexical lookup evidence for TES TTS."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import unicodedata
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "benchmarks/tes-tts/ptbr-lexical-sample.jsonl"
FIXTURE_PATH = ROOT / "benchmarks/tes-tts/ptbr-lexical-lookup-fixtures.json"
VERSION = "0.3.157"


def canonical_grapheme(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value.strip())
    return normalized.casefold()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"{path}:{line_number}: record must be an object")
        records.append(record)
    return records


def build_lookup(records: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    exact: dict[str, dict[str, Any]] = {}
    canonical: dict[str, dict[str, Any]] = {}
    for record in records:
        grapheme = record.get("text_graphemes")
        if not isinstance(grapheme, str) or not grapheme:
            continue
        exact[grapheme] = record
        key = canonical_grapheme(grapheme)
        canonical.setdefault(key, record)
    return exact, canonical


def lookup_grapheme(query: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    source_query = unicodedata.normalize("NFC", query)
    exact, canonical = build_lookup(records)
    if source_query in exact:
        record = exact[source_query]
        match_type = "exact"
    else:
        record = canonical.get(canonical_grapheme(source_query))
        match_type = "casefold" if record else "oov"

    if record is None:
        return {
            "query": source_query,
            "source_text_unchanged": source_query == query,
            "match_type": "oov",
            "record_id": None,
            "language": "pt-BR",
            "status": "degraded",
            "pronunciation": "",
            "pronunciation_system": "none",
            "usage": "evidence_only",
            "runtime_output": False,
        }

    return {
        "query": source_query,
        "source_text_unchanged": source_query == query,
        "match_type": match_type,
        "record_id": record["id"],
        "language": record["language"],
        "status": record["status"],
        "pronunciation": record["pronunciation"],
        "pronunciation_system": record["pronunciation_system"],
        "usage": record["usage"],
        "source": record["source"],
        "source_path": record["source_path"],
        "source_line": record["source_line"],
        "runtime_output": False,
    }


def load_fixtures() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def validate_fixture_shape(fixtures: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    cases = fixtures.get("cases")
    if fixtures.get("version") != VERSION:
        failures.append("fixture version drifted")
    if fixtures.get("manifest") != str(MANIFEST_PATH.relative_to(ROOT)):
        failures.append("fixture manifest path drifted")
    if not isinstance(cases, list) or len(cases) < 5:
        failures.append("fixture must include at least five lookup cases")
        return failures

    seen: set[str] = set()
    required_keys = {
        "id",
        "query",
        "expected_match_type",
        "expected_record_id",
        "expected_status",
        "expected_pronunciation_system",
    }
    for case in cases:
        if not isinstance(case, dict):
            failures.append("fixture case must be an object")
            continue
        if set(case) != required_keys:
            failures.append(f"{case.get('id', '<missing-id>')}: case fields drifted")
            continue
        if case["id"] in seen:
            failures.append(f"{case['id']}: duplicate case id")
        seen.add(case["id"])
    return failures


def validate_lookup(records: list[dict[str, Any]], fixtures: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    match_types = set()
    for case in fixtures.get("cases", []):
        result = lookup_grapheme(case["query"], records)
        match_types.add(result["match_type"])
        expected = {
            "match_type": case["expected_match_type"],
            "record_id": case["expected_record_id"],
            "status": case["expected_status"],
            "pronunciation_system": case["expected_pronunciation_system"],
        }
        observed = {key: result[key] for key in expected}
        if observed != expected:
            failures.append(f"{case['id']}: expected {expected}, got {observed}")
        if result["language"] != "pt-BR":
            failures.append(f"{case['id']}: lookup must remain pt-BR")
        if result["usage"] != "evidence_only":
            failures.append(f"{case['id']}: lookup usage must remain evidence_only")
        if result["runtime_output"] is not False:
            failures.append(f"{case['id']}: lookup must not claim runtime output")
        if not result["source_text_unchanged"]:
            failures.append(f"{case['id']}: lookup mutated source query")
        if result["status"] == "degraded" and result["pronunciation"]:
            failures.append(f"{case['id']}: degraded lookup must not claim pronunciation")
        if result["status"] == "reference" and not result["pronunciation"]:
            failures.append(f"{case['id']}: reference lookup must preserve pronunciation evidence")

    for required in {"exact", "casefold", "oov"}:
        if required not in match_types:
            failures.append(f"lookup fixtures must prove {required} behavior")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is supported")

    records = load_jsonl(MANIFEST_PATH)
    fixtures = load_fixtures()
    failures = validate_fixture_shape(fixtures)
    failures.extend(validate_lookup(records, fixtures))
    status = "FAIL" if failures else "PASS"
    print(
        json.dumps(
            {
                "status": status,
                "version": VERSION,
                "manifest": str(MANIFEST_PATH.relative_to(ROOT)),
                "fixtures": str(FIXTURE_PATH.relative_to(ROOT)),
                "checked_cases": len(fixtures.get("cases", [])),
                "failures": failures,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    print(f"[tes-tts-ptbr-lexical-lookup] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
