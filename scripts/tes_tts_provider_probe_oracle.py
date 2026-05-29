#!/usr/bin/env python3
"""Self-test TES TTS provider probe contracts with mocked local evidence only."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "benchmarks/tes-tts/provider-probe-fixtures.json"
VERSION = "0.3.147"

PROVIDER_STATUSES = {
    "provider_available",
    "provider_not_available",
    "provider_needs_review",
}
MOCK_STATE_TO_STATUS = {
    "available": "provider_available",
    "unavailable": "provider_not_available",
    "needs_review": "provider_needs_review",
}
REQUIRED_PROBE_KEYS = {
    "provider",
    "status",
    "version",
    "languages",
    "license_note",
    "reason",
}
FORBIDDEN_IMPORT_ROOTS = {
    "http",
    "urllib",
    "requests",
    "socket",
    "subprocess",
    "pip",
    "venv",
}
FORBIDDEN_CALL_NAMES = {
    "open",
    "system",
    "popen",
    "run",
    "call",
    "check_call",
    "check_output",
    "urlopen",
    "request",
    "NamedTemporaryFile",
    "mkstemp",
}
FORBIDDEN_ATTRIBUTE_CALLS = {
    "write_text",
    "write_bytes",
    "mkdir",
    "touch",
    "unlink",
    "rename",
    "replace",
}


@dataclass(frozen=True)
class ProviderProbe:
    provider: str
    status: str
    version: str | None
    languages: list[str]
    license_note: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "status": self.status,
            "version": self.version,
            "languages": self.languages,
            "license_note": self.license_note,
            "reason": self.reason,
        }


def load_fixtures() -> list[dict[str, Any]]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def probe_mock_provider(fixture: dict[str, Any]) -> ProviderProbe:
    status = MOCK_STATE_TO_STATUS[fixture["mock_state"]]
    return ProviderProbe(
        provider=fixture["provider"],
        status=status,
        version=fixture["version"],
        languages=fixture["languages"],
        license_note=fixture["license_note"],
        reason=fixture["expected_reason"],
    )


def validate_probe_contract(probe: dict[str, Any], fixture: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    fixture_id = fixture["id"]
    missing = sorted(REQUIRED_PROBE_KEYS - set(probe))
    extra = sorted(set(probe) - REQUIRED_PROBE_KEYS)
    if missing:
        failures.append(f"{fixture_id}: probe missing keys {missing}")
    if extra:
        failures.append(f"{fixture_id}: probe has extra keys {extra}")
    if probe.get("status") not in PROVIDER_STATUSES:
        failures.append(f"{fixture_id}: invalid status {probe.get('status')}")
    if probe.get("status") != fixture["expected_status"]:
        failures.append(
            f"{fixture_id}: expected status {fixture['expected_status']}, got {probe.get('status')}"
        )
    if probe.get("reason") != fixture["expected_reason"]:
        failures.append(f"{fixture_id}: reason drifted")
    if not isinstance(probe.get("languages"), list):
        failures.append(f"{fixture_id}: languages must be a list")
    if fixture["mock_state"] == "available" and not probe.get("languages"):
        failures.append(f"{fixture_id}: available provider needs at least one language")
    if fixture["mock_state"] == "unavailable" and probe.get("version") is not None:
        failures.append(f"{fixture_id}: unavailable provider version must be null")
    return failures


def validate_fixture_shape(fixture: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    required = {
        "id",
        "provider",
        "mock_state",
        "version",
        "languages",
        "license_note",
        "expected_status",
        "expected_reason",
    }
    missing = sorted(required - set(fixture))
    if missing:
        failures.append(f"{fixture.get('id', '<unknown>')}: missing fields {missing}")
        return failures
    if fixture["mock_state"] not in MOCK_STATE_TO_STATUS:
        failures.append(f"{fixture['id']}: invalid mock_state {fixture['mock_state']}")
    if fixture["expected_status"] not in PROVIDER_STATUSES:
        failures.append(f"{fixture['id']}: invalid expected_status {fixture['expected_status']}")
    if not isinstance(fixture["languages"], list):
        failures.append(f"{fixture['id']}: languages must be a list")
    return failures


def validate_no_probe_side_effect_surface() -> list[str]:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    failures: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in FORBIDDEN_IMPORT_ROOTS:
                    failures.append(f"forbidden import: {alias.name}")
        if isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".", 1)[0]
            if root in FORBIDDEN_IMPORT_ROOTS:
                failures.append(f"forbidden import: {node.module}")
        if isinstance(node, ast.Call):
            function = node.func
            if isinstance(function, ast.Name) and function.id in FORBIDDEN_CALL_NAMES:
                failures.append(f"forbidden call: {function.id}")
            if isinstance(function, ast.Attribute) and function.attr in FORBIDDEN_ATTRIBUTE_CALLS:
                failures.append(f"forbidden attribute call: {function.attr}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is supported")

    failures = validate_no_probe_side_effect_surface()
    fixtures = load_fixtures()
    seen_statuses: set[str] = set()
    for fixture in fixtures:
        shape_failures = validate_fixture_shape(fixture)
        failures.extend(shape_failures)
        if shape_failures:
            continue
        probe = probe_mock_provider(fixture).to_dict()
        seen_statuses.add(probe["status"])
        failures.extend(validate_probe_contract(probe, fixture))

    missing_statuses = sorted(PROVIDER_STATUSES - seen_statuses)
    if missing_statuses:
        failures.append(f"missing mocked provider statuses: {missing_statuses}")

    status = "FAIL" if failures else "PASS"
    print(
        json.dumps(
            {
                "status": status,
                "version": VERSION,
                "fixtures": str(FIXTURE_PATH.relative_to(ROOT)),
                "checked_fixtures": len(fixtures),
                "mocked_statuses": sorted(seen_statuses),
                "failures": failures,
            },
            indent=2,
        )
    )
    print(f"[tes-tts-provider-probe] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
