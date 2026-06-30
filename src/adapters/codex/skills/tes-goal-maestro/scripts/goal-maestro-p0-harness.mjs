// SPEC-001 Goal Maestro P0 linear pipeline harness.
// Validates a synthetic execute-loop event fixture for one-active-SPEC order,
// post-open evidence, oracle proof, local commit status, and parent validation
// before the next SPEC can open.
//
//   node scripts/goal-maestro-p0-harness.mjs <linear-pipeline-fixture.json>

import { readText, runChecks } from './lib/harness.mjs';

const STOP_STATE = 'NEEDS_LINEAR_SPEC_PIPELINE';
const EVENT_TYPES = new Set([
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
    detail: new Set(declaredSpecs).size === declaredSpecs.length ? undefined : `${STOP_STATE}: duplicate SPEC id in declared_specs`,
  },
  {
    name: 'declared SPEC queue is strict and consecutive',
    pass: isStrictConsecutiveSpecQueue(declaredSpecs),
    detail: isStrictConsecutiveSpecQueue(declaredSpecs) ? undefined : `${STOP_STATE}: declared_specs must be SPEC-NNN in consecutive order`,
  },
  {
    name: 'event stream is present',
    pass: events.length > 0,
    detail: events.length > 0 ? undefined : `${STOP_STATE}: no pipeline events were provided`,
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

  if (eventType === 'open_spec') {
    openSpec(eventIndex, event);
    continue;
  }

  applySpecEvent(eventIndex, event);
}

for (const specId of declaredSpecs) {
  const state = specStates.get(specId);
  checks.push({
    name: `${specId} opened`,
    pass: state.opened,
    detail: state.opened ? undefined : `${STOP_STATE}: ${specId} never opened`,
  });

  for (const step of REQUIRED_STEPS) {
    checks.push({
      name: `${specId} ${step} after open`,
      pass: state.complete[step],
      detail: state.complete[step] ? undefined : `${STOP_STATE}: ${specId} lacks ${REQUIRED_STEP_LABELS[step]} after ACTIVE_SPEC opened`,
    });
  }
}

runChecks(`SPEC-001 goal-maestro-p0-linear-pipeline (${STOP_STATE})`, checks);

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
  checks.push({ name, pass: false, detail: `${STOP_STATE}: ${detail}` });
}

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function nonEmptyString(value) {
  return typeof value === 'string' && value.trim().length > 0;
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
