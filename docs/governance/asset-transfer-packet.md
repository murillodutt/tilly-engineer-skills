---
tds_id: governance.asset_transfer_packet
tds_class: governance
status: active
consumer: maintainers, repository agents, and the Mantra Gate senior-manager detector
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Asset Transfer Packet Contract

This document is the machine-readable contract for the asset-transfer packet.
It exists so the Mantra Gate senior-manager detector has a concrete surface to
read, parse, and validate when deciding whether an asset-transfer packet is
present for a newly introduced skill. Without this contract the detector would
have nothing to read and would be a facade (the R1 failure the Tree Adversary
confirmed).

`docs/adr/0005-asset-transfer-to-existing-surfaces.md` is the **law**: it
accepts the asset-transfer framing and defines the eight packet fields. This
document is the **contract derived from that law**: it fixes the eight fields,
the machine-readable ledger shape, and the completeness rule that the detector
cites and enforces. When the law and this contract disagree, the law wins for
intent; this contract wins for the exact shape the detector parses.

## The Eight Required Fields

The asset-transfer packet has exactly eight required fields. The definitions
below are copied faithfully from ADR 0005, which is the source of truth for
their meaning.

| Field | Definition |
|-------|-----------|
| `target_asset` | Existing skill, script, hook, agent file, benchmark, adapter source, or route being changed. |
| `current_failure` | Falsifiable weakness in that asset: ambiguity, bloat, weak proof, bad routing, horizontal slicing, language drift, or shallow architecture. |
| `transferred_behavior` | The external behavior being absorbed, stated generically. |
| `smallest_patch` | The smallest edit to the existing asset that changes behavior. |
| `proof` | Focused oracle, fixture, benchmark, self-test, or materialization check that can fail before or after the patch. |
| `regression_surface` | Installed, generated, public, adapter, benchmark, or source surface that could regress. |
| `release_identity` | Maintainer-only or delivered behavior; if delivered, whether version/bundle surfaces must move. |
| `no_new_skill_evidence` | Why the existing asset can carry the behavior, or why a future new skill would be unavoidable. |

The cardinality is fixed at eight. There are no optional fields and no extra
required fields. The detector reads this cardinality from this contract, not
from the ADR.

## Machine-Readable Ledger Format

This is the new part the detector consumes. When a new skill is introduced — an
added file matching the glob `*/skills/*/SKILL.md` in the staged set — there
must exist a corresponding asset-transfer packet entry in the ledger
`.tes/field-reports/mantra-gates.jsonl`.

Each packet is a single JSON object on its own line (JSONL) with this shape:

```json
{
  "kind": "asset_transfer_packet",
  "skill_name": "<nome-da-skill>",
  "target_asset": "...",
  "current_failure": "...",
  "transferred_behavior": "...",
  "smallest_patch": "...",
  "proof": "...",
  "regression_surface": "...",
  "release_identity": "...",
  "no_new_skill_evidence": "..."
}
```

### Completeness Rule

A packet is **complete** only when **all** of the following hold:

1. `kind == "asset_transfer_packet"`.
2. `skill_name` matches the name of the staged skill (the skill directory name
   under `*/skills/<skill_name>/SKILL.md`).
3. All eight required fields above are present as keys.
4. Every one of the eight required field values is non-empty.

If a skill is added and no matching complete packet exists in the ledger — the
packet is missing, has the wrong `kind`, has a `skill_name` that does not match
the staged skill, is missing one or more of the eight fields, or carries an
empty value for any field — the verdict is `DRIFT_FROM_CONTRACT`.

A complete, matching packet yields a passing verdict for that skill. An
incomplete or absent packet yields `DRIFT_FROM_CONTRACT`.

## Falsifiability

This contract is the self-falsification surface for the detector. The detector's
green criterion is: **editing the packet contract changes the verdict.**

Concretely: editing this contract to change the cardinality of the required
fields — adding a ninth required field, removing one of the eight, or changing
the completeness rule — MUST change the detector's verdict for a previously
passing skill. That is what makes the detector auto-falsifiable. The detector is
not tied to the ADR on its critical path; it is tied to this editable contract.
If a change to this contract does not move the detector's verdict, the detector
is reading something else and is a facade.

## Boundary Note

This contract is maintainer/repository-layer governance. It governs agents
developing the Tilly Engineer Skills package and the Mantra Gate detector that
runs against this repository. It is **not** a target-project rule, **not** an
adopter instruction, and it does **not** enter `src/adapters/**` or any
delivered surface. Do not copy it into target bootloaders, adapter sources, or
user-facing manuals.
