---
tds_id: evidence.cortex_mcp_governed_remember_default_20260527
tds_class: evidence
status: active
consumer: Cortex maintainers, MCP adapter authors, installer authors, release reviewers, and operators
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# Cortex MCP Governed Remember Default

Date: 2026-05-27.

## Summary

TES changes the ADR 0002 MCP runtime posture from opt-in governed remember to
default governed remember. This is not automatic memory capture and not broad
write authority. The MCP server exposes only the governed
`cortex_remember_plan` and `cortex_remember` write lane, and `cortex_remember`
still writes one new grounded cell only after the exact approval phrase from
the matching plan is supplied.

Operators can explicitly hide the governed remember tools with `--read-only`.
The legacy `--enable-writes` flag remains accepted for compatibility but is no
longer required by generated project-scoped MCP configuration.

## Implemented

| Area | Result |
|------|--------|
| MCP default | `scripts/cortex_mcp.py` exposes governed remember tools by default. |
| Read-only opt-out | `cortex_mcp.py --read-only` and `install_mcp.py --read-only` hide governed remember tools. |
| Compatibility | `--enable-writes` remains accepted and conflicts with `--read-only`/`--disable-writes`. |
| Installer | `scripts/install_mcp.py` generates default MCP config without `--enable-writes`; read-only installs append `--read-only`. |
| Oracle | `scripts/cortex_mcp.py --self-test` verifies default tools, read-only hiding, approval mismatch refusal, approved write, duplicate refusal, and target override rejection. |
| Operator boundary | `scripts/cortex_operator_oracle.py --self-test` verifies default governed MCP surface and unsafe tool absence. |

## Evidence

Focused gates observed during implementation:

```text
python3 -m py_compile scripts/cortex_mcp.py scripts/install_mcp.py scripts/cortex_operator_oracle.py
python3 scripts/cortex_mcp.py --self-test
python3 scripts/cortex_operator_oracle.py --self-test
python3 scripts/install_mcp.py --self-test
python3 scripts/public_bundle_oracle.py
python3 scripts/build_public_docs.py --check
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
python3 scripts/private_vocabulary_oracle.py
python3 scripts/validate_reference_package.py
python3 scripts/materialize_adapter.py all --check
git diff --check
```

All listed gates passed at this checkpoint.

The stdio E2E smoke showed default MCP exposes 14 tools including
`cortex_remember_plan` and `cortex_remember`; `--read-only` exposes 12 tools
and hides both governed remember tools.

Local bundle identity:

```text
version: 0.3.140
bundle: docs/dist/0.3.140/tilly-engineer-skills-0.3.140.zip
sha256: 1f2bccf5858be2145c7520986f74139d415ccffd75061fd636bf68960c5ec958
```

## Boundaries

- No automatic Cortex writes.
- No update, delete, bulk delete, entity delete, checkpoint write, or direct MCP
  `apply`.
- No external memory backend, hosted service, graph store, UI, or runtime
  surface beyond the native TES MCP scripts.
- No global MCP configuration mutation.
- No remote tag, push, package publish, marketplace action, or commercial-use
  certification.

## Release Identity

This is delivered runtime, installer, adapter-skill, and public documentation
behavior. It requires patch release identity `0.3.140` plus regenerated local
bundle metadata before sealed local closure.
