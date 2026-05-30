#!/usr/bin/env python3
"""Validate the optional TES TTS OmniVoice provider surface."""

from __future__ import annotations

import argparse
import ast
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROVIDER_SCRIPT = ROOT / "scripts/tes_tts_omnivoice_provider.py"
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
    "command_shape",
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
    "result_json",
    "review_html",
    "package_zip",
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_source_imports() -> list[str]:
    failures: list[str] = []
    tree = ast.parse(PROVIDER_SCRIPT.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in FORBIDDEN_TOP_LEVEL_IMPORTS:
                    failures.append(f"top-level optional import leaked: {alias.name}")
        elif isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".", 1)[0]
            if root in FORBIDDEN_TOP_LEVEL_IMPORTS:
                failures.append(f"top-level optional import leaked: {node.module}")
    return failures


def validate_no_reference_text_logging() -> list[str]:
    failures: list[str] = []
    tree = ast.parse(PROVIDER_SCRIPT.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if isinstance(key, ast.Constant) and key.value == "ref_text":
                    failures.append("provider metrics must not emit reference voice text")
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
    return status_payload, dry_payload, bench_payload, review_payload, package_payload, failures


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
                            "text": "Leia API_KEY=abc123SECRET com segurança e avalie TypeScript.",
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
    ]
    for snippet in required_snippets:
        if snippet not in html_text:
            failures.append(f"review HTML missing scorecard snippet: {snippet}")
    if "abc123SECRET" in html_text:
        failures.append("review HTML leaked secret-like fixture text")
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is supported")

    failures: list[str] = []
    failures.extend(validate_source_imports())
    failures.extend(validate_no_reference_text_logging())
    probe, probe_failures = run_probe()
    failures.extend(probe_failures)
    status_payload, dry_payload, bench_payload, review_payload, package_payload, shortcut_failures = run_status_and_dry_run()
    failures.extend(shortcut_failures)
    failures.extend(validate_status_payload(status_payload))
    failures.extend(validate_dry_run_payload(dry_payload))
    failures.extend(validate_bench_dry_run_payload(bench_payload))
    failures.extend(validate_review_dry_run_payload(review_payload))
    failures.extend(validate_package_dry_run_payload(package_payload))
    failures.extend(validate_review_html_scorecard())
    failures.extend(validate_review_package_zip())
    failures.extend(validate_fixtures(load_json(FIXTURE_PATH)))
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
                "bench_dry_run": bench_payload.get("status") if bench_payload else None,
                "review_dry_run": review_payload.get("status") if review_payload else None,
                "package_dry_run": package_payload.get("status") if package_payload else None,
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
