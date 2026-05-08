---
tds_id: evidence.context_mesh.independent_canary_convergence_2026_05_08_journal
tds_class: evidence
status: active
consumer: TES maintainers and certification reviewers
source_of_truth: false
evidence_level: L3
---

# Independent Canary Convergence Journal - 2026-05-08

Run root: `/Users/murillo/Dev/tes-canaries/runs/20260508T135126Z/`

Prompt path: `docs/install/INDEPENDENT-CANARY-CONVERGENCE.prompt.md`

Prompt version: `0.1.0`

Prompt SHA-256: `d38f4b3fb469b0ccf1c186c9b96b896c1ea35a50d269c416fecffb42407b2eaf`

Starting TES HEAD: `2026990417787f85960ff70dc06852c98863b0a4`

Starting branch/upstream: `main` / `origin/main`

Starting worktree: clean; branch ahead of upstream by one commit.

## [2026-05-08T13:51:26Z] loop | Step Zero and authority frame

- Hypothesis: TES can be certified or improved through independent disposable canaries without treating any single target as the product mold.
- Canary or fixture: TES repository baseline and required source-of-truth documents.
- TES commit: `2026990417787f85960ff70dc06852c98863b0a4`
- Prompt version: `0.1.0`
- Command(s): `git status --short --branch --untracked-files=all`; `git log -8 --oneline`; `git rev-parse HEAD`; `git branch --show-current`; `git rev-parse --abbrev-ref --symbolic-full-name @{u}`; `shasum -a 256 docs/install/INDEPENDENT-CANARY-CONVERGENCE.prompt.md`; targeted reads of required docs.
- Observed result: repo is clean on `main`, ahead of `origin/main` by one commit; prompt hash recorded; package authorities confirm `src/**` as adapter source and `docs/**` as governed explanation.
- Failure/gap/bug: none yet; the first material risk is false closure from rerunning prior canaries without adding stronger adversarial coverage.
- Decision: proceed with canary execution and append evidence after each loop.
- Patch or no-patch reason: journal created as required durable output before the first canary.
- Regression gate: first canary must run installed `.tes/bin/tes_init.py`, project context oracle, and `tes_update.py plan --json-only`.
- Evidence promoted: durable journal path and run root.
- Residual risk: network cloning may block a specific public repository; if so, classify the affected canary as `BLOCKED` and use another repository only when it covers the same surface.

## [2026-05-08T13:53:34Z] loop | Real canary installed-helper initialization

- Hypothesis: The current package can initialize diverse real projects through installed `.tes/bin/tes_init.py`, not only through source-tree helpers.
- Canary or fixture: `pypa/sampleproject`, `sindresorhus/ky`, `pallets/click`, `expressjs/express`, `hashicorp-education/learn-terraform-import`, and a `sampleproject` clone with simulated project-owned `AGENTS.md`, `CLAUDE.md`, and `.cursor/rules/project-owned.mdc`.
- TES commit: `2026990417787f85960ff70dc06852c98863b0a4`
- Prompt version: `0.1.0`
- Command(s): `git clone --depth 1 ...`; `python3 scripts/install_mcp.py --target <canary> --adapter all --helpers-only --yes --json-only`; `python3 <canary>/.tes/bin/tes_init.py --target <canary> --yes`.
- Observed result: all six installed helper initializations returned `PASS`; file counts were sampleproject `12`, Ky `67`, Click `149`, Express `213`, Terraform `7`, owned bootloaders `15`.
- Failure/gap/bug: no runtime crash or bootstrap-only context; owned bootloaders correctly reported root context as `PRESERVED` during gate execution rather than overwriting local governance.
- Decision: proceed to project-context oracle and update-planner probes.
- Patch or no-patch reason: no TES product patch from this loop; the generated target files remain disposable canary output.
- Regression gate: `project_context_oracle.py --target <canary>` and installed `tes_update.py plan --target <canary> --json-only`.
- Evidence promoted: installed-helper execution across Python, TypeScript, Node, Terraform, and project-owned governance surfaces.
- Residual risk: `tes_init.py` gate table includes installed `.tes/bin/**` command paths as certification evidence; this is acceptable if `.tes/bin/**` does not appear in Source Anchors or Recommended Deep Reads.

## [2026-05-08T13:54:20Z] loop | Project-context and update-planner probes

- Hypothesis: `/tes-init` leaves a useful, auditable project map and `/tes-update` honestly reports current/drift state.
- Canary or fixture: all six initialized canaries.
- TES commit: `2026990417787f85960ff70dc06852c98863b0a4`
- Prompt version: `0.1.0`
- Command(s): `python3 scripts/project_context_oracle.py --target <canary>`; `python3 <canary>/.tes/bin/tes_update.py plan --target <canary> --json-only --timeout 15`.
- Observed result: project context oracle returned `PASS` for all six. Online update planner returned `CURRENT` with `helper_contract_status=PASS`, `project_context_status=PASS`, and `recommended_update_scope=none` for sampleproject, Ky, Click, Express, and Terraform.
- Failure/gap/bug: before adapter materialization, the owned-governance canary correctly reported `runtime_trigger_status=DRIFT` and `recommended_update_scope=adapter-config`; this was not a code bug, but evidence that helpers-only install is not a full runtime surface.
- Decision: run adapter materialization on the owned-governance canary and re-probe.
- Patch or no-patch reason: no TES source patch; the required repair was running the shipped adapter installer in the disposable target.
- Regression gate: `install_adapter.py --adapter all --target <owned> --yes`; repeat project-context oracle and installed update planner.
- Evidence promoted: update planner distinguishes helpers-only state from full adapter trigger parity without false `CURRENT`.
- Residual risk: local TES HEAD is one commit ahead of `origin/main`; online helper freshness checks compare installed helpers to remote commit `c7147c47038c66e30d214af2bb8f779f40fc8afb`, while this run records local starting HEAD separately.

## [2026-05-08T13:55:18Z] loop | Adapter materialization with project-owned governance

- Hypothesis: TES can add non-conflicting Codex, Claude, and Cursor assets while preserving project-owned root governance.
- Canary or fixture: `/Users/murillo/Dev/tes-canaries/runs/20260508T135126Z/owned-bootloaders`.
- TES commit: `2026990417787f85960ff70dc06852c98863b0a4`
- Prompt version: `0.1.0`
- Command(s): `python3 scripts/install_adapter.py --adapter all --target <owned> --yes`; `python3 scripts/project_context_oracle.py --target <owned>`; `python3 <owned>/.tes/bin/tes_update.py plan --target <owned> --json-only --timeout 15`; `python3 scripts/root_context.py analyze --target <owned>`.
- Observed result: adapter install returned `INSTALLED_WITH_PRESERVED_CONFLICTS`, preserving project-owned `AGENTS.md` and `CLAUDE.md` while copying TES-owned `.agents/**`, `.claude/**`, `skills/**`, `.claude-plugin/**`, `CURSOR.md`, and `.cursor/rules/tes-guidelines.mdc`. Re-probe returned `runtime_trigger_status=PASS`, `update_status=CURRENT`, and `recommended_update_scope=none`.
- Failure/gap/bug: none requiring TES source change; `root_context.py` still reports `NEEDS_REVIEW` because project-owned root context remains intentionally preserved.
- Decision: classify adapter materialization and local governance preservation as certified for this run.
- Patch or no-patch reason: no product patch; behavior matched contract.
- Regression gate: final focused gates and `npm run commit:check`.
- Evidence promoted: preserved-conflict route plus post-adapter update planner `CURRENT`.
- Residual risk: project-owned bootloader content itself is intentionally not merged into TES root files during this run; a real installation would still need a human merge plan for root bootloader prose if the user wants root-trigger text inside those files.

## [2026-05-08T13:59:40Z] loop | Closure gates

- Hypothesis: The evidence package can close under the repository's full commit gate after TDS registration.
- Canary or fixture: TES repository focused gates and `npm run commit:check`.
- TES commit: `2026990417787f85960ff70dc06852c98863b0a4`
- Prompt version: `0.1.0`
- Command(s): required focused gates; `python3 scripts/validate_tds.py`; `python3 scripts/validate_reference_package.py`; `npm run commit:check`.
- Observed result: focused gates passed. First broad closure attempt failed at `--staged-ready` because new evidence files were untracked. After staging only the journal, report, and TDS index, `npm run commit:check` passed.
- Failure/gap/bug: TDS/reference validation initially failed until the new journal/report were indexed; staged-ready initially failed until the evidence files were staged.
- Decision: GO after final evidence update and a confirming closure rerun.
- Patch or no-patch reason: evidence and TDS index only; no product source patch was required.
- Regression gate: repeat `npm run commit:check` after this final journal/report update.
- Evidence promoted: final gate output and staged evidence package.
- Residual risk: local branch remains ahead of `origin/main`; no push, tag, release, or marketplace action was performed in this run.
