---
tds_id: architecture.cortex_git_tap_contract
tds_class: architecture
status: active
consumer: maintainers, Cortex runtime authors, installer authors, hook authors, oracle authors, and release reviewers
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Cortex Git Tap Contract

Cortex Git Tap is the Git-driven observation lane for Cortex. It converts local
Git activity into privacy-safe runtime events so Cortex can propose memory
maintenance without letting hooks write curated memory.

Central rule:

```text
Git hooks may capture, classify, queue, and propose Cortex memory. They must not
write durable curated memory into docs/** without an explicit curation step.
```

## Runtime Surface

The delivered helper is `scripts/cortex_git_tap.py`, installed as
`.tes/bin/cortex_git_tap.py` when TES runtime helpers are applied. It writes only
local runtime state:

```text
.tes/runtime/cortex/git-tap/events.jsonl
.tes/runtime/cortex/git-tap/pending.jsonl
.tes/runtime/cortex/git-tap/proposals.jsonl
.tes/runtime/cortex/git-tap/git-tap.log
.tes/runtime/cortex/git-tap/git-tap.lock
```

These files are local evidence and must stay untracked. Tracked docs may report
only schema versions, counts, hashes, anonymized categories, oracle names, and
statuses.

## Event Schema

The schema is `tes-cortex-git-tap@1`. Every event carries:

- `schema`;
- `timestamp`;
- `event`;
- `repo_fingerprint`;
- `branch`;
- `head_before`;
- `head_after`;
- `commit_hash`;
- `parent_hashes`;
- `changed_path_count`;
- `changed_path_categories`;
- `changed_file_extensions`;
- `diff_stat`;
- `staged_digest`;
- `gate_snapshot`;
- `memory_signal`;
- `privacy_status`;
- `blockers`.

The event may include an implementation-owned `event_fingerprint` for queue
dedupe. The event must not store raw diff hunks, prompt text, tool payloads,
file contents, secrets, credentials, raw host transcripts, unredacted command
output, or local absolute filesystem paths.

## Hook Behavior

`pre-commit` captures only a lightweight staged snapshot and gate signal. It
does not reflect, curate, run an LLM, or write memory.

`post-commit` captures committed change metadata and may launch a detached
background drain. The drain is no-LLM and no-write by default.

`post-checkout` captures branch-switch freshness events. Ordinary file checkout
is skipped.

The installer appends marked blocks to active Git hook files, preserves existing
hook content, respects `core.hooksPath`, treats Husky's `.husky/_` wrapper as a
manager-owned indirection, and removes only its own marked blocks on uninstall.
Impossible hook paths fail loudly instead of creating junk directories.

## Queue And Lock

`git-tap.lock` serializes drain work. If a hook fires while the lock is held,
the event is appended to `pending.jsonl` instead of being dropped. The lock
holder drains pending events before and after consolidation. Pending records are
deduplicated by event fingerprint.

Hook-triggered work must not block normal Git workflows. Manual drain may wait
on the lock for certification, while background drain reports a timeout without
blocking the Git command path.

## Reflect Boundary

`reflect-proposals` reads Git Tap events and writes reviewable local proposals
to `.tes/runtime/cortex/git-tap/proposals.jsonl`. It never writes `docs/**`.

Durable Cortex memory remains governed by the approved Cortex promotion path:
review the proposal, decide the claim, then use the explicit Cortex apply/write
command with approval. Hook execution cannot invoke that durable write path.

## Oracles

`python3 scripts/cortex_git_tap.py --self-test` is the focused red-capable
oracle. It covers schema validation, malformed JSONL, privacy rejection, hook
preservation, idempotence, `core.hooksPath`, impossible path rejection,
queue/lock drain, pending dedupe, curation boundary, merge/rebase/cherry-pick
skip, file-checkout skip, self-generated runtime loop prevention, append-only
logs, and missing-runtime hook diagnostics.
