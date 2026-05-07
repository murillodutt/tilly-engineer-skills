---
tds_id: install.navigation.codex
tds_class: adapter
status: active
consumer: installing LLMs in Codex
source_of_truth: true
evidence_level: L2
tver: 0.2.0
---

# Codex Navigation Renderer

navigation_renderer: codex
navigation_mode_preference: request-user-input-when-available

## Platform Reading

Codex may run in the desktop app, IDE extension, CLI, app-server, or a
non-interactive automation path. Current Codex surfaces are not uniform.
Some expose `request_user_input` / `tool/requestUserInput`; others expose only
plain questions or no user-input tool in the active collaboration mode.

## Renderer Order

1. Inspect the active Codex tool schema first.
2. If `request_user_input` or `tool/requestUserInput` is available with labeled
   options, render the navigation intent through that tool.
3. If only string questions are supported, embed compact command options in the
   question text and parse the returned answer.
4. If the tool is unavailable, unavailable in the current mode, or would render
   as unlabeled numbers, use command navigation from `common.prompt.md`.
5. Never emulate a native card by printing raw JSON to the user.

## Native Mapping

When a structured input tool exists:

- one intent becomes one question;
- `header` is the chip/header;
- labels include the command in human-readable form;
- descriptions preserve trade-offs;
- recommended option is first;
- accepted answer is normalized back to the stable `command`.
- do not add a fake `Other` option if the harness injects one or exposes
  `isOther`.

If the tool has a limit below the number of options, fall back to command
navigation instead of splitting the intent silently.

For the current installer, the seven-option adapter route should remain command
navigation because common Codex structured-input shapes support fewer options.

## Evidence

Record:

```text
navigation_renderer: codex
navigation_mode: request-user-input | string-question | command-navigation
navigation_library: tes-navigation@0.1.1
```
