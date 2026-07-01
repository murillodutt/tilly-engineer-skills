#!/usr/bin/env python3
"""Runtime-signal oracle for host transcript canaries.

The oracle reads local Claude transcript JSONL, hook ledgers, and declared
artifacts, then emits only sanitized counts, hashes, booleans, statuses, and
failure classes. Raw prompts, tool inputs/results, and transcript lines stay
local and are never copied into the result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Any


SCHEMA = "tes-runtime-signal-audit@1"
SKILL_CONTRACT = "tes.host_transcript_canary@0.1.6"
MUTATION_TOOLS = {"Write", "Edit", "MultiEdit", "Agent"}
DIRECT_LOOKUP_TOOLS = {"Read", "Grep", "Glob", "LS"}
SHELL_LOOKUP_RE = re.compile(r"\b(cat|rg|grep|find|ls|sed|awk|python|sqlite)\b")
RECALL_RE = re.compile(r"\bcortex\.py\s+(recall|read-cell)\b")
DEFAULT_MEMORY_PATHS = ("docs/agents/cortex", ".tes/cortex")
REQUIRED_TEMPLATE_HEADINGS = (
    "## Command",
    "## Mode",
    "## Target",
    "## Transcript",
    "## Ledger Runtime Signal",
    "## First Artifact Mutation",
    "## Artifact Marker",
    "## Contamination",
    "## Related Gates",
    "## Residual Blockers",
    "## Decision",
    "## Forbidden Content",
)
FORBIDDEN_TEMPLATE_PLACEHOLDERS = (
    "<raw-prompt",
    "<raw-transcript",
    "<tool-input",
    "<tool-result",
    "<subagent-message",
    "<secret",
    "<credential",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def claude_project_slug_candidates(target: Path) -> list[str]:
    resolved = str(target.expanduser().resolve())
    candidates = [
        resolved.replace("/", "-"),
        re.sub(r"[^A-Za-z0-9_-]+", "-", resolved),
    ]
    unique: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def latest_transcript(project_dir: Path) -> Path | None:
    candidates = [path for path in project_dir.glob("*.jsonl") if path.is_file()] if project_dir.is_dir() else []
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name)) if candidates else None


def resolve_transcript(
    *, target: Path, session_id: str | None, projects_root: Path
) -> tuple[Path | None, dict[str, Any]]:
    projects_root = projects_root.expanduser().resolve()
    project_dirs = [projects_root / slug for slug in claude_project_slug_candidates(target)]
    if session_id:
        candidates = [project_dir / f"{session_id}.jsonl" for project_dir in project_dirs]
        resolved = next((candidate for candidate in candidates if candidate.is_file()), candidates[0])
        return resolved, {
            "mode": "target-session",
            "session_id": session_id,
            "project_dir": str(resolved.parent),
            "projects_root": str(projects_root),
        }

    latest = [candidate for project_dir in project_dirs if (candidate := latest_transcript(project_dir))]
    resolved = max(latest, key=lambda path: (path.stat().st_mtime_ns, path.name)) if latest else None
    return resolved, {
        "mode": "target-latest",
        "session_id": resolved.stem if resolved else None,
        "project_dir": str(resolved.parent if resolved else project_dirs[0]),
        "projects_root": str(projects_root),
    }


def load_jsonl(path: Path | None) -> tuple[list[dict[str, Any]], list[int]]:
    if path is None or not path.is_file():
        return [], []
    events: list[dict[str, Any]] = []
    invalid: list[int] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if not raw_line.strip():
                continue
            try:
                event = json.loads(raw_line)
            except json.JSONDecodeError:
                invalid.append(line_number)
                continue
            if isinstance(event, dict):
                events.append(event)
            else:
                invalid.append(line_number)
    return events, invalid


def content_blocks(event: dict[str, Any]) -> list[dict[str, Any]]:
    message = event.get("message")
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [block for block in content if isinstance(block, dict)]
    return []


def compact_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def tool_uses(events: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any]]]:
    uses: list[tuple[int, dict[str, Any]]] = []
    for index, event in enumerate(events, start=1):
        for block in content_blocks(event):
            if block.get("type") == "tool_use":
                uses.append((index, block))
    return uses


def count_tool_results(events: list[dict[str, Any]]) -> int:
    return sum(1 for event in events for block in content_blocks(event) if block.get("type") == "tool_result")


def load_subagent_events(transcript_path: Path | None) -> tuple[int, list[dict[str, Any]], int]:
    if transcript_path is None:
        return 0, [], 0
    subagents_dir = transcript_path.parent / transcript_path.stem / "subagents"
    if not subagents_dir.is_dir():
        return 0, [], 0
    all_events: list[dict[str, Any]] = []
    invalid_count = 0
    count = 0
    for path in sorted(subagents_dir.glob("*.jsonl")):
        if not path.is_file():
            continue
        count += 1
        events, invalid = load_jsonl(path)
        all_events.extend(events)
        invalid_count += len(invalid)
    return count, all_events, invalid_count


def has_memory_path(text: str, memory_paths: list[str]) -> bool:
    lowered = text.lower()
    return any(path.lower() in lowered for path in memory_paths)


def contamination(
    *,
    main_events: list[dict[str, Any]],
    subagent_events: list[dict[str, Any]],
    memory_paths: list[str],
    expected_marker: str,
) -> tuple[list[dict[str, Any]], int]:
    manual: list[dict[str, Any]] = []
    benign_marker_mentions = 0
    for source, events in (("main", main_events), ("subagent", subagent_events)):
        for event_index, block in tool_uses(events):
            name = str(block.get("name") or "")
            payload = compact_json(block.get("input", {}))
            if name in MUTATION_TOOLS and expected_marker and expected_marker in payload:
                benign_marker_mentions += 1
            if name in DIRECT_LOOKUP_TOOLS and has_memory_path(payload, memory_paths):
                manual.append({"source": source, "event_index": event_index, "tool": name})
            elif name == "Bash" and (
                RECALL_RE.search(payload) or (SHELL_LOOKUP_RE.search(payload) and has_memory_path(payload, memory_paths))
            ):
                manual.append({"source": source, "event_index": event_index, "tool": name})
    return manual, benign_marker_mentions


def row_session(row: dict[str, Any]) -> str | None:
    for key in ("session_id", "sessionId", "session", "transcript_session_id"):
        value = row.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def row_has_runtime_context(row: dict[str, Any]) -> bool:
    text = compact_json(row).lower()
    return (
        row.get("cortex_context_emitted") is True
        or row.get("runtime_context_emitted") is True
        or "cortex_context_emitted:true" in text
        or "runtime_context_emitted:true" in text
        or "runtime_context" in text
    )


def ledger_summary(target: Path, session_id: str | None, expected_marker: str) -> dict[str, int]:
    ledger = target / ".tes" / "runtime" / "hooks" / "executed.jsonl"
    rows = host_real = runtime_context = marker = 0
    if not ledger.is_file():
        return {
            "ledger_rows": 0,
            "host_real_rows": 0,
            "runtime_context_rows": 0,
            "marker_rows": 0,
        }
    with ledger.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            if not raw_line.strip():
                continue
            try:
                row = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            current_session = row_session(row)
            if session_id and current_session and current_session != session_id:
                continue
            rows += 1
            row_text = compact_json(row).lower()
            if row.get("host_real") is True or "host-real" in row_text or "host_real" in row_text:
                host_real += 1
            if row_has_runtime_context(row):
                runtime_context += 1
            if expected_marker and expected_marker in compact_json(row):
                marker += 1
    return {
        "ledger_rows": rows,
        "host_real_rows": host_real,
        "runtime_context_rows": runtime_context,
        "marker_rows": marker,
    }


def artifact_checks(target: Path, artifacts: list[str], expected_marker: str) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for artifact in artifacts:
        path = (target / artifact).resolve()
        exists = path.is_file()
        marker_present = False
        digest = None
        if exists:
            digest = sha256_file(path)
            marker_present = expected_marker in path.read_text(encoding="utf-8", errors="replace")
        checks.append(
            {
                "path": artifact,
                "exists": exists,
                "sha256": digest,
                "marker_present": marker_present,
            }
        )
    return checks


def first_mutation(
    *, events: list[dict[str, Any]], artifacts: list[str], expected_marker: str
) -> dict[str, Any]:
    for event_index, block in tool_uses(events):
        name = str(block.get("name") or "")
        if name not in MUTATION_TOOLS:
            continue
        payload = compact_json(block.get("input", {}))
        matched_artifact = next((artifact for artifact in artifacts if artifact in payload), None)
        if artifacts and not matched_artifact:
            continue
        has_context = (
            "cortex_context_emitted" in payload
            or "runtime_context" in payload
            or "hook injected" in payload.lower()
        )
        return {
            "found": True,
            "event_index": event_index,
            "tool": name,
            "artifact": matched_artifact,
            "runtime_context_present": has_context,
            "marker_present": bool(expected_marker and expected_marker in payload),
        }
    return {
        "found": False,
        "event_index": None,
        "tool": None,
        "artifact": None,
        "runtime_context_present": False,
        "marker_present": False,
    }


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    target = args.target.expanduser().resolve()
    transcript_path, resolution = resolve_transcript(
        target=target,
        session_id=args.session_id,
        projects_root=args.projects_root,
    )
    session_id = args.session_id or resolution.get("session_id")
    events, invalid_lines = load_jsonl(transcript_path)
    subagent_count, subagent_events, subagent_invalid_count = load_subagent_events(transcript_path)
    uses = tool_uses(events)
    tool_result_count = count_tool_results(events)
    manual_lookup, benign_mentions = contamination(
        main_events=events,
        subagent_events=subagent_events,
        memory_paths=args.memory_path or list(DEFAULT_MEMORY_PATHS),
        expected_marker=args.expected_marker,
    )
    ledger = ledger_summary(target, str(session_id) if session_id else None, args.expected_marker)
    checks = artifact_checks(target, args.artifact or [], args.expected_marker)
    mutation = first_mutation(events=events, artifacts=args.artifact or [], expected_marker=args.expected_marker)

    blockers: list[str] = []
    failure_class: str | None = None
    status = "PASS"
    transcript_status = "PASS"

    if transcript_path is None or not transcript_path.is_file():
        transcript_status = "NEEDS_EVIDENCE"
        blockers.append("no transcript resolved")
        failure_class = failure_class or "transcript_gap"
    if invalid_lines or subagent_invalid_count:
        transcript_status = "FAIL"
        blockers.append("transcript JSONL is malformed")
        failure_class = failure_class or "transcript_gap"
    if not any(event.get("type") == "user" for event in events):
        transcript_status = "NEEDS_EVIDENCE"
        blockers.append("transcript has no user events")
        failure_class = failure_class or "transcript_gap"
    if not any(event.get("type") == "assistant" for event in events):
        transcript_status = "NEEDS_EVIDENCE"
        blockers.append("transcript has no assistant events")
        failure_class = failure_class or "transcript_gap"
    if not uses:
        blockers.append("transcript has no tool_use blocks")
        failure_class = failure_class or "transcript_gap"
    if args.fresh_after and transcript_path and transcript_path.is_file() and transcript_path.stat().st_mtime < args.fresh_after:
        blockers.append("transcript is older than required freshness boundary")
        failure_class = failure_class or "transcript_gap"
    if ledger["host_real_rows"] == 0:
        blockers.append("missing same-session host-real ledger row")
        failure_class = failure_class or "evidence_gap"
    if ledger["runtime_context_rows"] == 0:
        blockers.append("missing same-session runtime context ledger row")
        failure_class = failure_class or "evidence_gap"
    if args.artifact and not checks:
        blockers.append("no artifact checks were produced")
        failure_class = failure_class or "evidence_gap"
    if any(not check["exists"] for check in checks):
        blockers.append("declared artifact is missing")
        failure_class = failure_class or "product_gap"
    if checks and not all(check["marker_present"] for check in checks):
        blockers.append("expected marker missing from declared artifact")
        failure_class = failure_class or "product_gap"
    if args.require_first_mutation_context and not mutation["runtime_context_present"]:
        blockers.append("first artifact mutation lacks runtime context signal")
        failure_class = failure_class or "product_gap"
    if manual_lookup:
        blockers.append("forbidden manual memory lookup detected")
        failure_class = "false_green"

    if invalid_lines or subagent_invalid_count or manual_lookup:
        status = "FAIL"
    elif blockers:
        status = "NEEDS_EVIDENCE"
    if transcript_status == "FAIL":
        status = "FAIL"
    elif transcript_status == "NEEDS_EVIDENCE" and status == "PASS":
        status = "NEEDS_EVIDENCE"

    return {
        "schema": SCHEMA,
        "skill_contract": SKILL_CONTRACT,
        "status": status,
        "target": str(target),
        "session_id": session_id,
        "transcript_path": str(transcript_path) if transcript_path else None,
        "transcript_sha256": sha256_file(transcript_path) if transcript_path and transcript_path.is_file() else None,
        "tool_use_count": len(uses),
        "tool_result_count": tool_result_count,
        "subagent_count": subagent_count,
        "ledger_rows": ledger["ledger_rows"],
        "host_real_rows": ledger["host_real_rows"],
        "runtime_context_rows": ledger["runtime_context_rows"],
        "marker_rows": ledger["marker_rows"],
        "artifact_checks": checks,
        "first_mutation": mutation,
        "manual_lookup_tool_uses": manual_lookup,
        "benign_marker_mentions": benign_mentions,
        "failure_class": failure_class,
        "blockers": blockers,
        "transcript_status": transcript_status,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def build_fixture(root: Path, *, marker: str, session_id: str, manual_lookup: bool = False, marker_in_artifact: bool = True) -> tuple[Path, Path]:
    target = root / "target-project"
    target.mkdir(parents=True)
    projects_root = root / ".claude" / "projects"
    transcript = projects_root / claude_project_slug_candidates(target)[0] / f"{session_id}.jsonl"
    artifact_text = f"runtime artifact\nmarker={marker if marker_in_artifact else 'missing'}\n"
    (target / "docs").mkdir(parents=True, exist_ok=True)
    (target / "docs" / "artifact.md").write_text(artifact_text, encoding="utf-8")
    tool_blocks: list[dict[str, Any]] = []
    if manual_lookup:
        tool_blocks.append(
            {
                "type": "tool_use",
                "id": "toolu_lookup",
                "name": "Read",
                "input": {"file_path": ".tes/cortex/cells/example.json"},
            }
        )
    tool_blocks.append(
        {
            "type": "tool_use",
            "id": "toolu_write",
            "name": "Write",
            "input": {
                "file_path": "docs/artifact.md",
                "content": f"cortex_context_emitted=true\nmarker={marker}\n",
            },
        }
    )
    write_jsonl(
        transcript,
        [
            {"type": "user", "sessionId": session_id, "message": {"role": "user", "content": "sanitized"}},
            {
                "type": "assistant",
                "sessionId": session_id,
                "message": {"role": "assistant", "content": tool_blocks},
            },
            {
                "type": "user",
                "sessionId": session_id,
                "message": {"role": "user", "content": [{"type": "tool_result", "content": "sanitized"}]},
            },
        ],
    )
    write_jsonl(
        target / ".tes" / "runtime" / "hooks" / "executed.jsonl",
        [
            {
                "schema": "tes-runtime-hook@fixture",
                "session_id": session_id,
                "provenance": "host-real",
                "host_real": True,
                "cortex_context_emitted": True,
                "marker": marker,
            }
        ],
    )
    return target, projects_root


def template_lint() -> list[str]:
    template = Path(__file__).resolve().parents[1] / "templates" / "runtime-signal-report.template.md"
    if not template.is_file():
        return ["runtime signal report template is missing"]
    text = template.read_text(encoding="utf-8")
    failures = [f"template missing heading: {heading}" for heading in REQUIRED_TEMPLATE_HEADINGS if heading not in text]
    failures.extend(
        f"template contains forbidden raw-content placeholder: {placeholder}"
        for placeholder in FORBIDDEN_TEMPLATE_PLACEHOLDERS
        if placeholder in text.lower()
    )
    return failures


def self_test(repo: Path | None) -> dict[str, Any]:
    failures: list[str] = []
    marker = "TES_SAFE_MARKER_RUNTIME_SIGNAL"
    session_id = "11111111-2222-3333-4444-555555555555"
    with tempfile.TemporaryDirectory(prefix="tes-runtime-signal-") as tmp:
        root = Path(tmp)
        target, projects_root = build_fixture(root / "pass", marker=marker, session_id=session_id)
        base = argparse.Namespace(
            target=target,
            session_id=session_id,
            latest=False,
            projects_root=projects_root,
            expected_marker=marker,
            artifact=["docs/artifact.md"],
            require_first_mutation_context=True,
            memory_path=list(DEFAULT_MEMORY_PATHS),
            fresh_after=None,
        )
        passed = evaluate(base)
        if passed["status"] != "PASS":
            failures.append(f"pass fixture should PASS, got {passed['status']}")
        if marker in json.dumps(passed.get("manual_lookup_tool_uses"), sort_keys=True):
            failures.append("manual lookup summary leaked marker text")

        missing_ledger_target, missing_ledger_projects = build_fixture(root / "missing-ledger", marker=marker, session_id=session_id)
        (missing_ledger_target / ".tes" / "runtime" / "hooks" / "executed.jsonl").unlink()
        missing_ledger = evaluate(
            argparse.Namespace(**{**vars(base), "target": missing_ledger_target, "projects_root": missing_ledger_projects})
        )
        if missing_ledger["status"] != "NEEDS_EVIDENCE" or missing_ledger["failure_class"] != "evidence_gap":
            failures.append("missing ledger fixture should be NEEDS_EVIDENCE/evidence_gap")

        missing_marker_target, missing_marker_projects = build_fixture(
            root / "missing-marker", marker=marker, session_id=session_id, marker_in_artifact=False
        )
        missing_marker = evaluate(
            argparse.Namespace(**{**vars(base), "target": missing_marker_target, "projects_root": missing_marker_projects})
        )
        if missing_marker["status"] != "NEEDS_EVIDENCE" or missing_marker["failure_class"] != "product_gap":
            failures.append("missing marker fixture should be NEEDS_EVIDENCE/product_gap")

        stale_target, stale_projects = build_fixture(root / "stale", marker=marker, session_id=session_id)
        stale_transcript = stale_projects / claude_project_slug_candidates(stale_target)[0] / f"{session_id}.jsonl"
        old = time.time() - 3600
        stale_transcript.touch()
        os.utime(stale_transcript, (old, old))
        stale = evaluate(
            argparse.Namespace(
                **{
                    **vars(base),
                    "target": stale_target,
                    "projects_root": stale_projects,
                    "fresh_after": time.time() - 60,
                }
            )
        )
        if stale["status"] != "NEEDS_EVIDENCE" or stale["failure_class"] != "transcript_gap":
            failures.append("stale transcript fixture should be NEEDS_EVIDENCE/transcript_gap")

        manual_target, manual_projects = build_fixture(root / "manual", marker=marker, session_id=session_id, manual_lookup=True)
        manual = evaluate(
            argparse.Namespace(**{**vars(base), "target": manual_target, "projects_root": manual_projects})
        )
        if manual["status"] != "FAIL" or manual["failure_class"] != "false_green":
            failures.append("manual lookup fixture should FAIL/false_green")
        if manual["benign_marker_mentions"] == 0:
            failures.append("benign marker reuse should still be counted")

    failures.extend(template_lint())
    return {
        "schema": SCHEMA,
        "skill_contract": SKILL_CONTRACT,
        "status": "PASS" if not failures else "FAIL",
        "coverage": [
            "pass",
            "missing ledger",
            "missing marker",
            "stale transcript",
            "manual lookup failure",
            "template lint",
        ],
        "failures": failures,
        "repo": str(repo) if repo else None,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit host-real runtime signal evidence without emitting raw transcript content.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo", type=Path, help="TES package root; accepted for validation harness parity.")
    parser.add_argument("--target", type=Path, help="Target project to audit.")
    parser.add_argument("--session-id", help="Claude Code session id under the target slug.")
    parser.add_argument("--latest", action="store_true", help="Use latest target transcript when --session-id is omitted.")
    parser.add_argument("--projects-root", type=Path, default=Path.home() / ".claude" / "projects")
    parser.add_argument("--expected-marker", help="Safe runtime marker expected in the artifact.")
    parser.add_argument("--artifact", action="append", default=[], help="Relative artifact path to check; repeatable.")
    parser.add_argument("--require-first-mutation-context", action="store_true")
    parser.add_argument("--memory-path", action="append", default=list(DEFAULT_MEMORY_PATHS))
    parser.add_argument("--fresh-after", type=float, help="Unix timestamp; transcript must be newer than this boundary.")
    parser.add_argument("--json-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        result = self_test(args.repo.expanduser().resolve() if args.repo else None)
    else:
        if not args.target:
            parser.error("--target is required unless --self-test is set")
        if not args.session_id and not args.latest:
            parser.error("provide --session-id or --latest")
        if not args.expected_marker:
            parser.error("--expected-marker is required")
        result = evaluate(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json_only:
        print("[runtime-signal-audit] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
