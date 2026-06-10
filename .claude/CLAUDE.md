# CLAUDE.md

Maintainer bootloader for the independent Tilly Engineer Skills package. The governance body below is mirrored verbatim with the root `AGENTS.md` (same XML tags, same rules) so Claude and Codex carry one identical discipline; only this header and `<routing>` differ, by platform. Detailed workflows live in `.claude/skills/tes-*` and `docs/governance/**`.

Distributable agent source lives in `src/**`. People-facing method, eval, and architecture material lives in `docs/**`. Keep this file small.

<core_contract>
```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```
</core_contract>

<instructions>
Apply Tilly Engineering Discipline to non-trivial material changes:
1. Think Before Coding — state assumptions, ambiguity, tradeoffs, and blockers before acting; do not pick a risky interpretation silently.
2. Maturity Layer Gate — default material work to `Birth`; promote only with evidence that names the protected baseline, allowed complexity, forbidden complexity, and oracle.
3. Simplicity First — keep the root thin, avoid duplicate source copies, and solve only the requested problem for the selected maturity layer; delete speculative scope before adding it.
4. Surgical Changes — treat `src/**` as adapter source and `docs/**` as governed explanation; touch only request-traceable lines. Classify every `scripts/**` change by consumer (`<scripts_classification>`) before deciding which surfaces move.
5. Goal-Driven Execution — define a falsifiable oracle and run the smallest relevant gate before claiming closure.
</instructions>

<success_formula>
```text
E = A * S * C * V
```
Success is zero if assumptions are hidden, scope is inflated, changes are not surgical, or verification is missing.
</success_formula>

<runtime_first_product_rule>
TES is a product, not a governance archive. Build the smallest durable runtime slice on the intended execution path before adding governance. No governance-only cycles, long SPECs before code, placeholder boundaries, or throwaway runtimes. Documentation must not become the work; prefer fixtures, oracles, and runtime evidence over parallel explanatory documents. Roadmaps are executive control surfaces — partition or compact at the `validate_doc_size.py` warning threshold before adding status.
</runtime_first_product_rule>

<scripts_classification>
Classify every `scripts/**` change by consumer before deciding which surfaces move:
- Maintainer gate (validators, self-tests) → maintainer-only; not delivered.
- Installer, Cortex, MCP, Field Reports, runtime, or adapter script that an adopter receives, invokes, or certifies → delivered behavior (see `<release_identity>`).
</scripts_classification>

<regression_guard>
For every package analysis, write, runtime change, oracle change, commit, or closeout, self-consume `.agents/skills/tes-regression-guard/SKILL.md` as an always-on local reasoning kernel — not a user-invoked skill. Before changing behavior that already has certified, installed, materialized, generated, or measured evidence, name the last-known-good baseline, classify whether the change preserves, extends, or replaces it, and list protected invariants first.
Regression is project-wide, not Python-specific: protect skills, triggers, adapters, materialized outputs, installers, runtime scripts, docs, roadmaps, oracles, generated public pages, version identity, release surfaces, private vocabulary, safety behavior, and UX claims. A passing source check is not enough when the risk lives in an installed, generated, materialized, public, or CLI surface; run the comparison matching the surface that can regress. Avoid narrow literal lists in runtime code unless they are governed data, schema, or contract backed — example-specific fixes are regression seeds.
</regression_guard>

<mantra_gate>
Before state-changing actions, use the TES Mantra Gate. When it permits proceeding, show only `[🍳 Flash-Fry]`; the full gate still records `VERIFY`, `SCOPE`, `BEST_PATH`, `DOCUMENT`, `ORACLE`, `RESOLVE`, and `STATUS` in the evidence surface. Report gate detail only on `BLOCKED`/`NEEDS_REVIEW`, when approval is needed, or when asked. For closure, commit, or push claims, use the Mantra Gate adoption oracle when available; treat `BYPASS_SUSPECTED`, `NEEDS_REVIEW`, or `BLOCKED` as a stop condition until the gate record, scope, risk, and closure oracle are repaired.
</mantra_gate>

<diamond_build_test_fail_fix>
For critical capabilities, build from the finished contract down: final behavior, adversarial fixture, observed failure, smallest repair, green gate. Do not call certified behavior experimental; use `blocked`, `degraded`, `not available`, `certified`, or `fail`.
</diamond_build_test_fail_fix>

<feedback_voice>
Default to SHORT answers: the fewest lines that answer the question — often one line. State the conclusion and stop. Do not pad with restated reasoning, alternatives you won't take, hedging caveats, file:line citations, or "want me to…" follow-ups unless the user asks. (Stating a load-bearing assumption, blocker, or the oracle you verified is not padding — that stays, in one line.) No tables, bullet dumps, code blocks, or inventories by default; use them only on explicit request or when the artifact needs exact syntax (a command, a routing table, a roadmap partition). This is a hard rule, not a preference — deep, exhaustive prose has a real token cost the user is paying to avoid. Be terse until the user explicitly asks for depth or detail. When unsure how deep to go, go shallow.
</feedback_voice>

<learning_and_boundaries>
Real project executions are learning loops: after each TES update cycle, use at least one canary to expose drift, false greens, stale helpers, and adapter gaps. When a canary reports `NEEDS_REVIEW`/`DEGRADED`/`BLOCKED` or meaningful drift, treat it as TES product evidence, classify it, patch TES source/oracle/docs, and certify in the `~/Dev/tes-canaries` workspace before re-running the original canary. Repeat on two more real projects before any commercial-use claim.
Installed targets and canary clones are evidence targets, not the source of truth. Portable findings get patched in the package source here (`src/**`, `scripts/**`, `docs/**`) — not only in installed mirrors (`.agents/skills/**`, `.claude/skills/**`, `plugins/tilly-engineer-skills/**`). Do not promote a project-specific workaround; only portable learning that survives canary replay and maintainer gates.
</learning_and_boundaries>

<confidentiality>
Use neutral placeholder vocabulary only (`target-project`, `canary-project`, `<project-A>`, `<storage-backend>`, …); no real project, product, internal-service names, storage backends, archive formats, or `~/Dev/<name>` paths in tracked content. The project's own infrastructure names (e.g. `~/Dev/tes-canaries`) are allowed. `scripts/private_vocabulary_oracle.py` runs on every `npm run commit:check` against `.tes/private-vocabulary.txt` (gitignored) and fails the gate if any listed name appears in tracked content. When in doubt, prefer the placeholder.
</confidentiality>

<maintainer_boundary>
This file governs agents working on the Tilly Engineer Skills package itself; it is not an installed target-project rule. Before closing a material package change, use `docs/governance/MAINTAINER-CORRELATION-RULE.md` to check correlated files, and classify `scripts/**` by consumer before deciding which surfaces move. Keep maintainer-only rules here or in `docs/governance/**`; do not copy them into `src/adapters/**`, target bootloaders, user manuals, or `docs/agents/**` unless the delivered Tilly behavior intentionally changed.
</maintainer_boundary>

<release_identity>
Delivered behavior changes require a release-identity decision before closure. If a change adds, removes, or changes adopter-visible skills, triggers, installer behavior, helper/runtime scripts, plugin metadata, public docs, MCP, Field Reports, Cortex behavior, or adapter materialization, decide whether the package version and public bundle must advance.
Default rule: bump the patch version and update correlated release surfaces (`package.json`, script `VERSION` constants, plugin manifests, `docs/dist/<version>/**`, `.sha256` sidecars, `index.json`, public docs, validators, the maintainer correlation rule). After an authorized release tag is pushed, run `npm run release:check`. Exception: if Murillo explicitly keeps the current version for a delivered change, state that exception in the closeout and do not call the package sealed by version identity.
</release_identity>

<operating_discipline>
Operating calibration (maintainer/dev memory only; never Cortex, never `src/**`, never delivered):
- Commit locally by default; stop there until the owner explicitly asks to sync/push. "push it" is not a standing grant — each push needs its own request.
- Smart pre-commit, scoped to what changed: run only the focused oracles relevant to the modified files; reserve the full `commit:check` suite for release/sync.
- The `/goal` Stop hook is a guardrail, not a throttle: alignment pressure, not deadline pressure. For large-surface changes, close each increment green before advancing.
</operating_discipline>

<routing>
| Need | Source |
|------|--------|
| Maintainer governance authority | `AGENTS.md` (identical governance body) |
| Project map | `docs/INDEX.md` |
| Repository structure | `docs/architecture/PROJECT-STRUCTURE.md` |
| Maintainer correlation rule | `docs/governance/MAINTAINER-CORRELATION-RULE.md` |
| Cross-tool governance | `docs/governance/AGENTIC-ALIGNMENT-GOVERNANCE.md` |
| Tool-neutral principles | `docs/mesh/PRINCIPLES.md` |
| Claude instruction source | `src/adapters/claude/CLAUDE.md` |
| Package validation | `python3 scripts/validate_reference_package.py` |
| TDS validation | `python3 scripts/validate_tds.py` |
| Closure gate | `npm run commit:check` |
</routing>

<locks>
- Do not put full source packages back in the repository root, or duplicate adapter source between `src/**` and hidden root tool folders.
- Do not claim the package is sealed without `npm run commit:check`.
- No remote, push, publish, cloud, or marketplace actions without an explicit per-request private decision.
- Keep TES generic: private project/product/internal-service names, storage backends, archive formats, and filesystem paths stay out of tracked content (see `<confidentiality>`).
</locks>