# Agent Hook Finding Certification Report

## Scope

- Target: `<target-label-or-none>`
- Current host: `<codex|claude|cursor|none>`
- Finding manifest: `references/agent-hook-findings.json`
- Overall status: `<PASS|NEEDS_EVIDENCE|FAIL|BLOCKED>`

## Host Replay

- Command label: `<safe-label-or-none>`
- Command fingerprint: `<sha256-or-none>`
- Transcript status: `<PASS|NEEDS_EVIDENCE|FAIL|not-run>`
- Transcript hash: `<sha256-or-none>`
- Tool uses/results: `<uses>/<results>`
- Fresh replay: `<yes|no|not-run>`

## Finding Summary

- Findings checked: `<count>`
- Source certified: `<count>`
- Target certified: `<count>`
- Host certified: `<count>`
- Host not applicable: `<count>`
- Refuted: `<count>`
- Needs evidence: `<ids-or-none>`
- Failed: `<ids-or-none>`

## Finding Matrix

| Finding | Required lane | Host applicability | Status | Evidence |
|---|---|---|---|---|
| `<H-03>` | `<host>` | `<required>` | `<HOST_CERTIFIED>` | `<source rows + host rows + gates>` |

## Gates

- `install_smoke.py --route audit`: `<status-or-not-run>`
- `pretooluse_kernel_oracle.py`: `<status-or-not-run>`
- `pretooluse_session_oracle.py`: `<status-or-not-run>`
- `tes_install.py --self-test`: `<status-or-not-run>`
- `canary_admission_oracle.py --self-test`: `<status-or-not-run>`
- `tes_update.py --self-test`: `<status-or-not-run>`

## Residuals

`<none-or-sanitized-residuals>`

## Decision

`<one paragraph. Name every finding still blocking and the exact missing lane.>`
