#!/usr/bin/env node
import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { createInterface } from "node:readline/promises";
import { fileURLToPath } from "node:url";

const AGENTS = new Set(["codex", "claude", "cursor", "all"]);
const MODES = new Set(["preserve", "clean-runtime"]);
const VALUE_OPTIONS = new Set(["--target", "--agent", "--mode", "--bundle", "--url", "--sha256", "--timeout"]);
const BOOL_OPTIONS = new Set(["--yes", "--dry-run", "--no-hooks", "--no-postinstall"]);
const MIN_NODE_MAJOR = 18;
const MIN_BUN_VERSION = [1, 0, 0];
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

Examples:
  npx --loglevel=error -y --package github:murillodutt/tilly-engineer-skills#v0.3.94 tilly-engineer-skills add
  npx --loglevel=error -y --package github:murillodutt/tilly-engineer-skills#v0.3.94 tilly-engineer-skills add --agent all --yes
  bunx --silent --bun --package github:murillodutt/tilly-engineer-skills#v0.3.94 tilly-engineer-skills add
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
  console.error("  npx --loglevel=error -y --package github:murillodutt/tilly-engineer-skills#v0.3.94 tilly-engineer-skills add");
  console.error("  bunx --silent --bun --package github:murillodutt/tilly-engineer-skills#v0.3.94 tilly-engineer-skills add");
  return 1;
}

function resolvePython() {
  const candidates = [];
  if (process.env.PYTHON) {
    candidates.push(process.env.PYTHON);
  }
  candidates.push("python3", "python");

  for (const candidate of candidates) {
    const result = spawnSync(candidate, ["--version"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
    });
    if (result.status === 0) {
      return candidate;
    }
  }
  return null;
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
  console.log(`Finish        ${parsed.noPostinstall ? "manual setup only" : "first agent run completes setup"}`);
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
      detail: "install record and first-run setup planned",
    };
  }
  if (lock || postinstall) {
    return {
      status: "READY",
      detail: "install record + first-run setup",
    };
  }
  return {
    status: "READY",
    detail: "local state checked",
  };
}

function printStep(number, label, status, detail) {
  console.log(`[${number}/5] ${label.padEnd(18)} ${String(status).padEnd(9)} ${detail}`);
}

function renderInstallSummary(summary, parsed) {
  const target = summary?.target || resolve(parsed.target);
  const version = summary?.version || "unknown";
  const stage = formatStage(summary);
  const apply = formatApply(summary);
  const state = formatState(summary);
  const dryRun = summary?.status === "DRY-RUN" || parsed.dryRun;
  const hooksStatus = dryRun ? "DRY-RUN" : "READY";

  console.log(`\nTES Installer ${version}\n`);
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
    dryRun ? "Rerun without --dry-run to install" : "Reopen your agent or run /tes-setup",
  );
  console.log("");
  console.log(dryRun ? "Dry run complete. No files were written." : "TES is ready for this project.");
}

function renderFailure(summary, output) {
  console.error("\nTES Installer failed\n");
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
  if (!python) {
    return fail("Python 3 is required. Install Python 3 or set PYTHON=/path/to/python3.");
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

  console.log("Installing TES...");
  const result = spawnSync(python, args, {
    cwd: process.cwd(),
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });

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
