---
tds_id: roadmap.goal_super_spec.tes_canary_pre_goal_maestro_cleanroom_fix
tds_class: roadmap
status: active
consumer: maintainers, Cursor execution agents, installer authors, oracle authors, canary operators, and Goal Maestro operators
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# GOAL-SUPER-SPEC: TES Canary Pre-Goal-Maestro Cleanroom Fix

Status: active corrective Super SPEC.

Execution host: Cursor.

Created: 2026-06-30.

Purpose: repair and recertify the three local TES canary targets before any
`tes-goal-maestro --execute-loop` run. The fix must be evidence-led, source-led
when the defect is portable, and cleanroom enough that a later Goal Maestro run
does not inherit false install, hook, Git, or alignment claims.

Canonical artifact:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-canary-pre-goal-maestro-cleanroom-fix.md`

## Targets

The corrective run owns these local canary targets only:

```text
/Users/murillo/Dev/tes-canary/cursor
/Users/murillo/Dev/tes-canary/claude
/Users/murillo/Dev/tes-canary/codex
```

The package source is:

```text
/Users/murillo/Dev/tilly-engineer-skills
```

Do not infer facts from prior chat reports. The Cursor executor must re-read
the files and rerun the read-only probes named below.

## Cleanroom Rule

```text
No TES skill invocation.
No Goal Maestro execution.
No report-only closure.
No synthetic hook evidence as native proof.
No installed-target-only patch for portable defects.
```

In the Cursor window:

- Do not type or execute `/tes-*` or `/tes:*` commands.
- Do not use `tes-goal-maestro`, `tes-align`, `tes-map`, `tes-setup`, or
  `tes-doctor` as agent skills.
- Do not write Cortex memory or use MCP remember tools.
- Do not push, publish, tag, release, open remote issues, or call cloud services.
- Use deterministic scripts, file inspection, and local Git only.
- Treat Cursor rules as ambient host context, not as evidence.
- Every final claim must cite a material file path or command output retained in
  a local evidence packet.

## Authority And Contract Sources

| Source | Required Use |
|---|---|
| `docs/install/INSTALL.md` | Defines functional default install, Field Reports `pre-push`, postinstall, and certification semantics. |
| `docs/install/COMMAND-TRIGGERS.md` | Defines `/tes-setup`, `/tes-align`, `/tes-map`, hook health, and Goal Maestro execution boundaries. |
| `docs/architecture/INSTALLATION-FRAMEWORK.md` | Defines attachment surfaces, runtime writers, per-host hooks, MCP registration, and manifest/reversibility. |
| `src/adapters/codex/skills/tes-align/SKILL.md` | Defines required `/tes-align` mesh surfaces, including `DOCUMENTATION-AUTHORITY.md` and `contracts/**`. |
| `src/adapters/codex/skills/tes-map/SKILL.md` | Defines `/tes-map` managed block and Atlas sidecar contract. |
| `scripts/tes_init.py` | Defines project context generation, Field Reports pre-push install, and persistent pre-commit detection semantics. |
| `scripts/project_context_oracle.py` | Current source oracle for `PROJECT-CONTEXT.md`. |
| `scripts/project_alignment_oracle.py` | Current source oracle for operating mesh alignment. |
| `scripts/tes_install.py` | Installer, postinstall, hook, hook-health, and installed certification entrypoint. |
| `scripts/field_reports.py` | Field Reports status, hook install, capture, drain, enable, and disable. |
| `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-goal-maestro-p0-harness-orchestration-feedback-fidelity.md` | Downstream admission pressure: Goal Maestro cannot start on false install/hook/Git evidence. |

If any source contradicts this Super SPEC, stop and record a contract collision
instead of choosing silently.

## Baseline Facts To Reconfirm

The previous audit found the following. They are not proof until reconfirmed in
the Cursor run.

| Finding | Current Expected Reconfirmation |
|---|---|
| All three canaries have TES `0.3.231`, staged 379 manifest entries, and `postinstall.json` state `complete`. | Read `.tes/manifest.json`, `.tes/tes-install-lock.json`, `.tes/postinstall.json`. |
| All three canaries are not Git repositories. | `git -C <target> rev-parse --is-inside-work-tree` fails before repair. |
| No material Git gate exists. | `.git/hooks/pre-commit`, `.git/hooks/pre-push`, `.githooks/*`, `.husky/*`, `lefthook.yml`, and `.pre-commit-config.yaml` absent before repair. |
| `cursor` and `claude` `.codex/config.toml` still use `$(git rev-parse --show-toplevel)` in non-Git targets. | Inspect `.codex/config.toml` lines for both canaries. |
| `codex` `.codex/config.toml` was manually corrected to absolute paths, but its lock still records stale hook runtime health. | Compare file with `.tes/tes-install-lock.json` and latest postinstall run. |
| `cursor` current `project_context_oracle.py --target` fails because `PROJECT-CONTEXT.md` has an invalid `docs/.DS_Store` anchor condition. | Rerun current oracle using Python. |
| `claude` lacks `docs/agents/DOCUMENTATION-AUTHORITY.md` and `docs/agents/contracts/**` even though `/tes-align` requires them. | File presence check plus skill contract line check. |
| `.DS_Store` files exist in all canaries while install certification reports `os_residue_absent: true`. | `find <target> -name .DS_Store`; inspect lock negative checks. |
| `hook_runtime_health` is not consistently closed. | Compare lock component, latest postinstall component, and `.tes/runtime/hooks/executed.jsonl`. |
| `/tes-map` Atlas sidecars and managed blocks exist in all three. | Run `tes_map_oracle.py --target <target>`. |

## Senior Success Bar

The repair is not complete when files merely exist. It is complete only when all
of these are true:

1. Each canary has a truthful state report retained in a new evidence packet.
2. Portable defects are repaired in package source, not only in canary mirrors.
3. Canary-only state defects are repaired locally with explicit scope and
   without changing TES default installer promises.
4. `project_context_oracle.py`, `project_alignment_oracle.py`, and
   `tes_map_oracle.py` pass on all three canaries after repair.
5. The active Cursor host has native hook runtime evidence or the report says
   exactly why it cannot be claimed.
6. Codex and Claude host hook health is not claimed from Cursor unless the proof
   is classified as config/simulation, not native host observation.
7. Field Reports `pre-push` is either materially installed in Git-backed
   canaries or explicitly `BLOCKED` with no GO for Goal Maestro admission.
8. A persistent pre-commit gate exists in each canary if the downstream Goal
   Maestro run will claim `precommit_enforced`; otherwise the state is
   explicitly `manual/no-precommit` and the Goal Maestro run must not claim
   enforcement.
9. `.DS_Store`, `__MACOSX`, AppleDouble files, `Thumbs.db`, bytecode caches, and
   generated local caches are excluded or removed from canary proof surfaces.
10. The final package source worktree status is understood and no unrelated user
    work is reverted.

## Key Distinctions

### Field Reports `pre-push` vs Project `pre-commit`

> **OVERTURNED (2026-06-30, tug-of-war ceiling F3).** The original constraint
> below — "TES does not auto-install a project pre-commit gate" — has been
> consciously overturned. The ceiling decision is that when a project is
> Git-eligible, TES **installs and verifies** both the Field Reports `pre-push`
> gate **and** a strict `pre-commit` gate, selecting the hook manager
> deterministically (husky for Node/TS, `pre-commit` when a config exists,
> lefthook as the polyglot default, deferring to any existing manager). Absence
> of an installable Git gate on an eligible target is no longer acceptable as
> advisory. See `docs/architecture/INSTALLER-TUG-OF-WAR-MATRIX.md` (F1/F2/F3) and
> `scripts/field_reports.py:install_hook` / `install_pre_commit_hook`. The
> historical text is retained for provenance only.

TES default install is responsible for Field Reports `pre-push` only when the
target is a Git repository. ~~TES does not auto-install a project pre-commit gate
during `/tes-setup`.~~ *(superseded — TES now installs a strict pre-commit gate
on an eligible Git target.)*

For these canaries, this Super SPEC authorizes local canary Git initialization
and a local persistent pre-commit gate **only as canary admission infrastructure
for Goal Maestro**, not as a new TES default installer behavior. *(The ceiling
overturn above promotes pre-commit installation to delivered default behavior on
eligible targets.)*

~~The executor must not patch TES to auto-install pre-commit in adopter
projects.~~ *(Overturned: TES now installs and verifies the strict pre-commit
gate on Git-eligible adopter projects.)*

### Native Hook Proof vs Synthetic Or Config Proof

Use these evidence classes:

| Class | Meaning | May Certify Native Host Health? |
|---|---|---|
| `MATERIAL_CONFIG` | Hook/MCP config file exists and points to a plausible command. | No. |
| `RECORDED_SCRIPT_RUN` | A deterministic script ran and returned PASS. | Only for the script scope. |
| `SYNTHETIC_LEDGER_FIXTURE` | A ledger entry was manually generated or replayed. | No. |
| `NATIVE_HOST_OBSERVED` | The current host actually fired the hook during host lifecycle or tool use. | Yes, for that host only. |
| `BLOCKED` | Required surface is absent, unsafe, or unobservable. | No. |

Cursor can natively observe Cursor. A Cursor-only execution must not claim native
Codex or Claude Code hook observation unless those hosts are separately opened
and observed in their native runtimes.

## Required Stop States

- `NEEDS_PREFLIGHT_EVIDENCE`
- `NEEDS_SOURCE_FIX`
- `NEEDS_CANARY_STATE_FIX`
- `NEEDS_GIT_REPOSITORY`
- `NEEDS_FIELD_REPORTS_PRE_PUSH`
- `NEEDS_PRECOMMIT_GATE_DECISION`
- `NEEDS_CURSOR_CONTEXT_REPAIR`
- `NEEDS_CLAUDE_ALIGNMENT_REPAIR`
- `NEEDS_CODEX_HOOK_PATH_REPAIR`
- `NEEDS_OS_RESIDUE_REPAIR`
- `NEEDS_NATIVE_HOOK_EVIDENCE`
- `NEEDS_LOCK_RUN_CONSISTENCY`
- `NEEDS_MANIFEST_HASH_DECISION`
- `NEEDS_RELEASE_IDENTITY_DECISION`
- `READY_FOR_GOAL_MAESTRO_CANARY`

Do not invent a green status. Use one of these until all acceptance criteria are
met.

## Evidence Packet

Before edits, create a local evidence directory in package source:

```bash
cd /Users/murillo/Dev/tilly-engineer-skills
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-tes-canary-pre-goal-maestro-cleanroom-fix"
EVIDENCE_DIR="docs/evidence/reports/2026/06/30/canary-pre-goal-maestro-cleanroom-fix-${RUN_ID}"
mkdir -p "$EVIDENCE_DIR"
```

Retain:

- `PREFLIGHT.md`
- `FIX-PLAN.md`
- `JOURNAL.md`
- `SOURCE-CHANGES.md` when package source changes
- `CANARY-REPAIR.md`
- `ORACLE-RESULTS.md`
- `HOOK-EVIDENCE.md`
- `GIT-GATES.md`
- `FINAL-ADMISSION.md`

These files are implementation evidence. They must not contain private secrets,
raw prompts, raw stack traces, or irrelevant local paths outside the named
canaries and package source.

### Mandatory Audit Journal

`JOURNAL.md` is mandatory and blocking. The Cursor executor must update it
throughout the run, not reconstruct it at the end. If `JOURNAL.md` is missing,
thin, backfilled, or inconsistent with file mtimes / command evidence, this
SPEC must close as `BLOCKED` with stop state `NEEDS_PREFLIGHT_EVIDENCE`.

The journal exists so this original audit window can inspect what happened
without trusting the executor's final summary.

Required journal location:

```text
$EVIDENCE_DIR/JOURNAL.md
```

Required first section:

```md
# Cleanroom Fix Journal

- SPEC: GOAL-SUPER-SPEC-tes-canary-pre-goal-maestro-cleanroom-fix
- Executor host: Cursor
- Started UTC:
- Package source: /Users/murillo/Dev/tilly-engineer-skills
- Canary targets:
  - /Users/murillo/Dev/tes-canary/cursor
  - /Users/murillo/Dev/tes-canary/claude
  - /Users/murillo/Dev/tes-canary/codex
- Cleanroom assertion: no /tes-* skills, no Goal Maestro execution, no MCP
  memory writes, no remote actions.
```

Every investigation, decision, command, and file edit must append an entry with
this exact shape:

```md
## <UTC timestamp> - <short action title>

- Phase: SPEC-000 | SPEC-001 | ... | SPEC-012
- Actor/host: Cursor
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

Rules:

- Append a journal entry before and after any material file edit. The "before"
  entry records intent, target files, and pre-edit proof. The "after" entry
  records actual writes, verification, and any deviation.
- For every command used as evidence, record the exact command, target, exit
  code, and where the full or summarized output was retained.
- For every canary file edited manually, record why deterministic regeneration
  was not used.
- For every source file changed, record why the defect is portable and which
  canary evidence forced the source change.
- For every blocked/skipped gate, record the concrete reason and whether it is
  an accepted downgrade or an admission blocker.
- For every Git operation, record repository path, `git status --short` before,
  command, result, and `git status --short` after.
- For every hook claim, classify evidence as `MATERIAL_CONFIG`,
  `RECORDED_SCRIPT_RUN`, `SYNTHETIC_LEDGER_FIXTURE`, `NATIVE_HOST_OBSERVED`, or
  `BLOCKED`.
- Do not paste huge raw JSON outputs into the journal. Keep the journal
  readable and link to the evidence file that retains the full output when
  needed.
- Do not omit failed attempts. Failed commands and abandoned hypotheses are
  required audit evidence.
- Do not rewrite journal history except to fix a typo in the current entry; add
  a correction entry instead.

Required final journal section:

```md
## Final Audit Handoff

- Final status:
- Remaining stop state:
- Source files changed:
- Canary files changed:
- Evidence files created:
- Commands that passed:
- Commands that failed or were skipped:
- Git/pre-push/pre-commit status by canary:
- Context/alignment/map status by canary:
- Hook evidence class by host:
- OS residue status by canary:
- Claims explicitly forbidden for the next Goal Maestro run:
- Exact next prompt/command recommended:
```

The final response in Cursor must cite `JOURNAL.md`. This current window should
be able to audit the run by opening only `JOURNAL.md` plus the evidence files it
references.

## SPEC-000 - Read-Only Preflight

Objective: reproduce the current gaps in Cursor without using reports as proof.

Allowed writes: the evidence packet only.

Commands:

```bash
cd /Users/murillo/Dev/tilly-engineer-skills
for t in cursor claude codex; do
  target="/Users/murillo/Dev/tes-canary/$t"
  {
    echo "## $t"
    echo "### git"
    git -C "$target" rev-parse --is-inside-work-tree 2>&1 || true
    git -C "$target" config --get core.hooksPath 2>&1 || true
    echo "### material git gates"
    for p in .git/hooks/pre-commit .git/hooks/pre-push .githooks/pre-commit .githooks/pre-push .husky/pre-commit .husky/pre-push lefthook.yml .pre-commit-config.yaml; do
      [ -e "$target/$p" ] && echo "PRESENT $p" || echo "absent $p"
    done
    echo "### postinstall"
    jq '{version,state,last_status,executed_by,last_run,advisories}' "$target/.tes/postinstall.json"
    echo "### install lock"
    jq '{version,attached_surfaces,apply:.apply.status,stage:.stage.status,certification:.certification.components,negative_checks:.certification.negative_checks}' "$target/.tes/tes-install-lock.json"
    echo "### os residue"
    find "$target" -name '.DS_Store' -o -name '__MACOSX' -o -name '._*' -o -name 'Thumbs.db' | sort
  } | tee -a "$EVIDENCE_DIR/PREFLIGHT.md"
done
```

Run current oracles through Python:

```bash
PY=/opt/homebrew/opt/python@3.14/bin/python3.14
for t in cursor claude codex; do
  target="/Users/murillo/Dev/tes-canary/$t"
  {
    echo "## $t project_context_oracle"
    "$PY" "$target/.tes/bin/project_context_oracle.py" --target "$target" || true
    echo "## $t project_alignment_oracle"
    "$PY" "$target/.tes/bin/project_alignment_oracle.py" --target "$target" || true
    echo "## $t tes_map_oracle"
    "$PY" "$target/.tes/bin/tes_map_oracle.py" --target "$target" || true
  } | tee -a "$EVIDENCE_DIR/PREFLIGHT.md"
done
```

Done when `PREFLIGHT.md` contains enough evidence to classify every finding
below as confirmed, disproven, or changed.

Stop if any target path is missing.

## SPEC-001 - Classify Defects As Source Or Canary State

Objective: prevent target-only patches from hiding package defects.

Required classification:

| Finding | Default Classification | Repair Rule |
|---|---|---|
| Codex hook command uses `git rev-parse` in non-Git canaries | Source defect or documented support collision | Patch package source to use absolute target paths or a safe non-Git fallback; then rematerialize canaries. |
| Cursor context oracle fails due `.DS_Store` source anchor | Source defect plus target residue | Patch generator/oracle/residue policy so OS residue is never a source anchor; clean target. |
| `.DS_Store` exists while `os_residue_absent: true` | Source certification defect plus target residue | Patch residue scan/negative check if it misses current residue; clean target. |
| Claude align omitted `DOCUMENTATION-AUTHORITY.md` and `contracts/**` | Source oracle gap plus target alignment gap | Strengthen source oracle or contract, then repair target mesh. |
| Hook runtime health stale/inconsistent | Source certification/reporting gap plus target evidence gap | Make lock/latest-run semantics truthful; do not use synthetic proof as native observation. |
| Git/pre-push/pre-commit absent | Canary state gap, not TES default install bug by itself | Initialize Git and local hooks only for canary admission, or classify as no-commit/no-precommit. |
| Manifest root-context full-file hashes mismatch due `TES:PROJECT-OVERLAY` wrapper | Source manifest semantics decision | Verify detach/uninstall behavior; patch manifest hash semantics only if reversibility/oracle uses full-file hash incorrectly. |

Produce `FIX-PLAN.md` with one row per finding:

```text
Finding:
Evidence:
Classification: source | canary-state | contract-collision | false-positive
Repair:
Oracle:
Owner decision needed:
```

Do not edit canaries before this classification exists.

## SPEC-002 - Source Fix: Non-Git-Safe Codex Hook Path

Objective: Codex hook config must not be broken in a target that TES itself
allows to complete setup without `.git`.

Required behavior:

- Fresh install into a non-Git target must not write Codex hook commands that
  depend on `git rev-parse --show-toplevel`.
- Preserve/update install must replace TES-owned stale Codex hook commands.
- The generated command may use an absolute target path, a safe environment
  variable if Codex provides one, or a robust shell fallback, but it must run in
  both Git and non-Git targets.
- Non-TES user config in `.codex/config.toml` must be preserved.

Forbidden behavior:

- Do not manually patch only `~/Dev/tes-canary/*/.codex/config.toml`.
- Do not require Git only to make Codex hooks work unless the install contract is
  explicitly changed and all docs/oracles are updated.
- Do not leave `cursor` and `claude` canaries with stale `git rev-parse`
  commands.

Minimum source tests:

```bash
python3 scripts/tes_install.py --self-test
python3 scripts/installed_certification_oracle.py --self-test
python3 scripts/command_trigger_oracle.py --self-test
```

Required target proof after rematerialization:

```bash
rg -n 'git rev-parse --show-toplevel' /Users/murillo/Dev/tes-canary/{cursor,claude,codex}/.codex/config.toml
# Expected: no matches, unless the command includes a proven non-Git fallback.
```

## SPEC-003 - Source Fix: OS Residue Is Not Project Context

Objective: `.DS_Store` and equivalent OS residue must not become anchors,
territory evidence, manifest quality evidence, or green negative checks.

Required behavior:

- `tes_init.py` must not cite `.DS_Store`, `__MACOSX`, AppleDouble `._*`, or
  `Thumbs.db` as project anchors or sample anchors.
- `project_context_oracle.py` must not require OS residue anchors.
- Installed certification must not report `os_residue_absent: true` when residue
  exists under the target.
- Bundle/materialization paths must avoid generating or preserving OS residue.
- Target-local Git exclude must include OS residue before Git admission commits.

Required source tests:

```bash
python3 scripts/tes_init.py --self-test
python3 scripts/project_context_oracle.py --self-test
python3 scripts/installed_certification_oracle.py --self-test
python3 scripts/tes_bundle.py --self-test
```

Required target cleanup:

```bash
find /Users/murillo/Dev/tes-canary/{cursor,claude,codex} \
  \( -name '.DS_Store' -o -name '__MACOSX' -o -name '._*' -o -name 'Thumbs.db' \) -print
```

The final command must print nothing, or the remaining files must be classified
as intentionally outside the proof surface with a reason. For these canaries,
the expected result is no residue.

## SPEC-004 - Source Fix: Alignment Contract And Oracle Symmetry

Objective: `/tes-align` contract and `project_alignment_oracle.py` must agree on
required mesh surfaces.

The contract currently requires:

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
docs/agents/evidence/<timestamp>-project-alignment.md
docs/agents/contracts/**
```

Required behavior:

- If `DOCUMENTATION-AUTHORITY.md` is missing after `/tes-align`, the oracle must
  return `NEEDS_REVIEW` or `FAIL`, unless the contract is explicitly changed.
- If `contracts/**` is missing after `/tes-align`, the oracle must return
  `NEEDS_REVIEW` or `FAIL`, unless the contract is explicitly changed.
- A human/agent cannot mark those required surfaces `deferred` and still claim
  full alignment PASS.
- The Claude canary must be repaired so the required surfaces exist or the
  final admission honestly blocks Goal Maestro.

Required source tests:

```bash
python3 scripts/project_alignment_oracle.py --self-test
python3 scripts/tes_init.py --self-test
```

Required target proof:

```bash
for t in cursor claude codex; do
  target="/Users/murillo/Dev/tes-canary/$t"
  test -s "$target/docs/agents/DOCUMENTATION-AUTHORITY.md"
  find "$target/docs/agents/contracts" -maxdepth 2 -type f | sort
done
```

## SPEC-005 - Source Fix: Hook Health Truthfulness

Objective: hook runtime health must distinguish config, synthetic ledger rows,
and native host observation.

Required behavior:

- `tes_install.py hook-health` and installed certification must not aggregate
  `NEEDS_EVIDENCE` into a plain `PASS` without a visible degraded component.
- A lock file must not remain stale after a recovery run claims a different
  hook health result.
- Synthetic/manual-repair ledger entries must not certify native hook health.
- Cursor execution may certify native Cursor hook evidence only when the Cursor
  host actually fires the hook.
- Codex and Claude Code hook health must be `CONFIGURED_WITHOUT_NATIVE_PROOF`,
  `NEEDS_EVIDENCE`, or equivalent unless those hosts are observed natively.

Required source tests:

```bash
python3 scripts/tes_install.py --self-test
python3 scripts/installed_certification_oracle.py --self-test
```

Required target proof:

```bash
for t in cursor claude codex; do
  target="/Users/murillo/Dev/tes-canary/$t"
  jq '.certification.components.hook_runtime_health' "$target/.tes/tes-install-lock.json"
  run="$(jq -r '.last_run' "$target/.tes/postinstall.json")"
  jq '.certification.components.hook_runtime_health' "$target/$run"
  tail -n 20 "$target/.tes/runtime/hooks/executed.jsonl" 2>/dev/null || true
done
```

The final report must classify each host:

```text
Cursor native: PASS | NEEDS_EVIDENCE | BLOCKED
Codex native: PASS | CONFIGURED_NOT_OBSERVED | NEEDS_EVIDENCE | BLOCKED
Claude native: PASS | CONFIGURED_NOT_OBSERVED | NEEDS_EVIDENCE | BLOCKED
```

Do not collapse this into one unqualified PASS.

## SPEC-006 - Canary State Fix: Git Admission

Objective: make each canary a Git-backed target so Field Reports `pre-push`,
local commit evidence, and optional pre-commit enforcement can be materially
proved before Goal Maestro.

This SPEC grants owner authorization for local canary Git initialization and
local canary hooks only. It does not authorize changing TES default adopter
install behavior.

For each canary:

```bash
for t in cursor claude codex; do
  target="/Users/murillo/Dev/tes-canary/$t"
  cd "$target"
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git init
  fi
  git config user.name "TES Canary"
  git config user.email "tes-canary@example.invalid"
  {
    echo ".DS_Store"
    echo "**/.DS_Store"
    echo "__MACOSX/"
    echo "._*"
    echo "Thumbs.db"
    echo ".tes/setup/"
    echo ".tes/bk/"
    echo ".tes/cortex/"
    echo ".tes/field-reports/"
    echo ".tes/runtime/"
    echo "**/__pycache__/"
    echo "*.pyc"
  } >> .git/info/exclude
  awk '!seen[$0]++' .git/info/exclude > .git/info/exclude.tmp
  mv .git/info/exclude.tmp .git/info/exclude
done
```

After Git exists, install or repair Field Reports `pre-push`:

```bash
for t in cursor claude codex; do
  target="/Users/murillo/Dev/tes-canary/$t"
  PY=/opt/homebrew/opt/python@3.14/bin/python3.14
  "$PY" "$target/.tes/bin/field_reports.py" install-hook --target "$target"
  "$PY" "$target/.tes/bin/field_reports.py" status --target "$target"
done
```

Expected:

- `git rev-parse --is-inside-work-tree` returns `true`.
- Active `pre-push` hook exists at `.git/hooks/pre-push` unless `core.hooksPath`
  is set.
- `field_reports.py status` is `PASS`, `DISABLED`, or an exact blocker. For
  Goal Maestro admission, expected state is `PASS`.

## SPEC-007 - Canary State Fix: Local Persistent Pre-Commit Gate

Objective: provide material pre-commit enforcement only if the downstream run
will claim `precommit_enforced`.

This local hook is for canary admission. It is not a TES installer default.

Install this minimal local `.git/hooks/pre-commit` in each canary after source
and target repairs:

```sh
#!/bin/sh
set -eu
PY="${PYTHON:-/opt/homebrew/opt/python@3.14/bin/python3.14}"
if [ ! -x "$PY" ] && ! command -v "$PY" >/dev/null 2>&1; then
  PY="python3"
fi
"$PY" .tes/bin/project_context_oracle.py --target .
"$PY" .tes/bin/project_alignment_oracle.py --target .
"$PY" .tes/bin/tes_map_oracle.py --target .
git diff --check
```

Then:

```bash
for t in cursor claude codex; do
  target="/Users/murillo/Dev/tes-canary/$t"
  chmod +x "$target/.git/hooks/pre-commit"
  test -x "$target/.git/hooks/pre-commit"
  git -C "$target" hook run pre-commit
done
```

Expected:

- Hook exists and is executable.
- `git hook run pre-commit` exits `0` in all three canaries.
- `docs/agents/QUALITY-GATES.md` in each canary describes this as a local
  canary gate or removes stale `needs_review` language.

If the hook is not installed, the final state must be:

```text
precommit_enforced: false
commit_mode: manual/no-precommit
Goal Maestro admission: blocked for any claim requiring precommit_enforced
```

## SPEC-008 - Rematerialize Or Repair Canaries Without Manual Drift

Objective: after source fixes, apply them to canaries through deterministic TES
scripts, not one-off edits.

Allowed target writes:

- Removal of OS residue.
- Git initialization and local Git hooks.
- Re-running installed/source TES scripts to regenerate or repair installed
  surfaces.
- Mesh repairs required by the source contract.
- Evidence packet updates.

Forbidden target writes:

- Hand editing only one target to make it pass while source remains wrong.
- Editing `.tes/tes-install-lock.json` manually.
- Editing `.tes/postinstall.json` manually.
- Creating synthetic hook ledger rows and calling them native proof.
- Removing user-authored content without backup. These canaries are test
  targets, but still treat existing content as owned evidence.

Preferred repair routes:

1. Apply source package fixes.
2. Build/stage/apply through existing package mechanisms when the defect is in
   installed runtime materialization.
3. Rerun installed oracles.
4. Only then perform narrow mesh repair for canary-specific `docs/agents/**`
   gaps.

When using installed helpers:

```bash
PY=/opt/homebrew/opt/python@3.14/bin/python3.14
for t in cursor claude codex; do
  target="/Users/murillo/Dev/tes-canary/$t"
  "$PY" "$target/.tes/bin/project_context_oracle.py" --target "$target"
  "$PY" "$target/.tes/bin/project_alignment_oracle.py" --target "$target"
  "$PY" "$target/.tes/bin/tes_map_oracle.py" --target "$target"
done
```

When using source helpers for external targets:

```bash
cd /Users/murillo/Dev/tilly-engineer-skills
for t in cursor claude codex; do
  target="/Users/murillo/Dev/tes-canary/$t"
  python3 scripts/project_context_oracle.py --target "$target"
  python3 scripts/project_alignment_oracle.py --target "$target"
  python3 scripts/tes_map_oracle.py --target "$target"
done
```

## SPEC-009 - Baseline Canary Commit

Objective: give Goal Maestro a clean Git baseline in each canary.

Only after all canary oracles and local hooks pass:

```bash
for t in cursor claude codex; do
  target="/Users/murillo/Dev/tes-canary/$t"
  cd "$target"
  git status --short --untracked-files=all
  git add -A
  git status --short --untracked-files=all
  git commit -m "chore: establish TES canary baseline before goal maestro"
done
```

Rules:

- Do not commit `.DS_Store`, `.tes/setup/**`, `.tes/bk/**`, `.tes/cortex/**`,
  `.tes/field-reports/**`, `.tes/runtime/**`, `__pycache__`, or `*.pyc`.
- If any excluded file appears in `git status`, stop and repair exclude/cleanup.
- If there is nothing to commit, record the existing HEAD and continue.
- This is local canary Git evidence only. It is not a package release, not a
  remote publication, and not proof that TES default installer creates Git.

## SPEC-010 - Final Recertification Matrix

Objective: produce a single admission matrix that can be handed to the later
Goal Maestro window.

For each canary, record:

```bash
target="/Users/murillo/Dev/tes-canary/<cursor|claude|codex>"
git -C "$target" rev-parse --is-inside-work-tree
git -C "$target" rev-parse --short HEAD
git -C "$target" status --short --untracked-files=all
test -x "$target/.git/hooks/pre-commit"
test -x "$target/.git/hooks/pre-push"
PY=/opt/homebrew/opt/python@3.14/bin/python3.14
"$PY" "$target/.tes/bin/project_context_oracle.py" --target "$target"
"$PY" "$target/.tes/bin/project_alignment_oracle.py" --target "$target"
"$PY" "$target/.tes/bin/tes_map_oracle.py" --target "$target"
"$PY" "$target/.tes/bin/field_reports.py" status --target "$target"
"$PY" "$target/.tes/bin/tes_install.py" hook-health --target "$target" --json-only --agent cursor
jq '{state,last_status,last_run,advisories}' "$target/.tes/postinstall.json"
jq '{version,attached_surfaces,components:.certification.components,negative_checks:.certification.negative_checks}' "$target/.tes/tes-install-lock.json"
find "$target" \( -name '.DS_Store' -o -name '__MACOSX' -o -name '._*' -o -name 'Thumbs.db' \) -print
```

Expected final matrix:

| Canary | Git | Pre-push | Pre-commit | Context | Align | Map | OS residue | Active host hook | Admission |
|---|---|---|---|---|---|---|---|---|---|
| `cursor` | PASS | PASS | PASS | PASS | PASS | PASS | none | Cursor-native PASS or exact blocker | GO/BLOCKED |
| `claude` | PASS | PASS | PASS | PASS | PASS | PASS | none | Configured-not-observed unless native Claude run occurs | GO/BLOCKED |
| `codex` | PASS | PASS | PASS | PASS | PASS | PASS | none | Configured-not-observed unless native Codex run occurs | GO/BLOCKED |

Admission for Goal Maestro in Cursor is `GO` only if:

- `cursor` canary has Git, `pre-push`, local `pre-commit`, context PASS,
  alignment PASS, map PASS, no OS residue, and Cursor-native hook proof or a
  consciously accepted `configured-not-observed` downgrade.
- `claude` and `codex` canaries are at least materially clean and truthful:
  context PASS, alignment PASS, map PASS, Git-backed gates present, no OS
  residue, and no false native hook claim.
- The final report says exactly which canary will be used for the first Goal
  Maestro run.

If `precommit_enforced` is required by the later Goal Maestro execution, all
three local pre-commit hooks must pass before admission.

## SPEC-011 - Package Source Gates

Objective: if package source changes were made, verify source quality before
declaring the fix reusable.

Run focused gates for touched surfaces:

```bash
cd /Users/murillo/Dev/tilly-engineer-skills
python3 scripts/tes_init.py --self-test
python3 scripts/project_context_oracle.py --self-test
python3 scripts/project_alignment_oracle.py --self-test
python3 scripts/tes_map_oracle.py --self-test
python3 scripts/tes_install.py --self-test
python3 scripts/installed_certification_oracle.py --self-test
python3 scripts/field_reports.py --self-test
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/tes_bundle.py --self-test
python3 scripts/private_vocabulary_oracle.py
python3 scripts/validate_tds.py
python3 scripts/validate_reference_graph.py
python3 scripts/validate_doc_size.py
git diff --check
npm run commit:check
```

If a command is missing or not applicable, record the exact reason. Do not hide
it under "not run".

If delivered behavior changes, add a version/release decision:

```text
Version decision: required | deferred by owner | not required
Reason:
Files that changed delivered behavior:
Release gates run:
Release gates blocked:
```

Do not bump, tag, push, publish, or release unless the owner explicitly
authorizes that separate action.

## SPEC-012 - Final Report Contract

Objective: make the handoff usable by another Goal Maestro execution window.

The final response and `FINAL-ADMISSION.md` must contain:

```text
Status: READY_FOR_GOAL_MAESTRO_CANARY | BLOCKED
Execution host: Cursor
Primary target for next run:
Canary matrix:
Source changes:
Target changes:
Git/pre-push/pre-commit proof:
Context/alignment/map proof:
Hook proof classification:
OS residue proof:
Remaining downgrades:
Forbidden claims:
Journal:
Next exact command or prompt:
```

Forbidden final claims:

- "All hooks PASS" unless native evidence exists for every claimed host.
- "Pre-commit enforced" unless a material executable hook exists and
  `git hook run pre-commit` passes.
- "Field Reports active" unless `field_reports.py status` and the active
  `pre-push` hook prove it.
- "Clean install fixed" if only one canary was manually patched.
- "Goal Maestro ready" if `project_context_oracle.py`, `project_alignment_oracle.py`,
  or `tes_map_oracle.py` fails on the selected target.
- "Package fixed" if only installed canary mirrors changed.

## Implementation Order

1. SPEC-000: capture read-only preflight evidence.
2. SPEC-001: classify each defect.
3. SPEC-002 to SPEC-005: patch package source for portable defects.
4. SPEC-011 focused source gates for touched source surfaces.
5. SPEC-006 and SPEC-007: initialize Git and local gates in canaries.
6. SPEC-008: rematerialize/repair canaries through deterministic routes.
7. SPEC-010: run final canary matrix.
8. SPEC-009: create local baseline commits after gates pass.
9. SPEC-010 again: prove clean post-commit status.
10. SPEC-012: write final admission report.

Do not reorder Git baseline before canary gates. Do not run Goal Maestro inside
this SPEC.

## Completion Criteria

The SPEC closes green only with:

- Evidence packet retained under `docs/evidence/reports/2026/06/30/**`.
- Detailed `JOURNAL.md` retained, current, and sufficient for audit from this
  window without trusting the final prose.
- `cursor`, `claude`, and `codex` canaries Git-backed or explicitly blocked.
- Field Reports `pre-push` materialized or explicitly blocked.
- Local pre-commit materialized and passing when enforcement is required.
- No `.DS_Store` or equivalent OS residue in proof surfaces.
- `project_context_oracle.py --target` PASS for all three.
- `project_alignment_oracle.py --target` PASS for all three.
- `tes_map_oracle.py --target` PASS for all three.
- `DOCUMENTATION-AUTHORITY.md` and `docs/agents/contracts/**` present in all
  three, unless the source contract is deliberately changed and indexed.
- Codex hook command path safe for non-Git targets in all three.
- Hook runtime health classified without false native cross-host claims.
- Package source gates run when source changed.
- Final admission explicitly says which target is safe for the next Cursor Goal
  Maestro run.

If any item is not true, close as `BLOCKED` with the exact stop state.
