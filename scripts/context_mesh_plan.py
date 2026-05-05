#!/usr/bin/env python3
"""Plan a context-mesh ablation matrix from the portable dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "benchmarks/context-mesh/eval-dataset.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DATASET)
    args = parser.parse_args()

    data = json.loads(args.dataset.read_text(encoding="utf-8"))
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

    conditions = ["full", "none", *[f"drop:{section}" for section in sections]]
    trigger_count = sum(1 for ev in evals if ev.get("kind") == "trigger")
    distractor_count = sum(1 for ev in evals if ev.get("kind") == "distractor")
    planned_calls = len(conditions) * trigger_count + distractor_count

    if failures:
        print("[context-mesh-plan] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("[context-mesh-plan] PASS")
    print(json.dumps({
        "dataset": str(args.dataset.relative_to(ROOT)),
        "sections": sections,
        "conditions": conditions,
        "trigger_evals": trigger_count,
        "distractors": distractor_count,
        "planned_calls": planned_calls
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
