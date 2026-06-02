---
tds_id: roadmap.goal_super_spec_tes_anti_contamination_hardening
tds_class: roadmap
status: active
consumer: maintainers, Cortex maintainers, oracle authors, adapter maintainers, release reviewers, and execution agents
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# GOAL Super SPEC: TES Anti-Contamination Hardening

Status: active planning artifact; no delivered behavior yet.

Capability: harden TES against private-context contamination, noisy target
canary feedback, and language-sensitive false positives discovered after a
private target canary absorbed TES `0.3.135`.

## Canonical Artifact

Canonical Super SPEC:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-anti-contamination-hardening.md`

Primary decision source:
`docs/adr/0001-tes-memory-lifecycle.md`

Related implementation surfaces:

- `scripts/cortex.py`
- `scripts/project_alignment_oracle.py`
- `scripts/private_vocabulary_oracle.py`
- `scripts/validate_reference_package.py`
- `docs/evals/CORTEX-MEMORY-BENCHMARKS.md`
- `docs/install/AGENT-ORACLE-INVENTORY.md`
- `docs/mesh/CORTEX.md`
- `docs/mesh/CORTEX-MCP.md`
- `docs/mesh/SCOPE-CONTRACT.md`
- `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md`
- `docs/governance/MAINTAINER-CORRELATION-RULE.md`

## Governing Matrix

| Layer | Meaning |
|-------|---------|
| ADR 0001 | Markdown remains durable Cortex memory truth; derived indexes, checkpoints, scores, and reports are evidence only. |
| Anti-contamination hardening | Prevent private target paths, project identifiers, runtime churn, and scanner-shaped fixture residue from becoming package behavior or public evidence. |
| Oracles | Detect absolute path leakage, language false positives, stale semantic residue, private vocabulary, and noisy installed-runtime changes. |
| Evidence | Use generic retained reports and self-tests; never copy private target names, paths, commits, remotes, product vocabulary, or domain decisions. |
| Non-Change | Does not add write-capable MCP, automatic Cortex writes, external memory backend, external datasets, UI, or release publishing. |

## Current Meaning

The `0.3.135` package-source implementation passed local closure, but a
private target canary dossier exposed hardening opportunities that are
portable to TES. The dossier itself is private project evidence and must not be
promoted into TES source. The portable learning is limited to generic failure
modes:

- Cortex evidence blocks can hide an absolute path beside a valid relative
  evidence ref.
- The alignment oracle can treat normal Portuguese prose as placeholder
  language.
- Cortex reflect can treat installed TES helper churn as durable project
  memory pressure.
- Semantic Residue authoring can overmatch live vocabulary or historiography
  when entries are too broad.
- Public bundles may include synthetic sanitizer fixtures that look like real
  secrets to generic scanners.

## Creation Gate Record

| Field | Record |
|-------|--------|
| `VERIFY` | ADR 0001, the `0.3.135` harness closure, the private target canary dossier, Cortex audit behavior, alignment oracle patterns, roadmap precedents, and TDS index shape were inspected before writing. |
| `SCOPE` | Add this Super SPEC and correlated documentation indexes only. No runtime, package version, adapter, MCP, installer, bundle, commit, tag, push, or publish changes. |
| `BEST_PATH` | Create one governed anti-contamination Super SPEC instead of copying private canary details into TES or opening separate ADRs for local hardening bugs. |
| `DOCUMENT` | This Super SPEC plus `docs/roadmap/README.md`, `docs/INDEX.md`, and `docs/tds/DOCS-INDEX.yml`. |
| `ORACLE` | `python3 scripts/validate_tds.py`, `python3 scripts/validate_doc_size.py`, `python3 scripts/validate_reference_graph.py`, `python3 scripts/private_vocabulary_oracle.py`, and `git diff --check`. |
| `RESOLVE` | Private evidence remains outside TES; portable fixes are specified as deterministic units. |
| `STATUS` | `PROCEED` |

## Assumptions

- The private target canary is evidence of TES behavior, not TES source
  material.
- Project-specific vocabulary, commit SHAs, remote names, paths, and domain
  decisions stay out of TES tracked content.
- The next implementation should be a small patch release if runtime or
  adopter-visible behavior changes.
- Deterministic fixtures are preferred over broad prose rules.
- Documentation must teach the boundary only where it reduces repeated failure.

## Non-Objectives

- Port private project terms, paths, commits, remotes, product names, domain
  architecture, or owner decisions into TES.
- Treat private canary evidence as a public benchmark dataset.
- Add a new memory backend or write-capable MCP.
- Add automatic Cortex writes.
- Add external datasets, external services, paid/API judging, UI, or cloud
  behavior.
- Claim commercial readiness, remote release readiness, or published fixed-ref
  certification.

## Required Fix Matrix

| Fix | Owned Surface | Failure Mode | Required Correction | Focused Oracle |
|-----|---------------|--------------|---------------------|----------------|
| Cortex absolute evidence guard | `scripts/cortex.py` | A Cortex cell can include an absolute local path in `## Evidence` while passing because a valid relative ref also exists. | Fail audit/apply when any absolute path-like token appears in the evidence section, even when valid refs are present. Preserve allowed relative refs and `Assumption:` handling. | `python3 scripts/cortex.py --self-test` plus a new regression fixture. |
| PT-BR placeholder false positive | `scripts/project_alignment_oracle.py` | The Portuguese word `todo` can be classified as English placeholder `TODO`. | Narrow placeholder detection to marker forms such as `TODO:`, standalone uppercase TODO markers, task-list placeholders, or explicit placeholder prose. Add a positive placeholder case and a Portuguese prose negative case. | `python3 scripts/project_alignment_oracle.py --self-test`. |
| Installed runtime churn noise | `scripts/cortex.py` and related docs if needed | `reflect` can treat `.tes/bin/**` helper churn from a TES update as project-memory pressure. | Classify installed runtime helper churn as derived/update noise unless paired with project durable docs, source evidence, or explicit closure note. Keep manual durable target edits visible. | `python3 scripts/cortex.py --self-test` with fixture for helper-only churn and fixture for durable docs churn. |
| Semantic Residue authoring guidance | `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` and oracle docs | Broad residue entries can overmatch live vocabulary or historical descriptions. | Clarify `term` vs `pattern`, `allowed_paths`, `exclude`, severity, expiration, and context inspection before remediation. Add examples using neutral placeholder terms only. | `python3 scripts/validate_tds.py`, `python3 scripts/private_vocabulary_oracle.py`. |
| Cortex evidence authoring guidance | `docs/mesh/CORTEX.md`, `docs/mesh/CORTEX-MCP.md`, or focused eval docs | Operators may try to include absolute paths beside relative refs to satisfy audit. | State allowed evidence forms explicitly: `sources/**`, `docs/agents/evidence/**`, or `Assumption:`. State that absolute paths fail even when paired with valid refs. | `python3 scripts/validate_reference_graph.py` and Cortex self-test. |
| Scanner-shaped synthetic fixture cleanup | sanitizer self-tests and docs | Public bundle can contain synthetic strings that resemble secrets or private paths, creating scanner noise. | Replace example secrets and paths with neutral placeholders that still exercise sanitizer behavior, or document them as synthetic fixtures only if replacement would weaken coverage. | Relevant self-tests plus `python3 scripts/private_vocabulary_oracle.py`; optional bundle scan before release claim. |
| Private canary evidence handling | evidence docs and release closeout language | Agents may cite private target details as public TES evidence. | Use only generic phrasing: `private target canary`, `target project`, `source-of-record kept outside TES`. Never include private identifiers in TES source, docs, commits, or release notes. | `python3 scripts/private_vocabulary_oracle.py` plus manual staged diff scan. |

## Execution Discipline

Run units sequentially. Do not bulk-implement later units before the current
unit has focused oracle, release identity classification, and closure note.

Before each unit, state:

- owned files;
- no-touch files;
- release identity impact;
- focused oracle;
- stop condition.

After each unit:

- run the focused oracle;
- fix and rerun on failure;
- update only correlated docs or indexes;
- run the private vocabulary oracle when fixtures, docs, reports, or public
  surfaces are touched.

## SPEC-000: Reentry And Contamination Boundary

Owned files:

- this Super SPEC;
- no runtime files.

Tasks:

1. Run `git status --short --branch --untracked-files=all`.
2. Run `git log -8 --oneline`.
3. Classify dirty changes as inherited, current-task delta, or unrelated.
4. Confirm no private target evidence will be copied into TES.
5. Confirm whether this planning-only work is still doc-only and version-neutral.

Focused oracle:

```bash
python3 scripts/private_vocabulary_oracle.py
git diff --check
```

Closure note:

```text
SPEC-000 PASS means the execution starts from a clean boundary and all private
target references are treated as off-repo source-of-record material.
```

## SPEC-001: Cortex Absolute Evidence Guard

Owned files:

- `scripts/cortex.py`
- docs only if the behavior contract must be visible to operators.

Implementation:

1. Add a scanner for absolute path-like evidence lines inside `## Evidence`.
2. Fail audit when the evidence section includes any absolute local path,
   including POSIX, macOS, Windows, temp, home, or repository-root-like paths.
3. Ensure valid relative evidence still passes:
   - `sources/<file>`;
   - `docs/agents/cortex/sources/<file>`;
   - `docs/agents/evidence/<file>`;
   - `Assumption:`.
4. Ensure invalid absolute refs fail even when a valid relative ref is also
   present.
5. Ensure `apply` remains fail-closed before writing.

Regression fixtures:

- passing cell with only relative evidence;
- failing cell with only absolute evidence;
- failing cell with both relative and absolute evidence;
- passing cell with `Assumption:` when explicitly allowed.

Focused oracle:

```bash
python3 scripts/cortex.py --self-test
```

Stop condition:

- If existing Cortex semantics intentionally allow absolute refs, stop with
  `NEEDS_REVIEW`; otherwise this is a safety bug.

## SPEC-002: PT-BR Placeholder False Positive

Owned files:

- `scripts/project_alignment_oracle.py`
- docs only if command behavior needs user-visible clarification.

Implementation:

1. Replace the broad lowercase `todo` detector with marker-sensitive detection.
2. Keep these as failures:
   - `TODO:`;
   - `TODO -`;
   - `- TODO`;
   - `TODO` as a standalone placeholder line;
   - prose such as `TODO fill this in` when clearly placeholder-shaped.
3. Allow normal Portuguese prose such as `cada`, and allow lowercase `todo`
   when embedded in grammatical prose without placeholder markers.
4. Preserve existing literal-path exceptions such as filenames containing
   `TODO`.

Regression fixtures:

- Portuguese sentence containing lowercase `todo` in prose must pass.
- `TODO: fill this in` must fail.
- `docs-archive/MCP-TESTS-TODO.md` must pass as a literal path.
- `generic project run tests` must still fail.

Focused oracle:

```bash
python3 scripts/project_alignment_oracle.py --self-test
```

Stop condition:

- If narrowing the detector permits obvious placeholder drift, stop with
  `NEEDS_REVIEW` and add a stricter marker grammar.

## SPEC-003: Installed Runtime Churn Noise

Owned files:

- `scripts/cortex.py`
- possibly `docs/mesh/CORTEX.md`.

Implementation:

1. Review `reflect` changed-file selection.
2. Classify installed TES runtime helper churn under `.tes/bin/**` as update
   noise when it is the only durable-looking change.
3. Preserve capture when:
   - a closure note is supplied;
   - docs under `docs/**` changed materially;
   - Cortex sources or cells changed;
   - project source changed outside installed TES runtime cache;
   - the line budget or curation threshold is exceeded by real project files.
4. Report a clear `no_capture_reason` for helper-only churn.

Regression fixtures:

- helper-only `.tes/bin/**` update does not require Cortex capture;
- helper plus project doc update still requires capture;
- changed Cortex cell still requires audit/curation;
- closure note still proposes a capture.

Focused oracle:

```bash
python3 scripts/cortex.py --self-test
```

Stop condition:

- If installed runtime helper churn is needed as durable memory evidence for
  another TES contract, stop and split the behavior into a separate ADR or
  explicit lifecycle decision.

## SPEC-004: Semantic Residue Authoring Guardrails

Owned files:

- `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md`
- `docs/install/AGENT-ORACLE-INVENTORY.md` if command guidance changes.

Implementation:

1. Add a concise authoring section:
   - use `term` only for exact retired vocabulary;
   - use `pattern` for variant-specific residue;
   - use `allowed_paths` only for known live or historical contexts;
   - inspect matched context before editing;
   - never use the contract to silence generic placeholders;
   - record rejected candidates when mis-scoped.
2. Add neutral examples:
   - retired term with successor;
   - pattern scoped to a variant prefix;
   - historiography allowed path;
   - `needs_review` for ambiguous residue.
3. Keep examples generic and reversible.

Focused oracle:

```bash
python3 scripts/validate_tds.py
python3 scripts/validate_reference_graph.py
python3 scripts/private_vocabulary_oracle.py
```

Stop condition:

- If the doc would duplicate an existing source of truth, update that source
  instead of creating parallel guidance.

## SPEC-005: Cortex Evidence Guidance

Owned files:

- `docs/mesh/CORTEX.md`
- `docs/mesh/CORTEX-MCP.md`
- `docs/evals/CORTEX-MEMORY-BENCHMARKS.md` if benchmark docs mention evidence.

Implementation:

1. Add a short evidence boundary:
   - allowed refs: `sources/**`, `docs/agents/cortex/sources/**`,
     `docs/agents/evidence/**`, or `Assumption:`;
   - absolute paths fail;
   - derived caches are not durable evidence;
   - benchmark artifacts do not write Cortex memory.
2. Ensure docs do not imply that absolute local paths can satisfy audit.
3. Keep MCP language read-only unless an existing authorized write command is
   already documented elsewhere.

Focused oracle:

```bash
python3 scripts/validate_tds.py
python3 scripts/validate_reference_graph.py
python3 scripts/private_vocabulary_oracle.py
```

Stop condition:

- If a doc currently declares absolute evidence as valid, stop for ADR review.

## SPEC-006: Synthetic Fixture Cleanup

Owned files:

- sanitizer self-test scripts only when scanner-shaped examples can be replaced
  without reducing coverage;
- docs only if retained explanation is needed.

Implementation:

1. Inventory synthetic path, email, token, and secret fixtures shipped in the
   public bundle.
2. Replace scanner-shaped examples with neutral placeholders where possible:
   - `<absolute-path>`;
   - `<email-address>`;
   - `<redacted-token>`;
   - `<private-url>`;
   - `<stack-trace>`.
3. Preserve sanitizer coverage by asserting placeholders are sanitized or by
   using generated strings assembled at runtime in tests when static scanning
   would be noisy.
4. If a literal fixture must remain, document why in the script comment and
   ensure no real-looking project name appears.

Focused oracle:

```bash
python3 scripts/field_reports.py --self-test
python3 scripts/mantra_gate.py --self-test
python3 scripts/mantra_gate_adoption_oracle.py --self-test
python3 scripts/checkpoint.py --self-test
python3 scripts/event_ledger.py --self-test
python3 scripts/private_vocabulary_oracle.py
```

Stop condition:

- If replacement weakens sanitizer proof, defer cleanup and keep the fixture
  with explicit synthetic labeling.

## SPEC-007: Release Identity And Package Closure

Owned files:

- `package.json` and release surfaces only if delivered behavior changes;
- docs/evidence only if retained proof is created.

Tasks:

1. Classify release identity after runtime changes:
   - planning-only docs: no bump;
   - script/oracle/command/adopter-visible docs: patch bump required by the
     maintainer release identity rule unless explicitly deferred by owner.
2. Run focused oracles from each implemented unit.
3. Run baseline gates:

```bash
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
python3 scripts/private_vocabulary_oracle.py
git diff --check
```

4. Before any sealed package claim, run:

```bash
npm run commit:check
```

5. If a version bump is performed, also run:

```bash
python3 scripts/tes_bump.py --governance-check --json
python3 scripts/build_public_docs.py --check
python3 scripts/public_bundle_oracle.py
```

Stop condition:

- If release identity requires a bump and owner authorization is unclear, stop
  with `NEEDS_REVIEW`.

## Private Vocabulary Guard

The implementation must not add private project names, repository paths,
remotes, commit narratives, target product vocabulary, target domain decisions,
canary identifiers, or target-specific storage/archive names. Use generic forms
only: `private target canary`, `target project`, `private source-of-record kept
outside TES`, `<project-A>`, `<retired-term>`, `<successor-term>`,
`<absolute-path>`, and `<redacted-token>`.

## Evidence Plan

Retained evidence for the implementation should be generic:

| Evidence | Location | Requirement |
|----------|----------|-------------|
| Unit self-test output | closeout summary or retained report | Include commands and PASS/FAIL only. |
| Private target canary replay | private target source-of-record, not TES | Mention only that a private canary replay was used. |
| TES package evidence | `docs/evidence/**` only if retained | Must omit private names, paths, commits, remotes, and domain vocabulary. |
| Bundle scan | closeout summary or retained report | Report synthetic fixture findings as generic scanner noise. |

## Final Closure Report Requirements

The executor must report:

- implemented SPEC units;
- files changed;
- release identity decision;
- focused oracle results;
- baseline gate results;
- whether `npm run commit:check` passed;
- residual risks;
- deferred work;
- confirmation that no private target identifiers were added.
