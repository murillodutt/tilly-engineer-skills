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

## Freshness Reconciliation

Before claiming alignment, read:

1. The newest accepted ADRs under `docs/agents/DECISIONS/**` or the linked
   decision system.
2. The newest retained alignment evidence packet under
   `docs/agents/evidence/**`.
3. The current `PROJECT-CONTEXT.md`, `PROJECT-STATE.md`, `PROJECT-ROADMAP.md`,
   and `EXECUTION-LINE.md`.

Precedence:

```text
accepted ADRs and active decisions
-> current project-state/roadmap/execution mesh
-> latest retained evidence and changelog packets
-> historical evidence and generated inventories
```

When a newer ADR introduces a term absent from the active mesh, mark the
alignment as `NEEDS_REVIEW` and re-read the ADR before reconciling.

## Project-Local Vocabulary Boundary

TES must not learn the private language of every project it aligns. The skill
body and the oracle stay vocabulary-free. The target project declares retired
terms, stale claim patterns, allowed historical paths, and successor language
through the Semantic Residue contract.
