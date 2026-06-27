---
tds_id: evidence.hooks.pretooluse_strategy_2026_06_27_journal
tds_class: evidence
status: active
consumer: TES maintainers, hook authors, installer authors, oracle authors, and strategy reviewers
source_of_truth: false
evidence_level: L3
tver: 0.1.0
---

# PreToolUse Strategy Journal - 2026-06-27

Purpose: record strategy decisions and evidence for the TES PreToolUse subsystem without creating a parallel changelog. Git records history; this journal records why a hook strategy changed, what evidence protected it, and what remains deliberately out of scope.

Scope:
- Kernel and session strategy for PreToolUse.
- Host-specific contract preservation for Claude Code, Codex, and Cursor.
- Hook audit prompt evolution when it changes real evidence requirements.
- Runtime evidence from source gates and target-project installs, using neutral target names.

Out of scope:
- Release chronology already represented by commits and package versions.
- Raw terminal dumps.
- Private project names, private paths, secrets, or target-specific implementation details.
- Product roadmap status that belongs in roadmap ledgers or Super SPECs.

Entry format:

```text
## [YYYY-MM-DDTHH:MM:SSZ] loop | <title>

- Strategy decision:
- Protected contract:
- Evidence:
- Failure/gap/bug:
- Patch or no-patch reason:
- Next strategic cut:
- Stop condition:
```

## [2026-06-27T16:40:00Z] loop | PreToolUse becomes an internal subsystem

- Strategy decision: keep PreToolUse as an internal TES subsystem, not an external package. Split it into a host-neutral decision kernel, a future session/suppression coordinator, and existing host renderers plus ledger writer.
- Protected contract: routine actions stay silent; governed mutations surface `Flash-Fry` once per session/context; forbidden actions block before execution; runtime ledger records agent, event, tool, session, path/command, decision, risk, and marker state; Claude Code/Codex/Cursor keep distinct output protocols.
- Evidence: commit `c157338f` extracted `scripts/pretooluse_kernel.py`, added `scripts/pretooluse_kernel_oracle.py`, advanced local package identity to `0.3.217`, regenerated the local public bundle, and passed source gates plus a target-project local npx install.
- Failure/gap/bug: first host-runtime matrix run exposed missing installed helper delivery for `pretooluse_kernel.py`; npx self-test exposed executable-bit drift for `bin/tes.js`.
- Patch or no-patch reason: patched package source because both failures affected delivered runtime or local install behavior.
- Next strategic cut: extract anti-cry-wolf session/suppression state into a PreToolUse sibling module without changing host output, marker text, ledger schema, or blocking semantics.
- Stop condition: stop if parity cannot prove first governed mutation surfaces once, second same-session governed mutation suppresses, and forbidden actions still block independently of suppression state.

## [2026-06-27T16:45:00Z] loop | Journal boundary

- Strategy decision: maintain this journal as an evidence report, not a root `JOURNAL.md`.
- Protected contract: TDS documents must not recreate a parallel changelog, diary, or historical drawer; evidence journals are acceptable when tied to a scoped run or strategy line and indexed in `docs/tds/DOCS-INDEX.yml`.
- Evidence: `docs/tds/TDS-SPEC.md` states commits declare semantic history and TDS documents must not recreate a parallel changelog or diary; existing indexed journals live under `docs/evidence/reports/**/JOURNAL.md`.
- Failure/gap/bug: a root journal would compete with Git history and the roadmap ledgers.
- Patch or no-patch reason: create a scoped, indexed evidence journal for PreToolUse strategy.
- Next strategic cut: use this file only when a PreToolUse strategy decision changes or when an oracle/canary surfaces new hook evidence.
- Stop condition: do not append routine progress, command transcripts, or general release notes.

## [2026-06-27T17:20:00Z] loop | Session coordinator extracted

- Strategy decision: move anti-cry-wolf sentinel and same-session suppression out of `tes_install.py` into `scripts/pretooluse_session.py`, keeping it as an internal TES helper beside the decision kernel.
- Protected contract: the first governed PreToolUse context surfaces once per session/context, the second same-session governed context is silent, forbidden blocks always surface and block independently of suppression state, and Claude Code/Codex/Cursor keep their host-specific output protocols.
- Evidence: `scripts/pretooluse_session_oracle.py` exercises `tes_install.py hook_pretooluse` for all three agents and requires governed first/second parity plus repeated forbidden blocks.
- Failure/gap/bug: the first oracle draft used identical forbidden payloads without `tool_use_id`, so runtime ledger dedupe correctly collapsed the second row; the oracle now uses distinct invocations while keeping the same session.
- Patch or no-patch reason: patched package source because the session state was delivered hook behavior and remained coupled to the installer adapter.
- Next strategic cut: leave host-specific rendering and ledger writing in `tes_install.py`; consider extracting only when there is a red-capable renderer parity oracle.
- Stop condition: stop if target-project install cannot prove both `pretooluse_kernel.py` and `pretooluse_session.py` are delivered and `hook-health` remains PASS.

## [2026-06-27T17:55:00Z] loop | Cursor StrReplace classified as mutating

- Strategy decision: treat Cursor-emitted `StrReplace` as a mutating PreToolUse tool inside the host-neutral kernel.
- Protected contract: governed artifact mutations must supervise regardless of the host's exact edit-tool name; anti-cry-wolf may suppress repeated markers but must not downgrade governed mutation classification to routine.
- Evidence: target-project native Cursor audit observed `StrReplace` on a governed `/SKILL.md` path allowing silently because the 0.3.218 kernel did not list `StrReplace` in `MUTATING_TOOLS`.
- Failure/gap/bug: `StrReplace` was a real host-emitted mutation, so classifying it as routine contradicted the PreToolUse governed-supervision contract even though `hook-health` remained green.
- Patch or no-patch reason: patch package source and audit prompt because this is delivered hook behavior and the old prompt left the exact regression optional.
- Next strategic cut: keep the mutation-name set in the kernel until a host supplies a documented closed enum; do not add unobserved tool names without runtime or official-schema evidence.
- Stop condition: stop if the kernel oracle cannot prove governed `StrReplace` supervises while routine reads stay silent and forbidden shell blocks remain unchanged.
