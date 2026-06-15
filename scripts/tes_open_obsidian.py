#!/usr/bin/env python3
"""Preflight and optionally open a TES project in Obsidian."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


VERSION = "0.3.182"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def helper_path(name: str) -> Path | None:
    candidates = (
        script_dir() / name,
        script_dir().parent / "scripts" / name,
    )
    for path in candidates:
        if path.exists():
            return path
    return None


def decode_first_json(text: str) -> dict[str, Any]:
    stripped = text.lstrip()
    decoder = json.JSONDecoder()
    data, _ = decoder.raw_decode(stripped)
    if not isinstance(data, dict):
        return {}
    return data


def run_json_helper(name: str, target: Path) -> dict[str, Any]:
    path = helper_path(name)
    if path is None:
        return {"status": "MISSING", "failures": [f"missing helper: {name}"]}
    result = subprocess.run(
        [sys.executable, str(path), "--target", str(target)],
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        payload = decode_first_json(result.stdout)
    except json.JSONDecodeError:
        payload = {"status": "FAIL", "failures": ["helper did not emit JSON"]}
    payload.setdefault("failures", [])
    if result.returncode != 0 and not payload["failures"]:
        payload["failures"] = [line for line in result.stderr.splitlines() if line]
    return payload


def detect_obsidian() -> dict[str, Any]:
    system = platform.system()
    candidates: list[str] = []
    cli = shutil.which("obsidian")
    app_found = False
    if system == "Darwin":
        candidates = [
            "/Applications/Obsidian.app",
            str(Path.home() / "Applications/Obsidian.app"),
        ]
        app_found = any(Path(path).exists() for path in candidates)
        if not app_found:
            result = subprocess.run(
                ["mdfind", "kMDItemCFBundleIdentifier == 'md.obsidian'"],
                text=True,
                capture_output=True,
                check=False,
            )
            app_found = result.returncode == 0 and bool(result.stdout.strip())
            if result.stdout.strip():
                candidates.extend(result.stdout.splitlines())
    if cli:
        candidates.append(cli)
    return {
        "system": system,
        "found": app_found or cli is not None,
        "candidates": candidates,
        "cli": {
            "found": cli is not None,
            "path": cli,
            "requires": "Obsidian 1.12+ installer with Command line interface enabled",
            "source": "https://obsidian.md/help/cli",
        },
    }


def obsidian_vault_root(target: Path) -> Path:
    return target / "docs/agents"


def build_open_action(target: Path, app: dict[str, Any]) -> dict[str, Any]:
    vault_root = obsidian_vault_root(target)
    project_context = vault_root / "PROJECT-CONTEXT.md"
    context_arg = "path=PROJECT-CONTEXT.md"
    if app.get("cli", {}).get("found") and project_context.exists():
        return {
            "command": ["obsidian", "open", context_arg],
            "cwd": str(vault_root),
            "method": "obsidian_cli_open_docs_agents_project_context",
            "source": "https://obsidian.md/help/cli",
            "vault_root": str(vault_root),
            "vault_root_relative": "docs/agents",
        }
    if app["system"] == "Darwin":
        return {
            "command": ["open", "-a", "Obsidian", str(vault_root)],
            "cwd": None,
            "method": "macos_open_docs_agents_vault",
            "source": "macOS open fallback",
            "vault_root": str(vault_root),
            "vault_root_relative": "docs/agents",
        }
    return {
        "command": ["obsidian", "open", context_arg],
        "cwd": str(vault_root),
        "method": "obsidian_cli_expected",
        "source": "https://obsidian.md/help/cli",
        "vault_root": str(vault_root),
        "vault_root_relative": "docs/agents",
    }


def obsidian_hashes(target: Path) -> dict[str, str]:
    root = target / ".obsidian"
    if not root.exists():
        return {}
    hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            hashes[path.relative_to(target).as_posix()] = sha256_file(path)
    return hashes


def analyze(target: Path, open_requested: bool, dry_run: bool) -> dict[str, Any]:
    target = target.resolve()
    failures: list[str] = []
    warnings: list[str] = []
    vault_root = obsidian_vault_root(target)
    if not target.exists():
        failures.append(f"target does not exist: {target}")

    docs_agents = vault_root
    if not docs_agents.exists():
        failures.append("missing docs/agents/**; run /tes-init first")

    context = run_json_helper("project_context_oracle.py", target) if docs_agents.exists() else {
        "status": "NOT_RUN",
        "failures": ["missing docs/agents/**"],
    }
    alignment = run_json_helper("project_alignment_oracle.py", target) if docs_agents.exists() else {
        "status": "NOT_RUN",
        "failures": ["missing docs/agents/**"],
    }
    if context.get("status") != "PASS":
        failures.extend(f"project-context: {item}" for item in context.get("failures", []))
    if alignment.get("status") != "PASS":
        failures.extend(f"project-alignment: {item}" for item in alignment.get("failures", []))

    before_hashes = obsidian_hashes(target)
    obsidian_dir = target / ".obsidian"
    obsidian_state = "present_project_owned" if obsidian_dir.exists() else "absent"
    if obsidian_state == "absent" and open_requested:
        warnings.append("opening may let Obsidian create project-owned .obsidian/** state")

    app = detect_obsidian()
    action: dict[str, Any] = {
        "requested": open_requested,
        "dry_run": dry_run,
        "command": None,
        "cwd": None,
        "method": None,
        "status": "NOT_REQUESTED",
        "vault_root": str(vault_root),
        "vault_root_relative": "docs/agents",
    }

    status = "BLOCKED" if failures else "READY"
    if not failures and open_requested:
        open_action = build_open_action(target, app)
        command = open_action["command"]
        action.update(open_action)
        vault_root_ok = True
        if Path(str(action.get("vault_root"))).resolve() != vault_root.resolve():
            action["status"] = "WRONG_VAULT_ROOT"
            status = "BLOCKED"
            failures.append("open action must target docs/agents as the Obsidian vault root")
            vault_root_ok = False
        elif "docs/agents" not in str(action.get("vault_root_relative")):
            action["status"] = "WRONG_VAULT_ROOT"
            status = "BLOCKED"
            failures.append("open action must expose docs/agents vault_root_relative evidence")
            vault_root_ok = False
        if dry_run and vault_root_ok:
            action["status"] = "WOULD_OPEN"
            status = "READY"
        elif not vault_root_ok:
            pass
        elif not app["found"]:
            action["status"] = "APP_NOT_FOUND"
            status = "BLOCKED"
            failures.append("Obsidian application not found")
        else:
            result = subprocess.run(
                command,
                cwd=open_action["cwd"],
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode == 0:
                action["status"] = "OPENED"
                status = "OPENED"
            else:
                action["status"] = "OPEN_FAILED"
                status = "BLOCKED"
                failures.extend(line for line in result.stderr.splitlines() if line)

    after_hashes = obsidian_hashes(target)
    if before_hashes != after_hashes and not open_requested:
        failures.append(".obsidian/** changed during preflight")
        status = "BLOCKED"

    return {
        "version": VERSION,
        "status": status,
        "target": str(target),
        "vault_root": str(vault_root),
        "vault_root_relative": "docs/agents",
        "docs_agents": docs_agents.exists(),
        "project_context_status": context.get("status"),
        "project_alignment_status": alignment.get("status"),
        "obsidian_state": obsidian_state,
        "obsidian_files_checked": len(before_hashes),
        "obsidian_hashes_unchanged": before_hashes == after_hashes,
        "app": app,
        "action": action,
        "warnings": warnings,
        "failures": failures,
    }


def write_fixture(target: Path, with_obsidian: bool = False) -> None:
    (target / "src").mkdir(parents=True, exist_ok=True)
    (target / "README.md").write_text("# Obsidian Open Fixture\n\nFixture for TES.\n", encoding="utf-8")
    (target / "package.json").write_text(
        json.dumps(
            {
                "name": "obsidian-open-fixture",
                "version": "0.0.0",
                "private": True,
                "scripts": {"test": "node src/index.js"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (target / "src/index.js").write_text("console.log('fixture');\n", encoding="utf-8")
    if with_obsidian:
        (target / ".obsidian").mkdir(parents=True, exist_ok=True)
        (target / ".obsidian/app.json").write_text('{"newFileLocation":"current"}\n', encoding="utf-8")
    subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)


def run_tes_init(target: Path) -> list[str]:
    path = helper_path("tes_init.py")
    if path is None:
        return ["missing helper: tes_init.py"]
    result = subprocess.run(
        [sys.executable, str(path), "--target", str(target), "--yes"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return []
    return [*result.stdout.splitlines(), *result.stderr.splitlines()]


def self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-open-obsidian-") as tempdir:
        missing = Path(tempdir) / "missing-context"
        missing.mkdir()
        missing_result = analyze(missing, open_requested=False, dry_run=True)
        if missing_result["status"] != "BLOCKED":
            failures.append("missing context fixture must block")

        ready = Path(tempdir) / "ready"
        ready.mkdir()
        write_fixture(ready)
        failures.extend(run_tes_init(ready))
        ready_result = analyze(ready, open_requested=True, dry_run=True)
        if ready_result["status"] != "READY":
            failures.append(f"ready fixture must be READY, got {ready_result['status']}")
        if ready_result["action"]["status"] != "WOULD_OPEN":
            failures.append("dry-run open must report WOULD_OPEN")
        if Path(str(ready_result["action"].get("vault_root"))).resolve() != (ready / "docs/agents").resolve():
            failures.append("open action must target docs/agents vault root")
        if (ready / ".obsidian").exists():
            failures.append("dry-run must not create .obsidian/**")
        if (ready / "docs/agents/.obsidian").exists():
            failures.append("dry-run must not create docs/agents/.obsidian/**")

        cli_action = build_open_action(
            ready,
            {"system": platform.system(), "found": True, "cli": {"found": True}},
        )
        if Path(str(cli_action.get("cwd"))).resolve() != (ready / "docs/agents").resolve():
            failures.append("CLI open action must use docs/agents as cwd")
        if "path=PROJECT-CONTEXT.md" not in cli_action.get("command", []):
            failures.append("CLI open action must target PROJECT-CONTEXT.md from docs/agents vault root")

        owned = Path(tempdir) / "owned-obsidian"
        owned.mkdir()
        write_fixture(owned, with_obsidian=True)
        before = sha256_file(owned / ".obsidian/app.json")
        failures.extend(run_tes_init(owned))
        owned_result = analyze(owned, open_requested=False, dry_run=True)
        after = sha256_file(owned / ".obsidian/app.json")
        if owned_result["status"] != "READY":
            failures.append(f"owned .obsidian fixture must be READY, got {owned_result['status']}")
        if before != after:
            failures.append(".obsidian/app.json must remain unchanged during preflight")

    installed_mode = script_dir().name == "bin" and script_dir().parent.name == ".tes"
    payload = {
        "version": VERSION,
        "coverage": "installed-helper-contract" if installed_mode else "source-package-contract",
        "failures": failures,
        "self_test_mode": "installed" if installed_mode else "package",
        "status": "FAIL" if failures else "PASS",
    }
    print(json.dumps(payload, indent=2))
    print("[tes-open-obsidian] " + payload["status"])
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=Path("."))
    parser.add_argument("--open", action="store_true", help="open the target in Obsidian after preflight")
    parser.add_argument("--dry-run", action="store_true", help="show the open action without launching Obsidian")
    parser.add_argument("--json-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    result = analyze(args.target, open_requested=args.open, dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
    if not args.json_only:
        print(f"[tes-open-obsidian] {result['status']}")
    return 0 if result["status"] in {"READY", "OPENED"} else 1


if __name__ == "__main__":
    sys.exit(main())
