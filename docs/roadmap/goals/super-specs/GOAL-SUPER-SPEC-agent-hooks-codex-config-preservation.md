---
tds_id: roadmap.goal_super_spec_agent_hooks_codex_config_preservation
tds_class: roadmap
status: proposed
consumer: maintainers, installer authors, hook authors, oracle authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: Agent Hooks Codex Config Preservation

Status: proposed execution packet for one isolated window.

Run this SPEC with `tes-host-transcript-canary` when host-real install behavior
is claimed. Source-only fixes may close as source/package increments, not as
installed host convergence.

## New-Window Prompt

```text
/goal Execute docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-agent-hooks-codex-config-preservation.md. Use a dedicated branch or worktree. Reproduce BUG-07 and PREC-01 first, patch the Codex config writer/remover surgically, preserve user TOML, run install smoke and package gates, and use tes-host-transcript-canary for any installed-host claim.
```

## Senior Framing

Protected baseline: H-01 and H-02 are already fixed. Codex marked hook blocks
must preserve adjacent user blocks, and user JSON configs must fail closed
instead of clobbering malformed files.

Open risk: the Codex TOML feature flag path is still asymmetric. Insert is
table-scoped; remove is line-global. A second precision risk exists when a new
`[features]` table is inserted before root keys.

Classification: `Platform`. This touches installer/uninstaller behavior and
target config preservation.

## Findings Owned

- BUG-07: Codex uninstall removes any `hooks = true` or `codex_hooks = true`
  line, even outside `[features]`.
- PREC-01: inserting `[features]` can capture root keys when root keys appear
  before any TOML table.

## Non-Goals

- Do not rewrite the whole Codex config subsystem.
- Do not add a TOML dependency unless a source-level proof shows the current
  parser strategy cannot be made safe.
- Do not touch Claude or Cursor JSON config behavior except through shared
  tests that prove no regression.
- Do not remove the H-01 END-marker compatibility path.

## Execution Rules

- Use a dedicated branch or worktree.
- If another spec changes `scripts/tes_install.py` or `scripts/install_smoke.py`,
  rebase and rerun all Codex install/uninstall fixtures.
- Preserve comments and unknown TOML content as much as the existing string
  editor allows. When unsure, refuse instead of clobbering.

## SPEC-000: Reproduce Current Damage

Before editing, prove BUG-07:

```bash
PYTHONPATH=scripts python3 - <<'PY'
from tes_install import remove_tes_codex_hook_text

before = """[features]
hooks = true

[integrations.github]
hooks = true
webhook = "https://example.invalid"

[other]
codex_hooks = true
"""
print(remove_tes_codex_hook_text(before))
PY
```

Expected before fix: non-`[features]` `hooks` or `codex_hooks` lines disappear.

Also create a fixture for PREC-01:

```toml
model = "x"

[workspace]
name = "target-project"
```

After `replace_or_insert_toml_feature(..., "hooks", "true")`, `model` must
remain a root key, not become part of `[features]`.

## SPEC-001: Scoped Codex Feature Removal

Required behavior:

- Remove `hooks = true` and legacy `codex_hooks = true` only inside the active
  `[features]` table.
- Preserve identical keys under any other table.
- Preserve the existing H-01 marked-block removal behavior.
- Output remains TOML-parseable.

Implementation guidance:

- Replace the global list-comprehension remover with a line scanner tracking the
  active table.
- Keep legacy cleanup only where TES historically wrote the flag.

## SPEC-002: Safe Feature Insertion

Required behavior:

- If `[features]` exists, update only that table.
- If no `[features]` exists and root keys are present, insert `[features]` after
  root-key block or at the end without reclassifying root keys.
- Preserve non-feature tables and comments.
- Output remains TOML-parseable through `tomllib`.

## SPEC-003: Red-Capable Install Smoke

Add fixtures to `scripts/install_smoke.py`:

- BUG-07 red: user `hooks = true` under a non-feature table survives uninstall.
- Legacy `codex_hooks = true` under a non-feature table survives uninstall.
- Canonical TES `[features] hooks = true` is still removed on uninstall.
- PREC-01 red: root keys stay root after insertion.
- Round trip is valid TOML.

Red capacity: reverting to the global remover or top-prepend insertion must
fail at least one fixture.

Required gates:

```bash
python3 scripts/install_smoke.py --route codex
python3 scripts/install_smoke.py --route all
python3 scripts/codex_plugin_oracle.py --self-test
python3 scripts/tes_install.py --self-test
python3 scripts/host_runtime_matrix_oracle.py --self-test
```

## SPEC-004: Installed Target Evidence

For a product claim, install the rebuilt package into a clean target and prove:

- existing foreign Codex TOML settings survive install/uninstall;
- TES hooks attach and detach correctly;
- hook-health reports expected configured/observed states;
- no raw private path or config content is retained as evidence.

Use `tes-host-transcript-canary` if a host-real Codex/Claude execution claim is
made. Otherwise close as package/installed-target only.

## SPEC-005: Release Identity And Closeout

Delivered installer behavior changed. Unless explicitly deferred:

```bash
python3 scripts/tes_bump.py patch --yes --json
python3 scripts/tes_bundle.py publish --adapter all --allow-dirty --gate
python3 scripts/build_public_docs.py
python3 scripts/public_bundle_oracle.py
python3 scripts/validate_reference_package.py
npm run commit:check
```

Acceptance: Codex uninstall no longer deletes user-owned feature flags outside
`[features]`, insertion no longer captures root keys, and install smoke proves
red capacity.
