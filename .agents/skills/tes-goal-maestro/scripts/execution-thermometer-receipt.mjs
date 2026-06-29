// SPEC-003 execution thermometer Markdown context receipt renderer.
// Renders the compact chat receipt from generation-time schema files only and
// rejects inline HTML, images, Mermaid, or over-wide lines so the artifact stays
// Markdown-only.
//
//   node scripts/execution-thermometer-receipt.mjs <exec_identity.yaml> <exec_metrics.json> <context-receipt.md>
//   node scripts/execution-thermometer-receipt.mjs --check-only <context-receipt.md>

import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readText } from './lib/harness.mjs';
import { writeFileSync } from 'node:fs';

const here = dirname(fileURLToPath(import.meta.url));
const MAX_LINE_WIDTH = 120;
const args = process.argv.slice(2);

if (args[0] === '--check-only') {
  const receiptPath = args[1];
  if (!receiptPath || args.length !== 2) {
    usage();
    process.exit(2);
  }
  const receipt = readText(receiptPath);
  const findings = validateReceipt(receipt);
  if (findings.length > 0) {
    for (const finding of findings) {
      console.error(finding);
    }
    process.exit(1);
  }
  console.log(JSON.stringify({ status: 'PASS', receipt: receiptPath }, null, 2));
  process.exit(0);
}

if (args.length !== 3) {
  usage();
  process.exit(2);
}

const [identityPath, metricsPath, outputPath] = args;

try {
  execFileSync('node', [join(here, 'execution-thermometer-schema.mjs'), identityPath, metricsPath], { stdio: 'pipe' });
} catch (error) {
  process.stderr.write(error.stdout?.toString() ?? '');
  process.stderr.write(error.stderr?.toString() ?? '');
  console.error('receipt input failed SPEC-001 schema validation');
  process.exit(1);
}

let identity;
let metrics;
try {
  identity = parseSimpleYaml(readText(identityPath));
  metrics = JSON.parse(readText(metricsPath));
} catch (error) {
  console.error(`cannot read receipt input: ${error.message}`);
  process.exit(1);
}

const receipt = renderReceipt(identity, metrics);
const findings = validateReceipt(receipt);

if (findings.length > 0) {
  for (const finding of findings) {
    console.error(finding);
  }
  process.exit(1);
}

writeFileSync(outputPath, receipt);
console.log(JSON.stringify({
  status: 'PASS',
  output: outputPath,
  run_id: identity.run_id,
  signals: Array.isArray(metrics.five_signals) ? metrics.five_signals.length : 0,
}, null, 2));

function usage() {
  console.error('usage: node scripts/execution-thermometer-receipt.mjs <exec_identity.yaml> <exec_metrics.json> <context-receipt.md>');
  console.error('   or: node scripts/execution-thermometer-receipt.mjs --check-only <context-receipt.md>');
}

function renderReceipt(identity, metrics) {
  const latestLoop = metrics.latest_loop ?? {};
  const sources = Array.isArray(metrics.sources) ? metrics.sources : [];
  const lines = [];

  lines.push('# Goal Maestro Execution Receipt');
  lines.push('');
  lines.push(`Run: \`${safeInline(clip(identity.run_id, 72))}\``);
  lines.push(`Project: \`${safeInline(clip(identity.project_id, 38))}\`; Series: \`${safeInline(clip(identity.series_id, 38))}\``);
  lines.push(`Report: \`${safeInline(clip(identity.report_status, 32))}\`; Generated: \`${safeInline(identity.generated_at_utc)}\``);
  lines.push(`Harness: \`${safeInline(clip(identity.harness?.name, 34))} ${safeInline(clip(identity.harness?.version, 16))}\`; Adapter: \`${safeInline(clip(identity.harness?.adapter, 12))}\``);
  lines.push(`Model: \`${safeInline(clip(identity.model?.provider, 24))}/${safeInline(clip(identity.model?.identity, 28))}\`; Reasoning: \`${safeInline(clip(identity.model?.reasoning_profile, 20))}\`; Effort: \`${safeInline(clip(identity.model?.effort_multiplier, 12))}\``);
  lines.push('');

  lines.push('## Five Signals');
  lines.push('');
  lines.push('| Signal | Status | Score | vs Plan | Notes |');
  lines.push('|---|---|---|---|---|');
  for (const row of metrics.five_signals ?? []) {
    lines.push(`| ${cell(row.signal)} | ${cell(displayStatus(row.status))} | ${cell(score(row.score))} | ${cell(vsPlan(row.vs_plan))} | ${cell(clip(row.notes, 42))} |`);
  }
  lines.push('');

  lines.push('## Objective Feedback');
  lines.push('');
  pushBullet(lines, 'Objective', latestLoop.objective || 'unproven');
  pushBullet(lines, 'Latest loop', `${latestLoop.loop_id || 'unproven'} / ${displayStatus(latestLoop.status)}`);
  pushBullet(lines, 'Summary', latestLoop.summary || 'unproven');
  pushBullet(lines, 'Evidence posture', `${metrics.unproven_metrics?.length ?? 0} unproven metric(s)`);
  lines.push('');

  lines.push('## Run Context');
  lines.push('');
  pushBullet(lines, 'Goal Maestro state', metrics.final_status?.goal_maestro_execution_state || 'unproven');
  pushBullet(lines, 'Thermometer report', metrics.final_status?.thermometer_report_status || 'unproven');
  pushBullet(lines, 'Share gate', metrics.final_status?.share_gate_status || 'unproven');
  pushBullet(lines, 'Specs', Array.isArray(latestLoop.spec_ids) ? latestLoop.spec_ids.join(', ') : 'unproven');
  lines.push('');

  lines.push('## Next Actions');
  lines.push('');
  const nextActions = Array.isArray(latestLoop.next_actions) ? latestLoop.next_actions : [];
  if (nextActions.length === 0) {
    lines.push('- No next actions recorded.');
  } else {
    for (const action of nextActions) {
      pushListItem(lines, action);
    }
  }
  lines.push('');

  lines.push('## Source Package References');
  lines.push('');
  lines.push('- `exec_identity.yaml`');
  lines.push('- `exec_metrics.json`');
  for (const source of sources) {
    lines.push(`- \`${safeInline(source.ref)}\`: ${plainText(clip(source.description, 70))}`);
    lines.push(`  - path: \`${safeInline(clip(source.path, 82))}\``);
    lines.push(`  - hash: \`${safeInline(source.hash)}\``);
  }

  return `${lines.join('\n')}\n`;
}

function validateReceipt(markdown) {
  const findings = [];
  const required = [
    '# Goal Maestro Execution Receipt',
    '## Five Signals',
    '## Objective Feedback',
    '## Run Context',
    '## Next Actions',
    '## Source Package References',
  ];
  for (const token of required) {
    if (!markdown.includes(token)) {
      findings.push(`missing required section: ${token}`);
    }
  }
  for (const signal of ['Delivery', 'Fidelity', 'Proof', 'Efficiency', 'Protection']) {
    if (!markdown.includes(`| ${signal} |`)) {
      findings.push(`missing signal row: ${signal}`);
    }
  }
  if (!/EV-[A-Z0-9-]+/.test(markdown)) {
    findings.push('missing source evidence references');
  }
  if (/<\/?[A-Za-z][^>\n]*>/.test(markdown)) {
    findings.push('inline HTML is not allowed');
  }
  if (/```mermaid/i.test(markdown) || /!\[/.test(markdown)) {
    findings.push('Mermaid blocks and images are not allowed');
  }
  if (/<script|<style|<button|<input|style=/i.test(markdown)) {
    findings.push('interactive or styled HTML is not allowed');
  }
  markdown.split(/\r?\n/).forEach((line, index) => {
    if (line.length > MAX_LINE_WIDTH) {
      findings.push(`line ${index + 1} exceeds ${MAX_LINE_WIDTH} characters`);
    }
  });
  return findings;
}

function pushBullet(lines, label, value) {
  lines.push(`- ${label}: ${plainText(clip(value, 94 - label.length))}`);
}

function pushListItem(lines, value) {
  lines.push(`- ${plainText(clip(value, 110))}`);
}

function displayStatus(status) {
  const value = String(status ?? 'unproven');
  return {
    on_track: 'ON TRACK',
    unproven: 'UNPROVEN',
    needs_review: 'NEEDS REVIEW',
    blocked: 'BLOCKED',
    fail: 'FAIL',
  }[value] ?? value.toUpperCase();
}

function score(value) {
  return typeof value === 'number' && Number.isFinite(value) ? `${Math.round(value)}%` : 'n/a';
}

function vsPlan(value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return 'n/a';
  }
  return `${value > 0 ? '+' : ''}${Math.round(value)}%`;
}

function cell(value) {
  return plainText(value).replace(/\|/g, '\\|');
}

function plainText(value) {
  return safeInline(value).replace(/\s+/g, ' ').trim();
}

function safeInline(value) {
  return String(value ?? 'unproven').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\r?\n/g, ' ');
}

function clip(value, maxLength) {
  const text = safeInline(value);
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, Math.max(0, maxLength - 3))}...`;
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
    if (indent % 2 !== 0) {
      throw new Error(`line ${index + 1}: indentation must use multiples of two spaces`);
    }
    const key = match[2];
    const rawValue = match[3] ?? '';

    while (stack.length > 1 && indent <= stack.at(-1).indent) {
      stack.pop();
    }
    const parent = stack.at(-1).value;
    if (Object.prototype.hasOwnProperty.call(parent, key)) {
      throw new Error(`line ${index + 1}: duplicate key "${key}"`);
    }

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
