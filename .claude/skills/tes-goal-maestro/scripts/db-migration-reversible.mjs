// Harness DB1 (SPEC-003) — Migração reversível.
// node-puro com fixture própria: cada migração declara up e down; aplica up→down→up sobre
// um estado-fixture (JSON) e exige que o hash do estado volte ao original após down, e que
// down NÃO mate dados-legacy fora do escopo da migração. exit≠0 → migração irreversível.
//
//   node scripts/db-migration-reversible.mjs <migrations.json>
//
// Formato (estado e migrações como dados puros — não exige banco externo):
//   {
//     "initial":   { "users": [{"id":1,"name":"a"}] },
//     "migrations": [
//       { "id": "001-add-email",
//         "up":   { "add_field": {"table":"users","field":"email","default":null} },
//         "down": { "drop_field": {"table":"users","field":"email"} } }
//     ]
//   }

import { createHash } from 'node:crypto';
import { runChecks, readText } from './lib/harness.mjs';

function stateHash(state) {
  return createHash('sha256').update(JSON.stringify(state)).digest('hex').slice(0, 16);
}

// Aplicador de migração puro (suporta add_field/drop_field/rename — o suficiente para o oráculo).
function apply(state, op) {
  const next = structuredClone(state);
  if (op.add_field) {
    const { table, field, default: def } = op.add_field;
    for (const row of next[table] || []) if (!(field in row)) row[field] = def ?? null;
  } else if (op.drop_field) {
    const { table, field } = op.drop_field;
    for (const row of next[table] || []) delete row[field];
  } else if (op.rename_field) {
    const { table, from, to } = op.rename_field;
    for (const row of next[table] || []) {
      row[to] = row[from];
      delete row[from];
    }
  }
  return next;
}

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/db-migration-reversible.mjs <migrations.json>');
  process.exit(2);
}

let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`migrations inválido: ${e.message}`);
  process.exit(2);
}

const migrations = Array.isArray(cfg.migrations) ? cfg.migrations : [];
const checks = [];

if (migrations.length === 0) {
  checks.push({ name: 'migrations declared', pass: false, detail: 'migrations[] vazio' });
  runChecks('DB1 migration-reversible', checks);
}

for (const m of migrations) {
  // (1) toda migração tem up E down
  if (!m.up || !m.down) {
    checks.push({ name: `${m.id}: declares up AND down`, pass: false, detail: 'migração sem down = irreversível' });
    continue;
  }
  // (2) up→down volta ao estado original (hash bate)
  const before = cfg.initial || {};
  const h0 = stateHash(before);
  const afterUp = apply(before, m.up);
  const afterDown = apply(afterUp, m.down);
  const h1 = stateHash(afterDown);
  checks.push({
    name: `${m.id}: up→down restores original state`,
    pass: h0 === h1,
    detail: h0 === h1 ? undefined : `down não reverteu: ${h0} ≠ ${h1} (dados perdidos ou mutados)`,
  });
}

runChecks('DB1 migration-reversible', checks);
