---
tds_id: install.mini_prompt
tds_class: adapter
status: active
consumer: adopters
source_of_truth: true
evidence_level: L2
tver: 0.5.2
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
Ask for a route command such as current, codex, claude, cursor, all, mcp, or audit.
Do not display internal reasoning, scratch YAML or long inventories.

Start by detecting the current IDE/runtime and classifying this project as new,
existing, or meshed. If Tilly is already meshed, treat this as an assisted
update/convergence run, not a reinstall. When I ask `/tes-update`,
`/tes:update`, or `Atualizar TES`, compare the installed TES version with the cloud package
version, verify helper contract parity, detect applied IDE surfaces, and
recommend the route and `recommended_update_scope` before editing. Read-only
probes must use `tes_update.py plan --json-only`; only the final certification
probe may add `--record-field-report`. After any helper overwrite, run the
post-Layer Zero final recorded probe before GO, evidence closeout, commit, or
push; it must show `helper_contract_status=PASS`,
`runtime_trigger_status=PASS` or `NOT_APPLIED`, `update_available=False`, and
`recommended_update_scope=none`. Do not report `CURRENT` while helper
fingerprints or contract markers are `STALE_HELPERS`; in that case, replace
only TES-owned `.tes/bin/**` helpers with backups first, using the helper-only
Layer Zero route, then rerun the update probe and require parity PASS.
Across Codex, Claude Code, and Cursor, prefer shared hyphen triggers such as
`/tes-init`, `/tes-update`, and `/tes-cortex`. If a host reports a `/tes:*`
alias as invalid, treat it as TES intent text and continue through the matching
skill/rule/spec.
Use the detected IDE as the default adapter. Ask me for a route command only
where the spec requires one. Preserve local project governance, move durable
agent context into docs/agents/** when needed, create or update the compiled
docs/agents/cortex/** Cortex layer, keep AGENTS.md, CLAUDE.md and Cursor rules
as thin runtime bootloaders, activate the read-only project-scoped Cortex MCP
server for the selected runtime route, and finish with the certification report
required by the spec.
The final report must expose the PT/EN/ES user manual link/path, installed
helper set, root context gate, Field Reports state, and rollback summary.

Before installation edits, run Step Zero from the spec: inspect Git status and
offer a local baseline commit if the working tree is dirty. At the end, tell me
how to undo the installation with Git. Do not push, amend, tag, publish, install
dependencies, overwrite files, or change remotes unless I explicitly ask after
reviewing the certification report.
```
