// SPEC-001/SPEC-002/SPEC-003 Goal Maestro P0 execution harness.
// Validates a synthetic execute-loop event fixture for one-active-SPEC order,
// post-open evidence, oracle proof, local commit status, and parent validation
// before the next SPEC can open. SPEC-002 fixtures opt into durable pre-edit
// artifact validation with pre_edit_gate_required:true. SPEC-003 fixtures opt
// into prompt enrichment packet validation with prompt_enrichment_packet_required:true.
//
//   node scripts/goal-maestro-p0-harness.mjs <linear-pipeline-fixture.json>

import { readText, runChecks } from './lib/harness.mjs';

const LINEAR_STOP_STATE = 'NEEDS_LINEAR_SPEC_PIPELINE';
const PRE_EDIT_STOP_STATE = 'NEEDS_PRE_EDIT_GATE_ARTIFACT';
const PROMPT_ENRICHMENT_STOP_STATE = 'NEEDS_PROMPT_ENRICHMENT_PACKET';
const PRE_EDIT_CONTRACT = 'goal-maestro-p0-pre-edit-gate';
const PROMPT_ENRICHMENT_CONTRACT = 'goal-maestro-p0-prompt-enrichment-packet';
const PRE_EDIT_EVENT_TYPE = 'pre_edit_gate_artifact';
const PROMPT_ENRICHMENT_EVENT_TYPE = 'prompt_enrichment_packet';
const EVENT_TYPES = new Set([
  PRE_EDIT_EVENT_TYPE,
  PROMPT_ENRICHMENT_EVENT_TYPE,
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
const preEditGateEvents = [];
const promptEnrichmentPacketEvents = [];
let firstLoopStartIndex = null;
let firstMaterialEditIndex = null;
const specStates = new Map();
for (const specId of declaredSpecs) {
  specStates.set(specId, {
    opened: false,
    openIndex: null,
    openedAt: null,
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

  if (!specStates.has(specId)) {
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

const harnessTitle = promptEnrichmentPacketRequired
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

function sameStringArray(left, right) {
  if (!Array.isArray(left) || !Array.isArray(right) || left.length !== right.length) return false;
  return left.every((value, index) => value === right[index]);
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

function isPromptEnrichmentPacketRef(value) {
  return nonEmptyString(value) && (value.endsWith('.json') || value.endsWith('.md'));
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
