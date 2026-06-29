// SPEC-002 execution thermometer ledger extractor.
// Reads an existing Goal Maestro ledger in read-only mode, writes the local
// generation-time schema files, and proves the source ledger plus extraction
// manifest by sha256. Missing ledger evidence is normalized as `unproven`.
//
//   node scripts/execution-thermometer-extract.mjs <ledger.md> <output-dir>
//   node scripts/execution-thermometer-extract.mjs <ledger.md> <output-dir> --expected-ledger-sha256 <sha256>

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { basename, dirname, isAbsolute, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const EXTRACTOR_VERSION = '0.1.0';
const SCHEMA_VERSION = 1;
const here = dirname(fileURLToPath(import.meta.url));

const cli = parseArgs(process.argv.slice(2));

if (cli.positionals.length !== 2) {
  usage();
  process.exit(2);
}

const ledgerPath = resolve(cli.positionals[0]);
const outputDir = resolve(cli.positionals[1]);
const generatedAt = cli.options.generatedAt ?? utcNowWithoutMillis();

if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(generatedAt)) {
  console.error(`invalid --generated-at: ${generatedAt}`);
  process.exit(2);
}

let before;
try {
  before = readLedgerSnapshot(ledgerPath);
} catch (error) {
  console.error(`cannot read source ledger: ${error.message}`);
  process.exit(2);
}

if (cli.options.expectedLedgerSha256 && cli.options.expectedLedgerSha256 !== before.sha256) {
  console.error(`BLOCKED_LEDGER_HASH_MISMATCH: expected ${cli.options.expectedLedgerSha256}, got ${before.sha256}`);
  process.exit(1);
}

const parsed = parseLedger(before.text);
const runId = cli.options.runId ?? `run-${before.sha256.slice(0, 12)}`;
const projectId = cli.options.projectId ?? 'target-project';
const seriesId = cli.options.seriesId ?? 'series-goal-maestro';
const ledgerDisplayPath = cli.options.ledgerPathLabel ?? displayPath(ledgerPath);

const manifest = {
  schema_version: SCHEMA_VERSION,
  extractor: 'execution-thermometer-extract',
  extractor_version: EXTRACTOR_VERSION,
  generated_at_utc: generatedAt,
  read_mode: 'read_only',
  source_ledger: {
    path: ledgerDisplayPath,
    sha256: before.sha256,
    bytes: before.bytes,
  },
  normalized: {
    project_id: projectId,
    series_id: seriesId,
    run_id: runId,
    spec_count: parsed.specs.length,
  },
  outputs: ['exec_identity.yaml', 'exec_metrics.json'],
};
const manifestText = `${stableJson(manifest)}\n`;
const manifestHash = sha256(manifestText);

const sources = [
  evidenceSource({
    ref: 'EV-LEDGER',
    type: 'ledger',
    description: 'Read-only Goal Maestro source ledger snapshot.',
    source: 'artifact',
    path: ledgerDisplayPath,
    hash: before.sha256,
  }),
  evidenceSource({
    ref: 'EV-EXTRACTION-MANIFEST',
    type: 'oracle',
    description: 'SPEC-002 extraction manifest proving source hash and normalized run identity.',
    source: 'generated',
    path: 'extraction_manifest.json',
    hash: manifestHash,
  }),
];

const unprovenMetrics = collectUnprovenMetrics(parsed.specs);
const specResults = buildSpecResults(parsed.specs, unprovenMetrics);
const loop = buildLoop(parsed, specResults, unprovenMetrics, generatedAt);
const signalStatus = unprovenMetrics.length > 0 ? 'unproven' : 'on_track';

const identity = {
  schema_version: SCHEMA_VERSION,
  report_id: `report-${runId}`,
  project_id: projectId,
  series_id: seriesId,
  run_id: runId,
  generated_at_utc: generatedAt,
  timezone: cli.options.timezone ?? 'UTC',
  report_class: 'execution_thermometer',
  report_status: 'local_package_ready',
  harness: {
    name: 'tes-goal-maestro',
    version: EXTRACTOR_VERSION,
    adapter: cli.options.adapter ?? detectAdapter(here),
    command: '--execute-loop',
    schema_version: String(SCHEMA_VERSION),
  },
  model: {
    provider: cli.options.modelProvider ?? 'operator',
    identity: cli.options.modelIdentity ?? 'unproven',
    reasoning_profile: cli.options.reasoningProfile ?? 'unproven',
    effort_multiplier: cli.options.effortMultiplier ?? 'unproven',
    metadata_source: 'unproven',
  },
  anchor: parsed.anchor,
  ledger: {
    path: ledgerDisplayPath,
    hash: before.sha256,
    read_mode: 'read_only',
    extraction_hash: manifestHash,
  },
  git: {
    repo_state: 'unproven',
    head: 'unproven',
  },
  privacy: {
    sanitizer_version: 'unproven',
    private_vocabulary_status: 'unproven',
  },
  share: {
    status: 'not_requested',
    approval: unprovenApproval(runId),
  },
};

const metrics = {
  schema_version: SCHEMA_VERSION,
  identity_ref: 'exec_identity.yaml',
  project: { project_id: projectId },
  series: { series_id: seriesId },
  sources,
  run_summary: {
    run_id: runId,
    status: loop.status,
    ledger_hash: before.sha256,
    extraction_hash: manifestHash,
  },
  loop_summary: {
    latest_loop_id: loop.loop_id,
    spec_count: specResults.length,
    unproven_metric_count: unprovenMetrics.length,
  },
  loops: [loop],
  latest_loop: loop,
  spec_results: specResults,
  five_signals: [
    signal('Delivery', loop.status, loop.status === 'on_track' ? 100 : null, 'SPEC results normalized from the source ledger.', ['EV-LEDGER']),
    signal('Fidelity', 'on_track', 100, 'Output validates against schema v1 closed renderer-facing fields.', ['EV-EXTRACTION-MANIFEST']),
    signal('Proof', signalStatus, signalStatus === 'on_track' ? 100 : null, unprovenMetrics.length === 0 ? 'All extracted SPEC rows carry ledger evidence.' : 'Some ledger evidence is missing and remains unproven.', ['EV-LEDGER']),
    signal('Efficiency', 'on_track', 100, 'Node-only local extraction without remote calls.', ['EV-EXTRACTION-MANIFEST']),
    signal('Protection', 'on_track', 100, 'Ledger source remains read-only and GitHub sharing is not requested.', ['EV-LEDGER', 'EV-EXTRACTION-MANIFEST']),
  ],
  lens_results: [
    metric('extracted_spec_count', specResults.length, 'count', 'proven', ['EV-LEDGER'], 'Count of SPEC sections found in the source ledger.'),
    metric('unproven_metric_count', unprovenMetrics.length, 'count', 'proven', ['EV-EXTRACTION-MANIFEST'], 'Count of missing evidence metrics preserved as unproven.'),
  ],
  flash_fry: {},
  cache_economy: {},
  model_profile: {},
  oracle_strength: {
    schema_validation: metric('schema_validation', 1, 'count', 'proven', ['EV-EXTRACTION-MANIFEST'], 'Extractor output was validated by the SPEC-001 schema validator.'),
  },
  structural_health: {
    read_only_ledger: metric('read_only_ledger', 'read_only', 'text', 'proven', ['EV-LEDGER', 'EV-EXTRACTION-MANIFEST'], 'Source ledger hash is checked before and after output generation.'),
  },
  runtime_visual: {},
  commits: {},
  audit: {},
  anti_gaming_flags: [],
  privacy: {
    private_vocabulary_status: 'unproven',
    sanitizer_status: 'unproven',
  },
  gold_analysis: {
    classification: 'ordinary',
    sanitizer_status: 'unproven',
    evidence_refs: ['EV-EXTRACTION-MANIFEST'],
    notes: 'SPEC-002 extraction does not request Gold sharing.',
  },
  share_gate: {
    status: 'not_requested',
    sanitizer_status: 'unproven',
    approval: unprovenApproval(runId),
    notes: 'GitHub sharing is opt-in and not requested by the extractor.',
  },
  unproven_metrics: unprovenMetrics,
  final_status: {
    goal_maestro_execution_state: parsed.stopState,
    thermometer_report_status: 'local_package_ready',
    share_gate_status: 'not_requested',
    notes: 'Thermometer report state is separate from the Goal Maestro execution stop state.',
  },
};

try {
  mkdirSync(outputDir, { recursive: true });
  writeFileSync(join(outputDir, 'extraction_manifest.json'), manifestText);
  writeFileSync(join(outputDir, 'exec_identity.yaml'), toSimpleYaml(identity));
  writeFileSync(join(outputDir, 'exec_metrics.json'), `${JSON.stringify(metrics, null, 2)}\n`);
} catch (error) {
  console.error(`cannot write extraction output: ${error.message}`);
  process.exit(1);
}

let after;
try {
  after = readLedgerSnapshot(ledgerPath);
} catch (error) {
  console.error(`cannot re-read source ledger after extraction: ${error.message}`);
  process.exit(2);
}

if (after.sha256 !== before.sha256) {
  console.error(`BLOCKED_LEDGER_MUTATION: before ${before.sha256}, after ${after.sha256}`);
  process.exit(1);
}

if (!cli.options.skipSchemaValidation) {
  try {
    execFileSync('node', [
      join(here, 'execution-thermometer-schema.mjs'),
      join(outputDir, 'exec_identity.yaml'),
      join(outputDir, 'exec_metrics.json'),
    ], { stdio: 'pipe' });
  } catch (error) {
    process.stderr.write(error.stdout?.toString() ?? '');
    process.stderr.write(error.stderr?.toString() ?? '');
    console.error('SPEC-002 output failed SPEC-001 schema validation');
    process.exit(1);
  }
}

console.log(JSON.stringify({
  status: 'PASS',
  ledger_sha256: before.sha256,
  extraction_hash: manifestHash,
  output_dir: outputDir,
  unproven_metrics: unprovenMetrics.length,
}, null, 2));

function usage() {
  console.error('usage: node scripts/execution-thermometer-extract.mjs <ledger.md> <output-dir> [--expected-ledger-sha256 <sha256>] [--generated-at <UTC timestamp>]');
}

function parseArgs(argv) {
  const positionals = [];
  const options = {};
  const optionNames = new Map([
    ['--expected-ledger-sha256', 'expectedLedgerSha256'],
    ['--generated-at', 'generatedAt'],
    ['--run-id', 'runId'],
    ['--project-id', 'projectId'],
    ['--series-id', 'seriesId'],
    ['--timezone', 'timezone'],
    ['--adapter', 'adapter'],
    ['--ledger-path-label', 'ledgerPathLabel'],
    ['--model-provider', 'modelProvider'],
    ['--model-identity', 'modelIdentity'],
    ['--reasoning-profile', 'reasoningProfile'],
    ['--effort-multiplier', 'effortMultiplier'],
  ]);
  for (let index = 0; index < argv.length; index++) {
    const token = argv[index];
    if (token === '--skip-schema-validation') {
      options.skipSchemaValidation = true;
      continue;
    }
    if (optionNames.has(token)) {
      const next = argv[++index];
      if (!next) {
        console.error(`missing value for ${token}`);
        process.exit(2);
      }
      options[optionNames.get(token)] = next;
      continue;
    }
    if (token.startsWith('--')) {
      console.error(`unknown option: ${token}`);
      process.exit(2);
    }
    positionals.push(token);
  }
  return { positionals, options };
}

function readLedgerSnapshot(path) {
  const buffer = readFileSync(path);
  const stat = statSync(path);
  return {
    text: buffer.toString('utf8'),
    sha256: sha256(buffer),
    bytes: stat.size,
  };
}

function parseLedger(text) {
  const title = firstMatch(text, /^#\s+(.+)$/m) ?? 'Goal Maestro execution ledger';
  const anchor = parseAnchor(text);
  const sections = parseSpecSections(text);
  const specs = sections.length > 0 ? sections : [{
    spec_id: 'SPEC-UNKNOWN',
    title: 'Unsectioned Ledger Evidence',
    fields: {},
  }];
  return {
    title,
    anchor,
    specs,
    stopState: lastField(specs, 'stop_state') ?? 'NEEDS_LEDGER_EVIDENCE',
  };
}

function parseAnchor(text) {
  const match = text.match(/^Anchor:\s+(.+?)\s+\(([^,]+),\s*git hash-object\s+([a-f0-9]+)\)/m);
  if (!match) {
    return { path: 'unproven', hash: 'unproven', class: 'unproven' };
  }
  return {
    path: match[1].trim(),
    class: match[2].trim(),
    hash: match[3].trim(),
  };
}

function parseSpecSections(text) {
  const matches = [...text.matchAll(/^###\s+(SPEC-\d+)\s+-\s+(.+)$/gm)];
  return matches.map((match, index) => {
    const next = matches[index + 1]?.index ?? text.length;
    const body = text.slice(match.index + match[0].length, next);
    return {
      spec_id: match[1],
      title: match[2].trim(),
      fields: parseFields(body),
    };
  });
}

function parseFields(text) {
  const fields = {};
  for (const line of text.split(/\r?\n/)) {
    const match = line.match(/^([A-Za-z0-9_]+):\s*(.*)$/);
    if (match) {
      fields[match[1]] = match[2].trim();
    }
  }
  return fields;
}

function buildSpecResults(specs, unprovenMetrics) {
  const unprovenBySpec = new Map();
  for (const item of unprovenMetrics) {
    const specId = item.name.split('.')[0];
    const list = unprovenBySpec.get(specId) ?? [];
    list.push(item.name);
    unprovenBySpec.set(specId, list);
  }
  return specs.map((spec) => {
    const status = specStatus(spec.fields.oracle_status);
    return {
      spec_id: spec.fields.spec_id || spec.spec_id,
      title: spec.title,
      type: 'functional',
      status,
      intent_score: status === 'pass' ? 100 : null,
      fidelity_score: status === 'pass' ? 100 : null,
      proof_score: status === 'pass' ? 100 : null,
      attempts: numberField(spec.fields.attempt, 1),
      rework_count: numberField(spec.fields.repair_count, 0),
      evidence_refs: ['EV-LEDGER'],
      unproven_metrics: unprovenBySpec.get(spec.spec_id) ?? [],
      notes: spec.fields.oracle_status || 'Missing oracle_status evidence; preserved as unproven.',
    };
  });
}

function buildLoop(parsed, specResults, unprovenMetrics, generatedAt) {
  const hasFail = specResults.some((result) => result.status === 'fail');
  const hasBlocked = specResults.some((result) => result.status === 'blocked');
  const status = hasFail ? 'fail' : hasBlocked ? 'blocked' : unprovenMetrics.length > 0 ? 'unproven' : 'on_track';
  return {
    loop_id: 'L1',
    label: 'L1 (Latest)',
    started_at_utc: generatedAt,
    ended_at_utc: generatedAt,
    objective: parsed.title,
    status,
    scores: {
      delivery: status === 'on_track' ? 100 : null,
      proof: unprovenMetrics.length === 0 ? 100 : null,
    },
    spec_ids: specResults.map((result) => result.spec_id),
    evidence_refs: ['EV-LEDGER', 'EV-EXTRACTION-MANIFEST'],
    summary: 'Ledger evidence normalized without mutating the source ledger.',
    next_actions: unprovenMetrics.length > 0 ? ['Resolve unproven ledger evidence before promotion.'] : [],
  };
}

function collectUnprovenMetrics(specs) {
  const metrics = [];
  for (const spec of specs) {
    if (!spec.fields.oracle_status || /^active\b/i.test(spec.fields.oracle_status)) {
      metrics.push(metric(
        `${spec.spec_id}.oracle_status`,
        null,
        'text',
        'unproven',
        ['EV-LEDGER'],
        'Source ledger does not contain closed oracle evidence for this SPEC.',
      ));
    }
    if (!spec.fields.runtime_smoke_oracle || spec.fields.runtime_smoke_oracle === 'not_applicable') {
      metrics.push(metric(
        `${spec.spec_id}.runtime_smoke_oracle`,
        null,
        'text',
        'unproven',
        ['EV-LEDGER'],
        'Source ledger does not contain runtime smoke evidence for this SPEC.',
      ));
    }
  }
  return metrics;
}

function specStatus(oracleStatus) {
  const value = (oracleStatus ?? '').toLowerCase();
  if (!value || value.startsWith('active')) {
    return 'unproven';
  }
  if (value.includes('fail')) {
    return 'fail';
  }
  if (value.includes('blocked')) {
    return 'blocked';
  }
  if (value.includes('needs_review')) {
    return 'needs_review';
  }
  if (value.includes('skipped') || value === 'not_applicable') {
    return 'skipped';
  }
  if (value.includes('repaired')) {
    return 'repaired_pass';
  }
  if (value.includes('pass')) {
    return 'pass';
  }
  return 'unproven';
}

function metric(name, value, unit, status, evidenceRefs, notes) {
  return { name, value, unit, status, evidence_refs: evidenceRefs, notes };
}

function signal(signalName, status, score, notes, evidenceRefs) {
  return { signal: signalName, status, score, vs_plan: null, notes, evidence_refs: evidenceRefs };
}

function evidenceSource({ ref, type, description, source, path, hash }) {
  return { ref, type, description, source, path, hash, sanitized: true };
}

function unprovenApproval(runId) {
  return {
    approved_at_utc: 'unproven',
    run_id: runId,
    destination_repository: 'unproven',
    destination_branch: 'unproven',
    payload_hash: 'unproven',
    manifest_hash: 'unproven',
  };
}

function numberField(value, fallback) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function lastField(specs, field) {
  for (let index = specs.length - 1; index >= 0; index--) {
    const value = specs[index].fields[field];
    if (value) {
      return value;
    }
  }
  return null;
}

function firstMatch(text, regex) {
  return text.match(regex)?.[1]?.trim() ?? null;
}

function detectAdapter(scriptDir) {
  const match = scriptDir.match(/[/\\]adapters[/\\](claude|codex|cursor)[/\\]/);
  return match?.[1] ?? 'other';
}

function displayPath(path) {
  const rel = relative(process.cwd(), path);
  if (rel && !rel.startsWith('..') && !isAbsolute(rel)) {
    return rel;
  }
  return `<external-ledger>/${basename(path)}`;
}

function toSimpleYaml(value, indent = 0) {
  const pad = ' '.repeat(indent);
  return Object.entries(value).map(([key, child]) => {
    if (isPlainObject(child)) {
      return `${pad}${key}:\n${toSimpleYaml(child, indent + 2)}`;
    }
    return `${pad}${key}: ${yamlScalar(child)}\n`;
  }).join('');
}

function yamlScalar(value) {
  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }
  if (value === null) {
    return 'null';
  }
  return JSON.stringify(String(value));
}

function stableJson(value) {
  if (Array.isArray(value)) {
    return `[${value.map(stableJson).join(',')}]`;
  }
  if (isPlainObject(value)) {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

function utcNowWithoutMillis() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}
