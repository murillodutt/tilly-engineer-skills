#!/usr/bin/env python3
"""Compare two Cortex memory benchmark evaluation artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import cortex_memory_benchmark as benchmark  # noqa: E402


VERSION = "0.3.192"


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def record_map(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    records = payload.get("records", [])
    if not isinstance(records, list):
        return {}
    return {
        str(record.get("fixture_id")): record
        for record in records
        if isinstance(record, dict) and record.get("fixture_id")
    }


def status_for(record: dict[str, object], cutoff: str) -> str:
    cutoffs = record.get("cutoffs", {})
    if not isinstance(cutoffs, dict):
        return "MISSING"
    judgment = cutoffs.get(cutoff, {})
    if not isinstance(judgment, dict):
        return "MISSING"
    return str(judgment.get("status", "MISSING"))


def compare_evaluations(baseline: dict[str, object], candidate: dict[str, object]) -> dict[str, object]:
    baseline_summary = baseline.get("summary", {}) if isinstance(baseline.get("summary"), dict) else {}
    candidate_summary = candidate.get("summary", {}) if isinstance(candidate.get("summary"), dict) else {}
    primary_cutoff = str(candidate_summary.get("primary_cutoff") or baseline_summary.get("primary_cutoff") or "top_5")
    baseline_records = record_map(baseline)
    candidate_records = record_map(candidate)
    fixture_ids = sorted(set(baseline_records) | set(candidate_records))

    flips = []
    improvements = 0
    regressions = 0
    for fixture_id in fixture_ids:
        before = status_for(baseline_records.get(fixture_id, {}), primary_cutoff)
        after = status_for(candidate_records.get(fixture_id, {}), primary_cutoff)
        if before == after:
            continue
        direction = "changed"
        if before == "FAIL" and after == "PASS":
            direction = "improvement"
            improvements += 1
        elif before == "PASS" and after == "FAIL":
            direction = "regression"
            regressions += 1
        flips.append({
            "fixture_id": fixture_id,
            "from": before,
            "to": after,
            "direction": direction,
        })

    baseline_rate = float(baseline_summary.get("pass_rate", 0.0) or 0.0)
    candidate_rate = float(candidate_summary.get("pass_rate", 0.0) or 0.0)
    return {
        "schema_version": benchmark.SCHEMA_VERSION,
        "mode": "compare",
        "metadata": {
            "created_at": benchmark.utc_now(),
            "primary_cutoff": primary_cutoff,
            "baseline_dataset_sha": baseline.get("metadata", {}).get("dataset_sha") if isinstance(baseline.get("metadata"), dict) else None,
            "candidate_dataset_sha": candidate.get("metadata", {}).get("dataset_sha") if isinstance(candidate.get("metadata"), dict) else None,
        },
        "summary": {
            "baseline_pass_rate": baseline_rate,
            "candidate_pass_rate": candidate_rate,
            "delta_pass_rate": round(candidate_rate - baseline_rate, 4),
            "improvements": improvements,
            "regressions": regressions,
            "status": "FAIL" if regressions else "PASS",
        },
        "flips": flips,
    }


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="tes-cortex-memory-compare-") as temp:
        target = Path(temp)
        data = benchmark.load_dataset()
        benchmark.materialize_fixture_target(target, data)
        predictions = benchmark.predict_only(target, force_rg=True)
        candidate = benchmark.evaluate_predictions(predictions)
        baseline = json.loads(json.dumps(candidate))
        baseline["records"][0]["cutoffs"][baseline["summary"]["primary_cutoff"]]["status"] = "FAIL"
        baseline["summary"] = benchmark.summarize(baseline["records"], baseline["metadata"]["cutoffs"])
        comparison = compare_evaluations(baseline, candidate)
        if comparison["summary"]["improvements"] != 1 or comparison["summary"]["regressions"] != 0:
            print("[cortex-memory-compare] FAIL")
            print(json.dumps(comparison, indent=2, sort_keys=True))
            return 1
    print("[cortex-memory-compare] PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not args.baseline or not args.candidate:
        parser.error("--baseline and --candidate are required unless --self-test is used")

    baseline = load_json(args.baseline)
    candidate = load_json(args.candidate)
    if not isinstance(baseline, dict) or not isinstance(candidate, dict):
        print("[cortex-memory-compare] FAIL")
        print("- baseline and candidate must be JSON objects")
        return 1
    comparison = compare_evaluations(baseline, candidate)
    if args.out:
        benchmark.write_json(args.out, comparison)
        print(str(args.out))
    else:
        print(json.dumps(comparison, indent=2, sort_keys=True))
    return 0 if comparison["summary"]["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
