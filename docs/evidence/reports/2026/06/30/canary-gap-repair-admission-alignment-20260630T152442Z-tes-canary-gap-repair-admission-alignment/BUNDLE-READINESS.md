---
tds_id: evidence.canary_gap_repair_admission_alignment.bundle_readiness_20260630
tds_class: evidence
status: active
consumer: maintainers, canary operators, release authors
source_of_truth: false
evidence_level: L2
---

# BUNDLE-READINESS — Replay Input Without Canary Install

The package source changed delivered behavior (HELPER_FILES), so per the
owner-confirmed release-identity decision the version was bumped and the local
public bundle refreshed. No install into the real canaries was performed here.

## Release-identity decision (owner-confirmed)

- Bump patch and refresh the local bundle: `0.3.231 -> 0.3.232`.
- No push / tag / publish / cloud action (local-only readiness window).
- The package is NOT release-sealed (no `npm run commit:closure`, no tag, no
  `release:check`); it is package-ready for the later replay session.

## Version bump

- `scripts/tes_bump.py patch --yes` applied `0.3.231 -> 0.3.232` across 70
  surfaces (package.json, README.md, bin/tes.js, docs, i18n content, plugins,
  52 script VERSION constants), all status `updated`.
- `scripts/canary_admission_oracle.py` VERSION set to `0.3.232` manually (it
  postdates the bump config globs).
- `scripts/build_public_docs.py` regenerated `docs/index.html` and
  `docs/install/USER-MANUAL.html` from the bumped i18n content (PASS); both now
  carry `0.3.232` and zero `0.3.231`.

## Refreshed public bundle (0.3.232)

```text
bundle:        docs/dist/0.3.232/tilly-engineer-skills-0.3.232.zip
sha256:        9461e708f5ba1c3b16f6669653581da6dcca37989cf51d2725c4e2f54d9bcf68
sha256 sidecar: matches (verified)
entry_count:   378
pycache:       0  (zero __pycache__/.pyc manifest entries; zero ZIP members)
source_commit: 89e5ea736db60d8f55761f6b68374165c7ec1715
source_tree_state: dirty (uncommitted gap-repair changes present at build time)
pruned:        0.3.231 (previous bundle dir removed by publish)
```

Built with `PYTHONDONTWRITEBYTECODE=1` via `tes_bundle.py publish --adapter all`.

## Bundle readiness oracles (SPEC-008)

```text
public_bundle_oracle.py            PASS   (helper drift reconciled by refresh; bytecode/residue rejection active)
tes_install.py --self-test         PASS
install_smoke.py --self-test       PASS
tes_bundle.py --self-test          PASS   (red-capable bytecode fixture green)
```

## Provenance note for the replay session

The refreshed `0.3.232` bundle is the clean replay input. Its `source_commit`
records HEAD `89e5ea73` with `source_tree_state: dirty` because the gap-repair
edits are not yet committed in this window. The replay session must install from
the bundle that matches the committed package state it runs against; if this
package is committed before replay, regenerate or re-verify the bundle so
`source_commit` and `source_tree_state` reflect the committed tree.
