---
tds_id: mesh.cortex
tds_class: mesh
status: active
consumer: installer authors, adopters, and agents
source_of_truth: true
evidence_level: L2
tver: 0.5.2
---

# TES Cortex

TES Cortex transforms the LLM Wiki pattern into Tilly memory: versioned,
auditable, filesystem-first, Obsidian-visible, and governed by contract.

Cortex is not copied LLM Wiki terminology. It is the Tilly-native projection of
compiled project memory. The filesystem Markdown artifacts are the source of
truth; SQLite, Obsidian, MCP, and LLM responses are access, visualization, or
acceleration surfaces.

## Memory Contract

The v1 stack is closed:

```text
Markdown filesystem is truth. SQLite FTS5 is derived recall. rg is fallback.
```

Memory lives in the versioned Cortex artifacts:

| Artifact | Role |
|----------|------|
| `sources/**` | Immutable user-curated sources, notes, clips, transcripts, and references |
| `cells/**` | Compiled and evolving knowledge for entities, concepts, decisions, and syntheses |
| `MAP.md` | Navigable catalog with links, one-line summaries, and source status |
| `TRAIL.md` | Append-only chronological record of Cortex evolution |
| `LINKS.md` | Plain-language relationship map |
| `CONTRACT.md` | Local Cortex operating contract |

The local recall index lives at:

```text
.tes/cortex/recall.sqlite
.tes/cortex/semantic.sqlite
```

These databases are never memory and never source of truth. They are derived
caches for faster recall and semantic curation. They must be rebuildable at any
time from `sources/**`, `cells/**`, `MAP.md`, `TRAIL.md`, `LINKS.md`, and
`CONTRACT.md`.

## Relationship To Mokh And TDS

Mokh preserves operational memory and events. Cortex is the compiled,
filesystem/Obsidian projection that agents and people can navigate over time.

TDS documents contracts, evidence, and governed explanations. TDS does not
become memory; Cortex compiles durable knowledge from sources, questions,
decisions, and lessons.

## Target Shape

The assisted installer creates or retrofits this structure:

```text
docs/agents/cortex/
  CONTRACT.md
  MAP.md
  TRAIL.md
  LINKS.md
  sources/
    README.md
    assets/
  cells/
.tes/cortex/
  recall.sqlite
  semantic.sqlite
```

The `.tes/cortex/recall.sqlite` and `.tes/cortex/semantic.sqlite` files are
derived and may be deleted. Running `rebuild` recreates recall. Running
`curate-plan` recreates the semantic curation index from `cells/**`.

## Obsidian Compatibility

Open `docs/agents/` as the TES mesh vault, or `docs/agents/cortex/` only when
you want a focused memory workspace.

Use plain Markdown files and links that remain useful outside Obsidian. Agents
may use Obsidian wikilinks between Cortex cells when that improves graph view,
but source citations stay as explicit repository paths.

Required boundary:

- Do not create or edit `.obsidian/**` during Cortex installation or operation.
- Do not require Dataview, Web Clipper, Canvas, Marp, or community plugins.
- Do not depend on Obsidian state for certification.
- Keep attachments under `sources/assets/**` when the user intentionally adds
  local assets.
- Treat Obsidian graph view as a user navigation aid, not proof of correctness.

## Starter File Minimums

| File | Minimum Content |
|------|-----------------|
| `CONTRACT.md` | Cortex purpose, artifact truth, SQLite-derived boundary, cell convention, privacy lock, Obsidian boundary |
| `MAP.md` | H1, empty sections for sources/cells/syntheses, and a note that agents read it first |
| `TRAIL.md` | H1 and one install/init entry using the parseable heading contract |
| `LINKS.md` | H1 and an empty adjacency-list section |
| `sources/README.md` | Warning that sources are user-owned and must not be edited by agents |

## Cell Integrity

Cells are compiled memory, not loose summaries. A cell under `cells/**` must
have:

- exactly one H1;
- a `## Claim` section with the durable claim or synthesis;
- a `## Evidence` section;
- at least one explicit evidence ref to `sources/**`,
  `docs/agents/cortex/sources/**`, `docs/agents/evidence/**`, or an
  `Assumption:` line.

`audit` fails when a cell misses this minimum. Missing map entries and orphan
cells remain warnings; broken wikilinks and ungrounded cells are failures.

Evidence refs are repository-relative by contract. Absolute filesystem paths,
home-directory paths, drive-letter paths, traversal refs, derived caches, run
scratch, checkpoints, benchmark outputs, recall indexes, and semantic indexes
do not satisfy `## Evidence`. If a claim can only be grounded by local context
that is not retained under an allowed evidence root, write an `Assumption:`
line and keep the cell reviewable instead of embedding the local path.

`curate-plan` adds the semantic gate above structural integrity. It classifies
merge candidates, split candidates, link candidates, semantic tensions,
evidence gaps, redundancy warnings, and reject candidates. It never writes
memory artifacts. Every curation candidate carries an action, rationale, and
next step so an agent can decide what to merge, split, link, resolve, ground, or
reject without inventing the reason.

Split detection uses compound pressure, not raw bullet count alone. A narrow
cell with many evidence bullets may remain valid when the claim is small and
the extra bullets are evidence support. A split candidate is raised when bullet
pressure combines with claim bullets, non-evidence bullets, long claims, many
headings, high line count, or mixed-topic markers.

## Curation Conveyor

Cortex does not store everything that passes through the agent window. Cortex
receives, classifies, separates, rejects, consolidates, and publishes only
knowledge with evidence, route, and authorization.

The conveyor has three gates:

| Gate | Contract |
|------|----------|
| `reflection_gate` | `reflect` decides whether durable capture or curation review is due. It writes nothing. |
| `semantic_curation_gate` | `curate-plan` classifies duplicates, compound swollen cells, nearby unlinked cells, tensions, evidence gaps, redundancy, and transient material. It writes no memory. |
| `promotion_gate` | `apply --yes` is the only built-in path that writes compiled memory, and only with explicit evidence and authorization. |

`learn` and `reflect` reject or no-op generic prompts that lack source evidence
or a specific durable lesson. Weak inputs return an explicit evidence gap or
no-capture reason instead of producing a plausible-looking memory proposal.

## Scope Boundary

Cortex command output carries the runtime scope defined in
`docs/mesh/SCOPE-CONTRACT.md`. The scope identifies the local run through an
opaque project fingerprint, adapter, agent, run id, source, bounded evidence
reference, timestamp, and status or trust level.

Scope is coordination metadata. It is not a Cortex cell, not durable memory,
not a project name, and not authorization to write. A scope failure must fail
closed instead of falling back to broad target assumptions.

## Event Ledger Boundary

`docs/mesh/EVENT-LEDGER.md` defines read-only lifecycle event inspection.
Event ledger entries are coordination evidence, not Cortex memory. Inspecting a
ledger must not append to `TRAIL.md`, create cells, rebuild recall, or promote
events into durable knowledge.

## Checkpoint Boundary

`docs/mesh/CHECKPOINTS.md` defines TTL resumability state. Checkpoints may help
an agent resume work, but they are not Cortex cells, not certification
evidence, not Event Ledger records, and not Field Reports. Creating or cleaning
a checkpoint must not append to `TRAIL.md`, create cells, rebuild recall, or
authorize durable memory writes.

`curate-plan` statuses:

| Status | Meaning |
|--------|---------|
| `PASS` | Cells are semantically healthy within the current thresholds |
| `FAIL` | Merge, split, tension, evidence-gap, or reject candidates require curation |
| `DEGRADED` | `--backend auto` could not use Xenova and fell back to lexical curation |
| `BLOCKED` | Explicit `--backend xenova` could not run because runtime, package, or model access is unavailable |

The semantic index is:

```text
.tes/cortex/semantic.sqlite
```

It stores path, content hash, model, dimensions, and serialized vectors derived
from `cells/**`. It is an acceleration and certification artifact, not memory.
The deterministic package gate uses `--backend lexical`. Real environments may
run `--backend xenova` or `--backend auto` with the optional
`@huggingface/transformers` dependency and the default
`Xenova/multilingual-e5-small` model. If explicit Xenova cannot run, the status
is `BLOCKED`; if `auto` falls back to lexical, the status is `DEGRADED` unless
memory-quality failures are also present.

## Rules

- Never modify `sources/**` after import/init.
- Do not file secrets, credentials, private keys, `.env` contents, or regulated
  personal data into Cortex unless the target project has an explicit local
  privacy contract.
- Every compiled claim points to `sources/**`,
  `docs/agents/cortex/sources/**`, `docs/agents/evidence/**`, or an explicit
  assumption inside the cell's `## Evidence` section.
- Do not use absolute local paths, derived caches, benchmark run artifacts,
  checkpoints, recall indexes, or semantic indexes as durable cell evidence.
- Every `absorb` updates `MAP.md`, `LINKS.md`, and appends to `TRAIL.md`.
- Important relationships appear as normal Markdown links and in `LINKS.md`.
- Prefer links that render in Obsidian and remain readable in GitHub or a plain
  editor.
- Contradictions are retained as contradictions until a newer source or user
  decision resolves them.
- Durable answers may be promoted into `cells/**`; transient chat is not filed.
- Do not call `.tes/cortex/recall.sqlite` memory.
- Do not call `.tes/cortex/semantic.sqlite` memory.
- Do not allow an answer to depend only on the recall index.

## Operations

| Operation | Expected Agent Behavior |
|-----------|-------------------------|
| `absorb` | Compile one source or a small batch into cells, map, links, and trail |
| `recall` | Search Cortex artifacts through SQLite FTS5 or `rg` fallback |
| `audit` | Find drift, stale claims, contradictions, broken links, ungrounded cells, orphan cells, and unlisted cells |
| `rebuild` | Recreate `.tes/cortex/recall.sqlite` from versioned Cortex artifacts |
| `curate-plan` | Rebuild the semantic curation index and classify memory-quality risks without writing memory |
| `learn` | Generate a promotion proposal with evidence; do not write automatically |
| `reflect` | No-write closure reflex that decides whether a memory proposal or curation review is due |
| `apply` | Write only with authorization and audit evidence |
| `read-cell` | Read a single cell under `cells/**` without using the derived index |
| `health` | Read-only operator health view with mutability classes |
| `peek` | Read-only operator recall or cell inspection |
| `review` | Read-only operator audit, curation, and reflection review |
| `checkpoint` | Write TTL checkpoint state only after explicit `--yes` |
| `remember` | Durable memory write through the same authorization and evidence gate as `apply` |
| `forget` | Blocked destructive operator until consolidation gate evidence exists |
| `consolidation_gate.py` | Lock and certify observed durable-memory writes without deleting memory |

## Operator Mutability

| Operator | Mutability class | Contract |
|----------|------------------|----------|
| `health` | `read-only` | Reports verify, audit, recall-index presence, semantic-index presence, and operator inventory. |
| `peek` | `read-only` | Reads recall results or a single cell. |
| `review` | `read-only` | Runs audit, no-write curation, and reflection without semantic-index writes. |
| `checkpoint` | `checkpoint-state-write` | Requires `--yes`; writes only `.tes/checkpoints/**`. |
| `remember` | `durable-memory-write` | Requires `--yes`, claim, evidence, and the Cortex write gate. |
| `forget` | `blocked-destructive` | Returns `BLOCKED` even with `--yes` until consolidation owns observed-write and rollback evidence. |

Read-only operators must report `writes: []` and `derived_writes: []`.

## Automation

The package provides a platform-neutral helper:

```bash
python3 scripts/cortex.py init --target /path/to/project-or-vault
python3 scripts/cortex.py verify --target /path/to/project-or-vault
python3 scripts/cortex.py audit --target /path/to/project-or-vault
python3 scripts/cortex.py rebuild --target /path/to/project-or-vault
python3 scripts/cortex.py curate-plan --target /path/to/project-or-vault --backend lexical
python3 scripts/cortex.py recall --target /path/to/project-or-vault "query"
python3 scripts/cortex.py read-cell --target /path/to/project-or-vault --cell path-or-stem
python3 scripts/cortex.py learn --target /path/to/project-or-vault --source docs/agents/cortex/sources/source.md
python3 scripts/cortex.py reflect --target /path/to/project-or-vault "decision or lesson"
python3 scripts/cortex.py absorb-plan --target /path/to/project-or-vault --source docs/agents/cortex/sources/source.md
python3 scripts/cortex.py apply --target /path/to/project-or-vault --cell path-or-stem --claim "durable claim" --evidence sources/source.md --yes
python3 scripts/cortex.py health --target /path/to/project-or-vault
python3 scripts/cortex.py peek --target /path/to/project-or-vault "query"
python3 scripts/cortex.py review --target /path/to/project-or-vault --backend lexical
python3 scripts/cortex.py checkpoint --target /path/to/project-or-vault --id run-id --yes
python3 scripts/cortex.py remember --target /path/to/project-or-vault --cell path-or-stem --claim "durable claim" --evidence sources/source.md --yes
python3 scripts/cortex.py forget --target /path/to/project-or-vault --cell path-or-stem --evidence sources/source.md --yes
python3 scripts/cortex.py --self-test
python3 scripts/cortex_operator_oracle.py --self-test
```

The helper scaffolds starter Markdown, migrates legacy Cortex names into the v1
names when safe, validates the required files, checks the parseable trail
heading, reports whether `.obsidian/**` is present, audits basic Cortex health,
rebuilds SQLite FTS5 recall, falls back to `rg` for recall when FTS5 is not
available, proposes promotions through `learn`, and applies cells only through
explicitly authorized `apply --yes` runs that pass audit and rebuild.

`reflect` is the low-friction capture layer. Bootloaders and skills should call
it before final responses for material work and before commits when Cortex
exists. It inspects the local Git diff, emits a no-write promotion proposal when
durable learning is likely, and marks curation as due when the current diff
crosses the default 500 changed-line budget. When curation is due, agents should
run `curate-plan` and use the returned classifications before proposing
compaction, split, or redundancy removal with a visible diff. Curation never
means automatic deletion.

Long closure notes do not become full cell filenames. `reflect` caps proposed
cell slugs and adds a deterministic hash plus `cell_name_reason`; operators
should still replace the suggestion with a short claim-specific cell name before
authorized `apply --yes` promotion.

`apply` writes only `cells/**`, `MAP.md`, `LINKS.md`, `TRAIL.md`, and the
derived recall index rebuilt from those artifacts. It refuses to write without
`--yes`, refuses ungrounded evidence, refuses to overwrite an existing cell
unless `--update` is passed, and never writes in `sources/**`.

`remember` is the operator spelling for the same authorized durable-memory path
as `apply`. `checkpoint` is not durable memory and writes only TTL state.
`forget` is intentionally blocked until the consolidation gate can prove
observed write behavior, rollback, and review evidence.

## Consolidation Gate

Consolidation is the review layer after an authorized durable-memory write. It
does not decide from intent, event records, checkpoints, or subagent claims
alone.

```bash
python3 scripts/consolidation_gate.py lock --target /path/to/project-or-vault --id run-id --evidence sources/source.md --yes
python3 scripts/consolidation_gate.py certify --target /path/to/project-or-vault --id run-id --observed-write .tes/cortex/consolidation/observed.json --review-status APPROVED --rollback-ref git:<sha> --evidence sources/source.md
python3 scripts/consolidation_gate.py --self-test
```

`lock` writes only `.tes/cortex/consolidation/**` and requires `--yes`.
`certify` is read-only. It returns `CERTIFIED` only when a valid lock, approved
review, rollback reference, allowed evidence, and observed Cortex cell, MAP,
LINKS, and TRAIL write result are present. Event-only records, checkpoint-only
state, stale locks, ambiguous review, or subagent direct memory writes return
`BLOCKED` or `NEEDS_REVIEW`.

Compatibility aliases `scaffold`, `check`, and `lint` may remain in the helper
only to prevent transition friction. Documentation and package scripts use
`init`, `verify`, and `audit`.

This makes Cortex portable across Codex, Claude Code, Cursor, OpenCode, and
generic terminal agents.

## Trail Contract

`TRAIL.md` uses parseable headings:

```text
## [YYYY-MM-DD] init | <scope>
## [YYYY-MM-DD] absorb | <source or topic>
## [YYYY-MM-DD] recall | <question or synthesis>
## [YYYY-MM-DD] audit | <scope>
## [YYYY-MM-DD] repair | <issue>
## [YYYY-MM-DD] rebuild | <index>
```

This lets agents and maintainers use simple tools such as:

```bash
rg "^## \\[" docs/agents/cortex/TRAIL.md
```

## Governance

Every Cortex cut should declare:

```yaml
cortex_cut:
  consumer:
  camada: contrato|estrutura|cli|obsidian|adapter|mcp
  escreve_em:
  nao_toca:
  oracle:
  rollback:
```

No-go:

- Do not implement MCP before the CLI is certified.
- Do not edit `.obsidian/**`.
- Do not write in `sources/**` after import/init.
- Do not promote automatically from LLM output.
- Do not maintain old and new Cortex names in parallel.
- Do not call the derived index memory.
- Do not let reflection or curation delete content automatically.
- Do not describe certified Cortex capability as experimental. Use `blocked`,
  `degraded`, `not available`, `certified`, or `fail`.
- Do not market Cortex as a RAG killer.

## Installer Boundary

The assisted installer creates the structure and local contract. It does not
bulk-import project history, scrape the web, install search tools, edit
Obsidian config, or claim a complete knowledge graph during installation.

Initial certification proves that:

- the Cortex contract exists;
- source and cell layers are separated;
- `.tes/cortex/recall.sqlite` is documented as derived and rebuildable;
- the Obsidian boundary is declared without requiring `.obsidian/**`;
- runtime bootloaders route to Cortex when durable project memory is relevant;
- read-only Cortex MCP is activated for selected runtime routes or explicitly
  blocked with a reason;
- `curate-plan` is available as a no-write curation gate;
- `health`, `peek`, and `review` are available as no-write operator commands;
- `checkpoint`, `remember`, and `forget` report explicit mutability classes;
- installation evidence states whether Cortex was created, skipped, or blocked.

## MCP Boundary

MCP enters only after CLI, rebuild, fallback recall, and no-write curation are
certified. The v1 MCP shape is read-only first: verify, audit, recall, read
cell, absorb-plan, curate-plan, and reflect. Write tools require a later
controlled cut.

The first read-only stdio surface is governed by
`docs/mesh/CORTEX-MCP.md` and implemented by `scripts/cortex_mcp.py`. It
is activated by `scripts/install_mcp.py`, delegates to the deterministic Cortex
CLI functions, and does not promote, rewrite, or persist knowledge.
