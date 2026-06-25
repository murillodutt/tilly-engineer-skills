// SPEC-012 — Mutation-suite das 7 famílias (12 testes-de-violação do placar).
// Para cada parede, monta uma fixture de VIOLAÇÃO em /tmp, roda o harness-dono e exige
// que ele DISPARE (exit≠0); depois monta a fixture REVERTIDA e exige PASS (exit 0).
// Uma parede só conta como "feita" quando dispara sob violação E passa quando revertida.
// Conduzido por agente independente (D1): este script não escreve nenhum dos harnesses.
//
//   node scripts/validate-walls.mjs
//
// Exit≠0 se QUALQUER parede falhar o par (não-disparo sob violação, ou não-passe ao reverter).

import { execFileSync, execSync } from 'node:child_process';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const tmp = mkdtempSync(join(tmpdir(), 'walls-'));

function runHarness(script, args) {
  try {
    execFileSync('node', [join(here, script), ...args], { stdio: 'pipe' });
    return 0;
  } catch (e) {
    return typeof e.status === 'number' ? e.status : 1;
  }
}

function fixture(name, content) {
  const p = join(tmp, name);
  writeFileSync(p, content);
  return p;
}

// Cada parede: {id, harness, violate→args (deve dar exit≠0), revert→args (deve dar exit 0)}.
const WALLS = [
  // D4 — ledger placeholder
  {
    id: 'D4 ledger-no-placeholder',
    harness: 'ledger-no-placeholder.mjs',
    violate: () => [fixture('d4-bad.md', '| S | x | g | commit: <a seguir> | n |\n')],
    revert: () => [fixture('d4-ok.md', '| S | x | g | commit: abc1234 | n |\n')],
  },
  // D1 — audit re-mutation (facade fica PASS = falha; honesto cai = passa)
  {
    id: 'D1 audit-remutation',
    harness: 'audit-remutation.mjs',
    violate: () => [fixture('d1-facade.json', JSON.stringify({ oracles: [{ axis: 'f', name: 'x', command: 'true', mutate: 'true', revert: 'true' }] }))],
    revert: () => [fixture('d1-honest.json', JSON.stringify({ oracles: [{ axis: 'h', name: 'y', command: `test ! -f ${join(tmp, '__f')}`, mutate: `touch ${join(tmp, '__f')}`, revert: `rm -f ${join(tmp, '__f')}` }] }))],
  },
  // C1 — name↔measure
  {
    id: 'C1 oracle-name-measure',
    harness: 'oracle-name-measure.mjs',
    violate: () => [fixture('c1-facade.json', JSON.stringify({ oracles: [{ name: 'avgLuma', proven_property: 'luminância', measured_quantity: 'statSync(png).size bytes' }] }))],
    revert: () => [fixture('c1-ok.json', JSON.stringify({ oracles: [{ name: 'avgLuma', proven_property: 'luminância', measured_quantity: 'média RGB dos pixels decodificados' }] }))],
  },
  // C2 — topology probe
  {
    id: 'C2 topology-probe',
    harness: 'topology-probe.mjs',
    violate: () => [fixture('c2-over.json', JSON.stringify({ targets: [{ file: join(here, 'validate-walls.mjs'), max: 1 }] }))],
    revert: () => [fixture('c2-ok.json', JSON.stringify({ targets: [{ file: join(here, 'validate-walls.mjs'), max: 100000 }] }))],
  },
  // B1 — runtime import grep
  {
    id: 'B1 runtime-import-grep',
    harness: 'runtime-import-grep.mjs',
    violate: () => [fixture('b1-bad.ts', "import { readFileSync } from 'node:fs';\n")],
    revert: () => [fixture('b1-ok.ts', "import { foo } from './local';\n")],
  },
  // C3 — browser boot smoke
  {
    id: 'C3 browser-boot-smoke',
    harness: 'browser-boot-smoke.mjs',
    violate: () => [fixture('c3-bad.json', JSON.stringify({ target: 'browser', ran_against: 'node-stub', consoleErrors: [], uncaught: [], ticks_advanced: true }))],
    revert: () => [fixture('c3-ok.json', JSON.stringify({ target: 'browser', ran_against: 'served-dist-client', consoleErrors: [], uncaught: [], ticks_advanced: true }))],
  },
  // META — context completeness
  {
    id: 'META context-completeness',
    harness: 'context-completeness.mjs',
    violate: () => [fixture('m-bad.json', JSON.stringify({ axes: [{ id: 'r', oracle_runner_contract: 'x', regression_target: 'ci' }] }))],
    revert: () => [fixture('m-ok.json', JSON.stringify({ axes: [{ id: 'r', runtime_target: 'browser', oracle_runner_contract: 'x', regression_target: 'ci' }] }))],
  },
  // C4 — scene non-degenerate (precisa de PNG; gerado abaixo)
  {
    id: 'C4 scene-non-degenerate',
    harness: 'scene-non-degenerate.mjs',
    violate: () => [makePng('c4-flat.png', () => [140, 100, 60])],
    revert: () => [makePng('c4-rich.png', (x, y) => [(x * 4) & 255, (y * 4) & 255, ((x + y) * 2) & 255])],
  },
  // D2 — claim↔artifact coherence
  {
    id: 'D2 claim-artifact-coherence',
    harness: 'claim-artifact-coherence.mjs',
    violate: () => [fixture('d2-bad.json', JSON.stringify({ claims: { backend: 'WebGPU' }, artifact: { backend: 'webgl2' }, fieldMap: { backend: 'backend' } }))],
    revert: () => [fixture('d2-ok.json', JSON.stringify({ claims: { backend: 'webgl2' }, artifact: { backend: 'webgl2' }, fieldMap: { backend: 'backend' } }))],
  },
  // D3 — oracle wiring por RE-MUTAÇÃO DO GATE (gate WIRED re-roda o oráculo; FACADE não)
  {
    id: 'D3 oracle-wiring-check',
    harness: 'oracle-wiring-check.mjs',
    // FACADE: gate_command 'true' nunca re-roda o oráculo → fica 0 mesmo com o oráculo quebrado → exit 1.
    violate: () => [fixture('d3-bad.json', JSON.stringify({ oracles: [{
      axis: 'f', regression_target: '.ci/fake',
      gate_command: 'true',
      oracle_command: `test ! -f ${join(tmp, '__d3f')}`,
      mutate: `touch ${join(tmp, '__d3f')}`, revert: `rm -f ${join(tmp, '__d3f')}`,
      decoy_mutate: `touch ${join(tmp, '__d3fd')}`, decoy_revert: `rm -f ${join(tmp, '__d3fd')}`,
    }] }))],
    // WIRED: gate envolve o oráculo via wrapper distinto (não-substring), insensível ao decoy → exit 0.
    revert: () => [fixture('d3-ok.json', JSON.stringify({ oracles: [{
      axis: 'h', regression_target: '.ci/real',
      gate_command: `sh -c '[ ! -e ${join(tmp, '__d3h')} ]'`,
      oracle_command: `test ! -f ${join(tmp, '__d3h')}`,
      mutate: `touch ${join(tmp, '__d3h')}`, revert: `rm -f ${join(tmp, '__d3h')}`,
      decoy_mutate: `touch ${join(tmp, '__d3hd')}`, decoy_revert: `rm -f ${join(tmp, '__d3hd')}`,
    }] }))],
  },
  // A1 — anchor rehash
  {
    id: 'A1 anchor-rehash',
    harness: 'anchor-rehash.mjs',
    violate: () => [join(here, 'validate-walls.mjs'), 'deadbeefdeadbeef'],
    revert: () => [join(here, 'validate-walls.mjs'), gitHash(join(here, 'validate-walls.mjs'))],
  },
  // META-PANEL — SPEC-004: o painel REJEITA diversidade vacuosa (refutadores-clone).
  // violate: refutadores com lens diferentes mas CORPOS idênticos → panel-diversity DEVE falhar (exit 1).
  // revert: refutadores com corpos distintos → exit 0.
  {
    id: 'META panel-diversity',
    harness: 'panel-diversity.mjs',
    violate: () => [fixture('mp-clones.json', JSON.stringify({ oracles: [{ axis: 'p', command: 'true', refuters: [
      { lens: 'a', mutate: 'X', revert: 'Y', decoy_mutate: 'Z' },
      { lens: 'b', mutate: 'X', revert: 'Y', decoy_mutate: 'Z' },
    ] }] }))],
    revert: () => [fixture('mp-distinct.json', JSON.stringify({ oracles: [{ axis: 'p', command: 'true', refuters: [
      { lens: 'a', mutate: 'X1', revert: 'Y1', decoy_mutate: 'Z1' },
      { lens: 'b', mutate: 'X2', revert: 'Y2', decoy_mutate: 'Z2' },
    ] }] }))],
  },
  // B2 — api lint evidence (textual: provado por grep no skill, não harness; verificado no closeout)

  // ─── DOMAIN WALLS (SPEC-003..018) — node-puro {violate,revert}; dep-pesada/não-det +blocked (exit 2) ───
  // Database
  { id: 'DB1 migration-reversible', harness: 'db-migration-reversible.mjs',
    violate: () => [fixture('db1b.json', JSON.stringify({ initial: { users: [{ id: 1 }] }, migrations: [{ id: 'm', up: { add_field: { table: 'users', field: 'e', default: null } } }] }))],
    revert: () => [fixture('db1g.json', JSON.stringify({ initial: { users: [{ id: 1 }] }, migrations: [{ id: 'm', up: { add_field: { table: 'users', field: 'e', default: null } }, down: { drop_field: { table: 'users', field: 'e' } } }] }))] },
  { id: 'DB2 tx-idempotency', harness: 'tx-idempotency.mjs',
    violate: () => [fixture('db2b.json', JSON.stringify({ initial: { rows: [] }, ops: [{ id: 'o', op: { delete: {} } }] }))],
    revert: () => [fixture('db2g.json', JSON.stringify({ initial: { rows: [] }, ops: [{ id: 'o', op: { insert: { table: 'rows', key: 'id', value: { id: 1 } } } }] }))] },
  { id: 'DB3 referential-integrity', harness: 'referential-integrity.mjs',
    violate: () => [fixture('db3b.json', JSON.stringify({ tables: { users: [{ id: 1 }], orders: [{ id: 9, user_id: 99 }] }, fks: [{ table: 'orders', field: 'user_id', references: 'users', ref_field: 'id' }] }))],
    revert: () => [fixture('db3g.json', JSON.stringify({ tables: { users: [{ id: 1 }], orders: [{ id: 9, user_id: 1 }] }, fks: [{ table: 'orders', field: 'user_id', references: 'users', ref_field: 'id' }] }))] },
  { id: 'DB4 batch-reconcile', harness: 'batch-reconcile.mjs',
    violate: () => [fixture('db4b.json', JSON.stringify({ input_count: 1000, output_count: 950, skipped: [] }))],
    revert: () => [fixture('db4g.json', JSON.stringify({ input_count: 1000, output_count: 950, skipped: [{ reason: 'timeout', count: 50 }] }))] },
  // Financeiro
  { id: 'FIN1 double-entry', harness: 'ledger-double-entry.mjs',
    violate: () => [fixture('f1b.json', JSON.stringify({ entries: [{ tx: 't', account: 'c', debit: 100, credit: 0, status: 'COMMITTED' }] }))],
    revert: () => [fixture('f1g.json', JSON.stringify({ entries: [{ tx: 't', account: 'c', debit: 100, credit: 0, status: 'COMMITTED' }, { tx: 't', account: 'r', debit: 0, credit: 100, status: 'COMMITTED' }] }))] },
  { id: 'FIN2 payment-idempotency', harness: 'payment-idempotency.mjs',
    violate: () => [fixture('f2b.json', JSON.stringify({ charges: [{ idempotency_key: 'k', charge_id: 'a' }, { idempotency_key: 'k', charge_id: 'b' }] }))],
    revert: () => [fixture('f2g.json', JSON.stringify({ charges: [{ idempotency_key: 'k', charge_id: 'a' }, { idempotency_key: 'k', charge_id: 'a' }] }))] },
  { id: 'FIN3 decimal-precision', harness: 'decimal-precision.mjs',
    violate: () => [fixture('f3b.ts', 'const t = parseFloat(amount);\n')],
    revert: () => [fixture('f3g.ts', 'const t = Decimal(amountCents);\n')] },
  { id: 'FIN4 audit-trail-immutable', harness: 'audit-trail-immutable.mjs',
    violate: () => [fixture('f4b.json', JSON.stringify({ operations: [{ type: 'DELETE', table: 'audit_log' }], txs: ['t'], trail_txs: ['t'] }))],
    revert: () => [fixture('f4g.json', JSON.stringify({ operations: [{ type: 'INSERT', table: 'audit_log' }], txs: ['t'], trail_txs: ['t'] }))] },
  // LLM
  { id: 'LLM1 eval-coverage', harness: 'eval-coverage.mjs',
    violate: () => [fixture('l1b.json', JSON.stringify({ prompts: ['p'], evals: [] }))],
    revert: () => [fixture('l1g.json', JSON.stringify({ prompts: ['p'], evals: [{ prompt: 'p', expected: 'x' }] }))] },
  { id: 'LLM2 token-budget', harness: 'token-budget.mjs',
    violate: () => [fixture('l2b.json', JSON.stringify({ budget: 50000, samples: [{ id: 'r', prompt_tokens: 40000, completion_tokens: 15000 }] }))],
    revert: () => [fixture('l2g.json', JSON.stringify({ budget: 50000, samples: [{ id: 'r', prompt_tokens: 1200, completion_tokens: 800 }] }))] },
  { id: 'LLM3 tool-reachability', harness: 'tool-reachability.mjs',
    violate: () => [fixture('l3b.json', JSON.stringify({ tools: ['t'], eval_traces: [] }))],
    revert: () => [fixture('l3g.json', JSON.stringify({ tools: ['t'], eval_traces: [{ case: 'c', tool_calls: ['t'] }] }))] },
  { id: 'LLM4 rag-relevance', harness: 'rag-relevance.mjs', klass: 'non-det',
    violate: () => [fixture('l4b.json', JSON.stringify({ floor: 0.7, frozen_scores: [{ query: 'q', top1_score: 0.62 }] }))],
    revert: () => [fixture('l4g.json', JSON.stringify({ floor: 0.7, frozen_scores: [{ query: 'q', top1_score: 0.82 }] }))],
    blocked: () => [fixture('l4k.json', JSON.stringify({ floor: 0.7, frozen_scores: [] }))] },
  // UX
  { id: 'UX3 i18n-coverage', harness: 'i18n-coverage.mjs',
    violate: () => [fixture('u3b.json', JSON.stringify({ fallback: 'pt', floor: 0.9, keys: ['a', 'b'], translations: { pt: { a: 'A' } } }))],
    revert: () => [fixture('u3g.json', JSON.stringify({ fallback: 'pt', floor: 0.9, keys: ['a', 'b'], translations: { pt: { a: 'A', b: 'B' } } }))] },
  { id: 'UX1 responsive-check', harness: 'responsive-check.mjs', klass: 'dep-heavy',
    violate: () => [fixture('u1b.json', JSON.stringify({ playwright_available: true, viewports: [{ width: 375, overflow: true }, { width: 768, overflow: false }, { width: 1440, overflow: false }] }))],
    revert: () => [fixture('u1g.json', JSON.stringify({ playwright_available: true, viewports: [{ width: 375, overflow: false }, { width: 768, overflow: false }, { width: 1440, overflow: false }] }))],
    blocked: () => [fixture('u1k.json', JSON.stringify({ playwright_available: false }))] },
  { id: 'UX2 a11y-audit', harness: 'a11y-audit.mjs', klass: 'dep-heavy',
    violate: () => [fixture('u2b.json', JSON.stringify({ axe_available: true, violations: [{ id: 'color-contrast' }] }))],
    revert: () => [fixture('u2g.json', JSON.stringify({ axe_available: true, violations: [] }))],
    blocked: () => [fixture('u2k.json', JSON.stringify({ axe_available: false }))] },
  { id: 'UX4 web-vitals', harness: 'web-vitals.mjs', klass: 'dep-heavy',
    violate: () => [fixture('u4b.json', JSON.stringify({ lighthouse_available: true, lcp_s: 3.5, cls: 0.05, inp_ms: 150 }))],
    revert: () => [fixture('u4g.json', JSON.stringify({ lighthouse_available: true, lcp_s: 2.1, cls: 0.05, inp_ms: 150 }))],
    blocked: () => [fixture('u4k.json', JSON.stringify({ lighthouse_available: false }))] },
];

function gitHash(path) {
  return execSync(`git hash-object "${path}"`, { stdio: 'pipe' }).toString().trim();
}

// Gerador de PNG mínimo (RGB 8-bit) para o C4.
import { deflateSync } from 'node:zlib';
function crc32(buf) { let c = ~0; for (let i = 0; i < buf.length; i++) { c ^= buf[i]; for (let k = 0; k < 8; k++) c = (c >>> 1) ^ (0xEDB88320 & -(c & 1)); } return ~c >>> 0; }
function pngChunk(type, data) { const t = Buffer.from(type, 'ascii'); const len = Buffer.alloc(4); len.writeUInt32BE(data.length); const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(Buffer.concat([t, data]))); return Buffer.concat([len, t, data, crc]); }
function makePng(name, fill) {
  const w = 32, h = 32;
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4); ihdr[8] = 8; ihdr[9] = 2;
  const stride = w * 3; const raw = Buffer.alloc(h * (stride + 1));
  for (let y = 0; y < h; y++) { raw[y * (stride + 1)] = 0; for (let x = 0; x < w; x++) { const o = y * (stride + 1) + 1 + x * 3; const [r, g, b] = fill(x, y); raw[o] = r; raw[o + 1] = g; raw[o + 2] = b; } }
  const png = Buffer.concat([sig, pngChunk('IHDR', ihdr), pngChunk('IDAT', deflateSync(raw)), pngChunk('IEND', Buffer.alloc(0))]);
  const p = join(tmp, name); writeFileSync(p, png); return p;
}

// Paredes de domínio cujo input é JSON (testáveis contra `{}` degenerado). As que recebem
// um path de source (.ts/.js para grep) ficam fora — têm seu próprio teste de presença.
const JSON_INPUT_WALLS = new Set([
  'db-migration-reversible.mjs', 'tx-idempotency.mjs', 'referential-integrity.mjs', 'batch-reconcile.mjs',
  'ledger-double-entry.mjs', 'payment-idempotency.mjs', 'audit-trail-immutable.mjs',
  'eval-coverage.mjs', 'token-budget.mjs', 'tool-reachability.mjs',
  'i18n-coverage.mjs',
]);

let failed = 0;
console.log('# mutation-suite — paredes executáveis (base + domínio). B2 textual no closeout.');
console.log('# node-puro: violação(≠0)+reverte(0). dep-pesada/não-det: também blocked(=2).\n');
for (const w of WALLS) {
  const vCode = runHarness(w.harness, w.violate());
  const rCode = runHarness(w.harness, w.revert());
  const fires = vCode === 1; // violação deve dar FAIL (1), não BLOCKED (2)
  const reverts = rCode === 0;
  let ok = fires && reverts;
  let blkNote = '';
  if (w.blocked) {
    const bCode = runHarness(w.harness, w.blocked());
    const blocksHonestly = bCode === 2; // BLOCKED-provado = exit 2 (não 0=PASS-falso, não 1=quebrado)
    // Ataque do Executive Stop Audit: dependência OMITIDA (não explicitamente false) também
    // deve BLOCKED (exit 2), nunca PASS-por-omissão. Prova: fixture vazio {} → exit 2.
    const iCode = runHarness(w.harness, [fixture(`${w.id.split(' ')[0]}-implicit.json`, '{}')]);
    const blocksOnOmission = iCode === 2;
    ok = ok && blocksHonestly && blocksOnOmission;
    blkNote = ` blocked:exit${bCode}${blocksHonestly ? '✓' : '✗(devia=2)'} omit:exit${iCode}${blocksOnOmission ? '✓' : '✗(devia=2,PASS-por-omissão!)'}`;
  } else if (JSON_INPUT_WALLS.has(w.harness)) {
    // Defesa universal (revisão profunda): paredes de domínio que recebem JSON devem REJEITAR
    // input degenerado `{}` (exit≠0), nunca vacuous-PASS. Pega .every()/.filter() em vazio,
    // campo-ausente-como-zero. Harnesses que recebem um path de SOURCE (.ts/.js grep) ficam fora —
    // `{}` não é o vetor de ataque deles (eles têm seu próprio teste de presença).
    const dCode = runHarness(w.harness, [fixture(`${w.id.split(' ')[0]}-degen.json`, '{}')]);
    const rejectsDegenerate = dCode !== 0;
    ok = ok && rejectsDegenerate;
    blkNote = ` degen:exit${dCode}${rejectsDegenerate ? '✓' : '✗(devia≠0,vacuous-PASS!)'}`;
  }
  if (!ok) failed++;
  console.log(`  [${ok ? 'PASS' : 'FAIL'}] ${w.id} — viol:exit${vCode}${fires ? '✓' : '✗(devia=1)'} rev:exit${rCode}${reverts ? '✓' : '✗(devia=0)'}${blkNote}`);
}
console.log(`\n# ${WALLS.length - failed}/${WALLS.length} paredes convergem (dispara+reverte; dep/não-det também bloqueia-honestamente)`);
process.exit(failed === 0 ? 0 : 1);
