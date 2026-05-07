---
tds_id: install.command_triggers
tds_class: adapter
status: active
consumer: adopters, installing agents, and package maintainers
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Tilly Command Triggers

Tilly commands are not the user interface. The user interface is an intent in
the current agent window; scripts and npm aliases are deterministic oracles the
agent invokes when the runtime exposes local tools.

## Trigger Matrix

| Trigger | User intent | Primary oracles | Writes |
|---------|-------------|-----------------|--------|
| `/tilly:init` | install, update, audit, or recertify Tilly in a project | `tilly_init.py`, assisted installer, install smoke, MCP install | `docs/agents/**`, Cortex, runtime bootloaders, project MCP config |
| `/tilly:cortex` | inspect, query, audit, rebuild, learn, reflect, or apply Cortex memory | `cortex.py`, read-only Cortex MCP | Cortex files only when authorized |
| `/tilly:mcp` | activate or verify read-only Cortex MCP | `install_mcp.py`, `cortex_mcp.py`, MCP smoke | `.tilly/bin/**` and project-scoped MCP config |
| `/tilly:doctor` | health-check, certify, or prepare a commit | validation, TDS, doc-size, platform, materialization, commit gates | none unless evidence is explicitly requested |
| `/tilly:adapter` | materialize, dry-run, retrofit, or install adapter surfaces | `materialize_adapter.py`, `install_adapter.py`, adapter oracles | adapter files only after review or approval |
| `/tilly:bench` | plan, run, or converge context-mesh benchmarks | benchmark plan/run/converge scripts | benchmark evidence artifacts |

Aliases:

```text
/tilly:recall  -> /tilly:cortex recall
/tilly:learn   -> /tilly:cortex learn
/tilly:reflect -> /tilly:cortex reflect
/tilly:check   -> /tilly:doctor
/tilly:certify -> /tilly:doctor
```

## Classification

| Command family | Runtime role |
|----------------|--------------|
| `python3 scripts/*.py ...` | portable oracle called by the active agent |
| `npm run ...` | package-local alias for the same oracles |
| MCP tools | read-only access surface, preferred for recall/read/reflection |
| skills | user-intent routers in runtimes that support skills |
| rules | always-on intent routers where skills are not native |
| hooks | Git-event gates, not general executors |

## No-Go

- Do not create one slash command per script.
- Do not certify a command that was skipped or blocked.
- Do not call SQLite, MCP, or generated output memory.
- Do not run write operations such as adapter install, MCP activation, Cortex
  apply, materialization, or benchmark artifact updates without a clear target
  and authorization.
