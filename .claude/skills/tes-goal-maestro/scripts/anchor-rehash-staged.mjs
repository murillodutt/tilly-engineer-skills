// Harness A1-staged — wrapper de roteamento do anchor-rehash para gates persistentes.
// Recebe ledgers staged como argumentos, descobre o anchor (path + hash declarado) da
// linha `Anchor:` de CADA ledger, e recomputa git hash-object byte-a-byte — movendo o
// defeito "proveniência auto-atestada" do audit-final para o commit-time.
//
//   node scripts/anchor-rehash-staged.mjs <ledger-1.md> [ledger-2.md ...]
//
// Ponteiro DECLARADO, zero canal novo: o hash já vive na linha `Anchor:` do ledger
// (forma "Anchor: <path> (... git hash-object <40-hex> ...)"). O wrapper não inventa
// um canal — lê o que o ledger já declara. Um ledger sem linha `Anchor:` parseável é
// BLOCKED-provado (não há âncora a verificar), nunca PASS falso.

import { execSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { runChecks, readText } from './lib/harness.mjs';

const ledgers = process.argv.slice(2);
const checks = [];

if (ledgers.length === 0) {
  // Sem ledger staged → o gate não foi roteado corretamente; nada a certificar = falha.
  checks.push({ name: 'staged ledger present', pass: false, detail: 'nenhum ledger passado ao wrapper' });
  runChecks('A1-staged anchor-rehash', checks);
}

const ANCHOR_RE = /^Anchor:\s*(\S+).*?\b([0-9a-f]{40})\b/im;

for (const ledger of ledgers) {
  const label = ledger.split('/').pop();
  if (!existsSync(ledger)) {
    checks.push({ name: `${label}: ledger exists`, pass: false, detail: `path inexistente: ${ledger}` });
    continue;
  }
  const text = readText(ledger);
  const m = ANCHOR_RE.exec(text);
  if (!m) {
    // Ledger sem linha Anchor: com hash → BLOCKED-provado (não há âncora declarada a
    // recomputar), nunca PASS silencioso.
    checks.push({
      name: `${label}: declares an Anchor: line with a 40-hex hash`,
      pass: false,
      blocked: true,
      blockedProof: `nenhuma linha "Anchor: <path> ... <40-hex>" encontrada em ${label}`,
    });
    continue;
  }
  const [, anchorPath, declaredHash] = m;
  if (!existsSync(anchorPath)) {
    checks.push({ name: `${label}: anchor_path exists (${anchorPath})`, pass: false, detail: 'NEEDS_ANCHOR_ARTIFACT: path do anchor inexistente' });
    continue;
  }
  let actual = '';
  try {
    actual = execSync(`git hash-object "${anchorPath}"`, { stdio: 'pipe' }).toString().trim();
  } catch (e) {
    actual = `<erro: ${e.message}>`;
  }
  checks.push({
    name: `${label}: recomputed git hash-object matches the Anchor: hash`,
    pass: actual === declaredHash,
    detail: actual === declaredHash ? undefined : `NEEDS_ANCHOR_ARTIFACT: recomputed=${actual} ≠ declared=${declaredHash}`,
  });
}

runChecks('A1-staged anchor-rehash', checks);
