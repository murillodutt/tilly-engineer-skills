#!/usr/bin/env python3
"""Build, stage, plan, and apply deterministic TES installer bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import materialize_adapter


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.71"
MANIFEST_NAME = "tes-bundle-manifest.json"
INSTALLED_MANIFEST = Path(".tes/manifest.json")
SETUP_ROOT = Path(".tes/setup")

REQUIRED_LAYERS = {
    "helper",
    "runtime_capability",
    "mcp_config",
    "context_governance",
    "project_alignment",
    "evidence",
    "cache",
}
REQUIRED_OWNERS = {"tes-owned", "project-owned", "generated", "derived"}
HELPER_FILES = (
    "cortex.py",
    "cortex_mcp.py",
    "cortex_embed.mjs",
    "field_reports.py",
    "tes_update.py",
    "tes_legacy_retirement.py",
    "root_context.py",
    "tes_init.py",
    "project_context_oracle.py",
    "project_alignment_oracle.py",
    "tes_open_obsidian.py",
)
CONTEXT_GOVERNANCE_PATHS = {
    "AGENTS.md",
    "CLAUDE.md",
    "CURSOR.md",
    ".cursorrules",
    ".cursor/rules/tes-guidelines.mdc",
}
MCP_CONFIG_PATHS = {
    ".codex/config.toml",
    ".mcp.json",
    ".cursor/mcp.json",
}


@dataclass(frozen=True)
class BundleEntry:
    path: str
    archive_path: str
    sha256: str
    layer: str
    owner: str
    install_policy: str
    obsolete_policy: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def iter_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def layer_for_path(path: str) -> str:
    parts = Path(path).parts
    if path.startswith(".tes/bin/"):
        return "helper"
    if path in MCP_CONFIG_PATHS:
        return "mcp_config"
    if path in CONTEXT_GOVERNANCE_PATHS:
        return "context_governance"
    if len(parts) >= 3 and parts[0] in {".agents", ".claude"} and parts[1] == "skills":
        return "runtime_capability"
    if len(parts) >= 2 and parts[0] == "skills":
        return "runtime_capability"
    if path.startswith("plugins/tilly-engineer-skills/"):
        return "runtime_capability"
    if path.startswith(".claude-plugin/"):
        return "runtime_capability"
    if path.startswith("docs/agents/evidence/"):
        return "evidence"
    if path.startswith("docs/agents/"):
        return "project_alignment"
    if path.startswith(".tes/field-reports/") or path.startswith(".tes/cortex/") or path.startswith(".tes/setup/"):
        return "cache"
    return "runtime_capability"


def owner_for_layer(layer: str) -> str:
    if layer == "context_governance":
        return "project-owned"
    if layer in {"project_alignment", "evidence"}:
        return "generated"
    if layer == "cache":
        return "derived"
    return "tes-owned"


def install_policy_for(layer: str) -> str:
    if layer == "context_governance":
        return "preserve-if-exists"
    if layer == "mcp_config":
        return "merge"
    if layer in {"project_alignment", "evidence", "cache"}:
        return "do-not-apply-directly"
    return "copy-with-backup"


def obsolete_policy_for(layer: str, owner: str) -> str:
    if owner == "tes-owned" and layer in {"helper", "runtime_capability", "mcp_config"}:
        return "remove-if-previously-manifested"
    return "preserve"


def make_entry(target_path: str, archive_path: str, source: Path) -> BundleEntry:
    layer = layer_for_path(target_path)
    owner = owner_for_layer(layer)
    return BundleEntry(
        path=target_path,
        archive_path=archive_path,
        sha256=sha256_file(source),
        layer=layer,
        owner=owner,
        install_policy=install_policy_for(layer),
        obsolete_policy=obsolete_policy_for(layer, owner),
    )


def manifest_payload(entries: list[BundleEntry]) -> dict[str, Any]:
    return {
        "schema": "tes-bundle-manifest@1",
        "version": VERSION,
        "layers": sorted(REQUIRED_LAYERS),
        "owners": sorted(REQUIRED_OWNERS),
        "purge_rule": "purge/update only acts on known tes-owned paths from the previous or current manifest",
        "entries": [entry.__dict__ for entry in sorted(entries, key=lambda item: item.path)],
    }


def validate_manifest(data: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if data.get("schema") != "tes-bundle-manifest@1":
        failures.append("manifest schema must be tes-bundle-manifest@1")
    if data.get("version") != VERSION:
        failures.append(f"manifest version must be {VERSION}")
    if set(data.get("layers", [])) != REQUIRED_LAYERS:
        failures.append("manifest layers do not match required layer set")
    if set(data.get("owners", [])) != REQUIRED_OWNERS:
        failures.append("manifest owners do not match required owner set")
    paths: set[str] = set()
    for entry in data.get("entries", []):
        if not isinstance(entry, dict):
            failures.append("manifest entry is not an object")
            continue
        path = str(entry.get("path", ""))
        if not path:
            failures.append("manifest entry missing path")
        if path in paths:
            failures.append(f"duplicate manifest path: {path}")
        paths.add(path)
        if entry.get("layer") not in REQUIRED_LAYERS:
            failures.append(f"{path}: invalid layer {entry.get('layer')}")
        if entry.get("owner") not in REQUIRED_OWNERS:
            failures.append(f"{path}: invalid owner {entry.get('owner')}")
        if not entry.get("sha256"):
            failures.append(f"{path}: missing sha256")
    return failures


def build_bundle(out: Path, adapter: str = "all") -> dict[str, Any]:
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    entries: list[BundleEntry] = []

    with tempfile.TemporaryDirectory(prefix="tes-bundle-") as tempdir:
        temp = Path(tempdir)
        adapter_root = temp / "adapters"
        for selected in materialize_adapter.selected_adapters(adapter):
            result = materialize_adapter.materialize(selected, adapter_root)
            if result.get("failures"):
                return {"version": VERSION, "status": "FAIL", "failures": result["failures"]}

        staged_files: list[tuple[Path, str]] = []
        for helper in HELPER_FILES:
            source = ROOT / "scripts" / helper
            if not source.exists():
                return {"version": VERSION, "status": "FAIL", "failures": [f"missing helper scripts/{helper}"]}
            archive_path = f"scripts/{helper}"
            entries.append(make_entry(f".tes/bin/{helper}", archive_path, source))
            staged_files.append((source, archive_path))

        for selected in materialize_adapter.selected_adapters(adapter):
            selected_root = adapter_root / selected
            for file_path in iter_files(selected_root):
                target_path = rel(file_path, selected_root)
                archive_path = f"adapters/{selected}/{target_path}"
                entries.append(make_entry(target_path, archive_path, file_path))
                staged_files.append((file_path, archive_path))

        manifest = manifest_payload(entries)
        failures = validate_manifest(manifest)
        if failures:
            return {"version": VERSION, "status": "FAIL", "failures": failures}

        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            bundle.writestr(MANIFEST_NAME, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            for source, archive_path in staged_files:
                bundle.write(source, archive_path)

    return {
        "version": VERSION,
        "status": "BUILT",
        "bundle": str(out),
        "sha256": sha256_file(out),
        "entries": len(entries),
    }


def stage_bundle(bundle: Path, target: Path, dry_run: bool = False) -> dict[str, Any]:
    bundle = bundle.resolve()
    target = target.resolve()
    stage_dir = target / SETUP_ROOT / VERSION
    if dry_run:
        return {
            "version": VERSION,
            "status": "DRY-RUN",
            "action": "would-stage",
            "bundle": str(bundle),
            "stage_dir": rel(stage_dir, target),
        }
    if not bundle.exists():
        return {"version": VERSION, "status": "FAIL", "failures": [f"missing bundle: {bundle}"]}
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(bundle) as archive:
        archive.extractall(stage_dir)
    current = target / SETUP_ROOT / "current"
    current.write_text(VERSION + "\n", encoding="utf-8")
    manifest = read_staged_manifest(target)
    failures = validate_manifest(manifest)
    return {
        "version": VERSION,
        "status": "STAGED" if not failures else "FAIL",
        "bundle": str(bundle),
        "stage_dir": rel(stage_dir, target),
        "manifest": rel(stage_dir / MANIFEST_NAME, target),
        "entries": len(manifest.get("entries", [])),
        "failures": failures,
    }


def stage_source_bundle(target: Path, dry_run: bool = False, adapter: str = "all") -> dict[str, Any]:
    target = target.resolve()
    if dry_run:
        return {
            "version": VERSION,
            "status": "DRY-RUN",
            "action": "would-build-and-stage",
            "stage_dir": rel(target / SETUP_ROOT / VERSION, target),
        }
    with tempfile.TemporaryDirectory(prefix="tes-bundle-build-") as tempdir:
        bundle = Path(tempdir) / f"tilly-engineer-skills-{VERSION}.zip"
        built = build_bundle(bundle, adapter=adapter)
        if built.get("status") != "BUILT":
            return built
        staged = stage_bundle(bundle, target)
        staged["built_sha256"] = built.get("sha256")
        return staged


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def read_staged_manifest(target: Path) -> dict[str, Any]:
    return read_json(target / SETUP_ROOT / VERSION / MANIFEST_NAME)


def read_installed_manifest(target: Path) -> dict[str, Any]:
    return read_json(target / INSTALLED_MANIFEST)


def plan_target(target: Path) -> dict[str, Any]:
    target = target.resolve()
    manifest = read_staged_manifest(target)
    if not manifest:
        return {"version": VERSION, "status": "FAIL", "failures": ["no staged bundle manifest"]}
    failures = validate_manifest(manifest)
    actions: list[dict[str, str]] = []
    for entry in manifest.get("entries", []):
        layer = entry["layer"]
        policy = entry["install_policy"]
        target_path = target / entry["path"]
        if layer in {"project_alignment", "evidence", "cache"}:
            action = "skip-layer"
        elif target_path.exists() and sha256_file(target_path) == entry["sha256"]:
            action = "skip-identical"
        elif policy == "preserve-if-exists" and target_path.exists():
            action = "preserve-context"
        elif policy == "merge":
            action = "needs-merge"
        elif target_path.exists():
            action = "overwrite-with-backup"
        else:
            action = "copy"
        actions.append({"path": entry["path"], "layer": layer, "owner": entry["owner"], "action": action})
    return {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "stage_dir": rel(target / SETUP_ROOT / VERSION, target),
        "actions": actions,
        "failures": failures,
    }


def backup_path(path: Path) -> Path:
    return path.with_name(f"{path.name}.bak-{VERSION}")


def copy_from_staged(target: Path, entry: dict[str, Any], dry_run: bool) -> dict[str, str]:
    source = target / SETUP_ROOT / VERSION / entry["archive_path"]
    dest = target / entry["path"]
    if dry_run:
        return {"path": entry["path"], "layer": entry["layer"], "action": "would-copy"}
    dest.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if dest.exists() and sha256_file(dest) != entry["sha256"]:
        backup = backup_path(dest)
        shutil.copy2(dest, backup)
    shutil.copy2(source, dest)
    result = {"path": entry["path"], "layer": entry["layer"], "action": "copy" if backup is None else "overwrite"}
    if backup:
        result["backup"] = rel(backup, target)
    return result


def purge_obsolete(target: Path, manifest: dict[str, Any], dry_run: bool) -> list[dict[str, str]]:
    previous = read_installed_manifest(target)
    current_paths = {entry["path"] for entry in manifest.get("entries", []) if isinstance(entry, dict)}
    actions: list[dict[str, str]] = []
    for entry in previous.get("entries", []):
        if not isinstance(entry, dict):
            continue
        path = str(entry.get("path", ""))
        if (
            path
            and path not in current_paths
            and entry.get("owner") == "tes-owned"
            and entry.get("obsolete_policy") == "remove-if-previously-manifested"
        ):
            target_path = target / path
            if target_path.exists():
                actions.append({"path": path, "action": "would-remove-obsolete" if dry_run else "remove-obsolete"})
                if not dry_run:
                    if target_path.is_dir():
                        shutil.rmtree(target_path)
                    else:
                        target_path.unlink()
    return actions


def apply_staged_bundle(target: Path, dry_run: bool = False, yes: bool = False) -> dict[str, Any]:
    target = target.resolve()
    manifest = read_staged_manifest(target)
    if not manifest:
        return {"version": VERSION, "status": "FAIL", "failures": ["no staged bundle manifest"]}
    failures = validate_manifest(manifest)
    if failures:
        return {"version": VERSION, "status": "FAIL", "failures": failures}
    if not dry_run and not yes:
        return {"version": VERSION, "status": "FAIL", "failures": ["apply requires --yes"]}

    actions = purge_obsolete(target, manifest, dry_run)
    for entry in manifest.get("entries", []):
        layer = entry["layer"]
        policy = entry["install_policy"]
        dest = target / entry["path"]
        if layer in {"project_alignment", "evidence", "cache"}:
            actions.append({"path": entry["path"], "layer": layer, "action": "skip-layer"})
            continue
        if policy == "preserve-if-exists" and dest.exists():
            actions.append({"path": entry["path"], "layer": layer, "action": "preserve-context"})
            continue
        if policy == "merge":
            actions.append({"path": entry["path"], "layer": layer, "action": "skip-merge-layer"})
            continue
        if dest.exists() and sha256_file(dest) == entry["sha256"]:
            actions.append({"path": entry["path"], "layer": layer, "action": "skip-identical"})
            continue
        actions.append(copy_from_staged(target, entry, dry_run))

    if not dry_run:
        installed_path = target / INSTALLED_MANIFEST
        installed_path.parent.mkdir(parents=True, exist_ok=True)
        installed_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "version": VERSION,
        "status": "DRY-RUN" if dry_run else "APPLIED",
        "actions": actions,
        "installed_manifest": rel(target / INSTALLED_MANIFEST, target),
    }


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-bundle-self-test-") as tempdir:
        temp = Path(tempdir)
        bundle = temp / "tes.zip"
        built = build_bundle(bundle)
        if built.get("status") != "BUILT":
            return {"version": VERSION, "status": "FAIL", "failures": built.get("failures", ["build failed"])}
        target = temp / "target"
        target.mkdir()
        (target / "AGENTS.md").write_text("project-owned\n", encoding="utf-8")
        (target / ".tes/bin").mkdir(parents=True)
        (target / ".tes/bin/local-only.py").write_text("do not purge\n", encoding="utf-8")
        staged = stage_bundle(bundle, target)
        if staged.get("status") != "STAGED":
            failures.extend(staged.get("failures", ["stage failed"]))
        planned = plan_target(target)
        if planned.get("status") != "PASS":
            failures.extend(planned.get("failures", ["plan failed"]))
        applied = apply_staged_bundle(target, yes=True)
        if applied.get("status") != "APPLIED":
            failures.extend(applied.get("failures", ["apply failed"]))
        if (target / "AGENTS.md").read_text(encoding="utf-8") != "project-owned\n":
            failures.append("project-owned AGENTS.md was overwritten")
        if not (target / ".tes/setup" / VERSION / MANIFEST_NAME).exists():
            failures.append("staged manifest missing")
        if not (target / ".tes/bin/tes_open_obsidian.py").exists():
            failures.append("helper tes_open_obsidian.py missing after apply")
        if not (target / ".agents/skills/tes-open-obsidian/SKILL.md").exists():
            failures.append("runtime tes-open-obsidian skill missing after apply")
        if not (target / ".tes/bin/local-only.py").exists():
            failures.append("unknown local helper was purged")
        reapplied = apply_staged_bundle(target, yes=True)
        if reapplied.get("status") != "APPLIED":
            failures.append("idempotent reapply failed")
    return {"version": VERSION, "status": "PASS" if not failures else "FAIL", "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--out", type=Path, required=True)
    build_parser.add_argument("--adapter", default="all", choices=["all", *sorted(materialize_adapter.ADAPTERS)])

    stage_parser = subparsers.add_parser("stage")
    stage_parser.add_argument("--target", type=Path, default=Path.cwd())
    stage_parser.add_argument("--bundle", type=Path)
    stage_parser.add_argument("--dry-run", action="store_true")

    plan_parser = subparsers.add_parser("plan")
    plan_parser.add_argument("--target", type=Path, default=Path.cwd())

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--target", type=Path, default=Path.cwd())
    apply_parser.add_argument("--dry-run", action="store_true")
    apply_parser.add_argument("--yes", action="store_true")

    args = parser.parse_args()
    if args.self_test:
        result = self_test()
    elif args.command == "build":
        result = build_bundle(args.out, adapter=args.adapter)
    elif args.command == "stage":
        if args.bundle:
            result = stage_bundle(args.bundle, args.target, dry_run=args.dry_run)
        else:
            result = stage_source_bundle(args.target, dry_run=args.dry_run)
    elif args.command == "plan":
        result = plan_target(args.target)
    elif args.command == "apply":
        result = apply_staged_bundle(args.target, dry_run=args.dry_run, yes=args.yes)
    else:
        parser.print_help()
        return 2

    print(json.dumps(result, indent=2))
    return 0 if result.get("status") in {"PASS", "BUILT", "STAGED", "DRY-RUN", "APPLIED"} else 1


if __name__ == "__main__":
    sys.exit(main())
