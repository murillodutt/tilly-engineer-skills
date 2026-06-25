// Harness D1 — Re-execução + re-mutação por auditor independente.
// Driver genérico do Executive Stop Audit: para cada oráculo de eixo required,
// (1) re-executa LIMPO e exige PASS (exit 0); (2) injeta uma violação SÓ na
// propriedade nomeada e exige FAIL (exit≠0); (3) reverte. Um oráculo que fica PASS
// sob a mutação da própria propriedade nomeada é facade → exit≠0 → NEEDS_INDEPENDENT_AUDIT.
//
//   node scripts/audit-remutation.mjs <remutation-plan.json>
//
// O plano (escrito pelo auditor, NÃO pelo operador) descreve cada oráculo:
//   {
//     "oracles": [
//       {
//         "axis": "visual-luma",
//         "name": "avgLuma é luminância média do frame",
//         "command": "npx tsx benchmark-001/src/oracles/lumaCheck.ts",
//         "mutate":  "cp fixtures/black.png artifacts/day.png",   // injeta violação na PROPRIEDADE nomeada
//         "revert":  "git checkout -- artifacts/day.png"
//       }
//     ]
//   }
//
// Princípio: o auditor é distinto do operador (este script não escreve oráculos),
// e a mutação ataca a propriedade SEMÂNTICA nomeada (luminância), não um proxy.

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

const planPath = process.argv[2];
if (!planPath) {
  console.error('uso: node scripts/audit-remutation.mjs <remutation-plan.json>');
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

if (oracles.length === 0) {
  // Sem oráculos de eixo required no plano → audit não pode certificar nada → falha.
  checks.push({ name: 'plan has required-axis oracles', pass: false, detail: 'oracles[] vazio' });
  runChecks('D1 audit-remutation', checks);
}

for (const o of oracles) {
  const label = o.axis || o.name || 'oracle';

  // (1) clean run deve PASSAR
  const cleanCode = run(o.command);
  checks.push({
    name: `${label}: clean run passes`,
    pass: cleanCode === 0,
    detail: cleanCode === 0 ? undefined : `exit=${cleanCode} (oráculo não passa no estado limpo)`,
  });
  if (cleanCode !== 0) continue; // sem clean PASS não há o que re-mutar

  // (2) injeta violação na propriedade nomeada → oráculo DEVE falhar
  run(o.mutate);
  const mutatedCode = run(o.command);
  checks.push({
    name: `${label}: fails under re-mutation of named property`,
    pass: mutatedCode !== 0,
    detail: mutatedCode !== 0 ? undefined : `FACADE: ficou PASS após mutar "${o.name}" → exit ainda 0`,
  });

  // (3) reverte sempre
  if (o.revert) run(o.revert);
}

runChecks('D1 audit-remutation', checks);
