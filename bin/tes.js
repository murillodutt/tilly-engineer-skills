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
                              Agent hooks to prepare. Defaults to all.
  --mode <preserve|clean-runtime>
                              Install mode passed to TES. Defaults to preserve.
  --yes                       Confirm writes for non-interactive installs.
  --dry-run                   Show planned installer writes without changing files.
  --bundle <path>             Use a local TES bundle.
  --url <url>                 Use a remote TES bundle.
  --sha256 <hash>             Expected hash for --url.
  --timeout <seconds>         Bundle download or postinstall timeout.
  --help                      Show this help.

Examples:
  npx -y --package github:murillodutt/tilly-engineer-skills#v0.3.87 tilly-engineer-skills add
  npx -y --prefer-online --package github:murillodutt/tilly-engineer-skills#latest tilly-engineer-skills add --agent all --yes
`);
}

function fail(message, code = 1) {
  console.error(`TES installer: ${message}`);
  return code;
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

async function confirmInstall(parsed) {
  if (parsed.yes || parsed.dryRun) {
    return true;
  }
  if (!process.stdin.isTTY) {
    console.error("TES installer: non-interactive installs require --yes.");
    return false;
  }

  const prompt = `TES will install local files in ${resolve(parsed.target)} for ${agentLabel(parsed.agent)}. Continue? [y/N] `;
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  try {
    const answer = (await rl.question(prompt)).trim().toLowerCase();
    return answer === "y" || answer === "yes";
  } catch {
    console.error("TES installer: could not read interactive confirmation. Rerun with --yes for non-interactive installs.");
    return false;
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
      detail: "lock and first-session sentinel planned",
    };
  }
  if (lock || postinstall) {
    return {
      status: "READY",
      detail: "lock + first-session sentinel",
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
  printStep(1, "Package stage", stage.status, stage.detail);
  printStep(2, "Runtime apply", apply.status, apply.detail);
  printStep(3, "Agent hooks", hooksStatus, formatHooks(summary?.hooks, parsed));
  printStep(4, "First session", state.status, state.detail);
  printStep(
    5,
    "Next step",
    dryRun ? "REVIEW" : "ACTION",
    dryRun ? "Rerun without --dry-run to install" : "Reopen your agent or run /tes-setup",
  );
  console.log("");
  console.log(dryRun ? "Dry run complete. No files were written." : "TES is installed locally.");
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

  if (!(await confirmInstall(parsed))) {
    return fail("installation cancelled.", 130);
  }

  const passthrough = [...parsed.passthrough];
  if (!parsed.yes && !parsed.dryRun) {
    passthrough.push("--yes");
  }

  const args = [
    enginePath,
    "install",
    "--target",
    parsed.target,
    "--agent",
    parsed.agent,
    "--mode",
    parsed.mode,
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
  renderInstallSummary(summary, parsed);
  return 0;
}

process.exitCode = await main();
