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
  limits:
```

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

## Roadmap Lanes

`PROJECT-ROADMAP.md` must separate:

- Done
- Active
- Next
- Later
- Deferred
- Blocked
- Unknown

Do not ask future agents to rebuild what the project already has.

## Obsidian Hygiene

Use Markdown, YAML frontmatter, and wikilinks. Do not write `.obsidian/**`.
Optional `.base` or `.canvas` views may be proposed only when every claim still
resolves back to Markdown.
