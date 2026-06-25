// Harness DB4 (SPEC-006) — Reconciliação de batch.
// node-puro: dado um batch de N linhas de entrada e o resultado processado, exige
// input_count == output_count + skipped_com_razão. Linhas que sumiram sem razão de skip
// (timeout/erro não-logado) → exit≠0. Pega o "tally final 950 de 1000 sem log".
//
//   node scripts/batch-reconcile.mjs <batch.json>
//
// Formato:
//   { "input_count": 1000,
//     "output_count": 950,
//     "skipped": [ {"reason":"invalid_format","count":30}, {"reason":"timeout","count":20} ] }

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/batch-reconcile.mjs <batch.json>');
  process.exit(2);
}
let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`batch inválido: ${e.message}`);
  process.exit(2);
}

const checks = [];

// Guarda de entrada: input degenerado não PROVA reconciliação — FAIL, nunca vacuous-PASS.
// Um batch sem input_count declarado não tem o que reconciliar (o auditor expôs `{}` → PASS falso).
if (typeof cfg.input_count !== 'number' || typeof cfg.output_count !== 'number') {
  checks.push({ name: 'batch declares input_count and output_count', pass: false, detail: 'contadores ausentes — nada a reconciliar (input degenerado não prova)' });
  runChecks('DB4 batch-reconcile', checks);
}

const input = cfg.input_count;
const output = cfg.output_count;
const skipped = Array.isArray(cfg.skipped) ? cfg.skipped : [];
const skippedTotal = skipped.reduce((s, x) => s + (x.count || 0), 0);
const allSkipsHaveReason = skipped.every((x) => x.reason && x.reason.length > 0);

// (1) toda linha de skip tem razão (nenhum silêncio)
checks.push({
  name: 'every skipped row carries a reason',
  pass: allSkipsHaveReason,
  detail: allSkipsHaveReason ? undefined : 'há skip sem reason (silêncio = perda não-rastreada)',
});

// (2) input == output + skipped (nenhuma linha desaparece sem conta)
const reconciled = output + skippedTotal === input;
checks.push({
  name: `input (${input}) == output (${output}) + skipped (${skippedTotal})`,
  pass: reconciled,
  detail: reconciled ? undefined : `desbalanço: ${input - output - skippedTotal} linha(s) sumiram sem conta`,
});

runChecks('DB4 batch-reconcile', checks);
