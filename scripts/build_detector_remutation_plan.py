#!/usr/bin/env python3
"""Build the DETECTOR falsifier (ADR 0006) — a re-mutation plan that proves the
``new_skill_without_packet.py`` detector FIRES on absent/incomplete packets and
SILENCES on the decoy (a second new skill that *has* a complete packet).

Distinct from the SPEC-001 non-regression plan: that one falsifies the harness's
no-regression claim and writes ``tmp/regression-remutation-plan.json``; this one
falsifies the DETECTOR and writes ``tmp/detector-remutation-plan.json``. The two
paths never collide (Tree Adversary OBJ-2).

"Affirmation is never credit": the detector earns credit only by surviving its own
falsifier, replayed by the independent ``audit-remutation.mjs`` harness.

  python3 scripts/build_detector_remutation_plan.py
      Prepare a git fixture (new staged skill, contract, complete ledger packet),
      write tmp/detector-remutation-plan.json pointing every command at that
      absolute fixture, print the plan path. exit 0.

  python3 scripts/build_detector_remutation_plan.py --self-test
      Same, then run audit-remutation.mjs over the plan and assert exit 0
      (clean PASS, both refuters fire, decoy stays OK). Print {"status":...}. exit
      0 only when the audit passes.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DETECTOR = REPO / "scripts/supervise_detectors/new_skill_without_packet.py"
AUDIT = REPO / "src/adapters/claude/skills/tes-goal-maestro/scripts/audit-remutation.mjs"
CONTRACT_SRC = REPO / "docs/governance/asset-transfer-packet.md"
PLAN_PATH = REPO / "tmp/detector-remutation-plan.json"
LEDGER_REL = ".tes/field-reports/mantra-gates.jsonl"

# The eight required packet fields (mirror the detector contract cardinality).
FIELDS = (
    "target_asset", "current_failure", "transferred_behavior", "smallest_patch",
    "proof", "regression_surface", "release_identity", "no_new_skill_evidence",
)
SKILL_REAL = "alpha"            # the real new skill under test
SKILL_DECOY = "beta"            # the decoy: another new skill WITH a complete packet


def _packet(name: str, **overrides: str) -> dict[str, object]:
    rec: dict[str, object] = {"kind": "asset_transfer_packet", "skill_name": name}
    for f in FIELDS:
        rec[f] = f"value for {f}"
    rec.update(overrides)
    return rec


def _jsonl(records: list[dict[str, object]]) -> str:
    return "".join(json.dumps(r) + "\n" for r in records)


def _git(fixture: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(fixture), *args], check=True, capture_output=True)


def build_fixture() -> Path:
    """Create an absolute git fixture: contract present, skill 'alpha' staged, and a
    complete packet for alpha in the ledger (clean state -> detector OK -> exit 0).
    The canonical clean ledger is also saved to a sidecar so reverts are exact."""
    fixture = Path(tempfile.mkdtemp(prefix="tes-detector-fixture-"))
    (fixture / f".claude/skills/{SKILL_REAL}").mkdir(parents=True)
    (fixture / f".claude/skills/{SKILL_REAL}/SKILL.md").write_text("# alpha skill\n")
    (fixture / "docs/governance").mkdir(parents=True)
    (fixture / "docs/governance/asset-transfer-packet.md").write_text(
        CONTRACT_SRC.read_text(encoding="utf-8"), encoding="utf-8")
    (fixture / ".tes/field-reports").mkdir(parents=True)

    clean = _jsonl([_packet(SKILL_REAL)])
    (fixture / LEDGER_REL).write_text(clean, encoding="utf-8")
    (fixture / ".tes/field-reports/ledger.clean.jsonl").write_text(clean, encoding="utf-8")

    _git(fixture, "init", "-q")
    _git(fixture, "config", "user.email", "fixture@tes.local")
    _git(fixture, "config", "user.name", "tes-fixture")
    _git(fixture, "add", "-A")  # stage alpha SKILL.md, contract, ledger as added
    return fixture


def build_plan(fixture: Path) -> dict[str, object]:
    """A single 'detector-drift' oracle, panel mode (quorum-with-veto), all commands
    path-safe via absolute paths. Lenses are disjoint:
      - missing-packet:    empty the ledger -> detector DRIFT (proves it FIRES).
      - incomplete-packet: blank one field    -> detector DRIFT (incompleteness != credit),
        with a NON-VACUOUS decoy: stage skill 'beta' WITH a complete packet so the
        matcher actually fires but the detector stays OK -> the DRIFT is attributable
        to the missing/incomplete packet, not to merely touching a SKILL.md.
    """
    f = str(fixture)                                   # absolute fixture dir
    ledger = str(fixture / LEDGER_REL)                 # absolute ledger
    clean = str(fixture / ".tes/field-reports/ledger.clean.jsonl")
    decoy_skill = f".claude/skills/{SKILL_DECOY}/SKILL.md"
    decoy_abs = str(fixture / decoy_skill)

    detector = f"python3 {DETECTOR} --target {f}"
    restore = f"cp {clean} {ledger}"                    # exact revert from sidecar

    # mutate the ledger via a path-safe python -c (no cwd dependence, absolute path).
    def write_ledger(records: list[dict[str, object]]) -> str:
        payload = json.dumps(_jsonl(records))
        return f"python3 -c 'import sys,io; open({json.dumps(ledger)},\"w\").write({payload})'"

    missing_mutate = f"python3 -c 'open({json.dumps(ledger)},\"w\").close()'"  # truncate
    incomplete_mutate = write_ledger([_packet(SKILL_REAL, proof="")])

    # Decoy: add a SECOND new skill 'beta' that the matcher DOES touch, but give it a
    # complete packet -> detector must stay OK. This is the non-vacuous negative control.
    decoy_mutate = " && ".join([
        f"mkdir -p {str(fixture / f'.claude/skills/{SKILL_DECOY}')}",
        f"printf '# beta skill\\n' > {decoy_abs}",
        f"git -C {f} add {decoy_skill}",
        write_ledger([_packet(SKILL_REAL), _packet(SKILL_DECOY)]),
    ])
    decoy_revert = " && ".join([
        f"git -C {f} reset -q -- {decoy_skill}",
        f"rm -f {decoy_abs}",
        restore,
    ])

    return {
        "oracles": [
            {
                "axis": "detector-drift",
                "name": "new_skill_without_packet fires on absent/incomplete packet and ignores a packeted decoy",
                "command": detector,
                "refuters": [
                    {
                        "lens": "missing-packet",
                        "mutate": missing_mutate,
                        "revert": restore,
                    },
                    {
                        "lens": "incomplete-packet",
                        "mutate": incomplete_mutate,
                        "revert": restore,
                        "decoy_mutate": decoy_mutate,
                        "decoy_revert": decoy_revert,
                    },
                ],
            }
        ]
    }


def write_plan(plan: dict[str, object]) -> Path:
    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLAN_PATH.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return PLAN_PATH


def main(argv: list[str] | None = None) -> int:
    self_test = "--self-test" in (argv if argv is not None else sys.argv[1:])
    fixture = build_fixture()
    plan = build_plan(fixture)
    write_plan(plan)

    if not self_test:
        print(str(PLAN_PATH))
        return 0

    audit = subprocess.run(
        ["node", str(AUDIT), str(PLAN_PATH)],
        capture_output=True, text=True,
    )
    sys.stderr.write(audit.stdout)
    sys.stderr.write(audit.stderr)
    status = "PASS" if audit.returncode == 0 else "FAIL"
    print(json.dumps({"status": status}))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
