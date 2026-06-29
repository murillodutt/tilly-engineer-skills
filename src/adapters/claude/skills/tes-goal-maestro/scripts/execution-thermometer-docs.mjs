// SPEC-010 Execution Thermometer user documentation contract.
// Checks that public/user-facing docs describe the report as local evidence,
// not telemetry, a dashboard, or a server, and that the agent reference names
// package files, key fields, UNPROVEN semantics, and opt-in sharing approval.
//
//   node scripts/execution-thermometer-docs.mjs docs/i18n/tes-public.content.json docs/install/AGENT-MANUAL.md

import { runChecks, readText } from './lib/harness.mjs';

const [contentPath, agentManualPath] = process.argv.slice(2);

if (!contentPath || !agentManualPath || process.argv.length !== 4) {
  console.error('usage: node scripts/execution-thermometer-docs.mjs <tes-public.content.json> <AGENT-MANUAL.md>');
  process.exit(2);
}

let content;
try {
  content = JSON.parse(readText(contentPath));
} catch (error) {
  console.error(`public content JSON invalid: ${error.message}`);
  process.exit(2);
}

const report = content.sections?.report ?? {};
const agentManual = readText(agentManualPath);
const packageFiles = [
  'README.md',
  'context-receipt.md',
  'exec_identity.yaml',
  'exec_metrics.json',
  'execution-thermometer.html',
  'checksums.sha256',
];
const keyFields = [
  'project_id',
  'series_id',
  'run_id',
  'generated_at_utc',
  'report_status',
  'share.status',
  'loops',
  'spec_results',
  'five_signals',
  'unproven_metrics',
  'final_status.goal_maestro_execution_state',
  'final_status.thermometer_report_status',
  'final_status.share_gate_status',
];

const checks = [];

for (const lang of ['en', 'es', 'pt']) {
  const text = sectionText(report[lang]);
  checks.push({
    name: `manual ${lang} names Execution Thermometer`,
    pass: /Execution Thermometer/.test(text),
  });
  checks.push({
    name: `manual ${lang} describes local/offline report`,
    pass: /local|offline|abrir offline|open offline/.test(text),
  });
  checks.push({
    name: `manual ${lang} rejects telemetry/dashboard/server framing`,
    pass: /not telemetry|no telemetria|não telemetria/.test(text) &&
      /not a dashboard|no dashboard|não dashboard/.test(text) &&
      /not a server|no servidor|não servidor/.test(text),
  });
  checks.push({
    name: `manual ${lang} explains UNPROVEN`,
    pass: text.includes('UNPROVEN') && /evidence|evidencia|evidência/.test(text),
  });
  checks.push({
    name: `manual ${lang} states GitHub sharing is opt-in`,
    pass: /GitHub/.test(text) && /opt-in/.test(text),
  });
  checks.push({
    name: `manual ${lang} names approval tuple hashes`,
    pass: /payload hash/.test(text) && /manifest hash/.test(text),
  });
  for (const file of packageFiles) {
    checks.push({
      name: `manual ${lang} names ${file}`,
      pass: text.includes(file),
    });
  }
}

for (const file of packageFiles) {
  checks.push({
    name: `agent manual names package file ${file}`,
    pass: agentManual.includes(file),
  });
}
for (const field of keyFields) {
  checks.push({
    name: `agent manual names field ${field}`,
    pass: agentManual.includes(field),
  });
}
checks.push({
  name: 'agent manual says report is not telemetry/dashboard/server',
  pass: agentManual.includes('not telemetry') && agentManual.includes('not a dashboard') && agentManual.includes('not a server'),
});
checks.push({
  name: 'agent manual binds GitHub approval tuple',
  pass: agentManual.includes('run_id') &&
    agentManual.includes('destination repository') &&
    agentManual.includes('destination branch') &&
    agentManual.includes('payload hash') &&
    agentManual.includes('manifest hash'),
});

runChecks('SPEC-010 execution-thermometer-docs', checks);

function sectionText(section) {
  if (!section) {
    return '';
  }
  const blocks = Array.isArray(section.blocks) ? section.blocks : [];
  return [
    section.title,
    section.lede,
    ...blocks.flatMap((block) => {
      if (block.text) {
        return [block.text];
      }
      if (Array.isArray(block.items)) {
        return block.items.flatMap((item) => typeof item === 'string' ? [item] : [item.title, item.body]);
      }
      if (Array.isArray(block.rows)) {
        return block.rows.flat();
      }
      return [];
    }),
  ].filter(Boolean).join('\n');
}
