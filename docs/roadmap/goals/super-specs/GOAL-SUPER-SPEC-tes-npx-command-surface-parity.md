---
tds_id: roadmap.goal_super_spec_tes_npx_command_surface_parity
tds_class: roadmap
status: proposed
consumer: maintainers, installer authors, NPX/BunX authors, oracle authors, release reviewers, and execution agents
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# GOAL Super SPEC: TES NPX Command Surface Parity

Status: proposed execution contract derived from ADR 0004 (active). This is a
follow-up execution line of capsule-first isolation. It builds directly on the
`uninstall`/`attach`/`detach` subcommands and the attach-health contract already
delivered in the engine by the capsule install+uninstall (`0.3.160`),
attach/detach+attach-health (`0.3.161`), and runtime-surface (`0.3.162`) lines.

Capability: close the gap where ADR 0004 reversibility lives in the Python
engine (`scripts/tes_install.py`) but is unreachable from the public NPX/BunX
entrypoint (`bin/tes.js`), which only routes `add`/`install`. An adopter who
installs with `npx` today cannot uninstall, attach, detach, or run a health
report without dropping to raw Python. This line makes the npx surface honor the
full ADR 0004 installer model. It does not decide the default materialization
set — that is owned by the sibling functional-default line; this line surfaces
whatever default that line sets.

## Canonical Artifact

Canonical Super SPEC:
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-npx-command-surface-parity.md`

Primary decision source:
`docs/adr/0004-tes-capsule-isolation-and-reversible-installation.md`
(section `### Installer model`, the five-command table: `install`, `attach`,
`detach`, `uninstall`, `doctor`).

Related implementation surfaces:

- `bin/tes.js` (`parse`, command guard, passthrough, dispatch, render helpers)
- `scripts/tes_install.py` (`install`, `uninstall`, `attach`, `detach`
  subparsers; a `doctor` command does not yet exist)
- `scripts/tes_bundle.py` (`uninstall_capsule`, `detach_surface`)
- `scripts/attach_health_oracle.py` (per-surface health verdict)
- `scripts/capsule_residue_oracle.py` (post-uninstall residue proof)
- `scripts/tes_npx_oracle.py` (npx/bunx contract and self-test)
- `scripts/install_smoke.py` (round-trip probes)

## Mantra Gate Snapshot

| Field | Record |
|-------|--------|
| `VERIFY` | The current state was inspected before writing. Engine subparsers `install`/`postinstall`/`hook`/`status`/`uninstall`/`attach`/`detach` exist (`tes_install.py:2333-2396`) and dispatch (`tes_install.py:2407-2422`). `bin/tes.js` rejects any command other than `add`/`install` (`bin/tes.js:262-263`), exposes `--attach` only as an install-time flag (`bin/tes.js:10,82-85`), and forces `--attach mcp --attach hooks` when none is passed (`bin/tes.js:714-715`). No `doctor` command exists in the engine or the bin. The default-materialization defect is owned by the sibling functional-default line; this line owns only the command-surface gap. |
| `SCOPE` | Add this Super SPEC and correlated indexes now (planning-only, version-neutral). The runtime slices it specifies change delivered npx behavior and carry a patch bump per ADR 0004 Release Identity. |
| `BEST_PATH` | The engine already owns the reversible machine. This line is a thin, faithful surfacing of existing subcommands through `bin/tes.js` plus one new `doctor` aggregator. Do not duplicate removal, attach, or health logic in JavaScript; the bin parses, validates, delegates to the engine, and renders. Reuse `runPythonInstaller` and the existing summary/failure renderers. |
| `DOCUMENT` | This Super SPEC plus `docs/roadmap/README.md`, `docs/INDEX.md`, `docs/tds/DOCS-INDEX.yml`, and `docs/install/AGENT-ORACLE-INVENTORY.md` if oracle coverage changes. |
| `ORACLE` | `python3 scripts/validate_tds.py`, `python3 scripts/validate_doc_size.py`, `python3 scripts/private_vocabulary_oracle.py`, `git diff --check` for this planning artifact; the per-unit focused oracles below for each runtime slice. |
| `RESOLVE` | No private target identifiers enter TES. This line only exposes the engine's reversible commands; it sets no default and overrides no materialization decision. |
| `STATUS` | `PROCEED` |

## Governing Matrix

| Layer | Meaning |
|-------|---------|
| ADR 0004 | The installer model is a five-command surface: `install`, `attach <surface>`, `detach <surface>`, `uninstall`, `doctor` (report capsule and attachment health separately). All five are decided behavior. What `install` materializes by default is set by the sibling functional-default line. |
| Engine (delivered) | `uninstall`/`attach`/`detach` already exist and pass their oracles in `tes_install.py`/`tes_bundle.py`. `doctor` is decided but not implemented anywhere. |
| NPX surface (gap) | `bin/tes.js` exposes only `add`/`install`. The reversible engine surface is unreachable from the public entrypoint adopters use. |
| Default ownership | The functional-default decision (a full TES whose every write is capsule-reversible) is owned by the sibling line `GOAL-SUPER-SPEC-tes-skills-surface-and-functional-default.md`, grounded in ADR 0004's capability-preservation invariant (`:205-206`, `:277`). This npx line consumes that default and surfaces it; it does not re-decide the materialization set. |
| Non-Change | Does not add new surfaces, change the attach-health evidence model, alter MCP/hook writers, add GPS/Goal Maestro/Mantra changes, decide the default materialization set, or take any remote/publish action. It is a surfacing + one aggregator line. |

## Current Meaning

Today the reversibility ADR 0004 promises — "install and uninstall cleanly
without sanitizing leftover TES residue by hand" — is only honored for an
operator who runs `python3 scripts/tes_install.py uninstall`. The public
`npx ... tilly-engineer-skills add` / `install` path cannot uninstall, attach a
single surface after install, detach one, or report health. The `parse()` guard
in `bin/tes.js` returns an `unknown command` error for anything but `add`/
`install`, so the engine's `uninstall`/`attach`/`detach` are dead to npx users.
`doctor` is named in the ADR installer table but implemented nowhere.

The npx public default materialization (today `mcp`+`hooks` only, which yields a
non-functional TES) is a separate defect owned by the sibling functional-default
line. This line does not re-decide it; it surfaces whatever default that line
sets, faithfully.

This line surfaces the existing engine commands through the npx entrypoint and
implements `doctor` as a read-only aggregator over the existing health oracles,
so the reversibility ADR 0004 promises is reachable from the entrypoint adopters
actually use.

## Invariants (must hold after every unit)

- No logic duplication: `bin/tes.js` parses, validates, delegates to the Python
  engine, and renders. Removal, attach, and health logic stay in the engine.
- Reversibility reachable: an adopter who installed via npx can uninstall via
  npx and return the project to its pre-TES state with zero active residue.
- No false green carried forward: npx render of `attach`/`uninstall`/`doctor`
  must surface the engine's ADR 0003.1 / attach-health verdict faithfully
  (`PASS`/`PARTIAL`/`NEEDS_REVIEW`/`BLOCKED`/`PENDING_*`/`HOST_UNOBSERVABLE`),
  never flatten a pending or unobservable state into a clean success line.
- Non-interactive safety preserved: destructive npx commands (`uninstall`,
  `detach`) require `--yes` and support `--dry-run`, matching the engine.
- Default honesty: the npx `--help` describes whatever default the sibling
  functional-default line sets, with no divergence between code, help, and the
  decision record. This line does not set or override that default.
- Inbound isolation preserved: surfacing commands adds no new write path; the
  MCP server still refuses a runtime `target` argument.

## Required Fix Matrix

| Fix | Owned Surface | Gap Today | Required Correction | Focused Oracle |
|-----|---------------|-----------|---------------------|----------------|
| Command parser | `bin/tes.js` | `parse()` rejects all but `add`/`install` (`:262-263`). | Accept `uninstall`, `attach`, `detach`, `doctor`; per-command option/argument validation; keep `add`/`install` unchanged. | `python3 scripts/tes_npx_oracle.py --self-test`. |
| Uninstall route | `bin/tes.js` | No npx uninstall; reversibility unreachable. | Delegate to engine `uninstall`; require `--yes`, support `--dry-run`; render the residue verdict. | `python3 scripts/tes_npx_oracle.py --self-test` uninstall fixture. |
| Attach/detach route | `bin/tes.js` | `--attach` is install-only; no post-install single-surface add/remove. | Delegate `attach <surface>` / `detach <surface>` to the engine; validate the surface name; render the attach-health verdict for that surface. | `python3 scripts/tes_npx_oracle.py --self-test` attach/detach fixtures. |
| Doctor command | `scripts/tes_install.py`, `bin/tes.js` | `doctor` is in the ADR table but implemented nowhere. | Add an engine `doctor` subcommand that aggregates capsule health plus per-surface attach-health read-only (no writes), and surface it through npx. | `python3 scripts/tes_install.py doctor --dry-run`; `tes_npx_oracle --self-test` doctor fixture. |
| NPX round-trip coverage | `scripts/tes_npx_oracle.py`, `scripts/install_smoke.py` | Oracles cover default capsule install only; no npx-level uninstall/attach/detach/doctor path. | Add npx-level fixtures: install then uninstall via the bin; attach then detach via the bin; doctor read-only verdict; assert no project residue. | `python3 scripts/tes_npx_oracle.py --self-test`; `python3 scripts/install_smoke.py --self-test`. |

## Execution Discipline

Run units sequentially. Do not implement a later unit before the current unit
has its focused oracle green, a release identity classification, and a closure
note. Before each unit state owned files, no-touch files, release identity
impact, focused oracle, and stop condition.

## SPEC-000: Reentry And Boundary

Owned files: this Super SPEC; no runtime files.

Tasks:

1. `git status --short --branch --untracked-files=all` and `git log -8 --oneline`.
2. Classify dirty changes as inherited, current-task delta, or unrelated.
3. Confirm the engine `uninstall`/`attach`/`detach` subcommands are present and
   green as the baseline to surface (do not reimplement them).
4. Confirm no private target evidence enters TES and this planning artifact is
   doc-only and version-neutral.

Focused oracle:

```bash
python3 scripts/validate_tds.py
python3 scripts/private_vocabulary_oracle.py
git diff --check
```

Closure note: SPEC-000 PASS means a clean boundary and a confirmed engine
command surface to expose without duplication.

## SPEC-001: NPX Command Parser

Owned files: `bin/tes.js`.

Implementation:

1. Extend `parse()` so the command guard accepts `add`, `install`, `uninstall`,
   `attach`, `detach`, and `doctor`. Keep `add`/`install` behavior byte-for-byte.
2. Add per-command option and positional validation: `attach`/`detach` take a
   single surface argument validated against the known surface set; `uninstall`
   and `detach` honor `--yes` and `--dry-run`; `doctor` is read-only.
3. Update `printHelp()` to document the new commands and their options.

Release identity impact: delivered npx behavior; patch bump decided at SPEC-005.

Focused oracle:

```bash
python3 scripts/tes_npx_oracle.py --self-test
```

Stop condition: if a new command needs an engine flag that does not exist yet,
stop with `NEEDS_REVIEW` and define the engine contract before wiring the bin.

## SPEC-002: Uninstall Route

Owned files: `bin/tes.js`.

Implementation:

1. Build the engine argv for `uninstall` (`--target`, `--yes`/`--dry-run`) and
   delegate via `runPythonInstaller`.
2. Render the result: surface the residue verdict and any `needs-review`
   preserved files; never flatten a `NEEDS_REVIEW` into a success line.
3. Require `--yes` for a real uninstall; `--dry-run` shows planned removals only.

Release identity impact: delivered npx behavior; patch bump decided at SPEC-005.

Focused oracle:

```bash
python3 scripts/tes_npx_oracle.py --self-test
```

Stop condition: if the engine reports a preserved user-modified file, render it
explicitly as retained, never as a clean removal.

## SPEC-003: Attach And Detach Routes

Owned files: `bin/tes.js`.

Implementation:

1. Delegate `attach <surface>` and `detach <surface>` to the engine subcommands.
2. Validate the surface against the known set before delegating; reject
   `capsule` for detach (route the user to `uninstall`).
3. Render the per-surface attach-health verdict for `attach`, and the detach
   actions plus residue verdict for `detach`, faithfully including
   `PENDING_*` / `HOST_UNOBSERVABLE`.

Release identity impact: delivered npx behavior; patch bump decided at SPEC-005.

Focused oracle:

```bash
python3 scripts/tes_npx_oracle.py --self-test
```

Stop condition: if a surface has no engine remover yet (the still-conceptual
field-reports/gps/goals/mantra), surface the engine `NEEDS_REVIEW` instead of
implying success.

## SPEC-004: Doctor Command

Owned files: `scripts/tes_install.py`, `bin/tes.js`.

Implementation:

1. Add an engine `doctor` subparser and a read-only `doctor(args)` that reports
   capsule health and per-surface attach-health separately, reusing
   `attach_health_oracle` and `capsule_residue_oracle`. No writes.
2. Surface `doctor` through the npx parser and render its two-part report.
3. Keep `doctor` distinct from repair: it reports; it does not mutate. Existing
   `/tes-doctor` skill repair routes remain a separate concern.

Release identity impact: delivered engine + npx behavior; patch bump decided at
SPEC-005.

Focused oracle:

```bash
python3 scripts/tes_install.py doctor --dry-run --target <fixture>
python3 scripts/tes_npx_oracle.py --self-test
```

Stop condition: if a health signal would require a write to compute, stop and
keep `doctor` read-only; do not let a report mutate the target.

## SPEC-005: Round-Trip Coverage, Release Identity, Closure

Owned files: `scripts/tes_npx_oracle.py`, `scripts/install_smoke.py`,
`package.json`, `bin/tes.js` `TES_VERSION`, script `VERSION` constants,
correlated bundle/public surfaces; docs/evidence only if retained.

Tasks:

1. Add npx-level round-trip fixtures: install then uninstall via the bin; attach
   then detach via the bin; a doctor read-only verdict. Assert no active project
   residue after uninstall.
2. Classify release identity: SPEC-001..004 change delivered npx and engine
   behavior — a patch bump is required unless the owner explicitly defers, per
   ADR 0004 Release Identity. Check `package.json`, `bin/` `TES_VERSION`, script
   `VERSION` constants, plugin manifests, `docs/dist/<version>/**`, `.sha256`
   sidecars, `index.json`, public docs, and the maintainer correlation rule.
3. Run every implemented unit's focused oracle and `npm run commit:check`.
4. If a bump is performed, run the bundle/governance checks via the source
   release flow (do not partial-bump the source package).

Focused oracle:

```bash
python3 scripts/tes_npx_oracle.py --self-test
python3 scripts/install_smoke.py --self-test
npm run commit:check
```

Stop condition: if release identity requires a bump and owner authorization for
remote actions is unclear, stop with `NEEDS_REVIEW` and keep the work local.

## Private Vocabulary Guard

No private project names, repository paths, remotes, commit narratives, target
product vocabulary, domain decisions, or canary identifiers may enter TES. Use
generic forms only: `target project`, `private target canary`, `<absolute-path>`,
`<redacted-token>`.

## Evidence Plan

| Evidence | Location | Requirement |
|----------|----------|-------------|
| Unit self-test output | closeout summary or retained report | Commands and PASS/FAIL only. |
| NPX round-trip proof | retained report | Generic; assert install->uninstall and attach->detach via the bin return the target to a clean state without target identifiers. |

## Final Closure Report Requirements

The executor must report: implemented SPEC units; files changed; the npx-to-engine
delegation map (which command routes to which engine subcommand); release
identity decision; focused oracle results; baseline gate results; whether
`npm run commit:check` passed; residual risks; deferred work; and confirmation
that no logic was duplicated into `bin/tes.js`, that this line set no default
materialization, and no private target identifiers were added.
