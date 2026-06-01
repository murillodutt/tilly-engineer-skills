"""TES TTS runtime adapters."""

from __future__ import annotations

import re
from typing import Any

from tes_tts_runtime_classifier import classify_text
from tes_tts_runtime_types import VERSION
from tes_tts_runtime_verbalizer import verbalize_ir


ENUMERATION_ITEM_RE = re.compile(r"^[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9_.+-]*(?:\s+[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9_.+-]*)?$")
ENUMERATION_CONNECTOR_RE = re.compile(r"^(?:e|ou|and|or)\s+", flags=re.IGNORECASE)
ENUMERATION_STOPWORDS = {"a", "as", "com", "de", "do", "dos", "e", "é", "o", "os", "ou", "sem"}
ASCII_WORD_RE = re.compile(r"^[a-z]{3,}$")
OMNIVOICE_PROSODY_WARMUP_TAGS = {
    "none": None,
    "confirmation-en": "[confirmation-en]",
    "question-en": "[question-en]",
    "sigh": "[sigh]",
}


def _looks_like_technical_item_word(word: str) -> bool:
    if any(char.isupper() for char in word):
        return True
    if any(char.isdigit() or char in "_.+-" for char in word):
        return True
    return bool(ASCII_WORD_RE.fullmatch(word)) and word.lower() not in ENUMERATION_STOPWORDS


def _is_short_enumeration_item(value: str) -> bool:
    item = ENUMERATION_CONNECTOR_RE.sub("", value.strip())
    if not item or len(item) > 32:
        return False
    words = item.split()
    if len(words) > 2 or not ENUMERATION_ITEM_RE.fullmatch(item):
        return False
    if item.lower() in ENUMERATION_STOPWORDS:
        return False
    if len(words) == 2 and not any(any(char.isupper() for char in word) for word in words):
        return False
    return all(_looks_like_technical_item_word(word) for word in words)


def _left_enumeration_item(value: str) -> str:
    tail = re.split(r"[;:!?]", value)[-1].strip()
    match = re.search(r"([A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9_.+-]*(?:\s+[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9_.+-]*)?)$", tail)
    return match.group(1) if match else ""


def _right_enumeration_item(value: str) -> str:
    head = re.split(r",|[;:!?]", value, maxsplit=1)[0].strip()
    head = ENUMERATION_CONNECTOR_RE.sub("", head).strip()
    connector = re.search(r"\s+(?:e|ou|and|or)\s+", head, flags=re.IGNORECASE)
    if connector:
        return head[: connector.start()].strip()
    return head


def add_enumeration_pauses(text: str) -> str:
    """Make compact comma-separated enumerations audible for local TTS providers."""

    parts = re.split(r"(,\s+)", text)
    if len(parts) < 5:
        return text

    output: list[str] = []
    for index, part in enumerate(parts):
        if not part.startswith(","):
            output.append(part)
            continue
        left = _left_enumeration_item(parts[index - 1] if index > 0 else "")
        right = _right_enumeration_item(parts[index + 1] if index + 1 < len(parts) else "")
        previous_left = _left_enumeration_item(parts[index - 3]) if index >= 3 and parts[index - 2].startswith(",") else ""
        next_right = _right_enumeration_item(parts[index + 3]) if index + 3 < len(parts) and parts[index + 2].startswith(",") else ""
        in_three_item_run = _is_short_enumeration_item(previous_left) or _is_short_enumeration_item(next_right)
        if _is_short_enumeration_item(left) and _is_short_enumeration_item(right) and in_three_item_run:
            output.append("; ")
        else:
            output.append(part)
    return "".join(output)


def apply_omnivoice_prosody_warmup(text: str, warmup: str = "none") -> dict[str, Any]:
    """Apply a whitelisted OmniVoice warmup tag to provider text only."""

    tag = OMNIVOICE_PROSODY_WARMUP_TAGS.get(warmup)
    if warmup not in OMNIVOICE_PROSODY_WARMUP_TAGS:
        raise ValueError(f"unsupported OmniVoice prosody warmup: {warmup}")
    if not tag:
        return {
            "text": text,
            "prosody_warmup": "none",
            "prosody_warmup_tag": None,
            "provider_tag_inserted": False,
        }
    stripped = text.lstrip()
    if stripped.startswith(tag):
        warmed = text
    else:
        warmed = f"{tag} {stripped}"
    return {
        "text": warmed,
        "prosody_warmup": warmup,
        "prosody_warmup_tag": tag,
        "provider_tag_inserted": True,
    }


def prepare_redacted_provider_text(source_text: str, locale: str = "pt-BR") -> dict[str, Any]:
    prepared = prepare_spoken_text(source_text, locale)
    text = add_enumeration_pauses(prepared["redacted_text"].replace("`", ""))
    return {
        "text": text,
        "prepared": prepared,
        "mode": "redacted_source",
        "strategy": "redacted_source_with_audible_enumeration_pauses",
    }


def prepare_audio_quality_text(source_text: str, locale: str = "pt-BR") -> dict[str, Any]:
    prepared = prepare_spoken_text(source_text, locale)
    text = prepared["redacted_text"].replace("`", "")
    replacements = (
        (r"\bspeak long\b", "leitura longa"),
        (r"\bchunks\b", "blocos"),
        (r"\bchunk\b", "bloco"),
        (r"\bJSONL\b", "JSON L"),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    text = add_enumeration_pauses(text)
    return {
        "text": text,
        "prepared": prepared,
        "mode": "audio_quality",
        "strategy": "minimal_functional_term_oralization",
    }


def adapt_plain_text(classified: dict[str, Any], verbalized: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": VERSION,
        "locale": classified["locale"],
        "pipeline": ["classify", "verbalize", "adapt_plain_text"],
        "source_text_immutable": True,
        "redacted_text": classified["redacted_text"],
        "spoken_text": verbalized["spoken_text"],
        "ir": classified["ir"],
        "span_kinds": classified["span_kinds"],
        "redaction_count": classified["redaction_count"],
        "index_strategy": classified["index_strategy"],
        "memo_scope": verbalized["memo_scope"],
        "cache_hits": verbalized["cache_hits"],
        "cache_misses": verbalized["cache_misses"],
        "provider_timing": "out_of_scope",
        "output_format": "plain_text",
        "summary_behavior": "none",
        "command_execution": "not_performed",
        "runtime_pronunciation_output": "none",
    }


def prepare_spoken_text(source_text: str, locale: str = "pt-BR") -> dict[str, Any]:
    classified = classify_text(source_text, locale)
    verbalized = verbalize_ir(classified["redacted_text"], classified["ir"])
    return adapt_plain_text(classified, verbalized)
