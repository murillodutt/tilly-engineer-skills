---
tds_id: evidence.context_mesh.install_smoke_2026_05_06
tds_class: evidence
status: active
consumer: installer authors, adapter maintainers, and certification reviewers
source_of_truth: false
evidence_level: L3
---

# Install Smoke Oracle - 2026-05-06

## Decision

The assisted installer routes now have a deterministic local smoke oracle. It probes temporary projects for `current`, `codex`, `claude`, `cursor`, `all`, `mcp`, and `audit`.

## Oracle

```bash
python3 scripts/install_smoke.py --self-test
```

The probe verifies adapter materialization, Cortex initialization, MCP helper installation, MCP self-test execution, and Cortex `verify`, `audit`, and `rebuild` gates where the route writes files. The `audit` route is dry-run only and fails if it mutates the target.

## Evidence Class

This is local installer evidence. It proves the package can create expected filesystem artifacts in clean temporary projects. It does not prove marketplace distribution, global IDE config, or interactive runtime UI behavior.
