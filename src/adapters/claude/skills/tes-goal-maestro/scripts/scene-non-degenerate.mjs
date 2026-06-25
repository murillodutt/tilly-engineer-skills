// Harness C4 — Não-degenerescência da cena visual.
// Opera sobre os PIXELS reais do PNG (decoder em lib/png.mjs), nunca sobre window.__game
// ou metadados de arquivo. Falha (exit≠0 → AXIS_UNPROVEN) quando a cena é degenerada:
// variância de luminância abaixo do piso E poucas cores distintas. Pega o caso do placar:
// câmera na parede → 92% dos pixels da mesma cor de tábua.
//
//   node scripts/scene-non-degenerate.mjs <image.png> [varianceFloor] [colorFloor]
//
// Pisos default conservadores; o anchor pode declarar pisos mais altos.

import { decodePng, pixelVariance, distinctColors } from './lib/png.mjs';
import { runChecks } from './lib/harness.mjs';

const imgPath = process.argv[2];
const varFloor = process.argv[3] != null ? Number(process.argv[3]) : 50; // variância de luma mínima
const colorFloor = process.argv[4] != null ? Number(process.argv[4]) : 16; // cores distintas mínimas

if (!imgPath) {
  console.error('uso: node scripts/scene-non-degenerate.mjs <image.png> [varianceFloor] [colorFloor]');
  process.exit(2);
}

let img;
try {
  img = decodePng(imgPath);
} catch (e) {
  // Não-degenerescência não pode ser provada se o PNG não decodifica → falha (não crash).
  runChecks('C4 scene-non-degenerate', [
    { name: `${imgPath}: decodable PNG`, pass: false, detail: e.message },
  ]);
}

const variance = pixelVariance(img);
const colors = distinctColors(img);

// A cena é não-degenerada se passa em PELO MENOS UM critério forte (variância OU cores).
// Uma cena degenerada (parede) falha em AMBOS.
const passVariance = variance >= varFloor;
const passColors = colors >= colorFloor;

const checks = [
  {
    name: `${imgPath}: scene is non-degenerate (variance OR distinct-colors)`,
    pass: passVariance || passColors,
    detail:
      passVariance || passColors
        ? `variance=${variance.toFixed(1)} (floor ${varFloor}), colors=${colors} (floor ${colorFloor})`
        : `DEGENERATE: variance=${variance.toFixed(1)}<${varFloor} E colors=${colors}<${colorFloor} (cena chapada — câmera na parede?)`,
  },
];

runChecks('C4 scene-non-degenerate', checks);
