#!/usr/bin/env python3
"""Build, stage, plan, and apply deterministic TES installer bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import materialize_adapter


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.143"
MANIFEST_NAME = "tes-bundle-manifest.json"
INSTALLED_MANIFEST = Path(".tes/manifest.json")
SETUP_ROOT = Path(".tes/setup")
BACKUP_ROOT = Path(".tes/bk")
PUBLIC_DIST_ROOT = ROOT / "docs" / "dist" / VERSION
BUNDLE_FILENAME = f"tilly-engineer-skills-{VERSION}.zip"
PUBLIC_BUNDLE_BASE_URL = "https://murillodutt.github.io/tilly-engineer-skills/dist"
SETUP_IGNORE_COMMENT = "# TES installer staging cache"
BACKUP_IGNORE_COMMENT = "# TES clean install local backups"
BACKUP_SCHEMA = "tes-clean-backup@1"
RECOVERY_SCHEMA = "tes-root-governance-recovery@1"

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
    "install_mcp.py",
    "install_mcp_hosts/__init__.py",
    "install_mcp_hosts/base.py",
    "install_mcp_hosts/codex.py",
    "install_mcp_hosts/claude.py",
    "install_mcp_hosts/cursor.py",
    "install_mcp_hosts/vscode.py",
    "cortex.py",
    "cortex_mcp.py",
    "cortex_embed.mjs",
    "scope_contract.py",
    "event_ledger.py",
    "checkpoint.py",
    "consolidation_gate.py",
    "field_reports.py",
    "mantra_gate.py",
    "mantra_gate_adoption_oracle.py",
    "tes_install.py",
    "tes_update.py",
    "tes_legacy_retirement.py",
    "root_context.py",
    "tes_init.py",
    "project_context_oracle.py",
    "project_alignment_oracle.py",
    "tes_map.py",
    "tes_map_oracle.py",
    "tes_open_obsidian.py",
    "tes_bump.py",
    "command_trigger_oracle.py",
    "tes_bundle.py",
    "materialize_adapter.py",
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
    ".vscode/mcp.json",
}
BACKUP_EXTRA_FILES = {
    *CONTEXT_GOVERNANCE_PATHS,
    *MCP_CONFIG_PATHS,
    ".tes/manifest.json",
    ".agents/plugins/marketplace.json",
}
BACKUP_EXTRA_DIRS = (
    ".cursor/rules",
    ".agents/skills",
    ".claude/skills",
    "skills",
    ".claude-plugin",
    "plugins/tilly-engineer-skills",
    ".tes/bin",
)
OBSOLETE_RUNTIME_DIRS = (
    ".agents/plugins",
    ".claude-plugin",
    "plugins/tilly-engineer-skills",
    "skills",
)
OBSOLETE_RUNTIME_FILE_PATHS = (
    ".agents/plugins/marketplace.json",
)
OBSOLETE_TES_MARKERS = (
    "tilly-engineer-skills",
    "Tilly Engineering",
    "TES",
    "Mantra Gate",
    "Context Mesh",
    "/tes-",
)
SECRET_RE = (
    "secret",
    "token",
    "apikey",
    "api_key",
    "password",
    "passwd",
    "private key",
    "-----begin",
)
NOISE_RE = (
    "tilly",
    "tes runtime",
    ".agents/skills",
    ".claude/skills",
    "plugins/tilly-engineer-skills",
    "/tes-",
    "docs/agents",
)
KEEP_RE = (
    "run ",
    "use ",
    "before ",
    "after ",
    "require",
    "must",
    "gate",
    "test",
    "build",
    "deploy",
    "approval",
    "owner",
    "security",
    "production",
)
REVIEW_RE = (
    "rm -rf",
    "sudo ",
    "chmod 777",
    "delete ",
    "drop database",
    "legal",
    "compliance",
)


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


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def public_bundle_url(version: str = VERSION) -> str:
    return f"{PUBLIC_BUNDLE_BASE_URL}/{version}/tilly-engineer-skills-{version}.zip"


def public_bundle_path() -> Path:
    return PUBLIC_DIST_ROOT / BUNDLE_FILENAME


def public_sha_path() -> Path:
    return PUBLIC_DIST_ROOT / f"{BUNDLE_FILENAME}.sha256"


def public_index_path() -> Path:
    return PUBLIC_DIST_ROOT / "index.json"


def parse_sha256_text(text: str) -> str:
    token = text.strip().split()[0] if text.strip() else ""
    if len(token) != 64 or any(char not in "0123456789abcdefABCDEF" for char in token):
        raise ValueError("invalid sha256 text")
    return token.lower()


def read_sha256_file(path: Path) -> str:
    return parse_sha256_text(path.read_text(encoding="utf-8"))


def git_value(args: list[str]) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def git_remote_head(repository: str, ref: str = "refs/heads/main") -> str | None:
    result = subprocess.run(
        ["git", "ls-remote", repository, ref],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    first = result.stdout.strip().split()
    if not first:
        return None
    value = first[0].strip()
    if len(value) != 40 or any(char not in "0123456789abcdef" for char in value.lower()):
        return None
    return value


def local_ancestor_check(source_commit: str, remote_commit: str) -> tuple[bool | None, str]:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", source_commit, remote_commit],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return True, "git-merge-base"
    if result.returncode == 1:
        return False, "git-merge-base"
    return None, "git-merge-base-unavailable"


def github_repo_slug(repository: str) -> str | None:
    if repository.startswith("git@github.com:"):
        slug = repository.removeprefix("git@github.com:").removesuffix(".git")
        return slug if "/" in slug else None
    parsed = urllib.parse.urlparse(repository)
    if parsed.netloc not in {"github.com", "www.github.com"}:
        return None
    slug = parsed.path.strip("/").removesuffix(".git")
    return slug if slug.count("/") == 1 else None


def github_ancestor_check(repository: str, source_commit: str, remote_commit: str) -> tuple[bool | None, str]:
    slug = github_repo_slug(repository)
    if not slug:
        return None, "github-compare-unavailable"
    url = f"https://api.github.com/repos/{slug}/compare/{source_commit}...{remote_commit}"
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return None, "github-compare-unavailable"
    status = payload.get("status")
    if status in {"identical", "ahead"}:
        return True, "github-compare"
    if status in {"behind", "diverged"}:
        return False, "github-compare"
    return None, "github-compare-unavailable"


def source_is_ancestor(repository: str, source_commit: str, remote_commit: str) -> tuple[bool | None, str]:
    local, method = local_ancestor_check(source_commit, remote_commit)
    if local is not None:
        return local, method
    return github_ancestor_check(repository, source_commit, remote_commit)


def bundle_metadata() -> dict[str, Any]:
    source_commit = git_value(["rev-parse", "HEAD"])
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    source_tree_state = "clean" if status.returncode == 0 and not status.stdout.strip() else "dirty"
    return {
        "schema": "tes-bundle-metadata@1",
        "version": VERSION,
        "source_repository": git_value(["config", "--get", "remote.origin.url"])
        or "https://github.com/murillodutt/tilly-engineer-skills.git",
        "source_commit": source_commit,
        "source_ref": "HEAD",
        "source_branch": git_value(["branch", "--show-current"]),
        "source_tree_state": source_tree_state,
        "created_at": git_value(["show", "-s", "--format=%cI", "HEAD"]),
    }


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
        return "tes-owned"
    if layer in {"project_alignment", "evidence"}:
        return "generated"
    if layer == "cache":
        return "derived"
    return "tes-owned"


def install_policy_for(layer: str) -> str:
    if layer == "context_governance":
        return "clean-overwrite-with-backup"
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
    metadata = bundle_metadata()
    return {
        "schema": "tes-bundle-manifest@1",
        "version": VERSION,
        "metadata": metadata,
        "source_repository": metadata["source_repository"],
        "source_commit": metadata["source_commit"],
        "created_at": metadata["created_at"],
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
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        failures.append("manifest metadata must be an object")
        metadata = {}
    for key in ("source_repository", "source_commit", "created_at"):
        if not data.get(key) and not metadata.get(key):
            failures.append(f"manifest missing {key}")
    source_commit = str(data.get("source_commit") or metadata.get("source_commit") or "")
    if len(source_commit) != 40 or any(char not in "0123456789abcdef" for char in source_commit.lower()):
        failures.append("manifest source_commit must be a 40-character git SHA")
    if metadata.get("schema") != "tes-bundle-metadata@1":
        failures.append("manifest metadata schema must be tes-bundle-metadata@1")
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
            bundle.writestr("tes-bundle-metadata.json", json.dumps(manifest["metadata"], indent=2, sort_keys=True) + "\n")
            for source, archive_path in staged_files:
                bundle.write(source, archive_path)

    return {
        "version": VERSION,
        "status": "BUILT",
        "bundle": str(out),
        "sha256": sha256_file(out),
        "entries": len(entries),
        "metadata": manifest["metadata"],
    }


def source_package_available() -> bool:
    return (ROOT / "src/adapters").is_dir() and (ROOT / "scripts/tes_bundle.py").exists()


def extracted_public_bundle_available() -> bool:
    return (ROOT / MANIFEST_NAME).is_file() and (ROOT / "scripts/tes_bundle.py").exists()


def zip_extracted_public_bundle(out: Path) -> dict[str, Any]:
    manifest_path = ROOT / MANIFEST_NAME
    if not manifest_path.exists():
        return {"version": VERSION, "status": "FAIL", "failures": ["missing extracted bundle manifest"]}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures = validate_manifest(manifest)
    if failures:
        return {"version": VERSION, "status": "FAIL", "failures": failures}

    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.write(manifest_path, MANIFEST_NAME)
        metadata_path = ROOT / "tes-bundle-metadata.json"
        if metadata_path.exists():
            bundle.write(metadata_path, "tes-bundle-metadata.json")
        for entry in manifest.get("entries", []):
            archive_path = str(entry.get("archive_path") or "")
            source = ROOT / archive_path
            if not source.exists():
                failures.append(f"missing extracted archive member: {archive_path}")
                continue
            digest = sha256_file(source)
            if digest != entry.get("sha256"):
                failures.append(f"{archive_path}: sha256 mismatch")
                continue
            bundle.write(source, archive_path)
    if failures:
        return {"version": VERSION, "status": "FAIL", "failures": failures}
    return {
        "version": VERSION,
        "status": "BUILT",
        "bundle": str(out),
        "sha256": sha256_file(out),
        "entries": len(manifest.get("entries", [])),
        "metadata": manifest.get("metadata", {}),
        "coverage": "public-extracted-bundle-contract",
    }


def prune_historical_dist(public_dist_root: Path = PUBLIC_DIST_ROOT) -> list[str]:
    """Enforce the single-current-dist policy.

    `docs/dist/` keeps exactly one directory: the current version. Older
    bundles are reachable via Git tags and the GitHub release surface;
    keeping every historical bundle inside the working tree inflates the
    repository without adding auditable value.

    Returns the list of removed version directory names (relative posix
    paths) so callers can report or test the action deterministically.
    """
    parent = public_dist_root.parent
    if not parent.is_dir():
        return []
    current_name = public_dist_root.name
    removed: list[str] = []
    for child in sorted(parent.iterdir()):
        if not child.is_dir():
            continue
        if child.name == current_name:
            continue
        shutil.rmtree(child)
        removed.append(child.name)
    return removed


def publish_public_bundle(out_dir: Path = PUBLIC_DIST_ROOT, adapter: str = "all") -> dict[str, Any]:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle = out_dir / BUNDLE_FILENAME
    built = build_bundle(bundle, adapter=adapter)
    if built.get("status") != "BUILT":
        return built
    digest = sha256_file(bundle)
    sha_path = out_dir / f"{bundle.name}.sha256"
    sha_path.write_text(f"{digest}  {bundle.name}\n", encoding="utf-8")
    metadata = built.get("metadata", {})
    index = {
        "schema": "tes-public-bundle-index@1",
        "version": VERSION,
        "bundle": bundle.name,
        "sha256": digest,
        "sha256_file": sha_path.name,
        "manifest": MANIFEST_NAME,
        "metadata": metadata,
        "source_repository": metadata.get("source_repository"),
        "source_commit": metadata.get("source_commit"),
        "created_at": metadata.get("created_at"),
        "stage_dir": f".tes/setup/{VERSION}",
        "urls": {
            "bundle": public_bundle_url(VERSION),
            "sha256": f"{public_bundle_url(VERSION)}.sha256",
        },
    }
    index_path = out_dir / "index.json"
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pruned = prune_historical_dist(out_dir)
    return {
        "version": VERSION,
        "status": "PUBLISHED",
        "bundle": str(bundle),
        "sha256": digest,
        "sha256_file": str(sha_path),
        "index": str(index_path),
        "entries": built.get("entries"),
        "metadata": metadata,
        "url": public_bundle_url(VERSION),
        "pruned_versions": pruned,
    }


def stage_bundle(bundle: Path, target: Path, dry_run: bool = False) -> dict[str, Any]:
    bundle = bundle.resolve()
    target = target.resolve()
    stage_dir = target / SETUP_ROOT / VERSION
    local_exclude = ensure_setup_excluded(target, dry_run=dry_run)
    if dry_run:
        return {
            "version": VERSION,
            "status": "DRY-RUN",
            "action": "would-stage",
            "bundle": str(bundle),
            "stage_dir": rel(stage_dir, target),
            "local_exclude": local_exclude,
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
        "local_exclude": local_exclude,
    }


def git_repo_paths(target: Path) -> tuple[Path, Path] | None:
    result = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "--show-toplevel", "--git-common-dir"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) < 2:
        return None
    repo_root = Path(lines[0]).resolve()
    common_dir = Path(lines[1])
    if not common_dir.is_absolute():
        common_dir = (target / common_dir).resolve()
    return repo_root, common_dir


def setup_exclude_pattern(target: Path, repo_root: Path) -> str:
    try:
        relative_target = target.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return ".tes/setup/"
    if relative_target == Path("."):
        return ".tes/setup/"
    return f"{relative_target.as_posix()}/.tes/setup/"


def backup_exclude_pattern(target: Path, repo_root: Path) -> str:
    try:
        relative_target = target.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return ".tes/bk/"
    if relative_target == Path("."):
        return ".tes/bk/"
    return f"{relative_target.as_posix()}/.tes/bk/"


def ensure_local_excluded(target: Path, pattern: str, comment: str, dry_run: bool = False) -> dict[str, str]:
    repo = git_repo_paths(target)
    if repo is None:
        return {"status": "NOT_APPLIED", "reason": "target is not inside a git worktree"}
    _, common_dir = repo
    exclude = common_dir / "info" / "exclude"
    if dry_run:
        return {
            "status": "DRY-RUN",
            "path": rel(exclude, target),
            "pattern": pattern,
            "action": "would-ensure-local-exclude",
        }
    existing = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    if pattern in {line.strip() for line in existing.splitlines()}:
        return {
            "status": "PASS",
            "path": rel(exclude, target),
            "pattern": pattern,
            "action": "already-ignored",
        }
    exclude.parent.mkdir(parents=True, exist_ok=True)
    prefix = "" if not existing or existing.endswith("\n") else "\n"
    comment_text = "" if comment in existing else f"{comment}\n"
    with exclude.open("a", encoding="utf-8") as handle:
        handle.write(f"{prefix}{comment_text}{pattern}\n")
    return {
        "status": "PASS",
        "path": rel(exclude, target),
        "pattern": pattern,
        "action": "add-local-exclude",
    }


def ensure_setup_excluded(target: Path, dry_run: bool = False) -> dict[str, str]:
    repo = git_repo_paths(target)
    if repo is None:
        return {"status": "NOT_APPLIED", "reason": "target is not inside a git worktree"}
    repo_root, _ = repo
    pattern = setup_exclude_pattern(target, repo_root)
    return ensure_local_excluded(target, pattern, SETUP_IGNORE_COMMENT, dry_run=dry_run)


def ensure_backup_excluded(target: Path, dry_run: bool = False) -> dict[str, str]:
    repo = git_repo_paths(target)
    if repo is None:
        return {"status": "NOT_APPLIED", "reason": "target is not inside a git worktree"}
    repo_root, _ = repo
    pattern = backup_exclude_pattern(target, repo_root)
    return ensure_local_excluded(target, pattern, BACKUP_IGNORE_COMMENT, dry_run=dry_run)


def hash_url_for_bundle(url: str) -> str:
    return f"{url}.sha256"


def fetch_url_text(url: str, timeout: float = 30.0) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read().decode("utf-8")


def download_bundle(url: str, out: Path, expected_sha256: str | None = None, timeout: float = 30.0) -> dict[str, Any]:
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        if expected_sha256 is None:
            expected_sha256 = parse_sha256_text(fetch_url_text(hash_url_for_bundle(url), timeout=timeout))
        with urllib.request.urlopen(url, timeout=timeout) as response:
            out.write_bytes(response.read())
    except (OSError, ValueError, urllib.error.URLError) as exc:
        return {"version": VERSION, "status": "FAIL", "failures": [f"bundle download failed: {exc}"]}
    actual = sha256_file(out)
    if actual != expected_sha256.lower():
        return {
            "version": VERSION,
            "status": "FAIL",
            "failures": [f"bundle sha256 mismatch: expected {expected_sha256.lower()} got {actual}"],
            "bundle": str(out),
            "sha256": actual,
        }
    return {
        "version": VERSION,
        "status": "DOWNLOADED",
        "url": url,
        "bundle": str(out),
        "sha256": actual,
    }


def stage_public_bundle(
    target: Path,
    url: str | None = None,
    expected_sha256: str | None = None,
    dry_run: bool = False,
    timeout: float = 30.0,
) -> dict[str, Any]:
    target = target.resolve()
    url = url or public_bundle_url(VERSION)
    if dry_run:
        return {
            "version": VERSION,
            "status": "DRY-RUN",
            "action": "would-download-and-stage",
            "url": url,
            "sha256": expected_sha256,
            "stage_dir": rel(target / SETUP_ROOT / VERSION, target),
        }
    with tempfile.TemporaryDirectory(prefix="tes-bundle-download-") as tempdir:
        bundle = Path(tempdir) / BUNDLE_FILENAME
        fetched = download_bundle(url, bundle, expected_sha256=expected_sha256, timeout=timeout)
        if fetched.get("status") != "DOWNLOADED":
            return fetched
        staged = stage_bundle(bundle, target)
        staged["download"] = {"url": url, "sha256": fetched.get("sha256")}
        staged["source"] = "public-bundle"
        return staged


def stage_local_public_bundle(target: Path, dry_run: bool = False) -> dict[str, Any]:
    bundle = public_bundle_path()
    sha_path = public_sha_path()
    if not bundle.exists() or not sha_path.exists():
        return {"version": VERSION, "status": "FAIL", "failures": ["local public bundle is missing"]}
    expected = read_sha256_file(sha_path)
    actual = sha256_file(bundle)
    if actual != expected:
        return {
            "version": VERSION,
            "status": "FAIL",
            "failures": [f"local public bundle sha256 mismatch: expected {expected} got {actual}"],
        }
    staged = stage_bundle(bundle, target, dry_run=dry_run)
    staged["source"] = "local-public-bundle"
    staged["sha256"] = actual
    return staged


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
        staged["source"] = "source-built-bundle"
        return staged


def stage_preferred_bundle(
    target: Path,
    dry_run: bool = False,
    adapter: str = "all",
    url: str | None = None,
    expected_sha256: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    if url:
        return stage_public_bundle(target, url=url, expected_sha256=expected_sha256, dry_run=dry_run, timeout=timeout)
    if public_bundle_path().exists() and public_sha_path().exists():
        local = stage_local_public_bundle(target, dry_run=dry_run)
        if local.get("status") != "FAIL":
            return local
    return stage_source_bundle(target, dry_run=dry_run, adapter=adapter)


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


def target_git_value(target: Path, args: list[str]) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(target), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def target_git_status(target: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(target), "status", "--short", "--branch"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "git-status-unavailable"


def backup_entry_index(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(entry.get("path")): entry
        for entry in manifest.get("entries", [])
        if isinstance(entry, dict) and entry.get("path")
    }


def is_backupable_path(relpath: str) -> bool:
    if not relpath or relpath.startswith("../") or relpath.startswith("/"):
        return False
    if relpath.startswith(".tes/setup/") or relpath.startswith(".tes/bk/"):
        return False
    return True


def collect_backup_candidates(target: Path, manifest: dict[str, Any]) -> list[Path]:
    candidates: set[Path] = set()
    for entry in manifest.get("entries", []):
        if not isinstance(entry, dict):
            continue
        relpath = str(entry.get("path") or "")
        if is_backupable_path(relpath) and (target / relpath).is_file():
            candidates.add(target / relpath)
    for relpath in BACKUP_EXTRA_FILES:
        path = target / relpath
        if path.is_file():
            candidates.add(path)
    for relpath in BACKUP_EXTRA_DIRS:
        root = target / relpath
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and is_backupable_path(rel(path, target)):
                candidates.add(path)
    return sorted(candidates)


def clean_backup(
    target: Path,
    *,
    adapter: str = "all",
    project_state: str = "unknown",
    backup_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    target = target.resolve()
    manifest = read_staged_manifest(target)
    if not manifest:
        manifest = read_installed_manifest(target)
    entry_index = backup_entry_index(manifest)
    backup_id = backup_id or utc_stamp()
    backup_dir = target / BACKUP_ROOT / backup_id
    local_exclude = ensure_backup_excluded(target, dry_run=dry_run)
    candidates = collect_backup_candidates(target, manifest)
    entries: list[dict[str, Any]] = []
    for path in candidates:
        relpath = rel(path, target)
        bundle_entry = entry_index.get(relpath, {})
        backup_rel = f"files/{relpath}"
        layer = str(bundle_entry.get("layer") or layer_for_path(relpath))
        owner_guess = "project-owned" if layer == "context_governance" else str(bundle_entry.get("owner") or owner_for_layer(layer))
        entries.append(
            {
                "path": relpath,
                "backup_path": backup_rel,
                "sha256": sha256_file(path),
                "layer": layer,
                "owner_guess": owner_guess,
                "reason": "pre-clean-runtime-snapshot",
                "restore_policy": "copy-back",
            }
        )
    if dry_run:
        return {
            "version": VERSION,
            "schema": BACKUP_SCHEMA,
            "status": "DRY-RUN",
            "backup_id": backup_id,
            "backup_dir": rel(backup_dir, target),
            "entries": entries,
            "local_exclude": local_exclude,
        }
    backup_dir.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        source = target / entry["path"]
        dest = backup_dir / entry["backup_path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
    payload = {
        "schema": BACKUP_SCHEMA,
        "version": VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "backup_id": backup_id,
        "target": str(target),
        "adapter": adapter,
        "route": adapter,
        "project_state": project_state,
        "source_tes_version": str(manifest.get("version") or "unknown"),
        "git_head": target_git_value(target, ["rev-parse", "HEAD"]) or "unknown",
        "git_status": target_git_status(target),
        "entries": entries,
    }
    manifest_path = backup_dir / "manifest.json"
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "version": VERSION,
        "schema": BACKUP_SCHEMA,
        "status": "BACKED_UP",
        "backup_id": backup_id,
        "backup_dir": rel(backup_dir, target),
        "manifest": rel(manifest_path, target),
        "entry_count": len(entries),
        "entries": entries,
        "local_exclude": local_exclude,
    }


def read_backup_manifest(target: Path, backup_id: str) -> dict[str, Any]:
    return read_json(target / BACKUP_ROOT / backup_id / "manifest.json")


def sanitize_excerpt(line: str) -> str:
    stripped = line.strip()
    if any(term in stripped.lower() for term in SECRET_RE):
        return "[redacted secret-like line]"
    return stripped[:180]


def classify_recovery_line(line: str) -> str:
    lower = line.lower()
    if any(term in lower for term in SECRET_RE) or any(term in lower for term in REVIEW_RE):
        return "needs_review"
    if any(term in lower for term in NOISE_RE):
        return "runtime_replaced"
    if any(term in lower for term in KEEP_RE):
        return "semantic_keep" if len(line) <= 140 else "semantic_compress"
    if len(line) > 140:
        return "semantic_compress"
    return "reject_noise"


def recovery_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line in {"---", "```", "```text"}:
            continue
        compact = line.lstrip("#>*-0123456789. `").strip()
        if len(compact) < 8:
            continue
        lines.append(compact)
        if len(lines) >= 20:
            break
    return lines


def recover_from_backup(
    target: Path,
    backup_id: str,
    *,
    apply_safe: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    target = target.resolve()
    manifest = read_backup_manifest(target, backup_id)
    if manifest.get("schema") != BACKUP_SCHEMA:
        return {"version": VERSION, "status": "FAIL", "failures": [f"missing clean backup: {backup_id}"]}
    groups: dict[str, list[dict[str, str]]] = {
        "semantic_keep": [],
        "semantic_compress": [],
        "runtime_replaced": [],
        "reject_noise": [],
        "needs_review": [],
    }
    backup_dir = target / BACKUP_ROOT / backup_id
    for entry in manifest.get("entries", []):
        if not isinstance(entry, dict):
            continue
        layer = str(entry.get("layer") or "")
        if layer not in {"context_governance", "runtime_capability"}:
            continue
        backup_path = backup_dir / str(entry.get("backup_path") or "")
        if not backup_path.is_file():
            continue
        try:
            text = backup_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            groups["needs_review"].append({"path": str(entry.get("path")), "excerpt": "non-utf8 file"})
            continue
        for line in recovery_lines(text):
            category = classify_recovery_line(line)
            item = {"path": str(entry.get("path")), "excerpt": sanitize_excerpt(line)}
            if item not in groups[category]:
                groups[category].append(item)
    status = "RECOVERED"
    if groups["needs_review"]:
        status = "NEEDS_REVIEW"
    report_rel = f"docs/agents/evidence/{backup_id}-root-governance-recovery.md"
    writes: list[str] = []
    if apply_safe and not dry_run:
        report = recovery_report(markdown_groups=groups, backup_id=backup_id, status=status, manifest=manifest)
        report_path = target / report_rel
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        writes.append(report_rel)
    return {
        "version": VERSION,
        "schema": RECOVERY_SCHEMA,
        "status": status if not dry_run else "DRY-RUN",
        "backup_id": backup_id,
        "report": report_rel if apply_safe else None,
        "writes": writes,
        "groups": groups,
        "counts": {key: len(value) for key, value in groups.items()},
    }


def recovery_report(
    *,
    markdown_groups: dict[str, list[dict[str, str]]],
    backup_id: str,
    status: str,
    manifest: dict[str, Any],
) -> str:
    sections: list[str] = []
    labels = {
        "semantic_keep": "Semantic Keep",
        "semantic_compress": "Semantic Compress",
        "runtime_replaced": "Runtime Replaced",
        "reject_noise": "Rejected Noise",
        "needs_review": "Needs Review",
    }
    for key, label in labels.items():
        rows = markdown_groups.get(key, [])
        body = "\n".join(f"- `{item['path']}`: {item['excerpt']}" for item in rows) or "- none"
        sections.append(f"## {label}\n\n{body}")
    return "\n\n".join(
        [
            "# TES Root Governance Recovery",
            "",
            f"Status: `{status}`",
            f"Backup: `{backup_id}`",
            f"TES Version: `{VERSION}`",
            f"Source TES Version: `{manifest.get('source_tes_version', 'unknown')}`",
            "",
            "This report treats previous root/runtime files as recovery evidence.",
            "The active runtime has already been replaced by canonical TES templates.",
            "",
            *sections,
            "",
        ]
    )


def restore_backup(target: Path, backup_id: str, *, dry_run: bool = False, yes: bool = False) -> dict[str, Any]:
    target = target.resolve()
    manifest = read_backup_manifest(target, backup_id)
    if manifest.get("schema") != BACKUP_SCHEMA:
        return {"version": VERSION, "status": "FAIL", "failures": [f"missing clean backup: {backup_id}"]}
    if not dry_run and not yes:
        return {"version": VERSION, "status": "FAIL", "failures": ["restore requires --yes"]}
    actions: list[dict[str, str]] = []
    backup_dir = target / BACKUP_ROOT / backup_id
    for entry in manifest.get("entries", []):
        if not isinstance(entry, dict):
            continue
        source = backup_dir / str(entry.get("backup_path") or "")
        dest = target / str(entry.get("path") or "")
        if not source.is_file():
            actions.append({"path": str(entry.get("path")), "action": "missing-backup-source"})
            continue
        actions.append({"path": str(entry.get("path")), "action": "would-restore" if dry_run else "restore"})
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
    return {
        "version": VERSION,
        "status": "DRY-RUN" if dry_run else "RESTORED",
        "backup_id": backup_id,
        "actions": actions,
    }


def public_index_data(index: Path | None = None) -> dict[str, Any]:
    if index is None:
        return {}
    return read_json(index)


def manifest_metadata(manifest: dict[str, Any]) -> dict[str, Any]:
    metadata = manifest.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def certify_source_freshness(
    target: Path,
    index: Path | None = None,
    remote_head: str | None = None,
) -> dict[str, Any]:
    target = target.resolve()
    manifest = read_staged_manifest(target)
    index_data = public_index_data(index)
    metadata = manifest_metadata(manifest) or manifest_metadata(index_data)
    source_commit = str(
        manifest.get("source_commit")
        or metadata.get("source_commit")
        or index_data.get("source_commit")
        or ""
    )
    repository = str(
        manifest.get("source_repository")
        or metadata.get("source_repository")
        or index_data.get("source_repository")
        or "https://github.com/murillodutt/tilly-engineer-skills.git"
    )
    failures: list[str] = []
    if not manifest:
        failures.append("no staged bundle manifest")
    if manifest.get("version") and manifest.get("version") != VERSION:
        failures.append(f"staged bundle version must be {VERSION}")
    if index_data:
        if index_data.get("version") != VERSION:
            failures.append(f"public bundle index version must be {VERSION}")
        if source_commit and index_data.get("source_commit") and source_commit != index_data.get("source_commit"):
            failures.append("staged manifest source_commit differs from public index")
    if len(source_commit) != 40 or any(char not in "0123456789abcdef" for char in source_commit.lower()):
        failures.append("source_commit is missing or invalid")
    remote_main = remote_head or git_remote_head(repository)
    if remote_main is None:
        failures.append("remote main could not be resolved")
    if failures:
        return {
            "version": VERSION,
            "status": "BLOCKED",
            "source_freshness": "BLOCKED",
            "meaning": "unknown",
            "source_package_commit": source_commit or "unknown",
            "source_remote_head": remote_main or "unknown",
            "source_repository": repository,
            "failures": failures,
        }
    if source_commit == remote_main:
        return {
            "version": VERSION,
            "status": "PASS",
            "source_freshness": "PASS",
            "meaning": "latest",
            "source_package_commit": source_commit,
            "source_remote_head": remote_main,
            "source_repository": repository,
            "comparison": "equal",
            "failures": [],
        }
    ancestor, method = source_is_ancestor(repository, source_commit, remote_main)
    if ancestor is True:
        return {
            "version": VERSION,
            "status": "PASS",
            "source_freshness": "PASS",
            "meaning": "current public bundle",
            "source_package_commit": source_commit,
            "source_remote_head": remote_main,
            "source_repository": repository,
            "comparison": method,
            "failures": [],
        }
    if ancestor is False:
        return {
            "version": VERSION,
            "status": "STALE_SOURCE",
            "source_freshness": "STALE_SOURCE",
            "meaning": "snapshot-only",
            "source_package_commit": source_commit,
            "source_remote_head": remote_main,
            "source_repository": repository,
            "comparison": method,
            "failures": ["source package commit is not an ancestor of remote main"],
        }
    return {
        "version": VERSION,
        "status": "BLOCKED",
        "source_freshness": "BLOCKED",
        "meaning": "unknown",
        "source_package_commit": source_commit,
        "source_remote_head": remote_main,
        "source_repository": repository,
        "comparison": method,
        "failures": ["source ancestry could not be checked"],
    }


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
        elif policy == "clean-overwrite-with-backup" and target_path.exists():
            action = "clean-overwrite-with-backup"
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


def copy_from_staged(target: Path, entry: dict[str, Any], dry_run: bool, backup_id: str | None) -> dict[str, str]:
    source = target / SETUP_ROOT / VERSION / entry["archive_path"]
    dest = target / entry["path"]
    if dry_run:
        return {"path": entry["path"], "layer": entry["layer"], "action": "would-copy"}
    dest.parent.mkdir(parents=True, exist_ok=True)
    had_dest = dest.exists()
    shutil.copy2(source, dest)
    action = "copy"
    if had_dest:
        action = "clean-overwrite" if backup_id else "overwrite"
    result = {"path": entry["path"], "layer": entry["layer"], "action": action}
    if backup_id and action == "clean-overwrite":
        result["backup_id"] = backup_id
    return result


def has_secret_signal(path: Path, text: str) -> bool:
    haystack = f"{path.as_posix()}\n{text}".lower()
    return any(marker in haystack for marker in SECRET_RE)


def read_small_text(path: Path) -> tuple[str | None, str | None]:
    try:
        if path.stat().st_size > 1_000_000:
            return None, "large-file"
        return path.read_text(encoding="utf-8", errors="ignore"), None
    except OSError as exc:
        return None, f"read-failed:{exc}"


def has_tes_marker(text: str) -> bool:
    return any(marker in text for marker in OBSOLETE_TES_MARKERS)


def marketplace_json_is_tes_only(path: Path) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        return False
    for item in plugins:
        if not isinstance(item, dict):
            return False
        plugin_identities = {str(item.get("name") or ""), str(item.get("id") or "")}
        if "tilly-engineer-skills" not in plugin_identities:
            return False
    return True


def classify_obsolete_file(target: Path, file_path: Path) -> tuple[bool, str]:
    relpath = rel(file_path, target)
    text, problem = read_small_text(file_path)
    if problem:
        return False, problem
    text = text or ""
    if has_secret_signal(file_path, text):
        return False, "secret-signal"

    parts = Path(relpath).parts
    if relpath == ".agents/plugins/marketplace.json":
        return (True, "tes-only-marketplace") if marketplace_json_is_tes_only(file_path) else (False, "ambiguous-marketplace")
    if parts[:1] == (".claude-plugin",):
        if file_path.name in {"plugin.json", "marketplace.json"} and "tilly-engineer-skills" in text:
            return True, "tes-claude-plugin-template"
        return False, "ambiguous-claude-plugin-file"
    if parts[:2] == ("plugins", "tilly-engineer-skills"):
        if has_tes_marker(text) or ".codex-plugin" in parts or (len(parts) >= 4 and parts[2] == "skills" and parts[3].startswith("tes-")):
            return True, "tes-codex-plugin-template"
        return False, "ambiguous-codex-plugin-file"
    if parts[:1] == ("skills",):
        if len(parts) >= 2 and parts[1].startswith("tes-") and has_tes_marker(text):
            return True, "tes-root-skill"
        return False, "ambiguous-root-skill"
    return False, "unknown-obsolete-path"


def backup_obsolete_review_items(
    target: Path,
    review_items: list[dict[str, str]],
    *,
    dry_run: bool,
) -> dict[str, Any] | None:
    if not review_items:
        return None
    backup_id = f"obsolete-runtime-{utc_stamp()}"
    backup_dir = target / BACKUP_ROOT / backup_id
    local_exclude = ensure_backup_excluded(target, dry_run=dry_run)
    entries: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in review_items:
        relpath = item["path"]
        path = target / relpath
        paths = [path] if path.is_file() else [candidate for candidate in path.rglob("*") if candidate.is_file()]
        for file_path in paths:
            file_rel = rel(file_path, target)
            if file_rel in seen or not is_backupable_path(file_rel):
                continue
            seen.add(file_rel)
            entry = {
                "path": file_rel,
                "backup_path": f"files/{file_rel}",
                "sha256": sha256_file(file_path),
                "layer": layer_for_path(file_rel),
                "owner_guess": "project-owned",
                "reason": "obsolete-runtime-needs-review",
                "restore_policy": "copy-back",
            }
            entries.append(entry)
            if not dry_run:
                dest = backup_dir / entry["backup_path"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest)

    payload = {
        "schema": BACKUP_SCHEMA,
        "version": VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "backup_id": backup_id,
        "target": str(target),
        "adapter": "obsolete-runtime-cleanup",
        "route": "obsolete-runtime-cleanup",
        "project_state": "needs_review",
        "source_tes_version": "unknown",
        "git_head": target_git_value(target, ["rev-parse", "HEAD"]) or "unknown",
        "git_status": target_git_status(target),
        "entries": entries,
        "review_items": review_items,
    }
    manifest_path = backup_dir / "manifest.json"
    if not dry_run:
        backup_dir.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        report_rel = f"docs/agents/evidence/{backup_id}-obsolete-runtime-review.md"
        report_path = target / report_rel
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Obsolete Runtime Review",
            "",
            f"Backup: `{backup_id}`",
            f"Status: `NEEDS_REVIEW`",
            "",
            "TES preserved obsolete plugin/root skill artifacts because at least one path was ambiguous, non-TES, modified, or secret-like.",
            "",
            "## Paths",
            "",
        ]
        for item in review_items:
            lines.append(f"- `{item['path']}`: {item['reason']}")
        lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "version": VERSION,
        "schema": BACKUP_SCHEMA,
        "status": "DRY-RUN" if dry_run else "BACKED_UP",
        "backup_id": backup_id,
        "backup_dir": rel(backup_dir, target),
        "manifest": rel(manifest_path, target),
        "entry_count": len(entries),
        "entries": entries,
        "local_exclude": local_exclude,
        "evidence_report": f"docs/agents/evidence/{backup_id}-obsolete-runtime-review.md",
    }


def cleanup_obsolete_runtime(target: Path, manifest: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    previous = read_installed_manifest(target)
    current_paths = {entry["path"] for entry in manifest.get("entries", []) if isinstance(entry, dict)}
    actions: list[dict[str, str]] = []
    review_items: list[dict[str, str]] = []
    handled_roots: set[str] = set()

    for entry in previous.get("entries", []):
        if not isinstance(entry, dict):
            continue
        path = str(entry.get("path", ""))
        if not (
            path
            and path not in current_paths
            and entry.get("owner") == "tes-owned"
            and entry.get("obsolete_policy") == "remove-if-previously-manifested"
        ):
            continue
        target_path = target / path
        if not target_path.exists():
            continue
        root = next((root for root in OBSOLETE_RUNTIME_DIRS if path == root or path.startswith(f"{root}/")), None)
        if root:
            handled_roots.add(root)
        expected = str(entry.get("sha256") or "")
        if target_path.is_file() and expected and sha256_file(target_path) != expected:
            review_items.append({"path": path, "action": "preserve-obsolete-runtime-needs-review", "reason": "manifest-sha256-mismatch"})
            continue
        actions.append({"path": path, "action": "would-remove-obsolete" if dry_run else "remove-obsolete", "reason": "previous-tes-manifest"})
        if not dry_run:
            if target_path.is_dir():
                shutil.rmtree(target_path)
            else:
                target_path.unlink()

    for relpath in (*OBSOLETE_RUNTIME_DIRS, *OBSOLETE_RUNTIME_FILE_PATHS):
        path = target / relpath
        if not path.exists():
            continue
        if relpath in handled_roots and not path.exists():
            continue
        if path.is_file():
            safe, reason = classify_obsolete_file(target, path)
            if safe:
                actions.append({"path": relpath, "action": "would-remove-obsolete-runtime" if dry_run else "remove-obsolete-runtime", "reason": reason})
                if not dry_run:
                    path.unlink()
                continue
            review_items.append({"path": relpath, "action": "preserve-obsolete-runtime-needs-review", "reason": reason})
            continue

        files = [candidate for candidate in path.rglob("*") if candidate.is_file()]
        if not files:
            actions.append({"path": relpath, "action": "would-remove-empty-obsolete-dir" if dry_run else "remove-empty-obsolete-dir", "reason": "empty"})
            if not dry_run:
                shutil.rmtree(path)
            continue
        unsafe = []
        for file_path in files:
            safe, reason = classify_obsolete_file(target, file_path)
            if not safe:
                unsafe.append({"path": rel(file_path, target), "reason": reason})
        if unsafe:
            reason = "; ".join(f"{item['path']}={item['reason']}" for item in unsafe[:5])
            review_items.append({"path": relpath, "action": "preserve-obsolete-runtime-needs-review", "reason": reason})
            continue
        actions.append({"path": relpath, "action": "would-remove-obsolete-runtime-dir" if dry_run else "remove-obsolete-runtime-dir", "reason": "tes-owned-generated"})
        if not dry_run:
            shutil.rmtree(path)

    backup = backup_obsolete_review_items(target, review_items, dry_run=dry_run)
    return {
        "version": VERSION,
        "status": "NEEDS_REVIEW" if review_items else ("DRY-RUN" if dry_run else "PASS"),
        "actions": [*actions, *review_items],
        "review_items": review_items,
        "review_backup": backup,
        "failures": [f"{item['path']}: {item['reason']}" for item in review_items],
    }


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


def remove_empty_obsolete_dirs(target: Path, dry_run: bool) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for relpath in OBSOLETE_RUNTIME_DIRS:
        path = target / relpath
        if not path.exists() or not path.is_dir():
            continue
        if any(item.is_file() for item in path.rglob("*")):
            actions.append({"path": relpath, "action": "preserve-nonempty-obsolete-dir"})
            continue
        actions.append({"path": relpath, "action": "would-remove-empty-obsolete-dir" if dry_run else "remove-empty-obsolete-dir"})
        if not dry_run:
            shutil.rmtree(path)
    return actions


def apply_staged_bundle(
    target: Path,
    dry_run: bool = False,
    yes: bool = False,
    mode: str = "clean-runtime",
    backup_id: str | None = None,
    adapter: str = "all",
) -> dict[str, Any]:
    target = target.resolve()
    manifest = read_staged_manifest(target)
    if not manifest:
        return {"version": VERSION, "status": "FAIL", "failures": ["no staged bundle manifest"]}
    failures = validate_manifest(manifest)
    if failures:
        return {"version": VERSION, "status": "FAIL", "failures": failures}
    if not dry_run and not yes:
        return {"version": VERSION, "status": "FAIL", "failures": ["apply requires --yes"]}
    clean_backup_result: dict[str, Any] | None = None
    if mode not in {"clean-runtime", "preserve"}:
        return {"version": VERSION, "status": "FAIL", "failures": [f"unsupported apply mode: {mode}"]}
    if mode == "clean-runtime" and not dry_run:
        if backup_id is None:
            clean_backup_result = clean_backup(target, adapter=adapter)
            if clean_backup_result.get("status") != "BACKED_UP":
                return clean_backup_result
            backup_id = str(clean_backup_result["backup_id"])
        elif not read_backup_manifest(target, backup_id):
            return {"version": VERSION, "status": "FAIL", "failures": [f"missing backup-id: {backup_id}"]}

    obsolete_cleanup = cleanup_obsolete_runtime(target, manifest, dry_run)
    actions = list(obsolete_cleanup.get("actions", []))
    for entry in manifest.get("entries", []):
        layer = entry["layer"]
        policy = entry["install_policy"]
        dest = target / entry["path"]
        if layer in {"project_alignment", "evidence", "cache"}:
            actions.append({"path": entry["path"], "layer": layer, "action": "skip-layer"})
            continue
        if mode == "preserve" and policy in {"preserve-if-exists", "clean-overwrite-with-backup"} and dest.exists():
            actions.append({"path": entry["path"], "layer": layer, "action": "preserve-context"})
            continue
        if policy == "merge":
            actions.append({"path": entry["path"], "layer": layer, "action": "skip-merge-layer"})
            continue
        if dest.exists() and sha256_file(dest) == entry["sha256"]:
            actions.append({"path": entry["path"], "layer": layer, "action": "skip-identical"})
            continue
        actions.append(copy_from_staged(target, entry, dry_run, backup_id))

    if not dry_run:
        installed_path = target / INSTALLED_MANIFEST
        installed_path.parent.mkdir(parents=True, exist_ok=True)
        installed_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    status = "DRY-RUN" if dry_run else ("CLEAN_APPLIED" if mode == "clean-runtime" else "APPLIED")
    if obsolete_cleanup.get("status") == "NEEDS_REVIEW":
        status = "NEEDS_REVIEW"

    return {
        "version": VERSION,
        "status": status,
        "mode": mode,
        "backup_id": backup_id,
        "clean_backup": clean_backup_result,
        "obsolete_cleanup": obsolete_cleanup,
        "actions": actions,
        "installed_manifest": rel(target / INSTALLED_MANIFEST, target),
        "failures": obsolete_cleanup.get("failures", []),
    }


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-bundle-self-test-") as tempdir:
        temp = Path(tempdir)
        bundle = temp / "tes.zip"
        if source_package_available():
            built = build_bundle(bundle)
            self_test_mode = "source-package"
        elif extracted_public_bundle_available():
            built = zip_extracted_public_bundle(bundle)
            self_test_mode = "public-extracted-bundle"
        else:
            return {
                "version": VERSION,
                "status": "FAIL",
                "failures": ["self-test requires source package or extracted public bundle"],
            }
        if built.get("status") != "BUILT":
            return {"version": VERSION, "status": "FAIL", "failures": built.get("failures", ["build failed"])}
        target = temp / "target"
        target.mkdir()
        subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)
        (target / "AGENTS.md").write_text("project-owned\nRun `npm test` before release.\n", encoding="utf-8")
        (target / ".cursor/rules").mkdir(parents=True)
        (target / ".cursor/rules/project.mdc").write_text("Use the internal emulator fixture.\n", encoding="utf-8")
        (target / ".tes/bin").mkdir(parents=True)
        (target / ".tes/bin/local-only.py").write_text("do not purge\n", encoding="utf-8")
        (target / ".tes/cortex").mkdir(parents=True)
        (target / ".tes/cortex/records.jsonl").write_text('{"durable":true}\n', encoding="utf-8")
        (target / ".tes/field-reports").mkdir(parents=True)
        (target / ".tes/field-reports/outbox.jsonl").write_text('{"event":"keep"}\n', encoding="utf-8")
        (target / "skills/tes-init").mkdir(parents=True)
        (target / "skills/tes-init/SKILL.md").write_text("# TES Init\n\nTilly Engineering /tes-init legacy root skill.\n", encoding="utf-8")
        (target / ".claude-plugin").mkdir(parents=True)
        (target / ".claude-plugin/plugin.json").write_text('{"name":"tilly-engineer-skills","version":"0.3.112","skills":["./skills/"]}\n', encoding="utf-8")
        (target / ".agents/plugins").mkdir(parents=True)
        (target / ".agents/plugins/marketplace.json").write_text('{"plugins":[{"id":"tilly-engineer-skills","version":"0.3.112"}]}\n', encoding="utf-8")
        (target / "plugins/tilly-engineer-skills/.codex-plugin").mkdir(parents=True)
        (target / "plugins/tilly-engineer-skills/.codex-plugin/plugin.json").write_text('{"name":"tilly-engineer-skills","version":"0.3.112","skills":"./skills/"}\n', encoding="utf-8")
        staged = stage_bundle(bundle, target)
        if staged.get("status") != "STAGED":
            failures.extend(staged.get("failures", ["stage failed"]))
        local_exclude = staged.get("local_exclude") if isinstance(staged.get("local_exclude"), dict) else {}
        if local_exclude.get("status") != "PASS":
            failures.append("staging did not ensure local .tes/setup/ git exclusion")
        ignored = subprocess.run(
            ["git", "check-ignore", f".tes/setup/{VERSION}/{MANIFEST_NAME}"],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
        )
        if ignored.returncode != 0:
            failures.append(".tes/setup staging cache is not ignored by target git")
        status = subprocess.run(
            ["git", "status", "--short", "--untracked-files=all"],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
        )
        if ".tes/setup/" in status.stdout:
            failures.append(".tes/setup staging cache is visible in target git status")
        manifest = read_staged_manifest(target)
        metadata = manifest.get("metadata") if isinstance(manifest.get("metadata"), dict) else {}
        if not metadata.get("source_commit"):
            failures.append("staged bundle manifest missing source_commit metadata")
        if validate_manifest(manifest):
            failures.extend(f"staged manifest invalid: {failure}" for failure in validate_manifest(manifest))
        downloaded_target = temp / "downloaded-target"
        downloaded_target.mkdir()
        downloaded = stage_public_bundle(
            downloaded_target,
            url=bundle.resolve().as_uri(),
            expected_sha256=str(built.get("sha256")),
        )
        if downloaded.get("status") != "STAGED":
            failures.extend(downloaded.get("failures", ["download stage failed"]))
        planned = plan_target(target)
        if planned.get("status") != "PASS":
            failures.extend(planned.get("failures", ["plan failed"]))
        if not any(action.get("action") == "clean-overwrite-with-backup" for action in planned.get("actions", [])):
            failures.append("plan must mark existing context as clean-overwrite-with-backup")
        backed_up = clean_backup(target, adapter="all", project_state="existing", backup_id="selftest")
        if backed_up.get("status") != "BACKED_UP":
            failures.extend(backed_up.get("failures", ["backup failed"]))
        if not (target / ".tes/bk/selftest/manifest.json").exists():
            failures.append("clean backup manifest missing")
        if not (target / ".tes/bk/selftest/files/AGENTS.md").exists():
            failures.append("clean backup did not preserve AGENTS.md")
        applied = apply_staged_bundle(target, yes=True)
        if applied.get("status") != "CLEAN_APPLIED":
            failures.extend(applied.get("failures", ["apply failed"]))
        installed = read_installed_manifest(target)
        installed_metadata = installed.get("metadata") if isinstance(installed.get("metadata"), dict) else {}
        if installed_metadata.get("source_commit") != metadata.get("source_commit"):
            failures.append("installed manifest source_commit metadata drifted")
        if "project-owned" in (target / "AGENTS.md").read_text(encoding="utf-8"):
            failures.append("clean runtime did not replace project-owned AGENTS.md")
        backup_id = str(applied.get("backup_id") or "")
        if not backup_id or not (target / ".tes/bk" / backup_id / "manifest.json").exists():
            failures.append("clean apply did not create central backup")
        recovery = recover_from_backup(target, backup_id, apply_safe=True)
        if recovery.get("status") not in {"RECOVERED", "NEEDS_REVIEW"}:
            failures.extend(recovery.get("failures", ["recovery failed"]))
        report = recovery.get("report")
        if not report or not (target / str(report)).exists():
            failures.append("recovery report missing")
        restored = restore_backup(target, "selftest", yes=True)
        if restored.get("status") != "RESTORED":
            failures.extend(restored.get("failures", ["restore failed"]))
        if "project-owned" not in (target / "AGENTS.md").read_text(encoding="utf-8"):
            failures.append("restore did not recover original AGENTS.md")
        reapplied_after_restore = apply_staged_bundle(target, yes=True)
        if reapplied_after_restore.get("status") != "CLEAN_APPLIED":
            failures.append("clean reapply after restore failed")
        if not (target / ".tes/setup" / VERSION / MANIFEST_NAME).exists():
            failures.append("staged manifest missing")
        if not (target / ".tes/bin/tes_open_obsidian.py").exists():
            failures.append("helper tes_open_obsidian.py missing after apply")
        if not (target / ".agents/skills/tes-open-obsidian/SKILL.md").exists():
            failures.append("runtime tes-open-obsidian skill missing after apply")
        for relpath in (".agents/plugins", ".claude-plugin", "plugins/tilly-engineer-skills", "skills"):
            if (target / relpath).exists():
                failures.append(f"source-only plugin artifact was installed: {relpath}")
        if not (target / ".tes/bin/local-only.py").exists():
            failures.append("unknown local helper was purged")
        if not (target / ".tes/cortex/records.jsonl").exists():
            failures.append("durable cortex state was not preserved")
        if not (target / ".tes/field-reports/outbox.jsonl").exists():
            failures.append("field reports state was not preserved")
        reapplied = apply_staged_bundle(target, yes=True)
        if reapplied.get("status") != "CLEAN_APPLIED":
            failures.append("idempotent reapply failed")
        review_target = temp / "obsolete-review-target"
        review_target.mkdir()
        subprocess.run(["git", "init"], cwd=review_target, text=True, capture_output=True, check=False)
        review_stage = stage_bundle(bundle, review_target)
        if review_stage.get("status") != "STAGED":
            failures.extend(review_stage.get("failures", ["review target stage failed"]))
        (review_target / "skills/custom").mkdir(parents=True)
        (review_target / "skills/custom/SKILL.md").write_text(
            "# Custom Skill\n\n" + "USER_" + "TOKEN=keep-me\n",
            encoding="utf-8",
        )
        review_apply = apply_staged_bundle(review_target, yes=True, mode="preserve")
        if review_apply.get("status") != "NEEDS_REVIEW":
            failures.append("ambiguous obsolete runtime must return NEEDS_REVIEW")
        if not (review_target / "skills/custom/SKILL.md").exists():
            failures.append("ambiguous obsolete runtime content was deleted")
        review_cleanup = review_apply.get("obsolete_cleanup") if isinstance(review_apply.get("obsolete_cleanup"), dict) else {}
        review_backup = review_cleanup.get("review_backup") if isinstance(review_cleanup.get("review_backup"), dict) else {}
        review_backup_id = str(review_backup.get("backup_id") or "")
        if not review_backup_id or not (review_target / ".tes/bk" / review_backup_id / "manifest.json").exists():
            failures.append("ambiguous obsolete runtime must be backed up for review")
        freshness = certify_source_freshness(target, remote_head=str(metadata.get("source_commit") or ""))
        if freshness.get("source_freshness") != "PASS":
            failures.append("source freshness helper did not certify equal staged source")

    # Single-current-dist policy: prune_historical_dist must keep only the
    # current version directory and remove every other docs/dist/<x>/ peer.
    # This regression-checks the policy added on 2026-05-25 in response to
    # the canary review that flagged stale dist artifacts in the repo.
    with tempfile.TemporaryDirectory(prefix="tes-bundle-prune-") as prune_temp:
        dist_root = Path(prune_temp) / "dist"
        for name in ("0.3.71", "0.3.99", "0.3.123", VERSION, "0.4.0-rc1"):
            (dist_root / name).mkdir(parents=True, exist_ok=True)
            (dist_root / name / "index.json").write_text("{}\n", encoding="utf-8")
        current = dist_root / VERSION
        pruned = prune_historical_dist(current)
        remaining = sorted(child.name for child in dist_root.iterdir() if child.is_dir())
        if remaining != [VERSION]:
            failures.append(
                f"single-current-dist policy must leave only {VERSION}, "
                f"found: {remaining}"
            )
        expected_pruned = {"0.3.71", "0.3.99", "0.3.123", "0.4.0-rc1"}
        if set(pruned) != expected_pruned:
            failures.append(
                f"prune_historical_dist must report removed peers exactly; "
                f"expected {sorted(expected_pruned)}, got {sorted(pruned)}"
            )
    return {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "self_test_mode": self_test_mode,
        "coverage": built.get("coverage", "source-package-contract"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--out", type=Path, required=True)
    build_parser.add_argument("--adapter", default="all", choices=["all", *sorted(materialize_adapter.ADAPTERS)])

    publish_parser = subparsers.add_parser("publish")
    publish_parser.add_argument("--out-dir", type=Path, default=PUBLIC_DIST_ROOT)
    publish_parser.add_argument("--adapter", default="all", choices=["all", *sorted(materialize_adapter.ADAPTERS)])

    stage_parser = subparsers.add_parser("stage")
    stage_parser.add_argument("--target", type=Path, default=Path.cwd())
    stage_parser.add_argument("--bundle", type=Path)
    stage_parser.add_argument("--url")
    stage_parser.add_argument("--sha256")
    stage_parser.add_argument("--dry-run", action="store_true")

    backup_parser = subparsers.add_parser("backup")
    backup_parser.add_argument("--target", type=Path, default=Path.cwd())
    backup_parser.add_argument("--adapter", default="all", choices=["all", *sorted(materialize_adapter.ADAPTERS)])
    backup_parser.add_argument("--project-state", default="unknown")
    backup_parser.add_argument("--backup-id")
    backup_parser.add_argument("--dry-run", action="store_true")
    backup_parser.add_argument("--yes", action="store_true", help="accepted for command symmetry")

    plan_parser = subparsers.add_parser("plan")
    plan_parser.add_argument("--target", type=Path, default=Path.cwd())

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--target", type=Path, default=Path.cwd())
    apply_parser.add_argument("--dry-run", action="store_true")
    apply_parser.add_argument("--yes", action="store_true")
    apply_parser.add_argument("--mode", default="clean-runtime", choices=["clean-runtime", "preserve"])
    apply_parser.add_argument("--backup-id")
    apply_parser.add_argument("--adapter", default="all", choices=["all", *sorted(materialize_adapter.ADAPTERS)])

    recover_parser = subparsers.add_parser("recover-plan")
    recover_parser.add_argument("--target", type=Path, default=Path.cwd())
    recover_parser.add_argument("--backup-id", required=True)
    recover_parser.add_argument("--apply-safe", action="store_true")
    recover_parser.add_argument("--dry-run", action="store_true")
    recover_parser.add_argument("--yes", action="store_true", help="confirm safe evidence writes")

    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("--target", type=Path, default=Path.cwd())
    restore_parser.add_argument("--backup-id", required=True)
    restore_parser.add_argument("--dry-run", action="store_true")
    restore_parser.add_argument("--yes", action="store_true")

    freshness_parser = subparsers.add_parser("freshness")
    freshness_parser.add_argument("--target", type=Path, default=Path.cwd())
    freshness_parser.add_argument("--index", type=Path)
    freshness_parser.add_argument("--remote-head")

    args = parser.parse_args()
    if args.self_test:
        result = self_test()
    elif args.command == "build":
        result = build_bundle(args.out, adapter=args.adapter)
    elif args.command == "publish":
        result = publish_public_bundle(args.out_dir, adapter=args.adapter)
    elif args.command == "stage":
        if args.url:
            result = stage_public_bundle(args.target, url=args.url, expected_sha256=args.sha256, dry_run=args.dry_run)
        elif args.bundle:
            result = stage_bundle(args.bundle, args.target, dry_run=args.dry_run)
        else:
            result = stage_preferred_bundle(args.target, dry_run=args.dry_run)
    elif args.command == "backup":
        result = clean_backup(
            args.target,
            adapter=args.adapter,
            project_state=args.project_state,
            backup_id=args.backup_id,
            dry_run=args.dry_run,
        )
    elif args.command == "plan":
        result = plan_target(args.target)
    elif args.command == "apply":
        result = apply_staged_bundle(
            args.target,
            dry_run=args.dry_run,
            yes=args.yes,
            mode=args.mode,
            backup_id=args.backup_id,
            adapter=args.adapter,
        )
    elif args.command == "recover-plan":
        if args.apply_safe and not args.dry_run and not args.yes:
            result = {"version": VERSION, "status": "FAIL", "failures": ["recover-plan --apply-safe requires --yes"]}
        else:
            result = recover_from_backup(
                args.target,
                args.backup_id,
                apply_safe=args.apply_safe,
                dry_run=args.dry_run,
            )
    elif args.command == "restore":
        result = restore_backup(args.target, args.backup_id, dry_run=args.dry_run, yes=args.yes)
    elif args.command == "freshness":
        result = certify_source_freshness(args.target, index=args.index, remote_head=args.remote_head)
    else:
        parser.print_help()
        return 2

    print(json.dumps(result, indent=2))
    return 0 if result.get("status") in {
        "PASS",
        "BUILT",
        "PUBLISHED",
        "STAGED",
        "DRY-RUN",
        "BACKED_UP",
        "APPLIED",
        "CLEAN_APPLIED",
        "RECOVERED",
        "RESTORED",
        "NEEDS_REVIEW",
        "STALE_SOURCE",
        "BLOCKED",
    } else 1


if __name__ == "__main__":
    sys.exit(main())
