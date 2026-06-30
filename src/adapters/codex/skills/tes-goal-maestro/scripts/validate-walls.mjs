// SPEC-012 — Mutation-suite das 7 famílias (12 testes-de-violação do placar).
// Para cada parede, monta uma fixture de VIOLAÇÃO em /tmp, roda o harness-dono e exige
// que ele DISPARE (exit≠0); depois monta a fixture REVERTIDA e exige PASS (exit 0).
// Uma parede só conta como "feita" quando dispara sob violação E passa quando revertida.
// Conduzido por agente independente (D1): este script não escreve nenhum dos harnesses.
//
//   node scripts/validate-walls.mjs
//
// Exit≠0 se QUALQUER parede falhar o par (não-disparo sob violação, ou não-passe ao reverter).

import { execFileSync, execSync } from 'node:child_process';
import { existsSync, mkdirSync, writeFileSync, mkdtempSync } from 'node:fs';
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
