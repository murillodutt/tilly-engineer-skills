---
tds_id: architecture.adr_0008_host_aware_runtime_contracts
tds_class: architecture
status: active
consumer: maintainers, runtime authors, hook authors, installer authors, adapter authors, oracle authors, and release operators
source_of_truth: true
evidence_level: L1
tver: 0.1.0
---

# ADR 0008: Host-Aware Runtime Contracts

Accepted on 2026-06-26. This ADR elevates host-aware runtime behavior from a local implementation detail into a TES architecture invariant. It records architecture only. It does not deliver hooks, scripts, installer behavior, adapter behavior, public docs, release identity, or public bundle changes by itself.

## Core Rule

Every delivered TES runtime or hook surface SHALL have one source-derived semantic contract and host-specific runtime projections.

```text
Shared semantic core.
Host-specific projection.
Executable proof per host.
No fake universal hook contract.
```

## Context

TES now spans multiple execution hosts: Claude Code, Codex, Cursor, local Git hooks, assisted installers, MCP surfaces, adapter bootloaders, and product skills. These surfaces share product intent but not runtime contracts. Hook names, lifecycle timing, payload shape, output fields, blocking semantics, trust and reload behavior, install paths, and config ownership differ by host.

ADR 0007 proved the risk through Cortex: proactive runtime behavior is valuable only when the runtime path is host-aware, no-write where required, and proved with executable fixtures. The same rule must govern future TES runtime surfaces, including Mantra Gate projections, Cortex projections, Field Reports hooks, installer hook wiring, adapter templates, and host-specific skill/preset routing.

The ceiling is not "works on the current machine." The ceiling is a package that can be installed into target projects using different agent hosts without silently flattening host semantics, duplicating protocols in bootloaders, or mistaking config presence for runtime behavior.

## Decision

1. **Host-aware is a package invariant.** Any delivered TES runtime, hook, installer, or adapter behavior that crosses a host boundary must model the host explicitly before claiming delivery.
2. **Semantic core before projection.** Shared TES intent belongs in a source-owned semantic core or contract. Claude Code, Codex, Cursor, Git hook managers, and other host surfaces receive projections of that core, not copies of a full protocol.
3. **Per-host contract proof.** Runtime delivery must include executable proof for each affected host. Build, typecheck, materialization, or prose-only checks are not enough for hook/runtime integration.
4. **No flattened blocking semantics.** A host that blocks through exit code, JSON permission, advisory context, prompt rewrite, status message, or no observable block channel must be represented as itself. One host's blocking model must not become the package-wide model.
5. **Config presence is not certification.** A written settings file, hook manifest, or installed script proves only filesystem materialization. Runtime certification requires the strongest observable evidence available for that host, and may end in `HOST_UNOBSERVABLE` when the host exposes no external firing proof.
6. **Installer ownership is host-specific.** Installers must detect the active hook/config owner before writing. Native Git hooks, Husky, Lefthook, Claude settings, Codex config, Cursor hooks, and project-owned files require different merge, chain, idempotency, and preservation rules.
7. **Fail open on ordinary work.** Advisory runtime surfaces must not block normal local edits, routine reads, focused oracles, staging, or local commits. Hard block behavior is reserved for destructive, remote, release, secret-bearing, governed write, or explicitly owner-approved high-impact actions.
8. **Discover before workaround.** When host behavior, package behavior, or framework behavior is uncertain, implementation must inspect local source, installed source, official docs, Context7/MCP where available, or upstream behavior before adding glue or workaround code.
9. **Release identity follows delivered behavior.** Any change that alters adopter-visible host behavior, installed hooks, helper scripts, adapter materialization, public docs, MCP, Field Reports, Cortex, Mantra Gate, or command routing requires a release-identity decision.
10. **Execution feedback is advisory only.** Local cross-window feedback files such as `.tes/FEEDBACK-LOOP.md` may guide an execution loop, but they are maintainer-only, untracked, lower authority than owner request, ADR/SPEC, source, and oracles, and must never become product behavior.

## Host Contract Minimum

Future runtime SPECs must record at least:

- host name and version/source evidence;
- lifecycle events and trigger layer;
- input payload fields and required defaults;
- output fields, exit-code behavior, and block/advisory semantics;
- install path and config owner;
- idempotency, merge, and preservation behavior;
- trust, reload, feature flag, or enablement requirements;
- hot-path tolerance and timeout behavior;
- strongest observable runtime proof and any `HOST_UNOBSERVABLE` limit;
- negative fixture showing the wrong host contract fails.

## Boundary Matrix

| Surface | Host-Aware Obligation | Must Not Do |
|---------|-----------------------|-------------|
| Agent hooks | Project semantic intent into Claude Code, Codex, Cursor, or later hosts through host-specific contracts | Pretend all hosts share one event/output/blocking protocol |
| Git hooks | Detect native Git, Husky, Lefthook, or project-owned hook routing before installing or chaining | Write to `.git/hooks/**` and assume Git will execute it |
| Bootloaders | Stay thin and route to source-owned behavior | Copy the full runtime protocol into each host bootloader |
| Skills/presets | Make capability discoverable and agent-usable in the host's native language | Create noisy human checklists or duplicate runtime enforcement |
| Installers | Preserve foreign hooks and project-owned config while installing TES-owned surfaces idempotently | Overwrite or silently orphan existing hook owners |
| Oracles | Prove host contracts with fixtures and negative cases | Certify integration from build/typecheck alone |

## Rejected Alternatives

| Alternative | Rejection |
|-------------|-----------|
| Universal hook adapter | It hides the exact behavior that causes production drift: event names, payloads, output fields, and block semantics differ by host. |
| Bootloader duplication | It makes each host file a second source of truth and guarantees protocol drift. |
| Config-written equals installed | It certifies the filesystem, not the runtime. Some hosts require trust, reload, feature flags, or manual enablement. |
| Always-verbose supervision | It trains agents and users to ignore the signal. Runtime supervision must stay quiet until risk, ambiguity, drift, or explicit audit requires detail. |
| Copying a reference implementation | Reference projects may validate patterns, but TES must implement TES-native contracts, names, storage, and oracles. |

## Consequences

- TES gains a stable rule for Claude Code, Codex, Cursor, Git hook managers, and future hosts without flattening them.
- Future hook/runtime work must spend proof on executable host fixtures and idempotent installation, not on prose claims.
- Host-unobservable limits become explicit instead of hidden behind green local materialization checks.
- Runtime surfaces can remain quiet and advisory while still becoming stricter for high-risk actions.
- The package can absorb lessons from mature references without copying their code, API, storage model, branding, or identifiers.

## Non-Goals

- No runtime implementation in this ADR phase.
- No hook, installer, script, adapter, public bundle, version, release, push, tag, publish, marketplace, cloud, or secret action.
- No new host abstraction that erases host differences.
- No replacement of ADR 0007; ADR 0008 generalizes the host-aware invariant that ADR 0007 needed for Cortex.
- No product dependency on `.tes/FEEDBACK-LOOP.md`.

## Future Implementation Gates

A later Super SPEC must prove:

1. source-derived host contract inventory for Claude Code, Codex, Cursor, and Git hook managers where affected;
2. executable fixtures for every affected host contract;
3. runtime topology that preserves one semantic core and host-specific projections;
4. installer idempotency and preservation for native Git, Husky, Lefthook, and project-owned hook/config owners where affected;
5. no noisy default behavior for successful advisory supervision;
6. negative checks for host-contract flattening, bootloader protocol duplication, copied reference implementation, and config-only certification;
7. release identity decision for delivered behavior.

## Evidence References

- `AGENTS.md`
- `.claude/CLAUDE.md`
- `docs/adr/0004-tes-capsule-isolation-and-reversible-installation.md`
- `docs/adr/0007-cortex-proactive-memory-and-mesh-drift.md`
- `docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-runtime-first-delivery.md`
- `docs/adapters/PLATFORM-DIFFERENCES.md`
- `scripts/cortex_host_contract_oracle.py`
- `scripts/platform_surface_oracle.py`
- `scripts/tes_install.py`
- `src/adapters/**`
- read-only mature reference review under `tmp/project-mem0/mem0/integrations/mem0-plugin/**`

## Done

ADR 0008 is satisfied when it is indexed, discoverable from the repository documentation map, validated by TDS/reference-package oracles, and a follow-on Super SPEC exists to materialize host-aware runtime contracts without claiming runtime delivery from this ADR alone.
