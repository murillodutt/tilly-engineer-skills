#!/usr/bin/env python3
"""Dependency-free TES TTS runtime preparation.

This is the small durable runtime path for text preparation:
source text -> protected spans -> IR -> request-local spoken text.
Provider playback stays outside this module.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
import unicodedata
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LEXICAL_MANIFEST_PATH = ROOT / "benchmarks/tes-tts/ptbr-lexical-sample.jsonl"
PRONUNCIATION_CATALOG_PATH = ROOT / "benchmarks/tes-tts/pronunciation-catalog-fixtures.json"
RUNTIME_LATENCY_FIXTURE_PATH = ROOT / "benchmarks/tes-tts/runtime-latency-fixtures.json"
VERSION = "0.3.147"
REDACTION_TOKEN = "[REDACTED_SECRET]"

SECRET_PATTERN = re.compile(
    r"\b(?:api_key|token|password|secret|[A-Z][A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD))="
    r"([A-Za-z0-9_./:+-]+)"
)
BEARER_SECRET_PATTERN = re.compile(r"\bBearer\s+([A-Za-z0-9._:+/-]{8,})")
REDACTED_SECRET_PATTERN = re.compile(re.escape(REDACTION_TOKEN))
INLINE_CODE_PATTERN = re.compile(r"`([^`]+)`")
URL_PATTERN = re.compile(r"https?://[^\s),;]+")
PATH_PATTERN = re.compile(
    r"(?<!\w)(?:\.{1,2}/|\.[A-Za-z0-9_-]+/|/)"
    r"[A-Za-z0-9._~@%+:-]+(?:/[A-Za-z0-9._~@%+:-]+)*"
)
HASH_PATTERN = re.compile(r"\b[0-9a-fA-F]{16,}\b")
EXACT_MARKERS = ("exatamente", "literalmente", "exact", "literal", "verbatim", "raw")


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
    preserve_identity: bool
    language_hint: str


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    kind: str
    text: str
    rendering: str
    source: str
    priority: int
    preserve_identity: bool = True
    language_hint: str = "pt-BR"
    exact_mode: bool = False
    redacted: bool = False
    executable: bool = False


def canonical(value: str) -> str:
    return unicodedata.normalize("NFC", value.strip()).casefold()


def is_phrase(term: str) -> bool:
    return any(char.isspace() for char in term) or "/" in term or ":" in term


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def redact_secret_like_values(source_text: str) -> tuple[str, list[dict[str, str]]]:
    redactions: list[dict[str, str]] = []

    def split_trailing_punctuation(value: str) -> tuple[str, str]:
        if len(value) > 1 and value[-1] in ".,;:!?)":
            return value[:-1], value[-1]
        return value, ""

    def replace_secret(match: re.Match[str]) -> str:
        value, trailing = split_trailing_punctuation(match.group(1))
        redactions.append({"kind": "secret", "value": value})
        prefix = match.group(0)[: match.start(1) - match.start(0)]
        return prefix + REDACTION_TOKEN + trailing

    redacted = SECRET_PATTERN.sub(replace_secret, source_text)

    def replace_bearer(match: re.Match[str]) -> str:
        value, trailing = split_trailing_punctuation(match.group(1))
        redactions.append({"kind": "bearer", "value": value})
        return "Bearer " + REDACTION_TOKEN + trailing

    redacted = BEARER_SECRET_PATTERN.sub(replace_bearer, redacted)
    return redacted, redactions


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
                preserve_identity=True,
                language_hint=record.get("language", "pt-BR"),
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
                preserve_identity=bool(record.get("preserve_written_identity", True)),
                language_hint=record.get("language_hint", record.get("default_language", "pt-BR")),
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
                    preserve_identity=True,
                    language_hint=locale,
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
    return {"exact": exact, "phrase": phrase, "duplicates": duplicates, "entry_count": len(entries)}


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
                redacted=True,
            )
        )
    for match in INLINE_CODE_PATTERN.finditer(redacted_text):
        content = match.group(1)
        exact_mode = has_exact_marker_before(redacted_text, match.start())
        spans.append(
            Span(
                start=match.start(),
                end=match.end(),
                kind="exact_island" if exact_mode else "code",
                text=content,
                rendering=content,
                source="inline_code",
                priority=900 if exact_mode else 850,
                exact_mode=exact_mode,
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
                preserve_identity=False,
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
                preserve_identity=False,
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
    entries.sort(key=entry_sort_key)
    for entry in entries:
        if not entry.spoken_rendering:
            continue
        pattern = re.compile(rf"(?<![\w/-]){re.escape(entry.term)}(?![\w/-])", re.IGNORECASE)
        for match in pattern.finditer(redacted_text):
            if redacted_text[match.end() :].startswith("=" + REDACTION_TOKEN):
                continue
            if entry.source == "pronunciation_catalog" and " --" in entry.term:
                kind = "command"
            else:
                kind = "protected_phrase" if entry.match_scope == "phrase" else "protected_term"
            spans.append(
                Span(
                    start=match.start(),
                    end=match.end(),
                    kind=kind,
                    text=match.group(0),
                    rendering=entry.spoken_rendering,
                    source=entry.source,
                    priority=entry.priority + (250 if kind == "protected_phrase" else 0),
                    preserve_identity=entry.preserve_identity,
                    language_hint=entry.language_hint,
                )
            )
    return spans


def overlaps(span: Span, accepted: list[Span]) -> bool:
    return any(span.start < existing.end and existing.start < span.end for existing in accepted)


def match_spans(source_text: str, locale: str = "pt-BR") -> dict[str, Any]:
    redacted_text, redactions = redact_secret_like_values(source_text)
    index = compile_index()
    candidates = literal_spans(redacted_text)
    candidates.extend(protected_spans(redacted_text, locale, index))
    candidates.sort(key=lambda span: (-span.priority, -(span.end - span.start), span.start))

    accepted: list[Span] = []
    for span in candidates:
        if not overlaps(span, accepted):
            accepted.append(span)
    accepted.sort(key=lambda span: span.start)

    return {
        "redacted_text": redacted_text,
        "redaction_count": len(redactions),
        "spans": accepted,
    }


def span_to_ir(span: Span) -> dict[str, Any]:
    say_as = {
        "secret": "redacted",
        "url": "alias",
        "path": "alias",
        "hash": "literal",
        "code": "literal_text",
        "exact_island": "literal",
        "command": "literal_text",
        "protected_phrase": "protected_alias",
        "protected_term": "protected_alias",
    }.get(span.kind, "text")
    return {
        "start": span.start,
        "end": span.end,
        "span_type": span.kind,
        "source": span.text,
        "spoken_alias": span.rendering,
        "language_hint": span.language_hint,
        "preserve_identity": span.preserve_identity,
        "say_as": say_as,
        "exact_mode": span.exact_mode,
        "redacted": span.redacted,
        "executable": False,
    }


def prepare_spoken_text(source_text: str, locale: str = "pt-BR") -> dict[str, Any]:
    match_result = match_spans(source_text, locale)
    redacted_text = match_result["redacted_text"]
    spans: list[Span] = match_result["spans"]
    memo: dict[str, str] = {}
    parts: list[str] = []
    cursor = 0
    hits = 0
    misses = 0
    for span in spans:
        key = f"{span.kind}:{span.text}->{span.rendering}"
        if key in memo:
            hits += 1
            rendering = memo[key]
        else:
            misses += 1
            rendering = span.rendering
            memo[key] = rendering
        parts.append(redacted_text[cursor : span.start])
        parts.append(rendering)
        cursor = span.end
    parts.append(redacted_text[cursor:])
    spoken_text = "".join(parts).replace("`", "")
    return {
        "version": VERSION,
        "locale": locale,
        "source_text_immutable": True,
        "redacted_text": redacted_text,
        "spoken_text": spoken_text,
        "ir": [span_to_ir(span) for span in spans],
        "span_kinds": [span.kind for span in spans],
        "redaction_count": match_result["redaction_count"],
        "memo_scope": "request_local",
        "cache_hits": hits,
        "cache_misses": misses,
        "provider_timing": "out_of_scope",
        "output_format": "plain_text",
        "summary_behavior": "none",
        "command_execution": "not_performed",
        "runtime_pronunciation_output": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare TES TTS spoken text and IR.")
    parser.add_argument("--text", required=True)
    parser.add_argument("--locale", default="pt-BR")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    result = prepare_spoken_text(args.text, args.locale)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
