---
tds_id: mesh.event_ledger
tds_class: mesh
status: active
consumer: Cortex maintainers, Field Reports maintainers, checkpoint authors, and oracle authors
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# TES Event Ledger

TES Event Ledger is the read-only inspection lane for lifecycle events.

It does not replace Field Reports, Cortex `TRAIL.md`, evidence reports, Git
history, checkpoints, or durable Cortex cells.

## Contract

The deterministic helper is `scripts/event_ledger.py`.

The inspected ledger path is:

```text
.tes/events/ledger.jsonl
```

The current schema is `tes-event-ledger@1`.

Minimum commands:

```bash
python3 scripts/event_ledger.py list --target /path/to/project
python3 scripts/event_ledger.py status --target /path/to/project
python3 scripts/event_ledger.py inspect-schema
python3 scripts/event_ledger.py --self-test
```

These commands inspect existing ledger bytes only. They must report `writes:
[]` and must not create, append, drain, publish, or promote anything.

## Lifecycle Map

Event lifecycle values map to the ADR memory flow:

| Event value | Lifecycle stage |
|-------------|-----------------|
| `scope` | scope normalization |
| `recall` | recall |
| `event` | event |
| `checkpoint` | checkpoint |
| `review` | review |
| `authorized_write` | authorized write |
| `evidence` | evidence |
| `closeout` | closeout |
| `subagent_return` | subagent return |

Allowed statuses are `PASS`, `FAIL`, `BLOCKED`, `DEGRADED`, `NEEDS_REVIEW`,
`SKIP`, and `CERTIFIED`.

## Privacy Boundary

Ledger entries carry the runtime scope from `docs/mesh/SCOPE-CONTRACT.md`.
Unsafe evidence references, absolute paths, URLs, emails, stack traces, and
secret-like values fail inspection and are redacted from command output.

The ledger never carries Field Reports `install_id`, GitHub issue transport
state, raw branch names, raw remotes, code, diffs, prompts, or file contents.

## Separation From Field Reports

Field Reports is operational transport. Event Ledger is local lifecycle
inspection. A Field Report can mention that an event-ledger inspection failed,
but the ledger itself is not drained through GitHub and is not the destination
for product feedback.

## Separation From Cortex

Cortex `TRAIL.md` remains the append-only evolution timeline for durable memory
changes. Event Ledger entries are coordination evidence and must not become
Cortex cells automatically.

Read-only event inspection must not write `docs/agents/cortex/TRAIL.md`,
`docs/agents/cortex/cells/**`, `.tes/field-reports/outbox.jsonl`, or
checkpoint state.

## Certification

The focused event-ledger gate is:

```text
python3 scripts/event_ledger.py --self-test
```

The self-test proves clean inspection, unsafe payload redaction, malformed
record failure, no hidden writes, and separation from Field Reports and Cortex.
