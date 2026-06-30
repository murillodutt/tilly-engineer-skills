---
tds_id: evidence.canary_gap_repair_admission_alignment.preflight_20260630
tds_class: evidence
status: active
consumer: maintainers, canary operators
source_of_truth: false
evidence_level: L2
---

# PREFLIGHT — Read-Only Gap Reconfirmation

CANARY_ROOT=/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532
Generated: 2026-06-30T15:24:57Z

## cursor
```
-- git rev-parse --is-inside-work-tree --
true
-- hook/gate files --
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.git/hooks/pre-push
-- postinstall.json --
{
  "version": "0.3.231",
  "state": "complete",
  "last_status": "PASS",
  "advisories": [
    {
      "code": "mesh.scaffold_only",
      "message": "O mesh é apenas scaffold inicial — rode /tes-align para refinamento semântico."
    },
    {
      "code": "cortex.empty",
      "message": "Cortex vazio — capacidade de memória durável não está sendo usada."
    }
  ]
}
-- manifest.json --
{
  "version": "0.3.231",
  "source_commit": "d05b050a5d8d1a10959276a3317eece18f5b8c4c",
  "entries": 379
}
-- bytecode under target --
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.agents/skills/tes-engineering-discipline/scripts/__pycache__
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.agents/skills/tes-engineering-discipline/scripts/__pycache__/discipline_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/capsule_residue_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/checkpoint.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/command_trigger_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/context_distill_coverage_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/cortex.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/event_ledger.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/field_reports.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/install_mcp.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/mantra_gate.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/mantra_gate_adoption_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/materialize_adapter.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/pretooluse_kernel.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/pretooluse_session.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/project_context_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/root_context.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/root_context_sanctioned_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/scope_contract.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/tes_bundle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/tes_install.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/__pycache__/tes_project_atlas.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/install_mcp_hosts/__pycache__
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/install_mcp_hosts/__pycache__/__init__.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/install_mcp_hosts/__pycache__/base.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/install_mcp_hosts/__pycache__/claude.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/install_mcp_hosts/__pycache__/codex.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/install_mcp_hosts/__pycache__/cursor.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/cursor/.tes/bin/install_mcp_hosts/__pycache__/vscode.cpython-314.pyc
```

## claude
```
-- git rev-parse --is-inside-work-tree --
true
-- hook/gate files --
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.git/hooks/pre-push
-- postinstall.json --
{
  "version": "0.3.231",
  "state": "complete",
  "last_status": "PASS",
  "advisories": [
    {
      "code": "mesh.scaffold_only",
      "message": "O mesh é apenas scaffold inicial — rode /tes-align para refinamento semântico."
    },
    {
      "code": "cortex.empty",
      "message": "Cortex vazio — capacidade de memória durável não está sendo usada."
    }
  ]
}
-- manifest.json --
{
  "version": "0.3.231",
  "source_commit": "d05b050a5d8d1a10959276a3317eece18f5b8c4c",
  "entries": 379
}
-- bytecode under target --
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.agents/skills/tes-engineering-discipline/scripts/__pycache__
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.agents/skills/tes-engineering-discipline/scripts/__pycache__/discipline_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/capsule_residue_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/checkpoint.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/command_trigger_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/context_distill_coverage_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/cortex.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/event_ledger.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/field_reports.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/install_mcp.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/mantra_gate.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/mantra_gate_adoption_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/materialize_adapter.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/pretooluse_kernel.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/pretooluse_session.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/project_context_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/root_context.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/root_context_sanctioned_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/scope_contract.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/tes_bundle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/tes_install.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/__pycache__/tes_project_atlas.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/install_mcp_hosts/__pycache__
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/install_mcp_hosts/__pycache__/__init__.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/install_mcp_hosts/__pycache__/base.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/install_mcp_hosts/__pycache__/claude.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/install_mcp_hosts/__pycache__/codex.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/install_mcp_hosts/__pycache__/cursor.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/claude/.tes/bin/install_mcp_hosts/__pycache__/vscode.cpython-314.pyc
```

## codex
```
-- git rev-parse --is-inside-work-tree --
true
-- hook/gate files --
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.git/hooks/pre-push
-- postinstall.json --
{
  "version": "0.3.231",
  "state": "complete",
  "last_status": "PASS",
  "advisories": [
    {
      "code": "mesh.scaffold_only",
      "message": "O mesh é apenas scaffold inicial — rode /tes-align para refinamento semântico."
    },
    {
      "code": "cortex.empty",
      "message": "Cortex vazio — capacidade de memória durável não está sendo usada."
    }
  ]
}
-- manifest.json --
{
  "version": "0.3.231",
  "source_commit": "d05b050a5d8d1a10959276a3317eece18f5b8c4c",
  "entries": 379
}
-- bytecode under target --
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.agents/skills/tes-engineering-discipline/scripts/__pycache__
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.agents/skills/tes-engineering-discipline/scripts/__pycache__/discipline_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/capsule_residue_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/checkpoint.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/command_trigger_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/context_distill_coverage_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/cortex.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/event_ledger.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/field_reports.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/install_mcp.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/mantra_gate.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/mantra_gate_adoption_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/materialize_adapter.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/pretooluse_kernel.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/pretooluse_session.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/project_context_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/root_context.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/root_context_sanctioned_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/scope_contract.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/tes_bundle.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/tes_install.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/__pycache__/tes_project_atlas.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/install_mcp_hosts/__pycache__
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/install_mcp_hosts/__pycache__/__init__.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/install_mcp_hosts/__pycache__/base.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/install_mcp_hosts/__pycache__/claude.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/install_mcp_hosts/__pycache__/codex.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/install_mcp_hosts/__pycache__/cursor.cpython-314.pyc
/Users/murillo/Dev/tes-canaries/tmp-replay-0.3.231-20260630092532/codex/.tes/bin/install_mcp_hosts/__pycache__/vscode.cpython-314.pyc
```

## Bundle proof
```
-- shasum --
565ccb30abceb635056db9f7211f155a740a2a7163895a52900304cc2c2a1912  /Users/murillo/Dev/tilly-engineer-skills/docs/dist/0.3.231/tilly-engineer-skills-0.3.231.zip
-- .sha256 sidecar --
565ccb30abceb635056db9f7211f155a740a2a7163895a52900304cc2c2a1912  tilly-engineer-skills-0.3.231.zip
-- bundle manifest name probe --
   219009  06-30-2026 11:25   tes-bundle-manifest.json
```
```
-- bundle manifest summary --
{
  "version": "0.3.231",
  "source_commit": "7a664a93b54575e99348cba216728da895b080c0",
  "entry_count": 378,
  "pycache": 0
}
```
