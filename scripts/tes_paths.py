#!/usr/bin/env python3
"""TES installation topology resolver.

Single source of truth for *where* installed assets live, per the installation
topology Super SPEC. Pure path logic — no filesystem side effects (no mkdir, no
writes). Callers create directories; this module only computes paths.

Three homes:

- runtime_root(version) -> ~/.tes/runtime/<version>/     shared read-only code
- project_root(target)  -> ~/.tes/projects/<slug>/       per-project durable state
- capsule_root(target)  -> <repo>/.tes/                   minimal in-repo capsule

The project slug derives from the target's real path ALONE (never from the
random install_id in the capsule), so a repo can find its global project
namespace even when <repo>/.tes/ has been deleted.

Set TES_HOME to override the ~/.tes home (used by tests and by adopters who want
a non-default location). The value is honored verbatim as the global root.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

VERSION = "0.3.235"

# Same slug rule as field_reports.safe_slug (kept self-contained so this
# foundation module does not depend on a capability module).
_UNSAFE = re.compile(r"[^a-zA-Z0-9_.:-]+")

# Component widths of the deterministic project key (see the Super SPEC pointer).
_SLUG_NAME_WIDTH = 12
_SLUG_HASH_WIDTH = 12


def tes_home() -> Path:
    """The global TES home. ~/.tes by default; TES_HOME overrides it verbatim."""
    override = os.environ.get("TES_HOME")
    if override:
        return Path(override)
    return Path.home() / ".tes"


def _safe_slug(value: str, default: str = "project") -> str:
    slug = _UNSAFE.sub("-", value.strip()).strip("-._:")
    return slug if slug else default


def real_target(target: Path | str) -> str:
    """The canonical absolute path used as the stable project identity."""
    return os.path.realpath(str(target))


def project_slug(target: Path | str) -> str:
    """Deterministic per-project key: safe_slug(realpath)[:12]-sha256(realpath)[:12].

    Same realpath -> same slug. Two projects with the same basename at different
    paths -> different slug (the hash component disambiguates). Independent of the
    capsule, so capsule loss does not change the slug.
    """
    real = real_target(target)
    name = _safe_slug(os.path.basename(real.rstrip("/")) or real)[:_SLUG_NAME_WIDTH]
    digest = hashlib.sha256(real.encode("utf-8")).hexdigest()[:_SLUG_HASH_WIDTH]
    name = name or "project"
    return f"{name}-{digest}"


def runtime_root(version: str = VERSION) -> Path:
    """Shared, read-only runtime home for a given TES version."""
    return tes_home() / "runtime" / version


def runtime_bin(version: str = VERSION) -> Path:
    """Where the centralized runtime helpers live (the former <repo>/.tes/bin)."""
    return runtime_root(version) / "bin"


def project_root(target: Path | str) -> Path:
    """Per-project durable namespace (backup, restore manifest, rollback, cache)."""
    return tes_home() / "projects" / project_slug(target)


def project_cache(target: Path | str) -> Path:
    """Rebuildable per-project caches (recall/semantic indexes, bytecode)."""
    return project_root(target) / "cache"


def project_backup(target: Path | str) -> Path:
    """Per-project pre-install context backups (the uninstall restore source)."""
    return project_root(target) / "backup"


def capsule_root(target: Path | str) -> Path:
    """The minimal in-repo capsule: identity + pointers + manifest worklist cache."""
    return Path(real_target(target)) / ".tes"


def manifest_capsule_path(target: Path | str) -> Path:
    return capsule_root(target) / "manifest.json"


def manifest_namespace_path(target: Path | str) -> Path:
    """Authoritative manifest mirror, used when the capsule is gone."""
    return project_root(target) / "manifest.json"


def pointer(target: Path | str, version: str = VERSION) -> dict:
    """The pointer the capsule records so it can reach its global homes."""
    return {
        "schema": "tes-topology-pointer@1",
        "version": version,
        "slug": project_slug(target),
        "real_target": real_target(target),
        "runtime_root": str(runtime_root(version)),
        "project_root": str(project_root(target)),
    }


def _self_test() -> int:
    import json
    import tempfile

    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix="tes-paths-self-test-") as home:
        os.environ["TES_HOME"] = home

        # 1. TES_HOME is honored verbatim.
        if tes_home() != Path(home):
            failures.append("TES_HOME override not honored")

        with tempfile.TemporaryDirectory(prefix="tes-paths-target-") as tdir:
            a = Path(tdir) / "api"
            a.mkdir()
            # 2. Same realpath -> same slug (stable across calls).
            s1 = project_slug(a)
            s2 = project_slug(a)
            if s1 != s2:
                failures.append("slug not stable for the same realpath")

            # 3. Capsule loss does not change the slug (slug derives from realpath
            #    alone; there is no capsule on disk here at all).
            (a / ".tes").mkdir(parents=True, exist_ok=True)
            s_with_capsule = project_slug(a)
            import shutil
            shutil.rmtree(a / ".tes")
            s_without_capsule = project_slug(a)
            if s_with_capsule != s_without_capsule:
                failures.append("slug changed when the capsule was removed")

            # 4. Same basename, different path -> different slug.
            other_parent = Path(tdir) / "elsewhere"
            other_parent.mkdir()
            b = other_parent / "api"
            b.mkdir()
            if project_slug(a) == project_slug(b):
                failures.append("same-basename different-path collided to the same slug")

            # 5. Roots resolve under the global home; capsule under the repo.
            if runtime_root("9.9.9") != Path(home) / "runtime" / "9.9.9":
                failures.append("runtime_root path wrong")
            if project_root(a) != Path(home) / "projects" / project_slug(a):
                failures.append("project_root path wrong")
            if capsule_root(a) != Path(os.path.realpath(a)) / ".tes":
                failures.append("capsule_root must be <repo>/.tes")

            # 6. The pointer is self-describing and realpath-keyed.
            ptr = pointer(a)
            if ptr["slug"] != project_slug(a) or ptr["real_target"] != os.path.realpath(a):
                failures.append("pointer must carry the realpath-derived slug")

    os.environ.pop("TES_HOME", None)
    result = {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-paths:self-test] " + result["status"])
    return 0 if not failures else 1


if __name__ == "__main__":
    import sys

    if "--self-test" in sys.argv[1:]:
        raise SystemExit(_self_test())
    if "--version" in sys.argv[1:]:
        print(VERSION)
        raise SystemExit(0)
    # Default: print the resolved topology for the cwd (diagnostic).
    import json

    target = Path.cwd()
    print(json.dumps(pointer(target), indent=2, sort_keys=True))
