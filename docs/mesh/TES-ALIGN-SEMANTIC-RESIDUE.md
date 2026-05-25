---
tds_id: mesh.tes_align_semantic_residue
tds_class: mesh
status: active
consumer: maintainers, `/tes-align` skill authors, and project residue contract authors
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# TES Align Semantic Residue Gate

This document is the governed reference for the Semantic Residue Gate and
freshness reconciliation that `/tes-align` runs before reporting PASS.

The parent source-of-truth document is
`docs/mesh/TES-ALIGN-SKILL-SOURCE-OF-TRUTH.md`. That document keeps the role
boundary, operating mesh contract, and oracle requirements. This document
keeps the portable contract shape, severity semantics, allowlists, and the
reconciliation heuristic that the oracle implements.

## Why The Gate Exists

Structural alignment proves the mesh shape exists. Semantic alignment must
also prove the mesh tells the current project truth.

A canary certification exposed the gap: `docs/agents/**` had the required
mesh shape, the structural oracle passed, and yet active documentation still
asserted retired claims and used implementation vocabulary the project had
already moved past. The structural pass became a false green because no gate
existed to ask: did the mesh absorb the latest project truth, and did it stop
using the language the project retired?

`/tes-align` therefore runs a Semantic Residue Gate before PASS. The gate is
portable: TES owns the mechanism; the target project owns the vocabulary.

## Contract Path

The semantic residue contract is a project-local file. The oracle accepts the
first path it finds in this order:

1. `docs/agents/contracts/SEMANTIC-RESIDUE.yml`
2. `docs/agents/contracts/semantic-residue.yml`
3. `docs/agents/SEMANTIC-RESIDUE.yml`

Absence of the contract is not a failure. The gate runs only when a contract
is declared. When no contract exists, the gate emits a single advisory
warning and the rest of the alignment oracle proceeds unchanged.

## Contract Shape

```yaml
# docs/agents/contracts/SEMANTIC-RESIDUE.yml
version: 1
defaults:
  severity: needs_review
  scope:
    - docs/agents/**
  exclude:
    - docs/agents/evidence/**
    - docs/agents/DECISIONS/archive/**
    - docs/agents/contracts/**
entries:
  - id: example-retired-term
    term: "<retired literal>"          # exact literal; word-boundary matched
    severity: fail                      # fail | needs_review | warn
    reason: "Replaced by <successor> in ADR-NNNN."
    successor: "<current vocabulary>"
    allowed_paths:                      # historical evidence may keep the term
      - docs/agents/evidence/**
      - docs/agents/DECISIONS/ADR-*-deprecate-<term>.md
    expires_on: 2026-12-31              # optional review/expiration date

  - id: example-retired-pattern
    pattern: "(?i)\\b<retired claim regex>\\b"  # explicit regex; user owns boundaries
    severity: needs_review
    reason: "Stale current-state phrasing."
    successor: "Replace with current claim referencing the latest ADR."
    scope:
      - docs/agents/PROJECT-STATE.md
      - docs/agents/PROJECT-ROADMAP.md
      - docs/agents/EXECUTION-LINE.md
      - docs/agents/CONTEXT*.md
```

Required entry fields: `id`, and exactly one of `term` or `pattern`.

Optional entry fields: `severity`, `reason`, `successor`, `scope`,
`allowed_paths`, `exclude`, `expires_on`, `tags`.

When `term` is used, the oracle matches the literal with explicit word
boundaries so a short literal does not falsely match a longer unrelated word
that contains it as a substring. When `pattern` is
used, the project owns the regex boundaries; the oracle compiles the pattern
as given.

## Severity Semantics

| Severity | Oracle effect |
|----------|---------------|
| `fail` | Oracle status becomes `FAIL`. Each match is recorded as a structured failure. |
| `needs_review` | Oracle status becomes `NEEDS_REVIEW` unless another failure already marked it `FAIL`. Matches are recorded as `needs_review` items. |
| `warn` | Oracle status is not lowered. Matches are recorded as warnings. |

`/tes-align` may finish with `NEEDS_REVIEW`, `BLOCKED`, or `DEFERRED` when
semantic truth cannot be resolved. It must not report PASS when stale
current-state claims remain in active documentation.

## Allowed Paths

Each entry may declare `allowed_paths`. Files matching those globs are
ignored for that entry even when they live inside the scanned scope. This is
the mechanism that lets historical evidence retain old vocabulary without
breaking the gate.

```text
retired term -> forbidden in active docs -> allowed only in named evidence
```

## Expiration

`expires_on: YYYY-MM-DD` lets the project declare a review date. Entries
past their expiration date stay enforced but emit an advisory warning so the
maintainer can reclassify, retire, or extend them. Expired entries do not
silently fall off the gate.

## What The Gate Does Not Do

- It does not invent retired terms. Only the target project may declare them.
- It does not embed any real project name or any other project-specific
  vocabulary into TES generic code. Real names of users' projects, products,
  storage backends, archive formats, or internal services are private context
  and stay out of the TES source.
- It does not require Obsidian or any runtime state.
- It does not replace `/tes-doctor`.
- It does not delete historical evidence; it only refuses to call active docs
  PASS while they still assert retired truth.

## Freshness Reconciliation

`/tes-align` must compare current mesh claims against the latest relevant
evidence, ADRs, decisions, and change logs. It must detect when a newer
evidence packet or decision introduces a current claim that the active mesh
failed to absorb.

### Precedence

```text
accepted ADRs and active decisions
-> current project-state/roadmap/execution mesh
-> latest retained evidence and changelog packets
-> historical evidence and generated inventories
```

Historical evidence may remain historical. It must not silently outrank a
newer accepted decision.

### Required Reads Before PASS

Before claiming alignment, the skill must read:

1. The most recent accepted ADRs under `docs/agents/DECISIONS/**` or the
   linked decision system.
2. The most recent retained alignment evidence packet under
   `docs/agents/evidence/**`.
3. The current `PROJECT-STATE.md`, `PROJECT-ROADMAP.md`, `EXECUTION-LINE.md`,
   and `PROJECT-CONTEXT.md`.

Contradictions between these surfaces are first-class evidence. They must be
classified as `contradictory` and recorded in the retained alignment evidence
packet. Erasing the older claim without a successor decision is not allowed.

### Reconciliation Heuristic

The oracle applies a deterministic reconciliation heuristic:

| Signal | Detection | Effect |
|--------|-----------|--------|
| Newer ADR mentions a successor term absent from active mesh | ADR file `updated`/`accepted` date is newer than the latest evidence packet and contains a term absent from `PROJECT-STATE.md`/`PROJECT-ROADMAP.md`/`EXECUTION-LINE.md` | `needs_review` warning citing ADR path |
| Active mesh asserts a term flagged by the semantic residue contract | Semantic residue gate match | severity applies |
| Latest retained alignment evidence is older than the latest accepted ADR | Compare `mtime` and YAML `updated` fields | `needs_review` warning |

Targets may opt in to richer heuristics through the residue contract by
declaring `pattern` entries that capture stale current-state phrasing.

The freshness token diff filters out a small set of generic ADR section
headings (`Status`, `Context`, `Decision`, `Consequences`, `Rationale`,
`Alternatives`, `Background`, `Summary`, `Outcome`, `References`,
`Accepted`, `Proposed`, `Rejected`, `Superseded`, `Notes`, `Deeper`,
`Section`, `Overview`, `Details`, `Updated`, `Evidence`) so they are not
reported as new vocabulary. This stopword list is internal and small by
design — it removes documentary scaffolding without silencing genuine
successor terms.

## Oracle Output Shape

The oracle emits structured findings in JSON. Each finding includes:

| Field | Meaning |
|-------|---------|
| `code` | `residue.match`, `residue.malformed_contract`, `residue.entry_conflict`, `residue.entry_missing_match`, `residue.invalid_pattern`, or freshness equivalents. |
| `severity` | `fail`, `needs_review`, or `warn`. |
| `entry_id` | The contract entry id, or null for contract-level errors. |
| `path` | Path of the offending document. |
| `line` | Line number of the match. |
| `match` | The literal matched substring. |
| `reason` | Free-text explanation, copied from the contract entry when present. |
| `successor` | Successor vocabulary when declared. |

Use `python3 scripts/project_alignment_oracle.py --target <target> --json`
to consume the structured shape from automation. Use `--strict` to make
`NEEDS_REVIEW` exit non-zero in CI.

When a contract file exists but cannot be parsed (invalid YAML, wrong
top-level type, missing PyYAML), the oracle emits
`residue.malformed_contract` as a structured finding inside
`semantic_residue.findings` with `severity: fail`, the contract `path`,
and a `reason` string. The same condition also appears as a human-readable
line in `failures`, but consumers parsing JSON do not have to read prose
to detect the broken contract.

## Locks

- Do not hard-code any real project name or any other project-specific
  vocabulary into generic TES code. The Semantic Residue Gate mechanism is
  TES; the vocabulary is target-owned.
- Do not delete historical evidence merely because it contains retired
  language. Allowlist it through the contract instead.
- Do not call structural PASS deep alignment when the project has unread
  newer ADRs or evidence packets.
- Do not require Obsidian or any runtime state for the gate to run.
- Do not replace `/tes-doctor` with this gate.

## Done

The Semantic Residue Gate is ready only when:

1. A target project can declare retired vocabulary without TES knowing the
   private language up front.
2. Historical evidence can keep retired terms through `allowed_paths`.
3. A structural PASS becomes a semantic FAIL or NEEDS_REVIEW when retired
   vocabulary remains in active docs.
4. Freshness reconciliation surfaces unread newer ADRs before PASS.
5. The oracle self-test exercises the adversarial fixture, the allowlist
   fixture, the word-boundary regression, and the malformed contract.
