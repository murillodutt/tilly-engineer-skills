# Agent Hooks Certification

Use this reference when a canary loop must verify, fix, and certify the TES
agent hook feature set across source, installed target, and host-real evidence.

## Evidence Lanes

Do not collapse the lanes:

```text
source contract -> installed target materialization -> host-real transcript
```

- Source contract: static source checks and focused self-tests prove that the
  feature exists in package source and is protected by an oracle.
- Installed target: hook config, helper files, runtime ledger, hook-health,
  admission, and installed certification prove the feature materialized.
- Host-real transcript: `host_canary_loop.py` plus
  `canary_transcript_oracle.py` prove the host command actually ran and
  produced fresh, sanitized transcript evidence.

Transcript evidence never replaces `tes_install.py hook-health`,
`canary_admission_oracle.py`, `installed_certification_oracle.py`,
`pretooluse_contract_oracle.py`, or `hook_audit_prompt_oracle.py`.

## Matrix Helper

Use the matrix helper before and after a fix:

```bash
python3 .agents/skills/tes-host-transcript-canary/scripts/agent_hooks_certification_matrix.py \
  --repo . \
  --target <target> \
  --current-host claude \
  --host-loop-json <sanitized-host-loop.json> \
  --run-related-gates \
  --require-target \
  --require-host-transcript \
  --json-only
```

The helper checks every listed hook characteristic against the owning evidence
lane. It reports `PASS`, `FAIL`, `NEEDS_EVIDENCE`, or `NOT_RUN` per row and
returns an overall status.

## Finding Matrix Helper

Use the finding matrix helper when the claim is not only "the hook contract is
green", but "each retained audit finding has its own certification state":

```bash
python3 .agents/skills/tes-host-transcript-canary/scripts/agent_hook_finding_matrix.py \
  --repo . \
  --target <target> \
  --current-host claude \
  --host-loop-json <sanitized-host-loop.json> \
  --run-finding-gates \
  --require-target \
  --require-host-transcript \
  --json-only
```

The helper reads `references/agent-hook-findings.json`, binds each finding to
aggregate matrix rows and focused gates, and emits one state per finding:
`SOURCE_CERTIFIED`, `TARGET_CERTIFIED`, `HOST_CERTIFIED`, `HOST_NOT_APPLICABLE`,
`REFUTED`, `NEEDS_EVIDENCE`, `FAIL`, or `BLOCKED`.

Rules:

- A host-required finding is not certified by source gates alone.
- A host-not-applicable finding can certify through source or target gates.
- A refuted finding stays `REFUTED`; do not convert it into a green behavior
  claim.
- A finding gate that was not run is `NEEDS_EVIDENCE`, not implicit pass.
- Raw transcripts, prompts, tool inputs, and tool outputs remain outside the
  retained report.

## Feature Groups

The certification matrix is grouped by behavior:

- host support and config paths;
- common entrypoint and delivered helpers;
- host event coverage;
- SessionStart lifecycle and Claude two-phase rewake;
- PreToolUse matcher, pipeline, kernel, governed surfaces, decisions, and
  anti-cry-wolf;
- host-specific renderers for Claude, Codex, and Cursor;
- runtime ledger, redaction, provenance, dedupe, and gitignore hygiene;
- hook-health schema, event states, status vocabulary, floor/ceiling split,
  current-host provenance, and no cross-fill;
- Cortex advisory no-write boundary;
- related source and installed oracles.

## Fix Ownership

Patch only the owner of the failed row:

- hook config writers, entrypoints, renderers, ledger, hook-health, and
  install behavior: `scripts/tes_install.py`;
- host-neutral decision, payload normalization, governed surfaces,
  decisions, and discoverability: `scripts/pretooluse_kernel.py`;
- anti-cry-wolf session suppression: `scripts/pretooluse_session.py`;
- canonical behavioral prose: `docs/architecture/PRETOOLUSE-CONTRACT.md` or
  `docs/architecture/INSTALLATION-FRAMEWORK.md`;
- source oracle coverage: the existing focused source oracle that owns the
  failed surface.

Do not patch installed canary mirrors as the source of truth. Reinstall from the
rebuilt package after source repair.

## Loop

Use this loop:

```text
run matrix -> classify failed row -> run focused red-capable oracle ->
patch source -> rerun source oracle -> rebuild bundle when delivered behavior
changed -> install canary -> run host command -> audit transcript ->
rerun matrix and related gates -> decide
```

Run the same host command through `host_canary_loop.py` until its fresh
transcript hash supports the same claim as the related gates.

## Certification States

- `SOURCE_CERTIFIED`: all source rows pass and focused source oracles pass.
- `TARGET_CERTIFIED`: source rows pass, target materialization rows pass, and
  hook-health/admission/certification agree.
- `HOST_CERTIFIED`: target is certified and the fresh host transcript plus
  related gates support the same claim.
- `CERTIFIED_WITH_RESIDUALS`: the requested hook feature is proven but a
  separate host or adapter remains `CONFIGURED_NOT_OBSERVED`,
  `NEEDS_DISCOVERABILITY`, or `NEEDS_EVIDENCE`.
- `NEEDS_EVIDENCE`: source is plausible but target or host evidence is absent,
  stale, or insufficient.
- `FAIL`: source, target, or host evidence contradicts the declared behavior.

Do not report `HOST_CERTIFIED` when only source fixtures passed, when the
transcript is stale, or when one host's ledger is used to prove another host.
