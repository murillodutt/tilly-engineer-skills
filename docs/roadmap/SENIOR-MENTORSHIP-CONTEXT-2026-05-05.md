---
tds_id: roadmap.senior_mentorship_context_2026_05_05
tds_class: roadmap
status: archived
consumer: next certification session
source_of_truth: false
evidence_level: L2
---

# Senior Mentorship Context 2026-05-05

This context is for the next engineering window working on
`/Users/murillo/Dev/tilly-engineer-skills`.

It aligns the current repository state with the senior feedback: stop expanding
surface area, freeze what exists, and certify the package responsibly before
claiming v1 behavior.

## Executive Direction

The team should not treat version `0.1.0` as a small or immature artifact. The
package can be a v1 release candidate in spirit while the package version stays
`0.1.0`. The reason for keeping `0.1.0` is governance: certify the existing
system before elevating it.

The next work is not "build a benchmark framework." The benchmark runner,
TDS, adapter materialization, governance docs, and local gates already exist.
The next work is certification.

The key question is:

```text
Which claim does this evidence have the right to make?
```

Do not claim behavioral certification from fixture evidence. Do not claim
section-level rent from a single trigger per gate. Do not claim a certified
Git state while running on uncommitted staged content unless the evidence
manifest records the tree or staged diff.

## Current Verified State

The repository currently contains a large staged patch that reorganizes the
project into a reference package:

| Area | Current state |
|------|---------------|
| Canonical adapter source | `src/adapters/**` |
| People-facing method and governance docs | `docs/**` |
| Eval dataset | `benchmarks/context-mesh/eval-dataset.json` |
| Planner | `scripts/context_mesh_plan.py` |
| Evidence runner | `scripts/context_mesh_run.py` |
| Adapter materializer | `scripts/materialize_adapter.py` |
| TDS validator | `scripts/validate_tds.py` |
| Reference validator | `scripts/validate_reference_package.py` |
| Generated install trees | `dist/adapters/**`, ignored |

Local checks run by Codex mentoring session:

| Command | Result |
|---------|--------|
| `npm run benchmark:plan` | PASS, `planned_calls=26` |
| `npm run benchmark:run -- --dry-run` | PASS, `matrix_calls=26`, `plan_parity=true` |
| `npm run validate` | PASS, `checked_files=37` |
| `npm run tds:validate` | PASS, `documents=15` before this document |
| `npm run materialize:check` | PASS, adapters `claude=4`, `codex=6`, `cursor=2` |
| `npm run oracle:self-test` | PASS |
| `git diff --check && git diff --cached --check` | PASS |
| `npm run commit:check` | PASS |

Additional non-mutating evidence runs were written under `/tmp`, not into the
repo:

| Backend | Command shape | Result |
|---------|---------------|--------|
| `fixture` | `python3 scripts/context_mesh_run.py --backend fixture --out-root /tmp/tilly-context-mesh-cert-check --run-id codex-mentorship-fixture --no-tds-index` | `certification_status=GO`, 26 executed |
| `echo` | `python3 scripts/context_mesh_run.py --backend echo --out-root /tmp/tilly-context-mesh-cert-check --run-id codex-mentorship-echo --no-tds-index` | pipeline PASS, `certification_status=NO-GO` |

This is good evidence that the runner can both certify and reject. It is not
yet evidence that a live model behaves correctly.

## The Main Mentorship Correction

The plan that says "add the runner" is stale. The runner already exists.

The correct next posture is:

```text
Freeze -> commit -> certify pipeline -> add/activate real backend -> certify behavior.
```

Do not add Promptfoo, HTML reports, LLM judge, N=3, or more adapter machinery
until the current staged patch is sealed and the evidence claims are classified.

## Certification Classes

Use two distinct certification labels.

| Label | May be claimed now? | Meaning |
|-------|---------------------|---------|
| `pipeline-v1-rc` | Yes, after committed evidence run | Planner, runner, raw evidence, report, thresholds, TDS, and NO-GO mechanics work |
| `behavior-v1-rc` | No | A real backend shows the context mesh changes behavior correctly without distractor leaks |

Never collapse these labels into a single generic `GO`.

Fixture `GO` means the evidence machine behaves. It does not mean a model has
been behaviorally improved.

## Immediate P0: Commit Or Tree Hash

The repository currently has staged changes. `context_mesh_run.py` records
`git_head`, but `git_head` points at the last commit, not necessarily the staged
tree being executed.

Therefore, a retained certification run before commit is ambiguous.

There are two acceptable paths:

1. Commit the staged patch first, then run retained certification.
2. Add `tree_sha` or `staged_diff_sha` to the manifest before retaining a run.

The simpler path is commit first.

Recommended first commands:

```bash
cd /Users/murillo/Dev/tilly-engineer-skills
git status --short --branch --untracked-files=all
npm run commit:check
git diff --cached --stat
```

If still green, seal the patch with a semantic local commit. Do not push unless
explicitly authorized.

## Pipeline Certification Procedure

After the patch is committed, run a retained pipeline certification:

```bash
npm run benchmark:run -- --backend fixture
npm run tds:validate
npm run commit:check
```

Expected evidence shape:

```text
docs/evidence/reports/context-mesh/<run-id>/
  manifest.json
  raw.ndjson
  summary.json
  REPORT.md
  graders-sha.json
```

The report may claim `pipeline-v1-rc` if:

| Metric | Required |
|--------|----------|
| `plan_run_parity` | `1.0` |
| `raw_evidence_coverage` | `1.0` |
| `distractor_leak_rate` | `0` |
| `all_failures_have_excerpt` | `true` |
| `dataset_sha_present` | `true` |
| `git_head_present` | `true` and points to committed package state |
| `backend_declared` | `true` |
| `grader_version_declared` | `true` |
| `grader_sha_present` | `true` |
| `evidence_limits_declared` | `true` |

The report must explicitly state the evidence limit:

```text
Fixture backend certifies pipeline and evidence mechanics only. It does not
certify live-model behavior.
```

## Behavioral Certification Procedure

Only after `pipeline-v1-rc` is retained should the team add or activate a real
backend.

The real backend should be isolated behind the existing backend interface. It
must not mix provider calls with grading, summary writing, TDS indexing, or
report rendering.

Minimal target:

```text
backend = claude-cli
samples = 1
judge = deterministic expected/forbidden
no LLM judge
no Promptfoo
no HTML
no N=3
```

`behavior-v1-rc` may be claimed only if:

| Metric | Required |
|--------|----------|
| `trigger_pass_rate_full` | greater than `trigger_pass_rate_none` |
| `distractor_leak_rate` | `0` |
| all failed samples | have excerpt and reasons |
| dataset hash | present and stable |
| grader hash | present and stable |
| backend/model | declared |
| evidence limits | explicit |

If `full <= none`, this is NO-GO unless the report retains a clear explanation
and does not claim behavioral success.

## Ablation Interpretation

The current dataset has one trigger eval per gate. That means each gate can
only produce maximum `loss=1`.

Per `docs/evals/EVALS.md`, `loss=1` means:

```text
adversarial_follow_up_required
```

So the current dataset can prove that the pipeline computes ablation losses.
It cannot yet make a strong rent claim per gate.

Do not inflate the dataset broadly. Add adversarial follow-ups only where the
real backend produces ambiguous `loss=1` or unexpected results.

Each new adversarial eval must include:

| Field | Required meaning |
|-------|------------------|
| `id` | stable eval id |
| `kind` | `trigger` |
| `target_section` | one of the four gates |
| `prompt` | plausible request that tempts violation |
| `expected` | observable desired behavior |
| `forbidden` | observable betrayal |
| reason in docs/report | why this eval was added |

## NO-GO Conditions

Stop certification if any of these occurs:

- `run` diverges from `plan`.
- Any raw sample lacks output, prompt hash, output hash, grader hash, or excerpt.
- Any failed sample lacks audit excerpt.
- Dataset changes without a new dataset hash in the report.
- Grader changes without new `grader_sha` and version.
- Report says `GO` without evidence limits.
- Fixture evidence is presented as live behavior evidence.
- Real backend has confirmed distractor leak.
- `git_head` does not identify the content being certified.

## Adapter Cohesion Guidance

Adapter parity is behavioral, not textual.

| Adapter | Correct shape |
|---------|---------------|
| Codex | `AGENTS.md` plus progressive skill in `.agents/skills/**` after materialization |
| Claude | `CLAUDE.md`, `.claude-plugin/**`, and `skills/**` after materialization |
| Cursor | `CURSOR.md` plus `.cursor/rules/*.mdc` |

Do not force symmetry that the tools do not natively share. The common truth is
the four behavioral gates, not identical packaging.

The current materializer already proves structural adapter output. Behavioral
adapter parity is a later certification step and should run the same matrix
through each adapter only after the live backend path is stable.

## What Not To Do Next

- Do not add LLM judge before deterministic grading is certified with a real backend.
- Do not add Promptfoo as source of truth.
- Do not add HTML reports.
- Do not add N=3 before one-sample behavior certification is understood.
- Do not publish packages or plugins.
- Do not add hooks, MCP servers, or subagents to the default package.
- Do not create `CHANGELOG.md`.
- Do not rewrite the repository structure again unless a validator proves it wrong.

## Suggested Mentoring Message To The Team

```text
The runner exists. The next session is not construction; it is certification.
First commit the current package shape so evidence points at a real Git state.
Then retain fixture evidence as pipeline-v1-rc only. Do not call it behavioral
certification. After that, add or activate a claude-cli backend as an isolated
adapter and run one-sample behavior-v1-rc. Because the dataset has one trigger
per gate, every loss=1 is a request for adversarial follow-up, not a strong
rent claim. Stop adding surfaces until the report can honestly say what it
proves and what it does not prove.
```

## Reentry Checklist

1. Confirm current Git state.
2. Run `npm run commit:check`.
3. Commit current staged patch if green.
4. Run fixture certification into governed evidence.
5. Confirm TDS index includes the generated evidence report.
6. State the certification class as `pipeline-v1-rc`.
7. Add or activate `claude-cli` backend only after the pipeline evidence is retained.
8. Run one-sample real backend certification.
9. Inspect losses and distractors.
10. Add adversarial follow-ups only for ambiguous gates.

## Final Principle

The team should not ask "what should we build next?" until it can answer:

```text
What claim can the current evidence make without exaggeration?
```

That question is the governance kernel for this phase.
