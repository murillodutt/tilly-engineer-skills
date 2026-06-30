#!/usr/bin/env python3
"""Canary admission gate: block false readiness when Git/pre-push/pre-commit or
per-host native hook evidence is absent or unproven.

This is MAINTAINER/canary-admission infrastructure, not delivered adopter
behavior. TES does NOT auto-install a strict pre-commit gate for adopters
(INSTALL.md:276 keeps project-scoped hooks idempotent and advisory). This oracle
is the gate a canary REPLAY session runs against a candidate target before it
may claim READY_FOR_GOAL_MAESTRO_CANARY. It exists because no prior surface
materially proved Git admission or refused cross-host native hook claims:
installed_certification_oracle has zero Git checks, and hook runtime evidence is
host-local (no host keeps a native ledger; only the hook's own runtime record
proves firing — Claude/Codex/Cursor confirmed).

Hard contract (never relaxed):
  - Git admission BLOCKS when the target is not a Git work tree.
  - On a Git-backed target, BLOCKS when the Field Reports pre-push gate is
    absent, and when strict pre-commit proof is absent.
  - precommit_enforced / prepush_installed / git_clean are emitted ONLY with
    material Git evidence; absent evidence yields false, never silence.
  - Each host's native hook claim is proven only by that host's own runtime
    records. A configured-but-unobserved host is CONFIGURED_NOT_OBSERVED, never
    native PASS. Records from one host MUST NOT fill another host's claim.

Consumer: maintainer/canary gate (self-test + replay admission). Not delivered
to adopters; not a HELPER_FILE.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import field_reports
import tes_install


VERSION = "0.3.232"
SCHEMA = "tes-canary-admission@1"
AGENTS = tes_install.AGENTS  # ("codex", "claude", "cursor")

# A host whose hook runtime is proven by that host's own records is NATIVE_PASS.
# A host configured but with no runtime record of its own is CONFIGURED_NOT_OBSERVED.
NATIVE_PASS = "NATIVE_PASS"
CONFIGURED_NOT_OBSERVED = "CONFIGURED_NOT_OBSERVED"
NOT_CONFIGURED = "NOT_CONFIGURED"


def is_git_work_tree(target: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "--is-inside-work-tree"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def git_is_clean(target: Path) -> bool | None:
    """True/False for clean/dirty; None when target is not a Git work tree."""
    if not is_git_work_tree(target):
        return None
    result = subprocess.run(
        ["git", "-C", str(target), "status", "--porcelain", "--untracked-files=all"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() == ""


def prepush_evidence(target: Path) -> dict[str, Any]:
    """Material proof of the Field Reports pre-push gate, reusing field_reports."""
    git_dir = target / ".git"
    if not git_dir.exists():
        return {"prepush_installed": False, "reason": "no .git directory"}
    hook_info = field_reports.resolve_pre_push_hook(target, git_dir)
    if hook_info.get("status") != "PASS":
        return {"prepush_installed": False, "reason": str(hook_info.get("reason") or "hook resolution blocked")}
    hook = hook_info.get("hook")
    hook_path = Path(str(hook)) if hook else None
    if not hook_path or not hook_path.is_file():
        return {"prepush_installed": False, "reason": "pre-push hook file absent", "hook": str(hook_path or "")}
    text = hook_path.read_text(encoding="utf-8", errors="ignore")
    if not field_reports.has_gate_pre_git_push(text):
        return {
            "prepush_installed": False,
            "reason": "pre-push hook present but missing Field Reports gate marker",
            "hook": str(hook_path),
        }
    return {"prepush_installed": True, "hook": str(hook_path), "mode": hook_info.get("mode")}


def precommit_evidence(target: Path) -> dict[str, Any]:
    """Material proof of a strict pre-commit gate file with a runnable command."""
    git_dir = target / ".git"
    if not git_dir.exists():
        return {"precommit_enforced": False, "reason": "no .git directory"}
    hooks_dir = git_dir / "hooks"
    configured = field_reports.git_config_get(target, "core.hooksPath")
    if configured and configured != "/dev/null":
        configured_path = Path(configured).expanduser()
        hooks_dir = configured_path if configured_path.is_absolute() else target / configured_path
    hook_path = hooks_dir / "pre-commit"
    if not hook_path.is_file():
        return {"precommit_enforced": False, "reason": "pre-commit hook file absent", "hook": str(hook_path)}
    text = hook_path.read_text(encoding="utf-8", errors="ignore")
    # Strict means the hook actually invokes a TES gate, not an empty stub.
    has_strict = ("--strict" in text) or ("commit:check" in text) or ("commit:closure" in text) or (
        "discipline_oracle" in text
    ) or ("project_context_oracle" in text)
    if not has_strict:
        return {
            "precommit_enforced": False,
            "reason": "pre-commit present but not a strict TES gate",
            "hook": str(hook_path),
        }
    return {"precommit_enforced": True, "hook": str(hook_path)}


def git_admission(target: Path) -> dict[str, Any]:
    """Block readiness unless Git, pre-push, and strict pre-commit are proven."""
    blockers: list[str] = []
    if not is_git_work_tree(target):
        # No Git: every Git claim is false, and admission is BLOCKED, not skipped.
        return {
            "status": "BLOCKED",
            "git_work_tree": False,
            "git_clean": False,
            "prepush_installed": False,
            "precommit_enforced": False,
            "blockers": ["target is not a Git work tree; canary admission requires Git"],
        }
    clean = git_is_clean(target)
    pre_push = prepush_evidence(target)
    pre_commit = precommit_evidence(target)
    if not pre_push.get("prepush_installed"):
        blockers.append(f"Field Reports pre-push gate absent: {pre_push.get('reason')}")
    if not pre_commit.get("precommit_enforced"):
        blockers.append(f"strict pre-commit gate absent: {pre_commit.get('reason')}")
    if clean is False:
        blockers.append("Git work tree is dirty")
    return {
        "status": "BLOCKED" if blockers else "PASS",
        "git_work_tree": True,
        "git_clean": bool(clean),
        "prepush_installed": bool(pre_push.get("prepush_installed")),
        "precommit_enforced": bool(pre_commit.get("precommit_enforced")),
        "prepush": pre_push,
        "precommit": pre_commit,
        "blockers": blockers,
    }


def host_hook_admission(target: Path) -> dict[str, Any]:
    """Per-host native hook claim. A host is NATIVE_PASS only when its OWN runtime
    records prove firing; configured-but-unobserved is CONFIGURED_NOT_OBSERVED.
    Records from one host never fill another host's claim.
    """
    hosts: dict[str, Any] = {}
    blockers: list[str] = []
    for host in AGENTS:
        # Scope evidence to THIS host: hook_health_payload labels each host's
        # events OBSERVED/CONFIGURED/NOT_CONFIGURED from that host's own records.
        payload = tes_install.hook_health_payload(target, current_host=host)
        host_events = payload.get("agents", {}).get(host, {}).get("events", [])
        observed = any(event.get("state") == "OBSERVED" for event in host_events)
        configured = any(event.get("state") in {"OBSERVED", "CONFIGURED"} for event in host_events)
        if observed:
            klass = NATIVE_PASS
        elif configured:
            klass = CONFIGURED_NOT_OBSERVED
        else:
            klass = NOT_CONFIGURED
        hosts[host] = {
            "class": klass,
            "observed": observed,
            "configured": configured,
            "floor_status": payload.get("floor_status"),
            "ceiling_status": payload.get("ceiling_status"),
        }
        if klass == CONFIGURED_NOT_OBSERVED:
            blockers.append(f"{host}: configured but no native runtime evidence (CONFIGURED_NOT_OBSERVED)")
    native_pass_hosts = sorted(h for h, info in hosts.items() if info["class"] == NATIVE_PASS)
    return {
        "status": "NEEDS_EVIDENCE" if blockers else "PASS",
        "hosts": hosts,
        "native_pass_hosts": native_pass_hosts,
        "blockers": blockers,
    }


def evaluate(target: Path) -> dict[str, Any]:
    target = target.expanduser().resolve()
    git = git_admission(target)
    hooks = host_hook_admission(target)
    blockers = list(git.get("blockers", [])) + list(hooks.get("blockers", []))
    # Git admission is a hard gate; hook evidence gaps are NEEDS_EVIDENCE, not a
    # silent PASS. Overall status never claims readiness while either is unmet.
    if git.get("status") == "BLOCKED":
        status = "BLOCKED"
    elif hooks.get("status") == "NEEDS_EVIDENCE":
        status = "NEEDS_EVIDENCE"
    else:
        status = "PASS"
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "target": str(target),
        "status": status,
        "git_admission": git,
        "host_hook_admission": hooks,
        "blockers": blockers,
        # Never claim these without material evidence (Gap 1 truthfulness).
        "claims": {
            "git_clean": bool(git.get("git_clean")),
            "prepush_installed": bool(git.get("prepush_installed")),
            "precommit_enforced": bool(git.get("precommit_enforced")),
            "native_hook_pass_hosts": hooks.get("native_pass_hosts", []),
        },
    }


def _init_git(target: Path) -> None:
    subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=target, text=True, capture_output=True, check=False)
    subprocess.run(["git", "config", "user.name", "t"], cwd=target, text=True, capture_output=True, check=False)


def _write_prepush(target: Path) -> None:
    hooks = target / ".git/hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "pre-push"
    hook.write_text(field_reports.gate_pre_git_push_shell(), encoding="utf-8")
    hook.chmod(0o755)


def _write_strict_precommit(target: Path) -> None:
    hooks = target / ".git/hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "pre-commit"
    hook.write_text(
        "#!/bin/sh\n# strict TES canary gate\npython3 .tes/bin/project_context_oracle.py --target . --strict\n",
        encoding="utf-8",
    )
    hook.chmod(0o755)


def _write_host_runtime_record(target: Path, host: str) -> None:
    """Write a single host's own SessionStart + PreToolUse runtime records."""
    ledger = target / tes_install.HOOK_SENTINEL_PATH
    ledger.parent.mkdir(parents=True, exist_ok=True)
    casing = {
        "codex": [("SessionStart", "SessionStart", "session_start"), ("PreToolUse", "PreToolUse", "pretooluse")],
        "claude": [("SessionStart", "SessionStart", "session_start"), ("PreToolUse", "PreToolUse", "pretooluse")],
        "cursor": [
            ("sessionStart", "sessionStart", "session_start"),
            ("preToolUse", "PreToolUse", "pretooluse"),
        ],
    }[host]
    records = []
    for event, canonical, mode in casing:
        rec = {
            "agent": host,
            "event": event,
            "event_canonical": canonical,
            "mode": mode,
            "session": f"obs-{host}",
            "ts": "2026-06-30T00:00:00Z",
        }
        if mode == "pretooluse":
            rec["schema_version"] = "pretooluse_decision@2"
        records.append(rec)
    with ledger.open("a", encoding="utf-8") as handle:
        for rec in records:
            handle.write(json.dumps(rec, sort_keys=True) + "\n")


def _configure_host_hooks(target: Path, host: str) -> None:
    """Configure a host's hooks on disk (so configured_hook_events sees them)."""
    if host == "claude":
        path = target / ".claude/settings.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "hooks": {
                        "SessionStart": [{"hooks": [{"command": "python3 .tes/bin/tes_install.py hook --agent claude --target ."}]}],
                        "PreToolUse": [{"matcher": "*", "hooks": [{"command": "python3 .tes/bin/tes_install.py hook --agent claude --target ."}]}],
                    }
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    elif host == "codex":
        path = target / ".codex/config.toml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            '[[hooks.SessionStart]]\ncommand = "python3 .tes/bin/tes_install.py hook --agent codex --target ."\n'
            '[[hooks.PreToolUse]]\ncommand = "python3 .tes/bin/tes_install.py hook --agent codex --target ."\n',
            encoding="utf-8",
        )
    elif host == "cursor":
        path = target / ".cursor/hooks.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
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
    lock = target / ".tes/tes-install-lock.json"
    lock.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if lock.is_file():
        try:
            existing = json.loads(lock.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    surfaces = set(existing.get("attached_surfaces", []))
    surfaces.add("hooks")
    existing["attached_surfaces"] = sorted(surfaces)
    lock.write_text(json.dumps(existing, sort_keys=True) + "\n", encoding="utf-8")


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-canary-admission-") as tempdir:
        root = Path(tempdir)

        # 1) No Git repo, but an admission report would claim readiness -> BLOCKED.
        no_git = root / "no-git"
        no_git.mkdir()
        result = evaluate(no_git)
        if result["status"] != "BLOCKED":
            failures.append(f"no-Git target must BLOCK admission, got {result['status']}")
        if result["git_admission"]["git_work_tree"] is not False:
            failures.append("no-Git target must report git_work_tree=False")
        if result["claims"]["prepush_installed"] or result["claims"]["precommit_enforced"] or result["claims"]["git_clean"]:
            failures.append("no-Git target must NOT claim prepush_installed/precommit_enforced/git_clean")

        # 2) Git but no pre-push and no strict pre-commit -> BLOCKED naming both.
        git_only = root / "git-only"
        git_only.mkdir()
        _init_git(git_only)
        git_only_result = evaluate(git_only)
        if git_only_result["status"] != "BLOCKED":
            failures.append("Git target without gates must BLOCK admission")
        blob = " ".join(git_only_result["git_admission"]["blockers"])
        if "pre-push" not in blob or "pre-commit" not in blob:
            failures.append("Git-only target must name both missing pre-push and pre-commit gates")

        # 3) Git + pre-push + strict pre-commit, clean tree -> git_admission PASS
        #    with all three claims true on material evidence.
        full = root / "full"
        full.mkdir()
        _init_git(full)
        _write_prepush(full)
        _write_strict_precommit(full)
        full_git = git_admission(full.resolve())
        if full_git["status"] != "PASS":
            failures.append(f"fully-gated Git target must PASS git_admission, got {full_git['status']}: {full_git['blockers']}")
        if not (full_git["prepush_installed"] and full_git["precommit_enforced"]):
            failures.append("fully-gated target must claim prepush_installed and precommit_enforced on real evidence")

        # 4) Per-host native hook truthfulness: only Claude has its own runtime
        #    records; Codex+Cursor are configured but unobserved. Claude must be
        #    NATIVE_PASS; the others CONFIGURED_NOT_OBSERVED — never filled by
        #    Claude's records. Overall hooks status NEEDS_EVIDENCE.
        hosts_target = root / "hosts"
        hosts_target.mkdir()
        _init_git(hosts_target)
        for host in AGENTS:
            _configure_host_hooks(hosts_target, host)
        _write_host_runtime_record(hosts_target, "claude")  # only Claude observed
        hooks = host_hook_admission(hosts_target.resolve())
        if hooks["hosts"]["claude"]["class"] != NATIVE_PASS:
            failures.append("Claude with its own runtime records must be NATIVE_PASS")
        for other in ("codex", "cursor"):
            if hooks["hosts"][other]["class"] != CONFIGURED_NOT_OBSERVED:
                failures.append(
                    f"{other} configured without its own records must be CONFIGURED_NOT_OBSERVED "
                    f"(no cross-host evidence filling), got {hooks['hosts'][other]['class']}"
                )
        if hooks["status"] != "NEEDS_EVIDENCE":
            failures.append("hook admission with configured-but-unobserved hosts must be NEEDS_EVIDENCE")
        if hooks["native_pass_hosts"] != ["claude"]:
            failures.append(f"only Claude may be a native_pass host, got {hooks['native_pass_hosts']}")

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "coverage": "canary-admission-git-gate-and-per-host-hook-truthfulness",
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Canary admission gate (Git + per-host hook evidence).")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--target", type=Path, default=Path("."))
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args(argv)

    result = self_test() if args.self_test else evaluate(args.target)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json_only:
        print("[canary-admission] " + result["status"])
    if args.self_test:
        return 0 if result["status"] == "PASS" else 1
    # As a target gate, PASS is the only admission; BLOCKED/NEEDS_EVIDENCE are non-zero.
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
