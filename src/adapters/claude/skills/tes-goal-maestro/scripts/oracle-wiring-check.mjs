// Harness D3 — Wiring de oráculo provado por RE-MUTAÇÃO DO GATE (não por menção).
// Antes media gateText.includes(oracle) — menção textual = facade um nível acima
// (um gate que só NOMEIA o oráculo num comentário passava). Agora prova, espelhando
// audit-remutation.mjs um nível acima do oráculo, que o gate persistente REALMENTE
// re-roda o oráculo de eixo e que o exit≠0 é ATRIBUÍVEL ao oráculo (não a ruído):
//
//   node scripts/oracle-wiring-check.mjs <wiring.json>
//
// Por oráculo de eixo required:
//   (1) clean: gate_command e oracle_command saem 0;
//   (2) mutate a PROPRIEDADE NOMEADA do oráculo → oracle_command DEVE sair ≠0
//       (prova que a mutação ataca a propriedade, não um proxy);
//   (3) gate_command DEVE então sair ≠0 → o gate RE-RODA o oráculo (wired);
//       se o gate continua 0 com o oráculo quebrado → FACADE (gate não re-roda);
//   (4) controle negativo OBRIGATÓRIO (decoy_mutate): perturbação que o oráculo ignora;
//       o gate DEVE sair 0 nela — se falha no decoy, o exit≠0 do passo 3 não é
//       atribuível ao oráculo (falso-positivo de wiring) → FAIL;
//   (5) reverte sempre.
//
// Anti "oráculo-como-gate": gate_command não pode ser igual/substring de oracle_command
// (rodar o oráculo direto não é um gate persistente que o envolve).
//
// Furo residual conhecido (mesma fronteira de confiança de audit-remutation.mjs): este
// check prova que o gate_command DECLARADO re-roda o oráculo de forma atribuível; NÃO prova
// que esse comando É o gate persistente real apontado por regression_target. regression_target
// é exigido e rotula a proveniência; o fechamento total exige um canário de target instalado.
//
// Formato:
//   { "oracles": [ {
//       "axis": "browser-render",
//       "regression_target": ".github/workflows/ci.yml",  // ponteiro do Worker Packet (proveniência)
//       "gate_command": "npm run commit:check",            // ORACLE_WIRING_PROOF — o gate que re-roda
//       "oracle_command": "npx tsx cert.ts",               // o oráculo de eixo
//       "mutate": "<cmd que viola a propriedade nomeada do oráculo>",
//       "revert": "<cmd que restaura>",
//       "decoy_mutate": "<perturbação que o oráculo ignora>",
//       "decoy_revert": "<cmd que restaura o decoy>"
//   } ] }

import { execSync } from 'node:child_process';
import { readText, runChecks } from './lib/harness.mjs';

function run(cmd) {
  try {
    execSync(cmd, { stdio: 'pipe' });
    return 0;
  } catch (e) {
    return typeof e.status === 'number' ? e.status : 1;
  }
}

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/oracle-wiring-check.mjs <wiring.json>');
  process.exit(2);
}

let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`config inválida: ${e.message}`);
  process.exit(2);
}

const oracles = Array.isArray(cfg.oracles) ? cfg.oracles : [];
const checks = [];

if (oracles.length === 0) {
  // Sem oráculos de eixo required → nada para provar → falha (nunca vacuous-PASS).
  checks.push({ name: 'wiring has required-axis oracles', pass: false, detail: 'oracles[] vazio' });
  runChecks('D3 oracle-wiring-check', checks);
}

for (const o of oracles) {
  const label = o.axis || o.regression_target || 'oracle';

  // (0) campos rodáveis obrigatórios; regression_target exigido como proveniência.
  const hasFields = o.gate_command && o.oracle_command && o.mutate && o.decoy_mutate;
  checks.push({
    name: `${label}: declares gate_command/oracle_command/mutate/decoy_mutate`,
    pass: Boolean(hasFields),
    detail: hasFields ? undefined : 'faltam campos rodáveis (gate/oracle/mutate/decoy_mutate)',
  });
  checks.push({
    name: `${label}: declares regression_target (proveniência do gate)`,
    pass: typeof o.regression_target === 'string' && o.regression_target.length > 0,
    detail: o.regression_target ? undefined : 'regression_target ausente (ponteiro do Worker Packet)',
  });
  if (!hasFields) continue;

  // Anti "oráculo-como-gate": rodar o oráculo direto não é um gate que o envolve.
  const gateIsOracle =
    o.gate_command.trim() === o.oracle_command.trim() ||
    o.gate_command.includes(o.oracle_command.trim());
  checks.push({
    name: `${label}: gate_command is not just the oracle run directly`,
    pass: !gateIsOracle,
    detail: gateIsOracle ? `FACADE: gate_command == oracle_command (sem rede de regressão real)` : undefined,
  });
  if (gateIsOracle) continue;

  // (1) clean: gate e oráculo saem 0.
  const gateClean = run(o.gate_command);
  const oracleClean = run(o.oracle_command);
  checks.push({
    name: `${label}: clean run (gate=0 and oracle=0)`,
    pass: gateClean === 0 && oracleClean === 0,
    detail: gateClean === 0 && oracleClean === 0 ? undefined : `clean falhou: gate=${gateClean} oracle=${oracleClean}`,
  });
  if (gateClean !== 0 || oracleClean !== 0) continue;

  // (2) mutate a propriedade nomeada → oráculo DEVE quebrar (mutação ataca a propriedade, não proxy).
  run(o.mutate);
  const oracleMutated = run(o.oracle_command);
  // (3) gate DEVE então quebrar → o gate re-roda o oráculo.
  const gateMutated = run(o.gate_command);
  if (o.revert) run(o.revert);

  checks.push({
    name: `${label}: mutation breaks the oracle (named property, not proxy)`,
    pass: oracleMutated !== 0,
    detail: oracleMutated !== 0 ? undefined : `mutate não quebrou o oráculo (proxy?) → exit ainda 0`,
  });
  checks.push({
    name: `${label}: gate re-runs the oracle (gate fails when oracle is broken)`,
    pass: gateMutated !== 0,
    detail: gateMutated !== 0 ? undefined : `FACADE: gate ficou PASS com o oráculo quebrado → não re-roda o oráculo`,
  });

  // (4) controle negativo: decoy que o oráculo ignora; o gate DEVE sair 0 nele.
  run(o.decoy_mutate);
  const gateDecoy = run(o.gate_command);
  if (o.decoy_revert) run(o.decoy_revert);
  checks.push({
    name: `${label}: gate is insensitive to decoy (exit≠0 is attributable to the oracle)`,
    pass: gateDecoy === 0,
    detail: gateDecoy === 0 ? undefined : `falso-positivo de wiring: gate falhou no decoy (exit≠0 não é atribuível ao oráculo)`,
  });
}

runChecks('D3 oracle-wiring-check', checks);
