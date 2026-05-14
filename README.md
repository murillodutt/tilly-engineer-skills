# Tilly Engineer Skills (TES)

[![Version](https://img.shields.io/badge/version-0.3.86-1f6feb)](package.json)
[![License](https://img.shields.io/github/license/murillodutt/tilly-engineer-skills)](LICENSE)
[![Live Landing](https://img.shields.io/badge/live--landing-GitHub%20Pages-0969da)](https://murillodutt.github.io/tilly-engineer-skills/)

<p align="center">
  <img src="https://github.com/user-attachments/assets/f5ca3e73-eec9-453a-bb97-a09bdd304c31" alt="Tilly Engineer Skills: agent operating layer for LLM development across Codex, Claude Code, Cursor, and Obsidian-ready project knowledge" width="100%">
</p>

## AI changed your repo. Can your team prove why?

TES gives AI coding work a local service record: the rules used, context
loaded, checks run, evidence kept, and rollback path stay inside the
repository.

[Install with the assisted prompt](https://murillodutt.github.io/tilly-engineer-skills/#start-en)
· [See the landing](https://murillodutt.github.io/tilly-engineer-skills/)
· [Read the manual](https://murillodutt.github.io/tilly-engineer-skills/install/USER-MANUAL.html)

Paste the assisted prompt into Codex, Claude Code, or Cursor from inside the
target repository. TES starts by protecting the repo, then installs with local
evidence and rollback guidance.

TES does not replace Codex, Claude Code, or Cursor. It gives their work an
operating trail: what context was loaded, which rules applied, which gates
passed, what evidence remains, and where rollback starts.

**What you get**

- A trail after the chat is gone.
- Versioned Markdown memory in the repo.
- Deterministic gates before closure.
- Retained evidence your team can inspect.
- Read-only Cortex MCP for project recall.

**Quickstart (30-second setup)**

TES is not active in a project until you install it there. Run the assisted
prompt from inside the target repository; it starts with repo inspection, local
governance preservation, staged installation, verification, and rollback
guidance before closure.

For the commercial npx path, run this from the target repository:

```bash
npx tilly-engineer-skills@latest add
```

For non-interactive installs, pass the agent selection explicitly:

```bash
npx tilly-engineer-skills@latest add --agent all --yes
```

That command is a thin Node wrapper around the certified Python engine. It
delivers the package mechanically, writes a lock and pending post-install
sentinel, and installs first-session hooks. When Codex, Claude Code, or Cursor
opens the project, the hook runs the idempotent post-install routine that
prepares `docs/agents/**` and certifies the initial mesh. You can also run
`/tes-setup` or `/tes-init` in the agent to finish setup.

Maintainers can still call the Python engine directly:

```bash
python3 scripts/tes_install.py install --target /path/to/project --agent all --yes
```

After installation, TES is local-first by default: no push, publish, tags,
remote changes, marketplace action, or write-capable MCP without explicit
authorization. Source maintainers verify this package with `npm run
commit:check`; adopters start from the assisted prompt.

MIT. See [LICENSE](LICENSE).
