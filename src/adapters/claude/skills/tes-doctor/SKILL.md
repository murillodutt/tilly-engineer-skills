---
name: tes-doctor
description: Use when the user says /tes-doctor, /tes:doctor, /tes:check, /tes:certify, or asks to validate, health-check, certify, or prepare a Tilly Engineer Skills commit.
license: MIT
---

# TES Doctor

`/tes-doctor` is the preferred shared TES trigger for installed-target and package-source health checks. `/tes:doctor`, `/tes:check`, and `/tes:certify` are compatible TES intent aliases if the host reports them as invalid slashes.

## Module Map

| Surface | Load when |
|---------|-----------|
| `docs/CONTRACT-HISTORY.md` | Workspace classification or oracle selection |

## Context Gate

Before choosing a command, classify the current workspace:

- **Installed target**: `.tes/bin/**` exists, or TES bootloaders/skills are installed into a project that is not the `tilly-engineer-skills` source package.
- **Package source**: `package.json` names `tilly-engineer-skills`, and the maintainer scripts plus adapter source tree are present.

Read `package.json` before recommending project scripts. A command is usable only when the current workspace exposes it or the installed helper exists.

## Gate Selection

Run the smallest gate that proves the claim:

| Context | Claim | Typical oracle |
|---------|-------|----------------|
| installed target | TES runtime is installed | `python3 .tes/bin/tes_install.py status --target .` |
| installed target | installed certification is clean or partial | `python3 .tes/bin/installed_certification_oracle.py --target . --json-only` |
| installed target | project context is healthy | `python3 .tes/bin/project_context_oracle.py --target .` |
| installed target | project alignment is healthy | `python3 .tes/bin/project_alignment_oracle.py --target .` |
| installed target | Mantra Gate adoption is healthy | `python3 .tes/bin/mantra_gate_adoption_oracle.py --target .` (health/read-only) |
| installed target | target exposes a health gate | run the discovered script, for example `pnpm run gate:doctor` or `npm run gate:doctor` |
| installed target | staged changes are commit-ready | run discovered `gate:staged`; otherwise use available project gates and `git diff --check` |
| installed target | push readiness | run discovered `gate:push` plus `python3 .tes/bin/mantra_gate_adoption_oracle.py --target . --commit-push`; otherwise report `NOT_AVAILABLE` instead of inventing one |
| installed target | Mantra Gate history needs review | `python3 .tes/bin/mantra_gate_adoption_oracle.py --target . --audit-history` |
| installed target | a stale/schema-invalid Mantra Gate record blocks certification | `python3 .tes/bin/field_reports.py prune-invalid-mantra-gates --target .` (quarantines invalid ledger records, then recertify) |
| package-source | package shape is valid | `npm run validate` |
| package-source | docs stay modular | `npm run docs:size` |
| package-source | TDS is aligned | `npm run tds:validate` |
| package-source | Cortex core works | `npm run cortex:self-test` |
| package-source | MCP helper works | `npm run mcp:self-test` and `npm run cortex:mcp:self-test` |
| package-source | Field Reports works | `npm run field-reports:self-test` |
| package-source | Mantra Gate adoption works | `npm run mantra-gate:adoption:self-test` |
| package-source | adapters materialize | `npm run materialize:check` |
| package-source | platform surfaces align | `npm run platform:surface:check` |
| package-source | staged changes are commit-ready | `npm run commit:check` |
| package-source | full local closure (explicit) | `npm run commit:closure` |

## MCP Fallback

When `/tes-doctor` is asked to validate, repair, install, or certify MCP, it acts as a fallback for `/tes-mcp` instead of stopping at a health report. Normal first registration for Codex, Claude Code, and Cursor belongs to the `npx`/`bunx` installer; doctor handles MCP drift, failed health, explicit repair/install requests, and host recognition evidence.

Use this sequence:

1. Test first.
   - Installed target: run `python3 .tes/bin/cortex_mcp.py --self-test` when the helper exists.
   - Package source: run `npm run mcp:self-test` and `npm run cortex:mcp:self-test`.
2. Identify the route. Use the active host route when obvious; otherwise use `all` so Codex, Claude, Cursor, and VS Code project MCP configs are covered.
3. Dry-run repair when changing files is not yet authorized: `python3 .tes/bin/install_mcp.py --target . --adapter all --dry-run --overwrite --json-only`. If the installed helper is unavailable, use `python3 <tes-package>/scripts/install_mcp.py --target . --adapter all --dry-run --overwrite --json-only`.
4. Repair or install only when the user requested repair/install or otherwise authorized writes: `python3 .tes/bin/install_mcp.py --target . --adapter all --overwrite --yes`. In the package source, use `python3 scripts/install_mcp.py --target <project> --adapter all --overwrite --yes`.
5. Certify file registration by checking the installer result `config_registrations`, rerunning `python3 .tes/bin/cortex_mcp.py --self-test` when installed, and confirming the expected project-scoped config path: `.codex/config.toml`, `.mcp.json`, `.cursor/mcp.json`, or `.vscode/mcp.json`.
6. Certify host recognition separately. Report `config_present`, `server_self_test_pass`, `protocol_handshake_pass`, `host_listed`, `host_connected`, or `session_restart_required` instead of collapsing them into one pass/fail claim.
   - Codex: run `codex mcp list` from the target project when available. If it lists `tes-cortex` but the current Codex thread cannot use the tools, report `session_restart_required` or workspace mismatch.
   - Cursor and VS Code: after valid project config, the host may still need reload, approval, enablement, or reconnect before `host_connected`.
   - Claude Code: use the host MCP manager or `/mcp` evidence when available.

Report `NOT_AVAILABLE` if neither the installed helper nor a TES package source installer is available. Report `NEEDS_REVIEW` for conflicting MCP entries when `--overwrite` is not authorized.

## Installed Certification Repair

When `/tes-doctor` is asked to repair installed TES health, run `installed_certification_oracle.py` first and preserve its distinction between `PASS`, `PARTIAL`, `NEEDS_REVIEW`, and `BLOCKED`. MCP `PASS` does not certify the install if Mantra Gate adoption, command trigger parity, quality-gate path, hygiene, or provenance is partial.

Safe repair order:

1. Read-only classify with `python3 .tes/bin/installed_certification_oracle.py --target . --json-only`.
2. If Mantra Gate or trigger surfaces are degraded and the user authorized repair, refresh TES-owned runtime files with the installed package route rather than editing generated target mirrors by hand.
3. If `.tes/postinstall.json` is `needs_review`, repair only the focused blocker, then run `python3 .tes/bin/tes_install.py postinstall --target . --recover-needs-review`.
4. Rerun `installed_certification_oracle.py`; report `PARTIAL` instead of claiming clean certification when any non-MCP component still fails.

## Contract-Symmetry Repair Routes

When the failure belongs to the postinstall recovery symmetry family, keep the same detected fact, status word, repair route, and Field Report hint aligned:

| Failure family | Doctor route |
|----------------|--------------|
| context oracle mismatch | Run `project_context_oracle.py`, preserve its structured failures, then rerun `/tes-init` or postinstall recovery only for that blocker. |
| stale quality-gate path | Run `tes_legacy_retirement.py plan`; if authorized, apply it to replace retired discipline oracle paths, then recertify. |
| missing Mantra Gate route | Run `mantra_gate_adoption_oracle.py`; repair bootloader-to-owner-skill routing through the TES adapter/update route, then recertify. |
| trigger parity drift | Run `command_trigger_oracle.py`; refresh TES-owned trigger surfaces through the adapter/update route, not by hand-editing installed mirrors. |
| residue | Run installed certification artifact hygiene; remove OS residue from source/materialized setup surfaces and rebuild only when authorized. |
| inherited-context state | See Inherited Context Recovery below. |

## Inherited Context Recovery

When install inherited a pre-existing `CLAUDE.md` / `AGENTS.md`, the root is a thin TES-rendered root (a `TES:CORE` block plus an `@docs/agents/PROJECT-CONTEXT.md` import for Claude, or a materialized `TES:PROJECT-OVERLAY` block for Codex), the human context lives in `docs/agents/PROJECT-CONTEXT.md`, and the original is archived as `<root>.bak-<stamp>`. Explain this state instead of telling the user to hand-overwrite the thin root.

Routes:

- **Verify non-loss.** The archive is the source of truth. Run `python3 .tes/bin/context_distill_coverage_oracle.py --bak <root>.bak-<stamp> --source docs/agents/PROJECT-CONTEXT.md`. `OVERLAY_COVERED` means every human unit is covered or discarded-with-reason; `NEEDS_REVIEW_COVERAGE` names the lost unit — repair the canonical source, do not overwrite the root.
- **Optimize the overlay.** For an opt-in condense/sanitize pass, route to `/tes-context-distill` (the judgment phase); never hand-edit a materialized overlay block — the next render overwrites it.
- **Recover the original.** The pre-inheritance root is restored on uninstall (`tes_install.py uninstall` restores `<root>.bak-<stamp>` byte-faithful). To recover it without uninstalling, copy the latest `<root>.bak-<stamp>` back over the root only after the user confirms they want the thin render gone.
- **Do not** treat the thin root as drift to overwrite, or delete the `<root>.bak-<stamp>` archive — it is both the non-loss oracle and the restore source.

## Rules

- Do not run heavy gates when a narrow oracle proves the claim.
- Do not certify skipped commands as passing.
- Do not certify unavailable commands. Report `NOT_AVAILABLE`, `BLOCKED`, or `NEEDS_REVIEW` with the missing script/helper named.
- In an installed target, prefer project-owned gates discovered from `package.json` before generic package-source commands.
- Before commit in an installed target, prefer discovered `gate:staged`; in the TES package source, prefer `npm run commit:check`. Use `npm run commit:closure` only when the user explicitly requests full closure, release certification, or a seal claim.
- For closure, commit, or push claims, treat Mantra Gate adoption statuses `BYPASS_SUSPECTED`, `NEEDS_REVIEW`, and `BLOCKED` as stop conditions.
- For read-only `/tes-doctor`, do not promote historical gate records to a current blocker; use `--audit-history` only when the user asks for explicit history audit.
- Do not edit global MCP config. The fallback may touch only `.tes/bin/**` and project-scoped MCP config after write authorization.
- After commit, rerun `commit:closure` when the user asks for sealed closure.
