---
tds_id: evidence.report.tes_sync_0_3_209
tds_class: evidence
status: active
consumer: maintainers, release reviewers, and hook-audit operators
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# TES Sync 0.3.209 Certification Packet

Date: 2026-06-27.

Scope: bump + bundle + public refs.

Reason: the sync payload ships the hardened installed-target host runtime
matrix so reviewers can rerun hook analysis from a synchronized public identity.
The release identity advances from `0.3.208` to `0.3.209`.

## Identity

- Previous source version: `0.3.208`.
- New source version: `0.3.209`.
- Bundle: `docs/dist/0.3.209/tilly-engineer-skills-0.3.209.zip`.
- Bundle SHA-256: `9a7f7fb59a60348dad846f221d94e944bd66a6f416552d01b9d7888f39063da0`.
- Single-current-dist policy: `docs/dist/0.3.208/**` pruned by the bundle publisher.

## Included Hook Matrix Delta

- `scripts/host_runtime_matrix_oracle.py` installs a temporary target with
  hooks attached, checks generated host config commands, exercises host-specific
  output contracts, checks runtime ledger records, and verifies Cortex no-write.
- `package.json` exposes `npm run host-runtime:matrix` and wires the matrix into
  `commit:closure`.
- `scripts/staged_commit_gate.py` runs the matrix when hook/runtime surfaces move.

## Reverse Certification

The matrix was stress-tested against temporary mutants before sync:

- Codex hook command with the wrong `--agent` must fail.
- Claude `SessionStart` rewake without async flags must fail.
- Cursor `preToolUse` timeout drift must fail.
- Runtime ledger with forbidden Cursor evidence removed must fail.

## Next Hook Test Protocol

Every platform should run the shared source/package gate first:

```bash
npm run host-runtime:matrix
```

Then each platform must add one native smoke using its normal editing tool,
before the final `hook-health` check:

- Codex: mutate `.tes/runtime/hook-smoke/codex/SKILL.md` through native
  `apply_patch`; verify first pass surfaces `Flash-Fry`, second same-session
  pass is silent, and `hook-health` records `codex PreToolUse OBSERVED`.
- Claude Code: mutate `.tes/runtime/hook-smoke/claude/SKILL.md` through native
  Write/Edit; verify `hookSpecificOutput.additionalContext` on first governed
  pass, no repeated marker on the second pass, and forbidden Bash exits `2`.
- Cursor: mutate `.tes/runtime/hook-smoke/cursor/SKILL.md` through native
  Write/Edit or MultiEdit; verify JSON allow with `user_message` on first
  governed pass, JSON deny for forbidden shell, and routine Read stays silent.

Final command on each installed target:

```bash
python3 .tes/bin/tes_install.py hook-health --target . --json-only
```

Expected result is `PASS` or `PASS_WITH_FINDINGS` only for known non-blocking
ledger residue/duplicate findings; any missing native `PreToolUse` observation
for the current platform is a failed smoke.

## Local Certification

Passed before sync closeout:

- `python3 scripts/tes_bump.py --governance-check`
- `python3 scripts/tes_bump.py patch --dry-run --json`
- `python3 scripts/tes_bump.py patch --yes --json`
- `python3 scripts/tes_bundle.py publish --adapter all`
- `python3 scripts/build_public_docs.py`
- `python3 scripts/validate_reference_package.py`
- `python3 scripts/public_bundle_oracle.py`
- `npm run host-runtime:matrix`
- `python3 scripts/validate_tds.py`
- `python3 scripts/tds_surface_oracle.py`
- `npm run commit:check`
- `npm run commit:closure`

## Boundaries

- No force push.
- No tag move.
- No secrets.
- No marketplace, cloud, or package-registry publish.
