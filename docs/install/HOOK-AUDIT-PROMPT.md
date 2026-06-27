---
tds_id: install.hook_audit_prompt
tds_class: adapter
status: active
consumer: adopters, installing agents, and package maintainers
source_of_truth: true
evidence_level: L2
tver: 0.1.1
---

# TES Hook Audit Prompt

Use this prompt inside a TES-installed target project to compare Claude Code,
Codex, and Cursor hook behavior without relying on package-source-only oracles.

```text
Analyze the TES agent hooks present in this project and generate an objective
report for the TES team.

Do not push, tag, release, publish, use secrets, or perform destructive
actions. You may run read-only local diagnostics and exactly one safe native
write/edit smoke for the current host. If a hook runtime ledger records this
analysis, treat that as runtime evidence, not product work.

Use installed-target evidence only. Inspect these paths when present:
- .tes/tes-install-lock.json
- .tes/postinstall.json
- .tes/runtime/hooks/executed.jsonl
- .tes/hooks/executed.jsonl only as legacy or residue
- .tes/bin/tes_install.py
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

Do not run package-source-only checks such as attach_health_oracle.py or
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
  native Write tool.

Expected native result: the current host should allow the edit and surface
`🍳 Flash-Fry` governed supervision exactly once for the session. A second
native mutation of the same governed path in the same session should be allowed
without repeating the marker. Remove only the smoke file you created if the test
policy asks for a clean worktree. Do not reuse another host's report as evidence
for the current host.

After the native smoke, use `python3 .tes/bin/tes_install.py hook --agent <host>
--target .` with JSON on stdin to simulate safe cross-host contracts. Simulate,
do not execute, forbidden commands such as `git push --force origin main`. The
simulation must cover:
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
  tools for the host under test. In Codex, verify `apply_patch` is covered and
  the hook can extract the path from the patch body.
- Anti-cry-wolf: the same governed supervision in the same session is surfaced
  once, then silenced.
- Runtime ledger: `.tes/runtime/hooks/executed.jsonl` records agent, event,
  tool, session, and path for the native smoke; `.tes/hooks/executed.jsonl` is
  legacy residue only.
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
- OBSERVED: hook fired and the current runtime ledger proves it.
- STALE/RESIDUE: legacy or orphaned file not used as current proof.
- PASS_WITH_FINDINGS: expected hooks are functionally healthy, with non-blocking
  observations such as legacy residue or duplicate ledger records.
- NEEDS_EVIDENCE: claim cannot be proven from installed target evidence.
- FAIL: installed contract is contradicted by evidence.

Report with this template:

# TES Agent Hooks Report

## Verdict
Status: PASS | PASS_WITH_FINDINGS | NEEDS_EVIDENCE | NEEDS_REVIEW | FAIL
Summary in 3-5 lines.

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
