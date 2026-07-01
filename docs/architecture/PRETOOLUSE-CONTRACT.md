---
tds_id: architecture.pretooluse_contract
tds_class: architecture
status: active
consumer: maintainers, hook authors, installer authors, oracle authors, and hook auditors
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# PreToolUse Contract

PreToolUse is the host-real projection of the Mantra Gate before a tool executes. This contract is the canonical source for PreToolUse behavior; implementation notes, installer docs, and audit prompts must point here instead of defining competing contracts.

## Boundary

PreToolUse is an internal TES subsystem, not an external package. Its runtime path is:

```text
host hook config
-> thin host adapter
-> host-neutral PreToolUse decision kernel
-> session/repetition coordinator
-> host-specific output renderer
-> runtime ledger writer
```

The decision kernel owns only normalized event/tool/payload/session input, path and command extraction, governed-surface detection, forbidden-classification input, and the host-neutral decision record. The session coordinator owns only anti-cry-wolf state. Host renderers, hook installation, Cortex advisory context, Field Reports, sync, release, postinstall advisories, and ledger writes stay outside the kernel.

## Floor Contract

The floor contract is operational correctness. A host reaches `PASS_BASIC` only when it proves all of these with installed-target evidence:

- routine silence: routine reads, diagnostics, and non-governed work allow without marker noise;
- governed supervision: mutations on governed surfaces supervise and surface the marker on every visible Mantra Gate application;
- forbidden block: forbidden actions block before execution with host-specific semantics;
- anti-cry-wolf: repeated same-session governed supervision may record repetition state, but must not suppress the `🍳 Flash-Fry` marker when the Mantra Gate applies;
- runtime evidence: the ledger records agent, event, tool, session, path or command, decision, risk, marker state, and enough host context to audit the result;
- host output contract: Claude Code and Codex render their exit-2/stderr contracts; Cursor renders JSON allow/deny with exit 0;
- no-write advisory boundary: Cortex context may propose recall, capture, or alignment but must not perform automatic durable writes.

`PASS_BASIC` is necessary but no longer sufficient for ceiling claims.

## Ceiling Contract

PreToolUse reaches `PASS_CEILING` only when it proves the floor contract and adds these higher-grade guarantees:

- decision reason codes: every decision records at least one stable reason code. Canonical codes are `routine_non_mutating`, `routine_non_governed`, `governed_surface_mutation`, `forbidden_class`, `anti_crywolf_repeated_context`, historical `anti_crywolf_suppressed`, `host_payload_labeling`, `patch_body_path_extracted`, `shell_command_path_extracted`, `needs_discoverability_unknown_mutation`, `renderer_contract_projected`, and `cortex_advisory_no_write`;
- classifier trace: material and forbidden outcomes name the evidence used, including path, command fragment category, payload field source, shell mutation category when present, and renderer path, without leaking secrets, raw shell commands, or file content;
- host payload evidence: audits distinguish host payload labeling from TES classification, especially Cursor cases where a native UI action may arrive as `tool: "Write"`;
- patch-body evidence: Codex `apply_patch` path extraction treats `tool_input.command` as canonical and accepts defensive aliases `input`, `patch`, flat string `arguments`, and `arguments.command`/`arguments.input`/`arguments.patch`;
- discoverability gate: observed or exposed host tool names that look mutating must not be silently classified as routine; ambiguous host semantics produce `NEEDS_DISCOVERABILITY` until fixture or native evidence resolves them;
- renderer parity: host-specific renderers are certified by fixtures that prove Claude Code, Codex, and Cursor contracts without flattening them into one protocol;
- ledger analytics contract: current v2 PreToolUse rows carry a non-empty invocation, using a stable synthetic invocation when a host or simulation payload omits a tool id; external dedup and analytics use tool, risk, path or redacted path class/hash, command category, session/mode, and marker state, not only invocation plus timestamp; historical anti-cry-wolf renderer transitions from first marker to silent repeat are compatibility evidence, while current rows should repeat the marker and record `anti_crywolf_repeated_context` when the same governed context repeats;
- current-host provenance: per-host native audits expose `ceiling_evidence_scope.claim_scope=current_host`, `ceiling_evidence_scope.current_host=<host>`, and required host evidence limited to that host;
- drift detection: the next audit can identify whether a regression came from host payload shape, kernel classification, session suppression, renderer output, or ledger write;
- red-capable oracle coverage: the source package has an oracle that fails when the canonical contract loses the floor/ceiling distinction, reason-code requirement, discoverability gate, or host-payload evidence rule.

If a run proves the floor but not these ceiling guarantees, report `PASS_BASIC` plus ceiling gaps. Do not call it `PASS_CEILING`.

## Current Runtime Slice

The source runtime now implements the ceiling substrate: every kernel decision
carries stable `reason_codes`, unknown mutating-looking tools on governed paths
return `NEEDS_DISCOVERABILITY` instead of routine allow, host renderers preserve
their native contracts, and hook-health separates floor from ceiling evidence.
`PASS_CEILING` still requires installed per-host runtime evidence; source
capability alone is not enough.

## No New Filter Split Today

The current runtime does not need additional PreToolUse filter layers for
anti-cry-wolf, discoverability, or renderer parity. They are already distinct
decision dimensions in the existing path:

```text
payload/path extraction
-> classifier decision
-> session repetition tracking
-> host renderer projection
-> ledger/health interpretation
```

Anti-cry-wolf is a session-repetition dimension, not a second classifier. Its
job is to track repeated governed session/context evidence without suppressing
the `🍳 Flash-Fry` marker. Current rows preserve `risk=material`,
`outcome=supervise`, `governed_surface_mutation`, and marker visibility on every
visible Mantra Gate application; repeated context adds
`anti_crywolf_repeated_context`. Historical duplicate rows, replay residue,
Cursor batch projections, and older first-marker to silent-repeat renderer
transitions are ledger-health noise unless current `pretooluse_decision@2`
rows contradict decision, risk, redaction, or marker state outside that
compatibility path. Adding a separate anti-cry-wolf filter now would duplicate
the session coordinator and increase the chance that repetition state hides
classification evidence.

Discoverability is an honest unknown-state dimension, not a new block policy.
When a tool name, payload shape, or host semantic looks mutating but lacks
fixture or native evidence, the correct result is `NEEDS_DISCOVERABILITY` with
`outcome=needs_discoverability`, `risk=needs-discoverability`, and
`needs_discoverability_unknown_mutation`. It must not be downgraded to routine
silence, and it must not become a generic hard block. Adding a separate
discoverability filter now would create another classification surface before a
new host/tool contract actually exists.

Renderer parity and alias handling are projection and extraction obligations,
not independent filters. The kernel records a host-neutral decision; Claude
Code, Codex, and Cursor render that decision through different native output
contracts. Codex patch-body aliases are accepted as payload/path extraction
evidence; Cursor host payload labeling is treated as host evidence when the TES
classification remains material. Adding a renderer-parity filter now would risk
flattening host protocols or letting one host's evidence prove another host's
native behavior.

The next implementation must stay in the existing path unless evidence shows a
real second consumer or contradiction that cannot be represented by the current
record: a host-native payload shape that cannot be expressed through
`classifier_trace`, a renderer output that cannot be represented through
`renderer_trace`, a repetition state that cannot be represented through
`anti_crywolf_repeated_context`, or a discoverability case that cannot be
represented through `NEEDS_DISCOVERABILITY`. Without that evidence, the right action is to
document, test, and canary the current dimensions, not add new filters.

## Status Vocabulary

- `PASS_BASIC`: the current installed host satisfies the floor contract.
- `PASS_CEILING`: the current installed host satisfies both floor and ceiling contracts.
- `NEEDS_DISCOVERABILITY`: the hook is safe, but host payload semantics or a new tool name cannot yet be classified with evidence.
- `NEEDS_REVIEW`: evidence is internally inconsistent or the audit cannot distinguish host behavior from TES behavior.
- `FAIL`: the installed contract is contradicted by evidence, a forbidden command executes, current-host native PreToolUse is missing, or a governed mutation is classified as routine without a documented host-payload explanation.

## Non-Goals

Ceiling does not mean moving installer logic into the kernel, adding a standalone PreToolUse package, adding broad host guesses without evidence, or increasing marker noise. The ceiling is better diagnosis, stronger evidence, and safer drift detection on the same small runtime path.
