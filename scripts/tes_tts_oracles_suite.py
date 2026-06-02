#!/usr/bin/env python3
"""Run the full tes-tts oracle suite as one maintainer gate.

Discovers every `scripts/tes_tts_*_oracle.py`, runs each with `--self-test`
(falling back to no-arg for the roadmap-partition oracle, which does not take
that flag), and fails if any oracle fails. This is the gate that closes audit
finding W-1: the runtime oracle suite must run in `commit:check` so a future
drift or regression cannot ship silently. Camada de trabalho only — not bundled.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

# The roadmap-partition oracle validates docs structure and takes no --self-test.
NO_SELF_TEST = {"tes_tts_roadmap_partition_oracle.py"}


def discover() -> list[Path]:
    return sorted(SCRIPTS.glob("tes_tts_*_oracle.py"))


def run_one(path: Path) -> tuple[str, bool]:
    args = [sys.executable, str(path)]
    if path.name not in NO_SELF_TEST:
        args.append("--self-test")
    proc = subprocess.run(args, capture_output=True, text=True)
    return path.name, proc.returncode == 0


def main() -> int:
    oracles = discover()
    results = [run_one(p) for p in oracles]
    failed = [name for name, ok in results if not ok]
    status = "PASS" if not failed else "FAIL"
    print(json.dumps({
        "status": status,
        "oracle_count": len(results),
        "passed": len(results) - len(failed),
        "failed": failed,
    }, indent=2))
    print("[tes-tts-oracles-suite] " + status)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
