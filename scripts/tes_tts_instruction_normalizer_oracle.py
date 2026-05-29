#!/usr/bin/env python3
"""Self-test instruction-level TES TTS normalization without providers."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "benchmarks/tes-tts/instruction-normalizer-fixtures.json"
NORMALIZATION_FIXTURE_PATH = ROOT / "benchmarks/tes-tts/normalization-fixtures.json"
VERSION = "0.3.147"

SECRET_PATTERN = re.compile(
    r"\b(?:api_key|token|password|secret|[A-Z][A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD))="
    r"([A-Za-z0-9_./:+-]+)"
)
BEARER_SECRET_PATTERN = re.compile(r"\bBearer\s+([A-Za-z0-9._:+/-]{8,})")
REDACTION_TOKEN = "[REDACTED_SECRET]"
REQUIRED_CACHE_KEYS = {
    "source_span",
    "detected_language",
    "target_language",
    "normalized_text",
    "spoken_text",
    "exact_terms",
    "preserved_terms",
    "pronunciation_hints",
    "redactions",
}
FIRST_CLASS_LANGUAGES = {"pt-BR", "en", "es", "fr", "it", "de", "he"}
LETTER_SPELLED_TERMS = {
    "ADR",
    "MCP",
    "API",
    "SDK",
    "CLI",
    "URL",
    "HTTP",
    "TTS",
    "LLM",
    "AI",
    "CI",
    "CD",
    "PR",
}
TECHNICAL_NOUN_TERMS = {"SPEC"}
COMMON_LOCAL_PRONUNCIATION_TERMS = {"JSON", "YAML", "SQL"}
PROPER_NOUN_TERMS = {"TES", "Tilly", "Codex", "Claude", "Cursor", "OpenAI"}
ENGLISH_PRONUNCIATION_TERMS = {
    "GitHub",
    "Markdown",
    "provider",
    "fallback",
    "cache",
    "prompt",
    "workflow",
    "pipeline",
    "branch",
    "commit",
    "release",
    "sync",
    "tag",
    "push",
    "pull request",
    "merge",
    "runtime",
    "fixture",
    "oracle",
    "adapter",
    "workbench",
    "rollback",
    "checkpoint",
    "canary",
    "debug",
    "build",
    "test",
    "deploy",
    "review",
    "diff",
    "patch",
    "issue",
    "milestone",
    "sprint",
    "backlog",
    "standup",
    "roadmap",
    "release candidate",
    "hotfix",
    "merge conflict",
    "rebase",
    "cherry-pick",
    "fork",
    "upstream",
    "origin",
    "main",
    "workspace",
    "worktree",
    "sandbox",
    "hook",
    "lint",
    "formatter",
    "CI",
    "CD",
    "GitHub Actions",
    "Docker",
    "Kubernetes",
    "Node.js",
    "TypeScript",
    "Playwright",
    "MCP server",
    "OpenAI",
    "Claude Code",
    "Cursor",
    "Codex",
    "ChatGPT",
    "ElevenLabs",
}
ACRONYM_PATTERN = re.compile(r"\b(ADR|MCP|API|SDK|CLI|URL|HTTP|TTS|LLM|AI|CI|CD|PR)(?:-(\d+))?\b")
URL_PATTERN = re.compile(r"https?://[^\s)\]]+")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
IPV4_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
GUID_PATTERN = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
LONG_HASH_PATTERN = re.compile(r"\b[0-9a-fA-F]{16,}\b")
MENTION_PATTERN = re.compile(r"(?<![\w.])@([A-Za-z0-9_][A-Za-z0-9_.-]{0,63})\b")
HASHTAG_PATTERN = re.compile(r"(?<![\w])#([A-Za-z0-9_][A-Za-z0-9_-]{0,63})\b")
SCOPED_PACKAGE_PATTERN = re.compile(
    r"(?<!\w)@[A-Za-z0-9_-]+/[A-Za-z0-9._~@%+:-]+"
)
PATH_PATTERN = re.compile(
    r"(?<!\w)(?:\.{1,2}/|\.[A-Za-z0-9_-]+/|/)"
    r"[A-Za-z0-9._~@%+:-]+(?:/[A-Za-z0-9._~@%+:-]+)*"
)
EXACT_READ_PATTERNS = (
    "exact",
    "verbatim",
    "literal",
    "raw",
    "exatamente",
    "literalmente",
    "sem alterar",
    "sem modificar",
    "preserve o path",
    "preserve the path",
)
FORBIDDEN_HINT_CLAIMS = {
    "ipa",
    "ssml",
    "phoneme",
    "phonetic",
    "provider-backed",
    "translate",
    "translation",
}


@dataclass(frozen=True)
class PreparedSpeech:
    cache: list[dict[str, Any]]
    speech_text: str
    translation_plan: dict[str, Any]
    pronunciation_plan: dict[str, Any]


def load_fixtures() -> list[dict[str, Any]]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def load_normalization_fixtures() -> list[dict[str, Any]]:
    return json.loads(NORMALIZATION_FIXTURE_PATH.read_text(encoding="utf-8"))


def redact_secret_like_values(text: str) -> tuple[str, list[str]]:
    redactions: list[str] = []

    def replace(match: re.Match[str]) -> str:
        redactions.append(match.group(0))
        return match.group(0).split("=", 1)[0] + "=" + REDACTION_TOKEN

    redacted = SECRET_PATTERN.sub(replace, text)

    def replace_bearer(match: re.Match[str]) -> str:
        redactions.append(match.group(0))
        return "Bearer " + REDACTION_TOKEN

    return BEARER_SECRET_PATTERN.sub(replace_bearer, redacted), redactions


def chunk_without_summary(text: str, max_chars: int) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) > max_chars and current:
            chunks.append(current)
            current = word
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def clean_markdown_for_speech(text: str) -> str:
    cleaned = text
    cleaned = re.sub(r"```[A-Za-z0-9_-]*\n?", "", cleaned)
    cleaned = cleaned.replace("```", "")
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"\1 \2", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 \2", cleaned)
    cleaned = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", cleaned)
    cleaned = re.sub(r"(?m)^\s*[-*+]\s+", "", cleaned)
    cleaned = re.sub(r"(?m)^\s*\d+[.)]\s+", "", cleaned)
    cleaned = re.sub(r"(?<!\w)[*_]{1,3}([^*_]+)[*_]{1,3}(?!\w)", r"\1", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def rendering_intent(fixture: dict[str, Any]) -> str:
    intent = fixture.get("rendering_intent")
    if intent in {"conversational", "faithful_reading"}:
        return intent
    source = fixture["source_text"].lower()
    if wants_exact_reading(source) or "leia fielmente" in source or "read faithfully" in source:
        return "faithful_reading"
    return "faithful_reading"


def parse_markdown_table(lines: list[str], start: int) -> tuple[list[str], int] | None:
    table_lines: list[str] = []
    index = start
    while index < len(lines) and lines[index].strip().startswith("|"):
        table_lines.append(lines[index].strip())
        index += 1
    if len(table_lines) < 3:
        return None
    rows = [
        [cell.strip() for cell in line.strip("|").split("|")]
        for line in table_lines
        if not re.fullmatch(r"\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?", line)
    ]
    if len(rows) < 2:
        return None
    headers = rows[0]
    rendered: list[str] = []
    for row in rows[1:]:
        if len(row) != len(headers):
            continue
        if len(row) == 2:
            rendered.append(f"{headers[0]} {row[0]}: {headers[1]} {row[1]}.")
        else:
            pairs = ", ".join(f"{header} {value}" for header, value in zip(headers, row))
            rendered.append(pairs + ".")
    return rendered, index


def conversational_connector(index: int, total: int) -> str:
    if index == 0:
        return "Primeiro"
    if index == total - 1:
        return "Por fim"
    return "Depois"


def render_conversational_structure(text: str) -> str:
    lines = text.splitlines()
    rendered: list[str] = []
    list_lines = [
        line for line in lines if re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", line)
    ]
    list_total = len(list_lines)
    list_index = 0
    index = 0
    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        if not stripped:
            index += 1
            continue
        table = parse_markdown_table(lines, index)
        if table is not None:
            table_rendered, next_index = table
            rendered.extend(table_rendered)
            index = next_index
            continue
        heading = re.match(r"^#{1,6}\s+(.+)$", stripped)
        if heading:
            rendered.append(heading.group(1).rstrip(".") + ".")
            index += 1
            continue
        if re.fullmatch(r"`{3}[A-Za-z0-9_-]*", stripped):
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and lines[index].strip() != "```":
                code_line = lines[index].strip()
                if code_line:
                    code_lines.append(code_line)
                index += 1
            if index < len(lines) and lines[index].strip() == "```":
                index += 1
            if code_lines:
                rendered.append("Bloco de codigo: " + " ".join(code_lines).rstrip(".") + ".")
            continue
        if stripped == "```":
            index += 1
            continue
        quote = re.match(r"^>\s*(.+)$", stripped)
        if quote:
            quote_lines = [quote.group(1).strip()]
            index += 1
            while index < len(lines):
                next_quote = re.match(r"^>\s*(.+)$", lines[index].strip())
                if not next_quote:
                    break
                quote_lines.append(next_quote.group(1).strip())
                index += 1
            rendered.append("Citacao: " + " ".join(quote_lines).rstrip(".") + ".")
            continue
        bullet = re.match(r"^[-*+]\s+(.+)$", stripped)
        if bullet:
            text_part = bullet.group(1).rstrip(".")
            connector = conversational_connector(list_index, list_total)
            rendered.append(f"{connector}, {text_part}.")
            list_index += 1
            index += 1
            continue
        numbered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if numbered:
            text_part = numbered.group(1).rstrip(".")
            connector = conversational_connector(list_index, list_total)
            rendered.append(f"{connector}, {text_part}.")
            list_index += 1
            index += 1
            continue
        rendered.append(stripped)
        index += 1
    return " ".join(rendered)


def wants_exact_reading(text: str) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in EXACT_READ_PATTERNS)


def spell_letters(term: str) -> str:
    return " ".join(term)


def render_acronym(match: re.Match[str]) -> str:
    term = match.group(1)
    suffix = match.group(2)
    rendered = spell_letters(term)
    if suffix:
        return f"{rendered} {suffix}"
    return rendered


def render_url_for_speech(url: str, exact_read: bool) -> str:
    if exact_read:
        return url
    if "github.com" in url.lower():
        return "pagina do GitHub"
    return "link"


def render_url_match_for_speech(url: str, exact_terms: set[str], global_exact: bool) -> str:
    trailing = ""
    while url and url[-1] in ".,;:!?":
        trailing = url[-1] + trailing
        url = url[:-1]
    return render_url_for_speech(url, should_keep_exact(url, exact_terms, global_exact)) + trailing


def render_path_for_speech(path: str, exact_read: bool) -> str:
    if exact_read:
        return path
    name = path.rstrip("/").split("/")[-1]
    spoken_name = re.sub(r"[-_]+", " ", name)
    if "." in name and not name.startswith("."):
        return f"arquivo {spoken_name}"
    return f"pasta {spoken_name}"


def render_email_for_speech(email: str, exact_read: bool) -> str:
    if exact_read:
        return email
    local, domain = email.split("@", 1)
    local_name = re.sub(r"[._%+-]+", " ", local).strip()
    domain_name = re.sub(r"[.-]+", " ", domain).strip()
    if local_name and domain_name:
        return f"email {local_name} em {domain_name}"
    return "email"


def is_valid_ipv4(candidate: str) -> bool:
    return all(0 <= int(part) <= 255 for part in candidate.split("."))


def render_ipv4_for_speech(ip_address: str, exact_read: bool) -> str:
    if exact_read or not is_valid_ipv4(ip_address):
        return ip_address
    return "IP " + " ponto ".join(ip_address.split("."))


def render_identifier_for_speech(identifier: str, exact_read: bool, label: str) -> str:
    if exact_read:
        return identifier
    return label


def render_mention_for_speech(match: re.Match[str], exact_read: bool) -> str:
    if exact_read:
        return match.group(0)
    return "mencao " + re.sub(r"[_.-]+", " ", match.group(1)).strip()


def render_hashtag_for_speech(match: re.Match[str], exact_read: bool) -> str:
    if exact_read:
        return match.group(0)
    return "hashtag " + re.sub(r"[_-]+", " ", match.group(1)).strip()


def should_keep_exact(candidate: str, exact_terms: set[str], global_exact: bool) -> bool:
    return global_exact or candidate in exact_terms


def render_spoken_text(
    text: str,
    source_text: str,
    exact_terms: set[str] | None = None,
) -> str:
    explicit_exact_terms = exact_terms if exact_terms is not None else set()
    global_exact = wants_exact_reading(source_text) and exact_terms is None
    rendered_spans: list[str] = []

    def stash(rendered: str) -> str:
        rendered_spans.append(rendered)
        return f"__TES_TTS_SPAN_{len(rendered_spans) - 1}__"

    def is_exact(candidate: str) -> bool:
        return should_keep_exact(candidate, explicit_exact_terms, global_exact)

    spoken = URL_PATTERN.sub(
        lambda match: stash(
            render_url_match_for_speech(match.group(0), explicit_exact_terms, global_exact)
        ),
        text,
    )
    spoken = EMAIL_PATTERN.sub(
        lambda match: stash(render_email_for_speech(match.group(0), is_exact(match.group(0)))),
        spoken,
    )
    spoken = IPV4_PATTERN.sub(
        lambda match: stash(render_ipv4_for_speech(match.group(0), is_exact(match.group(0)))),
        spoken,
    )
    spoken = GUID_PATTERN.sub(
        lambda match: stash(
            render_identifier_for_speech(match.group(0), is_exact(match.group(0)), "GUID")
        ),
        spoken,
    )
    spoken = LONG_HASH_PATTERN.sub(
        lambda match: stash(
            render_identifier_for_speech(match.group(0), is_exact(match.group(0)), "hash")
        ),
        spoken,
    )
    spoken = SCOPED_PACKAGE_PATTERN.sub(lambda match: stash(match.group(0)), spoken)
    spoken = PATH_PATTERN.sub(
        lambda match: stash(render_path_for_speech(match.group(0), is_exact(match.group(0)))),
        spoken,
    )
    spoken = MENTION_PATTERN.sub(
        lambda match: stash(render_mention_for_speech(match, is_exact(match.group(0)))),
        spoken,
    )
    spoken = HASHTAG_PATTERN.sub(
        lambda match: stash(render_hashtag_for_speech(match, is_exact(match.group(0)))),
        spoken,
    )
    if not global_exact:
        spoken = ACRONYM_PATTERN.sub(
            lambda match: match.group(0)
            if match.group(0) in explicit_exact_terms
            else render_acronym(match),
            spoken,
        )

    for index, rendered in enumerate(rendered_spans):
        spoken = spoken.replace(f"__TES_TTS_SPAN_{index}__", rendered)
    return re.sub(r"\s+", " ", spoken).strip()


def pronunciation_hint(term: str) -> str:
    if term in LETTER_SPELLED_TERMS:
        return f"{term} -> spell letters"
    if term in TECHNICAL_NOUN_TERMS:
        return "SPEC -> read as technical noun"
    if term in COMMON_LOCAL_PRONUNCIATION_TERMS:
        return f"{term} -> common local pronunciation"
    if term in ENGLISH_PRONUNCIATION_TERMS:
        return f"{term} -> preserve English pronunciation"
    if term in PROPER_NOUN_TERMS:
        return f"{term} -> preserve proper noun"
    if " --" in term or term.startswith("tes "):
        return f"{term} -> preserve command exactly"
    if "/" in term:
        return f"{term} -> preserve path exactly"
    if re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*\b", term):
        return f"{term} -> preserve code identifier exactly"
    if "_" in term and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", term):
        return f"{term} -> preserve code identifier exactly"
    if term.startswith("@") or re.search(r"[A-Za-z]+[-_][A-Za-z0-9]", term):
        return f"{term} -> preserve package or model identity"
    return f"{term} -> preserve written identity"


def pronunciation_hints(terms: list[str]) -> list[str]:
    return [pronunciation_hint(term) for term in terms]


def plan_optional_translation(
    fixture: dict[str, Any],
    redacted_text: str,
    protected_terms: list[str],
) -> dict[str, Any]:
    provider_state = fixture.get("translation_provider_state", "provider_not_available")
    language_pair_state = fixture.get("language_pair_state", "unknown")
    status = (
        "translation_ready"
        if provider_state == "provider_available" and language_pair_state == "available"
        else "normalization_degraded"
    )
    return {
        "mode": "speech_preparation_only",
        "status": status,
        "provider_state": provider_state,
        "language_pair_state": language_pair_state,
        "source_text_unchanged": fixture["source_text"],
        "redacted_text": redacted_text,
        "detected_language": fixture["detected_language"],
        "target_language": fixture["target_language"],
        "protected_terms": protected_terms,
        "actions": [
            "redaction_before_translation",
            "protected_terms_before_translation",
            "span_level_translation_only",
            "no_summary",
            "preserve_source_text",
        ],
    }


def plan_optional_pronunciation(
    fixture: dict[str, Any],
    protected_terms: list[str],
) -> dict[str, Any]:
    provider_state = fixture.get("pronunciation_provider_state", "provider_not_available")
    language_support_state = fixture.get("pronunciation_language_state", "unknown")
    status = "normalization_degraded"
    return {
        "mode": "instruction_hints_baseline",
        "status": status,
        "provider_state": provider_state,
        "language_support_state": language_support_state,
        "target_language": fixture["target_language"],
        "protected_terms": protected_terms,
        "emitted_outputs": ["instruction_level_hints"],
        "blocked_outputs": [
            "ipa",
            "ssml",
            "phoneme",
            "lexicon",
            "provider_backed_pronunciation",
        ],
        "hebrew_posture": "degraded" if fixture["target_language"] == "he" else "not_applicable",
    }


def select_target_language(selector: dict[str, str]) -> str:
    explicit = selector["explicit_user_language"]
    if explicit in FIRST_CLASS_LANGUAGES:
        return explicit

    declared = selector["declared_adapter_default"]
    if declared in FIRST_CLASS_LANGUAGES:
        return declared

    if selector["active_adapter"] == "cursor":
        codex_default = selector["codex_default"]
        if codex_default in FIRST_CLASS_LANGUAGES:
            return codex_default
        claude_default = selector["claude_default"]
        if claude_default in FIRST_CLASS_LANGUAGES:
            return claude_default

    request_language = selector["request_language"]
    if request_language in FIRST_CLASS_LANGUAGES:
        return request_language

    dominant_text_language = selector["dominant_text_language"]
    if dominant_text_language in FIRST_CLASS_LANGUAGES:
        return dominant_text_language

    return "preserve_original"


def prepare_instruction_level_speech(fixture: dict[str, Any]) -> PreparedSpeech:
    redacted_text, redactions = redact_secret_like_values(fixture["source_text"])
    intent = rendering_intent(fixture)
    intent_text = (
        render_conversational_structure(redacted_text)
        if intent == "conversational"
        else redacted_text
    )
    cleaned_text = clean_markdown_for_speech(intent_text)
    chunks = chunk_without_summary(cleaned_text, fixture["max_chunk_chars"])
    protected_terms = fixture["protected_terms"]
    exact_terms = set(fixture["exact_terms"]) if "exact_terms" in fixture else None
    translation_plan = plan_optional_translation(fixture, redacted_text, protected_terms)
    pronunciation_plan = plan_optional_pronunciation(fixture, protected_terms)
    cache = [
        {
            "source_span": chunk,
            "detected_language": fixture["detected_language"],
            "target_language": fixture["target_language"],
            "normalized_text": chunk,
            "spoken_text": render_spoken_text(chunk, fixture["source_text"], exact_terms),
            "exact_terms": sorted(exact_terms) if exact_terms is not None else [],
            "preserved_terms": [term for term in protected_terms if term in chunk],
            "pronunciation_hints": pronunciation_hints([term for term in protected_terms if term in chunk]),
            "redactions": redactions,
            "rendering_intent": intent,
        }
        for chunk in chunks
    ]
    return PreparedSpeech(
        cache=cache,
        speech_text=" ".join(entry["spoken_text"] for entry in cache),
        translation_plan=translation_plan,
        pronunciation_plan=pronunciation_plan,
    )


def validate_fixture_shape(fixture: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    required = {
        "id",
        "target_language",
        "detected_language",
        "source_text",
        "protected_terms",
        "expected_redactions",
        "forbidden_terms",
        "max_chunk_chars",
        "expected_min_chunks",
        "no_summary",
        "checks",
    }
    missing = sorted(required - set(fixture))
    if missing:
        failures.append(f"{fixture.get('id', '<unknown>')}: missing fields {missing}")
        return failures
    if fixture["no_summary"] is not True:
        failures.append(f"{fixture['id']}: no_summary must be true")
    if not fixture["source_text"]:
        failures.append(f"{fixture['id']}: source_text must be non-empty")
    if not isinstance(fixture["protected_terms"], list):
        failures.append(f"{fixture['id']}: protected_terms must be a list")
    if "expected_speech_contains" in fixture and not isinstance(
        fixture["expected_speech_contains"], list
    ):
        failures.append(f"{fixture['id']}: expected_speech_contains must be a list when present")
    if "expected_speech_excludes" in fixture and not isinstance(
        fixture["expected_speech_excludes"], list
    ):
        failures.append(f"{fixture['id']}: expected_speech_excludes must be a list when present")
    if "expected_pronunciation_hints" in fixture and not isinstance(
        fixture["expected_pronunciation_hints"], list
    ):
        failures.append(f"{fixture['id']}: expected_pronunciation_hints must be a list when present")
    if "exact_terms" in fixture and not isinstance(fixture["exact_terms"], list):
        failures.append(f"{fixture['id']}: exact_terms must be a list when present")
    if "rendering_intent" in fixture and fixture["rendering_intent"] not in {
        "conversational",
        "faithful_reading",
    }:
        failures.append(f"{fixture['id']}: unsupported rendering_intent")
    if "translation_boundary" in fixture["checks"]:
        for field in (
            "translation_provider_state",
            "language_pair_state",
            "expected_translation_status",
        ):
            if field not in fixture:
                failures.append(f"{fixture['id']}: {field} is required for translation_boundary")
    if "pronunciation_provider_boundary" in fixture["checks"]:
        for field in (
            "pronunciation_provider_state",
            "pronunciation_language_state",
            "expected_pronunciation_status",
        ):
            if field not in fixture:
                failures.append(
                    f"{fixture['id']}: {field} is required for pronunciation_provider_boundary"
                )
    return failures


def validate_prepared_fixture(fixture: dict[str, Any]) -> list[str]:
    failures: list[str] = validate_fixture_shape(fixture)
    if failures:
        return failures

    prepared = prepare_instruction_level_speech(fixture)
    fixture_id = fixture["id"]

    if len(prepared.cache) < fixture["expected_min_chunks"]:
        failures.append(
            f"{fixture_id}: expected at least {fixture['expected_min_chunks']} chunks, "
            f"got {len(prepared.cache)}"
        )

    for index, entry in enumerate(prepared.cache):
        missing_keys = sorted(REQUIRED_CACHE_KEYS - set(entry))
        if missing_keys:
            failures.append(f"{fixture_id}: cache[{index}] missing keys {missing_keys}")
        if len(entry["normalized_text"]) > fixture["max_chunk_chars"]:
            failures.append(f"{fixture_id}: cache[{index}] exceeds max_chunk_chars")
        if entry["target_language"] != fixture["target_language"]:
            failures.append(f"{fixture_id}: cache[{index}] target language drifted")
        expected_intent = fixture.get("rendering_intent")
        if expected_intent and entry.get("rendering_intent") != expected_intent:
            failures.append(f"{fixture_id}: cache[{index}] rendering intent drifted")

    normalized_text = " ".join(entry["normalized_text"] for entry in prepared.cache)

    for term in fixture["protected_terms"]:
        if term not in normalized_text:
            failures.append(f"{fixture_id}: protected term {term} missing from normalized text")

    for expected in fixture["expected_redactions"]:
        if not any(expected in entry["redactions"] for entry in prepared.cache):
            failures.append(f"{fixture_id}: expected redaction {expected} not recorded")
        if expected in prepared.speech_text:
            failures.append(f"{fixture_id}: secret-like value {expected} leaked to speech text")

    for forbidden in fixture["forbidden_terms"]:
        if forbidden in prepared.speech_text:
            failures.append(f"{fixture_id}: forbidden term {forbidden} leaked to speech text")

    for expected in fixture.get("expected_speech_contains", []):
        if expected not in prepared.speech_text:
            failures.append(f"{fixture_id}: expected speech text {expected!r} missing")

    for forbidden in fixture.get("expected_speech_excludes", []):
        if forbidden in prepared.speech_text:
            failures.append(f"{fixture_id}: excluded speech text {forbidden!r} leaked")

    actual_hints = [
        hint
        for entry in prepared.cache
        for hint in entry["pronunciation_hints"]
    ]
    for expected in fixture.get("expected_pronunciation_hints", []):
        if expected not in actual_hints:
            failures.append(f"{fixture_id}: expected pronunciation hint {expected!r} missing")

    if "pronunciation_hints" in fixture["checks"]:
        lowered_hints = " ".join(actual_hints).lower()
        leaked_claims = sorted(claim for claim in FORBIDDEN_HINT_CLAIMS if claim in lowered_hints)
        if leaked_claims:
            failures.append(f"{fixture_id}: pronunciation hints contain forbidden claims {leaked_claims}")
        for term in fixture["protected_terms"]:
            if term not in normalized_text:
                failures.append(f"{fixture_id}: pronunciation hint changed visible term {term}")

    if "markdown_cleanup" in fixture["checks"]:
        markdown_markers = ["```", "[", "](", "##", "`"]
        leaked = [marker for marker in markdown_markers if marker in prepared.speech_text]
        if leaked:
            failures.append(f"{fixture_id}: markdown markers leaked to speech text {leaked}")

    if "conversational_rendering" in fixture["checks"]:
        if fixture.get("rendering_intent") != "conversational":
            failures.append(f"{fixture_id}: conversational rendering requires conversational intent")
        leaked_shapes = ["|", "\n-", "\n* ", "```"]
        leaked = [marker for marker in leaked_shapes if marker in prepared.speech_text]
        if leaked:
            failures.append(f"{fixture_id}: structural markup leaked to conversational speech {leaked}")

    if "faithful_reading" in fixture["checks"]:
        if fixture.get("rendering_intent") != "faithful_reading":
            failures.append(f"{fixture_id}: faithful reading requires faithful_reading intent")

    if "exact_islands" in fixture["checks"]:
        exact_terms = fixture.get("exact_terms", fixture["protected_terms"])
        for term in exact_terms:
            if term not in prepared.speech_text and REDACTION_TOKEN not in term:
                failures.append(f"{fixture_id}: exact island {term} missing from speech text")

    if "no_execute" in fixture["checks"]:
        forbidden_actions = ["executado", "executei", "running", "ran command"]
        leaked = [action for action in forbidden_actions if action in prepared.speech_text.lower()]
        if leaked:
            failures.append(f"{fixture_id}: command execution claim leaked {leaked}")

    if "translation_boundary" in fixture["checks"]:
        plan = prepared.translation_plan
        if plan["mode"] != "speech_preparation_only":
            failures.append(f"{fixture_id}: translation mode must be speech_preparation_only")
        if plan["status"] != fixture["expected_translation_status"]:
            failures.append(
                f"{fixture_id}: expected translation status {fixture['expected_translation_status']}, "
                f"got {plan['status']}"
            )
        if plan["source_text_unchanged"] != fixture["source_text"]:
            failures.append(f"{fixture_id}: source text changed during translation planning")
        required_actions = {
            "redaction_before_translation",
            "protected_terms_before_translation",
            "span_level_translation_only",
            "no_summary",
            "preserve_source_text",
        }
        missing_actions = sorted(required_actions - set(plan["actions"]))
        if missing_actions:
            failures.append(f"{fixture_id}: translation plan missing actions {missing_actions}")
        for expected in fixture["expected_redactions"]:
            if expected in plan["redacted_text"]:
                failures.append(f"{fixture_id}: translation plan kept unredacted secret {expected}")
        for term in fixture["protected_terms"]:
            if term not in plan["protected_terms"]:
                failures.append(f"{fixture_id}: translation plan lost protected term {term}")
        if plan["status"] == "normalization_degraded" and plan["redacted_text"] != redact_secret_like_values(
            fixture["source_text"]
        )[0]:
            failures.append(f"{fixture_id}: degraded translation plan must preserve redacted source text")

    if "pronunciation_provider_boundary" in fixture["checks"]:
        plan = prepared.pronunciation_plan
        if plan["mode"] != "instruction_hints_baseline":
            failures.append(f"{fixture_id}: pronunciation mode must keep instruction hints as baseline")
        if plan["status"] != fixture["expected_pronunciation_status"]:
            failures.append(
                f"{fixture_id}: expected pronunciation status {fixture['expected_pronunciation_status']}, "
                f"got {plan['status']}"
            )
        if plan["emitted_outputs"] != ["instruction_level_hints"]:
            failures.append(f"{fixture_id}: pronunciation plan must emit only instruction-level hints")
        forbidden_outputs = {"ipa", "ssml", "phoneme", "lexicon", "provider_backed_pronunciation"}
        missing_blocked = sorted(forbidden_outputs - set(plan["blocked_outputs"]))
        if missing_blocked:
            failures.append(f"{fixture_id}: pronunciation plan missing blocked outputs {missing_blocked}")
        for term in fixture["protected_terms"]:
            if term not in plan["protected_terms"]:
                failures.append(f"{fixture_id}: pronunciation plan lost protected term {term}")
        if fixture["target_language"] == "he" and plan["hebrew_posture"] != "degraded":
            failures.append(f"{fixture_id}: Hebrew pronunciation posture must remain degraded")

    if "no_summary" in fixture["checks"] and fixture.get("rendering_intent") != "conversational":
        source_terms = set(clean_markdown_for_speech(redact_secret_like_values(fixture["source_text"])[0]).split())
        normalized_terms = set(normalized_text.split())
        missing_terms = sorted(source_terms - normalized_terms)
        if missing_terms:
            failures.append(f"{fixture_id}: normalized text dropped terms {missing_terms}")

    return failures


def validate_selector_corpus() -> list[str]:
    failures: list[str] = []
    for fixture in load_normalization_fixtures():
        fixture_id = fixture.get("id", "<unknown>")
        selector = fixture.get("selector")
        if not isinstance(selector, dict):
            failures.append(f"{fixture_id}: missing selector object")
            continue
        selected = select_target_language(selector)
        expected = fixture.get("expected_target_language")
        if selected != expected:
            failures.append(f"{fixture_id}: selector selected {selected}, expected {expected}")
    return failures


def validate_translation_boundary_fixtures(fixtures: list[dict[str, Any]]) -> list[str]:
    required = {
        "tts-translation-redaction-first",
        "tts-translation-protected-terms-first",
        "tts-translation-unclear-pair-degraded",
    }
    seen = {fixture["id"] for fixture in fixtures if "translation_boundary" in fixture["checks"]}
    missing = sorted(required - seen)
    if missing:
        return [f"missing translation boundary fixtures: {missing}"]
    return []


def validate_pronunciation_boundary_fixtures(fixtures: list[dict[str, Any]]) -> list[str]:
    required = {
        "tts-pronunciation-provider-boundary",
        "tts-pronunciation-hebrew-degraded",
        "tts-pronunciation-provider-unclear-degraded",
    }
    seen = {
        fixture["id"]
        for fixture in fixtures
        if "pronunciation_provider_boundary" in fixture["checks"]
    }
    missing = sorted(required - seen)
    if missing:
        return [f"missing pronunciation boundary fixtures: {missing}"]
    return []


def validate_spoken_rendering_fixtures(fixtures: list[dict[str, Any]]) -> list[str]:
    required = {
        "tts-spoken-acronym-rendering",
        "tts-spoken-path-rendering",
        "tts-spoken-github-url-rendering",
        "tts-spoken-exact-read-preserves-technical-spans",
        "tts-spoken-url-false-positive-guard",
        "tts-transform-markdown-entities",
        "tts-transform-code-fence-preserves-command",
        "tts-transform-long-hash-and-guid",
        "tts-transform-email-ip-social-spans",
        "tts-transform-exact-preserves-new-entities",
    }
    seen = {fixture["id"] for fixture in fixtures if "spoken_rendering" in fixture["checks"]}
    missing = sorted(required - seen)
    if missing:
        return [f"missing spoken rendering fixtures: {missing}"]
    return []


def validate_pronunciation_hint_fixtures(fixtures: list[dict[str, Any]]) -> list[str]:
    required = {
        "tts-pronunciation-technical-term-hints",
        "tts-pronunciation-package-model-proper-nouns",
        "tts-pronunciation-command-code-identifiers",
        "tts-pronunciation-forbidden-claim-guard",
        "tts-pronunciation-english-protected-terms",
    }
    seen = {fixture["id"] for fixture in fixtures if "pronunciation_hints" in fixture["checks"]}
    missing = sorted(required - seen)
    if missing:
        return [f"missing CAP-003 pronunciation hint fixtures: {missing}"]
    return []


def validate_cap006_conversational_fixtures(fixtures: list[dict[str, Any]]) -> list[str]:
    required = {
        "tts-cap006-interlocutor-oral-prose-ptbr",
        "tts-cap006-faithful-reading-markdown",
        "tts-cap006-exact-path-url-code-islands",
        "tts-cap006-ptbr-default-english-protected-terms",
        "tts-cap006-no-summary-long-operational-note",
        "tts-cap006-code-block-faithful-no-execute",
        "tts-cap006-table-to-prose-no-loss",
        "tts-cap006-secret-redaction-beats-exact",
    }
    seen = {fixture["id"] for fixture in fixtures if "cap006" in fixture["id"]}
    missing = sorted(required - seen)
    if missing:
        return [f"missing CAP-006 conversational fixtures: {missing}"]
    return []


def validate_cap007_exact_island_fixtures(fixtures: list[dict[str, Any]]) -> list[str]:
    required = {
        "tts-cap007-selective-exact-islands",
        "tts-cap007-secret-redaction-over-selective-exact",
        "tts-cap007-protect-fragile-span-classes",
        "tts-cap007-protect-scoped-package-before-mention",
    }
    seen = {fixture["id"] for fixture in fixtures if "cap007" in fixture["id"]}
    missing = sorted(required - seen)
    if missing:
        return [f"missing CAP-007 exact-island fixtures: {missing}"]
    return []


def validate_cap008_structure_oralization_fixtures(fixtures: list[dict[str, Any]]) -> list[str]:
    required = {
        "tts-cap008-table-multicolumn-ordered-facts",
        "tts-cap008-bullet-numbered-list-ordering",
        "tts-cap008-quote-oralization",
        "tts-cap008-code-block-conversational-no-execute",
        "tts-cap008-structure-preserves-exact-and-redaction",
    }
    seen = {fixture["id"] for fixture in fixtures if "cap008" in fixture["id"]}
    missing = sorted(required - seen)
    if missing:
        return [f"missing CAP-008 structure oralization fixtures: {missing}"]
    return []


def validate_cap009_english_identity_fixtures(fixtures: list[dict[str, Any]]) -> list[str]:
    required = {
        "tts-cap009-ptbr-narration-english-workflow-identity",
        "tts-cap009-mixed-span-translation-degraded-preserves-english",
        "tts-cap009-product-package-model-identity",
        "tts-cap009-hebrew-degraded-keeps-english-identity",
        "tts-cap009-structural-rendering-keeps-english-identity",
    }
    seen = {fixture["id"] for fixture in fixtures if "cap009" in fixture["id"]}
    missing = sorted(required - seen)
    if missing:
        return [f"missing CAP-009 English identity fixtures: {missing}"]
    return []


def validate_no_disk_write_surface() -> list[str]:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    failures: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Attribute) and function.attr in {"write_text", "write_bytes"}:
            failures.append(f"oracle contains disk write call: {function.attr}")
        if isinstance(function, ast.Name) and function.id in {"open", "NamedTemporaryFile", "mkstemp"}:
            failures.append(f"oracle contains disk write surface call: {function.id}")
        if isinstance(function, ast.Attribute) and function.attr in {"system", "popen"}:
            failures.append(f"oracle contains command execution surface call: {function.attr}")
        if isinstance(function, ast.Name) and function.id in {"run", "Popen", "call", "check_call"}:
            failures.append(f"oracle contains command execution surface call: {function.id}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is supported")

    failures = validate_no_disk_write_surface()
    failures.extend(validate_selector_corpus())
    fixtures = load_fixtures()
    failures.extend(validate_translation_boundary_fixtures(fixtures))
    failures.extend(validate_pronunciation_boundary_fixtures(fixtures))
    failures.extend(validate_spoken_rendering_fixtures(fixtures))
    failures.extend(validate_pronunciation_hint_fixtures(fixtures))
    failures.extend(validate_cap006_conversational_fixtures(fixtures))
    failures.extend(validate_cap007_exact_island_fixtures(fixtures))
    failures.extend(validate_cap008_structure_oralization_fixtures(fixtures))
    failures.extend(validate_cap009_english_identity_fixtures(fixtures))
    for fixture in fixtures:
        failures.extend(validate_prepared_fixture(fixture))

    status = "FAIL" if failures else "PASS"
    print(
        json.dumps(
            {
                "status": status,
                "version": VERSION,
                "fixtures": str(FIXTURE_PATH.relative_to(ROOT)),
                "checked_fixtures": len(fixtures),
                "failures": failures,
            },
            indent=2,
        )
    )
    print(f"[tes-tts-instruction-normalizer] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
