---
tds_id: evidence.context_mesh.cortex_mcp_readonly_2026_05_06
tds_class: evidence
status: active
consumer: MCP adapter authors, Cortex maintainers, and certification reviewers
source_of_truth: false
evidence_level: L3
---

# Cortex MCP Read-Only Smoke Report

This report records the first Cortex MCP cut on May 6, 2026.

## Decision

Result: `GO` for read-only MCP smoke.

Certified scope:

```text
transport: stdio JSON-RPC smoke
tools: verify, audit, recall, read_cell, absorb_plan
writes: none
target: temporary Cortex fixture
```

## Non-Claims

- No write-capable MCP tools.
- No default MCP config for Codex, Claude, or Cursor.
- No remote HTTP MCP server.
- No claim that MCP is memory or source of truth.
- No claim beyond local stdio smoke and package gates.

## Evidence Anchors

| Item | Value |
|------|-------|
| Base HEAD before cut | `b7576e9` |
| Package version | `0.2.9` |
| MCP script SHA-256 | `32750dac5616d748e9c0b9ffd200747108d717900e89aba9a38dff54271f2593` |
| MCP contract SHA-256 | `67444d8ba72f9b9958aa75338687dd1c4c5298c5dbd3e25f0d2dae058104c8a2` |

## Commands

```bash
python3 scripts/cortex_mcp.py --self-test
python3 scripts/validate_tds.py
python3 scripts/validate_reference_package.py
python3 scripts/materialize_adapter.py all --check
```

## Observed Results

| Command | Result |
|---------|--------|
| `python3 scripts/cortex_mcp.py --self-test` | `PASS` |
| `python3 scripts/validate_tds.py` | `PASS` |
| `python3 scripts/validate_reference_package.py` | `PASS` |
| `python3 scripts/materialize_adapter.py all --check` | `PASS` |

## Smoke Shape

The MCP self-test creates a temporary Cortex fixture, rebuilds recall, and
invokes:

- `initialize`
- `tools/list`
- `tools/call` for `cortex_verify`
- `tools/call` for `cortex_recall`
- `tools/call` for `cortex_read_cell`
- `tools/call` for `cortex_absorb_plan`

The test fails if the tool list diverges, if any read-only call returns an MCP
tool error, or if `cortex_read_cell` does not return the fixture cell text.
