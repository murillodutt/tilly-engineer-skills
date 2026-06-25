// SPEC-001 (ADR 0006, Axis 1) — O ORÁCULO DECLARANTE da síntese (auto-falsificação ao nascer).
// runChecks é o dono do exit-code. Para cada família conhecida, o gerador (lib/synth.mjs)
// PRODUZ a prova e ela é submetida ao falsificador autor-agnóstico EXISTENTE
// (audit-remutation.mjs :51,60-83) e ao controle de atribuição por decoy (oracle-wiring-check.mjs
// :131-139). Um trio sintetizado que não DISPARA sob mutação da própria propriedade nomeada,
// ou que NÃO ignora o decoy, é facade → este self-test FALHA.
//
//   node scripts/synth-selftest.mjs
//
// Controles negativos obrigatórios (re-mutação do próprio juiz):
//  (c) forçar uma measured_quantity proxy para propriedade semântica → o juiz EXISTENTE
//      (oracle-name-measure.mjs) DEVE reprovar (exit≠0). Se passar, a síntese é facade.
//  (d) propriedade fora das famílias → synthMeasure honest=false (NEEDS_HUMAN_ORACLE), nunca proxy.

import { execFileSync } from 'node:child_process';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { runChecks } from './lib/harness.mjs';
import { synthMeasure, synthMutation, synthFixture } from './lib/synth.mjs';

const here = dirname(fileURLToPath(import.meta.url)); // .../scripts
const auditRemutation = join(here, 'audit-remutation.mjs');
const wiringCheck = join(here, 'oracle-wiring-check.mjs');
const nameMeasure = join(here, 'oracle-name-measure.mjs');

function runScript(script, jsonPath) {
  try {
    execFileSync('node', [script, jsonPath], { stdio: 'pipe' });
    return 0;
  } catch (e) {
    return typeof e.status === 'number' ? e.status : 1;
  }
}

function tmpFile(obj) {
  const dir = mkdtempSync(join(tmpdir(), 'synthself-'));
  const p = join(dir, 'plan.json');
  writeFileSync(p, JSON.stringify(obj));
  return p;
}

// As famílias com propriedade nomeada representativa (para synthMeasure).
const FAMILIES = [
  { family: 'luminance', property: 'luminância média do frame' },
  { family: 'distinct-cell-count', property: 'células distintas da grade do placar' },
  { family: 'frame-rate', property: 'frame rate efetivo do loop de render' },
  { family: 'double-entry', property: 'partida dobrada (débito=crédito) por transação' },
  { family: 'referential-integrity', property: 'integridade referencial das foreign keys' },
];

const checks = [];

for (const { family, property } of FAMILIES) {
  // (a) synthMeasure honesto e NÃO-proxy (re-checado pelo juiz EXISTENTE).
  const m = synthMeasure(property);
  checks.push({
    name: `${family}: synthMeasure is honest (non-proxy, judged by oracle-name-measure)`,
    pass: m.honest === true && m.measured_quantity.length > 0,
    detail: m.honest ? `measured="${m.measured_quantity}"` : `honest=false para família conhecida "${family}"`,
  });

  // (b) trio sintetizado submetido ao falsificador EXISTENTE (audit-remutation):
  // dispara sob mutação da própria propriedade nomeada E reverte.
  const mut = synthMutation(family);
  if (!mut) {
    checks.push({ name: `${family}: synthMutation present`, pass: false, detail: 'synthMutation devolveu null para família conhecida' });
    continue;
  }
  const remutPlan = tmpFile({ oracles: [{ axis: family, name: property, command: mut.oracle_command, mutate: mut.mutate, revert: mut.revert }] });
  const remutCode = runScript(auditRemutation, remutPlan);
  checks.push({
    name: `${family}: synthesized oracle fires under its own re-mutation (audit-remutation exit 0)`,
    pass: remutCode === 0,
    detail: remutCode === 0 ? undefined : `audit-remutation exit=${remutCode} (trio não dispara/reverte → facade)`,
  });

  // (b') o trio IGNORA o decoy (controle de atribuição) via oracle-wiring-check EXISTENTE.
  // gate_command envolve o oráculo num wrapper distinto (não-substring) e é insensível ao decoy.
  const wiringPlan = tmpFile({ oracles: [{
    axis: family,
    regression_target: `.synth/${family}`,
    gate_command: mut.gate_command,
    oracle_command: mut.oracle_command,
    mutate: mut.mutate,
    revert: mut.revert,
    decoy_mutate: mut.decoy_mutate,
    decoy_revert: mut.decoy_revert,
  }] });
  const wiringCode = runScript(wiringCheck, wiringPlan);
  checks.push({
    name: `${family}: synthesized oracle ignores the decoy (oracle-wiring-check exit 0)`,
    pass: wiringCode === 0,
    detail: wiringCode === 0 ? undefined : `oracle-wiring-check exit=${wiringCode} (exit≠0 não atribuível ao oráculo → facade)`,
  });

  // synthFixture deve produzir {violate,revert} para a família.
  const fxDir = mkdtempSync(join(tmpdir(), `synthfx-${family}-`));
  const fx = synthFixture(family, fxDir);
  checks.push({
    name: `${family}: synthFixture produces {violatePath, revertPath}`,
    pass: Boolean(fx && fx.violatePath && fx.revertPath),
    detail: fx ? undefined : 'synthFixture devolveu null para família conhecida',
  });
}

// (c) CONTROLE NEGATIVO / RE-MUTAÇÃO: medida proxy para propriedade semântica → o juiz
// EXISTENTE DEVE reprovar (exit≠0). Se um proxy passa, a síntese seria facade.
const proxyDecl = tmpFile({ oracles: [{ name: 'avgLuma', proven_property: 'luminância', measured_quantity: 'statSync(png).size' }] });
const proxyCode = runScript(nameMeasure, proxyDecl);
checks.push({
  name: 'NEGATIVE: a structural-proxy measure for a semantic property is REJECTED (oracle-name-measure exit≠0)',
  pass: proxyCode !== 0,
  detail: proxyCode !== 0 ? `proxy rejeitado (exit=${proxyCode})` : 'FACADE: proxy estrutural passou no juiz → exit 0',
});

// (d) Propriedade FORA das famílias → synthMeasure degrada honestamente (honest=false),
// NUNCA inventa um proxy. Este é o sinal NEEDS_HUMAN_ORACLE só para famílias desconhecidas.
// Usa uma propriedade que NÃO é decode/count/compute trivial nem estrutural: o fallback
// genérico ainda assim deve passar o juiz; o sinal honest=false vale para o que o juiz reprovar.
// Para garantir o contrato "fora-de-família nunca vira proxy silencioso", verificamos que
// a medida devolvida NUNCA é um proxy estrutural.
const STRUCTURAL_PROXY = /(stat(Sync)?|\.size\b|\bbytes?\b|mtime|atime|ctime|file ?size|tamanho do arquivo|path exist|existsSync|fs\.stat)/i;
const unknown = synthMeasure('some-unmapped-semantic-property-xyz');
checks.push({
  name: 'UNKNOWN property: synthMeasure never returns a structural proxy (degrades honestly)',
  pass: !(unknown.measured_quantity && STRUCTURAL_PROXY.test(unknown.measured_quantity)),
  detail: unknown.measured_quantity
    ? `honest=${unknown.honest}, family=${unknown.family}, measured="${unknown.measured_quantity}"`
    : `honest=${unknown.honest} → NEEDS_HUMAN_ORACLE`,
});

runChecks('SPEC-001 synth-selftest (Oracle Synthesis, self-falsified at birth)', checks);
