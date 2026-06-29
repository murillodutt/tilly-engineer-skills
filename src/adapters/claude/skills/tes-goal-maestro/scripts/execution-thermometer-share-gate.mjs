// SPEC-007 Share Gate prompt and owner consent.
// Produces a local-only consent decision after the Gold and Sanitizer gates.
// It never performs GitHub or network work; remote export remains a later gate
// and requires tuple-bound approval plus dry-run evidence.
//
//   node scripts/execution-thermometer-share-gate.mjs <candidate.json> --expect-status proposed_gold

import { writeFileSync } from 'node:fs';
import { readText } from './lib/harness.mjs';

const SHARE_STATUSES = new Set([
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

const OWNER_DECISIONS = new Set(['decline', 'approve_local', 'approve_remote']);

const cli = parseArgs(process.argv.slice(2));

if (cli.positionals.length !== 1) {
  usage();
  process.exit(2);
}

let candidate;
try {
  candidate = JSON.parse(readText(cli.positionals[0]));
} catch (error) {
  console.error(`candidate JSON invalid: ${error.message}`);
  process.exit(2);
}

let approvalOverride;
if (cli.options.approvalRecord) {
  try {
    approvalOverride = JSON.parse(readText(cli.options.approvalRecord));
  } catch (error) {
    console.error(`approval record JSON invalid: ${error.message}`);
    process.exit(2);
  }
}

const result = decideShareGate(candidate, {
  ownerDecision: cli.options.decision,
  approval: approvalOverride,
  destinationRepository: cli.options.destinationRepository,
  destinationBranch: cli.options.destinationBranch,
});

const expectationErrors = [];
if (cli.options.expectStatus && result.status !== cli.options.expectStatus) {
  expectationErrors.push(`expected status ${cli.options.expectStatus}, got ${result.status}`);
}
if (typeof cli.options.expectPrompt === 'boolean' && result.prompt_required !== cli.options.expectPrompt) {
  expectationErrors.push(`expected prompt_required ${cli.options.expectPrompt}, got ${result.prompt_required}`);
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
  console.error('usage: node scripts/execution-thermometer-share-gate.mjs <candidate.json> [--decision decline|approve_local|approve_remote] [--approval-record <approval.json>] [--destination-repository <repo>] [--destination-branch <branch>] [--expect-status <status>] [--expect-prompt true|false] [--expect-remote-action true|false] [--out <decision.json>]');
}

function parseArgs(argv) {
  const positionals = [];
  const options = {};
  for (let index = 0; index < argv.length; index++) {
    const token = argv[index];
    if (token === '--decision') {
      options.decision = normalizeDecision(requiredValue(argv, ++index, token));
      continue;
    }
    if (token === '--approval-record') {
      options.approvalRecord = requiredValue(argv, ++index, token);
      continue;
    }
    if (token === '--destination-repository') {
      options.destinationRepository = requiredValue(argv, ++index, token);
      continue;
    }
    if (token === '--destination-branch') {
      options.destinationBranch = requiredValue(argv, ++index, token);
      continue;
    }
    if (token === '--expect-status') {
      options.expectStatus = requiredValue(argv, ++index, token);
      if (!SHARE_STATUSES.has(options.expectStatus)) {
        console.error(`invalid --expect-status value: ${options.expectStatus}`);
        process.exit(2);
      }
      continue;
    }
    if (token === '--expect-prompt') {
      options.expectPrompt = parseBoolean(requiredValue(argv, ++index, token), token);
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

function normalizeDecision(value) {
  const normalized = String(value ?? '').replace(/-/g, '_');
  if (!OWNER_DECISIONS.has(normalized)) {
    console.error(`invalid owner decision: ${value}`);
    process.exit(2);
  }
  return normalized;
}

function decideShareGate(candidate, overrides = {}) {
  const gold = candidate.gold_result ?? candidate.gold_analysis ?? {};
  const privacy = candidate.privacy ?? {};
  const packageManifest = candidate.package_manifest ?? {};
  const destination = candidate.destination ?? {};
  const tuple = {
    run_id: stringValue(candidate.run_id ?? gold.run_id),
    destination_repository: stringValue(overrides.destinationRepository ?? destination.repository ?? destination.destination_repository),
    destination_branch: stringValue(overrides.destinationBranch ?? destination.branch ?? destination.destination_branch),
    payload_hash: stringValue(packageManifest.payload_hash ?? candidate.payload_hash),
    manifest_hash: stringValue(packageManifest.manifest_hash ?? candidate.manifest_hash),
  };
  const ownerDecision = overrides.ownerDecision ?? normalizeOptionalDecision(candidate.owner_decision);
  const approval = overrides.approval ?? candidate.approval ?? candidate.owner_approval;
  const sanitizerStatus = packageManifest.sanitizer_status ?? gold.sanitizer_status ?? privacy.sanitizer_status ?? 'unproven';
  const privateVocabularyStatus = packageManifest.private_vocabulary_status ?? gold.private_vocabulary_status ?? privacy.private_vocabulary_status ?? 'unproven';
  const classification = gold.classification ?? 'ordinary';
  const includedFiles = arrayOfStrings(packageManifest.included_files ?? packageManifest.files);
  const excludedFiles = arrayOfStrings(packageManifest.excluded_files);
  const issues = [];
  let status = 'not_requested';
  let promptRequired = false;
  let approvalValid = false;
  let thermometerStopState = 'not_applicable';
  let nextRequiredGate = 'none';

  if (classification !== 'gold') {
    status = 'not_gold';
  } else if (sanitizerStatus !== 'pass' || privateVocabularyStatus !== 'pass') {
    status = 'blocked_by_sanitization';
    issues.push('gold report cannot be shared until sanitizer and private vocabulary checks pass');
  } else if (!tuple.destination_repository || !tuple.destination_branch) {
    status = 'blocked_by_missing_destination';
    issues.push('destination repository and branch are required before owner prompt');
  } else if (!isSha256(tuple.payload_hash) || !isSha256(tuple.manifest_hash)) {
    status = 'blocked_by_owner_decision';
    issues.push('payload hash and manifest hash are required before owner approval');
  } else if (!ownerDecision) {
    status = 'proposed_gold';
    promptRequired = true;
    thermometerStopState = 'NEEDS_OWNER_SHARE_DECISION';
  } else if (ownerDecision === 'decline') {
    status = 'declined';
  } else {
    const approvalIssues = approvalMatchesTuple(approval, tuple);
    approvalValid = approvalIssues.length === 0;
    if (!approvalValid) {
      status = 'blocked_by_owner_decision';
      issues.push(...approvalIssues);
    } else if (ownerDecision === 'approve_local') {
      status = 'approved_local_export';
    } else {
      status = 'proposed_gold';
      nextRequiredGate = 'github_dry_run';
    }
  }

  return {
    schema_version: 1,
    status,
    prompt_required: promptRequired,
    approval_valid: approvalValid,
    remote_action_performed: false,
    local_package_intact: true,
    thermometer_stop_state: thermometerStopState,
    goal_maestro_execution_state: stringValue(candidate.goal_maestro_execution_state ?? candidate.final_status?.goal_maestro_execution_state ?? 'unchanged'),
    goal_maestro_execution_state_changed: false,
    run_id: tuple.run_id || 'unproven',
    destination_repository: tuple.destination_repository || 'unproven',
    destination_branch: tuple.destination_branch || 'unproven',
    payload_hash: tuple.payload_hash || 'unproven',
    manifest_hash: tuple.manifest_hash || 'unproven',
    owner_decision: ownerDecision ?? 'pending',
    next_required_gate: nextRequiredGate,
    consent_summary: consentSummary(candidate, gold, packageManifest, tuple),
    dry_run: {
      mode: 'local_share_gate_only',
      remote_action: 'not_performed',
      included_files: includedFiles,
      excluded_files: excludedFiles,
      draft_pr_statement: 'Approved remote sharing opens a draft PR only after tuple-bound approval and later dry-run evidence.',
    },
    issues,
  };
}

function normalizeOptionalDecision(value) {
  if (value === undefined || value === null || value === '') {
    return null;
  }
  const normalized = String(value).replace(/-/g, '_');
  return OWNER_DECISIONS.has(normalized) ? normalized : null;
}

function approvalMatchesTuple(approval, tuple) {
  const issues = [];
  if (!isPlainObject(approval)) {
    return ['owner approval record is required'];
  }
  if (!isTimestamp(approval.approved_at_utc)) {
    issues.push('owner approval approved_at_utc must be an UTC timestamp');
  }
  for (const key of ['run_id', 'destination_repository', 'destination_branch', 'payload_hash', 'manifest_hash']) {
    if (approval[key] !== tuple[key]) {
      issues.push(`owner approval tuple mismatch: ${key}`);
    }
  }
  return issues;
}

function consentSummary(candidate, gold, packageManifest, tuple) {
  return {
    run_id: tuple.run_id || 'unproven',
    harness_version: stringValue(candidate.harness?.version ?? 'unproven'),
    model_identity: stringValue(candidate.model?.identity ?? candidate.model?.name ?? 'unproven'),
    reasoning_profile: stringValue(candidate.model?.reasoning_profile ?? 'unproven'),
    gold_reason_codes: arrayOfStrings(gold.reason_codes),
    included_files: arrayOfStrings(packageManifest.included_files ?? packageManifest.files),
    excluded_files: arrayOfStrings(packageManifest.excluded_files),
    sanitizer_result: stringValue(packageManifest.sanitizer_status ?? gold.sanitizer_status ?? candidate.privacy?.sanitizer_status ?? 'unproven'),
    destination_repository: tuple.destination_repository || 'unproven',
    destination_branch: tuple.destination_branch || 'unproven',
    payload_hash: tuple.payload_hash || 'unproven',
    manifest_hash: tuple.manifest_hash || 'unproven',
    draft_pr_statement: 'Remote approval means a draft PR will be opened by a later GitHub gate; this gate performs no remote action.',
  };
}

function stringValue(value) {
  return typeof value === 'string' ? value.trim() : '';
}

function arrayOfStrings(value) {
  return Array.isArray(value) ? value.filter((item) => typeof item === 'string') : [];
}

function isSha256(value) {
  return typeof value === 'string' && /^[a-f0-9]{64}$/i.test(value);
}

function isTimestamp(value) {
  return typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(value);
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}
