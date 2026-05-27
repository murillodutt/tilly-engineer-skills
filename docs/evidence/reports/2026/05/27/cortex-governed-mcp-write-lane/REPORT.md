---
tds_id: evidence.cortex_governed_mcp_write_lane_20260527
tds_class: evidence
status: active
consumer: Cortex maintainers, MCP adapter authors, installer authors, release reviewers, and operators
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# Cortex Governed MCP Write Lane

Date: 2026-05-27.

## Summary

TES adds ADR 0002 and implements a governed MCP write lane for Cortex. The
default MCP server remains read-only. Write-capable MCP tools are exposed only
when the server starts with `--enable-writes`, and the only durable-memory write
tool is `cortex_remember`.

The external memory MCP shape was used only as a portability study. TES keeps
Markdown under `docs/agents/cortex/**` as durable memory truth and does not add
an external backend, hosted MCP, graph store, update/delete/bulk/entity tools,
or automatic Cortex writes.

## Implemented

| Area | Result |
|------|--------|
| Architecture | `docs/adr/0002-cortex-governed-mcp-write-lane.md` records the decision. |
| MCP default | `scripts/cortex_mcp.py` stays read-only unless started with `--enable-writes`. |
| Governed write | `cortex_remember_plan` validates without writes and returns an approval phrase tied to the exact payload. |
| Durable write | `cortex_remember` writes one new cell only after exact approval phrase match. |
| Event inspection | `cortex_list_events` and `cortex_get_event_status` expose sanitized event evidence without writes. |
| Installer | `scripts/install_mcp.py --enable-writes` materializes the opt-in server arg; default install remains read-only. |
| Oracle | MCP self-test covers disabled-write blocking, bad approval refusal, approved write, duplicate refusal, event tools, target override rejection, and unsafe tool absence. |

## Evidence

Focused gates run during implementation:

```text
python3 scripts/cortex_mcp.py --self-test
python3 scripts/cortex_operator_oracle.py --self-test
python3 scripts/event_ledger.py --self-test
python3 scripts/install_mcp.py --self-test
python3 -m py_compile scripts/install_mcp.py scripts/cortex_mcp.py scripts/cortex_operator_oracle.py
python3 scripts/materialize_adapter.py all --check
```

All listed focused gates passed before this report was written.

## Boundaries

- No external memory backend.
- No hosted MCP dependency.
- No update, delete, bulk delete, or entity delete tool.
- No MCP checkpoint write.
- No direct MCP `apply`.
- No automatic Cortex writes from reflection, event ledger, checkpoints, or LLM
  output.
- No package publish, marketplace action, remote tag, push, or commercial-use
  certification.

## Release Identity

This is delivered runtime, installer, adapter-skill, and public documentation
behavior. It requires a patch release identity decision. The local package
source should move from `0.3.138` to `0.3.139` before sealed closure.
