---
tds_id: adapters.claude
tds_class: adapter
status: active
consumer: claude code adopters and package maintainers
source_of_truth: true
evidence_level: L2
tver: 0.3.2
---

# Claude Adapter

This document governs the Claude Code derivation of Tilly Engineering
Discipline.

The Claude adapter follows the same TES contract as Codex and Cursor, but it
must use Claude Code surfaces instead of copying Codex packaging. Do not claim
live behavior parity beyond the gates and evidence explicitly certified for
each runtime.

## Official Surfaces

| Surface | Role | Package Status |
|---------|------|----------------|
| `CLAUDE.md` | Persistent project guidance loaded as memory | Included |
| `.claude/skills/**` | Project-native reusable workflows and direct `/tes-*` slash commands | Included |
| `src/adapters/claude/plugin/**` | Plugin metadata template | Source-only; not installed into targets |
| Settings | Enforcement and permission policy | Documented only |
| Hooks | First-session setup context and operational scripts | Installer first-session hook only; plugin default stays blocked |
| MCP | Project-scoped Cortex access | Installer route only |
| Subagents | Independent specialist contexts | Blocked by default |
| Commands | Runtime command shortcuts | Not materialized; skills are preferred |

Official references: [Memory](https://code.claude.com/docs/en/memory),
[Settings](https://code.claude.com/docs/en/settings),
[Skills](https://code.claude.com/docs/en/skills),
[Plugins](https://code.claude.com/docs/en/plugins),
[Hooks](https://code.claude.com/docs/en/hooks),
[MCP](https://code.claude.com/docs/en/mcp), and
[Subagents](https://code.claude.com/docs/en/sub-agents).

## Source Contract

| Source | Purpose |
|--------|---------|
| `src/adapters/claude/CLAUDE.md` | Short target root instruction file |
| `src/adapters/claude/skills/tes-guidelines/SKILL.md` | Claude skill source |
| `src/adapters/claude/skills/tes-*/SKILL.md` | Project skill source |
| `src/adapters/claude/plugin/plugin.json` | Plugin metadata source |
| `src/adapters/claude/plugin/marketplace.json` | Local marketplace metadata source |

`CLAUDE.md` is guidance, not enforcement. Rules that must block tools,
network, files, or execution belong in Claude settings or hooks after a
dedicated decision.

## Packaging Rules

- The materialized target root is `dist/adapters/claude/**`.
- Project installs must include `.claude/skills/tes-*/SKILL.md`; Claude Code
  discovers these as project skills and exposes direct slash names such as
  `/tes-init`, `/tes-setup`, and `/tes-cortex`.
- Plugin metadata stays in `src/adapters/claude/plugin/**` as a source-only
  template; default project installs must not write `.claude-plugin/**` or root
  `skills/**`.
- If an older target still has `.claude-plugin/**` or root `skills/**`, TES
  removes the paths only when they are TES-owned/generated or empty. Ambiguous,
  modified, non-TES, or secret-like content is preserved, backed up under
  `.tes/bk/**`, and returned as `NEEDS_REVIEW`.
- `/tes-*` is the preferred cross-tool TES trigger vocabulary across Codex,
  Claude Code, and Cursor. Claude project installs expose skill-backed direct
  slash names such as `/tes-init`, `/tes-setup`, `/tes-update`,
  `/tes-align`, `/tes-open-obsidian`,
  `/tes-prospect`, `/tes-mine`, `/tes-cortex`, `/tes-mcp`,
  `/tes-field-reports`, `/tes-doctor`, `/tes-adapter`, and `/tes-bench`;
  grouped triggers such as `/tes-curate` route through their owning skills
  instead of a one-file-per-command package.
  `/tes:*` forms remain compatible TES intent aliases. If Claude receives
  `/tes:init` or `/tes:update` as invalid slash text, treat it as the matching
  TES intent and continue through the TES skill or bootloader route instead of
  asking the user to choose a hypothesis.
- `tes init` and natural init command-prompts route to `tes-init`.
  `Atualizar TES`, `atualizar TES`, `tes update`, and natural update prompts
  route to `tes-update`. `tes align`, `align TES`, `align this project`, `alinhar TES`,
  `alinhar projeto`, and natural alignment prompts route to `tes-align`.
  `open Obsidian`, `open this project in Obsidian`, `abrir Obsidian`, and
  `abrir no Obsidian` route to `tes-open-obsidian`.
- `/tes-prospect` and `/tes-mine` are direct explicit-invocation predictive
  skills. Their `/tes:prospect` and `/tes:mine` aliases are compatible intent
  text, but broad natural-language descriptions must not activate them. Once
  invoked, each skill may operate proactively and must honor its cognitive
  brake.
- When installing into an existing project, back up a divergent `CLAUDE.md`
  under `.tes/bk/**`, apply the clean bootloader, recover useful semantics into
  `docs/agents/**`, and still install TES-owned assets under
  `.claude/skills/**`.
- Hooks, write-capable MCP, and subagents must not be added to the default
  plugin.
- The installer may add a project `SessionStart` hook that runs the local TES
  post-install routine and returns concise `additionalContext`; this hook is
  separate from plugin packaging and must stay idempotent.
- Read-only Cortex MCP is activated by the assisted installer through
  project-scoped `.mcp.json`, not plugin metadata.
- Source-only plugin retention and target-install omission are certified by
  `python3 scripts/claude_plugin_oracle.py --self-test`.
- A publishable Claude marketplace package still requires a separate
  distribution oracle before certification.

## Sensitive Surface Register

| Surface | Risk | Default |
|---------|------|---------|
| Settings | Can enforce or deny runtime behavior | Out of package |
| Hooks | Run commands with user permissions | Out of package |
| MCP | Adds external tools, auth, and lifecycle | Read-only Cortex only via installer |
| Subagents | Can inherit tools and act automatically | Out of package |
| Marketplace | Can distribute stale or unsafe packages | Local metadata only |

## Validation

Run:

```bash
npm run materialize:claude
npm run materialize:check
python3 scripts/claude_plugin_oracle.py --self-test
npm run commit:check
```

Claude local adapter alignment is complete when the generated tree installs
only project runtime surfaces and the source-only plugin oracle passes.
Marketplace publication and global desktop registration remain explicit
non-claims.
