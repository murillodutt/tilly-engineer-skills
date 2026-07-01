# Agent Hooks Certification Report

## Scope

- Target: `<target-label-or-none>`
- Current host: `<codex|claude|cursor|none>`
- Decision: `<SOURCE_CERTIFIED|TARGET_CERTIFIED|HOST_CERTIFIED|CERTIFIED_WITH_RESIDUALS|NEEDS_EVIDENCE|FAIL>`
- Loop count: `<count>`

## Host Replay

- Command label: `<safe-label-or-none>`
- Command fingerprint: `<sha256-or-none>`
- Transcript status: `<PASS|NEEDS_EVIDENCE|FAIL|not-run>`
- Transcript hash: `<sha256-or-none>`
- Parsed events: `<count-or-none>`
- Tool uses/results: `<uses>/<results>`
- Fresh replay: `<yes|no|not-run>`

## Matrix Summary

- Source rows: `<pass>/<total>`
- Target rows: `<pass>/<total-or-not-run>`
- Host rows: `<pass>/<total-or-not-run>`
- Failed rows: `<ids-or-none>`
- Evidence gaps: `<ids-or-none>`

## Related Gates

- `tes_install.py --self-test`: `<status>`
- `pretooluse_contract_oracle.py --self-test`: `<status>`
- `hook_audit_prompt_oracle.py --self-test`: `<status>`
- `tes_install.py hook-health`: `<status>`
- `canary_admission_oracle.py`: `<status>`
- `installed_certification_oracle.py`: `<status>`

## Fix Loop

- Failure class: `<host_execution_gap|transcript_gap|oracle_gap|product_gap|evidence_gap|false_green|none>`
- Source owner: `<file-or-none>`
- Fix commit: `<hash-or-none>`
- Replayed same command: `<yes|no|not-needed>`

## Residuals

`<none-or-sanitized-residuals>`

## Decision

`<one-paragraph decision with the exact row that still blocks, if any>`
