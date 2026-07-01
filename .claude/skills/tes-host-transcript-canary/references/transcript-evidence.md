# Transcript Evidence

Use this reference when deciding whether a Claude Code transcript is sufficient
evidence for a host-backed canary claim.

## Evidence Boundary

Raw transcript JSONL remains local. Reports, commits, docs, and ledgers may
include only:

- transcript path when safe and useful;
- transcript SHA-256;
- parsed event counts;
- safe tool names;
- tool-use and tool-result counts;
- status, blockers, and failure class;
- safe command label and command fingerprint;
- stdout/stderr byte counts and hashes.

Never stage prompt text, tool inputs, tool results, subagent metadata content,
raw JSONL lines, secrets, credential material, or private target vocabulary.

## Required Signals

For a transcript-backed canary claim, require:

- parseable JSONL;
- at least one user event and one assistant event;
- fresh transcript hash for replay;
- required tool-use evidence when the claim depends on tool execution;
- subagent evidence when the host command delegated material work;
- explicit connection between command fingerprint, transcript hash, fix, and
  replay.

## Failure Classes

- `host_execution_gap`: the command did not run, attached to the wrong target,
  failed before producing host evidence, or timed out.
- `transcript_gap`: transcript is absent, stale, malformed, not parseable, or
  lacks required user/assistant/tool-use events.
- `oracle_gap`: transcript exists but the current oracle cannot express the
  evidence needed for the canary decision.
- `product_gap`: TES source behavior caused the canary failure.
- `evidence_gap`: the report or ledger does not connect command, transcript,
  correction, replay, and gates.
- `false_green`: a gate passed without proving host-real execution.

## Stale Evidence

Treat a `PASS` as stale when:

- replay resolves to the same transcript hash;
- event counts materially shrink without explanation;
- tool-use evidence disappears;
- a later correction has no newer host transcript;
- the ledger has a fix commit but no replay record.

Stale evidence is `NEEDS_EVIDENCE`, not partial progress.

## Subagents

When subagents are relevant, include subagent transcript counts and metadata
hashes only. Do not copy subagent messages, tool inputs, outputs, or metadata
content into tracked artifacts.
