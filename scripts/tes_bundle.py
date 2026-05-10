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
from pathlib import Path
from typing import Any

import materialize_adapter


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.78"
MANIFEST_NAME = "tes-bundle-manifest.json"
INSTALLED_MANIFEST = Path(".tes/manifest.json")
SETUP_ROOT = Path(".tes/setup")
PUBLIC_DIST_ROOT = ROOT / "docs" / "dist" / VERSION
BUNDLE_FILENAME = f"tilly-engineer-skills-{VERSION}.zip"
PUBLIC_BUNDLE_BASE_URL = "https://murillodutt.github.io/tilly-engineer-skills/dist"
SETUP_IGNORE_COMMENT = "# TES installer staging cache"

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


def ensure_setup_excluded(target: Path, dry_run: bool = False) -> dict[str, str]:
    repo = git_repo_paths(target)
    if repo is None:
        return {"status": "NOT_APPLIED", "reason": "target is not inside a git worktree"}
    repo_root, common_dir = repo
    exclude = common_dir / "info" / "exclude"
    pattern = setup_exclude_pattern(target, repo_root)
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
    comment = "" if SETUP_IGNORE_COMMENT in existing else f"{SETUP_IGNORE_COMMENT}\n"
    with exclude.open("a", encoding="utf-8") as handle:
        handle.write(f"{prefix}{comment}{pattern}\n")
    return {
        "status": "PASS",
        "path": rel(exclude, target),
        "pattern": pattern,
        "action": "add-local-exclude",
    }


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
        (target / "AGENTS.md").write_text("project-owned\n", encoding="utf-8")
        (target / ".tes/bin").mkdir(parents=True)
        (target / ".tes/bin/local-only.py").write_text("do not purge\n", encoding="utf-8")
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
        applied = apply_staged_bundle(target, yes=True)
        if applied.get("status") != "APPLIED":
            failures.extend(applied.get("failures", ["apply failed"]))
        installed = read_installed_manifest(target)
        installed_metadata = installed.get("metadata") if isinstance(installed.get("metadata"), dict) else {}
        if installed_metadata.get("source_commit") != metadata.get("source_commit"):
            failures.append("installed manifest source_commit metadata drifted")
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
        freshness = certify_source_freshness(target, remote_head=str(metadata.get("source_commit") or ""))
        if freshness.get("source_freshness") != "PASS":
            failures.append("source freshness helper did not certify equal staged source")
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

    plan_parser = subparsers.add_parser("plan")
    plan_parser.add_argument("--target", type=Path, default=Path.cwd())

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--target", type=Path, default=Path.cwd())
    apply_parser.add_argument("--dry-run", action="store_true")
    apply_parser.add_argument("--yes", action="store_true")

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
    elif args.command == "plan":
        result = plan_target(args.target)
    elif args.command == "apply":
        result = apply_staged_bundle(args.target, dry_run=args.dry_run, yes=args.yes)
    elif args.command == "freshness":
        result = certify_source_freshness(args.target, index=args.index, remote_head=args.remote_head)
    else:
        parser.print_help()
        return 2

    print(json.dumps(result, indent=2))
    return 0 if result.get("status") in {"PASS", "BUILT", "PUBLISHED", "STAGED", "DRY-RUN", "APPLIED", "STALE_SOURCE", "BLOCKED"} else 1


if __name__ == "__main__":
    sys.exit(main())
