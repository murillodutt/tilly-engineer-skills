# TES Host Transcript Canary Contract History

## Purpose

`tes-host-transcript-canary` preserves the local development workflow for using
real host execution transcripts as sanitized canary evidence.

## Why This Skill Exists

The TES canary loop became materially stronger when a host command could be run
through the real Claude surface and then audited through the local Claude Code
JSONL transcript. The workflow must persist across windows without inflating the
bootloader and without tracking raw transcript content.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| `scripts/canary_transcript_oracle.py` | Source oracle reads Claude Code JSONL and emits sanitized hashes, counts, statuses, and safe tool names. | high |
| `docs/install/AGENT-ORACLE-INVENTORY.md` | Canary inventory documents transcript evidence as a sidecar, not a replacement for admission. | high |
| `docs/architecture/INSTALLATION-FRAMEWORK.md` | Installation framework classifies transcript evidence as host-real canary side evidence. | high |
| Commit `ab10ea68` | Added the canary transcript evidence oracle and wired it into source gates. | high |
| Commit `c31d1f2e` | Published local bundle `0.3.240` after the transcript oracle was added. | high |
| Maintainer reflection, 2026-07-01 | Successful loops used Claude as a real execution command, then audited local transcripts to drive analysis, correction, replay, and convergence. | high |
| Maintainer directive, 2026-07-01 | Build this model as a development-layer skill instead of changing the bootloader. | high |
| Maintainer directive, 2026-07-01 | Turn the successful Claude-command loop pattern into an executable helper with a sanitized local ledger. | high |
| Maintainer directive, 2026-07-01 | Apply the `tes-goal-maestro` architecture pattern at compact scale: root routes, references own depth, templates preserve emitted shape, scripts prove fragile behavior. | high |
| Maintainer directive, 2026-07-01 | The harness must never optimize for the floor; it must pursue ceiling-grade host-real proof and reject floor-green certification. | high |
| Maintainer directive, 2026-07-01 | The harness is mandatory for TES construction and must own a post-execution gate so signal-only passes cannot masquerade as runtime convergence. | high |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| 2026-07-01 | `canary_transcript_oracle.py` across scripts/docs/package gates | source oracle, docs inventory, install framework, commit closure | The host transcript method already has a source oracle and should be persisted as workflow guidance. |
| 2026-07-01 | `.agents/skills` and `.claude/skills` local skill layout | mirrored local development skills with `SKILL.md`, `agents/openai.yaml`, and `docs/CONTRACT-HISTORY.md` | The new workflow belongs in local development skills, not root bootloaders. |
| 2026-07-01 | Claude command execution loops in current TES work | host command, transcript oracle, source patch, same-command replay, package/canary gates | The skill must preserve persistent analytical/corrective replay behavior, not only one-shot transcript auditing. |
| 2026-07-01 | `.tes/runs/` gitignore and skill `scripts/` support | local ignored run ledgers; bundled deterministic skill helpers | The loop helper can record replay memory locally without creating adopter-facing package behavior. |
| 2026-07-01 | `tes-goal-maestro` structure | `SKILL.md`, `references/`, `templates/`, `scripts/`, and contract history split responsibilities by loading cost and execution fragility | `tes-host-transcript-canary` should reuse the architecture, not the volume, so future windows can load only the needed host-loop depth. |
| 2026-07-01 | Maintainer ceiling directive in current session | "never the floor, always break through the ceiling" for this harness | Add a routed ceiling reference so future canary loops reject superficial passes without expanding scope. |

## Contracts Preserved

- Use host-real execution when a canary claim depends on host behavior.
- Use `canary_transcript_oracle.py` as the transcript evidence oracle.
- Run persistent analytical/corrective loops when host execution exposes a
  failure, gap, stale helper, false green, or unexplained drift.
- Replay the original host command after correction before broadening to final
  gates or claiming convergence.
- Use `scripts/host_canary_loop.py` when the loop needs command
  fingerprinting, stale-transcript rejection, and a local JSONL replay ledger.
- Keep `SKILL.md` as a router and move detailed host-command, transcript, and
  convergence behavior into one-level references.
- Load `references/ceiling-breakthrough.md` when a result looks merely green
  but the canary claim needs ceiling-grade host-real proof.
- Run the post-execution gate before closing TES construction work; downgrade
  missing host, runtime, or post-execution proof instead of claiming pass.
- Use `templates/host-canary-report.template.md` when a retained or chat
  evidence report needs a stable sanitized shape.
- Keep raw Claude Code JSONL local and unstaged.
- Record only sanitized hashes, counts, statuses, safe labels, output byte
  counts, return codes, and blockers.
- Treat transcript evidence as side evidence, never as a replacement for
  `canary_admission_oracle.py`, `installed_certification_oracle.py`,
  `git_gate_contract.py`, package validation, or host/runtime gates.
- Keep this workflow in `.agents/skills/**` and `.claude/skills/**` until the
  owner explicitly asks for a bootloader routing line.

## Known Failure Modes Prevented

- Losing the host transcript method when a new window starts.
- Claiming canary execution from agent memory without transcript evidence.
- Staging raw JSONL transcripts or subagent metadata.
- Treating a transcript hash as sufficient canary admission.
- Treating a one-shot transcript audit as convergence without replaying the
  original host command after a correction.
- Losing same-command replay memory between windows because no sanitized ledger
  recorded command fingerprint, transcript hash, failure class, and next action.
- Accidentally preserving raw host command output instead of byte counts and
  hashes.
- Inflating `SKILL.md` until every loop pays the full context cost.
- Copying the full `tes-goal-maestro` volume instead of transferring its
  modular architecture.
- Certifying floor-green evidence when host-real replay, fresh transcript,
  source ownership, or related gates remain weak.
- Certifying a signal-only execution as runtime convergence without asking the
  post-execution questions.
- Treating `tes-host-transcript-canary` as optional during TES construction.
- Broadening to package closure before classifying the host/transcript failure.
- Patching only a canary target while the source oracle or workflow remains
  stale.
- Inflating the root bootloader with a workflow that belongs in local skills.

## Relationship To Other Skills

- `tes-engineering-discipline` owns scope, maturity, and falsifiable closure.
- `tilly-build-test-fail-fix` owns persistent canary loops.
- `tilly-local-git-arsenal` owns local commit closeout.
- `tilly-skill-construction` owns the skill packaging and contract-history
  standard.
- `tes-host-transcript-canary` owns the host transcript evidence workflow only.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-07-01 | Created local development skill for host-backed transcript canary execution, mirrored across Codex and Claude skill folders. | Maintainer directive in current session; `scripts/canary_transcript_oracle.py`; commits `ab10ea68` and `c31d1f2e`. | high |
| 2026-07-01 | `tes.host_transcript_canary@0.1.1`: Added persistent analytical/corrective loop semantics: same host command replay, failure classes, stale transcript rejection, and convergence criteria. | Maintainer reflection in current session after successful Claude-command canary loops. | high |
| 2026-07-01 | `tes.host_transcript_canary@0.1.2`: Added `scripts/host_canary_loop.py` to record sanitized replay ledgers and enforce same-command/fresh-transcript checks. | Maintainer directive in current session; helper self-test. | high |
| 2026-07-01 | `tes.host_transcript_canary@0.1.3`: Added compact Goal-Maestro-style architecture with routed references for host command loops, transcript evidence, canary convergence, and a sanitized report template. | Maintainer directive in current session; structural comparison with `tes-goal-maestro`. | high |
| 2026-07-01 | `tes.host_transcript_canary@0.1.4`: Added `references/ceiling-breakthrough.md` so the harness rejects floor-green certification and pursues the strongest local host-real proof. | Maintainer ceiling directive in current session. | high |
| 2026-07-01 | `tes.host_transcript_canary@0.1.5`: Added the agent-hooks certification reference, report template, and matrix helper so future loops can verify, fix, and certify each TES agent hook characteristic across source, installed target, and host transcript lanes. | Maintainer request to certify the complete agent hook feature list through this harness. | high |
| 2026-07-01 | `tes.host_transcript_canary@0.1.6`: Added host-real canary modes, runtime memory canary guidance, transcript contamination classification, a runtime signal report template, and `runtime_signal_audit.py` so product-mode CORTEX memory claims can be certified without one-off audit scripts. | Runtime signal harness Super SPEC; script self-test fixtures for pass, missing ledger, missing marker, stale transcript, manual lookup failure, and `NEEDS_COST_BRAKE` claim alignment. | high |
| 2026-07-01 | `tes.host_transcript_canary@0.1.7`: Added mandatory TES construction semantics plus a post-execution gate reference and `post_execution_gate.py` so closeouts cannot call signal capture product/runtime convergence without host transcript, runtime signal, related gate, and post-execution proof. | Maintainer directive in current session; post-execution gate self-test. | high |

## Do Not Lose

The decisive behavior is not the transcript path itself; it is the chain from
real host execution to sanitized oracle evidence, failure classification,
minimal correction, original-command replay, ledger-backed continuity, and a
canary decision that still depends on primary TES gates. The root skill should
route; detailed loop behavior belongs in references, report shape belongs in a
template, fragile proof belongs in scripts, and ceiling posture belongs in a
routed reference. The workflow is now mandatory for TES construction; keep the
bootloader thin while making the routing obligation explicit.
