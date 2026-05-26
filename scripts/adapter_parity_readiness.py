#!/usr/bin/env python3
"""Check structural and contract parity readiness across adapters."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/mesh/CONTRACT-MANIFEST.yml"
LIFECYCLE_MATRIX = ROOT / "docs/adapters/ADAPTER-CAPABILITY-MATRIX.md"
MATERIALIZER = ROOT / "scripts/materialize_adapter.py"
DATASET = ROOT / "benchmarks/context-mesh/eval-dataset.json"

ADAPTER_SOURCE_PATHS = {
    "claude": (
        "src/adapters/claude/CLAUDE.md",
        "src/adapters/claude/skills/tes-guidelines/SKILL.md",
    ),
    "codex": (
        "src/adapters/codex/AGENTS.md",
        "src/adapters/codex/skills/tes-engineering-discipline/SKILL.md",
    ),
    "cursor": (
        "src/adapters/cursor/CURSOR.md",
        "src/adapters/cursor/rules/tes-guidelines.mdc",
    ),
}

ADAPTER_MATERIALIZED_PATHS = {
    "claude": (
        "CLAUDE.md",
        ".claude/skills/tes-guidelines/SKILL.md",
    ),
    "codex": (
        "AGENTS.md",
        ".agents/skills/tes-engineering-discipline/SKILL.md",
    ),
    "cursor": (
        "CURSOR.md",
        ".cursor/rules/tes-guidelines.mdc",
    ),
}

CORE_CONTRACT = "Assumptions visible. Scope smaller. Edits surgical. Success falsifiable."
SUCCESS_FORMULA = "E = A * S * C * V"
LIFECYCLE_MOMENTS = (
    "recall",
    "scope normalization",
    "write gate",
    "checkpoint",
    "closeout",
    "subagent return",
)
SUBAGENT_BOUNDARY_TERMS = (
    "TES Memory Lifecycle Boundary",
    "Parent owns durable memory",
    "durable Cortex writes",
    "evidence return only",
)
LIFECYCLE_STATUSES = (
    "certified",
    "blocked",
    "deferred",
    "not available",
    "git-governed",
)
INTERNAL_MATRIX_LABELS = (
    "condition: full",
    "condition: none",
    "condition: drop:",
    "matrix condition",
    "drop:Mantra Gate",
    "drop:Think Before Coding",
    "drop:Simplicity First",
    "drop:Surgical Changes",
    "drop:Goal-Driven Execution",
)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def contract_gate_names() -> list[str]:
    text = CONTRACT.read_text(encoding="utf-8")
    in_gates = False
    names: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line == "gates:":
            in_gates = True
            continue
        if in_gates and raw_line and not raw_line.startswith(" ") and line.endswith(":"):
            break
        if in_gates and line.startswith("name:"):
            names.append(line.split(":", 1)[1].strip())
    return names


def read_joined(paths: tuple[str, ...], root: Path = ROOT) -> str:
    parts = []
    for relpath in paths:
        path = root / relpath
        if not path.exists():
            raise FileNotFoundError(relpath)
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def check_adapter_text(
    adapter: str,
    text: str,
    gates: list[str],
    *,
    materialized: bool,
) -> dict[str, Any]:
    missing_gates = [gate for gate in gates if gate not in text]
    missing_terms = [
        term for term in (CORE_CONTRACT, SUCCESS_FORMULA)
        if term not in text
    ]
    missing_lifecycle_moments = [
        term for term in LIFECYCLE_MOMENTS
        if term not in text
    ]
    missing_subagent_boundary_terms = [
        term for term in SUBAGENT_BOUNDARY_TERMS
        if term not in text
    ]
    status = "GO"
    if missing_gates or missing_terms or missing_lifecycle_moments or missing_subagent_boundary_terms:
        status = "NO-GO"
    return {
        "adapter": adapter,
        "materialized": materialized,
        "gate_count": len(gates),
        "missing_gates": missing_gates,
        "missing_terms": missing_terms,
        "missing_lifecycle_moments": missing_lifecycle_moments,
        "missing_subagent_boundary_terms": missing_subagent_boundary_terms,
        "status": status,
    }


def check_lifecycle_matrix() -> dict[str, Any]:
    failures: list[str] = []
    if not LIFECYCLE_MATRIX.exists():
        failures.append(f"missing lifecycle matrix: {rel(LIFECYCLE_MATRIX)}")
        return {"status": "NO-GO", "failures": failures}

    text = LIFECYCLE_MATRIX.read_text(encoding="utf-8")
    for term in ("Memory Lifecycle Matrix", *LIFECYCLE_MOMENTS, *LIFECYCLE_STATUSES):
        if term not in text:
            failures.append(f"{rel(LIFECYCLE_MATRIX)} missing {term!r}")

    return {
        "status": "GO" if not failures else "NO-GO",
        "matrix": rel(LIFECYCLE_MATRIX),
        "lifecycle_moments": list(LIFECYCLE_MOMENTS),
        "statuses": list(LIFECYCLE_STATUSES),
        "failures": failures,
    }


def materialize_to_temp() -> tuple[tempfile.TemporaryDirectory[str], Path, dict[str, Any], list[str]]:
    tempdir = tempfile.TemporaryDirectory(prefix="tes-adapter-parity-")
    out_root = Path(tempdir.name) / "adapters"

    result = subprocess.run(
        [sys.executable, str(MATERIALIZER), "all", "--out", str(out_root)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    failures: list[str] = []
    if result.returncode != 0:
        failures.extend(result.stdout.splitlines())
        failures.extend(result.stderr.splitlines())
        return tempdir, out_root, {}, failures

    try:
        output = json.loads(result.stdout.split("[materialize] PASS", 1)[0])
    except Exception as exc:  # pragma: no cover - defensive CLI parsing guard.
        failures.append(f"could not parse materializer output: {exc}")
        output = {}
    return tempdir, out_root, output, failures


def benchmark_prompt_label_check(gates: list[str]) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from context_mesh_plan import load_dataset, validate_dataset  # type: ignore
    from context_mesh_run import build_samples  # type: ignore

    data = load_dataset(DATASET)
    failures = validate_dataset(data)
    if failures:
        return {"status": "NO-GO", "failures": failures}

    samples = build_samples(data)
    prompt_failures: list[str] = []
    for sample in samples:
        prompt = str(sample["prompt"])
        lowered = prompt.lower()
        for label in INTERNAL_MATRIX_LABELS:
            if label.lower() in lowered:
                prompt_failures.append(f"{sample['sample_id']} leaks {label!r}")
        condition = str(sample["condition"])
        if condition.startswith("drop:") and condition in prompt:
            prompt_failures.append(f"{sample['sample_id']} leaks condition {condition!r}")

    dataset_sections = list(data.get("sections", []))
    if dataset_sections != gates:
        prompt_failures.append(
            f"dataset sections {dataset_sections!r} differ from contract gates {gates!r}"
        )

    return {
        "status": "GO" if not prompt_failures else "NO-GO",
        "samples_checked": len(samples),
        "dataset": rel(DATASET),
        "failures": prompt_failures,
    }


def analyze() -> dict[str, Any]:
    gates = contract_gate_names()
    failures: list[str] = []

    if gates != [
        "Mantra Gate",
        "Think Before Coding",
        "Simplicity First",
        "Surgical Changes",
        "Goal-Driven Execution",
    ]:
        failures.append(f"unexpected contract gates: {gates!r}")

    lifecycle_matrix = check_lifecycle_matrix()
    if lifecycle_matrix["status"] != "GO":
        failures.append("memory lifecycle matrix failed")
        failures.extend(lifecycle_matrix.get("failures", []))

    source_results = []
    for adapter, paths in sorted(ADAPTER_SOURCE_PATHS.items()):
        try:
            text = read_joined(paths)
            result = check_adapter_text(adapter, text, gates, materialized=False)
        except FileNotFoundError as exc:
            result = {
                "adapter": adapter,
                "materialized": False,
                "status": "NO-GO",
                "missing_path": str(exc),
            }
        source_results.append(result)
        if result["status"] != "GO":
            failures.append(f"{adapter} source contract parity failed")

    tempdir, out_root, materializer_output, materializer_failures = materialize_to_temp()
    failures.extend(materializer_failures)

    materialized_results = []
    for adapter, paths in sorted(ADAPTER_MATERIALIZED_PATHS.items()):
        adapter_root = out_root / adapter
        try:
            text = read_joined(paths, adapter_root)
            result = check_adapter_text(adapter, text, gates, materialized=True)
        except FileNotFoundError as exc:
            result = {
                "adapter": adapter,
                "materialized": True,
                "status": "NO-GO",
                "missing_path": str(exc),
            }
        materialized_results.append(result)
        if result["status"] != "GO":
            failures.append(f"{adapter} materialized contract parity failed")

    benchmark = benchmark_prompt_label_check(gates)
    if benchmark["status"] != "GO":
        failures.append("benchmark condition label check failed")

    final_result = {
        "status": "GO" if not failures else "NO-GO",
        "git_head": git_head(),
        "contract_manifest": rel(CONTRACT),
        "contract_gates": gates,
        "memory_lifecycle_matrix": lifecycle_matrix,
        "source_results": source_results,
        "materializer": materializer_output,
        "materialized_results": materialized_results,
        "benchmark_condition_labels": benchmark,
        "claim": (
            "structural/contract and memory-lifecycle boundary readiness only; "
            "no behavior parity claim"
        ),
        "failures": failures,
    }
    tempdir.cleanup()
    return final_result


def render_text(result: dict[str, Any]) -> str:
    lines = [
        f"[adapter-parity-readiness] {result['status']}",
        f"git_head={result['git_head']}",
        f"contract_manifest={result['contract_manifest']}",
        f"claim={result['claim']}",
        "",
        "contract_gates:",
    ]
    for gate in result["contract_gates"]:
        lines.append(f"- {gate}")

    lifecycle_matrix = result["memory_lifecycle_matrix"]
    lines.append("")
    lines.append(f"memory_lifecycle_matrix: {lifecycle_matrix['status']}")

    lines.append("")
    lines.append("source_results:")
    for item in result["source_results"]:
        lines.append(f"- {item['adapter']}: {item['status']}")

    lines.append("")
    lines.append("materialized_results:")
    for item in result["materialized_results"]:
        lines.append(f"- {item['adapter']}: {item['status']}")

    benchmark = result["benchmark_condition_labels"]
    lines.append("")
    lines.append(
        "benchmark_condition_labels: "
        f"{benchmark['status']} samples_checked={benchmark.get('samples_checked')}"
    )
    lines.append("")
    lines.append("memory_lifecycle_boundary:")
    lines.append(f"- lifecycle_moments={len(LIFECYCLE_MOMENTS)}")
    lines.append(f"- subagent_boundary_terms={len(SUBAGENT_BOUNDARY_TERMS)}")

    if result["failures"]:
        lines.append("")
        lines.append("failures:")
        for failure in result["failures"]:
            lines.append(f"- {failure}")
    return "\n".join(lines)


def self_test() -> int:
    gates = contract_gate_names()
    real_text = read_joined(ADAPTER_SOURCE_PATHS["codex"])
    boundary_removed = real_text.replace("subagent return", "subagent handoff", 1)
    boundary_result = check_adapter_text(
        "codex",
        boundary_removed,
        gates,
        materialized=False,
    )

    matrix_text = LIFECYCLE_MATRIX.read_text(encoding="utf-8")
    matrix_backup = LIFECYCLE_MATRIX.read_text(encoding="utf-8")
    failures: list[str] = []
    try:
        if boundary_result["status"] != "NO-GO":
            failures.append("boundary removal fixture did not fail")
        if "subagent return" not in boundary_result["missing_lifecycle_moments"]:
            failures.append("boundary removal did not report missing subagent return")

        synthetic = matrix_text.replace("not available", "not-applicable", 1)
        missing_status = [
            term
            for term in LIFECYCLE_STATUSES
            if term not in synthetic
        ]
        if "not available" not in missing_status:
            failures.append("matrix status fixture did not detect missing not available")
    finally:
        # Keep the test read-only even if future edits change the helper.
        _ = matrix_backup

    if failures:
        print(json.dumps({"status": "FAIL", "failures": failures}, indent=2))
        return 1
    print("adapter_parity_readiness self-test PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    result = analyze()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_text(result))
    return 0 if result["status"] == "GO" else 1


if __name__ == "__main__":
    sys.exit(main())
