---
tds_id: evidence.cortex_reflect_slug_hygiene_20260527
tds_class: evidence
status: active
consumer: Cortex maintainers, adapter maintainers, release reviewers, and operators
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# Cortex Reflect Slug Hygiene Report

This report records the local package-source implementation of Cortex reflection proposal slug hygiene on 2026-05-27.

## Claim

TES `0.3.138` keeps `reflect` proposal-only and no-write while preventing long closure notes from becoming full Cortex cell filenames.

Implemented behavior:

- `reflect` caps proposed cell slugs at a bounded length.
- Capped slugs retain deterministic identity with a short hash.
- Proposal payloads include `cell_name_reason`.
- Long-note proposals ask operators to prefer a short claim-specific cell name before authorized `apply --yes`.

## Material Surfaces

| Surface | Path |
|---------|------|
| Cortex runtime and fixture | `scripts/cortex.py` |
| Cortex operator docs | `docs/mesh/CORTEX.md` |
| Current evidence claim | `docs/evidence/current/CLAIMS.md` |

## Release Identity

Package version: `0.3.138`.

Bundle: `docs/dist/0.3.138/tilly-engineer-skills-0.3.138.zip`.

Bundle SHA-256: `f4afd5f74b8333bb026fcc6bb6ca9feca278433845c7ff55e10e2c77e8b4f6c0`.

Remote tag, push, marketplace, cloud, package publish, and commercial-use claims remain outside this run.

## Closure Oracles

Focused gates:

```bash
python3 scripts/cortex.py --self-test
python3 scripts/tes_bump.py --governance-check --json
```

Baseline gates still required before final package closure:

```bash
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
python3 scripts/private_vocabulary_oracle.py
git diff --check
npm run commit:check
```

Observed status: focused Cortex, version, bundle, docs, TDS, reference graph, doc-size, private vocabulary, command-trigger, diff gates, and `npm run commit:check` passed during this run on the final staged snapshot.

## Boundary

The installed-target canary that exposed the long slug is private evidence, not TES source. This report does not include private project names, paths, commits, commands, product vocabulary, or target-owned decisions.

## Residual Risk

- The generated proposal name is a safe suggestion, not the final cell name.
- Operators still decide whether any reflection claim deserves durable Cortex promotion.
- This does not change `apply`, MCP write boundaries, or automatic memory write policy.

## Decision

Status: `GO` for local package-source implementation on the final staged snapshot.
