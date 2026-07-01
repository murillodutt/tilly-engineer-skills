---
tds_id: evals.canary_prompt.flappy_bird
tds_class: eval
status: active
consumer: maintainers, canary operators, and Goal Maestro operators
source_of_truth: true
evidence_level: L2
tver: 0.1.0
---

# SUPER-SPEC: Single-File Canvas Bird Game Canary

## Purpose

Build a complete, playable 2D side-scroller inspired by Flappy Bird as a real product slice for a browser target. This artifact is intentionally a product Super SPEC, not an optimized execution prompt. The harness must derive the execution tree, active SPEC queue, structural method, oracles, evidence, report sidecars, and optional audit heartbeat behavior from this artifact plus explicit runtime options.

## Canonical Output

- Deliver exactly one runtime file: `index.html`.
- Use only semantic HTML, internal CSS, and internal JavaScript.
- Use HTML5 Canvas for all gameplay rendering.
- Do not use external libraries, frameworks, images, fonts, CDNs, build tools, package managers, or network calls.
- The file must open directly in a modern browser from the filesystem.

## Product Goal

Create a polished, smooth, and fully playable bird-and-pipes arcade game with:

- responsive layout for desktop and mobile;
- base game coordinate system of `400 x 600`;
- Retina/HiDPI support using `devicePixelRatio` while preserving visual canvas size;
- stable `requestAnimationFrame` game loop;
- low allocation pressure during the animation loop;
- clear game states: `start`, `playing`, and `gameOver`;
- keyboard, pointer, and touch controls;
- score and high-score persistence with safe `localStorage` handling;
- fair collisions and immediate restart after game over;
- attractive visual presentation using Canvas shapes, colors, gradients, and no external assets.

## Non-Objectives

- Do not clone copyrighted assets, images, sounds, logos, names, or exact visual identity.
- Do not add multiplayer, backend, analytics, telemetry, service workers, PWA install flows, ads, accounts, or remote storage.
- Do not split the product into multiple runtime files.
- Do not introduce dependencies just to simplify drawing, physics, tests, or input handling.
- Do not treat a static code listing as sufficient evidence; the game must be locally runnable and visually inspected.

## Structural Method

Use a source-mandated single-file topology exception:

- Keep `index.html` as the only runtime deliverable.
- Organize internal code into named sections:
  - configuration;
  - runtime state;
  - canvas setup and resize;
  - input;
  - physics;
  - obstacle management;
  - scoring and storage;
  - collision detection;
  - update;
  - rendering;
  - main loop.
- Avoid duplicated logic and unrelated layer mixing.
- Keep per-frame work predictable: no DOM reads/writes inside the game loop, no avoidable object creation per frame, no repeated event listener creation, and no layout-triggering operations during gameplay.

## Execution Units

### SPEC-001 Runtime Shell And State Machine

Objective:
Create the single-file browser shell, Canvas initialization, responsive HiDPI scaling, game constants, runtime state, and state-machine transitions.

Required behavior:

- `index.html` exists and opens directly in a browser.
- Canvas is centered and responsive.
- Visual coordinate system is based on `400 x 600`.
- HiDPI rendering uses `devicePixelRatio` correctly.
- States include `start`, `playing`, and `gameOver`.
- Start screen shows title, instruction text, and saved high score when available.
- Game over screen shows final score, best score, and restart instruction.
- Space key must not scroll the page.

Focused oracles:

- Static source inspection proves one runtime file and no external dependencies.
- Browser open smoke proves the Canvas renders nonblank.
- Screenshot evidence proves start screen layout is legible at desktop size.

### SPEC-002 Gameplay Physics, Obstacles, Scoring, And Storage

Objective:
Implement the complete playable loop: bird physics, jump controls, obstacle spawning/movement, scoring, high-score persistence, and game restart.

Required behavior:

- Controls work through Space, ArrowUp, pointer click, and touch.
- Jump applies negative vertical velocity.
- Gravity and max fall speed are configurable.
- Bird rotation reacts to vertical velocity and is clamped.
- Pipes spawn from the right, move left, have fixed gaps, safe vertical margins, and are removed after leaving the screen.
- Score increments once when the bird fully passes each pipe pair.
- High score persists with safe `localStorage` reads/writes and does not crash if storage is unavailable.
- Restart after `gameOver` is immediate through the same jump command.

Focused oracles:

- Static source inspection proves `requestAnimationFrame`, `deltaTime`, max delta clamp, controls, scoring, and guarded storage.
- Runtime interaction smoke proves start, jump, scoring path viability, game over, and restart.

### SPEC-003 Collision, Visual Polish, Performance, And Certification

Objective:
Complete fair collision detection, polished Canvas rendering, performance hygiene, and final browser certification.

Required behavior:

- Detect collision with ground, top boundary, upper pipes, and lower pipes.
- Use a fair bird hitbox.
- Draw sky, ground, pipes, bird body, wing, eye, beak, score, start screen, and game-over screen using Canvas only.
- Use dedicated render functions such as `drawBackground`, `drawGround`, `drawBird`, `drawPipes`, `drawScore`, `drawStartScreen`, and `drawGameOverScreen`.
- Keep rendering crisp on Retina/HiDPI screens.
- Maintain smooth gameplay on 60 Hz and 120 Hz displays.
- No external assets or network behavior appear in HTML, CSS, or JS.

Focused oracles:

- Browser screenshot at desktop viewport.
- Browser screenshot at mobile viewport.
- Canvas nonblank/pixel evidence.
- Static negative grep for external URLs, `<script src=`, `<link href=`, imports, frameworks, fetch/XHR, analytics, and telemetry terms.
- Manual gameplay smoke records that start, jump, pipe movement, collision, game over, restart, and high score work.

## Acceptance Criteria

- The game starts from the initial screen.
- The bird jumps and falls smoothly.
- Pipes spawn continuously and remain playable.
- The score increases after passing pipes.
- High score is saved when storage is available.
- Collisions with ground, top, and pipes end the round.
- The game restarts after `gameOver` without reloading the page.
- Canvas looks crisp on HiDPI displays.
- The implementation uses no external dependencies or remote resources.
- Runtime loop uses `requestAnimationFrame` with `deltaTime` and a maximum delta clamp.
- The final closeout includes changed files, local commit evidence per material SPEC or accepted no-commit rationale, focused oracles, visual evidence, static negative checks, and current sync status.

## Canary Evaluation Contract

This artifact must be identical across Codex, Claude Code, and Cursor target projects. Host-specific behavior belongs to the installed harness, not to this product artifact.

The expected harness behavior is:

- `/tes-goal-maestro` enriches this Super SPEC into an execution-grade goal prompt.
- `--execute-loop` executes the derived active-SPEC queue sequentially.
- `--audit-heartbeat-prompt` emits the read-only heartbeat prompt as standalone output or as a same-response sidecar when combined with `--execute-loop`.
- The Execution Thermometer is generated after loop close or honest stop from the persistent ledger.
- A single execution containing `SPEC-001`, `SPEC-002`, and `SPEC-003` may produce one Thermometer loop (`L1`) with three `spec_results`; `L2` and `L3` require separate accumulated executions, not individual SPEC rows.

## Suggested Invocation

```text
/tes-goal-maestro --execute-loop --audit-heartbeat-prompt docs/project/super-spec.md
```
