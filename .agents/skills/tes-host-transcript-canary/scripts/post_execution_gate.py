#!/usr/bin/env python3
"""Post-execution gate for TES host transcript canary closeouts.

The gate validates sanitized evidence packets before a TES construction loop can
claim PASS/CERTIFIED. It intentionally does not read raw transcripts; transcript
and runtime details must already be reduced by the source oracles.
"""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


SCHEMA = "tes-host-transcript-post-execution-gate@1"
SKILL_CONTRACT = "tes.host_transcript_canary@0.1.7"
PASS_CLAIM_RE = re.compile(r"^(PASS|CERTIFIED|GO)(?:_|$)")
HEX64_RE = re.compile(r"^[a-fA-F0-9]{64}$")
REQUIRED_POST_EXECUTION = (
    "signal_captured",
    "proposal_generated",
    "curation_path_exists",
    "runtime_recall_proven",
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise SystemExit("evidence JSON must be an object")
    return payload


def is_pass_claim(claim: str) -> bool:
    return bool(PASS_CLAIM_RE.match(claim))


def has_hash(value: Any) -> bool:
    return isinstance(value, str) and bool(HEX64_RE.match(value))


def has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def count(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def is_true(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "pass"}
    return False


def status(value: Any) -> str:
    return str(value or "").upper()


def validate(payload: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    blockers: list[str] = []

    claim = str(payload.get("claim") or "")
    tes_construction = bool(payload.get("tes_construction"))
    platform_behavior = bool(payload.get("platform_behavior"))
    runtime_memory_claim = bool(payload.get("runtime_memory_claim"))
    pass_claim = is_pass_claim(claim)

    harness = payload.get("host_transcript_canary")
    if not isinstance(harness, dict):
        harness = {}
    post = payload.get("post_execution")
    if not isinstance(post, dict):
        post = {}
    runtime_signal = payload.get("runtime_signal_audit")
    if not isinstance(runtime_signal, dict):
        runtime_signal = {}
    related_gates = payload.get("related_gates")
    if not isinstance(related_gates, list):
        related_gates = []

    mandatory_host = tes_construction and platform_behavior and pass_claim
    if mandatory_host:
        if not has_text(harness.get("command_label")):
            failures.append("safe command label is required")
            blockers.append("NEEDS_HOST_TRANSCRIPT_CANARY")
        if not has_hash(harness.get("command_fingerprint")):
            failures.append("command fingerprint is required")
            blockers.append("NEEDS_HOST_TRANSCRIPT_CANARY")
        if status(harness.get("status")) != "PASS":
            failures.append("host transcript canary status must be PASS for TES Platform construction claims")
            blockers.append("NEEDS_HOST_TRANSCRIPT_CANARY")
        if not has_hash(harness.get("transcript_sha256")):
            failures.append("fresh transcript sha256 is required")
            blockers.append("NEEDS_HOST_TRANSCRIPT_CANARY")
        if count(harness.get("tool_use_count")) <= 0:
            failures.append("tool-use evidence is required for host-backed construction claims")
            blockers.append("NEEDS_HOST_TRANSCRIPT_CANARY")
        if not is_true(harness.get("same_command_replay")) and not is_true(harness.get("justified_replay_change")):
            failures.append("same-command replay or justified replay change is required")
            blockers.append("NEEDS_HOST_TRANSCRIPT_CANARY")
        if not any(isinstance(gate, dict) and status(gate.get("status")) == "PASS" for gate in related_gates):
            failures.append("at least one related TES gate must support the same claim")
            blockers.append("NEEDS_POST_EXECUTION_GATE")

    if runtime_memory_claim and pass_claim:
        if status(runtime_signal.get("status")) != "PASS":
            failures.append("runtime memory claims require runtime_signal_audit PASS")
            blockers.append("NEEDS_RUNTIME_SIGNAL_AUDIT")
        if not is_true(runtime_signal.get("contamination_free")):
            failures.append("runtime memory claims require contamination_free=true")
            blockers.append("NEEDS_RUNTIME_SIGNAL_AUDIT")

    if pass_claim and tes_construction:
        for key in REQUIRED_POST_EXECUTION:
            if status(post.get(key)) != "PASS":
                failures.append(f"post-execution field {key} must be PASS")
                blockers.append("NEEDS_POST_EXECUTION_GATE")

    if pass_claim and not (tes_construction and platform_behavior):
        blockers.append("LIMITED_NON_HOST_CLAIM")

    unique_blockers = sorted(set(blockers))
    if failures:
        decision = next(
            (
                blocker
                for blocker in (
                    "NEEDS_HOST_TRANSCRIPT_CANARY",
                    "NEEDS_RUNTIME_SIGNAL_AUDIT",
                    "NEEDS_POST_EXECUTION_GATE",
                )
                if blocker in unique_blockers
            ),
            "NEEDS_POST_EXECUTION_GATE",
        )
    elif "LIMITED_NON_HOST_CLAIM" in unique_blockers:
        decision = "LIMITED_NON_HOST_CLAIM"
    else:
        decision = "PASS"

    return {
        "schema": SCHEMA,
        "skill_contract": SKILL_CONTRACT,
        "status": "PASS" if decision == "PASS" else "NEEDS_REVIEW",
        "decision": decision,
        "claim": claim,
        "tes_construction": tes_construction,
        "platform_behavior": platform_behavior,
        "runtime_memory_claim": runtime_memory_claim,
        "failures": failures,
        "blockers": unique_blockers,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-post-exec-gate-") as tempdir:
        root = Path(tempdir)
        good = {
            "claim": "PASS_CORTEX_PROPOSAL_CURATION_LOOP",
            "tes_construction": True,
            "platform_behavior": True,
            "runtime_memory_claim": True,
            "host_transcript_canary": {
                "status": "PASS",
                "command_label": "self-test-host-command",
                "command_fingerprint": "b" * 64,
                "transcript_sha256": "a" * 64,
                "tool_use_count": 3,
                "same_command_replay": True,
            },
            "runtime_signal_audit": {"status": "PASS", "contamination_free": True},
            "related_gates": [{"name": "runtime-signal-audit", "status": "PASS"}],
            "post_execution": {
                "signal_captured": "PASS",
                "proposal_generated": "PASS",
                "curation_path_exists": "PASS",
                "runtime_recall_proven": "PASS",
            },
        }
        missing_host = {**good, "host_transcript_canary": {"status": "NEEDS_EVIDENCE"}}
        missing_runtime = {**good, "runtime_signal_audit": {"status": "NEEDS_EVIDENCE", "contamination_free": False}}
        missing_post = {**good, "post_execution": {**good["post_execution"], "runtime_recall_proven": "NEEDS_EVIDENCE"}}
        limited = {**good, "claim": "PASS_DOC_ONLY", "tes_construction": False, "platform_behavior": False}
        malformed = {
            **good,
            "host_transcript_canary": {
                **good["host_transcript_canary"],
                "command_fingerprint": "not-a-hash",
                "tool_use_count": "not-a-number",
                "same_command_replay": "false",
            },
        }

        cases = (
            ("good", good, "PASS"),
            ("missing-host", missing_host, "NEEDS_HOST_TRANSCRIPT_CANARY"),
            ("missing-runtime", missing_runtime, "NEEDS_RUNTIME_SIGNAL_AUDIT"),
            ("missing-post", missing_post, "NEEDS_POST_EXECUTION_GATE"),
            ("limited", limited, "LIMITED_NON_HOST_CLAIM"),
            ("malformed", malformed, "NEEDS_HOST_TRANSCRIPT_CANARY"),
        )
        for name, payload, expected in cases:
            path = root / f"{name}.json"
            write_json(path, payload)
            result = validate(load_json(path))
            if result["decision"] != expected:
                failures.append(f"{name}: expected {expected}, got {result['decision']}")

    return {
        "schema": SCHEMA,
        "skill_contract": SKILL_CONTRACT,
        "status": "PASS" if not failures else "FAIL",
        "decision": "PASS" if not failures else "FAIL",
        "coverage": [
            "mandatory host transcript canary",
            "runtime signal audit requirement",
            "post-execution chain",
            "limited non-host claim downgrade",
        ],
        "failures": failures,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate TES host transcript post-execution closeout evidence.")
    parser.add_argument("--evidence", type=Path, help="Sanitized JSON evidence packet.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        result = self_test()
    else:
        if not args.evidence:
            parser.error("--evidence is required unless --self-test is set")
        result = validate(load_json(args.evidence.expanduser().resolve()))

    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json_only:
        print(f"[post-execution-gate] {result['decision']}")
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
