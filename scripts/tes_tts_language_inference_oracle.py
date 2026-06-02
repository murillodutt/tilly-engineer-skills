#!/usr/bin/env python3
"""Behavior oracle for mixed pt/en chunk-language inference (P-2 / LIH line).

Exercises the real runtime infer_long_read_chunk_language under
requested_language='auto' and fails if a chunk's resolved language drifts from
the governed fixture. Camada de trabalho only — not bundled.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tes_tts_omnivoice_runtime_support import infer_long_read_chunk_language
from tes_tts_runtime_types import VERSION

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "benchmarks/tes-tts/language-inference-fixtures.json"


def validate_fixtures(fixtures: dict) -> tuple[list[str], list[dict]]:
    failures: list[str] = []
    observed: list[dict] = []

    structural: list[str] = []
    if fixtures.get("version") != VERSION:
        failures.append("fixture version drifted")
    if fixtures.get("usage") != "language_inference_contract":
        structural.append("fixture usage must be language_inference_contract")
    if fixtures.get("runtime_output") is not False:
        structural.append("language-inference fixture must not claim runtime output")
    failures.extend(structural)
    # De-mask: only a non-drift structural failure skips the behavior cases.
    if structural:
        return failures, observed

    for case in fixtures.get("cases", []):
        cid = case.get("id", "<missing-id>")
        got = infer_long_read_chunk_language(case["text"], "auto")
        observed.append({"id": cid, "language": got})
        if got != case["expected_language"]:
            failures.append(f"{cid}: language drifted (expected {case['expected_language']}, got {got})")

    return failures, observed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is supported")

    fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    failures, observed = validate_fixtures(fixtures)
    status = "PASS" if not failures else "FAIL"
    print(json.dumps({
        "status": status,
        "version": VERSION,
        "fixtures": str(FIXTURE_PATH.relative_to(ROOT)),
        "case_count": len(fixtures.get("cases", [])),
        "observed": observed,
        "failures": failures,
    }, indent=2, ensure_ascii=False))
    print("[tes-tts-language-inference] " + status)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
