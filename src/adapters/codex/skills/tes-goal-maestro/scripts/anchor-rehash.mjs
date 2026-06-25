// Harness A1 — Âncora recomputada (anti auto-declaração de proveniência).
// Recomputa git hash-object do anchor_path e compara byte-a-byte com o ANCHOR_HASH
// declarado; também reusa o PADRÃO de isolationCheck.ts (SEM importá-lo): o anchor_path
// não pode resolver para um benchmark-*/ distinto da run corrente (contaminação ADR-010).
// Divergência / path inexistente / benchmark cruzado → exit≠0 → NEEDS_ANCHOR_ARTIFACT.
//
//   node scripts/anchor-rehash.mjs <anchor_path> <declared_hash> [current_benchmark]
//
// current_benchmark default: derivado do anchor_path se for benchmark-*; senão "none".

import { execSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { runChecks } from './lib/harness.mjs';

const anchorPath = process.argv[2];
const declaredHash = process.argv[3];
const currentBenchmark = process.argv[4] || null;

if (!anchorPath || !declaredHash) {
  console.error('uso: node scripts/anchor-rehash.mjs <anchor_path> <declared_hash> [current_benchmark]');
  process.exit(2);
}

const checks = [];

// (1) o path existe
const exists = existsSync(anchorPath);
checks.push({
  name: `anchor_path exists: ${anchorPath}`,
  pass: exists,
  detail: exists ? undefined : 'NEEDS_ANCHOR_ARTIFACT: path inexistente',
});

// (2) hash recomputado bate byte-a-byte
if (exists) {
  let actual = '';
  try {
    actual = execSync(`git hash-object "${anchorPath}"`, { stdio: 'pipe' }).toString().trim();
  } catch (e) {
    actual = `<erro: ${e.message}>`;
  }
  checks.push({
    name: 'recomputed git hash-object matches declared ANCHOR_HASH',
    pass: actual === declaredHash,
    detail: actual === declaredHash ? undefined : `NEEDS_ANCHOR_ARTIFACT: recomputed=${actual} ≠ declared=${declaredHash}`,
  });
}

// (3) padrão isolationCheck: anchor não cai num benchmark-*/ distinto da run corrente
const anchorBenchmark = (() => {
  const m = /benchmark-\d+/.exec(anchorPath);
  return m ? m[0] : null;
})();
if (anchorBenchmark) {
  // se sabemos a run corrente, o anchor não pode citar OUTRO benchmark
  const crossed = currentBenchmark != null && anchorBenchmark !== currentBenchmark;
  checks.push({
    name: 'anchor does not cite a foreign benchmark-*/ (ADR-010 isolation)',
    pass: !crossed,
    detail: crossed ? `NEEDS_ANCHOR_ARTIFACT: anchor cita ${anchorBenchmark}, run corrente é ${currentBenchmark}` : undefined,
  });
}

runChecks('A1 anchor-rehash', checks);
