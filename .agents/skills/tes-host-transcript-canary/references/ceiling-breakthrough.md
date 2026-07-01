# Ceiling Breakthrough

Use this reference whenever a host-backed canary result looks merely acceptable
but the claim touches TES platform behavior, installed-target evidence, host
contracts, generated surfaces, or a prior false green.

## Core Posture

The harness does not optimize for the floor. Its job is to break through the
ceiling:

```text
floor = minimal pass, plausible transcript, broad confidence
ceiling = host-real replay, red-capable proof, source-owned correction, sharper next failure
```

A floor-green result can be useful as a signal, but it is not convergence when
the canary claim depends on host behavior or product correctness.

## Ceiling Standard

Prefer the strongest local proof that can still be produced surgically:

- same host command replay instead of a similar command;
- fresh transcript hash instead of remembered execution;
- required tool-use evidence instead of transcript presence;
- source-owned patch instead of installed mirror adjustment;
- focused red-capable oracle before broad closure;
- related TES gates agreeing with transcript evidence;
- explicit blocker rather than a weak pass when host truth is not observable.

Ceiling work is not bigger work by default. It is narrower proof, sharper
falsification, and less tolerance for facade evidence.

## Floor-Green Rejection

Do not certify on these floor signals alone:

- transcript exists but is stale;
- a command ran but target attachment is unproven;
- a gate passed without proving host-real execution;
- Field Reports, summaries, or journals imply success without transcript hash;
- broad package gates pass while the reported host failure is unclassified;
- a canary target is patched while package source remains stale.

Classify these as `NEEDS_EVIDENCE`, `FAIL`, or `BLOCKED` with a concrete
blocker. Do not call them `CERTIFIED`.

## Breakthrough Loop

When a floor-green result appears, ask:

1. What exact claim would still be false if this pass is superficial?
2. Which smallest replay or oracle would falsify that claim?
3. Which source surface owns the correction if the claim fails?
4. What evidence would prove the correction through the same host path?

Then run only that next loop. Breakthrough means reaching the next real failure
or a stronger certified proof, not expanding into unrelated governance.

## Closure Bar

Use `CERTIFIED` only when the closeout can show:

- fresh host transcript evidence;
- same-command or justified-command replay;
- no unresolved floor-green weakness;
- source-owned correction when a defect was found;
- related TES gates supporting the same claim;
- no remaining blocker hidden behind confidence language.
