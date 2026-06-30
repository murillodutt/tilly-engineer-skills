---
tds_id: evidence.canary_pre_goal_maestro_cleanroom_fix.parallel_audit_official_20260630
tds_class: evidence
status: active
consumer: maintainers, canary operators, and Goal Maestro operators
source_of_truth: false
evidence_level: L2
---

# PARALLEL-AUDIT vs OFFICIAL DOCS (SPEC-scoped)
Generated: 2026-06-30T13:40:39Z

## cursor
### install identity
{
  "version": "0.3.231",
  "state": "complete",
  "last_status": "PASS"
}
manifest_version=0.3.231 entries=0
### git
true
c0c75da
pre-push: yes
pre-commit-local: yes
### codex hook path
0
0
command = "/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/murillo/Dev/tes-canary/cursor/.tes/bin/tes_install.py hook --agent codex --target /Users/murillo/Dev/tes-canary/cursor"
### os residue count
0
### lock negative_checks.os_residue_absent
true
### lock hook_runtime_health
NEEDS_EVIDENCE
### mesh surfaces
doc-auth: yes
contracts_files: 3
### oracles exit
context_exit=0
align_exit=0
map_exit=0
field_reports parse-fail

## claude
### install identity
{
  "version": "0.3.231",
  "state": "complete",
  "last_status": "PASS"
}
manifest_version=0.3.231 entries=0
### git
true
d9083a7
pre-push: yes
pre-commit-local: yes
### codex hook path
0
0
command = "/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/murillo/Dev/tes-canary/claude/.tes/bin/tes_install.py hook --agent codex --target /Users/murillo/Dev/tes-canary/claude"
### os residue count
0
### lock negative_checks.os_residue_absent
true
### lock hook_runtime_health
NEEDS_EVIDENCE
### mesh surfaces
doc-auth: yes
contracts_files: 3
### oracles exit
context_exit=0
align_exit=0
map_exit=0
field_reports parse-fail

## codex
### install identity
{
  "version": "0.3.231",
  "state": "complete",
  "last_status": "PASS"
}
manifest_version=0.3.231 entries=0
### git
true
cf84c93
pre-push: yes
pre-commit-local: yes
### codex hook path
0
0
command = "/opt/homebrew/opt/python@3.14/bin/python3.14 /Users/murillo/Dev/tes-canary/codex/.tes/bin/tes_install.py hook --agent codex --target /Users/murillo/Dev/tes-canary/codex"
### os residue count
0
### lock negative_checks.os_residue_absent
true
### lock hook_runtime_health
NEEDS_EVIDENCE
### mesh surfaces
doc-auth: yes
contracts_files: 3
### oracles exit
context_exit=0
align_exit=0
map_exit=0
field_reports parse-fail

## source package spot checks
tes_install_git_rev_parse_count: 3
1
2
3

## Official-doc crosswalk (SPEC-scoped)

| SPEC axis | Official source | Expected | Observed now | Verdict |
|-----------|-----------------|----------|--------------|---------|
| Codex hook non-Git-safe | Super SPEC SPEC-002; `INSTALLATION-FRAMEWORK.md` L79 updated to absolute target path | Absolute target path in non-Git targets | Canaries: 0 `git rev-parse` matches; source `codex_hook_command()` uses absolute path; doc aligned | **PASS** |
| OS residue vs certification | Super SPEC SPEC-003; INSTALL artifact hygiene semantics | No residue on proof surfaces; `os_residue_absent` truthful | All canaries: 0 residue; source cert PASS; lock `os_residue_absent: true` consistent | **PASS** |
| Context anchor | `project_context_oracle.py` | No OS residue anchors | `context_exit=0` all | **PASS** |
| Align mesh | `tes-align` SKILL + `project_alignment_oracle.py` | `DOCUMENTATION-AUTHORITY` + `contracts/**` when refined | doc-auth yes; contracts 3 files; `align_exit=0` all | **PASS** |
| Map | `tes-map` SKILL | Managed `TES-MAP` block + sidecars | `map_exit=0`; `TES-MAP:START` present all | **PASS** |
| Field Reports pre-push | `INSTALL.md` L92; `COMMAND-TRIGGERS` `/tes-field-reports` | Material pre-push when Git-backed | pre-push yes; `[field-reports] PASS` all | **PASS** |
| Project pre-commit | `INSTALL.md` + Super SPEC distinction | TES default does **not** auto-install; canary-local gate authorized | Local `.git/hooks/pre-commit` yes; **not** a TES installer promise | **PASS (scoped)** |
| Hook native proof | Super SPEC + `COMMAND-TRIGGERS` hook-health | No false native PASS; NEEDS_EVIDENCE allowed | lock `hook_runtime_health=NEEDS_EVIDENCE`; hook-health cursor/claude NEEDS_EVIDENCE | **PASS (honest downgrade)** |
| Git admission | Super SPEC SPEC-006 | Git-backed canaries | `rev-parse=true`; HEAD c0c75da / d9083a7 / eea3d83 | **PASS** |

## Contract collisions recorded

1. ~~**`docs/architecture/INSTALLATION-FRAMEWORK.md` L79** documents Codex hooks as `$(git rev-parse --show-toplevel)/...`~~ **Resolved:** doc now matches `codex_hook_command()` absolute target path semantics.

## Admission re-check vs Super SPEC success bar

- **cursor:** GO for Goal Maestro primary target (oracles 0, residue 0, Git gates PASS).
- **claude:** GO as support canary (same).
- **codex:** GO as support canary after audit repair (residue removed, install lock recertified via `tes_install install` + `postinstall`; HEAD `cf84c93`).

Overall: **READY_FOR_GOAL_MAESTRO_CANARY (all three)** — cursor primary, claude/codex support.
