// Harness UX1 (SPEC-016) — Responsividade. CLASSE DEP-PESADA (Playwright).
// Renderiza o app em ≥3 breakpoints e exige sem scroll-h e sem overflow/cut-off.
// SEM Playwright instalado → BLOCKED-provado (exit 2), NUNCA PASS falso.
// Com Playwright → roda os viewports de verdade. Prova os 2 caminhos via report-fixture.
//
//   node scripts/responsive-check.mjs <report.json>
//
// O report é produzido por um runner Playwright real; o harness certifica o resultado.
// Se report.playwright_available=false → BLOCKED. Senão, valida os viewports.
//   { "playwright_available": true,
//     "viewports": [ {"width":375,"overflow":false}, {"width":768,"overflow":false}, {"width":1440,"overflow":false} ] }

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/responsive-check.mjs <report.json>');
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

// Dependência deve ser provada PRESENTE (=== true), não apenas "não-false": um report que
// OMITE playwright_available não comprova que rodou no browser → BLOCKED, nunca PASS.
if (r.playwright_available !== true) {
  checks.push({
    name: 'responsive check ran in a real browser',
    pass: false,
    blocked: true,
    blockedProof: `playwright_available=${JSON.stringify(r.playwright_available)} (não comprovadamente true): sem browser headless`,
  });
  runChecks('UX1 responsive-check', checks);
}

const viewports = Array.isArray(r.viewports) ? r.viewports : [];
const REQUIRED = [375, 768, 1440];
for (const w of REQUIRED) {
  const v = viewports.find((x) => x.width === w);
  checks.push({
    name: `viewport ${w}w: rendered without horizontal overflow`,
    pass: v ? v.overflow === false : false,
    detail: v ? (v.overflow ? 'overflow/cut-off detectado' : undefined) : 'viewport não testado',
  });
}

runChecks('UX1 responsive-check', checks);
