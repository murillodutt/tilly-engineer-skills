#!/usr/bin/env python3
"""Optional OmniVoice provider for TES TTS.

This script is intentionally dependency-optional. The TES package can validate
and probe it without importing OmniVoice; synthesis runs only inside an
environment where the maintainer explicitly installed `omnivoice`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any
import zipfile

import tes_tts_omnivoice_direct_kernel as direct_kernel
from tes_tts_omnivoice_runtime_support import (
    BufferedPlaybackQueue,
    RuntimeMonitor,
    add_edge_silence_to_wav,
    build_first_audio_long_read_plan,
    build_long_read_plan,
    combine_wav_files,
    playback_audio,
    playback_outputs,
    provider_prepare_ms,
    read_jsonl_payload,
    wait_or_terminate,
    wav_duration_seconds,
)


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.150"
DEFAULT_MODEL = "k2-fsa/OmniVoice"
DEFAULT_LANGUAGE = "pt"
AUTO_LANGUAGE = "auto"
GLOBAL_RUNTIME_DIR = Path.home() / ".tes/runtime/tes-tts/omnivoice"
LEGACY_PROJECT_RUNTIME_DIR = ROOT / ".tes/runtime/tes-tts/omnivoice"
DEFAULT_RUNTIME_DIR = GLOBAL_RUNTIME_DIR
DEFAULT_VOICE_PROFILE = "tes-tts-local-clone"
DEFAULT_PROFILE_DIR = DEFAULT_RUNTIME_DIR / "profiles"
DEFAULT_CACHE_DIR = DEFAULT_RUNTIME_DIR / "provider-cache"
DEFAULT_LOCAL_PYTHON = DEFAULT_RUNTIME_DIR / "venv/bin/python"
DEFAULT_LOCAL_REF_AUDIO = DEFAULT_RUNTIME_DIR / "refs/audio-modelo-clone-mono24k.wav"
DEFAULT_OUTPUT_DIR = DEFAULT_CACHE_DIR / "audio"
DEFAULT_BENCHMARK_CASES = ROOT / "benchmarks/tes-tts/omnivoice-provider-cases.json"
DEFAULT_LIVE_SMOKE_CASES = ROOT / "benchmarks/tes-tts/live-session-utterance-fixtures.json"
DEFAULT_BENCHMARK_DIR = DEFAULT_CACHE_DIR / "benchmarks"
DEFAULT_SESSION_DIR = DEFAULT_CACHE_DIR / "sessions"
DEFAULT_LONG_READ_DIR = DEFAULT_CACHE_DIR / "long-reads"
DEFAULT_RUNTIME_LOG_DIR = DEFAULT_CACHE_DIR / "runtime-logs"
ENV_PYTHON = "TES_TTS_OMNIVOICE_PYTHON"
ENV_REF_AUDIO = "TES_TTS_OMNIVOICE_REF_AUDIO"
ENV_OUTPUT_DIR = "TES_TTS_OMNIVOICE_OUTPUT_DIR"
ENV_BENCHMARK_DIR = "TES_TTS_OMNIVOICE_BENCHMARK_DIR"
LATENCY_PROFILES = {
    "fast": {"num_step": 8, "description": "lowest latency; audible quality must be reviewed per session"},
    "balanced": {"num_step": 16, "description": "middle ground for live iteration"},
    "quality": {"num_step": 32, "description": "current quality-preserving default"},
}
LATENCY_PROFILE_CHOICES = ("auto", *tuple(sorted(LATENCY_PROFILES)))
PROFILE_RECOMMENDATION_ORDER = ("fast", "balanced", "quality")
ACTIVE_PRODUCT_PATH = "direct_resident_omnivoice"
PROSODY_WARMUP_CHOICES = ("none", "confirmation-en", "question-en", "sigh")
LONG_READ_PROSODY_WARMUP_SCOPES = ("first_chunk_only", "each_chunk")
LONG_READ_PROFILE_CHOICES = ("manual", "technical-live", "technical-hd", "technical-quality", "technical-streamer")
DEFAULT_LONG_READ_PROFILE = "technical-live"
PTBR_TECHNICAL_INSTRUCT = "male, middle-aged, low pitch"
LONG_READ_LIVE_PROFILE = {
    "language": "en",
    "text_mode": "redacted_source",
    "prosody_warmup": "none",
    "prosody_warmup_scope": "none",
    "instruct": PTBR_TECHNICAL_INSTRUCT,
    "latency_profile": "quality",
    "num_step": 28,
    "chunk_chars": 420,
    "inter_chunk_silence_ms": 450,
    "combine": True,
    "first_audio_buffered": True,
    "first_audio_chars": 160,
    "first_audio_buffer_chunks": 2,
    "first_audio_max_unplanned_gap_ms": 1200.0,
}
LONG_READ_HD_PROFILE = {
    "language": "en",
    "text_mode": "redacted_source",
    "prosody_warmup": "none",
    "prosody_warmup_scope": "none",
    "instruct": PTBR_TECHNICAL_INSTRUCT,
    "latency_profile": "quality",
    "num_step": 32,
    "chunk_chars": 420,
    "inter_chunk_silence_ms": 450,
    "combine": True,
    "first_audio_buffered": False,
    "first_audio_chars": 160,
    "first_audio_buffer_chunks": 2,
    "first_audio_max_unplanned_gap_ms": 1200.0,
}
LONG_READ_PROFILES = {
    "technical-live": dict(LONG_READ_LIVE_PROFILE),
    "technical-streamer": dict(LONG_READ_LIVE_PROFILE),
    "technical-hd": dict(LONG_READ_HD_PROFILE),
    "technical-quality": dict(LONG_READ_HD_PROFILE),
}


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def emit_jsonl(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


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


def resolve_provider_python(explicit: str | None) -> tuple[str, str]:
    if explicit:
        return explicit, "arg"
    env_value = os.environ.get(ENV_PYTHON)
    if env_value:
        return env_value, "env"
    if DEFAULT_LOCAL_PYTHON.exists():
        return str(DEFAULT_LOCAL_PYTHON), "global_auto"
    return sys.executable, "current_python"


def voice_profile_dir(profile_name: str) -> Path:
    return DEFAULT_PROFILE_DIR / profile_name


def load_voice_profile(profile_name: str | None) -> tuple[dict[str, Any] | None, str]:
    if not profile_name or profile_name == "none":
        return None, "none"
    path = voice_profile_dir(profile_name) / "meta.json"
    if not path.exists():
        return None, "missing"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data, str(path)


def apply_voice_profile_defaults(args: argparse.Namespace) -> None:
    profile_name = getattr(args, "voice_profile", None)
    profile, profile_source = load_voice_profile(profile_name)
    setattr(args, "_voice_profile_source", profile_source)
    if not profile:
        return
    profile_root = voice_profile_dir(str(profile_name))
    profile_ref_audio = profile.get("ref_audio")
    if (
        profile_ref_audio
        and not getattr(args, "ref_audio", None)
        and not os.environ.get(ENV_REF_AUDIO)
    ):
        ref_audio = Path(str(profile_ref_audio))
        if not ref_audio.is_absolute():
            ref_audio = (profile_root / ref_audio).resolve()
        args.ref_audio = str(ref_audio)
        setattr(args, "_ref_audio_source", f"voice_profile:{profile_name}")
    if profile.get("ref_text") and not getattr(args, "ref_text", None):
        args.ref_text = str(profile["ref_text"])
        setattr(args, "_ref_text_source", f"voice_profile:{profile_name}")


def resolve_ref_audio(explicit: str | None, explicit_source: str | None = None) -> tuple[Path | None, str]:
    if explicit:
        return Path(explicit), explicit_source or "arg"
    env_value = os.environ.get(ENV_REF_AUDIO)
    if env_value:
        return Path(env_value), "env"
    if DEFAULT_LOCAL_REF_AUDIO.exists():
        return DEFAULT_LOCAL_REF_AUDIO, "global_auto"
    return None, "missing"


def resolve_runtime_ref_audio(args: argparse.Namespace) -> tuple[Path | None, str]:
    return resolve_ref_audio(getattr(args, "ref_audio", None), getattr(args, "_ref_audio_source", None))


def octal_mode(path: Path) -> str | None:
    try:
        return format(path.stat().st_mode & 0o777, "04o")
    except FileNotFoundError:
        return None


def runtime_cache_status(runtime_root: Path) -> dict[str, Any]:
    cache_dir = runtime_root / "provider-cache"
    voice_prompt_dir = cache_dir / "voice-prompts"
    if not voice_prompt_dir.exists():
        return {
            "status": "missing",
            "cache_dir": str(cache_dir),
            "voice_prompt_cache_dir": str(voice_prompt_dir),
            "voice_prompt_cache_dir_mode": None,
            "voice_prompt_cache_file_count": 0,
            "unprotected_voice_prompt_cache_files": [],
        }
    prompt_files = sorted(voice_prompt_dir.glob("*.pt"))
    unprotected = [
        str(path)
        for path in prompt_files
        if octal_mode(path) != "0600"
    ]
    dir_mode = octal_mode(voice_prompt_dir)
    status = "protected" if dir_mode == "0700" and not unprotected else "needs_permission_review"
    return {
        "status": status,
        "cache_dir": str(cache_dir),
        "voice_prompt_cache_dir": str(voice_prompt_dir),
        "voice_prompt_cache_dir_mode": dir_mode,
        "voice_prompt_cache_file_count": len(prompt_files),
        "unprotected_voice_prompt_cache_files": unprotected,
    }


def runtime_descriptor(runtime_root: Path, profile_name: str) -> dict[str, Any]:
    profile_path = runtime_root / "profiles" / profile_name / "meta.json"
    python_path = runtime_root / "venv/bin/python"
    reference_wav = runtime_root / "refs/audio-modelo-clone-mono24k.wav"
    return {
        "root": str(runtime_root),
        "present": runtime_root.exists(),
        "valid": python_path.exists() and reference_wav.exists() and profile_path.exists(),
        "provider_python": str(python_path),
        "provider_python_exists": python_path.exists(),
        "profile": profile_name,
        "profile_meta": str(profile_path),
        "profile_exists": profile_path.exists(),
        "reference_wav": str(reference_wav),
        "reference_wav_exists": reference_wav.exists(),
        "cache_status": runtime_cache_status(runtime_root),
    }


def runtime_diagnostics(profile_name: str | None) -> dict[str, Any]:
    profile = profile_name or DEFAULT_VOICE_PROFILE
    global_runtime = runtime_descriptor(GLOBAL_RUNTIME_DIR, profile)
    legacy_runtime = runtime_descriptor(LEGACY_PROJECT_RUNTIME_DIR, profile)
    if global_runtime["valid"]:
        active_runtime = global_runtime
        migration_status = "legacy_present" if legacy_runtime["present"] else "PASS"
    elif legacy_runtime["present"]:
        active_runtime = None
        migration_status = "NEEDS_MIGRATION"
    else:
        active_runtime = None
        migration_status = "needs_setup"
    return {
        "global_runtime": global_runtime,
        "legacy_project_runtime": legacy_runtime,
        "active_runtime": active_runtime,
        "migration_status": migration_status,
        "migration_source": legacy_runtime["root"] if migration_status == "NEEDS_MIGRATION" else None,
        "migration_destination": global_runtime["root"] if migration_status == "NEEDS_MIGRATION" else None,
        "profile": {
            "id": profile,
            "default": DEFAULT_VOICE_PROFILE,
            "active_profile_meta": active_runtime["profile_meta"] if active_runtime else None,
        },
        "cache_status": active_runtime["cache_status"] if active_runtime else global_runtime["cache_status"],
    }


def default_output_path(output: str | None) -> Path:
    if output:
        return Path(output)
    out_dir = Path(os.environ.get(ENV_OUTPUT_DIR, str(DEFAULT_OUTPUT_DIR)))
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return out_dir / f"tes-tts-omnivoice-{stamp}.wav"


def default_benchmark_dir(output_dir: str | None) -> Path:
    if output_dir:
        return Path(output_dir)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return DEFAULT_BENCHMARK_DIR / stamp


def default_session_dir(output_dir: str | None) -> Path:
    if output_dir:
        return Path(output_dir)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return DEFAULT_SESSION_DIR / stamp


def default_long_read_dir(output_dir: str | None) -> Path:
    if output_dir:
        return Path(output_dir)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return DEFAULT_LONG_READ_DIR / stamp


def default_runtime_log_path(log_path: str | None, session_id: str) -> Path:
    if log_path:
        return Path(log_path)
    return DEFAULT_RUNTIME_LOG_DIR / f"{session_id}.jsonl"


def command_status(args: argparse.Namespace) -> int:
    provider_python, python_source = resolve_provider_python(args.python)
    ref_audio, ref_source = resolve_runtime_ref_audio(args)
    diagnostics = runtime_diagnostics(getattr(args, "voice_profile", DEFAULT_VOICE_PROFILE))
    evidence = run_python_probe(provider_python)
    provider_available = (
        evidence.get("omnivoice_importable") is True
        and evidence.get("torch_importable") is True
        and evidence.get("soundfile_importable") is True
    )
    ref_audio_ready = bool(ref_audio and ref_audio.exists())
    ready = provider_available and ref_audio_ready
    status = (
        "ready"
        if ready
        else ("NEEDS_MIGRATION" if diagnostics["migration_status"] == "NEEDS_MIGRATION" else "needs_setup")
    )
    emit(
        {
            "provider": "omnivoice",
            "status": status,
            "version": VERSION,
            "runtime_dependency": "optional_external_python_env",
            "global_runtime": diagnostics["global_runtime"],
            "legacy_project_runtime": diagnostics["legacy_project_runtime"],
            "active_runtime": diagnostics["active_runtime"],
            "migration_status": diagnostics["migration_status"],
            "migration_source": diagnostics["migration_source"],
            "migration_destination": diagnostics["migration_destination"],
            "profile": diagnostics["profile"],
            "reference_wav": {
                "path": str(ref_audio) if ref_audio else None,
                "source": ref_source,
                "ready": ref_audio_ready,
                "identity": "audio-modelo-clone-mono24k.wav",
            },
            "cache_status": diagnostics["cache_status"],
            "provider_python": provider_python,
            "provider_python_source": python_source,
            "ref_audio": str(ref_audio) if ref_audio else None,
            "ref_audio_source": ref_source,
            "ref_audio_ready": ref_audio_ready,
            "allows_install": False,
            "allows_download": False,
            "allows_global_config_write": False,
            "evidence": evidence,
        }
    )
    return 0 if ready else 2


def common_runtime_arg_tokens(args: argparse.Namespace, ref_audio: Path) -> list[str]:
    apply_latency_profile(args)
    tokens = [
        "--model",
        args.model,
        "--language",
        args.language,
        "--locale",
        args.locale,
        "--ref-audio",
        str(ref_audio),
        "--cache-dir",
        args.cache_dir,
        "--latency-profile",
        args.latency_profile,
        "--text-mode",
        args.text_mode,
        "--prosody-warmup",
        args.prosody_warmup,
        "--num-step",
        str(args.num_step),
        "--guidance-scale",
        str(args.guidance_scale),
        "--speed",
        str(args.speed),
        "--t-shift",
        str(args.t_shift),
        "--denoise" if args.denoise else "--no-denoise",
        "--postprocess-output" if args.postprocess_output else "--no-postprocess-output",
    ]
    if getattr(args, "instruct", None):
        tokens.extend(["--instruct", args.instruct])
    return tokens


def apply_latency_profile(args: argparse.Namespace) -> argparse.Namespace:
    requested_profile = getattr(args, "requested_latency_profile", getattr(args, "latency_profile", "auto"))
    profile = requested_profile
    source = "explicit"
    if requested_profile == "auto":
        benchmark_dir = os.environ.get(ENV_BENCHMARK_DIR)
        profile, source = resolve_auto_latency_profile(benchmark_dir)
    args.requested_latency_profile = requested_profile
    args.latency_profile = profile
    args.latency_profile_source = source
    if getattr(args, "num_step", None) is None:
        args.num_step = LATENCY_PROFILES[profile]["num_step"]
    return args


def apply_long_read_profile(args: argparse.Namespace) -> argparse.Namespace:
    profile = getattr(args, "read_profile", "manual")
    if profile == "manual":
        return args
    values = LONG_READ_PROFILES[profile]
    for key, value in values.items():
        setattr(args, key, value)
    return args


def effective_prosody_warmup_scope(args: argparse.Namespace) -> str:
    if getattr(args, "prosody_warmup", "none") == "none":
        return "none"
    return getattr(args, "prosody_warmup_scope", "first_chunk_only")


def prosody_warmup_for_chunk(args: argparse.Namespace, index: int) -> str:
    if getattr(args, "prosody_warmup", "none") == "none":
        return "none"
    if effective_prosody_warmup_scope(args) == "each_chunk":
        return args.prosody_warmup
    return args.prosody_warmup if index == 1 else "none"


def latency_profile_metadata(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "requested_latency_profile": getattr(args, "requested_latency_profile", getattr(args, "latency_profile", None)),
        "latency_profile_source": getattr(args, "latency_profile_source", "explicit"),
    }


def timing_attribution_metadata(execution: str) -> dict[str, Any]:
    return {
        "timing_attribution": {
            "execution": execution,
            "text_prepare_ms": "TES request-local text preparation only",
            "provider_prepare_ms": "local optional provider model load plus voice prompt preparation",
            "provider_synthesis_ms": "local optional provider audio generation only",
            "generation_ms": "compatibility alias for provider_synthesis_ms",
            "audio_write_ms": "provider output file write only",
            "combine_wall_ms": "post-synthesis WAV combine; excluded from provider timing",
            "playback_wall_ms": "local playback only; excluded from provider timing",
            "total_wall_ms": "command wall time for this local process",
        }
    }


def resolve_auto_latency_profile(benchmark_dir: str | None = None) -> tuple[str, str]:
    review_html, source = resolve_review_html(None, benchmark_dir)
    if review_html is None:
        return "quality", "auto_fallback_no_review"
    decision_json = review_html.parent / "review-decision.json"
    if not decision_json.exists():
        return "quality", f"auto_fallback_no_decision:{source}"
    try:
        decision_payload = json.loads(decision_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "quality", f"auto_fallback_invalid_decision:{source}"
    if decision_payload.get("decision") != "AUDIO_CANDIDATE":
        return "quality", f"auto_fallback_not_candidate:{source}"
    recommended = decision_payload.get("recommended_latency_profile")
    if isinstance(recommended, str) and recommended in LATENCY_PROFILES:
        return recommended, f"auto_sealed_candidate:{source}"
    return "quality", f"auto_fallback_no_recommended_profile:{source}"


def synthesize_runtime_arg_tokens(args: argparse.Namespace, ref_audio: Path, output: Path) -> list[str]:
    return [
        *common_runtime_arg_tokens(args, ref_audio),
        "--output",
        str(output),
    ]


def prompt_cache_path_from_args(args: argparse.Namespace, ref_audio: Path) -> Path:
    if args.prompt_cache:
        return Path(args.prompt_cache)
    return direct_kernel.prompt_cache_path(Path(args.cache_dir), args.model, ref_audio, args.ref_text)


def safe_file_stem(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in value.strip())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return cleaned[:80] or "utterance"


def open_local_file(path: Path) -> dict[str, Any]:
    opener = shutil.which("open")
    if not opener:
        return {"open_status": "not_available", "opener": None}
    completed = subprocess.run([opener, str(path)], check=False)
    return {
        "open_status": "opened" if completed.returncode == 0 else "failed",
        "opener": opener,
        "returncode": completed.returncode,
    }


def live_smoke_package_files(result_json: Path) -> list[Path]:
    root = result_json.parent
    files: list[Path] = [result_json.resolve()]
    review_html = root / "review.html"
    if review_html.is_file():
        files.append(review_html.resolve())
    review_decision = root / "review-decision.json"
    if review_decision.is_file():
        files.append(review_decision.resolve())
    try:
        payload = json.loads(result_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        payload = {}
    outputs = payload.get("outputs")
    if isinstance(outputs, list):
        for item in outputs:
            if not isinstance(item, dict) or not isinstance(item.get("output"), str):
                continue
            candidate = Path(item["output"])
            if candidate.is_file() and is_relative_to(candidate, root):
                files.append(candidate.resolve())
    unique: dict[str, Path] = {}
    for item in files:
        unique[str(item.resolve())] = item
    return [unique[key] for key in sorted(unique)]


def write_live_smoke_package(result_json: Path, package_path: Path) -> dict[str, Any]:
    files = live_smoke_package_files(result_json)
    root = result_json.parent
    manifest = {
        "schema": "tes-tts-omnivoice-live-smoke-package@1",
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "provider": "omnivoice",
        "version": VERSION,
        "result_json": result_json.name,
        "files": [
            {
                "path": str(item.resolve().relative_to(root.resolve())),
                "bytes": item.stat().st_size,
                "sha256": sha256_path(item),
            }
            for item in files
        ],
        "allows_install": False,
        "allows_download": False,
        "allows_global_config_write": False,
    }
    package_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(package_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in files:
            archive.write(item, arcname=str(item.resolve().relative_to(root.resolve())))
        archive.writestr("live-smoke-package-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return {
        "package_zip": str(package_path),
        "package_sha256": sha256_path(package_path),
        "package_bytes": package_path.stat().st_size,
        "file_count": len(files),
        "included_files": [item["path"] for item in manifest["files"]],
        "manifest_schema": manifest["schema"],
    }


def redacted_case_text(case: dict[str, Any], locale: str) -> str:
    text = case.get("text")
    if not isinstance(text, str):
        text = case.get("source_text")
    if not isinstance(text, str):
        return ""
    return direct_kernel.provider_text(text, locale, "spoken_text")["prepared"]["redacted_text"]


def write_benchmark_review(
    *,
    payload: dict[str, Any],
    cases_path: Path,
    output_dir: Path,
    locale: str,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    result_json = output_dir / "result.json"
    review_html = output_dir / "review.html"
    payload["result_json"] = str(result_json)
    payload["review_html"] = str(review_html)
    result_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    cases_by_id = {str(case.get("id")): case for case in load_text_cases(cases_path)}
    rows: list[str] = []
    for item in payload.get("outputs", []):
        if not isinstance(item, dict):
            continue
        case_id = str(item.get("id", ""))
        case = cases_by_id.get(case_id, {})
        output = item.get("output")
        audio_name = Path(output).name if isinstance(output, str) else ""
        source = html.escape(redacted_case_text(case, locale))
        rows.append(
            "\n".join(
                [
                    f"<section class=\"case\" data-case-id=\"{html.escape(case_id)}\" data-audio=\"{html.escape(audio_name)}\">",
                    f"<h2>{html.escape(case_id)}</h2>",
                    f"<audio controls src=\"{html.escape(audio_name)}\"></audio>",
                    "<dl>",
                    f"<dt>RTF</dt><dd>{html.escape(str(item.get('rtf')))}</dd>",
                    f"<dt>Duration</dt><dd>{html.escape(str(item.get('audio_duration_seconds')))}s</dd>",
                    f"<dt>Generation</dt><dd>{html.escape(str(item.get('generation_ms')))}ms</dd>",
                    f"<dt>Redactions</dt><dd>{html.escape(str(item.get('redaction_count')))}</dd>",
                    "</dl>",
                    f"<p>{source}</p>",
                    "<fieldset class=\"scorecard\">",
                    "<legend>Avaliacao audivel</legend>",
                    "<label>Geral <input data-score=\"overall\" type=\"number\" min=\"0\" max=\"10\" step=\"0.5\" placeholder=\"0-10\"></label>",
                    "<label>Pronuncia <input data-score=\"pronunciation\" type=\"number\" min=\"0\" max=\"10\" step=\"0.5\" placeholder=\"0-10\"></label>",
                    "<label>Termos tecnicos <input data-score=\"technical_terms\" type=\"number\" min=\"0\" max=\"10\" step=\"0.5\" placeholder=\"0-10\"></label>",
                    "<label>Naturalidade <input data-score=\"naturalness\" type=\"number\" min=\"0\" max=\"10\" step=\"0.5\" placeholder=\"0-10\"></label>",
                    "<label class=\"notes\">Notas <textarea data-score=\"notes\" rows=\"3\" placeholder=\"O que ficou bom, ruim ou precisa repetir\"></textarea></label>",
                    "</fieldset>",
                    "</section>",
                ]
            )
        )

    summary = payload.get("benchmark_summary", {})
    html_text = "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"pt-BR\">",
            "<head>",
            "<meta charset=\"utf-8\">",
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
            "<title>TES TTS OmniVoice Review</title>",
            "<style>",
            "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:32px;line-height:1.45;color:#1f2933;background:#f7f8fa}",
            "main{max-width:960px;margin:0 auto}",
            ".case{background:white;border:1px solid #d9dee7;border-radius:8px;padding:18px;margin:18px 0}",
            "audio{width:100%;margin:8px 0 12px}",
            "dl{display:grid;grid-template-columns:140px 1fr;gap:4px 12px;margin:0 0 12px}",
            "dt{font-weight:700;color:#394655}dd{margin:0}p{white-space:pre-wrap}",
            ".actions{position:sticky;top:0;background:#111827;color:white;border-radius:8px;padding:14px 16px;margin:18px 0;z-index:1}",
            ".actions button{margin:4px 8px 4px 0;padding:8px 12px;border:0;border-radius:6px;background:#e5e7eb;color:#111827;font-weight:700;cursor:pointer}",
            ".scorecard{border:1px solid #d9dee7;border-radius:8px;margin-top:14px;padding:12px;display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}",
            ".scorecard legend{font-weight:700}.scorecard input,.scorecard textarea{box-sizing:border-box;width:100%;margin-top:4px}.notes{grid-column:1/-1}",
            "</style>",
            "</head>",
            f"<body data-result-json=\"{html.escape(str(result_json))}\">",
            "<main>",
            "<h1>TES TTS OmniVoice Review</h1>",
            f"<p>Status: {html.escape(str(payload.get('status')))}. Provider timing scope: {html.escape(str(summary.get('provider_timing_scope')))}.</p>",
            "<dl>",
            f"<dt>Cases</dt><dd>{html.escape(str(summary.get('case_count')))}</dd>",
            f"<dt>Average RTF</dt><dd>{html.escape(str(summary.get('avg_rtf')))}</dd>",
            f"<dt>Total Audio</dt><dd>{html.escape(str(summary.get('total_audio_duration_seconds')))}s</dd>",
            f"<dt>Total Generation</dt><dd>{html.escape(str(summary.get('total_generation_ms')))}ms</dd>",
            "</dl>",
            "<section class=\"actions\" aria-label=\"Review actions\">",
            "<strong id=\"decision\">PENDING_REVIEW</strong>",
            "<div>",
            "<button type=\"button\" id=\"saveReview\">Salvar no navegador</button>",
            "<button type=\"button\" id=\"exportReview\">Exportar JSON</button>",
            "<button type=\"button\" id=\"copyReview\">Copiar resumo</button>",
            "</div>",
            "</section>",
            *rows,
            "<script>",
            "const key='tes-tts-omnivoice-review:'+document.body.dataset.resultJson;",
            "function n(v){if(v==='')return null;const x=Number(v);return Number.isFinite(x)?x:null}",
            "function collect(){const cases=[...document.querySelectorAll('.case')].map(c=>{const scores={};c.querySelectorAll('[data-score]').forEach(el=>{scores[el.dataset.score]=el.tagName==='TEXTAREA'?el.value:n(el.value)});return {id:c.dataset.caseId,audio:c.dataset.audio,scores};});const scored=cases.filter(c=>['overall','pronunciation','technical_terms','naturalness'].every(k=>typeof c.scores[k]==='number'));let decision='PENDING_REVIEW';if(scored.length===cases.length&&cases.length){const mins=scored.map(c=>Math.min(c.scores.overall,c.scores.pronunciation,c.scores.technical_terms,c.scores.naturalness));const avg=mins.reduce((a,b)=>a+b,0)/mins.length;decision=mins.every(v=>v>=8)?'AUDIO_CANDIDATE':avg>=7?'NEEDS_TARGETED_FIX':'NEEDS_FIX';}return {schema:'tes-tts-omnivoice-review@1',created_at:new Date().toISOString(),result_json:document.body.dataset.resultJson,decision,cases};}",
            "function render(){document.getElementById('decision').textContent=collect().decision}",
            "document.addEventListener('input',render);",
            "document.getElementById('saveReview').onclick=()=>{const data=collect();localStorage.setItem(key,JSON.stringify(data));render()};",
            "document.getElementById('exportReview').onclick=()=>{const blob=new Blob([JSON.stringify(collect(),null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='tes-tts-omnivoice-review.json';a.click();URL.revokeObjectURL(a.href)};",
            "document.getElementById('copyReview').onclick=async()=>{const data=collect();const text=`${data.decision}: ${data.cases.map(c=>`${c.id} geral=${c.scores.overall??'?'}`).join('; ')}`;if(navigator.clipboard)await navigator.clipboard.writeText(text)};",
            "try{const saved=JSON.parse(localStorage.getItem(key)||'null');if(saved&&Array.isArray(saved.cases)){saved.cases.forEach(item=>{const c=document.querySelector(`.case[data-case-id=\"${CSS.escape(item.id)}\"]`);if(!c)return;Object.entries(item.scores||{}).forEach(([k,v])=>{const el=c.querySelector(`[data-score=\"${k}\"]`);if(el)el.value=v??''})})}}catch{}render();",
            "</script>",
            "</main>",
            "</body>",
            "</html>",
        ]
    )
    review_html.write_text(html_text, encoding="utf-8")
    return {"result_json": str(result_json), "review_html": str(review_html)}


def write_profile_review(
    *,
    payload: dict[str, Any],
    cases_path: Path,
    output_dir: Path,
    locale: str,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    result_json = output_dir / "result.json"
    review_html = output_dir / "review.html"
    payload["result_json"] = str(result_json)
    payload["review_html"] = str(review_html)
    result_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    cases_by_id = {str(case.get("id")): case for case in load_text_cases(cases_path)}
    outputs_by_case: dict[str, list[dict[str, Any]]] = {}
    for item in payload.get("outputs", []):
        if isinstance(item, dict):
            outputs_by_case.setdefault(str(item.get("id", "")), []).append(item)

    sections: list[str] = []
    for case_id, items in outputs_by_case.items():
        case = cases_by_id.get(case_id, {})
        source = html.escape(redacted_case_text(case, locale))
        cards: list[str] = []
        for item in sorted(items, key=lambda value: str(value.get("latency_profile", ""))):
            output = item.get("output")
            audio_src = ""
            if isinstance(output, str):
                audio_src = html.escape(str(Path(output).resolve().relative_to(output_dir.resolve())))
            profile = html.escape(str(item.get("latency_profile")))
            cards.append(
                "\n".join(
                    [
                        f"<article class=\"profile\" data-case-id=\"{html.escape(case_id)}\" data-profile=\"{profile}\">",
                        f"<h3>{profile}</h3>",
                        f"<audio controls src=\"{audio_src}\"></audio>",
                        "<dl>",
                        f"<dt>RTF</dt><dd>{html.escape(str(item.get('rtf')))}</dd>",
                        f"<dt>Duration</dt><dd>{html.escape(str(item.get('audio_duration_seconds')))}s</dd>",
                        f"<dt>Generation</dt><dd>{html.escape(str(item.get('generation_ms')))}ms</dd>",
                        f"<dt>Steps</dt><dd>{html.escape(str(item.get('num_step')))}</dd>",
                        "</dl>",
                        "<label>Nota <input data-score=\"score\" type=\"number\" min=\"0\" max=\"10\" step=\"0.5\" placeholder=\"0-10\"></label>",
                        "<label>Notas <textarea data-score=\"notes\" rows=\"3\" placeholder=\"pronuncia, naturalidade, termos tecnicos\"></textarea></label>",
                        "</article>",
                    ]
                )
            )
        sections.append(
            "\n".join(
                [
                    f"<section class=\"case\" data-case-id=\"{html.escape(case_id)}\">",
                    f"<h2>{html.escape(case_id)}</h2>",
                    f"<p>{source}</p>",
                    "<div class=\"profiles\">",
                    *cards,
                    "</div>",
                    "</section>",
                ]
            )
        )

    summary = payload.get("benchmark_summary", {})
    html_text = "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"pt-BR\">",
            "<head>",
            "<meta charset=\"utf-8\">",
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
            "<title>TES TTS OmniVoice Profile Review</title>",
            "<style>",
            "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:32px;line-height:1.45;color:#1f2933;background:#f7f8fa}",
            "main{max-width:1120px;margin:0 auto}.case{background:white;border:1px solid #d9dee7;border-radius:8px;padding:18px;margin:18px 0}",
            ".profiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}.profile{border:1px solid #d9dee7;border-radius:8px;padding:14px;background:#fbfcfe}",
            "audio{width:100%;margin:8px 0 12px}dl{display:grid;grid-template-columns:110px 1fr;gap:4px 10px}dt{font-weight:700}dd{margin:0}textarea,input{box-sizing:border-box;width:100%;margin-top:4px}",
            ".actions{position:sticky;top:0;background:#111827;color:white;border-radius:8px;padding:14px 16px;margin:18px 0;z-index:1}.actions button{margin:4px 8px 4px 0;padding:8px 12px;border:0;border-radius:6px;background:#e5e7eb;color:#111827;font-weight:700;cursor:pointer}",
            "</style>",
            "</head>",
            f"<body data-result-json=\"{html.escape(str(result_json))}\">",
            "<main>",
            "<h1>TES TTS OmniVoice Profile Review</h1>",
            f"<p>Profiles: {html.escape(', '.join(str(item) for item in payload.get('profiles', [])))}. Timing scope: {html.escape(str(summary.get('provider_timing_scope')))}.</p>",
            "<dl>",
            f"<dt>Cases</dt><dd>{html.escape(str(summary.get('case_count')))}</dd>",
            f"<dt>Outputs</dt><dd>{html.escape(str(summary.get('output_count')))}</dd>",
            f"<dt>Total generation</dt><dd>{html.escape(str(summary.get('total_generation_ms')))}ms</dd>",
            "</dl>",
            "<section class=\"actions\" aria-label=\"Review actions\">",
            "<strong id=\"decision\">PENDING_REVIEW</strong>",
            "<div>",
            "<button type=\"button\" id=\"saveReview\">Salvar no navegador</button>",
            "<button type=\"button\" id=\"exportReview\">Exportar JSON</button>",
            "<button type=\"button\" id=\"copyReview\">Copiar resumo</button>",
            "</div>",
            "</section>",
            *sections,
            "<script>",
            "const key='tes-tts-omnivoice-profile-review:'+document.body.dataset.resultJson;",
            "function n(v){if(v==='')return null;const x=Number(v);return Number.isFinite(x)?x:null}",
            "function collect(){const comparisons=[...document.querySelectorAll('.profile')].map(p=>{const data={};p.querySelectorAll('[data-score]').forEach(el=>{data[el.dataset.score]=el.tagName==='TEXTAREA'?el.value:n(el.value)});return {id:p.dataset.caseId,profile:p.dataset.profile,scores:data};});const scored=comparisons.filter(c=>typeof c.scores.score==='number');let decision='PENDING_REVIEW';if(scored.length===comparisons.length&&comparisons.length){const min=Math.min(...scored.map(c=>c.scores.score));decision=min>=8?'AUDIO_CANDIDATE':min>=7?'NEEDS_TARGETED_FIX':'NEEDS_FIX';}const cases=comparisons.map(c=>({id:`${c.id}/${c.profile}`,scores:c.scores}));return {schema:'tes-tts-omnivoice-profile-review@1',created_at:new Date().toISOString(),result_json:document.body.dataset.resultJson,decision,comparisons,cases};}",
            "function render(){document.getElementById('decision').textContent=collect().decision}",
            "document.addEventListener('input',render);",
            "document.getElementById('saveReview').onclick=()=>{localStorage.setItem(key,JSON.stringify(collect()));render()};",
            "document.getElementById('exportReview').onclick=()=>{const blob=new Blob([JSON.stringify(collect(),null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='tes-tts-omnivoice-profile-review.json';a.click();URL.revokeObjectURL(a.href)};",
            "document.getElementById('copyReview').onclick=async()=>{const data=collect();const text=`${data.decision}: ${data.comparisons.map(c=>`${c.id}/${c.profile}=${c.scores.score??'?'}`).join('; ')}`;if(navigator.clipboard)await navigator.clipboard.writeText(text)};",
            "try{const saved=JSON.parse(localStorage.getItem(key)||'null');if(saved&&Array.isArray(saved.comparisons)){saved.comparisons.forEach(item=>{const p=document.querySelector(`.profile[data-case-id=\"${CSS.escape(item.id)}\"][data-profile=\"${CSS.escape(item.profile)}\"]`);if(!p)return;Object.entries(item.scores||{}).forEach(([k,v])=>{const el=p.querySelector(`[data-score=\"${k}\"]`);if(el)el.value=v??''})})}}catch{}render();",
            "</script>",
            "</main>",
            "</body>",
            "</html>",
        ]
    )
    review_html.write_text(html_text, encoding="utf-8")
    return {"result_json": str(result_json), "review_html": str(review_html)}


def resolve_review_html(path: str | None, benchmark_dir: str | None) -> tuple[Path | None, str]:
    if path:
        candidate = Path(path)
        if candidate.is_dir():
            return candidate / "review.html", "arg_dir"
        return candidate, "arg_file"
    root = Path(benchmark_dir) if benchmark_dir else DEFAULT_BENCHMARK_DIR
    roots = [root] if benchmark_dir else [DEFAULT_BENCHMARK_DIR, DEFAULT_SESSION_DIR]
    candidates = [item for candidate_root in roots for item in candidate_root.glob("*/review.html") if item.is_file()]
    if not candidates:
        return None, "missing"
    candidates.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return candidates[0], "latest"


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def review_package_files(review_html: Path) -> list[Path]:
    root = review_html.parent
    files: list[Path] = []
    for candidate in (review_html, root / "result.json", root / "review-decision.json"):
        if candidate.is_file():
            files.append(candidate.resolve())
    result_json = root / "result.json"
    if result_json.is_file():
        try:
            payload = json.loads(result_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        for item in payload.get("outputs", []):
            if not isinstance(item, dict) or not isinstance(item.get("output"), str):
                continue
            candidate = Path(item["output"])
            if candidate.is_file() and is_relative_to(candidate, root):
                files.append(candidate.resolve())
    unique: dict[str, Path] = {}
    for item in files:
        unique[str(item.resolve())] = item
    return [unique[key] for key in sorted(unique)]


def review_package_manifest(review_html: Path, files: list[Path]) -> dict[str, Any]:
    root = review_html.parent
    return {
        "schema": "tes-tts-omnivoice-review-package@1",
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "provider": "omnivoice",
        "version": VERSION,
        "review_html": review_html.name,
        "files": [
            {
                "path": str(item.resolve().relative_to(root.resolve())),
                "bytes": item.stat().st_size,
                "sha256": sha256_path(item),
            }
            for item in files
        ],
        "allows_install": False,
        "allows_download": False,
        "allows_global_config_write": False,
    }


def default_review_package_path(review_html: Path, output: str | None) -> Path:
    if output:
        return Path(output)
    return review_html.parent / "tes-tts-omnivoice-review-package.zip"


def write_review_package(review_html: Path, package_path: Path) -> dict[str, Any]:
    files = review_package_files(review_html)
    manifest = review_package_manifest(review_html, files)
    package_path.parent.mkdir(parents=True, exist_ok=True)
    root = review_html.parent
    with zipfile.ZipFile(package_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in files:
            archive.write(item, arcname=str(item.resolve().relative_to(root.resolve())))
        archive.writestr("review-package-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return {
        "package_zip": str(package_path),
        "package_sha256": sha256_path(package_path),
        "package_bytes": package_path.stat().st_size,
        "file_count": len(files),
        "included_files": [item["path"] for item in manifest["files"]],
        "manifest_schema": manifest["schema"],
    }


def default_review_decision_path(review_html: Path, output: str | None) -> Path:
    if output:
        return Path(output)
    return review_html.parent / "review-decision.json"


def load_review_scores(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise ValueError("review JSON must contain a cases list")
    scores_by_id: dict[str, dict[str, Any]] = {}
    for item in cases:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            continue
        scores = item.get("scores")
        if isinstance(scores, dict):
            scores_by_id[item["id"]] = scores
    return scores_by_id


def score_value(scores: dict[str, Any], key: str) -> float | None:
    value = scores.get(key)
    if isinstance(value, (int, float)) and 0 <= float(value) <= 10:
        return float(value)
    return None


def build_profile_recommendation(cases: list[dict[str, Any]]) -> dict[str, Any] | None:
    grouped: dict[str, list[float | None]] = {}
    for case in cases:
        profile = case.get("latency_profile")
        if not isinstance(profile, str):
            continue
        scores = case.get("scores")
        if not isinstance(scores, dict):
            continue
        numeric = [float(value) for value in scores.values() if isinstance(value, (int, float))]
        grouped.setdefault(profile, []).append(min(numeric) if numeric else None)
    if not grouped:
        return None
    profile_scores: dict[str, dict[str, Any]] = {}
    for profile, values in grouped.items():
        complete_values = [value for value in values if value is not None]
        profile_scores[profile] = {
            "case_count": len(values),
            "scored_case_count": len(complete_values),
            "min_score": min(complete_values) if complete_values else None,
            "avg_score": round(sum(complete_values) / len(complete_values), 3) if complete_values else None,
            "candidate": len(complete_values) == len(values) and all(value >= 8 for value in complete_values),
        }
    for profile in PROFILE_RECOMMENDATION_ORDER:
        stats = profile_scores.get(profile)
        if stats and stats["candidate"]:
            return {
                "recommended_latency_profile": profile,
                "reason": "fastest_profile_meeting_audio_candidate_threshold",
                "profile_scores": profile_scores,
            }
    return {
        "recommended_latency_profile": None,
        "reason": "no_profile_met_audio_candidate_threshold",
        "profile_scores": profile_scores,
    }


def build_review_decision(review_html: Path, review_json: Path | None) -> dict[str, Any]:
    root = review_html.parent
    result_json = root / "result.json"
    result_payload = json.loads(result_json.read_text(encoding="utf-8")) if result_json.exists() else {}
    scores_by_id = load_review_scores(review_json)
    cases: list[dict[str, Any]] = []
    minimum_scores: list[float] = []
    result_mode = result_payload.get("mode")
    profile_review = result_mode == "product_profile_review"
    live_smoke_review = result_mode == "product_live_smoke"
    required = ("score",) if profile_review else ("overall", "pronunciation", "technical_terms", "naturalness")
    outputs = result_payload.get("outputs", [])
    output_items = outputs if isinstance(outputs, list) else []
    for item in output_items:
        if not isinstance(item, dict):
            continue
        case_id = str(item.get("id", ""))
        score_id = f"{case_id}/{item.get('latency_profile')}" if profile_review else case_id
        scores = scores_by_id.get(score_id, {})
        numeric = {key: score_value(scores, key) for key in required}
        complete = all(value is not None for value in numeric.values())
        if complete:
            minimum_scores.append(min(float(value) for value in numeric.values() if value is not None))
        cases.append(
            {
                "id": case_id,
                "score_id": score_id,
                "latency_profile": item.get("latency_profile") if profile_review else None,
                "audio": Path(str(item.get("output", ""))).name if item.get("output") else None,
                "scores": numeric,
                "notes": scores.get("notes") if isinstance(scores.get("notes"), str) else "",
                "complete": complete,
            }
        )
    if not cases or len(minimum_scores) != len(cases):
        decision = "PENDING_REVIEW"
    elif all(value >= 8 for value in minimum_scores):
        decision = "AUDIO_CANDIDATE"
    elif sum(minimum_scores) / len(minimum_scores) >= 7:
        decision = "NEEDS_TARGETED_FIX"
    else:
        decision = "NEEDS_FIX"
    profile_recommendation = build_profile_recommendation(cases) if profile_review else None
    return {
        "schema": "tes-tts-omnivoice-review-decision@1",
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "provider": "omnivoice",
        "version": VERSION,
        "review_kind": "profile_review" if profile_review else "live_smoke_review" if live_smoke_review else "benchmark_review",
        "decision": decision,
        "recommended_latency_profile": (
            profile_recommendation.get("recommended_latency_profile") if profile_recommendation else None
        ),
        "profile_recommendation": profile_recommendation,
        "review_html": str(review_html),
        "result_json": str(result_json) if result_json.exists() else None,
        "review_json": str(review_json) if review_json else None,
        "case_count": len(cases),
        "scored_case_count": len(minimum_scores),
        "cases": cases,
        "allows_install": False,
        "allows_download": False,
        "allows_global_config_write": False,
    }


def command_decide_review(args: argparse.Namespace) -> int:
    review_html, source = resolve_review_html(args.path, args.benchmark_dir)
    if review_html is None or not review_html.exists():
        emit(
            {
                "provider": "omnivoice",
                "status": "NOT_FOUND",
                "version": VERSION,
                "mode": "product_review_decision",
                "review_html": str(review_html) if review_html else None,
                "review_source": source,
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 2
    review_json = Path(args.review_json) if args.review_json else None
    decision_path = default_review_decision_path(review_html, args.output)
    decision = build_review_decision(review_html, review_json)
    decision.update(
        {
            "status": "DRY_RUN" if args.dry_run else "PASS",
            "mode": "product_review_decision",
            "review_source": source,
            "decision_json": str(decision_path),
            "package_requested": args.package,
        }
    )
    if args.dry_run:
        emit(decision)
        return 0
    decision_path.parent.mkdir(parents=True, exist_ok=True)
    decision_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.package and decision_path.resolve().parent != review_html.parent.resolve():
        shutil.copy2(decision_path, review_html.parent / "review-decision.json")
    if args.package:
        result_json = review_html.parent / "result.json"
        try:
            result_payload = json.loads(result_json.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            result_payload = {}
        if result_payload.get("mode") == "product_live_smoke":
            package_path = review_html.parent / "tes-tts-omnivoice-live-smoke-package.zip"
            decision.update(write_live_smoke_package(result_json, package_path))
        else:
            package_path = default_review_package_path(review_html, None)
            decision.update(write_review_package(review_html, package_path))
    emit(decision)
    return 0


def product_state_and_next_action(
    *,
    ready: bool,
    review_html: Path | None,
    decision: str | None,
    migration_status: str | None = None,
) -> tuple[str, str]:
    if migration_status == "NEEDS_MIGRATION":
        return (
            "NEEDS_MIGRATION",
            f"Move the project-local OmniVoice runtime from {LEGACY_PROJECT_RUNTIME_DIR} "
            f"to {GLOBAL_RUNTIME_DIR}, then rerun status.",
        )
    if not ready:
        return (
            "NEEDS_SETUP",
            "Configure the optional OmniVoice Python environment and reference voice, or use the local say fallback.",
        )
    if review_html is None or not review_html.exists():
        return (
            "NEEDS_BENCH",
            "Run: python3 scripts/tes_tts_omnivoice_provider.py bench --play --open --package",
        )
    if decision is None:
        return (
            "NEEDS_REVIEW_DECISION",
            "Score the review page, export JSON, then run decide-review --path <review.html> --review-json <exported-json> --package.",
        )
    if decision == "AUDIO_CANDIDATE":
        return (
            "AUDIO_CANDIDATE",
            "Ask for the release identity decision; do not sync, push, tag, publish, or redistribute provider assets yet.",
        )
    if decision == "NEEDS_TARGETED_FIX":
        return (
            "NEEDS_TARGETED_FIX",
            "Fix the lowest scored audible dimensions and rerun bench plus decide-review.",
        )
    if decision == "NEEDS_FIX":
        return (
            "NEEDS_FIX",
            "Repair provider/runtime speech quality before release identity planning.",
        )
    return (
        "PENDING_REVIEW",
        "Complete audible scoring, export review JSON, then seal a decision with decide-review.",
    )


def render_product_status_text(payload: dict[str, Any]) -> str:
    provider = "ready" if payload.get("provider_ready") else "needs setup"
    review = payload.get("review_html") or "not found"
    decision = payload.get("decision") or "not sealed"
    scored = payload.get("scored_case_count")
    cases = payload.get("case_count")
    score_line = f"{scored}/{cases} cases scored" if scored is not None and cases is not None else "scores unavailable"
    audio = payload.get("total_audio_duration_seconds")
    generation = payload.get("total_generation_ms")
    rtf = payload.get("avg_rtf")
    audio_line = "audio metrics unavailable"
    if audio is not None or generation is not None or rtf is not None:
        audio_line = f"audio={audio}s generation={generation}ms avg_rtf={rtf}"
    package_sha = payload.get("package_sha256") or "not packaged"
    profile = payload.get("recommended_latency_profile") or "not selected"
    active_runtime = payload.get("active_runtime")
    active_runtime_root = active_runtime.get("root") if isinstance(active_runtime, dict) else "not active"
    return "\n".join(
        [
            f"TES TTS OmniVoice product state: {payload.get('product_state')}",
            f"Provider: {provider}",
            f"Runtime: {active_runtime_root}",
            f"Migration: {payload.get('migration_status')}",
            f"Review: {review}",
            f"Decision: {decision} ({score_line})",
            f"Recommended profile: {profile}",
            f"Metrics: {audio_line}",
            f"Package SHA: {package_sha}",
            f"Next: {payload.get('next_action')}",
            "Locks: no install, no download, no global config write, no sync, no release.",
        ]
    )


def command_product_status(args: argparse.Namespace) -> int:
    provider_python, python_source = resolve_provider_python(args.python)
    ref_audio, ref_source = resolve_runtime_ref_audio(args)
    diagnostics = runtime_diagnostics(getattr(args, "voice_profile", DEFAULT_VOICE_PROFILE))
    evidence = run_python_probe(provider_python)
    provider_available = (
        evidence.get("omnivoice_importable") is True
        and evidence.get("torch_importable") is True
        and evidence.get("soundfile_importable") is True
    )
    ref_audio_ready = bool(ref_audio and ref_audio.exists())
    ready = provider_available and ref_audio_ready
    review_html, review_source = resolve_review_html(args.path, args.benchmark_dir)
    review_exists = bool(review_html and review_html.exists())
    result_json = review_html.parent / "result.json" if review_exists and review_html else None
    decision_json = review_html.parent / "review-decision.json" if review_exists and review_html else None
    package_zip: Path | None = None
    result_payload: dict[str, Any] = {}
    decision_payload: dict[str, Any] = {}
    if result_json and result_json.exists():
        result_payload = json.loads(result_json.read_text(encoding="utf-8"))
    if review_exists and review_html:
        package_name = (
            "tes-tts-omnivoice-live-smoke-package.zip"
            if result_payload.get("mode") == "product_live_smoke"
            else "tes-tts-omnivoice-review-package.zip"
        )
        package_zip = review_html.parent / package_name
    if decision_json and decision_json.exists():
        decision_payload = json.loads(decision_json.read_text(encoding="utf-8"))
    decision = decision_payload.get("decision") if isinstance(decision_payload.get("decision"), str) else None
    product_state, next_action = product_state_and_next_action(
        ready=ready,
        review_html=review_html if review_exists else None,
        decision=decision,
        migration_status=diagnostics["migration_status"],
    )
    summary = result_payload.get("benchmark_summary")
    summary = summary if isinstance(summary, dict) else {}
    payload = {
        "provider": "omnivoice",
        "status": "PASS",
        "version": VERSION,
        "mode": "product_status",
        "product_state": product_state,
        "next_action": next_action,
        "global_runtime": diagnostics["global_runtime"],
        "legacy_project_runtime": diagnostics["legacy_project_runtime"],
        "active_runtime": diagnostics["active_runtime"],
        "migration_status": diagnostics["migration_status"],
        "migration_source": diagnostics["migration_source"],
        "migration_destination": diagnostics["migration_destination"],
        "profile": diagnostics["profile"],
        "reference_wav": {
            "path": str(ref_audio) if ref_audio else None,
            "source": ref_source,
            "ready": ref_audio_ready,
            "identity": "audio-modelo-clone-mono24k.wav",
        },
        "cache_status": diagnostics["cache_status"],
        "provider_ready": ready,
        "provider_python": provider_python,
        "provider_python_source": python_source,
        "ref_audio": str(ref_audio) if ref_audio else None,
        "ref_audio_source": ref_source,
        "ref_audio_ready": ref_audio_ready,
        "review_html": str(review_html) if review_html else None,
        "review_source": review_source,
        "review_exists": review_exists,
        "result_json": str(result_json) if result_json else None,
        "result_json_exists": bool(result_json and result_json.exists()),
        "decision_json": str(decision_json) if decision_json else None,
        "decision_json_exists": bool(decision_json and decision_json.exists()),
        "decision": decision,
        "review_kind": decision_payload.get("review_kind"),
        "recommended_latency_profile": decision_payload.get("recommended_latency_profile"),
        "case_count": decision_payload.get("case_count"),
        "scored_case_count": decision_payload.get("scored_case_count"),
        "avg_rtf": summary.get("avg_rtf"),
        "total_audio_duration_seconds": summary.get("total_audio_duration_seconds"),
        "total_generation_ms": summary.get("total_generation_ms"),
        "package_zip": str(package_zip) if package_zip else None,
        "package_zip_exists": bool(package_zip and package_zip.exists()),
        "package_sha256": sha256_path(package_zip) if package_zip and package_zip.exists() else None,
        "release_identity": "deferred_until_owner_decision",
        "sync_status": "REMOTE_SYNC_NOT_REQUESTED",
        "allows_install": False,
        "allows_download": False,
        "allows_global_config_write": False,
        "allows_sync": False,
        "allows_release": False,
    }
    if args.format == "text":
        print(render_product_status_text(payload))
    else:
        emit(payload)
    if args.strict and product_state != "AUDIO_CANDIDATE":
        return 3
    return 0



def candidate_state_and_next_action(
    *,
    review_exists: bool,
    decision: str | None,
    package_exists: bool,
    audio_count: int,
) -> tuple[bool, str]:
    if not review_exists:
        return False, "Run bench --play --open --package to create a review page and audio evidence."
    if decision is None:
        return False, "Score the review page, export JSON, then seal it with decide-review --path <review.html> --review-json <json> --package."
    if decision != "AUDIO_CANDIDATE":
        return False, "Apply the targeted audio/runtime fix, then rerun bench and decide-review."
    if not package_exists:
        return False, "Run package-review --path <review.html> or decide-review --package to create the sealed ZIP."
    if audio_count <= 0:
        return False, "Rerun bench because the sealed review has no local audio files to replay."
    return True, "Replay with --play or inspect with --open; release identity still needs a separate owner decision."


def render_candidate_text(payload: dict[str, Any]) -> str:
    ready = "ready" if payload.get("candidate_ready") else "not ready"
    decision = payload.get("decision") or "not sealed"
    review = payload.get("review_html") or "not found"
    package_sha = payload.get("package_sha256") or "not packaged"
    profile = payload.get("recommended_latency_profile") or "not selected"
    return "\n".join(
        [
            f"TES TTS OmniVoice candidate: {ready}",
            f"Decision: {decision}",
            f"Recommended profile: {profile}",
            f"Review: {review}",
            f"Package SHA: {package_sha}",
            f"Audio files: {payload.get('audio_count')}",
            f"Next: {payload.get('next_action')}",
            "Locks: no install, no download, no global config write, no sync, no release.",
        ]
    )


def command_candidate(args: argparse.Namespace) -> int:
    review_html, review_source = resolve_review_html(args.path, args.benchmark_dir)
    review_exists = bool(review_html and review_html.exists())
    decision_json = review_html.parent / "review-decision.json" if review_exists and review_html else None
    package_zip = review_html.parent / "tes-tts-omnivoice-review-package.zip" if review_exists and review_html else None
    decision_payload: dict[str, Any] = {}
    if decision_json and decision_json.exists():
        decision_payload = json.loads(decision_json.read_text(encoding="utf-8"))
    decision = decision_payload.get("decision") if isinstance(decision_payload.get("decision"), str) else None
    package_files = review_package_files(review_html) if review_exists and review_html else []
    audio_files = [
        item
        for item in package_files
        if item.suffix.casefold() in {".wav", ".mp3", ".m4a", ".aiff", ".aif", ".flac", ".ogg"}
    ]
    package_exists = bool(package_zip and package_zip.exists())
    candidate_ready, next_action = candidate_state_and_next_action(
        review_exists=review_exists,
        decision=decision,
        package_exists=package_exists,
        audio_count=len(audio_files),
    )
    open_result: dict[str, Any] | None = None
    playback_results: list[dict[str, Any]] = []
    playback_failed = False
    if args.open and review_exists and review_html and not args.dry_run:
        open_result = open_local_file(review_html)
    if args.play and audio_files and not args.dry_run:
        playback_results = playback_outputs(
            [{"id": item.stem, "output": str(item)} for item in audio_files]
        )
        playback_failed = any(item.get("playback_status") == "failed" for item in playback_results)
    payload = {
        "provider": "omnivoice",
        "status": "PASS" if candidate_ready else "NEEDS_REVIEW",
        "version": VERSION,
        "mode": "product_candidate",
        "candidate_ready": candidate_ready,
        "next_action": next_action,
        "review_html": str(review_html) if review_html else None,
        "review_source": review_source,
        "review_exists": review_exists,
        "decision_json": str(decision_json) if decision_json else None,
        "decision_json_exists": bool(decision_json and decision_json.exists()),
        "decision": decision,
        "review_kind": decision_payload.get("review_kind"),
        "recommended_latency_profile": decision_payload.get("recommended_latency_profile"),
        "case_count": decision_payload.get("case_count"),
        "scored_case_count": decision_payload.get("scored_case_count"),
        "package_zip": str(package_zip) if package_zip else None,
        "package_zip_exists": package_exists,
        "package_sha256": sha256_path(package_zip) if package_zip and package_zip.exists() else None,
        "audio_count": len(audio_files),
        "audio_files": [str(item) for item in audio_files],
        "play_requested": args.play,
        "open_requested": args.open,
        "dry_run": args.dry_run,
        "open_result": open_result,
        "playback_results": playback_results,
        "allows_install": False,
        "allows_download": False,
        "allows_global_config_write": False,
        "allows_sync": False,
        "allows_release": False,
    }
    if args.format == "text":
        print(render_candidate_text(payload))
    else:
        emit(payload)
    if playback_failed:
        return 4
    if args.strict and not candidate_ready:
        return 3
    return 0 if review_exists else 2


def command_package_review(args: argparse.Namespace) -> int:
    review_html, source = resolve_review_html(args.path, args.benchmark_dir)
    if review_html is None or not review_html.exists():
        emit(
            {
                "provider": "omnivoice",
                "status": "NOT_FOUND",
                "version": VERSION,
                "mode": "product_review_package",
                "review_html": str(review_html) if review_html else None,
                "review_source": source,
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 2
    files = review_package_files(review_html)
    package_path = default_review_package_path(review_html, args.output)
    manifest = review_package_manifest(review_html, files)
    payload = {
        "provider": "omnivoice",
        "status": "DRY_RUN" if args.dry_run else "PASS",
        "version": VERSION,
        "mode": "product_review_package",
        "review_html": str(review_html),
        "review_source": source,
        "package_zip": str(package_path),
        "file_count": len(files),
        "included_files": [item["path"] for item in manifest["files"]],
        "manifest_schema": manifest["schema"],
        "allows_install": False,
        "allows_download": False,
        "allows_global_config_write": False,
    }
    if args.dry_run:
        emit(payload)
        return 0
    payload.update(write_review_package(review_html, package_path))
    emit(payload)
    return 0


def command_warm_cache(args: argparse.Namespace) -> int:
    provider_python, python_source = resolve_provider_python(args.python)
    ref_audio, ref_source = resolve_runtime_ref_audio(args)
    if not ref_audio or not ref_audio.exists():
        emit(
            {
                "provider": "omnivoice",
                "status": "NEEDS_SETUP",
                "version": VERSION,
                "mode": "product_warm_cache",
                "reason": "reference audio is required before voice prompt cache warmup",
                "ref_audio": str(ref_audio) if ref_audio else None,
                "ref_audio_source": ref_source,
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 2
    cache_path = prompt_cache_path_from_args(args, ref_audio)
    command = [
        provider_python,
        str(Path(__file__).resolve()),
        "prepare-prompt",
        *common_runtime_arg_tokens(args, ref_audio),
    ]
    if args.ref_text:
        command.extend(["--ref-text", args.ref_text])
    if args.prompt_cache:
        command.extend(["--prompt-cache", args.prompt_cache])
    if args.refresh_prompt:
        command.append("--refresh-prompt")
    if args.device:
        command.extend(["--device", args.device])
    if args.dry_run:
        apply_latency_profile(args)
        emit(
            {
                "provider": "omnivoice",
                "status": "DRY_RUN",
                "version": VERSION,
                "mode": "product_warm_cache",
                "provider_python": provider_python,
                "provider_python_source": python_source,
                "ref_audio": str(ref_audio),
                "ref_audio_source": ref_source,
                "voice_prompt_cache_path": str(cache_path),
                "voice_prompt_cache_exists": cache_path.exists(),
                "refresh_requested": args.refresh_prompt,
                "latency_profile": args.latency_profile,
                **latency_profile_metadata(args),
                **timing_attribution_metadata("dry_run_prepare_prompt"),
                "num_step": args.num_step,
                "instruct": args.instruct,
                "command_shape": redact_command_value(command, "--ref-text"),
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 0
    completed = subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        emit(
            {
                "provider": "omnivoice",
                "status": "FAIL",
                "version": VERSION,
                "mode": "product_warm_cache",
                "provider_python": provider_python,
                "stdout": completed.stdout[-1000:],
                "stderr": completed.stderr[-1000:],
                "returncode": completed.returncode,
            }
        )
        return 1
    payload["mode"] = "product_warm_cache"
    payload["provider_python"] = provider_python
    payload["provider_python_source"] = python_source
    payload["ref_audio_source"] = ref_source
    emit(payload)
    return completed.returncode


def command_session(args: argparse.Namespace) -> int:
    provider_python, python_source = resolve_provider_python(args.python)
    ref_audio, ref_source = resolve_runtime_ref_audio(args)
    output_dir = default_session_dir(args.output_dir)
    if not ref_audio or not ref_audio.exists():
        emit(
            {
                "provider": "omnivoice",
                "status": "NEEDS_SETUP",
                "version": VERSION,
                "mode": "product_session",
                "reason": "reference audio is required before resident session start",
                "ref_audio": str(ref_audio) if ref_audio else None,
                "ref_audio_source": ref_source,
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 2
    command = [
        provider_python,
        str(Path(__file__).resolve()),
        "serve",
        *common_runtime_arg_tokens(args, ref_audio),
        "--output-dir",
        str(output_dir),
    ]
    if args.ref_text:
        command.extend(["--ref-text", args.ref_text])
    if args.prompt_cache:
        command.extend(["--prompt-cache", args.prompt_cache])
    if args.refresh_prompt:
        command.append("--refresh-prompt")
    if args.device:
        command.extend(["--device", args.device])
    if args.dry_run:
        emit(
            {
                "provider": "omnivoice",
                "status": "DRY_RUN",
                "version": VERSION,
                "mode": "product_session",
                "provider_python": provider_python,
                "provider_python_source": python_source,
                "ref_audio": str(ref_audio),
                "ref_audio_source": ref_source,
                "output_dir": str(output_dir),
                "protocol": "jsonl_stdin_stdout",
                "resident_model": True,
                "resident_voice_prompt": True,
                "latency_profile": args.latency_profile,
                **latency_profile_metadata(args),
                **timing_attribution_metadata("dry_run_resident_session"),
                "num_step": args.num_step,
                "instruct": args.instruct,
                "latency_profiles": LATENCY_PROFILES,
                "command_shape": redact_command_value(command, "--ref-text"),
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 0
    output_dir.mkdir(parents=True, exist_ok=True)
    return subprocess.run(command, check=False).returncode


def command_speak_long(args: argparse.Namespace) -> int:
    apply_long_read_profile(args)
    provider_python, python_source = resolve_provider_python(args.python)
    ref_audio, ref_source = resolve_runtime_ref_audio(args)
    output_dir = default_long_read_dir(args.output_dir)
    args.first_audio_buffer_chunks = max(1, args.first_audio_buffer_chunks)
    args.first_audio_chars = max(80, args.first_audio_chars)
    args.first_audio_max_unplanned_gap_ms = max(0.0, args.first_audio_max_unplanned_gap_ms)
    session_id = output_dir.name
    log_path = default_runtime_log_path(args.monitor_log, session_id)
    result_json = output_dir / "result.json"
    stderr_log = output_dir / "resident-stderr.log"
    if args.first_audio_buffered:
        chunk_plan = build_first_audio_long_read_plan(
            args.text,
            max_chars=args.chunk_chars,
            language=args.language,
            first_audio_chars=args.first_audio_chars,
        )
    else:
        chunk_plan = build_long_read_plan(args.text, max_chars=args.chunk_chars, language=args.language)
    if not ref_audio or not ref_audio.exists():
        emit(
            {
                "provider": "omnivoice",
                "status": "NEEDS_SETUP",
                "version": VERSION,
                "mode": "product_long_read",
                "reason": "reference audio is required for OmniVoice long read",
                "ref_audio": str(ref_audio) if ref_audio else None,
                "ref_audio_source": ref_source,
                "fallback_used": False,
                "provider_exclusive": True,
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 2
    if not chunk_plan:
        emit(
            {
                "provider": "omnivoice",
                "status": "FAIL",
                "version": VERSION,
                "mode": "product_long_read",
                "reason": "text produced no speakable chunks",
                "fallback_used": False,
                "provider_exclusive": True,
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 1

    command = [
        provider_python,
        str(Path(__file__).resolve()),
        "serve",
        *common_runtime_arg_tokens(args, ref_audio),
        "--output-dir",
        str(output_dir),
    ]
    if args.ref_text:
        command.extend(["--ref-text", args.ref_text])
    if args.prompt_cache:
        command.extend(["--prompt-cache", args.prompt_cache])
    if args.refresh_prompt:
        command.append("--refresh-prompt")
    if args.device:
        command.extend(["--device", args.device])

    if args.dry_run:
        emit(
            {
                "provider": "omnivoice",
                "status": "DRY_RUN",
                "version": VERSION,
                "mode": "product_long_read",
                "provider_python": provider_python,
                "provider_python_source": python_source,
                "ref_audio": str(ref_audio),
                "ref_audio_source": ref_source,
                "text_chars": len(args.text),
                "chunk_count": len(chunk_plan),
                "chunk_chars": [chunk["chars"] for chunk in chunk_plan],
                "chunk_languages": [chunk["language"] for chunk in chunk_plan],
                "language_mode": args.language,
                "text_mode": args.text_mode,
                "max_chunk_chars": args.chunk_chars,
                "output_dir": str(output_dir),
                "result_json": str(result_json),
                "monitor_log": str(log_path),
                "monitor_heartbeat_seconds": args.monitor_heartbeat,
                "startup_timeout_seconds": args.startup_timeout,
                "utterance_timeout_seconds": args.utterance_timeout,
                "slow_chunk_ms": args.slow_chunk_ms,
                "play_requested": args.play,
                "combine_requested": args.combine,
                "inter_chunk_silence_ms": args.inter_chunk_silence_ms,
                "chunk_edge_silence_ms": args.chunk_edge_silence_ms,
                "first_audio_buffered": args.first_audio_buffered,
                "first_audio_chars": args.first_audio_chars,
                "first_audio_buffer_chunks": args.first_audio_buffer_chunks,
                "first_audio_max_unplanned_gap_ms": args.first_audio_max_unplanned_gap_ms,
                "read_profile": args.read_profile,
                "prosody_warmup": args.prosody_warmup,
                "prosody_warmup_scope": effective_prosody_warmup_scope(args),
                "latency_profile": args.latency_profile,
                **latency_profile_metadata(args),
                **timing_attribution_metadata("dry_run_resident_long_read"),
                "num_step": args.num_step,
                "instruct": args.instruct,
                "protocol": "jsonl_stdin_stdout",
                "resident_model": True,
                "resident_voice_prompt": True,
                "fallback_used": False,
                "provider_exclusive": True,
                "command_shape": redact_command_value(command, "--ref-text"),
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    monitor = RuntimeMonitor(log_path, heartbeat_seconds=args.monitor_heartbeat)
    monitor.start()
    monitor.record(
        "long_read_start",
        chunk_count=len(chunk_plan),
        text_chars=len(args.text),
        output_dir=str(output_dir),
        language_mode=args.language,
        chunk_languages=[chunk["language"] for chunk in chunk_plan],
        read_profile=args.read_profile,
        prosody_warmup=args.prosody_warmup,
        prosody_warmup_scope=effective_prosody_warmup_scope(args),
        latency_profile=args.latency_profile,
        num_step=args.num_step,
        provider_exclusive=True,
        fallback_used=False,
    )
    outputs: list[dict[str, Any]] = []
    playback_results: list[dict[str, Any]] = []
    buffered_playback: BufferedPlaybackQueue | None = None
    buffered_playback_started = False
    first_audio_summary: dict[str, Any] = {
        "enabled": args.first_audio_buffered,
        "status": "SKIPPED",
        "time_to_first_audio_ms": None,
    }
    startup_payload: dict[str, Any] | None = None
    status = "PASS"
    error: str | None = None
    total_started = time.perf_counter()
    process: subprocess.Popen[str] | None = None
    with stderr_log.open("w", encoding="utf-8") as stderr_handle:
        try:
            process = subprocess.Popen(
                command,
                text=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=stderr_handle,
            )
            startup_payload = read_jsonl_payload(process, args.startup_timeout, "resident long-read startup")
            monitor.record("startup", status=startup_payload.get("status"), startup=startup_payload)
            if startup_payload.get("status") != "READY":
                status = "FAIL"
                error = "resident session did not become ready"
            elif process.stdin is None:
                status = "FAIL"
                error = "resident session stdin is unavailable"
            else:
                if args.play and args.first_audio_buffered:
                    buffered_playback = BufferedPlaybackQueue(
                        started_at=total_started,
                        planned_gap_ms=args.inter_chunk_silence_ms,
                        monitor=monitor,
                    )
                for index, chunk in enumerate(chunk_plan, start=1):
                    chunk_id = str(chunk["id"])
                    output = output_dir / f"{index:03d}-{chunk_id}.wav"
                    request = {
                        "id": chunk_id,
                        "text": chunk["text"],
                        "language": chunk["language"],
                        "output": str(output),
                        "prosody_warmup": prosody_warmup_for_chunk(args, index),
                    }
                    monitor.record(
                        "chunk_start",
                        id=chunk_id,
                        index=index,
                        chunk_chars=chunk["chars"],
                        language=chunk["language"],
                        output=str(output),
                    )
                    process.stdin.write(json.dumps(request, ensure_ascii=False, separators=(",", ":")) + "\n")
                    process.stdin.flush()
                    response = read_jsonl_payload(process, args.utterance_timeout, f"resident long-read {chunk_id}")
                    outputs.append(response)
                    if response.get("status") == "PASS" and args.chunk_edge_silence_ms:
                        edge_silence = add_edge_silence_to_wav(output, silence_ms=args.chunk_edge_silence_ms)
                        response["edge_silence"] = edge_silence
                        monitor.record("chunk_edge_silence", id=chunk_id, **edge_silence)
                    monitor.record("chunk_result", id=chunk_id, status=response.get("status"), response=response)
                    request_ms = response.get("request_total_ms")
                    if isinstance(request_ms, (int, float)) and request_ms > args.slow_chunk_ms:
                        monitor.record(
                            "runtime_warning",
                            id=chunk_id,
                            class_="slow_chunk",
                            request_total_ms=request_ms,
                            slow_chunk_ms=args.slow_chunk_ms,
                            suggested_fix="reduce chunk size or use a faster sealed latency profile",
                        )
                    if response.get("status") != "PASS":
                        status = "FAIL"
                        error = f"{chunk_id} failed"
                        break
                    if buffered_playback is not None:
                        ready_count = len(outputs)
                        if not buffered_playback_started and ready_count >= args.first_audio_buffer_chunks:
                            for item in outputs:
                                item_id = item.get("id")
                                item_output = item.get("output")
                                if isinstance(item_id, str) and isinstance(item_output, str):
                                    buffered_playback.enqueue(item_id, Path(item_output))
                            buffered_playback.start()
                            buffered_playback_started = True
                            monitor.record(
                                "buffered_playback_armed",
                                ready_chunk_count=ready_count,
                                first_audio_buffer_chunks=args.first_audio_buffer_chunks,
                                first_audio_chars=args.first_audio_chars,
                            )
                        elif buffered_playback_started:
                            buffered_playback.enqueue(chunk_id, output)
                    if args.play and not args.combine and not args.first_audio_buffered:
                        playback = playback_audio(output)
                        playback_item = {"id": chunk_id, "output": str(output), **playback}
                        playback_results.append(playback_item)
                        monitor.record("playback_result", **playback_item)
                        if playback.get("playback_status") != "played":
                            status = "PLAYBACK_FAILED"
                            error = f"{chunk_id} playback failed"
                            break
        except Exception as exc:
            status = "FAIL"
            error = str(exc)
            monitor.record("runtime_error", error=error)
        finally:
            if buffered_playback is not None:
                buffered_playback.close()
                first_audio_summary = {
                    "enabled": True,
                    "ready_after_chunks": args.first_audio_buffer_chunks,
                    "first_audio_chars": args.first_audio_chars,
                    "max_unplanned_gap_target_ms": args.first_audio_max_unplanned_gap_ms,
                    **buffered_playback.summary(),
                }
                playback_results.extend(first_audio_summary.get("playback_results", []))
                buffered_status = first_audio_summary.get("status")
                if buffered_status != "PASS" and status == "PASS":
                    status = "TTS_NOT_AVAILABLE" if buffered_status == "PLAYBACK_NOT_AVAILABLE" else "PLAYBACK_FAILED"
                    error = f"buffered playback did not complete: {buffered_status}"
                elif (
                    first_audio_summary.get("max_unplanned_gap_ms", 0) > args.first_audio_max_unplanned_gap_ms
                    and status == "PASS"
                ):
                    status = "DEGRADED"
                    error = "buffered playback exceeded unplanned gap target"
            if process is not None:
                wait_or_terminate(process)

    generation_values = [item.get("generation_ms") for item in outputs if isinstance(item.get("generation_ms"), (int, float))]
    synthesis_values = [
        item.get("provider_synthesis_ms") for item in outputs if isinstance(item.get("provider_synthesis_ms"), (int, float))
    ]
    text_prepare_values = [
        item.get("text_prepare_ms") for item in outputs if isinstance(item.get("text_prepare_ms"), (int, float))
    ]
    audio_write_values = [
        item.get("audio_write_ms") for item in outputs if isinstance(item.get("audio_write_ms"), (int, float))
    ]
    request_values = [item.get("request_total_ms") for item in outputs if isinstance(item.get("request_total_ms"), (int, float))]
    duration_values = [
        item.get("audio_duration_seconds") for item in outputs if isinstance(item.get("audio_duration_seconds"), (int, float))
    ]
    rtf_values = [item.get("rtf") for item in outputs if isinstance(item.get("rtf"), (int, float))]
    combined_result: dict[str, Any] | None = None
    combine_wall_ms: float | None = None
    if args.combine and outputs:
        combined_result = combine_wav_files(
            [Path(item["output"]) for item in outputs if isinstance(item.get("output"), str)],
            output_dir / "combined.wav",
            silence_ms=args.inter_chunk_silence_ms,
        )
        combine_value = combined_result.get("combine_wall_ms")
        combine_wall_ms = combine_value if isinstance(combine_value, (int, float)) else None
        monitor.record("combined_audio", **combined_result)
        if combined_result.get("combined_status") != "PASS" and status == "PASS":
            status = "COMBINE_FAILED"
            error = str(combined_result.get("reason") or "combined WAV creation failed")
        elif args.play and status == "PASS" and not args.first_audio_buffered:
            playback = playback_audio(Path(str(combined_result["combined_output"])))
            playback_item = {"id": "combined", "output": combined_result["combined_output"], **playback}
            playback_results.append(playback_item)
            monitor.record("playback_result", **playback_item)
            if playback.get("playback_status") != "played":
                status = "PLAYBACK_FAILED"
                error = "combined playback failed"
    playback_values = [
        item.get("playback_wall_ms") for item in playback_results if isinstance(item.get("playback_wall_ms"), (int, float))
    ]
    total_wall_ms = round((time.perf_counter() - total_started) * 1000, 3)
    monitor.record("long_read_end", status=status, error=error)
    monitor.stop(status)
    payload = {
        "provider": "omnivoice",
        "status": status,
        "version": VERSION,
        "mode": "product_long_read",
        "provider_python": provider_python,
        "provider_python_source": python_source,
        "ref_audio": str(ref_audio),
        "ref_audio_source": ref_source,
        "output_dir": str(output_dir),
        "result_json": str(result_json),
        "monitor_log": str(log_path),
        "stderr_log": str(stderr_log),
        "text_chars": len(args.text),
        "chunk_count": len(chunk_plan),
        "completed_chunk_count": len(outputs),
        "language_mode": args.language,
        "text_mode": args.text_mode,
        "chunk_languages": [chunk["language"] for chunk in chunk_plan],
        "chunk_plan": [
            {
                "id": chunk["id"],
                "chars": chunk["chars"],
                "language": chunk["language"],
            }
            for chunk in chunk_plan
        ],
        "play_requested": args.play,
        "combine_requested": args.combine,
        "inter_chunk_silence_ms": args.inter_chunk_silence_ms,
        "chunk_edge_silence_ms": args.chunk_edge_silence_ms,
        "first_audio_buffered": args.first_audio_buffered,
        "first_audio_chars": args.first_audio_chars,
        "first_audio_buffer_chunks": args.first_audio_buffer_chunks,
        "first_audio_max_unplanned_gap_ms": args.first_audio_max_unplanned_gap_ms,
        "read_profile": args.read_profile,
        "prosody_warmup": args.prosody_warmup,
        "prosody_warmup_scope": effective_prosody_warmup_scope(args),
        "first_audio": {
            **first_audio_summary,
            "completed_before_full_synthesis": (
                isinstance(first_audio_summary.get("time_to_first_audio_ms"), (int, float))
                and bool(request_values)
                and first_audio_summary["time_to_first_audio_ms"] < sum(request_values)
            ),
        },
        "combined_audio": combined_result,
        "startup": startup_payload,
        "outputs": outputs,
        "playback_results": playback_results,
        "summary": {
            "chunk_count": len(chunk_plan),
            "pass_count": sum(1 for item in outputs if item.get("status") == "PASS"),
            "failed_count": sum(1 for item in outputs if item.get("status") != "PASS"),
            "total_audio_duration_seconds": round(sum(duration_values), 3) if duration_values else None,
            "total_generation_ms": round(sum(generation_values), 3) if generation_values else None,
            "total_provider_synthesis_ms": round(sum(synthesis_values), 3) if synthesis_values else None,
            "total_text_prepare_ms": round(sum(text_prepare_values), 3) if text_prepare_values else None,
            "total_audio_write_ms": round(sum(audio_write_values), 3) if audio_write_values else None,
            "total_request_ms": round(sum(request_values), 3) if request_values else None,
            "total_resident_request_ms": round(sum(request_values), 3) if request_values else None,
            "combine_wall_ms": combine_wall_ms,
            "total_playback_wall_ms": round(sum(playback_values), 3) if playback_values else None,
            "time_to_first_audio_ms": first_audio_summary.get("time_to_first_audio_ms"),
            "max_unplanned_gap_ms": first_audio_summary.get("max_unplanned_gap_ms"),
            "avg_rtf": round(sum(rtf_values) / len(rtf_values), 4) if rtf_values else None,
            "wall_ms": total_wall_ms,
            "total_wall_ms": total_wall_ms,
            "provider_timing_scope": "resident_long_read_local_optional_environment_only",
        },
        "latency_profile": args.latency_profile,
        **latency_profile_metadata(args),
        **timing_attribution_metadata("resident_long_read"),
        "num_step": args.num_step,
        "instruct": args.instruct,
        "resident_model": True,
        "resident_voice_prompt": True,
        "fallback_used": False,
        "provider_exclusive": True,
        "error": error,
        "allows_install": False,
        "allows_download": False,
        "allows_global_config_write": False,
    }
    result_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    emit(payload)
    if status == "PLAYBACK_FAILED":
        return 4
    return 0 if status == "PASS" else 1


def command_live_smoke(args: argparse.Namespace) -> int:
    provider_python, python_source = resolve_provider_python(args.python)
    ref_audio, ref_source = resolve_runtime_ref_audio(args)
    cases_path = Path(args.cases)
    output_dir = default_session_dir(args.output_dir)
    result_json = output_dir / "result.json"
    review_html = output_dir / "review.html"
    package_zip = output_dir / "tes-tts-omnivoice-live-smoke-package.zip"
    if not ref_audio or not ref_audio.exists():
        emit(
            {
                "provider": "omnivoice",
                "status": "NEEDS_SETUP",
                "version": VERSION,
                "mode": "product_live_smoke",
                "reason": "reference audio is required before resident live smoke",
                "ref_audio": str(ref_audio) if ref_audio else None,
                "ref_audio_source": ref_source,
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 2
    if not cases_path.exists():
        emit(
            {
                "provider": "omnivoice",
                "status": "FAIL",
                "version": VERSION,
                "mode": "product_live_smoke",
                "reason": "live smoke cases file does not exist",
                "cases": str(cases_path),
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 1

    all_cases = load_text_cases(cases_path)
    limit = max(1, args.limit)
    selected_cases = all_cases[:limit]
    command = [
        provider_python,
        str(Path(__file__).resolve()),
        "serve",
        *common_runtime_arg_tokens(args, ref_audio),
        "--output-dir",
        str(output_dir),
    ]
    if args.ref_text:
        command.extend(["--ref-text", args.ref_text])
    if args.prompt_cache:
        command.extend(["--prompt-cache", args.prompt_cache])
    if args.refresh_prompt:
        command.append("--refresh-prompt")
    if args.device:
        command.extend(["--device", args.device])

    if args.dry_run:
        emit(
            {
                "provider": "omnivoice",
                "status": "DRY_RUN",
                "version": VERSION,
                "mode": "product_live_smoke",
                "provider_python": provider_python,
                "provider_python_source": python_source,
                "ref_audio": str(ref_audio),
                "ref_audio_source": ref_source,
                "cases": str(cases_path),
                "case_count": len(selected_cases),
                "case_ids": [str(case.get("id") or f"case-{index:03d}") for index, case in enumerate(selected_cases, 1)],
                "output_dir": str(output_dir),
                "result_json": str(result_json),
                "review_html": str(review_html),
                "package_zip": str(package_zip),
                "play_requested": args.play,
                "package_requested": args.package,
                "startup_timeout_seconds": args.startup_timeout,
                "utterance_timeout_seconds": args.utterance_timeout,
                "latency_profile": args.latency_profile,
                **latency_profile_metadata(args),
                "num_step": args.num_step,
                "instruct": args.instruct,
                "protocol": "jsonl_stdin_stdout",
                "resident_model": True,
                "resident_voice_prompt": True,
                "command_shape": redact_command_value(command, "--ref-text"),
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(
        command,
        text=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    outputs: list[dict[str, Any]] = []
    startup_payload: dict[str, Any] | None = None
    status = "PASS"
    error: str | None = None
    try:
        startup_payload = read_jsonl_payload(process, args.startup_timeout, "resident session startup")
        if startup_payload.get("status") != "READY":
            status = "FAIL"
            error = "resident session did not become ready"
        elif process.stdin is None:
            status = "FAIL"
            error = "resident session stdin is unavailable"
        else:
            for index, case in enumerate(selected_cases, start=1):
                case_id = str(case.get("id") or f"case-{index:03d}")
                source_text = case.get("text") if isinstance(case.get("text"), str) else case.get("source_text")
                output = output_dir / f"{index:02d}-{safe_file_stem(case_id)}.wav"
                request = {
                    "id": case_id,
                    "text": str(source_text or ""),
                    "language": str(case.get("language") or args.language),
                    "output": str(output),
                }
                process.stdin.write(json.dumps(request, ensure_ascii=False, separators=(",", ":")) + "\n")
                process.stdin.flush()
                response = read_jsonl_payload(process, args.utterance_timeout, f"resident utterance {case_id}")
                outputs.append(response)
                if response.get("status") != "PASS":
                    status = "FAIL"
                    break
    except Exception as exc:
        status = "FAIL"
        error = str(exc)
    finally:
        wait_or_terminate(process)

    audio_outputs = [item for item in outputs if isinstance(item.get("output"), str)]
    generation_values = [item.get("generation_ms") for item in outputs if isinstance(item.get("generation_ms"), (int, float))]
    request_values = [item.get("request_total_ms") for item in outputs if isinstance(item.get("request_total_ms"), (int, float))]
    duration_values = [
        item.get("audio_duration_seconds") for item in outputs if isinstance(item.get("audio_duration_seconds"), (int, float))
    ]
    rtf_values = [item.get("rtf") for item in outputs if isinstance(item.get("rtf"), (int, float))]
    payload = {
        "provider": "omnivoice",
        "status": status,
        "version": VERSION,
        "mode": "product_live_smoke",
        "provider_python": provider_python,
        "provider_python_source": python_source,
        "ref_audio": str(ref_audio),
        "ref_audio_source": ref_source,
        "cases": str(cases_path),
        "case_count": len(selected_cases),
        "output_dir": str(output_dir),
        "result_json": str(result_json),
        "review_html": str(review_html),
        "play_requested": args.play,
        "package_requested": args.package,
        "startup": startup_payload,
        "outputs": outputs,
        "summary": {
            "request_count": len(selected_cases),
            "pass_count": sum(1 for item in outputs if item.get("status") == "PASS"),
            "failed_count": sum(1 for item in outputs if item.get("status") != "PASS"),
            "generated_audio_count": len(audio_outputs),
            "total_audio_duration_seconds": round(sum(duration_values), 3) if duration_values else None,
            "total_generation_ms": round(sum(generation_values), 3) if generation_values else None,
            "total_request_ms": round(sum(request_values), 3) if request_values else None,
            "avg_rtf": round(sum(rtf_values) / len(rtf_values), 4) if rtf_values else None,
            "provider_timing_scope": "resident_local_optional_environment_only",
        },
        "latency_profile": args.latency_profile,
        **latency_profile_metadata(args),
        **timing_attribution_metadata("resident_live_smoke"),
        "num_step": args.num_step,
        "instruct": args.instruct,
        "resident_model": True,
        "resident_voice_prompt": True,
        "error": error,
        "allows_install": False,
        "allows_download": False,
        "allows_global_config_write": False,
    }
    payload["benchmark_summary"] = {
        "case_count": payload["summary"]["request_count"],
        "avg_rtf": payload["summary"]["avg_rtf"],
        "total_audio_duration_seconds": payload["summary"]["total_audio_duration_seconds"],
        "total_generation_ms": payload["summary"]["total_generation_ms"],
        "provider_timing_scope": payload["summary"]["provider_timing_scope"],
    }
    write_benchmark_review(payload=payload, cases_path=cases_path, output_dir=output_dir, locale=args.language)
    if args.play and audio_outputs:
        playback_results = playback_outputs(audio_outputs)
        payload["playback_results"] = playback_results
        if any(item.get("playback_status") == "failed" for item in playback_results):
            payload["status"] = "PLAYBACK_FAILED"
        write_benchmark_review(payload=payload, cases_path=cases_path, output_dir=output_dir, locale=args.language)
    if args.package:
        payload.update(write_live_smoke_package(result_json, package_zip))
        result_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    emit(payload)
    if payload["status"] == "PLAYBACK_FAILED":
        return 4
    return 0 if payload["status"] == "PASS" else 1


def redact_command_value(tokens: list[str], option: str) -> list[str]:
    redacted = list(tokens)
    for index, token in enumerate(redacted[:-1]):
        if token == option:
            redacted[index + 1] = "<redacted>"
    return redacted


def same_executable_path(left: str, right: str) -> bool:
    left_path = Path(left)
    right_path = Path(right)
    try:
        return left_path.exists() and right_path.exists() and left_path.samefile(right_path)
    except OSError:
        return str(left_path.resolve()) == str(right_path.resolve())


def can_run_speak_in_process(provider_python: str) -> bool:
    return same_executable_path(provider_python, sys.executable)


def run_short_speak_in_process(
    args: argparse.Namespace,
    *,
    provider_python: str,
    python_source: str,
    ref_audio: Path,
    ref_source: str,
    output: Path,
) -> int:
    apply_latency_profile(args)
    total_started = time.perf_counter()
    kernel = direct_kernel.DirectOmniVoiceKernel.load(
        model_name=args.model,
        ref_audio=ref_audio,
        ref_text=args.ref_text,
        cache_path=prompt_cache_path_from_args(args, ref_audio),
        refresh_prompt=args.refresh_prompt,
        requested_device=args.device,
    )
    text_info, audio_metrics = kernel.synthesize_prepared(
        source_text=args.text,
        locale=args.locale,
        text_mode=args.text_mode,
        language=args.language,
        output=output,
        args=args,
    )
    payload = {
        "provider": "omnivoice",
        "status": "PASS",
        "version": VERSION,
        "mode": "product_shortcut",
        "model": args.model,
        "device": kernel.device,
        "language": args.language,
        "latency_profile": args.latency_profile,
        **latency_profile_metadata(args),
        **timing_attribution_metadata("direct_short_read"),
        "num_step": args.num_step,
        "instruct": args.instruct,
        "text_mode": text_info["mode"],
        "prosody_warmup": text_info.get("prosody_warmup", "none"),
        "prosody_warmup_tag": text_info.get("prosody_warmup_tag"),
        "provider_tag_inserted": text_info.get("provider_tag_inserted", False),
        "source_text_immutable": text_info["prepared"]["source_text_immutable"],
        "redaction_count": text_info["prepared"]["redaction_count"],
        "summary_behavior": text_info["prepared"]["summary_behavior"],
        "command_execution": text_info["prepared"]["command_execution"],
        "model_load_ms": kernel.model_load_ms,
        "provider_model_load_ms": kernel.model_load_ms,
        "provider_prepare_ms": provider_prepare_ms(kernel),
        **kernel.prompt_metrics,
        **audio_metrics,
        "total_ms": total_wall_ms,
        "total_wall_ms": total_wall_ms,
        "provider_python": provider_python,
        "provider_python_source": python_source,
        "ref_audio_source": ref_source,
        "play_requested": args.play,
        "short_read_execution": "in_process_direct_kernel",
    }
    if args.play:
        playback = playback_audio(output)
        payload.update(playback)
        if playback.get("playback_status") == "failed":
            payload["status"] = "PLAYBACK_FAILED"
            emit(payload)
            return 3
    emit(payload)
    return 0


def command_speak(args: argparse.Namespace) -> int:
    provider_python, python_source = resolve_provider_python(args.python)
    ref_audio, ref_source = resolve_runtime_ref_audio(args)
    output = default_output_path(args.output)
    if not ref_audio or not ref_audio.exists():
        emit(
            {
                "provider": "omnivoice",
                "status": "NEEDS_SETUP",
                "version": VERSION,
                "reason": "reference audio is required for OmniVoice voice cloning",
                "ref_audio": str(ref_audio) if ref_audio else None,
                "ref_audio_source": ref_source,
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 2

    command = [
        provider_python,
        str(Path(__file__).resolve()),
        "synthesize",
        "--text",
        args.text,
        *synthesize_runtime_arg_tokens(args, ref_audio, output),
    ]
    if args.ref_text:
        command.extend(["--ref-text", args.ref_text])
    if args.prompt_cache:
        command.extend(["--prompt-cache", args.prompt_cache])
    if args.refresh_prompt:
        command.append("--refresh-prompt")
    if args.device:
        command.extend(["--device", args.device])

    if args.dry_run:
        apply_latency_profile(args)
        emit(
            {
                "provider": "omnivoice",
                "status": "DRY_RUN",
                "version": VERSION,
                "mode": "product_shortcut",
                "provider_python": provider_python,
                "provider_python_source": python_source,
                "ref_audio": str(ref_audio),
                "ref_audio_source": ref_source,
                "output": str(output),
                "text_chars": len(args.text),
                "play_requested": args.play,
                "latency_profile": args.latency_profile,
                **latency_profile_metadata(args),
                **timing_attribution_metadata("dry_run_short_read"),
                "num_step": args.num_step,
                "instruct": args.instruct,
                "prosody_warmup": args.prosody_warmup,
                "command_shape": [
                    provider_python,
                    str(Path(__file__).resolve()),
                    "synthesize",
                    "--text",
                    "<redacted>",
                    *synthesize_runtime_arg_tokens(args, ref_audio, output),
                ],
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    if can_run_speak_in_process(provider_python):
        return run_short_speak_in_process(
            args,
            provider_python=provider_python,
            python_source=python_source,
            ref_audio=ref_audio,
            ref_source=ref_source,
            output=output,
        )
    completed = subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        emit(
            {
                "provider": "omnivoice",
                "status": "FAIL",
                "version": VERSION,
                "mode": "product_shortcut",
                "provider_python": provider_python,
                "stdout": completed.stdout[-1000:],
                "stderr": completed.stderr[-1000:],
                "returncode": completed.returncode,
            }
        )
        return 1
    payload["mode"] = "product_shortcut"
    payload["provider_python"] = provider_python
    payload["provider_python_source"] = python_source
    payload["ref_audio_source"] = ref_source
    payload["play_requested"] = args.play
    if args.play and completed.returncode == 0:
        playback = playback_audio(output)
        payload.update(playback)
        if playback.get("playback_status") == "failed":
            payload["status"] = "PLAYBACK_FAILED"
            emit(payload)
            return 3
    emit(payload)
    return completed.returncode


def command_bench(args: argparse.Namespace) -> int:
    provider_python, python_source = resolve_provider_python(args.python)
    ref_audio, ref_source = resolve_runtime_ref_audio(args)
    cases = Path(args.cases)
    output_dir = default_benchmark_dir(args.output_dir)
    if not ref_audio or not ref_audio.exists():
        emit(
            {
                "provider": "omnivoice",
                "status": "NEEDS_SETUP",
                "version": VERSION,
                "mode": "product_benchmark",
                "reason": "reference audio is required for OmniVoice voice cloning",
                "ref_audio": str(ref_audio) if ref_audio else None,
                "ref_audio_source": ref_source,
                "cases": str(cases),
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 2
    if not cases.exists():
        emit(
            {
                "provider": "omnivoice",
                "status": "FAIL",
                "version": VERSION,
                "mode": "product_benchmark",
                "reason": "benchmark cases file does not exist",
                "cases": str(cases),
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 1

    command = [
        provider_python,
        str(Path(__file__).resolve()),
        "batch",
        "--cases",
        str(cases),
        "--output-dir",
        str(output_dir),
        *common_runtime_arg_tokens(args, ref_audio),
    ]
    if args.ref_text:
        command.extend(["--ref-text", args.ref_text])
    if args.prompt_cache:
        command.extend(["--prompt-cache", args.prompt_cache])
    if args.refresh_prompt:
        command.append("--refresh-prompt")
    if args.device:
        command.extend(["--device", args.device])

    if args.dry_run:
        apply_latency_profile(args)
        emit(
            {
                "provider": "omnivoice",
                "status": "DRY_RUN",
                "version": VERSION,
                "mode": "product_benchmark",
                "provider_python": provider_python,
                "provider_python_source": python_source,
                "ref_audio": str(ref_audio),
                "ref_audio_source": ref_source,
                "cases": str(cases),
                "output_dir": str(output_dir),
                "play_requested": args.play,
                "open_requested": args.open,
                "package_requested": args.package,
                "latency_profile": args.latency_profile,
                **latency_profile_metadata(args),
                "num_step": args.num_step,
        "instruct": args.instruct,
                "result_json": str(output_dir / "result.json"),
                "review_html": str(output_dir / "review.html"),
                "package_zip": str(output_dir / "tes-tts-omnivoice-review-package.zip"),
                "command_shape": redact_command_value(command, "--ref-text"),
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        emit(
            {
                "provider": "omnivoice",
                "status": "FAIL",
                "version": VERSION,
                "mode": "product_benchmark",
                "provider_python": provider_python,
                "stdout": completed.stdout[-1000:],
                "stderr": completed.stderr[-1000:],
                "returncode": completed.returncode,
            }
        )
        return 1
    payload["mode"] = "product_benchmark"
    payload["provider_python"] = provider_python
    payload["provider_python_source"] = python_source
    payload["ref_audio_source"] = ref_source
    payload["cases"] = str(cases)
    payload["output_dir"] = str(output_dir)
    payload["play_requested"] = args.play
    payload["open_requested"] = args.open
    payload["package_requested"] = args.package
    outputs = payload.get("outputs")
    if isinstance(outputs, list) and outputs:
        rtfs = [item.get("rtf") for item in outputs if isinstance(item.get("rtf"), (int, float))]
        durations = [
            item.get("audio_duration_seconds")
            for item in outputs
            if isinstance(item.get("audio_duration_seconds"), (int, float))
        ]
        generations = [
            item.get("generation_ms")
            for item in outputs
            if isinstance(item.get("generation_ms"), (int, float))
        ]
        syntheses = [
            item.get("provider_synthesis_ms")
            for item in outputs
            if isinstance(item.get("provider_synthesis_ms"), (int, float))
        ]
        text_prepares = [
            item.get("text_prepare_ms")
            for item in outputs
            if isinstance(item.get("text_prepare_ms"), (int, float))
        ]
        audio_writes = [
            item.get("audio_write_ms")
            for item in outputs
            if isinstance(item.get("audio_write_ms"), (int, float))
        ]
        payload["benchmark_summary"] = {
            "case_count": len(outputs),
            "avg_rtf": round(sum(rtfs) / len(rtfs), 4) if rtfs else None,
            "total_audio_duration_seconds": round(sum(durations), 3) if durations else None,
            "total_generation_ms": round(sum(generations), 3) if generations else None,
            "total_provider_synthesis_ms": round(sum(syntheses), 3) if syntheses else None,
            "total_text_prepare_ms": round(sum(text_prepares), 3) if text_prepares else None,
            "total_audio_write_ms": round(sum(audio_writes), 3) if audio_writes else None,
            "provider_prepare_ms": payload.get("provider_prepare_ms"),
            "total_wall_ms": payload.get("total_wall_ms"),
            "provider_timing_scope": "local_optional_environment_only",
        }
        if args.play and completed.returncode == 0:
            playback_results = playback_outputs(outputs)
            payload["playback_results"] = playback_results
            if any(result.get("playback_status") == "failed" for result in playback_results):
                payload["status"] = "PLAYBACK_FAILED"
                write_benchmark_review(payload=payload, cases_path=cases, output_dir=output_dir, locale=args.locale)
                emit(payload)
                return 3
        review_paths = write_benchmark_review(payload=payload, cases_path=cases, output_dir=output_dir, locale=args.locale)
        if args.open and completed.returncode == 0:
            open_result = open_local_file(Path(review_paths["review_html"]))
            payload.update(open_result)
            if open_result.get("open_status") == "failed":
                payload["status"] = "OPEN_FAILED"
                Path(review_paths["result_json"]).write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                emit(payload)
                return 4
            Path(review_paths["result_json"]).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        if args.package and completed.returncode == 0:
            package_result = write_review_package(
                Path(review_paths["review_html"]),
                output_dir / "tes-tts-omnivoice-review-package.zip",
            )
            payload.update(package_result)
            Path(review_paths["result_json"]).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
    emit(payload)
    return completed.returncode


def command_profile_review(args: argparse.Namespace) -> int:
    provider_python, python_source = resolve_provider_python(args.python)
    ref_audio, ref_source = resolve_runtime_ref_audio(args)
    cases = Path(args.cases)
    output_dir = default_benchmark_dir(args.output_dir)
    profiles = [args.profile_a, args.profile_b]
    if args.profile_a == args.profile_b:
        emit(
            {
                "provider": "omnivoice",
                "status": "FAIL",
                "version": VERSION,
                "mode": "product_profile_review",
                "reason": "profile_a and profile_b must be different",
                "profiles": profiles,
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 1
    if not ref_audio or not ref_audio.exists():
        emit(
            {
                "provider": "omnivoice",
                "status": "NEEDS_SETUP",
                "version": VERSION,
                "mode": "product_profile_review",
                "reason": "reference audio is required for OmniVoice voice cloning",
                "ref_audio": str(ref_audio) if ref_audio else None,
                "ref_audio_source": ref_source,
                "cases": str(cases),
                "profiles": profiles,
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 2
    if not cases.exists():
        emit(
            {
                "provider": "omnivoice",
                "status": "FAIL",
                "version": VERSION,
                "mode": "product_profile_review",
                "reason": "benchmark cases file does not exist",
                "cases": str(cases),
                "profiles": profiles,
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 1

    commands: list[list[str]] = []
    for profile in profiles:
        profile_args = argparse.Namespace(**vars(args))
        profile_args.latency_profile = profile
        profile_args.num_step = None
        profile_output_dir = output_dir / profile
        command = [
            provider_python,
            str(Path(__file__).resolve()),
            "batch",
            "--cases",
            str(cases),
            "--output-dir",
            str(profile_output_dir),
            *common_runtime_arg_tokens(profile_args, ref_audio),
        ]
        if args.ref_text:
            command.extend(["--ref-text", args.ref_text])
        if args.prompt_cache:
            command.extend(["--prompt-cache", args.prompt_cache])
        if args.refresh_prompt:
            command.append("--refresh-prompt")
        if args.device:
            command.extend(["--device", args.device])
        commands.append(command)

    if args.dry_run:
        emit(
            {
                "provider": "omnivoice",
                "status": "DRY_RUN",
                "version": VERSION,
                "mode": "product_profile_review",
                "provider_python": provider_python,
                "provider_python_source": python_source,
                "ref_audio": str(ref_audio),
                "ref_audio_source": ref_source,
                "cases": str(cases),
                "output_dir": str(output_dir),
                "profiles": profiles,
                "play_requested": args.play,
                "open_requested": args.open,
                "package_requested": args.package,
                "result_json": str(output_dir / "result.json"),
                "review_html": str(output_dir / "review.html"),
                "package_zip": str(output_dir / "tes-tts-omnivoice-review-package.zip"),
                "command_shapes": [redact_command_value(command, "--ref-text") for command in commands],
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    payloads: list[dict[str, Any]] = []
    for profile, command in zip(profiles, commands, strict=True):
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            profile_payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            emit(
                {
                    "provider": "omnivoice",
                    "status": "FAIL",
                    "version": VERSION,
                    "mode": "product_profile_review",
                    "provider_python": provider_python,
                    "latency_profile": profile,
                    "stdout": completed.stdout[-1000:],
                    "stderr": completed.stderr[-1000:],
                    "returncode": completed.returncode,
                }
            )
            return 1
        profile_payload["latency_profile"] = profile
        profile_payload["returncode"] = completed.returncode
        payloads.append(profile_payload)
        if completed.returncode != 0:
            emit(profile_payload)
            return completed.returncode

    outputs: list[dict[str, Any]] = []
    for profile_payload in payloads:
        profile = profile_payload.get("latency_profile")
        for item in profile_payload.get("outputs", []):
            if isinstance(item, dict):
                item["latency_profile"] = profile
                outputs.append(item)

    rtfs = [item.get("rtf") for item in outputs if isinstance(item.get("rtf"), (int, float))]
    durations = [
        item.get("audio_duration_seconds")
        for item in outputs
        if isinstance(item.get("audio_duration_seconds"), (int, float))
    ]
    generations = [item.get("generation_ms") for item in outputs if isinstance(item.get("generation_ms"), (int, float))]
    syntheses = [
        item.get("provider_synthesis_ms") for item in outputs if isinstance(item.get("provider_synthesis_ms"), (int, float))
    ]
    text_prepares = [item.get("text_prepare_ms") for item in outputs if isinstance(item.get("text_prepare_ms"), (int, float))]
    audio_writes = [item.get("audio_write_ms") for item in outputs if isinstance(item.get("audio_write_ms"), (int, float))]
    provider_prepare_values = [
        item.get("provider_prepare_ms")
        for item in payloads
        if isinstance(item.get("provider_prepare_ms"), (int, float))
    ]
    total_wall_values = [
        item.get("total_wall_ms")
        for item in payloads
        if isinstance(item.get("total_wall_ms"), (int, float))
    ]
    payload = {
        "provider": "omnivoice",
        "status": "PASS",
        "version": VERSION,
        "mode": "product_profile_review",
        "provider_python": provider_python,
        "provider_python_source": python_source,
        "ref_audio": str(ref_audio),
        "ref_audio_source": ref_source,
        "cases": str(cases),
        "output_dir": str(output_dir),
        "profiles": profiles,
        "outputs": outputs,
        "profile_payloads": payloads,
        "play_requested": args.play,
        "open_requested": args.open,
        "package_requested": args.package,
        "benchmark_summary": {
            "case_count": len(load_text_cases(cases)),
            "output_count": len(outputs),
            "avg_rtf": round(sum(rtfs) / len(rtfs), 4) if rtfs else None,
            "total_audio_duration_seconds": round(sum(durations), 3) if durations else None,
            "total_generation_ms": round(sum(generations), 3) if generations else None,
            "total_provider_synthesis_ms": round(sum(syntheses), 3) if syntheses else None,
            "total_text_prepare_ms": round(sum(text_prepares), 3) if text_prepares else None,
            "total_audio_write_ms": round(sum(audio_writes), 3) if audio_writes else None,
            "total_provider_prepare_ms": round(sum(provider_prepare_values), 3) if provider_prepare_values else None,
            "total_wall_ms": round(sum(total_wall_values), 3) if total_wall_values else None,
            "provider_timing_scope": "local_optional_environment_only",
        },
        "allows_install": False,
        "allows_download": False,
        "allows_global_config_write": False,
    }
    if args.play and outputs:
        playback_results = playback_outputs(outputs)
        payload["playback_results"] = playback_results
        if any(result.get("playback_status") == "failed" for result in playback_results):
            payload["status"] = "PLAYBACK_FAILED"
            write_profile_review(payload=payload, cases_path=cases, output_dir=output_dir, locale=args.locale)
            emit(payload)
            return 3
    review_paths = write_profile_review(payload=payload, cases_path=cases, output_dir=output_dir, locale=args.locale)
    if args.open:
        open_result = open_local_file(Path(review_paths["review_html"]))
        payload.update(open_result)
        if open_result.get("open_status") == "failed":
            payload["status"] = "OPEN_FAILED"
            Path(review_paths["result_json"]).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            emit(payload)
            return 4
        Path(review_paths["result_json"]).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.package:
        package_result = write_review_package(
            Path(review_paths["review_html"]),
            output_dir / "tes-tts-omnivoice-review-package.zip",
        )
        payload.update(package_result)
        Path(review_paths["result_json"]).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    emit(payload)
    return 0


def command_review(args: argparse.Namespace) -> int:
    review_html, source = resolve_review_html(args.path, args.benchmark_dir)
    if review_html is None:
        emit(
            {
                "provider": "omnivoice",
                "status": "NOT_FOUND",
                "version": VERSION,
                "mode": "product_review",
                "review_html": None,
                "review_source": source,
                "allows_install": False,
                "allows_download": False,
                "allows_global_config_write": False,
            }
        )
        return 2
    payload = {
        "provider": "omnivoice",
        "status": "DRY_RUN" if args.dry_run else "PASS",
        "version": VERSION,
        "mode": "product_review",
        "review_html": str(review_html),
        "review_source": source,
        "open_requested": not args.dry_run,
        "exists": review_html.exists(),
        "allows_install": False,
        "allows_download": False,
        "allows_global_config_write": False,
    }
    if not review_html.exists():
        payload["status"] = "NOT_FOUND"
        emit(payload)
        return 2
    if args.dry_run:
        emit(payload)
        return 0
    open_result = open_local_file(review_html)
    payload.update(open_result)
    if open_result.get("open_status") == "failed":
        payload["status"] = "OPEN_FAILED"
        emit(payload)
        return 4
    emit(payload)
    return 0


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
    return direct_kernel.provider_text(source_text, locale, mode)


def load_omnivoice_modules() -> dict[str, Any]:
    return direct_kernel.load_omnivoice_modules()


def best_device(torch: Any, requested: str | None) -> str:
    return direct_kernel.best_device(torch, requested)


def prompt_cache_path(cache_dir: Path, model: str, ref_audio: Path, ref_text: str | None) -> Path:
    return direct_kernel.prompt_cache_path(cache_dir, model, ref_audio, ref_text)


def protect_voice_prompt_cache_path(cache_path: Path) -> None:
    direct_kernel.protect_voice_prompt_cache_path(cache_path)


def load_or_create_voice_prompt(
    *,
    model: Any,
    torch: Any,
    ref_audio: Path,
    ref_text: str | None,
    cache_path: Path,
    refresh: bool,
) -> tuple[Any, dict[str, Any]]:
    return direct_kernel.load_or_create_voice_prompt(
        model=model,
        torch=torch,
        ref_audio=ref_audio,
        ref_text=ref_text,
        cache_path=cache_path,
        refresh=refresh,
    )


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
    kernel = direct_kernel.DirectOmniVoiceKernel(
        model=model,
        soundfile=sf,
        voice_prompt=voice_prompt,
        device=str(getattr(model, "device", "unknown")),
        model_load_ms=0,
        prompt_metrics={},
    )
    return kernel.synthesize(
        text=text,
        language=language,
        instruct=getattr(args, "instruct", None),
        output=output,
        num_step=args.num_step,
        guidance_scale=args.guidance_scale,
        speed=args.speed,
        t_shift=args.t_shift,
        denoise=args.denoise,
        postprocess_output=args.postprocess_output,
    )


def command_prepare_prompt(args: argparse.Namespace) -> int:
    apply_latency_profile(args)
    total_started = time.perf_counter()
    ref_audio = Path(args.ref_audio)
    cache_path = prompt_cache_path_from_args(args, ref_audio)
    kernel = direct_kernel.DirectOmniVoiceKernel.load(
        model_name=args.model,
        ref_audio=ref_audio,
        ref_text=args.ref_text,
        cache_path=cache_path,
        refresh_prompt=args.refresh_prompt,
        requested_device=args.device,
    )
    total_wall_ms = round((time.perf_counter() - total_started) * 1000, 3)
    emit(
        {
            "provider": "omnivoice",
            "status": "PASS",
            "version": VERSION,
            "mode": "voice_prompt_cache",
            "model": args.model,
            "device": kernel.device,
            "language": args.language,
            "latency_profile": args.latency_profile,
            **latency_profile_metadata(args),
            **timing_attribution_metadata("prepare_prompt"),
            "num_step": args.num_step,
            "instruct": args.instruct,
            "model_load_ms": kernel.model_load_ms,
            "provider_model_load_ms": kernel.model_load_ms,
            "provider_prepare_ms": provider_prepare_ms(kernel),
            **kernel.prompt_metrics,
            "total_ms": total_wall_ms,
            "total_wall_ms": total_wall_ms,
            "allows_install": False,
            "allows_download": False,
            "allows_global_config_write": False,
        }
    )
    return 0


def command_synthesize(args: argparse.Namespace) -> int:
    apply_latency_profile(args)
    total_started = time.perf_counter()
    ref_audio = Path(args.ref_audio)
    kernel = direct_kernel.DirectOmniVoiceKernel.load(
        model_name=args.model,
        ref_audio=ref_audio,
        ref_text=args.ref_text,
        cache_path=prompt_cache_path_from_args(args, ref_audio),
        refresh_prompt=args.refresh_prompt,
        requested_device=args.device,
    )
    text_info, audio_metrics = kernel.synthesize_prepared(
        source_text=args.text,
        locale=args.locale,
        text_mode=args.text_mode,
        language=args.language,
        output=Path(args.output),
        args=args,
    )
    total_wall_ms = round((time.perf_counter() - total_started) * 1000, 3)
    emit(
        {
            "provider": "omnivoice",
            "status": "PASS",
            "version": VERSION,
            "model": args.model,
            "device": kernel.device,
            "language": args.language,
            "latency_profile": args.latency_profile,
            **latency_profile_metadata(args),
            **timing_attribution_metadata("synthesize"),
            "num_step": args.num_step,
            "instruct": args.instruct,
            "text_mode": text_info["mode"],
            "prosody_warmup": text_info.get("prosody_warmup", "none"),
            "prosody_warmup_tag": text_info.get("prosody_warmup_tag"),
            "provider_tag_inserted": text_info.get("provider_tag_inserted", False),
            "source_text_immutable": text_info["prepared"]["source_text_immutable"],
            "redaction_count": text_info["prepared"]["redaction_count"],
            "summary_behavior": text_info["prepared"]["summary_behavior"],
            "command_execution": text_info["prepared"]["command_execution"],
            "model_load_ms": kernel.model_load_ms,
            "provider_model_load_ms": kernel.model_load_ms,
            "provider_prepare_ms": provider_prepare_ms(kernel),
            **kernel.prompt_metrics,
            **audio_metrics,
            "total_ms": total_wall_ms,
            "total_wall_ms": total_wall_ms,
        }
    )
    return 0


def load_text_cases(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return data["cases"]


def command_batch(args: argparse.Namespace) -> int:
    apply_latency_profile(args)
    cases = load_text_cases(Path(args.cases))

    total_started = time.perf_counter()
    ref_audio = Path(args.ref_audio)
    kernel = direct_kernel.DirectOmniVoiceKernel.load(
        model_name=args.model,
        ref_audio=ref_audio,
        ref_text=args.ref_text,
        cache_path=prompt_cache_path_from_args(args, ref_audio),
        refresh_prompt=args.refresh_prompt,
        requested_device=args.device,
    )

    outputs: list[dict[str, Any]] = []
    out_dir = Path(args.output_dir)
    for index, case in enumerate(cases, start=1):
        case_id = case.get("id") or f"case-{index:03d}"
        source_text = case["text"]
        output = out_dir / f"{index:02d}-{case_id}.wav"
        text_info, metrics = kernel.synthesize_prepared(
            source_text=source_text,
            locale=args.locale,
            text_mode=args.text_mode,
            language=case.get("language", args.language),
            output=output,
            args=args,
        )
        outputs.append(
            {
                "id": case_id,
                "text_mode": text_info["mode"],
                "prosody_warmup": text_info.get("prosody_warmup", "none"),
                "prosody_warmup_tag": text_info.get("prosody_warmup_tag"),
                "provider_tag_inserted": text_info.get("provider_tag_inserted", False),
                "redaction_count": text_info["prepared"]["redaction_count"],
                **metrics,
            }
        )

    total_wall_ms = round((time.perf_counter() - total_started) * 1000, 3)
    emit(
        {
            "provider": "omnivoice",
            "status": "PASS",
            "version": VERSION,
            "model": args.model,
            "device": kernel.device,
            "language": args.language,
            "latency_profile": args.latency_profile,
            **latency_profile_metadata(args),
            **timing_attribution_metadata("batch"),
            "num_step": args.num_step,
            "instruct": args.instruct,
            "model_load_ms": kernel.model_load_ms,
            "provider_model_load_ms": kernel.model_load_ms,
            "provider_prepare_ms": provider_prepare_ms(kernel),
            **kernel.prompt_metrics,
            "outputs": outputs,
            "total_ms": total_wall_ms,
            "total_wall_ms": total_wall_ms,
        }
    )
    return 0


def command_serve(args: argparse.Namespace) -> int:
    apply_latency_profile(args)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    total_started = time.perf_counter()
    ref_audio = Path(args.ref_audio)
    kernel = direct_kernel.DirectOmniVoiceKernel.load(
        model_name=args.model,
        ref_audio=ref_audio,
        ref_text=args.ref_text,
        cache_path=prompt_cache_path_from_args(args, ref_audio),
        refresh_prompt=args.refresh_prompt,
        requested_device=args.device,
    )
    startup_wall_ms = round((time.perf_counter() - total_started) * 1000, 3)
    emit_jsonl(
        {
            "provider": "omnivoice",
            "status": "READY",
            "version": VERSION,
            "mode": "resident_session",
            "protocol": "jsonl_stdin_stdout",
            "model": args.model,
            "device": kernel.device,
            "language": args.language,
            "latency_profile": args.latency_profile,
            **latency_profile_metadata(args),
            **timing_attribution_metadata("serve_startup"),
            "num_step": args.num_step,
            "instruct": args.instruct,
            "output_dir": str(out_dir),
            "model_load_ms": kernel.model_load_ms,
            "provider_model_load_ms": kernel.model_load_ms,
            "provider_prepare_ms": provider_prepare_ms(kernel),
            **kernel.prompt_metrics,
            "startup_ms": startup_wall_ms,
            "provider_startup_ms": startup_wall_ms,
            "total_wall_ms": startup_wall_ms,
            "allows_install": False,
            "allows_download": False,
            "allows_global_config_write": False,
        }
    )
    sys.stdout.flush()

    served = 0
    for line in sys.stdin:
        if not line.strip():
            continue
        served += 1
        request_started = time.perf_counter()
        try:
            request = json.loads(line)
            text = request.get("text")
            if not isinstance(text, str) or not text:
                raise ValueError("request.text must be a non-empty string")
            request_id = str(request.get("id") or f"utterance-{served:04d}")
            language = str(request.get("language") or args.language)
            output_value = request.get("output")
            output = (
                Path(output_value)
                if isinstance(output_value, str) and output_value
                else out_dir / f"{served:04d}-{safe_file_stem(request_id)}.wav"
            )
            text_info, audio_metrics = kernel.synthesize_prepared(
                source_text=text,
                locale=args.locale,
                text_mode=args.text_mode,
                language=language,
                output=output,
                args=argparse.Namespace(
                    **{
                        **vars(args),
                        "prosody_warmup": str(request.get("prosody_warmup") or args.prosody_warmup),
                    }
                ),
            )
            request_wall_ms = round((time.perf_counter() - request_started) * 1000, 3)
            emit_jsonl(
                {
                    "provider": "omnivoice",
                    "status": "PASS",
                    "version": VERSION,
                    "mode": "resident_session_utterance",
                    "id": request_id,
                    "language": language,
                    "latency_profile": args.latency_profile,
                    **latency_profile_metadata(args),
                    **timing_attribution_metadata("resident_utterance"),
                    "num_step": args.num_step,
                    "instruct": args.instruct,
                    "text_mode": text_info["mode"],
                    "prosody_warmup": text_info.get("prosody_warmup", "none"),
                    "prosody_warmup_tag": text_info.get("prosody_warmup_tag"),
                    "provider_tag_inserted": text_info.get("provider_tag_inserted", False),
                    "source_text_immutable": text_info["prepared"]["source_text_immutable"],
                    "redaction_count": text_info["prepared"]["redaction_count"],
                    "summary_behavior": text_info["prepared"]["summary_behavior"],
                    "command_execution": text_info["prepared"]["command_execution"],
                    "model_reused": True,
                    "voice_prompt_reused": True,
                    **audio_metrics,
                    "request_total_ms": request_wall_ms,
                    "request_wall_ms": request_wall_ms,
                }
            )
        except Exception as exc:
            request_wall_ms = round((time.perf_counter() - request_started) * 1000, 3)
            emit_jsonl(
                {
                    "provider": "omnivoice",
                    "status": "FAIL",
                    "version": VERSION,
                    "mode": "resident_session_utterance",
                    "error": str(exc),
                    "request_total_ms": request_wall_ms,
                    "request_wall_ms": request_wall_ms,
                }
            )
        sys.stdout.flush()
    return 0


def add_runtime_args(parser: argparse.ArgumentParser, *, ref_audio_required: bool = True) -> None:
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--language", default=DEFAULT_LANGUAGE)
    parser.add_argument("--locale", default="pt-BR")
    parser.add_argument("--voice-profile", default=DEFAULT_VOICE_PROFILE)
    parser.add_argument("--ref-audio", required=ref_audio_required)
    parser.add_argument("--ref-text")
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    parser.add_argument("--prompt-cache")
    parser.add_argument("--refresh-prompt", action="store_true")
    parser.add_argument("--device")
    parser.add_argument(
        "--latency-profile",
        choices=LATENCY_PROFILE_CHOICES,
        default="auto",
        help="Use a concrete profile or auto-select the latest sealed AUDIO_CANDIDATE recommendation.",
    )
    parser.add_argument(
        "--text-mode",
        choices=["redacted_source", "spoken_text", "audio_quality", "raw"],
        default="redacted_source",
    )
    parser.add_argument(
        "--prosody-warmup",
        choices=PROSODY_WARMUP_CHOICES,
        default="none",
        help="Optional OmniVoice provider-only prosody warmup tag for explicit conversational experiments.",
    )
    parser.add_argument(
        "--instruct",
        help="Optional OmniVoice voice-design instruction; code-defined profiles use this for silent prosody.",
    )
    parser.add_argument("--num-step", type=int)
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

    status = subparsers.add_parser("status")
    status.add_argument("--python")
    status.add_argument("--ref-audio")
    status.add_argument("--voice-profile", default=DEFAULT_VOICE_PROFILE)
    status.set_defaults(func=command_status)

    warm_cache = subparsers.add_parser("warm-cache")
    add_runtime_args(warm_cache, ref_audio_required=False)
    warm_cache.add_argument("--python")
    warm_cache.add_argument("--dry-run", action="store_true")
    warm_cache.set_defaults(func=command_warm_cache)

    normalize = subparsers.add_parser("normalize-ref")
    normalize.add_argument("--input", required=True)
    normalize.add_argument("--output", required=True)
    normalize.set_defaults(func=lambda args: normalize_ref_audio(Path(args.input), Path(args.output)) or 0)

    prepare_prompt = subparsers.add_parser("prepare-prompt")
    add_runtime_args(prepare_prompt, ref_audio_required=False)
    prepare_prompt.set_defaults(func=command_prepare_prompt)

    serve = subparsers.add_parser("serve")
    add_runtime_args(serve, ref_audio_required=False)
    serve.add_argument("--output-dir", required=True)
    serve.set_defaults(func=command_serve)

    synthesize = subparsers.add_parser("synthesize")
    add_runtime_args(synthesize, ref_audio_required=False)
    synthesize.add_argument("--text", required=True)
    synthesize.add_argument("--output", required=True)
    synthesize.set_defaults(func=command_synthesize)

    batch = subparsers.add_parser("batch")
    add_runtime_args(batch, ref_audio_required=False)
    batch.add_argument("--cases", required=True)
    batch.add_argument("--output-dir", required=True)
    batch.set_defaults(func=command_batch)

    speak = subparsers.add_parser("speak")
    add_runtime_args(speak, ref_audio_required=False)
    speak.add_argument("--python")
    speak.add_argument("--text", required=True)
    speak.add_argument("--output")
    speak.add_argument("--play", action="store_true")
    speak.add_argument("--dry-run", action="store_true")
    speak.set_defaults(func=command_speak)

    speak_long = subparsers.add_parser("speak-long")
    add_runtime_args(speak_long, ref_audio_required=False)
    speak_long.add_argument("--python")
    speak_long.add_argument("--text", required=True)
    speak_long.add_argument("--output-dir")
    speak_long.add_argument("--monitor-log")
    speak_long.add_argument(
        "--read-profile",
        choices=LONG_READ_PROFILE_CHOICES,
        default=DEFAULT_LONG_READ_PROFILE,
        help="Apply a fixed TES-TTS long-read recipe; use manual to preserve hand-assembled flags.",
    )
    speak_long.add_argument("--chunk-chars", type=int, default=420)
    speak_long.add_argument("--startup-timeout", type=float, default=300.0)
    speak_long.add_argument("--utterance-timeout", type=float, default=180.0)
    speak_long.add_argument("--monitor-heartbeat", type=float, default=5.0)
    speak_long.add_argument("--slow-chunk-ms", type=float, default=45000.0)
    speak_long.add_argument(
        "--combine",
        action="store_true",
        help="Write combined.wav from chunk WAVs for review/playback while keeping individual chunks.",
    )
    speak_long.add_argument("--inter-chunk-silence-ms", type=int, default=350)
    speak_long.add_argument("--chunk-edge-silence-ms", type=int, default=0)
    speak_long.add_argument(
        "--first-audio-buffered",
        action="store_true",
        help="Start long-read playback after a small buffered head instead of waiting for combined.wav.",
    )
    speak_long.add_argument("--first-audio-chars", type=int, default=160)
    speak_long.add_argument("--first-audio-buffer-chunks", type=int, default=2)
    speak_long.add_argument("--first-audio-max-unplanned-gap-ms", type=float, default=1200.0)
    speak_long.add_argument(
        "--prosody-warmup-scope",
        choices=LONG_READ_PROSODY_WARMUP_SCOPES,
        default="first_chunk_only",
        help="Apply conversational warmup to the first chunk only or to every independent synthesis chunk.",
    )
    speak_long.add_argument("--play", action="store_true")
    speak_long.add_argument("--dry-run", action="store_true")
    speak_long.set_defaults(func=command_speak_long)

    session = subparsers.add_parser("session")
    add_runtime_args(session, ref_audio_required=False)
    session.add_argument("--python")
    session.add_argument("--output-dir")
    session.add_argument("--dry-run", action="store_true")
    session.set_defaults(func=command_session)

    live_smoke = subparsers.add_parser("live-smoke")
    add_runtime_args(live_smoke, ref_audio_required=False)
    live_smoke.add_argument("--python")
    live_smoke.add_argument("--cases", default=str(DEFAULT_LIVE_SMOKE_CASES))
    live_smoke.add_argument("--output-dir")
    live_smoke.add_argument("--limit", type=int, default=3)
    live_smoke.add_argument("--startup-timeout", type=float, default=300.0)
    live_smoke.add_argument("--utterance-timeout", type=float, default=180.0)
    live_smoke.add_argument("--play", action="store_true")
    live_smoke.add_argument("--package", action="store_true")
    live_smoke.add_argument("--dry-run", action="store_true")
    live_smoke.set_defaults(func=command_live_smoke)

    bench = subparsers.add_parser("bench")
    add_runtime_args(bench, ref_audio_required=False)
    bench.add_argument("--python")
    bench.add_argument("--cases", default=str(DEFAULT_BENCHMARK_CASES))
    bench.add_argument("--output-dir")
    bench.add_argument("--play", action="store_true")
    bench.add_argument("--open", action="store_true")
    bench.add_argument("--package", action="store_true")
    bench.add_argument("--dry-run", action="store_true")
    bench.set_defaults(func=command_bench)

    profile_review = subparsers.add_parser("profile-review")
    add_runtime_args(profile_review, ref_audio_required=False)
    profile_review.add_argument("--python")
    profile_review.add_argument("--cases", default=str(DEFAULT_BENCHMARK_CASES))
    profile_review.add_argument("--output-dir")
    profile_review.add_argument("--profile-a", choices=sorted(LATENCY_PROFILES), default="fast")
    profile_review.add_argument("--profile-b", choices=sorted(LATENCY_PROFILES), default="quality")
    profile_review.add_argument("--play", action="store_true")
    profile_review.add_argument("--open", action="store_true")
    profile_review.add_argument("--package", action="store_true")
    profile_review.add_argument("--dry-run", action="store_true")
    profile_review.set_defaults(func=command_profile_review)

    review = subparsers.add_parser("review")
    review.add_argument("--path")
    review.add_argument("--benchmark-dir")
    review.add_argument("--dry-run", action="store_true")
    review.set_defaults(func=command_review)

    decide_review = subparsers.add_parser("decide-review")
    decide_review.add_argument("--path")
    decide_review.add_argument("--benchmark-dir")
    decide_review.add_argument("--review-json")
    decide_review.add_argument("--output")
    decide_review.add_argument("--package", action="store_true")
    decide_review.add_argument("--dry-run", action="store_true")
    decide_review.set_defaults(func=command_decide_review)

    product_status = subparsers.add_parser("product-status")
    product_status.add_argument("--python")
    product_status.add_argument("--ref-audio")
    product_status.add_argument("--voice-profile", default=DEFAULT_VOICE_PROFILE)
    product_status.add_argument("--path")
    product_status.add_argument("--benchmark-dir")
    product_status.add_argument("--format", choices=["json", "text"], default="json")
    product_status.add_argument("--strict", action="store_true")
    product_status.set_defaults(func=command_product_status)

    candidate = subparsers.add_parser("candidate")
    candidate.add_argument("--path")
    candidate.add_argument("--benchmark-dir")
    candidate.add_argument("--format", choices=["json", "text"], default="json")
    candidate.add_argument("--play", action="store_true")
    candidate.add_argument("--open", action="store_true")
    candidate.add_argument("--dry-run", action="store_true")
    candidate.add_argument("--strict", action="store_true")
    candidate.set_defaults(func=command_candidate)

    package_review = subparsers.add_parser("package-review")
    package_review.add_argument("--path")
    package_review.add_argument("--benchmark-dir")
    package_review.add_argument("--output")
    package_review.add_argument("--dry-run", action="store_true")
    package_review.set_defaults(func=command_package_review)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "voice_profile"):
        apply_voice_profile_defaults(args)
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
