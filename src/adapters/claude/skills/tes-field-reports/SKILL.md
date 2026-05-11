---
name: tes-field-reports
description: Use when the user says /tes-field-reports, /tes:field-reports, /tes:field-reports:disable, /tes:field-reports:enable, or asks to inspect, drain, disable, enable, install, or explain sanitized TES Field Reports.
---

# TES Field Reports

`/tes-field-reports` is the preferred shared TES trigger for sanitized
operational feedback. `/tes:field-reports` is a compatible TES intent alias.

Field Reports records operational facts, not project truth. Use it to inspect
local feedback state, drain pending reports, disable or re-enable collection, or
repair the local pre-push drain hook.

## Intent Map

Use the installed helper inside a target project, or `scripts/field_reports.py`
when certifying from the TES source package.

| User intent | Preferred action |
|-------------|------------------|
| inspect state | `field_reports.py status --target . --json-only` |
| drain pending reports | `field_reports.py drain --target . --trigger manual --json-only` |
| disable reports | `field_reports.py disable --target . --json-only` |
| enable reports | `field_reports.py enable --target . --json-only` |
| repair hook | `field_reports.py install-hook --target . --json-only` |
| certify package behavior | `field_reports.py --self-test` |

## Rules

- Do not expand collection scope, schema, or detail levels.
- Do not treat reports, outbox records, receipts, or GitHub issues as project
  truth.
- Drain only when explicitly requested, or when the already-installed pre-push
  hook invokes it.
- Do not record exploratory `/tes-update` probes; only the final certification
  probe may record one field report.
- Report `BLOCKED` with the exact precondition when GitHub transport, local Git,
  or invalid outbox records prevent the action.

## Done

Close when the requested Field Reports action returns `PASS`, `SKIP`,
`BLOCKED`, or `NEEDS_REVIEW` with the relevant writes, pending count, receipt,
or blocker named.
