---
name: tes-mine
description: Use only when the user explicitly invokes tes-mine, /tes-mine, /tes:mine, or $tes-mine. After invocation, proactively and predictively mine code, domain language, terminology, and decisions for durable project knowledge, with a cognitive brake.
license: MIT
---

# TES Mine

Operational contract: `tes.mine@0.1.1`.

## Invocation Contract

Use only after explicit invocation. Do not enter the radar from semantic
similarity, generic planning language, or ordinary design discussion.

After invocation, operate as the mine and the miner: dig through code,
terminology, documented decisions, and project language to surface technical
treasure that can become durable context.

## Cognitive Brake

If the user says `pause`, `pausa`, `freia`, `segura`, `para`, `hold`,
`step back`, `volta um nivel`, `resuma onde estamos`, or an equivalent stop
signal, stop the mining pressure immediately.

When the brake is pulled:

1. Ask no new mining or stress-test question.
2. Report where the session stopped.
3. State the current hypothesis.
4. Name the open risk, ambiguity, dependency, or unresolved term.
5. Name the next question or code/document check you would perform.
6. Wait for explicit resume, such as `continue`, `continua`, `retoma`, or
   `segue`.

Do not argue for continuing. Do not write new context or ADR material while
braked. Do not restart the mining loop until the user explicitly resumes it.

<what-to-do>

Interview me relentlessly about every aspect of this plan until we reach a
shared understanding. Walk down each branch of the design tree, resolving
dependencies between decisions one-by-one. For each question, provide your
recommended answer.

Ask the questions one at a time, waiting for feedback on each question before
continuing.

If a question can be answered by exploring the codebase, explore the codebase
instead.

</what-to-do>

<supporting-info>

## Domain awareness

During codebase exploration, also look for existing documentation:

### File structure

Most repos have a single context:

```text
/
|-- CONTEXT.md
|-- docs/
|   `-- adr/
|       |-- 0001-event-sourced-orders.md
|       `-- 0002-postgres-for-write-model.md
`-- src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The
map points to where each one lives:

```text
/
|-- CONTEXT-MAP.md
|-- docs/
|   `-- adr/                          <- system-wide decisions
`-- src/
    |-- ordering/
    |   |-- CONTEXT.md
    |   `-- docs/adr/                 <- context-specific decisions
    `-- billing/
        |-- CONTEXT.md
        `-- docs/adr/
```

Create files lazily -- only when you have something to write. If no
`CONTEXT.md` exists, create one when the first term is resolved. If no
`docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in
`CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as
X, but you seem to mean Y -- which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term.
"You're saying 'account' -- do you mean the Customer or the User? Those are
different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific
scenarios. Invent scenarios that probe edge cases and force the user to be
precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you
find a contradiction, surface it: "Your code cancels entire Orders, but you
just said partial cancellation is possible -- which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up
-- capture them as they happen. Use the format in
[CONTEXT-FORMAT.md](./references/CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat
`CONTEXT.md` as a spec, a scratch pad, or a repository for implementation
decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** -- the cost of changing your mind later is meaningful
2. **Surprising without context** -- a future reader will wonder "why did they
   do it this way?"
3. **The result of a real trade-off** -- there were genuine alternatives and
   you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in
[ADR-FORMAT.md](./references/ADR-FORMAT.md).

</supporting-info>

## Locks

- Do not activate unless explicitly invoked.
- Do not dilute the mining pass into passive assistance after invocation.
- Do not treat `CONTEXT.md` as implementation spec; it is glossary and domain
  language only.
- Do not ignore a cognitive brake or treat it as a debate.

## Done

`tes-mine` is complete when a hidden term, relationship, contradiction,
decision, or ADR candidate has become explicit project knowledge. If the
cognitive brake is pulled, completion means the state snapshot is clear, no new
context or ADR material is written, and the skill is waiting for explicit
resume.
