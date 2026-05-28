---
tds_id: mesh.field_reports
tds_class: mesh
status: active
consumer: installer authors, adopters, and agents
source_of_truth: true
evidence_level: L2
tver: 0.2.1
---

# TES Field Reports

TES Field Reports is the project feedback gate for real-world TES operation.
It is active by default, captures only sanitized operational facts locally, and
drains through `gh issue create` only when local GitHub CLI, authentication, and
network are available. Deterministic certification covers local capture/drain,
fake `gh` transport, and receiver quarantine; live GitHub publication remains a
partial surface until explicitly authorized and replayed against the real
transport.

## Contract

Field Reports may record package version, runtime, OS, event name, status,
duration bucket, Tilly gate names, return codes, feature presence, failure
categories, report class, product class, severity, certification impact, owner
surface, next action, privacy state, signal score, and hash fingerprints.
Each high-signal report also exposes uppercase product-maintenance classes such
as `CERTIFICATION_GAP`, `ADAPTER_DRIFT`, `RELEASE_HYGIENE`, `PRODUCT_BUG`, or
`LOW_SIGNAL_SUPPRESSED` so maintainer triage can group sanitized reports by
ADR 0003.1 product responsibility rather than only by transport event shape.

High-signal classes include version drift, helper-contract failure,
adapter/runtime drift, MCP activation failure, Cortex certification batches,
legacy migration, installation signals, and multi-surface operations. Each
high-signal report is deduped by a sanitized fingerprint and carries an owner
surface plus bounded next action so it can feed TES product work instead of
becoming undifferentiated telemetry. Low-signal heartbeats are suppressed
locally with a receipt instead of becoming issues.

Field Reports must never send code, diffs, prompts, file contents, raw stack
traces, secrets, tokens, personal data, absolute paths, raw branch names, or raw
remote URLs. Reports are factual prose and bullets only; they must not contain
tables or code blocks.

The local identity is a random `install_id` stored under
`.tes/field-reports/`. It is not the project name and not a user identity.
Published reports use a hash fingerprint of that ID, not the raw value.

Captured events also carry the runtime scope defined in
`docs/mesh/SCOPE-CONTRACT.md`. Scope uses an opaque local project fingerprint
and bounded TES evidence references so Field Reports can correlate operational
events without publishing project names, local paths, branch names, remotes, or
user identity. Unsafe scope references block capture without writing to the
outbox.

`docs/mesh/EVENT-LEDGER.md` is separate from Field Reports. The ledger is local
read-only lifecycle inspection, not GitHub transport, not a report outbox, and
not a feedback destination. Field Reports may report that ledger inspection
failed, but it must not drain ledger records as if they were Field Reports.

`docs/mesh/CHECKPOINTS.md` is also separate from Field Reports. Checkpoints are
local TTL resumability state under `.tes/checkpoints/**`, not feedback, not
durable memory, and not certification evidence. Field Reports may report that
checkpoint validation failed, but must not publish checkpoint contents.

## GitHub Receiver

The GitHub side is governed by `.github/ISSUE_TEMPLATE/tes-field-report.yml`,
`.github/workflows/field-report-governance.yml`, and
`scripts/field_reports_github_oracle.py`.

The receiver requires the `tes-field-report@2` schema marker, rejects reports
with code blocks, tables, absolute paths, private URLs, raw remotes, raw branch
names, secrets, personal data, or raw stack traces, and labels accepted reports
as sanitized when a real issue exists. The receiver oracle proves this
quarantine contract without creating live issues. This workflow is a second
gate, not a privacy substitute for local sanitization.
Receiver bodies must include report class, product class, severity,
certification impact, owner surface, next action, privacy state, report
fingerprint, dedupe fingerprint, and uppercase product classes.

## Local State

The local transport state is:

- `.tes/field-reports/outbox.jsonl` for pending sanitized events.
- `.tes/field-reports/receipts/**` for issue receipts without payload.
- `.tes/field-reports/DISABLED` as the opt-out sentinel.

When the target is a Git repository, `.git/info/exclude` must ignore
`.tes/field-reports/` and the local artifact hygiene paths defined in
`GIT-SAFETY.md`. Git remains the project history. The outbox, GitHub issues,
hooks, receipts, rollback backups, bytecode, and SQLite caches are transport,
cache, or evidence aids, not source of truth for project behavior.

## Runtime

The deterministic CLI is `scripts/field_reports.py`.

Supported internal operations are `capture`, `drain`, `status`, `disable`,
`enable`, `install-hook`, and `--self-test`.

`install-hook` installs a local `pre-push` wrapper that calls:

```text
python3 .tes/bin/field_reports.py drain --target . --trigger pre-push
```

If an existing `pre-push` hook exists, it is backed up and chained before the
Field Reports drain. Low-signal heartbeat drains, such as a successful update
check with no version drift and no operational change, are suppressed locally
with a receipt instead of opening a GitHub issue. If Git, `gh`, network, or
authentication is unavailable, Field Reports records `BLOCKED` where possible,
keeps the outbox pending, and must not block the push.
Drain results distinguish `disabled`, `empty`, `suppressed`, `blocked`,
`invalid`, and `sent` transport states. Blocked and invalid drains write
receipts without payload bodies and do not clear pending events.

## Opt-Out

Opt-out is binary. Creating `.tes/field-reports/DISABLED` stops both
collection and drain. Re-enabling removes that sentinel and restores the
default active behavior.

Users do not configure levels, schemas, destinations, verbosity, or expanded
collection. The user-facing prompts for disabling and re-enabling live in the
user manual so the action happens through the active Tilly context window, not
through a raw shell command.

## Capture Points

Field Reports records high-value operational facts from initialization, adapter
installation, MCP activation, install smoke, Cortex verify/audit/rebuild,
Cortex curation/reflection/apply, MCP self-test, commit gates, and failed,
blocked, or degraded states. A report body, whether fake-drained in
certification or later published through real GitHub transport, must include
actionable findings, report class, product class, severity, certification
impact, owner surface, next action, privacy state, actionability, signal score,
report fingerprint, dedupe fingerprint, uppercase product classes, surface
counts, routes, versions, schemas seen, and event details. Transport heartbeats
alone are not product feedback.

## Certification

The official deterministic gate is:

```text
python3 scripts/field_reports.py --self-test
python3 scripts/field_reports_quality_oracle.py --self-test
python3 scripts/field_reports_github_oracle.py --self-test
```

Package closure must include this gate through `npm run commit:check`.
