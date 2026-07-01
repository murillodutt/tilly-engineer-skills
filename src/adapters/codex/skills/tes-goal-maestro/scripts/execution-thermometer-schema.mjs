// SPEC-001 execution thermometer schema validator.
// Node-only validator for the generation-time `exec_identity.yaml` plus
// `exec_metrics.json` data contract. It intentionally supports only the simple
// YAML subset used by the schema fixtures: nested maps, scalar values, and
// indentation-based sections.
//
//   node scripts/execution-thermometer-schema.mjs <exec_identity.yaml> <exec_metrics.json>

import { runChecks, readText } from './lib/harness.mjs';

const [identityPath, metricsPath] = process.argv.slice(2);

if (!identityPath || !metricsPath) {
  console.error('usage: node scripts/execution-thermometer-schema.mjs <exec_identity.yaml> <exec_metrics.json>');
  process.exit(2);
}

let identity;
let metrics;

try {
  identity = parseSimpleYaml(readText(identityPath));
} catch (error) {
  console.error(`identity YAML invalid: ${error.message}`);
  process.exit(2);
}

try {
  metrics = JSON.parse(readText(metricsPath));
} catch (error) {
  console.error(`metrics JSON invalid: ${error.message}`);
  process.exit(2);
}

const REPORT_STATUS = new Set([
  'generation_pending',
  'local_package_ready',
  'local_package_blocked',
  'share_blocked',
  'shared_draft_pr',
]);

const SHARE_GATE_STATUS = new Set([
  'not_requested',
  'not_gold',
  'proposed_gold',
  'declined',
  'approved_local_export',
  'draft_pr_opened',
  'blocked_by_sanitization',
  'blocked_by_missing_destination',
  'blocked_by_owner_decision',
  'blocked_by_github_auth',
]);

const SIGNAL_STATUS = new Set(['on_track', 'unproven', 'needs_review', 'blocked', 'fail']);
const METRIC_STATUS = new Set(['proven', 'unproven', 'blocked', 'not_applicable']);
const SPEC_STATUS = new Set(['pass', 'repaired_pass', 'skipped', 'unproven', 'needs_review', 'blocked', 'fail']);
const GOLD_CLASSIFICATION = new Set(['ordinary', 'useful', 'gold']);
const SANITIZER_STATUS = new Set(['pass', 'fail', 'unproven']);
const HARNESS_ADAPTER = new Set(['codex', 'claude', 'cursor', 'other']);
const MODEL_METADATA_SOURCE = new Set(['operator_declared', 'runtime_reported', 'unproven']);
const GIT_REPO_STATE = new Set(['clean', 'dirty', 'unproven']);
const SPEC_TYPE = new Set(['functional', 'non_functional', 'governance', 'safety']);
const EVIDENCE_TYPE = new Set(['test_report', 'oracle', 'screenshot', 'fixture', 'ledger', 'commit', 'manual_review']);
const EVIDENCE_SOURCE = new Set(['artifact', 'generated', 'operator_declared']);
const METRIC_UNIT = new Set(['percent', 'count', 'ms', 'tokens', 'usd', 'text']);
const SIGNAL_NAME = new Set(['Delivery', 'Fidelity', 'Proof', 'Efficiency', 'Protection']);

const IDENTITY_TOP_LEVEL = [
  'schema_version',
  'report_id',
  'project_id',
  'series_id',
  'run_id',
  'generated_at_utc',
  'timezone',
  'report_class',
  'report_status',
  'harness',
  'model',
  'anchor',
  'ledger',
  'git',
  'privacy',
  'share',
];

const METRICS_TOP_LEVEL = [
  'schema_version',
  'identity_ref',
  'project',
  'series',
  'sources',
  'run_summary',
  'loop_summary',
  'loops',
  'latest_loop',
  'spec_results',
  'five_signals',
  'lens_results',
  'flash_fry',
  'cache_economy',
  'model_profile',
  'oracle_strength',
  'structural_health',
  'runtime_visual',
  'commits',
  'audit',
  'anti_gaming_flags',
  'privacy',
  'gold_analysis',
  'share_gate',
  'unproven_metrics',
  'final_status',
];

const LOOP_FIELDS = [
  'loop_id',
  'label',
  'started_at_utc',
  'ended_at_utc',
  'objective',
  'status',
  'scores',
  'spec_ids',
  'evidence_refs',
  'summary',
  'next_actions',
];

const SPEC_RESULT_FIELDS = [
  'spec_id',
  'title',
  'type',
  'status',
  'intent_score',
  'fidelity_score',
  'proof_score',
  'attempts',
  'rework_count',
  'evidence_refs',
  'unproven_metrics',
  'notes',
];

const EVIDENCE_REF_FIELDS = ['ref', 'type', 'description', 'source', 'path', 'hash', 'sanitized'];
const FIVE_SIGNAL_FIELDS = ['signal', 'status', 'score', 'vs_plan', 'notes', 'evidence_refs'];
const SHARE_APPROVAL_FIELDS = [
  'approved_at_utc',
  'run_id',
  'destination_repository',
  'destination_branch',
  'payload_hash',
  'manifest_hash',
];
const METRIC_FIELDS = ['name', 'value', 'unit', 'status', 'evidence_refs', 'notes'];

const checks = [];

validateIdentity(identity, checks);
validateMetrics(metrics, checks);

const declaredRefs = new Set(Array.isArray(metrics?.sources) ? metrics.sources.map((source) => source?.ref).filter(Boolean) : []);
validateEvidenceRefs(metrics?.loops, 'metrics.loops', declaredRefs, checks);
validateEvidenceRefs(metrics?.latest_loop, 'metrics.latest_loop', declaredRefs, checks);
validateEvidenceRefs(metrics?.spec_results, 'metrics.spec_results', declaredRefs, checks);
validateEvidenceRefs(metrics?.five_signals, 'metrics.five_signals', declaredRefs, checks);
validateEvidenceRefs(metrics?.gold_analysis, 'metrics.gold_analysis', declaredRefs, checks);
validateEvidenceRefs(metrics?.share_gate, 'metrics.share_gate', declaredRefs, checks);
validateMetricsRecursively(metrics, 'metrics', declaredRefs, checks);

runChecks('SPEC-001 execution-thermometer-schema', checks);

function validateIdentity(value, target) {
  requirePlainObject(value, 'identity', target);
  requireExactKeys(value, 'identity', IDENTITY_TOP_LEVEL, target);
  expectLiteral(value?.schema_version, 1, 'identity.schema_version', target);
  expectNonEmptyString(value?.report_id, 'identity.report_id', target);
  expectNonEmptyString(value?.project_id, 'identity.project_id', target);
  expectNonEmptyString(value?.series_id, 'identity.series_id', target);
  expectNonEmptyString(value?.run_id, 'identity.run_id', target);
  expectTimestamp(value?.generated_at_utc, 'identity.generated_at_utc', target);
  expectNonEmptyString(value?.timezone, 'identity.timezone', target);
  expectLiteral(value?.report_class, 'execution_thermometer', 'identity.report_class', target);
  expectEnum(value?.report_status, REPORT_STATUS, 'identity.report_status', target);

  requireExactKeys(value?.harness, 'identity.harness', ['name', 'version', 'adapter', 'command', 'schema_version'], target);
  expectLiteral(value?.harness?.name, 'tes-goal-maestro', 'identity.harness.name', target);
  expectNonEmptyString(value?.harness?.version, 'identity.harness.version', target);
  expectEnum(value?.harness?.adapter, HARNESS_ADAPTER, 'identity.harness.adapter', target);
  expectLiteral(value?.harness?.command, '--execute-loop', 'identity.harness.command', target);
  expectNonEmptyString(value?.harness?.schema_version, 'identity.harness.schema_version', target);

  requireExactKeys(value?.model, 'identity.model', ['provider', 'identity', 'reasoning_profile', 'effort_multiplier', 'metadata_source'], target);
  expectNonEmptyString(value?.model?.provider, 'identity.model.provider', target);
  expectNonEmptyString(value?.model?.identity, 'identity.model.identity', target);
  expectNonEmptyString(value?.model?.reasoning_profile, 'identity.model.reasoning_profile', target);
  expectNonEmptyString(value?.model?.effort_multiplier, 'identity.model.effort_multiplier', target);
  expectEnum(value?.model?.metadata_source, MODEL_METADATA_SOURCE, 'identity.model.metadata_source', target);

  requireExactKeys(value?.anchor, 'identity.anchor', ['path', 'hash', 'class'], target);
  expectNonEmptyString(value?.anchor?.path, 'identity.anchor.path', target);
  expectNonEmptyString(value?.anchor?.hash, 'identity.anchor.hash', target);
  expectNonEmptyString(value?.anchor?.class, 'identity.anchor.class', target);

  requireExactKeys(value?.ledger, 'identity.ledger', ['path', 'hash', 'read_mode', 'extraction_hash'], target);
  expectNonEmptyString(value?.ledger?.path, 'identity.ledger.path', target);
  expectNonEmptyString(value?.ledger?.hash, 'identity.ledger.hash', target);
  expectLiteral(value?.ledger?.read_mode, 'read_only', 'identity.ledger.read_mode', target);
  expectNonEmptyString(value?.ledger?.extraction_hash, 'identity.ledger.extraction_hash', target);

  requireExactKeys(value?.git, 'identity.git', ['repo_state', 'head'], target);
  expectEnum(value?.git?.repo_state, GIT_REPO_STATE, 'identity.git.repo_state', target);
  expectNonEmptyString(value?.git?.head, 'identity.git.head', target);

  requireExactKeys(value?.privacy, 'identity.privacy', ['sanitizer_version', 'private_vocabulary_status'], target);
  expectNonEmptyString(value?.privacy?.sanitizer_version, 'identity.privacy.sanitizer_version', target);
  expectEnum(value?.privacy?.private_vocabulary_status, SANITIZER_STATUS, 'identity.privacy.private_vocabulary_status', target);

  requireExactKeys(value?.share, 'identity.share', ['status', 'approval'], target);
  expectEnum(value?.share?.status, SHARE_GATE_STATUS, 'identity.share.status', target);
  requireExactKeys(value?.share?.approval, 'identity.share.approval', SHARE_APPROVAL_FIELDS, target);
  for (const key of SHARE_APPROVAL_FIELDS) {
    expectNonEmptyString(value?.share?.approval?.[key], `identity.share.approval.${key}`, target);
  }
}

function validateMetrics(value, target) {
  requirePlainObject(value, 'metrics', target);
  requireExactKeys(value, 'metrics', METRICS_TOP_LEVEL, target);
  expectLiteral(value?.schema_version, 1, 'metrics.schema_version', target);
  expectLiteral(value?.identity_ref, 'exec_identity.yaml', 'metrics.identity_ref', target);

  for (const key of ['project', 'series', 'run_summary', 'loop_summary', 'latest_loop', 'flash_fry', 'cache_economy', 'model_profile', 'oracle_strength', 'structural_health', 'runtime_visual', 'commits', 'audit', 'privacy', 'gold_analysis', 'share_gate', 'final_status']) {
    requirePlainObject(value?.[key], `metrics.${key}`, target);
  }
  for (const key of ['sources', 'loops', 'spec_results', 'five_signals', 'lens_results', 'anti_gaming_flags', 'unproven_metrics']) {
    expectArray(value?.[key], `metrics.${key}`, target);
  }

  if (Array.isArray(value?.sources)) {
    value.sources.forEach((source, index) => {
      validateEvidenceSource(source, `metrics.sources[${index}]`, target);
    });
  }
  if (Array.isArray(value?.loops)) {
    value.loops.forEach((loop, index) => {
      validateLoop(loop, `metrics.loops[${index}]`, target);
    });
  }
  if (isPlainObject(value?.latest_loop)) {
    validateLoop(value.latest_loop, 'metrics.latest_loop', target);
  }
  if (Array.isArray(value?.spec_results)) {
    value.spec_results.forEach((result, index) => {
      validateSpecResult(result, `metrics.spec_results[${index}]`, target);
    });
  }
  validateFiveSignals(value?.five_signals, target);
  validateGoldAnalysis(value?.gold_analysis, target);
  validateShareGate(value?.share_gate, target);
  validateFinalStatus(value?.final_status, target);
}

function validateEvidenceSource(source, path, target) {
  requireExactKeys(source, path, EVIDENCE_REF_FIELDS, target);
  expectNonEmptyString(source?.ref, `${path}.ref`, target);
  expectEnum(source?.type, EVIDENCE_TYPE, `${path}.type`, target);
  expectNonEmptyString(source?.description, `${path}.description`, target);
  expectEnum(source?.source, EVIDENCE_SOURCE, `${path}.source`, target);
  expectNonEmptyString(source?.path, `${path}.path`, target);
  expectNonEmptyString(source?.hash, `${path}.hash`, target);
  expectBoolean(source?.sanitized, `${path}.sanitized`, target);
}

function validateLoop(loop, path, target) {
  requireExactKeys(loop, path, LOOP_FIELDS, target);
  expectNonEmptyString(loop?.loop_id, `${path}.loop_id`, target);
  expectNonEmptyString(loop?.label, `${path}.label`, target);
  expectTimestamp(loop?.started_at_utc, `${path}.started_at_utc`, target);
  expectTimestamp(loop?.ended_at_utc, `${path}.ended_at_utc`, target);
  expectString(loop?.objective, `${path}.objective`, target);
  expectEnum(loop?.status, SIGNAL_STATUS, `${path}.status`, target);
  requirePlainObject(loop?.scores, `${path}.scores`, target);
  expectArray(loop?.spec_ids, `${path}.spec_ids`, target);
  expectArray(loop?.evidence_refs, `${path}.evidence_refs`, target);
  expectString(loop?.summary, `${path}.summary`, target);
  expectArray(loop?.next_actions, `${path}.next_actions`, target);
}

function validateSpecResult(result, path, target) {
  requireExactKeys(result, path, SPEC_RESULT_FIELDS, target);
  expectNonEmptyString(result?.spec_id, `${path}.spec_id`, target);
  expectNonEmptyString(result?.title, `${path}.title`, target);
  expectEnum(result?.type, SPEC_TYPE, `${path}.type`, target);
  expectEnum(result?.status, SPEC_STATUS, `${path}.status`, target);
  expectNullableNumber(result?.intent_score, `${path}.intent_score`, target);
  expectNullableNumber(result?.fidelity_score, `${path}.fidelity_score`, target);
  expectNullableNumber(result?.proof_score, `${path}.proof_score`, target);
  expectNumber(result?.attempts, `${path}.attempts`, target);
  expectNumber(result?.rework_count, `${path}.rework_count`, target);
  expectArray(result?.evidence_refs, `${path}.evidence_refs`, target);
  expectArray(result?.unproven_metrics, `${path}.unproven_metrics`, target);
  expectString(result?.notes, `${path}.notes`, target);
}

function validateFiveSignals(signals, target) {
  if (!Array.isArray(signals)) {
    return;
  }
  target.push({
    name: 'metrics.five_signals has five signal rows',
    pass: signals.length === 5,
    detail: signals.length === 5 ? undefined : `expected 5 signal rows, got ${signals.length}`,
  });
  const seen = new Set();
  signals.forEach((signal, index) => {
    const path = `metrics.five_signals[${index}]`;
    requireExactKeys(signal, path, FIVE_SIGNAL_FIELDS, target);
    expectEnum(signal?.signal, SIGNAL_NAME, `${path}.signal`, target);
    expectEnum(signal?.status, SIGNAL_STATUS, `${path}.status`, target);
    expectNullableNumber(signal?.score, `${path}.score`, target);
    expectNullableNumber(signal?.vs_plan, `${path}.vs_plan`, target);
    expectString(signal?.notes, `${path}.notes`, target);
    expectArray(signal?.evidence_refs, `${path}.evidence_refs`, target);
    if (SIGNAL_NAME.has(signal?.signal)) {
      seen.add(signal.signal);
    }
  });
  for (const signal of SIGNAL_NAME) {
    target.push({
      name: `metrics.five_signals includes ${signal}`,
      pass: seen.has(signal),
      detail: seen.has(signal) ? undefined : `${signal} signal row is missing`,
    });
  }
}

function validateGoldAnalysis(gold, target) {
  if (!isPlainObject(gold)) {
    return;
  }
  if (hasOwn(gold, 'classification')) {
    expectEnum(gold.classification, GOLD_CLASSIFICATION, 'metrics.gold_analysis.classification', target);
  }
  if (hasOwn(gold, 'sanitizer_status')) {
    expectEnum(gold.sanitizer_status, SANITIZER_STATUS, 'metrics.gold_analysis.sanitizer_status', target);
  }
  if (hasOwn(gold, 'evidence_refs')) {
    expectArray(gold.evidence_refs, 'metrics.gold_analysis.evidence_refs', target);
  }
}

function validateShareGate(shareGate, target) {
  if (!isPlainObject(shareGate)) {
    return;
  }
  expectEnum(shareGate.status, SHARE_GATE_STATUS, 'metrics.share_gate.status', target);
  if (hasOwn(shareGate, 'sanitizer_status')) {
    expectEnum(shareGate.sanitizer_status, SANITIZER_STATUS, 'metrics.share_gate.sanitizer_status', target);
  }
  if (hasOwn(shareGate, 'approval')) {
    requireExactKeys(shareGate.approval, 'metrics.share_gate.approval', SHARE_APPROVAL_FIELDS, target);
    for (const key of SHARE_APPROVAL_FIELDS) {
      expectNonEmptyString(shareGate.approval?.[key], `metrics.share_gate.approval.${key}`, target);
    }
  }
}

function validateFinalStatus(finalStatus, target) {
  if (!isPlainObject(finalStatus)) {
    return;
  }
  requireExactKeys(finalStatus, 'metrics.final_status', ['goal_maestro_execution_state', 'thermometer_report_status', 'share_gate_status', 'notes'], target);
  expectNonEmptyString(finalStatus.goal_maestro_execution_state, 'metrics.final_status.goal_maestro_execution_state', target);
  expectEnum(finalStatus.thermometer_report_status, REPORT_STATUS, 'metrics.final_status.thermometer_report_status', target);
  expectEnum(finalStatus.share_gate_status, SHARE_GATE_STATUS, 'metrics.final_status.share_gate_status', target);
  expectString(finalStatus.notes, 'metrics.final_status.notes', target);
}

function validateEvidenceRefs(value, path, declaredRefs, target) {
  if (Array.isArray(value)) {
    value.forEach((item, index) => {
      validateEvidenceRefs(item, `${path}[${index}]`, declaredRefs, target);
    });
    return;
  }
  if (!isPlainObject(value)) {
    return;
  }
  if (Array.isArray(value.evidence_refs)) {
    for (const ref of value.evidence_refs) {
      target.push({
        name: `${path}.evidence_refs declares ${ref}`,
        pass: typeof ref === 'string' && declaredRefs.has(ref),
        detail: typeof ref === 'string' && declaredRefs.has(ref) ? undefined : `${path}.evidence_refs contains undeclared source ref "${ref}"`,
      });
    }
  }
  for (const [key, child] of Object.entries(value)) {
    if (key !== 'evidence_refs') {
      validateEvidenceRefs(child, `${path}.${key}`, declaredRefs, target);
    }
  }
}

function validateMetricsRecursively(value, path, declaredRefs, target) {
  if (Array.isArray(value)) {
    value.forEach((item, index) => {
      validateMetricsRecursively(item, `${path}[${index}]`, declaredRefs, target);
    });
    return;
  }
  if (!isPlainObject(value)) {
    return;
  }

  const metricFieldsPresent = METRIC_FIELDS.some((field) => hasOwn(value, field));
  const requiredMetricItem = /^metrics\.(lens_results|unproven_metrics)\[\d+\]$/.test(path);
  if (requiredMetricItem || (isMetricContainerPath(path) && metricFieldsPresent)) {
    validateMetric(value, path, declaredRefs, target);
    return;
  }

  for (const [key, child] of Object.entries(value)) {
    validateMetricsRecursively(child, `${path}.${key}`, declaredRefs, target);
  }
}

function isMetricContainerPath(path) {
  return /^metrics\.(flash_fry|cache_economy|model_profile|oracle_strength|structural_health|runtime_visual|commits|audit)(\.|$)/.test(path)
    || /^metrics\.(lens_results|unproven_metrics)\[\d+\](\.|$)/.test(path);
}

function validateMetric(metric, path, declaredRefs, target) {
  requireExactKeys(metric, path, METRIC_FIELDS, target);
  expectNonEmptyString(metric.name, `${path}.name`, target);
  expectEnum(metric.unit, METRIC_UNIT, `${path}.unit`, target);
  expectEnum(metric.status, METRIC_STATUS, `${path}.status`, target);
  expectArray(metric.evidence_refs, `${path}.evidence_refs`, target);
  expectString(metric.notes, `${path}.notes`, target);

  const refs = Array.isArray(metric.evidence_refs) ? metric.evidence_refs : [];
  target.push({
    name: `${path}: proven metric has evidence`,
    pass: metric.status !== 'proven' || refs.length > 0,
    detail: metric.status !== 'proven' || refs.length > 0 ? undefined : 'status is proven but evidence_refs is empty',
  });

  for (const ref of refs) {
    target.push({
      name: `${path}: metric evidence ref ${ref} is declared`,
      pass: typeof ref === 'string' && declaredRefs.has(ref),
      detail: typeof ref === 'string' && declaredRefs.has(ref) ? undefined : `metric evidence ref "${ref}" is not present in metrics.sources[].ref`,
    });
  }
}

function requireExactKeys(value, path, keys, target) {
  if (!requirePlainObject(value, path, target)) {
    return;
  }
  const allowed = new Set(keys);
  for (const key of keys) {
    target.push({
      name: `${path}.${key} is present`,
      pass: hasOwn(value, key),
      detail: hasOwn(value, key) ? undefined : `missing required field ${path}.${key}`,
    });
  }
  const unknown = Object.keys(value).filter((key) => !allowed.has(key));
  target.push({
    name: `${path} has no unknown renderer-facing fields`,
    pass: unknown.length === 0,
    detail: unknown.length === 0 ? undefined : `unknown field(s): ${unknown.join(', ')}`,
  });
}

function requirePlainObject(value, path, target) {
  const pass = isPlainObject(value);
  target.push({
    name: `${path} is an object`,
    pass,
    detail: pass ? undefined : `${path} must be an object`,
  });
  return pass;
}

function expectLiteral(value, expected, path, target) {
  target.push({
    name: `${path} equals ${JSON.stringify(expected)}`,
    pass: value === expected,
    detail: value === expected ? undefined : `got ${JSON.stringify(value)}, expected ${JSON.stringify(expected)}`,
  });
}

function expectEnum(value, allowed, path, target) {
  target.push({
    name: `${path} uses canonical enum value`,
    pass: allowed.has(value),
    detail: allowed.has(value) ? undefined : `got ${JSON.stringify(value)}, expected one of: ${[...allowed].join(', ')}`,
  });
}

function expectArray(value, path, target) {
  target.push({
    name: `${path} is an array`,
    pass: Array.isArray(value),
    detail: Array.isArray(value) ? undefined : `${path} must be an array`,
  });
}

function expectBoolean(value, path, target) {
  target.push({
    name: `${path} is boolean`,
    pass: typeof value === 'boolean',
    detail: typeof value === 'boolean' ? undefined : `${path} must be boolean`,
  });
}

function expectNumber(value, path, target) {
  target.push({
    name: `${path} is a number`,
    pass: typeof value === 'number' && Number.isFinite(value),
    detail: typeof value === 'number' && Number.isFinite(value) ? undefined : `${path} must be a finite number`,
  });
}

function expectNullableNumber(value, path, target) {
  const pass = value === null || (typeof value === 'number' && Number.isFinite(value));
  target.push({
    name: `${path} is null or number`,
    pass,
    detail: pass ? undefined : `${path} must be null or a finite number`,
  });
}

function expectString(value, path, target) {
  target.push({
    name: `${path} is a string`,
    pass: typeof value === 'string',
    detail: typeof value === 'string' ? undefined : `${path} must be a string`,
  });
}

function expectNonEmptyString(value, path, target) {
  const pass = typeof value === 'string' && value.length > 0;
  target.push({
    name: `${path} is a non-empty string`,
    pass,
    detail: pass ? undefined : `${path} must be a non-empty string`,
  });
}

function expectTimestamp(value, path, target) {
  const pass = typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(value);
  target.push({
    name: `${path} is UTC timestamp`,
    pass,
    detail: pass ? undefined : `${path} must match YYYY-MM-DDTHH:MM:SSZ`,
  });
}

function hasOwn(value, key) {
  return Object.hasOwn(Object(value), key);
}

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function parseSimpleYaml(text) {
  const root = {};
  const stack = [{ indent: -1, value: root }];
  const lines = text.split(/\r?\n/);

  lines.forEach((rawLine, index) => {
    if (/^\s*(#.*)?$/.test(rawLine)) {
      return;
    }
    const match = rawLine.match(/^(\s*)([A-Za-z0-9_]+):(?:\s*(.*))?$/);
    if (!match) {
      throw new Error(`line ${index + 1}: expected "key: value"`);
    }
    const indent = match[1].length;
    if (indent % 2 !== 0) {
      throw new Error(`line ${index + 1}: indentation must use multiples of two spaces`);
    }
    const key = match[2];
    const rawValue = match[3] ?? '';

    while (stack.length > 1 && indent <= stack.at(-1).indent) {
      stack.pop();
    }
    const parent = stack.at(-1).value;
    if (hasOwn(parent, key)) {
      throw new Error(`line ${index + 1}: duplicate key "${key}"`);
    }

    if (rawValue === '') {
      const child = {};
      parent[key] = child;
      stack.push({ indent, value: child });
      return;
    }
    parent[key] = parseYamlScalar(rawValue);
  });

  return root;
}

function parseYamlScalar(rawValue) {
  const value = stripYamlComment(rawValue).trim();
  if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
    return value.slice(1, -1);
  }
  if (value === 'true') {
    return true;
  }
  if (value === 'false') {
    return false;
  }
  if (value === 'null') {
    return null;
  }
  if (/^-?\d+(\.\d+)?$/.test(value)) {
    return Number(value);
  }
  return value;
}

function stripYamlComment(value) {
  let quote = null;
  for (let index = 0; index < value.length; index++) {
    const char = value[index];
    if ((char === '"' || char === "'") && value[index - 1] !== '\\') {
      quote = quote === char ? null : quote ?? char;
    }
    if (char === '#' && quote === null && /\s/.test(value[index - 1] ?? ' ')) {
      return value.slice(0, index);
    }
  }
  return value;
}
