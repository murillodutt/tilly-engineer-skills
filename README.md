[Start from the landing](https://murillodutt.github.io/tilly-engineer-skills/#start-en)
· [Read the manual](https://murillodutt.github.io/tilly-engineer-skills/install/USER-MANUAL.html)
· [Browse the docs](https://murillodutt.github.io/tilly-engineer-skills/#/doc/INDEX)

# Tilly Engineer Skills (TES)

[![Version](https://img.shields.io/badge/version-0.3.137-1f6feb)](package.json)
[![License](https://img.shields.io/github/license/murillodutt/tilly-engineer-skills)](LICENSE)
[![Live Landing](https://img.shields.io/badge/live--landing-GitHub%20Pages-0969da)](https://murillodutt.github.io/tilly-engineer-skills/)

<p align="center">
  <img src="https://github.com/user-attachments/assets/f5ca3e73-eec9-453a-bb97-a09bdd304c31" alt="Tilly Engineer Skills: agent operating layer for LLM development across Codex, Claude Code, Cursor, and Obsidian-ready project knowledge" width="100%">
</p>

## AI changed your repo. Can your team prove why?

TES is a local trust layer for AI coding work. It keeps the rules used,
context loaded, checks run, evidence kept, and rollback path inside the
repository.

> [!NOTE]
> TES does not replace Codex, Claude Code, or Cursor. It surrounds them with an
> operating trail your team can inspect after the chat is gone.

**What you get**

- A trail after the chat is gone.
- Versioned Markdown memory in the repo.
- Project GPS with `/tes-map` for the current phase, blockers, proof, and next move.
- Goal Maestro with `/tes-goal-maestro` for mature-artifact-to-execution-tree-to-`/goal` materialization with tree acceptance.
- Mantra Gate with `[🍳 Flash-Fry]` before state-changing actions.
- Deterministic gates before closure.
- Retained evidence your team can inspect.
- Read-only Cortex MCP for project recall.

**Where to start**

Installation details live on the public surface where users need them:

- The landing page gives the 30-second GitHub path for npx and Bun.
- The user manual covers options, first-session setup, rollback, and audit.
- This repository keeps the source, contracts, gates, and evidence.

> [!IMPORTANT]
> **Agent follow-up is host-specific**
>
> Do not start project work immediately after install. The first run completes
> differently by host:
>
> - Codex: open Settings > Hooks for this project, then Trust and enable the
>   Session Start hook if it is marked needs review.
> - Claude Code: open or reopen Claude Code, wait for the TES completion notice,
>   then run `/tes-setup`.
> - Cursor: reopen the workspace, let first-session setup complete, then run
>   `/tes-setup` for the report.

```text
install -> hook -> /tes-setup -> /tes-align -> /tes-map
```

> [!TIP]
> Only after `/tes-setup` reports complete, run `/tes-align` before project work.
> Use `/tes-map` when you need the current GPS view. `/tes-update` is a direct
> visible update skill for already installed meshes, and `/tes-doctor` is for
> repair.

Source maintainers verify this package with `npm run commit:check`.

MIT. See [LICENSE](LICENSE).
