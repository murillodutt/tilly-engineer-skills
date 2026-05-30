#!/usr/bin/env python3
"""Optional OmniVoice provider for TES TTS.

This script is intentionally dependency-optional. The TES package can validate
and probe it without importing OmniVoice; synthesis runs only inside an
environment where the maintainer explicitly installed `omnivoice`.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

from tes_tts_runtime_adapter import prepare_spoken_text


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.147"
DEFAULT_MODEL = "k2-fsa/OmniVoice"
DEFAULT_LANGUAGE = "pt"
DEFAULT_CACHE_DIR = ROOT / "tmp/tes-tts-omnivoice-provider"


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_python_probe(python: str) -> dict[str, Any]:
    code = r"""
import importlib.metadata as metadata
import importlib.util
import json
import sys

result = {
    "python": sys.executable,
    "omnivoice_importable": importlib.util.find_spec("omnivoice") is not None,
    "torch_importable": importlib.util.find_spec("torch") is not None,
    "soundfile_importable": importlib.util.find_spec("soundfile") is not None,
    "omnivoice_version": None,
    "torch_version": None,
    "mps_available": False,
    "cuda_available": False,
}
if result["omnivoice_importable"]:
    result["omnivoice_version"] = metadata.version("omnivoice")
if result["torch_importable"]:
    import torch
    result["torch_version"] = torch.__version__
    result["mps_available"] = bool(torch.backends.mps.is_available())
    result["cuda_available"] = bool(torch.cuda.is_available())
print(json.dumps(result))
"""
    completed = subprocess.run(
        [python, "-c", code],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        return {
            "python": python,
            "omnivoice_importable": False,
            "torch_importable": False,
            "soundfile_importable": False,
            "omnivoice_version": None,
            "torch_version": None,
            "mps_available": False,
            "cuda_available": False,
            "error": completed.stderr.strip() or completed.stdout.strip(),
        }
    return json.loads(completed.stdout)


def command_probe(args: argparse.Namespace) -> int:
    evidence = run_python_probe(args.python)
    available = (
        evidence.get("omnivoice_importable") is True
        and evidence.get("torch_importable") is True
        and evidence.get("soundfile_importable") is True
    )
    status = "provider_available" if available else "provider_not_available"
    emit(
        {
            "provider": "omnivoice",
            "status": status,
            "version": evidence.get("omnivoice_version"),
            "languages": ["pt", "en"] if available else [],
            "license_note": "OmniVoice package is Apache-2.0; model/license review remains required before redistribution.",
            "runtime_dependency": "optional_external_python_env",
            "allows_install": False,
            "allows_download": False,
            "allows_global_config_write": False,
            "certifies_provider_support": available,
            "evidence": evidence,
            "reason": "optional OmniVoice environment is usable" if available else "optional OmniVoice environment is not usable",
        }
    )
    return 0 if available else 2


def normalize_ref_audio(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            "-ac",
            "1",
            "-ar",
            "24000",
            str(output),
        ],
        check=True,
    )


def provider_text(source_text: str, locale: str, mode: str) -> dict[str, Any]:
    prepared = prepare_spoken_text(source_text, locale)
    if mode == "spoken_text":
        text = prepared["spoken_text"]
    elif mode == "redacted_source":
        text = prepared["redacted_text"].replace("`", "")
    else:
        text = source_text
    return {
        "text": text,
        "prepared": prepared,
        "mode": mode,
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


def load_or_create_voice_prompt(
    *,
    model: Any,
    torch: Any,
    ref_audio: Path,
    ref_text: str | None,
    cache_path: Path,
    refresh: bool,
) -> tuple[Any, dict[str, Any]]:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists() and not refresh:
        started = time.perf_counter()
        prompt = torch.load(cache_path, map_location=model.device, weights_only=False)
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
    prompt = model.create_voice_clone_prompt(ref_audio=str(ref_audio), ref_text=ref_text)
    torch.save(prompt, cache_path)
    prompt_ref_text = getattr(prompt, "ref_text", None)
    return prompt, {
        "voice_prompt_cache": "miss",
        "voice_prompt_cache_path": str(cache_path),
        "voice_prompt_prepare_ms": round((time.perf_counter() - started) * 1000, 3),
        "ref_text_source": "provided" if ref_text else "auto_transcribed",
        "ref_text_present": bool(prompt_ref_text),
        "ref_text_chars": len(prompt_ref_text or ""),
    }


def synthesize_once(
    *,
    model: Any,
    sf: Any,
    voice_prompt: Any,
    text: str,
    language: str,
    output: Path,
    args: argparse.Namespace,
) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    audios = model.generate(
        text=text,
        language=language,
        voice_clone_prompt=voice_prompt,
        num_step=args.num_step,
        guidance_scale=args.guidance_scale,
        speed=args.speed,
        t_shift=args.t_shift,
        denoise=args.denoise,
        postprocess_output=args.postprocess_output,
    )
    generation_ms = round((time.perf_counter() - started) * 1000, 3)
    sf.write(output, audios[0], model.sampling_rate)
    duration_seconds = round(float(len(audios[0]) / model.sampling_rate), 3)
    return {
        "output": str(output),
        "generation_ms": generation_ms,
        "audio_duration_seconds": duration_seconds,
        "rtf": round(generation_ms / 1000 / duration_seconds, 4) if duration_seconds else None,
        "sample_rate": model.sampling_rate,
    }


def command_synthesize(args: argparse.Namespace) -> int:
    modules = load_omnivoice_modules()
    torch = modules["torch"]
    sf = modules["soundfile"]
    OmniVoice = modules["OmniVoice"]
    device = best_device(torch, args.device)
    text_info = provider_text(args.text, args.locale, args.text_mode)

    total_started = time.perf_counter()
    load_started = time.perf_counter()
    model = OmniVoice.from_pretrained(args.model, device_map=device, dtype=torch.float16)
    model_load_ms = round((time.perf_counter() - load_started) * 1000, 3)
    cache_path = Path(args.prompt_cache) if args.prompt_cache else prompt_cache_path(
        Path(args.cache_dir), args.model, Path(args.ref_audio), args.ref_text
    )
    prompt, prompt_metrics = load_or_create_voice_prompt(
        model=model,
        torch=torch,
        ref_audio=Path(args.ref_audio),
        ref_text=args.ref_text,
        cache_path=cache_path,
        refresh=args.refresh_prompt,
    )
    audio_metrics = synthesize_once(
        model=model,
        sf=sf,
        voice_prompt=prompt,
        text=text_info["text"],
        language=args.language,
        output=Path(args.output),
        args=args,
    )
    emit(
        {
            "provider": "omnivoice",
            "status": "PASS",
            "version": VERSION,
            "model": args.model,
            "device": device,
            "language": args.language,
            "text_mode": text_info["mode"],
            "source_text_immutable": text_info["prepared"]["source_text_immutable"],
            "redaction_count": text_info["prepared"]["redaction_count"],
            "summary_behavior": text_info["prepared"]["summary_behavior"],
            "command_execution": text_info["prepared"]["command_execution"],
            "model_load_ms": model_load_ms,
            **prompt_metrics,
            **audio_metrics,
            "total_ms": round((time.perf_counter() - total_started) * 1000, 3),
        }
    )
    return 0


def load_text_cases(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return data["cases"]


def command_batch(args: argparse.Namespace) -> int:
    modules = load_omnivoice_modules()
    torch = modules["torch"]
    sf = modules["soundfile"]
    OmniVoice = modules["OmniVoice"]
    device = best_device(torch, args.device)
    cases = load_text_cases(Path(args.cases))

    total_started = time.perf_counter()
    load_started = time.perf_counter()
    model = OmniVoice.from_pretrained(args.model, device_map=device, dtype=torch.float16)
    model_load_ms = round((time.perf_counter() - load_started) * 1000, 3)
    cache_path = Path(args.prompt_cache) if args.prompt_cache else prompt_cache_path(
        Path(args.cache_dir), args.model, Path(args.ref_audio), args.ref_text
    )
    prompt, prompt_metrics = load_or_create_voice_prompt(
        model=model,
        torch=torch,
        ref_audio=Path(args.ref_audio),
        ref_text=args.ref_text,
        cache_path=cache_path,
        refresh=args.refresh_prompt,
    )

    outputs: list[dict[str, Any]] = []
    out_dir = Path(args.output_dir)
    for index, case in enumerate(cases, start=1):
        case_id = case.get("id") or f"case-{index:03d}"
        source_text = case["text"]
        text_info = provider_text(source_text, args.locale, args.text_mode)
        output = out_dir / f"{index:02d}-{case_id}.wav"
        metrics = synthesize_once(
            model=model,
            sf=sf,
            voice_prompt=prompt,
            text=text_info["text"],
            language=case.get("language", args.language),
            output=output,
            args=args,
        )
        outputs.append(
            {
                "id": case_id,
                "text_mode": text_info["mode"],
                "redaction_count": text_info["prepared"]["redaction_count"],
                **metrics,
            }
        )

    emit(
        {
            "provider": "omnivoice",
            "status": "PASS",
            "version": VERSION,
            "model": args.model,
            "device": device,
            "language": args.language,
            "model_load_ms": model_load_ms,
            **prompt_metrics,
            "outputs": outputs,
            "total_ms": round((time.perf_counter() - total_started) * 1000, 3),
        }
    )
    return 0


def add_runtime_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--language", default=DEFAULT_LANGUAGE)
    parser.add_argument("--locale", default="pt-BR")
    parser.add_argument("--ref-audio", required=True)
    parser.add_argument("--ref-text")
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    parser.add_argument("--prompt-cache")
    parser.add_argument("--refresh-prompt", action="store_true")
    parser.add_argument("--device")
    parser.add_argument(
        "--text-mode",
        choices=["redacted_source", "spoken_text", "raw"],
        default="redacted_source",
    )
    parser.add_argument("--num-step", type=int, default=32)
    parser.add_argument("--guidance-scale", type=float, default=2.0)
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--t-shift", type=float, default=0.1)
    parser.add_argument("--denoise", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--postprocess-output", action=argparse.BooleanOptionalAction, default=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TES TTS optional OmniVoice provider")
    subparsers = parser.add_subparsers(dest="command", required=True)

    probe = subparsers.add_parser("probe")
    probe.add_argument("--python", default=sys.executable)
    probe.set_defaults(func=command_probe)

    normalize = subparsers.add_parser("normalize-ref")
    normalize.add_argument("--input", required=True)
    normalize.add_argument("--output", required=True)
    normalize.set_defaults(func=lambda args: normalize_ref_audio(Path(args.input), Path(args.output)) or 0)

    synthesize = subparsers.add_parser("synthesize")
    add_runtime_args(synthesize)
    synthesize.add_argument("--text", required=True)
    synthesize.add_argument("--output", required=True)
    synthesize.set_defaults(func=command_synthesize)

    batch = subparsers.add_parser("batch")
    add_runtime_args(batch)
    batch.add_argument("--cases", required=True)
    batch.add_argument("--output-dir", required=True)
    batch.set_defaults(func=command_batch)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        emit(
            {
                "provider": "omnivoice",
                "status": "FAIL",
                "version": VERSION,
                "error": str(exc),
            }
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
