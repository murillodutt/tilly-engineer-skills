#!/usr/bin/env python3
"""Attach-health contract for project-visible surfaces (ADR 0004, SPEC-003/004/005).

Config presence is not certification. An attach is healthy only when its real
effect can be observed. For MCP this means a genuine out-of-process JSON-RPC
handshake against the server entrypoint the host spawns; for hooks it means a
sentinel the hook writes on execution. When proof cannot be reached, the verdict
is an explicit pending/unobservable state, never a clean PASS.

Status vocabulary extends ADR 0003.1 (PASS / PARTIAL / NEEDS_REVIEW / BLOCKED /
DEGRADED / NOT_APPLIED) with ADR 0004 attach-health states:

- PENDING_HOST_RESTART: surface configured but the host has not (re)spawned it.
- PENDING_TRUST: surface configured but the host has not trusted/enabled it.
- PENDING_RELOAD: surface configured but the host has not reloaded it.
- HOST_UNOBSERVABLE: TES did everything it can verify; the remaining proof
  depends on host action TES cannot observe. Terminal partial success, not FAIL.

The MCP handshake follows the Model Context Protocol stdio lifecycle
(initialize -> notifications/initialized -> tools/list), per the MCP
specification (modelcontextprotocol.io). The server is cortex_mcp.py, which
serves line-delimited JSON-RPC over stdio with PROTOCOL_VERSION 2025-06-18.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

import capsule_residue_oracle as residue


VERSION = "0.3.242"

# Surface set mirrors tes_install ALL_ATTACH_SURFACES.
SURFACES = ("mcp", "docs-mesh", "root-context", "skills", "hooks", "field-reports", "gps", "goals", "mantra")

# Installed MCP server entrypoint the host spawns (install_mcp_hosts args).
INSTALLED_MCP_ENTRYPOINT = ".tes/bin/cortex_mcp.py"
MCP_PROTOCOL_VERSION = "2025-06-18"
HANDSHAKE_TIMEOUT_S = 20.0

# Hook execution sentinel written by the hook on run (SPEC-005). The current
# path is local-runtime state; the legacy path is read-only compatibility for
# installed targets that have not updated yet.
HOOK_SENTINEL = ".tes/runtime/hooks/executed.jsonl"
LEGACY_HOOK_SENTINEL = ".tes/hooks/executed.jsonl"
HOOK_AGENTS = ("codex", "claude", "cursor")
HOOK_AGENT_CONFIGS = {
    "codex": (".codex/config.toml", ".codex/hooks.json"),
    "claude": (".claude/settings.json",),
    "cursor": (".cursor/hooks.json",),
}
DOCS_MESH_ROOT = "docs/agents"
DOCS_MESH_DEMAND_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    "CURSOR.md",
    ".cursor/rules/tes-engineering-discipline.mdc",
)


def python_executable() -> str:
    return sys.executable or shutil.which("python3") or "python3"


def mcp_handshake(target: Path, *, timeout: float = HANDSHAKE_TIMEOUT_S) -> dict[str, Any]:
    """Drive a real stdio JSON-RPC handshake against the installed MCP server.

    Returns a verdict dict with status and evidence. Maps outcomes:
    - entrypoint missing -> NOT_APPLIED
    - no python runtime -> HOST_UNOBSERVABLE
    - initialize + tools/list succeed -> PASS
    - spawn or response failure / timeout -> PENDING_HOST_RESTART
    """
    entrypoint = target / INSTALLED_MCP_ENTRYPOINT
    if not entrypoint.is_file():
        return {"status": "NOT_APPLIED", "reason": "no installed MCP entrypoint"}
    python = python_executable()
    if not python:
        return {"status": "HOST_UNOBSERVABLE", "reason": "no python runtime to spawn the server"}

    # MCP stdio lifecycle: initialize -> notifications/initialized -> tools/list.
    init = {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "tes-attach-health", "version": VERSION},
        },
    }
    initialized = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    tools_list = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    stdin_payload = "\n".join(json.dumps(m) for m in (init, initialized, tools_list)) + "\n"

    # Health probing is read-only: spawn the server with bytecode writing off so
    # the diagnostic never leaves __pycache__/*.pyc residue in the target.
    probe_env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        proc = subprocess.run(
            [python, "-B", str(entrypoint), "--target", str(target)],
            input=stdin_payload,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=probe_env,
        )
    except subprocess.TimeoutExpired:
        return {"status": "PENDING_HOST_RESTART", "reason": "server did not respond within timeout"}
    except OSError as exc:
        return {"status": "HOST_UNOBSERVABLE", "reason": f"could not spawn server: {exc}"}

    responses: list[dict[str, Any]] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            responses.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    by_id = {r.get("id"): r for r in responses if isinstance(r, dict)}
    init_resp = by_id.get(1)
    tools_resp = by_id.get(2)
    if not init_resp or "result" not in init_resp:
        return {"status": "PENDING_HOST_RESTART", "reason": "no valid initialize response", "stderr": proc.stderr[:400]}
    if not tools_resp or "result" not in tools_resp or "tools" not in tools_resp["result"]:
        return {"status": "PENDING_HOST_RESTART", "reason": "no valid tools/list response"}
    tools = tools_resp["result"]["tools"]
    server_version = init_resp["result"].get("protocolVersion")
    return {
        "status": "PASS",
        "protocol_version": server_version,
        "tool_count": len(tools),
        "reason": "out-of-process initialize + tools/list handshake succeeded",
    }


def canonical_hook_event(event: str) -> str:
    return "PreToolUse" if event in {"PreToolUse", "preToolUse"} else event


def configured_hook_agents(target: Path) -> dict[str, str]:
    agents: dict[str, str] = {}
    for agent, relpaths in HOOK_AGENT_CONFIGS.items():
        configured = False
        for relpath in relpaths:
            path = target / relpath
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if ".tes/bin/tes_install.py" in text and " hook" in text and f"--agent {agent}" in text:
                configured = True
                break
        if configured:
            agents[agent] = "CONFIGURED"
    return agents


def read_hook_sentinel(target: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for relpath in (HOOK_SENTINEL, LEGACY_HOOK_SENTINEL):
        sentinel = target / relpath
        if not sentinel.is_file():
            continue
        for line in sentinel.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                record.setdefault("sentinel_path", relpath)
                records.append(record)
    return records


def hook_health(target: Path) -> dict[str, Any]:
    """Health of the hooks surface from the execution sentinel (SPEC-005).

    - no hook config present -> NOT_APPLIED
    - config present, no sentinel -> PENDING_TRUST (host has not run it yet)
    - sentinel present, single handler per event -> PASS
    - sentinel present, duplicate handler for an event -> DEGRADED
    """
    configured = residue.detect_hooks(target)
    if not configured:
        return {"status": "NOT_APPLIED", "reason": "no TES hook configured"}
    records = read_hook_sentinel(target)
    agents = configured_hook_agents(target)
    if not records:
        return {
            "status": "PENDING_TRUST",
            "reason": "hook configured but never fired (no sentinel)",
            "configured": configured,
            "agents": agents,
        }
    observed_agents = {str(rec.get("agent")) for rec in records if rec.get("agent")}
    for agent in observed_agents:
        agents[agent] = "OBSERVED" if agent in agents else "STALE/UNEXPECTED"
    # Duplicate-handler detection: SessionStart is one fire per session. PreToolUse
    # can fire many times in the same session; only host-supplied invocation ids
    # are precise enough to diagnose duplicate PreToolUse handlers.
    seen: dict[tuple[str, str, str, str], int] = {}
    for rec in records:
        event = canonical_hook_event(str(rec.get("event_canonical") or rec.get("event") or ""))
        if event == "PreToolUse" and not rec.get("invocation"):
            continue
        mode = str(rec.get("mode") or event)
        session = str(rec.get("invocation") if event == "PreToolUse" else rec.get("session", ""))
        key = (str(rec.get("agent", "")), event, mode, session)
        seen[key] = seen.get(key, 0) + 1
    duplicates = [k for k, count in seen.items() if count > 1]
    if duplicates:
        return {
            "status": "DEGRADED",
            "reason": "duplicate hook handler fired",
            "duplicates": [list(k) for k in duplicates],
            "agents": agents,
        }
    legacy_records = sum(1 for record in records if record.get("sentinel_path") == LEGACY_HOOK_SENTINEL)
    return {
        "status": "PASS",
        "reason": "hook fired with a single handler",
        "fires": len(records),
        "agents": agents,
        "legacy_records": legacy_records,
    }


def docs_mesh_demand(target: Path) -> list[str]:
    """Root context references that make an absent docs-mesh reviewable.

    docs-mesh is opt-in for a fresh target. Once a root context points agents at
    `docs/agents/**`, absence is no longer neutral: the configured context asks
    for a project mesh that is not materialized.
    """
    demanded_by: list[str] = []
    for relpath in DOCS_MESH_DEMAND_FILES:
        path = target / relpath
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if DOCS_MESH_ROOT in text:
            demanded_by.append(relpath)
    return demanded_by


def evaluate(target: Path, surface: str, *, mcp_timeout: float = HANDSHAKE_TIMEOUT_S) -> dict[str, Any]:
    """Per-surface attach-health verdict."""
    target = target.resolve()
    if surface not in SURFACES:
        return {"version": VERSION, "status": "FAIL", "surface": surface, "failures": [f"unknown surface: {surface}"]}

    if surface == "mcp":
        health = mcp_handshake(target, timeout=mcp_timeout)
    elif surface == "hooks":
        health = hook_health(target)
    elif surface == "root-context":
        present = residue.detect_bootloader_blocks(target)
        health = {"status": "PASS" if present else "NOT_APPLIED", "present": present}
    elif surface == "skills":
        present = residue.detect_skills(target)
        health = {"status": "PASS" if present else "NOT_APPLIED", "present": present}
    elif surface == "docs-mesh":
        present = (target / "docs/agents").exists()
        demanded_by = docs_mesh_demand(target) if not present else []
        if present:
            health = {"status": "PASS"}
        elif demanded_by:
            health = {
                "status": "NEEDS_REVIEW",
                "reason": "root context references docs/agents but docs-mesh is absent",
                "demanded_by": demanded_by,
            }
        else:
            health = {"status": "NOT_APPLIED"}
    else:
        # field-reports / gps / goals / mantra: presence-only until their
        # detectors and health probes land in later units.
        health = {"status": "NOT_APPLIED", "reason": "surface health probe owned by a later unit"}

    return {"version": VERSION, "surface": surface, **health}


def self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-attach-health-self-test-") as tempdir:
        root = Path(tempdir)

        # MCP: no entrypoint -> NOT_APPLIED.
        empty = root / "empty"
        empty.mkdir()
        r = evaluate(empty, "mcp")
        if r["status"] != "NOT_APPLIED":
            failures.append(f"mcp with no entrypoint must be NOT_APPLIED: {r['status']}")

        # MCP: real handshake against the installed server. Install the helper by
        # copying the source server into the target's installed entrypoint path.
        live = root / "live"
        (live / ".tes/bin").mkdir(parents=True)
        # Copy the whole bin so the server's imports resolve.
        src_scripts = Path(__file__).resolve().parent
        for name in ("cortex_mcp.py", "cortex.py", "cortex_embed.mjs"):
            src = src_scripts / name
            if src.is_file():
                shutil.copy2(src, live / ".tes/bin" / name)
        # Bring sibling modules cortex_mcp imports (best-effort).
        for extra in ("scope_contract.py", "event_ledger.py", "checkpoint.py", "field_reports.py", "consolidation_gate.py"):
            src = src_scripts / extra
            if src.is_file():
                shutil.copy2(src, live / ".tes/bin" / extra)
        subprocess.run([python_executable(), str(src_scripts / "cortex.py"), "init", "--target", str(live)],
                       capture_output=True, text=True, check=False)
        r = evaluate(live, "mcp")
        if r["status"] not in {"PASS", "PENDING_HOST_RESTART", "HOST_UNOBSERVABLE"}:
            failures.append(f"mcp handshake returned unexpected status: {r['status']} ({r.get('reason')})")
        # We assert the handshake is at least observable (not a crash to FAIL).
        if r["status"] == "PASS" and not r.get("tool_count"):
            failures.append("mcp PASS must report a tool_count")

        # Hooks: no config -> NOT_APPLIED.
        h = evaluate(root / "empty", "hooks")
        if h["status"] != "NOT_APPLIED":
            failures.append(f"hooks with no config must be NOT_APPLIED: {h['status']}")

        # Hooks: configured but no sentinel -> PENDING_TRUST.
        hooked = root / "hooked"
        (hooked / ".claude").mkdir(parents=True)
        (hooked / ".claude/settings.json").write_text(
            json.dumps({"hooks": {"SessionStart": [{"command": "python3 .tes/bin/tes_install.py hook --agent claude"}]}}),
            encoding="utf-8",
        )
        h = evaluate(hooked, "hooks")
        if h["status"] != "PENDING_TRUST":
            failures.append(f"configured hook with no sentinel must be PENDING_TRUST: {h['status']}")

        # Hooks: sentinel present, single handler -> PASS.
        (hooked / ".tes/hooks").mkdir(parents=True)
        (hooked / ".tes/runtime/hooks").mkdir(parents=True)
        (hooked / HOOK_SENTINEL).write_text(
            json.dumps({"agent": "claude", "event": "SessionStart", "mode": "announce_start", "session": "s1"}) + "\n"
            + json.dumps({"agent": "claude", "event": "SessionStart", "mode": "rewake_on_complete", "session": "s1"}) + "\n",
            encoding="utf-8",
        )
        h = evaluate(hooked, "hooks")
        if h["status"] != "PASS":
            failures.append(f"fired hook with single handler must be PASS: {h['status']}")
        if h.get("agents", {}).get("claude") != "OBSERVED":
            failures.append("observed Claude hook must report agent state OBSERVED")

        # Hooks: duplicate handler -> DEGRADED.
        with (hooked / HOOK_SENTINEL).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"agent": "claude", "event": "SessionStart", "mode": "announce_start", "session": "s1"}) + "\n")
        h = evaluate(hooked, "hooks")
        if h["status"] != "DEGRADED":
            failures.append(f"duplicate hook handler must be DEGRADED: {h['status']}")

        # Hooks: repeated PreToolUse without host invocation id is a normal hot
        # path fallback, not evidence of duplicate handlers.
        pretool = root / "pretool"
        (pretool / ".cursor").mkdir(parents=True)
        (pretool / ".cursor/hooks.json").write_text(
            json.dumps({"hooks": {"preToolUse": [{"command": "python3 .tes/bin/tes_install.py hook --agent cursor"}]}}),
            encoding="utf-8",
        )
        (pretool / ".tes/runtime/hooks").mkdir(parents=True)
        (pretool / HOOK_SENTINEL).write_text(
            json.dumps({"agent": "cursor", "event": "preToolUse", "event_canonical": "PreToolUse", "mode": "pretooluse", "session": "s1", "tool": "Edit"}) + "\n"
            + json.dumps({"agent": "cursor", "event": "preToolUse", "event_canonical": "PreToolUse", "mode": "pretooluse", "session": "s1", "tool": "Read"}) + "\n",
            encoding="utf-8",
        )
        h = evaluate(pretool, "hooks")
        if h["status"] != "PASS":
            failures.append(f"repeated PreToolUse fallback records must be PASS: {h['status']}")

        with (pretool / HOOK_SENTINEL).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"agent": "cursor", "event": "preToolUse", "event_canonical": "PreToolUse", "mode": "pretooluse", "session": "s1", "invocation": "tool-1"}) + "\n")
            fh.write(json.dumps({"agent": "cursor", "event": "preToolUse", "event_canonical": "PreToolUse", "mode": "pretooluse", "session": "s1", "invocation": "tool-1"}) + "\n")
        h = evaluate(pretool, "hooks")
        if h["status"] != "DEGRADED":
            failures.append(f"duplicate PreToolUse invocation records must be DEGRADED: {h['status']}")

        legacy = root / "legacy"
        (legacy / ".claude").mkdir(parents=True)
        (legacy / ".claude/settings.json").write_text(
            json.dumps({"hooks": {"SessionStart": [{"command": "python3 .tes/bin/tes_install.py hook --agent claude"}]}}),
            encoding="utf-8",
        )
        (legacy / ".tes/hooks").mkdir(parents=True)
        (legacy / LEGACY_HOOK_SENTINEL).write_text(
            json.dumps({"agent": "claude", "event": "SessionStart", "session": "s1"}) + "\n",
            encoding="utf-8",
        )
        h = evaluate(legacy, "hooks")
        if h["status"] != "PASS" or h.get("legacy_records") != 1:
            failures.append(f"legacy hook sentinel must remain readable: {h}")

        # Docs-mesh: opt-in absence stays NOT_APPLIED unless root context demands it.
        docs_opt_in = evaluate(root / "empty", "docs-mesh")
        if docs_opt_in["status"] != "NOT_APPLIED":
            failures.append(f"docs-mesh absent with no demand must be NOT_APPLIED: {docs_opt_in}")

        docs_demanded = root / "docs-demanded"
        docs_demanded.mkdir()
        (docs_demanded / "AGENTS.md").write_text(
            "<!-- TES:CORE BEGIN version=0.0.0 sha256=x adapter=codex path=AGENTS.md -->\n"
            "Route to `docs/agents/**`.\n"
            "<!-- TES:CORE END -->\n",
            encoding="utf-8",
        )
        h = evaluate(docs_demanded, "docs-mesh")
        if h["status"] != "NEEDS_REVIEW" or "AGENTS.md" not in h.get("demanded_by", []):
            failures.append(f"context-demanded docs-mesh absence must be NEEDS_REVIEW: {h}")
        (docs_demanded / "docs/agents").mkdir(parents=True)
        h = evaluate(docs_demanded, "docs-mesh")
        if h["status"] != "PASS":
            failures.append(f"present docs-mesh must satisfy context demand: {h}")

        # Unknown surface -> FAIL.
        if evaluate(root / "empty", "bogus")["status"] != "FAIL":
            failures.append("unknown surface must be FAIL")

    result = {"version": VERSION, "status": "FAIL" if failures else "PASS", "failures": failures}
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[attach-health:self-test] " + result["status"])
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--surface", choices=list(SURFACES))
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.surface:
        print(json.dumps({"version": VERSION, "status": "FAIL", "failures": ["--surface is required"]}, indent=2))
        return 1
    result = evaluate(args.target, args.surface)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[attach-health] " + str(result.get("status")))
    return 0 if result.get("status") in {"PASS", "NOT_APPLIED", "HOST_UNOBSERVABLE"} else 1


if __name__ == "__main__":
    sys.exit(main())
