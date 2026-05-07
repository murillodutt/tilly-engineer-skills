---
tds_id: evidence.context_mesh.platform_surface_certification_2026_05_06
tds_class: evidence
status: active
consumer: certification reviewers and platform adapter maintainers
source_of_truth: false
evidence_level: L3
---

# Platform Surface Certification - 2026-05-06

## Decision

Result: `GO`

Claim:

```text
Tilly Engineer Skills v0.3.14 has certified local package alignment for the
Codex, Claude, and Cursor platform surfaces it claims.
```

This is a package-shape and contract certification. It is not a live IDE UI,
marketplace publication, or universal behavior-parity claim.

## Documentation Baseline

The oracle was aligned against official platform documentation:

| Area | Source |
|------|--------|
| Codex AGENTS.md | `https://developers.openai.com/codex/guides/agents-md` |
| Codex skills | `https://developers.openai.com/codex/skills` |
| Codex plugins | `https://developers.openai.com/codex/plugins` |
| Codex hooks | `https://developers.openai.com/codex/hooks` |
| Codex rules | `https://developers.openai.com/codex/rules` |
| Codex MCP | `https://developers.openai.com/codex/mcp` |
| Claude features | `https://code.claude.com/docs/en/features-overview` |
| Claude skills | `https://code.claude.com/docs/en/skills` |
| Claude plugins | `https://code.claude.com/docs/en/plugins-reference` |
| Claude hooks | `https://code.claude.com/docs/en/hooks` |
| Cursor rules | `https://docs.cursor.com/context/rules` |
| Cursor MCP | `https://docs.cursor.com/context/model-context-protocol` |
| MCP spec | `https://modelcontextprotocol.io/specification/latest` |

## Oracle

Command:

```bash
npm run platform:surface:check
```

Equivalent direct command:

```bash
python3 scripts/platform_surface_oracle.py --self-test
```

Observed result before final commit:

```text
[platform-surface] PASS
version=0.3.14
git_head=2a3a89df4ad758bb6588dcaee4a1665aa39c4d03
failures=[]
```

## Certified Surfaces

| Platform | Surface | Status | Evidence |
|----------|---------|--------|----------|
| Codex | agent | `certified` | `src/adapters/codex/AGENTS.md` |
| Codex | skill | `certified` | `src/adapters/codex/skills/tilly-*/SKILL.md` |
| Codex | plugin | `deferred` | Native platform support exists; Tilly ships local skill first. |
| Codex | hook | `git-governed` | `.githooks/pre-commit` |
| Codex | rules | `not-packaged` | No sandbox escalation rule is required by this package. |
| Codex | MCP | `certified` | `scripts/install_mcp.py` writes `.codex/config.toml`. |
| Claude | agent | `certified` | `src/adapters/claude/CLAUDE.md` |
| Claude | skill | `certified` | `src/adapters/claude/skills/tilly-*/SKILL.md` |
| Claude | plugin | `certified` | `src/adapters/claude/plugin/plugin.json` |
| Claude | hook | `deferred` | Native platform support exists; no plugin hook is claimed. |
| Claude | rules | `not-native` | Claude uses CLAUDE.md, permissions, hooks, skills, plugins, and MCP. |
| Claude | MCP | `certified` | `scripts/install_mcp.py` writes `.mcp.json`. |
| Cursor | agent | `certified` | `src/adapters/cursor/CURSOR.md` |
| Cursor | skill | `not-native` | Cursor rules are the portable instruction surface. |
| Cursor | plugin | `not-native` | No Cursor plugin package is claimed. |
| Cursor | hook | `git-governed` | `.githooks/pre-commit` |
| Cursor | rules | `certified` | `src/adapters/cursor/rules/tilly-guidelines.mdc` |
| Cursor | MCP | `certified` | `scripts/install_mcp.py` writes `.cursor/mcp.json`. |

## Criteria

| Criterion | Result |
|-----------|--------|
| Claimed surfaces exist in source | `GO` |
| Materialized adapter files preserve required surfaces | `GO` |
| Claude plugin manifests resolve locally | `GO` |
| Codex and Claude skills keep valid `SKILL.md` frontmatter | `GO` |
| Cursor rule keeps MDC frontmatter and `alwaysApply: true` | `GO` |
| MCP activation paths exist for Codex, Claude, and Cursor | `GO` |
| Git hook carries doc-size and Cortex reflection gates | `GO` |

## No-Claims

- No live marketplace publication is certified.
- No live IDE UI behavior is certified.
- No platform lifecycle hook is claimed when only `.githooks/pre-commit`
  exists.
- No Cursor skill/plugin parity is claimed because Cursor rules are the native
  portable surface.
- No Codex plugin package is claimed until a `.codex-plugin/plugin.json`
  package exists with its own oracle.

## Post-Gate

Keep `npm run platform:surface:check` inside `npm run commit:check` so every
future adapter, plugin, skill, MCP, hook, agent, or rule change is checked
against the platform-surface contract before certification.
