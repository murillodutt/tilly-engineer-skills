# Runtime Signal Report

## Command

- Safe label: `<safe-command-label>`
- Command fingerprint: `<sha256-or-none>`

## Mode

- Selected mode: `<smoke-host-real|product-host-real|ceiling-replay>`
- Reported claim: `<smoke-host-real|product-host-real|ceiling-replay>`

## Target

- Target fingerprint: `<sha256-or-safe-label>`

## Transcript

- Status: `<PASS|NEEDS_EVIDENCE|FAIL>`
- SHA-256: `<sha256-or-none>`
- Tool uses: `<count>`
- Tool results: `<count>`
- Subagent count: `<count-or-not-checked>`

## Ledger Runtime Signal

- Ledger rows: `<count>`
- Host-real rows: `<count>`
- Runtime context rows: `<count>`
- Marker rows: `<count>`

## First Artifact Mutation

- Artifact: `<relative-path-or-none>`
- Tool: `<safe-tool-name-or-none>`
- Runtime context present: `<yes|no>`

## Artifact Marker

- Checks: `<count>`
- Marker present: `<yes|no>`

## Contamination

- Classification: `<clean|forbidden_lookup>`
- Manual lookup tool uses: `<count>`
- Benign marker mentions: `<count>`

## Related Gates

`<sanitized gate list>`

## Residual Blockers

`<none-or-sanitized-blockers>`

## Decision

`<PASS_RUNTIME_SIGNAL_HARNESS|PASS_WITH_FINDINGS|NEEDS_*|BLOCKED>`

## Forbidden Content

Do not include raw prompt text, raw transcript JSONL, tool inputs or results,
subagent messages, secrets, or credentials.
