#!/usr/bin/env python3
"""Generate and maintain the TES Project GPS block."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


VERSION = "0.3.128"
START_MARKER = "<!-- TES-MAP:START -->"
END_MARKER = "<!-- TES-MAP:END -->"
ROADMAP_REL = Path("docs/agents/PROJECT-ROADMAP.md")
AGENTS_REL = Path("docs/agents")
MANAGED_HEADING = "## TES Map"
STATUS_PASS = "PASS"
STATUS_NEEDS_ALIGN = "NEEDS_ALIGN"
STATUS_NEEDS_CONTEXT = "NEEDS_CONTEXT"
STATUS_BLOCKED = "BLOCKED"
STATUS_NOT_AVAILABLE = "NOT_AVAILABLE"
SCRIPT_PATH = Path(__file__).resolve()
PACKAGE_MODE = (SCRIPT_PATH.parents[1] / "package.json").exists() and SCRIPT_PATH.parent.name == "scripts"


@dataclass(frozen=True)
class GitInfo:
    available: bool
    branch: str | None
    head: str | None
    dirty: bool | None
    limit: str | None = None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_text_if_changed(path: Path, text: str) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def relpath(target: Path, path: Path) -> str:
    try:
        return str(path.relative_to(target))
    except ValueError:
        return str(path)


def clean_line(line: str) -> str:
    value = line.strip()
    value = re.sub(r"^\s*[-*]\s+\[[ xX]\]\s+", "", value)
    value = re.sub(r"^\s*[-*]\s+", "", value)
    value = value.replace("`", "")
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[\[([^|\]]+)\|?([^\]]*)\]\]", lambda m: m.group(2) or m.group(1), value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" .")


def mermaid_label(value: str, fallback: str, max_len: int = 54) -> str:
    label = clean_line(value) or fallback
    label = label.replace('"', "'").replace("{", "(").replace("}", ")")
    if len(label) > max_len:
        label = label[: max_len - 1].rstrip() + "..."
    return label


def table_value(value: str | list[str]) -> str:
    if isinstance(value, list):
        if not value:
            return "None recorded."
        return "<br>".join(value[:3])
    return value or "None recorded."


def parse_sections(markdown: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = ""
    for line in markdown.splitlines():
        match = re.match(r"^(#{2,4})\s+(.+?)\s*$", line)
        if match:
            current = match.group(2).strip()
            sections.setdefault(current, [])
            continue
        if current:
            sections.setdefault(current, []).append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def first_bullets(section: str, limit: int = 3) -> list[str]:
    values: list[str] = []
    in_code = False
    for line in section.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if re.match(r"^\s*[-*]\s+", line):
            value = clean_line(line)
            if value and value not in values:
                values.append(value)
        if len(values) >= limit:
            break
    return values


def find_section(sections: dict[str, str], *names: str) -> str:
    folded = {name.casefold(): value for name, value in sections.items()}
    for name in names:
        direct = folded.get(name.casefold())
        if direct is not None:
            return direct
    for section_name, value in sections.items():
        if any(name.casefold() in section_name.casefold() for name in names):
            return value
    return ""


def first_sentence(text: str, fallback: str) -> str:
    for line in text.splitlines():
        cleaned = clean_line(line)
        if cleaned and not cleaned.startswith("#") and not cleaned.startswith(START_MARKER):
            return cleaned[:160]
    return fallback


def latest_files(root: Path, pattern: str, limit: int = 3) -> list[Path]:
    if not root.exists():
        return []
    files = [path for path in root.glob(pattern) if path.is_file()]
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)[:limit]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def git_value(target: Path, args: list[str]) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def git_info(target: Path) -> GitInfo:
    inside = git_value(target, ["rev-parse", "--is-inside-work-tree"])
    if inside != "true":
        return GitInfo(False, None, None, None, "target is not a Git repository")
    branch = git_value(target, ["rev-parse", "--abbrev-ref", "HEAD"])
    head = git_value(target, ["rev-parse", "--short=12", "HEAD"])
    status = git_value(target, ["status", "--short"])
    return GitInfo(True, branch, head, bool(status))


def detect_gate(target: Path) -> str:
    package_json = read_json(target / "package.json")
    scripts = package_json.get("scripts", {}) if isinstance(package_json, dict) else {}
    if isinstance(scripts, dict):
        for candidate in ("gate:doctor", "gate", "test", "build", "lint"):
            if candidate in scripts:
                manager = "pnpm" if (target / "pnpm-lock.yaml").exists() else "npm"
                if (target / "bun.lockb").exists() or (target / "bun.lock").exists():
                    manager = "bun"
                return f"{manager} run {candidate}"
    if (target / "Makefile").exists():
        return "make test"
    return "project_alignment_oracle.py --target ."


def classify_status(target: Path) -> tuple[str, list[str]]:
    agents_root = target / AGENTS_REL
    roadmap = target / ROADMAP_REL
    context = agents_root / "PROJECT-CONTEXT.md"
    limits: list[str] = []
    if not agents_root.exists() or not context.exists():
        limits.append("PROJECT-CONTEXT.md is missing; run /tes-init or /tes-align first.")
        return STATUS_NEEDS_CONTEXT, limits
    if not roadmap.exists():
        limits.append("PROJECT-ROADMAP.md is missing; run /tes-align first.")
        return STATUS_NEEDS_ALIGN, limits
    return STATUS_PASS, limits


def build_model(target: Path) -> dict[str, Any]:
    target = target.resolve()
    status, limits = classify_status(target)
    roadmap_path = target / ROADMAP_REL
    roadmap_text = read_text(roadmap_path)
    sections = parse_sections(roadmap_text)
    postinstall = read_json(target / ".tes/postinstall.json")
    lock = read_json(target / ".tes/tes-install-lock.json")
    git = git_info(target)
    evidence_files = latest_files(target / "docs/agents/evidence", "*.md", limit=3)
    gate = detect_gate(target)

    done_items = first_bullets(find_section(sections, "Done"), 3)
    active_items = first_bullets(find_section(sections, "Active"), 3)
    next_items = first_bullets(find_section(sections, "Next", "Next Irreversible Step"), 3)
    later_items = first_bullets(find_section(sections, "Later"), 2)
    deferred_items = first_bullets(find_section(sections, "Deferred"), 2)
    blocked_items = first_bullets(find_section(sections, "Blocked"), 3)
    unknown_items = first_bullets(find_section(sections, "Unknown"), 3)
    claim = first_sentence(find_section(sections, "Current Claim"), "No current claim recorded.")
    irreversible = first_bullets(find_section(sections, "Next Irreversible Step"), 1)

    position = active_items[0] if active_items else claim
    current_phase = active_items[0] if active_items else "Needs roadmap phase evidence."
    next_step = irreversible[0] if irreversible else (next_items[0] if next_items else "Run /tes-align to define the next step.")

    last_status = str(postinstall.get("last_status") or postinstall.get("state") or "").upper()
    version = str(postinstall.get("version") or lock.get("version") or VERSION)
    if last_status in {"PASS", "COMPLETE"}:
        last_proven = f"TES {version} first-session setup PASS"
    elif evidence_files:
        last_proven = relpath(target, evidence_files[0])
    elif done_items:
        last_proven = done_items[0]
    else:
        last_proven = "No retained proof found."

    evidence = [relpath(target, path) for path in evidence_files]
    if postinstall:
        evidence.append(".tes/postinstall.json")
    if lock:
        evidence.append(".tes/tes-install-lock.json")
    if (target / AGENTS_REL / "QUALITY-GATES.md").exists():
        evidence.append("docs/agents/QUALITY-GATES.md")
    if git.available and git.head:
        evidence.append(f"git:{git.branch or 'HEAD'}@{git.head}")

    if not git.available and git.limit:
        limits.append(git.limit)
    elif git.dirty:
        limits.append("Git worktree has uncommitted changes; map is a position report, not a release claim.")

    if status == STATUS_PASS:
        confidence = "high" if evidence_files and postinstall else "medium"
    elif status in {STATUS_NEEDS_CONTEXT, STATUS_NEEDS_ALIGN}:
        confidence = "low"
    else:
        confidence = "unknown"

    return {
        "version": VERSION,
        "status": status,
        "target": str(target),
        "roadmap": str(roadmap_path),
        "managed_block_present": START_MARKER in roadmap_text and END_MARKER in roadmap_text,
        "position": position,
        "current_phase": current_phase,
        "last_proven_point": last_proven,
        "next_irreversible_step": next_step,
        "next_safe_move": next_step,
        "blocking_items": blocked_items,
        "unknowns": unknown_items,
        "confidence": confidence,
        "proof_gate": gate,
        "evidence": evidence[:6],
        "done_items": done_items,
        "active_items": active_items,
        "next_items": next_items,
        "later_items": later_items,
        "deferred_items": deferred_items,
        "limits": limits,
        "git": {
            "available": git.available,
            "branch": git.branch,
            "head": git.head,
            "dirty": git.dirty,
            "limit": git.limit,
        },
    }


def build_mermaid(model: dict[str, Any]) -> str:
    done = mermaid_label((model["done_items"] or ["Done evidence"])[0], "Done evidence")
    current = mermaid_label(model["position"], "You are here")
    next_step = mermaid_label(model["next_irreversible_step"], "Next step")
    final = mermaid_label("Certified project movement", "Certified project movement")
    later = mermaid_label((model["later_items"] or ["Later"])[0], "Later")
    deferred = mermaid_label((model["deferred_items"] or ["Deferred"])[0], "Deferred")
    blocked = mermaid_label((model["blocking_items"] or ["No blocker recorded"])[0], "No blocker recorded")
    unknown = mermaid_label((model["unknowns"] or ["No unknown recorded"])[0], "No unknown recorded")
    return "\n".join(
        [
            "```mermaid",
            "flowchart LR",
            f'  done["Done: {done}"] --> current["You are here: {current}"]',
            f'  current --> next["Next safe move: {next_step}"]',
            f'  next --> final["Proof: {final}"]',
            f'  current -.-> later["Later: {later}"]',
            f'  current -.-> deferred["Deferred: {deferred}"]',
            f'  current -.-> blocked["Blocked by: {blocked}"]',
            f'  current -.-> unknown["Unknown: {unknown}"]',
            "  class done done",
            "  class current current",
            "  class next next",
            "  class later later",
            "  class deferred deferred",
            "  class blocked blocked",
            "  class unknown unknown",
            "  class final final",
            "  classDef done fill:#dcfce7,stroke:#166534,color:#052e16",
            "  classDef current fill:#dbeafe,stroke:#1d4ed8,color:#172554",
            "  classDef next fill:#fef3c7,stroke:#b45309,color:#451a03",
            "  classDef later fill:#f1f5f9,stroke:#475569,color:#0f172a",
            "  classDef deferred fill:#ede9fe,stroke:#6d28d9,color:#2e1065",
            "  classDef blocked fill:#fee2e2,stroke:#b91c1c,color:#450a0a",
            "  classDef unknown fill:#e5e7eb,stroke:#374151,color:#111827",
            "  classDef final fill:#ccfbf1,stroke:#0f766e,color:#042f2e",
            "```",
        ]
    )


def build_block(model: dict[str, Any]) -> str:
    status_table = "\n".join(
        [
            "| Signal | Value |",
            "|---|---|",
            f"| Position | {table_value(model['position'])} |",
            f"| Current phase | {table_value(model['current_phase'])} |",
            f"| Last proven point | {table_value(model['last_proven_point'])} |",
            f"| Next irreversible step | {table_value(model['next_irreversible_step'])} |",
            f"| Blocking items | {table_value(model['blocking_items'])} |",
            f"| Unknowns | {table_value(model['unknowns'])} |",
            f"| Confidence | {table_value(model['confidence'])} |",
        ]
    )
    evidence = model["evidence"] or ["No retained evidence found."]
    limits = model["limits"] or ["None recorded."]
    return "\n".join(
        [
            START_MARKER,
            "### Project GPS",
            "",
            "`tes-align` owns the map. `tes-map` updates the position.",
            "",
            status_table,
            "",
            build_mermaid(model),
            "",
            "### What changed",
            "",
            "- Refreshed the current project position from roadmap, state, gates, evidence, TES install records, and Git when available.",
            "",
            "### What to do next",
            "",
            f"- You are here: {model['position']}",
            f"- Next safe move: {model['next_safe_move']}",
            f"- Proof: `{model['proof_gate']}`",
            "",
            "### Evidence",
            "",
            *[f"- `{item}`" for item in evidence[:6]],
            "",
            "### Limits",
            "",
            *[f"- {item}" for item in limits],
            END_MARKER,
        ]
    ).rstrip() + "\n"


def replace_or_insert_block(original: str, block: str) -> tuple[str, str]:
    if START_MARKER in original and END_MARKER in original:
        pattern = re.compile(
            re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
            flags=re.DOTALL,
        )
        return pattern.sub(block.strip(), original, count=1), "updated"

    section = f"\n{MANAGED_HEADING}\n\n{block}"
    current_claim = re.search(r"\n## Current Claim\b", original)
    if current_claim:
        index = current_claim.start()
        return original[:index].rstrip() + "\n" + section + "\n" + original[index:].lstrip(), "inserted"
    return original.rstrip() + "\n" + section, "inserted"


def update_roadmap(target: Path, model: dict[str, Any]) -> dict[str, Any]:
    roadmap = target / ROADMAP_REL
    if model["status"] != STATUS_PASS:
        return {"changed": False, "action": "skipped", "path": relpath(target, roadmap)}
    original = read_text(roadmap)
    if not original:
        return {"changed": False, "action": "missing", "path": relpath(target, roadmap)}
    block = build_block(model)
    updated, action = replace_or_insert_block(original, block)
    changed = write_text_if_changed(roadmap, updated)
    return {
        "changed": changed,
        "action": action if changed else "unchanged",
        "path": relpath(target, roadmap),
        "block_sha256": hashlib.sha256(block.encode("utf-8")).hexdigest(),
    }


def human_report(model: dict[str, Any], write_result: dict[str, Any] | None) -> str:
    lines = [
        "Project GPS",
        "",
        f"Status   {model['status']}",
        f"Target   {model['target']}",
        "",
        f"You are here           {model['position']}",
        f"Current phase         {model['current_phase']}",
        f"Next safe move        {model['next_safe_move']}",
        f"Blocked by            {table_value(model['blocking_items'])}",
        f"Unknown               {table_value(model['unknowns'])}",
        f"Proof                 {model['proof_gate']}",
        f"Confidence            {model['confidence']}",
    ]
    if write_result:
        lines.extend(["", f"Roadmap               {write_result['action']} {write_result['path']}"])
    if model["status"] == STATUS_NEEDS_CONTEXT:
        lines.extend(["", "Run /tes-init first, then /tes-align when the setup report is complete."])
    elif model["status"] == STATUS_NEEDS_ALIGN:
        lines.extend(["", "Run /tes-align first so PROJECT-ROADMAP.md can own the map."])
    elif not write_result:
        lines.extend(["", "Run with --write to refresh the managed TES Map block."])
    if model["evidence"]:
        lines.extend(["", "Evidence"])
        lines.extend(f"- {item}" for item in model["evidence"][:4])
    if model["limits"]:
        lines.extend(["", "Limits"])
        lines.extend(f"- {item}" for item in model["limits"][:4])
    return "\n".join(lines)


def create_fixture(target: Path) -> None:
    agents = target / AGENTS_REL
    evidence = agents / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    (agents / "PROJECT-CONTEXT.md").write_text("# Project Context\n\nAnchor exists.\n", encoding="utf-8")
    (agents / "PROJECT-STATE.md").write_text("# Project State\n\n- Runtime installed.\n", encoding="utf-8")
    (agents / "EXECUTION-LINE.md").write_text("# Execution Line\n\n- Continue mapping.\n", encoding="utf-8")
    (agents / "QUALITY-GATES.md").write_text("# Quality Gates\n\n- `npm test`\n", encoding="utf-8")
    (evidence / "20260101T000000Z-project-alignment.md").write_text("# Evidence\n\nPASS.\n", encoding="utf-8")
    (target / ".tes").mkdir(parents=True, exist_ok=True)
    (target / ".tes/postinstall.json").write_text(
        json.dumps({"state": "complete", "last_status": "PASS", "version": VERSION}, indent=2),
        encoding="utf-8",
    )
    (target / ".tes/tes-install-lock.json").write_text(
        json.dumps({"version": VERSION}, indent=2),
        encoding="utf-8",
    )
    (target / "package.json").write_text(
        json.dumps({"scripts": {"test": "echo ok"}}, indent=2),
        encoding="utf-8",
    )
    (agents / "PROJECT-ROADMAP.md").write_text(
        """# Project Roadmap

## System X-Ray

```mermaid
flowchart TD
  ctx["Context"] --> gate["Gate"]
```

## Convergence Line

```mermaid
flowchart TD
  done["Done"] --> current["Active"] --> next["Next"] --> final["Final"]
  class done done
  class current current
  class next next
  class final final
  classDef done fill:#dcfce7,stroke:#166534
  classDef current fill:#dbeafe,stroke:#1d4ed8
  classDef next fill:#fef3c7,stroke:#b45309
  classDef later fill:#f1f5f9,stroke:#475569
  classDef deferred fill:#ede9fe,stroke:#6d28d9
  classDef blocked fill:#fee2e2,stroke:#b91c1c
  classDef unknown fill:#e5e7eb,stroke:#374151
  classDef final fill:#ccfbf1,stroke:#0f766e
```

## Current Claim

- TES runtime is installed.

## Next Irreversible Step

- Certify the next release gate.

## Done

- First-session setup completed.

## Active

- Project GPS adoption.

## Next

- Prove idempotent roadmap update.

## Later

- Expand project dashboard.

## Deferred

- Advanced portfolio map.

## Blocked

- None recorded.

## Unknown

- No unresolved unknowns.
""",
        encoding="utf-8",
    )


def self_test() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tes-map-self-test-") as tmp:
        target = Path(tmp)
        create_fixture(target)
        model = build_model(target)
        if model["status"] != STATUS_PASS:
            return {"status": "FAIL", "reason": "fixture did not pass", "model": model}
        first = update_roadmap(target, model)
        before = (target / ROADMAP_REL).read_text(encoding="utf-8")
        second_model = build_model(target)
        second = update_roadmap(target, second_model)
        after = (target / ROADMAP_REL).read_text(encoding="utf-8")
        failures: list[str] = []
        if not first["changed"]:
            failures.append("first write did not change roadmap")
        if second["changed"]:
            failures.append("second write was not idempotent")
        if before != after:
            failures.append("roadmap content changed on second write")
        for term in ("Project GPS", START_MARKER, END_MARKER, "flowchart LR", "You are here"):
            if term not in after:
                failures.append(f"missing term: {term}")
        return {
            "status": "FAIL" if failures else "PASS",
            "version": VERSION,
            "self_test_mode": "package" if PACKAGE_MODE else "installed",
            "coverage": "source-package-contract" if PACKAGE_MODE else "installed-helper-contract",
            "failures": failures,
            "first": first,
            "second": second,
        }


def run(args: argparse.Namespace) -> int:
    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "PASS" else 1

    target = Path(args.target).expanduser().resolve()
    model = build_model(target)
    write_result = update_roadmap(target, model) if args.write else None
    result = {"status": model["status"], "model": model, "write": write_result}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(human_report(model, write_result))
    return 0 if model["status"] in {STATUS_PASS, STATUS_NOT_AVAILABLE} else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update the TES Project GPS block.")
    parser.add_argument("--target", default=".", help="target project root")
    parser.add_argument("--write", action="store_true", help="update the managed TES Map block")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
