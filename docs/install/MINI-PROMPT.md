---
tds_id: install.mini_prompt
tds_class: adapter
status: active
consumer: adopters
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Tilly Context Installer Mini Prompt

Copy this into Codex, Claude Code, or Cursor while opened at the target project
root:

```text
Install Tilly Engineer Skills as an assisted context mesh, not as blind file
copying.

Read and follow this raw installer spec:

https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md

Run in quiet installer mode: show compact progress, blockers and the final
certification report only. When navigation is required, load the runtime
navigation library from the spec, use native structured cards only when the
current runtime safely supports them, otherwise render command navigation.
Ask for a route command such as current, codex, claude, cursor, all, or audit.
Do not display internal reasoning, scratch YAML or long inventories.

Start by detecting the current IDE/runtime and classifying this project as new
or existing. Use the detected IDE as the default adapter. Ask me for a route
command only where the spec requires one. Preserve local project governance,
move durable agent context into docs/agents/**, create the compiled
docs/agents/cortex/** Cortex layer, keep AGENTS.md, CLAUDE.md and Cursor rules
as thin runtime bootloaders, and finish with the certification report required
by the spec.

Before installation edits, run Step Zero from the spec: inspect Git status and
offer a local baseline commit if the working tree is dirty. At the end, tell me
how to undo the installation with Git. Do not push, amend, tag, publish, install
dependencies, overwrite files, or change remotes unless I explicitly ask after
reviewing the certification report.
```
