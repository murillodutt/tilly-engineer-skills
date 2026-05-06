---
tds_id: install.navigation.cursor_acp
tds_class: adapter
status: active
consumer: Cursor Agent Client Protocol harnesses
source_of_truth: true
evidence_level: L2
---

# Cursor ACP Navigation Renderer

navigation_renderer: cursor-acp
navigation_mode_preference: cursor-ask-question

## Platform Reading

Cursor ACP is a client/server boundary. Use this renderer only when another
program is driving Cursor through Agent Client Protocol methods such as
`cursor/ask_question`. Do not use ACP method names in normal Cursor project
rules unless the project is implementing an ACP client or server.

## Renderer Order

1. Use `cursor/ask_question` when the ACP client exposes it.
2. Map each Tilly option to `{ id, label }`; ACP does not carry per-option
   descriptions or previews.
3. Preserve the stable command in the option `id`.
4. Handle `answered`, `skipped`, and `cancelled`.
5. If ACP is unavailable, return to the host-specific Cursor renderer.

## Evidence

Record:

```text
navigation_renderer: cursor-acp
navigation_mode: cursor-ask-question
navigation_library: tilly-navigation@0.1.1
```
