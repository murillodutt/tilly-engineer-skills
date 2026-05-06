---
tds_id: mesh.scorecard
tds_class: mesh
status: active
consumer: adopters and reviewers
source_of_truth: true
evidence_level: L1
tver: 0.1.0
---

# Adoption Scorecard

Use this scorecard to evaluate whether a project adopted Tilly Engineering
Discipline as a real engineering layer or only copied guidance text.

## Behavioral Score

| Factor | Question | Score |
|--------|----------|-------|
| `A` | Are assumptions, ambiguity, tradeoffs, and blockers visible before action? | 0 or 1 |
| `S` | Was speculative scope deleted before implementation? | 0 or 1 |
| `C` | Does every changed line trace to the task? | 0 or 1 |
| `V` | Did a concrete oracle pass before closure? | 0 or 1 |

```text
E = A * S * C * V
```

If any factor is zero, the work is not converged.

## Context-System Score

Use this when the target project has Codex, reusable skills, hooks, MCPs, or
other persistent agent context.

| Factor | Question | Score |
|--------|----------|-------|
| `B` | Is the bootloader short and operational instead of an inventory? | 0 or 1 |
| `R` | Does routing select the smallest correct source set? | 0 or 1 |
| `M` | Are instruction, context, user input, and validation boundaries explicit? | 0 or 1 |
| `D` | Is the four-gate discipline available before implementation? | 0 or 1 |
| `G` | Are tools, hooks, plugins, MCPs, and subagents governed before use? | 0 or 1 |
| `O` | Are checks wired into local development or CI? | 0 or 1 |
| `C` | Can a new window recover state and the next oracle? | 0 or 1 |

```text
S = B * R * M * D * G * O * C
```

If any factor is zero, the context layer is not fully converged.

## Adoption Levels

| Level | State | Minimum Evidence |
|-------|-------|------------------|
| L0 | Text copied | Root instruction contains the four gates |
| L1 | Behavior active | Agents surface assumptions and run checks on material work |
| L2 | Progressive disclosure | Detailed workflow lives in a skill or equivalent reusable module |
| L3 | Local oracle | Package or project has a deterministic validation command |
| L4 | Governance integration | The oracle is part of local CI, hooks, or closure gates |
| L5 | Reentry stable | A new context window can resume with state, source route, and next check |

The DUTT-grade target is L4 or L5. L0 and L1 are useful, but they are not the
malha that produced the strongest ambiguity reduction.

## Anti-Score

Subtract confidence when any of these appear:

- Root instruction file becomes a long inventory.
- Tool-specific packaging is copied into another runtime.
- The agent says "done" without a check.
- The diff includes unrelated cleanup.
- The workflow depends on memory instead of a versioned source.
- Cortex is treated as hidden memory instead of versioned markdown under
  `docs/agents/cortex/**`.
