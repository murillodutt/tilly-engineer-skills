---
tds_id: roadmap.goal_super_spec_tes_host_hook_ceiling_hardening
tds_class: roadmap
status: archived
consumer: maintainers, hook authors, installer authors, oracle authors, release reviewers, and hook-audit operators
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Super SPEC: TES Host Hook Ceiling Hardening

Status: archived historical execution plan for post-`0.3.210` hook audit
findings. ADR 0009 execution is superseded by
`GOAL-SUPER-SPEC-adr-0009-pretooluse-ceiling-linear-slices.md`; keep this file
as prior hardening evidence, not as the current prompt track.

Protected baseline: release `0.3.210`, commit
`4ffc350a36b44b5492f5c70e832ef5758700e476`, public bundle SHA
`d0b6c015459432ed0927d57a186edfeaf8ece686d5ad5ba09ab90be6f8118bd6`.

Target release: `0.3.211`.

## Evidence Packet

Local sources:

- `scripts/tes_install.py`
- `scripts/host_runtime_matrix_oracle.py`
- `scripts/hook_audit_prompt_oracle.py`
- `docs/install/HOOK-AUDIT-PROMPT.md`
- `docs/adr/0008-host-aware-runtime-contracts.md`
- `docs/governance/AGENTIC-ALIGNMENT-GOVERNANCE.md`

Related official documentation:

- Codex hooks: `https://developers.openai.com/codex/hooks`
- Claude Code hooks: `https://code.claude.com/docs/en/hooks`
- Cursor hooks: `https://cursor.com/docs/hooks`

The Codex documentation names `tool_input.command` as the canonical field for
`Bash` and `apply_patch`. The correction below must preserve that canonical
contract while accepting observed defensive aliases (`input`, `patch`, and
`arguments.*`) so a host payload-shape variation cannot silently skip governed
path extraction.

## Finding Reflection

P1: Codex `apply_patch` path extraction is too narrow.

Reflection: `command` is canonical, but the reports proved the current matrix
does not falsify alias payloads. A ceiling-grade hook should not depend on one
happy-path key when the same semantic patch body can arrive under another key.
Closure requires parser hardening and red fixtures for each accepted key.

P2: Dual-agent ledger projection is ambiguous.

Reflection: dual rows across agents are not necessarily duplicates because each
host projection has its own output contract and sentinel state. The correction
must not collapse separate agents. It should dedupe only identical repeated
records and make the audit prompt treat cross-agent rows as parallel projection,
not as proof transfer.

P3: Cursor duplicate runtime records inflate hook-health.

Reflection: warning-level duplicates are tolerated, but ceiling-grade telemetry
should avoid identical append noise at the source. The append path should skip
exact duplicate hook records while keeping legitimate second mutations whose
decision fields differ, such as anti-cry-wolf suppression.

P4: Legacy ledger and backup residue remain hygiene findings.

Reflection: legacy `.tes/hooks/executed.jsonl` remains explicitly non-blocking
when `hook-health` classifies it as residue. This cycle should not erase target
evidence, but the prompt should keep residue out of current native proof.

## Goal

After this SPEC ships, the next per-host audit can prove:

```text
official host contract + defensive payload aliases + exact ledger semantics
+ per-host native smoke + release identity
= PASS_WITH_FINDINGS only for real non-blocking residue
```

## Non-Objectives

- Do not flatten host-specific output contracts.
- Do not treat non-current-host reports as native proof.
- Do not delete installed-target evidence or target smoke artifacts from the
  package source.
- Do not move public tags without explicit authorization.
- Do not add a new hook protocol, adapter boundary, or config knob.

## Ordered Units

### SPEC-000: Source Evidence And Contract Lock

Allowed files: this Super SPEC, its execution ledger, docs indexes.

Done when the evidence packet names the official docs, the local source files,
and the four findings without private target identifiers.

Focused oracle:

```bash
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py --paths docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-host-hook-ceiling-hardening.md
git diff --check
```

### SPEC-001: Defensive Codex Patch Body Extraction

Allowed files: `scripts/tes_install.py`,
`scripts/host_runtime_matrix_oracle.py`.

Required behavior:

- `tool_input.command` remains the preferred canonical source.
- `tool_input.input`, `tool_input.patch`, `tool_input.arguments.command`,
  `tool_input.arguments.input`, and `tool_input.arguments.patch` are accepted
  as defensive aliases.
- The same aliases are accepted from top-level hook input when present.
- Governed `apply_patch` bodies under each accepted key extract the path and
  surface `Flash-Fry` once.
- A second same-session governed mutation remains silent and writes
  `context_suppressed=true`.

Focused oracle:

```bash
npm run host-runtime:matrix
python3 scripts/tes_install.py --self-test
```

### SPEC-002: Exact Runtime Ledger Append Semantics

Allowed files: `scripts/tes_install.py`,
`scripts/host_runtime_matrix_oracle.py`.

Required behavior:

- Append skips only exact duplicate hook records under the same agent/event/
  mode/session/tool/path/command/invocation/decision fields.
- Distinct agent projections remain distinct.
- Anti-cry-wolf second mutations remain recorded because their decision fields
  differ from the first governed marker record.
- Hook-health duplicate findings stay red-capable for historical/manual
  duplicate files.

Focused oracle:

```bash
python3 scripts/tes_install.py --self-test
npm run host-runtime:matrix
```

### SPEC-003: Prompt And Prompt Oracle Upgrade

Allowed files: `docs/install/HOOK-AUDIT-PROMPT.md`,
`scripts/hook_audit_prompt_oracle.py`.

Required behavior:

- The prompt tells auditors that Codex `command` is canonical and aliases are
  defensive coverage.
- The prompt requires reporting alias-key failures separately from native
  output-contract failures.
- The prompt names dual-agent ledger rows as parallel projections unless the
  same agent/event/invocation is repeated identically.
- The prompt keeps legacy ledger residue out of current native proof.
- The oracle fails if those semantics are removed.

Focused oracle:

```bash
python3 scripts/hook_audit_prompt_oracle.py --self-test
```

### SPEC-004: Release Identity

Allowed files: correlated release surfaces only.

Required actions after local gates pass:

```bash
python3 scripts/tes_bump.py patch --yes --json
python3 scripts/tes_bundle.py publish --adapter all
python3 scripts/build_public_docs.py
git add -A
npm run commit:check
npm run commit:closure
git push origin main
git tag -a v0.3.211 -m "Release 0.3.211: host hook ceiling hardening"
git push origin v0.3.211
npm run release:check
python3 scripts/public_pages_oracle.py --version 0.3.211 --retries 12 --interval 10
```

Done when main, tag, bundle, release check, and public pages all resolve to
`0.3.211`.

### SPEC-005: Next Per-Host Audit Prompt

Objective: prepare the prompt operators should use after updating targets to
`0.3.211`.

Done when `docs/install/HOOK-AUDIT-PROMPT.md` is the prompt to reuse and its
oracle confirms alias coverage, dual-projection handling, and narrow
`PASS_WITH_FINDINGS` semantics.

## Required Closeout Oracles

Before source-local commit:

```bash
npm run host-runtime:matrix
python3 scripts/tes_install.py --self-test
python3 scripts/hook_audit_prompt_oracle.py --self-test
python3 scripts/validate_tds.py
python3 scripts/tds_surface_oracle.py
python3 scripts/validate_reference_package.py
python3 scripts/build_public_docs.py --check
git diff --check
```

Before release closure:

```bash
npm run commit:closure
npm run release:check
python3 scripts/public_pages_oracle.py --version 0.3.211 --retries 12 --interval 10
```

## Done

- Defensive Codex patch-body aliases are source-covered and matrix-covered.
- Exact duplicate hook appends are suppressed without suppressing
  anti-cry-wolf evidence.
- The audit prompt and its oracle carry the new ceiling semantics.
- The release is published as `0.3.211`.
- The next native test prompt is ready for Codex, Claude Code, and Cursor.
