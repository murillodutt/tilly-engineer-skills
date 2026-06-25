#!/usr/bin/env python3
"""Conditional Cortex reflection gate for pre-commit."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/agents/cortex/CONTRACT.md"
RUNTIME = ROOT / ".tes/bin/cortex.py"
PACKAGE = ROOT / "scripts/cortex.py"


def run(command: list[str]) -> int:
    print(f"[pre-commit-cortex] {' '.join(command)}")
    return subprocess.run(command, cwd=ROOT, check=False).returncode


def main() -> int:
    if not CONTRACT.is_file():
        print("[pre-commit-cortex] SKIP (no Cortex contract)")
        return 0

    if RUNTIME.is_file():
        cortex = RUNTIME
    elif PACKAGE.is_file():
        cortex = PACKAGE
    else:
        print("[pre-commit-cortex] SKIP (no Cortex runtime)")
        return 0

    failures = 0
    for args in (
        [str(cortex), "reflect", "--target", ".", "pre-commit Cortex reflection"],
        [str(cortex), "curate-plan", "--target", ".", "--backend", "lexical"],
    ):
        if run(["python3", *args]) != 0:
            failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
