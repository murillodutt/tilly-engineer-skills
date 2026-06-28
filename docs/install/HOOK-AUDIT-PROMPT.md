---
tds_id: install.hook_audit_prompt
tds_class: adapter
status: active
consumer: adopters, installing agents, and package maintainers
source_of_truth: true
evidence_level: L2
tver: 0.1.2
---

# TES Hook Audit Prompt

Use this prompt once inside each TES-installed host. Each run certifies the
current host's native hook behavior and may compare the other hosts only by
installed config, ledger history, or safe hook-entrypoint simulation.

```text
Analyze the TES agent hooks present in this project and generate an objective
report for the TES team.

Use the source-package `docs/architecture/PRETOOLUSE-CONTRACT.md` as the
canonical PreToolUse contract when available. This audit must distinguish the
floor contract (`PASS_BASIC`) from the ceiling contract (`PASS_CEILING`): a host
can be operationally healthy while still missing ceiling-grade reason codes,
classifier trace, discoverability, renderer parity, or ledger analytics proof.

Do not push, tag, release, publish, use secrets, or perform destructive
actions. You may run read-only local diagnostics and exactly one safe native
write/edit smoke for the current host. If a hook runtime ledger records this
analysis, treat that as runtime evidence, not product work.

This is a per-host native audit. Do not fail the current run only because
another platform's native tool is unavailable in this host. Mark other hosts as
CONFIGURED, OBSERVED from prior ledger records, CONTRACT_SIMULATED, or
NEEDS_EVIDENCE. A native-smoke failure is verdict-bearing only for the host that
is actually running this prompt.

Use installed-target evidence only. Inspect these paths when present:
- .tes/tes-install-lock.json
- .tes/postinstall.json
- .tes/runtime/hooks/executed.jsonl
- .tes/hooks/executed.jsonl only as legacy or residue
- .tes/bin/tes_install.py
- .tes/bin/pretooluse_kernel.py
- .tes/bin/pretooluse_session.py
- .tes/bin/installed_certification_oracle.py
- .tes/bin/mantra_gate_adoption_oracle.py
- .claude/settings.json
- .codex/config.toml
- .codex/hooks.json only as residue or unexpected config
- .cursor/hooks.json

Run only commands that exist in installed targets:
- python3 .tes/bin/installed_certification_oracle.py --target . --json-only
- python3 .tes/bin/mantra_gate_adoption_oracle.py --target .
- python3 .tes/bin/tes_install.py status --target .
- python3 .tes/bin/tes_install.py hook-health --target . --json-only --agent <current-host>
- python3 -c 'import sys; sys.path.insert(0, ".tes/bin"); import pretooluse_kernel; print("PRETOOLUSE_KERNEL_IMPORT_OK")'
- python3 -c 'import sys; sys.path.insert(0, ".tes/bin"); import pretooluse_session; print("PRETOOLUSE_SESSION_IMPORT_OK")'

Use `--agent <current-host>` for the final per-host hook-health run. Omit it
only when intentionally auditing the all-configured-host aggregate. A per-host
native audit must report `ceiling_evidence_scope.claim_scope=current_host`,
`ceiling_evidence_scope.current_host=<current-host>`, and
`ceiling_evidence_scope.required_hosts` containing only that host.

If this is the TES source repository, run `npm run host-runtime:matrix` before
the installed-target checks. If this is an adopter target, mark that source gate
N/A. Do not run package-source-only checks such as attach_health_oracle.py or
cortex_runtime.py --self-test unless those files and their fixtures are present
inside the installed target.

Exercise the current host's PreToolUse with a safe native governed mutation
before the final hook-health run. Use the host's normal file editing tool, not
shell redirection:
- Claude Code: create or update .tes/runtime/hook-smoke/claude/SKILL.md with
  the native Write or Edit tool.
- Codex: create or update .tes/runtime/hook-smoke/codex/SKILL.md with native
  apply_patch.
- Cursor: create or update .tes/runtime/hook-smoke/cursor/SKILL.md with the
  native Write tool. If the current Cursor host exposes StrReplace, use
  StrReplace for the second same-path mutation and verify the ledger treats it
  as governed material work, even when anti-cry-wolf suppresses the marker.
  Report the native payload tool label from a redacted raw hook payload or from
  enough current-session ledger evidence to distinguish host labeling from TES
  classification. If a native Cursor StrReplace UI action is recorded as
  `tool: "Write"`, treat that as host payload labeling and not as a TES finding
  when the row still has `risk=material`, the governed path, and correct
  marker or anti-cry-wolf fields. Classify it as a finding only when the native
  payload explicitly records `tool: "StrReplace"` and the hook treats it as
  routine or silently non-governed. Redact file content, secrets, and unrelated
  payload fields; the required proof is the tool label, path, session, decision,
  risk, and marker state.

Expected native result: the current host should allow the edit and surface
`🍳 Flash-Fry` governed supervision exactly once for the session. For Codex and
Cursor governed allow paths, acceptable proof is either visible hook output or
runtime evidence that the hook emitted the marker (`marker_emitted: true` in the
ledger, or the matching `.tes/mantra-gates/pretooluse-*.seen` sentinel plus a
current host PreToolUse ledger record). Cursor `preToolUse` deny messages are
agent-visible, but governed allow messages may be ledger-only in the native UI;
do not classify ledger-proven Cursor allow supervision as a finding solely
because no visible allow banner was shown. A second native mutation of the same
governed path in the same session should be allowed without repeating the
marker. Remove only the smoke file you created if the test policy asks for a
clean worktree. Do not reuse another host's report as evidence for the current
host's native smoke.

Before any native forbidden-shell test, inspect the current host config and
confirm that the host's PreToolUse matcher covers shell tools. If shell coverage
is missing, do not run a command that would change state; report native
forbidden-shell as FAIL due to matcher coverage. If shell coverage exists, use a
safe command whose only purpose is to prove pre-execution blocking. The command
must not write a file, delete data, push, tag, publish, or reveal secrets if the
hook fails.

After the native smoke, use `python3 .tes/bin/tes_install.py hook --agent <host>
--target .` with JSON on stdin to simulate safe cross-host contracts. Simulate,
do not execute, forbidden commands such as `git push --force origin main`. Do
not write helper scripts, audit harnesses, or payload files inside the target
project for these simulations; if wrapper code is needed, use stdin or a
temporary directory outside the target. Do not place the forbidden token
sequence in the outer shell command, heredoc, comment, label, or inline script
used to build the simulation; construct it from fragments inside the payload
generator or use a temp file created without contiguous forbidden text on the
command line. The simulation must cover:
- Routine silence: a non-mutating Read or ordinary non-governed edit allows
  without `Flash-Fry`.
- Governed supervision: Write/Edit/MultiEdit/apply_patch on `/SKILL.md`,
  `AGENTS.md`, `CLAUDE.md`, `docs/adr/`, `docs/governance/`, or
  `.cursor/rules/` allows and surfaces `Flash-Fry`.
- Forbidden block: `git push --force origin main` and root-wipe patterns are
  blocked with the host-specific output contract.
- Host output contract: Claude Code and Codex block with exit 2 plus stderr;
  Cursor blocks with JSON `permission: "deny"` and exit 0.
- Matcher coverage: installed PreToolUse config must include the native mutation
  tools for the host under test. In Codex, verify `apply_patch`, `Bash`,
  `Shell`, and `shell` are covered and the hook can extract the path from the
  patch body. Codex `tool_input.command` is the canonical patch-body field, and
  defensive aliases `input`, `patch`, flat string `arguments`, and
  `arguments.*` should also be tested by safe hook-entrypoint simulation;
  alias-key failures are findings even when the canonical native path passes. A
  Codex config with only `Write|Edit|MultiEdit` is FAIL for Codex native
  coverage until the target is updated.
  In Cursor, if native `StrReplace` is observed or exposed, governed
  `StrReplace` on `/SKILL.md`, `AGENTS.md`, `CLAUDE.md`, `docs/adr/`,
  `docs/governance/`, or `.cursor/rules/` must classify as material/supervised
  rather than routine; anti-cry-wolf may suppress only the repeated marker, not
  the governed classification. Cursor reports must separate host payload
  labeling from TES classification: a native ledger row with `tool: "Write"`
  after a StrReplace UI action is host labeling evidence, while a safe
  hook-entrypoint simulation with explicit `tool: "StrReplace"` proves the TES
  kernel path directly.
- Discoverability: simulate an unknown mutating-looking tool such as
  `PatchFile` on a governed path such as `docs/adr/0010-future.md`. It must not
  classify as routine. A ceiling-ready kernel returns
  `outcome=needs_discoverability`, `risk=needs-discoverability`, and
  `reason_codes` including `needs_discoverability_unknown_mutation`. Runtime
  output must include `outcome=needs_discoverability` and
  `risk=needs-discoverability`; the final hook-health JSON must expose top-level
  `discoverability_status=NEEDS_DISCOVERABILITY` from installed evidence, not a
  source-matrix synthesis. The ledger row must include
  `classifier_trace.unknown_mutating=true`, `renderer_trace.output_contract`,
  and redacted payload evidence (`command_category`, not raw `command`). If an
  installed target still returns routine allow, report `PASS_BASIC` with a
  ceiling gap, not `PASS_CEILING`.
- Anti-cry-wolf: the same governed supervision in the same session is surfaced
  once, then silenced.
- Runtime ledger: `.tes/runtime/hooks/executed.jsonl` records agent, event,
  tool, session, and path for the native smoke; `.tes/hooks/executed.jsonl` is
  legacy residue only. Treat dual-agent ledger rows for the same invocation as
  parallel host projections. Treat repeated stable simulation ids with different
  timestamps as replay history, not duplicate hook execution. Report duplicate
  runtime hooks only when the same agent/event/invocation/decision/timestamp is
  repeated identically. Current v2 PreToolUse rows must carry a non-empty
  `invocation`; when a host or simulation payload omits a tool id, TES should
  stamp a stable synthetic invocation. For external dedup or analytics, do not
  key only on invocation and timestamp; include at least tool, risk, path or
  command, and session/mode when present. Cursor may batch multiple native tool
  projections under the same invocation/timestamp, and those rows are not
  duplicates when tool, path, risk, marker, or mode differ.
  Duplicate history, replay residue, and Cursor batch rows are warning/info
  hygiene only; they must not block `PASS_CEILING` by themselves. They block
  ceiling only when current `pretooluse_decision@2` rows for the same host/scope
  contradict decision, risk, renderer trace, redaction, or marker state.
- Hook-health split: JSON schema `tes-hook-health@2` keeps `status` as the
  legacy functional field and adds `floor_status`, `ceiling_status`, and
  `ceiling_gaps`. It must also expose top-level `helper_contract_status` and
  `discoverability_status`. `floor_status=PASS_BASIC` is not `PASS_CEILING`; the
  ceiling passes only when `ceiling_status=PASS_CEILING` and no `ceiling_gaps`
  remain.
- PreToolUse helper packaging: TES 0.3.218+ installs must include
  `.tes/bin/pretooluse_kernel.py` and `.tes/bin/pretooluse_session.py`, and both
  must import successfully from `.tes/bin`. Missing or non-importable helpers
  are FAIL because `tes_install.py` depends on them before rendering
  host-specific hook output. The final hook-health JSON must expose top-level
  `helper_contract_status=PASS` computed from installed `.tes/bin` helpers;
  source-only imports cannot fill this field. Do not require a standalone
  external PreToolUse package; the kernel and session coordinator are internal
  TES helpers.
- Cortex no-write: hook context may propose recall/alignment/capture, but the
  runtime must report no automatic durable writes.
- Fixture completeness: if `.tes/bin/cortex_runtime.py --self-test` exists,
  run it only when `.tes/bin/fixtures/cortex_host_contracts/*.json` is present.
  Missing fixtures are an installed packaging finding.

Compare hosts as separate contracts, not one universal hook:
- Claude Code: .claude/settings.json, SessionStart, PreToolUse, JSON additionalContext,
  and exit 2 plus stderr when blocking.
- Codex: .codex/config.toml as canonical config, SessionStart, PreToolUse, and
  exit 2 plus stderr when blocking.
- Cursor: .cursor/hooks.json, sessionStart, beforeSubmitPrompt, preToolUse, and
  JSON permission allow/deny.

Classify evidence using:
- PASS: proven by installed file, ledger, or installed oracle.
- CONFIGURED: config exists, but no runtime execution was observed.
- CONTRACT_SIMULATED: host-specific contract was proven by direct
  `.tes/bin/tes_install.py hook --agent <host>` simulation, not by the native
  editor/tool.
- OBSERVED: hook fired and the current runtime ledger proves it.
- STALE/RESIDUE: legacy or orphaned file not used as current proof.
- PASS_WITH_FINDINGS: expected hooks are functionally healthy, with non-blocking
  observations such as legacy residue or duplicate ledger records.
- NEEDS_EVIDENCE: claim cannot be proven from installed target evidence.
- FAIL: installed contract is contradicted by evidence.

PASS_WITH_FINDINGS allowance is closed and narrow: legacy
`.tes/hooks/executed.jsonl` and duplicate runtime records are non-blocking only
when `hook-health` classifies them as info/warning and they are not used as
proof for the current host's native smoke. Missing current-host native
PreToolUse, matcher gaps, or execution of a forbidden command is FAIL.
When hook-health JSON exposes `dedupe_contract`, verify its fields include
host, tool, risk, path or command category, session, mode, and marker state.
It must document `same_semantic_different_timestamp_is_replay_history` and
`same_invocation_timestamp_different_tool_path_risk_marker_is_not_duplicate`.
If present, `ceiling_noise_rule` must keep historical duplicate/replay/Cursor
batch noise non-blocking without a current v2 contradiction, and
`current_v2_contradiction_rule` must scope the blocker to the same host/scope
and not count anti-cry-wolf first-marker to silent-repeat renderer transitions
as contradictions.

Also classify PreToolUse maturity against the canonical contract:
- `PASS_BASIC`: routine silence, governed supervision, forbidden block,
  anti-cry-wolf, runtime evidence, host output contract, and Cortex no-write all
  pass for the current host.
- `PASS_CEILING`: `PASS_BASIC` plus stable decision reason codes, classifier
  trace, redacted host payload evidence, discoverability handling for new
  mutating tool names, host renderer parity, ledger analytics semantics, and
  drift source attribution. Required reason-code vocabulary is
  `routine_non_mutating`, `routine_non_governed`,
  `governed_surface_mutation`, `forbidden_class`,
  `anti_crywolf_suppressed`, `host_payload_labeling`,
  `patch_body_path_extracted`, `needs_discoverability_unknown_mutation`,
  `renderer_contract_projected`, and `cortex_advisory_no_write`.
- `NEEDS_DISCOVERABILITY`: host payload semantics or a new tool name are safe
  but not yet classifiable with enough evidence.

Ceiling evidence checklist: before reporting `PASS_CEILING`, verify installed
evidence names `reason_codes`, `classifier_trace`, `renderer_trace`,
`command_redacted=true` or `command_category`, `dedupe_contract`,
top-level hook-health `helper_contract_status=PASS`, `floor_status`,
`ceiling_status`, `ceiling_gaps`, per-host
`ceiling_evidence_scope.current_host`, non-empty PreToolUse `invocation`, and
top-level hook-health `discoverability_status=NEEDS_DISCOVERABILITY` or native
equivalent. Missing checklist item is a ceiling gap, not a floor failure.

Do not collapse `PASS` into `PASS_CEILING`. If only the floor is proven, say the
hooks are operational at `PASS_BASIC` and list ceiling gaps separately.

Report with this template:

# TES Agent Hooks Report

## Verdict
Status: PASS | PASS_WITH_FINDINGS | NEEDS_EVIDENCE | NEEDS_REVIEW | FAIL
Name the current host. Summary in 3-5 lines. Do not mark FAIL merely because a
different host was not natively available in this execution.

## Evidence
List inspected installed files and command results.

## Host Matrix
Claude Code:
- Config:
- Runtime evidence:
- Output contract:
- Findings:

Codex:
- Config:
- Runtime evidence:
- Output contract:
- Findings:

Cursor:
- Config:
- Runtime evidence:
- Output contract:
- Findings:

## Runtime Ledger
- Current ledger:
- Legacy/residue:
- Observed agents/events:
- Missing evidence:

## Mantra Gate / Cortex
- Forbidden block:
- Governed supervision:
- Routine silence:
- Native matcher coverage:
- Anti-cry-wolf:
- Hook output contract:
- Runtime ledger fidelity:
- Cortex advisory behavior:

## Ceiling Assessment
- Floor status:
- Ceiling status:
- Discoverability result:
- Missing ceiling evidence:
- Drift/discoverability risks:

## Findings
Use H/M/L severity labels with impact and recommendation.

## Final Recommendation
Separate blockers from improvements.
```
