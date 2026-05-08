# AGENTS.md

Portable Codex bootloader for repositories adopting Tilly Engineering
Discipline.

Keep this file small. Put detailed workflows in
`.agents/skills/tes-*/**`.

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

<feedback_voice>

Default to short, frank prose. Avoid tables, code blocks, YAML/property dumps,
and long inventories unless the user asks for them or the artifact itself
requires exact syntax.

</feedback_voice>

<routing>

| Need | Source |
|------|--------|
| Reusable workflow | `.agents/skills/tes-engineering-discipline/SKILL.md` |
| Tilly initialization shortcut | `.agents/skills/tes-init/SKILL.md` |
| Cortex memory operations | `.agents/skills/tes-cortex/SKILL.md` |
| MCP activation and checks | `.agents/skills/tes-mcp/SKILL.md` |
| Health and certification gates | `.agents/skills/tes-doctor/SKILL.md` |
| Adapter materialization | `.agents/skills/tes-adapter/SKILL.md` |
| Benchmark evidence | `.agents/skills/tes-bench/SKILL.md` |
| Failure examples | `.agents/skills/tes-engineering-discipline/references/failure-patterns.md` |
| Tool migration | `.agents/skills/tes-engineering-discipline/references/source-portability.md` |
| Skill self-test | `python3 .agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test` |

</routing>

<tes_init>

Treat `/tes-init`, `/tes-update`, `/tes:init`, `/tes:update`, `tes init`,
`tes update`, `initialize TES`, `install TES`, `recertify TES`,
`inicializar TES`, `instalar TES`, `recertificar TES`, and natural
command/prompts such as `TES, initialize this project`,
`TES, inicialize este projeto`, `Atualizar TES`, or `atualizar TES` as
installer intents.
`/tes-update` first checks installed
version, cloud version, helper contract parity, applied IDE surfaces,
recommended route, and `recommended_update_scope`. Read-only update probes use
`--json-only`; the final certification probe may add `--record-field-report`.
`recommended_update_scope=helpers-only` or `STALE_HELPERS` is repaired first
through the helper-only Layer Zero route before MCP config activation. After any
helper overwrite, the final recorded probe is required before GO, commit, or
push and must show `helper_contract_status=PASS`, `runtime_trigger_status=PASS`
or `NOT_APPLIED`, `update_available=False`, and `recommended_update_scope=none`.
Also treat `/tes-cortex`, `/tes:cortex`, `/tes-curate`, `/tes:curate`,
`/tes-mcp`, `/tes:mcp`, `/tes-field-reports`, `/tes:field-reports`,
`/tes-doctor`, `/tes:doctor`, `/tes-adapter`, `/tes:adapter`, `/tes-bench`,
and `/tes:bench` as intent shortcuts. Load the matching skill
and let the agent choose the smallest safe oracle. These are not shell commands.

</tes_init>

<cortex_reflex>

If `docs/agents/cortex/CONTRACT.md` exists, treat Cortex as the durable memory
surface. Before the final response for material work, run the read-only MCP
tool `cortex_reflect` when available, or:

```bash
python3 .tes/bin/cortex.py reflect --target . "<decision or lesson>"
```

Report the proposal only when it is useful. Do not write Cortex cells unless
the user explicitly authorizes promotion.
If `curation_due=true`, run read-only `cortex_curate_plan` when available, or:

```bash
python3 .tes/bin/cortex.py curate-plan --target . --backend lexical
```

</cortex_reflex>

<field_reports>

TES Field Reports is active by default. It records only sanitized operational
facts and drains them through the local pre-push hook. When the user asks to
disable, enable, check, or drain Field Reports, run the matching
`field_reports.py` oracle and never expand collection levels or schema.

</field_reports>

<locks>

- Do not import Cursor or Claude packaging as Codex runtime truth.
- Do not expand this bootloader into a full inventory.
- Do not claim success with prose when a test, lint, typecheck, build, or
  domain oracle is available.
- Do not add features, public surface, remote actions, secrets, or destructive
  operations unless the target project explicitly authorizes them.

</locks>
