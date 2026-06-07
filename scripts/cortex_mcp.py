#!/usr/bin/env python3
"""Expose TES Cortex tools over MCP stdio."""

from __future__ import annotations

import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import sys
import tempfile
import threading
from typing import Any
from urllib import request as urllib_request

import cortex
import event_ledger
import field_reports


VERSION = "0.3.175"
PROTOCOL_VERSION = "2025-06-18"
WRITE_APPROVAL_PREFIX = "APPROVE TES CORTEX MCP WRITE"
WRITE_TOOL_NAMES = {"cortex_remember_plan", "cortex_remember"}
LOCAL_HTTP_HOSTS = {"127.0.0.1", "localhost", "::1"}
CELL_RESOURCE_PREFIX = "tes-cortex://cells/"
TRAIL_ENTRY_HEADING = re.compile(
    r"^## \[(?P<date>\d{4}-\d{2}-\d{2})\] (?P<event>[^|]+?) \| (?P<cell>.+)$"
)
SELF_TEST_MODE = False
VERIFY_CACHE: dict[str, tuple[int, dict[str, object]]] = {}
VERIFY_CACHE_STATS = {"hits": 0, "misses": 0, "bypasses": 0, "fallbacks": 0}
PROMPT_REGISTRY: dict[str, dict[str, str]] = {
    "cortex/closure-reflection": {
        "title": "Cortex Closure Reflection",
        "description": "Review a closure for durable Cortex learning without writing.",
        "version": "1",
        "body": (
            "Review the latest closure. Identify durable decisions, evidence still needed, "
            "and whether a memory proposal is warranted. Return no writes."
        ),
    },
    "cortex/curation-review": {
        "title": "Cortex Curation Review",
        "description": "Classify Cortex curation signals without mutating memory.",
        "version": "1",
        "body": (
            "Review Cortex curation signals. Classify duplicate, split, link, tension, "
            "evidence-gap, redundancy, or reject candidates. Return no writes."
        ),
    },
    "cortex/remember-checklist": {
        "title": "Cortex Remember Checklist",
        "description": "Check whether a durable-memory proposal is ready for human review.",
        "version": "1",
        "body": (
            "Before durable memory, verify one claim, explicit evidence, target-neutral "
            "wording, and user approval outside this prompt. Return checklist only."
        ),
    },
}


def schema_string(description: str) -> dict[str, str]:
    return {"type": "string", "description": description}


def schema_integer(description: str, default: int | None = None) -> dict[str, object]:
    schema: dict[str, object] = {"type": "integer", "description": description, "minimum": 1}
    if default is not None:
        schema["default"] = default
    return schema


def schema_string_array(description: str) -> dict[str, object]:
    return {"type": "array", "items": {"type": "string"}, "description": description}


def schema_boolean(description: str, default: bool | None = None) -> dict[str, object]:
    schema: dict[str, object] = {"type": "boolean", "description": description}
    if default is not None:
        schema["default"] = default
    return schema


def schema_field(descriptor: tuple[object, ...]) -> dict[str, object]:
    kind = str(descriptor[0])
    description = str(descriptor[1])
    if kind == "string":
        return schema_string(description)
    if kind == "integer":
        default = descriptor[2] if len(descriptor) > 2 else None
        return schema_integer(description, int(default) if default is not None else None)
    if kind == "string-array":
        return schema_string_array(description)
    if kind == "boolean":
        default = descriptor[2] if len(descriptor) > 2 else None
        return schema_boolean(description, bool(default) if default is not None else None)
    if kind == "enum":
        values = descriptor[2]
        if not isinstance(values, list):
            raise TypeError("enum descriptor values must be a list")
        schema: dict[str, object] = {"type": "string", "description": description, "enum": values}
        if len(descriptor) > 3:
            schema["default"] = descriptor[3]
        return schema
    raise ValueError(f"unknown schema descriptor type: {kind}")


def schema_object(
    properties: dict[str, tuple[object, ...]],
    required: list[str] | None = None,
) -> dict[str, object]:
    schema: dict[str, object] = {
        "type": "object",
        "properties": {name: schema_field(descriptor) for name, descriptor in properties.items()},
    }
    if required:
        schema["required"] = required
    return schema


def copy_verify_result(result: dict[str, object]) -> dict[str, object]:
    return json.loads(json.dumps(result))


def cortex_tree_mtime_key(target: Path) -> int:
    root = cortex.cortex_path(target)
    mtimes = [root.stat().st_mtime_ns]
    for path in root.rglob("*"):
        mtimes.append(path.stat().st_mtime_ns)
    return max(mtimes)


def verify_target(target: Path) -> dict[str, object]:
    if SELF_TEST_MODE:
        VERIFY_CACHE_STATS["bypasses"] += 1
        return cortex.verify(target)
    cache_key = str(target.resolve())
    try:
        mtime_key = cortex_tree_mtime_key(target)
    except OSError:
        VERIFY_CACHE_STATS["fallbacks"] += 1
        return cortex.verify(target)
    cached = VERIFY_CACHE.get(cache_key)
    if cached and cached[0] == mtime_key:
        VERIFY_CACHE_STATS["hits"] += 1
        return copy_verify_result(cached[1])
    VERIFY_CACHE_STATS["misses"] += 1
    result = cortex.verify(target)
    VERIFY_CACHE[cache_key] = (mtime_key, copy_verify_result(result))
    return result


def write_tool_definitions() -> list[dict[str, object]]:
    remember_properties = {
        "cell": schema_string("Cell stem or path under cells/**."),
        "claim": schema_string("Durable claim to write. Must not be a loose summary."),
        "evidence": schema_string_array("Evidence refs under sources/** or docs/agents/evidence/**."),
        "summary": schema_string("Optional MAP.md summary."),
        "links": schema_string_array("Optional Cortex cell links to add."),
    }
    return [
        {
            "name": "cortex_remember_plan",
            "title": "Plan Cortex Remember",
            "description": (
                "Validate a no-write durable-memory proposal and return the exact approval "
                "phrase required for cortex_remember."
            ),
            "inputSchema": {
                "type": "object",
                "properties": remember_properties,
                "required": ["cell", "claim", "evidence"],
            },
        },
        {
            "name": "cortex_remember",
            "title": "Remember Cortex",
            "description": (
                "Write one new Cortex cell only after explicit approval of the exact "
                "cortex_remember_plan phrase. Disabled only when the server starts read-only."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    **remember_properties,
                    "approval_phrase": schema_string(
                        f"Exact phrase from cortex_remember_plan: {WRITE_APPROVAL_PREFIX} <approval_id>."
                    ),
                },
                "required": ["cell", "claim", "evidence", "approval_phrase"],
            },
        },
    ]


def tool_definitions(writes_enabled: bool = True) -> list[dict[str, object]]:
    tools: list[dict[str, object]] = [
        {
            "name": "cortex_verify",
            "title": "Verify Cortex",
            "description": "Validate the Cortex structure and immutable-source contract.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "cortex_health",
            "title": "Cortex Health",
            "description": "Inspect Cortex health and operator mutability classes without writing.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "cortex_peek",
            "title": "Peek Cortex",
            "description": "Read one Cortex cell or recall query results without writing.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": schema_string("Optional recall query."),
                    "cell": schema_string("Optional cell stem or path under cells/**."),
                    "limit": schema_integer("Maximum recall matches.", 10),
                    "force_rg": {
                        "type": "boolean",
                        "description": "Force rg fallback instead of SQLite FTS5.",
                        "default": False,
                    },
                },
            },
        },
        {
            "name": "cortex_review",
            "title": "Review Cortex",
            "description": "Run no-write Cortex audit, curation, and reflection review.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": schema_string("Optional closure note, decision, or lesson to review."),
                    "limit": schema_integer("Maximum changed files to inspect.", 20),
                    "line_budget": schema_integer("Changed-line budget that triggers curation review.", 500),
                    "backend": {
                        "type": "string",
                        "description": "Curation backend: auto, xenova, or lexical.",
                        "enum": ["auto", "xenova", "lexical"],
                        "default": "lexical",
                    },
                },
            },
        },
        {
            "name": "cortex_audit",
            "title": "Audit Cortex",
            "description": "Audit cells, wikilinks, map coverage, and evidence grounding.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "cortex_recall",
            "title": "Recall Cortex",
            "description": "Search Cortex through SQLite FTS5 with rg fallback.",
            "inputSchema": schema_object(
                {
                    "query": ("string", "Recall query."),
                    "limit": ("integer", "Maximum matches.", 10),
                    "force_rg": ("boolean", "Force rg fallback instead of SQLite FTS5.", False),
                },
                ["query"],
            ),
        },
        {
            "name": "cortex_read_cell",
            "title": "Read Cortex Cell",
            "description": "Read one Markdown cell from docs/agents/cortex/cells/**.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cell": schema_string("Cell stem or path under cells/**, with or without .md."),
                },
                "required": ["cell"],
            },
        },
        {
            "name": "cortex_cell_history",
            "title": "Read Cortex Cell History",
            "description": "Read structured TRAIL.md entries associated with one Cortex cell.",
            "inputSchema": schema_object(
                {
                    "cell": ("string", "Cell stem or path under cells/**, with or without .md."),
                },
                ["cell"],
            ),
        },
        {
            "name": "cortex_absorb_plan",
            "title": "Plan Cortex Absorb",
            "description": "Generate a no-write absorb plan for a source under sources/**.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source": schema_string("Source path under docs/agents/cortex/sources/**."),
                },
                "required": ["source"],
            },
        },
        {
            "name": "cortex_curate_plan",
            "title": "Plan Cortex Curation",
            "description": (
                "Run the no-write semantic curation gate for duplicate, split, link, "
                "tension, evidence-gap, redundancy, and reject candidates."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "backend": {
                        "type": "string",
                        "description": "Curation backend: auto, xenova, or lexical.",
                        "enum": ["auto", "xenova", "lexical"],
                        "default": "lexical",
                    },
                },
            },
        },
        {
            "name": "cortex_reflect",
            "title": "Reflect Cortex Capture",
            "description": "Generate a no-write closure reflection for possible Cortex promotion.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": schema_string("Optional closure note, decision, or lesson to consider."),
                    "limit": schema_integer("Maximum changed files to inspect.", 20),
                    "line_budget": schema_integer("Changed-line budget that triggers curation review.", 500),
                },
            },
        },
        {
            "name": "cortex_list_events",
            "title": "List Cortex Events",
            "description": "List sanitized TES lifecycle ledger events without writing.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "status": schema_string("Optional event status filter."),
                    "lifecycle": schema_string("Optional event lifecycle filter."),
                    "limit": schema_integer("Maximum events to return.", 50),
                },
            },
        },
        {
            "name": "cortex_get_event_status",
            "title": "Get Cortex Event Status",
            "description": "Return one lifecycle event status by event_id without writing.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "event_id": schema_string("Exact event id to inspect."),
                },
                "required": ["event_id"],
            },
        },
    ]
    if writes_enabled:
        tools.extend(write_tool_definitions())
    return tools


def result_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def tool_result(payload: dict[str, Any], is_error: bool | None = None) -> dict[str, Any]:
    if is_error is None:
        is_error = payload.get("status") in {"FAIL", "BLOCKED"}
    return {
        "content": [{"type": "text", "text": result_text(payload)}],
        "structuredContent": payload,
        "isError": is_error,
    }


def progress_notification(progress_token: object, progress: int, total: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "method": "notifications/progress",
        "params": {
            "progressToken": progress_token,
            "progress": progress,
            "total": total,
            "message": message,
        },
    }


def emit_progress(
    progress_callback: Any,
    progress_token: object | None,
    progress: int,
    total: int,
    message: str,
) -> None:
    if progress_callback is None or progress_token is None:
        return
    try:
        progress_callback(progress_notification(progress_token, progress, total, message))
    except Exception:
        return


def resolve_target(default_target: Path, args: dict[str, Any]) -> Path:
    if "target" in args:
        raise ValueError("target argument is not accepted; restart the server with --target")
    return default_target


def string_list_arg(args: dict[str, Any], key: str) -> list[str]:
    raw = args.get(key, [])
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError(f"{key} must be an array")
    values: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            raise ValueError(f"{key} must contain only strings")
        stripped = item.strip()
        if stripped:
            values.append(stripped)
    return values


def string_arg(args: dict[str, Any], key: str, default: str = "") -> str:
    raw = args.get(key, default)
    if raw is None:
        return ""
    if not isinstance(raw, str):
        raise ValueError(f"{key} must be a string")
    return raw.strip()


def remember_payload(default_target: Path, args: dict[str, Any]) -> tuple[Path, dict[str, object]]:
    target = resolve_target(default_target, args)
    payload: dict[str, object] = {
        "cell": string_arg(args, "cell"),
        "claim": string_arg(args, "claim"),
        "evidence": string_list_arg(args, "evidence"),
        "summary": string_arg(args, "summary") or None,
        "links": string_list_arg(args, "links"),
    }
    return target, payload


def remember_validation(target: Path, payload: dict[str, object]) -> dict[str, object]:
    verify_result = verify_target(target)
    failures = list(verify_result["failures"])
    cell = str(payload["cell"])
    claim = str(payload["claim"])
    evidence = [str(item) for item in payload["evidence"]]  # type: ignore[index]
    links = [str(item) for item in payload["links"]]  # type: ignore[index]
    path: Path | None = None

    if not cell:
        failures.append("remember requires cell")
    if not claim:
        failures.append("remember requires claim")
    if not evidence:
        failures.append("remember requires at least one evidence ref")

    if cell:
        try:
            path = cortex.resolve_cell_path(target, cell)
        except ValueError as exc:
            failures.append(str(exc))
        else:
            if path.exists():
                failures.append(f"cell already exists; MCP remember does not overwrite: {cortex.rel(path, target)}")

    for link in links:
        try:
            cortex.normalize_cell_rel(link)
        except ValueError as exc:
            failures.append(f"invalid link {link!r}: {exc}")

    evidence_lines = [cortex.format_evidence_line(item) for item in evidence]
    evidence_text = "\n".join(evidence_lines)
    if evidence and not cortex.EVIDENCE_REF.search(evidence_text):
        failures.append("remember evidence must reference sources/**, docs/agents/evidence/**, or Assumption:")
    failures.extend(cortex.evidence_ref_failures(target, evidence_text))

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "cell_path": cortex.rel(path, target) if path is not None else None,
        "verify": verify_result,
    }


def remember_approval_id(target: Path, payload: dict[str, object]) -> str:
    approval_payload = {
        "schema": "tes-cortex-mcp-remember-approval@1",
        "target": str(target.resolve()),
        "cell": payload["cell"],
        "claim": payload["claim"],
        "evidence": payload["evidence"],
        "summary": payload["summary"],
        "links": payload["links"],
    }
    encoded = json.dumps(approval_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def remember_plan(default_target: Path, args: dict[str, Any]) -> dict[str, object]:
    target, payload = remember_payload(default_target, args)
    validation = remember_validation(target, payload)
    approval_id = remember_approval_id(target, payload)
    status = str(validation["status"])
    result: dict[str, object] = {
        "target": str(target),
        "status": status,
        "operator": "remember_plan",
        "mutability_class": "proposal-only",
        "writes": [],
        "derived_writes": [],
        "failures": validation["failures"],
        "cell": payload["cell"],
        "claim": payload["claim"],
        "evidence": payload["evidence"],
        "summary": payload["summary"],
        "links": payload["links"],
        "cell_path": validation["cell_path"],
        "approval_id": approval_id,
        "approval_phrase": f"{WRITE_APPROVAL_PREFIX} {approval_id}",
        "route": "no-write plan; pass approval_phrase to cortex_remember only after explicit user approval",
    }
    return result


def remember_apply(default_target: Path, args: dict[str, Any]) -> dict[str, object]:
    target, payload = remember_payload(default_target, args)
    validation = remember_validation(target, payload)
    approval_id = remember_approval_id(target, payload)
    expected_phrase = f"{WRITE_APPROVAL_PREFIX} {approval_id}"
    approval_phrase = string_arg(args, "approval_phrase")
    failures = [str(item) for item in validation["failures"]]  # type: ignore[index]
    if approval_phrase != expected_phrase:
        failures.append("approval_phrase must exactly match cortex_remember_plan for this payload")
    if failures:
        return {
            "target": str(target),
            "status": "FAIL",
            "operator": "remember",
            "mutability_class": "durable-memory-write",
            "approval_id": approval_id,
            "approval_status": "MISMATCH" if approval_phrase != expected_phrase else "MATCHED",
            "failures": failures,
            "writes": [],
            "derived_writes": [],
        }

    result = cortex.remember(
        target,
        str(payload["cell"]),
        str(payload["claim"]),
        [str(item) for item in payload["evidence"]],  # type: ignore[index]
        str(payload["summary"]) if payload["summary"] is not None else None,
        [str(item) for item in payload["links"]],  # type: ignore[index]
        authorized=True,
        update_existing=False,
    )
    result["operator"] = "remember"
    result["mutability_class"] = "durable-memory-write"
    result["approval_id"] = approval_id
    result["approval_status"] = "MATCHED"
    result["route"] = "mcp-governed-write"
    result.setdefault("derived_writes", [str(cortex.RECALL_DB)] if result.get("status") == "PASS" else [])
    return result


def list_events(default_target: Path, args: dict[str, Any]) -> dict[str, object]:
    target = resolve_target(default_target, args)
    result = event_ledger.list_events(target)
    events = list(result.get("events", []))
    status_filter = str(args.get("status", "")).strip().upper()
    lifecycle_filter = str(args.get("lifecycle", "")).strip()
    limit = int(args.get("limit", 50))
    if status_filter:
        events = [event for event in events if str(event.get("status", "")).upper() == status_filter]
    if lifecycle_filter:
        events = [event for event in events if str(event.get("lifecycle", "")) == lifecycle_filter]
    result["events"] = events[:limit]
    result["returned_count"] = len(result["events"])
    result["filters"] = {
        "status": status_filter or None,
        "lifecycle": lifecycle_filter or None,
        "limit": limit,
    }
    result["writes"] = []
    result["derived_writes"] = []
    return result


def get_event_status(default_target: Path, args: dict[str, Any]) -> dict[str, object]:
    target = resolve_target(default_target, args)
    event_id = str(args.get("event_id", "")).strip()
    if not event_id:
        return {"target": str(target), "status": "FAIL", "failures": ["event_id is required"], "writes": []}
    events, failures = event_ledger.read_events(target)
    for event in events:
        if str(event.get("id", "")) == event_id:
            return {
                "target": str(target),
                "status": "FAIL" if failures else "PASS",
                "event_id": event_id,
                "event_status": event.get("status"),
                "event": event,
                "failures": failures,
                "writes": [],
                "derived_writes": [],
            }
    return {
        "target": str(target),
        "status": "FAIL",
        "event_id": event_id,
        "failures": [f"event not found: {event_id}", *failures],
        "writes": [],
        "derived_writes": [],
    }


def read_cell(default_target: Path, args: dict[str, Any]) -> dict[str, Any]:
    target = resolve_target(default_target, args)
    verify_result = verify_target(target)
    if verify_result["status"] != "PASS":
        return {"target": str(target), "status": "FAIL", "failures": verify_result["failures"]}

    raw_cell = str(args.get("cell", "")).strip()
    if not raw_cell:
        return {"target": str(target), "status": "FAIL", "failures": ["cell is required"]}

    cell_rel = Path(raw_cell)
    if cell_rel.is_absolute() or ".." in cell_rel.parts:
        return {"target": str(target), "status": "FAIL", "failures": ["cell must stay under cells/**"]}
    if cell_rel.suffix != ".md":
        cell_rel = cell_rel.with_suffix(".md")

    cells_root = (cortex.cortex_path(target) / "cells").resolve()
    cell_path = (cells_root / cell_rel).resolve()
    try:
        cell_path.relative_to(cells_root)
    except ValueError:
        return {"target": str(target), "status": "FAIL", "failures": ["cell must stay under cells/**"]}
    if not cell_path.is_file():
        return {"target": str(target), "status": "FAIL", "failures": [f"cell missing: {cell_rel}"]}

    return {
        "target": str(target),
        "status": "PASS",
        "path": cortex.rel(cell_path, target),
        "text": cortex.read_text(cell_path),
    }


def trail_heading_match(line: str) -> re.Match[str] | None:
    return TRAIL_ENTRY_HEADING.match(line.strip())


def trail_entry_value(lines: list[str], prefix: str) -> str | None:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return None


def first_trail_detail(lines: list[str]) -> str | None:
    for line in lines:
        stripped = line.strip()
        if stripped:
            return stripped
    return None


def parse_cell_trail_entries(trail_text: str, wanted_cell: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    current: dict[str, str] | None = None
    current_lines: list[str] = []

    def flush_current() -> None:
        if current is None or current["cell"] != wanted_cell:
            return
        claim_summary = trail_entry_value(current_lines, "Claim:") or first_trail_detail(current_lines)
        entries.append({
            "date": current["date"],
            "event": current["event"],
            "cell": current["cell"],
            "claim_summary": claim_summary,
            "evidence_ref": trail_entry_value(current_lines, "Evidence:"),
            "links_delta": trail_entry_value(current_lines, "Links:"),
        })

    for line in trail_text.splitlines():
        match = trail_heading_match(line)
        if match:
            flush_current()
            current = {
                "date": match.group("date"),
                "event": match.group("event").strip(),
                "cell": match.group("cell").strip(),
            }
            current_lines = []
            continue
        if current is not None:
            current_lines.append(line)
    flush_current()
    return entries


def cell_history(default_target: Path, args: dict[str, Any]) -> dict[str, object]:
    target = resolve_target(default_target, args)
    verify_result = verify_target(target)
    if verify_result["status"] != "PASS":
        return {
            "target": str(target),
            "status": "FAIL",
            "failures": verify_result["failures"],
            "writes": [],
            "derived_writes": [],
        }

    raw_cell = string_arg(args, "cell")
    if not raw_cell:
        return {
            "target": str(target),
            "status": "FAIL",
            "failures": ["cell is required"],
            "writes": [],
            "derived_writes": [],
        }
    try:
        cell_path = cortex.resolve_cell_path(target, raw_cell)
    except ValueError as exc:
        return {
            "target": str(target),
            "status": "FAIL",
            "failures": [str(exc)],
            "writes": [],
            "derived_writes": [],
        }
    if not cell_path.is_file():
        return {
            "target": str(target),
            "status": "FAIL",
            "failures": [f"cell missing: {cortex.normalize_cell_rel(raw_cell)}"],
            "writes": [],
            "derived_writes": [],
        }

    root = cortex.cells_root(target).resolve()
    cell_reference = cortex.cell_ref(cell_path, root)
    trail_path = cortex.cortex_path(target) / "TRAIL.md"
    entries = parse_cell_trail_entries(cortex.read_text(trail_path), cell_reference) if trail_path.is_file() else []
    return {
        "target": str(target),
        "status": "PASS",
        "cell": cell_reference,
        "trail_path": cortex.rel(trail_path, target),
        "entries": entries,
        "writes": [],
        "derived_writes": [],
    }


def cell_resource_uri(cell_path: Path, cells_root: Path) -> str:
    cell_ref = cell_path.relative_to(cells_root).with_suffix("").as_posix()
    return f"{CELL_RESOURCE_PREFIX}{cell_ref}"


def list_cell_resources(default_target: Path, args: dict[str, Any]) -> dict[str, Any]:
    target = resolve_target(default_target, args)
    verify_result = verify_target(target)
    if verify_result["status"] != "PASS":
        raise ValueError("; ".join(str(item) for item in verify_result["failures"]))
    root = cortex.cells_root(target).resolve()
    resources = [
        {
            "uri": cell_resource_uri(path, root),
            "name": path.relative_to(root).with_suffix("").as_posix(),
            "mimeType": "text/markdown",
        }
        for path in sorted(root.rglob("*.md"))
        if path.is_file()
    ]
    return {"resources": resources}


def read_cell_resource(default_target: Path, args: dict[str, Any]) -> dict[str, Any]:
    target = resolve_target(default_target, args)
    raw_uri = args.get("uri", "")
    if not isinstance(raw_uri, str) or not raw_uri.startswith(CELL_RESOURCE_PREFIX):
        raise ValueError("resource uri must start with tes-cortex://cells/")
    cell_ref = raw_uri[len(CELL_RESOURCE_PREFIX):]
    if not cell_ref:
        raise ValueError("resource uri must name a cell")
    cell_path = cortex.resolve_cell_path(target, cell_ref)
    root = cortex.cells_root(target).resolve()
    try:
        cell_path.relative_to(root)
    except ValueError as exc:
        raise ValueError("resource uri must stay under cells/**") from exc
    if not cell_path.is_file():
        raise ValueError(f"resource cell missing: {cell_ref}")
    return {
        "contents": [
            {
                "uri": raw_uri,
                "mimeType": "text/markdown",
                "text": cell_path.read_text(encoding="utf-8"),
            }
        ]
    }


def list_prompts() -> dict[str, Any]:
    return {
        "prompts": [
            {
                "name": name,
                "title": prompt["title"],
                "description": prompt["description"],
            }
            for name, prompt in PROMPT_REGISTRY.items()
        ]
    }


def get_prompt(args: dict[str, Any]) -> dict[str, Any]:
    name = args.get("name", "")
    if not isinstance(name, str) or name not in PROMPT_REGISTRY:
        raise ValueError("unknown prompt")
    prompt = PROMPT_REGISTRY[name]
    body = f"{prompt['body']}\n\nPrompt version: {prompt['version']}."
    return {
        "description": prompt["description"],
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": body,
                },
            }
        ],
    }


def call_tool(
    default_target: Path,
    name: str,
    args: dict[str, Any],
    writes_enabled: bool = True,
    progress_callback: Any = None,
    progress_token: object | None = None,
) -> dict[str, Any]:
    resolve_target(default_target, args)
    if name in WRITE_TOOL_NAMES and not writes_enabled:
        return tool_result({
            "target": str(default_target),
            "status": "BLOCKED",
            "failures": ["governed MCP remember tools are disabled because the server started read-only"],
            "writes": [],
            "derived_writes": [],
        }, True)
    if name == "cortex_verify":
        return tool_result(verify_target(resolve_target(default_target, args)))
    if name == "cortex_health":
        return tool_result(cortex.health(resolve_target(default_target, args)))
    if name == "cortex_peek":
        query = str(args.get("query", "")).strip() or None
        cell = str(args.get("cell", "")).strip() or None
        limit = int(args.get("limit", 10))
        force_rg = bool(args.get("force_rg", False))
        return tool_result(cortex.peek(resolve_target(default_target, args), query, cell, limit, force_rg))
    if name == "cortex_review":
        backend = str(args.get("backend", "lexical")).strip() or "lexical"
        if backend not in {"auto", "xenova", "lexical"}:
            return tool_result({"status": "FAIL", "failures": ["backend must be auto, xenova, or lexical"]}, True)
        query = str(args.get("query", "")).strip() or None
        limit = int(args.get("limit", 20))
        line_budget = int(args.get("line_budget", 500))
        emit_progress(progress_callback, progress_token, 1, 3, "review: audit, curation, and reflection started")
        result = cortex.review(resolve_target(default_target, args), query, limit, line_budget, backend)
        emit_progress(progress_callback, progress_token, 3, 3, "review: completed")
        return tool_result(result)
    if name == "cortex_audit":
        emit_progress(progress_callback, progress_token, 1, 2, "audit: started")
        result = cortex.audit(resolve_target(default_target, args))
        emit_progress(progress_callback, progress_token, 2, 2, "audit: completed")
        return tool_result(result)
    if name == "cortex_recall":
        query = str(args.get("query", "")).strip()
        if not query:
            return tool_result({"status": "FAIL", "failures": ["query is required"]}, True)
        limit = int(args.get("limit", 10))
        force_rg = bool(args.get("force_rg", False))
        return tool_result(cortex.recall(resolve_target(default_target, args), query, limit, force_rg))
    if name == "cortex_read_cell":
        return tool_result(read_cell(default_target, args))
    if name == "cortex_cell_history":
        return tool_result(cell_history(default_target, args))
    if name == "cortex_absorb_plan":
        source = args.get("source")
        if not source:
            return tool_result({"status": "FAIL", "failures": ["source is required"]}, True)
        return tool_result(cortex.absorb_plan(resolve_target(default_target, args), Path(str(source))))
    if name == "cortex_curate_plan":
        backend = str(args.get("backend", "lexical")).strip() or "lexical"
        if backend not in {"auto", "xenova", "lexical"}:
            return tool_result({"status": "FAIL", "failures": ["backend must be auto, xenova, or lexical"]}, True)
        if backend != "lexical":
            emit_progress(progress_callback, progress_token, 1, 2, "curation: semantic backend started")
        result = cortex.curate_plan(resolve_target(default_target, args), backend, write_index=False)
        if backend != "lexical":
            emit_progress(progress_callback, progress_token, 2, 2, "curation: completed")
        return tool_result(result)
    if name == "cortex_reflect":
        query = str(args.get("query", "")).strip() or None
        limit = int(args.get("limit", 20))
        line_budget = int(args.get("line_budget", 500))
        return tool_result(cortex.reflect(resolve_target(default_target, args), query, limit, line_budget))
    if name == "cortex_list_events":
        return tool_result(list_events(default_target, args))
    if name == "cortex_get_event_status":
        return tool_result(get_event_status(default_target, args))
    if name == "cortex_remember_plan":
        return tool_result(remember_plan(default_target, args))
    if name == "cortex_remember":
        return tool_result(remember_apply(default_target, args))
    raise ValueError(f"unknown tool: {name}")


def response(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error_response(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle_message(
    default_target: Path,
    message: dict[str, Any],
    writes_enabled: bool = True,
    progress_callback: Any = None,
) -> dict[str, Any] | None:
    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}

    if request_id is None:
        return None
    if method == "initialize":
        client_version = params.get("protocolVersion") or PROTOCOL_VERSION
        return response(request_id, {
            "protocolVersion": client_version,
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"listChanged": False},
                "prompts": {"listChanged": False},
            },
            "serverInfo": {
                "name": "tes-cortex-mcp",
                "title": "TES Cortex MCP",
                "version": VERSION,
            },
            "instructions": (
                "Cortex access. Markdown artifacts remain the source of truth; SQLite is "
                "derived recall and rg is fallback. Governed remember tools are available "
                "by default and can write only through the two-step "
                "cortex_remember_plan/cortex_remember approval lane. Start with "
                "--read-only to hide durable-memory write tools."
            ),
        })
    if method == "ping":
        return response(request_id, {})
    if method == "tools/list":
        return response(request_id, {"tools": tool_definitions(writes_enabled)})
    if method == "resources/list":
        try:
            return response(request_id, list_cell_resources(default_target, params if isinstance(params, dict) else {}))
        except ValueError as exc:
            return error_response(request_id, -32602, str(exc))
    if method == "resources/read":
        if not isinstance(params, dict):
            return error_response(request_id, -32602, "resource arguments must be an object")
        try:
            return response(request_id, read_cell_resource(default_target, params))
        except ValueError as exc:
            return error_response(request_id, -32602, str(exc))
    if method == "prompts/list":
        return response(request_id, list_prompts())
    if method == "prompts/get":
        if not isinstance(params, dict):
            return error_response(request_id, -32602, "prompt arguments must be an object")
        try:
            return response(request_id, get_prompt(params))
        except ValueError as exc:
            return error_response(request_id, -32602, str(exc))
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") if "arguments" in params else {}
        meta = params.get("_meta") if isinstance(params, dict) else {}
        progress_token = meta.get("progressToken") if isinstance(meta, dict) else None
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            return error_response(request_id, -32602, "tool arguments must be an object")
        try:
            return response(
                request_id,
                call_tool(default_target, str(name), arguments, writes_enabled, progress_callback, progress_token),
            )
        except ValueError as exc:
            return error_response(request_id, -32602, str(exc))
        except Exception as exc:  # MCP transport should stay alive for client correction.
            return response(request_id, tool_result({"status": "FAIL", "failures": [str(exc)]}, True))
    return error_response(request_id, -32601, f"method not found: {method}")


def handle_json_payload(
    default_target: Path,
    message: Any,
    writes_enabled: bool = True,
    progress_callback: Any = None,
) -> dict[str, Any] | list[dict[str, Any]] | None:
    messages = message if isinstance(message, list) else [message]
    replies = [
        handle_message(default_target, item, writes_enabled, progress_callback)
        if isinstance(item, dict)
        else error_response(None, -32600, "request must be an object")
        for item in messages
    ]
    replies = [item for item in replies if item is not None]
    if not replies:
        return None
    return replies if isinstance(message, list) else replies[0]


def serve(default_target: Path, writes_enabled: bool = True) -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
            notifications: list[dict[str, Any]] = []
            payload = handle_json_payload(default_target, message, writes_enabled, notifications.append)
            if payload is None:
                continue
            for notification in notifications:
                print(json.dumps(notification, separators=(",", ":")), flush=True)
            print(json.dumps(payload, separators=(",", ":")), flush=True)
        except json.JSONDecodeError as exc:
            print(json.dumps(error_response(None, -32700, f"parse error: {exc}")), flush=True)
    return 0


class CortexHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def make_http_handler(default_target: Path, writes_enabled: bool) -> type[BaseHTTPRequestHandler]:
    class CortexHTTPHandler(BaseHTTPRequestHandler):
        server_version = "TESCortexMCPHTTP/1.0"

        def send_json(self, status: int, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
            encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def do_POST(self) -> None:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self.send_json(411, error_response(None, -32600, "invalid content length"))
                return
            try:
                message = json.loads(self.rfile.read(length).decode("utf-8"))
                notifications: list[dict[str, Any]] = []
                payload = handle_json_payload(default_target, message, writes_enabled, notifications.append)
                if payload is None:
                    self.send_json(204, {})
                    return
                if notifications:
                    payload = [*notifications, *(payload if isinstance(payload, list) else [payload])]
                self.send_json(200, payload)
            except json.JSONDecodeError as exc:
                self.send_json(400, error_response(None, -32700, f"parse error: {exc}"))
            except Exception as exc:  # Keep HTTP framing alive for caller correction.
                self.send_json(200, error_response(None, -32603, str(exc)))

        def log_message(self, format: str, *args: object) -> None:
            return

    return CortexHTTPHandler


def validate_http_bind(host: str, allow_non_localhost: bool = False) -> None:
    if host not in LOCAL_HTTP_HOSTS and not allow_non_localhost:
        raise ValueError("HTTP transport binds to localhost by default; pass --allow-non-localhost to bind elsewhere")


def make_http_server(default_target: Path, writes_enabled: bool, host: str, port: int) -> CortexHTTPServer:
    return CortexHTTPServer((host, port), make_http_handler(default_target, writes_enabled))


def serve_http(
    default_target: Path,
    writes_enabled: bool = True,
    host: str = "127.0.0.1",
    port: int = 8765,
    allow_non_localhost: bool = False,
) -> int:
    validate_http_bind(host, allow_non_localhost)
    if host not in LOCAL_HTTP_HOSTS:
        print(f"[cortex-mcp] WARNING: HTTP transport binding to non-localhost host {host}", file=sys.stderr)
    with make_http_server(default_target, writes_enabled, host, port) as server:
        print(f"[cortex-mcp] HTTP listening on http://{host}:{server.server_port}", file=sys.stderr)
        server.serve_forever()
    return 0


def self_test() -> int:
    global SELF_TEST_MODE
    previous_self_test_mode = SELF_TEST_MODE
    SELF_TEST_MODE = True
    with tempfile.TemporaryDirectory(prefix="tes-cortex-mcp-") as tempdir:
        target = Path(tempdir) / "project-a"
        cortex.init(target)
        source = cortex.cortex_path(target) / "sources" / "mcp-source.md"
        source.write_text("# MCP Source\n\nCortex exposes governed MCP tools.\n", encoding="utf-8")
        cell = cortex.cortex_path(target) / "cells" / "mcp-existing.md"
        cell.write_text(
            "# MCP Existing\n\n"
            "## Claim\n\n"
            "The MCP surface delegates to the Cortex CLI contract and gates durable writes.\n\n"
            "## Evidence\n\n"
            "- `sources/mcp-source.md` records the MCP source fixture.\n",
            encoding="utf-8",
        )
        map_path = cortex.cortex_path(target) / "MAP.md"
        map_path.write_text(cortex.read_text(map_path) + "\n| [[mcp-existing]] | MCP gates durable writes | |\n", encoding="utf-8")
        links_path = cortex.cortex_path(target) / "LINKS.md"
        links_path.write_text(cortex.read_text(links_path) + "\n- [[mcp-existing]] -> `sources/mcp-source.md`\n", encoding="utf-8")
        cortex.rebuild(target)
        cortex.semantic_db_path(target).unlink(missing_ok=True)
        events_dir = target / ".tes" / "events"
        events_dir.mkdir(parents=True, exist_ok=True)
        event_fixture = {
            "schema": event_ledger.SCHEMA,
            "id": "mcp-event-pass",
            "created_at": "2026-05-27T00:00:00Z",
            "lifecycle": "authorized_write",
            "status": "PASS",
            "surface": "mcp",
            "summary": "MCP event fixture",
            "evidence_ref": "none",
            "scope": {
                "adapter": "mcp",
                "agent": "cortex-mcp",
                "run": "mcp-self-test",
                "source": "event-ledger",
                "evidence_ref": "none",
                "status": "PASS",
            },
            "facts": {"tool": "cortex_remember"},
        }
        (events_dir / "ledger.jsonl").write_text(json.dumps(event_fixture, sort_keys=True) + "\n", encoding="utf-8")

        SELF_TEST_MODE = False
        VERIFY_CACHE.clear()
        for key in VERIFY_CACHE_STATS:
            VERIFY_CACHE_STATS[key] = 0
        first_verify = verify_target(target)
        second_verify = verify_target(target)
        if first_verify["status"] != "PASS" or second_verify["status"] != "PASS":
            failures_for_cache = ["verify cache fixture did not start from PASS"]
        else:
            failures_for_cache = []
        if VERIFY_CACHE_STATS["hits"] != 1 or VERIFY_CACHE_STATS["misses"] != 1:
            failures_for_cache.append(f"verify cache did not record one miss and one hit: {VERIFY_CACHE_STATS}")
        cell.write_text(cell.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        invalidated_verify = verify_target(target)
        if invalidated_verify["status"] != "PASS" or VERIFY_CACHE_STATS["misses"] != 2:
            failures_for_cache.append("verify cache did not invalidate after touched cell")
        SELF_TEST_MODE = True
        verify_target(target)
        if VERIFY_CACHE_STATS["bypasses"] != 1:
            failures_for_cache.append("verify cache was not bypassed in self-test mode")

        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": PROTOCOL_VERSION}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "cortex_verify", "arguments": {}}},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "cortex_health", "arguments": {}}},
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "cortex_peek", "arguments": {"query": "MCP"}}},
            {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "cortex_peek", "arguments": {"cell": "mcp-existing"}}},
            {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "cortex_review", "arguments": {"backend": "lexical"}}},
            {"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {"name": "cortex_recall", "arguments": {"query": "MCP"}}},
            {"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "cortex_read_cell", "arguments": {"cell": "mcp-existing"}}},
            {"jsonrpc": "2.0", "id": 10, "method": "tools/call", "params": {"name": "cortex_absorb_plan", "arguments": {"source": "docs/agents/cortex/sources/mcp-source.md"}}},
            {"jsonrpc": "2.0", "id": 11, "method": "tools/call", "params": {"name": "cortex_curate_plan", "arguments": {"backend": "lexical"}}},
            {"jsonrpc": "2.0", "id": 12, "method": "tools/call", "params": {"name": "cortex_reflect", "arguments": {"query": "MCP closure should consider memory capture"}}},
            {"jsonrpc": "2.0", "id": 13, "method": "tools/call", "params": {"name": "cortex_list_events", "arguments": {"status": "PASS"}}},
            {"jsonrpc": "2.0", "id": 14, "method": "tools/call", "params": {"name": "cortex_get_event_status", "arguments": {"event_id": "mcp-event-pass"}}},
        ]
        replies = [handle_message(target.resolve(), message) for message in messages]
        failures: list[str] = failures_for_cache

        tool_names = {
            tool["name"]
            for tool in replies[1]["result"]["tools"]  # type: ignore[index]
        }
        expected_tools = {
            "cortex_verify",
            "cortex_health",
            "cortex_peek",
            "cortex_review",
            "cortex_audit",
            "cortex_recall",
            "cortex_read_cell",
            "cortex_cell_history",
            "cortex_absorb_plan",
            "cortex_curate_plan",
            "cortex_reflect",
            "cortex_list_events",
            "cortex_get_event_status",
            "cortex_remember_plan",
            "cortex_remember",
        }
        if tool_names != expected_tools:
            failures.append(f"tool list mismatch: {sorted(tool_names)}")
        recall_schema = next(
            tool["inputSchema"]
            for tool in replies[1]["result"]["tools"]  # type: ignore[index]
            if tool["name"] == "cortex_recall"
        )
        expected_recall_schema = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Recall query."},
                "limit": {"type": "integer", "description": "Maximum matches.", "minimum": 1, "default": 10},
                "force_rg": {
                    "type": "boolean",
                    "description": "Force rg fallback instead of SQLite FTS5.",
                    "default": False,
                },
            },
            "required": ["query"],
        }
        if recall_schema != expected_recall_schema:
            failures.append("schema helper changed cortex_recall JSONSchema shape")
        if "resources" not in replies[0]["result"].get("capabilities", {}):  # type: ignore[index]
            failures.append("initialize did not advertise resources capability")
        resource_list_message = {"jsonrpc": "2.0", "id": 15, "method": "resources/list"}
        resource_read_message = {
            "jsonrpc": "2.0",
            "id": 16,
            "method": "resources/read",
            "params": {"uri": f"{CELL_RESOURCE_PREFIX}mcp-existing"},
        }
        resource_list_reply = handle_message(target.resolve(), resource_list_message)
        resource_read_reply = handle_message(target.resolve(), resource_read_message)
        if resource_list_reply is None:
            failures.append("resources/list returned no reply")
        else:
            resource_uris = {
                item.get("uri")
                for item in resource_list_reply["result"]["resources"]  # type: ignore[index]
            }
            if resource_uris != {f"{CELL_RESOURCE_PREFIX}mcp-existing"}:
                failures.append(f"resources/list exposed unexpected resources: {sorted(resource_uris)}")
        if resource_read_reply is None:
            failures.append("resources/read returned no reply")
        else:
            contents = resource_read_reply["result"]["contents"]  # type: ignore[index]
            if contents[0].get("text") != cell.read_text(encoding="utf-8"):
                failures.append("resources/read did not match on-disk cell bytes")
        for label, uri in (
            ("non-cell resource rejected", "tes-cortex://sources/mcp-source"),
            ("resource traversal rejected", f"{CELL_RESOURCE_PREFIX}../TRAIL"),
        ):
            reply = handle_message(
                target.resolve(),
                {"jsonrpc": "2.0", "id": 17, "method": "resources/read", "params": {"uri": uri}},
            )
            if reply is None or "error" not in reply:
                failures.append(label)

        empty_history_reply = handle_message(
            target.resolve(),
            {
                "jsonrpc": "2.0",
                "id": 171,
                "method": "tools/call",
                "params": {"name": "cortex_cell_history", "arguments": {"cell": "mcp-existing"}},
            },
        )
        if empty_history_reply is None:
            failures.append("cell history returned no reply for empty history")
        else:
            empty_history = empty_history_reply["result"]["structuredContent"]  # type: ignore[index]
            if empty_history.get("status") != "PASS" or empty_history.get("entries") != []:
                failures.append(f"empty cell history should pass with no entries: {empty_history}")
            if empty_history.get("writes") != [] or empty_history.get("derived_writes") != []:
                failures.append("empty cell history reported writes")

        history_cell = cortex.cortex_path(target) / "cells" / "mcp-history.md"
        history_cell.write_text(
            "# MCP History\n\n"
            "## Claim\n\n"
            "Structured history reads Cortex trail entries without writing.\n\n"
            "## Evidence\n\n"
            "- `sources/mcp-source.md` records the history fixture.\n",
            encoding="utf-8",
        )
        map_path.write_text(
            cortex.read_text(map_path) + "\n| [[mcp-history]] | MCP history fixture | [[mcp-existing]] |\n",
            encoding="utf-8",
        )
        links_path.write_text(
            cortex.read_text(links_path)
            + "\n- [[mcp-history]] -> `sources/mcp-source.md`\n"
            + "- [[mcp-history]] -> [[mcp-existing]]\n",
            encoding="utf-8",
        )
        trail_path = cortex.cortex_path(target) / "TRAIL.md"
        trail_path.write_text(
            cortex.read_text(trail_path)
            + "\n## [2026-05-27] apply | mcp-history\n"
            + "Claim: History fixture claim.\n"
            + "Evidence: `sources/mcp-source.md`\n"
            + "Links: +[[mcp-existing]]\n",
            encoding="utf-8",
        )
        history_message = {
            "jsonrpc": "2.0",
            "id": 172,
            "method": "tools/call",
            "params": {"name": "cortex_cell_history", "arguments": {"cell": "mcp-history"}},
        }
        history_reply = handle_message(target.resolve(), history_message)
        if history_reply is None:
            failures.append("cell history returned no reply")
        else:
            history_result = history_reply["result"]["structuredContent"]  # type: ignore[index]
            history_entries = history_result.get("entries", [])
            if history_result.get("status") != "PASS" or len(history_entries) != 1:
                failures.append(f"cell history did not return one structured entry: {history_result}")
            else:
                entry = history_entries[0]
                if entry.get("date") != "2026-05-27" or entry.get("event") != "apply":
                    failures.append(f"cell history parsed heading incorrectly: {entry}")
                if entry.get("claim_summary") != "History fixture claim.":
                    failures.append(f"cell history claim summary mismatch: {entry}")
                if entry.get("evidence_ref") != "`sources/mcp-source.md`":
                    failures.append(f"cell history evidence ref mismatch: {entry}")
                if entry.get("links_delta") != "+[[mcp-existing]]":
                    failures.append(f"cell history links delta mismatch: {entry}")
            if history_result.get("writes") != [] or history_result.get("derived_writes") != []:
                failures.append("cell history reported writes")

        history_traversal_reply = handle_message(
            target.resolve(),
            {
                "jsonrpc": "2.0",
                "id": 173,
                "method": "tools/call",
                "params": {"name": "cortex_cell_history", "arguments": {"cell": "../TRAIL"}},
            },
        )
        if history_traversal_reply is None or not history_traversal_reply.get("result", {}).get("isError"):
            failures.append("cell history traversal was not rejected")
        if "prompts" not in replies[0]["result"].get("capabilities", {}):  # type: ignore[index]
            failures.append("initialize did not advertise prompts capability")
        prompt_list_message = {"jsonrpc": "2.0", "id": 18, "method": "prompts/list"}
        prompt_list_reply = handle_message(target.resolve(), prompt_list_message)
        expected_prompts = {
            "cortex/closure-reflection",
            "cortex/curation-review",
            "cortex/remember-checklist",
        }
        if prompt_list_reply is None:
            failures.append("prompts/list returned no reply")
        else:
            prompt_names = {
                item.get("name")
                for item in prompt_list_reply["result"]["prompts"]  # type: ignore[index]
            }
            if prompt_names != expected_prompts:
                failures.append(f"prompts/list mismatch: {sorted(prompt_names)}")
        forbidden_prompt_terms = ("tools/call", "approval_phrase", "/Users", "/home", "token", "secret", "password")
        prompt_get_replies: dict[str, dict[str, Any]] = {}
        for prompt_name in sorted(expected_prompts):
            prompt_message = {
                "jsonrpc": "2.0",
                "id": 19,
                "method": "prompts/get",
                "params": {"name": prompt_name},
            }
            reply = handle_message(target.resolve(), prompt_message)
            if reply is None:
                failures.append(f"prompts/get returned no reply for {prompt_name}")
                continue
            prompt_get_replies[prompt_name] = reply
            messages_payload = reply["result"].get("messages", [])  # type: ignore[index]
            body = str(messages_payload[0].get("content", {}).get("text", "")) if messages_payload else ""
            if not body.strip():
                failures.append(f"prompt body is empty: {prompt_name}")
            for term in forbidden_prompt_terms:
                if term in body:
                    failures.append(f"prompt body contains forbidden term {term!r}: {prompt_name}")
        bad_prompt_reply = handle_message(
            target.resolve(),
            {"jsonrpc": "2.0", "id": 191, "method": "prompts/get", "params": {"name": "unsafe"}},
        )
        if bad_prompt_reply is None or "error" not in bad_prompt_reply:
            failures.append("unknown prompt was not rejected")
        tools_with_target = [
            tool["name"]
            for tool in replies[1]["result"]["tools"]  # type: ignore[index]
            if "target" in tool.get("inputSchema", {}).get("properties", {})
        ]
        if tools_with_target:
            failures.append(f"tool schemas expose target override: {sorted(tools_with_target)}")
        forbidden_tools = {
            name for name in tool_names
            if any(term in name for term in ("apply", "learn", "write", "mutate", "hook", "config"))
        }
        if forbidden_tools:
            failures.append(f"write-capable or unsafe tools exposed: {sorted(forbidden_tools)}")
        for reply in replies[2:]:
            result = reply["result"]  # type: ignore[index]
            if result.get("isError"):
                failures.append(result["content"][0]["text"])
        if replies[3]["result"]["structuredContent"].get("mutability_class") != "read-only":  # type: ignore[index]
            failures.append("health did not report read-only mutability")
        if replies[4]["result"]["structuredContent"].get("mutability_class") != "read-only":  # type: ignore[index]
            failures.append("peek did not report read-only mutability")
        if replies[6]["result"]["structuredContent"].get("writes") != []:  # type: ignore[index]
            failures.append("review reported writes over MCP")
        if replies[6]["result"]["structuredContent"].get("derived_writes") != []:  # type: ignore[index]
            failures.append("review reported derived writes over MCP")
        peek_matches = replies[4]["result"]["structuredContent"].get("matches", [])  # type: ignore[index]
        if not peek_matches:
            failures.append("peek query did not return recall result")
        if "MCP Existing" not in replies[5]["result"]["structuredContent"]["text"]:  # type: ignore[index]
            failures.append("peek cell did not return cell text")
        if "MCP Existing" not in replies[8]["result"]["structuredContent"]["text"]:  # type: ignore[index]
            failures.append("read_cell did not return cell text")
        if replies[10]["result"]["structuredContent"]["writes"] != []:  # type: ignore[index]
            failures.append("curate_plan did not remain no-write over MCP")
        if replies[10]["result"]["structuredContent"].get("derived_writes") != []:  # type: ignore[index]
            failures.append("curate_plan reported derived writes over MCP")
        if cortex.semantic_db_path(target).exists():
            failures.append("MCP curate_plan created a derived semantic index")
        if replies[12]["result"]["structuredContent"].get("returned_count") != 1:  # type: ignore[index]
            failures.append("event list did not return the PASS fixture")
        if replies[13]["result"]["structuredContent"].get("event_status") != "PASS":  # type: ignore[index]
            failures.append("event status did not return PASS fixture")
        if replies[12]["result"]["structuredContent"].get("writes") != []:  # type: ignore[index]
            failures.append("event list reported writes over MCP")
        if replies[13]["result"]["structuredContent"].get("writes") != []:  # type: ignore[index]
            failures.append("event status reported writes over MCP")

        enabled_tools = {tool["name"] for tool in tool_definitions(writes_enabled=True)}
        read_only_tools = {tool["name"] for tool in tool_definitions(writes_enabled=False)}
        if tool_names != enabled_tools:
            failures.append("default MCP tools must match governed-write-enabled tools")
        if "cortex_remember_plan" not in enabled_tools or "cortex_remember" not in enabled_tools:
            failures.append("default MCP did not expose governed remember tools")
        if "cortex_remember_plan" in read_only_tools or "cortex_remember" in read_only_tools:
            failures.append("read-only MCP exposed governed remember tools")
        unsafe_enabled = sorted(
            name for name in enabled_tools
            if any(term in name for term in ("forget", "delete", "update", "checkpoint", "apply"))
        )
        if unsafe_enabled:
            failures.append(f"default MCP exposed unsafe tools: {unsafe_enabled}")

        remember_args = {
            "cell": "mcp-governed-write",
            "claim": "Governed MCP remember writes one new Cortex cell only after exact approval.",
            "evidence": ["sources/mcp-source.md"],
            "summary": "Governed MCP remember lane",
            "links": ["mcp-existing"],
        }
        planned_cell = cortex.cortex_path(target) / "cells" / "mcp-governed-write.md"
        plan_reply = handle_message(
            target.resolve(),
            {
                "jsonrpc": "2.0",
                "id": 20,
                "method": "tools/call",
                "params": {"name": "cortex_remember_plan", "arguments": remember_args},
            },
        )
        if plan_reply is None:
            failures.append("remember plan returned no reply")
            approval_phrase = ""
        else:
            plan_result = plan_reply["result"]["structuredContent"]  # type: ignore[index]
            approval_phrase = str(plan_result.get("approval_phrase", ""))
            if plan_result.get("status") != "PASS" or plan_result.get("writes") != []:
                failures.append(f"remember plan should pass without writes: {plan_result}")
            if planned_cell.exists():
                failures.append("remember plan created a Cortex cell")

        disabled_reply = handle_message(
            target.resolve(),
            {
                "jsonrpc": "2.0",
                "id": 21,
                "method": "tools/call",
                "params": {
                    "name": "cortex_remember",
                    "arguments": {**remember_args, "approval_phrase": approval_phrase},
                },
            },
            writes_enabled=False,
        )
        if disabled_reply is None or not disabled_reply.get("result", {}).get("isError"):
            failures.append("remember must be blocked when server starts read-only")

        bad_approval_reply = handle_message(
            target.resolve(),
            {
                "jsonrpc": "2.0",
                "id": 22,
                "method": "tools/call",
                "params": {
                    "name": "cortex_remember",
                    "arguments": {**remember_args, "approval_phrase": "bad approval"},
                },
            },
        )
        if bad_approval_reply is None:
            failures.append("bad approval remember returned no reply")
        else:
            bad_result = bad_approval_reply["result"]["structuredContent"]  # type: ignore[index]
            if bad_result.get("status") != "FAIL" or bad_result.get("writes") != []:
                failures.append("bad approval remember must fail without writes")
            if planned_cell.exists():
                failures.append("bad approval remember created a Cortex cell")

        non_string_plan_reply = handle_message(
            target.resolve(),
            {
                "jsonrpc": "2.0",
                "id": 221,
                "method": "tools/call",
                "params": {
                    "name": "cortex_remember_plan",
                    "arguments": {**remember_args, "cell": 123},
                },
            },
        )
        if non_string_plan_reply is None or "error" not in non_string_plan_reply:
            failures.append("remember plan must reject non-string cell arguments")
        if planned_cell.exists():
            failures.append("non-string remember plan created a Cortex cell")

        remember_reply = handle_message(
            target.resolve(),
            {
                "jsonrpc": "2.0",
                "id": 23,
                "method": "tools/call",
                "params": {
                    "name": "cortex_remember",
                    "arguments": {**remember_args, "approval_phrase": approval_phrase},
                },
            },
        )
        if remember_reply is None:
            failures.append("approved remember returned no reply")
        else:
            remember_result = remember_reply["result"]["structuredContent"]  # type: ignore[index]
            if remember_result.get("status") != "PASS":
                failures.append(f"approved remember should pass: {remember_result}")
            writes = remember_result.get("writes", [])
            if "docs/agents/cortex/cells/mcp-governed-write.md" not in writes:
                failures.append(f"approved remember did not report cell write: {writes}")
            if remember_result.get("approval_status") != "MATCHED":
                failures.append("approved remember did not report matched approval")
            if not planned_cell.exists():
                failures.append("approved remember did not create the Cortex cell")

        duplicate_reply = handle_message(
            target.resolve(),
            {
                "jsonrpc": "2.0",
                "id": 24,
                "method": "tools/call",
                "params": {
                    "name": "cortex_remember",
                    "arguments": {**remember_args, "approval_phrase": approval_phrase},
                },
            },
        )
        if duplicate_reply is None:
            failures.append("duplicate remember returned no reply")
        else:
            duplicate_result = duplicate_reply["result"]["structuredContent"]  # type: ignore[index]
            if duplicate_result.get("status") != "FAIL" or duplicate_result.get("writes") != []:
                failures.append("duplicate remember must fail without writes")

        sibling_target = Path(tempdir) / "project-b"
        cortex.init(sibling_target)
        sibling_cell = cortex.cortex_path(sibling_target) / "cells" / "foreign-memory.md"
        sibling_cell.write_text(
            "# Foreign Memory\n\n"
            "## Claim\n\n"
            "A different project must not be readable through this MCP server.\n\n"
            "## Evidence\n\n"
            "- `sources/README.md`\n",
            encoding="utf-8",
        )
        map_path = cortex.cortex_path(sibling_target) / "MAP.md"
        map_path.write_text(
            cortex.read_text(map_path) + "\n| [[foreign-memory]] | Foreign project fixture | |\n",
            encoding="utf-8",
        )
        cross_project_messages = [
            ("cortex_verify", {"target": str(sibling_target)}),
            ("cortex_health", {"target": str(sibling_target)}),
            ("cortex_peek", {"target": str(sibling_target), "query": "Foreign Memory"}),
            ("cortex_review", {"target": str(sibling_target)}),
            ("cortex_audit", {"target": str(sibling_target)}),
            ("cortex_recall", {"target": str(sibling_target), "query": "Foreign Memory"}),
            ("cortex_read_cell", {"target": str(sibling_target), "cell": "foreign-memory"}),
            ("cortex_cell_history", {"target": str(sibling_target), "cell": "foreign-memory"}),
            ("cortex_absorb_plan", {"target": str(sibling_target), "source": "docs/agents/cortex/sources/README.md"}),
            ("cortex_curate_plan", {"target": str(sibling_target), "backend": "lexical"}),
            ("cortex_reflect", {"target": str(sibling_target), "query": "Foreign Memory"}),
            ("cortex_list_events", {"target": str(sibling_target)}),
            ("cortex_get_event_status", {"target": str(sibling_target), "event_id": "foreign"}),
        ]
        for name, arguments in cross_project_messages:
            reply = handle_message(
                target.resolve(),
                {"jsonrpc": "2.0", "id": 1000, "method": "tools/call", "params": {"name": name, "arguments": arguments}},
            )
            if reply is None:
                failures.append(f"{name} target override: no reply")
            elif "error" not in reply:
                failures.append(f"{name} target override was not rejected")

        negative_messages = [
            (
                "unknown write-like tool rejected",
                {"jsonrpc": "2.0", "id": 101, "method": "tools/call", "params": {"name": "cortex_apply", "arguments": {}}},
            ),
            (
                "empty remember payload rejected",
                {"jsonrpc": "2.0", "id": 1011, "method": "tools/call", "params": {"name": "cortex_remember", "arguments": {}}},
            ),
            (
                "unknown checkpoint tool rejected",
                {"jsonrpc": "2.0", "id": 1012, "method": "tools/call", "params": {"name": "cortex_checkpoint", "arguments": {}}},
            ),
            (
                "path traversal rejected",
                {"jsonrpc": "2.0", "id": 102, "method": "tools/call", "params": {"name": "cortex_read_cell", "arguments": {"cell": "../CONTRACT.md"}}},
            ),
            (
                "target override rejected",
                {"jsonrpc": "2.0", "id": 103, "method": "tools/call", "params": {"name": "cortex_verify", "arguments": {"target": str(target / "missing")}}},
            ),
            (
                "invalid backend rejected",
                {"jsonrpc": "2.0", "id": 104, "method": "tools/call", "params": {"name": "cortex_curate_plan", "arguments": {"backend": "unsafe"}}},
            ),
            (
                "empty recall query rejected",
                {"jsonrpc": "2.0", "id": 105, "method": "tools/call", "params": {"name": "cortex_recall", "arguments": {"query": ""}}},
            ),
            (
                "empty read-cell argument rejected",
                {"jsonrpc": "2.0", "id": 106, "method": "tools/call", "params": {"name": "cortex_read_cell", "arguments": {"cell": ""}}},
            ),
            (
                "empty cell-history argument rejected",
                {"jsonrpc": "2.0", "id": 1061, "method": "tools/call", "params": {"name": "cortex_cell_history", "arguments": {"cell": ""}}},
            ),
            (
                "empty absorb source rejected",
                {"jsonrpc": "2.0", "id": 107, "method": "tools/call", "params": {"name": "cortex_absorb_plan", "arguments": {"source": ""}}},
            ),
            (
                "empty event id rejected",
                {"jsonrpc": "2.0", "id": 1071, "method": "tools/call", "params": {"name": "cortex_get_event_status", "arguments": {"event_id": ""}}},
            ),
            (
                "non-object arguments rejected",
                {"jsonrpc": "2.0", "id": 108, "method": "tools/call", "params": {"name": "cortex_verify", "arguments": []}},
            ),
        ]
        for label, message in negative_messages:
            reply = handle_message(target.resolve(), message)
            if reply is None:
                failures.append(f"{label}: no reply")
                continue
            if "error" in reply:
                continue
            result = reply.get("result", {})
            if not result.get("isError"):
                failures.append(f"{label}: call was not rejected")

        progress_message = {
            "jsonrpc": "2.0",
            "id": 109,
            "method": "tools/call",
            "params": {
                "name": "cortex_review",
                "arguments": {"backend": "lexical"},
                "_meta": {"progressToken": "mcp-progress"},
            },
        }
        progress_notifications: list[dict[str, Any]] = []
        progress_reply = handle_message(target.resolve(), progress_message, progress_callback=progress_notifications.append)
        if progress_reply is None or progress_reply.get("result", {}).get("isError"):
            failures.append("progress review call did not complete")
        if not any(item.get("method") == "notifications/progress" for item in progress_notifications):
            failures.append("progress review call emitted no progress notification")

        def failing_progress_callback(_notification: dict[str, Any]) -> None:
            raise RuntimeError("simulated progress notification failure")

        progress_failure_reply = handle_message(
            target.resolve(),
            progress_message,
            progress_callback=failing_progress_callback,
        )
        if progress_failure_reply is None or progress_failure_reply.get("result", {}).get("isError"):
            failures.append("progress notification failure should not fail the tool result")

        def http_rpc(url: str, message: dict[str, Any]) -> dict[str, Any]:
            request = urllib_request.Request(
                url,
                data=json.dumps(message).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib_request.urlopen(request, timeout=5) as response_body:
                return json.loads(response_body.read().decode("utf-8"))

        try:
            validate_http_bind("0.0.0.0", allow_non_localhost=False)
            failures.append("non-localhost HTTP bind did not require explicit flag")
        except ValueError:
            pass

        http_server = make_http_server(target.resolve(), True, "127.0.0.1", 0)
        http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        http_thread.start()
        http_url = f"http://127.0.0.1:{http_server.server_port}/mcp"
        try:
            http_init = http_rpc(http_url, messages[0])
            http_tools = http_rpc(http_url, messages[1])
            http_verify = http_rpc(http_url, messages[2])
            stdio_resource_list_now = handle_message(target.resolve(), resource_list_message)
            stdio_resource_read_now = handle_message(target.resolve(), resource_read_message)
            http_resource_list = http_rpc(http_url, resource_list_message)
            http_resource_read = http_rpc(http_url, resource_read_message)
            http_prompt_list = http_rpc(http_url, prompt_list_message)
            http_progress = http_rpc(http_url, progress_message)
            stdio_history_now = handle_message(target.resolve(), history_message)
            http_history = http_rpc(http_url, history_message)
            if http_init != replies[0]:
                failures.append("HTTP initialize envelope differed from stdio")
            if http_tools != replies[1]:
                failures.append("HTTP tools/list envelope differed from stdio")
            if http_verify != replies[2]:
                failures.append("HTTP verify envelope differed from stdio")
            if http_resource_list != stdio_resource_list_now:
                failures.append("HTTP resources/list envelope differed from stdio")
            if http_resource_read != stdio_resource_read_now:
                failures.append("HTTP resources/read envelope differed from stdio")
            if http_prompt_list != prompt_list_reply:
                failures.append("HTTP prompts/list envelope differed from stdio")
            if http_history != stdio_history_now:
                failures.append("HTTP cell history envelope differed from stdio")
            for prompt_name, stdio_prompt_reply in prompt_get_replies.items():
                http_prompt = http_rpc(
                    http_url,
                    {
                        "jsonrpc": "2.0",
                        "id": 192,
                        "method": "prompts/get",
                        "params": {"name": prompt_name},
                    },
                )
                if http_prompt.get("result") != stdio_prompt_reply.get("result"):
                    failures.append(f"HTTP prompts/get envelope differed from stdio: {prompt_name}")
            if not isinstance(http_progress, list) or not any(
                item.get("method") == "notifications/progress" for item in http_progress
            ):
                failures.append("HTTP progress response did not include progress notification")

            http_bad_approval_args = {
                "cell": "mcp-http-write",
                "claim": "HTTP remember requires exact approval just like stdio.",
                "evidence": ["sources/mcp-source.md"],
                "approval_phrase": "bad approval",
            }
            http_bad_approval = http_rpc(
                http_url,
                {
                    "jsonrpc": "2.0",
                    "id": 25,
                    "method": "tools/call",
                    "params": {"name": "cortex_remember", "arguments": http_bad_approval_args},
                },
            )
            bad_http_result = http_bad_approval.get("result", {}).get("structuredContent", {})
            if bad_http_result.get("status") != "FAIL" or bad_http_result.get("writes") != []:
                failures.append("HTTP bad approval remember must fail without writes")
        finally:
            http_server.shutdown()
            http_server.server_close()
            http_thread.join(timeout=5)

        read_only_http_server = make_http_server(target.resolve(), False, "127.0.0.1", 0)
        read_only_thread = threading.Thread(target=read_only_http_server.serve_forever, daemon=True)
        read_only_thread.start()
        read_only_url = f"http://127.0.0.1:{read_only_http_server.server_port}/mcp"
        try:
            read_only_tools_reply = http_rpc(read_only_url, messages[1])
            read_only_http_tools = {
                tool["name"]
                for tool in read_only_tools_reply["result"]["tools"]  # type: ignore[index]
            }
            if "cortex_remember" in read_only_http_tools or "cortex_remember_plan" in read_only_http_tools:
                failures.append("read-only HTTP tools/list exposed governed remember tools")
            read_only_remember = http_rpc(
                read_only_url,
                {
                    "jsonrpc": "2.0",
                    "id": 26,
                    "method": "tools/call",
                    "params": {"name": "cortex_remember", "arguments": http_bad_approval_args},
                },
            )
            if not read_only_remember.get("result", {}).get("isError"):
                failures.append("read-only HTTP remember call was not blocked")
        finally:
            read_only_http_server.shutdown()
            read_only_http_server.server_close()
            read_only_thread.join(timeout=5)

        field_reports.safe_record_event(
            target,
            "cortex_mcp.self_test",
            "FAIL" if failures else "PASS",
            "mcp",
            "self-test",
            details={"tools": len(expected_tools), "failures": len(failures)},
        )
        print(json.dumps({"status": "FAIL" if failures else "PASS", "failures": failures}, indent=2))
        if failures:
            print("[cortex-mcp] FAIL")
            SELF_TEST_MODE = previous_self_test_mode
            return 1
    print("[cortex-mcp] PASS")
    SELF_TEST_MODE = previous_self_test_mode
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument(
        "--enable-writes",
        action="store_true",
        help="compatibility flag; governed Cortex remember tools are enabled by default",
    )
    parser.add_argument("--read-only", action="store_true", help="hide governed Cortex remember tools")
    parser.add_argument("--disable-writes", action="store_true", help="alias for --read-only")
    parser.add_argument("--transport", choices=("stdio", "http"), default="stdio")
    parser.add_argument("--host", default="127.0.0.1", help="HTTP bind host; defaults to localhost")
    parser.add_argument("--port", type=int, default=8765, help="HTTP bind port")
    parser.add_argument("--allow-non-localhost", action="store_true", help="allow HTTP bind outside localhost")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if args.enable_writes and (args.read_only or args.disable_writes):
        parser.error("--enable-writes cannot be combined with --read-only/--disable-writes")
    writes_enabled = not (args.read_only or args.disable_writes)
    target = args.target.expanduser().resolve()
    if args.transport == "http":
        try:
            return serve_http(target, writes_enabled, args.host, args.port, args.allow_non_localhost)
        except ValueError as exc:
            parser.error(str(exc))
    return serve(target, writes_enabled)


if __name__ == "__main__":
    sys.exit(main())
