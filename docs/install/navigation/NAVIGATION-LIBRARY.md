---
tds_id: install.navigation_library
tds_class: adapter
status: active
consumer: installing LLMs and adopters
source_of_truth: true
evidence_level: L2
---

# Assisted Installer Navigation Library

The assisted installer declares navigation as intent, then loads the smallest
runtime renderer that can present that intent safely.

```text
navigation intent -> runtime renderer -> answer parser -> installer action
```

The installer must not expose scratch JSON, hidden chain-of-thought, numbered
option fragments, or platform-specific internals to the user.

## Runtime Renderers

| Platform | Native support | Tilly renderer | Fallback |
|----------|----------------|----------------|----------|
| Claude Code CLI | Yes | `claude-code.prompt.md` | command navigation |
| Claude Agent SDK | Yes, same tool | `claude-code.prompt.md` | command navigation |
| Cursor | No certified native card | `cursor.prompt.md` | command navigation |
| Codex CLI | No certified native card | `codex-cli.prompt.md` | custom host function or command navigation |
| Codex app/IDE host | Host-dependent | `codex.prompt.md` | command navigation |
| Claude Desktop | No certified coding menu tool | `claude-desktop.prompt.md` | artifact or command navigation |
| Anthropic API direct | No UI without harness | `anthropic-api.prompt.md` | custom tool-use plus client-rendered UI |
| Continue.dev, Aider, other | No certified native card | `generic.prompt.md` | command navigation |

Different renderers are not drift. Drift occurs only when the same navigation
intent produces different installer actions.

Tilly command navigation uses named commands, not naked numbers. A host may add
ordinal decoration for accessibility, but the accepted answer remains the
stable command string.

## Basis

- Codex CLI documentation describes local interactive operation and repository
  access, but this package does not assume a native question-card tool exists
  in every Codex host:
  `https://developers.openai.com/codex/cli`
- Claude Code documents `AskUserQuestion` for clarifying questions and gives
  the 1-4 question / 2-4 option limits:
  `https://code.claude.com/docs/en/agent-sdk/user-input`
- Cursor documents project rules under `.cursor/rules/**`; this package does
  not currently certify a native installer menu API for Cursor:
  `https://docs.cursor.com/en/context/rules`

## Dynamic Loading

After detecting the runtime, load:

```text
docs/install/navigation/common.prompt.md
docs/install/navigation/<runtime>.prompt.md
```

Runtime file names:

```text
anthropic-api.prompt.md
codex.prompt.md
codex-cli.prompt.md
claude-code.prompt.md
claude-desktop.prompt.md
cursor.prompt.md
generic.prompt.md
```

If a runtime-specific file cannot be fetched, continue with
`common.prompt.md`. If the common file cannot be fetched, use the embedded
command navigation fallback in the main installer prompt.

## Intent Shape

Every menu starts as a compact semantic object:

```text
id: <stable-id>
type: single-select | multi-select
question: <question ending with ?>
header: <short chip label>
default: <recommended command>
options:
  - command: <machine-readable command>
    label: <user-facing label>
    recommended: true | false
    description: <honest trade-off>
```

The renderer may convert this shape to a native card, a terminal menu, or a
compact prose menu. It must preserve commands exactly.

## Evidence

The final certification report records:

```text
navigation_library: <common version>
navigation_renderer: <codex | claude-code | cursor | fallback>
navigation_mode: <native-card | command-navigation>
navigation_decisions:
  - id: <intent-id>
    selected: <command>
```

For installer certification, raw UI appearance is not the evidence. The
evidence is the selected command, the renderer used, and the resulting file
changes.
