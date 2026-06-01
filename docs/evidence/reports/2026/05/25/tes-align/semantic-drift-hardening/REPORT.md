---
tds_id: evidence.tes_align_semantic_drift_hardening_20260525
tds_class: evidence
status: active
consumer: TES maintainers, adapter authors, and certification reviewers
source_of_truth: false
evidence_level: L2
---

# TES Align Semantic Drift Hardening — Certification Packet

Date: 2026-05-25
Run id: tes-align/semantic-drift-hardening
Domain: tes-align
Retention status: retained

## Mission

Harden `/tes-align` across adapter skill surfaces and project-alignment oracles
so TES can detect and correct project-specific semantic drift, not only
structural mesh completeness. Carry the mechanism in TES while leaving the
vocabulary to the target project.

Source brief:
`docs/roadmap/product/TES-ALIGN-SEMANTIC-DRIFT-HARDENING-SUPER-PROMPT.md`.

## Origin Failure Pattern

A canary certification loop produced a structurally green oracle result while
active `docs/agents/**` documentation still asserted retired claims and used
implementation vocabulary the project had already moved past. The structural
PASS became a false green because no gate existed to ask: did the mesh absorb
the latest project truth, and did it stop using the language the project
retired?

## Behavior Before And After

| Question | Before | After |
|----------|--------|-------|
| Does the operating mesh exist? | Yes — structural oracle answered this. | Yes — structural oracle preserved. |
| Does the mesh tell the current project truth? | No portable gate. False greens possible. | Portable Semantic Residue Gate runs when a project contract is declared. |
| Are newer accepted ADRs read before PASS? | Not enforced. | Freshness reconciliation lowers status to `NEEDS_REVIEW` when newer ADRs introduce successor vocabulary absent from the active mesh. |
| Can historical evidence keep retired terms? | Would falsely fail under naive substring scans. | `allowed_paths` allowlist in the contract preserves history without breaking the gate. |
| Does a short literal term falsely match a longer unrelated word? | Naive substring scans would. | Oracle uses explicit word boundaries; short literals only match whole tokens. |
| Is failure output machine-readable? | Prose only. | Structured findings with `code`, `severity`, `entry_id`, `path`, `line`, `match`, `reason`, `successor`. `--json` and `--strict` available. |

## Files Changed

| File | Role |
|------|------|
| `docs/mesh/TES-ALIGN-SKILL-SOURCE-OF-TRUTH.md` | Refreshed `sources_verified_on` to 2026-05-25, added Semantic Residue and Freshness responsibilities summary, oracle requirement rows, locks, and ledger entry. |
| `docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` | New governed reference document holding the portable contract shape, severity semantics, allowlist rules, reconciliation heuristic, and structured finding shape. |
| `scripts/project_alignment_oracle.py` | Added contract loader, residue gate, freshness reconciliation, `--json` / `--strict`, and four new self-test fixtures. |
| `src/adapters/codex/skills/tes-align/SKILL.md` | Required reading of newest ADRs/evidence before PASS, added Semantic Residue Gate step and locks. |
| `src/adapters/codex/skills/tes-align/references/alignment-procedure.md` | Added Semantic Residue Gate, Freshness Reconciliation, and Project-Local Vocabulary Boundary sections. |
| `src/adapters/codex/skills/tes-align/docs/CONTRACT-HISTORY.md` | New changelog row 2026-05-25; new failure modes prevented. |
| `src/adapters/claude/skills/tes-align/SKILL.md` | Parity with Codex skill. |
| `src/adapters/claude/skills/tes-align/references/alignment-procedure.md` | Parity with Codex reference. |
| `src/adapters/claude/skills/tes-align/docs/CONTRACT-HISTORY.md` | Parity with Codex history. |
| `src/adapters/cursor/rules/tes-guidelines.mdc` | Extended existing `/tes-align` routing line to require Semantic Residue Gate and freshness reads where Cursor owns the routing surface. |
| `docs/INDEX.md`, `docs/tds/DOCS-INDEX.yml`, `scripts/validate_reference_package.py` | Indexed the new reference document. |

## Adapter Surfaces Updated

- Codex: `src/adapters/codex/skills/tes-align/**`.
- Claude: `src/adapters/claude/skills/tes-align/**`.
- Cursor: routing line in `src/adapters/cursor/rules/tes-guidelines.mdc`. No
  fake Cursor skill folder was created because Cursor does not own an
  equivalent skill surface for `/tes-align`.

## Oracle Behavior Snapshot

```text
$ python3 scripts/project_alignment_oracle.py --self-test
{
  "coverage": "source-package-contract",
  "failures": [],
  "self_test_mode": "package",
  "status": "PASS",
  "version": "0.3.123"
}
[project-alignment] PASS
```

The self-test now exercises:

| Fixture | Expected outcome |
|---------|------------------|
| Good fixture (no residue contract) | PASS, no contract emits a single advisory warning |
| Literal placeholder fixture | PASS |
| Roadmap missing Unknown lane | FAIL |
| Roadmap missing System X-Ray | FAIL |
| Roadmap missing Convergence Line | FAIL |
| Generic placeholder language | FAIL |
| Obsidian runtime pollution | FAIL |
| **Stale current claim in active doc under residue contract** | **FAIL with structured finding citing `entry_id`, `path`, `line`, and `match`** |
| **Same retired term retained under `allowed_paths` historical evidence** | **PASS** |
| **Word-boundary regression: short literal vs longer unrelated word** | **PASS — no false positive** |
| **Malformed contract entry declaring both `term` and `pattern`** | **FAIL with `residue.entry_conflict` code** |

## Acceptance Gates

| Gate | Result |
|------|--------|
| `python3 scripts/project_alignment_oracle.py --self-test` | PASS |
| `npm run project-alignment:self-test` | PASS |
| `python3 scripts/materialize_adapter.py all --check` | PASS |
| `python3 scripts/adapter_parity_readiness.py` | GO (claude, codex, cursor) |
| `python3 scripts/validate_reference_package.py` | PASS (200 files) |
| `python3 scripts/validate_tds.py` | PASS (110 documents) |
| `python3 scripts/validate_doc_size.py` | PASS |
| `python3 scripts/validate_reference_graph.py` | PASS |
| `python3 scripts/build_public_docs.py --check` | PASS |
| `python3 scripts/tds_surface_oracle.py` | PASS |
| `git diff --check` / `git diff --cached --check` | clean |
| `npm run commit:check` | PASS end-to-end |

`npm run commit:check` was executed once with all changes staged, confirming
the staged-ready validator accepted the new tracked path
`docs/mesh/TES-ALIGN-SEMANTIC-RESIDUE.md`. The stage was then reset because
this packet is evidence only; commit and release decisions remain with the
maintainer.

## Target Project Canary

The certification ran on package-internal fixtures only. The canary that
originally exposed the gap was target-side and remains the responsibility of
the next real-project run to re-execute against the hardened oracle.

```text
target-project canary used: none in this packet
required follow-up: rerun the originating canary with the hardened oracle
                    and a project-local SEMANTIC-RESIDUE.yml contract
```

## Limits And Remaining Risks

- Freshness reconciliation uses a deterministic but heuristic token diff
  between the newest ADR and the active mesh. Highly textual ADRs may emit
  benign `notes`. The gate stays advisory at `notes` level and only escalates
  to `needs_review` when an ADR is newer than the latest retained evidence.
- The contract loader requires PyYAML when a project declares a residue
  contract. The package already validates PyYAML availability through
  `validate_reference_package.py::yaml_surface_failures` so this dependency
  is implicit. When PyYAML is unavailable on a target, the oracle records a
  structural failure naming the missing dependency.
- Allowlist matching uses `fnmatch` semantics with explicit handling for
  `**` patterns. Project authors should follow the documented globs and
  avoid regex inside `allowed_paths`.
- The cross-adapter parity check is structural and contract-level. The
  cross-runtime behavior of the gate has not been re-certified against the
  full behavioral parity matrix; the closest existing behavioral evidence is
  the structural `adapter_parity_readiness` GO recorded above.

## Final Claim

```text
TES Align semantic drift hardening: PASS.
```

The structural alignment oracle is preserved. The Semantic Residue Gate is
portable, contract-driven, and target-vocabulary-free. Adversarial and
allowlist fixtures both behave as required. Cross-adapter materialization
and parity readiness gates remain GO.
