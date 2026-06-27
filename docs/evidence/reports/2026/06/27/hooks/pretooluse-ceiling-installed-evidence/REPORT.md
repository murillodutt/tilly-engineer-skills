---
tds_id: evidence.hooks.pretooluse_ceiling_installed_evidence_2026_06_27
tds_class: evidence
status: active
consumer: TES maintainers, hook authors, installer authors, oracle authors, release reviewers, and hook-audit operators
source_of_truth: false
evidence_level: L3
tver: 0.1.0
---

# PreToolUse Ceiling Installed Evidence - 2026-06-27

Retention status: retained.

Privacy state: sanitized. This report uses neutral host names and synthetic target evidence only. It does not contain raw hook payloads, private project names, private filesystem paths, secrets, native editor transcripts, or canary project identifiers.

Evidence source: `python3 scripts/host_runtime_matrix_oracle.py --self-test`.

Evidence kind: installed-target simulation. The source matrix installs TES into a temporary target, runs the installed `.tes/bin/tes_install.py` hook entrypoint, and validates host-specific output contracts plus runtime ledger fields.

Native evidence status: `NEEDS_EVIDENCE`. No native editor smoke is claimed by this packet.

Canary replay status: `NOT_RUN_NO_AUTHORIZATION`. No `~/Dev/tes-canaries` replay was used for this packet.

Summary:

- Functional matrix: `PASS`.
- Installed helper contract: `PASS`.
- Discoverability status: `NEEDS_DISCOVERABILITY`.
- Hook-health status: `NEEDS_EVIDENCE`.
- Hook-health floor status: `NEEDS_EVIDENCE`.
- Hook-health ceiling status: `NEEDS_FLOOR`.
- Ceiling claim: not claimed.

Host attribution:

- Codex: contract-simulated installed hook entrypoint.
- Claude Code: contract-simulated installed hook entrypoint.
- Cursor: contract-simulated installed hook entrypoint.

Boundary:

This packet supports P0/P1 source and installed-simulation evidence only. It does not certify `PASS_CEILING`; native host evidence and any canary replay must be recorded separately before a ceiling claim.
