---
tds_id: evidence.canary_claude_opus_clean_install_admission_aborted.clean_install_20260630
tds_class: evidence
status: archived
consumer: maintainers, canary operators, and Goal Maestro operators
source_of_truth: false
evidence_level: L1
---

# CLEAN-INSTALL.md

SPEC-003 reset (clean-in-place, owner-authorized) + SPEC-005 install
Captured: 2026-06-30T15:15:10Z
Executor: Claude Code / Claude Opus 4.8 Max

## SPEC-003 clean-in-place reset
Method: remove all contents inside each named target (cursor/claude/codex), keep the target dir itself, then prove empty.
```
===== reset cursor =====
before count: 1320
--- post-reset top-level listing (should be empty) ---
after count: 0
target still exists: yes
===== reset claude =====
before count: 1319
--- post-reset top-level listing (should be empty) ---
after count: 0
target still exists: yes
===== reset codex =====
before count: 1319
--- post-reset top-level listing (should be empty) ---
after count: 0
target still exists: yes
```
