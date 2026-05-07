---
name: tes-doctor
description: Use when the user says /tes:doctor, /tes:check, /tes:certify, or asks to validate, health-check, certify, or prepare a Tilly Engineer Skills commit.
---

# TES Doctor

`/tes:doctor` is the shortcut for package and mesh health checks. Use
`/tes:check` and `/tes:certify` as aliases.

## Gate Selection

Run the smallest gate that proves the claim:

| Claim | Typical oracle |
|-------|----------------|
| package shape is valid | `npm run validate` |
| docs stay modular | `npm run docs:size` |
| TDS is aligned | `npm run tds:validate` |
| Cortex core works | `npm run cortex:self-test` |
| MCP helper works | `npm run mcp:self-test` and `npm run cortex:mcp:self-test` |
| Field Reports works | `npm run field-reports:self-test` |
| adapters materialize | `npm run materialize:check` |
| platform surfaces align | `npm run platform:surface:check` |
| final local closure | `npm run commit:check` |

## Rules

- Do not run heavy gates when a narrow oracle proves the claim.
- Do not certify skipped commands as passing.
- Before commit, prefer `npm run commit:check`.
- After commit, rerun the principal gate when the user asks for sealed closure.
