// Harness LLM2 (SPEC-012) — Token budget.
// node-puro: app declara teto de tokens/request; o harness parseia um log de N samples e
// exige max(prompt+completion) ≤ teto. Uma call que estoura o teto sem flag → exit≠0.
//
//   node scripts/token-budget.mjs <usage.json>
//
// Formato:
//   { "budget": 50000,
//     "samples": [ {"id":"r1","prompt_tokens":1200,"completion_tokens":800} ] }

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/token-budget.mjs <usage.json>');
  process.exit(2);
}
let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`usage inválido: ${e.message}`);
  process.exit(2);
}

const budget = cfg.budget;
const samples = Array.isArray(cfg.samples) ? cfg.samples : [];
const checks = [];

if (typeof budget !== 'number' || samples.length === 0) {
  checks.push({ name: 'budget and samples present', pass: false, detail: 'falta budget numérico ou samples[]' });
  runChecks('LLM2 token-budget', checks);
}

for (const s of samples) {
  // Métrica ausente NÃO é "0 gasto" — é evidência faltando. Sample sem os campos de token
  // não prova nada (o auditor expôs `{"id":"r1"}` → PASS falso de "0 tokens").
  if (typeof s.prompt_tokens !== 'number' || typeof s.completion_tokens !== 'number') {
    checks.push({ name: `sample ${s.id}: declares prompt_tokens and completion_tokens`, pass: false, detail: 'campos de token ausentes — gasto não-medido, não "0"' });
    continue;
  }
  const total = s.prompt_tokens + s.completion_tokens;
  checks.push({
    name: `sample ${s.id}: ${total} tokens ≤ budget ${budget}`,
    pass: total <= budget,
    detail: total <= budget ? undefined : `estourou: ${total} > ${budget}`,
  });
}

runChecks('LLM2 token-budget', checks);
