#!/usr/bin/env python3
"""Certify the public TES bundle artifact and hash contract."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
import sys

import tes_bundle


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.71"


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

    with tempfile.TemporaryDirectory(prefix="tes-public-bundle-oracle-") as tempdir:
        target = Path(tempdir) / "target"
        target.mkdir()
        (target / "AGENTS.md").write_text("project-owned\n", encoding="utf-8")

        staged = tes_bundle.stage_public_bundle(
            target,
            url=bundle.resolve().as_uri(),
            expected_sha256=expected_sha,
        )
        if staged.get("status") != "STAGED":
            failures.extend(staged.get("failures", ["public bundle stage failed"]))

        plan = tes_bundle.plan_target(target)
        if plan.get("status") != "PASS":
            failures.extend(plan.get("failures", ["public bundle plan failed"]))

        applied = tes_bundle.apply_staged_bundle(target, yes=True)
        if applied.get("status") != "APPLIED":
            failures.extend(applied.get("failures", ["public bundle apply failed"]))

        if (target / "AGENTS.md").read_text(encoding="utf-8") != "project-owned\n":
            failures.append("public bundle apply overwrote project-owned AGENTS.md")
        for relpath in (
            f".tes/setup/{VERSION}/tes-bundle-manifest.json",
            ".tes/bin/tes_open_obsidian.py",
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
