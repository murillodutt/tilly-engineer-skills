"""Shared TES TTS runtime types and constants."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
LEXICAL_MANIFEST_PATH = ROOT / "benchmarks/tes-tts/ptbr-lexical-sample.jsonl"
PRONUNCIATION_CATALOG_PATH = ROOT / "benchmarks/tes-tts/pronunciation-catalog-fixtures.json"
RUNTIME_LATENCY_FIXTURE_PATH = ROOT / "benchmarks/tes-tts/runtime-latency-fixtures.json"
VERSION = "0.3.151"
REDACTION_TOKEN = "[REDACTED_SECRET]"


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


SPAN_TYPE_CATALOG: dict[str, dict[str, str]] = {
    "secret": {"say_as": "redacted", "runtime_class": "privacy"},
    "url": {"say_as": "alias", "runtime_class": "fragile_reference"},
    "path": {"say_as": "alias", "runtime_class": "fragile_reference"},
    "email": {"say_as": "alias", "runtime_class": "contact_reference"},
    "ipv4": {"say_as": "alias", "runtime_class": "network_reference"},
    "guid": {"say_as": "alias", "runtime_class": "identifier"},
    "mention": {"say_as": "alias", "runtime_class": "social_reference"},
    "hashtag": {"say_as": "alias", "runtime_class": "social_reference"},
    "branch": {"say_as": "alias", "runtime_class": "vcs_reference"},
    "scoped_package": {"say_as": "protected_identity", "runtime_class": "package_identity"},
    "model": {"say_as": "protected_identity", "runtime_class": "model_identity"},
    "hash": {"say_as": "literal", "runtime_class": "identifier"},
    "code": {"say_as": "literal_text", "runtime_class": "code_text"},
    "exact_island": {"say_as": "literal", "runtime_class": "exact_text"},
    "command": {"say_as": "literal_text", "runtime_class": "code_text"},
    "protected_phrase": {"say_as": "protected_alias", "runtime_class": "lexical_identity"},
    "protected_term": {"say_as": "protected_alias", "runtime_class": "lexical_identity"},
}


def canonical(value: str) -> str:
    return unicodedata.normalize("NFC", value.strip()).casefold()


def is_phrase(term: str) -> bool:
    return any(char.isspace() for char in term) or "/" in term or ":" in term


def entry_sort_key(entry: IndexEntry) -> tuple[int, int, int]:
    return (-entry.priority, -len(entry.term), entry.insertion_order)
