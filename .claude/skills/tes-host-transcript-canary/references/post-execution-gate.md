# Post-Execution Gate

Use this reference before closing any TES construction loop that uses or should
use host-backed canary evidence.

## Mandatory Rule

For TES construction work, `tes-host-transcript-canary` is mandatory. It is not
an optional confidence booster. A closeout that changes or certifies TES
Platform behavior must pass the post-execution gate or stop with an explicit
limited claim.

The gate asks the question that was previously missed:

```text
Did the execution only produce a signal, or did it prove the signal became
runtime-usable product behavior through the host-backed canary lane?
```

## Gate Order

Run this after the implementation loop and before the final answer:

1. Name the exact final claim.
2. Classify whether the claim is TES construction and whether it touches
   Platform behavior.
3. Verify the host-backed harness ran through the required chain:
   `host command -> transcript JSONL -> sanitized oracle -> replay/related gates`.
4. If the claim is runtime memory, verify `runtime_signal_audit.py` and
   contamination rules.
5. Verify the post-execution chain:
   `signal captured -> proposal generated -> curation path exists -> runtime
   recall/use proven`.
6. If any required proof is absent, downgrade the closeout to the precise stop
   state instead of claiming `PASS`, `CERTIFIED`, or `PASS_CEILING`.

## Required Evidence

For a final TES construction `PASS`/`CERTIFIED` claim, record sanitized evidence:

- safe host command label;
- command fingerprint;
- fresh transcript hash;
- transcript oracle status;
- tool-use count when tool evidence is required;
- same-command replay or justified replay change;
- related TES gates;
- last failure class or `none`;
- post-execution answers;
- runtime-signal audit status when runtime memory is claimed.

Never record raw prompts, raw command output, tool inputs, tool results, raw
transcript lines, secrets, credentials, or project-specific private paths.

## Decisions

- `PASS`: the host-backed harness and post-execution answers support the final
  claim.
- `NEEDS_HOST_TRANSCRIPT_CANARY`: TES construction claim lacks mandatory host
  transcript canary evidence.
- `NEEDS_RUNTIME_SIGNAL_AUDIT`: runtime memory claim lacks runtime signal proof.
- `NEEDS_POST_EXECUTION_GATE`: signal, proposal, curation, recall, or related
  gate proof is missing.
- `LIMITED_NON_HOST_CLAIM`: work is explicitly scoped below host-real/product
  convergence; do not present it as TES construction ceiling proof.

## Script

Use the deterministic helper when a retained JSON evidence packet exists:

```bash
python3 .agents/skills/tes-host-transcript-canary/scripts/post_execution_gate.py \
  --evidence <sanitized-evidence.json> \
  --json-only
```

The helper validates only sanitized fields. It does not read raw transcripts or
replace `host_canary_loop.py`, `runtime_signal_audit.py`, canary admission,
installed certification, Git gates, or package gates.
