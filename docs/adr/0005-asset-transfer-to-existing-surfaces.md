---
tds_id: architecture.adr_0005_asset_transfer_to_existing_surfaces
tds_class: architecture
status: active
consumer: maintainers, skill authors, oracle authors, benchmark authors, Goal Maestro authors, Prospect/Mine authors, and release operators
source_of_truth: true
evidence_level: L1
tver: 0.2.0
---

# ADR 0005: Asset Transfer To Existing TES Surfaces

Accepted on 2026-06-22 after inspecting Matt Pocock's public
`mattpocock/skills` repository at commit
`6eeb81b5fcfeeb5bd531dd47ab2f9f2bbea27461` and the Aditya Kumar Puri Medium
study shared by the maintainer. TES adopts transferable operating behavior, not
external packaging, command names, issue-tracker workflow, or project-specific
conventions.

## Correction

The first ADR 0005 draft correctly identified vertical proof and architecture
sanitization, but its operational posture drifted toward discovery governance.
That is not the product direction.

TES must not grow by creating more skills, routes, canaries, prompts, or
governance documents just because an external pattern is valuable. The value is
real only when it is absorbed into existing assets that agents actually load,
execute, validate, or install.

This ADR therefore replaces the discovery-first framing with an asset-transfer
framing:

```text
external learning -> existing TES asset -> falsifiable proof -> smaller surface
```

## Decision

TES will realign existing assets around a vertical proof loop:

```text
route -> pressure -> language -> slice -> prove -> implement -> sanitize -> retain
```

The loop is not a new governance layer. It is a constraint on how TES skills,
scripts, hooks, agents, benchmarks, and adapter surfaces are edited.

Every implementation wave under this ADR must produce an asset-transfer packet:

| Field | Requirement |
|-------|-------------|
| `target_asset` | Existing skill, script, hook, agent file, benchmark, adapter source, or route being changed. |
| `current_failure` | Falsifiable weakness in that asset: ambiguity, bloat, weak proof, bad routing, horizontal slicing, language drift, or shallow architecture. |
| `transferred_behavior` | The external behavior being absorbed, stated generically. |
| `smallest_patch` | The smallest edit to the existing asset that changes behavior. |
| `proof` | Focused oracle, fixture, benchmark, self-test, or materialization check that can fail before or after the patch. |
| `regression_surface` | Installed, generated, public, adapter, benchmark, or source surface that could regress. |
| `release_identity` | Maintainer-only or delivered behavior; if delivered, whether version/bundle surfaces must move. |
| `no_new_skill_evidence` | Why the existing asset can carry the behavior, or why a future new skill would be unavoidable. |

If the packet is missing, the implementation stops as `NEEDS_ASSET_PACKET`.

## Transfer Map

| External behavior | TES asset to harden first |
|-------------------|---------------------------|
| Relentless one-branch pressure | `tes-prospect` and `tes-mine` contracts, fixtures, and cognitive-brake proof. |
| Project language discipline | `tes-mine`, project context/glossary rules, Cortex proposal gates, and private-vocabulary oracle. |
| Vertical slices | `tes-goal-maestro`, its references, and `benchmarks/goal-maestro/**`. |
| Red-capable proof | `tes-engineering-discipline`, `discipline_oracle.py`, local quality recipe, and focused benchmark fixtures. |
| Architecture cleanup | Regression guard, deletion-test fixtures, route/oracle condensation, and pass-through surface review. |
| Lightweight routing | `docs/install/COMMAND-TRIGGERS.md`, `command_trigger_oracle.py`, installed adapter routing, and platform-surface checks. |
| Retention discipline | ADRs, TDS index, evidence reports, Cortex apply boundary, and contract histories. |

The first repair is never "create the missing skill." The first repair is one
of: condense an existing surface, move detail on demand, strengthen an oracle,
add a negative fixture, sharpen a loaded skill contract, delete pass-through
material, or route an existing asset more clearly.

## Mental Simulation

### Broad Product Idea

If a user arrives with a broad idea, TES should not jump to implementation or
write a large plan. The route selects the smallest existing surface, pressure
resolves one decision branch, language is sharpened only as needed, and Goal
Maestro materializes vertical units only after the artifact is mature enough.

Expected result: each expansion is earned by a decision and a proof candidate.

### Hard Bug

If a user reports a failure, TES starts with a reproducer or oracle, not an
architecture essay. The fix stays on the failing path. Sanitization happens only
after evidence shows that a shallow module or weak seam made the bug hard to
prove.

Expected result: architecture work follows evidence.

### Surface Bloat

If a maintainer wants a new skill, TES first tests existing surfaces. A new
skill is valid only when autonomous invocation or composition cannot be carried
by an existing asset without making that asset less clear.

Expected result: TES grows in leverage, not object count.

### Documentation Drift

If a new document explains behavior already owned by a skill, script, hook, or
oracle, the document is a smell. Move the behavior into the executable asset or
delete/condense the document.

Expected result: documentation routes and audits behavior; it does not replace
behavior.

## Invariants

1. No new skill by default.
2. No governance-only implementation wave.
3. No copied upstream packaging, command names, issue-tracker defaults, or
   private workflow assumptions.
4. Existing explicit-invocation contracts stay explicit unless a later accepted
   contract changes them.
5. Benchmark and oracle hardening beats explanatory prose when the behavior
   already exists.
6. Architecture sanitization must end in one of: `NO_CHANGE`, `CONDENSED`,
   `MOVED_ON_DEMAND`, `DEEPENED`, `DELETED`, `ROUTED_TO_UNIT`, or
   `NEEDS_OWNER_DECISION`.
7. Delivered behavior changes require release-identity classification before
   closure.
8. Private target-project vocabulary stays out of tracked TES source.

## Rejected Alternatives

| Alternative | Rejection |
|-------------|-----------|
| Mirror the external skill suite in TES. | It increases surface area and imports packaging instead of behavior. |
| Keep ADR 0005 as a discovery-only line. | It creates governance before asset transfer and delays product improvement. |
| Add a router skill first. | Current route, command, map, doctor, and bench surfaces must fail a deletion test before a new route exists. |
| Use canaries as the first move. | Canaries need a concrete target failure; otherwise they become ceremony. |
| Put long instructions in bootloaders. | TES already moved detail into lazy skills and references. |

## Consequences

ADR 0005 is implemented only when existing TES assets change or are proven
adequate. A future Super SPEC or GOAL prompt under this ADR must select concrete
assets and proof. A document-only closeout is incomplete unless the document is
removing, condensing, or correcting a prior governance error.
