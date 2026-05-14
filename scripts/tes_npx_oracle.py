#!/usr/bin/env python3
"""Validate the commercial npx-style TES installer entrypoint."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.86"
BIN_NAME = "tilly-engineer-skills"


def run(command: list[str], cwd: Path, timeout: float = 180.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
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


def package_contract_failures() -> list[str]:
    failures: list[str] = []
    package = load_json(ROOT / "package.json")
    bin_field = package.get("bin")
    if not isinstance(bin_field, dict):
        failures.append("package.json must declare bin object")
    elif bin_field.get(BIN_NAME) != "./bin/tes.js":
        failures.append(f"package.json bin.{BIN_NAME} must be ./bin/tes.js")
    scripts = package.get("scripts") if isinstance(package.get("scripts"), dict) else {}
    if "tes:npx:self-test" not in scripts:
        failures.append("package.json missing script: tes:npx:self-test")
    return failures


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
        elif f"npx {BIN_NAME}@latest add" not in help_result.stdout:
            failures.append("help output must advertise npx add")

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
        if (dry_target / ".tes").exists():
            failures.append("dry-run must not create .tes")

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
            f"npm exec --yes --package <tarball> -- {BIN_NAME} add --target <fixture> --agent all --yes",
            "python3 <fixture>/.tes/bin/tes_install.py hook --agent codex --target <fixture>",
        ],
        "failures": failures,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-npx:self-test] " + result["status"])
    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
