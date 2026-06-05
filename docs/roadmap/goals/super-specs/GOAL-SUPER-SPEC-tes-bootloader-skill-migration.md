---
tds_id: roadmap.goal_super_spec_tes_bootloader_skill_migration
tds_class: roadmap
status: archived
consumer: maintainers, adapter authors, skill authors, oracle authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L2
tver: 0.2.0
---

# GOAL Super SPEC: Bootloader-To-Skill Migration (Lazy Context)

Status: COMPLETE / archived for lineage (executed 2026-06-04, TES 0.3.165).
Reduce each adapter
bootloader (`CURSOR.md` / `AGENTS.md` / `CLAUDE.md`) to a thin always-loaded
anchor and move certified detail into each host's lazy, progressively-disclosed
skill layer. The behavioral core that drove the measured 7-day gains stays in
the always-loaded anchor; everything else loads on demand.

## Execution Record (closeout)

All seven units executed and committed; `npm run commit:check` PASS (43 gates,
exit 0). Anchor content lines after migration: CLAUDE.md 58, AGENTS.md 66
(XML-tagged), CURSOR.md 31, Cursor `tes-guidelines.mdc` 57 — all within the
parity oracle budget (70).

| Unit | Commit | Result |
|------|--------|--------|
| SPEC-000 inventory | `73afee5` | Persistent concept inventory + baseline |
| SPEC-001 skill single-source | `3d03a4c` | Memory Lifecycle moved into Claude/Codex skills |
| SPEC-002 thin Claude | `b1b4a92` | CLAUDE.md 247 -> 75 lines |
| SPEC-003 thin Codex | `3d21ca0` | AGENTS.md 252 -> 91 lines |
| SPEC-004 thin Cursor + rule modes | `6e0413a` | Lazy `alwaysApply:false` capability rule |
| SPEC-005 parity oracle | `780c38f` | `context_skill_parity_oracle.py` (byte + semantic) |
| SPEC-006 materialize/install/release | `491514f`, `8885e4a`, `690c4cc6` | Three-layer parity contract; 0.3.165 bundle |

The accepted contract was renegotiated mid-execution by owner decision: not a
bare ~50-line thinning, but a three-layer contract — short anchor + route in the
bootloader, full expansion in the lazy skill/rule, oracle proving both — so no
oracle protection was deleted and no certified knowledge was dropped.

Certified (self-test, smoke, composition, parity), not yet field-proven: no real
host loaded the thinned anchors and exercised lazy loading. The
`real_project_learning_standard` canary replay across three hosts remains the
open follow-up before any field claim. Remote sync (push, tag v0.3.165,
`release:check`, `public_pages_oracle`) was deferred by owner decision.

Capability: a thin, always-loaded discipline anchor per host plus a single-source
lazy skill layer, so the first context layer of every adopting project carries
maximum signal at minimum permanent weight.

## Why Now (Certified Evidence)

A 7-day, 8-project, 16-team parallel evaluation (8 teams with TES, 8 with default
agent features only, otherwise non-interfered) measured, for the TES arm: no
line-loss on long tasks, up to 12x faster goal attainment with large token
savings, ~3x fewer hallucinations, and ~7x more documentation/Context7 lookups.
TES is a method, and the method works. The remaining defect is delivery shape:
too much certified knowledge sits in the always-loaded bootloader when its
correct home is the lazy skill layer.

## Platform Truth (Official Docs, Verified Before Writing)

All three hosts implement the same always-loaded vs lazy split; this design is
aligned with each vendor's own recommendation:

| Host | Always-loaded layer | Lazy layer (progressive disclosure) | Lazy trigger |
|------|---------------------|--------------------------------------|--------------|
| Claude Code | `CLAUDE.md` (recommended <=200 lines; docs say "move reference material to skills, which load on-demand") | `.claude/skills/<n>/SKILL.md` | only `description` always in context; body loads when the description matches or on `/name` |
| Codex | `AGENTS.md` (kept minimal; closer files take precedence) | `.agents/skills/<n>/SKILL.md` | "initially accesses only the skill's name, description, and file path; full SKILL.md loaded only when needed... without bloating the context" |
| Cursor | rule with `alwaysApply: true` | rule with `description` + `alwaysApply: false` ("Apply Intelligently") | agent loads the rule body only when the description is judged relevant; `globs` auto-attach by file; none -> manual `@`-mention |

The ~50-line target is below the Claude recommended ceiling and matches the
Codex "minimal" and Cursor "small always-on" guidance.

## Current Meaning (Evidence-Based)

The bootloaders today DUPLICATE knowledge that the skills already carry lazily:
`src/adapters/claude/skills/tes-guidelines/SKILL.md` (161 lines) already has the
Four Gates table, Diamond, Mantra Gate, Infrastructure Gate, Workflow, Cortex
reflex, and Field Reports; `tes-init/SKILL.md` (124 lines) already has the full
init gate flow. So this line is mostly DEDUPLICATION — delete the duplicated
detail from the bootloader and let the skill be the single source — plus moving
the few items that have no skill home yet, plus the Cursor rule-mode change.

## Invariants (must hold after every unit)

- Anchor-not-copy: each of the four principles appears ONCE as a one-line
  falsifiable anchor in the bootloader and ONCE as expansion in the skill. The
  same paragraph must never live in both places (that is the disease being
  cured, and it risks divergence on later edits).
- Behavioral core stays always-loaded: the four principles, the runtime-first
  one-liner, the success formula, and the skill-routing map remain in the
  ~50-line anchor so the method influences every turn, not only when a skill
  matches.
- No certified knowledge lost: every detail removed from a bootloader must
  already exist (or be moved) in the host's lazy skill/rule layer; a parity
  oracle proves this before closure.
- Platform particularity preserved: Claude numbered-heading anchor, Codex
  XML-tagged anchor, Cursor thin-pointer rule. Do not flatten into one template.
- Cursor lazy correctness: capability rules use `description` +
  `alwaysApply: false`; only the thin discipline anchor may be `alwaysApply: true`.
- Confidentiality parity: the private-confidentiality rule must be present (anchor
  or skill) consistently across all three, now that the repo is public. (Today
  only Claude states it; this line fixes the unevenness recorded in the
  2026-06-04 adapter bootloader review.)
- Reversibility unaffected: the TES:CORE/PROJECT-OVERLAY composition and the
  capsule install/uninstall/attach/detach contract are not weakened; smaller
  cores still compose and decompose cleanly.

## Required Fix Matrix

| Fix | Owned Surface | Gap Today | Required Correction | Focused Oracle |
|-----|---------------|-----------|---------------------|----------------|
| Skill-layer single source | `src/adapters/*/skills/**`, `src/adapters/cursor/rules/**` | Detail is duplicated between bootloader and skill. | Ensure every detail (init gate, Cortex reflex, Field Reports, Memory Lifecycle, per-intent protocol) lives in exactly one skill/rule, complete and current. Move the few orphan items that have no skill home. | per-skill `--self-test` where present; skill presence check. |
| Thin Claude anchor | `src/adapters/claude/CLAUDE.md` | 248 lines, mostly duplicated. | Reduce to ~50 lines: identity, four one-line principles, runtime-first one-liner, success formula, confidentiality one-liner, skill-routing map, locks. Detail -> `tes-guidelines`/`tes-init`. | `python3 scripts/root_context.py --self-test`; line-count <= ~55. |
| Thin Codex anchor | `src/adapters/codex/AGENTS.md` | 252 lines. | Reduce to ~50 lines preserving XML-tag form: `<instructions>` (four one-liners), runtime-first, `<routing>` map, `<locks>`. Detail -> `.agents/skills/**`. | `python3 scripts/root_context.py --self-test`; `discipline_oracle --self-test`. |
| Thin Cursor anchor + rule modes | `src/adapters/cursor/CURSOR.md`, `src/adapters/cursor/rules/*.mdc` | Prose guide; rule-mode frontmatter not aligned to lazy. | Reduce CURSOR.md to ~50 lines; ensure `tes-guidelines.mdc` is the thin always-on anchor and `tes-runtime-capabilities.mdc` is `description`+`alwaysApply:false` (lazy). | `python3 scripts/root_context.py --self-test`; rule frontmatter check. |
| Parity oracle | new `scripts/context_skill_parity_oracle.py` | No proof that thinning a bootloader did not drop certified knowledge. | New oracle: for each removed bootloader concept, assert it is present in the host's skill/rule layer; assert no principle text is byte-duplicated between anchor and skill; assert anchor line budgets. | `python3 scripts/context_skill_parity_oracle.py --self-test`. |
| Materialization + install proof | `scripts/materialize_adapter.py`, `scripts/install_smoke.py` | Thinner cores must still materialize and compose. | Assert materialized adapters carry the thin anchor + full skill set; assert TES:CORE composition still works with the smaller core. | `python3 scripts/materialize_adapter.py all --check`; `install_smoke --self-test`. |

## Execution Discipline

Run units sequentially. Do not implement a later unit before the current unit
has its focused oracle green, a release identity classification, and a closure
note. Before each unit state owned files, no-touch files, release identity
impact, focused oracle, and stop condition.

## SPEC-000: Reentry, Baseline, Inventory

Owned files: this Super SPEC; no runtime files.

Tasks:

1. `git status` / `git log -8`; classify dirty as inherited/current/unrelated.
2. Name last-known-good: current bootloaders + skills, materialization PASS,
   composition PASS — the behavior the parity oracle must protect.
3. Inventory every concept in each bootloader and mark: already-in-skill /
   move-to-skill / keep-as-anchor. This inventory is the contract for SPEC-002..004.
4. Confirm planning-only, version-neutral.

Focused oracle: `validate_tds`, `private_vocabulary_oracle`, `git diff --check`.

Stop condition: if a concept has no clear skill home and is not anchor-worthy,
stop and decide its home before thinning.

## SPEC-001: Skill-Layer Single Source

Owned files: `src/adapters/*/skills/**`, `src/adapters/cursor/rules/**`.

Implementation:

1. For each concept marked move-to-skill in SPEC-000, ensure it is complete and
   current in exactly one skill/rule.
2. Do not duplicate; if a concept already exists in a skill, leave it and mark
   it for deletion from the bootloader (SPEC-002..004), do not re-add it.
3. Preserve each platform's skill format.

Release identity impact: delivered skill behavior; patch bump decided at SPEC-006.

Focused oracle: affected skill `--self-test` where present; skill presence check.

Stop condition: if moving a concept would weaken a skill self-test, fix the skill
first.

## SPEC-002: Thin Claude Anchor

Owned files: `src/adapters/claude/CLAUDE.md`.

Implementation: reduce to ~50 lines — identity; the four principles as one
falsifiable line each (anchor, not the detailed text that lives in the skill);
runtime-first one-liner; success formula; one-line confidentiality rule;
skill-routing map (intents -> `.claude/skills/tes-*`); locks. Everything else
references the skill, it does not restate it.

Release identity impact: delivered behavior; patch bump at SPEC-006.

Focused oracle: `root_context.py --self-test`; CLAUDE.md line count <= ~55.

Stop condition: if a removed line has no skill home, route it through SPEC-001
first; never drop certified knowledge to hit the line budget.

## SPEC-003: Thin Codex Anchor

Owned files: `src/adapters/codex/AGENTS.md`.

Implementation: reduce to ~50 lines preserving the XML-tag form Codex parses:
`<instructions>` (four one-liners), `<runtime_first_product_rule>` one-liner,
`<routing>` map to `.agents/skills/tes-*`, `<locks>`. Move init-gate, Cortex
reflex, Field Reports, and Memory Lifecycle detail to their skills (most already
exist there).

Release identity impact: delivered behavior; patch bump at SPEC-006.

Focused oracle: `root_context.py --self-test`; `discipline_oracle --self-test`;
AGENTS.md line count <= ~55.

Stop condition: same as SPEC-002.

## SPEC-004: Thin Cursor Anchor + Rule Modes

Owned files: `src/adapters/cursor/CURSOR.md`, `src/adapters/cursor/rules/*.mdc`.

Implementation:

1. Reduce `CURSOR.md` to ~50 lines (thin pointer + intents + locks).
2. Ensure `tes-guidelines.mdc` carries the always-on discipline anchor
   (`alwaysApply: true`, minimal) and `tes-runtime-capabilities.mdc` is lazy
   (`description` + `alwaysApply: false`), so capability detail loads only when
   relevant — the Cursor-native equivalent of a lazy skill.
3. Add the confidentiality one-liner so Cursor matches the other two.

Release identity impact: delivered behavior; patch bump at SPEC-006.

Focused oracle: `root_context.py --self-test`; rule frontmatter mode check;
CURSOR.md line count <= ~55.

Stop condition: if a capability rule cannot be made lazy without breaking Cursor
loading, keep it always-on and record why.

## SPEC-005: Parity Oracle

Owned files: new `scripts/context_skill_parity_oracle.py`.

Implementation:

1. For each concept the SPEC-000 inventory marked removed-from-bootloader, assert
   it is present in the host's skill/rule layer.
2. Assert no principle text is byte-duplicated between an anchor and its skill
   (anchor-not-copy invariant).
3. Assert each anchor is within its line budget.
4. `--self-test` with fixtures: a thinned anchor with full skill coverage (PASS);
   a thinned anchor missing a concept from skills (FAIL); a duplicated paragraph
   (FAIL).

Release identity impact: delivered oracle behavior; patch bump at SPEC-006.

Focused oracle: `python3 scripts/context_skill_parity_oracle.py --self-test`.

Stop condition: if parity cannot be proven mechanically for a concept, do not
thin that concept until it can.

## SPEC-006: Materialization, Install Proof, Release

Owned files: correlated bundle/public/version surfaces; `scripts/install_smoke.py`
fixtures only if needed.

Tasks:

1. `materialize_adapter all --check` and `install_smoke --self-test`: thinner
   cores still materialize, compose (TES:CORE/PROJECT-OVERLAY), and the capsule
   install/attach/detach contract is unaffected.
2. Run the parity oracle and every affected skill self-test.
3. Release identity: delivered bootloader + skill behavior -> patch bump unless
   the owner defers; run baseline gates and `npm run commit:check`; bump via the
   source release flow if performed.

Stop condition: if a smaller core breaks composition or detach, stop and fix the
core before release.

## Private Vocabulary Guard

No private project names, paths, remotes, or canary identifiers enter TES. Use
generic placeholders only.

## Evidence Plan

| Evidence | Location | Requirement |
|----------|----------|-------------|
| Per-bootloader line count before/after | closeout summary | Show ~50-line target met without losing concepts. |
| Parity oracle output | closeout summary | Every removed concept present in skill layer; no byte-duplication. |
| Materialization + composition proof | closeout summary | Thinner cores still install/compose/detach. |

## Final Closure Report Requirements

Report: implemented units; files changed; release identity decision; focused
oracle results; baseline gate results; `npm run commit:check` result;
confirmation that no certified knowledge was lost (parity oracle), that the
behavioral core stayed always-loaded, and that platform particularity was
preserved; residual risks; deferred work; no private identifiers added.
