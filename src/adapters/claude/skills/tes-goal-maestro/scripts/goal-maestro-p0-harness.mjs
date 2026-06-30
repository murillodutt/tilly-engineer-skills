// SPEC-001/SPEC-002/SPEC-003/SPEC-004/SPEC-005/SPEC-006/SPEC-007/SPEC-008 Goal Maestro P0 execution harness.
// Validates a synthetic execute-loop event fixture for one-active-SPEC order,
// post-open evidence, oracle proof, local commit status, and parent validation
// before the next SPEC can open. SPEC-002 fixtures opt into durable pre-edit
// artifact validation with pre_edit_gate_required:true. SPEC-003 fixtures opt
// into prompt enrichment packet validation with prompt_enrichment_packet_required:true.
// SPEC-004 fixtures opt into document analysis packet validation with
// document_analysis_packet_required:true.
// SPEC-005 fixtures opt into SPEC fidelity validation with spec_fidelity_required:true.
// SPEC-006 fixtures opt into Thermometer fidelity validation with
// thermometer_fidelity_required:true.
// SPEC-007 fixtures opt into canonical ledger grammar validation with
// ledger_grammar_required:true.
// SPEC-008 fixtures opt into report surface coherence validation with
// report_coherence_required:true.
//
//   node scripts/goal-maestro-p0-harness.mjs <linear-pipeline-fixture.json>

import { readText, runChecks } from './lib/harness.mjs';

const LINEAR_STOP_STATE = 'NEEDS_LINEAR_SPEC_PIPELINE';
const PRE_EDIT_STOP_STATE = 'NEEDS_PRE_EDIT_GATE_ARTIFACT';
const PROMPT_ENRICHMENT_STOP_STATE = 'NEEDS_PROMPT_ENRICHMENT_PACKET';
const DOCUMENT_ANALYSIS_STOP_STATE = 'NEEDS_DOCUMENT_ANALYSIS';
const SPEC_FIDELITY_STOP_STATE = 'NEEDS_SPEC_FIDELITY';
const THERMOMETER_FIDELITY_STOP_STATE = 'NEEDS_THERMOMETER_FIDELITY';
const LEDGER_GRAMMAR_STOP_STATE = 'NEEDS_LEDGER_GRAMMAR';
const REPORT_COHERENCE_STOP_STATE = 'NEEDS_REPORT_COHERENCE';
const PRE_EDIT_CONTRACT = 'goal-maestro-p0-pre-edit-gate';
const PROMPT_ENRICHMENT_CONTRACT = 'goal-maestro-p0-prompt-enrichment-packet';
const DOCUMENT_ANALYSIS_CONTRACT = 'goal-maestro-p0-document-analysis-packet';
const SPEC_FIDELITY_CONTRACT = 'goal-maestro-p0-spec-fidelity';
const THERMOMETER_FIDELITY_CONTRACT = 'goal-maestro-p0-thermometer-fidelity';
const LEDGER_GRAMMAR_CONTRACT = 'goal-maestro-p0-ledger-grammar';
const REPORT_COHERENCE_CONTRACT = 'goal-maestro-p0-report-coherence';
const PRE_EDIT_EVENT_TYPE = 'pre_edit_gate_artifact';
const PROMPT_ENRICHMENT_EVENT_TYPE = 'prompt_enrichment_packet';
const DOCUMENT_ANALYSIS_EVENT_TYPE = 'document_analysis_packet';
const MATERIAL_SPEC_HEADING_RE = /^### (SPEC-\d{3}) - (.+\S)$/;
const REPORT_COHERENCE_FIELDS = ['spec_ids', 'final_status', 'report_status', 'share_status', 'evidence_hashes', 'unproven_count'];
const EVENT_TYPES = new Set([
  PRE_EDIT_EVENT_TYPE,
  PROMPT_ENRICHMENT_EVENT_TYPE,
  DOCUMENT_ANALYSIS_EVENT_TYPE,
  'open_spec',
  'implement',
  'evidence',
  'oracle_result',
  'local_commit_status',
  'parent_validation',
]);
const REQUIRED_STEPS = ['evidence', 'oracle_result', 'local_commit_status', 'parent_validation'];
const REQUIRED_STEP_LABELS = {
  evidence: 'post-open evidence',
  oracle_result: 'passing oracle result',
  local_commit_status: 'LOCAL_COMMITTED status',
  parent_validation: 'passing parent validation',
};
const DEFAULT_REQUIRED_EXECUTION_FIDELITY_FIELDS = [
  'thermometer.spec_results',
  'thermometer.loops.spec_ids',
  'thermometer.latest_loop.spec_ids',
  'thermometer.final_status.goal_maestro_execution_state',
  'oracle_status',
];

const [fixturePath] = process.argv.slice(2);
if (!fixturePath) {
  console.error('usage: node scripts/goal-maestro-p0-harness.mjs <linear-pipeline-fixture.json>');
  process.exit(2);
}

let fixture;
try {
  fixture = JSON.parse(readText(fixturePath));
} catch (error) {
  console.error(`linear pipeline fixture JSON invalid: ${error.message}`);
  process.exit(2);
}

if (!isPlainObject(fixture) || !Array.isArray(fixture.declared_specs) || !Array.isArray(fixture.events)) {
  console.error('linear pipeline fixture must contain declared_specs[] and events[]');
  process.exit(2);
}

const declaredSpecs = fixture.declared_specs;
const events = fixture.events;
const preEditGateRequired = requiresPreEditGate(fixture);
const promptEnrichmentPacketRequired = requiresPromptEnrichmentPacket(fixture);
const documentAnalysisPacketRequired = requiresDocumentAnalysisPacket(fixture);
const specFidelityRequired = requiresSpecFidelityGate(fixture);
const thermometerFidelityRequired = requiresThermometerFidelityGate(fixture);
const ledgerGrammarRequired = requiresLedgerGrammarGate(fixture);
const reportCoherenceRequired = requiresReportCoherenceGate(fixture);
const acceptedBoundedRepairUnits = acceptedBoundedRepairUnitIds(fixture);
const preEditGateEvents = [];
const promptEnrichmentPacketEvents = [];
const documentAnalysisPacketEvents = [];
const materialOpenedSpecIds = [];
const materialExecutedSpecIds = [];
const materialCommittedSpecIds = [];
let firstLoopStartIndex = null;
let firstMaterialEditIndex = null;
const specStates = new Map();
for (const specId of declaredSpecs) {
  specStates.set(specId, {
    opened: false,
    openIndex: null,
    openedAt: null,
    executed: false,
    complete: {
      evidence: false,
      oracle_result: false,
      local_commit_status: false,
      parent_validation: false,
    },
  });
}

const checks = [
  {
    name: 'declared SPEC queue is unique',
    pass: new Set(declaredSpecs).size === declaredSpecs.length,
    detail: new Set(declaredSpecs).size === declaredSpecs.length ? undefined : `${LINEAR_STOP_STATE}: duplicate SPEC id in declared_specs`,
  },
  {
    name: 'declared SPEC queue is strict and consecutive',
    pass: isStrictConsecutiveSpecQueue(declaredSpecs),
    detail: isStrictConsecutiveSpecQueue(declaredSpecs) ? undefined : `${LINEAR_STOP_STATE}: declared_specs must be SPEC-NNN in consecutive order`,
  },
  {
    name: 'event stream is present',
    pass: events.length > 0,
    detail: events.length > 0 ? undefined : `${LINEAR_STOP_STATE}: no pipeline events were provided`,
  },
];

let activeSpec = null;
let nextOpenIndex = 0;

for (const [eventIndex, event] of events.entries()) {
  if (!isPlainObject(event)) {
    fail(`event ${eventIndex + 1} shape`, 'event must be an object');
    continue;
  }

  const eventType = event.type;
  const specId = event.spec_id;

  if (!EVENT_TYPES.has(eventType)) {
    fail(`event ${eventIndex + 1} type`, `unknown event type ${String(eventType)}`);
    continue;
  }

  if (specFidelityRequired) {
    observeSpecFidelityEvent(eventIndex, event);
  }

  if (!specStates.has(specId)) {
    if (isAcceptedBoundedRepairUnit(specId)) {
      continue;
    }
    fail(`event ${eventIndex + 1} spec`, `event references undeclared SPEC ${String(specId)}`);
    continue;
  }

  if (eventType === PRE_EDIT_EVENT_TYPE) {
    observePreEditGate(eventIndex, event);
    continue;
  }

  if (eventType === PROMPT_ENRICHMENT_EVENT_TYPE) {
    observePromptEnrichmentPacket(eventIndex, event);
    continue;
  }

  if (eventType === DOCUMENT_ANALYSIS_EVENT_TYPE) {
    observeDocumentAnalysisPacket(eventIndex, event);
    continue;
  }

  if (eventType === 'open_spec') {
    if (firstLoopStartIndex === null) firstLoopStartIndex = eventIndex;
    openSpec(eventIndex, event);
    continue;
  }

  if (eventType === 'implement' && firstMaterialEditIndex === null) {
    firstMaterialEditIndex = eventIndex;
  }
  applySpecEvent(eventIndex, event);
}

for (const specId of declaredSpecs) {
  const state = specStates.get(specId);
  checks.push({
    name: `${specId} opened`,
    pass: state.opened,
    detail: state.opened ? undefined : `${LINEAR_STOP_STATE}: ${specId} never opened`,
  });

  for (const step of REQUIRED_STEPS) {
    checks.push({
      name: `${specId} ${step} after open`,
      pass: state.complete[step],
      detail: state.complete[step] ? undefined : `${LINEAR_STOP_STATE}: ${specId} lacks ${REQUIRED_STEP_LABELS[step]} after ACTIVE_SPEC opened`,
    });
  }
}

if (preEditGateRequired) {
  addPreEditGateChecks();
}
if (promptEnrichmentPacketRequired) {
  addPromptEnrichmentPacketChecks();
}
if (documentAnalysisPacketRequired) {
  addDocumentAnalysisPacketChecks();
}
if (specFidelityRequired) {
  addSpecFidelityChecks();
}
if (ledgerGrammarRequired) {
  addLedgerGrammarChecks();
}
if (reportCoherenceRequired) {
  addReportCoherenceChecks();
}
if (thermometerFidelityRequired) {
  addThermometerFidelityChecks();
}

const harnessTitle = reportCoherenceRequired
  ? `SPEC-001+SPEC-002+SPEC-003+SPEC-004+SPEC-005+SPEC-006+SPEC-007+SPEC-008 goal-maestro-p0-report-coherence (${LINEAR_STOP_STATE}/${REPORT_COHERENCE_STOP_STATE})`
  : ledgerGrammarRequired
  ? `SPEC-001+SPEC-002+SPEC-003+SPEC-004+SPEC-005+SPEC-006+SPEC-007 goal-maestro-p0-ledger-grammar (${LINEAR_STOP_STATE}/${LEDGER_GRAMMAR_STOP_STATE})`
  : thermometerFidelityRequired
  ? `SPEC-001+SPEC-002+SPEC-003+SPEC-004+SPEC-005+SPEC-006 goal-maestro-p0-thermometer-fidelity (${LINEAR_STOP_STATE}/${THERMOMETER_FIDELITY_STOP_STATE})`
  : specFidelityRequired
  ? `SPEC-001+SPEC-002+SPEC-003+SPEC-004+SPEC-005 goal-maestro-p0-spec-fidelity (${LINEAR_STOP_STATE}/${SPEC_FIDELITY_STOP_STATE})`
  : documentAnalysisPacketRequired
  ? `SPEC-001+SPEC-002+SPEC-003+SPEC-004 goal-maestro-p0-document-analysis-packet (${LINEAR_STOP_STATE}/${PRE_EDIT_STOP_STATE}/${PROMPT_ENRICHMENT_STOP_STATE}/${DOCUMENT_ANALYSIS_STOP_STATE})`
  : promptEnrichmentPacketRequired
    ? `SPEC-001+SPEC-002+SPEC-003 goal-maestro-p0-prompt-enrichment-packet (${LINEAR_STOP_STATE}/${PRE_EDIT_STOP_STATE}/${PROMPT_ENRICHMENT_STOP_STATE})`
    : preEditGateRequired
      ? `SPEC-001+SPEC-002 goal-maestro-p0-pre-edit-gate (${LINEAR_STOP_STATE}/${PRE_EDIT_STOP_STATE})`
      : `SPEC-001 goal-maestro-p0-linear-pipeline (${LINEAR_STOP_STATE})`;
runChecks(harnessTitle, checks);

function observePreEditGate(eventIndex, event) {
  const artifact = isPlainObject(event.artifact) ? event.artifact : event;
  preEditGateEvents.push({ eventIndex, event, artifact });
}

function observePromptEnrichmentPacket(eventIndex, event) {
  const packet = isPlainObject(event.artifact) ? event.artifact : event;
  promptEnrichmentPacketEvents.push({ eventIndex, event, packet });
}

function observeDocumentAnalysisPacket(eventIndex, event) {
  const packet = isPlainObject(event.artifact) ? event.artifact : event;
  documentAnalysisPacketEvents.push({ eventIndex, event, packet });
}

function observeSpecFidelityEvent(eventIndex, event) {
  const eventType = event.type;
  const specId = event.spec_id;
  const mergedUnitIds = mergedSpecIds(event);
  if (mergedUnitIds.length > 0) {
    specFidelityCheck(
      `event ${eventIndex + 1} does not merge execution units`,
      false,
      `merged execution units are forbidden in material SPEC flow: ${formatIds(mergedUnitIds)}`,
    );
  }

  if (eventType === 'open_spec') {
    materialOpenedSpecIds.push(specId);
  } else if (eventType === 'implement') {
    materialExecutedSpecIds.push(specId);
  } else if (eventType === 'local_commit_status' && (event.status ?? event.value) === 'LOCAL_COMMITTED') {
    materialCommittedSpecIds.push(specId);
  }
}

function addPreEditGateChecks() {
  const gateEvent = preEditGateEvents[0] ?? null;
  const artifact = gateEvent?.artifact ?? {};
  const artifactRef = preEditArtifactRef(gateEvent?.event, artifact);
  const expected = isPlainObject(fixture.pre_edit_gate_expectations) ? fixture.pre_edit_gate_expectations : {};
  const expectedActiveSpec = expected.active_spec ?? fixture.active_spec;
  const expectedFirstUnexecutedSpec = expected.first_unexecuted_spec ?? expected.first_unexecuted_unit ?? fixture.first_unexecuted_spec ?? fixture.first_unexecuted_unit;
  const expectedAnchorHash = expected.anchor_hash ?? fixture.anchor_hash;
  const expectedAllowedFiles = expected.allowed_files ?? fixture.allowed_files;
  const expectedForbiddenFiles = expected.forbidden_files ?? fixture.forbidden_files;
  const expectedForbiddenActions = expected.forbidden_actions ?? fixture.forbidden_actions;
  const expectedRequiredGates = expected.required_gates ?? fixture.required_gates;
  const expectedCommitMode = expected.commit_mode ?? fixture.commit_mode;

  preEditCheck(
    'pre-edit artifact event exists',
    preEditGateEvents.length > 0,
    'loop start requires a durable pre-edit artifact event',
  );
  preEditCheck(
    'pre-edit artifact event is unique',
    preEditGateEvents.length === 1,
    'exactly one durable pre-edit artifact event must be emitted',
  );

  if (!gateEvent) return;

  preEditCheck(
    'pre-edit artifact precedes loop start',
    firstLoopStartIndex === null || gateEvent.eventIndex < firstLoopStartIndex,
    'pre-edit artifact was not emitted before loop start',
  );
  preEditCheck(
    'pre-edit artifact precedes first material edit',
    firstMaterialEditIndex === null || gateEvent.eventIndex < firstMaterialEditIndex,
    'pre-edit artifact was emitted after the first material edit',
  );
  preEditCheck(
    'pre-edit artifact ref is package-local',
    isPackageLocalArtifactRef(artifactRef),
    'artifact ref must be a non-absolute package-local path',
  );
  preEditCheck(
    'pre-edit artifact active SPEC is present',
    nonEmptyString(artifact.active_spec),
    'artifact lacks active_spec',
  );
  preEditCheck(
    'pre-edit artifact first unexecuted SPEC is present',
    nonEmptyString(artifact.first_unexecuted_spec ?? artifact.first_unexecuted_unit),
    'artifact lacks first_unexecuted_spec',
  );
  preEditCheck(
    'pre-edit artifact anchor hash is present',
    nonEmptyString(artifact.anchor_hash),
    'artifact lacks anchor_hash',
  );
  preEditCheck(
    'pre-edit artifact baseline state is present',
    hasBaselineState(artifact.baseline_state),
    'artifact lacks baseline_state',
  );
  preEditCheck(
    'pre-edit artifact allowed files are present',
    hasNonEmptyStringArray(artifact.allowed_files),
    'artifact lacks allowed_files',
  );
  preEditCheck(
    'pre-edit artifact forbidden files are present',
    hasNonEmptyStringArray(artifact.forbidden_files),
    'artifact lacks forbidden_files',
  );
  preEditCheck(
    'pre-edit artifact forbidden actions are present',
    hasNonEmptyStringArray(artifact.forbidden_actions),
    'artifact lacks forbidden_actions',
  );
  preEditCheck(
    'pre-edit artifact required gates are present',
    hasNonEmptyStringArray(artifact.required_gates),
    'artifact lacks required_gates',
  );
  preEditCheck(
    'pre-edit artifact installed TES version is present',
    nonEmptyString(artifact.installed_tes_version),
    'artifact lacks installed_tes_version',
  );
  preEditCheck(
    'pre-edit artifact commit mode is present',
    nonEmptyString(artifact.commit_mode),
    'artifact lacks commit_mode',
  );

  if (nonEmptyString(expectedActiveSpec)) {
    preEditCheck(
      'pre-edit artifact active SPEC matches expectation',
      artifact.active_spec === expectedActiveSpec,
      `artifact active_spec must be ${expectedActiveSpec}`,
    );
  }
  if (nonEmptyString(expectedFirstUnexecutedSpec)) {
    preEditCheck(
      'pre-edit artifact first unexecuted SPEC matches expectation',
      (artifact.first_unexecuted_spec ?? artifact.first_unexecuted_unit) === expectedFirstUnexecutedSpec,
      `artifact first_unexecuted_spec must be ${expectedFirstUnexecutedSpec}`,
    );
  }
  if (nonEmptyString(expectedAnchorHash)) {
    preEditCheck(
      'pre-edit artifact anchor hash matches expectation',
      artifact.anchor_hash === expectedAnchorHash,
      `artifact anchor_hash must be ${expectedAnchorHash}`,
    );
  }
  if (hasNonEmptyStringArray(expectedAllowedFiles)) {
    preEditCheck(
      'pre-edit artifact allowed files match expectation',
      sameStringArray(artifact.allowed_files, expectedAllowedFiles),
      'artifact allowed_files drifted from the execution contract',
    );
  }
  if (hasNonEmptyStringArray(expectedForbiddenFiles)) {
    preEditCheck(
      'pre-edit artifact forbidden files match expectation',
      sameStringArray(artifact.forbidden_files, expectedForbiddenFiles),
      'artifact forbidden_files drifted from the execution contract',
    );
  }
  if (hasNonEmptyStringArray(expectedForbiddenActions)) {
    preEditCheck(
      'pre-edit artifact forbidden actions match expectation',
      sameStringArray(artifact.forbidden_actions, expectedForbiddenActions),
      'artifact forbidden_actions drifted from the execution contract',
    );
  }
  if (hasNonEmptyStringArray(expectedRequiredGates)) {
    preEditCheck(
      'pre-edit artifact required gates match expectation',
      sameStringArray(artifact.required_gates, expectedRequiredGates),
      'artifact required_gates drifted from the execution contract',
    );
  }
  if (nonEmptyString(expectedCommitMode)) {
    preEditCheck(
      'pre-edit artifact commit mode matches expectation',
      artifact.commit_mode === expectedCommitMode,
      `artifact commit_mode must be ${expectedCommitMode}`,
    );
  }

  for (const [surfaceName, surface] of [
    ['ledger', fixture.ledger],
    ['thermometer metrics', fixture.thermometer_metrics],
    ['closeout', fixture.closeout],
  ]) {
    preEditCheck(
      `pre-edit artifact cited by ${surfaceName}`,
      surfaceCitesRef(surface, artifactRef),
      `${surfaceName} must cite ${artifactRef || 'the pre-edit artifact'}`,
    );
  }
}

function addPromptEnrichmentPacketChecks() {
  const packetEvent = promptEnrichmentPacketEvents[0] ?? null;
  const packet = packetEvent?.packet ?? {};
  const packetRef = preEditArtifactRef(packetEvent?.event, packet);
  const expected = isPlainObject(fixture.prompt_enrichment_expectations) ? fixture.prompt_enrichment_expectations : {};
  const expectedSpecQueue = expected.spec_queue ?? fixture.spec_queue ?? declaredSpecs;
  const expectedStructuralMethod = expected.structural_method ?? fixture.structural_method ?? fixture.structural_method_id;
  const expectedStopStates = expected.stop_states ?? fixture.stop_states;
  const sourcePrompt = expected.source_prompt ?? fixture.source_prompt ?? fixture.user_prompt;

  promptEnrichmentCheck(
    'prompt enrichment packet event exists',
    promptEnrichmentPacketEvents.length > 0,
    'loop start requires a durable prompt enrichment packet event',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet event is unique',
    promptEnrichmentPacketEvents.length === 1,
    'exactly one durable prompt enrichment packet event must be emitted',
  );

  if (!packetEvent) return;

  promptEnrichmentCheck(
    'prompt enrichment packet precedes loop start',
    firstLoopStartIndex === null || packetEvent.eventIndex < firstLoopStartIndex,
    'prompt enrichment packet was not emitted before loop start',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet precedes first material edit',
    firstMaterialEditIndex === null || packetEvent.eventIndex < firstMaterialEditIndex,
    'prompt enrichment packet was emitted after the first material edit',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet ref is package-local',
    isPackageLocalArtifactRef(packetRef),
    'packet ref must be a non-absolute package-local path',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet ref uses json or md',
    isPromptEnrichmentPacketRef(packetRef),
    'packet ref must end in .json or .md',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet is not prompt echo only',
    !isPromptEchoOnly(packet, sourcePrompt),
    'packet only repeats the user prompt and does not prove source-artifact enrichment',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet extracted intent is present',
    nonEmptyString(packet.extracted_intent),
    'packet lacks extracted_intent',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet SPEC queue is present',
    hasNonEmptyStringArray(packet.spec_queue),
    'packet lacks spec_queue',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet lenses are present',
    hasNonEmptyStringArray(packet.lenses_selected),
    'packet lacks lenses_selected',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet structural method is present',
    nonEmptyString(packet.structural_method),
    'packet lacks structural_method',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet oracle packet is present',
    hasNonEmptyObject(packet.oracle_packet),
    'packet lacks oracle_packet',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet evidence contract is present',
    hasNonEmptyObject(packet.evidence_contract),
    'packet lacks evidence_contract',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet stop states are present',
    hasNonEmptyStringArray(packet.stop_states),
    'packet lacks stop_states',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet risk decisions are present',
    hasNonEmptyStringArray(packet.risk_decisions),
    'packet lacks risk_decisions',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet non-objectives are present',
    hasNonEmptyStringArray(packet.non_objectives),
    'packet lacks non_objectives',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet sidecar requirements are present',
    hasNonEmptyStringArray(packet.sidecar_requirements),
    'packet lacks sidecar_requirements',
  );
  promptEnrichmentCheck(
    'prompt enrichment packet stop state is declared',
    Array.isArray(packet.stop_states) && packet.stop_states.includes(PROMPT_ENRICHMENT_STOP_STATE),
    `packet stop_states must include ${PROMPT_ENRICHMENT_STOP_STATE}`,
  );

  if (hasNonEmptyStringArray(expectedSpecQueue)) {
    promptEnrichmentCheck(
      'prompt enrichment packet SPEC queue matches expectation',
      sameStringArray(packet.spec_queue, expectedSpecQueue),
      'packet spec_queue drifted from the execution contract',
    );
  }
  if (nonEmptyString(expectedStructuralMethod)) {
    promptEnrichmentCheck(
      'prompt enrichment packet structural method matches expectation',
      packet.structural_method === expectedStructuralMethod,
      `packet structural_method must be ${expectedStructuralMethod}`,
    );
  }
  if (hasNonEmptyStringArray(expectedStopStates)) {
    promptEnrichmentCheck(
      'prompt enrichment packet stop states match expectation',
      sameStringArray(packet.stop_states, expectedStopStates),
      'packet stop_states drifted from the execution contract',
    );
  }
}

function addDocumentAnalysisPacketChecks() {
  const packetEvent = documentAnalysisPacketEvents[0] ?? null;
  const packet = packetEvent?.packet ?? {};
  const packetRef = preEditArtifactRef(packetEvent?.event, packet);
  const expected = isPlainObject(fixture.document_analysis_expectations) ? fixture.document_analysis_expectations : {};
  const expectedExternalDocumentationRequired = expected.external_documentation_required ?? fixture.external_documentation_required;
  const expectedCloudSearchRequired = expected.cloud_search_required ?? fixture.cloud_search_required;

  documentAnalysisCheck(
    'document analysis packet event exists',
    documentAnalysisPacketEvents.length > 0,
    'loop start requires a durable document analysis packet event',
  );
  documentAnalysisCheck(
    'document analysis packet event is unique',
    documentAnalysisPacketEvents.length === 1,
    'exactly one durable document analysis packet event must be emitted',
  );

  if (!packetEvent) return;

  documentAnalysisCheck(
    'document analysis packet precedes loop start',
    firstLoopStartIndex === null || packetEvent.eventIndex < firstLoopStartIndex,
    'document analysis packet was not emitted before loop start',
  );
  documentAnalysisCheck(
    'document analysis packet precedes first material edit',
    firstMaterialEditIndex === null || packetEvent.eventIndex < firstMaterialEditIndex,
    'document analysis packet was emitted after the first material edit',
  );
  documentAnalysisCheck(
    'document analysis packet ref is package-local',
    isPackageLocalArtifactRef(packetRef),
    'packet ref must be a non-absolute package-local path',
  );
  documentAnalysisCheck(
    'document analysis packet ref uses json or md',
    isDocumentAnalysisPacketRef(packetRef),
    'packet ref must end in .json or .md',
  );
  documentAnalysisCheck(
    'document analysis packet functional requirements are mapped',
    hasMappedPacketField(packet.functional_requirements),
    'packet lacks functional_requirements',
  );
  documentAnalysisCheck(
    'document analysis packet non-functional requirements are mapped',
    hasMappedPacketField(packet.non_functional_requirements),
    'packet lacks non_functional_requirements',
  );
  documentAnalysisCheck(
    'document analysis packet acceptance criteria are mapped',
    hasMappedPacketField(packet.acceptance_criteria),
    'packet lacks acceptance_criteria',
  );
  documentAnalysisCheck(
    'document analysis packet forbidden moves are mapped',
    hasMappedPacketField(packet.forbidden_moves),
    'packet lacks forbidden_moves',
  );
  documentAnalysisCheck(
    'document analysis packet visual/runtime requirements are mapped',
    hasMappedPacketField(packet.visual_runtime_requirements),
    'packet lacks visual_runtime_requirements',
  );
  documentAnalysisCheck(
    'document analysis packet evidence requirements are mapped',
    hasMappedPacketField(packet.evidence_requirements),
    'packet lacks evidence_requirements',
  );
  documentAnalysisCheck(
    'document analysis packet explicit ambiguities are mapped',
    hasMappedPacketField(packet.explicit_ambiguities),
    'packet lacks explicit_ambiguities',
  );
  documentAnalysisCheck(
    'document analysis packet external documentation requirement is recorded',
    typeof packet.external_documentation_required === 'boolean',
    'packet lacks external_documentation_required boolean',
  );
  documentAnalysisCheck(
    'document analysis packet cloud search requirement is recorded',
    typeof packet.cloud_search_required === 'boolean',
    'packet lacks cloud_search_required boolean',
  );

  if (typeof expectedExternalDocumentationRequired === 'boolean') {
    documentAnalysisCheck(
      'document analysis packet external documentation requirement matches expectation',
      packet.external_documentation_required === expectedExternalDocumentationRequired,
      `packet external_documentation_required must be ${expectedExternalDocumentationRequired}`,
    );
  }
  if (typeof expectedCloudSearchRequired === 'boolean') {
    documentAnalysisCheck(
      'document analysis packet cloud search requirement matches expectation',
      packet.cloud_search_required === expectedCloudSearchRequired,
      `packet cloud_search_required must be ${expectedCloudSearchRequired}`,
    );
  }
}

function addSpecFidelityChecks() {
  const reportedSpecIds = reportedSpecIdsFromFixture(fixture);
  specFidelityCheck(
    'reported SPEC IDs are present',
    reportedSpecIds.length > 0,
    'reported SPEC IDs are required for SPEC fidelity comparison',
  );

  compareSpecFidelityList('opened SPEC IDs', materialOpenedSpecIds);
  compareSpecFidelityList('executed SPEC IDs', materialExecutedSpecIds);
  compareSpecFidelityList('committed SPEC IDs', materialCommittedSpecIds);
  compareSpecFidelityList('reported SPEC IDs', reportedSpecIds);

  for (const specId of declaredSpecs) {
    const state = specStates.get(specId);
    specFidelityCheck(
      `${specId} executed`,
      state?.executed === true,
      `${specId} is declared but missing from execution`,
    );
    specFidelityCheck(
      `${specId} has per-SPEC evidence after open`,
      state?.opened === true && state.complete.evidence === true,
      `${specId} lacks per-SPEC evidence after ACTIVE_SPEC opened`,
    );
  }
}

function compareSpecFidelityList(label, ids) {
  const actualIds = normalizeSpecIdArray(ids);
  const auditIds = actualIds.filter(isAuditUnitId);
  const unexpectedUnits = actualIds.filter((id) => (
    !isMaterialSpecId(id) && !isAuditUnitId(id) && !isAcceptedBoundedRepairUnit(id)
  ));
  const materialSpecIds = actualIds.filter(isMaterialSpecId);

  specFidelityCheck(
    `${label} exclude audit units`,
    auditIds.length === 0,
    `${label} counted audit unit(s) as material: ${formatIds(auditIds)}`,
  );
  specFidelityCheck(
    `${label} contain only material SPECs or accepted repair units`,
    unexpectedUnits.length === 0,
    `${label} include undeclared non-SPEC unit(s): ${formatIds(unexpectedUnits)}`,
  );
  specFidelityCheck(
    `${label} match declared SPEC order exactly`,
    sameStringArray(materialSpecIds, declaredSpecs),
    `${label} ${formatIds(materialSpecIds)} must exactly match declared_specs ${formatIds(declaredSpecs)}`,
  );
}

function addThermometerFidelityChecks() {
  const metrics = thermometerMetricsFromFixture(fixture);
  const emittedSpecIds = collectThermometerSpecIds(metrics);
  const unknownSpecIds = emittedSpecIds.filter(isUnknownSpecId);
  const auditUnitIds = emittedSpecIds.filter(isAuditUnitId);
  const materialSpecIds = uniqueStrings(emittedSpecIds.filter(isMaterialSpecId));
  const missingDeclaredSpecs = declaredSpecs.filter((specId) => !materialSpecIds.includes(specId));
  const unprovenRequiredMetrics = blockingUnprovenExecutionMetrics(metrics, fixture);

  thermometerFidelityCheck(
    'thermometer metrics are present',
    hasNonEmptyObject(metrics),
    'thermometer metrics are required for complete closeout',
  );
  thermometerFidelityCheck(
    'thermometer emitted SPEC IDs are present',
    emittedSpecIds.length > 0,
    'thermometer must emit material SPEC IDs for execution fidelity',
  );
  thermometerFidelityCheck(
    'thermometer complete closeout excludes SPEC-UNKNOWN',
    unknownSpecIds.length === 0,
    `complete closeout cannot include ${formatIds(unknownSpecIds)}`,
  );
  thermometerFidelityCheck(
    'thermometer material SPECs include every declared SPEC',
    missingDeclaredSpecs.length === 0,
    `declared material SPEC(s) missing from thermometer: ${formatIds(missingDeclaredSpecs)}`,
  );
  thermometerFidelityCheck(
    'thermometer material SPECs exclude audit units',
    auditUnitIds.length === 0,
    `audit unit(s) counted as material SPECs: ${formatIds(auditUnitIds)}`,
  );
  thermometerFidelityCheck(
    'required execution fidelity fields have no unproven metrics',
    unprovenRequiredMetrics.length === 0,
    `unproven execution fidelity metric(s): ${formatMetricNames(unprovenRequiredMetrics)}`,
  );
}

function addLedgerGrammarChecks() {
  const ledgerText = ledgerTextFromFixture(fixture);
  const parsed = parseLedgerGrammar(ledgerText);
  const expected = isPlainObject(fixture.ledger_grammar_expectations) ? fixture.ledger_grammar_expectations : {};
  const expectedDeclaredSpecs = expected.declared_specs ?? fixture.ledger_declared_specs ?? declaredSpecs;
  const sectionSpecIds = parsed.materialSections.map((section) => section.headingSpecId);
  const duplicateSectionIds = duplicateStrings(sectionSpecIds);
  const nonMatchingSpecIdSections = parsed.materialSections.filter((section) => (
    section.specIdValues.some((specId) => specId !== section.headingSpecId)
  ));
  const invalidSpecIdCardinalitySections = parsed.materialSections.filter((section) => (
    section.specIdValues.length !== 1 || section.specIdValues[0] !== section.headingSpecId
  ));
  const finalSection = parsed.materialSections.at(-1) ?? null;
  const thermometerMetrics = thermometerMetricsFromFixture(fixture);
  const grammarValid = nonEmptyString(ledgerText)
    && parsed.malformedSpecHeadings.length === 0
    && duplicateSectionIds.length === 0
    && sameStringArray(sectionSpecIds, expectedDeclaredSpecs)
    && invalidSpecIdCardinalitySections.length === 0
    && nonMatchingSpecIdSections.length === 0
    && (finalSection?.nestedAuditCloseoutHeadings.length ?? 0) === 0;

  ledgerGrammarCheck(
    'ledger text is present',
    nonEmptyString(ledgerText),
    'ledger_text or ledger markdown text is required for grammar validation',
  );
  ledgerGrammarCheck(
    'material SPEC headings use canonical grammar',
    parsed.malformedSpecHeadings.length === 0,
    `material SPEC headings must use "### SPEC-NNN - Title": ${formatValues(parsed.malformedSpecHeadings)}`,
  );
  ledgerGrammarCheck(
    'material SPEC sections are unique',
    duplicateSectionIds.length === 0,
    `duplicate material SPEC section(s): ${formatValues(duplicateSectionIds)}`,
  );
  ledgerGrammarCheck(
    'material SPEC sections match declared SPEC order',
    sameStringArray(sectionSpecIds, expectedDeclaredSpecs),
    `ledger material sections ${formatValues(sectionSpecIds)} must match declared_specs ${formatValues(expectedDeclaredSpecs)}`,
  );
  ledgerGrammarCheck(
    'each material section has exactly one matching spec_id',
    invalidSpecIdCardinalitySections.length === 0,
    `section spec_id cardinality or value mismatch: ${formatValues(invalidSpecIdCardinalitySections.map((section) => section.headingSpecId))}`,
  );
  ledgerGrammarCheck(
    'audit fields cannot overwrite material spec_id',
    nonMatchingSpecIdSections.length === 0,
    `material section(s) contain non-matching spec_id fields: ${formatValues(nonMatchingSpecIdSections.map((section) => section.headingSpecId))}`,
  );
  ledgerGrammarCheck(
    'final material SPEC body excludes audit and closeout sections',
    (finalSection?.nestedAuditCloseoutHeadings.length ?? 0) === 0,
    `final material SPEC body contains audit/closeout heading(s): ${formatValues(finalSection?.nestedAuditCloseoutHeadings ?? [])}`,
  );
  if (hasNonEmptyObject(thermometerMetrics)) {
    ledgerGrammarCheck(
      'malformed grammar blocks Thermometer packaging',
      grammarValid,
      'canonical ledger grammar must pass before Thermometer metrics are packaged',
    );
  }
}

function addReportCoherenceChecks() {
  const metrics = thermometerMetricsFromFixture(fixture);
  const surfaces = [
    { name: 'ledger', snapshot: reportSurfaceSnapshot('ledger', reportCoherenceSurfaceFromFixture('ledger')) },
    { name: 'metrics', snapshot: reportSurfaceSnapshot('metrics', metrics) },
    { name: 'receipt', snapshot: reportSurfaceSnapshot('receipt', reportCoherenceSurfaceFromFixture('receipt')) },
    { name: 'html', snapshot: reportSurfaceSnapshot('html', reportCoherenceSurfaceFromFixture('html')) },
  ];
  const expected = expectedReportCoherenceSnapshot(surfaces.find((surface) => surface.name === 'metrics')?.snapshot ?? {});

  reportCoherenceCheck(
    'checksum validation passed before report coherence closeout',
    checksumValidationPassed(fixture),
    'report coherence requires a passing checksum validation for the local package',
  );

  for (const field of REPORT_COHERENCE_FIELDS) {
    reportCoherenceCheck(
      `${field} expectation is present`,
      reportCoherenceFieldPresent(expected, field),
      `report_coherence_expectations lacks ${field}`,
    );
    for (const surface of surfaces) {
      const surfaceFieldPresent = reportCoherenceFieldPresent(surface.snapshot, field);
      reportCoherenceCheck(
        `${surface.name} ${field} is present`,
        surfaceFieldPresent,
        `${surface.name} surface lacks ${field}`,
      );
      reportCoherenceCheck(
        `${surface.name} ${field} matches canonical report value`,
        surfaceFieldPresent && reportCoherenceFieldEqual(surface.snapshot[field], expected[field], field),
        `${surface.name} ${field} ${formatReportCoherenceField(surface.snapshot[field])} must match ${formatReportCoherenceField(expected[field])}`,
      );
    }
  }

  const metricsSnapshot = surfaces.find((surface) => surface.name === 'metrics')?.snapshot ?? {};
  const receiptSnapshot = surfaces.find((surface) => surface.name === 'receipt')?.snapshot ?? {};
  reportCoherenceCheck(
    'chat closeout does not pass with unproven report surfaces',
    !(closeoutSaysPass(reportCoherenceSurfaceFromFixture('closeout')) && reportSurfacesAreUnproven(metricsSnapshot, receiptSnapshot)),
    'chat closeout cannot say pass when metrics or receipt reports unproven counts',
  );
}

function openSpec(eventIndex, event) {
  const specId = event.spec_id;
  const expectedSpec = declaredSpecs[nextOpenIndex];
  const state = specStates.get(specId);

  if (state.opened) {
    fail(`event ${eventIndex + 1} duplicate open`, `${specId} opened more than once`);
    return;
  }

  if (specId !== expectedSpec) {
    fail(`event ${eventIndex + 1} open order`, `expected ${expectedSpec ?? 'no more SPECs'}, got ${specId}`);
    return;
  }

  if (activeSpec && !isComplete(specStates.get(activeSpec))) {
    fail(
      `event ${eventIndex + 1} next SPEC gate`,
      `${specId} opened before ${activeSpec} had evidence, oracle result, local commit status, and parent validation`,
    );
    return;
  }

  state.opened = true;
  state.openIndex = eventIndex;
  state.openedAt = event.at ?? null;
  activeSpec = specId;
  nextOpenIndex += 1;
}

function applySpecEvent(eventIndex, event) {
  const specId = event.spec_id;
  const state = specStates.get(specId);

  if (!state.opened) {
    if (event.type === 'implement' && activeSpec && !isComplete(specStates.get(activeSpec))) {
      fail(`event ${eventIndex + 1} future implementation`, `${specId} implementation ran before ${activeSpec} parent validation completed`);
      return;
    }
    if (event.type === 'evidence') {
      fail(`event ${eventIndex + 1} pre-open evidence`, `${specId} evidence occurred before that SPEC opened and cannot satisfy the SPEC`);
      return;
    }
    fail(`event ${eventIndex + 1} ${event.type} chronology`, `${event.type} for ${specId} occurred before that SPEC opened`);
    return;
  }

  if (activeSpec !== specId) {
    fail(`event ${eventIndex + 1} ACTIVE_SPEC ownership`, `${event.type} for ${specId} ran while ${activeSpec ?? 'no SPEC'} was active`);
    return;
  }

  if (isEarlierTimestamp(event.at, state.openedAt)) {
    fail(`event ${eventIndex + 1} timestamp`, `${event.type} for ${specId} is timestamped before ${specId} opened`);
    return;
  }

  if (event.type === 'implement') {
    state.executed = true;
    return;
  }

  if (event.type === 'evidence') {
    const hasEvidence = nonEmptyString(event.evidence_ref) || nonEmptyString(event.path) || nonEmptyString(event.artifact);
    if (!hasEvidence) {
      fail(`event ${eventIndex + 1} evidence`, `${specId} evidence event lacks evidence_ref, path, or artifact`);
      return;
    }
    state.complete.evidence = true;
    return;
  }

  if (event.type === 'oracle_result') {
    if (!isPassStatus(event.status ?? event.result)) {
      fail(`event ${eventIndex + 1} oracle result`, `${specId} oracle result is not pass`);
      return;
    }
    state.complete.oracle_result = true;
    return;
  }

  if (event.type === 'local_commit_status') {
    if ((event.status ?? event.value) !== 'LOCAL_COMMITTED') {
      fail(`event ${eventIndex + 1} local commit status`, `${specId} local commit status is not LOCAL_COMMITTED`);
      return;
    }
    state.complete.local_commit_status = true;
    return;
  }

  if (event.type === 'parent_validation') {
    if (!isPassStatus(event.status ?? event.result)) {
      fail(`event ${eventIndex + 1} parent validation`, `${specId} parent validation is not pass`);
      return;
    }
    state.complete.parent_validation = true;
  }
}

function fail(name, detail) {
  checks.push({ name, pass: false, detail: `${LINEAR_STOP_STATE}: ${detail}` });
}

function preEditCheck(name, pass, detail) {
  checks.push({ name, pass, detail: pass ? undefined : `${PRE_EDIT_STOP_STATE}: ${detail}` });
}

function promptEnrichmentCheck(name, pass, detail) {
  checks.push({ name, pass, detail: pass ? undefined : `${PROMPT_ENRICHMENT_STOP_STATE}: ${detail}` });
}

function documentAnalysisCheck(name, pass, detail) {
  checks.push({ name, pass, detail: pass ? undefined : `${DOCUMENT_ANALYSIS_STOP_STATE}: ${detail}` });
}

function specFidelityCheck(name, pass, detail) {
  checks.push({ name, pass, detail: pass ? undefined : `${SPEC_FIDELITY_STOP_STATE}: ${detail}` });
}

function thermometerFidelityCheck(name, pass, detail) {
  checks.push({ name, pass, detail: pass ? undefined : `${THERMOMETER_FIDELITY_STOP_STATE}: ${detail}` });
}

function ledgerGrammarCheck(name, pass, detail) {
  checks.push({ name, pass, detail: pass ? undefined : `${LEDGER_GRAMMAR_STOP_STATE}: ${detail}` });
}

function reportCoherenceCheck(name, pass, detail) {
  checks.push({ name, pass, detail: pass ? undefined : `${REPORT_COHERENCE_STOP_STATE}: ${detail}` });
}

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function nonEmptyString(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

function hasBaselineState(value) {
  if (nonEmptyString(value)) return true;
  return isPlainObject(value) && Object.keys(value).length > 0;
}

function hasNonEmptyStringArray(value) {
  return Array.isArray(value) && value.length > 0 && value.every(nonEmptyString);
}

function hasNonEmptyObject(value) {
  return isPlainObject(value) && Object.keys(value).length > 0;
}

function hasMappedPacketField(value) {
  if (nonEmptyString(value)) return true;
  if (Array.isArray(value)) return value.length > 0 && value.some(hasMappedPacketField);
  if (isPlainObject(value)) return Object.values(value).some(hasMappedPacketField);
  return false;
}

function sameStringArray(left, right) {
  if (!Array.isArray(left) || !Array.isArray(right) || left.length !== right.length) return false;
  return left.every((value, index) => value === right[index]);
}

function normalizeSpecIdArray(value) {
  if (!Array.isArray(value)) return [];
  return value.map(specIdFromValue).filter(nonEmptyString);
}

function specIdFromValue(value) {
  if (typeof value === 'string') return value;
  if (!isPlainObject(value)) return null;
  return value.spec_id ?? value.specId ?? value.id ?? value.unit_id ?? null;
}

function reportedSpecIdsFromFixture(value) {
  const candidates = [
    value.reported_specs,
    value.reported_spec_ids,
    value.material_specs,
    value.material_spec_ids,
    value.spec_fidelity?.reported_specs,
    value.spec_fidelity_report?.reported_specs,
    value.report?.specs,
    value.report?.reported_specs,
    value.thermometer_metrics?.specs,
    value.thermometer_metrics?.reported_specs,
    value.closeout?.specs,
    value.closeout?.reported_specs,
  ];
  for (const candidate of candidates) {
    const specIds = normalizeSpecIdArray(candidate);
    if (specIds.length > 0) return specIds;
  }
  return [];
}

function mergedSpecIds(event) {
  const mergedIds = [
    ...normalizeSpecIdArray(event.merged_spec_ids),
    ...normalizeSpecIdArray(event.merged_specs),
    ...normalizeSpecIdArray(event.merged_units),
  ];
  const eventSpecIds = normalizeSpecIdArray(event.spec_ids);
  if (eventSpecIds.length > 1 || (eventSpecIds.length === 1 && eventSpecIds[0] !== event.spec_id)) {
    mergedIds.push(...eventSpecIds);
  }
  return [...new Set(mergedIds)];
}

function preEditArtifactRef(event, artifact) {
  return artifact?.path ?? artifact?.artifact_ref ?? artifact?.ref ?? event?.path ?? event?.artifact_ref ?? event?.ref ?? null;
}

function isPackageLocalArtifactRef(value) {
  if (!nonEmptyString(value)) return false;
  if (value.startsWith('/') || /^[A-Za-z]:[\\/]/.test(value)) return false;
  return !value.split(/[\\/]+/).includes('..');
}

function surfaceCitesRef(surface, artifactRef) {
  if (!isPackageLocalArtifactRef(artifactRef)) return false;
  return collectStrings(surface).includes(artifactRef);
}

function collectStrings(value) {
  if (typeof value === 'string') return [value];
  if (Array.isArray(value)) return value.flatMap(collectStrings);
  if (isPlainObject(value)) return Object.values(value).flatMap(collectStrings);
  return [];
}

function requiresPreEditGate(value) {
  return value.pre_edit_gate_required === true
    || value.harness_contract === PRE_EDIT_CONTRACT
    || value.contract === PRE_EDIT_CONTRACT;
}

function requiresPromptEnrichmentPacket(value) {
  return value.prompt_enrichment_packet_required === true
    || value.harness_contract === PROMPT_ENRICHMENT_CONTRACT
    || value.contract === PROMPT_ENRICHMENT_CONTRACT;
}

function requiresDocumentAnalysisPacket(value) {
  return value.document_analysis_packet_required === true
    || value.harness_contract === DOCUMENT_ANALYSIS_CONTRACT
    || value.contract === DOCUMENT_ANALYSIS_CONTRACT;
}

function requiresSpecFidelityGate(value) {
  return value.spec_fidelity_required === true
    || value.harness_contract === SPEC_FIDELITY_CONTRACT
    || value.contract === SPEC_FIDELITY_CONTRACT;
}

function requiresThermometerFidelityGate(value) {
  return value.thermometer_fidelity_required === true
    || value.harness_contract === THERMOMETER_FIDELITY_CONTRACT
    || value.contract === THERMOMETER_FIDELITY_CONTRACT;
}

function requiresLedgerGrammarGate(value) {
  return value.ledger_grammar_required === true
    || value.harness_contract === LEDGER_GRAMMAR_CONTRACT
    || value.contract === LEDGER_GRAMMAR_CONTRACT;
}

function requiresReportCoherenceGate(value) {
  return value.report_coherence_required === true
    || value.harness_contract === REPORT_COHERENCE_CONTRACT
    || value.contract === REPORT_COHERENCE_CONTRACT;
}

function acceptedBoundedRepairUnitIds(value) {
  const acceptedUnits = [
    ...normalizeSpecIdArray(value.accepted_bounded_repair_units),
    ...normalizeSpecIdArray(value.accepted_repair_units),
  ];
  for (const unit of Array.isArray(value.bounded_repair_units) ? value.bounded_repair_units : []) {
    if (typeof unit === 'string') continue;
    if (!isPlainObject(unit)) continue;
    if (unit.accepted === true || unit.status === 'accepted') {
      const unitId = specIdFromValue(unit);
      if (nonEmptyString(unitId)) acceptedUnits.push(unitId);
    }
  }
  return new Set(acceptedUnits.filter((unitId) => !isMaterialSpecId(unitId)));
}

function isAcceptedBoundedRepairUnit(value) {
  return nonEmptyString(value) && acceptedBoundedRepairUnits.has(value);
}

function isMaterialSpecId(value) {
  return /^SPEC-\d{3}$/.test(String(value));
}

function isAuditUnitId(value) {
  return /(^|[-_])AUDIT($|[-_])/i.test(String(value));
}

function isUnknownSpecId(value) {
  return String(value).toUpperCase() === 'SPEC-UNKNOWN';
}

function formatIds(ids) {
  return `[${normalizeSpecIdArray(ids).join(', ')}]`;
}

function formatValues(values) {
  return `[${(Array.isArray(values) ? values : []).join(', ')}]`;
}

function duplicateStrings(values) {
  const seen = new Set();
  const duplicates = new Set();
  for (const value of values.filter(nonEmptyString)) {
    if (seen.has(value)) duplicates.add(value);
    seen.add(value);
  }
  return [...duplicates];
}

function uniqueStrings(values) {
  return [...new Set(values.filter(nonEmptyString))];
}

function thermometerMetricsFromFixture(value) {
  const metrics = value.thermometer_metrics ?? value.execution_thermometer ?? value.thermometer ?? {};
  return isPlainObject(metrics) ? metrics : {};
}

function reportCoherenceSurfaceFromFixture(surfaceName) {
  const reportSurfaces = isPlainObject(fixture.report_surfaces) ? fixture.report_surfaces : {};
  if (surfaceName === 'ledger') {
    const ledgerText = ledgerTextFromFixture(fixture);
    return reportSurfaces.ledger ?? fixture.ledger_report_coherence ?? (nonEmptyString(ledgerText) ? ledgerText : fixture.ledger ?? {});
  }
  if (surfaceName === 'receipt') return reportSurfaces.receipt ?? fixture.receipt_text ?? fixture.context_receipt_text ?? fixture.receipt_markdown ?? fixture.context_receipt ?? fixture.receipt ?? {};
  if (surfaceName === 'html') return reportSurfaces.html ?? fixture.html_text ?? fixture.execution_thermometer_html ?? fixture.html ?? {};
  if (surfaceName === 'closeout') return reportSurfaces.closeout ?? fixture.chat_closeout ?? fixture.closeout_text ?? fixture.closeout ?? {};
  return reportSurfaces[surfaceName] ?? {};
}

function ledgerTextFromFixture(value) {
  const candidates = [
    value.ledger_text,
    value.ledger_markdown,
    value.ledger?.text,
    value.ledger?.markdown,
    value.ledger?.body,
    value.ledger?.content,
  ];
  return candidates.find(nonEmptyString) ?? '';
}

function expectedReportCoherenceSnapshot(metricsSnapshot) {
  const expected = isPlainObject(fixture.report_coherence_expectations) ? fixture.report_coherence_expectations : {};
  return normalizeReportCoherenceSnapshot({
    spec_ids: expected.spec_ids ?? expected.reported_specs ?? expected.reported_spec_ids ?? declaredSpecs,
    final_status: expected.final_status ?? expected.goal_maestro_execution_state ?? metricsSnapshot.final_status,
    report_status: expected.report_status ?? expected.thermometer_report_status ?? metricsSnapshot.report_status,
    share_status: expected.share_status ?? expected.share_gate_status ?? metricsSnapshot.share_status,
    evidence_hashes: expected.evidence_hashes ?? expected.evidence_hash ?? metricsSnapshot.evidence_hashes,
    unproven_count: expected.unproven_count ?? expected.unproven_metrics_count ?? metricsSnapshot.unproven_count,
  });
}

function reportSurfaceSnapshot(surfaceName, surface) {
  if (typeof surface === 'string') return reportTextSnapshot(surface);
  if (!isPlainObject(surface)) return {};
  const direct = isPlainObject(surface.report_coherence)
    ? surface.report_coherence
    : isPlainObject(surface.coherence)
      ? surface.coherence
      : surface;
  if (surfaceName === 'metrics') {
    const surfaceHashes = evidenceHashesFromSurface(surface);
    return normalizeReportCoherenceSnapshot({
      spec_ids: surface.latest_loop?.spec_ids ?? surface.loops?.at?.(-1)?.spec_ids ?? surface.spec_results ?? direct.spec_ids,
      final_status: surface.final_status?.goal_maestro_execution_state ?? direct.final_status ?? direct.goal_maestro_execution_state,
      report_status: surface.final_status?.thermometer_report_status ?? direct.report_status ?? direct.thermometer_report_status,
      share_status: surface.final_status?.share_gate_status ?? surface.share_gate?.status ?? direct.share_status ?? direct.share_gate_status,
      evidence_hashes: surfaceHashes.length > 0 ? surfaceHashes : direct.evidence_hashes ?? direct.evidence_hash,
      unproven_count: direct.unproven_count ?? direct.unproven_metrics_count ?? countUnprovenMetrics(surface),
    });
  }
  return normalizeReportCoherenceSnapshot({
    spec_ids: direct.spec_ids ?? direct.reported_specs ?? direct.reported_spec_ids ?? direct.material_spec_ids ?? direct.specs ?? surface.latest_loop?.spec_ids ?? surface.loops?.at?.(-1)?.spec_ids ?? surface.spec_results,
    final_status: direct.final_status ?? direct.goal_maestro_execution_state ?? surface.final_status?.goal_maestro_execution_state,
    report_status: direct.report_status ?? direct.thermometer_report_status ?? surface.final_status?.thermometer_report_status,
    share_status: direct.share_status ?? direct.share_gate_status ?? surface.final_status?.share_gate_status ?? surface.share_gate?.status,
    evidence_hashes: direct.evidence_hashes ?? direct.evidence_hash ?? evidenceHashesFromSurface(surface),
    unproven_count: direct.unproven_count ?? direct.unproven_metrics_count ?? countUnprovenMetrics(surface),
  });
}

function reportTextSnapshot(text) {
  const normalizedText = String(text).replace(/<[^>]*>/g, ' ');
  return normalizeReportCoherenceSnapshot({
    spec_ids: textSpecIdsFromField(readReportTextField(normalizedText, ['spec_ids', 'reported_specs', 'specs'])),
    final_status: readReportTextField(normalizedText, ['final_status', 'goal_maestro_execution_state', 'Goal Maestro state']),
    report_status: readReportTextField(normalizedText, ['report_status', 'thermometer_report_status', 'Thermometer report']),
    share_status: readReportTextField(normalizedText, ['share_status', 'share_gate_status', 'Share gate']),
    evidence_hashes: readReportTextField(normalizedText, ['evidence_hashes', 'evidence hashes']),
    unproven_count: readReportTextField(normalizedText, ['unproven_count', 'unproven metrics', 'Evidence posture']),
  });
}

function readReportTextField(text, labels) {
  for (const label of labels) {
    const pattern = new RegExp(`${escapeRegExp(label)}\\s*[:=]\\s*([^\\n;<>]+)`, 'i');
    const match = pattern.exec(text);
    if (match) return match[1].trim();
  }
  return null;
}

function normalizeReportCoherenceSnapshot(value) {
  return {
    spec_ids: normalizeSpecIdArray(value.spec_ids),
    final_status: normalizeReportScalar(value.final_status),
    report_status: normalizeReportScalar(value.report_status),
    share_status: normalizeReportScalar(value.share_status),
    evidence_hashes: normalizeEvidenceHashArray(value.evidence_hashes),
    unproven_count: normalizeReportCount(value.unproven_count),
  };
}

function normalizeReportScalar(value) {
  return nonEmptyString(value) ? String(value).trim() : null;
}

function normalizeReportCount(value) {
  if (Number.isInteger(value) && value >= 0) return value;
  if (Array.isArray(value)) return value.length;
  if (nonEmptyString(value)) {
    const match = /\d+/.exec(value);
    return match ? Number.parseInt(match[0], 10) : null;
  }
  return null;
}

function normalizeEvidenceHashArray(value) {
  if (Array.isArray(value)) {
    return value.map(evidenceHashFromValue).filter(nonEmptyString);
  }
  if (nonEmptyString(value)) {
    return value
      .split(/[,;\s]+/)
      .map((entry) => entry.replace(/^[`'"]|[`'"]$/g, '').trim())
      .filter(nonEmptyString);
  }
  return [];
}

function evidenceHashFromValue(value) {
  if (typeof value === 'string') return value.trim();
  if (!isPlainObject(value)) return null;
  return value.hash ?? value.evidence_hash ?? value.sha256 ?? value.checksum ?? null;
}

function evidenceHashesFromSurface(surface) {
  const candidates = [
    surface.evidence_hashes,
    surface.evidence_hash,
    surface.sources,
    surface.evidence,
    surface.evidence_sources,
  ];
  for (const candidate of candidates) {
    const hashes = normalizeEvidenceHashArray(candidate);
    if (hashes.length > 0) return hashes;
  }
  return [];
}

function countUnprovenMetrics(surface) {
  if (Number.isInteger(surface.unproven_count)) return surface.unproven_count;
  if (Array.isArray(surface.unproven_metrics)) return surface.unproven_metrics.length;
  return null;
}

function reportCoherenceFieldPresent(snapshot, field) {
  const value = snapshot[field];
  if (Array.isArray(value)) return value.length > 0;
  if (field === 'unproven_count') return Number.isInteger(value) && value >= 0;
  return nonEmptyString(value);
}

function reportCoherenceFieldEqual(actual, expected, field) {
  if (Array.isArray(expected) || Array.isArray(actual)) {
    return sameStringArray(actual, expected);
  }
  if (field === 'unproven_count') return actual === expected;
  return actual === expected;
}

function formatReportCoherenceField(value) {
  if (Array.isArray(value)) return formatValues(value);
  if (value === null || value === undefined) return 'missing';
  return String(value);
}

function reportSurfacesAreUnproven(...snapshots) {
  return snapshots.some((snapshot) => Number.isInteger(snapshot.unproven_count) && snapshot.unproven_count > 0);
}

function closeoutSaysPass(closeout) {
  if (typeof closeout === 'string') {
    const status = readReportTextField(closeout, ['status', 'closeout_status', 'result']);
    return isCloseoutPassStatus(status) || /\b(pass|complete|completed)\b/i.test(closeout);
  }
  if (!isPlainObject(closeout)) return false;
  return isCloseoutPassStatus(closeout.status ?? closeout.closeout_status ?? closeout.result ?? closeout.final_status);
}

function isCloseoutPassStatus(value) {
  if (!nonEmptyString(value)) return false;
  return ['pass', 'passed', 'complete', 'completed', 'success'].includes(String(value).trim().toLowerCase());
}

function checksumValidationPassed(value) {
  const validation = value.checksum_validation ?? value.package_checksum_validation ?? value.checksums_validation;
  if (!isPlainObject(validation)) return false;
  const statusPass = isPassStatus(validation.status ?? validation.result ?? validation.checksum_status) || validation.valid === true;
  const entries = checksumValidationEntries(validation);
  const entriesPass = entries.length > 0 && entries.every((entry) => {
    const expected = entry.expected_hash ?? entry.expected ?? entry.hash;
    const actual = entry.actual_hash ?? entry.actual ?? entry.computed_hash;
    return nonEmptyString(expected) && nonEmptyString(actual) && expected === actual;
  });
  return statusPass && entriesPass;
}

function checksumValidationEntries(validation) {
  if (Array.isArray(validation.files)) return validation.files.filter(isPlainObject);
  if (Array.isArray(validation.entries)) return validation.entries.filter(isPlainObject);
  if (isPlainObject(validation.files)) return Object.values(validation.files).filter(isPlainObject);
  if (isPlainObject(validation.entries)) return Object.values(validation.entries).filter(isPlainObject);
  return [];
}

function textSpecIdsFromField(value) {
  if (!nonEmptyString(value)) return [];
  return value.split(/[,;\s]+/).filter(nonEmptyString);
}

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function parseLedgerGrammar(text) {
  if (!nonEmptyString(text)) {
    return { materialSections: [], malformedSpecHeadings: [] };
  }
  const lines = text.split(/\r?\n/);
  const headings = collectMarkdownHeadings(lines);
  const malformedSpecHeadings = headings
    .filter((heading) => heading.level === 3 && /^SPEC-\d+/.test(heading.text) && !MATERIAL_SPEC_HEADING_RE.test(heading.line))
    .map((heading) => heading.line.trim());
  const materialSections = headings
    .filter((heading) => MATERIAL_SPEC_HEADING_RE.test(heading.line))
    .map((heading) => ledgerMaterialSectionFromHeading(heading, headings, lines));
  return { materialSections, malformedSpecHeadings };
}

function collectMarkdownHeadings(lines) {
  const headings = [];
  for (const [index, line] of lines.entries()) {
    const match = /^(#{1,6})\s+(.+?)\s*$/.exec(line);
    if (!match) continue;
    headings.push({
      line,
      index,
      level: match[1].length,
      text: match[2],
    });
  }
  return headings;
}

function ledgerMaterialSectionFromHeading(heading, headings, lines) {
  const match = MATERIAL_SPEC_HEADING_RE.exec(heading.line);
  const nextBoundary = headings.find((candidate) => candidate.index > heading.index && candidate.level <= 3);
  const bodyLines = lines.slice(heading.index + 1, nextBoundary?.index ?? lines.length);
  return {
    headingSpecId: match[1],
    title: match[2].trim(),
    specIdValues: specIdFieldValues(bodyLines),
    nestedAuditCloseoutHeadings: nestedAuditCloseoutHeadings(bodyLines),
  };
}

function specIdFieldValues(lines) {
  return lines
    .map((line) => /^spec_id:\s*(.+?)\s*$/.exec(line))
    .filter(Boolean)
    .map((match) => match[1].trim())
    .filter(nonEmptyString);
}

function nestedAuditCloseoutHeadings(lines) {
  return lines
    .map((line) => /^(#{4,6})\s+(.+?)\s*$/.exec(line))
    .filter(Boolean)
    .map((match) => match[2].trim())
    .filter((headingText) => /\b(audit|closeout)\b/i.test(headingText));
}

function collectThermometerSpecIds(value) {
  const ids = [];
  collectThermometerSpecIdsInto(value, ids);
  return uniqueStrings(ids);
}

function collectThermometerSpecIdsInto(value, ids) {
  if (typeof value === 'string') {
    if (isMaterialSpecId(value) || isAuditUnitId(value) || isUnknownSpecId(value)) ids.push(value);
    return;
  }
  if (Array.isArray(value)) {
    for (const entry of value) collectThermometerSpecIdsInto(entry, ids);
    return;
  }
  if (!isPlainObject(value)) return;
  for (const entry of Object.values(value)) collectThermometerSpecIdsInto(entry, ids);
}

function blockingUnprovenExecutionMetrics(metrics, fixtureValue) {
  const unprovenMetrics = Array.isArray(metrics.unproven_metrics) ? metrics.unproven_metrics : [];
  const requiredFields = requiredExecutionFidelityFields(fixtureValue);
  return unprovenMetrics.filter((metric) => isRequiredExecutionFidelityMetric(metric, requiredFields));
}

function requiredExecutionFidelityFields(value) {
  const expected = isPlainObject(value.thermometer_fidelity_expectations) ? value.thermometer_fidelity_expectations : {};
  return hasNonEmptyStringArray(expected.required_execution_fidelity_fields)
    ? expected.required_execution_fidelity_fields
    : DEFAULT_REQUIRED_EXECUTION_FIDELITY_FIELDS;
}

function isRequiredExecutionFidelityMetric(metric, requiredFields) {
  const labels = unprovenMetricLabels(metric).map(normalizeMetricLabel);
  if (labels.length === 0) return true;
  return labels.some((label) => requiredFields.some((field) => metricLabelMatches(label, field)));
}

function unprovenMetricLabels(metric) {
  if (typeof metric === 'string') return [metric];
  if (!isPlainObject(metric)) return [];
  return ['name', 'field', 'path', 'metric', 'id', 'key', 'source_field']
    .map((key) => metric[key])
    .filter(nonEmptyString);
}

function metricLabelMatches(label, requiredField) {
  const normalizedRequired = normalizeMetricLabel(requiredField);
  return label === normalizedRequired || label.includes(normalizedRequired) || normalizedRequired.includes(label);
}

function normalizeMetricLabel(value) {
  return String(value).trim().toLowerCase();
}

function formatMetricNames(metrics) {
  return `[${metrics.map((metric) => unprovenMetricLabels(metric)[0] ?? String(metric)).join(', ')}]`;
}

function isPromptEnrichmentPacketRef(value) {
  return nonEmptyString(value) && (value.endsWith('.json') || value.endsWith('.md'));
}

function isDocumentAnalysisPacketRef(value) {
  if (!nonEmptyString(value)) return false;
  const fileName = value.split(/[\\/]+/).at(-1);
  return fileName === 'document_analysis_packet.json' || fileName === 'document_analysis_packet.md';
}

function isPromptEchoOnly(packet, sourcePrompt) {
  if (!nonEmptyString(sourcePrompt) || !isPlainObject(packet)) return false;
  const semanticStrings = collectSemanticStrings(packet);
  if (semanticStrings.length === 0) return false;
  const normalizedPrompt = normalizePrompt(sourcePrompt);
  return semanticStrings.every((value) => normalizePrompt(value) === normalizedPrompt);
}

function collectSemanticStrings(value, key = null) {
  if (typeof value === 'string') {
    return isMetadataStringKey(key) ? [] : [value];
  }
  if (Array.isArray(value)) return value.flatMap((entry) => collectSemanticStrings(entry));
  if (isPlainObject(value)) {
    return Object.entries(value).flatMap(([entryKey, entryValue]) => collectSemanticStrings(entryValue, entryKey));
  }
  return [];
}

function isMetadataStringKey(key) {
  return ['path', 'artifact_ref', 'ref', 'at', 'type', 'spec_id'].includes(key);
}

function normalizePrompt(value) {
  return String(value).replace(/\s+/g, ' ').trim();
}

function isPassStatus(value) {
  return value === 'pass' || value === 'PASS';
}

function isComplete(state) {
  return REQUIRED_STEPS.every((step) => state.complete[step]);
}

function isStrictConsecutiveSpecQueue(specs) {
  if (specs.length === 0) return false;
  const numbers = specs.map((specId) => {
    const match = /^SPEC-(\d{3})$/.exec(specId);
    return match ? Number.parseInt(match[1], 10) : null;
  });
  if (numbers.some((value) => value === null)) return false;
  return numbers.every((value, index) => index === 0 || value === numbers[index - 1] + 1);
}

function isEarlierTimestamp(value, openedAt) {
  if (!value || !openedAt) return false;
  const eventTime = Date.parse(value);
  const openedTime = Date.parse(openedAt);
  if (Number.isNaN(eventTime) || Number.isNaN(openedTime)) return false;
  return eventTime < openedTime;
}
