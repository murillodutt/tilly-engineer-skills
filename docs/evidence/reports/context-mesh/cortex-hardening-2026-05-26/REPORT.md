---
tds_id: evidence.context_mesh.cortex_hardening_2026_05_26
tds_class: evidence
status: active
consumer: Cortex maintainers, MCP reviewers, and certification reviewers
source_of_truth: false
evidence_level: L3
tver: 0.1.0
---

# Cortex Hardening Report

This report closes the Cortex hardening sequence from `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-hardening.md`.

## Claim

The three accepted Cortex findings were resolved in sequence:

1. Cortex MCP no longer accepts caller-provided `target` overrides.
2. MCP helper documentation now matches the installer helper inventory.
3. `reflect` now counts durable untracked text line volume toward curation.

No release, publish, marketplace, or target-project mirror action was performed. Remote sync to `origin/main` was performed only after the local package gate passed and the Mantra Gate adoption oracle accepted the push.

## Material Trail

| Unit | Commit | Result |
|------|--------|--------|
| Baseline planning artifact | `9a0f4772` | Super SPEC and roadmap/TDS indexes materialized |
| `SPEC-001` | `a5449f54` | MCP project scope enforced and negative cross-project fixture added |
| `SPEC-002` | `688369c2` | MCP helper inventory aligned with `scripts/install_mcp.py` |
| `SPEC-003` | `8209551a` | Durable untracked line counting added to `reflect` |
| `SPEC-004` | final closeout commit | Full gate certification and closeout evidence |

## Focused Evidence

Focused Cortex gates passed after material changes:

- `python3 scripts/cortex.py --self-test`
- `python3 scripts/cortex_quality_oracle.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`
- `python3 scripts/install_mcp.py --self-test`

Documentation and package evidence gates passed:

- `python3 scripts/validate_tds.py`
- `python3 scripts/validate_reference_graph.py`
- `python3 scripts/validate_doc_size.py`
- `git diff --check`

`npm run commit:check` initially reached the private vocabulary stage and then failed because `scripts/private_vocabulary_oracle.py` scanned ignored local scratch under `tmp/**`. That contradicted its tracked-content contract, so the closeout repaired the oracle to scan `git ls-files` when a Git worktree is available and added regression coverage for ignored scratch versus tracked source leakage.

## Negative Checks

The project-scope MCP fix added two guards:

- tool schemas must not expose a `target` property;
- each read-only Cortex MCP tool rejects a second project's `target` override.

The helper inventory was checked by comparing `SERVER_FILES` in `scripts/install_mcp.py` with the `.tes/bin/**` list in `docs/mesh/CORTEX-MCP.md`; parity was true.

The `reflect` fixture now proves:

- a durable untracked text file under `docs/**` triggers `curation_due`;
- ignored local scratch does not contribute to changed-line count.

Negative grep results containing placeholder terms, legacy `.tilly/bin` vocabulary, `push`, `publish`, `marketplace`, or `write-capable` were reviewed as policy, migration, test, or forbidden-action text. No new forbidden runtime behavior was introduced by this sequence.

## Closeout Status

Status: `GO`. The closeout commits record this report, the private-vocabulary gate repair, and the post-commit certification replay. Remote sync is limited to non-force `git push origin HEAD:main` after `npm run commit:check` passes.
