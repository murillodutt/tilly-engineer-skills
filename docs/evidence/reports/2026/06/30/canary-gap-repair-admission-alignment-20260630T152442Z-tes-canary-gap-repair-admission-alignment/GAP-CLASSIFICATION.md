---
tds_id: evidence.canary_gap_repair_admission_alignment.gap_classification_20260630
tds_class: evidence
status: active
consumer: maintainers, Claude Opus execution agents, oracle authors, canary operators
source_of_truth: false
evidence_level: L2
---

# GAP-CLASSIFICATION — Four Confirmed Canary Gaps

Read-only reconfirmation source: `PREFLIGHT.md` (this packet).
Authority sources inspected before classification: `docs/install/INSTALL.md`,
`docs/install/COMMAND-TRIGGERS.md`, `docs/architecture/INSTALLATION-FRAMEWORK.md`,
`scripts/tes_install.py`, `scripts/tes_bundle.py`, `scripts/tes_init.py`,
`scripts/project_alignment_oracle.py`, `scripts/installed_certification_oracle.py`,
`scripts/public_bundle_oracle.py`, `scripts/field_reports.py`,
`scripts/project_context_oracle.py`.

Cross-host hook semantics confirmed against official docs (Claude Code, Codex
CLI, Cursor): none of the three hosts maintains a native runtime ledger; a
certifier can only know a hook *fired* if the hook itself wrote a runtime
record. Event casing differs by host (Claude/Codex PascalCase
`SessionStart`/`PreToolUse`; Cursor camelCase `sessionStart`/`preToolUse`).

---

## Gap 1 — Git, pre-commit, and Field Reports pre-push absent / admission contract

```text
Gap: Canary admission can claim readiness while Git, Field Reports pre-push,
     and strict pre-commit are absent or unproven.
Observed evidence:
  - Prior audit: git rev-parse failed in all 3 original canaries; no
    .git/hooks/pre-commit or pre-push; init manifest tes_field_reports_pre_push=false;
    QUALITY-GATES named persistent commit gates needs_review/unavailable.
  - This run (read-only, tmp-replay root): all 3 targets ARE Git work trees and
    DO have .git/hooks/pre-push, but NO .git/hooks/pre-commit and no
    .pre-commit-config.yaml / lefthook.yml. So pre-push exists yet pre-commit
    admission proof does not, and no package surface blocks readiness on its
    absence.
  - Authority: INSTALL.md:92 documents only a non-blocking pre-push Field
    Reports *drain* (core.hooksPath-aware); INSTALL.md:276 constrains TES hooks
    to "idempotent and advisory unless a separate hard gate blocks a risky
    action". There is NO documented pre-commit, and pre-push is telemetry, not
    an admission gate.
  - installed_certification_oracle.py has zero Git checks: it never asserts
    precommit_enforced, prepush_installed, or git_clean.
Source defect? no (TES correctly does NOT auto-install pre-commit for adopters)
Contract/doc defect? yes (no admission contract that blocks canary readiness on
    missing Git / pre-push / strict pre-commit proof)
Oracle defect? yes (no oracle materially proves Git admission for canary replay)
Canary-state defect? yes (replay session, not this SPEC, must init Git + gates)
Package fix required: New focused canary-admission oracle that, given a target,
    BLOCKS readiness when (a) target is not a Git work tree, or (b) Field
    Reports pre-push hook is absent on a Git-backed target, or (c) strict
    pre-commit proof is absent — and that NEVER emits precommit_enforced /
    prepush_installed / git_clean without material Git evidence. Plus a docs
    note that strict pre-commit is canary admission infrastructure, not TES
    default adopter behavior.
Replay-session requirement: Git init first, Field Reports pre-push install,
    strict pre-commit install, baseline commit, then run the admission oracle.
Acceptance oracle: new canary_admission_oracle.py --self-test — red-capable
    fixture where a target with NO Git repo but an admission report claiming
    readiness FAILS.
```

---

## Gap 2 — Installed canaries do not match prepared local ZIP (+ bytecode manifest entry)

```text
Gap: Installed canary manifest diverges from the prepared public ZIP, and the
     divergence includes a runtime bytecode cache entry.
Observed evidence:
  - Local ZIP (this run): version 0.3.231, source_commit 7a664a93,
    entry_count 378, pycache 0 (bundle manifest is clean).
  - Installed canaries (this run): 379 entries, source_commit d05b050a — a
    DIFFERENT commit from the ZIP, with __pycache__/*.pyc present under the
    delivered skill tes-engineering-discipline/scripts AND under .tes/bin.
  - Authority: INSTALLATION-FRAMEWORK.md:64 documents a bytecode cache under
    .tes/bin/** as expected runtime; INSTALL.md:92 git-excludes bytecode via
    .git/info/exclude. So installed bytecode under .tes/bin is runtime cache,
    but bytecode under a DELIVERED SKILL path (.agents/skills/.../scripts) and
    in staged setup is contamination the certifier does not flag.
Source defect? yes (packaging hygiene: tes_bundle.iter_files / is_os_residue and
    the duplicated OS_RESIDUE constants exclude only OS residue, never
    __pycache__/.pyc; nothing falsifiably rejects bytecode if it enters)
Contract/doc defect? partial (no documented contract that the distributed ZIP
    and staging exclude bytecode)
Oracle defect? yes (public_bundle_oracle and installed_certification_oracle do
    not reject __pycache__/.pyc; artifact_hygiene only scans OS residue)
Canary-state defect? yes (the specific 379-vs-378 / d05b050a-vs-7a664a93
    divergence is a stale install; replay must reinstall from the clean ZIP)
Package fix required: Treat build bytecode (__pycache__, *.pyc, *.pyo) as
    contamination distinct from OS residue: exclude from bundle staging/manifest
    and purge before ZIP; make public_bundle_oracle reject bytecode ZIP members;
    make installed_certification_oracle flag bytecode under delivered skills /
    staged setup. Add a bundle-readiness comparison of ZIP paths/hashes against
    the package index that rejects extra bytecode entries.
Replay-session requirement: reinstall canaries from the clean 0.3.231 ZIP
    (SHA 565ccb30) so installed manifest matches 378 / 7a664a93.
Acceptance oracle: tes_bundle.py --self-test (bytecode excluded),
    public_bundle_oracle.py (rejects bytecode member),
    installed_certification_oracle.py --self-test (flags delivered-skill
    bytecode), validate_reference_package.py.
```

---

## Gap 3 — Stale mesh.scaffold_only advisory contradicts post-align state

```text
Gap: postinstall.json carries mesh.scaffold_only as an active advisory after the
     run is complete/PASS, even when alignment later passes — current-state
     evidence contradicts fresh alignment.
Observed evidence:
  - This run: all 3 targets postinstall.json state=complete, last_status=PASS,
    yet advisories still include mesh.scaffold_only ("rode /tes-align").
  - Mechanism: tes_install.collect_advisories() (L2023) derives
    mesh.scaffold_only from project_alignment_oracle freshness.mesh_scaffold_only
    captured AT POSTINSTALL TIME. postinstall() SKIPs when state==complete
    (L1833) unless --force/--recover, so after /tes-align refines the mesh the
    advisory is never re-derived. Advisories also carry no run/timestamp scope,
    so a historical scaffold-era advisory is indistinguishable from a current
    blocker.
Source defect? yes (advisory truthfulness: advisories are not scoped to the run
    that produced them, and a stale scaffold advisory survives alignment PASS)
Contract/doc defect? yes (no contract that a post-align postinstall refresh is
    required before postinstall is used as admission evidence)
Oracle defect? partial (no oracle asserts advisory-vs-current-state freshness)
Canary-state defect? yes (the specific stale advisory in these targets clears on
    a post-align postinstall refresh)
Package fix required: Scope each advisory to its producing run (stamp run id /
    derived_at); on a forced/recovery postinstall that observes alignment PASS,
    mesh.scaffold_only MUST NOT remain as active current-state evidence; reports
    must distinguish historical advisory from current blocker. Canary replay
    handoff must require a post-align postinstall refresh.
Replay-session requirement: after /tes-align passes, run a postinstall refresh
    so the sentinel re-derives advisories from the aligned mesh.
Acceptance oracle: tes_install.py --self-test fixture where a target transitions
    scaffold -> aligned and the current sentinel/report no longer presents
    mesh.scaffold_only as active.
```

---

## Gap 4 — hook_runtime_health=NEEDS_EVIDENCE under overall installed PASS

```text
Gap: Installed certification can report overall PASS while native hook runtime
     evidence is incomplete, and per-host native claims are not separated.
Observed evidence:
  - Prior audit: installed certification PASS overall but
    hook_runtime_health.status=NEEDS_EVIDENCE; each canary had only the active
    host observed, other hosts configured-without-observation.
  - Code: installed_certification_oracle.evaluate() already keeps
    hook_runtime_health=NEEDS_EVIDENCE visible as a finding without collapsing
    the aggregate (L323-332), and a self-test guards it (L564-571). tes_install
    hook_health_payload already labels each agent x event OBSERVED / CONFIGURED /
    NOT_CONFIGURED / STALE and returns NEEDS_EVIDENCE for configured-only,
    with floor_status/ceiling_status separating PASS_BASIC from PASS_CEILING.
  - Authority + official host docs: no host has a native ledger; only the
    hook's own runtime record proves firing; configured-only hosts must be
    CONFIGURED_NOT_OBSERVED, never native PASS. A Claude-run correction must not
    claim native Codex/Cursor hook evidence.
Source defect? no (payload already models per-host states correctly)
Contract/doc defect? partial (canary admission must consume per-host native
    hook claims separately and forbid cross-host evidence filling)
Oracle defect? yes-at-admission (the NEW admission oracle must treat each host's
    native hook claim separately and refuse native PASS for configured-only or
    cross-host-filled hosts; ensure a red-capable fixture exists for cross-host
    evidence filling)
Canary-state defect? no (this is truthfulness, not a broken install)
Package fix required: The canary-admission oracle must read hook runtime
    evidence per host and classify configured-but-unobserved hosts as
    CONFIGURED_NOT_OBSERVED, blocking any native-PASS claim. Add/confirm a
    red-capable fixture that fails when one host's runtime records are used to
    fill another host's native claim.
Replay-session requirement: each host's native hook claim must be proven by that
    host's own runtime records; a Claude run may only claim Claude native.
Acceptance oracle: tes_install.py --self-test (configured-only NEEDS_EVIDENCE),
    installed_certification_oracle.py --self-test (NEEDS_EVIDENCE stays visible),
    and the new admission oracle's per-host fixture.
```
