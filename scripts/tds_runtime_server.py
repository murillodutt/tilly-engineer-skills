#!/usr/bin/env python3
"""Serve TES docs with GitHub Pages-like routes and TDS runtime endpoints."""

from __future__ import annotations

import argparse
import json
import mimetypes
import subprocess
import sys
import tempfile
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import tds_surface_oracle  # noqa: E402


def normalize_base_path(value: str) -> str:
    if not value.startswith("/"):
        value = "/" + value
    if not value.endswith("/"):
        value += "/"
    return value


def json_response(value: object) -> bytes:
    return json.dumps(value, indent=2, sort_keys=True).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "TESTDSRuntime/0.1"

    @property
    def config(self) -> dict[str, object]:
        return self.server.config  # type: ignore[attr-defined]

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} - {fmt % args}", file=sys.stderr)

    def send_json(self, status: int, payload: object) -> None:
        body = json_response(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        request_path = unquote(urlparse(self.path).path)
        api_path = self.api_path(request_path)
        if api_path == "/health":
            self.send_json(
                200,
                {
                    "status": "PASS",
                    "target": str(self.config["target"]),
                    "docs_root": str(self.config["docs_root"]),
                    "base_path": str(self.config["base_path"]),
                    "routes": {
                        "landing": str(self.config["base_path"]),
                        "manual": str(self.config["base_path"]) + "install/USER-MANUAL.html",
                        "manifest": "/_tds/manifest",
                        "check": "/_tds/check",
                    },
                },
            )
            return
        if api_path == "/manifest":
            self.send_json(200, tds_surface_oracle.manifest(Path(str(self.config["target"]))))
            return
        if api_path == "/check":
            status, manifest, findings = tds_surface_oracle.audit(Path(str(self.config["target"])))
            self.send_json(
                200 if status == "PASS" else 409,
                {"status": status, "manifest": manifest, "findings": [finding.as_dict() for finding in findings]},
            )
            return
        self.serve_docs(request_path)

    def api_path(self, request_path: str) -> str | None:
        for prefix in ("/_tds", "/__tds__"):
            if request_path == prefix:
                return "/health"
            if request_path.startswith(prefix + "/"):
                return request_path[len(prefix):]
        return None

    def serve_docs(self, request_path: str) -> None:
        base_path = str(self.config["base_path"])
        docs_root = Path(str(self.config["docs_root"])).resolve()
        allowlist = set(self.config["allowlist"])  # type: ignore[arg-type]
        if request_path == "/":
            self.send_response(302)
            self.send_header("Location", base_path)
            self.end_headers()
            return
        if not request_path.startswith(base_path):
            self.send_error(404, "outside configured base path")
            return
        rel = request_path[len(base_path):].lstrip("/") or "index.html"
        if "//" in rel or any(part.startswith(".") for part in Path(rel).parts):
            self.send_error(403, "unsafe path blocked")
            return
        if rel not in allowlist:
            self.send_error(404, "not allowlisted")
            return
        path = (docs_root / rel).resolve()
        try:
            path.relative_to(docs_root)
        except ValueError:
            self.send_error(403, "path traversal blocked")
            return
        if path.is_dir():
            path = path / "index.html"
        if not path.exists() or not path.is_file():
            self.send_error(404, "not found")
            return
        content_type = mimetypes.guess_type(path.name)[0]
        if path.suffix == ".md":
            content_type = "text/markdown; charset=utf-8"
        elif content_type is None:
            content_type = "application/octet-stream"
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def collect_allowlist(target: Path, docs_root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "docs"],
        cwd=target,
        capture_output=True,
        check=False,
    )
    allowed: set[str] = set()
    if result.returncode == 0 and result.stdout:
        for raw in result.stdout.split(b"\0"):
            if not raw:
                continue
            repo_rel = Path(raw.decode("utf-8"))
            try:
                docs_rel = repo_rel.relative_to("docs")
            except ValueError:
                continue
            if docs_rel.parts and not any(part.startswith(".") for part in docs_rel.parts):
                allowed.add(docs_rel.as_posix())
    else:
        for path in docs_root.rglob("*"):
            if path.is_file():
                docs_rel = path.relative_to(docs_root)
                if docs_rel.parts and not any(part.startswith(".") for part in docs_rel.parts):
                    allowed.add(docs_rel.as_posix())

    try:
        for output in tds_surface_oracle.manifest(target).get("generated_outputs", []):
            try:
                allowed.add(Path(output).relative_to("docs").as_posix())
            except ValueError:
                continue
    except Exception:
        pass
    return allowed


def create_server(target: Path, docs_root: Path, base_path: str, host: str, port: int, auto_port: bool) -> ThreadingHTTPServer:
    config = {
        "target": target.resolve().as_posix(),
        "docs_root": docs_root.resolve().as_posix(),
        "base_path": normalize_base_path(base_path),
        "allowlist": sorted(collect_allowlist(target, docs_root)),
    }
    ports = range(port, port + 30) if auto_port and port else [port]
    last_error: OSError | None = None
    for candidate in ports:
        try:
            server = ThreadingHTTPServer((host, candidate), Handler)
            server.config = config  # type: ignore[attr-defined]
            return server
        except OSError as exc:
            last_error = exc
    if last_error:
        raise last_error
    raise OSError("no port available")


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        docs = root / "docs"
        (docs / "install").mkdir(parents=True)
        (docs / "index.html").write_text("<html>landing</html>\n", encoding="utf-8")
        (docs / "install/USER-MANUAL.html").write_text("<html>manual</html>\n", encoding="utf-8")
        (docs / "install/COMMAND-TRIGGERS.md").write_text("# Commands\n", encoding="utf-8")
        server = create_server(root, docs, "/tilly-engineer-skills/", "127.0.0.1", 0, False)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            host, port = server.server_address
            base = f"http://{host}:{port}"
            for route in (
                "/_tds/health",
                "/__tds__/health",
                "/tilly-engineer-skills/",
                "/tilly-engineer-skills/install/USER-MANUAL.html",
                "/tilly-engineer-skills/install/COMMAND-TRIGGERS.md",
            ):
                with urllib.request.urlopen(base + route, timeout=5) as response:
                    if response.status != 200:
                        raise AssertionError(route)
            try:
                urllib.request.urlopen(base + "/tilly-engineer-skills/../AGENTS.md", timeout=5)
            except Exception:
                pass
            else:
                raise AssertionError("path traversal was served")
        finally:
            server.shutdown()
            thread.join(timeout=5)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=ROOT.as_posix())
    parser.add_argument("--docs-root", default="docs")
    parser.add_argument("--base-path", default="/tilly-engineer-skills/")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument("--no-auto-port", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("[tds-runtime] self-test PASS")
        return 0

    target = Path(args.target).resolve()
    docs_root = (target / args.docs_root).resolve()
    server = create_server(target, docs_root, args.base_path, args.host, args.port, not args.no_auto_port)
    host, port = server.server_address
    base_path = normalize_base_path(args.base_path)
    print(f"[tds-runtime] ready http://{host}:{port}{base_path}", flush=True)
    print(f"[tds-runtime] health http://{host}:{port}/_tds/health", flush=True)
    print(f"[tds-runtime] check http://{host}:{port}/_tds/check", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[tds-runtime] stopped", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
