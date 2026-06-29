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

PASS. A fresh installed target generated the Execution Thermometer package from
installed Codex skill scripts, not from this repository root.

## Scope

- Target: `~/Dev/tes-canaries/goal-maestro-thermometer-20260629T185504Z`.
- Bundle: `~/Dev/tes-canaries/runs/goal-maestro-thermometer-20260629T185504Z/tes-0.3.224-current.tar.gz`.
- Bundle sha256: `8dfe577a7d7efe62963843dfac916e9d2263cb89cec63421afcf6a9681682d36`.
- Source commit: `7672c44feb8b3e7598476a13c674ab1971d6ee1b`.
- Installed version: `0.3.224`.

## Evidence

| Check | Result |
|-------|--------|
| `tes_bundle.py build --adapter all` | PASS, bundle source tree clean |
| `tes_install.py install --agent codex --attach all --bundle ...` | PASS, installed certification PASS |
| Installed `execution-thermometer-extract.mjs` | PASS, `unproven_metrics=0` |
| Installed `execution-thermometer-package.mjs` | PASS, local package generated |
| Installed receipt `--check-only` | PASS |
| Installed HTML `--check-only --expect-loop L1` | PASS |
| `shasum -a 256 -c checksums.sha256` | PASS |
| `qlmanage -t` against generated HTML | PASS, local PNG thumbnail produced |

## Artifacts

- Local package: `.tes/execution-thermometer/packages/execution-thermometer-canary-20260629T185504Z/`.
- Markdown receipt hash: `4a1cbd63908e7bf972c1c0c6e190f24f5a97ee7d9825f6ab7e140fa67d05770f`.
- HTML report hash: `db4d74272fc17c439a937fb1cf6b43341fbf3df1d5a05f7ad065d6a80f2c78ed`.
- HTML open PNG hash: `54c03dadb8bf2773bc48842bc48547a75f006e4ce69d69ab6694a43ccaece89f`.
- Package manifest hash: `f9a7dbb484f69f68d2875cf9687250bdcfda2beeba0dc30868b77256d7014f2b`.
- Canary ledger hash: `b8b73e3f00aed5c693f639e384cb08fb0bad2ca92e0e84e06dbc936b8db12b66`.
- Extraction manifest hash: `357ad104699cac8367281c2d093b441caa4931723b7dddd77080032872ffe773`.

## Boundaries

This proves the installed package path for a generic local canary target. It is
not a remote share, marketplace, telemetry, dashboard-server, or GitHub proof.
No network path was required for report/package generation or HTML opening.
