// Harness DB3 (SPEC-005) — Integridade referencial.
// node-puro: dada uma fixture de tabelas + FKs declaradas, exige que toda linha-filha aponte
// para um pai existente e que toda FK referencie uma tabela que existe. exit≠0 → órfã ou FK quebrada.
//
//   node scripts/referential-integrity.mjs <schema.json>
//
// Formato:
//   { "tables": { "users": [{"id":1}], "orders": [{"id":10,"user_id":1}] },
//     "fks": [ {"table":"orders","field":"user_id","references":"users","ref_field":"id"} ] }

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/referential-integrity.mjs <schema.json>');
  process.exit(2);
}
let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`schema inválido: ${e.message}`);
  process.exit(2);
}

const tables = cfg.tables || {};
const fks = Array.isArray(cfg.fks) ? cfg.fks : [];
const checks = [];

if (fks.length === 0) {
  checks.push({ name: 'fks declared', pass: false, detail: 'fks[] vazio — nada a validar' });
  runChecks('DB3 referential-integrity', checks);
}

for (const fk of fks) {
  // (1) a tabela referenciada existe
  const refTable = tables[fk.references];
  if (!refTable) {
    checks.push({ name: `${fk.table}.${fk.field} → ${fk.references}: target table exists`, pass: false, detail: `tabela "${fk.references}" não existe (FK quebrada)` });
    continue;
  }
  // (2) toda linha-filha aponta para um pai existente (sem órfã)
  const validKeys = new Set(refTable.map((r) => r[fk.ref_field]));
  const childRows = tables[fk.table] || [];
  const orphans = childRows.filter((r) => r[fk.field] != null && !validKeys.has(r[fk.field]));
  checks.push({
    name: `${fk.table}.${fk.field} → ${fk.references}.${fk.ref_field}: no orphan rows`,
    pass: orphans.length === 0,
    detail: orphans.length === 0 ? undefined : `${orphans.length} órfã(s): ${JSON.stringify(orphans.map((o) => o[fk.field]))}`,
  });
}

runChecks('DB3 referential-integrity', checks);
