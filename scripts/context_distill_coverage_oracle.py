#!/usr/bin/env python3
"""Context Distill Coverage Oracle.

P0 of GOAL-SUPER-SPEC-tes-inherited-context-canonical-source.

Enforces the non-loss contract of inherited-context distillation: when a
project's pre-existing root rules file (`CLAUDE.md` / `AGENTS.md`) is distilled
into the canonical overlay source (`docs/agents/PROJECT-CONTEXT.md`), every
non-trivial context unit in the archived original (`<root>.bak-<stamp>`) must be
either Covered (traceable to a canonical-source section) or
Discarded-with-reason (recorded with a reason from a closed set). A unit that is
neither is a coverage failure.

This module carries the P0 units of the Super SPEC:

- SPEC-001: the context-unit model (`detect_units`) and the coverage diff
  (`coverage_map`), classifying each `.bak` unit as Covered / Discarded /
  Uncovered, and emitting the coverage map as evidence.
- SPEC-002: the canonical-source section map (`CANONICAL_SECTIONS`,
  `home_section_for`) — every unit kind has a home among the 17 governed
  sections; no new schema is invented.
- SPEC-004 Phase 1: deterministic extract + archive (`phase1_distill`) — archive
  the original intact and extract units verbatim. No rewriting of meaning.

It does NOT render roots (P1) or touch the installer (P2). The asymmetric Claude
`@`-import / Codex materialized-block renderers are out of scope here by design.

Usage:

    python3 scripts/context_distill_coverage_oracle.py --self-test
    python3 scripts/context_distill_coverage_oracle.py \
        --bak path/to/CLAUDE.md.bak-<stamp> \
        --source docs/agents/PROJECT-CONTEXT.md \
        [--discards path/to/discards.json]

The discards file (optional) is a JSON list of objects:
    [{"unit": "<verbatim unit text>", "reason": "obsolete"}]
with reason drawn from the closed set in DISCARD_REASONS.

Exit status: 0 when coverage holds (OVERLAY_COVERED), 1 otherwise
(NEEDS_REVIEW_COVERAGE) or on a usage/IO error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.170"

# SPEC-002 — the 17 governed sections of docs/agents/PROJECT-CONTEXT.md, mirrored
# from scripts/project_context_oracle.py REQUIRED_SECTIONS. The canonical source
# schema is reused, never re-invented; this is only the map for unit homing.
CANONICAL_SECTIONS: tuple[str, ...] = (
    "# Tilly Project Context",
    "## Identity",
    "## Initial Semantic Signals",
    "## Maximum-Depth Initialization Contract",
    "## Active Agent Refinement Contract",
    "## Coverage",
    "## Project Territories",
    "## Semantic Territory Guide",
    "## Weak Anchor Triage",
    "## Caution Zones",
    "## Workspace Boundaries",
    "## Source Anchors Read First",
    "## Runtime And Governance Surfaces",
    "## Recommended Deep Reads",
    "## Next Work Guidance",
    "## Open Context Questions",
    "## Maintenance Rule",
)

# SPEC-002 — every context-unit kind has a home section. A distilled unit is
# Covered when its verbatim payload is traceable under its home section (or any
# section, for robustness; the home map is guidance for the distiller).
HOME_SECTION_FOR_KIND: dict[str, str] = {
    "directive": "## Next Work Guidance",
    "convention": "## Semantic Territory Guide",
    "routing": "## Source Anchors Read First",
    "architecture": "## Project Territories",
    "command": "## Runtime And Governance Surfaces",
    "constraint": "## Workspace Boundaries",
}

# Closed set of discard reasons (SPEC-001). No silent drops; every discard names
# one of these. `superseded-by-<unit>` is matched by prefix.
DISCARD_REASONS = ("redundant-with-tes-core", "obsolete", "duplicate")
SUPERSEDED_PREFIX = "superseded-by-"

# Phrases that are NOT context units — taste/vibe with no observable behavior.
TRIVIAL_PHRASES = (
    "be careful",
    "write good code",
    "use best practices",
    "do your best",
    "be thorough",
)

# Heuristic unit detectors (deterministic, SPEC-001). Each returns the unit kind
# for a line that carries a non-trivial, behavior-changing assertion.
_DIRECTIVE_RE = re.compile(r"^\s*(never|always|do not|don't|must|prefer|avoid)\b", re.IGNORECASE)
_COMMAND_RE = re.compile(r"`([^`]*\b(npm|pnpm|yarn|bun|make|python3?|pytest|go|cargo|docker)\b[^`]*)`", re.IGNORECASE)
_ROUTING_RE = re.compile(r"\b(docs?|api|tests?|schema)\b.*\b(in|under|live[s]? in|at)\b", re.IGNORECASE)
_CONSTRAINT_RE = re.compile(r"\b(do not touch|never edit|off-limits|read-only|secret[s]?|credential[s]?)\b", re.IGNORECASE)
_CONVENTION_RE = re.compile(r"\b(naming|convention|file layout|import order|format|style)\b", re.IGNORECASE)
_ARCH_RE = re.compile(r"\b(we use|architecture|event sourcing|monorepo|microservice[s]?|layered|hexagonal)\b", re.IGNORECASE)


def normalize(text: str) -> str:
    """Collapse whitespace and lowercase for traceability matching."""
    return re.sub(r"\s+", " ", text).strip().lower()


def is_trivial(line: str) -> bool:
    low = normalize(line)
    if not low:
        return True
    return any(phrase in low for phrase in TRIVIAL_PHRASES)


def classify_line(line: str) -> str | None:
    """Return the context-unit kind for a line, or None if it is not a unit."""
    if is_trivial(line):
        return None
    # Command takes priority: a runnable command embedded anywhere is a unit.
    if _COMMAND_RE.search(line):
        return "command"
    if _CONSTRAINT_RE.search(line):
        return "constraint"
    if _DIRECTIVE_RE.search(line):
        return "directive"
    if _ARCH_RE.search(line):
        return "architecture"
    if _ROUTING_RE.search(line):
        return "routing"
    if _CONVENTION_RE.search(line):
        return "convention"
    return None


def _strip_markup(line: str) -> str:
    """Strip leading list/heading markup so units compare cleanly."""
    return re.sub(r"^\s*([-*+]|\d+\.|#{1,6})\s+", "", line).strip()


def detect_units(text: str) -> list[dict[str, str]]:
    """SPEC-001 — extract context units from a root rules file, verbatim.

    Returns a list of {kind, text, key} where `text` is the verbatim line and
    `key` is its normalized form used for traceability. Order-preserving and
    deduplicated by key.
    """
    units: list[dict[str, str]] = []
    seen: set[str] = set()
    in_code_fence = False
    for raw in text.splitlines():
        if raw.strip().startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        candidate = _strip_markup(raw)
        if not candidate:
            continue
        kind = classify_line(candidate)
        if kind is None:
            continue
        key = normalize(candidate)
        if key in seen:
            continue
        seen.add(key)
        units.append({"kind": kind, "text": candidate, "key": key})
    return units


def home_section_for(kind: str) -> str:
    return HOME_SECTION_FOR_KIND.get(kind, "## Next Work Guidance")


def is_traceable(unit_key: str, source_text: str) -> bool:
    """A unit is Covered when its normalized payload (or the substantive token
    span of it) appears in the normalized canonical source."""
    source_norm = normalize(source_text)
    if unit_key in source_norm:
        return True
    # Fall back to a substantive-token overlap: a unit is traceable if a
    # contiguous span of its meaningful tokens (>=4 words, or its command body)
    # appears in the source. This tolerates the distiller rewrapping prose while
    # still catching genuine loss of the payload.
    tokens = [tok for tok in re.findall(r"[a-z0-9_./-]+", unit_key) if len(tok) > 1]
    if len(tokens) >= 4:
        span = " ".join(tokens[:6])
        if span in source_norm:
            return True
    # Command bodies: the runnable command itself must survive verbatim.
    cmd = _COMMAND_RE.search(unit_key)
    if cmd and normalize(cmd.group(1)) in source_norm:
        return True
    return False


def _valid_discard_reason(reason: str) -> bool:
    if reason in DISCARD_REASONS:
        return True
    return reason.startswith(SUPERSEDED_PREFIX) and len(reason) > len(SUPERSEDED_PREFIX)


def coverage_map(
    bak_text: str,
    source_text: str,
    discards: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """SPEC-001 — the coverage diff. Classify every `.bak` unit as Covered,
    Discarded (with a valid reason), or Uncovered (the failure state).

    Returns a structured result with the full coverage map as evidence.
    """
    discards = discards or []
    discard_by_key: dict[str, str] = {}
    invalid_discards: list[dict[str, str]] = []
    for entry in discards:
        unit_text = entry.get("unit", "")
        reason = entry.get("reason", "")
        key = normalize(unit_text)
        if not key:
            continue
        if _valid_discard_reason(reason):
            discard_by_key[key] = reason
        else:
            invalid_discards.append({"unit": unit_text, "reason": reason})

    units = detect_units(bak_text)
    mapped: list[dict[str, str]] = []
    covered = discarded = uncovered = 0
    for unit in units:
        key = unit["key"]
        if is_traceable(key, source_text):
            state, detail = "covered", home_section_for(unit["kind"])
            covered += 1
        elif key in discard_by_key:
            state, detail = "discarded", discard_by_key[key]
            discarded += 1
        else:
            state, detail = "uncovered", ""
            uncovered += 1
        mapped.append({"kind": unit["kind"], "text": unit["text"], "state": state, "detail": detail})

    failures: list[str] = []
    for entry in invalid_discards:
        failures.append(f"discard reason not in closed set: {entry['reason']!r} for unit {entry['unit']!r}")
    for entry in mapped:
        if entry["state"] == "uncovered":
            failures.append(f"uncovered {entry['kind']}: {entry['text']!r}")

    status = "OVERLAY_COVERED" if not failures else "NEEDS_REVIEW_COVERAGE"
    return {
        "status": status,
        "units_total": len(units),
        "covered": covered,
        "discarded": discarded,
        "uncovered": uncovered,
        "coverage_map": mapped,
        "failures": failures,
        "version": VERSION,
    }


def phase1_distill(root_text: str) -> str:
    """SPEC-004 Phase 1 — deterministic extract (verbatim).

    Produce a minimal canonical-source body that homes every detected unit under
    its section, verbatim, with no rewording. This is the deterministic floor;
    the optional agent condense (Phase 2) is out of scope for this oracle.
    Archiving the original is the caller's responsibility (see archive_root);
    this function never mutates the original.
    """
    units = detect_units(root_text)
    by_section: dict[str, list[str]] = {}
    for unit in units:
        by_section.setdefault(home_section_for(unit["kind"]), []).append(unit["text"])
    lines = ["# Tilly Project Context", "", "## Identity", "", "Inherited project context (Phase 1 verbatim extract).", ""]
    for section in CANONICAL_SECTIONS:
        if section in ("# Tilly Project Context", "## Identity"):
            continue
        lines.append(section)
        lines.append("")
        for item in by_section.get(section, []):
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def archive_root(root_path: Path, stamp: str) -> Path:
    """Archive the pre-existing root intact as <root>.bak-<stamp> (mandatory
    before any destructive write; the .bak is the coverage oracle's truth)."""
    bak = root_path.with_name(f"{root_path.name}.bak-{stamp}")
    bak.write_text(root_path.read_text(encoding="utf-8"), encoding="utf-8")
    return bak


# ---------------------------------------------------------------------------
# SPEC-000 — neutral rich-root fixtures (generic identity only).
# ---------------------------------------------------------------------------

RICH_ROOT_FIXTURE = """\
# Project Rules

Never commit directly to main; open a pull request instead.
Always run `npm test` before closeout.

## Conventions
- Naming convention: components use PascalCase, files use kebab-case.
- Import order: external packages first, then internal modules.

## Architecture
We use event sourcing for the orders domain.

## Routing
API docs live in docs/api/.

## Boundaries
Do not touch the legacy/ directory.
Secrets are read from the vault, never committed.

## Build
Run `pnpm build` to produce the bundle.

## Notes
Be careful and write good code.
"""


def make_rich_root(target: Path) -> Path:
    root = target / "CLAUDE.md"
    root.write_text(RICH_ROOT_FIXTURE, encoding="utf-8")
    return root


def faithful_source(bak_text: str) -> str:
    """A canonical source that covers every unit (the green case)."""
    return phase1_distill(bak_text)


def lossy_source(bak_text: str, drop_substring: str) -> str:
    """A canonical source that silently drops one unit (the red case)."""
    full = phase1_distill(bak_text)
    return "\n".join(line for line in full.splitlines() if drop_substring.lower() not in line.lower()) + "\n"


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-ctx-distill-") as tempdir:
        target = Path(tempdir)
        root = make_rich_root(target)

        # SPEC-004 Phase 1: archive must be byte-faithful and never mutate root.
        original = root.read_text(encoding="utf-8")
        bak = archive_root(root, "selftest")
        if bak.read_text(encoding="utf-8") != original:
            failures.append("archive_root: .bak is not byte-faithful to the original root")
        if root.read_text(encoding="utf-8") != original:
            failures.append("archive_root: original root was mutated (must be intact)")

        bak_text = bak.read_text(encoding="utf-8")

        # SPEC-001: the rich root must yield the expected unit kinds.
        units = detect_units(bak_text)
        kinds = {u["kind"] for u in units}
        for required in ("directive", "command", "constraint", "routing", "architecture", "convention"):
            if required not in kinds:
                failures.append(f"detect_units: missing expected unit kind {required!r}")
        # Trivial lines must NOT be units.
        if any("write good code" in normalize(u["text"]) for u in units):
            failures.append("detect_units: classified a trivial 'write good code' line as a unit")

        # GREEN: a faithful distillation covers everything → OVERLAY_COVERED.
        green = coverage_map(bak_text, faithful_source(bak_text))
        if green["status"] != "OVERLAY_COVERED":
            failures.append(f"faithful distillation must be OVERLAY_COVERED, got {green['status']}: {green['failures']}")
        if green["uncovered"] != 0:
            failures.append(f"faithful distillation must have zero uncovered, got {green['uncovered']}")

        # RED: a deliberately dropped directive with no reason → coverage failure.
        red = coverage_map(bak_text, lossy_source(bak_text, "npm test"))
        if red["status"] != "NEEDS_REVIEW_COVERAGE":
            failures.append("dropping a directive without a reason must be NEEDS_REVIEW_COVERAGE")
        if not any("npm test" in f for f in red["failures"]):
            failures.append("coverage failure must name the dropped 'npm test' command")

        # RED→GREEN: the same drop becomes acceptable when discarded-with-reason.
        excused = coverage_map(
            bak_text,
            lossy_source(bak_text, "npm test"),
            discards=[{"unit": "Always run `npm test` before closeout.", "reason": "obsolete"}],
        )
        if excused["status"] != "OVERLAY_COVERED":
            failures.append(f"discarded-with-reason must restore OVERLAY_COVERED, got {excused['status']}: {excused['failures']}")

        # NEGATIVE: an invalid discard reason must fail (closed set enforced).
        bad_reason = coverage_map(
            bak_text,
            lossy_source(bak_text, "npm test"),
            discards=[{"unit": "Always run `npm test` before closeout.", "reason": "i-felt-like-it"}],
        )
        if bad_reason["status"] != "NEEDS_REVIEW_COVERAGE":
            failures.append("an out-of-set discard reason must fail the gate")

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "version": VERSION,
    }


def _load_discards(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("discards file must be a JSON list of {unit, reason} objects")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Context distill coverage oracle (P0).")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--bak", type=Path, help="Path to the archived original root (<root>.bak-<stamp>).")
    parser.add_argument("--source", type=Path, help="Path to the canonical source (docs/agents/PROJECT-CONTEXT.md).")
    parser.add_argument("--discards", type=Path, help="Optional JSON list of {unit, reason} discards.")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2))
        print(f"[context-distill-coverage] {result['status']}")
        return 0 if result["status"] == "PASS" else 1

    if not args.bak or not args.source:
        parser.error("either --self-test, or both --bak and --source are required")

    try:
        bak_text = args.bak.read_text(encoding="utf-8")
        source_text = args.source.read_text(encoding="utf-8")
        discards = _load_discards(args.discards)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[context-distill-coverage] ERROR: {exc}", file=sys.stderr)
        return 1

    result = coverage_map(bak_text, source_text, discards)
    if not args.json_only:
        print(json.dumps(result, indent=2))
    print(f"[context-distill-coverage] {result['status']}")
    return 0 if result["status"] == "OVERLAY_COVERED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
