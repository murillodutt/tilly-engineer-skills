#!/usr/bin/env python3
"""Plan low-friction assisted Tilly updates for an already meshed project."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.34"
REPO_URL = "https://github.com/murillodutt/tilly-engineer-skills"
REMOTE_PACKAGE_JSON = (
    "https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/package.json"
)
REMOTE_REF = "refs/heads/main"
VERSION_RE = re.compile(
    r"""(?x)
    (?:VERSION\s*=\s*|["']version["']\s*:\s*|Version:\s*`?|version:\s*)
    ["`]?
    (?P<version>\d+\.\d+\.\d+)
    """
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return path.name


def parse_semver(value: str | None) -> tuple[int, int, int] | None:
    if not value:
        return None
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", value.strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def compare_semver(left: str | None, right: str | None) -> int | None:
    parsed_left = parse_semver(left)
    parsed_right = parse_semver(right)
    if parsed_left is None or parsed_right is None:
        return None
    return (parsed_left > parsed_right) - (parsed_left < parsed_right)


def version_records(target: Path) -> list[dict[str, str]]:
    candidates = [
        ".tes/bin/tes_update.py",
        ".tes/bin/cortex_mcp.py",
        ".tes/bin/cortex.py",
        ".tes/bin/field_reports.py",
        ".tilly/bin/tilly_update.py",
        ".tilly/bin/cortex_mcp.py",
        ".tilly/bin/cortex.py",
        ".tilly/bin/field_reports.py",
        ".claude-plugin/plugin.json",
        "docs/agents/PROJECT-REGISTER.md",
        "README.md",
    ]
    evidence_dir = target / "docs/agents/evidence"
    evidence = sorted({*evidence_dir.glob("*tes*.md"), *evidence_dir.glob("*tilly*.md")})
    records: list[dict[str, str]] = []
    for relpath in [*candidates, *[rel(path, target) for path in evidence[-5:]]]:
        path = target / relpath
        if not path.exists() or not path.is_file():
            continue
        for match in VERSION_RE.finditer(read_text(path)):
            records.append({"path": relpath, "version": match.group("version")})
            break
    return records


def installed_version(records: list[dict[str, str]]) -> str | None:
    versions = sorted(
        (record["version"] for record in records if parse_semver(record.get("version"))),
        key=lambda item: parse_semver(item) or (0, 0, 0),
    )
    return versions[-1] if versions else None


def surfaces(target: Path) -> dict[str, bool]:
    return {
        "docs_agents": (target / "docs/agents").exists(),
        "cortex": (target / "docs/agents/cortex/CONTRACT.md").exists(),
        "codex": (target / "AGENTS.md").exists()
        or (target / ".agents/skills/tes-engineering-discipline/SKILL.md").exists(),
        "claude": (target / "CLAUDE.md").exists()
        or (target / ".claude-plugin/plugin.json").exists()
        or (target / "skills/tes-guidelines/SKILL.md").exists(),
        "cursor": (target / ".cursor/rules").exists() or (target / "CURSOR.md").exists(),
        "mcp_codex": (target / ".codex/config.toml").exists(),
        "mcp_claude": (target / ".mcp.json").exists(),
        "mcp_cursor": (target / ".cursor/mcp.json").exists(),
        "mcp_server": (target / ".tes/bin/cortex_mcp.py").exists()
        or (target / ".tilly/bin/cortex_mcp.py").exists(),
        "field_reports": (target / ".tes/bin/field_reports.py").exists()
        or (target / ".tilly/bin/field_reports.py").exists()
        or (target / ".git/hooks/pre-push").exists(),
    }


def legacy_retirement(target: Path) -> dict[str, Any]:
    try:
        import tes_legacy_retirement  # type: ignore
    except Exception as exc:  # noqa: BLE001 - update planning must stay non-mutating
        return {
            "status": "BLOCKED",
            "legacy_retirement_required": False,
            "reason": str(exc),
        }
    return tes_legacy_retirement.build_plan(target)


def project_state(surface_map: dict[str, bool]) -> str:
    routed_runtime = surface_map["codex"] or surface_map["claude"] or surface_map["cursor"]
    if surface_map["docs_agents"] and routed_runtime:
        return "meshed"
    if surface_map["docs_agents"] or routed_runtime:
        return "existing"
    return "new"


def runtime_surfaces(surface_map: dict[str, bool]) -> list[str]:
    runtimes = []
    for runtime in ("codex", "claude", "cursor"):
        if surface_map[runtime] or surface_map[f"mcp_{runtime}"]:
            runtimes.append(runtime)
    return runtimes


def recommended_route(state: str, runtimes: list[str], runtime: str | None) -> tuple[str, str]:
    if state == "new":
        return "current", "Tilly is not installed yet; run init semantics first."
    if len(runtimes) > 1:
        return "all", "Multiple IDE/runtime surfaces are already applied."
    if len(runtimes) == 1:
        return runtimes[0], f"Only {runtimes[0]} is currently applied."
    if runtime in {"codex", "claude", "cursor"}:
        return runtime, "No applied runtime surface was detected; use the current runtime."
    return "current", "No applied runtime surface was detected."


def fetch_remote_version(timeout: float) -> dict[str, str]:
    with urllib.request.urlopen(REMOTE_PACKAGE_JSON, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    version = str(payload.get("version") or "")
    if not parse_semver(version):
        raise ValueError("remote package.json has no semantic version")
    return {"status": "PASS", "version": version, "source": REMOTE_PACKAGE_JSON}


def fetch_remote_commit(timeout: float) -> dict[str, str]:
    result = subprocess.run(
        ["git", "ls-remote", REPO_URL, REMOTE_REF],
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-remote failed")
    commit = result.stdout.split()[0] if result.stdout.split() else ""
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("remote main commit not found")
    return {"status": "PASS", "commit": commit, "source": REPO_URL}


def remote_facts(args: argparse.Namespace) -> dict[str, Any]:
    version_fact: dict[str, Any]
    commit_fact: dict[str, Any]
    if args.remote_version:
        version_fact = {"status": "PASS", "version": args.remote_version, "source": "override"}
    elif args.offline:
        version_fact = {"status": "BLOCKED", "version": None, "source": "offline"}
    else:
        try:
            version_fact = fetch_remote_version(args.timeout)
        except Exception as exc:  # noqa: BLE001 - report blocker without failing update planning
            version_fact = {"status": "BLOCKED", "version": None, "source": REMOTE_PACKAGE_JSON, "reason": str(exc)}

    if args.remote_commit:
        commit_fact = {"status": "PASS", "commit": args.remote_commit, "source": "override"}
    elif args.offline:
        commit_fact = {"status": "BLOCKED", "commit": None, "source": "offline"}
    else:
        try:
            commit_fact = fetch_remote_commit(args.timeout)
        except Exception as exc:  # noqa: BLE001
            commit_fact = {"status": "BLOCKED", "commit": None, "source": REPO_URL, "reason": str(exc)}

    return {"version": version_fact, "commit": commit_fact}


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    target = args.target.expanduser().resolve()
    if not target.exists() or not target.is_dir():
        return {"version": VERSION, "status": "FAIL", "failures": [f"target is not a directory: {target}"]}

    records = version_records(target)
    surface_map = surfaces(target)
    legacy = legacy_retirement(target)
    state = project_state(surface_map)
    runtimes = runtime_surfaces(surface_map)
    route, route_reason = recommended_route(state, runtimes, args.runtime)
    remote = remote_facts(args)
    installed = installed_version(records)
    cloud_version = remote["version"].get("version")
    cmp_result = compare_semver(installed, cloud_version)
    update_available = True if cmp_result is not None and cmp_result < 0 else False
    update_status = (
        "AVAILABLE"
        if update_available
        else "CURRENT"
        if cmp_result == 0
        else "UNKNOWN"
    )
    if state == "new":
        intent = "/tes:init"
    elif update_available:
        intent = f"/tes:update {route}"
    else:
        intent = "/tes:doctor" if update_status == "CURRENT" else f"/tes:update {route}"

    result: dict[str, Any] = {
        "version": VERSION,
        "status": "PASS",
        "target": str(target),
        "project_state": state,
        "installed_version": installed,
        "installed_version_records": records,
        "remote_version": cloud_version,
        "remote_version_status": remote["version"].get("status"),
        "remote_commit": remote["commit"].get("commit"),
        "remote_commit_status": remote["commit"].get("status"),
        "update_status": update_status,
        "update_available": update_available,
        "legacy_retirement_required": bool(legacy.get("legacy_retirement_required")),
        "legacy_retirement_status": legacy.get("status"),
        "legacy_retirement_counts": legacy.get("counts", {}),
        "surfaces": surface_map,
        "applied_runtimes": runtimes,
        "recommended_route": route,
        "route_reason": route_reason,
        "recommended_intent": intent,
        "writes": [],
        "failures": [],
    }
    return result


def record_field_report(target: Path, result: dict[str, Any]) -> None:
    try:
        import field_reports  # type: ignore
    except Exception:
        return
    field_reports.safe_record_event(
        target,
        "tes_update",
        result["status"],
        "installer",
        "cli",
        details={
            "installed_version": result.get("installed_version") or "unknown",
            "cloud_version": result.get("remote_version") or "unknown",
            "update_available": result.get("update_available"),
            "route": result.get("recommended_route"),
            "surface_count": len(result.get("applied_runtimes") or []),
            "legacy_retirement_required": result.get("legacy_retirement_required"),
        },
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-update-") as tempdir:
        target = Path(tempdir)
        write(target / "docs/agents/cortex/CONTRACT.md", "# Contract\n")
        write(target / "AGENTS.md", "Route to docs/agents/**\n")
        write(target / "CLAUDE.md", "Route to docs/agents/**\n")
        write(target / ".cursor/rules/tes-guidelines.mdc", "Route to docs/agents/**\n")
        write(target / ".tes/bin/cortex_mcp.py", 'VERSION = "0.3.24"\n')
        write(target / ".agents/skills/tilly-init/SKILL.md", "name: tilly-init\n")
        args = argparse.Namespace(
            target=target,
            remote_version="0.3.34",
            remote_commit="a" * 40,
            runtime="codex",
            offline=False,
            timeout=0.1,
        )
        result = analyze(args)
        if result["project_state"] != "meshed":
            failures.append("meshed fixture must be detected as meshed")
        if result["update_status"] != "AVAILABLE":
            failures.append("older installed version must report update available")
        if result["recommended_route"] != "all":
            failures.append("multi-runtime fixture must recommend all")
        if result["recommended_intent"] != "/tes:update all":
            failures.append("multi-runtime update intent must be /tes:update all")
        if result["legacy_retirement_required"] is not True:
            failures.append("legacy runtime fixture must require legacy retirement")

    with tempfile.TemporaryDirectory(prefix="tes-update-single-") as tempdir:
        target = Path(tempdir)
        write(target / "docs/agents/PROJECT-REGISTER.md", "Generated by Tilly\n")
        write(target / "AGENTS.md", "Route to docs/agents/**\n")
        write(target / ".tes/bin/tes_update.py", f'VERSION = "{VERSION}"\n')
        args = argparse.Namespace(
            target=target,
            remote_version=VERSION,
            remote_commit="b" * 40,
            runtime="codex",
            offline=False,
            timeout=0.1,
        )
        result = analyze(args)
        if result["update_status"] != "CURRENT":
            failures.append("equal version must report current")
        if result["recommended_route"] != "codex":
            failures.append("single Codex fixture must recommend codex")

    with tempfile.TemporaryDirectory(prefix="tes-update-new-") as tempdir:
        target = Path(tempdir)
        args = argparse.Namespace(
            target=target,
            remote_version=VERSION,
            remote_commit="c" * 40,
            runtime="cursor",
            offline=False,
            timeout=0.1,
        )
        result = analyze(args)
        if result["project_state"] != "new":
            failures.append("empty fixture must be new")
        if result["recommended_intent"] != "/tes:init":
            failures.append("new fixture must route to /tes:init")

    return {"version": VERSION, "status": "PASS" if not failures else "FAIL", "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=["plan", "status"], default="plan")
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--runtime", choices=["codex", "claude", "cursor"])
    parser.add_argument("--remote-version")
    parser.add_argument("--remote-commit")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result = self_test() if args.self_test else analyze(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[tes-update] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
