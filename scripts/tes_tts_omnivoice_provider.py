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
import importlib.util
import json
import os
from pathlib import Path
import shutil
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
DEFAULT_LOCAL_PYTHON = ROOT / "tmp/tes-tts-lab/omnivoice/.venv/bin/python"
DEFAULT_LOCAL_REF_AUDIO = ROOT / "tmp/tes-tts-lab/omnivoice/refs/audio-modelo-clone-mono24k.wav"
DEFAULT_OUTPUT_DIR = DEFAULT_CACHE_DIR / "audio"
DEFAULT_BENCHMARK_CASES = ROOT / "benchmarks/tes-tts/omnivoice-provider-cases.json"
DEFAULT_BENCHMARK_DIR = DEFAULT_CACHE_DIR / "benchmarks"
ENV_PYTHON = "TES_TTS_OMNIVOICE_PYTHON"
ENV_REF_AUDIO = "TES_TTS_OMNIVOICE_REF_AUDIO"
ENV_OUTPUT_DIR = "TES_TTS_OMNIVOICE_OUTPUT_DIR"


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


def synthesize_runtime_arg_tokens(args: argparse.Namespace, ref_audio: Path, output: Path) -> list[str]:
    return [
        *common_runtime_arg_tokens(args, ref_audio),
        "--output",
        str(output),
    ]


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


def redacted_case_text(case: dict[str, Any], locale: str) -> str:
    text = case.get("text")
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


def resolve_review_html(path: str | None, benchmark_dir: str | None) -> tuple[Path | None, str]:
    if path:
        candidate = Path(path)
        if candidate.is_dir():
            return candidate / "review.html", "arg_dir"
        return candidate, "arg_file"
    root = Path(benchmark_dir) if benchmark_dir else DEFAULT_BENCHMARK_DIR
    candidates = [item for item in root.glob("*/review.html") if item.is_file()]
    if not candidates:
        return None, "missing"
    candidates.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return candidates[0], "latest"


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
                "result_json": str(output_dir / "result.json"),
                "review_html": str(output_dir / "review.html"),
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
    emit(payload)
    return completed.returncode


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

    status = subparsers.add_parser("status")
    status.add_argument("--python")
    status.add_argument("--ref-audio")
    status.set_defaults(func=command_status)

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

    speak = subparsers.add_parser("speak")
    add_runtime_args(speak, ref_audio_required=False)
    speak.add_argument("--python")
    speak.add_argument("--text", required=True)
    speak.add_argument("--output")
    speak.add_argument("--play", action="store_true")
    speak.add_argument("--dry-run", action="store_true")
    speak.set_defaults(func=command_speak)

    bench = subparsers.add_parser("bench")
    add_runtime_args(bench, ref_audio_required=False)
    bench.add_argument("--python")
    bench.add_argument("--cases", default=str(DEFAULT_BENCHMARK_CASES))
    bench.add_argument("--output-dir")
    bench.add_argument("--play", action="store_true")
    bench.add_argument("--open", action="store_true")
    bench.add_argument("--dry-run", action="store_true")
    bench.set_defaults(func=command_bench)

    review = subparsers.add_parser("review")
    review.add_argument("--path")
    review.add_argument("--benchmark-dir")
    review.add_argument("--dry-run", action="store_true")
    review.set_defaults(func=command_review)
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
