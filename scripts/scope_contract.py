#!/usr/bin/env python3
"""Normalize TES runtime scope without exposing private project identifiers."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from posixpath import normpath
import re
import sys
import tempfile
from typing import Any


VERSION = "0.3.154"
SCHEMA = "tes-scope@1"
SAFE_TOKEN = re.compile(r"[^a-zA-Z0-9_.:-]+")
ISO_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
ABSOLUTE_PATH = re.compile(r"^(/|~|[A-Za-z]:[\\/])")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL = re.compile(r"https?://")
SECRET = re.compile(r"(?i)(api[_-]?key|authorization|bearer|credential|password|secret|token)")
ALLOWED_EVIDENCE_PREFIXES = (
    ".tes/field-reports/",
    "docs/agents/cortex/sources/",
    "docs/agents/evidence/",
)
ALLOWED_EVIDENCE_FILES = {
    "docs/agents/cortex/MAP.md",
    "docs/agents/cortex/TRAIL.md",
    "docs/agents/cortex/LINKS.md",
    "none",
}


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def project_fingerprint(target: Path) -> str:
    return f"project:{sha256_text(str(target.expanduser().resolve()))[:16]}"


def safe_token(value: object, default: str, *, lower: bool = True, limit: int = 64) -> str:
    raw = str(value or "").strip()
    if lower:
        raw = raw.lower()
    token = SAFE_TOKEN.sub("-", raw).strip("-._:")
    return token[:limit] if token else default


def unsafe_text_reason(value: object, field: str) -> str | None:
    raw = str(value or "")
    if "\n" in raw or "\r" in raw:
        return f"{field} must be a single-line scope value"
    if URL.search(raw):
        return f"{field} must not contain a URL"
    if EMAIL.search(raw):
        return f"{field} must not contain personal data"
    if SECRET.search(raw):
        return f"{field} must not contain secret-like labels"
    return None


def normalize_timestamp(value: object | None) -> tuple[str, list[str]]:
    timestamp = str(value or utc_stamp()).strip()
    if not ISO_UTC.match(timestamp):
        return timestamp, ["timestamp must be UTC ISO-8601 seconds with Z suffix"]
    return timestamp, []


def normalize_project(target: Path, value: object | None) -> tuple[str, list[str]]:
    expected = project_fingerprint(target)
    if value in (None, ""):
        return expected, []
    project = str(value).strip()
    if project != expected:
        return expected, ["project scope does not match the target fingerprint"]
    return project, []


def normalize_evidence_ref(value: object | None) -> tuple[str, list[str]]:
    raw = str(value or "none").strip().strip("`")
    failures: list[str] = []
    if not raw:
        return "none", []
    reason = unsafe_text_reason(raw, "evidence_ref")
    if reason:
        failures.append(reason)
    if ABSOLUTE_PATH.search(raw):
        failures.append("evidence_ref must not be absolute or home-relative")
    raw = raw.replace("\\", "/")
    normalized = normpath(raw)
    if normalized.startswith("../") or normalized == ".." or "/../" in f"/{raw}/":
        failures.append("evidence_ref must not traverse outside the runtime scope")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.startswith("sources/"):
        normalized = f"docs/agents/cortex/{normalized}"
    if normalized.startswith("docs/agents/cortex/sources/../"):
        failures.append("evidence_ref must not traverse outside Cortex sources")
    allowed = (
        normalized in ALLOWED_EVIDENCE_FILES
        or any(normalized.startswith(prefix) for prefix in ALLOWED_EVIDENCE_PREFIXES)
    )
    if not allowed:
        failures.append("evidence_ref must point to an allowed TES evidence surface")
    return normalized, failures


def normalize_scope(
    target: Path,
    *,
    project: object | None = None,
    adapter: object | None = None,
    agent: object | None = None,
    parent_agent: object | None = None,
    run: object | None = None,
    source: object | None = None,
    evidence_ref: object | None = None,
    timestamp: object | None = None,
    trust_level: object | None = None,
    status: object | None = None,
) -> dict[str, Any]:
    failures: list[str] = []
    normalized_project, project_failures = normalize_project(target, project)
    failures.extend(project_failures)
    normalized_timestamp, timestamp_failures = normalize_timestamp(timestamp)
    failures.extend(timestamp_failures)
    normalized_evidence, evidence_failures = normalize_evidence_ref(evidence_ref)
    failures.extend(evidence_failures)

    for field, value in (
        ("adapter", adapter),
        ("agent", agent),
        ("parent_agent", parent_agent),
        ("run", run),
        ("source", source),
        ("trust_level", trust_level),
        ("status", status),
    ):
        reason = unsafe_text_reason(value, field)
        if reason:
            failures.append(reason)

    normalized_agent = safe_token(agent, "")
    normalized_parent = safe_token(parent_agent, "")
    if not normalized_agent and not normalized_parent:
        failures.append("scope requires agent or parent_agent")
        normalized_agent = "unknown-agent"

    normalized_source = safe_token(source, "unknown-source")
    normalized_status = safe_token(status, "")
    normalized_trust = safe_token(trust_level, "")
    if not normalized_status and not normalized_trust:
        failures.append("scope requires status or trust_level")
        normalized_status = "unknown"

    if run in (None, ""):
        normalized_run = "run:" + sha256_text(
            "|".join(
                (
                    normalized_project,
                    normalized_source,
                    normalized_agent,
                    normalized_parent,
                    normalized_timestamp,
                    normalized_evidence,
                )
            )
        )[:16]
    else:
        normalized_run = safe_token(run, "run")

    scope = {
        "schema": SCHEMA,
        "project": normalized_project,
        "adapter": safe_token(adapter, "unknown-adapter"),
        "agent": normalized_agent or "none",
        "parent_agent": normalized_parent or "none",
        "run": normalized_run,
        "source": normalized_source,
        "evidence_ref": normalized_evidence,
        "timestamp": normalized_timestamp,
        "status": normalized_status or "none",
        "trust_level": normalized_trust or "none",
    }
    return {"version": VERSION, "status": "FAIL" if failures else "PASS", "scope": scope, "failures": failures}


def self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-scope-contract-") as tempdir:
        target = Path(tempdir)
        timestamp = "2026-05-26T12:00:00Z"
        first = normalize_scope(
            target,
            adapter="codex",
            agent="parent",
            run="wave-2",
            source="cortex",
            evidence_ref="sources/source.md",
            timestamp=timestamp,
            status="PASS",
        )
        second = normalize_scope(
            target,
            adapter="codex",
            agent="parent",
            run="wave-2",
            source="cortex",
            evidence_ref="sources/source.md",
            timestamp=timestamp,
            status="PASS",
        )
        if first.get("status") != "PASS":
            failures.append(f"valid scope should pass: {first.get('failures')}")
        if first.get("scope") != second.get("scope"):
            failures.append("scope normalization must be deterministic for equal input")
        scope = first.get("scope", {})
        required = {
            "schema",
            "project",
            "adapter",
            "agent",
            "parent_agent",
            "run",
            "source",
            "evidence_ref",
            "timestamp",
            "status",
            "trust_level",
        }
        missing = sorted(required - set(scope)) if isinstance(scope, dict) else sorted(required)
        if missing:
            failures.append("valid scope missing fields: " + ", ".join(missing))
        if isinstance(scope, dict) and scope.get("evidence_ref") != "docs/agents/cortex/sources/source.md":
            failures.append("Cortex source evidence ref was not canonicalized")

        cases = {
            "missing agent": normalize_scope(target, source="cortex", evidence_ref="sources/source.md", timestamp=timestamp, status="PASS"),
            "missing status": normalize_scope(target, agent="parent", source="cortex", evidence_ref="sources/source.md", timestamp=timestamp),
            "absolute path": normalize_scope(target, agent="parent", source="cortex", evidence_ref="/absolute/unsafe/project.md", timestamp=timestamp, status="PASS"),
            "traversal": normalize_scope(target, agent="parent", source="cortex", evidence_ref="sources/../secret.md", timestamp=timestamp, status="PASS"),
            "url": normalize_scope(
                target,
                agent="parent",
                source="cortex",
                evidence_ref="https://" + "private." + "example.test/evidence",
                timestamp=timestamp,
                status="PASS",
            ),
            "cross scope": normalize_scope(target, project="project:0000000000000000", agent="parent", source="cortex", evidence_ref="sources/source.md", timestamp=timestamp, status="PASS"),
            "bad timestamp": normalize_scope(target, agent="parent", source="cortex", evidence_ref="sources/source.md", timestamp="2026-05-26", status="PASS"),
        }
        for label, result in cases.items():
            if result.get("status") != "FAIL":
                failures.append(f"{label} fixture should fail")

    result = {"version": VERSION, "schema": SCHEMA, "status": "FAIL" if failures else "PASS", "failures": failures}
    print(json.dumps(result, indent=2, sort_keys=True))
    if failures:
        print("[scope-contract] FAIL")
        return 1
    print("[scope-contract] PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--adapter")
    parser.add_argument("--agent")
    parser.add_argument("--parent-agent")
    parser.add_argument("--run")
    parser.add_argument("--source")
    parser.add_argument("--evidence-ref")
    parser.add_argument("--timestamp")
    parser.add_argument("--trust-level")
    parser.add_argument("--status")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    result = normalize_scope(
        args.target,
        adapter=args.adapter,
        agent=args.agent,
        parent_agent=args.parent_agent,
        run=args.run,
        source=args.source,
        evidence_ref=args.evidence_ref,
        timestamp=args.timestamp,
        trust_level=args.trust_level,
        status=args.status,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
