---
tds_id: evidence.goal_maestro.execution_thermometer_installed_canary_2026_06_29
tds_class: evidence
status: active
consumer: maintainers, Goal Maestro authors, report renderer authors, and release reviewers
source_of_truth: false
evidence_level: L3
tver: 0.1.0
---

# Goal Maestro Execution Thermometer Installed Canary - 2026-06-29

## Decision

PASS. A fresh installed target generated the Execution Thermometer package for
package version `0.3.225` from installed Codex skill scripts, not from this
repository root.

## Scope

- Target: `~/Dev/tes-canaries/goal-maestro-thermometer-20260629T225000Z`.
- Bundle: `~/Dev/tes-canaries/runs/goal-maestro-thermometer-20260629T225000Z/tes-0.3.225-current.tar.gz`.
- Bundle sha256: `17333efd292b85889842984d478d9940302c35b60fdadc22ab43053d3aaba2d1`.
- Source commit: `f1b5dc99084bf51bfa840cce50c9d8c577e48337`.
- Installed version: `0.3.225`.

## Evidence

| Check | Result |
|-------|--------|
| `tes_bundle.py build --adapter all` | PASS, bundle source tree clean |
| `tes_install.py install --agent codex --attach all --bundle ...` | PASS, installed certification PASS |
| Installed `execution-thermometer-extract.mjs` | PASS, `unproven_metrics=0` |
| Installed `execution-thermometer-package.mjs` | PASS, local package generated |
| Package ownership marker | PASS, `.tes-execution-thermometer-package.json` proves TES ownership for the same run/package contract |
| Installed receipt `--check-only` | PASS |
| Installed HTML `--check-only --expect-loop L1` | PASS |
| `shasum -a 256 -c checksums.sha256` | PASS |
| `qlmanage -t` against generated HTML | PASS, local PNG thumbnail produced |

## Artifacts

- Local package: `.tes/execution-thermometer/packages/execution-thermometer-canary-20260629T225000Z/`.
- Markdown receipt hash: `7d370e6613fbbaed80912dae57e24b733c57ff96421559b2e5d0f3e89fec3259`.
- HTML report hash: `567513b8071db4f0f4a7ebcfc82e0007e5453bdf13c4e82b77e9f4ca83dd0373`.
- HTML open PNG hash: `9ad5ac34539214bc66a68639d91dc28ec7e744f1d3bd04d255d05db8a146ac3f`.
- Package manifest hash: `f836902e9ff74bff7d221fc95e72c73d026fbfa1a3a5eff65f7e45c435765c1b`.
- Canary ledger hash: `8e02c6a581d06a0498f9b2fd65ba9f61bcc368546ca663ed25df822c5d4f4fc3`.
- Extraction manifest hash: `52249380da92b496b10ccdc4e043c283050c5ebc5777b57b161e8c97869a8d26`.

## Boundaries

This proves the installed package path for a generic local canary target. It is
not a remote share, marketplace, telemetry, dashboard-server, or GitHub proof.
No network path was required for report/package generation or HTML opening.
