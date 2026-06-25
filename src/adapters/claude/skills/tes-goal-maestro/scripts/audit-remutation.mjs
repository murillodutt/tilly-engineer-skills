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
//
// SPEC-004 — PANEL MODE (Adversary Panel, quorum-with-veto):
//   um oráculo pode trazer um painel de refutadores de lentes disjuntas em vez do
//   par mutate/revert único. Cada refutador ataca a propriedade nomeada por uma
//   lente distinta; o painel só credita o oráculo se TODOS os refutadores o quebram
//   (veto: qualquer refutador que deixe o oráculo PASS sob sua própria mutação mata
//   o crédito). Não há maioria — o veto é a regra, herdada de runChecks (FAIL domina).
//
//   {
//     "oracles": [
//       {
//         "axis": "visual-luma",
//         "name": "avgLuma é luminância média do frame",
//         "command": "npx tsx benchmark-001/src/oracles/lumaCheck.ts",
//         "refuters": [
//           { "lens": "structural-proxy", "mutate": "<viola por lente A>", "revert": "<restaura>",
//             "decoy_mutate": "<perturbação que o oráculo IGNORA>", "decoy_revert": "<restaura decoy>" },
//           { "lens": "vacuous-empty",   "mutate": "<viola por lente B>", "revert": "<restaura>" }
//         ]
//       }
//     ]
//   }
//
// refuters ausente → modo single-plan retrocompatível (mutate/revert), idêntico ao original.
// refuters presente → modo painel: 1 check por refutador (rótulo = lens) + 1 check por decoy.

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

  if (Array.isArray(o.refuters)) {
    // ── MODO PAINEL (SPEC-004): quorum-with-veto por lentes disjuntas ──
    // 1 check por refutador (rótulo = lens). VETO vem de graça: qualquer refutador
    // que deixe o oráculo PASS sob sua própria mutação → pass:false → runChecks
    // FAIL-domina → exit 1 → crédito negado. NÃO há maioria.
    if (o.refuters.length === 0) {
      // Painel vazio não credita nada (nunca vacuous-PASS).
      checks.push({ name: `${label}: panel has refuters`, pass: false, detail: 'refuters[] vazio' });
      continue;
    }
    for (let i = 0; i < o.refuters.length; i++) {
      const r = o.refuters[i];
      const lens = r.lens || `refuter#${i}`;

      // (2) o refutador viola a propriedade pela sua lente → oráculo DEVE falhar.
      run(r.mutate);
      const mutatedCode = run(o.command);
      if (r.revert) run(r.revert);
      checks.push({
        name: `${label} [${lens}]: oracle fails under refuter's lens`,
        pass: mutatedCode !== 0,
        detail: mutatedCode !== 0 ? undefined : `FACADE: oráculo ficou PASS sob a lente "${lens}" → exit ainda 0 (veto)`,
      });

      // (2b) controle negativo opcional: o decoy é uma perturbação que o oráculo IGNORA
      // → oráculo DEVE permanecer exit 0 (se cair no decoy, o exit≠0 acima não é atribuível).
      if (r.decoy_mutate) {
        run(r.decoy_mutate);
        const decoyCode = run(o.command);
        if (r.decoy_revert) run(r.decoy_revert);
        checks.push({
          name: `${label} [${lens}]: oracle ignores the decoy (negative control)`,
          pass: decoyCode === 0,
          detail: decoyCode === 0 ? undefined : `oráculo caiu no decoy da lente "${lens}" → exit≠0 não é atribuível à propriedade`,
        });
      }
    }
    continue;
  }

  // ── MODO SINGLE-PLAN (retrocompatível, idêntico ao original) ──
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
