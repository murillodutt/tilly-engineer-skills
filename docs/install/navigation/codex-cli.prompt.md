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
navigation_mode_preference: command-navigation

## Platform Reading

Codex CLI does not currently have a certified native Tilly menu-card contract.
The installer therefore treats CLI navigation as text-first.

## Renderer Order

1. Use command navigation from `common.prompt.md`.
2. If a custom harness wraps Codex CLI with function calling and a labeled menu
   renderer, that harness may render the same navigation intent natively.
3. The harness must return the stable command string, not display labels only.
4. Never render a naked sequence such as `1, 2, 3`.

## Evidence

Record:

```text
navigation_renderer: codex-cli
navigation_mode: command-navigation | custom-function
navigation_library: tilly-navigation@0.1.0
```
