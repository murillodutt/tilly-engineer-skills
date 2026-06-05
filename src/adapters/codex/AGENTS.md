# AGENTS.md

Portable Codex bootloader for repositories adopting Tilly Engineering Discipline.
This is the always-on anchor; Codex loads only a skill's name, description, and
path until needed, so detailed workflows live in `.agents/skills/tes-*/**`.

<core_contract>

```text
Assumptions visible. Scope smaller. Edits surgical. Success falsifiable.
```

</core_contract>

<instructions>

Apply to non-trivial coding, review, refactor, or instruction-migration work:

1. Think Before Coding — state assumptions, ambiguity, tradeoffs, and blockers
   before acting; do not pick a risky interpretation silently.
2. Maturity Layer Gate — default material work to `Birth`; promote only with
   evidence that names the protected baseline, allowed complexity, forbidden
   complexity, and oracle.
3. Simplicity First — solve the requested problem only for the selected maturity
   layer; delete speculative scope before adding abstractions or configuration.
4. Surgical Changes — touch only request-traceable lines; clean only orphans you
   created; leave unrelated code, comments, and formatting alone.
5. Goal-Driven Execution — define a falsifiable oracle before closure; run the
   smallest relevant check first.

Full gate tables, Diamond, and the Infrastructure Decision Gate live in
`.agents/skills/tes-engineering-discipline/SKILL.md`. For state-changing
actions, route to the TES Mantra Gate defined in
`.agents/skills/tes-engineering-discipline/SKILL.md`. Do not reintroduce a
duplicated gate protocol here.

</instructions>

<runtime_first_product_rule>

Build the smallest durable runtime slice on the intended execution path before
adding governance. No governance-only cycles, long SPECs before code, placeholder
boundaries, or throwaway implementations.

</runtime_first_product_rule>

<success_formula>

```text
E = A * S * C * V
```

Success is zero if assumptions are hidden, scope is inflated, changes are not
surgical, or verification is missing.

</success_formula>

<feedback_voice>

Short, frank prose. Avoid tables, code blocks, and long inventories unless the
user asks or the artifact requires exact syntax.

</feedback_voice>

<confidentiality>

Use neutral placeholder vocabulary only; no real project, product,
internal-service names, or `~/Dev/<name>` paths in tracked content.

</confidentiality>

<routing>

`/tes-*` are canonical intents and `/tes:*` are compatible aliases — intent
shortcuts, not shell commands. Route each to its `.agents/skills/tes-*/SKILL.md`;
`/tes-init` routes to `tes-init` for the full install/update gate flow. Skills:
(engineering-discipline, init, setup, update, align, map, cortex, mcp,
field-reports, doctor, adapter, bench, bump, open-obsidian, goal-maestro,
prospect, mine), or to `docs/install/COMMAND-TRIGGERS.md` plus the smallest safe
oracle when no skill applies. Bilingual natural intents route the same way.

The engineering-discipline skill owns the Mantra Gate; its self-test is
`python3 .agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test`.
`/tes-prospect`, `/tes-mine`, and `/tes-goal-maestro` require explicit invocation
— never from broad natural language — and honor the cognitive brake.

</routing>

<locks>

- Do not import Cursor or Claude packaging as Codex runtime truth.
- Keep this bootloader thin; do not restate skill detail here.
- Do not claim success with prose when a test, lint, typecheck, build, or domain
  oracle is available.
- No features, public surface, remote actions, secrets, or destructive
  operations unless the target project explicitly authorizes them.

</locks>
