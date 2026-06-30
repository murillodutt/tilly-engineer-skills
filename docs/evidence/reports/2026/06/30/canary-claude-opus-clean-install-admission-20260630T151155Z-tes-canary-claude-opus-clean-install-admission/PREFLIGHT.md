---
tds_id: evidence.canary_claude_opus_clean_install_admission_aborted.preflight_20260630
tds_class: evidence
status: archived
consumer: maintainers, canary operators, and Goal Maestro operators
source_of_truth: false
evidence_level: L1
---

# PREFLIGHT.md

SPEC-000 path proof + SPEC-002 preflight of existing canaries (BEFORE reset)
Captured: 2026-06-30T15:14:32Z
Executor: Claude Code / Claude Opus 4.8 Max

## Path authority
```
PACKAGE_SOURCE=/Users/murillo/Dev/tilly-engineer-skills  (exists: yes)
CANARY_ROOT=/Users/murillo/Dev/tes-canary  (exists: yes)
Reference journal exists: yes
```

## SPEC-002 preflight loop

### cursor
```
target exists
fatal: not a git repository (or any of the parent directories): .git
--- git status short ---
fatal: not a git repository (or any of the parent directories): .git
--- residue/bytecode scan (maxdepth 4) ---
/Users/murillo/Dev/tes-canary/cursor/.DS_Store
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/capsule_residue_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/checkpoint.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/command_trigger_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/context_distill_coverage_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/cortex.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/cortex_runtime.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/event_ledger.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/field_reports.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/install_mcp.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/mantra_gate.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/mantra_gate_adoption_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/materialize_adapter.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/pretooluse_kernel.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/pretooluse_session.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/project_context_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/root_context.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/root_context_sanctioned_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/scope_contract.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/tes_bundle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/tes_install.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/tes_map.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/__pycache__/tes_project_atlas.cpython-314.pyc
/Users/murillo/Dev/tes-canary/cursor/.tes/bin/install_mcp_hosts/__pycache__
/Users/murillo/Dev/tes-canary/cursor/docs/.DS_Store
--- postinstall.json ---
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
--- manifest.json ---
{
  "version": "0.3.231",
  "source_commit": "88803788cb149d54d32eed543295fbca662aad21",
  "entries": 379
}
```

### claude
```
target exists
fatal: not a git repository (or any of the parent directories): .git
--- git status short ---
fatal: not a git repository (or any of the parent directories): .git
--- residue/bytecode scan (maxdepth 4) ---
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/capsule_residue_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/checkpoint.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/command_trigger_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/context_distill_coverage_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/cortex.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/cortex_runtime.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/event_ledger.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/field_reports.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/install_mcp.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/mantra_gate.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/mantra_gate_adoption_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/materialize_adapter.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/pretooluse_kernel.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/pretooluse_session.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/project_context_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/root_context.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/root_context_sanctioned_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/scope_contract.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/tes_bundle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/tes_install.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/tes_map.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/__pycache__/tes_project_atlas.cpython-314.pyc
/Users/murillo/Dev/tes-canary/claude/.tes/bin/install_mcp_hosts/__pycache__
--- postinstall.json ---
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
--- manifest.json ---
{
  "version": "0.3.231",
  "source_commit": "88803788cb149d54d32eed543295fbca662aad21",
  "entries": 379
}
```

### codex
```
target exists
fatal: not a git repository (or any of the parent directories): .git
--- git status short ---
fatal: not a git repository (or any of the parent directories): .git
--- residue/bytecode scan (maxdepth 4) ---
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/capsule_residue_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/checkpoint.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/command_trigger_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/context_distill_coverage_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/cortex.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/cortex_runtime.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/event_ledger.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/field_reports.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/install_mcp.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/mantra_gate.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/mantra_gate_adoption_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/materialize_adapter.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/pretooluse_kernel.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/pretooluse_session.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/project_context_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/root_context.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/root_context_sanctioned_oracle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/scope_contract.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/tes_bundle.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/tes_install.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/tes_map.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/__pycache__/tes_project_atlas.cpython-314.pyc
/Users/murillo/Dev/tes-canary/codex/.tes/bin/install_mcp_hosts/__pycache__
--- postinstall.json ---
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
--- manifest.json ---
{
  "version": "0.3.231",
  "source_commit": "88803788cb149d54d32eed543295fbca662aad21",
  "entries": 379
}
```
