#!/usr/bin/env python3
"""Validate post-retention metadata policy for generated evidence manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
EVIDENCE_ROOT = ROOT / "docs/evidence"
REPORTS = EVIDENCE_ROOT / "reports"
LEGACY_CONTEXT_MESH_REPORTS = REPORTS / "context-mesh"
POLICY_DOC = EVIDENCE_ROOT / "INDEX.md"
LEGACY_POLICY_REPORT = LEGACY_CONTEXT_MESH_REPORTS / "retention-metadata-strategy-2026-05-06/REPORT.md"
FINAL_REPORT = LEGACY_CONTEXT_MESH_REPORTS / "context-mesh-v1-final-certification-2026-05-05/REPORT.md"
POLICY_TERMS = (
    "docs/evidence/current/",
    "docs/evidence/reports/YYYY/MM/DD/<domain>/<run-id>/",
    "docs/evidence/archive/",
    "source_of_truth: false",
    "retained",
    "superseded",
    "archived",
    "expired",
)


def load_manifest(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def is_temporal_manifest(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root / "docs/evidence/reports").parts
    except ValueError:
        return False
    if len(parts) < 6 or parts[-1] != "manifest.json":
        return False
    year, month, day = parts[:3]
    return (
        len(year) == 4
        and len(month) == 2
        and len(day) == 2
        and year.isdigit()
        and month.isdigit()
        and day.isdigit()
    )


def check(root: Path = ROOT) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    pending: list[str] = []
    temporal: list[str] = []
    legacy: list[str] = []

    evidence_root = root / "docs/evidence"
    reports = evidence_root / "reports"
    policy_doc = evidence_root / "INDEX.md"
    legacy_policy_report = reports / "context-mesh/retention-metadata-strategy-2026-05-06/REPORT.md"
    final_report = reports / "context-mesh/context-mesh-v1-final-certification-2026-05-05/REPORT.md"

    if not policy_doc.exists():
        failures.append(f"missing retention policy document: {relative(policy_doc, root)}")
    else:
        policy_text = policy_doc.read_text(encoding="utf-8")
        for term in POLICY_TERMS:
            if term not in policy_text:
                failures.append(f"retention policy document missing term: {term}")

    if not legacy_policy_report.exists():
        failures.append(f"missing legacy retention policy report: {relative(legacy_policy_report, root)}")
    if not final_report.exists():
        failures.append(f"missing final certification report: {relative(final_report, root)}")
    elif "`retention_head=pending`" not in final_report.read_text(encoding="utf-8"):
        failures.append("final certification report must explain historical retention_head=pending")

    for manifest in sorted(reports.rglob("manifest.json")):
        rel = relative(manifest, root)
        if is_temporal_manifest(manifest, root):
            temporal.append(rel)
        elif "/reports/context-mesh/" in f"/{rel}":
            legacy.append(rel)
        try:
            data = load_manifest(manifest)
        except json.JSONDecodeError as exc:
            failures.append(f"invalid manifest JSON: {rel}: {exc}")
            continue
        if data.get("retention_head") != "pending":
            continue
        pending.append(rel)
        for key in ("run_id", "run_head", "gate_head"):
            if not data.get(key):
                failures.append(f"{rel} pending retention missing {key}")

    result = {
        "version": VERSION,
        "pending_manifest_count": len(pending),
        "pending_manifests": pending,
        "temporal_manifest_count": len(temporal),
        "legacy_context_mesh_manifest_count": len(legacy),
        "policy_document": relative(policy_doc, root),
        "legacy_policy_report": relative(legacy_policy_report, root),
        "final_report": relative(final_report, root),
    }
    return result, failures


def self_test() -> tuple[dict[str, object], list[str]]:
    with tempfile.TemporaryDirectory(prefix="tes-retention-metadata-") as tmp:
        root = Path(tmp)
        evidence = root / "docs/evidence"
        temporal_run = evidence / "reports/2026/05/21/context-mesh/temporal-smoke"
        legacy_run = evidence / "reports/context-mesh/legacy-smoke"
        legacy_policy = evidence / "reports/context-mesh/retention-metadata-strategy-2026-05-06"
        final = evidence / "reports/context-mesh/context-mesh-v1-final-certification-2026-05-05"
        for path in (temporal_run, legacy_run, legacy_policy, final):
            path.mkdir(parents=True, exist_ok=True)

        policy_text = "\n".join(POLICY_TERMS)
        (evidence / "INDEX.md").write_text(policy_text, encoding="utf-8")
        (legacy_policy / "REPORT.md").write_text("legacy policy report\n", encoding="utf-8")
        (final / "REPORT.md").write_text("historical note: `retention_head=pending`\n", encoding="utf-8")
        manifest = {"run_id": "smoke", "retention_head": "pending", "run_head": "abc", "gate_head": "def"}
        for path in (temporal_run / "manifest.json", legacy_run / "manifest.json"):
            path.write_text(json.dumps(manifest), encoding="utf-8")

        result, failures = check(root)
        if result.get("temporal_manifest_count") != 1:
            failures.append("self-test expected one temporal manifest")
        if result.get("legacy_context_mesh_manifest_count") != 1:
            failures.append("self-test expected one legacy manifest")
        return result, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result, failures = self_test() if args.self_test else check()
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
