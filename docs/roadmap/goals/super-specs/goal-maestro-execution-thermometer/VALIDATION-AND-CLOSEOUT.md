---
tds_id: roadmap.goal_super_spec.goal_maestro_execution_thermometer.validation_closeout
tds_class: roadmap
status: active
consumer: maintainers, Goal Maestro authors, oracle authors, release reviewers, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Goal Maestro Execution Thermometer: Validation And Closeout

This document defines the stop states, privacy gates, validation plan, and final
closure contract for the Execution Thermometer project.

## Stop States

Required stop states:

- `NEEDS_BASELINE_ORACLE`;
- `NEEDS_THERMOMETER_SCHEMA`;
- `NEEDS_LEDGER_EVIDENCE`;
- `NEEDS_METRIC_EVIDENCE`;
- `NEEDS_CONTEXT_RECEIPT_RENDERER`;
- `NEEDS_HTML_LOOP_SELECTION`;
- `NEEDS_GOLD_GATE_EVIDENCE`;
- `NEEDS_SANITIZATION`;
- `BLOCKED_BY_SANITIZATION`;
- `BLOCKED_BY_MISSING_DESTINATION`;
- `BLOCKED_BY_GITHUB_AUTH`;
- `NEEDS_OWNER_SHARE_DECISION`;
- `NEEDS_GITHUB_DESTINATION`;
- `NEEDS_GOAL_MAESTRO_INTEGRATION`;
- `NEEDS_USER_DOCS`;
- `NEEDS_INSTALLED_CANARY`;
- `NEEDS_RELEASE_IDENTITY_DECISION`;
- `THERMOMETER_PACKAGE_READY`;
- `THERMOMETER_SHARED_DRAFT_PR`;
- `THERMOMETER_LOCAL_ONLY`.

Stop states must be visible in the report package and final closeout. A blocked
share path must not mark the core local report as failed if local reporting
completed correctly.

## Privacy And Sanitization

Sanitization must run before a report is proposed for sharing.

Blocked content:

- secrets and tokens;
- private project names;
- private filesystem paths;
- private storage/backend names;
- raw prompts;
- raw diffs unless explicitly sanitized and allowed;
- full logs with uncontrolled content;
- proprietary customer data;
- internal service identifiers;
- unsanitized screenshots.

Required sanitizer outputs:

- pass/fail status;
- sanitizer version;
- files scanned;
- blocked patterns;
- private vocabulary result;
- shareable file list;
- excluded file list.

If sanitization is `UNPROVEN`, share status is blocked.

## GitHub Remote Gate

No remote GitHub action is allowed from this project without explicit owner
approval for the exact run and destination.

Required remote preconditions:

1. report classified `gold`;
2. package generated locally;
3. sanitizer passed;
4. owner approved sharing;
5. destination configured;
6. dry-run showed files, branch, and draft PR summary;
7. authentication available.

Failure to satisfy a remote precondition results in a blocked share state, not an
implementation workaround.

## Validation Plan

Focused validation must include:

```text
schema valid fixture -> pass
schema invalid fixture -> fail
extractor missing evidence fixture -> UNPROVEN
Markdown receipt fixture -> five signals present
HTML multi-loop fixture -> #loop-L4 loads selected loop
Gold gate ordinary fixture -> ordinary
Gold gate useful fixture -> useful
Gold gate gold fixture -> gold
sanitizer unsafe fixture -> blocked
share ordinary fixture -> no prompt
share gold unsafe fixture -> blocked
GitHub dry-run fixture -> no remote write
existing Goal Maestro execute-loop fixture -> unchanged behavior
installed-target canary -> local package generated
```

Repository gates before closeout:

- focused unit/oracle tests for changed surfaces;
- adapter materialization or parity check if delivered adapters change;
- package validation for delivered source changes;
- release check if version/bundle identity changes.

## Acceptance Criteria

The project is complete only when:

1. a Goal Maestro loop can generate the Markdown context receipt from local
   evidence;
2. a local package can be generated with README, Markdown, YAML, JSON, HTML, and
   checksums;
3. the HTML opens offline and loop links load the selected loop detail;
4. metrics without evidence are marked `UNPROVEN`;
5. the Gold Analysis Gate classifies ordinary/useful/gold fixtures correctly;
6. the Share Gate asks only for gold reports and only after sanitization passes;
7. GitHub sharing remains explicit, dry-run capable, and remote-action gated;
8. sanitizer blocks secrets, private paths, and private vocabulary fixtures;
9. Goal Maestro execution semantics remain unchanged;
10. adapter parity remains intact;
11. installed-target canary proves the local package path;
12. release identity is decided before any delivered-behavior closeout.

## Final Delivery Contract

Final closeout must include:

- SPECs executed;
- commits;
- files changed;
- script classification for every `scripts/**` path;
- package sample path;
- Markdown receipt sample path;
- HTML report sample path;
- YAML/JSON schema version;
- sanitizer result;
- gold gate result;
- share status;
- GitHub remote status;
- installed canary result;
- release identity decision;
- stop state.

## Local Package README Contract

Every generated evidence package must include a README that explains:

- what the package is;
- which run produced it;
- which files are source data and which are render outputs;
- what was excluded by sanitization;
- whether sharing was requested, declined, approved, or blocked;
- how to open the HTML report locally;
- how to verify checksums.

## Closure Rule

Do not claim this project sealed until the implementation proves both sides:

1. the report system works from real Goal Maestro evidence;
2. the original Goal Maestro harness still behaves the same when reporting is
   disabled or when report generation is local-only.
