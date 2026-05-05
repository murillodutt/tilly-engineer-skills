#!/usr/bin/env python3
"""Run the context-mesh benchmark matrix and write audit evidence."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import shutil
from typing import Any

from context_mesh_plan import (
    DATASET,
    ROOT,
    build_plan,
    distractor_evals,
    load_dataset,
    trigger_evals,
    validate_dataset,
)


RUNNER_VERSION = "0.1.0"
CERTIFICATION_PROFILE = "v1-rc"
PIPELINE_CERTIFICATION_CLASS = "pipeline-v1-rc"
BEHAVIOR_CERTIFICATION_CLASS = "behavior-v1-rc"
GRADER_VERSION = "deterministic-substring@0.1.2"
DEFAULT_OUT_ROOT = ROOT / "docs/evidence/reports/context-mesh"
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----", re.DOTALL),
)
SECTION_RULES = {
    "Think Before Coding": "Name facts, assumptions, ambiguity, tradeoffs, and blockers before acting.",
    "Simplicity First": "Implement only the current requirement; say the smallest/current implementation and reject future-type scaffolding until a real case exists.",
    "Surgical Changes": "For bugfix-plus-cleanup requests, explicitly split the requested fix from unrelated cleanup; fix only the crash path and defer cleanup unless necessary.",
    "Goal-Driven Execution": "Before acting, explicitly name the smallest reproducer or oracle; do not patch or claim closure before that check is named.",
}
GRADER_CONTRACT = {
    "version": GRADER_VERSION,
    "normalization": "case-insensitive substring match",
    "pass_rule": "all expected strings present and no forbidden strings present",
    "expected": "each dataset expected string must appear in output",
    "expected_any": "each expected_any group must have at least one string present in output",
    "forbidden": "each dataset forbidden string must be absent from output",
    "distractor_fail": "a distractor output failed expected/forbidden literal checks",
    "distractor_leak": "a distractor output shows heavy context leakage signals",
}
DISTRACTOR_LEAK_SIGNALS = {
    "mentions_contract_gate": (
        "think before coding",
        "simplicity first",
        "surgical changes",
        "goal-driven execution",
    ),
    "mentions_context_mesh": (
        "context mesh",
        "context-mesh",
    ),
    "mentions_benchmark_eval": (
        "benchmark",
        "eval",
        "grader",
        "certification",
    ),
    "mentions_governance_ceremony": (
        "governance ceremony",
        "multi-step governance",
        "tds",
        "no-go",
        "manifest.json",
        "raw.ndjson",
        "summary.json",
        "graders-sha.json",
    ),
    "pulls_unrelated_agent_rules": (
        "agent rules",
        "engineering discipline",
        "assumptions visible",
        "scope smaller",
        "success falsifiable",
    ),
}
TRIVIAL_TASK_OVERPLAN_SIGNALS = (
    "implementation plan",
    "multi-step",
    "oracle",
    "commit:check",
    "benchmark",
    "governance",
    "architecture",
)
RAW_REQUIRED_FIELDS = (
    "run_id",
    "dataset_sha",
    "git_head",
    "backend",
    "model",
    "condition",
    "eval_id",
    "sample_id",
    "prompt_sha",
    "output_sha",
    "output",
    "pass",
    "excerpt",
    "grader_version",
    "grader_sha",
)
EVIDENCE_LIMITS = (
    "fixture and echo backends prove pipeline behavior, not live model quality",
    "claude-cli backend uses Claude Code without --bare, so default Claude Code context may influence outputs beyond the runner prompt",
    "deterministic substring grading is intentionally strict and wording-sensitive",
    "v1-rc certification requires comparing full, none, and drop conditions from the same dataset hash",
    "loss=1 ablations require adversarial follow-up before making strong rent claims",
)


def certification_class_for_backend(backend: str) -> str:
    if backend in {"fixture", "echo"}:
        return PIPELINE_CERTIFICATION_CLASS
    return BEHAVIOR_CERTIFICATION_CLASS


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


def slug(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return result or "sample"


def redact_secrets(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    return redacted


def excerpt(text: str, limit: int = 240) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 3]}..."


def dataset_sha(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def grader_contract_sha() -> str:
    return sha256_text(json.dumps(GRADER_CONTRACT, sort_keys=True))


def grader_manifest() -> dict[str, Any]:
    source = Path(__file__).read_bytes()
    return {
        "certification_profile": CERTIFICATION_PROFILE,
        "certification_classes": [
            PIPELINE_CERTIFICATION_CLASS,
            BEHAVIOR_CERTIFICATION_CLASS,
        ],
        "runner_version": RUNNER_VERSION,
        "grader_version": GRADER_VERSION,
        "grader_sha": grader_contract_sha(),
        "runner_source_sha": sha256_bytes(source),
        "contract": GRADER_CONTRACT,
    }


def active_sections(condition: str, sections: list[str]) -> list[str]:
    if condition == "none":
        return []
    if condition.startswith("drop:"):
        dropped = condition.split(":", 1)[1]
        return [section for section in sections if section != dropped]
    return sections


def build_prompt(condition: str, ev: dict[str, Any], sections: list[str]) -> str:
    active = active_sections(condition, sections)
    if active:
        context = "\n".join(
            f"- {section}: {SECTION_RULES.get(section, 'Apply this section.')}"
            for section in active
        )
    else:
        context = "No project-specific engineering discipline context is provided."

    return "\n".join(
        [
            "You are a coding agent responding to a user request.",
            f"Benchmark condition: {condition}",
            "Active context:",
            context,
            "",
            "Benchmark response constraints:",
            "- Treat this as an eval prompt, not a live filesystem session.",
            "- Do not dwell on missing tool access.",
            "- Make the behavioral decision caused by active context visible in the response.",
            "",
            "User request:",
            str(ev["prompt"]),
            "",
            "Respond as the agent would before or during implementation.",
        ]
    )


def build_samples(data: dict[str, Any]) -> list[dict[str, Any]]:
    plan = build_plan(data)
    sections = list(plan["sections"])
    samples: list[dict[str, Any]] = []
    index = 1

    for condition in plan["conditions"]:
        for ev in trigger_evals(data):
            prompt = build_prompt(str(condition), ev, sections)
            samples.append({
                "index": index,
                "sample_id": f"{index:04d}-{slug(str(condition))}-{ev['id']}",
                "condition": condition,
                "kind": ev["kind"],
                "gate": ev.get("target_section", "unknown"),
                "eval": ev,
                "prompt": prompt,
                "prompt_sha": sha256_text(prompt),
            })
            index += 1

    for ev in distractor_evals(data):
        condition = "distractor"
        prompt = build_prompt(condition, ev, sections)
        samples.append({
            "index": index,
            "sample_id": f"{index:04d}-{condition}-{ev['id']}",
            "condition": condition,
            "kind": ev["kind"],
            "gate": "distractor",
            "eval": ev,
            "prompt": prompt,
            "prompt_sha": sha256_text(prompt),
        })
        index += 1

    return samples


def select_shard(samples: list[dict[str, Any]], shard_index: int | None, shard_count: int | None) -> list[dict[str, Any]]:
    if shard_index is None and shard_count is None:
        return samples
    if shard_index is None or shard_count is None:
        raise ValueError("--shard-index and --shard-count must be used together")
    if shard_count < 1:
        raise ValueError("--shard-count must be at least 1")
    if shard_index < 0 or shard_index >= shard_count:
        raise ValueError("--shard-index must be between 0 and shard-count - 1")
    return [
        sample for position, sample in enumerate(samples)
        if position % shard_count == shard_index
    ]


class Backend:
    name = "backend"

    def __init__(self, model: str | None = None, **_: Any) -> None:
        self.model = model or f"{self.name}-v0"

    def complete(self, sample: dict[str, Any]) -> str:
        raise NotImplementedError


class EchoBackend(Backend):
    name = "echo"

    def complete(self, sample: dict[str, Any]) -> str:
        return str(sample["prompt"])


class FixtureBackend(Backend):
    name = "fixture"

    def complete(self, sample: dict[str, Any]) -> str:
        ev = sample["eval"]
        expected = expected_fixture_text(ev)
        forbidden = " ".join(str(item) for item in ev.get("forbidden", []))
        condition = str(sample["condition"])

        if ev.get("kind") == "distractor":
            return f"Fixture direct response: {expected}."

        if condition == "full":
            return f"Fixture disciplined response: {expected}."

        if condition == "none":
            return f"Fixture baseline miss: {forbidden}."

        if condition == f"drop:{ev.get('target_section')}":
            return f"Fixture ablation miss: {forbidden}."

        return f"Fixture unaffected response: {expected}."


class ClaudeCliBackend(Backend):
    name = "claude-cli"

    def __init__(
        self,
        model: str | None = None,
        claude_bin: str | None = None,
        max_budget_usd: str | None = None,
        timeout_seconds: int = 180,
    ) -> None:
        super().__init__(model=model or "sonnet")
        self.claude_bin = claude_bin or "claude"
        self.max_budget_usd = max_budget_usd
        self.timeout_seconds = timeout_seconds

    def complete(self, sample: dict[str, Any]) -> str:
        if shutil.which(self.claude_bin) is None:
            raise RuntimeError(f"claude CLI not found: {self.claude_bin}")

        command = [
            self.claude_bin,
            "--print",
            "--output-format",
            "text",
            "--no-session-persistence",
            "--model",
            self.model,
            "--tools",
            "",
        ]
        if self.max_budget_usd:
            command.extend(["--max-budget-usd", self.max_budget_usd])
        command.append(str(sample["prompt"]))

        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        if result.returncode != 0:
            details = " ".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
            raise RuntimeError(f"claude CLI failed for {sample['sample_id']}: {details}")
        return result.stdout.strip()


def make_backend(
    name: str,
    model: str | None,
    claude_bin: str | None = None,
    max_budget_usd: str | None = None,
    timeout_seconds: int = 180,
) -> Backend:
    backends: dict[str, type[Backend]] = {
        "claude-cli": ClaudeCliBackend,
        "echo": EchoBackend,
        "fixture": FixtureBackend,
    }
    if name not in backends:
        choices = ", ".join(sorted(backends))
        raise ValueError(f"unknown backend {name!r}; choose one of: {choices}")
    return backends[name](
        model=model,
        claude_bin=claude_bin,
        max_budget_usd=max_budget_usd,
        timeout_seconds=timeout_seconds,
    )


def expected_fixture_text(ev: dict[str, Any]) -> str:
    terms = [str(item) for item in ev.get("expected", [])]
    for group in ev.get("expected_any", []):
        if isinstance(group, list) and group:
            terms.append(str(group[0]))
    return " ".join(terms).strip()


def grade_output(ev: dict[str, Any], output: str) -> dict[str, Any]:
    lowered = output.lower()
    expected = [
        {
            "text": str(term),
            "present": str(term).lower() in lowered,
        }
        for term in ev.get("expected", [])
    ]
    expected_any = []
    for group in ev.get("expected_any", []):
        if not isinstance(group, list):
            continue
        terms = [
            {
                "text": str(term),
                "present": str(term).lower() in lowered,
            }
            for term in group
        ]
        expected_any.append({
            "terms": terms,
            "present": any(term["present"] for term in terms),
        })
    forbidden = [
        {
            "text": str(term),
            "present": str(term).lower() in lowered,
        }
        for term in ev.get("forbidden", [])
    ]
    missing_expected = [item["text"] for item in expected if not item["present"]]
    missing_expected_any = [
        " | ".join(term["text"] for term in group["terms"])
        for group in expected_any
        if not group["present"]
    ]
    present_forbidden = [item["text"] for item in forbidden if item["present"]]

    passed = not missing_expected and not missing_expected_any and not present_forbidden
    reasons: list[str] = []
    if missing_expected:
        reasons.append(f"missing expected: {', '.join(missing_expected)}")
    if missing_expected_any:
        reasons.append(f"missing expected_any: {', '.join(missing_expected_any)}")
    if present_forbidden:
        reasons.append(f"present forbidden: {', '.join(present_forbidden)}")

    return {
        "pass": passed,
        "expected": expected,
        "expected_any": expected_any,
        "forbidden": forbidden,
        "reasons": reasons,
    }


def distractor_leak_reasons(record: dict[str, Any]) -> list[str]:
    if record.get("kind") != "distractor":
        return []

    output = str(record.get("output", "")).lower()
    prompt = str(record.get("prompt", "")).lower()
    reasons: list[str] = []
    for reason, signals in DISTRACTOR_LEAK_SIGNALS.items():
        if any(signal in output for signal in signals):
            reasons.append(reason)

    is_trivial_typo = "typo" in prompt or "'teh' should be 'the'" in prompt
    if is_trivial_typo and any(signal in output for signal in TRIVIAL_TASK_OVERPLAN_SIGNALS):
        reasons.append("overplans_trivial_typo")

    is_read_only = "read this file" in prompt or "summarize the title" in prompt
    if is_read_only and "implementation plan" in output:
        reasons.append("overplans_read_only_task")

    return sorted(set(reasons))


def rate(passed: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(passed / total, 4)


def condition_pass_rate(records: list[dict[str, Any]], condition: str, kind: str = "trigger") -> float:
    selected = [
        record for record in records
        if record["condition"] == condition and record["kind"] == kind
    ]
    passed = sum(1 for record in selected if record["pass"])
    return rate(passed, len(selected))


def raw_record_complete(record: dict[str, Any]) -> bool:
    return all(record.get(field) not in (None, "") for field in RAW_REQUIRED_FIELDS)


def duplicate_sample_count(records: list[dict[str, Any]]) -> int:
    counts: dict[str, int] = defaultdict(int)
    for record in records:
        counts[str(record.get("sample_id"))] += 1
    return sum(1 for count in counts.values() if count > 1)


def ablation_losses(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    gates = sorted({
        record["gate"]
        for record in records
        if record["kind"] == "trigger" and record["gate"] != "unknown"
    })
    losses: dict[str, dict[str, Any]] = {}
    for gate in gates:
        full = [
            record for record in records
            if record["kind"] == "trigger" and record["condition"] == "full" and record["gate"] == gate
        ]
        dropped = [
            record for record in records
            if record["kind"] == "trigger" and record["condition"] == f"drop:{gate}" and record["gate"] == gate
        ]
        full_passes = sum(1 for record in full if record["pass"])
        drop_passes = sum(1 for record in dropped if record["pass"])
        loss = full_passes - drop_passes
        if loss <= 0:
            decision = "prune_or_move_candidate_unless_justified"
        elif loss == 1:
            decision = "adversarial_follow_up_required"
        else:
            decision = "keep"
        losses[gate] = {
            "full_passes": full_passes,
            "drop_passes": drop_passes,
            "loss": loss,
            "decision": decision,
        }
    return losses


def certification_metrics(records: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    planned_calls = int(manifest["planned_calls"])
    raw_complete = sum(1 for record in records if raw_record_complete(record))
    failures = [record for record in records if not record["pass"]]
    distractors = [record for record in records if record["kind"] == "distractor"]
    distractor_fails = [record for record in distractors if not record["pass"]]
    distractor_leaks = [
        record for record in distractors
        if record.get("distractor_leak") or distractor_leak_reasons(record)
    ]
    backend_errors = [record for record in records if record.get("backend_error")]
    unique_sample_ids = {record.get("sample_id") for record in records}
    full_rate = condition_pass_rate(records, "full")
    none_rate = condition_pass_rate(records, "none")

    return {
        "certification_class": manifest["certification_class"],
        "plan_run_parity": rate(len(records), planned_calls),
        "unique_sample_coverage": rate(len(unique_sample_ids), planned_calls),
        "duplicate_sample_count": duplicate_sample_count(records),
        "raw_evidence_coverage": rate(raw_complete, planned_calls),
        "trigger_pass_rate_full": full_rate,
        "trigger_pass_rate_none": none_rate,
        "behavioral_lift": round(full_rate - none_rate, 4),
        "distractor_fail_rate": rate(len(distractor_fails), len(distractors)),
        "distractor_leak_rate": rate(len(distractor_leaks), len(distractors)),
        "all_failures_have_excerpt": all(bool(record.get("excerpt")) for record in failures),
        "dataset_sha_present": bool(manifest.get("dataset_sha")),
        "git_head_present": bool(manifest.get("git_head")) and manifest.get("git_head") != "unknown",
        "backend_declared": bool(manifest.get("backend")),
        "backend_error_count": len(backend_errors),
        "grader_version_declared": bool(manifest.get("grader_version")),
        "grader_sha_present": bool(manifest.get("grader_sha")),
        "evidence_limits_declared": bool(EVIDENCE_LIMITS),
    }


def certification_decision(metrics: dict[str, Any]) -> dict[str, Any]:
    no_go: list[str] = []
    thresholds = {
        "plan_run_parity": "must equal 1.0",
        "unique_sample_coverage": "must equal 1.0",
        "duplicate_sample_count": "must equal 0",
        "raw_evidence_coverage": "must equal 1.0",
        "trigger_pass_rate_full": "must be greater than trigger_pass_rate_none",
        "distractor_fail_rate": "reported separately from confirmed leak",
        "distractor_leak_rate": "must equal 0",
        "all_failures_have_excerpt": "must be true",
        "dataset_sha_present": "must be true",
        "git_head_present": "must be true",
        "backend_declared": "must be true",
        "grader_version_declared": "must be true",
        "grader_sha_present": "must be true",
        "evidence_limits_declared": "must be true",
    }

    if metrics["plan_run_parity"] != 1.0:
        no_go.append("run diverged from plan")
    if metrics["unique_sample_coverage"] != 1.0:
        no_go.append("unique sample coverage is incomplete")
    if metrics["duplicate_sample_count"]:
        no_go.append("duplicate sample ids occurred")
    if metrics["raw_evidence_coverage"] != 1.0:
        no_go.append("raw evidence coverage is incomplete")
    if metrics["trigger_pass_rate_full"] <= metrics["trigger_pass_rate_none"]:
        no_go.append("full condition did not outperform none")
    if metrics["distractor_leak_rate"] != 0:
        no_go.append("distractor leak confirmed")
    if not metrics["all_failures_have_excerpt"]:
        no_go.append("at least one failure lacks an audit excerpt")
    if metrics["backend_error_count"]:
        no_go.append("backend errors occurred during execution")
    for key in (
        "dataset_sha_present",
        "git_head_present",
        "backend_declared",
        "grader_version_declared",
        "grader_sha_present",
        "evidence_limits_declared",
    ):
        if not metrics[key]:
            no_go.append(f"{key} is false")

    return {
        "profile": CERTIFICATION_PROFILE,
        "class": metrics["certification_class"],
        "status": "GO" if not no_go else "NO-GO",
        "thresholds": thresholds,
        "no_go": no_go,
    }


def summarize(records: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    by_condition: dict[str, dict[str, int]] = defaultdict(lambda: {"passed": 0, "total": 0})
    by_gate: dict[str, dict[str, int]] = defaultdict(lambda: {"passed": 0, "total": 0})

    for record in records:
        for bucket, key in ((by_condition, record["condition"]), (by_gate, record["gate"])):
            bucket[key]["total"] += 1
            if record["pass"]:
                bucket[key]["passed"] += 1

    def finalize(bucket: dict[str, dict[str, int]]) -> dict[str, dict[str, float | int]]:
        return {
            key: {
                "passed": value["passed"],
                "total": value["total"],
                "pass_rate": rate(value["passed"], value["total"]),
            }
            for key, value in sorted(bucket.items())
        }

    passed = sum(1 for record in records if record["pass"])
    metrics = certification_metrics(records, manifest)
    return {
        "run_id": manifest["run_id"],
        "runner_version": RUNNER_VERSION,
        "certification_profile": CERTIFICATION_PROFILE,
        "certification_class": manifest["certification_class"],
        "certification": certification_decision(metrics),
        "dataset_sha": manifest["dataset_sha"],
        "git_head": manifest["git_head"],
        "backend": manifest["backend"],
        "model": manifest["model"],
        "grader_version": manifest["grader_version"],
        "grader_sha": manifest["grader_sha"],
        "planned_calls": manifest["planned_calls"],
        "executed_calls": len(records),
        "passed": passed,
        "failed": len(records) - passed,
        "pass_rate": rate(passed, len(records)),
        "metrics": metrics,
        "ablation_losses": ablation_losses(records),
        "evidence_limits": list(EVIDENCE_LIMITS),
        "by_condition": finalize(by_condition),
        "by_gate": finalize(by_gate),
        "failures": [
            {
                "sample_id": record["sample_id"],
                "condition": record["condition"],
                "gate": record["gate"],
                "eval_id": record["eval_id"],
                "reasons": record["reasons"],
                "excerpt": record["excerpt"],
                "distractor_leak": bool(record.get("distractor_leak")),
                "distractor_leak_reasons": record.get("distractor_leak_reasons", []),
            }
            for record in records
            if not record["pass"]
        ],
    }


def markdown_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    widths = [max(len(row[index]) for row in rows) for index in range(len(rows[0]))]
    rendered = []
    for row_index, row in enumerate(rows):
        rendered.append("| " + " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)) + " |")
        if row_index == 0:
            rendered.append("| " + " | ".join("-" * widths[index] for index in range(len(row))) + " |")
    return "\n".join(rendered)


def write_report(path: Path, manifest: dict[str, Any], summary: dict[str, Any]) -> None:
    tds_id = f"evidence.context_mesh.{slug(str(manifest['run_id'])).replace('-', '_')}"
    certification = summary["certification"]
    metrics = summary["metrics"]
    condition_rows = [["Condition", "Passed", "Total", "Pass Rate"]]
    for condition, value in summary["by_condition"].items():
        condition_rows.append([
            condition,
            str(value["passed"]),
            str(value["total"]),
            f"{value['pass_rate']:.2%}",
        ])

    gate_rows = [["Gate", "Passed", "Total", "Pass Rate"]]
    for gate, value in summary["by_gate"].items():
        gate_rows.append([
            gate,
            str(value["passed"]),
            str(value["total"]),
            f"{value['pass_rate']:.2%}",
        ])

    failure_rows = [["Sample", "Condition", "Gate", "Reason", "Distractor Leak", "Leak Reasons", "Excerpt"]]
    for failure in summary["failures"][:20]:
        failure_rows.append([
            failure["sample_id"],
            failure["condition"],
            failure["gate"],
            "; ".join(failure["reasons"]),
            str(failure["distractor_leak"]),
            ", ".join(failure["distractor_leak_reasons"]),
            failure["excerpt"],
        ])

    failure_section = "No failures."
    if summary["failures"]:
        failure_section = markdown_table(failure_rows)

    metrics_rows = [["Metric", "Value"]]
    for key, value in metrics.items():
        metrics_rows.append([key, str(value)])

    threshold_rows = [["Threshold", "Rule"]]
    for key, value in certification["thresholds"].items():
        threshold_rows.append([key, value])

    ablation_rows = [["Gate", "Full Passes", "Drop Passes", "Loss", "Decision"]]
    for gate, value in summary["ablation_losses"].items():
        ablation_rows.append([
            gate,
            str(value["full_passes"]),
            str(value["drop_passes"]),
            str(value["loss"]),
            value["decision"],
        ])

    no_go_section = "No NO-GO conditions."
    if certification["no_go"]:
        no_go_section = "\n".join(f"- {reason}" for reason in certification["no_go"])

    limits_section = "\n".join(f"- {limit}" for limit in summary["evidence_limits"])

    text = f"""---
tds_id: {tds_id}
tds_class: evidence
status: active
consumer: benchmark reviewers
source_of_truth: false
evidence_level: L4
---

# Context Mesh Benchmark Report

Run ID: `{manifest['run_id']}`

| Field | Value |
|-------|-------|
| Runner | `{RUNNER_VERSION}` |
| Certification profile | `{CERTIFICATION_PROFILE}` |
| Certification class | `{manifest['certification_class']}` |
| Certification status | `{certification['status']}` |
| Backend | `{manifest['backend']}` |
| Model | `{manifest['model']}` |
| Grader | `{manifest['grader_version']}` |
| Grader SHA | `{manifest['grader_sha']}` |
| Dataset SHA | `{manifest['dataset_sha']}` |
| Git HEAD | `{manifest['git_head']}` |
| Planned calls | `{manifest['planned_calls']}` |
| Executed calls | `{summary['executed_calls']}` |
| Pass rate | `{summary['pass_rate']:.2%}` |

## Certification Thresholds

{markdown_table(threshold_rows)}

## Certification Metrics

{markdown_table(metrics_rows)}

## NO-GO

{no_go_section}

## By Condition

{markdown_table(condition_rows)}

## By Gate

{markdown_table(gate_rows)}

## Ablation Losses

{markdown_table(ablation_rows)}

## Failures

{failure_section}

## Evidence Limits

{limits_section}

## Evidence Files

- `manifest.json`
- `raw.ndjson`
- `summary.json`
- `REPORT.md`
- `graders-sha.json`
"""
    path.write_text(text, encoding="utf-8")


def update_tds_index(report_path: Path, manifest: dict[str, Any]) -> None:
    try:
        relpath = report_path.relative_to(ROOT).as_posix()
    except ValueError:
        return
    if not relpath.startswith("docs/"):
        return

    index = ROOT / "docs/tds/DOCS-INDEX.yml"
    text = index.read_text(encoding="utf-8")
    if f"path: {relpath}" in text:
        return

    doc_id = f"evidence.context_mesh.{slug(str(manifest['run_id'])).replace('-', '_')}"
    entry = f"""  - path: {relpath}
    id: {doc_id}
    class: evidence
    status: active
    consumer: benchmark reviewers
    source_of_truth: false
    evidence_level: L4
"""
    index.write_text(f"{text.rstrip()}\n{entry}", encoding="utf-8")


def write_evidence(
    run_dir: Path,
    manifest: dict[str, Any],
    records: list[dict[str, Any]],
    update_index: bool,
) -> dict[str, Path]:
    if run_dir.exists():
        raise FileExistsError(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    manifest_path = run_dir / "manifest.json"
    raw_path = run_dir / "raw.ndjson"
    summary_path = run_dir / "summary.json"
    report_path = run_dir / "REPORT.md"
    graders_path = run_dir / "graders-sha.json"

    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    graders_path.write_text(json.dumps(grader_manifest(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with raw_path.open("x", encoding="utf-8") as raw:
        for record in records:
            raw.write(json.dumps(record, sort_keys=True) + "\n")

    summary = summarize(records, manifest)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(report_path, manifest, summary)
    if update_index:
        update_tds_index(report_path, manifest)

    return {
        "manifest": manifest_path,
        "raw": raw_path,
        "summary": summary_path,
        "report": report_path,
        "graders": graders_path,
    }


def write_shard_evidence(
    run_dir: Path,
    manifest: dict[str, Any],
    records: list[dict[str, Any]],
) -> dict[str, Path]:
    if run_dir.exists():
        raise FileExistsError(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    manifest_path = run_dir / "manifest.json"
    raw_path = run_dir / "raw.ndjson"
    graders_path = run_dir / "graders-sha.json"

    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    graders_path.write_text(json.dumps(grader_manifest(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with raw_path.open("x", encoding="utf-8") as raw:
        for record in records:
            raw.write(json.dumps(record, sort_keys=True) + "\n")

    return {
        "manifest": manifest_path,
        "raw": raw_path,
        "graders": graders_path,
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_raw_records(raw_path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in raw_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def collect_shard_dirs(paths: list[Path]) -> list[Path]:
    shard_dirs: list[Path] = []
    for path in paths:
        if (path / "manifest.json").exists() and (path / "raw.ndjson").exists():
            shard_dirs.append(path)
            continue
        shard_dirs.extend(
            child for child in sorted(path.iterdir())
            if child.is_dir() and (child / "manifest.json").exists() and (child / "raw.ndjson").exists()
        )
    return sorted(shard_dirs)


def merge_shard_records(
    shard_paths: list[Path],
    samples: list[dict[str, Any]],
    digest: str,
    run_id: str,
    dataset_path: Path,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]], list[str]]:
    failures: list[str] = []
    shard_dirs = collect_shard_dirs(shard_paths)
    manifests: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []

    if not shard_dirs:
        return None, [], [f"no shard directories found: {', '.join(str(path) for path in shard_paths)}"]

    for shard_dir in shard_dirs:
        manifest_path = shard_dir / "manifest.json"
        raw_path = shard_dir / "raw.ndjson"
        if not manifest_path.exists() or not raw_path.exists():
            failures.append(f"shard missing manifest or raw: {shard_dir}")
            continue
        manifest = load_json(manifest_path)
        manifests.append(manifest)
        for record in load_raw_records(raw_path):
            record = dict(record)
            record["source_run_id"] = record["run_id"]
            record["source_shard_id"] = manifest.get("shard_id", manifest.get("run_id"))
            record["run_id"] = run_id
            records.append(record)

    if not manifests:
        return None, records, failures or ["no valid shard manifests found"]

    first = manifests[0]
    consistent_fields = (
        "dataset_sha",
        "git_head",
        "backend",
        "model",
        "grader_version",
        "grader_sha",
        "runner_version",
        "certification_profile",
        "certification_class",
    )
    for manifest in manifests:
        for field in consistent_fields:
            if manifest.get(field) != first.get(field):
                failures.append(f"shard manifest mismatch for {field}: {manifest.get('run_id')}")

    expected_ids = {sample["sample_id"] for sample in samples}
    seen_ids: dict[str, int] = defaultdict(int)
    sample_by_id = {sample["sample_id"]: sample for sample in samples}
    for record in records:
        sample_id = record.get("sample_id")
        seen_ids[str(sample_id)] += 1
        if sample_id not in expected_ids:
            failures.append(f"unexpected sample id in shard raw: {sample_id}")
            continue
        sample = sample_by_id[sample_id]
        if record.get("prompt_sha") != sample["prompt_sha"]:
            failures.append(f"prompt hash mismatch for {sample_id}")
        if record.get("dataset_sha") != digest:
            failures.append(f"dataset hash mismatch for {sample_id}")
        if record.get("output_sha") != sha256_text(str(record.get("output", ""))):
            failures.append(f"output hash mismatch for {sample_id}")
        if not raw_record_complete(record):
            failures.append(f"raw record missing required fields for {sample_id}")

    duplicates = sorted(sample_id for sample_id, count in seen_ids.items() if count > 1)
    missing = sorted(expected_ids - set(seen_ids))
    if duplicates:
        failures.append(f"duplicate sample ids: {', '.join(duplicates)}")
    if missing:
        failures.append(f"missing sample ids: {', '.join(missing)}")

    manifest = {
        "run_id": run_id,
        "runner_version": RUNNER_VERSION,
        "certification_profile": CERTIFICATION_PROFILE,
        "certification_class": first["certification_class"],
        "created_at": utc_now(),
        "dataset": str(dataset_path),
        "dataset_sha": digest,
        "git_head": first["git_head"],
        "backend": first["backend"],
        "model": first["model"],
        "grader_version": first["grader_version"],
        "grader_sha": first["grader_sha"],
        "planned_calls": len(samples),
        "merge_contract_version": "context-mesh-merge@0.1.0",
        "merge_sources": [
            {
                "run_id": manifest["run_id"],
                "shard_id": manifest.get("shard_id"),
                "shard_index": manifest.get("shard_index"),
                "shard_count": manifest.get("shard_count"),
                "raw_sha": sha256_bytes((shard_dir / "raw.ndjson").read_bytes()),
            }
            for manifest, shard_dir in zip(manifests, shard_dirs)
        ],
    }
    return manifest, sorted(records, key=lambda record: record["sample_id"]), failures


def merge_shards(args: argparse.Namespace) -> int:
    data = load_dataset(args.dataset)
    failures = validate_dataset(data)
    if failures:
        print("[context-mesh-merge] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    samples = build_samples(data)
    digest = dataset_sha(args.dataset)
    run_id = args.run_id or build_run_id("merged", digest)
    manifest, records, merge_failures = merge_shard_records(args.merge_shards, samples, digest, run_id, args.dataset)
    if merge_failures or manifest is None:
        print("[context-mesh-merge] FAIL")
        for failure in merge_failures:
            print(f"- {failure}")
        return 1

    run_dir = args.out_root / run_id
    try:
        paths = write_evidence(run_dir, manifest, records, update_index=not args.no_tds_index)
    except FileExistsError as exc:
        print("[context-mesh-merge] FAIL")
        print(f"- {exc}")
        return 1
    summary = summarize(records, manifest)
    print("[context-mesh-merge] PASS")
    print(json.dumps({
        "run_id": run_id,
        "planned_calls": manifest["planned_calls"],
        "executed_calls": summary["executed_calls"],
        "passed": summary["passed"],
        "failed": summary["failed"],
        "pass_rate": summary["pass_rate"],
        "manifest": str(paths["manifest"]),
        "raw": str(paths["raw"]),
        "summary": str(paths["summary"]),
        "report": str(paths["report"]),
        "graders": str(paths["graders"]),
        "certification_class": summary["certification_class"],
        "certification_status": summary["certification"]["status"],
    }, indent=2))
    return 0


def build_run_id(backend: str, dataset_digest: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}-{backend}-{dataset_digest[:8]}"


def execute_samples(samples: list[dict[str, Any]], backend: Backend, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for sample in samples:
        backend_error = ""
        try:
            output = redact_secrets(backend.complete(sample))
        except Exception as exc:
            backend_error = redact_secrets(str(exc))
            output = f"BACKEND_ERROR: {backend_error}"
        grading = grade_output(sample["eval"], output)
        ev = sample["eval"]
        record = {
            "run_id": manifest["run_id"],
            "runner_version": RUNNER_VERSION,
            "created_at": manifest["created_at"],
            "dataset_sha": manifest["dataset_sha"],
            "git_head": manifest["git_head"],
            "backend": manifest["backend"],
            "model": manifest["model"],
            "certification_profile": CERTIFICATION_PROFILE,
            "certification_class": manifest["certification_class"],
            "grader_version": manifest["grader_version"],
            "grader_sha": manifest["grader_sha"],
            "condition": sample["condition"],
            "kind": sample["kind"],
            "gate": sample["gate"],
            "eval_id": ev["id"],
            "sample_id": sample["sample_id"],
            "prompt_sha": sample["prompt_sha"],
            "output_sha": sha256_text(output),
            "prompt": sample["prompt"],
            "output": output,
            "backend_error": backend_error,
            "pass": grading["pass"],
            "expected": grading["expected"],
            "expected_any": grading["expected_any"],
            "forbidden": grading["forbidden"],
            "reasons": grading["reasons"],
            "excerpt": excerpt(output),
        }
        leak_reasons = distractor_leak_reasons(record)
        record["distractor_leak"] = bool(leak_reasons)
        record["distractor_leak_reasons"] = leak_reasons
        if "shard_id" in manifest:
            record["source_shard_id"] = manifest["shard_id"]
        records.append(record)
    return records


def run(args: argparse.Namespace) -> int:
    data = load_dataset(args.dataset)
    failures = validate_dataset(data)
    if failures:
        print("[context-mesh-run] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    plan = build_plan(data, args.dataset)
    samples = build_samples(data)
    if len(samples) != plan["planned_calls"]:
        print("[context-mesh-run] FAIL")
        print(f"- matrix diverged from plan: samples={len(samples)} planned_calls={plan['planned_calls']}")
        return 1
    try:
        selected_samples = select_shard(samples, args.shard_index, args.shard_count)
    except ValueError as exc:
        print("[context-mesh-run] FAIL")
        print(f"- {exc}")
        return 1
    is_shard = args.shard_index is not None

    if args.dry_run:
        print("[context-mesh-run] DRY-RUN")
        print(json.dumps({
            **plan,
            "matrix_calls": len(samples),
            "selected_calls": len(selected_samples),
            "shard_index": args.shard_index,
            "shard_count": args.shard_count,
            "plan_parity": True,
        }, indent=2))
        return 0

    if is_shard and not args.run_id:
        print("[context-mesh-run] FAIL")
        print("- shard mode requires --run-id")
        return 1

    digest = dataset_sha(args.dataset)
    run_id = args.run_id or build_run_id(args.backend, digest)
    backend = make_backend(
        args.backend,
        args.model,
        claude_bin=args.claude_bin,
        max_budget_usd=args.max_budget_usd,
        timeout_seconds=args.timeout_seconds,
    )
    created_at = utc_now()
    head = git_head()
    grader = grader_manifest()
    certification_class = certification_class_for_backend(backend.name)
    manifest = {
        "run_id": run_id,
        "runner_version": RUNNER_VERSION,
        "certification_profile": CERTIFICATION_PROFILE,
        "certification_class": certification_class,
        "created_at": created_at,
        "dataset": str(args.dataset),
        "dataset_sha": digest,
        "git_head": head,
        "backend": backend.name,
        "model": backend.model,
        "grader_version": grader["grader_version"],
        "grader_sha": grader["grader_sha"],
        "planned_calls": plan["planned_calls"],
    }
    if is_shard:
        manifest["shard_id"] = f"shard-{args.shard_index:02d}-of-{args.shard_count:02d}"
        manifest["shard_index"] = args.shard_index
        manifest["shard_count"] = args.shard_count
        manifest["shard_calls"] = len(selected_samples)

    records = execute_samples(selected_samples, backend, manifest)

    out_root = args.out_root
    run_dir = out_root / run_id
    if is_shard:
        try:
            paths = write_shard_evidence(run_dir, manifest, records)
        except FileExistsError as exc:
            print("[context-mesh-shard] FAIL")
            print(f"- {exc}")
            return 1
        print("[context-mesh-shard] PASS")
        print(json.dumps({
            "run_id": run_id,
            "planned_calls": plan["planned_calls"],
            "shard_calls": len(records),
            "shard_index": args.shard_index,
            "shard_count": args.shard_count,
            "manifest": str(paths["manifest"]),
            "raw": str(paths["raw"]),
            "graders": str(paths["graders"]),
            "certification_class": certification_class,
            "certification_status": "SHARD-NOT-CERTIFIED",
        }, indent=2))
        return 0

    update_index = not args.no_tds_index
    try:
        paths = write_evidence(run_dir, manifest, records, update_index=update_index)
    except FileExistsError as exc:
        print("[context-mesh-run] FAIL")
        print(f"- {exc}")
        return 1
    summary = summarize(records, manifest)

    print("[context-mesh-run] PASS")
    print(json.dumps({
        "run_id": run_id,
        "planned_calls": plan["planned_calls"],
        "executed_calls": summary["executed_calls"],
        "passed": summary["passed"],
        "failed": summary["failed"],
        "pass_rate": summary["pass_rate"],
        "manifest": str(paths["manifest"]),
        "raw": str(paths["raw"]),
        "summary": str(paths["summary"]),
        "report": str(paths["report"]),
        "graders": str(paths["graders"]),
        "certification_class": summary["certification_class"],
        "certification_status": summary["certification"]["status"],
    }, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--backend", default="fixture", choices=("fixture", "echo", "claude-cli"))
    parser.add_argument("--model")
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--max-budget-usd")
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--run-id")
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--shard-count", type=int)
    parser.add_argument("--shard-index", type=int)
    parser.add_argument("--merge-shards", type=Path, nargs="+")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-tds-index", action="store_true")
    args = parser.parse_args()
    if args.merge_shards:
        return merge_shards(args)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
