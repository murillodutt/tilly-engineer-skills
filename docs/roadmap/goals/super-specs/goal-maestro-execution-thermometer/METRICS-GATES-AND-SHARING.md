---
tds_id: roadmap.goal_super_spec.goal_maestro_execution_thermometer.metrics_gates_sharing
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, oracle authors, GitHub workflow reviewers, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Goal Maestro Execution Thermometer: Metrics, Gates, And Sharing

This document defines what the thermometer may measure and how it decides
whether a run is ordinary, useful, or gold. The gate is conservative: it rewards
learning value and evidence quality, not flattering scores.

## Five Fundamental Signals

### Delivery

Question: did the loop deliver the intended product or loop outcome?

Inputs:

- accepted objective;
- SPEC completion statuses;
- final artifact paths;
- runtime/build/test evidence;
- final stop state.

Rules:

- `ON TRACK` requires the declared deliverable or accepted stop state.
- `UNPROVEN` is required when the deliverable exists but lacks evidence.
- `FAIL` is required when the loop claims delivery but the oracle failed.

### Fidelity

Question: did the harness preserve the accepted execution plan?

Inputs:

- accepted SPEC list;
- active-SPEC ledger;
- skipped/reordered SPEC evidence;
- scope additions;
- final audit.

Rules:

- A skipped SPEC requires `NEEDS REVIEW` or `FAIL` unless explicitly accepted.
- Silent scope expansion reduces fidelity even if delivery succeeded.
- Reordered execution is allowed only when ledger rationale is present.

### Proof

Question: was the result backed by enough evidence?

Inputs:

- test reports;
- runtime/manual evidence;
- structural probes;
- visual evidence where required;
- acceptance criteria;
- citation coverage.

Rules:

- Proof cannot be higher than the weakest required oracle class.
- Missing evidence must be represented as `UNPROVEN`, not zero.
- Passing build-only proof is insufficient for user-visible runtime behavior.

### Efficiency

Question: was execution economical without weakening proof?

Inputs:

- attempts per SPEC;
- rework count;
- elapsed time;
- token and cost metrics when available;
- cache hit/miss data;
- repeated context reuse;
- validation reruns.

Rules:

- Efficiency may be `UNPROVEN` when token/cost data is unavailable.
- Lower cost must not improve the score if proof or fidelity weakened.
- A SPEC that needed repair may still be efficient if the repair prevented a
  larger downstream defect and evidence supports that claim.

### Protection

Question: did the harness prevent weak, unsafe, or contaminated execution?

Inputs:

- Flash-Fry result;
- lens decisions;
- privacy/sanitization results;
- stop states;
- negative grep or semantic safety checks;
- final audit findings.

Rules:

- A blocked unsafe share can improve protection even when delivery is local-only.
- Protection is `FAIL` when a remote action occurs without explicit approval.
- A missing sanitizer makes share status blocked, not merely unproven.

## Full X-Ray Metrics

The HTML report may expose the full enterprise view. At minimum it should be able
to represent these measurement families:

1. five-signal summary;
2. SPEC intent precision;
3. SPEC fidelity to accepted plan;
4. SPEC proof coverage;
5. rework and attempt count;
6. lens contribution;
7. Flash-Fry blocks and saves;
8. LLM/cache economy;
9. token/cost status;
10. runtime/build/test latency;
11. oracle strength;
12. structural-method health;
13. material diff/sync discipline;
14. commit rhythm;
15. unproven metric inventory;
16. anti-gaming flags;
17. privacy and sanitization status;
18. model/harness/profile identity;
19. release identity pressure;
20. final stop-state quality.

The report may add fields, but it must preserve evidence references and
`UNPROVEN` semantics for every measurement.

## Lens Contribution

Lens metrics answer: what did each lens change?

Required per-lens fields:

- lens id or name;
- decision affected;
- before/after risk statement;
- evidence ref;
- outcome: `changed_decision`, `confirmed_path`, `no_effect`, `blocked`,
  `unproven`.

The report must distinguish a lens that changed an implementation decision from
a lens that merely restated the plan.

## Flash-Fry

Flash-Fry metrics answer: what did the early stress pass prevent or enable?

Required fields:

- status: `passed`, `blocked`, `needs_review`, `unproven`;
- risks detected;
- decisions changed;
- estimated downstream work avoided when evidence-backed;
- false-positive or false-negative notes;
- evidence refs.

Flash-Fry savings are never guessed. If avoided work cannot be proven, the value
is `UNPROVEN` and the narrative may explain the suspected benefit separately.

## Cache Economy

Cache economy answers: did reuse of LLM/cache/context reduce loop cost or time?

Required fields:

- cache source;
- hit/miss counts when available;
- reused context class;
- token/cost/time delta when measured;
- status: `proven`, `unproven`, `not_available`, `blocked`.

No cost saving may be shown as proven unless both baseline and measured values
are present, comparable, and cited.

## Gold Analysis Gate

The Gold Analysis Gate classifies whether a report should be proposed for
sharing back to improve TES.

Allowed classifications:

| Classification | Meaning |
|----------------|---------|
| `ordinary` | Useful local report, no special product learning |
| `useful` | Contains a clear improvement signal, but not strong enough to prompt sharing |
| `gold` | Contains high-value, sanitized, evidence-backed learning for TES evolution |

Gold is not a high score. A failed or blocked loop may be gold if it exposes a
portable defect, weak oracle, missing gate, or harness design improvement.

Gold reason codes:

- `new_stop_state_pattern`;
- `repeated_spec_repair`;
- `lens_broke_decision`;
- `oracle_facade_detected`;
- `cache_economy_unproven`;
- `visual_axis_blocked`;
- `integration_oracle_missing`;
- `high_rework_low_output`;
- `model_reasoning_profile_outlier`;
- `harness_version_regression`;
- `privacy_sanitization_edge`;
- `flash_fry_false_positive`;
- `flash_fry_early_block_saved_cost`;
- `audit_repair_found_late_defect`;
- `claim_artifact_mismatch`.

Gold requires:

1. at least one reason code;
2. cited evidence;
3. sanitizer pass;
4. no private vocabulary leakage;
5. a concise learning summary;
6. local package checksum.

## Share Gate

The Share Gate runs after the Gold Analysis Gate. It never runs for ordinary
reports and never performs remote work without explicit owner approval.

Allowed states:

- `not_requested`;
- `not_gold`;
- `proposed_gold`;
- `declined`;
- `approved_local_export`;
- `draft_pr_opened`;
- `blocked_by_sanitization`;
- `blocked_by_missing_destination`;
- `blocked_by_owner_decision`;
- `blocked_by_github_auth`.

The owner prompt must include:

- run id;
- harness version;
- model and reasoning profile;
- gold reason codes;
- included files;
- excluded files;
- sanitizer result;
- destination repository/branch;
- clear statement that a draft PR will be opened.

## GitHub Sharing Policy

GitHub sharing should create a branch and draft PR in a configured private
repository. The default payload is sanitized YAML plus JSON and checksums. README
may be included if sanitized. HTML and Markdown are excluded by default unless
the owner explicitly permits them for the destination.

Forbidden lanes:

- public Gist;
- issue body dump;
- PR body with full JSON payload;
- direct push to protected branch;
- automatic push after gold classification;
- sharing raw prompts, diffs, logs, private paths, or secrets.

Remote operations require a fresh owner approval for each run.

## Anti-Gaming Rules

- Scores cannot improve from missing evidence.
- Lower token cost cannot compensate for weaker proof.
- A blocked unsafe action is a valid protective outcome.
- HTML presentation cannot hide weak metrics behind aggregate scores.
- SPEC pass rate must distinguish pass, repaired pass, unproven, blocked, and
  skipped.
- Gold sharing is about product learning, not flattering the harness.
