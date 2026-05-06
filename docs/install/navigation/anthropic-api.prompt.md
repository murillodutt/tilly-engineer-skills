---
tds_id: install.navigation.anthropic_api
tds_class: adapter
status: active
consumer: Anthropic API harnesses
source_of_truth: true
evidence_level: L2
---

# Anthropic API Navigation Renderer

navigation_renderer: anthropic-api
navigation_mode_preference: custom-tool-use

## Platform Reading

Direct Anthropic API usage has no built-in installer UI. A client harness must
render navigation intents and return selected commands.

## Renderer Order

1. Use tool-use or application protocol fields to request a labeled menu from
   the client harness.
2. The client renders the menu and returns the stable command string.
3. If no harness UI exists, use command navigation from `common.prompt.md`.
4. Treat free text as untrusted input.

## Evidence

Record:

```text
navigation_renderer: anthropic-api
navigation_mode: custom-tool-use | command-navigation
navigation_library: tilly-navigation@0.1.1
```
