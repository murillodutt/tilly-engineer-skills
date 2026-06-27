---
tds_id: roadmap.goal_super_spec_adr_0009_pretooluse_ceiling_linear_slices
tds_class: roadmap
status: active
consumer: maintainers, hook authors, installer authors, oracle authors, release reviewers, execution agents, and hook-audit operators
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Super SPEC: ADR 0009 PreToolUse Ceiling Linear Slices

## Purpose

Translate ADR 0009 into a linear execution contract made of small,
specialized runtime slices. This Super SPEC does not implement the ADR. It
prevents a future executor from flattening the ADR into one broad hook pass,
one generic oracle, or one ambiguous `PASS_CEILING` claim.

Central rule:

```text
One slice, one runtime ambiguity, one red-capable oracle, one local commit.
```

## Anchor Artifact

```text
anchor_class=ADR
anchor_path=docs/adr/0009-pretooluse-ceiling-contract-and-hook-topology.md
anchor_hash=0deb168a61b4f0ca57103bb96619768863c984c03fd609e8b7b233fe852c3093
anchor_origin=provided
anchor_source=docs/adr/0009-pretooluse-ceiling-contract-and-hook-topology.md
```

ADR 0009 remains the source of truth. This Super SPEC is the current execution
router for PreToolUse ceiling work and supersedes the archived `0.3.209` and
`0.3.210` host-hook ceiling Super SPECs as prompt tracks. Regenerate or repair
this file if the anchor hash changes.

## Protected Baseline

The protected baseline is the current `PASS_BASIC` floor from the existing
PreToolUse, Mantra Gate, session, host runtime matrix, hook audit, and package
validators. The baseline is not `PASS_CEILING`.

The quality ceiling is the ADR 0009 requirement:

```text
PASS_CEILING proves diagnostic power, drift attribution, and host-aware evidence.
```

Any future execution that cannot prove those three axes must close as
`PASS_BASIC_WITH_CEILING_GAPS`, `NEEDS_DISCOVERABILITY`, `NEEDS_EVIDENCE`, or
`BLOCKED`, not as `PASS_CEILING`.

## Execution Boundary

This document materializes the execution contract only. Later execution must
walk the units below in order. A later executor may stop after any green unit,
but must not skip ahead while an earlier unit is red, ambiguous, or unreviewed.

No remote, push, publish, marketplace, release tag, or secret-bearing action is
authorized by this Super SPEC.

## Non-Objectives

- Do not implement runtime changes while creating this Super SPEC.
- Do not patch installed target mirrors from this repository.
- Do not invent a universal hook protocol that hides host renderer semantics.
- Do not collapse Codex, Claude, and Cursor into one textual output contract.
- Do not add marker noise where the Mantra Gate should be silent.
- Do not store raw private command payloads, private paths, project names, or
  target evidence in tracked files.
- Do not bump package version until a delivered behavior change is implemented
  and its release identity decision is explicit.

## Shared Contracts

### `pretooluse_decision@2`

`pretooluse_decision@2` is a cross-stage contract, not one writer. Kernel owns
decision, risk, normalized tool, path or command category, payload source, and
classifier trace. Session owns anti-cry-wolf and `session_trace`. `tes_install.py`
owns host renderer projection, runtime ledger row, schema/version, redaction,
dedup material, `renderer_trace`, and `ledger_trace`.

Forbidden behavior:

- replacing current v1-compatible fields without migration;
- persisting raw secret-bearing command text;
- treating absence of v2 evidence as a ceiling pass.

Primary oracles:

- `python3 scripts/host_runtime_matrix_oracle.py --self-test`
- `python3 scripts/pretooluse_kernel_oracle.py`
- `python3 scripts/pretooluse_session_oracle.py`
- `python3 scripts/mantra_gate_pretooluse_oracle.py --self-test`

### Host Renderer Contract

Runtime host rendering remains in `scripts/tes_install.py`. Renderer parity
fixtures and proof are owned by `scripts/mantra_gate_pretooluse_oracle.py`; the
host runtime matrix consumes that proof without duplicating renderer semantics.

### Hook Health Contract

`tes-hook-health@2` must distinguish floor health from ceiling health. A hook
can be installable and floor-green while still missing ceiling evidence. Missing
P0 evidence must make ceiling status fail or remain unavailable.

### Hook Audit Prompt Contract

The audit prompt must assess reason-code propagation, classifier trace,
discoverability, renderer parity, ledger analytics, installed helper parity, and
sanitized evidence. It must not invite generic "green hook" claims.

## Structural Method

```text
STRUCTURAL_METHOD=tes-python-runtime-adapter
runtime_target=local-python-hook
primary_language=python
primary_surface=scripts/**
adapter_surface=src/adapters/**
documentation_surface=docs/**
```

Implementation must prefer existing Python runtime scripts and existing oracle
entrypoints. Split files only when line budget, extension boundaries, or
duplicate ownership make the split safer than an internal section.

Required probes for each material unit:

- `wc -l` on touched runtime and oracle files before and after the change;
- `rg` for protocol tokens, raw command fields, host labels, and private
  vocabulary exposure where relevant;
- `python3 -m py_compile` for changed Python files;
- the smallest red-capable oracle named by the unit;
- `git diff --check`.

## Specialist Roles And Tree Adversary Intake

These are execution roles, not parallel write permissions: Contracts Senior
owns protocol shape and release identity; Runtime Senior patches only the unit
owner path; Tests Senior owns red-capable oracles; Reviewer Senior is read-only;
Evidence/Oracle Senior keeps evidence sanitized and availability honest.

```text
tree_adversary_status=OBJECTIONS_REPAIRED
adversary_objections=legacy-track collision; mixed contract ownership; renderer before discoverability; generic redaction proof; late audit/release identity
adversary_repair_evidence=archived prior hook-ceiling tracks and repaired this Super SPEC
```

Tree Adversary input packet:

- anchor: ADR 0009 path and hash above;
- generated tree: this Super SPEC path;
- source evidence: ADR 0009, `docs/architecture/PRETOOLUSE-CONTRACT.md`,
  current PreToolUse/runtime/audit/package oracles, and current Git status;
- declared constraints: no runtime work in this materialization, no remote
  action, no raw private evidence, one unit at a time.

Required attacks remain: facade oracle, decorative topology budget, unproven
axis, ceiling collapse, shared-contract looseness, context handoff loss, and
unsafe authority. New objections route to `NEEDS_TREE_REPAIR` before prompt use.

## Fixed Materialization Tree

### 1. Canonical Artifact

Anchor: ADR 0009 at
`docs/adr/0009-pretooluse-ceiling-contract-and-hook-topology.md`, hash
`0deb168a61b4f0ca57103bb96619768863c984c03fd609e8b7b233fe852c3093`.
Generated Super SPEC:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-adr-0009-pretooluse-ceiling-linear-slices.md`.

### 2. Certified Context

Surface: Platform PreToolUse hook/runtime behavior. Baseline: current
`PASS_BASIC` floor from source/package oracles. Ceiling is not certified until
ADR 0009 diagnostic power, drift attribution, and host-aware evidence pass.

### 3. Shared Contracts

Shared contracts: `pretooluse_decision@2`, host renderer contract,
`tes-hook-health@2`, and hook audit prompt ceiling assessment. Extension is
additive only; missing extension point routes to `NEEDS_CONTRACT_EXTENSION_POINT`.

### 4. Phase Boundary

This artifact prepares execution only. Runtime, packaging, audit prompt,
evidence, release identity, and final closure changes happen later, in ordered
units, with one current-unit diff at a time.

### 5. Non-Objectives

No runtime edits, installed-target mirror patches, version bump, release,
remote sync, marketplace action, or raw private evidence are authorized here.

### 6. Central Rule

```text
One slice, one runtime ambiguity, one red-capable oracle, one local commit.
```

### 7. Forbidden Moves

Do not skip units, merge units, self-clear Tree Adversary, claim
`PASS_CEILING` from floor evidence, flatten host renderers, add guessed broad
allowlists, persist raw commands, or stage unrelated files.

### 8. Execution Units

Declared order: `SPEC-000` preflight, `SPEC-001` v2/redaction, `SPEC-002`
reason codes, `SPEC-003` classifier trace, `SPEC-004` renderer parity,
`SPEC-005` discoverability, `SPEC-006` dedup, `SPEC-007` installed helpers,
`SPEC-008` hook-health split, `SPEC-009` audit prompt, `SPEC-010` evidence,
`SPEC-011` release identity, `SPEC-012` closure audit.

### 9. Subagent Ownership

Writer stays centralized for sequential commits. Reviewer and evidence roles
are read-only unless the owner explicitly authorizes delegation.

### 10. Per-SPEC Oracles

Each unit below names focused proof. Runtime/integration units must carry
`STRUCTURAL_METHOD=tes-python-runtime-adapter`, executable topology probes,
oracle class/strength, runtime smoke where wiring is touched, and incremental
audit-prompt updates whenever the unit changes audit-visible evidence.

### 11. Negative Grep

Semantic deny checks must cover raw command exposure, private vocabulary,
host-renderer leakage into generic kernel code, guessed discoverability
allowlists, stale ceiling claims, and forbidden remote/destructive actions.

### 12. Commit Strategy

`SPEC-000` is no-commit by default. Each material unit after it requires one
non-empty local commit, current-unit staging only, `git show --stat --oneline`,
post-commit status, and sync status. Runtime, packaging, and audit units are
local source commits only; the package is not sealed until `SPEC-011`. Remote
sync is not requested.

### 13. Review Loop

For each unit: inspect current diff, reject unrelated files and forbidden
moves, run focused oracles and negative checks, repair until green or stop,
review current-unit diff, commit locally, record evidence, then advance.

### 14. Stop States

Use `GO`, `PASS_BASIC_WITH_CEILING_GAPS`, `NEEDS_TREE_ADVERSARY`,
`NEEDS_TREE_REPAIR`, `NEEDS_DISCOVERABILITY`, `NEEDS_INTEGRATION_ORACLE`,
`AXIS_UNPROVEN`, `NEEDS_EVIDENCE`, `NEEDS_OWNER_DECISION`,
`SAFETY_BLOCKED`, or `BLOCKED`.

### 15. Final Delivery Contract

Final closeout must report unit count, files changed, commits, oracles,
negative checks, Tree Adversary result, sync status, release identity decision,
pending owner decisions, and whether ceiling evidence reaches `PASS_CEILING`.

## Linear Units

### SPEC-000 Preflight And Baseline

Goal: verify ADR 0009 hash, read the current PreToolUse/runtime/audit/package
surfaces, and name the protected `PASS_BASIC` baseline before touching files.
Allowed edits: none by default. Stop if the anchor changed, baseline fails for
unrelated reasons, or the executor cannot name the protected baseline.

### SPEC-001 Runtime Record Envelope And Redaction

Goal: materialize the `pretooluse_decision@2` ledger envelope with redacted
command evidence. Ambiguity: v2 must prove command-related decisions without
raw secret-bearing command text. Territory: `scripts/tes_install.py`,
`scripts/host_runtime_matrix_oracle.py`, required fixtures only. Proof:
matrix self-test, Mantra Gate self-test, and a `record_hook_execution` fixture
that writes a ledger row exposing `command_category` plus redaction state, not
raw command text.

### SPEC-002 Reason Code Propagation

Goal: persist `reason_codes[]` from kernel and session decisions into v2
runtime rows. Ambiguity: advisory silence, hard blocks, Cortex advisories, and
anti-cry-wolf suppression must remain explainable after the hook runs.
Territory: `scripts/pretooluse_kernel.py`, `scripts/pretooluse_session.py`,
`scripts/tes_install.py`, direct oracles. Proof: kernel oracle, session oracle,
Mantra Gate self-test, matrix self-test, including `anti_crywolf_suppressed`
and `cortex_advisory_no_write` where their scenarios apply.

### SPEC-003 Classifier Trace And Payload Source Evidence

Goal: preserve classifier trace and payload source evidence from host payload to
runtime decision. Ambiguity: raw tool label, normalized tool, path match, patch
extraction source, and payload source must be attributable without host renderer
logic leaking into the kernel. Territory: kernel, session, matrix oracle, owned
fixtures. Proof: kernel trace fields, matrix payload-source evidence, and `rg`
showing no host renderer output protocol tokens in the generic kernel.

### SPEC-004 Renderer Trace And Parity Ownership

Goal: keep host renderer parity owned by the Mantra Gate oracle while the host
matrix consumes the result. Ambiguity: host-specific renderer semantics must be
verified without duplicated or flattened renderer logic. Territory:
`scripts/tes_install.py` for runtime renderer behavior,
`scripts/mantra_gate_pretooluse_oracle.py` for parity fixtures, matrix oracle,
and topology oracle only if ownership checks need updating. Proof: Mantra Gate,
matrix, and runtime topology self-tests.

### SPEC-005 Discoverability End To End

Goal: make unknown mutating-looking governed tools surface
`needs_discoverability` through runtime output, ledger row, and audit trace.
Ambiguity: the system must refuse false certainty when a governed tool is
unknown after renderer ownership is fixed. Territory: existing
classifier/session/runtime discoverability owners and their oracles. Proof:
unknown mutating-looking fixture returns `needs_discoverability`, no broad
guessed allowlist is added, and matrix output distinguishes discoverability from
ordinary floor pass.

### SPEC-006 Ledger Analytics And Dedup Semantics

Goal: make v2 analytics and dedup keys diagnostic enough to explain repeated
events without losing real duplicates. Ambiguity: Cursor batches, repeated
paths, and identical command categories must dedupe for the right reason.
Territory: `scripts/tes_install.py`, owned hook-health/runtime fixtures, direct
analytics oracles. Proof: dedup key includes host, tool, risk, path or command
category, session, mode, and marker material where relevant; Cursor batches do
not collapse unrelated events; exact duplicates are still caught.

### SPEC-007 Installed Helper Packaging And Simulation

Goal: prove installed helper copies preserve the v2 contract under a simulated
host entrypoint. Ambiguity: repository source must not be green while installed
target helpers drift. Territory: bundle/install/helper packaging paths and owned
packaging fixtures. Proof: installed `.tes/bin/pretooluse_kernel.py`,
`.tes/bin/pretooluse_session.py`, and helper parity simulations; reference
package validation; matrix remains green or reports explicit ceiling gaps.

### SPEC-008 Hook Health Floor Ceiling Split

Goal: introduce `tes-hook-health@2` or an additive compatible extension that
separates floor status from ceiling status. Ambiguity: installability must not
be mistaken for ceiling diagnostic power. Territory: hook-health generation,
fixtures, `scripts/tes_install.py`, matrix oracle. Proof: floor can pass while
ceiling reports missing fields; ceiling cannot pass with absent ADR 0009 P0
evidence; v1 consumers remain compatible or receive an explicit migration path.

### SPEC-009 Audit Prompt Ceiling Projection

Goal: run the final audit-prompt projection sweep after earlier units updated
audit-visible evidence incrementally. Ambiguity: audit language must not
encourage generic hook-health claims or lag runtime evidence. Territory:
`docs/install/HOOK-AUDIT-PROMPT.md`, `scripts/hook_audit_prompt_oracle.py`, TDS
indices only if metadata changes. Proof: audit prompt self-test, TDS validation,
and checks for reason codes, classifier trace, discoverability, renderer parity,
ledger analytics, installed helper parity, and evidence redaction.

### SPEC-010 Sanitized Installed Evidence And Canary Packet

Goal: record native or simulated installed evidence without leaking private
project vocabulary or pretending unavailable native evidence is green.
Ambiguity: installed-target evidence must be real, sanitized, and host-attributed.
Territory: sanitized `docs/evidence/reports/hooks/**`, `~/Dev/tes-canaries`
only when explicitly available and authorized, evidence validators, private
vocabulary oracle. Proof: native evidence exists or status remains
`NEEDS_EVIDENCE`; no private vocabulary enters tracked content; canary replay
status is explicit when used.

### SPEC-011 Release Identity Decision

Goal: decide package version and public bundle identity after delivered behavior
changes. Ambiguity: adopter-visible runtime, audit, or packaging behavior must
not ship under stale identity. Territory: version constants, manifests,
`docs/dist/**`, checksums, public index surfaces, and correlation-rule updates.
Proof: patch bump and correlated bundle update unless the owner explicitly keeps
the version; reference package validation; release check only after an
authorized release tag; no remote action without a separate explicit request.

### SPEC-012 Final Ceiling Closure Audit

Goal: determine the honest final status after all prior units.
Ambiguity: the result must be classified as actual `PASS_CEILING` or floor-green
with ceiling gaps. Territory: closure reports, indices, and missing final oracle
repair only; no new feature work unless a previous unit is reopened. Proof: all
focused runtime oracles, TDS validation, reference package validation,
`npm run commit:check`, and installed-target or canary audit when native
evidence is required and authorized.

Allowed final statuses: `GO`, `PASS_BASIC_WITH_CEILING_GAPS`,
`NEEDS_DISCOVERABILITY`, `NEEDS_EVIDENCE`, `NEEDS_OWNER_DECISION`,
`SAFETY_BLOCKED`, `BLOCKED`.

## Commit And Status Contract

Each material unit after SPEC-000 should end in either one local commit or a
named stop state. Empty commits are forbidden. Remote sync is not requested.

Every closeout must report:

- unit id;
- files touched;
- oracle commands and status;
- exact stop state;
- release identity decision when adopter-visible behavior changed;
- Tree Adversary result before implementation begins.

## Prompt Emission Status

This Super SPEC has repaired the owner-provided Tree Adversary objections and
is ready as the anchor for later maestral prompt emission. The prompt itself is
not emitted by this artifact.

```text
PROMPT_STATUS=SUPER_SPEC_MATERIALIZED
TREE_ADVERSARY_STATUS=OBJECTIONS_REPAIRED
NEXT_ALLOWED_ACTION=load the maestral prompt template before prompt emission
```
