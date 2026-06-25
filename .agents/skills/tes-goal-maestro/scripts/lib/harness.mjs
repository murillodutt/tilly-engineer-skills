// Runner compartilhado dos harnesses de parede do tes-goal-maestro.
// Padrão de LEITURA: src/data/parse.assert.ts (header + Check{name,pass,detail} + exit≠0).
// Cada harness importa runChecks e devolve uma lista de Check; o exit-code é o oráculo.
//
//   import { runChecks, grepFile } from './lib/harness.mjs'
//
// Falsificável, 3 estados (SPEC-000b — protocolo BLOCKED):
//   exit 0 = todos PASS · exit 1 = algum FAIL · exit 2 = algum BLOCKED-provado (nenhum FAIL).
// BLOCKED é para paredes dep-pesada/não-det cuja dependência (Playwright/Axe/modelo) está
// legitimamente ausente — NUNCA "BLOCKED no texto + exit 0" (isso seria PASS falso = facade).

import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';

/** @typedef {{name: string, pass: boolean, blocked?: boolean, blockedProof?: string, detail?: string}} Check */

/**
 * Roda a lista de checks, imprime um relatório compacto e sai com exit-code de 3 estados.
 * Um check `blocked:true` exige `blockedProof` (a evidência de que a dependência falta).
 * @param {string} title
 * @param {Check[]} checks
 */
export function runChecks(title, checks) {
  let failed = 0;
  let blocked = 0;
  console.log(`# ${title}`);
  for (const c of checks) {
    if (c.blocked) {
      // BLOCKED sem prova é desonesto — vira FAIL, não BLOCKED.
      if (!c.blockedProof) {
        failed++;
        console.log(`  [FAIL] ${c.name} — BLOCKED sem blockedProof (desonesto)`);
        continue;
      }
      blocked++;
      console.log(`  [BLOCKED] ${c.name} — ${c.blockedProof}`);
      continue;
    }
    const mark = c.pass ? 'PASS' : 'FAIL';
    if (!c.pass) failed++;
    console.log(`  [${mark}] ${c.name}${c.detail ? ` — ${c.detail}` : ''}`);
  }
  const passed = checks.length - failed - blocked;
  console.log(`# ${passed} pass, ${failed} fail, ${blocked} blocked`);
  // Prioridade: FAIL domina (exit 1); senão BLOCKED (exit 2); senão tudo PASS (exit 0).
  process.exit(failed > 0 ? 1 : blocked > 0 ? 2 : 0);
}

/** Helper: True se um binário está no PATH (para detecção honesta de dependência ausente). */
export function hasBinary(name) {
  try {
    execFileSync(process.platform === 'win32' ? 'where' : 'which', [name], { stdio: 'pipe' });
    return true;
  } catch {
    return false;
  }
}

/** Lê um arquivo como texto; lança se ausente (a ausência é falha do oráculo, não crash silencioso). */
export function readText(path) {
  return readFileSync(path, 'utf8');
}

/** Conta ocorrências de um regex num texto (global). */
export function countMatches(text, regex) {
  const re = new RegExp(regex.source, regex.flags.includes('g') ? regex.flags : regex.flags + 'g');
  return (text.match(re) || []).length;
}

/** True se o regex casa pelo menos uma vez no arquivo. */
export function grepFile(path, regex) {
  return regex.test(readText(path));
}
