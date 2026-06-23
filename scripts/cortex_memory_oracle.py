#!/usr/bin/env python3
"""Validate Cortex memory benchmark datasets and retained result artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import cortex_memory_benchmark as benchmark  # noqa: E402


VERSION = "0.3.185"


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_predictions(payload: dict[str, object]) -> list[str]:
    failures: list[str] = []
    if payload.get("schema_version") != benchmark.SCHEMA_VERSION:
        failures.append("result schema_version mismatch")
    if payload.get("mode") != "predict-only":
        failures.append("prediction artifact mode must be predict-only")
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        failures.append("prediction metadata missing")
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        failures.append("prediction records missing")
        return failures
    for record in records:
        if not isinstance(record, dict):
            failures.append("prediction record must be an object")
            continue
        fixture_id = record.get("fixture_id", "(unknown)")
        if "matches" not in record:
            failures.append(f"{fixture_id}: missing preserved matches")
        if record.get("status") not in benchmark.VALID_STATUSES:
            failures.append(f"{fixture_id}: invalid status {record.get('status')!r}")
        for match in record.get("matches", []):
            if not isinstance(match, dict):
                failures.append(f"{fixture_id}: match must be an object")
                continue
            for key in ("rank", "path", "excerpt", "score_debug"):
                if key not in match:
                    failures.append(f"{fixture_id}: match missing {key}")
    return failures


def validate_evaluation(payload: dict[str, object]) -> list[str]:
    failures: list[str] = []
    if payload.get("schema_version") != benchmark.SCHEMA_VERSION:
        failures.append("evaluation schema_version mismatch")
    if payload.get("mode") != "evaluate-only":
        failures.append("evaluation artifact mode must be evaluate-only")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        failures.append("evaluation summary missing")
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        failures.append("evaluation records missing")
        return failures
    for record in records:
        if not isinstance(record, dict):
            failures.append("evaluation record must be an object")
            continue
        fixture_id = record.get("fixture_id", "(unknown)")
        recall = record.get("recall")
        if not isinstance(recall, dict) or "matches" not in recall:
            failures.append(f"{fixture_id}: recall evidence missing")
        cutoffs = record.get("cutoffs")
        if not isinstance(cutoffs, dict) or not cutoffs:
            failures.append(f"{fixture_id}: cutoff judgments missing")
            continue
        for label, judgment in cutoffs.items():
            if not isinstance(judgment, dict):
                failures.append(f"{fixture_id}: {label} judgment must be an object")
                continue
            if judgment.get("status") not in {"PASS", "FAIL"}:
                failures.append(f"{fixture_id}: {label} invalid status")
            if "retrieved_refs" not in judgment:
                failures.append(f"{fixture_id}: {label} missing retrieved_refs")
    return failures


def validate_result(path: Path) -> list[str]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        return ["artifact root must be an object"]
    mode = payload.get("mode")
    if mode == "predict-only":
        return validate_predictions(payload)
    if mode == "evaluate-only":
        return validate_evaluation(payload)
    return [f"unsupported artifact mode: {mode!r}"]


def command_validate_dataset(args: argparse.Namespace) -> int:
    data = benchmark.load_dataset(args.dataset)
    failures = benchmark.validate_dataset(data)
    if failures:
        print("[cortex-memory-oracle] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("[cortex-memory-oracle] PASS")
    print(json.dumps(benchmark.dataset_summary(data, args.dataset), indent=2, sort_keys=True))
    return 0


def command_validate_result(args: argparse.Namespace) -> int:
    failures = validate_result(args.result)
    if failures:
        print("[cortex-memory-result] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("[cortex-memory-result] PASS")
    return 0


def command_evaluate(args: argparse.Namespace) -> int:
    predictions = load_json(args.predictions)
    if not isinstance(predictions, dict):
        print("[cortex-memory-evaluate] FAIL")
        print("- predictions root must be an object")
        return 1
    payload = benchmark.evaluate_predictions(predictions, args.dataset)
    benchmark.write_json(args.out, payload)
    print(str(args.out))
    return 0 if payload.get("summary", {}).get("status") == "PASS" else 1


def self_test() -> int:
    if benchmark.self_test() != 0:
        return 1
    with tempfile.TemporaryDirectory(prefix="tes-cortex-memory-oracle-") as temp:
        target = Path(temp)
        data = benchmark.load_dataset()
        benchmark.materialize_fixture_target(target, data)
        predictions = benchmark.predict_only(target, force_rg=True)
        evaluation = benchmark.evaluate_predictions(predictions)
        prediction_path = target / "prediction.json"
        evaluation_path = target / "evaluation.json"
        benchmark.write_json(prediction_path, predictions)
        benchmark.write_json(evaluation_path, evaluation)
        failures = validate_result(prediction_path) + validate_result(evaluation_path)
        if failures:
            print("[cortex-memory-oracle] FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
    print("[cortex-memory-oracle] PASS")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    dataset = subparsers.add_parser("validate-dataset")
    dataset.add_argument("--dataset", type=Path, default=benchmark.DATASET)
    dataset.set_defaults(func=command_validate_dataset)

    result = subparsers.add_parser("validate-result")
    result.add_argument("result", type=Path)
    result.set_defaults(func=command_validate_result)

    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--predictions", type=Path, required=True)
    evaluate.add_argument("--dataset", type=Path, default=benchmark.DATASET)
    evaluate.add_argument("--out", type=Path, required=True)
    evaluate.set_defaults(func=command_evaluate)

    schema = subparsers.add_parser("inspect-schema")
    schema.set_defaults(func=lambda _args: print(benchmark.RESULT_SCHEMA.read_text(encoding="utf-8")) or 0)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
