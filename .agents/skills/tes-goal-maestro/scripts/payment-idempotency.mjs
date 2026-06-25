// Harness FIN2 (SPEC-008) — Idempotência de pagamento.
// node-puro: simula 2 POSTs /charge com o mesmo idempotency_key e exige que o 2º retorne
// o MESMO charge_id (não uma 2ª cobrança). Replay com key igual gerando charge_id distinto
// → exit≠0 (cobrança dupla — o bug financeiro clássico).
//
//   node scripts/payment-idempotency.mjs <charges.json>
//
// Formato (log de cobranças observado):
//   { "charges": [
//       {"idempotency_key":"k1","charge_id":"ch_1","amount":50},
//       {"idempotency_key":"k1","charge_id":"ch_1","amount":50}   // replay correto: mesmo charge_id
//   ] }

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/payment-idempotency.mjs <charges.json>');
  process.exit(2);
}
let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`charges inválido: ${e.message}`);
  process.exit(2);
}

const charges = Array.isArray(cfg.charges) ? cfg.charges : [];
const checks = [];

if (charges.length === 0) {
  checks.push({ name: 'charges exist', pass: false, detail: 'charges[] vazio' });
  runChecks('FIN2 payment-idempotency', checks);
}

// Para cada idempotency_key, todos os charge_id devem ser iguais (replay = mesma cobrança).
const byKey = {};
for (const c of charges) {
  (byKey[c.idempotency_key] || (byKey[c.idempotency_key] = new Set())).add(c.charge_id);
}
for (const [key, ids] of Object.entries(byKey)) {
  const single = ids.size === 1;
  checks.push({
    name: `idempotency_key "${key}": single charge_id across replays`,
    pass: single,
    detail: single ? undefined : `cobrança dupla: ${ids.size} charge_ids distintos para a mesma key (${[...ids].join(', ')})`,
  });
}

runChecks('FIN2 payment-idempotency', checks);
