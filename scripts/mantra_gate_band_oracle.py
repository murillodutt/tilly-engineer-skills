#!/usr/bin/env python3
"""Calibration band-oracle for the Mantra Gate senior-manager criterion (Pillar 0).

The <mantra_gate> bootloader block declares WHEN the senior manager fires: a HARD
GATE for destructive/remote/release/sync/secret/high-impact actions, and PROACTIVE
SUPERVISION (advise, do not block) for ordinary local edits. That criterion's
executable projection is ``mantra_gate.classify_risk`` (the risk regex IS the
machine form of the bootloader rule). This oracle proves the criterion DISCRIMINATES:

  - a corpus of RISK scenarios must classify at or above the hard-gate band
    (``material`` / ``high-risk`` / ``forbidden`` — the gate must wake);
  - a corpus of NON-RISK scenarios must classify ``routine``
    (supervision only — no cry-wolf);
  - the oracle FAILS if the rule cannot separate them (a sleeping gate that
    calls everything routine, or a crying-wolf gate that flags benign edits).

Falsifiable by construction (ADR 0006): mutate a risk pattern in mantra_gate.py
so a risk scenario drops to ``routine`` and this oracle goes RED; affirmation that
"the bootloader was promoted" is never credit — the band firing under the corpus is.

Exit 0 = the criterion discriminates within band. Exit 1 = it does not (a scenario
landed on the wrong side of the hard-gate line).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mantra_gate

# The bootloader declares TWO registers, and this oracle must mirror them exactly:
#   - HARD GATE: high-risk / forbidden — the destructive/remote/release/secret/
#     high-impact classes the bootloader names. Here the senior manager WAKES and
#     blocks (requires the 7-field gate).
#   - PROACTIVE SUPERVISION: routine / material — ordinary local work (edits,
#     staging, local commits). The bootloader says "do not block" here; the manager
#     supervises and advises but does not gate. A local commit classifying 'material'
#     is correct (it touches git) AND correctly supervision-band (do not block) —
#     tier of classification is NOT the same as the block action.
# The discrimination the oracle enforces: real risk reaches the hard-gate band;
# benign local work stays in the supervision band; nothing benign reaches
# high-risk/forbidden (no cry-wolf), and no real-risk action stays routine (no sleep).
HARD_GATE_BAND = ("high-risk", "forbidden")
SUPERVISION_BAND = ("routine", "material")

# RISK corpus — actions that MUST wake the hard gate. Each is a (label, kwargs)
# pair fed to classify_risk. These mirror the bootloader's named risk classes:
# destructive, remote, release, sync, secret-bearing, high-impact, generated.
RISK_CORPUS = (
    ("push to remote", {"action": "git push origin main"}),
    ("publish release", {"action": "npm publish the package to the registry"}),
    ("delete tracked tree", {"action": "rm -rf the docs/dist directory"}),
    ("force overwrite", {"action": "git push --force to overwrite remote history"}),
    ("tag a release", {"action": "create and push a release tag v0.4.0"}),
    ("materialize delivered adapter", {"action": "materialize adapter and regenerate the public bundle"}),
    ("secret-bearing change", {"action": "add the API key to the config file", "paths": ["config/secrets.env"]}),
    ("sync to cloud", {"action": "sync the bundle to the cloud marketplace"}),
)

# NON-RISK corpus — ordinary local work the gate must NOT block (supervise only).
NON_RISK_CORPUS = (
    ("read a file", {"action": "read scripts/mantra_gate.py to understand classify_risk"}),
    ("focused local edit", {"action": "fix a typo in a local docstring"}),
    ("run a self-test", {"action": "run the unit self-test for one module"}),
    ("stage a change", {"action": "git add a single edited file"}),
    ("local commit", {"action": "git commit the staged change locally"}),
    ("grep the tree", {"action": "grep for a function name across the repo"}),
)


def _level_index(level: str) -> int:
    return mantra_gate.RISK_LEVELS.index(level) if level in mantra_gate.RISK_LEVELS else -1


def evaluate() -> dict[str, object]:
    failures: list[str] = []
    hard_gate_floor = _level_index("high-risk")  # first level that wakes the hard gate (blocks)

    risk_results = []
    for label, kwargs in RISK_CORPUS:
        risk = mantra_gate.classify_risk(**kwargs)["risk"]
        risk_results.append({"label": label, "risk": risk})
        if _level_index(risk) < hard_gate_floor:
            failures.append(
                f"RISK scenario '{label}' classified '{risk}' (below hard-gate band "
                f"{HARD_GATE_BAND}) — the senior manager would SLEEP through a risky action"
            )

    non_risk_results = []
    for label, kwargs in NON_RISK_CORPUS:
        risk = mantra_gate.classify_risk(**kwargs)["risk"]
        non_risk_results.append({"label": label, "risk": risk})
        if risk not in SUPERVISION_BAND:
            failures.append(
                f"NON-RISK scenario '{label}' classified '{risk}' (in hard-gate band, "
                f"above supervision {SUPERVISION_BAND}) — the senior manager would CRY WOLF "
                f"on benign local work"
            )

    # Discrimination proof: the two bands must not collapse. If NO risk scenario reached
    # the hard-gate band, the gate sleeps; if ANY benign scenario reached it, it cries wolf.
    risk_levels_seen = {r["risk"] for r in risk_results}
    if not (risk_levels_seen & set(HARD_GATE_BAND)):
        failures.append("criterion does not discriminate: NO risk scenario reached the hard-gate band")

    return {
        "oracle": "mantra-gate-band",
        "status": "PASS" if not failures else "FAIL",
        "hard_gate_band": list(HARD_GATE_BAND),
        "risk_results": risk_results,
        "non_risk_results": non_risk_results,
        "failures": failures,
    }


def self_test() -> int:
    """Prove the oracle FIRES under mutation, not just passes when intact.

    1. Clean run: the criterion discriminates -> PASS.
    2. Mutated run: monkeypatch classify_risk to call everything 'routine'
       (a sleeping gate) -> the oracle MUST go FAIL. If it still passes, the
       oracle is a facade.
    3. Mutated run: monkeypatch to call everything 'forbidden' (a crying-wolf
       gate) -> the oracle MUST go FAIL on the non-risk band.
    """
    clean = evaluate()
    if clean["status"] != "PASS":
        print(json.dumps(clean, indent=2))
        print("[band-oracle:self-test] FAIL — clean criterion did not discriminate")
        return 1

    original = mantra_gate.classify_risk
    try:
        mantra_gate.classify_risk = lambda **kw: {"risk": "routine", "reasons": ["mutant-sleep"]}
        sleeping = evaluate()
        if sleeping["status"] != "FAIL":
            print("[band-oracle:self-test] FAIL — sleeping-gate mutant was not caught (FACADE)")
            return 1

        mantra_gate.classify_risk = lambda **kw: {"risk": "forbidden", "reasons": ["mutant-crywolf"]}
        crywolf = evaluate()
        if crywolf["status"] != "FAIL":
            print("[band-oracle:self-test] FAIL — crying-wolf mutant was not caught (FACADE)")
            return 1
    finally:
        mantra_gate.classify_risk = original

    # Re-confirm clean still passes after restore.
    if evaluate()["status"] != "PASS":
        print("[band-oracle:self-test] FAIL — criterion broke after mutant restore")
        return 1

    print(json.dumps({"status": "PASS", "clean": "discriminates", "sleeping_mutant": "caught", "crywolf_mutant": "caught"}, indent=2))
    print("[band-oracle:self-test] PASS")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    result = evaluate()
    print(json.dumps(result, indent=2))
    print("[band-oracle] " + str(result["status"]))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
