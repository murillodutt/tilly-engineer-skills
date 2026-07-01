# Transcript Contamination

Use this reference when a runtime memory canary must distinguish forbidden
manual lookup from benign use of a marker already injected by the hook.

## Forbidden Manual Lookup

Classify the transcript as contaminated when a main or subagent tool-use:

- uses `Read`, `Grep`, `Glob`, or `LS` against `docs/agents/cortex`,
  `.tes/cortex`, or another configured memory path;
- uses `Bash` with `cat`, `rg`, `grep`, `find`, `ls`, `sed`, `awk`, `python`, or
  `sqlite` against a memory path;
- uses `Bash` to invoke `cortex.py recall`, `cortex.py read-cell`, or an
  equivalent recall command during the host agent run;
- delegates to a subagent that performs the same forbidden pattern.

Forbidden lookup is a failure even when the final artifact contains the expected
marker.

## Benign Signal Use

Do not classify these as contamination:

- `Write`, `Edit`, `MultiEdit`, or `Agent` payloads containing an expected
  marker already injected by the hook;
- validation commands that inspect the generated artifact for the expected
  marker;
- retained report text that references the marker without accessing memory
  storage.

## Classifier Fixtures

- Benign marker reuse in an edit payload passes.
- Direct memory file reads fail.
- Shell lookups fail even when the final artifact is correct.
