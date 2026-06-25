---
tds_id: evidence.adapter_bootloader_review_20260604
tds_class: evidence
status: archived
consumer: maintainers, adapter authors, and release reviewers
source_of_truth: false
evidence_level: L2
tver: 0.1.1
---

# Adapter Bootloader Review — Cursor, Codex, Claude Code

> Superseded snapshot. This review describes the bootloaders at their pre-migration sizes (CLAUDE.md 248, AGENTS.md 252, CURSOR.md 99 lines) and recorded two divergences to revisit: the uneven confidentiality statement and the GPS wording lagging the ADR 0004 capsule mode. The bootloader-to-skill migration (TES 0.3.165) acted on both — bootloaders were thinned to lazy-anchor form and confidentiality was made even across all three. The current contract is `bootloader-concept-inventory-2026-06-04.md` plus the migration Super SPEC closeout. Retained as the pre-migration baseline, not the current state.

Read-only review of the three adapter context bootloaders. No file was changed. Each platform's particularity is respected; this document records what each file says, how they differ, and where they diverge from the current runtime, so a future maintainer can decide whether any divergence is intentional.

Reviewed sources:

- `src/adapters/cursor/CURSOR.md` (99 lines)
- `src/adapters/codex/AGENTS.md` (252 lines)
- `src/adapters/claude/CLAUDE.md` (248 lines)

These three are the source of the root bootloaders materialized into a target project as `CURSOR.md` / `AGENTS.md` / `CLAUDE.md` (see `scripts/root_context.py` `ROOT_FILES`). They are composed with a project overlay through the `TES:CORE` / `TES:PROJECT-OVERLAY` markers at install time.

## Why The Three Are Not Copies

Each file is shaped to its host, and that is correct — they must not be identical:

| Aspect | Cursor (`CURSOR.md`) | Codex (`AGENTS.md`) | Claude (`CLAUDE.md`) |
|--------|----------------------|---------------------|----------------------|
| Document form | Prose guide ("Using This Repo With Cursor") | XML-tagged blocks (`<instructions>`, `<routing>`, `<locks>`) | Numbered markdown headings (`## 1. Think Before Coding`) |
| Primary runtime surface | `.cursor/rules/*.mdc` rules | `AGENTS.md` + `.agents/skills/**` | `CLAUDE.md` + `.claude/skills/**` |
| Routing style | Intent + alias lists, natural prose | `<routing>` table to `.agents/skills/tes-*` | Prose "TES Shortcuts" to `.claude/skills/tes-*` |
| Length / depth | Shortest (99 lines); points outward to rules | Deepest routing table; full skill inventory | Full discipline text inline (the four principles spelled out) |
| Mantra Gate | Not present as a section (routing only, implicitly via rules) | `<mantra_gate>` routing block to the skill | `## Mantra Gate` routing block to the skill |

This is the intended design: the host that loads a single file (Claude) carries the discipline inline; the host with a strong skill system (Codex) keeps the bootloader thin and routes to skills; Cursor, which loads `.mdc` rules, keeps the root file as an outward pointer. Respecting this is correct and should not be "unified".

## Shared Behavioral Core (Consistent Across All Three)

All three carry the same behavioral contract, each in its native form:

- The four principles: Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution.
- The Runtime-First Product Rule (verbatim across all three): build the smallest durable runtime slice; no governance-only cycles, long SPECs before code, placeholder boundaries, or throwaway implementations.
- The success formula `E = A * S * C * V`.
- Field Reports active-by-default with sanitized-only collection.
- The same `/tes-*` canonical intents and `/tes:*` aliases, including the explicit-invocation brake on `/tes-prospect`, `/tes-mine`, `/tes-goal-maestro`.
- The bilingual (EN/PT) natural-intent phrasing for align/map/update/init.

The behavioral source-of-truth statement is explicit in `CURSOR.md` ("Keep Cursor, Claude, and Codex variants synchronized at the behavioral level") and is honored by the other two in practice.

## Divergences Worth Recording (Not Defects To Fix Here)

These are differences between the three files, or between the files and the current runtime. They are recorded for a future maintainer decision; this review changes nothing.

1. **Private-confidentiality section is uneven.**
   - `CLAUDE.md` has an explicit `## Private Project Confidentiality` section (placeholder vocabulary, no real project names/paths).
   - `AGENTS.md` and `CURSOR.md` do not carry that section; Codex relies on the skill layer and locks (`Do not add ... secrets`), Cursor does not state it.
   - Note: the repository was made public on 2026-06-04. The maintainer's stated sanitization should be confirmed against the public history; this review does not assess content sanitization, only that the three bootloaders state the confidentiality rule unevenly.

2. **GPS/MAP language predates the ADR 0004 GPS capsule mode (0.3.163).**
   - All three still describe `/tes-map` / `project GPS` against the `docs/agents/**` model (the attached-mode path).
   - The shipped GPS capsule mode added a `.tes/gps` / `.tes/context` projection and made `docs/agents/**` an export gated on docs-mesh. None of the three bootloaders mention capsule mode or the capsule projection.
   - This is consistent with "no changes" and is not necessarily wrong (the attached-mode wording is still accurate when docs-mesh is attached), but the bootloaders and the delivered runtime are now out of step on this point.

3. **Skill-routing coverage differs in shape.**
   - `AGENTS.md` `<routing>` lists every skill explicitly (goal-maestro, prospect, mine, cortex, mcp, doctor, adapter, bench, bump, ...).
   - `CLAUDE.md` lists the same intents in prose under "TES Shortcuts".
   - `CURSOR.md` lists the canonical `/tes-*` intents plus a longer `/tes:*` alias set, but does not enumerate goal-maestro/prospect/mine as separate routed skills (it routes alignment/obsidian intents explicitly and leaves the rest to the rule files).
   - All three honor the explicit-invocation brake; the difference is presentation completeness, not contract.

4. **`tes-init` gate detail is inline in Codex and Claude, absent in Cursor.**
   - `AGENTS.md` and `CLAUDE.md` carry the full Install/Update Gate → Project Context Gate → Project-Start Gate flow and the postinstall sentinel states (`complete` / `needs_review` / `running`) inline.
   - `CURSOR.md` does not spell out the gate flow; it points to the rule files and command intents. For Cursor, that is appropriate (the detail lives in `.cursor/rules/**`), but it does mean a Cursor reader of the root file alone sees less of the init contract than a Codex/Claude reader.

5. **Memory Lifecycle Boundary present in Codex and Claude, not in Cursor.**
   - The Memory Lifecycle Boundary block (recall read-only, write gate, checkpoint ≠ memory, subagent return is evidence-only) is present verbatim in `AGENTS.md` and `CLAUDE.md`, and absent from `CURSOR.md`.

## Platform-Particularity Notes (Respect, Do Not Normalize)

- **Cursor**: the root file is correctly a thin pointer to `.cursor/rules/*.mdc`; Cursor's runtime authority is the rule files, not the root markdown. The "Do not copy `.cursor/** into Codex or Claude`" lock is a correct isolation statement. Keeping it short is a feature.
- **Codex**: the XML-tagged structure (`<instructions>`, `<routing>`, `<mantra_gate>`, `<locks>`) matches how Codex parses `AGENTS.md`. The bootloader-as-routing-only discipline (gate logic lives in the skill) is explicit and should be preserved.
- **Claude Code**: the inline discipline (full four-principle text, examples, the "these guidelines are working when..." paragraph) suits a host that loads one file as primary context. The numbered-heading form is Claude-native.

## Review Verdict

The three bootloaders are coherent, share one behavioral contract, and each respects its host's loading model — that part is healthy and should not be flattened into a single template. The divergences above are mostly presentation depth (Cursor thinner by design) plus two substantive items a maintainer may want to revisit deliberately, in a future change, not here:

- the uneven private-confidentiality statement (now that the repo is public);
- the GPS wording lagging behind the shipped ADR 0004 GPS capsule mode.

No file was modified by this review.
