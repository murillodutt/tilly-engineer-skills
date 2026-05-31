#!/usr/bin/env python3
"""Validate TES TTS PT-BR lexical manifest records without external dependencies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "benchmarks/tes-tts/ptbr-lexical-manifest.schema.json"
SAMPLE_PATH = ROOT / "benchmarks/tes-tts/ptbr-lexical-sample.jsonl"
VERSION = "0.3.148"

REQUIRED_FIELDS = {
    "id",
    "language",
    "text_graphemes",
    "pronunciation",
    "pronunciation_system",
    "source",
    "source_path",
    "source_line",
    "license_note",
    "usage",
    "status",
}
ID_PATTERN = re.compile(r"^ptbr-lexical-[0-9]{6}$")
STATUSES = {"reference", "degraded"}
PRONUNCIATION_SYSTEMS = {"ipa", "none"}


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: record must be an object")
        records.append(value)
    return records


def validate_schema(schema: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    required = set(schema.get("required", []))
    properties = set(schema.get("properties", {}))
    if required != REQUIRED_FIELDS:
        failures.append(f"schema required fields drifted: {sorted(required)}")
    if not REQUIRED_FIELDS <= properties:
        failures.append(f"schema missing properties: {sorted(REQUIRED_FIELDS - properties)}")
    if schema.get("additionalProperties") is not False:
        failures.append("schema must disallow additional properties")
    if schema.get("properties", {}).get("language", {}).get("const") != "pt-BR":
        failures.append("schema language must be const pt-BR")
    if schema.get("properties", {}).get("usage", {}).get("const") != "evidence_only":
        failures.append("schema usage must be const evidence_only")
    statuses = set(schema.get("properties", {}).get("status", {}).get("enum", []))
    if statuses != STATUSES:
        failures.append(f"schema status enum drifted: {sorted(statuses)}")
    systems = set(schema.get("properties", {}).get("pronunciation_system", {}).get("enum", []))
    if systems != PRONUNCIATION_SYSTEMS:
        failures.append(f"schema pronunciation_system enum drifted: {sorted(systems)}")
    return failures


def validate_record(record: dict[str, Any], index: int) -> list[str]:
    failures: list[str] = []
    prefix = f"record[{index}] {record.get('id', '<missing-id>')}"
    if set(record) != REQUIRED_FIELDS:
        failures.append(f"{prefix}: fields drifted: {sorted(record)}")
        return failures
    if not isinstance(record["id"], str) or not ID_PATTERN.fullmatch(record["id"]):
        failures.append(f"{prefix}: invalid id")
    if record["language"] != "pt-BR":
        failures.append(f"{prefix}: language must be pt-BR")
    if not isinstance(record["text_graphemes"], str) or not record["text_graphemes"]:
        failures.append(f"{prefix}: text_graphemes must be non-empty")
    if not isinstance(record["pronunciation"], str):
        failures.append(f"{prefix}: pronunciation must be a string")
    if record["pronunciation_system"] not in PRONUNCIATION_SYSTEMS:
        failures.append(f"{prefix}: invalid pronunciation_system")
    if not isinstance(record["source"], str) or not record["source"]:
        failures.append(f"{prefix}: source must be non-empty")
    if not isinstance(record["source_path"], str) or not record["source_path"]:
        failures.append(f"{prefix}: source_path must be non-empty")
    if not isinstance(record["source_line"], int) or record["source_line"] < 0:
        failures.append(f"{prefix}: source_line must be a non-negative integer")
    if not isinstance(record["license_note"], str) or not record["license_note"]:
        failures.append(f"{prefix}: license_note must be non-empty")
    if record["usage"] != "evidence_only":
        failures.append(f"{prefix}: usage must be evidence_only")
    if record["status"] not in STATUSES:
        failures.append(f"{prefix}: invalid status")

    if record["status"] == "reference":
        if record["pronunciation_system"] != "ipa":
            failures.append(f"{prefix}: reference entries must use ipa")
        if not record["pronunciation"]:
            failures.append(f"{prefix}: reference entries must include pronunciation")
        if record["source_line"] < 1:
            failures.append(f"{prefix}: reference entries must preserve source_line")
    if record["status"] == "degraded":
        if record["pronunciation_system"] != "none":
            failures.append(f"{prefix}: degraded entries must use pronunciation_system none")
        if record["pronunciation"]:
            failures.append(f"{prefix}: degraded entries must not claim pronunciation")
    return failures


def validate_records(records: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    if len(records) < 4:
        failures.append("sample must include at least four records")
    ids = [record.get("id") for record in records]
    if len(ids) != len(set(ids)):
        failures.append("record ids must be unique")
    graphemes = {record.get("text_graphemes") for record in records}
    for expected in {"A", "A-PROPÓSITO", "ABACAXI", "TES-TTS-OOV"}:
        if expected not in graphemes:
            failures.append(f"sample missing required grapheme {expected}")
    if not any(record.get("status") == "degraded" for record in records):
        failures.append("sample must include a degraded OOV case")
    if not any("-" in str(record.get("text_graphemes", "")) for record in records):
        failures.append("sample must include a hyphenated grapheme")
    if not any("Ó" in str(record.get("text_graphemes", "")) for record in records):
        failures.append("sample must include an accented grapheme")
    for index, record in enumerate(records):
        failures.extend(validate_record(record, index))
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is supported")

    failures = validate_schema(load_schema())
    failures.extend(validate_records(load_jsonl(SAMPLE_PATH)))
    status = "FAIL" if failures else "PASS"
    print(
        json.dumps(
            {
                "status": status,
                "version": VERSION,
                "schema": str(SCHEMA_PATH.relative_to(ROOT)),
                "sample": str(SAMPLE_PATH.relative_to(ROOT)),
                "failures": failures,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    print(f"[tes-tts-ptbr-lexical-manifest] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
