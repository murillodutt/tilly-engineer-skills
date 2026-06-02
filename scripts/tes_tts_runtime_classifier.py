"""TES TTS runtime classifier.

Classifies source text into request-local IR spans while preserving source text
and redacting secrets before speech preparation.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
import re
from typing import Any

from tes_tts_runtime_types import (
    LEXICAL_MANIFEST_PATH,
    PRONUNCIATION_CATALOG_PATH,
    REDACTION_TOKEN,
    RUNTIME_LATENCY_FIXTURE_PATH,
    SPAN_TYPE_CATALOG,
    VERSION,
    IndexEntry,
    Span,
    canonical,
    entry_sort_key,
    is_phrase,
)


SECRET_PATTERN = re.compile(
    r"(?i)(?<![\w-])[\w-]*"
    r"(?:api_?key|access_?key|secret|token|password|passwd|pwd|\bkey)="
    r"(\S+)"
)
PREFIX_SECRET_PATTERN = re.compile(
    r"(?<![\w-])("
    r"sk-[A-Za-z0-9-]{6,}|gh[pousr]_[A-Za-z0-9]{8,}|"
    r"github_pat_[A-Za-z0-9_]{8,}|AKIA[0-9A-Z]{12,}"
    r")"
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
GUID_PATTERN = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
IPV4_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
SCOPED_PACKAGE_PATTERN = re.compile(r"(?<![\w/])@[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\b")
MENTION_PATTERN = re.compile(r"(?<![\w/.-])@([A-Za-z0-9_.-]{2,})\b")
HASHTAG_PATTERN = re.compile(r"(?<!\w)#([A-Za-z0-9_-]{2,})\b")
BRANCH_PATTERN = re.compile(r"\b(?:feature|fix|bugfix|hotfix|release|chore)/[A-Za-z0-9._-]+\b")
MODEL_PATTERN = re.compile(r"\b(?:gpt|gemini|claude|llama|mistral)-[A-Za-z0-9._-]+\b", re.IGNORECASE)
EXACT_MARKERS = ("exatamente", "literalmente", "exact", "literal", "verbatim", "raw")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def split_trailing_punctuation(value: str) -> tuple[str, str]:
    if len(value) > 1 and value[-1] in ".,;:!?)":
        return value[:-1], value[-1]
    return value, ""


def redact_secret_like_values(source_text: str) -> tuple[str, list[dict[str, str]]]:
    redactions: list[dict[str, str]] = []

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

    def replace_prefix(match: re.Match[str]) -> str:
        value, trailing = split_trailing_punctuation(match.group(1))
        redactions.append({"kind": "secret", "value": value})
        return REDACTION_TOKEN + trailing

    redacted = PREFIX_SECRET_PATTERN.sub(replace_prefix, redacted)
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


def compile_protected_matchers(
    exact: dict[str, dict[str, IndexEntry]],
    phrase: dict[str, list[IndexEntry]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    matchers: dict[str, dict[str, Any]] = {}
    strategies: dict[str, dict[str, Any]] = {}
    locales = sorted(set(exact) | set(phrase))
    for locale in locales:
        entries = list(phrase.get(locale, []))
        entries.extend(exact.get(locale, {}).values())
        entries = [entry for entry in entries if entry.spoken_rendering]
        entries.sort(key=lambda entry: (-len(entry.term), -entry.priority, entry.insertion_order))

        entries_by_key: dict[str, IndexEntry] = {}
        alternatives: list[str] = []
        for entry in entries:
            key = canonical(entry.term)
            if key in entries_by_key:
                continue
            entries_by_key[key] = entry
            alternatives.append(re.escape(entry.term))

        entry_count = len(alternatives)
        strategy = {
            "strategy": "regex_union" if entry_count else "empty",
            "runtime_dependency": "none",
            "entry_count": entry_count,
            "trie_recommended": entry_count >= 128,
            "aho_corasick_recommended": entry_count >= 512,
        }
        strategies[locale] = strategy
        if entry_count:
            pattern = re.compile(r"(?<![\w/-])(?:" + "|".join(alternatives) + r")(?![\w/-])", re.IGNORECASE)
            matchers[locale] = {
                "pattern": pattern,
                "entries_by_key": entries_by_key,
            }
    return matchers, strategies


@lru_cache(maxsize=1)
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
    protected_matchers, index_strategy = compile_protected_matchers(exact, phrase)
    return {
        "exact": exact,
        "phrase": phrase,
        "duplicates": duplicates,
        "entry_count": len(entries),
        "protected_matchers": protected_matchers,
        "index_strategy": index_strategy,
    }


def has_exact_marker_before(text: str, start: int) -> bool:
    prefix = text[max(0, start - 40) : start].casefold()
    return any(marker in prefix for marker in EXACT_MARKERS)


def has_label_before(text: str, start: int, labels: tuple[str, ...]) -> bool:
    prefix = text[max(0, start - 30) : start].casefold().rstrip()
    return any(prefix.endswith(label.casefold()) for label in labels)


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
    for match in EMAIL_PATTERN.finditer(redacted_text):
        email = match.group(0).rstrip(".,;")
        local, domain = email.split("@", 1)
        rendering = "email " + re.sub(r"[._%+-]+", " ", local).strip()
        rendering += " em " + re.sub(r"[.-]+", " ", domain).strip()
        spans.append(
            Span(
                start=match.start(),
                end=match.start() + len(email),
                kind="email",
                text=email,
                rendering=rendering,
                source="email_regex",
                priority=795,
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
    for match in SCOPED_PACKAGE_PATTERN.finditer(redacted_text):
        package = match.group(0).rstrip(".,;")
        spans.append(
            Span(
                start=match.start(),
                end=match.start() + len(package),
                kind="scoped_package",
                text=package,
                rendering=package,
                source="scoped_package_regex",
                priority=760,
            )
        )
    for match in MODEL_PATTERN.finditer(redacted_text):
        model = match.group(0).rstrip(".,;")
        spans.append(
            Span(
                start=match.start(),
                end=match.start() + len(model),
                kind="model",
                text=model,
                rendering=model,
                source="model_regex",
                priority=740,
            )
        )
    for match in BRANCH_PATTERN.finditer(redacted_text):
        branch = match.group(0).rstrip(".,;")
        branch_name = re.sub(r"[/_-]+", " ", branch).strip()
        label_present = has_label_before(redacted_text, match.start(), ("branch", "ramo"))
        spans.append(
            Span(
                start=match.start(),
                end=match.start() + len(branch),
                kind="branch",
                text=branch,
                rendering=branch_name if label_present else f"branch {branch_name}",
                source="branch_regex",
                priority=730,
                preserve_identity=False,
            )
        )
    for match in GUID_PATTERN.finditer(redacted_text):
        label_present = has_label_before(redacted_text, match.start(), ("guid",))
        spans.append(
            Span(
                start=match.start(),
                end=match.end(),
                kind="guid",
                text=match.group(0),
                rendering="identificador" if label_present else "GUID",
                source="guid_regex",
                priority=720,
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
    for match in IPV4_PATTERN.finditer(redacted_text):
        ip_address = match.group(0)
        if all(0 <= int(part) <= 255 for part in ip_address.split(".")):
            label_present = has_label_before(redacted_text, match.start(), ("ip",))
            rendered_ip = " ponto ".join(ip_address.split("."))
            spans.append(
                Span(
                    start=match.start(),
                    end=match.end(),
                    kind="ipv4",
                    text=ip_address,
                    rendering=rendered_ip if label_present else "IP " + rendered_ip,
                    source="ipv4_regex",
                    priority=690,
                    preserve_identity=False,
                )
            )
    for match in MENTION_PATTERN.finditer(redacted_text):
        mention = match.group(0)
        rendering = "mencao " + re.sub(r"[_.-]+", " ", match.group(1)).strip()
        spans.append(
            Span(
                start=match.start(),
                end=match.end(),
                kind="mention",
                text=mention,
                rendering=rendering,
                source="mention_regex",
                priority=660,
                preserve_identity=False,
            )
        )
    for match in HASHTAG_PATTERN.finditer(redacted_text):
        hashtag = match.group(0)
        label_present = has_label_before(redacted_text, match.start(), ("hashtag",))
        normalized_hashtag = re.sub(r"[_-]+", " ", match.group(1)).strip()
        rendering = normalized_hashtag if label_present else "hashtag " + normalized_hashtag
        spans.append(
            Span(
                start=match.start(),
                end=match.end(),
                kind="hashtag",
                text=hashtag,
                rendering=rendering,
                source="hashtag_regex",
                priority=650,
                preserve_identity=False,
            )
        )
    return spans


def protected_spans(redacted_text: str, locale: str, index: dict[str, Any]) -> list[Span]:
    spans: list[Span] = []
    matcher = index.get("protected_matchers", {}).get(locale)
    if not matcher:
        return spans
    pattern = matcher["pattern"]
    entries_by_key = matcher["entries_by_key"]
    for match in pattern.finditer(redacted_text):
        entry = entries_by_key.get(canonical(match.group(0)))
        if entry is None:
            continue
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
        "index_strategy": index.get(
            "index_strategy",
            {},
        ).get(
            locale,
            {
                "strategy": "empty",
                "runtime_dependency": "none",
                "entry_count": 0,
                "trie_recommended": False,
                "aho_corasick_recommended": False,
            },
        ),
    }


def span_to_ir(span: Span) -> dict[str, Any]:
    catalog_entry = SPAN_TYPE_CATALOG.get(span.kind, {"say_as": "text", "runtime_class": "text"})
    return {
        "start": span.start,
        "end": span.end,
        "span_type": span.kind,
        "source": span.text,
        "spoken_alias": span.rendering,
        "language_hint": span.language_hint,
        "preserve_identity": span.preserve_identity,
        "say_as": catalog_entry["say_as"],
        "runtime_class": catalog_entry["runtime_class"],
        "exact_mode": span.exact_mode,
        "redacted": span.redacted,
        "executable": False,
    }


def classify_text(source_text: str, locale: str = "pt-BR") -> dict[str, Any]:
    match_result = match_spans(source_text, locale)
    spans: list[Span] = match_result["spans"]
    return {
        "version": VERSION,
        "locale": locale,
        "source_text_immutable": True,
        "redacted_text": match_result["redacted_text"],
        "ir": [span_to_ir(span) for span in spans],
        "span_kinds": [span.kind for span in spans],
        "redaction_count": match_result["redaction_count"],
        "index_strategy": match_result["index_strategy"],
        "provider_timing": "out_of_scope",
        "summary_behavior": "none",
        "command_execution": "not_performed",
    }
