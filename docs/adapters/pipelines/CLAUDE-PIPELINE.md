---
tds_id: adapters.pipelines.claude
tds_class: adapter
status: active
consumer: claude code adopters and certification reviewers
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Claude Pipeline

The Claude pipeline materializes the neutral behavioral contract into Claude
Code instructions, plugin structure, and skills. It is the first adapter with a
declared behavior execution backend.

## Contract

- Contract manifest: `docs/mesh/CONTRACT-MANIFEST.yml`
- Adapter guide: `docs/adapters/CLAUDE.md`
- Adapter source: `src/adapters/claude/**`

## Materialization

| Area | Declaration |
|------|-------------|
| Source files | `src/adapters/claude/**` |
| Materialized files | `dist/adapters/claude/CLAUDE.md`, `dist/adapters/claude/.claude-plugin/**`, `dist/adapters/claude/skills/**` |
| Validation command | `npm run materialize:check` |
| Execution backend | `python3 scripts/context_mesh_run.py --backend claude-cli` |
| Evidence class | behavior candidate when raw run evidence is retained |

## Known Limits

- `claude-cli` executes through Claude Code, not a bare model API.
- The run may include Claude Code default context beyond the prompt assembled
  by the runner.
- Behavior certification applies only to the dataset hash, git head, backend,
  model, grader version, and run id declared in evidence.

## NO-GO

- Do not declare a fixture run as Claude behavior.
- Do not treat non-bare Claude Code execution as a hidden detail; report it in
  evidence limits.
- Do not change grader wording after a run without a new grader hash and
  changelog.
- Do not fix the runner reflexively when behavior evidence fails; classify the
  failure first.
