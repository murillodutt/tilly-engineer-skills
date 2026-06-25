// Harness UX3 (SPEC-015) — i18n coverage. node-puro.
// Toda string externalizada deve estar traduzida no idioma fallback 100%; demais idiomas ≥ piso.
// Chave faltando no fallback → exit≠0. Conta chaves, determinístico.
//
//   node scripts/i18n-coverage.mjs <i18n.json>
//
// Formato:
//   { "fallback": "pt-BR", "floor": 0.90,
//     "keys": ["submit","cancel","save"],
//     "translations": { "pt-BR": {"submit":"Enviar","cancel":"Cancelar","save":"Salvar"},
//                       "en": {"submit":"Submit","cancel":"Cancel"} } }

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/i18n-coverage.mjs <i18n.json>');
  process.exit(2);
}
let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`i18n inválido: ${e.message}`);
  process.exit(2);
}

const keys = Array.isArray(cfg.keys) ? cfg.keys : [];
const fallback = cfg.fallback;
const floor = cfg.floor ?? 0.9;
const translations = cfg.translations || {};
const checks = [];

if (keys.length === 0 || !fallback) {
  checks.push({ name: 'keys and fallback declared', pass: false, detail: 'falta keys[] ou fallback' });
  runChecks('UX3 i18n-coverage', checks);
}

// (1) fallback 100%
const fb = translations[fallback] || {};
const fbMissing = keys.filter((k) => !fb[k]);
checks.push({
  name: `fallback "${fallback}" is 100% translated`,
  pass: fbMissing.length === 0,
  detail: fbMissing.length === 0 ? undefined : `faltam no fallback: ${fbMissing.join(', ')}`,
});

// (2) demais idiomas ≥ piso
for (const [lang, dict] of Object.entries(translations)) {
  if (lang === fallback) continue;
  const present = keys.filter((k) => dict[k]).length;
  const ratio = present / keys.length;
  checks.push({
    name: `"${lang}" coverage ${(ratio * 100).toFixed(0)}% ≥ floor ${(floor * 100).toFixed(0)}%`,
    pass: ratio >= floor,
    detail: ratio >= floor ? undefined : `${present}/${keys.length} traduzidas`,
  });
}

runChecks('UX3 i18n-coverage', checks);
