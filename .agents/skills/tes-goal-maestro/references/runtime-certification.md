# Runtime Certification

Use this reference when a tree, prompt, `ACTIVE_SPEC`, or closeout needs proof
that a runtime, browser, UI, game, canvas, WebGL/WebGPU, Three.js, or integration
wiring path actually works.

## Core Rule

```text
Required runtime axes must pass; `DEGRADED` is evidence of a blocked axis, not
completion.
```

## Browser And Visual Certification

When `browser_metrics_required=yes` or `visual_spatial_oracle_required=yes`,
the tree must include a dedicated visual/runtime certification unit such as
`SPEC-VISUAL-CERT` or an equivalent source-declared unit. This unit cannot be
merged into a build-only integration unit.

The visual certification unit must:

1. start a real browser worker or equivalent browser automation;
2. navigate the built or served app when applicable;
3. capture at least one screenshot, pixel, canvas, bounding-box, accessibility
   tree, or rendered evidence artifact;
4. emit a stable `browser-metrics.json`;
5. record console/runtime failures;
6. return `PASS` only when the required axis is proven.

Minimum `browser-metrics.json` fields:

```json
{
  "status": "PASS|DEGRADED|BLOCKED",
  "consoleErrors": [],
  "runtime": {},
  "visual": {
    "proven": true,
    "evidence": []
  },
  "domainMetrics": {},
  "failures": []
}
```

For a required visual axis, `EXECUTION_LOOP_COMPLETE` requires
`status=PASS`, `visual.proven=true`, and at least one evidence path. A
`DEGRADED` or `BLOCKED` artifact routes to `AXIS_UNPROVEN` or
`VISUAL_CERT_BLOCKED`, not completion.

## Browser Attempt Escape Hatch

Non-visual certification is valid only after a real browser attempt fails for a
captured environment reason such as missing browser binary, sandbox denial, no
display, no GPU, or unsupported runtime. The ledger must include:

```text
browser_attempt=<tool_invoked|not_attempted|not_applicable>
visual_evidence=<screenshot_paths|degraded_with_proof|none>
browser_failure_log=<command output or not_applicable>
```

If the axis is required and `browser_attempt=not_attempted`, stop with
`VISUAL_CERT_BLOCKED`. Do not use source text to waive visual evidence unless
the anchor explicitly declares the phase non-visual before tree generation.

## Integration Runtime-Smoke Oracle

When a unit has `unit_role=integration`, `runtime-wiring`, `game-loop`,
`adapter-wiring`, or equivalent source-declared responsibility, build and
typecheck are necessary but not sufficient.

The unit must carry:

```text
unit_role=integration
runtime_smoke_oracle=<command or artifact>
oracle_class=behavioral
```

The runtime smoke must instantiate the real wiring module, use stubs only for
external browser/GPU/network/clock boundaries, run deterministic ticks or calls,
and assert invariants that the compiler cannot prove:

1. state advances across ticks or calls;
2. no throw, NaN, unresolved promise, or fatal console/runtime error appears on
   the hot path;
3. at least one cross-module interaction produces its declared effect.

If the tree gives an integration unit only build/typecheck, stop with
`NEEDS_INTEGRATION_ORACLE`.

## Visual-Runtime Senior

Use this role when browser, UI, game, canvas, render, layout, spawn, raycast, or
runtime-wiring evidence is required.

Ownership:
- browser/runtime smoke scripts, screenshots, `browser-metrics.json`, and
  runtime evidence artifacts.

Forbidden:
- replacing runtime proof with build-only, typecheck-only, or prose evidence.

Oracles:
- browser metrics parse;
- screenshot/pixel/bounding-box/accessibility evidence;
- runtime smoke artifact for integration units.

## Done

Runtime certification is done when every required runtime or visual axis has
PASS evidence, every integration unit has a behavioral smoke, and blocked
environments are proven by captured attempt logs rather than assumed.
