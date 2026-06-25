# TES Prospect Contract History

## Purpose

`tes-prospect` is an explicit-invocation project-stress skill that pressures a plan or design before execution.

## Why This Skill Exists

DUTT use showed that a normal assistant can remain too reactive during design. `tes-prospect` exists to take over the stress-test loop after invocation: anticipate failure, expose hidden branches, and keep the next decision concrete.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| `tmp/tes-prospect/SKILL.md` | Minimal DUTT skill source for relentless plan interrogation. | high |
| Murillo directive, 2026-05-13 | DUTT has used both skills for more than two months with extraordinary results. | high |
| Murillo directive, 2026-05-13 | Skill enters radar only when explicitly invoked. | high |
| Murillo directive, 2026-05-13 | Approved a cognitive brake so the user can pause intensity without weakening the skill. | high |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| 2026-05-13 | `tes-prospect` | `tmp/tes-prospect/SKILL.md` only before migration | Incubated source promoted to canonical adapter source. |

## Contracts Preserved

- Activate only when explicitly invoked.
- After invocation, act proactively and predictively.
- Stress-test the whole plan until shared understanding exists.
- Walk the decision tree one branch at a time.
- Ask one question at a time.
- Explore the codebase instead of asking when local evidence can answer.
- Stop immediately on a cognitive brake, summarize state, and wait for explicit resume.

## Known Failure Modes Prevented

- Reactive assistants approving weak plans.
- Design branches advancing with hidden dependency order.
- Vague language surviving into implementation.
- Asking the user questions the repository can answer.
- Skill discovery activating during ordinary planning without explicit request.
- High-pressure project stress continuing after the user asks to pause.

## Relationship To Other Skills

`tes-prospect` is the read-only pressure pass. `tes-mine` is the code and domain knowledge mining pass that can capture durable context and ADRs. Tilly Engineering Discipline remains the general engineering overlay.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-13 | Promoted DUTT incubated `tes-prospect` into TES canonical adapter source. | `tmp/tes-prospect/SKILL.md`; Murillo migration approval. | high |
| 2026-05-13 | Added cognitive brake semantics and bumped contract to `tes.prospect@0.1.1`. | Murillo approval after brake proposal. | high |

## Do Not Lose

Invocation is conservative, execution is intense. The skill must stay dormant until explicitly called, then apply real project pressure instead of behaving like a passive planning assistant. The cognitive brake regulates intensity without making the skill passive.
