---
tds_id: roadmap.goal_super_spec_tes_tts_secret_redaction_hardening
tds_class: roadmap
status: proposed
consumer: maintainers, tes-tts maintainers, adapter authors, validation authors, and execution agents
source_of_truth: false
evidence_level: L1
---

# GOAL Super SPEC: TES TTS Secret Redaction Hardening

Status: locally closed product-security line. Closes the P-1 finding from the
2026-06-02 systematic audit — the redaction boundary no longer leaks governed
credential formats into delivered runtime. Release identity remains a separate
owner decision.

Canonical artifact:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-secret-redaction-hardening.md`

Current execution unit:
`closed locally after residual private-key/PEM hardening`

Ready prompt:
`none; release identity remains separately deferred`

Audit source:
`TES-TTS-SYSTEMATIC-ANALYSIS-2026-06-02.md`, finding P-1.

## Execution Record (2026-06-02)

- SRH-001 DONE: `benchmarks/tes-tts/secret-redaction-fixtures.json` (19 cases) and
  `scripts/tes_tts_secret_redaction_oracle.py` created; observed FAIL against the
  baseline runtime — 13 formats leaked, proving the test catches P-1.
- SRH-002 DONE: `scripts/tes_tts_runtime_classifier.py:30-40` rewritten —
  `SECRET_PATTERN` is now case-insensitive with compound names and greedy
  capture; new `PREFIX_SECRET_PATTERN` covers `sk-`/`gh?_`/`github_pat_`/`AKIA`;
  `redact_secret_like_values` applies it. 16 insertions, 2 deletions.
- SRH-003 CERTIFY: secret_redaction, fixture_schema, instruction_normalizer all
  PASS. The 3 runtime-behavior oracles (runtime_ir, hot_path_span_matcher,
  fast_path) report only `fixture version drifted` (audit finding W-1); with the
  version-gate bypassed they pass 0 behavior failures, proving no regression.
  All governed gates PASS (materialize/tds/doc-size/ref-graph/ref-package/git
  diff). Protected invariants intact: `api_key=`, `token=`, `MY_PASSWORD=`,
  `Bearer`, and the non-secret negative case still behave as before.
- HISTORICAL STOP STATE `NEEDS_OWNER_DECISION`: `tes_bump --governance-check` returns "no
  bump-triggering change" because `DELIVERED_BEHAVIOR_GLOBS` (`tes_bump.py:50`)
  does not list the `tes_tts_*` helpers, even though `tes_bundle.py:94-101`
  ships the classifier to `.tes/bin/**`. Owner must decide: (a) treat this as
  delivered behavior and bump/bundle, or (b) accept the helper as non-bumping
  and record the deferral. The residual closure keeps release identity deferred
  and allows local commit only; push/tag/publish/sync remain unauthorized.
- RESIDUAL CLOSURE: the senior audit found remaining leaks for `private_key=`,
  `ssh_private_key=`, `PRIVATE_KEY=`, and PEM private-key blocks. The fixture
  corpus now has 23 cases; `PEM_PRIVATE_KEY_PATTERN` and the governed key-name
  pattern close that gap. Observed red failure first, then `secret_redaction`,
  `runtime_ir`, `hot_path_span_matcher`, and `fast_path_spoken_rendering` all
  PASS. No push/tag/publish/sync.

## Mantra Gate Snapshot

- `VERIFY`: live repro confirms `access_token=`, `client_secret=`,
  `db_password=`, `TOKEN=`, `Token=`, and `sk-proj-*` pass unredacted, and
  `password=p@ssw0rd!` leaks the `@ssw0rd!` suffix. The leaked value flows
  through `redacted_text` into the speech path.
- `SCOPE`: harden the secret-redaction boundary in
  `scripts/tes_tts_runtime_classifier.py`; do not touch unrelated runtime
  surfaces.
- `BEST_PATH`: make the failure falsifiable with an adversarial fixture and a
  dedicated redaction oracle first, then repair the pattern as governed data,
  then certify.
- `DOCUMENT`: this Super SPEC and one ready `SRH-001` prompt are the authority.
- `ORACLE`: every redaction claim must be proven by a dedicated redaction
  oracle over the adversarial fixture, not by inspection.
- `RESOLVE`: delivered behavior — a version/bundle decision is required before
  closeout (see `release_identity`). No release, push, tag, publish, or sync in
  this line.
- `STATUS`: `PASS_TO_EXECUTE`.

## Purpose

Make the `tes-tts` redaction boundary actually keep its promise. The skill
states that API keys, tokens, passwords, private keys, and bearer tokens are
redacted before speech, and that redaction overrides exact/literal/raw/verbatim
requests. The current implementation only covers the `key=value` form (lowercase
exact, or uppercase with a leading character) plus `Bearer <token>`, and
truncates values at the first special character. The goal is full-value
redaction of the canonical credential shapes, proven by a dedicated oracle,
without changing any unrelated runtime behavior.

## Certified Context

- Baseline last-known-good: commit `adebd5d` ("Improve TES TTS protected matcher
  runtime"), runtime VERSION `0.3.157` (`scripts/tes_tts_runtime_types.py:22`).
- Redaction lives in `scripts/tes_tts_runtime_classifier.py:30-92`
  (`SECRET_PATTERN`, `BEARER_SECRET_PATTERN`, `redact_secret_like_values`); the
  token is `REDACTION_TOKEN = "[REDACTED_SECRET]"`.
- This helper is a delivered runtime file: it ships in `tes_bundle.py`
  `HELPER_FILES` and installs to `.tes/bin/**`. Changing its behavior is
  delivered behavior under `release_identity`.
- `redacted_text` (classifier `:519,532,576`) flows downstream into the speech
  path, so a leak is spoken or persisted in request-local provider text.
- No dedicated secret-redaction oracle exists today. Scattered secret fixtures
  exist (`fixture_schema_oracle.py:360`, `instruction-normalizer-fixtures.json`),
  but no oracle systematically exercises the leaking formats — which is why the
  leak shipped.
- `regression_guard` doctrine already names the root cause: "narrow literal
  lists in runtime code … are regression seeds." The fix must move coverage
  toward governed pattern data, not a longer hand-list.

## Protected Invariants (must survive the fix)

- Already-working redaction must keep working: `api_key=`, `MY_PASSWORD=`,
  `APIKEY=`, and `Bearer <token>` must still redact.
- Source text stays immutable; only `redacted_text` / request-local provider
  text is altered.
- No command execution, no user-text summary, no provider-out-of-scope behavior.
- The redaction count and `[REDACTED_SECRET]` token contract stay stable for
  consumers that read them.
- No new runtime dependency; the core stays dependency-free.

## Non-Objectives

- no entropy-based or ML secret detection — pattern/data hardening only;
- no full secret-scanner parity (this is read-aloud safety, not a CI scanner);
- no release, push, tag, publish, version bump executed inside this line (the
  version/bundle decision is recorded for the owner, not performed here);
- no change to provider, chunking, latency, or language behavior;
- no proactive `speak` behavior.

## Target Coverage

The hardened redaction must fully redact (value never appears in
`redacted_text`):

```text
key=value, any case:        api_key=, API_KEY=, Api_Key=, password=, PASSWORD=,
                            Token=, SECRET=, token=
compound names:             access_token=, refresh_token=, client_secret=,
                            db_password=, aws_secret_access_key=
special-char values:        password=p@ssw0rd!   (no suffix leak)
bearer:                     Authorization: Bearer <token>   (already covered)
standalone prefixes:        sk-…, sk-proj-…, ghp_…, gho_…, AKIA…, PEM blocks
```

Out of target (acceptable to leave): free-prose secrets ("the password is
hunter2") — undetectable by pattern without unacceptable false positives.

## Execution Units

| Unit | Focus | Boundary |
|------|-------|----------|
| SRH-001 | Adversarial fixture + dedicated redaction oracle (the failing test) | Create `benchmarks/tes-tts/secret-redaction-fixtures.json` and `scripts/tes_tts_secret_redaction_oracle.py` that assert full-value redaction over Target Coverage; the oracle must FAIL against the current runtime (observed failure proven). No runtime change in this unit. |
| SRH-002 | Repair `SECRET_PATTERN` as governed data | Rewrite the pattern: case-insensitive, compound names, greedy capture to whitespace, known standalone prefixes. Smallest change that turns SRH-001 green while every Protected Invariant still holds. |
| SRH-003 | Certify and propagate | Run the full certification set; refresh the bundle so `.tes/bin/**` matches source; record the `release_identity` version/bundle decision for the owner; local commit on convergence. |

## Required Loop

```text
analise -> correção -> certificação -> local commit
```

Concretely, per unit:

```text
execute (build the failing test, then the fix)
-> analyze (observe the leak, name the cause)
-> fix (smallest governed-data repair)
-> certify (dedicated oracle + full set green, invariants intact)
-> local commit (with release_identity decision recorded)
```

The loop runs once per unit and stops at convergence — it must not spawn a new
unit by habit. If SRH-002 turns SRH-001 green with all invariants intact and the
full set passes, the line converges; do not invent SRH-004.

## Certification

```bash
python3 scripts/tes_tts_secret_redaction_oracle.py --self-test
python3 scripts/tes_tts_runtime_ir_oracle.py --self-test
python3 scripts/tes_tts_hot_path_span_matcher_oracle.py --self-test
python3 scripts/tes_tts_fast_path_spoken_rendering_oracle.py --self-test
python3 scripts/tes_tts_instruction_normalizer_oracle.py --self-test
python3 scripts/tes_tts_fixture_schema_oracle.py --self-test
python3 scripts/materialize_adapter.py all --check
python3 scripts/validate_tds.py
python3 scripts/validate_doc_size.py
python3 scripts/validate_reference_graph.py
python3 scripts/tes_bump.py --governance-check
git diff --check
```

`scripts/tes_tts_secret_redaction_oracle.py` is created by SRH-001 before it is
required outside that unit. The runtime-behavior oracles in the set carry the
known version-drift caveat (audit finding W-1); re-pin or repair under that line,
not this one — but SRH-002 must not regress any case those oracles cover.

## Stop States

- `PASS`: SRH-001 failed first, SRH-002 made it pass, all invariants intact,
  full set green.
- `DEGRADED`: redaction improved but a Target Coverage row still leaks; record
  which and why before closure.
- `REGRESSION`: a previously-redacting case (`api_key=`, `Bearer`, etc.) stopped
  redacting — stop and revert.
- `NEEDS_OWNER_DECISION`: the `release_identity` version/bundle decision, or any
  scope beyond pattern/data hardening (entropy/ML detection), needs maintainer
  approval.
- `SAFETY_BLOCKED`: the fix would expose a secret, execute a command, write
  global config, or perform push/tag/publish/sync.
- `BLOCKED`: continuing would violate an existing lock.

## Closure

This line is locally closed when the residual private-key/PEM cases, the full
TTS oracle suite, and `commit:check` pass, and the local commit records the
convergence. Closure does not authorize push, tag, publish, or sync; those
remain separate owner decisions.
