---
tds_id: architecture.adr_0004_tes_capsule_isolation_and_reversible_installation
tds_class: architecture
status: proposed
consumer: maintainers, installer authors, MCP authors, hook authors, GPS/MAP authors, Goal Maestro authors, Mantra Gate authors, and release operators
source_of_truth: false
evidence_level: L2
tver: 0.1.0
---

# ADR 0004: TES Capsule Isolation And Reversible Installation

Status: proposed. This ADR is a planning decision; it changes no runtime
behavior by itself. Acceptance and the first runtime slice carry the release
identity decision recorded under Release Identity below.

## Lineage

ADR 0004 extends ADR 0003 (Cortex MCP capability) and amends ADR 0003.1
(installed certification and Field Reports intake). It does not replace them.

ADR 0003.1 already established, and ADR 0004 reuses without redefining:

- the certification vocabulary `PASS` / `PARTIAL` / `NEEDS_REVIEW` / `BLOCKED`
  (implemented in `scripts/installed_certification_oracle.py`);
- the invariant that MCP config registration is separate from host connection,
  and that `host_connected` must never be inferred from file presence
  (`installed_certification_oracle.py` carries `host_connected_not_inferred`);
- the rule that `INSTALLED` is an operation status for a completed write, not a
  certification verdict.

ADR 0004 supersedes only the prior installation *defaults* where they conflict
with capsule-first ownership, namely: project-visible writes on by default. The
status vocabulary, the non-inference rule, and the certification model from
0003.1 stay authoritative.

ADR 0004 also consumes the active planning line
`docs/roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-anti-contamination-hardening.md`.
That Super SPEC hardened TES against *inbound* private-context contamination
and language false positives. ADR 0004 extends the same anti-contamination
intent to *outbound* project contamination (TES writing into a target) and to
reversibility. The two lines must not diverge; capsule-first is the
architectural completion of anti-contamination, not a parallel effort.

## Context

Two isolation directions must hold for TES to be a clean, removable product.

Outbound (TES must not contaminate the installed project). The installer today
is install-all, not capsule-first. A default install writes four
project-visible surfaces at once, without a real opt-out:

- root bootloaders `AGENTS.md` / `CLAUDE.md` / `CURSOR.md`
  (`scripts/install_adapter.py`);
- host hooks `.claude/settings.json` / `.codex/config.toml` / `.cursor/hooks.json`
  (`scripts/tes_install.py`);
- MCP configs `.mcp.json` / `.cursor/mcp.json` / `.vscode/mcp.json`
  (`scripts/install_mcp.py`);
- docs mesh `docs/agents/PROJECT-REGISTER.md`, `docs/agents/PROJECT-CONTEXT.md`,
  `docs/agents/evidence/**` (`scripts/tes_init.py`).

There is no `uninstall`, `attach`, or `detach` command. The closest mechanism,
`cleanup_obsolete_runtime()` in `scripts/tes_bundle.py`, only removes files that
left a manifest between versions; it does not return a project to its pre-TES
state nor prove residue is gone. The user-reported defect — "install and
uninstall without later sanitizing leftover TES residue by hand" — is therefore
factually true today.

Inbound (TES must not be contaminated by other projects on the machine). This
direction is already structurally protected and must be preserved as an
invariant: Cortex stores per-target at `.tes/cortex/recall.sqlite` relative to
the resolved target (`scripts/cortex.py`), and the MCP server refuses a runtime
`target` argument — `resolve_target()` raises rather than accept it
(`scripts/cortex_mcp.py`), binding each server instance to one project. There is
no shared cross-project store. ADR 0004 names this as a protected invariant so a
later refactor cannot silently introduce a global state path.

## Decision

TES becomes capsule-first without capability loss. The capsule (`.tes/**`) is
the runtime ownership authority. Every project-visible surface — root files,
hooks, MCP configs, docs mesh, host routes — becomes an explicit, reversible
attachment, manifest-backed and detachable.

Capability is preserved, not reduced. GPS/MAP, Goal Maestro, Mantra Gate, MCP,
Cortex, and Field Reports all remain available in capsule mode. What changes is
ownership and direction: TES uses internal capsule state first, then projects
outward only through reversible attachments the user explicitly enabled.

### Installer model

| Command | Behavior |
|---------|----------|
| `install` | Capsule only. Writes `.tes/**`. No root files, no hooks, no MCP config, no `docs/agents/**`, no Field Reports hook unless an attach profile is explicitly selected. |
| `attach <surface>` | Explicit host/project attachment. Surfaces: `gps`, `goals`, `mantra`, `mcp`, `field-reports`, `docs-mesh`, `root-context`, `hooks`. Each write is manifest-recorded and health-checked. |
| `detach <surface>` | Remove an active attachment and restore project-owned files from backup; capsule state is kept. |
| `uninstall` | Restore project-owned files, remove TES-owned surfaces, remove the capsule, and prove zero active residue. |
| `doctor` | Report capsule health and attachment health separately. |

### Capsule storage layout

Default writes live only under `.tes/**`. Capsule-mode destinations:

- GPS/MAP internal projection: `.tes/gps/**` (and `.tes/context/**` for read
  state), new construction;
- Goal Maestro Super SPECs in target projects: `.tes/goals/GOAL-SUPER-SPEC-*.md`;
- Mantra Gate records: `.tes/mantra-gates/records.jsonl`, or the existing
  `.tes/field-reports/mantra-gates.jsonl` when Field Reports is attached
  (already the current default in `scripts/mantra_gate.py`).

### Manifest contract

Every write records: `owner` (`tes-owned` / `generated` / `derived` /
`project-owned`), `layer`, `attachment_surface`, `backup_policy`,
`restore_policy`, `checksum`, and `uninstall_action`. The bundle manifest in
`scripts/tes_bundle.py` already carries `owner`, `layer`, `install_policy`, and
`obsolete_policy`; ADR 0004 adds `attachment_surface`, `restore_policy`, and
`uninstall_action` as required fields so detach and uninstall are deterministic.

### Attach-health contract for MCP and hooks

This ADR cannot be accepted as complete unless MCP and hooks get a stricter
attach-health contract. Config presence is not certification.

- MCP attach `PASS` must not mean only "config file exists". It requires config
  schema validity, server self-test, protocol handshake, tool listing, and the
  mutability mode the user selected.
- Hook attach `PASS` must not mean only "hook config was written". It requires
  config written, host loaded/trusted/reloaded where observable, real event
  execution evidence, idempotency, and no duplicate stale handlers.
- When host recognition or execution cannot be proven, status must be explicit
  and never a clean `PASS`: `PENDING_HOST_RESTART`, `PENDING_TRUST`,
  `PENDING_RELOAD`, `HOST_UNOBSERVABLE`, `PARTIAL`, or `NEEDS_REVIEW`.
- `NOT_APPLIED` cannot satisfy a user-selected attachment.

Observability bound (required, host-by-host). The hosts (Claude Code, Codex,
Cursor) do not expose an external API that confirms "this hook fired" or "this
MCP server is connected". ADR 0004 therefore defines the achievable evidence per
surface, and treats `HOST_UNOBSERVABLE` as a terminal partial-success state, not
a failure:

| Surface | Achievable evidence | Terminal state when host is silent |
|---------|---------------------|-----------------------------------|
| MCP server | In-process self-test plus an out-of-process handshake against the same server entrypoint the host would spawn (initialize, capabilities, `tools/list`). | `HOST_UNOBSERVABLE` for live host connection; capsule still certifies server readiness. |
| Hook | A sentinel the hook itself writes under `.tes/**` on execution, checked for idempotency and single-handler registration. | `PENDING_TRUST` / `PENDING_RELOAD` until the sentinel appears; `HOST_UNOBSERVABLE` if the host never runs hooks observably. |

`HOST_UNOBSERVABLE` is an acceptable closure state for an attachment: it means
TES did everything it can verify and the remaining proof depends on host action
TES cannot observe. It is not a false `PASS` and not a `FAIL`.

### GPS/MAP

GPS/MAP capsule mode is an architectural inversion, not a tweak, and it replaces
behavior currently certified by an oracle. Today `scripts/tes_map.py` anchors on
`docs/agents/PROJECT-ROADMAP.md`; a missing roadmap returns `NEEDS_ALIGN`, and
`scripts/tes_map_oracle.py` explicitly asserts that behavior. ADR 0004 changes
this and must do so as a migration line, not a patch:

- default GPS runs from the internal projection under `.tes/context/**` /
  `.tes/gps/**`;
- `/tes-map` reports the current position from capsule state plus repository
  scan evidence, with no dependency on `docs/agents/**`;
- missing `docs/agents/**` is no longer `NEEDS_ALIGN` in capsule mode; it is
  required only when `docs-mesh` is attached;
- when `docs-mesh` is attached, GPS may export/update the managed `TES-MAP`
  block in `docs/agents/PROJECT-ROADMAP.md`;
- the `tes_map_oracle` baseline is renegotiated in the same slice: when both
  capsule state and `docs/agents/**` exist, capsule state is the source of
  truth and the managed block is a projection of it. Existing target projects
  with a populated `docs/agents/**` keep working through this rule, not through
  silent overwrite.

### Goal Maestro

Goal Maestro stays explicit-invocation and high-power. In target projects,
generated Super SPECs default to `.tes/goals/GOAL-SUPER-SPEC-*.md`; export to
project docs/roadmap requires explicit save/export or a `docs-mesh` attach. In
the TES source package, the existing source-governed roadmap behavior
(`docs/roadmap/goals/super-specs/**`) remains the default and is unchanged.

### Mantra Gate

Mantra Gate is always available in capsule mode and already records under
`.tes/**` standalone. Root bootloader and host-hook routing are attachments, not
the source of truth. Missing root/hook adoption is not degraded in pure capsule
mode; it is degraded only when the user explicitly attached that surface. This
formalizes "capsule mode" vs "attached mode"; the gate runtime already supports
it (`scripts/mantra_gate.py`, `scripts/mantra_gate_adoption_oracle.py` treats
absence as `NOT_APPLIED`, not degraded).

## Invariants

- Inbound isolation: per-target Cortex storage and the MCP no-`target`-runtime
  rule are protected. No global cross-project state path may be introduced.
- Outbound reversibility: every project-visible write is manifest-backed,
  detachable, and uninstallable with a recorded restore action.
- Capability preservation: capsule mode must not weaken any TES capability;
  isolation is an ownership change, not a feature reduction.
- No false green: `INSTALLED` is not certification; config presence is not host
  connection; `NOT_APPLIED` cannot satisfy a selected attachment.
- Uninstall proves zero *active* residue: project-owned files restored,
  TES-owned surfaces removed, capsule removed. Explicitly retained user-chosen
  exports are reported, not silently deleted.

## Consequences

Installer, postinstall, update, doctor, attach, detach, and uninstall must share
one manifest and one certification vocabulary. New attach-health oracles for MCP
and hooks are required, with host-specific achievable-evidence definitions. GPS
capsule mode is a migration line with its own SPEC and a renegotiated
`tes_map_oracle`. The capsule layout adds `.tes/gps/**`, `.tes/context/**`,
`.tes/goals/**`, and `.tes/mantra-gates/**` as owned destinations.

## Release Identity

This ADR is planning-only and version-neutral: writing the ADR and correlating
indexes changes no delivered behavior, so it carries no bump.

The first runtime slice that changes delivered behavior triggers the release
identity decision. ADR 0004 names the bump point and the correlated surfaces in
advance, per the maintainer release identity rule. Current version baseline:
`0.3.159`.

Bump point: the first commit that adds capsule-only `install`, any
`attach`/`detach`/`uninstall` command, the new attach-health oracles, the
manifest field extensions, or GPS capsule mode. That is delivered, adopter-
visible behavior and requires at least a patch bump.

Correlated release surfaces to check at that point: `package.json`, the `bin/`
`TES_VERSION` constant, script `VERSION` constants (`scripts/tes_namespace.py`,
`scripts/cortex.py`, and peers), plugin manifests, `docs/dist/<version>/**`,
`.sha256` sidecars, `index.json`, public docs, `docs/i18n/tes-public.structure.yml`,
the validators, and `docs/governance/MAINTAINER-CORRELATION-RULE.md`. No remote,
push, tag, publish, or marketplace action is authorized by this ADR.

## Test Plan

- Fresh target: `install` capsule only; assert no root files, no
  `docs/agents/**`, no MCP configs, no hooks, no Field Reports hook.
- GPS capsule: run map/alignment in capsule mode; assert useful output plus
  `.tes/gps/**` state with no docs export.
- GPS attached: attach `docs-mesh`, update the managed `TES-MAP` block, detach,
  then uninstall cleanly; assert the renegotiated `tes_map_oracle` passes both
  capsule-only and attached fixtures.
- Goal Maestro capsule: generate a Super SPEC into `.tes/goals/**`; export only
  after explicit save/export.
- Mantra Gate capsule: record a full gate in `.tes/mantra-gates/**`; attached
  route health required only after attach.
- MCP attach regression suite: config-present-but-host-missing, wrong tool
  mutability, runtime failure, read-only vs write activation, restart required,
  and host-unobservable states.
- Hook regression suite: config written but not fired, trust/reload pending,
  duplicate hooks, wrong order, idempotent second event, and detach/uninstall
  cleanup.
- Reversibility: install all attach profiles, then uninstall; assert the target
  is byte-identical to its pre-install state for project-owned files and that no
  active TES surface remains.
- Inbound isolation guard: assert no capsule write resolves outside the target
  and the MCP server still refuses a runtime `target` argument.
- Final gates: relevant self-tests, the new attach-health oracle, the
  install/detach/uninstall residue oracle, `python3 scripts/validate_tds.py`,
  and `npm run commit:check`.

## Rejected Alternatives

| Alternative | Rejection |
|-------------|-----------|
| Open ADR 0004 as a standalone decision that supersedes 0003.1. | The certification vocabulary and the config-vs-host invariant already exist in 0003.1. Re-deciding them duplicates governance and risks divergence. ADR 0004 extends, it does not replace. |
| Treat capsule mode as "reduced TES". | Isolation is an ownership change. Reducing capability to gain isolation would make the product weaker, not cleaner. |
| Require live host connection proof for MCP/hook `PASS`. | Hosts do not expose that proof externally. An unsatisfiable contract makes every attach permanently pending. `HOST_UNOBSERVABLE` is defined as a terminal partial-success state instead. |
| Flip GPS to capsule storage as a patch. | The current `docs/agents/**` dependency is certified by `tes_map_oracle`. Flipping it silently is a regression. It is a migration line with a renegotiated oracle and a coexistence rule. |
| Run anti-contamination outbound as a new line separate from the existing Super SPEC. | The existing anti-contamination Super SPEC owns the contamination intent. Capsule-first is its outbound completion; keeping them separate would split one concern across two diverging lines. |
