---
tds_id: architecture.project_structure
tds_class: architecture
status: active
consumer: maintainers and adapter authors
source_of_truth: true
evidence_level: L2
tver: 0.2.8
---

# Project Structure

The repository is a source package, not a target-project install tree.

## Root

Root files are only entrypoints and local project controls:

| Path | Responsibility |
|------|----------------|
| `README.md` | User entrypoint |
| `llms.txt` | Optional machine-readable map to canonical public docs |
| `AGENTS.md` | Thin repository bootloader for agents working here |
| `package.json` | Local validation commands |
| `lefthook.yml` | Git hook entrypoint for the staged commit gate |
| `scripts/staged_commit_gate.py` | Intelligent staged-file commit router |
| `.githooks/**` | Git hook entrypoints (delegate to Lefthook) |
| `scripts/**` | Deterministic oracles and package helpers |
| `benchmarks/**` | Portable eval data |
| `docs/**` | Method, architecture, and eval explanation |
| `src/**` | Canonical copyable adapter source |
| `dist/**` | Temporary generated adapter inspection output, ignored by Git |
| `docs/dist/**` | Versioned public installer bundles served by GitHub Pages |
| `docs/llms.txt` | GitHub Pages-served mirror of the public LLM map |
| `docs/i18n/**` | JSON and YAML source for rendered public docs |
| Git history | Versioning and changelog trail |

`scripts/**` is classified by consumer, not by directory. Validator-only scripts are maintainer gates. Installer, Cortex, MCP, Field Reports, and adapter scripts are delivered behavior when adopters receive, invoke, or certify them. Bootstrap script entrypoints live under `scripts/bootstrap/**`; installer wrappers do not belong in the repository root.

Code files are maintainability surfaces. Any changed code file must carry direct documentation (module docstring, top-level file comment, or targeted inline comment for non-obvious logic) or be named by an associated Markdown document that explains its contract. `scripts/code_documentation_oracle.py` enforces this on staged code in `npm run commit:check`.

## Source

`src/**` is the only canonical home for installable agent material.

| Path | Responsibility |
|------|----------------|
| `src/adapters/codex/AGENTS.md` | Codex target bootloader source |
| `src/adapters/codex/plugin/**` | Codex plugin metadata source-only template |
| `src/adapters/codex/skills/**` | Codex-native skill source |
| `src/adapters/claude/CLAUDE.md` | Claude Code instruction source |
| `src/adapters/claude/plugin/**` | Claude plugin metadata source-only template |
| `src/adapters/claude/skills/**` | Claude Code skill source |
| `src/adapters/cursor/CURSOR.md` | Cursor adapter note |
| `src/adapters/cursor/rules/**` | Cursor project rule source |

## Materialization

`scripts/materialize_adapter.py` turns canonical source into installable target trees. `npm run materialize:check` does this in a temporary directory. Direct write-mode materialization may create `dist/adapters/**` for inspection only, and package validation requires that output to be purged afterward:

| Adapter | Materialized shape |
|---------|--------------------|
| Codex | `AGENTS.md` plus `.agents/skills/**` |
| Claude | `CLAUDE.md` and `.claude/skills/**` |
| Cursor | `CURSOR.md` plus `.cursor/rules/**` |

Use `npm run materialize:check` to verify this without writing to `dist/**`. `src/adapters/**` remains the only local canonical adapter source.

`docs/dist/<version>/` is the exception to the ignored `dist/**` rule. It holds the public TES ZIP, `.sha256`, and `index.json` used by installer staging. Target installs extract that ZIP under local `.tes/setup/<version>/`, which is staging cache and must stay out of Git.

`scripts/bootstrap/install.sh` and `scripts/bootstrap/install.ps1` are the canonical shell entrypoints for mechanical adapter installation. Root `install.sh` and `install.ps1` are intentionally absent so the root remains user-facing rather than a script surface.

`scripts/tes_install.py` is the thin mechanical package installer. It stages a TES bundle, applies runtime capabilities, writes `.tes/tes-install-lock.json` and `.tes/postinstall.json`, installs first-session hooks for selected agents, renders host-specific hook output, writes runtime hook evidence, and leaves semantic project preparation to the idempotent post-install routine. `scripts/pretooluse_kernel.py` is the associated host-neutral PreToolUse decision kernel: it normalizes tool payloads, extracts paths, classifies allow/supervise/block outcomes, and intentionally does not install hooks, render Claude/Codex/Cursor protocols, or write ledgers. `scripts/pretooluse_session.py` is the sibling session coordinator: it owns only the anti-cry-wolf sentinel and same-session repetition state for governed supervision; it must not hide the `🍳 Flash-Fry` marker when the Mantra Gate applies.

`bin/tes.js` is the commercial npx entrypoint. It accepts `add` and `install` as user-facing aliases, resolves Python, then delegates to `scripts/tes_install.py install` without reimplementing installer logic.

`scripts/install_mcp.py` is separate from adapter materialization. It activates the Cortex MCP server in a target project by copying local helpers to `.tes/bin/**` and writing project-scoped runtime config. The installed config is governed-write capable by default for ADR 0002 remember; `--read-only` explicitly hides the governed remember lane. Codex, Claude Code, Cursor, and VS Code MCP configs are verified after write at their native project-scoped paths.

`scripts/tes_update.py` plans low-friction updates by comparing installed and cloud package versions, detecting applied IDE surfaces, and recommending the route behind the visible `/tes-update` skill and its `/tes:update` compatibility alias.

`scripts/tes_bundle.py` orchestrates clean runtime install: stage the versioned bundle, create `.tes/bk/<timestamp>/manifest.json`, apply canonical runtime assets, recover useful old governance semantics into `docs/agents/**`, and restore backed-up root governance on request.

`scripts/tes_init.py` initializes and recertifies a target project. It writes `docs/agents/PROJECT-REGISTER.md` and `docs/agents/PROJECT-CONTEXT.md` before slower gates finish, so blocked gates leave auditable evidence instead of an uninitialized runtime.

`scripts/project_context_oracle.py` certifies that the generated `PROJECT-CONTEXT.md` is useful rather than decorative: it checks identity, manifest evidence, territories, source anchors, quality scripts, explicit unknowns, and absence of bulk-copied source code.

`scripts/tes_legacy_retirement.py` is the closed-catalog cleanup gate for updates and local npx installs. It removes known old runtime assets, migrates Field Reports state, archives legacy retrofit and hook-ledger records, compacts exact duplicate runtime hook rows, removes ephemeral hook-audit harness residue, and preserves project context.

`scripts/root_context.py` scans root runtime files such as `AGENTS.md`, `CLAUDE.md`, and Cursor rules before or from central backup evidence. Project-owned instructions must be backed up before overwrite and recovered into `docs/agents/**` or marked `NEEDS_REVIEW`.

`scripts/field_reports.py` installs the local Field Reports `pre-push` drain at the active Git hook path (`core.hooksPath` aware) and records sanitized operational facts under `.tes/field-reports/**`. That directory is local transport state, not repository truth.

`scripts/cortex_git_tap.py` installs marked `pre-commit`, `post-commit`, and `post-checkout` Git hook blocks at the active Git hook path (`core.hooksPath` aware) and records privacy-safe Cortex observation events under `.tes/runtime/cortex/git-tap/**`. It is an observation/proposal runtime only; hooks must not write curated memory into `docs/**`.

`.github/ISSUE_TEMPLATE/tes-field-report.yml` and `.github/workflows/field-report-governance.yml` govern the central GitHub receiver for those reports. The local oracle is `scripts/field_reports_github_oracle.py`. GitHub automation readiness, including Dependabot ecosystem and directory sanity when `.github/dependabot.yml` exists, is checked by `scripts/github_readiness_oracle.py`.

`scripts/install_smoke.py`, `scripts/claude_plugin_oracle.py`, `scripts/github_readiness_oracle.py`, `scripts/retention_metadata.py`, and `scripts/validate_reference_graph.py` provide deterministic closure gates for assisted installation, local Claude plugin shape, GitHub automation readiness, portable project-context fixtures, evidence retention policy, and governed link drift.

## Docs

`docs/**` explains the mesh and keeps large context out of the root.

| Path | Responsibility |
|------|----------------|
| `docs/mesh/**` | Method, principles, scorecard |
| `docs/evals/**` | Eval design and examples |
| `docs/governance/**` | Cross-tool authority and alignment rules |
| `docs/governance/MAINTAINER-CORRELATION-RULE.md` | Local maintainer map for package edits, not installed project context |
| `docs/evidence/**` | Current evidence claims, temporal run reports, and archive indexes |
| `docs/adapters/**` | User adapter guidance |
| `docs/architecture/**` | Repository topology and boundaries |
| `docs/i18n/**` | Modular text and structure source for public HTML |
| `docs/tds/**` | Documentation contract and governed index |

`docs/index.html` and `docs/install/USER-MANUAL.html` are generated static HTML surfaces. They stay checked in for GitHub Pages and `file://` use, while commercial, documentation, and user-facing copy lives in `docs/i18n/tes-public.content.json` and `docs/i18n/tes-public.structure.yml`. Regenerate and check them with `scripts/build_public_docs.py`.

## Structural Locks

- Root hidden tool folders such as `.agents`, `.cursor`, and `.claude-plugin` are not canonical source in this repository; root `skills/**` and plugin folders are treated as obsolete target runtime surfaces, not package source.
- Target projects may receive hidden adapter folders during installation, but this reference package keeps source in `src/**`.
- A new adapter must create one source directory under `src/adapters/<tool>/` and one short user guide under `docs/adapters/` only when needed.
- Validation must fail if source leaks back into the root.
- Generated `dist/**` output must be reproducible from `src/**`; versioned public bundles under `docs/dist/**` must pass `public_bundle_oracle.py`.
- Every push that changes delivered installer/helper/runtime behavior must advance the public bundle procedure: generate a new versioned ZIP under `docs/dist/<version>/`, write the matching `.sha256` sidecar and `index.json`, expose source commit metadata, keep the setup installer scripts inside the ZIP, and retain evidence from the bundle oracle.
- Do not add `CHANGELOG.md`; commit history is the changelog.
