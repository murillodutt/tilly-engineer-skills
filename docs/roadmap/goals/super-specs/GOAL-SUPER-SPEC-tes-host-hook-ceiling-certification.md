---
tds_id: roadmap.goal_super_spec_tes_host_hook_ceiling_certification
tds_class: roadmap
status: archived
consumer: maintainers, hook authors, installer authors, oracle authors, release reviewers, and hook-audit operators
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Super SPEC: TES Host Hook Ceiling Certification

Status: archived historical execution plan. ADR 0009 execution is superseded by
`GOAL-SUPER-SPEC-adr-0009-pretooluse-ceiling-linear-slices.md`; keep this file
only as prior `0.3.209` hook-ceiling evidence, not as the current prompt track.

Capability: make TES installed hook behavior ceiling-grade across Codex, Claude
Code, and Cursor by closing legacy-update gaps, unsafe native matcher gaps,
ledger evidence gaps, false-fail audit protocol gaps, and release identity gaps.

## Canonical Artifact

Canonical Super SPEC:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-host-hook-ceiling-certification.md`

Primary architecture source: `docs/adr/0008-host-aware-runtime-contracts.md`

Related sources:

- `docs/governance/AGENTIC-ALIGNMENT-GOVERNANCE.md`
- `docs/install/HOOK-AUDIT-PROMPT.md`
- `docs/evidence/reports/2026/06/27/sync/tes-sync-0.3.209/REPORT.md`
- `docs/roadmap/product/PLANTAO-HOOK-MECHANISM.md`
- `scripts/tes_install.py`
- `scripts/host_runtime_matrix_oracle.py`
- `scripts/mantra_gate_pretooluse_oracle.py`

Protected baseline: release `0.3.209`, commit `04637ce4`, bundle SHA
`9a7f7fb59a60348dad846f221d94e944bd66a6f416552d01b9d7888f39063da0`.

## Documentary Evidence

| Evidence | What It Proves | Use In This SPEC |
|---|---|---|
| ADR 0008 | Host-aware runtime behavior is a package invariant; config presence is not certification; per-host executable proof is required. | Governs every unit below. |
| Agentic Alignment Governance official source map | Codex, Claude Code, and Cursor have separate official hook surfaces; do not create false symmetry. | Anchors upstream-source lookup and host separation. |
| `0.3.209` sync report | The mini matrix was published, reverse-tested, and the next hook test protocol was defined. | Establishes the baseline that still missed update/preserve and audit-protocol gaps. |
| Hook audit reports from Codex, Cursor, and Claude Code | Exposed legacy Codex matcher drift, unsafe forbidden-shell native path, missing ledger proof fields, and false-fail cross-host protocol. | Supplies the defect classes; target names and private paths must not enter tracked artifacts. |
| `PLANTAO-HOOK-MECHANISM.md` | Pre-action hooks are host-specific and must self-falsify with block, allow, and anti-cry-wolf fixtures. | Reuses the proven hook-lens model without transplanting reference implementation code. |
| Official Codex hooks docs | Codex hook config and hook events are host-owned, not Claude/Cursor contracts. | Verify matcher and config behavior before source changes. |
| Official Claude Code hooks docs | Claude Code uses its own hook output contract and `hookSpecificOutput` surface. | Verify `additionalContext` and exit-code semantics before claims. |
| Official Cursor hooks docs | Cursor hook behavior is a Cursor-specific contract and must not be flattened into Claude/Codex exit-code semantics. | Verify JSON permission behavior before claims. |

Official source links are retained through
`docs/governance/AGENTIC-ALIGNMENT-GOVERNANCE.md`: Codex hooks
`https://developers.openai.com/codex/hooks`, Claude Code hooks
`https://code.claude.com/docs/en/hooks`, Cursor hooks
`https://cursor.com/docs/hooks`. The `Flash-Fry` label is a public TES marker
used by delivered hook supervision, not private target vocabulary.

## Problem

The post-`0.3.209` audit showed that the package crossed the floor but did not
yet cross the ceiling:

1. A preserved Codex install could retain a TES-owned legacy
   `PreToolUse` matcher of `Write|Edit|MultiEdit`.
2. That legacy matcher can leave native Codex `apply_patch` and shell tools
   outside the PreToolUse hard gate.
3. The installed-target matrix certified fresh installation but did not include
   a preserved-target migration fixture.
4. The runtime ledger proved that hooks fired, but did not persist whether the
   hook emitted the marker, blocked, or suppressed context through anti-cry-wolf.
5. The audit prompt asked one host execution to natively certify all hosts,
   creating false FAIL verdicts for tools unavailable in the current host.
6. Cursor Edit/MultiEdit coverage was treated as mandatory even when the host
   only exposed native Write for the smoke.
7. Simulated contracts, historical ledger observations, and current native
   observations were not separated by evidence class.
8. The repair changes delivered behavior and therefore require a patch release
   identity decision before target reruns can be final.

## Goal

After this Super SPEC is implemented and released, TES hook certification must be
able to say, with executable evidence:

```text
fresh install + preserved update + per-host native smoke + host-specific output
+ decision-rich ledger + reverse fixtures + release identity
= PASS or an exact, non-ambiguous finding
```

## Central Rule

```text
One semantic gate.
Host-specific hook projection.
One native host per smoke run.
Decision-rich ledger proof.
```

No target can be certified by config-only evidence. No single host run can fail
because another host's native tool is unavailable. No hook can be called healthy
if its native mutating or forbidden tools bypass the matcher.

## Non-Objectives

- Do not transplant reference-project code, identifiers, storage, scripts,
  prompts, plugin metadata, or domain concepts.
- Do not edit installed target mirrors as package truth.
- Do not push, tag, publish, release, marketplace-submit, or use secrets from
  this SPEC alone.
- Do not make a universal hook protocol.
- Do not broaden the Mantra Gate into routine cry-wolf output.
- Do not treat historical ledger records as native proof for the current host.
- Do not include private target names, private filesystem paths, product names,
  stack details, or raw report paths in tracked artifacts.

## Findings To Close

| Priority | Finding | Required Closure |
|---|---|---|
| P0 | Codex preserved installs can retain a legacy `Write|Edit|MultiEdit` matcher. | Reinstall/update replaces TES-owned Codex hook blocks with the current matcher and preserves non-TES config. |
| P0 | Native Codex forbidden shell can execute when shell tools are not matched. | Codex matcher must include `Bash`, `Shell`, and `shell`; audit must not run state-changing forbidden probes when matcher coverage is missing. |
| P1 | Audit protocol creates false cross-host FAIL verdicts. | Audit prompt certifies one native host per execution and classifies other hosts separately. |
| P1 | Ledger cannot prove marker/block/suppression decisions. | PreToolUse ledger records `risk`, `block`, `decision`, `permission_decision`, `marker_emitted`, `context_suppressed`, `surface_context`, and Cortex context state. |
| P1 | Mini matrix misses preserved-target migration. | `host_runtime_matrix_oracle.py` includes a legacy Codex matcher fixture and fails before migration. |
| P2 | Cursor Edit/MultiEdit is over-required. | Cursor native Write is required; Edit/MultiEdit is required only when the host exposes and declares it. |
| P2 | Evidence classes are ambiguous. | Add and use `CONTRACT_SIMULATED`; keep `OBSERVED` for current runtime proof only. |
| P3 | Delivered change lacks release identity. | Bump, bundle, docs, commit, push, tag, release check, and public-pages oracle are required before target rerun closure. |

## Ordered Units

### SPEC-000: Evidence Packet And Scope Lock

Objective: freeze the defect taxonomy and source evidence without expanding the
runtime patch.

Allowed files: this Super SPEC, `docs/INDEX.md`, `docs/tds/DOCS-INDEX.yml`,
and the required execute-loop ledger under `docs/roadmap/goals/ledgers/`.

Forbidden moves: runtime edits, release bump, bundle publish, push, tag, or target
mirror edits.

Focused oracle:

```bash
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py --paths docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-host-hook-ceiling-certification.md
git diff --check
```

Done when the Super SPEC is indexed and the evidence packet names every finding
without private target identifiers.

### SPEC-001: Codex Preserved-Update Matcher Migration

Objective: make `tes_install.py` refresh TES-owned Codex `SessionStart` and
`PreToolUse` TOML blocks during reinstall/update, including legacy marked or
unmarked TES blocks.

Allowed files: `scripts/tes_install.py`, focused installer fixtures inside its
self-test, correlated release surfaces only if authorized later.

Negative fixture: a target starts with TES-owned Codex `matcher =
"Write|Edit|MultiEdit"` and after `install_codex_hook` has exactly one TES
`PreToolUse` block with the full matcher.

Focused oracle:

```bash
python3 scripts/tes_install.py --self-test
npm run host-runtime:matrix
```

### SPEC-002: Decision-Rich PreToolUse Ledger

Objective: persist the hook decision that explains runtime behavior, not only
that the hook fired.

Allowed files: `scripts/tes_install.py`, `scripts/host_runtime_matrix_oracle.py`.

Required ledger fields for PreToolUse: `risk`, `block`, `decision`,
`permission_decision`, `marker_emitted`, `context_suppressed`,
`cortex_context_emitted`, `surface_context`.

Negative fixture: the matrix must fail if first governed Codex `apply_patch`
does not write `decision=allow`, `permission_decision=allow`, and
`marker_emitted=true`, if second same-session mutation does not write
`context_suppressed=true`, or if forbidden Codex shell lacks `decision=block`,
`permission_decision=deny`, and `block=true`. It must also fail if Cursor
governed JSON allow and Cursor forbidden JSON deny do not persist matching
`permission_decision` values.

Focused oracle:

```bash
npm run host-runtime:matrix
python3 scripts/mantra_gate_pretooluse_oracle.py --self-test
```

### SPEC-003: Per-Host Native Audit Prompt Repair

Objective: rewrite the installed hook audit prompt so each execution certifies
only the current host natively and labels all other evidence precisely.

Allowed files: `docs/install/HOOK-AUDIT-PROMPT.md`, TDS/index correlations if
needed.

Required semantics:

- Codex run requires native `apply_patch` and matcher coverage for shell tools.
- Claude Code run requires native `Write/Edit` and exit-code block proof.
- Cursor run requires native `Write`; Edit/MultiEdit is optional unless exposed.
- Other-host results are `CONFIGURED`, prior `OBSERVED`, `CONTRACT_SIMULATED`,
  or `NEEDS_EVIDENCE`, never automatic FAIL.
- Codex marker proof may use visible output or decision-rich ledger/sentinel
  evidence.

Focused oracle:

```bash
python3 scripts/hook_audit_prompt_oracle.py --self-test
python3 scripts/validate_tds.py
python3 scripts/validate_reference_package.py
python3 scripts/build_public_docs.py --check
python3 scripts/tds_surface_oracle.py
```

### SPEC-004: Reverse Certification And Mutation Suite

Objective: prove the new checks can go red.

Required mutants:

- legacy Codex matcher remains unchanged;
- Codex `apply_patch` ledger omits `marker_emitted`;
- second same-session governed mutation omits `context_suppressed`;
- forbidden shell ledger omits `block`;
- prompt reintroduces "all hosts must be native in one execution";
- prompt removes `CONTRACT_SIMULATED`, per-host native audit, Codex shell
  matcher coverage, Cursor optional Edit/MultiEdit, or closed
  `PASS_WITH_FINDINGS` allowance.

Focused oracle: run executable local mutation harnesses, not a manual-only
review. At minimum, the matrix must include executable negative checks for the
first four mutants, and `hook_audit_prompt_oracle.py --self-test` must fail
in-memory prompt mutants for the prompt contract.

### SPEC-005: Release Identity `0.3.210`

Objective: package the delivered behavior so installed targets can update and
rerun the corrected audit.

Required actions, only after explicit sync/release authorization:

```bash
python3 scripts/tes_bump.py patch --yes --json
python3 scripts/tes_bundle.py publish --adapter all
python3 scripts/build_public_docs.py
python3 scripts/validate_reference_package.py
npm run host-runtime:matrix
python3 scripts/validate_tds.py
python3 scripts/tds_surface_oracle.py
npm run commit:check
npm run commit:closure
git push origin main
git tag -a v0.3.210 -m "Release 0.3.210: host hook ceiling certification"
git push origin v0.3.210
npm run release:check
python3 scripts/public_pages_oracle.py --version 0.3.210 --retries 12 --interval 10
```

Done when `main`, tag, bundle, public pages, and release check all resolve to
the same release identity.

If explicit sync/release authorization is absent, stop after source-local
closure and report `NEEDS_OWNER_DECISION` for bump, bundle publish, push, tag,
release check, and public-page certification. Do not claim release closure from
source-local oracles alone.

### SPEC-006: Installed Target Rerun Protocol

Objective: rerun hook audits on updated targets using the corrected prompt.

Execution rule: one platform per run.

Expected verdicts:

- Codex: PASS or PASS_WITH_FINDINGS only if native `apply_patch` is observed,
  matcher includes `apply_patch|Bash|Shell|shell`, first governed event emits
  marker proof, second event suppresses context, and forbidden shell is blocked
  before execution.
- Claude Code: PASS or PASS_WITH_FINDINGS only if native `Write/Edit` is
  observed, `additionalContext` is emitted once, second event is silent, and
  forbidden Bash blocks with exit 2.
- Cursor: PASS or PASS_WITH_FINDINGS only if native Write is observed, governed
  JSON allow/user message is proven, second event is silent, and forbidden shell
  returns JSON deny without execution.

Known non-blocking findings remain ledger legacy residue and duplicate runtime
records only when hook-health classifies them as info/warning and they are not
used as evidence for the current host's native smoke. Missing current-host
native PreToolUse, matcher gaps, missing decision fields, or execution of a
forbidden command is always verdict-bearing FAIL.

## Required Closeout Oracles

Before claiming source closure:

```bash
npm run host-runtime:matrix
python3 scripts/tes_install.py --self-test
python3 scripts/mantra_gate_pretooluse_oracle.py --self-test
python3 scripts/mantra_gate.py --self-test
python3 scripts/hook_audit_prompt_oracle.py --self-test
python3 scripts/validate_tds.py
python3 scripts/tds_surface_oracle.py
python3 scripts/validate_reference_package.py
python3 scripts/build_public_docs.py --check
git diff --check
```

Before claiming release closure, also run `npm run commit:closure`,
`npm run release:check`, and `public_pages_oracle` for the released version.

## Done

This Super SPEC is complete only when:

- the source patch is committed;
- release identity advances to a synchronized public version;
- the mini matrix covers fresh install and preserved update;
- the ledger carries decision evidence;
- the prompt no longer creates false cross-host failures;
- Codex, Claude Code, and Cursor are rerun inside their own native hosts; and
- any remaining findings are explicitly non-blocking and tied to hook-health
  evidence.
