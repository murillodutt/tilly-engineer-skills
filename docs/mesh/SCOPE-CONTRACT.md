---
tds_id: mesh.scope_contract
tds_class: mesh
status: active
consumer: Cortex maintainers, Field Reports maintainers, oracle authors, and adapter authors
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# TES Scope Contract

TES runtime scope is the normalized identity envelope shared by Cortex, Field Reports, event ledgers, checkpoints, and future operator commands.

It is not the project name, a user identity, a filesystem path, a branch name, or a public durable memory cell.

## Contract

The deterministic helper is `scripts/scope_contract.py`.

Every normalized scope carries:

- `schema`: currently `tes-scope@1`.
- `project`: an opaque fingerprint derived from the local target path.
- `adapter`: the runtime adapter or `unknown-adapter`.
- `agent`: the acting agent when known.
- `parent_agent`: the parent coordinator when known.
- `run`: a caller-provided run id or deterministic derived run fingerprint.
- `source`: the TES subsystem producing the scope.
- `evidence_ref`: a bounded TES evidence reference.
- `timestamp`: UTC ISO-8601 seconds with `Z` suffix.
- `status`: operational status when no trust level is supplied.
- `trust_level`: trust classification when no status is supplied.

`agent` or `parent_agent` must be present. `status` or `trust_level` must be present.

## Evidence References

Scope evidence references are not arbitrary paths. The helper accepts only:

- `.tes/field-reports/**` transport evidence.
- `docs/agents/cortex/sources/**` Cortex source evidence.
- `docs/agents/evidence/**` project evidence.
- `docs/agents/cortex/MAP.md`, `TRAIL.md`, or `LINKS.md`.
- `none` when the command has no evidence-bearing artifact yet.

`sources/**` is canonicalized to `docs/agents/cortex/sources/**`.

Absolute paths, home-relative paths, traversal, URLs, personal data, and secret-like labels fail closed. A failed scope must not be hidden as a generic fallback.

## Privacy Boundary

The `project` field is an opaque local fingerprint so that Field Reports, receipts, future ledgers, and Cortex command output can correlate a run without publishing project names or local paths.

Tracked TES source, docs, fixtures, commits, evidence, and release material must continue to use neutral vocabulary such as `target-project` or `canary-project`. A scope fingerprint is runtime metadata, not public product copy.

## Runtime Consumers

Cortex CLI output attaches a normalized `scope` object to command results. Scope failure turns a previously passing Cortex command result into `FAIL`.

Field Reports attaches a normalized `scope` object to captured events. If a caller supplies an unsafe scope evidence reference, capture returns `BLOCKED` and writes nothing to the outbox.

MCP remains read-only. This scope contract does not authorize MCP mutation, checkpoint promotion, Field Reports doctrine memory, or subagent durable writes.

## Certification

The focused scope gate is:

```text
python3 scripts/scope_contract.py --self-test
```

The package closure gate also runs the Cortex and Field Reports quality oracles so consumer integration cannot silently drop the scope envelope.
