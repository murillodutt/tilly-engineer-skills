---
tds_id: evidence.report.tes_sync_0_3_224
tds_class: evidence
status: active
consumer: maintainers, release reviewers, hook-audit operators, and public-doc reviewers
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# TES Sync 0.3.224 Certification Packet

Date: 2026-06-27.

Scope: bump + bundle + public refs.

Reason: the sync payload closes the post-canary public-documentation alignment
and advances the package identity after local commits that clarified the
PreToolUse ceiling contract, public hook-evidence wording, and Codex hook
configuration troubleshooting. The release identity advances from `0.3.223` to
`0.3.224`.

## Identity

- Previous source version: `0.3.223`.
- New source version: `0.3.224`.
- Bundle: `docs/dist/0.3.224/tilly-engineer-skills-0.3.224.zip`.
- Bundle SHA-256:
  `093b4c58a95d41f4f85170cd38b1a87d487e9b8864caf1aba8cb220c8ad31d4a`.
- Single-current-dist policy: `docs/dist/0.3.223/**` pruned by the bundle
  publisher.

## Included Delta

- Public landing and user manual now align with the hook canary finding that
  host evidence is per-host: one host never proves another host by accident.
- The user manual troubleshooting path documents the Codex stale
  `.codex/hooks.json` residue case and preserves `.codex/config.toml` as the
  Codex hook source.
- `docs/i18n/tes-public.structure.yml` points at the current `0.3.224` bundle
  index and SHA-256.
- ADR 0009 no longer pins the recent canary note to the previous patch version.
- Version identity surfaces, plugin manifests, script constants, public refs,
  i18n sources, and generated HTML were synchronized to `0.3.224`.

## Local Certification

Passed before sync commit:

- `python3 scripts/tes_bump.py --governance-check`;
- `python3 scripts/tes_bump.py patch --dry-run --json`;
- `python3 scripts/tes_bump.py patch --yes --json`;
- `python3 scripts/tes_bundle.py publish --adapter all`;
- `python3 scripts/build_public_docs.py`;
- `python3 scripts/build_public_docs.py --check`;
- `python3 scripts/public_bundle_oracle.py`;
- `python3 scripts/validate_reference_package.py --staged-ready`;
- `python3 scripts/validate_tds.py`;
- `python3 scripts/validate_doc_size.py`;
- `npm run commit:check`.

## Boundaries

- No force push.
- No tag move.
- No package-registry publish.
- No marketplace action.
- No secret-bearing operation.
- Remote push, annotated tag, `npm run release:check`, and public Pages
  certification are part of the remaining sync phases after this local commit.
