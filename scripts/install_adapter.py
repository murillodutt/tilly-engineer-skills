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

import field_reports
import materialize_adapter
import root_context


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.47"
RETROFIT_DIR = ".tes/retrofit"


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
                "Use an LLM or human reviewer to merge intent. Do not blindly replace",
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
                "Keep the four behavioral gates visible:",
                "",
                "- Think Before Coding",
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

        if args.overwrite and root_context_result["status"] == "NEEDS_REVIEW" and not args.root_context_reviewed:
            print(json.dumps(
                {
                    "version": VERSION,
                    "status": "ROOT-CONTEXT-NEEDS-REVIEW",
                    "target": str(target_root),
                    "adapter": args.adapter,
                    "root_context": root_context_result,
                },
                indent=2,
            ))
            capture_install_result(target_root, args.adapter, "ROOT-CONTEXT-NEEDS-REVIEW", args.dry_run, len(root_context_result.get("roots", [])))
            print("[install-adapter] FAIL")
            print("- root bootloader context must be structured before overwrite; rerun root_context.py --write-plan")
            return 2

        if not require_confirmation(args):
            capture_install_result(target_root, args.adapter, "CANCELLED", args.dry_run, 0)
            return 1

        if not args.dry_run:
            field_reports.ensure_git_exclude(target_root)

        actions: list[dict[str, str]] = []
        preserved_conflicts: list[dict[str, str]] = []
        for adapter in selected_adapters(args.adapter):
            adapter_root = out_root / adapter
            copies, conflicts = collect_adapter_plan(adapter_root, target_root)
            overwrite_items = [
                {
                    **item,
                    "relpath": Path(item["source"]).relative_to(adapter_root).as_posix(),
                    "action": "overwrite",
                }
                for item in conflicts
            ] if args.overwrite else []
            preserved_items = [
                {
                    **item,
                    "relpath": Path(item["source"]).relative_to(adapter_root).as_posix(),
                }
                for item in conflicts
            ] if not args.overwrite else []
            preserved_conflicts.extend(preserved_items)
            actions.extend(copy_files(
                copies,
                overwrite_items,
                preserved_items,
                args.dry_run,
                backup=not args.no_backup,
            ))

        status = "DRY-RUN" if args.dry_run else "INSTALLED"
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
        if preserved_conflicts and not has_safe_adapter_surface:
            status = "DRY-RUN-CONFLICT" if args.dry_run else "CONFLICT"

        result = {
            "version": VERSION,
            "status": status,
            "target": str(target_root),
            "adapter": args.adapter,
            "planned": planned,
            "root_context": root_context_result,
            "actions": actions,
            "preserved_conflicts": preserved_conflicts,
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", default="all", choices=["all", *sorted(materialize_adapter.ADAPTERS)])
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true", help="confirm writes without an interactive prompt")
    parser.add_argument("--overwrite", action="store_true", help="replace conflicting target files")
    parser.add_argument("--root-context-reviewed", action="store_true", help="confirm root context was migrated or rejected before overwrite")
    parser.add_argument("--no-backup", action="store_true", help="do not create .bak-* files before overwrite")
    parser.add_argument("--retrofit-plan", action="store_true", help="write an LLM merge plan for conflicts")
    args = parser.parse_args()

    return install(args)


if __name__ == "__main__":
    sys.exit(main())
