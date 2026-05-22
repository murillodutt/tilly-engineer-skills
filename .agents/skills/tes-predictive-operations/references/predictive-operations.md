# Predictive Operations

## Modes

Use `tes-prospect` when the next risk is in the plan:

- hidden dependency;
- weak phase boundary;
- vague next decision;
- failure path before implementation;
- need for one project-stress question with a recommended answer.

Use `tes-mine` when the next risk is in language or evidence:

- overloaded term;
- contradiction between code and claim;
- unresolved domain relationship;
- implicit decision worth preserving;
- possible `CONTEXT.md` or ADR update after resolution.

Use `alternate` when the work needs both:

1. `tes-prospect` exposes the next failure risk.
2. `tes-mine` checks code, language, and durable context.
3. `tes-prospect` returns with a sharper next decision.
4. Durable context is written only after a term, relationship, contradiction,
   or decision resolves.

Use `package` only when the behavior is clear and the local skill surface needs
tightening.

## Brake Snapshot

When braked, report:

1. current position;
2. current hypothesis;
3. open risk or unresolved term;
4. next proposed question or repository check;
5. what remains unwritten.

Then wait for explicit resume.

## Write Policy

`tes-prospect` is read-only. `tes-mine` may write durable knowledge only after
resolution and only within its active contract. Packaging work changes local
skill files only when explicitly requested by the maintainer.
