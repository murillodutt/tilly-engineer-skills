#!/usr/bin/env python3
"""Validate the optional TES TTS OmniVoice provider surface."""

from __future__ import annotations

import argparse
import ast
import contextlib
import http.server
import importlib.util
import io
import json
import os
from pathlib import Path
import socketserver
import subprocess
import sys
import tempfile
import threading
from typing import Any
import wave


ROOT = Path(__file__).resolve().parents[1]
PROVIDER_SCRIPT = ROOT / "scripts/tes_tts_omnivoice_provider.py"
DIRECT_KERNEL_SCRIPT = ROOT / "scripts/tes_tts_omnivoice_direct_kernel.py"
FIXTURE_PATH = ROOT / "benchmarks/tes-tts/omnivoice-provider-cases.json"
VERSION = "0.3.147"
FORBIDDEN_TOP_LEVEL_IMPORTS = {"omnivoice", "torch", "soundfile"}
REQUIRED_PROBE_KEYS = {
    "provider",
    "status",
    "version",
    "languages",
    "license_note",
    "runtime_dependency",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
    "certifies_provider_support",
    "evidence",
    "reason",
}
REQUIRED_STATUS_KEYS = {
    "provider",
    "status",
    "version",
    "runtime_dependency",
    "provider_python",
    "provider_python_source",
    "ref_audio",
    "ref_audio_source",
    "ref_audio_ready",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
    "evidence",
}
REQUIRED_DRY_RUN_KEYS = {
    "provider",
    "status",
    "version",
    "mode",
    "provider_python",
    "provider_python_source",
    "ref_audio",
    "ref_audio_source",
    "output",
    "text_chars",
    "play_requested",
    "latency_profile",
    "requested_latency_profile",
    "latency_profile_source",
    "num_step",
    "command_shape",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
}
REQUIRED_SERVER_DRY_RUN_KEYS = {
    "provider",
    "status",
    "version",
    "mode",
    "server_url",
    "server_url_source",
    "endpoint",
    "api_key_env",
    "api_key_present",
    "model",
    "voice",
    "language",
    "speaker",
    "instructions_present",
    "task_type",
    "max_new_tokens",
    "guidance_scale",
    "denoise",
    "t_shift",
    "position_temperature",
    "class_temperature",
    "postprocess_output",
    "stream_requested",
    "num_step",
    "server_mode",
    "clone_ref_audio_present",
    "clone_ref_text_present",
    "output",
    "text_chars",
    "play_requested",
    "request_shape",
    "runtime_dependency",
    "route_status",
    "product_path",
    "legacy_reason",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
}
REQUIRED_SERVER_LONG_DRY_RUN_KEYS = {
    "provider",
    "status",
    "version",
    "mode",
    "server_url",
    "server_url_source",
    "endpoint",
    "api_key_env",
    "api_key_present",
    "model",
    "voice",
    "speaker",
    "instructions_present",
    "task_type",
    "max_new_tokens",
    "guidance_scale",
    "denoise",
    "t_shift",
    "position_temperature",
    "class_temperature",
    "postprocess_output",
    "stream_requested",
    "num_step",
    "server_mode",
    "clone_ref_audio_present",
    "clone_ref_text_present",
    "text_chars",
    "chunk_count",
    "chunk_chars",
    "chunk_languages",
    "language_mode",
    "max_chunk_chars",
    "output_dir",
    "result_json",
    "play_requested",
    "combine_requested",
    "inter_chunk_silence_ms",
    "request_shape",
    "runtime_dependency",
    "route_status",
    "product_path",
    "legacy_reason",
    "fallback_used",
    "provider_exclusive",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
}
REQUIRED_SERVER_STATUS_KEYS = {
    "provider",
    "status",
    "version",
    "mode",
    "server_url",
    "server_url_source",
    "endpoint",
    "health_url",
    "capability_endpoints",
    "api_key_env",
    "api_key_present",
    "timeout_seconds",
    "runtime_dependency",
    "route_status",
    "product_path",
    "legacy_reason",
    "probe_scope",
    "connectivity",
    "health",
    "capabilities",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
}
REQUIRED_BENCH_DRY_RUN_KEYS = {
    "provider",
    "status",
    "version",
    "mode",
    "provider_python",
    "provider_python_source",
    "ref_audio",
    "ref_audio_source",
    "cases",
    "output_dir",
    "play_requested",
    "open_requested",
    "package_requested",
    "latency_profile",
    "requested_latency_profile",
    "latency_profile_source",
    "num_step",
    "result_json",
    "review_html",
    "package_zip",
    "command_shape",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
}
REQUIRED_PROFILE_REVIEW_DRY_RUN_KEYS = {
    "provider",
    "status",
    "version",
    "mode",
    "provider_python",
    "provider_python_source",
    "ref_audio",
    "ref_audio_source",
    "cases",
    "output_dir",
    "profiles",
    "play_requested",
    "open_requested",
    "package_requested",
    "result_json",
    "review_html",
    "package_zip",
    "command_shapes",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
}
REQUIRED_WARM_CACHE_DRY_RUN_KEYS = {
    "provider",
    "status",
    "version",
    "mode",
    "provider_python",
    "provider_python_source",
    "ref_audio",
    "ref_audio_source",
    "voice_prompt_cache_path",
    "voice_prompt_cache_exists",
    "refresh_requested",
    "latency_profile",
    "requested_latency_profile",
    "latency_profile_source",
    "num_step",
    "command_shape",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
}
REQUIRED_SESSION_DRY_RUN_KEYS = {
    "provider",
    "status",
    "version",
    "mode",
    "provider_python",
    "provider_python_source",
    "ref_audio",
    "ref_audio_source",
    "output_dir",
    "protocol",
    "resident_model",
    "resident_voice_prompt",
    "latency_profile",
    "requested_latency_profile",
    "latency_profile_source",
    "num_step",
    "latency_profiles",
    "command_shape",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
}
REQUIRED_LONG_READ_DRY_RUN_KEYS = {
    "provider",
    "status",
    "version",
    "mode",
    "provider_python",
    "provider_python_source",
    "ref_audio",
    "ref_audio_source",
    "text_chars",
    "chunk_count",
    "chunk_chars",
    "chunk_languages",
    "language_mode",
    "max_chunk_chars",
    "output_dir",
    "result_json",
    "monitor_log",
    "monitor_heartbeat_seconds",
    "startup_timeout_seconds",
    "utterance_timeout_seconds",
    "slow_chunk_ms",
    "play_requested",
    "combine_requested",
    "inter_chunk_silence_ms",
    "chunk_edge_silence_ms",
    "latency_profile",
    "requested_latency_profile",
    "latency_profile_source",
    "num_step",
    "protocol",
    "resident_model",
    "resident_voice_prompt",
    "fallback_used",
    "provider_exclusive",
    "command_shape",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
}
REQUIRED_LIVE_SMOKE_DRY_RUN_KEYS = {
    "provider",
    "status",
    "version",
    "mode",
    "provider_python",
    "provider_python_source",
    "ref_audio",
    "ref_audio_source",
    "cases",
    "case_count",
    "case_ids",
    "output_dir",
    "result_json",
    "review_html",
    "package_zip",
    "play_requested",
    "package_requested",
    "startup_timeout_seconds",
    "utterance_timeout_seconds",
    "latency_profile",
    "requested_latency_profile",
    "latency_profile_source",
    "num_step",
    "protocol",
    "resident_model",
    "resident_voice_prompt",
    "command_shape",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
}
REQUIRED_REVIEW_DRY_RUN_KEYS = {
    "provider",
    "status",
    "version",
    "mode",
    "review_html",
    "review_source",
    "open_requested",
    "exists",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
}
REQUIRED_PACKAGE_DRY_RUN_KEYS = {
    "provider",
    "status",
    "version",
    "mode",
    "review_html",
    "review_source",
    "package_zip",
    "file_count",
    "included_files",
    "manifest_schema",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
}
REQUIRED_PRODUCT_STATUS_KEYS = {
    "provider",
    "status",
    "version",
    "mode",
    "product_state",
    "next_action",
    "provider_ready",
    "provider_python",
    "provider_python_source",
    "ref_audio",
    "ref_audio_source",
    "ref_audio_ready",
    "review_html",
    "review_source",
    "review_exists",
    "result_json",
    "result_json_exists",
    "decision_json",
    "decision_json_exists",
    "decision",
    "review_kind",
    "recommended_latency_profile",
    "case_count",
    "scored_case_count",
    "avg_rtf",
    "total_audio_duration_seconds",
    "total_generation_ms",
    "package_zip",
    "package_zip_exists",
    "package_sha256",
    "release_identity",
    "sync_status",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
    "allows_sync",
    "allows_release",
}
REQUIRED_CANDIDATE_KEYS = {
    "provider",
    "status",
    "version",
    "mode",
    "candidate_ready",
    "next_action",
    "review_html",
    "review_source",
    "review_exists",
    "decision_json",
    "decision_json_exists",
    "decision",
    "review_kind",
    "recommended_latency_profile",
    "case_count",
    "scored_case_count",
    "package_zip",
    "package_zip_exists",
    "package_sha256",
    "audio_count",
    "audio_files",
    "play_requested",
    "open_requested",
    "dry_run",
    "open_result",
    "playback_results",
    "allows_install",
    "allows_download",
    "allows_global_config_write",
    "allows_sync",
    "allows_release",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_source_imports() -> list[str]:
    failures: list[str] = []
    for source in (PROVIDER_SCRIPT, DIRECT_KERNEL_SCRIPT):
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if root in FORBIDDEN_TOP_LEVEL_IMPORTS:
                        failures.append(f"{source.name} top-level optional import leaked: {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".", 1)[0]
                if root in FORBIDDEN_TOP_LEVEL_IMPORTS:
                    failures.append(f"{source.name} top-level optional import leaked: {node.module}")
    return failures


def validate_no_reference_text_logging() -> list[str]:
    failures: list[str] = []
    for source in (PROVIDER_SCRIPT, DIRECT_KERNEL_SCRIPT):
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                for key in node.keys:
                    if isinstance(key, ast.Constant) and key.value == "ref_text":
                        failures.append(f"{source.name} metrics must not emit reference voice text")
    return failures


def run_probe() -> tuple[dict[str, Any] | None, list[str]]:
    completed = subprocess.run(
        [sys.executable, str(PROVIDER_SCRIPT), "probe"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    failures: list[str] = []
    if completed.returncode not in (0, 2):
        failures.append(f"probe returned unexpected exit code {completed.returncode}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        failures.append(f"probe did not emit JSON: {exc}")
        return None, failures
    missing = sorted(REQUIRED_PROBE_KEYS - set(payload))
    extra = sorted(set(payload) - REQUIRED_PROBE_KEYS)
    if missing:
        failures.append(f"probe missing keys {missing}")
    if extra:
        failures.append(f"probe has extra keys {extra}")
    if payload.get("provider") != "omnivoice":
        failures.append("probe provider drifted")
    if payload.get("runtime_dependency") != "optional_external_python_env":
        failures.append("probe must keep OmniVoice optional")
    if payload.get("allows_install") is not False:
        failures.append("probe must not install providers")
    if payload.get("allows_download") is not False:
        failures.append("probe must not download models")
    if payload.get("allows_global_config_write") is not False:
        failures.append("probe must not write global config")
    if payload.get("status") not in {"provider_available", "provider_not_available"}:
        failures.append("probe status is invalid")
    return payload, failures


def run_status_and_dry_run() -> tuple[
    dict[str, Any] | None,
    dict[str, Any] | None,
    dict[str, Any] | None,
    dict[str, Any] | None,
    dict[str, Any] | None,
    dict[str, Any] | None,
    dict[str, Any] | None,
    list[str],
]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        ref = Path(tmp_dir) / "ref.wav"
        review_dir = Path(tmp_dir) / "review-dir"
        review_dir.mkdir()
        review = review_dir / "review.html"
        result = review_dir / "result.json"
        wav = review_dir / "case.wav"
        ref.write_bytes(b"not-real-audio-for-dry-run")
        review.write_text("<!doctype html><audio controls></audio>", encoding="utf-8")
        wav.write_bytes(b"fake-wave")
        result.write_text(
            json.dumps({"outputs": [{"id": "case", "output": str(wav)}]}, ensure_ascii=False),
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["TES_TTS_OMNIVOICE_PYTHON"] = sys.executable
        env["TES_TTS_OMNIVOICE_REF_AUDIO"] = str(ref)
        status_completed = subprocess.run(
            [sys.executable, str(PROVIDER_SCRIPT), "status"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=env,
        )
        if status_completed.returncode not in (0, 2):
            failures.append(f"status returned unexpected exit code {status_completed.returncode}")
        try:
            status_payload = json.loads(status_completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"status did not emit JSON: {exc}")
            status_payload = None

        dry_completed = subprocess.run(
            [
                sys.executable,
                str(PROVIDER_SCRIPT),
                "speak",
                "--text",
                "API_KEY=abc123SECRET deve ficar fora do dry-run.",
                "--dry-run",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=env,
        )
        if dry_completed.returncode != 0:
            failures.append(f"speak dry-run returned unexpected exit code {dry_completed.returncode}")
        try:
            dry_payload = json.loads(dry_completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"speak dry-run did not emit JSON: {exc}")
            dry_payload = None

        long_read_completed = subprocess.run(
            [
                sys.executable,
                str(PROVIDER_SCRIPT),
                "speak-long",
                "--text",
                (
                    "Primeiro bloco com ADR e OmniVoice precisa ser preservado sem fallback.\n\n"
                    "English technical terms: JSON, YAML, HTTP, Node JS, TypeScript, Python, "
                    "Open AI API, Trie, Aho Corasick, and thresholds.\n\n"
                    "Segundo bloco confirma que a leitura longa segue pela sessão residente."
                ),
                "--chunk-chars",
                "180",
                "--language",
                "auto",
                "--chunk-edge-silence-ms",
                "120",
                "--play",
                "--dry-run",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=env,
        )
        if long_read_completed.returncode != 0:
            failures.append(f"speak-long dry-run returned unexpected exit code {long_read_completed.returncode}")
        try:
            long_read_payload = json.loads(long_read_completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"speak-long dry-run did not emit JSON: {exc}")
            long_read_payload = None

        bench_completed = subprocess.run(
            [
                sys.executable,
                str(PROVIDER_SCRIPT),
                "bench",
                "--ref-text",
                "voz privada SECRET_REF_TEXT",
                "--play",
                "--open",
                "--package",
                "--dry-run",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=env,
        )
        if bench_completed.returncode != 0:
            failures.append(f"bench dry-run returned unexpected exit code {bench_completed.returncode}")
        try:
            bench_payload = json.loads(bench_completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"bench dry-run did not emit JSON: {exc}")
            bench_payload = None

        profile_review_completed = subprocess.run(
            [
                sys.executable,
                str(PROVIDER_SCRIPT),
                "profile-review",
                "--ref-text",
                "voz privada SECRET_REF_TEXT",
                "--play",
                "--open",
                "--package",
                "--dry-run",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=env,
        )
        if profile_review_completed.returncode != 0:
            failures.append(f"profile-review dry-run returned unexpected exit code {profile_review_completed.returncode}")
        try:
            profile_review_payload = json.loads(profile_review_completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"profile-review dry-run did not emit JSON: {exc}")
            profile_review_payload = None

        review_completed = subprocess.run(
            [
                sys.executable,
                str(PROVIDER_SCRIPT),
                "review",
                "--path",
                str(review),
                "--dry-run",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=env,
        )
        if review_completed.returncode != 0:
            failures.append(f"review dry-run returned unexpected exit code {review_completed.returncode}")
        try:
            review_payload = json.loads(review_completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"review dry-run did not emit JSON: {exc}")
            review_payload = None

        package_completed = subprocess.run(
            [
                sys.executable,
                str(PROVIDER_SCRIPT),
                "package-review",
                "--path",
                str(review),
                "--dry-run",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=env,
        )
        if package_completed.returncode != 0:
            failures.append(f"package-review dry-run returned unexpected exit code {package_completed.returncode}")
        try:
            package_payload = json.loads(package_completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"package-review dry-run did not emit JSON: {exc}")
            package_payload = None
    return (
        status_payload,
        dry_payload,
        long_read_payload,
        bench_payload,
        profile_review_payload,
        review_payload,
        package_payload,
        failures,
    )


def validate_status_payload(payload: dict[str, Any] | None) -> list[str]:
    if payload is None:
        return []
    failures: list[str] = []
    missing = sorted(REQUIRED_STATUS_KEYS - set(payload))
    extra = sorted(set(payload) - REQUIRED_STATUS_KEYS)
    if missing:
        failures.append(f"status missing keys {missing}")
    if extra:
        failures.append(f"status has extra keys {extra}")
    if payload.get("provider") != "omnivoice":
        failures.append("status provider drifted")
    if payload.get("runtime_dependency") != "optional_external_python_env":
        failures.append("status must keep OmniVoice optional")
    if payload.get("allows_install") is not False:
        failures.append("status must not install providers")
    if payload.get("allows_download") is not False:
        failures.append("status must not download models")
    if payload.get("allows_global_config_write") is not False:
        failures.append("status must not write global config")
    if payload.get("status") not in {"ready", "needs_setup"}:
        failures.append("status value is invalid")
    return failures


def validate_dry_run_payload(payload: dict[str, Any] | None) -> list[str]:
    if payload is None:
        return []
    failures: list[str] = []
    missing = sorted(REQUIRED_DRY_RUN_KEYS - set(payload))
    extra = sorted(set(payload) - REQUIRED_DRY_RUN_KEYS)
    if missing:
        failures.append(f"speak dry-run missing keys {missing}")
    if extra:
        failures.append(f"speak dry-run has extra keys {extra}")
    if payload.get("status") != "DRY_RUN":
        failures.append("speak dry-run status drifted")
    if payload.get("mode") != "product_shortcut":
        failures.append("speak dry-run mode drifted")
    if payload.get("allows_install") is not False:
        failures.append("speak dry-run must not install providers")
    if payload.get("allows_download") is not False:
        failures.append("speak dry-run must not download models")
    command_shape = payload.get("command_shape")
    if not isinstance(command_shape, list):
        failures.append("speak dry-run command_shape must be a list")
    else:
        joined = " ".join(str(part) for part in command_shape)
        if "abc123SECRET" in joined or "API_KEY=" in joined:
            failures.append("speak dry-run leaked source text in command_shape")
        if "<redacted>" not in command_shape:
            failures.append("speak dry-run must redact command text")
    return failures


def validate_server_legacy_metadata(payload: dict[str, Any], label: str) -> list[str]:
    failures: list[str] = []
    if payload.get("route_status") != "legacy_lab_compatibility":
        failures.append(f"{label} must mark server route as legacy lab compatibility")
    if payload.get("product_path") != "direct_resident_omnivoice":
        failures.append(f"{label} must point to direct/resident OmniVoice as product path")
    if "server route is retained" not in str(payload.get("legacy_reason")):
        failures.append(f"{label} must explain why server route remains")
    return failures


def validate_server_route_command() -> list[str]:
    failures: list[str] = []

    def wav_bytes() -> bytes:
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as handle:
            handle.setnchannels(1)
            handle.setsampwidth(2)
            handle.setframerate(24000)
            handle.writeframes(b"\x00\x00" * 2400)
        return buffer.getvalue()

    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        output = root / "server.wav"
        status_dry_completed = subprocess.run(
            [
                sys.executable,
                str(PROVIDER_SCRIPT),
                "server-status",
                "--server-url",
                "http://127.0.0.1:9999",
                "--api-key-env",
                "TES_TTS_FAKE_SERVER_KEY",
                "--dry-run",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if status_dry_completed.returncode != 0:
            failures.append(f"server-status dry-run returned unexpected exit code {status_dry_completed.returncode}")
            return failures
        try:
            status_dry_payload = json.loads(status_dry_completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"server-status dry-run did not emit JSON: {exc}")
            return failures
        missing = sorted(REQUIRED_SERVER_STATUS_KEYS - set(status_dry_payload))
        extra = sorted(set(status_dry_payload) - REQUIRED_SERVER_STATUS_KEYS)
        if missing:
            failures.append(f"server-status dry-run missing keys {missing}")
        if extra:
            failures.append(f"server-status dry-run has extra keys {extra}")
        if status_dry_payload.get("status") != "DRY_RUN":
            failures.append("server-status dry-run status drifted")
        failures.extend(validate_server_legacy_metadata(status_dry_payload, "server-status dry-run"))
        if status_dry_payload.get("probe_scope") != "tcp_connect_plus_optional_health_no_synthesis":
            failures.append("server-status must stay a no-synthesis TCP/health preflight")
        if status_dry_payload.get("endpoint") != "http://127.0.0.1:9999/v1/audio/speech":
            failures.append("server-status must derive OpenAI-compatible speech endpoint")
        if status_dry_payload.get("health_url") != "http://127.0.0.1:9999/health":
            failures.append("server-status must derive community health endpoint")
        capability_endpoints = status_dry_payload.get("capability_endpoints")
        if not isinstance(capability_endpoints, dict):
            failures.append("server-status must emit capability endpoint plan")
        else:
            if capability_endpoints.get("audio_voices") != "http://127.0.0.1:9999/v1/audio/voices":
                failures.append("server-status must derive audio voices endpoint")
            if capability_endpoints.get("voices") != "http://127.0.0.1:9999/v1/voices":
                failures.append("server-status must derive legacy voices endpoint")
        v1_dry_completed = subprocess.run(
            [
                sys.executable,
                str(PROVIDER_SCRIPT),
                "server-status",
                "--server-url",
                "http://127.0.0.1:9999/v1",
                "--discover-capabilities",
                "--dry-run",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if v1_dry_completed.returncode != 0:
            failures.append(f"server-status /v1 dry-run returned unexpected exit code {v1_dry_completed.returncode}")
            return failures
        try:
            v1_dry_payload = json.loads(v1_dry_completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"server-status /v1 dry-run did not emit JSON: {exc}")
            return failures
        if v1_dry_payload.get("endpoint") != "http://127.0.0.1:9999/v1/audio/speech":
            failures.append("server-status must not duplicate /v1 for speech endpoint")
        if v1_dry_payload.get("health_url") != "http://127.0.0.1:9999/health":
            failures.append("server-status /v1 base must derive root health endpoint")
        v1_capability_endpoints = v1_dry_payload.get("capability_endpoints")
        if not isinstance(v1_capability_endpoints, dict):
            failures.append("server-status /v1 dry-run must emit capability endpoints")
        elif v1_capability_endpoints.get("audio_models") != "http://127.0.0.1:9999/v1/audio/models":
            failures.append("server-status /v1 base must derive audio models endpoint")
        for key in ("allows_install", "allows_download", "allows_global_config_write"):
            if status_dry_payload.get(key) is not False:
                failures.append(f"server-status dry-run must keep {key}=false")

        dry_completed = subprocess.run(
            [
                sys.executable,
                str(PROVIDER_SCRIPT),
                "speak-server",
                "--server-url",
                "http://127.0.0.1:9999",
                "--api-key-env",
                "TES_TTS_FAKE_SERVER_KEY",
                "--model",
                "omnivoice",
                "--voice",
                "tes-tts-local-clone",
                "--language",
                "pt",
                "--speaker",
                "tes-tts-local-clone",
                "--instructions",
                "Leia em PT-BR preservando termos tecnicos em ingles.",
                "--task-type",
                "CustomVoice",
                "--max-new-tokens",
                "2048",
                "--guidance-scale",
                "3.0",
                "--denoise",
                "--t-shift",
                "0.1",
                "--position-temperature",
                "0.0",
                "--class-temperature",
                "0.0",
                "--postprocess-output",
                "--stream",
                "--num-step",
                "8",
                "--text",
                "API_KEY=abc123SECRET deve ficar fora do dry-run.",
                "--output",
                str(output),
                "--dry-run",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if dry_completed.returncode != 0:
            failures.append(f"speak-server dry-run returned unexpected exit code {dry_completed.returncode}")
            return failures
        try:
            dry_payload = json.loads(dry_completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"speak-server dry-run did not emit JSON: {exc}")
            return failures

        missing = sorted(REQUIRED_SERVER_DRY_RUN_KEYS - set(dry_payload))
        extra = sorted(set(dry_payload) - REQUIRED_SERVER_DRY_RUN_KEYS)
        if missing:
            failures.append(f"speak-server dry-run missing keys {missing}")
        if extra:
            failures.append(f"speak-server dry-run has extra keys {extra}")
        if dry_payload.get("status") != "DRY_RUN":
            failures.append("speak-server dry-run status drifted")
        if dry_payload.get("mode") != "product_server_shortcut":
            failures.append("speak-server dry-run mode drifted")
        failures.extend(validate_server_legacy_metadata(dry_payload, "speak-server dry-run"))
        if dry_payload.get("runtime_dependency") != "optional_local_openai_compatible_http_server":
            failures.append("speak-server must stay optional local server route")
        if dry_payload.get("endpoint") != "http://127.0.0.1:9999/v1/audio/speech":
            failures.append("speak-server must derive OpenAI-compatible speech endpoint")
        if dry_payload.get("language") != "pt":
            failures.append("speak-server dry-run must report server language")
        if dry_payload.get("task_type") != "CustomVoice":
            failures.append("speak-server dry-run must report task_type")
        if dry_payload.get("max_new_tokens") != 2048:
            failures.append("speak-server dry-run must report max_new_tokens")
        if dry_payload.get("guidance_scale") != 3.0:
            failures.append("speak-server dry-run must report guidance_scale")
        if dry_payload.get("denoise") is not True:
            failures.append("speak-server dry-run must report denoise")
        if dry_payload.get("t_shift") != 0.1:
            failures.append("speak-server dry-run must report t_shift")
        if dry_payload.get("position_temperature") != 0.0:
            failures.append("speak-server dry-run must report position_temperature")
        if dry_payload.get("class_temperature") != 0.0:
            failures.append("speak-server dry-run must report class_temperature")
        if dry_payload.get("postprocess_output") is not True:
            failures.append("speak-server dry-run must report postprocess_output")
        request_shape = dry_payload.get("request_shape")
        if not isinstance(request_shape, dict) or request_shape.get("input") != "<redacted>":
            failures.append("speak-server dry-run must redact request input")
        elif request_shape.get("instructions") != "<redacted>":
            failures.append("speak-server dry-run must redact server instructions")
        elif request_shape.get("language") != "pt":
            failures.append("speak-server dry-run request shape must include language")
        elif request_shape.get("task_type") != "CustomVoice":
            failures.append("speak-server dry-run request shape must include task_type")
        elif request_shape.get("guidance_scale") != 3.0:
            failures.append("speak-server dry-run request shape must include guidance_scale")
        if dry_payload.get("speaker") != "tes-tts-local-clone":
            failures.append("speak-server dry-run must report speaker control field")
        if dry_payload.get("instructions_present") is not True:
            failures.append("speak-server dry-run must report instructions without leaking them")
        if dry_payload.get("stream_requested") is not True:
            failures.append("speak-server dry-run must report stream intent")
        if dry_payload.get("num_step") != 8:
            failures.append("speak-server dry-run must report num_step control field")
        if "abc123SECRET" in dry_completed.stdout or "API_KEY=" in dry_completed.stdout:
            failures.append("speak-server dry-run leaked source text")
        if "preservando termos tecnicos" in dry_completed.stdout:
            failures.append("speak-server dry-run leaked instruction text")
        for key in ("allows_install", "allows_download", "allows_global_config_write"):
            if dry_payload.get(key) is not False:
                failures.append(f"speak-server dry-run must keep {key}=false")

        long_dry_completed = subprocess.run(
            [
                sys.executable,
                str(PROVIDER_SCRIPT),
                "speak-long-server",
                "--server-url",
                "http://127.0.0.1:9999",
                "--speaker",
                "tes-tts-local-clone",
                "--instructions",
                "Mantenha ingles tecnico natural.",
                "--task-type",
                "CustomVoice",
                "--max-new-tokens",
                "2048",
                "--guidance-scale",
                "3.0",
                "--denoise",
                "--t-shift",
                "0.1",
                "--position-temperature",
                "0.0",
                "--class-temperature",
                "0.0",
                "--postprocess-output",
                "--no-stream",
                "--num-step",
                "12",
                "--text",
                (
                    "Primeiro bloco em PT-BR com ADR e API.\n\n"
                    "English technical terms: JSON, YAML, HTTP, Node JS, TypeScript, Python, "
                    "Open AI API, Trie, Aho Corasick, and thresholds.\n\n"
                    "Segundo bloco em PT-BR para fechar."
                ),
                "--chunk-chars",
                "120",
                "--output-dir",
                str(root / "server-long"),
                "--combine",
                "--dry-run",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if long_dry_completed.returncode != 0:
            failures.append(f"speak-long-server dry-run returned unexpected exit code {long_dry_completed.returncode}")
            return failures
        try:
            long_dry_payload = json.loads(long_dry_completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"speak-long-server dry-run did not emit JSON: {exc}")
            return failures
        missing = sorted(REQUIRED_SERVER_LONG_DRY_RUN_KEYS - set(long_dry_payload))
        extra = sorted(set(long_dry_payload) - REQUIRED_SERVER_LONG_DRY_RUN_KEYS)
        if missing:
            failures.append(f"speak-long-server dry-run missing keys {missing}")
        if extra:
            failures.append(f"speak-long-server dry-run has extra keys {extra}")
        if long_dry_payload.get("mode") != "product_server_long_read":
            failures.append("speak-long-server dry-run mode drifted")
        failures.extend(validate_server_legacy_metadata(long_dry_payload, "speak-long-server dry-run"))
        if long_dry_payload.get("speaker") != "tes-tts-local-clone":
            failures.append("speak-long-server dry-run must report speaker control field")
        if long_dry_payload.get("instructions_present") is not True:
            failures.append("speak-long-server dry-run must report instructions without leaking them")
        if long_dry_payload.get("task_type") != "CustomVoice":
            failures.append("speak-long-server dry-run must report task_type")
        if long_dry_payload.get("max_new_tokens") != 2048:
            failures.append("speak-long-server dry-run must report max_new_tokens")
        if long_dry_payload.get("guidance_scale") != 3.0:
            failures.append("speak-long-server dry-run must report guidance_scale")
        if long_dry_payload.get("denoise") is not True:
            failures.append("speak-long-server dry-run must report denoise")
        if long_dry_payload.get("t_shift") != 0.1:
            failures.append("speak-long-server dry-run must report t_shift")
        if long_dry_payload.get("position_temperature") != 0.0:
            failures.append("speak-long-server dry-run must report position_temperature")
        if long_dry_payload.get("class_temperature") != 0.0:
            failures.append("speak-long-server dry-run must report class_temperature")
        if long_dry_payload.get("postprocess_output") is not True:
            failures.append("speak-long-server dry-run must report postprocess_output")
        if long_dry_payload.get("stream_requested") is not False:
            failures.append("speak-long-server dry-run must report disabled stream intent")
        if long_dry_payload.get("num_step") != 12:
            failures.append("speak-long-server dry-run must report num_step control field")
        long_request_shape = long_dry_payload.get("request_shape")
        if not isinstance(long_request_shape, dict) or long_request_shape.get("instructions") != "<redacted>":
            failures.append("speak-long-server dry-run must redact server instructions")
        elif long_request_shape.get("language") != "pt":
            failures.append("speak-long-server dry-run request shape must include first chunk language")
        elif long_request_shape.get("task_type") != "CustomVoice":
            failures.append("speak-long-server dry-run request shape must include task_type")
        elif long_request_shape.get("guidance_scale") != 3.0:
            failures.append("speak-long-server dry-run request shape must include guidance_scale")
        if long_dry_payload.get("chunk_languages") != ["pt", "en", "pt"]:
            failures.append("speak-long-server must preserve PT/EN/PT chunk language plan")
        if long_dry_payload.get("combine_requested") is not True:
            failures.append("speak-long-server dry-run must report combine intent")
        if "English technical terms" in long_dry_completed.stdout:
            failures.append("speak-long-server dry-run leaked source text")
        if "Mantenha ingles tecnico" in long_dry_completed.stdout:
            failures.append("speak-long-server dry-run leaked instruction text")
        if long_dry_payload.get("fallback_used") is not False:
            failures.append("speak-long-server dry-run fallback flag drifted")
        if long_dry_payload.get("provider_exclusive") is not True:
            failures.append("speak-long-server dry-run provider_exclusive flag drifted")
        for key in ("allows_install", "allows_download", "allows_global_config_write"):
            if long_dry_payload.get(key) is not False:
                failures.append(f"speak-long-server dry-run must keep {key}=false")

        received: dict[str, Any] = {}
        requests: list[dict[str, Any]] = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
                bodies = {
                    "/health": b'{"status":"ok"}',
                    "/v1/audio/voices": b'{"voices":[{"id":"default"},{"id":"tes-tts-local-clone"}]}',
                    "/v1/audio/models": b'{"data":[{"id":"omnivoice"}]}',
                    "/v1/voices": b'{"voices":[{"id":"legacy-default"}]}',
                    "/v1/models": b'{"data":[{"id":"legacy-omnivoice"}]}',
                }
                body = bodies.get(self.path)
                if body is None:
                    self.send_response(404)
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                received["path"] = self.path
                received["authorization"] = self.headers.get("Authorization")
                content_type = self.headers.get("Content-Type", "")
                if content_type.startswith("multipart/form-data"):
                    received["content_type"] = content_type
                    received["body"] = body
                    requests.append({"path": self.path, "content_type": content_type, "body": body})
                else:
                    received["body"] = json.loads(body.decode("utf-8"))
                    requests.append({"path": self.path, "body": received["body"]})
                audio = wav_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "audio/wav")
                self.send_header("Content-Length", str(len(audio)))
                self.end_headers()
                self.wfile.write(audio)

            def log_message(self, _format: str, *_args: object) -> None:
                return

        with socketserver.TCPServer(("127.0.0.1", 0), Handler) as server:
            port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            env = os.environ.copy()
            env["TES_TTS_FAKE_SERVER_KEY"] = "local-test-key"
            status_completed = subprocess.run(
                [
                    sys.executable,
                    str(PROVIDER_SCRIPT),
                    "server-status",
                    "--server-url",
                    f"http://127.0.0.1:{port}",
                    "--api-key-env",
                    "TES_TTS_FAKE_SERVER_KEY",
                    "--discover-capabilities",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                env=env,
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(PROVIDER_SCRIPT),
                    "speak-server",
                    "--server-url",
                    f"http://127.0.0.1:{port}",
                    "--api-key-env",
                    "TES_TTS_FAKE_SERVER_KEY",
                    "--model",
                    "omnivoice",
                    "--voice",
                    "tes-tts-local-clone",
                    "--language",
                    "pt",
                    "--speaker",
                    "tes-tts-local-clone",
                    "--instructions",
                    "Preserve JSON and TypeScript.",
                    "--task-type",
                    "CustomVoice",
                    "--max-new-tokens",
                    "2048",
                    "--guidance-scale",
                    "3.0",
                    "--denoise",
                    "--t-shift",
                    "0.1",
                    "--position-temperature",
                    "0.0",
                    "--class-temperature",
                    "0.0",
                    "--postprocess-output",
                    "--stream",
                    "--num-step",
                    "8",
                    "--text",
                    "Teste real do TES TTS com JSON e TypeScript.",
                    "--output",
                    str(output),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                env=env,
            )
            server.shutdown()
            thread.join(timeout=2)
        if status_completed.returncode != 0:
            failures.append(f"server-status mock server returned unexpected exit code {status_completed.returncode}")
            return failures
        try:
            status_payload = json.loads(status_completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"server-status mock server did not emit JSON: {exc}")
            return failures
        if status_payload.get("status") != "SERVER_AVAILABLE":
            failures.append("server-status mock server should report SERVER_AVAILABLE")
        connectivity = status_payload.get("connectivity")
        if not isinstance(connectivity, dict) or connectivity.get("port") != port:
            failures.append("server-status must report TCP connectivity details")
        health = status_payload.get("health")
        if not isinstance(health, dict) or health.get("status") != "HEALTH_OK":
            failures.append("server-status must report successful community health check")
        capabilities = status_payload.get("capabilities")
        if not isinstance(capabilities, dict) or capabilities.get("status") != "DISCOVERED":
            failures.append("server-status must discover mock capability endpoints")
        elif capabilities.get("available") != ["audio_models", "audio_voices", "models", "root_health", "voices"]:
            failures.append("server-status capability availability list drifted")
        else:
            if capabilities.get("voice_ids") != ["default", "legacy-default", "tes-tts-local-clone"]:
                failures.append("server-status must extract voice ids from common capability responses")
            if capabilities.get("model_ids") != ["legacy-omnivoice", "omnivoice"]:
                failures.append("server-status must extract model ids from common capability responses")
            if capabilities.get("preferred_voice_id") != "tes-tts-local-clone":
                failures.append("server-status preferred voice selection drifted")
            if capabilities.get("preferred_model_id") != "omnivoice":
                failures.append("server-status preferred model selection drifted")
            audio_voices = (capabilities.get("resources") or {}).get("audio_voices")
            if not isinstance(audio_voices, dict) or audio_voices.get("ids") != ["default", "tes-tts-local-clone"]:
                failures.append("server-status must expose redacted audio voice ids per resource")
        if status_payload.get("probe_scope") != "tcp_connect_plus_optional_health_no_synthesis":
            failures.append("server-status mock server probe scope drifted")
        if completed.returncode != 0:
            failures.append(f"speak-server mock request returned unexpected exit code {completed.returncode}")
            return failures
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"speak-server mock request did not emit JSON: {exc}")
            return failures
        if payload.get("status") != "PASS":
            failures.append("speak-server mock request should pass")
        if payload.get("mode") != "product_server_shortcut":
            failures.append("speak-server mock request mode drifted")
        if payload.get("bytes") != len(wav_bytes()):
            failures.append("speak-server mock request must report written bytes")
        if output.read_bytes() != wav_bytes():
            failures.append("speak-server did not write the response audio bytes")
        if received.get("path") != "/v1/audio/speech":
            failures.append("speak-server must POST to /v1/audio/speech")
        if received.get("authorization") != "Bearer local-test-key":
            failures.append("speak-server must use Bearer auth when env key is present")
        body = received.get("body")
        if not isinstance(body, dict):
            failures.append("speak-server mock did not receive JSON body")
        else:
            if body.get("model") != "omnivoice" or body.get("voice") != "tes-tts-local-clone":
                failures.append("speak-server request body lost model or voice")
            if body.get("input") != "Teste real do TES TTS com JSON e TypeScript.":
                failures.append("speak-server request body lost input text")
            if body.get("language") != "pt":
                failures.append("speak-server request body lost language")
            if body.get("speaker") != "tes-tts-local-clone":
                failures.append("speak-server request body lost speaker")
            if body.get("instructions") != "Preserve JSON and TypeScript.":
                failures.append("speak-server request body lost instructions")
            if body.get("task_type") != "CustomVoice":
                failures.append("speak-server request body lost task_type")
            if body.get("max_new_tokens") != 2048:
                failures.append("speak-server request body lost max_new_tokens")
            if body.get("guidance_scale") != 3.0:
                failures.append("speak-server request body lost guidance_scale")
            if body.get("denoise") is not True:
                failures.append("speak-server request body lost denoise")
            if body.get("t_shift") != 0.1:
                failures.append("speak-server request body lost t_shift")
            if body.get("position_temperature") != 0.0:
                failures.append("speak-server request body lost position_temperature")
            if body.get("class_temperature") != 0.0:
                failures.append("speak-server request body lost class_temperature")
            if body.get("postprocess_output") is not True:
                failures.append("speak-server request body lost postprocess_output")
            if body.get("stream") is not True:
                failures.append("speak-server request body lost stream intent")
            if body.get("num_step") != 8:
                failures.append("speak-server request body lost num_step")

        clone_ref = root / "clone-ref.wav"
        clone_ref.write_bytes(b"fake-reference-audio")
        clone_output = root / "server-clone.wav"
        requests.clear()
        received.clear()
        with socketserver.TCPServer(("127.0.0.1", 0), Handler) as server:
            port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            env = os.environ.copy()
            env["TES_TTS_FAKE_SERVER_KEY"] = "local-test-key"
            clone_completed = subprocess.run(
                [
                    sys.executable,
                    str(PROVIDER_SCRIPT),
                    "speak-server",
                    "--server-url",
                    f"http://127.0.0.1:{port}",
                    "--api-key-env",
                    "TES_TTS_FAKE_SERVER_KEY",
                    "--clone-ref-audio",
                    str(clone_ref),
                    "--clone-ref-text",
                    "Reference transcript must not appear in dry-run metadata.",
                    "--language",
                    "pt",
                    "--guidance-scale",
                    "3.0",
                    "--denoise",
                    "--duration",
                    "3.5",
                    "--layer-penalty-factor",
                    "1.0",
                    "--preprocess-prompt",
                    "--audio-chunk-duration",
                    "1.5",
                    "--audio-chunk-threshold",
                    "0.25",
                    "--request-timeout-s",
                    "120",
                    "--num-step",
                    "8",
                    "--text",
                    "Teste real com clone local e TypeScript.",
                    "--output",
                    str(clone_output),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                env=env,
            )
            server.shutdown()
            thread.join(timeout=2)
        if clone_completed.returncode != 0:
            failures.append(f"speak-server clone mock request returned unexpected exit code {clone_completed.returncode}")
            return failures
        try:
            clone_payload = json.loads(clone_completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"speak-server clone mock request did not emit JSON: {exc}")
            return failures
        if clone_payload.get("status") != "PASS":
            failures.append("speak-server clone mock request should pass")
        if clone_payload.get("server_mode") != "clone":
            failures.append("speak-server clone mock request must report clone mode")
        if clone_payload.get("endpoint") != f"http://127.0.0.1:{port}/v1/audio/speech/clone":
            failures.append("speak-server clone mock request must derive /v1/audio/speech/clone endpoint")
        if clone_payload.get("clone_ref_audio_present") is not True:
            failures.append("speak-server clone mock request must report reference audio presence")
        if clone_payload.get("clone_ref_text_present") is not True:
            failures.append("speak-server clone mock request must report reference text presence without emitting it")
        if clone_output.read_bytes() != wav_bytes():
            failures.append("speak-server clone mock request did not write response audio bytes")
        if received.get("path") != "/v1/audio/speech/clone":
            failures.append("speak-server clone mock request must POST to /v1/audio/speech/clone")
        if received.get("authorization") != "Bearer local-test-key":
            failures.append("speak-server clone mock request must use Bearer auth when env key is present")
        clone_body = received.get("body")
        clone_content_type = str(received.get("content_type", ""))
        if not clone_content_type.startswith("multipart/form-data"):
            failures.append("speak-server clone mock request must send multipart/form-data")
        if not isinstance(clone_body, bytes):
            failures.append("speak-server clone mock request did not preserve multipart body")
        else:
            for marker in (
                b'name="text"',
                b'name="ref_text"',
                b'name="ref_audio"',
                b'name="response_format"',
                b'name="language"',
                b'name="duration"',
                b'name="layer_penalty_factor"',
                b'name="preprocess_prompt"',
                b'name="audio_chunk_duration"',
                b'name="audio_chunk_threshold"',
                b'name="request_timeout_s"',
                b'Teste real com clone local e TypeScript.',
                b"Reference transcript must not appear in dry-run metadata.",
                b"fake-reference-audio",
                b"pt",
                b"3.5",
                b"true",
            ):
                if marker not in clone_body:
                    failures.append(f"speak-server clone mock request multipart body missing {marker!r}")

        long_output_dir = root / "server-long-real"
        requests.clear()
        with socketserver.TCPServer(("127.0.0.1", 0), Handler) as server:
            port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            completed = subprocess.run(
                [
                    sys.executable,
                    str(PROVIDER_SCRIPT),
                    "speak-long-server",
                    "--server-url",
                    f"http://127.0.0.1:{port}",
                    "--speaker",
                    "tes-tts-local-clone",
                    "--instructions",
                    "Keep English terms stable.",
                    "--task-type",
                    "CustomVoice",
                    "--max-new-tokens",
                    "2048",
                    "--guidance-scale",
                    "3.0",
                    "--denoise",
                    "--t-shift",
                    "0.1",
                    "--position-temperature",
                    "0.0",
                    "--class-temperature",
                    "0.0",
                    "--postprocess-output",
                    "--no-stream",
                    "--num-step",
                    "12",
                    "--text",
                    "Primeiro bloco com API.\n\nEnglish technical terms: JSON, TypeScript, and thresholds.",
                    "--chunk-chars",
                    "80",
                    "--output-dir",
                    str(long_output_dir),
                    "--combine",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            server.shutdown()
            thread.join(timeout=2)
        if completed.returncode != 0:
            failures.append(f"speak-long-server mock request returned unexpected exit code {completed.returncode}")
            return failures
        try:
            long_payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"speak-long-server mock request did not emit JSON: {exc}")
            return failures
        if long_payload.get("status") != "PASS":
            failures.append("speak-long-server mock request should pass")
        if long_payload.get("mode") != "product_server_long_read":
            failures.append("speak-long-server mock request mode drifted")
        if long_payload.get("completed_chunk_count", 0) < 2:
            failures.append("speak-long-server mock request should process multiple chunks")
        combined = long_payload.get("combined_audio")
        if not isinstance(combined, dict) or combined.get("combined_status") != "PASS":
            failures.append("speak-long-server mock request should write combined.wav")
        if not (long_output_dir / "result.json").exists():
            failures.append("speak-long-server must write result.json")
        if not (long_output_dir / "combined.wav").exists():
            failures.append("speak-long-server must write combined.wav when requested")
        outputs = long_payload.get("outputs")
        if not isinstance(outputs, list) or not outputs:
            failures.append("speak-long-server must report chunk outputs")
        elif any(item.get("audio_duration_seconds") is None for item in outputs):
            failures.append("speak-long-server must measure WAV duration when server returns WAV")
        if not requests:
            failures.append("speak-long-server mock did not send any chunk requests")
        else:
            for index, request in enumerate(requests, start=1):
                request_body = request.get("body")
                if not isinstance(request_body, dict):
                    failures.append(f"speak-long-server chunk {index} did not send JSON body")
                    continue
                if request_body.get("speaker") != "tes-tts-local-clone":
                    failures.append(f"speak-long-server chunk {index} lost speaker")
                if request_body.get("instructions") != "Keep English terms stable.":
                    failures.append(f"speak-long-server chunk {index} lost instructions")
                if request_body.get("task_type") != "CustomVoice":
                    failures.append(f"speak-long-server chunk {index} lost task_type")
                if request_body.get("max_new_tokens") != 2048:
                    failures.append(f"speak-long-server chunk {index} lost max_new_tokens")
                if request_body.get("guidance_scale") != 3.0:
                    failures.append(f"speak-long-server chunk {index} lost guidance_scale")
                if request_body.get("denoise") is not True:
                    failures.append(f"speak-long-server chunk {index} lost denoise")
                if request_body.get("t_shift") != 0.1:
                    failures.append(f"speak-long-server chunk {index} lost t_shift")
                if request_body.get("position_temperature") != 0.0:
                    failures.append(f"speak-long-server chunk {index} lost position_temperature")
                if request_body.get("class_temperature") != 0.0:
                    failures.append(f"speak-long-server chunk {index} lost class_temperature")
                if request_body.get("postprocess_output") is not True:
                    failures.append(f"speak-long-server chunk {index} lost postprocess_output")
                if request_body.get("language") not in {"pt", "en"}:
                    failures.append(f"speak-long-server chunk {index} lost per-chunk language")
                if request_body.get("stream") is not False:
                    failures.append(f"speak-long-server chunk {index} lost disabled stream intent")
                if request_body.get("num_step") != 12:
                    failures.append(f"speak-long-server chunk {index} lost num_step")
        for key in ("allows_install", "allows_download", "allows_global_config_write"):
            if payload.get(key) is not False:
                failures.append(f"speak-server mock request must keep {key}=false")
            if long_payload.get(key) is not False:
                failures.append(f"speak-long-server mock request must keep {key}=false")
    return failures


def validate_long_read_dry_run_payload(payload: dict[str, Any] | None) -> list[str]:
    if payload is None:
        return []
    failures: list[str] = []
    missing = sorted(REQUIRED_LONG_READ_DRY_RUN_KEYS - set(payload))
    extra = sorted(set(payload) - REQUIRED_LONG_READ_DRY_RUN_KEYS)
    if missing:
        failures.append(f"speak-long dry-run missing keys {missing}")
    if extra:
        failures.append(f"speak-long dry-run has extra keys {extra}")
    if payload.get("status") != "DRY_RUN":
        failures.append("speak-long dry-run status drifted")
    if payload.get("mode") != "product_long_read":
        failures.append("speak-long dry-run mode drifted")
    if payload.get("fallback_used") is not False:
        failures.append("speak-long must not use fallback")
    if payload.get("provider_exclusive") is not True:
        failures.append("speak-long must be OmniVoice-exclusive")
    if payload.get("resident_model") is not True or payload.get("resident_voice_prompt") is not True:
        failures.append("speak-long must use the resident runtime path")
    if payload.get("chunk_count", 0) < 2:
        failures.append("speak-long fixture should prove chunking")
    if payload.get("language_mode") != "auto":
        failures.append("speak-long dry-run must preserve auto language mode")
    if payload.get("chunk_languages") != ["pt", "en", "pt"]:
        failures.append("speak-long auto language fixture must route PT/EN/PT chunks")
    if payload.get("play_requested") is not True:
        failures.append("speak-long dry-run must report playback intent")
    if payload.get("chunk_edge_silence_ms") != 120:
        failures.append("speak-long dry-run must report chunk edge silence")
    monitor_log = payload.get("monitor_log")
    if not isinstance(monitor_log, str) or "runtime-logs" not in monitor_log:
        failures.append("speak-long dry-run must point to the exclusive runtime log")
    command_shape = payload.get("command_shape")
    if not isinstance(command_shape, list):
        failures.append("speak-long dry-run command_shape must be a list")
    else:
        joined = " ".join(str(part) for part in command_shape)
        if "Primeiro bloco" in joined or "Segundo bloco" in joined:
            failures.append("speak-long dry-run leaked source text in command_shape")
    return failures


def validate_bench_dry_run_payload(payload: dict[str, Any] | None) -> list[str]:
    if payload is None:
        return []
    failures: list[str] = []
    missing = sorted(REQUIRED_BENCH_DRY_RUN_KEYS - set(payload))
    extra = sorted(set(payload) - REQUIRED_BENCH_DRY_RUN_KEYS)
    if missing:
        failures.append(f"bench dry-run missing keys {missing}")
    if extra:
        failures.append(f"bench dry-run has extra keys {extra}")
    if payload.get("status") != "DRY_RUN":
        failures.append("bench dry-run status drifted")
    if payload.get("mode") != "product_benchmark":
        failures.append("bench dry-run mode drifted")
    if payload.get("allows_install") is not False:
        failures.append("bench dry-run must not install providers")
    if payload.get("allows_download") is not False:
        failures.append("bench dry-run must not download models")
    if payload.get("allows_global_config_write") is not False:
        failures.append("bench dry-run must not write global config")
    if payload.get("play_requested") is not True:
        failures.append("bench dry-run must report playback intent")
    if payload.get("open_requested") is not True:
        failures.append("bench dry-run must report review-open intent")
    if payload.get("package_requested") is not True:
        failures.append("bench dry-run must report review-package intent")
    command_shape = payload.get("command_shape")
    if not isinstance(command_shape, list):
        failures.append("bench dry-run command_shape must be a list")
    else:
        joined = " ".join(str(part) for part in command_shape)
        if "batch" not in command_shape:
            failures.append("bench dry-run must delegate to batch")
        if "abc123SECRET" in joined or "API_KEY=" in joined or "SECRET_REF_TEXT" in joined:
            failures.append("bench dry-run leaked fixture or reference secret in command_shape")
        if "--ref-text" in command_shape and "<redacted>" not in command_shape:
            failures.append("bench dry-run must redact reference text")
    cases = payload.get("cases")
    if not isinstance(cases, str) or not cases.endswith("omnivoice-provider-cases.json"):
        failures.append("bench dry-run must default to OmniVoice provider cases")
    result_json = payload.get("result_json")
    review_html = payload.get("review_html")
    if not isinstance(result_json, str) or not result_json.endswith("result.json"):
        failures.append("bench dry-run must report result JSON path")
    if not isinstance(review_html, str) or not review_html.endswith("review.html"):
        failures.append("bench dry-run must report review HTML path")
    package_zip = payload.get("package_zip")
    if not isinstance(package_zip, str) or not package_zip.endswith("tes-tts-omnivoice-review-package.zip"):
        failures.append("bench dry-run must report review package path")
    return failures


def validate_profile_review_dry_run_payload(payload: dict[str, Any] | None) -> list[str]:
    if payload is None:
        return []
    failures: list[str] = []
    missing = sorted(REQUIRED_PROFILE_REVIEW_DRY_RUN_KEYS - set(payload))
    extra = sorted(set(payload) - REQUIRED_PROFILE_REVIEW_DRY_RUN_KEYS)
    if missing:
        failures.append(f"profile-review dry-run missing keys {missing}")
    if extra:
        failures.append(f"profile-review dry-run has extra keys {extra}")
    if payload.get("status") != "DRY_RUN":
        failures.append("profile-review dry-run status drifted")
    if payload.get("mode") != "product_profile_review":
        failures.append("profile-review dry-run mode drifted")
    if payload.get("profiles") != ["fast", "quality"]:
        failures.append("profile-review dry-run must default to fast vs quality")
    if payload.get("allows_install") is not False:
        failures.append("profile-review dry-run must not install providers")
    if payload.get("allows_download") is not False:
        failures.append("profile-review dry-run must not download models")
    if payload.get("allows_global_config_write") is not False:
        failures.append("profile-review dry-run must not write global config")
    if payload.get("play_requested") is not True:
        failures.append("profile-review dry-run must report playback intent")
    if payload.get("open_requested") is not True:
        failures.append("profile-review dry-run must report review-open intent")
    if payload.get("package_requested") is not True:
        failures.append("profile-review dry-run must report review-package intent")
    command_shapes = payload.get("command_shapes")
    if not isinstance(command_shapes, list) or len(command_shapes) != 2:
        failures.append("profile-review dry-run must emit two command shapes")
    else:
        joined = " ".join(str(part) for command in command_shapes for part in command)
        if "batch" not in joined:
            failures.append("profile-review dry-run must delegate to batch")
        if "--latency-profile fast" not in joined or "--latency-profile quality" not in joined:
            failures.append("profile-review dry-run must carry fast and quality profiles")
        if "--num-step 8" not in joined or "--num-step 32" not in joined:
            failures.append("profile-review dry-run must resolve fast and quality steps")
        if "SECRET_REF_TEXT" in joined:
            failures.append("profile-review dry-run leaked reference text")
        if "--ref-text" in joined and "<redacted>" not in joined:
            failures.append("profile-review dry-run must redact reference text")
    cases = payload.get("cases")
    if not isinstance(cases, str) or not cases.endswith("omnivoice-provider-cases.json"):
        failures.append("profile-review dry-run must default to OmniVoice provider cases")
    for key, suffix in (
        ("result_json", "result.json"),
        ("review_html", "review.html"),
        ("package_zip", "tes-tts-omnivoice-review-package.zip"),
    ):
        value = payload.get(key)
        if not isinstance(value, str) or not value.endswith(suffix):
            failures.append(f"profile-review dry-run must report {key}")
    return failures


def validate_warm_cache_dry_run_command() -> list[str]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        ref = root / "ref.wav"
        cache_dir = root / "cache"
        ref.write_bytes(b"not-real-audio-for-dry-run")
        completed = subprocess.run(
            [
                sys.executable,
                str(PROVIDER_SCRIPT),
                "warm-cache",
                "--python",
                sys.executable,
                "--ref-audio",
                str(ref),
                "--cache-dir",
                str(cache_dir),
                "--ref-text",
                "SECRET_REF_TEXT",
                "--refresh-prompt",
                "--dry-run",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    if completed.returncode != 0:
        failures.append(f"warm-cache dry-run returned unexpected exit code {completed.returncode}")
        return failures
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        failures.append(f"warm-cache dry-run did not emit JSON: {exc}")
        return failures
    missing = sorted(REQUIRED_WARM_CACHE_DRY_RUN_KEYS - set(payload))
    extra = sorted(set(payload) - REQUIRED_WARM_CACHE_DRY_RUN_KEYS)
    if missing:
        failures.append(f"warm-cache dry-run missing keys {missing}")
    if extra:
        failures.append(f"warm-cache dry-run has extra keys {extra}")
    if payload.get("status") != "DRY_RUN":
        failures.append("warm-cache dry-run status drifted")
    if payload.get("mode") != "product_warm_cache":
        failures.append("warm-cache dry-run mode drifted")
    if payload.get("refresh_requested") is not True:
        failures.append("warm-cache dry-run must report refresh intent")
    if payload.get("voice_prompt_cache_exists") is not False:
        failures.append("warm-cache dry-run should not create the cache")
    cache_path = payload.get("voice_prompt_cache_path")
    if not isinstance(cache_path, str) or not cache_path.endswith(".pt"):
        failures.append("warm-cache dry-run must report a .pt prompt cache path")
    command_shape = payload.get("command_shape")
    if not isinstance(command_shape, list):
        failures.append("warm-cache dry-run command_shape must be a list")
    else:
        joined = " ".join(str(part) for part in command_shape)
        if "prepare-prompt" not in command_shape:
            failures.append("warm-cache dry-run must delegate to prepare-prompt")
        if "SECRET_REF_TEXT" in joined:
            failures.append("warm-cache dry-run leaked reference text")
        if "--ref-text" in command_shape and "<redacted>" not in command_shape:
            failures.append("warm-cache dry-run must redact reference text")
    for key in ("allows_install", "allows_download", "allows_global_config_write"):
        if payload.get(key) is not False:
            failures.append(f"warm-cache dry-run must keep {key}=false")
    return failures


def validate_session_dry_run_command() -> list[str]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        ref = root / "ref.wav"
        output_dir = root / "session-audio"
        ref.write_bytes(b"not-real-audio-for-dry-run")
        completed = subprocess.run(
            [
                sys.executable,
                str(PROVIDER_SCRIPT),
                "session",
                "--python",
                sys.executable,
                "--ref-audio",
                str(ref),
                "--output-dir",
                str(output_dir),
                "--latency-profile",
                "fast",
                "--ref-text",
                "SECRET_REF_TEXT",
                "--dry-run",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    if completed.returncode != 0:
        failures.append(f"session dry-run returned unexpected exit code {completed.returncode}")
        return failures
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        failures.append(f"session dry-run did not emit JSON: {exc}")
        return failures
    missing = sorted(REQUIRED_SESSION_DRY_RUN_KEYS - set(payload))
    extra = sorted(set(payload) - REQUIRED_SESSION_DRY_RUN_KEYS)
    if missing:
        failures.append(f"session dry-run missing keys {missing}")
    if extra:
        failures.append(f"session dry-run has extra keys {extra}")
    if payload.get("status") != "DRY_RUN":
        failures.append("session dry-run status drifted")
    if payload.get("mode") != "product_session":
        failures.append("session dry-run mode drifted")
    if payload.get("protocol") != "jsonl_stdin_stdout":
        failures.append("session dry-run must report JSONL stdin/stdout protocol")
    if payload.get("resident_model") is not True:
        failures.append("session dry-run must report resident model reuse")
    if payload.get("resident_voice_prompt") is not True:
        failures.append("session dry-run must report resident voice prompt reuse")
    if payload.get("latency_profile") != "fast":
        failures.append("session dry-run must preserve requested latency profile")
    if payload.get("num_step") != 8:
        failures.append("session fast latency profile must resolve to num_step=8")
    profiles = payload.get("latency_profiles")
    if not isinstance(profiles, dict) or sorted(profiles) != ["balanced", "fast", "quality"]:
        failures.append("session dry-run must report supported latency profiles")
    command_shape = payload.get("command_shape")
    if not isinstance(command_shape, list):
        failures.append("session dry-run command_shape must be a list")
    else:
        joined = " ".join(str(part) for part in command_shape)
        if "serve" not in command_shape:
            failures.append("session dry-run must delegate to serve")
        if "--latency-profile" not in command_shape or "fast" not in command_shape:
            failures.append("session dry-run command must carry requested latency profile")
        if "--num-step" not in command_shape or "8" not in command_shape:
            failures.append("session dry-run command must carry resolved fast num-step")
        if "SECRET_REF_TEXT" in joined:
            failures.append("session dry-run leaked reference text")
        if "--ref-text" in command_shape and "<redacted>" not in command_shape:
            failures.append("session dry-run must redact reference text")
    if output_dir.exists():
        failures.append("session dry-run should not create output directory")
    for key in ("allows_install", "allows_download", "allows_global_config_write"):
        if payload.get(key) is not False:
            failures.append(f"session dry-run must keep {key}=false")
    return failures


def validate_auto_latency_profile_selection() -> list[str]:
    failures: list[str] = []
    provider = load_provider_module()
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        benchmark = root / "sealed-profile"
        benchmark.mkdir()
        ref = root / "ref.wav"
        review = benchmark / "review.html"
        decision = benchmark / "review-decision.json"
        ref.write_bytes(b"not-real-audio-for-dry-run")
        review.write_text("<!doctype html>", encoding="utf-8")
        decision.write_text(
            json.dumps(
                {
                    "schema": "tes-tts-omnivoice-review-decision@1",
                    "review_kind": "profile_review",
                    "decision": "AUDIO_CANDIDATE",
                    "recommended_latency_profile": "fast",
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        profile, source = provider.resolve_auto_latency_profile(str(root))
        if profile != "fast":
            failures.append("auto latency profile must use sealed AUDIO_CANDIDATE recommendation")
        if not source.startswith("auto_sealed_candidate"):
            failures.append("auto latency profile must explain sealed candidate source")

        env = os.environ.copy()
        env["TES_TTS_OMNIVOICE_PYTHON"] = sys.executable
        env["TES_TTS_OMNIVOICE_REF_AUDIO"] = str(ref)
        env["TES_TTS_OMNIVOICE_BENCHMARK_DIR"] = str(root)
        completed = subprocess.run(
            [
                sys.executable,
                str(PROVIDER_SCRIPT),
                "speak",
                "--text",
                "Teste ADR e API em modo automatico.",
                "--dry-run",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=env,
        )
    if completed.returncode != 0:
        failures.append(f"auto profile speak dry-run returned unexpected exit code {completed.returncode}")
        return failures
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        failures.append(f"auto profile speak dry-run did not emit JSON: {exc}")
        return failures
    if payload.get("requested_latency_profile") != "auto":
        failures.append("auto profile dry-run must preserve requested profile")
    if payload.get("latency_profile") != "fast":
        failures.append("auto profile dry-run must resolve to recommended fast profile")
    if payload.get("num_step") != 8:
        failures.append("auto profile dry-run must resolve fast profile to 8 steps")
    if not str(payload.get("latency_profile_source")).startswith("auto_sealed_candidate"):
        failures.append("auto profile dry-run must report sealed candidate source")
    command_shape = payload.get("command_shape")
    if not isinstance(command_shape, list):
        failures.append("auto profile dry-run command_shape must be a list")
    else:
        joined = " ".join(str(part) for part in command_shape)
        if "--latency-profile fast" not in joined or "--num-step 8" not in joined:
            failures.append("auto profile dry-run command must carry resolved fast profile")
    return failures


def validate_live_smoke_dry_run_command() -> list[str]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        ref = root / "ref.wav"
        output_dir = root / "live-smoke"
        ref.write_bytes(b"not-real-audio-for-dry-run")
        completed = subprocess.run(
            [
                sys.executable,
                str(PROVIDER_SCRIPT),
                "live-smoke",
                "--python",
                sys.executable,
                "--ref-audio",
                str(ref),
                "--output-dir",
                str(output_dir),
                "--limit",
                "2",
                "--latency-profile",
                "fast",
                "--ref-text",
                "SECRET_REF_TEXT",
                "--play",
                "--package",
                "--dry-run",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    if completed.returncode != 0:
        failures.append(f"live-smoke dry-run returned unexpected exit code {completed.returncode}")
        return failures
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        failures.append(f"live-smoke dry-run did not emit JSON: {exc}")
        return failures
    missing = sorted(REQUIRED_LIVE_SMOKE_DRY_RUN_KEYS - set(payload))
    extra = sorted(set(payload) - REQUIRED_LIVE_SMOKE_DRY_RUN_KEYS)
    if missing:
        failures.append(f"live-smoke dry-run missing keys {missing}")
    if extra:
        failures.append(f"live-smoke dry-run has extra keys {extra}")
    if payload.get("status") != "DRY_RUN":
        failures.append("live-smoke dry-run status drifted")
    if payload.get("mode") != "product_live_smoke":
        failures.append("live-smoke dry-run mode drifted")
    if payload.get("case_count") != 2:
        failures.append("live-smoke dry-run must honor --limit")
    case_ids = payload.get("case_ids")
    if not isinstance(case_ids, list) or len(case_ids) != 2:
        failures.append("live-smoke dry-run must report selected case ids")
    if payload.get("play_requested") is not True:
        failures.append("live-smoke dry-run must report playback intent")
    if payload.get("package_requested") is not True:
        failures.append("live-smoke dry-run must report package intent")
    if payload.get("latency_profile") != "fast" or payload.get("num_step") != 8:
        failures.append("live-smoke dry-run must resolve fast profile")
    if payload.get("requested_latency_profile") != "fast":
        failures.append("live-smoke dry-run must preserve requested profile")
    if payload.get("protocol") != "jsonl_stdin_stdout":
        failures.append("live-smoke dry-run must use resident JSONL protocol")
    if payload.get("resident_model") is not True or payload.get("resident_voice_prompt") is not True:
        failures.append("live-smoke dry-run must report resident reuse")
    command_shape = payload.get("command_shape")
    if not isinstance(command_shape, list):
        failures.append("live-smoke dry-run command_shape must be a list")
    else:
        joined = " ".join(str(part) for part in command_shape)
        if "serve" not in command_shape:
            failures.append("live-smoke dry-run must delegate to serve")
        if "--latency-profile fast" not in joined or "--num-step 8" not in joined:
            failures.append("live-smoke dry-run command must carry resolved fast profile")
        if "SECRET_REF_TEXT" in joined:
            failures.append("live-smoke dry-run leaked reference text")
        if "--ref-text" in command_shape and "<redacted>" not in command_shape:
            failures.append("live-smoke dry-run must redact reference text")
    for key in ("result_json", "review_html", "package_zip"):
        value = payload.get(key)
        if not isinstance(value, str) or not value.startswith(str(output_dir)):
            failures.append(f"live-smoke dry-run must report output-local {key}")
    if output_dir.exists():
        failures.append("live-smoke dry-run should not create output directory")
    for key in ("allows_install", "allows_download", "allows_global_config_write"):
        if payload.get(key) is not False:
            failures.append(f"live-smoke dry-run must keep {key}=false")
    return failures


def validate_review_dry_run_payload(payload: dict[str, Any] | None) -> list[str]:
    if payload is None:
        return []
    failures: list[str] = []
    missing = sorted(REQUIRED_REVIEW_DRY_RUN_KEYS - set(payload))
    extra = sorted(set(payload) - REQUIRED_REVIEW_DRY_RUN_KEYS)
    if missing:
        failures.append(f"review dry-run missing keys {missing}")
    if extra:
        failures.append(f"review dry-run has extra keys {extra}")
    if payload.get("status") != "DRY_RUN":
        failures.append("review dry-run status drifted")
    if payload.get("mode") != "product_review":
        failures.append("review dry-run mode drifted")
    if payload.get("open_requested") is not False:
        failures.append("review dry-run must not open the browser")
    if payload.get("exists") is not True:
        failures.append("review dry-run must resolve an existing review")
    if payload.get("allows_install") is not False:
        failures.append("review dry-run must not install providers")
    if payload.get("allows_download") is not False:
        failures.append("review dry-run must not download models")
    if payload.get("allows_global_config_write") is not False:
        failures.append("review dry-run must not write global config")
    review_html = payload.get("review_html")
    if not isinstance(review_html, str) or not review_html.endswith("review.html"):
        failures.append("review dry-run must report review HTML path")
    return failures


def validate_package_dry_run_payload(payload: dict[str, Any] | None) -> list[str]:
    if payload is None:
        return []
    failures: list[str] = []
    missing = sorted(REQUIRED_PACKAGE_DRY_RUN_KEYS - set(payload))
    extra = sorted(set(payload) - REQUIRED_PACKAGE_DRY_RUN_KEYS)
    if missing:
        failures.append(f"package-review dry-run missing keys {missing}")
    if extra:
        failures.append(f"package-review dry-run has extra keys {extra}")
    if payload.get("status") != "DRY_RUN":
        failures.append("package-review dry-run status drifted")
    if payload.get("mode") != "product_review_package":
        failures.append("package-review dry-run mode drifted")
    if payload.get("manifest_schema") != "tes-tts-omnivoice-review-package@1":
        failures.append("package-review manifest schema drifted")
    if payload.get("file_count") != 3:
        failures.append("package-review dry-run should include review, result, and audio fixture")
    included = payload.get("included_files")
    if not isinstance(included, list):
        failures.append("package-review included_files must be a list")
    else:
        for required in ("review.html", "result.json", "case.wav"):
            if required not in included:
                failures.append(f"package-review missing included file {required}")
    if payload.get("allows_install") is not False:
        failures.append("package-review must not install providers")
    if payload.get("allows_download") is not False:
        failures.append("package-review must not download models")
    if payload.get("allows_global_config_write") is not False:
        failures.append("package-review must not write global config")
    return failures


def load_provider_module() -> Any:
    scripts_dir = ROOT / "scripts"
    sys.path.insert(0, str(scripts_dir))
    try:
        spec = importlib.util.spec_from_file_location("tes_tts_omnivoice_provider_for_oracle", PROVIDER_SCRIPT)
        if spec is None or spec.loader is None:
            raise RuntimeError("could not load provider module spec")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        try:
            sys.path.remove(str(scripts_dir))
        except ValueError:
            pass


def validate_jsonl_emitter() -> list[str]:
    failures: list[str] = []
    provider = load_provider_module()
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        provider.emit_jsonl({"status": "READY", "nested": {"ok": True}})
    output = buffer.getvalue()
    lines = output.splitlines()
    if len(lines) != 1:
        failures.append("emit_jsonl must emit exactly one line per payload")
        return failures
    try:
        payload = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        failures.append(f"emit_jsonl did not emit parseable compact JSON: {exc}")
        return failures
    if payload.get("status") != "READY":
        failures.append("emit_jsonl payload drifted")
    if "  " in lines[0]:
        failures.append("emit_jsonl must not pretty-print resident session payloads")
    return failures


def validate_short_speak_in_process_boundary() -> list[str]:
    failures: list[str] = []
    provider = load_provider_module()
    if provider.can_run_speak_in_process(sys.executable) is not True:
        failures.append("short speak must detect current interpreter as in-process capable")
    fake_python = str(ROOT / "tmp" / "missing-python-for-oracle")
    if provider.can_run_speak_in_process(fake_python) is not False:
        failures.append("short speak must not treat a different provider python as in-process capable")
    return failures


def validate_review_html_scorecard() -> list[str]:
    failures: list[str] = []
    provider = load_provider_module()
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        cases = root / "cases.json"
        cases.write_text(
            json.dumps(
                {
                    "cases": [
                        {
                            "id": "scorecard-case",
                            "language": "pt",
                            "source_text": "Leia API_KEY=abc123SECRET com segurança e avalie TypeScript.",
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        payload = {
            "provider": "omnivoice",
            "status": "PASS",
            "version": VERSION,
            "outputs": [
                {
                    "id": "scorecard-case",
                    "output": str(root / "scorecard-case.wav"),
                    "rtf": 0.9,
                    "audio_duration_seconds": 3.2,
                    "generation_ms": 2880,
                    "redaction_count": 1,
                }
            ],
            "benchmark_summary": {
                "case_count": 1,
                "avg_rtf": 0.9,
                "total_audio_duration_seconds": 3.2,
                "total_generation_ms": 2880,
                "provider_timing_scope": "local_optional_environment_only",
            },
        }
        paths = provider.write_benchmark_review(payload=payload, cases_path=cases, output_dir=root, locale="pt-BR")
        html_text = Path(paths["review_html"]).read_text(encoding="utf-8")
    required_snippets = [
        "tes-tts-omnivoice-review@1",
        "data-score=\"overall\"",
        "data-score=\"pronunciation\"",
        "data-score=\"technical_terms\"",
        "data-score=\"naturalness\"",
        "Exportar JSON",
        "Copiar resumo",
        "if(v==='')return null",
        "AUDIO_CANDIDATE",
        "NEEDS_TARGETED_FIX",
        "NEEDS_FIX",
        "API_KEY=[REDACTED_SECRET]",
        "TypeScript",
    ]
    for snippet in required_snippets:
        if snippet not in html_text:
            failures.append(f"review HTML missing scorecard snippet: {snippet}")
    if "abc123SECRET" in html_text:
        failures.append("review HTML leaked secret-like fixture text")
    return failures


def validate_profile_review_html_scorecard() -> list[str]:
    failures: list[str] = []
    provider = load_provider_module()
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        cases = root / "cases.json"
        cases.write_text(
            json.dumps(
                {
                    "cases": [
                        {
                            "id": "profile-case",
                            "language": "pt",
                            "text": "Compare API_KEY=abc123SECRET, TypeScript e provider.",
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        payload = {
            "provider": "omnivoice",
            "status": "PASS",
            "version": VERSION,
            "profiles": ["fast", "quality"],
            "outputs": [
                {
                    "id": "profile-case",
                    "output": str(root / "fast" / "profile-case.wav"),
                    "rtf": 0.2,
                    "audio_duration_seconds": 3.2,
                    "generation_ms": 640,
                    "num_step": 8,
                    "latency_profile": "fast",
                },
                {
                    "id": "profile-case",
                    "output": str(root / "quality" / "profile-case.wav"),
                    "rtf": 0.8,
                    "audio_duration_seconds": 3.2,
                    "generation_ms": 2560,
                    "num_step": 32,
                    "latency_profile": "quality",
                },
            ],
            "benchmark_summary": {
                "case_count": 1,
                "output_count": 2,
                "total_generation_ms": 3200,
                "provider_timing_scope": "local_optional_environment_only",
            },
        }
        paths = provider.write_profile_review(payload=payload, cases_path=cases, output_dir=root, locale="pt-BR")
        html_text = Path(paths["review_html"]).read_text(encoding="utf-8")
    required_snippets = [
        "tes-tts-omnivoice-profile-review@1",
        "data-profile=\"fast\"",
        "data-profile=\"quality\"",
        "data-score=\"score\"",
        "Exportar JSON",
        "Copiar resumo",
        "cases=comparisons.map",
        "AUDIO_CANDIDATE",
        "NEEDS_TARGETED_FIX",
        "NEEDS_FIX",
        "API_KEY=[REDACTED_SECRET]",
    ]
    for snippet in required_snippets:
        if snippet not in html_text:
            failures.append(f"profile review HTML missing snippet: {snippet}")
    if "abc123SECRET" in html_text:
        failures.append("profile review HTML leaked secret-like fixture text")
    return failures


def validate_review_package_zip() -> list[str]:
    failures: list[str] = []
    provider = load_provider_module()
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        review = root / "review.html"
        result = root / "result.json"
        wav = root / "case.wav"
        review.write_text("<!doctype html><audio controls src=\"case.wav\"></audio>", encoding="utf-8")
        wav.write_bytes(b"fake-wave")
        result.write_text(
            json.dumps({"outputs": [{"id": "case", "output": str(wav)}]}, ensure_ascii=False),
            encoding="utf-8",
        )
        args = argparse.Namespace(path=str(review), benchmark_dir=None, output=None, dry_run=False)
        with contextlib.redirect_stdout(io.StringIO()):
            if provider.command_package_review(args) != 0:
                failures.append("package-review command failed for local fixture")
        package_zip = root / "tes-tts-omnivoice-review-package.zip"
        if not package_zip.exists():
            failures.append("package-review did not write expected zip")
            return failures
        import zipfile

        with zipfile.ZipFile(package_zip) as archive:
            names = set(archive.namelist())
            for required in {"review.html", "result.json", "case.wav", "review-package-manifest.json"}:
                if required not in names:
                    failures.append(f"package zip missing {required}")
            manifest = json.loads(archive.read("review-package-manifest.json").decode("utf-8"))
        if manifest.get("schema") != "tes-tts-omnivoice-review-package@1":
            failures.append("package zip manifest schema drifted")
        if manifest.get("allows_install") is not False:
            failures.append("package manifest must not install providers")
        if manifest.get("allows_download") is not False:
            failures.append("package manifest must not download models")
        if manifest.get("allows_global_config_write") is not False:
            failures.append("package manifest must not write global config")
    return failures


def validate_review_decision_command() -> list[str]:
    failures: list[str] = []
    provider = load_provider_module()
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        review = root / "review.html"
        result = root / "result.json"
        wav = root / "case.wav"
        review_json = root / "exported-review.json"
        review.write_text("<!doctype html><audio controls src=\"case.wav\"></audio>", encoding="utf-8")
        wav.write_bytes(b"fake-wave")
        result.write_text(
            json.dumps({"outputs": [{"id": "case", "output": str(wav)}]}, ensure_ascii=False),
            encoding="utf-8",
        )
        review_json.write_text(
            json.dumps(
                {
                    "schema": "tes-tts-omnivoice-review@1",
                    "cases": [
                        {
                            "id": "case",
                            "scores": {
                                "overall": 9,
                                "pronunciation": 8.5,
                                "technical_terms": 8,
                                "naturalness": 9,
                                "notes": "candidate",
                            },
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        args = argparse.Namespace(
            path=str(review),
            benchmark_dir=None,
            review_json=str(review_json),
            output=None,
            package=True,
            dry_run=False,
        )
        with contextlib.redirect_stdout(io.StringIO()):
            if provider.command_decide_review(args) != 0:
                failures.append("decide-review command failed for local fixture")
        decision_path = root / "review-decision.json"
        if not decision_path.exists():
            failures.append("decide-review did not write review-decision.json")
            return failures
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        if decision.get("schema") != "tes-tts-omnivoice-review-decision@1":
            failures.append("review decision schema drifted")
        if decision.get("decision") != "AUDIO_CANDIDATE":
            failures.append("review decision should classify strong scores as AUDIO_CANDIDATE")
        if decision.get("allows_install") is not False:
            failures.append("review decision must not install providers")
        if decision.get("allows_download") is not False:
            failures.append("review decision must not download models")
        if decision.get("allows_global_config_write") is not False:
            failures.append("review decision must not write global config")
        package_zip = root / "tes-tts-omnivoice-review-package.zip"
        if not package_zip.exists():
            failures.append("decide-review --package did not write package zip")
            return failures
        import zipfile

        with zipfile.ZipFile(package_zip) as archive:
            names = set(archive.namelist())
            if "review-decision.json" not in names:
                failures.append("decision package missing review-decision.json")
            manifest = json.loads(archive.read("review-package-manifest.json").decode("utf-8"))
        manifest_paths = {item.get("path") for item in manifest.get("files", []) if isinstance(item, dict)}
        if "review-decision.json" not in manifest_paths:
            failures.append("package manifest missing review-decision.json")
    return failures


def validate_live_smoke_review_decision_command() -> list[str]:
    failures: list[str] = []
    provider = load_provider_module()
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        cases = root / "cases.json"
        wav = root / "live-case.wav"
        review_json = root / "exported-live-review.json"
        wav.write_bytes(b"fake-wave")
        cases.write_text(
            json.dumps(
                {
                    "cases": [
                        {
                            "id": "live-case",
                            "source_text": "Teste live-smoke com API_KEY=abc123SECRET e TypeScript.",
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        payload = {
            "provider": "omnivoice",
            "status": "PASS",
            "version": VERSION,
            "mode": "product_live_smoke",
            "outputs": [
                {
                    "id": "live-case",
                    "output": str(wav),
                    "rtf": 0.4,
                    "audio_duration_seconds": 3.0,
                    "generation_ms": 1200,
                    "redaction_count": 1,
                }
            ],
            "summary": {
                "request_count": 1,
                "avg_rtf": 0.4,
                "total_audio_duration_seconds": 3.0,
                "total_generation_ms": 1200,
                "provider_timing_scope": "resident_local_optional_environment_only",
            },
            "benchmark_summary": {
                "case_count": 1,
                "avg_rtf": 0.4,
                "total_audio_duration_seconds": 3.0,
                "total_generation_ms": 1200,
                "provider_timing_scope": "resident_local_optional_environment_only",
            },
        }
        provider.write_benchmark_review(payload=payload, cases_path=cases, output_dir=root, locale="pt-BR")
        review_json.write_text(
            json.dumps(
                {
                    "schema": "tes-tts-omnivoice-review@1",
                    "cases": [
                        {
                            "id": "live-case",
                            "scores": {
                                "overall": 9,
                                "pronunciation": 8,
                                "technical_terms": 8,
                                "naturalness": 8.5,
                                "notes": "resident smoke candidate",
                            },
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        args = argparse.Namespace(
            path=str(root / "review.html"),
            benchmark_dir=None,
            review_json=str(review_json),
            output=None,
            package=True,
            dry_run=False,
        )
        with contextlib.redirect_stdout(io.StringIO()):
            if provider.command_decide_review(args) != 0:
                failures.append("decide-review failed for live-smoke review")
        decision_path = root / "review-decision.json"
        if not decision_path.exists():
            failures.append("live-smoke decide-review did not write review-decision.json")
            return failures
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        if decision.get("review_kind") != "live_smoke_review":
            failures.append("live-smoke decision must report review_kind=live_smoke_review")
        if decision.get("decision") != "AUDIO_CANDIDATE":
            failures.append("live-smoke decision should classify strong scores as AUDIO_CANDIDATE")
        package_zip = root / "tes-tts-omnivoice-live-smoke-package.zip"
        if not package_zip.exists():
            failures.append("live-smoke decide-review --package did not update live-smoke package")
            return failures
        import zipfile

        with zipfile.ZipFile(package_zip) as archive:
            names = set(archive.namelist())
            for required in {
                "live-case.wav",
                "result.json",
                "review.html",
                "review-decision.json",
                "live-smoke-package-manifest.json",
            }:
                if required not in names:
                    failures.append(f"live-smoke decision package missing {required}")
            manifest = json.loads(archive.read("live-smoke-package-manifest.json").decode("utf-8"))
        if manifest.get("schema") != "tes-tts-omnivoice-live-smoke-package@1":
            failures.append("live-smoke decision package manifest schema drifted")
        manifest_paths = {item.get("path") for item in manifest.get("files", []) if isinstance(item, dict)}
        if "review-decision.json" not in manifest_paths:
            failures.append("live-smoke package manifest missing review-decision.json")
    return failures


def validate_profile_review_decision_command() -> list[str]:
    failures: list[str] = []
    provider = load_provider_module()
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        review = root / "review.html"
        result = root / "result.json"
        review_json = root / "exported-profile-review.json"
        fast = root / "fast" / "case.wav"
        quality = root / "quality" / "case.wav"
        fast.parent.mkdir()
        quality.parent.mkdir()
        fast.write_bytes(b"fake-fast-wave")
        quality.write_bytes(b"fake-quality-wave")
        review.write_text("<!doctype html><audio controls src=\"fast/case.wav\"></audio>", encoding="utf-8")
        result.write_text(
            json.dumps(
                {
                    "mode": "product_profile_review",
                    "outputs": [
                        {"id": "case", "latency_profile": "fast", "output": str(fast)},
                        {"id": "case", "latency_profile": "quality", "output": str(quality)},
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        review_json.write_text(
            json.dumps(
                {
                    "schema": "tes-tts-omnivoice-profile-review@1",
                    "cases": [
                        {"id": "case/fast", "scores": {"score": 8, "notes": "fast ok"}},
                        {"id": "case/quality", "scores": {"score": 9, "notes": "quality ok"}},
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        decision = provider.build_review_decision(review, review_json)
    if decision.get("decision") != "AUDIO_CANDIDATE":
        failures.append("profile review decision should support score-only profile exports")
    if decision.get("review_kind") != "profile_review":
        failures.append("profile review decision must identify review kind")
    if decision.get("recommended_latency_profile") != "fast":
        failures.append("profile review decision should recommend the fastest passing profile")
    recommendation = decision.get("profile_recommendation")
    if not isinstance(recommendation, dict) or recommendation.get("reason") != "fastest_profile_meeting_audio_candidate_threshold":
        failures.append("profile review decision must explain profile recommendation")
    if decision.get("case_count") != 2 or decision.get("scored_case_count") != 2:
        failures.append("profile review decision should score both profile outputs")
    score_ids = {case.get("score_id") for case in decision.get("cases", [])}
    if score_ids != {"case/fast", "case/quality"}:
        failures.append("profile review decision score ids drifted")
    return failures


def validate_product_status_command() -> list[str]:
    failures: list[str] = []
    provider = load_provider_module()
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        review = root / "review.html"
        result = root / "result.json"
        decision = root / "review-decision.json"
        package_zip = root / "tes-tts-omnivoice-review-package.zip"
        review.write_text("<!doctype html><audio controls src=\"case.wav\"></audio>", encoding="utf-8")
        result.write_text(
            json.dumps(
                {
                    "outputs": [{"id": "case", "output": str(root / "case.wav")}],
                    "benchmark_summary": {
                        "case_count": 1,
                        "avg_rtf": 0.9,
                        "total_audio_duration_seconds": 3.2,
                        "total_generation_ms": 2880,
                    },
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        decision.write_text(
            json.dumps(
                {
                    "schema": "tes-tts-omnivoice-review-decision@1",
                    "review_kind": "profile_review",
                    "decision": "AUDIO_CANDIDATE",
                    "recommended_latency_profile": "fast",
                    "case_count": 1,
                    "scored_case_count": 1,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        package_zip.write_bytes(b"fake-package")
        args = argparse.Namespace(
            path=str(review),
            benchmark_dir=None,
            python=sys.executable,
            ref_audio=None,
            format="json",
            strict=False,
        )
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            if provider.command_product_status(args) != 0:
                failures.append("product-status command failed for local fixture")
        payload = json.loads(stdout.getvalue())
        text_args = argparse.Namespace(
            path=str(review),
            benchmark_dir=None,
            python=sys.executable,
            ref_audio=None,
            format="text",
            strict=False,
        )
        text_stdout = io.StringIO()
        with contextlib.redirect_stdout(text_stdout):
            if provider.command_product_status(text_args) != 0:
                failures.append("product-status text command failed for local fixture")
        text_output = text_stdout.getvalue()
        strict_args = argparse.Namespace(
            path=str(review),
            benchmark_dir=None,
            python=sys.executable,
            ref_audio=None,
            format="text",
            strict=True,
        )
        with contextlib.redirect_stdout(io.StringIO()):
            strict_code = provider.command_product_status(strict_args)
    missing = sorted(REQUIRED_PRODUCT_STATUS_KEYS - set(payload))
    extra = sorted(set(payload) - REQUIRED_PRODUCT_STATUS_KEYS)
    if missing:
        failures.append(f"product-status missing keys {missing}")
    if extra:
        failures.append(f"product-status has extra keys {extra}")
    if payload.get("mode") != "product_status":
        failures.append("product-status mode drifted")
    if payload.get("status") != "PASS":
        failures.append("product-status should be informational PASS")
    if payload.get("review_exists") is not True:
        failures.append("product-status must discover review fixture")
    if payload.get("decision_json_exists") is not True:
        failures.append("product-status must discover review-decision.json")
    if payload.get("decision") != "AUDIO_CANDIDATE":
        failures.append("product-status must report sealed decision")
    if payload.get("recommended_latency_profile") != "fast":
        failures.append("product-status must report recommended latency profile")
    if payload.get("product_state") != "NEEDS_SETUP":
        failures.append("product-status must not overclaim readiness when provider setup is absent")
    if payload.get("package_zip_exists") is not True:
        failures.append("product-status must discover packaged review")
    if payload.get("package_sha256") is None:
        failures.append("product-status must report package sha when zip exists")
    for snippet in ("TES TTS OmniVoice product state:", "Provider:", "Recommended profile:", "Next:", "Locks:"):
        if snippet not in text_output:
            failures.append(f"product-status text output missing snippet: {snippet}")
    if strict_code == 0:
        failures.append("product-status --strict must fail when provider setup is absent")
    for key in ("allows_install", "allows_download", "allows_global_config_write", "allows_sync", "allows_release"):
        if payload.get(key) is not False:
            failures.append(f"product-status must keep {key}=false")
    with tempfile.TemporaryDirectory() as tmp_dir:
        logic_review = Path(tmp_dir) / "review.html"
        logic_review.write_text("<!doctype html>", encoding="utf-8")
        state, action = provider.product_state_and_next_action(
            ready=True,
            review_html=logic_review,
            decision="AUDIO_CANDIDATE",
        )
        if state != "AUDIO_CANDIDATE" or "release identity" not in action:
            failures.append("product-state helper must route AUDIO_CANDIDATE to release identity decision")
        state, _action = provider.product_state_and_next_action(ready=True, review_html=logic_review, decision=None)
        if state != "NEEDS_REVIEW_DECISION":
            failures.append("product-state helper must require review decision when scores are absent")
    return failures


def validate_candidate_command() -> list[str]:
    failures: list[str] = []
    provider = load_provider_module()
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        review = root / "review.html"
        result = root / "result.json"
        decision = root / "review-decision.json"
        wav = root / "case.wav"
        review.write_text("<!doctype html><audio controls src=\"case.wav\"></audio>", encoding="utf-8")
        wav.write_bytes(b"fake-wave")
        result.write_text(
            json.dumps(
                {
                    "outputs": [{"id": "case", "output": str(wav)}],
                    "benchmark_summary": {
                        "case_count": 1,
                        "avg_rtf": 0.9,
                        "total_audio_duration_seconds": 3.2,
                        "total_generation_ms": 2880,
                    },
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        decision.write_text(
            json.dumps(
                {
                    "schema": "tes-tts-omnivoice-review-decision@1",
                    "review_kind": "profile_review",
                    "decision": "AUDIO_CANDIDATE",
                    "recommended_latency_profile": "fast",
                    "case_count": 1,
                    "scored_case_count": 1,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        provider.write_review_package(review, root / "tes-tts-omnivoice-review-package.zip")
        args = argparse.Namespace(
            path=str(review),
            benchmark_dir=None,
            format="json",
            play=True,
            open=True,
            dry_run=True,
            strict=True,
        )
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            if provider.command_candidate(args) != 0:
                failures.append("candidate command failed for sealed local fixture")
        payload = json.loads(stdout.getvalue())
        text_args = argparse.Namespace(
            path=str(review),
            benchmark_dir=None,
            format="text",
            play=True,
            open=True,
            dry_run=True,
            strict=True,
        )
        text_stdout = io.StringIO()
        with contextlib.redirect_stdout(text_stdout):
            if provider.command_candidate(text_args) != 0:
                failures.append("candidate text command failed for sealed local fixture")
        text_output = text_stdout.getvalue()

    missing = sorted(REQUIRED_CANDIDATE_KEYS - set(payload))
    extra = sorted(set(payload) - REQUIRED_CANDIDATE_KEYS)
    if missing:
        failures.append(f"candidate missing keys {missing}")
    if extra:
        failures.append(f"candidate has extra keys {extra}")
    if payload.get("mode") != "product_candidate":
        failures.append("candidate mode drifted")
    if payload.get("status") != "PASS":
        failures.append("candidate should pass for a sealed audio candidate")
    if payload.get("candidate_ready") is not True:
        failures.append("candidate_ready must be true for sealed AUDIO_CANDIDATE with package and audio")
    if payload.get("decision") != "AUDIO_CANDIDATE":
        failures.append("candidate must report sealed decision")
    if payload.get("recommended_latency_profile") != "fast":
        failures.append("candidate must report recommended latency profile")
    if payload.get("audio_count") != 1:
        failures.append("candidate must discover the local WAV output")
    if payload.get("package_zip_exists") is not True:
        failures.append("candidate must discover packaged review")
    if payload.get("package_sha256") is None:
        failures.append("candidate must report package sha")
    if payload.get("open_result") is not None:
        failures.append("candidate dry-run must not open review files")
    if payload.get("playback_results") != []:
        failures.append("candidate dry-run must not play audio")
    for snippet in ("TES TTS OmniVoice candidate: ready", "Recommended profile:", "Package SHA:", "Audio files: 1", "Locks:"):
        if snippet not in text_output:
            failures.append(f"candidate text output missing snippet: {snippet}")
    for key in ("allows_install", "allows_download", "allows_global_config_write", "allows_sync", "allows_release"):
        if payload.get(key) is not False:
            failures.append(f"candidate must keep {key}=false")

    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        review = root / "review.html"
        review.write_text("<!doctype html>", encoding="utf-8")
        args = argparse.Namespace(
            path=str(review),
            benchmark_dir=None,
            format="json",
            play=False,
            open=False,
            dry_run=True,
            strict=True,
        )
        with contextlib.redirect_stdout(io.StringIO()):
            code = provider.command_candidate(args)
        if code == 0:
            failures.append("candidate --strict must fail before review decision/package/audio evidence")
    return failures


def validate_fixtures(fixtures: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if fixtures.get("version") != VERSION:
        failures.append("fixture version drifted")
    if fixtures.get("usage") != "optional_omnivoice_provider_benchmark":
        failures.append("fixture usage drifted")
    if fixtures.get("runtime_dependency") != "optional_external_python_env":
        failures.append("fixture must keep OmniVoice optional")
    cases = fixtures.get("cases")
    if not isinstance(cases, list) or len(cases) < 3:
        failures.append("fixture must include at least three provider cases")
        return failures
    ids: set[str] = set()
    for case in cases:
        case_id = case.get("id")
        if not case_id or case_id in ids:
            failures.append(f"invalid or duplicate case id: {case_id}")
        ids.add(case_id)
        if case.get("language") != "pt":
            failures.append(f"{case_id}: expected language pt")
        text = case.get("text")
        if not isinstance(text, str) or not text.strip():
            failures.append(f"{case_id}: text must be non-empty")
        if "abc123SECRET" in text and "API_KEY=" not in text:
            failures.append(f"{case_id}: secret fixture shape drifted")
    return failures


def add_partition(
    partitions: list[dict[str, Any]],
    *,
    name: str,
    focus: str,
    failures: list[str],
) -> None:
    partitions.append(
        {
            "name": name,
            "focus": focus,
            "status": "FAIL" if failures else "PASS",
            "failure_count": len(failures),
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is supported")

    failures: list[str] = []
    partitions: list[dict[str, Any]] = []

    source_failures = validate_source_imports()
    source_failures.extend(validate_no_reference_text_logging())
    failures.extend(source_failures)
    add_partition(
        partitions,
        name="source_safety",
        focus="top-level optional imports and reference-text logging",
        failures=source_failures,
    )

    probe, probe_failures = run_probe()
    (
        status_payload,
        dry_payload,
        long_read_payload,
        bench_payload,
        profile_review_payload,
        review_payload,
        package_payload,
        shortcut_failures,
    ) = run_status_and_dry_run()

    status_failures = list(probe_failures)
    status_failures.extend(validate_status_payload(status_payload))
    failures.extend(status_failures)
    add_partition(
        partitions,
        name="provider_status_probe",
        focus="optional provider status and setup posture",
        failures=status_failures,
    )

    collection_failures = list(shortcut_failures)
    failures.extend(collection_failures)
    add_partition(
        partitions,
        name="dry_run_payload_collection",
        focus="shared dry-run payload collection without synthesis",
        failures=collection_failures,
    )

    active_failures: list[str] = []
    active_failures.extend(validate_dry_run_payload(dry_payload))
    active_failures.extend(validate_long_read_dry_run_payload(long_read_payload))
    active_failures.extend(validate_warm_cache_dry_run_command())
    active_failures.extend(validate_session_dry_run_command())
    active_failures.extend(validate_auto_latency_profile_selection())
    active_failures.extend(validate_live_smoke_dry_run_command())
    active_failures.extend(validate_jsonl_emitter())
    active_failures.extend(validate_short_speak_in_process_boundary())
    failures.extend(active_failures)
    add_partition(
        partitions,
        name="active_direct_kernel",
        focus="direct/resident product path, resident session, cache, and short speak boundary",
        failures=active_failures,
    )

    server_failures = validate_server_route_command()
    failures.extend(server_failures)
    add_partition(
        partitions,
        name="legacy_server_compatibility",
        focus="server commands retained only as legacy/lab compatibility with safety metadata",
        failures=server_failures,
    )

    packaging_failures: list[str] = []
    packaging_failures.extend(validate_bench_dry_run_payload(bench_payload))
    packaging_failures.extend(validate_profile_review_dry_run_payload(profile_review_payload))
    packaging_failures.extend(validate_review_dry_run_payload(review_payload))
    packaging_failures.extend(validate_package_dry_run_payload(package_payload))
    packaging_failures.extend(validate_review_html_scorecard())
    packaging_failures.extend(validate_profile_review_html_scorecard())
    packaging_failures.extend(validate_review_package_zip())
    packaging_failures.extend(validate_review_decision_command())
    packaging_failures.extend(validate_live_smoke_review_decision_command())
    packaging_failures.extend(validate_profile_review_decision_command())
    packaging_failures.extend(validate_product_status_command())
    packaging_failures.extend(validate_candidate_command())
    failures.extend(packaging_failures)
    add_partition(
        partitions,
        name="dry_run_packaging",
        focus="benchmark, review, package, candidate, and decision surfaces",
        failures=packaging_failures,
    )

    fixture_failures = validate_fixtures(load_json(FIXTURE_PATH))
    failures.extend(fixture_failures)
    add_partition(
        partitions,
        name="fixture_contract",
        focus="optional OmniVoice benchmark fixture contract",
        failures=fixture_failures,
    )

    print(
        json.dumps(
            {
                "status": "FAIL" if failures else "PASS",
                "version": VERSION,
                "provider_script": str(PROVIDER_SCRIPT.relative_to(ROOT)),
                "fixtures": str(FIXTURE_PATH.relative_to(ROOT)),
                "probe_status": probe.get("status") if probe else None,
                "status_command": status_payload.get("status") if status_payload else None,
                "speak_dry_run": dry_payload.get("status") if dry_payload else None,
                "speak_long_dry_run": long_read_payload.get("status") if long_read_payload else None,
                "bench_dry_run": bench_payload.get("status") if bench_payload else None,
                "profile_review_dry_run": profile_review_payload.get("status") if profile_review_payload else None,
                "review_dry_run": review_payload.get("status") if review_payload else None,
                "package_dry_run": package_payload.get("status") if package_payload else None,
                "partitions": partitions,
                "failures": failures,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    print(f"[tes-tts-omnivoice-provider] {'FAIL' if failures else 'PASS'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
