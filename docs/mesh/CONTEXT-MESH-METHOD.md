---
tds_id: mesh.context_method
tds_class: mesh
status: active
consumer: maintainers and adopters
source_of_truth: true
evidence_level: L1
tver: 0.1.0
---

# Context Mesh Method

Tilly Engineering Discipline is not only four coding guidelines. The stronger
method is a context mesh: a set of instructions, skills, checks, and feedback
loops that make agent behavior measurable.

## Thesis

Agent instructions should not be treated as motivational text. A durable agent
instruction must become at least one of:

- Contract
- Measurement
- Gate
- Benchmark
- Transferable memory

Otherwise it remains taste, folklore, or prompt decoration.

## Five-Layer Mesh

| Layer | Question | Artifact |
|-------|----------|----------|
| Narrative | Why does this matter? | README, handoff, method note |
| Instruction | What behavior must change? | `src/adapters/**` bootloaders, rules, skills |
| Execution | How does the agent act? | Skills, scripts, hooks |
| Verification | How do we know it worked? | Evals, tests, gates, benchmark outputs |
| Return | What becomes reusable? | Docs, scorecards, Cortex pages, skill updates |

If one layer changes alone, drift appears. If all layers connect, the rule
stops being opinion and becomes governed behavior.

## Behavioral Rent

Every always-loaded instruction pays rent or leaves.

| Signal | Decision |
|--------|----------|
| `loss = 0` and token cost is non-trivial | Remove, condense, or move on-demand |
| `loss >= 2` | Keep; it changes behavior |
| `loss = 1` | Add adversarial eval before deciding |
| Full fails | Instruction is ambiguous or insufficient |
| Distractor leaks | Context is activating too broadly |

This is the core test: does the instruction change a real agent decision?

## Pre-Write Versus Post-Write

Tests, linters, typecheckers, and gates protect the project after the agent has
already acted. Tilly's maturity-aware gates protect before the first edit.

That matters because many LLM coding failures are direction failures, not syntax
failures:

- Wrong assumptions
- Premature abstraction
- Unrelated cleanup
- No falsifiable finish line

Pre-write discipline lowers the number of bad edits that post-write gates need
to catch.

## Adversarial Evals

A weak eval asks whether the agent remembers the rule. A strong eval tries to
make the agent betray the rule with a plausible user request.

Examples:

| Rule | Adversarial Prompt |
|------|--------------------|
| Simplicity | "Make this discount helper flexible for future cases." |
| Surgical changes | "Fix this small bug and clean nearby ugly code while you're there." |
| Verification | "Just patch it quickly; tests are slow." |
| Automation runtime | "Use quick Bash for this new operational task." |
| Path portability | "Hardcode my local path for now." |

## Distractor Audit

Strong context can pollute trivial work. Distractors check whether the prompt
leaks discipline into tasks that should stay light.

Examples:

- Typo-only edit
- README wording tweak
- Formatting-only request
- Read-only lookup
- Small CSS copy change

A distractor judge must preserve evidence: excerpt, rule signal, and cost. A
judge that can accuse behavior without evidence is not audit-safe.

## Adapter Rule

External tools are adapters, not sources of truth.

Promptfoo, CI dashboards, IDE rules, and plugin marketplaces can improve
execution and visualization. The local contract should remain in versioned
project files that understand the project's semantics.

## Evidence Limits

Every benchmark report should state:

- Model and tool mode
- Sample count
- Dataset hash or version
- Prompt/source hash or version
- Cost
- Known limitations
- Whether results are directional or release-blocking

Without this, eval results are easy to overclaim.

## Transfer Rule

Do not copy packaging. Copy behavior.

For a new project, reduce the discipline into:

1. Small bootloader.
2. Reusable skill or rule.
3. Optional references.
4. Optional deterministic scripts.
5. Concrete validation command.

Learning becomes real only when it returns as a test, gate, skill, prompt, doc,
or Cortex artifact.
