#!/usr/bin/env python3
"""Mantra Gate senior-manager detector: new skill without a complete packet.

Detects ADR 0005 violation #1 ("no new skill by default"): a newly added
``*/skills/*/SKILL.md`` with no complete asset-transfer packet in the ledger
yields ``DRIFT_FROM_CONTRACT``. Completeness is read from the source-derived
contract ``docs/governance/asset-transfer-packet.md`` (SPEC-002), so editing
that contract moves this detector's verdict (ADR 0006: the obligation passes
through its own falsifier). Born with a ``--self-test`` that falsifies it.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

CONTRACT_RELPATH = "docs/governance/asset-transfer-packet.md"
SKILL_GLOB = "*/skills/*/SKILL.md"
PACKET_KIND = "asset_transfer_packet"
# The eight required packet fields (contract cardinality).
REQUIRED_FIELDS = (
    "target_asset",
    "current_failure",
    "transferred_behavior",
    "smallest_patch",
    "proof",
    "regression_surface",
    "release_identity",
    "no_new_skill_evidence",
)

def record_paths(target: Path) -> list[Path]:
    """Mirror mantra_gate_adoption_oracle.record_paths()."""
    return [
        target / ".tes/field-reports/mantra-gates.jsonl",
        target / ".tes/mantra-gates/records.jsonl",
    ]

def load_records(target: Path) -> list[dict[str, Any]]:
    """Mirror load_records(): one JSON per line, blank/undecodable lines skipped."""
    records: list[dict[str, Any]] = []
    for path in record_paths(target):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                records.append(event)
    return records

def git_added_paths(target: Path) -> list[str]:
    """Added (--diff-filter=A) staged paths — newly added SKILL.md only."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=A", "-z"],
        cwd=target,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [raw.decode("utf-8") for raw in result.stdout.split(b"\0") if raw]

def staged_skill_names(staged_paths: list[str]) -> list[tuple[str, str]]:
    """(skill_name, posix_path) for each added */skills/*/SKILL.md."""
    matched: list[tuple[str, str]] = []
    for raw in staged_paths:
        posix = Path(raw).as_posix()
        if fnmatch.fnmatch(posix, SKILL_GLOB):
            matched.append((Path(posix).parent.name, posix))
    return matched

def packet_completeness(record: dict[str, Any], skill_name: str) -> tuple[bool, list[str]]:
    """Complete iff kind matches, skill_name matches, and all eight fields are
    present and non-empty. Returns (matches_skill, missing_fields)."""
    if record.get("kind") != PACKET_KIND or record.get("skill_name") != skill_name:
        return False, []
    missing = [f for f in REQUIRED_FIELDS if not str(record.get(f) or "").strip()]
    return True, missing

def _verdict(status: str, skill: str | None, reason: str, missing: list[str]) -> dict[str, Any]:
    return {"status": status, "skill": skill, "reason": reason, "missing_fields": missing}

def evaluate(target: Path, *, staged_paths: list[str] | None = None) -> dict[str, Any]:
    target = Path(target)
    if staged_paths is None:
        staged_paths = git_added_paths(target)
    skills = staged_skill_names(staged_paths)

    if not skills:
        return _verdict("OK", None, "no newly added */skills/*/SKILL.md in staged set", [])

    # A skill is introduced. With no contract we cannot cite a completeness
    # rule — degrade honestly rather than false-OK.
    if not (target / CONTRACT_RELPATH).exists():
        return _verdict("NEEDS_REVIEW", skills[0][0], "no packet contract found", [])

    records = load_records(target)
    for skill_name, posix in skills:
        best_missing: list[str] | None = None
        for record in records:
            matches_skill, missing = packet_completeness(record, skill_name)
            if not matches_skill:
                continue
            if not missing:
                best_missing = []
                break
            if best_missing is None or len(missing) < len(best_missing):
                best_missing = missing

        if best_missing == []:
            continue  # complete packet clears this skill
        if best_missing is None:
            return _verdict(
                "DRIFT_FROM_CONTRACT", skill_name,
                f"new skill {posix} has no asset-transfer packet in the ledger",
                list(REQUIRED_FIELDS),
            )
        return _verdict(
            "DRIFT_FROM_CONTRACT", skill_name,
            f"new skill {posix} has an incomplete asset-transfer packet",
            best_missing,
        )

    return _verdict(
        "OK", skills[0][0],
        "every newly added skill has a complete asset-transfer packet", [],
    )

def _complete_packet(skill_name: str, **overrides: Any) -> dict[str, Any]:
    packet: dict[str, Any] = {"kind": PACKET_KIND, "skill_name": skill_name}
    for field in REQUIRED_FIELDS:
        packet[field] = f"value for {field}"
    packet.update(overrides)
    return packet

def _write_ledger(target: Path, records: list[dict[str, Any]]) -> None:
    ledger = target / ".tes/field-reports/mantra-gates.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")

def _write_contract(target: Path) -> None:
    contract = target / CONTRACT_RELPATH
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_text("# Asset Transfer Packet Contract\n", encoding="utf-8")

def self_test() -> dict[str, Any]:
    """Five fixtures falsify the detector: it must fire on absent/incomplete
    packets, clear on a complete one, stay silent off-scope, and degrade
    honestly when the contract is missing. Each runs in its own tmpdir."""
    skill = "my-new-skill"
    staged = [f".claude/skills/{skill}/SKILL.md"]
    failures: list[str] = []

    def run(setup, staged_paths, want_status, want_missing="__skip__"):
        with tempfile.TemporaryDirectory(prefix="tes-detector-") as tmp:
            target = Path(tmp)
            setup(target)
            result = evaluate(target, staged_paths=staged_paths)
            if result["status"] != want_status:
                return f"want {want_status}, got {result['status']} ({result['reason']})"
            if want_missing != "__skip__" and result["missing_fields"] != want_missing:
                return f"want missing {want_missing}, got {result['missing_fields']}"
            return None

    cases = [
        # 1. new skill + no packet -> DRIFT (the detector fires).
        (_write_contract, staged, "DRIFT_FROM_CONTRACT", "__skip__"),
        # 2. new skill + complete packet -> OK (clears).
        (lambda t: (_write_contract(t), _write_ledger(t, [_complete_packet(skill)])),
         staged, "OK", "__skip__"),
        # 3. new skill + incomplete packet (one field missing) -> DRIFT, names it.
        (lambda t: (_write_contract(t), _write_ledger(t, [_complete_packet(skill, proof="")])),
         staged, "DRIFT_FROM_CONTRACT", ["proof"]),
        # 4. no SKILL.md staged -> OK (anti-cry-wolf).
        (_write_contract, ["scripts/x.py", "docs/n.md"], "OK", "__skip__"),
        # 5. contract absent -> NEEDS_REVIEW (degrade honest, never false OK).
        (lambda t: None, staged, "NEEDS_REVIEW", "__skip__"),
    ]
    for index, (setup, paths, want, want_missing) in enumerate(cases, start=1):
        error = run(setup, paths, want, want_missing)
        if error:
            failures.append(f"case {index}: {error}")

    return {"status": "FAIL" if failures else "PASS", "failures": failures}

EXIT_CODES = {"OK": 0, "DRIFT_FROM_CONTRACT": 1, "NEEDS_REVIEW": 2}

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Detect a newly added skill without a complete asset-transfer packet.")
    parser.add_argument("--target", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--staged", nargs="*", default=None, help="optional staged paths (testing); omit to discover via git")
    args = parser.parse_args(argv)

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "PASS" else 1

    result = evaluate(args.target, staged_paths=args.staged)
    print(json.dumps(result, indent=2, sort_keys=True))
    return EXIT_CODES[result["status"]]

if __name__ == "__main__":
    sys.exit(main())
