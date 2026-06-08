# TES Align Procedure

Use this reference only after the `tes-align` skill is selected.

## Alignment Packet

Create or update a retained evidence packet with:

```yaml
alignment_evidence:
  target:
  tes_version:
  anchors_read:
  existing_docs_classification:
  created_or_updated:
  contradictions:
  quality_gates_discovered:
  roadmap_changes:
  obsidian_native_checks:
  oracle_result:
  retention_status: retained
  limits:
```

This packet is target-project alignment evidence and stays under
`docs/agents/evidence/**`. Do not redirect it to the TES source-package
benchmark evidence layers under `docs/evidence/**`.

## Document Classification

Before writing, classify each expected surface:

| Status | Action |
|--------|--------|
| `present` | Preserve and link. |
| `linked_existing` | Reference the existing source from `docs/agents/**`. |
| `created` | Create the minimal useful file. |
| `needs_update` | Patch with evidence and keep contradictions visible. |
| `contradictory` | Record the tension and current interpretation. |
| `deferred` | Record future work with reason. |
| `not_applicable` | Record why the surface does not fit. |

## System X-Ray, Convergence Line, And Roadmap Lanes

`PROJECT-ROADMAP.md` must open with two Mermaid `flowchart TD` graphs. The
System X-Ray shows Git state, delivered behavior, validation mesh, and release
boundary. The Convergence Line shows done/current/next work, later/deferred
branches, blocked branches, unknowns, and the final gate when one exists.

After the graphs, `PROJECT-ROADMAP.md` must separate:

- Done
- Active
- Next
- Later
- Deferred
- Blocked
- Unknown

Do not ask future agents to rebuild what the project already has. Do not
replace the System X-Ray and Convergence Line with only a textual roadmap.

## Obsidian Hygiene

Use Markdown, YAML frontmatter, and wikilinks. Do not write `.obsidian/**`.
Optional `.base` or `.canvas` views may be proposed only when every claim still
resolves back to Markdown.

## Semantic Residue Gate

Structural alignment proves the mesh shape exists. Semantic alignment must also
prove the mesh tells the current project truth.

The Semantic Residue Gate is a portable mechanism owned by TES; the vocabulary
is owned by the target project. Each project may declare a contract at
`docs/agents/contracts/SEMANTIC-RESIDUE.yml`:

```yaml
version: 1
defaults:
  severity: needs_review
  scope: [docs/agents/**]
  exclude:
    - docs/agents/evidence/**
    - docs/agents/contracts/**
entries:
  - id: example-retired-term
    term: "<retired literal>"           # word-boundary match
    severity: fail                       # fail | needs_review | warn
    reason: "Replaced by <successor> per ADR-NNNN."
    successor: "<current vocabulary>"
    allowed_paths:
      - docs/agents/evidence/**
    expires_on: 2026-12-31                # optional review date
```

Use `term` for literal vocabulary and `pattern` for regex-driven claim
detection. The oracle matches literals with explicit word boundaries so
a short literal does not falsely flag an unrelated longer word that contains
it as a substring. Historical evidence keeps retired
language only when listed under `allowed_paths`. Severity `fail` lowers the
overall oracle status to `FAIL`; `needs_review` lowers it to `NEEDS_REVIEW`;
`warn` records the finding without lowering status.

Run the gate before reporting PASS. When the gate fires, report the exact
path, line, and matched literal in the retained evidence packet.

## Documentation Authority Tiers

When the target project declares `docs/agents/DOCUMENTATION-AUTHORITY.md`, treat
it as the adjudication ladder for all alignment work:

```text
Tier 0 — runtime proof (code, tests, oracles)
Tier 1 — product truth (README, docs/roadmap.md, docs/decisions/**)
Tier 2 — agent operating line (EXECUTION-LINE, PROJECT-STATE, PROJECT-ROADMAP, gates, boundaries)
Tier 3 — derived contracts + init inventory (contracts/**, PROJECT-CONTEXT after align)
Tier 4 — archive (evidence/**, realign/**, retired methodology)
```

Alignment workflow:

1. Reconcile Tier 1 against Tier 0 before writing Tier 2.
2. Update Tier 2 mesh (state, roadmap, execution line, gates, boundaries).
3. Mirror Tier 1+2 into Tier 3 contracts; demote `PROJECT-CONTEXT` to inventory.
4. Banner or classify Tier 4 surfaces that compete with Tier 2.
5. Record phase-vocabulary bridges (e.g. Golden Record Done vs Fase 1 NEEDS_REVIEW).

Do not report PASS if Tier 3 contracts contradict Tier 1 or 2.

## Tier 3 Inventory Hygiene

When `docs/agents/contracts/INVENTORY-HYGIENE.yml` exists:

1. Scrub `PROJECT-CONTEXT.md` **Recommended Deep Reads** — no Tier 4 paths
   (`docs/realign/**`, `docs/agent-os-analysis.md`, `.agent-os`).
2. Point deep reads to [[DOCUMENTATION-AUTHORITY]] and [[EXECUTION-LINE]] first.
3. Update the Identity table Git HEAD to match `git rev-parse HEAD`.
4. Keep `tier: 3-inventory` in frontmatter.
5. Run `python3 scripts/verify_documentation_inventory.py --target .` before
   claiming alignment PASS (also enforced inside `project_alignment_oracle.py`).

## Freshness Reconciliation

Before claiming alignment, read:

1. `docs/agents/DOCUMENTATION-AUTHORITY.md` when present.
2. The newest accepted ADRs under `docs/agents/DECISIONS/**` or the linked
   decision system.
3. The newest retained alignment evidence packet under
   `docs/agents/evidence/**`.
4. Tier 2: `PROJECT-STATE.md`, `PROJECT-ROADMAP.md`, `EXECUTION-LINE.md`.
5. Tier 1: `docs/roadmap.md` and relevant `docs/decisions/**`.
6. `PROJECT-CONTEXT.md` only as Tier 3 inventory — not as position authority.

Precedence:

```text
Tier 0 runtime proof
-> Tier 1 product truth (ADRs, roadmap)
-> Tier 2 operating mesh
-> Tier 3 derived contracts and init inventory
-> Tier 4 historical evidence and snapshots
```

When a newer ADR introduces a term absent from the active mesh, mark the
alignment as `NEEDS_REVIEW` and re-read the ADR before reconciling.

## Project-Local Vocabulary Boundary

TES must not learn the private language of every project it aligns. The skill
body and the oracle stay vocabulary-free. The target project declares retired
terms, stale claim patterns, allowed historical paths, and successor language
through the Semantic Residue contract.
