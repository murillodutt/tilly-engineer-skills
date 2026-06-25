// Harness D3 — Wiring de oráculo em gate persistente.
// Falha (exit≠0 → eixo a DEGRADED/AXIS_UNPROVEN, nunca GO) quando um oráculo de eixo
// required não é referenciado por nenhum gate persistente (pre-commit ou CI por-workspace).
// GO exige oracle_ci_wired=yes provado por rg 'certify' .github/workflows/ não-vazio.
//
//   node scripts/oracle-wiring-check.mjs <wiring.json>
//
// Formato:
//   {
//     "requiredOracles": ["certify.ts", "lumaCheck.ts"],
//     "ciGlob": ".github/workflows",        // dir varrido por menção aos oráculos
//     "precommit": ".husky/pre-commit",     // arquivo opcional de pre-commit
//     "wiredText": "...conteúdo concatenado dos gates persistentes..."  // ou deixa o harness ler ciGlob
//   }

import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { runChecks } from './lib/harness.mjs';

function readDirText(dir) {
  if (!existsSync(dir)) return '';
  let text = '';
  for (const entry of readdirSync(dir)) {
    try {
      text += readFileSync(join(dir, entry), 'utf8') + '\n';
    } catch { /* ignora subdirs */ }
  }
  return text;
}

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/oracle-wiring-check.mjs <wiring.json>');
  process.exit(2);
}

let cfg;
try {
  cfg = JSON.parse(readFileSync(path, 'utf8'));
} catch (e) {
  console.error(`config inválida: ${e.message}`);
  process.exit(2);
}

// Texto dos gates persistentes: explícito (wiredText) ou lido do ciGlob + precommit.
let gateText = cfg.wiredText || '';
if (!gateText) {
  gateText += readDirText(cfg.ciGlob || '.github/workflows');
  if (cfg.precommit && existsSync(cfg.precommit)) gateText += readFileSync(cfg.precommit, 'utf8');
}

const required = Array.isArray(cfg.requiredOracles) ? cfg.requiredOracles : [];
const checks = [];

if (required.length === 0) {
  checks.push({ name: 'required oracles declared', pass: false, detail: 'requiredOracles[] vazio' });
  runChecks('D3 oracle-wiring-check', checks);
}

for (const oracle of required) {
  const wired = gateText.includes(oracle);
  checks.push({
    name: `oracle "${oracle}" wired into a persistent gate`,
    pass: wired,
    detail: wired ? undefined : `não referenciado por CI/pre-commit → eixo DEGRADED, nunca GO`,
  });
}

runChecks('D3 oracle-wiring-check', checks);
