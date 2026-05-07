# AGENTS.md

Repository bootloader for the independent Tilly Engineer Skills reference
package.

Keep this root file small. The distributable agent source lives in `src/**`.
Human method, eval, and architecture material lives in `docs/**`.

<instructions>

Apply Tilly Engineering Discipline to material changes in this repository:

1. Think Before Coding
   - State assumptions, ambiguity, tradeoffs, and blockers before acting.
2. Simplicity First
   - Keep root thin and avoid duplicate source copies.
3. Surgical Changes
   - Treat `src/**` as source, `docs/**` as explanation, and scripts as gates.
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

<routing>

| Need | Source |
|------|--------|
| Project map | `docs/INDEX.md` |
| Repository structure | `docs/architecture/PROJECT-STRUCTURE.md` |
| TDS contract | `docs/tds/TDS-SPEC.md` |
| TDS governed index | `docs/tds/DOCS-INDEX.yml` |
| Cross-tool governance | `docs/governance/AGENTIC-ALIGNMENT-GOVERNANCE.md` |
| Tool-neutral principles | `docs/mesh/PRINCIPLES.md` |
| Context mesh method | `docs/mesh/CONTEXT-MESH-METHOD.md` |
| Adoption scorecard | `docs/mesh/SCORECARD.md` |
| Eval design | `docs/evals/EVALS.md` |
| Detailed examples | `docs/evals/EXAMPLES.md` |
| Codex adapter guide | `docs/adapters/CODEX.md` |
| Claude adapter guide | `docs/adapters/CLAUDE.md` |
| Cursor adapter guide | `docs/adapters/CURSOR.md` |
| Codex bootloader source | `src/adapters/codex/AGENTS.md` |
| Codex skill source | `src/adapters/codex/skills/tilly-engineering-discipline/SKILL.md` |
| Claude instruction source | `src/adapters/claude/CLAUDE.md` |
| Cursor rule source | `src/adapters/cursor/rules/tilly-guidelines.mdc` |
| Package validation | `python3 scripts/validate_reference_package.py` |
| TDS validation | `python3 scripts/validate_tds.py` |

</routing>

<locks>

- Do not put full source packages back in the repository root.
- Do not duplicate adapter source between `src/**` and hidden root tool folders.
- Do not claim the package is sealed without `npm run commit:check`.
- Do not add remote, push, publish, cloud, or marketplace actions without an
  explicit private decision.

</locks>
