#!/usr/bin/env python3
"""Collect and drain sanitized Tilly operational field reports."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from typing import Any


VERSION = "0.3.20"
DESTINATION_REPO = "murillodutt/tilly-engineer-skills"
SCHEMA = "tilly-field-report@1"
FIELD_ROOT = Path(".tilly/field-reports")
OUTBOX = FIELD_ROOT / "outbox.jsonl"
RECEIPTS = FIELD_ROOT / "receipts"
DISABLED = FIELD_ROOT / "DISABLED"
INSTALL_ID = FIELD_ROOT / "install_id"
BIN_HELPER = Path(".tilly/bin/field_reports.py")
HOOK_MARKER = "TILLY_FIELD_REPORTS_PRE_PUSH"
MAX_ISSUE_BODY_CHARS = 48000

SAFE_SLUG = re.compile(r"[^a-zA-Z0-9_.:-]+")
ABSOLUTE_PATH = re.compile(r"(/Users|/home|/private|/var/folders|[A-Za-z]:\\)[^\s`\"')]+")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL = re.compile(r"https?://[^\s`\"')]+")
SECRET = re.compile(
    r"(?i)(api[_-]?key|authorization|bearer|credential|password|secret|token)\s*[:=]?\s*[A-Za-z0-9._:/+=-]+"
)
STACK_TRACE = re.compile(r"(?i)(traceback \(most recent call last\)|\bat .+:\d+:\d+|exception: .+)")
CODE_FENCE = re.compile(r"```")
GIT_REMOTE = re.compile(r"(?i)(github\.com[:/][^\s]+\.git|git@[^:\s]+:[^\s]+)")
BRANCH_NAME = re.compile(r"(?i)\b(branch|ref)\s*[:=]\s*[^\s]+")
PROHIBITED_KEY = re.compile(r"(?i)(api|auth|branch|code|content|diff|email|file|path|prompt|remote|secret|stack|token|url)")


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def file_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def root(target: Path) -> Path:
    return target / FIELD_ROOT


def outbox_path(target: Path) -> Path:
    return target / OUTBOX


def receipts_path(target: Path) -> Path:
    return target / RECEIPTS


def disabled_path(target: Path) -> Path:
    return target / DISABLED


def install_id_path(target: Path) -> Path:
    return target / INSTALL_ID


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return path.name


def safe_slug(value: str, default: str) -> str:
    slug = SAFE_SLUG.sub("-", value.strip()).strip("-._:")
    return slug[:64] if slug else default


def status_slug(value: str) -> str:
    return safe_slug(value.upper(), "UNKNOWN")


def field_reports_disabled(target: Path) -> bool:
    return disabled_path(target).exists()


def ensure_layout(target: Path) -> None:
    root(target).mkdir(parents=True, exist_ok=True)
    receipts_path(target).mkdir(parents=True, exist_ok=True)
    outbox_path(target).touch(exist_ok=True)


def ensure_install_id(target: Path) -> str:
    ensure_layout(target)
    path = install_id_path(target)
    if path.exists():
        value = path.read_text(encoding="utf-8").strip()
        if value:
            return safe_slug(value, "unknown-install")
    value = str(uuid.uuid4())
    path.write_text(value + "\n", encoding="utf-8")
    return value


def redaction_label(text: str) -> str:
    return f"redacted:{sha256_text(text)[:12]}"


def sanitize_key(key: str) -> str:
    raw = str(key).strip()
    if PROHIBITED_KEY.search(raw):
        return f"field_{sha256_text(raw)[:8]}"
    return safe_slug(raw.lower(), "field")


def sanitize_value(value: object) -> str:
    raw = str(value)
    if not raw:
        return ""
    if "\n" in raw or CODE_FENCE.search(raw) or STACK_TRACE.search(raw):
        return redaction_label(raw)
    sanitized = raw
    for pattern in (SECRET, EMAIL, URL, ABSOLUTE_PATH, GIT_REMOTE, BRANCH_NAME):
        sanitized = pattern.sub("[redacted]", sanitized)
    sanitized = sanitized.replace("`", "'").replace("|", "/").strip()
    if len(sanitized) > 160:
        return redaction_label(sanitized)
    if not sanitized:
        return "[redacted]"
    return sanitized


def parse_detail(items: list[str]) -> dict[str, str]:
    details: dict[str, str] = {}
    for item in items:
        key, sep, value = item.partition("=")
        if not sep:
            key, value = "note", item
        details[sanitize_key(key)] = sanitize_value(value)
    return details


def system_facts() -> dict[str, str]:
    return {
        "os": sanitize_value(platform.system() or "unknown"),
        "python": sanitize_value(platform.python_version()),
        "runtime": "python",
    }


def build_event(
    target: Path,
    event: str,
    status: str,
    surface: str = "unknown",
    trigger: str = "cli",
    duration_bucket: str | None = None,
    details: dict[str, object] | None = None,
) -> dict[str, object]:
    safe_details = {
        sanitize_key(key): sanitize_value(value)
        for key, value in (details or {}).items()
    }
    if duration_bucket:
        safe_details["duration_bucket"] = sanitize_value(duration_bucket)
    return {
        "schema": SCHEMA,
        "tilly_version": VERSION,
        "created_at": utc_stamp(),
        "install_id": ensure_install_id(target),
        "event": safe_slug(event, "unknown-event"),
        "status": status_slug(status),
        "surface": safe_slug(surface, "unknown"),
        "trigger": safe_slug(trigger, "cli"),
        "facts": {**system_facts(), **safe_details},
    }


def append_event(target: Path, event: dict[str, object]) -> None:
    ensure_layout(target)
    with outbox_path(target).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")


def record_event(
    target: Path,
    event: str,
    status: str,
    surface: str = "unknown",
    trigger: str = "cli",
    duration_bucket: str | None = None,
    details: dict[str, object] | None = None,
) -> dict[str, object]:
    target = target.expanduser().resolve()
    if field_reports_disabled(target):
        return {"version": VERSION, "status": "SKIP", "reason": "field reports disabled", "writes": []}
    payload = build_event(target, event, status, surface, trigger, duration_bucket, details)
    append_event(target, payload)
    ensure_git_exclude(target)
    return {
        "version": VERSION,
        "status": "PASS",
        "event": payload["event"],
        "outbox": rel(outbox_path(target), target),
        "writes": [rel(outbox_path(target), target)],
    }


def safe_record_event(
    target: Path,
    event: str,
    status: str,
    surface: str = "unknown",
    trigger: str = "cli",
    duration_bucket: str | None = None,
    details: dict[str, object] | None = None,
) -> None:
    try:
        record_event(target, event, status, surface, trigger, duration_bucket, details)
    except Exception:
        return


def read_outbox(target: Path) -> tuple[list[dict[str, object]], list[str]]:
    path = outbox_path(target)
    if not path.exists():
        return [], []
    events: list[dict[str, object]] = []
    failures: list[str] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            failures.append(f"invalid outbox json line: {idx}")
            continue
        if isinstance(item, dict):
            events.append(item)
        else:
            failures.append(f"invalid outbox payload line: {idx}")
    return events, failures


def sanitize_issue_text(text: str) -> str:
    sanitized = text
    for pattern in (SECRET, EMAIL, URL, ABSOLUTE_PATH, GIT_REMOTE, BRANCH_NAME, STACK_TRACE):
        sanitized = pattern.sub("[redacted]", sanitized)
    sanitized = sanitized.replace("```", "'''").replace("|", "/")
    return sanitized


def sanitize_issue_url(value: str) -> str:
    cleaned = value.strip().splitlines()[-1] if value.strip() else ""
    prefix = f"https://github.com/{DESTINATION_REPO}/issues/"
    if cleaned.startswith(prefix):
        suffix = cleaned.removeprefix(prefix)
        if suffix.isdigit():
            return cleaned
    return sanitize_value(cleaned)


def build_issue_body(events: list[dict[str, object]], chunk_index: int, chunk_count: int) -> str:
    statuses: dict[str, int] = {}
    surfaces: dict[str, int] = {}
    for event in events:
        statuses[str(event.get("status", "UNKNOWN"))] = statuses.get(str(event.get("status", "UNKNOWN")), 0) + 1
        surfaces[str(event.get("surface", "unknown"))] = surfaces.get(str(event.get("surface", "unknown")), 0) + 1
    lines = [
        f"<!-- {SCHEMA} -->",
        "Tilly Field Report",
        "",
        f"- Schema: {SCHEMA}",
        f"- Tilly version: {VERSION}",
        f"- Destination: {DESTINATION_REPO}",
        f"- Sent at: {utc_stamp()}",
        f"- Chunk: {chunk_index} of {chunk_count}",
        f"- Event count: {len(events)}",
        "- Status counts: " + ", ".join(f"{key}={value}" for key, value in sorted(statuses.items())),
        "- Surface counts: " + ", ".join(f"{key}={value}" for key, value in sorted(surfaces.items())),
        "",
        "Events",
    ]
    for event in events:
        facts = event.get("facts") if isinstance(event.get("facts"), dict) else {}
        fact_bits = ", ".join(
            f"{sanitize_key(str(key))}={sanitize_value(value)}"
            for key, value in sorted(facts.items())
        )
        lines.append(
            "- "
            + f"time={sanitize_value(event.get('created_at', 'unknown'))}, "
            + f"install={sanitize_value(event.get('install_id', 'unknown'))}, "
            + f"event={sanitize_value(event.get('event', 'unknown'))}, "
            + f"status={sanitize_value(event.get('status', 'UNKNOWN'))}, "
            + f"surface={sanitize_value(event.get('surface', 'unknown'))}, "
            + f"trigger={sanitize_value(event.get('trigger', 'cli'))}, "
            + f"facts={fact_bits}"
        )
    return sanitize_issue_text("\n".join(lines).strip() + "\n")


def chunk_events(events: list[dict[str, object]]) -> list[list[dict[str, object]]]:
    chunks: list[list[dict[str, object]]] = []
    current: list[dict[str, object]] = []
    for event in events:
        trial = [*current, event]
        body = build_issue_body(trial, len(chunks) + 1, 1)
        if current and len(body) > MAX_ISSUE_BODY_CHARS:
            chunks.append(current)
            current = [event]
        else:
            current = trial
    if current:
        chunks.append(current)
    return chunks


def gh_issue_create(title: str, body: str, env: dict[str, str] | None = None) -> tuple[bool, str]:
    gh = shutil.which("gh", path=(env or os.environ).get("PATH"))
    if not gh:
        return False, "gh unavailable"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        handle.write(body)
        body_file = handle.name
    try:
        result = subprocess.run(
            ["gh", "issue", "create", "--repo", DESTINATION_REPO, "--title", title, "--body-file", body_file],
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )
    finally:
        Path(body_file).unlink(missing_ok=True)
    if result.returncode != 0:
        return False, "gh issue create failed"
    output = result.stdout.strip() or result.stderr.strip()
    return True, sanitize_issue_url(output)


def write_receipt(target: Path, issue_url: str, events: list[dict[str, object]], body: str, chunk: int) -> str:
    receipts_path(target).mkdir(parents=True, exist_ok=True)
    payload = {
        "issue_url": sanitize_issue_url(issue_url),
        "event_count": len(events),
        "payload_sha256": sha256_text(body),
        "sent_at": utc_stamp(),
    }
    path = receipts_path(target) / f"{file_stamp()}-{chunk:02d}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return rel(path, target)


def drain(target: Path, trigger: str = "manual", env: dict[str, str] | None = None) -> dict[str, object]:
    target = target.expanduser().resolve()
    if field_reports_disabled(target):
        return {"version": VERSION, "status": "SKIP", "reason": "field reports disabled", "writes": []}

    ensure_layout(target)
    events, failures = read_outbox(target)
    if events:
        append_event(
            target,
            build_event(
                target,
                "field_reports.drain",
                "PASS",
                "field-reports",
                trigger,
                details={"pending_before": len(events)},
            ),
        )
        events, more_failures = read_outbox(target)
        failures.extend(more_failures)
    if failures:
        return {"version": VERSION, "status": "BLOCKED", "reason": "outbox contains invalid records", "failures": failures, "writes": []}
    if not events:
        return {"version": VERSION, "status": "PASS", "pending": 0, "writes": []}

    chunks = chunk_events(events)
    issue_urls: list[str] = []
    receipt_paths: list[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        body = build_issue_body(chunk, idx, len(chunks))
        title = f"Tilly Field Report {datetime.now(timezone.utc).strftime('%Y-%m-%d')} ({idx}/{len(chunks)})"
        ok, value = gh_issue_create(title, body, env=env)
        if not ok:
            return {
                "version": VERSION,
                "status": "BLOCKED",
                "reason": value,
                "pending": len(events),
                "writes": [],
            }
        issue_urls.append(value)
        receipt_paths.append(write_receipt(target, value, chunk, body, idx))

    outbox_path(target).write_text("", encoding="utf-8")
    return {
        "version": VERSION,
        "status": "PASS",
        "pending": 0,
        "issues": issue_urls,
        "receipts": receipt_paths,
        "writes": [rel(outbox_path(target), target), *receipt_paths],
    }


def ensure_git_exclude(target: Path) -> str | None:
    info = target / ".git/info"
    if not info.exists():
        return None
    exclude = info / "exclude"
    exclude.touch(exist_ok=True)
    text = exclude.read_text(encoding="utf-8")
    line = ".tilly/field-reports/"
    if line not in text.splitlines():
        exclude.write_text(text.rstrip() + ("\n" if text.strip() else "") + line + "\n", encoding="utf-8")
    return rel(exclude, target)


def copy_helper(target: Path) -> str:
    destination = target / BIN_HELPER
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__).resolve(), destination)
    return rel(destination, target)


def install_hook(target: Path) -> dict[str, object]:
    target = target.expanduser().resolve()
    git_dir = target / ".git"
    if not git_dir.exists() or not git_dir.is_dir():
        return {"version": VERSION, "status": "BLOCKED", "reason": "target is not a Git repository", "writes": []}

    ensure_layout(target)
    install_id = ensure_install_id(target)
    helper = copy_helper(target)
    exclude = ensure_git_exclude(target)
    hooks = git_dir / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "pre-push"
    backup_rel: str | None = None
    backup_shell = ""
    if hook.exists():
        current = hook.read_text(encoding="utf-8", errors="replace")
        if HOOK_MARKER not in current:
            backup = hook.with_name(f"pre-push.before-tilly-{file_stamp()}")
            shutil.copy2(hook, backup)
            backup.chmod(0o755)
            backup_rel = rel(backup, target)
            backup_shell = f"""
BACKUP_HOOK=".git/hooks/{backup.name}"
if [ -f "$BACKUP_HOOK" ]; then
  if [ -x "$BACKUP_HOOK" ]; then
    "$BACKUP_HOOK" "$@"
  else
    sh "$BACKUP_HOOK" "$@"
  fi
  rc=$?
  if [ "$rc" -ne 0 ]; then
    exit "$rc"
  fi
fi
"""

    hook_text = f"""#!/bin/sh
# {HOOK_MARKER}
set -u
{backup_shell}
if [ -f ".tilly/bin/field_reports.py" ]; then
  python3 ".tilly/bin/field_reports.py" drain --target . --trigger pre-push >/dev/null 2>&1 || true
elif [ -f "scripts/field_reports.py" ]; then
  python3 "scripts/field_reports.py" drain --target . --trigger pre-push >/dev/null 2>&1 || true
fi
exit 0
"""
    hook.write_text(hook_text, encoding="utf-8")
    hook.chmod(0o755)

    writes = [helper, rel(hook, target), rel(outbox_path(target), target), rel(install_id_path(target), target)]
    if exclude:
        writes.append(exclude)
    if backup_rel:
        writes.append(backup_rel)
    return {
        "version": VERSION,
        "status": "PASS",
        "install_id": install_id,
        "hook": rel(hook, target),
        "backup": backup_rel,
        "writes": writes,
    }


def status(target: Path) -> dict[str, object]:
    target = target.expanduser().resolve()
    events, failures = read_outbox(target)
    receipts = sorted(receipts_path(target).glob("*.json")) if receipts_path(target).exists() else []
    last_receipt = rel(receipts[-1], target) if receipts else None
    return {
        "version": VERSION,
        "status": "PASS" if not failures else "BLOCKED",
        "disabled": field_reports_disabled(target),
        "pending": len(events),
        "last_receipt": last_receipt,
        "outbox": rel(outbox_path(target), target),
        "failures": failures,
        "writes": [],
    }


def disable(target: Path) -> dict[str, object]:
    target = target.expanduser().resolve()
    ensure_layout(target)
    disabled_path(target).write_text("Tilly Field Reports disabled by local user intent.\n", encoding="utf-8")
    ensure_git_exclude(target)
    return {"version": VERSION, "status": "PASS", "disabled": True, "writes": [rel(disabled_path(target), target)]}


def enable(target: Path) -> dict[str, object]:
    target = target.expanduser().resolve()
    disabled_path(target).unlink(missing_ok=True)
    ensure_layout(target)
    ensure_install_id(target)
    ensure_git_exclude(target)
    return {"version": VERSION, "status": "PASS", "disabled": False, "writes": [rel(outbox_path(target), target)]}


def self_test() -> dict[str, object]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tilly-field-reports-") as tempdir:
        target = Path(tempdir)
        subprocess.run(["git", "init"], cwd=target, text=True, capture_output=True, check=False)

        hook_result = install_hook(target)
        for relpath in (".tilly/bin/field_reports.py", ".tilly/field-reports/outbox.jsonl", ".git/hooks/pre-push"):
            if not (target / relpath).exists():
                failures.append(f"missing installed path: {relpath}")
        if hook_result["status"] != "PASS":
            failures.append("install-hook did not pass in a Git fixture")

        record_event(
            target,
            "install_adapter",
            "FAIL",
            "adapter",
            "self-test",
            details={
                "unsafe_path": "/Users/private/project/secret.py",
                "unsafe_email": "person@example.com",
                "unsafe_token": "token=abc123",
                "unsafe_url": "https://private.example.test/repo",
                "unsafe_stack": "Traceback (most recent call last):\nFile x",
                "returncode": 1,
            },
        )
        events, event_failures = read_outbox(target)
        failures.extend(event_failures)
        if len(events) != 1:
            failures.append("capture must append exactly one event before drain")

        disabled = disable(target)
        skipped = record_event(target, "cortex.verify", "PASS", "cortex", "self-test")
        skipped_drain = drain(target, "self-test")
        if disabled["status"] != "PASS" or skipped["status"] != "SKIP" or skipped_drain["status"] != "SKIP":
            failures.append("disable must stop collection and drain")
        enabled = enable(target)
        if enabled["status"] != "PASS" or field_reports_disabled(target):
            failures.append("enable must remove the disabled sentinel")

        fake_bin = target / "fake-bin"
        fake_bin.mkdir()
        body_capture = target / "issue-body.txt"
        fake_gh = fake_bin / "gh"
        fake_gh.write_text(
            """#!/bin/sh
body=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "--body-file" ]; then
    shift
    body="$1"
  fi
  shift
done
cp "$body" "$GH_BODY_CAPTURE"
echo "https://github.com/murillodutt/tilly-engineer-skills/issues/999"
""",
            encoding="utf-8",
        )
        fake_gh.chmod(0o755)
        env = {**os.environ, "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}", "GH_BODY_CAPTURE": str(body_capture)}
        hook_run = subprocess.run(
            [str(target / ".git/hooks/pre-push")],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )
        if hook_run.returncode != 0:
            failures.append(f"pre-push hook must not fail: {hook_run.returncode}")
        if outbox_path(target).read_text(encoding="utf-8").strip():
            failures.append("pre-push drain must clear outbox after confirmed issue")
        if not list(receipts_path(target).glob("*.json")):
            failures.append("drain must write a receipt")
        else:
            receipt = json.loads(sorted(receipts_path(target).glob("*.json"))[-1].read_text(encoding="utf-8"))
            if not str(receipt.get("issue_url", "")).endswith("/issues/999"):
                failures.append("receipt must preserve the confirmed issue URL")
        body = body_capture.read_text(encoding="utf-8") if body_capture.exists() else ""
        if f"<!-- {SCHEMA} -->" not in body:
            failures.append("issue body must carry the field report schema marker")
        if f"- Schema: {SCHEMA}" not in body:
            failures.append("issue body must carry the visible field report schema")
        for forbidden in ("```", "|", "/Users", "person@example.com", "abc123", "https://private", "Traceback"):
            if forbidden in body:
                failures.append(f"issue body leaked prohibited token: {forbidden}")

        record_event(target, "cortex.audit", "FAIL", "cortex", "self-test", details={"returncode": 2})
        python_only = target / "python-only-bin"
        python_only.mkdir()
        (python_only / "python3").symlink_to(sys.executable)
        missing_env = {**os.environ, "PATH": str(python_only)}
        hook_missing = subprocess.run(
            [str(target / ".git/hooks/pre-push")],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
            env=missing_env,
        )
        if hook_missing.returncode != 0:
            failures.append("missing gh pre-push hook must not block")
        missing_gh = drain(target, "self-test", env=missing_env)
        if missing_gh["status"] != "BLOCKED":
            failures.append("missing gh must return BLOCKED")
        if not outbox_path(target).read_text(encoding="utf-8").strip():
            failures.append("missing gh must keep outbox pending")

    return {"version": VERSION, "status": "PASS" if not failures else "FAIL", "failures": failures}


def print_result(result: dict[str, object], label: str) -> int:
    print(json.dumps(result, indent=2, sort_keys=True))
    status_value = str(result.get("status", "FAIL"))
    print(f"[field-reports] {status_value}")
    if status_value == "FAIL":
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=("capture", "drain", "status", "disable", "enable", "install-hook"))
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--event")
    parser.add_argument("--status")
    parser.add_argument("--surface", default="unknown")
    parser.add_argument("--trigger", default="cli")
    parser.add_argument("--duration-bucket")
    parser.add_argument("--detail", action="append", default=[])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return print_result(self_test(), "self-test")
    if args.command == "capture":
        if not args.event or not args.status:
            parser.error("capture requires --event and --status")
        result = record_event(
            args.target,
            args.event,
            args.status,
            args.surface,
            args.trigger,
            args.duration_bucket,
            parse_detail(args.detail),
        )
    elif args.command == "drain":
        result = drain(args.target, args.trigger)
    elif args.command == "status":
        result = status(args.target)
    elif args.command == "disable":
        result = disable(args.target)
    elif args.command == "enable":
        result = enable(args.target)
    elif args.command == "install-hook":
        result = install_hook(args.target)
    else:
        parser.error("command is required unless --self-test is used")
    return print_result(result, str(args.command))


if __name__ == "__main__":
    sys.exit(main())
