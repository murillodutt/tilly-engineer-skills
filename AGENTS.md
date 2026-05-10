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

<locks>

- Do not put full source packages back in the repository root.
- Do not duplicate adapter source between `src/**` and hidden root tool folders.
- Do not claim the package is sealed without `npm run commit:check`.
- Do not add remote, push, publish, cloud, or marketplace actions without an
  explicit private decision.

</locks>
