#!/usr/bin/env python3
"""Validate the commercial npx-style TES installer entrypoint."""

from __future__ import annotations

import argparse
import os
import json
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
VERSION = "0.3.98"
BIN_NAME = "tilly-engineer-skills"
DEFAULT_GITHUB_SPEC = "github:murillodutt/tilly-engineer-skills"
DEFAULT_GITHUB_REPO_URL = "https://github.com/murillodutt/tilly-engineer-skills.git"
CLAUDE_SESSIONSTART_MATCHER = "startup|resume|clear|compact"


def run(command: list[str], cwd: Path, timeout: float = 180.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


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
    if "[tes-install]" in text:
        return True
    if "{" in lines or "}" in lines:
        return True
    raw_json_keys = {"\"agent\":", "\"apply\":", "\"hooks\":", "\"stage\":", "\"postinstall\":"}
    return any(any(line.startswith(key) for key in raw_json_keys) for line in lines)


def commercial_output_failures(label: str, stdout: str) -> list[str]:
    failures: list[str] = []
    if "TES Installer" not in stdout:
        failures.append(f"{label} must render the commercial installer screen")
    if raw_engine_output_leaked(stdout):
        failures.append(f"{label} must not leak raw Python engine JSON or [tes-install] sentinels")
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
    if len(tes_handlers) != 1:
        failures.append("Claude SessionStart hook must install exactly one TES handler")
    elif "args" in tes_handlers[0]:
        failures.append("Claude SessionStart hook must use the official single command field")
    else:
        command = str(tes_handlers[0].get("command", ""))
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
        if tes_handlers[0].get("async") is not True:
            failures.append("Claude SessionStart hook must run asynchronously")
        if tes_handlers[0].get("asyncRewake") is not True:
            failures.append("Claude SessionStart hook must use native asyncRewake completion")
        if "TES first-session setup is running" not in str(tes_handlers[0].get("statusMessage", "")):
            failures.append("Claude SessionStart hook must display setup status while running")
    setup_skill = target / ".claude/skills/tes-setup/SKILL.md"
    if not setup_skill.exists():
        failures.append("Claude install must deliver /tes-setup as a project skill")
    else:
        setup_text = setup_skill.read_text(encoding="utf-8")
        for term in ("name: tes-setup", "/tes-init", ".tes/postinstall.json"):
            if term not in setup_text:
                failures.append(f"Claude /tes-setup skill missing contract term: {term}")
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
    return failures


def github_ref_specs(ref: str) -> list[str]:
    if ref.startswith("refs/"):
        return [ref]
    return [f"refs/heads/{ref}", f"refs/tags/{ref}"]


def git_ls_remote(repo_url: str, ref: str) -> tuple[list[str], list[str]]:
    command = ["git", "ls-remote", repo_url, *github_ref_specs(ref)]
    result = run(command, ROOT, timeout=120.0)
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    errors = []
    if result.returncode != 0:
        errors.append("git ls-remote failed")
        errors.extend(result.stderr.splitlines())
    return lines, errors


def github_package_self_test(
    *,
    github_spec: str,
    repo_url: str,
    ref: str,
    target: Path | None,
) -> int:
    failures = package_contract_failures()
    blockers: list[str] = []
    if not shutil.which("node"):
        failures.append("node executable is required")
    if not shutil.which("npm"):
        failures.append("npm executable is required")
    if not shutil.which("git"):
        failures.append("git executable is required")

    resolved_refs: list[str] = []
    if not failures:
        resolved_refs, ref_errors = git_ls_remote(repo_url, ref)
        if ref_errors:
            blockers.extend(ref_errors)
        elif not resolved_refs:
            blockers.append(
                f"missing GitHub ref {ref!r}; create refs/heads/{ref} or refs/tags/{ref} before certification"
            )

    command = [
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

    with tempfile.TemporaryDirectory(prefix="tes-github-npx-oracle-") as tempdir:
        work = Path(tempdir)
        dry_target = target or fixture(work, "github-npx-target")
        command.extend(["--target", str(dry_target)])
        if not failures and not blockers:
            exec_result = run(command, work, timeout=360.0)
            if exec_result.returncode != 0:
                failures.append("GitHub package spec npm exec failed")
                failures.extend(exec_result.stdout.splitlines())
                failures.extend(exec_result.stderr.splitlines())
            else:
                failures.extend(commercial_output_failures("GitHub package spec dry-run", exec_result.stdout))
            if (dry_target / ".tes").exists():
                failures.append("GitHub npx dry-run must not create .tes")

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
        "command": " ".join(command),
        "failures": failures,
        "blockers": blockers,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-npx:github-self-test] " + status)
    return exit_code


def self_test() -> int:
    failures = package_contract_failures()
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
            ".tes/postinstall.json",
            ".codex/config.toml",
            ".claude/settings.json",
            ".cursor/hooks.json",
        ):
            if not (accept_target / relpath).exists():
                failures.append(f"interactive accept install missing path: {relpath}")

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
                if "IMPORTANT" not in exec_result.stdout or "wait" not in exec_result.stdout or "/tes-setup" not in exec_result.stdout:
                    failures.append("npm exec package add must give clear first-session wait and /tes-setup guidance")
            for relpath in (
                ".tes/bin/tes_install.py",
                ".tes/tes-install-lock.json",
                ".tes/postinstall.json",
                ".codex/config.toml",
                ".claude/settings.json",
                ".claude/skills/tes-setup/SKILL.md",
                ".cursor/hooks.json",
            ):
                if not (install_target / relpath).exists():
                    failures.append(f"npm exec install missing path: {relpath}")
            sentinel = load_json(install_target / ".tes/postinstall.json") if (install_target / ".tes/postinstall.json").exists() else {}
            if sentinel.get("state") != "pending":
                failures.append("npm exec install must leave pending postinstall sentinel")
            if (install_target / ".claude/settings.json").exists():
                failures.extend(claude_hook_contract_failures(install_target))

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
            sentinel = load_json(install_target / ".tes/postinstall.json") if (install_target / ".tes/postinstall.json").exists() else {}
            if sentinel.get("state") != "complete":
                failures.append("installed hook must complete postinstall sentinel")
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
            if not (first_claude_target / ".claude/skills/tes-setup/SKILL.md").exists():
                failures.append("npm exec Claude-only package add must install /tes-setup skill")
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
            if first_claude_hook.returncode != 2:
                failures.append("installed Claude first-session asyncRewake hook failed")
                failures.extend(first_claude_hook.stdout.splitlines())
                failures.extend(first_claude_hook.stderr.splitlines())
            else:
                if first_claude_hook.stdout.strip():
                    failures.append("installed Claude asyncRewake must not emit JSON stdout on exit 2")
                if (
                    "TES first-session setup completed." not in first_claude_hook.stderr
                    or "Please, run /tes-setup for the report." not in first_claude_hook.stderr
                ):
                    failures.append("installed Claude first-session asyncRewake must wake with /tes-setup guidance")
                first_sentinel = load_json(first_claude_target / ".tes/postinstall.json")
                if first_sentinel.get("state") != "complete":
                    failures.append("installed Claude asyncRewake postinstall must complete before completion message")
                if first_sentinel.get("last_status") != "PASS":
                    failures.append("installed Claude asyncRewake postinstall must record PASS before completion message")

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
            "python3 <fixture>/.tes/bin/tes_install.py hook --agent codex --target <fixture>",
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
        help="Git ref to test, e.g. v0.3.98 or main.",
    )
    parser.add_argument("--target", type=Path, help="Optional dry-run target for GitHub npx self-test.")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.runtime_matrix:
        return runtime_matrix()
    if args.github_self_test:
        return github_package_self_test(
            github_spec=args.github_spec,
            repo_url=args.github_repo_url,
            ref=args.github_ref,
            target=args.target,
        )
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
