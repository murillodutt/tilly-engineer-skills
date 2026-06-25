---
tds_id: evidence.memory_lifecycle.wave7_release_canary_20260526
tds_class: evidence
status: active
consumer: TES maintainers, Cortex maintainers, and release reviewers
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# TES Memory Lifecycle Wave 7 Release And Canary Report

This report closes the ADR 0001 implementation run at the local package-source level. It does not authorize or claim a remote tag, GitHub release, package publish, marketplace action, or broad commercial-use certification.

## Claim

ADR 0001 is implemented for the package-source contract through Wave 7:

- adapter lifecycle and subagent boundaries are explicit;
- scope normalization is shared by Cortex, Field Reports, events, and checkpoints;
- event ledger and checkpoint behavior are inspectable and sanitized;
- Cortex operator commands have explicit mutability classes;
- durable memory consolidation requires a lock, approved review, rollback reference, allowed evidence, and observed Cortex write evidence;
- release identity is resolved as package version `0.3.133`;
- the public bundle for `0.3.133` was regenerated from clean source commit `58e4772f393a368635cefe8e5c84e8b38b6c4a44`.

## Material Trail

| Wave | Commit | Result |
|------|--------|--------|
| Wave 1 | `2c13bc6b` | Adapter lifecycle matrix and subagent boundary certified |
| Wave 2 | `d7e8ea84` | Runtime scope envelope normalized |
| Wave 3 | `077c9dd7` | Lifecycle event ledger inspection added |
| Wave 4 | `748be759` | TTL checkpoint resume lane added |
| Wave 5 | `17c34ded` | Cortex operator layer added |
| Wave 6 | `58e4772f` | Consolidation gate added |
| Wave 7 | `0d314b44` | Clean bundle metadata, evidence, and canary closure |

## Release Identity

Package version: `0.3.133`.

Bundle: `docs/dist/0.3.133/tilly-engineer-skills-0.3.133.zip`.

Bundle SHA-256: `560e6d49c2c59f1927ef77169bbe934fb7ca6642697de84ac6e77a175b6dda4f`.

Bundle metadata:

- `source_commit`: `58e4772f393a368635cefe8e5c84e8b38b6c4a44`
- `source_tree_state`: `clean`
- `source_branch`: `main`

`npm run release:check` was not run because no release tag, fixed public installer ref, push, or remote release action was authorized in this loop. The correct status is local package-source closure with remote release certification deferred.

## Canary Replay

A disposable real-project canary was run from local notes kept outside the TES repository. Tracked evidence uses neutral placeholders only.

Commands, normalized:

```bash
git clone --depth 1 <remote> <canary-project>
python3 scripts/install_mcp.py --target <canary-project> --adapter all --helpers-only --yes --json-only
python3 <canary-project>/.tes/bin/tes_init.py --target <canary-project> --yes
python3 scripts/project_context_oracle.py --target <canary-project>
python3 <canary-project>/.tes/bin/tes_update.py plan --target <canary-project> --json-only --local-package-helpers
python3 <canary-project>/.tes/bin/tes_update.py plan --target <canary-project> --json-only --local-package-helpers --record-field-report
python3 <canary-project>/.tes/bin/consolidation_gate.py --self-test
python3 <canary-project>/.tes/bin/event_ledger.py --self-test
python3 <canary-project>/.tes/bin/checkpoint.py --self-test
python3 <canary-project>/.tes/bin/cortex.py --self-test
python3 <canary-project>/.tes/bin/cortex.py health --target <canary-project>
```

Observed result:

| Check | Result |
|-------|--------|
| Helper install | `INSTALLED` |
| Project context oracle | `PASS` |
| Update plan with local package helpers | `PASS` |
| `helper_contract_status` | `PASS` |
| `recommended_update_scope` | `none` |
| `update_available` | `false` |
| `runtime_trigger_status` | `NOT_APPLIED` |
| Recorded update probe | `PASS` |
| Consolidation gate self-test | `PASS` |
| Event ledger self-test | `PASS` |
| Checkpoint self-test | `PASS` |
| Cortex self-test | `PASS` |
| Cortex health | `PASS` |

The canary target was intentionally left as disposable local evidence. No canary files, private paths, remotes, or project identifiers are part of this repository.

## Closure Oracles

Focused and package gates used during Waves 1-7:

- `python3 scripts/platform_surface_oracle.py --self-test`
- `python3 scripts/adapter_parity_readiness.py --self-test`
- `python3 scripts/adapter_parity_readiness.py`
- `python3 scripts/scope_contract.py --self-test`
- `python3 scripts/event_ledger.py --self-test`
- `python3 scripts/checkpoint.py --self-test`
- `python3 scripts/cortex.py --self-test`
- `python3 scripts/cortex_operator_oracle.py --self-test`
- `python3 scripts/cortex_quality_oracle.py --self-test`
- `python3 scripts/cortex_mcp.py --self-test`
- `python3 scripts/consolidation_gate.py --self-test`
- `python3 scripts/public_bundle_oracle.py`
- `python3 scripts/build_public_docs.py --check`
- `python3 scripts/tes_bump.py --governance-check --json`
- `python3 scripts/private_vocabulary_oracle.py --self-test`
- `python3 scripts/private_vocabulary_oracle.py`
- `python3 scripts/validate_tds.py`
- `python3 scripts/validate_doc_size.py`
- `python3 scripts/validate_reference_graph.py`
- `npm run commit:check`

## Residual Risk

- Remote release certification is deferred until an explicit tag/ref/push or equivalent fixed public installer decision is authorized.
- One real-project canary supports this local closure but does not support a broad commercial-use claim.
- Cursor remains structural where behavior is not directly exercised by a retained backend run.
- MCP remains read-only; write-capable MCP behavior is not part of this implementation.

## Decision

Status: `GO` for local ADR 0001 package-source implementation closure.

Status: `DEFERRED` for remote release certification and commercial-use claim.
