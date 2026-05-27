---
name: tes-doctor
description: Use when the user says /tes-doctor, /tes:doctor, /tes:check, /tes:certify, or asks to validate, health-check, certify, or prepare a Tilly Engineer Skills commit.
---

# TES Doctor

`/tes-doctor` and `/tes:doctor` are shortcuts for installed-target and
package-source health checks. Use `/tes:check` and `/tes:certify` as aliases.

## Context Gate

Before choosing a command, classify the current workspace:

- **Installed target**: `.tes/bin/**` exists, or TES bootloaders/skills are
  installed into a project that is not the `tilly-engineer-skills` source
  package.
- **Package source**: `package.json` names `tilly-engineer-skills`, and the
  maintainer scripts plus adapter source tree are present.

Read `package.json` before recommending project scripts. A command is usable
only when the current workspace exposes it or the installed helper exists.

## Gate Selection

Run the smallest gate that proves the claim:

| Context | Claim | Typical oracle |
|---------|-------|----------------|
| installed target | TES runtime is installed | `python3 .tes/bin/tes_install.py status --target .` |
| installed target | project context is healthy | `python3 .tes/bin/project_context_oracle.py --target .` |
| installed target | project alignment is healthy | `python3 .tes/bin/project_alignment_oracle.py --target .` |
| installed target | Mantra Gate adoption is healthy | `python3 .tes/bin/mantra_gate_adoption_oracle.py --target .` (health/read-only) |
| installed target | target exposes a health gate | run the discovered script, for example `pnpm run gate:doctor` or `npm run gate:doctor` |
| installed target | staged changes are commit-ready | run discovered `gate:staged`; otherwise use available project gates and `git diff --check` |
| installed target | push readiness | run discovered `gate:push` plus `python3 .tes/bin/mantra_gate_adoption_oracle.py --target . --commit-push`; otherwise report `NOT_AVAILABLE` instead of inventing one |
| installed target | Mantra Gate history needs review | `python3 .tes/bin/mantra_gate_adoption_oracle.py --target . --audit-history` |
| package-source | package shape is valid | `npm run validate` |
| package-source | docs stay modular | `npm run docs:size` |
| package-source | TDS is aligned | `npm run tds:validate` |
| package-source | Cortex core works | `npm run cortex:self-test` |
| package-source | MCP helper works | `npm run mcp:self-test` and `npm run cortex:mcp:self-test` |
| package-source | Field Reports works | `npm run field-reports:self-test` |
| package-source | Mantra Gate adoption works | `npm run mantra-gate:adoption:self-test` |
| package-source | adapters materialize | `npm run materialize:check` |
| package-source | platform surfaces align | `npm run platform:surface:check` |
| package-source | final local closure | `npm run commit:check` |

## MCP Fallback

When `/tes-doctor` is asked to validate, repair, install, or certify MCP, it
acts as a fallback for `/tes-mcp` instead of stopping at a health report.

Use this sequence:

1. Test first.
   - Installed target: run `python3 .tes/bin/cortex_mcp.py --self-test` when
     the helper exists.
   - Package source: run `npm run mcp:self-test` and
     `npm run cortex:mcp:self-test`.
2. Identify the route. Use the active host route when obvious; otherwise use
   `all` so Codex, Claude, Cursor, and VS Code project MCP configs are covered.
3. Dry-run repair when changing files is not yet authorized:
   `python3 .tes/bin/install_mcp.py --target . --adapter all --dry-run --overwrite --json-only`.
   If the installed helper is unavailable, use
   `python3 <tes-package>/scripts/install_mcp.py --target . --adapter all --dry-run --overwrite --json-only`.
4. Repair or install only when the user requested repair/install or otherwise
   authorized writes:
   `python3 .tes/bin/install_mcp.py --target . --adapter all --overwrite --yes`.
   In the package source, use
   `python3 scripts/install_mcp.py --target <project> --adapter all --overwrite --yes`.
5. Certify the final MCP registration by checking the installer result
   `config_registrations`, rerunning `python3 .tes/bin/cortex_mcp.py --self-test`
   when installed, and confirming the expected project-scoped config path:
   `.codex/config.toml`, `.mcp.json`, `.cursor/mcp.json`, or `.vscode/mcp.json`.

Report `NOT_AVAILABLE` if neither the installed helper nor a TES package source
installer is available. Report `NEEDS_REVIEW` for conflicting MCP entries when
`--overwrite` is not authorized.

## Rules

- Do not run heavy gates when a narrow oracle proves the claim.
- Do not certify skipped commands as passing.
- Do not certify unavailable commands. Report `NOT_AVAILABLE`, `BLOCKED`, or
  `NEEDS_REVIEW` with the missing script/helper named.
- In an installed target, prefer project-owned gates discovered from
  `package.json` before generic package-source commands.
- Before commit in an installed target, prefer discovered `gate:staged`; in the
  TES package source, prefer `npm run commit:check`.
- For closure, commit, or push claims, treat Mantra Gate adoption statuses
  `BYPASS_SUSPECTED`, `NEEDS_REVIEW`, and `BLOCKED` as stop conditions.
- For read-only `/tes-doctor`, do not promote historical gate records to a
  current blocker; use `--audit-history` only when the user asks for explicit
  history audit.
- Do not edit global MCP config. The fallback may touch only `.tes/bin/**` and
  project-scoped MCP config after write authorization.
- After commit, rerun the principal gate when the user asks for sealed closure.
