// Harness FIN4 (SPEC-010) — Audit-trail imutável.
// node-puro: dado um log de operações sobre o audit_log, exige que ele seja append-only —
// nenhum DELETE/UPDATE sobre linhas existentes, e toda tx financeira tem entrada de trail
// (before/after). Um DELETE FROM audit_log ou tx sem trail → exit≠0.
//
//   node scripts/audit-trail-immutable.mjs <audit.json>
//
// Formato:
//   { "operations": [ {"type":"INSERT","table":"audit_log","tx":"t1"}, {"type":"DELETE","table":"audit_log"} ],
//     "txs": ["t1","t2"],            // transações financeiras que DEVEM ter trail
//     "trail_txs": ["t1","t2"] }     // txs que efetivamente têm entrada no audit_log

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/audit-trail-immutable.mjs <audit.json>');
  process.exit(2);
}
let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`audit inválido: ${e.message}`);
  process.exit(2);
}

const checks = [];

// Guarda de entrada: sem operações declaradas E sem txs a auditar, não há trilha para PROVAR
// imutável (o auditor expôs `{}` → 2 vacuous-PASS). Input degenerado é FAIL, nunca PASS.
if (!Array.isArray(cfg.operations) || !Array.isArray(cfg.txs)) {
  checks.push({ name: 'audit declares operations[] and txs[]', pass: false, detail: 'operations/txs ausentes — nada a provar (input degenerado não certifica imutabilidade)' });
  runChecks('FIN4 audit-trail-immutable', checks);
}

const ops = cfg.operations;

// (1) append-only: nenhum DELETE/UPDATE sobre audit_log
const mutations = ops.filter((o) => o.table === 'audit_log' && (o.type === 'DELETE' || o.type === 'UPDATE'));
checks.push({
  name: 'audit_log is append-only (no DELETE/UPDATE)',
  pass: mutations.length === 0,
  detail: mutations.length === 0 ? undefined : `${mutations.length} mutação(ões) proibida(s) no audit_log: ${mutations.map((m) => m.type).join(', ')}`,
});

// (2) toda tx financeira tem trail
const txs = cfg.txs;
const trail = new Set(cfg.trail_txs || []);
const missing = txs.filter((t) => !trail.has(t));
checks.push({
  name: 'every financial tx has an audit-trail entry',
  pass: missing.length === 0,
  detail: missing.length === 0 ? undefined : `tx sem trail: ${missing.join(', ')}`,
});

runChecks('FIN4 audit-trail-immutable', checks);
