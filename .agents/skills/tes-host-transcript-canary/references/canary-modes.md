# Canary Modes

Use this reference before running or certifying a host-real canary. The selected
mode fixes the evidence burden; a lower mode may not be reported as a higher
mode.

## Modes

| Mode | Claim It Can Support | Required Evidence | Stop Conditions |
|------|----------------------|-------------------|-----------------|
| `smoke-host-real` | The host command attached to the target and produced fresh transcript evidence. | safe command label, command fingerprint, fresh transcript hash, required tool-use count, minimal host-real ledger signal | `NEEDS_CANARY_MODE`, `NEEDS_EVIDENCE`, `false_green` |
| `product-host-real` | The host execution produced or modified a target artifact that carries the expected runtime signal. | all smoke evidence, artifact check, expected marker, first artifact mutation context, contamination pass | `NEEDS_RUNTIME_SIGNAL_AUDIT`, `NEEDS_CONTAMINATION_CLASSIFIER`, `product_gap`, `evidence_gap` |
| `ceiling-replay` | The full same-command replay supports a ceiling-grade canary decision. | all product evidence, same-command replay, subagent evidence when delegated, related package/install/Git/canary gates, no unresolved floor-green weakness | `NEEDS_COST_BRAKE`, `false_green`, `BLOCKED` |

## Cost Brake

The cost brake aligns proof to claim:

- `smoke-host-real` stops after transcript plus required ledger signal pass.
- `product-host-real` stops after transcript, first artifact mutation, artifact
  marker, and contamination checks pass.
- `ceiling-replay` continues through subagents and related gates.
- Escalate only when lower-mode evidence exposes drift, false green, product
  gap, or a claim that requires broader proof.

The brake is not a shortcut. Do not pay for proof the claim cannot use, and do
not claim proof the selected mode did not produce.

## Fixture Table

| Fixture | Selected Mode | Reported Claim | Expected Decision |
|---------|---------------|----------------|-------------------|
| fresh transcript plus host-real ledger row | `smoke-host-real` | smoke | pass |
| smoke evidence reported as ceiling | `smoke-host-real` | ceiling | `NEEDS_COST_BRAKE` |
| artifact marker and first mutation context present | `product-host-real` | product | pass |
| product evidence reported as ceiling without replay gates | `product-host-real` | ceiling | `NEEDS_COST_BRAKE` |
| same-command replay plus related gates | `ceiling-replay` | ceiling | pass |
