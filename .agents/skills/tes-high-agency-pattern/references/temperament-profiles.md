# Temperament Profiles

Use this reference when designing or reviewing a development-layer skill. The
goal is not to make every skill verbose or high pressure. The goal is to match
the skill's operating temperament to the job it protects.

## Temperament Fields

- `mode`: sniper, miner, prospector, builder, gate, or curator.
- `question_budget`: zero, one-at-a-time, bounded, or exhaustive.
- `verbosity`: terse, compact, explanatory, or high-pressure.
- `autonomy`: answer-first, inspect-first, ask-first, write-capable, or
  read-only.
- `evidence_posture`: command/result, code-first, domain-first, oracle-first,
  or memory-first.
- `output_shape`: fact, next question, decision, patch, pass/fail, durable
  context, or curation proposal.
- `stop_condition`: the smallest observable result that proves the skill is
  done.
- `drift_lock`: what this skill must never become.

## Profiles

### Sniper

Use for diagnostics, exact checks, local fixes, pass/fail gates, or narrow
decisions.

- Ask only when the request is unsafe or genuinely ambiguous.
- Read the smallest evidence surface that can prove the answer.
- Prefer command output, file lines, or oracle status over explanation.
- Close with the result and residual blocker, if any.
- Drift lock: do not turn into brainstorming, interviewing, or broad planning.

### Miner

Use when knowledge is hidden in code, language, decisions, or contradictions.

- Inspect local evidence before asking.
- Challenge overloaded terms and glossary drift.
- Ask one question at a time when evidence cannot resolve the term.
- Write durable context only after resolution and only when the active contract
  allows it.
- Drift lock: do not write speculative context or implementation specs.

### Prospector

Use when the next risk is a weak plan, hidden dependency, or ambiguous branch.

- Stay read-only unless another explicit contract authorizes writes.
- Pressure one risk or decision at a time.
- Include a recommended answer with each question.
- Stop when the next decision is sharper.
- Drift lock: do not become passive assistance or multi-question dumping.

### Builder

Use when the skill must produce a material change.

- State assumptions and oracle before editing.
- Keep the patch surgical and request-traceable.
- Prefer existing patterns over new machinery.
- Verify with the smallest relevant check first.
- Drift lock: do not refactor neighboring code opportunistically.

### Gate

Use when the skill certifies readiness, health, parity, or release posture.

- Run the oracle before prose when possible.
- Use explicit statuses such as PASS, FAIL, BLOCKED, DEGRADED, or
  NEEDS_REVIEW.
- Do not repair unless the gate contract authorizes repair.
- Report the blocker, evidence, and next permitted action.
- Drift lock: do not claim success from narrative confidence.

### Curator

Use when the skill manages durable memory, evidence, or retained context.

- Prefer read-only recall, audit, and curation plans before writes.
- Promote only grounded reusable facts, decisions, or lessons.
- Keep source authority separate from compiled memory.
- Preserve provenance and rejection reasons.
- Drift lock: do not turn transient chat into durable truth.

## Placement Rule

Keep this pattern in local development-layer guidance until a specific
distributable skill needs a contract change. Apply it to `src/**` only through
an explicit skill update with evidence, contract history, adapter parity, and
validation.
