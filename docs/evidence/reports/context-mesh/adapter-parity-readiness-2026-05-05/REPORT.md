---
tds_id: evidence.context_mesh.adapter_parity_readiness_2026_05_05
tds_class: evidence
status: active
consumer: certification reviewers and adapter authors
source_of_truth: false
evidence_level: L3
---

# Adapter Parity Readiness Report

This report certifies structural and contract parity readiness for the current
adapter set. It does not certify behavior parity.

## Decision

Result: `GO`

Claim:

```text
structural/contract parity readiness only; no behavior parity claim
```

The next risk after Context Mesh v1-rc is adapter drift, not model behavior.
This loop checks that Codex, Claude, and Cursor receive the same neutral
behavioral contract before any new behavior backend work.

## Gate

Command:

```bash
npm run adapter:parity:check
```

Output:

```text
[adapter-parity-readiness] GO
git_head=a6f21af01057a9ea9f62645058de1155bd6393d2
contract_manifest=docs/mesh/CONTRACT-MANIFEST.yml
claim=structural/contract parity readiness only; no behavior parity claim

contract_gates:
- Think Before Coding
- Simplicity First
- Surgical Changes
- Goal-Driven Execution

source_results:
- claude: GO
- codex: GO
- cursor: GO

materialized_results:
- claude: GO
- codex: GO
- cursor: GO

benchmark_condition_labels: GO samples_checked=44
```

## Readiness Matrix

| Area | Criterion | Result |
|------|-----------|--------|
| Source | One neutral contract remains canonical | `GO` |
| Claude source | Source files preserve four gates, core contract, and success formula | `GO` |
| Codex source | Source files preserve four gates, core contract, and success formula | `GO` |
| Cursor source | Source files preserve four gates, core contract, and success formula | `GO` |
| Claude materialization | Materialized files preserve four gates, core contract, and success formula | `GO` |
| Codex materialization | Materialized files preserve four gates, core contract, and success formula | `GO` |
| Cursor materialization | Materialized files preserve four gates, core contract, and success formula | `GO` |
| Benchmark condition labels | Prompts do not expose `full`, `none`, or `drop:<section>` labels to backend context | `GO` |
| Claim boundary | Structural/contract parity only | `GO` |

## Canonical Contract

Source:

```text
docs/mesh/CONTRACT-MANIFEST.yml
```

Gates:

| Gate |
|------|
| Think Before Coding |
| Simplicity First |
| Surgical Changes |
| Goal-Driven Execution |

## Adapter Scope

| Adapter | Current parity level | Behavior claim |
|---------|----------------------|----------------|
| Claude | Structural and contract readiness | Existing Claude behavior run remains scoped to its retained run/hash |
| Codex | Structural and contract readiness | No behavior backend certified |
| Cursor | Structural and contract readiness | No behavior backend certified |

## NO-GO Boundaries

- Do not declare behavior parity from this report.
- Do not declare Codex behavior certification.
- Do not declare Cursor behavior certification.
- Do not treat different adapter capabilities as drift.
- Do not compare adapter prose by literal text equality.
- Do not start behavior backend work until structural/contract readiness stays
  green after future adapter changes.

## Next Step

The next permitted loop is a behavior-readiness design pass per adapter. It
should start by defining execution backends and evidence limits, not by changing
the shared contract.
