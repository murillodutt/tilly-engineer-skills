#!/usr/bin/env python3
"""Non-blocking Field Reports drain for pre-push."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


# TES_FIELD_REPORTS_PRE_PUSH
ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = (
    ROOT / "scripts/field_reports.py",
    ROOT / ".tes/bin/field_reports.py",
)


def main() -> int:
    for script in CANDIDATES:
        if not script.is_file():
            continue
        subprocess.run(
            [
                "python3",
                str(script),
                "drain",
                "--target",
                ".",
                "--trigger",
                "pre-push",
            ],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        break
    return 0


if __name__ == "__main__":
    sys.exit(main())
