---
tds_id: install.navigation.claude_code
tds_class: adapter
status: active
consumer: installing LLMs in Claude Code
source_of_truth: true
evidence_level: L2
---

# Claude Code Navigation Renderer

navigation_renderer: claude-code
navigation_mode_preference: AskUserQuestion

## Platform Reading

Claude Code supports user input through `AskUserQuestion` in hosts that expose
that tool. Its documented limits are 1-4 questions per call and 2-4 options per
question. Some hosts or subagent contexts may not expose the tool.

## Renderer Order

1. Use `AskUserQuestion` only when it is available in the active host and the
   intent fits the documented limits.
2. If the intent has more than four options, use command navigation from
   `common.prompt.md`.
3. If `AskUserQuestion` is unavailable, use command navigation.
4. Never show the AskUserQuestion JSON payload to the user.

## AskUserQuestion Mapping

For a compatible single-select intent:

```text
questions[0].question = intent.question
questions[0].header = intent.header
questions[0].multiSelect = false
options[].label = intent option label, with "(Recommended)" on the default
options[].description = intent option description
```

Normalize the returned label back to the stable `command`. Treat free-text
`Other` responses as untrusted input.

## Evidence

Record:

```text
navigation_renderer: claude-code
navigation_mode: AskUserQuestion | command-navigation
navigation_library: tilly-navigation@0.1.1
```
