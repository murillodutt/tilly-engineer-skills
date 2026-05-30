"""TES TTS runtime adapters."""

from __future__ import annotations

import re
from typing import Any

from tes_tts_runtime_classifier import classify_text
from tes_tts_runtime_types import VERSION
from tes_tts_runtime_verbalizer import verbalize_ir


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
