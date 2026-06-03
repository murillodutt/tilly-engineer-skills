---
tds_id: install.independent_canary_convergence_prompt
tds_class: adapter
tver: 0.1.1
status: active
consumer: second-window TES convergence operators, maintainers, and certification reviewers
source_of_truth: true
evidence_level: L2
---

# Independent Canary Convergence Prompt

Prompt version: `0.1.1`

Purpose: start a clean, independent TES convergence window that tests the
published package against real projects, records a journal, converts findings
into portable product improvements, and closes only with objective gates.

## Versioning Contract

- Keep this prompt as the source prompt for independent canary runs.
- Each execution must record:
  - TES Git HEAD;
  - prompt path;
  - prompt version;
  - prompt SHA-256;
  - canary run root;
  - durable journal path;
  - final report path.
- If a run discovers that the prompt itself caused ambiguity or missed a useful
  instruction, update this file in a new commit and bump `Prompt version`.
- Do not edit completed run journals to fit a later prompt version. Add a new
  run section or new report instead.

## Expected Durable Outputs

Each independent run must create:

- `docs/evidence/reports/context-mesh/independent-canary-convergence-YYYY-MM-DD/JOURNAL.md`
- `docs/evidence/reports/context-mesh/independent-canary-convergence-YYYY-MM-DD/REPORT.md`

Each run may also create local disposable files under:

- `~/Dev/tes-canaries/runs/YYYYMMDDTHHMMSSZ/`

The durable journal/report live in the TES repository. The local canary run
root is disposable and must not become product truth.

Before creating canary clones, create or update the sandbox `.gitignore` at
`~/Dev/tes-canaries/.gitignore` so local journals, run indexes,
logs, clones, and transient tool layers remain untracked by default. Do not
ignore governed evidence under `docs/evidence/**`; promotion into that tree is
the explicit audit boundary.

## Copyable Prompt

```text
You are working on the Tilly Engineer Skills repository, not on a target
project.

Primary objective:
Execute an independent, evidence-driven convergence loop for TES as a portable
agent product. Do not assume the current package is correct. Prove, refute, or
improve it through real Build-Test-Fail-Fix loops in disposable sandboxes.

Repository and sandbox:
- TES repository: ~/Dev/tilly-engineer-skills
- Canary sandbox root: ~/Dev/tes-canaries
- Put all new canary clones under:
  ~/Dev/tes-canaries/runs/<UTC_RUN_ID>/
- Before cloning, ensure `~/Dev/tes-canaries/.gitignore` ignores
  `RUN-INDEX.md`, local `JOURNAL.md`/`REPORT.md`, `_logs/`, `runs/`, `.tes/`,
  `.codex/`, `.claude/`, `.cursor/`, `.vscode/`, and `.mcp.json`.
- Do not commit or push from canary repositories.
- Do not treat any canary as the TES design mold.
- Promote only portable findings back into the TES repository.

Start by reading:
- AGENTS.md
- docs/INDEX.md
- docs/architecture/PROJECT-STRUCTURE.md
- docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md
- docs/install/COMMAND-TRIGGERS.md
- docs/install/INDEPENDENT-CANARY-CONVERGENCE.prompt.md
- docs/adapters/PLATFORM-DIFFERENCES.md
- docs/tds/DOCS-INDEX.yml
- docs/evidence/reports/context-mesh/project-context-real-canaries-2026-05-08/REPORT.md

Step Zero:
- Run `git status --short --branch --untracked-files=all`.
- Record current branch, HEAD, upstream, dirty/staged/untracked state.
- If TES is dirty at start, preserve user changes and record the state in the
  journal before editing.
- Compute and record the SHA-256 of
  `docs/install/INDEPENDENT-CANARY-CONVERGENCE.prompt.md`.

Create a durable journal before the first canary:
- Path:
  docs/evidence/reports/context-mesh/independent-canary-convergence-YYYY-MM-DD/JOURNAL.md
- Include TDS frontmatter:
  tds_id: evidence.context_mesh.independent_canary_convergence_YYYY_MM_DD_journal
  tds_class: evidence
  status: active
  consumer: TES maintainers and certification reviewers
  source_of_truth: false
  evidence_level: L3
- Append after every loop. Do not wait until the end.

Journal entry format:
## [UTC timestamp] loop | <short title>

- Hypothesis:
- Canary or fixture:
- TES commit:
- Prompt version:
- Command(s):
- Observed result:
- Failure/gap/bug:
- Decision:
- Patch or no-patch reason:
- Regression gate:
- Evidence promoted:
- Residual risk:

Mission surfaces:
Validate and improve all material TES characteristics, including:
- assisted context installer;
- `/tes-init` as actual project initialization;
- `docs/agents/PROJECT-CONTEXT.md` as useful, persistent, auditable context;
- `project_context_oracle.py`;
- `tes_update.py` planner honesty;
- command triggers and `/tes:*` compatibility intents;
- Codex, Claude, and Cursor adapter routing;
- preservation of local project governance;
- Cortex;
- MCP;
- Field Reports;
- install smoke;
- TDS/doc governance;
- adapter materialization;
- platform surface certification;
- rollback and Git safety.

Build-Test-Fail-Fix loop:
1. Build: state a concrete hypothesis or product claim.
2. Test: use a fixture or real canary.
3. Fail: actively look for false greens, shallow context, pollution, drift,
   broken routing, missing evidence, and runtime errors.
4. Fix: apply the smallest portable TES patch.
5. Gate: convert the finding into an oracle, fixture, doc, or evidence entry.
6. Certify: run focused gates before broad gates.
7. Journal: append objective evidence immediately.
8. Repeat until remaining issues are either fixed or honestly classified as
   BLOCKED/DEFERRED with reason.

Minimum real canaries:
- pypa/sampleproject
- sindresorhus/ky
- pallets/click
- expressjs/express
- one public Terraform/docs-config repository
- one canary with simulated project-owned AGENTS.md, CLAUDE.md, and Cursor rule

Optional additional canaries:
- add any public repository that exposes a new class of risk, such as Go, Rust,
  monorepo, docs-only, non-English README, unusual root layout, or existing
  agent governance.

For each canary:
1. Clone a clean copy under the current run root.
2. Install the current TES package from the local TES repository.
3. Materialize adapters when needed.
4. Run the actual installed `.tes/bin/tes_init.py --target <canary> --yes`.
5. Run:
   - `python3 scripts/project_context_oracle.py --target <canary>`
   - `<canary>/.tes/bin/tes_update.py plan --target <canary> --json-only`
   - helper self-tests relevant to the changed surface.
6. Read `docs/agents/PROJECT-CONTEXT.md` as a user artifact:
   - identity correct;
   - description supported by source;
   - territories useful;
   - anchors strong;
   - scripts/gates detected when present;
   - unknowns explicit;
   - no bulk code copy;
   - no secret/diff/prompt leakage;
   - no TES internals polluting project anchors;
   - local governance preserved.
7. If a failure appears, fix TES, not the canary.
8. Convert material learning into a portable fixture/oracle/doc/evidence.

Required focused gates before final closure:
- `python3 scripts/field_reports.py --self-test`
- `python3 scripts/tes_init.py --self-test`
- `python3 scripts/project_context_oracle.py --self-test`
- `python3 scripts/tes_update.py --self-test`
- `python3 scripts/install_smoke.py --self-test`
- `python3 scripts/platform_surface_oracle.py --self-test`
- `python3 scripts/materialize_adapter.py all --check`
- `python3 scripts/validate_reference_package.py`
- `python3 scripts/validate_tds.py`

Required final gate:
- `npm run commit:check`

Final report:
Create:
docs/evidence/reports/context-mesh/independent-canary-convergence-YYYY-MM-DD/REPORT.md

The report must include:
- TDS frontmatter;
- prompt version and prompt SHA-256;
- TES starting HEAD and final HEAD;
- canary list with remote repo and commit;
- failures found;
- fixes applied;
- gates added or updated;
- commands run;
- final gate results;
- GO / NEEDS_REVIEW / BLOCKED decision;
- residual risks.

Closure criteria:
Declare GO only if:
- all required gates pass;
- real canaries pass;
- the durable journal exists and contains loop-by-loop evidence;
- every material bug became a patch or explicit BLOCKED/DEFERRED item;
- no target canary was used as a project-specific mold;
- TES improved as a portable product.

Git rules:
- Keep target canaries uncommitted and unpushed.
- Commit TES only after focused gates pass.
- Push `origin/main` only after `npm run commit:check` passes.
- Do not tag, publish, create release, change remotes, or publish marketplace
  artifacts.
- Do not revert user changes you did not make.

Operating posture:
Work like an independent senior team. Be skeptical, systematic, persistent, and
evidence-first. Use subagents when helpful. Do not optimize for speed over
truth. The product has value only when it improves the next real agent session
in a compatible project.
```

## Prompt Changelog

| Version | Date | Change |
|---|---|---|
| `0.1.1` | 2026-05-08 | Clarifies sandbox `.gitignore` guardrail for local journals, run indexes, clones, logs, and transient tool layers while preserving governed `docs/evidence/**`. |
| `0.1.0` | 2026-05-08 | Initial independent canary convergence prompt with journal, sandbox, gates, and versioning contract. |
