#!/usr/bin/env python3
"""Validate the live GitHub Pages installer surface for the current TES release."""

from __future__ import annotations

import argparse
import contextlib
import http.server
import json
import socketserver
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

import tes_bundle


ROOT = Path(__file__).resolve().parents[1]
VERSION = tes_bundle.VERSION
DEFAULT_BASE_URL = "https://murillodutt.github.io/tilly-engineer-skills/"


def normalize_base_url(value: str) -> str:
    return value.rstrip("/") + "/"


def fetch_text(url: str, timeout: float) -> tuple[str | None, str | None]:
    try:
        with urlopen(url, timeout=timeout) as response:  # noqa: S310 - controlled release oracle URL.
            return response.read().decode("utf-8", errors="replace"), None
    except (OSError, URLError) as exc:
        return None, str(exc)


def certify_pages_once(base_url: str, version: str, timeout: float = 20.0) -> dict[str, Any]:
    base_url = normalize_base_url(base_url)
    failures: list[str] = []
    observations: dict[str, Any] = {}
    endpoints = {
        "home": base_url,
        "manual": base_url + "install/USER-MANUAL.html",
        "bundle_index": base_url + f"dist/{version}/index.json",
    }

    for name, url in endpoints.items():
        body, error = fetch_text(url, timeout)
        if error:
            failures.append(f"{name} fetch failed: {error}")
            observations[name] = {"url": url, "status": "FETCH_FAIL"}
            continue
        assert body is not None
        observations[name] = {"url": url, "status": "FETCHED", "bytes": len(body)}
        if name in {"home", "manual"} and version not in body:
            failures.append(f"{name} page does not mention {version}")
        if name == "bundle_index":
            try:
                data = json.loads(body)
            except json.JSONDecodeError as exc:
                failures.append(f"bundle index JSON invalid: {exc}")
                data = {}
            observations[name]["json"] = data
            if data.get("version") != version:
                failures.append(f"bundle index version must be {version}")
            local_index_path = ROOT / f"docs/dist/{version}/index.json"
            if local_index_path.exists():
                local_index = json.loads(local_index_path.read_text(encoding="utf-8"))
                for key in ("bundle", "sha256"):
                    if data.get(key) != local_index.get(key):
                        failures.append(f"bundle index {key} does not match local public dist")

    return {
        "version": version,
        "base_url": base_url,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "observations": observations,
    }


def certify_pages(base_url: str, version: str, retries: int, interval: float, timeout: float) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    for attempt in range(1, retries + 1):
        result = certify_pages_once(base_url, version, timeout=timeout)
        result["attempt"] = attempt
        attempts.append(dict(result))
        if result["status"] == "PASS":
            return {**result, "attempts": attempts}
        if attempt < retries:
            time.sleep(interval)
    return {**attempts[-1], "attempts": attempts}


@contextlib.contextmanager
def fixture_server(root: Path):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            return

    with socketserver.TCPServer(("127.0.0.1", 0), Handler) as server:
        port = server.server_address[1]
        thread = threading.Thread(
            target=server.serve_forever,
            kwargs={"poll_interval": 0.05},
            daemon=True,
        )
        old_cwd = Path.cwd()
        try:
            import os

            os.chdir(root)
            thread.start()
            yield f"http://127.0.0.1:{port}/"
        finally:
            server.shutdown()
            thread.join(timeout=5)
            os.chdir(old_cwd)


def write_fixture(root: Path, version: str, stale_version: str | None = None) -> None:
    live_version = stale_version or version
    (root / "install").mkdir(parents=True)
    (root / f"dist/{version}").mkdir(parents=True)
    (root / "index.html").write_text(f"<html>Tilly {live_version}</html>\n", encoding="utf-8")
    (root / "install/USER-MANUAL.html").write_text(f"<html>Manual {live_version}</html>\n", encoding="utf-8")
    local_index = ROOT / f"docs/dist/{version}/index.json"
    if local_index.exists():
        data = json.loads(local_index.read_text(encoding="utf-8"))
    else:
        data = {"version": version, "bundle": f"tilly-engineer-skills-{version}.zip", "sha256": "fixture"}
    data["version"] = live_version
    (root / f"dist/{version}/index.json").write_text(json.dumps(data), encoding="utf-8")


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="tes-public-pages-oracle-") as tempdir:
        fixture = Path(tempdir) / "pass"
        fixture.mkdir()
        write_fixture(fixture, VERSION)
        with fixture_server(fixture) as base_url:
            passing = certify_pages(base_url, VERSION, retries=1, interval=0, timeout=5)
        json.dumps(passing, sort_keys=True)
        if passing["status"] != "PASS":
            print(json.dumps(passing, indent=2, sort_keys=True))
            return 1

        stale = Path(tempdir) / "stale"
        stale.mkdir()
        write_fixture(stale, VERSION, stale_version="0.0.0")
        with fixture_server(stale) as base_url:
            failing = certify_pages(base_url, VERSION, retries=1, interval=0, timeout=5)
        json.dumps(failing, sort_keys=True)
        if failing["status"] != "FAIL" or not failing["failures"]:
            print(json.dumps(failing, indent=2, sort_keys=True))
            return 1
    print("[public-pages] PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate live TES GitHub Pages release surface.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--version", default=VERSION)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--interval", type=float, default=10.0)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    result = certify_pages(args.base_url, args.version, args.retries, args.interval, args.timeout)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
