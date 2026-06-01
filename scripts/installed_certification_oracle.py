#!/usr/bin/env python3
"""Aggregate installed-target TES certification without hiding partial states."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

import command_trigger_oracle
import mantra_gate_adoption_oracle


VERSION = "0.3.155"
SCHEMA = "tes-installed-certification@1"
STALE_DISCIPLINE_PATH = ".agents/skills/tilly-engineer-skills/scripts/discipline_oracle.py"
CANONICAL_DISCIPLINE_PATH = ".agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py"
PARTIAL_STATUSES = {"DEGRADED", "FAIL", "PARTIAL"}
REVIEW_STATUSES = {"NEEDS_REVIEW"}
BLOCKED_STATUSES = {"BLOCKED", "BYPASS_SUSPECTED"}
OS_RESIDUE_NAMES = {".DS_Store", ".AppleDouble", ".LSOverride", "__MACOSX"}
OS_RESIDUE_PREFIXES = ("._",)
REPAIR_ROUTES = {
    "mcp_registration": "Run /tes-mcp or rerun install_mcp.py for the missing adapter, then recertify.",
    "mantra_gate_adoption": "Run /tes-doctor for Mantra Gate adoption, repair bootloader-to-owner-skill routing, then recertify.",
    "command_trigger_parity": "Regenerate installed trigger surfaces through the TES adapter/update path, then rerun command_trigger_oracle.py.",
    "quality_gates_path": "Run tes_legacy_retirement.py or tes_update.py to replace retired discipline paths, then recertify.",
    "artifact_hygiene": "Remove OS residue from package source/materialized setup surfaces, rebuild materialization if authorized, then recertify.",
    "tes_tts_runtime": "Rerun the TES installer/update from a bundle that includes .tes/bin/tes_tts_* runtime helpers and packaged TTS data, then recertify.",
}
ROOT = Path(__file__).resolve().parents[1]
TTS_SKILL_PATHS = (
    ".agents/skills/tes-tts/SKILL.md",
    ".claude/skills/tes-tts/SKILL.md",
)
TTS_RUNTIME_HELPERS = (
    "tes_tts_runtime.py",
    "tes_tts_runtime_adapter.py",
    "tes_tts_runtime_classifier.py",
    "tes_tts_runtime_types.py",
    "tes_tts_runtime_verbalizer.py",
    "tes_tts_omnivoice_direct_kernel.py",
    "tes_tts_omnivoice_provider.py",
    "tes_tts_omnivoice_runtime_support.py",
)
TTS_RUNTIME_DATA_FILES = (
    "ptbr-lexical-sample.jsonl",
    "pronunciation-catalog-fixtures.json",
    "runtime-latency-fixtures.json",
    "omnivoice-provider-cases.json",
    "live-session-utterance-fixtures.json",
)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def is_os_residue(path: Path) -> bool:
    return any(part in OS_RESIDUE_NAMES or part.startswith(OS_RESIDUE_PREFIXES) for part in path.parts)


def status_from_findings(findings: list[dict[str, Any]]) -> str:
    statuses = {str(item.get("status") or "UNKNOWN") for item in findings}
    if statuses & BLOCKED_STATUSES:
        return "BLOCKED"
    if statuses & REVIEW_STATUSES:
        return "NEEDS_REVIEW"
    if statuses & PARTIAL_STATUSES:
        return "PARTIAL"
    return "PASS"


def mcp_registration(target: Path) -> dict[str, Any]:
    failures: list[str] = []
    configs: list[dict[str, str]] = []
    codex = target / ".codex/config.toml"
    if codex.exists() and "[mcp_servers.tes-cortex]" in codex.read_text(encoding="utf-8", errors="ignore"):
        configs.append({"adapter": "codex", "path": ".codex/config.toml", "status": "PASS"})
    elif codex.exists():
        failures.append(".codex/config.toml missing tes-cortex")
        configs.append({"adapter": "codex", "path": ".codex/config.toml", "status": "FAIL"})

    for adapter, relpath, key in (
        ("claude", ".mcp.json", "mcpServers"),
        ("cursor", ".cursor/mcp.json", "mcpServers"),
    ):
        path = target / relpath
        if not path.exists():
            continue
        data = read_json(path)
        servers = data.get(key) if isinstance(data.get(key), dict) else {}
        if "tes-cortex" in servers:
            configs.append({"adapter": adapter, "path": relpath, "status": "PASS"})
        else:
            failures.append(f"{relpath} missing tes-cortex")
            configs.append({"adapter": adapter, "path": relpath, "status": "FAIL"})

    vscode = target / ".vscode/mcp.json"
    if vscode.exists():
        configs.append({"adapter": "vscode", "path": ".vscode/mcp.json", "status": "EXPLICIT"})

    return {
        "status": "FAIL" if failures else "PASS",
        "configs": configs,
        "failures": failures,
    }


def quality_gates_path_status(target: Path) -> dict[str, Any]:
    path = target / "docs/agents/QUALITY-GATES.md"
    if not path.exists():
        return {"status": "NOT_APPLIED", "path": "docs/agents/QUALITY-GATES.md", "failures": []}
    text = path.read_text(encoding="utf-8", errors="ignore")
    failures: list[str] = []
    if STALE_DISCIPLINE_PATH in text:
        failures.append(f"stale discipline oracle path present: {STALE_DISCIPLINE_PATH}")
    if "discipline_oracle.py" in text and CANONICAL_DISCIPLINE_PATH not in text:
        failures.append(f"canonical discipline oracle path missing: {CANONICAL_DISCIPLINE_PATH}")
    return {
        "status": "FAIL" if failures else "PASS",
        "path": "docs/agents/QUALITY-GATES.md",
        "failures": failures,
    }


def artifact_hygiene(target: Path) -> dict[str, Any]:
    failures: list[str] = []
    residue: list[str] = []
    manifest = read_json(target / ".tes/manifest.json")
    for entry in manifest.get("entries", []) if isinstance(manifest.get("entries"), list) else []:
        if isinstance(entry, dict) and is_os_residue(Path(str(entry.get("path", "")))):
            residue.append(str(entry.get("path")))
    for root in (target / ".tes/setup", target / ".tes/bin"):
        if root.exists():
            residue.extend(rel(path, target) for path in root.rglob("*") if path.is_file() and is_os_residue(path.relative_to(root)))
    if residue:
        failures.extend(f"OS residue present: {path}" for path in sorted(set(residue)))
    metadata = manifest.get("metadata") if isinstance(manifest.get("metadata"), dict) else {}
    source_tree_state = str(metadata.get("source_tree_state") or "unknown")
    sealed_claim_allowed = source_tree_state in {"clean", "unknown"} and not failures
    return {
        "status": "FAIL" if failures else "PASS",
        "source_tree_state": source_tree_state,
        "sealed_claim_allowed": sealed_claim_allowed,
        "release_claim_status": "SEALED_ALLOWED" if sealed_claim_allowed else "UNSEALED_OR_NEEDS_RELEASE_GATE",
        "residue": sorted(set(residue)),
        "failures": failures,
    }


def adoption_status(target: Path) -> dict[str, Any]:
    result = mantra_gate_adoption_oracle.evaluate(target)
    return {
        "status": result.get("status"),
        "surface_health": result.get("surface_health", {}),
        "findings": result.get("findings", []),
    }


def trigger_status(target: Path) -> dict[str, Any]:
    result = command_trigger_oracle.check_installed_target(target)
    return {
        "status": result.get("status"),
        "checked": result.get("checked", []),
        "failures": result.get("failures", []),
    }


def tes_tts_skill_installed(target: Path) -> bool:
    return any((target / relpath).exists() for relpath in TTS_SKILL_PATHS)


def tes_tts_runtime_status(target: Path) -> dict[str, Any]:
    if not tes_tts_skill_installed(target):
        return {"status": "NOT_APPLIED", "failures": []}
    failures: list[str] = []
    for helper in TTS_RUNTIME_HELPERS:
        path = target / ".tes/bin" / helper
        if not path.exists():
            failures.append(f"missing TES TTS runtime helper: .tes/bin/{helper}")
    for data_file in TTS_RUNTIME_DATA_FILES:
        path = target / ".tes/bin/tes_tts_data/benchmarks/tes-tts" / data_file
        if not path.exists():
            failures.append(f"missing TES TTS runtime data: .tes/bin/tes_tts_data/benchmarks/tes-tts/{data_file}")
    if failures:
        return {"status": "FAIL", "failures": failures}

    runtime = target / ".tes/bin/tes_tts_runtime.py"
    runtime_result = subprocess.run(
        [
            sys.executable,
            str(runtime),
            "--text",
            "Leia token=abc123 e /Users/demo/tes-tts sem resumir.",
            "--locale",
            "pt-BR",
        ],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    if runtime_result.returncode != 0:
        failures.append("TES TTS runtime CLI failed")
        return {"status": "FAIL", "failures": failures, "stderr": runtime_result.stderr}
    try:
        runtime_payload = json.loads(runtime_result.stdout)
    except json.JSONDecodeError:
        failures.append("TES TTS runtime CLI did not return JSON")
        return {"status": "FAIL", "failures": failures, "stdout": runtime_result.stdout}
    if runtime_payload.get("source_text_immutable") is not True:
        failures.append("TES TTS runtime did not preserve source immutability")
    if runtime_payload.get("redaction_count") != 1:
        failures.append("TES TTS runtime did not redact the secret fixture")
    if runtime_payload.get("summary_behavior") != "none":
        failures.append("TES TTS runtime must not summarize requested text")
    if runtime_payload.get("command_execution") != "not_performed":
        failures.append("TES TTS runtime must not execute command-like text")
    if "pasta tes tts" not in str(runtime_payload.get("spoken_text") or ""):
        failures.append("TES TTS runtime did not load packaged pronunciation/path data")

    provider = target / ".tes/bin/tes_tts_omnivoice_provider.py"
    provider_result = subprocess.run(
        [sys.executable, str(provider), "status"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    if provider_result.returncode not in {0, 2}:
        failures.append(f"TES TTS OmniVoice status returned unexpected code {provider_result.returncode}")
    try:
        provider_payload = json.loads(provider_result.stdout)
    except json.JSONDecodeError:
        failures.append("TES TTS OmniVoice status did not return JSON")
        provider_payload = {}
    for key in ("allows_install", "allows_download", "allows_global_config_write"):
        if provider_payload.get(key) is not False:
            failures.append(f"TES TTS OmniVoice status must keep {key}=False")
    return {
        "status": "FAIL" if failures else "PASS",
        "runtime": {
            "version": runtime_payload.get("version"),
            "redaction_count": runtime_payload.get("redaction_count"),
            "source_text_immutable": runtime_payload.get("source_text_immutable"),
            "summary_behavior": runtime_payload.get("summary_behavior"),
            "command_execution": runtime_payload.get("command_execution"),
        },
        "provider_status": provider_payload.get("status"),
        "provider_returncode": provider_result.returncode,
        "failures": failures,
    }


def evaluate(target: Path) -> dict[str, Any]:
    target = target.expanduser().resolve()
    quality = quality_gates_path_status(target)
    hygiene = artifact_hygiene(target)
    components = {
        "mcp_registration": mcp_registration(target),
        "mantra_gate_adoption": adoption_status(target),
        "command_trigger_parity": trigger_status(target),
        "tes_tts_runtime": tes_tts_runtime_status(target),
        "quality_gates_path": quality,
        "artifact_hygiene": hygiene,
    }
    findings: list[dict[str, Any]] = []
    for name, payload in components.items():
        status = str(payload.get("status") or "UNKNOWN")
        if status in {"PASS", "OK", "NOT_APPLIED"}:
            continue
        findings.append(
            {
                "component": name,
                "status": "PARTIAL" if status in {"DEGRADED", "FAIL"} else status,
                "detail": payload.get("failures") or payload.get("findings") or payload.get("surface_health") or [],
                "repair": REPAIR_ROUTES.get(name, "Inspect this certification component and rerun installed certification."),
            }
        )
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "target": str(target),
        "status": status_from_findings(findings),
        "components": components,
        "findings": findings,
        "negative_checks": {
            "host_connected_not_inferred": True,
            "vscode_not_part_of_agent_all": not (target / ".vscode/mcp.json").exists(),
            "stale_discipline_path_absent": not quality.get("failures"),
            "os_residue_absent": not hygiene.get("residue"),
        },
    }


def all_trigger_terms() -> str:
    terms = [
        *command_trigger_oracle.PREFERRED_TRIGGERS,
        *command_trigger_oracle.COMPATIBLE_ALIASES,
        *command_trigger_oracle.NATURAL_INTENTS,
        *command_trigger_oracle.CLAUDE_INVALID_SLASH_TERMS,
    ]
    return "\n".join(terms) + "\n"


def mantra_owner_text(*, include_triggers: bool) -> str:
    text = "## Mantra Gate\n\nUse the TES Mantra Gate. [🍳 Flash-Fry]\n"
    if include_triggers:
        text += all_trigger_terms()
    return text


def write_installed_trigger_surfaces(target: Path, *, include_portuguese_goal: bool) -> None:
    text = all_trigger_terms()
    if not include_portuguese_goal:
        text = text.replace("gerar um /goal maestral\n", "")
    for relpath in command_trigger_oracle.CODEX_PROJECT_SKILLS:
        path = target / ".agents/skills" / relpath / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for relpath in command_trigger_oracle.CLAUDE_PROJECT_SKILLS:
        path = target / ".claude/skills" / relpath / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    cursor = target / ".cursor/rules/tes-guidelines.mdc"
    cursor.parent.mkdir(parents=True, exist_ok=True)
    cursor.write_text(all_trigger_terms(), encoding="utf-8")


def source_tts_helper(helper: str) -> Path:
    for candidate in (ROOT / "scripts" / helper, Path(__file__).resolve().parent / helper):
        if candidate.exists():
            return candidate
    return ROOT / "scripts" / helper


def source_tts_data(data_file: str) -> Path:
    for candidate in (
        ROOT / "benchmarks/tes-tts" / data_file,
        Path(__file__).resolve().parent / "tes_tts_data/benchmarks/tes-tts" / data_file,
    ):
        if candidate.exists():
            return candidate
    return ROOT / "benchmarks/tes-tts" / data_file


def write_tts_runtime_fixture(target: Path) -> None:
    bin_dir = target / ".tes/bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    for helper in TTS_RUNTIME_HELPERS:
        shutil.copy2(source_tts_helper(helper), bin_dir / helper)
    data_dir = bin_dir / "tes_tts_data/benchmarks/tes-tts"
    data_dir.mkdir(parents=True, exist_ok=True)
    for data_file in TTS_RUNTIME_DATA_FILES:
        shutil.copy2(source_tts_data(data_file), data_dir / data_file)


def write_base_fixture(target: Path, *, healthy: bool) -> None:
    target.mkdir(parents=True, exist_ok=True)
    write_installed_trigger_surfaces(target, include_portuguese_goal=healthy)
    if healthy:
        (target / "AGENTS.md").write_text(
            "For state-changing actions, route to the TES Mantra Gate defined in "
            "`.agents/skills/tes-engineering-discipline/SKILL.md`. Do not reintroduce.\n",
            encoding="utf-8",
        )
        (target / "CLAUDE.md").write_text(
            "For state-changing actions, route to the TES Mantra Gate defined in "
            "`.claude/skills/tes-guidelines/SKILL.md`. Do not reintroduce.\n",
            encoding="utf-8",
        )
    else:
        (target / "AGENTS.md").write_text("TES installed target bootloader without active gate route.\n", encoding="utf-8")
        (target / "CLAUDE.md").write_text("TES installed target bootloader without active gate route.\n", encoding="utf-8")

    (target / ".agents/skills/tes-engineering-discipline/SKILL.md").write_text(
        mantra_owner_text(include_triggers=healthy),
        encoding="utf-8",
    )
    (target / ".claude/skills/tes-guidelines/SKILL.md").write_text(
        mantra_owner_text(include_triggers=healthy),
        encoding="utf-8",
    )
    (target / ".cursor/rules/tes-guidelines.mdc").write_text(
        mantra_owner_text(include_triggers=True),
        encoding="utf-8",
    )
    (target / ".codex").mkdir(parents=True, exist_ok=True)
    codex_config = "[mcp_servers.tes-cortex]\ncommand = \"python3\"\n"
    if healthy:
        codex_config += '\n[hooks.SessionStart]\ncommand = ".tes/bin/tes_install.py postinstall --agent codex"\n'
    (target / ".codex/config.toml").write_text(codex_config, encoding="utf-8")
    if healthy:
        (target / ".claude/settings.json").parent.mkdir(parents=True, exist_ok=True)
        (target / ".claude/settings.json").write_text(
            json.dumps({"hooks": {"SessionStart": [".tes/bin/tes_install.py postinstall --agent claude"]}}) + "\n",
            encoding="utf-8",
        )
        (target / ".cursor/hooks.json").parent.mkdir(parents=True, exist_ok=True)
        (target / ".cursor/hooks.json").write_text(
            json.dumps({"hooks": {"SessionStart": [".tes/bin/tes_install.py postinstall --agent cursor"]}}) + "\n",
            encoding="utf-8",
        )
    (target / ".mcp.json").write_text(json.dumps({"mcpServers": {"tes-cortex": {"command": "python3"}}}) + "\n", encoding="utf-8")
    (target / ".cursor/mcp.json").parent.mkdir(parents=True, exist_ok=True)
    (target / ".cursor/mcp.json").write_text(json.dumps({"mcpServers": {"tes-cortex": {"command": "python3"}}}) + "\n", encoding="utf-8")
    quality = target / "docs/agents/QUALITY-GATES.md"
    quality.parent.mkdir(parents=True, exist_ok=True)
    quality.write_text(
        "# Quality Gates\n\n"
        + (
            f"- `python3 {CANONICAL_DISCIPLINE_PATH} --self-test`\n"
            if healthy
            else f"- `python3 {STALE_DISCIPLINE_PATH} --self-test`\n"
        ),
        encoding="utf-8",
    )
    manifest = {
        "schema": "tes-bundle-manifest@1",
        "metadata": {"source_tree_state": "clean" if healthy else "dirty"},
        "entries": [] if healthy else [{"path": ".agents/skills/tes-goal-maestro/._SKILL.md"}],
    }
    (target / ".tes").mkdir(parents=True, exist_ok=True)
    (target / ".tes/manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if healthy:
        write_tts_runtime_fixture(target)
    if not healthy:
        residue = target / ".tes/setup/0.0.0/adapters/codex/.agents/skills/tes-goal-maestro/__MACOSX/._SKILL.md"
        residue.parent.mkdir(parents=True, exist_ok=True)
        residue.write_text("", encoding="utf-8")


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-installed-cert-") as tempdir:
        root = Path(tempdir)
        degraded = root / "degraded-target"
        healthy = root / "healthy-target"
        write_base_fixture(degraded, healthy=False)
        write_base_fixture(healthy, healthy=True)
        degraded_result = evaluate(degraded)
        healthy_result = evaluate(healthy)
        if degraded_result["status"] != "PARTIAL":
            failures.append(f"degraded fixture must report PARTIAL, got {degraded_result['status']}")
        degraded_components = degraded_result["components"]
        if degraded_components["mantra_gate_adoption"]["status"] != "DEGRADED":
            failures.append("degraded fixture must expose Mantra Gate DEGRADED")
        if degraded_components["command_trigger_parity"]["status"] != "FAIL":
            failures.append("degraded fixture must expose command trigger FAIL")
        if degraded_components["quality_gates_path"]["status"] != "FAIL":
            failures.append("degraded fixture must expose stale quality-gate path")
        if degraded_components["tes_tts_runtime"]["status"] != "FAIL":
            failures.append("degraded fixture must expose missing TES TTS runtime")
        if degraded_components["artifact_hygiene"]["status"] != "FAIL":
            failures.append("degraded fixture must expose artifact hygiene failure")
        healthy_components = healthy_result["components"]
        if healthy_components["tes_tts_runtime"]["status"] != "PASS":
            failures.append("healthy fixture must certify installed TES TTS runtime")
        if any(not item.get("repair") for item in degraded_result.get("findings", [])):
            failures.append("degraded fixture findings must include repair routes")
        if healthy_result["status"] != "PASS":
            failures.append(f"healthy fixture must report PASS, got {healthy_result['status']}")
        if not healthy_result["negative_checks"]["host_connected_not_inferred"]:
            failures.append("installed certification must never infer host_connected")
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "coverage": "neutral-installed-target-partial-certification",
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate installed-target TES certification.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--target", type=Path, default=Path("."))
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args(argv)

    result = self_test() if args.self_test else evaluate(args.target)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json_only:
        print("[installed-certification] " + result["status"])
    return 0 if result["status"] in {"PASS", "PARTIAL"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
