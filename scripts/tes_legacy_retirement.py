#!/usr/bin/env python3
"""Retire known legacy Tilly runtime assets before TES updates."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import field_reports
except Exception:  # noqa: BLE001 - installed copies may audit without package context
    field_reports = None  # type: ignore[assignment]


VERSION = "0.3.248"
LEGACY_FIELD_ROOT = Path(".tilly/field-reports")
FIELD_ROOT = Path(".tes/field-reports")
LEGACY_RETROFIT_ROOT = Path(".tilly/retrofit")
RETROFIT_ARCHIVE_ROOT = Path(".tes/legacy-retirement/retrofit")
BACKUP_ROOT = Path(".tes/legacy-retirement")
LEGACY_HOOK_LEDGER = Path(".tes/hooks/executed.jsonl")
RUNTIME_HOOK_LEDGER = Path(".tes/runtime/hooks/executed.jsonl")
HOOK_LEDGER_ARCHIVE = Path(".tes/legacy-retirement/hooks")
HOOK_SMOKE_ROOT = Path(".tes/runtime/hook-smoke")
LEGACY_MCP_SERVER = "tilly-cortex"
STALE_DISCIPLINE_PATH = ".agents/skills/tilly-engineer-skills/scripts/discipline_oracle.py"
CANONICAL_DISCIPLINE_PATH = ".agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py"
KNOWN_TEMPLATE_MARKERS = ("tilly-field-report@1", "Tilly Field Report", "tilly-version")
SKIP_PARTS = {".git", "node_modules", "dist", ".venv", "venv"}
CLEANUP_REASONS = {"python bytecode cache", "old TES rollback backup"}
HOOK_AUDIT_HARNESS_FILES = {
    "claude-forbidden-payload.json",
    "forbidden-executed.txt",
    "run_contract_sim.py",
    "run_forbidden_test.py",
    "run_sim.py",
}


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def add_action(actions: list[dict[str, Any]], action: str, path: Path, target: Path, reason: str, **extra: Any) -> None:
    record = {"action": action, "path": rel(path, target), "reason": reason, **extra}
    if record not in actions:
        actions.append(record)


def should_skip(path: Path, target: Path) -> bool:
    parts = path.relative_to(target).parts
    relpath = path.relative_to(target).as_posix()
    return relpath.startswith(BACKUP_ROOT.as_posix() + "/") or any(part in SKIP_PARTS for part in parts)


def known_removals(target: Path) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for root in (target / ".agents/skills", target / "skills"):
        if root.exists():
            for path in sorted(root.glob("tilly-*")):
                add_action(actions, "remove", path, target, "legacy skill directory")

    cursor_legacy = target / ".cursor/rules/tilly-guidelines.mdc"
    if cursor_legacy.exists():
        add_action(actions, "remove", cursor_legacy, target, "legacy Cursor packaged rule")

    legacy_bin = target / ".tilly/bin"
    if legacy_bin.exists():
        add_action(actions, "remove", legacy_bin, target, "legacy installed helper directory")

    for backup in sorted((target / ".tes/bin").glob("*.bak-*")) if (target / ".tes/bin").exists() else []:
        add_action(actions, "remove", backup, target, "old TES rollback backup")

    legacy_cortex = target / ".tilly/cortex"
    if legacy_cortex.exists():
        for cache in sorted(legacy_cortex.glob("*.sqlite*")):
            add_action(actions, "remove", cache, target, "legacy derived Cortex cache")

    for path in sorted(target.rglob("__pycache__")):
        if not should_skip(path, target) and not covered_by_known(path, target, actions):
            add_action(actions, "remove", path, target, "python bytecode cache")
    for path in sorted(target.rglob("*.pyc")):
        if not should_skip(path, target) and not covered_by_known(path, target, actions):
            add_action(actions, "remove", path, target, "python bytecode cache")

    smoke_root = target / HOOK_SMOKE_ROOT
    if smoke_root.exists():
        for path in sorted(smoke_root.glob("run_*.py")):
            add_action(actions, "remove", path, target, "legacy hook audit harness residue")
        for name in sorted(HOOK_AUDIT_HARNESS_FILES):
            path = smoke_root / name
            if path.exists():
                add_action(actions, "remove", path, target, "legacy hook audit harness residue")

    template = target / ".github/ISSUE_TEMPLATE/tilly-field-report.yml"
    if template.exists():
        text = read_text(template)
        if any(marker in text for marker in KNOWN_TEMPLATE_MARKERS):
            add_action(actions, "remove", template, target, "legacy Field Reports issue template")
        else:
            add_action(actions, "blocked", template, target, "unknown tilly field report template")

    return actions


def mcp_config_actions(target: Path) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    codex = target / ".codex/config.toml"
    if codex.exists():
        text = read_text(codex)
        if "[mcp_servers.tilly-cortex]" in text:
            add_action(actions, "edit_config", codex, target, "remove legacy Codex MCP server", mode="toml-section")
        elif LEGACY_MCP_SERVER in text:
            add_action(actions, "blocked", codex, target, "ambiguous legacy MCP reference")

    for path, server_key in (
        (target / ".mcp.json", "mcpServers"),
        (target / ".cursor/mcp.json", "mcpServers"),
        (target / ".vscode/mcp.json", "servers"),
    ):
        if not path.exists():
            continue
        text = read_text(path)
        if LEGACY_MCP_SERVER not in text:
            continue
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            add_action(actions, "blocked", path, target, "invalid JSON with legacy MCP server")
            continue
        servers = data.get(server_key)
        if isinstance(servers, dict) and LEGACY_MCP_SERVER in servers:
            add_action(
                actions,
                "edit_config",
                path,
                target,
                "remove legacy JSON MCP server",
                mode=f"json-server:{server_key}",
            )
        else:
            add_action(actions, "blocked", path, target, "ambiguous legacy MCP reference")
    return actions


def canonical_jsonl_key(line: str) -> str:
    """Return a stable key for one JSONL record without changing invalid rows."""
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return line
    if isinstance(payload, dict):
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return line


def runtime_hook_duplicates(path: Path) -> list[str]:
    """List exact duplicate runtime hook rows; distinct replay rows are kept."""
    if not path.exists():
        return []
    seen: set[str] = set()
    duplicates: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    for line in lines:
        key = canonical_jsonl_key(line)
        if key in seen:
            duplicates.append(line)
        else:
            seen.add(key)
    return duplicates


def runtime_hook_duplicate_count(path: Path) -> int:
    return len(runtime_hook_duplicates(path))


def migration_actions(target: Path) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    legacy = target / LEGACY_FIELD_ROOT
    if legacy.exists():
        add_action(
            actions,
            "migrate",
            legacy,
            target,
            "preserve legacy Field Reports state",
            target_path=FIELD_ROOT.as_posix(),
            mode="field-reports",
        )
    retrofit = target / LEGACY_RETROFIT_ROOT
    if retrofit.exists():
        add_action(
            actions,
            "migrate",
            retrofit,
            target,
            "archive legacy retrofit records",
            target_path=RETROFIT_ARCHIVE_ROOT.as_posix(),
            mode="retrofit-records",
        )
    legacy_hook_ledger = target / LEGACY_HOOK_LEDGER
    if legacy_hook_ledger.exists():
        add_action(
            actions,
            "migrate",
            legacy_hook_ledger,
            target,
            "archive legacy hook ledger",
            target_path=(HOOK_LEDGER_ARCHIVE / "executed.jsonl").as_posix(),
            mode="legacy-hook-ledger",
        )
    runtime_hook_ledger = target / RUNTIME_HOOK_LEDGER
    duplicate_count = runtime_hook_duplicate_count(runtime_hook_ledger)
    if duplicate_count:
        add_action(
            actions,
            "compact",
            runtime_hook_ledger,
            target,
            "compact exact duplicate runtime hook records",
            duplicate_records=duplicate_count,
            target_path=(HOOK_LEDGER_ARCHIVE / f"executed-duplicates-{utc_stamp()}.jsonl").as_posix(),
            mode="runtime-hook-ledger",
        )
    return actions


def text_rewrite_actions(target: Path) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    quality_gates = target / "docs/agents/QUALITY-GATES.md"
    if quality_gates.exists():
        text = read_text(quality_gates)
        if STALE_DISCIPLINE_PATH in text:
            add_action(
                actions,
                "edit_text",
                quality_gates,
                target,
                "replace retired discipline oracle path",
                mode="quality-gates-discipline-path",
            )
    return actions


def preserve_actions(target: Path) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for relpath in ("AGENTS.md", "CLAUDE.md", "CURSOR.md", ".cursorrules", "docs/agents", "docs/agents/cortex"):
        path = target / relpath
        if path.exists():
            add_action(actions, "preserve", path, target, "project-owned context or Cortex memory")
    rules = target / ".cursor/rules"
    if rules.exists():
        for path in sorted(rules.glob("*.mdc")):
            if path.name != "tilly-guidelines.mdc":
                add_action(actions, "preserve", path, target, "project-owned Cursor rule")
    return actions


def covered_by_known(path: Path, target: Path, actions: list[dict[str, Any]]) -> bool:
    raw = rel(path, target)
    for action in actions:
        action_path = action["path"]
        if raw == action_path or raw.startswith(action_path.rstrip("/") + "/"):
            return True
    return False


def blocked_unknowns(target: Path, actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blocked: list[dict[str, Any]] = []
    legacy_root = target / ".tilly"
    if legacy_root.exists():
        for path in sorted(legacy_root.rglob("*")):
            if path.is_dir() or covered_by_known(path, target, actions):
                continue
            add_action(blocked, "blocked", path, target, "unknown legacy .tilly asset")

    issue_templates = target / ".github/ISSUE_TEMPLATE"
    if issue_templates.exists():
        for path in sorted(issue_templates.glob("*tilly*")):
            if not covered_by_known(path, target, actions):
                add_action(blocked, "blocked", path, target, "unknown legacy GitHub issue template")
    return blocked


def build_plan(target: Path) -> dict[str, Any]:
    target = target.expanduser().resolve()
    if not target.exists() or not target.is_dir():
        return {"version": VERSION, "status": "FAIL", "target": str(target), "failures": [f"target is not a directory: {target}"], "writes": []}

    actions = [
        *known_removals(target),
        *mcp_config_actions(target),
        *migration_actions(target),
        *text_rewrite_actions(target),
    ]
    blocked = [item for item in actions if item["action"] == "blocked"]
    blocked.extend(blocked_unknowns(target, actions))
    actions = [item for item in actions if item["action"] != "blocked"]
    preserves = preserve_actions(target)
    required_actions = [item for item in actions if item.get("reason") not in CLEANUP_REASONS]
    required = bool(required_actions or blocked)
    status = "NEEDS_REVIEW" if blocked else "PASS"
    return {
        "version": VERSION,
        "status": status,
        "target": str(target),
        "legacy_retirement_required": required,
        "counts": {
            "remove": sum(1 for item in actions if item["action"] == "remove"),
            "migrate": sum(1 for item in actions if item["action"] == "migrate"),
            "compact": sum(1 for item in actions if item["action"] == "compact"),
            "edit_config": sum(1 for item in actions if item["action"] == "edit_config"),
            "edit_text": sum(1 for item in actions if item["action"] == "edit_text"),
            "cleanup": sum(1 for item in actions if item.get("reason") in CLEANUP_REASONS),
            "preserve": len(preserves),
            "blocked": len(blocked),
        },
        "actions": actions,
        "preserve": preserves,
        "blocked": blocked,
        "writes": [],
        "failures": [],
    }


def backup_path_for(target: Path, backup_root: Path, relpath: str) -> Path:
    return backup_root / relpath


def backup_existing(path: Path, target: Path, backup_root: Path) -> str | None:
    if not path.exists():
        return None
    destination = backup_path_for(target, backup_root, rel(path, target))
    destination.parent.mkdir(parents=True, exist_ok=True)
    if path.is_dir():
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(path, destination, symlinks=True)
    else:
        shutil.copy2(path, destination)
    return rel(destination, target)


def remove_path(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def remove_empty_parents(path: Path, target: Path) -> list[str]:
    removed: list[str] = []
    current = path.parent
    while current != target and target in current.parents:
        try:
            current.rmdir()
        except OSError:
            break
        removed.append(rel(current, target))
        current = current.parent
    return removed


def remove_toml_section(text: str, header: str) -> str:
    lines = text.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == header)
    except StopIteration:
        return text
    end = len(lines)
    for index in range(start + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            end = index
            break
    updated = [*lines[:start], *lines[end:]]
    return ("\n".join(updated).strip() + "\n") if any(line.strip() for line in updated) else ""


def edit_config(path: Path, mode: str) -> None:
    text = read_text(path)
    if mode == "toml-section":
        write_text(path, remove_toml_section(text, "[mcp_servers.tilly-cortex]"))
        return
    if mode.startswith("json-server:"):
        server_key = mode.split(":", 1)[1]
        data = json.loads(text)
        servers = data.get(server_key)
        if isinstance(servers, dict):
            servers.pop(LEGACY_MCP_SERVER, None)
        write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n")
        return
    raise ValueError(f"unknown edit mode: {mode}")


def edit_text(path: Path, mode: str) -> None:
    text = read_text(path)
    if mode == "quality-gates-discipline-path":
        write_text(path, text.replace(STALE_DISCIPLINE_PATH, CANONICAL_DISCIPLINE_PATH))
        return
    raise ValueError(f"unknown text edit mode: {mode}")


def merge_outbox(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    text = source.read_text(encoding="utf-8", errors="replace").strip()
    if text:
        existing = destination.read_text(encoding="utf-8") if destination.exists() else ""
        prefix = existing if existing.endswith("\n") or not existing else existing + "\n"
        destination.write_text(prefix + text + "\n", encoding="utf-8")
    elif not destination.exists():
        destination.touch()
    source.unlink()


def move_if_absent(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        source.unlink()
    else:
        source.replace(destination)


def migrate_field_reports(target: Path) -> None:
    legacy = target / LEGACY_FIELD_ROOT
    if not legacy.exists():
        return
    destination = target / FIELD_ROOT
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "receipts").mkdir(parents=True, exist_ok=True)
    merge_outbox(legacy / "outbox.jsonl", destination / "outbox.jsonl")
    move_if_absent(legacy / "install_id", destination / "install_id")
    move_if_absent(legacy / "DISABLED", destination / "DISABLED")
    receipts = legacy / "receipts"
    if receipts.exists():
        for receipt in sorted(receipts.glob("*.json")):
            target_receipt = destination / "receipts" / receipt.name
            if target_receipt.exists():
                target_receipt = destination / "receipts" / f"legacy-{utc_stamp()}-{receipt.name}"
            receipt.replace(target_receipt)
        try:
            receipts.rmdir()
        except OSError:
            pass
    try:
        legacy.rmdir()
    except OSError:
        pass
    remove_empty_parents(legacy, target)


def migrate_directory_contents(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    destination.mkdir(parents=True, exist_ok=True)
    for item in sorted(source.rglob("*")):
        if item.is_dir():
            continue
        relative = item.relative_to(source)
        target_item = destination / relative
        target_item.parent.mkdir(parents=True, exist_ok=True)
        if target_item.exists():
            target_item = target_item.with_name(f"legacy-{utc_stamp()}-{target_item.name}")
        item.replace(target_item)
    shutil.rmtree(source, ignore_errors=True)


def migrate_retrofit_records(target: Path) -> None:
    legacy = target / LEGACY_RETROFIT_ROOT
    destination = target / RETROFIT_ARCHIVE_ROOT
    migrate_directory_contents(legacy, destination)
    remove_empty_parents(legacy, target)


def append_archive_file(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    text = source.read_text(encoding="utf-8", errors="replace")
    if destination.exists():
        existing = destination.read_text(encoding="utf-8", errors="replace")
        prefix = existing if existing.endswith("\n") or not existing else existing + "\n"
        destination.write_text(prefix + text.rstrip("\n") + "\n", encoding="utf-8")
        source.unlink()
    else:
        source.replace(destination)


def migrate_legacy_hook_ledger(target: Path) -> None:
    legacy = target / LEGACY_HOOK_LEDGER
    destination = target / HOOK_LEDGER_ARCHIVE / "executed.jsonl"
    append_archive_file(legacy, destination)
    remove_empty_parents(legacy, target)


def compact_runtime_hook_ledger(target: Path, archive_relpath: str | None = None) -> list[str]:
    ledger = target / RUNTIME_HOOK_LEDGER
    if not ledger.exists():
        return []
    lines = ledger.read_text(encoding="utf-8", errors="replace").splitlines()
    seen: set[str] = set()
    kept: list[str] = []
    duplicates: list[str] = []
    for line in lines:
        key = canonical_jsonl_key(line)
        if key in seen:
            duplicates.append(line)
        else:
            seen.add(key)
            kept.append(line)
    if not duplicates:
        return []
    archive = target / (archive_relpath or (HOOK_LEDGER_ARCHIVE / f"executed-duplicates-{utc_stamp()}.jsonl").as_posix())
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_text("\n".join(duplicates) + "\n", encoding="utf-8")
    ledger.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
    return [rel(archive, target), rel(ledger, target)]


def ensure_local_excludes(target: Path) -> str | None:
    if field_reports is None:
        return None
    return field_reports.ensure_git_exclude(target)


def apply_plan(target: Path, *, yes: bool) -> dict[str, Any]:
    plan = build_plan(target)
    if plan["status"] == "FAIL":
        return plan
    if plan["blocked"]:
        return {**plan, "status": "NEEDS_REVIEW", "message": "legacy outside the closed catalog requires review"}
    if not yes:
        return {**plan, "status": "NEEDS_AUTH", "message": "legacy retirement writes require --yes"}

    target = target.expanduser().resolve()
    backup_root = target / BACKUP_ROOT / utc_stamp()
    writes: list[str] = []
    backups: list[str] = []
    removed_empty_dirs: list[str] = []

    exclude = ensure_local_excludes(target)
    if exclude:
        writes.append(exclude)

    for action in plan["actions"]:
        path = target / action["path"]
        if action["action"] in {"remove", "edit_config", "edit_text", "migrate", "compact"}:
            backup = backup_existing(path, target, backup_root)
            if backup:
                backups.append(backup)
        if action["action"] == "remove":
            remove_path(path)
            writes.append(action["path"])
            removed_empty_dirs.extend(remove_empty_parents(path, target))
        elif action["action"] == "edit_config":
            edit_config(path, str(action["mode"]))
            writes.append(action["path"])
        elif action["action"] == "edit_text":
            edit_text(path, str(action["mode"]))
            writes.append(action["path"])
        elif action["action"] == "migrate":
            if action.get("mode") == "field-reports":
                migrate_field_reports(target)
            elif action.get("mode") == "retrofit-records":
                migrate_retrofit_records(target)
            elif action.get("mode") == "legacy-hook-ledger":
                migrate_legacy_hook_ledger(target)
            else:
                return {
                    "version": VERSION,
                    "status": "FAIL",
                    "target": str(target),
                    "writes": writes,
                    "backups": backups,
                    "failures": [f"unknown migration mode: {action.get('mode')}"],
                }
            writes.append(action["path"])
            writes.append(str(action["target_path"]))
        elif action["action"] == "compact":
            compact_writes = compact_runtime_hook_ledger(target, str(action.get("target_path") or ""))
            writes.extend(compact_writes or [action["path"]])

    audit = audit_target(target)
    return {
        "version": VERSION,
        "status": "PASS" if audit["status"] == "PASS" else "FAIL",
        "target": str(target),
        "legacy_retirement_required": plan.get("legacy_retirement_required"),
        "counts": plan.get("counts", {}),
        "writes": sorted(set(writes)),
        "backups": backups,
        "removed_empty_dirs": sorted(set(removed_empty_dirs)),
        "post_audit": audit,
        "failures": audit.get("failures", []),
    }


def audit_target(target: Path) -> dict[str, Any]:
    plan = build_plan(target)
    active_actions = [item for item in plan["actions"] if item.get("reason") not in CLEANUP_REASONS]
    active = [*active_actions, *plan["blocked"]]
    if plan["blocked"]:
        status = "NEEDS_REVIEW"
        failures = [f"blocked legacy path: {item['path']}" for item in plan["blocked"]]
    elif active:
        status = "FAIL"
        failures = [f"legacy runtime still active: {item['path']}" for item in active]
    else:
        status = "PASS"
        failures = []
    return {
        "version": VERSION,
        "status": status,
        "target": str(target.expanduser().resolve()),
        "legacy_retirement_required": bool(active),
        "counts": plan.get("counts", {}),
        "failures": failures,
        "writes": [],
    }


def run_self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-legacy-retirement-") as tempdir:
        target = Path(tempdir)
        (target / ".agents/skills/tilly-init").mkdir(parents=True)
        (target / ".agents/skills/tilly-init/SKILL.md").write_text("name: tilly-init\n", encoding="utf-8")
        (target / "skills/tilly-guidelines").mkdir(parents=True)
        (target / "skills/tilly-guidelines/SKILL.md").write_text("Tilly Guidelines\n", encoding="utf-8")
        (target / ".cursor/rules").mkdir(parents=True)
        (target / ".cursor/rules/tilly-guidelines.mdc").write_text("legacy rule\n", encoding="utf-8")
        (target / ".cursor/rules/project.mdc").write_text("project-owned rule\n", encoding="utf-8")
        (target / ".tilly/bin").mkdir(parents=True)
        (target / ".tilly/bin/tilly_update.py").write_text("VERSION = '0.3.1'\n", encoding="utf-8")
        (target / ".tilly/cortex").mkdir(parents=True)
        (target / ".tilly/cortex/recall.sqlite").write_bytes(b"sqlite")
        (target / ".tilly/field-reports/receipts").mkdir(parents=True)
        (target / ".tilly/field-reports/outbox.jsonl").write_text('{"event":"legacy","status":"PASS"}\n', encoding="utf-8")
        (target / ".tilly/field-reports/install_id").write_text("legacy-install\n", encoding="utf-8")
        (target / ".tilly/field-reports/DISABLED").write_text("disabled\n", encoding="utf-8")
        (target / ".tilly/field-reports/receipts/one.json").write_text('{"issue_url":"legacy"}\n', encoding="utf-8")
        (target / ".tilly/retrofit").mkdir(parents=True)
        (target / ".tilly/retrofit/previous-retrofit.md").write_text("# Previous retrofit\n", encoding="utf-8")
        (target / ".codex").mkdir()
        (target / ".codex/config.toml").write_text(
            "[mcp_servers.other]\ncommand = \"true\"\n\n[mcp_servers.tilly-cortex]\ncommand = \"python3\"\n",
            encoding="utf-8",
        )
        (target / ".mcp.json").write_text(
            json.dumps({"mcpServers": {"tilly-cortex": {"command": "python3"}, "other": {"command": "true"}}}) + "\n",
            encoding="utf-8",
        )
        (target / ".vscode").mkdir()
        (target / ".vscode/mcp.json").write_text(
            json.dumps({"servers": {"tilly-cortex": {"command": "python3"}, "other": {"command": "true"}}}) + "\n",
            encoding="utf-8",
        )
        (target / ".github/ISSUE_TEMPLATE").mkdir(parents=True)
        (target / ".github/ISSUE_TEMPLATE/tilly-field-report.yml").write_text("name: Tilly Field Report\nbody: tilly-field-report@1\n", encoding="utf-8")
        (target / "AGENTS.md").write_text("# Project rules\n\nKeep local governance.\n", encoding="utf-8")
        (target / "docs/agents/cortex").mkdir(parents=True)
        (target / "docs/agents/cortex/CONTRACT.md").write_text("# Cortex\n", encoding="utf-8")
        (target / "docs/agents/QUALITY-GATES.md").write_text(
            "# Quality Gates\n\n"
            f"- `python3 {STALE_DISCIPLINE_PATH} --self-test`\n",
            encoding="utf-8",
        )
        (target / "__pycache__").mkdir()
        (target / "__pycache__/probe.pyc").write_bytes(b"pyc")
        (target / ".tes/hooks").mkdir(parents=True)
        (target / LEGACY_HOOK_LEDGER).write_text(
            json.dumps({"agent": "codex", "event": "PreToolUse", "session": "legacy", "ts": "2026-06-26T00:00:00Z"}) + "\n",
            encoding="utf-8",
        )
        (target / ".tes/runtime/hooks").mkdir(parents=True)
        duplicate_hook_record = {
            "agent": "codex",
            "event": "PreToolUse",
            "event_canonical": "PreToolUse",
            "mode": "pretooluse",
            "session": "duplicate-runtime",
            "tool": "apply_patch",
            "path": "docs/governance/policy/SKILL.md",
            "decision": "allow",
            "permission_decision": "allow",
            "marker_emitted": True,
            "ts": "2026-06-27T00:00:00Z",
        }
        runtime_lines = [
            json.dumps(duplicate_hook_record, sort_keys=True),
            json.dumps(duplicate_hook_record, sort_keys=True),
            json.dumps({**duplicate_hook_record, "session": "unique-runtime"}, sort_keys=True),
        ]
        (target / RUNTIME_HOOK_LEDGER).write_text("\n".join(runtime_lines) + "\n", encoding="utf-8")
        (target / HOOK_SMOKE_ROOT / "claude").mkdir(parents=True)
        (target / HOOK_SMOKE_ROOT / "claude/SKILL.md").write_text("# Smoke Evidence\n", encoding="utf-8")
        (target / HOOK_SMOKE_ROOT / "run_sim.py").write_text("print('residue')\n", encoding="utf-8")
        (target / HOOK_SMOKE_ROOT / "forbidden-executed.txt").write_text("EXECUTED\n", encoding="utf-8")

        before = audit_target(target)
        if before["status"] != "FAIL":
            failures.append("audit must fail before legacy retirement")
        plan = build_plan(target)
        if plan["status"] != "PASS":
            failures.append("known legacy fixture must be plannable")
        if not plan["legacy_retirement_required"]:
            failures.append("known legacy fixture must require retirement")
        if not any(item.get("action") == "edit_text" for item in plan["actions"]):
            failures.append("stale quality gate discipline path must require text migration")
        if not any(item.get("mode") == "legacy-hook-ledger" for item in plan["actions"]):
            failures.append("legacy hook ledger must require archive migration")
        if not any(item.get("action") == "compact" and item.get("mode") == "runtime-hook-ledger" for item in plan["actions"]):
            failures.append("exact duplicate runtime hook records must require compaction")
        if not any(item.get("path") == f"{HOOK_SMOKE_ROOT.as_posix()}/run_sim.py" for item in plan["actions"]):
            failures.append("legacy hook audit harness script must be planned for removal")
        result = apply_plan(target, yes=True)
        if result["status"] != "PASS":
            failures.append("known legacy fixture must apply cleanly")
            failures.extend(result.get("failures", []))
        for relpath in (
            ".agents/skills/tilly-init",
            "skills/tilly-guidelines",
            ".cursor/rules/tilly-guidelines.mdc",
            ".tilly/bin",
            ".tilly/field-reports",
            ".tilly/retrofit",
            ".github/ISSUE_TEMPLATE/tilly-field-report.yml",
            "__pycache__",
            ".tes/hooks/executed.jsonl",
            ".tes/runtime/hook-smoke/run_sim.py",
            ".tes/runtime/hook-smoke/forbidden-executed.txt",
        ):
            if (target / relpath).exists():
                failures.append(f"legacy path still exists after apply: {relpath}")
        if not (target / ".tes/field-reports/outbox.jsonl").exists():
            failures.append("Field Reports outbox must migrate")
        if not (target / ".tes/field-reports/DISABLED").exists():
            failures.append("Field Reports DISABLED sentinel must migrate")
        if not (target / ".tes/legacy-retirement/retrofit/previous-retrofit.md").exists():
            failures.append("legacy retrofit records must migrate to TES archive")
        if not (target / ".tes/legacy-retirement/hooks/executed.jsonl").exists():
            failures.append("legacy hook ledger must migrate to TES archive")
        deduped_runtime = (target / RUNTIME_HOOK_LEDGER).read_text(encoding="utf-8").splitlines()
        if len(deduped_runtime) != 2:
            failures.append("runtime hook ledger must keep one copy of exact duplicates plus unique records")
        if not list((target / ".tes/legacy-retirement/hooks").glob("executed-duplicates-*.jsonl")):
            failures.append("runtime hook duplicate rows must be archived before compaction")
        if not (target / HOOK_SMOKE_ROOT / "claude/SKILL.md").exists():
            failures.append("hook smoke SKILL evidence must be preserved")
        if not (target / ".cursor/rules/project.mdc").exists():
            failures.append("project-owned Cursor rule must be preserved")
        if not (target / "AGENTS.md").exists():
            failures.append("root context must be preserved")
        if "tilly-cortex" in read_text(target / ".codex/config.toml"):
            failures.append("Codex legacy MCP server must be removed")
        if "tilly-cortex" in read_text(target / ".mcp.json"):
            failures.append("JSON legacy MCP server must be removed")
        if "other" not in read_text(target / ".mcp.json"):
            failures.append("other MCP servers must be preserved")
        if "tilly-cortex" in read_text(target / ".vscode/mcp.json"):
            failures.append("VS Code legacy MCP server must be removed")
        if "other" not in read_text(target / ".vscode/mcp.json"):
            failures.append("VS Code non-TES MCP servers must be preserved")
        quality_text = read_text(target / "docs/agents/QUALITY-GATES.md")
        if STALE_DISCIPLINE_PATH in quality_text:
            failures.append("stale quality gate discipline path must be removed")
        if CANONICAL_DISCIPLINE_PATH not in quality_text:
            failures.append("canonical quality gate discipline path must be present")

    with tempfile.TemporaryDirectory(prefix="tes-legacy-retirement-blocked-") as tempdir:
        target = Path(tempdir)
        (target / ".tilly/custom").mkdir(parents=True)
        (target / ".tilly/custom/state.json").write_text("{}\n", encoding="utf-8")
        blocked = build_plan(target)
        if blocked["status"] != "NEEDS_REVIEW":
            failures.append("unknown .tilly asset must block")
        applied = apply_plan(target, yes=True)
        if applied["status"] != "NEEDS_REVIEW":
            failures.append("apply must not remove unknown legacy assets")
        if not (target / ".tilly/custom/state.json").exists():
            failures.append("unknown legacy asset must remain")

    return {"version": VERSION, "status": "PASS" if not failures else "FAIL", "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=("plan", "apply", "audit"), default="plan")
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = run_self_test()
    elif args.command == "plan":
        result = build_plan(args.target)
    elif args.command == "apply":
        result = apply_plan(args.target, yes=args.yes)
    else:
        result = audit_target(args.target)

    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-legacy-retirement] " + result["status"])
    if result["status"] == "PASS":
        return 0
    if result["status"] in {"NEEDS_REVIEW", "NEEDS_AUTH"}:
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
