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
  const latestLoopId = latest.loop_id ?? loops.at(-1)?.loop_id ?? 'L1';
  const snapshot = JSON.stringify({ identity, metrics }, null, 2);
  const title = `Goal Maestro Execution Thermometer - ${identity.run_id}`;
  const fiveSignals = Array.isArray(metrics.five_signals) ? metrics.five_signals : [];
  const specResults = Array.isArray(metrics.spec_results) ? metrics.spec_results : [];
  const sources = Array.isArray(metrics.sources) ? metrics.sources : [];
  const unprovenMetrics = Array.isArray(metrics.unproven_metrics) ? metrics.unproven_metrics : [];
  const overall = averageScore(fiveSignals.map((signal) => signal.score));

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(title)}</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #172033;
      --muted: #5b6475;
      --quiet: #7b8494;
      --line: #d8dee8;
      --line-strong: #aeb8c8;
      --paper: #ffffff;
      --surface: #f6f8fb;
      --surface-strong: #eef3f8;
      --accent: #0f766e;
      --accent-ink: #0b4f4a;
      --green: #15803d;
      --amber: #b45309;
      --red: #b91c1c;
      --shadow: 0 18px 46px rgba(23, 32, 51, 0.08);
    }
    * { box-sizing: border-box; }
    html { background: #e9edf3; }
    body {
      margin: 0;
      font: 14px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: linear-gradient(180deg, #f8fafc 0, #eef2f6 310px, #e9edf3 310px);
    }
    h1, h2, h3, p { margin: 0; }
    h1 { font-size: 30px; line-height: 1.08; letter-spacing: 0; }
    h2 { font-size: 17px; line-height: 1.2; letter-spacing: 0; }
    h3 { font-size: 15px; line-height: 1.2; letter-spacing: 0; }
    a { color: var(--accent-ink); text-decoration-thickness: 1px; text-underline-offset: 3px; }
    code { overflow-wrap: anywhere; font-size: 0.94em; }
    table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    th, td { border-bottom: 1px solid var(--line); padding: 10px 12px; text-align: left; vertical-align: top; }
    th { background: var(--surface-strong); color: #2d3748; font-size: 12px; font-weight: 700; }
    td { background: var(--paper); }
    .report-shell { max-width: 1280px; margin: 0 auto; padding: 28px; }
    .report-hero {
      display: grid;
      grid-template-columns: minmax(280px, 1fr) minmax(420px, 0.95fr);
      gap: 28px;
      align-items: start;
      padding: 28px;
      border: 1px solid var(--line);
      background: var(--paper);
      box-shadow: var(--shadow);
    }
    .eyebrow { color: var(--accent-ink); font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
    .subtitle { color: var(--muted); margin-top: 10px; max-width: 66ch; }
    .hero-metrics { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border: 1px solid var(--line); }
    .hero-metric { min-width: 0; padding: 14px; border-right: 1px solid var(--line); border-bottom: 1px solid var(--line); background: #fbfcfe; }
    .hero-metric:nth-child(3n) { border-right: 0; }
    .hero-metric:nth-last-child(-n + 3) { border-bottom: 0; }
    .metric-label { color: var(--quiet); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
    .metric-value { display: block; margin-top: 6px; color: var(--ink); font-size: 15px; font-weight: 750; overflow-wrap: anywhere; }
    .meta-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 18px; }
    .meta-item { min-width: 0; border-top: 1px solid var(--line); padding-top: 10px; }
    .section { margin-top: 20px; border: 1px solid var(--line); background: var(--paper); box-shadow: 0 10px 26px rgba(23, 32, 51, 0.05); }
    .section-header { display: flex; justify-content: space-between; gap: 16px; align-items: baseline; padding: 16px 18px; border-bottom: 1px solid var(--line); background: #fbfcfe; }
    .section-note { color: var(--muted); font-size: 12px; }
    .section-body { padding: 18px; }
    .signal-grid { display: grid; grid-template-columns: repeat(5, minmax(140px, 1fr)); gap: 12px; }
    .signal-tile { min-width: 0; border: 1px solid var(--line); background: var(--surface); padding: 14px; }
    .signal-name { color: var(--muted); font-size: 12px; font-weight: 750; }
    .signal-score { display: block; margin: 6px 0 8px; font-size: 26px; line-height: 1; font-weight: 800; }
    .signal-notes { color: var(--muted); font-size: 12px; min-height: 34px; overflow-wrap: anywhere; }
    .table-scroll { width: 100%; overflow-x: auto; border: 1px solid var(--line); }
    .table-scroll table { min-width: 880px; }
    .loop-table th:nth-child(1), .loop-table td:nth-child(1) { width: 120px; }
    .loop-table th:nth-child(2), .loop-table td:nth-child(2) { width: 172px; }
    .loop-table th:nth-child(n+3):nth-child(-n+8), .loop-table td:nth-child(n+3):nth-child(-n+8) { width: 96px; }
    .loop-table th:nth-child(9), .loop-table td:nth-child(9) { width: 130px; }
    .loop-link { font-weight: 800; }
    .selected-loop-frame { border: 2px solid var(--accent); background: #f8fffd; }
    .loop-detail-pane { display: none; padding: 18px; }
    .loop-detail-pane.is-latest { display: block; }
    .loop-detail-pane:target { display: block; }
    body:has(.loop-detail-pane:target) .loop-detail-pane.is-latest:not(:target) { display: none; }
    .pane-head { display: grid; grid-template-columns: minmax(260px, 1fr) auto; gap: 18px; align-items: start; padding-bottom: 16px; border-bottom: 1px solid var(--line); }
    .pane-title { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .pane-summary { color: var(--muted); margin-top: 8px; max-width: 86ch; }
    .detail-grid { display: grid; grid-template-columns: minmax(260px, 0.74fr) minmax(420px, 1.26fr); gap: 16px; margin-top: 16px; }
    .report-block { min-width: 0; border: 1px solid var(--line); background: var(--paper); }
    .report-block.wide { grid-column: 1 / -1; }
    .block-title { padding: 12px 14px; border-bottom: 1px solid var(--line); background: var(--surface); font-weight: 800; }
    .block-body { padding: 14px; }
    .key-value { display: grid; grid-template-columns: 132px minmax(0, 1fr); gap: 8px 14px; }
    .key { color: var(--muted); font-size: 12px; font-weight: 750; }
    .value { min-width: 0; overflow-wrap: anywhere; }
    .status-pill { display: inline-flex; align-items: center; min-height: 24px; padding: 3px 8px; border: 1px solid var(--line-strong); background: var(--surface); color: var(--ink); font-size: 12px; font-weight: 800; white-space: nowrap; }
    .status-on-track, .status-pass, .status-proven, .status-green { color: var(--green); background: #edfdf4; border-color: #a7e3bf; }
    .status-unproven, .status-needs-review, .status-skipped, .status-not-applicable { color: var(--amber); background: #fff7ed; border-color: #fed7aa; }
    .status-blocked, .status-fail { color: var(--red); background: #fef2f2; border-color: #fecaca; }
    .score-strong { color: var(--green); font-weight: 800; }
    .score-warn { color: var(--amber); font-weight: 800; }
    .score-risk { color: var(--red); font-weight: 800; }
    .empty-state { color: var(--muted); padding: 12px 0; }
    .source-list { margin: 0; padding-left: 18px; }
    .snapshot { white-space: pre-wrap; overflow-wrap: anywhere; }
    @media print {
      html, body { background: white; }
      a[href]::after { content: ""; }
      .report-shell { max-width: none; padding: 0; }
      .report-hero, .section { box-shadow: none; }
      .loop-detail-pane { display: block !important; break-inside: avoid; page-break-inside: avoid; }
      .table-scroll { overflow: visible; }
      .selected-loop-frame { border-color: var(--line); }
    }
    @media (max-width: 920px) {
      .report-shell { padding: 14px; }
      .report-hero, .pane-head, .detail-grid { grid-template-columns: 1fr; }
      .hero-metrics, .meta-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .signal-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 560px) {
      h1 { font-size: 24px; }
      .hero-metrics, .meta-grid, .signal-grid { grid-template-columns: 1fr; }
      .hero-metric { border-right: 0; }
      .hero-metric:nth-last-child(-n + 3) { border-bottom: 1px solid var(--line); }
      .hero-metric:last-child { border-bottom: 0; }
      .key-value { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main class="report-shell">
    <header class="report-hero">
      <div>
        <p class="eyebrow">Static HTML Evidence Report</p>
        <h1>Goal Maestro Execution Thermometer</h1>
        <p class="subtitle">Local, offline execution evidence for run <code>${escapeHtml(identity.run_id)}</code>.</p>
        <div class="meta-grid">
          ${metaItem('Project', identity.project_id)}
          ${metaItem('Series', identity.series_id)}
          ${metaItem('Harness', `${identity.harness?.name ?? 'unproven'} ${identity.harness?.version ?? ''}`.trim())}
          ${metaItem('Generated', identity.generated_at_utc)}
        </div>
      </div>
      <div class="hero-metrics">
        ${heroMetric('Overall', percent(overall))}
        ${heroMetric('Loops', loops.length)}
        ${heroMetric('SPECs', specResults.length)}
        ${heroMetric('Evidence', sources.length)}
        ${heroMetric('Unproven', unprovenMetrics.length)}
        ${heroMetric('Report', displayStatus(identity.report_status))}
      </div>
    </header>
    <section class="section" id="five-signals">
      <div class="section-header"><h2>Five Signals</h2><span class="section-note">Latest execution thermometer</span></div>
      <div class="section-body">${renderSignals(fiveSignals)}</div>
    </section>
    <section class="section" id="loop-index">
      <div class="section-header"><h2>Accumulated Loops Index</h2><span class="section-note">Selected anchor: <code>#${escapeHtml(loopAnchor(latestLoopId))}</code></span></div>
      <div class="section-body">${renderLoopIndex(loops)}</div>
    </section>
    <section class="section selected-loop-frame" id="selected-loop-detail">
      <div class="section-header"><h2>Selected Loop Detail</h2><span class="section-note">Screen shows the selected anchor; print expands every loop.</span></div>
      ${renderLoopPanels(loops, metrics, identity, latestLoopId)}
    </section>
    <section class="section" id="model-harness">
      <div class="section-header"><h2>Model And Harness</h2><span class="section-note">Run identity and source files</span></div>
      <div class="section-body">
        <div class="detail-grid">
          <div class="report-block">
            <div class="block-title">Execution Identity</div>
            <div class="block-body key-value">
              ${kv('Harness command', identity.harness?.command)}
              ${kv('Schema version', identity.schema_version)}
              ${kv('Model', `${identity.model?.provider ?? 'unproven'}/${identity.model?.identity ?? 'unproven'}`)}
              ${kv('Reasoning profile', identity.model?.reasoning_profile)}
              ${kv('Effort multiplier', identity.model?.effort_multiplier)}
              ${kv('Share gate', metrics.final_status?.share_gate_status)}
            </div>
          </div>
          <div class="report-block">
            <div class="block-title">Source Files</div>
            <div class="block-body">
              <ul class="source-list">
                <li><code>exec_identity.yaml</code></li>
                <li><code>exec_metrics.json</code></li>
                <li>Ledger hash: <code>${escapeHtml(identity.ledger?.hash)}</code></li>
                <li>Extraction manifest hash: <code>${escapeHtml(identity.ledger?.extraction_hash)}</code></li>
              </ul>
            </div>
          </div>
          <div class="report-block wide" id="normalized-snapshot-section">
            <div class="block-title">Embedded Normalized Snapshot</div>
            <div class="block-body">
              <p class="section-note">Escaped at generation time; the report performs no runtime YAML, JSON, file, or network reads.</p>
              <pre id="normalized-snapshot" class="snapshot" hidden>${escapeHtml(snapshot)}</pre>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</body>
</html>
`;
}

function renderSignals(signals) {
  if (signals.length === 0) {
    return '<p class="empty-state">No signal rows recorded.</p>';
  }
  return `<div class="signal-grid">
${signals.map((signal) => `          <div class="signal-tile">
            <div class="signal-name">${escapeHtml(signal.signal)}</div>
            <span class="signal-score ${scoreTone(signal.score)}">${score(signal.score)}</span>
            <span class="status-pill ${statusClass(signal.status)}">${escapeHtml(displayStatus(signal.status))}</span>
            <p class="signal-notes">${escapeHtml(signal.notes)}</p>
          </div>`).join('\n')}
        </div>`;
}

function renderLoopIndex(loops) {
  if (loops.length === 0) {
    return '<p class="empty-state">No loops recorded.</p>';
  }
  return `<div class="table-scroll">
          <table class="loop-table">
            <thead><tr><th>Loop</th><th>Time UTC</th><th>Delivery</th><th>Fidelity</th><th>Proof</th><th>Efficiency</th><th>Protection</th><th>Overall</th><th>Status</th></tr></thead>
            <tbody>
${loops.map((loop) => {
  const scores = loop.scores ?? {};
  return `              <tr>
                <td><a class="loop-link" href="#${escapeHtml(loopAnchor(loop.loop_id))}">${escapeHtml(loop.label)}</a></td>
                <td><code>${escapeHtml(loop.ended_at_utc ?? loop.started_at_utc)}</code></td>
                <td>${score(scores.delivery)}</td>
                <td>${score(scores.fidelity)}</td>
                <td>${score(scores.proof)}</td>
                <td>${score(scores.efficiency)}</td>
                <td>${score(scores.protection)}</td>
                <td>${score(averageScore(Object.values(scores)))}</td>
                <td><span class="status-pill ${statusClass(loop.status)}">${escapeHtml(displayStatus(loop.status))}</span></td>
              </tr>`;
}).join('\n')}
            </tbody>
          </table>
        </div>`;
}

function renderLoopPanels(loops, metrics, identity, latestLoopId) {
  if (loops.length === 0) {
    return '<div class="section-body"><p class="empty-state">No loop detail recorded.</p></div>';
  }
  return loops.map((loop) => renderLoopPanel(loop, metrics, identity, loop.loop_id === latestLoopId)).join('\n');
}

function renderLoopPanel(loop, metrics, identity, isLatest) {
  const evidenceRefs = loopEvidenceRefs(loop, metrics.spec_results ?? []);
  const specs = filterSpecsForLoop(metrics.spec_results ?? [], loop);
  const sources = filterSourcesByEvidence(metrics.sources ?? [], evidenceRefs);
  const lens = filterRowsByEvidence(metrics.lens_results ?? [], evidenceRefs);
  const latestLoopId = metrics.loop_summary?.latest_loop_id ?? metrics.latest_loop?.loop_id;
  const unproven = filterRowsByEvidence(metrics.unproven_metrics ?? [], evidenceRefs, { keepRowsWithoutEvidence: loop.loop_id === latestLoopId });

  return `<article id="${escapeHtml(loopAnchor(loop.loop_id))}" class="loop-detail-pane${isLatest ? ' is-latest' : ''}">
        <div class="pane-head">
          <div>
            <div class="pane-title"><h3>${escapeHtml(loop.label)}</h3><span class="status-pill ${statusClass(loop.status)}">${escapeHtml(displayStatus(loop.status))}</span></div>
            <p class="pane-summary">${escapeHtml(loop.summary)}</p>
          </div>
          <div class="key-value">
            ${kv('Started', loop.started_at_utc)}
            ${kv('Ended', loop.ended_at_utc)}
            ${kv('SPECs', (loop.spec_ids ?? []).join(', ') || 'unproven')}
            ${kv('Evidence', (loop.evidence_refs ?? []).join(', ') || 'unproven')}
          </div>
        </div>
        <div class="detail-grid">
          <div class="report-block">
            <div class="block-title">Loop Objective</div>
            <div class="block-body key-value">
              ${kv('Objective', loop.objective)}
              ${kv('Next actions', (loop.next_actions ?? []).join('; ') || 'None recorded.')}
              ${kv('Goal state', metrics.final_status?.goal_maestro_execution_state)}
              ${kv('Report state', metrics.final_status?.thermometer_report_status)}
            </div>
          </div>
          <div class="report-block">
            <div class="block-title">SPEC Results</div>
            <div class="block-body">${renderSpecResults(specs)}</div>
          </div>
          <div class="report-block wide">
            <div class="block-title">Evidence References</div>
            <div class="block-body">${renderSources(sources)}</div>
          </div>
          <div class="report-block">
            <div class="block-title">Key Metrics</div>
            <div class="block-body">${renderMetrics(lens)}</div>
          </div>
          <div class="report-block">
            <div class="block-title">Unproven Metrics</div>
            <div class="block-body">${renderMetrics(unproven)}</div>
          </div>
          <div class="report-block wide">
            <div class="block-title">Model And Harness For This Loop</div>
            <div class="block-body key-value">
              ${kv('Harness', `${identity.harness?.name ?? 'unproven'} ${identity.harness?.version ?? ''}`.trim())}
              ${kv('Command', identity.harness?.command)}
              ${kv('Model', `${identity.model?.provider ?? 'unproven'}/${identity.model?.identity ?? 'unproven'}`)}
              ${kv('Reasoning', identity.model?.reasoning_profile)}
            </div>
          </div>
        </div>
      </article>`;
}

function renderSpecResults(results) {
  if (results.length === 0) {
    return '<p class="empty-state">No SPEC results recorded for this loop.</p>';
  }
  return `<div class="table-scroll">
            <table>
              <thead><tr><th>SPEC</th><th>Status</th><th>Intent</th><th>Fidelity</th><th>Proof</th><th>Evidence</th><th>Notes</th></tr></thead>
              <tbody>
${results.map((result) => `                <tr><td>${escapeHtml(result.spec_id)}<br><span class="section-note">${escapeHtml(result.title)}</span></td><td><span class="status-pill ${statusClass(result.status)}">${escapeHtml(displayStatus(result.status))}</span></td><td>${score(result.intent_score)}</td><td>${score(result.fidelity_score)}</td><td>${score(result.proof_score)}</td><td>${escapeHtml((result.evidence_refs ?? []).join(', '))}</td><td>${escapeHtml(result.notes)}</td></tr>`).join('\n')}
              </tbody>
            </table>
          </div>`;
}

function renderMetrics(metrics) {
  if (metrics.length === 0) {
    return '<p class="empty-state">No rows recorded.</p>';
  }
  return `<div class="table-scroll">
            <table>
              <thead><tr><th>Name</th><th>Status</th><th>Value</th><th>Unit</th><th>Evidence</th><th>Notes</th></tr></thead>
              <tbody>
${metrics.map((metric) => `                <tr><td>${escapeHtml(metric.name)}</td><td><span class="status-pill ${statusClass(metric.status)}">${escapeHtml(displayStatus(metric.status))}</span></td><td>${escapeHtml(metric.value ?? 'n/a')}</td><td>${escapeHtml(metric.unit)}</td><td>${escapeHtml((metric.evidence_refs ?? []).join(', '))}</td><td>${escapeHtml(metric.notes)}</td></tr>`).join('\n')}
              </tbody>
            </table>
          </div>`;
}

function renderSources(sources) {
  if (sources.length === 0) {
    return '<p class="empty-state">No evidence references recorded for this loop.</p>';
  }
  return `<div class="table-scroll">
            <table>
              <thead><tr><th>Ref</th><th>Type</th><th>Description</th><th>Source</th><th>Path</th><th>Hash</th></tr></thead>
              <tbody>
${sources.map((source) => `                <tr><td>${escapeHtml(source.ref)}</td><td>${escapeHtml(source.type)}</td><td>${escapeHtml(source.description)}</td><td>${escapeHtml(source.source)}</td><td><code>${escapeHtml(source.path)}</code></td><td><code>${escapeHtml(source.hash)}</code></td></tr>`).join('\n')}
              </tbody>
            </table>
          </div>`;
}

function heroMetric(label, value) {
  return `<div class="hero-metric"><span class="metric-label">${escapeHtml(label)}</span><span class="metric-value">${escapeHtml(value)}</span></div>`;
}

function metaItem(label, value) {
  return `<div class="meta-item"><span class="metric-label">${escapeHtml(label)}</span><span class="metric-value"><code>${escapeHtml(value)}</code></span></div>`;
}

function kv(label, value) {
  return `<div class="key">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div>`;
}

function loopAnchor(loopId) {
  return `loop-${String(loopId ?? 'unproven').replace(/[^A-Za-z0-9_-]/g, '-')}`;
}

function loopEvidenceRefs(loop, specs) {
  const refs = new Set(loop.evidence_refs ?? []);
  for (const spec of filterSpecsForLoop(specs, loop)) {
    for (const ref of spec.evidence_refs ?? []) {
      refs.add(ref);
    }
  }
  return refs;
}

function filterSpecsForLoop(specs, loop) {
  const ids = new Set(loop.spec_ids ?? []);
  if (ids.size === 0) {
    return [];
  }
  return specs.filter((spec) => ids.has(spec.spec_id));
}

function filterRowsByEvidence(rows, evidenceRefs, options = {}) {
  return rows.filter((row) => {
    const refs = row.evidence_refs ?? [];
    if (refs.length === 0) {
      return Boolean(options.keepRowsWithoutEvidence);
    }
    return refs.some((ref) => evidenceRefs.has(ref));
  });
}

function filterSourcesByEvidence(sources, evidenceRefs) {
  return sources.filter((source) => evidenceRefs.has(source.ref));
}

function averageScore(values) {
  const valid = values.filter((value) => typeof value === 'number' && Number.isFinite(value));
  if (valid.length === 0) {
    return null;
  }
  return valid.reduce((sum, value) => sum + value, 0) / valid.length;
}

function percent(value) {
  return typeof value === 'number' && Number.isFinite(value) ? `${Math.round(value)}%` : 'n/a';
}

function scoreTone(value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return 'score-warn';
  }
  if (value >= 90) {
    return 'score-strong';
  }
  if (value >= 70) {
    return 'score-warn';
  }
  return 'score-risk';
}

function validateHtml(html, expectedLoop) {
  const findings = [];
  for (const token of [
    '<!doctype html>',
    'class="report-shell"',
    'class="report-hero"',
    'class="signal-grid"',
    'id="loop-index"',
    'id="selected-loop-detail"',
    'class="section selected-loop-frame"',
    'class="loop-detail-pane',
    'body:has(.loop-detail-pane:target)',
    '@media print',
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
    on_track: 'status-on-track',
    green: 'status-green',
    pass: 'status-pass',
    passed: 'status-pass',
    proven: 'status-proven',
    repaired_pass: 'status-pass',
    unproven: 'status-unproven',
    needs_review: 'status-needs-review',
    skipped: 'status-skipped',
    not_applicable: 'status-not-applicable',
    blocked: 'status-blocked',
    fail: 'status-fail',
    failed: 'status-fail',
  }[String(status)] ?? '';
}

function displayStatus(status) {
  const value = String(status ?? 'unproven');
  return {
    local_package_ready: 'LOCAL PACKAGE READY',
    not_requested: 'NOT REQUESTED',
    on_track: 'ON TRACK',
    green: 'GREEN',
    unproven: 'UNPROVEN',
    needs_review: 'NEEDS REVIEW',
    blocked: 'BLOCKED',
    fail: 'FAIL',
    failed: 'FAILED',
    pass: 'PASS',
    passed: 'PASS',
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
    if (Object.hasOwn(parent, key)) {
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
