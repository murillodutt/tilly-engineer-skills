#!/usr/bin/env python3
"""Sanitized Claude Code transcript evidence oracle for canary replay.

This is a canary sidecar: it proves that local Claude Code transcript evidence
exists and is parseable without copying prompt text, tool inputs, tool results,
or subagent metadata into tracked reports. The raw JSONL stays local; this
oracle emits only counts, SHA-256 hashes, statuses, and safe enum-like names.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


VERSION = "0.3.241"
SCHEMA = "tes-canary-transcript@1"


def counter_dict(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def claude_project_slug(target: Path) -> str:
    return str(target.expanduser().resolve()).replace("/", "-")


def latest_transcript(project_dir: Path) -> Path | None:
    if not project_dir.is_dir():
        return None
    candidates = [path for path in project_dir.glob("*.jsonl") if path.is_file()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name))


def _safe_counter_key(value: Any) -> str:
    if not isinstance(value, str) or not value:
        return "<missing>"
    return value if len(value) <= 120 else value[:117] + "..."


def summarize_transcript(path: Path) -> dict[str, Any]:
    path = path.expanduser().resolve()
    if not path.is_file():
        return {
            "status": "NEEDS_EVIDENCE",
            "path": str(path),
            "exists": False,
            "blockers": [f"transcript not found: {path}"],
        }

    top_level_types: Counter[str] = Counter()
    roles: Counter[str] = Counter()
    content_block_types: Counter[str] = Counter()
    tool_use_names: Counter[str] = Counter()
    stop_reasons: Counter[str] = Counter()
    assistant_models: Counter[str] = Counter()
    invalid_lines: list[int] = []
    session_ids: set[str] = set()
    cwd_count = 0
    git_branch_count = 0
    prompt_id_count = 0
    parsed_lines = 0

    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if not raw_line.strip():
                continue
            try:
                event = json.loads(raw_line)
            except json.JSONDecodeError:
                invalid_lines.append(line_number)
                continue
            if not isinstance(event, dict):
                invalid_lines.append(line_number)
                continue

            parsed_lines += 1
            top_level_types[_safe_counter_key(event.get("type"))] += 1
            if event.get("sessionId"):
                session_ids.add(str(event.get("sessionId")))
            if event.get("cwd"):
                cwd_count += 1
            if event.get("gitBranch"):
                git_branch_count += 1
            if event.get("promptId"):
                prompt_id_count += 1

            message = event.get("message")
            if not isinstance(message, dict):
                continue
            roles[_safe_counter_key(message.get("role"))] += 1
            if message.get("stop_reason"):
                stop_reasons[_safe_counter_key(message.get("stop_reason"))] += 1
            if message.get("model"):
                assistant_models[_safe_counter_key(message.get("model"))] += 1

            content = message.get("content")
            if isinstance(content, str):
                content_block_types["string"] += 1
                continue
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    content_block_types["<non-object>"] += 1
                    continue
                block_type = _safe_counter_key(block.get("type"))
                content_block_types[block_type] += 1
                if block_type == "tool_use":
                    tool_use_names[_safe_counter_key(block.get("name"))] += 1

    blockers: list[str] = []
    if invalid_lines:
        blockers.append(f"invalid_jsonl_lines={len(invalid_lines)}")
    if parsed_lines == 0:
        blockers.append("transcript has no parseable events")
    if top_level_types["user"] == 0:
        blockers.append("transcript has no user events")
    if top_level_types["assistant"] == 0:
        blockers.append("transcript has no assistant events")

    if invalid_lines:
        status = "FAIL"
    elif blockers:
        status = "NEEDS_EVIDENCE"
    else:
        status = "PASS"

    return {
        "status": status,
        "path": str(path),
        "exists": True,
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "parsed_lines": parsed_lines,
        "invalid_line_count": len(invalid_lines),
        "invalid_lines": invalid_lines[:20],
        "top_level_types": counter_dict(top_level_types),
        "message_roles": counter_dict(roles),
        "content_block_types": counter_dict(content_block_types),
        "tool_use_names": counter_dict(tool_use_names),
        "tool_use_count": sum(tool_use_names.values()),
        "tool_result_count": content_block_types["tool_result"],
        "assistant_models": counter_dict(assistant_models),
        "stop_reasons": counter_dict(stop_reasons),
        "session_count": len(session_ids),
        "cwd_event_count": cwd_count,
        "git_branch_event_count": git_branch_count,
        "prompt_id_count": prompt_id_count,
        "blockers": blockers,
    }


def summarize_subagents(main_transcript: Path) -> dict[str, Any]:
    subagents_dir = main_transcript.expanduser().resolve().parent / main_transcript.stem / "subagents"
    if not subagents_dir.is_dir():
        return {
            "status": "NOT_FOUND",
            "path": str(subagents_dir),
            "jsonl_count": 0,
            "meta_count": 0,
            "transcripts": [],
            "metadata": [],
            "blockers": [],
        }

    transcripts = [summarize_transcript(path) for path in sorted(subagents_dir.glob("*.jsonl")) if path.is_file()]
    metadata = [
        {
            "path": str(path.resolve()),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
        for path in sorted(subagents_dir.glob("*.meta.json"))
        if path.is_file()
    ]
    statuses = [str(item.get("status")) for item in transcripts]
    blockers = [
        f"{Path(str(item.get('path'))).name}: {blocker}"
        for item in transcripts
        for blocker in item.get("blockers", [])
    ]
    if any(status == "FAIL" for status in statuses):
        status = "FAIL"
    elif any(status == "NEEDS_EVIDENCE" for status in statuses):
        status = "NEEDS_EVIDENCE"
    else:
        status = "PASS"

    return {
        "status": status,
        "path": str(subagents_dir),
        "jsonl_count": len(transcripts),
        "meta_count": len(metadata),
        "transcripts": transcripts,
        "metadata": metadata,
        "blockers": blockers,
    }


def resolve_transcript(
    *,
    transcript: Path | None,
    target: Path | None,
    session_id: str | None,
    projects_root: Path,
) -> tuple[Path | None, dict[str, Any]]:
    projects_root = projects_root.expanduser().resolve()
    if transcript is not None:
        resolved = transcript.expanduser().resolve()
        return resolved, {
            "mode": "explicit-transcript",
            "transcript": str(resolved),
            "projects_root": str(projects_root),
        }

    if target is None:
        return None, {
            "mode": "missing-input",
            "projects_root": str(projects_root),
            "blockers": ["provide --transcript or --target"],
        }

    slug = claude_project_slug(target)
    project_dir = projects_root / slug
    if session_id:
        resolved = project_dir / f"{session_id}.jsonl"
        mode = "target-session"
    else:
        resolved = latest_transcript(project_dir)
        mode = "target-latest"

    return resolved, {
        "mode": mode,
        "target": str(target.expanduser().resolve()),
        "slug": slug,
        "project_dir": str(project_dir),
        "session_id": session_id,
        "projects_root": str(projects_root),
    }


def evaluate(
    *,
    transcript: Path | None = None,
    target: Path | None = None,
    session_id: str | None = None,
    projects_root: Path | None = None,
    include_subagents: bool = False,
    require_tool_use: bool = False,
) -> dict[str, Any]:
    root = projects_root or (Path.home() / ".claude" / "projects")
    resolved, resolution = resolve_transcript(
        transcript=transcript,
        target=target,
        session_id=session_id,
        projects_root=root,
    )

    blockers = list(resolution.get("blockers", []))
    if resolved is None:
        main = {
            "status": "NEEDS_EVIDENCE",
            "exists": False,
            "blockers": blockers or ["no transcript resolved"],
        }
    else:
        main = summarize_transcript(resolved)
        blockers.extend(main.get("blockers", []))

    if require_tool_use and int(main.get("tool_use_count", 0)) == 0:
        blockers.append("transcript has no tool_use blocks")
        if main.get("status") == "PASS":
            main["status"] = "NEEDS_EVIDENCE"
            main["blockers"] = [*main.get("blockers", []), "transcript has no tool_use blocks"]

    subagents: dict[str, Any] | None = None
    if include_subagents and resolved is not None:
        subagents = summarize_subagents(resolved)
        if subagents["status"] in {"FAIL", "NEEDS_EVIDENCE"}:
            blockers.extend(subagents.get("blockers", []))

    status = str(main.get("status", "NEEDS_EVIDENCE"))
    if subagents and subagents["status"] == "FAIL":
        status = "FAIL"
    elif subagents and subagents["status"] == "NEEDS_EVIDENCE" and status == "PASS":
        status = "NEEDS_EVIDENCE"

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "status": status,
        "resolution": resolution,
        "main": main,
        "claims": {
            "transcript_parseable": main.get("status") == "PASS",
            "raw_content_emitted": False,
            "tool_use_count": int(main.get("tool_use_count", 0)),
            "subagents_checked": include_subagents,
        },
        "blockers": blockers,
    }
    if subagents is not None:
        result["subagents"] = subagents
    return result


def _write_jsonl(path: Path, events: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(event, sort_keys=True) for event in events) + "\n", encoding="utf-8")


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    secret = "SECRET_VALUE_SHOULD_NOT_LEAK"
    session_id = "11111111-2222-3333-4444-555555555555"

    with tempfile.TemporaryDirectory(prefix="tes-transcript-oracle-") as tmp:
        root = Path(tmp)
        target = root / "target-project"
        projects_root = root / ".claude" / "projects"
        project_dir = projects_root / claude_project_slug(target)
        main_path = project_dir / f"{session_id}.jsonl"
        _write_jsonl(
            main_path,
            [
                {
                    "type": "user",
                    "sessionId": session_id,
                    "cwd": str(target),
                    "gitBranch": f"{secret}-branch",
                    "promptId": "prompt-1",
                    "message": {"role": "user", "content": f"{secret} prompt text"},
                },
                {
                    "type": "assistant",
                    "sessionId": session_id,
                    "message": {
                        "role": "assistant",
                        "model": "claude-test",
                        "stop_reason": "tool_use",
                        "content": [
                            {"type": "text", "text": f"{secret} assistant text"},
                            {
                                "type": "tool_use",
                                "id": "toolu_1",
                                "name": "Bash",
                                "input": {"cmd": f"echo {secret}"},
                            },
                        ],
                    },
                },
                {
                    "type": "user",
                    "sessionId": session_id,
                    "message": {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": "toolu_1",
                                "content": f"{secret} command output",
                            }
                        ],
                    },
                },
                {"type": "system", "sessionId": session_id, "messageCount": 3},
            ],
        )
        sub_path = project_dir / session_id / "subagents" / "agent-a.jsonl"
        _write_jsonl(
            sub_path,
            [
                {"type": "user", "sessionId": session_id, "message": {"role": "user", "content": secret}},
                {
                    "type": "assistant",
                    "sessionId": session_id,
                    "message": {
                        "role": "assistant",
                        "model": "claude-test",
                        "content": [{"type": "tool_use", "id": "toolu_2", "name": "Read", "input": {"file": secret}}],
                    },
                },
            ],
        )
        (sub_path.parent / "agent-a.meta.json").write_text(json.dumps({"secret": secret}) + "\n", encoding="utf-8")

        explicit = evaluate(transcript=main_path, include_subagents=True, require_tool_use=True)
        if explicit["status"] != "PASS":
            failures.append(f"valid explicit transcript should PASS, got {explicit['status']}")
        if explicit["main"]["tool_use_names"].get("Bash") != 1:
            failures.append("main transcript should count one Bash tool_use")
        if explicit.get("subagents", {}).get("jsonl_count") != 1:
            failures.append("subagent transcript should be counted")
        if secret in json.dumps(explicit, sort_keys=True):
            failures.append("sanitized output leaked raw transcript or metadata content")

        latest = evaluate(target=target, projects_root=projects_root, require_tool_use=True)
        if latest["status"] != "PASS":
            failures.append(f"target latest transcript should PASS, got {latest['status']}")

        no_tool_path = project_dir / "22222222-2222-3333-4444-555555555555.jsonl"
        _write_jsonl(
            no_tool_path,
            [
                {"type": "user", "message": {"role": "user", "content": "hello"}},
                {"type": "assistant", "message": {"role": "assistant", "content": "world"}},
            ],
        )
        no_tool = evaluate(transcript=no_tool_path, require_tool_use=True)
        if no_tool["status"] != "NEEDS_EVIDENCE":
            failures.append("require_tool_use should reject transcripts with no tool_use blocks")

        malformed_path = project_dir / "33333333-2222-3333-4444-555555555555.jsonl"
        malformed_path.write_text("{not-json}\n", encoding="utf-8")
        malformed = evaluate(transcript=malformed_path)
        if malformed["status"] != "FAIL":
            failures.append("malformed JSONL should FAIL")

        missing = evaluate(target=root / "missing-target", projects_root=projects_root)
        if missing["status"] != "NEEDS_EVIDENCE":
            failures.append("missing target transcript should be NEEDS_EVIDENCE")

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "coverage": "sanitized-claude-transcript-canary-evidence",
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sanitized Claude Code transcript evidence oracle.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--transcript", type=Path, help="Explicit Claude Code session JSONL transcript.")
    parser.add_argument("--target", type=Path, help="Target project whose Claude project slug should be inspected.")
    parser.add_argument("--session-id", help="Claude Code session id under the target slug.")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Use the newest target transcript. This is implied when --target is set without --session-id.",
    )
    parser.add_argument("--projects-root", type=Path, default=Path.home() / ".claude" / "projects")
    parser.add_argument("--include-subagents", action="store_true")
    parser.add_argument("--require-tool-use", action="store_true")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        result = self_test()
    else:
        result = evaluate(
            transcript=args.transcript,
            target=args.target,
            session_id=args.session_id,
            projects_root=args.projects_root,
            include_subagents=args.include_subagents,
            require_tool_use=args.require_tool_use,
        )

    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json_only:
        print("[canary-transcript] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
