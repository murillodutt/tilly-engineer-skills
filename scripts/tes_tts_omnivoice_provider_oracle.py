#!/usr/bin/env python3
"""Validate the optional TES TTS OmniVoice provider surface."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import subprocess
import sys
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
    failures.extend(validate_fixtures(load_json(FIXTURE_PATH)))
    print(
        json.dumps(
            {
                "status": "FAIL" if failures else "PASS",
                "version": VERSION,
                "provider_script": str(PROVIDER_SCRIPT.relative_to(ROOT)),
                "fixtures": str(FIXTURE_PATH.relative_to(ROOT)),
                "probe_status": probe.get("status") if probe else None,
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
