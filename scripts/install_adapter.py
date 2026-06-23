#!/usr/bin/env python3
"""Install materialized adapter files into a target project safely."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import context_distill_coverage_oracle as context_distill
import field_reports
import materialize_adapter
import root_context
import tes_bundle


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.188"
RETROFIT_DIR = ".tes/retrofit"
CANONICAL_SOURCE_REL = "docs/agents/PROJECT-CONTEXT.md"


def route_inherited_context_roots(
    overwrite_items: list[dict[str, str]],
    target_root: Path,
    dry_run: bool,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """P2 SPEC-007: turn the default for context_governance roots in conflict.

    Instead of whole-file overwrite (which loses human context to a .bak) or
    whole-file preserve (which leaves the TES core stale), inherit the human
    context into the canonical source and write the thin rendered root. Only
    Claude (`CLAUDE.md`) and Codex (`AGENTS.md`) are routed; other
    context_governance paths (Cursor) keep the legacy copy path.

    Returns (routed_actions, remaining_overwrite_items): the routed items are
    removed from the blind-copy list so they are not double-written.
    """
    routed_actions: list[dict[str, str]] = []
    remaining: list[dict[str, str]] = []
    adapter_for_root = {"CLAUDE.md": "claude", "AGENTS.md": "codex"}
    source_path = target_root / CANONICAL_SOURCE_REL

    for item in overwrite_items:
        relpath = item.get("relpath", "")
        adapter = adapter_for_root.get(relpath)
        if item.get("layer") != "context_governance" or adapter is None:
            remaining.append(item)
            continue

        target = Path(item["target"])
        try:
            root_text = target.read_text(encoding="utf-8")
            core_text = Path(item["source"]).read_text(encoding="utf-8")
            existing_source = source_path.read_text(encoding="utf-8") if source_path.exists() else ""
        except OSError as exc:
            routed_actions.append({**item, "action": "route-error", "error": str(exc)})
            remaining.append(item)
            continue

        stamp = "" if dry_run else context_distill_stamp()
        decision = context_distill.route_context_governance_root(
            adapter=adapter,
            root_text=root_text,
            core_text=core_text,
            existing_source_text=existing_source,
            stamp=stamp,
        )

        if dry_run:
            routed_actions.append({**item, "action": "would-inherit", "route_status": decision["status"]})
            continue

        if decision["status"] not in {"INHERITED", "ALREADY_INHERITED"}:
            # Coverage failure or blocked archive: do NOT overwrite. Fall back to
            # preserve so the human root is never lost.
            routed_actions.append({**item, "action": "preserve-conflict", "route_status": decision["status"]})
            continue

        if decision["bak_name"]:
            backup_path = target.with_name(f"{target.name}{decision['bak_name']}")
            shutil.copy2(target, backup_path)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(decision["source_text"], encoding="utf-8")
        target.write_text(decision["root_text"], encoding="utf-8")
        routed_actions.append({**item, "action": "inherit", "route_status": decision["status"]})

    return routed_actions, remaining


def context_distill_stamp() -> str:
    return utc_stamp()


def is_tes_runtime_conflict(relpath: str) -> bool:
    parts = Path(relpath).parts
    if len(parts) >= 3 and parts[0] == ".agents" and parts[1] == "skills" and parts[2].startswith("tes-"):
        return True
    if len(parts) >= 3 and parts[0] == ".claude" and parts[1] == "skills" and parts[2].startswith("tes-"):
        return True
    if len(parts) >= 2 and parts[0] == "skills" and parts[1].startswith("tes-"):
        return True
    if (
        len(parts) >= 4
        and parts[0] == "plugins"
        and parts[1] == "tilly-engineer-skills"
        and parts[2] == "skills"
        and parts[3].startswith("tes-")
    ):
        return True
    if relpath.startswith(".claude-plugin/"):
        return True
    if relpath.startswith("plugins/tilly-engineer-skills/.codex-plugin/"):
        return True
    if relpath == ".agents/plugins/marketplace.json":
        return True
    if relpath == ".cursor/rules/tes-runtime-capabilities.mdc":
        return True
    return False


def is_context_governance_path(relpath: str) -> bool:
    if relpath == ".cursor/rules/tes-runtime-capabilities.mdc":
        return False
    if relpath in {"AGENTS.md", "CLAUDE.md", "CURSOR.md", ".cursorrules"}:
        return True
    return relpath.startswith(".cursor/rules/")


def layer_for_relpath(relpath: str) -> str:
    if is_tes_runtime_conflict(relpath):
        return "runtime_capability"
    if is_context_governance_path(relpath):
        return "context_governance"
    return "runtime_capability"


def is_tes_owned_cursor_bootloader(relpath: str, target: Path) -> bool:
    if relpath != "CURSOR.md" or not target.exists():
        return False
    try:
        text = target.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    markers = (
        "# Using This Repo With Cursor",
        "Cursor loads `.cursor/rules/tes-guidelines.mdc`.",
        "## Behavioral Source Of Truth",
    )
    return sum(1 for marker in markers if marker in text) >= 2


def is_tes_owned_cursor_rule(relpath: str, target: Path) -> bool:
    if relpath != ".cursor/rules/tes-guidelines.mdc" or not target.exists():
        return False
    try:
        text = target.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    markers = (
        "Tilly Engineering",
        "Think Before Coding",
        "Maturity Layer Gate",
        "Goal-Driven Execution",
        "/tes-init",
    )
    return sum(1 for marker in markers if marker in text) >= 2


def can_overwrite_conflict(
    relpath: str,
    target: Path,
    broad_overwrite: bool,
    root_context_reviewed: bool = False,
    clean_runtime: bool = False,
) -> bool:
    if is_tes_runtime_conflict(relpath):
        return True
    if is_context_governance_path(relpath):
        if clean_runtime:
            return True
        if root_context_reviewed:
            return True
        return is_tes_owned_cursor_bootloader(relpath, target) or is_tes_owned_cursor_rule(relpath, target)
    return broad_overwrite


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def selected_adapters(adapter: str) -> list[str]:
    return materialize_adapter.selected_adapters(adapter)


def iter_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def relative_files(root: Path) -> list[Path]:
    return [path.relative_to(root) for path in iter_files(root)]


def target_for(source_root: Path, target_root: Path, source_file: Path) -> Path:
    return target_root / source_file.relative_to(source_root)


def build_retrofit_plan(
    target_root: Path,
    adapter: str,
    conflicts: list[dict[str, str]],
    install_command: str,
) -> Path:
    plan_dir = target_root / RETROFIT_DIR
    plan_dir.mkdir(parents=True, exist_ok=True)
    path = plan_dir / f"{utc_stamp()}-{adapter}-retrofit.md"
    rows = "\n".join(
        f"| `{item['target']}` | `{item['source']}` | `{item['target_sha']}` | `{item['source_sha']}` |"
        for item in conflicts
    )
    path.write_text(
        "\n".join(
            [
                "# TES Adapter Retrofit Plan",
                "",
                "This file was generated because installation found existing target files",
                "that differ from the materialized Tilly adapter files.",
                "",
                "Use an LLM or reviewer to merge intent. Do not blindly replace",
                "project-specific instructions.",
                "",
                "## Install Command",
                "",
                "```bash",
                install_command,
                "```",
                "",
                "## Conflicts",
                "",
                "| Target | Source | Target SHA | Source SHA |",
                "|--------|--------|------------|------------|",
                rows,
                "",
                "## LLM Retrofit Instructions",
                "",
                "Merge the Tilly Engineering Discipline contract into the target project",
                "without deleting existing project-specific instructions. Preserve local",
                "commands, test oracles, paths, security constraints, and ownership notes.",
                "",
                "Keep the maturity-aware behavioral gates visible:",
                "",
                "- Think Before Coding",
                "- Maturity Layer Gate",
                "- Simplicity First",
                "- Surgical Changes",
                "- Goal-Driven Execution",
                "",
                "After merging, run the target project's smallest relevant validation and",
                "then run this installer again without `--retrofit-plan` to confirm there",
                "are no unmanaged conflicts.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def collect_adapter_plan(adapter_root: Path, target_root: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    copies: list[dict[str, str]] = []
    conflicts: list[dict[str, str]] = []

    for source in iter_files(adapter_root):
        relpath = source.relative_to(adapter_root).as_posix()
        target = target_for(adapter_root, target_root, source)
        source_sha = sha256_file(source)
        if target.exists():
            target_sha = sha256_file(target)
            if target_sha != source_sha:
                conflicts.append(
                    {
                        "source": str(source),
                        "target": str(target),
                        "source_sha": source_sha,
                        "target_sha": target_sha,
                    }
                )
                continue
            action = "skip-identical"
        else:
            target_sha = ""
            action = "copy"

        copies.append(
            {
                "source": str(source),
                "target": str(target),
                "relpath": relpath,
                "source_sha": source_sha,
                "target_sha": target_sha,
                "action": action,
            }
        )

    return copies, conflicts


def require_confirmation(args: argparse.Namespace) -> bool:
    if args.dry_run or args.yes:
        return True
    if not sys.stdin.isatty():
        print("[install-adapter] FAIL")
        print("- write mode requires --yes when stdin is not interactive")
        return False
    answer = input("Install files into target project? Type 'yes' to continue: ")
    if answer.strip().lower() != "yes":
        print("[install-adapter] CANCELLED")
        return False
    return True


def capture_install_result(target: Path, adapter: str, status: str, dry_run: bool, failure_count: int) -> None:
    if dry_run:
        return
    field_reports.safe_record_event(
        target,
        "install_adapter",
        status,
        "adapter",
        "cli",
        details={"adapter": adapter, "dry_run": dry_run, "failures": failure_count},
    )


def copy_files(
    copies: list[dict[str, str]],
    overwrite_conflicts: list[dict[str, str]],
    preserved_conflicts: list[dict[str, str]],
    dry_run: bool,
    backup: bool,
) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for item in preserved_conflicts:
        actions.append({**item, "action": "preserve-conflict"})
    for item in [*copies, *overwrite_conflicts]:
        source = Path(item["source"])
        target = Path(item["target"])
        action = item.get("action", "overwrite")
        if action == "skip-identical":
            actions.append({**item, "action": "skip-identical"})
            continue

        if dry_run:
            actions.append({**item, "action": "would-" + action})
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and backup:
            backup_path = target.with_name(f"{target.name}.bak-{utc_stamp()}")
            shutil.copy2(target, backup_path)
            actions.append({**item, "action": "backup", "backup": str(backup_path)})
        shutil.copy2(source, target)
        actions.append({**item, "action": action})
    return actions


def install(args: argparse.Namespace) -> int:
    target_root = args.target.resolve()
    if not target_root.exists():
        print("[install-adapter] FAIL")
        print(f"- target does not exist: {target_root}")
        return 1
    if not target_root.is_dir():
        print("[install-adapter] FAIL")
        print(f"- target is not a directory: {target_root}")
        return 1
    blocked = tes_bundle.package_source_block(target_root, "install_adapter")
    if blocked:
        print(json.dumps(blocked, indent=2))
        print("[install-adapter] BLOCKED")
        return 2

    with tempfile.TemporaryDirectory(prefix="tes-install-") as tempdir:
        out_root = Path(tempdir) / "adapters"
        materialized = [
            materialize_adapter.materialize(adapter, out_root)
            for adapter in selected_adapters(args.adapter)
        ]
        failures = [
            failure
            for result in materialized
            for failure in result["failures"]
        ]
        if failures:
            print("[install-adapter] FAIL")
            for failure in failures:
                print(f"- materialization failed: {failure}")
            return 1

        planned: list[dict[str, Any]] = []
        all_conflicts: list[dict[str, str]] = []
        for adapter in selected_adapters(args.adapter):
            adapter_root = out_root / adapter
            copies, conflicts = collect_adapter_plan(adapter_root, target_root)
            planned.append(
                {
                    "adapter": adapter,
                    "source_root": str(adapter_root),
                    "files": len(relative_files(adapter_root)),
                    "copy_or_skip": len(copies),
                    "conflicts": len(conflicts),
                }
            )
            all_conflicts.extend(conflicts)

        root_context_result = root_context.analyze(target_root)
        retrofit_plan = None
        if all_conflicts and not args.overwrite:
            if args.retrofit_plan:
                retrofit_plan = build_retrofit_plan(
                    target_root,
                    args.adapter,
                    all_conflicts,
                    " ".join(sys.argv),
                )

        if not require_confirmation(args):
            capture_install_result(target_root, args.adapter, "CANCELLED", args.dry_run, 0)
            return 1

        bundle_stage = tes_bundle.stage_preferred_bundle(target_root, dry_run=args.dry_run, adapter=args.adapter)
        if bundle_stage.get("status") == "FAIL":
            print(json.dumps(
                {
                    "version": VERSION,
                    "status": "BUNDLE-STAGE-FAIL",
                    "target": str(target_root),
                    "adapter": args.adapter,
                    "bundle_stage": bundle_stage,
                },
                indent=2,
            ))
            capture_install_result(target_root, args.adapter, "BUNDLE-STAGE-FAIL", args.dry_run, 1)
            return 1

        if not args.dry_run:
            field_reports.ensure_git_exclude(target_root)

        clean_runtime = not args.preserve_context
        clean_backup = None
        obsolete_cleanup = None
        if clean_runtime and not args.dry_run:
            clean_backup = tes_bundle.clean_backup(
                target_root,
                adapter=args.adapter,
                project_state="unknown",
            )
            if clean_backup.get("status") != "BACKED_UP":
                print(json.dumps(clean_backup, indent=2))
                capture_install_result(target_root, args.adapter, "BACKUP-FAIL", args.dry_run, 1)
                return 1
            staged_manifest = tes_bundle.read_staged_manifest(target_root)
            obsolete_cleanup = tes_bundle.cleanup_obsolete_runtime(target_root, staged_manifest, dry_run=False)

        actions: list[dict[str, str]] = []
        preserved_conflicts: list[dict[str, str]] = []
        for adapter in selected_adapters(args.adapter):
            adapter_root = out_root / adapter
            copies, conflicts = collect_adapter_plan(adapter_root, target_root)
            copies = [
                {
                    **item,
                    "layer": layer_for_relpath(item["relpath"]),
                }
                for item in copies
            ]
            overwrite_items = [
                {
                    **item,
                    "relpath": Path(item["source"]).relative_to(adapter_root).as_posix(),
                    "layer": layer_for_relpath(Path(item["source"]).relative_to(adapter_root).as_posix()),
                    "action": "overwrite",
                }
                for item in conflicts
                if can_overwrite_conflict(
                    Path(item["source"]).relative_to(adapter_root).as_posix(),
                    Path(item["target"]),
                    args.overwrite,
                    args.root_context_reviewed,
                    clean_runtime,
                )
            ]
            preserved_items = [
                {
                    **item,
                    "relpath": Path(item["source"]).relative_to(adapter_root).as_posix(),
                    "layer": layer_for_relpath(Path(item["source"]).relative_to(adapter_root).as_posix()),
                }
                for item in conflicts
                if not can_overwrite_conflict(
                    Path(item["source"]).relative_to(adapter_root).as_posix(),
                    Path(item["target"]),
                    args.overwrite,
                    args.root_context_reviewed,
                    clean_runtime,
                )
            ]
            preserved_conflicts.extend(preserved_items)
            # P2 SPEC-007: route context_governance roots (CLAUDE.md/AGENTS.md)
            # through inherit+render instead of blind whole-file overwrite.
            routed_actions, overwrite_items = route_inherited_context_roots(
                overwrite_items, target_root, args.dry_run,
            )
            actions.extend(routed_actions)
            actions.extend(copy_files(
                copies,
                overwrite_items,
                preserved_items,
                args.dry_run,
                backup=(not args.no_backup and not clean_runtime),
            ))

        status = "DRY-RUN" if args.dry_run else "INSTALLED"
        if clean_runtime and not args.dry_run:
            status = "INSTALLED_CLEAN_RUNTIME"
        if preserved_conflicts:
            status = "DRY-RUN-WITH-PRESERVED-CONFLICTS" if args.dry_run else "INSTALLED_WITH_PRESERVED_CONFLICTS"
        safe_action_names = {
            "copy",
            "overwrite",
            "skip-identical",
            "would-copy",
            "would-overwrite",
        }
        has_safe_adapter_surface = any(action.get("action") in safe_action_names for action in actions)
        preserved_context = [
            item for item in preserved_conflicts
            if item.get("layer") == "context_governance"
        ]
        if preserved_conflicts and not has_safe_adapter_surface:
            status = "DRY-RUN-CONFLICT" if args.dry_run else "CONFLICT"
        elif preserved_context:
            status = "DRY-RUN-WITH-PRESERVED-CONTEXT" if args.dry_run else "INSTALLED_WITH_PRESERVED_CONTEXT"
        if obsolete_cleanup and obsolete_cleanup.get("status") == "NEEDS_REVIEW" and status != "CONFLICT":
            status = "NEEDS_REVIEW"

        layer_results: dict[str, dict[str, int]] = {}
        for action in actions:
            layer = action.get("layer", "unknown")
            name = action.get("action", "unknown")
            layer_results.setdefault(layer, {})
            layer_results[layer][name] = layer_results[layer].get(name, 0) + 1
        installed_capabilities = [
            action for action in actions
            if action.get("layer") == "runtime_capability"
            and action.get("action") in {"copy", "overwrite", "skip-identical", "would-copy", "would-overwrite"}
        ]
        recovery = None
        if clean_runtime and clean_backup and not args.dry_run:
            recovery = tes_bundle.recover_from_backup(
                target_root,
                str(clean_backup["backup_id"]),
                apply_safe=True,
            )

        result = {
            "version": VERSION,
            "status": status,
            "target": str(target_root),
            "adapter": args.adapter,
            "planned": planned,
            "bundle_stage": bundle_stage,
            "mode": "clean-runtime" if clean_runtime else "preserve",
            "clean_backup": clean_backup,
            "obsolete_cleanup": obsolete_cleanup,
            "semantic_recovery": recovery,
            "root_context": root_context_result,
            "layer_results": layer_results,
            "actions": actions,
            "preserved_conflicts": preserved_conflicts,
            "preserved_context": preserved_context,
            "installed_capabilities": installed_capabilities,
            "obsolete_removed": [
                action for action in (obsolete_cleanup or {}).get("actions", [])
                if str(action.get("action", "")).startswith("remove-")
            ],
            "retrofit_plan": str(retrofit_plan) if retrofit_plan else None,
        }
        print(json.dumps(result, indent=2))
        capture_install_result(target_root, args.adapter, str(result["status"]), args.dry_run, len(preserved_conflicts))
        if result["status"] == "CONFLICT":
            print("[install-adapter] FAIL")
            print("- target has only conflicting files; use --retrofit-plan or explicit --overwrite after review")
            return 2
        print("[install-adapter] PASS")
        return 0


def self_test() -> dict[str, Any]:
    """SPEC-007 regression fixture: exercise route_inherited_context_roots, the
    installer seam that turns the default for context_governance roots. This
    covers the integration (read target root, merge canonical source, write the
    three artifacts, drop from blind copy), not just the pure decision in the
    oracle. Adversarial fixtures: rich root inherits, coverage failure falls back
    to preserve, idempotent re-route, and non-routed paths pass through.
    """
    failures: list[str] = []
    rich_root = (
        "# Project Rules\n"
        "Never commit directly to main; open a pull request instead.\n"
        "Always run `npm test` before closeout.\n"
        "Do not touch the legacy/ directory.\n"
        "API docs live in docs/api/.\n"
    )
    core_text = "# TES Core\n\nRoute project context to docs/agents/**. Use `/tes-update`.\n"

    def make_item(target_root: Path, relpath: str) -> dict[str, str]:
        source = target_root / "_src" / relpath
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(core_text, encoding="utf-8")
        return {
            "source": str(source),
            "target": str(target_root / relpath),
            "relpath": relpath,
            "layer": "context_governance",
        }

    with tempfile.TemporaryDirectory(prefix="tes-spec007-") as tempdir:
        target_root = Path(tempdir)

        # Case 1: a rich CLAUDE.md in conflict inherits — three artifacts written.
        (target_root / "CLAUDE.md").write_text(rich_root, encoding="utf-8")
        item = make_item(target_root, "CLAUDE.md")
        routed, remaining = route_inherited_context_roots([item], target_root, dry_run=False)
        if not routed or routed[0].get("action") != "inherit":
            failures.append(f"rich CLAUDE.md must route to inherit, got {routed and routed[0].get('action')}")
        if remaining:
            failures.append("inherited root must be removed from the blind-copy list")
        root_after = (target_root / "CLAUDE.md").read_text(encoding="utf-8")
        if "<!-- TES:CORE BEGIN" not in root_after or "@docs/agents/PROJECT-CONTEXT.md" not in root_after:
            failures.append("inherited CLAUDE.md must be the thin core + @ pointer render")
        source_path = target_root / CANONICAL_SOURCE_REL
        if not source_path.exists():
            failures.append("inherit must create the canonical source")
        else:
            src = source_path.read_text(encoding="utf-8")
            for unit in ("npm test", "legacy", "docs/api"):
                if unit not in src:
                    failures.append(f"canonical source missing inherited unit: {unit}")
        baks = list(target_root.glob("CLAUDE.md.bak-*"))
        if not baks:
            failures.append("inherit must archive the original root as .bak")
        elif baks[0].read_text(encoding="utf-8") != rich_root:
            failures.append("archived .bak must be byte-faithful to the original")

        # Case 2: re-routing the now-inherited root is ALREADY_INHERITED, no new .bak.
        item2 = make_item(target_root, "CLAUDE.md")
        routed2, _ = route_inherited_context_roots([item2], target_root, dry_run=False)
        if not routed2 or routed2[0].get("route_status") != "ALREADY_INHERITED":
            failures.append("re-routing an inherited root must be ALREADY_INHERITED")
        if len(list(target_root.glob("CLAUDE.md.bak-*"))) != len(baks):
            failures.append("already-inherited routing must not create another .bak")

        # Case 3: coverage failure falls back to preserve — root NOT overwritten.
        # A discards-free drop is simulated by routing a root whose units cannot
        # all be covered; here we force it via a monkeypatched decision.
        with tempfile.TemporaryDirectory(prefix="tes-spec007-cov-") as cov_dir:
            cov_root = Path(cov_dir)
            (cov_root / "CLAUDE.md").write_text(rich_root, encoding="utf-8")
            cov_item = {
                "source": str(make_item(cov_root, "CLAUDE.md")["source"]),
                "target": str(cov_root / "CLAUDE.md"),
                "relpath": "CLAUDE.md",
                "layer": "context_governance",
            }
            original = context_distill.route_context_governance_root
            try:
                context_distill.route_context_governance_root = (  # type: ignore[assignment]
                    lambda **kw: {"status": "NEEDS_REVIEW_COVERAGE", "bak_name": ".bak-x",
                                  "source_text": "", "root_text": None, "coverage": {"status": "NEEDS_REVIEW_COVERAGE"}}
                )
                cov_routed, _ = route_inherited_context_roots([cov_item], cov_root, dry_run=False)
            finally:
                context_distill.route_context_governance_root = original  # type: ignore[assignment]
            if not cov_routed or cov_routed[0].get("action") != "preserve-conflict":
                failures.append("coverage failure must fall back to preserve-conflict")
            if (cov_root / "CLAUDE.md").read_text(encoding="utf-8") != rich_root:
                failures.append("coverage failure must NOT overwrite the human root")

        # Case 4: a non-routed context_governance path (Cursor) passes through.
        cursor_item = {"source": "x", "target": "y", "relpath": ".cursorrules", "layer": "context_governance"}
        c_routed, c_remaining = route_inherited_context_roots([cursor_item], target_root, dry_run=False)
        if c_routed or len(c_remaining) != 1:
            failures.append(".cursorrules must pass through to the legacy copy path, not route")

        # Case 5: dry-run never writes and reports would-inherit.
        with tempfile.TemporaryDirectory(prefix="tes-spec007-dry-") as dry_dir:
            dry_root = Path(dry_dir)
            (dry_root / "AGENTS.md").write_text(rich_root, encoding="utf-8")
            dry_item = make_item(dry_root, "AGENTS.md")
            dry_routed, _ = route_inherited_context_roots([dry_item], dry_root, dry_run=True)
            if not dry_routed or dry_routed[0].get("action") != "would-inherit":
                failures.append("dry-run must report would-inherit")
            if (dry_root / "AGENTS.md").read_text(encoding="utf-8") != rich_root:
                failures.append("dry-run must not modify the root")
            if (dry_root / CANONICAL_SOURCE_REL).exists():
                failures.append("dry-run must not write the canonical source")

    return {"status": "PASS" if not failures else "FAIL", "failures": failures, "version": VERSION}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--adapter", default="all", choices=["all", *sorted(materialize_adapter.ADAPTERS)])
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true", help="confirm writes without an interactive prompt")
    parser.add_argument("--overwrite", action="store_true", help="replace conflicting target files")
    parser.add_argument("--preserve-context", action="store_true", help="legacy mode: preserve conflicting root governance")
    parser.add_argument("--root-context-reviewed", action="store_true", help="confirm root context was migrated or rejected before overwrite")
    parser.add_argument("--no-backup", action="store_true", help="do not create .bak-* files before overwrite")
    parser.add_argument("--retrofit-plan", action="store_true", help="write an LLM merge plan for conflicts")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2))
        print(f"[install-adapter] {result['status']}")
        return 0 if result["status"] == "PASS" else 1

    return install(args)


if __name__ == "__main__":
    sys.exit(main())
