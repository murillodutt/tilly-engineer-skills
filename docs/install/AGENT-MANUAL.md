---
tds_id: install.agent_manual
tds_class: adapter
status: active
consumer: installing agents and runtime adapters
source_of_truth: true
evidence_level: L2
tver: 0.1.6
---

# Tilly Engineer Skills — Agent Manual

Operational contract for coding agents (Codex, Claude Code, Cursor) executing
TES intents. Companion to `docs/install/USER-MANUAL.html` (user surface).
This file is the agent-side surface: triggers, oracles, gates, return states,
schemas, MCP contract.

> Audience: the active coding agent inside an IDE/runtime window.
> Users consume `USER-MANUAL.html`. This file is the contract the agent
> follows when a user types a TES intent.

---

## 1. Execution model

- Executor: active coding agent inside the current IDE/runtime window.
- Skills, rules, bootloaders route behavior.
- Python scripts and `npm run ...` entries are deterministic oracles the
  agent invokes when local tool access exists.
- Hooks are Git-event gates for validation and no-write Cortex
  reflection/curation.
- MCP is a read-only Cortex access surface.
- If a runtime cannot execute an oracle, the agent reports `BLOCKED` or
  `SKIPPED` instead of claiming certification.

---

## 2. Command triggers

User-facing intent typed in the agent window — never a shell command.

| Trigger | Purpose | Aliases |
|---------|---------|---------|
| `/tes-init` | First setup on a target project | `/tes:init` (compat) |
| `/tes-setup` | First-session report or setup alias | direct alias for `/tes-init` |
| `/tes-update` | Update an already-meshed project | `/tes:update` (compat) |
| `/tes-align` | Re-run alignment after context drift | `/tes:align` (compat) |
| `/tes-map` | Refresh the Project GPS position in the roadmap | `/tes:gps` (compat) |
| `/tes-goal-maestro` | Generate an execution-grade tree and maestral `/goal` prompt from a mature SPEC, Super SPEC, PRD, relational project plan, or accepted execution tree | `/tes:goal-maestro` (compat) |
| `/tes-prospect` | Stress-test a plan or design after explicit invocation | `/tes:prospect` (compat) |
| `/tes-mine` | Mine code, terminology, context, and ADR candidates after explicit invocation | `/tes:mine` (compat) |
| `/tes-open-obsidian` | Open `docs/agents/` in Obsidian via CLI or macOS app fallback | `/tes:open-obsidian` (compat) |
| `/tes-cortex` | Inspect, query, audit, rebuild, curate, learn, reflect, or apply Cortex memory | `/tes:cortex`, `/tes:recall`, `/tes:learn`, `/tes:reflect` |
| `/tes-curate` | Classify Cortex quality risks without writing memory | `/tes:curate` |
| `/tes-mcp` | Activate or verify Cortex MCP | `/tes:mcp` |
| `/tes-field-reports` | Inspect, drain, disable, or enable sanitized Field Reports | `/tes:field-reports`, `/tes:field-reports:disable`, `/tes:field-reports:enable` |
| `/tes-doctor` | Health-check, certify, prepare a commit, or fallback-test/repair/install MCP | `/tes:doctor`, `/tes:check`, `/tes:certify` |
| `/tes-adapter` | Materialize, dry-run, retrofit, or install adapter surfaces | `/tes:adapter` |
| `/tes-bench` | Plan, run, or converge context-mesh benchmarks | `/tes:bench` |
| `/tes-bump` | Govern, plan, and apply bounded project version bumps | `/tes:bump` |
| `/tes-tts` | Read user-provided text aloud through an available local TTS tool | `/tes:tts` |
`/tes-update` is a direct visible skill in Codex and Claude Code. It starts
with the read-only `tes_update.py plan --json-only` probe and must not rerun
`/tes-init` unless the planner declares Project-Start, missing context, evidence
drift, or the user explicitly asks to recertify.

Invalid `/tes:*` slash text still signals TES intent. Agent selects the
smallest safe oracle.

`/tes-goal-maestro`, `/tes-prospect`, and `/tes-mine` are explicit-invocation
skills, not broad natural intent routers. Do not activate them from vague goal,
stress-test, or mining language unless the user explicitly names the skill or
direct action. `tes-goal-maestro` may also route from a direct request to
generate a maestral `/goal` prompt from a mature artifact; it preserves
declared execution units, validates the tree internally, requires
material-diff, material-continuation, semantic negative-grep, sequential
ownership and sync-status evidence, and emits `/goal` when gates pass. When
it generates or expands a Super SPEC, the full content is written to
`GOAL-SUPER-SPEC-*.md` and chat shows only the artifact path plus a short
summary.
`tes-bump` is different: it is the version governance guard. It routes from
direct bump/sync requests and auto-activates read-only when commit, release,
delivered behavior, or another TES gate reports a version-decision condition.
It must run `tes_bump.py --governance-check` before inferred closure decisions,
dry-run target discovery before writes, and must not commit, tag, push, publish,
or edit remotes. After
prospecting or mining invocation, they may drive the sequence proactively and
must honor the cognitive brake:
`pause`, `pausa`, `freia`, `segura`, `para`, `hold`, `step back`, or
`resuma onde estamos` stops pressure immediately. Report where the session
stopped, the current hypothesis, the open risk or unresolved term, and the next
question/check. Resume only after explicit `continue`, `continua`, `retoma`,
or `segue`.

`/tes-map` is the Project GPS route. `tes-align` owns the map; `tes-map`
updates only the managed `TES-MAP` block inside
`docs/agents/PROJECT-ROADMAP.md`. If the roadmap is missing, return
`NEEDS_ALIGN`; if project context is missing, return `NEEDS_CONTEXT`. The
answer should be short and visual: `You are here`, `Next safe move`,
`Blocked by`, and `Proof`.

### Passive overlays

These are not user-invocable triggers. They are always-on skills/rules that
shape how other triggers behave; they have no `/tes-*` slash and never write
on their own.

| Overlay | Host surface | Role |
|---------|--------------|------|
| `tes-guidelines` | Claude `SKILL.md`, Cursor `.cursor/rules/tes-guidelines.mdc` | Behavioral engineering discipline: assumptions visible, scope smaller, edits surgical, success falsifiable. Activates on non-trivial coding, review, refactor, or instruction-migration work. |
| `tes-engineering-discipline` | Codex `SKILL.md` | Codex-side equivalent of `tes-guidelines` with the same four-gate discipline contract. |
| `tes-runtime-capabilities` | Cursor `.cursor/rules/tes-runtime-capabilities.mdc` | Always-on Cursor rule that maps TES runtime command capabilities after clean install or semantic recovery. Refreshed only by the deterministic installer. |

Overlays are not selected by user intent. Adapter certification and `/tes-doctor`
verify the overlay surface is present on every supported host.

When MCP is the failing surface, `/tes-doctor` falls back to `/tes-mcp`: test
with `cortex_mcp.py --self-test`, dry-run `install_mcp.py --target . --adapter all --overwrite --json-only`, repair with `--yes` only after authorization, then certify `config_registrations` and the project-scoped config path.
For full installed health, `/tes-doctor` runs `installed_certification_oracle.py --target . --json-only` and preserves `PASS`, `PARTIAL`, `NEEDS_REVIEW`, or `BLOCKED`; MCP success alone is not a clean installed certification.
---

## 3. Routes

Selected during install/update or explicit MCP work. Default: `current`. For `npx`/`bunx add`, `--agent all` means Codex, Claude Code, and Cursor; VS Code MCP registration is an explicit `/tes-mcp` or `install_mcp.py` route.

| Route | Effect |
|-------|--------|
| `current` | Updates current runtime + its default governed Cortex MCP config |
| `codex` | Prepares `AGENTS.md`, Codex skill, `.codex/config.toml` |
| `claude` | Prepares `CLAUDE.md`, `.claude/skills/**`, `.mcp.json` |
| `cursor` | Prepares rules in `.cursor/rules/**`, `.cursor/mcp.json` |
| `vscode` | Explicit MCP-only route for `.vscode/mcp.json` |
| `all` | Prepares Codex, Claude, Cursor + their project MCP configs |
| `mcp` | Activates only Cortex MCP layer for detected runtime; `--read-only` is opt-out |
| `audit` | Inspects without modifying files |

---

## 4. Project states

Determined during Step Zero scan.

| State | Meaning |
|-------|---------|
| `new` | No relevant agent instructions; installer creates minimal mesh |
| `existing` | Local rules/docs exist; installer backs them up, applies clean runtime, then recovers semantics |
| `meshed` | TES already present; run becomes update/convergence |

---

## 5. Gate sequence

`/tes-init` routes through three sequential gates:

1. **Install/Update Gate** — Step Zero protects installer/update writes.
2. **Project Context Gate** — preflight context check; PASS does not
   replace project-start execution.
3. **Project-Start Gate** — after helper-only repairs, execute
   `tes_init.py --target . --yes`, the context + alignment oracles, and
   required project quality gates from `docs/agents/QUALITY-GATES.md` before
   final report.

When `.tes/postinstall.json` is already `complete` from the first-session hook,
a plain `/tes-init` or `/tes-setup` immediately after opening the agent is a
status/report request. Read the sentinel and its `last_run`, summarize the
completed setup, and rerun Project-Start only when the user asks to recertify or
update, the sentinel is not `complete`, the planner reports drift, or evidence
is missing. When the sentinel is `running`, tell the user to wait for
first-session setup to finish and run `/tes-setup` again; do not launch duplicate
setup commands. In Claude Code, TES first emits a synchronous start notice:
`IMPORTANT: TES setup is running. Please wait; do not start project work.` It then uses native
`asyncRewake` so setup runs in the background and wakes the session with:
`Please, run /tes-setup for the report.` Repeated complete hooks stay quiet.
When the sentinel is `needs_review`, `/tes-init` is recovery: inspect the latest
run record, repair the focused blocker, then run
`python3 .tes/bin/tes_install.py postinstall --target . --recover-needs-review`.
That recovery reruns Project-Start, records the new run, and clears the sentinel
only on PASS.

After install, platform-specific host review still matters:

- Codex can show the Session Start hook as `needs review` in Settings > Hooks.
  The user must inspect, Trust, and enable the hook before Codex will run it.
- Claude Code should be opened or reopened, then left idle until the TES
  completion notice appears; `/tes-setup` is the report route after completion.
- Cursor should be reopened so it reloads `.cursor/hooks.json`; when
  first-session setup completes, `/tes-setup` is the report route. A dry
  `/tes-init` after a `complete` sentinel should report current evidence, not
  run Project-Start again, unless the user explicitly asks to recertify.

Step Zero must not block project-context initialization when TES is
already current and only `PROJECT-CONTEXT.md` needs work.

When legacy retirement is true, the agent runs that gate before copying
new TES assets. Legacy retrofit records archive under
`.tes/legacy-retirement/retrofit/`.

---

## 6. Mantra Gate

Mantra Gate is the TES pre-action micro-gate for state-changing work:
evidence, scope, path, record, oracle, and stop rule.

Permitted writes show only `[🍳 Flash-Fry]`, but the full gate
(`VERIFY`, `SCOPE`, `BEST_PATH`, `DOCUMENT`, `ORACLE`, `RESOLVE`, `STATUS`)
must be recorded in the active evidence/report surface, Field Reports/Cortex,
or `.tes/mantra-gates/` fallback. Risk is `routine`, `material`, `high-risk`,
or `forbidden`: high-risk work needs a complete internal record and oracle,
forbidden work stops, and state-changing evidence without a nearby record
reports `BYPASS_SUSPECTED`. The default adoption check is health/read-only:
dirty trees are context, not current-action blockers.

Helpers: `python3 .tes/bin/mantra_gate.py --self-test`,
`python3 .tes/bin/mantra_gate.py emit-marker`,
`python3 .tes/bin/mantra_gate.py classify-risk --action "git push to origin"`,
`python3 .tes/bin/mantra_gate_adoption_oracle.py --target .`,
`python3 .tes/bin/mantra_gate_adoption_oracle.py --target . --action "commit" --state-changing`,
and `python3 .tes/bin/mantra_gate_adoption_oracle.py --target . --commit-push`.
Recover by recording the missing gate, adding the closure `ORACLE`, resolving
review detail, or stopping forbidden work. Read-only inspection is not blocked.

---

## 7. Update probe contract

Compares: installed version vs cloud version, helper parity, IDE
surfaces, route, `recommended_update_scope`.

- Inspection: `--json-only` (read-only).
- Final probe before GO/commit/push: `--record-field-report` (mandatory
  after helper overwrite).

**GO requires all of:**

| Field | Required value |
|-------|----------------|
| `helper_contract_status` | `PASS` |
| `runtime_trigger_status` | `PASS` or `NOT_APPLIED` |
| Project quality gates | `PASS`, or `BLOCKED` / `NEEDS_REVIEW` with reason |
| `update_available` | `False` |
| `recommended_update_scope` | `none` |

`STALE_HELPERS` requires update; not current. Repair first with
helper-only Layer Zero before activating MCP configs.

---

## 8. Return state vocabulary

Use these literal tokens. Never substitute synonyms.

| State | Use |
|-------|-----|
| `PASS` | Oracle/gate succeeded |
| `BLOCKED` | Required dependency or capability unavailable |
| `DEGRADED` | Fell back to a lower-fidelity backend (e.g. `auto` → lexical) |
| `NEEDS_REVIEW` | Run closed with evidence; manual review required |
| `STALE_SOURCE` | Source package commit behind current Tilly `main`; not used when a public bundle source commit is an ancestor of the current distribution commit |
| `STALE_HELPERS` | Helper contract drift detected; update required |
| `RECOVERED` | Previous bootloader/rule context is backed up and semantically recovered from `.tes/bk/**` |
| `NOT_APPLIED` | Trigger not relevant to detected runtime |
| `FAIL` | Hard failure; close with evidence |

Do not call certified behavior `experimental`. Use the vocabulary above.

---

## 9. Cortex contract

### Layout

```
docs/agents/cortex/
  CONTRACT.md
  MAP.md
  TRAIL.md
  LINKS.md
  sources/
  cells/
.tes/cortex/recall.sqlite
.tes/cortex/semantic.sqlite
```

Markdown is the source of truth. SQLite is derived recall + semantic
curation cache only. Never treat SQLite, MCP, or LLM as memory.

### Cell schema

- Required headings: `## Claim` and `## Evidence`.
- `sources/**` is immutable after import.

### Write rules

| Operation | Writes? | Conditions |
|-----------|---------|------------|
| `learn` | No | Requires source evidence or specific durable lesson; generic input → evidence-gap/no-capture |
| `reflect` | No | Generates proposal only |
| `curate-plan` | No | `writes: []` always; may refresh derived semantic index from CLI only, not over MCP |
| `apply --yes` | Yes | Requires explicit evidence + audit + rebuild; never writes to `sources/**` |
| `health` / `peek` / `review` | No | Operator read-only commands; must report `writes: []` and `derived_writes: []` |
| `checkpoint --yes` | Yes | Writes only `.tes/checkpoints/**`; not durable memory |
| `remember --yes` | Yes | Same durable-memory gate as `apply --yes` |
| `forget --yes` | Blocked | Returns `BLOCKED` until consolidation gate evidence exists |
| `consolidation_gate.py lock --yes` | Yes | Writes only `.tes/cortex/consolidation/**`; never writes durable memory |
| `consolidation_gate.py certify` | No | Requires lock, approved review, rollback, evidence, and observed Cortex write result |

### Backends

| Backend | Behavior |
|---------|----------|
| `lexical` | Deterministic gate; default |
| `xenova` | Requires `@huggingface/transformers` + `Xenova/multilingual-e5-small`; reports `BLOCKED` when unavailable |
| `auto` | Tries Xenova; reports `DEGRADED` when falling back to lexical |

---

## 10. Oracle inventory

Agent-callable script and npm oracle inventory lives in
`docs/install/AGENT-ORACLE-INVENTORY.md`.

Use the TES package root for package checks, or `--target` when operating on
another project or vault. In an installed target, prefer installed helpers under
`.tes/bin/**` and the target's own discovered scripts; do not certify an
`npm run ...` command unless it exists in the current workspace.
package-source conveniences are not target-project guarantees. Do not certify an
`npm run ...` command unless that command exists in the current workspace.

Routing matrix: `docs/install/COMMAND-TRIGGERS.md`.

---

## 11. MCP contract

Governed remember is available by default; `--read-only` hides that lane.
Activation writes only `.tes/bin/**` and project-scoped runtime config. It must
not touch global MCP config, secrets, hooks, or `sources/**`.

### Project-scoped config per runtime

| Runtime | Config path |
|---------|-------------|
| Codex | `.codex/config.toml` |
| Claude Code | `.mcp.json` |
| Cursor | `.cursor/mcp.json` |
| VS Code | `.vscode/mcp.json` |

### Tool surface

| Tool | Behavior |
|------|----------|
| `cortex_verify` | Validates Cortex structure and contract |
| `cortex_health` | Reports health and operator mutability classes without writes |
| `cortex_peek` | Reads recall results or one cell without writes |
| `cortex_review` | Runs audit, no-write curation, and reflection review |
| `cortex_audit` | Finds broken links, missing evidence, loose cells |
| `cortex_recall` | SQLite FTS5 search; falls back to `rg` |
| `cortex_read_cell` | Reads one cell directly from `cells/**` |
| `cortex_absorb_plan` | No-write absorb plan |
| `cortex_curate_plan` | Classifies semantic memory quality risks; no writes to memory or derived indexes |
| `cortex_reflect` | No-write memory + curation proposal |

Write-capable MCP tools are intentionally outside this version.

### Installed helper set

`cortex.py`, `cortex_mcp.py`, `cortex_embed.mjs`, `scope_contract.py`,
`event_ledger.py`, `checkpoint.py`, `consolidation_gate.py`, `field_reports.py`, `tes_update.py`, `tes_legacy_retirement.py`, `root_context.py`,
`tes_init.py`, `project_context_oracle.py`, `project_alignment_oracle.py`,
`tes_open_obsidian.py`, `command_trigger_oracle.py`, `tes_bundle.py`,
`materialize_adapter.py`.

---

## 12. Field Reports pipeline

Active by default. Captures sanitized operational facts locally; drains
through `gh` during `git push` only when local CLI, authentication, and
network are available.

### Privacy invariants

Never sends: code, diffs, prompts, file contents, secrets, personal
data, absolute paths, raw stack traces, raw branch names, raw remotes.

### Local pipeline

- Hook: local `pre-push`.
- State: `.tes/field-reports/**`.
- Behavior on missing `gh` / network / auth: outbox stays pending; push
  continues.
- Low-signal heartbeats: suppressed locally with receipt; no noisy
  issues.

### GitHub receiver

Issue template + schema check + quarantine workflow. Local sanitization
is the first privacy gate; GitHub governance is the second audit gate.

Certification covers: local capture/drain, fake transport, receiver
quarantine. Live GitHub publication remains partial until explicitly
authorized.

### Opt-out

Triggers (typed in agent window):

- `/tes:field-reports:disable`
- `/tes:field-reports:enable`

CLI equivalents (audit only):

```bash
python3 scripts/field_reports.py disable --target /path/to/project
python3 scripts/field_reports.py enable --target /path/to/project
```

---

## 13. Layer split

| Layer | Responsibility | Surface |
|-------|----------------|---------|
| Installer scripts | Download or use the versioned ZIP, verify SHA-256, stage `.tes/setup/<version>/`, refresh manifest-known TES-owned helpers and runtime capabilities | Python + npm |
| LLM layer | Project understanding, semantic governance review | Active agent in IDE window |
| Root runtime files | `AGENTS.md`, `CLAUDE.md`, `CURSOR.md`, Cursor rules — backed up before clean overwrite | Markdown bootloaders |

`/tes-align`, `/tes-map`, and `/tes-open-obsidian` become active through safe runtime
surfaces.

---

## 14. Git safety

Tilly protects local rollback and cache artifacts via
`.git/info/exclude`:

- `.tes/bk/**`
- legacy `.tes/bin/*.bak-*`
- Python bytecode
- Field Reports state
- Cortex SQLite caches

Tilly does **not** ignore `.tes/bin/*.py` — those helpers are the
installed runtime surface.

---

## 15. Convergence Report contract

Every run ends with a short **TES Context Mesh Convergence Report** in
chat. Required fields:

| Field | Notes |
|-------|-------|
| Status | One of the return-state tokens (Section 7) |
| Source snapshot freshness | `PASS` for latest source or current public bundle; use `tes_bundle.py freshness --target <project>` when available; `STALE_SOURCE` only when the source snapshot is behind or unrelated |
| Changed surfaces | List affected files/configs |
| Root context gate | `PASS` / `RECOVERED` / `NEEDS_REVIEW` |
| Installed helper set | Helper inventory (Section 10) |
| Helper contract parity | `helper_contract_status=PASS` |
| Field Reports state | `enabled` / `disabled` + outbox state |
| Gates | Per-gate disposition, including project quality gates such as lint, typecheck, test, and CI-equivalent commands |
| Limits | Capabilities not exercised |
| Rollback summary | Baseline head + revert commands |

Long inventories live in the evidence file, not the chat report. Backup
files are rollback artifacts, never new TES surfaces.

---

## 16. Rollback

Use the baseline recorded during Step Zero.

```bash
git reset --hard <baseline-head>
git revert <install-commit>
```

---

## 17. Cross-references

| Need | Source |
|------|--------|
| User-facing manual | `docs/install/USER-MANUAL.html` |
| Installer prompt | `docs/install/MINI-PROMPT.md` |
| Agent oracle inventory | `docs/install/AGENT-ORACLE-INVENTORY.md` |
| Trigger routing matrix | `docs/install/COMMAND-TRIGGERS.md` |
| Independent canary | `docs/install/INDEPENDENT-CANARY-CONVERGENCE.prompt.md` |
| Assisted context installer | `docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md` |
| Repository structure | `docs/architecture/PROJECT-STRUCTURE.md` |
| TDS contract | `docs/tds/TDS-SPEC.md` |
| Cross-tool governance | `docs/governance/AGENTIC-ALIGNMENT-GOVERNANCE.md` |
| Tool-neutral principles | `docs/mesh/PRINCIPLES.md` |
| Codex adapter | `docs/adapters/CODEX.md` |
| Claude adapter | `docs/adapters/CLAUDE.md` |
| Cursor adapter | `docs/adapters/CURSOR.md` |
