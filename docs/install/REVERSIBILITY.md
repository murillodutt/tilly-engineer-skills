---
tds_id: install.reversibility
tds_class: adapter
status: active
consumer: adopters uninstalling or reshaping a TES install, and agents driving detach/uninstall
source_of_truth: false
evidence_level: L2
tver: 0.3.170
---

# TES Install Reversibility — Detach, Uninstall, Attach-Health

The adopter-facing guide to undoing or reshaping a TES install. `docs/install/INSTALL.md` owns how TES installs; this document owns how it comes back off. The architecture behind both — the manifest, the two runtime writers, the per-surface removers — is the maintainer map `docs/architecture/INSTALLATION-FRAMEWORK.md` (source of truth); the invariants are `docs/adr/0004-tes-capsule-isolation-and-reversible-installation.md`.

Per ADR 0004 the install is reversible by construction: every project-visible write is recorded in the `tes-bundle-manifest@2` with a `restore_policy` and an `uninstall_action`, and each remover is the precise inverse of its writer.

## Reshape one surface — `detach`

`detach <surface>` removes a single attached surface and leaves the capsule and the other surfaces intact. It restores the project-owned file from the central backup, decomposes TES:CORE blocks out of bootloaders, prunes empty parent directories, and applies a sha256 fail-safe: a file you modified after install is preserved as `needs-review` rather than deleted.

```bash
python3 .tes/bin/tes_install.py detach root-context --target . --dry-run
python3 .tes/bin/tes_install.py detach root-context --target . --yes
```

Surfaces with no detach writer yet (`field-reports`, `gps`, `goals`, `mantra`) return `NEEDS_REVIEW` by design rather than a false success.

## Remove everything — `uninstall`

`uninstall` runs the same machine across every surface: it restores project-owned files from backup, removes every TES-owned surface, removes the capsule (`.tes/**`), and then the `capsule_residue_oracle` proves **zero active residue**. Inert exported project content (e.g. `docs/agents/**` authored by `/tes-init`) is retained and reported, not deleted.

```bash
python3 .tes/bin/tes_install.py uninstall --target . --dry-run
python3 .tes/bin/tes_install.py uninstall --target . --yes
python3 .tes/bin/capsule_residue_oracle.py --target .
```

A `PASS` from the residue oracle is the proof of a clean uninstall: `active_residue` is empty. A `FAIL` lists the surfaces that still carry TES state.

## Backups and rollback — `.tes/bk/**`

Before any runtime overwrite the installer creates `.tes/bk/<timestamp>/` with a manifest and a restore command. This is local rollback history; it stays out of Git.

```bash
python3 .tes/bin/tes_bundle.py backup --target .
python3 .tes/bin/tes_bundle.py restore --backup-id <id> --yes --target .
```

`detach` and `uninstall` restore from this backup automatically; the explicit commands above are for manual rollback or inspection.

## Attach-health — observed, never assumed

Reversibility depends on knowing what is actually attached. Attach health is verified per surface by execution proof, never inferred from config presence:

| Surface | Proof |
|---------|-------|
| `mcp` | a real out-of-process JSON-RPC handshake (`initialize` → `tools/list`) against the Cortex server |
| `hooks` | an execution sentinel the hook writes when it fires |
| `root-context` / `skills` | the materialized blocks/files are present |

When the host has not yet acted, the oracle reports an honest pending state instead of a false `PASS`:

- `PENDING_HOST_RESTART` — config written, server not yet spawned by the host.
- `PENDING_TRUST` — hook configured, not yet fired (host trust/approval pending).
- `HOST_UNOBSERVABLE` — TES did everything; the remaining proof is the host's to give.
- `DEGRADED` — a duplicate handler was detected.

```bash
python3 .tes/bin/attach_health_oracle.py --target . --surface mcp
python3 .tes/bin/tes_install.py doctor --target .
```

`doctor` is the read-only roll-up: capsule presence plus per-surface health.

## Certification basis

Reversibility is certified by the `capsule_residue_oracle` and the install/uninstall round-trip in `commit:check`. It is bench-certified; it is not yet field-proven against a live host session — the host-real canary is the only thing that upgrades a hook claim from "written correctly to disk" to "converged in real use".
