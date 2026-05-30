#!/usr/bin/env python3
"""Audit TES TTS chunk audio against preserved source text.

The script is intentionally dependency-light. Basic WAV metrics and text
inspection use only the standard library. STT is optional and runs in a caller
provided Python environment when `--stt` is requested.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
from typing import Any
import unicodedata
import wave


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STT_PYTHON = ROOT / "tmp/tes-tts-lab/omnivoice/.venv/bin/python"
DEFAULT_STT_MODEL = (
    ROOT
    / "tmp/tes-tts-lab/omnivoice/hf-cache/hub/"
    "models--openai--whisper-large-v3-turbo/snapshots/"
    "41f01f3fe87f28c78e2fbf8b568835947dd65ed9"
)
VERSION = "0.3.147"
SILENCE_THRESHOLD = 0.005
NEAR_CLIP_THRESHOLD = 0.95
BAD_SIMILARITY_THRESHOLD = 0.86
BAD_WER_THRESHOLD = 0.28
DOMAIN_NORMALIZED_SUBSTITUTIONS = [
    (r"\bjson[\s-]*l\b", "jsonl"),
    (r"\bjason[\s-]*l\b", "jsonl"),
    (r"\bomni\s+voice\b", "omnivoice"),
    (r"\bomni\s*voyce\b", "omnivoice"),
    (r"\bomnivoyce\b", "omnivoice"),
    (r"\bou\s+minivoiz\b", "omnivoice"),
    (r"\bminivoiz\b", "omnivoice"),
    (r"\bresident\b", "residente"),
]


def normalize_for_compare(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^\w\sáàâãéêíóôõúçü-]", " ", text, flags=re.IGNORECASE)
    return [word for word in re.sub(r"\s+", " ", text).strip().split(" ") if word]


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def normalize_domain_terms_for_compare(text: str) -> str:
    normalized = strip_accents(text.lower())
    normalized = normalized.replace("-", " ")
    for pattern, replacement in DOMAIN_NORMALIZED_SUBSTITUTIONS:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\b(a|o|as|os|um|uma|uns|umas)\b", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def domain_normalized_comparison(reference: str, hypothesis: str) -> dict[str, Any]:
    normalized_reference = normalize_domain_terms_for_compare(reference)
    normalized_hypothesis = normalize_domain_terms_for_compare(hypothesis)
    similarity = round(similarity_ratio(normalized_reference, normalized_hypothesis), 4)
    wer = round(word_error_rate(normalized_reference, normalized_hypothesis), 4)
    return {
        "normalizer": "tes_tts_domain_terms@1",
        "reference": normalized_reference,
        "hypothesis": normalized_hypothesis,
        "similarity": similarity,
        "wer": wer,
        "status": "PASS" if similarity >= BAD_SIMILARITY_THRESHOLD and wer <= BAD_WER_THRESHOLD else "NEEDS_REVIEW",
    }


def edit_distance(left: list[str], right: list[str]) -> int:
    previous = list(range(len(right) + 1))
    for i, left_item in enumerate(left, start=1):
        current = [i]
        for j, right_item in enumerate(right, start=1):
            current.append(
                min(
                    previous[j] + 1,
                    current[j - 1] + 1,
                    previous[j - 1] + (0 if left_item == right_item else 1),
                )
            )
        previous = current
    return previous[-1]


def similarity_ratio(left: str, right: str) -> float:
    left_words = normalize_for_compare(left)
    right_words = normalize_for_compare(right)
    if not left_words and not right_words:
        return 1.0
    distance = edit_distance(left_words, right_words)
    return max(0.0, 1.0 - distance / max(len(left_words), len(right_words), 1))


def word_error_rate(reference: str, hypothesis: str) -> float:
    reference_words = normalize_for_compare(reference)
    hypothesis_words = normalize_for_compare(hypothesis)
    if not reference_words:
        return 0.0 if not hypothesis_words else 1.0
    return edit_distance(reference_words, hypothesis_words) / len(reference_words)


def inspect_text(text: str) -> dict[str, Any]:
    categories: dict[str, int] = {}
    suspicious: list[dict[str, Any]] = []
    non_ascii: list[dict[str, Any]] = []
    for index, char in enumerate(text):
        category = unicodedata.category(char)
        categories[category] = categories.get(category, 0) + 1
        item = {
            "index": index,
            "char": char,
            "code": f"U+{ord(char):04X}",
            "name": unicodedata.name(char, "UNKNOWN"),
            "category": category,
        }
        if ord(char) > 127:
            non_ascii.append(item)
        if category.startswith("C") or (category.startswith("Z") and char != " "):
            suspicious.append(item)
    return {
        "chars": len(text),
        "unicode_categories": categories,
        "non_ascii_count": len(non_ascii),
        "non_ascii": non_ascii,
        "suspicious_count": len(suspicious),
        "suspicious": suspicious,
    }


def read_wave_samples(path: Path) -> tuple[list[float], int, int, int]:
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        sample_rate = handle.getframerate()
        sample_width = handle.getsampwidth()
        frame_count = handle.getnframes()
        raw = handle.readframes(frame_count)

    if sample_width != 2:
        raise ValueError(f"{path}: only 16-bit PCM WAV is supported, got sample width {sample_width}")
    if not raw:
        return [], sample_rate, channels, frame_count
    count = len(raw) // 2
    values = struct.unpack("<" + "h" * count, raw)
    if channels <= 1:
        samples = [value / 32768.0 for value in values]
    else:
        samples = []
        for offset in range(0, len(values), channels):
            frame = values[offset : offset + channels]
            samples.append(sum(frame) / (32768.0 * len(frame)))
    return samples, sample_rate, channels, frame_count


def audio_metrics(path: Path) -> dict[str, Any]:
    samples, sample_rate, channels, frame_count = read_wave_samples(path)
    duration = frame_count / sample_rate if sample_rate else 0.0
    if not samples:
        return {
            "file": str(path),
            "exists": path.exists(),
            "duration_seconds": round(duration, 3),
            "sample_rate": sample_rate,
            "channels": channels,
            "peak": 0.0,
            "rms": 0.0,
            "peak_dbfs": None,
            "rms_dbfs": None,
            "clip_ratio": 0.0,
            "near_clip_ratio": 0.0,
            "silence_ratio": 1.0,
            "max_sample_jump": 0.0,
            "zero_crossing_rate": 0.0,
        }

    abs_samples = [abs(sample) for sample in samples]
    peak = max(abs_samples)
    rms = math.sqrt(sum(sample * sample for sample in samples) / len(samples))
    clip_ratio = sum(1 for sample in abs_samples if sample >= 0.999) / len(samples)
    near_clip_ratio = sum(1 for sample in abs_samples if sample >= NEAR_CLIP_THRESHOLD) / len(samples)
    silence_ratio = sum(1 for sample in abs_samples if sample <= SILENCE_THRESHOLD) / len(samples)
    jumps = [abs(samples[index] - samples[index - 1]) for index in range(1, len(samples))]
    zero_crossings = sum(
        1
        for index in range(1, len(samples))
        if (samples[index - 1] < 0 <= samples[index]) or (samples[index - 1] > 0 >= samples[index])
    )

    return {
        "file": str(path),
        "exists": path.exists(),
        "duration_seconds": round(duration, 3),
        "sample_rate": sample_rate,
        "channels": channels,
        "peak": round(peak, 6),
        "rms": round(rms, 6),
        "peak_dbfs": round(20 * math.log10(peak), 2) if peak > 0 else None,
        "rms_dbfs": round(20 * math.log10(rms), 2) if rms > 0 else None,
        "clip_ratio": round(clip_ratio, 8),
        "near_clip_ratio": round(near_clip_ratio, 8),
        "silence_ratio": round(silence_ratio, 6),
        "max_sample_jump": round(max(jumps) if jumps else 0.0, 6),
        "zero_crossing_rate": round(zero_crossings / max(len(samples) - 1, 1), 6),
    }


def resolve_audio_path(session_dir: Path, expected_audio: str | None, chunk_id: str) -> Path:
    candidates: list[Path] = []
    if expected_audio:
        expected = Path(expected_audio)
        candidates.append(expected if expected.is_absolute() else ROOT / expected)
        candidates.append(session_dir / expected.name)
    candidates.extend(sorted(session_dir.glob(f"*-{chunk_id}.wav")))
    candidates.extend(sorted(session_dir.glob(f"*{chunk_id}*.wav")))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0] if candidates else session_dir / f"{chunk_id}.wav"


def audit_combined_audio(session_dir: Path, args: argparse.Namespace) -> dict[str, Any] | None:
    if not args.audit_combined:
        return None
    path = session_dir / "combined.wav"
    if not path.exists():
        return {
            "audio": str(path),
            "exists": False,
            "flags": ["COMBINED_AUDIO_MISSING"],
        }
    metrics = audio_metrics(path)
    flags: list[str] = []
    if metrics["clip_ratio"] or metrics["near_clip_ratio"]:
        flags.append("COMBINED_CLIPPING_RISK")
    if metrics["max_sample_jump"] >= args.max_sample_jump:
        flags.append("COMBINED_SAMPLE_JUMP_REVIEW")
    return {
        "audio": str(path),
        "exists": True,
        "audio_metrics": metrics,
        "flags": flags,
    }


def load_chunks(session_dir: Path) -> list[dict[str, Any]]:
    chunk_path = session_dir / "chunk-texts.json"
    if not chunk_path.exists():
        raise FileNotFoundError(f"missing {chunk_path}")
    payload = json.loads(chunk_path.read_text(encoding="utf-8"))
    chunks = payload.get("chunks")
    if not isinstance(chunks, list):
        raise ValueError("chunk-texts.json must contain a chunks list")
    normalized: list[dict[str, Any]] = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_id = chunk.get("id") or f"chunk-{index:03d}"
        text = chunk.get("text")
        if not isinstance(text, str):
            raise ValueError(f"{chunk_id}: text is required")
        audio = resolve_audio_path(session_dir, chunk.get("expected_audio"), chunk_id)
        normalized.append({"id": chunk_id, "text": text, "audio": audio})
    return normalized


def run_stt(
    *,
    python: Path,
    model: Path,
    language: str,
    rows: list[dict[str, Any]],
    require_stt: bool,
) -> tuple[dict[str, str], dict[str, Any]]:
    if not python.exists() or not model.exists():
        details = {
            "status": "STT_NOT_AVAILABLE",
            "python": str(python),
            "model": str(model),
            "reason": "python or model path does not exist",
        }
        if require_stt:
            raise RuntimeError(details["reason"])
        return {}, details

    request = {"model": str(model), "language": language, "files": [str(row["audio"]) for row in rows]}
    code = r"""
import json
import os
import sys
import time

request = json.loads(sys.stdin.read())
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

try:
    import torch
    from transformers import pipeline
except Exception as exc:
    print(json.dumps({"status": "STT_NOT_AVAILABLE", "reason": repr(exc)}, ensure_ascii=False))
    raise SystemExit(0)

device = "mps" if torch.backends.mps.is_available() else "cpu"
started = time.perf_counter()
asr = pipeline(
    "automatic-speech-recognition",
    model=request["model"],
    device=device,
    dtype=torch.float16 if device == "mps" else torch.float32,
)
load_ms = round((time.perf_counter() - started) * 1000, 3)
rows = []
for file_path in request["files"]:
    item_started = time.perf_counter()
    output = asr(
        file_path,
        generate_kwargs={"language": request["language"], "task": "transcribe"},
    )
    rows.append(
        {
            "file": file_path,
            "transcription": output.get("text", ""),
            "stt_ms": round((time.perf_counter() - item_started) * 1000, 3),
        }
    )
print(json.dumps({"status": "PASS", "device": device, "load_ms": load_ms, "rows": rows}, ensure_ascii=False))
"""
    completed = subprocess.run(
        [str(python), "-c", code],
        check=False,
        input=json.dumps(request),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        details = {
            "status": "STT_FAILED",
            "returncode": completed.returncode,
            "stderr": completed.stderr.strip(),
        }
        if require_stt:
            raise RuntimeError(details["stderr"] or "STT failed")
        return {}, details
    try:
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
    except json.JSONDecodeError as exc:
        details = {"status": "STT_FAILED", "reason": f"invalid STT JSON: {exc}", "stdout": completed.stdout}
        if require_stt:
            raise RuntimeError(details["reason"])
        return {}, details
    if payload.get("status") != "PASS":
        if require_stt:
            raise RuntimeError(payload.get("reason", "STT not available"))
        return {}, payload
    return {Path(row["file"]).name: row.get("transcription", "") for row in payload["rows"]}, payload


def audit_session(args: argparse.Namespace) -> dict[str, Any]:
    session_dir = Path(args.session_dir).resolve()
    chunks = load_chunks(session_dir)
    stt_by_file: dict[str, str] = {}
    stt_details: dict[str, Any] = {"status": "SKIPPED"}
    audit_flags: list[str] = []
    if args.stt:
        stt_by_file, stt_details = run_stt(
            python=Path(args.stt_python),
            model=Path(args.stt_model),
            language=args.stt_language,
            rows=chunks,
            require_stt=args.require_stt,
        )
        if stt_details.get("status") != "PASS":
            audit_flags.append("STT_UNAVAILABLE_REVIEW")

    audited_chunks: list[dict[str, Any]] = []
    status = "PASS"
    for chunk in chunks:
        metrics = audio_metrics(chunk["audio"])
        text_report = inspect_text(chunk["text"])
        transcript = stt_by_file.get(chunk["audio"].name)
        flags: list[str] = []
        if text_report["suspicious_count"]:
            flags.append("SUSPICIOUS_TEXT_CHARACTER")
        if metrics["clip_ratio"] or metrics["near_clip_ratio"]:
            flags.append("CLIPPING_RISK")
        if metrics["max_sample_jump"] >= args.max_sample_jump:
            flags.append("SAMPLE_JUMP_REVIEW")
        comparison: dict[str, Any] | None = None
        if transcript is not None:
            raw_similarity = round(similarity_ratio(chunk["text"], transcript), 4)
            raw_wer = round(word_error_rate(chunk["text"], transcript), 4)
            domain_comparison = domain_normalized_comparison(chunk["text"], transcript)
            comparison = {
                "transcription": transcript.strip(),
                "similarity": raw_similarity,
                "wer": raw_wer,
                "domain_normalized": domain_comparison,
            }
            raw_needs_review = raw_similarity < BAD_SIMILARITY_THRESHOLD or raw_wer > BAD_WER_THRESHOLD
            domain_needs_review = domain_comparison["status"] != "PASS"
            if raw_needs_review and domain_needs_review:
                flags.append("STT_DEGRADATION_REVIEW")
            elif raw_needs_review:
                flags.append("RAW_STT_DRIFT_DOMAIN_NORMALIZED_REVIEW")
                comparison["interpretation"] = "RAW_STT_DRIFT_DOMAIN_NORMALIZED_PASS"
            else:
                comparison["interpretation"] = "RAW_STT_PASS"
        if flags and status == "PASS":
            status = "NEEDS_REVIEW"
        audited_chunks.append(
            {
                "id": chunk["id"],
                "text": chunk["text"],
                "audio": str(chunk["audio"]),
                "text_inspection": text_report,
                "audio_metrics": metrics,
                "stt_comparison": comparison,
                "flags": flags,
            }
        )

    combined_audio = audit_combined_audio(session_dir, args)
    if combined_audio and combined_audio.get("flags"):
        audit_flags.extend(str(flag) for flag in combined_audio["flags"])
    if audit_flags and status == "PASS":
        status = "NEEDS_REVIEW"

    return {
        "schema": "tes-tts-audio-audit@1",
        "version": VERSION,
        "status": status,
        "session_dir": str(session_dir),
        "chunk_count": len(audited_chunks),
        "stt": stt_details,
        "audit_flags": sorted(set(audit_flags)),
        "combined_audio": combined_audio,
        "thresholds": {
            "bad_similarity_below": BAD_SIMILARITY_THRESHOLD,
            "bad_wer_above": BAD_WER_THRESHOLD,
            "max_sample_jump_review": args.max_sample_jump,
            "domain_normalizer": "tes_tts_domain_terms@1",
            "domain_normalizer_scope": "STT evaluation only; raw WER remains preserved",
        },
        "chunks": audited_chunks,
    }


def command_audit(args: argparse.Namespace) -> int:
    payload = audit_session(args)
    output = Path(args.output) if args.output else Path(args.session_dir) / "audio-audit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "output": str(output), "chunk_count": payload["chunk_count"]}, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASS" or not args.strict else 2


def write_test_wav(path: Path) -> None:
    sample_rate = 8000
    duration_seconds = 0.25
    frames = []
    for index in range(int(sample_rate * duration_seconds)):
        sample = int(0.2 * 32767 * math.sin(2 * math.pi * 440 * (index / sample_rate)))
        frames.append(struct.pack("<h", sample))
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(b"".join(frames))


def command_self_test(_args: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        wav_path = root / "001-chunk-001.wav"
        combined_path = root / "combined.wav"
        write_test_wav(wav_path)
        write_test_wav(combined_path)
        (root / "chunk-texts.json").write_text(
            json.dumps(
                {
                    "schema": "tes-tts-test@1",
                    "chunks": [
                        {
                            "id": "chunk-001",
                            "text": "Teste limpo de áudio.",
                            "expected_audio": str(wav_path),
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        args = argparse.Namespace(
            session_dir=str(root),
            stt=False,
            stt_python=str(DEFAULT_STT_PYTHON),
            stt_model=str(DEFAULT_STT_MODEL),
            stt_language="portuguese",
            require_stt=False,
            max_sample_jump=0.7,
            output=None,
            strict=False,
            audit_combined=True,
        )
        payload = audit_session(args)
        failures = []
        if payload["status"] != "PASS":
            failures.append("expected PASS self-test")
        chunk = payload["chunks"][0]
        if chunk["text_inspection"]["suspicious_count"] != 0:
            failures.append("unexpected suspicious text")
        if chunk["audio_metrics"]["duration_seconds"] <= 0:
            failures.append("missing audio duration")
        if chunk["audio_metrics"]["clip_ratio"] != 0:
            failures.append("unexpected clipping")
        if not payload.get("combined_audio"):
            failures.append("expected combined audio audit")
        domain = domain_normalized_comparison(
            "usa sessão residente OmniVoice e grava um log JSONL",
            "usa a sessão Resident e Omni Voice e grava um log Jason L",
        )
        if domain["status"] != "PASS":
            failures.append("expected domain-normalized comparison to pass")
        if failures:
            print(json.dumps({"status": "FAIL", "failures": failures, "payload": payload}, ensure_ascii=False, indent=2))
            return 1
    print(json.dumps({"status": "PASS", "mode": "self_test"}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit-session")
    audit.add_argument("--session-dir", required=True)
    audit.add_argument("--output")
    audit.add_argument("--stt", action="store_true")
    audit.add_argument("--require-stt", action="store_true")
    audit.add_argument("--stt-python", default=str(DEFAULT_STT_PYTHON))
    audit.add_argument("--stt-model", default=str(DEFAULT_STT_MODEL))
    audit.add_argument("--stt-language", default="portuguese")
    audit.add_argument("--max-sample-jump", type=float, default=0.5)
    audit.add_argument("--audit-combined", action="store_true")
    audit.add_argument("--strict", action="store_true")
    audit.set_defaults(func=command_audit)

    self_test = subparsers.add_parser("self-test")
    self_test.set_defaults(func=command_self_test)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
