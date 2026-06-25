#!/usr/bin/env python3
"""Deterministic quality oracle for TES Cortex curation and proposal UX."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

import cortex


ACTIONABLE_KEYS = {"category", "action", "rationale", "next_step"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def markdown_snapshot(target: Path) -> dict[str, str]:
    root = cortex.cortex_path(target)
    if not root.exists():
        return {}
    return {
        cortex.rel(path, target): sha(path)
        for path in sorted(root.rglob("*.md"))
    }


def write_cell(target: Path, name: str, claim: str, evidence: str, links: str = "") -> None:
    path = cortex.cortex_path(target) / "cells" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (
        f"# {Path(name).stem.replace('-', ' ').title()}\n\n"
        "## Claim\n\n"
        f"{claim.strip()}\n\n"
        "## Evidence\n\n"
        f"{evidence.strip()}\n"
    )
    if links:
        text += "\n## Links\n\n" + links.strip() + "\n"
    path.write_text(text, encoding="utf-8")


def append_catalog(target: Path) -> None:
    cells = cortex.cortex_path(target) / "cells"
    map_path = cortex.cortex_path(target) / "MAP.md"
    links_path = cortex.cortex_path(target) / "LINKS.md"
    for path in sorted(cells.rglob("*.md")):
        ref = cortex.cell_ref(path, cells)
        cortex.append_unique_line(map_path, f"| [[{ref}]] | Cortex quality oracle fixture | |")
        cortex.append_unique_line(links_path, f"- [[{ref}]] -> `sources/quality-source.md`")


def make_dirty_fixture(target: Path) -> None:
    cortex.init(target)
    source = cortex.cortex_path(target) / "sources" / "quality-source.md"
    source.write_text(
        "# Quality Source\n\n"
        "This source grounds duplicate, split, link, tension, evidence-gap, and reject fixtures.\n",
        encoding="utf-8",
    )
    evidence = "- `sources/quality-source.md` records this quality fixture."
    write_cell(
        target,
        "markdown-memory.md",
        "Cortex memory lives in durable Markdown files with explicit source evidence.",
        evidence,
    )
    write_cell(
        target,
        "compiled-knowledge.md",
        "Cortex keeps durable knowledge inside versioned filesystem artifacts with proof.",
        evidence,
    )
    write_cell(
        target,
        "agent-routing.md",
        "Agents route durable memory through Cortex cells and cite source evidence before applying.",
        evidence,
    )
    write_cell(
        target,
        "memory-routing.md",
        "Cortex memory routing should connect related cells with evidence before future work.",
        evidence,
    )
    write_cell(
        target,
        "retain-sources.md",
        "Cortex must preserve source evidence for audit and keep versioned memory.",
        evidence,
    )
    write_cell(
        target,
        "delete-sources.md",
        "Cortex should automatically delete source evidence and overwrite memory after each run.",
        evidence,
    )
    write_cell(
        target,
        "assumption-only.md",
        "Cortex can promote a durable operating rule from chat context alone.",
        "- Assumption: first ungrounded assertion.\n- Assumption: second ungrounded assertion.",
    )
    write_cell(
        target,
        "scratch-todo.md",
        "Temporary scratch todo notes should be filed as Cortex memory.",
        evidence,
    )
    swollen_claim = "\n".join(
        f"- Cortex curation topic {number} should be treated as a separate concern."
        for number in range(30)
    )
    write_cell(target, "swollen-cell.md", swollen_claim, evidence)
    append_catalog(target)


def make_healthy_fixture(target: Path) -> None:
    cortex.init(target)
    source = cortex.cortex_path(target) / "sources" / "quality-source.md"
    source.write_text(
        "# Quality Source\n\n"
        "Healthy Cortex memory contains distinct cells with explicit relationships.\n",
        encoding="utf-8",
    )
    evidence = "- `sources/quality-source.md` records the healthy fixture."
    write_cell(
        target,
        "adapter-routing.md",
        "Adapter bootloaders stay thin and route agents toward governed project context.",
        evidence,
        "- [[gate-closure]]",
    )
    write_cell(
        target,
        "gate-closure.md",
        "Project cuts close only after the smallest relevant oracle reports a passing result.",
        evidence,
        "- [[adapter-routing]]",
    )
    append_catalog(target)


def candidate_missing(candidate: dict[str, Any]) -> list[str]:
    missing = sorted(ACTIONABLE_KEYS - set(candidate))
    if not str(candidate.get("rationale", "")).strip():
        missing.append("rationale:text")
    if not str(candidate.get("next_step", "")).strip():
        missing.append("next_step:text")
    return missing


def assert_actionable(
    result: dict[str, Any],
    category: str,
    failures: list[str],
    required: bool = True,
) -> None:
    candidates = result.get(category, [])
    if required and not candidates:
        failures.append(f"{category} missing")
        return
    for index, raw in enumerate(candidates):
        if not isinstance(raw, dict):
            failures.append(f"{category}[{index}] is not an object")
            continue
        missing = candidate_missing(raw)
        if missing:
            failures.append(f"{category}[{index}] missing actionable fields: {', '.join(missing)}")


def proposal_missing(proposal: dict[str, Any] | None) -> list[str]:
    if not proposal:
        return ["proposal"]
    required = {"cell", "claim_needed", "evidence", "apply_command", "route", "evidence_status"}
    missing = sorted(required - set(proposal))
    if "--yes" not in str(proposal.get("apply_command", "")):
        missing.append("apply_command:--yes")
    return missing


def run_oracle() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-cortex-quality-") as tempdir:
        root = Path(tempdir)
        dirty = root / "dirty"
        healthy = root / "healthy"
        make_dirty_fixture(dirty)
        make_healthy_fixture(healthy)

        before_dirty = markdown_snapshot(dirty)
        dirty_result = cortex.curate_plan(dirty, "lexical", write_index=True)
        after_dirty = markdown_snapshot(dirty)
        if before_dirty != after_dirty:
            failures.append("dirty curate-plan mutated Cortex Markdown memory")
        if dirty_result.get("writes") != []:
            failures.append("dirty curate-plan reported memory writes")
        if dirty_result.get("derived_writes") != [" .tes/cortex/semantic.sqlite".strip()]:
            failures.append(f"dirty curate-plan derived writes mismatch: {dirty_result.get('derived_writes')}")
        if not cortex.semantic_db_path(dirty).exists():
            failures.append("dirty curate-plan did not create the derived semantic index")
        if dirty_result.get("status") != "FAIL":
            failures.append(f"dirty curate-plan should FAIL, got {dirty_result.get('status')}")
        for category in (
            "merge_candidates",
            "split_candidates",
            "link_candidates",
            "tension_candidates",
            "evidence_gaps",
            "reject_candidates",
        ):
            assert_actionable(dirty_result, category, failures)
        assert_actionable(dirty_result, "redundancy_warnings", failures, required=False)

        before_healthy = markdown_snapshot(healthy)
        healthy_result = cortex.curate_plan(healthy, "lexical", write_index=False)
        after_healthy = markdown_snapshot(healthy)
        if before_healthy != after_healthy:
            failures.append("healthy curate-plan mutated Cortex Markdown memory")
        if healthy_result.get("writes") != [] or healthy_result.get("derived_writes") != []:
            failures.append("healthy no-write curate-plan reported writes")
        if healthy_result.get("status") != "PASS":
            failures.append(f"healthy curate-plan should PASS, got {healthy_result.get('status')}")
        scoped_result = cortex.attach_runtime_scope(
            {"status": "PASS", "writes": []},
            healthy,
            "curate-plan",
            None,
            [],
        )
        if scoped_result.get("scope_status") != "PASS" or not isinstance(scoped_result.get("scope"), dict):
            failures.append("Cortex runtime results must carry normalized scope")
        unsafe_scope = cortex.attach_runtime_scope(
            {"status": "PASS", "writes": []},
            healthy,
            "learn",
            Path("/absolute/unsafe/source.md"),
            [],
        )
        if unsafe_scope.get("status") != "FAIL" or unsafe_scope.get("scope_status") != "FAIL":
            failures.append("Cortex runtime scope must reject unsafe source references")

        weak_learn = cortex.learn(healthy, "important context")
        if weak_learn.get("status") not in {"NEEDS_EVIDENCE", "FAIL"}:
            failures.append(f"weak learn should require evidence, got {weak_learn.get('status')}")
        if weak_learn.get("writes") != []:
            failures.append("weak learn wrote memory")
        if weak_learn.get("proposal") is not None:
            failures.append("weak learn produced a proposal")

        valid_learn = cortex.learn(healthy, "capture adapter routing boundary", Path("docs/agents/cortex/sources/quality-source.md"))
        missing = proposal_missing(valid_learn.get("proposal"))  # type: ignore[arg-type]
        if valid_learn.get("status") != "PASS" or valid_learn.get("writes") != [] or missing:
            failures.append(f"valid learn proposal is not actionable: status={valid_learn.get('status')} missing={missing}")

        outside_learn = cortex.learn(healthy, "capture outside source", Path("README.md"))
        if outside_learn.get("status") != "FAIL":
            failures.append("learn accepted source outside Cortex sources")

        weak_reflect = cortex.reflect(healthy, "important context")
        if weak_reflect.get("capture_needed"):
            failures.append("weak reflect query should not request capture")
        if weak_reflect.get("proposal") is not None:
            failures.append("weak reflect produced a proposal")
        if not weak_reflect.get("no_capture_reason"):
            failures.append("weak reflect omitted no_capture_reason")

        quiet_reflect = cortex.reflect(healthy, None)
        if quiet_reflect.get("capture_needed"):
            failures.append("quiet reflect should not request capture")
        if not quiet_reflect.get("no_capture_reason"):
            failures.append("quiet reflect omitted no_capture_reason")

        specific_reflect = cortex.reflect(healthy, "adapter routing and gate closure produced a reusable Cortex lesson")
        missing = proposal_missing(specific_reflect.get("proposal"))  # type: ignore[arg-type]
        if specific_reflect.get("status") != "PASS" or specific_reflect.get("writes") != [] or missing:
            failures.append(f"specific reflect proposal is not actionable: missing={missing}")

        unauthorized = cortex.apply_cell(
            healthy,
            "unauthorized-quality",
            "Unauthorized quality writes must not happen.",
            ["sources/quality-source.md"],
            None,
            [],
            authorized=False,
            update_existing=False,
        )
        if unauthorized.get("status") != "NEEDS_AUTH" or unauthorized.get("writes") != []:
            failures.append("unauthorized apply did not preserve no-write contract")

        missing_apply = cortex.apply_cell(
            healthy,
            "missing-quality",
            "Missing source evidence must not be promoted into Cortex memory.",
            ["sources/missing-quality-source.md"],
            None,
            [],
            authorized=True,
            update_existing=False,
        )
        if missing_apply.get("status") != "FAIL" or missing_apply.get("writes") != []:
            failures.append("missing-evidence apply did not fail without writes")
        if not any("evidence file missing" in failure for failure in missing_apply.get("failures", [])):
            failures.append("missing-evidence apply omitted missing evidence reason")
        if (cortex.cortex_path(healthy) / "cells" / "missing-quality.md").exists():
            failures.append("missing-evidence apply created a cell")

        missing_cell = cortex.cortex_path(healthy) / "cells" / "missing-quality-audit.md"
        missing_cell.write_text(
            "# Missing Quality Audit\n\n"
            "## Claim\n\n"
            "Audit must reject cells that cite missing real evidence files.\n\n"
            "## Evidence\n\n"
            "- `sources/missing-quality-source.md`\n",
            encoding="utf-8",
        )
        missing_audit = cortex.audit(healthy)
        if missing_audit.get("status") != "FAIL":
            failures.append("missing-evidence audit did not fail")
        if not any("evidence file missing" in failure for failure in missing_audit.get("failures", [])):
            failures.append("missing-evidence audit omitted missing evidence reason")
        missing_cell.unlink()

        xenova_probe = cortex.curate_plan(healthy, "xenova", write_index=False)
        xenova_status = xenova_probe.get("status")
        xenova_backend_ok = xenova_probe.get("backend_status") == "CERTIFIED"
        xenova_probe_ok = xenova_status in {"PASS", "BLOCKED"} or (
            xenova_status == "FAIL" and xenova_backend_ok
        )
        if not xenova_probe_ok:
            failures.append(f"xenova probe returned ambiguous status: {xenova_status}")
        if xenova_status == "PASS" and xenova_probe.get("backend_status") != "CERTIFIED":
            failures.append("xenova PASS did not report CERTIFIED backend status")
        if xenova_status == "BLOCKED" and not xenova_probe.get("failures"):
            failures.append("xenova BLOCKED omitted exact reason")

        return {
            "status": "FAIL" if failures else "PASS",
            "failures": failures,
            "dirty_status": dirty_result.get("status"),
            "healthy_status": healthy_result.get("status"),
            "weak_learn_status": weak_learn.get("status"),
            "weak_reflect_capture_needed": weak_reflect.get("capture_needed"),
            "xenova_status": xenova_probe.get("status"),
            "xenova_backend_status": xenova_probe.get("backend_status"),
        }


def self_test() -> int:
    result = run_oracle()
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        print("[cortex-quality-oracle] FAIL")
        return 1
    print("[cortex-quality-oracle] PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    parser.error("--self-test is required")


if __name__ == "__main__":
    sys.exit(main())
