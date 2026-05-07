---
tds_id: install.navigation.generic
tds_class: adapter
status: active
consumer: Continue.dev, Aider, and other installing LLMs
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Generic Navigation Renderer

navigation_renderer: generic
navigation_mode_preference: command-navigation

## Platform Reading

Use this renderer when the active host is not Codex, Claude Code, Claude
Desktop, Cursor, or a certified API harness.

## Renderer Order

1. Use command navigation from `common.prompt.md`.
2. Keep the menu compact and command-labeled.
3. Do not use A/B/C or numeric labels unless each line also includes the stable
   command and the parser can map the response without ambiguity.

## Evidence

Record:

```text
navigation_renderer: generic
navigation_mode: command-navigation
navigation_library: tes-navigation@0.1.1
```
