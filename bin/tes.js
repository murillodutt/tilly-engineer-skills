#!/usr/bin/env node
import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { spawn, spawnSync } from "node:child_process";
import { createInterface } from "node:readline/promises";
import { fileURLToPath } from "node:url";

const AGENTS = new Set(["codex", "claude", "cursor", "all"]);
const MODES = new Set(["preserve", "clean-runtime"]);
const VALUE_OPTIONS = new Set(["--target", "--agent", "--mode", "--bundle", "--url", "--sha256", "--timeout"]);
const BOOL_OPTIONS = new Set(["--yes", "--dry-run", "--no-hooks", "--no-postinstall"]);
const MIN_NODE_MAJOR = 18;
const MIN_BUN_VERSION = [1, 0, 0];
const MIN_PYTHON_VERSION = [3, 11, 0];
const ANSI = {
  reset: "\x1b[0m",
  bold: "\x1b[1m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  cyan: "\x1b[36m",
};
const AGENT_CHOICES = [
  { key: "1", value: "all", label: "All agents", detail: "Codex, Claude Code, Cursor" },
  { key: "2", value: "codex", label: "Codex", detail: ".codex/config.toml" },
  { key: "3", value: "claude", label: "Claude Code", detail: ".claude/settings.json" },
  { key: "4", value: "cursor", label: "Cursor", detail: ".cursor/hooks.json" },
];
const MODE_CHOICES = [
  { key: "1", value: "preserve", label: "Standard", detail: "keep existing project files and update TES" },
  { key: "2", value: "clean-runtime", label: "Refresh TES", detail: "replace TES-managed runtime files only" },
];

const packageRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const enginePath = resolve(packageRoot, "scripts", "tes_install.py");

function supportsColor() {
  return Boolean(process.stdout.isTTY) && !process.env.NO_COLOR && process.env.TERM !== "dumb";
}

function color(text, ...codes) {
  if (!supportsColor()) {
    return text;
  }
  return `${codes.join("")}${text}${ANSI.reset}`;
}

function statusColor(status, text) {
  const value = String(status || "");
  if (["STAGED", "APPLIED", "CLEAN_APPLIED", "READY", "PASS"].includes(value)) {
    return color(text, ANSI.green);
  }
  if (["ACTION", "REVIEW", "DRY-RUN"].includes(value)) {
    return color(text, ANSI.cyan);
  }
  if (["NEEDS_REVIEW", "FAIL", "FAILED"].includes(value)) {
    return color(text, ANSI.red);
  }
  return text;
}

function printHelp() {
  console.log(`Tilly Engineer Skills installer

Usage:
  tilly-engineer-skills add [options]
  tilly-engineer-skills install [options]

Options:
  --target <path>             Target project. Defaults to the current directory.
  --agent <codex|claude|cursor|all>
                              Agent startup support to prepare. Defaults to all.
  --mode <preserve|clean-runtime>
                              Installation style. Defaults to preserve.
  --yes                       Confirm writes for non-interactive installs.
  --dry-run                   Show planned installer writes without changing files.
  --bundle <path>             Use a local TES bundle.
  --url <url>                 Use a remote TES bundle.
  --sha256 <hash>             Expected hash for --url.
  --timeout <seconds>         Bundle download or postinstall timeout.
  --help                      Show this help.

Runtime:
  Node.js 18+ with npm/npx, or Bun 1.0+ with bunx --bun.
  Python 3.11+ for the local TES engine and first-session oracles.

Examples:
  npx --loglevel=error -y --package github:murillodutt/tilly-engineer-skills#v0.3.106 tilly-engineer-skills add
  npx --loglevel=error -y --package github:murillodutt/tilly-engineer-skills#v0.3.106 tilly-engineer-skills add --agent all --yes
  bunx --silent --bun --package github:murillodutt/tilly-engineer-skills#v0.3.106 tilly-engineer-skills add
`);
}

function fail(message, code = 1) {
  console.error(`TES installer: ${message}`);
  return code;
}

function parseVersionParts(version) {
  return String(version || "")
    .replace(/^v/, "")
    .split(".")
    .map((part) => Number.parseInt(part, 10))
    .map((part) => (Number.isFinite(part) ? part : 0));
}

function versionAtLeast(version, minimum) {
  const current = parseVersionParts(version);
  for (let index = 0; index < minimum.length; index += 1) {
    const value = current[index] || 0;
    if (value > minimum[index]) {
      return true;
    }
    if (value < minimum[index]) {
      return false;
    }
  }
  return true;
}

function detectRuntime() {
  const bunVersion = process.versions?.bun || globalThis.Bun?.version || null;
  if (bunVersion) {
    return {
      name: "Bun",
      version: bunVersion,
      supported: versionAtLeast(bunVersion, MIN_BUN_VERSION),
      minimum: "1.0.0",
    };
  }
  const nodeVersion = process.versions?.node || null;
  if (nodeVersion) {
    const major = parseVersionParts(nodeVersion)[0] || 0;
    return {
      name: "Node.js",
      version: nodeVersion,
      supported: major >= MIN_NODE_MAJOR,
      minimum: `${MIN_NODE_MAJOR}.0.0`,
    };
  }
  return {
    name: "unknown JavaScript runtime",
    version: null,
    supported: false,
    minimum: `Node.js ${MIN_NODE_MAJOR}+ or Bun ${MIN_BUN_VERSION.join(".")}+`,
  };
}

function runtimeFailure(runtime) {
  console.error("TES installer: unsupported JavaScript runtime.");
  console.error(`Detected: ${runtime.version ? `${runtime.name} ${runtime.version}` : runtime.name}.`);
  console.error(`Required: Node.js ${MIN_NODE_MAJOR}+ or Bun ${MIN_BUN_VERSION.join(".")}+.`);
  console.error("");
  console.error("Install one runtime, then rerun the installer:");
  console.error("  Node.js LTS: https://nodejs.org/en/download");
  console.error("  Bun: https://bun.sh/docs/installation");
  console.error("");
  console.error("Commands:");
  console.error("  npx --loglevel=error -y --package github:murillodutt/tilly-engineer-skills#v0.3.106 tilly-engineer-skills add");
  console.error("  bunx --silent --bun --package github:murillodutt/tilly-engineer-skills#v0.3.106 tilly-engineer-skills add");
  return 1;
}

function inspectPython(candidate) {
  const result = spawnSync(candidate, [
    "-c",
    [
      "import json, sys",
      "payload = {\"executable\": sys.executable, \"version\": \".\".join(str(part) for part in sys.version_info[:3])}",
      "try:",
      "    import tomllib",
      "    payload[\"tomllib\"] = True",
      "except Exception:",
      "    payload[\"tomllib\"] = False",
      "print(json.dumps(payload))",
    ].join("\n"),
  ], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });
  if (result.status !== 0) {
    return {
      candidate,
      found: false,
      supported: false,
      detail: String(result.stderr || result.stdout || "").trim(),
    };
  }
  try {
    const payload = JSON.parse(String(result.stdout || "").trim());
    const supported = versionAtLeast(payload.version, MIN_PYTHON_VERSION) && payload.tomllib === true;
    return {
      candidate,
      found: true,
      supported,
      executable: payload.executable || candidate,
      version: payload.version || "unknown",
      detail: supported ? "ok" : "Python 3.11+ with tomllib is required",
    };
  } catch (error) {
    return {
      candidate,
      found: true,
      supported: false,
      detail: `could not inspect Python runtime: ${error.message}`,
    };
  }
}

function resolvePython() {
  const candidates = [];
  if (process.env.PYTHON) {
    candidates.push(process.env.PYTHON);
  }
  candidates.push("python3", "python");

  const seen = [];
  const uniqueCandidates = [...new Set(candidates.filter(Boolean))];
  for (const candidate of uniqueCandidates) {
    const inspected = inspectPython(candidate);
    seen.push(inspected);
    if (inspected.supported) {
      return {
        command: candidate,
        executable: inspected.executable,
        version: inspected.version,
        seen,
      };
    }
  }
  return { command: null, executable: null, version: null, seen };
}

function pythonFailure(resolution) {
  console.error("TES installer: Python 3.11+ is required for TES local oracles.");
  const seen = Array.isArray(resolution?.seen) ? resolution.seen : [];
  const inspected = seen.filter((item) => item.found);
  if (inspected.length > 0) {
    console.error("Detected:");
    for (const item of inspected) {
      console.error(`  ${item.candidate}: Python ${item.version || "unknown"} (${item.detail})`);
    }
  } else {
    console.error("Detected: no Python runtime on PATH.");
  }
  console.error("");
  console.error("Install Python 3.11+ or set PYTHON=/path/to/python3.11, then rerun TES.");
  return 1;
}

function parse(argv) {
  if (argv.length === 0 || argv.includes("--help") || argv[0] === "help") {
    return { help: true };
  }

  const command = argv[0];
  if (!["add", "install"].includes(command)) {
    return { error: `unknown command "${command}". Use "add" or "install".` };
  }

  const options = {
    command,
    target: process.cwd(),
    agent: "all",
    mode: "preserve",
    yes: false,
    dryRun: false,
    noHooks: false,
    noPostinstall: false,
    passthrough: [],
  };

  for (let index = 1; index < argv.length; index += 1) {
    const item = argv[index];
    if (BOOL_OPTIONS.has(item)) {
      if (item === "--yes") {
        options.yes = true;
      }
      if (item === "--dry-run") {
        options.dryRun = true;
      }
      if (item === "--no-hooks") {
        options.noHooks = true;
      }
      if (item === "--no-postinstall") {
        options.noPostinstall = true;
      }
      options.passthrough.push(item);
      continue;
    }
    if (!VALUE_OPTIONS.has(item)) {
      return { error: `unknown option "${item}".` };
    }
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      return { error: `${item} requires a value.` };
    }
    index += 1;
    if (item === "--target") {
      options.target = value;
    } else if (item === "--agent") {
      if (!AGENTS.has(value)) {
        return { error: `--agent must be one of codex, claude, cursor, all.` };
      }
      options.agent = value;
    } else if (item === "--mode") {
      if (!MODES.has(value)) {
        return { error: `--mode must be preserve or clean-runtime.` };
      }
      options.mode = value;
    } else {
      options.passthrough.push(item, value);
    }
  }

  return options;
}

function findChoice(choices, value) {
  return choices.find((choice) => choice.value === value) || choices[0];
}

function normalizeAnswer(value) {
  return String(value || "").trim().toLowerCase();
}

async function askLine(rl, prompt, fallback) {
  const answer = await rl.question(prompt);
  const normalized = answer.trim();
  return normalized ? normalized : fallback;
}

async function askChoice(rl, title, choices, currentValue) {
  const current = findChoice(choices, currentValue);
  console.log(title);
  for (const choice of choices) {
    const marker = choice.value === current.value ? "*" : " ";
    console.log(`  ${choice.key}. ${choice.label.padEnd(14)} ${choice.detail} ${marker}`);
  }
  while (true) {
    const answer = normalizeAnswer(await rl.question(`Select [${current.key}]: `)) || current.key;
    const selected = choices.find(
      (choice) => answer === choice.key || answer === choice.value || answer === choice.label.toLowerCase(),
    );
    if (selected) {
      return selected.value;
    }
    console.log("Please choose one of the listed options.");
  }
}

function printPlan(parsed) {
  console.log("\nReview\n");
  console.log(`Project       ${resolve(parsed.target)}`);
  console.log(`Installation  ${parsed.mode === "clean-runtime" ? "refresh TES files" : "standard update"}`);
  console.log(`Agents        ${agentLabel(parsed.agent)}`);
  console.log(`Startup       ${parsed.noHooks ? "agent startup disabled" : "agent startup prepared"}`);
  console.log(`Finish        ${parsed.noPostinstall ? "manual setup only" : "wait for completion notice"}`);
}

async function configureInteractively(parsed) {
  if (parsed.yes || parsed.dryRun) {
    return { ok: true, parsed };
  }
  if (!process.stdin.isTTY) {
    console.error("TES installer: non-interactive installs require --yes.");
    return { ok: false, parsed };
  }

  const rl = createInterface({ input: process.stdin, output: process.stdout });
  try {
    console.log("\nTilly Engineer Skills\n");
    console.log("Set up local AI-agent support for this project.\n");
    parsed.target = await askLine(rl, `Target project [${resolve(parsed.target)}]: `, parsed.target);
    console.log("");
    parsed.agent = await askChoice(rl, "Choose agents", AGENT_CHOICES, parsed.agent);
    console.log("");
    parsed.mode = await askChoice(rl, "Installation style", MODE_CHOICES, parsed.mode);
    printPlan(parsed);
    const answer = normalizeAnswer(await rl.question("\nInstall TES with these settings? [Y/n] "));
    return { ok: answer === "" || answer === "y" || answer === "yes", parsed };
  } catch {
    console.error("TES installer: could not read interactive confirmation. Rerun with --yes for non-interactive installs.");
    return { ok: false, parsed };
  } finally {
    rl.close();
  }
}

function extractJson(text) {
  const start = text.indexOf("{");
  if (start === -1) {
    return null;
  }
  let depth = 0;
  let inString = false;
  let escaping = false;
  for (let index = start; index < text.length; index += 1) {
    const char = text[index];
    if (inString) {
      if (escaping) {
        escaping = false;
      } else if (char === "\\") {
        escaping = true;
      } else if (char === "\"") {
        inString = false;
      }
      continue;
    }
    if (char === "\"") {
      inString = true;
    } else if (char === "{") {
      depth += 1;
    } else if (char === "}") {
      depth -= 1;
      if (depth === 0) {
        try {
          return JSON.parse(text.slice(start, index + 1));
        } catch {
          return null;
        }
      }
    }
  }
  return null;
}

function agentLabel(agent) {
  const labels = {
    all: "Codex, Claude Code, Cursor",
    codex: "Codex",
    claude: "Claude Code",
    cursor: "Cursor",
  };
  return labels[agent] || agent;
}

function agentName(agent) {
  return agentLabel(agent).replace(", Claude Code, Cursor", "");
}

function hookActionLabel(action) {
  const labels = {
    "skip-identical": "up to date",
    create: "prepared",
    update: "updated",
    "write-text": "prepared",
    "write-json": "prepared",
    "would-create": "would prepare",
    "would-update": "would update",
    "would-write-text": "would prepare",
    "would-write-json": "would prepare",
    "skip-disabled": "disabled",
  };
  return labels[action] || String(action || "checked");
}

function formatHooks(hooks, parsed) {
  if (!Array.isArray(hooks) || hooks.length === 0) {
    return parsed.passthrough.includes("--no-hooks") ? "disabled" : "no hook changes";
  }
  return hooks.map((hook) => `${agentName(hook.agent)} ${hookActionLabel(hook.action)}`).join("; ");
}

function formatStage(summary) {
  const stage = summary?.stage || {};
  const status = stage.status || (summary?.status === "DRY-RUN" ? "DRY-RUN" : "READY");
  const parts = [];
  if (stage.stage_dir) {
    parts.push(stage.stage_dir);
  }
  if (stage.entries !== undefined) {
    parts.push(`${stage.entries} entries`);
  }
  if (stage.source) {
    parts.push(stage.source);
  }
  if (stage.action) {
    parts.push(stage.action.replaceAll("-", " "));
  }
  return { status, detail: parts.join(" | ") || "bundle resolved" };
}

function formatApply(summary) {
  const apply = summary?.apply || {};
  const status = apply.status || (summary?.status === "DRY-RUN" ? "DRY-RUN" : "READY");
  const detail = apply.installed_manifest || apply.action?.replaceAll("-", " ") || `mode ${summary?.mode || "preserve"}`;
  return { status, detail };
}

function formatState(summary) {
  const lock = summary?.lock?.action;
  const postinstall = summary?.postinstall?.action;
  if (summary?.status === "DRY-RUN") {
    return {
      status: "DRY-RUN",
      detail: "install record and first-run setup trigger planned",
    };
  }
  if (lock || postinstall) {
    return {
      status: "READY",
      detail: "install record + first-run setup trigger",
    };
  }
  return {
    status: "READY",
    detail: "local state checked",
  };
}

function printStep(number, label, status, detail) {
  const paddedStatus = String(status).padEnd(9);
  console.log(`[${number}/5] ${label.padEnd(18)} ${statusColor(status, paddedStatus)} ${detail}`);
}

function startSpinner(message) {
  if (!process.stdout.isTTY) {
    console.log(`${message}...`);
    return () => {};
  }
  const frames = ["|", "/", "-", "\\"];
  let index = 0;
  process.stdout.write(`${color(message, ANSI.bold, ANSI.cyan)} ${color(`[${frames[index]}]`, ANSI.cyan)}`);
  const timer = setInterval(() => {
    index = (index + 1) % frames.length;
    process.stdout.write(`\r${color(message, ANSI.bold, ANSI.cyan)} ${color(`[${frames[index]}]`, ANSI.cyan)}`);
  }, 120);
  return (result) => {
    clearInterval(timer);
    const suffix = result === "done" ? "done" : "failed";
    const suffixColor = result === "done" ? ANSI.green : ANSI.red;
    process.stdout.write(`\r${color(message, ANSI.bold, ANSI.cyan)} ${color(suffix, suffixColor)}${" ".repeat(8)}\n`);
  };
}

function runPythonInstaller(python, args) {
  return new Promise((resolveResult) => {
    const stopSpinner = startSpinner("Installing TES");
    let stdout = "";
    let stderr = "";
    let settled = false;
    const child = spawn(python.command, args, {
      cwd: process.cwd(),
      env: {
        ...process.env,
        TES_PYTHON: python.executable || python.command,
      },
      stdio: ["ignore", "pipe", "pipe"],
    });
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => {
      stdout += chunk;
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });
    child.on("error", (error) => {
      if (settled) {
        return;
      }
      settled = true;
      stopSpinner("failed");
      resolveResult({ status: 1, stdout, stderr: `${stderr}${String(error.message || error)}` });
    });
    child.on("close", (code) => {
      if (settled) {
        return;
      }
      settled = true;
      const status = code === null ? 1 : code;
      stopSpinner(status === 0 ? "done" : "failed");
      resolveResult({ status, stdout, stderr });
    });
  });
}

function printCompletionNotice(parsed, dryRun) {
  if (dryRun) {
    console.log("Dry run complete. No files were written.");
    return;
  }
  console.log(color("TES is ready for this project.", ANSI.bold, ANSI.green));
  if (parsed.noHooks || parsed.noPostinstall) {
    console.log(`\n${color("IMPORTANT", ANSI.bold, ANSI.yellow)}`);
    console.log("Agent startup was not fully prepared. Run /tes-init or /tes-setup inside your agent to finish setup.");
    return;
  }
  console.log(`\n${color("IMPORTANT", ANSI.bold, ANSI.yellow)}`);
  console.log("Agent follow-up is host-specific:");
  console.log("1. Codex: open Settings > Hooks for this project, then Trust and enable the Session Start hook if it is marked needs review.");
  console.log("2. Claude Code: open or reopen Claude Code, wait for the TES completion notice, then continue.");
  console.log("3. Cursor: reopen the workspace, let first-session setup complete, then run /tes-setup for the report.");
  console.log(`4. ${color("Please, run /tes-setup for the report before starting project work.", ANSI.bold, ANSI.cyan)}`);
}

function renderInstallSummary(summary, parsed) {
  const target = summary?.target || resolve(parsed.target);
  const version = summary?.version || "unknown";
  const stage = formatStage(summary);
  const apply = formatApply(summary);
  const state = formatState(summary);
  const dryRun = summary?.status === "DRY-RUN" || parsed.dryRun;
  const hooksStatus = dryRun ? "DRY-RUN" : "READY";

  console.log(`\n${color(`TES Installer ${version}`, ANSI.bold, ANSI.cyan)}\n`);
  console.log(`Target   ${target}`);
  console.log(`Mode     ${summary?.mode || parsed.mode}`);
  console.log(`Agents   ${agentLabel(summary?.agent || parsed.agent)}\n`);
  printStep(1, "Package", stage.status, stage.detail);
  printStep(2, "Runtime", apply.status, apply.detail);
  printStep(3, "Agents", hooksStatus, formatHooks(summary?.hooks, parsed));
  printStep(4, "First run", state.status, state.detail);
  printStep(
    5,
    "Next step",
    dryRun ? "REVIEW" : "ACTION",
    dryRun ? "Rerun without --dry-run to install" : "Follow platform-specific host steps",
  );
  console.log("");
  printCompletionNotice(parsed, dryRun);
}

function renderFailure(summary, output) {
  console.error(`\n${color("TES Installer failed", ANSI.bold, ANSI.red)}\n`);
  const failures = summary?.failures || summary?.stage?.failures || summary?.apply?.failures || [];
  if (Array.isArray(failures) && failures.length > 0) {
    for (const item of failures.slice(0, 8)) {
      console.error(`- ${item}`);
    }
    return;
  }
  const lines = String(output || "").split(/\r?\n/);
  for (const line of lines.filter((item) => {
    const trimmed = item.trim();
    return trimmed
      && trimmed !== "{"
      && trimmed !== "}"
      && !trimmed.startsWith("\"")
      && !trimmed.startsWith("[tes-install]");
  }).slice(0, 12)) {
    console.error(line);
  }
}

async function main() {
  const runtime = detectRuntime();
  if (!runtime.supported) {
    return runtimeFailure(runtime);
  }

  const parsed = parse(process.argv.slice(2));
  if (parsed.help) {
    printHelp();
    return 0;
  }
  if (parsed.error) {
    printHelp();
    return fail(parsed.error);
  }

  if (!existsSync(enginePath)) {
    return fail(`missing Python engine at ${enginePath}. Reinstall the TES package.`);
  }

  const python = resolvePython();
  if (!python.command) {
    return pythonFailure(python);
  }

  const configured = await configureInteractively(parsed);
  if (!configured.ok) {
    return fail("installation cancelled.", 130);
  }
  const installOptions = configured.parsed;

  const passthrough = [...installOptions.passthrough];
  if (!installOptions.yes && !installOptions.dryRun) {
    passthrough.push("--yes");
  }

  const args = [
    enginePath,
    "install",
    "--target",
    installOptions.target,
    "--agent",
    installOptions.agent,
    "--mode",
    installOptions.mode,
    ...passthrough,
  ];

  const result = await runPythonInstaller(python, args);
  const status = result.status === null ? 1 : result.status;
  const combinedOutput = `${result.stdout || ""}\n${result.stderr || ""}`;
  const summary = extractJson(combinedOutput);
  if (status !== 0) {
    renderFailure(summary, combinedOutput);
    return status;
  }

  if (!summary) {
    console.log("TES Installer");
    console.log("TES finished, but the installer summary was not returned by the Python engine.");
    return 0;
  }
  renderInstallSummary(summary, installOptions);
  return 0;
}

process.exitCode = await main();
