#!/usr/bin/env python3
"""Plan low-friction assisted Tilly updates for an already meshed project."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.39"
REPO_URL = "https://github.com/murillodutt/tilly-engineer-skills"
REMOTE_PACKAGE_JSON = (
    "https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills/main/package.json"
)
REMOTE_RAW_ORIGIN = "https://raw.githubusercontent.com/murillodutt/tilly-engineer-skills"
REMOTE_RAW_BASE = f"{REMOTE_RAW_ORIGIN}/main"
REMOTE_REF = "refs/heads/main"
HELPER_FILES = (
    "cortex.py",
    "cortex_mcp.py",
    "cortex_embed.mjs",
    "field_reports.py",
    "tes_update.py",
    "tes_legacy_retirement.py",
    "root_context.py",
)
HELPER_CONTRACT_MARKERS = {
    "field_reports.py": ('SCHEMA = "tes-field-report@2"',),
}
UPDATE_SCOPES = ("none", "helpers-only", "adapter-config", "full-convergence")
POST_LAYER_ZERO_FINAL_PROBE_CONTRACT = (
    "helper_contract_status=PASS",
    "update_available=False",
    "recommended_update_scope=none",
)
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


def read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError:
        return b""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(read_bytes(path))


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


def remote_raw_base(ref: str | None = None) -> str:
    return f"{REMOTE_RAW_ORIGIN}/{ref or 'main'}"


def remote_raw_url(path: str, ref: str | None = None) -> str:
    return f"{remote_raw_base(ref)}/{path.lstrip('/')}"


def fetch_remote_version(timeout: float, ref: str | None = None) -> dict[str, str]:
    url = remote_raw_url("package.json", ref) if ref else REMOTE_PACKAGE_JSON
    with urllib.request.urlopen(url, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    version = str(payload.get("version") or "")
    if not parse_semver(version):
        raise ValueError("remote package.json has no semantic version")
    return {"status": "PASS", "version": version, "source": url}


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


def helper_manifest_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    helpers = payload.get("helpers", payload)
    if not isinstance(helpers, dict):
        raise ValueError("remote helper manifest must be an object")
    normalized: dict[str, dict[str, Any]] = {}
    for name in HELPER_FILES:
        value = helpers.get(name)
        if isinstance(value, str):
            normalized[name] = {"sha256": value}
        elif isinstance(value, dict) and isinstance(value.get("sha256"), str):
            normalized[name] = dict(value)
    return normalized


def local_helper_manifest() -> dict[str, Any]:
    helpers: dict[str, dict[str, Any]] = {}
    source_root = ROOT / "scripts"
    source_label = "local-package"
    if not source_root.exists():
        source_root = ROOT / "bin"
        source_label = "installed-helper"
    for name in HELPER_FILES:
        path = source_root / name
        data = read_bytes(path)
        if not data:
            continue
        text = data.decode("utf-8", errors="replace")
        helpers[name] = {
            "sha256": sha256_bytes(data),
            "source": f"{source_label}:{name}",
            "markers": {
                marker: marker in text
                for marker in HELPER_CONTRACT_MARKERS.get(name, ())
            },
        }
    if len(helpers) != len(HELPER_FILES):
        missing = sorted(set(HELPER_FILES) - set(helpers))
        raise FileNotFoundError(f"missing local helper source: {', '.join(missing)}")
    return {"status": "PASS", "helpers": helpers, "source": source_label}


def fetch_remote_helper_manifest(timeout: float, ref: str | None = None) -> dict[str, Any]:
    helpers: dict[str, dict[str, Any]] = {}
    base = remote_raw_base(ref)
    for name in HELPER_FILES:
        url = f"{base}/scripts/{name}"
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = response.read()
        text = data.decode("utf-8", errors="replace")
        helpers[name] = {
            "sha256": sha256_bytes(data),
            "source": url,
            "markers": {
                marker: marker in text
                for marker in HELPER_CONTRACT_MARKERS.get(name, ())
            },
        }
    return {"status": "PASS", "helpers": helpers, "source": f"{base}/scripts"}


def remote_helper_facts(args: argparse.Namespace, required: bool = True, remote_commit: str | None = None) -> dict[str, Any]:
    if not required:
        return {"status": "SKIP", "helpers": {}, "source": "not-installed"}
    manifest_path = getattr(args, "remote_helper_manifest", None)
    if getattr(args, "local_package_helpers", False):
        try:
            return local_helper_manifest()
        except Exception as exc:  # noqa: BLE001 - report blocker without hiding update state
            return {"status": "BLOCKED", "helpers": {}, "source": "local-package", "reason": str(exc)}
    if manifest_path:
        try:
            return {
                "status": "PASS",
                "helpers": helper_manifest_from_payload(json.loads(manifest_path.read_text(encoding="utf-8"))),
                "source": str(manifest_path),
            }
        except Exception as exc:  # noqa: BLE001
            return {"status": "BLOCKED", "helpers": {}, "source": str(manifest_path), "reason": str(exc)}
    if args.offline:
        return {"status": "BLOCKED", "helpers": {}, "source": "offline"}
    try:
        return fetch_remote_helper_manifest(args.timeout, remote_commit)
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "BLOCKED",
            "helpers": {},
            "source": f"{remote_raw_base(remote_commit)}/scripts",
            "reason": str(exc),
        }


def remote_facts(args: argparse.Namespace, helper_required: bool = True) -> dict[str, Any]:
    version_fact: dict[str, Any]
    commit_fact: dict[str, Any]
    if args.remote_commit:
        commit_fact = {"status": "PASS", "commit": args.remote_commit, "source": "override"}
    elif args.offline:
        commit_fact = {"status": "BLOCKED", "commit": None, "source": "offline"}
    else:
        try:
            commit_fact = fetch_remote_commit(args.timeout)
        except Exception as exc:  # noqa: BLE001
            commit_fact = {"status": "BLOCKED", "commit": None, "source": REPO_URL, "reason": str(exc)}

    remote_commit = str(commit_fact.get("commit") or "") if commit_fact.get("status") == "PASS" else None
    if args.remote_version:
        version_fact = {"status": "PASS", "version": args.remote_version, "source": "override"}
    elif args.offline:
        version_fact = {"status": "BLOCKED", "version": None, "source": "offline"}
    else:
        try:
            version_fact = fetch_remote_version(args.timeout, remote_commit)
        except Exception as exc:  # noqa: BLE001 - report blocker without failing update planning
            version_fact = {
                "status": "BLOCKED",
                "version": None,
                "source": remote_raw_url("package.json", remote_commit),
                "reason": str(exc),
            }

    return {
        "version": version_fact,
        "commit": commit_fact,
        "helpers": remote_helper_facts(args, helper_required, remote_commit),
    }


def installed_helper_records(target: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for bin_dir in (".tes/bin", ".tilly/bin"):
        for name in HELPER_FILES:
            path = target / bin_dir / name
            if not path.exists() or not path.is_file():
                continue
            text = read_text(path)
            records.append(
                {
                    "name": name,
                    "path": rel(path, target),
                    "sha256": sha256_file(path),
                    "markers": {
                        marker: marker in text
                        for marker in HELPER_CONTRACT_MARKERS.get(name, ())
                    },
                }
            )
    legacy_update = target / ".tilly/bin/tilly_update.py"
    if legacy_update.exists() and legacy_update.is_file():
        records.append(
            {
                "name": "tes_update.py",
                "path": rel(legacy_update, target),
                "sha256": sha256_file(legacy_update),
                "legacy_name": "tilly_update.py",
                "markers": {},
            }
        )
    return records


def helper_contract(target: Path, remote_helpers: dict[str, Any], installed: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    installed = installed if installed is not None else installed_helper_records(target)
    if not installed:
        return {"status": "NOT_INSTALLED", "records": [], "failures": []}

    if remote_helpers.get("status") != "PASS":
        return {
            "status": "BLOCKED",
            "records": [
                {
                    **record,
                    "status": "UNKNOWN",
                    "remote_sha256": None,
                    "failures": ["remote helper manifest unavailable"],
                }
                for record in installed
            ],
            "failures": [str(remote_helpers.get("reason") or "remote helper manifest unavailable")],
        }

    expected = remote_helpers.get("helpers") or {}
    records: list[dict[str, Any]] = []
    failures: list[str] = []
    for record in installed:
        name = str(record["name"])
        remote = expected.get(name)
        record_failures: list[str] = []
        status = "PASS"
        if not isinstance(remote, dict) or not remote.get("sha256"):
            status = "UNKNOWN"
            record_failures.append("remote helper hash missing")
        elif record["sha256"] != remote["sha256"]:
            status = "STALE_HELPER"
            record_failures.append("installed helper hash differs from remote source")

        for marker, present in record.get("markers", {}).items():
            if not present:
                status = "STALE_HELPER"
                record_failures.append(f"missing contract marker: {marker}")

        if record.get("legacy_name"):
            status = "STALE_HELPER"
            record_failures.append("legacy helper name is still installed")

        if record_failures:
            failures.append(f"{record['path']}: {'; '.join(record_failures)}")
        records.append(
            {
                **record,
                "remote_sha256": remote.get("sha256") if isinstance(remote, dict) else None,
                "status": status,
                "failures": record_failures,
            }
        )

    statuses = {str(record["status"]) for record in records}
    status = (
        "STALE_HELPERS"
        if "STALE_HELPER" in statuses
        else "BLOCKED"
        if "UNKNOWN" in statuses
        else "PASS"
    )
    return {"status": status, "records": records, "failures": failures}


def package_source_available() -> bool:
    return (ROOT / "scripts/tes_update.py").exists() and (ROOT / "scripts/field_reports.py").exists()


def helper_source_text(name: str) -> str:
    for folder in ("scripts", "bin"):
        text = read_text(ROOT / folder / name)
        if text:
            return text
    if name == "field_reports.py":
        return f'VERSION = "{VERSION}"\nSCHEMA = "tes-field-report@2"\n'
    return f'VERSION = "{VERSION}"\n'


def recommended_update_scope(state: str, update_available: bool, helper_status: str) -> str:
    if state == "new":
        return "full-convergence"
    if helper_status == "STALE_HELPERS":
        return "helpers-only"
    if update_available:
        return "full-convergence"
    return "none"


def recommended_intent(state: str, update_status: str, route: str, update_scope: str) -> str:
    if state == "new":
        return "/tes:init"
    if update_scope == "helpers-only":
        return f"/tes:update {route} --helpers-only"
    if update_scope in {"adapter-config", "full-convergence"}:
        return f"/tes:update {route}"
    return "/tes:doctor" if update_status == "CURRENT" else f"/tes:update {route}"


def post_layer_zero_final_probe(result: dict[str, Any]) -> dict[str, Any]:
    ready = (
        result.get("helper_contract_status") == "PASS"
        and result.get("update_available") is False
        and result.get("recommended_update_scope") == "none"
    )
    return {
        "required_after": "post-Layer Zero helper overwrite",
        "command": "tes_update.py plan --json-only --record-field-report",
        "event": "final Field Reports `tes_update` event",
        "contract": list(POST_LAYER_ZERO_FINAL_PROBE_CONTRACT),
        "status": "READY" if ready else "PENDING",
    }


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
    installed_helpers = installed_helper_records(target)
    remote = remote_facts(args, bool(installed_helpers))
    installed = installed_version(records)
    cloud_version = remote["version"].get("version")
    cmp_result = compare_semver(installed, cloud_version)
    helper = helper_contract(target, remote["helpers"], installed_helpers)
    helper_stale = helper["status"] == "STALE_HELPERS"
    update_available = True if (cmp_result is not None and cmp_result < 0) or helper_stale else False
    update_reasons: list[str] = []
    if cmp_result is not None and cmp_result < 0:
        update_reasons.append("installed_version_behind")
    if helper_stale:
        update_reasons.append("helper_contract_drift")
    if helper["status"] == "BLOCKED":
        update_reasons.append("helper_contract_blocked")
    update_status = (
        "AVAILABLE"
        if update_available
        else "CURRENT"
        if cmp_result == 0 and helper["status"] in {"PASS", "NOT_INSTALLED"}
        else "UNKNOWN"
    )
    update_scope = recommended_update_scope(state, update_available, helper["status"])
    intent = recommended_intent(state, update_status, route, update_scope)

    result: dict[str, Any] = {
        "version": VERSION,
        "status": "PASS",
        "target": str(target),
        "project_state": state,
        "installed_version": installed,
        "installed_version_records": records,
        "remote_version": cloud_version,
        "remote_version_status": remote["version"].get("status"),
        "remote_version_source": remote["version"].get("source"),
        "remote_commit": remote["commit"].get("commit"),
        "remote_commit_status": remote["commit"].get("status"),
        "remote_commit_source": remote["commit"].get("source"),
        "remote_helper_status": remote["helpers"].get("status"),
        "remote_helper_source": remote["helpers"].get("source"),
        "update_status": update_status,
        "update_available": update_available,
        "update_reasons": update_reasons,
        "requires_helper_overwrite": helper_stale,
        "helper_update_action": "overwrite-with-backup" if helper_stale else "none",
        "recommended_update_scope": update_scope,
        "adapter_refresh_required": update_scope in {"adapter-config", "full-convergence"},
        "next_probe_required": update_scope != "none",
        "helper_contract_status": helper["status"],
        "installed_helper_records": helper["records"],
        "helper_contract_failures": helper["failures"],
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
    result["post_layer_zero_final_probe"] = post_layer_zero_final_probe(result)
    return result


def record_field_report(target: Path, result: dict[str, Any]) -> dict[str, Any] | None:
    if not (result.get("surfaces") or {}).get("field_reports"):
        return None
    try:
        import field_reports  # type: ignore
    except Exception:
        return None
    try:
        return field_reports.record_event(
            target,
            "tes_update",
            result["status"],
            "installer",
            "cli",
            details={
                "installed_version": result.get("installed_version") or "unknown",
                "cloud_version": result.get("remote_version") or "unknown",
                "update_available": result.get("update_available"),
                "update_reasons": ",".join(result.get("update_reasons") or []),
                "helper_contract_status": result.get("helper_contract_status"),
                "update_scope": result.get("recommended_update_scope"),
                "recommended_update_scope": result.get("recommended_update_scope"),
                "route": result.get("recommended_route"),
                "surface_count": len(result.get("applied_runtimes") or []),
                "legacy_retirement_required": result.get("legacy_retirement_required"),
                "post_layer_zero_final_probe_status": (
                    (result.get("post_layer_zero_final_probe") or {}).get("status")
                ),
            },
        )
    except Exception:
        return None


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    mode = "package" if package_source_available() else "installed"
    coverage = "source-package-contract" if mode == "package" else "installed-helper-contract"
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
            remote_version=VERSION,
            remote_commit="a" * 40,
            remote_helper_manifest=None,
            local_package_helpers=True,
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
        if result["recommended_update_scope"] != "helpers-only":
            failures.append("stale multi-runtime fixture must recommend helpers-only update scope")
        if result["recommended_intent"] != "/tes:update all --helpers-only":
            failures.append("multi-runtime helper update intent must be /tes:update all --helpers-only")
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
            remote_helper_manifest=None,
            local_package_helpers=True,
            runtime="codex",
            offline=False,
            timeout=0.1,
        )
        write(target / ".tes/bin/tes_update.py", helper_source_text("tes_update.py"))
        result = analyze(args)
        if result["update_status"] != "CURRENT":
            failures.append("equal version must report current")
        if result["recommended_route"] != "codex":
            failures.append("single Codex fixture must recommend codex")
        if result["recommended_update_scope"] != "none":
            failures.append("current fixture must recommend no update scope")
        final_probe = result.get("post_layer_zero_final_probe") or {}
        if final_probe.get("status") != "READY":
            failures.append("current fixture must be ready for post-Layer Zero final recorded probe")
        if final_probe.get("contract") != list(POST_LAYER_ZERO_FINAL_PROBE_CONTRACT):
            failures.append("final recorded probe contract must list required proof fields")

    with tempfile.TemporaryDirectory(prefix="tes-update-stale-helper-") as tempdir:
        target = Path(tempdir)
        write(target / "docs/agents/PROJECT-REGISTER.md", "Generated by Tilly\n")
        write(target / "AGENTS.md", "Route to docs/agents/**\n")
        write(target / ".tes/bin/tes_update.py", helper_source_text("tes_update.py"))
        write(target / ".tes/bin/field_reports.py", f'VERSION = "{VERSION}"\nSCHEMA = "tes-field-report@1"\n')
        args = argparse.Namespace(
            target=target,
            remote_version=VERSION,
            remote_commit="d" * 40,
            remote_helper_manifest=None,
            local_package_helpers=True,
            runtime="codex",
            offline=False,
            timeout=0.1,
        )
        result = analyze(args)
        if result["update_status"] != "AVAILABLE":
            failures.append("equal version with stale helper must report update available")
        if result["helper_contract_status"] != "STALE_HELPERS":
            failures.append("stale field_reports contract must report STALE_HELPERS")
        if "helper_contract_drift" not in result["update_reasons"]:
            failures.append("stale helper update must include helper_contract_drift reason")
        if result["requires_helper_overwrite"] is not True:
            failures.append("stale helper update must require helper overwrite with backup")
        if result["recommended_update_scope"] != "helpers-only":
            failures.append("stale helper update must recommend helpers-only scope")
        if result["recommended_intent"] != "/tes:update codex --helpers-only":
            failures.append("stale helper update must recommend helpers-only intent")

    with tempfile.TemporaryDirectory(prefix="tes-update-new-") as tempdir:
        target = Path(tempdir)
        args = argparse.Namespace(
            target=target,
            remote_version=VERSION,
            remote_commit="c" * 40,
            remote_helper_manifest=None,
            local_package_helpers=True,
            runtime="cursor",
            offline=False,
            timeout=0.1,
        )
        result = analyze(args)
        if result["project_state"] != "new":
            failures.append("empty fixture must be new")
        if result["recommended_intent"] != "/tes:init":
            failures.append("new fixture must route to /tes:init")

    with tempfile.TemporaryDirectory(prefix="tes-update-field-report-") as tempdir:
        target = Path(tempdir)
        subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)
        write(target / "docs/agents/PROJECT-REGISTER.md", "Generated by Tilly\n")
        write(target / "AGENTS.md", "Route to docs/agents/**\n")
        write(target / ".tes/bin/tes_update.py", helper_source_text("tes_update.py"))
        write(target / ".tes/bin/field_reports.py", helper_source_text("field_reports.py"))
        args = argparse.Namespace(
            target=target,
            remote_version=VERSION,
            remote_commit="e" * 40,
            remote_helper_manifest=None,
            local_package_helpers=True,
            runtime="codex",
            offline=False,
            timeout=0.1,
        )
        readonly = subprocess.run(
            [
                sys.executable,
                __file__,
                "plan",
                "--target",
                str(target),
                "--remote-version",
                VERSION,
                "--remote-commit",
                "e" * 40,
                "--local-package-helpers",
                "--json-only",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if readonly.returncode != 0:
            failures.append("tes_update read-only plan must pass")
            failures.extend(readonly.stderr.splitlines())
        outbox = target / ".tes/field-reports/outbox.jsonl"
        lines = outbox.read_text(encoding="utf-8").splitlines() if outbox.exists() else []
        if lines:
            failures.append("tes_update read-only plan must not write Field Reports evidence")
        recorded = subprocess.run(
            [
                sys.executable,
                __file__,
                "plan",
                "--target",
                str(target),
                "--remote-version",
                VERSION,
                "--remote-commit",
                "e" * 40,
                "--local-package-helpers",
                "--json-only",
                "--record-field-report",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if recorded.returncode != 0:
            failures.append("tes_update recorded plan must pass")
            failures.extend(recorded.stderr.splitlines())
        lines = outbox.read_text(encoding="utf-8").splitlines() if outbox.exists() else []
        if not lines:
            failures.append("tes_update field report must write an outbox event")
        else:
            event = json.loads(lines[-1])
            facts = event.get("facts", {})
            if event.get("event") != "tes_update":
                failures.append("tes_update field report must use tes_update event")
            if facts.get("helper_contract_status") != "PASS":
                failures.append("tes_update field report must include helper_contract_status")
            if facts.get("update_available") != "False":
                failures.append("tes_update field report must include update_available=False")
            if facts.get("route") != "codex":
                failures.append("tes_update field report must include recommended route")
            if facts.get("update_scope") != "none":
                failures.append("tes_update field report must include update scope")
            if facts.get("recommended_update_scope") != "none":
                failures.append("tes_update field report must include recommended update scope")
            if facts.get("post_layer_zero_final_probe_status") != "READY":
                failures.append("tes_update field report must include final probe readiness")
        readonly_again = subprocess.run(
            [
                sys.executable,
                __file__,
                "plan",
                "--target",
                str(target),
                "--remote-version",
                VERSION,
                "--remote-commit",
                "e" * 40,
                "--local-package-helpers",
                "--json-only",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if readonly_again.returncode != 0:
            failures.append("tes_update repeated read-only plan must pass")
            failures.extend(readonly_again.stderr.splitlines())
        repeated_lines = outbox.read_text(encoding="utf-8").splitlines() if outbox.exists() else []
        if len(repeated_lines) != len(lines):
            failures.append("tes_update repeated read-only plan must not duplicate Field Reports evidence")

    original_fetch_remote_version = fetch_remote_version
    original_remote_helper_facts = remote_helper_facts
    observed_refs: dict[str, str | None] = {}

    def fake_fetch_remote_version(timeout: float, ref: str | None = None) -> dict[str, str]:
        observed_refs["version_ref"] = ref
        return {"status": "PASS", "version": VERSION, "source": remote_raw_url("package.json", ref)}

    def fake_remote_helper_facts(
        args: argparse.Namespace,
        required: bool = True,
        remote_commit: str | None = None,
    ) -> dict[str, Any]:
        observed_refs["helper_ref"] = remote_commit
        return {"status": "SKIP", "helpers": {}, "source": "test"}

    try:
        globals()["fetch_remote_version"] = fake_fetch_remote_version
        globals()["remote_helper_facts"] = fake_remote_helper_facts
        commit = "f" * 40
        remote_facts(
            argparse.Namespace(
                remote_version=None,
                remote_commit=commit,
                remote_helper_manifest=None,
                local_package_helpers=False,
                offline=False,
                timeout=0.1,
            )
        )
        if observed_refs.get("version_ref") != commit:
            failures.append("remote version lookup must use commit-pinned raw source")
        if observed_refs.get("helper_ref") != commit:
            failures.append("remote helper lookup must use commit-pinned raw source")
    finally:
        globals()["fetch_remote_version"] = original_fetch_remote_version
        globals()["remote_helper_facts"] = original_remote_helper_facts

    return {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "self_test_mode": mode,
        "coverage": coverage,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=["plan", "status"], default="plan")
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--runtime", choices=["codex", "claude", "cursor"])
    parser.add_argument("--remote-version")
    parser.add_argument("--remote-commit")
    parser.add_argument("--remote-helper-manifest", type=Path)
    parser.add_argument("--local-package-helpers", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--json-only", action="store_true")
    parser.add_argument("--record-field-report", action="store_true")
    parser.add_argument("--no-field-report", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result = self_test() if args.self_test else analyze(args)
    if not args.self_test and args.record_field_report and not args.no_field_report:
        report = record_field_report(args.target.expanduser().resolve(), result)
        if report:
            result["field_report_status"] = report.get("status")
            result["field_report_writes"] = report.get("writes", [])
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json_only:
        print("[tes-update] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
