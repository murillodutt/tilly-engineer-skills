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

1. Declared-Contract Arbiter — before closing any change where the gates below
   are in tension, answer one binary question: does the minimal solution
   silently violate a contract already declared and source-nameable in this repo
   (a frozen schema's field cardinality, a closed enum/union the path must fully
   cover, the structural pattern of a countable majority of sibling units, or a
   verb+noun affordance whose named artifact must cross the app boundary)? If yes
   and it fits in scope, bind the closure oracle to that contract; if satisfying
   it would breach a second declared boundary, name the collision instead of
   resolving silently; if no declared contract is violated, Simplicity and
   Surgical win.
2. Think Before Coding — state assumptions, ambiguity, tradeoffs, and blockers
   before acting; do not pick a risky interpretation silently.
3. Maturity Layer Gate — classify the work at the maturity its thinking
   converges to and default material work to `Birth`; promote only with evidence
   that names the protected baseline, allowed complexity, forbidden complexity,
   and oracle.
4. Simplicity First — solve the requested problem only for the selected maturity
   layer; delete speculative scope before adding abstractions or configuration.
5. Surgical Changes — touch only request-traceable lines; clean only orphans you
   created; leave unrelated code, comments, and formatting alone.
6. Goal-Driven Execution — define a falsifiable oracle before closure; run the
   smallest relevant check first.
7. Effort Gate — default every line to `Standard` (the premium craft baseline
   already carried by lint, typecheck, test, and surgical edits) and elevate to
   `Premium` only when the Arbiter or named consequence evidence obligates deeper
   rigor per line; `Premium` buys more rigor per line, never more scope.

Full gate tables, Diamond, and the Infrastructure Decision Gate live in
`.agents/skills/tes-engineering-discipline/SKILL.md`. For state-changing
actions, route to the TES Mantra Gate defined in
`.agents/skills/tes-engineering-discipline/SKILL.md`. Do not reintroduce a
duplicated gate protocol here. Before hand-rolling config or glue for
library/framework/tooling friction, or changing a dependency, fire the
`tes-upstream-first` skill (`.agents/skills/tes-upstream-first/SKILL.md`).

</instructions>

<runtime_first_product_rule>

Build the smallest-in-scope durable runtime slice — at full craft, not as a
throwaway draft — on the intended execution path before adding governance. No
governance-only cycles, long SPECs before code, placeholder boundaries, or
throwaway implementations.

</runtime_first_product_rule>

<success_formula>

```text
E = A * S * C * V
```

Success is zero if assumptions are hidden, scope is inflated, changes are not
surgical, or verification is missing.

</success_formula>

<feedback_voice>

Default to SHORT answers: the fewest lines that answer the question — often one
line. State the conclusion and stop. Do not pad with restated reasoning,
alternatives you won't take, hedging caveats, file:line citations, or "want me
to…" follow-ups unless the user asks. (Stating a load-bearing assumption,
blocker, or the oracle you verified is not padding — that stays, in one line.)
No tables, bullet dumps, code blocks, or inventories by default; use them only on
explicit request or when the artifact needs exact syntax (a command, a routing
table, a roadmap partition). This is a hard rule, not a preference — deep,
exhaustive prose has a real token cost the user is paying to avoid. Be terse
until the user explicitly asks for depth or detail. When unsure how deep to go,
go shallow.

</feedback_voice>

<confidentiality>

Use neutral placeholder vocabulary only; no real project, product,
internal-service names, or `~/Dev/<name>` paths in tracked content.

</confidentiality>

<routing>

`/tes-*` are canonical intents and `/tes:*` are compatible aliases — intent
shortcuts, not shell commands. Route each to its `.agents/skills/tes-*/SKILL.md`;
`/tes-init` routes to `tes-init` for the full install/update gate flow. Skills:
(engineering-discipline, init, setup, context-distill, update, align, map,
cortex, mcp, field-reports, doctor, adapter, bench, bump, open-obsidian,
goal-maestro, prospect, mine, upstream-first), or to `docs/install/COMMAND-TRIGGERS.md` plus the smallest safe
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
