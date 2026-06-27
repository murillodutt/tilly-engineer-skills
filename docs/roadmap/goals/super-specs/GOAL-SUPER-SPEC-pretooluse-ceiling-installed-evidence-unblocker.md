---
tds_id: roadmap.goal_super_spec_pretooluse_ceiling_installed_evidence_unblocker
tds_class: roadmap
status: active
consumer: maintainers, hook authors, installer authors, oracle authors, release reviewers, execution agents, and hook-audit operators
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Super SPEC: PreToolUse Ceiling Installed Evidence Unblocker

## Purpose

Turn the `0.3.220` PreToolUse ceiling substrate into an installed-target
`PASS_CEILING` claim without weakening the floor, deleting historical evidence,
or treating a noisy aggregate ledger as a runtime failure.

This Super SPEC is a follow-on execution router, not a replacement for ADR 0009
or its linear slice plan. ADR 0009 remains the canonical architecture; this
document targets the four senior recommendations from the first installed
ceiling audit after `0.3.220`, anchored below by tracked evidence and by the
owner-provided review that authorized this repair.

Central rule:

```text
Current v2 evidence decides ceiling readiness; historical rows explain history.
```

## Anchor Artifacts

```text
hash_algorithm=sha256
architecture_anchor=docs/adr/0009-pretooluse-ceiling-contract-and-hook-topology.md
contract_anchor=docs/architecture/PRETOOLUSE-CONTRACT.md
contract_hash=5218b57ba81fee0614eff3308d78c6d14a0377d0f8783132f77fd38b682c2a71
execution_plan_anchor=docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-adr-0009-pretooluse-ceiling-linear-slices.md
execution_plan_hash=53d10883f0054c11e76c3c3b2ccec7cccefca8fdc5e5bc063e13cf64bd9ca780
closure_report_anchor=docs/evidence/reports/2026/06/27/hooks/pretooluse-ceiling-closure-audit/REPORT.md
closure_report_hash=214b39a3931eefb3c7ce53416f12078b8c06782d91c030b1c11b859707f732d7
installed_evidence_anchor=docs/evidence/reports/2026/06/27/hooks/pretooluse-ceiling-installed-evidence/REPORT.md
installed_evidence_hash=7e6314c35ad286ddcdb5368c789bf1f587fb03dd7686770f6fb65f171e4715ae
owner_review_source=owner-provided installed audit review, untracked by design
```

If any anchor changes before execution, the executor must re-read the changed
surface and state whether this Super SPEC still applies.

## Protected Baseline

The protected baseline is TES `0.3.220` local source substrate:

- `pretooluse_decision@2` rows exist and carry reason codes, classifier trace,
  renderer trace, ledger trace, payload source, command category, and redaction;
- discoverability is implemented for unknown mutating-looking governed tools;
- helper parity and source matrix oracles are green;
- installed closure remains `NEEDS_EVIDENCE`, not `PASS_CEILING`, because
  installed native aggregate evidence is not yet cleanly scoped.

Do not regress `PASS_BASIC`. Do not turn historical pre-v2 rows into runtime
failures. Do not claim `PASS_CEILING` without current installed native evidence.

## Senior Recommendations Covered

1. Scope or migrate `pretooluse_ceiling_gaps()` so legacy pre-v2 rows cannot
   permanently reclassify current ceiling-ready behavior as missing evidence.
2. Expose `helper_contract_status` and `discoverability_status` directly in
   installed `hook-health`, not only in source matrix summaries.
3. Make the canonical PreToolUse contract discoverable from installed targets by
   shipping an installed contract copy and recording a versioned lock reference.
4. Treat duplicate historical rows and smoke residue as low-severity historical
   noise unless they contradict current v2 semantics.

## Execution Boundary

No remote, push, publish, tag, marketplace action, destructive target cleanup,
or private target evidence is authorized by this Super SPEC. Installed-target
tests may be run only on an authorized target or canary. Any delivered package
behavior change requires an explicit release identity decision before closure.

## Unit Commit Contract

`SPEC-000` may close as preflight with no commit. Each material unit from
`SPEC-001` through `SPEC-006` must close with one local commit for that unit, or
with a named no-op/blocked state explaining why no commit exists. Do not batch
multiple material units into one commit unless the owner explicitly authorizes
the batch and the closeout maps the combined commit back to each unit.

## Non-Objectives

- Do not rewrite the PreToolUse kernel unless a fixture proves current v2
  decisions are wrong.
- Do not delete installed hook ledgers to manufacture a clean ceiling result.
- Do not backfill legacy rows with guessed v2 fields.
- Do not flatten Claude Code, Codex, and Cursor renderer contracts.
- Do not ship private target paths, project names, raw command text, or raw
  native audit transcripts in tracked evidence.
- Do not spend implementation scope on duplicate warnings or smoke residue
  unless they block current v2 evidence.

## Required Semantics

### Ceiling Evidence Scope

`hook-health` must report which rows were considered for ceiling evaluation:

```text
ceiling_evidence_scope:
  schema_version: pretooluse_decision@2
  claim_scope: current_host | all_configured_hosts
  aggregation_policy: per_host_no_cross_fill
  current_host: <host or null>
  required_hosts: [claude, codex, cursor] | [<current-host>]
  per_host:
    <host>:
      agent: <agent>
      native_evidence: observed | not_available | contract_simulated_only
      considered_records: <count>
      ignored_legacy_records: <count>
      oldest_considered_ts: <timestamp or null>
      newest_considered_ts: <timestamp or null>
      status: PASS_CEILING | PASS_BASIC_WITH_CEILING_GAPS | NEEDS_EVIDENCE
  legacy_policy: historical_context_only
```

Legacy rows may produce informational migration context, but they must not
produce current `missing_reason_codes`, `missing_classifier_trace`,
`missing_renderer_trace`, `missing_command_category`, `missing_payload_source`,
`missing_decision_projection`, `raw_command_not_redacted`, or
`missing_pretooluse_decision_v2_schema` gaps inside a host scope when enough v2
evidence exists for that same host.

`PASS_CEILING` must never be derived by pooling fields across hosts. Each host
must independently satisfy the full v2 evidence checklist for its declared
scope. A current-host audit may claim only the current-host scope. A package or
all-host claim requires each configured host to have its own complete scoped
evidence, or it must close as `NEEDS_EVIDENCE` for the missing host.

### Installed Health Fields

Installed `hook-health --json-only` must expose:

```text
helper_contract_status
discoverability_status
floor_status
ceiling_status
ceiling_gaps[]
dedupe_contract
ceiling_evidence_scope
```

The source matrix may still compute these fields for source-side checks, but
installed audit should not depend on source-only summaries to answer installed
readiness.

Installed `hook-health` owns these installed field sources:

- `helper_contract_status`: computed from the installed `.tes/bin`
  `pretooluse_kernel.py` and `pretooluse_session.py` imports plus their expected
  schema/contract constants or lock-recorded fingerprints. Source-only imports
  cannot fill this field for an installed target.
- `discoverability_status`: computed from installed evidence only. Acceptable
  sources are scoped v2 ledger rows with `outcome=needs_discoverability`,
  `risk=needs-discoverability`, the
  `needs_discoverability_unknown_mutation` reason code, and renderer trace, or a
  hook-health-owned installed fixture/probe that uses the installed helpers. The
  source matrix may verify this field, but must not synthesize it after reading
  `hook-health`.

### Installed Contract Reference

An installed target must be able to answer "where is the PreToolUse contract?"
without access to the source repository. The minimum acceptable result is:

```text
.tes/tes-install-lock.json:
  pretooluse_contract:
    package_path: docs/architecture/PRETOOLUSE-CONTRACT.md
    installed_path: .tes/docs/architecture/PRETOOLUSE-CONTRACT.md
    sha256: <contract hash>
    version: <package version>
```

The installed contract copy may be under `.tes/docs/**`; it is reference
material, not a new source of behavior. The lock reference is authoritative for
version and hash.

### Historical Noise Policy

Duplicate records, stable replay rows, Cursor batched invocations, and smoke
artifacts are not ceiling blockers unless a current v2 row contradicts the
expected decision, risk, renderer trace, redaction, or marker state. They may be
reported as `info` or `warning` with dedupe guidance.

## Linear Units

### SPEC-000 Preflight And Evidence Baseline

Goal: confirm the current state before implementation.

Required proof:

- `git status --short --branch`;
- `python3 scripts/host_runtime_matrix_oracle.py --self-test`;
- `python3 scripts/pretooluse_evidence_oracle.py --packet <installed-evidence-packet>`;
- inspect the latest closure summary and confirm final status is
  `NEEDS_EVIDENCE`, not `PASS_CEILING`.

Stop if the worktree contains unrelated changes or if the latest closure report
already proves installed `PASS_CEILING`.

### SPEC-001 Version-Scoped Ceiling Gap Evaluation

Goal: repair `pretooluse_ceiling_gaps()` so current v2 records decide ceiling
gaps while legacy rows remain historical context.

Territory:

- `scripts/tes_install.py`;
- existing hook-health fixtures/self-tests;
- `scripts/host_runtime_matrix_oracle.py` only if source matrix assertions need
  the new scope fields.

Required behavior:

- mixed ledgers with complete v2 rows and older pre-v2 rows do not produce v2
  missing-field gaps from the legacy rows inside the same host scope;
- mixed ledgers still report ignored legacy counts and preserve duplicate
  warnings when exact duplicates are real;
- v2 rows that actually miss required fields still fail ceiling evidence;
- a ledger where Claude supplies `reason_codes`, Codex supplies
  `renderer_trace`, and Cursor supplies redaction must still fail all-host
  `PASS_CEILING`; no host can borrow fields from another host.

Required oracle:

- a red-capable fixture that fails before the scoped evaluation and passes
  after repair;
- a red-capable fixture proving cross-host field pooling cannot pass;
- `python3 scripts/tes_install.py --self-test`;
- `python3 scripts/host_runtime_matrix_oracle.py --self-test`;
- `git diff --check`.

### SPEC-002 Installed Health Status Surfacing

Goal: expose `helper_contract_status` and `discoverability_status` directly in
installed `hook-health` output.

Territory:

- `scripts/tes_install.py`;
- `scripts/host_runtime_matrix_oracle.py`;
- `docs/install/HOOK-AUDIT-PROMPT.md`;
- `scripts/hook_audit_prompt_oracle.py`.

Required behavior:

- installed `hook-health --json-only` contains `helper_contract_status`;
- installed `hook-health --json-only` contains `discoverability_status`;
- both fields are computed by installed `hook-health` from installed helpers,
  scoped ledger rows, or installed fixture/probe evidence, not injected by
  `host_runtime_matrix_oracle.py`;
- absent helper/discoverability evidence returns explicit `NEEDS_EVIDENCE` or
  `MISSING`, not silent omission;
- audit prompt requires these fields before `PASS_CEILING`.

Required oracle:

- `python3 scripts/tes_install.py --self-test`;
- `python3 scripts/host_runtime_matrix_oracle.py --self-test`;
- `python3 scripts/hook_audit_prompt_oracle.py --self-test`.

### SPEC-003 Installed Contract Reference

Goal: make the canonical PreToolUse contract discoverable from an installed
target.

Territory:

- installer/bundle helper allowlist paths;
- `.tes/tes-install-lock.json` generation in `scripts/tes_install.py`;
- reference package and install fixtures;
- `docs/architecture/PRETOOLUSE-CONTRACT.md` as the canonical source.

Required behavior:

- installed targets receive `.tes/docs/architecture/PRETOOLUSE-CONTRACT.md`;
- lock JSON records `pretooluse_contract` with package path, installed path,
  sha256, and package version;
- installed certification can verify the contract reference without reading the
  source repository;
- stale or mismatched contract hash is reported as certification evidence, not
  silently ignored.

Required oracle:

- `python3 scripts/tes_install.py --self-test`;
- `python3 scripts/installed_certification_oracle.py --self-test` if available
  or an equivalent installed fixture;
- `python3 scripts/validate_reference_package.py`;
- `python3 scripts/hook_audit_prompt_oracle.py --self-test`.

### SPEC-004 Historical Noise And Dedupe Policy

Goal: ensure duplicate warnings and smoke residue stay low-severity unless they
contradict current v2 semantics.

Territory:

- hook-health duplicate findings;
- dedupe contract documentation in `docs/install/HOOK-AUDIT-PROMPT.md`;
- existing self-test fixtures.

Required behavior:

- duplicate historical rows remain `warning` or `info`;
- Cursor batched rows differing by tool, risk, path, command category, marker,
  session, or mode are not exact duplicate executions;
- smoke artifacts under runtime-excluded paths are reported only as cleanup
  hygiene unless they alter current v2 evidence.

Required oracle:

- existing duplicate/replay hook-health fixtures;
- `python3 scripts/tes_install.py --self-test`;
- `python3 scripts/hook_audit_prompt_oracle.py --self-test`.

### SPEC-005 Installed Native Evidence Replay

Goal: rerun the installed target audit after SPEC-001 through SPEC-004 and decide
whether `PASS_CEILING` is now claimable.

Territory:

- authorized installed target or canary only;
- `docs/install/HOOK-AUDIT-PROMPT.md`;
- `scripts/pretooluse_evidence_oracle.py`;
- sanitized evidence packet under `docs/evidence/reports/hooks/**` or dated
  equivalent.

Required behavior:

- current-host native smoke produces v2 rows with reason codes, classifier
  trace, renderer trace, ledger trace, command redaction, and discoverability;
- `hook-health` reports `floor_status=PASS_BASIC`;
- `hook-health` reports `ceiling_status=PASS_CEILING` only if v2 current-host
  evidence is complete and no ceiling gaps remain;
- if native evidence is unavailable, close as `NEEDS_EVIDENCE`;
- `pretooluse_evidence_oracle.py` supports the existing needs-evidence packet
  contract and a ceiling-validation mode for sanitized `PASS_CEILING` packets;
- the ceiling-validation mode fails simulated-only packets, packets missing
  host attribution, packets without scoped native evidence for the claimed host,
  and packets where `ceiling_status` is cross-filled across hosts.

Required oracle:

- installed `HOOK-AUDIT-PROMPT.md` report;
- `python3 scripts/pretooluse_evidence_oracle.py --packet <packet> --expect needs-evidence`;
- `python3 scripts/pretooluse_evidence_oracle.py --packet <packet> --expect pass-ceiling`;
- `python3 scripts/private_vocabulary_oracle.py --paths <packet-files>`.

### SPEC-006 Release Identity And Closure

Goal: decide whether the delivered installer/runtime changes require a package
version and bundle update.

Required behavior:

- if SPEC-001 through SPEC-004 changed delivered behavior, bump patch version
  and regenerate correlated public bundle surfaces unless the owner explicitly
  keeps the current version unsealed;
- no push, tag, publish, or release check without explicit separate
  authorization;
- final report distinguishes source green, installed floor, installed ceiling,
  and release identity.

Required oracle:

- `python3 scripts/validate_reference_package.py`;
- `python3 scripts/validate_tds.py`;
- `python3 scripts/validate_doc_size.py`;
- `npm run commit:check`;
- public bundle oracle only if a bundle is regenerated.

## Stop States

Use only these final states:

- `PASS_CEILING`: current installed native evidence satisfies the full ceiling
  checklist after scoped v2 evaluation.
- `PASS_BASIC_WITH_CEILING_GAPS`: floor is operational but at least one ceiling
  field remains missing.
- `NEEDS_EVIDENCE`: native installed evidence is unavailable or unauthorized.
- `NEEDS_DISCOVERABILITY`: a host tool or payload remains unclassified by
  evidence.
- `NEEDS_RELEASE_IDENTITY`: runtime/source changes are green but package identity
  has not been updated or explicitly waived.
- `BLOCKED`: safety, privacy, or authority prevents continuation.

## Final Delivery Contract

Closeout must report:

- current package version and whether package identity changed;
- `floor_status`, `ceiling_status`, `helper_contract_status`, and
  `discoverability_status`;
- `ceiling_evidence_scope` counts;
- whether the installed contract reference is present and hash-matched;
- duplicate/noise status and whether it affected ceiling;
- installed native evidence packet path or `NEEDS_EVIDENCE`;
- commit hash for each material unit, mapped to `SPEC-001` through `SPEC-006`;
- sync status.

## Prompt Status

```text
PROMPT_STATUS=SUPER_SPEC_MATERIALIZED
REPAIR_STATUS=OBJECTIONS_REPAIRED_FOR_EXECUTION
NEXT_ALLOWED_ACTION=execute SPEC-000 preflight before runtime edits
```
