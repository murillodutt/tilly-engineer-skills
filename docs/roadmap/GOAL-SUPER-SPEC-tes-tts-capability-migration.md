---
tds_id: roadmap.goal_super_spec_tes_tts_capability_migration
tds_class: roadmap
status: active
consumer: maintainers, tes-tts maintainers, adapter authors, and validation authors
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: TES TTS Capability Migration

Status: active execution contract after ADR 0004 acceptance.

Canonical artifact:
`docs/roadmap/GOAL-SUPER-SPEC-tes-tts-capability-migration.md`

ADR boundary:
`docs/adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md`

## Purpose

Migrate portable, already-mapped capabilities into `tes-tts` in small certified
cuts while preserving the accepted ADR boundary.

## Development Target

During capability migration, the active development and test workbench is:

`/Users/murillo/Dev/tilly-engineer-skills/.agents/skills/tes-tts`

The canonical adapter target remains:

`/Users/murillo/Dev/tilly-engineer-skills/src/adapters/codex/skills/tes-tts`

Develop first in `.agents/skills/tes-tts`, validate the local runtime skill,
and mirror the converged content into `src/adapters/codex/skills/tes-tts` only
after the current unit passes its focused checks. The workbench is not a
second source of truth; it is the execution surface used to evolve and test the
skill before canonical synchronization.

## Migration Rule

Use existing simple TTS and `speak` learning as reference material, not as
source to copy wholesale. A capability may move into `tes-tts` only when it is:

- reactive and user-requested;
- dependency-free or optional-provider guarded;
- covered by focused fixtures or an oracle;
- first validated in `.agents/skills/tes-tts`;
- mirrored to `src/adapters/codex/skills/tes-tts` after convergence;
- mirrored across Claude adapter skill source when behavior changes and parity
  is required for the package cut;
- honest about degraded, deferred, or unavailable states.

## Candidate Units

| Unit | Focus | Boundary |
|------|-------|----------|
| CAP-001 | Portable capability inventory and first migration cut | No provider installs, no global config, no proactive behavior. |
| CAP-002 | Speech transformation hardening | Preserve user text; no summary unless requested. |
| CAP-003 | Pronunciation hints and protected terms | Technical terms stay semantic-original. |
| CAP-004 | Optional provider fallback catalog use | Catalog/reference only until probes certify runtime. |
| CAP-005 | Adapter parity and final local audit | No sync or release unless separately authorized. |

## Required Loop

```text
execute -> analyze -> fix -> certify -> create next /goal prompt or close
convergence -> local commit
```

Each non-closed unit must update `docs/roadmap/TES-TTS-SKILL-ROADMAP.md` and
create the next ready prompt artifact before local commit.

## Forbidden

- sync, release, push, tag, publish;
- version bump or bundle generation;
- provider install, provider download, or provider certification;
- proactive `speak` behavior;
- global config writes or durable conversion cache;
- user-text summary unless explicitly requested;
- unrelated `.agents/**` changes.

## Ready Prompt

`docs/roadmap/GOAL-PROMPT-tes-tts-CAP-004-provider-fallback-catalog-use.md`
