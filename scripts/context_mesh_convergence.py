#!/usr/bin/env python3
"""Analyze context-mesh evidence and decide the next convergence step."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_ROOT = ROOT / "docs/evidence/reports"

GATE_FIX_HINTS = {
    "Think Before Coding": "add adversarial prompts where acting before naming ambiguity is clearly wrong",
    "Simplicity First": "tighten current-scope signals and forbid future-type scaffolding",
    "Surgical Changes": "require explicit deferral of unrelated cleanup and request-traceable scope",
    "Goal-Driven Execution": "require a named reproducer, oracle, or test before any patch claim",
}


def latest_summary(root: Path) -> Path:
    summaries = sorted(
        root.rglob("summary.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not summaries:
        raise FileNotFoundError(f"no summary.json files found under {root}")
    return summaries[0]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(summary: dict[str, Any], min_loss: int) -> dict[str, Any]:
    metrics = summary.get("metrics", {})
    certification = summary.get("certification", {})
    losses = summary.get("ablation_losses", {})
    failures: list[str] = []
    fixes: list[dict[str, Any]] = []

    def require(condition: bool, failure: str, fix: str) -> None:
        if not condition:
            failures.append(failure)
            fixes.append({"area": "certification", "reason": failure, "fix": fix})

    require(certification.get("status") == "GO", "certification is not GO", "inspect NO-GO reasons before changing dataset or context")
    require(metrics.get("plan_run_parity") == 1.0, "plan/run parity is not 100%", "fix runner matrix parity before behavior work")
    require(metrics.get("raw_evidence_coverage") == 1.0, "raw evidence coverage is incomplete", "fix evidence writer before behavior work")
    require(metrics.get("backend_error_count") == 0, "backend errors occurred", "classify backend/auth/timeout before grading fixes")
    require(metrics.get("distractor_leak_rate") == 0.0, "distractor leak is non-zero", "tighten context or distractor leak rules before GO")
    require(
        metrics.get("trigger_pass_rate_full", 0) > metrics.get("trigger_pass_rate_none", 0),
        "full does not outperform none",
        "calibrate context, dataset, or grader until full lift is positive",
    )

    gate_results = []
    for gate, value in sorted(losses.items()):
        loss = int(value.get("loss", 0))
        converged = loss >= min_loss
        gate_results.append({
            "gate": gate,
            "loss": loss,
            "full_passes": value.get("full_passes"),
            "drop_passes": value.get("drop_passes"),
            "converged": converged,
            "fix": None if converged else GATE_FIX_HINTS.get(gate, "add adversarial follow-up"),
        })
        if not converged:
            failures.append(f"{gate} loss {loss} is below {min_loss}")
            fixes.append({
                "area": gate,
                "reason": f"loss={loss}",
                "fix": GATE_FIX_HINTS.get(gate, "add adversarial follow-up"),
            })

    status = "CONVERGED" if not failures else "NEEDS_FIX"
    return {
        "status": status,
        "run_id": summary.get("run_id"),
        "certification_status": certification.get("status"),
        "min_loss": min_loss,
        "metrics": {
            "trigger_pass_rate_full": metrics.get("trigger_pass_rate_full"),
            "trigger_pass_rate_none": metrics.get("trigger_pass_rate_none"),
            "behavioral_lift": metrics.get("behavioral_lift"),
            "distractor_fail_rate": metrics.get("distractor_fail_rate"),
            "distractor_leak_rate": metrics.get("distractor_leak_rate"),
            "backend_error_count": metrics.get("backend_error_count"),
        },
        "gate_results": gate_results,
        "failures": failures,
        "fixes": fixes,
        "test_loop": [
            "run fixture pipeline evidence for the new git head and grader hash",
            "run behavior backend only after fixture GO is retained",
            "rerun this convergence gate on the retained behavior summary",
        ],
    }


def render_text(result: dict[str, Any], summary_path: Path) -> str:
    lines = [
        f"[context-mesh-convergence] {result['status']}",
        f"summary={summary_path}",
        f"run_id={result.get('run_id')}",
        f"certification_status={result.get('certification_status')}",
        f"min_loss={result.get('min_loss')}",
        "",
        "metrics:",
    ]
    for key, value in result["metrics"].items():
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("gate_results:")
    for gate in result["gate_results"]:
        marker = "ok" if gate["converged"] else "fix"
        lines.append(
            f"- {marker}: {gate['gate']} loss={gate['loss']} "
            f"full={gate['full_passes']} drop={gate['drop_passes']}"
        )
        if gate["fix"]:
            lines.append(f"  fix: {gate['fix']}")

    if result["fixes"]:
        lines.append("")
        lines.append("next_fix:")
        for fix in result["fixes"]:
            lines.append(f"- {fix['area']}: {fix['fix']}")

    lines.append("")
    lines.append("test_loop:")
    for step in result["test_loop"]:
        lines.append(f"- {step}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    parser.add_argument("--min-loss", type=int, default=1)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--advisory", action="store_true", help="always exit zero after printing analysis")
    args = parser.parse_args()

    try:
        summary_path = args.summary or latest_summary(args.report_root)
        summary = load_json(summary_path)
        result = analyze(summary, args.min_loss)
    except Exception as exc:
        print(f"[context-mesh-convergence] FAIL\n- {exc}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_text(result, summary_path))

    if args.advisory:
        return 0
    return 0 if result["status"] == "CONVERGED" else 1


if __name__ == "__main__":
    sys.exit(main())
