# CLAUDE.md

Behavioral engineering discipline for reducing common LLM coding mistakes.
Project-specific instructions belong in `docs/agents/**`; clean install backs
up older Claude governance before applying this bootloader.

Tradeoff: this biases toward caution over speed. Use judgment for trivial
one-line changes.

## Core Contract

```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```

## 1. Think Before Coding

Do not assume. Do not hide confusion. Surface tradeoffs.

Before implementing:

- State assumptions explicitly.
- If multiple interpretations exist, present them instead of picking silently.
- Name blockers and ask when evidence or authorization is missing.
- Push back when a simpler or safer path exists.

## 2. Simplicity First

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No unrequested flexibility or configurability.
- No error handling for impossible scenarios.
- If the implementation is much larger than the problem, simplify first.

## 3. Surgical Changes

Touch only what you must. Clean up only your own mess.

- Do not improve adjacent code, comments, or formatting.
- Do not refactor code that is not part of the task.
- Match existing style even when you would choose another style.
- Remove imports, variables, or helpers only when your change made them unused.
- Mention unrelated dead code instead of deleting it.

Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

Define success criteria. Loop until verified.

Transform tasks into verifiable goals:

- "Add validation" becomes "cover invalid inputs, then make the check pass".
- "Fix the bug" becomes "reproduce the bug, then make the reproducer pass".
- "Refactor X" becomes "prove behavior before and after".

For multi-step tasks:

```text
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

## Success Formula

```text
E = A * S * C * V
```

Success is zero if assumptions are hidden, scope is inflated, changes are not
surgical, or verification is missing.

These guidelines are working when diffs are smaller, clarifying questions come
before implementation mistakes, and closure is backed by a concrete check.

## Diamond Build-Test-Fail-Fix

For critical capabilities, build from the finished contract down: final
behavior, adversarial fixture, observed failure, smallest repair, and green
gate. Do not call certified behavior experimental; use `blocked`, `degraded`,
`not available`, `certified`, or `fail`.

## Mantra Gate

For state-changing actions, route to the TES Mantra Gate defined in
`.claude/skills/tes-guidelines/SKILL.md`. The skill owns the gate schema,
compact marker, escalation rule, and adoption-oracle stop states.

Keep this bootloader as routing only. Do not reintroduce a project-local or
duplicated Mantra Gate protocol block here.

## Feedback Voice

Default to short, frank prose. Avoid tables, code blocks, YAML/property dumps,
and long inventories unless the user asks for them or the artifact itself
requires exact syntax.

## Private Project Confidentiality

TES is a generic engineering discipline package. Worked examples in
source files, docs, evidence packets, fixtures, commit messages, and
tag annotations must use neutral placeholder vocabulary
(`target-project`, `canary-project`, `<project-A>`,
`<storage-backend>`, etc.). Real project names, product names,
internal-service names, and filesystem paths inside `~/Dev/<name>`
belong in the maintainer's local notes, not in TES tracked content.

When in doubt, prefer the placeholder.

## TES Shortcuts

Treat `/tes-init`, `/tes-setup`, `/tes:init`,
`tes init`, `tes setup`, `initialize TES`, `install TES`, `recertify TES`,
`inicializar TES`, `instalar TES`, `recertificar TES`, and natural
command/prompts such as `TES, initialize this project`,
`TES, inicialize este projeto`, `Atualizar TES`, or `atualizar TES` as
installer intents.
For `/tes-init`, initialize the project as well as TES: read the strongest
project anchors available and leave `docs/agents/PROJECT-CONTEXT.md` as the
initial durable project map for future agents.
Route `/tes-init` through two read-only gates before choosing writes:
**Install/Update Gate** checks whether TES install/update work is needed, and
**Project Context Gate** checks whether `PROJECT-CONTEXT.md` exists and passes
the context oracle. Step Zero protects installer/update writes; it must not
block project-context initialization when TES is already installed/current and
only the Project Context Gate fails.
Then run the **Project-Start Gate** before the final `/tes-init` report:
execute the installed `tes_init.py --target . --yes`, open strong anchors, and
run `project_context_oracle.py --target .`. A preflight context PASS does not
replace project-start execution; after helper-only repairs, rerun this gate.
If `.tes/postinstall.json` is already `complete` from the first-session hook
and the user asks plain `/tes-init` or `/tes-setup`, read the sentinel and
`last_run`, summarize the completed run, and do not rerun Project-Start unless
the user explicitly asks to recertify/update, the sentinel is not `complete`,
the planner reports drift, or evidence is missing.
If `.tes/postinstall.json` is `needs_review`, route `/tes-init` as recovery:
inspect the latest run, repair the focused blocker, then run
`python3 .tes/bin/tes_install.py postinstall --target . --recover-needs-review`
to rerun Project-Start, verify selected MCP config, record the recovery run,
and clear the sentinel only on PASS.
`tes_init.py` creates the scaffold; the active agent must open strong anchors
before claiming deep project understanding and refine the context or report
`Project context: NEEDS_REVIEW`.
Across Codex, Claude Code, and Cursor, `/tes-*` forms are the preferred shared
triggers and `/tes:*` forms are compatible TES intent aliases. If Claude Code
says `/tes:init` or another `/tes:*` form is an invalid slash command, continue
as TES intent text; do not stop to ask which TES route the user meant when the
intent is clear. Route `/tes-update`, `/tes:update`, `tes update`,
`Atualizar TES`, and `atualizar TES` to `.claude/skills/tes-update/SKILL.md`.
`/tes-update` first checks installed version, cloud version, helper contract
parity, applied IDE surfaces, recommended route, and
`recommended_update_scope`. Read-only update probes use `--json-only`; the
final certification probe may add `--record-field-report`.
`recommended_update_scope=helpers-only` or `STALE_HELPERS` is repaired first
through the helper-only Layer Zero route before adapter or MCP config refresh.
When adapter runtime drift remains after helper parity passes, refresh selected
TES adapter MCP config as part of the update plan. After any helper overwrite,
the final recorded probe is required before GO, commit, or push and must show
`helper_contract_status=PASS`,
`runtime_trigger_status=PASS` or `NOT_APPLIED`, `update_available=False`, and
`recommended_update_scope=none`. Also
treat `/tes-align`, `/tes:align`, `tes align`, `align TES`,
`align this project`, `alinhar TES`, `alinhar projeto`, `/tes-map`,
`/tes:gps`, `tes map`, `project GPS`, `mapa TES`, `map this project`,
`mapear TES`, `mapear projeto`,
`/tes-goal-maestro`, `/tes:goal-maestro`,
`generate a maestral /goal prompt`, `generate a /goal from a PRD`,
`gerar um /goal maestral`, `gerar /goal de um PRD`,
`/tes-prospect`, `/tes:prospect`, `/tes-mine`, `/tes:mine`,
`/tes-open-obsidian`, `/tes:open-obsidian`, `open Obsidian`,
`open this project in Obsidian`, `abrir Obsidian`, `abrir no Obsidian`,
`/tes-cortex`,
`/tes:cortex`, `/tes-curate`, `/tes:curate`,
`/tes-mcp`, `/tes:mcp`, `/tes-field-reports`, `/tes:field-reports`,
`/tes-doctor`, `/tes:doctor`, `/tes-adapter`, `/tes:adapter`, `/tes-bench`,
`/tes:bench`, `/tes-bump`, `/tes:bump`, `/tes-tts`, `/tes:tts`, `tes tts`,
`read this text aloud`, `leia em voz alta`, and `narrar este texto` as intent
shortcuts. Use the
matching `.claude/skills/tes-*` skill when present; otherwise follow the local
installer or helper spec directly and choose the smallest safe oracle. These
are not shell commands.
Do not activate `/tes-prospect`, `/tes-mine`, or `/tes-goal-maestro` from broad
natural language. They require explicit invocation;
`tes-goal-maestro` may also route from a direct request for a maestral `/goal`
prompt from a mature SPEC, Super SPEC, PRD, relational project plan, or
accepted execution tree. It must preserve declared execution units, validate
the tree internally, require material-diff, material-continuation, semantic
negative-grep, sequential ownership and sync-status evidence, and emit `/goal`
when gates pass. `tes-bump` is a version governance guard: direct bump/sync
requests route to it, and commit, release, delivered-behavior, or gate-reported
bump conditions auto-activate its read-only `--governance-check`. It must
dry-run target discovery before any write and must not commit, tag, push,
publish, or edit remotes.
`/tes-prospect` and `/tes-mine` must honor the cognitive brake.

## Cortex Reflection

If `docs/agents/cortex/CONTRACT.md` exists, Cortex is the durable memory
surface. Before the final response for material work, use read-only
`cortex_reflect` when available, or run:

```bash
python3 .tes/bin/cortex.py reflect --target . "<decision or lesson>"
```

Mention useful proposals. Do not write Cortex cells without explicit user
authorization.
If `curation_due=true`, run read-only `cortex_curate_plan` when available, or:

```bash
python3 .tes/bin/cortex.py curate-plan --target . --backend lexical
```

## Field Reports

TES Field Reports is active by default. It records only sanitized operational
facts and drains them through the local pre-push hook. When the user asks to
disable, enable, check, or drain Field Reports, run the matching
`field_reports.py` oracle and never expand collection levels or schema.

## TES Memory Lifecycle Boundary

- recall stays read-only unless a specific TES skill or oracle authorizes more;
- scope normalization is handled by the parent context until the shared
  normalizer exists;
- write gate means durable Cortex writes require explicit parent authorization;
- checkpoint state is resumability, not durable memory;
- closeout is proven by TES oracles and repository Git hooks;
- subagent return is evidence return only.

Parent owns durable memory. Subagents may inspect, patch, or report findings
inside their assigned scope, but they must not perform durable Cortex writes or
promote checkpoint/event state into memory directly.
