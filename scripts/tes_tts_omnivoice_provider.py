#!/usr/bin/env python3
"""Optional OmniVoice provider for TES TTS.

This script is intentionally dependency-optional. The TES package can validate
and probe it without importing OmniVoice; synthesis runs only inside an
environment where the maintainer explicitly installed `omnivoice`.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import sys
import time
from typing import Any
import zipfile

from tes_tts_runtime_adapter import prepare_spoken_text


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.147"
DEFAULT_MODEL = "k2-fsa/OmniVoice"
DEFAULT_LANGUAGE = "pt"
DEFAULT_CACHE_DIR = ROOT / "tmp/tes-tts-omnivoice-provider"
DEFAULT_LOCAL_PYTHON = ROOT / "tmp/tes-tts-lab/omnivoice/.venv/bin/python"
DEFAULT_LOCAL_REF_AUDIO = ROOT / "tmp/tes-tts-lab/omnivoice/refs/audio-modelo-clone-mono24k.wav"
DEFAULT_OUTPUT_DIR = DEFAULT_CACHE_DIR / "audio"
DEFAULT_BENCHMARK_CASES = ROOT / "benchmarks/tes-tts/omnivoice-provider-cases.json"
DEFAULT_LIVE_SMOKE_CASES = ROOT / "benchmarks/tes-tts/live-session-utterance-fixtures.json"
DEFAULT_BENCHMARK_DIR = DEFAULT_CACHE_DIR / "benchmarks"
DEFAULT_SESSION_DIR = DEFAULT_CACHE_DIR / "sessions"
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
        return str(DEFAULT_LOCAL_PYTHON), "local_auto"
    return sys.executable, "current_python"


def resolve_ref_audio(explicit: str | None) -> tuple[Path | None, str]:
    if explicit:
        return Path(explicit), "arg"
    env_value = os.environ.get(ENV_REF_AUDIO)
    if env_value:
        return Path(env_value), "env"
    if DEFAULT_LOCAL_REF_AUDIO.exists():
        return DEFAULT_LOCAL_REF_AUDIO, "local_auto"
    return None, "missing"


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


def command_status(args: argparse.Namespace) -> int:
    provider_python, python_source = resolve_provider_python(args.python)
    ref_audio, ref_source = resolve_ref_audio(args.ref_audio)
    evidence = run_python_probe(provider_python)
    provider_available = (
        evidence.get("omnivoice_importable") is True
        and evidence.get("torch_importable") is True
        and evidence.get("soundfile_importable") is True
    )
    ref_audio_ready = bool(ref_audio and ref_audio.exists())
    ready = provider_available and ref_audio_ready
    emit(
        {
            "provider": "omnivoice",
            "status": "ready" if ready else "needs_setup",
            "version": VERSION,
            "runtime_dependency": "optional_external_python_env",
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
    return [
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


def latency_profile_metadata(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "requested_latency_profile": getattr(args, "requested_latency_profile", getattr(args, "latency_profile", None)),
        "latency_profile_source": getattr(args, "latency_profile_source", "explicit"),
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
    return prompt_cache_path(Path(args.cache_dir), args.model, ref_audio, args.ref_text)


def playback_audio(output: Path) -> dict[str, Any]:
    player = shutil.which("afplay")
    if not player:
        return {"playback_status": "not_available", "player": None}
    completed = subprocess.run([player, str(output)], check=False)
    return {
        "playback_status": "played" if completed.returncode == 0 else "failed",
        "player": player,
        "returncode": completed.returncode,
    }


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
    return prepare_spoken_text(text, locale)["redacted_text"]


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


def product_state_and_next_action(*, ready: bool, review_html: Path | None, decision: str | None) -> tuple[str, str]:
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
    return "\n".join(
        [
            f"TES TTS OmniVoice product state: {payload.get('product_state')}",
            f"Provider: {provider}",
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
    ref_audio, ref_source = resolve_ref_audio(args.ref_audio)
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
    ref_audio, ref_source = resolve_ref_audio(args.ref_audio)
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
                "num_step": args.num_step,
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
    ref_audio, ref_source = resolve_ref_audio(args.ref_audio)
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
                "num_step": args.num_step,
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


def command_live_smoke(args: argparse.Namespace) -> int:
    provider_python, python_source = resolve_provider_python(args.python)
    ref_audio, ref_source = resolve_ref_audio(args.ref_audio)
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
        "num_step": args.num_step,
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


def command_speak(args: argparse.Namespace) -> int:
    provider_python, python_source = resolve_provider_python(args.python)
    ref_audio, ref_source = resolve_ref_audio(args.ref_audio)
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
                "num_step": args.num_step,
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
    ref_audio, ref_source = resolve_ref_audio(args.ref_audio)
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
        payload["benchmark_summary"] = {
            "case_count": len(outputs),
            "avg_rtf": round(sum(rtfs) / len(rtfs), 4) if rtfs else None,
            "total_audio_duration_seconds": round(sum(durations), 3) if durations else None,
            "total_generation_ms": round(sum(generations), 3) if generations else None,
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
    ref_audio, ref_source = resolve_ref_audio(args.ref_audio)
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
    with contextlib.redirect_stdout(sys.stderr):
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
    with contextlib.redirect_stdout(sys.stderr):
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


def command_prepare_prompt(args: argparse.Namespace) -> int:
    apply_latency_profile(args)
    modules = load_omnivoice_modules()
    torch = modules["torch"]
    OmniVoice = modules["OmniVoice"]
    device = best_device(torch, args.device)
    total_started = time.perf_counter()
    load_started = time.perf_counter()
    with contextlib.redirect_stdout(sys.stderr):
        model = OmniVoice.from_pretrained(args.model, device_map=device, dtype=torch.float16)
    model_load_ms = round((time.perf_counter() - load_started) * 1000, 3)
    ref_audio = Path(args.ref_audio)
    cache_path = prompt_cache_path_from_args(args, ref_audio)
    _prompt, prompt_metrics = load_or_create_voice_prompt(
        model=model,
        torch=torch,
        ref_audio=ref_audio,
        ref_text=args.ref_text,
        cache_path=cache_path,
        refresh=args.refresh_prompt,
    )
    emit(
        {
            "provider": "omnivoice",
            "status": "PASS",
            "version": VERSION,
            "mode": "voice_prompt_cache",
            "model": args.model,
            "device": device,
            "language": args.language,
            "latency_profile": args.latency_profile,
            **latency_profile_metadata(args),
            "num_step": args.num_step,
            "model_load_ms": model_load_ms,
            **prompt_metrics,
            "total_ms": round((time.perf_counter() - total_started) * 1000, 3),
            "allows_install": False,
            "allows_download": False,
            "allows_global_config_write": False,
        }
    )
    return 0


def command_synthesize(args: argparse.Namespace) -> int:
    apply_latency_profile(args)
    modules = load_omnivoice_modules()
    torch = modules["torch"]
    sf = modules["soundfile"]
    OmniVoice = modules["OmniVoice"]
    device = best_device(torch, args.device)
    text_info = provider_text(args.text, args.locale, args.text_mode)

    total_started = time.perf_counter()
    load_started = time.perf_counter()
    with contextlib.redirect_stdout(sys.stderr):
        model = OmniVoice.from_pretrained(args.model, device_map=device, dtype=torch.float16)
    model_load_ms = round((time.perf_counter() - load_started) * 1000, 3)
    cache_path = prompt_cache_path_from_args(args, Path(args.ref_audio))
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
            "latency_profile": args.latency_profile,
            **latency_profile_metadata(args),
            "num_step": args.num_step,
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
    apply_latency_profile(args)
    modules = load_omnivoice_modules()
    torch = modules["torch"]
    sf = modules["soundfile"]
    OmniVoice = modules["OmniVoice"]
    device = best_device(torch, args.device)
    cases = load_text_cases(Path(args.cases))

    total_started = time.perf_counter()
    load_started = time.perf_counter()
    with contextlib.redirect_stdout(sys.stderr):
        model = OmniVoice.from_pretrained(args.model, device_map=device, dtype=torch.float16)
    model_load_ms = round((time.perf_counter() - load_started) * 1000, 3)
    cache_path = prompt_cache_path_from_args(args, Path(args.ref_audio))
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
            "latency_profile": args.latency_profile,
            **latency_profile_metadata(args),
            "num_step": args.num_step,
            "model_load_ms": model_load_ms,
            **prompt_metrics,
            "outputs": outputs,
            "total_ms": round((time.perf_counter() - total_started) * 1000, 3),
        }
    )
    return 0


def command_serve(args: argparse.Namespace) -> int:
    apply_latency_profile(args)
    modules = load_omnivoice_modules()
    torch = modules["torch"]
    sf = modules["soundfile"]
    OmniVoice = modules["OmniVoice"]
    device = best_device(torch, args.device)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    total_started = time.perf_counter()
    load_started = time.perf_counter()
    with contextlib.redirect_stdout(sys.stderr):
        model = OmniVoice.from_pretrained(args.model, device_map=device, dtype=torch.float16)
    model_load_ms = round((time.perf_counter() - load_started) * 1000, 3)
    cache_path = prompt_cache_path_from_args(args, Path(args.ref_audio))
    prompt, prompt_metrics = load_or_create_voice_prompt(
        model=model,
        torch=torch,
        ref_audio=Path(args.ref_audio),
        ref_text=args.ref_text,
        cache_path=cache_path,
        refresh=args.refresh_prompt,
    )
    emit_jsonl(
        {
            "provider": "omnivoice",
            "status": "READY",
            "version": VERSION,
            "mode": "resident_session",
            "protocol": "jsonl_stdin_stdout",
            "model": args.model,
            "device": device,
            "language": args.language,
            "latency_profile": args.latency_profile,
            **latency_profile_metadata(args),
            "num_step": args.num_step,
            "output_dir": str(out_dir),
            "model_load_ms": model_load_ms,
            **prompt_metrics,
            "startup_ms": round((time.perf_counter() - total_started) * 1000, 3),
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
            text_info = provider_text(text, args.locale, args.text_mode)
            audio_metrics = synthesize_once(
                model=model,
                sf=sf,
                voice_prompt=prompt,
                text=text_info["text"],
                language=language,
                output=output,
                args=args,
            )
            emit_jsonl(
                {
                    "provider": "omnivoice",
                    "status": "PASS",
                    "version": VERSION,
                    "mode": "resident_session_utterance",
                    "id": request_id,
                    "latency_profile": args.latency_profile,
                    **latency_profile_metadata(args),
                    "num_step": args.num_step,
                    "text_mode": text_info["mode"],
                    "source_text_immutable": text_info["prepared"]["source_text_immutable"],
                    "redaction_count": text_info["prepared"]["redaction_count"],
                    "summary_behavior": text_info["prepared"]["summary_behavior"],
                    "command_execution": text_info["prepared"]["command_execution"],
                    "model_reused": True,
                    "voice_prompt_reused": True,
                    **audio_metrics,
                    "request_total_ms": round((time.perf_counter() - request_started) * 1000, 3),
                }
            )
        except Exception as exc:
            emit_jsonl(
                {
                    "provider": "omnivoice",
                    "status": "FAIL",
                    "version": VERSION,
                    "mode": "resident_session_utterance",
                    "error": str(exc),
                    "request_total_ms": round((time.perf_counter() - request_started) * 1000, 3),
                }
            )
        sys.stdout.flush()
    return 0


def add_runtime_args(parser: argparse.ArgumentParser, *, ref_audio_required: bool = True) -> None:
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--language", default=DEFAULT_LANGUAGE)
    parser.add_argument("--locale", default="pt-BR")
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
        choices=["redacted_source", "spoken_text", "raw"],
        default="redacted_source",
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
    add_runtime_args(prepare_prompt)
    prepare_prompt.set_defaults(func=command_prepare_prompt)

    serve = subparsers.add_parser("serve")
    add_runtime_args(serve)
    serve.add_argument("--output-dir", required=True)
    serve.set_defaults(func=command_serve)

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

    speak = subparsers.add_parser("speak")
    add_runtime_args(speak, ref_audio_required=False)
    speak.add_argument("--python")
    speak.add_argument("--text", required=True)
    speak.add_argument("--output")
    speak.add_argument("--play", action="store_true")
    speak.add_argument("--dry-run", action="store_true")
    speak.set_defaults(func=command_speak)

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
