#!/usr/bin/env python3
"""No-write Cortex runtime semantic core."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from typing import Any

import cortex


MESH_FILES = {
    "docs/agents/PROJECT-STATE.md",
    "docs/agents/PROJECT-ROADMAP.md",
    "docs/agents/EXECUTION-LINE.md",
    "docs/agents/QUALITY-GATES.md",
}
MESH_DECISIONS_PREFIX = "docs/agents/DECISIONS/"
ALIGN_SENTINEL = Path(".tes/runtime/tes-align.active")
ALIGN_SENTINEL_MAX_AGE_SECONDS = 4 * 60 * 60
PATCH_FILE_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$|^\*\*\* Move to: (.+)$", re.MULTILINE)
MESH_REF_RE = re.compile(
    r"docs/agents/(?:PROJECT-STATE\.md|PROJECT-ROADMAP\.md|EXECUTION-LINE\.md|"
    r"QUALITY-GATES\.md|DECISIONS/[^\s`'\"),]+)"
)
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{1,80}")
TRANSCRIPT_TAIL_BYTES = 768 * 1024
TRANSCRIPT_PROMPT_CHAR_LIMIT = 6000
QUERY_STOPWORDS = {
    "and", "are", "com", "das", "dos", "for", "from", "into", "not", "para", "por", "que",
    "the", "this", "that", "these", "those", "uma", "with",
}
QUERY_GENERIC_TERMS = {
    "agents", "any", "args", "audit", "build", "canaries", "canary", "changed", "class",
    "closeout", "command", "config", "const", "constraints", "content", "context", "dependency",
    "discover", "docs", "execute", "files", "free", "function", "glob", "goal", "grep",
    "heartbeat", "hook", "hooks", "honor", "html", "information", "injected", "local", "loop",
    "during", "maestro", "manual", "md", "message", "name", "product", "project", "prompt", "read",
    "return", "run", "scan", "script", "section", "spec", "specified", "super", "target", "tes",
    "tool", "tools", "use", "value", "verification", "window",
}
WRITE_TOOL_HINTS = {
    "bash",
    "edit",
    "multiedit",
    "notebookedit",
    "patch",
    "write",
    "apply_patch",
}

__all__ = ["evaluate_runtime_event"]


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _event_input(event: dict[str, Any]) -> dict[str, Any]:
    nested = event.get("input")
    return nested if isinstance(nested, dict) else event


def _walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_walk_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(_walk_strings(item))
        return strings
    return []


def _safe_transcript_path(payload: dict[str, Any], target: Path) -> Path | None:
    value = payload.get("transcript_path") or payload.get("transcriptPath")
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = target / path
    try:
        resolved = path.resolve()
    except OSError:
        return None
    if resolved.suffix != ".jsonl" or not resolved.is_file():
        return None
    return resolved


def _tail_text(path: Path, byte_budget: int) -> str:
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - byte_budget))
            return handle.read(byte_budget).decode("utf-8", errors="replace")
    except OSError:
        return ""


def _latest_transcript_user_prompt(payload: dict[str, Any], target: Path) -> str:
    """Read only the bounded latest human prompt from a host transcript."""
    transcript = _safe_transcript_path(payload, target)
    if transcript is None:
        return ""
    latest = ""
    for line in _tail_text(transcript, TRANSCRIPT_TAIL_BYTES).splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict) or event.get("type") != "user":
            continue
        message = event.get("message") if isinstance(event.get("message"), dict) else {}
        content = message.get("content") if isinstance(message, dict) else None
        # Tool-result arrays often carry command output; only the plain user
        # prompt string is query material for runtime recall.
        if isinstance(content, str) and content.strip():
            latest = content.strip()
    return latest[-TRANSCRIPT_PROMPT_CHAR_LIMIT:]


def _host_from_event(event: dict[str, Any], payload: dict[str, Any]) -> str:
    host = event.get("host") or payload.get("host")
    if isinstance(host, str) and host.strip():
        return host.strip()
    joined = "\n".join(_walk_strings(payload))
    if ".cursor/" in joined:
        return "cursor"
    if ".codex/" in joined:
        return "codex"
    if ".claude/" in joined:
        return "claude-code"
    hook_event = str(payload.get("hook_event_name") or event.get("event") or "")
    if hook_event and hook_event[:1].islower():
        return "cursor"
    return "unknown"


def _rel_path(value: str, target: Path) -> str | None:
    text = value.strip()
    if not text:
        return None
    mesh_match = MESH_REF_RE.search(text)
    if mesh_match:
        return mesh_match.group(0)
    path = Path(text)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(target.resolve()).as_posix()
        except ValueError:
            return None
    normalized = path.as_posix().lstrip("./")
    if normalized and not normalized.startswith("../"):
        return normalized
    return None


def _path_like_key(key: str) -> bool:
    lowered = key.lower()
    return any(part in lowered for part in ("path", "file", "filename"))


def _extract_paths(value: Any, target: Path, *, key_hint: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            paths.extend(_extract_paths(item, target, key_hint=str(key)))
        return paths
    if isinstance(value, list):
        for item in value:
            paths.extend(_extract_paths(item, target, key_hint=key_hint))
        return paths
    if not isinstance(value, str):
        return paths

    if key_hint == "command":
        for match in PATCH_FILE_RE.finditer(value):
            candidate = match.group(1) or match.group(2)
            rel_path = _rel_path(candidate, target)
            if rel_path:
                paths.append(rel_path)
    if _path_like_key(key_hint):
        rel_path = _rel_path(value, target)
        if rel_path:
            paths.append(rel_path)
    for match in MESH_REF_RE.finditer(value):
        paths.append(match.group(0))
    return paths


def _dedupe(values: list[str], limit: int | None = None) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
        if limit is not None and len(result) >= limit:
            break
    return result


def _compact_text(value: str, limit: int) -> str:
    text = " ".join(value.replace("\x00", "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _matched_memory_excerpt(target: Path, relpath: str, limit: int = 360) -> str:
    path = (target / relpath).resolve()
    cortex_root = cortex.cortex_path(target).resolve()
    try:
        path.relative_to(cortex_root)
    except ValueError:
        return ""
    if not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return _compact_text(text, limit)


def _enrich_runtime_matches(target: Path, matches: list[Any]) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for match in matches:
        if not isinstance(match, dict):
            continue
        item = dict(match)
        relpath = str(item.get("path") or "")
        if relpath.startswith("docs/agents/cortex/"):
            excerpt = _matched_memory_excerpt(target, relpath)
            if excerpt:
                item["excerpt"] = excerpt
        enriched.append(item)
    return enriched


def _query_terms(query: str) -> set[str]:
    return {
        token.lower()
        for token in re.findall(r"[A-Za-z0-9_]{3,80}", query)
        if token.lower() not in QUERY_STOPWORDS and token.lower() not in QUERY_GENERIC_TERMS
    }


def _runtime_match_score(match: dict[str, Any], query_terms: set[str]) -> tuple[int, int, int, str]:
    """Rank actionable Cortex memory above root boilerplate and explain why."""
    relpath = str(match.get("path") or "")
    text = " ".join(
        str(match.get(key) or "")
        for key in ("path", "layer", "title", "excerpt")
    ).lower()
    overlap = sum(1 for term in query_terms if term in text)
    if relpath.startswith("docs/agents/cortex/cells/"):
        layer_score = 30
    elif relpath.startswith("docs/agents/cortex/sources/"):
        layer_score = 24
    elif relpath.startswith("docs/agents/cortex/"):
        layer_score = 8
    else:
        layer_score = 0
    marker_score = 6 if re.search(r"\bmarker\b|cortex-recall|recall bird", text) else 0
    return (layer_score + marker_score + overlap, layer_score, overlap, relpath)


def _rank_runtime_matches(matches: list[dict[str, Any]], query: str, limit: int) -> list[dict[str, Any]]:
    terms = _query_terms(query)
    ranked: list[dict[str, Any]] = []
    for match in matches:
        item = dict(match)
        score, layer_score, overlap, _ = _runtime_match_score(item, terms)
        item["score_details"] = {
            "runtime_score": score,
            "layer_score": layer_score,
            "query_overlap": overlap,
            "query_terms": sorted(term for term in terms if term in " ".join(str(item.get(k) or "").lower() for k in ("path", "layer", "title", "excerpt"))),
        }
        ranked.append(item)
    ranked.sort(key=lambda item: _runtime_match_score(item, terms), reverse=True)
    actionable = [
        item for item in ranked
        if str(item.get("path") or "").startswith(("docs/agents/cortex/cells/", "docs/agents/cortex/sources/"))
    ]
    if actionable:
        return actionable[:limit]
    return ranked[:limit]


def _mesh_refs(paths: list[str]) -> list[str]:
    refs = []
    for path in paths:
        normalized = path.replace("\\", "/").lstrip("./")
        if normalized in MESH_FILES or normalized.startswith(MESH_DECISIONS_PREFIX):
            refs.append(normalized)
    return _dedupe(refs)


def _explicit_align_context(payload: dict[str, Any]) -> bool:
    return any("/tes-align" in text or "tes-align" in text for text in _walk_strings(payload))


def _active_align_sentinel(target: Path) -> bool:
    sentinel = target / ALIGN_SENTINEL
    try:
        stat = sentinel.stat()
    except OSError:
        return False
    if not sentinel.is_file():
        return False
    age_seconds = time.time() - stat.st_mtime
    if age_seconds < 0 or age_seconds > ALIGN_SENTINEL_MAX_AGE_SECONDS:
        return False
    try:
        text = sentinel.read_text(encoding="utf-8", errors="replace").lower()
    except OSError:
        return False
    return "tes-align" in text and "active" in text


def _write_like_event(payload: dict[str, Any]) -> bool:
    hook_event = str(payload.get("hook_event_name") or payload.get("event") or "")
    tool_name = str(payload.get("tool_name") or payload.get("toolName") or "").lower()
    if hook_event not in {"PreToolUse", "preToolUse"} and not tool_name:
        return False
    if tool_name and any(hint in tool_name for hint in WRITE_TOOL_HINTS):
        return True
    tool_input = _as_dict(payload.get("tool_input") or payload.get("toolInput"))
    if "command" in tool_input and PATCH_FILE_RE.search(str(tool_input.get("command", ""))):
        return True
    return any(key in tool_input for key in ("file_path", "content", "old_string", "new_string"))


def _bounded_query(payload: dict[str, Any], paths: list[str], target: Path, limit: int) -> str:
    source_values: list[tuple[str, int, int]] = []
    transcript_prompt = _latest_transcript_user_prompt(payload, target)
    if transcript_prompt:
        source_values.append((transcript_prompt, 30, 220))
    for key in (
        "last_assistant_message",
        "prompt",
        "user_prompt",
        "message",
    ):
        value = payload.get(key)
        if isinstance(value, str):
            source_values.append((value, 24, 180))
    tool_input = _as_dict(payload.get("tool_input") or payload.get("toolInput"))
    for key in ("file_path", "path", "cwd"):
        value = tool_input.get(key) or payload.get(key)
        if isinstance(value, str):
            source_values.append((value, 12, 60))
    for key in ("command", "content", "old_string", "new_string"):
        value = tool_input.get(key)
        if isinstance(value, str):
            source_values.append((value, 2, 120))
    source_values.extend((path, 10, 60) for path in paths)
    scored: dict[str, dict[str, Any]] = {}
    order = 0
    for index, (value, weight, cap) in enumerate(source_values):
        seen_in_source: set[str] = set()
        for token in re.findall(r"[A-Za-z0-9_]{2,80}", value):
            normalized = token.strip("._:/-").lower()
            order += 1
            if (
                len(normalized) < 3
                or normalized in seen_in_source
                or normalized in QUERY_STOPWORDS
                or normalized in QUERY_GENERIC_TERMS
            ):
                continue
            seen_in_source.add(normalized)
            entry = scored.setdefault(normalized, {"score": 0, "hits": 0, "first": index, "order": order})
            entry["score"] += weight
            entry["hits"] += 1
            if len(seen_in_source) >= cap:
                break
    ranked = sorted(
        scored,
        key=lambda item: (
            -int(scored[item]["score"]),
            -int(scored[item]["hits"]),
            int(scored[item]["first"]),
            int(scored[item]["order"]),
        ),
    )
    tokens = _dedupe(ranked, 6)
    return " ".join(tokens)[:240] or "Cortex"


def _runtime_recall(target: Path, query: str, limit: int) -> tuple[str, dict[str, Any]]:
    """Recall runtime memory with deterministic relaxation for noisy host prompts."""
    recall_limit = max(limit * 4, 20)
    result = cortex.recall(target, query, recall_limit)
    if result.get("matches"):
        return query, result
    tokens = query.split()
    candidates = []
    for size in (5, 4, 3):
        if len(tokens) >= size:
            candidates.append(" ".join(tokens[:size]))
    for candidate in _dedupe(candidates):
        if candidate == query:
            continue
        candidate_result = cortex.recall(target, candidate, recall_limit)
        if candidate_result.get("matches"):
            candidate_result["relaxed_from"] = query
            return candidate, candidate_result
    return query, result


def _alignment_signal(mesh_refs: list[str], write_like: bool, explicit_align: bool) -> dict[str, Any]:
    if mesh_refs and write_like and not explicit_align:
        return {
            "status": "NEEDS_ALIGN",
            "evidence_refs": mesh_refs,
            "reason": "Runtime event proposes a write touching the operating mesh outside an explicit alignment context.",
            "next_action": "Run /tes-align before claiming operating-mesh alignment.",
            "confidence": 0.9,
        }
    if mesh_refs and explicit_align:
        return {
            "status": "PASS",
            "evidence_refs": mesh_refs,
            "reason": "Operating mesh path appears under an explicit alignment context.",
            "next_action": "Continue with the governed alignment flow.",
            "confidence": 0.7,
        }
    return {
        "status": "PASS",
        "evidence_refs": [],
        "reason": "No operating mesh write drift was detected.",
        "next_action": "Continue.",
        "confidence": 0.6,
    }


def _capture_proposal(review_result: dict[str, Any], mesh_refs: list[str]) -> dict[str, Any]:
    reflection = _as_dict(review_result.get("reflection"))
    proposal = reflection.get("proposal")
    if not proposal:
        return {
            "status": "NONE",
            "evidence_refs": mesh_refs,
            "reason": reflection.get("no_capture_reason") or "No capture proposal was produced.",
            "writes": [],
            "derived_writes": [],
        }
    proposal_dict = _as_dict(proposal)
    evidence = proposal_dict.get("evidence")
    evidence_refs = [str(evidence)] if isinstance(evidence, str) and evidence else []
    return {
        "status": "PROPOSED",
        "evidence_refs": _dedupe([*mesh_refs, *evidence_refs], 5),
        "reason": "Cortex review produced a proposal-only capture candidate.",
        "route": proposal_dict.get("route", "proposal-only"),
        "cell": proposal_dict.get("cell"),
        "writes": [],
        "derived_writes": [],
    }


def evaluate_runtime_event(
    target: Path,
    event: dict[str, Any],
    *,
    limit: int = 5,
    line_budget: int = 500,
    backend: str = "lexical",
) -> dict[str, Any]:
    """Evaluate one host-shaped runtime event without writing project state."""
    target = target.resolve()
    event = _as_dict(event)
    payload = _event_input(event)
    paths = _dedupe(_extract_paths(payload, target), limit)
    mesh_refs = _mesh_refs(paths)
    query = _bounded_query(payload, paths, target, limit)
    query, recall_result = _runtime_recall(target, query, limit)
    recall_matches = _rank_runtime_matches(
        _enrich_runtime_matches(target, recall_result.get("matches", [])),
        query,
        limit,
    )
    effective_backend = "lexical" if backend != "lexical" else backend
    review_result = cortex.review(target, query, limit=limit, line_budget=line_budget, backend=effective_backend)
    explicit_align = _explicit_align_context(payload) or _active_align_sentinel(target)
    signal = _alignment_signal(mesh_refs, _write_like_event(payload), explicit_align)

    return {
        "target": str(target),
        "status": "PASS" if signal["status"] != "NEEDS_ALIGN" else "NEEDS_ALIGN",
        "host": _host_from_event(event, payload),
        "hook_event_name": payload.get("hook_event_name") or event.get("event"),
        "tool_name": payload.get("tool_name") or payload.get("toolName"),
        "recall_query": query,
        "advisory_context": {
            "status": recall_result.get("status"),
            "backend": recall_result.get("backend"),
            "relaxed_from": recall_result.get("relaxed_from"),
            "matches": recall_matches,
            "failures": recall_result.get("failures", []),
        },
        "proposal_evidence": {
            "review_status": review_result.get("status"),
            "backend": _as_dict(review_result.get("curation")).get("backend"),
            "curation_status": _as_dict(review_result.get("curation")).get("status"),
            "reflection_status": _as_dict(review_result.get("reflection")).get("status"),
            "capture_needed": _as_dict(review_result.get("reflection")).get("capture_needed", False),
        },
        "capture_proposal": _capture_proposal(review_result, mesh_refs),
        "alignment_signal": signal,
        "touched_paths": paths,
        "writes": [],
        "derived_writes": [],
    }


def _append_unique_line(path: Path, line: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if line in text.splitlines():
        return
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_text(text + line + "\n", encoding="utf-8")


def _build_runtime_fixture(target: Path) -> None:
    cortex.init(target)
    root = cortex.cortex_path(target)
    source = root / "sources" / "runtime-source.md"
    source.write_text(
        "# Runtime Source\n\n"
        "Cortex runtime recall can advise on PROJECT-STATE mesh drift without writing the mesh.\n",
        encoding="utf-8",
    )
    cell = root / "cells" / "runtime-recall.md"
    cell.write_text(
        "# Runtime Recall\n\n"
        "## Claim\n\n"
        "Cortex runtime recall stays advisory and reports operating mesh drift as a signal only.\n\n"
        "## Evidence\n\n"
        "- `sources/runtime-source.md` records the runtime recall fixture.\n",
        encoding="utf-8",
    )
    flappy_source = root / "sources" / "flappy-runtime-memory.md"
    flappy_source.write_text(
        "# Flappy Runtime Memory Source\n\n"
        "For single-file canvas bird game canaries, runtime recall should surface "
        "the title Cortex Recall Bird and marker cortex-recall-green-244.\n",
        encoding="utf-8",
    )
    flappy_cell = root / "cells" / "flappy-runtime-memory.md"
    flappy_cell.write_text(
        "# Flappy Runtime Memory\n\n"
        "## Claim\n\n"
        "Single-file canvas bird game canaries should use the title Cortex Recall Bird "
        "and marker cortex-recall-green-244 when runtime recall is available.\n\n"
        "## Evidence\n\n"
        "- `sources/flappy-runtime-memory.md`\n",
        encoding="utf-8",
    )
    _append_unique_line(root / "MAP.md", "| [[runtime-recall]] | Runtime recall stays advisory | |")
    _append_unique_line(root / "MAP.md", "| [[flappy-runtime-memory]] | Runtime recall can surface canary memory | |")
    _append_unique_line(root / "LINKS.md", "- [[runtime-recall]] -> `sources/runtime-source.md`")
    _append_unique_line(root / "LINKS.md", "- [[flappy-runtime-memory]] -> `sources/flappy-runtime-memory.md`")

    agents = target / "docs" / "agents"
    decisions = agents / "DECISIONS"
    decisions.mkdir(parents=True, exist_ok=True)
    for name in ("PROJECT-STATE.md", "PROJECT-ROADMAP.md", "EXECUTION-LINE.md", "QUALITY-GATES.md"):
        (agents / name).write_text(f"# {name.removesuffix('.md')}\n\nFixture baseline.\n", encoding="utf-8")
    (decisions / "runtime.md").write_text("# Runtime Decision\n\nFixture baseline.\n", encoding="utf-8")
    cortex.rebuild(target)


def _snapshot(target: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(target.rglob("*")):
        if path.is_file():
            files[path.relative_to(target).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def _reported_write_failures(value: Any, prefix: str = "result") -> list[str]:
    failures: list[str] = []
    if isinstance(value, dict):
        for key in ("writes", "derived_writes"):
            reported = value.get(key)
            if reported not in (None, []):
                failures.append(f"{prefix}.{key} is not empty")
        for key, item in value.items():
            failures.extend(_reported_write_failures(item, f"{prefix}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            failures.extend(_reported_write_failures(item, f"{prefix}[{index}]"))
    return failures


def _load_host_samples() -> list[tuple[str, str, dict[str, Any]]]:
    fixture_dir = Path(__file__).resolve().parent / "fixtures" / "cortex_host_contracts"
    samples: list[tuple[str, str, dict[str, Any]]] = []
    for name in ("claude-code.json", "codex.json", "cursor.json"):
        fixture = json.loads((fixture_dir / name).read_text(encoding="utf-8"))
        host = str(fixture["host"])
        for sample in fixture.get("samples", []):
            samples.append((host, str(sample.get("intent")), sample))
    return samples


def self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-cortex-runtime-") as tempdir:
        target = Path(tempdir)
        _build_runtime_fixture(target)
        transcript = target / ".tes" / "runtime" / "transcripts" / "flappy.jsonl"
        transcript.parent.mkdir(parents=True, exist_ok=True)
        transcript.write_text(
            json.dumps(
                {
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": "Build the single-file canvas bird game canary from the product spec.",
                    },
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        before = _snapshot(target)

        non_mesh = evaluate_runtime_event(
            target,
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Edit",
                "tool_input": {"file_path": str(target / "docs" / "notes.md"), "new_string": "next"},
            },
        )
        runtime_memory = evaluate_runtime_event(
            target,
            {
                "hook_event_name": "PreToolUse",
                "transcript_path": str(transcript),
                "tool_name": "Write",
                "tool_input": {
                    "file_path": str(target / "index.html"),
                    "content": (
                        "<!doctype html><title>Canvas Bird Canary</title><canvas id='game'></canvas><script>"
                        + " ".join(
                            "/* SECTION */ ctx.fillStyle = CONFIG.BASE_W; function drawBird(){} function drawPipes(){}"
                            for _ in range(80)
                        )
                        + " const gameState='playing'; requestAnimationFrame(function frame(){});</script>"
                    ),
                },
            },
        )
        mesh = evaluate_runtime_event(
            target,
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": str(target / "docs" / "agents" / "PROJECT-STATE.md"),
                    "old_string": "previous",
                    "new_string": "next",
                },
            },
        )
        explicit_align = evaluate_runtime_event(
            target,
            {
                "hook_event_name": "PreToolUse",
                "user_prompt": "Run /tes-align against the current operating mesh.",
                "tool_name": "Edit",
                "tool_input": {"file_path": str(target / "docs" / "agents" / "PROJECT-ROADMAP.md")},
            },
        )
        align_sentinel = target / ALIGN_SENTINEL
        align_sentinel.parent.mkdir(parents=True, exist_ok=True)
        align_sentinel.write_text("tes-align active\nstarted_at=fixture\n", encoding="utf-8")
        active_sentinel = evaluate_runtime_event(
            target,
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": str(target / "docs" / "agents" / "EXECUTION-LINE.md"),
                    "old_string": "previous",
                    "new_string": "next",
                },
            },
        )
        stale_time = time.time() - ALIGN_SENTINEL_MAX_AGE_SECONDS - 60
        os.utime(align_sentinel, (stale_time, stale_time))
        stale_sentinel = evaluate_runtime_event(
            target,
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": str(target / "docs" / "agents" / "EXECUTION-LINE.md"),
                    "old_string": "previous",
                    "new_string": "next",
                },
            },
        )
        align_sentinel.unlink()
        capture = evaluate_runtime_event(
            target,
            {
                "hook_event_name": "Stop",
                "last_assistant_message": "Runtime recall stayed advisory and produced a capture proposal only.",
            },
        )
        host_results = [
            (host, intent, evaluate_runtime_event(target, sample))
            for host, intent, sample in _load_host_samples()
        ]

        all_results = {
            "non_mesh": non_mesh,
            "runtime_memory": runtime_memory,
            "mesh": mesh,
            "explicit_align": explicit_align,
            "active_sentinel": active_sentinel,
            "stale_sentinel": stale_sentinel,
            "capture": capture,
            "host_results": [
                {"host": host, "intent": intent, "result": result}
                for host, intent, result in host_results
            ],
        }
        failures.extend(_reported_write_failures(all_results))

        if non_mesh["alignment_signal"]["status"] == "NEEDS_ALIGN":
            failures.append("non-mesh edit raised NEEDS_ALIGN")
        runtime_matches = runtime_memory["advisory_context"].get("matches", [])
        if not any("flappy-runtime-memory" in str(match.get("path") or "") for match in runtime_matches):
            failures.append("runtime memory recall did not match the flappy Cortex cell")
        if "cortex-recall-green-244" not in json.dumps(runtime_matches, ensure_ascii=False):
            failures.append("runtime memory recall did not surface the seeded marker")
        runtime_query = str(runtime_memory.get("recall_query") or "")
        if "ctx" in runtime_query or "fillstyle" in runtime_query or "section" in runtime_query:
            failures.append(f"runtime memory query must not be dominated by code tokens: {runtime_query}")
        if mesh["alignment_signal"]["status"] != "NEEDS_ALIGN":
            failures.append("mesh edit did not raise NEEDS_ALIGN")
        if explicit_align["alignment_signal"]["status"] == "NEEDS_ALIGN":
            failures.append("explicit alignment context raised NEEDS_ALIGN")
        if active_sentinel["alignment_signal"]["status"] == "NEEDS_ALIGN":
            failures.append("active alignment sentinel raised NEEDS_ALIGN")
        if stale_sentinel["alignment_signal"]["status"] != "NEEDS_ALIGN":
            failures.append("stale alignment sentinel did not raise NEEDS_ALIGN")
        if capture["capture_proposal"]["writes"] or capture["capture_proposal"]["derived_writes"]:
            failures.append("capture proposal reported durable writes")
        for host, intent, result in host_results:
            signal_status = result["alignment_signal"]["status"]
            if intent == "needs_align" and signal_status != "NEEDS_ALIGN":
                failures.append(f"{host} needs_align sample did not raise NEEDS_ALIGN")
            if intent != "needs_align" and signal_status == "NEEDS_ALIGN":
                failures.append(f"{host} {intent} sample raised NEEDS_ALIGN")

        after = _snapshot(target)
        if after != before:
            failures.append("runtime evaluation changed the fixture filesystem")
        if cortex.semantic_db_path(target).exists():
            failures.append("runtime evaluation created a semantic index")

        summary = {
            "status": "PASS" if not failures else "FAIL",
            "cases": {
                "false_positive_non_mesh": non_mesh["alignment_signal"]["status"],
                "runtime_memory_matches": len(runtime_matches),
                "false_negative_mesh": mesh["alignment_signal"]["status"],
                "explicit_align_context": explicit_align["alignment_signal"]["status"],
                "active_align_sentinel": active_sentinel["alignment_signal"]["status"],
                "stale_align_sentinel": stale_sentinel["alignment_signal"]["status"],
                "capture_proposal": capture["capture_proposal"]["status"],
                "host_samples": len(host_results),
            },
            "semantic_index_present": cortex.semantic_db_path(target).exists(),
            "filesystem_changed": after != before,
            "failures": failures,
        }
        print(json.dumps(summary, indent=2, sort_keys=True))

    print("[cortex-runtime] " + ("PASS" if not failures else "FAIL"))
    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    parser.error("only --self-test is supported for now")


if __name__ == "__main__":
    sys.exit(main())
