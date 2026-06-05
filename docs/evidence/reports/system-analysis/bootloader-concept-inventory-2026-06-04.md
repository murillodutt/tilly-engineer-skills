---
tds_id: evidence.bootloader_concept_inventory_20260604
tds_class: evidence
status: active
consumer: maintainers, adapter authors, skill authors, and the parity oracle
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# Bootloader Concept Inventory — Migration Contract (SPEC-000)

Persistent, machine-readable inventory of every concept currently carried by the
three adapter bootloaders, with its disposition for the bootloader-to-skill
migration. This document is the contract for SPEC-002..004 (what each anchor may
keep, move, or delete) and the source-of-truth the SPEC-005 parity oracle reads
to verify that no certified knowledge was lost.

Baseline (last-known-good, recorded at SPEC-000): TES `0.3.164`; bootloaders and
skills as committed at `1e3e639`; `root_context.py --self-test` PASS;
`validate_tds` PASS (153 docs); `private_vocabulary_oracle` PASS. The migration
must preserve `root_context.py` composition (`TES:CORE` / `TES:PROJECT-OVERLAY`)
and the capsule install/uninstall/attach/detach contract from ADR 0004.

Baseline line counts (source bootloaders and lazy targets):

| Surface | Lines | Role |
|---------|------:|------|
| `src/adapters/claude/CLAUDE.md` | 247 | Claude bootloader (anchor target) |
| `src/adapters/codex/AGENTS.md` | 252 | Codex bootloader (anchor target) |
| `src/adapters/cursor/CURSOR.md` | 99 | Cursor prose bootloader (anchor target) |
| `src/adapters/cursor/rules/tes-guidelines.mdc` | 238 | Cursor always-on rule; ROOT_FILE under composition (anchor target) |
| `src/adapters/cursor/rules/tes-runtime-capabilities.mdc` | 101 | Cursor capability rule; lazy target (must become `alwaysApply: false`) |
| `src/adapters/claude/skills/tes-guidelines/SKILL.md` | 161 | Claude lazy skill (expansion home) |
| `src/adapters/claude/skills/tes-init/SKILL.md` | 124 | Claude init skill (expansion home) |
| `src/adapters/codex/skills/tes-engineering-discipline/SKILL.md` | 183 | Codex lazy skill (expansion home) |

`root_context.py` `ROOT_FILES` treats `AGENTS.md`, `CLAUDE.md`, `CURSOR.md`, and
`.cursor/rules/tes-guidelines.mdc` as composed bootloaders (TES:CORE + overlay).
`.cursor/rules/tes-runtime-capabilities.mdc` is NOT a ROOT_FILE, so it is the
free lazy surface that may receive migrated Cursor capability detail.

## Disposition Vocabulary

- `keep-as-anchor`: stays in the bootloader as a one-line falsifiable anchor.
  Its expansion (where one exists) also lives once in the skill; the anchor must
  not be the same paragraph as the expansion (anchor-not-copy).
- `already-in-skill`: full detail already exists, complete and current, in the
  host's lazy skill/rule. The bootloader copy is duplicated and must be deleted
  in SPEC-002..004; the anchor keeps at most a one-line pointer.
- `move-to-skill`: full detail exists ONLY in the bootloader today; SPEC-001
  must move it into the host's lazy skill/rule before SPEC-002..004 deletes it
  from the bootloader. Deleting before moving would lose certified knowledge.

## Anchor-Not-Copy Invariant

A `keep-as-anchor` concept appears once as a short anchor in the bootloader and
once as expansion in the skill. The SPEC-005 oracle asserts both the byte-level
rule (no identical paragraph in both places) and the semantic rule (per concept:
a short anchor present in the bootloader AND a single expansion present in the
skill/rule).

## Machine-Readable Inventory

The block below is the parity-oracle contract. `host` is the bootloader the
concept lives in today; `target_surface` is where its expansion must live after
migration. `anchor` is the one-line anchor that stays in the bootloader for
`keep-as-anchor` concepts (empty for pure `already-in-skill`/`move-to-skill`
detail that needs no standing anchor beyond the routing map).

```yaml
inventory_version: 1
baseline_commit: "1e3e639"
baseline_version: "0.3.164"
hosts:
  claude:
    bootloader: src/adapters/claude/CLAUDE.md
    skills:
      - src/adapters/claude/skills/tes-guidelines/SKILL.md
      - src/adapters/claude/skills/tes-init/SKILL.md
  codex:
    bootloader: src/adapters/codex/AGENTS.md
    skills:
      - src/adapters/codex/skills/tes-engineering-discipline/SKILL.md
      - src/adapters/codex/skills/tes-init/SKILL.md
  cursor:
    bootloader: src/adapters/cursor/CURSOR.md
    anchor_rule: src/adapters/cursor/rules/tes-guidelines.mdc
    lazy_rule: src/adapters/cursor/rules/tes-runtime-capabilities.mdc
concepts:
  - id: core-contract
    label: "Core contract (assumptions visible / scope smaller / surgical / falsifiable)"
    hosts: [claude, codex, cursor]
    disposition: keep-as-anchor
    anchor: "Core contract: Assumptions visible. Scope smaller. Edits surgical. Success falsifiable."
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/skills/tes-engineering-discipline/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: four-principles
    label: "Four principles: Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution"
    hosts: [claude, codex, cursor]
    disposition: keep-as-anchor
    anchor: "Four gates: Think Before Coding; Simplicity First; Surgical Changes; Goal-Driven Execution."
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/skills/tes-engineering-discipline/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: runtime-first
    label: "Runtime-First Product Rule"
    hosts: [claude, codex, cursor]
    disposition: keep-as-anchor
    anchor: "Runtime-first: build the smallest durable runtime slice; no governance-only cycles, long SPECs before code, placeholder boundaries, or throwaway implementations."
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/skills/tes-engineering-discipline/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: success-formula
    label: "Success Formula E = A * S * C * V"
    hosts: [claude, codex, cursor]
    disposition: keep-as-anchor
    anchor: "Success formula: E = A * S * C * V (assumptions, scope, change, verification); any zero means stop."
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/skills/tes-engineering-discipline/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: skill-routing-map
    label: "Skill/intent routing map (/tes-* canonical + /tes:* aliases)"
    hosts: [claude, codex, cursor]
    disposition: keep-as-anchor
    anchor: "Route /tes-* intents to the matching host skill/rule; /tes:* are compatible aliases; not shell commands."
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/AGENTS.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: confidentiality
    label: "Private project confidentiality (placeholder vocabulary only)"
    hosts: [claude, codex, cursor]
    disposition: keep-as-anchor
    anchor: "Confidentiality: use neutral placeholder vocabulary only; no real project/product/path names in tracked content."
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/skills/tes-engineering-discipline/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: feedback-voice
    label: "Feedback voice (short frank prose, avoid table/dump bloat)"
    hosts: [claude, codex, cursor]
    disposition: keep-as-anchor
    anchor: "Feedback voice: short, frank prose; avoid tables/dumps unless asked or syntax requires."
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/skills/tes-engineering-discipline/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: locks
    label: "Bootloader locks (no inventory bloat, no unauthorized remote/secrets/destructive ops)"
    hosts: [claude, codex, cursor]
    disposition: keep-as-anchor
    anchor: "Locks: keep the bootloader thin; no remote/publish/secret/destructive actions without explicit project authorization."
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/AGENTS.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: diamond
    label: "Diamond Build-Test-Fail-Fix"
    hosts: [claude, codex, cursor]
    disposition: already-in-skill
    anchor: ""
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/skills/tes-engineering-discipline/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: mantra-gate
    label: "Mantra Gate (VERIFY/SCOPE/BEST_PATH/DOCUMENT/ORACLE/RESOLVE/STATUS + Flash-Fry marker)"
    hosts: [claude, codex, cursor]
    disposition: already-in-skill
    anchor: ""
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/skills/tes-engineering-discipline/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: infrastructure-gate
    label: "Infrastructure Decision Gate / Stack Surface Scan"
    hosts: [claude, codex, cursor]
    disposition: already-in-skill
    anchor: ""
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/skills/tes-engineering-discipline/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: tes-init-gate
    label: "tes-init gate flow (Install/Update Gate, Project Context Gate, Project-Start Gate, postinstall sentinel states)"
    hosts: [claude, codex, cursor]
    disposition: already-in-skill
    anchor: ""
    expansion_in:
      claude: src/adapters/claude/skills/tes-init/SKILL.md
      codex: src/adapters/codex/skills/tes-init/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: tes-update-protocol
    label: "tes-update protocol (helper parity, recommended_update_scope, final recorded probe gates)"
    hosts: [claude, codex, cursor]
    disposition: already-in-skill
    anchor: ""
    expansion_in:
      claude: src/adapters/claude/skills/tes-update/SKILL.md
      codex: src/adapters/codex/skills/tes-update/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: explicit-invocation-brake
    label: "Explicit-invocation brake for /tes-prospect, /tes-mine, /tes-goal-maestro + cognitive brake"
    hosts: [claude, codex, cursor]
    disposition: already-in-skill
    anchor: ""
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/skills/tes-engineering-discipline/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: cortex-reflex
    label: "Cortex Reflection reflex (read-only cortex_reflect / curate-plan, no write without authorization)"
    hosts: [claude, codex, cursor]
    disposition_by_host:
      claude: already-in-skill
      codex: move-to-skill
      cursor: already-in-skill
    note: "Claude tes-guidelines Workflow step 6 carries it; Cursor tes-guidelines.mdc carries it; Codex tes-engineering-discipline Workflow step 6 carries it. Codex AGENTS.md <cortex_reflex> duplicate must be deleted; skill already has it, so effectively already-in-skill. Confirm during SPEC-001 that the skill copy is complete and current."
    anchor: ""
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/skills/tes-engineering-discipline/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: field-reports
    label: "Field Reports active-by-default, sanitized-only, pre-push drain"
    hosts: [claude, codex, cursor]
    disposition_by_host:
      claude: already-in-skill
      codex: already-in-skill
      cursor: already-in-skill
    note: "Claude tes-guidelines Workflow step 7; Codex tes-engineering-discipline Workflow step 7; Cursor tes-guidelines.mdc Field Reports section. Bootloader copies are duplicates to delete."
    anchor: ""
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/skills/tes-engineering-discipline/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc

  - id: memory-lifecycle-boundary
    label: "TES Memory Lifecycle Boundary (recall read-only, write gate, checkpoint != memory, subagent return is evidence-only)"
    hosts: [claude, codex]
    disposition_by_host:
      claude: move-to-skill
      codex: move-to-skill
    note: "CRITICAL: this block lives ONLY in CLAUDE.md and AGENTS.md today. The Claude tes-guidelines skill and the Codex tes-engineering-discipline skill do NOT carry it. SPEC-001 must move it into each host skill before SPEC-002/003 deletes it from the bootloader. Cursor tes-guidelines.mdc already carries the block; for Cursor it is already-in-rule (move to lazy rule in SPEC-004)."
    anchor: ""
    expansion_in:
      claude: src/adapters/claude/skills/tes-guidelines/SKILL.md
      codex: src/adapters/codex/skills/tes-engineering-discipline/SKILL.md
      cursor: src/adapters/cursor/rules/tes-runtime-capabilities.mdc
```

## Stop-Condition Resolution (SPEC-000 gate)

The SPEC-000 stop condition is: "if a concept has no clear skill home and is not
anchor-worthy, stop and decide its home before thinning." Resolution:

- Every concept above has a clear `target_surface`. No concept is orphaned.
- The one concept that is NOT already present in its target skill is
  `memory-lifecycle-boundary` for Claude and Codex (it currently lives only in
  the bootloader). It has a clear home (`tes-guidelines` / `tes-engineering-discipline`)
  and SPEC-001 is the unit that moves it. This is the single move-to-skill action
  with real new content; everything else is delete-duplication or keep-anchor.
- `confidentiality` exists as a full section only in `CLAUDE.md` today; SPEC-001
  adds the one-line rule to the Codex and Cursor surfaces so the anchor exists
  consistently (fixing the unevenness recorded in the 2026-06-04 review).

No orphan concept remains. SPEC-000 passes; SPEC-001..004 may proceed against
this contract.
