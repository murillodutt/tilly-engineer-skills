---
tds_id: install.navigation.codex_cli
tds_class: adapter
status: active
consumer: installing LLMs in Codex CLI
source_of_truth: true
evidence_level: L2
---

# Codex CLI Navigation Renderer

navigation_renderer: codex-cli
navigation_mode_preference: request-user-input-or-command-navigation

## Platform Reading

Codex CLI may be connected to app-server or protocol surfaces that support
`request_user_input`, but availability is version, mode, and harness sensitive.
The installer therefore treats CLI navigation as text-first unless the active
tool schema proves structured input is available.

## Renderer Order

1. Inspect the active tool schema.
2. Use `request_user_input` only when it is exposed with labeled options in the
   current mode.
3. If only string questions are supported, embed command options in the prompt.
4. If a custom harness wraps Codex CLI with function calling and a labeled menu
   renderer, that harness may render the same navigation intent natively.
5. Otherwise use command navigation from `common.prompt.md`.
6. The harness must return the stable command string, not display labels only.
7. Never render a naked sequence such as `1, 2, 3`.

## Evidence

Record:

```text
navigation_renderer: codex-cli
navigation_mode: request-user-input | string-question | command-navigation | custom-function
navigation_library: tilly-navigation@0.1.1
```
