// Harness LLM3 (SPEC-013) — Tool-use reachability.
// node-puro: cada tool declarada para o agente deve ter ≥1 eval case que efetivamente a
// INVOCA (não só "a tool existe"). Tool definida com zero evals que a chamam → exit≠0.
//
//   node scripts/tool-reachability.mjs <tools.json>
//
// Formato:
//   { "tools": ["search_web","get_weather"],
//     "eval_traces": [ {"case":"c1","tool_calls":["search_web"]} ] }

import { runChecks, readText } from './lib/harness.mjs';

const path = process.argv[2];
if (!path) {
  console.error('uso: node scripts/tool-reachability.mjs <tools.json>');
  process.exit(2);
}
let cfg;
try {
  cfg = JSON.parse(readText(path));
} catch (e) {
  console.error(`tools inválido: ${e.message}`);
  process.exit(2);
}

const tools = Array.isArray(cfg.tools) ? cfg.tools : [];
const traces = Array.isArray(cfg.eval_traces) ? cfg.eval_traces : [];
const invoked = new Set(traces.flatMap((t) => t.tool_calls || []));
const checks = [];

if (tools.length === 0) {
  checks.push({ name: 'tools declared', pass: false, detail: 'tools[] vazio' });
  runChecks('LLM3 tool-reachability', checks);
}

for (const tool of tools) {
  checks.push({
    name: `tool "${tool}" invoked by ≥1 eval case`,
    pass: invoked.has(tool),
    detail: invoked.has(tool) ? undefined : 'declarada mas nunca invocada num eval (inalcançável/não-testada)',
  });
}

runChecks('LLM3 tool-reachability', checks);
