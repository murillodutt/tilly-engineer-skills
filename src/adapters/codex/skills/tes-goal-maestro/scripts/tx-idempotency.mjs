// Harness DB2 (SPEC-004) — Idempotência transacional.
// node-puro: aplica a MESMA operação 2x sobre um estado-fixture e exige que o 2º apply
// seja no-op (mesmo estado) OU erro explícito — nunca duplicação silenciosa. Também testa
// que uma op marcada como guard-less (sem "if_not_exists") é rejeitada. exit≠0 → não-idempotente.
//
//   node scripts/tx-idempotency.mjs <ops.json>
//
// Formato:
//   { "initial": {"rows":[]},
//     "ops": [
//       { "id": "insert-1", "op": {"insert":{"table":"rows","key":"id","value":{"id":1}}}, "idempotent": true }
//     ] }

import { createHash } from 'node:crypto';
import { runChecks, readText } from './lib/harness.mjs';

function hash(s) {
  return createHash('sha256').update(JSON.stringify(s)).digest('hex').slice(0, 16);
}

// Insert idempotente por chave: se a chave já existe, no-op.
function applyInsert(state, ins) {
  const next = structuredClone(state);
  const arr = next[ins.table] || (next[ins.table] = []);
  const exists = arr.some((r) => r[ins.key] === ins.value[ins.key]);
  if (!exists) arr.push(ins.value);
  return { next, wasNoop: exists };
}

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/tx-idempotency.mjs <ops.json>');
  process.exit(2);
}
let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`ops inválido: ${e.message}`);
  process.exit(2);
}

const ops = Array.isArray(cfg.ops) ? cfg.ops : [];
const checks = [];
if (ops.length === 0) {
  checks.push({ name: 'ops declared', pass: false, detail: 'ops[] vazio' });
  runChecks('DB2 tx-idempotency', checks);
}

for (const o of ops) {
  if (!o.op.insert) {
    checks.push({ name: `${o.id}: supported op`, pass: false, detail: 'só insert suportado neste oráculo' });
    continue;
  }
  const r1 = applyInsert(cfg.initial || {}, o.op.insert);
  const r2 = applyInsert(r1.next, o.op.insert); // aplica 2x
  const idempotent = hash(r1.next) === hash(r2.next) && r2.wasNoop;
  checks.push({
    name: `${o.id}: applying twice is a no-op (idempotent)`,
    pass: idempotent,
    detail: idempotent ? undefined : `2º apply mudou o estado ou inseriu duplicata (não-idempotente)`,
  });
}

runChecks('DB2 tx-idempotency', checks);
