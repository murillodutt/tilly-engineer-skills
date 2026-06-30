#!/usr/bin/env python3
"""Canary admission gate: block false readiness when Git/pre-push/pre-commit or
per-host native hook evidence is absent or unproven.

This is MAINTAINER/canary-admission infrastructure that VERIFIES the delivered
Git-gate behavior. Ceiling decision (tug-of-war matrix F1/F2/F3): when a project
is Git-eligible, TES installs, chooses and verifies its Git gates — it installs
the Field Reports pre-push gate AND a strict pre-commit gate (selecting the hook
manager deterministically: husky for Node/TS, pre-commit when a config exists,
lefthook as the polyglot default, deferring to any existing owner). This oracle
is the gate a canary REPLAY session runs against a candidate target before it
may claim READY_FOR_GOAL_MAESTRO_CANARY; its evidence functions
(prepush_evidence / precommit_evidence) define the contract the delivered
installer (field_reports.install_hook) must satisfy. It exists because no prior
surface materially proved Git admission or refused cross-host native hook
claims: installed_certification_oracle had zero Git checks, and hook runtime
evidence is host-local (no host keeps a native ledger; only the hook's own
runtime record proves firing — Claude/Codex/Cursor confirmed).

NOTE — overturned contract: an earlier contract stated "TES does NOT auto-install
a strict pre-commit gate for adopters" (INSTALL.md:276 advisory-only). The
tug-of-war ceiling consciously overturns that: absence of an installable Git
gate on an eligible target is no longer acceptable as advisory; TES installs and
verifies the gate, and admission BLOCKS when material proof is absent.

Hard contract (never relaxed):
  - Git admission BLOCKS when the target is not a Git work tree.
  - On a Git-backed target, BLOCKS when the Field Reports pre-push gate is
    absent, and when strict pre-commit proof is absent.
  - precommit_enforced / prepush_installed / git_clean are emitted ONLY with
    material Git evidence; absent evidence yields false, never silence.
  - Each host's native hook claim is proven only by that host's own runtime
    records. A configured-but-unobserved host is CONFIGURED_NOT_OBSERVED, never
    native PASS. Records from one host MUST NOT fill another host's claim.

Consumer: maintainer/canary gate (self-test + replay admission). Verifies
delivered behavior; the oracle itself is not a HELPER_FILE.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import field_reports
import tes_install


VERSION = "0.3.235"
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
    """Two distinct pre-push claims, each proven by its OWN marker (ceiling F21).

    The pre-push surface carries two structurally different things that earlier
    code conflated:
      - field_reports_prepush_drain: the Field Reports drain the installer writes,
        identified ONLY by HOOK_MARKER. It is an ADVISORY, non-blocking drain
        (exit 0 by design); its presence proves Field Reports is active.
      - project_prepush_gate: a blocking project gate, identified ONLY by the
        gate-pre-git invocation. Its presence proves a hard pre-push gate exists.

    Neither marker may prove the other claim. `prepush_installed` is kept as a
    back-compatible alias meaning "the Field Reports drain is installed" (the
    claim canary admission actually gates on), preserving session-1 behavior.
    """
    git_dir = target / ".git"
    if not git_dir.exists():
        return {
            "prepush_installed": False,
            "field_reports_prepush_drain": False,
            "project_prepush_gate": False,
            "reason": "no .git directory",
        }
    hook_info = field_reports.resolve_pre_push_hook(target, git_dir)
    if hook_info.get("status") != "PASS":
        return {
            "prepush_installed": False,
            "field_reports_prepush_drain": False,
            "project_prepush_gate": False,
            "reason": str(hook_info.get("reason") or "hook resolution blocked"),
        }
    hook = hook_info.get("hook")
    hook_path = Path(str(hook)) if hook else None
    if not hook_path or not hook_path.is_file():
        return {
            "prepush_installed": False,
            "field_reports_prepush_drain": False,
            "project_prepush_gate": False,
            "reason": "pre-push hook file absent",
            "hook": str(hook_path or ""),
        }
    text = hook_path.read_text(encoding="utf-8", errors="ignore")
    drain_present = field_reports.HOOK_MARKER in text  # advisory drain claim
    project_gate_present = field_reports.has_gate_pre_git_push(text)  # blocking gate claim
    if not (drain_present or project_gate_present):
        return {
            "prepush_installed": False,
            "field_reports_prepush_drain": False,
            "project_prepush_gate": False,
            "reason": "pre-push hook present but missing the Field Reports drain marker",
            "hook": str(hook_path),
        }
    return {
        # Back-compat alias: admission gates on the Field Reports drain claim.
        "prepush_installed": drain_present,
        "field_reports_prepush_drain": drain_present,
        "project_prepush_gate": project_gate_present,
        "hook": str(hook_path),
        "mode": hook_info.get("mode"),
        "reason": None if drain_present else "project pre-push gate present but Field Reports drain absent",
    }


STRICT_GATE_TOKENS = ("--strict", "commit:check", "commit:closure", "discipline_oracle", "project_context_oracle")


def _strip_shell_comments(text: str) -> str:
    """Drop full-line and trailing `#` comments so a token in a comment never
    counts as a real gate invocation (ceiling F22: prove the command, not a note).

    Conservative: removes from an unquoted `#` to end of line. A `#` inside a
    quote is rare in hook bodies and erring toward stripping only makes the proof
    stricter, never falsely positive.
    """
    out: list[str] = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue  # full comment / shebang line
        # Trailing comment: cut at the first ' #' not inside an obvious quote.
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


def precommit_evidence(target: Path) -> dict[str, Any]:
    """Proof of a strict pre-commit gate by EXECUTABILITY, not comment substring.

    Ceiling F22: a comment containing `commit:check` must never set
    precommit_enforced=true. The proof is two-part: (1) the resolved hook is
    runnable (executable bit, mirroring tes_init's hook-runnability check), and
    (2) a strict gate token appears in the hook's CODE (comments stripped), i.e.
    it actually invokes a TES gate rather than merely mentioning one.
    """
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
    # (1) Runnability: a strict gate must be executable to actually fire.
    runnable = os.access(hook_path, os.X_OK)
    if not runnable:
        return {
            "precommit_enforced": False,
            "reason": "pre-commit hook present but not executable (cannot fire as a gate)",
            "hook": str(hook_path),
            "executable": False,
        }
    # (2) Real invocation: a strict gate token in CODE, not in a comment.
    code = _strip_shell_comments(hook_path.read_text(encoding="utf-8", errors="ignore"))
    matched = [token for token in STRICT_GATE_TOKENS if token in code]
    if not matched:
        return {
            "precommit_enforced": False,
            "reason": "pre-commit present and executable but invokes no strict TES gate (token only in comments, or absent)",
            "hook": str(hook_path),
            "executable": True,
        }
    return {"precommit_enforced": True, "hook": str(hook_path), "executable": True, "gate_tokens": matched}


def git_admission(target: Path) -> dict[str, Any]:
    """Block readiness unless Git, the Field Reports drain, and a strict
    pre-commit are proven.

    Ceiling F25: the Field Reports pre-push is an ADVISORY non-blocking drain
    (exit-0 by design — it must never block an adopter's push). Admission gates on
    the drain being INSTALLED (proves Field Reports is active), not on it being a
    blocking gate. The blocking `project_prepush_gate` claim is reported
    separately and observationally — its absence is not an admission blocker.
    """
    blockers: list[str] = []
    if not is_git_work_tree(target):
        # No Git: every Git claim is false, and admission is BLOCKED, not skipped.
        return {
            "status": "BLOCKED",
            "readiness": "NEEDS_GIT",
            "headline": "NEEDS_GIT: target is not a Git work tree; canary admission requires Git",
            "git_work_tree": False,
            "git_clean": False,
            "prepush_installed": False,
            "field_reports_prepush_drain": False,
            "project_prepush_gate": False,
            "precommit_enforced": False,
            "blockers": ["target is not a Git work tree; canary admission requires Git"],
        }
    clean = git_is_clean(target)
    pre_push = prepush_evidence(target)
    pre_commit = precommit_evidence(target)
    # Admission gate: the Field Reports drain must be installed (advisory claim).
    if not pre_push.get("field_reports_prepush_drain"):
        blockers.append(f"Field Reports pre-push drain absent: {pre_push.get('reason')}")
    if not pre_commit.get("precommit_enforced"):
        blockers.append(f"strict pre-commit gate absent: {pre_commit.get('reason')}")
    if clean is False:
        blockers.append("Git work tree is dirty")
    return {
        "status": "BLOCKED" if blockers else "PASS",
        "git_work_tree": True,
        "git_clean": bool(clean),
        # Back-compat alias kept; the drain is the gated claim.
        "prepush_installed": bool(pre_push.get("field_reports_prepush_drain")),
        "field_reports_prepush_drain": bool(pre_push.get("field_reports_prepush_drain")),
        # Observational: a blocking project pre-push gate exists or not. Not an
        # admission blocker (the drain is advisory; the project gate is optional).
        "project_prepush_gate": bool(pre_push.get("project_prepush_gate")),
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
    readiness = str(git.get("readiness") or status)
    headline = str(
        git.get("headline")
        or ("PASS: canary admission ready" if status == "PASS" else f"{status}: canary admission not ready")
    )
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "target": str(target),
        "status": status,
        "readiness": readiness,
        "headline": headline,
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
    """Write a fully-equipped pre-push carrying BOTH claims: the Field Reports
    drain (HOOK_MARKER, the advisory claim admission gates on) AND a blocking
    project gate (gate-pre-git). After the F21 split, a fully-gated target must
    carry the drain marker — a project gate alone no longer satisfies admission.
    """
    hooks = target / ".git/hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "pre-push"
    hook.write_text(
        f"#!/bin/sh\n# {field_reports.HOOK_MARKER}\n"
        + field_reports.gate_pre_git_push_shell(),
        encoding="utf-8",
    )
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
        if result.get("readiness") != "NEEDS_GIT" or "NEEDS_GIT" not in str(result.get("headline")):
            failures.append("no-Git target must propagate NEEDS_GIT in readiness/headline")
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

        # 3a) Ceiling F21 — drain vs project gate are SEPARATE claims, each proven
        #     by its own marker only. A drain-only pre-push (HOOK_MARKER, no
        #     gate-pre-git) proves the drain but NOT the project gate; a
        #     gate-only pre-push proves the inverse. Neither marker proves the
        #     other claim.
        drain_only = root / "drain-only"
        drain_only.mkdir()
        _init_git(drain_only)
        po = drain_only / ".git/hooks/pre-push"
        po.parent.mkdir(parents=True, exist_ok=True)
        po.write_text(f"#!/bin/sh\n# {field_reports.HOOK_MARKER}\nexit 0\n", encoding="utf-8")
        po.chmod(0o755)
        drain_ev = prepush_evidence(drain_only.resolve())
        if not drain_ev.get("field_reports_prepush_drain") or drain_ev.get("project_prepush_gate"):
            failures.append(
                "F21: drain-only pre-push must prove the drain claim and NOT the project gate claim, "
                f"got drain={drain_ev.get('field_reports_prepush_drain')} gate={drain_ev.get('project_prepush_gate')}"
            )
        gate_only = root / "gate-only"
        gate_only.mkdir()
        _init_git(gate_only)
        go = gate_only / ".git/hooks/pre-push"
        go.parent.mkdir(parents=True, exist_ok=True)
        go.write_text(field_reports.gate_pre_git_push_shell(), encoding="utf-8")  # gate-pre-git, no HOOK_MARKER
        go.chmod(0o755)
        gate_ev = prepush_evidence(gate_only.resolve())
        if gate_ev.get("field_reports_prepush_drain") or not gate_ev.get("project_prepush_gate"):
            failures.append(
                "F21: gate-only pre-push must prove the project gate claim and NOT the drain claim, "
                f"got drain={gate_ev.get('field_reports_prepush_drain')} gate={gate_ev.get('project_prepush_gate')}"
            )
        # And admission gates on the DRAIN: a gate-only target is BLOCKED (no drain).
        if git_admission(gate_only.resolve())["status"] != "BLOCKED":
            failures.append("F21/F25: a project-gate-only target (no Field Reports drain) must BLOCK admission")

        # 3b) Ceiling F22 — strict pre-commit proven by EXECUTABILITY + real
        #     invocation, never a comment substring. A comment-only stub and a
        #     non-executable real-token hook must both be rejected.
        comment_stub = root / "comment-stub"
        comment_stub.mkdir()
        _init_git(comment_stub)
        cs = comment_stub / ".git/hooks/pre-commit"
        cs.parent.mkdir(parents=True, exist_ok=True)
        cs.write_text("#!/bin/sh\n# someday run commit:check here\nexit 0\n", encoding="utf-8")
        cs.chmod(0o755)
        if precommit_evidence(comment_stub.resolve()).get("precommit_enforced"):
            failures.append("F22: a pre-commit with the gate token only in a comment must NOT be precommit_enforced")
        non_exec = root / "non-exec"
        non_exec.mkdir()
        _init_git(non_exec)
        ne = non_exec / ".git/hooks/pre-commit"
        ne.parent.mkdir(parents=True, exist_ok=True)
        ne.write_text("#!/bin/sh\nnpm run commit:check\n", encoding="utf-8")
        ne.chmod(0o644)  # real invocation but not executable
        if precommit_evidence(non_exec.resolve()).get("precommit_enforced"):
            failures.append("F22: a non-executable pre-commit must NOT be precommit_enforced (cannot fire)")

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
