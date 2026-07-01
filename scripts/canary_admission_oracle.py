#!/usr/bin/env python3
"""Canary admission gate: block false readiness when Git/pre-push/pre-commit or
per-host native hook evidence is absent or unproven.

This is MAINTAINER/canary-admission infrastructure that VERIFIES the delivered
Git-gate behavior. Ceiling decision (tug-of-war matrix F1/F2/F3): when a project
is Git-eligible, TES installs, chooses and verifies its Git gates — it installs
a strict pre-push quality gate, keeps the Field Reports pre-push drain additive,
and installs a strict pre-commit gate (selecting the hook manager
deterministically: husky for Node/TS, pre-commit when a config exists, lefthook
as the polyglot default, deferring to any existing owner). This oracle is the
gate a canary REPLAY session runs against a candidate target before it may claim
READY_FOR_GOAL_MAESTRO_CANARY; its evidence functions (prepush_evidence /
precommit_evidence) define the contract the delivered installer
(field_reports.install_hook) must satisfy. It exists because no prior surface
materially proved Git admission or refused cross-host native hook claims:
installed_certification_oracle had zero Git checks, and hook runtime evidence is
host-local (no host keeps a native ledger; only the hook's own runtime record
proves firing — Claude/Codex/Cursor confirmed).

NOTE — overturned contract: an earlier contract stated "TES does NOT auto-install
a strict pre-commit gate for adopters" (INSTALL.md:276 advisory-only). The
tug-of-war ceiling consciously overturns that: absence of an installable Git
gate on an eligible target is no longer acceptable as advisory; TES installs and
verifies the gate, and admission BLOCKS when material proof is absent.

Hard contract (never relaxed):
  - Git admission BLOCKS when the target is not a Git work tree.
  - On a Git-backed target, BLOCKS when the Field Reports pre-push drain is
    absent, when strict pre-push proof is absent, and when strict pre-commit
    proof is absent.
  - precommit_enforced / prepush_installed / prepush_enforced / git_clean are
    emitted ONLY with material Git evidence; absent evidence yields false,
    never silence.
  - Each host's native hook claim is proven only by that host's own runtime
    records. A configured-but-unobserved host is CONFIGURED_NOT_OBSERVED, never
    native PASS. Records from one host MUST NOT fill another host's claim.

Consumer: maintainer/canary gate (self-test + replay admission). Verifies
delivered behavior; the oracle itself is not a HELPER_FILE.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import field_reports
import git_gate_contract
import tes_install


VERSION = "0.3.251"
SCHEMA = "tes-canary-admission@1"
AGENTS = tes_install.AGENTS  # ("codex", "claude", "cursor")

# A host whose hook runtime is proven by that host's own records is NATIVE_PASS.
# A host configured but with no runtime record of its own is CONFIGURED_NOT_OBSERVED.
NATIVE_PASS = "NATIVE_PASS"
CONFIGURED_NOT_OBSERVED = "CONFIGURED_NOT_OBSERVED"
NOT_CONFIGURED = "NOT_CONFIGURED"


def is_git_work_tree(target: Path) -> bool:
    return git_gate_contract.is_git_work_tree(target)


def git_is_clean(target: Path) -> bool | None:
    """True/False for clean/dirty; None when target is not a Git work tree."""
    return git_gate_contract.git_is_clean(target)


def prepush_evidence(target: Path) -> dict[str, Any]:
    return git_gate_contract.canary_prepush_evidence(target)


def precommit_evidence(target: Path) -> dict[str, Any]:
    return git_gate_contract.canary_precommit_evidence(target)


def git_admission(target: Path) -> dict[str, Any]:
    return git_gate_contract.canary_git_admission(target)


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
        ceiling_scope = payload.get("ceiling_evidence_scope") if isinstance(payload.get("ceiling_evidence_scope"), dict) else {}
        per_host = ceiling_scope.get("per_host") if isinstance(ceiling_scope.get("per_host"), dict) else {}
        host_ceiling = per_host.get(host) if isinstance(per_host.get(host), dict) else {}
        observed = any(event.get("state") == "OBSERVED" for event in host_events)
        configured = any(event.get("state") in {"OBSERVED", "CONFIGURED"} for event in host_events)
        native_ceiling_pass = host_ceiling.get("status") == "PASS_CEILING"
        if observed and native_ceiling_pass:
            klass = NATIVE_PASS
        elif configured or observed:
            klass = CONFIGURED_NOT_OBSERVED
        else:
            klass = NOT_CONFIGURED
        hosts[host] = {
            "class": klass,
            "observed": observed,
            "configured": configured,
            "floor_status": payload.get("floor_status"),
            "ceiling_status": payload.get("ceiling_status"),
            "native_evidence": host_ceiling.get("native_evidence"),
            "host_real_records": host_ceiling.get("host_real_records", 0),
            "legacy_unknown_records": host_ceiling.get("legacy_unknown_records", 0),
        }
        if klass == CONFIGURED_NOT_OBSERVED:
            blockers.append(f"{host}: configured or observed but no transcript-correlated native hook evidence (CONFIGURED_NOT_OBSERVED)")
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
            "prepush_enforced": bool(git.get("prepush_enforced")),
            "precommit_enforced": bool(git.get("precommit_enforced")),
            "native_hook_pass_hosts": hooks.get("native_pass_hosts", []),
        },
    }


def _init_git(target: Path) -> None:
    git_env = git_gate_contract.isolated_git_env()
    subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False, env=git_env)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=target, text=True, capture_output=True, check=False, env=git_env)
    subprocess.run(["git", "config", "user.name", "t"], cwd=target, text=True, capture_output=True, check=False, env=git_env)


def _write_prepush(target: Path) -> None:
    """Write a fully-equipped pre-push carrying BOTH claims: the Field Reports
    drain (HOOK_MARKER, the advisory claim) AND a blocking TES quality fallback.
    After the F38 split, a fully-gated target must carry both the drain marker
    and a resolvable quality command.
    """
    hooks = target / ".git/hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "pre-push"
    hook.write_text(
        f"#!/bin/sh\n# {field_reports.HOOK_MARKER}\n"
        + field_reports.strict_pre_push_shell()
        + "\nif [ -f \".tes/bin/field_reports.py\" ]; then\n"
        + "  python3 \".tes/bin/field_reports.py\" drain --target . --trigger pre-push >/dev/null 2>&1 || true\n"
        + "fi\nexit 0\n",
        encoding="utf-8",
    )
    hook.chmod(0o755)


def _write_strict_precommit(target: Path) -> None:
    oracle = target / ".agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py"
    oracle.parent.mkdir(parents=True, exist_ok=True)
    oracle.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n", encoding="utf-8")
    oracle.chmod(0o755)
    hooks = target / ".git/hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "pre-commit"
    hook.write_text(
        "#!/bin/sh\n# strict TES canary gate\n"
        "python3 .agents/skills/tes-engineering-discipline/scripts/discipline_oracle.py --self-test\n",
        encoding="utf-8",
    )
    hook.chmod(0o755)


def _write_host_runtime_record(
    target: Path,
    host: str,
    *,
    provenance: str | None = tes_install.HOOK_PROVENANCE_FIXTURE,
    transcript_evidence: bool = False,
) -> None:
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
        if provenance is not None:
            rec["provenance"] = provenance
        if mode == "pretooluse":
            rec["schema_version"] = "pretooluse_decision@2"
            rec.update(
                {
                    "invocation": f"obs-{host}-tool",
                    "reason_codes": ["needs_discoverability_unknown_mutation", "renderer_contract_projected"],
                    "classifier_trace": {"payload_source": "tool_input", "path_source": "tool_input.file_path"},
                    "renderer_trace": {"renderer": f"{host}_pretooluse", "output_contract": "stderr_context"},
                    "command_category": "shell_command",
                    "command_redacted": True,
                    "payload_source": "tool_input",
                    "risk": "needs-discoverability",
                    "decision": "allow",
                    "permission_decision": "allow",
                    "outcome": "needs_discoverability",
                    "marker_emitted": True,
                    "context_suppressed": False,
                    "tool_use_count": 1,
                    "governed_surface": True,
                    "redaction_count": 1,
                }
            )
            if transcript_evidence:
                rec.update(
                    {
                        "transcript_sha256": "a" * 64,
                        "command_fingerprint": "b" * 64,
                        "same_command_replay": True,
                    }
                )
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
        if (
            result["claims"]["prepush_installed"]
            or result["claims"]["prepush_enforced"]
            or result["claims"]["precommit_enforced"]
            or result["claims"]["git_clean"]
        ):
            failures.append("no-Git target must NOT claim prepush_installed/prepush_enforced/precommit_enforced/git_clean")

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
        git_gate_contract.write_git_gate_fixture(full, precommit="strict", prepush="full")
        subprocess.run(["git", "add", "."], cwd=full, text=True, capture_output=True, check=False, env=git_gate_contract.isolated_git_env())
        subprocess.run(
            ["git", "commit", "-m", "fixture gate"],
            cwd=full,
            text=True,
            capture_output=True,
            check=False,
            env=git_gate_contract.isolated_git_env(),
        )
        full_git = git_admission(full.resolve())
        if full_git["status"] != "PASS":
            failures.append(f"fully-gated Git target must PASS git_admission, got {full_git['status']}: {full_git['blockers']}")
        if not (full_git["prepush_installed"] and full_git["precommit_enforced"]):
            failures.append("fully-gated target must claim prepush_installed and precommit_enforced on real evidence")

        # 3a) Ceiling F21 — drain vs quality gate are SEPARATE claims, each proven
        #     by its own marker only. A drain-only pre-push (HOOK_MARKER, no
        #     gate-pre-git) proves the drain but NOT the project gate; a
        #     gate-only pre-push proves only a configured gate token. Neither
        #     marker proves enforcement without a resolved command.
        drain_only = root / "drain-only"
        git_gate_contract.write_git_gate_fixture(drain_only, precommit="strict", prepush="drain-only")
        subprocess.run(
            ["git", "add", "."], cwd=drain_only, text=True, capture_output=True, check=False, env=git_gate_contract.isolated_git_env()
        )
        subprocess.run(
            ["git", "commit", "-m", "fixture drain only"],
            cwd=drain_only,
            text=True,
            capture_output=True,
            check=False,
            env=git_gate_contract.isolated_git_env(),
        )
        drain_ev = prepush_evidence(drain_only.resolve())
        if not drain_ev.get("prepush_installed"):
            failures.append("F38: drain-only pre-push must still report prepush_installed=true")
        if not drain_ev.get("field_reports_prepush_drain") or drain_ev.get("project_prepush_gate") or drain_ev.get("prepush_enforced"):
            failures.append(
                "F38: drain-only pre-push must prove the drain claim and NOT quality enforcement, "
                f"got drain={drain_ev.get('field_reports_prepush_drain')} "
                f"gate={drain_ev.get('project_prepush_gate')} enforced={drain_ev.get('prepush_enforced')}"
            )
        drain_only_admission = git_admission(drain_only.resolve())
        if drain_only_admission["status"] != "BLOCKED":
            failures.append("F38: drain-only pre-push with strict pre-commit must BLOCK git_admission")
        elif not any("strict pre-push quality gate" in item for item in drain_only_admission.get("blockers", [])):
            failures.append("F38: drain-only blocker must name the missing strict pre-push quality gate")
        gate_only = root / "gate-only"
        git_gate_contract.write_git_gate_fixture(gate_only, precommit="none", prepush="unresolved-gate-only")
        gate_ev = prepush_evidence(gate_only.resolve())
        if gate_ev.get("field_reports_prepush_drain") or not gate_ev.get("project_prepush_gate") or gate_ev.get("prepush_enforced"):
            failures.append(
                "F38: unresolved gate-only pre-push must prove a configured gate token but NOT enforcement, "
                f"got drain={gate_ev.get('field_reports_prepush_drain')} "
                f"gate={gate_ev.get('project_prepush_gate')} enforced={gate_ev.get('prepush_enforced')}"
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

        # 3c) F37 — reproduced false green: the TES-installed hook must not exit
        #     0 or be admitted when no project commit:check and no installed TES
        #     oracle exists. The fixture is committed with --no-verify only to
        #     make Git clean; the hook itself must still fail closed.
        no_real_gate = root / "installed-no-real-gate"
        no_real_gate.mkdir()
        _init_git(no_real_gate)
        install = field_reports.install_hook(no_real_gate)
        if install.get("status") != "PASS":
            failures.append(f"F37: install_hook should install the fail-closed hook, got {install.get('status')}")
        hook = no_real_gate / ".git/hooks/pre-commit"
        hook_run = subprocess.run(
            [str(hook)], cwd=no_real_gate, text=True, capture_output=True, check=False, env=git_gate_contract.isolated_git_env()
        )
        if hook_run.returncode == 0:
            failures.append("F37: TES-installed pre-commit with no real gate must fail closed, not exit 0")
        subprocess.run(
            ["git", "add", "."], cwd=no_real_gate, text=True, capture_output=True, check=False, env=git_gate_contract.isolated_git_env()
        )
        subprocess.run(
            ["git", "commit", "--no-verify", "-m", "fixture install"],
            cwd=no_real_gate,
            text=True,
            capture_output=True,
            check=False,
            env=git_gate_contract.isolated_git_env(),
        )
        no_gate_precommit = precommit_evidence(no_real_gate.resolve())
        if no_gate_precommit.get("precommit_enforced"):
            failures.append("F37: canary admission must not mark a no-real-gate hook as precommit_enforced")
        no_gate_admission = git_admission(no_real_gate.resolve())
        if no_gate_admission.get("status") != "BLOCKED":
            failures.append("F37: clean installed target with no real pre-commit gate must BLOCK git_admission")

        # 4) Per-host native hook truthfulness: only Claude has its own runtime
        #    records; Codex+Cursor are configured but unobserved. Claude must be
        #    NATIVE_PASS; the others CONFIGURED_NOT_OBSERVED — never filled by
        #    Claude's records. Overall hooks status NEEDS_EVIDENCE.
        hosts_target = root / "hosts"
        hosts_target.mkdir()
        _init_git(hosts_target)
        for host in AGENTS:
            _configure_host_hooks(hosts_target, host)
        _write_host_runtime_record(
            hosts_target,
            "claude",
            provenance=tes_install.HOOK_PROVENANCE_HOST_REAL,
            transcript_evidence=True,
        )  # only Claude observed with ceiling-grade provenance
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

        for provenance, label, transcript_evidence in (
            (tes_install.HOOK_PROVENANCE_FIXTURE, "fixture", True),
            (tes_install.HOOK_PROVENANCE_MANUAL, "manual", True),
            (tes_install.HOOK_PROVENANCE_UNATTESTED, "unattested", True),
            (None, "legacy-unknown", True),
            (tes_install.HOOK_PROVENANCE_HOST_REAL, "host-real-without-transcript", False),
        ):
            target = root / f"provenance-{label}"
            target.mkdir()
            _init_git(target)
            _configure_host_hooks(target, "claude")
            _write_host_runtime_record(
                target,
                "claude",
                provenance=provenance,
                transcript_evidence=transcript_evidence,
            )
            result = host_hook_admission(target.resolve())
            if result["hosts"]["claude"]["class"] == NATIVE_PASS or "claude" in result.get("native_pass_hosts", []):
                failures.append(f"{label} hook runtime row must not become NATIVE_PASS")
            if result["status"] != "NEEDS_EVIDENCE":
                failures.append(f"{label} hook runtime row must keep canary admission at NEEDS_EVIDENCE")

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
