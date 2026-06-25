// Harness LLM1 (SPEC-011) — Eval coverage.
// node-puro: cada comportamento de prompt distinto declarado deve ter ≥1 eval case com
// oráculo (expected_output ou similarity threshold). Prompt sem nenhum eval → exit≠0.
// Conta cases, não roda o modelo — determinístico.
//
//   node scripts/eval-coverage.mjs <evals.json>
//
// Formato:
//   { "prompts": ["extract_dates","classify_intent"],
//     "evals": [ {"prompt":"extract_dates","expected":"2026-01-01"} ] }

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/eval-coverage.mjs <evals.json>');
  process.exit(2);
}
let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`evals inválido: ${e.message}`);
  process.exit(2);
}

const prompts = Array.isArray(cfg.prompts) ? cfg.prompts : [];
const evals = Array.isArray(cfg.evals) ? cfg.evals : [];
const checks = [];

if (prompts.length === 0) {
  checks.push({ name: 'prompts declared', pass: false, detail: 'prompts[] vazio' });
  runChecks('LLM1 eval-coverage', checks);
}

for (const p of prompts) {
  const cases = evals.filter((e) => e.prompt === p && (e.expected != null || e.similarity_threshold != null));
  checks.push({
    name: `prompt "${p}" has ≥1 eval case with an oracle`,
    pass: cases.length >= 1,
    detail: cases.length >= 1 ? undefined : 'zero eval cases com expected/similarity — comportamento não-verificado',
  });
}

runChecks('LLM1 eval-coverage', checks);
