// SPEC-006 sanitized local package builder.
// Builds the default local evidence package and blocks unsafe input before any
// share lane can exist. The package stays local-only: README, Markdown, YAML,
// JSON, static HTML, and checksums.
//
//   node scripts/execution-thermometer-package.mjs <exec_identity.yaml> <exec_metrics.json> <output-root>

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { copyFileSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readText } from './lib/harness.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const [identityPath, metricsPath, outputRoot] = process.argv.slice(2);

if (!identityPath || !metricsPath || !outputRoot || process.argv.length !== 5) {
  console.error('usage: node scripts/execution-thermometer-package.mjs <exec_identity.yaml> <exec_metrics.json> <output-root>');
  process.exit(2);
}

const identityText = readText(identityPath);
const metricsText = readText(metricsPath);
const sanitizerFindings = scanUnsafe(`${identityText}\n${metricsText}`);

if (sanitizerFindings.length > 0) {
  for (const finding of sanitizerFindings) {
    console.error(`BLOCKED_BY_SANITIZATION: ${finding}`);
  }
  process.exit(1);
}

let identity;
try {
  execFileSync('node', [join(here, 'execution-thermometer-schema.mjs'), identityPath, metricsPath], { stdio: 'pipe' });
  identity = parseSimpleYaml(identityText);
} catch (error) {
  process.stderr.write(error.stdout?.toString() ?? '');
  process.stderr.write(error.stderr?.toString() ?? '');
  console.error(`package input invalid: ${error.message}`);
  process.exit(1);
}

const runId = safeSegment(identity.run_id);
const packageDir = resolve(outputRoot, `execution-thermometer-${runId}`);

try {
  rmSync(packageDir, { recursive: true, force: true });
  mkdirSync(packageDir, { recursive: true });
  copyFileSync(identityPath, join(packageDir, 'exec_identity.yaml'));
  copyFileSync(metricsPath, join(packageDir, 'exec_metrics.json'));
  writeFileSync(join(packageDir, 'README.md'), renderReadme(identity));
  execFileSync('node', [
    join(here, 'execution-thermometer-receipt.mjs'),
    join(packageDir, 'exec_identity.yaml'),
    join(packageDir, 'exec_metrics.json'),
    join(packageDir, 'context-receipt.md'),
  ], { stdio: 'pipe' });
  execFileSync('node', [
    join(here, 'execution-thermometer-html.mjs'),
    join(packageDir, 'exec_identity.yaml'),
    join(packageDir, 'exec_metrics.json'),
    join(packageDir, 'execution-thermometer.html'),
  ], { stdio: 'pipe' });
} catch (error) {
  process.stderr.write(error.stdout?.toString() ?? '');
  process.stderr.write(error.stderr?.toString() ?? '');
  console.error(`cannot build local package: ${error.message}`);
  process.exit(1);
}

const packageFiles = [
  'README.md',
  'context-receipt.md',
  'exec_identity.yaml',
  'exec_metrics.json',
  'execution-thermometer.html',
];

const generatedText = packageFiles.map((file) => readFileSync(join(packageDir, file), 'utf8')).join('\n');
const generatedFindings = scanUnsafe(generatedText);
if (generatedFindings.length > 0) {
  rmSync(packageDir, { recursive: true, force: true });
  for (const finding of generatedFindings) {
    console.error(`BLOCKED_BY_SANITIZATION: generated ${finding}`);
  }
  process.exit(1);
}

const checksumLines = packageFiles.map((file) => `${sha256(readFileSync(join(packageDir, file)))}  ${file}`);
writeFileSync(join(packageDir, 'checksums.sha256'), `${checksumLines.join('\n')}\n`);
const manifestHash = sha256(readFileSync(join(packageDir, 'checksums.sha256')));

console.log(JSON.stringify({
  status: 'PASS',
  package_dir: packageDir,
  run_id: identity.run_id,
  files: [...packageFiles, 'checksums.sha256'],
  manifest_hash: manifestHash,
}, null, 2));

function renderReadme(identity) {
  return `# Execution Thermometer Package

Local-first evidence package for Goal Maestro run \`${identity.run_id}\`.

Files:

- \`context-receipt.md\`
- \`exec_identity.yaml\`
- \`exec_metrics.json\`
- \`execution-thermometer.html\`
- \`checksums.sha256\`

Sharing remains opt-in and requires the later Share Gate. This package builder
does not push, publish, fetch, or open a remote connection.
`;
}

function scanUnsafe(text) {
  const findings = [];
  const patterns = [
    ['secret token marker', /SECRET_TOKEN|sk-[A-Za-z0-9_-]{10,}|AKIA[0-9A-Z]{16}|BEGIN (RSA |OPENSSH |)PRIVATE KEY/],
    ['private filesystem path', /(^|[\s"'(:])(?:\/Users\/|\/home\/|C:\\Users\\|~\/Dev\/)/],
  ];
  for (const [label, pattern] of patterns) {
    if (pattern.test(text)) {
      findings.push(label);
    }
  }
  for (const term of privateVocabulary()) {
    if (term && text.includes(term)) {
      findings.push(`private vocabulary term "${term}"`);
    }
  }
  return findings;
}

function privateVocabulary() {
  const path = resolve(process.cwd(), '.tes/private-vocabulary.txt');
  if (!existsSync(path)) {
    return [];
  }
  return readFileSync(path, 'utf8')
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith('#'));
}

function safeSegment(value) {
  const text = String(value ?? 'unproven').replace(/[^A-Za-z0-9._-]/g, '-');
  return text || 'unproven';
}

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

function parseSimpleYaml(text) {
  const root = {};
  const stack = [{ indent: -1, value: root }];
  const lines = text.split(/\r?\n/);

  lines.forEach((rawLine, index) => {
    if (/^\s*(#.*)?$/.test(rawLine)) {
      return;
    }
    const match = rawLine.match(/^(\s*)([A-Za-z0-9_]+):(?:\s*(.*))?$/);
    if (!match) {
      throw new Error(`line ${index + 1}: expected "key: value"`);
    }
    const indent = match[1].length;
    const key = match[2];
    const rawValue = match[3] ?? '';

    while (stack.length > 1 && indent <= stack.at(-1).indent) {
      stack.pop();
    }
    const parent = stack.at(-1).value;
    if (rawValue === '') {
      const child = {};
      parent[key] = child;
      stack.push({ indent, value: child });
      return;
    }
    parent[key] = parseYamlScalar(rawValue);
  });

  return root;
}

function parseYamlScalar(rawValue) {
  const value = stripYamlComment(rawValue).trim();
  if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
    return value.slice(1, -1);
  }
  if (value === 'true') {
    return true;
  }
  if (value === 'false') {
    return false;
  }
  if (value === 'null') {
    return null;
  }
  if (/^-?\d+(\.\d+)?$/.test(value)) {
    return Number(value);
  }
  return value;
}

function stripYamlComment(value) {
  let quote = null;
  for (let index = 0; index < value.length; index++) {
    const char = value[index];
    if ((char === '"' || char === "'") && value[index - 1] !== '\\') {
      quote = quote === char ? null : quote ?? char;
    }
    if (char === '#' && quote === null && /\s/.test(value[index - 1] ?? ' ')) {
      return value.slice(0, index);
    }
  }
  return value;
}
