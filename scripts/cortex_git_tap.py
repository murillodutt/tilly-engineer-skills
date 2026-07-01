#!/usr/bin/env python3
"""Cortex Git Tap runtime for privacy-safe Git observation events.

The tap is an observation funnel only: it writes local runtime JSONL under
`.tes/runtime/cortex/git-tap/**`, may create reviewable local proposals, and
never writes curated Cortex memory under `docs/**` from a Git hook.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

import tes_codex_policy


VERSION = "0.3.249"
SCHEMA = "tes-cortex-git-tap@1"
RUNTIME_ROOT = Path(".tes/runtime/cortex/git-tap")
EVENTS_FILE = RUNTIME_ROOT / "events.jsonl"
PENDING_FILE = RUNTIME_ROOT / "pending.jsonl"
PROPOSALS_FILE = RUNTIME_ROOT / "proposals.jsonl"
AUTO_PROMOTIONS_FILE = RUNTIME_ROOT / "auto-promotions.jsonl"
LOG_FILE = RUNTIME_ROOT / "git-tap.log"
LOCK_FILE = RUNTIME_ROOT / "git-tap.lock"
PROPOSAL_SCHEMA = "tes-cortex-git-tap-proposal@1"
CURATION_PLAN_SCHEMA = "tes-cortex-git-tap-curate-plan@1"
GIT_EXCLUDE_PATTERNS = (
    ".tes/runtime/cortex/git-tap/",
    ".tes/runtime/cortex/git-tap/events.jsonl",
    ".tes/runtime/cortex/git-tap/pending.jsonl",
    ".tes/runtime/cortex/git-tap/proposals.jsonl",
    ".tes/runtime/cortex/git-tap/auto-promotions.jsonl",
    ".tes/runtime/cortex/git-tap/git-tap.log",
    ".tes/runtime/cortex/git-tap/git-tap.lock",
)
EVENTS = {"pre-commit", "post-commit", "post-checkout", "manual-drain"}
MEMORY_SIGNALS = {
    "none",
    "candidate",
    "contract_change",
    "runtime_learning",
    "oracle_learning",
    "docs_memory_change",
}
DECISION_STATES = {
    "NO_MEMORY_SIGNAL",
    "PROPOSE_MEMORY",
    "NEEDS_CURATION",
    "AUTO_PROMOTED",
    "PROPOSED",
    "REVIEW_REQUIRED",
    "DENIED_BY_POLICY",
    "BLOCKED_IN_HOOK",
    "BLOCKED_PRIVACY",
    "CURATED",
}
HOOKS = ("pre-commit", "post-commit", "post-checkout")
START_MARKER_PREFIX = "# >>> TES CORTEX GIT TAP BEGIN"
END_MARKER_PREFIX = "# <<< TES CORTEX GIT TAP END"
HOOK_MARKER = "TES_CORTEX_GIT_TAP"
LOCK_TIMEOUT_SECONDS = 10.0
SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|authorization|bearer|credential|password|secret|token)\s*[:=]\s*[A-Za-z0-9._:/+=-]+"
)
ABSOLUTE_PATH_RE = re.compile(r"(^|\s)(/Users|/home|/private|/var/folders|[A-Za-z]:\\)[^\s`\"')]+")
RAW_DIFF_RE = re.compile(r"(^diff --git|\n@@\s|^\+\+\+ |^--- )", re.MULTILINE)
FORBIDDEN_KEY_RE = re.compile(r"(?i)(raw_?diff|diff_?hunk|prompt|tool_?payload|file_?content|transcript|command_?output)")
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")
GIT_ENV_BLOCKLIST = {
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_DIR",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_PREFIX",
    "GIT_WORK_TREE",
}


def utc_stamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return path.name


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def isolated_git_env(overrides: dict[str, str] | None = None) -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if key not in GIT_ENV_BLOCKLIST}
    if overrides:
        env.update(overrides)
    return env


def run_git(target: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
        env=isolated_git_env(),
    )


def git_value(target: Path, *args: str) -> str:
    result = run_git(target, *args)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def is_git_work_tree(target: Path) -> bool:
    return git_value(target, "rev-parse", "--is-inside-work-tree") == "true"


def git_path(target: Path, name: str) -> Path:
    value = git_value(target, "rev-parse", "--git-path", name)
    if not value:
        return target / ".git" / name
    path = Path(value)
    return path if path.is_absolute() else target / path


def git_dir(target: Path) -> Path | None:
    value = git_value(target, "rev-parse", "--git-dir")
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else target / path


def git_config_get(target: Path, key: str) -> str | None:
    result = run_git(target, "config", "--get", key)
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def repository_fingerprint(target: Path) -> str:
    root = git_value(target, "rev-parse", "--show-toplevel") or str(target.resolve())
    git_directory = str(git_dir(target) or target / ".git")
    return sha256_text(f"{Path(root).resolve()}::{Path(git_directory).resolve()}")[:24]


def git_in_progress(target: Path) -> str | None:
    for name in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD"):
        if git_path(target, name).exists():
            return name.lower()
    for name in ("rebase-merge", "rebase-apply"):
        if git_path(target, name).exists():
            return name
    return None


def runtime_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized.startswith(".tes/runtime/cortex/git-tap/")


def changed_paths(target: Path, event: str, head_before: str = "", head_after: str = "") -> list[str]:
    if event == "pre-commit":
        result = run_git(target, "diff", "--cached", "--name-only", "--diff-filter=ACMRD")
    elif event == "post-commit":
        result = run_git(target, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "HEAD")
    elif event == "post-checkout" and head_before and head_after:
        result = run_git(target, "diff", "--name-only", head_before, head_after)
    else:
        result = run_git(target, "status", "--porcelain", "--untracked-files=all")
        if result.returncode == 0:
            paths: list[str] = []
            for line in result.stdout.splitlines():
                path = line[3:].strip()
                if " -> " in path:
                    path = path.rsplit(" -> ", 1)[1]
                if path:
                    paths.append(path)
            return sorted(set(paths))
    if result.returncode != 0:
        return []
    return sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})


def diff_numstat(target: Path, event: str, head_before: str = "", head_after: str = "") -> str:
    if event == "pre-commit":
        result = run_git(target, "diff", "--cached", "--numstat")
    elif event == "post-commit":
        result = run_git(target, "diff-tree", "--root", "--no-commit-id", "--numstat", "-r", "HEAD")
    elif event == "post-checkout" and head_before and head_after:
        result = run_git(target, "diff", "--numstat", head_before, head_after)
    else:
        result = run_git(target, "diff", "--numstat", "HEAD")
    return result.stdout if result.returncode == 0 else ""


def summarized_diff_stat(numstat: str) -> dict[str, int | str]:
    files = 0
    insertions = 0
    deletions = 0
    binary = 0
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        files += 1
        added, removed = parts[0], parts[1]
        if added == "-" or removed == "-":
            binary += 1
            continue
        if added.isdigit():
            insertions += int(added)
        if removed.isdigit():
            deletions += int(removed)
    return {
        "files": files,
        "insertions": insertions,
        "deletions": deletions,
        "binary_files": binary,
        "numstat_digest": sha256_text(numstat)[:16],
    }


def extension_for(path: str) -> str:
    suffix = Path(path).suffix.lower().lstrip(".")
    return suffix or "[none]"


def category_for(path: str) -> str:
    normalized = path.replace("\\", "/")
    if normalized.startswith("docs/agents/cortex/"):
        return "cortex_memory"
    if normalized.startswith("docs/"):
        return "docs"
    if normalized.startswith("scripts/"):
        return "runtime_script"
    if normalized.startswith("src/"):
        return "adapter_source"
    if normalized.startswith((".agents/", ".claude/", ".cursor/", ".codex/")):
        return "agent_runtime"
    if normalized in {"AGENTS.md", "CLAUDE.md", "CURSOR.md", "package.json", "package-lock.json"}:
        return "contract_or_package"
    return "other"


def counted(values: list[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        result[value] = result.get(value, 0) + 1
    return dict(sorted(result.items()))


def classify_memory_signal(paths: list[str]) -> str:
    normalized = [path.replace("\\", "/") for path in paths]
    if not normalized:
        return "none"
    if any(path.startswith("docs/agents/cortex/") for path in normalized):
        return "docs_memory_change"
    if any(
        path.startswith(("docs/architecture/", "docs/adr/", "docs/tds/"))
        or path in {"AGENTS.md", "CLAUDE.md", "CURSOR.md", "package.json", "package-lock.json"}
        for path in normalized
    ):
        return "contract_change"
    if any(path.startswith("scripts/") and ("oracle" in path or "gate" in path) for path in normalized):
        return "oracle_learning"
    if any(path.startswith(("scripts/cortex", "scripts/tes_", "src/adapters/")) for path in normalized):
        return "runtime_learning"
    if any(path.startswith(("docs/", "scripts/", "src/")) for path in normalized):
        return "candidate"
    return "none"


def staged_digest(target: Path) -> str | None:
    result = run_git(target, "diff", "--cached", "--numstat")
    if result.returncode != 0 or not result.stdout.strip():
        return None
    name_status = run_git(target, "diff", "--cached", "--name-status")
    material = result.stdout + "\n" + (name_status.stdout if name_status.returncode == 0 else "")
    return sha256_text(material)[:32]


def gate_snapshot(target: Path, event: str) -> dict[str, Any] | None:
    if event != "pre-commit":
        return None
    staged = changed_paths(target, "pre-commit")
    return {
        "staged_path_count": len(staged),
        "staged_category_count": counted([category_for(path) for path in staged]),
        "quality_gate_invoked": False,
    }


def event_fingerprint(event: dict[str, Any]) -> str:
    payload = {
        "schema": event.get("schema"),
        "event": event.get("event"),
        "head_before": event.get("head_before"),
        "head_after": event.get("head_after"),
        "commit_hash": event.get("commit_hash"),
        "staged_digest": event.get("staged_digest"),
        "changed_path_count": event.get("changed_path_count"),
        "changed_path_categories": event.get("changed_path_categories"),
        "changed_file_extensions": event.get("changed_file_extensions"),
        "diff_stat": event.get("diff_stat"),
    }
    return sha256_text(canonical_json(payload))[:32]


def build_event(
    target: Path,
    event: str,
    *,
    head_before: str = "",
    head_after: str = "",
    commit_hash: str = "",
) -> dict[str, Any]:
    paths = changed_paths(target, event, head_before, head_after)
    numstat = diff_numstat(target, event, head_before, head_after)
    head = git_value(target, "rev-parse", "HEAD")
    commit = commit_hash or (head if event in {"post-commit", "post-checkout"} else "")
    parents = git_value(target, "show", "-s", "--format=%P", commit).split() if commit else []
    policy_decision = tes_codex_policy.decision_for_paths(target, paths)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "timestamp": utc_stamp(),
        "event": event,
        "repo_fingerprint": repository_fingerprint(target),
        "branch": git_value(target, "rev-parse", "--abbrev-ref", "HEAD") or "UNKNOWN",
        "head_before": head_before,
        "head_after": head_after or head,
        "commit_hash": commit,
        "parent_hashes": parents,
        "changed_paths": paths,
        "changed_path_count": len(paths),
        "changed_path_categories": counted([category_for(path) for path in paths]),
        "changed_file_extensions": counted([extension_for(path) for path in paths]),
        "diff_stat": summarized_diff_stat(numstat),
        "staged_digest": staged_digest(target),
        "gate_snapshot": gate_snapshot(target, event),
        "memory_signal": classify_memory_signal(paths),
        "policy_schema": policy_decision.get("schema"),
        "policy_digest": policy_decision.get("policy_digest"),
        "policy_state": policy_decision.get("policy_state"),
        "policy_decision": policy_decision.get("decision_state"),
        "policy_path_classes": policy_decision.get("source_classes", {}),
        "privacy_status": "PASS",
        "blockers": [],
    }
    if policy_decision.get("failures"):
        payload["blockers"] = [*payload["blockers"], *policy_decision.get("failures", [])]
    failures = privacy_failures(payload)
    if failures:
        payload["privacy_status"] = "NEEDS_PRIVACY_GUARD"
        payload["blockers"] = failures
    payload["event_fingerprint"] = event_fingerprint(payload)
    return payload


def iter_strings(value: Any, path: str = "") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, dict):
        out: list[tuple[str, str]] = []
        for key, item in value.items():
            key_path = f"{path}.{key}" if path else str(key)
            out.extend(iter_strings(item, key_path))
        return out
    if isinstance(value, list):
        out = []
        for index, item in enumerate(value):
            out.extend(iter_strings(item, f"{path}[{index}]"))
        return out
    return []


def privacy_failures(event: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if event.get("schema") != SCHEMA:
        failures.append("schema mismatch")
    if event.get("event") not in EVENTS:
        failures.append("unsupported event")
    if event.get("memory_signal") not in MEMORY_SIGNALS:
        failures.append("unsupported memory_signal")
    for key in event.keys():
        if FORBIDDEN_KEY_RE.search(str(key)):
            failures.append(f"forbidden event key: {key}")
    for path, value in iter_strings(event):
        if "\n" in value:
            failures.append(f"multiline value rejected at {path}")
        if RAW_DIFF_RE.search(value):
            failures.append(f"raw diff content rejected at {path}")
        if SECRET_RE.search(value):
            failures.append(f"secret-like content rejected at {path}")
        if ABSOLUTE_PATH_RE.search(value):
            failures.append(f"absolute local path rejected at {path}")
    return sorted(set(failures))


def validate_event_payload(event: dict[str, Any]) -> dict[str, Any]:
    required = {
        "schema",
        "timestamp",
        "event",
        "repo_fingerprint",
        "branch",
        "head_before",
        "head_after",
        "commit_hash",
        "parent_hashes",
        "changed_path_count",
        "changed_path_categories",
        "changed_file_extensions",
        "diff_stat",
        "staged_digest",
        "gate_snapshot",
        "memory_signal",
        "privacy_status",
        "blockers",
    }
    failures = [f"missing field: {field}" for field in sorted(required - set(event.keys()))]
    failures.extend(privacy_failures(event))
    status = "PASS" if not failures else ("NEEDS_PRIVACY_GUARD" if any("rejected" in item or "forbidden" in item for item in failures) else "FAIL")
    return {"version": VERSION, "status": status, "failures": sorted(set(failures))}


def runtime_dir(target: Path) -> Path:
    return target / RUNTIME_ROOT


def ensure_runtime(target: Path) -> None:
    runtime_dir(target).mkdir(parents=True, exist_ok=True)
    for path in (target / EVENTS_FILE, target / PENDING_FILE):
        path.touch(exist_ok=True)


def log_line(target: Path, message: str) -> None:
    ensure_runtime(target)
    with (target / LOG_FILE).open("a", encoding="utf-8") as handle:
        handle.write(f"{utc_stamp()} {message}\n")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(payload) + "\n")


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.exists():
        return [], []
    records: list[dict[str, Any]] = []
    failures: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            failures.append(f"{rel(path, path.parents[3] if len(path.parents) > 3 else path.parent)}:{line_number}: malformed JSONL")
            continue
        if not isinstance(payload, dict):
            failures.append(f"{path.name}:{line_number}: JSONL record must be an object")
            continue
        validation = validate_event_payload(payload)
        if validation["status"] != "PASS":
            failures.extend(f"{path.name}:{line_number}: {item}" for item in validation.get("failures", []))
        records.append(payload)
    return records, failures


def acquire_lock(target: Path, *, wait: bool, timeout: float) -> bool:
    ensure_runtime(target)
    lock = target / LOCK_FILE
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if not wait or time.monotonic() >= deadline:
                return False
            time.sleep(0.05)
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump({"pid": os.getpid(), "created_at": utc_stamp(), "schema": SCHEMA}, handle, sort_keys=True)
            handle.write("\n")
        return True


def release_lock(target: Path) -> None:
    try:
        (target / LOCK_FILE).unlink()
    except FileNotFoundError:
        pass


def append_pending(target: Path, event: dict[str, Any]) -> str:
    ensure_runtime(target)
    pending_path = target / PENDING_FILE
    records, _failures = read_jsonl(pending_path)
    fingerprint = event.get("event_fingerprint") or event_fingerprint(event)
    if any(record.get("event_fingerprint") == fingerprint for record in records):
        return "dedupe-pending"
    append_jsonl(pending_path, event)
    return "append-pending"


def append_event(target: Path, event: dict[str, Any]) -> dict[str, Any]:
    validation = validate_event_payload(event)
    if validation["status"] != "PASS":
        log_line(target, f"privacy-blocked {validation['status']} {validation.get('failures', [])}")
        return {
            "version": VERSION,
            "status": validation["status"],
            "event": event.get("event"),
            "failures": validation.get("failures", []),
            "writes": [],
        }
    append_jsonl(target / EVENTS_FILE, event)
    log_line(target, f"event-appended {event.get('event')} {event.get('event_fingerprint')}")
    return {
        "version": VERSION,
        "status": "PASS",
        "event": event.get("event"),
        "event_fingerprint": event.get("event_fingerprint"),
        "writes": [EVENTS_FILE.as_posix()],
    }


def drain_pending(target: Path) -> int:
    pending_path = target / PENDING_FILE
    records, failures = read_jsonl(pending_path)
    if failures:
        log_line(target, "pending-drain-fail " + "; ".join(failures))
        return 0
    if not records:
        return 0
    existing, _existing_failures = read_jsonl(target / EVENTS_FILE)
    seen = {record.get("event_fingerprint") for record in existing if record.get("event_fingerprint")}
    drained = 0
    for record in records:
        fingerprint = record.get("event_fingerprint") or event_fingerprint(record)
        if fingerprint in seen:
            continue
        append_jsonl(target / EVENTS_FILE, record)
        seen.add(fingerprint)
        drained += 1
    pending_path.write_text("", encoding="utf-8")
    if drained:
        log_line(target, f"pending-drained count={drained}")
    return drained


def launch_background_drain(target: Path) -> None:
    if os.environ.get("TES_CORTEX_GIT_TAP_NO_BACKGROUND") == "1":
        return
    helper = Path(__file__).resolve()
    log = target / LOG_FILE
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        subprocess.Popen(
            [sys.executable, str(helper), "drain", "--target", str(target), "--background"],
            cwd=target,
            stdout=handle,
            stderr=handle,
            start_new_session=True,
        )


def should_skip_capture(target: Path, event: str, checkout_flag: str | None, paths: list[str]) -> str | None:
    in_progress = git_in_progress(target)
    if in_progress:
        return f"git operation in progress: {in_progress}"
    if event == "post-checkout" and checkout_flag == "0":
        return "post-checkout file checkout"
    if paths and all(runtime_path(path) for path in paths):
        return "self-generated runtime path"
    return None


def capture(
    target: Path,
    event: str,
    *,
    head_before: str = "",
    head_after: str = "",
    checkout_flag: str | None = None,
    no_background: bool = False,
) -> dict[str, Any]:
    target = target.expanduser().resolve()
    if event not in EVENTS:
        return {"version": VERSION, "status": "FAIL", "failures": [f"unsupported event: {event}"]}
    if not is_git_work_tree(target):
        return {"version": VERSION, "status": "SKIP", "reason": "target is not a Git work tree", "writes": []}
    paths = changed_paths(target, event, head_before, head_after)
    skip_reason = should_skip_capture(target, event, checkout_flag, paths)
    if skip_reason:
        log_line(target, f"capture-skip event={event} reason={skip_reason}")
        return {"version": VERSION, "status": "SKIP", "event": event, "reason": skip_reason, "writes": []}
    event_payload = build_event(target, event, head_before=head_before, head_after=head_after)
    if not acquire_lock(target, wait=False, timeout=0):
        action = append_pending(target, event_payload)
        log_line(target, f"event-queued action={action} event={event} {event_payload.get('event_fingerprint')}")
        return {
            "version": VERSION,
            "status": "QUEUED",
            "event": event,
            "action": action,
            "event_fingerprint": event_payload.get("event_fingerprint"),
            "writes": [PENDING_FILE.as_posix()],
        }
    try:
        result = append_event(target, event_payload)
    finally:
        release_lock(target)
    if result["status"] == "PASS" and event in {"post-commit", "post-checkout"} and not no_background:
        launch_background_drain(target)
    return result


def drain(target: Path, *, background: bool = False, timeout: float = LOCK_TIMEOUT_SECONDS) -> dict[str, Any]:
    target = target.expanduser().resolve()
    if not is_git_work_tree(target):
        return {"version": VERSION, "status": "SKIP", "reason": "target is not a Git work tree", "writes": []}
    if not acquire_lock(target, wait=not background, timeout=timeout):
        status = "NEEDS_CANARY_EVIDENCE" if background else "FAIL"
        log_line(target, f"drain-lock-timeout status={status}")
        return {"version": VERSION, "status": status, "reason": "lock held", "writes": [LOG_FILE.as_posix()]}
    try:
        before = drain_pending(target)
        log_line(target, "consolidation no_llm=true durable_docs_write=false")
        if os.environ.get("TES_CORTEX_GIT_TAP_TEST_ENQUEUE_DURING_DRAIN") == "1":
            pending = build_event(target, "manual-drain")
            pending["event_fingerprint"] = sha256_text(canonical_json(pending) + ":during-drain")[:32]
            append_jsonl(target / PENDING_FILE, pending)
        after = drain_pending(target)
    finally:
        release_lock(target)
    return {
        "version": VERSION,
        "status": "PASS",
        "drained_before": before,
        "drained_after": after,
        "writes": [EVENTS_FILE.as_posix(), PENDING_FILE.as_posix(), LOG_FILE.as_posix()],
    }


def proposal_for_event(event: dict[str, Any]) -> dict[str, Any]:
    signal = str(event.get("memory_signal") or "none")
    state = "NO_MEMORY_SIGNAL"
    if event.get("privacy_status") != "PASS":
        state = "BLOCKED_PRIVACY"
    elif event.get("policy_decision") in {
        "AUTO_PROMOTED",
        "REVIEW_REQUIRED",
        "DENIED_BY_POLICY",
        "BLOCKED_PRIVACY",
        "NO_MEMORY_SIGNAL",
    }:
        state = str(event.get("policy_decision"))
    elif signal in {"contract_change", "runtime_learning", "oracle_learning", "docs_memory_change"}:
        state = "NEEDS_CURATION"
    elif signal == "candidate":
        state = "PROPOSE_MEMORY"
    if state not in DECISION_STATES:
        state = "NO_MEMORY_SIGNAL"
    evidence_hash = sha256_text(canonical_json(event))[:24]
    return {
        "schema": PROPOSAL_SCHEMA,
        "created_at": utc_stamp(),
        "decision_state": state,
        "event_fingerprint": event.get("event_fingerprint") or event_fingerprint(event),
        "evidence_hash": evidence_hash,
        "memory_signal": signal,
        "event_summary": {
            "event": event.get("event"),
            "changed_path_count": event.get("changed_path_count", 0),
            "changed_path_categories": event.get("changed_path_categories", {}),
            "changed_file_extensions": event.get("changed_file_extensions", {}),
            "diff_stat": event.get("diff_stat", {}),
            "privacy_status": event.get("privacy_status"),
            "policy_state": event.get("policy_state"),
            "policy_digest": event.get("policy_digest"),
            "policy_decision": event.get("policy_decision"),
            "policy_path_classes": event.get("policy_path_classes", {}),
            "changed_paths": event.get("changed_paths", []),
        },
        "proposal": None if state == "NO_MEMORY_SIGNAL" else {
            "route": "policy auto-promote outside hook" if state == "AUTO_PROMOTED" else "proposal-only; review before Cortex apply",
            "claim_needed": "Promote only policy-approved agent memory, durable decisions, reusable lessons, contract changes, or runtime learning.",
            "curation_boundary": "Git Tap does not write docs/**; use the approved Cortex apply path after explicit curation.",
        },
    }


def reflect_proposals(target: Path) -> dict[str, Any]:
    target = target.expanduser().resolve()
    events, failures = read_jsonl(target / EVENTS_FILE)
    if failures:
        return {"version": VERSION, "status": "FAIL", "failures": failures, "writes": []}
    proposals = [proposal_for_event(event) for event in events]
    material = [proposal for proposal in proposals if proposal["decision_state"] != "NO_MEMORY_SIGNAL"]
    if material:
        (target / PROPOSALS_FILE).parent.mkdir(parents=True, exist_ok=True)
        existing_text = (target / PROPOSALS_FILE).read_text(encoding="utf-8") if (target / PROPOSALS_FILE).exists() else ""
        existing_ids = {
            json.loads(line).get("event_fingerprint")
            for line in existing_text.splitlines()
            if line.strip().startswith("{")
        }
        with (target / PROPOSALS_FILE).open("a", encoding="utf-8") as handle:
            for proposal in material:
                if proposal["event_fingerprint"] not in existing_ids:
                    handle.write(canonical_json(proposal) + "\n")
    return {
        "version": VERSION,
        "status": "PASS",
        "events": len(events),
        "proposals": len(material),
        "decision_states": counted([str(proposal["decision_state"]) for proposal in proposals]),
        "writes": [PROPOSALS_FILE.as_posix()] if material else [],
    }


def proposal_privacy_failures(proposal: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for key in proposal.keys():
        if FORBIDDEN_KEY_RE.search(str(key)):
            failures.append(f"forbidden proposal key: {key}")
    for path, value in iter_strings(proposal):
        if "\n" in value:
            failures.append(f"multiline value rejected at {path}")
        if RAW_DIFF_RE.search(value):
            failures.append(f"raw diff content rejected at {path}")
        if SECRET_RE.search(value):
            failures.append(f"secret-like content rejected at {path}")
        if ABSOLUTE_PATH_RE.search(value):
            failures.append(f"absolute local path rejected at {path}")
    return sorted(set(failures))


def validate_proposal_payload(proposal: dict[str, Any]) -> dict[str, Any]:
    required = {
        "schema",
        "created_at",
        "decision_state",
        "event_fingerprint",
        "evidence_hash",
        "memory_signal",
        "proposal",
    }
    failures = [f"missing field: {field}" for field in sorted(required - set(proposal.keys()))]
    if proposal.get("schema") != PROPOSAL_SCHEMA:
        failures.append("proposal schema mismatch")
    if proposal.get("decision_state") not in DECISION_STATES:
        failures.append("unsupported decision_state")
    if proposal.get("memory_signal") not in MEMORY_SIGNALS:
        failures.append("unsupported memory_signal")
    failures.extend(proposal_privacy_failures(proposal))
    status = "PASS" if not failures else (
        "NEEDS_PRIVACY_GUARD"
        if any("rejected" in item or "forbidden" in item for item in failures)
        else "FAIL"
    )
    return {"version": VERSION, "status": status, "failures": sorted(set(failures))}


def read_proposals(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.exists():
        return [], []
    records: list[dict[str, Any]] = []
    failures: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            failures.append(f"{path.name}:{line_number}: malformed JSONL")
            continue
        if not isinstance(payload, dict):
            failures.append(f"{path.name}:{line_number}: JSONL record must be an object")
            continue
        validation = validate_proposal_payload(payload)
        if validation["status"] != "PASS":
            failures.extend(f"{path.name}:{line_number}: {item}" for item in validation.get("failures", []))
        records.append(payload)
    return records, failures


def preferred_git_tap_command(target: Path) -> str:
    if (target / ".tes/bin/cortex_git_tap.py").exists():
        return "python3 .tes/bin/cortex_git_tap.py"
    if (target / "scripts/cortex_git_tap.py").exists():
        return "python3 scripts/cortex_git_tap.py"
    return "python3 <tes-package>/scripts/cortex_git_tap.py"


def proposal_cell_name(proposal: dict[str, Any]) -> str:
    signal = str(proposal.get("memory_signal") or "memory")
    fingerprint = str(proposal.get("event_fingerprint") or "proposal")[:12]
    return f"git-tap-{signal.replace('_', '-')}-{fingerprint}"


def proposal_plan_item(target: Path, proposal: dict[str, Any]) -> dict[str, Any]:
    decision = str(proposal.get("decision_state") or "NO_MEMORY_SIGNAL")
    fingerprint = str(proposal.get("event_fingerprint") or "")
    cell = proposal_cell_name(proposal)
    if decision == "BLOCKED_PRIVACY":
        action = "blocked-privacy-review"
        next_step = "Reject or sanitize the proposal evidence before any Cortex apply command."
        apply_command = None
    elif decision == "DENIED_BY_POLICY":
        action = "denied-by-policy"
        next_step = "Do not promote this event into Cortex memory."
        apply_command = None
    elif decision == "REVIEW_REQUIRED":
        action = "review-required"
        next_step = "Review the proposal before any Cortex apply command."
        command = preferred_git_tap_command(target)
        apply_command = (
            f"{command} apply-proposal --target . "
            f"--event-fingerprint {shlex.quote(fingerprint)} "
            f"--cell {shlex.quote(cell)} "
            "--claim '<approved durable claim>' --yes"
        )
    elif decision == "AUTO_PROMOTED":
        action = "auto-promote-outside-hook"
        next_step = "Run auto-promote outside hook execution or let the host canary curation step run it."
        command = preferred_git_tap_command(target)
        apply_command = f"{command} auto-promote --target ."
    elif decision == "NO_MEMORY_SIGNAL":
        action = "no-op"
        next_step = "No durable Cortex memory action is recommended."
        apply_command = None
    else:
        action = "review-then-explicit-apply"
        next_step = "Review the proposal, write an approved durable claim, then run apply-proposal with --yes outside hook execution."
        command = preferred_git_tap_command(target)
        apply_command = (
            f"{command} apply-proposal --target . "
            f"--event-fingerprint {shlex.quote(fingerprint)} "
            f"--cell {shlex.quote(cell)} "
            "--claim '<approved durable claim>' --yes"
        )
    return {
        "event_fingerprint": fingerprint,
        "decision_state": decision,
        "memory_signal": proposal.get("memory_signal"),
        "evidence_hash": proposal.get("evidence_hash"),
        "action": action,
        "recommended_cell": cell,
        "next_step": next_step,
        "apply_command": apply_command,
    }


def curate_proposals_plan(target: Path) -> dict[str, Any]:
    target = target.expanduser().resolve()
    proposals, failures = read_proposals(target / PROPOSALS_FILE)
    if failures:
        return {"version": VERSION, "schema": CURATION_PLAN_SCHEMA, "status": "FAIL", "failures": failures, "writes": []}
    plan = [proposal_plan_item(target, proposal) for proposal in proposals]
    return {
        "version": VERSION,
        "schema": CURATION_PLAN_SCHEMA,
        "status": "PASS",
        "proposal_count": len(proposals),
        "decision_states": counted([str(proposal.get("decision_state")) for proposal in proposals]),
        "plan": plan,
        "writes": [],
    }


def find_proposal(target: Path, event_fingerprint: str) -> tuple[dict[str, Any] | None, list[str]]:
    proposals, failures = read_proposals(target / PROPOSALS_FILE)
    if failures:
        return None, failures
    for proposal in proposals:
        if proposal.get("event_fingerprint") == event_fingerprint:
            return proposal, []
    return None, [f"proposal not found: {event_fingerprint}"]


def load_cortex_helper() -> Any:
    import cortex as cortex_helper

    return cortex_helper


def proposal_source_rel(event_fingerprint: str) -> str:
    safe = re.sub(r"[^a-fA-F0-9]", "", event_fingerprint)[:32]
    return f"sources/git-tap/{safe or 'proposal'}.md"


def proposal_source_text(proposal: dict[str, Any]) -> str:
    summary = proposal.get("event_summary") if isinstance(proposal.get("event_summary"), dict) else {}
    diff_stat = summary.get("diff_stat") if isinstance(summary.get("diff_stat"), dict) else {}
    categories = canonical_json(summary.get("changed_path_categories", {}))
    extensions = canonical_json(summary.get("changed_file_extensions", {}))
    return (
        "# Git Tap Proposal Evidence\n\n"
        "## Proposal\n\n"
        f"- Schema: `{proposal.get('schema')}`\n"
        f"- Decision state: `{proposal.get('decision_state')}`\n"
        f"- Memory signal: `{proposal.get('memory_signal')}`\n"
        f"- Event fingerprint: `{proposal.get('event_fingerprint')}`\n"
        f"- Evidence hash: `{proposal.get('evidence_hash')}`\n"
        f"- Event: `{summary.get('event', 'unknown')}`\n"
        f"- Changed path count: `{summary.get('changed_path_count', 0)}`\n"
        f"- Changed path categories: `{categories}`\n"
        f"- Changed file extensions: `{extensions}`\n"
        f"- Diff stat digest: `{diff_stat.get('numstat_digest', '')}`\n"
        f"- Privacy status: `{summary.get('privacy_status', 'unknown')}`\n\n"
        "## Boundary\n\n"
        "This source retains only sanitized Git Tap status, counts, and hashes. "
        "It contains no raw diff, raw transcript, prompt text, tool payload, command output, secret, or local absolute path.\n"
    )


def apply_proposal(
    target: Path,
    *,
    event_fingerprint: str,
    cell: str,
    claim: str,
    summary: str | None,
    authorized: bool,
    update_existing: bool,
) -> dict[str, Any]:
    target = target.expanduser().resolve()
    if os.environ.get("TES_CORTEX_GIT_TAP_HOOK") == "1":
        return {
            "version": VERSION,
            "status": "BLOCKED",
            "failures": ["hook-triggered execution cannot apply Cortex memory"],
            "writes": [],
        }
    if not authorized:
        return {
            "version": VERSION,
            "status": "NEEDS_AUTH",
            "failures": [],
            "writes": [],
            "message": "apply-proposal requires --yes outside hook execution",
        }
    proposal, failures = find_proposal(target, event_fingerprint)
    if failures or proposal is None:
        return {"version": VERSION, "status": "FAIL", "failures": failures, "writes": []}
    if proposal.get("decision_state") in {"NO_MEMORY_SIGNAL", "BLOCKED_PRIVACY", "DENIED_BY_POLICY"}:
        return {
            "version": VERSION,
            "status": "FAIL",
            "failures": [f"proposal is not eligible for apply: {proposal.get('decision_state')}"],
            "writes": [],
        }
    cortex_helper = load_cortex_helper()
    verify_result = cortex_helper.verify(target)
    if verify_result.get("status") != "PASS":
        return {
            "version": VERSION,
            "status": "FAIL",
            "failures": verify_result.get("failures", []),
            "writes": [],
        }
    try:
        cell_path = cortex_helper.resolve_cell_path(target, cell)
    except ValueError as exc:
        return {"version": VERSION, "status": "FAIL", "failures": [str(exc)], "writes": []}
    if cell_path.exists() and not update_existing:
        return {
            "version": VERSION,
            "status": "FAIL",
            "failures": [f"cell already exists; pass --update to replace it: {cortex_helper.rel(cell_path, target)}"],
            "writes": [],
        }
    source_rel = proposal_source_rel(event_fingerprint)
    source_path = cortex_helper.cortex_path(target) / source_rel
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(proposal_source_text(proposal), encoding="utf-8")
    result = cortex_helper.apply_cell(
        target,
        cell,
        claim,
        [source_rel],
        summary,
        [],
        authorized=True,
        update_existing=update_existing,
    )
    result["version"] = VERSION
    result["proposal"] = {
        "event_fingerprint": event_fingerprint,
        "decision_state": proposal.get("decision_state"),
        "memory_signal": proposal.get("memory_signal"),
        "evidence_hash": proposal.get("evidence_hash"),
    }
    if result.get("status") == "PASS" and cortex_helper.rel(source_path, target) not in result.get("writes", []):
        result["writes"] = [cortex_helper.rel(source_path, target), *result.get("writes", [])]
    return result


def auto_promote(target: Path) -> dict[str, Any]:
    target = target.expanduser().resolve()
    if os.environ.get("TES_CORTEX_GIT_TAP_HOOK") == "1":
        return {
            "version": VERSION,
            "status": "BLOCKED_IN_HOOK",
            "failures": ["hook-triggered execution cannot auto-promote Cortex memory"],
            "writes": [],
        }
    proposals, failures = read_proposals(target / PROPOSALS_FILE)
    if failures:
        return {"version": VERSION, "status": "FAIL", "failures": failures, "writes": []}
    writes: list[str] = []
    promoted: list[dict[str, Any]] = []
    skipped = 0
    promotion_failures: list[str] = []
    seen_candidates: set[str] = set()
    for proposal in proposals:
        if proposal.get("decision_state") != "AUTO_PROMOTED":
            skipped += 1
            continue
        summary = proposal.get("event_summary") if isinstance(proposal.get("event_summary"), dict) else {}
        paths = [str(path) for path in summary.get("changed_paths", []) if isinstance(path, str)]
        candidate_key = sha256_text(canonical_json({"paths": sorted(paths), "policy": summary.get("policy_digest")}))[:24]
        if candidate_key in seen_candidates:
            skipped += 1
            continue
        seen_candidates.add(candidate_key)
        decision = tes_codex_policy.decision_for_paths(target, paths)
        if summary.get("policy_digest") and summary.get("policy_digest") != decision.get("policy_digest"):
            promotion_failures.append(f"{proposal.get('event_fingerprint')}: stale proposal policy digest changed")
            continue
        if summary.get("policy_decision") != "AUTO_PROMOTED":
            promotion_failures.append(f"{proposal.get('event_fingerprint')}: stale proposal missing AUTO_PROMOTED policy decision")
            continue
        if summary.get("policy_state") not in {"DEFAULT", "OWNER_EDITED"}:
            promotion_failures.append(f"{proposal.get('event_fingerprint')}: stale proposal policy state is not valid")
            continue
        if decision.get("decision_state") != "AUTO_PROMOTED":
            promotion_failures.append(
                f"{proposal.get('event_fingerprint')}: current policy decision is {decision.get('decision_state')}, not AUTO_PROMOTED"
            )
            continue
        result = tes_codex_policy.auto_promote_candidates(
            target,
            paths,
            event_fingerprint=str(proposal.get("event_fingerprint") or ""),
            policy_decision=decision,
        )
        if result.get("status") != "PASS":
            promotion_failures.extend(str(item) for item in result.get("failures", []))
            if not result.get("failures"):
                promotion_failures.append(f"{proposal.get('event_fingerprint')}: auto promotion returned {result.get('status')}")
            continue
        writes.extend(str(path) for path in result.get("writes", []))
        promoted.extend(item for item in result.get("promoted", []) if isinstance(item, dict))
    status = "PASS" if promoted and not promotion_failures else ("FAIL" if promotion_failures else "SKIP")
    return {
        "version": VERSION,
        "status": status,
        "promoted": promoted,
        "skipped": skipped,
        "writes": sorted(set(writes)),
        "failures": sorted(set(promotion_failures)),
    }


def audit(target: Path) -> dict[str, Any]:
    target = target.expanduser().resolve()
    events, event_failures = read_jsonl(target / EVENTS_FILE)
    pending, pending_failures = read_jsonl(target / PENDING_FILE)
    failures = [*event_failures, *pending_failures]
    return {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "events": len(events),
        "pending": len(pending),
        "failures": failures,
    }


def hook_block(target: Path, hook_name: str) -> str:
    helper = ".tes/bin/cortex_git_tap.py"
    source_helper = "scripts/cortex_git_tap.py"
    if hook_name == "post-checkout":
        capture_args = 'post-checkout --head-before "${1:-}" --head-after "${2:-}" --checkout-flag "${3:-}"'
    else:
        capture_args = hook_name
    return f"""{START_MARKER_PREFIX} {hook_name}
# {HOOK_MARKER}
if [ -z "${{TES_CORTEX_GIT_TAP_DISABLE:-}}" ]; then
  mkdir -p ".tes/runtime/cortex/git-tap"
  if [ -f "{helper}" ]; then
    TES_CORTEX_GIT_TAP_HOOK=1 python3 "{helper}" capture --target . --event {capture_args} >/dev/null 2>>".tes/runtime/cortex/git-tap/git-tap.log" || true
  elif [ -f "{source_helper}" ]; then
    TES_CORTEX_GIT_TAP_HOOK=1 python3 "{source_helper}" capture --target . --event {capture_args} >/dev/null 2>>".tes/runtime/cortex/git-tap/git-tap.log" || true
  else
    printf '%s\\n' "TES Cortex Git Tap runtime missing" >> ".tes/runtime/cortex/git-tap/git-tap.log"
  fi
fi
{END_MARKER_PREFIX} {hook_name}
"""


def remove_marked_block(text: str, hook_name: str) -> str:
    start = f"{START_MARKER_PREFIX} {hook_name}"
    end = f"{END_MARKER_PREFIX} {hook_name}"
    lines = text.splitlines()
    out: list[str] = []
    index = 0
    while index < len(lines):
        if lines[index].strip() == start:
            index += 1
            while index < len(lines) and lines[index].strip() != end:
                index += 1
            if index < len(lines):
                index += 1
            continue
        out.append(lines[index])
        index += 1
    body = "\n".join(out).rstrip()
    return body + ("\n" if body else "")


def resolve_hook(target: Path, hook_name: str) -> dict[str, Any]:
    directory = git_dir(target)
    if directory is None:
        return {"status": "BLOCKED", "reason": "target is not a Git work tree"}
    configured = git_config_get(target, "core.hooksPath")
    if configured == "/dev/null":
        return {"status": "BLOCKED", "reason": "Git hooks are disabled by core.hooksPath=/dev/null"}
    if configured and os.name != "nt" and WINDOWS_DRIVE_RE.match(configured):
        return {"status": "BLOCKED", "reason": f"impossible hook path on POSIX: {configured}"}
    hooks_dir = directory / "hooks"
    mode = "git-default"
    if configured:
        configured_path = Path(configured).expanduser()
        hooks_dir = configured_path if configured_path.is_absolute() else target / configured_path
        mode = "core.hooksPath"
    if hooks_dir.name == "_" and hooks_dir.parent.name == ".husky":
        return {"status": "PASS", "hook": hooks_dir.parent / hook_name, "mode": "husky", "hooksPath": configured}
    return {"status": "PASS", "hook": hooks_dir / hook_name, "mode": mode, "hooksPath": configured}


def ensure_git_exclude(target: Path) -> str | None:
    directory = git_dir(target)
    if directory is None:
        return None
    exclude = directory / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    existing = exclude.read_text(encoding="utf-8", errors="replace") if exclude.exists() else ""
    lines = existing.splitlines()
    changed = False
    for pattern in GIT_EXCLUDE_PATTERNS:
        if pattern not in lines:
            lines.append(pattern)
            changed = True
    if changed:
        exclude.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return rel(exclude, target)


def install_hooks(target: Path, *, dry_run: bool = False) -> dict[str, Any]:
    target = target.expanduser().resolve()
    if not is_git_work_tree(target):
        return {"version": VERSION, "status": "BLOCKED", "reason": "target is not a Git work tree", "writes": []}
    resolved = {hook: resolve_hook(target, hook) for hook in HOOKS}
    blockers = [f"{hook}: {data['reason']}" for hook, data in resolved.items() if data.get("status") != "PASS"]
    if blockers:
        return {"version": VERSION, "status": "BLOCKED", "failures": blockers, "writes": []}
    writes: list[str] = []
    for hook_name, data in resolved.items():
        hook = Path(data["hook"])
        prior = hook.read_text(encoding="utf-8", errors="replace") if hook.exists() else "#!/bin/sh\n"
        if not prior.startswith("#!"):
            prior = "#!/bin/sh\n" + prior
        text = remove_marked_block(prior, hook_name).rstrip() + "\n" + hook_block(target, hook_name)
        if dry_run:
            writes.append(rel(hook, target))
            continue
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text(text, encoding="utf-8")
        hook.chmod(0o755)
        writes.append(rel(hook, target))
    exclude = ensure_git_exclude(target) if not dry_run else ".git/info/exclude"
    if exclude:
        writes.append(exclude)
    return {
        "version": VERSION,
        "status": "PASS",
        "hooks": {hook: rel(Path(data["hook"]), target) for hook, data in resolved.items()},
        "hook_modes": {hook: data.get("mode") for hook, data in resolved.items()},
        "hooksPath": next((data.get("hooksPath") for data in resolved.values() if data.get("hooksPath")), None),
        "writes": sorted(set(writes)),
    }


def uninstall_hooks(target: Path, *, dry_run: bool = False) -> dict[str, Any]:
    target = target.expanduser().resolve()
    if not is_git_work_tree(target):
        return {"version": VERSION, "status": "SKIP", "reason": "target is not a Git work tree", "writes": []}
    writes: list[str] = []
    for hook_name in HOOKS:
        data = resolve_hook(target, hook_name)
        if data.get("status") != "PASS":
            continue
        hook = Path(data["hook"])
        if not hook.exists():
            continue
        current = hook.read_text(encoding="utf-8", errors="replace")
        stripped = remove_marked_block(current, hook_name)
        if stripped == current:
            continue
        writes.append(rel(hook, target))
        if dry_run:
            continue
        if stripped.strip():
            hook.write_text(stripped, encoding="utf-8")
            hook.chmod(0o755)
        else:
            hook.unlink()
    return {"version": VERSION, "status": "PASS", "writes": writes}


def init_git(target: Path) -> None:
    git_env = isolated_git_env()
    subprocess.run(["git", "init", "-q"], cwd=target, text=True, capture_output=True, check=False, env=git_env)
    subprocess.run(
        ["git", "config", "user.email", "target@example.test"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
        env=git_env,
    )
    subprocess.run(
        ["git", "config", "user.name", "Target User"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
        env=git_env,
    )


def commit_file(target: Path, path: str, content: str, message: str) -> str:
    file_path = target / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", path], cwd=target, text=True, capture_output=True, check=False, env=isolated_git_env())
    result = subprocess.run(
        ["git", "commit", "-q", "-m", message],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
        env=isolated_git_env(),
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return git_value(target, "rev-parse", "HEAD")


def docs_snapshot(target: Path) -> dict[str, str]:
    docs = target / "docs"
    if not docs.exists():
        return {}
    return {
        rel(path, target): sha256_text(path.read_text(encoding="utf-8", errors="replace"))
        for path in sorted(docs.rglob("*"))
        if path.is_file()
    }


def copy_installed_git_tap_helpers(target: Path) -> None:
    bin_dir = target / ".tes/bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    for helper in ("cortex_git_tap.py", "tes_codex_policy.py"):
        shutil.copy2(Path(__file__).resolve().with_name(helper), bin_dir / helper)


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-cortex-git-tap-") as tempdir:
        root = Path(tempdir)

        schema_target = root / "schema"
        schema_target.mkdir()
        init_git(schema_target)
        (schema_target / "docs/architecture").mkdir(parents=True)
        (schema_target / "docs/architecture/CONTRACT.md").write_text("# Contract\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "docs/architecture/CONTRACT.md"],
            cwd=schema_target,
            text=True,
            capture_output=True,
            check=False,
            env=isolated_git_env(),
        )
        event = build_event(schema_target, "pre-commit")
        validation = validate_event_payload(event)
        if validation["status"] != "PASS":
            failures.append("synthetic pre-commit event must validate")
            failures.extend(validation.get("failures", []))
        capture_result = capture(schema_target, "pre-commit", no_background=True)
        if capture_result.get("status") != "PASS":
            failures.append("pre-commit capture must pass")
        audit_result = audit(schema_target)
        if audit_result.get("status") != "PASS" or audit_result.get("events") != 1:
            failures.append("event audit must pass after capture")

        malformed_target = root / "malformed"
        malformed_target.mkdir()
        init_git(malformed_target)
        ensure_runtime(malformed_target)
        (malformed_target / EVENTS_FILE).write_text("{not-json}\n", encoding="utf-8")
        malformed = audit(malformed_target)
        if malformed.get("status") != "FAIL":
            failures.append("malformed JSONL must classify as FAIL")

        raw_event = dict(event)
        raw_event["raw_diff"] = "diff --git a/a b/a\n@@ -1 +1 @@\n"
        raw_validation = validate_event_payload(raw_event)
        if raw_validation["status"] != "NEEDS_PRIVACY_GUARD":
            failures.append("raw diff content must be rejected as NEEDS_PRIVACY_GUARD")
        secret_event = dict(event)
        secret_event["branch"] = "token=abc123"
        if validate_event_payload(secret_event)["status"] != "NEEDS_PRIVACY_GUARD":
            failures.append("secret-like content must be rejected")
        counts_event = dict(event)
        counts_event["changed_path_categories"] = {"docs": 2}
        counts_event["changed_file_extensions"] = {"md": 2}
        if validate_event_payload(counts_event)["status"] != "PASS":
            failures.append("counts, hashes, and categories must remain allowed")

        hook_target = root / "hooks"
        hook_target.mkdir()
        init_git(hook_target)
        existing = hook_target / ".git/hooks/post-commit"
        existing.write_text("#!/bin/sh\nprintf '%s\\n' foreign-hook\n", encoding="utf-8")
        existing.chmod(0o755)
        first_install = install_hooks(hook_target)
        second_install = install_hooks(hook_target)
        post_commit_text = existing.read_text(encoding="utf-8")
        if first_install.get("status") != "PASS" or second_install.get("status") != "PASS":
            failures.append("hook install must pass twice")
        if "foreign-hook" not in post_commit_text:
            failures.append("hook install must preserve existing content")
        if post_commit_text.count(START_MARKER_PREFIX + " post-commit") != 1:
            failures.append("hook install must be idempotent")
        uninstall_result = uninstall_hooks(hook_target)
        if uninstall_result.get("status") != "PASS":
            failures.append("hook uninstall must pass")
        if START_MARKER_PREFIX in existing.read_text(encoding="utf-8") or "foreign-hook" not in existing.read_text(encoding="utf-8"):
            failures.append("hook uninstall must remove only TES block")

        hooks_path_target = root / "core-hooks-path"
        hooks_path_target.mkdir()
        init_git(hooks_path_target)
        subprocess.run(
            ["git", "config", "core.hooksPath", ".githooks"],
            cwd=hooks_path_target,
            text=True,
            capture_output=True,
            check=False,
            env=isolated_git_env(),
        )
        hooks_path_install = install_hooks(hooks_path_target)
        if hooks_path_install.get("status") != "PASS":
            failures.append("core.hooksPath install must pass")
        if not (hooks_path_target / ".githooks/post-commit").exists():
            failures.append("core.hooksPath must target active hook directory")
        if (hooks_path_target / ".git/hooks/post-commit").exists():
            failures.append("core.hooksPath install must not write orphan default hook")

        if os.name != "nt":
            impossible_target = root / "impossible"
            impossible_target.mkdir()
            init_git(impossible_target)
            subprocess.run(
                ["git", "config", "core.hooksPath", r"C:\hooks"],
                cwd=impossible_target,
                text=True,
                capture_output=True,
                check=False,
                env=isolated_git_env(),
            )
            impossible = install_hooks(impossible_target)
            if impossible.get("status") != "BLOCKED":
                failures.append("Windows-style core.hooksPath on POSIX must fail safely")

        queue_target = root / "queue"
        queue_target.mkdir()
        init_git(queue_target)
        commit_file(queue_target, "README.md", "# One\n", "one")
        ensure_runtime(queue_target)
        acquire_lock(queue_target, wait=False, timeout=0)
        try:
            first_queue = capture(queue_target, "post-commit", no_background=True)
            commit_file(queue_target, "docs/architecture/CHANGE.md", "# Change\n", "two")
            second_queue = capture(queue_target, "post-commit", no_background=True)
        finally:
            release_lock(queue_target)
        if first_queue.get("status") != "QUEUED" or second_queue.get("status") != "QUEUED":
            failures.append("locked post-commit captures must queue pending events")
        drain_result = drain(queue_target, background=False)
        queue_audit = audit(queue_target)
        if drain_result.get("status") != "PASS" or queue_audit.get("events", 0) < 2:
            failures.append("drain must preserve two locked post-commit events")
        duplicate_event = build_event(queue_target, "manual-drain")
        append_pending(queue_target, duplicate_event)
        append_pending(queue_target, duplicate_event)
        pending_records, _ = read_jsonl(queue_target / PENDING_FILE)
        if len(pending_records) != 1:
            failures.append("pending queue must deduplicate identical event fingerprints")
        release_lock(queue_target)

        boundary_target = root / "boundary"
        boundary_target.mkdir()
        init_git(boundary_target)
        install_hooks(boundary_target)
        copy_installed_git_tap_helpers(boundary_target)
        before = docs_snapshot(boundary_target)
        commit_file(boundary_target, "docs/architecture/CORTEX-GIT-TAP-CONTRACT.md", "# Contract\n", "contract")
        hook_path = boundary_target / ".git/hooks/post-commit"
        hook_run = subprocess.run([str(hook_path)], cwd=boundary_target, text=True, capture_output=True, check=False)
        if hook_run.returncode != 0:
            failures.append("post-commit hook must not block Git command path")
        reflect_result = reflect_proposals(boundary_target)
        after = docs_snapshot(boundary_target)
        if reflect_result.get("status") != "PASS" or reflect_result.get("proposals", 0) < 1:
            failures.append("reflect-proposals must create local proposal for memory-worthy event")
        if before.keys() - after.keys():
            failures.append("hook-triggered path must not remove docs/**")
        if before:
            for path, digest in before.items():
                if after.get(path) != digest:
                    failures.append("hook-triggered path must not modify existing docs/**")
                    break

        curation_target = root / "curation-loop"
        curation_target.mkdir()
        init_git(curation_target)
        cortex_helper = load_cortex_helper()
        cortex_helper.init(curation_target)
        subprocess.run(
            ["git", "add", "docs"],
            cwd=curation_target,
            text=True,
            capture_output=True,
            check=False,
            env=isolated_git_env(),
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", "baseline cortex"],
            cwd=curation_target,
            text=True,
            capture_output=True,
            check=False,
            env=isolated_git_env(),
        )
        install_hooks(curation_target)
        copy_installed_git_tap_helpers(curation_target)
        previous_no_background = os.environ.get("TES_CORTEX_GIT_TAP_NO_BACKGROUND")
        os.environ["TES_CORTEX_GIT_TAP_NO_BACKGROUND"] = "1"
        try:
            commit_file(
                curation_target,
                "docs/architecture/CORTEX-GIT-TAP-CONTRACT.md",
                "# Cortex Git Tap Contract\n\nExplicit proposal curation is required before durable memory apply.\n",
                "contract change",
            )
        finally:
            if previous_no_background is None:
                os.environ.pop("TES_CORTEX_GIT_TAP_NO_BACKGROUND", None)
            else:
                os.environ["TES_CORTEX_GIT_TAP_NO_BACKGROUND"] = previous_no_background
        docs_before_plan = docs_snapshot(curation_target)
        curation_reflect = reflect_proposals(curation_target)
        curation_plan = curate_proposals_plan(curation_target)
        docs_after_plan = docs_snapshot(curation_target)
        curation_proposals, curation_proposal_failures = read_proposals(curation_target / PROPOSALS_FILE)
        selected_proposal = next(
            (proposal for proposal in curation_proposals if proposal.get("decision_state") == "NEEDS_CURATION"),
            None,
        )
        if curation_reflect.get("status") != "PASS" or curation_reflect.get("proposals", 0) < 1:
            failures.append("Git Tap curation loop must produce reviewable runtime proposals")
        if curation_plan.get("status") != "PASS" or curation_plan.get("writes") != []:
            failures.append("Git Tap curate-plan must be deterministic and no-write")
        if docs_before_plan != docs_after_plan:
            failures.append("Git Tap reflect/curate-plan must not write docs/**")
        if curation_proposal_failures:
            failures.extend(curation_proposal_failures)
        if selected_proposal is None:
            failures.append("Git Tap curation loop must include a NEEDS_CURATION proposal")
        else:
            fingerprint = str(selected_proposal["event_fingerprint"])
            hook_env_previous = os.environ.get("TES_CORTEX_GIT_TAP_HOOK")
            os.environ["TES_CORTEX_GIT_TAP_HOOK"] = "1"
            try:
                hook_apply = apply_proposal(
                    curation_target,
                    event_fingerprint=fingerprint,
                    cell="git-tap-hook-blocked",
                    claim="Hook execution must not apply Cortex memory.",
                    summary=None,
                    authorized=True,
                    update_existing=False,
                )
            finally:
                if hook_env_previous is None:
                    os.environ.pop("TES_CORTEX_GIT_TAP_HOOK", None)
                else:
                    os.environ["TES_CORTEX_GIT_TAP_HOOK"] = hook_env_previous
            unauthorized_apply = apply_proposal(
                curation_target,
                event_fingerprint=fingerprint,
                cell="git-tap-unauthorized",
                claim="Unauthorized proposal apply must not write Cortex memory.",
                summary=None,
                authorized=False,
                update_existing=False,
            )
            docs_before_apply = docs_snapshot(curation_target)
            explicit_apply = apply_proposal(
                curation_target,
                event_fingerprint=fingerprint,
                cell="git-tap-proposal-curation-loop",
                claim="Cortex Git Tap proposals require explicit apply before durable memory writes.",
                summary="Git Tap proposal curation requires explicit apply.",
                authorized=True,
                update_existing=False,
            )
            docs_after_apply = docs_snapshot(curation_target)
            recall_after_apply = cortex_helper.recall(curation_target, "explicit apply durable memory writes", 5)
            apply_writes = [str(path) for path in explicit_apply.get("writes", [])]
            if hook_apply.get("status") != "BLOCKED":
                failures.append("hook-triggered execution must be blocked from apply-proposal")
            if unauthorized_apply.get("status") != "NEEDS_AUTH":
                failures.append("apply-proposal must require explicit --yes authorization")
            if explicit_apply.get("status") != "PASS":
                failures.append("explicit apply-proposal must create curated Cortex memory")
                failures.extend(str(item) for item in explicit_apply.get("failures", []))
            if not docs_after_apply.keys() - docs_before_apply.keys():
                failures.append("explicit apply-proposal must write approved Cortex memory docs")
            if any(
                not path.startswith(
                    (
                        "docs/agents/cortex/sources/",
                        "docs/agents/cortex/cells/",
                        "docs/agents/cortex/MAP.md",
                        "docs/agents/cortex/LINKS.md",
                        "docs/agents/cortex/TRAIL.md",
                    )
                )
                for path in apply_writes
            ):
                failures.append("explicit apply-proposal must only report approved Cortex memory writes")
            source_paths = [path for path in apply_writes if path.startswith("docs/agents/cortex/sources/git-tap/")]
            if not source_paths:
                failures.append("explicit apply-proposal must retain sanitized Git Tap source evidence")
            else:
                source_text = (curation_target / source_paths[0]).read_text(encoding="utf-8")
                if "diff --git" in source_text or "/Users/" in source_text or "token=" in source_text:
                    failures.append("Git Tap proposal evidence must stay sanitized")
            if recall_after_apply.get("status") != "PASS" or recall_after_apply.get("backend") != "sqlite-fts5":
                failures.append("runtime recall must use the derived recall index after explicit apply")
            if not any(
                str(match.get("path", "")).endswith("cells/git-tap-proposal-curation-loop.md")
                for match in recall_after_apply.get("matches", [])
            ):
                failures.append("runtime recall must surface the curated Git Tap memory cell")
            if "apply" in hook_block(curation_target, "post-commit"):
                failures.append("Git Tap hook template must remain proposal-only and not call apply")

        policy_target = root / "policy-auto-promote"
        policy_target.mkdir()
        init_git(policy_target)
        policy_cortex = load_cortex_helper()
        policy_cortex.init(policy_target)
        tes_codex_policy.materialize_policy(policy_target)
        subprocess.run(
            ["git", "add", "docs", ".tes/tes-codex.md"],
            cwd=policy_target,
            text=True,
            capture_output=True,
            check=False,
            env=isolated_git_env(),
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", "baseline policy"],
            cwd=policy_target,
            text=True,
            capture_output=True,
            check=False,
            env=isolated_git_env(),
        )
        install_hooks(policy_target)
        copy_installed_git_tap_helpers(policy_target)
        previous_no_background = os.environ.get("TES_CORTEX_GIT_TAP_NO_BACKGROUND")
        os.environ["TES_CORTEX_GIT_TAP_NO_BACKGROUND"] = "1"
        try:
            commit_file(
                policy_target,
                "docs/agents/POLICY-RUNTIME.md",
                "# Policy Runtime Memory\n\nmarker policy-runtime-green-249\n",
                "policy memory",
            )
        finally:
            if previous_no_background is None:
                os.environ.pop("TES_CORTEX_GIT_TAP_NO_BACKGROUND", None)
            else:
                os.environ["TES_CORTEX_GIT_TAP_NO_BACKGROUND"] = previous_no_background
        policy_reflect = reflect_proposals(policy_target)
        policy_proposals, policy_proposal_failures = read_proposals(policy_target / PROPOSALS_FILE)
        policy_selected = next((proposal for proposal in policy_proposals if proposal.get("decision_state") == "AUTO_PROMOTED"), None)
        if policy_reflect.get("status") != "PASS" or policy_selected is None:
            failures.append("policy Git Tap loop must create an AUTO_PROMOTED proposal for docs/agents/**")
        if policy_proposal_failures:
            failures.extend(policy_proposal_failures)
        hook_env_previous = os.environ.get("TES_CORTEX_GIT_TAP_HOOK")
        os.environ["TES_CORTEX_GIT_TAP_HOOK"] = "1"
        try:
            policy_hook_auto = auto_promote(policy_target)
        finally:
            if hook_env_previous is None:
                os.environ.pop("TES_CORTEX_GIT_TAP_HOOK", None)
            else:
                os.environ["TES_CORTEX_GIT_TAP_HOOK"] = hook_env_previous
        if policy_hook_auto.get("status") != "BLOCKED_IN_HOOK":
            failures.append("policy auto-promote must block inside hook execution")
        policy_auto = auto_promote(policy_target)
        policy_recall = policy_cortex.recall(policy_target, "policy-runtime-green-249", 5)
        if policy_auto.get("status") != "PASS":
            failures.append("policy auto-promote must pass outside hook execution")
            failures.extend(str(item) for item in policy_auto.get("failures", []))
        if len(policy_auto.get("promoted", [])) != 1:
            failures.append("policy auto-promote must dedupe repeated pre/post commit proposals")
        if not any("policy-runtime-green-249" in json.dumps(match, ensure_ascii=False) for match in policy_recall.get("matches", [])):
            failures.append("policy auto-promoted memory must be recallable")

        skip_target = root / "skip"
        skip_target.mkdir()
        init_git(skip_target)
        commit_file(skip_target, "README.md", "# Base\n", "base")
        git_path(skip_target, "MERGE_HEAD").write_text("0" * 40 + "\n", encoding="utf-8")
        skipped = capture(skip_target, "post-commit", no_background=True)
        if skipped.get("status") != "SKIP":
            failures.append("merge/rebase/cherry-pick state must skip capture")
        git_path(skip_target, "MERGE_HEAD").unlink(missing_ok=True)
        file_checkout = capture(skip_target, "post-checkout", head_before="a", head_after="b", checkout_flag="0", no_background=True)
        if file_checkout.get("status") != "SKIP":
            failures.append("post-checkout file checkout must skip capture")
        if should_skip_capture(skip_target, "post-commit", None, [".tes/runtime/cortex/git-tap/events.jsonl"]) is None:
            failures.append("self-generated runtime paths must skip capture loops")

        log_target = root / "log"
        log_target.mkdir()
        init_git(log_target)
        log_line(log_target, "first")
        size_one = (log_target / LOG_FILE).stat().st_size
        log_line(log_target, "second")
        size_two = (log_target / LOG_FILE).stat().st_size
        if size_two <= size_one:
            failures.append("logs must append instead of overwriting")

        helper_missing_block = hook_block(hook_target, "post-commit")
        if "TES Cortex Git Tap runtime missing" not in helper_missing_block:
            failures.append("hook template must fail loud to log when runtime helper is missing")

    status = "PASS" if not failures else "FAIL"
    return {"version": VERSION, "schema": SCHEMA, "status": status, "failures": failures}


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cortex Git Tap runtime")
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    capture_parser = subparsers.add_parser("capture")
    capture_parser.add_argument("--target", type=Path, default=Path.cwd())
    capture_parser.add_argument("--event", required=True, choices=sorted(EVENTS))
    capture_parser.add_argument("--head-before", default="")
    capture_parser.add_argument("--head-after", default="")
    capture_parser.add_argument("--checkout-flag")
    capture_parser.add_argument("--no-background", action="store_true")

    drain_parser = subparsers.add_parser("drain")
    drain_parser.add_argument("--target", type=Path, default=Path.cwd())
    drain_parser.add_argument("--background", action="store_true")
    drain_parser.add_argument("--timeout", type=float, default=LOCK_TIMEOUT_SECONDS)

    install_parser = subparsers.add_parser("install-hooks")
    install_parser.add_argument("--target", type=Path, default=Path.cwd())
    install_parser.add_argument("--dry-run", action="store_true")

    uninstall_parser = subparsers.add_parser("uninstall-hooks")
    uninstall_parser.add_argument("--target", type=Path, default=Path.cwd())
    uninstall_parser.add_argument("--dry-run", action="store_true")

    audit_parser = subparsers.add_parser("audit")
    audit_parser.add_argument("--target", type=Path, default=Path.cwd())

    reflect_parser = subparsers.add_parser("reflect-proposals")
    reflect_parser.add_argument("--target", type=Path, default=Path.cwd())

    curate_parser = subparsers.add_parser("curate-plan")
    curate_parser.add_argument("--target", type=Path, default=Path.cwd())

    auto_promote_parser = subparsers.add_parser("auto-promote")
    auto_promote_parser.add_argument("--target", type=Path, default=Path.cwd())

    apply_parser = subparsers.add_parser("apply-proposal")
    apply_parser.add_argument("--target", type=Path, default=Path.cwd())
    apply_parser.add_argument("--event-fingerprint", required=True)
    apply_parser.add_argument("--cell", required=True)
    apply_parser.add_argument("--claim", required=True)
    apply_parser.add_argument("--summary")
    apply_parser.add_argument("--yes", action="store_true")
    apply_parser.add_argument("--update", action="store_true")

    validate_parser = subparsers.add_parser("validate-event")
    validate_parser.add_argument("--event-json", required=True)

    args = parser.parse_args(argv)
    if args.self_test:
        result = self_test()
        print_json(result)
        print("[cortex-git-tap:self-test] " + result["status"])
        return 0 if result["status"] == "PASS" else 1
    if args.command == "capture":
        result = capture(
            args.target,
            args.event,
            head_before=args.head_before,
            head_after=args.head_after,
            checkout_flag=args.checkout_flag,
            no_background=args.no_background,
        )
    elif args.command == "drain":
        result = drain(args.target, background=args.background, timeout=args.timeout)
    elif args.command == "install-hooks":
        result = install_hooks(args.target, dry_run=args.dry_run)
    elif args.command == "uninstall-hooks":
        result = uninstall_hooks(args.target, dry_run=args.dry_run)
    elif args.command == "audit":
        result = audit(args.target)
    elif args.command == "reflect-proposals":
        result = reflect_proposals(args.target)
    elif args.command == "curate-plan":
        result = curate_proposals_plan(args.target)
    elif args.command == "auto-promote":
        result = auto_promote(args.target)
    elif args.command == "apply-proposal":
        result = apply_proposal(
            args.target,
            event_fingerprint=args.event_fingerprint,
            cell=args.cell,
            claim=args.claim,
            summary=args.summary,
            authorized=args.yes,
            update_existing=args.update,
        )
    elif args.command == "validate-event":
        try:
            payload = json.loads(args.event_json)
        except json.JSONDecodeError as exc:
            result = {"version": VERSION, "status": "FAIL", "failures": [str(exc)]}
        else:
            result = validate_event_payload(payload if isinstance(payload, dict) else {})
    else:
        parser.print_help()
        return 1
    print_json(result)
    status = str(result.get("status") or "")
    return 0 if status in {"PASS", "SKIP", "QUEUED", "NEEDS_CANARY_EVIDENCE"} else 1


if __name__ == "__main__":
    sys.exit(main())
