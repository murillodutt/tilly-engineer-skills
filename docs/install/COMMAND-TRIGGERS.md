---
tds_id: install.command_triggers
tds_class: adapter
status: active
consumer: adopters, installing agents, and package maintainers
source_of_truth: true
evidence_level: L2
tver: 0.4.3
---

# TES Command Triggers

TES commands are not the user interface. The user interface is an intent in
the current agent window; scripts and npm aliases are deterministic oracles the
agent invokes when the runtime exposes local tools.

All adapters share the same preferred user triggers: `/tes-init`,
`/tes-update`, `/tes-cortex`, `/tes-mcp`, `/tes-doctor`, `/tes-adapter`, and
`/tes-bench`. Treat `/tes:*` forms as compatible TES intent aliases; if a host
reports one as an invalid slash, continue through the matching `tes-*`
skill/rule/spec instead of asking the user to restate the route.

## Trigger Matrix

| Trigger | User intent | Primary oracles | Writes |
|---------|-------------|-----------------|--------|
| `/tes-init` or `/tes:init` | install, update, audit, or recertify TES in a project | `root_context.py`, `tes_init.py`, assisted installer, install smoke, MCP install | `docs/agents/**`, Cortex, runtime bootloaders, project MCP config |
| `/tes-update` or `/tes:update` | update an already meshed project with the lowest-friction route | `tes_update.py`, `root_context.py`, `tes_legacy_retirement.py`, assisted installer, install smoke, MCP install | only selected TES surfaces after Step Zero and legacy retirement |
| `/tes-cortex` or `/tes:cortex` | inspect, query, audit, rebuild, curate, learn, reflect, or apply Cortex memory | `cortex.py`, read-only Cortex MCP | Cortex files only when authorized |
| `/tes-curate` or `/tes:curate` | classify Cortex memory quality risks without writing memory | `cortex.py curate-plan`, read-only `cortex_curate_plan` | no memory writes; CLI may refresh `.tes/cortex/semantic.sqlite` |
| `/tes-mcp` or `/tes:mcp` | activate or verify read-only Cortex MCP | `install_mcp.py`, `cortex_mcp.py`, MCP smoke | `.tes/bin/**` and project-scoped MCP config |
| `/tes-field-reports` or `/tes:field-reports` | inspect, drain, disable, or re-enable sanitized operational reports | `field_reports.py`, local `pre-push` hook | `.tes/field-reports/**`, `.git/info/exclude`, `.git/hooks/pre-push` |
| `/tes-doctor` or `/tes:doctor` | health-check, certify, or prepare a commit | validation, TDS, doc-size, platform, materialization, commit gates | none unless evidence is explicitly requested |
| `/tes-adapter` or `/tes:adapter` | materialize, dry-run, retrofit, or install adapter surfaces | `materialize_adapter.py`, `install_adapter.py`, adapter oracles | adapter files only after review or approval |
| `/tes-bench` or `/tes:bench` | plan, run, or converge context-mesh benchmarks | benchmark plan/run/converge scripts | benchmark evidence artifacts |

Aliases:

```text
tes init  -> /tes-init
tes update / update TES / Atualizar TES / atualizar TES -> /tes-update
initialize TES / install TES / recertify TES -> /tes-init
inicializar TES / instalar TES / recertificar TES -> /tes-init
/tes:recall  -> /tes-cortex recall
/tes:learn   -> /tes-cortex learn
/tes:reflect -> /tes-cortex reflect
/tes:curate  -> /tes-cortex curate-plan
/tes:check   -> /tes-doctor
/tes:certify -> /tes-doctor
```

## Classification

| Command family | Runtime role |
|----------------|--------------|
| `python3 scripts/*.py ...` | portable oracle called by the active agent |
| `npm run ...` | package-local alias for the same oracles |
| MCP tools | read-only access surface, preferred for recall/read/curation/reflection |
| skills | user-intent routers in runtimes that support skills |
| rules | always-on intent routers where skills are not native |
| hooks | Git-event gates for validation, no-write Cortex reflection/curation, and Field Reports drain |

## No-Go

- Do not create one slash command per script.
- Do not certify a command that was skipped or blocked.
- Do not claim latest-source certification when the installer reports
  `STALE_SOURCE` or `BLOCKED` source freshness.
- Do not claim `/tes-update` or `/tes:update` is `CURRENT` while helper contract parity is
  `STALE_HELPERS` or `BLOCKED`.
- Do not record Field Reports from exploratory `/tes-update` or `/tes:update` probes; use
  `--record-field-report` only on the final certification probe.
- Do not commit or push after a helper overwrite until a post-Layer Zero final
  recorded probe shows `helper_contract_status=PASS`,
  `update_available=False`, and `recommended_update_scope=none`.
- Do not use MCP config activation to repair stale helpers; run the helper-only
  Layer Zero route first.
- Do not call SQLite, MCP, or generated output memory.
- Do not call `.tes/cortex/semantic.sqlite` memory; it is only derived
  curation cache.
- Do not overwrite root runtime files before `root_context.py` has preserved or
  rejected project-owned instructions.
- Do not copy new TES assets over old runtime surfaces while
  `tes_legacy_retirement.py audit` still reports active legacy.
- Do not treat Field Reports, GitHub issues, outbox, or hooks as project truth.
- Do not assume a silent pre-push hook created no upstream issue; verify
  `.tes/field-reports/receipts/**` or `field_reports.py status`.
- Field Reports also has a GitHub receiver gate: issue template, schema oracle,
  labels, and quarantine workflow.
- Do not run write operations such as adapter install, MCP activation, Cortex
  apply, materialization, or benchmark artifact updates without a clear target
  and authorization.
