---
tds_id: mesh.context_mesh_convergence
tds_class: mesh
status: active
consumer: benchmark authors, adapter authors, and certification reviewers
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# Context Mesh Convergence

Context mesh convergence is the package method for turning agent context into a contract. The rule is simple:

```text
Context becomes contract only after evidence convergence.
```

This document records the loop that emerged from retained context-mesh runs. It does not add a backend, grader, judge, or dataset surface.

## Loop

Use the loop when a rule looks plausible but has not yet proved behavioral rent:

```text
contract -> eval -> evidence -> convergence gate -> targeted repair -> repeat
```

Operational sequence:

1. Define the contract.
2. Build the eval.
3. Run evidence.
4. Fail honestly.
5. Classify failure.
6. Apply targeted repair.
7. Repeat until convergence.

## Evidence Requirements

A context rule is evidence-converged only when the retained run shows:

| Requirement | Meaning |
|-------------|---------|
| Behavioral lift | `full` outperforms `none` on the same dataset hash |
| Distractor survival | Confirmed `distractor_leak_rate` remains `0` |
| Ablation loss | Dropping the rule weakens the target behavior |
| Raw evidence | Every sample has prompt, output, hashes, grader, and excerpt |
| Targeted repair | Fixes trace to classified failures, not speculative rewrites |

## Failure Classification

Classify failures before changing source context:

| Class | Meaning | First response |
|-------|---------|----------------|
| Backend/auth | The adapter could not produce usable output | Fix execution before grading |
| Grader wording | Correct behavior failed a brittle literal | Calibrate deterministic signals |
| Dataset ambiguity | The prompt cannot isolate the target rule | Add or replace a narrow eval |
| Context leak | Heavy guidance activated on a distractor | Tighten prompt or leak rules |
| Rule insufficient | The active context did not change behavior | Amend the rule surgically |

## Governance

Convergence is not a claim about all tools or all future prompts. It is scoped to the retained dataset hash, backend, model, grader version, Git HEAD, and run id. Cross-adapter parity requires separate evidence per adapter capability.

Do not use prose quality as a substitute for convergence. A rule that reads well but has no measured lift is still a hypothesis.

## Boundaries

Do not expand the system while running a convergence loop:

- Do not add a backend just to improve a failed rule.
- Do not add an LLM judge before deterministic evidence is exhausted.
- Do not grow the dataset broadly when one adversarial eval can isolate the failure.
- Do not declare adapter parity from matching text.
- Do not call fixture evidence live-model behavior.
