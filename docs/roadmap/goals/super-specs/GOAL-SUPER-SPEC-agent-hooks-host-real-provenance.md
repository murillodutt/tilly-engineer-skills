---
tds_id: roadmap.goal_super_spec_agent_hooks_host_real_provenance
tds_class: roadmap
status: proposed
consumer: maintainers, hook authors, oracle authors, installed-certification authors, canary operators, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: Agent Hooks Host-Real Provenance

Status: proposed execution packet for one isolated window.

Run this SPEC with `tes-host-transcript-canary`. The point of this loop is to
make host-real evidence harder to forge, not to add another narrative gate.

## New-Window Prompt

```text
/goal Execute docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-agent-hooks-host-real-provenance.md with tes-host-transcript-canary. Use a dedicated branch or worktree, prove the current forged-host-real gap first, patch TES source and oracles only, and do not claim PASS_CEILING unless transcript-backed host evidence and related gates agree.
```

## Senior Framing

Protected baseline: hook-health and installed certification currently separate
floor from ceiling and do not let explicit `provenance="fixture"` rows count as
native proof.

Open risk: `record_hook_execution()` still writes `provenance="host-real"`
unconditionally and ceiling logic treats any non-`fixture` row as host-real for
back compatibility. This means the string is too trusted.

Classification: `Platform`. This touches evidence semantics, installed target
certification, host hook trust boundaries, canary claims, and release identity.

## Findings Owned

- H-04: `provenance="host-real"` is minted unconditionally.
- LEDGER-02 residual: ledger append lacks tamper evidence or host/session
  correlation strong enough for ceiling-grade proof.

## Non-Goals

- Do not introduce a remote signer, cloud service, or marketplace dependency.
- Do not break existing installed targets without a clear compatibility state.
- Do not make source fixtures pretend to be host-real.
- Do not treat transcript evidence as a replacement for installed
  certification or hook-health.

## Execution Rules

- Use a dedicated branch or worktree.
- If another spec changes `scripts/tes_install.py`,
  `scripts/installed_certification_oracle.py`, or
  `scripts/attach_health_oracle.py`, rebase and rerun all focused gates.
- Keep compatibility explicit: legacy rows may remain readable, but they must
  not silently authorize new ceiling claims unless backed by fresh host
  evidence.

## SPEC-000: Reproduce Forged Evidence

Create a source-level fixture that writes or seeds a PreToolUse ledger row
without a host transcript and proves current logic counts it too strongly.

Minimum expected red before fix:

- synthetic or manual invocation can produce a row classified as host-real;
- installed certification or hook-health cannot distinguish it from real host
  execution with enough confidence for ceiling semantics.

The fixture must not use private paths or raw transcript content.

## SPEC-001: Provenance Contract

Define explicit provenance states:

- `host-real`: minted only from real host hook entrypoints with host payload
  evidence and a correlatable session.
- `fixture`: deterministic source/self-test evidence.
- `manual` or `unattested`: local manual/script invocation without host proof.
- `legacy-unknown`: old rows without explicit provenance.

Required behavior:

- `record_hook_execution()` accepts provenance or derives a conservative state
  from a narrow host-entrypoint context.
- Self-tests and seeded fixtures must write `fixture`.
- Manual calls that lack host payload proof must not write `host-real`.
- Ceiling code must distinguish `legacy-unknown` from fresh `host-real`.
- A new host-real claim needs transcript-backed evidence or degrades to
  `NEEDS_EVIDENCE` / `PASS_BASIC_WITH_CEILING_GAPS`.

## SPEC-002: Host Correlation

The smallest acceptable local correlation:

- session id from host payload;
- canonical event and agent;
- tool-use id when present;
- sanitized transcript hash from `canary_transcript_oracle.py` or
  `host_canary_loop.py` when making a ceiling claim;
- same-command replay status or justified replay change for host-backed
  claims.

Do not persist raw prompt, raw command output, tool inputs, or raw transcript
  lines.

## SPEC-003: Red-Capable Oracles

Add or update fixtures so these cases are explicit:

- explicit `fixture` row never counts as native host-real;
- `manual` / `unattested` row never authorizes `PASS_CEILING`;
- legacy untagged row is reported separately and cannot silently create a new
  ceiling claim without current host evidence;
- fresh host-backed row plus transcript evidence can support the host-real lane;
- one host's row cannot cross-fill another host.

Required gates:

```bash
python3 scripts/tes_install.py --self-test
python3 scripts/installed_certification_oracle.py --self-test
python3 scripts/attach_health_oracle.py --self-test
python3 scripts/canary_admission_oracle.py --self-test
python3 scripts/canary_transcript_oracle.py --self-test
python3 .agents/skills/tes-host-transcript-canary/scripts/agent_hooks_certification_matrix.py --self-test --repo .
```

## SPEC-004: Host Canary

Run a clean installed target and force a real host hook execution through the
harness. The sanitized report must include:

- safe command label;
- command fingerprint;
- fresh transcript hash;
- event count and required tool-use count;
- ledger row provenance classification;
- installed certification result;
- hook-health result;
- post-execution gate result.

Use `ceiling-replay` only when replay gates are present. Otherwise close as
`SOURCE_CERTIFIED`, `TARGET_CERTIFIED`, or `NEEDS_HOST_TRANSCRIPT_CANARY`.

## SPEC-005: Release Identity And Closeout

Delivered behavior changed. Unless explicitly deferred:

```bash
python3 scripts/tes_bump.py patch --yes --json
python3 scripts/tes_bundle.py publish --adapter all --allow-dirty --gate
python3 scripts/build_public_docs.py
python3 scripts/public_bundle_oracle.py
python3 scripts/validate_reference_package.py
npm run commit:check
```

Acceptance: a synthetic/manual ledger row can no longer satisfy a native
ceiling claim, host-real evidence is transcript-correlated, and the final
claim is downgraded when host truth is absent.
