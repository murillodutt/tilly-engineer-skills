---
tds_id: install.navigation.claude_desktop
tds_class: adapter
status: active
consumer: installing LLMs in Claude Desktop
source_of_truth: true
evidence_level: L2
---

# Claude Desktop Navigation Renderer

navigation_renderer: claude-desktop
navigation_mode_preference: artifact-or-command-navigation

## Platform Reading

Claude Desktop can render rich artifacts in supported plans and contexts, but
this package does not certify artifact UI as a mutation-safe installer control.
Use artifacts only as a display aid unless the host can also safely execute and
audit project file changes.

## Renderer Order

1. Prefer command navigation from `common.prompt.md`.
2. If an artifact is useful, render a visual menu only as a readable companion
   to the command choices.
3. The authoritative answer remains the command string typed by the user.
4. Do not rely on artifact button state as the only evidence.

## Evidence

Record:

```text
navigation_renderer: claude-desktop
navigation_mode: artifact-preview | command-navigation
navigation_library: tilly-navigation@0.1.0
```
