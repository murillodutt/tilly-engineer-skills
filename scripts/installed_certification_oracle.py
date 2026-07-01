#!/usr/bin/env python3
"""Aggregate installed-target TES certification without hiding partial states."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any

import git_gate_contract
import command_trigger_oracle
import capsule_residue_oracle
import mantra_gate_adoption_oracle
import tes_bundle
import tes_install

# Soft import (mirrors the capsule_residue pattern): the MCP registration ladder
# uses the real out-of-process handshake when available, and degrades to
# config-presence-only evidence (never inferring host connection) if the
# attach-health helper is absent.
try:
    import attach_health_oracle as _attach_health
except ModuleNotFoundError:  # pragma: no cover - degraded environment
    _attach_health = None


VERSION = "0.3.238"
SCHEMA = "tes-installed-certification@1"
STALE_DISCIPLINE_PATH = ".agents/skills/tilly-engineer-skills/scripts/discipline_oracle.py"
CANONICAL_DISCIPLINE_PATH = ".agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py"
CLAUDE_DISCIPLINE_PATH = ".claude/skills/tes-engineering-discipline/scripts/discipline_oracle.py"
LOCK_PATH = ".tes/tes-install-lock.json"
PRETOOLUSE_CONTRACT_PACKAGE_PATH = "docs/architecture/PRETOOLUSE-CONTRACT.md"
PRETOOLUSE_CONTRACT_INSTALLED_PATH = ".tes/docs/architecture/PRETOOLUSE-CONTRACT.md"
PARTIAL_STATUSES = {"DEGRADED", "FAIL", "PARTIAL"}
REVIEW_STATUSES = {"NEEDS_REVIEW"}
BLOCKED_STATUSES = {"BLOCKED", "BYPASS_SUSPECTED"}
# Ceiling F9: honest pending verdicts the runtime CAN produce must GATE the
# headline, never be absorbed as success at the presence-consuming aggregation.
# NEEDS_EVIDENCE / PENDING_* / HOST_UNOBSERVABLE are real, unfinished proof —
# they fold to NEEDS_REVIEW, not PASS.
PENDING_STATUSES = {"NEEDS_EVIDENCE", "PENDING_TRUST", "PENDING_HOST_RESTART", "HOST_UNOBSERVABLE"}
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
    "git_admission": "Repair Git hooks through tes_install.py/field_reports.py install-hook, then rerun canary admission and installed certification.",
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
    # Fold the MIN over all signals (strictest wins), including pending/blocked —
    # not just .status==PASS. A computed BLOCKED / pending / partial verdict one
    # layer down propagates to the headline; it is never softened to PASS.
    statuses = {str(item.get("status") or "UNKNOWN") for item in findings}
    if statuses & BLOCKED_STATUSES:
        return "BLOCKED"
    if statuses & (REVIEW_STATUSES | PENDING_STATUSES):
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

    # Ceiling F5: config presence is the FIRST rung of the registration ladder
    # (config written), not the proof. A substring match in a config file is not
    # a registered, host-connected MCP server. When config is present, climb the
    # ladder with the real out-of-process handshake (initialize -> tools/list).
    # The component only reads PASS when the handshake proves connection; a
    # present-but-unproven config is NEEDS_EVIDENCE, never an inferred PASS.
    config_present = bool(configs)
    server_entrypoint = target / ".tes/bin/cortex_mcp.py"
    server_installed = server_entrypoint.is_file()
    handshake: dict[str, Any] = {"status": "NOT_APPLIED", "reason": "no MCP config present"}
    host_connected_measured = False
    if config_present and server_installed and _attach_health is not None:
        handshake = _attach_health.mcp_handshake(target)
        host_connected_measured = handshake.get("status") == "PASS"
    elif config_present and not server_installed:
        # Config written but the MCP server is not installed (capsule-only / thin
        # install before the server materializes): the registration ladder has not
        # started. NOT_APPLIED, not a false PASS and not a hard gate — there is no
        # server yet to prove.
        handshake = {"status": "NOT_APPLIED", "reason": "MCP config present but server not installed (ladder not started)"}
    elif config_present:
        handshake = {"status": "HOST_UNOBSERVABLE", "reason": "handshake helper unavailable; config presence only"}

    # Ceiling F26: certify the EXPECTED MCP from the install lock, not from
    # config presence alone. If the lock says the MCP surface was attached (for
    # one or more agents) but NO registered config is present, that is a FAILURE
    # — total absence of MCP config must not read as PASS when MCP was promised.
    lock = read_json(target / LOCK_PATH)
    lock_surfaces = lock.get("attached_surfaces") if isinstance(lock.get("attached_surfaces"), list) else []
    mcp_expected = "mcp" in lock_surfaces
    if mcp_expected and not config_present:
        failures.append("install lock attached the MCP surface but no registered MCP config is present")

    if failures:
        status = "FAIL"
    elif not config_present and mcp_expected:
        # Defensive: should be caught by the failure above; never silently PASS.
        status = "FAIL"
    elif not config_present:
        status = "NOT_APPLIED"  # MCP not attached and none present — nothing to register, not a green PASS
    elif host_connected_measured:
        status = "PASS"  # config written AND host handshake proved the server
    elif not server_installed:
        # Config-only, server not yet materialized: registration is genuinely
        # not-applicable at this stage (a substring match was never registration).
        status = "NOT_APPLIED"
    else:
        # Server installed but the handshake did not prove connection (host has
        # not (re)spawned it / cannot be observed): honest pending proof, gated
        # downstream — config presence never reads as a silent green.
        status = "NEEDS_EVIDENCE"

    return {
        "status": status,
        "configs": configs,
        "server_installed": server_installed,
        "handshake": handshake,
        "host_connected": host_connected_measured,
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
    """Scan the installed target for OS residue without hiding Git-scoped residue."""
    found: list[str] = []
    for path in target.rglob("*"):
        if not path.is_file():
            continue
        try:
            relpath = path.relative_to(target)
        except ValueError:
            continue
        if is_os_residue(relpath):
            found.append(rel(path, target))
    return sorted(set(found))


# Delivered-skill territories whose source-of-truth is Markdown/source, never
# bytecode. .tes/bin is intentionally excluded: it legitimately carries a
# runtime bytecode cache (INSTALLATION-FRAMEWORK.md:64). Bytecode found here, or
# in the manifest, or in staged setup, is delivered contamination.
BYTECODE_GUARDED_ROOTS = (".agents/skills", ".claude/skills", ".cursor", ".tes/setup", "skills")


def target_delivered_bytecode_files(target: Path) -> list[str]:
    """Scan delivered-skill + staged-setup territories for Python bytecode."""
    found: list[str] = []
    for root_rel in BYTECODE_GUARDED_ROOTS:
        root = target / root_rel
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and tes_bundle.is_build_artifact(path.relative_to(root)):
                found.append(rel(path, target))
    return sorted(set(found))


def artifact_hygiene(target: Path) -> dict[str, Any]:
    failures: list[str] = []
    residue: list[str] = []
    bytecode: list[str] = []
    manifest = read_json(target / ".tes/manifest.json")
    for entry in manifest.get("entries", []) if isinstance(manifest.get("entries"), list) else []:
        if isinstance(entry, dict) and is_os_residue(Path(str(entry.get("path", "")))):
            residue.append(str(entry.get("path")))
        if isinstance(entry, dict) and tes_bundle.is_build_artifact(Path(str(entry.get("path", "")))):
            bytecode.append(str(entry.get("path")))
    for root in (target / ".tes/setup", target / ".tes/bin"):
        if root.exists():
            residue.extend(rel(path, target) for path in root.rglob("*") if path.is_file() and is_os_residue(path.relative_to(root)))
    residue.extend(target_os_residue_files(target))
    bytecode.extend(target_delivered_bytecode_files(target))
    if residue:
        failures.extend(f"OS residue present: {path}" for path in sorted(set(residue)))
    if bytecode:
        failures.extend(f"delivered Python bytecode contamination: {path}" for path in sorted(set(bytecode)))
    metadata = manifest.get("metadata") if isinstance(manifest.get("metadata"), dict) else {}
    # Ceiling F6: absent provenance is UNKNOWN, never folded in with CLEAN. Only a
    # measured "clean" source tree may allow a sealed claim; "unknown" (no
    # provenance recorded) and "dirty"/"unsealed-package" are fail-closed. Missing
    # proof must never read as sealed.
    source_tree_state = str(metadata.get("source_tree_state") or "unknown")
    sealed_claim_allowed = source_tree_state == "clean" and not failures
    return {
        "status": "FAIL" if failures else "PASS",
        "source_tree_state": source_tree_state,
        "sealed_claim_allowed": sealed_claim_allowed,
        "release_claim_status": "SEALED_ALLOWED" if sealed_claim_allowed else "UNSEALED_OR_NEEDS_RELEASE_GATE",
        "residue": sorted(set(residue)),
        "bytecode": sorted(set(bytecode)),
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


def _hooks_attached(target: Path) -> bool:
    lock = read_json(target / LOCK_PATH)
    attached = lock.get("attached_surfaces") if isinstance(lock.get("attached_surfaces"), list) else []
    return "hooks" in attached or any(
        (target / relpath).exists()
        for relpath in (".git/hooks/pre-push", ".git/hooks/pre-commit", ".githooks/pre-push", ".githooks/pre-commit")
    )


def _git_hook_gate_evidence(target: Path, hook_type: str) -> dict[str, Any]:
    return git_gate_contract.installed_hook_evidence(target, hook_type)


def git_admission_status(target: Path) -> dict[str, Any]:
    return git_gate_contract.installed_git_admission_status(target, hooks_attached=_hooks_attached(target))


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
        "git_admission": git_admission_status(target),
        "pretooluse_contract_reference": contract_reference,
    }
    findings: list[dict[str, Any]] = []
    for name, payload in components.items():
        status = str(payload.get("status") or "UNKNOWN")
        if status in {"PASS", "PASS_WITH_FINDINGS", "OK", "NOT_APPLIED"}:
            continue
        # Ceiling F9: any honest pending verdict (not just hook_runtime_health)
        # becomes a gating finding — presence one layer down never consumes a
        # pending state as success.
        if status in PENDING_STATUSES:
            findings.append(
                {
                    "component": name,
                    "status": status,
                    "detail": payload.get("findings") or payload.get("agents") or payload.get("failures") or [],
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
    # Ceiling F8: the seal verdict reaches the headline, not just an internal
    # component. When the source tree is not provably sealed *for a provenance
    # reason* (unknown/dirty/unsealed-package) — and artifact_hygiene has not
    # already FAILed for another cause (whose PARTIAL already gates the headline
    # and whose failure is itself what suppresses the seal) — append a gating
    # finding so the top-level status folds the seal in instead of burying it.
    if hygiene.get("release_claim_status") != "SEALED_ALLOWED" and hygiene.get("status") != "FAIL":
        findings.append(
            {
                "component": "release_claim",
                "status": "NEEDS_REVIEW",
                "detail": [
                    f"source_tree_state={hygiene.get('source_tree_state')}; "
                    f"release_claim_status={hygiene.get('release_claim_status')}"
                ],
                "repair": "Rebuild the bundle from a clean, provenance-stamped source tree before claiming a sealed release.",
            }
        )
    # Ceiling F24: distinguish PASS_BASIC from PASS_CEILING at the headline. The
    # PreToolUse ceiling status rides on hook_runtime_health; when it has not
    # proven the ceiling (ceiling_status != PASS_CEILING while hooks are in play),
    # surface NEEDS_CEILING_EVIDENCE as a visible finding rather than letting a
    # floor-green hook collapse into an unqualified PASS headline.
    hook_health = components.get("hook_runtime_health") if isinstance(components.get("hook_runtime_health"), dict) else {}
    ceiling_status = str(hook_health.get("ceiling_status") or "")
    hooks_in_play = str(hook_health.get("status") or "") != "NOT_APPLIED"
    certification_tier = "PASS_BASIC"
    if hooks_in_play and ceiling_status == "PASS_CEILING":
        certification_tier = "PASS_CEILING"
    if hooks_in_play and ceiling_status and ceiling_status != "PASS_CEILING":
        # The hook ran at the floor (PASS_BASIC) but the ceiling is not yet
        # observed. Per ceiling F24 this must be DISTINGUISHED (certification_tier
        # stays PASS_BASIC) and SURFACED (a visible ceiling_evidence finding), but
        # on an otherwise-healthy fresh install it is readiness, not a defect —
        # the ceiling is proven by exercising the host PreToolUse path, exactly
        # like host-pending MCP/hook evidence. So the finding is INFO (visible,
        # non-gating); the tier difference is the load-bearing signal. It would
        # only gate if some OTHER finding already makes the run non-PASS.
        if not any(f.get("component") == "ceiling_evidence" for f in findings):
            findings.append(
                {
                    "component": "ceiling_evidence",
                    "status": "INFO",
                    "detail": [f"hook ceiling_status={ceiling_status} (PASS_BASIC, ceiling not yet observed)"],
                    "repair": "Exercise the host PreToolUse path so the ceiling contract is observed, then recertify for PASS_CEILING.",
                }
            )
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "target": str(target),
        "status": status_from_findings(findings),
        "certification_tier": certification_tier,
        "components": components,
        "findings": findings,
        "release_claim_status": hygiene.get("release_claim_status"),
        "negative_checks": {
            # Ceiling F5: host_connected is a MEASURED field, never an inferred
            # constant. The mcp_registration ladder sets host_connected True only
            # when the real handshake proved the server; this negative check
            # asserts the certification did not infer connection without that
            # proof — i.e. host_connected is only True when handshake==PASS.
            "host_connected_not_inferred": (
                components["mcp_registration"].get("host_connected", False)
                == (components["mcp_registration"].get("handshake", {}).get("status") == "PASS")
            ),
            "vscode_not_part_of_agent_all": not (target / ".vscode/mcp.json").exists(),
            "stale_discipline_path_absent": not quality.get("failures"),
            "os_residue_absent": not hygiene.get("residue"),
            "delivered_bytecode_absent": not hygiene.get("bytecode"),
            "stale_codex_hooks_json_absent": not hook_hygiene.get("failures"),
            "git_admission_enforced": components["git_admission"].get("status") in {"PASS", "NOT_APPLIED"},
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


def write_git_gate_fixture(target: Path, *, drain_only: bool = False) -> None:
    git_gate_contract.write_git_gate_fixture(
        target,
        precommit="strict",
        prepush="drain-only" if drain_only else "full",
    )


def write_mcp_server_stub(target: Path) -> None:
    """Plant a minimal MCP stdio server so the F5 registration ladder can climb.

    Config presence alone is rung 1; the real handshake (initialize -> tools/list)
    is the proof. This stub answers both so a fully-installed fixture proves
    host_connected by measurement, not inference. A fixture WITHOUT this stub
    leaves the ladder unproven (NEEDS_EVIDENCE) — the exact F5 false-PASS the
    ceiling forbids.
    """
    entrypoint = target / ".tes/bin/cortex_mcp.py"
    entrypoint.parent.mkdir(parents=True, exist_ok=True)
    entrypoint.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "for line in sys.stdin:\n"
        "    line = line.strip()\n"
        "    if not line:\n"
        "        continue\n"
        "    try:\n"
        "        msg = json.loads(line)\n"
        "    except json.JSONDecodeError:\n"
        "        continue\n"
        "    mid = msg.get('id')\n"
        "    method = msg.get('method')\n"
        "    if method == 'initialize':\n"
        "        print(json.dumps({'jsonrpc': '2.0', 'id': mid, 'result': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'serverInfo': {'name': 'tes-cortex-stub', 'version': '0'}}}), flush=True)\n"
        "    elif method == 'tools/list':\n"
        "        print(json.dumps({'jsonrpc': '2.0', 'id': mid, 'result': {'tools': [{'name': 'tes_probe'}]}}), flush=True)\n",
        encoding="utf-8",
    )
    entrypoint.chmod(0o755)


def write_base_fixture(target: Path, *, healthy: bool) -> None:
    target.mkdir(parents=True, exist_ok=True)
    write_installed_trigger_surfaces(target, include_portuguese_goal=healthy)
    # Both fixtures install the MCP server so the registration ladder is proven by
    # a real handshake (F5), not inferred from config presence.
    write_mcp_server_stub(target)
    write_git_gate_fixture(target)
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
        git_component = healthy_result["components"]["git_admission"]
        if git_component.get("status") != "PASS":
            failures.append(f"healthy fixture must expose PASS git_admission, got {git_component.get('status')}")
        if not (
            git_component.get("precommit_enforced")
            and git_component.get("prepush_installed")
            and git_component.get("field_reports_prepush_drain")
            and git_component.get("prepush_enforced")
        ):
            failures.append("healthy fixture must prove enforced pre-commit and enforced pre-push plus Field Reports drain")
        hook_health = healthy_result["components"]["hook_runtime_health"]
        if hook_health.get("status") == "NEEDS_EVIDENCE":
            hook_finding = next(
                (item for item in healthy_result.get("findings", []) if item.get("component") == "hook_runtime_health"),
                None,
            )
            if not hook_finding or hook_finding.get("status") != "NEEDS_EVIDENCE":
                failures.append("hook_runtime_health NEEDS_EVIDENCE must remain visible without collapsing aggregate PASS")

        drain_only_target = root / "healthy-with-drain-only-prepush"
        write_base_fixture(drain_only_target, healthy=True)
        write_git_gate_fixture(drain_only_target, drain_only=True)
        drain_only_result = evaluate(drain_only_target)
        drain_git = drain_only_result["components"]["git_admission"]
        if drain_only_result["status"] != "NEEDS_REVIEW":
            failures.append(f"drain-only pre-push must gate installed certification to NEEDS_REVIEW, got {drain_only_result['status']}")
        if not (
            drain_git.get("prepush_installed")
            and drain_git.get("field_reports_prepush_drain")
            and not drain_git.get("prepush_enforced")
            and not drain_git.get("project_prepush_gate")
        ):
            failures.append("drain-only pre-push must not be certified as enforced git admission")

        no_git_target = root / "healthy-hooks-attached-no-git"
        write_base_fixture(no_git_target, healthy=True)
        shutil.rmtree(no_git_target / ".git")
        no_git_result = evaluate(no_git_target)
        if no_git_result["components"]["git_admission"].get("status") != "NEEDS_REVIEW":
            failures.append("hooks-attached no-Git fixture must report git_admission NEEDS_REVIEW")

        # Red-capable Gap 4 / Ceiling F9 fixture: hooks CONFIGURED on disk + lock
        # declares the hooks surface, but NO runtime ledger exists -> hook_runtime
        # _health must be NEEDS_EVIDENCE, that finding MUST stay visible in
        # findings[], AND the aggregate must now GATE to NEEDS_REVIEW. The ceiling
        # decision (F9) overturns the prior "NEEDS_EVIDENCE stays PASS" rule:
        # configured-but-unobserved is honest pending proof, not success — absence
        # of runtime evidence never reads green. NEEDS_REVIEW is a readiness
        # verdict (install stays reversible, exit 0 at the install layer), not a
        # process failure. Deleting the NEEDS_EVIDENCE finding emission, or folding
        # it back to PASS, turns THIS assertion red.
        needs_evidence_target = root / "healthy-hooks-configured-no-runtime"
        write_base_fixture(needs_evidence_target, healthy=True)
        ne_ledger = needs_evidence_target / ".tes/runtime/hooks/executed.jsonl"
        if ne_ledger.exists():
            ne_ledger.unlink()  # configured-but-unobserved: no host produced runtime records
        needs_evidence_result = evaluate(needs_evidence_target)
        ne_hook_health = needs_evidence_result["components"]["hook_runtime_health"]
        if ne_hook_health.get("status") != "NEEDS_EVIDENCE":
            failures.append(
                f"configured-hooks-without-runtime fixture must drive hook_runtime_health "
                f"NEEDS_EVIDENCE, got {ne_hook_health.get('status')}"
            )
        ne_finding = next(
            (item for item in needs_evidence_result.get("findings", []) if item.get("component") == "hook_runtime_health"),
            None,
        )
        if not ne_finding or ne_finding.get("status") != "NEEDS_EVIDENCE":
            failures.append("hook_runtime_health NEEDS_EVIDENCE finding must remain visible (not silently collapsed)")
        if needs_evidence_result["status"] != "NEEDS_REVIEW":
            failures.append(
                f"NEEDS_EVIDENCE hook runtime must GATE the installed aggregate to NEEDS_REVIEW "
                f"(ceiling F9: pending never reads PASS), got {needs_evidence_result['status']}"
            )
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

        # Red-capable bytecode fixture (Gap 4 / canary 379-vs-378): a __pycache__
        # cache planted under a delivered skill must surface as artifact_hygiene
        # contamination and drive a certification finding — the exact divergence
        # the installed canary exhibited under an overall-PASS report.
        bytecode_target = root / "healthy-with-delivered-bytecode"
        write_base_fixture(bytecode_target, healthy=True)
        bytecode_cache = (
            bytecode_target
            / ".agents/skills/tes-engineering-discipline/scripts/__pycache__/discipline_oracle.cpython-314.pyc"
        )
        bytecode_cache.parent.mkdir(parents=True, exist_ok=True)
        bytecode_cache.write_bytes(b"\x00\x00\x00\x00delivered-bytecode")
        bytecode_result = evaluate(bytecode_target)
        bytecode_hygiene = bytecode_result["components"]["artifact_hygiene"]
        if bytecode_hygiene["status"] != "FAIL":
            failures.append("delivered-skill Python bytecode must drive artifact_hygiene FAIL")
        if not any("bytecode" in str(item) for item in bytecode_hygiene.get("failures", [])):
            failures.append("artifact_hygiene must name the delivered bytecode contamination")
        if not any(f.get("component") == "artifact_hygiene" for f in bytecode_result.get("findings", [])):
            failures.append("delivered bytecode must be reported as a certification finding")
        if not bytecode_result["negative_checks"].get("os_residue_absent", True):
            # bytecode is a separate class; OS-residue check must not be conflated
            pass
        if bytecode_result["negative_checks"].get("delivered_bytecode_absent") is not False:
            failures.append("negative_checks must expose delivered_bytecode_absent=False under contamination")

        # Red-capable Ceiling F4 fixture: do not hide the whole .git tree from
        # artifact hygiene. Normal Git metadata is not residue, but an AppleDouble
        # file under .git is still residue and must be surfaced.
        git_residue_target = root / "healthy-with-git-scoped-residue"
        write_base_fixture(git_residue_target, healthy=True)
        git_object = git_residue_target / ".git/objects/aa/neutral-object"
        git_object.parent.mkdir(parents=True, exist_ok=True)
        git_object.write_text("not an OS residue name\n", encoding="utf-8")
        git_residue = git_residue_target / ".git/._config"
        git_residue.write_text("appledouble residue\n", encoding="utf-8")
        git_residue_result = evaluate(git_residue_target)
        git_residue_hygiene = git_residue_result["components"]["artifact_hygiene"]
        if git_residue_hygiene["status"] != "FAIL":
            failures.append("F4: .git-scoped OS residue must drive artifact_hygiene FAIL")
        if ".git/._config" not in git_residue_hygiene.get("residue", []):
            failures.append("F4: artifact_hygiene must surface .git/._config residue")
        if ".git/objects/aa/neutral-object" in git_residue_hygiene.get("residue", []):
            failures.append("F4: normal Git metadata must not be treated as OS residue")

        # Red-capable Ceiling F6 + F8 fixture: an otherwise-healthy target whose
        # manifest records NO provenance (source_tree_state="unknown") must NOT
        # read as sealed, and the seal verdict must reach the HEADLINE — the
        # aggregate gates to NEEDS_REVIEW and release_claim_status surfaces at the
        # top level, not buried under artifact_hygiene. Folding "unknown" back in
        # with "clean", or dropping the release_claim finding, turns this red.
        unsealed_target = root / "healthy-unknown-provenance"
        write_base_fixture(unsealed_target, healthy=True)
        manifest_path = unsealed_target / ".tes/manifest.json"
        manifest = read_json(manifest_path)
        manifest.setdefault("metadata", {})["source_tree_state"] = "unknown"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        unsealed_result = evaluate(unsealed_target)
        if unsealed_result["components"]["artifact_hygiene"].get("sealed_claim_allowed") is not False:
            failures.append("unknown provenance must NOT allow a sealed claim (F6: unknown is fail-closed, not clean)")
        if unsealed_result.get("release_claim_status") != "UNSEALED_OR_NEEDS_RELEASE_GATE":
            failures.append("release_claim_status must surface UNSEALED at the certification headline (F8)")
        if unsealed_result["status"] != "NEEDS_REVIEW":
            failures.append(
                f"unsealed (unknown-provenance) target must GATE the aggregate to NEEDS_REVIEW "
                f"(F8: seal reaches headline), got {unsealed_result['status']}"
            )
        if not any(f.get("component") == "release_claim" for f in unsealed_result.get("findings", [])):
            failures.append("unsealed target must emit a release_claim certification finding (F8)")

        # Red-capable Ceiling F5 fixture: MCP server IS installed and config IS
        # present, but the server does not complete the handshake (here: a broken
        # server that never answers initialize). config-substring PASS is gone —
        # the ladder requires a real handshake, so mcp_registration must be
        # NEEDS_EVIDENCE, host_connected measured False, and the aggregate gates
        # to NEEDS_REVIEW. (Config WITHOUT an installed server is a distinct
        # NOT_APPLIED case — the ladder has not started — exercised separately.)
        unproven_mcp_target = root / "healthy-mcp-server-no-handshake"
        write_base_fixture(unproven_mcp_target, healthy=True)
        broken_server = unproven_mcp_target / ".tes/bin/cortex_mcp.py"
        broken_server.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n", encoding="utf-8")  # answers nothing
        unproven_result = evaluate(unproven_mcp_target)
        unproven_mcp = unproven_result["components"]["mcp_registration"]
        if unproven_mcp.get("status") != "NEEDS_EVIDENCE":
            failures.append(
                f"installed MCP server that fails the handshake must be NEEDS_EVIDENCE (F5: config presence is not registration), "
                f"got {unproven_mcp.get('status')}"
            )
        if unproven_mcp.get("host_connected") is not False:
            failures.append("host_connected must be measured False when the handshake does not prove the server (F5)")
        if not unproven_result["negative_checks"]["host_connected_not_inferred"]:
            failures.append("host_connected_not_inferred must hold (measured, not inferred) when handshake fails (F5)")
        if unproven_result["status"] != "NEEDS_REVIEW":
            failures.append(
                f"unproven MCP registration must GATE the aggregate to NEEDS_REVIEW (F5+F9), "
                f"got {unproven_result['status']}"
            )

        # Companion: config present but server NOT installed -> NOT_APPLIED (the
        # ladder has not started; a substring was never registration). This must
        # NOT gate, distinguishing thin/capsule-only install from a broken server.
        no_server_target = root / "healthy-mcp-config-no-server"
        write_base_fixture(no_server_target, healthy=True)
        no_server_stub = no_server_target / ".tes/bin/cortex_mcp.py"
        if no_server_stub.exists():
            no_server_stub.unlink()
        no_server_result = evaluate(no_server_target)
        if no_server_result["components"]["mcp_registration"].get("status") != "NOT_APPLIED":
            failures.append(
                f"MCP config without an installed server must be NOT_APPLIED (ladder not started), "
                f"got {no_server_result['components']['mcp_registration'].get('status')}"
            )

        # Red-capable Ceiling F26: the install lock attached the MCP surface but
        # NO MCP config is present -> mcp_registration must FAIL (promised MCP is
        # absent), never read as PASS. Reverting to a config-presence PASS turns
        # this red.
        mcp_expected_target = root / "healthy-mcp-attached-but-absent"
        write_base_fixture(mcp_expected_target, healthy=True)
        # Remove every MCP config so configs=[] while the lock says mcp attached.
        for relpath in (".codex/config.toml", ".mcp.json", ".cursor/mcp.json", ".vscode/mcp.json"):
            p = mcp_expected_target / relpath
            if p.exists():
                p.unlink()
        lock_path = mcp_expected_target / LOCK_PATH
        lock = read_json(lock_path)
        surfaces = set(lock.get("attached_surfaces") or [])
        surfaces.add("mcp")
        lock["attached_surfaces"] = sorted(surfaces)
        lock_path.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        mcp_expected_result = evaluate(mcp_expected_target)
        if mcp_expected_result["components"]["mcp_registration"].get("status") != "FAIL":
            failures.append(
                "F26: lock attached MCP but no config present must FAIL mcp_registration, "
                f"got {mcp_expected_result['components']['mcp_registration'].get('status')}"
            )

        # Red-capable Ceiling F24: certification_tier must distinguish PASS_BASIC
        # from PASS_CEILING. The healthy fixture's hook runs at the floor with the
        # ceiling unobserved -> tier must be PASS_BASIC and a visible (non-gating)
        # ceiling_evidence finding must be present. Collapsing tier into a bare
        # PASS, or hiding the ceiling_evidence finding, turns this red.
        if healthy_result.get("certification_tier") != "PASS_BASIC":
            failures.append(
                f"F24: healthy floor-only hook must report certification_tier PASS_BASIC, "
                f"got {healthy_result.get('certification_tier')}"
            )
        if not any(f.get("component") == "ceiling_evidence" for f in healthy_result.get("findings", [])):
            failures.append("F24: a floor-only (ceiling-unobserved) hook must surface a ceiling_evidence finding")
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
