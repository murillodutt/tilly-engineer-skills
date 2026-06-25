---
tds_id: evidence.context_mesh.cortex_cli_v2_controlled_apply_2026_05_06
tds_class: evidence
status: active
consumer: Cortex maintainers, installer authors, and certification reviewers
source_of_truth: false
evidence_level: L3
---

# Cortex CLI V2 Controlled Apply Report

This report records the Cortex CLI v2 cut on May 6, 2026.

## Decision

Result: `GO` for controlled CLI promotion.

Certified scope:

```text
commands: read-cell, learn, apply
learn writes: none
apply authorization: --yes required
apply writes: cells/**, MAP.md, LINKS.md, TRAIL.md, derived recall rebuild
source writes: none
```

## Non-Claims

- No automatic LLM promotion.
- No MCP write tools.
- No write access to `sources/**`.
- No Obsidian configuration writes.
- No semantic guarantee that a reviewer-approved claim is true beyond the explicit evidence provided to the cell.

## Evidence Anchors

| Item | Value |
|------|-------|
| Base HEAD before cut | `ddaa098` |
| Package version | `0.3.0` |
| Cortex script SHA-256 | `dc681da3dddc5a1638dca199e125bd9f833fba961a2de8169cf80cea5326c705` |
| Cortex contract SHA-256 | `cd6dd2ea7d5e4ae7e1eb15a6754f198b183c3a7be59462088d60c208ef22422f` |

## Commands

```bash
python3 scripts/cortex.py --self-test
python3 scripts/cortex_mcp.py --self-test
python3 scripts/validate_tds.py
python3 scripts/validate_reference_package.py
python3 scripts/materialize_adapter.py all --check
```

## Observed Results

| Command | Result |
|---------|--------|
| `python3 scripts/cortex.py --self-test` | `PASS` |
| `python3 scripts/cortex_mcp.py --self-test` | `PASS` |
| `python3 scripts/validate_tds.py` | `PASS` |
| `python3 scripts/validate_reference_package.py` | `PASS` |
| `python3 scripts/materialize_adapter.py all --check` | `PASS` |

## Self-Test Coverage

The Cortex self-test now verifies:

- `learn` returns a proposal with `writes: []`.
- `apply` without `--yes` returns `NEEDS_AUTH` and `writes: []`.
- authorized `apply` writes a grounded cell plus `MAP.md`, `LINKS.md`, and `TRAIL.md`.
- authorized `apply` runs `audit` and `rebuild` before returning `PASS`.
- `read-cell` reads the applied cell directly from `cells/**`.
- existing v1 gates remain active: recursive cell audit, broken wikilink failure, loose cell failure, SQLite rebuild, and `rg` fallback.
