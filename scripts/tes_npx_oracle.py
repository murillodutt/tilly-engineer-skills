#!/usr/bin/env python3
"""Validate the commercial npx-style TES installer entrypoint."""

from __future__ import annotations

import argparse
import os
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

try:
    import pty
    import select
except ImportError:  # pragma: no cover - Windows fallback
    pty = None  # type: ignore[assignment]
    select = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.181"
BIN_NAME = "tilly-engineer-skills"
DEFAULT_GITHUB_SPEC = "github:murillodutt/tilly-engineer-skills"
DEFAULT_GITHUB_REPO_URL = "https://github.com/murillodutt/tilly-engineer-skills.git"
CLAUDE_SESSIONSTART_MATCHER = "startup|resume|clear|compact"
CLAUDE_SETUP_RUNNING_MESSAGE = "IMPORTANT: TES setup is running. Please wait; do not start project work."


def run(command: list[str], cwd: Path, timeout: float = 180.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


def run_external_smoke(command: list[str], cwd: Path, timeout: float) -> tuple[subprocess.CompletedProcess[str] | None, str | None]:
    """Run an external-network install smoke (npm exec / bunx pulling a GitHub
    package). A timeout or a missing runtime here is an EXTERNAL condition — a
    slow GitHub clone, a cold bun cache, no network — not a product bug. Return
    (result, None) on completion, or (None, reason) so the caller can record a
    blocker (blocked_external) instead of letting TimeoutExpired crash the whole
    release-check with a traceback."""
    try:
        return run(command, cwd, timeout=timeout), None
    except subprocess.TimeoutExpired:
        return None, f"external install smoke timed out after {timeout:g}s: {command[0]} (network/clone latency, not a package defect)"
    except FileNotFoundError:
        return None, f"external install smoke runtime not found: {command[0]}"


def run_pty_script(
    command: list[str],
    cwd: Path,
    script: list[tuple[str, str]],
    timeout: float = 30.0,
) -> tuple[int | None, str]:
    if pty is None or select is None:
        return None, "pty unavailable"

    master_fd, slave_fd = pty.openpty()
    output: list[str] = []
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        close_fds=True,
    )
    os.close(slave_fd)
    next_response = 0
    deadline = time.monotonic() + timeout
    try:
        while True:
            if time.monotonic() > deadline:
                process.kill()
                return process.wait(timeout=5), "".join(output) + "\n[TES oracle timeout]"

            readable, _, _ = select.select([master_fd], [], [], 0.1)
            if readable:
                try:
                    chunk = os.read(master_fd, 4096)
                except OSError:
                    chunk = b""
                if chunk:
                    text = chunk.decode("utf-8", errors="replace")
                    output.append(text)
                    joined = "".join(output)
                    if next_response < len(script):
                        pattern, response = script[next_response]
                        if pattern in joined:
                            os.write(master_fd, response.encode("utf-8"))
                            next_response += 1

            code = process.poll()
            if code is not None:
                while True:
                    readable, _, _ = select.select([master_fd], [], [], 0)
                    if not readable:
                        break
                    try:
                        chunk = os.read(master_fd, 4096)
                    except OSError:
                        break
                    if not chunk:
                        break
                    output.append(chunk.decode("utf-8", errors="replace"))
                return code, "".join(output)
    finally:
        try:
            os.close(master_fd)
        except OSError:
            pass


def run_pty_cancel(command: list[str], cwd: Path, timeout: float = 30.0) -> tuple[int | None, str]:
    return run_pty_script(
        command,
        cwd,
        [
            ("Target project [", "\n"),
            ("Choose agents", "\n"),
            ("Installation style", "\n"),
            ("Install TES with these settings? [Y/n]", "n\n"),
        ],
        timeout=timeout,
    )


def run_pty_accept(command: list[str], cwd: Path, timeout: float = 60.0) -> tuple[int | None, str]:
    return run_pty_script(
        command,
        cwd,
        [
            ("Target project [", "\n"),
            ("Choose agents", "\n"),
            ("Installation style", "\n"),
            ("Install TES with these settings? [Y/n]", "\n"),
        ],
        timeout=timeout,
    )


def fixture(root: Path, name: str) -> Path:
    target = root / name
    target.mkdir(parents=True)
    (target / "README.md").write_text(f"# {name}\n\nTES npx fixture.\n", encoding="utf-8")
    (target / "package.json").write_text(
        json.dumps({"name": name, "scripts": {"test": "echo test"}}, indent=2) + "\n",
        encoding="utf-8",
    )
    (target / "src").mkdir()
    (target / "src/index.js").write_text("console.log('tes npx fixture')\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)
    return target


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def raw_engine_output_leaked(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines()]
    if "[tes-install]" in text or "[tes-" in text:
        return True
    if "{" in lines or "}" in lines:
        return True
    # Closing-punctuation fragments of a serialized JSON payload — `],` `},`
    # `}],` `}` `]` — were the exact garbage the failed install leaked. A line
    # made only of braces/brackets and commas carries no human meaning.
    if any(re.fullmatch(r"[{}\[\],]+,?", line) for line in lines if line):
        return True
    raw_json_keys = {"\"agent\":", "\"apply\":", "\"hooks\":", "\"mcp\":", "\"stage\":", "\"postinstall\":", "\"certification\":", "\"status\":"}
    return any(any(line.startswith(key) for key in raw_json_keys) for line in lines)


def commercial_output_failures(label: str, stdout: str) -> list[str]:
    failures: list[str] = []
    if "TES Installer" not in stdout:
        failures.append(f"{label} must render the commercial installer screen")
    if raw_engine_output_leaked(stdout):
        failures.append(f"{label} must not leak raw Python engine JSON or [tes-install] sentinels")
    return failures


def plant_stale_gate_record(target: Path) -> None:
    """Write a historical Mantra Gate record using a retired STATUS vocabulary
    (`PASS`, which is not a valid gate STATUS). This is the exact shape that
    drove a real install to certify BLOCKED and leak a serialized JSON blob as
    `],` `},` fragments. A stale historical record must downgrade certification
    to a clean NEEDS_REVIEW notice, never crash the install or leak fragments."""
    records = target / ".tes/field-reports/mantra-gates.jsonl"
    records.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "gate": {
            "VERIFY": "checked",
            "SCOPE": "small",
            "BEST_PATH": "direct",
            "DOCUMENT": "noted",
            "ORACLE": "ran tests",
            "RESOLVE": "done",
            "STATUS": "PASS",
        },
        "visible": "full",
    }
    records.write_text(json.dumps(record) + "\n", encoding="utf-8")


def stale_record_review_failures(label: str, code: int, stdout: str, stderr: str, target: Path) -> list[str]:
    """A re-certify run over a target carrying a stale gate record must: exit 0
    (the apply succeeded and is reversible — a review item is not a failure),
    keep the install lock APPLIED, and never leak raw engine JSON in either
    stream."""
    failures: list[str] = []
    if code != 0:
        failures.append(f"{label} must exit 0 on a post-apply review verdict, got {code}")
    if raw_engine_output_leaked(stdout):
        failures.append(f"{label} stdout must not leak raw engine JSON on a review verdict")
    if raw_engine_output_leaked(stderr):
        failures.append(f"{label} stderr must not leak raw engine JSON on a review verdict")
    if "TES installer failed" in stdout.lower() or "tes installer failed" in stderr.lower():
        failures.append(f"{label} must not report a hard failure when the apply succeeded")
    lock = target / ".tes/tes-install-lock.json"
    if lock.exists():
        try:
            apply_status = load_json(lock).get("apply", {}).get("status")
        except (json.JSONDecodeError, OSError):
            apply_status = None
        if apply_status not in {"APPLIED", "CLEAN_APPLIED"}:
            failures.append(f"{label} install lock apply.status must stay applied, got {apply_status!r}")
    return failures


def claude_hook_contract_failures(target: Path) -> list[str]:
    failures: list[str] = []
    settings_path = target / ".claude/settings.json"
    if not settings_path.exists():
        return ["Claude settings missing after install"]
    settings = load_json(settings_path)
    groups = settings.get("hooks", {}).get("SessionStart", [])
    if not isinstance(groups, list):
        return ["Claude SessionStart hooks must be a list"]
    matching_groups = [
        group
        for group in groups
        if isinstance(group, dict) and group.get("matcher") == CLAUDE_SESSIONSTART_MATCHER
    ]
    handlers = []
    for group in matching_groups:
        hooks = group.get("hooks")
        if isinstance(hooks, list):
            handlers.extend(hook for hook in hooks if isinstance(hook, dict))
    tes_handlers = [
        hook
        for hook in handlers
        if ".tes/bin/tes_install.py" in json.dumps(hook, sort_keys=True) and "--agent claude" in json.dumps(hook, sort_keys=True)
    ]
    if len(tes_handlers) != 2:
        failures.append("Claude SessionStart hook must install notice + asyncRewake TES handlers")
    else:
        if any("args" in handler for handler in tes_handlers):
            failures.append("Claude SessionStart hooks must use the official single command field")
        notice_handlers = [handler for handler in tes_handlers if "--announce-start" in str(handler.get("command", ""))]
        setup_handlers = [handler for handler in tes_handlers if "--rewake-on-complete" in str(handler.get("command", ""))]
        if len(notice_handlers) != 1:
            failures.append("Claude SessionStart hook must install one synchronous start notice handler")
        if len(setup_handlers) != 1:
            failures.append("Claude SessionStart hook must install one asyncRewake setup handler")
    if len(tes_handlers) == 2:
        notice = next((handler for handler in tes_handlers if "--announce-start" in str(handler.get("command", ""))), {})
        setup = next((handler for handler in tes_handlers if "--rewake-on-complete" in str(handler.get("command", ""))), {})
        notice_command = str(notice.get("command", ""))
        for term in (
            ".tes/bin/tes_install.py",
            "hook",
            "--agent claude",
            "--target",
            "${CLAUDE_PROJECT_DIR}",
            "--announce-start",
        ):
            if term not in notice_command:
                failures.append(f"Claude start notice hook command missing term: {term}")
        if notice.get("async") is True or notice.get("asyncRewake") is True:
            failures.append("Claude start notice hook must be synchronous so the running message is visible immediately")
        command = str(setup.get("command", ""))
        for term in (
            ".tes/bin/tes_install.py",
            "hook",
            "--agent claude",
            "--target",
            "${CLAUDE_PROJECT_DIR}",
            "--rewake-on-complete",
        ):
            if term not in command:
                failures.append(f"Claude SessionStart hook command missing term: {term}")
        if setup.get("async") is not True:
            failures.append("Claude SessionStart hook must run asynchronously")
        if setup.get("asyncRewake") is not True:
            failures.append("Claude SessionStart hook must use native asyncRewake completion")
        if CLAUDE_SETUP_RUNNING_MESSAGE not in str(setup.get("statusMessage", "")):
            failures.append("Claude SessionStart hook must display setup status while running")
    return failures


def mcp_all_contract_failures(target: Path, label: str) -> list[str]:
    failures: list[str] = []
    expected = (".codex/config.toml", ".mcp.json", ".cursor/mcp.json")
    for relpath in expected:
        if not (target / relpath).exists():
            failures.append(f"{label} missing MCP config: {relpath}")
    if (target / ".vscode/mcp.json").exists():
        failures.append(f"{label} --agent all must not create .vscode/mcp.json")
    codex_config = (target / ".codex/config.toml").read_text(encoding="utf-8") if (target / ".codex/config.toml").exists() else ""
    if "[mcp_servers.tes-cortex]" not in codex_config:
        failures.append(f"{label} must register Codex tes-cortex MCP server")
    for relpath in (".mcp.json", ".cursor/mcp.json"):
        if not (target / relpath).exists():
            continue
        data = load_json(target / relpath)
        servers = data.get("mcpServers") if isinstance(data.get("mcpServers"), dict) else {}
        if "tes-cortex" not in servers:
            failures.append(f"{label} must register tes-cortex in {relpath}")
    return failures


def package_contract_failures() -> list[str]:
    failures: list[str] = []
    package = load_json(ROOT / "package.json")
    if package.get("private") is not True:
        failures.append("package.json must keep private:true for GitHub-only distribution")
    engines = package.get("engines") if isinstance(package.get("engines"), dict) else {}
    if engines.get("node") != ">=18":
        failures.append("package.json engines.node must be >=18")
    if engines.get("bun") != ">=1.0.0":
        failures.append("package.json engines.bun must be >=1.0.0")
    bin_field = package.get("bin")
    if not isinstance(bin_field, dict):
        failures.append("package.json must declare bin object")
    elif bin_field.get(BIN_NAME) != "./bin/tes.js":
        failures.append(f"package.json bin.{BIN_NAME} must be ./bin/tes.js")
    bin_path = ROOT / "bin/tes.js"
    if not bin_path.exists():
        failures.append("bin/tes.js must exist")
    else:
        first_line = bin_path.read_text(encoding="utf-8").splitlines()[0]
        if first_line != "#!/usr/bin/env node":
            failures.append("bin/tes.js must start with #!/usr/bin/env node")
        bin_text = bin_path.read_text(encoding="utf-8")
        if "readSync" in bin_text or "readLineSync" in bin_text:
            failures.append("bin/tes.js must not use synchronous fd reads for interactive prompts")
        for expected in ("detectRuntime", "Node.js 18+", "Bun 1.0+", "bunx --silent --bun"):
            if expected not in bin_text:
                failures.append(f"bin/tes.js missing runtime compatibility contract: {expected}")
    scripts = package.get("scripts") if isinstance(package.get("scripts"), dict) else {}
    if "tes:npx:self-test" not in scripts:
        failures.append("package.json missing script: tes:npx:self-test")
    if "tes:npx:runtime-matrix" not in scripts:
        failures.append("package.json missing script: tes:npx:runtime-matrix")
    if "tes:npx:github-self-test" not in scripts:
        failures.append("package.json missing script: tes:npx:github-self-test")
    if scripts.get("release:check") != "python3 scripts/tes_npx_oracle.py --release-check":
        failures.append("package.json release:check must run tes_npx_oracle.py --release-check")
    return failures


def github_ref_specs(ref: str) -> list[str]:
    if ref.startswith("refs/"):
        refs = [ref]
        if ref.startswith("refs/tags/"):
            refs.append(f"{ref}^{{}}")
        return refs
    return [f"refs/heads/{ref}", f"refs/tags/{ref}", f"refs/tags/{ref}^{{}}"]


def git_ls_remote(repo_url: str, ref: str) -> tuple[list[str], list[str]]:
    command = ["git", "ls-remote", repo_url, *github_ref_specs(ref)]
    result = run(command, ROOT, timeout=120.0)
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    errors = []
    if result.returncode != 0:
        errors.append("git ls-remote failed")
        errors.extend(result.stderr.splitlines())
    return lines, errors


def ls_remote_ref_map(lines: list[str]) -> dict[str, str]:
    refs: dict[str, str] = {}
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            refs[parts[1]] = parts[0]
    return refs


def resolved_ref_commit(lines: list[str], ref: str) -> str:
    refs = ls_remote_ref_map(lines)
    for candidate in github_ref_specs(ref):
        peeled = f"{candidate}^{{}}" if not candidate.endswith("^{}") else candidate
        if peeled in refs:
            return refs[peeled]
    for candidate in github_ref_specs(ref):
        if candidate in refs:
            return refs[candidate]
    return ""


def git_rev_parse(ref: str) -> tuple[str, list[str]]:
    result = run(["git", "rev-parse", "--verify", ref], ROOT, timeout=30.0)
    if result.returncode != 0:
        return "", ["git rev-parse failed", *result.stderr.splitlines()]
    return result.stdout.strip(), []


def git_is_ancestor(ancestor: str, descendant: str) -> tuple[bool, list[str]]:
    result = run(["git", "merge-base", "--is-ancestor", ancestor, descendant], ROOT, timeout=30.0)
    if result.returncode == 0:
        return True, []
    if result.returncode == 1:
        return False, []
    return False, ["git merge-base --is-ancestor failed", *result.stderr.splitlines()]


def public_release_source_commit() -> tuple[str, list[str]]:
    index_path = ROOT / "docs" / "dist" / VERSION / "index.json"
    if not index_path.exists():
        return "", [f"missing public bundle index: {index_path.relative_to(ROOT)}"]
    try:
        index = load_json(index_path)
    except json.JSONDecodeError as exc:
        return "", [f"invalid public bundle index: {exc}"]
    metadata = index.get("metadata") if isinstance(index.get("metadata"), dict) else {}
    source_commit = str(index.get("source_commit") or metadata.get("source_commit") or "")
    if len(source_commit) != 40 or any(char not in "0123456789abcdef" for char in source_commit.lower()):
        return "", ["public bundle index source_commit must be a 40-character git SHA"]
    return source_commit, []


def github_package_self_test(
    *,
    github_spec: str,
    repo_url: str,
    ref: str,
    target: Path | None,
    require_current_head: bool = False,
    require_public_bundle_source: bool = False,
    include_bunx: bool = False,
) -> int:
    failures = package_contract_failures()
    blockers: list[str] = []
    if not shutil.which("node"):
        failures.append("node executable is required")
    if not shutil.which("npm"):
        failures.append("npm executable is required")
    if not shutil.which("git"):
        failures.append("git executable is required")
    if include_bunx and not shutil.which("bunx"):
        failures.append("bunx executable is required for release GitHub package certification")
    if include_bunx and not shutil.which("bun"):
        failures.append("bun executable is required for release GitHub package certification")

    resolved_refs: list[str] = []
    resolved_commit = ""
    if not failures:
        resolved_refs, ref_errors = git_ls_remote(repo_url, ref)
        resolved_commit = resolved_ref_commit(resolved_refs, ref)
        if ref_errors:
            blockers.extend(ref_errors)
        elif not resolved_refs:
            blockers.append(
                f"missing GitHub ref {ref!r}; create refs/heads/{ref} or refs/tags/{ref} before certification"
            )
        elif require_public_bundle_source:
            expected_commit, expected_errors = public_release_source_commit()
            if expected_errors:
                blockers.extend(expected_errors)
            else:
                is_ancestor, ancestor_errors = git_is_ancestor(expected_commit, resolved_commit)
                if ancestor_errors:
                    blockers.extend(ancestor_errors)
                elif not is_ancestor:
                    blockers.append(
                        f"GitHub ref {ref!r} resolves to {resolved_commit or 'unknown'}, "
                        f"but public bundle source_commit {expected_commit} is not an ancestor; "
                        "tag the release lineage before certification"
                    )
        elif require_current_head:
            head, head_errors = git_rev_parse("HEAD")
            if head_errors:
                blockers.extend(head_errors)
            elif resolved_commit != head:
                blockers.append(
                    f"GitHub ref {ref!r} resolves to {resolved_commit or 'unknown'}, "
                    f"but local HEAD is {head}; tag the release commit before certification"
                )

    npm_command = [
        "npm",
        "exec",
        "--yes",
        "--prefer-online",
        "--package",
        f"{github_spec}#{ref}",
        "--",
        BIN_NAME,
        "add",
        "--dry-run",
        "--agent",
        "all",
        "--yes",
    ]
    bunx_command = [
        "bunx",
        "--silent",
        "--bun",
        "--package",
        f"{github_spec}#{ref}",
        BIN_NAME,
        "add",
        "--dry-run",
        "--agent",
        "all",
        "--yes",
    ]

    with tempfile.TemporaryDirectory(prefix="tes-github-npx-oracle-") as tempdir:
        work = Path(tempdir)
        dry_target = target or fixture(work, "github-npx-target")
        npm_command.extend(["--target", str(dry_target)])
        if not failures and not blockers:
            exec_result, exec_block = run_external_smoke(npm_command, work, timeout=360.0)
            if exec_block:
                blockers.append(exec_block)
            elif exec_result.returncode != 0:
                failures.append("GitHub package spec npm exec failed")
                failures.extend(exec_result.stdout.splitlines())
                failures.extend(exec_result.stderr.splitlines())
            else:
                failures.extend(commercial_output_failures("GitHub package spec dry-run", exec_result.stdout))
            if (dry_target / ".tes").exists():
                failures.append("GitHub npx dry-run must not create .tes")

            if include_bunx and not blockers:
                bunx_target = fixture(work, "github-bunx-target")
                bunx_command.extend(["--target", str(bunx_target)])
                bunx_result, bunx_block = run_external_smoke(bunx_command, work, timeout=360.0)
                if bunx_block:
                    blockers.append(bunx_block)
                elif bunx_result.returncode != 0:
                    failures.append("GitHub package spec bunx dry-run failed")
                    failures.extend(bunx_result.stdout.splitlines())
                    failures.extend(bunx_result.stderr.splitlines())
                else:
                    failures.extend(commercial_output_failures("GitHub package spec bunx dry-run", bunx_result.stdout))
                if (bunx_target / ".tes").exists():
                    failures.append("GitHub bunx dry-run must not create .tes")

    if failures:
        status = "FAIL"
        classification = "product_bug"
        exit_code = 1
    elif blockers:
        status = "BLOCKED"
        classification = "blocked_external"
        exit_code = 2
    else:
        status = "PASS"
        classification = "certified_local"
        exit_code = 0

    result = {
        "version": VERSION,
        "status": status,
        "classification": classification,
        "coverage": "github-npx-installer",
        "bin": BIN_NAME,
        "package_spec": f"{github_spec}#{ref}",
        "repo_url": repo_url,
        "ref": ref,
        "resolved_refs": resolved_refs,
        "resolved_commit": resolved_commit,
        "require_current_head": require_current_head,
        "require_public_bundle_source": require_public_bundle_source,
        "include_bunx": include_bunx,
        "commands": [
            " ".join(npm_command),
            *([" ".join(bunx_command)] if include_bunx else []),
        ],
        "failures": failures,
        "blockers": blockers,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-npx:github-self-test] " + status)
    return exit_code


def manage_roundtrip_failures(work: Path) -> list[str]:
    """NPX-level reversibility round-trip through bin/tes.js (the entrypoint
    adopters use): minimal install -> attach skills -> detach skills -> uninstall,
    plus a read-only doctor report. Asserts the project returns to a clean state
    with zero residue and that each command surfaces the engine verdict.
    """
    failures: list[str] = []
    target = fixture(work, "npx-manage-roundtrip-target")

    # Minimal capsule-only install via the bin.
    install = run(["node", "bin/tes.js", "add", "--target", str(target),
                   "--agent", "claude", "--yes", "--attach", "capsule"], ROOT)
    if install.returncode != 0:
        failures.append("npx minimal install failed")
        return failures
    if (target / ".claude/skills").exists():
        failures.append("minimal capsule install must not materialize skills")

    # Attach skills via the bin.
    attach = run(["node", "bin/tes.js", "attach", "skills", "--target", str(target), "--yes"], ROOT)
    if attach.returncode != 0:
        failures.append("npx attach skills failed")
        failures.extend(attach.stderr.splitlines()[:4])
    if not (target / ".claude/skills/tes-map/SKILL.md").exists():
        failures.append("npx attach skills did not materialize the skill command set")
    if "ATTACHED" not in attach.stdout:
        failures.append("npx attach must surface the ATTACHED verdict")

    # Doctor: read-only health report; must not mutate the target.
    before = sorted(p.name for p in target.rglob("*") if p.is_file())
    doc = run(["node", "bin/tes.js", "doctor", "--target", str(target)], ROOT)
    after = sorted(p.name for p in target.rglob("*") if p.is_file())
    if doc.returncode != 0:
        failures.append("npx doctor failed")
    if before != after:
        failures.append("npx doctor must be read-only (it changed files)")
    if "skills" not in doc.stdout:
        failures.append("npx doctor must report the skills attachment")

    # Detach skills via the bin.
    detach = run(["node", "bin/tes.js", "detach", "skills", "--target", str(target), "--yes"], ROOT)
    if detach.returncode != 0:
        failures.append("npx detach skills failed")
    if (target / ".claude/skills").exists():
        failures.append("npx detach skills left a residue (skill tree not removed)")
    if "DETACHED" not in detach.stdout:
        failures.append("npx detach must surface the DETACHED verdict")

    # Destructive commands require --yes.
    no_yes = run(["node", "bin/tes.js", "uninstall", "--target", str(target)], ROOT)
    if no_yes.returncode == 0:
        failures.append("npx uninstall without --yes must not proceed")

    # Uninstall via the bin: zero residue.
    uninstall = run(["node", "bin/tes.js", "uninstall", "--target", str(target), "--yes"], ROOT)
    if uninstall.returncode != 0:
        failures.append("npx uninstall failed")
    if (target / ".tes").exists():
        failures.append("npx uninstall did not remove the capsule")
    leftover = [p for p in (".claude/skills", "CLAUDE.md", ".mcp.json", ".claude/settings.json")
                if (target / p).exists()]
    if leftover:
        failures.append(f"npx uninstall left project-visible residue: {leftover}")
    return failures


def self_test() -> int:
    failures = package_contract_failures()

    # Gap 3: an external install smoke that exceeds its timeout must degrade to a
    # blocker reason, never raise TimeoutExpired and crash the release-check with
    # a traceback. A missing runtime must likewise become a reason, not a crash.
    with tempfile.TemporaryDirectory(prefix="tes-npx-smoke-guard-") as smoke_dir:
        smoke_cwd = Path(smoke_dir)
        timed = run_external_smoke([sys.executable, "-c", "import time; time.sleep(5)"], smoke_cwd, timeout=0.2)
        if timed[0] is not None or not timed[1] or "timed out" not in timed[1]:
            failures.append("run_external_smoke must return a timeout reason instead of raising TimeoutExpired")
        missing = run_external_smoke(["tes-nonexistent-binary-xyz"], smoke_cwd, timeout=5.0)
        if missing[0] is not None or not missing[1] or "not found" not in missing[1]:
            failures.append("run_external_smoke must return a not-found reason for a missing runtime")
        ok = run_external_smoke([sys.executable, "-c", "print('ok')"], smoke_cwd, timeout=10.0)
        if ok[1] is not None or ok[0] is None or ok[0].returncode != 0:
            failures.append("run_external_smoke must pass through a successful command result")

    if not shutil.which("node"):
        failures.append("node executable is required")
    if not shutil.which("npm"):
        failures.append("npm executable is required")
    if not shutil.which("bun"):
        failures.append("bun executable is required for Bun compatibility certification")
    if not shutil.which("bunx"):
        failures.append("bunx executable is required for Bun package execution certification")
    if failures:
        result = {"version": VERSION, "status": "FAIL", "failures": failures}
        print(json.dumps(result, indent=2, sort_keys=True))
        print("[tes-npx:self-test] FAIL")
        return 1

    with tempfile.TemporaryDirectory(prefix="tes-npx-oracle-") as tempdir:
        work = Path(tempdir)
        dry_target = fixture(work, "dry-target")
        install_target = fixture(work, "install-target")
        pack_dir = work / "pack"
        pack_dir.mkdir()

        help_result = run(["node", "bin/tes.js", "--help"], ROOT)
        if help_result.returncode != 0:
            failures.append("node bin/tes.js --help failed")
            failures.extend(help_result.stdout.splitlines())
            failures.extend(help_result.stderr.splitlines())
        elif f"github:murillodutt/{BIN_NAME}#v{VERSION}" not in help_result.stdout:
            failures.append("help output must advertise GitHub npx add")

        fake_bin = work / "fake-python-bin"
        fake_bin.mkdir()
        fake_python = fake_bin / "python3"
        fake_python.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' '{\"executable\":\"/fake/python3\",\"version\":\"3.9.6\",\"tomllib\":false}'\n",
            encoding="utf-8",
        )
        fake_python.chmod(0o755)
        python_failure_env = {**os.environ, "PATH": str(fake_bin)}
        python_failure_env.pop("PYTHON", None)
        python_failure = subprocess.run(
            [
                shutil.which("node") or "node",
                "bin/tes.js",
                "add",
                "--dry-run",
                "--target",
                str(work / "old-python-target"),
                "--agent",
                "claude",
                "--yes",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=180.0,
            env=python_failure_env,
        )
        python_failure_output = f"{python_failure.stdout}\n{python_failure.stderr}"
        if python_failure.returncode == 0:
            failures.append("old Python fixture must fail before install")
        if "Python 3.11+ is required" not in python_failure_output:
            failures.append("old Python fixture must print actionable Python 3.11+ guidance")
        if "Python 3.9.6" not in python_failure_output:
            failures.append("old Python fixture must report the detected Python version")

        dry_result = run(
            [
                "node",
                "bin/tes.js",
                "add",
                "--dry-run",
                "--target",
                str(dry_target),
                "--agent",
                "all",
                "--yes",
            ],
            ROOT,
        )
        if dry_result.returncode != 0:
            failures.append("node bin/tes.js add --dry-run failed")
            failures.extend(dry_result.stdout.splitlines())
            failures.extend(dry_result.stderr.splitlines())
        else:
            failures.extend(commercial_output_failures("node dry-run", dry_result.stdout))
            if "Dry run complete. No files were written." not in dry_result.stdout:
                failures.append("node dry-run must clearly state that no files were written")
        if (dry_target / ".tes").exists():
            failures.append("dry-run must not create .tes")

        bun_target = fixture(work, "bun-dry-target")
        bun_result = run(
            [
                "bun",
                "bin/tes.js",
                "add",
                "--dry-run",
                "--target",
                str(bun_target),
                "--agent",
                "all",
                "--yes",
            ],
            ROOT,
        )
        if bun_result.returncode != 0:
            failures.append("bun bin/tes.js add --dry-run failed")
            failures.extend(bun_result.stdout.splitlines())
            failures.extend(bun_result.stderr.splitlines())
        else:
            failures.extend(commercial_output_failures("bun dry-run", bun_result.stdout))
            if "Dry run complete. No files were written." not in bun_result.stdout:
                failures.append("bun dry-run must clearly state that no files were written")
        if (bun_target / ".tes").exists():
            failures.append("bun dry-run must not create .tes")

        cancel_target = fixture(work, "interactive-cancel-target")
        cancel_code, cancel_output = run_pty_cancel(
            ["node", "bin/tes.js", "add", "--target", str(cancel_target), "--agent", "all"],
            ROOT,
        )
        if cancel_code is None:
            failures.append("interactive cancel prompt pty test could not run")
        elif cancel_code != 130:
            failures.append(f"interactive cancel prompt must exit 130, got {cancel_code}")
            failures.extend(cancel_output.splitlines())
        if "EAGAIN" in cancel_output or "node:fs" in cancel_output or "readSync" in cancel_output:
            failures.append("interactive prompt must not leak Node fd read errors")
            failures.extend(cancel_output.splitlines())
        for expected in ("Choose agents", "Installation style", "Review"):
            if expected not in cancel_output:
                failures.append(f"interactive prompt must show {expected!r}")
        if (cancel_target / ".tes").exists():
            failures.append("interactive cancellation must not create .tes")

        accept_target = fixture(work, "interactive-accept-target")
        accept_code, accept_output = run_pty_accept(
            ["node", "bin/tes.js", "add", "--target", str(accept_target), "--agent", "all"],
            ROOT,
        )
        if accept_code is None:
            failures.append("interactive accept prompt pty test could not run")
        elif accept_code != 0:
            failures.append(f"interactive accept prompt must exit 0, got {accept_code}")
            failures.extend(accept_output.splitlines())
        else:
            failures.extend(commercial_output_failures("interactive accept", accept_output))
        for relpath in (
            ".tes/bin/tes_install.py",
            ".codex/config.toml",
            ".mcp.json",
            ".cursor/mcp.json",
            ".claude/settings.json",
            ".cursor/hooks.json",
        ):
            if not (accept_target / relpath).exists():
                failures.append(f"interactive accept install missing path: {relpath}")
        failures.extend(mcp_all_contract_failures(accept_target, "interactive accept install"))

        # Regression: a stale historical gate record must not crash the install
        # or leak `],` `},` JSON fragments. Plant one into the freshly installed
        # target, then re-run the bin (idempotent preserve re-certify) and assert
        # a clean, non-leaking NEEDS_REVIEW outcome with the apply still applied.
        if not failures:
            plant_stale_gate_record(accept_target)
            recert = run(
                ["node", "bin/tes.js", "add", "--target", str(accept_target), "--agent", "all", "--yes"],
                ROOT,
            )
            failures.extend(
                stale_record_review_failures(
                    "stale-record re-certify",
                    recert.returncode,
                    recert.stdout,
                    recert.stderr,
                    accept_target,
                )
            )

        pack_result = run(["npm", "pack", "--pack-destination", str(pack_dir)], ROOT, timeout=240.0)
        if pack_result.returncode != 0:
            failures.append("npm pack failed")
            failures.extend(pack_result.stdout.splitlines())
            failures.extend(pack_result.stderr.splitlines())
            tarballs: list[Path] = []
        else:
            tarballs = sorted(pack_dir.glob("*.tgz"))
            if not tarballs:
                failures.append("npm pack did not create a tarball")

        if not failures and tarballs:
            tarball = tarballs[-1]
            bunx_target = fixture(work, "bunx-install-target")
            bunx_result = run(
                [
                    "bunx",
                    "--silent",
                    "--bun",
                    "--package",
                    str(tarball),
                    BIN_NAME,
                    "add",
                    "--dry-run",
                    "--target",
                    str(bunx_target),
                    "--agent",
                    "all",
                    "--yes",
                ],
                work,
                timeout=300.0,
            )
            if bunx_result.returncode != 0:
                failures.append("bunx --bun package dry-run failed")
                failures.extend(bunx_result.stdout.splitlines())
                failures.extend(bunx_result.stderr.splitlines())
            else:
                failures.extend(commercial_output_failures("bunx --bun package dry-run", bunx_result.stdout))
            if (bunx_target / ".tes").exists():
                failures.append("bunx --bun dry-run must not create .tes")

            exec_result = run(
                [
                    "npm",
                    "exec",
                    "--yes",
                    "--package",
                    str(tarball),
                    "--",
                    BIN_NAME,
                    "add",
                    "--target",
                    str(install_target),
                    "--agent",
                    "all",
                    "--yes",
                ],
                work,
                timeout=300.0,
            )
            if exec_result.returncode != 0:
                failures.append("npm exec package add failed")
                failures.extend(exec_result.stdout.splitlines())
                failures.extend(exec_result.stderr.splitlines())
            else:
                failures.extend(commercial_output_failures("npm exec package add", exec_result.stdout))
                if "TES is ready for this project." not in exec_result.stdout:
                    failures.append("npm exec package add must finish with a human success message")
                # ADR 0004 (amended): the public default delivers a full,
                # reversible TES. The follow-up must describe full materialization
                # and the reversibility path, not a capsule-only install.
                required_followup_terms = (
                    "full, reversible workspace",
                    "may ask you to trust the project hook before it fires",
                    "uninstall",
                )
                for term in required_followup_terms:
                    if term not in exec_result.stdout:
                        failures.append(f"npm exec package add missing platform follow-up term: {term}")
            # The functional default materializes the full TES: capsule runtime,
            # MCP, hooks, the engineering-discipline bootloaders, and the project
            # skill command set. Every one of these must be present.
            for relpath in (
                ".tes/bin/tes_install.py",
                ".tes/tes-install-lock.json",
                ".codex/config.toml",
                ".mcp.json",
                ".cursor/mcp.json",
                ".claude/settings.json",
                ".cursor/hooks.json",
                "AGENTS.md",
                "CLAUDE.md",
                "CURSOR.md",
                ".agents/skills/tes-map/SKILL.md",
                ".claude/skills/tes-map/SKILL.md",
                ".cursor/rules/tes-guidelines.mdc",
                ".cursor/rules/tes-runtime-capabilities.mdc",
            ):
                if not (install_target / relpath).exists():
                    failures.append(f"npm exec install missing path: {relpath}")
            # docs-mesh stays opt-in (it authors project docs), so the default must
            # NOT write docs/agents/**. The postinstall sentinel is NOT docs-mesh —
            # it records first-session state for the installed hook and IS expected
            # in the functional default (which attaches hooks).
            for relpath in (
                "docs/agents/PROJECT-CONTEXT.md",
                "docs/agents/PROJECT-REGISTER.md",
            ):
                if (install_target / relpath).exists():
                    failures.append(f"npm exec default install must not materialize docs-mesh path: {relpath}")
            failures.extend(mcp_all_contract_failures(install_target, "npm exec install"))
            # The functional default attaches hooks, so it must leave a pending
            # postinstall sentinel for the SessionStart hook to read; without it the
            # hook fires into an empty state and the post-install flow is dead.
            sentinel = load_json(install_target / ".tes/postinstall.json") if (install_target / ".tes/postinstall.json").exists() else {}
            if not sentinel:
                failures.append("npm exec default install must leave a pending postinstall sentinel for the hook")
            elif sentinel.get("state") != "pending":
                failures.append(f"default postinstall sentinel must start pending, got {sentinel.get('state')}")
            if (install_target / ".claude/settings.json").exists():
                failures.extend(claude_hook_contract_failures(install_target))
            claude_start_result = run(
                [
                    sys.executable,
                    str(install_target / ".tes/bin/tes_install.py"),
                    "hook",
                    "--agent",
                    "claude",
                    "--target",
                    str(install_target),
                    "--announce-start",
                ],
                work,
                timeout=60.0,
            )
            if claude_start_result.returncode != 0:
                failures.append("installed Claude start notice hook failed")
                failures.extend(claude_start_result.stdout.splitlines())
                failures.extend(claude_start_result.stderr.splitlines())
            else:
                try:
                    start_payload = json.loads(claude_start_result.stdout)
                except json.JSONDecodeError:
                    start_payload = {}
                    failures.append("installed Claude start notice hook must emit structured JSON")
                # With a pending sentinel present, the start notice must announce
                # the running setup (not stay silent).
                if not start_payload:
                    failures.append("installed Claude start notice must announce while postinstall is pending")
                elif "systemMessage" not in start_payload:
                    failures.append("installed Claude start notice must carry the setup-running systemMessage")

            hook_result = run(
                [
                    sys.executable,
                    str(install_target / ".tes/bin/tes_install.py"),
                    "hook",
                    "--agent",
                    "codex",
                    "--target",
                    str(install_target),
                ],
                work,
                timeout=300.0,
            )
            if hook_result.returncode != 0:
                failures.append("installed first-session hook failed")
                failures.extend(hook_result.stdout.splitlines())
                failures.extend(hook_result.stderr.splitlines())
            # The install-time pending sentinel must persist; the codex hook reads
            # it (and may advance it), it does not erase it.
            sentinel = load_json(install_target / ".tes/postinstall.json") if (install_target / ".tes/postinstall.json").exists() else {}
            if not sentinel:
                failures.append("postinstall sentinel must persist for the first-session hook to read")
            claude_hook_result = run(
                [
                    sys.executable,
                    str(install_target / ".tes/bin/tes_install.py"),
                    "hook",
                    "--agent",
                    "claude",
                    "--target",
                    str(install_target),
                ],
                work,
                timeout=300.0,
            )
            if claude_hook_result.returncode != 0:
                failures.append("installed Claude hook retry failed")
                failures.extend(claude_hook_result.stdout.splitlines())
                failures.extend(claude_hook_result.stderr.splitlines())
            else:
                try:
                    claude_payload = json.loads(claude_hook_result.stdout)
                except json.JSONDecodeError:
                    claude_payload = {}
                    failures.append("installed Claude hook must emit structured hook JSON")
                hook_output = claude_payload.get("hookSpecificOutput") if isinstance(claude_payload, dict) else None
                if not isinstance(hook_output, dict):
                    failures.append("installed Claude hook output missing hookSpecificOutput")
                elif hook_output.get("hookEventName") != "SessionStart":
                    failures.append("installed Claude hook output must target SessionStart")
                else:
                    context = hook_output.get("additionalContext")
                    if not isinstance(context, str) or "TES SessionStart hook ran" not in context:
                        failures.append("installed Claude hook output must provide TES additionalContext")
                    if isinstance(context, str) and '"commands"' in context:
                        failures.append("installed Claude hook context must not leak raw command JSON")
                if "systemMessage" in claude_payload:
                    failures.append("installed Claude idempotent retry must stay quiet after postinstall is complete")

            first_claude_target = fixture(work, "claude-first-hook-target")
            first_claude_install = run(
                [
                    "npm",
                    "exec",
                    "--yes",
                    "--package",
                    str(tarball),
                    "--",
                    BIN_NAME,
                    "add",
                    "--target",
                    str(first_claude_target),
                    "--agent",
                    "claude",
                    "--yes",
                ],
                work,
                timeout=300.0,
            )
            if first_claude_install.returncode != 0:
                failures.append("npm exec Claude-only package add failed")
                failures.extend(first_claude_install.stdout.splitlines())
                failures.extend(first_claude_install.stderr.splitlines())
            # ADR 0004 (amended): the functional default materializes the project
            # skill command set for the selected agent, so Claude-only must install
            # its skills (tes-setup among them) and the discipline bootloader.
            if not (first_claude_target / ".claude/skills/tes-setup/SKILL.md").exists():
                failures.append("npm exec Claude-only default add must install the project skill set")
            if not (first_claude_target / "CLAUDE.md").exists():
                failures.append("npm exec Claude-only default add must install the discipline bootloader")
            if (first_claude_target / ".claude/settings.json").exists():
                failures.extend(claude_hook_contract_failures(first_claude_target))
            first_start_notice = run(
                [
                    sys.executable,
                    str(first_claude_target / ".tes/bin/tes_install.py"),
                    "hook",
                    "--agent",
                    "claude",
                    "--target",
                    str(first_claude_target),
                    "--announce-start",
                ],
                work,
                timeout=60.0,
            )
            if first_start_notice.returncode != 0:
                failures.append("installed Claude first-session start notice failed")
                failures.extend(first_start_notice.stdout.splitlines())
            elif first_start_notice.stdout.strip() in {"", "{}"}:
                # Claude-only default attaches hooks, so the pending sentinel exists
                # and the start notice must announce the running setup.
                failures.append("installed Claude first-session start notice must announce while postinstall is pending")
                failures.extend(first_start_notice.stderr.splitlines())
            first_claude_hook = run(
                [
                    sys.executable,
                    str(first_claude_target / ".tes/bin/tes_install.py"),
                    "hook",
                    "--agent",
                    "claude",
                    "--target",
                    str(first_claude_target),
                    "--rewake-on-complete",
                ],
                work,
                timeout=300.0,
            )
            # --rewake-on-complete runs the post-install flow, marks the sentinel
            # complete, and exits 2 — the SessionStart rewake signal Claude Code
            # uses to reprocess the session. Exit 2 here is success, not failure.
            if first_claude_hook.returncode not in {0, 2}:
                failures.append("installed Claude default asyncRewake hook failed")
                failures.extend(first_claude_hook.stdout.splitlines())
                failures.extend(first_claude_hook.stderr.splitlines())
            else:
                # On exit 2 the SessionStart rewake message goes to stderr (that is
                # what Claude Code surfaces to the user); on exit 0 it may be stdout.
                rewake_text = first_claude_hook.stderr + first_claude_hook.stdout
                if "setup completed" not in rewake_text:
                    failures.append("asyncRewake completion must announce setup completion")
                # The sentinel must persist and have advanced to complete.
                first_sentinel = load_json(first_claude_target / ".tes/postinstall.json") if (first_claude_target / ".tes/postinstall.json").exists() else {}
                if not first_sentinel:
                    failures.append("postinstall sentinel must persist for the Claude first-session lifecycle")
                elif first_sentinel.get("state") != "complete":
                    failures.append(f"asyncRewake must advance the sentinel to complete, got {first_sentinel.get('state')}")
            first_complete_notice = run(
                [
                    sys.executable,
                    str(first_claude_target / ".tes/bin/tes_install.py"),
                    "hook",
                    "--agent",
                    "claude",
                    "--target",
                    str(first_claude_target),
                    "--announce-start",
                ],
                work,
                timeout=60.0,
            )
            if first_complete_notice.returncode != 0:
                failures.append("installed Claude complete start notice failed")
            else:
                try:
                    first_complete_payload = json.loads(first_complete_notice.stdout)
                except json.JSONDecodeError:
                    first_complete_payload = {}
                    failures.append("installed Claude complete start notice must emit structured JSON")
                if "systemMessage" in first_complete_payload:
                    failures.append("installed Claude start notice must stay quiet after postinstall is complete")

        # NPX-level reversibility: install -> attach -> detach -> uninstall + doctor
        # through bin/tes.js (the command surface this line adds).
        failures.extend(manage_roundtrip_failures(work))

    result = {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "coverage": "npx-commercial-installer",
        "bin": BIN_NAME,
        "commands": [
            "node bin/tes.js --help",
            "node bin/tes.js add --dry-run --target <fixture> --agent all --yes",
            "bun bin/tes.js add --dry-run --target <fixture> --agent all --yes",
            "node bin/tes.js add --target <fixture> --agent all # interactive cancel via pty",
            "node bin/tes.js add --target <fixture> --agent all # interactive accept via pty",
            f"npm exec --yes --package <tarball> -- {BIN_NAME} add --target <fixture> --agent all --yes",
            f"bunx --silent --bun --package <tarball> {BIN_NAME} add --dry-run --target <fixture> --agent all --yes",
            "node bin/tes.js attach skills / detach skills / uninstall / doctor --target <fixture>",
            "python3 <fixture>/.tes/bin/tes_install.py hook --agent codex --target <fixture>",
            "python3 <fixture>/.tes/bin/tes_install.py hook --agent claude --announce-start --target <fixture>",
            "old Python fixture fails with Python 3.11+ guidance",
            "commercial installer screen without raw Python JSON",
        ],
        "failures": failures,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-npx:self-test] " + result["status"])
    return 0 if not failures else 1


def runtime_matrix() -> int:
    failures = package_contract_failures()
    required = ["npx", "node", "npm", "bun", "bunx"]
    for executable in required:
        if not shutil.which(executable):
            failures.append(f"{executable} executable is required for runtime matrix certification")

    with tempfile.TemporaryDirectory(prefix="tes-npx-runtime-matrix-") as tempdir:
        work = Path(tempdir)
        targets = {
            "node-current": fixture(work, "node-current-target"),
            "bun-current": fixture(work, "bun-current-target"),
            "bunx-package": fixture(work, "bunx-package-target"),
        }
        node_versions = ["18", "20", "22"]
        for version in node_versions:
            target = fixture(work, f"node-{version}-target")
            result = run(
                [
                    "npx",
                    "-y",
                    f"node@{version}",
                    "bin/tes.js",
                    "add",
                    "--dry-run",
                    "--target",
                    str(target),
                    "--agent",
                    "all",
                    "--yes",
                ],
                ROOT,
                timeout=240.0,
            )
            if result.returncode != 0:
                failures.append(f"Node.js {version} dry-run failed")
                failures.extend(result.stdout.splitlines())
                failures.extend(result.stderr.splitlines())
            else:
                failures.extend(commercial_output_failures(f"Node.js {version} dry-run", result.stdout))
            if (target / ".tes").exists():
                failures.append(f"Node.js {version} dry-run must not create .tes")

        current_node = run(
            [
                "node",
                "bin/tes.js",
                "add",
                "--dry-run",
                "--target",
                str(targets["node-current"]),
                "--agent",
                "all",
                "--yes",
            ],
            ROOT,
        )
        if current_node.returncode != 0:
            failures.append("current Node.js dry-run failed")
            failures.extend(current_node.stdout.splitlines())
            failures.extend(current_node.stderr.splitlines())
        else:
            failures.extend(commercial_output_failures("current Node.js dry-run", current_node.stdout))

        current_bun = run(
            [
                "bun",
                "bin/tes.js",
                "add",
                "--dry-run",
                "--target",
                str(targets["bun-current"]),
                "--agent",
                "all",
                "--yes",
            ],
            ROOT,
        )
        if current_bun.returncode != 0:
            failures.append("current Bun dry-run failed")
            failures.extend(current_bun.stdout.splitlines())
            failures.extend(current_bun.stderr.splitlines())
        else:
            failures.extend(commercial_output_failures("current Bun dry-run", current_bun.stdout))

        pack_dir = work / "pack"
        pack_dir.mkdir()
        pack_result = run(["npm", "pack", "--pack-destination", str(pack_dir)], ROOT, timeout=240.0)
        tarballs = sorted(pack_dir.glob("*.tgz")) if pack_result.returncode == 0 else []
        if pack_result.returncode != 0 or not tarballs:
            failures.append("runtime matrix npm pack failed")
            failures.extend(pack_result.stdout.splitlines())
            failures.extend(pack_result.stderr.splitlines())
        else:
            bunx_package = run(
                [
                    "bunx",
                    "--silent",
                    "--bun",
                    "--package",
                    str(tarballs[-1]),
                    BIN_NAME,
                    "add",
                    "--dry-run",
                    "--target",
                    str(targets["bunx-package"]),
                    "--agent",
                    "all",
                    "--yes",
                ],
                work,
                timeout=300.0,
            )
            if bunx_package.returncode != 0:
                failures.append("bunx --bun packaged dry-run failed")
                failures.extend(bunx_package.stdout.splitlines())
                failures.extend(bunx_package.stderr.splitlines())
            else:
                failures.extend(commercial_output_failures("bunx --bun packaged dry-run", bunx_package.stdout))

    result = {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "coverage": "node18-node20-node22-current-node-bun-bunx",
        "bin": BIN_NAME,
        "node_versions": ["18", "20", "22", "current"],
        "bun": "current",
        "failures": failures,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-npx:runtime-matrix] " + result["status"])
    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--runtime-matrix", action="store_true")
    parser.add_argument("--github-self-test", action="store_true")
    parser.add_argument(
        "--release-check",
        action="store_true",
        help="Certify the fixed GitHub release ref against the public bundle source commit, npm exec, and bunx.",
    )
    parser.add_argument(
        "--require-current-head",
        action="store_true",
        help="Require the remote ref to resolve to local HEAD.",
    )
    parser.add_argument(
        "--include-bunx",
        action="store_true",
        help="Also dry-run the GitHub package spec through bunx --bun.",
    )
    parser.add_argument(
        "--github-spec",
        default=os.environ.get("TES_GITHUB_NPX_SPEC", DEFAULT_GITHUB_SPEC),
        help="GitHub npm package spec without #ref.",
    )
    parser.add_argument(
        "--github-repo-url",
        default=os.environ.get("TES_GITHUB_REPO_URL", DEFAULT_GITHUB_REPO_URL),
        help="Git remote used for ref preflight.",
    )
    parser.add_argument(
        "--github-ref",
        default=os.environ.get("TES_GITHUB_NPX_REF", f"v{VERSION}"),
        help="Git ref to test, e.g. v0.3.181 or main.",
    )
    parser.add_argument("--target", type=Path, help="Optional dry-run target for GitHub npx self-test.")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.runtime_matrix:
        return runtime_matrix()
    if args.github_self_test or args.release_check:
        return github_package_self_test(
            github_spec=args.github_spec,
            repo_url=args.github_repo_url,
            ref=args.github_ref,
            target=args.target,
            require_current_head=args.require_current_head,
            require_public_bundle_source=args.release_check,
            include_bunx=args.include_bunx or args.release_check,
        )
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
