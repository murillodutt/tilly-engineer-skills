#!/usr/bin/env python3
"""Aggregate installed-target TES certification without hiding partial states."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
from typing import Any

import command_trigger_oracle
import mantra_gate_adoption_oracle


VERSION = "0.3.204"
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
}
ROOT = Path(__file__).resolve().parents[1]


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
    if not any((target / relpath).exists() for relpath in ("AGENTS.md", "CLAUDE.md", "CURSOR.md")):
        return {"status": "NOT_APPLIED", "reason": "root-context not attached"}
    result = mantra_gate_adoption_oracle.evaluate(target)
    return {
        "status": result.get("status"),
        "surface_health": result.get("surface_health", {}),
        "findings": result.get("findings", []),
    }


def trigger_status(target: Path) -> dict[str, Any]:
    if not any(
        (target / relpath).exists()
        for relpath in (
            "AGENTS.md",
            "CLAUDE.md",
            "CURSOR.md",
            ".agents/skills/tes-engineering-discipline/SKILL.md",
            ".claude/skills/tes-engineering-discipline/SKILL.md",
            ".cursor/rules/tes-engineering-discipline.mdc",
        )
    ):
        return {"status": "NOT_APPLIED", "checked": [], "failures": [], "reason": "root-context not attached"}
    result = command_trigger_oracle.check_installed_target(target)
    return {
        "status": result.get("status"),
        "checked": result.get("checked", []),
        "failures": result.get("failures", []),
    }


def evaluate(target: Path) -> dict[str, Any]:
    target = target.expanduser().resolve()
    quality = quality_gates_path_status(target)
    hygiene = artifact_hygiene(target)
    components = {
        "mcp_registration": mcp_registration(target),
        "mantra_gate_adoption": adoption_status(target),
        "command_trigger_parity": trigger_status(target),
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
    text = (
        "## Mantra Gate\n\n"
        "Use the TES Mantra Gate for destructive, remote, release, sync, "
        "secret-bearing, or high-impact state changes. Ordinary local edits "
        "do not block on gate artifacts, markers, or skill loading.\n"
    )
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
    cursor = target / ".cursor/rules/tes-engineering-discipline.mdc"
    cursor.parent.mkdir(parents=True, exist_ok=True)
    cursor.write_text(all_trigger_terms(), encoding="utf-8")


def write_base_fixture(target: Path, *, healthy: bool) -> None:
    target.mkdir(parents=True, exist_ok=True)
    write_installed_trigger_surfaces(target, include_portuguese_goal=healthy)
    if healthy:
        (target / "AGENTS.md").write_text(
            "Use the TES Mantra Gate defined in "
            "`.agents/skills/tes-engineering-discipline/SKILL.md` for destructive, remote, "
            "release, sync, secret-bearing, or high-impact state changes. Do not reintroduce.\n",
            encoding="utf-8",
        )
        (target / "CLAUDE.md").write_text(
            "Use the TES Mantra Gate defined in "
            "`.claude/skills/tes-engineering-discipline/SKILL.md` for destructive, remote, release, "
            "sync, secret-bearing, or high-impact state changes. Do not reintroduce.\n",
            encoding="utf-8",
        )
    else:
        (target / "AGENTS.md").write_text("TES installed target bootloader without active gate route.\n", encoding="utf-8")
        (target / "CLAUDE.md").write_text("TES installed target bootloader without active gate route.\n", encoding="utf-8")

    (target / ".agents/skills/tes-engineering-discipline/SKILL.md").write_text(
        mantra_owner_text(include_triggers=healthy),
        encoding="utf-8",
    )
    (target / ".claude/skills/tes-engineering-discipline/SKILL.md").write_text(
        mantra_owner_text(include_triggers=healthy),
        encoding="utf-8",
    )
    (target / ".cursor/rules/tes-engineering-discipline.mdc").write_text(
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
        if degraded_components["artifact_hygiene"]["status"] != "FAIL":
            failures.append("degraded fixture must expose artifact hygiene failure")
        if any(not item.get("repair") for item in degraded_result.get("findings", [])):
            failures.append("degraded fixture findings must include repair routes")
        if healthy_result["status"] != "PASS":
            failures.append(f"healthy fixture must report PASS, got {healthy_result['status']}")
        if not healthy_result["negative_checks"]["host_connected_not_inferred"]:
            failures.append("installed certification must never infer host_connected")

        # A schema-invalid historical gate record on an otherwise healthy target
        # must surface in the certification finding's detail (naming the invalid
        # record), not fall through to surface_health:OK — the disagreement that
        # sent a real recovery down the wrong path.
        invalid_record_target = root / "healthy-with-invalid-record"
        write_base_fixture(invalid_record_target, healthy=True)
        ledger = invalid_record_target / ".tes/field-reports/mantra-gates.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_text(
            json.dumps({"gate": {"VERIFY": "x", "SCOPE": "s", "BEST_PATH": "d", "DOCUMENT": "n",
                                 "RESOLVE": "done", "STATUS": "PASS"}, "visible": "full"}) + "\n",
            encoding="utf-8",
        )
        invalid_result = evaluate(invalid_record_target)
        adoption_finding = next(
            (f for f in invalid_result.get("findings", []) if f.get("component") == "mantra_gate_adoption"),
            None,
        )
        detail_blob = json.dumps(adoption_finding.get("detail")) if adoption_finding else ""
        if not adoption_finding:
            failures.append("invalid historical record must produce a mantra_gate_adoption certification finding")
        elif "invalid_historical_record" not in detail_blob and "PASS" not in detail_blob:
            failures.append("certification finding detail must name the invalid record, not fall back to surface_health:OK")
        if invalid_result["status"] == "BLOCKED":
            failures.append("invalid historical record must not drive installed certification to BLOCKED (D-fix invariant)")
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
