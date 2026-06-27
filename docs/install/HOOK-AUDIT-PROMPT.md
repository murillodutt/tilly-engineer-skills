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
- python3 .tes/bin/tes_install.py hook-health --target . --json-only
- python3 -c 'import sys; sys.path.insert(0, ".tes/bin"); import pretooluse_kernel; print("PRETOOLUSE_KERNEL_IMPORT_OK")'

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
  native Write tool. Edit/MultiEdit/StrReplace coverage is optional unless the
  current Cursor host exposes those tools and its hook config declares them.

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
  defensive aliases `input`, `patch`, and `arguments.*` should also be tested by
  safe hook-entrypoint simulation; alias-key failures are findings even when the
  canonical native path passes. A Codex config with only `Write|Edit|MultiEdit`
  is FAIL for Codex native coverage until the target is updated.
- Anti-cry-wolf: the same governed supervision in the same session is surfaced
  once, then silenced.
- Runtime ledger: `.tes/runtime/hooks/executed.jsonl` records agent, event,
  tool, session, and path for the native smoke; `.tes/hooks/executed.jsonl` is
  legacy residue only. Treat dual-agent ledger rows for the same invocation as
  parallel host projections. Treat repeated stable simulation ids with different
  timestamps as replay history, not duplicate hook execution. Report duplicate
  runtime hooks only when the same agent/event/invocation/decision/timestamp is
  repeated identically.
- PreToolUse kernel packaging: TES 0.3.217+ installs must include
  `.tes/bin/pretooluse_kernel.py` and it must import successfully from
  `.tes/bin`. Missing or non-importable kernel is FAIL because `tes_install.py`
  depends on it before rendering host-specific hook output. Do not require a
  standalone external PreToolUse package; the kernel is an internal TES helper.
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

## Findings
Use H/M/L severity labels with impact and recommendation.

## Final Recommendation
Separate blockers from improvements.
```
