# CLAUDE.md

Maintainer bootloader for the independent Tilly Engineer Skills package. The governance body below is mirrored verbatim with the root `AGENTS.md` (same XML tags, same rules) so Claude and Codex carry one identical discipline; only this header and `<routing>` differ, by platform. Claude should treat this bootloader as sufficient for ordinary work: local development skills are reference surfaces loaded only when the task explicitly needs them or the owner asks for them.

Distributable agent source lives in `src/**`. People-facing method, eval, and architecture material lives in `docs/**`. Keep this file small.

<core_contract>
```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```
</core_contract>

<instructions> Apply Tilly Engineering Discipline to non-trivial material changes:
1. Think Before Coding — state assumptions, ambiguity, tradeoffs, and blockers before acting; do not pick a risky interpretation silently.
2. Maturity Layer Gate — default material work to `Birth`; promote only with evidence that names the protected baseline, allowed complexity, forbidden complexity, and oracle.
3. Simplicity First — keep the root thin, avoid duplicate source copies, and solve only the requested problem for the selected maturity layer; delete speculative scope before adding it.
4. Surgical Changes — treat `src/**` as adapter source and `docs/**` as governed explanation; touch only request-traceable lines. Classify every `scripts/**` change by consumer (`<scripts_classification>`) before deciding which surfaces move.
5. Goal-Driven Execution — define a falsifiable oracle and run the smallest relevant gate before claiming closure. </instructions>

<success_formula>
```text
E = A * S * C * V
```
Success is zero if assumptions are hidden, scope is inflated, changes are not surgical, or verification is missing. </success_formula>

<runtime_first_product_rule> TES is a product, not a governance archive. Build the smallest durable runtime slice on the intended execution path before adding governance. Smallest means narrow scope, not shallow proof. No governance-only cycles, long SPECs before code, placeholder boundaries, throwaway runtimes, or "minimum viable" closure on adopter-runtime surfaces. Documentation must not become the work; prefer fixtures, oracles, and runtime evidence over parallel explanatory documents. Roadmaps are executive control surfaces — partition or compact at the `validate_doc_size.py` warning threshold before adding status. </runtime_first_product_rule>

<platform_ceiling_classification> The goal is ceiling-grade product behavior, not floor-grade patching. Any work that touches or evaluates hooks, installers, update/uninstall paths, adapter materialization, MCP, Cortex runtime, Field Reports, public bundle identity, host contracts, generated target surfaces, or real installed-target evidence is `Platform` from the first line. PreToolUse work is governed by `docs/architecture/PRETOOLUSE-CONTRACT.md`: do not collapse a floor-green hook audit into `PASS_CEILING`; distinguish `PASS_BASIC`, `PASS_CEILING`, and `NEEDS_DISCOVERABILITY`, and preserve host-specific renderer semantics plus host-payload evidence. Do not classify it as a small local fix because the user says "direct", "sem nova spec", "ajuste fino", "rápido", or "no governance"; those phrases remove document ceremony only, never runtime rigor. For `Platform` work, the minimum acceptable execution is: name the protected installed baseline, preserve host-specific contracts, reproduce or fixture the reported behavior when practical, patch package source instead of installed mirrors, add or update the red-capable oracle, run the focused host/runtime gate, and make a release-identity decision. If host behavior is uncertain, consult official docs or installed/source fixtures before coding. If evidence cannot distinguish bug from host contract, stop as `NEEDS_DISCOVERABILITY` or `NEEDS_OWNER_DECISION`; do not guess and do not collapse to a generic hook contract. </platform_ceiling_classification>

<scripts_classification> Classify every `scripts/**` change by consumer before deciding which surfaces move:
- Maintainer gate (validators, self-tests) → maintainer-only; not delivered.
- Installer, Cortex, MCP, Field Reports, runtime, or adapter script that an adopter receives, invokes, or certifies → delivered behavior (see `<release_identity>`). </scripts_classification>

<code_documentation> Every code file changed or added must carry maintenance documentation either directly or through an associated Markdown reference. Direct documentation means a module docstring, top-level file comment, or narrowly placed inline comment for non-obvious logic; associated documentation means an indexed Markdown surface that names the code path and explains the contract. Do not leave behavior encoded only in code shape, test names, or commit history. The staged code documentation oracle enforces this for local commits. </code_documentation>

<layer_boundary> TES has two repository layers:
- Maintainer/development layer: root bootloaders (`AGENTS.md`, `.claude/CLAUDE.md`), local development skills (`.agents/skills/**`, `.claude/skills/**`), `docs/governance/**`, maintainer gates, and repository-only validation. This layer teaches agents how to develop TES and is not delivered to target projects by default.
- Product/source layer: `src/**` adapter source plus adopter-facing docs, delivered runtime/helper scripts, plugin manifests, public docs, bundles, and generated or installed target surfaces. This layer is the source of truth for behavior adopters receive.

Portable learning belongs in the product/source layer first when it changes delivered TES behavior. Update the maintainer/development layer only when the local development workflow changes or a bootloader mirror must stay aligned. Do not certify product behavior by running installed-target checks against this repository root; use source/package oracles here and installed-target oracles only against a real target-project fixture. For correlated file decisions, apply `docs/governance/MAINTAINER-CORRELATION-RULE.md`. </layer_boundary>

<regression_guard> Use regression thinking inline for changes that can affect certified, installed, materialized, generated, measured, release, CLI, public, or user-visible behavior. Do not load a regression skill by default, and honor an explicit no-skill run unless a concrete destructive, secret, remote, release, or safety risk must be escalated. Before risky behavior changes, name the last-known-good baseline, classify whether the change preserves, extends, or replaces it, list protected invariants, and run the comparison matching the surface that can regress. On `Platform` surfaces, "focused" means the smallest red-capable host/runtime comparison, not build-only proof and not config-only proof. For low-risk local analysis or ordinary edits, keep this as a short mental check and move. Avoid narrow literal lists in runtime code unless they are governed data, schema, or contract backed — example-specific fixes are regression seeds. </regression_guard>

<mantra_gate> The Mantra Gate is your continuous senior manager, not a pointwise checkpoint: it watches the whole task for you, deriving obligations from the active contracts (ADR/PRD/SPEC) and the protected baseline, and stays alert across ordinary work where drift is born. When in doubt it pulls you toward the right move before you act — forcing a lens, maturity acquisition (upstream/docs/related code) before coding, reuse over new code, and package-fix over local workaround — and it supervises by injecting that obligation as context, never by deciding for you. Two bands, by risk: (1) PROACTIVE SUPERVISION — for ordinary local edits, focused oracles, staging, and local commits, do not block on gate artifacts, markers, or skill loading; advise inline only when doubt or drift is real, and stay silent otherwise (anti-cry-wolf). (2) HARD GATE — for destructive, remote, release, sync, secret-bearing, or high-impact state changes, and for closure claims that depend on those actions, require `VERIFY`, `SCOPE`, `BEST_PATH`, `DOCUMENT`, `ORACLE`, `RESOLVE`, `STATUS`. Host hooks are projections of this contract: they may inject supervision context and must use their host-specific block semantics, not one flattened output protocol. Report gate detail only on `BLOCKED`/`NEEDS_REVIEW`, when approval is needed, or when asked. Treat `BYPASS_SUSPECTED`, `NEEDS_REVIEW`, or `BLOCKED` as a stop condition only for the risky action whose gate failed. The compact marker is a discreet signal, not a human command surface. </mantra_gate>

<diamond_build_test_fail_fix> For critical capabilities, build from the finished contract down: final behavior, adversarial fixture, observed failure, smallest repair, green gate. Do not call certified behavior experimental; use `blocked`, `degraded`, `not available`, `certified`, or `fail`. </diamond_build_test_fail_fix>

<feedback_voice> Default to SHORT answers: the fewest lines that answer the question — often one line. Short chat is an output discipline, not an engineering downgrade: it must never lower maturity classification, skip Platform proof, or turn runtime evidence into a recommendation-only closeout. State the conclusion and stop. Do not pad with restated reasoning, alternatives you won't take, hedging caveats, file:line citations, or "want me to…" follow-ups unless the user asks. (Stating a load-bearing assumption, blocker, or the oracle you verified is not padding — that stays, in one line.) No tables, bullet dumps, code blocks, or inventories by default; use them only on explicit request or when the artifact needs exact syntax (a command, a routing table, a roadmap partition). This is a hard rule, not a preference — deep, exhaustive prose has a real token cost the user is paying to avoid. Be terse in reporting; do not be shallow in execution. </feedback_voice>

<learning_and_boundaries> Real project executions are learning loops: after each TES update cycle, use at least one canary to expose drift, false greens, stale helpers, and adapter gaps. When a canary reports `NEEDS_REVIEW`/`DEGRADED`/`BLOCKED` or meaningful drift, treat it as TES product evidence, classify it, patch TES source/oracle/docs, and certify in the `~/Dev/tes-canaries` workspace before re-running the original canary. Repeat on two more real projects before any commercial-use claim. Installed targets and canary clones are evidence targets, not the source of truth. Portable findings get patched in the package source here (`src/**`, `scripts/**`, `docs/**`) — not only in installed mirrors (`.agents/skills/**`, `.claude/skills/**`, `plugins/tilly-engineer-skills/**`). Do not promote a project-specific workaround; only portable learning that survives canary replay and maintainer gates. </learning_and_boundaries>

<confidentiality> Use neutral placeholder vocabulary only (`target-project`, `canary-project`, `<project-A>`, `<storage-backend>`, …); no real project, product, internal-service names, storage backends, archive formats, or `~/Dev/<name>` paths in tracked content. The project's own infrastructure names (e.g. `~/Dev/tes-canaries`) are allowed. `scripts/private_vocabulary_oracle.py` scans staged text surfaces on the default `npm run commit:check` gate and the full tracked tree on explicit `npm run commit:closure` against `.tes/private-vocabulary.txt` (gitignored). When in doubt, prefer the placeholder. </confidentiality>

<maintainer_boundary> This file governs agents working on the Tilly Engineer Skills package itself; it is not an installed target-project rule. Before closing a material package change, use `docs/governance/MAINTAINER-CORRELATION-RULE.md` to check correlated files, and classify `scripts/**` by consumer before deciding which surfaces move. Keep maintainer-only rules here or in `docs/governance/**`; do not copy them into `src/adapters/**`, target bootloaders, user manuals, or `docs/agents/**` unless the delivered Tilly behavior intentionally changed. </maintainer_boundary>

<release_identity> Delivered behavior changes require a release-identity decision before closure. If a change adds, removes, or changes adopter-visible skills, triggers, installer behavior, helper/runtime scripts, plugin metadata, public docs, MCP, Field Reports, Cortex behavior, or adapter materialization, decide whether the package version and public bundle must advance. Default rule: bump the patch version and update correlated release surfaces (`package.json`, script `VERSION` constants, plugin manifests, `docs/dist/<version>/**`, `.sha256` sidecars, `index.json`, public docs, validators, the maintainer correlation rule). After an authorized release tag is pushed, run `npm run release:check`. Exception: if Murillo explicitly keeps the current version for a delivered change, state that exception in the closeout and do not call the package sealed by version identity. </release_identity>

<operating_discipline> Operating calibration (maintainer/dev memory only; never Cortex, never `src/**`, never delivered):
- Commit locally by default; stop there until the owner explicitly asks to sync/push. "push it" is not a standing grant — each push needs its own request.
- Smart pre-commit, scoped to what changed: run only the focused oracles relevant to the modified files; reserve `npm run commit:closure` for release/sync or explicit seal claims.
- The `/goal` Stop hook is a guardrail, not a throttle: alignment pressure, not deadline pressure. For large-surface changes, close each increment green before advancing.
- User instructions can narrow local development aids: if the owner says no skills or no governance expansion, keep execution bootloader-first unless destructive, remote, secret, release, or safety risk requires escalation. </operating_discipline>

<routing>
| Need | Source |
|------|--------|
| Maintainer governance authority | `AGENTS.md` (identical governance body) |
| Project map | `docs/INDEX.md` |
| Repository structure | `docs/architecture/PROJECT-STRUCTURE.md` |
| PreToolUse ceiling contract | `docs/architecture/PRETOOLUSE-CONTRACT.md` |
| Maintainer correlation rule | `docs/governance/MAINTAINER-CORRELATION-RULE.md` |
| Cross-tool governance | `docs/governance/AGENTIC-ALIGNMENT-GOVERNANCE.md` |
| Tool-neutral principles | `docs/mesh/PRINCIPLES.md` |
| Claude instruction source | `src/adapters/claude/CLAUDE.md` |
| Package validation | `python3 scripts/validate_reference_package.py` |
| TDS validation | `python3 scripts/validate_tds.py` |
| Default commit gate | `npm run commit:check` |
| Full closure gate | `npm run commit:closure` |
</routing>

<locks>
- Do not put full source packages back in the repository root, or duplicate adapter source between `src/**` and hidden root tool folders.
- Do not claim the package is sealed without `npm run commit:closure`.
- No remote, push, publish, cloud, or marketplace actions without an explicit per-request private decision.
- Keep TES generic: private project/product/internal-service names, storage backends, archive formats, and filesystem paths stay out of tracked content (see `<confidentiality>`). </locks>
