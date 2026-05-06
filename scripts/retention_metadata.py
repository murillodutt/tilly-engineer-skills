#!/usr/bin/env python3
"""Validate post-retention metadata policy for generated evidence manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
REPORTS = ROOT / "docs/evidence/reports/context-mesh"
POLICY_REPORT = REPORTS / "retention-metadata-strategy-2026-05-06/REPORT.md"
FINAL_REPORT = REPORTS / "context-mesh-v1-final-certification-2026-05-05/REPORT.md"


def load_manifest(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def check() -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    pending: list[str] = []

    if not POLICY_REPORT.exists():
        failures.append(f"missing retention policy report: {POLICY_REPORT.relative_to(ROOT)}")
    if not FINAL_REPORT.exists():
        failures.append(f"missing final certification report: {FINAL_REPORT.relative_to(ROOT)}")
    elif "`retention_head=pending`" not in FINAL_REPORT.read_text(encoding="utf-8"):
        failures.append("final certification report must explain historical retention_head=pending")

    for manifest in sorted(REPORTS.rglob("manifest.json")):
        try:
            data = load_manifest(manifest)
        except json.JSONDecodeError as exc:
            failures.append(f"invalid manifest JSON: {manifest.relative_to(ROOT)}: {exc}")
            continue
        if data.get("retention_head") != "pending":
            continue
        pending.append(manifest.relative_to(ROOT).as_posix())
        for key in ("run_id", "run_head", "gate_head"):
            if not data.get(key):
                failures.append(f"{manifest.relative_to(ROOT)} pending retention missing {key}")

    result = {
        "version": VERSION,
        "pending_manifest_count": len(pending),
        "pending_manifests": pending,
        "policy_report": POLICY_REPORT.relative_to(ROOT).as_posix(),
        "final_report": FINAL_REPORT.relative_to(ROOT).as_posix(),
    }
    return result, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result, failures = check()
    result["status"] = "FAIL" if failures else "PASS"
    result["failures"] = failures
    print(json.dumps(result, indent=2))
    if failures:
        print("[retention-metadata] FAIL")
        return 1
    print("[retention-metadata] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
