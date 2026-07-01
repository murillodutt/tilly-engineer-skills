# Host Command Loop

Use this reference when the canary claim depends on a real host command, not on
agent memory, copied logs, or a manually reconstructed narrative.

## Loop Contract

The smallest valid host loop is:

```text
frame command -> run or fingerprint command -> resolve transcript ->
run transcript oracle -> classify -> patch source -> replay same command
```

The command itself can be recorded as a safe label and fingerprint. Do not put
raw command text into tracked reports when it carries project-specific paths,
prompts, secrets, payloads, or private vocabulary.

## Authority

Run the host command only when the action is local, non-destructive, and already
authorized by the current task. Stop before commands that mutate remotes,
publish, tag, upload, use credentials, delete state, or expose secrets.

When execution is not authorized, use `host_canary_loop.py` without `--execute`
to record the command fingerprint and audit the latest or explicit transcript.

## Same-Command Discipline

Use the same command until one of these is true:

- the transcript proves the command reached the expected host path;
- the failure is classified and source has been patched;
- the replay produces a fresh transcript hash;
- the next blocker requires owner authority or a different command by design.

Changing the command without recording the reason is an evidence gap. Prefer
`--enforce-same-command` and require a fresh transcript hash on replay.

## Correction Loop

Patch only the source surface that owns the defect:

- TES product behavior: patch package source and source oracle.
- Local development workflow: patch the local skill, reference, template, or
  helper script.
- Target-only evidence: patch nothing; collect and classify evidence.

Do not patch installed target mirrors as the source of truth unless the task is
explicitly target-only evidence collection.

## Stop States

- `PRODUCE_AND_CONTINUE`: transcript path is derivable or the same command can
  be replayed locally without destructive or remote effects.
- `NEEDS_EVIDENCE`: command did not produce a usable fresh transcript, or the
  transcript lacks required tool-use evidence.
- `FAIL`: host command failed, timed out, or transcript JSONL is malformed.
- `BLOCKED`: the same blocker repeated three times, authority is missing, or
  host truth cannot be observed with the available local surfaces.
- `CERTIFIED`: same command replay, transcript oracle, and related TES gates all
  support the canary claim.
