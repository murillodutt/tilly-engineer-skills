// Harness UX4 (SPEC-018) — Core Web Vitals. CLASSE DEP-PESADA (Lighthouse/browser).
// LCP ≤ 2.5s, CLS ≤ 0.1, INP ≤ 200ms, medido em browser real.
// SEM Lighthouse/browser → BLOCKED-provado (exit 2). Com → valida as métricas.
//
//   node scripts/web-vitals.mjs <report.json>
//
//   { "lighthouse_available": true, "lcp_s": 2.1, "cls": 0.05, "inp_ms": 150 }
//   { "lighthouse_available": false }  // → BLOCKED

import { runChecks, readText } from './lib/harness.mjs';

const CEILINGS = { lcp_s: 2.5, cls: 0.1, inp_ms: 200 };

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/web-vitals.mjs <report.json>');
  process.exit(2);
}
let r;
try {
  r = JSON.parse(readText(path));
} catch (e) {
  console.error(`report inválido: ${e.message}`);
  process.exit(2);
}

const checks = [];

// Dependência provada PRESENTE (=== true), não "não-false": report sem lighthouse_available
// não comprova medição em browser real → BLOCKED, nunca FAIL-por-métrica-ausente nem PASS.
if (r.lighthouse_available !== true) {
  checks.push({
    name: 'web vitals measured in a real browser',
    pass: false,
    blocked: true,
    blockedProof: `lighthouse_available=${JSON.stringify(r.lighthouse_available)} (não comprovadamente true): sem Lighthouse/browser`,
  });
  runChecks('UX4 web-vitals', checks);
}

for (const [metric, ceiling] of Object.entries(CEILINGS)) {
  const val = r[metric];
  checks.push({
    name: `${metric} = ${val} ≤ ${ceiling}`,
    pass: typeof val === 'number' && val <= ceiling,
    detail: typeof val !== 'number' ? 'métrica ausente' : val <= ceiling ? undefined : `acima do teto: ${val} > ${ceiling}`,
  });
}

runChecks('UX4 web-vitals', checks);
