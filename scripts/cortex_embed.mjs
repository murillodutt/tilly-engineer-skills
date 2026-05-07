#!/usr/bin/env node
/**
 * Local Cortex embedding helper.
 *
 * Reads JSON on stdin:
 *   {"model":"Xenova/multilingual-e5-small","items":[{"path":"...","text":"..."}]}
 *
 * Writes JSON on stdout. This helper is intentionally honest: when the runtime,
 * package, model, or cache is unavailable it returns BLOCKED instead of silently
 * pretending neural semantic curation happened.
 */

import { stdin } from "node:process";

async function readStdin() {
  const chunks = [];
  for await (const chunk of stdin) {
    chunks.push(Buffer.from(chunk));
  }
  return Buffer.concat(chunks).toString("utf8");
}

function blocked(failures) {
  return {
    status: "BLOCKED",
    backend: "xenova",
    backend_status: "BLOCKED",
    failures: Array.isArray(failures) ? failures : [String(failures)],
  };
}

function rowsFromTensor(tensor, expectedRows) {
  const raw = typeof tensor.tolist === "function" ? tensor.tolist() : tensor;
  if (!Array.isArray(raw)) {
    throw new Error("embedding tensor is not array-like");
  }
  if (raw.length === expectedRows && Array.isArray(raw[0]) && typeof raw[0][0] === "number") {
    return raw;
  }
  if (expectedRows === 1 && typeof raw[0] === "number") {
    return [raw];
  }
  if (
    raw.length === expectedRows
    && Array.isArray(raw[0])
    && Array.isArray(raw[0][0])
  ) {
    return raw.map((sequence) => {
      const dimensions = sequence[0].length;
      const pooled = Array(dimensions).fill(0);
      for (const token of sequence) {
        for (let index = 0; index < dimensions; index += 1) {
          pooled[index] += token[index];
        }
      }
      const scale = sequence.length || 1;
      return pooled.map((value) => value / scale);
    });
  }
  throw new Error("unexpected embedding tensor shape");
}

function normalize(vector) {
  const magnitude = Math.sqrt(vector.reduce((total, value) => total + value * value, 0));
  if (!magnitude) {
    return vector;
  }
  return vector.map((value) => Number((value / magnitude).toFixed(8)));
}

async function main() {
  let payload;
  try {
    payload = JSON.parse(await readStdin());
  } catch (error) {
    console.log(JSON.stringify(blocked(`invalid input JSON: ${error.message}`)));
    return 2;
  }

  const model = payload.model || "Xenova/multilingual-e5-small";
  const items = Array.isArray(payload.items) ? payload.items : [];
  let transformers;
  try {
    transformers = await import("@huggingface/transformers");
  } catch (error) {
    console.log(JSON.stringify(blocked(`@huggingface/transformers unavailable: ${error.message}`)));
    return 2;
  }

  if (!items.length) {
    console.log(JSON.stringify({
      status: "PASS",
      backend: "xenova",
      backend_status: "CERTIFIED",
      model,
      dimensions: 0,
      vectors: [],
      failures: [],
    }));
    return 0;
  }

  try {
    const { pipeline } = transformers;
    const extractor = await pipeline("feature-extraction", model);
    const texts = items.map((item) => item.text || "");
    const tensor = await extractor(texts, { pooling: "mean", normalize: true });
    const rows = rowsFromTensor(tensor, texts.length).map(normalize);
    const dimensions = rows[0] ? rows[0].length : 0;

    console.log(JSON.stringify({
      status: "PASS",
      backend: "xenova",
      backend_status: "CERTIFIED",
      model,
      dimensions,
      vectors: items.map((item, index) => ({
        path: item.path,
        title: item.title || "",
        content_hash: item.content_hash || "",
        vector: rows[index],
      })),
      failures: [],
    }));
    return 0;
  } catch (error) {
    console.log(JSON.stringify(blocked(`Xenova embedding failed: ${error.message}`)));
    return 2;
  }
}

main().then((code) => {
  process.exitCode = code;
}).catch((error) => {
  console.log(JSON.stringify(blocked(`unhandled Xenova helper error: ${error.message}`)));
  process.exitCode = 2;
});
