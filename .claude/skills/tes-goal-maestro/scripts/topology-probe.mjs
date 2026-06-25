// Harness C2 — Probe estrutural versionado com exit-code.
// É o probe que a parede exige existir NO DIFF (não comando ad-hoc): conta linhas de
// cada arquivo-alvo contra um budget e falha (exit≠0 → topology_probe_result=FAIL →
// NEEDS_STRUCTURAL_METHOD) quando qualquer arquivo excede. O reviewer re-roda este script.
//
//   node scripts/topology-probe.mjs <budget.json>
//
// Formato:
//   { "budget": 300, "files": ["src/game.ts", "src/render.ts"] }   // budget de linhas por arquivo
//   { "targets": [ {"file":"src/game.ts","max":300} ] }            // ou budget por arquivo

import { readFileSync } from 'node:fs';
import { runChecks, readText } from './lib/harness.mjs';

function lineCount(path) {
  return readFileSync(path, 'utf8').split('\n').length;
}

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/topology-probe.mjs <budget.json>');
  process.exit(2);
}

let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`budget inválido: ${e.message}`);
  process.exit(2);
}

// Normaliza para [{file, max}]
let targets = [];
if (Array.isArray(cfg.targets)) {
  targets = cfg.targets;
} else if (Array.isArray(cfg.files) && typeof cfg.budget === 'number') {
  targets = cfg.files.map((file) => ({ file, max: cfg.budget }));
}

const checks = [];
if (targets.length === 0) {
  checks.push({ name: 'topology budget targets present', pass: false, detail: 'sem files+budget nem targets[]' });
  runChecks('C2 topology-probe', checks);
}

for (const t of targets) {
  let count;
  try {
    count = lineCount(t.file);
  } catch (e) {
    checks.push({ name: `${t.file}: readable`, pass: false, detail: `não pôde ler: ${e.message}` });
    continue;
  }
  checks.push({
    name: `${t.file}: ${count} lines ≤ budget ${t.max}`,
    pass: count <= t.max,
    detail: count <= t.max ? undefined : `EXCEDE: ${count} > ${t.max}`,
  });
}

runChecks('C2 topology-probe', checks);
