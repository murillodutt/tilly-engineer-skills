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
SENTENCE_BOUNDARY_CHARS = ".!?…。！？"
CLAUSE_BOUNDARY_CHARS = ",;:"
CLOSING_BOUNDARY_CHARS = "\"'”’)]}>»"
MIN_SPEECH_CHUNK_CHARS = 80
COMMON_DOTTED_ABBREVIATIONS = {
    "dr.",
    "dra.",
    "mr.",
    "mrs.",
    "ms.",
    "prof.",
    "sr.",
    "sra.",
    "jr.",
    "etc.",
    "e.g.",
    "i.e.",
    "vs.",
}


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
        self._batch_index = 0

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

    def _drain_ready_batch(self, first_item: tuple[str, Path]) -> tuple[list[tuple[str, Path]], bool]:
        items = [first_item]
        stop_after_batch = False
        while True:
            try:
                item = self._queue.get_nowait()
            except queue.Empty:
                break
            if item is None:
                stop_after_batch = True
                break
            items.append(item)
        return items, stop_after_batch

    def _playback_batch_output(self, items: list[tuple[str, Path]]) -> tuple[str, Path, list[str]]:
        chunk_ids = [chunk_id for chunk_id, _output in items]
        if len(items) == 1:
            return chunk_ids[0], items[0][1], chunk_ids
        self._batch_index += 1
        batch_dir = items[0][1].parent / "buffered-playback-batches"
        output = batch_dir / f"playback-batch-{self._batch_index:03d}.wav"
        combine_wav_files([path for _chunk_id, path in items], output, silence_ms=self.planned_gap_ms)
        return "+".join(chunk_ids), output, chunk_ids

    def _run(self) -> None:
        previous_end: float | None = None
        while True:
            wait_started = time.perf_counter()
            item = self._queue.get()
            if item is None:
                return
            if previous_end is not None:
                unplanned_gap_ms = round((time.perf_counter() - wait_started) * 1000, 3)
                self.max_unplanned_gap_ms = max(self.max_unplanned_gap_ms, unplanned_gap_ms)
            batch_items, stop_after_batch = self._drain_ready_batch(item)
            chunk_id, output, source_chunks = self._playback_batch_output(batch_items)
            playback_start_ms = round((time.perf_counter() - self.started_at) * 1000, 3)
            if self.first_audio_ms is None:
                self.first_audio_ms = playback_start_ms
            self._record(
                "buffered_playback_start",
                id=chunk_id,
                output=str(output),
                source_chunks=source_chunks,
                playback_start_ms=playback_start_ms,
            )
            playback = playback_audio(output)
            playback_item = {
                "id": chunk_id,
                "output": str(output),
                "source_chunks": source_chunks,
                "playback_start_ms": playback_start_ms,
                **playback,
            }
            self.results.append(playback_item)
            self._record("buffered_playback_result", **playback_item)
            previous_end = time.perf_counter()
            if stop_after_batch:
                return
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


def _last_token_ending_at(text: str, end: int) -> str:
    prefix = text[:end].rstrip()
    if not prefix:
        return ""
    return prefix.split()[-1]


def _next_non_space_char(text: str, start: int) -> str:
    index = start
    while index < len(text) and text[index] in CLOSING_BOUNDARY_CHARS:
        index += 1
    while index < len(text) and text[index].isspace():
        index += 1
    return text[index] if index < len(text) else ""


def _looks_like_decimal_period(text: str, index: int) -> bool:
    return 0 < index < len(text) - 1 and text[index - 1].isdigit() and text[index + 1].isdigit()


def _looks_like_dotted_identity(token: str) -> bool:
    if token.lower() in COMMON_DOTTED_ABBREVIATIONS:
        return True
    if re.fullmatch(r"(?:[A-Za-z]\.){1,}", token):
        return True
    return bool(re.fullmatch(r"(?:[A-Za-z][A-Za-z0-9]*\.){2,}", token))


def _is_sentence_boundary(text: str, index: int) -> bool:
    char = text[index]
    if char not in SENTENCE_BOUNDARY_CHARS:
        return False
    following = text[index + 1] if index + 1 < len(text) else ""
    if following and not following.isspace() and following not in CLOSING_BOUNDARY_CHARS and following not in ",;:":
        return False
    if char == ".":
        if _looks_like_decimal_period(text, index):
            return False
        token = _last_token_ending_at(text, index + 1)
        if _looks_like_dotted_identity(token):
            return False
        next_char = _next_non_space_char(text, index + 1)
        if next_char in {",", ";", ":"}:
            return False
    return True


def _sentence_boundary_end(text: str, index: int) -> int:
    end = index + 1
    while end < len(text) and text[end] in ".…":
        end += 1
    while end < len(text) and text[end] in CLOSING_BOUNDARY_CHARS:
        end += 1
    return end


def _split_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    start = 0
    index = 0
    while index < len(text):
        if not _is_sentence_boundary(text, index):
            index += 1
            continue
        end = _sentence_boundary_end(text, index)
        piece = text[start:end].strip()
        if piece:
            sentences.append(piece)
        start = end
        while start < len(text) and text[start].isspace():
            start += 1
        index = start
    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences or ([text.strip()] if text.strip() else [])


def _find_best_cut(text: str, *, ideal_chars: int, hard_chars: int, allow_forward: bool) -> int | None:
    min_chars = min(MIN_SPEECH_CHUNK_CHARS, max(1, hard_chars // 2))
    hard_chars = min(len(text), max(min_chars, hard_chars))
    ideal_chars = min(max(min_chars, ideal_chars), hard_chars)

    def cut_after_clause(index: int) -> int:
        end = index + 1
        while end < len(text) and text[end] in CLOSING_BOUNDARY_CHARS:
            end += 1
        return end

    def candidates_before(predicate: Any, limit: int) -> list[int]:
        values: list[int] = []
        for index, char in enumerate(text[:limit]):
            if index + 1 < min_chars:
                continue
            cut = predicate(index, char)
            if cut:
                values.append(cut)
        return values

    sentence_before = candidates_before(
        lambda index, _char: _sentence_boundary_end(text, index) if _is_sentence_boundary(text, index) else None,
        ideal_chars,
    )
    if sentence_before:
        return max(sentence_before)

    clause_before = candidates_before(
        lambda index, char: cut_after_clause(index) if char in CLAUSE_BOUNDARY_CHARS else None,
        ideal_chars,
    )
    if clause_before:
        return max(clause_before)

    if allow_forward:
        forward_limit = min(len(text), max(hard_chars, ideal_chars + MIN_SPEECH_CHUNK_CHARS))
        for index in range(ideal_chars, forward_limit):
            if _is_sentence_boundary(text, index):
                return _sentence_boundary_end(text, index)
        for index in range(ideal_chars, forward_limit):
            if text[index] in CLAUSE_BOUNDARY_CHARS:
                return cut_after_clause(index)

    whitespace = [match.end() for match in re.finditer(r"\s+", text[:ideal_chars]) if min_chars <= match.end()]
    if whitespace:
        return max(whitespace)
    return hard_chars if hard_chars < len(text) else None


def _split_overlong_sentence(text: str, *, max_chars: int) -> list[str]:
    remaining = text.strip()
    if len(remaining) <= max_chars:
        return [remaining] if remaining else []

    parts: list[str] = []
    while len(remaining) > max_chars:
        cut = _find_best_cut(
            remaining,
            ideal_chars=max_chars,
            hard_chars=max_chars,
            allow_forward=False,
        )
        if cut is None or cut <= 0:
            cut = max_chars
        parts.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        parts.append(remaining)
    return [part for part in parts if part]


def split_long_text(text: str, *, max_chars: int) -> list[str]:
    max_chars = max(120, max_chars)
    normalized = "\n\n".join(part.strip() for part in text.strip().splitlines() if part.strip())
    if not normalized:
        return []
    chunks: list[str] = []
    current = ""
    min_chars = min(MIN_SPEECH_CHUNK_CHARS, max_chars)

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

    for paragraph in re.split(r"\n\s*\n+", normalized):
        sentences = _split_sentences(paragraph.strip())
        for sentence in sentences:
            for piece in _split_overlong_sentence(sentence, max_chars=max_chars):
                add_piece(piece)
        if current:
            if chunks and len(current) < min_chars:
                candidate = f"{chunks[-1]} {current}".strip()
                if len(candidate) <= max_chars:
                    chunks[-1] = candidate
                    current = ""
            if current:
                push(current)
                current = ""
    if current:
        if chunks and len(current) < min_chars:
            candidate = f"{chunks[-1]} {current}".strip()
            if len(candidate) <= max_chars:
                chunks[-1] = candidate
                current = ""
        if current:
            push(current)
            current = ""
    return chunks


def infer_long_read_chunk_language(text: str, requested_language: str) -> str:
    """Resolve a synthesis language for one resident long-read chunk."""
    if requested_language != AUTO_LANGUAGE:
        return requested_language

    normalized = re.sub(r"\s+", " ", text.strip().lower())
    if not normalized:
        return DEFAULT_LANGUAGE

    portuguese_markers = {
        # high-frequency PT function words (governed stopword data) plus the
        # original fixture markers, so common Portuguese prose is recognized.
        "a", "ao", "aos", "agora", "as", "à", "às", "com", "como", "da", "das",
        "de", "depois", "do", "dos", "e", "em", "essa", "esse", "esses", "está",
        "eu", "ficam", "foi", "fonema", "futuros", "isso", "já", "mais", "na",
        "nao", "não", "nas", "no", "nos", "o", "os", "ou", "para", "pela", "pelo",
        "por", "protege", "que", "real", "são", "se", "ser", "seu", "sistema",
        "sua", "suporte", "teste", "um", "uma", "usar", "vamos", "é",
    }
    english_markers = {
        # high-frequency EN function words (governed stopword data) plus the
        # original fixture markers, so common English prose is recognized.
        "a", "across", "after", "an", "and", "any", "are", "as", "at", "be",
        "by", "called", "can", "english", "every", "from", "for", "in",
        "interface", "is", "it", "language", "limits", "matching", "more",
        "names", "of", "on", "or", "protocol", "provider", "run", "runtime",
        "string", "technical", "terms", "that", "the", "then", "these",
        "this", "those", "thresholds", "to", "tree", "was", "will", "with",
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
    # Proportional signal: when English function words clearly outweigh
    # Portuguese ones, the chunk is English prose even without technical terms.
    # Ambiguous or Portuguese-leaning chunks still fall through to the pt default.
    if english_score >= 2 and english_score > portuguese_score:
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
    max_chars = max(MIN_SPEECH_CHUNK_CHARS, max_chars)
    cleaned = text.strip()
    if len(cleaned) <= max_chars:
        return cleaned, ""

    cut = _find_best_cut(
        cleaned,
        ideal_chars=max_chars,
        hard_chars=min(len(cleaned), max(max_chars, max_chars + MIN_SPEECH_CHUNK_CHARS)),
        allow_forward=True,
    )
    if cut is None:
        cut = max_chars
    head = cleaned[:cut].strip()
    tail = cleaned[cut:].strip()
    if tail and len(tail) < MIN_SPEECH_CHUNK_CHARS:
        return cleaned, ""
    return head, tail
