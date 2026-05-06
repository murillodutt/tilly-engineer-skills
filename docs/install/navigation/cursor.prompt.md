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
navigation_mode_preference: ask-question-when-available

## Platform Reading

Cursor has project rules in `.cursor/rules/**`, native agent tools that vary by
mode, and ACP extension methods when another program drives Cursor. Do not
conflate those surfaces.

## Renderer Order

1. If the current Cursor tool schema includes `AskQuestion` or `ask_question`,
   use it for discrete trade-off decisions.
2. If the active integration is ACP, use `cursor-acp.prompt.md`.
3. If the tool is absent, mode-gated, or not clearly interactive, use command
   navigation from `common.prompt.md`.
4. Never use numbered-only choices.

## Evidence

Record:

```text
navigation_renderer: cursor
navigation_mode: ask-question | command-navigation
navigation_library: tilly-navigation@0.1.1
```
