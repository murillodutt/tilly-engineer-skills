---
tds_id: install.mini_prompt
tds_class: adapter
status: active
consumer: adopters
source_of_truth: true
evidence_level: L2
---

# Tilly Context Installer Mini Prompt

Copy this into Codex, Claude Code, or Cursor while opened at the target project
root:

```text
Install Tilly Engineer Skills as an assisted context mesh, not as blind file
copying.

Read and follow this raw installer spec:

https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md

Start by detecting the current IDE/runtime and classifying this project as new
or existing. Use the detected IDE as the default adapter. Ask me for a menu
choice only where the spec requires one. Preserve local project governance,
move durable agent context into docs/agents/**, keep AGENTS.md, CLAUDE.md and
Cursor rules as thin runtime bootloaders, and finish with the certification
report required by the spec.
```
