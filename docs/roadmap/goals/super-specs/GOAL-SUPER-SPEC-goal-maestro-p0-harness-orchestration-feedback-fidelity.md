---
tds_id: roadmap.goal_super_spec.goal_maestro_p0_harness_orchestration_feedback_fidelity
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, adapter authors, oracle authors, installed-canary operators, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# GOAL-SUPER-SPEC: Goal Maestro P0 Harness Orchestration And Feedback Fidelity

Status: active corrective Super SPEC.

Purpose: repair `tes-goal-maestro --execute-loop` based on real cross-host
canary evidence where the delivered product could look good while the harness
failed to prove linear execution, enrichment, visual evidence, thermometer
fidelity, install chronology, Flash-Fry status, and closeout consistency.

This is the first of three linked corrective Super SPECs:

- P0: 24 blocking slices that must converge before the same validation prompt is
  repeated.
- P1: 6 parity and report-experience slices.
- P2: 4 schema, fixture, stop-state, and anti-contamination slices.

The partition count is exact. This document carries SPEC-001 through SPEC-024.
There is no extra SPEC-000 slice in this Super SPEC.

## Evidence Base

The corrective work is anchored in installed canary evidence from three target
hosts. The canary proved that a strong final product does not prove that Goal
Maestro executed as an auditable production line.

Observed failure classes:

- SPEC execution was not consistently linear.
- Prompt enrichment was described but not persisted as a required artifact.
- Visual evidence gates accepted weak or incomplete scene coverage.
- Thermometer extraction accepted `SPEC-UNKNOWN`, missing material SPECs, and
  audit rows counted as material SPECs.
- Flash-Fry had no operational stamp in any observed host.
- Document analysis and cloud-search classification were not uniformly
  represented.
- Commit enforcement was manual while the reports did not clearly separate
  manual commit evidence from hook enforcement.
- Install chronology was weak in hosts where TES installation appeared after
  material commits.

## Central Rule

```text
Goal Maestro may not close a loop as complete unless the execution line,
evidence line, thermometer line, and chat closeout all prove the same ordered
SPEC execution from the same installed harness state.
```

## Platform Classification

This work is `Platform` from the first line. It touches delivered Goal Maestro
behavior, adapter materialization, installed target evidence, execution reports,
oracles, prompt sidecars, and canary interpretation.

## Protected Baseline

Protect the existing `tes-goal-maestro` contracts:

- explicit `--execute-loop` opt-in;
- one active SPEC at a time;
- parent runner authority;
- local-only default behavior;
- no remote, cloud, share, publish, or automation action without explicit owner
  authorization;
- existing `Execution Thermometer` and `Adversarial Audit Heartbeat` boundaries;
- adapter source parity across Codex, Claude Code, and Cursor;
- report states remain separate from Goal Maestro stop states.

## Non-Objectives

- Do not improve the validation target or validation prompt.
- Do not tune the model prompt to make the next canary easier.
- Do not encode canary-specific product nouns into Goal Maestro.
- Do not add telemetry, dashboards, background jobs, implicit sharing, or remote
  execution.
- Do not collapse the 24 P0 slices into a single broad patch.

## Required Stop States

- `NEEDS_LINEAR_SPEC_PIPELINE`
- `NEEDS_PRE_EDIT_GATE_ARTIFACT`
- `NEEDS_PROMPT_ENRICHMENT_PACKET`
- `NEEDS_DOCUMENT_ANALYSIS`
- `NEEDS_SPEC_FIDELITY`
- `NEEDS_THERMOMETER_FIDELITY`
- `NEEDS_LEDGER_GRAMMAR`
- `NEEDS_REPORT_COHERENCE`
- `NEEDS_THERMOMETER_PACKAGE_HIERARCHY`
- `NEEDS_REPORT_IDENTITY`
- `NEEDS_VISUAL_EVIDENCE_CONTRACT`
- `NEEDS_VISUAL_SEMANTIC_GATE`
- `NEEDS_BROWSER_METRICS_SCHEMA`
- `NEEDS_INSTALL_CHRONOLOGY`
- `NEEDS_COMMIT_ENFORCEMENT_CLASSIFICATION`
- `NEEDS_GIT_REPOSITORY`
- `NEEDS_EVIDENCE_TRACKING_CLASSIFICATION`
- `NEEDS_FLASH_FRY_STATUS`
- `NEEDS_LENS_LEDGER`
- `NEEDS_CLOUD_SEARCH_CLASSIFICATION`
- `NEEDS_LLM_CACHE_COST_TELEMETRY`
- `NEEDS_CLOSEOUT_CONSISTENCY`
- `NEEDS_HEARTBEAT_SIDECAR`
- `NEEDS_NO_AUTOMATION_BOUNDARY`
- `PASS_P0_HARNESS_ORCHESTRATION_FEEDBACK_FIDELITY`

## Execution Slices

### SPEC-001 - Linear SPEC Pipeline Gate

Goal: make sequential execution enforceable, not narrative.

- The parent runner opens exactly one `ACTIVE_SPEC`.
- The next SPEC cannot open until the active SPEC has evidence, oracle result,
  local commit status, and parent validation.
- Evidence produced before a SPEC opens cannot satisfy that SPEC.
- Broad implementation before SPEC activation must stop the loop.

- A fixture where multiple SPECs are implemented before parent validation fails.
- A fixture with strict SPEC-001 -> SPEC-002 -> SPEC-003 evidence passes.
- Stop state on violation: `NEEDS_LINEAR_SPEC_PIPELINE`.

### SPEC-002 - Pre-Edit Gate Artifact

Goal: require a durable pre-edit artifact before any material edit.

- Emit `pre_edit_gate.json` or equivalent package-local artifact before first
  edit.
- Include active SPEC, first unexecuted SPEC, anchor hash, baseline state,
  allowed files, forbidden files/actions, required gates, installed TES version,
  and commit mode.
- The artifact must be cited by ledger, thermometer metrics, and closeout.

- Loop start without the artifact fails.
- Artifact after first edit fails chronology.
- Stop state: `NEEDS_PRE_EDIT_GATE_ARTIFACT`.

### SPEC-003 - Prompt Enrichment Packet

Goal: prove that Goal Maestro enriched the source artifact before execution.

- Emit `prompt_enrichment_packet.json` or `.md`.
- Include extracted intent, SPEC queue, lenses selected, structural method,
  oracle packet, evidence contract, stop states, risk decisions, non-objectives,
  and sidecar requirements.
- The user must not need to provide an optimized execution prompt.

- Missing enrichment packet blocks execution.
- Packet that only repeats the user prompt fails.
- Stop state: `NEEDS_PROMPT_ENRICHMENT_PACKET`.

### SPEC-004 - Document Analysis Gate

Goal: convert ADR, PRD, Super SPEC, or project artifact into a documented
analysis packet before execution.

- Emit `document_analysis_packet.json` or `.md`.
- Map functional requirements, non-functional requirements, acceptance criteria,
  forbidden moves, visual/runtime requirements, evidence requirements, and
  explicit ambiguities.
- Record whether external documentation or cloud search is required.

- Execution without a document analysis packet fails.
- Packet with missing acceptance criteria fails.
- Stop state: `NEEDS_DOCUMENT_ANALYSIS`.

### SPEC-005 - SPEC Fidelity Gate

Goal: preserve declared execution units exactly.

- Compare declared SPEC IDs with opened, executed, committed, and reported SPEC
  IDs.
- Fail on skipped, merged, reordered, or anticipated SPECs unless a bounded
  repair unit is explicitly declared and accepted.
- Require per-SPEC evidence after the SPEC opened.

- Declared `SPEC-003` missing from execution fails.
- Audit row counted as material SPEC fails.
- Stop state: `NEEDS_SPEC_FIDELITY`.

### SPEC-006 - Thermometer Fidelity Gate

Goal: prevent a rendered report from hiding incorrect execution semantics.

- Block complete closeout if Thermometer emits `SPEC-UNKNOWN`.
- Block if any declared material SPEC is missing.
- Block if `EXECUTIVE-STOP-AUDIT` or equivalent audit unit is counted as a
  material SPEC.
- Block if `unproven_metrics > 0` for required execution fidelity fields.

- Real canary-derived fixtures for unknown SPEC and audit-as-SPEC fail.
- Correct `SPEC-001,SPEC-002,SPEC-003` fixture passes.
- Stop state: `NEEDS_THERMOMETER_FIDELITY`.

### SPEC-007 - Canonical Ledger Grammar

Goal: define the ledger grammar the extractor can trust.

- Material SPEC sections use `### SPEC-NNN - Title`.
- Each material section contains exactly one matching `spec_id: SPEC-NNN`.
- Audit and closeout sections cannot appear inside the final material SPEC body.
- Audit fields cannot overwrite material `spec_id`.

- Parser fixtures reproduce the observed last-SPEC overwrite bug.
- Malformed grammar fails before Thermometer packaging.
- Stop state: `NEEDS_LEDGER_GRAMMAR`.

### SPEC-008 - Ledger Metrics Receipt HTML Coherence

Goal: make every report surface agree.

- The same SPEC IDs, final status, report status, share status, evidence hashes,
  and unproven counts must appear in ledger, metrics, receipt, and HTML.
- Chat closeout cannot say pass when receipt or metrics says unproven.

- Coherence oracle fails on contradictory surfaces.
- Correct package passes after checksum validation.
- Stop state: `NEEDS_REPORT_COHERENCE`.

### SPEC-009 - Thermometer Package Finalization Hierarchy

Goal: avoid competing reports for one loop.

- Every package declares whether it is `latest`, `superseded`, or historical.
- A failed earlier package records `superseded_by` when repaired.
- The closeout links only the latest package unless explicitly listing history.

- Two unsorted package candidates fail.
- One latest plus one superseded package passes.
- Stop state: `NEEDS_THERMOMETER_PACKAGE_HIERARCHY`.

### SPEC-010 - Report Identity And Version Accuracy

Goal: make identity fields operationally useful.

- `harness.version` reflects the installed TES package version.
- `adapter` resolves to `codex`, `claude`, or `cursor` when known.
- Model and reasoning fields are either real observed values or explicit
  `unproven` with reason.
- `installed_version`, `installed_at`, and source package identity are captured
  where available.

- `harness.version: 0.1.0` under installed TES `0.3.x` fails.
- `adapter: other` for known hosts fails.
- Stop state: `NEEDS_REPORT_IDENTITY`.

### SPEC-011 - Visual Evidence Contract

Goal: define minimum scene coverage for UI, browser, and rendered app work.

- Require scene evidence appropriate to the artifact class.
- For interactive rendered work, require at minimum: initial state, active state
  with domain objects, terminal/end state, and mobile/responsive evidence when
  the source artifact asks for responsive behavior.
- A screenshot must be mapped to the state it proves.

- Initial-state-only evidence cannot mark active-state visual proof as complete.
- Terminal-state-only evidence cannot mark active-state proof as complete.
- Stop state: `NEEDS_VISUAL_EVIDENCE_CONTRACT`.

### SPEC-012 - Visual Semantic Gate

Goal: make visual proof semantic, not just non-blank pixels.

- Keep pixel non-degeneracy as a floor.
- Add semantic assertions per artifact class: expected objects, state label,
  score/status, layout area, and interaction result.
- For rendered work, prove expected object classes are visible in the expected
  state.

- A non-blank screenshot without required scene objects fails.
- An active-state screenshot with expected objects and state metadata passes.
- Stop state: `NEEDS_VISUAL_SEMANTIC_GATE`.

### SPEC-013 - Browser Metrics Schema

Goal: standardize browser metrics across hosts.

- Define a common `browser-metrics.json` schema.
- Include runtime target, browser source, console errors, uncaught errors,
  screenshots, state transitions, visual assertions, interaction path, restart
  where applicable, scoring or domain metrics where applicable, and failures.

- Host-specific minimal metrics that omit required fields fail.
- All three adapters can generate or validate the same schema.
- Stop state: `NEEDS_BROWSER_METRICS_SCHEMA`.

### SPEC-014 - Install Chronology Gate

Goal: prove the target used the installed TES baseline.

- Emit `install_chronology.json` or equivalent fields.
- Record installed version, installed timestamp, git HEAD before loop, baseline
  commit, and material commit timestamps.
- Fail if installation evidence is after material commits unless explicitly
  classified as unrelated later reinstall.

- Install-after-material fixture fails.
- Install-before-baseline fixture passes.
- Stop state: `NEEDS_INSTALL_CHRONOLOGY`.

### SPEC-015 - Commit Enforcement Classification

Goal: stop conflating manual commits with hook enforcement.

- Record `commit_mode=manual`, `precommit_enforced`, or `unknown`.
- If TES recommends a pre-commit hook, installed target evidence must show the
  hook or explicitly mark `PRECOMMIT_NOT_INSTALLED`.
- Reports must not imply hook enforcement when commits are manual.

- Missing pre-commit plus enforcement claim fails.
- Manual commit evidence with honest classification passes.
- Stop state: `NEEDS_COMMIT_ENFORCEMENT_CLASSIFICATION`.

### SPEC-016 - Git Admission Gate

Goal: handle non-git targets honestly.

- Before loop execution, confirm a Git repository exists.
- If absent, stop with `NEEDS_GIT_REPOSITORY` or request explicit owner
  authorization for `git init`.
- Record the owner decision and baseline commit classification.

- Silent `git init` fails.
- Explicit owner authorization with baseline evidence passes.
- Stop state: `NEEDS_GIT_REPOSITORY`.

### SPEC-017 - Evidence Tracking Classification

Goal: make evidence storage status explicit.

- Classify ledger, screenshots, metrics, reports, and packages as tracked,
  runtime-only, ignored, or intentionally untracked.
- Closeout cannot say clean evidence if required evidence is untracked without
  classification.

- `git status` clean for tracked files while required untracked evidence exists
  fails unless classified.
- Stop state: `NEEDS_EVIDENCE_TRACKING_CLASSIFICATION`.

### SPEC-018 - Flash-Fry Operational Status

Goal: turn Flash-Fry from an assumed capability into an observable status.

- Record `flash_fry_status=ran|not_required|not_configured|blocked`.
- If `ran`, cite artifact, marker, or decision packet.
- If not run, reports must say why.
- Do not introduce a new command solely to satisfy this status.

- Absence of Flash-Fry status fails when loop reports protection quality.
- Honest `not_configured` passes with protection score adjusted.
- Stop state: `NEEDS_FLASH_FRY_STATUS`.

### SPEC-019 - Lens Ledger

Goal: record which lenses shaped execution.

- Emit a lens ledger or section with document, product, architecture, runtime,
  visual, security, performance, evidence, adversarial, cost, DX, and delivery
  classification.
- Each lens is `applied`, `not_required`, or `blocked`, with one-line impact.

- Protection or proof score cannot cite lenses without lens evidence.
- Stop state: `NEEDS_LENS_LEDGER`.

### SPEC-020 - Cloud Search Classification

Goal: make cloud or external lookup decisions explicit.

- Record `cloud_search=required|not_required|not_authorized|blocked|ran`.
- Include reason and redaction/authorization status when relevant.
- Do not run cloud search unless the owner explicitly authorizes it or the
  active contract already allows it.

- Silent omission fails.
- Honest `not_required` passes for self-contained local work.
- Stop state: `NEEDS_CLOUD_SEARCH_CLASSIFICATION`.

### SPEC-021 - LLM Cache And Cost Telemetry

Goal: support efficiency claims with evidence.

- Record input tokens, cached input tokens, output tokens, reasoning tokens,
  cache-hit estimate, wall time where available, and confidence.
- Missing fields become `unproven`, not zero.

- Efficiency score based on absent token/cache data fails.
- `unproven` efficiency data lowers or qualifies the score.
- Stop state: `NEEDS_LLM_CACHE_COST_TELEMETRY`.

### SPEC-022 - Closeout Consistency Gate

Goal: prevent final chat claims from outrunning artifacts.

- Compare chat closeout, ledger, metrics, receipt, HTML, and package manifest.
- Block complete closeout if any required surface says `UNPROVEN`,
  `NEEDS_LEDGER_EVIDENCE`, missing SPEC, or contradictory status.

- Chat PASS with receipt UNPROVEN fails.
- All surfaces aligned passes.
- Stop state: `NEEDS_CLOSEOUT_CONSISTENCY`.

### SPEC-023 - Heartbeat Sidecar Materialization

Goal: make `--audit-heartbeat-prompt` visible when requested.

- With `--execute-loop --audit-heartbeat-prompt`, emit the read-only heartbeat
  prompt as same-response sidecar or tracked local artifact.
- Do not create a second Goal Maestro command.
- Do not execute, schedule, or share the heartbeat.

- Contract-only pass without closeout sidecar evidence fails.
- Sidecar present with read-only boundary passes.
- Stop state: `NEEDS_HEARTBEAT_SIDECAR`.

### SPEC-024 - No Automation Boundary

Goal: block unintended scheduling, wakeups, and jobs.

- Goal Maestro and Heartbeat cannot create host jobs, wakeups, schedules, or
  automations by default.
- Any host-level automation requires separate explicit owner authorization.
- Reports must classify accidental automation as a boundary violation.

- A scheduled wakeup without explicit automation authorization fails.
- No automation plus explicit sidecar prompt passes.
- Stop state: `NEEDS_NO_AUTOMATION_BOUNDARY`.

## Required P0 Oracles

- Focused fixture suite for the observed canary failures.
- Thermometer parser and coherence oracle.
- Visual evidence contract oracle.
- Install chronology oracle.
- Commit enforcement classifier.
- Heartbeat sidecar materialization oracle.
- No-automation boundary oracle.
- Adapter materialization proof across Codex, Claude Code, and Cursor.

## Done Means

P0 is complete only when the observed failure classes fail before repair,
the repaired harness passes source and installed-target canaries, and the same
unchanged external validation prompt cannot close as complete unless the execution
line, evidence line, thermometer line, and chat closeout agree.
