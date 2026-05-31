#!/usr/bin/env python3
"""Validate the PT-BR lexical evidence boundary for request-local speech prep."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

from tes_tts_ptbr_lexical_lookup_oracle import load_jsonl, lookup_grapheme


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "benchmarks/tes-tts/ptbr-lexical-sample.jsonl"
FIXTURE_PATH = ROOT / "benchmarks/tes-tts/ptbr-lexical-integration-fixtures.json"
VERSION = "0.3.148"
SECRET_PATTERN = re.compile(r"\b(?:sk|pk|ghp|gho|ghu|ghs|github_pat)-[A-Za-z0-9_-]{10,}\b")
TOKEN_PATTERN = re.compile(r"[\wÀ-ÿ]+(?:-[\wÀ-ÿ]+)*", re.UNICODE)


def redact_secrets(text: str) -> tuple[str, list[str]]:
    redactions: list[str] = []

    def replace(match: re.Match[str]) -> str:
        redactions.append(match.group(0))
        return "[SECRET_REDACTED]"

    return SECRET_PATTERN.sub(replace, text), redactions


def lexical_boundary_record(source_text: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    spoken_text, redactions = redact_secrets(source_text)
    evidence: list[dict[str, Any]] = []
    for match in TOKEN_PATTERN.finditer(spoken_text):
        token = match.group(0)
        result = lookup_grapheme(token, records)
        if result["record_id"] is None:
            continue
        evidence.append(
            {
                "span": token,
                "record_id": result["record_id"],
                "status": result["status"],
                "pronunciation_system": result["pronunciation_system"],
                "usage": result["usage"],
                "runtime_output": False,
            }
        )
    return {
        "source_text": source_text,
        "source_text_unchanged": source_text,
        "spoken_text": spoken_text,
        "spoken_text_scope": "request_local",
        "lexical_evidence": evidence,
        "redactions": len(redactions),
        "code_executed": False,
        "summary_performed": False,
        "provider_required": False,
        "provider_absence_status": "degraded",
        "runtime_ipa_output": False,
        "runtime_phoneme_output": False,
        "runtime_ssml_output": False,
        "status": "prepared" if evidence else "degraded",
    }


def load_fixtures() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def validate_fixture_shape(fixtures: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if fixtures.get("version") != VERSION:
        failures.append("fixture version drifted")
    if fixtures.get("manifest") != str(MANIFEST_PATH.relative_to(ROOT)):
        failures.append("fixture manifest path drifted")
    cases = fixtures.get("cases")
    if not isinstance(cases, list) or len(cases) < 6:
        failures.append("fixture must include at least six integration cases")
        return failures
    required = {
        "id",
        "source_text",
        "expected_spoken_text",
        "expected_evidence_ids",
        "expected_status",
        "expect_secret_redaction",
    }
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            failures.append("fixture case must be an object")
            continue
        if set(case) != required:
            failures.append(f"{case.get('id', '<missing-id>')}: case fields drifted")
            continue
        if case["id"] in seen:
            failures.append(f"{case['id']}: duplicate case id")
        seen.add(case["id"])
    return failures


def validate_boundary(records: list[dict[str, Any]], fixtures: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    known_pronunciations = {
        record["pronunciation"]
        for record in records
        if record.get("pronunciation_system") == "ipa" and record.get("pronunciation")
    }
    for case in fixtures.get("cases", []):
        result = lexical_boundary_record(case["source_text"], records)
        evidence_ids = [item["record_id"] for item in result["lexical_evidence"]]
        if result["source_text_unchanged"] != case["source_text"]:
            failures.append(f"{case['id']}: source_text mutated")
        if result["spoken_text"] != case["expected_spoken_text"]:
            failures.append(
                f"{case['id']}: expected spoken_text {case['expected_spoken_text']!r}, "
                f"got {result['spoken_text']!r}"
            )
        if evidence_ids != case["expected_evidence_ids"]:
            failures.append(f"{case['id']}: expected evidence ids {case['expected_evidence_ids']}, got {evidence_ids}")
        if result["status"] != case["expected_status"]:
            failures.append(f"{case['id']}: expected status {case['expected_status']}, got {result['status']}")
        if bool(result["redactions"]) != case["expect_secret_redaction"]:
            failures.append(f"{case['id']}: redaction expectation drifted")
        if any(pronunciation and pronunciation in result["spoken_text"] for pronunciation in known_pronunciations):
            failures.append(f"{case['id']}: pronunciation leaked into spoken_text")
        for forbidden_flag in ("code_executed", "summary_performed", "provider_required"):
            if result[forbidden_flag] is not False:
                failures.append(f"{case['id']}: {forbidden_flag} must remain false")
        for runtime_flag in ("runtime_ipa_output", "runtime_phoneme_output", "runtime_ssml_output"):
            if result[runtime_flag] is not False:
                failures.append(f"{case['id']}: {runtime_flag} must remain false")
        for item in result["lexical_evidence"]:
            if item["usage"] != "evidence_only":
                failures.append(f"{case['id']}: lexical evidence usage drifted")
            if item["runtime_output"] is not False:
                failures.append(f"{case['id']}: lexical evidence claimed runtime output")
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
    failures.extend(validate_boundary(records, fixtures))
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
    print(f"[tes-tts-ptbr-lexical-integration] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
