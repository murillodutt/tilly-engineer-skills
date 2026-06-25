# Execution Context Handoff

Use this reference when `--execute-loop` will send fresh workers into a real codebase. It owns the transfer of exact source facts from the parent to each worker.

## Core Rule

```text
Workers need source-derived facts, not parent memory.
```

The parent must not summarize reused APIs from memory when the repository can provide exact symbols, paths, commands, and environment facts.

## Contract Handoff Artifact

After each material SPEC commit and before the next worker spawn, produce or refresh a compact handoff artifact from the real source. The artifact may be a checked prompt block, a temporary ledger section, or a generated file when the run explicitly allows it.

Minimum fields:

```text
contract_handoff_artifact=<path|ledger-section|prompt-block>
runtime_target=<node|browser|isomorphic>
symbol_index_source=<tsc-declarations|ts-morph|grep|manual-source-read>
symbols=<export name, exact signature, import path>
reused_source_files=<paths and attached snippets or none>
oracle_runner_contract=<canonical commands and fallback commands>
environment_notes=<known local runtime/tooling facts>
api_lint_status=<PASS|FAIL|not_applicable>
```

`runtime_target` is mandatory and propagated to the worker as `RUNTIME_TARGET`. Typecheck and build are blind to it — a browser-bound module that imports `node:fs` compiles and bundles, then breaks only in the browser. The envelope must carry the target so the parent can guard it before the commit, not after.

For TypeScript projects, prefer declaration output or a syntax-aware extractor when available. A grep/manual digest is acceptable only when the parent records the exact files read and the worker receives the resulting signatures literally.

## Envelope API Lint

Before spawning a worker, validate every symbol, type, count, and command that the envelope states as fact. If the envelope says a module exports a function, field, union member, oracle count, or runner command, it must be confirmed against the repository or marked unknown.

If a stated source fact cannot be validated, stop with `NEEDS_TREE_REPAIR` or repair the handoff before worker spawn. Do not make the worker discover that the parent envelope was wrong by failing typecheck.

`api_lint_status=PASS` is a self-declared enum and carries no weight alone — the agent that wanted PASS wrote PASS, the same hole as a facade oracle. Accept `PASS` only with `api_lint_evidence=<commands run + literal output + paths/hash>` that a reader can re-run. Parent Validation rejects `PASS` without re-runnable evidence, and the independent reviewer re-executes that evidence in the `Executive Stop Audit`; if it does not reproduce, stop with `NEEDS_TREE_REPAIR`.

## Reuse Source Attachment

For the two to four load-bearing modules a worker must reuse, attach exact source snippets, signatures, or the full file when context size allows. The worker may still inspect files, but it should not need exploratory reads to learn the API surface named by the envelope.

## External API Research Budget

When an active SPEC touches a recently changed or version-sensitive external API, the envelope must include:

```text
research_budget=<required|not_applicable>
official_source=<Context7 library id, official docs, installed .d.ts, or source>
local_cross_check=<node_modules grep, typecheck, runtime probe, or none>
```

For library/framework/API questions, use official docs or Context7 plus a local cross-check when the installed package is available. Do not rely on memory for volatile APIs.

## Canonical Node Oracle Block

This block applies only when `runtime_target=node`. For `runtime_target=browser`, do not hand the worker a Node oracle shape — that is the path that smuggles `node:fs`/`path`/`os` into a browser bundle. Use the browser runtime-smoke from `references/runtime-certification.md` instead.

For Node-headless project oracles, the parent should provide a stable block instead of making each worker rediscover command shape:

1. assertion name -> file -> signature map;
2. canonical command and fallback command;
3. runner location rules, such as writing temporary runners at repo root;
4. module format rules, such as `.mts` plus async IIFE when needed;
5. bootstrap helpers and constants required by inherited oracles;
6. environment notes such as absent macOS coreutils;
7. cleanup and formatting expectations for generated artifacts.

## Done

"Done" is completeness per axis, not mere presence of symbols. Before the Worker Packet is emitted, for **every** anchor-traceable axis of the PRD/ADR the packet must carry: `runtime_target` resolved (B1), an `oracle_runner_contract` with a regression target (D3), and — for axes under isolation (ADR-010) — the `forbidden-write` (e.g. `/docs/**`) and `forbidden-import` (e.g. another `benchmark-*/`) constraints. A packet that "contains symbols" but leaves an axis without these is incomplete: the skill's own job is to promote direction AND context, and a holed envelope is what lets a worker trip outside its span (the node-in-browser bug was an envelope with no runtime target). Any axis missing a required field → stop with `NEEDS_CONTEXT`; the packet is **not** emitted. Drive the per-axis check with `scripts/context-completeness.mjs`.

Beyond that, the handoff also requires source-derived symbols, validated commands, external API research instructions when needed, and enough oracle context that the next worker is not forced into broad exploratory reads before it can start the active SPEC.
