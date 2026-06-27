#!/usr/bin/env python3
"""Validate sanitized PreToolUse installed-evidence packets by expected claim."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = ROOT / "docs/evidence/reports/2026/06/27/hooks/pretooluse-ceiling-installed-evidence"
PRIVATE_PATH_RE = re.compile(r"(/Users/|/home/|~/Dev/(?!tes-canaries\b)|[A-Za-z]:\\\\)")
EXPECT_NEEDS_EVIDENCE = "needs-evidence"
EXPECT_PASS_CEILING = "pass-ceiling"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _base_packet(packet: Path, failures: list[str]) -> tuple[str, dict[str, Any]]:
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

    if summary.get("schema") != "pretooluse-installed-evidence@1":
        failures.append("summary schema must be pretooluse-installed-evidence@1")
    if summary.get("privacy_state") != "sanitized":
        failures.append("summary privacy_state must be sanitized")

    if "Privacy state: sanitized" not in report_text:
        failures.append("REPORT.md missing 'Privacy state: sanitized'")

    return report_text, summary


def _validate_needs_evidence_packet(report_text: str, summary: dict[str, Any], failures: list[str]) -> None:
    for term in (
        "Native evidence status: `NEEDS_EVIDENCE`",
        "Canary replay status: `NOT_RUN_NO_AUTHORIZATION`",
        "Ceiling claim: not claimed",
    ):
        if term not in report_text:
            failures.append(f"REPORT.md missing {term!r}")

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


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return path.as_posix()


def _claimed_hosts(summary: dict[str, Any], failures: list[str]) -> list[str]:
    raw_claimed = summary.get("claimed_hosts")
    if isinstance(raw_claimed, list) and raw_claimed and all(isinstance(item, str) and item for item in raw_claimed):
        return list(raw_claimed)
    current_host = summary.get("current_host")
    if isinstance(current_host, str) and current_host:
        return [current_host]
    failures.append("summary must name current_host or claimed_hosts for PASS_CEILING")
    return []


def _validate_pass_ceiling_packet(report_text: str, summary: dict[str, Any], failures: list[str]) -> None:
    for term in (
        "Native evidence status: `OBSERVED`",
        "Ceiling claim: `PASS_CEILING`",
    ):
        if term not in report_text:
            failures.append(f"REPORT.md missing {term!r}")

    if summary.get("native_evidence_status") != "OBSERVED":
        failures.append("summary native_evidence_status must be OBSERVED for PASS_CEILING")
    if summary.get("ceiling_claim") != "PASS_CEILING":
        failures.append("summary ceiling_claim must be PASS_CEILING")

    matrix = _as_dict(summary.get("matrix"))
    expected_matrix = {
        "helper_contract_status": "PASS",
        "hook_health_floor_status": "PASS_BASIC",
        "hook_health_ceiling_status": "PASS_CEILING",
    }
    for key, expected in expected_matrix.items():
        if matrix.get(key) != expected:
            failures.append(f"summary matrix {key} must be {expected}")
    if matrix.get("hook_health_status") not in {"PASS", "PASS_WITH_FINDINGS"}:
        failures.append("summary matrix hook_health_status must be PASS or PASS_WITH_FINDINGS")
    if matrix.get("discoverability_status") not in {"NEEDS_DISCOVERABILITY", "PASS"}:
        failures.append("summary matrix discoverability_status must prove installed discoverability evidence")

    hosts = _as_dict(summary.get("host_attribution"))
    claimed_hosts = _claimed_hosts(summary, failures)
    for host in claimed_hosts:
        if hosts.get(host) != "OBSERVED":
            failures.append(f"host_attribution.{host} must be OBSERVED for PASS_CEILING")

    scope = _as_dict(summary.get("ceiling_evidence_scope"))
    if scope.get("schema_version") != "pretooluse_decision@2":
        failures.append("ceiling_evidence_scope.schema_version must be pretooluse_decision@2")
    if scope.get("aggregation_policy") != "per_host_no_cross_fill":
        failures.append("ceiling_evidence_scope.aggregation_policy must be per_host_no_cross_fill")
    if scope.get("legacy_policy") != "historical_context_only":
        failures.append("ceiling_evidence_scope.legacy_policy must be historical_context_only")
    if scope.get("claim_scope") not in {"current_host", "all_configured_hosts"}:
        failures.append("ceiling_evidence_scope.claim_scope must be current_host or all_configured_hosts")
    if scope.get("claim_scope") == "current_host" and len(claimed_hosts) == 1 and scope.get("current_host") != claimed_hosts[0]:
        failures.append("ceiling_evidence_scope.current_host must match the claimed host")

    required_hosts = [item for item in _as_list(scope.get("required_hosts")) if isinstance(item, str)]
    for host in claimed_hosts:
        if host not in required_hosts:
            failures.append(f"ceiling_evidence_scope.required_hosts must include {host}")

    per_host = _as_dict(scope.get("per_host"))
    for host in claimed_hosts:
        entry = _as_dict(per_host.get(host))
        if entry.get("agent") != host:
            failures.append(f"ceiling_evidence_scope.per_host.{host}.agent must match the host")
        if entry.get("native_evidence") != "observed":
            failures.append(f"ceiling_evidence_scope.per_host.{host}.native_evidence must be observed")
        if entry.get("status") != "PASS_CEILING":
            failures.append(f"ceiling_evidence_scope.per_host.{host}.status must be PASS_CEILING")
        if not isinstance(entry.get("considered_records"), int) or entry.get("considered_records", 0) < 1:
            failures.append(f"ceiling_evidence_scope.per_host.{host}.considered_records must be positive")
        if _as_list(entry.get("gaps")):
            failures.append(f"ceiling_evidence_scope.per_host.{host}.gaps must be empty")
        if _as_list(entry.get("current_v2_contradictions")):
            failures.append(f"ceiling_evidence_scope.per_host.{host}.current_v2_contradictions must be empty")


def validate_packet(packet: Path, expect: str = EXPECT_NEEDS_EVIDENCE) -> dict[str, Any]:
    failures: list[str] = []
    report_text, summary = _base_packet(packet, failures)

    if expect == EXPECT_NEEDS_EVIDENCE:
        _validate_needs_evidence_packet(report_text, summary, failures)
    elif expect == EXPECT_PASS_CEILING:
        _validate_pass_ceiling_packet(report_text, summary, failures)
    else:
        failures.append(f"unsupported expectation {expect!r}")

    return {
        "oracle": "pretooluse-evidence",
        "expect": expect,
        "packet": _display_path(packet),
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def _write_packet(packet: Path, report_text: str, summary: dict[str, Any]) -> None:
    packet.mkdir(parents=True, exist_ok=True)
    (packet / "REPORT.md").write_text(report_text, encoding="utf-8")
    (packet / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _pass_ceiling_summary() -> dict[str, Any]:
    return {
        "schema": "pretooluse-installed-evidence@1",
        "privacy_state": "sanitized",
        "native_evidence_status": "OBSERVED",
        "ceiling_claim": "PASS_CEILING",
        "current_host": "codex",
        "claimed_hosts": ["codex"],
        "host_attribution": {
            "codex": "OBSERVED",
            "claude": "CONTRACT_SIMULATED",
            "cursor": "CONTRACT_SIMULATED",
        },
        "matrix": {
            "status": "PASS",
            "helper_contract_status": "PASS",
            "discoverability_status": "NEEDS_DISCOVERABILITY",
            "hook_health_status": "PASS",
            "hook_health_floor_status": "PASS_BASIC",
            "hook_health_ceiling_status": "PASS_CEILING",
        },
        "ceiling_evidence_scope": {
            "schema_version": "pretooluse_decision@2",
            "claim_scope": "current_host",
            "aggregation_policy": "per_host_no_cross_fill",
            "current_host": "codex",
            "required_hosts": ["codex"],
            "legacy_policy": "historical_context_only",
            "per_host": {
                "codex": {
                    "agent": "codex",
                    "native_evidence": "observed",
                    "considered_records": 3,
                    "ignored_legacy_records": 1,
                    "oldest_considered_ts": "2026-06-27T00:00:00Z",
                    "newest_considered_ts": "2026-06-27T00:05:00Z",
                    "gaps": [],
                    "current_v2_contradictions": [],
                    "status": "PASS_CEILING",
                },
                "claude": {
                    "agent": "claude",
                    "native_evidence": "contract_simulated_only",
                    "considered_records": 0,
                    "ignored_legacy_records": 0,
                    "oldest_considered_ts": None,
                    "newest_considered_ts": None,
                    "gaps": ["missing_pretooluse_runtime_rows"],
                    "current_v2_contradictions": [],
                    "status": "NEEDS_EVIDENCE",
                },
            },
        },
    }


def _needs_evidence_summary() -> dict[str, Any]:
    return {
        "schema": "pretooluse-installed-evidence@1",
        "privacy_state": "sanitized",
        "native_evidence_status": "NEEDS_EVIDENCE",
        "canary_replay_status": "NOT_RUN_NO_AUTHORIZATION",
        "ceiling_claim": "not_claimed",
        "evidence_kind": "installed-target-simulation",
        "generated_from": "self-test fixture",
        "host_attribution": {
            "claude": "CONTRACT_SIMULATED",
            "codex": "CONTRACT_SIMULATED",
            "cursor": "CONTRACT_SIMULATED",
        },
        "matrix": {
            "status": "PASS",
            "helper_contract_status": "PASS",
            "discoverability_status": "NEEDS_DISCOVERABILITY",
            "hook_health_status": "NEEDS_EVIDENCE",
            "hook_health_floor_status": "NEEDS_EVIDENCE",
            "hook_health_ceiling_status": "NEEDS_FLOOR",
        },
    }


def _report_text(native_status: str, ceiling_claim: str, canary_status: str | None = None) -> str:
    lines = [
        "# Sanitized PreToolUse Evidence Fixture",
        "",
        "Privacy state: sanitized.",
        f"Native evidence status: `{native_status}`.",
    ]
    if canary_status:
        lines.append(f"Canary replay status: `{canary_status}`.")
    lines.append(f"Ceiling claim: `{ceiling_claim}`." if ceiling_claim == "PASS_CEILING" else f"Ceiling claim: {ceiling_claim}.")
    return "\n".join(lines) + "\n"


def _assert_status(
    failures: list[str],
    *,
    label: str,
    result: dict[str, Any],
    expected_status: str,
    expected_failure: str | None = None,
) -> None:
    if result["status"] != expected_status:
        failures.append(f"{label} expected {expected_status}, got {result['status']}: {result['failures']}")
        return
    if expected_failure and not any(expected_failure in item for item in result.get("failures", [])):
        failures.append(f"{label} did not produce expected failure {expected_failure!r}: {result['failures']}")


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="pretooluse-evidence-oracle-") as tempdir:
        root = Path(tempdir)

        needs_packet = root / "needs-evidence"
        _write_packet(
            needs_packet,
            _report_text("NEEDS_EVIDENCE", "not claimed", "NOT_RUN_NO_AUTHORIZATION"),
            _needs_evidence_summary(),
        )
        _assert_status(
            failures,
            label="needs-evidence fixture",
            result=validate_packet(needs_packet, EXPECT_NEEDS_EVIDENCE),
            expected_status="PASS",
        )

        pass_packet = root / "pass-ceiling"
        _write_packet(pass_packet, _report_text("OBSERVED", "PASS_CEILING"), _pass_ceiling_summary())
        _assert_status(
            failures,
            label="valid PASS_CEILING fixture",
            result=validate_packet(pass_packet, EXPECT_PASS_CEILING),
            expected_status="PASS",
        )

        simulated = _pass_ceiling_summary()
        simulated["native_evidence_status"] = "NEEDS_EVIDENCE"
        simulated["host_attribution"]["codex"] = "CONTRACT_SIMULATED"
        simulated["ceiling_evidence_scope"]["per_host"]["codex"]["native_evidence"] = "contract_simulated_only"
        simulated_packet = root / "pass-ceiling-simulated-only"
        _write_packet(simulated_packet, _report_text("NEEDS_EVIDENCE", "PASS_CEILING"), simulated)
        _assert_status(
            failures,
            label="simulated-only PASS_CEILING fixture",
            result=validate_packet(simulated_packet, EXPECT_PASS_CEILING),
            expected_status="FAIL",
            expected_failure="native_evidence_status must be OBSERVED",
        )

        missing_attribution = _pass_ceiling_summary()
        missing_attribution["host_attribution"] = {}
        missing_attribution_packet = root / "pass-ceiling-missing-attribution"
        _write_packet(missing_attribution_packet, _report_text("OBSERVED", "PASS_CEILING"), missing_attribution)
        _assert_status(
            failures,
            label="missing host attribution PASS_CEILING fixture",
            result=validate_packet(missing_attribution_packet, EXPECT_PASS_CEILING),
            expected_status="FAIL",
            expected_failure="host_attribution.codex must be OBSERVED",
        )

        missing_scoped_native = _pass_ceiling_summary()
        missing_scoped_native["ceiling_evidence_scope"]["per_host"]["codex"]["native_evidence"] = "not_available"
        missing_scoped_native["ceiling_evidence_scope"]["per_host"]["codex"]["considered_records"] = 0
        missing_scoped_packet = root / "pass-ceiling-missing-scoped-native"
        _write_packet(missing_scoped_packet, _report_text("OBSERVED", "PASS_CEILING"), missing_scoped_native)
        _assert_status(
            failures,
            label="missing scoped native evidence PASS_CEILING fixture",
            result=validate_packet(missing_scoped_packet, EXPECT_PASS_CEILING),
            expected_status="FAIL",
            expected_failure="native_evidence must be observed",
        )

        cross_filled = _pass_ceiling_summary()
        codex_entry = cross_filled["ceiling_evidence_scope"]["per_host"]["codex"]
        codex_entry["native_evidence"] = "not_available"
        codex_entry["considered_records"] = 0
        codex_entry["status"] = "NEEDS_EVIDENCE"
        cross_filled["ceiling_evidence_scope"]["per_host"]["claude"] = {
            "agent": "claude",
            "native_evidence": "observed",
            "considered_records": 3,
            "ignored_legacy_records": 0,
            "oldest_considered_ts": "2026-06-27T00:00:00Z",
            "newest_considered_ts": "2026-06-27T00:05:00Z",
            "gaps": [],
            "current_v2_contradictions": [],
            "status": "PASS_CEILING",
        }
        cross_packet = root / "pass-ceiling-cross-filled"
        _write_packet(cross_packet, _report_text("OBSERVED", "PASS_CEILING"), cross_filled)
        _assert_status(
            failures,
            label="cross-filled host PASS_CEILING fixture",
            result=validate_packet(cross_packet, EXPECT_PASS_CEILING),
            expected_status="FAIL",
            expected_failure="per_host.codex.status must be PASS_CEILING",
        )

    return {
        "oracle": "pretooluse-evidence",
        "mode": "self-test",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--expect", choices=(EXPECT_NEEDS_EVIDENCE, EXPECT_PASS_CEILING), default=EXPECT_NEEDS_EVIDENCE)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2, sort_keys=True))
        print("[pretooluse-evidence] " + result["status"])
        return 0 if result["status"] == "PASS" else 1

    result = validate_packet(args.packet if args.packet.is_absolute() else ROOT / args.packet, args.expect)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[pretooluse-evidence] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
