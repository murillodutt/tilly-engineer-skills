// SPEC-005 Gold Analysis Gate.
// Classifies a normalized report candidate as ordinary, useful, or gold. The
// `gold` result is deliberately conservative and requires allowed reason codes,
// declared evidence refs, sanitizer pass, private-vocabulary pass, a concise
// learning summary, and a local package checksum.
//
//   node scripts/execution-thermometer-gold.mjs <candidate.json> --expect gold

import { writeFileSync } from 'node:fs';
import { readText } from './lib/harness.mjs';

const ALLOWED_REASON_CODES = new Set([
  'new_stop_state_pattern',
  'repeated_spec_repair',
  'lens_broke_decision',
  'oracle_facade_detected',
  'cache_economy_unproven',
  'visual_axis_blocked',
  'integration_oracle_missing',
  'high_rework_low_output',
  'model_reasoning_profile_outlier',
  'harness_version_regression',
  'privacy_sanitization_edge',
  'flash_fry_false_positive',
  'flash_fry_early_block_saved_cost',
  'audit_repair_found_late_defect',
  'claim_artifact_mismatch',
]);

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

const result = classify(candidate, cli.options.packageChecksum);

if (cli.options.expect && result.classification !== cli.options.expect) {
  result.errors.push(`expected ${cli.options.expect}, got ${result.classification}`);
}

if (cli.options.out) {
  writeFileSync(cli.options.out, `${JSON.stringify(result, null, 2)}\n`);
}

if (result.errors.length > 0) {
  for (const error of result.errors) {
    console.error(error);
  }
  process.exit(1);
}

console.log(JSON.stringify(result, null, 2));

function usage() {
  console.error('usage: node scripts/execution-thermometer-gold.mjs <candidate.json> [--expect ordinary|useful|gold] [--package-checksum <sha256>] [--out <gold.json>]');
}

function parseArgs(argv) {
  const positionals = [];
  const options = {};
  for (let index = 0; index < argv.length; index++) {
    const token = argv[index];
    if (token === '--expect') {
      options.expect = requiredValue(argv, ++index, token);
      continue;
    }
    if (token === '--package-checksum') {
      options.packageChecksum = requiredValue(argv, ++index, token);
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
  if (options.expect && !['ordinary', 'useful', 'gold'].includes(options.expect)) {
    console.error(`invalid --expect value: ${options.expect}`);
    process.exit(2);
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

function classify(candidate, checksumOverride) {
  const sources = Array.isArray(candidate.sources) ? candidate.sources : [];
  const declaredRefs = new Set(sources.map((source) => source?.ref).filter(Boolean));
  const privacy = candidate.privacy ?? {};
  const gold = candidate.gold_analysis ?? {};
  const reasonCodes = arrayOfStrings(gold.reason_codes);
  const evidenceRefs = arrayOfStrings(gold.evidence_refs);
  const requested = gold.classification;
  const checksum = checksumOverride ?? gold.package_checksum;
  const learningSummary = String(gold.learning_summary ?? gold.notes ?? '').trim();
  const sanitizerStatus = gold.sanitizer_status ?? privacy.sanitizer_status;
  const privateVocabularyStatus = privacy.private_vocabulary_status ?? gold.private_vocabulary_status;

  const errors = [];
  for (const code of reasonCodes) {
    if (!ALLOWED_REASON_CODES.has(code)) {
      errors.push(`unknown gold reason code: ${code}`);
    }
  }
  for (const ref of evidenceRefs) {
    if (!declaredRefs.has(ref)) {
      errors.push(`gold evidence ref is undeclared: ${ref}`);
    }
  }

  const hasImprovementSignal = reasonCodes.length > 0 || evidenceRefs.length > 0 || learningSummary.length > 0;
  let classification = requested === 'gold' ? 'gold' : requested === 'useful' ? 'useful' : hasImprovementSignal ? 'useful' : 'ordinary';

  const goldRequirements = [
    ['gold requires at least one reason code', reasonCodes.length > 0],
    ['gold requires cited evidence refs', evidenceRefs.length > 0],
    ['gold requires sanitizer pass', sanitizerStatus === 'pass'],
    ['gold requires private vocabulary pass', privateVocabularyStatus === 'pass'],
    ['gold requires concise learning summary', learningSummary.length > 0],
    ['gold requires local package checksum', isChecksum(checksum)],
  ];

  if (classification === 'gold') {
    for (const [message, pass] of goldRequirements) {
      if (!pass) {
        errors.push(message);
      }
    }
  }

  if (classification !== 'gold' && requested === 'gold') {
    errors.push('requested gold classification did not satisfy gold requirements');
  }

  if (errors.length > 0 && classification === 'gold') {
    classification = 'useful';
  }

  if (requested === 'ordinary') {
    classification = 'ordinary';
  }

  return {
    schema_version: 1,
    classification,
    reason_codes: reasonCodes,
    evidence_refs: evidenceRefs,
    sanitizer_status: sanitizerStatus ?? 'unproven',
    private_vocabulary_status: privateVocabularyStatus ?? 'unproven',
    package_checksum: checksum ?? 'unproven',
    learning_summary: learningSummary || 'unproven',
    errors,
  };
}

function arrayOfStrings(value) {
  return Array.isArray(value) ? value.filter((item) => typeof item === 'string') : [];
}

function isChecksum(value) {
  return typeof value === 'string' && /^[a-f0-9]{64}$/i.test(value);
}
