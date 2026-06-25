// Decoder PNG mínimo (IHDR + IDAT inflate + unfilter) sem dependência externa.
// Só o necessário para o oráculo de não-degenerescência: dimensões + pixels RGBA.
// Suporta o caso comum: bit depth 8, color type 2 (RGB) ou 6 (RGBA). Outros → throw.
// Usa node:zlib (built-in). Este é o caminho HONESTO: mede pixels, não metadados.

import { readFileSync } from 'node:fs';
import { inflateSync } from 'node:zlib';

const SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function paeth(a, b, c) {
  const p = a + b - c;
  const pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c);
  if (pa <= pb && pa <= pc) return a;
  if (pb <= pc) return b;
  return c;
}

/** Decodifica um PNG em {width, height, channels, data: Uint8Array (linha-major, sem filtro)}. */
export function decodePng(path) {
  const buf = readFileSync(path);
  if (!buf.subarray(0, 8).equals(SIG)) throw new Error('não é PNG (assinatura)');

  let off = 8;
  let width = 0, height = 0, bitDepth = 0, colorType = 0;
  const idat = [];

  while (off < buf.length) {
    const len = buf.readUInt32BE(off);
    const type = buf.toString('ascii', off + 4, off + 8);
    const dataStart = off + 8;
    if (type === 'IHDR') {
      width = buf.readUInt32BE(dataStart);
      height = buf.readUInt32BE(dataStart + 4);
      bitDepth = buf[dataStart + 8];
      colorType = buf[dataStart + 9];
    } else if (type === 'IDAT') {
      idat.push(buf.subarray(dataStart, dataStart + len));
    } else if (type === 'IEND') {
      break;
    }
    off = dataStart + len + 4; // pula dados + CRC
  }

  if (bitDepth !== 8 || (colorType !== 2 && colorType !== 6)) {
    throw new Error(`PNG não suportado (bitDepth=${bitDepth}, colorType=${colorType}); use 8-bit RGB/RGBA`);
  }
  const channels = colorType === 6 ? 4 : 3;
  const raw = inflateSync(Buffer.concat(idat));

  // Unfilter por scanline.
  const stride = width * channels;
  const out = new Uint8Array(height * stride);
  let pos = 0;
  for (let y = 0; y < height; y++) {
    const filter = raw[pos++];
    for (let x = 0; x < stride; x++) {
      const rawByte = raw[pos++];
      const a = x >= channels ? out[y * stride + x - channels] : 0;
      const b = y > 0 ? out[(y - 1) * stride + x] : 0;
      const c = x >= channels && y > 0 ? out[(y - 1) * stride + x - channels] : 0;
      let val;
      switch (filter) {
        case 0: val = rawByte; break;
        case 1: val = rawByte + a; break;
        case 2: val = rawByte + b; break;
        case 3: val = rawByte + ((a + b) >> 1); break;
        case 4: val = rawByte + paeth(a, b, c); break;
        default: throw new Error(`filtro PNG desconhecido: ${filter}`);
      }
      out[y * stride + x] = val & 0xff;
    }
  }
  return { width, height, channels, data: out };
}

/** Variância média de luminância (0..255²) sobre todos os pixels. */
export function pixelVariance(img) {
  const { data, channels } = img;
  const n = data.length / channels;
  let sum = 0;
  const lumas = new Float64Array(n);
  for (let i = 0, p = 0; i < data.length; i += channels, p++) {
    const luma = 0.2126 * data[i] + 0.7152 * data[i + 1] + 0.0722 * data[i + 2];
    lumas[p] = luma;
    sum += luma;
  }
  const mean = sum / n;
  let acc = 0;
  for (let p = 0; p < n; p++) acc += (lumas[p] - mean) ** 2;
  return acc / n;
}

/** Conta cores RGB distintas (quantizadas a 5 bits/canal para tolerar ruído). */
export function distinctColors(img) {
  const { data, channels } = img;
  const seen = new Set();
  for (let i = 0; i < data.length; i += channels) {
    const r = data[i] >> 3, g = data[i + 1] >> 3, b = data[i + 2] >> 3;
    seen.add((r << 10) | (g << 5) | b);
  }
  return seen.size;
}
