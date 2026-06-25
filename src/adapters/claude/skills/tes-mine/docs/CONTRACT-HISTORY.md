# TES Mine Contract History

## Purpose

`tes-mine` is an explicit-invocation code and domain knowledge mining skill. After invocation, it digs through plans, code, language, decisions, and context documents to surface durable project knowledge.

## Why This Skill Exists

DUTT use showed that valuable project knowledge is often present but buried: terms are overloaded, domain concepts drift from code, and decisions remain implicit. `tes-mine` exists to mine those hidden assets and turn resolved language or decisions into durable context.

## Origin Signals

| Source | Signal | Confidence |
|--------|--------|------------|
| `tmp/tes-mine/SKILL.md` | DUTT mining skill source with glossary, code cross-reference, CONTEXT.md, and ADR behavior. | high |
| `tmp/tes-mine/CONTEXT-FORMAT.md` | Captures context glossary and relationship format. | high |
| `tmp/tes-mine/ADR-FORMAT.md` | Captures minimal ADR format and creation threshold. | high |
| Murillo directive, 2026-05-13 | DUTT has used both skills for more than two months with extraordinary results. | high |
| Murillo directive, 2026-05-13 | Skill enters radar only when explicitly invoked. | high |
| Murillo directive, 2026-05-13 | Approved a cognitive brake so the user can pause intensity without weakening the skill. | high |

## Source Search Ledger

| Window | Query | Occurrences | Meaning |
|--------|-------|-------------|---------|
| 2026-05-13 | `tes-mine` | `tmp/tes-mine/SKILL.md` only before migration | Incubated source promoted to canonical adapter source. |
| 2026-05-13 | `CONTEXT-FORMAT.md` | `tmp/tes-mine/CONTEXT-FORMAT.md` only before migration | Supporting format moved with the skill. |
| 2026-05-13 | `ADR-FORMAT.md` | `tmp/tes-mine/ADR-FORMAT.md` only before migration | Supporting format moved with the skill. |

## Contracts Preserved

- Activate only when explicitly invoked.
- After invocation, act proactively and predictively.
- Interview relentlessly until shared understanding exists.
- Ask one question at a time and wait for feedback before continuing.
- Explore the codebase instead of asking when local evidence can answer.
- Challenge glossary conflicts immediately.
- Sharpen fuzzy or overloaded language into canonical terms.
- Cross-reference user claims with code.
- Update `CONTEXT.md` inline when a term is resolved.
- Offer ADRs only when the decision is hard to reverse, surprising without context, and the result of a real trade-off.
- Stop immediately on a cognitive brake, summarize state, avoid new context or ADR writes while braked, and wait for explicit resume.

## Known Failure Modes Prevented

- Domain language drifting away from implemented behavior.
- Project-specific terminology remaining implicit.
- ADRs being created for reversible or obvious choices.
- Implementation details polluting `CONTEXT.md`.
- Asking the user questions the repository can answer.
- Skill discovery activating during ordinary planning without explicit request.
- Mining pressure or context writes continuing after the user asks to pause.

## Relationship To Other Skills

`tes-mine` is the mining pass for durable project knowledge. `tes-prospect` is the read-only project-stress pressure pass. Tilly Engineering Discipline remains the general engineering overlay.

## Changelog

| Date | Change | Evidence | Confidence |
|------|--------|----------|------------|
| 2026-05-13 | Promoted DUTT incubated `tes-mine` into TES canonical adapter source. | `tmp/tes-mine/**`; Murillo migration approval. | high |
| 2026-05-13 | Added cognitive brake semantics and bumped contract to `tes.mine@0.1.1`. | Murillo approval after brake proposal. | high |

## Do Not Lose

The skill is both the mine and the miner: it must keep digging until hidden technical value becomes shared project language, resolved context, or a sparse ADR candidate. The cognitive brake regulates intensity and write timing without weakening the mining behavior.
