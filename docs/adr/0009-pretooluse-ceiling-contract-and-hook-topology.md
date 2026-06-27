---
tds_id: architecture.adr_0009_pretooluse_ceiling_contract_and_hook_topology
tds_class: architecture
status: active
consumer: maintainers, hook authors, installer authors, oracle authors, hook auditors, and release operators
source_of_truth: true
evidence_level: L1
tver: 0.1.0
---

# ADR 0009: PreToolUse Ceiling Contract and Hook Topology

Accepted on 2026-06-27. This ADR records architecture only. It does not change
runtime behavior, installer behavior, hook output, adapter materialization,
public bundle identity, release identity, push, tag, publish, or installed
target state by itself.

## Core Rule

PreToolUse is the host-real projection of the Mantra Gate before a tool
executes. It is an internal TES subsystem, not a standalone package, and its
ceiling is not another successful floor audit.

```text
PASS_BASIC proves operational safety.
PASS_CEILING proves diagnostic power, drift attribution, and host-aware evidence.
```

`docs/architecture/PRETOOLUSE-CONTRACT.md` is the canonical PreToolUse contract.
`docs/install/HOOK-AUDIT-PROMPT.md` is the per-host installed-target audit
projection of that contract. Future hook work must preserve both surfaces:
contract first, installed-target evidence second, no competing local protocol.

## Context

Recent per-host installed-target reports indicate that TES host hooks satisfy
the basic contract on Claude Code, Codex, and Cursor: routine work stays quiet,
governed mutations are supervised, forbidden classes block before execution,
anti-cry-wolf suppresses repeat markers, the current runtime ledger is present,
legacy hook ledgers are retired, and host-specific output contracts are not
flattened. That evidence is operational audit input, not a release-sealed bundle
claim. A release identity claim still requires clean bundle provenance in
`docs/dist/<version>/index.json`, including a reproducible `source_commit` and
non-dirty source tree state.

That is the floor. The strategic next problem is different. The hook runtime can
work and still be too opaque to diagnose the next host payload change, renderer
drift, session-suppression mistake, or ledger analytics false positive. The
ceiling requires explicit reason codes, classifier traces, host payload evidence,
renderer parity fixtures, discoverability stops, and ledger analytics semantics.

This ADR exists so a future execution window can start from one topology map
instead of rediscovering where the hook code, prompts, ledgers, oracles, and
host configs live.

## Current Hook Topology

The intended runtime path is:

```text
host hook config
-> thin host adapter
-> host-neutral PreToolUse decision kernel
-> session/suppression coordinator
-> host-specific output renderer
-> runtime ledger writer
```

The source package owns the following hook-related surfaces:

| Surface | Role |
|---------|------|
| `scripts/tes_install.py` | Installer engine, host hook materializer, installed hook entrypoint, host-specific renderer, `hook-health`, and runtime ledger writer. |
| `scripts/pretooluse_kernel.py` | Host-neutral decision kernel: payload normalization, path extraction, governed-surface detection, forbidden-classification input, and allow/supervise/block decision record. |
| `scripts/pretooluse_session.py` | Session coordinator for anti-cry-wolf sentinel state and same-session context suppression. |
| `scripts/mantra_gate.py` | Mantra marker, governed-surface and risk policy inputs used by PreToolUse. |
| `scripts/event_ledger.py` | Adjacent lifecycle ledger helper for `.tes/events/ledger.jsonl`; it is not the current hook runtime writer. Hook runtime rows are written by `record_hook_execution` in `scripts/tes_install.py`. |
| `scripts/tes_legacy_retirement.py` | Legacy runtime residue and migration hygiene support. |
| `scripts/install_mcp.py` | Installed helper allowlist; ensures PreToolUse helpers are delivered into target `.tes/bin/**`. |
| `bin/tes.js` | Thin npx entrypoint; delegates installation to `scripts/tes_install.py` and must not duplicate hook logic. |

The source package owns these red-capable or maintenance oracles:

| Oracle | Role |
|--------|------|
| `scripts/pretooluse_contract_oracle.py` | Protects the canonical contract vocabulary, floor/ceiling split, and audit-prompt linkage. |
| `scripts/pretooluse_kernel_oracle.py` | Exercises host-neutral PreToolUse decision behavior. |
| `scripts/pretooluse_session_oracle.py` | Exercises anti-cry-wolf session suppression behavior. |
| `scripts/mantra_gate_pretooluse_oracle.py` | Protects Mantra Gate behavior as consumed by PreToolUse. |
| `scripts/hook_audit_prompt_oracle.py` | Protects the installed-target hook audit prompt requirements. |
| `scripts/host_runtime_matrix_oracle.py` | Source-side host runtime matrix gate when the source repository is under audit. |
| `scripts/installed_certification_oracle.py` | Installed-target certification, including hook-config hygiene. |
| `scripts/mantra_gate_adoption_oracle.py` | Installed-target Mantra Gate adoption check. |
| `scripts/install_smoke.py` | Source install smoke coverage, including hook fixtures and legacy-ledger cases. |
| `scripts/runtime_topology_oracle.py` | Higher-level runtime topology self-tests that include PreToolUse helper oracles. |

The governing documentation and audit surfaces are:

| Document | Role |
|----------|------|
| `docs/architecture/PRETOOLUSE-CONTRACT.md` | Canonical PreToolUse contract, including `PASS_BASIC`, `PASS_CEILING`, and `NEEDS_DISCOVERABILITY`. |
| `docs/architecture/INSTALLATION-FRAMEWORK.md` | Installer and host-hook wiring map, including helper boundaries and ledger observability guidance. |
| `docs/install/HOOK-AUDIT-PROMPT.md` | Per-host installed-target audit prompt. It must require current-host native smoke, safe cross-host simulation, and ceiling assessment. |
| `docs/install/AGENT-ORACLE-INVENTORY.md` | Operator-facing command inventory for installed or source checks. |
| `docs/architecture/PROJECT-STRUCTURE.md` | Repository-level ownership map for installer, helper, and adapter source boundaries. |
| `AGENTS.md` | Codex maintainer bootloader; routes PreToolUse work to the ceiling contract. |
| `.claude/CLAUDE.md` | Claude maintainer bootloader mirror; same governance body as `AGENTS.md`. |
| `docs/evidence/reports/hooks/pretooluse-strategy-2026-06-27/JOURNAL.md` | Maintainer evidence journal for the PreToolUse extraction and ceiling strategy. |
| `docs/INDEX.md` and `docs/tds/DOCS-INDEX.yml` | Discoverability and TDS indexing for the contract, audit prompt, and this ADR. |

Installed targets receive or materialize these runtime surfaces:

| Installed Surface | Role |
|-------------------|------|
| `.tes/bin/tes_install.py` | Installed hook entrypoint and host renderer. |
| `.tes/bin/pretooluse_kernel.py` | Installed decision kernel helper. |
| `.tes/bin/pretooluse_session.py` | Installed session/suppression helper. |
| `.tes/bin/mantra_gate.py` | Installed Mantra Gate helper consumed by PreToolUse. |
| `.tes/bin/cortex_runtime.py` | Installed Cortex advisory runtime; PreToolUse may propose context but must not write durable state automatically. |
| `.tes/runtime/hooks/executed.jsonl` | Current runtime hook ledger and primary installed evidence surface. |
| `.tes/mantra-gates/pretooluse-*.seen` | Anti-cry-wolf sentinel state. |
| `.tes/tes-install-lock.json` | Installed version, agent set, certification, and negative checks. |
| `.tes/postinstall.json` | Postinstall status and non-hook advisories. |
| `.tes/hooks/executed.jsonl` | Retired legacy ledger path; residue only when present. |

Installed host configs are projections, not the semantic source:

| Host | Config | Runtime Contract |
|------|--------|------------------|
| Claude Code | `.claude/settings.json` | `SessionStart` and `PreToolUse`; governed allow uses `hookSpecificOutput.additionalContext`; hard block uses exit 2 plus stderr. |
| Codex | `.codex/config.toml` | Canonical Codex hook config; `SessionStart` and `PreToolUse`; governed context is generally stderr; hard block uses exit 2 plus stderr. |
| Cursor | `.cursor/hooks.json` | `sessionStart`, `beforeSubmitPrompt`, and `preToolUse`; allow/deny is JSON permission output; hard block returns exit 0 with `permission: "deny"`. |

## Decision

1. **PreToolUse remains an internal subsystem.** The package must keep
   `pretooluse_kernel.py` and `pretooluse_session.py` inside TES and must not
   split them into a standalone external package.
2. **The kernel stays host-neutral.** The kernel owns normalized input,
   extraction, governed detection, forbidden classification input, and
   host-neutral decision data. It must not own installer/update logic,
   postinstall advisories, sync/release behavior, Field Reports, Cortex durable
   writes, host renderer protocols, or ledger writes.
3. **TES remains the integrator.** `tes_install.py` installs host configs,
   invokes the kernel and session coordinator, renders Claude/Codex/Cursor
   output, writes runtime evidence, and reports hook health.
4. **`HOOK-AUDIT-PROMPT.md` is mandatory audit projection.** Per-host hook
   reports must follow it when auditing installed targets. It is not a loose
   checklist; it is the operational projection of the canonical contract.
5. **Future reports must separate floor from ceiling.** A run that proves
   routine silence, governed supervision, forbidden block, anti-cry-wolf,
   ledger evidence, host output, and Cortex no-write reports `PASS_BASIC`.
   It reports `PASS_CEILING` only when ceiling evidence also exists.
6. **Discoverability beats guessing.** Unknown or newly exposed mutating tool
   names must not be silently treated as routine. If host payload semantics are
   unclear, the correct state is `NEEDS_DISCOVERABILITY` until fixture or native
   evidence resolves the host contract. This is a ceiling obligation, not
   current floor behavior: the current floor still depends on the kernel's
   known mutating-tool set and the existing risk classifier.
7. **Ledger analytics must be part of the contract.** External analytics and
   dedup guidance must include tool, risk, path or command, session or mode, and
   marker state. Invocation plus timestamp is insufficient for Cursor batched
   projections and parallel host projections.

## What Is Already Proven

Current reports and oracles establish the floor for the recent installed-target
baseline:

- Claude Code, Codex, and Cursor hook configs are materialized and observed by recent per-host reports; retained repo evidence is not yet a strong sanitized baseline archive.
- Native smokes have proven governed supervision and anti-cry-wolf per host.
- Forbidden classes block before execution with host-specific output semantics.
- Codex covers `apply_patch`, `Bash`, `Shell`, and `shell`, and extracts patch
  paths from canonical and defensive payload fields.
- Cursor `StrReplace` is now covered as governed mutating work in the TES
  kernel path; native host labeling can still arrive as `tool: "Write"` and
  must be treated as host payload evidence when `risk=material` is correct.
- Legacy `.tes/hooks/executed.jsonl` is retired from current evidence.
- Exact duplicate runtime rows are no longer part of the healthy path; apparent
  collisions need dedup keys that include tool/risk/path/session/mode.
- Cortex advisory behavior is no-write: recall, capture, and alignment may be
  proposed, but PreToolUse must not commit durable Cortex writes.

This evidence supports `PASS_BASIC`. It does not by itself support
`PASS_CEILING`.

## What Must Be Implemented To Pierce The Ceiling

The next wave must add diagnostic structure without increasing marker noise:
reason codes, classifier trace, host payload evidence, discoverability,
renderer parity, ledger analytics schema, drift attribution, audit-prompt
enforcement, and installed-target canaries. P0/P1 below make those requirements
executable.

## Ceiling Runtime Contract Shape

P0 must introduce a versioned, redaction-safe runtime record testable before
installed-target claims. Python shape may differ; semantic fields are frozen:

```text
pretooluse_decision@2
  schema_version, host, event / event_canonical
  session_id, invocation_id
  raw_tool_label, normalized_tool, payload_source
  paths[], command_category, risk, outcome
  reason_codes[]
  classifier_trace, session_trace, renderer_trace, ledger_trace
```

The record must not store file contents, raw secret-bearing command text, full
environment dumps, or unrelated host payload fields. It may store command
categories and redacted token classes such as `forbidden_git_force_push`,
`forbidden_root_wipe`, `patch_body`, or `no_command`.

Minimum `reason_codes[]` values:

| Code | Required When |
|------|---------------|
| `routine_non_mutating` | A non-mutating tool is allowed silently. |
| `routine_non_governed` | A mutating tool touches no governed surface and is allowed silently. |
| `governed_surface_mutation` | A mutating tool touches a path segment ending in `/SKILL.md`, `AGENTS.md`, `CLAUDE.md`, `docs/adr/`, `docs/governance/`, or `.cursor/rules/`. |
| `forbidden_class` | A forbidden command or action class is blocked before execution. |
| `anti_crywolf_suppressed` | A repeated same-session governed marker is suppressed while the classification stays material. |
| `host_payload_labeling` | The host raw label differs from the normalized TES classification or requires explanation. |
| `patch_body_path_extracted` | A governed path is extracted from an `apply_patch` body or alias field. |
| `needs_discoverability_unknown_mutation` | A mutating-looking host tool has insufficient fixture/native evidence. |
| `renderer_contract_projected` | A host renderer emits its own output protocol for the decision. |
| `cortex_advisory_no_write` | Cortex context is advisory and no durable write is performed. |

`classifier_trace` must name only evidence classes: normalized tool, payload
field source, path match hint, patch-body extraction source, forbidden class,
and governed-surface match. `session_trace` must identify suppression state
without exposing unrelated session content. `renderer_trace` must name the host
renderer and output contract, not duplicate the full rendered message.
`ledger_trace` must name the hook ledger writer and schema/version used for the
runtime row. The current floor ledger may still persist raw `command`; P0 must
replace or supplement that with redacted `command_category` before any
`PASS_CEILING` claim.

## P0 Red Fixture Matrix

P0 is not complete until source oracles fail red for these cases:

| Fixture | Expected Ceiling Evidence |
|---------|---------------------------|
| Routine read on non-governed path | `outcome=allow`, `risk=routine`, `reason_codes` includes `routine_non_mutating`, no marker. |
| Non-governed mutating edit | `outcome=allow`, `reason_codes` includes `routine_non_governed`, no marker. |
| Governed Write/Edit/StrReplace on `/SKILL.md` path | `outcome=supervise`, `risk=material`, `reason_codes` includes `governed_surface_mutation`. |
| Same governed path twice in one session | First record supervises; second keeps `risk=material` and adds `anti_crywolf_suppressed`. |
| Codex `apply_patch` canonical field | Path extracted from patch body; `reason_codes` includes `patch_body_path_extracted`. |
| Codex `apply_patch` alias fields | Same extraction evidence as canonical field or explicit fixture failure. |
| Forbidden force-push class | `outcome=block`, `reason_codes` includes `forbidden_class`, command text redacted to category. |
| Cursor raw tool label differs from TES classification | `raw_tool_label` and `normalized_tool` both present; `reason_codes` includes `host_payload_labeling`. |
| Unknown mutating-looking host tool on governed path | `outcome=needs_discoverability`, not routine, with `needs_discoverability_unknown_mutation`. |
| Cursor batched invocation rows | Dedup fixture proves rows differing by tool/risk/path/mode are not duplicate hook execution. |
| Cortex advisory context | `cortex_advisory_no_write` present and no durable write side effect. |
| Renderer contract projection | Claude Code, Codex, and Cursor fixture outputs remain host-specific. |

The renderer fixture owner is `scripts/mantra_gate_pretooluse_oracle.py`;
`scripts/host_runtime_matrix_oracle.py` must consume it, not re-implement it.
The current matrix contains floor renderer cases; P0 must route ceiling renderer
assertions through the owner before adding new ceiling cases.

## Runtime Priority Cut

The ceiling implementation must be sequenced as runtime work, not as another
documentation-only pass.

**P0: runtime diagnosis substrate.** P0 is the smallest delivered runtime slice
that makes a future regression explainable. It includes decision reason codes,
redacted classifier trace, host payload evidence, `NEEDS_DISCOVERABILITY`,
renderer input/output parity fixtures, and ledger schema/version semantics for
dedup and analytics. P0 is complete only when the source oracles can fail red
for a missing reason code, missing trace, flattened renderer output, silently
routine unknown mutating tool, or ambiguous ledger analytics key.

Current source status: the kernel implements the first P0 slice for stable
decision `reason_codes` and unknown mutating-looking governed tools returning
`needs_discoverability`. Full P0 remains incomplete until redacted classifier
trace, host payload evidence, renderer trace, ledger trace, and renderer parity
ownership are source-oracle enforced.

**P1: installed-target ceiling certification.** P1 starts only after P0 is green
in source. It updates the installed audit flow so `HOOK-AUDIT-PROMPT.md`,
`hook-health`, installed helper packaging, and target-project canaries can prove
`PASS_CEILING` per host. P1 must show where each result came from: host payload,
kernel classification, session suppression, renderer output, or ledger write.
P1 is not complete from one host alone; it needs per-host native evidence or an
explicit `NEEDS_EVIDENCE` / `NEEDS_DISCOVERABILITY` status.

Everything else is lower priority until P0 and P1 are green. Postinstall
advisories, Field Reports backlog, mesh alignment, public docs, release sync,
and general cleanup may be important, but they do not pierce the PreToolUse
runtime ceiling. Bundle provenance cleanup is required before any release-sealed
claim, but it is not a substitute for P0 or P1 runtime evidence.

## P1 Installed Evidence Matrix

P1 must prove the P0 record survives packaging, installation, host projection,
native execution, and hook-health reporting.

| Installed Evidence | Required Claim |
|--------------------|----------------|
| `.tes/bin/pretooluse_kernel.py` and `.tes/bin/pretooluse_session.py` import | Installed helpers match the P0 source contract. |
| `.tes/bin/tes_install.py hook --agent <host>` simulation | Host renderer consumes `pretooluse_decision@2` and preserves reason/trace fields. |
| Native smoke per host | Current-host ledger row contains reason codes, classifier trace, host payload evidence, renderer trace, and ledger trace. |
| `hook-health --json-only` | Current `tes-hook-health@1` is floor-oriented. P1 must add floor and ceiling status; it cannot report `PASS_CEILING` if any P0 field is absent. |
| `HOOK-AUDIT-PROMPT.md` report | Contains a `Ceiling Assessment` with reason-code, trace, discoverability, renderer, and ledger evidence. |
| Sanitized per-host evidence | Retains current-host native audit summaries in repo evidence without private target names or absolute paths. |
| Installed target canary | Replays one Claude Code, one Codex, and one Cursor path or returns explicit `NEEDS_EVIDENCE` / `NEEDS_DISCOVERABILITY`. |
| Bundle provenance | Release-sealed claim waits for clean `source_commit` and non-dirty source tree state. |

`PASS_BASIC` remains valid for operational safety when these P1 fields are
missing. `PASS_CEILING` is invalid unless every row above has direct evidence.

## Rejected Alternatives

| Alternative | Rejection |
|-------------|-----------|
| Declare current hook PASS as ceiling | Current evidence proves floor behavior, not reason-code, trace, renderer parity, discoverability, or drift attribution. |
| Move renderers into the kernel | It would collapse host protocols and violate ADR 0008 host-aware runtime contracts. |
| Add broad guessed tool names | Guessing creates silent routine holes. Unknown mutating surfaces need fixtures or `NEEDS_DISCOVERABILITY`. |
| Certify from config presence or ledger count | Configs and row counts prove materialization and activity, not correct classification or output semantics. |
| Add more marker noise | Ceiling is better evidence and diagnosis, not more frequent human interruption. |
| Patch installed targets directly | Portable hook learning belongs in package source first, then installed-target canaries. |

## Consequences

- Future hook reports can honestly say "operational at `PASS_BASIC`, not yet
  `PASS_CEILING`" without downgrading the real safety gain already achieved.
- Hook bugs become localizable: host payload, kernel, session, renderer, or
  ledger.
- New host tool names get a safe stop state instead of disappearing into
  routine silence.
- The installed audit prompt becomes more important, not less; it is the
  reproducible operator surface for target-project evidence.
- Release identity remains a separate decision. This ADR does not require a
  version bump by itself, but any delivered runtime or audit-prompt behavior
  change that follows it does. A dirty or non-reproducible bundle index blocks
  release-sealed claims even when this ADR and its documentation gates pass.

## Non-Goals

- No runtime implementation in this ADR.
- No package version bump, public bundle update, tag, push, publish, or release.
- No universal host protocol.
- No standalone PreToolUse package.
- No increase in marker frequency.
- No target-project local workaround.

## Future Implementation Gates

A future ceiling implementation is not complete until all of these pass:

1. `scripts/pretooluse_contract_oracle.py --self-test`
2. `scripts/pretooluse_kernel_oracle.py`
3. `scripts/pretooluse_session_oracle.py`
4. `scripts/mantra_gate_pretooluse_oracle.py` extended as the renderer parity
   owner for Claude Code, Codex, and Cursor output shapes for allow, supervise,
   block, and suppression, with `scripts/host_runtime_matrix_oracle.py`
   consuming that owner;
5. the discoverability fixture in `scripts/pretooluse_kernel_oracle.py`, which
   fails when unknown mutating-looking tools on governed paths fall through to
   routine allow;
6. `scripts/hook_audit_prompt_oracle.py --self-test`;
7. `python3 scripts/validate_tds.py`;
8. `npm run commit:check`;
9. at least one installed-target audit using `docs/install/HOOK-AUDIT-PROMPT.md`
   that reports `PASS_CEILING` only when all ceiling fields are present.

## Evidence References

- `AGENTS.md`
- `.claude/CLAUDE.md`
- `docs/adr/0008-host-aware-runtime-contracts.md`
- `docs/architecture/PRETOOLUSE-CONTRACT.md`
- `docs/architecture/INSTALLATION-FRAMEWORK.md`
- `docs/architecture/PROJECT-STRUCTURE.md`
- `docs/install/HOOK-AUDIT-PROMPT.md`
- `docs/install/AGENT-ORACLE-INVENTORY.md`
- `docs/evidence/reports/hooks/pretooluse-strategy-2026-06-27/JOURNAL.md`
- `scripts/tes_install.py`
- `scripts/pretooluse_kernel.py`
- `scripts/pretooluse_session.py`
- `scripts/mantra_gate.py`
- `scripts/event_ledger.py`
- `scripts/tes_legacy_retirement.py`
- `scripts/install_mcp.py`
- `scripts/pretooluse_contract_oracle.py`
- `scripts/pretooluse_kernel_oracle.py`
- `scripts/pretooluse_session_oracle.py`
- `scripts/mantra_gate_pretooluse_oracle.py`
- `scripts/hook_audit_prompt_oracle.py`
- `scripts/host_runtime_matrix_oracle.py`
- `scripts/installed_certification_oracle.py`
- `scripts/mantra_gate_adoption_oracle.py`
- installed target `.tes/bin/**`, `.tes/runtime/hooks/executed.jsonl`,
  `.tes/mantra-gates/pretooluse-*.seen`, `.claude/settings.json`,
  `.codex/config.toml`, and `.cursor/hooks.json`

## Done

ADR 0009 is satisfied when it is indexed in `docs/INDEX.md` and
`docs/tds/DOCS-INDEX.yml`, passes the documentation gates, and can be handed to
a new execution window as the complete hook topology and ceiling backlog.
