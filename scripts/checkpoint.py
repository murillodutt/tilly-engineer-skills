#!/usr/bin/env python3
"""Manage TES resumability checkpoints without writing durable memory."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Any

import scope_contract


VERSION = "0.3.186"
SCHEMA = "tes-checkpoint@1"
CHECKPOINT_ROOT = Path(".tes/checkpoints")
DEFAULT_TTL_SECONDS = 24 * 60 * 60
MAX_TTL_SECONDS = 7 * 24 * 60 * 60
RESUME_STATUSES = ("RESUMABLE", "EXPIRED", "MISSING", "INVALID")
SAFE_TOKEN = re.compile(r"[^a-zA-Z0-9_.:-]+")
ISO_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
ABSOLUTE_PATH = re.compile(r"(/Users|/home|/private|/var/folders|/absolute|[A-Za-z]:\\)[^\s`\"')]+")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL = re.compile(r"https?://[^\s`\"')]+")
SECRET = re.compile(
    r"(?i)(api[_-]?key|authorization|bearer|credential|password|secret|token)\s*[:=]?\s*[A-Za-z0-9._:/+=-]+"
)
STACK_TRACE = re.compile(r"(?i)(traceback \(most recent call last\)|\bat .+:\d+:\d+|exception: .+)")
SYNTHETIC_EMAIL = "person" + "@example.com"
SYNTHETIC_SECRET_VALUE = "abc" + "123"
SYNTHETIC_BEARER_SECRET = "Bearer " + SYNTHETIC_SECRET_VALUE
SYNTHETIC_SECRET_ASSIGNMENT = "token=" + SYNTHETIC_SECRET_VALUE
SYNTHETIC_PRIVATE_URL = "https://" + "private." + "example.test"
SYNTHETIC_PRIVATE_REPO_URL = SYNTHETIC_PRIVATE_URL + "/repo"
FORBIDDEN_OUTPUT = (
    "/absolute/unsafe",
    "/Users/",
    SYNTHETIC_EMAIL,
    SYNTHETIC_BEARER_SECRET,
    SYNTHETIC_SECRET_ASSIGNMENT,
    SYNTHETIC_PRIVATE_URL,
    "Traceback (most recent call last):",
)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def root_path(target: Path) -> Path:
    return target / CHECKPOINT_ROOT


def safe_token(value: object, default: str, *, limit: int = 80) -> str:
    token = SAFE_TOKEN.sub("-", str(value or "").strip()).strip("-._:")
    return token[:limit] if token else default


def checkpoint_id(value: object, *, summary: object = "", now: object = "") -> str:
    if value not in (None, ""):
        return safe_token(value, "checkpoint")
    digest = sha256_text(f"{summary}|{now}")[:12]
    return f"checkpoint-{digest}"


def checkpoint_path(target: Path, value: object) -> Path:
    return root_path(target) / f"{checkpoint_id(value)}.json"


def parse_stamp(value: object) -> tuple[datetime | None, list[str]]:
    raw = str(value or "").strip()
    if not ISO_UTC.match(raw):
        return None, ["timestamp must be UTC ISO-8601 seconds with Z suffix"]
    return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc), []


def normalize_now(value: object | None = None) -> tuple[str, datetime, list[str]]:
    raw = str(value or utc_stamp()).strip()
    parsed, failures = parse_stamp(raw)
    if parsed is None:
        parsed = datetime(1970, 1, 1, tzinfo=timezone.utc)
    return raw, parsed, failures


def stamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def unsafe_value(value: object) -> bool:
    raw = str(value or "")
    return any(pattern.search(raw) for pattern in (SECRET, EMAIL, URL, ABSOLUTE_PATH, STACK_TRACE)) or "\n" in raw


def sanitize_value(value: object) -> str:
    raw = str(value or "")
    if "\n" in raw or STACK_TRACE.search(raw):
        return f"redacted:{sha256_text(raw)[:12]}"
    sanitized = raw
    for pattern in (SECRET, EMAIL, URL, ABSOLUTE_PATH):
        sanitized = pattern.sub("[redacted]", sanitized)
    sanitized = sanitized.replace("`", "'").replace("|", "/").strip()
    if len(sanitized) > 180:
        return f"redacted:{sha256_text(sanitized)[:12]}"
    return sanitized or "none"


def sanitize_state(value: object, failures: list[str]) -> dict[str, str]:
    if value in (None, ""):
        return {}
    if not isinstance(value, dict):
        failures.append("state must be an object")
        return {}
    sanitized: dict[str, str] = {}
    for key, item in sorted(value.items()):
        safe_key = safe_token(key, "field").lower()
        if unsafe_value(key) or unsafe_value(item):
            failures.append(f"unsafe state redacted: {safe_key}")
        sanitized[safe_key] = sanitize_value(item)
    return sanitized


def authority_block() -> dict[str, object]:
    return {
        "automatic_promotion": False,
        "certification_evidence": False,
        "durable_memory_write": False,
        "rule": "checkpoint-only",
    }


def validate_authority(raw: object, failures: list[str]) -> dict[str, object]:
    expected = authority_block()
    if not isinstance(raw, dict):
        failures.append("checkpoint authority block is missing")
        return expected
    for key, expected_value in expected.items():
        if raw.get(key) != expected_value:
            failures.append(f"checkpoint authority must keep {key}={expected_value}")
    return expected


def validate_scope(target: Path, raw_scope: object, raw_checkpoint: dict[str, object], failures: list[str]) -> dict[str, object]:
    if not isinstance(raw_scope, dict):
        failures.append("checkpoint scope must be an object")
        raw_scope = {}
    scope_result = scope_contract.normalize_scope(
        target,
        project=raw_scope.get("project"),
        adapter=raw_scope.get("adapter", raw_checkpoint.get("adapter", "checkpoint")),
        agent=raw_scope.get("agent", raw_checkpoint.get("agent", "checkpoint")),
        parent_agent=raw_scope.get("parent_agent"),
        run=raw_scope.get("run", raw_checkpoint.get("id")),
        source=raw_scope.get("source", "checkpoint"),
        evidence_ref=raw_scope.get("evidence_ref", raw_checkpoint.get("evidence_ref", "none")),
        timestamp=raw_scope.get("timestamp", raw_checkpoint.get("created_at")),
        status=raw_scope.get("status", raw_checkpoint.get("resume_status", "RESUMABLE")),
        trust_level=raw_scope.get("trust_level"),
    )
    if scope_result.get("status") != "PASS":
        failures.extend(str(item) for item in scope_result.get("failures", []))
    scope = scope_result.get("scope", {})
    return scope if isinstance(scope, dict) else {}


def normalize_ttl(value: object) -> tuple[int, list[str]]:
    failures: list[str] = []
    try:
        ttl = int(value)
    except (TypeError, ValueError):
        return DEFAULT_TTL_SECONDS, ["ttl_seconds must be an integer"]
    if ttl <= 0:
        failures.append("ttl_seconds must be positive")
        ttl = DEFAULT_TTL_SECONDS
    if ttl > MAX_TTL_SECONDS:
        failures.append("ttl_seconds exceeds maximum checkpoint TTL")
        ttl = MAX_TTL_SECONDS
    return ttl, failures


def build_checkpoint(
    target: Path,
    *,
    checkpoint_id_value: object,
    ttl_seconds: object,
    summary: object,
    adapter: object,
    agent: object,
    parent_agent: object,
    run: object,
    source: object,
    evidence_ref: object,
    status_value: object,
    state: object,
    now_value: object | None = None,
) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    now_raw, now, now_failures = normalize_now(now_value)
    failures.extend(now_failures)
    ttl, ttl_failures = normalize_ttl(ttl_seconds)
    failures.extend(ttl_failures)
    expires_at = stamp(now + timedelta(seconds=ttl))
    cid = checkpoint_id(checkpoint_id_value, summary=summary, now=now_raw)
    if unsafe_value(summary):
        failures.append("summary contained unsafe private context")
    evidence, evidence_failures = scope_contract.normalize_evidence_ref(evidence_ref)
    failures.extend(evidence_failures)
    if evidence_failures:
        evidence = "invalid"
    sanitized_state = sanitize_state(state, failures)
    scope_result = scope_contract.normalize_scope(
        target,
        adapter=adapter or "checkpoint",
        agent=agent or "checkpoint",
        parent_agent=parent_agent,
        run=run or cid,
        source=source or "checkpoint",
        evidence_ref=evidence,
        timestamp=now_raw,
        status=status_value or "RESUMABLE",
    )
    if scope_result.get("status") != "PASS":
        failures.extend(str(item) for item in scope_result.get("failures", []))
    scope = scope_result.get("scope", {})
    payload = {
        "schema": SCHEMA,
        "id": cid,
        "created_at": now_raw,
        "expires_at": expires_at,
        "ttl_seconds": ttl,
        "resume_status": "RESUMABLE",
        "summary": sanitize_value(summary),
        "evidence_ref": evidence,
        "scope": scope if isinstance(scope, dict) else {},
        "state": sanitized_state,
        "authority": authority_block(),
    }
    return payload, failures


def create_checkpoint(
    target: Path,
    *,
    checkpoint_id_value: object,
    ttl_seconds: object,
    summary: object,
    adapter: object = "checkpoint",
    agent: object = "checkpoint",
    parent_agent: object = None,
    run: object = None,
    source: object = "checkpoint",
    evidence_ref: object = "none",
    status_value: object = "RESUMABLE",
    state: object = None,
    replace: bool = False,
    now_value: object | None = None,
) -> dict[str, object]:
    target = target.expanduser().resolve()
    payload, failures = build_checkpoint(
        target,
        checkpoint_id_value=checkpoint_id_value,
        ttl_seconds=ttl_seconds,
        summary=summary,
        adapter=adapter,
        agent=agent,
        parent_agent=parent_agent,
        run=run,
        source=source,
        evidence_ref=evidence_ref,
        status_value=status_value,
        state=state,
        now_value=now_value,
    )
    path = checkpoint_path(target, payload.get("id"))
    writes: list[str] = []
    if path.exists() and not replace:
        failures.append("checkpoint already exists; pass --replace to overwrite checkpoint state")
    if not failures:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        writes.append(rel(path, target))
    return {
        "version": VERSION,
        "schema": SCHEMA,
        "status": "FAIL" if failures else "PASS",
        "checkpoint": payload,
        "checkpoint_path": rel(path, target),
        "resume_status": "INVALID" if failures else "RESUMABLE",
        "failures": failures,
        "writes": writes,
        "durable_memory_write": False,
        "certification_evidence": False,
    }


def read_json(path: Path) -> tuple[dict[str, object] | None, list[str]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None, ["checkpoint JSON is malformed"]
    if not isinstance(raw, dict):
        return None, ["checkpoint payload must be an object"]
    return raw, []


def validate_checkpoint(target: Path, path: Path, now_value: object | None = None) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    raw, read_failures = read_json(path)
    if raw is None:
        return {
            "schema": SCHEMA,
            "id": path.stem,
            "path": rel(path, target),
            "resume_status": "INVALID",
            "valid": False,
            "summary": "invalid",
            "scope": {},
            "state": {},
            "authority": authority_block(),
        }, read_failures
    failures.extend(read_failures)
    if raw.get("schema") != SCHEMA:
        failures.append("checkpoint schema mismatch")
    cid = safe_token(raw.get("id"), path.stem)
    created_at = str(raw.get("created_at", "")).strip()
    expires_at = str(raw.get("expires_at", "")).strip()
    if not ISO_UTC.match(created_at):
        failures.append("checkpoint created_at must be UTC ISO-8601 seconds with Z suffix")
        created_at = "1970-01-01T00:00:00Z"
    expires, expires_failures = parse_stamp(expires_at)
    failures.extend(f"expires_at {failure}" for failure in expires_failures)
    ttl, ttl_failures = normalize_ttl(raw.get("ttl_seconds", DEFAULT_TTL_SECONDS))
    failures.extend(ttl_failures)
    now_raw, now, now_failures = normalize_now(now_value)
    failures.extend(now_failures)
    resume_status = "RESUMABLE"
    if expires is None:
        resume_status = "INVALID"
    elif expires <= now:
        resume_status = "EXPIRED"
    if raw.get("resume_status") not in (None, "RESUMABLE", "EXPIRED"):
        failures.append("checkpoint resume_status is outside the allowed persisted values")
    summary = sanitize_value(raw.get("summary", "none"))
    if unsafe_value(raw.get("summary", "")):
        failures.append("summary contained unsafe private context")
    evidence, evidence_failures = scope_contract.normalize_evidence_ref(raw.get("evidence_ref", "none"))
    failures.extend(evidence_failures)
    state = sanitize_state(raw.get("state", {}), failures)
    authority = validate_authority(raw.get("authority"), failures)
    scope = validate_scope(target, raw.get("scope"), raw, failures)
    if failures:
        resume_status = "INVALID"
    checkpoint = {
        "schema": SCHEMA,
        "id": cid,
        "path": rel(path, target),
        "created_at": created_at,
        "expires_at": expires_at if ISO_UTC.match(expires_at) else "1970-01-01T00:00:00Z",
        "ttl_seconds": ttl,
        "resume_status": resume_status,
        "summary": summary,
        "evidence_ref": evidence if not evidence_failures else "invalid",
        "scope": scope,
        "state": state,
        "authority": authority,
        "valid": not failures,
        "inspected_at": now_raw,
    }
    return checkpoint, failures


def list_checkpoints(target: Path, *, now_value: object | None = None) -> dict[str, object]:
    target = target.expanduser().resolve()
    root = root_path(target)
    checkpoints: list[dict[str, object]] = []
    failures: list[str] = []
    if root.exists():
        for path in sorted(root.glob("*.json")):
            checkpoint, checkpoint_failures = validate_checkpoint(target, path, now_value=now_value)
            checkpoints.append(checkpoint)
            failures.extend(f"{rel(path, target)}: {failure}" for failure in checkpoint_failures)
    counts: dict[str, int] = {}
    for checkpoint in checkpoints:
        status = str(checkpoint.get("resume_status", "INVALID"))
        counts[status] = counts.get(status, 0) + 1
    return {
        "version": VERSION,
        "schema": SCHEMA,
        "status": "FAIL" if failures else "PASS",
        "root": rel(root, target),
        "checkpoint_count": len(checkpoints),
        "resume_status_counts": dict(sorted(counts.items())),
        "checkpoints": checkpoints,
        "failures": failures,
        "writes": [],
        "durable_memory_write": False,
        "certification_evidence": False,
    }


def status_checkpoint(target: Path, checkpoint_id_value: object, *, now_value: object | None = None) -> dict[str, object]:
    target = target.expanduser().resolve()
    path = checkpoint_path(target, checkpoint_id_value)
    if not path.exists():
        return {
            "version": VERSION,
            "schema": SCHEMA,
            "status": "PASS",
            "checkpoint_path": rel(path, target),
            "resume_status": "MISSING",
            "checkpoint": None,
            "failures": [],
            "writes": [],
            "durable_memory_write": False,
            "certification_evidence": False,
        }
    checkpoint, failures = validate_checkpoint(target, path, now_value=now_value)
    return {
        "version": VERSION,
        "schema": SCHEMA,
        "status": "FAIL" if failures else "PASS",
        "checkpoint_path": rel(path, target),
        "resume_status": checkpoint.get("resume_status", "INVALID"),
        "checkpoint": checkpoint,
        "failures": failures,
        "writes": [],
        "durable_memory_write": False,
        "certification_evidence": False,
    }


def cleanup_expired(target: Path, *, now_value: object | None = None) -> dict[str, object]:
    target = target.expanduser().resolve()
    root = root_path(target)
    failures: list[str] = []
    deleted: list[str] = []
    inspected = 0
    if root.exists():
        for path in sorted(root.glob("*.json")):
            inspected += 1
            checkpoint, checkpoint_failures = validate_checkpoint(target, path, now_value=now_value)
            if checkpoint_failures:
                failures.extend(f"{rel(path, target)}: {failure}" for failure in checkpoint_failures)
                continue
            if checkpoint.get("resume_status") == "EXPIRED":
                path.unlink()
                deleted.append(rel(path, target))
    return {
        "version": VERSION,
        "schema": SCHEMA,
        "status": "FAIL" if failures else "PASS",
        "root": rel(root, target),
        "inspected": inspected,
        "deleted": deleted,
        "failures": failures,
        "writes": deleted,
        "durable_memory_write": False,
        "certification_evidence": False,
    }


def inspect_schema() -> dict[str, object]:
    return {
        "version": VERSION,
        "schema": SCHEMA,
        "status": "PASS",
        "root": CHECKPOINT_ROOT.as_posix(),
        "default_ttl_seconds": DEFAULT_TTL_SECONDS,
        "max_ttl_seconds": MAX_TTL_SECONDS,
        "resume_statuses": list(RESUME_STATUSES),
        "required_fields": [
            "schema",
            "id",
            "created_at",
            "expires_at",
            "ttl_seconds",
            "resume_status",
            "summary",
            "evidence_ref",
            "scope",
            "state",
            "authority",
        ],
        "authority": authority_block(),
        "writes": [],
        "durable_memory_write": False,
        "certification_evidence": False,
    }


def snapshot(target: Path) -> dict[str, str]:
    if not target.exists():
        return {}
    return {
        rel(path, target): sha256_text(path.read_text(encoding="utf-8", errors="replace"))
        for path in sorted(target.rglob("*"))
        if path.is_file()
    }


def forbidden_output_failures(payload: object) -> list[str]:
    text = json.dumps(payload, sort_keys=True)
    return [f"unsafe output leaked: {item}" for item in FORBIDDEN_OUTPUT if item in text]


def self_test_mode() -> tuple[str, str]:
    root = Path(__file__).resolve().parents[1]
    if (root / "package.json").exists():
        return "package", "source-package-contract"
    return "installed", "installed-helper-contract"


def self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-checkpoint-") as tempdir:
        base = Path(tempdir)
        clean = base / "clean"
        expired = base / "expired"
        hostile = base / "hostile"
        reject = base / "reject"
        for target in (clean, expired, hostile, reject):
            target.mkdir()

        created = create_checkpoint(
            clean,
            checkpoint_id_value="resume-wave",
            ttl_seconds=60,
            summary="Resume after checkpoint lane self-test.",
            adapter="codex",
            agent="checkpoint",
            run="wave-4",
            source="checkpoint",
            evidence_ref="none",
            state={"phase": "wave-4", "next": "resume"},
            now_value="2026-05-26T12:00:00Z",
        )
        if created.get("status") != "PASS":
            failures.append(f"valid checkpoint create should pass: {created.get('failures')}")
        if created.get("writes") != [".tes/checkpoints/resume-wave.json"]:
            failures.append("checkpoint create must report only the checkpoint write")
        before_clean = snapshot(clean)
        listed = list_checkpoints(clean, now_value="2026-05-26T12:00:30Z")
        checked = status_checkpoint(clean, "resume-wave", now_value="2026-05-26T12:00:30Z")
        schema_result = inspect_schema()
        after_clean = snapshot(clean)
        if before_clean != after_clean:
            failures.append("checkpoint list/status/inspect-schema must not write")
        if listed.get("status") != "PASS" or checked.get("resume_status") != "RESUMABLE":
            failures.append("fresh checkpoint should remain resumable")
        if schema_result.get("authority", {}).get("durable_memory_write") is not False:
            failures.append("checkpoint schema must reject durable memory authority")
        for forbidden_path in (
            "docs/agents/cortex/TRAIL.md",
            "docs/agents/cortex/cells/generated.md",
            ".tes/field-reports/outbox.jsonl",
            ".tes/events/ledger.jsonl",
        ):
            if (clean / forbidden_path).exists():
                failures.append(f"checkpoint lane must not write {forbidden_path}")

        created_expired = create_checkpoint(
            expired,
            checkpoint_id_value="old-run",
            ttl_seconds=1,
            summary="Short lived resume state.",
            adapter="codex",
            agent="checkpoint",
            run="wave-4",
            source="checkpoint",
            evidence_ref="none",
            now_value="2026-05-26T12:00:00Z",
        )
        if created_expired.get("status") != "PASS":
            failures.append("expired checkpoint fixture failed to create")
        before_cleanup = snapshot(expired)
        cleanup = cleanup_expired(expired, now_value="2026-05-26T12:00:02Z")
        after_cleanup = snapshot(expired)
        removed = sorted(set(before_cleanup) - set(after_cleanup))
        changed = sorted(path for path in set(before_cleanup) & set(after_cleanup) if before_cleanup[path] != after_cleanup[path])
        if cleanup.get("status") != "PASS" or cleanup.get("deleted") != [".tes/checkpoints/old-run.json"]:
            failures.append("expired checkpoint cleanup must delete only expired checkpoint files")
        if removed != [".tes/checkpoints/old-run.json"] or changed:
            failures.append("cleanup must not mutate non-checkpoint files")
        if (expired / "docs/agents/cortex/TRAIL.md").exists() or (expired / ".tes/field-reports/outbox.jsonl").exists():
            failures.append("cleanup must not write Cortex or Field Reports surfaces")

        rejected = create_checkpoint(
            reject,
            checkpoint_id_value="unsafe",
            ttl_seconds=60,
            summary="Traceback (most recent call last): /absolute/unsafe/source.py "
            + SYNTHETIC_SECRET_ASSIGNMENT,
            adapter="codex",
            agent="checkpoint",
            source="checkpoint",
            evidence_ref="/absolute/unsafe/evidence.md",
            now_value="2026-05-26T12:00:00Z",
        )
        if rejected.get("status") != "FAIL":
            failures.append("unsafe checkpoint creation must fail closed")
        if (reject / ".tes/checkpoints/unsafe.json").exists():
            failures.append("unsafe checkpoint creation must not write a checkpoint")
        failures.extend(forbidden_output_failures(rejected))

        (root_path(hostile)).mkdir(parents=True, exist_ok=True)
        (root_path(hostile) / "unsafe.json").write_text(
            json.dumps(
                {
                    "schema": SCHEMA,
                    "id": "unsafe",
                    "created_at": "2026-05-26T12:00:00Z",
                    "expires_at": "2026-05-26T13:00:00Z",
                    "ttl_seconds": 3600,
                    "resume_status": "RESUMABLE",
                    "summary": "Traceback (most recent call last): /absolute/unsafe/source.py "
                    + SYNTHETIC_SECRET_ASSIGNMENT,
                    "evidence_ref": "/absolute/unsafe/evidence.md",
                    "scope": scope_contract.normalize_scope(
                        hostile,
                        adapter="codex",
                        agent="checkpoint",
                        run="unsafe",
                        source="checkpoint",
                        evidence_ref="none",
                        timestamp="2026-05-26T12:00:00Z",
                        status="RESUMABLE",
                    ).get("scope", {}),
                    "state": {
                        "unsafe_path": "/absolute/unsafe/source.py",
                        "unsafe_email": SYNTHETIC_EMAIL,
                        "unsafe_secret": SYNTHETIC_BEARER_SECRET,
                        "unsafe_url": SYNTHETIC_PRIVATE_REPO_URL,
                    },
                    "authority": authority_block(),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (root_path(hostile) / "broken.json").write_text("{not-json}\n", encoding="utf-8")
        before_hostile = snapshot(hostile)
        hostile_list = list_checkpoints(hostile, now_value="2026-05-26T12:00:30Z")
        hostile_status = status_checkpoint(hostile, "unsafe", now_value="2026-05-26T12:00:30Z")
        missing_status = status_checkpoint(hostile, "missing", now_value="2026-05-26T12:00:30Z")
        after_hostile = snapshot(hostile)
        if hostile_list.get("status") != "FAIL" or hostile_status.get("resume_status") != "INVALID":
            failures.append("unsafe checkpoint inspection must fail and remain bounded")
        if missing_status.get("resume_status") != "MISSING":
            failures.append("missing checkpoint status must be explicit")
        if before_hostile != after_hostile:
            failures.append("hostile checkpoint inspection must not write")
        failures.extend(forbidden_output_failures(hostile_list))
        failures.extend(forbidden_output_failures(hostile_status))
        if (hostile / "docs/agents/cortex/TRAIL.md").exists() or (hostile / ".tes/field-reports/outbox.jsonl").exists():
            failures.append("hostile inspection must not write Cortex or Field Reports surfaces")

    mode, coverage = self_test_mode()
    result = {
        "version": VERSION,
        "schema": SCHEMA,
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
        "self_test_mode": mode,
        "coverage": coverage,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if failures:
        print("[checkpoint] FAIL")
        return 1
    print("[checkpoint] PASS")
    return 0


def parse_state(raw: str | None) -> dict[str, object]:
    if raw in (None, ""):
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("--state-json must be a JSON object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=("create", "list", "status", "cleanup", "inspect-schema"))
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--id", default="")
    parser.add_argument("--ttl-seconds", type=int, default=DEFAULT_TTL_SECONDS)
    parser.add_argument("--summary", default="checkpoint")
    parser.add_argument("--adapter", default="checkpoint")
    parser.add_argument("--agent", default="checkpoint")
    parser.add_argument("--parent-agent", default="")
    parser.add_argument("--run", default="")
    parser.add_argument("--source", default="checkpoint")
    parser.add_argument("--evidence-ref", default="none")
    parser.add_argument("--status", default="RESUMABLE")
    parser.add_argument("--state-json", default="")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--now", default="")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        state = parse_state(args.state_json)
    except (json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"version": VERSION, "schema": SCHEMA, "status": "FAIL", "failures": [str(exc)], "writes": []}, indent=2))
        return 1
    if args.command == "create":
        result = create_checkpoint(
            args.target,
            checkpoint_id_value=args.id,
            ttl_seconds=args.ttl_seconds,
            summary=args.summary,
            adapter=args.adapter,
            agent=args.agent,
            parent_agent=args.parent_agent,
            run=args.run,
            source=args.source,
            evidence_ref=args.evidence_ref,
            status_value=args.status,
            state=state,
            replace=args.replace,
            now_value=args.now or None,
        )
    elif args.command == "list":
        result = list_checkpoints(args.target, now_value=args.now or None)
    elif args.command == "status":
        result = status_checkpoint(args.target, args.id, now_value=args.now or None)
    elif args.command == "cleanup":
        result = cleanup_expired(args.target, now_value=args.now or None)
    elif args.command == "inspect-schema":
        result = inspect_schema()
    else:
        parser.error("command is required unless --self-test is used")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
