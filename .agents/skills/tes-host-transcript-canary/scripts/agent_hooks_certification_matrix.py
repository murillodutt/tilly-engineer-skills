#!/usr/bin/env python3
"""Build a TES agent-hook certification matrix.

The matrix is a local development harness: it organizes existing TES source,
installed-target, and host-transcript evidence without replacing the product
oracles that own hook behavior.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA = "tes-agent-hooks-certification-matrix@1"
SKILL_CONTRACT = "tes.host_transcript_canary@0.1.8"
STATUSES = {"PASS", "FAIL", "NEEDS_EVIDENCE", "NOT_RUN"}


@dataclass(frozen=True)
class SourceCheck:
    """One source-owned hook characteristic and the tokens that prove it."""

    row_id: str
    label: str
    paths: tuple[str, ...]
    tokens: tuple[str, ...]
    owner: str
    evidence_lane: str = "source"


SOURCE_CHECKS: tuple[SourceCheck, ...] = (
    SourceCheck(
        "hosts-supported",
        "Codex, Claude, and Cursor are the supported agent hook hosts.",
        ("scripts/tes_install.py",),
        ('AGENTS = ("codex", "claude", "cursor")',),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "host-config-paths",
        "Each host has its own config path.",
        ("scripts/tes_install.py", "docs/architecture/INSTALLATION-FRAMEWORK.md"),
        (".codex/config.toml", ".claude/settings.json", ".cursor/hooks.json"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "common-entrypoint",
        "Agent hook configs call tes_install.py hook with an agent id and target.",
        ("scripts/tes_install.py",),
        ("tes_install.py", "hook --agent", "--target"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "runtime-helpers",
        "Hook runtime helpers are delivered under .tes/bin.",
        ("scripts/tes_install.py",),
        ("HOOK_RUNTIME_HELPERS", "cortex_runtime.py", "pretooluse_kernel.py", "pretooluse_session.py"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "codex-events",
        "Codex declares SessionStart and PreToolUse hook events.",
        ("scripts/tes_install.py",),
        ('"codex"', '"SessionStart"', '"PreToolUse"', ".codex/config.toml"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "claude-events",
        "Claude declares SessionStart and PreToolUse hook events.",
        ("scripts/tes_install.py",),
        ('"claude"', '"SessionStart"', '"PreToolUse"', ".claude/settings.json"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "cursor-events",
        "Cursor declares sessionStart, beforeSubmitPrompt, and preToolUse hook events.",
        ("scripts/tes_install.py",),
        ('"cursor"', '"sessionStart"', '"beforeSubmitPrompt"', '"preToolUse"', ".cursor/hooks.json"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "sessionstart-two-phase",
        "SessionStart uses first-session setup and Claude announce/rewake phases.",
        ("scripts/tes_install.py",),
        ("--announce-start", "--rewake-on-complete", "asyncRewake", ".tes/postinstall.json"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "pretooluse-projection",
        "PreToolUse projects the Mantra Gate before tool execution.",
        ("scripts/tes_install.py", "scripts/pretooluse_kernel.py", "docs/architecture/PRETOOLUSE-CONTRACT.md"),
        ("hook_pretooluse", "decide_pretooluse", "Mantra Gate"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "pretooluse-matcher",
        "PreToolUse matcher covers mutating tool classes.",
        ("scripts/tes_install.py",),
        ("Write|Edit|MultiEdit|NotebookEdit|Bash|Shell|shell|apply_patch",),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "pipeline-boundary",
        "Pipeline stays split across adapter, kernel, session, renderer, and ledger.",
        ("docs/architecture/PRETOOLUSE-CONTRACT.md", "scripts/pretooluse_kernel.py", "scripts/pretooluse_session.py"),
        ("host hook config", "host-neutral PreToolUse decision kernel", "session coordinator", "runtime ledger"),
        "docs/architecture/PRETOOLUSE-CONTRACT.md",
    ),
    SourceCheck(
        "kernel-behavior",
        "Kernel normalizes payloads, extracts patch paths, detects governed surfaces, and records classifier trace.",
        ("scripts/pretooluse_kernel.py",),
        ("hook_patch_paths", "hook_tool_path_source", "is_governed_path", "classifier_trace"),
        "scripts/pretooluse_kernel.py",
    ),
    SourceCheck(
        "governed-surfaces",
        "Governed surface hints cover bootloaders, ADR/governance docs, skills, and Cursor rules.",
        ("scripts/pretooluse_kernel.py",),
        ("AGENTS.md", "CLAUDE.md", "docs/adr/", "docs/governance/", "SKILL.md", ".cursor/rules/"),
        "scripts/pretooluse_kernel.py",
    ),
    SourceCheck(
        "decision-vocabulary",
        "PreToolUse emits allow, supervise, block, and needs_discoverability outcomes.",
        ("scripts/pretooluse_kernel.py",),
        ('"outcome": "allow"', '"outcome": "supervise"', '"outcome": "block"', '"outcome": "needs_discoverability"'),
        "scripts/pretooluse_kernel.py",
    ),
    SourceCheck(
        "routine-silence",
        "Routine non-governed work allows silently.",
        ("scripts/pretooluse_kernel.py", "scripts/tes_install.py"),
        ("routine_non_mutating", "routine_non_governed", "silent_allow"),
        "scripts/pretooluse_kernel.py",
    ),
    SourceCheck(
        "governed-supervision",
        "Governed mutations allow with supervision context instead of silent allow.",
        ("scripts/pretooluse_kernel.py",),
        ("governed_surface_mutation", '"outcome": "supervise"', "Confirm the contract obligation"),
        "scripts/pretooluse_kernel.py",
    ),
    SourceCheck(
        "forbidden-block",
        "Forbidden actions block before execution.",
        ("scripts/pretooluse_kernel.py", "scripts/tes_install.py"),
        ("forbidden_class", '"block": True', '"permission_decision": "deny"'),
        "scripts/pretooluse_kernel.py",
    ),
    SourceCheck(
        "discoverability",
        "Unknown mutating-looking governed tools produce NEEDS_DISCOVERABILITY.",
        ("scripts/pretooluse_kernel.py", "docs/architecture/PRETOOLUSE-CONTRACT.md"),
        ("needs_discoverability_unknown_mutation", "NEEDS_DISCOVERABILITY", "risk=needs-discoverability"),
        "scripts/pretooluse_kernel.py",
    ),
    SourceCheck(
        "anti-cry-wolf",
        "Same-session repeated supervision suppresses repeated context only.",
        ("scripts/pretooluse_session.py", "scripts/tes_install.py"),
        ("coordinate_pretooluse_context", "anti_crywolf_suppressed", "context_suppressed"),
        "scripts/pretooluse_session.py",
    ),
    SourceCheck(
        "claude-renderer",
        "Claude renders hookSpecificOutput/additionalContext and blocks with exit 2.",
        ("scripts/tes_install.py",),
        ("json_hookSpecificOutput_allow", "hookSpecificOutput", "permissionDecision", "return 2"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "codex-renderer",
        "Codex renders context to stderr and blocks with exit 2.",
        ("scripts/tes_install.py",),
        ("stderr_context", "print(combined_context, file=sys.stderr)", "return 2"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "cursor-renderer",
        "Cursor renders JSON permission/continue/user_message/agent_message contracts.",
        ("scripts/tes_install.py",),
        ("json_permission_deny", '"permission": "deny"', '"continue": True', "user_message", "agent_message"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "runtime-ledger",
        "Runtime hook ledger and legacy ledger paths are declared.",
        ("scripts/tes_install.py",),
        (".tes/runtime/hooks/executed.jsonl", ".tes/hooks/executed.jsonl", "HOOK_SENTINEL_PATH"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "ledger-gitignore",
        "Runtime hook ledgers are excluded from Git.",
        ("scripts/tes_install.py",),
        ("ensure_hook_runtime_excluded", ".tes/runtime/", ".tes/hooks/executed.jsonl"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "host-real-provenance",
        "Runtime records written by real hooks use explicit host-real provenance and transcript correlation.",
        ("scripts/tes_install.py",),
        (
            'HOOK_PROVENANCE_HOST_REAL = "host-real"',
            "hook_execution_provenance",
            "apply_host_transcript_evidence",
        ),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "pretooluse-ledger-fields",
        "PreToolUse records include decision, risk, classifier, renderer, and marker fields.",
        ("scripts/tes_install.py",),
        ("classifier_trace", "renderer_trace", "reason_codes", "marker_emitted", "context_suppressed"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "redaction-boundary",
        "Ledger records command categories/redaction state rather than raw command text.",
        ("scripts/tes_install.py",),
        ("hook_command_category", "command_category", "command_redacted"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "dedupe-contract",
        "Dedupe distinguishes Cursor batch rows and replay history from contradictions.",
        ("scripts/tes_install.py",),
        ("hook_dedupe_contract", "cursor_batch_rule", "current_v2_contradiction_rule"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "hook-health-schema",
        "Hook health emits tes-hook-health@2.",
        ("scripts/tes_install.py",),
        ('HOOK_HEALTH_SCHEMA_VERSION = "tes-hook-health@2"',),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "event-states",
        "Hook health event states include observed, configured, not configured, and stale/unexpected.",
        ("scripts/tes_install.py",),
        ("OBSERVED", "CONFIGURED", "NOT_CONFIGURED", "STALE/UNEXPECTED"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "health-statuses",
        "Hook health status vocabulary covers not applied, evidence gap, degraded, findings, and pass.",
        ("scripts/tes_install.py",),
        ("NOT_APPLIED", "NEEDS_EVIDENCE", "DEGRADED", "PASS_WITH_FINDINGS", "PASS"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "floor-ceiling-split",
        "PASS_BASIC is distinct from PASS_CEILING and ceiling gaps remain visible.",
        ("scripts/tes_install.py", "docs/architecture/PRETOOLUSE-CONTRACT.md"),
        ("PASS_BASIC", "PASS_CEILING", "ceiling_gaps"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "no-cross-fill",
        "Current-host evidence cannot be filled by another host.",
        ("scripts/tes_install.py", "scripts/canary_admission_oracle.py"),
        ("current_host", "per_host_no_cross_fill", "CONFIGURED_NOT_OBSERVED"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "cortex-advisory-no-write",
        "Cortex advisory may add context but cannot write durable memory automatically.",
        ("scripts/tes_install.py", "docs/architecture/PRETOOLUSE-CONTRACT.md"),
        ("cortex_advisory_no_write", "no-write advisory boundary", "capture_proposal=PROPOSED"),
        "scripts/tes_install.py",
    ),
    SourceCheck(
        "related-oracles",
        "Primary hook certification oracles exist.",
        (
            "scripts/tes_install.py",
            "scripts/installed_certification_oracle.py",
            "scripts/canary_admission_oracle.py",
            "scripts/pretooluse_contract_oracle.py",
            "scripts/hook_audit_prompt_oracle.py",
        ),
        ("hook-health", "tes-installed-certification@1", "tes-canary-admission@1", "CONTRACT_TERMS", "REQUIRED_TERMS"),
        "scripts",
    ),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def file_exists(repo: Path, relpath: str) -> bool:
    return (repo / relpath).is_file()


def run_process(argv: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(argv, cwd=cwd, check=False, capture_output=True, text=True)
    payload: dict[str, Any] | None = None
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = None
    return {
        "argv": argv,
        "returncode": completed.returncode,
        "stdout_bytes": len(completed.stdout.encode("utf-8")),
        "stderr_bytes": len(completed.stderr.encode("utf-8")),
        "json": payload,
        "status": payload.get("status") if isinstance(payload, dict) else None,
    }


def source_row(repo: Path, check: SourceCheck) -> dict[str, Any]:
    missing_files = [path for path in check.paths if not file_exists(repo, path)]
    corpus = "\n".join(read_text(repo / path) for path in check.paths)
    missing_tokens = [token for token in check.tokens if token not in corpus]
    status = "PASS" if not missing_files and not missing_tokens else "FAIL"
    return {
        "id": check.row_id,
        "label": check.label,
        "lane": check.evidence_lane,
        "status": status,
        "owner": check.owner,
        "paths": list(check.paths),
        "missing_files": missing_files,
        "missing_tokens": missing_tokens,
    }


def source_matrix(repo: Path) -> list[dict[str, Any]]:
    return [source_row(repo, check) for check in SOURCE_CHECKS]


def target_matrix(
    repo: Path,
    target: Path | None,
    current_host: str | None,
    host_loop_json: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if target is None:
        return (
            [
                {
                    "id": "installed-target-materialization",
                    "label": "Installed target hook materialization was not run.",
                    "lane": "target",
                    "status": "NOT_RUN",
                    "owner": "canary target",
                }
            ],
            {},
        )

    target = target.expanduser().resolve()
    rows: list[dict[str, Any]] = []
    config_paths = {
        "codex": ".codex/config.toml",
        "claude": ".claude/settings.json",
        "cursor": ".cursor/hooks.json",
    }
    for host, relpath in config_paths.items():
        text = read_text(target / relpath)
        rows.append(
            {
                "id": f"target-config-{host}",
                "label": f"{host} hook config exists and references tes_install.py hook.",
                "lane": "target",
                "status": "PASS" if "tes_install.py" in text and " hook" in text and f"--agent {host}" in text else "NEEDS_EVIDENCE",
                "owner": relpath,
                "path": relpath,
            }
        )

    for helper in ("cortex_runtime.py", "pretooluse_kernel.py", "pretooluse_session.py"):
        relpath = f".tes/bin/{helper}"
        rows.append(
            {
                "id": f"target-helper-{helper}",
                "label": f"{relpath} is installed.",
                "lane": "target",
                "status": "PASS" if (target / relpath).is_file() else "NEEDS_EVIDENCE",
                "owner": relpath,
                "path": relpath,
            }
        )

    hook_health: dict[str, Any] = {}
    hook_health_argv = [
        sys.executable,
        str(repo / "scripts" / "tes_install.py"),
        "hook-health",
        "--target",
        str(target),
        "--json-only",
        "--query",
    ]
    if current_host:
        hook_health_argv.extend(["--agent", current_host])
    if host_loop_json:
        hook_health_argv.extend(["--host-loop-json", str(host_loop_json)])
    hook_health = run_process(hook_health_argv, repo)
    hook_health_json = hook_health.get("json") if isinstance(hook_health.get("json"), dict) else {}

    rows.append(
        {
            "id": "target-hook-health-schema",
            "label": "Installed hook-health emits tes-hook-health@2.",
            "lane": "target",
            "status": "PASS" if hook_health_json.get("schema") == "tes-hook-health@2" else "NEEDS_EVIDENCE",
            "owner": "scripts/tes_install.py hook-health",
            "observed": hook_health_json.get("schema"),
        }
    )
    rows.append(
        {
            "id": "target-helper-contract",
            "label": "Installed hook-health sees helper_contract_status=PASS.",
            "lane": "target",
            "status": "PASS" if hook_health_json.get("helper_contract_status") == "PASS" else "NEEDS_EVIDENCE",
            "owner": ".tes/bin",
            "observed": hook_health_json.get("helper_contract_status"),
        }
    )
    rows.append(
        {
            "id": "target-floor-ceiling-visible",
            "label": "Installed hook-health exposes floor_status, ceiling_status, and ceiling_gaps.",
            "lane": "target",
            "status": "PASS"
            if all(key in hook_health_json for key in ("floor_status", "ceiling_status", "ceiling_gaps"))
            else "NEEDS_EVIDENCE",
            "owner": "scripts/tes_install.py hook-health",
            "observed": {
                "floor_status": hook_health_json.get("floor_status"),
                "ceiling_status": hook_health_json.get("ceiling_status"),
                "ceiling_gaps": hook_health_json.get("ceiling_gaps"),
            },
        }
    )
    rows.append(
        {
            "id": "target-runtime-ledger",
            "label": "Runtime hook ledger status is visible.",
            "lane": "target",
            "status": "PASS"
            if isinstance(hook_health_json.get("sentinels"), dict)
            and isinstance(hook_health_json["sentinels"].get("current"), dict)
            else "NEEDS_EVIDENCE",
            "owner": ".tes/runtime/hooks/executed.jsonl",
            "observed": hook_health_json.get("sentinels"),
        }
    )

    return rows, {"hook_health": hook_health}


def related_gates(
    repo: Path,
    target: Path | None,
    current_host: str | None,
    run: bool,
    host_loop_json: Path | None = None,
) -> dict[str, Any]:
    if not run:
        return {"status": "NOT_RUN", "gates": {}}
    gates: dict[str, Any] = {
        "tes-install-self-test": run_process([sys.executable, "scripts/tes_install.py", "--self-test"], repo),
        "pretooluse-contract": run_process([sys.executable, "scripts/pretooluse_contract_oracle.py", "--self-test"], repo),
        "hook-audit-prompt": run_process([sys.executable, "scripts/hook_audit_prompt_oracle.py", "--self-test"], repo),
    }
    if target is not None:
        hook_health = [sys.executable, "scripts/tes_install.py", "hook-health", "--target", str(target), "--json-only", "--query"]
        if current_host:
            hook_health.extend(["--agent", current_host])
        if host_loop_json:
            hook_health.extend(["--host-loop-json", str(host_loop_json)])
        gates["hook-health"] = run_process(hook_health, repo)
        canary_admission = [sys.executable, "scripts/canary_admission_oracle.py", "--target", str(target), "--json-only"]
        if current_host:
            canary_admission.extend(["--current-host", current_host])
        if host_loop_json:
            canary_admission.extend(["--host-loop-json", str(host_loop_json)])
        gates["canary-admission"] = run_process(canary_admission, repo)
        installed_certification = [
            sys.executable,
            "scripts/installed_certification_oracle.py",
            "--target",
            str(target),
            "--json-only",
        ]
        if current_host:
            installed_certification.extend(["--current-host", current_host])
        if host_loop_json:
            installed_certification.extend(["--host-loop-json", str(host_loop_json)])
        gates["installed-certification"] = run_process(installed_certification, repo)
    failed = [name for name, item in gates.items() if item.get("returncode") not in (0,)]
    # Installed target gates may intentionally return non-zero for host evidence
    # gaps; keep them visible without pretending the source contract failed.
    return {
        "status": "PASS" if not failed else "NEEDS_EVIDENCE",
        "gates": gates,
        "nonzero": failed,
    }


def load_json_file(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "FAIL", "blockers": [f"could not read parseable JSON: {path}"]}
    return data if isinstance(data, dict) else {"status": "FAIL", "blockers": [f"JSON root is not an object: {path}"]}


def transcript_session_id(transcript_path: Any) -> str:
    raw = str(transcript_path or "").strip()
    if not raw:
        return ""
    return Path(raw).stem


def read_runtime_hook_records(target: Path | None) -> list[dict[str, Any]]:
    if target is None:
        return []
    ledger = target / ".tes/runtime/hooks/executed.jsonl"
    if not ledger.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line in ledger.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return records


def host_runtime_rows(target: Path | None, current_host: str | None, host_loop_json: dict[str, Any] | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if target is None or current_host is None or host_loop_json is None:
        return rows
    oracle = host_loop_json.get("oracle") if isinstance(host_loop_json.get("oracle"), dict) else {}
    session_id = transcript_session_id(oracle.get("transcript_path"))
    records = [
        record
        for record in read_runtime_hook_records(target)
        if record.get("agent") == current_host
        and str(record.get("event_canonical") or record.get("event") or "") == "PreToolUse"
        and str(record.get("session") or "") == session_id
    ]
    host_real_records = [record for record in records if record.get("provenance") == "host-real"]
    supervised = [
        record
        for record in host_real_records
        if record.get("governed_surface") is True
        and record.get("outcome") == "supervise"
        and isinstance(record.get("renderer_trace"), dict)
        and record["renderer_trace"].get("output_contract")
    ]
    redacted_shell = [
        record
        for record in host_real_records
        if record.get("command_redacted") is True
        and str(record.get("command_category") or "") not in {"", "no_command"}
    ]
    rows.extend(
        [
            {
                "id": "host-runtime-session-correlated",
                "label": "Host runtime ledger has a host-real PreToolUse row for the transcript session.",
                "lane": "host",
                "status": "PASS" if host_real_records else "NEEDS_EVIDENCE",
                "owner": ".tes/runtime/hooks/executed.jsonl",
                "observed": {
                    "session": session_id,
                    "records": len(records),
                    "host_real_records": len(host_real_records),
                },
            },
            {
                "id": "host-runtime-governed-supervision",
                "label": "Host runtime ledger proves governed-surface supervision with renderer projection.",
                "lane": "host",
                "status": "PASS" if supervised else "NEEDS_EVIDENCE",
                "owner": ".tes/runtime/hooks/executed.jsonl",
                "observed": {
                    "session": session_id,
                    "records": len(supervised),
                    "outcomes": sorted({str(record.get("outcome") or "") for record in supervised}),
                },
            },
            {
                "id": "host-runtime-shell-redaction",
                "label": "Host runtime ledger proves shell command classification and redaction.",
                "lane": "host",
                "status": "PASS" if redacted_shell else "NEEDS_EVIDENCE",
                "owner": ".tes/runtime/hooks/executed.jsonl",
                "observed": {
                    "session": session_id,
                    "records": len(redacted_shell),
                    "command_categories": sorted({str(record.get("command_category") or "") for record in redacted_shell}),
                },
            },
        ]
    )
    return rows


def host_matrix(
    host_loop_json: dict[str, Any] | None,
    transcript_json: dict[str, Any] | None,
    *,
    target: Path | None = None,
    current_host: str | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if host_loop_json is None and transcript_json is None:
        return [
            {
                "id": "host-transcript-evidence",
                "label": "Host transcript evidence was not provided.",
                "lane": "host",
                "status": "NOT_RUN",
                "owner": "host_canary_loop.py",
            }
        ]

    if host_loop_json is not None:
        oracle = host_loop_json.get("oracle") if isinstance(host_loop_json.get("oracle"), dict) else {}
        rows.append(
            {
                "id": "host-loop-pass",
                "label": "host_canary_loop.py reported a passing, non-stale loop.",
                "lane": "host",
                "status": "PASS"
                if host_loop_json.get("loop_status") == "PASS" and host_loop_json.get("stale_transcript") is False
                else "NEEDS_EVIDENCE",
                "owner": "host_canary_loop.py",
                "observed": {
                    "loop_status": host_loop_json.get("loop_status"),
                    "stale_transcript": host_loop_json.get("stale_transcript"),
                    "command_fingerprint": host_loop_json.get("command_fingerprint"),
                },
            }
        )
        rows.append(
            {
                "id": "host-loop-oracle",
                "label": "Host loop contains transcript oracle hash and tool-use evidence.",
                "lane": "host",
                "status": "PASS"
                if oracle.get("status") == "PASS" and oracle.get("transcript_sha256") and int(oracle.get("tool_use_count") or 0) > 0
                else "NEEDS_EVIDENCE",
                "owner": "canary_transcript_oracle.py",
                "observed": {
                    "oracle_status": oracle.get("status"),
                    "transcript_sha256": oracle.get("transcript_sha256"),
                    "tool_use_count": oracle.get("tool_use_count"),
                },
            }
        )
        rows.extend(host_runtime_rows(target, current_host, host_loop_json))

    if transcript_json is not None:
        main = transcript_json.get("main") if isinstance(transcript_json.get("main"), dict) else {}
        rows.append(
            {
                "id": "host-transcript-oracle",
                "label": "canary_transcript_oracle.py passed with transcript hash and tool-use evidence.",
                "lane": "host",
                "status": "PASS"
                if transcript_json.get("status") == "PASS" and main.get("sha256") and int(main.get("tool_use_count") or 0) > 0
                else "NEEDS_EVIDENCE",
                "owner": "canary_transcript_oracle.py",
                "observed": {
                    "status": transcript_json.get("status"),
                    "sha256": main.get("sha256"),
                    "tool_use_count": main.get("tool_use_count"),
                },
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]], *, require_target: bool, require_host_transcript: bool) -> dict[str, Any]:
    by_lane: dict[str, dict[str, int]] = {}
    for row in rows:
        lane = str(row.get("lane") or "unknown")
        status = str(row.get("status") or "FAIL")
        by_lane.setdefault(lane, {status: 0 for status in STATUSES})
        by_lane[lane][status] = by_lane[lane].get(status, 0) + 1
    failed = [row["id"] for row in rows if row.get("status") == "FAIL"]
    evidence_gaps = [row["id"] for row in rows if row.get("status") == "NEEDS_EVIDENCE"]
    not_run = [row["id"] for row in rows if row.get("status") == "NOT_RUN"]
    if failed:
        status = "FAIL"
    elif evidence_gaps:
        status = "NEEDS_EVIDENCE"
    elif require_target and any(row.get("lane") == "target" and row.get("status") == "NOT_RUN" for row in rows):
        status = "NEEDS_EVIDENCE"
    elif require_host_transcript and any(row.get("lane") == "host" and row.get("status") == "NOT_RUN" for row in rows):
        status = "NEEDS_EVIDENCE"
    else:
        status = "PASS"
    return {
        "status": status,
        "by_lane": by_lane,
        "failed": failed,
        "evidence_gaps": evidence_gaps,
        "not_run": not_run,
    }


def decision(summary: dict[str, Any], *, target: Path | None, host_rows: list[dict[str, Any]]) -> str:
    if summary["status"] == "FAIL":
        return "FAIL"
    if summary["status"] == "NEEDS_EVIDENCE":
        return "NEEDS_EVIDENCE"
    if target is None:
        return "SOURCE_CERTIFIED"
    if all(row.get("lane") != "host" or row.get("status") == "NOT_RUN" for row in host_rows):
        return "TARGET_CERTIFIED"
    host_ceiling_ids = {
        "host-runtime-session-correlated",
        "host-runtime-governed-supervision",
        "host-runtime-shell-redaction",
    }
    host_ceiling_statuses = {
        str(row.get("id")): str(row.get("status"))
        for row in host_rows
        if row.get("id") in host_ceiling_ids
    }
    if host_ceiling_statuses and all(host_ceiling_statuses.get(row_id) == "PASS" for row_id in host_ceiling_ids):
        return "HOST_CEILING_CERTIFIED"
    return "HOST_CERTIFIED"


def build_matrix(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo.expanduser().resolve()
    target = args.target.expanduser().resolve() if args.target else None
    source_rows = source_matrix(repo)
    target_rows, target_evidence = target_matrix(repo, target, args.current_host, args.host_loop_json)
    host_loop_json = load_json_file(args.host_loop_json)
    transcript_json = load_json_file(args.transcript_oracle_json)
    host_rows = host_matrix(host_loop_json, transcript_json, target=target, current_host=args.current_host)
    rows = [*source_rows, *target_rows, *host_rows]
    summary = summarize(rows, require_target=args.require_target, require_host_transcript=args.require_host_transcript)
    gates = related_gates(repo, target, args.current_host, args.run_related_gates, args.host_loop_json)
    status = summary["status"]
    matrix_decision = decision(summary, target=target, host_rows=host_rows)
    if gates.get("status") == "NEEDS_EVIDENCE" and status == "PASS":
        status = "NEEDS_EVIDENCE"
        matrix_decision = "CERTIFIED_WITH_RESIDUALS" if target is not None else "NEEDS_EVIDENCE"
    return {
        "schema": SCHEMA,
        "skill_contract": SKILL_CONTRACT,
        "status": status,
        "decision": matrix_decision,
        "repo": str(repo),
        "target": str(target) if target else None,
        "current_host": args.current_host,
        "summary": summary,
        "rows": rows,
        "target_evidence": target_evidence,
        "related_gates": gates,
    }


def self_test(repo: Path) -> dict[str, Any]:
    failures: list[str] = []
    source_only_args = argparse.Namespace(
        repo=repo,
        target=None,
        current_host=None,
        host_loop_json=None,
        transcript_oracle_json=None,
        run_related_gates=False,
        require_target=False,
        require_host_transcript=False,
    )
    result = build_matrix(source_only_args)
    if result.get("status") != "PASS":
        failures.append("source-only matrix should pass in the TES package root")
    if result.get("decision") != "SOURCE_CERTIFIED":
        failures.append("source-only matrix should decide SOURCE_CERTIFIED")
    if len(result.get("rows", [])) < len(SOURCE_CHECKS):
        failures.append("matrix omitted source rows")

    required_host_args = argparse.Namespace(
        repo=repo,
        target=None,
        current_host=None,
        host_loop_json=None,
        transcript_oracle_json=None,
        run_related_gates=False,
        require_target=False,
        require_host_transcript=True,
    )
    required_host = build_matrix(required_host_args)
    if required_host.get("status") != "NEEDS_EVIDENCE":
        failures.append("required host transcript without evidence should be NEEDS_EVIDENCE")

    return {
        "schema": SCHEMA,
        "skill_contract": SKILL_CONTRACT,
        "status": "PASS" if not failures else "FAIL",
        "rows": len(SOURCE_CHECKS),
        "coverage": [
            "source feature matrix",
            "target materialization lane",
            "host transcript lane",
            "related gate launcher",
            "required evidence semantics",
        ],
        "failures": failures,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a TES agent-hook certification matrix.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--target", type=Path)
    parser.add_argument("--current-host", choices=("codex", "claude", "cursor"))
    parser.add_argument("--host-loop-json", type=Path, help="Sanitized JSON output from host_canary_loop.py.")
    parser.add_argument("--transcript-oracle-json", type=Path, help="Sanitized JSON output from canary_transcript_oracle.py.")
    parser.add_argument("--run-related-gates", action="store_true")
    parser.add_argument("--require-target", action="store_true")
    parser.add_argument("--require-host-transcript", action="store_true")
    parser.add_argument("--json-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo = args.repo.expanduser().resolve()
    if args.self_test:
        result = self_test(repo)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "PASS" else 1

    result = build_matrix(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json_only:
        print(f"[agent-hooks-certification] {result['status']} decision={result['decision']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
