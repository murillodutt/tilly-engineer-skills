// SPEC-010 Execution Thermometer documentation and installed-surface contract.
// Source mode checks public/user-facing docs plus the agent manual. Installed
// mode checks the delivered Goal Maestro skill surfaces that adopters receive.
//
//   node scripts/execution-thermometer-docs.mjs docs/i18n/tes-public.content.json docs/install/AGENT-MANUAL.md
//   node scripts/execution-thermometer-docs.mjs --installed-skill-root .agents/skills/tes-goal-maestro

import { runChecks, readText } from './lib/harness.mjs';

const args = process.argv.slice(2);
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

if (args[0] === '--installed-skill-root') {
  const skillRoot = args[1];
  if (!skillRoot || args.length !== 2) {
    console.error('usage: node scripts/execution-thermometer-docs.mjs --installed-skill-root <tes-goal-maestro-skill-root>');
    process.exit(2);
  }
  runInstalledChecks(skillRoot);
}

const [contentPath, agentManualPath] = args;

if (!contentPath || !agentManualPath || args.length !== 2) {
  console.error('usage: node scripts/execution-thermometer-docs.mjs <tes-public.content.json> <AGENT-MANUAL.md>');
  console.error('   or: node scripts/execution-thermometer-docs.mjs --installed-skill-root <tes-goal-maestro-skill-root>');
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

function runInstalledChecks(skillRoot) {
  const rootSkill = readText(`${skillRoot}/SKILL.md`);
  const runner = readText(`${skillRoot}/references/execution-loop-runner.md`);
  const template = readText(`${skillRoot}/templates/maestral-goal-prompt.template.md`);
  const packageScript = readText(`${skillRoot}/scripts/execution-thermometer-package.mjs`);
  const htmlScript = readText(`${skillRoot}/scripts/execution-thermometer-html.mjs`);
  const schemaScript = readText(`${skillRoot}/scripts/execution-thermometer-schema.mjs`);
  const extractScript = readText(`${skillRoot}/scripts/execution-thermometer-extract.mjs`);
  const installedText = [
    rootSkill,
    runner,
    template,
    packageScript,
    htmlScript,
    schemaScript,
    extractScript,
  ].join('\n');

  const installedChecks = [
    {
      name: 'installed skill names Execution Thermometer Hook',
      pass: runner.includes('## Execution Thermometer Hook') &&
        template.includes('Execution Thermometer Hook:'),
    },
    {
      name: 'installed skill declares local default sidecar after loop close or honest stop',
      pass: runner.includes('default/always-on') &&
        /after loop\s+close or honest stop/.test(runner) &&
        /sidecar evidence step/.test(runner),
    },
    {
      name: 'installed skill reads persistent ledger read-only and extracts YAML/JSON',
      pass: runner.includes('read the persistent loop ledger in read-only mode') &&
        runner.includes('execution-thermometer-extract.mjs'),
    },
    {
      name: 'installed skill builds local package and records separate Thermometer fields',
      pass: runner.includes('execution-thermometer-package.mjs') &&
        runner.includes('package path') &&
        runner.includes('manifest hash') &&
        runner.includes('Thermometer fields'),
    },
    {
      name: 'installed skill rejects network/server/dashboard behavior',
      pass: runner.includes('must not') &&
        runner.includes('fetch') &&
        runner.includes('push') &&
        runner.includes('publish') &&
        runner.includes('start a server') &&
        runner.includes('open a') &&
        runner.includes('remote share lane') &&
        runner.includes('not telemetry') &&
        runner.includes('not a dashboard') &&
        runner.includes('not a server'),
    },
    {
      name: 'installed skill keeps GitHub sharing opt-in',
      pass: runner.includes('GitHub sharing remains opt-in') &&
        runner.includes('Share Gate') &&
        runner.includes('GitHub export dry-run'),
    },
    {
      name: 'installed skill keeps Goal Maestro stop states separate',
      pass: runner.includes('must not rewrite Goal Maestro execution stop states') &&
        runner.includes('Thermometer report/share fields') &&
        template.includes('do not rewrite Goal Maestro execution stop states'),
    },
    {
      name: 'installed package script names package files',
      pass: packageFiles.every((file) => packageScript.includes(file)),
    },
    {
      name: 'installed package script declares local-only sharing boundary',
      pass: packageScript.includes('Local-first evidence package') &&
        packageScript.includes('Sharing remains opt-in') &&
        packageScript.includes('does not push, publish, fetch, or open a remote connection'),
    },
    {
      name: 'installed HTML script embeds static snapshot without runtime reads',
      pass: htmlScript.includes('Embedded Normalized Snapshot') &&
        htmlScript.includes('performs no runtime YAML, JSON, file, or network reads') &&
        htmlScript.includes('validateHtml'),
    },
    {
      name: 'installed schema preserves key report fields',
      pass: keyFields.every((field) => installedText.includes(field)),
    },
  ];

  runChecks('SPEC-010 execution-thermometer-installed-surfaces', installedChecks);
}

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
