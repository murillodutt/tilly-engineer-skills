# AGENTS.md

Repository bootloader for the independent Tilly Engineer Skills reference
package.

Keep this root file small. The distributable agent source lives in `src/**`.
People-facing method, eval, and architecture material lives in `docs/**`.

<instructions>

Apply Tilly Engineering Discipline to material changes in this repository:

1. Think Before Coding
   - State assumptions, ambiguity, tradeoffs, and blockers before acting.
2. Simplicity First
   - Keep root thin and avoid duplicate source copies.
3. Surgical Changes
   - Treat `src/**` as adapter source and `docs/**` as governed explanation.
   - Classify `scripts/**` by consumer: validators are maintainer gates;
     installer, Cortex, MCP, Field Reports, and adapter scripts may be
     delivered behavior when adopters receive, invoke, or certify them.
4. Goal-Driven Execution
   - Run the smallest relevant oracle before closure.

</instructions>

<success_formula>

```text
E = A * S * C * V
```

Success is zero if assumptions are hidden, scope is inflated, changes are not
surgical, or verification is missing.

</success_formula>

<diamond_build_test_fail_fix>

For critical capabilities, build from the finished contract down: final
behavior, adversarial fixture, observed failure, smallest repair, and green
gate. Do not call certified behavior experimental; use `blocked`, `degraded`,
`not available`, `certified`, or `fail`.

</diamond_build_test_fail_fix>

<real_project_learning_standard>

Real project executions are learning loops, not one-off support runs. After each
TES update cycle, use at least one real project canary to expose drift, false
greens, stale helpers, adapter gaps, and semantic-context gaps.

When a canary reports `NEEDS_REVIEW`, `DEGRADED`, `BLOCKED`, or any meaningful
drift:

1. Treat the finding as TES product evidence.
2. Classify the failure before fixing it.
3. Patch TES source, oracle, docs, adapter, installer, or governance as needed.
4. Return to `~/Dev/tes-canaries` and certify the fix with a durable run record.
5. Re-run the original project canary to prove the fix.
6. Repeat on two additional real projects before making a commercial-use claim.

Do not promote a project-specific workaround into TES. Only promote portable
learning that survives canary replay and maintainer gates.

</real_project_learning_standard>

<target_source_boundary>

Installed projects such as <project-A>, <project-b>-private, or canary clones are evidence
targets, not the source of truth for TES behavior.

When a target-project run exposes a TES skill, installer, hook, oracle, or docs
bug:

1. Classify whether the finding is portable TES product evidence or a
   target-owned issue.
2. If portable, patch the TES package source here: `src/**`, `scripts/**`,
   `docs/**`, and the correlated release surfaces.
3. Do not fix only the installed mirrors inside the target project, such as
   `.agents/skills/**`, `.claude/skills/**`, `skills/**`, or
   `plugins/tilly-engineer-skills/**`.
4. Use the target again only to certify that the packaged TES fix installs and
   behaves correctly.
5. Do not generalize one target project's npm, pnpm, bun, or gate scripts as
   universal TES commands. Delivered skills must distinguish installed-target
   gates from package-source gates before certifying anything.

</target_source_boundary>

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

This file governs agents working on the Tilly Engineer Skills package itself.
It is not an installed target-project rule.

Before closing a material package change, use
`docs/governance/MAINTAINER-CORRELATION-RULE.md` to check correlated files.
Classify `scripts/**` by consumer before deciding which surfaces must move.
Keep maintainer-only rules in `AGENTS.md` or `docs/governance/**`; do not copy
them into `src/adapters/**`, target bootloaders, user manuals, or
`docs/agents/**` unless the delivered Tilly behavior intentionally changed.

</maintainer_boundary>

<release_identity>

Delivered behavior changes require a release identity decision before closure.
If a change adds, removes, or changes adopter-visible skills, triggers,
installer behavior, helper/runtime scripts, plugin metadata, public docs, MCP,
Field Reports, Cortex behavior, or adapter materialization, check whether the
package version and public bundle must advance.

Reference case: adding `/tes-prospect` and `/tes-mine` as explicit-invocation
predictive skills is delivered behavior, even when their execution remains
opt-in and their behavior is otherwise preserved. That class of change needs a
version/bundle decision before closeout.

Default rule: bump the patch version and update correlated release surfaces
when delivered behavior changes. Check `package.json`, script `VERSION`
constants, plugin manifests, `docs/dist/<version>/**`, `.sha256` sidecars,
`index.json`, public docs, validators, and the maintainer correlation rule.

Exception rule: if Murillo explicitly decides to keep the current version for a
delivered behavior change, state that exception in the closeout and do not call
the package sealed by version identity. The behavior may be committed, but the
next release/bundle cycle must know the version bump was intentionally deferred.

</release_identity>

<locks>

- Do not put full source packages back in the repository root.
- Do not duplicate adapter source between `src/**` and hidden root tool folders.
- Do not claim the package is sealed without `npm run commit:check`.
- Do not add remote, push, publish, cloud, or marketplace actions without an
  explicit private decision.

</locks>
