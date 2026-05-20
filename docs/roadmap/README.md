---
tds_id: roadmap.index
tds_class: roadmap
status: active
consumer: maintainers, release reviewers, and next-loop operators
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# Roadmap Index

This folder preserves roadmap lineage. Older v1 planning documents remain
auditable, but the active planning surface now starts from the Wave 6 release
readiness baseline.

## Current Line

| Line | Status | Document |
|------|--------|----------|
| RC1 readiness cleanup | Active | `RC1-READINESS-ROADMAP.md` |
| V1 convergence lineage | Historical | `V1-CONVERGENCE-LOOP.md` |
| V1 goal checklist | Historical | `V1-GOAL-CHECKLIST.md` |
| 2026-05-05 continuity letter | Historical | `NEXT-STEPS-LETTER-2026-05-05.md` |
| Senior mentorship context | Historical | `SENIOR-MENTORSHIP-CONTEXT-2026-05-05.md` |

## Baseline

The current release-readiness baseline is TES `0.3.119`, after the GitHub-only
npx installer line, interactive installer screen, Node/Bun runtime matrix,
first-session hooks, and fixed release documentation alignment.

The next work is not to create a release. The next work is to remove obvious
pre-RC1 friction:

- documentation freshness;
- root structure clarity;
- GitHub community and security documents;
- GitHub Pages landing;
- no overclaim against deferred or partial surfaces.

## Operating Rule

Roadmap updates must classify their status clearly:

| Status | Meaning |
|--------|---------|
| Active | Current planning authority |
| Historical | Retained for lineage, not the next execution source |
| Deferred | Intentionally postponed with reason |
| Complete | Closed by evidence or replaced by a newer source |

Do not delete old roadmap documents merely because they are outdated. Add a
new active document and make the lineage explicit.
