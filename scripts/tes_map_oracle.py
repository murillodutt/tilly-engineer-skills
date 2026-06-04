#!/usr/bin/env python3
"""Certify the TES Project GPS helper and managed roadmap block."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import tes_map


VERSION = "0.3.162"
SCRIPT_PATH = Path(__file__).resolve()
PACKAGE_MODE = (SCRIPT_PATH.parents[1] / "package.json").exists() and SCRIPT_PATH.parent.name == "scripts"
REQUIRED_BLOCK_TERMS = (
    tes_map.START_MARKER,
    tes_map.END_MARKER,
    "Project GPS",
    "`tes-align` owns the map. `tes-map` updates the position.",
    "Position",
    "Current phase",
    "Last proven point",
    "Next irreversible step",
    "Blocking items",
    "Unknowns",
    "Confidence",
    "flowchart LR",
    "classDef done",
    "classDef current",
    "classDef next",
    "classDef later",
    "classDef deferred",
    "classDef blocked",
    "classDef unknown",
    "classDef final",
    "What changed",
    "What to do next",
    "Evidence",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_target(target: Path, require_block: bool = True) -> dict[str, Any]:
    target = target.resolve()
    roadmap = target / tes_map.ROADMAP_REL
    failures: list[str] = []
    model = tes_map.build_model(target)
    if model["status"] != tes_map.STATUS_PASS:
        failures.append(f"tes_map status is {model['status']}")
    if not roadmap.exists():
        failures.append(f"missing roadmap: {tes_map.ROADMAP_REL}")
        text = ""
    else:
        text = roadmap.read_text(encoding="utf-8")
    if require_block:
        for term in REQUIRED_BLOCK_TERMS:
            if term not in text:
                failures.append(f"missing managed block term: {term}")
    if ".obsidian/" in text or ".obsidian\\" in text:
        failures.append("roadmap block must not depend on .obsidian")
    if text.count(tes_map.START_MARKER) > 1 or text.count(tes_map.END_MARKER) > 1:
        failures.append("managed block markers must be unique")
    return {
        "status": "FAIL" if failures else "PASS",
        "version": VERSION,
        "target": str(target),
        "roadmap": str(roadmap),
        "failures": failures,
        "model_status": model["status"],
        "managed_block_present": tes_map.START_MARKER in text and tes_map.END_MARKER in text,
    }


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-map-oracle-") as tmp:
        target = Path(tmp)
        tes_map.create_fixture(target)
        roadmap = target / tes_map.ROADMAP_REL
        read_only_model = tes_map.build_model(target)
        read_only_hash = sha256(roadmap)
        if read_only_model["status"] != tes_map.STATUS_PASS:
            failures.append("read-only model did not pass")
        if sha256(roadmap) != read_only_hash:
            failures.append("read-only analysis changed roadmap")

        first = tes_map.update_roadmap(target, read_only_model)
        after_first = sha256(roadmap)
        second = tes_map.update_roadmap(target, tes_map.build_model(target))
        after_second = sha256(roadmap)
        if not first["changed"]:
            failures.append("first update did not write managed block")
        if second["changed"]:
            failures.append("second update was not idempotent")
        if after_first != after_second:
            failures.append("roadmap hash changed on second update")

        target_result = validate_target(target)
        failures.extend(f"target: {failure}" for failure in target_result["failures"])

        missing_roadmap = Path(tmp) / "missing-roadmap"
        (missing_roadmap / "docs/agents").mkdir(parents=True)
        (missing_roadmap / "docs/agents/PROJECT-CONTEXT.md").write_text(
            "# Project Context\n", encoding="utf-8"
        )
        missing_model = tes_map.build_model(missing_roadmap)
        if missing_model["status"] != tes_map.STATUS_NEEDS_ALIGN:
            failures.append("missing roadmap did not return NEEDS_ALIGN")

        missing_context = Path(tmp) / "missing-context"
        missing_context.mkdir()
        context_model = tes_map.build_model(missing_context)
        if context_model["status"] != tes_map.STATUS_NEEDS_CONTEXT:
            failures.append("missing context did not return NEEDS_CONTEXT")

        return {
            "status": "FAIL" if failures else "PASS",
            "version": VERSION,
            "self_test_mode": "package" if PACKAGE_MODE else "installed",
            "coverage": "source-package-contract" if PACKAGE_MODE else "installed-helper-contract",
            "failures": failures,
            "first": first,
            "second": second,
            "target_result": target_result,
            "missing_roadmap_status": missing_model["status"],
            "missing_context_status": context_model["status"],
        }


def run(args: argparse.Namespace) -> int:
    if args.self_test:
        result = self_test()
    else:
        result = validate_target(Path(args.target), require_block=not args.allow_missing_block)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Certify TES Project GPS output.")
    parser.add_argument("--target", default=".", help="target project root")
    parser.add_argument("--allow-missing-block", action="store_true")
    parser.add_argument("--self-test", action="store_true", help="run built-in oracle self-test")
    return parser


def main(argv: list[str] | None = None) -> int:
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
