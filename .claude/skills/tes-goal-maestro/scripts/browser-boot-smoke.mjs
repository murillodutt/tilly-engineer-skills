// Harness C3 — Smoke do bundle SERVIDO no runtime-alvo, com console gating.
// Driver: roda o comando de boot do bundle como servido (headless ou import-in-bundle),
// lê o relatório de console e falha (exit≠0 → AXIS_UNPROVEN) se houver qualquer
// consoleError/uncaught na hot path, OU se o boot não rodou no alvo browser real.
//
//   node scripts/browser-boot-smoke.mjs <smoke-report.json>
//
// O relatório é produzido pelo boot concreto do projeto (headless browser / dist-client
// importado). O harness não inventa o boot — ele certifica o resultado.
//
// Formato:
//   {
//     "target": "browser",                 // tem de ser browser real, não node
//     "ran_against": "served-dist-client", // served-dist-client | headless | node-stub(REJEITADO p/ browser)
//     "consoleErrors": [],                 // qualquer entrada → FAIL (gating, não log)
//     "uncaught": [],                      // idem
//     "ticks_advanced": true               // estado avançou na hot path
//   }

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/browser-boot-smoke.mjs <smoke-report.json>');
  process.exit(2);
}

let r;
try {
  r = JSON.parse(readText(path));
} catch (e) {
  console.error(`relatório inválido: ${e.message}`);
  process.exit(2);
}

const checks = [];

// (1) alvo browser não pode ter rodado num node-stub (a brecha C3)
const ranAgainst = r.ran_against || '';
const isNodeStub = /node-stub|node-only|node_process/i.test(ranAgainst);
checks.push({
  name: 'browser target ran against served bundle, not a node stub',
  pass: r.target === 'browser' ? !isNodeStub && ranAgainst.length > 0 : true,
  detail:
    r.target === 'browser' && isNodeStub
      ? `AXIS_UNPROVEN: smoke browser rodou em "${ranAgainst}" (node-stub estuba o boundary)`
      : r.target === 'browser' && !ranAgainst
        ? 'ran_against ausente: não dá para provar que rodou no alvo'
        : undefined,
});

// (2) console gating: qualquer consoleError/uncaught na hot path → FAIL
const consoleErrors = Array.isArray(r.consoleErrors) ? r.consoleErrors : [];
const uncaught = Array.isArray(r.uncaught) ? r.uncaught : [];
checks.push({
  name: 'no consoleError on hot path (gate, not log)',
  pass: consoleErrors.length === 0,
  detail: consoleErrors.length ? `consoleErrors: ${JSON.stringify(consoleErrors)}` : undefined,
});
checks.push({
  name: 'no uncaught exception on hot path',
  pass: uncaught.length === 0,
  detail: uncaught.length ? `uncaught: ${JSON.stringify(uncaught)}` : undefined,
});

// (3) estado avançou (o smoke não é um boot vazio)
checks.push({
  name: 'state advanced across ticks',
  pass: r.ticks_advanced === true,
  detail: r.ticks_advanced === true ? undefined : 'ticks_advanced não comprovado',
});

runChecks('C3 browser-boot-smoke', checks);
