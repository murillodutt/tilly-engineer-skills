---
tds_id: docs.index
tds_class: index
status: active
consumer: maintainers and agents
source_of_truth: true
evidence_level: L2
tver: 0.4.17
---

# Tilly Engineer Skills Docs

This documentation layer explains the method behind the source package without
turning the repository root into an inventory.

## Map

| Need | Document |
|------|----------|
| Repository shape and ownership | `architecture/PROJECT-STRUCTURE.md` |
| TES namespace migration catalog | `architecture/TES-NAMING-MIGRATION-CATALOG.md` |
| Archived TES Memory Lifecycle ADR | `adr/0001-tes-memory-lifecycle.md` |
| Archived Cortex governed MCP write lane ADR | `adr/0002-cortex-governed-mcp-write-lane.md` |
| Active Cortex MCP capability expansion ADR | `adr/0003-cortex-mcp-capability-expansion.md` |
| Active installed certification and Field Reports intake ADR | `adr/0003-1-installed-certification-and-field-reports-feedback-intake.md` |
| Active TES TTS pronunciation normalization and enrichment ADR | `adr/0004-tes-tts-pronunciation-normalization-and-enrichment.md` |
| User manual PT/EN/ES | `install/USER-MANUAL.html` |
| Agent manual | `install/AGENT-MANUAL.md` |
| Agent oracle inventory | `install/AGENT-ORACLE-INVENTORY.md` |
| GitHub Pages landing | `index.html` |
| Public page i18n source | `i18n/tes-public.content.json` and `i18n/tes-public.structure.yml` |
| Live GitHub Pages landing | `https://murillodutt.github.io/tilly-engineer-skills/` |
| Optional public LLM navigation map | `../llms.txt` and `llms.txt` |
| Public installer bundle | `dist/0.3.151/tilly-engineer-skills-0.3.151.zip` |
| GitHub package-spec installation | `install/INSTALL.md` |
| Optional TES TTS OmniVoice local provider guide | `install/TES-TTS-OMNIVOICE.md` |
| Command trigger matrix | `install/COMMAND-TRIGGERS.md` |
| Runtime navigation library | `install/navigation/NAVIGATION-LIBRARY.md` |
| Tool-neutral engineering principles | `mesh/PRINCIPLES.md` |
| Neutral behavioral contract manifest | `mesh/CONTRACT-MANIFEST.yml` |
| Context mesh method | `mesh/CONTEXT-MESH-METHOD.md` |
| TES Align skill source of truth | `mesh/TES-ALIGN-SKILL-SOURCE-OF-TRUTH.md` |
| TES Align semantic residue gate | `mesh/TES-ALIGN-SEMANTIC-RESIDUE.md` |
| TES Mantra Gate | `mesh/MANTRA-GATE.md` |
| TES Scope Contract | `mesh/SCOPE-CONTRACT.md` |
| TES Event Ledger | `mesh/EVENT-LEDGER.md` |
| TES Checkpoints | `mesh/CHECKPOINTS.md` |
| TES Cortex | `mesh/CORTEX.md` |
| TES Cortex MCP | `mesh/CORTEX-MCP.md` |
| TES Field Reports | `mesh/FIELD-REPORTS.md` |
| Tilly Git safety | `mesh/GIT-SAFETY.md` |
| Local quality recipe | `mesh/LOCAL-QUALITY-RECIPE.md` |
| Adoption and convergence scorecard | `mesh/SCORECARD.md` |
| Eval and ablation design | `evals/EVALS.md` |
| Cortex memory benchmarks | `evals/CORTEX-MEMORY-BENCHMARKS.md` |
| Detailed examples | `evals/EXAMPLES.md` |
| Cross-adapter parity gate | `evals/PARITY-GATE.md` |
| Evidence retention policy | `evidence/INDEX.md` |
| Current evidence claims | `evidence/current/CLAIMS.md` |
| Cross-tool agentic governance | `governance/AGENTIC-ALIGNMENT-GOVERNANCE.md` |
| Maintainer correlation rule | `governance/MAINTAINER-CORRELATION-RULE.md` |
| Sync audit checklist | `governance/SYNC-AUDIT-CHECKLIST.md` |
| Adapter capability matrix | `adapters/ADAPTER-CAPABILITY-MATRIX.md` |
| Platform differences reference | `adapters/PLATFORM-DIFFERENCES.md` |
| Codex adapter guide | `adapters/CODEX.md` |
| Claude adapter guide | `adapters/CLAUDE.md` |
| Cursor adapter guide | `adapters/CURSOR.md` |
| Adapter materialization | `adapters/MATERIALIZATION.md` |
| Codex adapter pipeline | `adapters/pipelines/CODEX-PIPELINE.md` |
| Claude adapter pipeline | `adapters/pipelines/CLAUDE-PIPELINE.md` |
| Cursor adapter pipeline | `adapters/pipelines/CURSOR-PIPELINE.md` |
| Current roadmap index | `roadmap/README.md` |
| Cortex MCP Capability Expansion Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-mcp-capability-expansion.md` |
| Cortex MCP Host Segmentation Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-mcp-host-segmentation.md` |
| TES Memory Lifecycle Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-memory-lifecycle.md` |
| Cortex Memory Benchmark Harness Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-cortex-memory-benchmark-harness.md` |
| TES Anti-Contamination Hardening Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-anti-contamination-hardening.md` |
| TES Postinstall And Cortex Curation Hardening Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-postinstall-cortex-hardening.md` |
| TES Postinstall Recovery Contract Symmetry Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-postinstall-recovery-contract-symmetry.md` |
| TES NPX MCP Convergence Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-npx-mcp-convergence.md` |
| TES Installed Certification And Field Reports Hardening Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-installed-certification-and-field-reports-hardening.md` |
| TES TTS Sequential Convergence Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-sequential-convergence.md` |
| TES TTS Ten-SPEC Convergence Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-ten-spec-convergence.md` |
| TES TTS Owner Decision Gate Goal Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-owner-decision-gate.md` |
| TES TTS TTS-000 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-000-preflight-and-baseline.md` |
| TES TTS TTS-001 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-001-roadmap-and-spec-coherence.md` |
| TES TTS TTS-002 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-002-default-language-selector.md` |
| TES TTS TTS-003 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-003-fixture-schema.md` |
| TES TTS TTS-004 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-004-fixture-corpus.md` |
| TES TTS TTS-005 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-005-instruction-normalizer-oracle.md` |
| TES TTS TTS-006 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-006-provider-probe-contract.md` |
| TES TTS TTS-007 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-007-provider-candidate-review.md` |
| TES TTS TTS-008 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-008-adapter-parity.md` |
| TES TTS TTS-009 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-009-acceptance-and-release-decision.md` |
| TES TTS TTS-010 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-010-owner-approval-gate.md` |
| TES TTS TTS-011 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-011-owner-decision-required.md` |
| TES TTS TTS-012 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-012-explicit-owner-decision.md` |
| TES TTS TTS-013 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-013-owner-decision-pending.md` |
| TES TTS TTS-014 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-014-owner-decision-still-pending.md` |
| TES TTS TTS-015 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-015-owner-decision-still-required.md` |
| TES TTS TTS-016 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-016-owner-decision-remains-required.md` |
| TES TTS TTS-017 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-017-owner-decision-open.md` |
| TES TTS TTS-018 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-018-owner-decision-unresolved.md` |
| TES TTS TTS-019 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-019-owner-decision-still-unresolved.md` |
| TES TTS TTS-020 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-020-owner-decision-continues-unresolved.md` |
| TES TTS TTS-021 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-021-owner-decision-remains-unresolved.md` |
| TES TTS TTS-022 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-022-owner-decision-still-remains-unresolved.md` |
| TES TTS TTS-023 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-023-owner-decision-unresolved-again.md` |
| TES TTS TTS-024 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-024-owner-decision-still-unresolved-again.md` |
| TES TTS TTS-025 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-025-owner-decision-continues-unresolved-again.md` |
| TES TTS TTS-026 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-026-owner-decision-remains-unresolved-again.md` |
| TES TTS TTS-027 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-027-owner-decision-still-remains-unresolved-again.md` |
| TES TTS TTS-028 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-028-owner-decision-remains-open-again.md` |
| TES TTS TTS-029 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-029-owner-decision-still-open-again.md` |
| TES TTS TTS-030 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-030-owner-decision-continues-open-again.md` |
| TES TTS TTS-031 ready goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-031-owner-decision-remains-open-yet-again.md` |
| TES TTS TTS-032 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-TTS-032-owner-decision-still-open-yet-again.md` |
| TES TTS SPEC-001 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-SPEC-001-roadmap-compaction-agent-default-language.md` |
| TES TTS SPEC-002 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-SPEC-002-fixture-corpus-complete.md` |
| TES TTS SPEC-003 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-SPEC-003-deterministic-instruction-normalizer.md` |
| TES TTS SPEC-004 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-SPEC-004-pronunciation-enrichment-rules.md` |
| TES TTS SPEC-005 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-SPEC-005-provider-probe-no-write.md` |
| TES TTS SPEC-006 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-SPEC-006-provider-candidate-selection.md` |
| TES TTS SPEC-007 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-SPEC-007-optional-translation-layer.md` |
| TES TTS SPEC-008 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-SPEC-008-optional-g2p-pronunciation-provider-layer.md` |
| TES TTS SPEC-009 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-SPEC-009-release-identity-sync-readiness.md` |
| TES TTS SPEC-010 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-SPEC-010-final-audit-and-closure.md` |
| TES TTS OWNER-001 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-OWNER-001-acceptance-release-sync-decision.md` |
| TES TTS OWNER-001 acceptance decision | `roadmap/tes-tts/TES-TTS-OWNER-001-ACCEPTANCE-DECISION.md` |
| TES TTS capability migration Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-capability-migration.md` |
| TES TTS conversational rendering Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-conversational-rendering.md` |
| TES TTS PT-BR lexical normalization Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-ptbr-lexical-normalization.md` |
| TES TTS lexical runtime engine latency reduction Super SPEC | `roadmap/goals/super-specs/GOAL-SUPER-SPEC-tes-tts-lexical-runtime-engine-latency-reduction.md` |
| TES TTS RTE-006 runtime audit and closure | `roadmap/tes-tts/TES-TTS-RTE-006-RUNTIME-AUDIT-AND-CLOSURE.md` |
| TES TTS CAP-001 feasibility study | `roadmap/tes-tts/TES-TTS-CAP-001-PORTABLE-CAPABILITY-FEASIBILITY.md` |
| TES TTS CAP-001 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-CAP-001-portable-capability-migration.md` |
| TES TTS CAP-002 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-CAP-002-speech-transformation-hardening.md` |
| TES TTS CAP-003 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-CAP-003-pronunciation-hints-protected-terms.md` |
| TES TTS CAP-004 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-CAP-004-provider-fallback-catalog-use.md` |
| TES TTS CAP-005 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-CAP-005-adapter-parity-final-local-audit.md` |
| TES TTS CAP-005 final local audit | `roadmap/tes-tts/TES-TTS-CAP-005-FINAL-LOCAL-AUDIT.md` |
| TES TTS CAP-006 conversational spoken rendering | `roadmap/tes-tts/TES-TTS-CAP-006-CONVERSATIONAL-SPOKEN-RENDERING.md` |
| TES TTS CAP-006 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-CAP-006-conversational-spoken-rendering.md` |
| TES TTS CAP-007 exact-island protected-span hardening | `roadmap/tes-tts/TES-TTS-CAP-007-EXACT-ISLAND-PROTECTED-SPAN-HARDENING.md` |
| TES TTS CAP-007 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-CAP-007-exact-island-protected-span-hardening.md` |
| TES TTS CAP-008 table list code block oralization | `roadmap/tes-tts/TES-TTS-CAP-008-TABLE-LIST-CODE-BLOCK-ORALIZATION.md` |
| TES TTS CAP-008 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-CAP-008-table-list-code-block-oralization.md` |
| TES TTS CAP-009 mixed-language English identity hardening | `roadmap/tes-tts/TES-TTS-CAP-009-MIXED-LANGUAGE-ENGLISH-IDENTITY-HARDENING.md` |
| TES TTS CAP-009 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-CAP-009-mixed-language-english-identity-hardening.md` |
| TES TTS CAP-010 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-CAP-010-conversational-rendering-final-audit.md` |
| TES TTS LEX-001 PT-BR lexical dataset manifest | `roadmap/tes-tts/TES-TTS-LEX-001-PTBR-LEXICAL-DATASET-MANIFEST.md` |
| TES TTS LEX-001 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-LEX-001-ptbr-lexical-dataset-manifest.md` |
| TES TTS LEX-002 PT-BR lexical lookup oracle | `roadmap/tes-tts/TES-TTS-LEX-002-PTBR-LEXICAL-LOOKUP-ORACLE.md` |
| TES TTS LEX-002 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-LEX-002-ptbr-lexical-lookup-oracle.md` |
| TES TTS LEX-003 spoken-rendering integration boundary | `roadmap/tes-tts/TES-TTS-LEX-003-SPOKEN-RENDERING-INTEGRATION-BOUNDARY.md` |
| TES TTS LEX-003 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-LEX-003-spoken-rendering-integration-boundary.md` |
| TES TTS LEX-004 fixture migration | `roadmap/tes-tts/TES-TTS-LEX-004-FIXTURE-MIGRATION-FROM-MARKDOWN-SHAPED-TTS-CASES.md` |
| TES TTS LEX-004 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-LEX-004-fixture-migration-from-markdown-shaped-tts-cases.md` |
| TES TTS LEX-005 PT-BR lexical final audit | `roadmap/tes-tts/TES-TTS-LEX-005-PTBR-LEXICAL-FINAL-AUDIT.md` |
| TES TTS LEX-005 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-LEX-005-ptbr-lexical-final-audit.md` |
| TES TTS RTE-000 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-RTE-000-preflight-latency-baseline.md` |
| TES TTS RTE-001 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-RTE-001-compiled-lexical-index-contract.md` |
| TES TTS RTE-002 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-RTE-002-hot-path-span-matcher.md` |
| TES TTS RTE-003 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-RTE-003-fast-path-spoken-rendering.md` |
| TES TTS RTE-004 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-RTE-004-request-local-memoization.md` |
| TES TTS RTE-005 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-RTE-005-chunked-preparation-boundary.md` |
| TES TTS RTE-006 historical goal prompt | `roadmap/goals/prompts/tes-tts/GOAL-PROMPT-tes-tts-RTE-006-runtime-audit-and-closure.md` |
| TES TTS skill roadmap | `roadmap/tes-tts/TES-TTS-SKILL-ROADMAP.md` |
| TES TTS skill roadmap registry | `roadmap/tes-tts/TES-TTS-SKILL-ROADMAP-REGISTRY.md` |
| TES TTS skill roadmap history | `roadmap/tes-tts/TES-TTS-SKILL-ROADMAP-HISTORY.md` |
| TES TTS acceptance and release decision | `roadmap/tes-tts/TES-TTS-ACCEPTANCE-AND-RELEASE-DECISION.md` |
| TES TTS owner approval gate | `roadmap/tes-tts/TES-TTS-OWNER-APPROVAL-GATE.md` |
| TES TTS owner decision required | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-REQUIRED.md` |
| TES TTS explicit owner decision | `roadmap/tes-tts/TES-TTS-EXPLICIT-OWNER-DECISION.md` |
| TES TTS owner decision pending | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-PENDING.md` |
| TES TTS owner decision still pending | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-STILL-PENDING.md` |
| TES TTS owner decision still required | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-STILL-REQUIRED.md` |
| TES TTS owner decision remains required | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-REMAINS-REQUIRED.md` |
| TES TTS owner decision open | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-OPEN.md` |
| TES TTS owner decision unresolved | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-UNRESOLVED.md` |
| TES TTS owner decision still unresolved | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-STILL-UNRESOLVED.md` |
| TES TTS owner decision continues unresolved | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-CONTINUES-UNRESOLVED.md` |
| TES TTS owner decision remains unresolved | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-REMAINS-UNRESOLVED.md` |
| TES TTS owner decision still remains unresolved | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-STILL-REMAINS-UNRESOLVED.md` |
| TES TTS owner decision unresolved again | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-UNRESOLVED-AGAIN.md` |
| TES TTS owner decision still unresolved again | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-STILL-UNRESOLVED-AGAIN.md` |
| TES TTS owner decision continues unresolved again | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-CONTINUES-UNRESOLVED-AGAIN.md` |
| TES TTS owner decision remains unresolved again | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-REMAINS-UNRESOLVED-AGAIN.md` |
| TES TTS owner decision still remains unresolved again | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-STILL-REMAINS-UNRESOLVED-AGAIN.md` |
| TES TTS owner decision remains open again | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-REMAINS-OPEN-AGAIN.md` |
| TES TTS owner decision still open again | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-STILL-OPEN-AGAIN.md` |
| TES TTS owner decision continues open again | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-CONTINUES-OPEN-AGAIN.md` |
| TES TTS owner decision remains open yet again | `roadmap/tes-tts/TES-TTS-OWNER-DECISION-REMAINS-OPEN-YET-AGAIN.md` |
| TES TTS normalization architecture SPEC | `roadmap/tes-tts/TES-TTS-NORMALIZATION-ARCHITECTURE-SPEC.md` |
| TES TTS normalization execution SPEC | `roadmap/tes-tts/TES-TTS-NORMALIZATION-EXECUTION-SPEC.md` |
| TES TTS normalization fixture schema | `roadmap/tes-tts/TES-TTS-NORMALIZATION-FIXTURE-SCHEMA.md` |
| TES TTS provider candidate review | `roadmap/tes-tts/TES-TTS-PROVIDER-CANDIDATE-REVIEW.md` |
| TES TTS SPEC 001 roadmap compaction and agent default language | `roadmap/tes-tts/TES-TTS-SPEC-001-roadmap-compaction-agent-default-language.md` |
| TES TTS SPEC 002 fixture corpus complete | `roadmap/tes-tts/TES-TTS-SPEC-002-fixture-corpus-complete.md` |
| TES TTS SPEC 003 deterministic instruction normalizer | `roadmap/tes-tts/TES-TTS-SPEC-003-deterministic-instruction-normalizer.md` |
| TES TTS SPEC 004 pronunciation enrichment rules | `roadmap/tes-tts/TES-TTS-SPEC-004-pronunciation-enrichment-rules.md` |
| TES TTS SPEC 005 provider probe no-write | `roadmap/tes-tts/TES-TTS-SPEC-005-provider-probe-no-write.md` |
| TES TTS SPEC 006 provider candidate selection | `roadmap/tes-tts/TES-TTS-SPEC-006-provider-candidate-selection.md` |
| TES TTS SPEC 007 optional translation layer | `roadmap/tes-tts/TES-TTS-SPEC-007-optional-translation-layer.md` |
| TES TTS SPEC 008 optional G2P pronunciation provider layer | `roadmap/tes-tts/TES-TTS-SPEC-008-optional-g2p-pronunciation-provider-layer.md` |
| TES TTS SPEC 009 release identity and sync readiness | `roadmap/tes-tts/TES-TTS-SPEC-009-release-identity-sync-readiness.md` |
| TES TTS SPEC 010 final audit and closure | `roadmap/tes-tts/TES-TTS-SPEC-010-final-audit-and-closure.md` |
| RC1 readiness roadmap | `roadmap/product/RC1-READINESS-ROADMAP.md` |
| TES Align semantic drift hardening prompt | `roadmap/product/TES-ALIGN-SEMANTIC-DRIFT-HARDENING-SUPER-PROMPT.md` |
| Flash-Fry skill gap spec | `roadmap/product/FLASH-FRY-SKILL-SPEC.md` |
| Historical next-session continuity | `roadmap/archive/notes/NEXT-STEPS-LETTER-2026-05-05.md` |
| TDS specification | `tds/TDS-SPEC.md` |
| TDS document index | `tds/DOCS-INDEX.yml` |

## Source Boundary

`docs/**` explains and audits behavior. It is not the installable source.

`docs/tds/DOCS-INDEX.yml` governs Markdown files under `docs/**`. Rendered
HTML and text surfaces such as `docs/index.html`,
`docs/install/USER-MANUAL.html`, and `docs/llms.txt` remain public
documentation entrypoints referenced here and in `README.md`, but they are not
listed as TDS documents because they do not carry Markdown frontmatter.

`docs/index.html` and `docs/install/USER-MANUAL.html` are rendered public
surfaces. Their commercial, documentation, and user-facing text is sourced from
`docs/i18n/tes-public.content.json` and structured by
`docs/i18n/tes-public.structure.yml`. Use
`python3 scripts/build_public_docs.py` to regenerate them and
`python3 scripts/build_public_docs.py --check` before closure.

Public surface review follows a source/render/output contract:

```text
The source is the contract.
The rendered document is evidence.
The module graph is the memory.
The generated surface must never become the hidden source.
```

Use `python3 scripts/tds_surface_oracle.py` to check rendered public docs
against their structured sources, copy-ready payloads, generated markers, TDS
labels, and public source map. Use `python3 scripts/tds_runtime_server.py` for
a local GitHub Pages-like runtime with `/_tds/health`, `/_tds/manifest`, and
`/_tds/check` endpoints.

Copyable adapter material lives in `src/adapters/**`:

| Adapter | Source |
|---------|--------|
| Codex | `../src/adapters/codex/**` |
| Claude | `../src/adapters/claude/**` |
| Cursor | `../src/adapters/cursor/**` |
