#!/usr/bin/env python3
"""Validate dependency-free compiled lexical index behavior for TES TTS."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
import unicodedata
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LEXICAL_MANIFEST_PATH = ROOT / "benchmarks/tes-tts/ptbr-lexical-sample.jsonl"
PRONUNCIATION_CATALOG_PATH = ROOT / "benchmarks/tes-tts/pronunciation-catalog-fixtures.json"
RUNTIME_LATENCY_FIXTURE_PATH = ROOT / "benchmarks/tes-tts/runtime-latency-fixtures.json"
FIXTURE_PATH = ROOT / "benchmarks/tes-tts/compiled-lexical-index-fixtures.json"
VERSION = "0.3.154"
FORBIDDEN_RUNTIME_OUTPUTS = {"ipa", "phoneme", "ssml", "pls", "provider_lexicon", "g2p"}


@dataclass(frozen=True)
class IndexEntry:
    term: str
    locale: str
    source: str
    status: str
    priority: int
    insertion_order: int
    match_scope: str
    spoken_rendering: str
    usage: str
    runtime_output: bool
    pronunciation_system: str


def canonical(value: str) -> str:
    return unicodedata.normalize("NFC", value.strip()).casefold()


def is_phrase(term: str) -> bool:
    return any(char.isspace() for char in term) or "/" in term or ":" in term


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def lexical_entries(records: list[dict[str, Any]], start_order: int) -> list[IndexEntry]:
    entries: list[IndexEntry] = []
    order = start_order
    for record in records:
        term = record.get("text_graphemes")
        if not isinstance(term, str) or not term:
            continue
        entries.append(
            IndexEntry(
                term=term,
                locale=record.get("language", "pt-BR"),
                source="ptbr_lexical_manifest",
                status=record.get("status", "reference"),
                priority=20 if record.get("status") == "reference" else 5,
                insertion_order=order,
                match_scope="phrase" if is_phrase(term) else "exact",
                spoken_rendering="",
                usage=record.get("usage", "evidence_only"),
                runtime_output=False,
                pronunciation_system=record.get("pronunciation_system", "none"),
            )
        )
        order += 1
    return entries


def catalog_entries(catalog: dict[str, Any], start_order: int) -> list[IndexEntry]:
    priorities = {
        "acronym": 100,
        "proper_noun": 90,
        "technical_noun": 85,
        "url": 80,
        "path": 80,
        "command": 75,
    }
    entries: list[IndexEntry] = []
    order = start_order
    for record in catalog.get("entries", []):
        term = record.get("term")
        if not isinstance(term, str) or not term:
            continue
        record_class = record.get("class", "protected_term")
        entries.append(
            IndexEntry(
                term=term,
                locale=record.get("default_language", "pt-BR"),
                source="pronunciation_catalog",
                status="indexed",
                priority=priorities.get(record_class, 50),
                insertion_order=order,
                match_scope="phrase" if is_phrase(term) else "exact",
                spoken_rendering=record.get("spoken_rendering", ""),
                usage="evidence_only",
                runtime_output=False,
                pronunciation_system="none",
            )
        )
        order += 1
    return entries


def runtime_protected_entries(fixtures: dict[str, Any], start_order: int) -> list[IndexEntry]:
    entries: list[IndexEntry] = []
    order = start_order
    seen: set[tuple[str, str]] = set()
    for case in fixtures.get("cases", []):
        locale = case.get("target_language", "pt-BR")
        for term in case.get("protected_terms", []):
            if not isinstance(term, str) or not term:
                continue
            key = (locale, canonical(term))
            if key in seen:
                continue
            seen.add(key)
            entries.append(
                IndexEntry(
                    term=term,
                    locale=locale,
                    source="runtime_latency_fixture",
                    status="indexed",
                    priority=60,
                    insertion_order=order,
                    match_scope="phrase" if is_phrase(term) else "exact",
                    spoken_rendering=term,
                    usage="evidence_only",
                    runtime_output=False,
                    pronunciation_system="none",
                )
            )
            order += 1
    return entries


def entry_sort_key(entry: IndexEntry) -> tuple[int, int, int]:
    return (-entry.priority, -len(entry.term), entry.insertion_order)


def compile_index() -> dict[str, Any]:
    entries: list[IndexEntry] = []
    entries.extend(lexical_entries(load_jsonl(LEXICAL_MANIFEST_PATH), len(entries)))
    entries.extend(catalog_entries(load_json(PRONUNCIATION_CATALOG_PATH), len(entries)))
    entries.extend(runtime_protected_entries(load_json(RUNTIME_LATENCY_FIXTURE_PATH), len(entries)))

    exact: dict[str, dict[str, IndexEntry]] = {}
    phrase: dict[str, list[IndexEntry]] = {}
    duplicates: list[dict[str, Any]] = []
    for entry in sorted(entries, key=entry_sort_key):
        locale_exact = exact.setdefault(entry.locale, {})
        locale_phrase = phrase.setdefault(entry.locale, [])
        key = canonical(entry.term)
        if entry.match_scope == "exact":
            if key in locale_exact:
                duplicates.append(
                    {
                        "locale": entry.locale,
                        "term": entry.term,
                        "kept": locale_exact[key].source,
                        "dropped": entry.source,
                    }
                )
                continue
            locale_exact[key] = entry
        else:
            if any(canonical(existing.term) == key for existing in locale_phrase):
                duplicates.append(
                    {
                        "locale": entry.locale,
                        "term": entry.term,
                        "kept": next(existing.source for existing in locale_phrase if canonical(existing.term) == key),
                        "dropped": entry.source,
                    }
                )
                continue
            locale_phrase.append(entry)

    for entries_for_locale in phrase.values():
        entries_for_locale.sort(key=entry_sort_key)

    return {
        "exact": exact,
        "phrase": phrase,
        "duplicates": duplicates,
        "entry_count": len(entries),
    }


def lookup(query: str, locale: str, index: dict[str, Any]) -> dict[str, Any]:
    source_query = unicodedata.normalize("NFC", query)
    for entry in index["phrase"].get(locale, []):
        if canonical(source_query) == canonical(entry.term):
            return format_result(source_query, "phrase", entry)

    exact_locale = index["exact"].get(locale, {})
    if source_query in {entry.term for entry in exact_locale.values()}:
        entry = next(entry for entry in exact_locale.values() if entry.term == source_query)
        return format_result(source_query, "exact", entry)

    entry = exact_locale.get(canonical(source_query))
    if entry is not None:
        return format_result(source_query, "casefold", entry)

    return {
        "query": source_query,
        "locale": locale,
        "match_type": "oov",
        "term": "",
        "source": "",
        "status": "degraded",
        "priority": 0,
        "spoken_rendering": "",
        "usage": "evidence_only",
        "runtime_output": False,
        "pronunciation_system": "none",
    }


def format_result(query: str, match_type: str, entry: IndexEntry) -> dict[str, Any]:
    return {
        "query": query,
        "locale": entry.locale,
        "match_type": match_type,
        "term": entry.term,
        "source": entry.source,
        "status": entry.status,
        "priority": entry.priority,
        "spoken_rendering": entry.spoken_rendering,
        "usage": entry.usage,
        "runtime_output": entry.runtime_output,
        "pronunciation_system": entry.pronunciation_system,
    }


def validate_fixture_shape(fixtures: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if fixtures.get("version") != VERSION:
        failures.append("fixture version drifted")
    if fixtures.get("usage") != "compiled_lexical_index_contract":
        failures.append("fixture usage must be compiled_lexical_index_contract")
    if fixtures.get("runtime_output") is not False:
        failures.append("compiled index fixture must not claim runtime output")
    expected_sources = {
        "benchmarks/tes-tts/ptbr-lexical-sample.jsonl",
        "benchmarks/tes-tts/pronunciation-catalog-fixtures.json",
        "benchmarks/tes-tts/runtime-latency-fixtures.json",
    }
    if set(fixtures.get("canonical_sources", [])) != expected_sources:
        failures.append("canonical source list drifted")
    cases = fixtures.get("cases")
    if not isinstance(cases, list) or len(cases) < 5:
        failures.append("compiled lexical index fixtures must include at least five cases")
        return failures
    required = {
        "id",
        "query",
        "locale",
        "expected_match_type",
        "expected_term",
        "expected_source",
        "expected_spoken_rendering",
        "expected_status",
    }
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            failures.append("case must be an object")
            continue
        if set(case) != required:
            failures.append(f"{case.get('id', '<missing-id>')}: case fields drifted")
        if case.get("id") in seen:
            failures.append(f"{case['id']}: duplicate case id")
        seen.add(case.get("id", ""))
    return failures


def validate_index(fixtures: dict[str, Any], index: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    failures: list[str] = []
    observed: list[dict[str, Any]] = []
    match_types: set[str] = set()

    if index["entry_count"] < 15:
        failures.append("compiled index did not ingest enough governed entries")
    if not any(item["term"] == "ADR" for item in index["duplicates"]):
        failures.append("duplicate handling for ADR was not observed")

    for case in fixtures.get("cases", []):
        result = lookup(case["query"], case["locale"], index)
        observed.append(result)
        match_types.add(result["match_type"])
        expected = {
            "match_type": case["expected_match_type"],
            "term": case["expected_term"],
            "source": case["expected_source"],
            "spoken_rendering": case["expected_spoken_rendering"],
            "status": case["expected_status"],
        }
        actual = {key: result[key] for key in expected}
        if actual != expected:
            failures.append(f"{case['id']}: expected {expected}, got {actual}")
        if result["usage"] != "evidence_only":
            failures.append(f"{case['id']}: compiled index usage must remain evidence_only")
        if result["runtime_output"] is not False:
            failures.append(f"{case['id']}: compiled index must not claim runtime output")
        if result["pronunciation_system"].casefold() in FORBIDDEN_RUNTIME_OUTPUTS and result["spoken_rendering"]:
            failures.append(f"{case['id']}: pronunciation evidence leaked into runtime rendering")

    for required in {"exact", "phrase", "casefold", "oov"}:
        if required not in match_types:
            failures.append(f"compiled index fixtures must prove {required} lookup")
    return failures, observed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is supported")

    fixtures = load_json(FIXTURE_PATH)
    index = compile_index()
    failures = validate_fixture_shape(fixtures)
    observed: list[dict[str, Any]] = []
    if not failures:
        failures, observed = validate_index(fixtures, index)
    status = "FAIL" if failures else "PASS"
    print(
        json.dumps(
            {
                "status": status,
                "version": VERSION,
                "fixtures": str(FIXTURE_PATH.relative_to(ROOT)),
                "entry_count": index["entry_count"],
                "duplicate_count": len(index["duplicates"]),
                "observed": observed,
                "failures": failures,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    print(f"[tes-tts-compiled-lexical-index] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
