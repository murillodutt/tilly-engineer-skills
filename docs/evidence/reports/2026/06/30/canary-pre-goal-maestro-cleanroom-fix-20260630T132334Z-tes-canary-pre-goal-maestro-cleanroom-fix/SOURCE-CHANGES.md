# SOURCE-CHANGES

Portable fixes applied in `/Users/murillo/Dev/tilly-engineer-skills`:

| File | SPEC | Change |
|------|------|--------|
| `scripts/tes_install.py` | SPEC-002, SPEC-005 | Codex hook commands use absolute target paths; legacy migration self-test; hook-health truthfulness preserved |
| `scripts/project_context_oracle.py` | SPEC-003 | OS residue excluded from territory anchors |
| `scripts/tes_init.py` | SPEC-003 | OS residue excluded from project scan/anchors by name and prefix |
| `scripts/installed_certification_oracle.py` | SPEC-003, SPEC-005 | Full-target OS residue scan; visible `hook_runtime_health` NEEDS_EVIDENCE finding without collapsing aggregate PASS |
| `scripts/project_alignment_oracle.py` | SPEC-004 | Require `DOCUMENTATION-AUTHORITY.md` and `docs/agents/contracts/**` after non-scaffold mesh |
| `scripts/verify_documentation_inventory.py` | repair round 2 | Accept Identity Git HEAD at `HEAD`, `HEAD~1`, or any Git ancestor of `HEAD`; self-tests for parent and multi-commit drift |
| `docs/architecture/INSTALLATION-FRAMEWORK.md` | SPEC-002 (audit) | Codex hook entry documents absolute target path via `codex_hook_command()`, not `git rev-parse` |

Version decision: **required content, identity already 0.3.231** — delivered installer/oracle behavior changed; package version was already bumped to `0.3.231` in-tree before this run. No additional bump/tag/push performed (owner authorization required).

Self-tests run: `project_context_oracle`, `project_alignment_oracle`, `tes_map_oracle`, `tes_install`, `installed_certification_oracle`, `command_trigger_oracle`, `tes_bundle`, `field_reports`, `private_vocabulary_oracle` PASS. `tes_init --self-test` FAIL (pre-existing `install_smoke.py --self-test` gate inside init bundle). `validate_tds.py` FAIL on untracked evidence/Super SPEC paths (expected before index/commit).
