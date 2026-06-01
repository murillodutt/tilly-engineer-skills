#!/usr/bin/env python3
"""Certify the public TES bundle artifact and hash contract."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import sys
import zipfile

import root_context
import tes_bundle


ROOT = Path(__file__).resolve().parents[1]
VERSION = tes_bundle.VERSION


def certify_public_bundle() -> dict[str, object]:
    failures: list[str] = []
    bundle = tes_bundle.public_bundle_path()
    sha_path = tes_bundle.public_sha_path()
    index_path = tes_bundle.public_index_path()

    for path in (bundle, sha_path, index_path):
        if not path.exists():
            failures.append(f"missing public bundle artifact: {path.relative_to(ROOT)}")
    if failures:
        return {"version": VERSION, "status": "FAIL", "failures": failures}

    try:
        expected_sha = tes_bundle.read_sha256_file(sha_path)
    except ValueError as exc:
        return {"version": VERSION, "status": "FAIL", "failures": [str(exc)]}

    actual_sha = tes_bundle.sha256_file(bundle)
    if actual_sha != expected_sha:
        failures.append(f"public bundle sha256 mismatch: expected {expected_sha} got {actual_sha}")

    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid public bundle index: {exc}")
        index = {}

    if index.get("schema") != "tes-public-bundle-index@1":
        failures.append("public bundle index schema must be tes-public-bundle-index@1")
    if index.get("version") != VERSION:
        failures.append(f"public bundle index version must be {VERSION}")
    if index.get("bundle") != bundle.name:
        failures.append("public bundle index bundle name mismatch")
    if index.get("sha256") != expected_sha:
        failures.append("public bundle index sha256 mismatch")
    if index.get("urls", {}).get("bundle") != tes_bundle.public_bundle_url(VERSION):
        failures.append("public bundle index URL mismatch")
    metadata = index.get("metadata")
    if not isinstance(metadata, dict):
        failures.append("public bundle index metadata must be an object")
        metadata = {}
    for key in ("source_repository", "source_commit", "created_at"):
        if not index.get(key) and not metadata.get(key):
            failures.append(f"public bundle index missing {key}")
    source_commit = str(index.get("source_commit") or metadata.get("source_commit") or "")
    if len(source_commit) != 40 or any(char not in "0123456789abcdef" for char in source_commit.lower()):
        failures.append("public bundle index source_commit must be a 40-character git SHA")

    with tempfile.TemporaryDirectory(prefix="tes-public-bundle-oracle-") as tempdir:
        extracted = Path(tempdir) / "extracted"
        with zipfile.ZipFile(bundle) as archive:
            names = set(archive.namelist())
            residue = sorted(name for name in names if tes_bundle.is_os_residue(Path(name)))
            if residue:
                failures.extend(f"public bundle includes OS residue member: {name}" for name in residue)
            for relpath in (
                "scripts/install_mcp.py",
                "scripts/tes_bundle.py",
                "scripts/tes_install.py",
                "scripts/materialize_adapter.py",
                "scripts/mantra_gate.py",
                "scripts/mantra_gate_adoption_oracle.py",
                "scripts/tes_init.py",
                "scripts/tes_map.py",
                "scripts/tes_map_oracle.py",
                "scripts/command_trigger_oracle.py",
                "tes-bundle-manifest.json",
                "tes-bundle-metadata.json",
            ):
                if relpath not in names:
                    failures.append(f"public bundle missing self-apply member: {relpath}")
            archive.extractall(extracted)

        if not failures:
            bundle_self_test = subprocess.run(
                [sys.executable, str(extracted / "scripts/tes_init.py"), "--self-test"],
                text=True,
                capture_output=True,
                check=False,
            )
            if bundle_self_test.returncode != 0:
                failures.append("extracted public bundle tes_init.py --self-test failed")
                failures.extend(bundle_self_test.stdout.splitlines())
                failures.extend(bundle_self_test.stderr.splitlines())

            extracted_target = Path(tempdir) / "extracted-target"
            extracted_target.mkdir()
            subprocess.run(["git", "init"], cwd=extracted_target, text=True, capture_output=True, check=False)
            stage_result = subprocess.run(
                [
                    sys.executable,
                    str(extracted / "scripts/tes_bundle.py"),
                    "stage",
                    "--target",
                    str(extracted_target),
                    "--bundle",
                    str(bundle),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            if stage_result.returncode != 0:
                failures.append("extracted public bundle tes_bundle.py stage failed")
                failures.extend(stage_result.stdout.splitlines())
                failures.extend(stage_result.stderr.splitlines())
            else:
                try:
                    stage_json = json.loads(stage_result.stdout)
                except json.JSONDecodeError:
                    stage_json = {}
                local_exclude = stage_json.get("local_exclude") if isinstance(stage_json, dict) else {}
                if not isinstance(local_exclude, dict) or local_exclude.get("status") != "PASS":
                    failures.append("extracted public bundle stage did not ensure local .tes/setup/ git exclusion")
                ignored = subprocess.run(
                    ["git", "check-ignore", f".tes/setup/{VERSION}/tes-bundle-manifest.json"],
                    cwd=extracted_target,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if ignored.returncode != 0:
                    failures.append("extracted public bundle setup cache is not git-ignored")
                status = subprocess.run(
                    ["git", "status", "--short", "--untracked-files=all"],
                    cwd=extracted_target,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if ".tes/setup/" in status.stdout:
                    failures.append("extracted public bundle setup cache is visible in git status")
            apply_result = subprocess.run(
                [
                    sys.executable,
                    str(extracted / "scripts/tes_bundle.py"),
                    "apply",
                    "--target",
                    str(extracted_target),
                    "--yes",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            if apply_result.returncode != 0:
                failures.append("extracted public bundle tes_bundle.py apply failed")
                failures.extend(apply_result.stdout.splitlines())
                failures.extend(apply_result.stderr.splitlines())
            for relpath in (
                ".tes/bin/install_mcp.py",
                ".tes/bin/tes_bundle.py",
                ".tes/bin/tes_install.py",
                ".tes/bin/materialize_adapter.py",
            ):
                if not (extracted_target / relpath).exists():
                    failures.append(f"extracted public bundle apply missing expected path: {relpath}")

        target = Path(tempdir) / "target"
        target.mkdir()
        subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)
        (target / "AGENTS.md").write_text("project-owned\n", encoding="utf-8")

        staged = tes_bundle.stage_public_bundle(
            target,
            url=bundle.resolve().as_uri(),
            expected_sha256=expected_sha,
        )
        if staged.get("status") != "STAGED":
            failures.extend(staged.get("failures", ["public bundle stage failed"]))
        local_exclude = staged.get("local_exclude") if isinstance(staged.get("local_exclude"), dict) else {}
        if local_exclude.get("status") != "PASS":
            failures.append("public bundle stage did not ensure local .tes/setup/ git exclusion")
        ignored = subprocess.run(
            ["git", "check-ignore", f".tes/setup/{VERSION}/tes-bundle-manifest.json"],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
        )
        if ignored.returncode != 0:
            failures.append("public bundle setup cache is not git-ignored")
        status = subprocess.run(
            ["git", "status", "--short", "--untracked-files=all"],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
        )
        if ".tes/setup/" in status.stdout:
            failures.append("public bundle setup cache is visible in git status")

        manifest = tes_bundle.read_staged_manifest(target)
        manifest_metadata = manifest.get("metadata") if isinstance(manifest.get("metadata"), dict) else {}
        if manifest_metadata.get("source_commit") != metadata.get("source_commit"):
            failures.append("staged manifest source_commit must match public index")
        if tes_bundle.validate_manifest(manifest):
            failures.extend(f"staged manifest invalid: {failure}" for failure in tes_bundle.validate_manifest(manifest))
        if not (target / f".tes/setup/{VERSION}/tes-bundle-metadata.json").exists():
            failures.append("public bundle stage missing tes-bundle-metadata.json")
        freshness = tes_bundle.certify_source_freshness(
            target,
            index=index_path,
            remote_head=str(metadata.get("source_commit") or ""),
        )
        if freshness.get("source_freshness") != "PASS":
            failures.append("public bundle freshness helper did not certify equal staged source")

        plan = tes_bundle.plan_target(target)
        if plan.get("status") != "PASS":
            failures.extend(plan.get("failures", ["public bundle plan failed"]))

        applied = tes_bundle.apply_staged_bundle(target, yes=True)
        if applied.get("status") != "CLEAN_APPLIED":
            failures.extend(applied.get("failures", ["public bundle apply failed"]))
        installed_manifest = tes_bundle.read_installed_manifest(target)
        installed_metadata = installed_manifest.get("metadata") if isinstance(installed_manifest.get("metadata"), dict) else {}
        if installed_metadata.get("source_commit") != metadata.get("source_commit"):
            failures.append("installed manifest source_commit must match public index")

        backup_id = str(applied.get("backup_id") or "")
        if not backup_id or not (target / ".tes/bk" / backup_id / "manifest.json").exists():
            failures.append("public bundle apply did not create central clean backup")
        agents_text = (target / "AGENTS.md").read_text(encoding="utf-8")
        agents_core = root_context.extract_core(agents_text)
        agents_overlay = root_context.extract_overlay(agents_text)
        if not agents_core:
            failures.append("public bundle apply did not install marked TES core in AGENTS.md")
        elif agents_core.get("sha256") != root_context.text_sha256(
            (ROOT / "src/adapters/codex/AGENTS.md").read_text(encoding="utf-8")
        ):
            failures.append("public bundle apply installed stale TES core in AGENTS.md")
        if not agents_overlay:
            failures.append("public bundle apply did not create project overlay in AGENTS.md")
        elif "project-owned" not in str(agents_overlay.get("text") or ""):
            failures.append("public bundle apply did not preserve project-owned AGENTS.md overlay")
        for relpath in (
            f".tes/setup/{VERSION}/tes-bundle-manifest.json",
            ".tes/bin/install_mcp.py",
            ".tes/bin/tes_map.py",
            ".tes/bin/tes_map_oracle.py",
            ".tes/bin/tes_open_obsidian.py",
            ".tes/bin/command_trigger_oracle.py",
            ".tes/bin/mantra_gate.py",
            ".tes/bin/mantra_gate_adoption_oracle.py",
            ".tes/bin/tes_bundle.py",
            ".tes/bin/tes_install.py",
            ".tes/bin/materialize_adapter.py",
            ".agents/skills/tes-open-obsidian/SKILL.md",
            ".claude/skills/tes-align/SKILL.md",
            ".cursor/rules/tes-runtime-capabilities.mdc",
        ):
            if not (target / relpath).exists():
                failures.append(f"public bundle apply missing expected path: {relpath}")

        mismatch = tes_bundle.stage_public_bundle(
            target,
            url=bundle.resolve().as_uri(),
            expected_sha256="0" * 64,
        )
        if mismatch.get("status") != "FAIL":
            failures.append("public bundle stage must fail on sha256 mismatch")

    return {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "bundle": str(bundle.relative_to(ROOT)),
        "sha256": actual_sha,
        "url": tes_bundle.public_bundle_url(VERSION),
        "failures": failures,
    }


def main() -> int:
    result = certify_public_bundle()
    print(json.dumps(result, indent=2))
    print("[public-bundle-oracle] " + str(result["status"]))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
