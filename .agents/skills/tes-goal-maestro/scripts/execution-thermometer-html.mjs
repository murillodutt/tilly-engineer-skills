// SPEC-004 execution thermometer static HTML renderer.
// Generates an offline report from generation-time schema files, embeds a
// static normalized snapshot, and rejects fetch/CDN/telemetry/runtime reads.
//
//   node scripts/execution-thermometer-html.mjs <exec_identity.yaml> <exec_metrics.json> <execution-thermometer.html>
//   node scripts/execution-thermometer-html.mjs --check-only <execution-thermometer.html> --expect-loop L4

import { execFileSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readText } from './lib/harness.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const cli = parseArgs(process.argv.slice(2));

if (cli.checkOnly) {
  if (cli.positionals.length !== 1) {
    usage();
    process.exit(2);
  }
  const html = readText(cli.positionals[0]);
  const findings = validateHtml(html, cli.options.expectLoop);
  if (findings.length > 0) {
    for (const finding of findings) {
      console.error(finding);
    }
    process.exit(1);
  }
  console.log(JSON.stringify({ status: 'PASS', html: cli.positionals[0] }, null, 2));
  process.exit(0);
}

if (cli.positionals.length !== 3) {
  usage();
  process.exit(2);
}

const [identityPath, metricsPath, outputPath] = cli.positionals;

try {
  execFileSync('node', [join(here, 'execution-thermometer-schema.mjs'), identityPath, metricsPath], { stdio: 'pipe' });
} catch (error) {
  process.stderr.write(error.stdout?.toString() ?? '');
  process.stderr.write(error.stderr?.toString() ?? '');
  console.error('HTML input failed SPEC-001 schema validation');
  process.exit(1);
}

let identity;
let metrics;
try {
  identity = parseSimpleYaml(readText(identityPath));
  metrics = JSON.parse(readText(metricsPath));
} catch (error) {
  console.error(`cannot read HTML input: ${error.message}`);
  process.exit(1);
}

const html = renderHtml(identity, metrics);
const findings = validateHtml(html, cli.options.expectLoop);

if (findings.length > 0) {
  for (const finding of findings) {
    console.error(finding);
  }
  process.exit(1);
}

writeFileSync(outputPath, html);
console.log(JSON.stringify({
  status: 'PASS',
  output: outputPath,
  run_id: identity.run_id,
  loops: Array.isArray(metrics.loops) ? metrics.loops.length : 0,
}, null, 2));

function usage() {
  console.error('usage: node scripts/execution-thermometer-html.mjs <exec_identity.yaml> <exec_metrics.json> <execution-thermometer.html> [--expect-loop <loop-id>]');
  console.error('   or: node scripts/execution-thermometer-html.mjs --check-only <execution-thermometer.html> [--expect-loop <loop-id>]');
}

function parseArgs(argv) {
  const positionals = [];
  const options = {};
  let checkOnly = false;
  for (let index = 0; index < argv.length; index++) {
    const token = argv[index];
    if (token === '--check-only') {
      checkOnly = true;
      continue;
    }
    if (token === '--expect-loop') {
      const value = argv[++index];
      if (!value) {
        console.error('missing value for --expect-loop');
        process.exit(2);
      }
      options.expectLoop = value;
      continue;
    }
    if (token.startsWith('--')) {
      console.error(`unknown option: ${token}`);
      process.exit(2);
    }
    positionals.push(token);
  }
  return { checkOnly, positionals, options };
}

function renderHtml(identity, metrics) {
  const loops = Array.isArray(metrics.loops) ? metrics.loops : [];
  const latest = metrics.latest_loop ?? loops.at(-1) ?? {};
  const snapshot = JSON.stringify({ identity, metrics }, null, 2);
  const title = `Goal Maestro Execution Thermometer - ${identity.run_id}`;

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(title)}</title>
  <style>
    :root { color-scheme: light; --ink: #1f2937; --muted: #4b5563; --line: #d1d5db; --accent: #0f766e; --soft: #f8fafc; --warn: #fff7ed; }
    * { box-sizing: border-box; }
    body { margin: 0; font: 14px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: white; }
    header, main { max-width: 1120px; margin: 0 auto; padding: 24px; }
    header { border-bottom: 1px solid var(--line); background: var(--soft); }
    h1, h2, h3 { margin: 0 0 12px; line-height: 1.2; }
    h1 { font-size: 28px; }
    h2 { font-size: 20px; margin-top: 28px; }
    h3 { font-size: 16px; }
    p { margin: 0 0 10px; }
    table { width: 100%; border-collapse: collapse; margin: 10px 0 18px; }
    th, td { border: 1px solid var(--line); padding: 8px; text-align: left; vertical-align: top; }
    th { background: #eef2f7; }
    a { color: var(--accent); }
    code { overflow-wrap: anywhere; }
    .meta { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 8px 16px; margin-top: 12px; }
    .pill { display: inline-block; border: 1px solid var(--line); border-radius: 4px; padding: 2px 6px; background: white; }
    .loop-detail { border: 2px solid var(--line); border-radius: 6px; padding: 14px; margin: 14px 0; }
    .loop-detail:target { border-color: var(--accent); background: #ecfdf5; }
    .unproven, .blocked, .needs-review { background: var(--warn); }
    .snapshot { white-space: pre-wrap; overflow-wrap: anywhere; }
    @media print {
      a[href]::after { content: ""; }
      .loop-detail { break-inside: avoid; page-break-inside: avoid; }
      header, main { max-width: none; padding: 12px; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Goal Maestro Execution Thermometer</h1>
    <p>Static local report for run <code>${escapeHtml(identity.run_id)}</code>.</p>
    <div class="meta">
      <div><strong>Project</strong><br><code>${escapeHtml(identity.project_id)}</code></div>
      <div><strong>Series</strong><br><code>${escapeHtml(identity.series_id)}</code></div>
      <div><strong>Report status</strong><br><span class="pill">${escapeHtml(identity.report_status)}</span></div>
      <div><strong>Generated</strong><br><code>${escapeHtml(identity.generated_at_utc)}</code></div>
      <div><strong>Harness</strong><br><code>${escapeHtml(identity.harness?.name)} ${escapeHtml(identity.harness?.version)}</code></div>
      <div><strong>Model</strong><br><code>${escapeHtml(identity.model?.provider)}/${escapeHtml(identity.model?.identity)}</code></div>
    </div>
  </header>
  <main>
    <section id="loop-index">
      <h2>Accumulated Loops</h2>
      ${renderLoopIndex(loops)}
    </section>
    <section id="selected-loop-detail">
      <h2>Selected Loop Detail</h2>
      <p>Use the loop links to load a stable anchor such as <code>#loop-${escapeHtml(latest.loop_id ?? 'L1')}</code>. Printing includes every loop detail below.</p>
      ${loops.map(renderLoopDetail).join('\n')}
    </section>
    <section id="spec-results">
      <h2>SPEC Results</h2>
      ${renderSpecResults(metrics.spec_results ?? [])}
    </section>
    <section id="key-metrics">
      <h2>Key Metrics</h2>
      ${renderMetrics(metrics.lens_results ?? [])}
    </section>
    <section id="unproven-metrics">
      <h2>Unproven Metrics</h2>
      ${renderMetrics(metrics.unproven_metrics ?? [])}
    </section>
    <section id="evidence-references">
      <h2>Evidence References</h2>
      ${renderSources(metrics.sources ?? [])}
    </section>
    <section id="model-harness">
      <h2>Model And Harness Metadata</h2>
      <table>
        <tbody>
          <tr><th>Harness command</th><td><code>${escapeHtml(identity.harness?.command)}</code></td></tr>
          <tr><th>Schema version</th><td><code>${escapeHtml(identity.schema_version)}</code></td></tr>
          <tr><th>Reasoning profile</th><td><code>${escapeHtml(identity.model?.reasoning_profile)}</code></td></tr>
          <tr><th>Effort multiplier</th><td><code>${escapeHtml(identity.model?.effort_multiplier)}</code></td></tr>
          <tr><th>Share gate</th><td><code>${escapeHtml(metrics.final_status?.share_gate_status)}</code></td></tr>
        </tbody>
      </table>
    </section>
    <section id="source-files">
      <h2>Source Files And Checksums</h2>
      <ul>
        <li><code>exec_identity.yaml</code></li>
        <li><code>exec_metrics.json</code></li>
        <li>Ledger hash: <code>${escapeHtml(identity.ledger?.hash)}</code></li>
        <li>Extraction manifest hash: <code>${escapeHtml(identity.ledger?.extraction_hash)}</code></li>
      </ul>
    </section>
    <section id="normalized-snapshot-section">
      <h2>Embedded Normalized Snapshot</h2>
      <p>The escaped snapshot below was embedded at generation time; the report performs no runtime YAML, JSON, file, or network reads.</p>
      <pre id="normalized-snapshot" class="snapshot" hidden>${escapeHtml(snapshot)}</pre>
    </section>
  </main>
</body>
</html>
`;
}

function renderLoopIndex(loops) {
  if (loops.length === 0) {
    return '<p>No loops recorded.</p>';
  }
  return `<table>
  <thead><tr><th>Loop</th><th>Status</th><th>Objective</th><th>Evidence</th></tr></thead>
  <tbody>
${loops.map((loop) => `    <tr><td><a href="#loop-${escapeHtml(loop.loop_id)}">${escapeHtml(loop.label)}</a></td><td class="${statusClass(loop.status)}">${escapeHtml(displayStatus(loop.status))}</td><td>${escapeHtml(loop.objective)}</td><td>${escapeHtml((loop.evidence_refs ?? []).join(', '))}</td></tr>`).join('\n')}
  </tbody>
</table>`;
}

function renderLoopDetail(loop) {
  return `<article id="loop-${escapeHtml(loop.loop_id)}" class="loop-detail">
  <h3>${escapeHtml(loop.label)}</h3>
  <p><strong>Status:</strong> <span class="${statusClass(loop.status)}">${escapeHtml(displayStatus(loop.status))}</span></p>
  <p><strong>Objective:</strong> ${escapeHtml(loop.objective)}</p>
  <p><strong>Summary:</strong> ${escapeHtml(loop.summary)}</p>
  <p><strong>SPECs:</strong> ${escapeHtml((loop.spec_ids ?? []).join(', ') || 'unproven')}</p>
  <p><strong>Next actions:</strong> ${escapeHtml((loop.next_actions ?? []).join('; ') || 'None recorded.')}</p>
</article>`;
}

function renderSpecResults(results) {
  if (results.length === 0) {
    return '<p>No SPEC results recorded.</p>';
  }
  return `<table>
  <thead><tr><th>SPEC</th><th>Status</th><th>Intent</th><th>Fidelity</th><th>Proof</th><th>Evidence</th></tr></thead>
  <tbody>
${results.map((result) => `    <tr><td>${escapeHtml(result.spec_id)} - ${escapeHtml(result.title)}</td><td class="${statusClass(result.status)}">${escapeHtml(displayStatus(result.status))}</td><td>${score(result.intent_score)}</td><td>${score(result.fidelity_score)}</td><td>${score(result.proof_score)}</td><td>${escapeHtml((result.evidence_refs ?? []).join(', '))}</td></tr>`).join('\n')}
  </tbody>
</table>`;
}

function renderMetrics(metrics) {
  if (metrics.length === 0) {
    return '<p>No rows recorded.</p>';
  }
  return `<table>
  <thead><tr><th>Name</th><th>Status</th><th>Value</th><th>Unit</th><th>Evidence</th><th>Notes</th></tr></thead>
  <tbody>
${metrics.map((metric) => `    <tr><td>${escapeHtml(metric.name)}</td><td class="${statusClass(metric.status)}">${escapeHtml(displayStatus(metric.status))}</td><td>${escapeHtml(metric.value ?? 'n/a')}</td><td>${escapeHtml(metric.unit)}</td><td>${escapeHtml((metric.evidence_refs ?? []).join(', '))}</td><td>${escapeHtml(metric.notes)}</td></tr>`).join('\n')}
  </tbody>
</table>`;
}

function renderSources(sources) {
  if (sources.length === 0) {
    return '<p>No evidence references recorded.</p>';
  }
  return `<table>
  <thead><tr><th>Ref</th><th>Type</th><th>Description</th><th>Path</th><th>Hash</th></tr></thead>
  <tbody>
${sources.map((source) => `    <tr><td>${escapeHtml(source.ref)}</td><td>${escapeHtml(source.type)}</td><td>${escapeHtml(source.description)}</td><td><code>${escapeHtml(source.path)}</code></td><td><code>${escapeHtml(source.hash)}</code></td></tr>`).join('\n')}
  </tbody>
</table>`;
}

function validateHtml(html, expectedLoop) {
  const findings = [];
  for (const token of [
    '<!doctype html>',
    'id="loop-index"',
    'id="selected-loop-detail"',
    'id="spec-results"',
    'id="evidence-references"',
    'id="normalized-snapshot"',
  ]) {
    if (!html.includes(token)) {
      findings.push(`missing HTML token: ${token}`);
    }
  }
  if (expectedLoop) {
    if (!html.includes(`href="#loop-${expectedLoop}"`)) {
      findings.push(`missing loop link #loop-${expectedLoop}`);
    }
    if (!html.includes(`id="loop-${expectedLoop}"`)) {
      findings.push(`missing selected loop target loop-${expectedLoop}`);
    }
  }
  const prohibited = [
    /<script\b/i,
    /\bfetch\s*\(/i,
    /XMLHttpRequest/i,
    /\bimport\s*\(/i,
    /FileReader/i,
    /navigator\.sendBeacon/i,
    /localStorage/i,
    /sessionStorage/i,
    /<link\b[^>]+href=/i,
    /\bsrc\s*=\s*["']/i,
    /https?:\/\//i,
    /cdn/i,
    /telemetry/i,
    /tracking/i,
  ];
  for (const pattern of prohibited) {
    if (pattern.test(html)) {
      findings.push(`prohibited runtime/network pattern: ${pattern}`);
    }
  }
  return findings;
}

function statusClass(status) {
  return {
    unproven: 'unproven',
    blocked: 'blocked',
    needs_review: 'needs-review',
    fail: 'blocked',
  }[String(status)] ?? '';
}

function displayStatus(status) {
  const value = String(status ?? 'unproven');
  return {
    on_track: 'ON TRACK',
    unproven: 'UNPROVEN',
    needs_review: 'NEEDS REVIEW',
    blocked: 'BLOCKED',
    fail: 'FAIL',
    pass: 'PASS',
    repaired_pass: 'REPAIRED PASS',
    skipped: 'SKIPPED',
    proven: 'PROVEN',
    not_applicable: 'NOT APPLICABLE',
  }[value] ?? value.toUpperCase();
}

function score(value) {
  return typeof value === 'number' && Number.isFinite(value) ? `${Math.round(value)}%` : 'n/a';
}

function escapeHtml(value) {
  return String(value ?? 'unproven')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
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
