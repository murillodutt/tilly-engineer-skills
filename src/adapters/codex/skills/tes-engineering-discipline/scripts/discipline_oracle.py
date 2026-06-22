#!/usr/bin/env python3
"""Small deterministic oracle for Tilly Engineering Discipline."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


REQUIRED_TERMS = (
    "Assumptions visible",
    "Scope smaller",
    "Edits surgical",
    "Success falsifiable",
    "E = A * S * C * V",
    "Maturity Layer Gate",
    "Birth",
    "Consolidation",
    "Evolution",
    "Platform",
    "Fit First",
    "promotion evidence",
    "protected baseline",
    "allowed complexity",
    "forbidden complexity",
    "Mantra Gate",
    "[🍳 Flash-Fry]",
    "VERIFY -> SCOPE -> BEST_PATH -> DOCUMENT -> ORACLE -> RESOLVE -> STATUS",
    "Infrastructure Decision Gate",
    "Stack Surface Scan",
    "Context7 or official documentation",
    "runtime-bound dependencies",
    "Declared-Contract Arbiter",
    "Effort Gate",
    "Standard",
    "Premium",
    "Escalate-collision",
    "focused_proof",
    "red-capable proof",
    "broad closure gate",
)

PLAN_FIELDS = (
    "assumptions",
    "ambiguity",
    "maturity_layer",
    "promotion_evidence",
    "protected_baseline",
    "stack_surface",
    "simplest_path",
    "allowed_complexity",
    "forbidden_complexity",
    "deleted_scope",
    "oracle",
    "effort_tier",
    "consequence_evidence",
    "declared_contract",
    "named_consequence_surface",
    "focused_proof",
)

# Effort-axis fields are recognized by the parser but optional in a plan: a plan
# that names no effort tier defaults to Standard, and an absent declared_contract
# or named_consequence_surface is legal ("none"). They are exempt from the
# mandatory missing-field sweep and validated only by the Effort Gate block below
# when present.
EFFORT_FIELDS = (
    "effort_tier",
    "consequence_evidence",
    "declared_contract",
    "named_consequence_surface",
)

OPTIONAL_PLAN_FIELDS = (*EFFORT_FIELDS, "focused_proof")

VALID_LAYERS = ("birth", "consolidation", "evolution", "platform")
GENERIC_VALUES = {
    "as needed",
    "as appropriate",
    "everything",
    "good system",
    "later",
    "n/a",
    "na",
    "none",
    "ok",
    "oracle",
    "relevant",
    "same",
    "test",
    "tests",
    "the whole thing",
    "tbd",
    "todo",
    "unknown",
}
ORACLE_SIGNALS = (
    "build",
    "bun ",
    "check",
    "fixture",
    "lint",
    "npm ",
    "oracle",
    "pytest",
    "python",
    "reproducer",
    "run ",
    "test",
    "typecheck",
)

BROAD_CLOSURE_ORACLE_SIGNALS = (
    "commit:check",
    "validate_reference_package.py",
    "validate_tds.py",
    "git diff --check",
    "full closure",
    "package validation",
    "reference package",
)

RED_CAPABLE_PROOF_SIGNALS = (
    "assert",
    "behavior",
    "boundary",
    "declared interface",
    "fixture",
    "focused",
    "golden",
    "public interface",
    "regression",
    "reproducer",
    "same-input",
    "specific",
)

# The effort axis resolves binary-hard, mirroring the maturity layer: a plan
# names exactly one tier or it defaults to Standard; a partial tier is rejected.
VALID_TIERS = ("standard", "premium")

# A declared contract is one an oracle could name from source WITHOUT running it.
# Exactly four source-nameable types (see Gate Zero in the skill). A plan resolves
# to exactly one type or it is absent — never "partial".
DECLARED_CONTRACT_TYPES = (
    "frozen-schema cardinality",
    "closed-domain coverage",
    "peer-convergence",
    "affordance-deliverable",
)

# Legal ways a plan states it has NO declared contract on the path. Absence is a
# valid answer (the broad default wins), not a missing field.
CONTRACT_ABSENT = {"none", "no declared contract", "n/a", "na", "absent"}

# Named consequence surfaces are the SECOND Premium trigger, co-equal in hardness
# with a declared contract. They are NOT substrings searched over free prose (that
# fragile deny-list is exactly what this change retires); they are a DECLARED enum
# the author must name. The field resolves binary-hard to exactly one surface, or
# is absent, or — when something is declared that matches no known surface — fails
# as NEEDS_REVIEW (the curation signal). "irreversible-migration" carries the one
# near-adjective, justified as a checkable property (revert+redeploy cannot undo
# it before a reader sees it), not a feeling. This enum, like any enum, needs
# governance curation over time — but a declared enum that resolves binary-hard is
# a contract, not a substring match.
NAMED_CONSEQUENCE_SURFACES = (
    "credit-decision-threshold",
    "ledger-row",
    "auth-issuance",
    "irreversible-migration",
    "pii-export-surface",
)

# Legal ways a plan states it names NO consequence surface on the path. Absence is
# a valid answer (the surface is simply not a Premium trigger here), not garbage.
SURFACE_ABSENT = {"none", "no named consequence surface", "n/a", "na", "absent"}

# Pure-weasel adjectives that are NOT a declared contract or a named consequence.
# A plan whose consequence_evidence is only weasel content leaves the tier at
# Standard; a real consequence co-occurring with a weasel word still passes.
EFFORT_WEASEL = (
    "important",
    "sensitive",
    "premium-looking",
    "could be nicer",
    "deserves polish",
    "feels important",
    "more thorough",
    "nicer",
    "polish",
)


def normalize(value: str) -> str:
    return " ".join(value.lower().strip().split())


def parse_plan_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    current: str | None = None
    field_names = set(PLAN_FIELDS)
    pattern = re.compile(r"^\s*([A-Za-z_]+)\s*:\s*(.*)$")

    for line in text.splitlines():
        match = pattern.match(line)
        if match and match.group(1).lower() in field_names:
            current = match.group(1).lower()
            fields[current] = match.group(2).strip()
            continue

        if current and (line.startswith(" ") or line.strip().startswith(("-", "*"))):
            value = line.strip().lstrip("-*").strip()
            if value:
                fields[current] = f"{fields[current]} {value}".strip()
            continue

        if line.strip() and not line.startswith(" "):
            current = None

    return fields


def is_generic(value: str, *, allow_birth_none: bool = False, allow_none: bool = False) -> bool:
    normalized = normalize(value)
    if not normalized:
        return True
    if allow_birth_none and normalized in {"none", "no higher-layer evidence", "default birth"}:
        return False
    # Some fields legitimately answer "none" to mean "nothing to declare" (e.g.
    # ambiguity: no unresolved question). For those, a bare "none"/"n/a" is an
    # honest answer, not empty-or-generic — the same exemption promotion_evidence
    # already gets in Birth.
    if allow_none and normalized in {"none", "n/a", "na"}:
        return False
    if normalized in GENERIC_VALUES:
        return True
    return False


def selected_layer(value: str) -> str | None:
    normalized = normalize(value)
    matches = [layer for layer in VALID_LAYERS if layer in normalized.split()]
    if len(matches) == 1:
        return matches[0]
    if normalized in VALID_LAYERS:
        return normalized
    return None


def selected_tier(value: str) -> str | None:
    """Resolve the effort tier binary-hard, mirroring selected_layer.

    Exactly one of Standard/Premium or None. A value naming both, or neither,
    returns None so the caller can fail it as NEEDS_REVIEW (no "partially
    Premium" state). An empty value is handled by the caller as the Standard
    default.
    """
    normalized = normalize(value)
    matches = [tier for tier in VALID_TIERS if tier in normalized.split()]
    if len(matches) == 1:
        return matches[0]
    if normalized in VALID_TIERS:
        return normalized
    return None


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9-]+", text.lower()))


def signal_present(text: str, signals) -> bool:
    """Word-boundary match: single-word signals match by token-set membership
    (so "drop" never fires on "dropdown"); multi-word/hyphenated signals match
    by substring on the normalized text."""
    normalized = normalize(text)
    tokens = _tokens(normalized)
    for signal in signals:
        if " " in signal or "-" in signal:
            if signal in normalized:
                return True
        elif signal in tokens:
            return True
    return False


def oracle_is_broad_closure(value: str) -> bool:
    normalized = normalize(value)
    return any(signal in normalized for signal in BROAD_CLOSURE_ORACLE_SIGNALS)


def has_red_capable_proof(value: str) -> bool:
    return signal_present(value, RED_CAPABLE_PROOF_SIGNALS)


def declared_contract(value: str) -> str | None:
    """Resolve the declared contract to exactly one type, absent, or NEEDS_REVIEW.

    Returns the matched type name, the sentinel "absent" when the plan states no
    contract is on the path, or None when the value is non-empty but does not
    resolve to exactly one known type (caller fails it as NEEDS_REVIEW). Absence
    is legal — the broad default wins — and is never a missing field.
    """
    normalized = normalize(value)
    if not normalized or normalized in CONTRACT_ABSENT:
        return "absent"
    matches = [t for t in DECLARED_CONTRACT_TYPES if t in normalized]
    if len(matches) == 1:
        return matches[0]
    return None


def named_consequence_surface(value: str) -> str | None:
    """Resolve the named consequence surface to one enum value, absent, or None.

    Co-equal in hardness with declared_contract and resolved the same way: exactly
    one named surface, the sentinel "absent" when none is named, or None when
    something IS declared but matches no known surface (caller fails it as
    NEEDS_REVIEW — the curation signal). A surface is a DECLARED field, never a
    substring the matcher hunts in free prose.
    """
    normalized = normalize(value)
    if not normalized or normalized in SURFACE_ABSENT:
        return "absent"
    matches = [s for s in NAMED_CONSEQUENCE_SURFACES if s in normalized]
    if len(matches) == 1:
        return matches[0]
    return None


def is_only_weasel(text: str) -> bool:
    """True when the value is weasel-or-empty content with no substance.

    Used only as a quality guard on consequence_evidence prose; it is NOT a Premium
    trigger (the triggers are the declared_contract and named_consequence_surface
    enums). An empty value, or one that carries a weasel phrase, is weasel."""
    if not normalize(text):
        return True
    return signal_present(text, EFFORT_WEASEL)


def validate_plan_text(text: str) -> list[str]:
    failures: list[str] = []
    lowered = text.lower()
    fields = parse_plan_fields(text)

    # Effort-axis fields are optional: a plan may omit them entirely (Standard
    # default, no declared contract). Only the original mandatory fields are
    # swept for presence and generic content.
    mandatory_fields = tuple(f for f in PLAN_FIELDS if f not in OPTIONAL_PLAN_FIELDS)

    for field in mandatory_fields:
        if field not in lowered:
            failures.append(f"plan missing field: {field}")
        if field not in fields:
            failures.append(f"plan missing structured value: {field}")

    if failures:
        return failures

    layer = selected_layer(fields["maturity_layer"])
    if layer is None:
        failures.append("maturity_layer must be exactly one of Birth, Consolidation, Evolution, or Platform")
        layer = "unknown"

    for field in mandatory_fields:
        allow_birth_none = field == "promotion_evidence" and layer == "birth"
        allow_none = field == "ambiguity"
        if is_generic(fields[field], allow_birth_none=allow_birth_none, allow_none=allow_none):
            failures.append(f"plan field is empty or generic: {field}")

    if layer != "birth":
        for field in (
            "promotion_evidence",
            "protected_baseline",
            "allowed_complexity",
            "forbidden_complexity",
        ):
            if normalize(fields[field]) in {"none", "no higher-layer evidence", "default birth"}:
                failures.append(f"{field} cannot be none outside Birth")

    oracle = normalize(fields["oracle"])
    if not any(signal in f" {oracle} " for signal in ORACLE_SIGNALS):
        failures.append("oracle must name a falsifiable command, test, fixture, or check")
    focused_proof = fields.get("focused_proof", "")
    if oracle_is_broad_closure(fields["oracle"]) and not has_red_capable_proof(focused_proof):
        failures.append(
            "broad closure gate requires focused_proof with a red-capable fixture, "
            "reproducer, assertion, boundary, or interface-specific regression check"
        )

    # Effort Gate (Stage A): validate the effort tier and its two DECLARED, binary-
    # hard triggers. This does NOT detect a violation in a diff — it validates that
    # the plan DECLARES a named trigger. Both triggers are first-class enums: a
    # declared_contract resolving to one of four structural types, OR a
    # named_consequence_surface resolving to one named surface. Neither is a
    # substring searched over free prose, and neither is co-equal with mere
    # rejection of weasel content.
    tier_value = fields.get("effort_tier", "")
    tier = "standard" if not normalize(tier_value) else selected_tier(tier_value)
    if tier is None:
        failures.append("effort_tier must resolve to exactly one of Standard or Premium")
        tier = "standard"

    contract = declared_contract(fields.get("declared_contract", ""))
    if contract is None:
        failures.append(
            "declared_contract must resolve to exactly one declared type "
            "(frozen-schema cardinality, closed-domain coverage, peer-convergence, "
            "affordance-deliverable) or be absent"
        )

    surface = named_consequence_surface(fields.get("named_consequence_surface", ""))
    if surface is None:
        failures.append(
            "named_consequence_surface must resolve to exactly one named surface "
            "(credit-decision-threshold, ledger-row, auth-issuance, "
            "irreversible-migration) or be absent"
        )

    # A named trigger is present when EITHER enum resolved to a real value (not the
    # "absent" sentinel and not the None NEEDS_REVIEW state). This is the single
    # source of Premium authority — co-equal in hardness across both triggers.
    has_named_trigger = (
        contract not in (None, "absent")
        or surface not in (None, "absent")
    )

    consequence = fields.get("consequence_evidence", "")
    if tier == "premium":
        # Positive floor: Premium MUST name at least one declared trigger. Rejecting
        # weasel prose is not a floor; requiring a named fact is. With no named
        # trigger, Premium fails as NEEDS_REVIEW — the same way selected_layer
        # requires one enum, not the absence of garbage.
        if not has_named_trigger:
            failures.append(
                "Premium effort requires a named declared trigger: a declared_contract "
                "that resolves to one of the four types, or a named_consequence_surface "
                "that resolves to one named surface. Neither was named; fails as "
                "NEEDS_REVIEW"
            )
        # Quality guard on the optional prose: if consequence_evidence is supplied at
        # all, it must not be generic or pure-weasel. It is description, not a trigger.
        elif normalize(consequence) and (is_generic(consequence) or is_only_weasel(consequence)):
            failures.append(
                "Premium consequence_evidence, when supplied, must describe the named "
                "trigger, not a generic or weasel value"
            )
    else:
        # UNDER_EFFORT: a named declared trigger is present but the tier is Standard
        # — under-rigor on a contract line. Promote to Premium or drop the trigger.
        if has_named_trigger:
            failures.append(
                "UNDER_EFFORT: a declared contract or named consequence surface is "
                "named but the effort tier is Standard; promote to Premium"
            )

    return failures


def semantic_self_test() -> list[str]:
    valid_plan = """
engineering_discipline:
  assumptions: adapter contract already exists
  ambiguity: no unresolved authority conflict
  maturity_layer: Evolution
  promotion_evidence: accepted adapter contract used by existing installs
  protected_baseline: compatibility interface behavior
  stack_surface: adapter source and parity oracle
  simplest_path: keep the interface and simplify internals behind it
  allowed_complexity: compatibility wrapper stays in place
  forbidden_complexity: deleting the interface or adding a plugin framework
  deleted_scope: broad adapter redesign
  oracle: python3 scripts/adapter_parity_readiness.py
"""
    vague_plan = """
engineering_discipline:
  assumptions: ok
  ambiguity: ok
  maturity_layer: Evolution
  promotion_evidence: good system
  protected_baseline: the whole thing
  stack_surface: relevant
  simplest_path: as needed
  allowed_complexity: as needed
  forbidden_complexity: same
  deleted_scope: later
  oracle: maybe
"""
    # Real arbiter fixture (frozen-schema persist defect). declared_contract
    # resolves to a real type; the consequence prose is NEUTRAL (no token doing the
    # work). PASSES. The crucial property — tested below — is that stripping the
    # declared_contract to absent makes the SAME plan FAIL. If it passed identically
    # without the trigger, it would prove nothing.
    real_arbiter_premium_plan = """
engineering_discipline:
  assumptions: persist path round-trips a frozen schema before save
  ambiguity: no unresolved authority conflict
  maturity_layer: Birth
  promotion_evidence: none
  protected_baseline: the existing persist function behavior
  stack_surface: the single persist function and its schema
  simplest_path: replace the JSON round-trip with a field-preserving clone
  allowed_complexity: a structural clone on the one path
  forbidden_complexity: a serializer abstraction, factory, or config knob
  deleted_scope: a broad serialization layer refactor
  oracle: pytest that the optional field survives the clone
  effort_tier: Premium
  consequence_evidence: an optional field must survive the save
  declared_contract: frozen-schema cardinality
  named_consequence_surface: none
"""
    # Same plan with the declared trigger STRIPPED to absent. The real-arbiter
    # property: this MUST now FAIL (no named trigger floors the Premium claim).
    real_arbiter_stripped_plan = real_arbiter_premium_plan.replace(
        "declared_contract: frozen-schema cardinality",
        "declared_contract: none",
    )
    # Named-consequence-surface fixture (the credit-threshold flip). Promotes via a
    # DECLARED surface, not a token in prose. PASSES — proving the legitimate
    # domain-consequence path works without any substring shortcut.
    named_surface_premium_plan = """
engineering_discipline:
  assumptions: flip the credit approval threshold from 0.70 to 0.75
  ambiguity: no unresolved authority conflict
  maturity_layer: Birth
  promotion_evidence: none
  protected_baseline: the existing threshold constant behavior
  stack_surface: the single threshold constant
  simplest_path: change the one declared constant
  allowed_complexity: edit the existing constant only
  forbidden_complexity: a thresholds config map or policy seam
  deleted_scope: a pluggable policy framework
  oracle: pytest the boundary fixture at 0.74/0.75/0.76
  effort_tier: Premium
  consequence_evidence: the new cut must be proven at the boundary
  declared_contract: none
  named_consequence_surface: credit-decision-threshold
"""
    # UNDER_EFFORT: a named consequence surface is DECLARED but the tier is left at
    # Standard. UNDER_EFFORT must fire. FAILS as expected.
    under_effort_plan = """
engineering_discipline:
  assumptions: flip the credit approval threshold from 0.70 to 0.75
  ambiguity: no unresolved authority conflict
  maturity_layer: Birth
  promotion_evidence: none
  protected_baseline: the existing threshold constant behavior
  stack_surface: the single threshold constant
  simplest_path: change the one declared constant
  allowed_complexity: edit the existing constant only
  forbidden_complexity: a thresholds config map or policy seam
  deleted_scope: a pluggable policy framework
  oracle: pytest the boundary fixture at 0.74/0.75/0.76
  effort_tier: Standard
  declared_contract: none
  named_consequence_surface: credit-decision-threshold
"""
    # Should-fail: Premium claimed with NO named trigger and non-generic, non-weasel
    # prose. This is the adjective-as-criteria / invented-rigor failure the gate
    # exists to block; its absence is exactly what let the original gap ship. MUST
    # FAIL as NEEDS_REVIEW.
    premium_no_named_fact_plan = """
engineering_discipline:
  assumptions: change a button colour from blue to teal
  ambiguity: no unresolved authority conflict
  maturity_layer: Birth
  promotion_evidence: none
  protected_baseline: the existing button colour token
  stack_surface: the one button component
  simplest_path: edit the colour token value
  allowed_complexity: a single token edit
  forbidden_complexity: a theming system or config map
  deleted_scope: a shared colour registry
  oracle: npm run lint on the changed file
  effort_tier: Premium
  consequence_evidence: i just feel like being thorough about this button
  declared_contract: none
  named_consequence_surface: none
"""
    # A benign Standard change whose prose contains the word "dropdown". Kept as the
    # one honest word-boundary fixture: "drop" must never fire on "dropdown", and a
    # Standard plan with no named trigger PASSES.
    benign_standard_plan = """
engineering_discipline:
  assumptions: rename a dropdown label in a throwaway demo screen
  ambiguity: no unresolved authority conflict
  maturity_layer: Birth
  promotion_evidence: none
  protected_baseline: the existing demo label text
  stack_surface: the one demo component
  simplest_path: edit the dropdown label string
  allowed_complexity: a single string edit
  forbidden_complexity: any new component or config
  deleted_scope: a shared label registry
  oracle: npm run lint on the changed file
  effort_tier: Standard
  consequence_evidence: a dropdown label tweak with no declared contract
  declared_contract: none
  named_consequence_surface: none
"""
    # Canary finding 1: "ambiguity: none" is an honest answer ("nothing unresolved"),
    # not an empty-or-generic field. A well-formed Standard plan that answers none
    # to ambiguity must PASS. (Lived: every realistic plan a canary agent wrote.)
    ambiguity_none_plan = """
engineering_discipline:
  assumptions: rename a label in a throwaway demo screen
  ambiguity: none
  maturity_layer: Birth
  promotion_evidence: none
  protected_baseline: the existing demo label text
  stack_surface: the one demo component
  simplest_path: edit the label string
  allowed_complexity: a single string edit
  forbidden_complexity: any new component or config
  deleted_scope: a shared label registry
  oracle: npm run lint on the changed file
  effort_tier: Standard
  declared_contract: none
  named_consequence_surface: none
"""
    # Canary finding 2: a PII export across the app boundary is a first-class named
    # consequence surface (a universal class, not a project special-case). Promoting
    # via the declared surface PASSES. (Lived: the canary receipt-export-with-PII.)
    pii_export_premium_plan = """
engineering_discipline:
  assumptions: the receipt export will include the buyer's address and email
  ambiguity: none
  maturity_layer: Birth
  promotion_evidence: none
  protected_baseline: the existing receipt export payload
  stack_surface: the receipt export function
  simplest_path: add the declared PII fields to the export payload
  allowed_complexity: extend the existing payload builder
  forbidden_complexity: a new export framework
  deleted_scope: a generic export pipeline
  oracle: pytest the export payload shape and PII redaction
  effort_tier: Premium
  consequence_evidence: personal data crosses the app boundary in this export
  declared_contract: none
  named_consequence_surface: pii-export-surface
"""
    # Safeguard: the enum is curated, not open. A surface that is NOT a known member
    # must still fail as NEEDS_REVIEW — proving expansion is curation, not a path
    # for any string to mint Premium.
    unknown_surface_plan = pii_export_premium_plan.replace(
        "named_consequence_surface: pii-export-surface",
        "named_consequence_surface: some-unlisted-surface",
    )
    broad_only_oracle_plan = """
engineering_discipline:
  assumptions: change one exported behavior
  ambiguity: none
  maturity_layer: Birth
  promotion_evidence: none
  protected_baseline: the existing exported behavior
  stack_surface: the public entrypoint
  simplest_path: edit the existing branch
  allowed_complexity: one branch edit
  forbidden_complexity: a validation framework
  deleted_scope: a broad quality pass
  oracle: npm run commit:check
  effort_tier: Standard
  declared_contract: none
  named_consequence_surface: none
"""
    broad_with_focused_proof_plan = broad_only_oracle_plan + (
        "  focused_proof: pytest boundary fixture asserts the exported behavior regression\n"
    )
    failures: list[str] = []
    broad_only_fields = parse_plan_fields(broad_only_oracle_plan)
    broad_with_focused_fields = parse_plan_fields(broad_with_focused_proof_plan)
    if not oracle_is_broad_closure(broad_only_fields["oracle"]):
        failures.append("semantic self-test did not detect a broad closure oracle")
    if has_red_capable_proof(broad_only_fields.get("focused_proof", "")):
        failures.append("semantic self-test found focused proof where none was declared")
    if not has_red_capable_proof(broad_with_focused_fields.get("focused_proof", "")):
        failures.append("semantic self-test did not detect a red-capable focused proof")
    if not validate_plan_text(broad_only_oracle_plan):
        failures.append("semantic self-test accepted a broad closure gate with no focused_proof")
    if validate_plan_text(broad_with_focused_proof_plan):
        failures.append("semantic self-test rejected a broad closure gate with focused_proof")
    if validate_plan_text(valid_plan):
        failures.append("semantic self-test rejected a valid Evolution plan")
    if not validate_plan_text(vague_plan):
        failures.append("semantic self-test accepted a vague promoted plan")
    if validate_plan_text(real_arbiter_premium_plan):
        failures.append("semantic self-test rejected a real-arbiter Premium plan")
    if not validate_plan_text(real_arbiter_stripped_plan):
        failures.append("semantic self-test accepted a Premium plan after its declared trigger was stripped (arbiter has no teeth)")
    if validate_plan_text(named_surface_premium_plan):
        failures.append("semantic self-test rejected a named-consequence-surface Premium plan")
    if not validate_plan_text(under_effort_plan):
        failures.append("semantic self-test accepted an under-effort plan (UNDER_EFFORT did not fire)")
    if not validate_plan_text(premium_no_named_fact_plan):
        failures.append("semantic self-test accepted a Premium plan with no named trigger (the shipped gap)")
    if validate_plan_text(benign_standard_plan):
        failures.append("semantic self-test rejected a benign Standard plan (dropdown false-fire)")
    if validate_plan_text(ambiguity_none_plan):
        failures.append("semantic self-test rejected an honest 'ambiguity: none' plan (canary finding 1)")
    if validate_plan_text(pii_export_premium_plan):
        failures.append("semantic self-test rejected a PII-export named-surface Premium plan (canary finding 2)")
    if not validate_plan_text(unknown_surface_plan):
        failures.append("semantic self-test accepted an unlisted consequence surface (enum is not curated/binary-hard)")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--plan", type=Path)
    args = parser.parse_args()

    failures: list[str] = []

    if args.self_test:
        root = Path(__file__).resolve().parents[1]
        skill = root / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        for term in REQUIRED_TERMS:
            if term not in text:
                failures.append(f"missing skill term: {term}")
        failures.extend(semantic_self_test())

    if args.plan:
        text = args.plan.read_text(encoding="utf-8")
        failures.extend(validate_plan_text(text))

    if not args.self_test and not args.plan:
        failures.append("choose --self-test or --plan <file>")

    if failures:
        print("[tes-discipline] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("[tes-discipline] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
