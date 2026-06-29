// Focused contract oracle for the optional Goal Maestro adversarial audit heartbeat prompt.
// It validates source surfaces and mutation fixtures without granting runtime authority.

import { existsSync, readdirSync, statSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readText } from './lib/harness.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const skillRoot = dirname(here);
const sourceRepoRoot = findSourceRepoRoot(here);
const targetRoot = sourceRepoRoot ?? findInstalledTargetRoot(skillRoot);
const displayRoot = sourceRepoRoot ?? targetRoot ?? skillRoot;
const fixtureRoot = join(here, 'fixtures/adversarial-audit-heartbeat');
const placeholders = [
  '{audit_subject}',
  '{execution_command}',
  '{active_goal}',
  '{active_spec}',
  '{available_thread_state}',
  '{state_access_boundary}',
  '{hard_preconditions}',
  '{contract_blockers}',
  '{required_ledger}',
  '{forbidden_actions}',
  '{stop_state_vocabulary}',
  '{heartbeat_report_status_vocabulary}',
  '{completion_condition}',
];
const heartbeatStatuses = [
  'HEARTBEAT_OK',
  'HEARTBEAT_RISK',
  'HEARTBEAT_BLOCKED_CONTEXT',
  'HEARTBEAT_COMPLETE',
  'HEARTBEAT_PAUSE_RECOMMENDED',
];
const exactOptIns = [
  '--audit-heartbeat-prompt',
  'audit_heartbeat=true',
  'adversarial_audit_heartbeat: requested',
];
const dynamicForbiddenTerms = [
  ['dash', 'board'].join(''),
  ['tele', 'metry'].join(''),
  ['track', 'ing'].join(''),
  ['send', 'Beacon'].join(''),
  ['XML', 'HttpRequest'].join(''),
  ['ana', 'lytics'].join(''),
  ['pub', 'lish'].join(''),
  ['rel', 'ease'].join(''),
];

const cli = parseArgs(process.argv.slice(2));

if (cli.fixture) {
  const candidate = loadCandidateFromFixture(cli.fixture);
  const result = validateCandidate(candidate);
  printCandidateResult(candidate.name, result);
  if (cli.expectFail) {
    process.exit(result.failed > 0 ? 0 : 1);
  }
  process.exit(result.failed === 0 ? 0 : 1);
}

const sourceCandidate = loadSourceCandidate();
let failures = 0;
const sourceResult = validateCandidate(sourceCandidate);
printCandidateResult(sourceCandidate.name, sourceResult);
if (sourceResult.failed > 0) {
  failures++;
}

if (!cli.skipFixtures && existsSync(fixtureRoot)) {
  const fixtureResults = runFixtureSuite(fixtureRoot);
  failures += fixtureResults.failed;
}

process.exit(failures === 0 ? 0 : 1);

function parseArgs(argv) {
  const options = { skipFixtures: false, expectFail: false };
  for (let index = 0; index < argv.length; index++) {
    const token = argv[index];
    if (token === '--fixture') {
      options.fixture = requiredValue(argv, ++index, token);
      continue;
    }
    if (token === '--expect-fail') {
      options.expectFail = true;
      continue;
    }
    if (token === '--skip-fixtures') {
      options.skipFixtures = true;
      continue;
    }
    if (token.startsWith('--')) {
      console.error(`unknown option: ${token}`);
      process.exit(2);
    }
    if (!options.fixture) {
      options.fixture = token;
      continue;
    }
    console.error(`unexpected positional argument: ${token}`);
    process.exit(2);
  }
  return options;
}

function requiredValue(argv, index, option) {
  const value = argv[index];
  if (!value) {
    console.error(`missing value for ${option}`);
    process.exit(2);
  }
  return value;
}

function findSourceRepoRoot(start) {
  let current = start;
  while (current !== dirname(current)) {
    if (existsSync(join(current, 'AGENTS.md')) && existsSync(join(current, 'src/adapters'))) {
      return current;
    }
    current = dirname(current);
  }
  return null;
}

function findInstalledTargetRoot(start) {
  let current = start;
  while (current !== dirname(current)) {
    if (
      existsSync(join(current, '.agents/skills/tes-goal-maestro')) ||
      existsSync(join(current, '.claude/skills/tes-goal-maestro')) ||
      existsSync(join(current, '.cursor/rules/tes-runtime-capabilities.mdc'))
    ) {
      return current;
    }
    current = dirname(current);
  }
  return null;
}

function loadSourceCandidate() {
  if (!sourceRepoRoot) {
    return loadInstalledCandidate();
  }
  const codexRoot = join(sourceRepoRoot, 'src/adapters/codex/skills/tes-goal-maestro');
  const claudeRoot = join(sourceRepoRoot, 'src/adapters/claude/skills/tes-goal-maestro');
  return {
    name: 'source surfaces',
    surfaces: {
      rootSkill: readText(join(skillRoot, 'SKILL.md')),
      maestralReference: readText(join(skillRoot, 'references/maestral-goal-prompt.md')),
      maestralTemplate: readText(join(skillRoot, 'templates/maestral-goal-prompt.template.md')),
      heartbeatReference: readText(join(skillRoot, 'references/adversarial-audit-heartbeat.md')),
      heartbeatTemplate: readText(join(skillRoot, 'templates/adversarial-audit-heartbeat.template.md')),
      cursorRule: readText(join(sourceRepoRoot, 'src/adapters/cursor/rules/tes-runtime-capabilities.mdc')),
      codexHeartbeatReference: readText(join(codexRoot, 'references/adversarial-audit-heartbeat.md')),
      codexHeartbeatTemplate: readText(join(codexRoot, 'templates/adversarial-audit-heartbeat.template.md')),
      claudeHeartbeatReference: readText(join(claudeRoot, 'references/adversarial-audit-heartbeat.md')),
      claudeHeartbeatTemplate: readText(join(claudeRoot, 'templates/adversarial-audit-heartbeat.template.md')),
    },
  };
}

function loadInstalledCandidate() {
  if (!targetRoot) {
    console.error('could not locate source repository or installed TES target root');
    process.exit(2);
  }
  const codexRoot = join(targetRoot, '.agents/skills/tes-goal-maestro');
  const claudeRoot = join(targetRoot, '.claude/skills/tes-goal-maestro');
  const cursorRulePath = join(targetRoot, '.cursor/rules/tes-runtime-capabilities.mdc');
  const codexReference = existsSync(codexRoot)
    ? readText(join(codexRoot, 'references/adversarial-audit-heartbeat.md'))
    : readText(join(skillRoot, 'references/adversarial-audit-heartbeat.md'));
  const codexTemplate = existsSync(codexRoot)
    ? readText(join(codexRoot, 'templates/adversarial-audit-heartbeat.template.md'))
    : readText(join(skillRoot, 'templates/adversarial-audit-heartbeat.template.md'));
  const claudeReference = existsSync(claudeRoot)
    ? readText(join(claudeRoot, 'references/adversarial-audit-heartbeat.md'))
    : readText(join(skillRoot, 'references/adversarial-audit-heartbeat.md'));
  const claudeTemplate = existsSync(claudeRoot)
    ? readText(join(claudeRoot, 'templates/adversarial-audit-heartbeat.template.md'))
    : readText(join(skillRoot, 'templates/adversarial-audit-heartbeat.template.md'));
  return {
    name: 'installed surfaces',
    surfaces: {
      rootSkill: readText(join(skillRoot, 'SKILL.md')),
      maestralReference: readText(join(skillRoot, 'references/maestral-goal-prompt.md')),
      maestralTemplate: readText(join(skillRoot, 'templates/maestral-goal-prompt.template.md')),
      heartbeatReference: readText(join(skillRoot, 'references/adversarial-audit-heartbeat.md')),
      heartbeatTemplate: readText(join(skillRoot, 'templates/adversarial-audit-heartbeat.template.md')),
      cursorRule: existsSync(cursorRulePath) ? readText(cursorRulePath) : '',
      codexHeartbeatReference: codexReference,
      codexHeartbeatTemplate: codexTemplate,
      claudeHeartbeatReference: claudeReference,
      claudeHeartbeatTemplate: claudeTemplate,
    },
  };
}

function loadCandidateFromFixture(path) {
  const fullPath = resolve(path);
  let fixture;
  try {
    fixture = JSON.parse(readText(fullPath));
  } catch (error) {
    console.error(`fixture JSON invalid: ${error.message}`);
    process.exit(2);
  }
  const candidate = loadSourceCandidate();
  candidate.name = fixture.name ?? relative(displayRoot, fullPath);
  applyFixtureMutations(candidate.surfaces, fixture);
  return candidate;
}

function applyFixtureMutations(surfaces, fixture) {
  const mutations = fixture.mutations ?? {};
  for (const [surface, text] of Object.entries(mutations.replace ?? {})) {
    requireSurface(surfaces, surface);
    surfaces[surface] = String(text);
  }
  for (const [surface, text] of Object.entries(mutations.append ?? {})) {
    requireSurface(surfaces, surface);
    surfaces[surface] += String(text);
  }
  for (const [surface, replacements] of Object.entries(mutations.replaceText ?? {})) {
    requireSurface(surfaces, surface);
    for (const replacement of replacements) {
      const from = String(replacement.from ?? '');
      const to = String(replacement.to ?? '');
      if (!from || !surfaces[surface].includes(from)) {
        console.error(`fixture replacement not found on ${surface}: ${from}`);
        process.exit(2);
      }
      surfaces[surface] = surfaces[surface].split(from).join(to);
    }
  }
  for (const [surface, removals] of Object.entries(mutations.removeText ?? {})) {
    requireSurface(surfaces, surface);
    for (const removal of removals) {
      const text = String(removal);
      if (!surfaces[surface].includes(text)) {
        console.error(`fixture removal not found on ${surface}: ${text}`);
        process.exit(2);
      }
      surfaces[surface] = surfaces[surface].split(text).join('');
    }
  }
}

function requireSurface(surfaces, surface) {
  if (!(surface in surfaces)) {
    console.error(`unknown fixture surface: ${surface}`);
    process.exit(2);
  }
}

function validateCandidate(candidate) {
  const s = candidate.surfaces;
  const checks = [];
  const promptRouteText = `${s.rootSkill}\n${s.maestralReference}\n${s.heartbeatReference}`;
  const heartbeatText = `${s.heartbeatReference}\n${s.heartbeatTemplate}`;

  for (const optIn of exactOptIns) {
    checks.push(check(`exact opt-in present: ${optIn}`, promptRouteText.includes(optIn)));
  }
  checks.push(check('direct generate/create request is the only natural-language opt-in',
    /direct request to generate or create an adversarial audit heartbeat prompt/i.test(promptRouteText)));
  checks.push(check('broad wording is explicitly rejected',
    /Do not activate from broad words/i.test(s.heartbeatReference) &&
      /heartbeat, monitor, audit/i.test(s.heartbeatReference) &&
      /translated equivalents/i.test(s.heartbeatReference)));
  checks.push(check('ordinary maestral template has no heartbeat section',
    !/Adversarial Audit Heartbeat|audit-heartbeat|HEARTBEAT_/i.test(s.maestralTemplate)));
  checks.push(check('no new command is introduced',
    !/\/tes-(audit|heartbeat)|\/tes:(audit|heartbeat)/i.test(promptRouteText)));

  checks.push(check('heartbeat reference routes to the standalone template',
    s.heartbeatReference.includes('templates/adversarial-audit-heartbeat.template.md')));
  for (const placeholder of placeholders) {
    checks.push(check(`placeholder preserved: ${placeholder}`, s.heartbeatTemplate.includes(placeholder)));
  }
  for (const status of heartbeatStatuses) {
    checks.push(check(`status vocabulary preserved: ${status}`,
      s.heartbeatReference.includes(status) && s.heartbeatTemplate.includes(status)));
  }

  checks.push(check('latest available state review is required',
    /Read available latest execution or thread state before commenting\./.test(s.heartbeatTemplate) &&
      /inspect available latest execution or thread state before commenting/.test(s.heartbeatReference)));
  checks.push(check('host-state boundary is honest',
    /host makes visible/i.test(s.heartbeatTemplate) &&
      /HEARTBEAT_BLOCKED_CONTEXT/.test(s.heartbeatTemplate) &&
      /smallest missing visible state/i.test(s.heartbeatTemplate) &&
      /must not infer unavailable state/i.test(s.heartbeatReference)));
  checks.push(check('no-runtime-before-hardening check remains configurable',
    /configured no-runtime-before-hardening/i.test(s.heartbeatReference) &&
      /configured no-runtime-before-hardening rule/i.test(s.heartbeatTemplate)));
  checks.push(check('green response has five-line ceiling',
    /at most five non-empty lines/i.test(s.heartbeatTemplate) &&
      /at most five non-empty lines/i.test(s.heartbeatReference)));
  checks.push(check('risk response names risk, contract, correction, and stop state',
    /If risky, cite the risk, violated contract, minimum corrective action, and\s+most specific recommended Goal Maestro stop state\./i.test(s.heartbeatTemplate)));
  checks.push(check('completion response recommends external heartbeat pause or deletion',
    /recommend\s+pausing or deleting the external heartbeat/i.test(s.heartbeatTemplate) &&
      /summarize residual risk/i.test(s.heartbeatTemplate)));

  checks.push(check('auditor/executor separation is explicit',
    /not the executor/i.test(s.heartbeatTemplate) &&
      /never owns the loop/i.test(s.heartbeatReference) &&
      /not a scheduler, executor/i.test(s.heartbeatReference)));
  checks.push(check('read-only denial set is complete', requiredReadOnlyLines(s.heartbeatTemplate).length === 0,
    requiredReadOnlyLines(s.heartbeatTemplate).join('; ')));
  const authorityLeaks = unauthorizedAuthorityLines(heartbeatText);
  checks.push(check('no mutation or remote authority is granted', authorityLeaks.length === 0, authorityLeaks.join(' | ')));

  const productDrift = heartbeatText.match(/Thermometer|Gold Sharing|Execution Thermometer|PASS_CEILING/g) ?? [];
  checks.push(check('no product-specific heartbeat drift', productDrift.length === 0, productDrift.join(', ')));
  const forbiddenBehavior = dynamicForbiddenTerms.filter((term) => new RegExp(escapeRegExp(term), 'i').test(heartbeatText));
  checks.push(check('no hidden network, reporting, visual-control, or external-publication terms',
    forbiddenBehavior.length === 0, forbiddenBehavior.join(', ')));

  checks.push(check('Goal Maestro stop states remain authoritative',
    /Goal Maestro stop states remain authoritative/i.test(s.heartbeatReference) &&
      /Do not claim or replace the authoritative Goal Maestro stop state\./.test(s.heartbeatTemplate)));
  checks.push(check('heartbeat statuses stay separate from Goal Maestro stop states',
    /separate from Goal Maestro stop states/i.test(s.heartbeatReference) &&
      /Keep heartbeat report statuses separate from Goal Maestro stop states\./.test(s.heartbeatTemplate)));

  checks.push(check('Cursor lazy rule names capability without fake skill parity',
    s.cursorRule.includes('Adversarial Audit Heartbeat Prompt') &&
      s.cursorRule.includes('Cursor lazy capability detail') &&
      s.cursorRule.includes('not a Cursor skill package') &&
      s.cursorRule.includes('structural and materialization coverage') &&
      s.cursorRule.includes('HEARTBEAT_BLOCKED_CONTEXT') &&
      !/Cursor skill parity/i.test(s.cursorRule)));
  checks.push(check('Codex and Claude heartbeat references match',
    s.codexHeartbeatReference === s.claudeHeartbeatReference));
  checks.push(check('Codex and Claude heartbeat templates match',
    s.codexHeartbeatTemplate === s.claudeHeartbeatTemplate));

  return summarizeChecks(checks);
}

function requiredReadOnlyLines(template) {
  const required = [
    'Do not edit files.',
    'Do not stage or commit repository changes.',
    'Do not create branches or tags.',
    'Do not perform Git remote writes.',
    'Do not call remotes or external services.',
    'Do not create, update, or remove host jobs.',
    'Do not share artifacts externally.',
    'Do not redirect execution or open another Goal Maestro loop.',
    'Do not claim or replace the authoritative Goal Maestro stop state.',
  ];
  return required.filter((line) => !template.includes(line));
}

function unauthorizedAuthorityLines(text) {
  const action = /(edit files|stage|commit|create branches|create tags|push|remote writes|call remotes|external services|create host jobs|update host jobs|remove host jobs|share artifacts|redirect execution|open another Goal Maestro loop|claim .*stop state|replace .*stop state)/i;
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .filter((line) => !/^(?:-|[0-9]+\.)?\s*(?:Do not|Never|avoid|must not|does not|is not|not a)\b/i.test(line))
    .filter((line) => /\b(?:may|can|should|must|will|allow|allows|allowed|authorize|authorized|claim|replace)\b/i.test(line) && action.test(line));
}

function check(name, pass, detail = '') {
  return { name, pass, detail };
}

function summarizeChecks(checks) {
  const failedChecks = checks.filter((item) => !item.pass);
  return {
    checks,
    failed: failedChecks.length,
    passed: checks.length - failedChecks.length,
  };
}

function printCandidateResult(name, result) {
  console.log(`# adversarial-audit-heartbeat-contract — ${name}`);
  for (const c of result.checks) {
    console.log(`  [${c.pass ? 'PASS' : 'FAIL'}] ${c.name}${c.detail ? ` — ${c.detail}` : ''}`);
  }
  console.log(`# ${result.passed} pass, ${result.failed} fail`);
}

function runFixtureSuite(root) {
  const files = listJsonFiles(root);
  let failed = 0;
  console.log(`# adversarial-audit-heartbeat-contract fixtures — ${relative(displayRoot, root)}`);
  for (const file of files) {
    const rel = relative(root, file);
    const expectInvalid = rel.split('/').some((part) => part.startsWith('invalid-'));
    const candidate = loadCandidateFromFixture(file);
    const result = validateCandidate(candidate);
    const accepted = result.failed === 0;
    const ok = expectInvalid ? !accepted : accepted;
    if (!ok) {
      failed++;
    }
    console.log(`  [${ok ? 'PASS' : 'FAIL'}] ${rel} — ${expectInvalid ? 'invalid rejected' : 'valid accepted'} (${result.failed} failures)`);
  }
  console.log(`# ${files.length - failed}/${files.length} fixtures prove the contract`);
  return { failed };
}

function listJsonFiles(root) {
  const results = [];
  for (const entry of readdirSync(root)) {
    const full = join(root, entry);
    const stat = statSync(full);
    if (stat.isDirectory()) {
      results.push(...listJsonFiles(full));
    } else if (entry.endsWith('.json')) {
      results.push(full);
    }
  }
  return results.sort();
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
