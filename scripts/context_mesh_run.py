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
import tempfile
import time
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


RUNNER_VERSION = "0.1.15"
CERTIFICATION_PROFILE = "v1-rc"
PROGRESS_LOG_CONTRACT = "context-mesh-progress@0.1.0"
PIPELINE_CERTIFICATION_CLASS = "pipeline-v1-rc"
BEHAVIOR_CERTIFICATION_CLASS = "behavior-v1-rc"
RUNTIME_SKILL_CERTIFICATION_CLASS = "runtime-skill-v1-rc"
DEFAULT_RUNTIME_SKILL_SOURCE = ROOT / "src/adapters/codex/skills/tes-engineering-discipline/SKILL.md"
GRADER_VERSION = "deterministic-substring@0.1.11"
EVIDENCE_REPORTS_ROOT = ROOT / "docs/evidence/reports"
DEFAULT_EVIDENCE_DOMAIN = "context-mesh"
LEGACY_OUT_ROOT = EVIDENCE_REPORTS_ROOT / DEFAULT_EVIDENCE_DOMAIN
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----", re.DOTALL),
)
SECTION_RULES = {
    "Mantra Gate": "Before state-changing work, use the TES Mantra Gate as a compact pre-action gate: VERIFY evidence, SCOPE allowed territory, choose BEST_PATH, DOCUMENT the record, name the ORACLE, RESOLVE ambiguity, and report STATUS before writes or closure.",
    "Think Before Coding": "Name facts, assumptions, ambiguity, tradeoffs, and blockers before acting; push back when a request says not to ask but hides privacy, sensitive-field, or scope ambiguity, and explicitly name the privacy or sensitive-field risk.",
    "Maturity Layer Gate": "Default material work to Birth only when no higher-layer evidence exists. Birth is invalid when the prompt names existing installs, an accepted contract, a compatibility interface, installer, fallback, rollback, release, migration, CLI, MCP, adapter, or public-doc surface. Promote to Consolidation, Evolution, or Platform only with promotion evidence naming protected baseline, allowed complexity, forbidden complexity, and oracle. Existing installs, installer, fallback, compatibility, rollback, release, migration, CLI, MCP, adapter, or public-doc surfaces are Platform, not Birth. In Platform, do not remove fallback or compatibility because the new path passes locally; keep the baseline until explicit retirement evidence and a compatibility or release oracle prove it can be cut. Use Fit First in Evolution: preserve accepted architecture instead of flattening it for local minimalism.",
    "Simplicity First": "Implement only the current requirement; say the smallest/current implementation and reject future-type scaffolding until a real case exists.",
    "Surgical Changes": "For bugfix-plus-cleanup requests, explicitly split the requested fix from unrelated cleanup; fix only the crash path, keep every touched line traceable to that crash, and defer whole-file reformatting or nearby renames unless necessary.",
    "Goal-Driven Execution": "Before acting, explicitly name the smallest reproducer or oracle; do not patch or claim closure before that check is named.",
}
GRADER_CONTRACT = {
    "version": GRADER_VERSION,
    "normalization": "case-insensitive substring match with negated forbidden mentions ignored",
    "pass_rule": "all expected strings present and no endorsed forbidden strings present",
    "expected": "each dataset expected string must appear in output",
    "expected_any": "each expected_any group must have at least one string present in output",
    "forbidden": "each dataset forbidden string must be absent from output unless all mentions appear in explicit rejection context",
    "distractor_fail": "a distractor output failed expected/forbidden literal checks",
    "distractor_leak": "a distractor output shows heavy context leakage signals",
}
DISTRACTOR_LEAK_SIGNALS = {
    "mentions_contract_gate": (
        "think before coding",
        "maturity layer gate",
        "simplicity first",
        "surgical changes",
        "goal-driven execution",
    ),
    "mentions_context_mesh": (
        "context mesh",
        "context-mesh",
    ),
    "mentions_benchmark_eval": (
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
    "codex-cli backend uses Codex CLI with a temporary adapter workspace; Stage 1 smoke evidence is not behavior certification",
    "deterministic substring grading is intentionally strict and wording-sensitive",
    "v1-rc certification requires comparing full, none, and drop conditions from the same dataset hash",
    "loss=1 ablations require adversarial follow-up before making strong rent claims",
)
CODEX_MODEL_ALLOWLIST = (
    "gpt-5.3-codex",
    "gpt-5.3-codex-spark",
    "gpt-5.4",
    "gpt-5.4-mini",
    "gpt-5.5",
)
CODEX_ADAPTER_PROMPT_CONTRACT = "codex-adapter-prompt@0.1.1"
PROGRESSIVE_LEVELS = {
    "L0": "static instrument check",
    "L1": "one target eval: full + none + informative drop",
    "L2": "up to two target evals plus distractors",
    "L3": "all evals for one target gate plus distractors",
    "L4": "full informative matrix",
}



def certification_class_for_backend(backend: str) -> str:
    if backend in {"fixture", "echo"}:
        return PIPELINE_CERTIFICATION_CLASS
    if backend == "runtime-skill":
        return RUNTIME_SKILL_CERTIFICATION_CLASS
    return BEHAVIOR_CERTIFICATION_CLASS


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_path_tree(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(child for child in path.rglob("*") if child.is_file()):
        relpath = item.relative_to(path).as_posix()
        digest.update(relpath.encode("utf-8"))
        digest.update(b"\0")
        digest.update(item.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_out_root(now: datetime | None = None) -> Path:
    stamp = now or datetime.now(timezone.utc)
    return (
        EVIDENCE_REPORTS_ROOT
        / f"{stamp:%Y}"
        / f"{stamp:%m}"
        / f"{stamp:%d}"
        / DEFAULT_EVIDENCE_DOMAIN
    )


def resolve_out_root(out_root: Path | None) -> Path:
    return out_root if out_root is not None else default_out_root()


class ProgressLogger:
    """Write monitor-friendly run progress without replacing retained evidence."""

    def __init__(self, run_dir: Path, enabled: bool = True) -> None:
        self.enabled = enabled
        self.run_dir = run_dir
        self.progress_dir = run_dir / "progress"
        self.events_path = self.progress_dir / "events.ndjson"
        self.latest_path = self.progress_dir / "latest.json"
        if not enabled:
            return
        self.progress_dir.mkdir(parents=True, exist_ok=True)
        if self.events_path.exists():
            raise FileExistsError(f"progress events already exists: {self.events_path}")
        self.events_path.write_text("", encoding="utf-8")

    def emit(self, event: str, **payload: Any) -> None:
        if not self.enabled:
            return
        record = {
            "created_at": utc_now(),
            "event": event,
            **payload,
        }
        with self.events_path.open("a", encoding="utf-8") as events:
            events.write(json.dumps(record, sort_keys=True) + "\n")
            events.flush()
        latest_tmp = self.latest_path.with_suffix(".json.tmp")
        latest_tmp.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        latest_tmp.replace(self.latest_path)


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


NEGATED_FORBIDDEN_PATTERNS = (
    re.compile(r"\bdo\s+not\b"),
    re.compile(r"\bdon't\b"),
    re.compile(r"\bwould\s+not\b"),
    re.compile(r"\bshould\s+not\b"),
    re.compile(r"\bmust\s+not\b"),
    re.compile(r"\bnot\s+(?:build|create|add|implement|introduce|remove|delete|flatten|call|skip|use)\b"),
    re.compile(r"\bnot\s*$"),
    re.compile(r"\bno\s+(?:need\s+to\s+)?(?:new\s+)?$"),
    re.compile(r"\bsem\s*$"),
    re.compile(r"\baus[eê]ncia\s+de\s*$"),
    re.compile(r"\bnenhum(?:a)?(?:\s+(?:refer[eê]ncia\s+a|evid[eê]ncia\s+de))?\s*$"),
    re.compile(r"\bzero\s+(?:arquivos\s+)?(?:staged\s+ou\s+)?$"),
    re.compile(r"\bwithout\b"),
    re.compile(r"\bn[ãa]o\s+(?:vou\s+)?(?:criar|construir|adicionar|implementar|introduzir|usar)\b"),
    re.compile(r"\breject(?:ing)?\b"),
    re.compile(r"\brejeit(?:ar|o|ando|e)\b"),
    re.compile(r"\bdefer(?:red|ring)?\b"),
    re.compile(r"\bavoid(?:ing)?\b"),
    re.compile(r"\bforbidden\b"),
)
NEGATED_FORBIDDEN_CONTEXT_PATTERNS = (
    re.compile(r"\bnot\s+a\s+runtime\s+need\b"),
    re.compile(r"\bviolat(?:e|es|ing)\b"),
    re.compile(r"\bscaffolding\b.*\bnot\b"),
    re.compile(r"\bgovernance-shaped\s+scaffolding\b"),
    re.compile(r"\bo\s+que\b.*\bn[ãa]o\b.*\b(?:construir|criaria|criar)\b"),
    re.compile(r"\bpor\s+qu[eê]\s+n[ãa]o\b"),
    re.compile(r"\bnegative\s+(?:checks|grep)\b"),
    re.compile(r"\bgrep\s+negativo\b"),
    re.compile(r"\bcandidatos?\s+a\s+negative-grep\b"),
    re.compile(r"\bforbidden\s+as\s+(?:an\s+)?(?:executed\s+)?action\b"),
    re.compile(r"\bproibido\s+como\s+a[cç][aã]o\s+(?:executada|realizada)\b"),
    re.compile(r"\bproibid[oa]s?\b"),
    re.compile(r"\bpara\s+atingir\b"),
    re.compile(r"\bviol(?:a|am|ar|ando|ou|aria|ação|a[cç][aã]o)\b"),
    re.compile(r"\bcolaps(?:a|am|ar|ando|ou|aria|ad[ao]s?)\b"),
    re.compile(r"\brecusad[ao]\b"),
    re.compile(r"\bcaso\s+de\s+falha\b"),
    re.compile(r"\bcobrindo\s+os\s+casos\b"),
    re.compile(r"\bfixtures?\s+cobr(?:e|em|indo)\b"),
    re.compile(r"\bpermitidos?\s+como\s+vocabul[aá]rio\s+de\s+pol[ií]tica\b"),
    re.compile(r"\bvocabul[aá]rio\s+de\s+pol[ií]tica\b"),
    re.compile(r"\bvocabul[aá]rio\s+de\s+policy\b"),
    re.compile(r"\bvocabul[aá]rio\s+v[aá]lido\b"),
    re.compile(r"\bn[ãa]o\s+deve\s+falhar\b"),
    re.compile(r"\bcontexto\s+proibido\b"),
)


def forbidden_term_mentions(output: str, term: str) -> list[dict[str, Any]]:
    lowered = output.lower()
    lowered_term = term.lower()
    mentions: list[dict[str, Any]] = []
    for match in re.finditer(re.escape(lowered_term), lowered):
        before = lowered[max(0, match.start() - 240):match.start()]
        after = lowered[match.end():match.end() + 160]
        context = f"{before}{lowered_term}{after}"
        plain_before = re.sub(r"[*_`~>\[\]()]|#+", " ", before)
        plain_before = re.sub(r"\s+", " ", plain_before)
        plain_context = re.sub(r"[*_`~>\[\]()]|#+", " ", context)
        plain_context = re.sub(r"\s+", " ", plain_context)
        line_start = lowered.rfind("\n", 0, match.start()) + 1
        line_end = lowered.find("\n", match.end())
        if line_end == -1:
            line_end = len(lowered)
        line_after = lowered[match.end():line_end]
        table_rejection = bool(
            "|" in lowered[line_start:line_end]
            and re.search(
                r"\|\s*(?:[*_`~ ]*)?(?:não|nao|nenhum|nenhuma|no|not|zero|reject(?:ed|ing)?|deletado|deleted)\b",
                line_after,
            )
        )
        negated = (
            any(pattern.search(plain_before) for pattern in NEGATED_FORBIDDEN_PATTERNS)
            or any(pattern.search(plain_context) for pattern in NEGATED_FORBIDDEN_CONTEXT_PATTERNS)
            or table_rejection
        )
        mentions.append({
            "start": match.start(),
            "end": match.end(),
            "negated": negated,
            "context": context.strip(),
        })
    return mentions


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
            RUNTIME_SKILL_CERTIFICATION_CLASS,
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
            "Active context:",
            context,
            "",
            "Response constraints:",
            "- Treat this as a controlled prompt, not a live filesystem session.",
            "- Do not dwell on missing tool access.",
            "- Make the behavioral decision caused by active context visible in the response.",
            "",
            "User request:",
            str(ev["prompt"]),
            "",
            "Respond as the agent would before or during implementation.",
        ]
    )


def build_adapter_user_prompt(ev: dict[str, Any]) -> str:
    custom_constraints = ev.get("response_constraints")
    if isinstance(custom_constraints, list) and all(isinstance(item, str) for item in custom_constraints):
        constraints = custom_constraints
    elif ev.get("kind") == "distractor":
        constraints = [
            "- Treat this as a controlled prompt, not a live filesystem session.",
            "- Use project instructions only when they are necessary to answer the request.",
            "- Answer the user's task directly.",
            "- Preserve the user's essential task words when they are natural, such as fix, typo, README, title, or summarize.",
            "- Do not name rules, gates, governance, benchmarks, evals, or project discipline.",
            "- Do not add assumptions, oracle, verification, or planning ceremony for trivial or read-only tasks.",
        ]
    else:
        constraints = [
            "- Treat this as a controlled prompt, not a live filesystem session.",
            "- This is a behavioral decision sample, not an implementation task.",
            "- Do not refuse, block, or defer because source files are absent; the workspace intentionally holds only project instructions.",
            "- State the design decision you would make before implementation, including the maturity layer and what you would and would not build.",
            "- Use any project instructions available in the current workspace.",
            "- Do not mention benchmark machinery, matrix conditions, or hidden labels.",
            "- Make the behavioral decision caused by available project context visible in the response.",
        ]
    return "\n".join(
        [
            "You are a coding agent responding to a user request.",
            "",
            "Response constraints:",
            *constraints,
            "",
            "User request:",
            str(ev["prompt"]),
            "",
            "Respond as the agent would before or during implementation.",
        ]
    )


ADAPTER_PROMPT_BACKENDS = {"codex-cli", "runtime-skill"}


def prepare_samples_for_backend(samples: list[dict[str, Any]], backend_name: str) -> list[dict[str, Any]]:
    # codex-cli and runtime-skill both deliver the discipline out-of-band (codex
    # materializes the skill into the workspace; runtime-skill injects it as the
    # system prompt), so the user prompt must be the task alone — not the
    # SECTION_RULES-laden prompt from build_prompt. Both therefore share the
    # adapter user prompt.
    if backend_name not in ADAPTER_PROMPT_BACKENDS:
        return samples
    prepared: list[dict[str, Any]] = []
    for sample in samples:
        prompt = build_adapter_user_prompt(sample["eval"])
        updated = dict(sample)
        updated["prompt"] = prompt
        updated["prompt_sha"] = sha256_text(prompt)
        updated["prompt_contract"] = CODEX_ADAPTER_PROMPT_CONTRACT
        prepared.append(updated)
    return prepared


def build_samples(data: dict[str, Any]) -> list[dict[str, Any]]:
    plan = build_plan(data)
    sections = list(plan["sections"])
    samples: list[dict[str, Any]] = []
    index = 1

    # Per trigger eval: full + none + its single informative drop
    # (drop:<target_section>). Dropping a non-target section measures nothing
    # (same as full) and ablation_losses never reads it, so those cross pairs are
    # not generated. Ordered condition-major (all full, then all none, then the
    # drops) so --sample-cap stays predictable (cap=2*triggers covers full+none).
    triggers = trigger_evals(data)
    for condition_kind in ("full", "none", "drop"):
        for ev in triggers:
            if condition_kind == "drop":
                target = ev.get("target_section")
                if target not in sections:
                    continue
                condition = f"drop:{target}"
            else:
                condition = condition_kind
            prompt = build_prompt(condition, ev, sections)
            samples.append({
                "index": index,
                "sample_id": f"{index:04d}-{slug(condition)}-{ev['id']}",
                "condition": condition,
                "kind": ev["kind"],
                "gate": ev.get("target_section", "unknown"),
                "eval": ev,
                "sections": sections,
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
            "sections": sections,
            "prompt": prompt,
            "prompt_sha": sha256_text(prompt),
        })
        index += 1

    return samples


def normalize_progressive_level(value: str | None) -> str | None:
    if value is None:
        return None
    level = value.upper()
    if level not in PROGRESSIVE_LEVELS:
        choices = ", ".join(PROGRESSIVE_LEVELS)
        raise ValueError(f"--progressive-level must be one of: {choices}")
    return level


def eval_id(sample: dict[str, Any]) -> str:
    return str(sample["eval"]["id"])


def progressive_default_eval_id(data: dict[str, Any], target_section: str) -> str | None:
    defaults = data.get("progressive_defaults", {})
    if not isinstance(defaults, dict):
        return None
    value = defaults.get(target_section)
    return str(value) if value else None


def order_progressive_evals(
    data: dict[str, Any],
    selected: list[dict[str, Any]],
    level: str,
    target_section: str,
) -> list[dict[str, Any]]:
    default_id = progressive_default_eval_id(data, target_section)
    if level not in {"L1", "L2"} or not default_id:
        return selected
    by_id = {str(ev.get("id")): ev for ev in selected}
    default = by_id.get(default_id)
    if default is None:
        return selected
    return [default, *[ev for ev in selected if str(ev.get("id")) != default_id]]


def progressive_eval_subset(
    data: dict[str, Any],
    level: str,
    target_section: str | None,
    target_eval: str | None,
) -> list[dict[str, Any]]:
    triggers = trigger_evals(data)
    if target_eval:
        selected = [ev for ev in triggers if ev.get("id") == target_eval]
        if not selected:
            raise ValueError(f"--target-eval not found: {target_eval}")
        if target_section and selected[0].get("target_section") != target_section:
            raise ValueError("--target-eval does not belong to --target-section")
        return selected

    if not target_section:
        raise ValueError("--target-section is required for progressive levels L1-L3 unless --target-eval is provided")
    selected = [ev for ev in triggers if ev.get("target_section") == target_section]
    if not selected:
        raise ValueError(f"--target-section has no trigger evals: {target_section}")
    selected = order_progressive_evals(data, selected, level, target_section)

    if level == "L1":
        return selected[:1]
    if level == "L2":
        return selected[:2]
    return selected


def select_progressive_samples(
    samples: list[dict[str, Any]],
    data: dict[str, Any],
    level: str | None,
    target_section: str | None,
    target_eval: str | None,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    normalized = normalize_progressive_level(level)
    if normalized is None:
        return samples, None
    if normalized == "L0":
        return [], {
            "progressive_level": normalized,
            "progressive_stage": PROGRESSIVE_LEVELS[normalized],
            "target_section": target_section,
            "target_eval": target_eval,
            "selected_eval_ids": [],
            "matrix_planned_calls": len(samples),
            "selected_calls": 0,
        }
    if normalized == "L4":
        return samples, {
            "progressive_level": normalized,
            "progressive_stage": PROGRESSIVE_LEVELS[normalized],
            "target_section": target_section,
            "target_eval": target_eval,
            "selected_eval_ids": [str(ev.get("id")) for ev in trigger_evals(data)],
            "matrix_planned_calls": len(samples),
            "selected_calls": len(samples),
        }

    selected_evals = progressive_eval_subset(data, normalized, target_section, target_eval)
    selected_ids = {str(ev["id"]) for ev in selected_evals}
    include_distractors = normalized in {"L2", "L3"}
    selected_samples = [
        sample for sample in samples
        if eval_id(sample) in selected_ids
        or (include_distractors and sample["kind"] == "distractor")
    ]
    return selected_samples, {
        "progressive_level": normalized,
        "progressive_stage": PROGRESSIVE_LEVELS[normalized],
        "target_section": target_section or selected_evals[0].get("target_section"),
        "target_eval": target_eval,
        "selected_eval_ids": [str(ev["id"]) for ev in selected_evals],
        "matrix_planned_calls": len(samples),
        "selected_calls": len(selected_samples),
    }


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
        self.last_metadata: dict[str, Any] = {}

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


def remove_markdown_section(text: str, section: str) -> str:
    lines = text.splitlines()
    result: list[str] = []
    skipping = False
    section_pattern = re.compile(rf"^##?\s+\d*\.?\s*{re.escape(section)}\s*$")
    for line in lines:
        if section_pattern.match(line.strip()):
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            result.append(line)
    return "\n".join(result).rstrip() + "\n"


def strip_section_from_text(text: str, section: str) -> str:
    """Remove a gate section from skill/bootloader markdown robustly.

    Two passes, matching the codex drop-condition contract:
    1. ``remove_markdown_section`` drops a section that owns a ``##`` heading
       (e.g. ``Mantra Gate``, ``Maturity Layer Gate``).
    2. A line-level filter drops any remaining line that names the section,
       which is what catches sections that exist only as table rows
       (``Simplicity First``, ``Surgical Changes``, ``Goal-Driven Execution``,
       ``Think Before Coding``). Without this second pass, ``drop:<section>``
       for those four would be byte-identical to ``full`` and the ablation
       loss would be a meaningless zero.
    """
    text = remove_markdown_section(text, section)
    filtered_lines = [line for line in text.splitlines() if section not in line]
    return "\n".join(filtered_lines).rstrip() + "\n"


def remove_codex_gate_from_workspace(workspace: Path, section: str) -> None:
    for relpath in (
        "AGENTS.md",
        ".agents/skills/tes-engineering-discipline/SKILL.md",
    ):
        path = workspace / relpath
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        path.write_text(strip_section_from_text(text, section), encoding="utf-8")


def load_runtime_skill_text(source: Path = DEFAULT_RUNTIME_SKILL_SOURCE) -> str:
    return source.read_text(encoding="utf-8")


def runtime_skill_system_prompt(condition: str, sections: list[str], skill_text: str) -> str:
    """Derive the condition-controlled system prompt for the runtime-skill backend.

    The full skill is injected as the subagent's system prompt; the ablation is
    in what is *removed* from it, not in a per-section summary:

    - ``none``      -> empty (no discipline injected; the baseline subject)
    - ``full``      -> the entire skill
    - ``drop:<S>``  -> the skill with section ``S`` stripped (robustly, so all
                       six sections are genuinely droppable; see
                       ``strip_section_from_text``)
    - distractor    -> empty (trivial tasks must not carry discipline ceremony)
    """
    if condition in {"none", "distractor"}:
        return ""
    if condition.startswith("drop:"):
        dropped = condition.split(":", 1)[1]
        return strip_section_from_text(skill_text, dropped)
    return skill_text


class RuntimeSkillBackend(Backend):
    """Probe whether the TES skill governs a real agent in execution.

    Unlike ``claude-cli`` (which runs in ``cwd=ROOT`` and lets the project's
    ``.claude/CLAUDE.md`` / ``AGENTS.md`` leak the discipline into every
    condition, including ``none``), this backend isolates the subagent: it runs
    ``claude --print`` in an empty temp directory and injects the skill itself
    as the system prompt, ablated per condition. The cwd carries nothing; the
    only variable across none/full/drop is the injected text. Without that
    isolation the ``none`` condition would absorb the discipline by cwd leak and
    the ablation would be meaningless.
    """

    name = "runtime-skill"

    ISOLATION = "empty-tempdir+append-system-prompt+tools-off"

    def __init__(
        self,
        model: str | None = None,
        claude_bin: str | None = None,
        max_budget_usd: str | None = None,
        timeout_seconds: int = 180,
        fake_bin: str | None = None,
        skill_source: Path = DEFAULT_RUNTIME_SKILL_SOURCE,
    ) -> None:
        super().__init__(model=model or "sonnet")
        self.claude_bin = claude_bin or "claude"
        self.max_budget_usd = max_budget_usd
        self.timeout_seconds = timeout_seconds
        self.skill_source = skill_source
        # fake_bin enables the offline oracle: a deterministic echo stands in for
        # the model so the contract (none empty / full whole / drop != full) can
        # be certified in commit:check without spending a real model call.
        self.fake_bin = fake_bin
        self._skill_text = load_runtime_skill_text(skill_source)
        self._skill_source_sha = sha256_text(self._skill_text)
        self._tempdirs: list[tempfile.TemporaryDirectory[str]] = []

    def _isolated_cwd(self) -> Path:
        tempdir = tempfile.TemporaryDirectory(prefix="tes-runtime-skill-")
        self._tempdirs.append(tempdir)
        workspace = Path(tempdir.name) / "workspace"
        workspace.mkdir(parents=True)
        # An empty workspace with a neutral README — never the project tree, so
        # no .claude/CLAUDE.md or AGENTS.md can leak the discipline by cwd.
        (workspace / "README.md").write_text(
            "# Isolated Runtime Skill Probe\n\nNo project context is mounted here.\n",
            encoding="utf-8",
        )
        return workspace

    def system_prompt_for(self, sample: dict[str, Any], sections: list[str]) -> str:
        return runtime_skill_system_prompt(
            str(sample["condition"]), sections, self._skill_text
        )

    def complete(self, sample: dict[str, Any]) -> str:
        self.last_metadata = {}
        binary = self.fake_bin or self.claude_bin
        if shutil.which(binary) is None and not Path(binary).exists():
            self.last_metadata = {"runtime_skill_error_code": "claude_cli_missing"}
            raise RuntimeError(f"runtime-skill backend binary not found: {binary}")

        sections = list(sample.get("sections") or [])
        system_prompt = self.system_prompt_for(sample, sections)
        workspace = self._isolated_cwd()

        command = [
            binary,
            "--print",
            "--output-format",
            "text",
            "--no-session-persistence",
            "--model",
            self.model,
            "--tools",
            "",
        ]
        if system_prompt:
            command.extend(["--append-system-prompt", system_prompt])
        if self.max_budget_usd:
            command.extend(["--max-budget-usd", self.max_budget_usd])
        # Deliver the task prompt over stdin, not as a positional argument: the
        # CLI's `--tools <tools...>` is variadic, so a positional prompt after
        # `--tools ""` is silently swallowed as a tools value when no other flag
        # separates them (the none condition, which has no --append-system-prompt).
        # stdin is unambiguous and the CLI documents it as a first-class input.

        result = subprocess.run(
            command,
            cwd=workspace,
            input=str(sample["prompt"]),
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        self.last_metadata = {
            "skill_source_sha": self._skill_source_sha,
            "condition_system_prompt_sha": sha256_text(system_prompt),
            "subagent_model": self.model,
            "subagent_isolation": self.ISOLATION,
            "subagent_cwd_is_root": False,
        }
        if result.returncode != 0:
            details = " ".join(
                redact_secrets(part.strip())
                for part in (result.stdout, result.stderr)
                if part.strip()
            )
            self.last_metadata["runtime_skill_error_code"] = "claude_cli_failed"
            raise RuntimeError(
                f"runtime-skill backend failed for {sample['sample_id']}: {details}"
            )
        return redact_secrets(result.stdout.strip())


class CodexCliBackend(Backend):
    name = "codex-cli"

    def __init__(
        self,
        model: str | None = None,
        codex_bin: str | None = None,
        timeout_seconds: int = 180,
    ) -> None:
        super().__init__(model=model or "gpt-5.3-codex")
        self.codex_bin = codex_bin or "codex"
        self.timeout_seconds = timeout_seconds
        self._tempdirs: list[tempfile.TemporaryDirectory[str]] = []
        if self.model not in CODEX_MODEL_ALLOWLIST:
            allowed = ", ".join(CODEX_MODEL_ALLOWLIST)
            raise ValueError(f"codex model not allowed for bounded runs: {self.model}; allowed: {allowed}")

    def _new_tempdir(self) -> Path:
        tempdir = tempfile.TemporaryDirectory(prefix="tes-codex-bench-")
        self._tempdirs.append(tempdir)
        return Path(tempdir.name)

    def _materialized_workspace(self, sample: dict[str, Any]) -> Path:
        root = self._new_tempdir()
        workspace = root / "workspace"
        condition = str(sample["condition"])

        if condition == "none":
            workspace.mkdir(parents=True)
            (workspace / "README.md").write_text(
                "# Context Mesh Baseline Workspace\n\nNo project-specific agent context is installed.\n",
                encoding="utf-8",
            )
            return workspace

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/materialize_adapter.py"),
                "codex",
                "--out",
                str(root / "adapters"),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            self.last_metadata = {
                "codex_backend_error_code": "codex_materialize_failed",
                "codex_stdout_jsonl": redact_secrets(result.stdout),
                "codex_stderr": redact_secrets(result.stderr),
                "codex_stdout_jsonl_sha": sha256_text(result.stdout),
                "codex_stderr_sha": sha256_text(result.stderr),
            }
            raise RuntimeError("codex_materialize_failed")

        workspace = root / "adapters" / "codex"
        if condition.startswith("drop:"):
            remove_codex_gate_from_workspace(workspace, condition.split(":", 1)[1])
        return workspace

    def complete(self, sample: dict[str, Any]) -> str:
        self.last_metadata = {}
        codex_path = shutil.which(self.codex_bin)
        if codex_path is None:
            self.last_metadata = {"codex_backend_error_code": "codex_cli_missing"}
            raise RuntimeError(f"codex_cli_missing: {self.codex_bin}")

        workspace = self._materialized_workspace(sample)
        output_file = workspace.parent / "codex-final-output.txt"
        prompt = str(sample["prompt"])
        command = [
            codex_path,
            "--ask-for-approval",
            "never",
            "exec",
            "--cd",
            str(workspace),
            "--sandbox",
            "read-only",
            "--ignore-user-config",
            "--ignore-rules",
            "--ephemeral",
            "--skip-git-repo-check",
            "--model",
            self.model,
            "--json",
            "--output-last-message",
            str(output_file),
            "-",
        ]

        try:
            result = subprocess.run(
                command,
                input=prompt,
                cwd=workspace,
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            self.last_metadata = {
                "codex_backend_error_code": "codex_timeout",
                "codex_elapsed_timeout_seconds": self.timeout_seconds,
                "codex_stdout_jsonl": redact_secrets(str(stdout)),
                "codex_stderr": redact_secrets(str(stderr)),
                "codex_stdout_jsonl_sha": sha256_text(str(stdout)),
                "codex_stderr_sha": sha256_text(str(stderr)),
                "codex_adapter_workspace_sha": sha256_path_tree(workspace),
                "codex_prompt_contract": sample.get("prompt_contract", ""),
            }
            raise RuntimeError(f"codex_timeout after {self.timeout_seconds}s")

        stdout = redact_secrets(result.stdout)
        stderr = redact_secrets(result.stderr)
        self.last_metadata = {
            "codex_stdout_jsonl": stdout,
            "codex_stderr": stderr,
            "codex_stdout_jsonl_sha": sha256_text(stdout),
            "codex_stderr_sha": sha256_text(stderr),
            "codex_adapter_workspace_sha": sha256_path_tree(workspace),
            "codex_prompt_contract": sample.get("prompt_contract", ""),
            "codex_cli_version": self._version(),
        }

        if result.returncode != 0:
            combined = f"{stdout}\n{stderr}".lower()
            code = "codex_auth_failure" if "auth" in combined or "login" in combined else "codex_nonzero_exit"
            self.last_metadata["codex_backend_error_code"] = code
            raise RuntimeError(f"{code}: exit={result.returncode}: {excerpt(stdout + ' ' + stderr)}")

        if not output_file.exists():
            self.last_metadata["codex_backend_error_code"] = "codex_missing_output"
            raise RuntimeError("codex_missing_output")

        output = redact_secrets(output_file.read_text(encoding="utf-8").strip())
        self.last_metadata["codex_final_output_sha"] = sha256_text(output)
        return output

    def _version(self) -> str:
        result = subprocess.run(
            [self.codex_bin, "--version"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        return result.stdout.strip() or result.stderr.strip()


def runtime_skill_self_test() -> int:
    """Offline contract oracle for the runtime-skill backend (no model call).

    Diamond fixture: this is the test that fails first if the section-drop is not
    robust. It certifies, without spending a model call, that the injected system
    prompt is genuinely ablated per condition:

    - ``none`` injects an empty system prompt (the baseline subject);
    - ``full`` injects the whole skill;
    - for every gate section, ``drop:<section>`` differs from ``full`` (so the
      ablation loss is real, not an artifact of a section that only lives as a
      table row — the defect this catches);
    - the subagent cwd is an isolated temp dir, never ROOT (so the ``none``
      condition cannot absorb the discipline by a project-context cwd leak).
    """
    failures: list[str] = []
    skill_text = load_runtime_skill_text()
    sections = list(SECTION_RULES.keys())
    full_sha = sha256_text(skill_text)

    none_prompt = runtime_skill_system_prompt("none", sections, skill_text)
    if none_prompt != "":
        failures.append("none condition must inject an empty system prompt")

    full_prompt = runtime_skill_system_prompt("full", sections, skill_text)
    if sha256_text(full_prompt) != full_sha:
        failures.append("full condition must inject the whole skill text")

    distractor_prompt = runtime_skill_system_prompt("distractor", sections, skill_text)
    if distractor_prompt != "":
        failures.append("distractor condition must inject an empty system prompt")

    for section in sections:
        drop_prompt = runtime_skill_system_prompt(f"drop:{section}", sections, skill_text)
        if sha256_text(drop_prompt) == full_sha:
            failures.append(
                f"drop:{section} is byte-identical to full — section not actually removed"
            )
        if section in drop_prompt:
            failures.append(
                f"drop:{section} still names the section after removal"
            )

    backend = RuntimeSkillBackend(fake_bin="true")
    workspace = backend._isolated_cwd()
    if workspace == ROOT or ROOT in workspace.parents:
        failures.append("isolated cwd must not be the project ROOT (cwd-leak guard)")
    if (workspace / ".claude").exists() or (workspace / "AGENTS.md").exists():
        failures.append("isolated cwd must not contain project context files")

    with tempfile.TemporaryDirectory(prefix="tes-progress-log-self-test-") as tempdir:
        progress_run_dir = Path(tempdir) / "run"
        progress = ProgressLogger(progress_run_dir)
        progress.emit("run_started", run_id="self-test", planned_calls=1)
        progress.emit("sample_finished", run_id="self-test", sample_id="0001-self-test", passed=True)
        events = (progress_run_dir / "progress" / "events.ndjson").read_text(encoding="utf-8").splitlines()
        latest = load_json(progress_run_dir / "progress" / "latest.json")
        if len(events) != 2:
            failures.append("progress log must append one NDJSON event per emit")
        if latest.get("event") != "sample_finished":
            failures.append("progress latest.json must mirror the most recent event")

    table_rejection_grade = grade_output(
        {"expected": [], "expected_any": [], "forbidden": ["abstract factory"]},
        "| Artifact | Decision |\n|---|---|\n| abstract factory | **Não** |\n",
    )
    if not table_rejection_grade["pass"]:
        failures.append("forbidden table rows marked Não must be treated as rejected, not endorsed")
    table_reason_rejection_grade = grade_output(
        {"expected": [], "expected_any": [], "forbidden": ["abstract factory"]},
        "| Artifact | Por quê não |\n|---|---|\n| abstract factory | Uma fábrica com um único produto é ruído |\n",
    )
    if not table_reason_rejection_grade["pass"]:
        failures.append("forbidden table rows under Por quê não must be treated as rejected")

    data = load_dataset(DATASET)
    samples = build_samples(data)
    try:
        level_0, meta_0 = select_progressive_samples(samples, data, "L0", None, None)
        level_1, meta_1 = select_progressive_samples(samples, data, "L1", "Maturity Layer Gate", None)
        level_2, meta_2 = select_progressive_samples(samples, data, "L2", "Maturity Layer Gate", None)
        level_3, meta_3 = select_progressive_samples(samples, data, "L3", "Maturity Layer Gate", None)
        level_4, meta_4 = select_progressive_samples(samples, data, "L4", None, None)
    except ValueError as exc:
        failures.append(f"progressive selector raised unexpectedly: {exc}")
    else:
        if level_0 or meta_0 is None or meta_0["selected_calls"] != 0:
            failures.append("progressive L0 must select no model samples")
        if len(level_1) != 3 or meta_1 is None:
            failures.append("progressive L1 must select one eval triplet")
        elif meta_1["selected_eval_ids"] != ["E2d-maturity-platform-risk"]:
            failures.append("progressive L1 must use the dataset-declared Maturity Layer Gate smoke eval")
        if len(level_2) != 8 or meta_2 is None:
            failures.append("progressive L2 must select two eval triplets plus two distractors")
        elif meta_2["selected_eval_ids"][0] != "E2d-maturity-platform-risk":
            failures.append("progressive L2 must keep the dataset-declared smoke eval first")
        if len(level_3) != 14 or meta_3 is None:
            failures.append("progressive L3 must select all Maturity Layer Gate evals plus two distractors")
        if len(level_4) != len(samples) or meta_4 is None:
            failures.append("progressive L4 must select the full matrix")
        if any(sample["kind"] == "distractor" for sample in level_1):
            failures.append("progressive L1 must not include distractors")
        if sum(1 for sample in level_2 if sample["kind"] == "distractor") != 2:
            failures.append("progressive L2 must include distractors")

    result = {
        "skill_source_sha": full_sha,
        "sections": sections,
        "isolation": RuntimeSkillBackend.ISOLATION,
        "progressive_levels": PROGRESSIVE_LEVELS,
        "certification_class": RUNTIME_SKILL_CERTIFICATION_CLASS,
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }
    print(json.dumps(result, indent=2))
    print(f"[runtime-skill] {result['status']}")
    return 0 if not failures else 1


def make_backend(
    name: str,
    model: str | None,
    claude_bin: str | None = None,
    codex_bin: str | None = None,
    max_budget_usd: str | None = None,
    timeout_seconds: int = 180,
    fake_subagent_bin: str | None = None,
    runtime_skill_source: Path = DEFAULT_RUNTIME_SKILL_SOURCE,
) -> Backend:
    backends: dict[str, type[Backend]] = {
        "claude-cli": ClaudeCliBackend,
        "codex-cli": CodexCliBackend,
        "echo": EchoBackend,
        "fixture": FixtureBackend,
        "runtime-skill": RuntimeSkillBackend,
    }
    if name not in backends:
        choices = ", ".join(sorted(backends))
        raise ValueError(f"unknown backend {name!r}; choose one of: {choices}")
    if name == "claude-cli":
        return ClaudeCliBackend(
            model=model,
            claude_bin=claude_bin,
            max_budget_usd=max_budget_usd,
            timeout_seconds=timeout_seconds,
        )
    if name == "codex-cli":
        return CodexCliBackend(
            model=model,
            codex_bin=codex_bin,
            timeout_seconds=timeout_seconds,
        )
    if name == "runtime-skill":
        return RuntimeSkillBackend(
            model=model,
            claude_bin=claude_bin,
            max_budget_usd=max_budget_usd,
            timeout_seconds=timeout_seconds,
            fake_bin=fake_subagent_bin,
            skill_source=runtime_skill_source,
        )
    return backends[name](
        model=model,
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
    forbidden = []
    for term in ev.get("forbidden", []):
        text = str(term)
        mentions = forbidden_term_mentions(output, text)
        forbidden.append({
            "text": text,
            "mentions": mentions,
            "present": any(not mention["negated"] for mention in mentions),
        })
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
    progress_rows = ""
    progress_files = ""
    if manifest.get("progress_log_contract"):
        progress_rows = (
            f"| Progress log | `{manifest.get('progress_events', 'progress/events.ndjson')}` |\n"
            f"| Progress latest | `{manifest.get('progress_latest', 'progress/latest.json')}` |\n"
        )
        progress_files = "- `progress/events.ndjson`\n- `progress/latest.json`\n"
    progressive_rows = ""
    if manifest.get("progressive_level"):
        progressive_rows = (
            f"| Progressive level | `{manifest['progressive_level']}` |\n"
            f"| Progressive stage | `{manifest.get('progressive_stage', '')}` |\n"
            f"| Target section | `{manifest.get('target_section', '')}` |\n"
            f"| Target eval | `{manifest.get('target_eval', '')}` |\n"
            f"| Matrix planned calls | `{manifest.get('matrix_planned_calls', manifest['planned_calls'])}` |\n"
        )

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
| Retention status | `{manifest.get('retention_status', 'retained')}` |
| Planned calls | `{manifest['planned_calls']}` |
| Executed calls | `{summary['executed_calls']}` |
| Pass rate | `{summary['pass_rate']:.2%}` |
{progress_rows}
{progressive_rows}

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
{progress_files}
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


def assert_evidence_paths_available(run_dir: Path, filenames: tuple[str, ...]) -> None:
    for filename in filenames:
        path = run_dir / filename
        if path.exists():
            raise FileExistsError(f"evidence file already exists: {path}")


def write_evidence(
    run_dir: Path,
    manifest: dict[str, Any],
    records: list[dict[str, Any]],
    update_index: bool,
) -> dict[str, Path]:
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = run_dir / "manifest.json"
    raw_path = run_dir / "raw.ndjson"
    summary_path = run_dir / "summary.json"
    report_path = run_dir / "REPORT.md"
    graders_path = run_dir / "graders-sha.json"
    assert_evidence_paths_available(
        run_dir,
        ("manifest.json", "raw.ndjson", "summary.json", "REPORT.md", "graders-sha.json"),
    )

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
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = run_dir / "manifest.json"
    raw_path = run_dir / "raw.ndjson"
    graders_path = run_dir / "graders-sha.json"
    assert_evidence_paths_available(run_dir, ("manifest.json", "raw.ndjson", "graders-sha.json"))

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

    expected_samples = prepare_samples_for_backend(samples, str(first.get("backend", "")))
    expected_ids = {sample["sample_id"] for sample in expected_samples}
    seen_ids: dict[str, int] = defaultdict(int)
    sample_by_id = {sample["sample_id"]: sample for sample in expected_samples}
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
        "retention_status": "retained",
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

    run_dir = resolve_out_root(args.out_root) / run_id
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


def execute_samples(
    samples: list[dict[str, Any]],
    backend: Backend,
    manifest: dict[str, Any],
    progress: ProgressLogger | None = None,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    total = len(samples)
    for position, sample in enumerate(samples, start=1):
        backend_error = ""
        started_at = time.monotonic()
        if progress:
            progress.emit(
                "sample_started",
                run_id=manifest["run_id"],
                sample_id=sample["sample_id"],
                eval_id=sample["eval"]["id"],
                condition=sample["condition"],
                gate=sample["gate"],
                sample_position=position,
                total_calls=total,
            )
        try:
            output = redact_secrets(backend.complete(sample))
        except Exception as exc:
            backend_error = redact_secrets(str(exc))
            output = f"BACKEND_ERROR: {backend_error}"
        backend_metadata = {
            key: redact_secrets(value) if isinstance(value, str) else value
            for key, value in backend.last_metadata.items()
        }
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
            "duration_ms": round((time.monotonic() - started_at) * 1000),
        }
        record.update(backend_metadata)
        leak_reasons = distractor_leak_reasons(record)
        record["distractor_leak"] = bool(leak_reasons)
        record["distractor_leak_reasons"] = leak_reasons
        if "shard_id" in manifest:
            record["source_shard_id"] = manifest["shard_id"]
        records.append(record)
        if progress:
            progress.emit(
                "sample_finished",
                run_id=manifest["run_id"],
                sample_id=record["sample_id"],
                eval_id=record["eval_id"],
                condition=record["condition"],
                gate=record["gate"],
                sample_position=position,
                total_calls=total,
                passed=record["pass"],
                backend_error=bool(backend_error),
                duration_ms=record["duration_ms"],
                output_sha=record["output_sha"],
                reasons=record["reasons"],
                distractor_leak=record["distractor_leak"],
                distractor_leak_reasons=record["distractor_leak_reasons"],
                excerpt=record["excerpt"],
            )
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
    samples = prepare_samples_for_backend(build_samples(data), args.backend)
    if len(samples) != plan["planned_calls"]:
        print("[context-mesh-run] FAIL")
        print(f"- matrix diverged from plan: samples={len(samples)} planned_calls={plan['planned_calls']}")
        return 1

    if args.progressive_level and (args.shard_index is not None or args.shard_count is not None):
        print("[context-mesh-run] FAIL")
        print("- progressive mode cannot be combined with shard mode")
        return 1
    if args.progressive_level and args.sample_cap is not None:
        print("[context-mesh-run] FAIL")
        print("- progressive mode cannot be combined with --sample-cap")
        return 1

    try:
        progressive_samples, progressive_meta = select_progressive_samples(
            samples,
            data,
            args.progressive_level,
            args.target_section,
            args.target_eval,
        )
    except ValueError as exc:
        print("[context-mesh-run] FAIL")
        print(f"- {exc}")
        return 1

    if progressive_meta and progressive_meta["progressive_level"] == "L0":
        print("[context-mesh-progressive] PASS")
        print(json.dumps({
            **plan,
            **progressive_meta,
            "progressive_levels": PROGRESSIVE_LEVELS,
            "runtime_skill_self_test": "run `python3 scripts/context_mesh_run.py --self-test` for the offline runtime oracle",
            "plan_parity": True,
        }, indent=2))
        return 0

    try:
        selected_samples = select_shard(progressive_samples, args.shard_index, args.shard_count)
    except ValueError as exc:
        print("[context-mesh-run] FAIL")
        print(f"- {exc}")
        return 1
    if args.sample_cap is not None:
        if args.sample_cap < 1:
            print("[context-mesh-run] FAIL")
            print("- --sample-cap must be at least 1")
            return 1
        selected_samples = selected_samples[:args.sample_cap]
    is_shard = args.shard_index is not None
    out_root = resolve_out_root(args.out_root)

    if args.dry_run:
        dry_run_id = args.run_id or "<auto-run-id>"
        print("[context-mesh-run] DRY-RUN")
        print(json.dumps({
            **plan,
            "matrix_calls": len(samples),
            "selected_calls": len(selected_samples),
            "progressive": progressive_meta,
            "shard_index": args.shard_index,
            "shard_count": args.shard_count,
            "out_root": str(out_root),
            "legacy_out_root": str(LEGACY_OUT_ROOT),
            "evidence_path_schema": "tes-evidence-temporal@1",
            "progress_log_contract": PROGRESS_LOG_CONTRACT,
            "progress_dir": str(out_root / dry_run_id / "progress"),
            "plan_parity": True,
        }, indent=2))
        return 0

    if is_shard and not args.run_id:
        print("[context-mesh-run] FAIL")
        print("- shard mode requires --run-id")
        return 1
    if args.backend == "codex-cli" and args.sample_cap is None and not args.allow_full_codex_run:
        bounded_progressive = bool(progressive_meta and progressive_meta["progressive_level"] in {"L1", "L2", "L3"})
        if not bounded_progressive:
            print("[context-mesh-run] FAIL")
            print("- codex-cli requires --sample-cap for bounded smoke runs, --progressive-level L1/L2/L3, or --allow-full-codex-run for explicit full matrix execution")
            return 1
    if (
        args.backend == "runtime-skill"
        and args.fake_subagent_bin is None
        and args.sample_cap is None
        and not args.allow_full_codex_run
    ):
        bounded_progressive = bool(progressive_meta and progressive_meta["progressive_level"] in {"L1", "L2", "L3"})
        if not bounded_progressive:
            print("[context-mesh-run] FAIL")
            print("- runtime-skill requires --sample-cap for bounded model runs, --progressive-level L1/L2/L3, --allow-full-codex-run for the full matrix, or --fake-subagent-bin for the offline oracle")
            return 1

    digest = dataset_sha(args.dataset)
    run_id = args.run_id or build_run_id(args.backend, digest)
    run_dir = out_root / run_id
    backend = make_backend(
        args.backend,
        args.model,
        claude_bin=args.claude_bin,
        codex_bin=args.codex_bin,
        max_budget_usd=args.max_budget_usd,
        timeout_seconds=args.timeout_seconds,
        fake_subagent_bin=args.fake_subagent_bin,
        runtime_skill_source=args.runtime_skill_source,
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
        "planned_calls": len(selected_samples) if progressive_meta else plan["planned_calls"],
        "matrix_planned_calls": plan["planned_calls"],
        "retention_status": "retained",
        "progress_log_contract": PROGRESS_LOG_CONTRACT,
        "progress_dir": "progress",
        "progress_events": "progress/events.ndjson",
        "progress_latest": "progress/latest.json",
    }
    if args.backend == "runtime-skill":
        try:
            manifest["runtime_skill_source"] = str(args.runtime_skill_source.relative_to(ROOT))
        except ValueError:
            manifest["runtime_skill_source"] = str(args.runtime_skill_source)
    if progressive_meta:
        manifest.update(progressive_meta)
    if args.sample_cap is not None:
        manifest["sample_cap"] = args.sample_cap
    if args.backend == "codex-cli":
        manifest["gate_head"] = "e67bf9808c7cc55accc151a1c91ded0215d199c7"
        manifest["run_head"] = head
        manifest["retention_head"] = "pending"
        manifest["backend_stage"] = "codex-backend-implementation-stage-1"
    if is_shard:
        manifest["shard_id"] = f"shard-{args.shard_index:02d}-of-{args.shard_count:02d}"
        manifest["shard_index"] = args.shard_index
        manifest["shard_count"] = args.shard_count
        manifest["shard_calls"] = len(selected_samples)

    try:
        evidence_filenames = ("manifest.json", "raw.ndjson", "graders-sha.json")
        if not is_shard:
            evidence_filenames = (
                "manifest.json",
                "raw.ndjson",
                "summary.json",
                "REPORT.md",
                "graders-sha.json",
            )
        assert_evidence_paths_available(run_dir, evidence_filenames)
        progress = ProgressLogger(run_dir)
    except FileExistsError as exc:
        print("[context-mesh-run] FAIL")
        print(f"- {exc}")
        return 1
    progress.emit(
        "run_started",
        run_id=run_id,
        backend=backend.name,
        model=backend.model,
        planned_calls=manifest["planned_calls"],
        matrix_planned_calls=manifest.get("matrix_planned_calls"),
        progressive_level=manifest.get("progressive_level"),
        target_section=manifest.get("target_section"),
        shard_id=manifest.get("shard_id"),
        progress_log_contract=PROGRESS_LOG_CONTRACT,
    )

    records = execute_samples(selected_samples, backend, manifest, progress=progress)

    if is_shard:
        try:
            paths = write_shard_evidence(run_dir, manifest, records)
        except FileExistsError as exc:
            progress.emit("run_failed", run_id=run_id, reason=str(exc))
            print("[context-mesh-shard] FAIL")
            print(f"- {exc}")
            return 1
        progress.emit(
            "shard_finished",
            run_id=run_id,
            shard_id=manifest["shard_id"],
            executed_calls=len(records),
            certification_status="SHARD-NOT-CERTIFIED",
        )
        print("[context-mesh-shard] PASS")
        print(json.dumps({
            "run_id": run_id,
            "planned_calls": plan["planned_calls"],
            "shard_calls": len(records),
            "shard_index": args.shard_index,
            "shard_count": args.shard_count,
            "manifest": str(paths["manifest"]),
            "raw": str(paths["raw"]),
            "progress": str(run_dir / "progress" / "events.ndjson"),
            "graders": str(paths["graders"]),
            "certification_class": certification_class,
            "certification_status": "SHARD-NOT-CERTIFIED",
        }, indent=2))
        return 0

    update_index = not args.no_tds_index
    try:
        paths = write_evidence(run_dir, manifest, records, update_index=update_index)
    except FileExistsError as exc:
        progress.emit("run_failed", run_id=run_id, reason=str(exc))
        print("[context-mesh-run] FAIL")
        print(f"- {exc}")
        return 1
    summary = summarize(records, manifest)
    progress.emit(
        "run_finished",
        run_id=run_id,
        executed_calls=summary["executed_calls"],
        passed=summary["passed"],
        failed=summary["failed"],
        pass_rate=summary["pass_rate"],
        certification_class=summary["certification_class"],
        certification_status=summary["certification"]["status"],
        report=str(paths["report"]),
    )

    print("[context-mesh-run] PASS")
    print(json.dumps({
        "run_id": run_id,
        "planned_calls": manifest["planned_calls"],
        "matrix_planned_calls": manifest.get("matrix_planned_calls"),
        "progressive": progressive_meta,
        "executed_calls": summary["executed_calls"],
        "passed": summary["passed"],
        "failed": summary["failed"],
        "pass_rate": summary["pass_rate"],
        "manifest": str(paths["manifest"]),
        "raw": str(paths["raw"]),
        "summary": str(paths["summary"]),
        "report": str(paths["report"]),
        "progress": str(run_dir / "progress" / "events.ndjson"),
        "graders": str(paths["graders"]),
        "certification_class": summary["certification_class"],
        "certification_status": summary["certification"]["status"],
    }, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--backend", default="fixture", choices=("fixture", "echo", "claude-cli", "codex-cli", "runtime-skill"))
    parser.add_argument("--model")
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--max-budget-usd")
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--run-id")
    parser.add_argument(
        "--out-root",
        type=Path,
        help=(
            "Evidence output root. Defaults to "
            "docs/evidence/reports/YYYY/MM/DD/context-mesh. "
            "Use docs/evidence/reports/context-mesh to write the legacy layout."
        ),
    )
    parser.add_argument("--shard-count", type=int)
    parser.add_argument("--shard-index", type=int)
    parser.add_argument("--sample-cap", type=int)
    parser.add_argument(
        "--progressive-level",
        choices=tuple(PROGRESSIVE_LEVELS),
        help="Run a progressive benchmark level: L0 static, L1 probe, L2 smoke, L3 gate shard, or L4 full matrix.",
    )
    parser.add_argument(
        "--target-section",
        help="Gate section for progressive levels L1-L3, such as 'Maturity Layer Gate'.",
    )
    parser.add_argument(
        "--target-eval",
        help="Specific eval id for progressive L1/L2/L3 selection; overrides the default first eval for L1.",
    )
    parser.add_argument("--allow-full-codex-run", action="store_true")
    parser.add_argument("--merge-shards", type=Path, nargs="+")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-tds-index", action="store_true")
    parser.add_argument(
        "--fake-subagent-bin",
        help="runtime-skill only: a deterministic echo binary that stands in for the model, for the offline oracle (no model call).",
    )
    parser.add_argument(
        "--runtime-skill-source",
        type=Path,
        default=DEFAULT_RUNTIME_SKILL_SOURCE,
        help="runtime-skill only: SKILL.md source to inject as the isolated subagent system prompt.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the offline runtime-skill contract oracle (no model call) and exit.",
    )
    args = parser.parse_args()

    if args.self_test:
        return runtime_skill_self_test()
    if args.merge_shards:
        return merge_shards(args)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
