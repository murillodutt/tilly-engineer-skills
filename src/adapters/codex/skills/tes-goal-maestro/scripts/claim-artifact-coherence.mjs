// Harness D2 — Coerência claim↔artefato + artefato canônico único.
// (a) cada claim quantitativa/categórica do SCORECARD deve citar campo do artefato e bater;
//     contradição → exit≠0 → AXIS_UNPROVEN (claim não-provada elevada sobre a provada).
// (b) artefatos divergentes sem superseded_by → exit≠0 → NEEDS_OWNER_DECISION.
//
//   node scripts/claim-artifact-coherence.mjs <coherence.json>
//
// Formato:
//   {
//     "claims":   { "backend": "WebGPU", "fps": 60 },
//     "artifact": { "backend": "webgl2", "frames": 112 },
//     "fieldMap": { "backend": "backend", "fps": "frames" },   // claim → artifact field
//     "artifacts": [ {"path": "a/browser-metrics.json", "proven": true},
//                    {"path": "b/browser-metrics.json", "proven": false, "superseded_by": "a/..."} ]
//   }

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/claim-artifact-coherence.mjs <coherence.json>');
  process.exit(2);
}

let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`config inválida: ${e.message}`);
  process.exit(2);
}

const checks = [];
const claims = cfg.claims || {};
const artifact = cfg.artifact || {};
const fieldMap = cfg.fieldMap || {};

// (a) coerência claim↔artefato
for (const [claimKey, claimVal] of Object.entries(claims)) {
  const artField = fieldMap[claimKey] || claimKey;
  const artVal = artifact[artField];
  // comparação case-insensitive para categóricos; numérica para números
  const agree =
    typeof claimVal === 'number'
      ? Number(artVal) === claimVal
      : String(artVal).toLowerCase() === String(claimVal).toLowerCase();
  checks.push({
    name: `claim "${claimKey}=${claimVal}" agrees with artifact.${artField}`,
    pass: artVal !== undefined && agree,
    detail: agree && artVal !== undefined ? undefined : `AXIS_UNPROVEN: claim=${claimVal} vs artifact.${artField}=${artVal}`,
  });
}

// (b) artefato canônico único por eixo
const artifacts = Array.isArray(cfg.artifacts) ? cfg.artifacts : [];
if (artifacts.length > 1) {
  const authoritative = artifacts.filter((a) => !a.superseded_by);
  const divergentProven = new Set(artifacts.map((a) => a.proven)).size > 1;
  checks.push({
    name: 'single canonical artifact per axis (or stale carries superseded_by)',
    pass: authoritative.length === 1,
    detail:
      authoritative.length === 1
        ? undefined
        : divergentProven
          ? `NEEDS_OWNER_DECISION: ${authoritative.length} artefatos autoritativos com proven divergente, sem superseded_by`
          : `${authoritative.length} artefatos sem superseded_by`,
  });
}

if (checks.length === 0) {
  checks.push({ name: 'has claims or artifacts to check', pass: false, detail: 'nada para verificar' });
}

runChecks('D2 claim-artifact-coherence', checks);
