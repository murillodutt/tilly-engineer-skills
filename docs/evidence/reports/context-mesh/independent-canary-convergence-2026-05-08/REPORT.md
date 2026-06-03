---
tds_id: evidence.context_mesh.independent_canary_convergence_2026_05_08
tds_class: evidence
status: active
consumer: TES maintainers and certification reviewers
source_of_truth: false
evidence_level: L3
---

# Independent Canary Convergence Report - 2026-05-08

## Run Metadata

| Field | Value |
|---|---|
| Prompt path | `docs/install/INDEPENDENT-CANARY-CONVERGENCE.prompt.md` |
| Prompt version | `0.1.0` |
| Prompt SHA-256 | `d38f4b3fb469b0ccf1c186c9b96b896c1ea35a50d269c416fecffb42407b2eaf` |
| Run root | `~/Dev/tes-canaries/runs/20260508T135126Z/` |
| Journal | `docs/evidence/reports/context-mesh/independent-canary-convergence-2026-05-08/JOURNAL.md` |
| Starting TES HEAD | `2026990417787f85960ff70dc06852c98863b0a4` |
| Final TES HEAD | `2026990417787f85960ff70dc06852c98863b0a4` before evidence commit |
| Starting worktree | clean, `main...origin/main [ahead 1]` |

## Canary Matrix

| Canary | Remote | Commit | Result |
|---|---|---:|---|
| sampleproject | `https://github.com/pypa/sampleproject.git` | `621e4974ca25ce531773def586ba3ed8e736b3fc` | PASS |
| Ky | `https://github.com/sindresorhus/ky.git` | `61d6d66d27911001b9b4d57ab93139f9ad61384b` | PASS |
| Click | `https://github.com/pallets/click.git` | `fc6c7c47edd6110b6bd5a1a5297b2035214b0cd1` | PASS |
| Express | `https://github.com/expressjs/express.git` | `f873ac23124ffcff8c040b4bd257b32c29828d53` | PASS |
| Terraform import | `https://github.com/hashicorp-education/learn-terraform-import.git` | `7c3edec5ab8a84858e4a26ffe5e18e2047a09441` | PASS |
| Owned bootloaders | `https://github.com/pypa/sampleproject.git` plus simulated local governance | `621e4974ca25ce531773def586ba3ed8e736b3fc` | PASS |

## Findings

No TES source bug was found in this independent run.

One operational gap was intentionally exercised: helpers-only install leaves
adapter triggers unapplied. `tes_update.py plan` reported
`runtime_trigger_status=DRIFT` and `recommended_update_scope=adapter-config`
for the owned-governance canary. Running the shipped adapter installer repaired
the target without overwriting project-owned `AGENTS.md` or `CLAUDE.md`; the
post-adapter planner returned `runtime_trigger_status=PASS`,
`update_status=CURRENT`, and `recommended_update_scope=none`.

An initial focused TDS/reference gate failed because the new journal was not
yet registered in `docs/tds/DOCS-INDEX.yml`. The evidence package adds TDS
index entries for both this report and the journal before final closure.

## Fixes Applied

No product code changed. The TES repository changes from this run are durable
evidence and TDS governance only:

- `docs/evidence/reports/context-mesh/independent-canary-convergence-2026-05-08/JOURNAL.md`
- `docs/evidence/reports/context-mesh/independent-canary-convergence-2026-05-08/REPORT.md`
- `docs/tds/DOCS-INDEX.yml`

## Commands Run

Canary commands:

```text
git clone --depth 1 <remote> <run-root>/<canary>
python3 scripts/install_mcp.py --target <canary> --adapter all --helpers-only --yes --json-only
python3 <canary>/.tes/bin/tes_init.py --target <canary> --yes
python3 scripts/project_context_oracle.py --target <canary>
python3 <canary>/.tes/bin/tes_update.py plan --target <canary> --json-only --timeout 15
python3 scripts/install_adapter.py --adapter all --target <owned-bootloaders> --yes
python3 scripts/root_context.py analyze --target <owned-bootloaders>
```

Focused gates:

```text
python3 scripts/field_reports.py --self-test
python3 scripts/tes_init.py --self-test
python3 scripts/project_context_oracle.py --self-test
python3 scripts/tes_update.py --self-test
python3 scripts/install_smoke.py --self-test
python3 scripts/platform_surface_oracle.py --self-test
python3 scripts/materialize_adapter.py all --check
python3 scripts/validate_reference_package.py
python3 scripts/validate_tds.py
```

Final gate:

```text
npm run commit:check
```

## Gate Results

| Gate | Result |
|---|---|
| Installed `.tes/bin/tes_init.py` across six canaries | PASS |
| `project_context_oracle.py --target` across six canaries | PASS |
| Online installed `tes_update.py plan --json-only` across six canaries after adapter convergence | PASS |
| `field_reports.py --self-test` | PASS |
| `tes_init.py --self-test` | PASS |
| `project_context_oracle.py --self-test` | PASS |
| `tes_update.py --self-test` | PASS |
| `install_smoke.py --self-test` | PASS |
| `platform_surface_oracle.py --self-test` | PASS |
| `materialize_adapter.py all --check` | PASS |
| `validate_reference_package.py` | PASS |
| `validate_tds.py` | PASS |
| `npm run commit:check` | PASS |

## Decision

GO.

All required gates passed, the real canaries passed, the durable journal exists,
and the only material drift found in the owned-governance canary converged
through the shipped adapter route without a TES source patch.

## Residual Risks

- Local TES HEAD is ahead of `origin/main`; canary update-planner freshness
  compared helper files against remote commit
  `c7147c47038c66e30d214af2bb8f779f40fc8afb`, while this run records local
  HEAD `2026990417787f85960ff70dc06852c98863b0a4`.
- Project-owned root bootloaders are preserved, not automatically merged.
  Real installs still need reviewer review when local governance should absorb TES
  root trigger prose.
- The generated `PROJECT-CONTEXT.md` certification table necessarily records
  installed `.tes/bin/**` gate commands; the reviewer check found no `.tes/bin/**`
  pollution in Source Anchors or Recommended Deep Reads.
