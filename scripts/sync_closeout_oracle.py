#!/usr/bin/env python3
"""Certify that a TES bundle sync was fully closed after push.

This maintainer-only oracle exists because a branch push is not a release
closeout for bundle-scope syncs. A complete closeout must prove the pushed HEAD,
the release tag, the GitHub package release check, and GitHub Pages all agree on
the current TES version.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import public_pages_oracle
import tes_bundle


ROOT = Path(__file__).resolve().parents[1]
VERSION = tes_bundle.VERSION
HEX40_RE = re.compile(r"^[a-fA-F0-9]{40}$")
JSON_START_RE = re.compile(r"^\s*\{", re.MULTILINE)


def run(command: list[str], timeout: float = 600.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, timeout=timeout)


def git_output(command: list[str]) -> tuple[str, list[str]]:
    result = run(["git", *command], timeout=60.0)
    if result.returncode != 0:
        return "", [line for line in (result.stderr or result.stdout).splitlines() if line.strip()]
    return result.stdout.strip(), []


def first_json_object(text: str) -> tuple[dict[str, Any], list[str]]:
    match = JSON_START_RE.search(text)
    if not match:
        return {}, ["no JSON object found in command output"]
    decoder = json.JSONDecoder()
    try:
        value, _ = decoder.raw_decode(text[match.start():])
    except json.JSONDecodeError as exc:
        return {}, [f"could not parse JSON object: {exc}"]
    if not isinstance(value, dict):
        return {}, ["first JSON value is not an object"]
    return value, []


def package_version() -> tuple[str, list[str]]:
    try:
        data = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return "", [f"could not read package.json version: {exc}"]
    version = str(data.get("version") or "")
    return version, [] if version else ["package.json version is missing"]


def local_tag_commit(tag: str) -> tuple[str, list[str]]:
    return git_output(["rev-list", "-n", "1", tag])


def remote_tag_commit(tag: str, remote: str) -> tuple[str, list[str]]:
    output, errors = git_output(["ls-remote", "--tags", remote, f"{tag}*"])
    if errors:
        return "", errors
    commit = ""
    for line in output.splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        sha, ref = parts
        if ref == f"refs/tags/{tag}^{{}}":
            commit = sha
            break
        if ref == f"refs/tags/{tag}" and not commit:
            commit = sha
    if not commit:
        return "", [f"remote tag {tag} is missing on {remote}"]
    return commit, []


def release_check(tag: str) -> tuple[dict[str, Any], list[str]]:
    result = run([sys.executable, "scripts/tes_npx_oracle.py", "--release-check", "--github-ref", tag])
    payload, parse_errors = first_json_object(result.stdout)
    failures = list(parse_errors)
    if result.returncode != 0:
        failures.append(f"release:check command exited {result.returncode}")
    if result.stderr.strip():
        failures.extend(result.stderr.splitlines())
    return payload, failures


def pages_check(version: str, retries: int, interval: float) -> tuple[dict[str, Any], list[str]]:
    result = public_pages_oracle.certify_pages(
        public_pages_oracle.DEFAULT_BASE_URL,
        version,
        retries=retries,
        interval=interval,
        timeout=20.0,
    )
    failures = [str(item) for item in result.get("failures", []) if item]
    return result, failures


def evaluate_signals(
    *,
    version: str,
    package_version_value: str,
    head: str,
    origin_main: str,
    local_tag: str,
    remote_tag: str,
    release: dict[str, Any],
    pages: dict[str, Any],
    require_pages: bool,
) -> dict[str, Any]:
    blockers: list[str] = []

    if package_version_value != version:
        blockers.append(f"package.json version {package_version_value or 'missing'} != {version}")
    for label, value in (
        ("HEAD", head),
        ("origin/main", origin_main),
        ("local tag", local_tag),
        ("remote tag", remote_tag),
    ):
        if not HEX40_RE.match(value or ""):
            blockers.append(f"{label} commit is missing or invalid")
    if head and origin_main and head != origin_main:
        blockers.append(f"origin/main ({origin_main}) must equal HEAD ({head})")
    if head and local_tag and local_tag != head:
        blockers.append(f"local tag must point to HEAD ({head}), got {local_tag}")
    if head and remote_tag and remote_tag != head:
        blockers.append(f"remote tag must point to HEAD ({head}), got {remote_tag}")

    if str(release.get("status") or "") != "PASS":
        blockers.append("release:check status must be PASS")
    if str(release.get("classification") or "") != "certified_local":
        blockers.append("release:check classification must be certified_local")
    if head and str(release.get("resolved_commit") or "") != head:
        blockers.append(
            f"release:check resolved_commit must equal HEAD ({head}), got {release.get('resolved_commit') or 'missing'}"
        )

    if require_pages:
        if str(pages.get("status") or "") != "PASS":
            blockers.append("public_pages_oracle status must be PASS")
        observations = pages.get("observations") if isinstance(pages.get("observations"), dict) else {}
        bundle_index = observations.get("bundle_index") if isinstance(observations.get("bundle_index"), dict) else {}
        live_index = bundle_index.get("json") if isinstance(bundle_index.get("json"), dict) else {}
        if str(live_index.get("version") or "") != version:
            blockers.append(f"live public bundle index must report version {version}")

    return {
        "version": version,
        "status": "PASS" if not blockers else "BLOCKED",
        "blockers": blockers,
        "signals": {
            "package_version": package_version_value,
            "head": head,
            "origin_main": origin_main,
            "local_tag": local_tag,
            "remote_tag": remote_tag,
            "release_status": release.get("status"),
            "release_classification": release.get("classification"),
            "release_resolved_commit": release.get("resolved_commit"),
            "pages_status": pages.get("status") if require_pages else "SKIP",
        },
    }


def certify(version: str, tag: str, remote: str, retries: int, interval: float, require_pages: bool) -> dict[str, Any]:
    failures: list[str] = []
    package_value, package_errors = package_version()
    failures.extend(package_errors)
    head, head_errors = git_output(["rev-parse", "HEAD"])
    failures.extend(head_errors)
    origin_main, origin_errors = git_output(["rev-parse", f"{remote}/main"])
    failures.extend(origin_errors)
    local, local_errors = local_tag_commit(tag)
    failures.extend(local_errors)
    remote_commit, remote_errors = remote_tag_commit(tag, remote)
    failures.extend(remote_errors)
    release, release_errors = release_check(tag)
    failures.extend(release_errors)
    pages: dict[str, Any] = {"status": "SKIP"}
    if require_pages:
        pages, pages_errors = pages_check(version, retries=retries, interval=interval)
        failures.extend(pages_errors)

    result = evaluate_signals(
        version=version,
        package_version_value=package_value,
        head=head,
        origin_main=origin_main,
        local_tag=local,
        remote_tag=remote_commit,
        release=release,
        pages=pages,
        require_pages=require_pages,
    )
    result["failures"] = failures
    if failures and result["status"] == "PASS":
        result["status"] = "BLOCKED"
    return result


def self_test() -> int:
    head = "a" * 40
    good_release = {"status": "PASS", "classification": "certified_local", "resolved_commit": head}
    good_pages = {
        "status": "PASS",
        "observations": {"bundle_index": {"json": {"version": "0.3.255"}}},
    }
    cases = (
        (
            "pass",
            dict(
                version="0.3.255",
                package_version_value="0.3.255",
                head=head,
                origin_main=head,
                local_tag=head,
                remote_tag=head,
                release=good_release,
                pages=good_pages,
                require_pages=True,
            ),
            "PASS",
        ),
        (
            "missing-tag",
            dict(
                version="0.3.255",
                package_version_value="0.3.255",
                head=head,
                origin_main=head,
                local_tag="",
                remote_tag=head,
                release=good_release,
                pages=good_pages,
                require_pages=True,
            ),
            "BLOCKED",
        ),
        (
            "unpushed-main",
            dict(
                version="0.3.255",
                package_version_value="0.3.255",
                head=head,
                origin_main="b" * 40,
                local_tag=head,
                remote_tag=head,
                release=good_release,
                pages=good_pages,
                require_pages=True,
            ),
            "BLOCKED",
        ),
        (
            "release-not-certified",
            dict(
                version="0.3.255",
                package_version_value="0.3.255",
                head=head,
                origin_main=head,
                local_tag=head,
                remote_tag=head,
                release={"status": "PASS", "classification": "draft", "resolved_commit": head},
                pages=good_pages,
                require_pages=True,
            ),
            "BLOCKED",
        ),
        (
            "pages-stale",
            dict(
                version="0.3.255",
                package_version_value="0.3.255",
                head=head,
                origin_main=head,
                local_tag=head,
                remote_tag=head,
                release=good_release,
                pages={"status": "FAIL", "observations": {"bundle_index": {"json": {"version": "0.3.254"}}}},
                require_pages=True,
            ),
            "BLOCKED",
        ),
    )
    failures: list[str] = []
    for name, kwargs, expected in cases:
        result = evaluate_signals(**kwargs)
        if result["status"] != expected:
            failures.append(f"{name}: expected {expected}, got {result['status']}")
    malformed, malformed_errors = first_json_object("noise\n{\"status\":\"PASS\"}\n[done]")
    if malformed_errors or malformed.get("status") != "PASS":
        failures.append("first_json_object must parse JSON after command noise")
    result = {"version": VERSION, "status": "PASS" if not failures else "FAIL", "failures": failures}
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[sync-closeout] " + result["status"])
    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Certify TES bundle sync closeout after push/tag.")
    parser.add_argument("--version", default=VERSION)
    parser.add_argument("--tag", default=None)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--retries", type=int, default=12)
    parser.add_argument("--interval", type=float, default=10.0)
    parser.add_argument("--skip-pages", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    tag = args.tag or f"v{args.version}"
    result = certify(
        version=args.version,
        tag=tag,
        remote=args.remote,
        retries=args.retries,
        interval=args.interval,
        require_pages=not args.skip_pages,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json_only:
        print("[sync-closeout] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
