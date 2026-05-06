---
tds_id: mesh.cortex
tds_class: mesh
status: active
consumer: installer authors, adopters, and agents
source_of_truth: true
evidence_level: L1
---

# Tilly Cortex

Tilly Cortex transforms the LLM Wiki pattern into Tilly memory: versioned,
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
| `LINKS.md` | Human-readable relationship map |
| `CONTRACT.md` | Local Cortex operating contract |

The local recall index lives at:

```text
.tilly/cortex/recall.sqlite
```

That database is never memory and never source of truth. It is a derived cache
for faster recall and must be rebuildable at any time from `sources/**`,
`cells/**`, `MAP.md`, `TRAIL.md`, `LINKS.md`, and `CONTRACT.md`.

## Relationship To Mokh And TDS

Mokh preserves operational memory and events. Cortex is the compiled,
filesystem/Obsidian projection that agents and humans can navigate over time.

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
.tilly/cortex/
  recall.sqlite
```

The `.tilly/cortex/recall.sqlite` file is derived and may be deleted. Running
`rebuild` recreates it from the versioned Cortex artifacts.

## Obsidian Compatibility

Open either the project root or `docs/agents/cortex/` as an Obsidian vault.

Use plain Markdown files and links that remain useful outside Obsidian. Agents
may use Obsidian wikilinks between Cortex cells when that improves graph view,
but source citations stay as explicit repository paths.

Required boundary:

- Do not create or edit `.obsidian/**` during Cortex installation or operation.
- Do not require Dataview, Web Clipper, Canvas, Marp, or community plugins.
- Do not depend on Obsidian state for certification.
- Keep attachments under `sources/assets/**` when the user intentionally adds
  local assets.
- Treat Obsidian graph view as a human navigation aid, not proof of correctness.

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
- at least one explicit evidence ref to `sources/**`, `docs/agents/evidence/**`,
  or an `Assumption:` line.

`audit` fails when a cell misses this minimum. Missing map entries and orphan
cells remain warnings; broken wikilinks and ungrounded cells are failures.

## Rules

- Never modify `sources/**` after import/init.
- Do not file secrets, credentials, private keys, `.env` contents, or regulated
  personal data into Cortex unless the target project has an explicit local
  privacy contract.
- Every compiled claim points to a source path, conversation evidence entry, or
  explicit assumption inside the cell's `## Evidence` section.
- Every `absorb` updates `MAP.md`, `LINKS.md`, and appends to `TRAIL.md`.
- Important relationships appear as normal Markdown links and in `LINKS.md`.
- Prefer links that render in Obsidian and remain readable in GitHub or a plain
  editor.
- Contradictions are retained as contradictions until a newer source or user
  decision resolves them.
- Durable answers may be promoted into `cells/**`; transient chat is not filed.
- Do not call `.tilly/cortex/recall.sqlite` memory.
- Do not allow an answer to depend only on the recall index.

## Operations

| Operation | Expected Agent Behavior |
|-----------|-------------------------|
| `absorb` | Compile one source or a small batch into cells, map, links, and trail |
| `recall` | Search Cortex artifacts through SQLite FTS5 or `rg` fallback |
| `audit` | Find drift, stale claims, contradictions, broken links, ungrounded cells, orphan cells, and unlisted cells |
| `rebuild` | Recreate `.tilly/cortex/recall.sqlite` from versioned Cortex artifacts |
| `learn` | Generate a promotion proposal with evidence; do not write automatically |
| `apply` | Write only with authorization and audit evidence |

## Automation

The package provides a platform-neutral helper:

```bash
python3 scripts/cortex.py init --target /path/to/project-or-vault
python3 scripts/cortex.py verify --target /path/to/project-or-vault
python3 scripts/cortex.py audit --target /path/to/project-or-vault
python3 scripts/cortex.py rebuild --target /path/to/project-or-vault
python3 scripts/cortex.py recall --target /path/to/project-or-vault "query"
python3 scripts/cortex.py absorb-plan --target /path/to/project-or-vault --source docs/agents/cortex/sources/source.md
python3 scripts/cortex.py --self-test
```

The helper scaffolds starter Markdown, migrates legacy Cortex names into the v1
names when safe, validates the required files, checks the parseable trail
heading, reports whether `.obsidian/**` is present, audits basic Cortex health,
rebuilds SQLite FTS5 recall, and falls back to `rg` for recall when FTS5 is not
available.

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
- Do not market Cortex as a RAG killer.

## Installer Boundary

The assisted installer creates the structure and local contract. It does not
bulk-import project history, scrape the web, install search tools, edit
Obsidian config, or claim a complete knowledge graph during installation.

Initial certification proves that:

- the Cortex contract exists;
- source and cell layers are separated;
- `.tilly/cortex/recall.sqlite` is documented as derived and rebuildable;
- the Obsidian boundary is declared without requiring `.obsidian/**`;
- runtime bootloaders route to Cortex when durable project memory is relevant;
- installation evidence states whether Cortex was created, skipped, or blocked.

## MCP Boundary

MCP enters only after CLI, rebuild, and fallback recall are certified. The v1
MCP shape is read-only first: verify, audit, recall, read cell, and absorb-plan.
Write tools require a later controlled cut.
