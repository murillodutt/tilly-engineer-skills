---
tds_id: roadmap.goal_super_spec_adr_0005_correction_alignment
tds_class: roadmap
status: active
consumer: maintainers, engineering-discipline authors, regression-guard authors, oracle authors, ADR 0005 operators, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: ADR 0005 Correction And Alignment

Status: active correction SPEC derived from the ADR 0005 certification audit.

Purpose: close the remaining implementation defects in ADR 0005 asset transfer without treating release bump, bundle publication, tag, push, or administrative commit shape as part of the technical correction.

## Audit Result

The ADR 0005 asset-transfer lanes are locally implemented in existing assets, but two implementation defects prevent a clean technical certification:

1. Proof lane false green: the discipline oracle accepts generic `focused_proof` values such as `behavior`, which does not prove a red-capable fixture, reproducer, assertion, boundary, or interface-specific regression check.
2. Sanitization lane weak deletion test: the benchmark fixture deletion check can treat a textual reference as an active consumer, which can let stale prose mask an orphaned fixture.

Release identity, version bump, public bundle publication, remote push, and tag state are explicitly out of scope for this correction SPEC unless the owner separately authorizes release work.

## Correction Packet

| Field | Value |
|-------|-------|
| `target_asset` | `src/adapters/codex/skills/tes-engineering-discipline/**`, `.agents/skills/tes-engineering-discipline/**`, `scripts/validate_reference_package.py`, and directly correlated self-tests. |
| `current_failure` | ADR 0005 can be claimed implemented while the proof oracle accepts generic proof wording or while fixture deletion is justified by stale text. |
| `transferred_behavior` | Technical certification requires red-capable proof semantics and executable consumer evidence for fixture deletion. |
| `smallest_patch` | Tighten the existing proof oracle signals and deletion-test consumer classification; do not add a new skill, command, router, or governance document. |
| `proof` | Focused adversarial self-tests first, then `discipline_oracle.py --self-test`, `validate_reference_package.py`, `validate_tds.py`, `private_vocabulary_oracle.py`, `materialize_adapter.py all --check`, and `git diff --check`. |
| `regression_surface` | Engineering discipline closeout semantics, adapter/materialized parity, reference package validation, benchmark retention/deletion rules, and source-vs-installed layer classification. |
| `release_identity` | `TECHNICAL_ONLY_FOR_THIS_SPEC`; do not perform bump, bundle, tag, push, or publication in this execution unit. |
| `no_new_skill_evidence` | Existing discipline and reference-package validators already own the defects; new governance would hide the correction behind process. |

## Layer Boundary

This repository has two relevant layers:

1. Product source: `src/**`, `scripts/**`, `docs/**`, and benchmark fixtures.
2. Maintainer/development bootloaders: `.agents/**`, `.claude/**`, and local project mirrors used by maintainers.

Do not certify the source package by running installed-target checks against the repository root. Use source/package oracles for the source package. Use installed-target oracles only against a real installed fixture or target workspace.

## SPEC-000: Baseline And Scope Lock

Objective: Capture the current technical baseline and lock the correction to implementation defects only.

Tasks:

1. Capture `git status --short --branch --untracked-files=all`.
2. Read ADR 0005, the Proof lane SPEC, the Sanitization lane SPEC, the current discipline oracle, and the benchmark deletion-test implementation.
3. Confirm that release bump, public bundle, tag, push, and administrative commit history are out of scope for this execution.
4. Name correlated product-source and maintainer-bootloader surfaces before editing.

Focused oracles:

```bash
python3 src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test
python3 scripts/validate_reference_package.py
python3 scripts/validate_tds.py
git diff --check
```

Commit:
- none

## SPEC-001: Proof False-Green Fixture

Objective: Prove the discipline oracle currently accepts generic proof wording that is not red-capable.

Tasks:

1. Add or identify an adversarial plan where `oracle` is a broad closure gate and `focused_proof` is only a generic term such as `behavior`, `focused`, or `specific`.
2. Require that plan to fail with a message that demands a concrete fixture, reproducer, assertion, boundary, declared interface, public interface, or interface-specific regression check.
3. Preserve legitimate focused proof examples that name a concrete failure detector.

Allowed files:
- `src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py`
- `.agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py` if materialized parity is maintained directly in this repository

Forbidden:
- adding a new proof skill
- accepting generic words as proof
- requiring private-method or implementation-detail tests as the default

Focused oracle:

```bash
python3 src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test
```

Commit:
- `test(proof): reject generic focused proof`

## SPEC-002: Proof Existing Asset Patch

Objective: Patch the smallest existing discipline oracle behavior so broad closure gates must name red-capable proof with concrete detection semantics.

Tasks:

1. Remove generic proof signals that are valid adjectives but not evidence.
2. Keep concrete proof signals tied to executable or inspectable detection: fixture, reproducer, assertion, boundary, declared interface, public interface, exported behavior, or interface-specific regression check.
3. Update any mirrored local development oracle only if the repository maintains that mirror as an active bootloader surface.
4. Run materialization/parity checks after source changes.

Focused oracles:

```bash
python3 src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test
python3 .agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test
python3 scripts/materialize_adapter.py all --check
python3 scripts/validate_reference_package.py
git diff --check
```

Commit:
- `fix(proof): require concrete focused proof`

## SPEC-003: Sanitization Consumer Fixture

Objective: Prove the deletion-test validator distinguishes an executable consumer from a stale textual reference.

Tasks:

1. Add or identify a fixture where a removed benchmark file is mentioned in prose but no executable replacement oracle or self-test owns the behavior.
2. Require that case to fail as an orphaned or weakly justified deletion.
3. Preserve the valid case where behavior moved from the removed benchmark into an executable oracle self-test.

Allowed files:
- `scripts/validate_reference_package.py`

Forbidden:
- restoring deleted benchmark fixtures only to satisfy inventory
- counting arbitrary roadmap, changelog, or prose references as active consumers
- adding a new sanitization document or governance layer

Focused oracle:

```bash
python3 scripts/validate_reference_package.py
```

Commit:
- `test(sanitization): reject stale textual deletion evidence`

## SPEC-004: Sanitization Existing Asset Patch

Objective: Patch the smallest deletion-test rule so fixture deletion is justified by executable ownership or explicit no-runtime-claim evidence, not stale prose.

Tasks:

1. Classify consumers as executable owner, generated/index owner, explicit no-runtime claim, or stale textual reference.
2. For benchmark deletion, prefer executable oracle/self-test ownership.
3. Keep ADR 0005 language benchmark deletion valid only if `project_alignment_oracle.py --self-test` still proves the moved behavior.
4. Do not delete compatibility, release, public, adapter, or installed paths without retirement evidence.

Focused oracles:

```bash
python3 scripts/project_alignment_oracle.py --self-test
python3 scripts/validate_reference_package.py
python3 scripts/validate_tds.py
git diff --check
```

Commit:
- `fix(sanitization): require executable deletion evidence`

## SPEC-005: Source And Bootloader Alignment Certification

Objective: Certify the implementation at the correct layer without confusing source package state with installed target state.

Tasks:

1. Run source/package oracles for product source.
2. Run materialization/parity checks for adapter source and generated mirrors.
3. Do not run installed-target checks against the repository root as proof of product certification.
4. If installed-target certification is desired, create or use a real fixture target and report it separately from source-package certification.

Focused oracles:

```bash
python3 scripts/command_trigger_oracle.py --self-test
python3 scripts/platform_surface_oracle.py --self-test
python3 scripts/validate_reference_package.py
python3 scripts/materialize_adapter.py all --check
python3 scripts/private_vocabulary_oracle.py
git diff --check
```

Regression gate:

```bash
npm run commit:check
```

Commit:
- `chore(adr-0005): certify correction alignment` only if a retained closeout artifact is required.

## Final Delivery

Return:

1. `TECHNICALLY_CERTIFIED` or `DEGRADED`.
2. Proof false-green result before and after the patch.
3. Sanitization stale-reference result before and after the patch.
4. Source/package oracle evidence.
5. Bootloader/materialization evidence.
6. Explicit statement that release bump, public bundle, tag, push, and remote publication were not performed under this SPEC.

Valid statuses: `TECHNICALLY_CERTIFIED`, `DEGRADED`, `NEEDS_OWNER_DECISION`, `NEEDS_ASSET_PACKET`, `BLOCKED`.
