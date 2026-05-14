---
tds_id: roadmap.rc1_readiness
tds_class: roadmap
status: active
consumer: maintainers, release reviewers, and documentation operators
source_of_truth: false
evidence_level: L2
tver: 0.1.1
---

# RC1 Readiness Roadmap

This roadmap starts after the Wave 6 `RELEASE_CANDIDATE_READY /
CERTIFIED_REMOTE` result. It does not authorize a tag, release, package
publish, marketplace submission, live GitHub issue, global install, or global
configuration mutation.

## Goal

Prepare the repository for an RC1 decision by making the public-facing package
coherent for a new adopter and auditable for a maintainer.

## Baseline

| Item | Value |
|------|-------|
| Package version | `0.3.86` |
| Latest certified line | Wave 6 release readiness plus `/tes-open-obsidian` gate |
| Release action status | Not taken |
| Release readiness claim | Candidate-ready only, pending user decision |

## Stage 1: Documentation Freshness

Acceptance:

- `docs/roadmap/**` has an active index and current RC1 line.
- Historical roadmap documents are explicitly marked as lineage.
- `docs/INDEX.md` routes readers to current roadmap authority.
- `README.md`, `docs/INDEX.md`, and `docs/install/INSTALL.md` route users to
  both the user manual and the agent manual.
- `docs/tds/DOCS-INDEX.yml` includes every governed Markdown document.
- Rendered HTML entrypoints are treated as public surfaces, not TDS Markdown
  records, and are linked from the user-facing maps.
- Public docs do not claim tag, release, marketplace, publish, live GitHub
  issue creation, vector certification, write-capable MCP, or global install.

## Stage 2: Root Structure

Acceptance:

- Root remains thin and people-friendly.
- Root `install.sh` and `install.ps1` are absent.
- Installer shell entrypoints live under `scripts/bootstrap/**`.
- `docs/architecture/PROJECT-STRUCTURE.md` explains root vs bootstrap
  ownership.
- Package validators certify the bootstrap paths and reject root wrappers.

## Stage 3: GitHub Community Documents

Acceptance:

- `.github/CONTRIBUTING.md` explains contribution flow and required gates.
- `.github/SECURITY.md` explains vulnerability reporting without asking users
  to publish secrets.
- `.github/SUPPORT.md` points adopters to install, troubleshooting, and issue
  routes.
- `.github/CODE_OF_CONDUCT.md` sets collaboration expectations.
- `.github/PULL_REQUEST_TEMPLATE.md` makes release locks visible.
- GitHub automation readiness fails if Dependabot points an ecosystem at a
  directory without matching manifests or workflow files.

## Stage 4: Landing Page

Acceptance:

- `docs/index.html` is a GitHub Pages-ready landing page.
- The live landing at `https://murillodutt.github.io/tilly-engineer-skills/`
  exposes the current package version, install prompt, user manual, agent
  manual, certified/partial/deferred boundaries, and RC1 status.
- The landing page links to install, docs, roadmap, evidence, and safety
  boundaries.
- The page distinguishes certified, partial, deferred, and not-taken release
  actions.
- It stays within the documentation size gate.

## Stage 5: Pre-RC1 Gate

Acceptance:

- `python3 scripts/validate_reference_package.py`
- `python3 scripts/validate_tds.py`
- `python3 scripts/validate_doc_size.py`
- `python3 scripts/github_readiness_oracle.py --self-test`
- bootstrap install entrypoints still resolve;
- `git diff --check`;
- `npm run commit:check` before any RC1 claim.

## Open Before RC1

| Item | Status | Reason |
|------|--------|--------|
| Tag or release | Not authorized | Requires explicit user decision |
| Package publish | Not authorized | Wave 6 certified readiness, not publication |
| Marketplace submission | Deferred | Local plugin/package surfaces only |
| Live GitHub issue publication | Partial | Fake transport and receiver quarantine certified |
| Vector/Xenova behavior | Optional blocked/deferred | Dependency not installed by default |

## Done When

The repository reads like a release candidate package without taking release
actions: a new adopter can understand what TES does, how to install it, what is
certified, what is partial, and how maintainers verify changes.
