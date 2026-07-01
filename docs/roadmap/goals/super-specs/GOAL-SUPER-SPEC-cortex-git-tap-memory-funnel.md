---
tds_id: roadmap.goal_super_spec_cortex_git_tap_memory_funnel
tds_class: roadmap
status: active
consumer: maintainers, Cortex runtime authors, installer authors, hook authors, oracle authors, release reviewers, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# GOAL-SUPER-SPEC: Cortex Git Tap Memory Funnel

Status: active corrective/product Super SPEC.

Purpose: add a Git-driven observation lane for Cortex so commits, staged
changes, and branch switches become a reliable memory-maintenance funnel without
letting Git hooks write durable memory into `docs/**` automatically.

## Evidence Base

The graphify hook design exposed a mature pattern that Cortex should reuse
conceptually, not copy wholesale:

- use `post-commit` and `post-checkout` for expensive freshness work;
- keep `pre-commit` cheap and reserved for validation or event capture;
- launch background work detached so Git returns immediately;
- write logs to a cache path rather than stdout-heavy hook output;
- skip rebase, merge, and cherry-pick states;
- skip self-generated output paths to avoid rebuild loops;
- resolve the runtime interpreter at install time with safe fallbacks;
- append marked hook blocks instead of replacing existing user hooks;
- respect `core.hooksPath` and hook-manager layouts;
- use start/end markers for uninstall safety;
- serialize rebuilds with a lock and queue pending paths when another rebuild is
  already running;
- keep the hook deterministic and no-LLM by default;
- treat reflective memory updates as an optimization, not as the only way memory
  becomes available.

The Cortex learning from the CORTEX runtime-memory canary adds a second
constraint: memory is powerful only when available at runtime, but durable memory
must remain curated. Git is an excellent observation funnel; it is not an
unreviewed memory writer.

## Central Rule

```text
Git hooks may capture, classify, queue, and propose Cortex memory. They must not
write durable curated memory into docs/** without an explicit curation step.
```

## Platform Classification

This work is `Platform` in the product/source layer when delivered to installed
targets. It touches Git hooks, installer behavior, Cortex runtime events, local
runtime ledgers, and memory claims. The first implementation may be narrow, but
it is not a maintainer-only experiment if an adopter receives the hook.

## Protected Baseline

Preserve these baselines:

- existing pre-commit and pre-push quality gates remain authoritative;
- Field Reports drain remains separate from quality enforcement;
- existing user hooks and hook-manager files are preserved;
- `core.hooksPath`, Husky-style layouts, native hooks, and hook chaining stay
  supported;
- Cortex recall remains read-oriented unless a specific curate/write command is
  invoked;
- raw diffs, raw prompts, tool inputs, secrets, credentials, and private local
  absolute paths are not written to tracked files;
- hook-triggered background work must not block normal local Git workflows;
- hook evidence strengthens memory maintenance but never replaces package,
  install, Git gate, or Cortex oracles.

## Non-Objectives

- Do not copy graphify implementation or package graphify as a dependency.
- Do not add cloud upload, remote service calls, or background daemon
  requirements.
- Do not run LLM extraction from a Git hook by default.
- Do not auto-edit `docs/**`, `docs/agents/cortex/**`, or curated memory cells
  from a hook.
- Do not make Git hook evidence a substitute for Cortex oracles.
- Do not broaden this into a dashboard or full telemetry platform.

## Required New Surfaces

The exact names may adjust to local conventions, but the implementation must
create these capabilities:

- a source-owned Cortex Git Tap runtime script, likely
  `scripts/cortex_git_tap.py`;
- a focused oracle/self-test surface, likely
  `scripts/cortex_git_tap_oracle.py` or `--self-test` on the runtime script;
- an installer/materialization path that installs or updates Git hooks without
  clobbering existing hooks;
- a Cortex reference contract, likely
  `docs/architecture/CORTEX-GIT-TAP-CONTRACT.md` or an indexed Cortex reference;
- fixtures proving event schema, hook install safety, queue/lock behavior,
  privacy guard, and curation boundary;
- release identity updates if the hook is delivered to target projects.

## Stop States

- `NEEDS_GIT_TAP_CONTRACT`
- `NEEDS_EVENT_SCHEMA`
- `NEEDS_HOOK_INSTALLER_PARITY`
- `NEEDS_PENDING_QUEUE`
- `NEEDS_REFLECT_BOUNDARY`
- `NEEDS_PRIVACY_GUARD`
- `NEEDS_CANARY_EVIDENCE`
- `PASS_CORTEX_GIT_TAP`

## SPEC-001 - Git Tap Event Model

Goal: define the smallest durable local event that lets Cortex understand what
changed without storing raw content.

Create schema `tes-cortex-git-tap@1`.

Required event fields:

- `schema`;
- `timestamp`;
- `event`: `pre-commit`, `post-commit`, `post-checkout`, or `manual-drain`;
- `repo_fingerprint`;
- `branch`;
- `head_before`;
- `head_after`;
- `commit_hash`;
- `parent_hashes`;
- `changed_path_count`;
- `changed_path_categories`;
- `changed_file_extensions`;
- `diff_stat`;
- `staged_digest` when available;
- `gate_snapshot` when available;
- `memory_signal`: `none`, `candidate`, `contract_change`,
  `runtime_learning`, `oracle_learning`, or `docs_memory_change`;
- `privacy_status`;
- `blockers`.

Allowed local runtime storage:

```text
.tes/runtime/cortex/git-tap/events.jsonl
.tes/runtime/cortex/git-tap/pending.jsonl
.tes/runtime/cortex/git-tap/git-tap.log
.tes/runtime/cortex/git-tap/git-tap.lock
```

These runtime paths must be gitignored. Tracked evidence may summarize counts,
hashes, schema versions, and status only.

Oracle:

- self-test writes synthetic events and validates schema;
- malformed JSONL is classified as `FAIL`;
- raw diff content in the event is rejected as `NEEDS_PRIVACY_GUARD`.

Stop state: `NEEDS_EVENT_SCHEMA`.

## SPEC-002 - Hook Placement And Behavior

Goal: use the right Git hook for each cost band.

Required hook responsibilities:

- `pre-commit`: optional lightweight staged snapshot and privacy-safe gate
  signal only; must not run reflection or memory curation.
- `post-commit`: append a committed event and launch background consolidation
  if enabled.
- `post-checkout`: mark Cortex runtime observations stale after branch switches
  and optionally enqueue a refresh event.
- `pre-push`: optional hard gate only when a future SPEC explicitly requires
  pending critical memory curation; not part of this first slice.

Hook install rules:

- preserve existing hooks by appending marked TES blocks;
- use explicit start/end markers;
- uninstall removes only TES-owned blocks;
- respect `core.hooksPath` and user-editable hook-manager locations;
- fail loudly on impossible hook paths instead of creating junk directories;
- local installed hooks may contain an absolute interpreter path when needed,
  but tracked source templates must not contain machine-specific paths.

Oracle:

- fixture with existing hook content proves append/uninstall preservation;
- fixture with `core.hooksPath` proves correct target directory;
- fixture with existing TES block proves idempotence;
- fixture with Windows-style path on POSIX fails safely.

Stop state: `NEEDS_HOOK_INSTALLER_PARITY`.

## SPEC-003 - Queue, Lock, And Background Drain

Goal: commits made during an active Cortex Git Tap run must not lose events.

Rules:

- a per-repo lock serializes consolidation;
- lock losers append pending events instead of dropping work;
- the lock holder drains pending events before and after consolidation;
- background work has a timeout and appends to a log;
- hook-triggered consolidation defaults to no LLM and no durable memory writes;
- a manual command may block on the lock for deterministic certification.

Oracle:

- two simulated post-commit events while locked both appear after drain;
- timeout produces `NEEDS_CANARY_EVIDENCE` or `FAIL` without blocking commit;
- pending queue deduplicates identical path/event fingerprints.

Stop state: `NEEDS_PENDING_QUEUE`.

## SPEC-004 - Privacy And Contamination Boundary

Goal: make Git-derived memory useful without leaking private content or turning
local runtime facts into tracked secrets.

Forbidden in Git Tap events:

- raw diff hunks;
- prompt text or tool payloads;
- file contents;
- secrets or credentials;
- full local absolute paths in tracked artifacts;
- raw host transcript JSONL;
- unredacted command output.

Allowed in local runtime events:

- relative paths;
- path category and extension;
- counts;
- hashes/fingerprints;
- gate statuses;
- commit hashes;
- failure classes.

Allowed in tracked reports:

- schema version;
- event counts;
- pass/fail status;
- anonymized path categories;
- oracle names and statuses.

Oracle:

- fixture with raw diff content fails;
- fixture with secret-like content fails;
- fixture with counts/hashes/categories passes;
- staged private-vocabulary oracle remains clean.

Stop state: `NEEDS_PRIVACY_GUARD`.

## SPEC-005 - Reflect And Curate Boundary

Goal: separate observation from durable memory.

Required behavior:

- Git Tap writes runtime events only;
- `cortex reflect --from-git-tap` or equivalent reads events and emits proposals;
- proposals are local, reviewable, and tagged with evidence hashes;
- durable writes to `docs/**` require an explicit curate/write command;
- hook execution never invokes the durable write path;
- repeated low-value events are compacted or summarized before proposal.

Decision states:

- `NO_MEMORY_SIGNAL`: event captured, no memory proposal needed.
- `PROPOSE_MEMORY`: local proposal created, no durable write.
- `NEEDS_CURATION`: durable memory may be useful but needs explicit action.
- `BLOCKED_PRIVACY`: event cannot be used due to privacy or contamination.
- `CURATED`: explicit command promoted memory to a tracked docs surface.

Oracle:

- post-commit event can create a proposal without modifying `docs/**`;
- explicit curation can write only through the approved Cortex path;
- hook-triggered run that modifies `docs/**` fails the self-test.

Stop state: `NEEDS_REFLECT_BOUNDARY`.

## SPEC-006 - Graphify-Derived Regression Fixtures

Goal: encode the operational lessons that made the graphify hook mature.

Fixtures must prove:

- hook install appends to existing hook content;
- uninstall removes only marked TES blocks;
- install is idempotent;
- `core.hooksPath` is respected;
- hook path parsing rejects impossible cross-platform paths;
- branch checkout event skips ordinary file checkout;
- rebase, merge, and cherry-pick states skip background work;
- self-generated runtime paths do not create loops;
- background launch does not block the Git command path;
- logs append instead of overwriting;
- interpreter/runtime resolution fails loud and non-destructive.

Oracle:

- `scripts/cortex_git_tap.py --self-test` or paired oracle covers every fixture;
- red-capable fixture proves at least one old unsafe behavior fails.

Stop state: `NEEDS_CANARY_EVIDENCE`.

## SPEC-007 - Installed Canary Certification

Goal: prove the Git Tap works in a clean installed target, not only in the TES
source repository.

Required canary:

```text
clean target -> install TES bundle -> enable Cortex Git Tap ->
commit code/doc changes -> inspect hooks -> inspect runtime ledger ->
run reflect proposal -> verify docs/** unchanged until explicit curate ->
run related install/Git/Cortex gates
```

Acceptance:

- hook files contain TES start/end blocks and preserve foreign hook content;
- `core.hooksPath` is reported accurately;
- post-commit event appears in `.tes/runtime/cortex/git-tap/events.jsonl`;
- branch switch creates a stale/checkout event when applicable;
- no raw diff or secret-like content appears in the event ledger;
- reflect proposal exists when a memory-worthy change is committed;
- `docs/**` is unchanged before explicit curation;
- hook-triggered execution cannot modify `docs/**`;
- canary evidence is host-real or installed-target real, not only mocked.

Stop state: `PASS_CORTEX_GIT_TAP`.

## Implementation Order

1. Add the Cortex Git Tap contract/reference and index it.
2. Implement the runtime event writer and self-tests.
3. Implement hook install/update/uninstall using marked blocks and hook-manager
   awareness.
4. Add queue/lock/background drain.
5. Add reflect proposal integration without durable docs writes.
6. Add privacy fixtures and red-capable self-tests.
7. Add installed-target canary replay.
8. Make the release-identity decision and rebuild package surfaces if delivered.

## Validation

Minimum local gates before closing:

- `python3 scripts/cortex_git_tap.py --self-test` or equivalent;
- `python3 scripts/cortex_git_tap_oracle.py --self-test` if split;
- `python3 scripts/tes_install.py --self-test`;
- `python3 scripts/install_smoke.py --route all`;
- `python3 scripts/git_gate_contract.py --self-test`;
- `python3 scripts/canary_admission_oracle.py --self-test`;
- `python3 scripts/installed_certification_oracle.py --self-test`;
- `python3 scripts/validate_tds.py`;
- `python3 scripts/validate_doc_size.py`;
- `npm run commit:check`;
- one installed-target canary replay when implementation reaches delivered
  behavior.

## Closeout Decision

Close as `PASS_CORTEX_GIT_TAP` only when Cortex can observe Git activity,
queue and drain events safely, propose memory from Git Tap evidence, and prove
that no hook-triggered path writes durable memory into `docs/**` without
explicit curation.

Do not claim commercial or ceiling memory automation from this slice alone. This
SPEC creates the funnel and the guardrails; durable memory quality still depends
on Cortex curation and installed-target replay.
