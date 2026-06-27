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
-> session/suppression coordinator
-> host-specific output renderer
-> runtime ledger writer
```

The decision kernel owns only normalized event/tool/payload/session input, path and command extraction, governed-surface detection, forbidden-classification input, and the host-neutral decision record. The session coordinator owns only anti-cry-wolf state. Host renderers, hook installation, Cortex advisory context, Field Reports, sync, release, postinstall advisories, and ledger writes stay outside the kernel.

## Floor Contract

The floor contract is operational correctness. A host reaches `PASS_BASIC` only when it proves all of these with installed-target evidence:

- routine silence: routine reads, diagnostics, and non-governed work allow without marker noise;
- governed supervision: mutations on governed surfaces supervise and surface the marker once per session/context;
- forbidden block: forbidden actions block before execution with host-specific semantics;
- anti-cry-wolf: repeated same-session governed supervision suppresses only the repeated marker, never the governed classification;
- runtime evidence: the ledger records agent, event, tool, session, path or command, decision, risk, marker state, and enough host context to audit the result;
- host output contract: Claude Code and Codex render their exit-2/stderr contracts; Cursor renders JSON allow/deny with exit 0;
- no-write advisory boundary: Cortex context may propose recall, capture, or alignment but must not perform automatic durable writes.

`PASS_BASIC` is necessary but no longer sufficient for ceiling claims.

## Ceiling Contract

PreToolUse reaches `PASS_CEILING` only when it proves the floor contract and adds these higher-grade guarantees:

- decision reason codes: every decision records at least one stable reason code. Canonical codes are `routine_non_mutating`, `routine_non_governed`, `governed_surface_mutation`, `forbidden_class`, `anti_crywolf_suppressed`, `host_payload_labeling`, `patch_body_path_extracted`, `needs_discoverability_unknown_mutation`, `renderer_contract_projected`, and `cortex_advisory_no_write`;
- classifier trace: material and forbidden outcomes name the evidence used, including path, command fragment category, payload field source, and renderer path, without leaking secrets or file content;
- host payload evidence: audits distinguish host payload labeling from TES classification, especially Cursor cases where a native UI action may arrive as `tool: "Write"`;
- discoverability gate: observed or exposed host tool names that look mutating must not be silently classified as routine; ambiguous host semantics produce `NEEDS_DISCOVERABILITY` until fixture or native evidence resolves them;
- renderer parity: host-specific renderers are certified by fixtures that prove Claude Code, Codex, and Cursor contracts without flattening them into one protocol;
- ledger analytics contract: external dedup and analytics use tool, risk, path or command, session/mode, and marker state, not only invocation plus timestamp;
- drift detection: the next audit can identify whether a regression came from host payload shape, kernel classification, session suppression, renderer output, or ledger write;
- red-capable oracle coverage: the source package has an oracle that fails when the canonical contract loses the floor/ceiling distinction, reason-code requirement, discoverability gate, or host-payload evidence rule.

If a run proves the floor but not these ceiling guarantees, report `PASS_BASIC` plus ceiling gaps. Do not call it `PASS_CEILING`.

## Status Vocabulary

- `PASS_BASIC`: the current installed host satisfies the floor contract.
- `PASS_CEILING`: the current installed host satisfies both floor and ceiling contracts.
- `NEEDS_DISCOVERABILITY`: the hook is safe, but host payload semantics or a new tool name cannot yet be classified with evidence.
- `NEEDS_REVIEW`: evidence is internally inconsistent or the audit cannot distinguish host behavior from TES behavior.
- `FAIL`: the installed contract is contradicted by evidence, a forbidden command executes, current-host native PreToolUse is missing, or a governed mutation is classified as routine without a documented host-payload explanation.

## Non-Goals

Ceiling does not mean moving installer logic into the kernel, adding a standalone PreToolUse package, adding broad host guesses without evidence, or increasing marker noise. The ceiling is better diagnosis, stronger evidence, and safer drift detection on the same small runtime path.
