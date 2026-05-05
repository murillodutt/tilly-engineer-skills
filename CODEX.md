# Codex Derivation

This directory contains a Codex-native derivation of Tilly Engineering
Discipline.

Project version: `0.1.0`.

It follows the Codex customization order:

1. `AGENTS.md` for durable repository guidance.
2. Skills for reusable workflows and domain expertise.
3. Scripts and references for progressive disclosure.
4. MCP or plugins only when a workflow needs external systems or distribution.

Official reference: <https://developers.openai.com/codex/concepts/customization>

## Files To Copy

| Source | Target |
|--------|--------|
| `AGENTS.md` | Target repo root `AGENTS.md` or merge into existing one |
| `.agents/skills/tilly-engineering-discipline/` | Target repo `.agents/skills/tilly-engineering-discipline/` |
| `scripts/validate_reference_package.py` | Optional package validation script |

For a global personal skill, copy the skill directory to
`$HOME/.agents/skills/tilly-engineering-discipline/`.

## Why This Shape

Codex uses progressive disclosure for skills:

- Metadata stays visible for discovery.
- `SKILL.md` loads only when the workflow is selected.
- References and scripts load or run only when needed.

This keeps the four gates available without bloating every context window.

## Do Not Copy

Do not copy these into Codex runtime as authoritative surfaces:

- `.claude-plugin/**`
- `.cursor/**`
- `.DS_Store`

They are tool-specific packages or local OS artifacts. Use them only as source
material when maintaining the corresponding tool variant.

## Validation

From this repository:

```bash
python3 scripts/validate_reference_package.py
python3 scripts/context_mesh_plan.py
python3 .agents/skills/tilly-engineering-discipline/scripts/discipline_oracle.py --self-test
```

In a target Codex repository, add project-specific checks such as tests,
typecheck, lint, build, or governance gates. The discipline is successful only
when a concrete oracle passes.
