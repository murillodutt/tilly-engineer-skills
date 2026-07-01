#!/usr/bin/env python3
"""Parse and apply the target-local TES Codex agent memory policy."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import tomllib
from typing import Any


VERSION = "0.3.253"
SCHEMA = "tes-codex-policy@1"
POLICY_PATH = Path(".tes/tes-codex.md")
ALLOWED_ACTIONS = {"auto_promote", "propose", "review_required", "deny", "ignore"}
ALLOWED_WRITE_TARGETS = {"runtime_index", "cortex_cell", "proposal_only"}
RISK_ORDER = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "conflict": 4,
    "private_identifier": 5,
    "secret_like": 6,
    "destructive": 7,
    "release": 8,
}
SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|authorization|bearer|credential|password|secret|token)\s*[:=]\s*[A-Za-z0-9._:/+=-]+"
)
ABSOLUTE_PATH_RE = re.compile(r"(^|\s)(/Users|/home|/private|/var/folders|[A-Za-z]:\\)[^\s`\"')]+")
RAW_DIFF_RE = re.compile(r"(^diff --git|\n@@\s|^\+\+\+ |^--- )", re.MULTILINE)
POLICY_BLOCK_RE = re.compile(r"```toml\s+tes-codex-policy@1\s*\n(.*?)\n```", re.DOTALL)


DEFAULT_POLICY_TEXT = """# TES Codex Policy

This file declares how TES agents convert project material into agent memory.
Humans own this policy; agents operate within it.

```toml tes-codex-policy@1
schema = "tes-codex-policy@1"
runtime_recall_first = true
broad_scan_requires_recall_miss = true
default_action = "propose"

[auto_promote]
enabled = true
outside_hook_only = true
max_risk = "low"
write_targets = ["runtime_index", "cortex_cell"]

[review]
required_risks = ["medium", "high", "conflict", "private_identifier", "secret_like", "destructive", "release"]

[source_classes.agent_memory]
path_globs = ["docs/agents/**", "docs/adr/**", "docs/architecture/**", "docs/roadmap/goals/super-specs/**", "docs/mesh/**"]
action = "auto_promote"
risk_ceiling = "low"

[source_classes.documentation]
path_globs = ["README.md", "docs/install/**", "docs/index.html"]
action = "propose"

[source_classes.denied]
path_globs = [".env*", ".tes/runtime/**", "tmp/**"]
action = "deny"
```
"""


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def policy_file(target: Path) -> Path:
    return target / POLICY_PATH


def default_policy_digest() -> str:
    return sha256_text(DEFAULT_POLICY_TEXT)


def extract_policy_block(text: str) -> tuple[str | None, list[str]]:
    matches = POLICY_BLOCK_RE.findall(text)
    if len(matches) != 1:
        return None, [f"expected exactly one fenced TOML {SCHEMA} block, found {len(matches)}"]
    return matches[0], []


def _list_of_strings(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)


def validate_policy(data: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if data.get("schema") != SCHEMA:
        failures.append(f"schema must be {SCHEMA}")
    if not isinstance(data.get("runtime_recall_first"), bool):
        failures.append("runtime_recall_first must be boolean")
    if not isinstance(data.get("broad_scan_requires_recall_miss"), bool):
        failures.append("broad_scan_requires_recall_miss must be boolean")
    if data.get("default_action") not in ALLOWED_ACTIONS:
        failures.append("default_action is unsupported")

    auto = data.get("auto_promote")
    if not isinstance(auto, dict):
        failures.append("auto_promote must be a table")
        auto = {}
    if not isinstance(auto.get("enabled"), bool):
        failures.append("auto_promote.enabled must be boolean")
    if auto.get("outside_hook_only") is not True:
        failures.append("auto_promote.outside_hook_only must be true")
    if str(auto.get("max_risk") or "") not in RISK_ORDER:
        failures.append("auto_promote.max_risk is unsupported")
    if not _list_of_strings(auto.get("write_targets")):
        failures.append("auto_promote.write_targets must be a string list")
    else:
        unsupported = sorted(set(auto["write_targets"]) - ALLOWED_WRITE_TARGETS)
        failures.extend(f"unsupported write target: {item}" for item in unsupported)

    review = data.get("review")
    if not isinstance(review, dict):
        failures.append("review must be a table")
        review = {}
    if not _list_of_strings(review.get("required_risks")):
        failures.append("review.required_risks must be a string list")
    else:
        unsupported = sorted(set(review["required_risks"]) - set(RISK_ORDER))
        failures.extend(f"unsupported review risk: {item}" for item in unsupported)

    classes = data.get("source_classes")
    if not isinstance(classes, dict) or not classes:
        failures.append("source_classes must be a non-empty table")
        classes = {}
    for name, config in classes.items():
        if not isinstance(config, dict):
            failures.append(f"source_classes.{name} must be a table")
            continue
        if not _list_of_strings(config.get("path_globs")):
            failures.append(f"source_classes.{name}.path_globs must be a string list")
        if config.get("action") not in ALLOWED_ACTIONS:
            failures.append(f"source_classes.{name}.action is unsupported")
        risk_ceiling = config.get("risk_ceiling")
        if risk_ceiling is not None and str(risk_ceiling) not in RISK_ORDER:
            failures.append(f"source_classes.{name}.risk_ceiling is unsupported")
    return sorted(set(failures))


def load_policy(target: Path) -> dict[str, Any]:
    target = target.expanduser().resolve()
    path = policy_file(target)
    if not path.exists():
        return {
            "version": VERSION,
            "schema": SCHEMA,
            "status": "MISSING",
            "state": "MISSING",
            "path": POLICY_PATH.as_posix(),
            "policy_loaded": False,
            "failures": [],
        }
    text = path.read_text(encoding="utf-8", errors="replace")
    digest = sha256_text(text)
    block, failures = extract_policy_block(text)
    data: dict[str, Any] = {}
    if block is not None:
        try:
            parsed = tomllib.loads(block)
            data = parsed if isinstance(parsed, dict) else {}
        except tomllib.TOMLDecodeError as exc:
            failures.append(f"policy TOML parse failed: {exc}")
    failures.extend(validate_policy(data) if data else ["policy block did not parse to an object"])
    state = "INVALID"
    if not failures:
        state = "DEFAULT" if digest == default_policy_digest() else "OWNER_EDITED"
    elif data.get("schema") and data.get("schema") != SCHEMA:
        state = "STALE_SCHEMA"
    return {
        "version": VERSION,
        "schema": SCHEMA,
        "status": "PASS" if not failures else "INVALID",
        "state": state,
        "path": POLICY_PATH.as_posix(),
        "digest": digest,
        "policy": data if not failures else {},
        "policy_loaded": not failures,
        "failures": failures,
    }


def materialize_policy(target: Path, *, dry_run: bool = False) -> dict[str, Any]:
    target = target.expanduser().resolve()
    path = policy_file(target)
    current = load_policy(target)
    if current["state"] == "MISSING":
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(DEFAULT_POLICY_TEXT, encoding="utf-8")
        return {
            "version": VERSION,
            "status": "PASS",
            "state": "DEFAULT",
            "action": "would-write-default" if dry_run else "write-default",
            "path": POLICY_PATH.as_posix(),
            "digest": default_policy_digest(),
            "writes": [POLICY_PATH.as_posix()],
        }
    if current["state"] in {"DEFAULT", "OWNER_EDITED"}:
        return {
            "version": VERSION,
            "status": "PASS",
            "state": current["state"],
            "action": "preserve-existing",
            "path": POLICY_PATH.as_posix(),
            "digest": current.get("digest"),
            "writes": [],
        }
    return {
        "version": VERSION,
        "status": "NEEDS_REVIEW",
        "state": current["state"],
        "action": "preserve-invalid",
        "path": POLICY_PATH.as_posix(),
        "failures": current.get("failures", []),
        "writes": [],
    }


def _path_matches(pattern: str, path: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("/")
    return fnmatch.fnmatchcase(normalized, pattern)


def classify_path(policy: dict[str, Any], path: str) -> dict[str, Any]:
    classes = policy.get("source_classes") if isinstance(policy.get("source_classes"), dict) else {}
    ordered_names = ["denied", *[name for name in classes if name != "denied"]]
    for name in ordered_names:
        config = classes.get(name)
        if not isinstance(config, dict):
            continue
        patterns = config.get("path_globs") if isinstance(config.get("path_globs"), list) else []
        if any(isinstance(pattern, str) and _path_matches(pattern, path) for pattern in patterns):
            return {
                "path": path,
                "source_class": name,
                "action": str(config.get("action") or policy.get("default_action") or "propose"),
                "risk": str(config.get("risk_ceiling") or "low"),
            }
    return {
        "path": path,
        "source_class": "unclassified",
        "action": str(policy.get("default_action") or "propose"),
        "risk": "medium",
    }


def content_failures(text: str) -> list[str]:
    failures: list[str] = []
    if RAW_DIFF_RE.search(text):
        failures.append("raw diff content rejected")
    if SECRET_RE.search(text):
        failures.append("secret-like content rejected")
    if ABSOLUTE_PATH_RE.search(text):
        failures.append("absolute local path rejected")
    return failures


def decision_for_paths(target: Path, paths: list[str]) -> dict[str, Any]:
    target = target.expanduser().resolve()
    loaded = load_policy(target)
    if loaded["state"] == "MISSING":
        return {
            "version": VERSION,
            "schema": SCHEMA,
            "policy_loaded": False,
            "policy_state": "MISSING",
            "decision_state": "PROPOSED",
            "action": "propose",
            "source_classes": {"unclassified": len(paths)},
            "path_hashes": [sha256_text(path)[:16] for path in paths],
            "failures": [],
        }
    if loaded["state"] not in {"DEFAULT", "OWNER_EDITED"}:
        return {
            "version": VERSION,
            "schema": SCHEMA,
            "policy_loaded": False,
            "policy_state": loaded["state"],
            "policy_digest": loaded.get("digest"),
            "decision_state": "REVIEW_REQUIRED",
            "action": "review_required",
            "source_classes": {},
            "path_hashes": [sha256_text(path)[:16] for path in paths],
            "failures": loaded.get("failures", []),
        }
    policy = loaded["policy"]
    classifications = [classify_path(policy, path) for path in paths]
    counts: dict[str, int] = {}
    for item in classifications:
        source_class = str(item["source_class"])
        counts[source_class] = counts.get(source_class, 0) + 1
    actions = {str(item["action"]) for item in classifications} or {str(policy.get("default_action") or "propose")}
    auto = policy.get("auto_promote") if isinstance(policy.get("auto_promote"), dict) else {}
    max_risk = str(auto.get("max_risk") or "low")
    max_rank = RISK_ORDER.get(max_risk, 1)
    highest_rank = max((RISK_ORDER.get(str(item["risk"]), 99) for item in classifications), default=0)
    failures: list[str] = []
    for item in classifications:
        if item["action"] == "auto_promote":
            candidate = target / str(item["path"])
            if candidate.is_file():
                try:
                    failures.extend(f"{item['path']}: {failure}" for failure in content_failures(candidate.read_text(encoding="utf-8", errors="replace")))
                except OSError as exc:
                    failures.append(f"{item['path']}: cannot read candidate: {exc}")
    if failures:
        decision_state = "BLOCKED_PRIVACY"
        action = "review_required"
    elif "deny" in actions:
        decision_state = "DENIED_BY_POLICY"
        action = "deny"
    elif "review_required" in actions or highest_rank > max_rank:
        decision_state = "REVIEW_REQUIRED"
        action = "review_required"
    elif actions == {"ignore"}:
        decision_state = "NO_MEMORY_SIGNAL"
        action = "ignore"
    elif actions <= {"auto_promote"} and auto.get("enabled") is True:
        decision_state = "AUTO_PROMOTED"
        action = "auto_promote"
    else:
        decision_state = "PROPOSED"
        action = "propose"
    return {
        "version": VERSION,
        "schema": SCHEMA,
        "policy_loaded": True,
        "policy_state": loaded["state"],
        "policy_digest": loaded.get("digest"),
        "decision_state": decision_state,
        "action": action,
        "source_classes": dict(sorted(counts.items())),
        "path_hashes": [sha256_text(path)[:16] for path in paths],
        "matched_paths": classifications,
        "write_targets": auto.get("write_targets", []),
        "failures": sorted(set(failures)),
    }


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "policy-memory"


def _text_file(path: Path, max_bytes: int = 24000) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    try:
        text = data[:max_bytes].decode("utf-8")
    except UnicodeDecodeError:
        return None
    return text


def _title_from_text(path: str, text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()[:120] or Path(path).stem
        if stripped:
            return stripped[:120]
    return Path(path).stem.replace("-", " ").replace("_", " ").title()


def candidate_source_text(path: str, text: str, policy_digest: str, event_fingerprint: str) -> str:
    return (
        "# TES Codex Policy Memory Source\n\n"
        "## Source\n\n"
        f"- Path: `{path}`\n"
        f"- Policy digest: `{policy_digest}`\n"
        f"- Event fingerprint: `{event_fingerprint}`\n\n"
        "## Content\n\n"
        "```text\n"
        f"{text.rstrip()}\n"
        "```\n"
    )


def auto_promote_candidates(
    target: Path,
    paths: list[str],
    *,
    event_fingerprint: str,
    policy_decision: dict[str, Any] | None = None,
) -> dict[str, Any]:
    target = target.expanduser().resolve()
    if os.environ.get("TES_CORTEX_GIT_TAP_HOOK") == "1":
        return {"version": VERSION, "status": "BLOCKED_IN_HOOK", "failures": ["policy auto-promotion is blocked inside Git hooks"], "writes": []}
    decision = policy_decision or decision_for_paths(target, paths)
    if decision.get("decision_state") != "AUTO_PROMOTED":
        return {
            "version": VERSION,
            "status": "SKIP",
            "decision_state": decision.get("decision_state"),
            "reason": "policy did not allow automatic promotion",
            "writes": [],
        }
    try:
        import cortex as cortex_helper  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        return {"version": VERSION, "status": "FAIL", "failures": [f"cortex helper unavailable: {exc}"], "writes": []}

    cortex_helper.init(target)
    policy_digest = str(decision.get("policy_digest") or "")
    writes: list[str] = []
    promoted: list[dict[str, Any]] = []
    failures: list[str] = []
    for item in decision.get("matched_paths", []):
        if not isinstance(item, dict) or item.get("action") != "auto_promote":
            continue
        relpath = str(item.get("path") or "")
        source = target / relpath
        text = _text_file(source)
        if text is None:
            failures.append(f"{relpath}: not a readable UTF-8 text file")
            continue
        guard_failures = content_failures(text)
        if guard_failures:
            failures.extend(f"{relpath}: {failure}" for failure in guard_failures)
            continue
        digest = sha256_text(relpath + "\n" + text)[:16]
        title = _title_from_text(relpath, text)
        source_rel = f"sources/policy/{_slug(Path(relpath).stem)}-{digest}.md"
        source_path = cortex_helper.cortex_path(target) / source_rel
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(candidate_source_text(relpath, text, policy_digest, event_fingerprint), encoding="utf-8")
        cell = f"policy-{_slug(Path(relpath).stem)}-{digest}"
        claim = f"Policy-approved agent memory from `{relpath}`: {title}"
        result = cortex_helper.apply_cell(
            target,
            cell,
            claim,
            [source_rel],
            f"Policy-approved agent memory from {relpath}",
            [],
            authorized=True,
            update_existing=True,
        )
        if result.get("status") != "PASS":
            failures.extend(str(failure) for failure in result.get("failures", []))
            continue
        result_writes = [str(path) for path in result.get("writes", [])]
        writes.extend([rel(source_path, target), *result_writes])
        promoted.append({"path": relpath, "cell": f"docs/agents/cortex/cells/{cell}.md", "source": f"docs/agents/cortex/{source_rel}", "digest": digest})
    audit_path = target / ".tes/runtime/cortex/git-tap/auto-promotions.jsonl"
    if promoted:
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "schema": "tes-codex-policy-auto-promotion@1",
            "event_fingerprint": event_fingerprint,
            "policy_digest": policy_digest,
            "decision_state": decision.get("decision_state"),
            "promoted": promoted,
            "rollback": "git-revert-or-cortex-forget-after-review",
        }
        audit_path.open("a", encoding="utf-8").write(canonical_json(record) + "\n")
        writes.append(rel(audit_path, target))
    return {
        "version": VERSION,
        "status": "PASS" if promoted and not failures else ("FAIL" if failures else "SKIP"),
        "decision_state": decision.get("decision_state"),
        "policy_digest": policy_digest,
        "promoted": promoted,
        "writes": sorted(set(writes)),
        "failures": sorted(set(failures)),
    }


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-codex-policy-") as tempdir:
        target = Path(tempdir)
        materialized = materialize_policy(target)
        if materialized.get("status") != "PASS" or not policy_file(target).exists():
            failures.append("materialize must write the default policy")
        loaded = load_policy(target)
        if loaded.get("state") != "DEFAULT":
            failures.append("default policy must load as DEFAULT")
        duplicate = target / ".tes/tes-codex.md"
        duplicate.write_text(DEFAULT_POLICY_TEXT + "\n" + DEFAULT_POLICY_TEXT, encoding="utf-8")
        if load_policy(target).get("state") != "INVALID":
            failures.append("duplicate policy block must be INVALID")
        duplicate.write_text(DEFAULT_POLICY_TEXT, encoding="utf-8")
        denied = decision_for_paths(target, [".tes/runtime/x"])
        if denied.get("decision_state") != "DENIED_BY_POLICY":
            failures.append("denied path must be DENIED_BY_POLICY")
        source = target / "docs/agents/PROJECT-CONTEXT.md"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("# Agent Memory\n\nmarker policy-runtime-green-249\n", encoding="utf-8")
        decision = decision_for_paths(target, ["docs/agents/PROJECT-CONTEXT.md"])
        if decision.get("decision_state") != "AUTO_PROMOTED":
            failures.append("agent memory path must auto-promote under default policy")
        hook_previous = os.environ.get("TES_CORTEX_GIT_TAP_HOOK")
        os.environ["TES_CORTEX_GIT_TAP_HOOK"] = "1"
        try:
            hook_result = auto_promote_candidates(target, ["docs/agents/PROJECT-CONTEXT.md"], event_fingerprint="abc", policy_decision=decision)
        finally:
            if hook_previous is None:
                os.environ.pop("TES_CORTEX_GIT_TAP_HOOK", None)
            else:
                os.environ["TES_CORTEX_GIT_TAP_HOOK"] = hook_previous
        if hook_result.get("status") != "BLOCKED_IN_HOOK":
            failures.append("auto promotion must block inside hook execution")
        promote = auto_promote_candidates(target, ["docs/agents/PROJECT-CONTEXT.md"], event_fingerprint="abc", policy_decision=decision)
        if promote.get("status") != "PASS":
            failures.append("outside-hook auto promotion must pass")
            failures.extend(str(item) for item in promote.get("failures", []))
    return {"version": VERSION, "schema": SCHEMA, "status": "PASS" if not failures else "FAIL", "failures": failures}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TES Codex agent memory policy helper")
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--target", type=Path, default=Path.cwd())
    materialize_parser = subparsers.add_parser("materialize")
    materialize_parser.add_argument("--target", type=Path, default=Path.cwd())
    materialize_parser.add_argument("--dry-run", action="store_true")
    classify_parser = subparsers.add_parser("classify")
    classify_parser.add_argument("--target", type=Path, default=Path.cwd())
    classify_parser.add_argument("paths", nargs="*")
    args = parser.parse_args(argv)
    if args.self_test:
        result = self_test()
    elif args.command == "status":
        result = load_policy(args.target)
    elif args.command == "materialize":
        result = materialize_policy(args.target, dry_run=args.dry_run)
    elif args.command == "classify":
        result = decision_for_paths(args.target, args.paths)
    else:
        parser.print_help()
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    status = str(result.get("status") or result.get("state") or "")
    return 0 if status in {"PASS", "DEFAULT", "OWNER_EDITED", "MISSING", "SKIP"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
