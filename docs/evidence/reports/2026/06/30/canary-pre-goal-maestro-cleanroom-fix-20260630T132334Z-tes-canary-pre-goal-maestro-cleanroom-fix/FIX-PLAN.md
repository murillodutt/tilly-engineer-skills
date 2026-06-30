---
tds_id: evidence.canary_pre_goal_maestro_cleanroom_fix.fix_plan_20260630
tds_class: evidence
status: active
consumer: maintainers, canary operators, and Goal Maestro operators
source_of_truth: false
evidence_level: L2
---

# FIX-PLAN

Finding: Codex hook command uses `git rev-parse --show-toplevel` in non-Git canaries (cursor, claude confirmed; codex partially fixed)
Evidence: PREFLIGHT.md codex config sections; `rg git rev-parse` on cursor/claude `.codex/config.toml`
Classification: source
Repair: Patch `scripts/tes_install.py` to emit absolute target-safe Codex hook commands; rematerialize via `attach --surface hooks`
Oracle: `tes_install.py --self-test`; target `rg` must return no stale git rev-parse paths
Owner decision needed: none

Finding: Cursor `project_context_oracle.py --target` fails on `docs/.DS_Store` anchor
Evidence: PREFLIGHT.md cursor project_context_oracle FAIL
Classification: source plus canary-state residue
Repair: Exclude OS residue from anchor generation in `project_context_oracle.py` and `tes_init.py`; remove `.DS_Store` from canaries; regenerate PROJECT-CONTEXT
Oracle: `project_context_oracle.py --self-test`; per-target `--target` PASS
Owner decision needed: none

Finding: `.DS_Store` exists while `os_residue_absent: true`
Evidence: PREFLIGHT.md os residue lists; lock negative_checks
Classification: source certification defect plus target residue
Repair: Expand `installed_certification_oracle.py` target scan; clean canary residue
Oracle: `installed_certification_oracle.py --self-test`; `find` returns nothing
Owner decision needed: none

Finding: Claude lacks `DOCUMENTATION-AUTHORITY.md` (contracts present in cursor/codex, absent authority in claude)
Evidence: PREFLIGHT file checks; alignment oracle previously PASS without authority surface
Classification: source oracle gap plus target alignment gap
Repair: Require authority and contracts in `project_alignment_oracle.py`; repair claude mesh surfaces
Oracle: `project_alignment_oracle.py --self-test`; per-target mesh file checks PASS
Owner decision needed: none

Finding: `hook_runtime_health` NEEDS_EVIDENCE while overall certification reads PASS
Evidence: PREFLIGHT lock components; postinstall last_status PASS
Classification: source certification reporting gap
Repair: Treat NEEDS_EVIDENCE as NEEDS_REVIEW in aggregate certification status; refresh lock after hook-health run
Oracle: `installed_certification_oracle.py --self-test`; HOOK-EVIDENCE.md classification
Owner decision needed: none

Finding: No Git repository, no pre-push, no pre-commit
Evidence: PREFLIGHT git and material git gates
Classification: canary-state
Repair: SPEC-authorized local `git init`, Field Reports pre-push, local pre-commit gate
Oracle: GIT-GATES.md; `git hook run pre-commit` exit 0
Owner decision needed: none (authorized by Super SPEC for canary admission)

Finding: Manifest root-context hash semantics / TES:PROJECT-OVERLAY wrapper
Evidence: not reproduced in preflight as blocking
Classification: false-positive for this run
Repair: none unless oracle failure appears after other repairs
Oracle: `tes_map_oracle.py --target`
Owner decision needed: none unless detach/uninstall regression appears
