// Harness LLM4 (SPEC-014) — RAG relevance. CLASSE NÃO-DETERMINÍSTICA.
// O score de relevância vem de embedding/modelo (não-determinístico). Para colidir com D1
// (precisa disparar/passar de forma ESTÁVEL), o harness opera sobre um GOLD CONGELADO de
// scores (determinístico) quando presente; se o gold/modelo não está disponível, emite
// BLOCKED-provado (exit 2) — NUNCA PASS instável nem PASS falso.
//
//   node scripts/rag-relevance.mjs <rag.json>
//
// Formato:
//   { "floor": 0.70,
//     "frozen_scores": [ {"query":"q1","top1_score":0.82} ],   // gold congelado → determinístico
//     "live_model": false }                                     // se true e sem frozen → BLOCKED

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/rag-relevance.mjs <rag.json>');
  process.exit(2);
}
let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`rag inválido: ${e.message}`);
  process.exit(2);
}

const floor = cfg.floor ?? 0.7;
const frozen = Array.isArray(cfg.frozen_scores) ? cfg.frozen_scores : [];
const checks = [];

// Sem gold congelado: a relevância só viria de um modelo vivo (não-determinístico).
// Honestidade: BLOCKED-provado, não PASS instável, não PASS falso.
if (frozen.length === 0) {
  checks.push({
    name: 'RAG relevance is deterministic (frozen gold present)',
    pass: false,
    blocked: true,
    blockedProof: 'sem frozen_scores: relevância só de modelo vivo (não-determinístico) — gold congelado ausente',
  });
  runChecks('LLM4 rag-relevance', checks);
}

// Com gold congelado: determinístico — top1 de cada query ≥ floor.
for (const s of frozen) {
  checks.push({
    name: `query "${s.query}": top1 relevance ${s.top1_score} ≥ floor ${floor}`,
    pass: s.top1_score >= floor,
    detail: s.top1_score >= floor ? undefined : `abaixo do piso: ${s.top1_score} < ${floor}`,
  });
}

runChecks('LLM4 rag-relevance', checks);
