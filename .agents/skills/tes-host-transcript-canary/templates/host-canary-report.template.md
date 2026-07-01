# Host Canary Report

## Scope

- Target: `<target-label>`
- Host: `<host-label>`
- Loop count: `<count>`
- Decision: `<PASS|NEEDS_EVIDENCE|FAIL|BLOCKED|CERTIFIED>`

## Command

- Safe label: `<safe-command-label-or-none>`
- Command fingerprint: `<sha256-or-none>`
- Executed: `<yes|no>`
- Replay status: `<not-run|fresh|stale|blocked>`

## Transcript Evidence

- Oracle status: `<PASS|NEEDS_EVIDENCE|FAIL>`
- Transcript hash: `<sha256-or-none>`
- Parsed events: `<count-or-none>`
- Tool uses: `<count-or-none>`
- Tool results: `<count-or-none>`
- Subagents checked: `<yes|no>`

## Correction

- Failure class: `<class-or-none>`
- Source surface: `<package-source|local-skill|target-evidence|none>`
- Fix commit: `<hash-or-none>`

## Gates

- Transcript oracle: `<status>`
- Canary admission: `<status-or-not-run>`
- Installed certification: `<status-or-not-run>`
- Git gate: `<status-or-not-run>`
- Package/source gate: `<status-or-not-run>`

## Blockers

`<none-or-sanitized-blockers>`

## Next Action

`<rerun_host_command|classify_and_patch|run_related_gates|certified|blocked>`
