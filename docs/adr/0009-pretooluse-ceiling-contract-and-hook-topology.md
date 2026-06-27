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

TES host hooks now pass the basic installed-target contract on Claude Code,
Codex, and Cursor: routine work stays quiet, governed mutations are supervised,
forbidden classes block before execution, anti-cry-wolf suppresses repeat
markers, the current runtime ledger is present, legacy hook ledgers are retired,
and host-specific output contracts are not flattened.

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
| `scripts/event_ledger.py` | General event-ledger helper and schema inspection surface used around runtime evidence. |
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
   evidence resolves the host contract.
7. **Ledger analytics must be part of the contract.** External analytics and
   dedup guidance must include tool, risk, path or command, session or mode, and
   marker state. Invocation plus timestamp is insufficient for Cursor batched
   projections and parallel host projections.

## What Is Already Proven

Current reports and oracles establish the floor for the recent installed-target
baseline:

- Claude Code, Codex, and Cursor hook configs are materialized and observed.
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

The next implementation wave should be small in diff but strategic in evidence.
It should add diagnostic structure without changing the user-facing marker
frequency.

1. **Decision reason codes.** Add stable reason codes to the host-neutral
   decision record, renderer inputs, and ledger rows. Minimum codes should cover
   routine non-mutating work, governed surface, forbidden class, anti-cry-wolf
   suppression, host payload labeling, and needs-discoverability.
2. **Classifier trace.** Add a redacted trace object for material and forbidden
   decisions. It should name extracted paths, command category, payload field
   source, normalized event/tool, governed match reason, forbidden class, and
   renderer path without logging secrets or file contents.
3. **Host payload evidence.** Persist enough redacted host evidence to
   distinguish host labels from TES classification. At minimum, record raw host
   tool label, normalized tool, payload field source, host renderer id, risk,
   and path or command category.
4. **Discoverability gate.** Add `NEEDS_DISCOVERABILITY` as a first-class safe
   outcome when host tool semantics are mutating-looking but not fixture-backed.
   Add at least one red fixture that fails if the kernel silently treats an
   unknown mutating surface as routine.
5. **Renderer parity fixtures.** Add fixtures that prove Claude Code, Codex, and
   Cursor render allow, supervise, block, and anti-cry-wolf outcomes without
   flattening output protocols.
6. **Ledger analytics schema.** Add schema/version guidance and fixture coverage
   for dedup keys that include tool, risk, path or command, session or mode, and
   marker state.
7. **Drift attribution.** Make audits able to say whether a failure came from
   host payload shape, kernel classification, session suppression, host renderer
   output, or ledger writing.
8. **Audit prompt enforcement.** Keep `HOOK-AUDIT-PROMPT.md` aligned with the
   new fields so installed-target audits must report floor status, ceiling
   status, discoverability status, and drift source.
9. **Installed target canaries.** Prove the ceiling on target-project installs
   after source oracles pass. Source-package proof alone is not sufficient for a
   delivered hook ceiling claim.

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
  change that follows it does.

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
4. a renderer parity oracle that proves Claude Code, Codex, and Cursor output
   shapes for allow, supervise, block, and suppression;
5. a discoverability fixture that fails for unknown mutating-looking tools;
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
