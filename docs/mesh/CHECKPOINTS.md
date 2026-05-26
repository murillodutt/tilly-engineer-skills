---
tds_id: mesh.checkpoints
tds_class: mesh
status: active
consumer: Cortex maintainers, checkpoint authors, installer authors, and oracle authors
source_of_truth: true
evidence_level: L2
tver: 0.1.1
---

# TES Checkpoints

TES Checkpoints are the TTL resumability lane for interrupted or resumable
agent work.

They do not replace Cortex cells, Cortex `TRAIL.md`, Event Ledger records,
Field Reports, evidence reports, Git history, release identity, or closeout
oracles.

## Contract

The deterministic helper is `scripts/checkpoint.py`.

The checkpoint state path is:

```text
.tes/checkpoints/*.json
```

The current schema is `tes-checkpoint@1`.

Minimum commands:

```bash
python3 scripts/checkpoint.py create --target /path/to/project --id run-id
python3 scripts/checkpoint.py list --target /path/to/project
python3 scripts/checkpoint.py status --target /path/to/project --id run-id
python3 scripts/checkpoint.py cleanup --target /path/to/project
python3 scripts/checkpoint.py inspect-schema
python3 scripts/checkpoint.py --self-test
```

`list`, `status`, and `inspect-schema` are read-only and must report
`writes: []`. `create` may write only `.tes/checkpoints/<id>.json`. `cleanup`
may delete only expired checkpoint files.

## Resume Status

Checkpoint inspection reports one of these resume states:

| Status | Meaning |
|--------|---------|
| `RESUMABLE` | The checkpoint is valid and has not reached its TTL. |
| `EXPIRED` | The checkpoint is valid but past `expires_at`; cleanup may delete it. |
| `MISSING` | The requested checkpoint id has no local checkpoint file. |
| `INVALID` | The checkpoint is malformed, unsafe, cross-scope, or claims authority it does not have. |

Invalid checkpoints remain visible to inspection. They are not silently
promoted, cleaned as success, or used as certification evidence.

## TTL Boundary

Every checkpoint carries `created_at`, `expires_at`, and `ttl_seconds`.

The default TTL is 24 hours. The maximum TTL is seven days. Longer retention
requires a future decision because checkpoints are temporary execution state,
not durable memory.

Expired checkpoint cleanup is bounded to `.tes/checkpoints/**`; it must not
touch `docs/agents/cortex/**`, `.tes/events/**`, `.tes/field-reports/**`, or
Git history.

## Privacy Boundary

Checkpoint records carry the runtime scope from `docs/mesh/SCOPE-CONTRACT.md`.
Unsafe evidence references, absolute paths, URLs, emails, stack traces, and
secret-like values fail or are redacted before command output.

Tracked TES source, docs, fixtures, evidence, commits, and release material
must continue to use neutral placeholder vocabulary.

## Non-Promotion Rule

Each checkpoint carries an authority block:

```json
{
  "automatic_promotion": false,
  "certification_evidence": false,
  "durable_memory_write": false,
  "rule": "checkpoint-only"
}
```

Changing any of these values makes the checkpoint invalid. A checkpoint cannot
bypass closeout, release identity, observed write evidence, or the Cortex write
gate.

The consolidation gate treats checkpoint-only state as temporary execution
context. It can explain why memory consolidation is blocked, but it cannot
certify durable memory.

## Certification

The focused checkpoint gate is:

```text
python3 scripts/checkpoint.py --self-test
```

The self-test proves schema validation, TTL classification, expired cleanup,
unsafe payload rejection and redaction, no hidden Cortex write, no Field
Reports write, and no automatic Event Ledger write.
