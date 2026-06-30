---
tds_id: evidence.canary_pre_goal_maestro_cleanroom_fix.final_admission_matrix_20260630
tds_class: evidence
status: active
consumer: maintainers, canary operators, and Goal Maestro operators
source_of_truth: false
evidence_level: L2
---

# FINAL RECERTIFICATION MATRIX
## cursor
true
6a2a735
pre-commit: executable
pre-push: executable
{
  "anchors_checked": [
    "docs/agents/DOCUMENTATION-AUTHORITY.md"
  ],
  "failures": [],
  "quality_scripts_checked": [],
  "status": "PASS",
  "target": "/Users/murillo/Dev/tes-canary/cursor",
  "territories_checked": [
    ".cursor",
    "docs"
  ],
  "version": "0.3.231",
  "warnings": [],
  "workspace_boundaries_checked": []
}
[project-context] PASS
{
  "docs": {
    "boundaries": {
      "exists": true,
      "path": "docs/agents/BOUNDARIES-AND-CONSTRAINTS.md",
      "path_refs": [
        "AGENTS.md",
        "CLAUDE.md",
        "CURSOR.md",
        "docs/agents/DOCUMENTATION-AUTHORITY.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 4
    },
    "execution_line": {
      "exists": true,
      "path": "docs/agents/EXECUTION-LINE.md",
      "path_refs": [
        "docs/agents/DOCUMENTATION-AUTHORITY.md",
        "docs/agents/evidence/20260630T123904Z-project-alignment.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 9
    },
    "glossary": {
      "exists": true,
      "path": "docs/agents/GLOSSARY.md",
      "path_refs": [
        "CURSOR.md",
        "docs/agents/DOCUMENTATION-AUTHORITY.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 2
    },
    "knowledge_lifecycle": {
      "exists": true,
      "path": "docs/agents/KNOWLEDGE-LIFECYCLE.md",
      "path_refs": [
        "docs/agents/DOCUMENTATION-AUTHORITY.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 4
    },
    "project_context": {
      "exists": true,
      "path": "docs/agents/PROJECT-CONTEXT.md",
      "path_refs": [
        ".claude/settings.json",
        ".claude/settings.json.bak-20260630T123556Z",
        ".codex/config.toml",
        ".cursor/hooks.json",
        ".cursor/hooks.json.bak-20260630T123556Z",
        ".cursor/mcp.json",
        ".cursor/rules/tes-runtime-capabilities.md",
        ".cursor/rules/tes-runtime-capabilities.mdc",
        ".mcp.json",
        "/Users/murillo/Dev/tes-canary/cursor",
        "/Users/murillo/Dev/tes-canary/cursor/.agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py",
        "/Users/murillo/Dev/tes-canary/cursor/.tes/bin/cortex_mcp.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/cortex.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/field_reports.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/project_alignment_oracle.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/project_context_oracle.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/root_context.py",
        "CURSOR.md",
        "docs/agents/DOCUMENTATION-AUTHORITY.md",
        "docs/agents/contracts/INVENTORY-HYGIENE.yml"
      ],
      "wikilinks": 6
    },
    "project_roadmap": {
      "exists": true,
      "path": "docs/agents/PROJECT-ROADMAP.md",
      "path_refs": [
        ".tes/gps/data-map.eraserdiagram",
        ".tes/gps/dependency-map.eraserdiagram",
        ".tes/gps/gates-evidence.eraserdiagram",
        ".tes/gps/module-tree.eraserdiagram",
        ".tes/gps/project-gps.eraserdiagram",
        ".tes/gps/project-overview.eraserdiagram",
        ".tes/gps/runtime-integrations.eraserdiagram",
        ".tes/postinstall.json",
        ".tes/tes-install-lock.json",
        "CURSOR.md",
        "docs/agents/QUALITY-GATES.md",
        "docs/agents/evidence/20260630T123631Z-project-alignment.md",
        "docs/agents/evidence/20260630T123631Z-tes-initialization.md",
        "docs/agents/evidence/20260630T123904Z-project-alignment.md",
        "docs/project/super-spec.md",
        "project_alignment_oracle.py"
      ],
      "wikilinks": 3
    },
    "project_state": {
      "exists": true,
      "path": "docs/agents/PROJECT-STATE.md",
      "path_refs": [
        ".tes/postinstall.json",
        "CURSOR.md",
        "docs/agents/evidence/20260630T123904Z-project-alignment.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 6
    },
    "quality_gates": {
      "exists": true,
      "path": "docs/agents/QUALITY-GATES.md",
      "path_refs": [
        ".tes/bin/cortex.py",
        ".tes/bin/project_alignment_oracle.py",
        ".tes/bin/project_context_oracle.py",
        ".tes/bin/verify_documentation_inventory.py",
        "docs/agents/DOCUMENTATION-AUTHORITY.md",
        "docs/agents/evidence/20260630T123904Z-project-alignment.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 3
    }
  },
  "evidence_packets": [
    "docs/agents/evidence/20260630T123631Z-project-alignment.md",
    "docs/agents/evidence/20260630T123904Z-project-alignment.md",
    "docs/agents/evidence/20260630T133120Z-project-alignment.md"
  ],
  "failures": [],
  "freshness": {
    "mesh_scaffold_only": true,
    "needs_review": [],
    "newest_adr": "docs/agents/DECISIONS/002-super-spec-tier-1-product-truth.md",
    "newest_evidence": "docs/agents/evidence/20260630T133120Z-project-alignment.md",
    "notes": [
      "newest ADR docs/agents/DECISIONS/001-initial-operating-mesh.md introduces tokens absent from the active mesh: Markdown, Obsidian, super-spec-tier-1-product-truth"
    ]
  },
  "inventory_hygiene": {
    "applied": true,
    "contract_path": "docs/agents/contracts/INVENTORY-HYGIENE.yml",
    "findings": [
      {
        "code": "inventory.stale_git_head",
        "path": "docs/agents/PROJECT-CONTEXT.md",
        "reason": "Identity table missing Git HEAD row",
        "severity": "needs_review"
      }
    ],
    "status": "NEEDS_REVIEW"
  },
  "needs_review": [
    "inventory hygiene: Identity table missing Git HEAD row"
  ],
  "semantic_residue": {
    "applied": false,
    "contract_path": null,
    "findings": [],
    "status": "PASS",
    "warnings": [
      "no Semantic Residue contract declared under docs/agents/contracts/SEMANTIC-RESIDUE.yml"
    ]
  },
  "status": "NEEDS_REVIEW",
  "target": "/Users/murillo/Dev/tes-canary/cursor",
  "version": "0.3.231",
  "warnings": [
    "no Semantic Residue contract declared under docs/agents/contracts/SEMANTIC-RESIDUE.yml",
    "newest ADR docs/agents/DECISIONS/001-initial-operating-mesh.md introduces tokens absent from the active mesh: Markdown, Obsidian, super-spec-tier-1-product-truth"
  ]
}
[project-alignment] NEEDS_REVIEW
{
  "atlas_views": {
    "data_map": true,
    "dependency_map": true,
    "gates_evidence": true,
    "module_tree": true,
    "project_gps": true,
    "project_overview": true,
    "runtime_integrations": true
  },
  "failures": [],
  "managed_block_present": true,
  "model_status": "PASS",
  "roadmap": "/Users/murillo/Dev/tes-canary/cursor/docs/agents/PROJECT-ROADMAP.md",
  "status": "PASS",
  "target": "/Users/murillo/Dev/tes-canary/cursor",
  "version": "0.3.231"
}
{
  "disabled": false,
  "failures": [],
  "last_receipt": null,
  "outbox": ".tes/field-reports/outbox.jsonl",
  "pending": 15,
  "pending_advisory": null,
  "status": "PASS",
  "version": "0.3.231",
  "writes": []
}
[field-reports] PASS
{
  "agents": {
    "claude": {
      "events": [
        {
          "config": ".claude/settings.json",
          "event": "SessionStart",
          "event_canonical": "SessionStart",
          "legacy_observed": false,
          "runtime_records": 0,
          "state": "CONFIGURED"
        },
        {
          "config": ".claude/settings.json",
          "event": "PreToolUse",
          "event_canonical": "PreToolUse",
          "legacy_observed": false,
          "runtime_records": 23,
          "state": "OBSERVED"
        }
      ]
    },
    "codex": {
      "events": [
        {
          "config": ".codex/config.toml",
          "event": "SessionStart",
          "event_canonical": "SessionStart",
          "legacy_observed": false,
          "runtime_records": 0,
          "state": "CONFIGURED"
        },
        {
          "config": ".codex/config.toml",
          "event": "PreToolUse",
          "event_canonical": "PreToolUse",
          "legacy_observed": false,
          "runtime_records": 0,
          "state": "CONFIGURED"
        }
      ]
    },
    "cursor": {
      "events": [
        {
          "config": ".cursor/hooks.json",
          "event": "sessionStart",
          "event_canonical": "sessionStart",
          "legacy_observed": false,
          "runtime_records": 1,
          "state": "OBSERVED"
        },
        {
          "config": ".cursor/hooks.json",
          "event": "beforeSubmitPrompt",
          "event_canonical": "beforeSubmitPrompt",
          "legacy_observed": false,
          "runtime_records": 1,
          "state": "OBSERVED"
        },
        {
          "config": ".cursor/hooks.json",
          "event": "preToolUse",
          "event_canonical": "PreToolUse",
          "legacy_observed": false,
          "runtime_records": 71,
          "state": "OBSERVED"
        }
      ]
    }
  },
  "attached_surfaces": [
    "capsule",
    "hooks",
    "mcp",
    "root-context",
    "skills"
  ],
  "ceiling_evidence_scope": {
    "aggregation_policy": "per_host_no_cross_fill",
    "claim_scope": "current_host",
    "current_host": "cursor",
    "legacy_policy": "historical_context_only",
    "per_host": {
      "cursor": {
        "agent": "cursor",
        "considered_records": 71,
        "current_v2_contradictions": [],
        "gaps": [
          "missing_discoverability_runtime_row"
        ],
        "ignored_legacy_records": 0,
        "native_evidence": "observed",
        "newest_considered_ts": "2026-06-30T12:41:09Z",
        "oldest_considered_ts": "2026-06-30T12:36:38Z",
        "status": "PASS_BASIC_WITH_CEILING_GAPS"
      }
    },
    "required_hosts": [
      "cursor"
    ],
    "schema_version": "pretooluse_decision@2"
  },
  "ceiling_gaps": [
    "missing_discoverability_runtime_row"
  ],
  "ceiling_status": "NEEDS_FLOOR",
  "dedupe_contract": {
    "ceiling_noise_rule": "historical_duplicate_replay_and_cursor_batch_noise_is_non_blocking_without_current_v2_contradiction",
    "current_v2_contradiction_rule": "same_host_scope_unexplained_decision_risk_renderer_redaction_marker_contradiction_blocks_ceiling",
    "cursor_batch_rule": "same_invocation_timestamp_different_tool_path_risk_marker_is_not_duplicate",
    "fields": [
      "schema_version",
      "agent",
      "event_canonical",
      "mode",
      "session",
      "tool",
      "path",
      "command_category",
      "command_redacted",
      "invocation",
      "raw_tool_label",
      "normalized_tool",
      "payload_source",
      "classifier_trace",
      "renderer_trace",
      "risk",
      "outcome",
      "reason_codes",
      "block",
      "decision",
      "permission_decision",
      "marker_emitted",
      "context_suppressed",
      "cortex_context_emitted",
      "surface_context"
    ],
    "schema": "tes-hook-dedupe@1",
    "timestamp_rule": "same_semantic_different_timestamp_is_replay_history"
  },
  "discoverability_status": "NEEDS_EVIDENCE",
  "finding_counts": {
    "error": 0,
    "info": 3,
    "warning": 0
  },
  "findings": [
    {
      "agent": "codex",
      "event": "SessionStart",
      "severity": "info",
      "type": "configured_without_runtime_observation"
    },
    {
      "agent": "codex",
      "event": "PreToolUse",
      "severity": "info",
      "type": "configured_without_runtime_observation"
    },
    {
      "agent": "claude",
      "event": "SessionStart",
      "severity": "info",
      "type": "configured_without_runtime_observation"
    }
  ],
  "floor_status": "NEEDS_EVIDENCE",
  "helper_contract_status": "PASS",
  "legacy_schema": "tes-hook-health@1",
  "schema": "tes-hook-health@2",
  "sentinels": {
    "current": {
      "path": ".tes/runtime/hooks/executed.jsonl",
      "records": 98,
      "status": "OBSERVED"
    },
    "legacy": {
      "path": ".tes/hooks/executed.jsonl",
      "records": 0,
      "status": "ABSENT"
    }
  },
  "status": "NEEDS_EVIDENCE",
  "target": "/Users/murillo/Dev/tes-canary/cursor",
  "version": "0.3.231"
}
{
  "state": "complete",
  "last_status": "PASS",
  "last_run": ".tes/postinstall-runs/20260630T123634Z-cursor.json",
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
{
  "version": "0.3.231",
  "attached_surfaces": [
    "capsule",
    "hooks",
    "mcp",
    "root-context",
    "skills"
  ],
  "components": {
    "artifact_hygiene": "PASS",
    "command_trigger_parity": "PASS",
    "hook_config_hygiene": "PASS",
    "hook_runtime_health": "NEEDS_EVIDENCE",
    "mantra_gate_adoption": "OK",
    "mcp_registration": "PASS",
    "pretooluse_contract_reference": "PASS",
    "quality_gates_path": "NOT_APPLIED"
  },
  "negative_checks": {
    "host_connected_not_inferred": true,
    "os_residue_absent": true,
    "pretooluse_contract_reference_valid": true,
    "stale_codex_hooks_json_absent": true,
    "stale_discipline_path_absent": true,
    "vscode_not_part_of_agent_all": true
  }
}
os_residue:
18:command = "/opt/homebrew/opt/python@3.14/bin/python3.14 \"$(git rev-parse --show-toplevel)/.tes/bin/tes_install.py\" hook --agent codex --target \"$(git rev-parse --show-toplevel)\""
28:command = "/opt/homebrew/opt/python@3.14/bin/python3.14 \"$(git rev-parse --show-toplevel)/.tes/bin/tes_install.py\" hook --agent codex --target \"$(git rev-parse --show-toplevel)\""
## claude
true
aa2ce20
pre-commit: executable
pre-push: executable
{
  "anchors_checked": [
    "docs/agents/DOCUMENTATION-AUTHORITY.md"
  ],
  "failures": [],
  "quality_scripts_checked": [],
  "status": "PASS",
  "target": "/Users/murillo/Dev/tes-canary/claude",
  "territories_checked": [
    ".cursor",
    "docs"
  ],
  "version": "0.3.231",
  "warnings": [],
  "workspace_boundaries_checked": []
}
[project-context] PASS
{
  "docs": {
    "boundaries": {
      "exists": true,
      "path": "docs/agents/BOUNDARIES-AND-CONSTRAINTS.md",
      "path_refs": [
        "AGENTS.md",
        "CLAUDE.md",
        "CURSOR.md",
        "docs/agents/PROJECT-CONTEXT.md",
        "docs/agents/evidence/20260630T123619Z-tes-project-manifest.json"
      ],
      "wikilinks": 3
    },
    "execution_line": {
      "exists": true,
      "path": "docs/agents/EXECUTION-LINE.md",
      "path_refs": [
        ".tes/tes-install-lock.json",
        "docs/agents/DECISIONS/002-canary-parity-alignment.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 9
    },
    "glossary": {
      "exists": true,
      "path": "docs/agents/GLOSSARY.md",
      "path_refs": [
        "AGENTS.md",
        "CLAUDE.md",
        "CURSOR.md",
        "docs/agents/DECISIONS/002-canary-parity-alignment.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 2
    },
    "knowledge_lifecycle": {
      "exists": true,
      "path": "docs/agents/KNOWLEDGE-LIFECYCLE.md",
      "path_refs": [
        ".tes/tes-install-lock.json",
        "CURSOR.md",
        "docs/agents/PROJECT-CONTEXT.md",
        "docs/agents/evidence/20260630T123619Z-tes-project-manifest.json",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 5
    },
    "project_context": {
      "exists": true,
      "path": "docs/agents/PROJECT-CONTEXT.md",
      "path_refs": [
        ".claude/settings.json",
        ".claude/settings.json.bak-20260630T123613Z",
        ".codex/config.toml",
        ".cursor/hooks.json",
        ".cursor/hooks.json.bak-20260630T123613Z",
        ".cursor/mcp.json",
        ".cursor/rules/tes-runtime-capabilities.md",
        ".cursor/rules/tes-runtime-capabilities.mdc",
        ".mcp.json",
        "/Users/murillo/Dev/tes-canary/claude",
        "/Users/murillo/Dev/tes-canary/claude/.agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py",
        "/Users/murillo/Dev/tes-canary/claude/.tes/bin/cortex_mcp.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/cortex.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/field_reports.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/project_alignment_oracle.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/project_context_oracle.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/root_context.py",
        "CURSOR.md",
        "docs/agents/DOCUMENTATION-AUTHORITY.md",
        "docs/agents/evidence/20260630T133151Z-tes-project-manifest.json"
      ],
      "wikilinks": 6
    },
    "project_roadmap": {
      "exists": true,
      "path": "docs/agents/PROJECT-ROADMAP.md",
      "path_refs": [
        ".tes/gps/data-map.eraserdiagram",
        ".tes/gps/dependency-map.eraserdiagram",
        ".tes/gps/gates-evidence.eraserdiagram",
        ".tes/gps/module-tree.eraserdiagram",
        ".tes/gps/project-gps.eraserdiagram",
        ".tes/gps/project-overview.eraserdiagram",
        ".tes/gps/runtime-integrations.eraserdiagram",
        ".tes/postinstall.json",
        ".tes/tes-install-lock.json",
        "DOCUMENTATION-AUTHORITY.md",
        "docs/agents/DECISIONS/002-canary-parity-alignment.md",
        "docs/agents/QUALITY-GATES.md",
        "docs/agents/evidence/20260630T123619Z-project-alignment.md",
        "docs/agents/evidence/20260630T123619Z-tes-initialization.md",
        "docs/agents/evidence/20260630T123940Z-project-alignment.md",
        "docs/project/super-spec.md",
        "project_alignment_oracle.py",
        "super-spec.md"
      ],
      "wikilinks": 6
    },
    "project_state": {
      "exists": true,
      "path": "docs/agents/PROJECT-STATE.md",
      "path_refs": [
        "CURSOR.md",
        "DOCUMENTATION-AUTHORITY.md",
        "docs/agents/DECISIONS/002-canary-parity-alignment.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 4
    },
    "quality_gates": {
      "exists": true,
      "path": "docs/agents/QUALITY-GATES.md",
      "path_refs": [
        ".tes/bin/project_alignment_oracle.py",
        ".tes/bin/project_context_oracle.py",
        ".tes/bin/tes_map_oracle.py",
        ".tes/tes-install-lock.json",
        "docs/agents/DECISIONS/002-canary-parity-alignment.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 3
    }
  },
  "evidence_packets": [
    "docs/agents/evidence/20260630T123619Z-project-alignment.md",
    "docs/agents/evidence/20260630T123940Z-project-alignment.md",
    "docs/agents/evidence/20260630T133151Z-project-alignment.md"
  ],
  "failures": [],
  "freshness": {
    "mesh_scaffold_only": true,
    "needs_review": [],
    "newest_adr": "docs/agents/DECISIONS/002-canary-parity-alignment.md",
    "newest_evidence": "docs/agents/evidence/20260630T133151Z-project-alignment.md",
    "notes": [
      "newest ADR docs/agents/DECISIONS/002-canary-parity-alignment.md introduces tokens absent from the active mesh: GLOSSARY, Markdown, initial-operating-mesh"
    ]
  },
  "inventory_hygiene": {
    "applied": true,
    "contract_path": "docs/agents/contracts/INVENTORY-HYGIENE.yml",
    "findings": [
      {
        "code": "inventory.stale_git_head",
        "path": "docs/agents/PROJECT-CONTEXT.md",
        "reason": "Identity table missing Git HEAD row",
        "severity": "needs_review"
      }
    ],
    "status": "NEEDS_REVIEW"
  },
  "needs_review": [
    "inventory hygiene: Identity table missing Git HEAD row"
  ],
  "semantic_residue": {
    "applied": false,
    "contract_path": null,
    "findings": [],
    "status": "PASS",
    "warnings": [
      "no Semantic Residue contract declared under docs/agents/contracts/SEMANTIC-RESIDUE.yml"
    ]
  },
  "status": "NEEDS_REVIEW",
  "target": "/Users/murillo/Dev/tes-canary/claude",
  "version": "0.3.231",
  "warnings": [
    "no Semantic Residue contract declared under docs/agents/contracts/SEMANTIC-RESIDUE.yml",
    "newest ADR docs/agents/DECISIONS/002-canary-parity-alignment.md introduces tokens absent from the active mesh: GLOSSARY, Markdown, initial-operating-mesh"
  ]
}
[project-alignment] NEEDS_REVIEW
{
  "atlas_views": {
    "data_map": true,
    "dependency_map": true,
    "gates_evidence": true,
    "module_tree": true,
    "project_gps": true,
    "project_overview": true,
    "runtime_integrations": true
  },
  "failures": [],
  "managed_block_present": true,
  "model_status": "PASS",
  "roadmap": "/Users/murillo/Dev/tes-canary/claude/docs/agents/PROJECT-ROADMAP.md",
  "status": "PASS",
  "target": "/Users/murillo/Dev/tes-canary/claude",
  "version": "0.3.231"
}
{
  "disabled": false,
  "failures": [],
  "last_receipt": null,
  "outbox": ".tes/field-reports/outbox.jsonl",
  "pending": 15,
  "pending_advisory": null,
  "status": "PASS",
  "version": "0.3.231",
  "writes": []
}
[field-reports] PASS
{
  "agents": {
    "claude": {
      "events": [
        {
          "config": ".claude/settings.json",
          "event": "SessionStart",
          "event_canonical": "SessionStart",
          "legacy_observed": false,
          "runtime_records": 2,
          "state": "OBSERVED"
        },
        {
          "config": ".claude/settings.json",
          "event": "PreToolUse",
          "event_canonical": "PreToolUse",
          "legacy_observed": false,
          "runtime_records": 35,
          "state": "OBSERVED"
        }
      ]
    },
    "codex": {
      "events": [
        {
          "config": ".codex/config.toml",
          "event": "SessionStart",
          "event_canonical": "SessionStart",
          "legacy_observed": false,
          "runtime_records": 0,
          "state": "CONFIGURED"
        },
        {
          "config": ".codex/config.toml",
          "event": "PreToolUse",
          "event_canonical": "PreToolUse",
          "legacy_observed": false,
          "runtime_records": 0,
          "state": "CONFIGURED"
        }
      ]
    },
    "cursor": {
      "events": [
        {
          "config": ".cursor/hooks.json",
          "event": "sessionStart",
          "event_canonical": "sessionStart",
          "legacy_observed": false,
          "runtime_records": 0,
          "state": "CONFIGURED"
        },
        {
          "config": ".cursor/hooks.json",
          "event": "beforeSubmitPrompt",
          "event_canonical": "beforeSubmitPrompt",
          "legacy_observed": false,
          "runtime_records": 0,
          "state": "CONFIGURED"
        },
        {
          "config": ".cursor/hooks.json",
          "event": "preToolUse",
          "event_canonical": "PreToolUse",
          "legacy_observed": false,
          "runtime_records": 0,
          "state": "CONFIGURED"
        }
      ]
    }
  },
  "attached_surfaces": [
    "capsule",
    "hooks",
    "mcp",
    "root-context",
    "skills"
  ],
  "ceiling_evidence_scope": {
    "aggregation_policy": "per_host_no_cross_fill",
    "claim_scope": "current_host",
    "current_host": "cursor",
    "legacy_policy": "historical_context_only",
    "per_host": {
      "cursor": {
        "agent": "cursor",
        "considered_records": 0,
        "current_v2_contradictions": [],
        "gaps": [
          "missing_pretooluse_runtime_rows"
        ],
        "ignored_legacy_records": 0,
        "native_evidence": "not_available",
        "newest_considered_ts": null,
        "oldest_considered_ts": null,
        "status": "NEEDS_EVIDENCE"
      }
    },
    "required_hosts": [
      "cursor"
    ],
    "schema_version": "pretooluse_decision@2"
  },
  "ceiling_gaps": [
    "missing_pretooluse_runtime_rows"
  ],
  "ceiling_status": "NEEDS_FLOOR",
  "dedupe_contract": {
    "ceiling_noise_rule": "historical_duplicate_replay_and_cursor_batch_noise_is_non_blocking_without_current_v2_contradiction",
    "current_v2_contradiction_rule": "same_host_scope_unexplained_decision_risk_renderer_redaction_marker_contradiction_blocks_ceiling",
    "cursor_batch_rule": "same_invocation_timestamp_different_tool_path_risk_marker_is_not_duplicate",
    "fields": [
      "schema_version",
      "agent",
      "event_canonical",
      "mode",
      "session",
      "tool",
      "path",
      "command_category",
      "command_redacted",
      "invocation",
      "raw_tool_label",
      "normalized_tool",
      "payload_source",
      "classifier_trace",
      "renderer_trace",
      "risk",
      "outcome",
      "reason_codes",
      "block",
      "decision",
      "permission_decision",
      "marker_emitted",
      "context_suppressed",
      "cortex_context_emitted",
      "surface_context"
    ],
    "schema": "tes-hook-dedupe@1",
    "timestamp_rule": "same_semantic_different_timestamp_is_replay_history"
  },
  "discoverability_status": "NEEDS_EVIDENCE",
  "finding_counts": {
    "error": 0,
    "info": 5,
    "warning": 0
  },
  "findings": [
    {
      "agent": "codex",
      "event": "SessionStart",
      "severity": "info",
      "type": "configured_without_runtime_observation"
    },
    {
      "agent": "codex",
      "event": "PreToolUse",
      "severity": "info",
      "type": "configured_without_runtime_observation"
    },
    {
      "agent": "cursor",
      "event": "sessionStart",
      "severity": "info",
      "type": "configured_without_runtime_observation"
    },
    {
      "agent": "cursor",
      "event": "beforeSubmitPrompt",
      "severity": "info",
      "type": "configured_without_runtime_observation"
    },
    {
      "agent": "cursor",
      "event": "preToolUse",
      "severity": "info",
      "type": "configured_without_runtime_observation"
    }
  ],
  "floor_status": "NEEDS_EVIDENCE",
  "helper_contract_status": "PASS",
  "legacy_schema": "tes-hook-health@1",
  "schema": "tes-hook-health@2",
  "sentinels": {
    "current": {
      "path": ".tes/runtime/hooks/executed.jsonl",
      "records": 37,
      "status": "OBSERVED"
    },
    "legacy": {
      "path": ".tes/hooks/executed.jsonl",
      "records": 0,
      "status": "ABSENT"
    }
  },
  "status": "NEEDS_EVIDENCE",
  "target": "/Users/murillo/Dev/tes-canary/claude",
  "version": "0.3.231"
}
{
  "state": "complete",
  "last_status": "PASS",
  "last_run": ".tes/postinstall-runs/20260630T123622Z-claude.json",
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
{
  "version": "0.3.231",
  "attached_surfaces": [
    "capsule",
    "hooks",
    "mcp",
    "root-context",
    "skills"
  ],
  "components": {
    "artifact_hygiene": "PASS",
    "command_trigger_parity": "PASS",
    "hook_config_hygiene": "PASS",
    "hook_runtime_health": "NEEDS_EVIDENCE",
    "mantra_gate_adoption": "OK",
    "mcp_registration": "PASS",
    "pretooluse_contract_reference": "PASS",
    "quality_gates_path": "NOT_APPLIED"
  },
  "negative_checks": {
    "host_connected_not_inferred": true,
    "os_residue_absent": true,
    "pretooluse_contract_reference_valid": true,
    "stale_codex_hooks_json_absent": true,
    "stale_discipline_path_absent": true,
    "vscode_not_part_of_agent_all": true
  }
}
os_residue:
18:command = "/opt/homebrew/opt/python@3.14/bin/python3.14 \"$(git rev-parse --show-toplevel)/.tes/bin/tes_install.py\" hook --agent codex --target \"$(git rev-parse --show-toplevel)\""
28:command = "/opt/homebrew/opt/python@3.14/bin/python3.14 \"$(git rev-parse --show-toplevel)/.tes/bin/tes_install.py\" hook --agent codex --target \"$(git rev-parse --show-toplevel)\""
## codex
true
7e79582
pre-commit: executable
pre-push: executable
{
  "anchors_checked": [
    "docs/agents/DOCUMENTATION-AUTHORITY.md"
  ],
  "failures": [],
  "quality_scripts_checked": [],
  "status": "PASS",
  "target": "/Users/murillo/Dev/tes-canary/codex",
  "territories_checked": [
    ".cursor",
    "docs"
  ],
  "version": "0.3.231",
  "warnings": [],
  "workspace_boundaries_checked": []
}
[project-context] PASS
{
  "docs": {
    "boundaries": {
      "exists": true,
      "path": "docs/agents/BOUNDARIES-AND-CONSTRAINTS.md",
      "path_refs": [
        "CURSOR.md",
        "docs/agents/evidence/20260630T124501Z-project-alignment.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 3
    },
    "execution_line": {
      "exists": true,
      "path": "docs/agents/EXECUTION-LINE.md",
      "path_refs": [
        "docs/agents/QUALITY-GATES.md",
        "docs/agents/evidence/20260630T124501Z-project-alignment.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 11
    },
    "glossary": {
      "exists": true,
      "path": "docs/agents/GLOSSARY.md",
      "path_refs": [
        "docs/agents/evidence/20260630T124501Z-project-alignment.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 4
    },
    "knowledge_lifecycle": {
      "exists": true,
      "path": "docs/agents/KNOWLEDGE-LIFECYCLE.md",
      "path_refs": [
        "docs/agents/evidence/20260630T124501Z-project-alignment.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 5
    },
    "project_context": {
      "exists": true,
      "path": "docs/agents/PROJECT-CONTEXT.md",
      "path_refs": [
        ".claude/settings.json",
        ".claude/settings.json.bak-20260630T123604Z",
        ".codex/config.toml",
        ".cursor/hooks.json",
        ".cursor/hooks.json.bak-20260630T123604Z",
        ".cursor/mcp.json",
        ".cursor/rules/tes-runtime-capabilities.md",
        ".cursor/rules/tes-runtime-capabilities.mdc",
        ".mcp.json",
        "/Users/murillo/Dev/tes-canary/codex",
        "/Users/murillo/Dev/tes-canary/codex/.agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py",
        "/Users/murillo/Dev/tes-canary/codex/.tes/bin/cortex_mcp.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/cortex.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/field_reports.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/project_alignment_oracle.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/project_context_oracle.py",
        "/Users/murillo/Dev/tilly-engineer-skills/scripts/root_context.py",
        "CURSOR.md",
        "docs/agents/DOCUMENTATION-AUTHORITY.md",
        "docs/agents/contracts/OPERATING-MESH-CONTRACT.md"
      ],
      "wikilinks": 6
    },
    "project_roadmap": {
      "exists": true,
      "path": "docs/agents/PROJECT-ROADMAP.md",
      "path_refs": [
        ".tes/gps/data-map.eraserdiagram",
        ".tes/gps/dependency-map.eraserdiagram",
        ".tes/gps/gates-evidence.eraserdiagram",
        ".tes/gps/module-tree.eraserdiagram",
        ".tes/gps/project-gps.eraserdiagram",
        ".tes/gps/project-overview.eraserdiagram",
        ".tes/gps/runtime-integrations.eraserdiagram",
        ".tes/postinstall.json",
        ".tes/tes-install-lock.json",
        "docs/agents/QUALITY-GATES.md",
        "docs/agents/evidence/20260630T124121Z-project-alignment.md",
        "docs/agents/evidence/20260630T124121Z-tes-initialization.md",
        "docs/agents/evidence/20260630T124501Z-project-alignment.md",
        "docs/project/super-spec.md",
        "project_alignment_oracle.py"
      ],
      "wikilinks": 4
    },
    "project_state": {
      "exists": true,
      "path": "docs/agents/PROJECT-STATE.md",
      "path_refs": [
        "CURSOR.md",
        "docs/agents/evidence/20260630T124501Z-project-alignment.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 4
    },
    "quality_gates": {
      "exists": true,
      "path": "docs/agents/QUALITY-GATES.md",
      "path_refs": [
        ".tes/bin/installed_certification_oracle.py",
        ".tes/bin/project_alignment_oracle.py",
        ".tes/bin/project_context_oracle.py",
        "docs/agents/evidence/20260630T124501Z-project-alignment.md",
        "docs/project/super-spec.md"
      ],
      "wikilinks": 3
    }
  },
  "evidence_packets": [
    "docs/agents/evidence/20260630T123825Z-project-alignment.md",
    "docs/agents/evidence/20260630T124121Z-project-alignment.md",
    "docs/agents/evidence/20260630T124501Z-project-alignment.md",
    "docs/agents/evidence/20260630T133221Z-project-alignment.md"
  ],
  "failures": [],
  "freshness": {
    "mesh_scaffold_only": true,
    "needs_review": [],
    "newest_adr": "docs/agents/DECISIONS/002-super-spec-runtime-contract.md",
    "newest_evidence": "docs/agents/evidence/20260630T133221Z-project-alignment.md",
    "notes": []
  },
  "inventory_hygiene": {
    "applied": true,
    "contract_path": "docs/agents/contracts/INVENTORY-HYGIENE.yml",
    "findings": [
      {
        "code": "inventory.stale_git_head",
        "path": "docs/agents/PROJECT-CONTEXT.md",
        "reason": "Identity table missing Git HEAD row",
        "severity": "needs_review"
      }
    ],
    "status": "NEEDS_REVIEW"
  },
  "needs_review": [
    "inventory hygiene: Identity table missing Git HEAD row"
  ],
  "semantic_residue": {
    "applied": false,
    "contract_path": null,
    "findings": [],
    "status": "PASS",
    "warnings": [
      "no Semantic Residue contract declared under docs/agents/contracts/SEMANTIC-RESIDUE.yml"
    ]
  },
  "status": "NEEDS_REVIEW",
  "target": "/Users/murillo/Dev/tes-canary/codex",
  "version": "0.3.231",
  "warnings": [
    "no Semantic Residue contract declared under docs/agents/contracts/SEMANTIC-RESIDUE.yml"
  ]
}
[project-alignment] NEEDS_REVIEW
{
  "atlas_views": {
    "data_map": true,
    "dependency_map": true,
    "gates_evidence": true,
    "module_tree": true,
    "project_gps": true,
    "project_overview": true,
    "runtime_integrations": true
  },
  "failures": [],
  "managed_block_present": true,
  "model_status": "PASS",
  "roadmap": "/Users/murillo/Dev/tes-canary/codex/docs/agents/PROJECT-ROADMAP.md",
  "status": "PASS",
  "target": "/Users/murillo/Dev/tes-canary/codex",
  "version": "0.3.231"
}
{
  "disabled": false,
  "failures": [],
  "last_receipt": null,
  "outbox": ".tes/field-reports/outbox.jsonl",
  "pending": 21,
  "pending_advisory": null,
  "status": "PASS",
  "version": "0.3.231",
  "writes": []
}
[field-reports] PASS
{
  "agents": {
    "claude": {
      "events": [
        {
          "config": ".claude/settings.json",
          "event": "SessionStart",
          "event_canonical": "SessionStart",
          "legacy_observed": false,
          "runtime_records": 1,
          "state": "OBSERVED"
        },
        {
          "config": ".claude/settings.json",
          "event": "PreToolUse",
          "event_canonical": "PreToolUse",
          "legacy_observed": false,
          "runtime_records": 1,
          "state": "OBSERVED"
        }
      ]
    },
    "codex": {
      "events": [
        {
          "config": ".codex/config.toml",
          "event": "SessionStart",
          "event_canonical": "SessionStart",
          "legacy_observed": false,
          "runtime_records": 1,
          "state": "OBSERVED"
        },
        {
          "config": ".codex/config.toml",
          "event": "PreToolUse",
          "event_canonical": "PreToolUse",
          "legacy_observed": false,
          "runtime_records": 1,
          "state": "OBSERVED"
        }
      ]
    },
    "cursor": {
      "events": [
        {
          "config": ".cursor/hooks.json",
          "event": "sessionStart",
          "event_canonical": "sessionStart",
          "legacy_observed": false,
          "runtime_records": 1,
          "state": "OBSERVED"
        },
        {
          "config": ".cursor/hooks.json",
          "event": "beforeSubmitPrompt",
          "event_canonical": "beforeSubmitPrompt",
          "legacy_observed": false,
          "runtime_records": 1,
          "state": "OBSERVED"
        },
        {
          "config": ".cursor/hooks.json",
          "event": "preToolUse",
          "event_canonical": "PreToolUse",
          "legacy_observed": false,
          "runtime_records": 1,
          "state": "OBSERVED"
        }
      ]
    }
  },
  "attached_surfaces": [
    "capsule",
    "hooks",
    "mcp",
    "root-context",
    "skills"
  ],
  "ceiling_evidence_scope": {
    "aggregation_policy": "per_host_no_cross_fill",
    "claim_scope": "current_host",
    "current_host": "cursor",
    "legacy_policy": "historical_context_only",
    "per_host": {
      "cursor": {
        "agent": "cursor",
        "considered_records": 1,
        "current_v2_contradictions": [],
        "gaps": [
          "missing_discoverability_runtime_row",
          "missing_redacted_command_evidence"
        ],
        "ignored_legacy_records": 0,
        "native_evidence": "observed",
        "newest_considered_ts": "2026-06-30T12:40:34Z",
        "oldest_considered_ts": "2026-06-30T12:40:34Z",
        "status": "PASS_BASIC_WITH_CEILING_GAPS"
      }
    },
    "required_hosts": [
      "cursor"
    ],
    "schema_version": "pretooluse_decision@2"
  },
  "ceiling_gaps": [
    "missing_discoverability_runtime_row",
    "missing_redacted_command_evidence"
  ],
  "ceiling_status": "NEEDS_CEILING_EVIDENCE",
  "dedupe_contract": {
    "ceiling_noise_rule": "historical_duplicate_replay_and_cursor_batch_noise_is_non_blocking_without_current_v2_contradiction",
    "current_v2_contradiction_rule": "same_host_scope_unexplained_decision_risk_renderer_redaction_marker_contradiction_blocks_ceiling",
    "cursor_batch_rule": "same_invocation_timestamp_different_tool_path_risk_marker_is_not_duplicate",
    "fields": [
      "schema_version",
      "agent",
      "event_canonical",
      "mode",
      "session",
      "tool",
      "path",
      "command_category",
      "command_redacted",
      "invocation",
      "raw_tool_label",
      "normalized_tool",
      "payload_source",
      "classifier_trace",
      "renderer_trace",
      "risk",
      "outcome",
      "reason_codes",
      "block",
      "decision",
      "permission_decision",
      "marker_emitted",
      "context_suppressed",
      "cortex_context_emitted",
      "surface_context"
    ],
    "schema": "tes-hook-dedupe@1",
    "timestamp_rule": "same_semantic_different_timestamp_is_replay_history"
  },
  "discoverability_status": "NEEDS_EVIDENCE",
  "finding_counts": {
    "error": 0,
    "info": 0,
    "warning": 0
  },
  "findings": [],
  "floor_status": "PASS_BASIC",
  "helper_contract_status": "PASS",
  "legacy_schema": "tes-hook-health@1",
  "schema": "tes-hook-health@2",
  "sentinels": {
    "current": {
      "path": ".tes/runtime/hooks/executed.jsonl",
      "records": 7,
      "status": "OBSERVED"
    },
    "legacy": {
      "path": ".tes/hooks/executed.jsonl",
      "records": 0,
      "status": "ABSENT"
    }
  },
  "status": "PASS",
  "target": "/Users/murillo/Dev/tes-canary/codex",
  "version": "0.3.231"
}
{
  "state": "complete",
  "last_status": "PASS",
  "last_run": ".tes/postinstall-runs/20260630T124125Z-codex.json",
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
{
  "version": "0.3.231",
  "attached_surfaces": [
    "capsule",
    "hooks",
    "mcp",
    "root-context",
    "skills"
  ],
  "components": {
    "artifact_hygiene": "PASS",
    "command_trigger_parity": "PASS",
    "hook_config_hygiene": "PASS",
    "hook_runtime_health": "NEEDS_EVIDENCE",
    "mantra_gate_adoption": "OK",
    "mcp_registration": "PASS",
    "pretooluse_contract_reference": "PASS",
    "quality_gates_path": "NOT_APPLIED"
  },
  "negative_checks": {
    "host_connected_not_inferred": true,
    "os_residue_absent": true,
    "pretooluse_contract_reference_valid": true,
    "stale_codex_hooks_json_absent": true,
    "stale_discipline_path_absent": true,
    "vscode_not_part_of_agent_all": true
  }
}
os_residue:
/Users/murillo/Dev/tes-canary/codex/.DS_Store
/Users/murillo/Dev/tes-canary/codex/.claude/.DS_Store
/Users/murillo/Dev/tes-canary/codex/docs/.DS_Store
/Users/murillo/Dev/tes-canary/codex/docs/agents/.DS_Store
/Users/murillo/Dev/tes-canary/codex/.tes/.DS_Store
/Users/murillo/Dev/tes-canary/codex/.tes/bin/.DS_Store
/Users/murillo/Dev/tes-canary/codex/.tes/setup/.DS_Store
/Users/murillo/Dev/tes-canary/codex/.git/.DS_Store
codex_hook_path: safe
# POST-FINAL MATRIX
## cursor
/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python: can't open file '/.tes/bin/project_context_oracle.py': [Errno 2] No such file or directory
/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python: can't open file '/.tes/bin/project_alignment_oracle.py': [Errno 2] No such file or directory
/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python: can't open file '/.tes/bin/tes_map_oracle.py': [Errno 2] No such file or directory
       0
## claude
/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python: can't open file '/.tes/bin/project_context_oracle.py': [Errno 2] No such file or directory
/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python: can't open file '/.tes/bin/project_alignment_oracle.py': [Errno 2] No such file or directory
/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python: can't open file '/.tes/bin/tes_map_oracle.py': [Errno 2] No such file or directory
       0
## codex
/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python: can't open file '/.tes/bin/project_context_oracle.py': [Errno 2] No such file or directory
/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python: can't open file '/.tes/bin/project_alignment_oracle.py': [Errno 2] No such file or directory
/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python: can't open file '/.tes/bin/tes_map_oracle.py': [Errno 2] No such file or directory
       8

# REPAIR-ROUND-2 MATRIX (2026-06-30T14:06Z)

| Canary | HEAD | git status | context | align | map | pre-commit strict | .DS_Store |
|--------|------|------------|---------|-------|-----|-------------------|-----------|
| cursor | 44c80e7 | clean | PASS exit 0 | PASS exit 0 | PASS exit 0 | exit 0 | 0 |
| claude | 3fe7bc2 | clean | PASS exit 0 | PASS exit 0 | PASS exit 0 | exit 0 | 0 |
| codex | 6f9f118 | clean | PASS exit 0 | PASS exit 0 | PASS exit 0 | exit 0 | 0 |

Command bundle:

```bash
for t in cursor claude codex; do
  TARGET=/Users/murillo/Dev/tes-canary/$t
  python3 /Users/murillo/Dev/tilly-engineer-skills/scripts/project_context_oracle.py --target "$TARGET"; echo context:$?
  python3 /Users/murillo/Dev/tilly-engineer-skills/scripts/project_alignment_oracle.py --target "$TARGET"; echo align:$?
  python3 /Users/murillo/Dev/tilly-engineer-skills/scripts/tes_map_oracle.py --target "$TARGET"; echo map:$?
  git -C "$TARGET" hook run pre-commit; echo pre-commit:$?
  find "$TARGET" -name .DS_Store | wc -l
done
```
