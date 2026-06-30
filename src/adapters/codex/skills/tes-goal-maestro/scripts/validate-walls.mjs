// SPEC-021 — Mutation suite for executable wall fixtures.
// Para cada parede, monta uma fixture de VIOLAÇÃO em /tmp, roda o harness-dono e exige
// que ele DISPARE (exit≠0); depois monta a fixture REVERTIDA e exige PASS (exit 0).
// Uma parede só conta como "feita" quando dispara sob violação E passa quando revertida.
// Conduzido por agente independente (D1): este script não escreve nenhum dos harnesses.
//
//   node scripts/validate-walls.mjs
//
// Exit≠0 se QUALQUER parede falhar o par (não-disparo sob violação, ou não-passe ao reverter).

import { execFileSync, execSync } from 'node:child_process';
import { existsSync, mkdirSync, writeFileSync, mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const tmp = mkdtempSync(join(tmpdir(), 'walls-'));
const skillRoot = dirname(here);
const sourceRoot = join(here, '../../../../../../');
const sourcePublicContent = join(sourceRoot, 'docs/i18n/tes-public.content.json');
const sourceAgentManual = join(sourceRoot, 'docs/install/AGENT-MANUAL.md');
const sourceCursorRuntimeRule = join(sourceRoot, 'src/adapters/cursor/rules/tes-runtime-capabilities.mdc');
const installedCursorRuntimeRule = join(skillRoot, '../../../.cursor/rules/tes-runtime-capabilities.mdc');
const GM12_SPEC2_PRE_EDIT_REF = 'pre_edit_gate.json';
const GM12_SPEC2_ANCHOR_HASH = '1f99741c919726b2d088e038078e7931ab9c2a70';
const GM12_SPEC3_PROMPT_REF = 'prompt_enrichment_packet.json';
const GM12_SPEC3_STRUCTURAL_METHOD = 'gm-p0-harness-platform';
const GM12_SPEC3_STOP_STATE = 'NEEDS_PROMPT_ENRICHMENT_PACKET';
const GM12_SPEC3_SOURCE_PROMPT = 'ACTIVE_SPEC=SPEC-003 execute only the Prompt Enrichment Packet slice; do not execute SPEC-004 or later.';
const GM12_SPEC4_DOCUMENT_REF = 'document_analysis_packet.json';
const GM12_SPEC4_STOP_STATE = 'NEEDS_DOCUMENT_ANALYSIS';
const GM12_SPEC5_CONTRACT = 'goal-maestro-p0-spec-fidelity';
const GM12_SPEC5_STOP_STATE = 'NEEDS_SPEC_FIDELITY';
const GM12_SPEC5_DECLARED_SPECS = ['SPEC-001', 'SPEC-002', 'SPEC-003'];
const GM12_SPEC5_REPAIR_UNIT = 'REPAIR-SPEC-002-HARNESS';
const GM12_SPEC6_CONTRACT = 'goal-maestro-p0-thermometer-fidelity';
const GM12_SPEC6_STOP_STATE = 'NEEDS_THERMOMETER_FIDELITY';
const GM12_SPEC6_DECLARED_SPECS = ['SPEC-001', 'SPEC-002', 'SPEC-003'];
const GM12_SPEC7_CONTRACT = 'goal-maestro-p0-ledger-grammar';
const GM12_SPEC7_STOP_STATE = 'NEEDS_LEDGER_GRAMMAR';
const GM12_SPEC7_DECLARED_SPECS = ['SPEC-001', 'SPEC-002', 'SPEC-003'];
const GM12_SPEC8_CONTRACT = 'goal-maestro-p0-report-coherence';
const GM12_SPEC8_STOP_STATE = 'NEEDS_REPORT_COHERENCE';
const GM12_SPEC8_DECLARED_SPECS = ['SPEC-001', 'SPEC-002', 'SPEC-003'];
const GM12_SPEC8_FINAL_STATUS = 'PASS_P0_HARNESS_ORCHESTRATION_FEEDBACK_FIDELITY';
const GM12_SPEC8_REPORT_STATUS = 'local_package_ready';
const GM12_SPEC8_SHARE_STATUS = 'not_requested';
const GM12_SPEC9_CONTRACT = 'goal-maestro-p0-package-hierarchy';
const GM12_SPEC9_STOP_STATE = 'NEEDS_THERMOMETER_PACKAGE_HIERARCHY';
const GM12_SPEC9_LATEST_PACKAGE = 'execution-thermometer-run-html-002';
const GM12_SPEC9_SUPERSEDED_PACKAGE = 'execution-thermometer-run-html-001';
const GM12_SPEC10_CONTRACT = 'goal-maestro-p0-report-identity';
const GM12_SPEC10_STOP_STATE = 'NEEDS_REPORT_IDENTITY';
const GM12_SPEC10_INSTALLED_VERSION = sourcePackageVersion();
const GM12_SPEC10_INSTALLED_AT = '2026-06-29T00:00:00Z';
const GM12_SPEC10_SOURCE_HASH = 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee';
const GM12_SPEC11_CONTRACT = 'goal-maestro-p0-visual-evidence-contract';
const GM12_SPEC11_STOP_STATE = 'NEEDS_VISUAL_EVIDENCE_CONTRACT';
const GM12_SPEC11_DOMAIN_OBJECTS = ['board', 'score', 'selected card'];
const GM12_SPEC12_CONTRACT = 'goal-maestro-p0-visual-semantic-gate';
const GM12_SPEC12_STOP_STATE = 'NEEDS_VISUAL_SEMANTIC_GATE';
const GM12_SPEC12_EXPECTED_OBJECTS = ['board', 'score', 'selected card'];
const GM12_SPEC12_SCORE_STATUS = ['score 12', 'active'];
const GM12_SPEC12_LAYOUT_AREAS = ['game board area', 'score panel'];
const GM12_SPEC12_INTERACTION_RESULTS = ['card selected'];
const GM12_SPEC13_CONTRACT = 'goal-maestro-p0-browser-metrics-schema';
const GM12_SPEC13_STOP_STATE = 'NEEDS_BROWSER_METRICS_SCHEMA';
const GM12_SPEC13_BROWSER_SOURCES = ['codex', 'claude', 'cursor'];
const GM12_SPEC14_CONTRACT = 'goal-maestro-p0-install-chronology';
const GM12_SPEC14_STOP_STATE = 'NEEDS_INSTALL_CHRONOLOGY';
const GM12_SPEC14_INSTALLED_AT = '2026-06-28T23:55:00Z';
const GM12_SPEC14_AFTER_MATERIAL_AT = '2026-06-29T00:30:00Z';
const GM12_SPEC15_CONTRACT = 'goal-maestro-p0-commit-enforcement-classification';
const GM12_SPEC15_STOP_STATE = 'NEEDS_COMMIT_ENFORCEMENT_CLASSIFICATION';
const GM12_SPEC16_CONTRACT = 'goal-maestro-p0-git-admission-gate';
const GM12_SPEC16_STOP_STATE = 'NEEDS_GIT_REPOSITORY';
const GM12_SPEC17_CONTRACT = 'goal-maestro-p0-evidence-tracking-classification';
const GM12_SPEC17_STOP_STATE = 'NEEDS_EVIDENCE_TRACKING_CLASSIFICATION';
const GM12_SPEC18_CONTRACT = 'goal-maestro-p0-flash-fry-operational-status';
const GM12_SPEC18_STOP_STATE = 'NEEDS_FLASH_FRY_STATUS';
const GM12_SPEC19_CONTRACT = 'goal-maestro-p0-lens-ledger';
const GM12_SPEC19_STOP_STATE = 'NEEDS_LENS_LEDGER';
const GM12_SPEC19_LENSES = ['document', 'product', 'architecture', 'runtime', 'visual', 'security', 'performance', 'evidence', 'adversarial', 'cost', 'dx', 'delivery'];
const GM12_SPEC20_CONTRACT = 'goal-maestro-p0-cloud-search-classification';
const GM12_SPEC20_STOP_STATE = 'NEEDS_CLOUD_SEARCH_CLASSIFICATION';
const GM12_SPEC21_CONTRACT = 'goal-maestro-p0-llm-cache-cost-telemetry';
const GM12_SPEC21_STOP_STATE = 'NEEDS_LLM_CACHE_COST_TELEMETRY';
const GM12_SPEC8_EVIDENCE_HASHES = [
  '1111111111111111111111111111111111111111111111111111111111111111',
  '2222222222222222222222222222222222222222222222222222222222222222',
  '3333333333333333333333333333333333333333333333333333333333333333',
];
const GM12_SPEC8_CHECKSUM_HASHES = {
  ledger: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
  metrics: 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
  receipt: 'cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc',
  html: 'dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd',
};
const GM12_SPEC2_ALLOWED_FILES = [
  'src/adapters/codex/skills/tes-goal-maestro/scripts/goal-maestro-p0-harness.mjs',
  'src/adapters/claude/skills/tes-goal-maestro/scripts/goal-maestro-p0-harness.mjs',
  'src/adapters/codex/skills/tes-goal-maestro/scripts/validate-walls.mjs',
  'src/adapters/claude/skills/tes-goal-maestro/scripts/validate-walls.mjs',
];
const GM12_SPEC2_FORBIDDEN_FILES = [
  'docs/**',
  'package.json',
  'docs/dist/**',
  '.agents/**',
  '.claude/**',
  'src/adapters/cursor/**',
];
const GM12_SPEC2_FORBIDDEN_ACTIONS = [
  'docs claims',
  'package version bump',
  'remote sync',
  'cloud share',
  'automation',
  'local mirror edit',
  'Cursor fake skill parity',
  'SPEC-003 execution',
];
const GM12_SPEC2_REQUIRED_GATES = [
  'direct positive fixture through goal-maestro-p0-harness.mjs',
  'direct negative missing-or-late fixture through goal-maestro-p0-harness.mjs',
  'node src/adapters/codex/skills/tes-goal-maestro/scripts/validate-walls.mjs',
  'git diff --check',
  'cmp Codex/Claude harness and validate-walls',
];

function runHarness(script, args) {
  try {
    execFileSync('node', [join(here, script), ...args], { stdio: 'pipe' });
    return 0;
  } catch (e) {
    return typeof e.status === 'number' ? e.status : 1;
  }
}

function fixture(name, content) {
  const p = join(tmp, name);
  writeFileSync(p, content);
  return p;
}

function outputRootWithUnownedPackage(name) {
  const root = join(tmp, name);
  const packageDir = join(root, 'execution-thermometer-run-html-001');
  mkdirSync(packageDir, { recursive: true });
  writeFileSync(join(packageDir, 'foreign.txt'), 'not owned by TES\n');
  return root;
}

function outputRootWithOwnedPackage(name) {
  const root = join(tmp, name);
  const packageDir = join(root, 'execution-thermometer-run-html-001');
  mkdirSync(packageDir, { recursive: true });
  writeFileSync(join(packageDir, '.tes-execution-thermometer-package.json'), JSON.stringify({
    schema_version: 1,
    owner: 'tes-goal-maestro-execution-thermometer',
    package_contract: 'execution-thermometer-package@1',
    run_id: 'run-html-001',
    package_name: 'execution-thermometer-run-html-001',
    files: ['README.md', 'context-receipt.md', 'exec_identity.yaml', 'exec_metrics.json', 'execution-thermometer.html', 'checksums.sha256'],
  }));
  writeFileSync(join(packageDir, 'stale.txt'), 'old generated content\n');
  return root;
}

function hasSourceDocs() {
  return existsSync(sourcePublicContent) && existsSync(sourceAgentManual);
}

function gm10ViolateArgs() {
  if (hasSourceDocs()) {
    return [
      fixture('gm10-bad-content.json', JSON.stringify({ sections: { report: { en: { blocks: [] }, es: { blocks: [] }, pt: { blocks: [] } } } })),
      fixture('gm10-bad-agent.md', 'Execution Thermometer without fields.\n'),
    ];
  }
  return ['--installed-skill-root', badInstalledThermometerSkillRoot('gm10-bad-installed-skill')];
}

function gm10RevertArgs() {
  if (hasSourceDocs()) {
    return [sourcePublicContent, sourceAgentManual];
  }
  return ['--installed-skill-root', skillRoot];
}

function gm12ViolateArgs() {
  return [fixture('gm12-linear-pipeline-bad.json', JSON.stringify({
    schema_version: 1,
    declared_specs: ['SPEC-001', 'SPEC-002', 'SPEC-003'],
    events: [
      { type: 'open_spec', spec_id: 'SPEC-001', at: '2026-06-29T00:00:00Z' },
      { type: 'implement', spec_id: 'SPEC-001', at: '2026-06-29T00:00:01Z' },
      { type: 'evidence', spec_id: 'SPEC-002', evidence_ref: 'EV-PREOPEN', at: '2026-06-29T00:00:02Z' },
      { type: 'implement', spec_id: 'SPEC-002', at: '2026-06-29T00:00:03Z' },
      { type: 'open_spec', spec_id: 'SPEC-002', at: '2026-06-29T00:00:04Z' },
    ],
  }))];
}

function gm12RevertArgs() {
  return [fixture('gm12-linear-pipeline-ok.json', JSON.stringify(gm12ValidFixture()))];
}

function gm12Spec2MissingPreEditArgs() {
  return [fixture('gm12-spec2-pre-edit-missing.json', JSON.stringify(gm12Spec2Fixture('missing')))];
}

function gm12Spec2LatePreEditArgs() {
  return [fixture('gm12-spec2-pre-edit-late.json', JSON.stringify(gm12Spec2Fixture('late')))];
}

function gm12Spec2RevertArgs() {
  return [fixture('gm12-spec2-pre-edit-ok.json', JSON.stringify(gm12Spec2Fixture('valid')))];
}

function gm12Spec3MissingPromptArgs() {
  return [fixture('gm12-spec3-prompt-enrichment-missing.json', JSON.stringify(gm12Spec3Fixture('missing')))];
}

function gm12Spec3EchoPromptArgs() {
  return [fixture('gm12-spec3-prompt-enrichment-echo.json', JSON.stringify(gm12Spec3Fixture('echo')))];
}

function gm12Spec3RevertArgs() {
  return [fixture('gm12-spec3-prompt-enrichment-ok.json', JSON.stringify(gm12Spec3Fixture('valid')))];
}

function gm12Spec4MissingDocumentAnalysisArgs() {
  return [fixture('gm12-spec4-document-analysis-missing.json', JSON.stringify(gm12Spec4Fixture('missing')))];
}

function gm12Spec4MissingAcceptanceCriteriaArgs() {
  return [fixture('gm12-spec4-document-analysis-missing-acceptance.json', JSON.stringify(gm12Spec4Fixture('missing_acceptance_criteria')))];
}

function gm12Spec4RevertArgs() {
  return [fixture('gm12-spec4-document-analysis-ok.json', JSON.stringify(gm12Spec4Fixture('valid')))];
}

function gm12Spec5MissingExecutionArgs() {
  return [fixture('gm12-spec5-spec-fidelity-missing-execution.json', JSON.stringify(gm12Spec5Fixture('missing_execution')))];
}

function gm12Spec5ReportedDriftArgs() {
  return [fixture('gm12-spec5-spec-fidelity-reported-drift.json', JSON.stringify(gm12Spec5Fixture('reported_drift')))];
}

function gm12Spec5AuditMaterialArgs() {
  return [fixture('gm12-spec5-spec-fidelity-audit-material.json', JSON.stringify(gm12Spec5Fixture('audit_material')))];
}

function gm12Spec5MergedExecutionArgs() {
  return [fixture('gm12-spec5-spec-fidelity-merged-execution.json', JSON.stringify(gm12Spec5Fixture('merged_execution')))];
}

function gm12Spec5UnacceptedRepairArgs() {
  return [fixture('gm12-spec5-spec-fidelity-unaccepted-repair.json', JSON.stringify(gm12Spec5Fixture('unaccepted_repair')))];
}

function gm12Spec5RevertArgs() {
  return [fixture('gm12-spec5-spec-fidelity-ok.json', JSON.stringify(gm12Spec5Fixture('valid')))];
}

function gm12Spec5AcceptedRepairArgs() {
  return [fixture('gm12-spec5-spec-fidelity-accepted-repair.json', JSON.stringify(gm12Spec5Fixture('accepted_repair')))];
}

function gm12Spec6UnknownSpecArgs() {
  return [fixture('gm12-spec6-thermometer-fidelity-unknown-spec.json', JSON.stringify(gm12Spec6Fixture('unknown_spec')))];
}

function gm12Spec6MissingMaterialArgs() {
  return [fixture('gm12-spec6-thermometer-fidelity-missing-material.json', JSON.stringify(gm12Spec6Fixture('missing_material')))];
}

function gm12Spec6AuditMaterialArgs() {
  return [fixture('gm12-spec6-thermometer-fidelity-audit-material.json', JSON.stringify(gm12Spec6Fixture('audit_material')))];
}

function gm12Spec6UnprovenMetricsArgs() {
  return [fixture('gm12-spec6-thermometer-fidelity-unproven-metrics.json', JSON.stringify(gm12Spec6Fixture('unproven_metrics')))];
}

function gm12Spec6RevertArgs() {
  return [fixture('gm12-spec6-thermometer-fidelity-ok.json', JSON.stringify(gm12Spec6Fixture('valid')))];
}

function gm12Spec7MalformedHeadingArgs() {
  return [fixture('gm12-spec7-ledger-grammar-malformed-heading.json', JSON.stringify(gm12Spec7Fixture('malformed_heading')))];
}

function gm12Spec7DuplicateSpecIdArgs() {
  return [fixture('gm12-spec7-ledger-grammar-duplicate-spec-id.json', JSON.stringify(gm12Spec7Fixture('duplicate_spec_id')))];
}

function gm12Spec7AuditOverwriteArgs() {
  return [fixture('gm12-spec7-ledger-grammar-audit-overwrite.json', JSON.stringify(gm12Spec7Fixture('audit_overwrite')))];
}

function gm12Spec7NestedCloseoutArgs() {
  return [fixture('gm12-spec7-ledger-grammar-nested-closeout.json', JSON.stringify(gm12Spec7Fixture('nested_closeout')))];
}

function gm12Spec7RevertArgs() {
  return [fixture('gm12-spec7-ledger-grammar-ok.json', JSON.stringify(gm12Spec7Fixture('valid')))];
}

function gm12Spec8SpecIdDriftArgs() {
  return [fixture('gm12-spec8-report-coherence-spec-id-drift.json', JSON.stringify(gm12Spec8Fixture('spec_id_drift')))];
}

function gm12Spec8StatusDriftArgs() {
  return [fixture('gm12-spec8-report-coherence-status-drift.json', JSON.stringify(gm12Spec8Fixture('status_drift')))];
}

function gm12Spec8EvidenceHashDriftArgs() {
  return [fixture('gm12-spec8-report-coherence-evidence-hash-drift.json', JSON.stringify(gm12Spec8Fixture('evidence_hash_drift')))];
}

function gm12Spec8UnprovenCloseoutArgs() {
  return [fixture('gm12-spec8-report-coherence-unproven-closeout.json', JSON.stringify(gm12Spec8Fixture('unproven_closeout_pass')))];
}

function gm12Spec8ChecksumMismatchArgs() {
  return [fixture('gm12-spec8-report-coherence-checksum-mismatch.json', JSON.stringify(gm12Spec8Fixture('checksum_mismatch')))];
}

function gm12Spec8RevertArgs() {
  return [fixture('gm12-spec8-report-coherence-ok.json', JSON.stringify(gm12Spec8Fixture('valid')))];
}

function gm12Spec9UnsortedCandidatesArgs() {
  return [fixture('gm12-spec9-package-hierarchy-unsorted-candidates.json', JSON.stringify(gm12Spec9Fixture('unsorted_candidates')))];
}

function gm12Spec9MissingSupersededByArgs() {
  return [fixture('gm12-spec9-package-hierarchy-missing-superseded-by.json', JSON.stringify(gm12Spec9Fixture('missing_superseded_by')))];
}

function gm12Spec9CloseoutHistoryLeakArgs() {
  return [fixture('gm12-spec9-package-hierarchy-closeout-history-leak.json', JSON.stringify(gm12Spec9Fixture('closeout_history_leak')))];
}

function gm12Spec9ExplicitHistoryArgs() {
  return [fixture('gm12-spec9-package-hierarchy-explicit-history.json', JSON.stringify(gm12Spec9Fixture('explicit_history')))];
}

function gm12Spec9RevertArgs() {
  return [fixture('gm12-spec9-package-hierarchy-ok.json', JSON.stringify(gm12Spec9Fixture('valid')))];
}

function gm12Spec10VersionMismatchArgs() {
  return [fixture('gm12-spec10-report-identity-version-mismatch.json', JSON.stringify(gm12Spec10Fixture('version_mismatch')))];
}

function gm12Spec10KnownAdapterOtherArgs() {
  return [fixture('gm12-spec10-report-identity-known-adapter-other.json', JSON.stringify(gm12Spec10Fixture('known_adapter_other')))];
}

function gm12Spec10MissingInstalledAtArgs() {
  return [fixture('gm12-spec10-report-identity-missing-installed-at.json', JSON.stringify(gm12Spec10Fixture('missing_installed_at')))];
}

function gm12Spec10MissingModelReasonArgs() {
  return [fixture('gm12-spec10-report-identity-missing-model-reason.json', JSON.stringify(gm12Spec10Fixture('missing_model_reason')))];
}

function gm12Spec10MissingSourceIdentityArgs() {
  return [fixture('gm12-spec10-report-identity-missing-source-identity.json', JSON.stringify(gm12Spec10Fixture('missing_source_identity')))];
}

function gm12Spec10RevertArgs() {
  return [fixture('gm12-spec10-report-identity-ok.json', JSON.stringify(gm12Spec10Fixture('valid')))];
}

function gm12Spec11UnsupportedArtifactClassArgs() {
  return [fixture('gm12-spec11-visual-evidence-unsupported-artifact-class.json', JSON.stringify(gm12Spec11Fixture('unsupported_artifact_class')))];
}

function gm12Spec11InitialOnlyArgs() {
  return [fixture('gm12-spec11-visual-evidence-initial-only.json', JSON.stringify(gm12Spec11Fixture('initial_only')))];
}

function gm12Spec11TerminalOnlyArgs() {
  return [fixture('gm12-spec11-visual-evidence-terminal-only.json', JSON.stringify(gm12Spec11Fixture('terminal_only')))];
}

function gm12Spec11UnmappedScreenshotArgs() {
  return [fixture('gm12-spec11-visual-evidence-unmapped-screenshot.json', JSON.stringify(gm12Spec11Fixture('unmapped_screenshot')))];
}

function gm12Spec11ActiveWithoutDomainObjectsArgs() {
  return [fixture('gm12-spec11-visual-evidence-active-without-domain-objects.json', JSON.stringify(gm12Spec11Fixture('active_without_domain_objects')))];
}

function gm12Spec11MissingResponsiveArgs() {
  return [fixture('gm12-spec11-visual-evidence-missing-responsive.json', JSON.stringify(gm12Spec11Fixture('missing_responsive')))];
}

function gm12Spec11RevertArgs() {
  return [fixture('gm12-spec11-visual-evidence-ok.json', JSON.stringify(gm12Spec11Fixture('valid')))];
}

function gm12Spec12MissingPixelFloorArgs() {
  return [fixture('gm12-spec12-visual-semantic-missing-pixel-floor.json', JSON.stringify(gm12Spec12Fixture('missing_pixel_floor')))];
}

function gm12Spec12MissingStateMetadataArgs() {
  return [fixture('gm12-spec12-visual-semantic-missing-state-metadata.json', JSON.stringify(gm12Spec12Fixture('missing_state_metadata')))];
}

function gm12Spec12MissingObjectsArgs() {
  return [fixture('gm12-spec12-visual-semantic-missing-objects.json', JSON.stringify(gm12Spec12Fixture('missing_objects')))];
}

function gm12Spec12MissingScoreStatusArgs() {
  return [fixture('gm12-spec12-visual-semantic-missing-score-status.json', JSON.stringify(gm12Spec12Fixture('missing_score_status')))];
}

function gm12Spec12MissingLayoutAreaArgs() {
  return [fixture('gm12-spec12-visual-semantic-missing-layout-area.json', JSON.stringify(gm12Spec12Fixture('missing_layout_area')))];
}

function gm12Spec12MissingInteractionResultArgs() {
  return [fixture('gm12-spec12-visual-semantic-missing-interaction-result.json', JSON.stringify(gm12Spec12Fixture('missing_interaction_result')))];
}

function gm12Spec12RevertArgs() {
  return [fixture('gm12-spec12-visual-semantic-ok.json', JSON.stringify(gm12Spec12Fixture('valid')))];
}

function gm12Spec13HostMinimalArgs() {
  return [fixture('gm12-spec13-browser-metrics-host-minimal.json', JSON.stringify(gm12Spec13Fixture('host_minimal')))];
}

function gm12Spec13MissingStatusArgs() {
  return [fixture('gm12-spec13-browser-metrics-missing-status.json', JSON.stringify(gm12Spec13Fixture('missing_status')))];
}

function gm12Spec13MissingSourceCoverageArgs() {
  return [fixture('gm12-spec13-browser-metrics-missing-source-coverage.json', JSON.stringify(gm12Spec13Fixture('missing_source_coverage')))];
}

function gm12Spec13MissingStateTransitionsArgs() {
  return [fixture('gm12-spec13-browser-metrics-missing-state-transitions.json', JSON.stringify(gm12Spec13Fixture('missing_state_transitions')))];
}

function gm12Spec13MissingRestartEvidenceArgs() {
  return [fixture('gm12-spec13-browser-metrics-missing-restart-evidence.json', JSON.stringify(gm12Spec13Fixture('missing_restart_evidence')))];
}

function gm12Spec13MissingDomainMetricsArgs() {
  return [fixture('gm12-spec13-browser-metrics-missing-domain-metrics.json', JSON.stringify(gm12Spec13Fixture('missing_domain_metrics')))];
}

function gm12Spec13RevertArgs() {
  return [fixture('gm12-spec13-browser-metrics-ok.json', JSON.stringify(gm12Spec13Fixture('valid')))];
}

function gm12Spec14InstallAfterMaterialArgs() {
  return [fixture('gm12-spec14-install-chronology-after-material.json', JSON.stringify(gm12Spec14Fixture('install_after_material')))];
}

function gm12Spec14MissingInstalledVersionArgs() {
  return [fixture('gm12-spec14-install-chronology-missing-installed-version.json', JSON.stringify(gm12Spec14Fixture('missing_installed_version')))];
}

function gm12Spec14MissingGitHeadArgs() {
  return [fixture('gm12-spec14-install-chronology-missing-git-head.json', JSON.stringify(gm12Spec14Fixture('missing_git_head')))];
}

function gm12Spec14MissingBaselineCommitArgs() {
  return [fixture('gm12-spec14-install-chronology-missing-baseline-commit.json', JSON.stringify(gm12Spec14Fixture('missing_baseline_commit')))];
}

function gm12Spec14MissingMaterialTimestampsArgs() {
  return [fixture('gm12-spec14-install-chronology-missing-material-timestamps.json', JSON.stringify(gm12Spec14Fixture('missing_material_timestamps')))];
}

function gm12Spec14ClassifiedLaterReinstallArgs() {
  return [fixture('gm12-spec14-install-chronology-classified-later-reinstall.json', JSON.stringify(gm12Spec14Fixture('classified_later_reinstall')))];
}

function gm12Spec14RevertArgs() {
  return [fixture('gm12-spec14-install-chronology-ok.json', JSON.stringify(gm12Spec14Fixture('valid')))];
}

function gm12Spec15MissingPrecommitEvidenceArgs() {
  return [fixture('gm12-spec15-commit-enforcement-missing-precommit-evidence.json', JSON.stringify(gm12Spec15Fixture('missing_precommit_evidence')))];
}

function gm12Spec15ManualClaimsEnforcedArgs() {
  return [fixture('gm12-spec15-commit-enforcement-manual-claims-enforced.json', JSON.stringify(gm12Spec15Fixture('manual_claims_enforced')))];
}

function gm12Spec15MissingCommitModeArgs() {
  return [fixture('gm12-spec15-commit-enforcement-missing-commit-mode.json', JSON.stringify(gm12Spec15Fixture('missing_commit_mode')))];
}

function gm12Spec15HonestManualArgs() {
  return [fixture('gm12-spec15-commit-enforcement-honest-manual.json', JSON.stringify(gm12Spec15Fixture('honest_manual')))];
}

function gm12Spec15PrecommitEnforcedArgs() {
  return [fixture('gm12-spec15-commit-enforcement-precommit-enforced.json', JSON.stringify(gm12Spec15Fixture('precommit_enforced')))];
}

function gm12Spec15RevertArgs() {
  return [fixture('gm12-spec15-commit-enforcement-ok.json', JSON.stringify(gm12Spec15Fixture('valid')))];
}

function gm12Spec16MissingRepoNoStopArgs() {
  return [fixture('gm12-spec16-git-admission-missing-repo-no-stop.json', JSON.stringify(gm12Spec16Fixture('missing_repo_no_stop')))];
}

function gm12Spec16SilentGitInitArgs() {
  return [fixture('gm12-spec16-git-admission-silent-init.json', JSON.stringify(gm12Spec16Fixture('silent_git_init')))];
}

function gm12Spec16MissingBaselineClassificationArgs() {
  return [fixture('gm12-spec16-git-admission-missing-baseline-classification.json', JSON.stringify(gm12Spec16Fixture('missing_baseline_classification')))];
}

function gm12Spec16NeedsGitRepositoryArgs() {
  return [fixture('gm12-spec16-git-admission-needs-git-repository.json', JSON.stringify(gm12Spec16Fixture('needs_git_repository')))];
}

function gm12Spec16AuthorizedGitInitArgs() {
  return [fixture('gm12-spec16-git-admission-authorized-init.json', JSON.stringify(gm12Spec16Fixture('authorized_git_init')))];
}

function gm12Spec16RevertArgs() {
  return [fixture('gm12-spec16-git-admission-ok.json', JSON.stringify(gm12Spec16Fixture('valid')))];
}

function gm12Spec17MissingClassArgs() {
  return [fixture('gm12-spec17-evidence-tracking-missing-class.json', JSON.stringify(gm12Spec17Fixture('missing_screenshot_classification')))];
}

function gm12Spec17UntrackedUnclassifiedArgs() {
  return [fixture('gm12-spec17-evidence-tracking-untracked-unclassified.json', JSON.stringify(gm12Spec17Fixture('untracked_unclassified')))];
}

function gm12Spec17CleanClaimUnclassifiedArgs() {
  return [fixture('gm12-spec17-evidence-tracking-clean-claim-unclassified.json', JSON.stringify(gm12Spec17Fixture('clean_claim_unclassified')))];
}

function gm12Spec17RuntimeOnlyArgs() {
  return [fixture('gm12-spec17-evidence-tracking-runtime-only.json', JSON.stringify(gm12Spec17Fixture('runtime_only_classified')))];
}

function gm12Spec17RevertArgs() {
  return [fixture('gm12-spec17-evidence-tracking-ok.json', JSON.stringify(gm12Spec17Fixture('valid')))];
}

function gm12Spec18MissingStatusArgs() {
  return [fixture('gm12-spec18-flash-fry-missing-status.json', JSON.stringify(gm12Spec18Fixture('missing_status')))];
}

function gm12Spec18RanMissingEvidenceArgs() {
  return [fixture('gm12-spec18-flash-fry-ran-missing-evidence.json', JSON.stringify(gm12Spec18Fixture('ran_missing_evidence')))];
}

function gm12Spec18NotConfiguredNoAdjustmentArgs() {
  return [fixture('gm12-spec18-flash-fry-not-configured-no-adjustment.json', JSON.stringify(gm12Spec18Fixture('not_configured_no_adjustment')))];
}

function gm12Spec18NewCommandArgs() {
  return [fixture('gm12-spec18-flash-fry-new-command.json', JSON.stringify(gm12Spec18Fixture('new_command')))];
}

function gm12Spec18NotConfiguredAdjustedArgs() {
  return [fixture('gm12-spec18-flash-fry-not-configured-adjusted.json', JSON.stringify(gm12Spec18Fixture('not_configured_adjusted')))];
}

function gm12Spec18RevertArgs() {
  return [fixture('gm12-spec18-flash-fry-ok.json', JSON.stringify(gm12Spec18Fixture('valid')))];
}

function gm12Spec19MissingLedgerArgs() {
  return [fixture('gm12-spec19-lens-ledger-missing.json', JSON.stringify(gm12Spec19Fixture('missing_ledger')))];
}

function gm12Spec19MissingLensArgs() {
  return [fixture('gm12-spec19-lens-ledger-missing-lens.json', JSON.stringify(gm12Spec19Fixture('missing_lens')))];
}

function gm12Spec19MissingImpactArgs() {
  return [fixture('gm12-spec19-lens-ledger-missing-impact.json', JSON.stringify(gm12Spec19Fixture('missing_impact')))];
}

function gm12Spec19ScoreWithoutEvidenceArgs() {
  return [fixture('gm12-spec19-lens-ledger-score-without-evidence.json', JSON.stringify(gm12Spec19Fixture('score_without_evidence')))];
}

function gm12Spec19ScoreWithEvidenceArgs() {
  return [fixture('gm12-spec19-lens-ledger-score-with-evidence.json', JSON.stringify(gm12Spec19Fixture('score_with_evidence')))];
}

function gm12Spec19RevertArgs() {
  return [fixture('gm12-spec19-lens-ledger-ok.json', JSON.stringify(gm12Spec19Fixture('valid')))];
}

function gm12Spec20MissingStatusArgs() {
  return [fixture('gm12-spec20-cloud-search-missing-status.json', JSON.stringify(gm12Spec20Fixture('missing_status')))];
}

function gm12Spec20MissingReasonArgs() {
  return [fixture('gm12-spec20-cloud-search-missing-reason.json', JSON.stringify(gm12Spec20Fixture('missing_reason')))];
}

function gm12Spec20UnauthorizedRunArgs() {
  return [fixture('gm12-spec20-cloud-search-unauthorized-run.json', JSON.stringify(gm12Spec20Fixture('unauthorized_run')))];
}

function gm12Spec20MissingRedactionArgs() {
  return [fixture('gm12-spec20-cloud-search-missing-redaction.json', JSON.stringify(gm12Spec20Fixture('missing_redaction')))];
}

function gm12Spec20RanAuthorizedArgs() {
  return [fixture('gm12-spec20-cloud-search-ran-authorized.json', JSON.stringify(gm12Spec20Fixture('ran_authorized')))];
}

function gm12Spec20RevertArgs() {
  return [fixture('gm12-spec20-cloud-search-ok.json', JSON.stringify(gm12Spec20Fixture('valid')))];
}

function gm12Spec21MissingTelemetryArgs() {
  return [fixture('gm12-spec21-llm-cache-cost-missing-telemetry.json', JSON.stringify(gm12Spec21Fixture('missing_telemetry')))];
}

function gm12Spec21MissingFieldArgs() {
  return [fixture('gm12-spec21-llm-cache-cost-missing-field.json', JSON.stringify(gm12Spec21Fixture('missing_field')))];
}

function gm12Spec21ZeroedMissingFieldArgs() {
  return [fixture('gm12-spec21-llm-cache-cost-zeroed-missing-field.json', JSON.stringify(gm12Spec21Fixture('zeroed_missing_field')))];
}

function gm12Spec21UnqualifiedEfficiencyArgs() {
  return [fixture('gm12-spec21-llm-cache-cost-unqualified-efficiency.json', JSON.stringify(gm12Spec21Fixture('unqualified_efficiency')))];
}

function gm12Spec21UnprovenQualifiedArgs() {
  return [fixture('gm12-spec21-llm-cache-cost-unproven-qualified.json', JSON.stringify(gm12Spec21Fixture('unproven_qualified')))];
}

function gm12Spec21RevertArgs() {
  return [fixture('gm12-spec21-llm-cache-cost-ok.json', JSON.stringify(gm12Spec21Fixture('valid')))];
}

function gm12ValidFixture() {
  const declared_specs = ['SPEC-001', 'SPEC-002', 'SPEC-003'];
  const events = [];
  let second = 0;
  for (const spec_id of declared_specs) {
    events.push(
      { type: 'open_spec', spec_id, at: gm12Time(second++) },
      { type: 'implement', spec_id, at: gm12Time(second++) },
      { type: 'evidence', spec_id, evidence_ref: `EV-${spec_id}`, at: gm12Time(second++) },
      { type: 'oracle_result', spec_id, status: 'pass', at: gm12Time(second++) },
      { type: 'local_commit_status', spec_id, status: 'LOCAL_COMMITTED', at: gm12Time(second++) },
      { type: 'parent_validation', spec_id, status: 'pass', at: gm12Time(second++) },
    );
  }
  return { schema_version: 1, declared_specs, events };
}

function gm12Spec2Fixture(mode) {
  const spec_id = 'SPEC-002';
  const events = [];
  let second = 0;
  if (mode === 'valid') {
    events.push(gm12Spec2PreEditEvent(spec_id, gm12Time(second++)));
  }
  events.push(
    { type: 'open_spec', spec_id, at: gm12Time(second++) },
    { type: 'implement', spec_id, at: gm12Time(second++) },
  );
  if (mode === 'late') {
    events.push(gm12Spec2PreEditEvent(spec_id, gm12Time(second++)));
  }
  events.push(
    { type: 'evidence', spec_id, evidence_ref: 'EV-SPEC-002-PRE-EDIT-GATE', at: gm12Time(second++) },
    { type: 'oracle_result', spec_id, status: 'pass', at: gm12Time(second++) },
    { type: 'local_commit_status', spec_id, status: 'LOCAL_COMMITTED', at: gm12Time(second++) },
    { type: 'parent_validation', spec_id, status: 'pass', at: gm12Time(second++) },
  );

  return {
    schema_version: 1,
    harness_contract: 'goal-maestro-p0-pre-edit-gate',
    pre_edit_gate_required: true,
    active_spec: spec_id,
    first_unexecuted_spec: spec_id,
    anchor_hash: GM12_SPEC2_ANCHOR_HASH,
    allowed_files: GM12_SPEC2_ALLOWED_FILES,
    forbidden_files: GM12_SPEC2_FORBIDDEN_FILES,
    forbidden_actions: GM12_SPEC2_FORBIDDEN_ACTIONS,
    required_gates: GM12_SPEC2_REQUIRED_GATES,
    commit_mode: 'no-commit',
    pre_edit_gate_expectations: {
      active_spec: spec_id,
      first_unexecuted_spec: spec_id,
      anchor_hash: GM12_SPEC2_ANCHOR_HASH,
      allowed_files: GM12_SPEC2_ALLOWED_FILES,
      forbidden_files: GM12_SPEC2_FORBIDDEN_FILES,
      forbidden_actions: GM12_SPEC2_FORBIDDEN_ACTIONS,
      required_gates: GM12_SPEC2_REQUIRED_GATES,
      commit_mode: 'no-commit',
    },
    ledger: {
      pre_edit_gate_ref: GM12_SPEC2_PRE_EDIT_REF,
      active_spec: spec_id,
    },
    thermometer_metrics: {
      sources: [{ ref: GM12_SPEC2_PRE_EDIT_REF, type: 'pre_edit_gate' }],
      pre_edit_gate_ref: GM12_SPEC2_PRE_EDIT_REF,
    },
    closeout: {
      evidence_refs: [GM12_SPEC2_PRE_EDIT_REF],
      status: 'pass',
    },
    declared_specs: [spec_id],
    events,
  };
}

function gm12Spec3Fixture(mode) {
  const spec_id = 'SPEC-003';
  const events = [];
  let second = 0;
  if (mode === 'valid' || mode === 'echo') {
    events.push(gm12Spec3PromptEvent(spec_id, gm12Time(second++), mode));
  }
  events.push(
    { type: 'open_spec', spec_id, at: gm12Time(second++) },
    { type: 'implement', spec_id, at: gm12Time(second++) },
    { type: 'evidence', spec_id, evidence_ref: 'EV-SPEC-003-PROMPT-ENRICHMENT-PACKET', at: gm12Time(second++) },
    { type: 'oracle_result', spec_id, status: 'pass', at: gm12Time(second++) },
    { type: 'local_commit_status', spec_id, status: 'LOCAL_COMMITTED', at: gm12Time(second++) },
    { type: 'parent_validation', spec_id, status: 'pass', at: gm12Time(second++) },
  );

  return {
    schema_version: 1,
    harness_contract: 'goal-maestro-p0-prompt-enrichment-packet',
    prompt_enrichment_packet_required: true,
    source_prompt: GM12_SPEC3_SOURCE_PROMPT,
    structural_method: GM12_SPEC3_STRUCTURAL_METHOD,
    prompt_enrichment_expectations: {
      spec_queue: [spec_id],
      structural_method: GM12_SPEC3_STRUCTURAL_METHOD,
      stop_states: [GM12_SPEC3_STOP_STATE],
      source_prompt: GM12_SPEC3_SOURCE_PROMPT,
    },
    declared_specs: [spec_id],
    events,
  };
}

function gm12Spec4Fixture(mode) {
  const spec_id = 'SPEC-004';
  const events = [];
  let second = 0;
  if (mode === 'valid' || mode === 'missing_acceptance_criteria') {
    events.push(gm12Spec4DocumentAnalysisEvent(spec_id, gm12Time(second++), mode));
  }
  events.push(
    { type: 'open_spec', spec_id, at: gm12Time(second++) },
    { type: 'implement', spec_id, at: gm12Time(second++) },
    { type: 'evidence', spec_id, evidence_ref: 'EV-SPEC-004-DOCUMENT-ANALYSIS-PACKET', at: gm12Time(second++) },
    { type: 'oracle_result', spec_id, status: 'pass', at: gm12Time(second++) },
    { type: 'local_commit_status', spec_id, status: 'LOCAL_COMMITTED', at: gm12Time(second++) },
    { type: 'parent_validation', spec_id, status: 'pass', at: gm12Time(second++) },
  );

  return {
    schema_version: 1,
    harness_contract: 'goal-maestro-p0-document-analysis-packet',
    document_analysis_packet_required: true,
    document_analysis_expectations: {
      external_documentation_required: false,
      cloud_search_required: false,
    },
    declared_specs: [spec_id],
    events,
  };
}

function gm12Spec5Fixture(mode) {
  const declared_specs = GM12_SPEC5_DECLARED_SPECS;
  const events = [];
  let second = 0;
  for (const spec_id of declared_specs) {
    events.push({ type: 'open_spec', spec_id, at: gm12Time(second++) });
    if (!(mode === 'missing_execution' && spec_id === 'SPEC-003')) {
      const implementEvent = { type: 'implement', spec_id, at: gm12Time(second++) };
      if (mode === 'merged_execution' && spec_id === 'SPEC-002') {
        implementEvent.merged_spec_ids = ['SPEC-003'];
      }
      events.push(implementEvent);
    }
    events.push(
      { type: 'evidence', spec_id, evidence_ref: `EV-${spec_id}-SPEC-FIDELITY`, at: gm12Time(second++) },
      { type: 'oracle_result', spec_id, status: 'pass', at: gm12Time(second++) },
      { type: 'local_commit_status', spec_id, status: 'LOCAL_COMMITTED', at: gm12Time(second++) },
      { type: 'parent_validation', spec_id, status: 'pass', at: gm12Time(second++) },
    );
  }

  const reported_specs = mode === 'reported_drift'
    ? ['SPEC-001', 'SPEC-003', 'SPEC-002', 'SPEC-004']
    : mode === 'audit_material'
      ? [...declared_specs, 'EXECUTIVE-STOP-AUDIT']
      : (mode === 'accepted_repair' || mode === 'unaccepted_repair')
        ? [...declared_specs, GM12_SPEC5_REPAIR_UNIT]
        : declared_specs;
  const fixture = {
    schema_version: 1,
    harness_contract: GM12_SPEC5_CONTRACT,
    spec_fidelity_required: true,
    spec_fidelity_expectations: {
      stop_state: GM12_SPEC5_STOP_STATE,
      declared_specs,
    },
    declared_specs,
    reported_specs,
    events,
  };
  if (mode === 'accepted_repair') {
    fixture.accepted_bounded_repair_units = [GM12_SPEC5_REPAIR_UNIT];
  }
  return fixture;
}

function gm12Spec6Fixture(mode) {
  const declared_specs = GM12_SPEC6_DECLARED_SPECS;
  const events = [];
  let second = 0;
  for (const spec_id of declared_specs) {
    events.push(
      { type: 'open_spec', spec_id, at: gm12Time(second++) },
      { type: 'implement', spec_id, at: gm12Time(second++) },
      { type: 'evidence', spec_id, evidence_ref: `EV-${spec_id}-THERMOMETER-FIDELITY`, at: gm12Time(second++) },
      { type: 'oracle_result', spec_id, status: 'pass', at: gm12Time(second++) },
      { type: 'local_commit_status', spec_id, status: 'LOCAL_COMMITTED', at: gm12Time(second++) },
      { type: 'parent_validation', spec_id, status: 'pass', at: gm12Time(second++) },
    );
  }

  const spec_results = declared_specs.map((spec_id) => ({
    spec_id,
    title: `${spec_id} material execution unit`,
    status: 'pass',
    evidence_refs: [`EV-${spec_id}-THERMOMETER-FIDELITY`],
    unproven_metrics: [],
  }));
  if (mode === 'unknown_spec') {
    spec_results[2] = {
      spec_id: 'SPEC-UNKNOWN',
      title: 'Unsectioned ledger evidence from installed canary report',
      status: 'pass',
      evidence_refs: ['EV-SPEC-UNKNOWN-CANARY'],
      unproven_metrics: [],
    };
  }
  if (mode === 'missing_material') {
    spec_results.pop();
  }
  if (mode === 'audit_material') {
    spec_results.push({
      spec_id: 'EXECUTIVE-STOP-AUDIT',
      title: 'Executive Stop Audit row from installed canary report',
      status: 'pass',
      evidence_refs: ['EV-AUDIT-CANARY'],
      unproven_metrics: [],
    });
  }
  const specIds = spec_results.map((result) => result.spec_id);
  const unproven_metrics = mode === 'unproven_metrics'
    ? [{ name: 'thermometer.spec_results', field: 'thermometer.spec_results', status: 'unproven', evidence_refs: [] }]
    : [];

  return {
    schema_version: 1,
    harness_contract: GM12_SPEC6_CONTRACT,
    thermometer_fidelity_required: true,
    thermometer_fidelity_expectations: {
      stop_state: GM12_SPEC6_STOP_STATE,
      declared_specs,
      required_execution_fidelity_fields: [
        'thermometer.spec_results',
        'thermometer.loops.spec_ids',
        'thermometer.final_status.goal_maestro_execution_state',
      ],
    },
    declared_specs,
    thermometer_metrics: {
      spec_results,
      loops: [{ loop_id: 'L1', spec_ids: specIds, status: 'on_track' }],
      latest_loop: { loop_id: 'L1', spec_ids: specIds, status: 'on_track' },
      final_status: {
        goal_maestro_execution_state: 'PASS_P0_HARNESS_ORCHESTRATION_FEEDBACK_FIDELITY',
        thermometer_report_status: 'local_package_ready',
        share_gate_status: 'not_requested',
        notes: 'SPEC-006 fixture exercises thermometer execution fidelity.',
      },
      unproven_metrics,
    },
    closeout: {
      status: 'complete',
      reported_specs: specIds,
    },
    events,
  };
}

function gm12Spec7Fixture(mode) {
  const base = gm12Spec6Fixture('valid');
  return {
    ...base,
    harness_contract: GM12_SPEC7_CONTRACT,
    ledger_grammar_required: true,
    thermometer_fidelity_required: true,
    ledger_grammar_expectations: {
      stop_state: GM12_SPEC7_STOP_STATE,
      declared_specs: GM12_SPEC7_DECLARED_SPECS,
    },
    declared_specs: GM12_SPEC7_DECLARED_SPECS,
    ledger_text: gm12Spec7LedgerText(mode),
  };
}

function gm12Spec7LedgerText(mode) {
  const spec3Heading = mode === 'malformed_heading'
    ? '### SPEC-003 Prompt Enrichment'
    : '### SPEC-003 - Prompt Enrichment';
  const spec3Lines = [
    spec3Heading,
    'spec_id: SPEC-003',
  ];
  if (mode === 'duplicate_spec_id') {
    spec3Lines.push('spec_id: SPEC-003');
  }
  spec3Lines.push(
    'oracle_status: PASS',
    'stop_state: ready_for_closeout',
  );
  if (mode === 'audit_overwrite') {
    spec3Lines.push(
      '',
      '#### Executive Stop Audit',
      'spec_id: EXECUTIVE-STOP-AUDIT',
      'audit_status: PASS',
    );
  } else if (mode === 'nested_closeout') {
    spec3Lines.push(
      '',
      '#### Closeout',
      'status: complete',
    );
  } else {
    spec3Lines.push(
      '',
      '### Executive Stop Audit',
      'spec_id: EXECUTIVE-STOP-AUDIT',
      'audit_status: PASS',
      '',
      '### Closeout',
      'status: complete',
      'reported_specs: SPEC-001,SPEC-002,SPEC-003',
    );
  }

  return [
    '# Synthetic Goal Maestro P0 Ledger',
    '',
    '## Ledger Entries',
    '',
    '### SPEC-001 - Linear Pipeline',
    'spec_id: SPEC-001',
    'oracle_status: PASS',
    'stop_state: ready_for_SPEC-002',
    '',
    '### SPEC-002 - Pre Edit Gate',
    'spec_id: SPEC-002',
    'oracle_status: PASS',
    'stop_state: ready_for_SPEC-003',
    '',
    ...spec3Lines,
    '',
  ].join('\n');
}

function gm12Spec8Fixture(mode) {
  const base = gm12Spec7Fixture('valid');
  const unproven_count = mode === 'unproven_closeout_pass' ? 1 : 0;
  const expected = {
    spec_ids: GM12_SPEC8_DECLARED_SPECS,
    final_status: GM12_SPEC8_FINAL_STATUS,
    report_status: GM12_SPEC8_REPORT_STATUS,
    share_status: GM12_SPEC8_SHARE_STATUS,
    evidence_hashes: GM12_SPEC8_EVIDENCE_HASHES,
    unproven_count,
  };
  const ledgerSnapshot = { ...expected };
  const metricsSnapshot = { ...expected };
  const receiptSnapshot = { ...expected };
  const htmlSnapshot = { ...expected };

  if (mode === 'spec_id_drift') {
    receiptSnapshot.spec_ids = ['SPEC-001', 'SPEC-002'];
  }
  if (mode === 'status_drift') {
    ledgerSnapshot.share_status = 'blocked_by_sanitization';
    receiptSnapshot.report_status = 'local_package_blocked';
    htmlSnapshot.final_status = GM12_SPEC8_STOP_STATE;
  }
  if (mode === 'evidence_hash_drift') {
    htmlSnapshot.evidence_hashes = [
      GM12_SPEC8_EVIDENCE_HASHES[0],
      'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
      GM12_SPEC8_EVIDENCE_HASHES[2],
    ];
  }

  return {
    ...base,
    harness_contract: GM12_SPEC8_CONTRACT,
    report_coherence_required: true,
    ledger_grammar_expectations: {
      stop_state: GM12_SPEC7_STOP_STATE,
      declared_specs: GM12_SPEC8_DECLARED_SPECS,
    },
    report_coherence_expectations: expected,
    ledger_text: [
      gm12Spec7LedgerText('valid'),
      '',
      gm12Spec8SurfaceText('ledger', ledgerSnapshot),
    ].join('\n'),
    thermometer_metrics: {
      ...base.thermometer_metrics,
      sources: GM12_SPEC8_EVIDENCE_HASHES.map((hash, index) => ({
        ref: `EV-SPEC-00${index + 1}-REPORT-COHERENCE`,
        type: 'fixture',
        hash,
      })),
      final_status: {
        ...base.thermometer_metrics.final_status,
        goal_maestro_execution_state: GM12_SPEC8_FINAL_STATUS,
        thermometer_report_status: GM12_SPEC8_REPORT_STATUS,
        share_gate_status: GM12_SPEC8_SHARE_STATUS,
      },
      report_coherence: metricsSnapshot,
    },
    receipt_text: gm12Spec8SurfaceText('receipt', receiptSnapshot),
    html_text: gm12Spec8HtmlText(htmlSnapshot),
    closeout: {
      status: 'pass',
      report_coherence: expected,
    },
    checksum_validation: gm12Spec8ChecksumValidation(mode),
  };
}

function gm12Spec8SurfaceText(surface, snapshot) {
  return [
    `# ${surface} report coherence`,
    `spec_ids: ${snapshot.spec_ids.join(',')}`,
    `final_status: ${snapshot.final_status}`,
    `report_status: ${snapshot.report_status}`,
    `share_status: ${snapshot.share_status}`,
    `evidence_hashes: ${snapshot.evidence_hashes.join(',')}`,
    `unproven_count: ${snapshot.unproven_count}`,
  ].join('\n');
}

function gm12Spec8HtmlText(snapshot) {
  return [
    '<!doctype html>',
    '<html lang="en">',
    '<body>',
    '<pre>',
    gm12Spec8SurfaceText('html', snapshot),
    '</pre>',
    '</body>',
    '</html>',
  ].join('\n');
}

function gm12Spec8ChecksumValidation(mode) {
  const actualHtmlHash = mode === 'checksum_mismatch'
    ? 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    : GM12_SPEC8_CHECKSUM_HASHES.html;
  return {
    status: 'pass',
    files: [
      { path: 'ledger.md', expected_hash: GM12_SPEC8_CHECKSUM_HASHES.ledger, actual_hash: GM12_SPEC8_CHECKSUM_HASHES.ledger },
      { path: 'exec_metrics.json', expected_hash: GM12_SPEC8_CHECKSUM_HASHES.metrics, actual_hash: GM12_SPEC8_CHECKSUM_HASHES.metrics },
      { path: 'context-receipt.md', expected_hash: GM12_SPEC8_CHECKSUM_HASHES.receipt, actual_hash: GM12_SPEC8_CHECKSUM_HASHES.receipt },
      { path: 'execution-thermometer.html', expected_hash: GM12_SPEC8_CHECKSUM_HASHES.html, actual_hash: actualHtmlHash },
    ],
  };
}

function gm12Spec9Fixture(mode) {
  const base = gm12Spec8Fixture('valid');
  const latestPackage = {
    package_id: GM12_SPEC9_LATEST_PACKAGE,
    path: `reports/${GM12_SPEC9_LATEST_PACKAGE}`,
    finalization_status: 'latest',
    package_result: 'pass',
  };
  const supersededPackage = {
    package_id: GM12_SPEC9_SUPERSEDED_PACKAGE,
    path: `reports/${GM12_SPEC9_SUPERSEDED_PACKAGE}`,
    finalization_status: 'superseded',
    failed: true,
    package_result: 'failed',
    superseded_by: GM12_SPEC9_LATEST_PACKAGE,
  };
  let packages = [supersededPackage, latestPackage];
  let closeoutPackageRefs = [GM12_SPEC9_LATEST_PACKAGE];
  let explicitPackageHistory = false;

  if (mode === 'unsorted_candidates') {
    packages = [
      { ...supersededPackage, finalization_status: 'candidate', superseded_by: undefined },
      { ...latestPackage, finalization_status: 'candidate' },
    ];
    closeoutPackageRefs = [GM12_SPEC9_SUPERSEDED_PACKAGE, GM12_SPEC9_LATEST_PACKAGE];
  }
  if (mode === 'missing_superseded_by') {
    packages = [
      { ...supersededPackage, superseded_by: undefined },
      latestPackage,
    ];
  }
  if (mode === 'closeout_history_leak') {
    closeoutPackageRefs = [GM12_SPEC9_SUPERSEDED_PACKAGE, GM12_SPEC9_LATEST_PACKAGE];
  }
  if (mode === 'explicit_history') {
    closeoutPackageRefs = [GM12_SPEC9_SUPERSEDED_PACKAGE, GM12_SPEC9_LATEST_PACKAGE];
    explicitPackageHistory = true;
  }

  return {
    ...base,
    harness_contract: GM12_SPEC9_CONTRACT,
    package_hierarchy_required: true,
    package_hierarchy_expectations: {
      stop_state: GM12_SPEC9_STOP_STATE,
      latest_package_id: GM12_SPEC9_LATEST_PACKAGE,
    },
    thermometer_packages: packages,
    thermometer_metrics: {
      ...base.thermometer_metrics,
      package_hierarchy: {
        latest_package_id: GM12_SPEC9_LATEST_PACKAGE,
        packages,
      },
    },
    closeout: {
      ...base.closeout,
      package_refs: closeoutPackageRefs,
      explicit_package_history: explicitPackageHistory,
    },
  };
}

function gm12Spec10Fixture(mode) {
  const base = gm12Spec9Fixture('valid');
  const identity = gm12Spec10Identity(mode);
  return {
    ...base,
    harness_contract: GM12_SPEC10_CONTRACT,
    report_identity_required: true,
    report_identity_expectations: {
      stop_state: GM12_SPEC10_STOP_STATE,
      installed_version: GM12_SPEC10_INSTALLED_VERSION,
      installed_available: true,
      source_package_available: true,
      known_adapter: 'codex',
    },
    report_identity: identity,
    thermometer_metrics: {
      ...base.thermometer_metrics,
      identity,
    },
    closeout: {
      ...base.closeout,
      report_identity: {
        harness_version: identity.harness.version,
        adapter: identity.harness.adapter,
        installed_version: identity.installed_version,
        source_package_version: identity.source_package.version,
      },
    },
  };
}

function gm12Spec10Identity(mode) {
  const identity = {
    schema_version: 1,
    report_id: 'report-run-010',
    generated_at_utc: '2026-06-29T00:00:00Z',
    harness: {
      name: 'tes-goal-maestro',
      version: GM12_SPEC10_INSTALLED_VERSION,
      adapter: 'codex',
      command: '--execute-loop',
      schema_version: '1',
    },
    model: {
      provider: 'openai',
      provider_source: 'host_observed',
      identity: 'gpt-5-codex',
      identity_source: 'host_observed',
      reasoning_profile: 'unproven',
      reasoning_profile_unproven_reason: 'host did not expose reasoning profile in the local report input',
      effort_multiplier: 'unproven',
      effort_multiplier_unproven_reason: 'host did not expose reasoning effort in the local report input',
    },
    installed_version: GM12_SPEC10_INSTALLED_VERSION,
    installed_at: GM12_SPEC10_INSTALLED_AT,
    source_package: {
      name: 'tilly-engineer-skills',
      version: GM12_SPEC10_INSTALLED_VERSION,
      source_commit: 'source-anchor-1f99741c',
      bundle_sha256: GM12_SPEC10_SOURCE_HASH,
    },
  };

  if (mode === 'version_mismatch') {
    identity.harness.version = '0.1.0';
  }
  if (mode === 'known_adapter_other') {
    identity.harness.adapter = 'other';
  }
  if (mode === 'missing_installed_at') {
    delete identity.installed_at;
  }
  if (mode === 'missing_model_reason') {
    delete identity.model.reasoning_profile_unproven_reason;
  }
  if (mode === 'missing_source_identity') {
    delete identity.source_package.source_commit;
    delete identity.source_package.bundle_sha256;
  }
  return identity;
}

function gm12Spec11Fixture(mode) {
  const base = gm12Spec10Fixture('valid');
  const artifact_class = mode === 'unsupported_artifact_class' ? 'api' : 'interactive_rendered_app';
  const visual_evidence = gm12Spec11VisualEvidence(mode);
  return {
    ...base,
    harness_contract: GM12_SPEC11_CONTRACT,
    visual_evidence_contract_required: true,
    visual_evidence_expectations: {
      stop_state: GM12_SPEC11_STOP_STATE,
      artifact_class,
      interactive: true,
      responsive_required: true,
      required_states: ['initial', 'active', 'terminal'],
    },
    source_artifact: {
      artifact_class,
      asks_for_responsive_behavior: true,
    },
    visual_evidence,
    thermometer_metrics: {
      ...base.thermometer_metrics,
      visual_evidence,
    },
    closeout: {
      ...base.closeout,
      visual_evidence: {
        status: mode === 'valid' ? 'complete' : 'claimed_complete_by_mutation',
        screenshot_refs: visual_evidence.map((item) => item.ref),
      },
    },
  };
}

function gm12Spec11VisualEvidence(mode) {
  const initial = {
    type: 'screenshot',
    ref: 'screenshots/spec-011-initial.png',
    state: 'initial',
    proves: 'initial state before interaction',
  };
  const active = {
    type: 'screenshot',
    ref: 'screenshots/spec-011-active.png',
    state: 'active',
    domain_objects: GM12_SPEC11_DOMAIN_OBJECTS,
    proves: 'active state with domain objects',
  };
  const terminal = {
    type: 'screenshot',
    ref: 'screenshots/spec-011-terminal.png',
    state: 'terminal',
    proves: 'terminal state after completion',
  };
  const mobileActive = {
    type: 'screenshot',
    ref: 'screenshots/spec-011-mobile-active.png',
    state: 'active',
    viewport: 'mobile',
    responsive: true,
    domain_objects: GM12_SPEC11_DOMAIN_OBJECTS,
    proves: 'mobile responsive active state',
  };

  if (mode === 'initial_only') return [initial];
  if (mode === 'terminal_only') return [terminal];
  if (mode === 'unmapped_screenshot') return [initial, { ...active, state: undefined }, terminal, mobileActive];
  if (mode === 'active_without_domain_objects') {
    return [
      initial,
      { ...active, domain_objects: [] },
      terminal,
      { ...mobileActive, domain_objects: [] },
    ];
  }
  if (mode === 'missing_responsive') return [initial, active, terminal];
  return [initial, active, terminal, mobileActive];
}

function gm12Spec12Fixture(mode) {
  const base = gm12Spec11Fixture('valid');
  const visual_evidence = gm12Spec12VisualEvidence(mode);
  return {
    ...base,
    harness_contract: GM12_SPEC12_CONTRACT,
    visual_semantic_gate_required: true,
    visual_semantic_expectations: {
      stop_state: GM12_SPEC12_STOP_STATE,
      artifact_class: 'rendered_app',
      expected_state: 'active',
      expected_objects: GM12_SPEC12_EXPECTED_OBJECTS,
      expected_score_status: GM12_SPEC12_SCORE_STATUS,
      expected_layout_area: GM12_SPEC12_LAYOUT_AREAS,
      expected_interaction_result: GM12_SPEC12_INTERACTION_RESULTS,
    },
    source_artifact: {
      artifact_class: 'rendered_app',
      asks_for_responsive_behavior: true,
    },
    visual_evidence,
    thermometer_metrics: {
      ...base.thermometer_metrics,
      visual_evidence,
    },
    closeout: {
      ...base.closeout,
      visual_evidence: {
        status: mode === 'valid' ? 'complete' : 'claimed_complete_by_mutation',
        screenshot_refs: visual_evidence.map((item) => item.ref),
      },
    },
  };
}

function gm12Spec12VisualEvidence(mode) {
  const [initial, spec11Active, terminal, mobileActive] = gm12Spec11VisualEvidence('valid');
  const active = {
    ...spec11Active,
    ref: 'screenshots/spec-012-active.png',
    artifact_class: 'rendered_app',
    pixel_non_degenerate: true,
    state_metadata: ['active'],
    visible_object_classes: GM12_SPEC12_EXPECTED_OBJECTS,
    score_status: GM12_SPEC12_SCORE_STATUS,
    layout_areas: GM12_SPEC12_LAYOUT_AREAS,
    interaction_results: GM12_SPEC12_INTERACTION_RESULTS,
    semantic_assertions: {
      pixel_non_degenerate: true,
      state_label: 'active',
      visible_object_classes: GM12_SPEC12_EXPECTED_OBJECTS,
      score_status: GM12_SPEC12_SCORE_STATUS,
      layout_area: GM12_SPEC12_LAYOUT_AREAS,
      interaction_result: GM12_SPEC12_INTERACTION_RESULTS,
    },
  };
  const responsive = { ...mobileActive, ref: 'screenshots/spec-012-mobile-active.png' };

  if (mode === 'missing_pixel_floor') {
    return [initial, { ...active, pixel_non_degenerate: false, semantic_assertions: { ...active.semantic_assertions, pixel_non_degenerate: false } }, terminal, responsive];
  }
  if (mode === 'missing_state_metadata') {
    const { state_metadata, semantic_assertions, ...withoutStateMetadata } = active;
    return [initial, { ...withoutStateMetadata, semantic_assertions: { ...semantic_assertions, state_label: 'idle' } }, terminal, responsive];
  }
  if (mode === 'missing_objects') {
    return [initial, { ...active, visible_object_classes: ['background'], semantic_assertions: { ...active.semantic_assertions, visible_object_classes: ['background'] } }, terminal, responsive];
  }
  if (mode === 'missing_score_status') {
    return [initial, { ...active, score_status: ['pending'], semantic_assertions: { ...active.semantic_assertions, score_status: ['pending'] } }, terminal, responsive];
  }
  if (mode === 'missing_layout_area') {
    return [initial, { ...active, layout_areas: ['footer'], semantic_assertions: { ...active.semantic_assertions, layout_area: ['footer'] } }, terminal, responsive];
  }
  if (mode === 'missing_interaction_result') {
    return [initial, { ...active, interaction_results: ['no interaction'], semantic_assertions: { ...active.semantic_assertions, interaction_result: ['no interaction'] } }, terminal, responsive];
  }
  return [initial, active, terminal, responsive];
}

function gm12Spec13Fixture(mode) {
  const base = gm12Spec12Fixture('valid');
  const browserMetrics = mode === 'host_minimal'
    ? [gm12Spec13HostMinimalMetric()]
    : gm12Spec13BrowserMetricsForMode(mode);
  return {
    ...base,
    harness_contract: GM12_SPEC13_CONTRACT,
    browser_metrics_schema_required: true,
    browser_metrics_expectations: {
      stop_state: GM12_SPEC13_STOP_STATE,
      required_browser_sources: GM12_SPEC13_BROWSER_SOURCES,
    },
    browser_metrics_json: {
      schema_version: 1,
      metrics: browserMetrics,
    },
    thermometer_metrics: {
      ...base.thermometer_metrics,
      browser_metrics: {
        schema_version: 1,
        metrics: browserMetrics,
      },
    },
    closeout: {
      ...base.closeout,
      browser_metrics: {
        status: mode === 'valid' ? 'complete' : 'claimed_complete_by_mutation',
        sources: browserMetrics.map((entry) => entry.browser_source),
      },
    },
  };
}

function gm12Spec13HostMinimalMetric() {
  return {
    runtime_target: 'browser',
    browser_source: 'codex',
    console_errors: [],
  };
}

function gm12Spec13BrowserMetricsForMode(mode) {
  const metrics = GM12_SPEC13_BROWSER_SOURCES.map(gm12Spec13BrowserMetric);
  if (mode === 'missing_status') {
    delete metrics[0].status;
  }
  if (mode === 'missing_source_coverage') {
    return metrics.filter((entry) => entry.browser_source !== 'cursor');
  }
  if (mode === 'missing_state_transitions') {
    delete metrics[0].state_transitions;
  }
  if (mode === 'missing_restart_evidence') {
    const cursorMetric = metrics.find((entry) => entry.browser_source === 'cursor');
    cursorMetric.restart = { applicable: true };
  }
  if (mode === 'missing_domain_metrics') {
    metrics[0].domain_metrics = { applicable: true, metrics: [] };
  }
  return metrics;
}

function gm12Spec13BrowserMetric(browser_source) {
  const screenshotRef = `screenshots/spec-013-${browser_source}-active.png`;
  const restartApplicable = browser_source === 'cursor';
  return {
    status: 'PASS',
    runtime_target: 'browser',
    browser_source,
    console_errors: [],
    uncaught_errors: [],
    screenshots: [
      {
        ref: screenshotRef,
        state: 'active',
        hash: `${browser_source}-screenshot-hash`,
      },
    ],
    state_transitions: [
      { from: 'initial', to: 'active', via: 'open served app and run interaction' },
      { from: 'active', to: 'terminal', via: 'complete the checked interaction path' },
    ],
    visual_assertions: [
      { name: 'active scene visible', status: 'pass', evidence_ref: screenshotRef },
      { name: 'expected objects present', status: 'pass', evidence_ref: screenshotRef },
    ],
    interaction_path: [
      { step: 1, action: 'navigate', target: 'served browser runtime' },
      { step: 2, action: 'interact', target: 'active scene control' },
    ],
    restart: {
      applicable: restartApplicable,
      status: restartApplicable ? 'pass' : 'not_applicable',
      attempts: restartApplicable ? [{ reason: 'host requested browser restart', status: 'pass' }] : [],
    },
    domain_metrics: {
      applicable: true,
      metrics: [
        { name: 'score', value: 12, source: 'rendered_output' },
        { name: 'state', value: 'active', source: 'visual_assertion' },
      ],
    },
    failures: [],
  };
}

function gm12Spec14Fixture(mode) {
  const base = gm12Spec13Fixture('valid');
  const installChronology = gm12Spec14InstallChronology(mode);
  return {
    ...base,
    harness_contract: GM12_SPEC14_CONTRACT,
    install_chronology_required: true,
    install_chronology_json: installChronology,
    thermometer_metrics: {
      ...base.thermometer_metrics,
      install_chronology: installChronology,
    },
    closeout: {
      ...base.closeout,
      install_chronology: {
        status: mode === 'valid' || mode === 'classified_later_reinstall' ? 'complete' : 'claimed_complete_by_mutation',
        installed_at: installChronology.installed_at,
      },
    },
  };
}

function gm12Spec14InstallChronology(mode) {
  const chronology = {
    installed_version: GM12_SPEC10_INSTALLED_VERSION,
    installed_at: mode === 'install_after_material' || mode === 'classified_later_reinstall'
      ? GM12_SPEC14_AFTER_MATERIAL_AT
      : GM12_SPEC14_INSTALLED_AT,
    git_head_before_loop: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    baseline_commit: 'cc4a8bbe',
    material_commit_timestamps: [
      { commit: '74c4bfc2', committed_at: '2026-06-29T00:00:00Z' },
      { commit: 'e3e85baf', committed_at: '2026-06-29T00:20:00Z' },
    ],
  };
  if (mode === 'missing_installed_version') {
    delete chronology.installed_version;
  }
  if (mode === 'missing_git_head') {
    delete chronology.git_head_before_loop;
  }
  if (mode === 'missing_baseline_commit') {
    delete chronology.baseline_commit;
  }
  if (mode === 'missing_material_timestamps') {
    delete chronology.material_commit_timestamps;
  }
  if (mode === 'classified_later_reinstall') {
    chronology.install_classification = 'unrelated_later_reinstall';
    chronology.install_classification_reason = 'reinstall happened after material commits and did not provide the baseline used for execution';
  }
  return chronology;
}

function gm12Spec15Fixture(mode) {
  const base = gm12Spec14Fixture('valid');
  const commitEnforcement = gm12Spec15CommitEnforcement(mode);
  return {
    ...base,
    harness_contract: GM12_SPEC15_CONTRACT,
    commit_enforcement_classification_required: true,
    commit_enforcement_classification: commitEnforcement,
    thermometer_metrics: {
      ...base.thermometer_metrics,
      commit_enforcement: commitEnforcement,
    },
    closeout: gm12Spec15Closeout(base.closeout, mode, commitEnforcement),
  };
}

function gm12Spec15CommitEnforcement(mode) {
  const classification = mode === 'precommit_enforced'
    ? {
        commit_mode: 'precommit_enforced',
        tes_recommends_precommit: true,
        precommit_evidence: {
          status: 'installed',
          hook_path: '.githooks/pre-commit',
        },
      }
    : {
        commit_mode: 'manual',
        tes_recommends_precommit: true,
        precommit_evidence: {
          status: 'PRECOMMIT_NOT_INSTALLED',
        },
      };
  if (mode === 'missing_precommit_evidence') {
    delete classification.precommit_evidence;
  }
  if (mode === 'missing_commit_mode') {
    delete classification.commit_mode;
  }
  return classification;
}

function gm12Spec15Closeout(closeout, mode, commitEnforcement) {
  const result = {
    ...closeout,
    commit_enforcement: {
      commit_mode: commitEnforcement.commit_mode,
      precommit_status: commitEnforcement.precommit_evidence?.status ?? 'missing',
      report_text: 'manual commit evidence classified honestly',
    },
  };
  if (mode === 'manual_claims_enforced') {
    result.commit_enforcement.report_text = 'precommit enforced by installed hook';
  }
  if (mode === 'precommit_enforced') {
    result.commit_enforcement.report_text = 'precommit enforced by installed hook evidence';
  }
  return result;
}

function gm12Spec16Fixture(mode) {
  const base = gm12Spec15Fixture('valid');
  const gitAdmission = gm12Spec16GitAdmission(mode);
  return {
    ...base,
    harness_contract: GM12_SPEC16_CONTRACT,
    git_admission_gate_required: true,
    git_admission: gitAdmission,
    thermometer_metrics: {
      ...base.thermometer_metrics,
      git_admission: gitAdmission,
    },
    closeout: gm12Spec16Closeout(base.closeout, mode, gitAdmission),
  };
}

function gm12Spec16GitAdmission(mode) {
  const admission = {
    checked_before_loop: true,
    repository_status: 'present',
    git_repository_exists: true,
    owner_decision: 'use_existing_repository',
    git_init: {
      performed: false,
      owner_authorized: false,
    },
    baseline_commit_classification: {
      status: 'existing_head',
      commit: '5246d3c8',
      evidence_ref: 'git rev-parse HEAD',
    },
  };
  if (mode === 'missing_repo_no_stop') {
    admission.repository_status = 'absent';
    admission.git_repository_exists = false;
    admission.owner_decision = 'continue_without_git';
    admission.baseline_commit_classification = {
      status: 'no_git_repository',
      evidence_ref: 'git rev-parse --is-inside-work-tree exit 128',
    };
  }
  if (mode === 'needs_git_repository') {
    admission.repository_status = 'absent';
    admission.git_repository_exists = false;
    admission.owner_decision = 'needs_git_repository';
    admission.stop_state = GM12_SPEC16_STOP_STATE;
    admission.baseline_commit_classification = {
      status: 'no_git_repository',
      evidence_ref: 'git rev-parse --is-inside-work-tree exit 128',
    };
  }
  if (mode === 'silent_git_init' || mode === 'authorized_git_init') {
    admission.repository_status = 'absent';
    admission.git_repository_exists = false;
    admission.owner_decision = mode === 'authorized_git_init' ? 'authorized_git_init' : 'git_init_performed';
    admission.owner_authorization_ref = mode === 'authorized_git_init' ? 'owner-approved-git-init' : '';
    admission.git_init = {
      performed: true,
      owner_authorized: mode === 'authorized_git_init',
    };
    admission.baseline_commit_classification = {
      status: 'initialized_empty_repository',
      evidence_ref: mode === 'authorized_git_init' ? 'owner-approved-git-init' : 'git init terminal output',
    };
  }
  if (mode === 'missing_baseline_classification') {
    delete admission.baseline_commit_classification;
  }
  return admission;
}

function gm12Spec16Closeout(closeout, mode, gitAdmission) {
  return {
    ...closeout,
    git_admission: {
      repository_status: gitAdmission.repository_status,
      owner_decision: gitAdmission.owner_decision,
      stop_state: mode === 'needs_git_repository' ? GM12_SPEC16_STOP_STATE : 'ready_for_loop',
      baseline_commit_classification: gitAdmission.baseline_commit_classification ?? null,
      report_text: mode === 'authorized_git_init'
        ? 'git init authorized explicitly by owner with initialized-empty baseline evidence'
        : 'Git repository admission classified before execution loop',
    },
  };
}

function gm12Spec17Fixture(mode) {
  const base = gm12Spec16Fixture('valid');
  const evidenceTracking = gm12Spec17EvidenceTracking(mode);
  return {
    ...base,
    harness_contract: GM12_SPEC17_CONTRACT,
    evidence_tracking_classification_required: true,
    evidence_tracking: evidenceTracking,
    thermometer_metrics: {
      ...base.thermometer_metrics,
      evidence_tracking: evidenceTracking,
    },
    closeout: gm12Spec17Closeout(base.closeout, mode, evidenceTracking),
  };
}

function gm12Spec17EvidenceTracking(mode) {
  const screenshotClassification = mode === 'missing_screenshot_classification'
    || mode === 'untracked_unclassified'
    || mode === 'clean_claim_unclassified'
    ? ''
    : 'runtime_only';
  const artifacts = [
    {
      artifact_class: 'ledger',
      path: 'docs/roadmap/goals/ledgers/goal-ledger.md',
      classification: 'tracked',
    },
    {
      artifact_class: 'screenshots',
      path: 'artifacts/browser-initial.png',
      classification: screenshotClassification,
    },
    {
      artifact_class: 'metrics',
      path: 'artifacts/browser-metrics.json',
      classification: 'tracked',
    },
    {
      artifact_class: 'reports',
      path: 'artifacts/closeout.md',
      classification: 'tracked',
    },
    {
      artifact_class: 'packages',
      path: 'artifacts/package.zip',
      classification: 'tracked',
    },
  ];
  const untrackedScreenshot = {
    artifact_class: 'screenshots',
    path: 'artifacts/browser-initial.png',
  };
  if (mode === 'runtime_only_classified') {
    untrackedScreenshot.classification = 'runtime_only';
  }
  return {
    git_status: {
      tracked_files_clean: true,
      untracked_required_evidence: [untrackedScreenshot],
    },
    artifacts,
  };
}

function gm12Spec17Closeout(closeout, mode, evidenceTracking) {
  return {
    ...closeout,
    evidence_tracking: {
      status: mode === 'clean_claim_unclassified' ? 'clean' : 'classified',
      stop_state: mode === 'clean_claim_unclassified' ? GM12_SPEC17_STOP_STATE : 'ready_for_loop',
      required_classes: ['ledger', 'screenshots', 'metrics', 'reports', 'packages'],
      artifact_count: evidenceTracking.artifacts.length,
      report_text: mode === 'clean_claim_unclassified'
        ? 'all evidence clean; no untracked evidence remains'
        : 'required evidence storage classifications are recorded',
    },
  };
}

function gm12Spec18Fixture(mode) {
  const base = gm12Spec17Fixture('valid');
  const flashFry = gm12Spec18FlashFry(mode);
  return {
    ...base,
    harness_contract: GM12_SPEC18_CONTRACT,
    flash_fry_operational_status_required: true,
    flash_fry: flashFry,
    thermometer_metrics: {
      ...base.thermometer_metrics,
      flash_fry: flashFry,
    },
    closeout: gm12Spec18Closeout(base.closeout, mode, flashFry),
  };
}

function gm12Spec18FlashFry(mode) {
  const flashFry = {
    status: 'ran',
    artifact_ref: 'artifacts/flash-fry-decision.json',
    protection_score_adjusted: false,
    command_introduced_solely_for_status: false,
  };
  if (mode === 'missing_status') {
    delete flashFry.status;
  }
  if (mode === 'ran_missing_evidence') {
    delete flashFry.artifact_ref;
  }
  if (mode === 'not_configured_no_adjustment' || mode === 'not_configured_adjusted') {
    flashFry.status = 'not_configured';
    delete flashFry.artifact_ref;
    flashFry.reason = 'Flash-Fry is not configured in this target runtime';
    flashFry.protection_score_adjusted = mode === 'not_configured_adjusted';
  }
  if (mode === 'new_command') {
    flashFry.new_command = {
      command: 'npm run flash-fry-status',
      solely_for_status: true,
    };
  }
  return flashFry;
}

function gm12Spec18Closeout(closeout, mode, flashFry) {
  return {
    ...closeout,
    flash_fry: {
      status: flashFry.status ?? 'missing',
      stop_state: mode === 'missing_status' ? GM12_SPEC18_STOP_STATE : 'ready_for_loop',
      reason: flashFry.reason,
      protection_score_adjusted: flashFry.protection_score_adjusted,
      report_text: mode === 'missing_status'
        ? 'protection quality remains high'
        : 'Flash-Fry operational status recorded with protection score context',
    },
  };
}

function gm12Spec19Fixture(mode) {
  const base = gm12Spec18Fixture('valid');
  const lensLedger = gm12Spec19LensLedger(mode);
  return {
    ...base,
    harness_contract: GM12_SPEC19_CONTRACT,
    lens_ledger_required: true,
    lens_ledger: lensLedger,
    thermometer_metrics: {
      ...base.thermometer_metrics,
      lens_ledger: lensLedger,
    },
    closeout: gm12Spec19Closeout(base.closeout, mode, lensLedger),
  };
}

function gm12Spec19LensLedger(mode) {
  if (mode === 'missing_ledger') return {};
  const lenses = GM12_SPEC19_LENSES.map((lens) => ({
    lens,
    classification: lens === 'visual' ? 'not_required' : 'applied',
    impact: `${lens} lens shaped the execution decision`,
    evidence_ref: `lens-ledger:${lens}`,
  }));
  if (mode === 'missing_lens') {
    return { lenses: lenses.filter((entry) => entry.lens !== 'security') };
  }
  if (mode === 'missing_impact') {
    lenses.find((entry) => entry.lens === 'cost').impact = '';
  }
  if (mode === 'score_without_evidence') {
    for (const entry of lenses) delete entry.evidence_ref;
  }
  return {
    section_ref: mode === 'score_without_evidence' ? '' : 'lens-ledger-section',
    lenses,
  };
}

function gm12Spec19Closeout(closeout, mode, lensLedger) {
  const result = {
    ...closeout,
    lens_ledger: {
      status: mode === 'missing_ledger' ? 'missing' : 'present',
      stop_state: mode === 'missing_ledger' ? GM12_SPEC19_STOP_STATE : 'ready_for_loop',
      lens_count: Array.isArray(lensLedger.lenses) ? lensLedger.lenses.length : 0,
      report_text: 'lens ledger records applied, not_required, and blocked execution lenses',
    },
  };
  if (mode === 'score_without_evidence' || mode === 'score_with_evidence') {
    result.proof_score = {
      value: 0.82,
      lenses: ['runtime', 'evidence'],
    };
  }
  return result;
}

function gm12Spec20Fixture(mode) {
  const base = gm12Spec19Fixture('valid');
  const cloudSearch = gm12Spec20CloudSearch(mode);
  return {
    ...base,
    harness_contract: GM12_SPEC20_CONTRACT,
    cloud_search_classification_required: true,
    cloud_search: cloudSearch,
    thermometer_metrics: {
      ...base.thermometer_metrics,
      cloud_search: cloudSearch,
    },
    closeout: gm12Spec20Closeout(base.closeout, mode, cloudSearch),
  };
}

function gm12Spec20CloudSearch(mode) {
  const classification = {
    status: 'not_required',
    reason: 'self-contained local work used repository source and local fixtures only',
    authorization_status: 'not_required',
    redaction_status: 'not_required',
  };
  if (mode === 'missing_status') {
    delete classification.status;
  }
  if (mode === 'missing_reason') {
    delete classification.reason;
  }
  if (mode === 'unauthorized_run' || mode === 'missing_redaction' || mode === 'ran_authorized') {
    classification.status = 'ran';
    classification.reason = 'external lookup was used to verify current host behavior';
    classification.authorization_status = mode === 'unauthorized_run' ? 'not_authorized' : 'owner_authorized';
    classification.redaction_status = mode === 'missing_redaction' ? '' : 'redacted';
  }
  return classification;
}

function gm12Spec20Closeout(closeout, mode, cloudSearch) {
  return {
    ...closeout,
    cloud_search: {
      status: cloudSearch.status ?? 'missing',
      stop_state: mode === 'missing_status' ? GM12_SPEC20_STOP_STATE : 'ready_for_loop',
      reason: cloudSearch.reason,
      authorization_status: cloudSearch.authorization_status,
      redaction_status: cloudSearch.redaction_status,
      report_text: mode === 'missing_status'
        ? 'cloud search decision omitted'
        : 'cloud search decision recorded with authorization and redaction context',
    },
  };
}

function gm12Spec21Fixture(mode) {
  const base = gm12Spec20Fixture('valid');
  const telemetry = gm12Spec21Telemetry(mode);
  const result = {
    ...base,
    harness_contract: GM12_SPEC21_CONTRACT,
    llm_cache_cost_telemetry_required: true,
    llm_cache_cost_telemetry: telemetry,
    thermometer_metrics: {
      ...base.thermometer_metrics,
      llm_cache_cost_telemetry: telemetry,
    },
    closeout: gm12Spec21Closeout(base.closeout, mode, telemetry),
  };
  if (mode === 'missing_telemetry') {
    delete result.llm_cache_cost_telemetry;
    delete result.thermometer_metrics.llm_cache_cost_telemetry;
  }
  return result;
}

function gm12Spec21Telemetry(mode) {
  const telemetry = {
    input_tokens: 12000,
    cached_input_tokens: 8000,
    output_tokens: 900,
    reasoning_tokens: 700,
    cache_hit_estimate: 0.66,
    wall_time_ms: 184000,
    confidence: 0.82,
    efficiency_score: {
      value: 0.74,
      basis: ['input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_tokens', 'cache_hit_estimate'],
    },
  };
  if (mode === 'missing_field') {
    delete telemetry.cached_input_tokens;
  }
  if (mode === 'zeroed_missing_field') {
    telemetry.cached_input_tokens = 0;
    telemetry.missing_fields = ['cached_input_tokens'];
    telemetry.efficiency_score = {
      value: 0.65,
      qualified: true,
      qualification: 'cached input tokens unproven',
    };
  }
  if (mode === 'unqualified_efficiency' || mode === 'unproven_qualified') {
    telemetry.cached_input_tokens = 'unproven';
    telemetry.missing_fields = ['cached_input_tokens'];
    telemetry.efficiency_score = {
      value: 0.92,
      basis: ['input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_tokens', 'cache_hit_estimate'],
      qualified: mode === 'unproven_qualified',
      qualification: mode === 'unproven_qualified' ? 'cached input tokens unproven' : '',
    };
  }
  return telemetry;
}

function gm12Spec21Closeout(closeout, mode, telemetry) {
  return {
    ...closeout,
    llm_cache_cost_telemetry: {
      status: mode === 'missing_telemetry' ? 'missing' : 'present',
      stop_state: mode === 'missing_telemetry' ? GM12_SPEC21_STOP_STATE : 'ready_for_loop',
      input_tokens: telemetry.input_tokens,
      cached_input_tokens: telemetry.cached_input_tokens,
      output_tokens: telemetry.output_tokens,
      reasoning_tokens: telemetry.reasoning_tokens,
      cache_hit_estimate: telemetry.cache_hit_estimate,
      wall_time_ms: telemetry.wall_time_ms,
      confidence: telemetry.confidence,
      report_text: mode === 'missing_telemetry'
        ? 'LLM cache and cost telemetry omitted'
        : 'LLM cache and cost telemetry records token, cache, timing, and confidence fields',
    },
    efficiency_score: telemetry.efficiency_score,
  };
}

function gm12Spec2PreEditEvent(spec_id, at) {
  return {
    type: 'pre_edit_gate_artifact',
    spec_id,
    at,
    artifact: {
      path: GM12_SPEC2_PRE_EDIT_REF,
      active_spec: spec_id,
      first_unexecuted_spec: spec_id,
      anchor_hash: GM12_SPEC2_ANCHOR_HASH,
      baseline_state: {
        spec_001_commit: '74c4bfc2',
        worktree: 'unrelated-change-present',
      },
      allowed_files: GM12_SPEC2_ALLOWED_FILES,
      forbidden_files: GM12_SPEC2_FORBIDDEN_FILES,
      forbidden_actions: GM12_SPEC2_FORBIDDEN_ACTIONS,
      required_gates: GM12_SPEC2_REQUIRED_GATES,
      installed_tes_version: '0.3.230',
      commit_mode: 'no-commit',
    },
  };
}

function gm12Spec3PromptEvent(spec_id, at, mode) {
  const artifact = mode === 'echo'
    ? {
        path: 'prompt_enrichment_packet.md',
        body: GM12_SPEC3_SOURCE_PROMPT,
      }
    : {
        path: GM12_SPEC3_PROMPT_REF,
        extracted_intent: 'Validate that Goal Maestro enriched the source artifact before SPEC-003 execution.',
        spec_queue: [spec_id],
        lenses_selected: ['execution-order', 'prompt-enrichment', 'evidence-contract'],
        structural_method: GM12_SPEC3_STRUCTURAL_METHOD,
        oracle_packet: {
          direct_positive: 'goal-maestro-p0-harness.mjs accepts a complete prompt enrichment packet',
          direct_negative: GM12_SPEC3_STOP_STATE,
        },
        evidence_contract: {
          packet_ref: GM12_SPEC3_PROMPT_REF,
          required_before: ['open_spec', 'implement'],
        },
        stop_states: [GM12_SPEC3_STOP_STATE],
        risk_decisions: ['SPEC-004 and later remain out of scope'],
        non_objectives: ['no docs claims', 'no package version bump', 'no remote sync'],
        sidecar_requirements: ['prompt_enrichment_packet.json or prompt_enrichment_packet.md'],
      };

  return {
    type: 'prompt_enrichment_packet',
    spec_id,
    at,
    artifact,
  };
}

function gm12Spec4DocumentAnalysisEvent(spec_id, at, mode) {
  const artifact = {
    path: GM12_SPEC4_DOCUMENT_REF,
    source_artifact_kind: 'Super SPEC',
    functional_requirements: ['convert the source artifact into a document analysis packet before execution'],
    non_functional_requirements: ['local-only harness validation with no runtime service'],
    acceptance_criteria: [
      'execution without a document analysis packet fails',
      'a packet with missing acceptance criteria fails',
    ],
    forbidden_moves: ['SPEC-005 and later remain out of scope', 'no docs claims', 'no package version bump'],
    visual_runtime_requirements: ['runtime harness validation only; visual requirements not applicable'],
    evidence_requirements: ['direct positive fixture', 'missing packet negative fixture', 'missing acceptance criteria negative fixture'],
    explicit_ambiguities: ['none for this SPEC-004 harness fixture'],
    external_documentation_required: false,
    cloud_search_required: false,
  };
  if (mode === 'missing_acceptance_criteria') {
    delete artifact.acceptance_criteria;
  }

  return {
    type: 'document_analysis_packet',
    spec_id,
    at,
    artifact,
  };
}

function gm12Time(second) {
  return `2026-06-29T00:00:${String(second).padStart(2, '0')}Z`;
}

function sourcePackageVersion() {
  const packageJsonPath = join(sourceRoot, 'package.json');
  if (!existsSync(packageJsonPath)) return '0.3.230';
  try {
    const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf8'));
    return typeof packageJson.version === 'string' && packageJson.version.length > 0
      ? packageJson.version
      : '0.3.230';
  } catch {
    return '0.3.230';
  }
}

function badInstalledThermometerSkillRoot(name) {
  const root = join(tmp, name);
  mkdirSync(join(root, 'references'), { recursive: true });
  mkdirSync(join(root, 'templates'), { recursive: true });
  mkdirSync(join(root, 'scripts'), { recursive: true });
  writeFileSync(join(root, 'SKILL.md'), '# Bad Goal Maestro\n');
  writeFileSync(join(root, 'references/execution-loop-runner.md'), 'Execution Thermometer without installed contract.\n');
  writeFileSync(join(root, 'templates/maestral-goal-prompt.template.md'), 'No thermometer hook.\n');
  writeFileSync(join(root, 'scripts/execution-thermometer-package.mjs'), 'console.log("bad package");\n');
  writeFileSync(join(root, 'scripts/execution-thermometer-html.mjs'), 'console.log("bad html");\n');
  writeFileSync(join(root, 'scripts/execution-thermometer-schema.mjs'), 'console.log("bad schema");\n');
  writeFileSync(join(root, 'scripts/execution-thermometer-extract.mjs'), 'console.log("bad extract");\n');
  return root;
}

function cursorRuntimeRuleArg() {
  if (existsSync(sourceCursorRuntimeRule)) {
    return sourceCursorRuntimeRule;
  }
  if (existsSync(installedCursorRuntimeRule)) {
    return installedCursorRuntimeRule;
  }
  return fixture('missing-cursor-runtime-capabilities.mdc', '');
}

// Cada parede: {id, harness, violate→args (deve dar exit≠0), revert→args (deve dar exit 0)}.
const WALLS = [
  // D4 — ledger placeholder
  {
    id: 'D4 ledger-no-placeholder',
    harness: 'ledger-no-placeholder.mjs',
    violate: () => [fixture('d4-bad.md', '| S | x | g | commit: <a seguir> | n |\n')],
    revert: () => [fixture('d4-ok.md', '| S | x | g | commit: abc1234 | n |\n')],
  },
  // D1 — audit re-mutation (facade fica PASS = falha; honesto cai = passa)
  {
    id: 'D1 audit-remutation',
    harness: 'audit-remutation.mjs',
    violate: () => [fixture('d1-facade.json', JSON.stringify({ oracles: [{ axis: 'f', name: 'x', command: 'true', mutate: 'true', revert: 'true' }] }))],
    revert: () => [fixture('d1-honest.json', JSON.stringify({ oracles: [{ axis: 'h', name: 'y', command: `test ! -f ${join(tmp, '__f')}`, mutate: `touch ${join(tmp, '__f')}`, revert: `rm -f ${join(tmp, '__f')}` }] }))],
  },
  // C1 — name↔measure
  {
    id: 'C1 oracle-name-measure',
    harness: 'oracle-name-measure.mjs',
    violate: () => [fixture('c1-facade.json', JSON.stringify({ oracles: [{ name: 'avgLuma', proven_property: 'luminância', measured_quantity: 'statSync(png).size bytes' }] }))],
    revert: () => [fixture('c1-ok.json', JSON.stringify({ oracles: [{ name: 'avgLuma', proven_property: 'luminância', measured_quantity: 'média RGB dos pixels decodificados' }] }))],
  },
  // C2 — topology probe
  {
    id: 'C2 topology-probe',
    harness: 'topology-probe.mjs',
    violate: () => [fixture('c2-over.json', JSON.stringify({ targets: [{ file: join(here, 'validate-walls.mjs'), max: 1 }] }))],
    revert: () => [fixture('c2-ok.json', JSON.stringify({ targets: [{ file: join(here, 'validate-walls.mjs'), max: 100000 }] }))],
  },
  // B1 — runtime import grep
  {
    id: 'B1 runtime-import-grep',
    harness: 'runtime-import-grep.mjs',
    violate: () => [fixture('b1-bad.ts', "import { readFileSync } from 'node:fs';\n")],
    revert: () => [fixture('b1-ok.ts', "import { foo } from './local';\n")],
  },
  // C3 — browser boot smoke
  {
    id: 'C3 browser-boot-smoke',
    harness: 'browser-boot-smoke.mjs',
    violate: () => [fixture('c3-bad.json', JSON.stringify({ target: 'browser', ran_against: 'node-stub', consoleErrors: [], uncaught: [], ticks_advanced: true }))],
    revert: () => [fixture('c3-ok.json', JSON.stringify({ target: 'browser', ran_against: 'served-dist-client', consoleErrors: [], uncaught: [], ticks_advanced: true }))],
  },
  // META — context completeness
  {
    id: 'META context-completeness',
    harness: 'context-completeness.mjs',
    violate: () => [fixture('m-bad.json', JSON.stringify({ axes: [{ id: 'r', oracle_runner_contract: 'x', regression_target: 'ci' }] }))],
    revert: () => [fixture('m-ok.json', JSON.stringify({ axes: [{ id: 'r', runtime_target: 'browser', oracle_runner_contract: 'x', regression_target: 'ci' }] }))],
  },
  // C4 — scene non-degenerate (precisa de PNG; gerado abaixo)
  {
    id: 'C4 scene-non-degenerate',
    harness: 'scene-non-degenerate.mjs',
    violate: () => [makePng('c4-flat.png', () => [140, 100, 60])],
    revert: () => [makePng('c4-rich.png', (x, y) => [(x * 4) & 255, (y * 4) & 255, ((x + y) * 2) & 255])],
  },
  // D2 — claim↔artifact coherence
  {
    id: 'D2 claim-artifact-coherence',
    harness: 'claim-artifact-coherence.mjs',
    violate: () => [fixture('d2-bad.json', JSON.stringify({ claims: { backend: 'WebGPU' }, artifact: { backend: 'webgl2' }, fieldMap: { backend: 'backend' } }))],
    revert: () => [fixture('d2-ok.json', JSON.stringify({ claims: { backend: 'webgl2' }, artifact: { backend: 'webgl2' }, fieldMap: { backend: 'backend' } }))],
  },
  // D3 — oracle wiring por RE-MUTAÇÃO DO GATE (gate WIRED re-roda o oráculo; FACADE não)
  {
    id: 'D3 oracle-wiring-check',
    harness: 'oracle-wiring-check.mjs',
    // FACADE: gate_command 'true' nunca re-roda o oráculo → fica 0 mesmo com o oráculo quebrado → exit 1.
    violate: () => [fixture('d3-bad.json', JSON.stringify({ oracles: [{
      axis: 'f', regression_target: '.ci/fake',
      gate_command: 'true',
      oracle_command: `test ! -f ${join(tmp, '__d3f')}`,
      mutate: `touch ${join(tmp, '__d3f')}`, revert: `rm -f ${join(tmp, '__d3f')}`,
      decoy_mutate: `touch ${join(tmp, '__d3fd')}`, decoy_revert: `rm -f ${join(tmp, '__d3fd')}`,
    }] }))],
    // WIRED: gate envolve o oráculo via wrapper distinto (não-substring), insensível ao decoy → exit 0.
    revert: () => [fixture('d3-ok.json', JSON.stringify({ oracles: [{
      axis: 'h', regression_target: '.ci/real',
      gate_command: `sh -c '[ ! -e ${join(tmp, '__d3h')} ]'`,
      oracle_command: `test ! -f ${join(tmp, '__d3h')}`,
      mutate: `touch ${join(tmp, '__d3h')}`, revert: `rm -f ${join(tmp, '__d3h')}`,
      decoy_mutate: `touch ${join(tmp, '__d3hd')}`, decoy_revert: `rm -f ${join(tmp, '__d3hd')}`,
    }] }))],
  },
  // A1 — anchor rehash
  {
    id: 'A1 anchor-rehash',
    harness: 'anchor-rehash.mjs',
    violate: () => [join(here, 'validate-walls.mjs'), 'deadbeefdeadbeef'],
    revert: () => [join(here, 'validate-walls.mjs'), gitHash(join(here, 'validate-walls.mjs'))],
  },
  // GM1 — execution thermometer schema validator (valid fixture passes; invalid metric ref fires).
  {
    id: 'GM1 execution-thermometer-schema',
    harness: 'execution-thermometer-schema.mjs',
    violate: () => [
      join(here, 'fixtures/execution-thermometer/valid/exec_identity.yaml'),
      join(here, 'fixtures/execution-thermometer/invalid-unreferenced-metric/exec_metrics.json'),
    ],
    revert: () => [
      join(here, 'fixtures/execution-thermometer/valid/exec_identity.yaml'),
      join(here, 'fixtures/execution-thermometer/valid/exec_metrics.json'),
    ],
  },
  // GM2 — execution thermometer extractor (hash mismatch blocks; valid ledger extracts and validates).
  {
    id: 'GM2 execution-thermometer-extract',
    harness: 'execution-thermometer-extract.mjs',
    violate: () => [
      join(here, 'fixtures/execution-thermometer-extract/valid/ledger.md'),
      join(tmp, 'gm2-hash-mismatch'),
      '--expected-ledger-sha256',
      'deadbeef',
    ],
    revert: () => [
      join(here, 'fixtures/execution-thermometer-extract/valid/ledger.md'),
      join(tmp, 'gm2-valid'),
      '--generated-at',
      '2026-06-29T00:00:00Z',
    ],
  },
  // GM3 — Markdown context receipt (inline HTML fails; valid schema renders Markdown-only).
  {
    id: 'GM3 execution-thermometer-receipt',
    harness: 'execution-thermometer-receipt.mjs',
    violate: () => ['--check-only', join(here, 'fixtures/execution-thermometer-receipt/invalid-inline-html/context-receipt.md')],
    revert: () => [
      join(here, 'fixtures/execution-thermometer/valid/exec_identity.yaml'),
      join(here, 'fixtures/execution-thermometer/valid/exec_metrics.json'),
      join(tmp, 'gm3-context-receipt.md'),
    ],
  },
  // GM4 — static HTML report (runtime fetch fixture fails; multi-loop #loop-L4 renders).
  {
    id: 'GM4 execution-thermometer-html',
    harness: 'execution-thermometer-html.mjs',
    violate: () => ['--check-only', join(here, 'fixtures/execution-thermometer-html/invalid-runtime-read/execution-thermometer.html'), '--expect-loop', 'L4'],
    revert: () => [
      join(here, 'fixtures/execution-thermometer-html/multi-loop/exec_identity.yaml'),
      join(here, 'fixtures/execution-thermometer-html/multi-loop/exec_metrics.json'),
      join(tmp, 'gm4-execution-thermometer.html'),
      '--expect-loop',
      'L4',
    ],
  },
  // GM5 — Gold Analysis Gate (gold missing evidence fails; complete gold fixture passes).
  {
    id: 'GM5 execution-thermometer-gold',
    harness: 'execution-thermometer-gold.mjs',
    violate: () => [join(here, 'fixtures/execution-thermometer-gold/invalid-missing-evidence/candidate.json'), '--expect', 'gold'],
    revert: () => [join(here, 'fixtures/execution-thermometer-gold/gold/candidate.json'), '--expect', 'gold'],
  },
  // GM6 — sanitized package builder (private path blocks; safe fixture emits local package).
  {
    id: 'GM6 execution-thermometer-package',
    harness: 'execution-thermometer-package.mjs',
    violate: () => [
      join(here, 'fixtures/execution-thermometer-package/unsafe-private-path/exec_identity.yaml'),
      join(here, 'fixtures/execution-thermometer-html/multi-loop/exec_metrics.json'),
      join(tmp, 'gm6-unsafe'),
    ],
    revert: () => [
      join(here, 'fixtures/execution-thermometer-html/multi-loop/exec_identity.yaml'),
      join(here, 'fixtures/execution-thermometer-html/multi-loop/exec_metrics.json'),
      join(tmp, 'gm6-safe'),
    ],
  },
  // GM6O — package overwrite requires a TES ownership marker for the same run/package contract.
  {
    id: 'GM6O execution-thermometer-package-overwrite-guard',
    harness: 'execution-thermometer-package.mjs',
    violate: () => [
      join(here, 'fixtures/execution-thermometer-html/multi-loop/exec_identity.yaml'),
      join(here, 'fixtures/execution-thermometer-html/multi-loop/exec_metrics.json'),
      outputRootWithUnownedPackage('gm6-unowned'),
    ],
    revert: () => [
      join(here, 'fixtures/execution-thermometer-html/multi-loop/exec_identity.yaml'),
      join(here, 'fixtures/execution-thermometer-html/multi-loop/exec_metrics.json'),
      outputRootWithOwnedPackage('gm6-owned'),
    ],
  },
  // GM7 — Share Gate (tuple drift cannot reuse approval; gold sanitized report prompts).
  {
    id: 'GM7 execution-thermometer-share-gate',
    harness: 'execution-thermometer-share-gate.mjs',
    violate: () => [
      join(here, 'fixtures/execution-thermometer-share-gate/tuple-mismatch/candidate.json'),
      '--expect-status',
      'approved_local_export',
    ],
    revert: () => [
      join(here, 'fixtures/execution-thermometer-share-gate/gold-shareable/candidate.json'),
      '--expect-status',
      'proposed_gold',
      '--expect-prompt',
      'true',
      '--expect-remote-action',
      'false',
    ],
  },
  // GM8 — GitHub export stays dry-run/local unless tuple-bound approval and remote lane exist.
  {
    id: 'GM8 execution-thermometer-github-export',
    harness: 'execution-thermometer-github-export.mjs',
    violate: () => [
      join(here, 'fixtures/execution-thermometer-github-export/dry-run/share-decision.json'),
      join(here, 'fixtures/execution-thermometer-github-export/dry-run/package'),
      '--destination-config',
      join(here, 'fixtures/execution-thermometer-github-export/dry-run/destination.json'),
      '--mode',
      'execute',
      '--expect-status',
      'draft_pr_opened',
    ],
    revert: () => [
      join(here, 'fixtures/execution-thermometer-github-export/dry-run/share-decision.json'),
      join(here, 'fixtures/execution-thermometer-github-export/dry-run/package'),
      '--destination-config',
      join(here, 'fixtures/execution-thermometer-github-export/dry-run/destination.json'),
      '--approval-record',
      join(here, 'fixtures/execution-thermometer-github-export/dry-run/approval.json'),
      '--expect-status',
      'dry_run_ready',
      '--expect-remote-action',
      'false',
    ],
  },
  // GM8P — public GitHub destinations are mechanically blocked before payload planning.
  {
    id: 'GM8P execution-thermometer-github-export-public-destination',
    harness: 'execution-thermometer-github-export.mjs',
    violate: () => [
      join(here, 'fixtures/execution-thermometer-github-export/dry-run/share-decision.json'),
      join(here, 'fixtures/execution-thermometer-github-export/dry-run/package'),
      '--destination-config',
      join(here, 'fixtures/execution-thermometer-github-export/public-destination/destination.json'),
      '--expect-status',
      'dry_run_ready',
    ],
    revert: () => [
      join(here, 'fixtures/execution-thermometer-github-export/dry-run/share-decision.json'),
      join(here, 'fixtures/execution-thermometer-github-export/dry-run/package'),
      '--destination-config',
      join(here, 'fixtures/execution-thermometer-github-export/public-destination/destination.json'),
      '--expect-status',
      'blocked_by_public_destination',
      '--expect-remote-action',
      'false',
    ],
  },
  // GM9 — Thermometer integration cannot rewrite Goal Maestro execution stop states.
  {
    id: 'GM9 execution-thermometer-integration',
    harness: 'execution-thermometer-integration.mjs',
    violate: () => [
      join(here, '../references/execution-loop-runner.md'),
      join(here, '../templates/maestral-goal-prompt.template.md'),
      join(here, 'fixtures/execution-thermometer-integration/state-namespace-invalid.json'),
      cursorRuntimeRuleArg(),
    ],
    revert: () => [
      join(here, '../references/execution-loop-runner.md'),
      join(here, '../templates/maestral-goal-prompt.template.md'),
      join(here, 'fixtures/execution-thermometer-integration/state-namespace-valid.json'),
      cursorRuntimeRuleArg(),
    ],
  },
  // GM9C — Cursor lazy runtime rule covers Thermometer without claiming fake skill parity.
  {
    id: 'GM9C execution-thermometer-cursor-lazy',
    harness: 'execution-thermometer-integration.mjs',
    violate: () => [
      join(here, '../references/execution-loop-runner.md'),
      join(here, '../templates/maestral-goal-prompt.template.md'),
      join(here, 'fixtures/execution-thermometer-integration/state-namespace-valid.json'),
      fixture('gm9c-bad-cursor.mdc', 'Cursor runtime capability without Execution Thermometer coverage.\n'),
    ],
    revert: () => [
      join(here, '../references/execution-loop-runner.md'),
      join(here, '../templates/maestral-goal-prompt.template.md'),
      join(here, 'fixtures/execution-thermometer-integration/state-namespace-valid.json'),
      cursorRuntimeRuleArg(),
    ],
  },
  // GM10 — User docs describe local report, UNPROVEN, opt-in sharing and fields.
  {
    id: 'GM10 execution-thermometer-docs',
    harness: 'execution-thermometer-docs.mjs',
    violate: gm10ViolateArgs,
    revert: gm10RevertArgs,
  },
  // GM11 — Adversarial Audit Heartbeat remains exact opt-in and read-only.
  {
    id: 'GM11 adversarial-audit-heartbeat-contract',
    harness: 'adversarial-audit-heartbeat-contract.mjs',
    violate: () => [join(here, 'fixtures/adversarial-audit-heartbeat/invalid-no-opt-in/fixture.json')],
    revert: () => [join(here, 'fixtures/adversarial-audit-heartbeat/valid/source/fixture.json')],
  },
  // GM12 — SPEC-001 linear pipeline blocks future SPEC work and pre-open evidence.
  {
    id: 'GM12 goal-maestro-p0-linear-pipeline',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12ViolateArgs,
    revert: gm12RevertArgs,
  },
  // GM12S2 — SPEC-002 pre-edit gate requires a durable artifact before loop/edit.
  {
    id: 'GM12S2 goal-maestro-p0-pre-edit-gate-missing',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec2MissingPreEditArgs,
    revert: gm12Spec2RevertArgs,
  },
  {
    id: 'GM12S2 goal-maestro-p0-pre-edit-gate-chronology',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec2LatePreEditArgs,
    revert: gm12Spec2RevertArgs,
  },
  // GM12S3 — SPEC-003 prompt enrichment packet must exist before execution and not echo the prompt.
  {
    id: 'GM12S3 goal-maestro-p0-prompt-enrichment-missing',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec3MissingPromptArgs,
    revert: gm12Spec3RevertArgs,
  },
  {
    id: 'GM12S3 goal-maestro-p0-prompt-enrichment-echo-only',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec3EchoPromptArgs,
    revert: gm12Spec3RevertArgs,
  },
  // GM12S4 — SPEC-004 document analysis packet must exist and map acceptance criteria before execution.
  {
    id: 'GM12S4 goal-maestro-p0-document-analysis-missing',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec4MissingDocumentAnalysisArgs,
    revert: gm12Spec4RevertArgs,
  },
  {
    id: 'GM12S4 goal-maestro-p0-document-analysis-acceptance-criteria',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec4MissingAcceptanceCriteriaArgs,
    revert: gm12Spec4RevertArgs,
  },
  // GM12S5 — SPEC-005 preserves declared SPEC units across execution and report surfaces.
  {
    id: 'GM12S5 goal-maestro-p0-spec-fidelity-missing-execution',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec5MissingExecutionArgs,
    revert: gm12Spec5RevertArgs,
  },
  {
    id: 'GM12S5 goal-maestro-p0-spec-fidelity-reported-drift',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec5ReportedDriftArgs,
    revert: gm12Spec5RevertArgs,
  },
  {
    id: 'GM12S5 goal-maestro-p0-spec-fidelity-audit-material',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec5AuditMaterialArgs,
    revert: gm12Spec5RevertArgs,
  },
  {
    id: 'GM12S5 goal-maestro-p0-spec-fidelity-merged-execution',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec5MergedExecutionArgs,
    revert: gm12Spec5RevertArgs,
  },
  {
    id: 'GM12S5 goal-maestro-p0-spec-fidelity-bounded-repair',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec5UnacceptedRepairArgs,
    revert: gm12Spec5AcceptedRepairArgs,
  },
  // GM12S6 — SPEC-006 Thermometer cannot hide unknown, missing, audit, or unproven execution semantics.
  {
    id: 'GM12S6 goal-maestro-p0-thermometer-fidelity-unknown-spec',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec6UnknownSpecArgs,
    revert: gm12Spec6RevertArgs,
  },
  {
    id: 'GM12S6 goal-maestro-p0-thermometer-fidelity-missing-material',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec6MissingMaterialArgs,
    revert: gm12Spec6RevertArgs,
  },
  {
    id: 'GM12S6 goal-maestro-p0-thermometer-fidelity-audit-material',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec6AuditMaterialArgs,
    revert: gm12Spec6RevertArgs,
  },
  {
    id: 'GM12S6 goal-maestro-p0-thermometer-fidelity-unproven-metrics',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec6UnprovenMetricsArgs,
    revert: gm12Spec6RevertArgs,
  },
  // GM12S7 — SPEC-007 ledger grammar blocks malformed material sections before Thermometer packaging.
  {
    id: 'GM12S7 goal-maestro-p0-ledger-grammar-malformed-heading',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec7MalformedHeadingArgs,
    revert: gm12Spec7RevertArgs,
  },
  {
    id: 'GM12S7 goal-maestro-p0-ledger-grammar-duplicate-spec-id',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec7DuplicateSpecIdArgs,
    revert: gm12Spec7RevertArgs,
  },
  {
    id: 'GM12S7 goal-maestro-p0-ledger-grammar-last-spec-overwrite',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec7AuditOverwriteArgs,
    revert: gm12Spec7RevertArgs,
  },
  {
    id: 'GM12S7 goal-maestro-p0-ledger-grammar-final-closeout-body',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec7NestedCloseoutArgs,
    revert: gm12Spec7RevertArgs,
  },
  // GM12S8 — SPEC-008 keeps ledger, metrics, receipt, HTML, checksum, and closeout coherent.
  {
    id: 'GM12S8 goal-maestro-p0-report-coherence-spec-id-drift',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec8SpecIdDriftArgs,
    revert: gm12Spec8RevertArgs,
  },
  {
    id: 'GM12S8 goal-maestro-p0-report-coherence-status-drift',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec8StatusDriftArgs,
    revert: gm12Spec8RevertArgs,
  },
  {
    id: 'GM12S8 goal-maestro-p0-report-coherence-evidence-hash-drift',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec8EvidenceHashDriftArgs,
    revert: gm12Spec8RevertArgs,
  },
  {
    id: 'GM12S8 goal-maestro-p0-report-coherence-unproven-closeout',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec8UnprovenCloseoutArgs,
    revert: gm12Spec8RevertArgs,
  },
  {
    id: 'GM12S8 goal-maestro-p0-report-coherence-checksum-mismatch',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec8ChecksumMismatchArgs,
    revert: gm12Spec8RevertArgs,
  },
  // GM12S9 — SPEC-009 prevents competing Thermometer packages for one loop.
  {
    id: 'GM12S9 goal-maestro-p0-package-hierarchy-unsorted-candidates',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec9UnsortedCandidatesArgs,
    revert: gm12Spec9RevertArgs,
  },
  {
    id: 'GM12S9 goal-maestro-p0-package-hierarchy-superseded-by',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec9MissingSupersededByArgs,
    revert: gm12Spec9RevertArgs,
  },
  {
    id: 'GM12S9 goal-maestro-p0-package-hierarchy-closeout-latest-only',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec9CloseoutHistoryLeakArgs,
    revert: gm12Spec9ExplicitHistoryArgs,
  },
  // GM12S10 — SPEC-010 makes report identity fields operational, not decorative.
  {
    id: 'GM12S10 goal-maestro-p0-report-identity-version',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec10VersionMismatchArgs,
    revert: gm12Spec10RevertArgs,
  },
  {
    id: 'GM12S10 goal-maestro-p0-report-identity-adapter',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec10KnownAdapterOtherArgs,
    revert: gm12Spec10RevertArgs,
  },
  {
    id: 'GM12S10 goal-maestro-p0-report-identity-installed-at',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec10MissingInstalledAtArgs,
    revert: gm12Spec10RevertArgs,
  },
  {
    id: 'GM12S10 goal-maestro-p0-report-identity-model-reason',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec10MissingModelReasonArgs,
    revert: gm12Spec10RevertArgs,
  },
  {
    id: 'GM12S10 goal-maestro-p0-report-identity-source-package',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec10MissingSourceIdentityArgs,
    revert: gm12Spec10RevertArgs,
  },
  // GM12S11 — SPEC-011 requires mapped scene coverage for visual UI/browser/rendered app evidence.
  {
    id: 'GM12S11 goal-maestro-p0-visual-evidence-artifact-class',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec11UnsupportedArtifactClassArgs,
    revert: gm12Spec11RevertArgs,
  },
  {
    id: 'GM12S11 goal-maestro-p0-visual-evidence-initial-only',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec11InitialOnlyArgs,
    revert: gm12Spec11RevertArgs,
  },
  {
    id: 'GM12S11 goal-maestro-p0-visual-evidence-terminal-only',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec11TerminalOnlyArgs,
    revert: gm12Spec11RevertArgs,
  },
  {
    id: 'GM12S11 goal-maestro-p0-visual-evidence-state-map',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec11UnmappedScreenshotArgs,
    revert: gm12Spec11RevertArgs,
  },
  {
    id: 'GM12S11 goal-maestro-p0-visual-evidence-active-domain-objects',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec11ActiveWithoutDomainObjectsArgs,
    revert: gm12Spec11RevertArgs,
  },
  {
    id: 'GM12S11 goal-maestro-p0-visual-evidence-responsive',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec11MissingResponsiveArgs,
    revert: gm12Spec11RevertArgs,
  },
  // GM12S12 — SPEC-012 requires semantic proof, not only non-blank screenshots.
  {
    id: 'GM12S12 goal-maestro-p0-visual-semantic-pixel-floor',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec12MissingPixelFloorArgs,
    revert: gm12Spec12RevertArgs,
  },
  {
    id: 'GM12S12 goal-maestro-p0-visual-semantic-state-metadata',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec12MissingStateMetadataArgs,
    revert: gm12Spec12RevertArgs,
  },
  {
    id: 'GM12S12 goal-maestro-p0-visual-semantic-objects',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec12MissingObjectsArgs,
    revert: gm12Spec12RevertArgs,
  },
  {
    id: 'GM12S12 goal-maestro-p0-visual-semantic-score-status',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec12MissingScoreStatusArgs,
    revert: gm12Spec12RevertArgs,
  },
  {
    id: 'GM12S12 goal-maestro-p0-visual-semantic-layout-area',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec12MissingLayoutAreaArgs,
    revert: gm12Spec12RevertArgs,
  },
  {
    id: 'GM12S12 goal-maestro-p0-visual-semantic-interaction-result',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec12MissingInteractionResultArgs,
    revert: gm12Spec12RevertArgs,
  },
  // GM12S13 — SPEC-013 standardizes browser-metrics.json across Codex, Claude, and Cursor sources.
  {
    id: 'GM12S13 goal-maestro-p0-browser-metrics-schema-host-minimal',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec13HostMinimalArgs,
    revert: gm12Spec13RevertArgs,
  },
  {
    id: 'GM12S13 goal-maestro-p0-browser-metrics-schema-status',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec13MissingStatusArgs,
    revert: gm12Spec13RevertArgs,
  },
  {
    id: 'GM12S13 goal-maestro-p0-browser-metrics-schema-source-coverage',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec13MissingSourceCoverageArgs,
    revert: gm12Spec13RevertArgs,
  },
  {
    id: 'GM12S13 goal-maestro-p0-browser-metrics-schema-state-transitions',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec13MissingStateTransitionsArgs,
    revert: gm12Spec13RevertArgs,
  },
  {
    id: 'GM12S13 goal-maestro-p0-browser-metrics-schema-restart-evidence',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec13MissingRestartEvidenceArgs,
    revert: gm12Spec13RevertArgs,
  },
  {
    id: 'GM12S13 goal-maestro-p0-browser-metrics-schema-domain-metrics',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec13MissingDomainMetricsArgs,
    revert: gm12Spec13RevertArgs,
  },
  // GM12S14 — SPEC-014 proves the installed TES baseline predates material execution.
  {
    id: 'GM12S14 goal-maestro-p0-install-chronology-after-material',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec14InstallAfterMaterialArgs,
    revert: gm12Spec14RevertArgs,
  },
  {
    id: 'GM12S14 goal-maestro-p0-install-chronology-installed-version',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec14MissingInstalledVersionArgs,
    revert: gm12Spec14RevertArgs,
  },
  {
    id: 'GM12S14 goal-maestro-p0-install-chronology-git-head',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec14MissingGitHeadArgs,
    revert: gm12Spec14RevertArgs,
  },
  {
    id: 'GM12S14 goal-maestro-p0-install-chronology-baseline-commit',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec14MissingBaselineCommitArgs,
    revert: gm12Spec14RevertArgs,
  },
  {
    id: 'GM12S14 goal-maestro-p0-install-chronology-material-timestamps',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec14MissingMaterialTimestampsArgs,
    revert: gm12Spec14RevertArgs,
  },
  {
    id: 'GM12S14 goal-maestro-p0-install-chronology-classified-later-reinstall',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec14InstallAfterMaterialArgs,
    revert: gm12Spec14ClassifiedLaterReinstallArgs,
  },
  // GM12S15 — SPEC-015 separates manual commits from pre-commit enforcement claims.
  {
    id: 'GM12S15 goal-maestro-p0-commit-enforcement-precommit-evidence',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec15MissingPrecommitEvidenceArgs,
    revert: gm12Spec15RevertArgs,
  },
  {
    id: 'GM12S15 goal-maestro-p0-commit-enforcement-manual-claim',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec15ManualClaimsEnforcedArgs,
    revert: gm12Spec15HonestManualArgs,
  },
  {
    id: 'GM12S15 goal-maestro-p0-commit-enforcement-mode',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec15MissingCommitModeArgs,
    revert: gm12Spec15RevertArgs,
  },
  {
    id: 'GM12S15 goal-maestro-p0-commit-enforcement-precommit-installed',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec15ManualClaimsEnforcedArgs,
    revert: gm12Spec15PrecommitEnforcedArgs,
  },
  // GM12S16 — SPEC-016 classifies Git repository admission before execution.
  {
    id: 'GM12S16 goal-maestro-p0-git-admission-missing-repository',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec16MissingRepoNoStopArgs,
    revert: gm12Spec16NeedsGitRepositoryArgs,
  },
  {
    id: 'GM12S16 goal-maestro-p0-git-admission-silent-init',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec16SilentGitInitArgs,
    revert: gm12Spec16AuthorizedGitInitArgs,
  },
  {
    id: 'GM12S16 goal-maestro-p0-git-admission-baseline-classification',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec16MissingBaselineClassificationArgs,
    revert: gm12Spec16RevertArgs,
  },
  // GM12S17 — SPEC-017 classifies tracked, runtime-only, ignored, and intentionally-untracked evidence.
  {
    id: 'GM12S17 goal-maestro-p0-evidence-tracking-class-coverage',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec17MissingClassArgs,
    revert: gm12Spec17RevertArgs,
  },
  {
    id: 'GM12S17 goal-maestro-p0-evidence-tracking-untracked-required',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec17UntrackedUnclassifiedArgs,
    revert: gm12Spec17RuntimeOnlyArgs,
  },
  {
    id: 'GM12S17 goal-maestro-p0-evidence-tracking-clean-claim',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec17CleanClaimUnclassifiedArgs,
    revert: gm12Spec17RuntimeOnlyArgs,
  },
  // GM12S18 — SPEC-018 records Flash-Fry operational status without inventing status-only commands.
  {
    id: 'GM12S18 goal-maestro-p0-flash-fry-status-present',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec18MissingStatusArgs,
    revert: gm12Spec18RevertArgs,
  },
  {
    id: 'GM12S18 goal-maestro-p0-flash-fry-ran-evidence',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec18RanMissingEvidenceArgs,
    revert: gm12Spec18RevertArgs,
  },
  {
    id: 'GM12S18 goal-maestro-p0-flash-fry-not-configured-adjusted',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec18NotConfiguredNoAdjustmentArgs,
    revert: gm12Spec18NotConfiguredAdjustedArgs,
  },
  {
    id: 'GM12S18 goal-maestro-p0-flash-fry-no-status-only-command',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec18NewCommandArgs,
    revert: gm12Spec18RevertArgs,
  },
  // GM12S19 — SPEC-019 records execution lenses and evidence for score citations.
  {
    id: 'GM12S19 goal-maestro-p0-lens-ledger-present',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec19MissingLedgerArgs,
    revert: gm12Spec19RevertArgs,
  },
  {
    id: 'GM12S19 goal-maestro-p0-lens-ledger-coverage',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec19MissingLensArgs,
    revert: gm12Spec19RevertArgs,
  },
  {
    id: 'GM12S19 goal-maestro-p0-lens-ledger-impact',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec19MissingImpactArgs,
    revert: gm12Spec19RevertArgs,
  },
  {
    id: 'GM12S19 goal-maestro-p0-lens-ledger-score-evidence',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec19ScoreWithoutEvidenceArgs,
    revert: gm12Spec19ScoreWithEvidenceArgs,
  },
  // GM12S20 — SPEC-020 records cloud/external lookup decisions and authorization.
  {
    id: 'GM12S20 goal-maestro-p0-cloud-search-status-present',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec20MissingStatusArgs,
    revert: gm12Spec20RevertArgs,
  },
  {
    id: 'GM12S20 goal-maestro-p0-cloud-search-reason',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec20MissingReasonArgs,
    revert: gm12Spec20RevertArgs,
  },
  {
    id: 'GM12S20 goal-maestro-p0-cloud-search-authorization',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec20UnauthorizedRunArgs,
    revert: gm12Spec20RanAuthorizedArgs,
  },
  {
    id: 'GM12S20 goal-maestro-p0-cloud-search-redaction',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec20MissingRedactionArgs,
    revert: gm12Spec20RanAuthorizedArgs,
  },
  // GM12S21 — SPEC-021 records LLM cache/cost telemetry and qualifies efficiency claims.
  {
    id: 'GM12S21 goal-maestro-p0-llm-cache-cost-telemetry-present',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec21MissingTelemetryArgs,
    revert: gm12Spec21RevertArgs,
  },
  {
    id: 'GM12S21 goal-maestro-p0-llm-cache-cost-fields-recorded',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec21MissingFieldArgs,
    revert: gm12Spec21RevertArgs,
  },
  {
    id: 'GM12S21 goal-maestro-p0-llm-cache-cost-missing-unproven-not-zero',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec21ZeroedMissingFieldArgs,
    revert: gm12Spec21UnprovenQualifiedArgs,
  },
  {
    id: 'GM12S21 goal-maestro-p0-llm-cache-cost-efficiency-qualified',
    harness: 'goal-maestro-p0-harness.mjs',
    violate: gm12Spec21UnqualifiedEfficiencyArgs,
    revert: gm12Spec21UnprovenQualifiedArgs,
  },
  // META-PANEL — SPEC-004: o painel REJEITA diversidade vacuosa (refutadores-clone).
  // violate: refutadores com lens diferentes mas CORPOS idênticos → panel-diversity DEVE falhar (exit 1).
  // revert: refutadores com corpos distintos → exit 0.
  {
    id: 'META panel-diversity',
    harness: 'panel-diversity.mjs',
    violate: () => [fixture('mp-clones.json', JSON.stringify({ oracles: [{ axis: 'p', command: 'true', refuters: [
      { lens: 'a', mutate: 'X', revert: 'Y', decoy_mutate: 'Z' },
      { lens: 'b', mutate: 'X', revert: 'Y', decoy_mutate: 'Z' },
    ] }] }))],
    revert: () => [fixture('mp-distinct.json', JSON.stringify({ oracles: [{ axis: 'p', command: 'true', refuters: [
      { lens: 'a', mutate: 'X1', revert: 'Y1', decoy_mutate: 'Z1' },
      { lens: 'b', mutate: 'X2', revert: 'Y2', decoy_mutate: 'Z2' },
    ] }] }))],
  },
  // B2 — api lint evidence (textual: provado por grep no skill, não harness; verificado no closeout)

  // ─── DOMAIN WALLS (SPEC-003..018) — node-puro {violate,revert}; dep-pesada/não-det +blocked (exit 2) ───
  // Database
  { id: 'DB1 migration-reversible', harness: 'db-migration-reversible.mjs',
    violate: () => [fixture('db1b.json', JSON.stringify({ initial: { users: [{ id: 1 }] }, migrations: [{ id: 'm', up: { add_field: { table: 'users', field: 'e', default: null } } }] }))],
    revert: () => [fixture('db1g.json', JSON.stringify({ initial: { users: [{ id: 1 }] }, migrations: [{ id: 'm', up: { add_field: { table: 'users', field: 'e', default: null } }, down: { drop_field: { table: 'users', field: 'e' } } }] }))] },
  { id: 'DB2 tx-idempotency', harness: 'tx-idempotency.mjs',
    violate: () => [fixture('db2b.json', JSON.stringify({ initial: { rows: [] }, ops: [{ id: 'o', op: { delete: {} } }] }))],
    revert: () => [fixture('db2g.json', JSON.stringify({ initial: { rows: [] }, ops: [{ id: 'o', op: { insert: { table: 'rows', key: 'id', value: { id: 1 } } } }] }))] },
  { id: 'DB3 referential-integrity', harness: 'referential-integrity.mjs',
    violate: () => [fixture('db3b.json', JSON.stringify({ tables: { users: [{ id: 1 }], orders: [{ id: 9, user_id: 99 }] }, fks: [{ table: 'orders', field: 'user_id', references: 'users', ref_field: 'id' }] }))],
    revert: () => [fixture('db3g.json', JSON.stringify({ tables: { users: [{ id: 1 }], orders: [{ id: 9, user_id: 1 }] }, fks: [{ table: 'orders', field: 'user_id', references: 'users', ref_field: 'id' }] }))] },
  { id: 'DB4 batch-reconcile', harness: 'batch-reconcile.mjs',
    violate: () => [fixture('db4b.json', JSON.stringify({ input_count: 1000, output_count: 950, skipped: [] }))],
    revert: () => [fixture('db4g.json', JSON.stringify({ input_count: 1000, output_count: 950, skipped: [{ reason: 'timeout', count: 50 }] }))] },
  // Financeiro
  { id: 'FIN1 double-entry', harness: 'ledger-double-entry.mjs',
    violate: () => [fixture('f1b.json', JSON.stringify({ entries: [{ tx: 't', account: 'c', debit: 100, credit: 0, status: 'COMMITTED' }] }))],
    revert: () => [fixture('f1g.json', JSON.stringify({ entries: [{ tx: 't', account: 'c', debit: 100, credit: 0, status: 'COMMITTED' }, { tx: 't', account: 'r', debit: 0, credit: 100, status: 'COMMITTED' }] }))] },
  { id: 'FIN2 payment-idempotency', harness: 'payment-idempotency.mjs',
    violate: () => [fixture('f2b.json', JSON.stringify({ charges: [{ idempotency_key: 'k', charge_id: 'a' }, { idempotency_key: 'k', charge_id: 'b' }] }))],
    revert: () => [fixture('f2g.json', JSON.stringify({ charges: [{ idempotency_key: 'k', charge_id: 'a' }, { idempotency_key: 'k', charge_id: 'a' }] }))] },
  { id: 'FIN3 decimal-precision', harness: 'decimal-precision.mjs',
    violate: () => [fixture('f3b.ts', 'const t = parseFloat(amount);\n')],
    revert: () => [fixture('f3g.ts', 'const t = Decimal(amountCents);\n')] },
  { id: 'FIN4 audit-trail-immutable', harness: 'audit-trail-immutable.mjs',
    violate: () => [fixture('f4b.json', JSON.stringify({ operations: [{ type: 'DELETE', table: 'audit_log' }], txs: ['t'], trail_txs: ['t'] }))],
    revert: () => [fixture('f4g.json', JSON.stringify({ operations: [{ type: 'INSERT', table: 'audit_log' }], txs: ['t'], trail_txs: ['t'] }))] },
  // LLM
  { id: 'LLM1 eval-coverage', harness: 'eval-coverage.mjs',
    violate: () => [fixture('l1b.json', JSON.stringify({ prompts: ['p'], evals: [] }))],
    revert: () => [fixture('l1g.json', JSON.stringify({ prompts: ['p'], evals: [{ prompt: 'p', expected: 'x' }] }))] },
  { id: 'LLM2 token-budget', harness: 'token-budget.mjs',
    violate: () => [fixture('l2b.json', JSON.stringify({ budget: 50000, samples: [{ id: 'r', prompt_tokens: 40000, completion_tokens: 15000 }] }))],
    revert: () => [fixture('l2g.json', JSON.stringify({ budget: 50000, samples: [{ id: 'r', prompt_tokens: 1200, completion_tokens: 800 }] }))] },
  { id: 'LLM3 tool-reachability', harness: 'tool-reachability.mjs',
    violate: () => [fixture('l3b.json', JSON.stringify({ tools: ['t'], eval_traces: [] }))],
    revert: () => [fixture('l3g.json', JSON.stringify({ tools: ['t'], eval_traces: [{ case: 'c', tool_calls: ['t'] }] }))] },
  { id: 'LLM4 rag-relevance', harness: 'rag-relevance.mjs', klass: 'non-det',
    violate: () => [fixture('l4b.json', JSON.stringify({ floor: 0.7, frozen_scores: [{ query: 'q', top1_score: 0.62 }] }))],
    revert: () => [fixture('l4g.json', JSON.stringify({ floor: 0.7, frozen_scores: [{ query: 'q', top1_score: 0.82 }] }))],
    blocked: () => [fixture('l4k.json', JSON.stringify({ floor: 0.7, frozen_scores: [] }))] },
  // UX
  { id: 'UX3 i18n-coverage', harness: 'i18n-coverage.mjs',
    violate: () => [fixture('u3b.json', JSON.stringify({ fallback: 'pt', floor: 0.9, keys: ['a', 'b'], translations: { pt: { a: 'A' } } }))],
    revert: () => [fixture('u3g.json', JSON.stringify({ fallback: 'pt', floor: 0.9, keys: ['a', 'b'], translations: { pt: { a: 'A', b: 'B' } } }))] },
  { id: 'UX1 responsive-check', harness: 'responsive-check.mjs', klass: 'dep-heavy',
    violate: () => [fixture('u1b.json', JSON.stringify({ playwright_available: true, viewports: [{ width: 375, overflow: true }, { width: 768, overflow: false }, { width: 1440, overflow: false }] }))],
    revert: () => [fixture('u1g.json', JSON.stringify({ playwright_available: true, viewports: [{ width: 375, overflow: false }, { width: 768, overflow: false }, { width: 1440, overflow: false }] }))],
    blocked: () => [fixture('u1k.json', JSON.stringify({ playwright_available: false }))] },
  { id: 'UX2 a11y-audit', harness: 'a11y-audit.mjs', klass: 'dep-heavy',
    violate: () => [fixture('u2b.json', JSON.stringify({ axe_available: true, violations: [{ id: 'color-contrast' }] }))],
    revert: () => [fixture('u2g.json', JSON.stringify({ axe_available: true, violations: [] }))],
    blocked: () => [fixture('u2k.json', JSON.stringify({ axe_available: false }))] },
  { id: 'UX4 web-vitals', harness: 'web-vitals.mjs', klass: 'dep-heavy',
    violate: () => [fixture('u4b.json', JSON.stringify({ lighthouse_available: true, lcp_s: 3.5, cls: 0.05, inp_ms: 150 }))],
    revert: () => [fixture('u4g.json', JSON.stringify({ lighthouse_available: true, lcp_s: 2.1, cls: 0.05, inp_ms: 150 }))],
    blocked: () => [fixture('u4k.json', JSON.stringify({ lighthouse_available: false }))] },
];

function gitHash(path) {
  return execSync(`git hash-object "${path}"`, { stdio: 'pipe' }).toString().trim();
}

// Gerador de PNG mínimo (RGB 8-bit) para o C4.
import { deflateSync } from 'node:zlib';
function crc32(buf) { let c = ~0; for (let i = 0; i < buf.length; i++) { c ^= buf[i]; for (let k = 0; k < 8; k++) c = (c >>> 1) ^ (0xEDB88320 & -(c & 1)); } return ~c >>> 0; }
function pngChunk(type, data) { const t = Buffer.from(type, 'ascii'); const len = Buffer.alloc(4); len.writeUInt32BE(data.length); const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(Buffer.concat([t, data]))); return Buffer.concat([len, t, data, crc]); }
function makePng(name, fill) {
  const w = 32, h = 32;
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4); ihdr[8] = 8; ihdr[9] = 2;
  const stride = w * 3; const raw = Buffer.alloc(h * (stride + 1));
  for (let y = 0; y < h; y++) { raw[y * (stride + 1)] = 0; for (let x = 0; x < w; x++) { const o = y * (stride + 1) + 1 + x * 3; const [r, g, b] = fill(x, y); raw[o] = r; raw[o + 1] = g; raw[o + 2] = b; } }
  const png = Buffer.concat([sig, pngChunk('IHDR', ihdr), pngChunk('IDAT', deflateSync(raw)), pngChunk('IEND', Buffer.alloc(0))]);
  const p = join(tmp, name); writeFileSync(p, png); return p;
}

// Paredes de domínio cujo input é JSON (testáveis contra `{}` degenerado). As que recebem
// um path de source (.ts/.js para grep) ficam fora — têm seu próprio teste de presença.
const JSON_INPUT_WALLS = new Set([
  'db-migration-reversible.mjs', 'tx-idempotency.mjs', 'referential-integrity.mjs', 'batch-reconcile.mjs',
  'ledger-double-entry.mjs', 'payment-idempotency.mjs', 'audit-trail-immutable.mjs',
  'eval-coverage.mjs', 'token-budget.mjs', 'tool-reachability.mjs',
  'i18n-coverage.mjs',
]);

let failed = 0;
console.log('# mutation-suite — paredes executáveis (base + domínio). B2 textual no closeout.');
console.log('# node-puro: violação(≠0)+reverte(0). dep-pesada/não-det: também blocked(=2).\n');
for (const w of WALLS) {
  const vCode = runHarness(w.harness, w.violate());
  const rCode = runHarness(w.harness, w.revert());
  const fires = vCode === 1; // violação deve dar FAIL (1), não BLOCKED (2)
  const reverts = rCode === 0;
  let ok = fires && reverts;
  let blkNote = '';
  if (w.blocked) {
    const bCode = runHarness(w.harness, w.blocked());
    const blocksHonestly = bCode === 2; // BLOCKED-provado = exit 2 (não 0=PASS-falso, não 1=quebrado)
    // Ataque do Executive Stop Audit: dependência OMITIDA (não explicitamente false) também
    // deve BLOCKED (exit 2), nunca PASS-por-omissão. Prova: fixture vazio {} → exit 2.
    const iCode = runHarness(w.harness, [fixture(`${w.id.split(' ')[0]}-implicit.json`, '{}')]);
    const blocksOnOmission = iCode === 2;
    ok = ok && blocksHonestly && blocksOnOmission;
    blkNote = ` blocked:exit${bCode}${blocksHonestly ? '✓' : '✗(devia=2)'} omit:exit${iCode}${blocksOnOmission ? '✓' : '✗(devia=2,PASS-por-omissão!)'}`;
  } else if (JSON_INPUT_WALLS.has(w.harness)) {
    // Defesa universal (revisão profunda): paredes de domínio que recebem JSON devem REJEITAR
    // input degenerado `{}` (exit≠0), nunca vacuous-PASS. Pega .every()/.filter() em vazio,
    // campo-ausente-como-zero. Harnesses que recebem um path de SOURCE (.ts/.js grep) ficam fora —
    // `{}` não é o vetor de ataque deles (eles têm seu próprio teste de presença).
    const dCode = runHarness(w.harness, [fixture(`${w.id.split(' ')[0]}-degen.json`, '{}')]);
    const rejectsDegenerate = dCode !== 0;
    ok = ok && rejectsDegenerate;
    blkNote = ` degen:exit${dCode}${rejectsDegenerate ? '✓' : '✗(devia≠0,vacuous-PASS!)'}`;
  }
  if (!ok) failed++;
  console.log(`  [${ok ? 'PASS' : 'FAIL'}] ${w.id} — viol:exit${vCode}${fires ? '✓' : '✗(devia=1)'} rev:exit${rCode}${reverts ? '✓' : '✗(devia=0)'}${blkNote}`);
}
console.log(`\n# ${WALLS.length - failed}/${WALLS.length} paredes convergem (dispara+reverte; dep/não-det também bloqueia-honestamente)`);
process.exit(failed === 0 ? 0 : 1);
