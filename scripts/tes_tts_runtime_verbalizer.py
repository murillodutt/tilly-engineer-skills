"""TES TTS plain-text verbalizer."""

from __future__ import annotations

from typing import Any


def verbalize_ir(redacted_text: str, ir: list[dict[str, Any]]) -> dict[str, Any]:
    memo: dict[str, str] = {}
    parts: list[str] = []
    cursor = 0
    hits = 0
    misses = 0
    for span in ir:
        key = f"{span['span_type']}:{span['source']}->{span['spoken_alias']}"
        if key in memo:
            hits += 1
            rendering = memo[key]
        else:
            misses += 1
            rendering = span["spoken_alias"]
            memo[key] = rendering
        parts.append(redacted_text[cursor : span["start"]])
        parts.append(rendering)
        cursor = span["end"]
    parts.append(redacted_text[cursor:])
    return {
        "spoken_text": "".join(parts).replace("`", ""),
        "memo_scope": "request_local",
        "cache_hits": hits,
        "cache_misses": misses,
    }
