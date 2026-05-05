#!/usr/bin/env python3
"""Plan a context-mesh ablation matrix from the portable dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "benchmarks/context-mesh/eval-dataset.json"


def load_dataset(path: Path = DATASET) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_dataset(data: dict[str, object]) -> list[str]:
    failures: list[str] = []

    sections = data.get("sections", [])
    evals = data.get("evals", [])
    if not sections:
        failures.append("dataset has no sections")
    if not evals:
        failures.append("dataset has no evals")

    for section in sections:
        if not any(ev.get("target_section") == section for ev in evals if ev.get("kind") == "trigger"):
            failures.append(f"section has no trigger eval: {section}")

    if not any(ev.get("kind") == "distractor" for ev in evals):
        failures.append("dataset has no distractors")

    for ev in evals:
        for key in ("id", "kind", "prompt", "expected", "forbidden"):
            if key not in ev:
                failures.append(f"eval missing {key}: {ev.get('id', '(unknown)')}")
        if not ev.get("expected") and not ev.get("expected_any"):
            failures.append(f"eval has no expected assertions: {ev.get('id', '(unknown)')}")
        for index, group in enumerate(ev.get("expected_any", [])):
            if not isinstance(group, list) or not group:
                failures.append(f"expected_any group is empty or invalid: {ev.get('id', '(unknown)')}[{index}]")

    return failures


def build_conditions(sections: list[str]) -> list[str]:
    return ["full", "none", *[f"drop:{section}" for section in sections]]


def trigger_evals(data: dict[str, object]) -> list[dict[str, object]]:
    return [ev for ev in data.get("evals", []) if ev.get("kind") == "trigger"]


def distractor_evals(data: dict[str, object]) -> list[dict[str, object]]:
    return [ev for ev in data.get("evals", []) if ev.get("kind") == "distractor"]


def build_plan(data: dict[str, object], dataset_path: Path = DATASET) -> dict[str, object]:
    sections = data.get("sections", [])
    if not isinstance(sections, list):
        sections = []
    conditions = build_conditions(sections)
    triggers = trigger_evals(data)
    distractors = distractor_evals(data)

    try:
        dataset = str(dataset_path.relative_to(ROOT))
    except ValueError:
        dataset = str(dataset_path)

    return {
        "dataset": dataset,
        "sections": sections,
        "conditions": conditions,
        "trigger_evals": len(triggers),
        "distractors": len(distractors),
        "planned_calls": len(conditions) * len(triggers) + len(distractors),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DATASET)
    args = parser.parse_args()

    data = load_dataset(args.dataset)
    failures = validate_dataset(data)

    if failures:
        print("[context-mesh-plan] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("[context-mesh-plan] PASS")
    print(json.dumps(build_plan(data, args.dataset), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
