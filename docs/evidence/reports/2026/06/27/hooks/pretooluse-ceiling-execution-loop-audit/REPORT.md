---
tds_id: evidence.hooks.pretooluse_ceiling_execution_loop_audit_2026_06_27
tds_class: evidence
status: active
consumer: TES maintainers, hook authors, installer authors, oracle authors, release reviewers, and audit agents
source_of_truth: false
evidence_level: L3
tver: 0.1.0
---

# PreToolUse Ceiling Execution Loop Audit

Audit date: 2026-06-27.

Final status: `LOCAL_BUNDLED_NEEDS_EVIDENCE`.

This report audits the linear execution of the PreToolUse ceiling installed
evidence unblocker loop. It does not declare `PASS_CEILING`. The package source
and local release identity are green at version `0.3.221`, but native installed
host evidence was not available in this run, so installed ceiling remains
`NEEDS_EVIDENCE`.

## Scope

The audited source instruction was
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-pretooluse-ceiling-installed-evidence-unblocker.md`.

The execution ledger was
`docs/roadmap/goals/ledgers/GOAL-EXECUTION-LOOP-LEDGER-pretooluse-ceiling-installed-evidence-unblocker.md`.

The protected baseline was the earlier closure state `NEEDS_EVIDENCE`. The loop
was required to preserve host-specific contracts and avoid any all-host
`PASS_CEILING` claim unless each host proved its own current v2 scope.

## Unit Outcome

| Unit | Commit | Outcome |
|------|--------|---------|
| `SPEC-000` | no material commit | Read-only preflight confirmed `NEEDS_EVIDENCE` and no proven `PASS_CEILING`. |
| `SPEC-001` | `e1e51351` | Scoped ceiling evidence per host using `pretooluse_decision@2` and no cross-fill. |
| `SPEC-002` | `2b6b7d6e` | Exposed installed `helper_contract_status` and `discoverability_status`. |
| `SPEC-003` | `986cfc0a` | Installed `PRETOOLUSE-CONTRACT.md` and locked path/hash/version. |
| `SPEC-004` | `aae491ec` | Formalized duplicate/replay/Cursor batch noise as non-blocking unless current v2 contradiction exists. |
| `SPEC-005` | `e67ee51e` | Added `needs-evidence` and `pass-ceiling` packet gates; closed current packet as `NEEDS_EVIDENCE`. |
| `SPEC-006` | `2de324bc` | Bumped package identity to `0.3.221` and regenerated the local public bundle. |

## Behavioral Findings

`hook-health` now evaluates PreToolUse ceiling evidence per host. Evidence from
Claude Code, Codex, and Cursor is not pooled to satisfy another host's missing
fields.

The ceiling schema is `pretooluse_decision@2`. Legacy rows remain historical
context and can produce duplicate diagnostics, but they do not fill current v2
ceiling requirements.

Installed `hook-health` exposes `helper_contract_status` and
`discoverability_status` from installed evidence. These statuses are not filled
from the source matrix.

The installed target now receives
`.tes/docs/architecture/PRETOOLUSE-CONTRACT.md`, and the install lock records
the installed path, package path, SHA-256 hash, and package version.

Duplicate history, replay residue, and distinct Cursor batch rows are hygiene
signals. They cannot block ceiling by themselves. A current
`pretooluse_decision@2` contradiction blocks only the same host and scope.

`pretooluse_evidence_oracle.py` now has expectation modes. The current packet
passes `--expect needs-evidence`; it fails `--expect pass-ceiling` because it has
no native host evidence, claimed host scope, or `PASS_CEILING` matrix state.

## Release Identity

Delivered behavior changed in the installer, hook-health, evidence oracle,
contract installation, prompt oracle, and public bundle surfaces. The correct
release-identity decision was a patch bump.

Package version: `0.3.221`.

Local bundle:
`docs/dist/0.3.221/tilly-engineer-skills-0.3.221.zip`.

Bundle SHA-256:
`edac2cbba41fac9b4bd19cf8b403f1ae3382edb3a5670866c97486ec203c00b1`.

The previous local dist directory `docs/dist/0.3.220` was pruned by the
single-current-dist policy. Public docs and i18n metadata were regenerated for
the new fixed-ref version. No push, tag, remote publish, marketplace action,
`npm publish`, or `npm run release:check` was performed.

## Verification Evidence

The following gates passed during the loop or immediately after closure:

- `python3 scripts/tes_install.py --self-test`;
- `python3 scripts/host_runtime_matrix_oracle.py --self-test`;
- `python3 scripts/hook_audit_prompt_oracle.py --self-test`;
- `python3 scripts/installed_certification_oracle.py --self-test`;
- `python3 scripts/pretooluse_evidence_oracle.py --self-test`;
- `python3 scripts/pretooluse_evidence_oracle.py --packet docs/evidence/reports/2026/06/27/hooks/pretooluse-ceiling-installed-evidence --expect needs-evidence`;
- negative `pass-ceiling` packet validation against the current packet;
- `python3 scripts/public_bundle_oracle.py`;
- `python3 scripts/tes_bundle.py --self-test`;
- `python3 scripts/tes_bump.py --governance-check --json`;
- `python3 scripts/validate_reference_package.py`;
- `python3 scripts/validate_tds.py`;
- `python3 scripts/validate_doc_size.py`;
- `npm run commit:check`;
- `git diff --check`.

The final post-commit package checks reported:

- `public_bundle_oracle.py`: `PASS` for version `0.3.221`;
- `validate_reference_package.py`: `PASS`;
- `tes_bump.py --governance-check --json`: `PASS`, with no pending bump-triggering change;
- current evidence packet with `--expect needs-evidence`: `PASS`;
- current evidence packet with `--expect pass-ceiling`: expected `FAIL`.

## Ceiling Decision

`PASS_CEILING` remains unavailable. The current evidence packet is sanitized
installed-target simulation, not native installed host proof.

The missing proof is native, per-host evidence that shows each claimed host's
own current v2 scope with:

- reason codes;
- classifier trace;
- renderer trace;
- ledger trace;
- command redaction evidence;
- discoverability evidence;
- helper contract status from the installed target;
- `floor_status=PASS_BASIC`;
- `ceiling_status=PASS_CEILING`;
- no same-host current v2 contradiction.

Until that packet exists, the correct audit status is
`LOCAL_BUNDLED_NEEDS_EVIDENCE`.

## Residual Risk

The remaining risk is evidence availability, not source implementation. Native
host smoke or authorized canary replay must be captured before any global
ceiling claim can be made.

The local package identity is complete, but remote release certification is out
of scope until a separate push, tag, publish, and `release:check` authorization
exists.
