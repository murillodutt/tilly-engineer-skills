---
tds_id: roadmap.goal_super_spec_tes_loop_sentinel
tds_class: roadmap
status: proposed
consumer: maintainers, Goal Maestro authors, hook authors, runtime authors, oracle authors, and execution agents
source_of_truth: false
evidence_level: L1
tver: 0.1.0
---

# GOAL Super SPEC: TES Loop Sentinel Harness

Status: proposed concept. This document preserves a future target idea. It does not deliver a skill, hook agent, runtime script, installer behavior, public docs, release identity, or bundle change.

Capability: create a partner harness for long TES execution loops. The Sentinel studies the active ADR/PRD/SPEC, watches the executing harness, researches uncertainty, detects drift and debt early, and feeds concise mentor guidance without becoming the executor.

Selected harness name: `tes-loop-sentinel`.

Selected bridge model: local hybrid bridge. Use `.tes/FEEDBACK-LOOP.md` for concise agent-facing guidance, and `.tes/loop-sentinel/events.jsonl` plus `.tes/loop-sentinel/state.json` for durable machine-readable coordination. MCP remains a later optional coordination layer, not the first dependency.

## Core Rule

```text
Goal Maestro drives execution.
Loop Sentinel studies, watches, researches, and advises.
Feedback Loop carries concise guidance.
Owner decides escalation.
```

The Sentinel is not a replacement for `tes-goal-maestro`, not a sublayer inside it, and not a second executor. It is an independent mentor/auditor harness that protects long loops from degradation.

## Context

Long `tes-goal-maestro --execute-loop` runs can last hours and span multiple SPEC units, commits, oracles, repairs, and decisions. The parent runner must preserve active-SPEC discipline, subagent lifecycle, source-derived handoff, commit rhythm, release identity, and final audit. As the loop grows, cognitive load rises and small false greens become easy: skipped subagents, weak ledgers, stale skill copies, config-only certification, unproved host behavior, forgotten release identity, or unchallenged assumptions.

The host-aware runtime contract execution exposed a useful pattern. A second window can audit Git, ledger, commits, and feedback bridge while the execution window works. That audit can detect a gap the executing harness misses and write a short advisory into `.tes/FEEDBACK-LOOP.md`. A future harness should productize that collaboration without turning it into noisy governance.

## Mission

Design and later materialize `tes-loop-sentinel`: a skill plus optional hook-agent/runtime layer that accompanies long execution harnesses, especially `tes-goal-maestro --execute-loop`.

The Sentinel should:

1. read the active ADR/PRD/SPEC and derive an obligation matrix;
2. track declared units, active unit, allowed files, forbidden moves, oracles, commit rhythm, and stop states;
3. monitor Git state, staged files, commits, ledger entries, and feedback bridge state;
4. research uncertainty through repository source, official docs, Context7/MCP, installed source, package metadata, and approved reference projects;
5. detect drift, bugs, tech debt, stale packages, weak oracles, false greens, and missing release identity;
6. write concise advisory guidance to `.tes/FEEDBACK-LOOP.md`;
7. notify the owner only when a real decision, risk, or intervention is needed;
8. perform or request a final independent audit when the executing harness claims closure.

## Authority Boundary

The Sentinel may read broadly, run read-only oracles, inspect package metadata, query official docs/Context7/MCP when uncertainty is volatile, and write advisory text to local feedback files.

The Sentinel must not:

- execute active SPEC implementation;
- edit product/source files unless a later SPEC explicitly authorizes an auditor repair mode;
- commit product changes;
- push, tag, publish, release, use secrets, or mutate cloud/marketplace state;
- rewrite the executing harness ledger;
- become the source of truth over the owner request, ADR/SPEC, source, oracles, or Git evidence;
- turn successful loops into noisy status chatter.

## Surfaces

### Skill

Selected skill name: `tes-loop-sentinel`.

The skill owns:

- activation rules;
- audit posture;
- obligation matrix extraction;
- feedback bridge format;
- escalation rules;
- stop states;
- final independent audit expectations;
- no-executor boundary.

### Hook Agent

Future hook agent surfaces may include:

- Git `post-commit` or hook-manager equivalent;
- ledger file change;
- `.tes/FEEDBACK-LOOP.md` state change;
- heartbeat fallback for hosts without event hooks;
- optional pre-close audit trigger.

Hook behavior must follow ADR 0008: host-aware, idempotent, hook-manager-aware, no config-only certification, no universal hook protocol, and no hard block for routine advisory checks.

### Runtime Script

Potential script: `scripts/loop_sentinel.py`.

Responsibilities:

- parse active Super SPEC/ADR references;
- parse loop ledger;
- inspect Git state and recent commits;
- run selected read-only oracles;
- detect missing worker/subagent lifecycle evidence;
- detect no-commit rationale gaps;
- detect broad commit or out-of-unit changes;
- detect package/version/release identity risk;
- emit a compact machine-readable status and optional feedback text.

### Feedback Bridge

Default human-and-agent bridge: `.tes/FEEDBACK-LOOP.md`.

Rules:

- local-only and advisory;
- short enough for repeated reading;
- explicit `status=OK`, `status=WATCH`, or `status=INTERVENTION_REQUIRED`;
- includes one next action, not a long report;
- never carries secrets, raw diffs, private target names, or source-of-truth decisions.

Default machine bridge:

- `.tes/loop-sentinel/events.jsonl` records append-only observations, warnings, source classes, SPEC ids, worker ids, oracle ids, commit ids, and stop states.
- `.tes/loop-sentinel/state.json` records the current compact state: active contract, active SPEC, last checked commit, last feedback status, and next recommended check.

The Markdown bridge is the resilient coordination surface across Codex, Claude, Cursor, and degraded loops. The JSONL/state bridge is the durable automation surface for oracles, replay, deduplication, and long-loop continuity.

MCP is reserved for a later promotion when the local bridge is already proven. MCP may eventually provide richer cross-window coordination, memory-backed recall, and queryable audit state, but the Sentinel must remain useful without MCP.

## Research Role

The Sentinel may reduce executor load by researching questions before they block:

- official host hook behavior;
- current package APIs and versions;
- framework/plugin docs;
- MCP capabilities;
- related repo/reference patterns;
- known production failure classes;
- package update or deprecation risks.

For volatile behavior, it must cite the source class used: local source, installed source, official docs, Context7/MCP, package metadata, or reference project. If it cannot discover the fact, it reports `NEEDS_DISCOVERABILITY`; it does not guess.

## Detection Matrix

| Risk | Sentinel Detection |
|------|--------------------|
| SPEC drift | active unit differs from first unexecuted unit, or later unit files move early |
| False green | oracle passes but does not test the claimed property |
| Ledger debt | missing Pre-Edit Gate, worker lifecycle, no-commit rationale, commit hash, or audit fields |
| Subagent collapse | `--execute-loop` runs in parent without explicit fallback |
| Host flattening | one hook output protocol used for multiple host contracts |
| Config-only certification | file exists but runtime firing/observable proof is missing |
| Tech debt | new script grows into orchestration, duplicates protocol, or bypasses existing helpers |
| Package staleness | dependency/API behavior uncertain or outdated without upstream check |
| Release identity miss | delivered behavior changes without version/bundle decision |
| Reference contamination | copied identifiers, branding, storage assumptions, or API assumptions from reference projects |
| Noisy success | clean advisory path produces verbose or blocking output |

## Stop States

- `OK`: no material drift detected.
- `WATCH`: low-risk issue found; feedback bridge updated, no owner decision required.
- `INTERVENTION_REQUIRED`: executor should stop before next commit or next SPEC.
- `NEEDS_OWNER_DECISION`: scope, fallback, release, public surface, remote sync, or authority is unclear.
- `NEEDS_DISCOVERABILITY`: a required claim cannot be discovered from approved sources.
- `NEEDS_INDEPENDENT_AUDIT`: closure depends on evidence authored by the same operator.
- `SAFETY_BLOCKED`: secrets, destructive action, private data, unauthorized remote, or bypass risk exists.

## Future Implementation Units

1. **SPEC-000 Contract Draft**
   - Materialize skill contract, boundaries, stop states, and TDS/index entries.
   - No runtime behavior.

2. **SPEC-001 Sentinel Read-Only Core**
   - Add a script that parses Git, Super SPEC, ledger, and feedback bridge.
   - Prove no product edits and no commits.

3. **SPEC-002 Ledger And Harness Gap Oracles**
   - Detect missing worker lifecycle, Pre-Edit Gate, no-commit rationale, auditor distinction, and parent fallback authorization.

4. **SPEC-003 Research Assistant Lane**
   - Add source-classed research packets for official docs, Context7/MCP, installed source, package metadata, and reference projects.

5. **SPEC-004 Hook-Agent Triggers**
   - Add host-aware event triggers: post-commit, ledger-change, feedback-change, and heartbeat fallback.
   - Prove native Git, Husky, Lefthook, and project-owned hook routing.

6. **SPEC-005 Product Boundary And Noise Control**
   - Ensure clean loops stay quiet and only meaningful risks notify.

7. **SPEC-006 Release Identity And Local Certification**
   - Decide whether delivered behavior requires version/bundle update and certify locally.

## Open Decisions

- Whether hook-agent triggers live in the installed product by default or as maintainer-only opt-in.
- Whether final independent audit can be automated enough to run without a second live agent.
- Whether Sentinel should ever open a bounded auditor repair SPEC, or remain strictly advisory.
- How to certify package/version staleness checks without creating internet-noise or false urgency.
- When, if ever, MCP should be promoted from optional enhancement to delivered coordination surface.

## Done

This proposed Super SPEC is done when the idea is retained, indexed, and validated as a future target without claiming delivered behavior. A later owner request must promote it into an active implementation line before code, hooks, skills, or release identity move.
