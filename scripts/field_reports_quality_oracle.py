#!/usr/bin/env python3
"""Deterministic quality oracle for TES Field Reports signal and privacy."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any

import field_reports


SYNTHETIC_PRIVATE_FILE = "/" + "Users/murillo/private/project.py"
SYNTHETIC_EMAIL = "person" + "@example.com"
SYNTHETIC_SECRET_VALUE = "abc" + "123"
SYNTHETIC_BEARER_SECRET = "Bearer " + SYNTHETIC_SECRET_VALUE
SYNTHETIC_SECRET_ASSIGNMENT = "token=" + SYNTHETIC_SECRET_VALUE
SYNTHETIC_PRIVATE_URL = "https://" + "private." + "example.test/repo"
SYNTHETIC_PRIVATE_ISSUE_URL = "https://" + "private." + "example.test/issues/secret"
SYNTHETIC_PRIVATE_REMOTE = "git@" + "github.com:private/repo.git"
SYNTHETIC_PRIVATE_BRANCH = "feature/" + "private-branch"
SYNTHETIC_PRIVATE_SHELL = "rm -rf " + "/" + "Users/murillo/private"
FORBIDDEN_SNIPPETS = (
    SYNTHETIC_PRIVATE_FILE,
    SYNTHETIC_EMAIL,
    SYNTHETIC_BEARER_SECRET,
    SYNTHETIC_SECRET_ASSIGNMENT,
    SYNTHETIC_PRIVATE_URL,
    SYNTHETIC_PRIVATE_REMOTE,
    SYNTHETIC_PRIVATE_BRANCH,
    "Traceback (most recent call last):",
    "```",
    "| leaked | table |",
    "def leaked_function",
    "rm -rf",
    "raw prompt text",
)


def init_git(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)


def event(target: Path, name: str, status: str, surface: str, **details: object) -> dict[str, object]:
    return field_reports.build_event(target, name, status, surface, "oracle", details=details)


def classify_single(target: Path, name: str, status: str, surface: str, **details: object) -> dict[str, object]:
    return field_reports.classify_report([event(target, name, status, surface, **details)])


def require_class(
    target: Path,
    failures: list[str],
    label: str,
    expected_class: str,
    expected_actionability: str,
    name: str,
    status: str,
    surface: str,
    **details: object,
) -> None:
    summary = classify_single(target, name, status, surface, **details)
    if summary.get("report_class") != expected_class:
        failures.append(f"{label}: expected class {expected_class}, got {summary.get('report_class')}")
    if summary.get("actionability") != expected_actionability:
        failures.append(f"{label}: expected actionability {expected_actionability}, got {summary.get('actionability')}")
    for required in (
        "certification_impact",
        "dedupe_fingerprint",
        "findings",
        "next_action",
        "owner_surface",
        "privacy_state",
        "product_class",
        "report_fingerprint",
        "severity",
        "surface_counts",
        "status_counts",
    ):
        if not summary.get(required):
            failures.append(f"{label}: missing {required}")


def assert_private_values_absent(text: str, failures: list[str], context: str) -> None:
    for snippet in FORBIDDEN_SNIPPETS:
        if snippet in text:
            failures.append(f"{context}: leaked forbidden snippet {snippet!r}")
    for name, pattern in (
        ("absolute path", re.compile(r"(/Users|/home|/private|/var/folders|[A-Za-z]:\\)[^\s`\"')]+")),
        ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
        ("code fence", re.compile(r"```")),
        ("markdown table", re.compile(r"(?m)^\s*\|.+\|\s*$")),
        ("git remote", re.compile(r"(?i)(github\.com[:/][^\s]+\.git|git@[^:\s]+:[^\s]+)")),
        ("stack trace", re.compile(r"(?i)(traceback \(most recent call last\)|\bat .+:\d+:\d+|exception: .+)")),
    ):
        if pattern.search(text):
            failures.append(f"{context}: leaked {name}")


def fake_gh(bin_dir: Path, mode: str) -> None:
    path = bin_dir / "gh"
    if mode == "success":
        script = """#!/bin/sh
echo "https://github.com/murillodutt/tilly-engineer-skills/issues/123"
"""
    elif mode == "unsafe-success":
        script = f"""#!/bin/sh
echo "{SYNTHETIC_PRIVATE_ISSUE_URL}"
"""
    else:
        script = """#!/bin/sh
echo "auth failed" >&2
exit 2
"""
    path.write_text(script, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def receipt_payloads(target: Path) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for path in sorted(field_reports.receipts_path(target).glob("*.json")):
        payloads.append(json.loads(path.read_text(encoding="utf-8")))
    return payloads


def has_receipt(target: Path, outcome: str) -> bool:
    return any(item.get("outcome") == outcome or item.get("reason") == outcome for item in receipt_payloads(target))


def run_oracle() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-field-quality-") as tempdir:
        root = Path(tempdir)
        target = root / "target"
        init_git(target)
        field_reports.install_hook(target)

        require_class(
            target,
            failures,
            "version drift",
            "version-drift",
            "high",
            "tes_update",
            "PASS",
            "installer",
            installed_version="0.3.61",
            cloud_version=field_reports.VERSION,
            update_available=True,
            recommended_update_scope="helpers-only",
        )
        require_class(
            target,
            failures,
            "helper contract",
            "helper-contract-failure",
            "high",
            "tes_update",
            "FAIL",
            "installer",
            helper_contract_status="FAIL",
            recommended_update_scope="helpers-only",
            returncode=1,
        )
        require_class(
            target,
            failures,
            "adapter drift",
            "adapter-drift",
            "high",
            "install_adapter",
            "NEEDS_REVIEW",
            "adapter",
            route="codex",
            adapter="codex",
            runtime_trigger_status="DRIFT",
        )
        require_class(
            target,
            failures,
            "mcp activation",
            "mcp-activation-failure",
            "high",
            "install_mcp",
            "BLOCKED",
            "mcp",
            route="mcp",
            returncode=2,
        )
        require_class(
            target,
            failures,
            "cortex batch",
            "cortex-certification",
            "medium",
            "cortex.audit",
            "PASS",
            "cortex",
            surface_count=2,
        )
        scoped_event = event(target, "cortex.audit", "PASS", "cortex", surface_count=2)
        if scoped_event.get("scope_status") != "PASS" or not isinstance(scoped_event.get("scope"), dict):
            failures.append("field report events must carry normalized runtime scope")
        unsafe_scope = field_reports.record_event(
            target,
            "cortex.audit",
            "FAIL",
            "cortex",
            "oracle",
            details={"evidence_ref": "/absolute/unsafe/evidence.md"},
        )
        if unsafe_scope.get("status") != "BLOCKED" or unsafe_scope.get("writes") != []:
            failures.append("unsafe scope refs must be blocked without writes")

        hostile = event(
            target,
            "tes_update",
            "FAIL",
            "installer",
            unsafe_path=SYNTHETIC_PRIVATE_FILE,
            unsafe_email=SYNTHETIC_EMAIL,
            unsafe_token=SYNTHETIC_BEARER_SECRET,
            unsafe_url=SYNTHETIC_PRIVATE_URL,
            unsafe_remote=SYNTHETIC_PRIVATE_REMOTE,
            unsafe_branch=SYNTHETIC_PRIVATE_BRANCH,
            unsafe_stack="Traceback (most recent call last):\n  File '" + SYNTHETIC_PRIVATE_FILE + "', line 1",
            unsafe_prompt="raw prompt text",
            unsafe_code="def leaked_function(): return 'secret'",
            unsafe_shell=SYNTHETIC_PRIVATE_SHELL,
            unsafe_table="| leaked | table |",
        )
        hostile_text = json.dumps(hostile, sort_keys=True)
        assert_private_values_absent(hostile_text, failures, "event payload")
        body = field_reports.build_issue_body([hostile], 1, 1)
        assert_private_values_absent(body, failures, "issue body")
        for term in (
            "Actionable findings",
            "Certification impact:",
            "Dedupe fingerprint:",
            "Next action:",
            "Owner surface:",
            "Privacy state:",
            "Product class:",
            "Report class:",
            "Severity:",
        ):
            if term not in body:
                failures.append(f"issue body missing actionable report field: {term}")
        hostile_summary = field_reports.classify_report([hostile])
        if hostile_summary.get("privacy_state") != "sanitized":
            failures.append("field report summaries must declare sanitized privacy state")
        if not hostile_summary.get("dedupe_fingerprint"):
            failures.append("field report summaries must expose a dedupe fingerprint")
            failures.append("issue body missing actionable report fields")

        low_target = root / "low"
        init_git(low_target)
        field_reports.install_hook(low_target)
        field_reports.record_event(
            low_target,
            "tes_update",
            "PASS",
            "installer",
            "oracle",
            details={"cloud_version": "unknown", "installed_version": field_reports.VERSION, "update_available": False},
        )
        low_drain = field_reports.drain(low_target, "oracle", env={**os.environ, "PATH": str(root / "missing-gh")})
        if low_drain.get("status") != "PASS" or low_drain.get("suppressed") is not True:
            failures.append(f"low heartbeat should suppress, got {low_drain}")
        if not has_receipt(low_target, "low-signal-heartbeat"):
            failures.append("suppressed low heartbeat must write suppression receipt")

        invalid_target = root / "invalid"
        init_git(invalid_target)
        field_reports.install_hook(invalid_target)
        field_reports.outbox_path(invalid_target).write_text("{not-json}\n", encoding="utf-8")
        invalid = field_reports.drain(invalid_target, "oracle")
        if invalid.get("status") != "BLOCKED":
            failures.append("invalid outbox must block drain")
        if not field_reports.outbox_path(invalid_target).read_text(encoding="utf-8").strip():
            failures.append("invalid outbox must remain pending")
        if not has_receipt(invalid_target, "invalid-outbox"):
            failures.append("invalid outbox must write blocked receipt")

        blocked_target = root / "blocked"
        init_git(blocked_target)
        field_reports.install_hook(blocked_target)
        field_reports.record_event(blocked_target, "cortex.audit", "FAIL", "cortex", "oracle", details={"returncode": 2})
        blocked = field_reports.drain(blocked_target, "oracle", env={**os.environ, "PATH": str(root / "missing-gh")})
        if blocked.get("status") != "BLOCKED" or blocked.get("transport_state") != "blocked":
            failures.append(f"missing gh should be blocked transport, got {blocked}")
        if not field_reports.outbox_path(blocked_target).read_text(encoding="utf-8").strip():
            failures.append("blocked transport must keep outbox pending")
        if not has_receipt(blocked_target, "transport-blocked"):
            failures.append("blocked transport must write blocked receipt")

        sent_target = root / "sent"
        init_git(sent_target)
        field_reports.install_hook(sent_target)
        field_reports.record_event(sent_target, "cortex.audit", "FAIL", "cortex", "oracle", details={"returncode": 2})
        bin_dir = root / "bin-success"
        bin_dir.mkdir()
        fake_gh(bin_dir, "success")
        sent = field_reports.drain(sent_target, "oracle", env={**os.environ, "PATH": str(bin_dir)})
        if sent.get("status") != "PASS" or sent.get("transport_state") != "sent":
            failures.append(f"successful fake gh drain should be sent, got {sent}")
        if field_reports.outbox_path(sent_target).read_text(encoding="utf-8").strip():
            failures.append("successful send must clear outbox")
        receipt_text = json.dumps(receipt_payloads(sent_target), sort_keys=True)
        assert_private_values_absent(receipt_text, failures, "receipt")
        if "payload" in receipt_text.lower() and "payload_sha256" not in receipt_text:
            failures.append("receipt must not contain payload body")

        unsafe_target = root / "unsafe"
        init_git(unsafe_target)
        field_reports.install_hook(unsafe_target)
        field_reports.record_event(unsafe_target, "cortex.audit", "FAIL", "cortex", "oracle", details={"returncode": 2})
        unsafe_bin = root / "bin-unsafe"
        unsafe_bin.mkdir()
        fake_gh(unsafe_bin, "unsafe-success")
        unsafe = field_reports.drain(unsafe_target, "oracle", env={**os.environ, "PATH": str(unsafe_bin)})
        if unsafe.get("status") != "BLOCKED":
            failures.append("unsafe gh issue output must block drain")
        if not field_reports.outbox_path(unsafe_target).read_text(encoding="utf-8").strip():
            failures.append("unsafe gh output must keep outbox pending")
        if not has_receipt(unsafe_target, "transport-blocked"):
            failures.append("unsafe gh output must write blocked receipt")

        disabled_target = root / "disabled"
        init_git(disabled_target)
        field_reports.install_hook(disabled_target)
        field_reports.disable(disabled_target)
        disabled = field_reports.drain(disabled_target, "oracle")
        if disabled.get("status") != "SKIP" or disabled.get("transport_state") != "disabled":
            failures.append(f"disabled drain must be explicit, got {disabled}")

        empty_target = root / "empty"
        init_git(empty_target)
        field_reports.install_hook(empty_target)
        empty = field_reports.drain(empty_target, "oracle")
        if empty.get("status") != "PASS" or empty.get("transport_state") != "empty":
            failures.append(f"empty drain must be explicit, got {empty}")

    return {"version": field_reports.VERSION, "status": "FAIL" if failures else "PASS", "failures": failures}


def self_test() -> int:
    result = run_oracle()
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        print("[field-reports-quality] FAIL")
        return 1
    print("[field-reports-quality] PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    parser.error("--self-test is required")


if __name__ == "__main__":
    sys.exit(main())
