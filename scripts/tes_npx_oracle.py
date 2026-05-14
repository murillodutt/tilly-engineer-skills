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
VERSION = "0.3.88"
BIN_NAME = "tilly-engineer-skills"
DEFAULT_GITHUB_SPEC = "github:murillodutt/tilly-engineer-skills"
DEFAULT_GITHUB_REPO_URL = "https://github.com/murillodutt/tilly-engineer-skills.git"


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
            ("Agent hooks", "\n"),
            ("Install mode", "\n"),
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
            ("Agent hooks", "\n"),
            ("Install mode", "\n"),
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


def package_contract_failures() -> list[str]:
    failures: list[str] = []
    package = load_json(ROOT / "package.json")
    if package.get("private") is not True:
        failures.append("package.json must keep private:true for GitHub-only distribution")
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
    scripts = package.get("scripts") if isinstance(package.get("scripts"), dict) else {}
    if "tes:npx:self-test" not in scripts:
        failures.append("package.json missing script: tes:npx:self-test")
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
        for expected in ("Agent hooks", "Install mode", "Ready to install"):
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
                if "TES is installed locally." not in exec_result.stdout:
                    failures.append("npm exec package add must finish with a human success message")
            for relpath in (
                ".tes/bin/tes_install.py",
                ".tes/tes-install-lock.json",
                ".tes/postinstall.json",
                ".codex/config.toml",
                ".claude/settings.json",
                ".cursor/hooks.json",
            ):
                if not (install_target / relpath).exists():
                    failures.append(f"npm exec install missing path: {relpath}")
            sentinel = load_json(install_target / ".tes/postinstall.json") if (install_target / ".tes/postinstall.json").exists() else {}
            if sentinel.get("state") != "pending":
                failures.append("npm exec install must leave pending postinstall sentinel")

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

    result = {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "coverage": "npx-commercial-installer",
        "bin": BIN_NAME,
        "commands": [
            "node bin/tes.js --help",
            "node bin/tes.js add --dry-run --target <fixture> --agent all --yes",
            "node bin/tes.js add --target <fixture> --agent all # interactive cancel via pty",
            "node bin/tes.js add --target <fixture> --agent all # interactive accept via pty",
            f"npm exec --yes --package <tarball> -- {BIN_NAME} add --target <fixture> --agent all --yes",
            "python3 <fixture>/.tes/bin/tes_install.py hook --agent codex --target <fixture>",
            "commercial installer screen without raw Python JSON",
        ],
        "failures": failures,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-npx:self-test] " + result["status"])
    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
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
        help="Git ref to test, e.g. v0.3.88 or latest.",
    )
    parser.add_argument("--target", type=Path, help="Optional dry-run target for GitHub npx self-test.")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
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
