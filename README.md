# Tilly Engineer Skills (TES)

[![Version](https://img.shields.io/badge/version-0.3.101-1f6feb)](package.json)
[![License](https://img.shields.io/github/license/murillodutt/tilly-engineer-skills)](LICENSE)
[![Live Landing](https://img.shields.io/badge/live--landing-GitHub%20Pages-0969da)](https://murillodutt.github.io/tilly-engineer-skills/)

<p align="center">
  <img src="https://github.com/user-attachments/assets/f5ca3e73-eec9-453a-bb97-a09bdd304c31" alt="Tilly Engineer Skills: agent operating layer for LLM development across Codex, Claude Code, Cursor, and Obsidian-ready project knowledge" width="100%">
</p>

## AI changed your repo. Can your team prove why?

TES is a local trust layer for AI coding work. It keeps the rules used,
context loaded, checks run, evidence kept, and rollback path inside the
repository.

[Start from the landing](https://murillodutt.github.io/tilly-engineer-skills/#start-en)
· [Read the manual](https://murillodutt.github.io/tilly-engineer-skills/install/USER-MANUAL.html)
· [Browse the docs](docs/INDEX.md)

TES does not replace Codex, Claude Code, or Cursor. It surrounds them with an
operating trail your team can inspect after the chat is gone.

**What you get**

- A trail after the chat is gone.
- Versioned Markdown memory in the repo.
- Deterministic gates before closure.
- Retained evidence your team can inspect.
- Read-only Cortex MCP for project recall.

**Where to start**

Installation details live on the public surface where users need them:

- The landing page gives the 30-second GitHub path for npx and Bun.
- The user manual covers options, first-session setup, rollback, and audit.
- This repository keeps the source, contracts, gates, and evidence.

Important: do not start project work immediately after install. The first run
must complete the agent path:

```text
install -> hook -> /tes-setup -> /tes-align
```

Use `/tes-update` for updates, `/tes-doctor` for repair, and `/tes-align` when
the project Markdown operating mesh needs to be refreshed.

Source maintainers verify this package with `npm run commit:check`.

MIT. See [LICENSE](LICENSE).
