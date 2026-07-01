// Harness FIN1 (SPEC-007) — Double-entry (partidas dobradas).
// node-puro: dado um ledger contábil, exige que toda transação committed tenha
// SUM(débitos) == SUM(créditos). Uma tx com débito sem crédito correspondente → exit≠0.
// É a parede contábil fundamental: dinheiro não some nem aparece.
//
//   node scripts/ledger-double-entry.mjs <ledger.json>
//
// Formato:
//   { "entries": [
//       {"tx":"t1","account":"caixa","debit":100,"credit":0,"status":"COMMITTED"},
//       {"tx":"t1","account":"receita","debit":0,"credit":100,"status":"COMMITTED"}
//   ] }

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/ledger-double-entry.mjs <ledger.json>');
  process.exit(2);
}
let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`ledger inválido: ${e.message}`);
  process.exit(2);
}

const entries = (Array.isArray(cfg.entries) ? cfg.entries : []).filter((e) => e.status === 'COMMITTED');
const checks = [];

if (entries.length === 0) {
  checks.push({ name: 'committed entries exist', pass: false, detail: 'nenhuma entrada COMMITTED' });
  runChecks('FIN1 double-entry', checks);
}

// Agrupa por tx e exige balanço zero por transação (em centavos, para evitar float).
const byTx = {};
for (const e of entries) {
  byTx[e.tx] ??= [];
  byTx[e.tx].push(e);
}
for (const [tx, rows] of Object.entries(byTx)) {
  const debit = rows.reduce((s, r) => s + Math.round((r.debit || 0) * 100), 0);
  const credit = rows.reduce((s, r) => s + Math.round((r.credit || 0) * 100), 0);
  const balanced = debit === credit;
  checks.push({
    name: `tx ${tx}: SUM(debits) == SUM(credits)`,
    pass: balanced,
    detail: balanced ? undefined : `desbalanço: débitos=${debit / 100} ≠ créditos=${credit / 100}`,
  });
}

runChecks('FIN1 double-entry', checks);
