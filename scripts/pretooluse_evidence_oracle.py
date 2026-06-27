#!/usr/bin/env python3
"""Validate sanitized PreToolUse installed-evidence packets."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = ROOT / "docs/evidence/reports/2026/06/27/hooks/pretooluse-ceiling-installed-evidence"
PRIVATE_PATH_RE = re.compile(r"(/Users/|/home/|~/Dev/(?!tes-canaries\b)|[A-Za-z]:\\\\)")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def validate_packet(packet: Path) -> dict[str, Any]:
    failures: list[str] = []
    report = packet / "REPORT.md"
    summary_path = packet / "summary.json"
    report_text = report.read_text(encoding="utf-8") if report.is_file() else ""
    summary = _read_json(summary_path)

    if not report_text:
        failures.append("missing REPORT.md")
    if not summary:
        failures.append("missing or invalid summary.json")
    combined = report_text + "\n" + json.dumps(summary, sort_keys=True)
    if PRIVATE_PATH_RE.search(combined):
        failures.append("evidence packet must not contain private filesystem paths")
    for term in (
        "Privacy state: sanitized",
        "Native evidence status: `NEEDS_EVIDENCE`",
        "Canary replay status: `NOT_RUN_NO_AUTHORIZATION`",
        "Ceiling claim: not claimed",
    ):
        if term not in report_text:
            failures.append(f"REPORT.md missing {term!r}")

    if summary.get("schema") != "pretooluse-installed-evidence@1":
        failures.append("summary schema must be pretooluse-installed-evidence@1")
    if summary.get("privacy_state") != "sanitized":
        failures.append("summary privacy_state must be sanitized")
    if summary.get("native_evidence_status") != "NEEDS_EVIDENCE":
        failures.append("summary native_evidence_status must remain NEEDS_EVIDENCE")
    if summary.get("canary_replay_status") != "NOT_RUN_NO_AUTHORIZATION":
        failures.append("summary canary_replay_status must be explicit when canary is not used")
    if summary.get("ceiling_claim") != "not_claimed":
        failures.append("summary must not claim PASS_CEILING")

    matrix = summary.get("matrix") if isinstance(summary.get("matrix"), dict) else {}
    expected_matrix = {
        "status": "PASS",
        "helper_contract_status": "PASS",
        "discoverability_status": "NEEDS_DISCOVERABILITY",
        "hook_health_status": "NEEDS_EVIDENCE",
        "hook_health_floor_status": "NEEDS_EVIDENCE",
        "hook_health_ceiling_status": "NEEDS_FLOOR",
    }
    for key, expected in expected_matrix.items():
        if matrix.get(key) != expected:
            failures.append(f"summary matrix {key} must be {expected}")

    hosts = summary.get("host_attribution") if isinstance(summary.get("host_attribution"), dict) else {}
    for host in ("codex", "claude", "cursor"):
        if hosts.get(host) != "CONTRACT_SIMULATED":
            failures.append(f"host_attribution.{host} must be CONTRACT_SIMULATED")

    return {
        "oracle": "pretooluse-evidence",
        "packet": str(packet.relative_to(ROOT)),
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    args = parser.parse_args(argv)
    result = validate_packet(args.packet if args.packet.is_absolute() else ROOT / args.packet)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[pretooluse-evidence] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
