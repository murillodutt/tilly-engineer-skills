---
tds_id: roadmap.goal_super_spec_host_aware_runtime_contracts
tds_class: roadmap
status: active
consumer: maintainers, runtime authors, hook authors, installer authors, adapter authors, oracle authors, release reviewers, execution agents, and audit agents
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Super SPEC: Host-Aware Runtime Contracts

Status: active execution plan. This document materializes ADR 0008 through an incremental `tes-goal-maestro --execute-loop` run. It does not deliver runtime behavior by itself; delivery occurs only through committed SPEC units with executable host oracles.

Capability: make host-aware runtime contracts a package-wide executable discipline for TES surfaces that cross Claude Code, Codex, Cursor, Git hook managers, installers, bootloaders, skills, MCP, Field Reports, Cortex, Mantra Gate, or future host boundaries.

## Canonical Artifact

Canonical Super SPEC: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-host-aware-runtime-contracts.md`

Primary decision source: `docs/adr/0008-host-aware-runtime-contracts.md`

Related decisions: `docs/adr/0004-tes-capsule-isolation-and-reversible-installation.md`; `docs/adr/0007-cortex-proactive-memory-and-mesh-drift.md`

Baseline commit: `1f118042`

Baseline release: `0.3.202`

Loop feedback bridge: `.tes/FEEDBACK-LOOP.md` (local-only, untracked, advisory)

## Anchor Packet

| Field | Value |
|-------|-------|
| `anchor_class` | `ADR` |
| `anchor_path` | `docs/adr/0008-host-aware-runtime-contracts.md` |
| `anchor_sha256` | `e628052b39ee76e8dc12a5abeb1eba402081c80816ad28350529bcdc6a277842` |
| `anchor_origin` | active owner request in the current thread |
| `quality_ceiling` | host-aware runtime contracts with executable proof per host, not config-only delivery |
| `ambition_directive` | break through the ceiling, not hit the floor |

## Mission

Materialize ADR 0008 as a runtime-first, host-aware, oracle-backed package discipline. The implementation must preserve existing TES behavior while preventing future hook/runtime work from flattening Claude Code, Codex, Cursor, native Git hooks, Husky, Lefthook, or project-owned config into one fake universal contract.

## Central Rule

```text
Shared semantic core.
Host-specific projection.
Executable proof per host.
Installer ownership before write.
```

TES runtime surfaces may share intent, but they must not share an invented host contract. Config written is not runtime certified. A hook that is installed but orphaned by `core.hooksPath`, host trust, reload state, feature flag, or project-owned routing is not fully delivered until that state is detected and reported.

## Phase Boundary

This phase may design and materialize source behavior, fixtures, oracles, host contract docs, installer owner detection, adapter templates, skill/preset routing, public/product docs, and release identity updates when required by delivered behavior.

This phase must not push, tag, publish, release, use secrets, perform destructive Git, mutate cloud/marketplace state, edit `tmp/project-mem0/**`, copy reference implementation code, or claim live host UI firing when only fixture/install proof exists.

## Non-Objectives

- Do not replace ADR 0007 or reimplement Cortex unless a SPEC proves a host-aware gap.
- Do not create a universal hook protocol.
- Do not duplicate full runtime protocols into bootloaders.
- Do not make ordinary successful supervision verbose.
- Do not auto-run `/tes-align`.
- Do not let Cortex write the operating mesh.
- Do not certify delivery from installed mirrors or config presence alone.
- Do not update README, HTML, public pages, or user manuals unless adopter-visible behavior changes.
- Do not rely on memory for volatile host, hook, package, framework, or MCP behavior.

## Shared Contracts

### `host_runtime_contract`

Declared in ADR 0008. Any delivered host/runtime surface must have source-derived host identity, lifecycle events, payload shape, output contract, block/advisory semantics, install path, config owner, idempotency behavior, trust/reload requirements, timeout behavior, observable proof, and a negative wrong-host fixture.

### `semantic_core_projection`

Shared TES behavior belongs in a semantic core or source-owned contract. Claude Code, Codex, Cursor, Git hook managers, MCP, and adapter surfaces receive host-specific projections. Bootloaders stay thin.

### `feedback_loop_bridge`

`.tes/FEEDBACK-LOOP.md` is a local-only advisory channel from an audit/mentor window to the `tes-goal-maestro --execute-loop` window. It is lower authority than owner request, ADR/SPEC, source, tests, oracles, and Git evidence. The executor reads it, considers it, records material action in the loop ledger or commit evidence, and never treats it as source of truth.

### `release_identity`

Delivered host behavior, installer behavior, helper/runtime scripts, adapter materialization, public docs, MCP, Field Reports, Cortex, Mantra Gate, or command routing changes require a release-identity decision. Default is patch bump and correlated bundle/public surfaces unless the owner explicitly defers.

## Engineering Method Profile

`STRUCTURAL_METHOD=tes-host-aware-runtime-contracts`

Method packet:

- one semantic core or declared contract per capability;
- host-specific wrappers, templates, or output serializers;
- host contract fixtures before runtime claims;
- no build/typecheck-only proof for integration;
- no growth into a god script;
- installer writes only after owner/routing detection;
- topology probes for every new runtime or hook surface;
- failed hook/runtime attempts must classify `bug_vs_architecture` before retry.

## Reference Boundary

Primary reference: `tmp/project-mem0/mem0/integrations/mem0-plugin/**`

Transferable lessons: host matrix, wrappers per host, inject-not-decide hooks, hot-path tolerance, idempotent install/update, platform-specific scripts, prompt/read lifecycle context, production-regression tests, and explicit host capability gaps.

Non-transferable: code, identifiers, branding, API assumptions, storage model, cloud assumptions, secrets, target-specific examples, or implementation paths.

## Feedback Loop Protocol

The execution loop SHALL read `.tes/FEEDBACK-LOOP.md`:

- once during SPEC-000 after baseline status;
- before opening each later `ACTIVE_SPEC`;
- before committing a SPEC if more than five minutes passed since the last read;
- immediately when the auditor explicitly marks `status=INTERVENTION_REQUIRED`.

The executor SHALL NOT edit `.tes/FEEDBACK-LOOP.md` unless the owner explicitly asks. It may quote compact feedback into the loop ledger or closeout. If feedback conflicts with ADR/SPEC/source/oracles, stop with `NEEDS_REVIEW` and name the conflict. If feedback is stale, irrelevant, or lower authority, continue and record why.

## Subagents

1. **Host Contracts Senior**
   - Owns Claude Code, Codex, Cursor, native Git, Husky, Lefthook, and project-owned hook/config contract discovery.
   - Must verify uncertain behavior through source, official docs, Context7/MCP, installed source, or executable fixtures.

2. **Runtime/Installer Senior**
   - Owns `scripts/**` changes, consumer classification, runtime helper topology, installer hook-owner detection, idempotency, and preservation of foreign hooks/config.

3. **Skills/Adapters Senior**
   - Owns bootloader thinness, skill/preset routing, adapter templates, command triggers, and no-duplication discipline.

4. **Reviewer Senior**
   - Attacks host-contract flattening, config-only proof, scope inflation, copied reference implementation, noisy success behavior, and false closure.

5. **Evidence/Oracle Senior**
   - Owns focused commands, negative checks, host fixture evidence, commit proof, release identity decision, and sync status.

## First Mandatory Act

Run and record:

- `git status --short --branch --untracked-files=all`
- `shasum -a 256 docs/adr/0008-host-aware-runtime-contracts.md`
- read `AGENTS.md`, `.claude/CLAUDE.md`, ADR 0008, ADR 0007, ADR 0004, this Super SPEC, `.tes/FEEDBACK-LOOP.md` if present, `src/adapters/**`, relevant `scripts/*hook*`, `scripts/*oracle*`, `scripts/tes_install.py`, existing Cortex/Mantra Gate host oracles, and `tmp/project-mem0/mem0/integrations/mem0-plugin/**` reference surfaces
- classify every planned `scripts/**` change by consumer before editing

## Pre-Execution Tree Adversary

Before the first runtime edit, run a read-only adversarial review.

Required result:

- `tree_adversary_status=ADVERSARY_CLEARED` or `OBJECTIONS_REPAIRED`
- `adversary_objections=<none or compact list>`
- `adversary_repair_evidence=<tree or prompt repair summary>`

Attack at least:

- host-contract flattening;
- config-only certification;
- build/typecheck-only integration proof;
- installer writes before hook-owner detection;
- native Git/Husky/Lefthook orphaned hooks;
- noisy default feedback;
- Cortex writing mesh or auto-running `/tes-align`;
- copied mem0-plugin implementation;
- bootloader protocol duplication;
- unauthorized remote/destructive/release authority.

## Declared Ordered Units

Declared order is exact:

1. SPEC-000 Preflight, Anchor, And Host Inventory
2. SPEC-001 Host Contract Registry And Fixture Oracles
3. SPEC-002 Runtime Topology And Shared Contract Probes
4. SPEC-003 Agent Host Projections
5. SPEC-004 Git Hook Manager Awareness
6. SPEC-005 Skills, Adapters, And Product Boundary
7. SPEC-006 Documentation, Reference Boundaries, And User Surfaces
8. SPEC-007 Release Identity And Local Certification

Do not execute a later SPEC until the prior SPEC is validated and locally committed when it changes tracked files.

### SPEC-000: Preflight, Anchor, And Host Inventory

Objective: establish baseline, verify ADR anchor, read current TES surfaces, extract mem0-plugin reference lessons, read `.tes/FEEDBACK-LOOP.md`, and produce the execution inventory without runtime edits.

Allowed files: none unless the Super SPEC itself needs typo-level repair before execution starts.

Forbidden moves: runtime edits, script edits, adapter edits, installer edits, package/version/bundle edits, public docs edits, remote sync.

Focused oracles: `python3 scripts/validate_reference_package.py`; `python3 scripts/validate_tds.py`; `python3 scripts/materialize_adapter.py all --check`; existing host/runtime self-tests discovered in source; `git diff --check`.

Negative checks: no changed runtime files; no copied mem0 implementation; no host claim without source evidence; no unread feedback bridge.

Commit message: none unless the Super SPEC required repair.

Completion evidence: host inventory, hook manager inventory, scripts consumer classification, mem0 reference extraction, feedback loop read timestamp, oracle output, post-SPEC Git status.

### SPEC-001: Host Contract Registry And Fixture Oracles

Objective: create or consolidate executable host-contract fixtures and oracles that prove affected Claude Code, Codex, Cursor, native Git, Husky, Lefthook, and project-owned hook/config behavior.

Allowed files: focused fixture/oracle files, host contract docs, this Super SPEC if repair is required, TDS/index surfaces required by changed docs.

Forbidden moves: runtime delivery, installer behavior change, adapter materialization change, release bump, or claims from prose-only host notes.

Focused oracles: host-contract fixture self-test; `python3 scripts/platform_surface_oracle.py --self-test`; existing Cortex/Mantra host contract oracles; `git diff --check`.

Negative checks: wrong-host fixture fails; Cursor is not treated as exit-code blocking; native Git is not treated as Husky or Lefthook; config presence is not runtime certification; fixture cannot pass without checking output shape.

Commit message: `test(hosts): add host-aware runtime contract fixtures`

### SPEC-002: Runtime Topology And Shared Contract Probes

Objective: harden shared runtime topology so TES capabilities expose semantic intent once and host-specific projections separately, with executable topology probes.

Allowed files: focused runtime contract helpers, topology probes, related fixtures, docs/mesh references, and TDS/index surfaces required by changed docs.

Forbidden moves: god-script expansion, full protocol duplication in bootloaders, mesh writes by Cortex, automatic `/tes-align`, host-specific protocol inside the semantic core.

Focused oracles: topology probe self-test; relevant runtime self-tests; `python3 scripts/materialize_adapter.py all --check`; `git diff --check`.

Negative checks: semantic core does not emit one flattened host output; bootloaders do not copy the full contract; advisory clean path stays quiet.

Commit message: `runtime: add host-aware topology probes`

### SPEC-003: Agent Host Projections

Objective: apply or repair Claude Code, Codex, and Cursor projections so each host receives the right lifecycle events, output contract, advisory/block semantics, timeout behavior, and install/materialization shape.

Allowed files: `src/adapters/**`, focused host adapter templates, host hook/runtime scripts, fixtures/oracles, installer materialization code only when required by projection delivery, correlated docs.

Forbidden moves: fake universal hook adapter, copied host protocol across hosts, noisy clean success output, hard block for ordinary work, mesh writes, automatic `/tes-align`.

Focused oracles: per-host projection fixture; materialization check; platform surface oracle; runtime smoke oracle for each affected host contract; `git diff --check`.

Negative checks: Claude, Codex, and Cursor output contracts are independently proven; host-specific fields do not leak across hosts; host-unobservable limits are reported honestly.

Commit message: `adapters: project runtime contracts per agent host`

### SPEC-004: Git Hook Manager Awareness

Objective: fix or formalize installer behavior for native Git hooks, Husky, Lefthook, and project-owned hook routing so TES hooks cannot be silently orphaned by `core.hooksPath` or another hook manager.

Allowed files: installer scripts, hook templates, install/idempotency fixtures, docs/install references, Field Reports hook surfaces if affected, correlated package surfaces if delivered behavior changes.

Forbidden moves: destructive overwrite of project hooks, writing `.git/hooks/**` while ignoring active `core.hooksPath`, assuming Husky or Lefthook without source evidence, silent failure when hook owner is unsupported.

Focused oracles: installer self-test; hook-manager idempotency fixture; orphaned-hook regression fixture; installed-target smoke against a fixture target, not the package root; `git diff --check`.

Negative checks: native Git, Husky, and Lefthook paths are distinct; reinstall does not duplicate drains; foreign hooks are preserved or explicitly reported; unsupported hook owners return `NEEDS_REVIEW` rather than false `PASS`.

Commit message: `installer: respect host hook manager ownership`

### SPEC-005: Skills, Adapters, And Product Boundary

Objective: align skills, command triggers, adapter docs, and product surfaces with host-aware runtime contracts without turning them into human checklists or duplicating protocols.

Allowed files: skill sources, adapter rules, command trigger docs, docs/adapters, docs/mesh, relevant manifests, materializer code when source projection changes.

Forbidden moves: full protocol in skill text, noisy default feedback, maintainer-only rules in product surfaces, README/HTML edits unless user-facing entrypoint behavior changes.

Focused oracles: command trigger oracle; adapter materialization check; platform surface oracle; relevant skill self-tests; `git diff --check`.

Negative checks: skills invoke lenses and host-aware discipline but do not become enforcement scripts; product docs describe delivered behavior only.

Commit message: `adapters: align host-aware runtime product surfaces`

### SPEC-006: Documentation, Reference Boundaries, And User Surfaces

Objective: document delivered host-aware behavior where it actually changed, keep maintainer docs and user docs separated, and preserve reference boundaries.

Allowed files: docs/mesh, docs/adapters, docs/install, docs/tds, docs/INDEX, public/user docs only when adopter-visible behavior changed.

Forbidden moves: documenting unimplemented behavior as delivered, mem0 branding as TES behavior, private vocabulary, README/HTML changes for maintainer-only work.

Focused oracles: `python3 scripts/validate_tds.py`; `python3 scripts/validate_reference_package.py`; public docs checks only if public docs changed; private vocabulary oracle; `git diff --check`.

Negative checks: no copied reference identifiers; no universal hook claims; no config-only certification language; no target-specific paths or private names.

Commit message: `docs: document host-aware runtime contracts`

### SPEC-007: Release Identity And Local Certification

Objective: decide and implement release identity for any delivered behavior, update correlated bundle/version/public surfaces when required, and certify locally without unauthorized remote action.

Allowed files: package version surfaces, docs/dist, index/sha256 sidecars, validators, correlated docs/source surfaces from earlier SPECs.

Forbidden moves: push, tag, publish, marketplace, cloud, secrets, destructive Git, or release claim without explicit owner authorization.

Focused oracles: `npm run commit:check`; `npm run commit:closure` if claiming sealed local package; full host contract fixture suite; materialization check; reference package validation; TDS validation; `git diff --check`.

Negative checks: no stale version/bundle pointer; no unproved host; no copied reference implementation; no private vocabulary; no remote-release claim.

Commit message: `release: certify host-aware runtime contracts`

## Full Oracle And Closeout Run

Use the source-discovered exact commands, including at minimum:

- `python3 scripts/validate_reference_package.py`
- `python3 scripts/validate_tds.py`
- `python3 scripts/materialize_adapter.py all --check`
- `python3 scripts/platform_surface_oracle.py --self-test`
- host contract fixture suite created or reused by SPEC-001
- installer/hook-manager fixture suite created or reused by SPEC-004 when installer behavior changes
- `npm run commit:check`
- `npm run commit:closure` only when claiming sealed local package
- `git diff --check`

## Negative Grep

- No copied mem0-plugin implementation code or identifiers in TES source unless clearly cited as reference-only docs.
- No fake universal hook contract.
- No config-only runtime certification.
- No bootloader full-protocol duplication.
- No noisy default feedback for successful advisory supervision.
- No Cortex mesh writer or automatic `/tes-align`.
- No Git hook manager flattening.
- No remote, push, publish, tag, marketplace, cloud, destructive action, secrets, private project names, or target-specific paths in tracked content.
- No broad lexical grep that rejects valid `BLOCKED`, `NEEDS_REVIEW`, `HOST_UNOBSERVABLE`, or status vocabulary.

## Per-Unit Completion Evidence

Each committed unit must report:

- changed files;
- scripts consumer classification;
- focused oracles;
- negative checks;
- structural method result;
- topology probe result where applicable;
- runtime smoke result where applicable;
- feedback loop read timestamp and material response;
- reviewer result;
- semantic commit hash;
- `git show --stat --oneline <commit>`;
- post-commit Git status;
- sync status: `LOCAL_COMMITTED`, `REMOTE_SYNCED`, `REMOTE_SYNC_NOT_REQUESTED`, or `SYNC_BLOCKED`.

## Stop States

- `GO`: active SPEC is bounded, validated, committed locally when needed, and may advance.
- `NEEDS_OWNER_DECISION`: release identity, public bundle, remote sync, host behavior, version bump, public/user docs, or feedback conflict cannot be safely inferred.
- `NEEDS_DISCOVERABILITY`: a host behavior claim cannot be discovered from source, official docs, MCP/context tools, installed source, or reference evidence.
- `NEEDS_INTEGRATION_ORACLE`: hook/runtime integration has only build/typecheck/lint/materialization proof.
- `NEEDS_STRUCTURAL_METHOD`: topology passes behavior but duplicates protocol, grows into a god script, flattens hosts, or lacks executable topology probe.
- `NEEDS_TREE_REPAIR`: tree adversary finds unrepaired host-contract, oracle, boundary, feedback-loop, or ceiling defects.
- `BLOCKED`: required local oracle fails outside the active SPEC repair scope.
- `SAFETY_BLOCKED`: task requires secrets, destructive actions, private data, bypass, unauthorized release, or unauthorized remote state.

## Ready Execution Prompt

Use this prompt in the execution window:

```text
/tes-goal-maestro --execute-loop read, analyze, and implement docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-host-aware-runtime-contracts.md. Do not restart from zero. The anchor is docs/adr/0008-host-aware-runtime-contracts.md with SHA-256 e628052b39ee76e8dc12a5abeb1eba402081c80816ad28350529bcdc6a277842. Our target is not to hit the floor; it is to break through the ceiling.

Before each ACTIVE_SPEC and before any commit when more than five minutes passed since the last read, read .tes/FEEDBACK-LOOP.md as advisory mentor feedback. Treat it as lower authority than owner request, ADR/SPEC, source, oracles, and Git evidence. If it conflicts with the execution tree, stop with NEEDS_REVIEW and name the conflict. Do not edit .tes/FEEDBACK-LOOP.md unless the owner explicitly asks.
```

## Final Delivery Contract

Report units executed, files changed, commits, oracles, negative checks, host matrix status, hook manager status, feedback loop usage, reference boundary status, release identity decision, sync status, boundaries preserved, unresolved ambiguities, and remaining owner decisions.
