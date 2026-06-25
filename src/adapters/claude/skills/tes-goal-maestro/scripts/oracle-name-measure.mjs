// Harness C1 (tree-time) — Oráculo mede o que nomeia (NAME↔MEASURE).
// Teste ESTÁTICO do par: cada oráculo declarado deve trazer PROVEN_PROPERTY e
// MEASURED_QUANTITY, e o MEASURED_QUANTITY não pode ser um proxy estrutural conhecido
// (size/mtime/byte/path/statSync) quando a PROVEN_PROPERTY é semântica. Mismatch →
// exit≠0 → oracle_strength=facade → NEEDS_TREE_REPAIR.
//
//   node scripts/oracle-name-measure.mjs <oracle-decls.json>
//
// A parte DINÂMICA (re-mutação da propriedade nomeada) é do scripts/audit-remutation.mjs
// (SPEC-001/D1). C1 estático + D1 dinâmico compõem — ver delta dos 7 mecanismos.
//
// Formato:
//   { "oracles": [
//       { "name": "avgLuma", "proven_property": "luminância média do frame",
//         "measured_quantity": "statSync(png).size em bytes" }   // <- FACADE: proxy estrutural
//   ] }

import { runChecks, readText } from './lib/harness.mjs';

// Proxies estruturais: medem metadados de arquivo/path, nunca propriedade de runtime.
const STRUCTURAL_PROXY = /(stat(Sync)?|\.size\b|\bbytes?\b|mtime|atime|ctime|file ?size|tamanho do arquivo|path exist|existsSync|fs\.stat)/i;
// Propriedade EXPLICITAMENTE estrutural (o único caso em que medir metadados é honesto):
// o nome promete o próprio metadado. Cobre PT/EN.
const NAMED_STRUCTURAL = /(file ?size|tamanho (do )?arquivo|byte count|contagem de bytes|mtime|timestamp|path exist|caminho existe)/i;

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/oracle-name-measure.mjs <oracle-decls.json>');
  process.exit(2);
}

let decl;
try {
  decl = JSON.parse(readText(path));
} catch (e) {
  console.error(`decls inválidas: ${e.message}`);
  process.exit(2);
}

const oracles = Array.isArray(decl.oracles) ? decl.oracles : [];
const checks = [];

if (oracles.length === 0) {
  checks.push({ name: 'oracle declarations present', pass: false, detail: 'oracles[] vazio' });
  runChecks('C1 oracle-name-measure', checks);
}

for (const o of oracles) {
  const label = o.name || '(unnamed)';
  const proven = o.proven_property || '';
  const measured = o.measured_quantity || '';

  // (1) o par deve estar declarado
  checks.push({
    name: `${label}: declares PROVEN_PROPERTY + MEASURED_QUANTITY`,
    pass: proven.length > 0 && measured.length > 0,
    detail: proven && measured ? undefined : 'falta proven_property e/ou measured_quantity',
  });
  if (!proven || !measured) continue;

  // (2) Se a medida é um proxy estrutural, é facade — A MENOS que o nome prometa
  // explicitamente esse próprio metadado. Inverte o gatilho: o proxy na medida é o
  // suspeito (robusto a idioma/propriedade não-listada), e só o nome estrutural escapa.
  const measuresProxy = STRUCTURAL_PROXY.test(measured);
  const namedStructural = NAMED_STRUCTURAL.test(label) || NAMED_STRUCTURAL.test(proven);
  checks.push({
    name: `${label}: measure is not a structural proxy for the named property`,
    pass: !(measuresProxy && !namedStructural),
    detail:
      measuresProxy && !namedStructural
        ? `FACADE: nomeia "${proven}" mas mede o proxy estrutural "${measured}"`
        : undefined,
  });
}

runChecks('C1 oracle-name-measure', checks);
