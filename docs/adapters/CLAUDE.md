---
tds_id: adapters.claude
tds_class: adapter
status: active
consumer: claude code adopters and package maintainers
source_of_truth: true
evidence_level: L2
tver: 0.2.0
---

# Claude Adapter

This document governs the Claude Code derivation of Tilly Engineering
Discipline.

The Claude adapter is aligned behaviorally with Codex and Cursor, but it must
use Claude-native surfaces instead of copying Codex packaging.

## Official Surfaces

| Surface | Role | Package Status |
|---------|------|----------------|
| `CLAUDE.md` | Persistent project guidance loaded as memory | Included |
| `skills/**` | Reusable workflows with `SKILL.md` frontmatter | Included |
| `.claude-plugin/**` | Distribution metadata | Included as source, not published |
| Settings | Enforcement and permission policy | Documented only |
| Hooks | Operational enforcement scripts | Blocked by default |
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
| `src/adapters/claude/skills/tilly-guidelines/SKILL.md` | Claude skill source |
| `src/adapters/claude/skills/tilly-*/SKILL.md` | Command-shortcut skills |
| `src/adapters/claude/plugin/plugin.json` | Plugin metadata source |
| `src/adapters/claude/plugin/marketplace.json` | Local marketplace metadata source |

`CLAUDE.md` is guidance, not enforcement. Rules that must block tools,
network, files, or execution belong in Claude settings or hooks after a
dedicated decision.

## Packaging Rules

- The materialized plugin root is `dist/adapters/claude/**`.
- `.claude-plugin/plugin.json` must not depend on files outside the plugin
  root.
- Skill paths in plugin metadata must be root-relative, such as
  `skills/tilly-guidelines`, not `../skills/tilly-guidelines`.
- `/tilly:*` shortcuts map to Claude skills and then to deterministic oracles:
  `tilly-init`, `tilly-cortex`, `tilly-mcp`, `tilly-doctor`, `tilly-adapter`,
  and `tilly-bench`.
- Hooks, write-capable MCP, and subagents must not be added to the default
  plugin.
- Read-only Cortex MCP is activated by the assisted installer through
  project-scoped `.mcp.json`, not plugin metadata.
- Local target plugin shape is certified by
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

Claude local adapter alignment is complete when the generated tree is
root-contained and the local plugin oracle passes. Marketplace publication and
global desktop registration remain explicit non-claims.
