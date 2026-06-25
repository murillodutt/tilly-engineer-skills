// Harness META — Completude de contexto por eixo.
// Antes de emitir o Worker Packet, falha (exit≠0 → NEEDS_CONTEXT) se QUALQUER eixo
// rastreável do anchor chega sem contexto resolvido: runtime_target, oracle_runner_contract
// com alvo de regressão, e — para eixos sob isolamento — forbidden-write/forbidden-import.
//
//   node scripts/context-completeness.mjs <packet.json>
//
// Formato:
//   { "axes": [
//       { "id": "browser-render", "isolated": true,
//         "runtime_target": "browser",
//         "oracle_runner_contract": "npx tsx cert.ts",
//         "regression_target": ".github/workflows/ci.yml",
//         "forbidden_write": ["/docs/**"], "forbidden_import": ["benchmark-002/"] }
//   ] }

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/context-completeness.mjs <packet.json>');
  process.exit(2);
}

let pkt;
try {
  pkt = JSON.parse(readText(path));
} catch (e) {
  console.error(`packet inválido: ${e.message}`);
  process.exit(2);
}

const axes = Array.isArray(pkt.axes) ? pkt.axes : [];
const checks = [];

if (axes.length === 0) {
  checks.push({ name: 'packet has traceable axes', pass: false, detail: 'axes[] vazio — nada para emitir' });
  runChecks('META context-completeness', checks);
}

const VALID_TARGET = /^(node|browser|isomorphic)$/;

for (const a of axes) {
  const id = a.id || '(unnamed axis)';

  checks.push({
    name: `${id}: runtime_target resolved`,
    pass: VALID_TARGET.test(a.runtime_target || ''),
    detail: VALID_TARGET.test(a.runtime_target || '') ? undefined : `runtime_target inválido/ausente: "${a.runtime_target}"`,
  });

  const hasContract = typeof a.oracle_runner_contract === 'string' && a.oracle_runner_contract.length > 0;
  const hasRegression = typeof a.regression_target === 'string' && a.regression_target.length > 0;
  checks.push({
    name: `${id}: oracle_runner_contract with regression target`,
    pass: hasContract && hasRegression,
    detail: hasContract && hasRegression ? undefined : 'falta oracle_runner_contract e/ou regression_target',
  });

  if (a.isolated === true) {
    const fw = Array.isArray(a.forbidden_write) && a.forbidden_write.length > 0;
    const fi = Array.isArray(a.forbidden_import) && a.forbidden_import.length > 0;
    checks.push({
      name: `${id}: isolated axis declares forbidden-write/forbidden-import`,
      pass: fw && fi,
      detail: fw && fi ? undefined : 'eixo isolado sem forbidden_write e/ou forbidden_import (ADR-010)',
    });
  }
}

runChecks('META context-completeness', checks);
