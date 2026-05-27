---
tds_id: evidence.tes_doctor_mcp_fallback_20260527
tds_class: evidence
status: active
consumer: maintainers, installer authors, MCP operators, and release reviewers
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# TES Doctor MCP Fallback

## Summary

The VS Code MCP config parity fix made MCP registration validation strict, but
`/tes-doctor` still described MCP as a package-source health check rather than
an installed-target fallback repair lane. This left a practical support gap:
when the user asks the doctor to certify or repair a broken MCP install, the
skill must know how to test, repair, or install MCP without pretending skipped
commands passed.

The portable correction gives `/tes-doctor` a bounded MCP fallback path while
preserving `/tes-mcp` as the primary activation route.

## Mantra Gate

| Field | Record |
|-------|--------|
| `VERIFY` | Existing `/tes-doctor` skill had MCP source self-tests but no installed-target repair/install sequence. |
| `SCOPE` | `tes-doctor` skills, MCP helper payload, command-trigger oracle, install docs, public docs, bundle, and evidence. |
| `BEST_PATH` | Install `install_mcp.py` as a target helper and document `/tes-doctor` as fallback only when MCP health is the failing surface. |
| `DOCUMENT` | This report plus correlated install/MCP docs and current claims. |
| `ORACLE` | `install_mcp.py --self-test`, `command_trigger_oracle.py --self-test`, public bundle oracle, and package closure gates. |
| `RESOLVE` | Same in-flight `0.3.141` release identity, because no commit/tag/publish occurred before this correlated behavior landed. |
| `STATUS` | `PASS` after focused oracle and closure gates. |

## Contract

`/tes-doctor` now handles MCP fallback in this order:

1. Test with `cortex_mcp.py --self-test` or package MCP self-tests.
2. Select the active route, or `all` when the host route is unclear.
3. Dry-run `install_mcp.py --target . --adapter all --overwrite --json-only`
   when write authorization is not yet established.
4. Repair or install with `--yes` only after repair/install authorization.
5. Certify `config_registrations` and the project-scoped config path.

The fallback may write only `.tes/bin/**` and project-scoped MCP config. It
must not edit global MCP config, secrets, hooks, remotes, cloud settings, or
ungoverned MCP write tools.

## Evidence

`install_mcp.py` is now installed into `.tes/bin/**`, so an installed target can
repair a missing or broken project MCP config without requiring a source-package
checkout. Its self-test removes a VS Code MCP config from a neutral temporary
target, runs the installed `.tes/bin/install_mcp.py` fallback, and verifies that
`.vscode/mcp.json` is recreated with `servers.tes-cortex` in
`config_registrations`.

The command-trigger oracle now requires both Codex and Claude `tes-doctor`
skills to carry the MCP fallback contract, the installed helper repair command,
`config_registrations`, and the global MCP config lock.

## Closure

Focused oracles:

```bash
python3 -m py_compile scripts/install_mcp.py scripts/tes_bundle.py scripts/tes_update.py scripts/install_smoke.py scripts/public_bundle_oracle.py scripts/command_trigger_oracle.py
python3 scripts/install_mcp.py --self-test
python3 scripts/command_trigger_oracle.py --self-test
```

Status: `PASS`.
