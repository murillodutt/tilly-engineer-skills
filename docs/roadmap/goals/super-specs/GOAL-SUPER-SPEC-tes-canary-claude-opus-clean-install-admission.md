---
tds_id: roadmap.goal_super_spec.tes_canary_claude_opus_clean_install_admission
tds_class: roadmap
status: active
consumer: maintainers, Claude Opus execution agents, installer authors, oracle authors, canary operators, and Goal Maestro operators
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# GOAL-SUPER-SPEC: TES Canary Claude Opus Clean Install Admission

Status: active corrective Super SPEC.

Execution host: Claude Code.

Execution model: Claude Opus 4.8 Max, or the closest explicitly selected
Claude Opus Max mode available to the operator.

Created: 2026-06-30.

Purpose: recreate and certify the three TES canaries from the prepared local
`0.3.231` bundle before any `tes-goal-maestro --execute-loop` run. This SPEC
exists because the last cycle showed green reports can still hide absent Git
gates, missing Field Reports `pre-push`, stale postinstall ledgers, and bundle
contamination.

Canonical artifact:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-canary-claude-opus-clean-install-admission.md`

## Inputs

The Claude executor must set and journal these values before writes:

```bash
export PACKAGE_SOURCE="<absolute path to this package source checkout>"
export CANARY_ROOT="<absolute path to the local canary root>"
export PY="/opt/homebrew/opt/python@3.14/bin/python3.14"
export BUNDLE_VERSION="0.3.231"
export BUNDLE_PATH="$PACKAGE_SOURCE/docs/dist/0.3.231/tilly-engineer-skills-0.3.231.zip"
export BUNDLE_SHA="565ccb30abceb635056db9f7211f155a740a2a7163895a52900304cc2c2a1912"
```

Targets:

```text
$CANARY_ROOT/cursor
$CANARY_ROOT/claude
$CANARY_ROOT/codex
```

If paths are not explicit, stop as `NEEDS_PATH_AUTHORITY`.

## Cleanroom Rules

- Do not run Goal Maestro in this SPEC.
- Do not invoke slash skills for `/tes-setup`, `/tes-align`, `/tes-map`, or
  `/tes-goal-maestro`.
- Do not use a source-built bundle fallback while the prepared local ZIP is
  valid.
- Do not claim native Codex or Cursor hook evidence from a Claude-only run.
- Do not push, tag, publish, release, call remote services, or write MCP memory.
- Do not change TES default adopter behavior to auto-install pre-commit.
- Patch package source only for reproduced portable defects.

## Journal Reference Gate

Mandatory reference:

```text
docs/evidence/reports/2026/06/30/canary-pre-goal-maestro-cleanroom-fix-20260630T132334Z-tes-canary-pre-goal-maestro-cleanroom-fix/JOURNAL.md
```

Before any canary write, Claude must open that journal and record in the new
`JOURNAL.md`:

- the reference path;
- UTC timestamp read;
- which practices are being reused;
- which prior gaps are explicitly guarded: stale HEADs, thin command logs,
  missing failed attempts, report-only proof, skipped gates hidden as PASS.

The reference journal is a format and quality baseline, not evidence for the new
state. If missing, stop as `NEEDS_JOURNAL_REFERENCE`.

## Evidence Packet

Create before canary writes:

```bash
cd "$PACKAGE_SOURCE"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-tes-canary-claude-opus-clean-install-admission"
EVIDENCE_DIR="docs/evidence/reports/2026/06/30/canary-claude-opus-clean-install-admission-${RUN_ID}"
mkdir -p "$EVIDENCE_DIR"
```

Required files:

```text
JOURNAL.md
PREFLIGHT.md
BUNDLE-PROVENANCE.md
CLEAN-INSTALL.md
SETUP-ALIGN-MAP.md
GIT-GATES.md
HOOK-EVIDENCE.md
ORACLE-RESULTS.md
SOURCE-CHANGES.md   # only if package source changes
FINAL-ADMISSION.md
```

`JOURNAL.md` must let this original package window audit the run without
trusting the executor's final chat summary.

## Journal Shape

First section:

```md
# Claude Opus Clean Install Admission Journal

- SPEC: GOAL-SUPER-SPEC-tes-canary-claude-opus-clean-install-admission
- Journal reference read:
- Executor host: Claude Code
- Executor model: Claude Opus 4.8 Max
- Started UTC:
- Package source:
- Canary root:
- Canary targets:
  - cursor:
  - claude:
  - codex:
- Cleanroom assertion: no slash-skill execution, no Goal Maestro execution, no
  MCP memory writes, no remote actions.
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
- Hash/proof before:
- Hash/proof after:
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
- Bundle path, sha256, and manifest source_commit:
- Canary reset method:
- Git HEAD and clean status by canary:
- Field Reports pre-push status by canary:
- Strict pre-commit status by canary:
- Setup/context/alignment/map status by canary:
- Installed certification status by canary:
- Hook evidence class by host and canary:
- OS residue and bytecode status by canary:
- Commands failed or skipped:
- Claims forbidden for the next Goal Maestro run:
- Exact next command recommended:
```

Do not rewrite journal history; append correction entries.

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

Contract collision stops as `NEEDS_CONTRACT_DECISION`.

## Stop States

Use only:

```text
NEEDS_PATH_AUTHORITY
NEEDS_JOURNAL_REFERENCE
NEEDS_BUNDLE_PROVENANCE
NEEDS_CANARY_RESET_AUTHORITY
NEEDS_CLEAN_INSTALL
NEEDS_GIT_REPOSITORY
NEEDS_FIELD_REPORTS_PRE_PUSH
NEEDS_PRECOMMIT_GATE
NEEDS_SETUP_PASS
NEEDS_ALIGN_PASS
NEEDS_MAP_PASS
NEEDS_INSTALLED_CERTIFICATION
NEEDS_NATIVE_CLAUDE_HOOK_EVIDENCE
NEEDS_SOURCE_FIX
NEEDS_RELEASE_IDENTITY_DECISION
BLOCKED_BY_UNAUTHORIZED_REMOTE_ACTION
READY_FOR_GOAL_MAESTRO_CANARY
```

## SPEC-000 - Reference And Evidence Start

Run:

```bash
cd "$PACKAGE_SOURCE"
test -f docs/evidence/reports/2026/06/30/canary-pre-goal-maestro-cleanroom-fix-20260630T132334Z-tes-canary-pre-goal-maestro-cleanroom-fix/JOURNAL.md
sed -n '1,260p' docs/evidence/reports/2026/06/30/canary-pre-goal-maestro-cleanroom-fix-20260630T132334Z-tes-canary-pre-goal-maestro-cleanroom-fix/JOURNAL.md
```

Write `JOURNAL.md` first entry and `PREFLIGHT.md` reference proof.

## SPEC-001 - Local Bundle Provenance

Run:

```bash
cd "$PACKAGE_SOURCE"
test -f "$BUNDLE_PATH"
test -f "$BUNDLE_PATH.sha256"
shasum -a 256 "$BUNDLE_PATH"
cat "$BUNDLE_PATH.sha256"
jq '{version,sha256,source_commit,metadata,stage_dir}' docs/dist/0.3.231/index.json
unzip -p "$BUNDLE_PATH" tes-bundle-manifest.json | jq '{version,source_commit,entry_count:(.entries|length), pycache:([.entries[].path] | map(select(test("__pycache__|\\\\.pyc$"))) | length)}'
PYTHONDONTWRITEBYTECODE=1 python3 scripts/tes_bundle.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 scripts/tes_install.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 scripts/install_smoke.py --self-test
```

Accept only SHA
`565ccb30abceb635056db9f7211f155a740a2a7163895a52900304cc2c2a1912`, matching
index/sha file, zero ZIP `__pycache__` or `.pyc`, and passing self-tests.

## SPEC-002 - Existing Canary Preflight

Run read-only probes for each target:

```bash
for t in cursor claude codex; do
  target="$CANARY_ROOT/$t"
  {
    echo "## $t"
    test -d "$target" && echo "target exists" || echo "target missing"
    git -C "$target" rev-parse --is-inside-work-tree 2>&1 || true
    git -C "$target" status --short --untracked-files=all 2>&1 || true
    find "$target" -maxdepth 4 \( -name '.DS_Store' -o -name '__MACOSX' -o -name '._*' -o -name 'Thumbs.db' -o -name '__pycache__' -o -name '*.pyc' \) -print 2>/dev/null | sort
    test -f "$target/.tes/postinstall.json" && jq '{version,state,last_status,advisories}' "$target/.tes/postinstall.json" || true
    test -f "$target/.tes/manifest.json" && jq '{version,source_commit,entries:(.entries|length)}' "$target/.tes/manifest.json" || true
  } | tee -a "$EVIDENCE_DIR/PREFLIGHT.md"
done
```

No report text may replace this proof.

## SPEC-003 - Reset Or Recreate Canaries

Preferred reset: archive existing target directories to a timestamped local
backup outside the new canary target, then create empty `cursor`, `claude`, and
`codex` directories. Clean-in-place requires explicit owner authorization in
the Claude window.

After reset:

```bash
for t in cursor claude codex; do
  target="$CANARY_ROOT/$t"
  mkdir -p "$target"
  find "$target" -mindepth 1 -maxdepth 1 -print | sort
done
```

Targets must be empty before Git init, or the run stops as
`NEEDS_CANARY_RESET_AUTHORITY`.

## SPEC-004 - Git Before TES Install

Run:

```bash
for t in cursor claude codex; do
  target="$CANARY_ROOT/$t"
  cd "$target"
  git init
  git config user.name "TES Canary"
  git config user.email "tes-canary@example.invalid"
  {
    echo ".DS_Store"; echo "**/.DS_Store"; echo "__MACOSX/"; echo "._*"; echo "Thumbs.db"
    echo ".tes/setup/"; echo ".tes/bk/"; echo ".tes/cortex/"; echo ".tes/field-reports/"; echo ".tes/runtime/"
    echo "**/__pycache__/"; echo "*.pyc"
  } >> .git/info/exclude
  awk '!seen[$0]++' .git/info/exclude > .git/info/exclude.tmp
  mv .git/info/exclude.tmp .git/info/exclude
  git rev-parse --is-inside-work-tree
done
```

Git must exist before TES install. Otherwise stop as `NEEDS_GIT_REPOSITORY`.

## SPEC-005 - Clean Install From Local ZIP

Run:

```bash
for t in cursor claude codex; do
  target="$CANARY_ROOT/$t"
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$PACKAGE_SOURCE/scripts/tes_install.py" install \
    --target "$target" --agent all --mode clean-runtime \
    --bundle "$BUNDLE_PATH" --sha256 "$BUNDLE_SHA" --attach all --yes
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$PACKAGE_SOURCE/scripts/tes_install.py" postinstall \
    --target "$target" --agent claude --force
  jq '{version,attached_surfaces,target,mode}' "$target/.tes/tes-install-lock.json"
  jq '{version,state,last_status,last_run,advisories}' "$target/.tes/postinstall.json"
  jq '{version,source_commit,entries:(.entries|length)}' "$target/.tes/manifest.json"
done
```

Acceptance: version `0.3.231`, expected attach surfaces, postinstall
`complete/PASS`, and installed/staged manifests with no bytecode entries.

## SPEC-006 - Setup Equivalent

Run:

```bash
for t in cursor claude codex; do
  target="$CANARY_ROOT/$t"
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$target/.tes/bin/tes_init.py" --target "$target" --yes
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$target/.tes/bin/project_context_oracle.py" --target "$target"
done
```

Acceptance: `PROJECT-CONTEXT.md`, manifest evidence, and context oracle PASS.

## SPEC-007 - Alignment Equivalent

Without invoking `/tes-align`, create or update these canary mesh surfaces:

```text
docs/agents/DOCUMENTATION-AUTHORITY.md
docs/agents/PROJECT-STATE.md
docs/agents/PROJECT-ROADMAP.md
docs/agents/EXECUTION-LINE.md
docs/agents/QUALITY-GATES.md
docs/agents/BOUNDARIES-AND-CONSTRAINTS.md
docs/agents/KNOWLEDGE-LIFECYCLE.md
docs/agents/GLOSSARY.md
docs/agents/DECISIONS/**
docs/agents/evidence/*-project-alignment.md
docs/agents/contracts/**
```

Then run:

```bash
for t in cursor claude codex; do
  target="$CANARY_ROOT/$t"
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$target/.tes/bin/project_alignment_oracle.py" --target "$target" --strict
done
```

Acceptance: strict alignment exits `0`, `mesh_scaffold_only=false`, and
`DOCUMENTATION-AUTHORITY.md` plus `contracts/**` exist in every canary.

## SPEC-008 - Map Equivalent

Run:

```bash
for t in cursor claude codex; do
  target="$CANARY_ROOT/$t"
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$target/.tes/bin/tes_map.py" --target "$target" --write
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$target/.tes/bin/tes_map_oracle.py" --target "$target"
done
```

Acceptance: `.tes/gps/atlas.json`, `.tes/gps/*.eraserdiagram`, one `TES-MAP`
block, and map oracle PASS.

## SPEC-009 - Certification And Hook Health

Run after align/map:

```bash
for t in cursor claude codex; do
  target="$CANARY_ROOT/$t"
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$PACKAGE_SOURCE/scripts/tes_install.py" postinstall --target "$target" --agent claude --force
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$target/.tes/bin/installed_certification_oracle.py" --target "$target"
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$PACKAGE_SOURCE/scripts/tes_install.py" hook-health --target "$target" --agent claude --json-only
done
```

Acceptance: installed certification PASS, no stale `mesh.scaffold_only`
advisory after alignment, and Claude hook health classified from evidence.

## SPEC-010 - Field Reports Pre-Push

Run:

```bash
for t in cursor claude codex; do
  target="$CANARY_ROOT/$t"
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$target/.tes/bin/field_reports.py" install-hook --target "$target"
  test -f "$target/.git/hooks/pre-push"
  test -x "$target/.git/hooks/pre-push"
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$target/.tes/bin/field_reports.py" status --target "$target"
done
```

Missing executable `pre-push` stops as `NEEDS_FIELD_REPORTS_PRE_PUSH`.

## SPEC-011 - Strict Local Pre-Commit

Create `.git/hooks/pre-commit` in each canary. It must run:

```text
project_context_oracle.py --target "$root"
project_alignment_oracle.py --target "$root" --strict
tes_map_oracle.py --target "$root"
residue/bytecode negative scan
git diff --check
git diff --cached --check
```

Then prove:

```bash
for t in cursor claude codex; do
  target="$CANARY_ROOT/$t"
  chmod +x "$target/.git/hooks/pre-commit"
  git -C "$target" hook run pre-commit || "$target/.git/hooks/pre-commit"
done
```

The pre-commit gate is canary admission infrastructure only. Do not patch TES to
auto-install it for adopters.

## SPEC-012 - Baseline Commit

Run:

```bash
for t in cursor claude codex; do
  target="$CANARY_ROOT/$t"
  git -C "$target" status --short --untracked-files=all
  git -C "$target" add -A
  git -C "$target" commit -m "Prepare TES canary for Goal Maestro admission"
  git -C "$target" status --short --untracked-files=all
  git -C "$target" rev-parse --short HEAD
done
```

Acceptance: clean status after commit; ignored caches and runtime state are not
committed.

## SPEC-013 - Final Matrix

Run and retain output:

```bash
for t in cursor claude codex; do
  target="$CANARY_ROOT/$t"
  git -C "$target" rev-parse --short HEAD
  git -C "$target" status --short --untracked-files=all
  git -C "$target" hook run pre-commit || "$target/.git/hooks/pre-commit"
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$target/.tes/bin/project_context_oracle.py" --target "$target"
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$target/.tes/bin/project_alignment_oracle.py" --target "$target" --strict
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$target/.tes/bin/tes_map_oracle.py" --target "$target"
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$target/.tes/bin/installed_certification_oracle.py" --target "$target"
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$target/.tes/bin/field_reports.py" status --target "$target"
  find "$target" \( -name '.DS_Store' -o -name '__MACOSX' -o -name '._*' -o -name 'Thumbs.db' -o -name '__pycache__' -o -name '*.pyc' \) -not -path '*/.git/*' -print
done
```

All commands must exit `0`, all Git statuses must be clean, and residue scan
must print nothing.

## SPEC-014 - Hook Evidence Classification

Classify each canary:

```text
Claude: NATIVE_HOST_OBSERVED | MATERIAL_CONFIG | NEEDS_EVIDENCE | BLOCKED
Codex: MATERIAL_CONFIG | NATIVE_HOST_OBSERVED | NEEDS_EVIDENCE | BLOCKED
Cursor: MATERIAL_CONFIG | NATIVE_HOST_OBSERVED | NEEDS_EVIDENCE | BLOCKED
```

Claude native evidence may be claimed only from actual Claude Code hook ledger
rows. Codex/Cursor native evidence may not be cross-filled from Claude.

Required proof:

```bash
for t in cursor claude codex; do
  target="$CANARY_ROOT/$t"
  tail -n 80 "$target/.tes/runtime/hooks/executed.jsonl" 2>/dev/null || true
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$PACKAGE_SOURCE/scripts/tes_install.py" hook-health --target "$target" --json-only
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$PACKAGE_SOURCE/scripts/tes_install.py" hook-health --target "$target" --agent claude --json-only
done
```

## SPEC-015 - Final Admission

`FINAL-ADMISSION.md` must state:

- final stop state;
- bundle SHA and manifest source commit;
- canary HEADs and clean status;
- Field Reports `pre-push`;
- strict pre-commit;
- setup/context/align/map/install-certification;
- hook evidence class;
- residue/bytecode status;
- forbidden claims for Goal Maestro.

Preferred next command only after all gates pass:

```bash
/tes-goal-maestro --execute-loop --target "$CANARY_ROOT/claude"
```

## Source Fix Rule

If a portable package defect is reproduced, stop canary mutation, record
evidence in `SOURCE-CHANGES.md`, patch package source, run focused self-tests,
make a release-identity decision, and restart canary install from a verified
bundle. Do not patch installed mirrors only.

## Done

Close `READY_FOR_GOAL_MAESTRO_CANARY` only when the journal meets the reference
quality bar, all evidence files exist, all three canaries are Git-backed clean
commits, Field Reports `pre-push` and strict pre-commit exist and pass, local
bundle provenance is proven, setup/align/map/certification oracles pass, hook
evidence is classified without cross-host inference, and final admission names
no blocker.
