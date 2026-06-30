#!/usr/bin/env python3
"""Aggregate installed-target TES certification without hiding partial states."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any

import command_trigger_oracle
import capsule_residue_oracle
import mantra_gate_adoption_oracle
import tes_install


VERSION = "0.3.231"
SCHEMA = "tes-installed-certification@1"
STALE_DISCIPLINE_PATH = ".agents/skills/tilly-engineer-skills/scripts/discipline_oracle.py"
CANONICAL_DISCIPLINE_PATH = ".agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py"
LOCK_PATH = ".tes/tes-install-lock.json"
PRETOOLUSE_CONTRACT_PACKAGE_PATH = "docs/architecture/PRETOOLUSE-CONTRACT.md"
PRETOOLUSE_CONTRACT_INSTALLED_PATH = ".tes/docs/architecture/PRETOOLUSE-CONTRACT.md"
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
    "hook_config_hygiene": "Remove or regenerate stale hook config through tes_install.py attach/detach/update, then recertify.",
    "hook_runtime_health": "Repair or intentionally detach TES hooks, then rerun tes_install.py hook-health and installed certification.",
    "pretooluse_contract_reference": "Rerun tes_install.py from the package version that owns the installed target, then recertify.",
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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def target_os_residue_files(target: Path) -> list[str]:
    """Scan the installed target for OS residue outside Git metadata."""
    found: list[str] = []
    for path in target.rglob("*"):
        if not path.is_file():
            continue
        try:
            relpath = path.relative_to(target)
        except ValueError:
            continue
        if relpath.parts and relpath.parts[0] == ".git":
            continue
        if is_os_residue(relpath):
            found.append(rel(path, target))
    return sorted(set(found))


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
    residue.extend(target_os_residue_files(target))
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


def hook_config_hygiene(target: Path) -> dict[str, Any]:
    residue_result = capsule_residue_oracle.evaluate(target)
    active = residue_result.get("active_residue") if isinstance(residue_result.get("active_residue"), list) else []
    codex_hook_residue = sorted(str(item) for item in active if ".codex/hooks.json" in str(item))
    failures = [f"stale Codex hook config residue present: {item}" for item in codex_hook_residue]
    return {
        "status": "NEEDS_REVIEW" if failures else "PASS",
        "failures": failures,
        "checked": [".codex/hooks.json"],
    }


def hook_runtime_health(target: Path) -> dict[str, Any]:
    """Certify installed hook runtime health when the lock declares hooks."""
    lock = read_json(target / LOCK_PATH)
    attached_surfaces = lock.get("attached_surfaces") if isinstance(lock.get("attached_surfaces"), list) else []
    if "hooks" not in attached_surfaces and not any(
        (target / relpath).exists()
        for relpath in (
            ".codex/config.toml",
            ".claude/settings.json",
            ".cursor/hooks.json",
            ".tes/runtime/hooks/executed.jsonl",
            ".tes/hooks/executed.jsonl",
        )
    ):
        return {"status": "NOT_APPLIED", "reason": "hooks not attached"}
    result = tes_install.hook_health_payload(target)
    return {
        "status": result.get("status"),
        "attached_surfaces": result.get("attached_surfaces", []),
        "sentinels": result.get("sentinels", {}),
        "agents": result.get("agents", {}),
        "findings": result.get("findings", []),
        "helper_contract_status": result.get("helper_contract_status"),
        "floor_status": result.get("floor_status"),
        "ceiling_status": result.get("ceiling_status"),
    }


def pretooluse_contract_reference(target: Path) -> dict[str, Any]:
    """Verify the installed PreToolUse contract copy and lock without source reads."""
    has_capsule_signal = any(
        (target / relpath).exists()
        for relpath in (
            ".tes/manifest.json",
            ".tes/bin/tes_install.py",
            LOCK_PATH,
            PRETOOLUSE_CONTRACT_INSTALLED_PATH,
        )
    )
    if not has_capsule_signal:
        return {"status": "NOT_APPLIED", "failures": [], "reason": "capsule not installed"}

    failures: list[str] = []
    lock = read_json(target / LOCK_PATH)
    reference = lock.get("pretooluse_contract") if isinstance(lock.get("pretooluse_contract"), dict) else None
    if reference is None:
        failures.append(f"{LOCK_PATH} missing pretooluse_contract")
        reference = {}

    expected = {
        "package_path": PRETOOLUSE_CONTRACT_PACKAGE_PATH,
        "installed_path": PRETOOLUSE_CONTRACT_INSTALLED_PATH,
        "version": VERSION,
    }
    for key, value in expected.items():
        if reference.get(key) != value:
            failures.append(f"pretooluse_contract.{key} expected {value!r}, got {reference.get(key)!r}")

    installed = target / PRETOOLUSE_CONTRACT_INSTALLED_PATH
    actual_sha: str | None = None
    if not installed.is_file():
        failures.append(f"installed PreToolUse contract missing: {PRETOOLUSE_CONTRACT_INSTALLED_PATH}")
    else:
        actual_sha = sha256_file(installed)
        if reference.get("sha256") != actual_sha:
            failures.append(
                "pretooluse_contract.sha256 mismatch: "
                f"lock={reference.get('sha256')!r} installed={actual_sha!r}"
            )

    return {
        "status": "NEEDS_REVIEW" if failures else "PASS",
        "lock_path": LOCK_PATH,
        "package_path": reference.get("package_path"),
        "installed_path": PRETOOLUSE_CONTRACT_INSTALLED_PATH,
        "sha256": reference.get("sha256"),
        "actual_sha256": actual_sha,
        "version": reference.get("version"),
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
    hook_hygiene = hook_config_hygiene(target)
    contract_reference = pretooluse_contract_reference(target)
    components = {
        "mcp_registration": mcp_registration(target),
        "mantra_gate_adoption": adoption_status(target),
        "command_trigger_parity": trigger_status(target),
        "quality_gates_path": quality,
        "artifact_hygiene": hygiene,
        "hook_config_hygiene": hook_hygiene,
        "hook_runtime_health": hook_runtime_health(target),
        "pretooluse_contract_reference": contract_reference,
    }
    findings: list[dict[str, Any]] = []
    for name, payload in components.items():
        status = str(payload.get("status") or "UNKNOWN")
        if status in {"PASS", "PASS_WITH_FINDINGS", "OK", "NOT_APPLIED"}:
            continue
        if status == "NEEDS_EVIDENCE" and name == "hook_runtime_health":
            findings.append(
                {
                    "component": name,
                    "status": "NEEDS_EVIDENCE",
                    "detail": payload.get("findings") or payload.get("agents") or [],
                    "repair": REPAIR_ROUTES.get(name, "Inspect this certification component and rerun installed certification."),
                }
            )
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
            "stale_codex_hooks_json_absent": not hook_hygiene.get("failures"),
            "pretooluse_contract_reference_valid": not contract_reference.get("failures"),
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
        codex_config += (
            '\n[[hooks.SessionStart]]\ncommand = "python3 .tes/bin/tes_install.py hook --agent codex --target ."\n'
            '\n[[hooks.PreToolUse]]\ncommand = "python3 .tes/bin/tes_install.py hook --agent codex --target ."\n'
        )
    (target / ".codex/config.toml").write_text(codex_config, encoding="utf-8")
    if healthy:
        (target / ".claude/settings.json").parent.mkdir(parents=True, exist_ok=True)
        (target / ".claude/settings.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "SessionStart": [
                            {"hooks": [{"command": "python3 .tes/bin/tes_install.py hook --agent claude --target ."}]}
                        ],
                        "PreToolUse": [
                            {"matcher": "*", "hooks": [{"command": "python3 .tes/bin/tes_install.py hook --agent claude --target ."}]}
                        ],
                    }
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (target / ".cursor/hooks.json").parent.mkdir(parents=True, exist_ok=True)
        (target / ".cursor/hooks.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "sessionStart": [{"command": "python3 .tes/bin/tes_install.py hook --agent cursor --target ."}],
                        "beforeSubmitPrompt": [{"command": "python3 .tes/bin/tes_install.py hook --agent cursor --target ."}],
                        "preToolUse": [{"command": "python3 .tes/bin/tes_install.py hook --agent cursor --target ."}],
                    }
                },
                sort_keys=True,
            )
            + "\n",
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
        bin_dir = target / ".tes/bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        for helper in ("pretooluse_kernel.py", "pretooluse_session.py", "cortex_runtime.py", "cortex.py"):
            source = ROOT / "scripts" / helper
            if source.is_file():
                (bin_dir / helper).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        ledger = target / ".tes/runtime/hooks/executed.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        records = [
            {"agent": "codex", "event": "SessionStart", "event_canonical": "SessionStart", "mode": "session_start", "session": "healthy-codex"},
            {"agent": "codex", "event": "PreToolUse", "event_canonical": "PreToolUse", "mode": "pretooluse", "session": "healthy-codex", "schema_version": "pretooluse_decision@2"},
            {"agent": "claude", "event": "SessionStart", "event_canonical": "SessionStart", "mode": "session_start", "session": "healthy-claude"},
            {"agent": "claude", "event": "PreToolUse", "event_canonical": "PreToolUse", "mode": "pretooluse", "session": "healthy-claude", "schema_version": "pretooluse_decision@2"},
            {"agent": "cursor", "event": "sessionStart", "event_canonical": "sessionStart", "mode": "session_start", "session": "healthy-cursor"},
            {"agent": "cursor", "event": "beforeSubmitPrompt", "event_canonical": "beforeSubmitPrompt", "mode": "before_submit_prompt", "session": "healthy-cursor"},
            {"agent": "cursor", "event": "preToolUse", "event_canonical": "PreToolUse", "mode": "pretooluse", "session": "healthy-cursor", "schema_version": "pretooluse_decision@2"},
        ]
        ledger.write_text(
            "".join(json.dumps({**record, "ts": "2026-06-30T00:00:00Z"}, sort_keys=True) + "\n" for record in records),
            encoding="utf-8",
        )
    contract_text = "# PreToolUse Contract\n\nFixture contract.\n"
    contract_path = target / PRETOOLUSE_CONTRACT_INSTALLED_PATH
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_text(contract_text, encoding="utf-8")
    lock = {
        "schema": "tes-install-lock@1",
        "version": VERSION,
        "attached_surfaces": ["capsule", "hooks", "mcp", "root-context", "skills"],
        "pretooluse_contract": {
            "package_path": PRETOOLUSE_CONTRACT_PACKAGE_PATH,
            "installed_path": PRETOOLUSE_CONTRACT_INSTALLED_PATH,
            "sha256": sha256_file(contract_path),
            "version": VERSION,
        },
    }
    (target / LOCK_PATH).write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
        if degraded_components["hook_config_hygiene"]["status"] != "PASS":
            failures.append("degraded fixture must not invent hook config hygiene failure")
        if any(not item.get("repair") for item in degraded_result.get("findings", [])):
            failures.append("degraded fixture findings must include repair routes")
        if healthy_result["status"] != "PASS":
            failures.append(f"healthy fixture must report PASS, got {healthy_result['status']}")
        hook_health = healthy_result["components"]["hook_runtime_health"]
        if hook_health.get("status") == "NEEDS_EVIDENCE":
            hook_finding = next(
                (item for item in healthy_result.get("findings", []) if item.get("component") == "hook_runtime_health"),
                None,
            )
            if not hook_finding or hook_finding.get("status") != "NEEDS_EVIDENCE":
                failures.append("hook_runtime_health NEEDS_EVIDENCE must remain visible without collapsing aggregate PASS")
        if not healthy_result["negative_checks"]["host_connected_not_inferred"]:
            failures.append("installed certification must never infer host_connected")
        if healthy_result["components"]["pretooluse_contract_reference"]["status"] != "PASS":
            failures.append("healthy fixture must expose PASS PreToolUse contract reference")
        if not healthy_result["negative_checks"]["pretooluse_contract_reference_valid"]:
            failures.append("healthy fixture must mark pretooluse_contract_reference_valid")

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

        stale_codex_hook_target = root / "healthy-with-stale-codex-hook"
        write_base_fixture(stale_codex_hook_target, healthy=True)
        stale_hook = stale_codex_hook_target / ".codex/hooks.json"
        stale_hook.write_text(
            json.dumps(
                {
                    "hooks": {
                        "PreToolUse": [
                            {
                                "command": (
                                    "python3 ${CLAUDE_PROJECT_DIR}/.tes/bin/tes_install.py "
                                    "hook --agent claude --target ${CLAUDE_PROJECT_DIR}"
                                )
                            }
                        ]
                    }
                }
            )
            + "\n",
            encoding="utf-8",
        )
        stale_result = evaluate(stale_codex_hook_target)
        stale_hook_hygiene = stale_result["components"]["hook_config_hygiene"]
        if stale_hook_hygiene["status"] != "NEEDS_REVIEW":
            failures.append("stale .codex/hooks.json TES command must produce hook_config_hygiene NEEDS_REVIEW")
        if not any(f.get("component") == "hook_config_hygiene" for f in stale_result.get("findings", [])):
            failures.append("stale .codex/hooks.json must be reported as a certification finding")

        stale_contract_target = root / "healthy-with-stale-contract-lock"
        write_base_fixture(stale_contract_target, healthy=True)
        stale_lock_path = stale_contract_target / LOCK_PATH
        stale_lock = read_json(stale_lock_path)
        stale_lock["pretooluse_contract"]["version"] = "0.0.0"
        stale_lock["pretooluse_contract"]["sha256"] = "0" * 64
        stale_lock_path.write_text(json.dumps(stale_lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        stale_contract_result = evaluate(stale_contract_target)
        stale_contract_component = stale_contract_result["components"]["pretooluse_contract_reference"]
        if stale_contract_component["status"] != "NEEDS_REVIEW":
            failures.append("stale PreToolUse contract lock must produce NEEDS_REVIEW")
        if not any(f.get("component") == "pretooluse_contract_reference" for f in stale_contract_result.get("findings", [])):
            failures.append("stale PreToolUse contract lock must be reported as a certification finding")
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
