#!/usr/bin/env python3
"""Certify Cortex consolidation only after observed authorized writes."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Any

import cortex
import scope_contract


VERSION = "0.3.134"
SCHEMA = "tes-consolidation-gate@1"
LOCK_ROOT = Path(".tes/cortex/consolidation")
SAFE_TOKEN = re.compile(r"[^a-zA-Z0-9_.:-]+")
ISO_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
ALLOWED_REVIEW_STATUSES = ("APPROVED", "REJECTED", "NEEDS_REVIEW")
ALLOWED_DERIVED_WRITES = {".tes/cortex/recall.sqlite"}
ALLOWED_CORTEX_FILES = {
    "docs/agents/cortex/MAP.md",
    "docs/agents/cortex/LINKS.md",
    "docs/agents/cortex/TRAIL.md",
}
FORBIDDEN_EVIDENCE_PREFIXES = (".tes/events/", ".tes/checkpoints/")
FORBIDDEN_WRITE_PREFIXES = (
    ".tes/events/",
    ".tes/checkpoints/",
    ".tes/field-reports/",
    "docs/agents/cortex/sources/",
)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def safe_token(value: object, default: str, *, limit: int = 80) -> str:
    token = SAFE_TOKEN.sub("-", str(value or "").strip()).strip("-._:")
    return token[:limit] if token else default


def root_path(target: Path) -> Path:
    return target / LOCK_ROOT


def lock_id(value: object) -> str:
    return safe_token(value, "consolidation")


def lock_path(target: Path, value: object) -> Path:
    return root_path(target) / f"{lock_id(value)}.lock.json"


def authority_block() -> dict[str, object]:
    return {
        "automatic_promotion": False,
        "durable_memory_write": False,
        "forget_enabled": False,
        "rule": "consolidation-lock",
    }


def normalize_relative_path(raw: object, failures: list[str], *, label: str) -> str:
    value = str(raw or "").strip().replace("\\", "/")
    if not value:
        failures.append(f"{label} is required")
        return ""
    if value.startswith("/") or value.startswith("~") or re.match(r"^[A-Za-z]:/", value):
        failures.append(f"{label} must be relative to the target")
    parts = Path(value).parts
    if ".." in parts:
        failures.append(f"{label} must not traverse outside the target")
    if value.startswith("./"):
        value = value[2:]
    return value


def resolve_input_file(target: Path, raw: object, failures: list[str], *, label: str) -> Path | None:
    relpath = normalize_relative_path(raw, failures, label=label)
    if not relpath:
        return None
    path = target / relpath
    try:
        path.resolve().relative_to(target)
    except ValueError:
        failures.append(f"{label} resolves outside the target")
        return None
    if not path.is_file():
        failures.append(f"{label} is missing: {relpath}")
        return None
    return path


def read_json_file(path: Path, failures: list[str], *, label: str) -> dict[str, object] | None:
    try:
        raw = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        failures.append(f"{label} JSON is malformed")
        return None
    if not isinstance(raw, dict):
        failures.append(f"{label} payload must be an object")
        return None
    return raw


def normalize_evidence_refs(evidence: list[str], failures: list[str]) -> list[str]:
    if not evidence:
        failures.append("at least one source or evidence ref is required")
        return []
    normalized: list[str] = []
    for raw in evidence:
        ref, ref_failures = scope_contract.normalize_evidence_ref(raw)
        failures.extend(ref_failures)
        if ref == "none":
            failures.append("consolidation evidence cannot be none")
        if ref.startswith(FORBIDDEN_EVIDENCE_PREFIXES):
            failures.append("event or checkpoint evidence cannot certify durable memory")
        normalized.append(ref)
    return normalized


def validate_lock_payload(target: Path, raw: dict[str, object], lock_file: Path) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    if raw.get("schema") != SCHEMA:
        failures.append("lock schema mismatch")
    if str(raw.get("status", "")).upper() != "LOCKED":
        failures.append("consolidation lock must be LOCKED")
    created_at = str(raw.get("created_at", "")).strip()
    if not ISO_UTC.match(created_at):
        failures.append("lock created_at must be UTC ISO-8601 seconds with Z suffix")
        created_at = "1970-01-01T00:00:00Z"
    expected_authority = authority_block()
    authority = raw.get("authority")
    if not isinstance(authority, dict):
        failures.append("consolidation lock authority block is missing")
        authority = expected_authority
    for key, expected in expected_authority.items():
        if authority.get(key) != expected:
            failures.append(f"consolidation authority must keep {key}={expected}")
    evidence_ref, evidence_failures = scope_contract.normalize_evidence_ref(raw.get("evidence_ref", "none"))
    failures.extend(evidence_failures)
    lock = {
        "schema": SCHEMA,
        "id": lock_id(raw.get("id", lock_file.stem.replace(".lock", ""))),
        "path": rel(lock_file, target),
        "status": str(raw.get("status", "INVALID")).upper(),
        "created_at": created_at,
        "summary": str(raw.get("summary") or "none"),
        "evidence_ref": evidence_ref if not evidence_failures else "invalid",
        "authority": expected_authority,
        "valid": not failures,
    }
    return lock, failures


def create_lock(
    target: Path,
    *,
    lock_id_value: str,
    summary: str,
    evidence_ref: str,
    authorized: bool,
    replace: bool = False,
) -> dict[str, object]:
    target = target.expanduser().resolve()
    path = lock_path(target, lock_id_value)
    if not authorized:
        return {
            "version": VERSION,
            "schema": SCHEMA,
            "status": "NEEDS_AUTH",
            "lock_path": rel(path, target),
            "writes": [],
            "message": "consolidation lock requires --yes before writing .tes/cortex/consolidation/**",
        }
    failures: list[str] = []
    evidence, evidence_failures = scope_contract.normalize_evidence_ref(evidence_ref)
    failures.extend(evidence_failures)
    if evidence == "none":
        failures.append("lock evidence_ref cannot be none")
    payload = {
        "schema": SCHEMA,
        "id": lock_id(lock_id_value),
        "created_at": utc_stamp(),
        "status": "LOCKED",
        "summary": summary or "Cortex consolidation lock.",
        "evidence_ref": evidence if not evidence_failures else "invalid",
        "authority": authority_block(),
    }
    writes: list[str] = []
    if path.exists() and not replace:
        failures.append("consolidation lock already exists; pass --replace to update lock state")
    if not failures:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        writes.append(rel(path, target))
    return {
        "version": VERSION,
        "schema": SCHEMA,
        "status": "FAIL" if failures else "PASS",
        "lock": payload,
        "lock_path": rel(path, target),
        "failures": failures,
        "writes": writes,
        "durable_memory_write": False,
        "certification_evidence": False,
    }


def read_lock(target: Path, lock_id_value: str, failures: list[str]) -> dict[str, object] | None:
    path = lock_path(target, lock_id_value)
    if not path.is_file():
        failures.append(f"consolidation lock missing: {rel(path, target)}")
        return None
    raw = read_json_file(path, failures, label="consolidation lock")
    if raw is None:
        return None
    lock, lock_failures = validate_lock_payload(target, raw, path)
    failures.extend(lock_failures)
    return lock


def observed_write_paths(raw: object, failures: list[str]) -> list[str]:
    if not isinstance(raw, list):
        failures.append("observed write result must contain writes[]")
        return []
    paths: list[str] = []
    for item in raw:
        path = normalize_relative_path(item, failures, label="observed write path")
        if path:
            paths.append(path)
    return paths


def validate_observed_write(raw: dict[str, object]) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    if str(raw.get("status", "")).upper() != "PASS":
        failures.append("observed write status must be PASS")
    if raw.get("schema") == "tes-checkpoint@1" or "checkpoint_path" in raw:
        failures.append("checkpoint-only state cannot certify durable memory")
    if raw.get("schema") == "tes-event-ledger@1":
        failures.append("event-ledger records cannot certify durable memory")
    operator = str(raw.get("operator") or raw.get("command") or "").strip()
    if operator == "remember" and raw.get("mutability_class") != "durable-memory-write":
        failures.append("remember observations must report durable-memory-write mutability")
    if operator in {"checkpoint", "forget"}:
        failures.append(f"{operator} observations cannot certify durable memory")
    scope = raw.get("scope")
    if isinstance(scope, dict) and (scope.get("parent_agent") or str(scope.get("agent", "")).startswith("subagent")):
        failures.append("subagent observations cannot directly certify durable memory")
    if str(raw.get("agent_role", "")).lower() == "subagent":
        failures.append("subagent observations cannot directly certify durable memory")

    writes = observed_write_paths(raw.get("writes"), failures)
    if not writes:
        failures.append("observed write result has no writes")
    cell_writes = [path for path in writes if path.startswith("docs/agents/cortex/cells/") and path.endswith(".md")]
    if not cell_writes:
        failures.append("observed write must include at least one Cortex cell write")
    for required in ALLOWED_CORTEX_FILES:
        if required not in writes:
            failures.append(f"observed write must include {required}")
    for path in writes:
        if path.startswith(FORBIDDEN_WRITE_PREFIXES):
            failures.append(f"forbidden consolidation write surface: {path}")
        allowed = (
            path in ALLOWED_CORTEX_FILES
            or path in ALLOWED_DERIVED_WRITES
            or (path.startswith("docs/agents/cortex/cells/") and path.endswith(".md"))
        )
        if not allowed:
            failures.append(f"observed write outside Cortex consolidation surface: {path}")
    return {
        "operator": operator or "unknown",
        "write_count": len(writes),
        "cell_writes": cell_writes,
        "writes": writes,
        "valid": not failures,
    }, failures


def review_status(raw: str, failures: list[str]) -> str:
    status = str(raw or "").strip().upper()
    if status not in ALLOWED_REVIEW_STATUSES:
        failures.append("review_status must be APPROVED, REJECTED, or NEEDS_REVIEW")
        return "NEEDS_REVIEW"
    if status != "APPROVED":
        failures.append(f"review_status is {status}; consolidation needs approval")
    return status


def validate_rollback_ref(raw: str, failures: list[str]) -> str:
    value = str(raw or "").strip()
    if not value or value == "none":
        failures.append("rollback_ref is required")
        return "none"
    if "\n" in value or "\r" in value:
        failures.append("rollback_ref must be a single line")
    if value.startswith(FORBIDDEN_EVIDENCE_PREFIXES):
        failures.append("event or checkpoint state cannot be rollback evidence")
    if not (value.startswith("git:") or value.startswith("manual:")):
        failures.append("rollback_ref must start with git: or manual:")
    return value


def certify(
    target: Path,
    *,
    lock_id_value: str,
    observed_write_ref: str,
    review_status_value: str,
    rollback_ref: str,
    evidence: list[str],
) -> dict[str, object]:
    target = target.expanduser().resolve()
    failures: list[str] = []
    lock = read_lock(target, lock_id_value, failures)
    observed_path = resolve_input_file(target, observed_write_ref, failures, label="observed_write")
    observed_payload = read_json_file(observed_path, failures, label="observed_write") if observed_path else None
    observed_summary: dict[str, object] | None = None
    if observed_payload is not None:
        observed_summary, observed_failures = validate_observed_write(observed_payload)
        failures.extend(observed_failures)
    normalized_evidence = normalize_evidence_refs(evidence, failures)
    review = review_status(review_status_value, failures)
    rollback = validate_rollback_ref(rollback_ref, failures)
    status = "CERTIFIED" if not failures else "BLOCKED"
    if review != "APPROVED":
        status = "NEEDS_REVIEW"
    return {
        "version": VERSION,
        "schema": SCHEMA,
        "status": status,
        "lock": lock,
        "review_status": review,
        "rollback_ref": rollback,
        "evidence": normalized_evidence,
        "observed_write": observed_summary,
        "failures": failures,
        "writes": [],
        "durable_memory_write": False,
        "certification_evidence": status == "CERTIFIED",
    }


def inspect_schema() -> dict[str, object]:
    return {
        "version": VERSION,
        "schema": SCHEMA,
        "lock_root": LOCK_ROOT.as_posix(),
        "lock_authority": authority_block(),
        "review_statuses": list(ALLOWED_REVIEW_STATUSES),
        "allowed_writes": sorted([*ALLOWED_CORTEX_FILES, *ALLOWED_DERIVED_WRITES, "docs/agents/cortex/cells/*.md"]),
        "writes": [],
    }


def snapshot(target: Path) -> dict[str, str]:
    if not target.exists():
        return {}
    return {
        rel(path, target): sha256_bytes(path.read_bytes())
        for path in sorted(target.rglob("*"))
        if path.is_file()
    }


def changed_paths(before: dict[str, str], after: dict[str, str]) -> list[str]:
    keys = set(before) | set(after)
    return sorted(path for path in keys if before.get(path) != after.get(path))


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-consolidation-") as tempdir:
        target = Path(tempdir) / "target-project"
        cortex.init(target)
        source = cortex.cortex_path(target) / "sources" / "consolidation-source.md"
        source.write_text("# Consolidation Source\n\nDurable memory writes need observed certification.\n", encoding="utf-8")

        before_blocked = snapshot(target)
        blocked_lock = create_lock(
            target,
            lock_id_value="wave",
            summary="Consolidate observed memory.",
            evidence_ref="sources/consolidation-source.md",
            authorized=False,
        )
        after_blocked = snapshot(target)
        if blocked_lock.get("status") != "NEEDS_AUTH" or blocked_lock.get("writes") != []:
            failures.append("unauthorized consolidation lock must be NEEDS_AUTH with no writes")
        if before_blocked != after_blocked:
            failures.append("unauthorized consolidation lock mutated files")

        before_lock = snapshot(target)
        lock = create_lock(
            target,
            lock_id_value="wave",
            summary="Consolidate observed memory.",
            evidence_ref="sources/consolidation-source.md",
            authorized=True,
        )
        after_lock = snapshot(target)
        if lock.get("status") != "PASS":
            failures.append(f"authorized consolidation lock should pass: {lock.get('failures')}")
        if changed_paths(before_lock, after_lock) != [".tes/cortex/consolidation/wave.lock.json"]:
            failures.append(f"consolidation lock wrote unexpected files: {changed_paths(before_lock, after_lock)}")

        observed = cortex.remember(
            target,
            "consolidated-memory",
            "Consolidated memory requires approval, evidence, rollback, and observed writes.",
            ["sources/consolidation-source.md"],
            "Observed consolidation write.",
            [],
            authorized=True,
            update_existing=False,
        )
        observed_path = target / ".tes/cortex/consolidation/observed.json"
        write_json(observed_path, observed)
        certified = certify(
            target,
            lock_id_value="wave",
            observed_write_ref=".tes/cortex/consolidation/observed.json",
            review_status_value="APPROVED",
            rollback_ref="git:abcdef0",
            evidence=["sources/consolidation-source.md"],
        )
        if certified.get("status") != "CERTIFIED":
            failures.append(f"valid consolidation should certify: {certified.get('failures')}")
        if certified.get("writes") != []:
            failures.append("certify must be read-only")

        no_lock = certify(
            target,
            lock_id_value="missing",
            observed_write_ref=".tes/cortex/consolidation/observed.json",
            review_status_value="APPROVED",
            rollback_ref="git:abcdef0",
            evidence=["sources/consolidation-source.md"],
        )
        if no_lock.get("status") != "BLOCKED":
            failures.append("missing lock must block consolidation")

        review_rejected = certify(
            target,
            lock_id_value="wave",
            observed_write_ref=".tes/cortex/consolidation/observed.json",
            review_status_value="REJECTED",
            rollback_ref="git:abcdef0",
            evidence=["sources/consolidation-source.md"],
        )
        if review_rejected.get("status") != "NEEDS_REVIEW":
            failures.append("rejected review must stay NEEDS_REVIEW")

        event_only_path = target / ".tes/cortex/consolidation/event-only.json"
        write_json(event_only_path, {"schema": "tes-event-ledger@1", "status": "PASS", "writes": [".tes/events/ledger.jsonl"]})
        event_only = certify(
            target,
            lock_id_value="wave",
            observed_write_ref=".tes/cortex/consolidation/event-only.json",
            review_status_value="APPROVED",
            rollback_ref="git:abcdef0",
            evidence=["sources/consolidation-source.md"],
        )
        if event_only.get("status") != "BLOCKED":
            failures.append("event-only evidence must block consolidation")

        checkpoint_only_path = target / ".tes/cortex/consolidation/checkpoint-only.json"
        checkpoint_only = cortex.checkpoint_operator(
            target,
            checkpoint_id="consolidation",
            ttl_seconds=60,
            summary="Checkpoint only.",
            state={"phase": "wave"},
            authorized=True,
        )
        write_json(checkpoint_only_path, checkpoint_only)
        checkpoint_result = certify(
            target,
            lock_id_value="wave",
            observed_write_ref=".tes/cortex/consolidation/checkpoint-only.json",
            review_status_value="APPROVED",
            rollback_ref="git:abcdef0",
            evidence=["sources/consolidation-source.md"],
        )
        if checkpoint_result.get("status") != "BLOCKED":
            failures.append("checkpoint-only state must block consolidation")

        subagent_path = target / ".tes/cortex/consolidation/subagent.json"
        subagent = dict(observed)
        subagent["scope"] = {"agent": "subagent-worker", "parent_agent": "maestro"}
        write_json(subagent_path, subagent)
        subagent_result = certify(
            target,
            lock_id_value="wave",
            observed_write_ref=".tes/cortex/consolidation/subagent.json",
            review_status_value="APPROVED",
            rollback_ref="git:abcdef0",
            evidence=["sources/consolidation-source.md"],
        )
        if subagent_result.get("status") != "BLOCKED":
            failures.append("subagent direct memory write must block consolidation")

        stale_lock_path = lock_path(target, "wave")
        stale_lock = json.loads(stale_lock_path.read_text(encoding="utf-8"))
        stale_lock["status"] = "STALE"
        stale_lock_path.write_text(json.dumps(stale_lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        stale_result = certify(
            target,
            lock_id_value="wave",
            observed_write_ref=".tes/cortex/consolidation/observed.json",
            review_status_value="APPROVED",
            rollback_ref="git:abcdef0",
            evidence=["sources/consolidation-source.md"],
        )
        if stale_result.get("status") != "BLOCKED":
            failures.append("stale or non-LOCKED consolidation lock must block")

    result = {"version": VERSION, "schema": SCHEMA, "status": "FAIL" if failures else "PASS", "failures": failures}
    print(json.dumps(result, indent=2, sort_keys=True))
    if failures:
        print("[consolidation-gate] FAIL")
        return 1
    print("[consolidation-gate] PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate Cortex consolidation with observed-write evidence.")
    parser.add_argument("command", nargs="?", choices=("lock", "certify", "inspect-schema"))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--target", type=Path, default=Path("."))
    parser.add_argument("--id", default="consolidation")
    parser.add_argument("--summary", default="")
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--observed-write", default="")
    parser.add_argument("--review-status", default="NEEDS_REVIEW")
    parser.add_argument("--rollback-ref", default="")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if args.command == "lock":
        result = create_lock(
            args.target,
            lock_id_value=args.id,
            summary=args.summary,
            evidence_ref=args.evidence[0] if args.evidence else "none",
            authorized=args.yes,
            replace=args.replace,
        )
    elif args.command == "certify":
        result = certify(
            args.target,
            lock_id_value=args.id,
            observed_write_ref=args.observed_write,
            review_status_value=args.review_status,
            rollback_ref=args.rollback_ref,
            evidence=args.evidence,
        )
    elif args.command == "inspect-schema":
        result = inspect_schema()
    else:
        parser.error("command is required unless --self-test is used")

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") in {"PASS", "CERTIFIED"} or args.command == "inspect-schema" else 1


if __name__ == "__main__":
    raise SystemExit(main())
