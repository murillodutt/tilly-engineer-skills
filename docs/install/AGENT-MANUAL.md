---
tds_id: install.agent_manual
tds_class: adapter
status: active
consumer: installing agents and runtime adapters
source_of_truth: true
evidence_level: L2
tver: 0.1.1
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
| `/tes-update` | Update an already-meshed project | `/tes:update` (compat) |
| `/tes-align` | Re-run alignment after context drift | — |
| `/tes-open-obsidian` | Open `docs/agents/` in Obsidian via CLI or macOS app fallback | — |
| `/tes:field-reports:disable` | Opt out of field-report capture/drain | — |
| `/tes:field-reports:enable` | Restore default field-report behavior | — |

Invalid `/tes:*` slash text still signals TES intent. Agent selects the
smallest safe oracle.

---

## 3. Routes

Selected during install/update. Default: `current`.

| Route | Effect |
|-------|--------|
| `current` | Updates current runtime + its read-only Cortex MCP config |
| `codex` | Prepares `AGENTS.md`, Codex skill, `.codex/config.toml` |
| `claude` | Prepares `CLAUDE.md`, `.claude/skills/**`, plugin skills, `.mcp.json` |
| `cursor` | Prepares rules in `.cursor/rules/**`, `.cursor/mcp.json` |
| `all` | Prepares Codex, Claude, Cursor + all project MCP configs |
| `mcp` | Activates only read-only Cortex MCP layer for detected runtime |
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
   `tes_init.py --target . --yes` and the context + alignment oracles
   before final report.

Step Zero must not block project-context initialization when TES is
already current and only `PROJECT-CONTEXT.md` needs work.

When legacy retirement is true, the agent runs that gate before copying
new TES assets. Legacy retrofit records archive under
`.tes/legacy-retirement/retrofit/`.

---

## 6. Update probe contract

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
| `update_available` | `False` |
| `recommended_update_scope` | `none` |

`STALE_HELPERS` requires update; not current. Repair first with
helper-only Layer Zero before activating MCP configs.

---

## 7. Return state vocabulary

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

## 8. Cortex contract

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

### Backends

| Backend | Behavior |
|---------|----------|
| `lexical` | Deterministic gate; default |
| `xenova` | Requires `@huggingface/transformers` + `Xenova/multilingual-e5-small`; reports `BLOCKED` when unavailable |
| `auto` | Tries Xenova; reports `DEGRADED` when falling back to lexical |

---

## 9. CLI oracle inventory

Agent-callable oracles. Use the TES package root for package checks, or
`--target` when operating on another project or vault.

### Init / update / context

```bash
python3 scripts/tes_init.py --target /path/to/project --yes
python3 scripts/tes_init.py --self-test
python3 scripts/project_context_oracle.py --target /path/to/project && python3 scripts/project_alignment_oracle.py --target /path/to/project
python3 scripts/project_context_oracle.py --self-test && python3 scripts/project_alignment_oracle.py --self-test
python3 scripts/tes_update.py plan --target /path/to/project --json-only
python3 scripts/tes_update.py plan --target /path/to/project --json-only --record-field-report
python3 scripts/tes_update.py --self-test
python3 scripts/tes_legacy_retirement.py plan --target /path/to/project
python3 scripts/tes_legacy_retirement.py apply --target /path/to/project --yes
python3 scripts/tes_legacy_retirement.py audit --target /path/to/project
python3 scripts/tes_legacy_retirement.py --self-test
python3 scripts/root_context.py analyze --target /path/to/project
python3 scripts/root_context.py --self-test
```

`tes_init.py` recertifies package health, scans the target project,
writes `docs/agents/PROJECT-REGISTER.md`, writes
`docs/agents/PROJECT-CONTEXT.md` as the initial project map, creates the
first-pass Obsidian-compatible operating mesh when missing, and stores a
full manifest under `docs/agents/evidence/**`. If a later oracle is
blocked, the run closes as `NEEDS_REVIEW` with evidence instead of
leaving the project uninitialized.

### Field reports

```bash
python3 scripts/field_reports.py status --target /path/to/project
python3 scripts/field_reports.py drain --target /path/to/project
python3 scripts/field_reports.py disable --target /path/to/project
python3 scripts/field_reports.py enable --target /path/to/project
python3 scripts/field_reports.py --self-test
```

### Cortex

```bash
python3 scripts/cortex.py init --target /path/to/project-or-vault
python3 scripts/cortex.py verify --target /path/to/project-or-vault
python3 scripts/cortex.py audit --target /path/to/project-or-vault
python3 scripts/cortex.py rebuild --target /path/to/project-or-vault
python3 scripts/cortex.py curate-plan --target /path/to/project-or-vault --backend lexical
python3 scripts/cortex.py recall --target /path/to/project-or-vault "query"
python3 scripts/cortex.py read-cell --target /path/to/project-or-vault --cell cell-name
python3 scripts/cortex.py absorb-plan --target /path/to/project-or-vault --source docs/agents/cortex/sources/source.md
python3 scripts/cortex.py learn --target /path/to/project-or-vault --source docs/agents/cortex/sources/source.md
python3 scripts/cortex.py reflect --target /path/to/project-or-vault "decision or lesson"
python3 scripts/cortex.py apply --target /path/to/project-or-vault --cell cell-name --claim "durable claim" --evidence sources/source.md --yes
python3 scripts/cortex.py --self-test
```

### Adapters and MCP install

```bash
python3 scripts/install_adapter.py --dry-run --target /path/to/project --adapter all
python3 scripts/install_adapter.py --target /path/to/project --adapter codex --yes
python3 scripts/install_adapter.py --target /path/to/project --adapter all --yes
python3 scripts/install_smoke.py --self-test
python3 scripts/install_smoke.py --route mcp
python3 scripts/claude_plugin_oracle.py --self-test
python3 scripts/install_mcp.py --target /path/to/project --adapter codex --yes
python3 scripts/install_mcp.py --target /path/to/project --adapter all --yes
python3 scripts/install_mcp.py --self-test
python3 scripts/cortex_mcp.py --target /path/to/project-or-vault
python3 scripts/cortex_mcp.py --self-test
python3 scripts/materialize_adapter.py all --check
python3 scripts/materialize_adapter.py all
```

### Validation gates

```bash
python3 scripts/validate_reference_package.py
python3 scripts/validate_reference_package.py --staged-ready
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/retention_metadata.py --check
python3 scripts/validate_reference_graph.py
python3 scripts/platform_surface_oracle.py --self-test
python3 scripts/adapter_parity_readiness.py
python3 scripts/context_mesh_plan.py
python3 scripts/context_mesh_run.py --backend fixture
python3 scripts/context_mesh_convergence.py
python3 src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test
```

### npm wrappers

```bash
npm run validate
npm run install:dry-run
npm run install:smoke
npm run tes:init -- --target /path/to/project --yes
npm run tes:init:self-test
npm run tes:update -- --target /path/to/project
npm run tes:update:self-test
npm run tes:legacy:plan -- --target /path/to/project
npm run tes:legacy:apply -- --target /path/to/project --yes
npm run tes:legacy:audit -- --target /path/to/project
npm run tes:legacy:self-test
npm run install:adapter -- --target /path/to/project --adapter all --yes
npm run mcp:dry-run -- --target /path/to/project --adapter all
npm run mcp:install -- --target /path/to/project --adapter codex --yes
npm run mcp:install -- --target /path/to/project --adapter all --yes
npm run mcp:self-test
npm run field-reports:self-test
npm run field-reports:status -- --target /path/to/project
npm run field-reports:drain -- --target /path/to/project
npm run claude:plugin:oracle
npm run retention:check
npm run reference:graph
npm run docs:size
npm run tds:validate
npm run cortex:init -- --target /path/to/project-or-vault
npm run cortex:verify -- --target /path/to/project-or-vault
npm run cortex:audit -- --target /path/to/project-or-vault
npm run cortex:rebuild -- --target /path/to/project-or-vault
npm run cortex:curate-plan -- --target /path/to/project-or-vault --backend lexical
npm run cortex:recall -- --target /path/to/project-or-vault "query"
npm run cortex:read-cell -- --target /path/to/project-or-vault --cell cell-name
npm run cortex:absorb-plan -- --target /path/to/project-or-vault --source docs/agents/cortex/sources/source.md
npm run cortex:learn -- --target /path/to/project-or-vault --source docs/agents/cortex/sources/source.md
npm run cortex:reflect -- --target /path/to/project-or-vault "decision or lesson"
npm run cortex:apply -- --target /path/to/project-or-vault --cell cell-name --claim "durable claim" --evidence sources/source.md --yes
npm run cortex:self-test
npm run cortex:mcp:self-test
npm run materialize:all
npm run materialize:codex
npm run materialize:cursor
npm run materialize:claude
npm run materialize:check
npm run benchmark:plan
npm run benchmark:run -- --backend fixture
npm run benchmark:converge
npm run adapter:parity:check
npm run platform:surface:check
npm run oracle:self-test
npm run git:diff-check
npm run commit:check
```

Routing matrix: `docs/install/COMMAND-TRIGGERS.md`.

---

## 10. MCP contract

Read-only. Activation writes only `.tes/bin/**` and project-scoped
runtime config. Must not touch global MCP config, secrets, hooks, or
`sources/**`.

### Project-scoped config per runtime

| Runtime | Config path |
|---------|-------------|
| Codex | `.codex/config.toml` |
| Claude Code | `.mcp.json` |
| Cursor | `.cursor/mcp.json` |

### Tool surface

| Tool | Behavior |
|------|----------|
| `cortex_verify` | Validates Cortex structure and contract |
| `cortex_audit` | Finds broken links, missing evidence, loose cells |
| `cortex_recall` | SQLite FTS5 search; falls back to `rg` |
| `cortex_read_cell` | Reads one cell directly from `cells/**` |
| `cortex_absorb_plan` | No-write absorb plan |
| `cortex_curate_plan` | Classifies semantic memory quality risks; no writes to memory or derived indexes |
| `cortex_reflect` | No-write memory + curation proposal |

Write-capable MCP tools are intentionally outside this version.

### Installed helper set

`cortex.py`, `cortex_mcp.py`, `cortex_embed.mjs`, `field_reports.py`,
`tes_update.py`, `tes_legacy_retirement.py`, `root_context.py`,
`tes_init.py`, `project_context_oracle.py`, `project_alignment_oracle.py`,
`tes_open_obsidian.py`.

---

## 11. Field Reports pipeline

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

## 12. Layer split

| Layer | Responsibility | Surface |
|-------|----------------|---------|
| Installer scripts | Download or use the versioned ZIP, verify SHA-256, stage `.tes/setup/<version>/`, refresh manifest-known TES-owned helpers and runtime capabilities | Python + npm |
| LLM layer | Project understanding, semantic governance review | Active agent in IDE window |
| Root runtime files | `AGENTS.md`, `CLAUDE.md`, `CURSOR.md`, Cursor rules — backed up before clean overwrite | Markdown bootloaders |

`/tes-align` and `/tes-open-obsidian` become active through safe runtime
surfaces.

---

## 13. Git safety

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

## 14. Convergence Report contract

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
| Gates | Per-gate disposition |
| Limits | Capabilities not exercised |
| Rollback summary | Baseline head + revert commands |

Long inventories live in the evidence file, not the chat report. Backup
files are rollback artifacts, never new TES surfaces.

---

## 15. Rollback

Use the baseline recorded during Step Zero.

```bash
git reset --hard <baseline-head>
git revert <install-commit>
```

---

## 16. Cross-references

| Need | Source |
|------|--------|
| User-facing manual | `docs/install/USER-MANUAL.html` |
| Installer prompt | `docs/install/MINI-PROMPT.md` |
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
