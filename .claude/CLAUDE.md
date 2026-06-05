# CLAUDE.md

Repository bootloader for the independent Tilly Engineer Skills reference
package.

Keep this root file small. Distributable agent source lives in `src/**`;
people-facing method, eval, and architecture material lives in `docs/**`.

<instructions>

Apply Tilly Engineering Discipline to material changes:

1. Think Before Coding — state assumptions, ambiguity, tradeoffs, and blockers
   before acting.
2. Simplicity First — keep root thin; avoid duplicate source copies.
3. Surgical Changes — treat `src/**` as adapter source and `docs/**` as governed
   explanation. Classify `scripts/**` by consumer (see `<scripts_classification>`).
4. Goal-Driven Execution — run the smallest relevant oracle before closure.

</instructions>

<scripts_classification>

Classify every `scripts/**` change by consumer before deciding which surfaces
move:

- Maintainer gate (validators, self-tests) → maintainer-only; not delivered.
- Installer, Cortex, MCP, Field Reports, runtime, or adapter script that an
  adopter receives, invokes, or certifies → delivered behavior (see
  `<release_identity>`).

</scripts_classification>

<documentation_runtime_focus>

Documentation must not become the work. For active engineering lines, use the
latest accepted SPEC/Super SPEC plus its audit record as the normalization
surface, then update only the indexes or roadmap entries needed to keep that
line executable. Prefer programming, fixtures, oracles, and runtime evidence
over parallel explanatory documents.

When a doc change is still necessary, keep it structural and compact: record the
current execution authority, the audit result, the next prompt when the sequence
is open, and the smallest evidence pointer a future agent needs to continue
without chat history.

Roadmaps are executive control surfaces — keep each partition organized and
objective: dashboard for state/next action, registry for durable pointers,
history for closed lineage, audit records for evidence. When a roadmap reaches
its size-warning threshold (`scripts/validate_doc_size.py`, default 85% of the
line limit), partition or compact before adding status. Repeated or ambiguous
roadmap text is a defect to fix in the same cycle.

</documentation_runtime_focus>

<runtime_first_rule>

TES is a product, not a governance archive. Optimize material work for result,
maturity, efficiency, and precision. When an architecture is accepted and the
remaining risk is implementation quality, switch to runtime-first execution. Do
not create governance-only cycles, evidence-only layers, placeholder boundaries,
long SPECs before code, or temporary runtimes meant to be removed immediately.

Build the smallest durable runtime slice on the intended execution path, then
use fixtures, oracles, and compact docs to protect that behavior. Boundaries and
SPECs are valuable only when they constrain or certify executable behavior — they
are not progress by themselves. Circular execution is useful for a real defect
or a clear incremental delivery; once it creates the next prompt by habit it is
noise. If the next unit does not improve runtime, latency, audio quality,
safety, or direct maintenance, do not create it.

</runtime_first_rule>

<success_formula>

```text
E = A * S * C * V
```

Success is zero if assumptions are hidden, scope is inflated, changes are not
surgical, or verification is missing.

</success_formula>

<feedback_voice>

Talk to the user in objective, direct human prose. Lead with the conclusion,
then the reasoning that supports it — humans follow clear, logical prose well.
Default away from tables, bullet dumps, code blocks, and long inventories; use
them only when the user asks or when the artifact genuinely needs exact syntax
(a routing table, a command, a roadmap partition). Do not pad answers into a
"Wikipedia" wall of structured facts and cross-references. Fewer words, more
signal: say what is true, why it matters, and what to do next.

</feedback_voice>

<diamond_build_test_fail_fix>

For critical capabilities, build from the finished contract down: final
behavior, adversarial fixture, observed failure, smallest repair, green gate. Do
not call certified behavior experimental; use `blocked`, `degraded`,
`not available`, `certified`, or `fail`.

</diamond_build_test_fail_fix>

<regression_guard>

For every TES package analysis, write, runtime change, oracle change, commit, or
closeout, self-consume `.agents/skills/tes-regression-guard/SKILL.md`. This is an
always-on local reasoning kernel, not a user-invoked skill and not a product
command. Routine use stays implicit; report it only when it blocks, downgrades
confidence, requires owner choice, or the user asks for audit detail.

Before changing behavior that already has certified, installed, materialized,
generated, measured, or human-rated evidence, name the last-known-good baseline,
classify whether the change preserves/extends/replaces it, and list protected
invariants before editing.

Regression is project-wide, not Python-specific. Protect skills, triggers,
adapters, materialized outputs, installers, runtime scripts, docs, roadmaps,
oracles, generated public pages, version identity, release surfaces, private
vocabulary, safety behavior, and UX claims. A passing source check is not enough
when the risk lives in an installed, generated, materialized, audio, public, or
CLI surface; run the comparison matching the surface that can regress.

Avoid narrow literal lists in runtime code unless they are governed data, schema,
or contract backed. Example-specific fixes are regression seeds.

</regression_guard>

<mantra_gate>

Before state-changing actions, use the TES Mantra Gate. When it permits
proceeding, show only `[🍳 Flash-Fry]` to the user, but the full gate must still
record `VERIFY`, `SCOPE`, `BEST_PATH`, `DOCUMENT`, `ORACLE`, `RESOLVE`, and
`STATUS` in the appropriate evidence surface.

Report gate detail only when it returns `BLOCKED`/`NEEDS_REVIEW`, when approval
is needed, or when the user asks for audit detail. High-risk work requires a
complete internal record and oracle; forbidden work still stops.

For closure, commit, or push claims, use the Mantra Gate adoption oracle when
available. Treat `BYPASS_SUSPECTED`, `NEEDS_REVIEW`, or `BLOCKED` as a stop
condition until the gate record, scope, risk, and closure oracle are repaired.

</mantra_gate>

<real_project_learning_standard>

Real project executions are learning loops, not one-off support runs. After each
TES update cycle, use at least one real project canary to expose drift, false
greens, stale helpers, adapter gaps, and semantic-context gaps.

When a canary reports `NEEDS_REVIEW`, `DEGRADED`, `BLOCKED`, or any meaningful
drift:

1. Treat the finding as TES product evidence.
2. Classify the failure before fixing it.
3. Patch TES source, oracle, docs, adapter, installer, or governance as needed.
4. Return to the TES canary workspace (`~/Dev/tes-canaries`, the TES project's
   own named test area — not a client project, so it is allowed in tracked
   content) and certify the fix with a durable run record.
5. Re-run the original project canary to prove the fix.
6. Repeat on two additional real projects before any commercial-use claim.

Do not promote a project-specific workaround into TES. Only promote portable
learning that survives canary replay and maintainer gates.

</real_project_learning_standard>

<target_source_boundary>

Installed target projects and canary clones are evidence targets, not the source
of truth for TES behavior.

When a target-project run exposes a TES skill, installer, hook, oracle, or docs
bug:

1. Classify whether the finding is portable TES product evidence or a
   target-owned issue.
2. If portable, patch the TES package source here (`src/**`, `scripts/**`,
   `docs/**`, and correlated release surfaces) — not only the installed mirrors
   inside the target (`.agents/skills/**`, `.claude/skills/**`, `skills/**`,
   `plugins/tilly-engineer-skills/**`).
3. Use the target again only to certify the packaged fix installs and behaves.
4. Do not generalize one target's npm/pnpm/bun or gate scripts as universal TES
   commands; delivered skills must distinguish installed-target gates from
   package-source gates before certifying.

Private project names stay out of TES content (see
`<private_project_confidentiality>`).

</target_source_boundary>

<private_project_confidentiality>

TES is a generic engineering discipline package. Worked examples in source, docs,
evidence, fixtures, commit messages, and tag annotations must use neutral
placeholder vocabulary only: `target-project`, `canary-project`, `real-project`,
`<project-A>`, `<storage-backend>`, `<archive-format>`, and similar.

Anything identifying a specific real client/adopter project, product,
internal-service, repository path under `~/Dev/<client-name>`, or private
codebase vocabulary belongs in the maintainer's local notes, not in TES tracked
content. (The TES project's own infrastructure names, such as the
`~/Dev/tes-canaries` workspace, are not client names and are allowed.) When
citing a private canary for traceability, use a generic form such as "a private
canary project (source-of-record kept off TES repository)" and keep the
identifier local.

`docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` defines the mechanism that lets target
projects declare and enforce their own vocabulary without it being known to TES.
`scripts/private_vocabulary_oracle.py` runs on every `npm run commit:check`
against the local allowlist at `.tes/private-vocabulary.txt` (gitignored, never
committed) and fails the gate if any listed name appears in tracked content.

When in doubt, prefer the placeholder — placeholders are always reversible in
private notes.

</private_project_confidentiality>

<routing>

| Need | Source |
|------|--------|
| Project map | `docs/INDEX.md` |
| Repository structure | `docs/architecture/PROJECT-STRUCTURE.md` |
| TDS contract | `docs/tds/TDS-SPEC.md` |
| TDS governed index | `docs/tds/DOCS-INDEX.yml` |
| Cross-tool governance | `docs/governance/AGENTIC-ALIGNMENT-GOVERNANCE.md` |
| Maintainer correlation rule | `docs/governance/MAINTAINER-CORRELATION-RULE.md` |
| Tool-neutral principles | `docs/mesh/PRINCIPLES.md` |
| Context mesh method | `docs/mesh/CONTEXT-MESH-METHOD.md` |
| Adoption scorecard | `docs/mesh/SCORECARD.md` |
| Eval design | `docs/evals/EVALS.md` |
| Detailed examples | `docs/evals/EXAMPLES.md` |
| Codex adapter guide | `docs/adapters/CODEX.md` |
| Claude adapter guide | `docs/adapters/CLAUDE.md` |
| Cursor adapter guide | `docs/adapters/CURSOR.md` |
| Codex bootloader source | `src/adapters/codex/AGENTS.md` |
| Codex skill source | `src/adapters/codex/skills/tes-engineering-discipline/SKILL.md` |
| Claude instruction source | `src/adapters/claude/CLAUDE.md` |
| Cursor rule source | `src/adapters/cursor/rules/tes-guidelines.mdc` |
| Package validation | `python3 scripts/validate_reference_package.py` |
| TDS validation | `python3 scripts/validate_tds.py` |
| Closure gate | `npm run commit:check` |

</routing>

<maintainer_boundary>

This file governs agents working on the Tilly Engineer Skills package itself; it
is not an installed target-project rule.

Before closing a material package change, use
`docs/governance/MAINTAINER-CORRELATION-RULE.md` to check correlated files, and
classify `scripts/**` by consumer (`<scripts_classification>`) before deciding
which surfaces must move. Keep maintainer-only rules in `AGENTS.md` or
`docs/governance/**`; do not copy them into `src/adapters/**`, target
bootloaders, user manuals, or `docs/agents/**` unless the delivered Tilly
behavior intentionally changed.

</maintainer_boundary>

<release_identity>

Delivered behavior changes require a release identity decision before closure. If
a change adds, removes, or changes adopter-visible skills, triggers, installer
behavior, helper/runtime scripts, plugin metadata, public docs, MCP, Field
Reports, Cortex behavior, or adapter materialization, check whether the package
version and public bundle must advance.

Reference case: adding `/tes-prospect` and `/tes-mine` as explicit-invocation
predictive skills is delivered behavior even when execution stays opt-in and
behavior is otherwise preserved — that class of change needs a version/bundle
decision before closeout.

Default rule: bump the patch version and update correlated release surfaces when
delivered behavior changes. Check `package.json`, script `VERSION` constants,
plugin manifests, `docs/dist/<version>/**`, `.sha256` sidecars, `index.json`,
public docs, validators, and the maintainer correlation rule. After an authorized
release tag is pushed, run `npm run release:check` before claiming the fixed
GitHub npx or Bun installer ref is certified.

Exception rule: if Murillo explicitly decides to keep the current version for a
delivered behavior change, state that exception in the closeout and do not call
the package sealed by version identity. The behavior may be committed, but the
next release/bundle cycle must know the bump was intentionally deferred.

</release_identity>

<maintainer_operating_discipline>

Operating calibration for working in this repository (maintainer/dev memory only;
never Cortex, never `src/**`, never delivered).

- Commit locally by default. Apply commits to the local repository and stop there
  until the owner explicitly asks to sync/push. "push it" is not a standing
  grant; each push needs its own request (this strengthens the remote-action lock
  in `<locks>`).
- Smart pre-commit, scoped to what changed. Do not run the full `commit:check`
  suite for every change. Run only the focused oracles relevant to the modified
  files; reserve the full suite for release/sync. This saves significant time and
  compute. The full suite remains mandatory before a sync/bump/push.
- The `/goal` Stop hook is a guardrail, not a throttle. It keeps the agent on the
  line — on task, on the current SPEC, minimizing invention and drift — rather
  than pushing for speed. When the agent is being creative, that hook is what
  closes the drift valve; treat it as alignment pressure, not deadline pressure.
  For large-surface changes, close each increment green before advancing; a
  forced march produced this session's reverts and tracking slips.

</maintainer_operating_discipline>

<locks>

- Do not put full source packages back in the repository root.
- Do not duplicate adapter source between `src/**` and hidden root tool folders.
- Do not claim the package is sealed without `npm run commit:check`.
- Do not add remote, push, publish, cloud, or marketplace actions without an
  explicit private decision.
- Keep TES generic: private project/product/internal-service names, storage
  backends, archive formats, and filesystem paths stay out of tracked content
  (see `<private_project_confidentiality>`).

</locks>
