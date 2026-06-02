---
tds_id: roadmap.goal_super_spec_tes_tts_low_severity_cleanup
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: TES TTS Low-Severity Cleanup

Status: open final cleanup line. Closes the remaining low-severity findings from
the 2026-06-02 systematic audit. Its closure marks convergence of the whole
remediation sequence.

Canonical artifact:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-low-severity-cleanup.md`

Current execution unit:
`LSC-001`

Ready prompt:
`LSC-001 (analise → correção → certificação → local commit)`

Prior line:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-audio-audit-resolver.md`
(AAR / W-3, locally closed).

Audit source:
`TES-TTS-SYSTEMATIC-ANALYSIS-2026-06-02.md`, P-LOW and W-LOW findings.

## Mantra Gate Snapshot

- `VERIFY`: the high/medium findings (P-1, P-2, P-3, W-1, W-3) are closed and
  green. What remains are low-severity quality/cleanup items.
- `SCOPE`: each item is small and independent; fix the objective ones, and for
  any that turn out to be intentional or risky, record the rationale instead of
  forcing a change.
- `BEST_PATH`: triage each item, fix or justify, certify with the suite per
  change. Do not let cleanup expand scope.
- `DOCUMENT`: this Super SPEC is the authority; this is the last line.
- `ORACLE`: the full oracle suite plus any item-specific fixture.
- `RESOLVE`: mixed camada — some items touch bundled helpers (delivered, defer
  bump like P-1); some are work-layer (oracles/docs). Classify per item.
- `STATUS`: `PASS_TO_EXECUTE`.

## Purpose

Close the low-severity tail so the audit converges, without inflating scope.
Some of these are objective defects worth a small fix; others may be acceptable
by design — in which case the honest outcome is a recorded justification, not a
change.

## Findings to triage

Product layer (bundled helpers — defer bump like P-1):
- IPv4-vs-version: `1.2.3.4` spoken as an IP (`classifier.py` IPV4 path).
- PATH accent truncation: `/home/joão` → `/home/jo` (`classifier.py` PATH_PATTERN).
- `verbalize_ir` assumes IR ordered by start (implicit contract).
- `combine_wav_files` silently drops a missing chunk and still reports PASS;
  buffered playback may play a non-existent file.
- read profile silently overrides explicit `--chunk-chars`/`--language`.
- `torch.load(weights_only=False)` in the prompt cache (mitigated; local 0600).

Work layer:
- dead reimplementation in `hot_path_span_matcher_oracle` (NameError if run).
- AST guard in `candidate_review_oracle` only scans its own source (info-level).
- ~20 redundant `OWNER-DECISION` docs in `docs/roadmap/tes-tts/`.

## Execution Units

| Unit | Focus | Boundary |
|------|-------|----------|
| LSC-001 | Triage + objective fixes | For each item: fix if objective and safe, or record why it stays. Add/extend fixtures where a fix changes behavior. Each behavior fix gets a same-input check. |
| LSC-002 | Certify + local commit | Full suite green; governed gates green; per delivered fix, record the release_identity deferral; local commit. |

## Required Loop

```text
analise -> correção -> certificação -> local commit
```

This is the final line: its closure does not create a new Super SPEC. Instead it
records convergence — every P- and W- finding in the audit closed or explicitly
deferred by an owner decision.

## Certification

```bash
python3 scripts/tes_tts_oracles_suite.py
python3 scripts/materialize_adapter.py all --check
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/tes_bump.py --governance-check
git diff --check
```

## Stop States

- `PASS`: each item fixed or justified, suite green.
- `DEGRADED`: an item could not be cleanly fixed — record the residue.
- `REGRESSION`: a fix broke a green oracle — stop and revert that item.
- `NEEDS_OWNER_DECISION`: an item needs a boundary call (e.g. deleting the
  OWNER-DECISION docs is a process decision, not a code defect).
- `SAFETY_BLOCKED` / `BLOCKED`: a lock or forbidden side effect would occur.

## Closure

This line is locally closed when LSC-002 records a `PASS`. There is no next
line: closure of this line is **convergence** of the 2026-06-02 audit
remediation sequence (SRH → OGR → LIH → PCC → AAR → LSC). At convergence, every
audit finding is closed or explicitly deferred, and the standing owner decisions
are: (1) the version/bundle bump for the bundled-helper fixes (P-1, P-2, P-3),
and (2) whether to consolidate the redundant OWNER-DECISION docs.
