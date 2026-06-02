---
tds_id: roadmap.goal_super_spec_tes_installed_certification_and_field_reports_hardening
tds_class: roadmap
status: active
consumer: maintainers, installer authors, Field Reports maintainers, adapter maintainers, release reviewers, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Super SPEC: TES Installed Certification And Field Reports Hardening

Status: execution contract derived from ADR 0003.1 for the next TES package
source convergence cut after `0.3.144`.

Capability: make TES installation and update certification truthful at the
installed-target boundary, and make Field Reports GitHub issues actionable
product feedback rather than high-volume event logs.

## Mantra Gate Snapshot

| Field | Decision |
|-------|----------|
| VERIFY | Reviewed GitHub issue #46, a maintainer-local installation audit retained outside TES tracked source, ADR 0003, Field Reports contracts, installer/postinstall behavior, adapter bootloader contracts, and package hygiene evidence. |
| SCOPE | Plan the complete repair wave. No runtime code, version bump, public bundle rebuild, tag, push, publish, marketplace, or cloud action is authorized by this SPEC alone. |
| BEST_PATH | Seal ADR 0003.1 first, then execute a reproducer-led Build-Test-Fail-Fix sequence across installed-target certification, adapter parity, bundle hygiene, and Field Reports intake. |
| DOCUMENT | This Super SPEC plus ADR 0003.1, roadmap/index/TDS correlations, and future evidence reports produced during implementation. |
| ORACLE | Implementation must add or reuse deterministic package-source and installed-target oracles listed below before claiming convergence. |
| RESOLVE | none found |
| STATUS | GO for governed implementation planning. |

## Authority

| Source | Role |
|--------|------|
| ADR 0003 | Active Cortex MCP capability and governed-write contract. |
| ADR 0003.1 | Installed certification and Field Reports feedback-intake decision. |
| GitHub issue #46 | Public sanitized Field Reports signal that exposed partial certification. |
| Maintainer-local installation audit `20260528T120318Z` | Private evidence source retained outside TES tracked docs; use only generic references in package source. |
| Maintainer correlation rule | Determines correlated source, docs, adapter, release, and public surfaces. |
| Platform differences reference | Keeps adapter-specific certification honest without fabricating cross-host symmetry. |
| Field Reports contract | Defines privacy, transport, suppression, and receiver requirements. |

## Problem

TES `0.3.144` can install core runtime and MCP config successfully while still
leaving the active installed project in a partial certification state:

- MCP registration for Codex, Claude Code, and Cursor may pass;
- Cortex self-tests and local verification may pass;
- installed Codex/Claude bootloaders may still fail Mantra Gate routing health;
- installed Codex/Claude command-trigger coverage may lag the source contract;
- generated target docs may reference stale quality-gate paths;
- bundle or manifest surfaces may include operating-system residue;
- bundle metadata may record a dirty source tree;
- Field Reports may open a high-signal issue without enough product-class
  routing to drive the next maintenance action.

The dangerous failure is a false green: `INSTALLED` or postinstall `PASS`
appearing broader than the evidence actually proves.

## Goal

After this goal is implemented, a TES install/update run must produce a truthful
certification state:

```text
core runtime + MCP registration + installed adapter surfaces + trigger parity
+ bundle hygiene + provenance + Field Reports intake classification
= PASS, PARTIAL, NEEDS_REVIEW, or BLOCKED
```

Field Reports must preserve the privacy boundary while emitting enough
classification, dedupe, severity, and next-action metadata for maintainers to
turn real-project signals into TES product fixes.

## Non-Objectives

- Do not add global MCP writes.
- Do not make VS Code part of `npx --agent all`.
- Do not infer `host_connected` from config file presence.
- Do not add new Cortex MCP tools or broaden MCP write authority.
- Do not publish, push, tag, release, rebuild public bundles, or claim remote
  GitHub package-spec certification unless a later explicit release identity
  decision authorizes it.
- Do not commit private canary names, private target paths, private product
  vocabulary, raw target docs, raw stack traces, prompts, code, diffs, branch
  names, remotes, or secrets.
- Do not fix only an installed target mirror. Portable defects must land in TES
  package source and be replayed through neutral fixtures.

## Required Status Semantics

| Status | Required Meaning |
|--------|------------------|
| `PASS` | Every required verifier for the claimed scope is green. |
| `PARTIAL` | Usable runtime exists, but certification-relevant adoption, parity, hygiene, provenance, or Field Reports intake evidence is degraded/failing. |
| `NEEDS_REVIEW` | A concrete maintainer or user repair route is required before readiness can be claimed. |
| `BLOCKED` | Unsafe, privacy-breaking, destructive, or unresolved contract state prevents continuation. |

`INSTALLED` may remain an operation status in installer/MCP events, but it must
not be used as the final certification verdict.

## Implementation Units

| Unit | Owned Surfaces | Required Behavior | Required Oracle |
|------|----------------|-------------------|-----------------|
| SPEC-000 Preflight And Reproducer | new or existing installed-target fixture/oracle, issue #46 evidence mapping | Reproduce the partial-certification shape in a neutral fixture without private names. Capture expected failing conditions before repair: Mantra Gate degraded, command-trigger parity fail, stale quality-gate path when generated, residue/provenance hygiene risk. | A fixture command that fails before repair and passes after repair; `git status --short --branch --untracked-files=all`. |
| SPEC-001 Certification Aggregator | `scripts/tes_install.py`, postinstall run records, `scripts/tes_npx_oracle.py`, `scripts/install_smoke.py` | Installer/postinstall summaries aggregate core runtime, MCP, installed adoption, trigger parity, and hygiene into `PASS`/`PARTIAL`/`NEEDS_REVIEW`/`BLOCKED`. MCP success alone cannot close as clean certification. | `python3 scripts/tes_install.py --self-test`; new fixture proving partial state does not produce final `PASS`. |
| SPEC-002 Installed Mantra Gate Surface | `scripts/mantra_gate_adoption_oracle.py`, adapter materialization, installer preserve/update behavior, `/tes-doctor` docs | Active installed Codex/Claude bootloaders either route to the owner skill or are reported as degraded/repairable. Preserve mode may keep user files but must not hide degraded TES routing. | `python3 scripts/mantra_gate_adoption_oracle.py --self-test`; installed fixture for Codex/Claude/Cursor. |
| SPEC-003 Command Trigger Parity | `scripts/command_trigger_oracle.py`, adapter bootloaders/skills/rules, generated runtime surfaces | Preferred triggers, aliases, and natural intents, including Portuguese `/goal` intent, are present in installed Codex, Claude, and Cursor surfaces or the installer reports partial certification. | `python3 scripts/command_trigger_oracle.py --self-test`; installed fixture with Codex/Claude/Cursor checks. |
| SPEC-004 Target Quality Gates Path | `scripts/tes_init.py`, project alignment/update docs, generated `docs/agents/QUALITY-GATES.md` fixtures | Generated or refreshed quality gates use `.agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py`, never the stale `tilly-engineer-skills/scripts/discipline_oracle.py` path. | Self-test/fixture with negative grep for the stale path. |
| SPEC-005 Bundle Hygiene And Provenance | `scripts/tes_bundle.py`, `scripts/materialize_adapter.py`, `scripts/validate_reference_package.py`, public bundle oracle | `.DS_Store` and OS residue are excluded from materialization, bundle entries, manifests, and staged setup. Dirty source provenance blocks sealed release claims or records an explicit exception. | `python3 scripts/tes_bundle.py --self-test`; `python3 scripts/validate_reference_package.py --staged-ready`; negative find/manifest fixture. |
| SPEC-006 Field Reports 2.1 Intake | `scripts/field_reports.py`, `scripts/field_reports_quality_oracle.py`, `scripts/field_reports_github_oracle.py`, GitHub issue template/workflow, docs | Field Reports body includes product class, severity, dedupe fingerprint, certification impact, likely owner surface, next action, and privacy-preserving evidence hints. Low-signal reports are suppressed; high-signal issues are actionable. | Field Reports self-tests and GitHub oracle prove classification, privacy, suppression, dedupe, and unsafe-body rejection. |
| SPEC-007 Doctor And Repair Routes | `/tes-doctor`, `/tes-mcp`, adapter docs, public docs | Doctor remains fallback/repair. It can repair installed Mantra Gate/trigger/MCP drift where safe, and it reports host-recognition states separately from config presence. | Command trigger/platform surface oracles; MCP smoke route; negative check for `host_connected` claim from file presence. |
| SPEC-008 Correlation, Evidence, And Release Identity | `docs/INDEX.md`, `docs/tds/DOCS-INDEX.yml`, roadmap, ADR, public docs, package version/bundle surfaces if authorized | Correlated docs reflect new certification semantics. Delivered behavior change gets explicit version/bundle decision before closure. No public release/ref claim without authorized release gate. | `python3 scripts/validate_tds.py`; `python3 scripts/validate_doc_size.py`; `python3 scripts/validate_reference_graph.py`; `npm run commit:check` before closure. |

## Field Reports 2.1 Required Shape

Every high-signal GitHub Field Report should expose sanitized maintainer routing:

```text
Report class: certification-gap
Product classes: CERTIFICATION_GAP, ADAPTER_DRIFT, RELEASE_HYGIENE
Severity: high
Certification impact: install/update cannot be claimed clean PASS
Affected surfaces: installer, adapter, field-reports, release-hygiene
Fingerprint: stable privacy-safe hash
Next action: run installed-target certification fixture
Privacy state: sanitized
```

The issue body must still avoid code, diffs, prompts, file contents, stack
traces, private paths, branch names, remotes, emails, URLs outside the TES issue
destination, and secrets.

## Required Negative Checks

- No private project names or private filesystem paths in TES tracked source,
  docs, evidence, fixtures, commits, or generated public docs.
- No `.vscode/mcp.json` from `npx --agent all`.
- No global MCP writes.
- No non-TES MCP server removal during repair/update.
- No `host_connected` claim from config file presence.
- No `PASS` certification when installed adoption or trigger parity fails.
- No stale `tilly-engineer-skills/scripts/discipline_oracle.py` quality-gate
  command in generated target docs.
- No `.DS_Store` in adapter materialization, bundle, staged setup, or manifest.
- No sealed release/ref/bundle claim when `source_tree_state=dirty`, unless a
  maintainer exception is recorded and the claim stays explicitly unsealed.
- No Field Reports issue body containing prohibited private or raw operational
  content.

## Required Oracles Before Closeout

Implementation closeout must run the smallest relevant subset while developing,
then the full package gate before claiming convergence:

```bash
python3 scripts/mantra_gate_adoption_oracle.py --self-test
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/tes_install.py --self-test
python3 scripts/tes_npx_oracle.py --self-test
python3 scripts/install_smoke.py --route mcp
python3 scripts/tes_update.py --self-test
python3 scripts/tes_bundle.py --self-test
python3 scripts/field_reports.py --self-test
python3 scripts/field_reports_quality_oracle.py --self-test
python3 scripts/field_reports_github_oracle.py --self-test
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
python3 scripts/private_vocabulary_oracle.py
git diff --check
npm run commit:check
```

If a runtime change is intentionally split across commits, each commit must name
the narrower oracle it passed and leave the Super SPEC status honest.

## Evidence And Canary Requirements

The final implementation must include:

- neutral fixture evidence proving the issue #46 failure class is reproduced and
  then repaired;
- a local package-source evidence report under `docs/evidence/reports/**`;
- a private canary replay note kept outside TES tracked content, referenced only
  generically in closeout;
- `git status --short --branch --untracked-files=all`;
- release identity decision: version/bundle unchanged by explicit exception, or
  version/bundle advanced under an authorized release plan.
