// Meta-certification for the tes-goal-maestro executable harness.
// This oracle checks that declared harness contracts, mutation walls, routed
// skill surfaces, adapter parity, and persistent gate wiring still agree.

import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { runChecks } from './lib/harness.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const skillRoot = dirname(here);
const repoRoot = findRepoRoot(here);
const args = new Set(process.argv.slice(2));

const supportScripts = new Set([
  'anchor-rehash-staged.mjs',
  'goal-maestro-harness-certification.mjs',
  'synth-selftest.mjs',
  'validate-walls.mjs',
]);

const requiredSkillFiles = [
  'SKILL.md',
  'agents/openai.yaml',
  'docs/CONTRACT-HISTORY.md',
  'references/adversarial-audit-heartbeat.md',
  'references/ambition-and-anchor.md',
  'references/execution-context-handoff.md',
  'references/execution-loop-runner.md',
  'references/maestral-goal-prompt.md',
  'references/materialization-tree.md',
  'references/quality-gates.md',
  'references/runtime-certification.md',
  'references/structural-method.md',
  'references/subagents-and-oracles.md',
  'references/tree-adversary.md',
  'templates/adversarial-audit-heartbeat.template.md',
  'templates/maestral-goal-prompt.template.md',
  'scripts/goal-maestro-p0-harness.mjs',
  'scripts/goal-maestro-harness-certification.mjs',
  'scripts/validate-walls.mjs',
];

const sourceClaudeRoot = join(repoRoot, 'src/adapters/claude/skills/tes-goal-maestro');
const sourceCodexRoot = join(repoRoot, 'src/adapters/codex/skills/tes-goal-maestro');
const localClaudeRoot = join(repoRoot, '.claude/skills/tes-goal-maestro');
const localCodexRoot = join(repoRoot, '.agents/skills/tes-goal-maestro');

const skillText = readText(join(skillRoot, 'SKILL.md'));
const p0HarnessText = readText(join(skillRoot, 'scripts/goal-maestro-p0-harness.mjs'));
let validateWallsText = readText(join(skillRoot, 'scripts/validate-walls.mjs'));
let stagedGateText = readText(join(repoRoot, 'scripts/staged_commit_gate.py'));
let packageText = readText(join(repoRoot, 'package.json'));

if (args.has('--simulate-missing-routed-file')) {
  requiredSkillFiles.push('references/missing-meta-route.md');
}
if (args.has('--simulate-missing-wall')) {
  validateWallsText = validateWallsText.replaceAll('goal-maestro-p0-no-automation-boundary', 'goal-maestro-p0-wall-removed');
}
if (args.has('--simulate-missing-meta-route')) {
  validateWallsText = validateWallsText.replaceAll('goal-maestro-harness-certification.mjs', 'goal-maestro-harness-certification.missing.mjs');
}
if (args.has('--simulate-unresolved-wall-harness')) {
  validateWallsText += "\nconst SIMULATED_UNRESOLVED_WALL = { harness: 'missing-meta-wall.mjs' };\n";
}
if (args.has('--simulate-narrow-staged-gate')) {
  stagedGateText = stagedGateText.replaceAll('*/skills/tes-goal-maestro/**', '*/skills/tes-goal-maestro/scripts/*.mjs');
}
if (args.has('--simulate-missing-closure-gate')) {
  packageText = packageText.replaceAll(' && node src/adapters/claude/skills/tes-goal-maestro/scripts/validate-walls.mjs', '');
}

const harnessContracts = extractConstStrings(p0HarnessText, /const\s+([A-Z0-9_]+_CONTRACT)\s*=\s*'([^']+)'/g);
const simulatedMissingTriggerKey = harnessContracts.length > 0
  ? harnessContracts[harnessContracts.length - 1].key
  : 'NO_AUTOMATION_CONTRACT';
const triggerText = args.has('--simulate-missing-contract-trigger')
  ? p0HarnessText.replaceAll(simulatedMissingTriggerKey, 'REMOVED_META_TRIGGER_TOKEN')
  : p0HarnessText;
const wallHarnesses = uniqueStrings([...validateWallsText.matchAll(/harness:\s*'([^']+\.mjs)'/g)].map((match) => match[1]));
const scriptFiles = executableScriptFiles(join(skillRoot, 'scripts'));
if (args.has('--simulate-unclassified-script')) {
  scriptFiles.push('unclassified-meta-probe.mjs');
}
const unclassifiedScripts = scriptFiles.filter((name) => !wallHarnesses.includes(name) && !supportScripts.has(name));
const simulatedParityDriftLabel = args.has('--simulate-tree-parity-drift') ? 'source Claude/Codex' : null;

const checks = [
  ...requiredSkillFiles.map((path) => check(
    `required routed file exists: ${path}`,
    existsSync(join(skillRoot, path)),
    `missing routed file ${path}`,
  )),
  check(
    'SKILL routes executable wall harnesses through validate-walls',
    skillText.includes('scripts/validate-walls.mjs') && skillText.includes('run') && skillText.includes('exit'),
    'SKILL must route validate-walls as an executed oracle, not a prose reference',
  ),
  check(
    'all validate-walls harness entries resolve to scripts',
    wallHarnesses.every((name) => existsSync(join(skillRoot, 'scripts', name))),
    `missing wall harness script(s): ${wallHarnesses.filter((name) => !existsSync(join(skillRoot, 'scripts', name))).join(', ')}`,
  ),
  check(
    'new executable scripts are wall-covered or explicitly classified as support',
    unclassifiedScripts.length === 0,
    `unclassified script(s): ${unclassifiedScripts.join(', ')}`,
  ),
  ...harnessContracts.map(({ key, value }) => check(
    `contract has a requires trigger: ${value}`,
    requiresFunctionBodies(triggerText).some((body) => body.includes(key)),
    `${value} is declared but not activated by a requires* trigger`,
  )),
  ...harnessContracts.map(({ value }) => check(
    `contract has at least one mutation wall: ${value}`,
    validateWallsText.includes(value),
    `${value} is declared but validate-walls has no matching wall id or fixture`,
  )),
  check(
    'meta-certification is itself routed by validate-walls',
    validateWallsText.includes('goal-maestro-harness-certification.mjs'),
    'validate-walls must run goal-maestro-harness-certification.mjs',
  ),
  check(
    'staged gate re-runs walls for all Goal Maestro skill surfaces',
    stagedGateText.includes('src/adapters/claude/skills/tes-goal-maestro/scripts/validate-walls.mjs')
      && stagedGateText.includes('*/skills/tes-goal-maestro/**'),
    'staged gate must not limit goal-maestro-walls to scripts/*.mjs only',
  ),
  check(
    'closure gate re-runs validate-walls',
    packageText.includes('node src/adapters/claude/skills/tes-goal-maestro/scripts/validate-walls.mjs'),
    'package.json commit:closure must include validate-walls',
  ),
  ...treeParityChecks(sourceClaudeRoot, sourceCodexRoot, 'source Claude/Codex'),
  ...treeParityChecks(localClaudeRoot, localCodexRoot, 'local development Claude/Codex'),
  ...treeParityChecks(sourceClaudeRoot, localClaudeRoot, 'source/local Claude'),
  ...treeParityChecks(sourceCodexRoot, localCodexRoot, 'source/local Codex'),
];

runChecks('goal-maestro harness certification', checks);

function findRepoRoot(start) {
  let current = start;
  while (current && current !== dirname(current)) {
    if (existsSync(join(current, 'package.json')) && existsSync(join(current, 'AGENTS.md'))) {
      return current;
    }
    current = dirname(current);
  }
  throw new Error(`repo root not found from ${start}`);
}

function readText(path) {
  return readFileSync(path, 'utf8');
}

function uniqueStrings(values) {
  return [...new Set(values)].sort();
}

function check(name, pass, detail) {
  return { name, pass, detail: pass ? undefined : detail };
}

function extractConstStrings(text, regex) {
  return [...text.matchAll(regex)].map((match) => ({ key: match[1], value: match[2] }));
}

function requiresFunctionBodies(text) {
  return [...text.matchAll(/function\s+requires[A-Za-z0-9]+\([^)]*\)\s*\{([\s\S]*?)\n\}/g)].map((match) => match[1]);
}

function executableScriptFiles(root) {
  return readdirSync(root)
    .filter((name) => name.endsWith('.mjs'))
    .sort();
}

function treeParityChecks(leftRoot, rightRoot, label) {
  const leftFiles = fileMap(leftRoot);
  const rightFiles = fileMap(rightRoot);
  const relpaths = uniqueStrings([...Object.keys(leftFiles), ...Object.keys(rightFiles)]);
  const failures = [];
  for (const relpath of relpaths) {
    if (!leftFiles[relpath]) {
      failures.push(`missing left ${relpath}`);
      continue;
    }
    if (!rightFiles[relpath]) {
      failures.push(`missing right ${relpath}`);
      continue;
    }
    if (readFileSync(leftFiles[relpath]).compare(readFileSync(rightFiles[relpath])) !== 0) {
      failures.push(`drift ${relpath}`);
    }
  }
  if (label === simulatedParityDriftLabel) {
    failures.push('simulated tree drift');
  }
  return [{
    name: `${label} trees are byte-identical`,
    pass: failures.length === 0,
    detail: failures.slice(0, 8).join('; '),
  }];
}

function fileMap(root) {
  const files = {};
  if (!existsSync(root)) return files;
  walk(root, (path) => {
    const relpath = relative(root, path);
    files[relpath] = path;
  });
  return files;
}

function walk(root, visit) {
  for (const name of readdirSync(root)) {
    if (name === '.DS_Store' || name === '__pycache__') continue;
    const path = join(root, name);
    const stats = statSync(path);
    if (stats.isDirectory()) {
      walk(path, visit);
      continue;
    }
    if (name.endsWith('.pyc') || name.endsWith('.pyo')) continue;
    visit(path);
  }
}
