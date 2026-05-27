---
tds_id: evidence.cortex_mcp_host_recognition_parity_20260527
tds_class: evidence
status: active
consumer: maintainers, installer authors, MCP operators, and release reviewers
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# Cortex MCP Host Recognition Parity

## Summary

A private canary project exposed a false-green class in MCP activation:
`tes-cortex` could be correctly written to project config and pass protocol
handshake, while a host UI still did not show the server until its own
recognition path reloaded or observed the correct workspace.

TES `0.3.142` narrows that gap. The installer now writes absolute Python,
script, target, and Codex `cwd` paths for all project MCP configs. `/tes-mcp`
and `/tes-doctor` now classify host recognition separately from config
registration, using the states `config_present`, `server_self_test_pass`,
`protocol_handshake_pass`, `host_listed`, `host_connected`, and
`session_restart_required`.

## Evidence

The canary confirmed the MCP server itself was not the blocker: direct stdio
handshake returned `tes-cortex-mcp`, version `0.3.141`, and fourteen tools.
`cortex_verify` returned `PASS`.

After direct project config repair with absolute command and target arguments,
Cursor and VS Code exposed the `tes-cortex` tool surface. Codex CLI listed the
project server from the target workspace, while an already-running Codex
session outside that workspace required workspace alignment or restart before
the in-app UI could be expected to show the project server.

## Product Change

The package-source installer now treats generated MCP command paths as part of
the registration contract. JSON runtimes and Codex TOML all receive absolute
commands and absolute target arguments. Codex additionally receives absolute
`cwd`.

Documentation and trigger oracles now prevent reports from calling MCP
activation fully functional when only a config file was written. Host
recognition is a distinct observation and may legitimately close as
`session_restart_required` when config, self-test, and protocol handshake pass
but the host has not reloaded or is observing another workspace.

## Oracles

The focused package-source checks for this change are:

```bash
python3 -m py_compile scripts/install_mcp.py scripts/command_trigger_oracle.py
python3 scripts/install_mcp.py --self-test
python3 scripts/command_trigger_oracle.py --self-test
```

Full closure remains governed by the package gates and private vocabulary
oracle before any release or commercial-use claim.

## Boundaries

This does not add global MCP mutation, hosted MCP, external memory storage,
automatic Cortex writes, write-capable tools beyond ADR 0002 governed remember,
or UI/runtime-specific control over host reload behavior.
