// Harness B1 — Negative-grep de runtime-alvo.
// Quando runtime_target=browser, falha (exit≠0 → NEEDS_TREE_REPAIR) se qualquer
// allowed_file importa um módulo Node não-stubado (node:*, child_process, bare fs/path/os).
// É a causa-raiz do node:fs no browser, pego DENTRO do span do SPEC.
//
//   node scripts/runtime-import-grep.mjs <file1> [file2 ...]
//
// Stub explícito: uma linha que importa node:* mas é claramente marcada como server-only
// (comentário /* @server-only */ na mesma linha) é tolerada — o build a remove do bundle client.

import { runChecks, readText } from './lib/harness.mjs';

// import/require de módulo Node. Cobre: `from 'node:fs'`, `from 'fs'`, `require('child_process')`,
// `import 'os'`. Bare specifiers só para os builtins de risco (fs/path/os), não para libs npm.
const NODE_IMPORT =
  /\b(?:import|require)\b[^\n;]*?['"](node:[a-z/]+|child_process|fs|path|os|crypto|stream|worker_threads)['"]/g;
const SERVER_ONLY = /@server-only/;

const files = process.argv.slice(2);
if (files.length === 0) {
  console.error('uso: node scripts/runtime-import-grep.mjs <file1> [file2 ...]');
  process.exit(2);
}

const checks = [];
for (const file of files) {
  let text;
  try {
    text = readText(file);
  } catch (e) {
    checks.push({ name: `${file}: readable`, pass: false, detail: `não pôde ler: ${e.message}` });
    continue;
  }
  const lines = text.split('\n');
  let offenders = 0;
  lines.forEach((line, i) => {
    NODE_IMPORT.lastIndex = 0;
    const m = NODE_IMPORT.exec(line);
    if (m && !SERVER_ONLY.test(line)) {
      offenders++;
      checks.push({
        name: `${file}:${i + 1} no node import in browser-bound source`,
        pass: false,
        detail: `importa "${m[1]}" sem stub: ${line.trim()}`,
      });
    }
  });
  if (offenders === 0) {
    checks.push({ name: `${file}: no non-stubbed node imports`, pass: true });
  }
}

runChecks('B1 runtime-import-grep', checks);
