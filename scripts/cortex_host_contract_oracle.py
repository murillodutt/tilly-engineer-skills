#!/usr/bin/env python3
"""Certify Cortex host hook contracts from offline fixtures."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "scripts" / "fixtures" / "cortex_host_contracts"
FIXTURE_SCHEMA = "tes.cortex.host-contract.v1"
REQUIRED_INTENTS = ("advisory_recall", "capture_proposal", "needs_align")
OFFICIAL_SOURCE_PREFIXES = (
    "https://code.claude.com/docs/",
    "https://developers.openai.com/codex/",
    "https://cursor.com/docs/",
)

HOST_CONTRACTS: dict[str, dict[str, Any]] = {
    "claude-code": {
        "config_surfaces": {".claude/settings.json"},
        "event_case": "PascalCase",
        "events": {"SessionStart", "UserPromptSubmit", "PreToolUse", "Stop", "PreCompact"},
        "output_style": "claude-json-or-exit-code",
        "blocks_with_exit_code_2": True,
        "cursor_native": False,
    },
    "codex": {
        "config_surfaces": {".codex/hooks.json", ".codex/config.toml"},
        "event_case": "PascalCase",
        "events": {"SessionStart", "UserPromptSubmit", "PreToolUse", "Stop", "PreCompact"},
        "output_style": "codex-json-or-exit-code",
        "blocks_with_exit_code_2": True,
        "cursor_native": False,
    },
    "cursor": {
        "config_surfaces": {".cursor/hooks.json"},
        "event_case": "camelCase",
        "events": {"sessionStart", "beforeSubmitPrompt", "preToolUse", "stop", "preCompact"},
        "output_style": "cursor-json-permission-continue",
        "blocks_with_exit_code_2": False,
        "cursor_native": True,
    },
}

WRONG_SURFACE_PREFIXES = {
    "claude-code": (".codex/", ".cursor/"),
    "codex": (".claude/", ".cursor/"),
    "cursor": (".claude/", ".codex/"),
}

CURSOR_ONLY_FIELDS = {"permission", "user_message", "agent_message", "updated_input", "followup_message"}
CLAUDE_CODEX_ONLY_FIELDS = {"hookSpecificOutput", "decision", "reason", "stopReason", "systemMessage"}


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def load_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, [f"{rel(path)}: cannot load JSON: {exc}"]
    if not isinstance(data, dict):
        return None, [f"{rel(path)}: root must be an object"]
    return data, []


def official_source_refs(fixture: dict[str, Any], path: Path) -> list[str]:
    failures: list[str] = []
    refs = fixture.get("source_refs")
    if not isinstance(refs, list) or not refs:
        return [f"{rel(path)}: missing source_refs"]
    for ref in refs:
        if not isinstance(ref, str):
            failures.append(f"{rel(path)}: source_refs entries must be strings")
        elif not ref.startswith(OFFICIAL_SOURCE_PREFIXES):
            failures.append(f"{rel(path)}: source ref is not an official host doc/source URL: {ref}")
    return failures


def sample_stdout(output: dict[str, Any]) -> Any:
    return output.get("stdout")


def hook_specific(stdout: Any, event: str) -> dict[str, Any] | None:
    if not isinstance(stdout, dict):
        return None
    data = stdout.get("hookSpecificOutput")
    if not isinstance(data, dict):
        return None
    if data.get("hookEventName") != event:
        return None
    return data


def validate_claude_codex_output(host: str, event: str, output: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    exit_code = output.get("exit_code")
    stdout = sample_stdout(output)
    stderr = output.get("stderr", "")

    if exit_code == 2:
        if not isinstance(stderr, str) or not stderr.strip():
            failures.append(f"{host} {event}: exit 2 must carry stderr feedback")
        return failures
    if exit_code != 0:
        return [f"{host} {event}: unsupported fixture exit_code {exit_code}"]
    if stdout is None:
        return [f"{host} {event}: exit 0 fixture must include structured stdout"]
    if not isinstance(stdout, dict):
        return [f"{host} {event}: structured stdout must be a JSON object"]

    cursor_fields = sorted(CURSOR_ONLY_FIELDS.intersection(stdout))
    if cursor_fields:
        failures.append(f"{host} {event}: cursor-native output fields are wrong host contract: {', '.join(cursor_fields)}")

    if event in {"SessionStart", "UserPromptSubmit", "PreToolUse"}:
        specific = hook_specific(stdout, event)
        if not specific:
            failures.append(f"{host} {event}: missing hookSpecificOutput.hookEventName")
        elif "additionalContext" not in specific and "permissionDecision" not in specific:
            failures.append(f"{host} {event}: hookSpecificOutput must carry additionalContext or permissionDecision")
    elif event == "Stop":
        specific = hook_specific(stdout, event)
        if specific:
            if "additionalContext" not in specific:
                failures.append(f"{host} Stop: hookSpecificOutput must carry additionalContext")
        else:
            failures.append(f"{host} Stop: Cortex capture proposal must be advisory additionalContext, not a block")
    elif event == "PreCompact":
        if "continue" not in stdout and stdout.get("decision") != "block":
            failures.append(f"{host} PreCompact: missing continue or decision block")
    else:
        failures.append(f"{host}: unsupported event fixture {event}")
    return failures


def validate_cursor_output(event: str, output: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    exit_code = output.get("exit_code")
    stdout = sample_stdout(output)
    if exit_code != 0:
        failures.append("cursor native Cortex fixture must use JSON output instead of exit-code blocking")
    if not isinstance(stdout, dict):
        return failures + ["cursor output stdout must be a JSON object"]

    wrong_fields = sorted(CLAUDE_CODEX_ONLY_FIELDS.intersection(stdout))
    if wrong_fields:
        failures.append(f"cursor {event}: Claude/Codex output fields are wrong native contract: {', '.join(wrong_fields)}")
    if "hookSpecificOutput" in stdout:
        failures.append(f"cursor {event}: native .cursor/hooks.json fixture must not use hookSpecificOutput")

    if event == "preToolUse":
        if stdout.get("continue") is not True:
            failures.append("cursor preToolUse: continue must be true for advisory flow")
        if stdout.get("permission") not in {"allow", "deny", "ask"}:
            failures.append("cursor preToolUse: missing native permission decision")
        if not any(isinstance(stdout.get(field), str) and stdout[field].strip() for field in ("agent_message", "user_message")):
            failures.append("cursor preToolUse: missing agent_message or user_message")
    elif event in {"sessionStart", "beforeSubmitPrompt", "preCompact"}:
        if stdout.get("continue") is not True:
            failures.append(f"cursor {event}: continue must be true")
        if not any(isinstance(stdout.get(field), str) and stdout[field].strip() for field in ("agent_message", "user_message")):
            failures.append(f"cursor {event}: missing agent_message or user_message")
    elif event == "stop":
        if stdout.get("continue") is not True:
            failures.append("cursor stop: continue must be true")
        if not isinstance(stdout.get("followup_message"), str) or not stdout["followup_message"].strip():
            failures.append("cursor stop: missing native followup_message")
    else:
        failures.append(f"cursor: unsupported event fixture {event}")
    return failures


def validate_output(host: str, event: str, output: Any) -> list[str]:
    if not isinstance(output, dict):
        return [f"{host} {event}: output must be an object"]
    if "exit_code" not in output:
        return [f"{host} {event}: output missing exit_code"]
    if host == "cursor":
        return validate_cursor_output(event, output)
    if host in {"claude-code", "codex"}:
        return validate_claude_codex_output(host, event, output)
    return [f"unknown host for output validation: {host}"]


def validate_sample(host: str, sample: Any, path: Path) -> list[str]:
    if not isinstance(sample, dict):
        return [f"{rel(path)}: sample must be an object"]
    failures: list[str] = []
    intent = sample.get("intent")
    event = sample.get("event")
    input_data = sample.get("input")
    if intent not in REQUIRED_INTENTS:
        failures.append(f"{rel(path)}: sample has unsupported intent {intent!r}")
    if event not in HOST_CONTRACTS[host]["events"]:
        failures.append(f"{rel(path)}: sample event {event!r} is not valid for {host}")
    if not isinstance(input_data, dict):
        failures.append(f"{rel(path)}: sample {intent} missing input object")
    else:
        if input_data.get("hook_event_name") != event:
            failures.append(f"{rel(path)}: sample {intent} input hook_event_name must match {event}")
        for field in ("session_id", "cwd", "hook_event_name"):
            if field not in input_data:
                failures.append(f"{rel(path)}: sample {intent} input missing {field}")
        if event in {"PreToolUse", "preToolUse"}:
            if "tool_name" not in input_data or "tool_input" not in input_data:
                failures.append(f"{rel(path)}: {event} input must include tool_name and tool_input")
    failures.extend(
        f"{rel(path)}: {failure}"
        for failure in validate_output(host, str(event), sample.get("output"))
    )
    return failures


def validate_fixture(path: Path, fixture: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if fixture.get("fixture_schema") != FIXTURE_SCHEMA:
        failures.append(f"{rel(path)}: fixture_schema must be {FIXTURE_SCHEMA}")
    host = fixture.get("host")
    if host not in HOST_CONTRACTS:
        failures.append(f"{rel(path)}: unsupported host {host!r}")
        return failures
    host_contract = HOST_CONTRACTS[str(host)]
    failures.extend(official_source_refs(fixture, path))

    contract = fixture.get("contract")
    if not isinstance(contract, dict):
        return failures + [f"{rel(path)}: missing contract object"]

    surfaces = contract.get("config_surfaces")
    if not isinstance(surfaces, list) or not all(isinstance(item, str) for item in surfaces):
        failures.append(f"{rel(path)}: contract.config_surfaces must be a string array")
        surfaces = []
    surface_set = set(surfaces)
    expected_surfaces = set(host_contract["config_surfaces"])
    if host == "codex":
        if not surface_set.intersection(expected_surfaces):
            failures.append(f"{rel(path)}: codex config surface must include .codex/hooks.json or .codex/config.toml")
    elif surface_set != expected_surfaces:
        failures.append(f"{rel(path)}: config surfaces for {host} must be {sorted(expected_surfaces)}")
    for surface in surface_set:
        if any(surface.startswith(prefix) for prefix in WRONG_SURFACE_PREFIXES[str(host)]):
            failures.append(f"{rel(path)}: wrong-host config surface {surface}")

    if contract.get("event_case") != host_contract["event_case"]:
        failures.append(f"{rel(path)}: event_case must be {host_contract['event_case']}")
    if contract.get("output_style") != host_contract["output_style"]:
        failures.append(f"{rel(path)}: output_style must be {host_contract['output_style']}")
    if contract.get("blocks_with_exit_code_2") is not host_contract["blocks_with_exit_code_2"]:
        failures.append(f"{rel(path)}: blocks_with_exit_code_2 is wrong for {host}")

    lifecycle = contract.get("lifecycle_events")
    if not isinstance(lifecycle, dict):
        failures.append(f"{rel(path)}: missing lifecycle_events object")
        lifecycle = {}
    for intent in REQUIRED_INTENTS:
        event = lifecycle.get(intent)
        if event not in host_contract["events"]:
            failures.append(f"{rel(path)}: {intent} event {event!r} is not valid for {host}")

    samples = fixture.get("samples")
    if not isinstance(samples, list):
        return failures + [f"{rel(path)}: missing samples array"]
    sample_intents = {sample.get("intent") for sample in samples if isinstance(sample, dict)}
    for intent in REQUIRED_INTENTS:
        if intent not in sample_intents:
            failures.append(f"{rel(path)}: missing sample for {intent}")
    for sample in samples:
        if isinstance(sample, dict):
            expected_event = lifecycle.get(sample.get("intent"))
            if expected_event and sample.get("event") != expected_event:
                failures.append(f"{rel(path)}: sample {sample.get('intent')} event must be {expected_event}")
        failures.extend(validate_sample(str(host), sample, path))

    negative_cases = fixture.get("negative_cases")
    if not isinstance(negative_cases, list) or not negative_cases:
        failures.append(f"{rel(path)}: missing negative_cases")
    else:
        for case in negative_cases:
            if not isinstance(case, dict):
                failures.append(f"{rel(path)}: negative case must be an object")
                continue
            event = case.get("event")
            output_failures = validate_output(str(host), str(event), case.get("output"))
            if not output_failures:
                failures.append(f"{rel(path)}: negative case {case.get('name')} was accepted")
    return failures


def analyze() -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    loaded: list[str] = []
    negative_proofs: list[str] = []
    positive_hosts: set[str] = set()

    if not FIXTURE_DIR.exists():
        failures.append(f"missing fixture directory: {rel(FIXTURE_DIR)}")
        return {"status": "FAIL", "fixtures": loaded, "failures": failures, "warnings": warnings}

    for path in sorted(FIXTURE_DIR.rglob("*.json")):
        loaded.append(rel(path))
        fixture, load_failures = load_json(path)
        failures.extend(load_failures)
        if fixture is None:
            continue
        if fixture.get("negative") is True:
            result = validate_fixture(path, fixture)
            if result:
                negative_proofs.append(rel(path))
            else:
                failures.append(f"{rel(path)}: negative fixture was accepted")
            continue
        fixture_failures = validate_fixture(path, fixture)
        failures.extend(fixture_failures)
        host = fixture.get("host")
        if host in HOST_CONTRACTS and not fixture_failures:
            positive_hosts.add(str(host))

    missing_hosts = sorted(set(HOST_CONTRACTS) - positive_hosts)
    for host in missing_hosts:
        failures.append(f"missing valid positive fixture for {host}")
    if not negative_proofs:
        failures.append("missing negative fixture proof")

    return {
        "status": "PASS" if not failures else "FAIL",
        "fixture_schema": FIXTURE_SCHEMA,
        "fixtures": loaded,
        "positive_hosts": sorted(positive_hosts),
        "negative_proofs": sorted(negative_proofs),
        "warnings": warnings,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.parse_args()

    result = analyze()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[cortex-host-contract] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
