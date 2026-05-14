---
tds_id: install.command_triggers
tds_class: adapter
status: active
consumer: adopters, installing agents, and package maintainers
source_of_truth: true
evidence_level: L2
tver: 0.4.6
---

# TES Command Triggers

After installation, TES commands are intent text in the current agent window.
Scripts and npm aliases are deterministic oracles the agent invokes when the
runtime exposes local tools.

All adapters share the same preferred user triggers: `/tes-init`,
`/tes-update`, `/tes-align`, `/tes-prospect`, `/tes-mine`,
`/tes-open-obsidian`, `/tes-cortex`, `/tes-curate`, `/tes-mcp`,
`/tes-field-reports`, `/tes-doctor`, `/tes-adapter`, and `/tes-bench`. Treat
`/tes:*` forms as compatible TES intent aliases; if a host reports one as an
invalid slash, continue through the matching `tes-*` skill/rule/spec instead of
asking the user to restate the route.

`/tes-prospect` and `/tes-mine` are explicit-invocation predictive skills. They
do not have broad natural-language routing. They stay dormant until the user
names the skill or trigger, then operate proactively with a cognitive brake.
The executable parity gate is `python3 scripts/command_trigger_oracle.py
--self-test`.
Installed target parity can be checked with
`python3 scripts/command_trigger_oracle.py --target <target-root>`.

## Visible Skill Surface

Some triggers are primary visible skills. Some are supported command intents
routed through a broader skill so TES does not create one skill per alias.

| Trigger | Visible router | Surface contract |
|---------|----------------|------------------|
| `/tes-init` | `tes-init` | visible skill |
| `/tes-update` | `tes-init` | grouped update intent |
| `/tes-align` | `tes-align` | visible skill |
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

## Trigger Matrix

| Trigger | User intent | Primary oracles | Writes |
|---------|-------------|-----------------|--------|
| `/tes-init`, `/tes-setup`, or `/tes:init` | finish setup, recertify, initialize project context, and create first-pass project alignment for TES in a project | `tes_install.py`, `root_context.py`, `tes_init.py`, `project_context_oracle.py`, `project_alignment_oracle.py`, install smoke, MCP install | `.tes/tes-install-lock.json`, `.tes/postinstall.json`, first-session hooks, `docs/agents/**`, `docs/agents/PROJECT-CONTEXT.md`, initial operating mesh with System X-Ray and Convergence Line, Cortex, runtime bootloaders, project MCP config |
| `/tes-update` or `/tes:update` | update an already meshed project with the lowest-friction route | `tes_update.py`, `root_context.py`, `tes_legacy_retirement.py`, install smoke, MCP install | only selected TES surfaces after Step Zero and legacy retirement |
| `/tes-align` or `/tes:align` | semantically align a TES-initialized project into an operating mesh with a System X-Ray and Convergence Line | `project_alignment_oracle.py`, `project_context_oracle.py`, project gates | `docs/agents/PROJECT-STATE.md`, `PROJECT-ROADMAP.md` Mermaid X-Ray and convergence graphs, `EXECUTION-LINE.md`, `QUALITY-GATES.md`, `BOUNDARIES-AND-CONSTRAINTS.md`, `KNOWLEDGE-LIFECYCLE.md`, `GLOSSARY.md`, `DECISIONS/**`, evidence |
| `/tes-prospect` or `/tes:prospect` | explicitly invoke project-stress prospecting to pressure a plan or design, expose hidden dependencies, and ask one question at a time | active agent codebase exploration; cognitive brake state snapshot when paused | no project writes |
| `/tes-mine` or `/tes:mine` | explicitly invoke code and domain mining to extract terms, contradictions, decisions, context, and ADR candidates | active agent code/doc exploration; cognitive brake state snapshot when paused | `CONTEXT.md` and ADRs only when the mining contract resolves terms or decisions and the brake is not active |
| `/tes-open-obsidian` or `/tes:open-obsidian` | open `docs/agents` as the Obsidian vault after context and alignment pass | `tes_open_obsidian.py`, `project_context_oracle.py`, `project_alignment_oracle.py` | no TES writes; Obsidian app may manage project-owned `.obsidian/**` after explicit launch |
| `/tes-cortex` or `/tes:cortex` | inspect, query, audit, rebuild, curate, learn, reflect, or apply Cortex memory | `cortex.py`, read-only Cortex MCP | Cortex files only when authorized |
| `/tes-curate` or `/tes:curate` | classify Cortex memory quality risks without writing memory | `cortex.py curate-plan`, read-only `cortex_curate_plan` | no memory writes; CLI may refresh `.tes/cortex/semantic.sqlite` |
| `/tes-mcp` or `/tes:mcp` | activate or verify read-only Cortex MCP | `install_mcp.py`, `cortex_mcp.py`, MCP smoke | `.tes/bin/**` and project-scoped MCP config |
| `/tes-field-reports` or `/tes:field-reports` | inspect, drain, disable, or re-enable sanitized operational reports | `field_reports.py`, local `pre-push` hook | `.tes/field-reports/**`, `.git/info/exclude`, `.git/hooks/pre-push` |
| `/tes-doctor` or `/tes:doctor` | health-check, certify, or prepare a commit | validation, TDS, doc-size, platform, materialization, commit gates | none unless evidence is explicitly requested |
| `/tes-adapter` or `/tes:adapter` | materialize, dry-run, retrofit, or install adapter surfaces | `materialize_adapter.py`, `install_adapter.py`, adapter oracles | adapter files only after review or approval |
| `/tes-bench` or `/tes:bench` | plan, run, or converge context-mesh benchmarks | benchmark plan/run/converge scripts | benchmark evidence artifacts |

Aliases:

```text
tes init  -> /tes-init
tes update / update TES / Atualizar TES / atualizar TES -> /tes-update
tes align / align TES / align this project / alinhar TES / alinhar projeto -> /tes-align
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
```

## Classification

| Command family | Runtime role |
|----------------|--------------|
| `python3 scripts/*.py ...` | portable oracle called by the active agent |
| `npm run ...` | package-local alias for the same oracles |
| `npx --loglevel=error -y --package github:murillodutt/tilly-engineer-skills#v0.3.90 tilly-engineer-skills add` | fixed GitHub npx installer entrypoint |
| `npx --loglevel=error -y --prefer-online --package github:murillodutt/tilly-engineer-skills#latest tilly-engineer-skills add` | moving GitHub branch channel; use `--prefer-online` when following `latest` |
| installer | package delivery, lock/sentinel creation, and first-session post-install hook setup |
| MCP tools | read-only access surface, preferred for recall/read/curation/reflection |
| skills | user-intent routers in runtimes that support skills |
| predictive skills | explicit-invocation project-stress and mining skills with cognitive brake |
| rules | always-on intent routers where skills are not native |
| hooks | Git-event gates for validation, no-write Cortex reflection/curation, and Field Reports drain |
| command-trigger oracle | package gate that checks docs, Codex, Claude, and Cursor share the same trigger vocabulary |
| project-context oracle | target gate that checks `/tes-init` left a useful, evidenced project map |
| project-alignment oracle | target gate that checks `/tes-align` left an evidenced operating mesh |
| Obsidian open gate | target gate that checks context/alignment before visible local Obsidian launch |

## `/tes-init` Router Contract

`/tes-init` is the canonical user-facing initialization entrypoint. `/tes-setup`
is a commercial setup alias for the same route after npx installation. Neither
form should split into user-visible parameters or a second context command. The
active agent routes internally through two read-only gates before choosing
writes:

The mechanical install route may install runtime capabilities first. That route
deliberately does not perform semantic project analysis in the installer. It
leaves `.tes/postinstall.json` pending and
lets the first-session hook call `tes_install.py hook`, which runs
`tes_init.py`, `project_context_oracle.py`, and `project_alignment_oracle.py`
once. Repeated hook executions must be idempotent and fast after the sentinel is
`complete`.

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
  `.agents/skills/tes-*`, `.claude/skills/tes-*`, `skills/tes-*`, plugin
  metadata, and `.cursor/rules/tes-runtime-capabilities.mdc`.
- `semantic_recovery`: analyze `.tes/bk/<timestamp>/**` as evidence, migrate
  safe local semantics into `docs/agents/**`, compress redundant legacy rules,
  reject runtime noise, and mark ambiguous material as `NEEDS_REVIEW`.

`runtime_trigger_status=PASS` must not rely on root bootloaders left in a
legacy state. The active runtime is clean; backup evidence is the recovery
source for project-specific semantics.

This keeps `/tes-init` simple for users: make this project usable by TES. If
both gates pass, close with certification and recommend `/tes-doctor` only for a
full health check.

## No-Go

- Do not create one slash command per script.
- Do not give `/tes-prospect` or `/tes-mine` broad natural-language activation;
  they require explicit invocation.
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
