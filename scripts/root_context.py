#!/usr/bin/env python3
"""Detect durable agent context hidden in root runtime bootloaders."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:  # Sanctioned-drift attestation is optional; degrade to suppress-nothing.
    import root_context_sanctioned_oracle as _sanctioned
except ImportError:  # pragma: no cover - exercised only when the oracle is absent
    _sanctioned = None


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.189"
EVIDENCE_DIR = Path("docs/agents/evidence")
BACKUP_ROOT = Path(".tes/bk")
ROOT_FILES = (
    ("codex", "AGENTS.md", "src/adapters/codex/AGENTS.md"),
    ("claude", "CLAUDE.md", "src/adapters/claude/CLAUDE.md"),
    ("cursor", "CURSOR.md", "src/adapters/cursor/CURSOR.md"),
    ("cursor", ".cursor/rules/tes-guidelines.mdc", "src/adapters/cursor/rules/tes-guidelines.mdc"),
    ("cursor", ".cursorrules", None),
)
ROOT_CONTEXT_PATHS = {relpath for _, relpath, _ in ROOT_FILES}
CORE_BEGIN_RE = re.compile(r"<!-- TES:CORE BEGIN(?P<meta>[^>]*)-->\n?")
CORE_END = "<!-- TES:CORE END -->"
OVERLAY_BEGIN_RE = re.compile(r"<!-- TES:PROJECT-OVERLAY BEGIN(?P<meta>[^>]*)-->\n?")
OVERLAY_END = "<!-- TES:PROJECT-OVERLAY END -->"
IGNORE_TERMS = (
    "tilly",
    "cortex",
    "field reports",
    "/tilly",
    "docs/agents",
    ".agents/skills",
    "assumptions visible",
    "think before coding",
    "simplicity first",
    "surgical changes",
    "goal-driven execution",
    "diamond build",
    "success formula",
    "codex",
    "claude",
    "cursor",
    "mcp",
    "bootloader",
    "runtime",
    "shortcuts",
    "do not claim",
)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def source_sha(source_rel: str | None) -> str | None:
    if source_rel is None:
        return None
    source = ROOT / source_rel
    return sha256(source) if source.exists() else None


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def final_newline(text: str) -> str:
    return text if not text or text.endswith("\n") else f"{text}\n"


def marker_attrs(raw: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for key, value in re.findall(r"([A-Za-z0-9_-]+)=([^\s>]+)", raw):
        attrs[key] = value.strip('"')
    return attrs


def marked_block(text: str, begin_re: re.Pattern[str], end_marker: str) -> dict[str, Any] | None:
    begin = begin_re.search(text)
    if not begin:
        return None
    end = text.find(end_marker, begin.end())
    if end < 0:
        return None
    return {
        "text": text[begin.end():end],
        "attrs": marker_attrs(begin.group("meta") or ""),
        "start": begin.start(),
        "end": end + len(end_marker),
    }


def extract_core(text: str) -> dict[str, Any] | None:
    block = marked_block(text, CORE_BEGIN_RE, CORE_END)
    if not block:
        return None
    core_text = str(block["text"])
    return {**block, "sha256": text_sha256(core_text)}


def extract_overlay(text: str) -> dict[str, Any] | None:
    block = marked_block(text, OVERLAY_BEGIN_RE, OVERLAY_END)
    if not block:
        return None
    overlay_text = str(block["text"])
    return {**block, "sha256": text_sha256(overlay_text)}


def strip_nested_core(text: str) -> str:
    """Remove fossilized TES:CORE blocks from project-overlay text.

    A root file composed by TES must carry exactly one TES:CORE block (the
    current one at the top). Earlier install/update layers could leave an older
    core fossilized inside the PROJECT-OVERLAY region; if preserved verbatim it
    is re-injected on every later compose, duplicating the core indefinitely.
    This removes any complete `TES:CORE BEGIN ... TES:CORE END` pair, anchored on
    the module's own markers so a missing END never consumes legitimate overlay.
    """
    out: list[str] = []
    cursor = 0
    while True:
        begin = CORE_BEGIN_RE.search(text, cursor)
        if not begin:
            out.append(text[cursor:])
            break
        end = text.find(CORE_END, begin.end())
        if end < 0:
            # Unterminated marker: not a complete block, leave the rest intact.
            out.append(text[cursor:])
            break
        out.append(text[cursor:begin.start()])
        cursor = end + len(CORE_END)
        # Drop a single trailing newline left by the removed block, if present.
        if cursor < len(text) and text[cursor] == "\n":
            cursor += 1
    return "".join(out)


def strip_tes_blocks(text: str) -> dict[str, Any]:
    """Reverse root-context composition for uninstall (ADR 0004).

    Return the project's own content (the PROJECT-OVERLAY body) with the TES:CORE
    block and composition wrappers removed. `had_tes` is True when a TES:CORE
    block was present. `project_text` is empty when the file held no project
    content (it was a pure TES bootloader and can be deleted).
    """
    core = extract_core(text)
    overlay = extract_overlay(text)
    if core is None:
        # No TES block; leave the file untouched.
        return {"had_tes": False, "project_text": text}
    project_text = str(overlay["text"]).strip("\n") if overlay is not None else ""
    if project_text:
        project_text = project_text + "\n"
    return {"had_tes": True, "project_text": project_text}


def root_context_adapter(relpath: str) -> str:
    for adapter, candidate, _ in ROOT_FILES:
        if relpath == candidate:
            return adapter
    return "unknown"


def is_root_context_path(relpath: str) -> bool:
    return relpath in ROOT_CONTEXT_PATHS


def sanctioned_drift_allowlist(target: Path) -> list[Any]:
    """Load the project's sanctioned root-drift attestation, or [] when absent.

    Degrades to an empty list (suppress nothing) if the optional oracle is not
    importable or the attestation file/contents are invalid — preserving the
    pre-attestation behavior exactly.
    """
    if _sanctioned is None:
        return []
    try:
        return _sanctioned.load_sanctioned(target)
    except (OSError, ValueError):
        return []


def is_sanctioned_drift(relpath: str, allowlist: list[Any]) -> bool:
    if not allowlist or _sanctioned is None:
        return False
    return _sanctioned.is_sanctioned(relpath, allowlist)


def compose_root_context(
    *,
    relpath: str,
    core_text: str,
    existing_text: str = "",
    version: str = VERSION,
    previous_core_sha256: str | None = None,
) -> dict[str, Any]:
    """Compose current TES core with preserved project overlay."""

    core = final_newline(core_text)
    core_sha = text_sha256(core)
    existing_core = extract_core(existing_text) if existing_text else None
    existing_overlay = extract_overlay(existing_text) if existing_text else None
    existing_sha = text_sha256(existing_text) if existing_text else None
    overlay_text = ""
    overlay_source = "none"

    if existing_overlay is not None:
        # Drop any fossilized TES:CORE block left inside a prior overlay so the
        # composed file keeps exactly one core (the current top one). Without
        # this, an older core embedded in the overlay is re-injected on every
        # update and the core duplicates indefinitely.
        overlay_text = final_newline(strip_nested_core(str(existing_overlay["text"])))
        overlay_source = "marked-overlay"
    elif existing_text and existing_sha not in {core_sha, previous_core_sha256}:
        overlay_text = final_newline(existing_text)
        overlay_source = "legacy-unmarked-root"

    adapter = root_context_adapter(relpath)
    core_begin = f"<!-- TES:CORE BEGIN version={version} sha256={core_sha} adapter={adapter} path={relpath} -->"
    overlay_sha = text_sha256(overlay_text)
    overlay_begin = (
        f"<!-- TES:PROJECT-OVERLAY BEGIN source={overlay_source} "
        f"sha256={overlay_sha} path={relpath} -->"
    )
    composed = "\n".join(
        [
            core_begin,
            core.rstrip("\n"),
            CORE_END,
            "",
            overlay_begin,
            overlay_text.rstrip("\n"),
            OVERLAY_END,
            "",
        ]
    )
    if core.endswith("\n"):
        # The join above strips only boundary newlines; keep core hash stable by
        # comparing extracted core through the helper instead of the visual body.
        composed = composed.replace(f"{core.rstrip(chr(10))}\n{CORE_END}", f"{core}{CORE_END}", 1)

    extracted = extract_core(composed)
    status = "COMPOSED" if extracted and extracted.get("sha256") == core_sha else "NEEDS_REVIEW_CONFLICT"
    return {
        "status": status,
        "path": relpath,
        "adapter": adapter,
        "text": composed,
        "core_sha256": core_sha,
        "existing_core_sha256": existing_core.get("sha256") if existing_core else None,
        "overlay_sha256": overlay_sha,
        "overlay_source": overlay_source,
        "overlay_preserved": overlay_source in {"marked-overlay", "legacy-unmarked-root"} or not existing_text,
        "had_existing": bool(existing_text),
        "has_existing_markers": bool(existing_core or existing_overlay),
        "failures": [] if status == "COMPOSED" else ["composed core hash mismatch"],
    }


def package_source_available() -> bool:
    return (ROOT / "src/adapters/codex/AGENTS.md").exists()


def packaged_codex_bootloader() -> str:
    source = ROOT / "src/adapters/codex/AGENTS.md"
    if source.exists():
        return source.read_text(encoding="utf-8")
    return "# Tilly Codex Bootloader\n\nRoute to `docs/agents/**`.\nTilly applies.\n"


def root_candidates(target: Path) -> list[tuple[str, Path, str | None]]:
    candidates = [(adapter, target / relpath, source) for adapter, relpath, source in ROOT_FILES]
    rules = sorted((target / ".cursor/rules").glob("*.mdc"))
    known = {path for _, path, _ in candidates}
    for path in rules:
        if path not in known:
            candidates.append(("cursor", path, None))
    return candidates


def backup_root_candidates(target: Path, backup_id: str) -> list[tuple[str, Path, str | None]]:
    backup_files = target / BACKUP_ROOT / backup_id / "files"
    candidates = [(adapter, backup_files / relpath, source) for adapter, relpath, source in ROOT_FILES]
    rules = sorted((backup_files / ".cursor/rules").glob("*.mdc"))
    known = {path for _, path, _ in candidates}
    for path in rules:
        if path not in known:
            candidates.append(("cursor", path, None))
    return candidates


def meaningful_lines(text: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line in {"---", "```", "```text", "<instructions>", "</instructions>"}:
            continue
        compact = re.sub(r"^[#>*\-\d\.\s`]+", "", line).strip()
        if len(compact) < 6:
            continue
        lines.append((lineno, line))
    return lines


def project_context_lines(text: str) -> list[dict[str, Any]]:
    snippets: list[dict[str, Any]] = []
    for lineno, line in meaningful_lines(text):
        lower = line.lower()
        if any(term in lower for term in IGNORE_TERMS):
            continue
        snippets.append({"line": lineno, "excerpt": line[:160]})
        if len(snippets) >= 5:
            break
    return snippets


def classify_file(
    target: Path,
    adapter: str,
    path: Path,
    source_rel: str | None,
    sanctioned: list[Any] | None = None,
) -> dict[str, Any]:
    relpath = rel(path, target)
    if not path.exists():
        return {"adapter": adapter, "path": relpath, "state": "missing", "requires_structure_gate": False}
    if not path.is_file():
        return {"adapter": adapter, "path": relpath, "state": "not-file", "requires_structure_gate": True}

    text = read(path)
    current_sha = sha256(path)
    expected_sha = source_sha(source_rel)
    line_count = len(text.splitlines())
    core = extract_core(text)
    overlay = extract_overlay(text)
    classified_text = str(overlay["text"]) if overlay else text
    snippets = project_context_lines(classified_text)
    has_tes = any(term in text.lower() for term in ("tilly", "docs/agents", ".agents/skills", "/tilly"))

    if expected_sha and current_sha == expected_sha:
        state = "current-tes-root"
        requires = False
    elif expected_sha and core and core.get("sha256") == expected_sha:
        state = "composed-tes-root"
        requires = False
    elif snippets:
        state = "mixed-or-project-root-context" if has_tes else "project-root-context"
        requires = True
    elif has_tes:
        state = "tes-root-drift"
        requires = False
    elif line_count == 0:
        state = "empty"
        requires = False
    else:
        state = "project-root-context"
        requires = True

    # Sanctioned drift: the project has attested this customized root file as
    # intentional, so it no longer raises the structure gate every postinstall.
    sanctioned_drift = bool(requires and is_sanctioned_drift(relpath, sanctioned or []))
    if sanctioned_drift:
        requires = False
        state = f"{state}-sanctioned"

    return {
        "adapter": adapter,
        "path": relpath,
        "state": state,
        "requires_structure_gate": requires,
        "sanctioned_drift": sanctioned_drift,
        "line_count": line_count,
        "sha256": current_sha,
        "core_sha256": core.get("sha256") if core else None,
        "overlay_sha256": overlay.get("sha256") if overlay else None,
        "source": source_rel,
        "source_sha256": expected_sha,
        "signals": snippets,
    }


def analyze(target: Path, *, write_plan: bool = False, backup_id: str | None = None) -> dict[str, Any]:
    target = target.expanduser().resolve()
    if not target.exists() or not target.is_dir():
        return {"version": VERSION, "status": "FAIL", "failures": [f"target is not a directory: {target}"]}

    candidate_root = target if backup_id is None else target / BACKUP_ROOT / backup_id / "files"
    candidates = root_candidates(target) if backup_id is None else backup_root_candidates(target, backup_id)
    sanctioned = sanctioned_drift_allowlist(target)
    roots = [classify_file(candidate_root, adapter, path, source, sanctioned) for adapter, path, source in candidates]
    required = [item for item in roots if item.get("requires_structure_gate")]
    sanctioned_paths = [item["path"] for item in roots if item.get("sanctioned_drift")]
    result: dict[str, Any] = {
        "version": VERSION,
        "status": "NEEDS_REVIEW" if required else "PASS",
        "target": str(target),
        "source": "active-root" if backup_id is None else f"backup:{backup_id}",
        "structure_gate": "required" if required else "not_required",
        "root_count": len([item for item in roots if item["state"] != "missing"]),
        "requires_structure_count": len(required),
        "sanctioned_drift_paths": sanctioned_paths,
        "roots": roots,
        "writes": [],
        "failures": [],
    }
    if write_plan and required:
        plan = write_structure_plan(target, required)
        result["writes"].append(plan)
    return result


def write_structure_plan(target: Path, required: list[dict[str, Any]]) -> str:
    evidence = target / EVIDENCE_DIR
    evidence.mkdir(parents=True, exist_ok=True)
    path = evidence / f"{utc_stamp()}-root-context-structure-plan.md"
    sections = []
    for item in required:
        signals = "\n".join(f"- line {signal['line']}: {signal['excerpt']}" for signal in item.get("signals", []))
        sections.append(
            "\n".join(
                [
                    f"## {item['path']}",
                    "",
                    f"State: `{item['state']}`",
                    f"SHA-256: `{item.get('sha256', '')}`",
                    "",
                    "Signals:",
                    signals or "- present root context",
                    "",
                    "Required action: migrate durable instructions into `docs/agents/**`",
                    "or a project-owned adapter note before rewriting this root file.",
                ]
            )
        )
    path.write_text(
        "\n\n".join(
            [
                "# Tilly Root Context Structure Plan",
                "",
                "Root runtime files may contain project-owned instructions.",
                "Back them up centrally before clean runtime overwrite, then recover",
                "durable semantics into docs/agents evidence.",
                "",
                *sections,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path.relative_to(target).as_posix()


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    mode = "package" if package_source_available() else "installed"
    coverage = "source-package-contract" if mode == "package" else "installed-helper-contract"
    with tempfile.TemporaryDirectory(prefix="tes-root-context-") as tempdir:
        target = Path(tempdir)
        clean = analyze(target)
        if clean["status"] != "PASS":
            failures.append("empty project must pass")

        (target / "AGENTS.md").write_text(packaged_codex_bootloader(), encoding="utf-8")
        current = analyze(target)
        if current["status"] != "PASS":
            failures.append("current Tilly AGENTS.md must pass")

        (target / "AGENTS.md").write_text("# Project Agent Rules\n\nUse `bun run gate:closure` before final answers.\n", encoding="utf-8")
        project = analyze(target)
        if project["status"] != "NEEDS_REVIEW" or project["structure_gate"] != "required":
            failures.append("project root context must require structure gate")

        # Sanctioned-drift attestation (GAP-3): declaring the customized root file
        # suppresses its structure gate. When the optional oracle is not available
        # (e.g. an isolated installed-helper run that did not stage it), the
        # attestation degrades to suppress-nothing — so only the preserved
        # NEEDS_REVIEW is asserted there. Suppression itself is asserted only when
        # the oracle is importable.
        sanctioned_file = target / ".tes/root-context-sanctioned.txt"
        sanctioned_file.parent.mkdir(parents=True, exist_ok=True)
        sanctioned_file.write_text("AGENTS.md\n", encoding="utf-8")
        attested = analyze(target)
        if _sanctioned is not None:
            if attested["status"] != "PASS" or attested["structure_gate"] != "not_required":
                failures.append("sanctioned root drift must suppress the structure gate")
            if "AGENTS.md" not in attested.get("sanctioned_drift_paths", []):
                failures.append("analyze must report which root paths were sanctioned")
        else:
            # Oracle absent: attestation must be a no-op, gate stays required.
            if attested["status"] != "NEEDS_REVIEW" or attested["structure_gate"] != "required":
                failures.append("absent sanctioned oracle must degrade to suppress-nothing")
        sanctioned_file.write_text("# no entries\n", encoding="utf-8")
        unattested = analyze(target)
        if unattested["status"] != "NEEDS_REVIEW" or unattested["structure_gate"] != "required":
            failures.append("empty attestation must preserve the original NEEDS_REVIEW")
        sanctioned_file.unlink()

        (target / "CLAUDE.md").write_text("# CLAUDE.md\n\nTilly applies.\n\nProduction deploys require owner approval.\n", encoding="utf-8")
        mixed = analyze(target, write_plan=True)
        if not mixed["writes"] or not (target / mixed["writes"][0]).exists():
            failures.append("write_plan must create local evidence")

        (target / ".cursor/rules").mkdir(parents=True, exist_ok=True)
        (target / ".cursor/rules/project.mdc").write_text("Always use the internal emulator fixture.\n", encoding="utf-8")
        cursor = analyze(target)
        if cursor["requires_structure_count"] < 3:
            failures.append("custom Cursor root rule must be detected")

        backup_files = target / ".tes/bk/selftest/files"
        backup_files.mkdir(parents=True, exist_ok=True)
        (backup_files / "AGENTS.md").write_text("# Legacy\n\nRun `npm test` before release.\n", encoding="utf-8")
        backup = analyze(target, backup_id="selftest")
        if backup["source"] != "backup:selftest" or backup["status"] != "NEEDS_REVIEW":
            failures.append("backup root context analysis must inspect .tes/bk/<id>/files")

        core_v1 = "# TES Core\n\nUse `/tes-update`.\n"
        core_v2 = "# TES Core\n\nUse `/tes-update` and `/tes-map`.\n"
        overlay = "# Project Rules\n\nPreserve project release gates.\n"
        composed_v1 = compose_root_context(
            relpath="AGENTS.md",
            core_text=core_v1,
            existing_text=overlay,
            version=VERSION,
        )
        if composed_v1["status"] != "COMPOSED" or "Preserve project release gates" not in composed_v1["text"]:
            failures.append("composer must preserve legacy project overlay")
        composed_v2 = compose_root_context(
            relpath="AGENTS.md",
            core_text=core_v2,
            existing_text=str(composed_v1["text"]),
            version=VERSION,
            previous_core_sha256=str(composed_v1["core_sha256"]),
        )
        if composed_v2["status"] != "COMPOSED":
            failures.append("composer must update marked root context")
        extracted_v2 = extract_core(str(composed_v2["text"]))
        if not extracted_v2 or extracted_v2.get("sha256") != text_sha256(final_newline(core_v2)):
            failures.append("composer must expose current core hash")
        if "Preserve project release gates" not in str(composed_v2["text"]):
            failures.append("composer must preserve overlay during core update")
        composed_clean = compose_root_context(
            relpath="AGENTS.md",
            core_text=core_v2,
            existing_text=core_v1,
            version=VERSION,
            previous_core_sha256=text_sha256(final_newline(core_v1)),
        )
        if "TES:PROJECT-OVERLAY" not in str(composed_clean["text"]):
            failures.append("composer must always emit overlay boundary")
        if "Use `/tes-update`.\n<!-- TES:PROJECT-OVERLAY" in str(composed_clean["text"]):
            failures.append("previous TES core must not become project overlay")

        # Adversarial: a prior overlay already carries a fossilized TES:CORE
        # block from an earlier install. Composing again must yield exactly one
        # core and keep the legitimate project overlay intact.
        contaminated = "\n".join(
            [
                "<!-- TES:CORE BEGIN version=0.0.1 sha256=deadbeef adapter=codex path=AGENTS.md -->",
                "# TES Core",
                "",
                "Fossilized older core body.",
                CORE_END,
                "",
                "<!-- TES:PROJECT-OVERLAY BEGIN source=marked-overlay sha256=cafef00d path=AGENTS.md -->",
                "<!-- TES:CORE BEGIN version=0.0.1 sha256=deadbeef adapter=codex -->",
                "# TES Core",
                "",
                "Fossilized older core body.",
                CORE_END,
                "",
                "# Project Rules",
                "",
                "Preserve project release gates.",
                "@docs/agents/EXECUTION-LINE.md",
                OVERLAY_END,
                "",
            ]
        )
        composed_dedup = compose_root_context(
            relpath="AGENTS.md",
            core_text=core_v2,
            existing_text=contaminated,
            version=VERSION,
        )
        if str(composed_dedup["text"]).count("<!-- TES:CORE BEGIN") != 1:
            failures.append("composer must dedup nested TES:CORE in overlay to a single core")
        if "Preserve project release gates" not in str(composed_dedup["text"]):
            failures.append("composer must preserve legitimate overlay while deduping nested core")
        if "@docs/agents/EXECUTION-LINE.md" not in str(composed_dedup["text"]):
            failures.append("composer must preserve overlay pointers while deduping nested core")
        dedup_overlay = extract_overlay(str(composed_dedup["text"])) or {}
        if "Fossilized older core body" in str(dedup_overlay.get("text", "")):
            failures.append("fossilized core body must not survive inside the overlay")
        # Control: a clean overlay must remain byte-identical (no regression).
        clean_overlay = compose_root_context(
            relpath="AGENTS.md",
            core_text=core_v2,
            existing_text=str(composed_v2["text"]),
            version=VERSION,
            previous_core_sha256=str(composed_v2["core_sha256"]),
        )
        if str(clean_overlay["text"]).count("<!-- TES:CORE BEGIN") != 1:
            failures.append("clean overlay recompose must keep exactly one core")

    return {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "self_test_mode": mode,
        "coverage": coverage,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=["analyze"], default="analyze")
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--write-plan", action="store_true")
    parser.add_argument("--backup-id")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result = self_test() if args.self_test else analyze(args.target, write_plan=args.write_plan, backup_id=args.backup_id)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[root-context] " + result["status"])
    if result["status"] == "PASS":
        return 0
    if result["status"] == "NEEDS_REVIEW":
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
