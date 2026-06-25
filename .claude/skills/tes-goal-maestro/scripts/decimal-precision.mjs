// Harness FIN3 (SPEC-009) — Precisão decimal monetária.
// node-puro: grep estático sobre source financeiro — rejeita float para dinheiro
// (parseFloat/Number em valores monetários, colunas FLOAT/DOUBLE para money). Exige
// Decimal/integer-cents. Um `parseFloat(price)` em código financeiro → exit≠0.
//
//   node scripts/decimal-precision.mjs <file1> [file2 ...]
//
// Heurística: sinais de dinheiro (amount/price/total/balance/value) + float = suspeito.

import { runChecks, readText } from './lib/harness.mjs';

const MONEY = String.raw`(?:\w+\.)?(?:amount|price|total|balance|value|cost|fee|sum|money)`;
// Float aplicado a contexto monetário, por várias rotas (o auditor escapou via +x e *1.0):
//   parseFloat(amount) | Number(total) | +amount (unary plus) | total * 1.0 | price / 1.0 | parseFloat(this.amount)
const FLOAT_ON_MONEY = new RegExp(
  [
    String.raw`(parseFloat|Number)\s*\([^)]*\b${MONEY}\b`, // parseFloat(...amount...)
    String.raw`(^|[^\w.])\+\s*${MONEY}\b`, // +amount (unary plus → float coercion)
    String.raw`\b${MONEY}\b\s*[*/]\s*1\.0\b`, // amount * 1.0 / total / 1.0
    String.raw`\b${MONEY}\b\s*=\s*\d+\.\d+`, // total = 50.25 (literal float em var monetária)
  ].join('|'),
  'i',
);
// Coluna de schema FLOAT/DOUBLE/REAL para dinheiro.
const FLOAT_COLUMN = /\b(amount|price|total|balance|value|cost|fee)\b[^;\n]*\b(FLOAT|DOUBLE|REAL)\b/i;

const files = process.argv.slice(2);
if (files.length === 0) {
  console.error('uso: node scripts/decimal-precision.mjs <file1> [...]');
  process.exit(2);
}

const checks = [];
for (const file of files) {
  let text;
  try {
    text = readText(file);
  } catch (e) {
    checks.push({ name: `${file}: readable`, pass: false, detail: e.message });
    continue;
  }
  const lines = text.split('\n');
  let offenders = 0;
  lines.forEach((line, i) => {
    if (FLOAT_ON_MONEY.test(line) || FLOAT_COLUMN.test(line)) {
      offenders++;
      checks.push({
        name: `${file}:${i + 1} no float arithmetic on money`,
        pass: false,
        detail: `dinheiro como float (use Decimal ou inteiro em centavos): ${line.trim()}`,
      });
    }
  });
  if (offenders === 0) checks.push({ name: `${file}: no float-on-money`, pass: true });
}

runChecks('FIN3 decimal-precision', checks);
