---
tds_id: adapters.pipelines.claude
tds_class: adapter
status: active
consumer: claude code adopters and certification reviewers
source_of_truth: true
evidence_level: L2
tver: 0.2.0
---

# Claude Pipeline

The Claude pipeline materializes the neutral behavioral contract into Claude Code instructions, plugin structure, and skills. It has retained v1 behavior evidence for the declared `claude-cli` backend.

## Contract

- Contract manifest: `docs/mesh/CONTRACT-MANIFEST.yml`
- Adapter guide: `docs/adapters/CLAUDE.md`
- Adapter source: `src/adapters/claude/**`

## Materialization

| Area | Declaration |
|------|-------------|
| Source files | `src/adapters/claude/**` |
| Temporary materialized files | `dist/adapters/claude/CLAUDE.md`, `dist/adapters/claude/.claude/skills/**`; purge after inspection |
| Validation command | `npm run materialize:check` |
| Execution backend | `python3 scripts/context_mesh_run.py --backend claude-cli` |
| Evidence class | structural plus retained v1 behavior evidence |

## Known Limits

- `claude-cli` executes through Claude Code, not a bare model API.
- The run may include Claude Code default context beyond the prompt assembled by the runner.
- Behavior certification applies only to the dataset hash, git head, backend, model, grader version, and run id declared in evidence.
- Source-only plugin metadata retention and target-install omission are checked by `python3 scripts/claude_plugin_oracle.py --self-test`; marketplace distribution remains outside the certified scope.

## NO-GO

- Do not declare a fixture run as Claude behavior.
- Do not treat non-bare Claude Code execution as a hidden detail; report it in evidence limits.
- Do not change grader wording after a run without a new grader hash and changelog.
- Do not fix the runner reflexively when behavior evidence fails; classify the failure first.
