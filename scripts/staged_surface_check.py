#!/usr/bin/env python3
"""Fast syntax validation for staged JSON, YAML, and JavaScript surfaces."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def check_json(path: Path) -> str | None:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return f"invalid JSON {path}: {type(exc).__name__}: {exc}"
    return None


def check_yaml(path: Path) -> str | None:
    try:
        import yaml  # type: ignore[import-untyped]
    except Exception as exc:
        return f"PyYAML required to validate {path}: {exc}"
    try:
        yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return f"invalid YAML {path}: {type(exc).__name__}: {exc}"
    return None


def check_javascript(path: Path) -> str | None:
    result = subprocess.run(
        ["node", "--check", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        return f"invalid JavaScript {path}: {detail or 'node --check failed'}"
    return None


def validate_path(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return check_json(path)
    if suffix in {".yml", ".yaml"}:
        return check_yaml(path)
    if suffix in {".js", ".mjs", ".cjs"}:
        return check_javascript(path)
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    failures: list[str] = []
    checked = 0
    for raw in args.files:
        path = Path(raw)
        if not path.is_file():
            continue
        failure = validate_path(path)
        checked += 1
        if failure:
            failures.append(failure)

    if failures:
        print("[staged-surface-check] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("[staged-surface-check] PASS")
    print(f"checked_files={checked}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
