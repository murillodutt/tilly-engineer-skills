// Harness B1 phase-aware (SPEC-002) — negative-grep de símbolo-de-fase-errada.
// Generaliza runtime-import-grep além de node-em-browser: rejeita um símbolo gated por fase
// (livePaymentProcessor, realModelCall, pg.connect(realUrl)) usado FORA de allowed_phases.
// Serve DB/LLM/Financeiro com um só harness. exit≠0 → NEEDS_TREE_REPAIR.
//
//   node scripts/runtime-phase-grep.mjs <phase-config.json> <file1> [file2 ...]
//
// phase-config (entregue pelo envelope do eixo):
//   { "phase": "fixture",
//     "gated": [ {"symbol": "livePaymentProcessor", "allowed_phases": ["live"]},
//                {"symbol": "pg.connect", "allowed_phases": ["live","sandbox"]} ] }
//
// Regra: se o arquivo usa um símbolo gated e a fase corrente NÃO está em allowed_phases → FAIL.

import { runChecks, readText } from './lib/harness.mjs';

const cfgPath = process.argv[2];
const files = process.argv.slice(3);
if (!cfgPath || files.length === 0) {
  console.error('uso: node scripts/runtime-phase-grep.mjs <phase-config.json> <file1> [...]');
  process.exit(2);
}

let cfg;
try {
  cfg = JSON.parse(readText(cfgPath));
} catch (e) {
  console.error(`phase-config inválido: ${e.message}`);
  process.exit(2);
}

const phase = cfg.phase || 'unknown';
const gated = Array.isArray(cfg.gated) ? cfg.gated : [];
const checks = [];

if (gated.length === 0) {
  checks.push({ name: 'phase-config has gated symbols', pass: false, detail: 'gated[] vazio — nada a validar' });
  runChecks('B1 runtime-phase-grep', checks);
}

for (const file of files) {
  let text;
  try {
    text = readText(file);
  } catch (e) {
    checks.push({ name: `${file}: readable`, pass: false, detail: e.message });
    continue;
  }
  for (const g of gated) {
    if (!text.includes(g.symbol)) continue;
    const allowed = Array.isArray(g.allowed_phases) && g.allowed_phases.includes(phase);
    checks.push({
      name: `${file}: "${g.symbol}" allowed in phase "${phase}"`,
      pass: allowed,
      detail: allowed
        ? undefined
        : `usa "${g.symbol}" em phase=${phase}, só permitido em [${(g.allowed_phases || []).join(',')}]`,
    });
  }
}

if (checks.length === 0) {
  checks.push({ name: 'no gated symbol used (clean)', pass: true });
}

runChecks('B1 runtime-phase-grep', checks);
