// Harness D4 — Ledger sem placeholder.
// Falha (exit≠0 → NEEDS_EXECUTION_UNIT_FIDELITY) se qualquer entrada `commit:` do
// ledger/SCORECARD carrega placeholder em vez de sha real ou rationale no-commit explícito.
// Rodado pelo Executive Stop Audit.
//
//   node scripts/ledger-no-placeholder.mjs <ledger-or-scorecard.md> [more.md...]
//
// Placeholders proibidos numa linha `commit:`: <a seguir>, vazio, TODO, TBD, <...>, <hash>.

import { runChecks, readText } from './lib/harness.mjs';

// Placeholder proibido logo após `commit:` (schema field ou célula de tabela).
const PLACEHOLDER = /commit:\s*(<a seguir>|<\.\.\.>|<hash>|TODO|TBD)\b/i;
// Linha de commit aceitável: sha hex (>=7) OU rationale explícito começando com "no-commit".
const ACCEPTABLE = /commit:\s*([0-9a-f]{7,40}\b|no-commit\b)/i;
// Uma DECLARAÇÃO de commit é `commit:` seguido de um VALOR não-vazio (não ` |` nem fim de
// célula): campo de schema no início da linha, ou célula de tabela de dados. Headers de tabela
// (`| commit ref |`, ou `commit:` colado em ` |`) e menção em prosa não declaram valor → ignorados.
const COMMIT_WITH_VALUE = /commit:\s*\S/i;
const IS_TABLE_SEPARATOR = (line) => /^\s*\|?[\s:|-]+\|?\s*$/.test(line) && line.includes('-');
const IS_COMMIT_DECLARATION = (line) =>
  !IS_TABLE_SEPARATOR(line) &&
  COMMIT_WITH_VALUE.test(line) &&
  // o caractere após `commit:` e espaços não pode ser fechamento de célula vazia
  !/commit:\s*\|/i.test(line) &&
  (/^\s*commit:/i.test(line) || /^\s*\|/.test(line));

const files = process.argv.slice(2);
if (files.length === 0) {
  console.error('uso: node scripts/ledger-no-placeholder.mjs <file.md> [...]');
  process.exit(2);
}

const checks = [];
for (const file of files) {
  const text = readText(file);
  const lines = text.split('\n');
  lines.forEach((line, i) => {
    // Só inspeciona linhas que DECLARAM um commit (schema field ou célula de tabela),
    // não prosa que apenas menciona a palavra.
    if (!IS_COMMIT_DECLARATION(line)) return;
    const isPlaceholder = PLACEHOLDER.test(line);
    const isAcceptable = ACCEPTABLE.test(line);
    checks.push({
      name: `${file}:${i + 1} commit field`,
      pass: !isPlaceholder && isAcceptable,
      detail: isPlaceholder
        ? `placeholder proibido: "${line.trim()}"`
        : isAcceptable
          ? undefined
          : `commit nem sha nem rationale no-commit: "${line.trim()}"`,
    });
  });
}

if (checks.length === 0) {
  checks.push({ name: 'commit lines present', pass: false, detail: 'nenhuma linha commit: encontrada' });
}

runChecks('D4 ledger-no-placeholder', checks);
