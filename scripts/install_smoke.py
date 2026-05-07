#!/usr/bin/env python3
"""Run deterministic assisted-install smoke probes in temporary projects."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import field_reports


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.16"
ROUTES = ("current", "codex", "claude", "cursor", "all", "mcp", "audit")


def run(command: list[str], cwd: Path = ROOT) -> tuple[int, str, str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def require_paths(target: Path, relpaths: tuple[str, ...]) -> list[str]:
    failures: list[str] = []
    for relpath in relpaths:
        if not (target / relpath).exists():
            failures.append(f"missing path: {relpath}")
    return failures


def init_git(target: Path) -> list[str]:
    code, stdout, stderr = run(["git", "init"], cwd=target)
    if code == 0:
        return []
    return ["git init failed", *stdout.splitlines(), *stderr.splitlines()]


def init_cortex(target: Path) -> list[str]:
    code, stdout, stderr = run(
        [sys.executable, str(ROOT / "scripts/cortex.py"), "init", "--target", str(target)]
    )
    if code == 0:
        return []
    return ["cortex init failed", *stdout.splitlines(), *stderr.splitlines()]


def install_adapter(target: Path, adapter: str, dry_run: bool = False) -> list[str]:
    command = [
        sys.executable,
        str(ROOT / "scripts/install_adapter.py"),
        "--target",
        str(target),
        "--adapter",
        adapter,
        "--yes",
    ]
    if dry_run:
        command.append("--dry-run")
    code, stdout, stderr = run(command)
    if code == 0:
        return []
    return [f"adapter install failed: {adapter}", *stdout.splitlines(), *stderr.splitlines()]


def install_mcp(target: Path, adapter: str, dry_run: bool = False) -> list[str]:
    command = [
        sys.executable,
        str(ROOT / "scripts/install_mcp.py"),
        "--target",
        str(target),
        "--adapter",
        adapter,
        "--yes",
    ]
    if dry_run:
        command.append("--dry-run")
    code, stdout, stderr = run(command)
    if code == 0:
        return []
    return [f"mcp install failed: {adapter}", *stdout.splitlines(), *stderr.splitlines()]


def cortex_gate(target: Path) -> list[str]:
    failures: list[str] = []
    for command in ("verify", "audit", "rebuild", "curate-plan"):
        extra_args = ["--backend", "lexical"] if command == "curate-plan" else []
        code, stdout, stderr = run(
            [sys.executable, str(ROOT / "scripts/cortex.py"), command, "--target", str(target), *extra_args]
        )
        if code != 0:
            failures.extend([f"cortex {command} failed", *stdout.splitlines(), *stderr.splitlines()])
    return failures


def mcp_gate(target: Path) -> list[str]:
    code, stdout, stderr = run(
        [sys.executable, str(target / ".tilly/bin/cortex_mcp.py"), "--self-test"],
        cwd=target,
    )
    if code == 0:
        return []
    return ["installed cortex_mcp.py --self-test failed", *stdout.splitlines(), *stderr.splitlines()]


def install_field_reports(target: Path) -> list[str]:
    code, stdout, stderr = run(
        [sys.executable, str(ROOT / "scripts/field_reports.py"), "install-hook", "--target", str(target)]
    )
    failures: list[str] = []
    if code != 0:
        failures.extend(["field reports hook install failed", *stdout.splitlines(), *stderr.splitlines()])
    failures.extend(require_paths(target, (
        ".tilly/bin/field_reports.py",
        ".tilly/field-reports/outbox.jsonl",
        ".git/hooks/pre-push",
    )))
    if (target / ".tilly/field-reports/DISABLED").exists():
        failures.append("field reports must be active by default")
    return failures


def expected_adapter_paths(adapter: str) -> tuple[str, ...]:
    if adapter == "codex":
        return ("AGENTS.md", ".agents/skills/tilly-engineering-discipline/SKILL.md")
    if adapter == "claude":
        return ("CLAUDE.md", ".claude-plugin/plugin.json", "skills/tilly-guidelines/SKILL.md")
    if adapter == "cursor":
        return ("CURSOR.md", ".cursor/rules/tilly-guidelines.mdc")
    raise ValueError(f"unknown adapter: {adapter}")


def expected_mcp_paths(adapter: str) -> tuple[str, ...]:
    base = (
        ".tilly/bin/cortex.py",
        ".tilly/bin/cortex_mcp.py",
        ".tilly/bin/cortex_embed.mjs",
        ".tilly/bin/field_reports.py",
    )
    if adapter == "codex":
        return (*base, ".codex/config.toml")
    if adapter == "claude":
        return (*base, ".mcp.json")
    if adapter == "cursor":
        return (*base, ".cursor/mcp.json")
    if adapter == "all":
        return (*base, ".codex/config.toml", ".mcp.json", ".cursor/mcp.json")
    raise ValueError(f"unknown MCP adapter: {adapter}")


def route_adapters(route: str) -> list[str]:
    if route == "current":
        return ["codex"]
    if route == "all":
        return ["codex", "claude", "cursor"]
    if route in {"codex", "claude", "cursor"}:
        return [route]
    return []


def probe_route(route: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"tilly-install-smoke-{route}-") as tempdir:
        target = Path(tempdir)
        failures: list[str] = []
        failures.extend(init_git(target))

        def finish() -> dict[str, Any]:
            status = "FAIL" if failures else "PASS"
            field_reports.safe_record_event(
                target,
                "install_smoke",
                status,
                "installer",
                "self-test",
                details={"route": route, "failures": len(failures)},
            )
            return {"route": route, "status": status, "failures": failures}

        if route == "audit":
            failures.extend(install_adapter(target, "all", dry_run=True))
            failures.extend(install_mcp(target, "all", dry_run=True))
            for unexpected in ("AGENTS.md", "CLAUDE.md", ".tilly/bin/cortex_mcp.py"):
                if (target / unexpected).exists():
                    failures.append(f"audit route wrote unexpected path: {unexpected}")
            return finish()

        failures.extend(init_cortex(target))
        failures.extend(install_field_reports(target))

        if route == "mcp":
            failures.extend(install_mcp(target, "all"))
            failures.extend(require_paths(target, expected_mcp_paths("all")))
            failures.extend(mcp_gate(target))
            failures.extend(cortex_gate(target))
            return finish()

        adapters = route_adapters(route)
        adapter_arg = "all" if route == "all" else adapters[0]
        failures.extend(install_adapter(target, adapter_arg))
        failures.extend(install_mcp(target, adapter_arg))
        failures.extend(cortex_gate(target))
        failures.extend(mcp_gate(target))
        for adapter in adapters:
            failures.extend(require_paths(target, expected_adapter_paths(adapter)))
            failures.extend(require_paths(target, expected_mcp_paths(adapter)))

        return finish()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=ROUTES, default="all")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    routes = ROUTES if args.self_test else (args.route,)
    results = [probe_route(route) for route in routes]
    failures = [
        failure
        for result in results
        for failure in result["failures"]
    ]
    print(json.dumps({"version": VERSION, "status": "FAIL" if failures else "PASS", "routes": results}, indent=2))
    if failures:
        print("[install-smoke] FAIL")
        return 1
    print("[install-smoke] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
