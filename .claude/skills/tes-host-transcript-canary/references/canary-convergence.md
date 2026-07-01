# Canary Convergence

Use this reference before declaring that a host-backed canary loop converged.

## Convergence Formula

Canary convergence requires agreement across three evidence classes:

```text
host-real transcript evidence
+ source-owned correction
+ related TES gates
= canary decision
```

Transcript evidence strengthens the claim but never replaces the primary gate
for the surface under test.

## Decision Matrix

- `PASS`: transcript exists, parses, is fresh for the replay, and satisfies the
  required host/tool-use evidence. Continue to related TES gates.
- `NEEDS_EVIDENCE`: host evidence is absent, stale, insufficient, or not
  connected to the correction. Replay or collect the missing evidence.
- `FAIL`: host command failed, transcript is malformed, or the oracle emitted
  non-parseable output. Classify before patching.
- `BLOCKED`: same blocker repeated three times, the next action needs owner
  authority, or the host truth is not locally observable.
- `CERTIFIED`: original host command replay, transcript oracle, canary
  admission, installed certification, Git gate, package gate, or other related
  TES gate all support the same claim.

## Related Gates

Choose the smallest related gate that can falsify the claim:

- Git hook or admission behavior: `git_gate_contract.py`,
  `canary_admission_oracle.py`, or the focused hook fixture.
- Installed target behavior: `installed_certification_oracle.py` against a real
  target fixture.
- Transcript evidence behavior: `canary_transcript_oracle.py` and
  `host_canary_loop.py`.
- Package source behavior: focused source oracle, then `npm run commit:check`.
- Public bundle identity: package validation and bundle checks only when a
  delivered behavior change is intentionally being sealed.

## Loop Closeout

A closeout may claim `CERTIFIED` only when it names:

- safe host command label or reason no command ran;
- command fingerprint;
- transcript hash;
- loop count;
- last failure class;
- correction commit when applicable;
- replay status;
- related gates;
- remaining blocker or no blocker.

If any of those fields are unavailable, use `NEEDS_EVIDENCE` or `BLOCKED`
instead of `CERTIFIED`.

## Ledger Discipline

The local ledger is continuity evidence, not a source of product truth. Use it
to reconstruct loop state across windows, then promote only portable findings
into package source, source oracles, docs, or this skill.
