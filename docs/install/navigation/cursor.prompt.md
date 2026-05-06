---
tds_id: install.navigation.cursor
tds_class: adapter
status: active
consumer: installing LLMs in Cursor
source_of_truth: true
evidence_level: L2
---

# Cursor Navigation Renderer

navigation_renderer: cursor
navigation_mode_preference: command-navigation

## Platform Reading

Cursor has project rules in `.cursor/rules/**` and agent-oriented UI surfaces,
but this package does not currently certify a stable native question-card API
for assisted installer menus.

## Renderer Order

1. Use command navigation from `common.prompt.md`.
2. If a future Cursor host exposes a stable labeled-options question tool, it
   may be used only when it preserves command labels and evidence fields.
3. Never use numbered-only choices.

## Evidence

Record:

```text
navigation_renderer: cursor
navigation_mode: command-navigation
navigation_library: tilly-navigation@0.1.0
```
