# AGENTS.md

Portable Codex bootloader for repositories adopting Tilly Engineering
Discipline.

Keep this file small. Put detailed workflows in
`.agents/skills/tilly-engineering-discipline/**`.

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

<routing>

| Need | Source |
|------|--------|
| Reusable workflow | `.agents/skills/tilly-engineering-discipline/SKILL.md` |
| Failure examples | `.agents/skills/tilly-engineering-discipline/references/failure-patterns.md` |
| Tool migration | `.agents/skills/tilly-engineering-discipline/references/source-portability.md` |
| Skill self-test | `python3 .agents/skills/tilly-engineering-discipline/scripts/discipline_oracle.py --self-test` |

</routing>

<locks>

- Do not import Cursor or Claude packaging as Codex runtime truth.
- Do not expand this bootloader into a full inventory.
- Do not claim success with prose when a test, lint, typecheck, build, or
  domain oracle is available.
- Do not add features, public surface, remote actions, secrets, or destructive
  operations unless the target project explicitly authorizes them.

</locks>
