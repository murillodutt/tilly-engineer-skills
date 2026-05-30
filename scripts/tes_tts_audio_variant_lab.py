#!/usr/bin/env python3
"""Run TES TTS audio variants through synthesize-and-audit loops."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any
import zipfile

from tes_tts_omnivoice_provider import split_long_text
from tes_tts_runtime_adapter import prepare_audio_quality_text


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_SESSION = (
    ROOT / "tmp/tes-tts-omnivoice-provider/comparative-2chunks/20260530-131619"
)
DEFAULT_OUTPUT_ROOT = ROOT / "tmp/tes-tts-omnivoice-provider/audio-variant-lab"
VERSION = "0.3.147"
MIN_CHUNK_CHARS = 80


def safe_stem(value: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-")
    return stem[:80] or "variant"


def load_source_chunks(path: Path) -> list[dict[str, Any]]:
    payload = json.loads((path / "chunk-texts.json").read_text(encoding="utf-8"))
    chunks = payload.get("chunks")
    if not isinstance(chunks, list):
        raise ValueError(f"{path}/chunk-texts.json must contain chunks")
    return chunks


def split_sentence_chunks(text: str, *, max_chars: int) -> list[str]:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]
    if not sentences:
        return [text.strip()] if text.strip() else []
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = sentence if not current else f"{current} {sentence}"
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        chunks.append(current)

    bounded: list[str] = []
    for chunk in chunks:
        if len(chunk) <= max_chars:
            bounded.append(chunk)
            continue
        current = ""
        for word in chunk.split():
            candidate = word if not current else f"{current} {word}"
            if current and len(candidate) > max_chars:
                bounded.append(current)
                current = word
            else:
                current = candidate
        if current:
            bounded.append(current)
    return merge_short_chunks(bounded, min_chars=MIN_CHUNK_CHARS, max_chars=max_chars)


def merge_short_chunks(chunks: list[str], *, min_chars: int, max_chars: int) -> list[str]:
    merged: list[str] = []
    for chunk in chunks:
        if not merged:
            merged.append(chunk)
            continue
        previous = merged[-1]
        candidate = f"{previous} {chunk}"
        if len(chunk) < min_chars or len(previous) < min_chars:
            if len(candidate) <= max_chars:
                merged[-1] = candidate
            else:
                merged.append(chunk)
        else:
            merged.append(chunk)
    return merged


def technical_oral_ptbr(text: str) -> str:
    replacements = [
        (r"\bspeak long\b", "leitura longa"),
        (r"\bchunk\b", "bloco"),
        (r"\bchunks\b", "blocos"),
        (r"\bJSONL\b", "JSON L"),
        (r"\bfallback\b", "fallback"),
        (r"\bOmniVoice\b", "OmniVoice"),
    ]
    rendered = text
    for pattern, replacement in replacements:
        rendered = re.sub(pattern, replacement, rendered, flags=re.IGNORECASE)
    return rendered


def technical_oral_ptbr_keep_jsonl(text: str) -> str:
    rendered = technical_oral_ptbr(text)
    return re.sub(r"\bJSON L\b", "JSONL", rendered, flags=re.IGNORECASE)


def technical_oral_ptbr_json_hyphen(text: str) -> str:
    rendered = technical_oral_ptbr(text)
    return re.sub(r"\bJSON L\b", "JSON-L", rendered, flags=re.IGNORECASE)


def pause_newlines(text: str) -> str:
    text = re.sub(r"(?<=[.!?])\s+", "\n\n", text.strip())
    text = re.sub(r":\s+", ".\n\n", text)
    return text


def mixed_technical_spell_pause(text: str) -> str:
    rendered = text
    replacements = [
        (r"\bTES-TTS\b", "T E S T T S"),
        (r"\bOpen\.?\s*A\.?I\.?\s*A\.?P\.?I\.?\b", "Open A I A P I"),
        (r"\bADR\b", "A D R"),
        (r"\bAPI\b", "A P I"),
        (r"\bSDK\b", "S D K"),
        (r"\bCLI\b", "C L I"),
        (r"\bMCP\b", "M C P"),
        (r"\bSSML\b", "S S M L"),
        (r"\bPLS\b", "P L S"),
        (r"\bJSON\b", "J S O N"),
        (r"\bYAML\b", "Y A M L"),
        (r"\bHTTP\b", "H T T P"),
        (r"\bNode\.?JS\b", "Node J S"),
        (r"\b0004\b", "zero zero zero quatro"),
        (r"\bG\.\s*dois\s*P\.?\b", "G dois P"),
        (r"\bprovider\b", "prováider"),
        (r"\bTrie\b", "trai"),
        (r"\bAho\s+Corasick\b", "A rô Corássic"),
        (r"\bthresholds\b", "trésholds"),
    ]
    for pattern, replacement in replacements:
        rendered = re.sub(pattern, replacement, rendered, flags=re.IGNORECASE)
    rendered = rendered.replace(".,", ",")
    rendered = re.sub(r"\.{2,}", ".", rendered)
    rendered = re.sub(r"\s+", " ", rendered).strip()
    return rendered


def mixed_technical_clean_natural(text: str) -> str:
    rendered = text
    replacements = [
        (r"\bTES-TTS\b", "TES TTS"),
        (r"\b0004\b", "zero zero zero quatro"),
        (r"\bG\.\s*dois\s*P\.?\b", "G dois P"),
        (r"\bNode\.?JS\b", "Node JS"),
        (r"\bOpen\.?\s*A\.?I\.?\s*A\.?P\.?I\.?\b", "Open AI API"),
    ]
    for pattern, replacement in replacements:
        rendered = re.sub(pattern, replacement, rendered, flags=re.IGNORECASE)
    rendered = rendered.replace(".,", ",")
    rendered = re.sub(r"\.{2,}", ".", rendered)
    rendered = re.sub(r":\s+", ". ", rendered)
    rendered = re.sub(r"\s+", " ", rendered).strip()
    return rendered


def mixed_technical_clean_chunked(text: str) -> str:
    rendered = mixed_technical_clean_natural(text)
    rendered = re.sub(r"(?<=TES TTS\.)\s+", "\n\n", rendered)
    rendered = re.sub(r"(?<=MCP\.)\s+", "\n\n", rendered)
    rendered = re.sub(r"(?<=agora\.)\s+", "\n\n", rendered)
    return rendered


def mixed_technical_english_phrase(text: str) -> str:
    rendered = mixed_technical_clean_natural(text)
    rendered = re.sub(
        r"JSON, YAML, HTTP, Node JS, TypeScript, Python, Open AI API, Trie e Aho Corasick ficam como thresholds futuros\.",
        "English technical terms: JSON, YAML, HTTP, Node JS, TypeScript, Python, Open AI API, Trie, Aho Corasick, and thresholds. Esses ficam como thresholds futuros.",
        rendered,
        flags=re.IGNORECASE,
    )
    return rendered


def mixed_technical_english_sentence(text: str) -> str:
    rendered = mixed_technical_clean_natural(text)
    rendered = re.sub(
        r"JSON, YAML, HTTP, Node JS, TypeScript, Python, Open AI API, Trie e Aho Corasick ficam como thresholds futuros\.",
        "The English technical terms are JSON, YAML, HTTP, Node.js, TypeScript, Python, OpenAI API, Trie, Aho-Corasick, and thresholds. Esses ficam como thresholds futuros.",
        rendered,
        flags=re.IGNORECASE,
    )
    return rendered


def mixed_technical_english_phrase_chunked(text: str) -> str:
    rendered = mixed_technical_english_phrase(text)
    rendered = re.sub(r"(?<=MCP\.)\s+", "\n\n", rendered)
    rendered = re.sub(r"(?<=agora\.)\s+", "\n\n", rendered)
    rendered = re.sub(r"(?<=thresholds\.)\s+", "\n\n", rendered)
    return rendered


def mixed_technical_english_grouped(text: str) -> str:
    rendered = mixed_technical_clean_natural(text)
    rendered = re.sub(
        r"JSON, YAML, HTTP, Node JS, TypeScript, Python, Open AI API, Trie e Aho Corasick ficam como thresholds futuros\.",
        (
            "English technical terms, first group: JSON, YAML, and HTTP.\n\n"
            "English technical terms, second group: Node JS, TypeScript, Python, and Open AI API.\n\n"
            "English technical terms, third group: Trie, Aho Corasick, and thresholds.\n\n"
            "Esses ficam como thresholds futuros."
        ),
        rendered,
        flags=re.IGNORECASE,
    )
    rendered = re.sub(r"(?<=MCP\.)\s+", "\n\n", rendered)
    rendered = re.sub(r"(?<=agora\.)\s+", "\n\n", rendered)
    return rendered


def mixed_technical_canonical_english_chunked(text: str) -> str:
    rendered = mixed_technical_clean_natural(text)
    rendered = re.sub(
        r"JSON, YAML, HTTP, Node JS, TypeScript, Python, Open AI API, Trie e Aho Corasick ficam como thresholds futuros\.",
        (
            "The English technical terms are JSON, YAML, HTTP, Node.js, TypeScript, Python, OpenAI API, Trie, Aho-Corasick, and thresholds.\n\n"
            "Esses ficam como thresholds futuros."
        ),
        rendered,
        flags=re.IGNORECASE,
    )
    rendered = re.sub(r"(?<=MCP\.)\s+", "\n\n", rendered)
    rendered = re.sub(r"(?<=agora\.)\s+", "\n\n", rendered)
    return rendered


def mixed_technical_spelled_acronym_canonical_english(text: str) -> str:
    rendered = mixed_technical_canonical_english_chunked(text)
    rendered = re.sub(r"\bADR\b", "A D R", rendered)
    rendered = re.sub(r"\bAPI\b", "A P I", rendered)
    rendered = re.sub(r"\bSDK\b", "S D K", rendered)
    rendered = re.sub(r"\bCLI\b", "C L I", rendered)
    rendered = re.sub(r"\bMCP\b", "M C P", rendered)
    return rendered


def mixed_technical_semicolon_english_chunked(text: str) -> str:
    rendered = mixed_technical_clean_natural(text)
    rendered = re.sub(
        r"JSON, YAML, HTTP, Node JS, TypeScript, Python, Open AI API, Trie e Aho Corasick ficam como thresholds futuros\.",
        (
            "The English technical terms are: JSON and YAML; HTTP; Node.js, TypeScript, and Python; "
            "the OpenAI API; Trie, the data-structure name; Aho-Corasick, the algorithm name; and thresholds.\n\n"
            "Esses ficam como thresholds futuros."
        ),
        rendered,
        flags=re.IGNORECASE,
    )
    rendered = re.sub(r"(?<=MCP\.)\s+", "\n\n", rendered)
    rendered = re.sub(r"(?<=agora\.)\s+", "\n\n", rendered)
    return rendered


def mixed_technical_pt_letter_names_semicolon_english(text: str) -> str:
    rendered = mixed_technical_semicolon_english_chunked(text)
    rendered = re.sub(
        r"Teste real do TES TTS\. ADR\. zero zero zero quatro protege API, SDK, CLI\. e MCP\.",
        (
            "Teste real do TES TTS.\n\n"
            "Siglas em português. A sigla a dê érre, zero zero zero quatro, protege as siglas a pê i, "
            "ésse dê cá, cê éle i e ême cê pê."
        ),
        rendered,
        flags=re.IGNORECASE,
    )
    return rendered


def mixed_technical_scope_semicolon_english(text: str) -> str:
    rendered = mixed_technical_semicolon_english_chunked(text)
    rendered = re.sub(
        r"Não vamos usar SSML, PLS, fonema ou G dois P\. com suporte de provider agora\.",
        (
            "Limite atual. As siglas SSML e PLS ficam fora. "
            "Fonema, G dois P e suporte de provider também ficam fora agora."
        ),
        rendered,
        flags=re.IGNORECASE,
    )
    return rendered


def mixed_technical_problem_aliases(text: str) -> str:
    rendered = mixed_technical_clean_natural(text)
    rendered = re.sub(
        r"JSON, YAML, HTTP, Node JS, TypeScript, Python, Open AI API, Trie e Aho Corasick ficam como thresholds futuros\.",
        (
            "English technical terms: JSON, YAML, HTTP, Node JS, TypeScript, Python, and Open AI API.\n\n"
            "English problem terms: try, A ho Corasick, and thresholds.\n\n"
            "Esses ficam como thresholds futuros."
        ),
        rendered,
        flags=re.IGNORECASE,
    )
    rendered = re.sub(r"(?<=MCP\.)\s+", "\n\n", rendered)
    rendered = re.sub(r"(?<=agora\.)\s+", "\n\n", rendered)
    return rendered


def mixed_technical_context_sentences(text: str) -> str:
    rendered = mixed_technical_clean_natural(text)
    rendered = re.sub(
        r"JSON, YAML, HTTP, Node JS, TypeScript, Python, Open AI API, Trie e Aho Corasick ficam como thresholds futuros\.",
        (
            "English context: JSON and YAML are data formats.\n\n"
            "English context: HTTP is the protocol.\n\n"
            "English context: Node JS, TypeScript, and Python are runtime and language names.\n\n"
            "English context: Open AI API is the interface name.\n\n"
            "English context: Trie is a prefix tree.\n\n"
            "English context: Aho Corasick is a string matching algorithm.\n\n"
            "English context: thresholds are future limits.\n\n"
            "Esses ficam como thresholds futuros."
        ),
        rendered,
        flags=re.IGNORECASE,
    )
    rendered = re.sub(r"(?<=MCP\.)\s+", "\n\n", rendered)
    rendered = re.sub(r"(?<=agora\.)\s+", "\n\n", rendered)
    return rendered


def mixed_technical_cmu_hint(text: str) -> str:
    rendered = mixed_technical_clean_natural(text)
    replacements = [
        (r"\bprovider\b", "[P R AH0 V AY1 D ER0]"),
        (r"\bTrie\b", "[T R AY1]"),
        (r"\bAho\s+Corasick\b", "[AA1 HH OW0] [K AO1 R AH0 S IH0 K]"),
        (r"\bthresholds\b", "[TH R EH1 SH OW2 L D Z]"),
    ]
    for pattern, replacement in replacements:
        rendered = re.sub(pattern, replacement, rendered, flags=re.IGNORECASE)
    return rendered


def mixed_technical_chunked(text: str) -> str:
    rendered = mixed_technical_spell_pause(text)
    rendered = re.sub(r":\s+", ".\n\n", rendered)
    rendered = re.sub(r"(?<=M C P\.)\s+", "\n\n", rendered)
    rendered = re.sub(r"(?<=agora\.)\s+", "\n\n", rendered)
    return rendered


def build_variant_plan(source_text: str, variant: str) -> dict[str, Any]:
    if variant == "baseline":
        return {"text": source_text, "audit_text": source_text, "chunk_chars": 420, "text_mode": "redacted_source"}
    if variant == "audio_quality_text_mode":
        return {
            "text": source_text,
            "audit_text": prepare_audio_quality_text(source_text)["text"],
            "chunk_chars": 420,
            "text_mode": "audio_quality",
        }
    if variant == "small_sentence_chunks":
        return {"text": source_text, "audit_text": source_text, "chunk_chars": 240, "text_mode": "redacted_source"}
    if variant == "technical_oral_ptbr":
        text = technical_oral_ptbr(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 420, "text_mode": "redacted_source"}
    if variant == "technical_oral_ptbr_keep_jsonl":
        text = technical_oral_ptbr_keep_jsonl(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 420, "text_mode": "redacted_source"}
    if variant == "technical_oral_ptbr_json_hyphen":
        text = technical_oral_ptbr_json_hyphen(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 420, "text_mode": "redacted_source"}
    if variant == "technical_oral_ptbr_small":
        text = technical_oral_ptbr(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 240, "text_mode": "redacted_source"}
    if variant == "pause_newlines":
        text = pause_newlines(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 240, "text_mode": "redacted_source"}
    if variant == "mixed_technical_spell_pause":
        text = mixed_technical_spell_pause(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 420, "text_mode": "redacted_source"}
    if variant == "mixed_technical_clean_natural":
        text = mixed_technical_clean_natural(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 420, "text_mode": "redacted_source"}
    if variant == "mixed_technical_clean_chunked":
        text = mixed_technical_clean_chunked(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 180, "text_mode": "redacted_source"}
    if variant == "mixed_technical_english_phrase":
        text = mixed_technical_english_phrase(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 420, "text_mode": "redacted_source"}
    if variant == "mixed_technical_english_sentence":
        text = mixed_technical_english_sentence(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 420, "text_mode": "redacted_source"}
    if variant == "mixed_technical_english_phrase_chunked":
        text = mixed_technical_english_phrase_chunked(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 180, "text_mode": "redacted_source"}
    if variant == "mixed_technical_english_grouped":
        text = mixed_technical_english_grouped(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 180, "text_mode": "redacted_source"}
    if variant == "mixed_technical_canonical_english_chunked":
        text = mixed_technical_canonical_english_chunked(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 180, "text_mode": "redacted_source"}
    if variant == "mixed_technical_spelled_acronym_canonical_english":
        text = mixed_technical_spelled_acronym_canonical_english(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 180, "text_mode": "redacted_source"}
    if variant == "mixed_technical_semicolon_english_chunked":
        text = mixed_technical_semicolon_english_chunked(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 220, "text_mode": "redacted_source"}
    if variant == "mixed_technical_pt_letter_names_semicolon_english":
        text = mixed_technical_pt_letter_names_semicolon_english(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 220, "text_mode": "redacted_source"}
    if variant == "mixed_technical_scope_semicolon_english":
        text = mixed_technical_scope_semicolon_english(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 220, "text_mode": "redacted_source"}
    if variant == "mixed_technical_problem_aliases":
        text = mixed_technical_problem_aliases(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 180, "text_mode": "redacted_source"}
    if variant == "mixed_technical_context_sentences":
        text = mixed_technical_context_sentences(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 140, "text_mode": "redacted_source"}
    if variant == "mixed_technical_cmu_hint":
        text = mixed_technical_cmu_hint(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 420, "text_mode": "redacted_source"}
    if variant == "mixed_technical_chunked":
        text = mixed_technical_chunked(source_text)
        return {"text": text, "audit_text": text, "chunk_chars": 180, "text_mode": "redacted_source"}
    raise ValueError(f"unknown variant: {variant}")


def write_variant_session(
    root: Path,
    *,
    source_id: str,
    variant: str,
    text: str,
    audit_text: str,
    chunk_chars: int,
    text_mode: str,
) -> Path:
    session = root / f"{safe_stem(source_id)}--{safe_stem(variant)}"
    session.mkdir(parents=True, exist_ok=True)
    chunks = split_long_text(audit_text, max_chars=chunk_chars)
    (session / "input.txt").write_text(text, encoding="utf-8")
    (session / "audit-reference.txt").write_text(audit_text, encoding="utf-8")
    (session / "chunk-texts.json").write_text(
        json.dumps(
            {
                "schema": "tes-tts-audio-variant-session@1",
                "version": VERSION,
                "source_chunk_id": source_id,
                "variant": variant,
                "chunk_chars": chunk_chars,
                "text_mode": text_mode,
                "chunks": [
                    {
                        "id": f"chunk-{index:03d}",
                        "text": chunk,
                        "chars": len(chunk),
                        "expected_audio": str(session / f"{index:03d}-chunk-{index:03d}.wav"),
                    }
                    for index, chunk in enumerate(chunks, start=1)
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return session


def run_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def run_server_preflight(server_url: str | None, *, health_path: str, dry_run: bool = False) -> dict[str, Any]:
    command = [
        "python3",
        "scripts/tes_tts_omnivoice_provider.py",
        "server-status",
        "--health-path",
        health_path,
        "--discover-capabilities",
    ]
    if server_url:
        command.extend(["--server-url", server_url])
    if dry_run:
        command.append("--dry-run")
    result = run_command(command)
    try:
        result["json"] = json.loads(result["stdout"])
    except json.JSONDecodeError:
        result["json"] = None
    return result


def synthesize_session(
    session: Path,
    *,
    chunk_chars: int,
    latency_profile: str,
    text_mode: str,
    provider_language: str,
    provider_route: str,
    server_url: str | None,
    server_voice: str,
    server_speaker: str | None,
    server_instructions: str | None,
    server_stream: bool | None,
    server_num_step: int | None,
    combine: bool,
    inter_chunk_silence_ms: int,
    chunk_edge_silence_ms: int,
) -> dict[str, Any]:
    text = (session / "input.txt").read_text(encoding="utf-8")
    if provider_route == "server":
        command = [
            "python3",
            "scripts/tes_tts_omnivoice_provider.py",
            "speak-long-server",
            "--language",
            provider_language,
            "--chunk-chars",
            str(chunk_chars),
            "--voice",
            server_voice,
            "--output-dir",
            str(session),
            "--text",
            text,
        ]
        if server_url:
            command.extend(["--server-url", server_url])
        if server_speaker:
            command.extend(["--speaker", server_speaker])
        if server_instructions:
            command.extend(["--instructions", server_instructions])
        if server_stream is True:
            command.append("--stream")
        elif server_stream is False:
            command.append("--no-stream")
        if server_num_step is not None:
            command.extend(["--num-step", str(server_num_step)])
    else:
        command = [
            "python3",
            "scripts/tes_tts_omnivoice_provider.py",
            "speak-long",
            "--latency-profile",
            latency_profile,
            "--language",
            provider_language,
            "--chunk-chars",
            str(chunk_chars),
            "--text-mode",
            text_mode,
            "--monitor-heartbeat",
            "3",
            "--slow-chunk-ms",
            "20000",
            "--output-dir",
            str(session),
            "--text",
            text,
        ]
    if combine:
        command.extend(["--combine", "--inter-chunk-silence-ms", str(inter_chunk_silence_ms)])
    if provider_route != "server" and chunk_edge_silence_ms:
        command.extend(["--chunk-edge-silence-ms", str(chunk_edge_silence_ms)])
    result = run_command(command)
    try:
        result["json"] = json.loads(result["stdout"])
    except json.JSONDecodeError:
        result["json"] = None
    return result


def discovered_preferred_voice(server_preflight: dict[str, Any] | None) -> str | None:
    if not isinstance(server_preflight, dict):
        return None
    payload = server_preflight.get("json")
    if not isinstance(payload, dict):
        return None
    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, dict):
        return None
    value = capabilities.get("preferred_voice_id")
    return value if isinstance(value, str) and value else None


def audit_session(session: Path, *, stt: bool, audit_combined: bool, stt_language: str) -> dict[str, Any]:
    command = [
        "python3",
        "scripts/tes_tts_audio_audit.py",
        "audit-session",
        "--session-dir",
        str(session),
    ]
    audit_path = session / "audio-audit.json"
    audit_path.unlink(missing_ok=True)
    if stt:
        command.extend(["--stt", "--require-stt", "--stt-language", stt_language])
    if audit_combined:
        command.append("--audit-combined")
    result = run_command(command)
    result["audit"] = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else None
    return result


def summarize_audit(audit: dict[str, Any] | None) -> dict[str, Any]:
    if not audit:
        return {"status": "MISSING_AUDIT"}
    comparisons = [chunk.get("stt_comparison") for chunk in audit.get("chunks", []) if chunk.get("stt_comparison")]
    wers = [item["wer"] for item in comparisons if isinstance(item.get("wer"), (int, float))]
    similarities = [item["similarity"] for item in comparisons if isinstance(item.get("similarity"), (int, float))]
    domain_comparisons = [
        item.get("domain_normalized")
        for item in comparisons
        if isinstance(item.get("domain_normalized"), dict)
    ]
    domain_wers = [item["wer"] for item in domain_comparisons if isinstance(item.get("wer"), (int, float))]
    domain_similarities = [
        item["similarity"] for item in domain_comparisons if isinstance(item.get("similarity"), (int, float))
    ]
    interpretations = sorted(
        {
            item["interpretation"]
            for item in comparisons
            if isinstance(item.get("interpretation"), str)
        }
    )
    combined = audit.get("combined_audio") if isinstance(audit.get("combined_audio"), dict) else None
    flags = sorted(
        {flag for chunk in audit.get("chunks", []) for flag in chunk.get("flags", [])}
        | set(audit.get("audit_flags", []))
        | set(combined.get("flags", []) if combined else [])
    )
    return {
        "status": audit.get("status"),
        "chunk_count": audit.get("chunk_count"),
        "max_wer": round(max(wers), 4) if wers else None,
        "avg_wer": round(sum(wers) / len(wers), 4) if wers else None,
        "min_similarity": round(min(similarities), 4) if similarities else None,
        "max_domain_wer": round(max(domain_wers), 4) if domain_wers else None,
        "min_domain_similarity": round(min(domain_similarities), 4) if domain_similarities else None,
        "interpretations": interpretations,
        "combined_audio": combined,
        "flags": flags,
    }


def rank_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for result in results:
        summary = result.get("audit_summary") or {}
        max_wer = summary.get("max_wer")
        min_similarity = summary.get("min_similarity")
        ranked.append(
            {
                "source_chunk_id": result.get("source_chunk_id"),
                "variant": result.get("variant"),
                "text_mode": result.get("text_mode"),
                "session": result.get("session"),
                "status": summary.get("status") or result.get("synthesize_status"),
                "max_wer": max_wer,
                "min_similarity": min_similarity,
                "flag_count": len(summary.get("flags", [])),
            }
        )
    ranked.sort(
        key=lambda item: (
            0 if item["status"] == "PASS" else 1,
            item["max_wer"] if isinstance(item["max_wer"], (int, float)) else 999,
            -(item["min_similarity"] if isinstance(item["min_similarity"], (int, float)) else 0),
            item["flag_count"],
        )
    )
    return ranked


def overall_status(results: list[dict[str, Any]]) -> str:
    if not results:
        return "FAIL"
    statuses = [
        (result.get("audit_summary") or {}).get("status") or result.get("synthesize_status")
        for result in results
    ]
    if any(result.get("synthesize_returncode") not in (None, 0) for result in results):
        return "FAIL"
    if any(result.get("audit_returncode") not in (None, 0) for result in results):
        return "FAIL"
    if any(status in {"FAIL", "MISSING_AUDIT"} for status in statuses):
        return "FAIL"
    if any(status not in {None, "PASS"} for status in statuses):
        return "NEEDS_REVIEW"
    return "PASS"


def audio_files_for_session(session: Path) -> list[Path]:
    return sorted(path for path in session.glob("*.wav") if path.is_file())


def write_review_html(output_root: Path, payload: dict[str, Any]) -> Path:
    review_path = output_root / "review.html"
    rows: list[str] = []
    for result in payload["results"]:
        session = Path(result["session"])
        summary = result.get("audit_summary") or {}
        audio_items = []
        for audio in audio_files_for_session(session):
            rel_audio = audio.relative_to(output_root)
            audio_items.append(
                "<li>"
                f"<code>{html.escape(str(rel_audio))}</code><br>"
                f"<audio controls src=\"{html.escape(str(rel_audio))}\"></audio>"
                "</li>"
            )
        input_text = (session / "input.txt").read_text(encoding="utf-8") if (session / "input.txt").exists() else ""
        audit_text = (
            (session / "audit-reference.txt").read_text(encoding="utf-8")
            if (session / "audit-reference.txt").exists()
            else input_text
        )
        rows.append(
            "<section class=\"case\">"
            f"<h2>{html.escape(str(result['source_chunk_id']))} / {html.escape(result['variant'])}</h2>"
            "<dl>"
            f"<dt>Status</dt><dd>{html.escape(str(summary.get('status', 'not audited')))}</dd>"
            f"<dt>Text mode</dt><dd>{html.escape(str(result.get('text_mode')))}</dd>"
            f"<dt>Max WER</dt><dd>{html.escape(str(summary.get('max_wer')))}</dd>"
            f"<dt>Min similarity</dt><dd>{html.escape(str(summary.get('min_similarity')))}</dd>"
            f"<dt>Domain WER</dt><dd>{html.escape(str(summary.get('max_domain_wer')))}</dd>"
            f"<dt>Domain similarity</dt><dd>{html.escape(str(summary.get('min_domain_similarity')))}</dd>"
            f"<dt>Interpretation</dt><dd>{html.escape(', '.join(summary.get('interpretations', [])) or 'none')}</dd>"
            f"<dt>Flags</dt><dd>{html.escape(', '.join(summary.get('flags', [])) or 'none')}</dd>"
            "</dl>"
            "<h3>Input text</h3>"
            f"<pre>{html.escape(input_text)}</pre>"
            "<h3>Audit reference</h3>"
            f"<pre>{html.escape(audit_text)}</pre>"
            f"<ul>{''.join(audio_items)}</ul>"
            "</section>"
        )
    ranked = "\n".join(
        "<li>"
        f"{html.escape(item['variant'])}: status={html.escape(str(item['status']))}, "
        f"WER={html.escape(str(item['max_wer']))}, "
        f"similarity={html.escape(str(item['min_similarity']))}, "
        f"text_mode={html.escape(str(item.get('text_mode')))}"
        "</li>"
        for item in payload.get("ranked_results", [])
    )
    review_path.write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<meta charset=\"utf-8\">",
                "<title>TES TTS Audio Variant Review</title>",
                "<style>body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;line-height:1.5;max-width:960px;margin:32px auto;padding:0 16px}section{border-top:1px solid #ddd;padding:20px 0}pre{white-space:pre-wrap;background:#f7f7f7;padding:12px}audio{width:100%;max-width:720px}dt{font-weight:700}dd{margin:0 0 8px}</style>",
                "<h1>TES TTS Audio Variant Review</h1>",
                f"<p>Source session: <code>{html.escape(payload['source_session'])}</code></p>",
                "<h2>Ranking</h2>",
                f"<ol>{ranked}</ol>",
                *rows,
            ]
        ),
        encoding="utf-8",
    )
    return review_path


def write_review_package(output_root: Path, review_html: Path, payload: dict[str, Any]) -> Path:
    package_path = output_root / "audio-variant-review.zip"
    files = [review_html, output_root / "variant-lab-summary.json"]
    for result in payload["results"]:
        session = Path(result["session"])
        files.extend(path for path in session.iterdir() if path.is_file())
    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            if file_path.exists():
                archive.write(file_path, file_path.relative_to(output_root))
    return package_path


def command_run(args: argparse.Namespace) -> int:
    source_session = Path(args.source_session).resolve()
    output_root = Path(args.output_root).resolve() / dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    output_root.mkdir(parents=True, exist_ok=True)
    source_chunks = load_source_chunks(source_session)
    selected_ids = set(args.chunk_id or [])
    available_ids = {str(source.get("id")) for source in source_chunks if source.get("id")}
    missing_ids = sorted(selected_ids - available_ids)
    if missing_ids:
        output = output_root / "variant-lab-summary.json"
        payload = {
            "schema": "tes-tts-audio-variant-lab@1",
            "version": VERSION,
            "status": "FAIL",
            "reason": "requested chunk id was not found in source session",
            "source_session": str(source_session),
            "output_root": str(output_root),
            "available_chunk_ids": sorted(available_ids),
            "missing_chunk_ids": missing_ids,
            "results": [],
            "ranked_results": [],
        }
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": "FAIL", "output": str(output), "missing_chunk_ids": missing_ids}, ensure_ascii=False, indent=2))
        return 2
    variants = args.variant or [
        "baseline",
        "small_sentence_chunks",
        "technical_oral_ptbr",
        "technical_oral_ptbr_keep_jsonl",
        "technical_oral_ptbr_json_hyphen",
        "technical_oral_ptbr_small",
        "pause_newlines",
    ]

    server_preflight: dict[str, Any] | None = None
    if args.synthesize and args.provider_route == "server":
        server_preflight = run_server_preflight(args.server_url, health_path=args.server_health_path)
        preflight_payload = server_preflight.get("json") if isinstance(server_preflight.get("json"), dict) else {}
        preflight_status = preflight_payload.get("status")
        if server_preflight["returncode"] != 0 or preflight_status != "SERVER_AVAILABLE":
            output = output_root / "variant-lab-summary.json"
            payload = {
                "schema": "tes-tts-audio-variant-lab@1",
                "version": VERSION,
                "status": preflight_status or "SERVER_PREFLIGHT_FAILED",
                "reason": "server route preflight did not prove a ready OpenAI-compatible TTS server",
                "source_session": str(source_session),
                "output_root": str(output_root),
                "available_chunk_ids": sorted(available_ids),
                "selected_chunk_ids": sorted(selected_ids),
                "synthesize": args.synthesize,
                "audit": args.audit,
                "stt": args.stt,
                "combine": args.combine,
                "provider_route": args.provider_route,
                "server_url": args.server_url,
                "server_health_path": args.server_health_path,
                "server_voice": args.server_voice or "default",
                "server_voice_source": "arg" if args.server_voice else "default",
                "server_speaker": args.server_speaker,
                "server_instructions_present": bool(args.server_instructions),
                "server_stream": args.server_stream,
                "server_num_step": args.server_num_step,
                "server_preflight": server_preflight,
                "results": [],
                "ranked_results": [],
            }
            output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            print(
                json.dumps(
                    {
                        "status": payload["status"],
                        "output": str(output),
                        "server_preflight_status": preflight_status,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 2

    resolved_server_voice = (
        args.server_voice
        or discovered_preferred_voice(server_preflight)
        or "default"
    )

    results: list[dict[str, Any]] = []
    for source in source_chunks:
        source_id = source.get("id")
        if selected_ids and source_id not in selected_ids:
            continue
        source_text = source.get("text")
        if not isinstance(source_text, str) or not source_text:
            continue
        for variant in variants:
            plan = build_variant_plan(source_text, variant)
            variant_text = plan["text"]
            audit_text = plan["audit_text"]
            chunk_chars = plan["chunk_chars"]
            text_mode = plan["text_mode"]
            session = write_variant_session(
                output_root,
                source_id=str(source_id),
                variant=variant,
                text=variant_text,
                audit_text=audit_text,
                chunk_chars=chunk_chars,
                text_mode=text_mode,
            )
            entry: dict[str, Any] = {
                "source_chunk_id": source_id,
                "variant": variant,
                "text_mode": text_mode,
                "session": str(session),
                "chunk_chars": chunk_chars,
                "source_chars": len(source_text),
                "variant_chars": len(variant_text),
            }
            if args.synthesize:
                synth = synthesize_session(
                    session,
                    chunk_chars=chunk_chars,
                    latency_profile=args.latency_profile,
                    text_mode=text_mode,
                    provider_language=args.provider_language,
                    provider_route=args.provider_route,
                    server_url=args.server_url,
                    server_voice=resolved_server_voice,
                    server_speaker=args.server_speaker,
                    server_instructions=args.server_instructions,
                    server_stream=args.server_stream,
                    server_num_step=args.server_num_step,
                    combine=args.combine,
                    inter_chunk_silence_ms=args.inter_chunk_silence_ms,
                    chunk_edge_silence_ms=args.chunk_edge_silence_ms,
                )
                entry["synthesize_returncode"] = synth["returncode"]
                entry["synthesize_status"] = (synth.get("json") or {}).get("status")
                entry["combined_audio"] = (synth.get("json") or {}).get("combined_audio")
            if args.audit:
                audit = audit_session(
                    session,
                    stt=args.stt,
                    audit_combined=args.combine,
                    stt_language=args.stt_language,
                )
                entry["audit_returncode"] = audit["returncode"]
                entry["audit_summary"] = summarize_audit(audit.get("audit"))
            results.append(entry)

    payload = {
        "schema": "tes-tts-audio-variant-lab@1",
        "version": VERSION,
        "source_session": str(source_session),
        "output_root": str(output_root),
        "status": overall_status(results),
        "available_chunk_ids": sorted(available_ids),
        "selected_chunk_ids": sorted(selected_ids),
        "synthesize": args.synthesize,
        "audit": args.audit,
        "stt": args.stt,
        "combine": args.combine,
        "inter_chunk_silence_ms": args.inter_chunk_silence_ms,
        "chunk_edge_silence_ms": args.chunk_edge_silence_ms,
        "provider_language": args.provider_language,
        "provider_route": args.provider_route,
        "server_url": args.server_url,
        "server_health_path": args.server_health_path if args.provider_route == "server" else None,
        "server_preflight": server_preflight if args.provider_route == "server" and args.synthesize else None,
        "server_voice": resolved_server_voice if args.provider_route == "server" else None,
        "server_voice_source": (
            "arg"
            if args.provider_route == "server" and args.server_voice
            else "capability_discovery"
            if args.provider_route == "server" and discovered_preferred_voice(server_preflight)
            else "default"
            if args.provider_route == "server"
            else None
        ),
        "server_speaker": args.server_speaker if args.provider_route == "server" else None,
        "server_instructions_present": bool(args.server_instructions) if args.provider_route == "server" else None,
        "server_stream": args.server_stream if args.provider_route == "server" else None,
        "server_num_step": args.server_num_step if args.provider_route == "server" else None,
        "stt_language": args.stt_language,
        "results": results,
        "ranked_results": rank_results(results),
    }
    output = output_root / "variant-lab-summary.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    review_html = write_review_html(output_root, payload) if args.review else None
    package = write_review_package(output_root, review_html, payload) if args.package and review_html else None
    print(
        json.dumps(
            {
                "status": overall_status(results),
                "output": str(output),
                "review_html": str(review_html) if review_html else None,
                "package": str(package) if package else None,
                "result_count": len(results),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if results else 2


def command_self_test(_args: argparse.Namespace) -> int:
    text = (
        "A mudança real foi o novo caminho speak long: ele divide textos longos "
        "em blocos naturais, usa sessão residente OmniVoice e grava um log JSONL."
    )
    failures: list[str] = []
    small = split_sentence_chunks(text, max_chars=80)
    if len(small) < 2:
        failures.append("sentence chunking did not split representative text")
    if any(len(chunk) < MIN_CHUNK_CHARS for chunk in small[:-1]):
        failures.append("sentence chunking produced a short non-final orphan chunk")
    oral = technical_oral_ptbr(text)
    if "speak long" in oral.lower() or "chunk" in oral.lower() or "JSON L" not in oral:
        failures.append("technical oral PT-BR transform drifted")
    if overall_status([{"audit_summary": {"status": "NEEDS_REVIEW"}}]) != "NEEDS_REVIEW":
        failures.append("overall status did not preserve NEEDS_REVIEW")
    if overall_status([{"synthesize_returncode": 1, "synthesize_status": "FAIL"}]) != "FAIL":
        failures.append("overall status did not preserve synth failure")
    if "JSONL" not in technical_oral_ptbr_keep_jsonl(text):
        failures.append("keep JSONL transform drifted")
    if "JSON-L" not in technical_oral_ptbr_json_hyphen(text):
        failures.append("JSON hyphen transform drifted")
    if build_variant_plan(text, "audio_quality_text_mode")["text_mode"] != "audio_quality":
        failures.append("audio_quality text mode plan drifted")
    paused = pause_newlines(text)
    if "\n\n" not in paused:
        failures.append("pause newline transform did not add paragraph boundary")
    mixed = mixed_technical_spell_pause("Teste real do TES-TTS: ADR. 0004 protege API., Node.JS., Open.AI. API., Trie e Aho Corasick ficam como thresholds futuros.")
    for expected in ("T E S T T S", "A D R", "zero zero zero quatro", "A P I", "Node J S", "Open A I A P I", "trai", "A rô Corássic", "trésholds"):
        if expected not in mixed:
            failures.append(f"mixed technical transform missing {expected}")
    clean = mixed_technical_clean_natural("Teste real do TES-TTS: 0004 usa G. dois P. e Open.AI. API., Node.JS.")
    for expected in ("TES TTS", "zero zero zero quatro", "G dois P", "Open AI API", "Node JS"):
        if expected not in clean:
            failures.append(f"mixed clean transform missing {expected}")
    english_phrase = mixed_technical_english_phrase(
        "Teste real do TES-TTS: JSON., YAML., HTTP., Node.JS., TypeScript, Python, Open.AI. API., Trie e Aho Corasick ficam como thresholds futuros."
    )
    if "English technical terms:" not in english_phrase:
        failures.append("mixed English phrase transform missing phrase boundary")
    english_sentence = mixed_technical_english_sentence(
        "Teste real do TES-TTS: JSON., YAML., HTTP., Node.JS., TypeScript, Python, Open.AI. API., Trie e Aho Corasick ficam como thresholds futuros."
    )
    if "The English technical terms are" not in english_sentence:
        failures.append("mixed English sentence transform missing sentence boundary")
    english_chunked = mixed_technical_english_phrase_chunked(
        "Teste real do TES-TTS: MCP. Não vamos usar SSML com suporte de provider agora. JSON., YAML., HTTP., Node.JS., TypeScript, Python, Open.AI. API., Trie e Aho Corasick ficam como thresholds futuros."
    )
    if english_chunked.count("\n\n") < 2:
        failures.append("mixed English phrase chunked transform missing chunk boundaries")
    english_grouped = mixed_technical_english_grouped(
        "Teste real do TES-TTS: MCP. Não vamos usar SSML com suporte de provider agora. JSON., YAML., HTTP., Node.JS., TypeScript, Python, Open.AI. API., Trie e Aho Corasick ficam como thresholds futuros."
    )
    for expected in ("first group", "second group", "third group"):
        if expected not in english_grouped:
            failures.append(f"mixed English grouped transform missing {expected}")
    canonical_chunked = mixed_technical_canonical_english_chunked(
        "Teste real do TES-TTS: MCP. Não vamos usar SSML com suporte de provider agora. JSON., YAML., HTTP., Node.JS., TypeScript, Python, Open.AI. API., Trie e Aho Corasick ficam como thresholds futuros."
    )
    for expected in ("The English technical terms are", "Node.js", "OpenAI API", "Aho-Corasick"):
        if expected not in canonical_chunked:
            failures.append(f"mixed canonical English chunked transform missing {expected}")
    spelled_canonical = mixed_technical_spelled_acronym_canonical_english(
        "Teste real do TES-TTS: ADR. 0004 protege API., SDK., CLI. e MCP. Não vamos usar SSML com suporte de provider agora. JSON., YAML., HTTP., Node.JS., TypeScript, Python, Open.AI. API., Trie e Aho Corasick ficam como thresholds futuros."
    )
    for expected in ("A D R", "A P I", "S D K", "C L I", "M C P", "OpenAI A P I"):
        if expected not in spelled_canonical:
            failures.append(f"mixed spelled acronym canonical transform missing {expected}")
    semicolon_chunked = mixed_technical_semicolon_english_chunked(
        "Teste real do TES-TTS: MCP. Não vamos usar SSML com suporte de provider agora. JSON., YAML., HTTP., Node.JS., TypeScript, Python, Open.AI. API., Trie e Aho Corasick ficam como thresholds futuros."
    )
    for expected in ("JSON and YAML; HTTP;", "the OpenAI API", "Trie, the data-structure name", "Aho-Corasick, the algorithm name"):
        if expected not in semicolon_chunked:
            failures.append(f"mixed semicolon English chunked transform missing {expected}")
    pt_letters = mixed_technical_pt_letter_names_semicolon_english(
        "Teste real do TES-TTS: ADR. 0004 protege API., SDK., CLI. e MCP. Não vamos usar SSML com suporte de provider agora. JSON., YAML., HTTP., Node.JS., TypeScript, Python, Open.AI. API., Trie e Aho Corasick ficam como thresholds futuros."
    )
    for expected in ("Siglas em português", "a dê érre", "a pê i", "ésse dê cá", "ême cê pê"):
        if expected not in pt_letters:
            failures.append(f"mixed PT letter names transform missing {expected}")
    scope_semicolon = mixed_technical_scope_semicolon_english(
        "Teste real do TES-TTS: Não vamos usar SSML, PLS, fonema ou G. dois P. com suporte de provider agora. JSON., YAML., HTTP., Node.JS., TypeScript, Python, Open.AI. API., Trie e Aho Corasick ficam como thresholds futuros."
    )
    for expected in ("Limite atual", "As siglas SSML e PLS ficam fora", "suporte de provider também fica"):
        if expected not in scope_semicolon:
            failures.append(f"mixed scope semicolon transform missing {expected}")
    problem_aliases = mixed_technical_problem_aliases(
        "Teste real do TES-TTS: MCP. Não vamos usar SSML com suporte de provider agora. JSON., YAML., HTTP., Node.JS., TypeScript, Python, Open.AI. API., Trie e Aho Corasick ficam como thresholds futuros."
    )
    for expected in ("English problem terms", "try", "A ho Corasick"):
        if expected not in problem_aliases:
            failures.append(f"mixed problem alias transform missing {expected}")
    context_sentences = mixed_technical_context_sentences(
        "Teste real do TES-TTS: MCP. Não vamos usar SSML com suporte de provider agora. JSON., YAML., HTTP., Node.JS., TypeScript, Python, Open.AI. API., Trie e Aho Corasick ficam como thresholds futuros."
    )
    for expected in ("English context: JSON and YAML", "Aho Corasick is a string matching algorithm", "Esses ficam"):
        if expected not in context_sentences:
            failures.append(f"mixed context sentence transform missing {expected}")
    cmu = mixed_technical_cmu_hint("provider, Trie, Aho Corasick e thresholds")
    for expected in ("[P R AH0 V AY1 D ER0]", "[T R AY1]", "[AA1 HH OW0]", "[TH R EH1 SH OW2 L D Z]"):
        if expected not in cmu:
            failures.append(f"mixed CMU hint transform missing {expected}")
    source_session = DEFAULT_SOURCE_SESSION
    if source_session.exists():
        source_ids = {chunk["id"] for chunk in load_source_chunks(source_session)}
        if "chunk-003" in source_ids:
            failures.append("default fixture unexpectedly contains chunk-003; update missing-id self-test")
    preflight = run_server_preflight("http://127.0.0.1:9999/v1", health_path="/health", dry_run=True)
    preflight_payload = preflight.get("json") if isinstance(preflight.get("json"), dict) else {}
    if preflight_payload.get("endpoint") != "http://127.0.0.1:9999/v1/audio/speech":
        failures.append("server preflight did not normalize /v1 base URL")
    if preflight_payload.get("health_url") != "http://127.0.0.1:9999/health":
        failures.append("server preflight did not derive root health URL")
    if preflight_payload.get("status") != "DRY_RUN":
        failures.append("server preflight dry-run status drifted")
    preferred = discovered_preferred_voice({"json": {"capabilities": {"preferred_voice_id": "felipe-clone"}}})
    if preferred != "felipe-clone":
        failures.append("server preferred voice discovery drifted")
    original_run_command = run_command
    captured: dict[str, Any] = {}

    def fake_run_command(command: list[str]) -> dict[str, Any]:
        captured["command"] = command
        return {"command": command, "returncode": 0, "stdout": "{}", "stderr": "", "json": {}}

    try:
        globals()["run_command"] = fake_run_command
        with tempfile.TemporaryDirectory() as tmp_dir:
            session = Path(tmp_dir)
            (session / "input.txt").write_text("Teste com JSON e TypeScript.", encoding="utf-8")
            synthesize_session(
                session,
                chunk_chars=120,
                latency_profile="fast",
                text_mode="redacted_source",
                provider_language="pt",
                provider_route="server",
                server_url="http://127.0.0.1:8880/v1",
                server_voice="felipe-clone",
                server_speaker="felipe-clone",
                server_instructions="Preserve English technical terms.",
                server_stream=False,
                server_num_step=12,
                combine=True,
                inter_chunk_silence_ms=350,
                chunk_edge_silence_ms=0,
            )
    finally:
        globals()["run_command"] = original_run_command
    command = captured.get("command")
    if not isinstance(command, list):
        failures.append("server synthesis command capture failed")
    else:
        expected_parts = {
            "--server-url",
            "http://127.0.0.1:8880/v1",
            "--voice",
            "felipe-clone",
            "--speaker",
            "felipe-clone",
            "--instructions",
            "Preserve English technical terms.",
            "--no-stream",
            "--num-step",
            "12",
            "--combine",
        }
        missing = sorted(expected_parts - set(command))
        if missing:
            failures.append(f"server synthesis command missing controls {missing}")
    if failures:
        print(json.dumps({"status": "FAIL", "failures": failures}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"status": "PASS", "mode": "self_test"}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run")
    run.add_argument("--source-session", default=str(DEFAULT_SOURCE_SESSION))
    run.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    run.add_argument("--chunk-id", action="append")
    run.add_argument("--variant", action="append")
    run.add_argument("--synthesize", action="store_true")
    run.add_argument("--audit", action="store_true")
    run.add_argument("--stt", action="store_true")
    run.add_argument("--review", action="store_true")
    run.add_argument("--package", action="store_true")
    run.add_argument("--combine", action="store_true")
    run.add_argument("--inter-chunk-silence-ms", type=int, default=350)
    run.add_argument("--chunk-edge-silence-ms", type=int, default=0)
    run.add_argument("--latency-profile", default="fast")
    run.add_argument("--provider-language", default="pt")
    run.add_argument("--provider-route", choices=["resident", "server"], default="resident")
    run.add_argument("--server-url")
    run.add_argument("--server-voice")
    run.add_argument("--server-speaker")
    run.add_argument("--server-instructions")
    run.add_argument("--server-stream", action=argparse.BooleanOptionalAction, default=None)
    run.add_argument("--server-num-step", type=int)
    run.add_argument("--server-health-path", default="/health")
    run.add_argument("--stt-language", default="portuguese")
    run.set_defaults(func=command_run)

    self_test = subparsers.add_parser("self-test")
    self_test.set_defaults(func=command_self_test)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
