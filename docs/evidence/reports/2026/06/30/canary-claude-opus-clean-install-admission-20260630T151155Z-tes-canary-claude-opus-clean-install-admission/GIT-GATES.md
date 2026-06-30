---
tds_id: evidence.canary_claude_opus_clean_install_admission_aborted.git_gates_20260630
tds_class: evidence
status: archived
consumer: maintainers, canary operators, and Goal Maestro operators
source_of_truth: false
evidence_level: L1
---

# GIT-GATES.md

SPEC-004 git init (before TES install) + later SPEC-010/011/012/013 gates
Captured: 2026-06-30T15:15:42Z
Executor: Claude Code / Claude Opus 4.8 Max

## SPEC-004 git init each canary BEFORE TES install
```
===== git init cursor =====
Initialized empty Git repository in /Users/murillo/Dev/tes-canary/cursor/.git/
--- is-inside-work-tree: true ---
--- git status short (should be empty, no TES files yet) ---
--- TES present? .tes exists: no ---
===== git init claude =====
Initialized empty Git repository in /Users/murillo/Dev/tes-canary/claude/.git/
--- is-inside-work-tree: true ---
--- git status short (should be empty, no TES files yet) ---
--- TES present? .tes exists: no ---
===== git init codex =====
Initialized empty Git repository in /Users/murillo/Dev/tes-canary/codex/.git/
--- is-inside-work-tree: true ---
--- git status short (should be empty, no TES files yet) ---
--- TES present? .tes exists: no ---
```
