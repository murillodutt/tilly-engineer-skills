---
tds_id: install.command_triggers
tds_class: adapter
status: active
consumer: adopters, installing agents, and package maintainers
source_of_truth: true
evidence_level: L2
tver: 0.4.8
---

# TES Command Triggers

After installation, TES commands are intent text in the current agent window.
Scripts and npm aliases are deterministic oracles the agent invokes when the
runtime exposes local tools.

All adapters share the same preferred user triggers: `/tes-init`,
`/tes-update`, `/tes-align`, `/tes-map`, `/tes-goal-maestro`,
`/tes-prospect`, `/tes-mine`,
`/tes-open-obsidian`, `/tes-cortex`, `/tes-curate`, `/tes-mcp`,
`/tes-field-reports`, `/tes-doctor`, `/tes-adapter`, `/tes-bench`, and
`/tes-bump`. Treat
`/tes:*` forms as compatible TES intent aliases; if a host reports one as an
invalid slash, continue through the matching `tes-*` skill/rule/spec instead of
asking the user to restate the route.

`/tes-prospect`, `/tes-mine`, and `/tes-goal-maestro` are
explicit-invocation skills. They do not have broad natural-language routing.
Prospecting and mining stay dormant until the user names the skill or trigger,
then operate proactively with a cognitive brake. Goal maestro may also route
from a direct request to generate a maestral `/goal` prompt from a mature SPEC,
Super SPEC, PRD, relational project plan, or accepted execution tree.
`/tes-bump` is the version governance guard: it routes from direct bump/sync
requests and auto-activates read-only when commit, release, delivered behavior,
or another TES gate reports a version-decision condition.
The executable parity gate is `python3 scripts/command_trigger_oracle.py
--self-test`.
Installed target parity can be checked with
`python3 scripts/command_trigger_oracle.py --target <target-root>`.

## Visible Skill Surface

Some triggers are primary visible skills. Some are supported command intents
routed through a broader skill only when the user-facing surface is genuinely a
sub-mode of that skill. `/tes-update` is a visible update command, not a hidden
mode of `/tes-init`.

| Trigger | Visible router | Surface contract |
|---------|----------------|------------------|
| `/tes-init` | `tes-init` | visible skill |
| `/tes-setup` | `tes-setup` | visible skill alias for `/tes-init` |
| `/tes-update` | `tes-update` | visible update skill |
| `/tes-align` | `tes-align` | visible skill |
| `/tes-map` | `tes-map` | visible Project GPS skill |
| `/tes-goal-maestro` | `tes-goal-maestro` | visible mature-artifact-to-goal materialization skill |
| `/tes-prospect` | `tes-prospect` | visible predictive skill |
| `/tes-mine` | `tes-mine` | visible predictive skill |
| `/tes-open-obsidian` | `tes-open-obsidian` | visible skill |
| `/tes-cortex` | `tes-cortex` | visible skill |
| `/tes-curate` | `tes-cortex` | grouped Cortex curation intent |
| `/tes-mcp` | `tes-mcp` | visible skill |
| `/tes-field-reports` | `tes-field-reports` | visible skill |
| `/tes-doctor` | `tes-doctor` | visible skill |
| `/tes-adapter` | `tes-adapter` | visible skill |
| `/tes-bench` | `tes-bench` | visible skill |
| `/tes-bump` | `tes-bump` | visible version-governance guard |

## Trigger Matrix

| Trigger | User intent | Primary oracles | Writes |
|---------|-------------|-----------------|--------|
| `/tes-init`, `/tes-setup`, or `/tes:init` | finish setup, recertify, initialize project context, and create first-pass project alignment for TES in a project | `tes_install.py`, `root_context.py`, `tes_init.py`, `project_context_oracle.py`, `project_alignment_oracle.py`, install smoke, MCP install | `.tes/tes-install-lock.json`, `.tes/postinstall.json`, first-session hooks, `docs/agents/**`, `docs/agents/PROJECT-CONTEXT.md`, initial operating mesh with System X-Ray and Convergence Line, Cortex, runtime bootloaders, project MCP config |
| `/tes-update` or `/tes:update` | update an already meshed project with the lowest-friction route | `tes_update.py`, `root_context.py`, `tes_legacy_retirement.py`, install smoke, MCP install | only selected TES surfaces after Step Zero and legacy retirement |
| `/tes-align` or `/tes:align` | semantically align a TES-initialized project into an operating mesh with an Eraser-first Atlas, System X-Ray, and Convergence Line | `project_alignment_oracle.py`, `project_context_oracle.py`, project gates | `docs/agents/PROJECT-STATE.md`, `PROJECT-ROADMAP.md` Eraser Atlas links plus Mermaid fallback X-Ray/convergence graphs, `.tes/gps/*.eraserdiagram`, `EXECUTION-LINE.md`, `QUALITY-GATES.md`, `BOUNDARIES-AND-CONSTRAINTS.md`, `KNOWLEDGE-LIFECYCLE.md`, `GLOSSARY.md`, `DECISIONS/**`, evidence |
| `/tes-map` or `/tes:gps` | refresh the adaptive Project Atlas and GPS position; in capsule mode from the internal projection, in attached mode also into the roadmap | `tes_project_atlas.py`, `tes_map.py`, `tes_map_oracle.py`, `project_alignment_oracle.py` when needed | capsule mode: `.tes/gps/**` Eraser Atlas sidecars + `.tes/context/**` projection, no docs export and no `NEEDS_ALIGN` when `docs/agents/**` is absent; when `docs-mesh` is attached, also the managed `TES-MAP` block inside `docs/agents/PROJECT-ROADMAP.md` with Mermaid fallback (capsule state is the source of truth) |
| `/tes-goal-maestro` or `/tes:goal-maestro` | materialize a mature SPEC, Super SPEC, PRD, relational project plan, or accepted execution tree into an execution-grade tree and a ready maestral `/goal` prompt when internal gates pass | active agent artifact review; `NEEDS_SPEC_MATURITY`, `NEEDS_EXECUTION_UNIT_FIDELITY`, `NEEDS_TREE_REPAIR`, `DRAFT_MATERIALIZATION_TREE`, `NEEDS_TREE_ACCEPTANCE`, `SUPER_SPEC_MATERIALIZED`, or `READY_GOAL_PROMPT` status | generated Super SPECs are written to `GOAL-SUPER-SPEC-*.md`; prompt/tree output stays chat-first unless explicitly saved |
| `/tes-prospect` or `/tes:prospect` | explicitly invoke project-stress prospecting to pressure a plan or design, expose hidden dependencies, and ask one question at a time | active agent codebase exploration; cognitive brake state snapshot when paused | no project writes |
| `/tes-mine` or `/tes:mine` | explicitly invoke code and domain mining to extract terms, contradictions, decisions, context, and ADR candidates | active agent code/doc exploration; cognitive brake state snapshot when paused | `CONTEXT.md` and ADRs only when the mining contract resolves terms or decisions and the brake is not active |
| `/tes-open-obsidian` or `/tes:open-obsidian` | open `docs/agents` as the Obsidian vault after context and alignment pass | `tes_open_obsidian.py`, `project_context_oracle.py`, `project_alignment_oracle.py` | no TES writes; Obsidian app may manage project-owned `.obsidian/**` after explicit launch |
| `/tes-cortex` or `/tes:cortex` | inspect, query, audit, rebuild, curate, learn, reflect, consolidate, or apply Cortex memory | `cortex.py`, `consolidation_gate.py`, Cortex MCP | Cortex files only when authorized; consolidation lock writes only `.tes/cortex/consolidation/**`; MCP remember requires ADR 0002 exact approval |
| `/tes-curate` or `/tes:curate` | classify Cortex memory quality risks without writing memory | `cortex.py curate-plan`, read-only `cortex_curate_plan` | no memory writes; CLI may refresh `.tes/cortex/semantic.sqlite` |
| `/tes-mcp` or `/tes:mcp` | explicitly activate, repair, or verify Cortex MCP after install, including VS Code MCP | `install_mcp.py`, `cortex_mcp.py`, MCP smoke, host listing when observable | `.tes/bin/**` and project-scoped MCP config, including `.vscode/mcp.json`; governed remember is default; use `--read-only` for inspection-only activation |
| `/tes-field-reports` or `/tes:field-reports` | inspect, drain, disable, or re-enable sanitized operational reports | `field_reports.py`, local `pre-push` hook | `.tes/field-reports/**`, `.git/info/exclude`, `.git/hooks/pre-push` |
| `/tes-doctor` or `/tes:doctor` | health-check, certify, prepare a commit, or fallback-test/repair/install MCP when MCP health is the failure | installed certification, validation, TDS, doc-size, platform, materialization, MCP self-test, MCP install registration, MCP host recognition, commit gates | read-only by default; MCP fallback may write `.tes/bin/**` and project-scoped MCP config only after repair/install authorization; evidence only when requested |
| `/tes-adapter` or `/tes:adapter` | materialize, dry-run, retrofit, or install adapter surfaces | `materialize_adapter.py`, `install_adapter.py`, adapter oracles | adapter files only after review or approval |
| `/tes-bench` or `/tes:bench` | plan, run, or converge context-mesh benchmarks | benchmark plan/run/converge scripts | temporal benchmark evidence artifacts under `docs/evidence/reports/YYYY/MM/DD/**` |
| `/tes-bump` or `/tes:bump` | govern, plan, and apply bounded project version bumps | `tes_bump.py --governance-check`; `tes_bump.py --dry-run`, then `tes_bump.py --yes` after write authorization | governance check is read-only; writes only discovered version targets; no commits, tags, pushes, remotes, package locks, or publishing |

Aliases:

```text
tes init  -> /tes-init
tes update / update TES / Atualizar TES / atualizar TES -> /tes-update
tes align / align TES / align this project / alinhar TES / alinhar projeto -> /tes-align
tes map / project GPS / mapa TES / map this project / mapear TES / mapear projeto -> /tes-map
/tes:goal-maestro -> /tes-goal-maestro
generate a maestral /goal prompt / gerar um /goal maestral -> /tes-goal-maestro
generate a /goal from a PRD / gerar /goal de um PRD -> /tes-goal-maestro
/tes:prospect -> /tes-prospect
/tes:mine     -> /tes-mine
tes open obsidian / open Obsidian / open this project in Obsidian / abrir Obsidian / abrir no Obsidian -> /tes-open-obsidian
tes setup / initialize TES / install TES / recertify TES -> /tes-init
inicializar TES / instalar TES / recertificar TES -> /tes-init
/tes:recall  -> /tes-cortex recall
/tes:learn   -> /tes-cortex learn
/tes:reflect -> /tes-cortex reflect
/tes:curate  -> /tes-cortex curate-plan
/tes:check   -> /tes-doctor
/tes:certify -> /tes-doctor
/tes:bump    -> /tes-bump
tes bump     -> /tes-bump
```

## Classification

| Command family | Runtime role |
|----------------|--------------|
| `python3 scripts/*.py ...` | portable oracle called by the active agent |
| `npm run ...` | package-source alias for the same oracles; not a target-project guarantee |
| `npx --loglevel=error -y --package github:murillodutt/tilly-engineer-skills#v0.3.171 tilly-engineer-skills add` | fixed GitHub npx installer entrypoint |
| installer | package delivery, lock/sentinel creation, and first-session post-install hook setup |
| MCP tools | project-scoped Cortex surface, preferred for recall/read/curation/reflection and governed remember |
| MCP host recognition | separate state after file registration: `config_present`, `server_self_test_pass`, `protocol_handshake_pass`, `host_listed`, `host_connected`, or `session_restart_required` |
| Installed certification | aggregate installed state: core runtime, MCP registration, Mantra Gate adoption, command trigger parity, quality-gate path, artifact hygiene, and provenance; report `PARTIAL` when MCP passes but any non-MCP component fails |
| skills | user-intent routers in runtimes that support skills |
| goal materialization skill | explicit mature-artifact-to-`/goal` prompt materialization with artifact maturity, execution-unit fidelity, internal tree, material-diff, material-continuation, semantic negative-grep, sequential ownership, and sync-status gates |
| predictive skills | explicit-invocation project-stress and mining skills with cognitive brake |
| version governance guard | auto-read-only bump decision guard with dry-run-first target discovery and no Git or publishing side effects |
| rules | always-on intent routers where skills are not native |
| hooks | Git-event gates for validation, no-write Cortex reflection/curation, and Field Reports drain |
| command-trigger oracle | package gate that checks docs, Codex, Claude, and Cursor share the same trigger vocabulary |
| project-context oracle | target gate that checks `/tes-init` left a useful, evidenced project map |
| project-alignment oracle | target gate that checks `/tes-align` left an evidenced operating mesh |
| Obsidian open gate | target gate that checks context/alignment before visible local Obsidian launch |
| behavioral overlay | always-on, never-invoked discipline that constrains how other skills write (assumptions visible, maturity layer selected, scope smaller, edits surgical, success falsifiable) |
| runtime capability rule | always-on Cursor rule that maps TES runtime command capabilities after clean install or semantic recovery |

## Passive Overlays

These are not user-invocable triggers. They are always-on skills/rules that
shape how other triggers behave; they have no `/tes-*` slash and never write
on their own.

| Overlay | Host surface | Role |
|---------|--------------|------|
| `tes-guidelines` | Claude `SKILL.md`, Cursor `.cursor/rules/tes-guidelines.mdc` | Behavioral engineering discipline: assumptions visible, maturity layer selected before simplicity, scope smaller, edits surgical, success falsifiable. Activates on non-trivial coding, review, refactor, or instruction-migration work. |
| `tes-engineering-discipline` | Codex `SKILL.md` | Codex-side equivalent of `tes-guidelines` with the same maturity-aware discipline contract. |
| `tes-runtime-capabilities` | Cursor `.cursor/rules/tes-runtime-capabilities.mdc` | Always-on Cursor rule that maps TES runtime command capabilities after clean install or semantic recovery. Refreshed only by the deterministic installer. |

Overlays do not appear in the `Trigger Matrix` because users never invoke
them. They are listed here so installers, doctors, and adapter certification
can verify the overlay surface is present on every supported host.

## `/tes-init` Router Contract

`/tes-init` is the canonical user-facing initialization entrypoint. `/tes-setup`
is a commercial setup alias for the same route after npx installation, and is
installed as a direct skill/slash command where the host resolves slash commands
by skill name. Neither form should split into user-visible parameters or a
second context command. The active agent routes internally through two read-only
gates before choosing writes:

The mechanical install route may install runtime capabilities first. That route
deliberately does not perform semantic project analysis in the installer. It
leaves `.tes/postinstall.json` pending and
lets the first-session hook call `tes_install.py hook`, which runs
`tes_init.py`, `project_context_oracle.py`, and `project_alignment_oracle.py`
once. Repeated hook executions must be idempotent and fast after the sentinel is
`complete`.

Claude Code `SessionStart` hooks pass this result as hook context rather than a
normal chat message. TES installs a fast synchronous start notice before the
background runner: `IMPORTANT: TES setup is running. Please wait; do not start project work.`
The second handler uses Claude Code's native `asyncRewake` hook mode, runs
post-install in the background, and wakes the session when setup finishes. The
completion instruction is: `Please, run /tes-setup for the report.` If
`.tes/postinstall.json` is
`running`, a plain `/tes-init` or `/tes-setup` should ask the user to wait and
avoid duplicate setup work. If the sentinel is already `complete`, summarize the
sentinel and `last_run` instead of rerunning Project-Start, unless the user
explicitly asks to recertify/update or the planner reports drift.
If the sentinel is `needs_review`, `/tes-init` is the recovery route: inspect
the latest run, repair the focused blocker, then run
`tes_install.py postinstall --recover-needs-review` so TES reruns Project-Start,
verifies selected MCP config, records the recovery run, and clears the sentinel
only when the gates pass.

1. **Install/Update Gate**: detect whether TES is missing, stale, helper-drifted,
   adapter-drifted, or legacy-blocked. When this gate requires installer/update
   writes, Step Zero protects installer/update writes with the normal Git
   baseline or dirty-tree choice.
2. **Project Context Gate**: detect whether
   `docs/agents/PROJECT-CONTEXT.md` is missing, bootstrap-only, stale, weak, or
   failing `project_context_oracle.py`. When TES is already installed/current and
   only this gate fails, a dirty tree must not block project-context
   initialization; report the dirty tree, then run the project-context scaffold
   and oracle without refreshing helpers, adapters, MCP config, bootloaders, or
   remotes.
3. **Project-Start Gate**: for `/tes-init`, always run the installed
   project-context initializer before the final report. The initializer also
   creates the first-pass Obsidian-compatible operating mesh when missing:
   `python3 .tes/bin/tes_init.py --target . --yes` when operating inside an
   installed target, or the package `scripts/tes_init.py --target <target> --yes`
   when certifying from source. A preflight context PASS does not replace
   project-start execution. Certify both `project_context_oracle.py --target
   <target>` and `project_alignment_oracle.py --target <target>`. After
   helper-only or adapter repairs, rerun the Project-Start Gate before closing
   `/tes-init`; `tes_update.py plan` exposes the `project_start_gate` contract
   so executors cannot treat route planning as context initialization.
   For `needs_review` postinstall recovery, use
   `python3 .tes/bin/tes_install.py postinstall --target . --recover-needs-review`
   as the final Project-Start closure instead of a broad forced rerun.

When an old meshed project has stale helpers, runtime trigger drift, or an
incomplete alignment mesh, `tes_update.py plan --json-only` also exposes a
`continuation_plan`. If required writes are not authorized yet, the final
report must include that plan with phases, approvals, write surfaces, commands,
and final recorded probe instead of closing with an unstructured
`NEEDS_REVIEW`.

The continuation plan separates deterministic script layers from semantic
context layers:

- `bundle_staging`: download or use the versioned TES ZIP, verify SHA-256, and
  create `.tes/setup/<version>/` from the TES bundle manifest.
- `clean_backup`: before any runtime overwrite, create `.tes/bk/<timestamp>/`
  with `manifest.json`, file hashes, Git state, adapter route, and restore
  policy. The backup captures previous root governance, runtime skills,
  adapter/plugin surfaces, MCP config, and prior TES manifests.
- `.tes/setup/**` is local staging cache. The bundle script must add a
  target-local Git exclude entry before extraction so adopter repositories do
  not accidentally commit the downloaded ZIP or extracted setup payload.
- `.tes/bk/**` is local rollback and recovery history. The bundle script must
  add a target-local Git exclude entry before backup so adopter repositories do
  not commit legacy governance or sensitive local context.
- If the ZIP is manually extracted only to reach `scripts/tes_bundle.py`, rerun
  that extracted script with `stage --target <project> --bundle <verified-zip>`
  before reporting certification. Manual unzip alone is not a certified stage.
- `layer_zero_helpers`: refresh manifest-known `.tes/bin/**` helpers.
- `runtime_capability_refresh`: apply the canonical clean runtime from the
  staged bundle with `tes_bundle.py apply --mode clean-runtime`. This may
  overwrite `AGENTS.md`, `CLAUDE.md`, `CURSOR.md`, Cursor rules, and TES-owned
  routers only after the central backup exists. It also installs routers such as
  `.agents/skills/tes-*`, `.claude/skills/tes-*`, and
  `.cursor/rules/tes-runtime-capabilities.mdc`. Plugin templates remain
  source-only in the TES Git package. Obsolete runtime plugin/root-skill
  surfaces (`skills/**`, `.claude-plugin/**`, `.agents/plugins/**`, and
  `plugins/tilly-engineer-skills/**`) are removed only when they are
  TES-owned/generated or empty; ambiguous content is preserved, backed up, and
  returned as `NEEDS_REVIEW`.
- `semantic_recovery`: analyze `.tes/bk/<timestamp>/**` as evidence, migrate
  safe local semantics into `docs/agents/**`, compress redundant legacy rules,
  reject runtime noise, and mark ambiguous material as `NEEDS_REVIEW`.

`runtime_trigger_status=PASS` must not rely on root bootloaders left in a
legacy state. The active runtime is clean; backup evidence is the recovery
source for project-specific semantics.

This keeps `/tes-init` simple for users: make this project usable by TES. If
both gates pass, close with certification and recommend `/tes-doctor` only for a
full health check.

## `/tes-update` Update Contract

`/tes-update` is the canonical user-facing update entrypoint for an installed
TES mesh. `/tes:update` is a compatibility alias; when a host rejects the colon
form as invalid slash text, route it to the visible `tes-update` skill.

The active agent must start with a read-only planner call, not with Project
Start and not with raw JSON to the user:

```bash
python3 .tes/bin/tes_update.py plan --target . --json-only
```

When certifying from package source or a canary, use:

```bash
python3 scripts/tes_update.py plan --target <target> --json-only
```

The report should be short and product-shaped: current version, available
version, scope, route, action, and proof. If the first call is read-only, state
`No project work started`.

`/tes-update` does not rerun `/tes-init` by default. Route to `/tes-init` only
when the planner declares Project-Start, missing context, evidence drift, or
the user explicitly asks to recertify/reinitialize. If the planner reports
`STALE_HELPERS` or `recommended_update_scope=helpers-only`, repair only
TES-owned `.tes/bin/**` helpers first, then rerun the planner before adapter or
MCP config refresh. If adapter/runtime drift remains, refresh runtime capability
and selected TES adapter MCP config only after helper parity is `PASS`.

After any write, the final recorded probe is mandatory:

```bash
python3 .tes/bin/tes_update.py plan --target . --json-only --record-field-report
```

The final probe must show `helper_contract_status=PASS`,
`runtime_trigger_status=PASS` or `NOT_APPLIED`, `update_available=False`, and
`recommended_update_scope=none`.

## `/tes-map` Project Atlas And GPS Contract

`/tes-align` owns the project map. `/tes-map` updates the adaptive Project
Atlas and current position. Easy-first is the Atlas birth surface, not the
evolution ceiling: the first output is certified and useful, while deeper
project-specific relationships evolve through profilers, `--deep`, fixtures,
and oracles.

`/tes-map` reads the existing mesh, writes local Eraser `.eraserdiagram`
sidecars under `.tes/gps/**`, and refreshes only this managed block in
`docs/agents/PROJECT-ROADMAP.md` when docs-mesh is attached:

```md
## TES Map

<!-- TES-MAP:START -->
...
<!-- TES-MAP:END -->
```

The helpers are `tes_project_atlas.py` and `tes_map.py`; the oracle is
`tes_map_oracle.py`. If
`PROJECT-CONTEXT.md` is missing, return `NEEDS_CONTEXT` and route the user to
`/tes-init`. If `PROJECT-ROADMAP.md` is missing, return `NEEDS_ALIGN` and route
the user to `/tes-align`. Do not write `.obsidian/**`, do not rewrite the whole
roadmap, and do not invent phases, blockers, or proof gates. The user-facing
report should stay short: `Atlas`, `You are here`, `Next safe move`,
`Blocked by`, and `Proof`. Mermaid is the Markdown fallback, not the primary
visual language.

## No-Go

- Do not create a slash command merely because a script exists. Visible commands
  must be product entrypoints; `/tes-update` is visible because update is a
  commercial user workflow.
- Do not give `/tes-prospect`, `/tes-mine`, or `/tes-goal-maestro` broad
  natural-language activation; they require explicit invocation or, for
  `tes-goal-maestro`, a direct request for a maestral `/goal` prompt from a
  mature SPEC, Super SPEC, PRD, relational project plan, or accepted execution
  tree. Generated Super SPEC content must be written to
  `GOAL-SUPER-SPEC-*.md` and summarized in chat instead of being pasted into
  the context window.
- Do not certify a command that was skipped or blocked.
- Do not claim latest-source certification when the installer reports
  `STALE_SOURCE` or `BLOCKED` source freshness.
- For public bundles, do not call the bundle stale just because the bundle
  `source_commit` differs from remote `main`. If that commit is an ancestor of
  the distribution commit that serves the same version/hash, freshness is
  `PASS` with meaning `current public bundle`.
- Prefer `tes_bundle.py freshness --target <project>` over prose comparison
  when bundle metadata is present.
- Do not claim `/tes-update` or `/tes:update` is `CURRENT` while helper contract parity is
  `STALE_HELPERS` or `BLOCKED`.
- Do not record Field Reports from exploratory `/tes-update` or `/tes:update` probes; use
  `--record-field-report` only on the final certification probe.
- Do not commit or push after a helper overwrite until a post-Layer Zero final
  recorded probe shows `helper_contract_status=PASS`,
  `runtime_trigger_status=PASS` or `NOT_APPLIED`, `update_available=False`,
  and `recommended_update_scope=none`.
- Do not claim `CURRENT` when `runtime_trigger_status=DRIFT`; run the adapter
  refresh route until installed trigger parity is PASS.
- Do not let a project-owned bootloader conflict block clean runtime install.
  Back it up centrally, apply the canonical runtime, and recover useful
  semantics from the backup evidence.
- Do not use MCP config activation to repair stale helpers; run the helper-only
  Layer Zero route first.
- Do not call SQLite, MCP, or generated output memory.
- Do not call `.tes/cortex/semantic.sqlite` memory; it is only derived
  curation cache.
- Do not overwrite root runtime files before `.tes/bk/<timestamp>/manifest.json`
  exists and can restore the previous files.
- Do not copy new TES assets over old runtime surfaces while
  `tes_legacy_retirement.py audit` still reports active legacy.
- Do not treat Field Reports, GitHub issues, outbox, or hooks as project truth.
- Do not assume a silent pre-push hook created no upstream issue; verify
  `.tes/field-reports/receipts/**` or `field_reports.py status`.
- Field Reports also has a GitHub receiver gate: issue template, schema oracle,
  labels, and quarantine workflow.
- Do not run write operations such as adapter install, MCP activation, Cortex
  apply, materialization, or benchmark artifact updates without a clear target
  and authorization.
- Do not treat `/tes-init` as only an installer. It must leave an initial
  `docs/agents/PROJECT-CONTEXT.md` project map or report why project
  contextualization was blocked.
- Do not claim `Project context: PASS` unless
  `python3 scripts/project_context_oracle.py --target <target-root>` passes or
  the installed package source is unavailable and the report explicitly marks
  the gate `BLOCKED` or `NEEDS_REVIEW`.
- Do not claim `GO` when discovered safe project quality gates such as lint,
  typecheck, test, build, validate, contract, or CI-equivalent commands were
  skipped. Run them, or report the exact gate as `BLOCKED` or `NEEDS_REVIEW`
  with the precondition.
