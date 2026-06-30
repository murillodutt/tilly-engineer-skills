---
tds_id: roadmap.goal_super_spec.tes_canary_gap_repair_admission_alignment
tds_class: roadmap
status: active
consumer: maintainers, Claude Opus execution agents, installer authors, oracle authors, canary operators, and Goal Maestro operators
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# GOAL-SUPER-SPEC: TES Canary Gap Repair And Admission Alignment

Status: active corrective Super SPEC.

Execution host: Claude Code.

Execution model: Claude Opus 4.8 Max, or the closest explicitly selected
Claude Opus Max mode available to the operator.

Created: 2026-06-30.

Purpose: repair the package-source contracts, oracles, documentation, and local
bundle readiness behind the confirmed canary gaps. This is **not** a canary
replay SPEC. A separate session will later recreate or rerun the canaries after
this correction package is ready.

Canonical artifact:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-canary-gap-repair-and-admission-alignment.md`

## Confirmed Gaps

The executor must treat these as already confirmed by the previous audit, then
reconfirm read-only before changing source:

1. Git, pre-commit, and Field Reports `pre-push` were absent:
   - `git -C <canary> rev-parse` failed in all three canaries.
   - no `.git/hooks/pre-commit` or `.git/hooks/pre-push` existed.
   - init manifests recorded `tes_field_reports_pre_push=false`.
   - canary `QUALITY-GATES.md` files named persistent commit gates as
     `needs_review` or `unavailable`.
2. Installed canaries did not exactly match the prepared local ZIP:
   - local ZIP had 378 manifest entries, source commit `7a664a93`, SHA
     `565ccb30abceb635056db9f7211f155a740a2a7163895a52900304cc2c2a1912`;
   - canaries had 379 entries, source commit `88803788`;
   - the extra entry was a Python bytecode cache under a delivered skill.
3. Postinstall ledger contradicted post-align state:
   - `.tes/postinstall.json` was `complete/PASS`;
   - stale `mesh.scaffold_only` advisory remained after strict alignment passed.
4. Hook runtime evidence remained incomplete:
   - installed certification passed overall;
   - `hook_runtime_health.status=NEEDS_EVIDENCE`;
   - each canary had only the active host observed and other hosts configured
     without runtime observation.

## Non-Goal

Do not fix this by rerunning canaries in this SPEC. Do not reset, reinstall,
initialize Git, install hooks, rerun `install -> /tes-setup -> /tes-align ->
/tes-map`, or execute Goal Maestro against the canary targets here.

This SPEC ends at package/source readiness:

```text
PACKAGE_READY_FOR_CANARY_REPLAY
```

The later canary replay session will decide whether the canaries become:

```text
READY_FOR_GOAL_MAESTRO_CANARY
```

## Inputs

The Claude executor must set and journal these values:

```bash
export PACKAGE_SOURCE="<absolute path to this package source checkout>"
export CANARY_ROOT="<absolute path to the local canary root for read-only probes>"
export PY="/opt/homebrew/opt/python@3.14/bin/python3.14"
export BUNDLE_VERSION="0.3.231"
export BUNDLE_PATH="$PACKAGE_SOURCE/docs/dist/0.3.231/tilly-engineer-skills-0.3.231.zip"
export BUNDLE_SHA="565ccb30abceb635056db9f7211f155a740a2a7163895a52900304cc2c2a1912"
```

If paths are not explicit, stop as `NEEDS_PATH_AUTHORITY`.

## Cleanroom Rules

- No canary writes except evidence reads already present in the package source.
- No canary reset, reinstall, Git init, hook install, commit, or replay.
- No slash-skill execution for `/tes-setup`, `/tes-align`, `/tes-map`, or
  `/tes-goal-maestro`.
- No Goal Maestro execution.
- No MCP memory writes.
- No push, tag, publish, release, or cloud action.
- Package source may be patched only for reproduced portable defects.
- Installed canary mirrors must not be patched as the fix.

## Journal Reference Gate

Mandatory reference:

```text
docs/evidence/reports/2026/06/30/canary-pre-goal-maestro-cleanroom-fix-20260630T132334Z-tes-canary-pre-goal-maestro-cleanroom-fix/JOURNAL.md
```

Before any source edit, Claude must open that journal and record in the new
`JOURNAL.md`:

- reference path and UTC timestamp read;
- which audit practices are reused;
- how this SPEC avoids the previous drift: stale HEADs, thin command logs,
  omitted failed attempts, report-only proof, and skipped gates hidden as PASS.

The reference journal is a quality baseline, not evidence for the current
package state. If missing, stop as `NEEDS_JOURNAL_REFERENCE`.

## Evidence Packet

Create before source edits:

```bash
cd "$PACKAGE_SOURCE"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-tes-canary-gap-repair-admission-alignment"
EVIDENCE_DIR="docs/evidence/reports/2026/06/30/canary-gap-repair-admission-alignment-${RUN_ID}"
mkdir -p "$EVIDENCE_DIR"
```

Required files:

```text
JOURNAL.md
PREFLIGHT.md
GAP-CLASSIFICATION.md
SOURCE-CHANGES.md
BUNDLE-READINESS.md
ORACLE-RESULTS.md
CANARY-REPLAY-HANDOFF.md
FINAL-ADMISSION.md
```

`JOURNAL.md` must be sufficient for this package window to audit the run without
trusting final chat text.

## Journal Shape

First section:

```md
# Canary Gap Repair And Admission Alignment Journal

- SPEC: GOAL-SUPER-SPEC-tes-canary-gap-repair-and-admission-alignment
- Journal reference read:
- Executor host: Claude Code
- Executor model: Claude Opus 4.8 Max
- Started UTC:
- Package source:
- Canary root:
- Cleanroom assertion: no canary writes, no slash-skill execution, no Goal
  Maestro execution, no MCP memory writes, no remote actions.
```

Every material action:

```md
## <UTC timestamp> - <short action title>

- Phase:
- Actor/host:
- Working directory:
- Intent:
- Precondition:
- Command(s):
  ```bash
  <exact command or "none - file inspection/edit">
  ```
- Exit code(s):
- Files read:
- Files written:
- Proof before:
- Proof after:
- Evidence written:
- Result:
- Decision:
- Stop state after this entry:
- Next action:
```

Final section:

```md
## Final Audit Handoff

- Final status:
- Remaining stop state:
- Confirmed gaps:
- Source files changed:
- Docs/evidence files changed:
- Bundle status:
- Oracles passed:
- Oracles failed or skipped:
- Release identity decision:
- Canary replay requirements:
- Claims forbidden until replay:
- Exact next SPEC/session recommended:
```

## Authority Sources

Inspect before repair decisions:

- `docs/install/INSTALL.md`
- `docs/install/COMMAND-TRIGGERS.md`
- `docs/architecture/INSTALLATION-FRAMEWORK.md`
- `src/adapters/claude/skills/tes-align/SKILL.md`
- `src/adapters/claude/skills/tes-map/SKILL.md`
- `scripts/tes_install.py`
- `scripts/tes_bundle.py`
- `scripts/tes_init.py`
- `scripts/project_context_oracle.py`
- `scripts/project_alignment_oracle.py`
- `scripts/tes_map_oracle.py`
- `scripts/installed_certification_oracle.py`
- `scripts/field_reports.py`
- `scripts/validate_doc_size.py`

Contract collision stops as `NEEDS_CONTRACT_DECISION`.

## Stop States

Use only:

```text
NEEDS_PATH_AUTHORITY
NEEDS_JOURNAL_REFERENCE
NEEDS_PREFLIGHT_EVIDENCE
NEEDS_GAP_CLASSIFICATION
NEEDS_SOURCE_FIX
NEEDS_ORACLE_FIX
NEEDS_BUNDLE_READINESS
NEEDS_RELEASE_IDENTITY_DECISION
NEEDS_CANARY_REPLAY_HANDOFF
BLOCKED_BY_CANARY_WRITE_ATTEMPT
BLOCKED_BY_UNAUTHORIZED_REMOTE_ACTION
PACKAGE_READY_FOR_CANARY_REPLAY
```

## SPEC-000 - Reference And Evidence Start

Run:

```bash
cd "$PACKAGE_SOURCE"
test -f docs/evidence/reports/2026/06/30/canary-pre-goal-maestro-cleanroom-fix-20260630T132334Z-tes-canary-pre-goal-maestro-cleanroom-fix/JOURNAL.md
sed -n '1,260p' docs/evidence/reports/2026/06/30/canary-pre-goal-maestro-cleanroom-fix-20260630T132334Z-tes-canary-pre-goal-maestro-cleanroom-fix/JOURNAL.md
```

Write the first `JOURNAL.md` entry and retain reference proof in `PREFLIGHT.md`.

## SPEC-001 - Read-Only Gap Reconfirmation

Run only read-only probes against existing canary targets:

```bash
for t in cursor claude codex; do
  target="$CANARY_ROOT/$t"
  {
    echo "## $t"
    git -C "$target" rev-parse --is-inside-work-tree 2>&1 || true
    find "$target" -maxdepth 4 \( -path '*/.git/hooks/pre-commit' -o -path '*/.git/hooks/pre-push' -o -name '.pre-commit-config.yaml' -o -name 'lefthook.yml' \) -print 2>/dev/null | sort
    test -f "$target/.tes/postinstall.json" && jq '{version,state,last_status,advisories}' "$target/.tes/postinstall.json" || true
    test -f "$target/.tes/manifest.json" && jq '{version,source_commit,entries:(.entries|length)}' "$target/.tes/manifest.json" || true
    find "$target" -maxdepth 6 \( -name '__pycache__' -o -name '*.pyc' \) -print 2>/dev/null | sort
  } | tee -a "$EVIDENCE_DIR/PREFLIGHT.md"
done
```

Also prove the local bundle:

```bash
shasum -a 256 "$BUNDLE_PATH"
cat "$BUNDLE_PATH.sha256"
unzip -p "$BUNDLE_PATH" tes-bundle-manifest.json | jq '{version,source_commit,entry_count:(.entries|length), pycache:([.entries[].path] | map(select(test("__pycache__|\\\\.pyc$"))) | length)}'
```

No canary mutation is allowed. Any write attempt stops as
`BLOCKED_BY_CANARY_WRITE_ATTEMPT`.

## SPEC-002 - Classify Each Gap

Write `GAP-CLASSIFICATION.md` with one block per gap:

```text
Gap:
Observed evidence:
Source defect? yes/no
Contract/doc defect? yes/no
Oracle defect? yes/no
Canary-state defect? yes/no
Package fix required:
Replay-session requirement:
Acceptance oracle:
```

Minimum classification:

- Missing Git/pre-commit/pre-push is canary-state plus admission-contract gap.
  TES should not auto-install pre-commit for adopters, but the canary admission
  contract/oracle must block readiness when the replay session lacks Git,
  Field Reports `pre-push`, or strict pre-commit proof.
- Bundle mismatch and bytecode manifest entry is package/source or packaging
  hygiene gap when the prepared ZIP and installed staging disagree.
- Stale `mesh.scaffold_only` after strict alignment is postinstall/advisory
  truthfulness gap.
- `hook_runtime_health=NEEDS_EVIDENCE` under overall installed PASS is
  certification/admission truthfulness gap.

Do not patch before classification is written.

## SPEC-003 - Git Gate Admission Contract

Objective: make the package contract and/or oracle prevent false canary
readiness when Git gates are absent.

Required behavior:

- Field Reports `pre-push` is required for canary admission when the canary is
  Git-backed; if no Git repo exists, admission is blocked, not silently skipped.
- Strict pre-commit is canary admission infrastructure, not TES default adopter
  behavior.
- Final Goal Maestro admission must not claim `precommit_enforced`,
  `prepush_installed`, or `git_clean` without material Git proof.

Allowed source targets include docs, an existing oracle, or a new focused
admission oracle. Do not patch installed canaries.

Required proof: a red-capable fixture or self-test that fails when a target has
no Git repository but an admission report would claim readiness.

## SPEC-004 - Bundle And Bytecode Hygiene

Objective: prevent delivered manifests/staging from including runtime bytecode
or source-tree cache contamination.

Required behavior:

- public ZIP manifest excludes `__pycache__` and `.pyc`;
- source-built and local-bundle staging exclude `__pycache__` and `.pyc`;
- installed manifest or certification flags bytecode under delivered skills or
  staged setup as contamination;
- bundle readiness evidence compares ZIP manifest paths/hashes to the package
  index and rejects extra bytecode entries.

Required proof:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/tes_bundle.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 scripts/public_bundle_oracle.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_reference_package.py
```

If delivered behavior changes, make the release-identity decision before
claiming package readiness.

## SPEC-005 - Postinstall Advisory Truthfulness

Objective: prevent stale postinstall advisories from contradicting fresh
alignment oracles.

Required behavior:

- postinstall advisories must be scoped to the run that produced them;
- if a later forced postinstall or recovery run observes alignment PASS,
  `mesh.scaffold_only` must not remain as active current-state evidence;
- reports must distinguish historical advisory from current blocker;
- canary replay handoff must require a post-align postinstall refresh if the
  replay uses postinstall as admission evidence.

Required proof: a fixture or self-test where a target transitions from scaffold
to aligned, and the current sentinel/report no longer presents
`mesh.scaffold_only` as active.

## SPEC-006 - Hook Runtime Evidence Truthfulness

Objective: avoid overall PASS hiding incomplete native hook evidence.

Required behavior:

- installed certification may pass file/config installation while still
  surfacing `hook_runtime_health=NEEDS_EVIDENCE`;
- canary admission must treat native hook claims separately by host;
- configured-only hosts are `CONFIGURED_NOT_OBSERVED` or equivalent, not native
  PASS;
- Claude-run correction must not claim native Codex/Cursor hook evidence.

Required proof:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/tes_install.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 scripts/installed_certification_oracle.py --self-test
```

Add or update a red-capable fixture if no current fixture fails on cross-host
evidence filling.

## SPEC-007 - Source Patch And Validation

If source changes are needed:

1. patch package source only;
2. update associated docs when contracts change;
3. record every changed file in `SOURCE-CHANGES.md`;
4. run the focused self-tests named by the changed surface;
5. run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_tds.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_doc_size.py
git diff --check
npm run commit:check
```

If the change affects delivered behavior, decide whether to bump version and
refresh local bundle. If the owner explicitly keeps `0.3.231`, record that
exception and do not call it release-sealed.

## SPEC-008 - Bundle Readiness Without Canary Replay

Objective: prepare the package for the later replay session, without installing
into canaries here.

If delivered source changed and version policy allows bundle refresh, run the
package bundle path and retain `BUNDLE-READINESS.md`:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/tes_bundle.py publish --adapter all
PYTHONDONTWRITEBYTECODE=1 python3 scripts/public_bundle_oracle.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/tes_install.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 scripts/install_smoke.py --self-test
```

If no delivered source changed, record that the existing bundle remains the
replay input and include its SHA/provenance.

Do not stage, apply, install, or postinstall into the real canaries.

## SPEC-009 - Canary Replay Handoff

Write `CANARY-REPLAY-HANDOFF.md` for the later dedicated replay session. It must
include:

- exact package commit;
- bundle path/SHA or version bump decision;
- required replay order: Git init first, install from local bundle, setup,
  align, map, post-align postinstall refresh, Field Reports `pre-push`, strict
  pre-commit, baseline commit, final oracle matrix;
- forbidden claims until replay proves them;
- exact evidence files the replay session must produce;
- expected final replay state: `READY_FOR_GOAL_MAESTRO_CANARY` or named blocker.

This handoff is the only output that should instruct canary recreation.

## Final Admission

`FINAL-ADMISSION.md` must say one of:

- `PACKAGE_READY_FOR_CANARY_REPLAY`
- a stop state from this SPEC

It must not say `READY_FOR_GOAL_MAESTRO_CANARY`; that state belongs only to the
later canary replay session.

## Done Criteria

The SPEC is done only when:

- journal reference gate is recorded;
- all four confirmed gaps are classified;
- required source/doc/oracle fixes are made or explicitly blocked;
- focused self-tests and `npm run commit:check` pass for changed files;
- bundle readiness is either refreshed or explicitly unchanged with SHA proof;
- `CANARY-REPLAY-HANDOFF.md` exists;
- `FINAL-ADMISSION.md` ends as `PACKAGE_READY_FOR_CANARY_REPLAY` or a named
  blocker.
