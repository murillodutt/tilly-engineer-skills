# Operating Temperament

Use this reference when choosing the smallest useful reasoning mode for a
development-layer skill.

## Mode Selection

Use `sniper` when the task needs precision more than exploration:

- exact fact, command, check, patch, or PASS/FAIL result;
- low ambiguity;
- questions would slow the user down;
- smallest evidence surface is enough.

Use `prospector` when the task needs risk pressure:

- plan can fail before implementation;
- hidden dependency or phase boundary is unclear;
- one recommended question can sharpen the next decision.

Use `miner` when the task needs hidden knowledge extraction:

- language is overloaded;
- code contradicts the plan;
- a term, relationship, or decision may need durable context after resolution.

Use `builder` when the task needs a material artifact:

- patch, script, generated file, local skill update, or adapter change;
- scope and oracle can be stated before editing.

Use `gate` when the task needs certification:

- health check, parity check, release readiness, install/update validation, or
  contract audit;
- output should be status-first and evidence-backed.

Use `curator` when the task needs memory hygiene:

- recall, reflect, absorb, audit, curation plan, or retained evidence review;
- write only when grounded and authorized.

## Question Policy

- `sniper`: zero questions unless unsafe or blocking ambiguity exists.
- `prospector`: one question at a time, with a recommended answer.
- `miner`: ask after repository evidence cannot resolve the term or
  contradiction.
- `builder`: ask only when the implementation choice would be risky to infer.
- `gate`: do not ask before running the available read-only oracle.
- `curator`: ask before promotion, not before read-only recall or audit.

## Output Policy

Match output to the mode:

- `sniper`: result, evidence, blocker.
- `prospector`: risk, next question, recommended answer.
- `miner`: term or contradiction, evidence, resolution path.
- `builder`: assumptions, changed files, oracle.
- `gate`: status, evidence, next permitted action.
- `curator`: proposal, source evidence, promotion boundary.

Do not escalate to a heavier mode when a smaller one can close the task.
