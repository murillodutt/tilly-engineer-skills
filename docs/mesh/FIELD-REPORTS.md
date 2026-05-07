---
tds_id: mesh.field_reports
tds_class: mesh
status: active
consumer: installer authors, adopters, and agents
source_of_truth: true
evidence_level: L2
tver: 0.2.0
---

# Tilly Field Reports

Tilly Field Reports is the project feedback gate for real-world TES operation.
It is active by default and sends only sanitized operational facts to GitHub
issues in `murillodutt/tilly-engineer-skills`.

## Contract

Field Reports may record package version, runtime, OS, event name, status,
duration bucket, Tilly gate names, return codes, feature presence, failure
categories, and hash fingerprints.

Field Reports must never send code, diffs, prompts, file contents, raw stack
traces, secrets, tokens, personal data, absolute paths, raw branch names, or raw
remote URLs. Reports are factual prose and bullets only; they must not contain
tables or code blocks.

The local identity is a random `install_id` stored under
`.tilly/field-reports/`. It is not the project name and not a user identity.

## GitHub Receiver

The GitHub side is governed by `.github/ISSUE_TEMPLATE/tilly-field-report.yml`,
`.github/workflows/field-report-governance.yml`, and
`scripts/field_reports_github_oracle.py`.

The receiver requires the `tilly-field-report@1` schema marker, rejects reports
with code blocks, tables, absolute paths, private URLs, raw remotes, raw branch
names, secrets, personal data, or raw stack traces, and labels accepted reports
as sanitized. A rejected report is quarantined and closed. This workflow is a
second gate, not a privacy substitute for local sanitization.

## Local State

The local transport state is:

- `.tilly/field-reports/outbox.jsonl` for pending sanitized events.
- `.tilly/field-reports/receipts/**` for issue receipts without payload.
- `.tilly/field-reports/DISABLED` as the opt-out sentinel.

When the target is a Git repository, `.git/info/exclude` must ignore
`.tilly/field-reports/`. Git remains the project history. The outbox, GitHub
issues, hooks, and receipts are transport and evidence aids, not source of
truth for project behavior.

## Runtime

The deterministic CLI is `scripts/field_reports.py`.

Supported internal operations are `capture`, `drain`, `status`, `disable`,
`enable`, `install-hook`, and `--self-test`.

`install-hook` installs a local `pre-push` wrapper that calls:

```text
python3 .tilly/bin/field_reports.py drain --target . --trigger pre-push
```

If an existing `pre-push` hook exists, it is backed up and chained before the
Field Reports drain. If Git, `gh`, network, or authentication is unavailable,
Field Reports records `BLOCKED` where possible, keeps the outbox pending, and
must not block the push.

## Opt-Out

Opt-out is binary. Creating `.tilly/field-reports/DISABLED` stops both
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
blocked, or degraded states.

## Certification

The official deterministic gate is:

```text
python3 scripts/field_reports.py --self-test
python3 scripts/field_reports_github_oracle.py --self-test
```

Package closure must include this gate through `npm run commit:check`.
