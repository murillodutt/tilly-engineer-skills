#!/usr/bin/env python3
"""Short recursive validation loop for the TES Git gate contract."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from typing import Any


CHECKS: tuple[tuple[str, list[str]], ...] = (
    ("git-gate-contract", ["python3", "scripts/git_gate_contract.py", "--self-test", "--json-only"]),
    ("canary-admission", ["python3", "scripts/canary_admission_oracle.py", "--self-test", "--json-only"]),
    ("installed-certification", ["python3", "scripts/installed_certification_oracle.py", "--self-test", "--json-only"]),
    ("field-reports", ["python3", "scripts/field_reports.py", "--self-test", "--json-only"]),
    ("hook-manager-awareness", ["python3", "scripts/hook_manager_awareness_oracle.py", "--self-test"]),
    ("tes-install", ["python3", "scripts/tes_install.py", "--self-test"]),
)

HEAVY_CHECKS: tuple[tuple[str, list[str]], ...] = (
    ("commit-check", ["npm", "run", "--silent", "commit:check"]),
)


def run_check(name: str, command: list[str]) -> dict[str, Any]:
    started = time.monotonic()
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    duration = round(time.monotonic() - started, 3)
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    return {
        "name": name,
        "command": command,
        "returncode": result.returncode,
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "duration_seconds": duration,
        "stdout_tail": stdout[-4000:],
        "stderr_tail": stderr[-4000:],
    }


def run_loop(iterations: int, *, include_heavy: bool) -> dict[str, Any]:
    checks = [*CHECKS, *(HEAVY_CHECKS if include_heavy else ())]
    rows: list[dict[str, Any]] = []
    started = time.monotonic()
    for iteration in range(1, iterations + 1):
        for name, command in checks:
            row = run_check(name, command)
            row["iteration"] = iteration
            rows.append(row)
            if row["status"] != "PASS":
                return {
                    "schema": "tes-git-gate-convergence-loop@1",
                    "status": "FAIL",
                    "iterations_requested": iterations,
                    "iterations_completed": iteration - 1,
                    "failed_check": name,
                    "duration_seconds": round(time.monotonic() - started, 3),
                    "checks": rows,
                }
    return {
        "schema": "tes-git-gate-convergence-loop@1",
        "status": "PASS",
        "iterations_requested": iterations,
        "iterations_completed": iterations,
        "duration_seconds": round(time.monotonic() - started, 3),
        "checks": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the short Git gate convergence loop.")
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--include-heavy", action="store_true", help="Also run staged commit gate checks.")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args(argv)
    if args.iterations < 1:
        parser.error("--iterations must be >= 1")
    result = run_loop(args.iterations, include_heavy=args.include_heavy)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json_only:
        print("[git-gate-convergence] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
