---
tds_id: install.mini_prompt
tds_class: adapter
status: active
consumer: adopters
source_of_truth: true
evidence_level: L2
tver: 0.5.4
---

# Tilly Context Installer Mini Prompt

Copy this into Codex, Claude Code, or Cursor while opened at the target project root:

```text
Install Tilly Engineer Skills as an assisted context mesh, not as blind file copying.

Read and follow this raw installer spec:

https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/docs/install/ASSISTED-CONTEXT-INSTALLER.prompt.md

Run in quiet installer mode: show compact progress, blockers and the final certification report only. When navigation is required, load the runtime navigation library from the spec, use native structured cards only when the current runtime safely supports them, otherwise render command navigation. Ask for a route command such as current, codex, claude, cursor, vscode, all, mcp, or audit. Do not display internal reasoning, scratch YAML or long inventories.

Start by detecting the current IDE/runtime and classifying this project as new, existing, or meshed. If Tilly is already meshed, treat this as an assisted update/convergence run, not a reinstall.

When I ask `/tes-update`, `/tes:update`, or `Atualizar TES`, compare the installed TES version with the cloud package version, verify helper contract parity, detect applied IDE surfaces, and recommend the route and `recommended_update_scope` before editing. Read-only probes must use `tes_update.py plan --json-only`; only the final certification probe may add `--record-field-report`. After any helper overwrite, run the post-Layer Zero final recorded probe before GO, evidence closeout, commit, or push; it must show `helper_contract_status=PASS`, `runtime_trigger_status=PASS` or `NOT_APPLIED`, `update_available=False`, and `recommended_update_scope=none`. Do not report `CURRENT` while helper fingerprints or contract markers are `STALE_HELPERS`; in that case, replace only TES-owned `.tes/bin/**` helpers with backups first, using the helper-only Layer Zero route, then rerun the update probe and require parity PASS.

Across Codex, Claude Code, and Cursor, prefer shared hyphen triggers such as `/tes-init`, `/tes-setup`, `/tes-update`, `/tes-goal-maestro`, `/tes-prospect`, `/tes-mine`, and `/tes-cortex`. If a host reports a `/tes:*` alias as invalid, treat it as TES intent text and continue through the matching skill/rule/spec. `/tes-setup` is the direct setup alias for `/tes-init`; `/tes-goal-maestro`, `/tes-prospect`, and `/tes-mine` require explicit invocation, and `tes-goal-maestro` may also route from a direct request to generate a maestral `/goal` prompt from a mature SPEC, Super SPEC, PRD, relational project plan, or accepted execution tree after internal tree, material-diff, material-continuation, semantic negative-grep, sequential ownership, and sync-status gates pass. Generated Super SPEC content is written to `GOAL-SUPER-SPEC-*.md` and summarized in chat instead of being pasted into the context window.

Use the detected IDE as the default adapter. Ask me for a route command only where the spec requires one. Stage the deterministic TES bundle under .tes/setup/<version>/ when update writes are needed, using the public ZIP and SHA-256 when available.

Before runtime writes, create a central .tes/bk/<timestamp>/ backup, apply a clean TES runtime, recover durable local governance semantics into docs/agents/**, analyze the project in depth and write docs/agents/PROJECT-CONTEXT.md as the initial project map, create the first-pass Obsidian-compatible operating mesh when missing, create or update the compiled docs/agents/cortex/** Cortex layer, keep active AGENTS.md, CLAUDE.md, CURSOR.md and Cursor rules as thin TES bootloaders, install TES-owned runtime capabilities such as /tes-align, /tes-goal-maestro, /tes-prospect, /tes-mine, and /tes-open-obsidian, activate the project-scoped Cortex MCP server for the selected runtime route with governed remember by default unless read-only was requested, and finish with the certification report required by the spec.

If package source is available, certify docs/agents/PROJECT-CONTEXT.md with project_context_oracle.py and the operating mesh with project_alignment_oracle.py before claiming Project context PASS; otherwise report those gates as BLOCKED or NEEDS_REVIEW with the reason.

Run discovered safe project quality gates such as lint, typecheck, test, build or CI-equivalent commands before GO; unsafe or unavailable gates must be BLOCKED or NEEDS_REVIEW with reason, not buried in Limits.

Treat tes_init.py as the deterministic scaffold and the active agent as the semantic refiner: for non-trivial projects, open strong anchors before claiming deep context, then refine the file or mark Project context NEEDS_REVIEW.

For `/tes-init`, run the Project-Start Gate before final reporting even when a preflight context check already passes. After helper-only or adapter repairs, run the installed `tes_init.py --target . --yes`, then certify with `project_context_oracle.py --target .` and `project_alignment_oracle.py --target .`.

If `.tes/postinstall.json` is `needs_review`, inspect the latest run, repair the focused blocker, then run `python3 .tes/bin/tes_install.py postinstall --target . --recover-needs-review` so the Project-Start recovery clears the sentinel only on PASS.

If `tes_update.py plan --json-only` exposes `continuation_plan.status=PENDING_APPROVAL`, do not close with a bare `NEEDS_REVIEW`. Include the required phases, approvals, write surfaces, commands, and final recorded probe so the next run can resume without abandoning the line.

The final report must expose the PT/EN/ES user manual link/path, installed helper set, root context gate, project context path, Field Reports state, and rollback summary.

Before installation edits, run Step Zero from the spec: inspect Git status and offer a local baseline commit if the working tree is dirty. At the end, tell me how to undo the installation with Git. Do not push, amend, tag, publish, install dependencies, overwrite files outside the selected TES clean-runtime route, overwrite root runtime files before .tes/bk/<timestamp>/manifest.json exists, or change remotes unless I explicitly ask after reviewing the certification report.
```
