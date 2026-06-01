#!/usr/bin/env python3
"""Direct/resident OmniVoice kernel for TES TTS.

This module owns the active local OmniVoice path without importing optional
provider dependencies at module import time. CLI, review, and packaging
surfaces stay in `tes_tts_omnivoice_provider.py`.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any

from tes_tts_runtime_adapter import (
    apply_omnivoice_prosody_warmup,
    prepare_audio_quality_text,
    prepare_redacted_provider_text,
    prepare_spoken_text,
)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def provider_text(source_text: str, locale: str, mode: str, prosody_warmup: str = "none") -> dict[str, Any]:
    if mode == "audio_quality":
        text_info = prepare_audio_quality_text(source_text, locale)
        warmup = apply_omnivoice_prosody_warmup(text_info["text"], prosody_warmup)
        text_info.update(warmup)
        return text_info
    if mode == "redacted_source":
        text_info = prepare_redacted_provider_text(source_text, locale)
        warmup = apply_omnivoice_prosody_warmup(text_info["text"], prosody_warmup)
        text_info.update(warmup)
        return text_info
    prepared = prepare_spoken_text(source_text, locale)
    if mode == "spoken_text":
        text = prepared["spoken_text"]
    else:
        text = source_text
    warmup = apply_omnivoice_prosody_warmup(text, prosody_warmup)
    return {
        "text": warmup["text"],
        "prepared": prepared,
        "mode": mode,
        "input_surface": "source_text",
        "provider_text_surface": mode,
        "prosody_warmup": warmup["prosody_warmup"],
        "prosody_warmup_tag": warmup["prosody_warmup_tag"],
        "provider_tag_inserted": warmup["provider_tag_inserted"],
    }


def load_omnivoice_modules() -> dict[str, Any]:
    missing = [name for name in ("omnivoice", "torch", "soundfile") if importlib.util.find_spec(name) is None]
    if missing:
        raise RuntimeError(f"missing optional OmniVoice dependencies: {', '.join(missing)}")
    import torch
    import soundfile as sf
    from omnivoice.models.omnivoice import OmniVoice

    return {
        "torch": torch,
        "soundfile": sf,
        "OmniVoice": OmniVoice,
    }


def best_device(torch: Any, requested: str | None) -> str:
    if requested:
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def prompt_cache_path(cache_dir: Path, model: str, ref_audio: Path, ref_text: str | None) -> Path:
    cache_key = {
        "model": model,
        "ref_audio_sha256": sha256_path(ref_audio),
        "ref_text_sha256": hashlib.sha256((ref_text or "").encode("utf-8")).hexdigest(),
    }
    key = hashlib.sha256(json.dumps(cache_key, sort_keys=True).encode("utf-8")).hexdigest()[:24]
    return cache_dir / "voice-prompts" / f"{key}.pt"


def protect_voice_prompt_cache_path(cache_path: Path) -> None:
    """Keep local cloned-voice prompt artifacts private to the current user."""
    cache_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        cache_path.parent.chmod(0o700)
    except OSError:
        pass
    if cache_path.exists():
        try:
            cache_path.chmod(0o600)
        except OSError:
            pass


def load_or_create_voice_prompt(
    *,
    model: Any,
    torch: Any,
    ref_audio: Path,
    ref_text: str | None,
    cache_path: Path,
    refresh: bool,
) -> tuple[Any, dict[str, Any]]:
    protect_voice_prompt_cache_path(cache_path)
    if cache_path.exists() and not refresh:
        started = time.perf_counter()
        prompt = torch.load(cache_path, map_location=model.device, weights_only=False)
        protect_voice_prompt_cache_path(cache_path)
        cached_ref_text = getattr(prompt, "ref_text", None)
        return prompt, {
            "voice_prompt_cache": "hit",
            "voice_prompt_cache_path": str(cache_path),
            "voice_prompt_prepare_ms": round((time.perf_counter() - started) * 1000, 3),
            "ref_text_source": "cache",
            "ref_text_present": bool(cached_ref_text),
            "ref_text_chars": len(cached_ref_text or ""),
        }

    started = time.perf_counter()
    with contextlib.redirect_stdout(sys.stderr):
        prompt = model.create_voice_clone_prompt(ref_audio=str(ref_audio), ref_text=ref_text)
    torch.save(prompt, cache_path)
    protect_voice_prompt_cache_path(cache_path)
    prompt_ref_text = getattr(prompt, "ref_text", None)
    return prompt, {
        "voice_prompt_cache": "miss",
        "voice_prompt_cache_path": str(cache_path),
        "voice_prompt_prepare_ms": round((time.perf_counter() - started) * 1000, 3),
        "ref_text_source": "provided" if ref_text else "auto_transcribed",
        "ref_text_present": bool(prompt_ref_text),
        "ref_text_chars": len(prompt_ref_text or ""),
    }


class DirectOmniVoiceKernel:
    """Resident local OmniVoice model plus one protected voice prompt."""

    def __init__(
        self,
        *,
        model: Any,
        soundfile: Any,
        voice_prompt: Any,
        device: str,
        model_load_ms: float,
        prompt_metrics: dict[str, Any],
    ) -> None:
        self.model = model
        self.soundfile = soundfile
        self.voice_prompt = voice_prompt
        self.device = device
        self.model_load_ms = model_load_ms
        self.prompt_metrics = prompt_metrics

    @classmethod
    def load(
        cls,
        *,
        model_name: str,
        ref_audio: Path,
        ref_text: str | None,
        cache_path: Path,
        refresh_prompt: bool,
        requested_device: str | None,
    ) -> "DirectOmniVoiceKernel":
        modules = load_omnivoice_modules()
        torch = modules["torch"]
        soundfile = modules["soundfile"]
        OmniVoice = modules["OmniVoice"]
        device = best_device(torch, requested_device)
        load_started = time.perf_counter()
        with contextlib.redirect_stdout(sys.stderr):
            model = OmniVoice.from_pretrained(model_name, device_map=device, dtype=torch.float16)
        model_load_ms = round((time.perf_counter() - load_started) * 1000, 3)
        prompt, prompt_metrics = load_or_create_voice_prompt(
            model=model,
            torch=torch,
            ref_audio=ref_audio,
            ref_text=ref_text,
            cache_path=cache_path,
            refresh=refresh_prompt,
        )
        return cls(
            model=model,
            soundfile=soundfile,
            voice_prompt=prompt,
            device=device,
            model_load_ms=model_load_ms,
            prompt_metrics=prompt_metrics,
        )

    def synthesize(
        self,
        *,
        text: str,
        language: str,
        output: Path,
        num_step: int,
        guidance_scale: float,
        speed: float,
        t_shift: float,
        denoise: bool,
        postprocess_output: bool,
    ) -> dict[str, Any]:
        output.parent.mkdir(parents=True, exist_ok=True)
        synthesis_started = time.perf_counter()
        with contextlib.redirect_stdout(sys.stderr):
            audios = self.model.generate(
                text=text,
                language=language,
                voice_clone_prompt=self.voice_prompt,
                num_step=num_step,
                guidance_scale=guidance_scale,
                speed=speed,
                t_shift=t_shift,
                denoise=denoise,
                postprocess_output=postprocess_output,
            )
        provider_synthesis_ms = round((time.perf_counter() - synthesis_started) * 1000, 3)
        write_started = time.perf_counter()
        self.soundfile.write(output, audios[0], self.model.sampling_rate)
        audio_write_ms = round((time.perf_counter() - write_started) * 1000, 3)
        duration_seconds = round(float(len(audios[0]) / self.model.sampling_rate), 3)
        return {
            "output": str(output),
            "generation_ms": provider_synthesis_ms,
            "provider_synthesis_ms": provider_synthesis_ms,
            "audio_write_ms": audio_write_ms,
            "audio_duration_seconds": duration_seconds,
            "rtf": round(provider_synthesis_ms / 1000 / duration_seconds, 4) if duration_seconds else None,
            "sample_rate": self.model.sampling_rate,
        }

    def synthesize_prepared(
        self,
        *,
        source_text: str,
        locale: str,
        text_mode: str,
        language: str,
        output: Path,
        args: Any,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        text_prepare_started = time.perf_counter()
        text_info = provider_text(source_text, locale, text_mode, getattr(args, "prosody_warmup", "none"))
        text_prepare_ms = round((time.perf_counter() - text_prepare_started) * 1000, 3)
        audio_metrics = self.synthesize(
            text=text_info["text"],
            language=language,
            output=output,
            num_step=args.num_step,
            guidance_scale=args.guidance_scale,
            speed=args.speed,
            t_shift=args.t_shift,
            denoise=args.denoise,
            postprocess_output=args.postprocess_output,
        )
        audio_metrics["text_prepare_ms"] = text_prepare_ms
        return text_info, audio_metrics
