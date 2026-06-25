# Failure Patterns

Load this reference when a task shows ambiguity, overengineering, broad diffs, or weak closure.

## Silent Wrong Interpretation

Signal:

- The request has multiple meanings.
- The agent chooses one without saying why.
- The implementation implies product, security, or data assumptions.

Repair:

- Name interpretations.
- Pick only when local evidence makes one clearly safer.
- Ask when the answer changes scope, authorization, or irreversible behavior.

## Overbuilt Solution

Signal:

- New abstractions have one consumer.
- Configuration appears before a real variant exists.
- Error handling covers impossible states.
- The implementation is much larger than the requested behavior.

Repair:

- Delete speculative features.
- Implement the direct path.
- Add abstraction only after a second real consumer appears.

## Drive-By Refactor

Signal:

- Unrelated files change.
- Comments or formatting change without need.
- Existing style is replaced with the agent's preferred style.

Repair:

- Restore unrelated churn.
- Keep only request-traceable lines.
- Mention unrelated cleanup separately.

## False Completion

Signal:

- The answer says "done" without a test, lint, typecheck, build, or domain oracle.
- The agent relies on prose confidence.
- A benchmark or fixture exists but was not run.

Repair:

- Define the smallest relevant oracle.
- Run it.
- If it fails, fix the cause and rerun the failing check first.

## Context Bloat

Signal:

- Root instruction files become inventories.
- The agent reads many documents before selecting the relevant source.
- Tool-specific packaging is copied into another runtime.

Repair:

- Keep bootloaders small.
- Move detail into skills, references, or project docs.
- Route to the smallest correct source set.
