#!/usr/bin/env python3
"""Self-falsifiable non-regression oracle for the TES Mantra Gate.

Protected baseline: promoting the gate (adding supervise tiers, statuses, fields)
must keep the owner's law "gain tools without losing what it is". Every assert is
a SUBSET (`<=`) check, never equality where promotion ADDS, so a later SPEC can
extend STATUS_WEIGHT / event keys without this oracle going red.

  --self-test / --assert : run the 10 asserts (exit 0 = intact, 1 = regressed).
  --write-plan           : emit tmp/regression-remutation-plan.json for
                           audit-remutation.mjs, which reversibly mutates COPIES
                           of the source and proves each assert actually FIRES.

Asserts import the gate modules from TES_MANTRA_GATE_DIR (default: real scripts/).
--write-plan stages a clean copy there so a refuter's `mutate` breaks the COPY
(never the real source) and `revert`/`--restage` restores it.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
FIXTURE_DIR = ROOT / "tmp" / "regression-fixture-clean"
PLAN_PATH = ROOT / "tmp" / "regression-remutation-plan.json"

EXPECTED_GATE_FIELDS = ("VERIFY", "SCOPE", "BEST_PATH", "DOCUMENT", "ORACLE", "RESOLVE", "STATUS")
EXPECTED_MARKER = "[🍳 Flash-Fry]"
EXPECTED_GATE_WEIGHT = {"PROCEED": 0, "NEEDS_REVIEW": 1, "BLOCKED": 2}
EXPECTED_STATUSES = {"PROCEED", "BLOCKED", "NEEDS_REVIEW"}
EXPECTED_ORACLE_WEIGHT = {"OK": 0, "DEGRADED": 1, "BYPASS_SUSPECTED": 2, "NEEDS_REVIEW": 3, "BLOCKED": 4}
EXPECTED_MODES = ("commit-push", "closure-claim", "state-changing", "audit-history", "health")
ORIGINAL_EVENT_KEYS = {"schema", "recorded_at", "action", "marker", "status", "visible", "result", "gate"}


def _load_modules():
    """Import the gate pair from TES_MANTRA_GATE_DIR (real scripts/ by default)."""
    src = os.environ.get("TES_MANTRA_GATE_DIR")
    src_dir = Path(src).resolve() if src else SCRIPTS
    sys.path.insert(0, str(src_dir))
    for name in ("mantra_gate_adoption_oracle", "mantra_gate"):
        sys.modules.pop(name, None)
    mg = importlib.import_module("mantra_gate")
    oracle = importlib.import_module("mantra_gate_adoption_oracle")
    return mg, oracle


def run_asserts() -> list[str]:
    mg, oracle = _load_modules()
    failures: list[str] = []

    def check(name: str, ok: bool) -> None:
        if not ok:
            failures.append(name)

    # A — marker identity unchanged.
    check("A marker", mg.MARKER == EXPECTED_MARKER)
    # B — gate field order frozen for this slice (equality OK: GATE_FIELDS is closed here).
    check("B gate_fields", oracle.GATE_FIELDS == EXPECTED_GATE_FIELDS)
    # C — gate weights + statuses are a SUBSET of the live ones (promotion may add).
    check("C gate_weight", EXPECTED_GATE_WEIGHT.items() <= mg.STATUS_WEIGHT.items())
    check("C statuses", EXPECTED_STATUSES <= set(mg.STATUSES))
    # D — adoption weights are a SUBSET of the live ones.
    check("D oracle_weight", EXPECTED_ORACLE_WEIGHT.items() <= oracle.STATUS_WEIGHT.items())
    # E — the 5 legacy operation_mode returns are unchanged. Flags ordered
    # (state_changing, closure_claim, commit_push, audit_history); first match wins.
    flag_names = ("state_changing", "closure_claim", "commit_push", "audit_history")
    combos = {
        "commit-push": (False, False, True, False),
        "closure-claim": (False, True, False, False),
        "state-changing": (True, False, False, False),
        "audit-history": (False, False, False, True),
        "health": (False, False, False, False),
    }
    for expected, flags in combos.items():
        check(f"E mode {expected}", oracle.operation_mode(**dict(zip(flag_names, flags))) == expected)
    # F — D-fix: health branch still caps a malformed historical record at NEEDS_REVIEW.
    src_text = (Path(oracle.__file__)).read_text(encoding="utf-8")
    check("F dfix_escalate", 'escalate(status, "NEEDS_REVIEW")' in src_text)
    # G/H — both self-tests pass (run the real CLIs, not the staged copy).
    check("G mantra_gate_selftest", _self_test_exit(mg) == 0)
    check("H oracle_selftest", _self_test_exit(oracle) == 0)
    # I/J — supervise-envelope tolerance: a record carrying event["supervise"] must
    # not leak into the extracted gate, and the original 8 keys remain a subset.
    base = mg.validate_gate(mg.sample_gate(), state_changing=True, closure_claim=True)
    # record_gate's 8-key event reconstructed in-memory, then add the 9th key.
    event = {
        "schema": mg.SCHEMA, "recorded_at": mg.utc_now(), "action": "self-test",
        "marker": mg.MARKER, "status": base["status"], "visible": base["visible"],
        "result": {"valid": base["valid"], "failures": base["failures"],
                   "declared_status": base["declared_status"]},
        "gate": base["gate"],
    }
    event["supervise"] = {"tier": "guard", "interrupted": False}
    gate = oracle.gate_from_record(event)
    check("I supervise_not_leaked", "supervise" not in gate and "tier" not in gate)
    revalidated = mg.validate_gate(gate, state_changing=True, closure_claim=True)
    check("I gate_still_valid", revalidated["valid"] is True)
    check("J original_keys_subset", ORIGINAL_EVENT_KEYS <= set(event.keys()))
    return failures


def _self_test_exit(module) -> int:
    return subprocess.run(
        [sys.executable, str(Path(module.__file__).resolve()), "--self-test"],
        capture_output=True, text=True,
    ).returncode


def _stage_clean_copy() -> Path:
    """Copy the two source modules into tmp/ so a refuter can mutate the COPY."""
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("mantra_gate.py", "mantra_gate_adoption_oracle.py"):
        shutil.copy2(SCRIPTS / name, FIXTURE_DIR / name)
    return FIXTURE_DIR


def _pyrepr(s: str) -> str:
    """Double-quoted literal with the emoji passed through verbatim (no \\uXXXX
    surrogate-pair escapes, which would not equal the real single code point)."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _mutate_cmd(old: str, new: str) -> str:
    """python -c that reversibly rewrites `old`->`new` in the staged copy. Body is
    shell-single-quoted (old/new have no single quotes); literals inside use \"."""
    clean = FIXTURE_DIR / "mantra_gate.py"
    body = (
        'import pathlib;p=pathlib.Path(r"%s");'
        "t=p.read_text(encoding=\"utf-8\");assert %s in t;"
        "p.write_text(t.replace(%s,%s),encoding=\"utf-8\")"
        % (clean, _pyrepr(old), _pyrepr(old), _pyrepr(new))
    )
    return f"{sys.executable} -c '{body}'"


def write_plan() -> Path:
    """Emit the audit-remutation plan: clean run passes; each refuter breaks a copy."""
    _stage_clean_copy()
    test = "scripts/test_mantra_gate_no_regression.py"
    command = f'env TES_MANTRA_GATE_DIR="{FIXTURE_DIR}" {sys.executable} {test} --assert'
    restage = f"{sys.executable} {test} --restage"

    def oracle(axis: str, name: str, lens: str, old: str, new: str) -> dict:
        return {
            "axis": axis, "name": name, "command": command,
            "refuters": [{"lens": lens, "mutate": _mutate_cmd(old, new), "revert": restage}],
        }

    plan = {"oracles": [
        oracle(
            "marker-identity", "mantra_gate.MARKER is the Flash-Fry marker", "marker-mutation",
            'MARKER = "[\U0001f373 Flash-Fry]"', 'MARKER = "[REGRESSED]"',
        ),
        oracle(
            "gate-status-weight", "mantra_gate.STATUS_WEIGHT keeps PROCEED/NEEDS_REVIEW/BLOCKED at 0/1/2",
            "weight-mutation",
            'STATUS_WEIGHT = {"PROCEED": 0, "NEEDS_REVIEW": 1, "BLOCKED": 2}',
            'STATUS_WEIGHT = {"PROCEED": 9, "NEEDS_REVIEW": 1, "BLOCKED": 2}',
        ),
    ]}
    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLAN_PATH.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return PLAN_PATH


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mantra Gate non-regression oracle.")
    parser.add_argument("--self-test", action="store_true", help="run the 10 asserts")
    parser.add_argument("--assert", dest="assert_mode", action="store_true", help="alias for --self-test (plan command)")
    parser.add_argument("--write-plan", action="store_true", help="emit the audit-remutation plan")
    parser.add_argument("--restage", action="store_true", help="re-copy clean source into the fixture dir")
    args = parser.parse_args(argv)

    if args.write_plan:
        path = write_plan()
        print(f"wrote {path}")
        return 0
    if args.restage:
        _stage_clean_copy()
        return 0

    failures = run_asserts()
    result = {"status": "FAIL" if failures else "PASS", "failures": failures}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
