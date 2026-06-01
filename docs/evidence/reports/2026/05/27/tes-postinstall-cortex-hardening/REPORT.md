---
tds_id: evidence.tes_postinstall_cortex_hardening_20260527
tds_class: evidence
status: active
consumer: TES maintainers, installer authors, Cortex maintainers, adapter maintainers, and release reviewers
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# TES Postinstall And Cortex Curation Hardening Report

This report records the local package-source implementation of TES
postinstall recovery and Cortex curation hardening on 2026-05-27.

## Claim

TES `0.3.137` implements two portable corrections:

- `tes_install.py postinstall --recover-needs-review` reruns Project-Start only
  when `.tes/postinstall.json` is `needs_review`, records the recovery run, and
  clears the sentinel only on PASS.
- `cortex.py curate-plan` treats evidence-heavy Cortex cells as healthy when
  the claim remains narrow, while still flagging swollen claim cells through
  compound split pressure.

## Material Surfaces

| Surface | Path |
|---------|------|
| Postinstall runtime | `scripts/tes_install.py` |
| Cortex curation runtime | `scripts/cortex.py` |
| Command parity oracle | `scripts/command_trigger_oracle.py` |
| Init/setup adapter routers | `src/adapters/**/skills/tes-{init,setup}/SKILL.md` |
| Runtime bootloader/rule routers | `src/adapters/codex/AGENTS.md`, `src/adapters/claude/CLAUDE.md`, `src/adapters/cursor/rules/**` |
| Installer docs | `docs/install/**` |
| Cortex docs | `docs/mesh/CORTEX.md` |
| Planning artifact | `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-postinstall-cortex-hardening.md` |

## Release Identity

Package version: `0.3.137`.

Bundle: `docs/dist/0.3.137/tilly-engineer-skills-0.3.137.zip`.

Bundle SHA-256:
`39dfff625a3ee3e468c52ee843c7870d57e0b0920b76b3cf85d9a031b4922130`.

Remote tag, push, marketplace, cloud, package publish, and commercial-use
claims remain outside this run.

## Closure Oracles

Focused gates:

```bash
python3 scripts/tes_install.py --self-test
python3 scripts/cortex.py --self-test
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/tes_bump.py --governance-check --json
python3 scripts/public_bundle_oracle.py
python3 scripts/build_public_docs.py --check
python3 scripts/private_vocabulary_oracle.py
python3 scripts/validate_reference_graph.py
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
git diff --check
```

Observed status: all listed focused gates passed during this run after the
version index was synchronized to `0.3.137`.

`npm run commit:check` passed after staging this package-source implementation.

## Boundary

The private installed-target dossier that triggered this hardening is not TES
source. This report does not include private project names, paths, commits,
commands, product vocabulary, or target-owned decisions.

## Residual Risk

- `--recover-needs-review` reruns the deterministic Project-Start helpers; it
  does not repair arbitrary target project quality gates.
- The curation heuristic remains deterministic and lexical-first; it does not
  replace operator review of actual split candidates.
- Remote release certification is deferred until an authorized tag or fixed ref
  and `npm run release:check`.

## Decision

Status: `GO` for local package-source implementation and `0.3.137` bundle
metadata.

Status: `DEFERRED` for remote tag/ref certification, marketplace action,
package publishing, cloud action, and commercial-use claims.
