---
tds_id: roadmap.goal_super_spec.tes_host_transcript_canary_runtime_signal_harness
tds_class: roadmap
status: active
consumer: maintainers, host-canary harness authors, oracle authors, installed-canary operators, and execution agents
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# GOAL-SUPER-SPEC: TES Host Transcript Canary Runtime Signal Harness

Status: active corrective Super SPEC.

Purpose: evolve `tes-host-transcript-canary` from a host transcript replay
harness into a calibrated runtime-signal certification harness, based on the
CORTEX memory canary loop that exposed a false green, forced a source-owned
repair, and then proved host-real memory injection through Claude Code
transcripts, hook ledgers, and a generated artifact.

## Evidence Base

The CORTEX flappy canary loop exposed five harness gaps:

- one host command mode was used for quick smoke, product canary, and ceiling
  replay;
- runtime signal checks were performed with ad hoc scripts instead of a reusable
  harness oracle;
- the CORTEX seed-memory pattern was useful but not retained as a recipe;
- contamination detection initially confused benign marker reuse with manual
  memory lookup;
- Goal Maestro replay produced very strong evidence but at high runtime cost.

The successful final proof shape was:

```text
clean target -> install final bundle -> seed CORTEX memory ->
real Claude host command -> fresh transcript -> hook ledger ->
first artifact mutation with runtime context -> artifact marker present ->
no manual memory lookup -> related source/package gates
```

## Central Rule

```text
The harness must select the smallest host-real mode that can falsify the claim,
then preserve enough transcript, ledger, and artifact signals for a future
window to reconstruct the decision without raw transcript content.
```

## Platform Classification

This work is `Platform` in the maintainer/development layer. It does not change
adopter-facing TES runtime behavior by itself, but it governs how installed
targets, host hooks, transcripts, CORTEX runtime memory, and canary claims are
certified.

## Protected Baseline

Preserve the existing `tes-host-transcript-canary` contract:

- raw Claude JSONL transcripts remain local and unstaged;
- sanitized evidence may include paths, hashes, counts, safe tool names,
  statuses, blockers, and failure classes;
- transcript evidence strengthens but never replaces package, install, Git,
  hook, or canary gates;
- source-owned defects are repaired in source, not installed canary mirrors;
- fresh transcript hash and tool-use evidence are required for host-real claims;
- same-command replay remains the default for corrective loops.

## Non-Objectives

- Do not package this harness as adopter-facing TES behavior.
- Do not stage raw transcript JSONL, tool inputs, tool results, prompts,
  secrets, or subagent metadata content.
- Do not create a broad dashboard, remote upload, cloud service, or background
  monitor.
- Do not weaken existing gates to make host canaries easier to pass.
- Do not make Goal Maestro the default path for every smoke-level claim.

## Required New Surfaces

- `references/canary-modes.md`
- `references/memory-runtime-canary.md`
- `references/transcript-contamination.md`
- `scripts/runtime_signal_audit.py`
- `templates/runtime-signal-report.template.md`

## Stop States

- `NEEDS_CANARY_MODE`
- `NEEDS_RUNTIME_SIGNAL_AUDIT`
- `NEEDS_MEMORY_CANARY_RECIPE`
- `NEEDS_CONTAMINATION_CLASSIFIER`
- `NEEDS_COST_BRAKE`
- `NEEDS_SIGNAL_REPORT_TEMPLATE`
- `PASS_RUNTIME_SIGNAL_HARNESS`

## SPEC-001 - Canary Mode Taxonomy

Goal: make host canary scope explicit before execution.

Implement `references/canary-modes.md` with exactly three modes:

- `smoke-host-real`: prove host command attachment, fresh transcript, required
  tool-use, and a minimal ledger signal.
- `product-host-real`: prove host execution produced or modified the target
  artifact and that the artifact carries the expected runtime signal.
- `ceiling-replay`: prove full same-command replay, subagent evidence, related
  package/install gates, and no unresolved floor-green weakness.

Rules:

- The harness must choose or record one mode before execution.
- The mode determines required evidence and stop conditions.
- A lower mode cannot be reported as a higher mode.
- A higher mode may reuse lower-mode evidence, but must add the missing signals.

Oracle:

- A reference-level fixture table maps each mode to required fields.
- `host_canary_loop.py --self-test` includes one case where a smoke result is
  rejected as a ceiling result.

Stop state: `NEEDS_CANARY_MODE`.

## SPEC-002 - Runtime Signal Audit Script

Goal: replace ad hoc transcript/ledger/artifact checks with one deterministic
runtime signal oracle.

Create `scripts/runtime_signal_audit.py`.

Inputs:

- `--target <path>`;
- `--session-id <id>` or `--latest`;
- `--expected-marker <safe marker>`;
- `--artifact <relative path>` optional, repeatable;
- `--require-first-mutation-context`;
- `--json-only`.

Output fields:

- `status`;
- `target`;
- `session_id`;
- `transcript_path`;
- `transcript_sha256`;
- `tool_use_count`;
- `tool_result_count`;
- `subagent_count`;
- `ledger_rows`;
- `host_real_rows`;
- `runtime_context_rows`;
- `marker_rows`;
- `artifact_checks`;
- `first_mutation`;
- `manual_lookup_tool_uses`;
- `benign_marker_mentions`;
- `failure_class`;
- `blockers`.

Pass criteria for a runtime memory claim:

- transcript is fresh and parseable;
- required tool-use evidence exists;
- hook ledger has host-real rows for the same session;
- first mutation of the declared artifact has `cortex_context_emitted=true` or
  the configured runtime signal equivalent;
- expected marker is present in the artifact;
- manual lookup detector reports no forbidden lookup tool-use.

Oracle:

- Self-test fixtures for pass, missing ledger, missing marker, stale transcript,
  and manual lookup failure.

Stop state: `NEEDS_RUNTIME_SIGNAL_AUDIT`.

## SPEC-003 - Memory Runtime Canary Recipe

Goal: retain the CORTEX canary pattern as a reusable host-backed recipe.

Create `references/memory-runtime-canary.md`.

Recipe:

```text
create clean target
install final bundle
initialize memory runtime
seed unique safe marker
run direct hook smoke
run host command with manual lookup forbidden
audit transcript + ledger + artifact
classify pass, false green, product gap, or evidence gap
```

The reference must distinguish:

- seed memory setup performed by the harness before host execution;
- memory available to the agent only through hook/runtime injection;
- forbidden manual discovery by `Read`, `Grep`, `Glob`, `LS`, or shell lookup;
- expected benign marker reuse after the hook injected context.

Oracle:

- The runtime signal script can certify the recipe without custom one-off
  Python snippets.

Stop state: `NEEDS_MEMORY_CANARY_RECIPE`.

## SPEC-004 - Transcript Contamination Classifier

Goal: prevent both false negatives and false positives in transcript
contamination checks.

Create `references/transcript-contamination.md` and wire the classifier into
`runtime_signal_audit.py`.

Forbidden manual lookup:

- `Read`, `Grep`, `Glob`, or `LS` with `docs/agents/cortex`, `.tes/cortex`, or a
  configured memory path;
- `Bash` command using `cat`, `rg`, `grep`, `find`, `ls`, `sed`, `awk`, `python`,
  or `sqlite` against memory paths;
- `Bash` invoking `cortex.py recall`, `cortex.py read-cell`, or equivalent recall
  commands during the host agent run;
- subagent tool-use with the same forbidden pattern.

Benign signal use:

- `Write`, `Edit`, `MultiEdit`, or `Agent` payloads containing an expected marker
  already injected by the hook;
- validation commands that inspect the generated artifact for the expected
  marker;
- retained report text that references the marker without accessing memory
  storage.

Oracle:

- Fixtures prove that benign marker reuse passes.
- Fixtures prove that direct memory file reads fail.
- Fixtures prove that shell lookups fail even when the final artifact is
  correct.

Stop state: `NEEDS_CONTAMINATION_CLASSIFIER`.

## SPEC-005 - Ceiling Cost Brake

Goal: keep ceiling proof strong without making every loop pay Goal Maestro
runtime cost.

Add a cost-brake rule to `references/canary-modes.md` and the runtime signal
report:

- If the selected mode is `smoke-host-real`, stop after transcript + required
  ledger signal pass.
- If the selected mode is `product-host-real`, stop after transcript + first
  artifact mutation + artifact marker + contamination pass.
- If the selected mode is `ceiling-replay`, continue through subagents and
  related gates.
- Escalate from a lower mode only when the lower-mode evidence exposes drift,
  a false green, a product gap, or a claim that requires broader proof.

The cost brake is not a shortcut. It is a claim-to-proof alignment rule: do not
pay for a broader proof than the claim can use, and do not claim a broader proof
than the mode produced.

Oracle:

- A product-mode fixture with all required runtime signals passes without
  requiring unrelated ceiling gates.
- A ceiling claim from product-mode evidence fails as `NEEDS_COST_BRAKE`.

Stop state: `NEEDS_COST_BRAKE`.

## SPEC-006 - Runtime Signal Report Template

Goal: make retained or chat-emitted evidence consistent and sanitized.

Create `templates/runtime-signal-report.template.md`.

Required sections:

- safe command label and command fingerprint;
- selected mode;
- target fingerprint;
- transcript status and SHA-256;
- tool-use/tool-result counts;
- subagent count when included;
- ledger runtime signal summary;
- first artifact mutation summary;
- artifact marker summary;
- contamination classification;
- related gates;
- residual blockers;
- decision.

Forbidden sections:

- raw prompt text;
- raw transcript JSONL;
- tool inputs/results;
- subagent messages;
- secrets or credentials.

Oracle:

- Template lint in the harness self-test verifies required headings and forbidden
  raw-content placeholders.

Stop state: `NEEDS_SIGNAL_REPORT_TEMPLATE`.

## SPEC-007 - Harness Validation And Parity

Goal: close the harness update without drifting `.agents` and `.claude` copies.

Validation:

- `python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/tes-host-transcript-canary`
- `python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .claude/skills/tes-host-transcript-canary`
- `diff -qr .agents/skills/tes-host-transcript-canary .claude/skills/tes-host-transcript-canary`
- `python3 .agents/skills/tes-host-transcript-canary/scripts/host_canary_loop.py --self-test --repo .`
- `python3 .agents/skills/tes-host-transcript-canary/scripts/runtime_signal_audit.py --self-test --repo .`
- `python3 scripts/canary_transcript_oracle.py --self-test`
- `python3 scripts/validate_tds.py`

Acceptance:

- The five new surfaces exist and are routed from `SKILL.md`.
- The root `SKILL.md` stays thin.
- Raw transcripts remain unstaged.
- The runtime signal script can reproduce the CORTEX canary decision from a
  sanitized fixture.
- A future window can select smoke, product, or ceiling mode without inventing
  ad hoc scripts.

Stop state: `PASS_RUNTIME_SIGNAL_HARNESS`.

## Implementation Order

1. Add references and template with route-map entries in `.agents` and `.claude`.
2. Add `runtime_signal_audit.py` with self-tests.
3. Update `host_canary_loop.py` only where needed to record selected mode and
   link to the runtime signal audit.
4. Mirror `.agents` and `.claude` harness copies.
5. Run validation and one product-mode host canary replay when authorized.

## Closeout Decision

This Super SPEC is complete only when the harness can reproduce the CORTEX loop
as a product-mode runtime signal decision without one-off audit scripts, while
still preserving the stronger ceiling replay path for claims that need it.
