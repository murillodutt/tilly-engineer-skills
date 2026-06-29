// SPEC-009 Execution Thermometer integration contract.
// Validates that the execute-loop runner generates local reports after loop
// close or honest stop while keeping Thermometer/report/share states separate
// from Goal Maestro execution stop states.
//
//   node scripts/execution-thermometer-integration.mjs references/execution-loop-runner.md templates/maestral-goal-prompt.template.md fixture.json

import { runChecks, readText } from './lib/harness.mjs';

const [runnerPath, templatePath, fixturePath] = process.argv.slice(2);

if (!runnerPath || !templatePath || !fixturePath || process.argv.length !== 5) {
  console.error('usage: node scripts/execution-thermometer-integration.mjs <execution-loop-runner.md> <maestral-goal-prompt.template.md> <state-fixture.json>');
  process.exit(2);
}

let fixture;
try {
  fixture = JSON.parse(readText(fixturePath));
} catch (error) {
  console.error(`state fixture JSON invalid: ${error.message}`);
  process.exit(2);
}

const runner = readText(runnerPath);
const template = readText(templatePath);
const lifecycleBlock = extractBetween(runner, 'Use these states:', 'Stop or branch with:');
const before = fixture.before ?? {};
const after = fixture.after ?? {};
const report = after.report_generation ?? {};

const REPORT_STATUS = new Set([
  'generation_pending',
  'local_package_ready',
  'local_package_blocked',
  'share_blocked',
  'shared_draft_pr',
]);
const SHARE_STATUS = new Set([
  'not_requested',
  'not_gold',
  'proposed_gold',
  'declined',
  'approved_local_export',
  'draft_pr_opened',
  'blocked_by_sanitization',
  'blocked_by_missing_destination',
  'blocked_by_owner_decision',
  'blocked_by_github_auth',
]);

runChecks('SPEC-009 execution-thermometer-integration', [
  {
    name: 'runner declares Execution Thermometer Hook',
    pass: runner.includes('## Execution Thermometer Hook'),
  },
  {
    name: 'runner makes local generation default/always-on after loop close or honest stop',
    pass: runner.includes('default/always-on') && /after loop\s+close or honest stop/.test(runner),
  },
  {
    name: 'runner points to local package generator',
    pass: runner.includes('execution-thermometer-package.mjs'),
  },
  {
    name: 'runner keeps report failure from rewriting execution stop state',
    pass: runner.includes('report generation failure') && runner.includes('must not rewrite Goal Maestro execution stop states'),
  },
  {
    name: 'template carries Execution Thermometer Hook',
    pass: template.includes('Execution Thermometer Hook:') && template.includes('default/always-on local report/package generation'),
  },
  {
    name: 'existing execution-loop lifecycle remains free of Thermometer states',
    pass: lifecycleBlock.includes('ready_goal_prompt') &&
      lifecycleBlock.includes('execution_loop_complete') &&
      !/thermometer|report_status|share_gate|local_package/i.test(lifecycleBlock),
  },
  {
    name: 'fixture keeps Goal Maestro execution state unchanged',
    pass: before.goal_maestro_execution_state === after.goal_maestro_execution_state,
    detail: before.goal_maestro_execution_state === after.goal_maestro_execution_state ? undefined : `${before.goal_maestro_execution_state} -> ${after.goal_maestro_execution_state}`,
  },
  {
    name: 'fixture uses Thermometer report status namespace',
    pass: REPORT_STATUS.has(after.thermometer_report_status),
    detail: REPORT_STATUS.has(after.thermometer_report_status) ? undefined : `invalid report status ${after.thermometer_report_status}`,
  },
  {
    name: 'fixture uses Share Gate status namespace',
    pass: SHARE_STATUS.has(after.share_gate_status),
    detail: SHARE_STATUS.has(after.share_gate_status) ? undefined : `invalid share status ${after.share_gate_status}`,
  },
  {
    name: 'optional report failure remains sidecar unless reporting is required',
    pass: report.required === true || report.status === 'pass' || before.goal_maestro_execution_state === after.goal_maestro_execution_state,
  },
]);

function extractBetween(text, start, end) {
  const startIndex = text.indexOf(start);
  if (startIndex === -1) {
    return '';
  }
  const endIndex = text.indexOf(end, startIndex + start.length);
  return endIndex === -1 ? text.slice(startIndex) : text.slice(startIndex, endIndex);
}
