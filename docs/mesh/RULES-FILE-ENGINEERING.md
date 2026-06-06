---
tds_id: mesh.rules_file_engineering
tds_class: mesh
status: active
consumer: agents authoring CLAUDE.md and AGENTS.md rules files
source_of_truth: true
evidence_level: L1
tver: 0.1.0
---

# Rules File Engineering

> Portable, project-neutral reference. This document describes how to engineer
> rules files for coding agents in general; it is bound to no host project and
> mentions none. Keep it that way — do not introduce names, paths, vocabulary,
> or conventions specific to whatever repository happens to store it. The YAML
> frontmatter above is host-repository governance metadata, **not** part of the
> document; strip it on export and the body stands alone unchanged.

Build instruction for an agent that is about to write or revise a rules file for
Claude Code (`CLAUDE.md`) or Codex (`AGENTS.md`). Read this first, then write.
Cursor (`.mdc`) appears only as a portability note. This file is method, not
enforcement — it shapes how you author, it does not block anything.

## The One Invariant

A rules file is **instruction injected into context, not enforcement.** It
persuades; it does not block. Community audits report guidance-only rules landing
roughly ~25–40% compliance versus ~95% when the same rule is a runtime hook
(figures are community-reported, not published by Anthropic; treat as direction,
not measurement). The official docs back the direction qualitatively: rules
shape behavior but are not a hard enforcement layer. So the first authoring
decision is always classification:

- **Judgment, convention, routing, taste** → rules file. This is its job.
- **Must block network, files, execution, permissions, secrets** → settings/hooks
  (Claude) or `config.toml`/sandbox (Codex). Never the rules file.

If a line in your draft would cause real damage when ignored, it is in the wrong
file. Move it out before you do anything else.

## Universal Authoring Gate

Run this on every draft, both platforms, before declaring it done:

1. **Classify** — every rule is guidance, not enforcement (see invariant above).
2. **Thin root** — the root file states identity, invariants, and routing.
   Detail lives elsewhere (imports/skills on Claude, nested files on Codex). If
   the root explains *how* to do a task step-by-step, it is too fat.
3. **Imperative voice** — write directives the agent obeys ("Do X", "Never Y",
   "Route Z to W"), not prose an editor would write. No hedging, no narration.
4. **Size discipline** — spend bytes deliberately, but for different reasons per
   platform: Codex drops whole files once the chain hits a hard byte cap (lose
   the tail); Claude loads in full but *adherence degrades* as the file grows.
   Either way: cut adjectives, repeated examples, and ceremony.
5. **No conflict** — two rules must not contradict. On conflict the later/closer
   one silently wins, which is invisible drift. Resolve at author time.
6. **Anchored sections** — give the model stable section names it can cite and
   obey (semantic tags or clear headings), not a wall of paragraphs.
7. **Falsifiable** — prefer rules with an observable check ("run `npm test`
   before closeout") over vibes ("write good code"). A rule you cannot verify is
   a rule the agent cannot prove it followed.
8. **Right loading semantics** — for any rule you link out instead of inlining,
   decide eager vs lazy vs path-scoped *on purpose*, and use the mechanism that
   matches the platform (see Linking to External Context). A link is a loading
   decision, not just a tidiness one.

## Claude Code — `CLAUDE.md`

**Architecture: layered memory, concatenated by ascending precedence, loaded in
full.** Files load and merge from broadest to most specific, so a later (more
specific) instruction appears after — and on conflict the **closest-to-cwd /
last-loaded rule wins.** Tiers, lowest precedence first:

- managed policy (e.g. `/Library/Application Support/ClaudeCode/CLAUDE.md`) —
  outranks everything, cannot be excluded; usually not yours to author.
- `~/.claude/CLAUDE.md` — personal, all projects.
- `<project>/CLAUDE.md` (or `.claude/CLAUDE.md`) — project rules, committed.
- `<project>/CLAUDE.local.md` — local overrides, gitignored.

Crucially, `CLAUDE.md` is **loaded in full regardless of length** — there is no
truncation cap. Size is an *adherence* problem, not a survival problem: shorter
files produce better compliance (target well under ~200 lines). Do not author as
if low-precedence content survives a cut — nothing is cut; precedence only
decides who wins a conflict.

Author for these surface facts:

- **Imports with `@path`.** Pull detail on reference (e.g. `@docs/<topic>.md`),
  relative or absolute, recursive up to 4 hops. Use imports to *organize* — they
  do **not** reduce context, since imported files also load in full. The benefit
  is a thin, readable root, not a smaller budget.
- **`.claude/rules/` for path-scoped material.** The modern idiomatic surface for
  long, conditional guidance is a rules file under `.claude/rules/` with
  frontmatter `paths`, so it activates only for matching files — often a cleaner
  fit than `@`-imports for subsystem-specific detail.
- **Semantic tags as anchors.** Named blocks (`<instructions>`, `<routing>`,
  `<locks>`) give the model citable structure it respects. Not required syntax;
  strongly rewarded behavior.
- **Skills, hooks, settings, MCP are separate surfaces — don't smuggle them into
  the rules file.** Reusable workflow → `.claude/skills/**` (progressive
  disclosure: loads only when selected). Enforcement → `settings.json`.
  Automation → hooks. A workflow or block written into `CLAUDE.md` that should
  be a skill is the most common Claude anti-pattern.

Claude anti-patterns: fat root that should have been imports / `.claude/rules/` /
skills; enforcement language with no hook behind it; duplicating a skill's body
inline; treating imports as a way to fit under a budget (they don't — everything
loads); authoring as if size truncates (it doesn't — it degrades adherence).

## Codex — `AGENTS.md`

**Architecture: instruction chain assembled by directory walk, merged
root→leaf.** No fixed three-tier model — a chain along the directory tree, built
once per session:

1. **Global:** `~/.codex/AGENTS.override.md` if it exists, otherwise
   `~/.codex/AGENTS.md` (override wins; only one is read at this level).
2. **Project:** from the project root (usually Git root) **down to the current
   working directory**; in each directory: `AGENTS.override.md`, then
   `AGENTS.md`, then `project_doc_fallback_filenames`.
3. **Merge:** concatenated top→bottom, joined by blank lines. **Files closer to
   the cwd win because they appear later in the prompt.**

Author for these surface facts:

- **Scope by directory, not by user tier.** Subsystem-specific rules go in an
  `AGENTS.md` inside that subdirectory — it enters the chain only when the cwd is
  in or under that directory, and overrides the root because it merges later.
  This is Codex's native project-scoping mechanism (see Linking to External
  Context); do not fake it with one giant root.
- **Hard byte ceiling: `project_doc_max_bytes`, 32 KiB default.** Codex stops
  adding files once the sum hits the cap. Byte economy is architectural here, not
  cosmetic — distribute across directories before inflating the root.
- **`AGENTS.override.md`** is strong same-directory precedence (beats `AGENTS.md`
  in that dir). Use for local overrides without editing the committed file.
- **Operational manual register.** Codex rewards repo structure/architecture,
  code + naming conventions, and explicitly **how to run tests/lint/build** — it
  uses these to generate integrating, self-verifying code. Lean more "runbook"
  than the persona/routing tilt of `CLAUDE.md`.

Codex anti-patterns: one monolithic root instead of per-directory files; relying
on global `~/.codex` rules to carry project specifics; exceeding 32 KiB and
silently losing the tail of the chain; omitting the test/build commands the agent
needs to self-check.

## Claude vs Codex — the axes that break a copy-paste

| Axis | Claude `CLAUDE.md` | Codex `AGENTS.md` |
|------|--------------------|--------------------|
| Discovery | tiers: managed → user → project → project-local | directory walk: global → root → … → cwd |
| Precedence | broad→specific; closest/last-loaded wins on conflict | root→leaf; closest-to-cwd wins |
| Loading | **loaded in full**, no size cap | whole files dropped once the byte cap is hit (tail of chain lost) |
| Fine scope | `@` imports, `.claude/rules/` (paths), skills | one `AGENTS.md` per subdirectory |
| Strong override | `CLAUDE.local.md` (gitignored) | `AGENTS.override.md` (per directory) |
| Size pressure | adherence degrades with length (~200 lines) | `project_doc_max_bytes`, 32 KiB default (hard) |
| Idiomatic shape | thin root + routing + skills/hooks/settings | concatenated chain + per-folder rules |
| Enforcement lives in | settings + hooks | `config.toml` + sandbox |

A rule written for one and copied verbatim usually breaks on the **size model**
(Claude degrades with length; Codex drops whole files past the cap), the
**precedence direction** (who wins on conflict), or the **scoping mechanism**
(import / `rules/` / skill vs nested file). Re-target all three before reusing.

## Linking to External Context

This is a distinct authoring method, not a footnote. The moment you reference
another file from a rules file, you are choosing a **loading semantics**, and the
choice is the whole decision. Get it wrong and you either flood every context
window with situational material or starve the agent of a rule exactly when it
matters.

Reduce every "should I link out?" to one question: **does the agent need this in
every session (eager), only sometimes (lazy/conditional), or only when touching
certain files/dirs (path-scoped)?** Then pick the mechanism that matches — and
the mechanisms are not interchangeable across the two agents.

### The loading-semantics map

| Intent | Claude mechanism | Codex mechanism |
|--------|------------------|------------------|
| Always present, every session | `@path` import (eager, loads in full) or inline | root `AGENTS.md` body (no inline import exists) |
| Present only in a subtree of the repo | subdir `CLAUDE.md` (loads when Claude reads a file there) **or** `.claude/rules/` with `paths:` globs | nested `AGENTS.md` in that subdir (enters the chain only when cwd is in/under it) |
| Present only when a workflow is invoked | **skill** (`.claude/skills/**`, lazy by invocation/relevance) | **skill** (`SKILL.md` loads only when the workflow is selected) |
| Shared across projects / machines | import `@~/.claude/…`, or symlink into `.claude/rules/` | `~/.codex/AGENTS.md` (global), or `project_doc_fallback_filenames` |
| Interop with the *other* agent | `@AGENTS.md` import or `ln -s AGENTS.md CLAUDE.md` | (Codex never reads `CLAUDE.md`; bridge from the Claude side) |

### Claude — what each link actually does

- **`@path` import is eager and does NOT save budget.** Imported files expand and
  load in full at launch alongside the referencing file. Relative paths resolve
  against the importing file (not cwd); absolute and `@~/…` allowed; recursion up
  to **4 hops**. First encounter of an *external* import shows a one-time approval
  dialog — if declined, imports stay disabled silently. Use imports to make the
  root readable, never to "fit under" a size limit.
- **Subdirectory `CLAUDE.md` is lazy by file-read.** A `CLAUDE.md` in a
  subdirectory (e.g. `<subtree>/`) is not loaded at launch — it enters context
  when Claude reads a file in that directory, and (caveat) is **not**
  automatically re-injected after `/compact`, unlike the project-root file.
  Don't put must-always-hold rules there.
- **`.claude/rules/` is the modern path-scoped surface.** Files with `paths:`
  glob frontmatter load only when Claude touches matching files; without `paths:`
  they load at launch with the same priority as `.claude/CLAUDE.md`. Prefer this
  over `@`-imports for conditional, subsystem-specific material — it is the
  cleaner fit and it actually keeps situational rules out of the base context.
- **Skill is lazy by invocation.** For multi-step procedures or anything that
  only matters on a specific task, a skill is correct, not an import — it stays
  out of context until invoked or judged relevant.

### Codex — the link is spatial, never inline

Codex has **no `@import`, include, or link directive.** Do not invent one;
writing `@docs/foo.md` in `AGENTS.md` puts the literal string in context, not the
file. Beyond the global `~/.codex/AGENTS.md`, the only ways to bring in
project-scoped context are:

- **Place a nested `AGENTS.md`** in the relevant directory. It is "linked" purely
  by location: it joins the chain only when the cwd is in or under that directory,
  overriding the root because it merges later. This is Codex's entire scoping and
  external-context model.
- **`project_doc_fallback_filenames`** lets the project's existing doc names act
  as the rules file, instead of pointing at them from inside `AGENTS.md`.

So a Claude `@import` and a Codex nested file are **not** the same operation:
the import is an explicit eager pull anywhere in the tree; the nested file is an
implicit spatial activation. Porting one to the other means re-expressing intent
as location (Claude→Codex) or as an explicit reference / rule-scope
(Codex→Claude), never copying syntax.

### Cross-agent bridging

When one repo must serve both agents, link from the Claude side: a `CLAUDE.md`
that is just `@AGENTS.md` (plus any Claude-only rules below it), or a symlink
`ln -s AGENTS.md CLAUDE.md`. This keeps one source of truth and respects that
Codex will never read `CLAUDE.md`. Do not maintain two divergent rules files by
hand — that is the conflict-drift anti-pattern at the repo level.

## Portability note — Cursor `.mdc`

Cursor rules (`.cursor/rules/*.mdc`) add an orthogonal axis the other two lack:
**activation metadata in frontmatter** (`alwaysApply`, `globs`, `description`),
so a rule can be always-on, glob-scoped, or model-selected. This is a third way
of expressing the same loading-semantics decision from Linking to External
Context — declaratively in frontmatter rather than by import (Claude) or by
location (Codex): `alwaysApply: true` = eager, `globs` = path-scoped,
`description` = lazy/model-selected. When porting: map intent, not syntax — a
Claude import or a Codex nested file becomes a glob-scoped `.mdc`; the always-on
root becomes `alwaysApply: true`. Same invariant holds: guidance, not
enforcement.

## Closeout Check

Before claiming a rules file is done:

- Universal gate (8 items) passes.
- No enforcement language without a hook/config behind it.
- Targeted to the right platform's size model, precedence, and scoping mechanism.
- Size right for the platform (Codex: well below 32 KiB per chain so nothing
  truncates; Claude: root thin enough for high adherence — it won't truncate, but
  bloat lowers compliance).
- Every falsifiable rule names its check.
