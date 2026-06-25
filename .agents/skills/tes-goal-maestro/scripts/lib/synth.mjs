// SPEC-001 (ADR 0006, Axis 1) — Oracle Synthesis: módulo importável, SEM exit no topo.
// Promove os geradores hoje PRESOS no self-test (makePng :197, family→mutation map
// :36-187 do validate-walls.mjs) e INVERTE o discriminador do oracle-name-measure.mjs
// (STRUCTURAL_PROXY :21, NAMED_STRUCTURAL :24) para um serviço chamável.
//
// REGRA CENTRAL (ADR 0006): o harness GERA a prova da propriedade nomeada e a submete
// ao SEU PRÓPRIO falsificador autor-agnóstico antes de admiti-la. Uma medida que é proxy
// estrutural para uma propriedade semântica é facade — mesmo que o harness a tenha escrito.
//
//   import { synthMeasure, synthMutation, synthFixture } from './lib/synth.mjs'
//
// O juiz da auto-validação é o EXISTENTE oracle-name-measure.mjs (shell-out), não uma
// cópia da regra — assim o gerador passa pelo MESMO juiz independente que o operador.

import { execFileSync } from 'node:child_process';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { deflateSync } from 'node:zlib';

const here = dirname(fileURLToPath(import.meta.url));        // .../scripts/lib
const scripts = dirname(here);                              // .../scripts
const nameMeasure = join(scripts, 'oracle-name-measure.mjs');

// ─── Mapa família → MEASURED_QUANTITY honesta (complemento do STRUCTURAL_PROXY) ───
// Cada medida é uma frase decode/count/compute, NUNCA statSync/size/bytes/mtime/path.
// As chaves cobrem PT/EN da propriedade nomeada das 5 famílias conhecidas.
const FAMILY_MEASURE = [
  { family: 'luminance', match: /lumin[âa]ncia|luminance|luma|brilho|brightness/i,
    measured_quantity: 'média RGB dos pixels decodificados do frame' },
  { family: 'distinct-cell-count', match: /c[ée]lulas? distintas|distinct[- ]?cells?|c[óo]digos distintos|distinct[- ]?colors?|cores distintas/i,
    measured_quantity: 'contagem de células distintas decodificadas da grade' },
  { family: 'frame-rate', match: /frame[- ]?rate|fps|quadros por segundo|taxa de quadros/i,
    measured_quantity: 'quadros renderizados contados por segundo de execução' },
  { family: 'double-entry', match: /double[- ]?entry|partida dobrada|d[ée]bito.*cr[ée]dito|debit.*credit/i,
    measured_quantity: 'soma de débitos menos créditos computada por transação' },
  { family: 'referential-integrity', match: /referential[- ]?integrity|integridade referencial|foreign[- ]?key|chave estrangeira|fk\b/i,
    measured_quantity: 'contagem de chaves estrangeiras órfãs computada contra a tabela referenciada' },
];

// Fallback genérico para QUALQUER propriedade semântica fora das 5 famílias: propõe uma
// frase decode/count/compute honesta (nunca um proxy). Se nem assim passa o juiz, honest=false.
function genericHonestMeasure(provenProperty) {
  return `valor de "${provenProperty}" computado/decodificado do artefato de runtime e contado`;
}

// Mesma estrutura do oracle-name-measure.mjs:24 — propriedade EXPLICITAMENTE estrutural.
const NAMED_STRUCTURAL = /(file ?size|tamanho (do )?arquivo|byte count|contagem de bytes|mtime|timestamp|path exist|caminho existe)/i;
// Medida estrutural honesta quando a própria propriedade promete o metadado.
const STRUCTURAL_MEASURE = 'statSync(path).size em bytes do próprio arquivo nomeado';

// Shell-out ao juiz EXISTENTE: retorna true se {name,proven,measured} passa (exit 0).
function passesNameMeasureJudge(name, provenProperty, measured) {
  const dir = mkdtempSync(join(tmpdir(), 'synth-'));
  const p = join(dir, 'decl.json');
  writeFileSync(p, JSON.stringify({ oracles: [{ name, proven_property: provenProperty, measured_quantity: measured }] }));
  try {
    execFileSync('node', [nameMeasure, p], { stdio: 'pipe' });
    return true; // exit 0
  } catch {
    return false; // exit≠0 → o juiz diz facade
  }
}

/**
 * synthMeasure(provenProperty) — PROPÕE uma MEASURED_QUANTITY honesta para a propriedade
 * nomeada e a auto-valida pelo juiz EXISTENTE (oracle-name-measure.mjs) antes de retornar.
 * @param {string} provenProperty
 * @returns {{ measured_quantity: string, honest: boolean, family: string|null }}
 */
export function synthMeasure(provenProperty) {
  const proven = String(provenProperty || '');
  const name = 'synthOracle';

  // (1) Propriedade EXPLICITAMENTE estrutural: o único caso honesto de medir metadados.
  if (NAMED_STRUCTURAL.test(proven)) {
    const honest = passesNameMeasureJudge(name, proven, STRUCTURAL_MEASURE);
    return { measured_quantity: STRUCTURAL_MEASURE, honest, family: 'structural' };
  }

  // (2) Família conhecida → medida canônica; auto-valida pelo juiz.
  for (const fam of FAMILY_MEASURE) {
    if (fam.match.test(proven)) {
      const honest = passesNameMeasureJudge(name, proven, fam.measured_quantity);
      // Se (improvável) o juiz reprovar a própria medida de família, NÃO inventa proxy.
      return { measured_quantity: fam.measured_quantity, honest, family: fam.family };
    }
  }

  // (3) Semântica fora das famílias → fallback genérico honesto; auto-valida.
  const generic = genericHonestMeasure(proven);
  const honest = passesNameMeasureJudge(name, proven, generic);
  // Se o juiz reprovar o fallback (não deveria, é decode/count), degrada honestamente.
  return { measured_quantity: honest ? generic : '', honest, family: honest ? 'generic' : null };
}

// ─── Mapa família → mutação canônica (extraído do WALLS de validate-walls.mjs:36-187) ───
// Usa o padrão de fixture temp-file do D1 honesto (validate-walls.mjs:49): test ! -f / touch / rm.
// `mutate` injeta a violação da propriedade nomeada; `decoy_*` é uma perturbação NÃO-relacionada
// que o oráculo deve IGNORAR (controle de atribuição, como o decoy do D3 :131-139).
function tmpToken(family) {
  const dir = mkdtempSync(join(tmpdir(), `synthmut-${family}-`));
  return {
    target: join(dir, '__violation'),
    decoy: join(dir, '__decoy'),
  };
}

/**
 * synthMutation(family) — devolve comandos shell {mutate, revert, decoy_mutate, decoy_revert}
 * que disparam o oráculo de uma família sob mutação da propriedade nomeada e ignoram o decoy.
 * @param {string} family
 * @returns {{ mutate: string, revert: string, decoy_mutate: string, decoy_revert: string }|null}
 */
export function synthMutation(family) {
  // Famílias file-content / temp-file (o caminho canônico do D1 honesto).
  const known = new Set([
    'ledger-placeholder', 'name-measure',
    'luminance', 'distinct-cell-count', 'frame-rate',
    'double-entry', 'referential-integrity',
  ]);
  if (!known.has(family)) return null;

  const t = tmpToken(family);
  // O oráculo sintetizado para a família é `test ! -f <target>` (PASS quando limpo);
  // mutate injeta o arquivo (viola a propriedade nomeada → FAIL); decoy toca um arquivo
  // NÃO observado pelo oráculo (o oráculo continua passando → atribuição correta).
  // gate_command ENVOLVE o oráculo num idioma DISTINTO (não-substring), espelhando o
  // fixture D3 honesto (validate-walls.mjs:115-116): `[ ! -e <path> ]` ≠ `test ! -f <path>`
  // semanticamente equivalente, mas não é substring → escapa do anti "oráculo-como-gate".
  return {
    mutate: `touch ${t.target}`,
    revert: `rm -f ${t.target}`,
    decoy_mutate: `touch ${t.decoy}`,
    decoy_revert: `rm -f ${t.decoy}`,
    // O comando-oráculo canônico desta família (exposto para o plano de re-mutação).
    oracle_command: `test ! -f ${t.target}`,
    // O gate persistente que RE-RODA o oráculo num wrapper distinto (não-substring).
    gate_command: `sh -c '[ ! -e ${t.target} ]'`,
    target: t.target,
  };
}

// ─── Gerador de PNG mínimo (cópia self-contained do makePng de validate-walls.mjs:197) ───
// sig + IHDR + IDAT(deflateSync) + IEND. O decoder honesto vive em lib/png.mjs.
function crc32(buf) { let c = ~0; for (let i = 0; i < buf.length; i++) { c ^= buf[i]; for (let k = 0; k < 8; k++) c = (c >>> 1) ^ (0xEDB88320 & -(c & 1)); } return ~c >>> 0; }
function pngChunk(type, data) { const t = Buffer.from(type, 'ascii'); const len = Buffer.alloc(4); len.writeUInt32BE(data.length); const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(Buffer.concat([t, data]))); return Buffer.concat([len, t, data, crc]); }
function makePng(p, fill) {
  const w = 32, h = 32;
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4); ihdr[8] = 8; ihdr[9] = 2;
  const stride = w * 3; const raw = Buffer.alloc(h * (stride + 1));
  for (let y = 0; y < h; y++) { raw[y * (stride + 1)] = 0; for (let x = 0; x < w; x++) { const o = y * (stride + 1) + 1 + x * 3; const [r, g, b] = fill(x, y); raw[o] = r; raw[o + 1] = g; raw[o + 2] = b; } }
  const png = Buffer.concat([sig, pngChunk('IHDR', ihdr), pngChunk('IDAT', deflateSync(raw)), pngChunk('IEND', Buffer.alloc(0))]);
  writeFileSync(p, png);
  return p;
}

/**
 * synthFixture(family, dir) — gera o par {violatePath, revertPath} de uma família.
 * Scene/luminance: PNG chapado (viola) vs PNG rico (reverte), via makePng (validate-walls.mjs:90-91).
 * json-input: o JSON violador vs o JSON honesto.
 * @param {string} family
 * @param {string} dir  diretório onde escrever as fixtures
 * @returns {{ violatePath: string, revertPath: string }|null}
 */
export function synthFixture(family, dir) {
  const writeJson = (name, obj) => { const p = join(dir, name); writeFileSync(p, JSON.stringify(obj)); return p; };

  switch (family) {
    case 'luminance':
    case 'distinct-cell-count':
    case 'frame-rate': // famílias de cena visual: degenerada (chapada) vs rica
      return {
        violatePath: makePng(join(dir, `${family}-flat.png`), () => [140, 100, 60]),
        revertPath: makePng(join(dir, `${family}-rich.png`), (x, y) => [(x * 4) & 255, (y * 4) & 255, ((x + y) * 2) & 255]),
      };
    case 'double-entry':
      return {
        violatePath: writeJson('de-bad.json', { entries: [{ tx: 't', account: 'c', debit: 100, credit: 0, status: 'COMMITTED' }] }),
        revertPath: writeJson('de-ok.json', { entries: [{ tx: 't', account: 'c', debit: 100, credit: 0, status: 'COMMITTED' }, { tx: 't', account: 'r', debit: 0, credit: 100, status: 'COMMITTED' }] }),
      };
    case 'referential-integrity':
      return {
        violatePath: writeJson('ri-bad.json', { tables: { users: [{ id: 1 }], orders: [{ id: 9, user_id: 99 }] }, fks: [{ table: 'orders', field: 'user_id', references: 'users', ref_field: 'id' }] }),
        revertPath: writeJson('ri-ok.json', { tables: { users: [{ id: 1 }], orders: [{ id: 9, user_id: 1 }] }, fks: [{ table: 'orders', field: 'user_id', references: 'users', ref_field: 'id' }] }),
      };
    default:
      return null;
  }
}
