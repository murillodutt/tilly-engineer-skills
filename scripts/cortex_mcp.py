#!/usr/bin/env python3
"""Expose TES Cortex read-only tools over MCP stdio."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

import cortex
import field_reports


VERSION = "0.3.137"
PROTOCOL_VERSION = "2025-06-18"


def schema_string(description: str) -> dict[str, str]:
    return {"type": "string", "description": description}


def schema_integer(description: str, default: int | None = None) -> dict[str, object]:
    schema: dict[str, object] = {"type": "integer", "description": description, "minimum": 1}
    if default is not None:
        schema["default"] = default
    return schema


def tool_definitions() -> list[dict[str, object]]:
    return [
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
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": schema_string("Recall query."),
                    "limit": schema_integer("Maximum matches.", 10),
                    "force_rg": {
                        "type": "boolean",
                        "description": "Force rg fallback instead of SQLite FTS5.",
                        "default": False,
                    },
                },
                "required": ["query"],
            },
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
    ]


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


def resolve_target(default_target: Path, args: dict[str, Any]) -> Path:
    if "target" in args:
        raise ValueError("target argument is not accepted; restart the server with --target")
    return default_target


def read_cell(default_target: Path, args: dict[str, Any]) -> dict[str, Any]:
    target = resolve_target(default_target, args)
    verify_result = cortex.verify(target)
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


def call_tool(default_target: Path, name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name == "cortex_verify":
        return tool_result(cortex.verify(resolve_target(default_target, args)))
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
        return tool_result(cortex.review(resolve_target(default_target, args), query, limit, line_budget, backend))
    if name == "cortex_audit":
        return tool_result(cortex.audit(resolve_target(default_target, args)))
    if name == "cortex_recall":
        query = str(args.get("query", "")).strip()
        if not query:
            return tool_result({"status": "FAIL", "failures": ["query is required"]}, True)
        limit = int(args.get("limit", 10))
        force_rg = bool(args.get("force_rg", False))
        return tool_result(cortex.recall(resolve_target(default_target, args), query, limit, force_rg))
    if name == "cortex_read_cell":
        return tool_result(read_cell(default_target, args))
    if name == "cortex_absorb_plan":
        source = args.get("source")
        if not source:
            return tool_result({"status": "FAIL", "failures": ["source is required"]}, True)
        return tool_result(cortex.absorb_plan(resolve_target(default_target, args), Path(str(source))))
    if name == "cortex_curate_plan":
        backend = str(args.get("backend", "lexical")).strip() or "lexical"
        if backend not in {"auto", "xenova", "lexical"}:
            return tool_result({"status": "FAIL", "failures": ["backend must be auto, xenova, or lexical"]}, True)
        return tool_result(cortex.curate_plan(resolve_target(default_target, args), backend, write_index=False))
    if name == "cortex_reflect":
        query = str(args.get("query", "")).strip() or None
        limit = int(args.get("limit", 20))
        line_budget = int(args.get("line_budget", 500))
        return tool_result(cortex.reflect(resolve_target(default_target, args), query, limit, line_budget))
    raise ValueError(f"unknown tool: {name}")


def response(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error_response(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle_message(default_target: Path, message: dict[str, Any]) -> dict[str, Any] | None:
    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}

    if request_id is None:
        return None
    if method == "initialize":
        client_version = params.get("protocolVersion") or PROTOCOL_VERSION
        return response(request_id, {
            "protocolVersion": client_version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {
                "name": "tes-cortex-mcp",
                "title": "TES Cortex MCP",
                "version": VERSION,
            },
            "instructions": (
                "Read-only Cortex access. Markdown artifacts remain the source of truth; "
                "SQLite is derived recall and rg is fallback."
            ),
        })
    if method == "ping":
        return response(request_id, {})
    if method == "tools/list":
        return response(request_id, {"tools": tool_definitions()})
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") if "arguments" in params else {}
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            return error_response(request_id, -32602, "tool arguments must be an object")
        try:
            return response(request_id, call_tool(default_target, str(name), arguments))
        except ValueError as exc:
            return error_response(request_id, -32602, str(exc))
        except Exception as exc:  # MCP transport should stay alive for client correction.
            return response(request_id, tool_result({"status": "FAIL", "failures": [str(exc)]}, True))
    return error_response(request_id, -32601, f"method not found: {method}")


def serve(default_target: Path) -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
            messages = message if isinstance(message, list) else [message]
            replies = [handle_message(default_target, item) for item in messages]
            replies = [item for item in replies if item is not None]
            if not replies:
                continue
            payload: dict[str, Any] | list[dict[str, Any]] = replies if isinstance(message, list) else replies[0]
            print(json.dumps(payload, separators=(",", ":")), flush=True)
        except json.JSONDecodeError as exc:
            print(json.dumps(error_response(None, -32700, f"parse error: {exc}")), flush=True)
    return 0


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="tes-cortex-mcp-") as tempdir:
        target = Path(tempdir) / "project-a"
        cortex.init(target)
        source = cortex.cortex_path(target) / "sources" / "mcp-source.md"
        source.write_text("# MCP Source\n\nCortex exposes read-only MCP tools.\n", encoding="utf-8")
        cell = cortex.cortex_path(target) / "cells" / "mcp-read-only.md"
        cell.write_text(
            "# MCP Read Only\n\n"
            "## Claim\n\n"
            "The MCP surface is read-only and delegates to the Cortex CLI contract.\n\n"
            "## Evidence\n\n"
            "- `sources/mcp-source.md` records the MCP source fixture.\n",
            encoding="utf-8",
        )
        map_path = cortex.cortex_path(target) / "MAP.md"
        map_path.write_text(cortex.read_text(map_path) + "\n| [[mcp-read-only]] | MCP is read-only | |\n", encoding="utf-8")
        links_path = cortex.cortex_path(target) / "LINKS.md"
        links_path.write_text(cortex.read_text(links_path) + "\n- [[mcp-read-only]] -> `sources/mcp-source.md`\n", encoding="utf-8")
        cortex.rebuild(target)
        cortex.semantic_db_path(target).unlink(missing_ok=True)

        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": PROTOCOL_VERSION}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "cortex_verify", "arguments": {}}},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "cortex_health", "arguments": {}}},
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "cortex_peek", "arguments": {"query": "MCP"}}},
            {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "cortex_peek", "arguments": {"cell": "mcp-read-only"}}},
            {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "cortex_review", "arguments": {"backend": "lexical"}}},
            {"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {"name": "cortex_recall", "arguments": {"query": "MCP"}}},
            {"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "cortex_read_cell", "arguments": {"cell": "mcp-read-only"}}},
            {"jsonrpc": "2.0", "id": 10, "method": "tools/call", "params": {"name": "cortex_absorb_plan", "arguments": {"source": "docs/agents/cortex/sources/mcp-source.md"}}},
            {"jsonrpc": "2.0", "id": 11, "method": "tools/call", "params": {"name": "cortex_curate_plan", "arguments": {"backend": "lexical"}}},
            {"jsonrpc": "2.0", "id": 12, "method": "tools/call", "params": {"name": "cortex_reflect", "arguments": {"query": "MCP closure should consider memory capture"}}},
        ]
        replies = [handle_message(target.resolve(), message) for message in messages]
        failures: list[str] = []

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
            "cortex_absorb_plan",
            "cortex_curate_plan",
            "cortex_reflect",
        }
        if tool_names != expected_tools:
            failures.append(f"tool list mismatch: {sorted(tool_names)}")
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
        if "MCP Read Only" not in replies[5]["result"]["structuredContent"]["text"]:  # type: ignore[index]
            failures.append("peek cell did not return cell text")
        if "MCP Read Only" not in replies[8]["result"]["structuredContent"]["text"]:  # type: ignore[index]
            failures.append("read_cell did not return cell text")
        if replies[10]["result"]["structuredContent"]["writes"] != []:  # type: ignore[index]
            failures.append("curate_plan did not remain no-write over MCP")
        if replies[10]["result"]["structuredContent"].get("derived_writes") != []:  # type: ignore[index]
            failures.append("curate_plan reported derived writes over MCP")
        if cortex.semantic_db_path(target).exists():
            failures.append("MCP curate_plan created a derived semantic index")

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
            ("cortex_absorb_plan", {"target": str(sibling_target), "source": "docs/agents/cortex/sources/README.md"}),
            ("cortex_curate_plan", {"target": str(sibling_target), "backend": "lexical"}),
            ("cortex_reflect", {"target": str(sibling_target), "query": "Foreign Memory"}),
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
                "unknown remember tool rejected",
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
                "empty absorb source rejected",
                {"jsonrpc": "2.0", "id": 107, "method": "tools/call", "params": {"name": "cortex_absorb_plan", "arguments": {"source": ""}}},
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
            return 1
    print("[cortex-mcp] PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    return serve(args.target.expanduser().resolve())


if __name__ == "__main__":
    sys.exit(main())
