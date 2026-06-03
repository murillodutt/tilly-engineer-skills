#!/usr/bin/env python3
"""Run deterministic Cortex memory benchmark recall and sufficiency checks."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "benchmarks/cortex-memory/eval-dataset.json"
RESULT_SCHEMA = ROOT / "benchmarks/cortex-memory/result-schema.json"
SCHEMA_VERSION = "tes-cortex-memory-benchmark@0.1"
FIXTURE_SCHEMA_VERSION = "tes-cortex-memory-fixtures@0.1"
VERSION = "0.3.159"
VALID_STATUSES = {"PASS", "FAIL", "BLOCKED", "DEGRADED", "NEEDS_REVIEW", "NOT_AVAILABLE"}

sys.path.insert(0, str(ROOT / "scripts"))
import cortex  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def rel(path: Path, root: Path = ROOT) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_dataset(path: Path = DATASET) -> dict[str, Any]:
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError("dataset root must be an object")
    return data


def validate_dataset(data: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if data.get("schema_version") != FIXTURE_SCHEMA_VERSION:
        failures.append("dataset schema_version mismatch")
    cutoffs = data.get("cutoffs")
    if not isinstance(cutoffs, list) or not cutoffs or not all(isinstance(item, int) and item > 0 for item in cutoffs):
        failures.append("dataset cutoffs must be positive integers")
    elif cutoffs != sorted(set(cutoffs)):
        failures.append("dataset cutoffs must be sorted and unique")

    capabilities = data.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        failures.append("dataset has no capabilities")

    documents = data.get("fixture_documents")
    if not isinstance(documents, list) or not documents:
        failures.append("dataset has no fixture_documents")
    else:
        seen_paths: set[str] = set()
        for index, document in enumerate(documents):
            if not isinstance(document, dict):
                failures.append(f"fixture_documents[{index}] must be an object")
                continue
            path = document.get("path")
            content = document.get("content")
            if not isinstance(path, str) or not path:
                failures.append(f"fixture_documents[{index}] missing path")
            elif path.startswith("/") or ".." in Path(path).parts:
                failures.append(f"fixture document has unsafe path: {path}")
            elif path in seen_paths:
                failures.append(f"duplicate fixture document path: {path}")
            else:
                seen_paths.add(path)
            if not isinstance(content, str) or not content.strip():
                failures.append(f"fixture document missing content: {path}")

    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        failures.append("dataset has no fixtures")
        return failures

    ids: set[str] = set()
    for index, fixture in enumerate(fixtures):
        if not isinstance(fixture, dict):
            failures.append(f"fixtures[{index}] must be an object")
            continue
        fixture_id = fixture.get("id")
        if not isinstance(fixture_id, str) or not fixture_id:
            failures.append(f"fixture missing id at index {index}")
        elif fixture_id in ids:
            failures.append(f"duplicate fixture id: {fixture_id}")
        else:
            ids.add(fixture_id)
        if fixture.get("capability") not in capabilities:
            failures.append(f"{fixture_id}: capability not declared")
        if not isinstance(fixture.get("question"), str) or not fixture["question"].strip():
            failures.append(f"{fixture_id}: missing question")
        if not isinstance(fixture.get("query"), str) or not fixture["query"].strip():
            failures.append(f"{fixture_id}: missing query")
        sufficiency = fixture.get("expected_sufficiency", "sufficient")
        if sufficiency not in {"sufficient", "insufficient"}:
            failures.append(f"{fixture_id}: invalid expected_sufficiency")
        required_refs = fixture.get("required_refs", [])
        if not isinstance(required_refs, list):
            failures.append(f"{fixture_id}: required_refs must be a list")
        if sufficiency == "sufficient" and not required_refs:
            failures.append(f"{fixture_id}: sufficient fixtures need required_refs")
        for key in ("forbidden_refs", "required_terms", "forbidden_terms", "expected_order"):
            if key in fixture and not isinstance(fixture[key], list):
                failures.append(f"{fixture_id}: {key} must be a list")
        nuggets = fixture.get("rubric_nuggets", [])
        if not isinstance(nuggets, list):
            failures.append(f"{fixture_id}: rubric_nuggets must be a list")
    return failures


def dataset_summary(data: dict[str, Any], dataset_path: Path) -> dict[str, Any]:
    return {
        "dataset": rel(dataset_path),
        "dataset_sha": sha256_path(dataset_path),
        "version": data.get("version"),
        "schema_version": data.get("schema_version"),
        "capabilities": data.get("capabilities", []),
        "cutoffs": data.get("cutoffs", []),
        "fixtures": len(data.get("fixtures", [])),
        "fixture_documents": len(data.get("fixture_documents", [])),
    }


def normalize_match(raw: dict[str, Any], rank: int, backend: str) -> dict[str, Any]:
    score = 1.0 / rank
    return {
        "rank": rank,
        "path": raw.get("path", ""),
        "line": raw.get("line"),
        "layer": raw.get("layer"),
        "title": raw.get("title"),
        "excerpt": raw.get("excerpt", ""),
        "score": score,
        "score_debug": {
            "backend": backend,
            "rank_score": score,
        },
    }


def recall_fixture(target: Path, fixture: dict[str, Any], limit: int, force_rg: bool) -> dict[str, Any]:
    started = time.perf_counter()
    result = cortex.recall(target, str(fixture["query"]), limit, force_rg=force_rg)
    latency_ms = round((time.perf_counter() - started) * 1000, 3)
    backend = str(result.get("backend", "unknown"))
    matches = [
        normalize_match(match, index + 1, backend)
        for index, match in enumerate(result.get("matches", []))
        if isinstance(match, dict)
    ]
    status = result.get("status", "FAIL")
    if status == "PASS" and result.get("sqlite_error"):
        status = "DEGRADED"
    return {
        "fixture_id": fixture["id"],
        "capability": fixture["capability"],
        "question": fixture["question"],
        "query": fixture["query"],
        "status": status if status in VALID_STATUSES else "FAIL",
        "backend": backend,
        "latency_ms": latency_ms,
        "matches": matches,
        "total_results": len(matches),
        "failures": result.get("failures", []),
        "sqlite_error": result.get("sqlite_error"),
        "forced_fallback": bool(result.get("forced_fallback")),
    }


def load_checkpoint(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {"schema_version": SCHEMA_VERSION, "items": {}}
    data = load_json(path)
    if not isinstance(data, dict):
        return {"schema_version": SCHEMA_VERSION, "items": {}}
    items = data.get("items")
    if not isinstance(items, dict):
        data["items"] = {}
    return data


def save_checkpoint(path: Path | None, checkpoint: dict[str, Any]) -> None:
    if path is None:
        return
    checkpoint["updated_at"] = utc_now()
    write_json(path, checkpoint)


def predict_only(
    target: Path,
    dataset_path: Path = DATASET,
    cutoffs: list[int] | None = None,
    force_rg: bool = False,
    checkpoint_path: Path | None = None,
    resume: bool = False,
) -> dict[str, Any]:
    data = load_dataset(dataset_path)
    failures = validate_dataset(data)
    if failures:
        return {
            "schema_version": SCHEMA_VERSION,
            "mode": "predict-only",
            "status": "FAIL",
            "failures": failures,
        }

    selected_cutoffs = cutoffs or list(data["cutoffs"])
    limit = max(selected_cutoffs)
    checkpoint = load_checkpoint(checkpoint_path) if resume or checkpoint_path else {"schema_version": SCHEMA_VERSION, "items": {}}
    items = checkpoint.setdefault("items", {})

    records: list[dict[str, Any]] = []
    for fixture in data["fixtures"]:
        fixture_id = fixture["id"]
        if resume and fixture_id in items:
            records.append(items[fixture_id])
            continue
        record = recall_fixture(target, fixture, limit, force_rg)
        items[fixture_id] = record
        records.append(record)
        save_checkpoint(checkpoint_path, checkpoint)

    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "predict-only",
        "metadata": {
            "created_at": utc_now(),
            "dataset": rel(dataset_path),
            "dataset_sha": sha256_path(dataset_path),
            "git_head": git_head(),
            "target": str(target.resolve()),
            "backend": "rg" if force_rg else "auto",
            "cutoffs": selected_cutoffs,
            "checkpoint": str(checkpoint_path) if checkpoint_path else None,
        },
        "records": records,
    }


def match_paths(prediction: dict[str, Any], cutoff: int) -> list[str]:
    return [
        str(match.get("path", ""))
        for match in prediction.get("matches", [])
        if isinstance(match, dict) and int(match.get("rank", 0) or 0) <= cutoff
    ]


def joined_excerpt(prediction: dict[str, Any], cutoff: int) -> str:
    excerpts = [
        str(match.get("excerpt", ""))
        for match in prediction.get("matches", [])
        if isinstance(match, dict) and int(match.get("rank", 0) or 0) <= cutoff
    ]
    return "\n".join(excerpts)


def present_refs(paths: list[str], refs: list[str]) -> list[str]:
    path_set = set(paths)
    return [ref for ref in refs if ref in path_set]


def missing_refs(paths: list[str], refs: list[str]) -> list[str]:
    path_set = set(paths)
    return [ref for ref in refs if ref not in path_set]


def present_terms(text: str, terms: list[str]) -> list[str]:
    lowered = text.lower()
    return [term for term in terms if term.lower() in lowered]


def missing_terms(text: str, terms: list[str]) -> list[str]:
    lowered = text.lower()
    return [term for term in terms if term.lower() not in lowered]


def order_score(paths: list[str], expected_order: list[str]) -> float | None:
    if not expected_order:
        return None
    # Event-order fixtures judge reconstructability from retained refs. The
    # recall backend may return matches in backend-specific rank order, so the
    # deterministic event oracle uses lexical ref order for numbered fixtures.
    ordered_paths = [path for path in sorted(paths) if path in set(expected_order)]
    ranks = {path: index for index, path in enumerate(ordered_paths)}
    if any(ref not in ranks for ref in expected_order):
        return 0.0
    total = 0
    concordant = 0
    for left_index, left in enumerate(expected_order):
        for right in expected_order[left_index + 1 :]:
            total += 1
            if ranks[left] < ranks[right]:
                concordant += 1
    return round(concordant / total, 3) if total else 1.0


def score_nugget(nugget: dict[str, Any], paths: list[str], text: str) -> dict[str, Any]:
    required_refs = nugget.get("required_refs", [])
    forbidden_refs = nugget.get("forbidden_refs", [])
    required_terms = nugget.get("required_terms", [])
    forbidden_terms = nugget.get("forbidden_terms", [])
    missing_required_refs = missing_refs(paths, required_refs)
    present_forbidden_refs = present_refs(paths, forbidden_refs)
    missing_required_terms = missing_terms(text, required_terms)
    present_forbidden_terms = present_terms(text, forbidden_terms)
    failures = missing_required_refs + present_forbidden_refs + missing_required_terms + present_forbidden_terms
    score = 1.0 if not failures else 0.0
    if failures and (present_refs(paths, required_refs) or present_terms(text, required_terms)):
        score = 0.5
    return {
        "id": nugget.get("id", "unnamed"),
        "description": nugget.get("description", ""),
        "score": score,
        "missing_required_refs": missing_required_refs,
        "present_forbidden_refs": present_forbidden_refs,
        "missing_required_terms": missing_required_terms,
        "present_forbidden_terms": present_forbidden_terms,
    }


def judge_fixture(fixture: dict[str, Any], prediction: dict[str, Any], cutoff: int) -> dict[str, Any]:
    paths = match_paths(prediction, cutoff)
    text = joined_excerpt(prediction, cutoff)
    expected_sufficiency = fixture.get("expected_sufficiency", "sufficient")
    required_refs = fixture.get("required_refs", [])
    forbidden_refs = fixture.get("forbidden_refs", [])
    required_terms = fixture.get("required_terms", [])
    forbidden_terms = fixture.get("forbidden_terms", [])

    missing_required_refs = missing_refs(paths, required_refs)
    present_forbidden_refs = present_refs(paths, forbidden_refs)
    missing_required_terms = missing_terms(text, required_terms)
    present_forbidden_terms = present_terms(text, forbidden_terms)
    order = order_score(paths, fixture.get("expected_order", []))
    nugget_scores = [
        score_nugget(nugget, paths, text)
        for nugget in fixture.get("rubric_nuggets", [])
        if isinstance(nugget, dict)
    ]

    failures = []
    if prediction.get("status") not in {"PASS", "DEGRADED"}:
        failures.extend(prediction.get("failures", []) or ["recall did not pass"])
    if expected_sufficiency == "insufficient":
        if paths:
            failures.append("expected insufficient evidence but recall returned matches")
    else:
        if missing_required_refs:
            failures.append(f"missing required refs: {', '.join(missing_required_refs)}")
        if present_forbidden_refs:
            failures.append(f"present forbidden refs: {', '.join(present_forbidden_refs)}")
        if missing_required_terms:
            failures.append(f"missing required terms: {', '.join(missing_required_terms)}")
        if present_forbidden_terms:
            failures.append(f"present forbidden terms: {', '.join(present_forbidden_terms)}")
        if order is not None and order < 1.0:
            failures.append(f"event order score below 1.0: {order}")

    if expected_sufficiency == "insufficient":
        sufficiency = "insufficient"
    elif failures:
        sufficiency = "insufficient"
    else:
        sufficiency = "sufficient"

    return {
        "cutoff": cutoff,
        "label": f"top_{cutoff}",
        "status": "PASS" if not failures else "FAIL",
        "sufficiency": sufficiency,
        "retrieved_refs": paths,
        "missing_required_refs": missing_required_refs,
        "present_forbidden_refs": present_forbidden_refs,
        "missing_required_terms": missing_required_terms,
        "present_forbidden_terms": present_forbidden_terms,
        "order_score": order,
        "nuggets": nugget_scores,
        "failures": failures,
    }


def summarize(records: list[dict[str, Any]], cutoffs: list[int]) -> dict[str, Any]:
    by_cutoff: dict[str, dict[str, Any]] = {}
    for cutoff in cutoffs:
        label = f"top_{cutoff}"
        total = len(records)
        passed = sum(1 for record in records if record["cutoffs"][label]["status"] == "PASS")
        by_cutoff[label] = {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(passed / total, 4) if total else 0.0,
        }

    by_capability: dict[str, dict[str, Any]] = {}
    primary = f"top_{max(cutoffs)}"
    for record in records:
        bucket = by_capability.setdefault(record["capability"], {"total": 0, "passed": 0, "failed": 0})
        bucket["total"] += 1
        if record["cutoffs"][primary]["status"] == "PASS":
            bucket["passed"] += 1
        else:
            bucket["failed"] += 1
    for bucket in by_capability.values():
        bucket["pass_rate"] = round(bucket["passed"] / bucket["total"], 4) if bucket["total"] else 0.0

    return {
        "primary_cutoff": primary,
        "total": len(records),
        "passed": by_cutoff[primary]["passed"],
        "failed": by_cutoff[primary]["failed"],
        "pass_rate": by_cutoff[primary]["pass_rate"],
        "status": "PASS" if by_cutoff[primary]["failed"] == 0 else "FAIL",
        "by_cutoff": by_cutoff,
        "by_capability": by_capability,
    }


def evaluate_predictions(predictions: dict[str, Any], dataset_path: Path = DATASET) -> dict[str, Any]:
    data = load_dataset(dataset_path)
    failures = validate_dataset(data)
    if failures:
        return {
            "schema_version": SCHEMA_VERSION,
            "mode": "evaluate-only",
            "status": "FAIL",
            "failures": failures,
        }
    cutoffs = list(predictions.get("metadata", {}).get("cutoffs") or data["cutoffs"])
    prediction_by_id = {record.get("fixture_id"): record for record in predictions.get("records", [])}
    records: list[dict[str, Any]] = []
    for fixture in data["fixtures"]:
        prediction = prediction_by_id.get(fixture["id"])
        if not prediction:
            prediction = {
                "fixture_id": fixture["id"],
                "status": "FAIL",
                "matches": [],
                "failures": ["missing prediction record"],
            }
        cutoff_results = {
            f"top_{cutoff}": judge_fixture(fixture, prediction, cutoff)
            for cutoff in cutoffs
        }
        records.append(
            {
                "fixture_id": fixture["id"],
                "capability": fixture["capability"],
                "question": fixture["question"],
                "recall": prediction,
                "cutoffs": cutoff_results,
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "evaluate-only",
        "metadata": {
            "created_at": utc_now(),
            "dataset": rel(dataset_path),
            "dataset_sha": sha256_path(dataset_path),
            "git_head": git_head(),
            "source_predictions_sha": sha256_bytes(json.dumps(predictions, sort_keys=True).encode("utf-8")),
            "cutoffs": cutoffs,
        },
        "records": records,
        "summary": summarize(records, cutoffs),
    }


def safe_fixture_path(root: Path, raw_path: str) -> Path:
    if raw_path.startswith("/") or ".." in Path(raw_path).parts:
        raise ValueError(f"unsafe fixture path: {raw_path}")
    return root / "docs/agents/cortex" / raw_path


def materialize_fixture_target(target: Path, data: dict[str, Any]) -> None:
    cortex_root = target / "docs/agents/cortex"
    if cortex_root.exists():
        shutil.rmtree(cortex_root)
    init_result = cortex.init(target)
    init_status = init_result.get("status") or init_result.get("verify", {}).get("status")
    if init_status != "PASS":
        raise RuntimeError(f"fixture target init failed: {init_result}")
    core_files = {"CONTRACT.md", "MAP.md", "TRAIL.md", "LINKS.md"}
    for document in data.get("fixture_documents", []):
        if str(document["path"]) in core_files:
            continue
        path = safe_fixture_path(target, str(document["path"]))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(document["content"]), encoding="utf-8")
    rebuild = cortex.rebuild(target)
    if rebuild.get("status") != "PASS":
        raise RuntimeError(f"fixture target rebuild failed: {rebuild}")


def markdown_snapshot(target: Path) -> dict[str, str]:
    root = target / "docs/agents/cortex"
    return {
        path.relative_to(target).as_posix(): sha256_path(path)
        for path in root.rglob("*.md")
        if path.is_file()
    }


def self_test() -> int:
    data = load_dataset(DATASET)
    failures = validate_dataset(data)
    if failures:
        print("[cortex-memory-benchmark] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    with tempfile.TemporaryDirectory(prefix="tes-cortex-memory-") as temp:
        target = Path(temp)
        materialize_fixture_target(target, data)
        before = markdown_snapshot(target)
        checkpoint = target / ".tes/runs/cortex-memory/checkpoint.json"
        predictions = predict_only(target, DATASET, force_rg=True, checkpoint_path=checkpoint)
        resumed = predict_only(target, DATASET, force_rg=True, checkpoint_path=checkpoint, resume=True)
        evaluation = evaluate_predictions(predictions, DATASET)
        after = markdown_snapshot(target)
        test_failures = []
        if before != after:
            test_failures.append("predict/evaluate changed Cortex Markdown")
        if not checkpoint.exists():
            test_failures.append("checkpoint was not written")
        if len(resumed.get("records", [])) != len(predictions.get("records", [])):
            test_failures.append("resume did not preserve prediction count")
        if evaluation.get("summary", {}).get("status") != "PASS":
            test_failures.append(f"evaluation did not pass: {evaluation.get('summary')}")
        if any(not record.get("matches") and record["fixture_id"] != "CM005-abstention" for record in predictions.get("records", [])):
            test_failures.append("non-abstention fixture has no preserved matches")
        if test_failures:
            print("[cortex-memory-benchmark] FAIL")
            for failure in test_failures:
                print(f"- {failure}")
            return 1

    print("[cortex-memory-benchmark] PASS")
    print(json.dumps(dataset_summary(data, DATASET), indent=2, sort_keys=True))
    return 0


def command_plan(args: argparse.Namespace) -> int:
    data = load_dataset(args.dataset)
    failures = validate_dataset(data)
    if failures:
        print("[cortex-memory-plan] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("[cortex-memory-plan] PASS")
    print(json.dumps(dataset_summary(data, args.dataset), indent=2, sort_keys=True))
    return 0


def emit_or_write(payload: dict[str, Any], out: Path | None) -> None:
    if out:
        write_json(out, payload)
        print(str(out))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))


def command_predict(args: argparse.Namespace) -> int:
    payload = predict_only(
        args.target,
        args.dataset,
        cutoffs=args.cutoff,
        force_rg=args.force_rg,
        checkpoint_path=args.checkpoint,
        resume=args.resume,
    )
    emit_or_write(payload, args.out)
    return 0 if payload.get("status") != "FAIL" else 1


def command_evaluate(args: argparse.Namespace) -> int:
    predictions = load_json(args.predictions)
    payload = evaluate_predictions(predictions, args.dataset)
    emit_or_write(payload, args.out)
    return 0 if payload.get("summary", {}).get("status") == "PASS" else 1


def command_run(args: argparse.Namespace) -> int:
    out_dir = args.out_dir or ROOT / ".tes/runs/cortex-memory" / utc_now().replace(":", "").replace("-", "")
    out_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = args.checkpoint or out_dir / "checkpoint.json"
    predictions = predict_only(
        args.target,
        args.dataset,
        cutoffs=args.cutoff,
        force_rg=args.force_rg,
        checkpoint_path=checkpoint,
        resume=args.resume,
    )
    evaluation = evaluate_predictions(predictions, args.dataset)
    write_json(out_dir / "recall.json", predictions)
    write_json(out_dir / "evaluation.json", evaluation)
    print(json.dumps({
        "status": evaluation.get("summary", {}).get("status"),
        "out_dir": str(out_dir),
        "recall": str(out_dir / "recall.json"),
        "evaluation": str(out_dir / "evaluation.json"),
    }, indent=2, sort_keys=True))
    return 0 if evaluation.get("summary", {}).get("status") == "PASS" else 1


def command_schema(args: argparse.Namespace) -> int:
    print(RESULT_SCHEMA.read_text(encoding="utf-8"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    plan = subparsers.add_parser("plan")
    plan.add_argument("--dataset", type=Path, default=DATASET)
    plan.set_defaults(func=command_plan)

    predict = subparsers.add_parser("predict-only")
    predict.add_argument("--target", type=Path, default=Path.cwd())
    predict.add_argument("--dataset", type=Path, default=DATASET)
    predict.add_argument("--out", type=Path)
    predict.add_argument("--cutoff", type=int, action="append")
    predict.add_argument("--force-rg", action="store_true")
    predict.add_argument("--checkpoint", type=Path)
    predict.add_argument("--resume", action="store_true")
    predict.set_defaults(func=command_predict)

    evaluate = subparsers.add_parser("evaluate-only")
    evaluate.add_argument("--predictions", type=Path, required=True)
    evaluate.add_argument("--dataset", type=Path, default=DATASET)
    evaluate.add_argument("--out", type=Path)
    evaluate.set_defaults(func=command_evaluate)

    run = subparsers.add_parser("run")
    run.add_argument("--target", type=Path, default=Path.cwd())
    run.add_argument("--dataset", type=Path, default=DATASET)
    run.add_argument("--out-dir", type=Path)
    run.add_argument("--cutoff", type=int, action="append")
    run.add_argument("--force-rg", action="store_true")
    run.add_argument("--checkpoint", type=Path)
    run.add_argument("--resume", action="store_true")
    run.set_defaults(func=command_run)

    schema = subparsers.add_parser("inspect-schema")
    schema.set_defaults(func=command_schema)
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
