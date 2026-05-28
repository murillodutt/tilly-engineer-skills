---
tds_id: evidence.installed_certification_field_reports_hardening_20260528
tds_class: evidence
status: active
consumer: maintainers, installer authors, adapter authors, Field Reports maintainers, and release reviewers
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# Installed Certification And Field Reports Hardening

Date: 2026-05-28.

## Summary

This run implements the local package-source work from ADR 0003.1 and the
installed certification hardening Super SPEC. The portable failure class was a
false green: MCP/config success could look clean while installed adoption,
command triggers, generated quality gates, artifact hygiene, provenance, or
feedback intake still needed review.

TES now has a deterministic installed certification oracle and the installer
aggregates that oracle into install and postinstall status. Clean certification
distinguishes `PASS`, `PARTIAL`, `NEEDS_REVIEW`, and `BLOCKED`; MCP success
alone is not enough.

## Commits

| SPEC | Commit | Result |
|------|--------|--------|
| Baseline | `38da8ae` | ADR 0003.1 and Super SPEC preserved as planning baseline. |
| SPEC-000 | `e03711c` | Neutral installed-target fixture/oracle proves degraded and healthy states. |
| SPEC-001 | `e9dfa15` | Installer/postinstall aggregate installed certification and retain MCP summary. |
| SPEC-002 | no material change | Mantra Gate installed surfaces already certified by oracle. |
| SPEC-003 | no material change | Command trigger parity already certified, including `gerar um /goal maestral`. |
| SPEC-004 | no material change | Generated `QUALITY-GATES.md` already uses the canonical discipline oracle path. |
| SPEC-005 | `e9dfa15` | Bundle excludes `.DS_Store`; dirty/package provenance is explicit and unsealed. |
| SPEC-006 | `9bc944e` | Field Reports carries product class, severity, dedupe, certification impact, owner surface, next action, and privacy state. |
| SPEC-007 | `9484f26` | `/tes-doctor` and `/tes-mcp` remain repair/fallback routes and preserve MCP state separation. |
| SPEC-008 | this report | Evidence and release identity decision. |

## Material Surfaces

- `scripts/installed_certification_oracle.py`
- `scripts/tes_install.py`
- `scripts/tes_bundle.py`
- `scripts/tes_npx_oracle.py`
- `scripts/field_reports.py`
- `scripts/field_reports_quality_oracle.py`
- `scripts/field_reports_github_oracle.py`
- `.github/ISSUE_TEMPLATE/tes-field-report.yml`
- `src/adapters/{codex,claude}/skills/tes-{doctor,mcp}/SKILL.md`
- `docs/install/AGENT-MANUAL.md`
- `docs/install/COMMAND-TRIGGERS.md`
- `docs/mesh/FIELD-REPORTS.md`

## Negative Checks

- No `.vscode/mcp.json` from `npx --agent all`.
- No `--agent vscode` in the npx surface.
- No global MCP writes.
- No removal of non-TES MCP servers.
- No `host_connected` claim from file presence.
- No clean `PASS` when installed adoption, trigger parity, quality gate path,
  hygiene, or provenance fails.
- No stale `.agents/skills/tilly-engineer-skills/scripts/discipline_oracle.py`
  path in generated quality gates.
- Source bundle generation removes and rejects `.DS_Store` and OS residue in
  bundle entries, staged setup, installed runtime artifacts, and the regenerated
  public bundle for `0.3.144`.
- No sealed release claim with dirty or unsealed package provenance.
- No unsafe Field Reports body content.

## Closeout Gate

Current local closeout status is `PASS`.

After explicit maintainer authorization, the public bundle script now purges
macOS residue before packaging and separates source provenance from
`docs/dist/**` distribution artifacts. The regenerated `0.3.144` bundle records
`source_tree_state=clean`, carries SHA-256
`5cccb0b3c900552504e87aa3b6337ad4266acc3a54dcaf8728239165cf9568fd`, and passes
`scripts/public_bundle_oracle.py`.

Mantra Gate record:

- `VERIFY`: `scripts/public_bundle_oracle.py` proves the regenerated public
  artifact has no OS residue and applies through the public bundle path.
- `SCOPE`: local source, docs, and `docs/dist/0.3.144/**` only; no tag, push,
  marketplace, cloud, or remote sync.
- `BEST_PATH`: keep source hygiene in the bundle generator and keep public
  release/ref certification separate from local artifact certification.
- `DOCUMENT`: this report carries the local closeout result and release
  identity boundary.
- `ORACLE`: `python3 scripts/public_bundle_oracle.py` passes on
  `docs/dist/0.3.144/**`.
- `RESOLVE`: remote GitHub npx/Bun ref certification remains pending explicit
  remote release gate authorization.
- `STATUS`: `PASS`.

## Release Identity

Delivered behavior changed. The local `0.3.144` public bundle was regenerated
after maintainer authorization, but no tag, push, publish, marketplace, cloud
action, or remote sync was performed. A sealed GitHub npx/Bun ref certification
still requires the authorized remote release gate.

Current local status is therefore: implementation and regenerated public bundle
committed locally; remote installer certification not claimed.

## Boundary

The private canary audit that motivated this work stays outside TES tracked
content. This report does not include private project names, paths, raw target
docs, code, diffs, prompts, remotes, branches, stack traces, or vocabulary.
