---
tds_id: evidence.report.tes_sync_0_3_208
tds_class: evidence
status: active
consumer: maintainers, release reviewers, and sync operators
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# TES Sync 0.3.208 Certification Packet

Date: 2026-06-26.

Scope: bump + bundle + public refs.

Reason: the sync payload changes delivered hook behavior, installed helper
assets, public installer refs, and the installed-target hook audit prompt. The
selected route advances the full release identity to `0.3.208`.

## Identity

- Previous source version: `0.3.207`.
- New source version: `0.3.208`.
- Bundle: `docs/dist/0.3.208/tilly-engineer-skills-0.3.208.zip`.
- Bundle SHA-256: `9d3308fefffa8942297a05cfd740cd628ed9d4d082929c7b6c2880548289c500`.
- Single-current-dist policy: `docs/dist/0.3.207/**` pruned by the bundle publisher.

## Hook Test Contract

The installed-target test prompt now requires each host to prove more than
configuration presence:

- native governed smoke on the current host using `SKILL.md`;
- Codex `apply_patch` matcher coverage and path extraction from patch bodies;
- safe simulated forbidden blocks per host;
- routine silence, governed supervision, anti-cry-wolf, and host output
  contract lenses;
- runtime ledger fidelity and Cortex no-write behavior;
- installed Cortex fixture completeness before running `cortex_runtime.py
  --self-test`.

## Local Certification

Passed before commit:

- `python3 scripts/tes_bump.py patch --dry-run --json`
- `python3 scripts/tes_bump.py patch --yes --json`
- `python3 scripts/tes_bundle.py publish --adapter all`
- `python3 scripts/build_public_docs.py`
- `npm run commit:check`
- `python3 scripts/tes_bump.py --governance-check`
- `python3 scripts/mantra_gate_pretooluse_oracle.py --self-test`
- `python3 scripts/mantra_gate_agent_idempotency_oracle.py --self-test`
- `python3 scripts/cortex_runtime.py --self-test`
- `python3 scripts/cortex_host_contract_oracle.py --self-test`

Additional checks:

- generated public HTML contains zero active `0.3.207` references;
- tracked `tes-sync` mirrors validate under `.agents/skills/tes-sync` and
  `.claude/skills/tes-sync`;
- the Codex user-skill install path was absent in this environment, so no
  installed-copy validation was possible there.

## Boundaries

- No force push.
- No tag move.
- No secrets.
- No marketplace, cloud, or package-registry publish.
- Post-commit remote certification still requires `git push origin main`,
  annotated tag `v0.3.208`, `npm run release:check`, and public Pages oracle.
