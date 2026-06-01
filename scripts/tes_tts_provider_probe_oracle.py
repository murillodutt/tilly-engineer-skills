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
FALLBACK_FIXTURE_PATH = ROOT / "benchmarks/tes-tts/provider-fallback-fixtures.json"
VERSION = "0.3.153"

PROVIDER_ORDER = ["omnivoice", "google", "openai", "elevenlabs", "say"]
PROVIDER_STATUSES = {
    "provider_available",
    "provider_not_available",
    "provider_needs_review",
}
FALLBACK_STATUSES = {
    "fallback_ready",
    "TTS_NOT_AVAILABLE",
}
ERROR_CLASSES = {
    "AUTH_UNAVAILABLE",
    "RATE_LIMITED",
    "PROVIDER_UNAVAILABLE",
    "VOICE_UNAVAILABLE",
    "GENERIC_TTS_ERROR",
}
MOCK_STATE_TO_STATUS = {
    "available": "provider_available",
    "unavailable": "provider_not_available",
    "needs_review": "provider_needs_review",
    "degraded": "provider_needs_review",
}
REQUIRED_PROBE_KEYS = {
    "provider",
    "status",
    "version",
    "languages",
    "license_note",
    "reason",
}
SIDE_EFFECT_FIELDS = {
    "allows_network",
    "allows_install",
    "allows_download",
    "allows_write",
    "certifies_provider_support",
}
FALLBACK_SIDE_EFFECT_FIELDS = SIDE_EFFECT_FIELDS | {
    "writes_global_config",
    "writes_unavailable_registry",
    "writes_durable_cache",
}
REQUEST_LOCAL_ACTIONS = [
    "no_provider_install",
    "no_provider_download",
    "no_provider_certification",
    "no_global_config_write",
    "no_unavailable_provider_registry",
    "no_durable_conversion_cache",
]
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


def load_fallback_fixtures() -> list[dict[str, Any]]:
    return json.loads(FALLBACK_FIXTURE_PATH.read_text(encoding="utf-8"))


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


def plan_provider_fallback(fixture: dict[str, Any]) -> dict[str, Any]:
    attempted_providers: list[str] = []
    error_classes: list[str] = []
    voice_default_retries: list[str] = []
    selected_provider: str | None = None
    selected_voice: str | None = None
    reason = fixture["expected_reason"]

    for attempt in fixture["attempts"]:
        provider = attempt["provider"]
        if provider not in attempted_providers:
            attempted_providers.append(provider)
        error_class = attempt["error_class"]
        if error_class and error_class not in error_classes:
            error_classes.append(error_class)
        if error_class == "VOICE_UNAVAILABLE" and provider not in voice_default_retries:
            voice_default_retries.append(provider)
        if attempt["outcome"] == "success":
            selected_provider = provider
            selected_voice = attempt["voice"]
            break

    status = "fallback_ready" if selected_provider else "TTS_NOT_AVAILABLE"
    return {
        "status": status,
        "provider_order": fixture["provider_order"],
        "attempted_providers": attempted_providers,
        "selected_provider": selected_provider,
        "selected_voice": selected_voice,
        "voice_default_retries": voice_default_retries,
        "error_classes": error_classes,
        "request_local_actions": REQUEST_LOCAL_ACTIONS,
        "certifies_provider_support": False,
        "reason": reason,
    }


def validate_fallback_fixture_shape(fixture: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    required = {
        "id",
        "provider_order",
        "requested_voice",
        "attempts",
        "allows_network",
        "allows_install",
        "allows_download",
        "allows_write",
        "writes_global_config",
        "writes_unavailable_registry",
        "writes_durable_cache",
        "certifies_provider_support",
        "expected_status",
        "expected_attempted_providers",
        "expected_selected_provider",
        "expected_selected_voice",
        "expected_voice_default_retries",
        "expected_error_classes",
        "expected_reason",
    }
    fixture_id = fixture.get("id", "<unknown>")
    missing = sorted(required - set(fixture))
    if missing:
        failures.append(f"{fixture_id}: missing fields {missing}")
        return failures
    if fixture["provider_order"] != PROVIDER_ORDER:
        failures.append(f"{fixture_id}: provider_order must be {PROVIDER_ORDER}")
    if fixture["expected_status"] not in FALLBACK_STATUSES:
        failures.append(f"{fixture_id}: invalid expected_status {fixture['expected_status']}")
    if not isinstance(fixture["attempts"], list) or not fixture["attempts"]:
        failures.append(f"{fixture_id}: attempts must be a non-empty list")
    for field in FALLBACK_SIDE_EFFECT_FIELDS:
        if fixture.get(field) is not False:
            failures.append(f"{fixture_id}: {field} must be false")
    provider_positions = {provider: index for index, provider in enumerate(PROVIDER_ORDER)}
    previous_position = -1
    previous_attempt: dict[str, Any] | None = None
    for attempt in fixture["attempts"]:
        provider = attempt.get("provider")
        if provider not in PROVIDER_ORDER:
            failures.append(f"{fixture_id}: invalid provider {provider}")
        else:
            position = provider_positions[provider]
            same_provider_retry = (
                previous_attempt is not None
                and previous_attempt.get("provider") == provider
                and previous_attempt.get("error_class") == "VOICE_UNAVAILABLE"
            )
            if position < previous_position:
                failures.append(f"{fixture_id}: attempts must preserve provider catalog order")
            if position == previous_position and not same_provider_retry:
                failures.append(
                    f"{fixture_id}: repeated provider attempts require VOICE_UNAVAILABLE retry"
                )
            previous_position = position
        if attempt.get("outcome") not in {"success", "error"}:
            failures.append(f"{fixture_id}: invalid outcome {attempt.get('outcome')}")
        error_class = attempt.get("error_class")
        if attempt.get("outcome") == "error" and error_class not in ERROR_CLASSES:
            failures.append(f"{fixture_id}: invalid error_class {error_class}")
        if attempt.get("outcome") == "success" and error_class is not None:
            failures.append(f"{fixture_id}: successful attempt error_class must be null")
        previous_attempt = attempt
    return failures


def validate_provider_fallback_plan(plan: dict[str, Any], fixture: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    fixture_id = fixture["id"]
    expected = {
        "status": fixture["expected_status"],
        "attempted_providers": fixture["expected_attempted_providers"],
        "selected_provider": fixture["expected_selected_provider"],
        "selected_voice": fixture["expected_selected_voice"],
        "voice_default_retries": fixture["expected_voice_default_retries"],
        "error_classes": fixture["expected_error_classes"],
        "reason": fixture["expected_reason"],
    }
    for key, value in expected.items():
        if plan.get(key) != value:
            failures.append(f"{fixture_id}: expected {key} {value!r}, got {plan.get(key)!r}")
    if plan.get("provider_order") != PROVIDER_ORDER:
        failures.append(f"{fixture_id}: plan provider_order drifted")
    if plan.get("certifies_provider_support") is not False:
        failures.append(f"{fixture_id}: plan must not certify provider support")
    if plan.get("request_local_actions") != REQUEST_LOCAL_ACTIONS:
        failures.append(f"{fixture_id}: request-local action set drifted")
    if plan.get("status") == "TTS_NOT_AVAILABLE" and plan.get("selected_provider") is not None:
        failures.append(f"{fixture_id}: unavailable plan must not select a provider")
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
        "allows_network",
        "allows_install",
        "allows_download",
        "allows_write",
        "certifies_provider_support",
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
    for field in SIDE_EFFECT_FIELDS:
        if fixture.get(field) is not False:
            failures.append(f"{fixture['id']}: {field} must be false")
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
    fallback_fixtures = load_fallback_fixtures()
    seen_statuses: set[str] = set()
    seen_mock_states: set[str] = set()
    seen_error_classes: set[str] = set()
    seen_fallback_statuses: set[str] = set()
    for fixture in fixtures:
        shape_failures = validate_fixture_shape(fixture)
        failures.extend(shape_failures)
        if shape_failures:
            continue
        probe = probe_mock_provider(fixture).to_dict()
        seen_statuses.add(probe["status"])
        seen_mock_states.add(fixture["mock_state"])
        failures.extend(validate_probe_contract(probe, fixture))

    missing_statuses = sorted(PROVIDER_STATUSES - seen_statuses)
    if missing_statuses:
        failures.append(f"missing mocked provider statuses: {missing_statuses}")
    missing_mock_states = sorted(set(MOCK_STATE_TO_STATUS) - seen_mock_states)
    if missing_mock_states:
        failures.append(f"missing mocked provider states: {missing_mock_states}")

    for fixture in fallback_fixtures:
        shape_failures = validate_fallback_fixture_shape(fixture)
        failures.extend(shape_failures)
        if shape_failures:
            continue
        plan = plan_provider_fallback(fixture)
        seen_fallback_statuses.add(plan["status"])
        seen_error_classes.update(plan["error_classes"])
        failures.extend(validate_provider_fallback_plan(plan, fixture))

    missing_fallback_statuses = sorted(FALLBACK_STATUSES - seen_fallback_statuses)
    if missing_fallback_statuses:
        failures.append(f"missing fallback statuses: {missing_fallback_statuses}")
    missing_error_classes = sorted(ERROR_CLASSES - seen_error_classes)
    if missing_error_classes:
        failures.append(f"missing fallback error classes: {missing_error_classes}")

    status = "FAIL" if failures else "PASS"
    print(
        json.dumps(
            {
                "status": status,
                "version": VERSION,
                "fixtures": str(FIXTURE_PATH.relative_to(ROOT)),
                "fallback_fixtures": str(FALLBACK_FIXTURE_PATH.relative_to(ROOT)),
                "checked_fixtures": len(fixtures),
                "checked_fallback_fixtures": len(fallback_fixtures),
                "mocked_statuses": sorted(seen_statuses),
                "mocked_states": sorted(seen_mock_states),
                "fallback_statuses": sorted(seen_fallback_statuses),
                "fallback_error_classes": sorted(seen_error_classes),
                "failures": failures,
            },
            indent=2,
        )
    )
    print(f"[tes-tts-provider-probe] {status}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
