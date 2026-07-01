# Memory Runtime Canary

Use this recipe when a canary claim depends on runtime memory injection rather
than manual memory lookup.

## Recipe

```text
create clean target
install final bundle
initialize memory runtime
seed unique safe marker
run direct hook smoke
run host command with manual lookup forbidden
audit transcript + ledger + artifact
classify pass, false green, product gap, or evidence gap
```

## Boundaries

- The harness may seed memory before host execution.
- The agent may receive memory only through hook or runtime injection during the
  host run.
- Manual discovery by `Read`, `Grep`, `Glob`, `LS`, or shell lookup against
  memory paths is forbidden during the host agent run.
- Benign marker reuse is expected after hook injection and may appear in
  generated artifacts, edit payloads, validation commands, or retained reports.

## Runtime Signal

`runtime_signal_audit.py` certifies this recipe without one-off snippets when it
can prove:

- the transcript is parseable and fresh for the selected session;
- tool-use evidence exists;
- hook ledger rows connect the same session to host-real runtime context;
- the first mutation of the declared artifact carried
  `cortex_context_emitted=true` or an equivalent runtime context signal;
- the expected safe marker is present in the artifact;
- no forbidden memory lookup occurred.

## Decisions

- `PASS`: host-real memory injection produced the artifact signal without
  forbidden lookup.
- `false_green`: a report claims runtime memory proof without the required
  transcript, ledger, artifact, or contamination evidence.
- `product_gap`: the product/runtime failed to inject the memory context.
- `evidence_gap`: evidence exists but does not connect session, ledger, marker,
  and artifact.
