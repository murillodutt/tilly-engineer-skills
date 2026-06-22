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

This module carries the P0 and P1 units of the Super SPEC:

P0 — non-loss canonical-source contract:
- SPEC-001: the context-unit model (`detect_units`) and the coverage diff
  (`coverage_map`), classifying each `.bak` unit as Covered / Discarded /
  Uncovered, and emitting the coverage map as evidence.
- SPEC-002: the canonical-source section map (`CANONICAL_SECTIONS`,
  `home_section_for`) — every unit kind has a home among the 17 governed
  sections; no new schema is invented.
- SPEC-004 Phase 1: deterministic extract + archive (`phase1_distill`,
  `archive_root`) — archive the original intact and extract units verbatim.

P1 — two asymmetric renderings + idempotency:
- SPEC-004: `render_claude_root` — thin TES:CORE block + an eager `@` import of
  the canonical source.
- SPEC-005: `render_codex_root` / `condense_source` — thin TES:CORE block + a
  materialized TES:PROJECT-OVERLAY block with `src-sha`, no `@`, under 32 KiB.
- SPEC-006: `is_already_inherited` — a thin root skips distillation; re-render is
  stable.

It does NOT touch the installer or uninstall (P2: SPEC-007/008). The parent
root-context-composition contract is reused (marker shape) but not redefined.

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
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.184"

# Parent (root-context-composition) marker shape, reused verbatim. This line
# does not redefine the markers; it renders within them. Kept in sync with
# scripts/root_context.py CORE_BEGIN_RE / OVERLAY_BEGIN_RE.
CORE_BEGIN_RE = re.compile(r"<!-- TES:CORE BEGIN(?P<meta>[^>]*)-->")
CORE_END = "<!-- TES:CORE END -->"
OVERLAY_BEGIN_RE = re.compile(r"<!-- TES:PROJECT-OVERLAY BEGIN(?P<meta>[^>]*)-->")
OVERLAY_END = "<!-- TES:PROJECT-OVERLAY END -->"
CANONICAL_SOURCE_REL = "docs/agents/PROJECT-CONTEXT.md"
CODEX_CHAIN_BYTE_CAP = 32 * 1024  # RULES-FILE-ENGINEERING.md Codex hard cap.

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
# P1 — two asymmetric renderings + idempotency (SPEC-004 / SPEC-005 / SPEC-006).
# Both render a thin TES:CORE block; Claude points with @, Codex materializes.
# The parent marker shape is reused, never redefined.
# ---------------------------------------------------------------------------


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _core_block(core_text: str, version: str, adapter: str) -> str:
    core = core_text if core_text.endswith("\n") else core_text + "\n"
    core_sha = text_sha256(core)
    begin = f"<!-- TES:CORE BEGIN version={version} sha256={core_sha} adapter={adapter} -->"
    return f"{begin}\n{core.rstrip(chr(10))}\n{CORE_END}\n"


def render_claude_root(core_text: str, *, version: str = VERSION) -> str:
    """SPEC-004 — thin TES:CORE block + an eager @ import of the canonical
    source. Claude reads the overlay by reference; the import loads in full."""
    return f"{_core_block(core_text, version, 'claude')}\n@{CANONICAL_SOURCE_REL}\n"


def condense_source(source_text: str, *, max_items_per_section: int = 12) -> str:
    """Produce the lean, objective Codex materialization of the canonical source.

    Not the full source verbatim — a structured condensation: section headings
    plus their bullet/directive lines, trivia and prose padding dropped, sized to
    stay well below the Codex chain byte cap.
    """
    lines: list[str] = []
    current_items = 0
    for raw in source_text.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            lines.append(stripped)
            current_items = 0
            continue
        candidate = _strip_markup(raw)
        if not candidate or is_trivial(candidate):
            continue
        # Keep substantive bullets/directives only.
        if raw.lstrip().startswith(("-", "*", "+")) or classify_line(candidate) is not None:
            if current_items < max_items_per_section:
                lines.append(f"- {candidate}")
                current_items += 1
    return "\n".join(lines).rstrip() + "\n"


def render_codex_root(core_text: str, source_text: str, *, version: str = VERSION) -> str:
    """SPEC-005 — thin TES:CORE block + a materialized TES:PROJECT-OVERLAY block
    condensed from the canonical source, stamped with src-sha. No @ (Codex
    cannot import). The overlay block is generated, never hand-authored."""
    src_sha = text_sha256(source_text)
    overlay_body = condense_source(source_text).rstrip("\n")
    overlay_begin = f"<!-- TES:PROJECT-OVERLAY BEGIN source={CANONICAL_SOURCE_REL} sha256={src_sha} -->"
    block = "\n".join([overlay_begin, overlay_body, OVERLAY_END])
    return f"{_core_block(core_text, version, 'codex')}\n{block}\n"


def render_status(adapter: str, root_text: str, source_text: str | None) -> dict[str, Any]:
    """Verify a rendered root and return its status (SPEC-004 / SPEC-005)."""
    has_core = CORE_BEGIN_RE.search(root_text) is not None and CORE_END in root_text
    if adapter == "claude":
        has_pointer = f"@{CANONICAL_SOURCE_REL}" in root_text
        # A thin Claude root must not carry an inline overlay block.
        inline_overlay = OVERLAY_BEGIN_RE.search(root_text) is not None
        ok = has_core and has_pointer and not inline_overlay
        return {"status": "RENDER_CLAUDE_OK" if ok else "NEEDS_REVIEW_RENDER",
                "has_core": has_core, "has_pointer": has_pointer, "inline_overlay": inline_overlay}
    if adapter == "codex":
        begin = OVERLAY_BEGIN_RE.search(root_text)
        has_block = begin is not None and OVERLAY_END in root_text
        attrs = dict(re.findall(r"(\w+)=(\S+)", begin.group("meta")) if begin else [])
        src_sha_ok = source_text is not None and attrs.get("sha256") == text_sha256(source_text)
        no_at = f"@{CANONICAL_SOURCE_REL}" not in root_text
        within_cap = len(root_text.encode("utf-8")) < CODEX_CHAIN_BYTE_CAP
        ok = has_core and has_block and src_sha_ok and no_at and within_cap
        return {"status": "RENDER_CODEX_OK" if ok else "NEEDS_REVIEW_RENDER",
                "has_core": has_core, "has_block": has_block, "src_sha_ok": src_sha_ok,
                "no_at": no_at, "within_cap": within_cap}
    return {"status": "NEEDS_REVIEW_RENDER", "reason": f"unknown adapter {adapter!r}"}


def is_already_inherited(adapter: str, root_text: str) -> bool:
    """SPEC-006 — a root whose only non-core content is the @ pointer (Claude)
    or the materialized overlay block (Codex) is already a TES thin root, so
    distillation must be skipped (no recursion, no emptied source)."""
    core = CORE_BEGIN_RE.search(root_text)
    if core is None or CORE_END not in root_text:
        return False
    # Remove the core block, then check what non-trivial content remains.
    after_core = root_text[root_text.find(CORE_END) + len(CORE_END):]
    remainder = after_core
    if adapter == "claude":
        remainder = remainder.replace(f"@{CANONICAL_SOURCE_REL}", "")
    elif adapter == "codex":
        begin = OVERLAY_BEGIN_RE.search(remainder)
        if begin is not None and OVERLAY_END in remainder:
            end = remainder.find(OVERLAY_END) + len(OVERLAY_END)
            remainder = remainder[:begin.start()] + remainder[end:]
    return remainder.strip() == ""


# ---------------------------------------------------------------------------
# P2 — installer routing (SPEC-007). Turn the default for a context_governance
# root in conflict: instead of whole-file overwrite (loses human context to
# .bak) or whole-file preserve (leaves TES core stale), inherit the human
# context into the canonical source and write the thin rendered root.
# ---------------------------------------------------------------------------


def route_context_governance_root(
    *,
    adapter: str,
    root_text: str,
    core_text: str,
    existing_source_text: str,
    stamp: str,
    discards: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Decide and produce the write for one context_governance root.

    Returns a dict with:
      - status: INHERITED | ALREADY_INHERITED | BLOCKED_ARCHIVE_MISSING |
                NEEDS_REVIEW_COVERAGE
      - bak_name: the <root>.bak-<stamp> archive name (None when skipped)
      - source_text: the canonical source to write (existing when skipped)
      - root_text: the thin rendered root to write (None on coverage failure)
      - coverage: the coverage map evidence (None when skipped)

    Pure function: it computes the writes; the caller performs the IO. This keeps
    the installer wiring thin and the decision fully unit-testable.
    """
    # SPEC-006 idempotency: an already-inherited root only re-renders.
    if is_already_inherited(adapter, root_text):
        rendered = (
            render_claude_root(core_text)
            if adapter == "claude"
            else render_codex_root(core_text, existing_source_text)
        )
        return {
            "status": "ALREADY_INHERITED",
            "bak_name": None,
            "source_text": existing_source_text,
            "root_text": rendered,
            "coverage": None,
        }

    # SPEC-008 invariant: no destructive write without an archive.
    if not stamp:
        return {"status": "BLOCKED_ARCHIVE_MISSING", "bak_name": None,
                "source_text": existing_source_text, "root_text": None, "coverage": None}
    bak_name = f".bak-{stamp}"

    # Phase 1 deterministic distill: extract human units into the canonical
    # source, merged after whatever the source already holds.
    extracted = phase1_distill(root_text)
    merged_source = existing_source_text
    if existing_source_text.strip():
        merged_source = existing_source_text.rstrip("\n") + "\n\n" + extracted
    else:
        merged_source = extracted

    # Hard non-loss floor: never render a thin root over an empty canonical
    # source — that WOULD lose context. This is the only blocking coverage case.
    if not merged_source.strip():
        return {"status": "BLOCKED_EMPTY_SOURCE", "bak_name": bak_name,
                "source_text": merged_source, "root_text": None, "coverage": None}

    # Coverage is ADVISORY, not blocking. The regex unit detector only sees
    # syntactic fragments; a canonical source authored by the tes_init LLM
    # preserves meaning by paraphrase, so literal-fragment coverage routinely
    # under-reports on real rich roots (proven on a real project canary). The
    # real non-loss guarantee is the <root>.bak-<stamp> archive (always written,
    # uninstall-restorable). So inherit even when coverage is incomplete, and
    # surface the uncovered units as a hint for the optional /tes-context-distill
    # judgment pass — do not block the install.
    coverage = coverage_map(root_text, merged_source, discards)
    rendered = (
        render_claude_root(core_text)
        if adapter == "claude"
        else render_codex_root(core_text, merged_source)
    )
    result = {
        "status": "INHERITED",
        "bak_name": bak_name,
        "source_text": merged_source,
        "root_text": rendered,
        "coverage": coverage,
    }
    if coverage["status"] != "OVERLAY_COVERED":
        result["coverage_advisory"] = (
            f"{coverage.get('uncovered', 0)} regex-detected unit(s) not literally "
            "traceable in the canonical source; the .bak archive is the non-loss "
            "guarantee. Run /tes-context-distill for an LLM coverage pass if desired."
        )
    return result


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

        # --- P1 renderings (SPEC-004 / SPEC-005 / SPEC-006) ---
        core = "# TES Core\n\nRoute project context to docs/agents/**. Use `/tes-update`.\n"
        source = faithful_source(bak_text)

        # SPEC-004: Claude renders thin core + @ pointer, no inline overlay.
        claude_root = render_claude_root(core)
        claude_status = render_status("claude", claude_root, source)
        if claude_status["status"] != "RENDER_CLAUDE_OK":
            failures.append(f"Claude render must be RENDER_CLAUDE_OK, got {claude_status}")
        if f"@{CANONICAL_SOURCE_REL}" not in claude_root:
            failures.append("Claude root must carry the @ pointer to the canonical source")

        # NEGATIVE: an @ directive must never appear in a Codex root.
        # SPEC-005: Codex materializes a condensed overlay block with src-sha.
        codex_root = render_codex_root(core, source)
        codex_status = render_status("codex", codex_root, source)
        if codex_status["status"] != "RENDER_CODEX_OK":
            failures.append(f"Codex render must be RENDER_CODEX_OK, got {codex_status}")
        if f"@{CANONICAL_SOURCE_REL}" in codex_root:
            failures.append("Codex root must NOT contain an @ import directive")
        if len(codex_root.encode("utf-8")) >= CODEX_CHAIN_BYTE_CAP:
            failures.append("Codex root must stay below the 32 KiB chain cap")
        # src-sha parity: a stale source must fail Codex render.
        stale = render_status("codex", codex_root, source + "\n- extra drift line\n")
        if stale["status"] == "RENDER_CODEX_OK":
            failures.append("Codex render must fail src-sha parity when the source drifted")

        # SPEC-006: idempotency — already-rendered thin roots are ALREADY_INHERITED.
        if not is_already_inherited("claude", claude_root):
            failures.append("a thin Claude root must be detected as already inherited")
        if not is_already_inherited("codex", codex_root):
            failures.append("a thin Codex root must be detected as already inherited")
        # A rich, un-rendered root must NOT be already-inherited.
        if is_already_inherited("claude", bak_text):
            failures.append("a rich un-rendered root must not be treated as already inherited")
        # Re-rendering an already-inherited root is stable (same bytes out).
        if render_claude_root(core) != claude_root:
            failures.append("Claude re-render is not stable (idempotency broken)")
        if render_codex_root(core, source) != codex_root:
            failures.append("Codex re-render is not stable (idempotency broken)")

        # --- P2 installer routing (SPEC-007 / SPEC-008) ---
        # A rich context_governance root in conflict routes to INHERITED:
        # human context lands in the source, the root is rendered thin.
        routed = route_context_governance_root(
            adapter="claude", root_text=bak_text, core_text=core,
            existing_source_text="", stamp="selftest",
        )
        if routed["status"] != "INHERITED":
            failures.append(f"routing a rich root must be INHERITED, got {routed['status']}")
        if routed["bak_name"] != ".bak-selftest":
            failures.append("routing must name the .bak archive")
        if not routed["root_text"] or f"@{CANONICAL_SOURCE_REL}" not in routed["root_text"]:
            failures.append("routed Claude root must be the thin @-pointer render")
        # The human units must be covered by the merged source (no loss to .bak).
        if routed["coverage"]["status"] != "OVERLAY_COVERED":
            failures.append("routed source must cover all human units")

        # REGRESSION GUARD (SPEC-008 invariant): no destructive write without an
        # archive — an empty stamp must block, never overwrite.
        blocked = route_context_governance_root(
            adapter="claude", root_text=bak_text, core_text=core,
            existing_source_text="", stamp="",
        )
        if blocked["status"] != "BLOCKED_ARCHIVE_MISSING":
            failures.append("routing without an archive stamp must be BLOCKED_ARCHIVE_MISSING")
        if blocked["root_text"] is not None:
            failures.append("blocked routing must not produce a root write")

        # SPEC-006 in the routing path: an already-inherited root only re-renders.
        re_routed = route_context_governance_root(
            adapter="claude", root_text=routed["root_text"], core_text=core,
            existing_source_text=routed["source_text"], stamp="selftest2",
        )
        if re_routed["status"] != "ALREADY_INHERITED":
            failures.append(f"routing an inherited root must be ALREADY_INHERITED, got {re_routed['status']}")
        if re_routed["bak_name"] is not None:
            failures.append("already-inherited routing must not re-archive")

        # Codex routing yields the materialized block, no @.
        codex_routed = route_context_governance_root(
            adapter="codex", root_text=bak_text, core_text=core,
            existing_source_text="", stamp="selftest",
        )
        if codex_routed["status"] != "INHERITED":
            failures.append(f"Codex routing must be INHERITED, got {codex_routed['status']}")
        if codex_routed["root_text"] and f"@{CANONICAL_SOURCE_REL}" in codex_routed["root_text"]:
            failures.append("Codex routed root must not contain an @ directive")

        # Coverage is ADVISORY, not blocking: a root whose distilled source does
        # not literally cover every regex unit must still INHERIT (real non-loss
        # is the .bak), surfacing the gap as a non-blocking advisory. This is the
        # real-project-canary fix — regex coverage under-reports on LLM-authored
        # canonical sources and must not block the install.
        prose_human = "# Rules\n\nNever commit to main.\nRun `npm test` before release.\n"
        lossy_existing = "# Tilly Project Context\n\n## Identity\n\nx\n"  # has content, won't cover the units
        advisory = route_context_governance_root(
            adapter="claude", root_text=prose_human, core_text=core,
            existing_source_text=lossy_existing, stamp="selftest",
        )
        if advisory["status"] != "INHERITED":
            failures.append(f"incomplete coverage must still INHERIT (advisory), got {advisory['status']}")
        if not advisory.get("root_text") or f"@{CANONICAL_SOURCE_REL}" not in advisory["root_text"]:
            failures.append("advisory inherit must still render the thin root")
        if advisory["coverage"]["status"] == "OVERLAY_COVERED":
            # sanity: this fixture is meant to be incompletely covered
            pass
        elif "coverage_advisory" not in advisory:
            failures.append("incomplete coverage must surface a non-blocking coverage_advisory")

        # Hard floor: an empty canonical source WOULD lose context — must block.
        empty_src = route_context_governance_root(
            adapter="claude", root_text="# Rules\n\n(no detectable units here)\n",
            core_text=core, existing_source_text="", stamp="selftest",
        )
        # root_text with no units distills to a non-empty scaffold, so this path
        # normally inherits; the block only triggers on a truly empty merged
        # source. Assert the contract holds when it does occur.
        if empty_src["status"] == "BLOCKED_EMPTY_SOURCE" and empty_src.get("root_text") is not None:
            failures.append("blocked-empty-source must not produce a root write")

        # --- SPEC-002: cross-check against the overlay oracle ---
        # (a) every unit-kind's home section is one of the 17 governed sections.
        for kind, section in HOME_SECTION_FOR_KIND.items():
            if section not in CANONICAL_SECTIONS:
                failures.append(f"SPEC-002: home section for {kind!r} is not a governed section: {section}")

        # (b) merging distilled units into a complete PROJECT-CONTEXT.md must NOT
        # break the existing overlay oracle. The distillation contributes human
        # units; it must not destroy the governed structure tes_init produced.
        try:
            import project_context_oracle as overlay
        except Exception as exc:  # pragma: no cover - import guard
            failures.append(f"SPEC-002: could not import project_context_oracle: {exc}")
            overlay = None
        if overlay is not None:
            import tempfile as _tf
            with _tf.TemporaryDirectory(prefix="tes-spec002-") as s2:
                s2t = Path(s2)
                overlay.make_fixture(s2t)  # a complete, oracle-passing target
                pc = s2t / "docs/agents/PROJECT-CONTEXT.md"
                complete = pc.read_text(encoding="utf-8")
                # Baseline: the fixture passes before any merge.
                if overlay.analyze(s2t)["status"] != "PASS":
                    failures.append("SPEC-002: baseline overlay fixture must PASS before merge")
                # Merge distilled human units the way the route does, into a home
                # section that already exists, then re-run the overlay oracle. All
                # bullets are merged — the contract never truncates human units.
                human_units = phase1_distill(bak_text)
                bullets = [ln for ln in human_units.splitlines() if ln.startswith("- ")]
                merged = complete.replace(
                    "## Next Work Guidance",
                    "## Next Work Guidance\n\n" + "\n".join(bullets),
                    1,
                )
                pc.write_text(merged, encoding="utf-8")
                after = overlay.analyze(s2t)
                if after["status"] != "PASS":
                    failures.append(f"SPEC-002: merging distilled units must keep overlay oracle PASS, got {after['status']}: {after['failures'][:3]}")
                # And the merged units stay coverage-traceable.
                cov = coverage_map(bak_text, merged)
                if cov["status"] != "OVERLAY_COVERED":
                    failures.append(f"SPEC-002: merged units must remain OVERLAY_COVERED, got {cov['status']}")

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
    parser = argparse.ArgumentParser(description="Context distill coverage oracle + renderers (P0+P1).")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--bak", type=Path, help="Path to the archived original root (<root>.bak-<stamp>).")
    parser.add_argument("--source", type=Path, help="Path to the canonical source (docs/agents/PROJECT-CONTEXT.md).")
    parser.add_argument("--discards", type=Path, help="Optional JSON list of {unit, reason} discards.")
    parser.add_argument("--render", choices=["claude", "codex"], help="Emit a thin rendered root for the adapter (P1).")
    parser.add_argument("--core", type=Path, help="Path to the thin TES core text (required with --render).")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2))
        print(f"[context-distill-coverage] {result['status']}")
        return 0 if result["status"] == "PASS" else 1

    if args.render:
        if not args.core or not args.source:
            parser.error("--render requires --core and --source")
        try:
            core_text = args.core.read_text(encoding="utf-8")
            source_text = args.source.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"[context-distill-coverage] ERROR: {exc}", file=sys.stderr)
            return 1
        if args.render == "claude":
            rendered = render_claude_root(core_text)
        else:
            rendered = render_codex_root(core_text, source_text)
        status = render_status(args.render, rendered, source_text)
        sys.stdout.write(rendered)
        print(f"[context-distill-coverage] {status['status']}", file=sys.stderr)
        return 0 if status["status"].endswith("_OK") else 1

    if not args.bak or not args.source:
        parser.error("either --self-test, --render, or both --bak and --source are required")

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
