// Meta-wall SPEC-004 — o painel REJEITA diversidade vacuosa (refutadores-clone).
// Um painel de R refutadores com rótulos (lens) DIFERENTES mas CORPOS IDÊNTICOS
// (mutate+revert+decoy_mutate iguais) é diversidade de fachada: não prova R lentes
// disjuntas, só renomeia uma. Este harness FALHA (exit≠0) quando algum painel tem
// refutadores cujas tuplas {mutate,revert,decoy_mutate} não são distintas, e PASSA
// quando os refutadores têm corpos genuinamente distintos.
//
//   node scripts/panel-diversity.mjs <plan.json>
//
// O discriminador compara CORPOS, não rótulos: dois refutadores com o mesmo
// {mutate,revert,decoy_mutate} são clones mesmo com lens diferentes.

import { readText, runChecks } from './lib/harness.mjs';

const planPath = process.argv[2];
if (!planPath) {
  console.error('uso: node scripts/panel-diversity.mjs <plan.json>');
  process.exit(2);
}

let plan;
try {
  plan = JSON.parse(readText(planPath));
} catch (e) {
  console.error(`plano inválido: ${e.message}`);
  process.exit(2);
}

const oracles = Array.isArray(plan.oracles) ? plan.oracles : [];
const checks = [];

// Assinatura de CORPO de um refutador (não inclui o rótulo lens).
function bodyKey(r) {
  return JSON.stringify([r.mutate ?? null, r.revert ?? null, r.decoy_mutate ?? null]);
}

// Apenas oráculos em modo painel (com refuters[]) são auditáveis aqui.
const panels = oracles.filter((o) => Array.isArray(o.refuters));

if (panels.length === 0) {
  // Sem painéis declarados → nada a provar → falha (nunca vacuous-PASS).
  checks.push({ name: 'plan has panel oracles (refuters[])', pass: false, detail: 'nenhum oráculo em modo painel' });
  runChecks('META panel-diversity', checks);
}

for (const o of panels) {
  const label = o.axis || o.name || 'oracle';
  const refuters = o.refuters;

  // Um painel precisa de pelo menos 2 refutadores para que "diversidade" seja afirmável.
  if (refuters.length < 2) {
    checks.push({
      name: `${label}: panel has >= 2 refuters`,
      pass: false,
      detail: `painel com ${refuters.length} refutador(es) — quorum-with-veto exige >= 2 lentes`,
    });
    continue;
  }

  const keys = refuters.map(bodyKey);
  const distinct = new Set(keys);
  const allDistinct = distinct.size === keys.length;
  checks.push({
    name: `${label}: refuter bodies are distinct (no clones)`,
    pass: allDistinct,
    detail: allDistinct
      ? undefined
      : `diversidade vacuosa: ${keys.length} refutadores, só ${distinct.size} corpo(s) {mutate,revert,decoy_mutate} distinto(s) — clones com lens renomeada`,
  });
}

runChecks('META panel-diversity', checks);
