---
tds_id: architecture.adr_0003_1_installed_certification_and_field_reports_feedback_intake
tds_class: architecture
status: active
consumer: maintainers, installer authors, Field Reports maintainers, adapter authors, and release operators
source_of_truth: true
evidence_level: L1
tver: 0.1.0
---

# ADR 0003.1: Installed Certification And Field Reports Feedback Intake

Accepted on 2026-05-28 as an operational amendment to ADR 0003.

ADR 0003 remains the active Cortex MCP capability contract. This amendment
defines the certification and feedback rules required around that contract:
installed-target evidence, Field Reports intake, adapter parity, and release
hygiene must agree before TES can claim an installation or update is cleanly
certified.

## Context

ADR 0003 expanded Cortex MCP capability while preserving the project-scoped,
non-destructive, governed-write boundary. A real adopter installation then
reported sanitized Field Reports through GitHub issue #46. The public report
showed `install_mcp=INSTALLED` and Cortex certification events passing, while
installer initialization also produced `NEEDS_REVIEW` events.

A maintainer-local installation audit, retained outside the TES repository to
protect private project identity, correlated the public signal with concrete
installed-target findings:

- core TES runtime and MCP registration for Codex, Claude Code, and Cursor
  passed;
- Mantra Gate adoption on active installed bootloaders was degraded;
- command-trigger parity failed for Codex and Claude installed surfaces;
- a generated quality-gate command referenced a stale discipline-oracle path;
- `.DS_Store` residue appeared in TES-owned manifest and bundle surfaces;
- bundle metadata reported a dirty source tree.

The defect class is not "MCP failed to install." The defect class is "installed
runtime certification can overstate success when downstream adoption,
trigger-parity, release-hygiene, or feedback-intake evidence is partial."

## Decision

TES keeps Field Reports active as the official sanitized operational feedback
transport, but Field Reports issues must become product-feedback intake rather
than remote logs. A report has product value only when it is classified,
deduplicated, privacy-governed, and routed to an actionable maintenance class.

TES also adopts installed-target certification as part of installer and
postinstall truth. A local install/update claim must distinguish:

| State | Meaning |
|-------|---------|
| `PASS` | Core runtime, selected adapter surfaces, MCP config, installed-target adoption, command-trigger parity, and release hygiene all satisfy the claimed scope. |
| `PARTIAL` | Core runtime or MCP is usable, but a certification-relevant installed-target or release-hygiene check failed or degraded. |
| `NEEDS_REVIEW` | A concrete repair, maintainer decision, or explicit fallback route is required before claiming readiness. |
| `BLOCKED` | A safety, privacy, destructive, or unresolved contract failure prevents continuation. |

`INSTALLED` remains an operation status for a completed write. It is not by
itself a certification verdict.

## Field Reports Intake Classes

Field Reports classification must use product-maintenance classes that a
maintainer can act on:

| Class | Meaning |
|-------|---------|
| `PRODUCT_BUG` | TES delivered behavior is wrong, missing, stale, or contradictory. |
| `CERTIFICATION_GAP` | TES reports success while a required verifier is degraded, failing, missing, or too narrow. |
| `ADAPTER_DRIFT` | Codex, Claude Code, Cursor, or host-specific installed surfaces diverge from the shared contract. |
| `RELEASE_HYGIENE` | Bundle, manifest, version, provenance, residue, or public-release identity is unsafe to certify. |
| `DOCS_CONTRACT_DRIFT` | Public docs, generated target docs, skill docs, or governed indexes disagree with runtime behavior. |
| `LOW_SIGNAL_SUPPRESSED` | The drain contained only expected heartbeat/no-op evidence and should not create maintainer work. |

GitHub issue #46 is therefore actionable as:
`CERTIFICATION_GAP`, `ADAPTER_DRIFT`, and `RELEASE_HYGIENE`.

## Invariants

- Field Reports remain sanitized operational transport. They are not durable
  Cortex memory, not Event Ledger, not checkpoints, and not proof of release by
  themselves.
- Field Reports must never carry private target names, filesystem paths, branch
  names, remote URLs, prompts, code, diffs, file contents, stack traces,
  secrets, tokens, or raw user material.
- Public Field Reports may reference public issue numbers and sanitized
  fingerprints. Private canary and adopter identities stay outside tracked TES
  source, docs, evidence, fixtures, commits, tags, and release notes.
- Installed-target oracles are required for installation certification when the
  claim includes delivered adapter behavior.
- MCP config registration is separate from host connection. TES may certify
  `config_present` and self-test/handshake evidence; it must not infer
  `host_connected` from file presence.
- Preserve-mode installation may preserve user-owned files, but any preserved
  active TES bootloader that fails a required route or parity contract must be
  reported as `PARTIAL`, `DEGRADED`, or `NEEDS_REVIEW`.
- Release certification requires clean artifact hygiene or an explicit recorded
  exception. Dirty provenance cannot be silently described as sealed release
  identity.

## Consequences

Installer, postinstall, update, doctor, and Field Reports work must now share a
single certification vocabulary. Runtime repairs must not only make MCP usable;
they must also prevent false green claims when installed adapter surfaces are
stale.

The derived execution plan is:
`docs/roadmap/GOAL-SUPER-SPEC-tes-installed-certification-and-field-reports-hardening.md`.

## Rejected Alternatives

| Alternative | Rejection |
|-------------|-----------|
| Open a new ADR 0004 for Field Reports alone. | The evidence came from ADR 0003-adjacent MCP/Cortex installation and certification. A focused amendment keeps the decision lineage tighter. |
| Disable GitHub Field Reports because they can be noisy. | Issue #46 proved the channel can expose real product drift that local package gates missed. The right fix is classification and suppression, not removal. |
| Treat `INSTALLED` as enough when MCP config is present. | Installed helper/config success does not prove adapter adoption, command trigger parity, host recognition, or release hygiene. |
| Patch the private target project first. | Target projects are evidence surfaces. Portable TES defects must be fixed in package source and then replayed against neutral fixtures and private canaries. |
| Put private canary identifiers into tracked TES docs for traceability. | TES is a generic package. Private identifiers belong in maintainer-local notes. |
