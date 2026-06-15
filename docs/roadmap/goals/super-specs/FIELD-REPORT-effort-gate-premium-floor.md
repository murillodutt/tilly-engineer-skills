---
tds_id: roadmap.field_report_effort_gate_premium_floor
tds_class: roadmap
status: active
consumer: maintainers and execution agents (TES window)
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# Field Report — Effort Gate Premium has no positive floor (SPEC-070 correction)

For the TES execution window. This is a correction to the
Declared-Contract Arbiter + Effort Gate change you just installed
(commits b64eead4..9a5e8fa4). A senior audit of the installed product-layer
files found a real, reproduced gap. The text contracts and the regression
survivors are clean; the gap is in the Effort Gate's Premium logic and the
self-test fixtures that bless it. Treat this as one additional execution unit,
**SPEC-070**, applied with the same discipline as the rest: per-adapter intent,
product layer only, oracle green, one commit.

## What is fine (do not touch)

The audit certified, by direct read of the installed files, that these are
faithful and must be left alone: the Gate Zero arbiter text on both surfaces;
the maturity reframe (the temporal sentence "Preserve the baseline first, then
simplify inside it." is gone, "smallest" is shielded to scope); the
scope-isolation clause; the thin product-layer bootloaders; the per-adapter
heading split (Claude "Six Gates", Codex "Core Gates"); the contract-history
row; and the absence of the old typos. The ArchiveStrategy and Platform worked
examples survive byte-identical. The earlier audit blocker that claimed "not
installed" was a false positive — it inspected the work layer (`.agents/`,
`.claude/`) which is correctly pre-change; the change is committed in the product
layer (`src/adapters/**`), which is exactly where it belongs. None of that needs
work.

## The gap (reproduced, real)

The Effort Gate's Premium branch has no positive floor. In
`src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py`,
`validate_plan_text` decides a Premium plan solely by REJECTING generic or
weasel prose, and never REQUIRES a source-nameable trigger:

> for a Premium tier, the code fails the plan only if `consequence_evidence` is
> generic or is-only-weasel; it never checks that a declared contract or a named
> consequence was actually stated.

Three consequences follow, each reproduced by direct execution against the
installed oracle:

First, the named `declared_contract` field is inert to every Premium outcome.
`valid_premium_plan` passes identically whether its `declared_contract` is
"frozen-schema cardinality", "none", or absent. The binary-hard arbiter — the
whole reason this change exists — has no teeth on the Premium path.

Second, adjective-only prose mints Premium. A Premium claim on a button-colour
change with `declared_contract: none` and the consequence text "i just feel like
being thorough about this button" PASSES. That is precisely the
"adjective-as-criteria" / "invented rigor on undeclared ones" failure the Effort
Gate text claims to block. No fixture guards against it.

Third — and this is the root — `CONSEQUENCE_SIGNALS` is a substring deny-list
that MIXES two different kinds of thing into one flat list: the four structural
declared-contract types ("frozen schema", "closed-domain", "peer-convergence",
"affordance-deliverable") sit in the same list as soft domain surfaces ("money",
"credit", "ledger", "auth", "migration"). Because of that mix, the weak
substring path and the strong declared-contract path are conflated: a plan
"about" a frozen schema passes via the token "frozen-schema" appearing in its
prose, with `declared_contract` doing nothing. The SPEC text itself sanctions
this — it defines Premium as firing when "the Declared-Contract Arbiter fires OR
named consequence evidence (a ledger/money/auth/migration surface)" — an OR that
makes a fragile token co-equal to the binary-hard arbiter. The fixtures are
named for the arbiter but only ever exercise the token path, so the green proves
author/code/fixture self-consistency, not fidelity to the objective. Of the four
new fixtures only `benign_standard_plan` (the dropdown word-boundary guard) is
honest and well-aimed.

The irony is the certification: a gate built to kill "fix-by-literal-list" and
"adjective-as-criteria" was caught doing both. The protocol, applied to its own
implementation, correctly condemned it. That is the system working — and the
clearest evidence the Effort Gate is needed.

## The fix (design, not patch)

Do not just bolt a floor onto the Premium branch — that would keep the flawed OR
and the fragile token list. Fix the design so both sides of the Premium trigger
are binary-hard, named, and first-class. The principle: Premium fires only on a
DECLARED, source-nameable fact that resolves to exactly one value or fails as
NEEDS_REVIEW — never on a substring match or undeclared prose. There is no
middle ground, in the spirit of tes-mine.

Concretely, three moves, applied per-adapter (Claude byte-for-byte, Codex by
equivalent intent in its own wording, never editing the work layer):

1. Split the conflated list. Keep the four structural declared-contract types
   exactly as they are. Promote "named consequence surface" from a loose token
   in `CONSEQUENCE_SIGNALS` to a first-class declared field of its own — a fifth
   trigger that the author must DECLARE, not a word the matcher finds in prose.
   It resolves binary-hard to one named surface (e.g. a credit-decision
   threshold, a ledger row, an auth/session issuance, an irreversible migration)
   or it is absent. Stop using substring search over free prose as the Premium
   mechanism; that is the fragile deny-list the whole change exists to retire.

2. Give the Premium branch a positive floor. A Premium plan must NAME at least
   one of: a `declared_contract` that resolves to one of the four types, OR a
   `named_consequence_surface` that resolves to one declared surface. If neither
   resolves to a named value, Premium FAILS as NEEDS_REVIEW — the same way
   `selected_layer` requires one enum, not the absence of garbage. Rejecting a
   weasel list is not a floor; requiring a named fact is.

3. Resolve the SPEC's OR so the two sides are co-equal in HARDNESS, not one
   strong and one weak. Both the declared contract and the named consequence
   surface are declared, binary-hard, source-nameable facts. The threshold
   worked example must stop attributing the promotion to "the Arbiter fires"
   (money/credit is none of the four contract types) and instead attribute it to
   a "named consequence surface" — a one-line wording fix on both SKILL
   surfaces, so the text and the oracle agree on which trigger fired.

## The fixtures (this is where the green failed)

The current fixtures certify the shortcut. Replace the distorted ones and add the
missing should-fail. At minimum:

- A real arbiter fixture: `declared_contract` resolves to a real type, the
  consequence prose is NEUTRAL (no token), and the plan PASSES — and crucially,
  stripping the `declared_contract` to absent makes the same plan FAIL. If a
  fixture passes identically with its declared trigger removed, it proves
  nothing; that property is the test.
- A should-fail Premium-with-no-named-fact: `effort_tier: Premium`,
  `declared_contract: none`, `named_consequence_surface: none`, consequence prose
  that is non-generic and non-weasel ("i just feel like being thorough about this
  button"). It MUST FAIL. This is the fixture whose absence let the gap ship.
- A named-consequence-surface fixture: the credit-threshold case, promoting via a
  DECLARED surface (not a token in prose), PASSES — proving the legitimate
  domain-consequence path still works without the substring shortcut.
- Keep `benign_standard_plan` as is; it is the one honest fixture.

Every fixture must trace back to a real lived scenario (the frozen-schema persist
defect, the credit-threshold flip, the export-affordance collision), not a
generic invented one, and must exercise the path it is NAMED for.

## Acceptance for SPEC-070

The unit is done when, in the product layer only: the Premium branch requires a
named declared trigger (contract OR named consequence surface) and fails
NEEDS_REVIEW otherwise; `CONSEQUENCE_SIGNALS` no longer conflates structural
contract types with soft domain tokens; the threshold worked example attributes
its promotion correctly on both SKILL surfaces; the new should-fail and
real-arbiter fixtures are present and the full self-test (now eight-plus
fixtures) is green; and the same green now proves the arbiter has teeth on the
Premium path, not just internal consistency. Commit message:
`fix(discipline): give Effort Gate Premium a positive named-trigger floor`.
Append a CONTRACT-HISTORY row recording the audit finding and the fix. One
commit, oracle green, no work-layer edit.

## Honest limits carried forward

This stays Stage A string validation: the oracle checks that the plan DECLARES a
named trigger, not that the trigger is true in a diff. That limit is correct and
must not be overclaimed. The named-consequence-surface list, like any enum, will
need governance curation over time — but a declared enum that resolves
binary-hard is a contract, not the substring deny-list it replaces. The fix
narrows the regression seed; it does not pretend to eliminate the need for
curation.
