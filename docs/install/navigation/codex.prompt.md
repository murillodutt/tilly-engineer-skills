---
tds_id: install.navigation.codex
tds_class: adapter
status: active
consumer: installing LLMs in Codex
source_of_truth: true
evidence_level: L2
---

# Codex Host Navigation Renderer

navigation_renderer: codex
navigation_mode_preference: native-card-when-available

## Platform Reading

Codex may run in the desktop app, IDE extension, CLI, or a non-interactive
automation path. The public Codex docs describe app, IDE, CLI, web and
automation surfaces. This renderer covers Codex hosts that expose a structured
user-input tool to the active agent.

For plain Codex CLI, use `codex-cli.prompt.md`.

## Renderer Order

1. If the active Codex host exposes a structured user-input tool with labeled
   options, render the navigation intent through that tool.
2. If the tool is unavailable, unavailable in the current mode, or would render
   as unlabeled numbers, use command navigation from `common.prompt.md`.
3. Never emulate a native card by printing raw JSON to the user.

## Native Mapping

When a structured input tool exists:

- one intent becomes one question;
- `header` is the chip/header;
- labels include the command in human-readable form;
- descriptions preserve trade-offs;
- recommended option is first;
- accepted answer is normalized back to the stable `command`.

If the tool has a limit below the number of options, fall back to command
navigation instead of splitting the intent silently.

## Evidence

Record:

```text
navigation_renderer: codex
navigation_mode: native-card | command-navigation
navigation_library: tilly-navigation@0.1.0
```
