---
tds_id: roadmap.goal_super_spec_tes_postinstall_recovery_contract_symmetry
tds_class: roadmap
status: active
consumer: maintainers, installer authors, oracle authors, adapter maintainers, release reviewers, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Super SPEC: TES Postinstall Recovery Contract Symmetry

Status: active planning artifact; no delivered behavior yet.

Capability: make TES first-session and recovery flows converge truthfully by keeping generators, validators, installed certification, bundle hygiene, and repair routes symmetric across package source and installed targets.

Canonical artifact: `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-postinstall-recovery-contract-symmetry.md`

## Mantra Gate Snapshot

| Field | Decision |
|-------|----------|
| VERIFY | Reviewed GitHub issue #47, the sanitized Field Report payload, a maintainer-local private canary recovery analysis retained outside TES tracked source, `scripts/tes_init.py`, `scripts/project_context_oracle.py`, `scripts/installed_certification_oracle.py`, `scripts/command_trigger_oracle.py`, `scripts/mantra_gate_adoption_oracle.py`, roadmap precedents, and the maintainer correlation rule. |
| SCOPE | Create one governed Super SPEC and index it. No runtime code, package version, bundle rebuild, release, tag, push, publish, marketplace, cloud, or target-project write is authorized by this SPEC alone. |
| BEST_PATH | Treat issue #47 as a contract-symmetry failure family, not a one-off target workaround. Start implementation with neutral failing fixtures, then patch source generators/oracles and replay private canaries outside TES tracked content. |
| DOCUMENT | This Super SPEC plus roadmap/index/TDS correlations and future evidence reports produced during implementation. |
| ORACLE | Planning closeout uses TDS, doc-size, reference-graph, private-vocabulary, and diff-check gates. Implementation must add deterministic package-source and installed-target fixtures before claiming convergence. |
| RESOLVE | none found |
| STATUS | GO for governed implementation planning. |

## Authority

| Source | Role |
|--------|------|
| GitHub issue #47 | Public sanitized Field Report exposing repeated `tes_init:NEEDS_REVIEW` and mixed installer, MCP, Cortex, and Field Reports events. |
| Private canary recovery analysis | Maintainer-local evidence source retained outside TES tracked docs; use only generic references such as `private canary project`. |
| Maintainer correlation rule | Classifies `scripts/**` changes by consumer and forces correlated docs, adapter, version, bundle, and release checks. |
| Installed certification contract | Defines installed-target certification components and partial-state aggregation. |
| Command trigger oracle | Defines preferred triggers, aliases, and natural-intent parity across installed adapters. |
| Mantra Gate adoption oracle | Defines required bootloader-to-owner-skill routing health. |
| Private vocabulary oracle | Protects TES source from project-specific vocabulary and private target details. |

## Problem

TES `0.3.145` can enter a first-session or recovery loop where generated target context is immediately rejected by an oracle that expects a different contract. The issue #47 Field Report is the public sanitized symptom. The private canary analysis shows a concrete family of failures:

- `tes_init.py` writes `docs/agents/PROJECT-CONTEXT.md` from an inventory based on `git ls-files --cached --others --exclude-standard`;
- `project_context_oracle.py` requires some Caution Zones from direct filesystem checks;
- lockfiles ignored by `.gitignore` can therefore be invisible to the generator while still required by the validator;
- manual repairs to generated context are not durable because the next recovery run rewrites the context from the same asymmetric generator;
- installed certification can identify secondary partial states, but the first-session operator sees repeated `NEEDS_REVIEW` before a clear repair route;
- release/bundle hygiene and adapter trigger/adoption drift can surface in the same recovery run, making root cause harder to isolate.

The dangerous behavior is not merely "missing dependency locks." It is a wider anti-pattern:

```text
generator source of truth != validator source of truth
or
installer materialization != installed certification contract
or
published bundle contents != release hygiene oracle
```

When any of those are true, TES can produce false blockers, false greens, or non-durable repair instructions.

## Goal

After this goal is implemented, TES install, first-session recovery, update, doctor, and certification flows must satisfy this equation:

```text
same detected facts + same contract constants + same status semantics
= same generator output, oracle expectation, repair route, and Field Report
```

For the issue #47 class, a neutral target fixture with ignored lockfiles must fail before repair and pass after repair without manual installed-target edits.

## Non-Objectives

- Do not copy private canary names, paths, domain vocabulary, commits, remotes, target docs, target code, raw run records, or raw stack traces into TES.
- Do not patch only installed mirrors such as `.tes/bin/**`, `.agents/skills/**`, `.claude/skills/**`, or `skills/**` in a target project.
- Do not declare a package sealed, released, or remotely certified without `npm run commit:check` and an explicit release identity decision.
- Do not make lockfile handling project-specific to one stack or package manager.
- Do not make every ignored file part of TES project context; only declared contract facts should bypass the git-index inventory.
- Do not weaken oracles merely to remove friction. Generators must satisfy useful validators, or validators must be narrowed with an explicit contract.
- Do not expand MCP write authority, global config writes, cloud behavior, or marketplace behavior.

## Required Status Semantics

| Status | Required Meaning |
|--------|------------------|
| `PASS` | The generated surface, installed certification, and focused oracles agree for the claimed scope. |
| `PARTIAL` | Runtime is usable, but at least one adoption, trigger, hygiene, provenance, or repair-route component is degraded. |
| `NEEDS_REVIEW` | A concrete user or maintainer action is required and must be named in the run record or Field Report. |
| `BLOCKED` | Unsafe, private, destructive, missing-authority, or contract-incoherent state prevents continuation. |
| `DEGRADED` | A component is below contract but still diagnosable without hiding the final certification status. |
| `NOT_AVAILABLE` | A surface or host capability is absent by design and must not be reported as failed or inferred. |

`INSTALLED` may describe a completed write operation. It must not be used as a final certification verdict.

## Assumptions

- The private canary finding is portable TES product evidence because the failing condition can be reproduced with neutral fixture files.
- `scripts/tes_init.py`, `scripts/project_context_oracle.py`, and installed target copies under `.tes/bin/**` are delivered behavior when adopters invoke or certify them.
- Shared constants are preferable to duplicated tuples when generator and validator must agree.
- Filesystem checks are acceptable for narrow root-level contract facts, such as known dependency lockfiles, even when general project inventory remains git-index based.
- A patch release is the default release-identity outcome if delivered runtime behavior changes.

## Contract Symmetry Principles

| Principle | Rule |
|-----------|------|
| One fact set | A generator and its oracle must share names, status semantics, and detection predicates for the same behavior. |
| Fixture before repair | Any canary-reported blocker must become a neutral failing fixture before source repair closes. |
| Repair at source | Portable TES bugs land in `scripts/**`, `src/**`, `docs/**`, and release surfaces, not only in installed target mirrors. |
| Useful strictness | Oracles should remain strict when they protect real behavior; generators must be upgraded to meet them. |
| Honest partials | Install/MCP success cannot hide adapter, context, trigger, hygiene, or provenance failures. |
| Private boundary | Private target evidence is a source-of-record outside TES, never package content. |

## Implementation Units

| Unit | Owned Surfaces | Required Behavior | Required Oracle |
|------|----------------|-------------------|-----------------|
| SPEC-000 Reproducer And Boundary | neutral fixtures, self-tests, evidence notes | Reproduce the issue #47 failure class with a generic target containing a `.gitignore`-ignored root lockfile. Show pre-repair generator output omits `dependency locks` while oracle expects it. Keep private canary evidence off-repo. | New focused fixture must fail before repair and pass after repair; `python3 scripts/private_vocabulary_oracle.py`; `git diff --check`. |
| SPEC-001 Lockfile Contract Symmetry | `scripts/tes_init.py`, `scripts/project_context_oracle.py`, any shared constants module if needed | Generator and oracle share the same root lockfile names and detection predicate for `dependency locks`. Include at minimum `pnpm-lock.yaml`, `npm-shrinkwrap.json`, `package-lock.json`, `yarn.lock`, `uv.lock`, `Cargo.lock`, `composer.lock`, `Gemfile.lock`, `poetry.lock`, and `Pipfile.lock`, unless implementation records a narrower explicit decision. | `python3 scripts/tes_init.py --self-test`; `python3 scripts/project_context_oracle.py --self-test`; neutral ignored-lockfile regression. |
| SPEC-002 Weak Anchor Coverage | `scripts/tes_init.py`, context fixtures | `weak_anchor_triage` and `caution_zones` use a consistent lockfile set. Dependency lockfiles are weak ownership evidence and caution-zone evidence without implying architecture ownership. | Self-test fixture proving lockfiles appear in weak-anchor triage and caution zones with stable language. |
| SPEC-003 Project Context Rewrite Durability | `scripts/tes_init.py`, `scripts/project_context_oracle.py`, postinstall recovery behavior | Recovery runs must not erase user repairs without warning or must regenerate a context that already satisfies the oracle. If manual sections remain unsupported, the run record must say that regeneration rewrites generated sections. | Fixture where repeated recovery remains `PASS` after regeneration; negative case records actionable failure detail. |
| SPEC-004 Oracle Failure Propagation | `scripts/tes_install.py`, postinstall run records, Field Reports payload shaping if touched | When `project_context_oracle.py` fails inside postinstall/recovery, structured failures are copied into the run record and sanitized Field Report evidence hints. `returncode=1` alone is insufficient. | `python3 scripts/tes_install.py --self-test`; fixture proving `commands[].oracle_failures[]` or equivalent structured field appears. |
| SPEC-005 Installed Certification Secondary Drift | `scripts/installed_certification_oracle.py`, `scripts/command_trigger_oracle.py`, `scripts/mantra_gate_adoption_oracle.py`, adapter materialization | Quality-gate path, Mantra Gate adoption, command-trigger parity, and artifact hygiene failures remain distinct components with repair guidance. First-session install must materialize the surfaces the oracles require or report `PARTIAL` with exact repair route. | `python3 scripts/installed_certification_oracle.py --self-test`; `python3 scripts/command_trigger_oracle.py --self-test`; `python3 scripts/mantra_gate_adoption_oracle.py --self-test`. |
| SPEC-006 Rename And Legacy Path Migration | `scripts/tes_legacy_retirement.py`, `scripts/tes_update.py`, generated `docs/agents/QUALITY-GATES.md`, adapter docs if behavior changes | Known retired skill paths such as `tilly-engineer-skills/scripts/discipline_oracle.py` are detected and migrated or reported with a repair route in generated target docs and bootloaders. | Negative grep fixture for stale path; `python3 scripts/tes_legacy_retirement.py --self-test`; `python3 scripts/tes_update.py --self-test`. |
| SPEC-007 Bundle Hygiene And Release Residue | `scripts/tes_bundle.py`, `scripts/materialize_adapter.py`, `scripts/public_bundle_oracle.py`, `scripts/validate_reference_package.py` | `.DS_Store`, `Thumbs.db`, `__MACOSX`, and AppleDouble residue are excluded from adapter materialization, setup bundles, manifests, and public zips. Release claims fail or degrade when residue exists. | `python3 scripts/tes_bundle.py --self-test`; `python3 scripts/public_bundle_oracle.py`; residue negative fixture. |
| SPEC-008 Postinstall Run Retention | `scripts/tes_install.py`, postinstall sentinel docs if needed | `postinstall.json` remains bounded or indexed. Recent runs stay visible; older runs are archived or summarized without losing forensic traceability. | Self-test proving bounded sentinel behavior and archive/index integrity. |
| SPEC-009 Dirty Worktree Signal Quality | `scripts/mantra_gate_adoption_oracle.py`, related docs only if user-visible | Dirty-worktree reporting distinguishes tracked/staged material changes from ignored local files. Ignored local config should not create closure noise unless a closure claim depends on it. | `python3 scripts/mantra_gate_adoption_oracle.py --self-test` with ignored-file and tracked-file fixtures. |
| SPEC-010 Doctor Repair Routes | `src/adapters/*/skills/tes-doctor/SKILL.md`, `docs/install/AGENT-MANUAL.md`, repair helpers if needed | `/tes-doctor` can identify and safely guide repair for contract-symmetry failures: context oracle mismatch, stale quality-gate path, missing Mantra Gate route, trigger parity drift, and residue. Repairs remain source-aware and never patch installed mirrors as the only fix. | Doctor route fixture or oracle; platform surface oracle if docs/adapter routing changes. |
| SPEC-011 Field Reports Actionability | `scripts/field_reports.py`, Field Reports oracles, GitHub receiver docs if needed | Field Reports for this class include product class, certification impact, owner surface, next action, dedupe fingerprint, status counts, and sanitized failure hints. They must never include private target identity. | `python3 scripts/field_reports.py --self-test`; `python3 scripts/field_reports_quality_oracle.py --self-test`; `python3 scripts/field_reports_github_oracle.py --self-test`. |
| SPEC-012 Correlation And Release Identity | `package.json`, version constants, docs indexes, public bundle surfaces, release docs when authorized | Delivered behavior changes receive a patch-version/bundle decision before closure. If version bump is deferred by explicit maintainer decision, closeout must say the behavior is not sealed by version identity. | `python3 scripts/validate_tds.py`; `python3 scripts/validate_doc_size.py`; `python3 scripts/validate_reference_graph.py`; `npm run commit:check`. |

## P0 Cut: Minimum Convergent Repair

The first implementation wave should be small enough to land without absorbing the entire backlog:

1. Add a neutral ignored-lockfile regression fixture.
2. Share lockfile constants/predicate between generator and oracle.
3. Make `caution_zones` satisfy `expected_caution_terms` for root lockfiles.
4. Align `weak_anchor_triage` with the same lockfile set.
5. Propagate context-oracle failure details into postinstall run records if the implementation touches recovery code.
6. Run focused gates and record release identity impact.

P0 is complete only when a repeated first-session/recovery run no longer rewrites itself into the same `NEEDS_REVIEW` state for the neutral fixture.

## P1 Cut: Installed Surface Repairability

After P0:

1. Ensure first-session materialization and installed certification agree on Mantra Gate routing.
2. Ensure command trigger parity is generated in installed Codex, Claude, and Cursor surfaces during the relevant write path.
3. Add or update legacy-path retirement for generated target docs.
4. Make `/tes-doctor` route each drift class to source-aware repair guidance.

P1 is complete only when installed certification components either pass or report exact repair routes without hiding under a broader `INSTALLED` status.

## P2 Cut: Operational Noise And Retention

After P0/P1:

1. Bound or index postinstall `runs[]`.
2. Granularize dirty-worktree reporting.
3. Improve Field Reports summaries for multi-surface drains.
4. Add evidence reports for the repaired failure family.

P2 is complete only when noisy but non-blocking runtime state remains observable without becoming a false blocker.

## Required Negative Checks

- No private project names, private filesystem paths, private stack names, internal service names, branch names, remotes, commits, product vocabulary, or raw target docs in TES tracked content.
- No target-only installed mirror patch as the final repair.
- No duplicated lockfile tuple drift between generator and validator.
- No `PASS` when generator output is immediately rejected by the paired oracle.
- No `PASS` when installed certification components are degraded.
- No stale retired skill path in generated quality gates.
- No `.DS_Store`, `Thumbs.db`, `__MACOSX`, or AppleDouble residue in public bundle or adapter materialization.
- No `host_connected` or runtime availability claim inferred from config file presence alone.
- No remote release/ref claim without explicit release identity authorization.

## Required Oracles Before Implementation Closeout

Run focused gates during each unit. Before claiming convergence of this Super SPEC, run:

```bash
python3 scripts/tes_init.py --self-test
python3 scripts/project_context_oracle.py --self-test
python3 scripts/tes_install.py --self-test
python3 scripts/installed_certification_oracle.py --self-test
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/mantra_gate_adoption_oracle.py --self-test
python3 scripts/tes_update.py --self-test
python3 scripts/tes_legacy_retirement.py --self-test
python3 scripts/tes_bundle.py --self-test
python3 scripts/public_bundle_oracle.py
python3 scripts/field_reports.py --self-test
python3 scripts/field_reports_quality_oracle.py --self-test
python3 scripts/field_reports_github_oracle.py --self-test
python3 scripts/private_vocabulary_oracle.py
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
git diff --check
npm run commit:check
```

If a unit intentionally lands before the full wave, closeout must name the narrower oracle that passed and the remaining units that are still open.

## Evidence And Canary Requirements

The final implementation must include:

- neutral fixture evidence for the ignored-lockfile contract-symmetry failure;
- before/after proof that the paired generator and oracle agree;
- a package-source evidence report under `docs/evidence/reports/**`;
- one replay on the original private canary project with the source-of-record kept outside TES tracked content;
- two additional private real-project canary replays before any commercial-use or broad readiness claim;
- `git status --short --branch --untracked-files=all`;
- release identity decision for any delivered behavior change.
