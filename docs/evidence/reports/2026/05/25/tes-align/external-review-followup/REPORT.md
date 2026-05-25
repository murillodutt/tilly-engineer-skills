---
tds_id: evidence.tes_align_external_review_followup_20260525
tds_class: evidence
status: active
consumer: TES maintainers, adapter authors, and certification reviewers
source_of_truth: false
evidence_level: L2
---

# TES Align External Review Follow-up — Certification Packet

Date: 2026-05-25
Run id: tes-align/external-review-followup
Domain: tes-align
Retention status: retained
Prior packet: `docs/evidence/reports/2026/05/25/tes-align/semantic-drift-hardening/REPORT.md`

## Mission

Close the three review items raised against the initial semantic drift
hardening release (0.3.124) and adopt a single-current-dist repository
policy in the same wave.

## Review Items Closed

### 1. `residue.malformed_contract` as a structured finding

Before: when `docs/agents/contracts/SEMANTIC-RESIDUE.yml` existed but was
malformed (invalid YAML, wrong top-level type, missing PyYAML), the oracle
correctly set `status: FAIL` and listed the error in `failures[]`, but the
`semantic_residue` block remained `applied: false / findings: []`.
Consumers parsing the JSON contract had to fall back to prose lines.

After: a new `ResidueContractError` carries the contract path, and
`analyze()` promotes it to a structured finding inside
`semantic_residue.findings` with `code: residue.malformed_contract`,
`severity: fail`, `path` set to the contract file, and `reason` populated.
`semantic_residue.status` becomes `FAIL` and `applied` becomes `true`. The
free-text failure line in `failures[]` is preserved so existing CLI users
are not broken.

Regression fixture: `tes-align-residue-broken-yaml-` in
`scripts/project_alignment_oracle.py::self_test`. Writes a contract with
`entries: [this is: not valid yaml at all`, runs `analyze`, and asserts
the structured shape end-to-end.

### 2. Freshness stopword list

Before: the freshness heuristic flagged generic ADR section headings such
as `Consequences`, `Deeper`, `Rationale`, `Alternatives`, and `Background`
as "tokens absent from the active mesh". This produced operational noise
on every ADR that used standard scaffolding.

After: `FRESHNESS_STOPWORDS` declares a small internal set of documentary
words and is consulted by `freshness_reconciliation`. The heuristic
remains advisory — it never lowers status to `FAIL` — but it no longer
reports documentary scaffolding. The stopword list is intentionally small;
the goal is to drop noise, not to silence genuine successor terms.

Regression fixture: `tes-align-freshness-stopwords-` in
`scripts/project_alignment_oracle.py::self_test`. Writes an ADR composed
entirely of generic headings (`Status`, `Context`, `Decision`,
`Consequences`, `Rationale`, `Alternatives`) and asserts the freshness
notes do not mention any of them.

### 3. Single-current-dist repository policy

Before: every published version left a `docs/dist/<version>/` directory in
the working tree. The repository had accumulated 50 historical bundles
(`0.3.71` through `0.3.123`) plus the current one. The review flagged
those as out-of-scope deletions during the 0.3.124 release prep.

After: `prune_historical_dist(out_dir)` runs at the end of
`tes_bundle.publish_public_bundle()`. After every publish, `docs/dist/`
contains exactly one directory: the current version. Historical bundles
remain reachable via Git tags (`git checkout v<X> -- docs/dist/<X>`) and
via the GitHub release surface.

Regression fixture: `tes-bundle-prune-` in
`scripts/tes_bundle.py::self_test`. Seeds a synthetic `docs/dist/` with
five peer version directories, calls `prune_historical_dist`, and asserts
only the current version survives and the report lists the removed peers.

Repository sweep: 50 `docs/dist/0.3.<NN>/` directories (versions 71–112,
114–123) removed via `git rm -rq`. After the sweep, `docs/dist/` contains
`0.3.124/` only. Historical bundles remain available through Git tags
`v0.3.71`..`v0.3.123` and through release URLs already published on
GitHub Pages prior to the prune.

## Governance Surfaces Updated

| Surface | Change |
|---------|--------|
| `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` | Documents the structured `residue.malformed_contract` finding and the freshness stopword list. |
| `docs/governance/SYNC-AUDIT-CHECKLIST.md` | New retention step and matching lock requiring exactly one `docs/dist/<version>/` in the repository. |
| `scripts/project_alignment_oracle.py` | `ResidueContractError`, structured malformed contract finding, `FRESHNESS_STOPWORDS`, two new fixtures (totaling 13 fixtures). |
| `scripts/tes_bundle.py` | `prune_historical_dist` helper, publish flow integration, new fixture. |
| `docs/evidence/current/CLAIMS.md` | Will be updated with this packet path when the 0.3.125 release closes. |

## Acceptance Gates

| Gate | Result |
|------|--------|
| `python3 scripts/project_alignment_oracle.py --self-test` | PASS (13 fixtures) |
| `python3 scripts/tes_bundle.py --self-test` | PASS (includes prune fixture) |
| `npm run commit:check` | PASS end-to-end |
| `python3 scripts/tes_bump.py --governance-check` | (run during 0.3.125 release; see prior section) |
| `npm run release:check` | (run after tag push; see prior section) |

## Limits And Remaining Risks

- The single-current-dist policy is enforced on publish. If a maintainer
  hand-creates `docs/dist/<other>/` outside the publish flow, the next
  publish prunes it. The lock in `SYNC-AUDIT-CHECKLIST.md` blocks the
  inverse path (re-adding a historical bundle to `main`).
- Freshness stopwords are an internal heuristic, not a contract. If a
  target project's vocabulary collides with one of them, the project can
  always pin the concern through a `pattern` entry in
  `SEMANTIC-RESIDUE.yml` instead of relying on freshness alone.
- The structured malformed-contract finding uses `line: 0` because a
  top-level YAML error does not have a meaningful line number from PyYAML
  in every case. Where PyYAML returns line context, it is included inside
  the `reason` string.

## Final Claim

```text
TES Align external review follow-up: PASS.
```

All three review items closed in package source. Regression fixtures added.
Repository swept to single-current-dist. Bump 0.3.124 → 0.3.125 publishes
the wave under the new policy.
