// SPEC-008 GitHub draft PR export dry-run planner.
// Builds an exact local plan for a private draft PR lane without performing any
// remote operation. Execute mode is deliberately gated by tuple-bound approval
// and still blocks before network/auth work in this local-first implementation.
//
//   node scripts/execution-thermometer-github-export.mjs <share-decision.json> <package-dir> --destination-config github-destination.json

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { join, posix, relative, sep } from 'node:path';
import { readText } from './lib/harness.mjs';

const STATUSES = new Set([
  'dry_run_ready',
  'draft_pr_opened',
  'blocked_by_owner_decision',
  'blocked_by_public_destination',
  'blocked_by_github_auth',
  'needs_github_destination',
  'blocked_by_payload_mismatch',
  'blocked_by_missing_package',
]);

const DEFAULT_ALLOWED_FILES = new Set(['exec_identity.yaml', 'exec_metrics.json', 'checksums.sha256']);
const DEFAULT_EXCLUDED_FILES = new Set(['context-receipt.md', 'execution-thermometer.html']);
const cli = parseArgs(process.argv.slice(2));

if (cli.positionals.length !== 2) {
  usage();
  process.exit(2);
}

let shareDecision;
let destinationConfig = null;
let approvalRecord = null;

try {
  shareDecision = JSON.parse(readText(cli.positionals[0]));
} catch (error) {
  console.error(`share decision JSON invalid: ${error.message}`);
  process.exit(2);
}

if (cli.options.destinationConfig) {
  try {
    destinationConfig = JSON.parse(readText(cli.options.destinationConfig));
  } catch (error) {
    console.error(`destination config JSON invalid: ${error.message}`);
    process.exit(2);
  }
}

if (cli.options.approvalRecord) {
  try {
    approvalRecord = JSON.parse(readText(cli.options.approvalRecord));
  } catch (error) {
    console.error(`approval record JSON invalid: ${error.message}`);
    process.exit(2);
  }
}

const result = planExport(shareDecision, cli.positionals[1], {
  destinationConfig,
  approvalRecord,
  mode: cli.options.mode,
});

const expectationErrors = [];
if (cli.options.expectStatus && result.status !== cli.options.expectStatus) {
  expectationErrors.push(`expected status ${cli.options.expectStatus}, got ${result.status}`);
}
if (typeof cli.options.expectRemoteAction === 'boolean' && result.remote_action_performed !== cli.options.expectRemoteAction) {
  expectationErrors.push(`expected remote_action_performed ${cli.options.expectRemoteAction}, got ${result.remote_action_performed}`);
}

if (cli.options.out) {
  writeFileSync(cli.options.out, `${JSON.stringify(result, null, 2)}\n`);
}

console.log(JSON.stringify(result, null, 2));

if (expectationErrors.length > 0) {
  for (const error of expectationErrors) {
    console.error(error);
  }
  process.exit(1);
}

function usage() {
  console.error('usage: node scripts/execution-thermometer-github-export.mjs <share-decision.json> <package-dir> [--destination-config <config.json>] [--approval-record <approval.json>] [--mode dry-run|execute] [--expect-status <status>] [--expect-remote-action true|false] [--out <plan.json>]');
}

function parseArgs(argv) {
  const positionals = [];
  const options = { mode: 'dry-run' };
  for (let index = 0; index < argv.length; index++) {
    const token = argv[index];
    if (token === '--destination-config') {
      options.destinationConfig = requiredValue(argv, ++index, token);
      continue;
    }
    if (token === '--approval-record') {
      options.approvalRecord = requiredValue(argv, ++index, token);
      continue;
    }
    if (token === '--mode') {
      options.mode = requiredValue(argv, ++index, token);
      if (!['dry-run', 'execute'].includes(options.mode)) {
        console.error(`invalid --mode value: ${options.mode}`);
        process.exit(2);
      }
      continue;
    }
    if (token === '--expect-status') {
      options.expectStatus = requiredValue(argv, ++index, token);
      if (!STATUSES.has(options.expectStatus)) {
        console.error(`invalid --expect-status value: ${options.expectStatus}`);
        process.exit(2);
      }
      continue;
    }
    if (token === '--expect-remote-action') {
      options.expectRemoteAction = parseBoolean(requiredValue(argv, ++index, token), token);
      continue;
    }
    if (token === '--out') {
      options.out = requiredValue(argv, ++index, token);
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

function requiredValue(argv, index, option) {
  const value = argv[index];
  if (!value) {
    console.error(`missing value for ${option}`);
    process.exit(2);
  }
  return value;
}

function parseBoolean(value, option) {
  if (value === 'true') {
    return true;
  }
  if (value === 'false') {
    return false;
  }
  console.error(`invalid ${option} value: ${value}`);
  process.exit(2);
}

function planExport(decision, packageDir, options) {
  const destination = lookupDestination(decision, options.destinationConfig);
  const issues = [];
  const unloadedPackageState = unloadedPackage(packageDir);

  if (!destination.repository || !destination.branch) {
    return blocked('needs_github_destination', 'NEEDS_GITHUB_DESTINATION', decision, destination, unloadedPackageState, [
      'destination repository and branch are required',
    ]);
  }
  if (destination.visibility !== 'private') {
    return blocked('blocked_by_public_destination', 'BLOCKED_BY_PUBLIC_DESTINATION', decision, destination, unloadedPackageState, [
      `destination visibility must be private, got ${destination.visibility || 'unproven'}`,
    ]);
  }

  const packageState = loadPackage(packageDir);
  if (!packageState.exists || packageState.files.length === 0) {
    return blocked('blocked_by_missing_package', 'BLOCKED_BY_MISSING_PACKAGE', decision, destination, packageState, [
      'local package directory is missing or empty',
    ]);
  }

  const selected = selectPayloadFiles(packageState.files, options.destinationConfig);
  const layout = selected.included.map((file) => ({
    source: file.name,
    destination: posix.join(destination.path_prefix, file.name),
    sha256: file.sha256,
    bytes: file.bytes,
  }));
  const payloadHash = hashPayload(layout);
  const manifestHash = packageState.manifest_hash;
  const tuple = {
    run_id: stringValue(decision.run_id),
    destination_repository: destination.repository,
    destination_branch: destination.branch,
    payload_hash: payloadHash,
    manifest_hash: manifestHash,
  };
  const declaredTuple = {
    run_id: stringValue(decision.run_id),
    destination_repository: stringValue(decision.destination_repository),
    destination_branch: stringValue(decision.destination_branch),
    payload_hash: stringValue(decision.payload_hash),
    manifest_hash: stringValue(decision.manifest_hash),
  };
  const declaredTupleIssues = compareTuple(declaredTuple, tuple, 'share decision tuple');
  const approvalIssues = options.approvalRecord ? compareTuple(approvalTuple(options.approvalRecord), tuple, 'approval tuple') : ['tuple-bound approval record is required for remote execution'];
  const approvalValid = approvalIssues.length === 0 && isTimestamp(options.approvalRecord?.approved_at_utc);

  if (declaredTupleIssues.length > 0) {
    issues.push(...declaredTupleIssues);
  }

  let status = 'dry_run_ready';
  let stopState = 'not_applicable';
  if (declaredTupleIssues.length > 0) {
    status = 'blocked_by_payload_mismatch';
    stopState = 'NEEDS_OWNER_SHARE_DECISION';
  } else if (options.mode === 'execute' && !approvalValid) {
    status = 'blocked_by_owner_decision';
    stopState = 'NEEDS_OWNER_SHARE_DECISION';
    issues.push(...approvalIssues);
  } else if (options.mode === 'execute') {
    status = 'blocked_by_github_auth';
    stopState = 'BLOCKED_BY_GITHUB_AUTH';
    issues.push('remote execution is not available without an explicit authenticated GitHub lane');
  }

  return {
    schema_version: 1,
    status,
    stop_state: stopState,
    remote_action_performed: false,
    destination,
    run_id: tuple.run_id || 'unproven',
    approval_tuple: tuple,
    approval_valid: approvalValid,
    payload_hash: payloadHash,
    manifest_hash: manifestHash,
    branch_layout: layout,
    included_files: layout.map((file) => file.source),
    excluded_files: selected.excluded,
    dry_run_evidence: {
      mode: options.mode,
      exact_file_count: layout.length,
      exact_destination_count: layout.length,
      remote_write: 'not_performed',
    },
    pr_body_summary: renderPrBodySummary(decision, destination, layout),
    full_payload_embedded_in_pr_body: false,
    issues,
  };
}

function lookupDestination(decision, config) {
  const repository = knownString(config?.repository ?? config?.destination_repository ?? decision.destination_repository);
  const branch = knownString(config?.branch ?? config?.destination_branch ?? decision.destination_branch);
  const baseBranch = stringValue(config?.base_branch ?? 'main') || 'main';
  const prefix = stringValue(config?.path_prefix ?? `reports/${safeSegment(decision.run_id)}`) || `reports/${safeSegment(decision.run_id)}`;
  return {
    repository,
    branch,
    base_branch: baseBranch,
    path_prefix: normalizePosixPath(prefix),
    visibility: stringValue(config?.visibility ?? 'private').toLowerCase() || 'unproven',
  };
}

function unloadedPackage(packageDir) {
  return { exists: false, files: [], manifest_hash: 'unproven', package_dir: safePackageLabel(packageDir) };
}

function loadPackage(packageDir) {
  if (!existsSync(packageDir) || !statSync(packageDir).isDirectory()) {
    return { exists: false, files: [], manifest_hash: 'unproven', package_dir: safePackageLabel(packageDir) };
  }
  const files = readdirSync(packageDir)
    .filter((name) => statSync(join(packageDir, name)).isFile())
    .sort()
    .map((name) => {
      const bytes = readFileSync(join(packageDir, name));
      return {
        name,
        sha256: sha256(bytes),
        bytes: bytes.length,
      };
    });
  const manifest = files.find((file) => file.name === 'checksums.sha256');
  return {
    exists: true,
    files,
    manifest_hash: manifest?.sha256 ?? 'unproven',
    package_dir: safePackageLabel(packageDir),
  };
}

function selectPayloadFiles(files, config) {
  const includeReadme = Boolean(config?.include_readme);
  const includeMarkdown = Boolean(config?.include_markdown);
  const includeHtml = Boolean(config?.include_html);
  const included = [];
  const excluded = [];

  for (const file of files) {
    let allowed = DEFAULT_ALLOWED_FILES.has(file.name);
    if (file.name === 'README.md' && includeReadme) {
      allowed = true;
    }
    if (file.name === 'context-receipt.md' && includeMarkdown) {
      allowed = true;
    }
    if (file.name === 'execution-thermometer.html' && includeHtml) {
      allowed = true;
    }
    if (allowed) {
      included.push(file);
    } else if (DEFAULT_EXCLUDED_FILES.has(file.name) || file.name === 'README.md') {
      excluded.push(file.name);
    } else {
      excluded.push(file.name);
    }
  }

  return { included, excluded };
}

function renderPrBodySummary(decision, destination, layout) {
  return {
    title: `Execution Thermometer ${stringValue(decision.run_id) || 'unproven'}`,
    body_lines: [
      `Run: ${stringValue(decision.run_id) || 'unproven'}`,
      `Destination: ${destination.repository}:${destination.branch}`,
      `Files: ${layout.map((file) => file.destination).join(', ')}`,
      'Payload: sanitized evidence files only; full JSON is attached as a file, not pasted into the PR body.',
      'Remote write: not performed by dry-run.',
    ],
  };
}

function blocked(status, stopState, decision, destination, packageState, issues) {
  return {
    schema_version: 1,
    status,
    stop_state: stopState,
    remote_action_performed: false,
    destination,
    run_id: stringValue(decision.run_id) || 'unproven',
    approval_tuple: {
      run_id: stringValue(decision.run_id) || 'unproven',
      destination_repository: destination.repository || 'unproven',
      destination_branch: destination.branch || 'unproven',
      payload_hash: 'unproven',
      manifest_hash: packageState.manifest_hash || 'unproven',
    },
    approval_valid: false,
    payload_hash: 'unproven',
    manifest_hash: packageState.manifest_hash || 'unproven',
    branch_layout: [],
    included_files: [],
    excluded_files: [],
    dry_run_evidence: {
      mode: 'blocked',
      exact_file_count: 0,
      exact_destination_count: 0,
      remote_write: 'not_performed',
    },
    pr_body_summary: {
      title: 'Execution Thermometer export blocked',
      body_lines: [],
    },
    full_payload_embedded_in_pr_body: false,
    issues,
  };
}

function compareTuple(left, right, label) {
  const issues = [];
  for (const key of ['run_id', 'destination_repository', 'destination_branch', 'payload_hash', 'manifest_hash']) {
    if (left[key] !== right[key]) {
      issues.push(`${label} mismatch: ${key}`);
    }
  }
  return issues;
}

function approvalTuple(record) {
  return {
    run_id: stringValue(record?.run_id),
    destination_repository: stringValue(record?.destination_repository),
    destination_branch: stringValue(record?.destination_branch),
    payload_hash: stringValue(record?.payload_hash),
    manifest_hash: stringValue(record?.manifest_hash),
  };
}

function hashPayload(layout) {
  const text = layout.map((file) => `${file.destination}\0${file.sha256}\0${file.bytes}`).join('\n');
  return sha256(text);
}

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

function stringValue(value) {
  return typeof value === 'string' ? value.trim() : '';
}

function knownString(value) {
  const text = stringValue(value);
  return text === 'unproven' ? '' : text;
}

function isTimestamp(value) {
  return typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(value);
}

function safeSegment(value) {
  return String(value ?? 'unproven').replace(/[^A-Za-z0-9._-]/g, '-') || 'unproven';
}

function normalizePosixPath(value) {
  return String(value).split(sep).join('/').replace(/^\/+/, '').replace(/\/+$/, '');
}

function safePackageLabel(packageDir) {
  return relative(process.cwd(), packageDir).split(sep).join('/') || '.';
}
