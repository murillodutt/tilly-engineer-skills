// Harness UX2 (SPEC-017) — Acessibilidade WCAG. CLASSE DEP-PESADA (Axe).
// Toda página passa Axe com 0 violações de contraste/alt/foco/semântica.
// SEM Axe disponível → BLOCKED-provado (exit 2). Com Axe → valida o report de violações.
//
//   node scripts/a11y-audit.mjs <report.json>
//
//   { "axe_available": true, "violations": [] }   // 0 violações → PASS
//   { "axe_available": false }                     // → BLOCKED

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/a11y-audit.mjs <report.json>');
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

// Honestidade: a dependência deve ser provada PRESENTE (=== true), não apenas "não-false".
// Um report que OMITE axe_available não comprova que Axe rodou → BLOCKED, nunca PASS.
if (r.axe_available !== true) {
  checks.push({
    name: 'a11y audit ran with Axe',
    pass: false,
    blocked: true,
    blockedProof: `axe_available=${JSON.stringify(r.axe_available)} (não comprovadamente true): sem evidência de que Axe rodou`,
  });
  runChecks('UX2 a11y-audit', checks);
}

const violations = Array.isArray(r.violations) ? r.violations : [];
checks.push({
  name: 'zero WCAG violations (contrast/alt/focus/semantics)',
  pass: violations.length === 0,
  detail: violations.length === 0 ? undefined : `${violations.length} violação(ões): ${violations.map((v) => v.id || v).join(', ')}`,
});

runChecks('UX2 a11y-audit', checks);
