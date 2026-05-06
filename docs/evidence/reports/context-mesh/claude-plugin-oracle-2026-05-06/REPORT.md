---
tds_id: evidence.context_mesh.claude_plugin_oracle_2026_05_06
tds_class: evidence
status: active
consumer: Claude adapter maintainers and certification reviewers
source_of_truth: false
evidence_level: L3
---

# Claude Plugin Oracle - 2026-05-06

## Decision

The Claude adapter has a local target-install oracle for the plugin package
shape.

## Oracle

```bash
python3 scripts/claude_plugin_oracle.py --self-test
```

The oracle installs the Claude adapter into a temporary project and verifies:

- `CLAUDE.md` exists;
- `.claude-plugin/plugin.json` exists and declares the package version;
- `.claude-plugin/marketplace.json` exists and declares the package version;
- `skills/tilly-guidelines/SKILL.md` exists;
- plugin skill paths are relative, contained, and resolvable;
- marketplace plugin source resolves to the installed adapter root.

## No-Claim

This closes local packaging/install shape. It does not claim Claude marketplace
publication, global desktop registration, or live Claude UI behavior.
