#!/usr/bin/env python3
"""Canonical TES Git gate contract.

This module owns the installed Git-gate evidence used by canary admission,
installed certification, and hook-manager tests. Field Reports pre-push drain is
an additive transport behavior; it never satisfies the blocking quality gate.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
from typing import Any

import field_reports


SCHEMA = "tes-git-gate-contract@1"
VERSION = "0.3.244"

PRECOMMIT_GATE_TOKENS = ("commit:check", "commit:closure", "discipline_oracle", "project_context_oracle")
PREPUSH_GATE_TOKENS = ("prepush:check", "commit:check", "discipline_oracle", "project_context_oracle", "gate-pre-git")
CANONICAL_DISCIPLINE_ORACLES = (
    ".agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py",
    ".claude/skills/tes-engineering-discipline/scripts/discipline_oracle.py",
)
PROJECT_CONTEXT_ORACLES = (
    ".tes/bin/project_context_oracle.py",
    "scripts/project_context_oracle.py",
)


def is_git_work_tree(target: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "--is-inside-work-tree"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def git_is_clean(target: Path) -> bool | None:
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


def strip_shell_comments(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        in_single = in_double = False
        cut = None
        for i, ch in enumerate(line):
            if ch == "'" and not in_double:
                in_single = not in_single
            elif ch == '"' and not in_single:
                in_double = not in_double
            elif ch == "#" and not in_single and not in_double and (i == 0 or line[i - 1].isspace()):
                cut = i
                break
        out.append(line[:cut] if cut is not None else line)
    return "\n".join(out)


def package_has_script(target: Path, script_name: str) -> bool:
    try:
        data = json.loads((target / "package.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    scripts = data.get("scripts") if isinstance(data, dict) else None
    return isinstance(scripts, dict) and isinstance(scripts.get(script_name), str)


def resolve_husky_active_entrypoint(target: Path, hooks_path: object, hook_name: str) -> Path | None:
    if not hooks_path:
        return None
    configured = Path(str(hooks_path)).expanduser()
    hooks_dir = configured if configured.is_absolute() else target / configured
    if hooks_dir.name == "_" and hooks_dir.parent.name == ".husky":
        return hooks_dir.parent / hook_name
    return None


def _shell_words(line: str) -> list[str]:
    try:
        return shlex.split(line, comments=False, posix=True)
    except ValueError:
        return []


def _shell_lines(code: str) -> list[list[str]]:
    return [_shell_words(line.strip()) for line in code.splitlines() if line.strip()]


def shell_invokes_npm_script(code: str, script_name: str) -> bool:
    for words in _shell_lines(code):
        for idx, word in enumerate(words):
            if word != "npm":
                continue
            if idx + 1 >= len(words) or words[idx + 1] != "run":
                continue
            rest = words[idx + 2 :]
            for item in rest:
                if item.startswith("-"):
                    continue
                if item == script_name:
                    return True
                break
    return False


def shell_invokes_python_file(code: str, relpath: str, *, required_args: tuple[str, ...] = ()) -> bool:
    for words in _shell_lines(code):
        if not words:
            continue
        for idx, word in enumerate(words):
            if Path(word).name not in {"python", "python3"}:
                continue
            rest = words[idx + 1 :]
            if relpath not in rest:
                continue
            if all(arg in rest for arg in required_args):
                return True
    return False


def resolved_gate_commands(target: Path, code: str, *, hook_type: str) -> tuple[list[dict[str, str]], list[str], list[str]]:
    matched: list[str] = []
    resolved: list[dict[str, str]] = []
    rejected: list[str] = []

    if hook_type == "pre-push" and shell_invokes_npm_script(code, "prepush:check"):
        matched.append("prepush:check")
        if not package_has_script(target, "prepush:check"):
            rejected.append("package.json scripts.prepush:check absent")
        elif shutil.which("npm") is None:
            rejected.append("npm unavailable for scripts.prepush:check")
        else:
            resolved.append({"kind": "npm-prepush", "command": "npm run --silent prepush:check"})

    if shell_invokes_npm_script(code, "commit:check"):
        matched.append("commit:check")
        if not package_has_script(target, "commit:check"):
            rejected.append("package.json scripts.commit:check absent")
        elif shutil.which("npm") is None:
            rejected.append("npm unavailable for scripts.commit:check")
        else:
            resolved.append({"kind": "npm", "command": "npm run --silent commit:check"})

    if "discipline_oracle" in code:
        matched_path = False
        for relpath in CANONICAL_DISCIPLINE_ORACLES:
            if shell_invokes_python_file(code, relpath, required_args=("--self-test",)):
                if "discipline_oracle" not in matched:
                    matched.append("discipline_oracle")
                matched_path = True
                if (target / relpath).is_file():
                    resolved.append({"kind": "tes-discipline", "command": f"python3 {relpath} --self-test"})
                else:
                    rejected.append(f"{relpath} absent")
        if ".tes/bin/discipline_oracle.py" in code or "scripts/discipline_oracle.py" in code:
            matched_path = True
            rejected.append("stale/non-delivered discipline_oracle.py path")
        if not matched_path:
            rejected.append("discipline_oracle token without canonical path")

    if "project_context_oracle" in code:
        matched_path = False
        for relpath in PROJECT_CONTEXT_ORACLES:
            if shell_invokes_python_file(code, relpath):
                if "project_context_oracle" not in matched:
                    matched.append("project_context_oracle")
                matched_path = True
                if (target / relpath).is_file():
                    resolved.append({"kind": "project-context", "command": f"python3 {relpath} --target ."})
                else:
                    rejected.append(f"{relpath} absent")
        if not matched_path:
            rejected.append("project_context_oracle token without runnable path")

    if hook_type == "pre-push" and field_reports.has_gate_pre_git_push(code):
        matched.append("gate-pre-git")
        if (target / ".gate-pre-git/bin/gate-pre-git").is_file():
            resolved.append({"kind": "gate-pre-git", "command": ".gate-pre-git/bin/gate-pre-git push --target <repo-root>"})
        else:
            rejected.append(".gate-pre-git/bin/gate-pre-git absent")

    return resolved, rejected, matched


def hook_gate_evidence(target: Path, hook_type: str) -> dict[str, Any]:
    if hook_type not in {"pre-commit", "pre-push"}:
        raise ValueError(f"unsupported hook_type: {hook_type}")

    git_dir = target / ".git"
    if not git_dir.exists():
        payload: dict[str, Any] = {
            "installed": False,
            "enforced": False,
            "resolved_gates": [],
            "reason": "no .git directory",
        }
        if hook_type == "pre-push":
            payload.update({"field_reports_prepush_drain": False, "project_prepush_gate": False})
        return payload

    resolver = field_reports.resolve_pre_push_hook if hook_type == "pre-push" else field_reports.resolve_pre_commit_hook
    hook_info = resolver(target, git_dir)
    if hook_info.get("status") != "PASS":
        payload = {
            "installed": False,
            "enforced": False,
            "resolved_gates": [],
            "reason": str(hook_info.get("reason") or "hook resolution blocked"),
        }
        if hook_type == "pre-push":
            payload.update({"field_reports_prepush_drain": False, "project_prepush_gate": False})
        return payload

    hook_path = Path(str(hook_info.get("hook")))
    active_entrypoint = resolve_husky_active_entrypoint(target, hook_info.get("hooksPath"), hook_type) or hook_path
    if not hook_path.is_file():
        payload = {
            "installed": False,
            "enforced": False,
            "resolved_gates": [],
            "reason": f"{hook_type} hook file absent",
            "hook": str(hook_path),
        }
        if hook_type == "pre-push":
            payload.update({"field_reports_prepush_drain": False, "project_prepush_gate": False})
        return payload

    text = hook_path.read_text(encoding="utf-8", errors="ignore")
    drain_present = field_reports.HOOK_MARKER in text if hook_type == "pre-push" else None

    if not active_entrypoint.is_file():
        payload = {
            "installed": False,
            "enforced": False,
            "resolved_gates": [],
            "reason": f"active {hook_type} entrypoint absent",
            "hook": str(hook_path),
            "active_entrypoint": str(active_entrypoint),
        }
        if hook_type == "pre-push":
            payload.update({"field_reports_prepush_drain": drain_present, "project_prepush_gate": False})
        return payload

    if not os.access(active_entrypoint, os.X_OK):
        payload = {
            "installed": False,
            "enforced": False,
            "resolved_gates": [],
            "reason": f"active {hook_type} entrypoint present but not executable",
            "hook": str(hook_path),
            "active_entrypoint": str(active_entrypoint),
            "executable": False,
        }
        if hook_type == "pre-push":
            payload.update({"field_reports_prepush_drain": drain_present, "project_prepush_gate": False})
        return payload

    code = strip_shell_comments(text)
    resolved, rejected, matched = resolved_gate_commands(target, code, hook_type=hook_type)
    enforced = bool(resolved)
    reasons: list[str] = []
    if hook_type == "pre-push" and not drain_present:
        reasons.append("Field Reports drain absent")
    if not enforced:
        reasons.append(f"{hook_type} has no resolved quality gate")

    payload = {
        "installed": True,
        "enforced": enforced,
        "hook": str(hook_path),
        "active_entrypoint": str(active_entrypoint),
        "mode": hook_info.get("mode"),
        "executable": True,
        "gate_tokens": matched,
        "resolved_gates": resolved,
        "unresolved_gates": rejected,
        "reason": None if not reasons else "; ".join(reasons),
    }
    if hook_type == "pre-push":
        payload.update(
            {
                "field_reports_prepush_drain": drain_present,
                "project_prepush_gate": bool(matched),
            }
        )
    return payload


def canary_prepush_evidence(target: Path) -> dict[str, Any]:
    evidence = hook_gate_evidence(target, "pre-push")
    return {
        "prepush_installed": bool(evidence.get("installed")),
        "field_reports_prepush_drain": bool(evidence.get("field_reports_prepush_drain")),
        "prepush_enforced": bool(evidence.get("enforced")),
        "project_prepush_gate": bool(evidence.get("project_prepush_gate")),
        "hook": evidence.get("hook", ""),
        "active_entrypoint": evidence.get("active_entrypoint", ""),
        "executable": evidence.get("executable", False),
        "mode": evidence.get("mode"),
        "gate_tokens": evidence.get("gate_tokens", []),
        "resolved_gates": evidence.get("resolved_gates", []),
        "unresolved_gates": evidence.get("unresolved_gates", []),
        "reason": evidence.get("reason"),
    }


def canary_precommit_evidence(target: Path) -> dict[str, Any]:
    evidence = hook_gate_evidence(target, "pre-commit")
    payload = {
        "precommit_enforced": bool(evidence.get("enforced")),
        "reason": evidence.get("reason"),
        "hook": evidence.get("hook", ""),
        "active_entrypoint": evidence.get("active_entrypoint", ""),
        "executable": evidence.get("executable", False),
        "gate_tokens": evidence.get("gate_tokens", []),
        "resolved_gates": evidence.get("resolved_gates", []),
        "unresolved_gates": evidence.get("unresolved_gates", []),
    }
    return payload


def installed_hook_evidence(target: Path, hook_type: str) -> dict[str, Any]:
    return hook_gate_evidence(target, hook_type)


def _git_gate_failures(pre_commit: dict[str, Any], pre_push: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if not pre_commit.get("enforced"):
        failures.append(f"strict pre-commit gate absent: {pre_commit.get('reason')}")
    if not pre_push.get("installed"):
        failures.append(f"pre-push hook absent or inactive: {pre_push.get('reason')}")
    if not pre_push.get("field_reports_prepush_drain"):
        failures.append(f"Field Reports pre-push drain absent: {pre_push.get('reason')}")
    if not pre_push.get("enforced"):
        failures.append(f"strict pre-push quality gate absent: {pre_push.get('reason')}")
    return failures


def canary_git_admission(target: Path) -> dict[str, Any]:
    if not is_git_work_tree(target):
        return {
            "status": "BLOCKED",
            "readiness": "NEEDS_GIT",
            "headline": "NEEDS_GIT: target is not a Git work tree; canary admission requires Git",
            "git_work_tree": False,
            "git_clean": False,
            "prepush_installed": False,
            "field_reports_prepush_drain": False,
            "prepush_enforced": False,
            "project_prepush_gate": False,
            "precommit_enforced": False,
            "prepush_resolved_gates": [],
            "blockers": ["target is not a Git work tree; canary admission requires Git"],
        }

    clean = git_is_clean(target)
    pre_push = hook_gate_evidence(target, "pre-push")
    pre_commit = hook_gate_evidence(target, "pre-commit")
    blockers = _git_gate_failures(pre_commit, pre_push)
    if clean is False:
        blockers.append("Git work tree is dirty")
    return {
        "status": "BLOCKED" if blockers else "PASS",
        "git_work_tree": True,
        "git_clean": bool(clean),
        "prepush_installed": bool(pre_push.get("installed")),
        "field_reports_prepush_drain": bool(pre_push.get("field_reports_prepush_drain")),
        "prepush_enforced": bool(pre_push.get("enforced")),
        "project_prepush_gate": bool(pre_push.get("project_prepush_gate")),
        "prepush_resolved_gates": pre_push.get("resolved_gates", []),
        "precommit_enforced": bool(pre_commit.get("enforced")),
        "prepush": canary_prepush_evidence(target),
        "precommit": canary_precommit_evidence(target),
        "blockers": blockers,
    }


def installed_git_admission_status(target: Path, *, hooks_attached: bool) -> dict[str, Any]:
    if not hooks_attached:
        return {"status": "NOT_APPLIED", "reason": "hooks not attached"}
    if not is_git_work_tree(target):
        return {
            "status": "NEEDS_REVIEW",
            "git_work_tree": False,
            "failures": ["target is not a Git work tree; Git gates cannot be certified"],
        }

    pre_push = hook_gate_evidence(target, "pre-push")
    pre_commit = hook_gate_evidence(target, "pre-commit")
    failures = _git_gate_failures(pre_commit, pre_push)
    return {
        "status": "PASS" if not failures else "NEEDS_REVIEW",
        "git_work_tree": True,
        "precommit_enforced": bool(pre_commit.get("enforced")),
        "prepush_installed": bool(pre_push.get("installed")),
        "field_reports_prepush_drain": bool(pre_push.get("field_reports_prepush_drain")),
        "prepush_enforced": bool(pre_push.get("enforced")),
        "project_prepush_gate": bool(pre_push.get("project_prepush_gate")),
        "prepush_resolved_gates": pre_push.get("resolved_gates", []),
        "precommit": pre_commit,
        "prepush": pre_push,
        "failures": failures,
    }


def _init_git(target: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=target, text=True, capture_output=True, check=False)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=target, text=True, capture_output=True, check=False)
    subprocess.run(["git", "config", "user.name", "t"], cwd=target, text=True, capture_output=True, check=False)


def _write_discipline_oracle(target: Path) -> None:
    oracle = target / CANONICAL_DISCIPLINE_ORACLES[0]
    oracle.parent.mkdir(parents=True, exist_ok=True)
    oracle.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n", encoding="utf-8")
    oracle.chmod(0o755)


def _write_precommit(target: Path, *, comment_only: bool = False, executable: bool = True) -> None:
    hook = target / ".git/hooks/pre-commit"
    hook.parent.mkdir(parents=True, exist_ok=True)
    if comment_only:
        hook.write_text("#!/bin/sh\n# someday run commit:check here\nexit 0\n", encoding="utf-8")
    else:
        _write_discipline_oracle(target)
        hook.write_text(
            "#!/bin/sh\npython3 .agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test\n",
            encoding="utf-8",
        )
    hook.chmod(0o755 if executable else 0o644)


def _write_prepush(target: Path, *, drain: bool, quality: bool) -> None:
    hook = target / ".git/hooks/pre-push"
    hook.parent.mkdir(parents=True, exist_ok=True)
    body = "#!/bin/sh\n"
    if drain:
        body += f"# {field_reports.HOOK_MARKER}\n"
    if quality:
        _write_discipline_oracle(target)
        body += 'python3 ".agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py" --self-test\n'
    if drain:
        body += 'python3 ".tes/bin/field_reports.py" drain --target . --trigger pre-push >/dev/null 2>&1 || true\n'
    body += "exit 0\n"
    hook.write_text(body, encoding="utf-8")
    hook.chmod(0o755)


def write_git_gate_fixture(
    target: Path,
    *,
    init_git: bool = True,
    precommit: str = "strict",
    prepush: str = "full",
    package_scripts: dict[str, str] | None = None,
) -> None:
    """Materialize a standardized Git-gate fixture.

    Scenarios are intentionally named by contract state, not by a consumer's
    expected verdict. This keeps canary admission and installed certification
    fixtures equivalent when they need the same state.
    """
    target.mkdir(parents=True, exist_ok=True)
    if init_git:
        _init_git(target)
    if package_scripts is not None:
        (target / "package.json").write_text(json.dumps({"scripts": package_scripts}, sort_keys=True) + "\n", encoding="utf-8")

    if precommit == "strict":
        _write_precommit(target)
    elif precommit == "comment-only":
        _write_precommit(target, comment_only=True)
    elif precommit == "non-executable":
        _write_precommit(target, executable=False)
    elif precommit == "echo-token":
        hook = target / ".git/hooks/pre-commit"
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text("#!/bin/sh\necho commit:check\nexit 0\n", encoding="utf-8")
        hook.chmod(0o755)
    elif precommit != "none":
        raise ValueError(f"unsupported precommit fixture: {precommit}")

    if prepush == "full":
        _write_prepush(target, drain=True, quality=True)
    elif prepush == "drain-only":
        _write_prepush(target, drain=True, quality=False)
    elif prepush == "quality-only":
        _write_prepush(target, drain=False, quality=True)
    elif prepush == "unresolved-gate-only":
        hook = target / ".git/hooks/pre-push"
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text(field_reports.gate_pre_git_push_shell(), encoding="utf-8")
        hook.chmod(0o755)
    elif prepush == "echo-token":
        hook = target / ".git/hooks/pre-push"
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text(f"#!/bin/sh\n# {field_reports.HOOK_MARKER}\necho prepush:check\necho commit:check\nexit 0\n", encoding="utf-8")
        hook.chmod(0o755)
    elif prepush != "none":
        raise ValueError(f"unsupported prepush fixture: {prepush}")


CONTRACT_MATRIX: tuple[dict[str, Any], ...] = (
    {
        "name": "no-git",
        "git": False,
        "precommit": "none",
        "prepush": "none",
        "hooks_attached": True,
        "expected": {
            "canary_status": "BLOCKED",
            "installed_status": "NEEDS_REVIEW",
            "precommit_enforced": False,
            "prepush_installed": False,
            "field_reports_prepush_drain": False,
            "prepush_enforced": False,
        },
    },
    {
        "name": "git-only",
        "git": True,
        "precommit": "none",
        "prepush": "none",
        "hooks_attached": True,
        "expected": {
            "canary_status": "BLOCKED",
            "installed_status": "NEEDS_REVIEW",
            "precommit_enforced": False,
            "prepush_installed": False,
            "field_reports_prepush_drain": False,
            "prepush_enforced": False,
        },
    },
    {
        "name": "precommit-only",
        "git": True,
        "precommit": "strict",
        "prepush": "none",
        "commit_clean": True,
        "hooks_attached": True,
        "expected": {
            "canary_status": "BLOCKED",
            "installed_status": "NEEDS_REVIEW",
            "precommit_enforced": True,
            "prepush_installed": False,
            "field_reports_prepush_drain": False,
            "prepush_enforced": False,
        },
    },
    {
        "name": "prepush-full-no-precommit",
        "git": True,
        "precommit": "none",
        "prepush": "full",
        "commit_clean": True,
        "hooks_attached": True,
        "expected": {
            "canary_status": "BLOCKED",
            "installed_status": "NEEDS_REVIEW",
            "precommit_enforced": False,
            "prepush_installed": True,
            "field_reports_prepush_drain": True,
            "prepush_enforced": True,
        },
    },
    {
        "name": "drain-only",
        "git": True,
        "precommit": "strict",
        "prepush": "drain-only",
        "commit_clean": True,
        "hooks_attached": True,
        "expected": {
            "canary_status": "BLOCKED",
            "installed_status": "NEEDS_REVIEW",
            "precommit_enforced": True,
            "prepush_installed": True,
            "field_reports_prepush_drain": True,
            "prepush_enforced": False,
        },
    },
    {
        "name": "quality-only",
        "git": True,
        "precommit": "strict",
        "prepush": "quality-only",
        "commit_clean": True,
        "hooks_attached": True,
        "expected": {
            "canary_status": "BLOCKED",
            "installed_status": "NEEDS_REVIEW",
            "precommit_enforced": True,
            "prepush_installed": True,
            "field_reports_prepush_drain": False,
            "prepush_enforced": True,
        },
    },
    {
        "name": "unresolved-gate-only",
        "git": True,
        "precommit": "strict",
        "prepush": "unresolved-gate-only",
        "commit_clean": True,
        "hooks_attached": True,
        "expected": {
            "canary_status": "BLOCKED",
            "installed_status": "NEEDS_REVIEW",
            "precommit_enforced": True,
            "prepush_installed": True,
            "field_reports_prepush_drain": False,
            "prepush_enforced": False,
        },
    },
    {
        "name": "echo-token",
        "git": True,
        "precommit": "echo-token",
        "prepush": "echo-token",
        "package_scripts": {"commit:check": "true", "prepush:check": "true"},
        "commit_clean": True,
        "hooks_attached": True,
        "expected": {
            "canary_status": "BLOCKED",
            "installed_status": "NEEDS_REVIEW",
            "precommit_enforced": False,
            "prepush_installed": True,
            "field_reports_prepush_drain": True,
            "prepush_enforced": False,
        },
    },
    {
        "name": "full",
        "git": True,
        "precommit": "strict",
        "prepush": "full",
        "commit_clean": True,
        "hooks_attached": True,
        "expected": {
            "canary_status": "PASS",
            "installed_status": "PASS",
            "precommit_enforced": True,
            "prepush_installed": True,
            "field_reports_prepush_drain": True,
            "prepush_enforced": True,
        },
    },
    {
        "name": "full-dirty",
        "git": True,
        "precommit": "strict",
        "prepush": "full",
        "commit_clean": True,
        "dirty_after_commit": True,
        "hooks_attached": True,
        "expected": {
            "canary_status": "BLOCKED",
            "installed_status": "PASS",
            "precommit_enforced": True,
            "prepush_installed": True,
            "field_reports_prepush_drain": True,
            "prepush_enforced": True,
        },
    },
    {
        "name": "hooks-not-attached",
        "git": True,
        "precommit": "none",
        "prepush": "none",
        "hooks_attached": False,
        "expected": {
            "canary_status": "BLOCKED",
            "installed_status": "NOT_APPLIED",
            "precommit_enforced": False,
            "prepush_installed": False,
            "field_reports_prepush_drain": False,
            "prepush_enforced": False,
        },
    },
)


def _commit_fixture(target: Path) -> None:
    subprocess.run(["git", "add", "."], cwd=target, text=True, capture_output=True, check=False)
    subprocess.run(["git", "commit", "--no-verify", "-m", "fixture"], cwd=target, text=True, capture_output=True, check=False)


def evaluate_contract_matrix() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-git-gate-matrix-") as d:
        root = Path(d)
        for case in CONTRACT_MATRIX:
            target = root / str(case["name"])
            if case.get("git"):
                write_git_gate_fixture(
                    target,
                    precommit=str(case.get("precommit", "none")),
                    prepush=str(case.get("prepush", "none")),
                    package_scripts=case.get("package_scripts"),
                )
                if case.get("commit_clean"):
                    _commit_fixture(target)
                if case.get("dirty_after_commit"):
                    (target / "dirty.txt").write_text("dirty\n", encoding="utf-8")
            else:
                target.mkdir(parents=True, exist_ok=True)

            canary = canary_git_admission(target)
            installed = installed_git_admission_status(target, hooks_attached=bool(case.get("hooks_attached", True)))
            actual = {
                "canary_status": canary.get("status"),
                "installed_status": installed.get("status"),
                "precommit_enforced": bool(canary.get("precommit_enforced")),
                "prepush_installed": bool(canary.get("prepush_installed")),
                "field_reports_prepush_drain": bool(canary.get("field_reports_prepush_drain")),
                "prepush_enforced": bool(canary.get("prepush_enforced")),
            }
            expected = case["expected"]
            mismatches = {
                key: {"expected": expected.get(key), "actual": actual.get(key)}
                for key in expected
                if actual.get(key) != expected.get(key)
            }
            if mismatches:
                failures.append(f"{case['name']}: {mismatches}")
            rows.append(
                {
                    "case": case["name"],
                    "expected": expected,
                    "actual": actual,
                    "status": "PASS" if not mismatches else "FAIL",
                    "mismatches": mismatches,
                }
            )
    passed = sum(1 for row in rows if row["status"] == "PASS")
    return {
        "status": "PASS" if not failures else "FAIL",
        "total": len(rows),
        "passed": passed,
        "failed": len(rows) - passed,
        "rows": rows,
        "failures": failures,
    }


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    cases: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="tes-git-gate-contract-") as d:
        root = Path(d)

        no_git = root / "no-git"
        no_git.mkdir()
        no_git_result = canary_git_admission(no_git)
        cases.append({"case": "no-git", "status": no_git_result["status"]})
        if no_git_result["status"] != "BLOCKED" or no_git_result.get("git_work_tree") is not False:
            failures.append("no-Git target must BLOCK and report git_work_tree=false")

        git_only = root / "git-only"
        git_only.mkdir()
        _init_git(git_only)
        git_only_result = canary_git_admission(git_only)
        cases.append({"case": "git-only", "status": git_only_result["status"], "blockers": len(git_only_result["blockers"])})
        if git_only_result["status"] != "BLOCKED":
            failures.append("Git target without hooks must BLOCK")

        drain_only = root / "drain-only"
        drain_only.mkdir()
        _init_git(drain_only)
        _write_precommit(drain_only)
        _write_prepush(drain_only, drain=True, quality=False)
        drain_evidence = canary_prepush_evidence(drain_only)
        cases.append(
            {
                "case": "drain-only",
                "installed": drain_evidence.get("prepush_installed"),
                "drain": drain_evidence.get("field_reports_prepush_drain"),
                "enforced": drain_evidence.get("prepush_enforced"),
            }
        )
        if not drain_evidence.get("field_reports_prepush_drain") or drain_evidence.get("prepush_enforced"):
            failures.append("drain-only pre-push must prove drain but not enforcement")
        if canary_git_admission(drain_only)["status"] != "BLOCKED":
            failures.append("drain-only pre-push must BLOCK Git admission")

        gate_only = root / "gate-only"
        gate_only.mkdir()
        _init_git(gate_only)
        _write_precommit(gate_only)
        _write_prepush(gate_only, drain=False, quality=True)
        gate_evidence = canary_prepush_evidence(gate_only)
        cases.append(
            {
                "case": "gate-only",
                "drain": gate_evidence.get("field_reports_prepush_drain"),
                "enforced": gate_evidence.get("prepush_enforced"),
            }
        )
        if gate_evidence.get("field_reports_prepush_drain") or not gate_evidence.get("prepush_enforced"):
            failures.append("gate-only pre-push must prove enforcement but not Field Reports drain")
        if canary_git_admission(gate_only)["status"] != "BLOCKED":
            failures.append("gate-only pre-push must BLOCK because Field Reports drain is absent")

        full = root / "full"
        full.mkdir()
        _init_git(full)
        _write_precommit(full)
        _write_prepush(full, drain=True, quality=True)
        subprocess.run(["git", "add", "."], cwd=full, text=True, capture_output=True, check=False)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=full, text=True, capture_output=True, check=False)
        full_result = canary_git_admission(full)
        cases.append({"case": "full", "status": full_result["status"]})
        if full_result["status"] != "PASS":
            failures.append(f"full Git gate contract must PASS, got {full_result['status']}: {full_result['blockers']}")

        comment_only = root / "comment-only"
        comment_only.mkdir()
        _init_git(comment_only)
        _write_precommit(comment_only, comment_only=True)
        if canary_precommit_evidence(comment_only).get("precommit_enforced"):
            failures.append("comment-only pre-commit must not be enforced")

        non_exec = root / "non-exec"
        non_exec.mkdir()
        _init_git(non_exec)
        _write_precommit(non_exec, executable=False)
        if canary_precommit_evidence(non_exec).get("precommit_enforced"):
            failures.append("non-executable pre-commit must not be enforced")

        echo_token = root / "echo-token"
        echo_token.mkdir()
        _init_git(echo_token)
        (echo_token / "package.json").write_text(
            json.dumps({"scripts": {"commit:check": "true", "prepush:check": "true"}}, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        echo_pc = echo_token / ".git/hooks/pre-commit"
        echo_pc.parent.mkdir(parents=True, exist_ok=True)
        echo_pc.write_text("#!/bin/sh\necho commit:check\nexit 0\n", encoding="utf-8")
        echo_pc.chmod(0o755)
        echo_pp = echo_token / ".git/hooks/pre-push"
        echo_pp.write_text(f"#!/bin/sh\n# {field_reports.HOOK_MARKER}\necho prepush:check\necho commit:check\nexit 0\n", encoding="utf-8")
        echo_pp.chmod(0o755)
        echo_result = canary_git_admission(echo_token)
        cases.append(
            {
                "case": "echo-token",
                "precommit_enforced": echo_result.get("precommit_enforced"),
                "prepush_enforced": echo_result.get("prepush_enforced"),
            }
        )
        if echo_result.get("precommit_enforced") or echo_result.get("prepush_enforced"):
            failures.append("echoed npm script names must not count as enforced Git gates")

    matrix = evaluate_contract_matrix()
    if matrix["status"] != "PASS":
        failures.extend(str(item) for item in matrix.get("failures", []))

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "cases": cases,
        "matrix": {
            "status": matrix["status"],
            "total": matrix["total"],
            "passed": matrix["passed"],
            "failed": matrix["failed"],
            "rows": matrix["rows"],
        },
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Canonical TES Git gate contract.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args(argv)
    result = self_test() if args.self_test else {"schema": SCHEMA, "status": "PASS"}
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json_only:
        print("[git-gate-contract] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
