---
name: tes-map
description: Use when the user says /tes-map, /tes:gps, tes map, project GPS, mapa TES, map this project, mapear TES, mapear projeto, or asks for a visual current-position map of the project after TES setup/alignment.
---

# TES Map

`/tes-map` is the preferred shared TES trigger for the Project GPS.
`/tes:gps` is a compatible TES intent alias.

`tes-align` owns the map. `tes-map` updates the position.

Use this skill when the user wants a short, visual, actionable answer to:

- what is already implemented;
- where the project is now;
- which phase is active;
- what is next;
- what is blocked or unknown;
- which gate proves movement.

## Contract

`PROJECT-ROADMAP.md` remains the source of truth. Do not create a parallel
roadmap. The Project GPS is a managed block inside:

```text
docs/agents/PROJECT-ROADMAP.md
```

The only writable region for this skill is:

```md
## TES Map

<!-- TES-MAP:START -->
...
<!-- TES-MAP:END -->
```

If `PROJECT-ROADMAP.md` is missing, report `NEEDS_ALIGN` and tell the user to
run `/tes-align`. If `PROJECT-CONTEXT.md` is missing, report `NEEDS_CONTEXT`
and tell the user to run `/tes-init` first.

## Workflow

1. Confirm TES is installed and the target has `docs/agents/**`.
2. Run the installed helper when available:

```bash
python3 .tes/bin/tes_map.py --target . --write
```

Use this from the TES source package when testing an external target:

```bash
python3 scripts/tes_map.py --target <target> --write
```

3. Keep the human report short:
   - `You are here`
   - `Next safe move`
   - `Blocked by`
   - `Proof`
4. Certify the block when a claim needs proof:

```bash
python3 .tes/bin/tes_map_oracle.py --target .
```

Use `python3 scripts/tes_map_oracle.py --target <target>` from the TES source
package.

## Output Rules

- Do not print raw JSON to the user unless they asked for machine output.
- Do not rewrite the whole roadmap.
- Do not invent phases, blockers, gates, or completion claims.
- Do not write `.obsidian/**`.
- Treat Cortex as optional evidence only; Markdown remains authority.
- Second execution with no new evidence should be idempotent.

## Done

Close with one of these states:

- `PASS`: Project GPS updated or already current.
- `NEEDS_ALIGN`: `PROJECT-ROADMAP.md` is not ready.
- `NEEDS_CONTEXT`: project context is missing.
- `BLOCKED`: required files exist but cannot be read or updated.

The certification sentence is:

```text
Project GPS: PASS, with explicit limits.
```
