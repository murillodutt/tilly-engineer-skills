---
name: tes-host-transcript-canary
description: Local-only Tilly development workflow for persistent host-backed canary execution with Claude CLI/host transcripts. Use when Codex must run or audit a TES canary through the real host, inspect Claude Code local JSONL transcripts, convert host execution history into sanitized evidence, preserve execution continuity across windows, run analytical/corrective replay loops, or prove that a canary claim is backed by host-real transcript evidence.
---

# TES Host Transcript Canary

Operational contract: `tes.host_transcript_canary@0.1.6`.

Central rule:

```text
Root routes. References own depth. Templates preserve evidence shape. Scripts prove fragile evidence.
```

Local development surface only. Do not package, publish, materialize, or treat
as adopter-facing TES behavior.

## Contract

Use this chain:

```text
host command -> local transcript JSONL -> sanitized oracle ->
analysis -> minimal correction -> same host command replay -> canary decision
```

The raw transcript stays local. Tracked evidence may contain paths, statuses,
counts, hashes, safe tool names, and blockers; it must not contain prompt text,
tool inputs, tool results, subagent metadata content, secrets, or raw JSONL.

This skill strengthens canary replay evidence. It does not replace
`canary_admission_oracle.py`, `installed_certification_oracle.py`,
`git_gate_contract.py`, package validation, or host/runtime gates.

## Load Routing

Load only the reference needed by the current loop:

| Need | Load |
|------|------|
| Real host command authority, same-command replay, correction ownership, stop states | `references/host-command-loop.md` |
| Transcript sanitization, required signals, subagents, stale evidence, failure classes | `references/transcript-evidence.md` |
| Final canary decision, related gates, certification closeout, ledger discipline | `references/canary-convergence.md` |
| Ceiling posture, floor-green rejection, strongest local proof, breakthrough loop | `references/ceiling-breakthrough.md` |
| Agent hook feature matrix, source/target/host evidence lanes, fix ownership, certification states | `references/agent-hooks-certification.md` |
| Host-real canary scope, mode evidence, and cost brake | `references/canary-modes.md` |
| CORTEX runtime memory canary recipe and runtime signal proof shape | `references/memory-runtime-canary.md` |
| Forbidden manual memory lookup versus benign injected marker reuse | `references/transcript-contamination.md` |
| A retained or chat-emitted sanitized evidence report | `templates/host-canary-report.template.md` |
| A retained agent hook certification report | `templates/agent-hooks-certification-report.template.md` |
| A retained runtime signal certification report | `templates/runtime-signal-report.template.md` |

If a claim depends on one of these behaviors, load the owning reference before
deciding. Do not inline reference-owned detail into `SKILL.md` just to make the
root feel complete.

## Scripted Loop Helper

Use `scripts/host_canary_loop.py` when the loop needs deterministic replay
memory, command fingerprinting, stale-transcript rejection, or a local
gitignored JSONL ledger:

```bash
python3 .agents/skills/tes-host-transcript-canary/scripts/host_canary_loop.py \
  --repo . \
  --target <target> \
  --command '<host command>' \
  --command-label '<safe label>' \
  --include-subagents \
  --require-tool-use \
  --mode product-host-real \
  --claim-mode product-host-real \
  --require-fresh \
  --enforce-same-command
```

Add `--execute` only when the command is authorized to run. The helper captures
return codes, output byte counts, and output hashes only; it does not write raw
commands, stdout, stderr, prompts, tool inputs, or tool results. Its default
ledger is `.tes/runs/host-canary-loop.jsonl`, which is local and gitignored.

## Workflow

1. Frame the canary target, host, command, expected transcript evidence, and
   stop condition. Stop before destructive, remote, secret-bearing, or
   credentialed commands unless Murillo explicitly authorizes that action.
2. Execute the real host command only when the request requires execution. For
   Claude Code, prefer the real CLI/host surface over simulated logs when the
   claim is host-real behavior.
3. Resolve the local Claude Code transcript:
   - Project directory: `~/.claude/projects/<project-slug>/`
   - Main transcript: `<session-id>.jsonl`
   - Subagents: `<session-id>/subagents/*.jsonl`
   - Slug resolution: use `scripts/canary_transcript_oracle.py` or an explicit
     transcript path. Claude Code may normalize path punctuation in the project
     slug, so do not rely on a hand-built slash-only slug.
4. Run the source oracle from the TES package root:

```bash
python3 scripts/canary_transcript_oracle.py --target <target> --latest --include-subagents --require-tool-use --json-only
```

Use `--transcript <path>` when the exact JSONL is known and `--session-id` when
the target has multiple host sessions.

For runtime memory claims, run the runtime signal audit after transcript
resolution:

```bash
python3 .agents/skills/tes-host-transcript-canary/scripts/runtime_signal_audit.py \
  --target <target> \
  --session-id <session-id> \
  --expected-marker '<safe marker>' \
  --artifact <relative artifact path> \
  --require-first-mutation-context \
  --json-only
```

5. Interpret statuses:
   - `PASS`: transcript exists, parses, has user and assistant events, and
     satisfies requested tool-use evidence.
   - `NEEDS_EVIDENCE`: no transcript, no tool-use evidence when required, or
     insufficient host evidence. Do not promote the canary claim.
   - `FAIL`: malformed JSONL or corrupted evidence. Classify before retrying.
6. Record only the sanitized oracle result or a concise summary. Include the
   transcript SHA-256 and command context when useful; never stage raw JSONL.
7. Combine transcript evidence with canary admission, installed certification,
   Git gate, package, and public-bundle gates before claiming convergence.

## Persistent Loop

Use a loop when the host command exposes a defect, gap, stale helper, false
green, missing evidence, or unexplained drift:

```text
run host command -> audit transcript -> classify failure -> patch source ->
rerun same host command -> audit new transcript -> rerun related gates
```

Loop rules:

- Keep one active hypothesis per iteration.
- Prefer replaying the same host command before broadening the gate set.
- Patch package source or local development skill source, not installed canary
  mirrors, unless the task is explicitly target-only evidence collection.
- Treat `PASS` without a fresh transcript hash as stale evidence.
- Treat a new transcript with fewer material events, no tool-use evidence, or
  malformed JSONL as `NEEDS_EVIDENCE`/`FAIL`, not progress.
- Continue while each loop produces a new classified failure or a smaller
  correction target.
- Stop as `BLOCKED` when the same blocker repeats after three attempts, the
  next action needs authority, or host truth cannot be observed.
- Stop as `CERTIFIED` only after the original host command replay, transcript
  oracle, and related TES gates all support the claim.

Failure classes:

- `host_execution_gap`: command did not run, did not attach to the expected
  target, or produced no usable host transcript.
- `transcript_gap`: JSONL absent, stale, malformed, or missing required tool
  evidence.
- `oracle_gap`: transcript exists but the source oracle cannot express the
  evidence needed for the canary decision.
- `product_gap`: TES source behavior caused the failed canary result.
- `evidence_gap`: reports or summaries do not connect command, transcript hash,
  correction, and replay.
- `false_green`: a gate passed without proving host-real execution.

## State Model

```text
framed -> host_executed -> transcript_resolved -> sanitized_oracle_run ->
loop_ledger_recorded -> failure_classified -> correction_applied ->
original_command_replayed -> related_gates_run -> canary_decision
```

- `produce_and_continue`: transcript path can be derived or the target can be
  re-run locally without destructive or remote effects.
- `hard_stop`: the next step needs destructive state, remotes, secrets, raw
  transcript staging, or a host/runtime truth that the oracle cannot observe.
- `post_run_learning`: repeated transcript gaps, stale sessions, missing
  subagent evidence, or useful host command patterns should be promoted to a
  source oracle, fixture, docs, or this skill only after material proof.

## Output

Keep the chat closeout short:

- host command or reason no host command ran
- transcript oracle status
- transcript hash and event/tool counts when available
- local loop ledger path when `host_canary_loop.py` wrote one
- loop count, last failure class, and original replay status when in loop mode
- related gates run
- blockers or next concrete fix

## Validation

When this skill changes, run:

```bash
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/tes-host-transcript-canary
python3 /Users/murillo/.codex/skills/.system/skill-creator/scripts/quick_validate.py .claude/skills/tes-host-transcript-canary
diff -qr .agents/skills/tes-host-transcript-canary .claude/skills/tes-host-transcript-canary
python3 .agents/skills/tes-host-transcript-canary/scripts/host_canary_loop.py --self-test --repo .
python3 .agents/skills/tes-host-transcript-canary/scripts/runtime_signal_audit.py --self-test --repo .
python3 .agents/skills/tes-host-transcript-canary/scripts/agent_hooks_certification_matrix.py --self-test --repo .
python3 scripts/canary_transcript_oracle.py --self-test
```

When references or templates change, inspect the route map above and verify the
changed file remains one level deep from `SKILL.md`.

If the skill is used in a canary loop, also run the target-specific
`canary_transcript_oracle.py --target ...` command and the smallest related
canary/package gate.

## Done

Done means a future window can reconstruct the host-backed canary method from
this skill, raw transcript content remains unstaged, the transcript oracle or
scripted loop helper ran or the blocker is classified, and the canary decision
still depends on the primary TES gates.

## Locks

- Do not put raw Claude JSONL transcripts in tracked files.
- Do not claim host-real evidence from agent memory alone.
- Do not let transcript evidence bypass Git, install, package, or host gates.
- Do not update bootloaders for this workflow unless the owner explicitly asks.
- Do not promote project-specific transcript paths into tracked content.
- Do not stage `.tes/runs/host-canary-loop.jsonl`; promote only portable rules
  back into this skill, source oracles, fixtures, or docs.
