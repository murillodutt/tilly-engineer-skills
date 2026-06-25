#!/usr/bin/env python3
"""Mantra Gate senior-manager detector: new skill without a complete packet.

Detects ADR 0005 violation #1 ("no new skill by default"): a newly added
``*/skills/*/SKILL.md`` with no complete asset-transfer packet in the ledger
yields ``DRIFT_FROM_CONTRACT``. The required-field set is PARSED at runtime
from the required-fields table in the source-derived contract
``docs/governance/asset-transfer-packet.md`` (SPEC-002) via
``parse_required_fields()`` — not from any hardcoded list. Editing that
contract's table (add, remove, or rename a field) therefore moves this
detector's verdict (ADR 0006: the obligation passes through its own
falsifier). A present-but-unparseable contract degrades to ``NEEDS_REVIEW``;
it never silently falls back to a default. Born with a ``--self-test`` that
falsifies it, including a fixture that adds a ninth contract field and proves
the verdict flips.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

CONTRACT_RELPATH = "docs/governance/asset-transfer-packet.md"
SKILL_GLOB = "*/skills/*/SKILL.md"
PACKET_KIND = "asset_transfer_packet"
# Reference list of fields the contract currently fixes — used only by the
# self-test fixtures and as documentation. The validation path NEVER reads
# this: it parses the live contract via parse_required_fields(). Falling back
# to a hardcoded tuple when a contract is present would recreate the facade.
EXPECTED_FIELDS = (
    "target_asset",
    "current_failure",
    "transferred_behavior",
    "smallest_patch",
    "proof",
    "regression_surface",
    "release_identity",
    "no_new_skill_evidence",
)
# First column of a markdown table row: | `field_name` | definition |
_FIELD_ROW = re.compile(r"^\|\s*`(\w+)`\s*\|")
# Header introducing the required-fields table, e.g. "## The Eight Required Fields".
_REQUIRED_HEADER = re.compile(r"^#+\s.*required\s+fields", re.IGNORECASE)

def parse_required_fields(contract_path: Path) -> list[str]:
    """Parse the required packet field names FROM the contract, in order.

    The detector's completeness rule is whatever the contract says — not a
    hardcoded tuple. Editing the contract's required-fields table (adding,
    removing, or renaming a field) therefore moves this list and, with it,
    the detector's verdict (ADR 0006: the obligation passes through its own
    falsifier).

    Locates the first markdown table after a header containing "Required
    Fields" and extracts the backticked name in each row's first column. If
    the contract is absent, returns ``[]`` (the caller degrades honestly).
    Returns whatever the table yields; an empty list with a present contract
    means a malformed contract, which the caller reports as NEEDS_REVIEW —
    it must never silently fall back to a hardcoded default.
    """
    if not contract_path.exists():
        return []
    fields: list[str] = []
    in_required_section = False
    for line in contract_path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("#"):
            # A new header: enter the required-fields section, or (once we
            # have started collecting) a later header ends the first table.
            if _REQUIRED_HEADER.search(line):
                in_required_section = True
            elif fields:
                break
            continue
        if not in_required_section:
            continue
        match = _FIELD_ROW.match(line)
        if match:
            fields.append(match.group(1))
        elif fields:
            # Past the table (blank line or prose) once rows have started.
            break
    return fields

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

def packet_completeness(
    record: dict[str, Any], skill_name: str, required_fields: list[str]
) -> tuple[bool, list[str]]:
    """Complete iff kind matches, skill_name matches, and every field parsed
    from the contract is present and non-empty. ``required_fields`` is the
    list parsed from the contract — not a hardcoded tuple. Returns
    (matches_skill, missing_fields)."""
    if record.get("kind") != PACKET_KIND or record.get("skill_name") != skill_name:
        return False, []
    missing = [f for f in required_fields if not str(record.get(f) or "").strip()]
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
    contract_path = target / CONTRACT_RELPATH
    if not contract_path.exists():
        return _verdict("NEEDS_REVIEW", skills[0][0], "no packet contract found", [])

    # The completeness rule is whatever the contract's required-fields table
    # says — parsed live, never a hardcoded default. A present-but-unparseable
    # contract is a malformed contract, not a license to fall back.
    required_fields = parse_required_fields(contract_path)
    if not required_fields:
        return _verdict(
            "NEEDS_REVIEW", skills[0][0],
            "contract present but no required fields parseable", [],
        )

    records = load_records(target)
    for skill_name, posix in skills:
        best_missing: list[str] | None = None
        for record in records:
            matches_skill, missing = packet_completeness(record, skill_name, required_fields)
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
                list(required_fields),
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

def _complete_packet(
    skill_name: str, fields: tuple[str, ...] = EXPECTED_FIELDS, **overrides: Any
) -> dict[str, Any]:
    packet: dict[str, Any] = {"kind": PACKET_KIND, "skill_name": skill_name}
    for field in fields:
        packet[field] = f"value for {field}"
    packet.update(overrides)
    return packet

def _write_ledger(target: Path, records: list[dict[str, Any]]) -> None:
    ledger = target / ".tes/field-reports/mantra-gates.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")

def _write_contract(target: Path, fields: tuple[str, ...] = EXPECTED_FIELDS) -> None:
    """Write a tmpdir contract whose required-fields table lists ``fields``.

    The detector parses this table, so the table — not a hardcoded tuple — is
    what the fixtures vary. The cardinality fixture appends a ninth row here
    and watches the verdict move; it never touches the real contract.
    """
    contract = target / CONTRACT_RELPATH
    contract.parent.mkdir(parents=True, exist_ok=True)
    rows = "\n".join(f"| `{f}` | definition of {f} |" for f in fields)
    contract.write_text(
        "# Asset Transfer Packet Contract\n\n"
        "## The Required Fields\n\n"
        "| Field | Definition |\n"
        "|-------|-----------|\n"
        f"{rows}\n",
        encoding="utf-8",
    )

def self_test() -> dict[str, Any]:
    """Six fixtures falsify the detector: it must fire on absent/incomplete
    packets, clear on a complete one, stay silent off-scope, degrade honestly
    when the contract is missing, and — the acceptance test the auditor used —
    flip its verdict when the contract's required-fields cardinality changes
    while the packet stays the same. Each runs in its own tmpdir; none touches
    the real contract."""
    skill = "my-new-skill"
    staged = [f".claude/skills/{skill}/SKILL.md"]
    failures: list[str] = []
    ninth = EXPECTED_FIELDS + ("ninth_field",)

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
        # 6a. 8-field contract + matching 8-field packet -> OK (the baseline
        #     the auditor mutated). Same as case 2, stated for the pair below.
        (lambda t: (_write_contract(t, EXPECTED_FIELDS),
                    _write_ledger(t, [_complete_packet(skill, EXPECTED_FIELDS)])),
         staged, "OK", "__skip__"),
        # 6b. Add a NINTH row to the contract table; the SAME 8-field packet
        #     now drifts, missing exactly ninth_field. Editing the contract
        #     moved the verdict -> the facade is repaired (proves the auditor's
        #     re-mutation now flips). Removing the row (6a) returns OK.
        (lambda t: (_write_contract(t, ninth),
                    _write_ledger(t, [_complete_packet(skill, EXPECTED_FIELDS)])),
         staged, "DRIFT_FROM_CONTRACT", ["ninth_field"]),
        # 7. contract present but no parseable required-fields table ->
        #    NEEDS_REVIEW (malformed contract never silently uses a default).
        (lambda t: (t / CONTRACT_RELPATH).parent.mkdir(parents=True, exist_ok=True)
         or (t / CONTRACT_RELPATH).write_text("# Contract\n\nno table here\n", encoding="utf-8"),
         staged, "NEEDS_REVIEW", "__skip__"),
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
