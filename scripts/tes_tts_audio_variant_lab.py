#!/usr/bin/env python3
"""Run TES TTS audio variants through synthesize-and-audit loops."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


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


def build_variant_text(source_text: str, variant: str) -> tuple[str, int]:
    if variant == "baseline":
        return source_text, 420
    if variant == "small_sentence_chunks":
        return source_text, 240
    if variant == "technical_oral_ptbr":
        return technical_oral_ptbr(source_text), 420
    if variant == "technical_oral_ptbr_keep_jsonl":
        return technical_oral_ptbr_keep_jsonl(source_text), 420
    if variant == "technical_oral_ptbr_json_hyphen":
        return technical_oral_ptbr_json_hyphen(source_text), 420
    if variant == "technical_oral_ptbr_small":
        return technical_oral_ptbr(source_text), 240
    if variant == "pause_newlines":
        return pause_newlines(source_text), 240
    raise ValueError(f"unknown variant: {variant}")


def write_variant_session(root: Path, *, source_id: str, variant: str, text: str, chunk_chars: int) -> Path:
    session = root / f"{safe_stem(source_id)}--{safe_stem(variant)}"
    session.mkdir(parents=True, exist_ok=True)
    chunks = split_sentence_chunks(text, max_chars=chunk_chars)
    (session / "input.txt").write_text(text, encoding="utf-8")
    (session / "chunk-texts.json").write_text(
        json.dumps(
            {
                "schema": "tes-tts-audio-variant-session@1",
                "version": VERSION,
                "source_chunk_id": source_id,
                "variant": variant,
                "chunk_chars": chunk_chars,
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


def synthesize_session(session: Path, *, chunk_chars: int, latency_profile: str) -> dict[str, Any]:
    text = (session / "input.txt").read_text(encoding="utf-8")
    command = [
        "python3",
        "scripts/tes_tts_omnivoice_provider.py",
        "speak-long",
        "--latency-profile",
        latency_profile,
        "--chunk-chars",
        str(chunk_chars),
        "--monitor-heartbeat",
        "3",
        "--slow-chunk-ms",
        "20000",
        "--output-dir",
        str(session),
        "--text",
        text,
    ]
    result = run_command(command)
    try:
        result["json"] = json.loads(result["stdout"])
    except json.JSONDecodeError:
        result["json"] = None
    return result


def audit_session(session: Path, *, stt: bool) -> dict[str, Any]:
    command = [
        "python3",
        "scripts/tes_tts_audio_audit.py",
        "audit-session",
        "--session-dir",
        str(session),
    ]
    if stt:
        command.append("--stt")
    result = run_command(command)
    audit_path = session / "audio-audit.json"
    result["audit"] = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else None
    return result


def summarize_audit(audit: dict[str, Any] | None) -> dict[str, Any]:
    if not audit:
        return {"status": "MISSING_AUDIT"}
    comparisons = [chunk.get("stt_comparison") for chunk in audit.get("chunks", []) if chunk.get("stt_comparison")]
    wers = [item["wer"] for item in comparisons if isinstance(item.get("wer"), (int, float))]
    similarities = [item["similarity"] for item in comparisons if isinstance(item.get("similarity"), (int, float))]
    flags = sorted({flag for chunk in audit.get("chunks", []) for flag in chunk.get("flags", [])})
    return {
        "status": audit.get("status"),
        "chunk_count": audit.get("chunk_count"),
        "max_wer": round(max(wers), 4) if wers else None,
        "avg_wer": round(sum(wers) / len(wers), 4) if wers else None,
        "min_similarity": round(min(similarities), 4) if similarities else None,
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


def command_run(args: argparse.Namespace) -> int:
    source_session = Path(args.source_session).resolve()
    output_root = Path(args.output_root).resolve() / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    output_root.mkdir(parents=True, exist_ok=True)
    source_chunks = load_source_chunks(source_session)
    selected_ids = set(args.chunk_id or [])
    variants = args.variant or [
        "baseline",
        "small_sentence_chunks",
        "technical_oral_ptbr",
        "technical_oral_ptbr_keep_jsonl",
        "technical_oral_ptbr_json_hyphen",
        "technical_oral_ptbr_small",
        "pause_newlines",
    ]

    results: list[dict[str, Any]] = []
    for source in source_chunks:
        source_id = source.get("id")
        if selected_ids and source_id not in selected_ids:
            continue
        source_text = source.get("text")
        if not isinstance(source_text, str) or not source_text:
            continue
        for variant in variants:
            variant_text, chunk_chars = build_variant_text(source_text, variant)
            session = write_variant_session(
                output_root,
                source_id=str(source_id),
                variant=variant,
                text=variant_text,
                chunk_chars=chunk_chars,
            )
            entry: dict[str, Any] = {
                "source_chunk_id": source_id,
                "variant": variant,
                "session": str(session),
                "chunk_chars": chunk_chars,
                "source_chars": len(source_text),
                "variant_chars": len(variant_text),
            }
            if args.synthesize:
                synth = synthesize_session(session, chunk_chars=chunk_chars, latency_profile=args.latency_profile)
                entry["synthesize_returncode"] = synth["returncode"]
                entry["synthesize_status"] = (synth.get("json") or {}).get("status")
            if args.audit:
                audit = audit_session(session, stt=args.stt)
                entry["audit_returncode"] = audit["returncode"]
                entry["audit_summary"] = summarize_audit(audit.get("audit"))
            results.append(entry)

    payload = {
        "schema": "tes-tts-audio-variant-lab@1",
        "version": VERSION,
        "source_session": str(source_session),
        "output_root": str(output_root),
        "synthesize": args.synthesize,
        "audit": args.audit,
        "stt": args.stt,
        "results": results,
        "ranked_results": rank_results(results),
    }
    output = output_root / "variant-lab-summary.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(output), "result_count": len(results)}, ensure_ascii=False, indent=2))
    return 0


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
    if "JSONL" not in technical_oral_ptbr_keep_jsonl(text):
        failures.append("keep JSONL transform drifted")
    if "JSON-L" not in technical_oral_ptbr_json_hyphen(text):
        failures.append("JSON hyphen transform drifted")
    paused = pause_newlines(text)
    if "\n\n" not in paused:
        failures.append("pause newline transform did not add paragraph boundary")
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
    run.add_argument("--latency-profile", default="fast")
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
