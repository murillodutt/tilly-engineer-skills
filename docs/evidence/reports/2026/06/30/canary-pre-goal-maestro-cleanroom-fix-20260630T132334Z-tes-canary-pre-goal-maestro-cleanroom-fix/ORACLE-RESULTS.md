---
tds_id: evidence.canary_pre_goal_maestro_cleanroom_fix.oracle_results_20260630
tds_class: evidence
status: active
consumer: maintainers, canary operators, and Goal Maestro operators
source_of_truth: false
evidence_level: L2
---

# ORACLE-RESULTS
## cursor
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
    "findings": [],
    "status": "PASS"
  },
  "needs_review": [],
  "semantic_residue": {
    "applied": false,
    "contract_path": null,
    "findings": [],
    "status": "PASS",
    "warnings": [
      "no Semantic Residue contract declared under docs/agents/contracts/SEMANTIC-RESIDUE.yml"
    ]
  },
  "status": "PASS",
  "target": "/Users/murillo/Dev/tes-canary/cursor",
  "version": "0.3.231",
  "warnings": [
    "no Semantic Residue contract declared under docs/agents/contracts/SEMANTIC-RESIDUE.yml",
    "newest ADR docs/agents/DECISIONS/001-initial-operating-mesh.md introduces tokens absent from the active mesh: Markdown, Obsidian, super-spec-tier-1-product-truth"
  ]
}
[project-alignment] PASS
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
## claude
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
    "findings": [],
    "status": "PASS"
  },
  "needs_review": [],
  "semantic_residue": {
    "applied": false,
    "contract_path": null,
    "findings": [],
    "status": "PASS",
    "warnings": [
      "no Semantic Residue contract declared under docs/agents/contracts/SEMANTIC-RESIDUE.yml"
    ]
  },
  "status": "PASS",
  "target": "/Users/murillo/Dev/tes-canary/claude",
  "version": "0.3.231",
  "warnings": [
    "no Semantic Residue contract declared under docs/agents/contracts/SEMANTIC-RESIDUE.yml",
    "newest ADR docs/agents/DECISIONS/002-canary-parity-alignment.md introduces tokens absent from the active mesh: GLOSSARY, Markdown, initial-operating-mesh"
  ]
}
[project-alignment] PASS
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
## codex
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
    "findings": [],
    "status": "PASS"
  },
  "needs_review": [],
  "semantic_residue": {
    "applied": false,
    "contract_path": null,
    "findings": [],
    "status": "PASS",
    "warnings": [
      "no Semantic Residue contract declared under docs/agents/contracts/SEMANTIC-RESIDUE.yml"
    ]
  },
  "status": "PASS",
  "target": "/Users/murillo/Dev/tes-canary/codex",
  "version": "0.3.231",
  "warnings": [
    "no Semantic Residue contract declared under docs/agents/contracts/SEMANTIC-RESIDUE.yml"
  ]
}
[project-alignment] PASS
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
