#!/usr/bin/env python3
"""Adversarial secret-redaction oracle for the P-1 hardening line.

Exercises the real runtime `redact_secret_like_values` against governed
adversarial fixtures and fails if any secret value survives in `redacted_text`,
or if a baseline-protected case stops redacting. This oracle is a maintainer
gate (camada de trabalho); it is not bundled and not delivered runtime.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tes_tts_runtime_classifier import redact_secret_like_values
from tes_tts_runtime_types import REDACTION_TOKEN, VERSION

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "benchmarks/tes-tts/secret-redaction-fixtures.json"


def validate_fixtures(fixtures: dict) -> tuple[list[str], list[dict]]:
    failures: list[str] = []
    observed: list[dict] = []

    if fixtures.get("version") != VERSION:
        failures.append("fixture version drifted")
        return failures, observed

    for case in fixtures.get("cases", []):
        cid = case.get("id", "<missing-id>")
        redacted, redactions = redact_secret_like_values(case["source_text"])
        result = {"id": cid, "redacted_text": redacted}
        observed.append(result)

        if case.get("must_redact"):
            token_present = REDACTION_TOKEN in redacted
            leaked = case.get("leaked_value")
            value_survived = bool(leaked) and leaked in redacted
            if not token_present:
                failures.append(f"{cid}: secret not redacted (no token emitted)")
            if value_survived:
                failures.append(f"{cid}: secret value leaked in redacted_text: {leaked!r}")
            if not redactions:
                failures.append(f"{cid}: no redaction recorded")
        else:
            if REDACTION_TOKEN in redacted:
                failures.append(f"{cid}: redaction fired on a non-secret case")

    return failures, observed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is supported")

    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failures, observed = validate_fixtures(fixtures)
    status = "PASS" if not failures else "FAIL"
    payload = {
        "status": status,
        "version": VERSION,
        "fixtures": str(FIXTURES.relative_to(ROOT)),
        "case_count": len(fixtures.get("cases", [])),
        "failures": failures,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("[tes-tts-secret-redaction] " + status)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
