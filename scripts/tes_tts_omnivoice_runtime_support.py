#!/usr/bin/env python3
"""Runtime helpers for the active TES TTS OmniVoice product path.

This module stays dependency-free and owns only direct/resident runtime support:
audio playback/combine helpers, resident JSONL process control, chunk planning,
and lightweight runtime monitoring. Provider CLI, review, benchmark, and
packaging surfaces remain in `tes_tts_omnivoice_provider.py`.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import queue
import re
import select
import shutil
import subprocess
import threading
import time
from typing import Any
import wave


DEFAULT_LANGUAGE = "pt"
AUTO_LANGUAGE = "auto"


def wav_duration_seconds(path: Path) -> float | None:
    try:
        with wave.open(str(path), "rb") as handle:
            return round(handle.getnframes() / handle.getframerate(), 3)
    except (wave.Error, OSError, ZeroDivisionError):
        return None


def playback_audio(output: Path) -> dict[str, Any]:
    started = time.perf_counter()
    player = shutil.which("afplay")
    if not player:
        return {"playback_status": "not_available", "player": None, "playback_wall_ms": 0.0}
    completed = subprocess.run([player, str(output)], check=False)
    return {
        "playback_status": "played" if completed.returncode == 0 else "failed",
        "player": player,
        "returncode": completed.returncode,
        "playback_wall_ms": round((time.perf_counter() - started) * 1000, 3),
    }


def combine_wav_files(inputs: list[Path], output: Path, *, silence_ms: int) -> dict[str, Any]:
    """Write one review/playback WAV from chunk WAVs with deterministic gaps."""
    started = time.perf_counter()
    existing = [path for path in inputs if path.exists()]
    if not existing:
        return {
            "combined_status": "SKIPPED",
            "reason": "no chunk wav files found",
            "combined_output": str(output),
            "combined_chunk_count": 0,
            "combine_wall_ms": round((time.perf_counter() - started) * 1000, 3),
        }

    params: wave._wave_params | None = None
    frames: list[bytes] = []
    total_frames = 0
    silence_frames = 0
    for index, path in enumerate(existing):
        with wave.open(str(path), "rb") as handle:
            current_params = handle.getparams()
            if params is None:
                params = current_params
                silence_frames = int(current_params.framerate * max(0, silence_ms) / 1000)
            elif (
                current_params.nchannels != params.nchannels
                or current_params.sampwidth != params.sampwidth
                or current_params.framerate != params.framerate
                or current_params.comptype != params.comptype
            ):
                return {
                    "combined_status": "FAIL",
                    "reason": f"incompatible WAV params at {path}",
                    "combined_output": str(output),
                    "combined_chunk_count": len(existing),
                    "combine_wall_ms": round((time.perf_counter() - started) * 1000, 3),
                }
            frames.append(handle.readframes(handle.getnframes()))
            total_frames += current_params.nframes
        if index < len(existing) - 1 and silence_frames:
            frames.append(b"\x00" * silence_frames * params.nchannels * params.sampwidth)
            total_frames += silence_frames

    assert params is not None
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as handle:
        handle.setnchannels(params.nchannels)
        handle.setsampwidth(params.sampwidth)
        handle.setframerate(params.framerate)
        handle.writeframes(b"".join(frames))
    return {
        "combined_status": "PASS",
        "combined_output": str(output),
        "combined_chunk_count": len(existing),
        "combined_silence_ms": max(0, silence_ms),
        "combined_duration_seconds": round(total_frames / params.framerate, 3),
        "combine_wall_ms": round((time.perf_counter() - started) * 1000, 3),
    }


def add_edge_silence_to_wav(path: Path, *, silence_ms: int) -> dict[str, Any]:
    silence_ms = max(0, silence_ms)
    if not silence_ms:
        return {"edge_silence_status": "SKIPPED", "edge_silence_ms": 0}
    if not path.exists():
        return {"edge_silence_status": "FAIL", "reason": "WAV missing", "edge_silence_ms": silence_ms}

    with wave.open(str(path), "rb") as handle:
        params = handle.getparams()
        frames = handle.readframes(handle.getnframes())
    silence_frames = int(params.framerate * silence_ms / 1000)
    silence = b"\x00" * silence_frames * params.nchannels * params.sampwidth
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(params.nchannels)
        handle.setsampwidth(params.sampwidth)
        handle.setframerate(params.framerate)
        handle.writeframes(silence + frames + silence)
    return {
        "edge_silence_status": "PASS",
        "edge_silence_ms": silence_ms,
        "edge_silence_frames_each_side": silence_frames,
    }


def playback_outputs(outputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in outputs:
        output = item.get("output")
        if not isinstance(output, str):
            results.append(
                {
                    "id": item.get("id"),
                    "output": output,
                    "playback_status": "missing_output",
                    "player": None,
                }
            )
            continue
        playback = playback_audio(Path(output))
        results.append(
            {
                "id": item.get("id"),
                "output": output,
                **playback,
            }
        )
        if playback.get("playback_status") == "failed":
            break
    return results


class BufferedPlaybackQueue:
    """Play generated WAV chunks on a background thread as soon as buffered."""

    def __init__(
        self,
        *,
        started_at: float,
        planned_gap_ms: int,
        monitor: RuntimeMonitor | None = None,
    ) -> None:
        self.started_at = started_at
        self.planned_gap_ms = max(0, planned_gap_ms)
        self.monitor = monitor
        self.results: list[dict[str, Any]] = []
        self.first_audio_ms: float | None = None
        self.max_unplanned_gap_ms = 0.0
        self._queue: queue.Queue[tuple[str, Path] | None] = queue.Queue()
        self._thread = threading.Thread(target=self._run, name="tes-tts-buffered-playback", daemon=True)
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        self._started = True
        self._thread.start()

    def enqueue(self, chunk_id: str, output: Path) -> None:
        self._queue.put((chunk_id, output))

    def close(self) -> None:
        if not self._started:
            return
        self._queue.put(None)
        self._thread.join()

    def _record(self, event: str, **payload: Any) -> None:
        if self.monitor is not None:
            self.monitor.record(event, **payload)

    def _run(self) -> None:
        previous_end: float | None = None
        while True:
            wait_started = time.perf_counter()
            item = self._queue.get()
            if item is None:
                return
            chunk_id, output = item
            if previous_end is not None:
                unplanned_gap_ms = round((time.perf_counter() - wait_started) * 1000, 3)
                self.max_unplanned_gap_ms = max(self.max_unplanned_gap_ms, unplanned_gap_ms)
            playback_start_ms = round((time.perf_counter() - self.started_at) * 1000, 3)
            if self.first_audio_ms is None:
                self.first_audio_ms = playback_start_ms
            self._record("buffered_playback_start", id=chunk_id, output=str(output), playback_start_ms=playback_start_ms)
            playback = playback_audio(output)
            playback_item = {
                "id": chunk_id,
                "output": str(output),
                "playback_start_ms": playback_start_ms,
                **playback,
            }
            self.results.append(playback_item)
            self._record("buffered_playback_result", **playback_item)
            previous_end = time.perf_counter()
            if self.planned_gap_ms:
                time.sleep(self.planned_gap_ms / 1000)

    def summary(self) -> dict[str, Any]:
        failed = any(item.get("playback_status") == "failed" for item in self.results)
        not_available = any(item.get("playback_status") == "not_available" for item in self.results)
        if failed:
            status = "PLAYBACK_FAILED"
        elif not_available:
            status = "PLAYBACK_NOT_AVAILABLE"
        elif self.results:
            status = "PASS"
        else:
            status = "SKIPPED"
        return {
            "status": status,
            "time_to_first_audio_ms": self.first_audio_ms,
            "played_chunk_count": len(self.results),
            "planned_gap_ms": self.planned_gap_ms,
            "max_unplanned_gap_ms": round(self.max_unplanned_gap_ms, 3),
            "playback_results": self.results,
        }


def provider_prepare_ms(kernel: Any) -> float:
    prompt_ms = kernel.prompt_metrics.get("voice_prompt_prepare_ms")
    prompt_value = prompt_ms if isinstance(prompt_ms, (int, float)) else 0
    return round(kernel.model_load_ms + prompt_value, 3)


def read_jsonl_payload(process: subprocess.Popen[str], timeout: float, label: str) -> dict[str, Any]:
    if process.stdout is None:
        raise RuntimeError(f"{label}: process stdout is unavailable")
    ready, _, _ = select.select([process.stdout], [], [], timeout)
    if not ready:
        raise TimeoutError(f"{label}: timed out after {timeout}s")
    line = process.stdout.readline()
    if not line:
        raise RuntimeError(f"{label}: process ended before emitting JSONL")
    return json.loads(line)


def wait_or_terminate(process: subprocess.Popen[str], timeout: float = 10.0) -> None:
    if process.stdin and not process.stdin.closed:
        process.stdin.close()
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


class RuntimeMonitor:
    """Append-only runtime monitor for one OmniVoice operation."""

    def __init__(self, log_path: Path, *, heartbeat_seconds: float) -> None:
        self.log_path = log_path
        self.heartbeat_seconds = max(1.0, heartbeat_seconds)
        self.started = time.perf_counter()
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._heartbeat_loop, name="tes-tts-omnivoice-monitor", daemon=True)

    def start(self) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.record("monitor_start")
        self._thread.start()

    def record(self, event: str, **payload: Any) -> None:
        item = {
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
            "elapsed_ms": round((time.perf_counter() - self.started) * 1000, 3),
            "event": event,
            **payload,
        }
        with self._lock:
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")

    def stop(self, status: str) -> None:
        self.record("monitor_stop", status=status)
        self._stop.set()
        self._thread.join(timeout=2)

    def _heartbeat_loop(self) -> None:
        while not self._stop.wait(self.heartbeat_seconds):
            self.record("heartbeat")


def split_long_text(text: str, *, max_chars: int) -> list[str]:
    max_chars = max(120, max_chars)
    normalized = "\n\n".join(part.strip() for part in text.strip().splitlines() if part.strip())
    if not normalized:
        return []
    chunks: list[str] = []
    current = ""

    def push(value: str) -> None:
        cleaned = value.strip()
        if cleaned:
            chunks.append(cleaned)

    def add_piece(piece: str) -> None:
        nonlocal current
        piece = piece.strip()
        if not piece:
            return
        if len(piece) > max_chars:
            if current:
                push(current)
                current = ""
            split_oversized_piece(piece)
            return
        candidate = f"{current} {piece}".strip() if current else piece
        if len(candidate) <= max_chars:
            current = candidate
        else:
            push(current)
            current = piece

    def split_oversized_piece(piece: str) -> None:
        words = piece.split()
        bucket = ""
        for word in words:
            candidate = f"{bucket} {word}".strip() if bucket else word
            if len(candidate) <= max_chars:
                bucket = candidate
            else:
                push(bucket)
                bucket = word
        push(bucket)

    for paragraph in re.split(r"\n\s*\n+", normalized):
        sentences = re.split(r"(?<=[.!?;:])\s+", paragraph.strip())
        for sentence in sentences:
            add_piece(sentence)
        if current:
            push(current)
            current = ""
    if current:
        push(current)
    return chunks


def infer_long_read_chunk_language(text: str, requested_language: str) -> str:
    """Resolve a synthesis language for one resident long-read chunk."""
    if requested_language != AUTO_LANGUAGE:
        return requested_language

    normalized = re.sub(r"\s+", " ", text.strip().lower())
    if not normalized:
        return DEFAULT_LANGUAGE

    portuguese_markers = {
        "agora",
        "como",
        "com",
        "de",
        "do",
        "e",
        "esse",
        "esses",
        "ficam",
        "fonema",
        "futuros",
        "nao",
        "não",
        "ou",
        "protege",
        "real",
        "suporte",
        "teste",
        "usar",
        "vamos",
    }
    english_markers = {
        "and",
        "are",
        "called",
        "english",
        "interface",
        "language",
        "limits",
        "matching",
        "names",
        "protocol",
        "runtime",
        "string",
        "technical",
        "terms",
        "the",
        "thresholds",
        "tree",
        "provider",
    }
    technical_terms = {
        "aho",
        "api",
        "corasick",
        "http",
        "json",
        "node",
        "open",
        "python",
        "thresholds",
        "trie",
        "typescript",
        "yaml",
    }
    tokens = re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9_.-]*", normalized)
    portuguese_score = sum(1 for token in tokens if token in portuguese_markers)
    english_score = sum(1 for token in tokens if token in english_markers)
    technical_score = sum(1 for token in tokens if token in technical_terms)

    if normalized.startswith((
        "english context:",
        "english technical terms:",
        "the english technical terms are",
        "english problem terms:",
    )):
        return "en"
    if english_score >= 4 and portuguese_score == 0:
        return "en"
    if technical_score >= 2 and portuguese_score == 0 and english_score >= 1:
        return "en"
    return DEFAULT_LANGUAGE


def build_long_read_plan(text: str, *, max_chars: int, language: str) -> list[dict[str, Any]]:
    return [
        {
            "id": f"chunk-{index:03d}",
            "text": chunk,
            "chars": len(chunk),
            "language": infer_long_read_chunk_language(chunk, language),
        }
        for index, chunk in enumerate(split_long_text(text, max_chars=max_chars), start=1)
    ]


def build_first_audio_long_read_plan(
    text: str,
    *,
    max_chars: int,
    language: str,
    first_audio_chars: int,
) -> list[dict[str, Any]]:
    chunks = split_long_text(text, max_chars=max_chars)
    first_audio_chars = max(0, first_audio_chars)
    if not chunks or not first_audio_chars:
        speech_chunks = chunks
    else:
        first = chunks[0]
        head, tail = split_first_audio_chunk(first, max_chars=first_audio_chars)
        speech_chunks = [head]
        if tail:
            speech_chunks.extend(split_long_text(tail, max_chars=max_chars))
        speech_chunks.extend(chunks[1:])
    return [
        {
            "id": f"chunk-{index:03d}",
            "text": chunk,
            "chars": len(chunk),
            "language": infer_long_read_chunk_language(chunk, language),
        }
        for index, chunk in enumerate(speech_chunks, start=1)
    ]


def split_first_audio_chunk(text: str, *, max_chars: int) -> tuple[str, str]:
    max_chars = max(80, max_chars)
    cleaned = text.strip()
    if len(cleaned) <= max_chars:
        return cleaned, ""

    candidates: list[int] = []
    for pattern in (r"[.!?;:]\s+", r",\s+", r"\s+"):
        candidates.extend(match.end() for match in re.finditer(pattern, cleaned[: max_chars + 1]))
    candidates = [index for index in candidates if 80 <= index <= max_chars]
    cut = max(candidates) if candidates else max_chars
    return cleaned[:cut].strip(), cleaned[cut:].strip()
