# AGENTS.md

Portable Codex bootloader for repositories adopting Tilly Engineering
Discipline.

Keep this file small. Put detailed workflows in
`.agents/skills/tilly-*/**`.

<instructions>

Apply this overlay to non-trivial coding, review, refactor, or
instruction-migration work:

1. Think Before Coding
   - State assumptions, ambiguity, tradeoffs, and blockers before acting.
   - Do not pick a risky interpretation silently.
2. Simplicity First
   - Solve the requested problem only.
   - Delete speculative scope before adding abstractions or configuration.
3. Surgical Changes
   - Touch only request-traceable lines.
   - Clean only orphans created by the current change.
   - Leave unrelated code, comments, formatting, and dead code alone.
4. Goal-Driven Execution
   - Define a falsifiable oracle before closure.
   - Run the smallest relevant check first, then broader gates when needed.

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
| Reusable workflow | `.agents/skills/tilly-engineering-discipline/SKILL.md` |
| Tilly initialization shortcut | `.agents/skills/tilly-init/SKILL.md` |
| Cortex memory operations | `.agents/skills/tilly-cortex/SKILL.md` |
| MCP activation and checks | `.agents/skills/tilly-mcp/SKILL.md` |
| Health and certification gates | `.agents/skills/tilly-doctor/SKILL.md` |
| Adapter materialization | `.agents/skills/tilly-adapter/SKILL.md` |
| Benchmark evidence | `.agents/skills/tilly-bench/SKILL.md` |
| Failure examples | `.agents/skills/tilly-engineering-discipline/references/failure-patterns.md` |
| Tool migration | `.agents/skills/tilly-engineering-discipline/references/source-portability.md` |
| Skill self-test | `python3 .agents/skills/tilly-engineering-discipline/scripts/discipline_oracle.py --self-test` |

</routing>

<tilly_init>

Treat `/tilly:init`, `/tilly:cortex`, `/tilly:curate`, `/tilly:mcp`, `/tilly:doctor`,
`/tilly:adapter`, and `/tilly:bench` as intent shortcuts. Load the matching
skill and let the agent choose the smallest safe oracle. These are not shell
commands.

</tilly_init>

<cortex_reflex>

If `docs/agents/cortex/CONTRACT.md` exists, treat Cortex as the durable memory
surface. Before the final response for material work, run the read-only MCP
tool `cortex_reflect` when available, or:

```bash
python3 .tilly/bin/cortex.py reflect --target . "<decision or lesson>"
```

Report the proposal only when it is useful. Do not write Cortex cells unless
the user explicitly authorizes promotion.
If `curation_due=true`, run read-only `cortex_curate_plan` when available, or:

```bash
python3 .tilly/bin/cortex.py curate-plan --target . --backend lexical
```

</cortex_reflex>

<locks>

- Do not import Cursor or Claude packaging as Codex runtime truth.
- Do not expand this bootloader into a full inventory.
- Do not claim success with prose when a test, lint, typecheck, build, or
  domain oracle is available.
- Do not add features, public surface, remote actions, secrets, or destructive
  operations unless the target project explicitly authorizes them.

</locks>
