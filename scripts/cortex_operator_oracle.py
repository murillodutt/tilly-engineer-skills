#!/usr/bin/env python3
"""Validate Cortex operator mutability boundaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

import cortex
import cortex_mcp


VERSION = "0.3.204"


def sha256_bytes(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


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


def prepare_target(target: Path) -> None:
    cortex.init(target)
    source = cortex.cortex_path(target) / "sources" / "operator-source.md"
    source.write_text("# Operator Source\n\nCortex operator layer has explicit mutability classes.\n", encoding="utf-8")
    cell = cortex.cortex_path(target) / "cells" / "operator-existing.md"
    cell.write_text(
        "# Operator Existing\n\n"
        "## Claim\n\n"
        "Operator inspection reads Cortex memory without writing durable memory.\n\n"
        "## Evidence\n\n"
        "- `sources/operator-source.md`\n",
        encoding="utf-8",
    )
    map_path = cortex.cortex_path(target) / "MAP.md"
    map_path.write_text(cortex.read_text(map_path) + "\n| [[operator-existing]] | Operator inspection is read-only | |\n", encoding="utf-8")
    links_path = cortex.cortex_path(target) / "LINKS.md"
    links_path.write_text(cortex.read_text(links_path) + "\n- [[operator-existing]] -> `sources/operator-source.md`\n", encoding="utf-8")
    cortex.rebuild(target)


def self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-cortex-operator-") as tempdir:
        target = Path(tempdir) / "target-project"
        prepare_target(target)

        before_read = snapshot(target)
        read_results = {
            "health": cortex.health(target),
            "peek_query": cortex.peek(target, "Operator", None, 5),
            "peek_cell": cortex.peek(target, None, "operator-existing", 5),
            "review": cortex.review(target, None, 5, 500, "lexical"),
        }
        after_read = snapshot(target)
        if before_read != after_read:
            failures.append(f"read-only operators changed files: {changed_paths(before_read, after_read)}")
        for name, result in read_results.items():
            if result.get("status") not in {"PASS", "NEEDS_REVIEW", "DEGRADED"}:
                failures.append(f"{name} returned unexpected status: {result.get('status')}")
            if result.get("writes") != [] or result.get("derived_writes") != []:
                failures.append(f"{name} reported writes: {result.get('writes')} / {result.get('derived_writes')}")
            if result.get("mutability_class") != "read-only":
                failures.append(f"{name} mutability class mismatch: {result.get('mutability_class')}")

        before_checkpoint_block = snapshot(target)
        checkpoint_blocked = cortex.checkpoint_operator(
            target,
            checkpoint_id="operator",
            ttl_seconds=60,
            summary="Operator checkpoint",
            state={"phase": "operator"},
            authorized=False,
        )
        after_checkpoint_block = snapshot(target)
        if checkpoint_blocked.get("status") != "NEEDS_AUTH" or checkpoint_blocked.get("writes") != []:
            failures.append("checkpoint without authorization must be NEEDS_AUTH with no writes")
        if before_checkpoint_block != after_checkpoint_block:
            failures.append("unauthorized checkpoint mutated files")

        before_checkpoint = snapshot(target)
        checkpoint_written = cortex.checkpoint_operator(
            target,
            checkpoint_id="operator",
            ttl_seconds=60,
            summary="Operator checkpoint",
            state={"phase": "operator"},
            authorized=True,
        )
        after_checkpoint = snapshot(target)
        if checkpoint_written.get("status") != "PASS":
            failures.append(f"authorized checkpoint should pass: {checkpoint_written.get('failures')}")
        if changed_paths(before_checkpoint, after_checkpoint) != [".tes/checkpoints/operator.json"]:
            failures.append(f"checkpoint wrote outside checkpoint lane: {changed_paths(before_checkpoint, after_checkpoint)}")

        before_remember_block = snapshot(target)
        remember_blocked = cortex.remember(
            target,
            "operator-memory",
            "Authorized memory writes require evidence.",
            ["sources/operator-source.md"],
            None,
            [],
            authorized=False,
            update_existing=False,
        )
        after_remember_block = snapshot(target)
        if remember_blocked.get("status") != "NEEDS_AUTH" or remember_blocked.get("writes") != []:
            failures.append("remember without authorization must be NEEDS_AUTH with no writes")
        if before_remember_block != after_remember_block:
            failures.append("unauthorized remember mutated files")

        before_missing_evidence = snapshot(target)
        missing_evidence = cortex.remember(
            target,
            "operator-memory",
            "Authorized memory writes require evidence.",
            [],
            None,
            [],
            authorized=True,
            update_existing=False,
        )
        after_missing_evidence = snapshot(target)
        if missing_evidence.get("status") != "FAIL" or missing_evidence.get("writes") != []:
            failures.append("remember without evidence must fail without writes")
        if before_missing_evidence != after_missing_evidence:
            failures.append("missing-evidence remember mutated files")

        before_remember = snapshot(target)
        remember_written = cortex.remember(
            target,
            "operator-memory",
            "Authorized operator memory writes require evidence and approval.",
            ["sources/operator-source.md"],
            "Operator write gate.",
            ["operator-existing"],
            authorized=True,
            update_existing=False,
        )
        after_remember = snapshot(target)
        changed = changed_paths(before_remember, after_remember)
        expected_prefixes = {
            ".tes/cortex/recall.sqlite",
            "docs/agents/cortex/LINKS.md",
            "docs/agents/cortex/MAP.md",
            "docs/agents/cortex/TRAIL.md",
            "docs/agents/cortex/cells/operator-memory.md",
        }
        if remember_written.get("status") != "PASS":
            failures.append(f"authorized remember should pass: {remember_written.get('failures')}")
        if set(changed) != expected_prefixes:
            failures.append(f"remember wrote unexpected files: {changed}")

        before_forget_block = snapshot(target)
        forget_blocked = cortex.forget(target, "operator-memory", ["sources/operator-source.md"], authorized=False)
        after_forget_block = snapshot(target)
        if forget_blocked.get("status") != "NEEDS_AUTH" or forget_blocked.get("writes") != []:
            failures.append("forget without authorization must be NEEDS_AUTH with no writes")
        if before_forget_block != after_forget_block:
            failures.append("unauthorized forget mutated files")

        before_forget = snapshot(target)
        forget_authorized = cortex.forget(target, "operator-memory", ["sources/operator-source.md"], authorized=True)
        after_forget = snapshot(target)
        if forget_authorized.get("status") != "BLOCKED" or forget_authorized.get("writes") != []:
            failures.append("authorized forget must stay BLOCKED until consolidation gate")
        if before_forget != after_forget:
            failures.append("blocked forget mutated files")

        mcp_tools = {tool["name"] for tool in cortex_mcp.tool_definitions()}
        for required in ("cortex_health", "cortex_peek", "cortex_review", "cortex_remember_plan", "cortex_remember"):
            if required not in mcp_tools:
                failures.append(f"MCP missing default governed operator: {required}")
        for forbidden in ("checkpoint", "forget", "delete", "update", "apply", "write", "mutate"):
            exposed = sorted(name for name in mcp_tools if forbidden in name)
            if exposed:
                failures.append(f"MCP exposed unsafe operator terms: {exposed}")
        read_only_mcp_tools = {tool["name"] for tool in cortex_mcp.tool_definitions(writes_enabled=False)}
        for required in ("cortex_health", "cortex_peek", "cortex_review"):
            if required not in read_only_mcp_tools:
                failures.append(f"MCP missing read-only operator: {required}")
        for hidden in ("cortex_remember_plan", "cortex_remember"):
            if hidden in read_only_mcp_tools:
                failures.append(f"read-only MCP exposed governed operator: {hidden}")
        for forbidden in ("checkpoint", "forget", "delete", "update", "apply"):
            exposed = sorted(name for name in mcp_tools if forbidden in name)
            if exposed:
                failures.append(f"default MCP exposed unsafe operator terms: {exposed}")

    result = {"version": VERSION, "status": "FAIL" if failures else "PASS", "failures": failures}
    print(json.dumps(result, indent=2, sort_keys=True))
    if failures:
        print("[cortex-operator] FAIL")
        return 1
    print("[cortex-operator] PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    parser.error("--self-test is required")


if __name__ == "__main__":
    raise SystemExit(main())
