# Bump Scope Decision

Read this when `tes_bump.py --governance-check` reports
`NEEDS_VERSION_DECISION` and you need to pick the sync scope.

## The Three Scopes

### No bump

Governance verdict is `PASS`. The change is documentation, governance,
test scaffolding, or evidence — no delivered behavior, no installer
ref, no skill body, no oracle gate moved.

Sync surface: source only.
Phases run: pre-flight, validation, commit, push.
Phases skipped: identity bump, public refs, bundle, tag, release:check.

### Source-only bump

Governance verdict is `NEEDS_VERSION_DECISION`, but the change does not
move installer refs, i18n, or bundle behavior. Examples that fit here:

- Internal oracle hardening that does not change CLI flags.
- New self-test fixtures.
- Adapter source edits that materialize identically.

This scope is rare in practice. The TES `release_identity` block in
`AGENTS.md` allows it with an explicit closeout exception ("bump
intentionally deferred from public refs"), but most delivered-behavior
changes flow naturally into the bundle scope.

Sync surface: source identity only (no `docs/install/**`, no `i18n`, no
`docs/dist/`).
Phases run: identity bump, validation, commit, push.
Phases skipped: public refs, bundle publish, public HTML regen, tag,
release:check.

### Bump + bundle + public refs (default)

Governance verdict is `NEEDS_VERSION_DECISION` and delivered behavior
flows to adopters: skill body changed, oracle behavior changed, new
delivered command, new ref, installer copy moved.

Sync surface: everything.
Phases run: all 12 from `SKILL.md`.

This is the path the 0.3.124 and 0.3.125 cycles took. Use this scope by
default unless you can clearly justify the narrower one.

## Decision Heuristic

Ask: would a target project that installs the new version observe a
difference?

- Yes (skill body, oracle exit code, installer copy, command surface) →
  bundle scope.
- No (test fixtures, internal docs, governance) → no bump.
- Yes but installer refs were already moved this session, or refs stay
  on the old version intentionally → source-only with explicit closeout.

## Canonical Identity Bump File Set

When the scope is source-only or bundle:

| Surface | Path | Notes |
|---------|------|-------|
| Package manifest | `package.json` | `version` |
| CLI bin | `bin/tes.js` | `TES_VERSION` constant |
| Public badge | `README.md` | shields.io URL |
| TDS header | `docs/tds/DOCS-INDEX.yml` | top-level `version` |
| Doc index | `docs/INDEX.md` | "Public installer bundle" row |
| Codex doc | `docs/adapters/CODEX.md` | "Project version" |
| Roadmap | `docs/roadmap/README.md` | baseline sentence |
| RC roadmap | `docs/roadmap/RC1-READINESS-ROADMAP.md` | "Package version" |
| Script constants | `scripts/**.py` | `VERSION = "<old>"` (bulk sed safe) |
| Validator paths | `scripts/validate_reference_package.py` | `docs/dist/<old>/...` (3 entries) — see trap |
| Oracle fixture | `scripts/project_alignment_oracle.py` | `tes_version: <old>` |
| npx help text | `scripts/tes_npx_oracle.py` | `e.g. v<old>` |
| Codex plugin | `src/adapters/codex/plugin/plugin.json` | |
| Codex marketplace | `src/adapters/codex/plugin/marketplace.json` | two `version` keys |
| Claude plugin | `src/adapters/claude/plugin/plugin.json` | |
| Claude marketplace | `src/adapters/claude/plugin/marketplace.json` | two `version` keys |

When the scope is bundle:

| Surface | Path | Notes |
|---------|------|-------|
| Install command | `docs/install/INSTALL.md` | `#v<old>` in 3 commands |
| Trigger matrix | `docs/install/COMMAND-TRIGGERS.md` | install row |
| LLM map | `docs/llms.txt` | install line |
| i18n content | `docs/i18n/tes-public.content.json` | release_meta, manual_meta, version, code blocks (3 languages) |
| i18n structure | `docs/i18n/tes-public.structure.yml` | `bundle_index`. `bundle_sha256` updated post-publish. |

## Bulk Sed Pattern

For the script VERSION constants:

```bash
for f in scripts/*.py; do
  sed -i '' 's/^VERSION = "0\.3\.<old>"$/VERSION = "0.3.<new>"/' "$f"
done
```

The anchored `^...$` pattern protects against accidentally touching
strings inside docstrings, help text, or fixture data that happens to
contain the version.

## Why The Scoped Pattern Matters For `validate_reference_package.py`

The three REQUIRED_PATHS entries for the bundle look like:

```python
"docs/dist/0.3.124/index.json",
"docs/dist/0.3.124/tilly-engineer-skills-0.3.124.zip",
"docs/dist/0.3.124/tilly-engineer-skills-0.3.124.zip.sha256",
```

A global `sed 's|0.3.124|0.3.125|g'` against the whole file replaces the
**directory** version but also leaves the **zip filename** broken:

```python
"docs/dist/0.3.125/tilly-engineer-skills-0.3.124.zip",
```

This passed the syntax check but fails commit:check because the actual
zip file is named `tilly-engineer-skills-<new>.zip`.

Use a scoped pattern or just hand-edit those three lines. The trap cost
real time during the 0.3.125 cycle.
