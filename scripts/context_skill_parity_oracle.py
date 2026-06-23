#!/usr/bin/env python3
"""Context/skill parity oracle (bootloader-to-skill migration, SPEC-005).

Proves that thinning the adapter bootloaders did not drop certified knowledge.
The contract is the persistent concept inventory written by SPEC-000
(docs/evidence/reports/system-analysis/bootloader-concept-inventory-2026-06-04.md);
this oracle reads its embedded YAML rather than hardcoding the concept list, so
the inventory stays the single source of truth and the oracle is not an
example-specific literal list.

Three checks per concept (the two layers the owner asked for, plus budgets):

1. Semantic, per concept (the layer beyond byte matching):
   - keep-as-anchor: anchor_markers must be present in the bootloader, AND when
     expansion_required, skill_markers must be present in the host skill/rule.
   - already-in-skill / move-to-skill: skill_markers must be present in the host
     skill/rule (the knowledge has a single home there).
2. Byte-level (the owner's baseline): no multi-line paragraph is byte-identical
   between an anchor bootloader and its host skill/rule (the anchor-not-copy
   disease). One-line pointer sentences are allowed.
3. Anchor budgets: each composed bootloader's content-line count is within
   ANCHOR_BUDGET; budget never justifies dropping a concept (that is caught by
   check 1, which runs regardless of budget).

Status vocabulary follows ADR 0003.1: PASS / NEEDS_REVIEW / FAIL. A missing
concept in its single home is FAIL (certified knowledge lost). A byte-duplicated
paragraph is FAIL. A budget overflow with all concepts present is NEEDS_REVIEW
(thinner is better, but no knowledge was lost).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

VERSION = "0.3.186"

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_REL = (
    "docs/evidence/reports/system-analysis/"
    "bootloader-concept-inventory-2026-06-04.md"
)

# Content-line budget for an always-loaded anchor. Measured from the thinned
# anchors (Claude 54, Codex 62 with XML tags, Cursor anchor 46); 70 leaves room
# for the XML-tagged Codex form without permitting a return to bloat.
ANCHOR_BUDGET = 70

# Bootloaders whose content-line budget is enforced (the always-loaded layer).
# The Cursor lazy rule is intentionally excluded: alwaysApply:false means it is
# not always-loaded, so it carries weight without an anchor budget.
BUDGETED_BOOTLOADERS = {
    "src/adapters/claude/CLAUDE.md",
    "src/adapters/codex/AGENTS.md",
    "src/adapters/cursor/CURSOR.md",
    "src/adapters/cursor/rules/tes-guidelines.mdc",
}


def content_lines(text: str) -> int:
    """Count non-blank lines (the honest size of an anchor)."""
    return sum(1 for line in text.splitlines() if line.strip())


def paragraphs(text: str) -> list[str]:
    """Split into blank-line-delimited blocks, normalized for byte comparison."""
    blocks: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.strip():
            current.append(line.rstrip())
        elif current:
            blocks.append("\n".join(current))
            current = []
    if current:
        blocks.append("\n".join(current))
    return blocks


def prose_paragraphs(text: str) -> set[str]:
    """Multi-line prose blocks eligible for the anchor-not-copy byte check.

    Excludes code fences and short anchors: a shared `E = A * S * C * V` fence or
    a one-line pointer is not the disease. The disease is a multi-line paragraph
    of explanation duplicated between an anchor and its skill home. Blocks that
    contain a code fence (```), or whose longest line is short, are not prose.
    """
    out: set[str] = set()
    for block in paragraphs(text):
        lines = block.splitlines()
        if len(lines) < 2:
            continue
        if any("```" in ln for ln in lines):
            continue
        if max((len(ln) for ln in lines), default=0) < 30:
            continue
        out.add(block)
    return out


def load_inventory(inventory_path: Path) -> dict[str, Any]:
    """Extract and parse the ```yaml fenced block from the inventory markdown."""
    md = inventory_path.read_text(encoding="utf-8")
    match = re.search(r"```yaml\n(.*?)\n```", md, re.DOTALL)
    if not match:
        raise ValueError(f"no ```yaml block found in {inventory_path}")
    return yaml.safe_load(match.group(1))


def host_disposition(concept: dict[str, Any], host: str) -> str | None:
    """Resolve a concept's disposition for a host (per-host overrides win)."""
    by_host = concept.get("disposition_by_host")
    if by_host:
        return by_host.get(host)
    if host in concept.get("hosts", []):
        return concept.get("disposition")
    return None


def host_surfaces(inventory: dict[str, Any], host: str) -> dict[str, Path]:
    """Map a host to its bootloader and skill/rule files, repo-root-relative."""
    spec = inventory["hosts"][host]
    surfaces: dict[str, Path] = {}
    if "bootloader" in spec:
        surfaces["bootloader"] = REPO_ROOT / spec["bootloader"]
    if "anchor_rule" in spec:
        surfaces["anchor_rule"] = REPO_ROOT / spec["anchor_rule"]
    if "lazy_rule" in spec:
        surfaces["lazy_rule"] = REPO_ROOT / spec["lazy_rule"]
    for skill in spec.get("skills", []):
        surfaces.setdefault("skills", [])  # type: ignore[arg-type]
    return surfaces


def markers_present(text: str, markers: list[str]) -> list[str]:
    """Return the markers that are missing from text (empty list == all present)."""
    return [m for m in markers if m not in text]


def check_against_inventory(inventory: dict[str, Any], root: Path) -> dict[str, Any]:
    """Run the three parity checks against the inventory and current sources."""
    failures: list[str] = []
    reviews: list[str] = []
    concepts = inventory["concepts"]
    host_specs = inventory["hosts"]

    # --- Check 3 first (cheap), but never let it gate check 1. ---
    for host, spec in host_specs.items():
        for key in ("bootloader", "anchor_rule"):
            rel = spec.get(key)
            if not rel or rel not in BUDGETED_BOOTLOADERS:
                continue
            path = root / rel
            if not path.exists():
                failures.append(f"[{host}] budgeted bootloader missing: {rel}")
                continue
            n = content_lines(path.read_text(encoding="utf-8"))
            if n > ANCHOR_BUDGET:
                reviews.append(
                    f"[{host}] {rel} has {n} content lines (> budget {ANCHOR_BUDGET}); "
                    "all concepts may still be present — review for further thinning"
                )

    # --- Checks 1 and 2, per concept per host. ---
    for concept in concepts:
        cid = concept["id"]
        for host in concept.get("hosts", []):
            disp = host_disposition(concept, host)
            if disp is None:
                continue
            spec = host_specs[host]
            expansion_rel = concept.get("expansion_in", {}).get(host)
            expansion_path = (root / expansion_rel) if expansion_rel else None

            # Resolve the bootloader/anchor file(s) for this host.
            boot_rels = [r for r in (spec.get("bootloader"), spec.get("anchor_rule")) if r]
            boot_texts = {
                r: (root / r).read_text(encoding="utf-8")
                for r in boot_rels
                if (root / r).exists()
            }

            if disp == "keep-as-anchor":
                anchor_markers = concept.get("anchor_markers", [])
                # The anchor must be present in at least one of this host's
                # always-loaded bootloader files.
                if anchor_markers:
                    present_somewhere = any(
                        not markers_present(t, anchor_markers)
                        for t in boot_texts.values()
                    )
                    if not present_somewhere:
                        failures.append(
                            f"[{host}/{cid}] keep-as-anchor: anchor_markers "
                            f"{anchor_markers} not found in any bootloader "
                            f"({list(boot_texts)})"
                        )
                if concept.get("expansion_required") and expansion_path:
                    if not expansion_path.exists():
                        failures.append(
                            f"[{host}/{cid}] expansion file missing: {expansion_rel}"
                        )
                    else:
                        missing = markers_present(
                            expansion_path.read_text(encoding="utf-8"),
                            concept.get("skill_markers", []),
                        )
                        if missing:
                            failures.append(
                                f"[{host}/{cid}] expansion_required: skill_markers "
                                f"{missing} missing from {expansion_rel}"
                            )

            elif disp in ("already-in-skill", "move-to-skill"):
                # The detail must live in its single home (the skill/rule).
                if not expansion_path or not expansion_path.exists():
                    failures.append(
                        f"[{host}/{cid}] {disp}: home file missing: {expansion_rel}"
                    )
                else:
                    missing = markers_present(
                        expansion_path.read_text(encoding="utf-8"),
                        concept.get("skill_markers", []),
                    )
                    if missing:
                        failures.append(
                            f"[{host}/{cid}] {disp}: skill_markers {missing} missing "
                            f"from single home {expansion_rel} (certified knowledge lost)"
                        )

            # --- Check 2: byte-duplication between an anchor and its skill home.
            # Only meaningful when the expansion home is a lazy skill/rule, not
            # another always-loaded anchor of the same host: a shared one-line
            # confidentiality rule across two Cursor anchors is design, not the
            # disease. So skip when the expansion home is itself budgeted. ---
            expansion_is_anchor = expansion_rel in BUDGETED_BOOTLOADERS
            if (
                expansion_path
                and expansion_path.exists()
                and boot_texts
                and not expansion_is_anchor
            ):
                expansion_blocks = prose_paragraphs(
                    expansion_path.read_text(encoding="utf-8")
                )
                for boot_rel, boot_text in boot_texts.items():
                    if boot_rel == expansion_rel:
                        continue  # same file
                    for block in prose_paragraphs(boot_text):
                        if block in expansion_blocks:
                            failures.append(
                                f"[{host}/{cid}] byte-duplicated prose paragraph between "
                                f"{boot_rel} and {expansion_rel} (anchor-not-copy "
                                f"violation):\n    {block.splitlines()[0][:70]}..."
                            )
                            break

    status = "FAIL" if failures else ("NEEDS_REVIEW" if reviews else "PASS")
    return {
        "version": VERSION,
        "status": status,
        "concepts_checked": len(concepts),
        "anchor_budget": ANCHOR_BUDGET,
        "failures": failures,
        "reviews": reviews,
    }


def self_test() -> dict[str, Any]:
    """Fixtures: PASS (full coverage), FAIL (missing concept), FAIL (byte dup)."""
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        boot = root / "boot.md"
        skill = root / "skill.md"
        inv = {
            "hosts": {
                "h": {"bootloader": "boot.md", "skills": ["skill.md"]},
            },
            "concepts": [
                {
                    "id": "anchored",
                    "hosts": ["h"],
                    "disposition": "keep-as-anchor",
                    "expansion_required": True,
                    "anchor_markers": ["ANCHOR_TOKEN"],
                    "skill_markers": ["EXPANSION_TOKEN"],
                    "expansion_in": {"h": "skill.md"},
                },
                {
                    "id": "detail",
                    "hosts": ["h"],
                    "disposition": "already-in-skill",
                    "skill_markers": ["DETAIL_TOKEN"],
                    "expansion_in": {"h": "skill.md"},
                },
            ],
        }
        # BUDGETED_BOOTLOADERS does not include the fixture path, so budget is
        # skipped and only the semantic/byte checks run.

        # Fixture A: full coverage -> PASS.
        boot.write_text("intro\n\nANCHOR_TOKEN line here\n", encoding="utf-8")
        skill.write_text(
            "EXPANSION_TOKEN paragraph\n\nDETAIL_TOKEN paragraph\n", encoding="utf-8"
        )
        a = check_against_inventory(inv, root)
        if a["status"] != "PASS":
            failures.append(f"fixtureA expected PASS, got {a['status']}: {a['failures']}")

        # Fixture B: detail concept missing from its single home -> FAIL.
        skill.write_text("EXPANSION_TOKEN paragraph\n", encoding="utf-8")
        b = check_against_inventory(inv, root)
        if b["status"] != "FAIL":
            failures.append(f"fixtureB expected FAIL (missing concept), got {b['status']}")

        # Fixture C: byte-duplicated multi-line paragraph between boot and skill -> FAIL.
        dup = "ANCHOR_TOKEN duplicated line one\nduplicated line two of the block"
        boot.write_text(f"intro\n\n{dup}\n", encoding="utf-8")
        skill.write_text(
            f"EXPANSION_TOKEN paragraph\n\nDETAIL_TOKEN paragraph\n\n{dup}\n",
            encoding="utf-8",
        )
        c = check_against_inventory(inv, root)
        if c["status"] != "FAIL":
            failures.append(f"fixtureC expected FAIL (byte dup), got {c['status']}")
        elif not any("byte-duplicated" in f for f in c["failures"]):
            failures.append("fixtureC: byte-duplication not reported")

        # Fixture D: anchor marker missing from bootloader -> FAIL.
        boot.write_text("intro only, no anchor token\n", encoding="utf-8")
        skill.write_text(
            "EXPANSION_TOKEN paragraph\n\nDETAIL_TOKEN paragraph\n", encoding="utf-8"
        )
        d = check_against_inventory(inv, root)
        if d["status"] != "FAIL":
            failures.append(f"fixtureD expected FAIL (missing anchor), got {d['status']}")

    return {
        "version": VERSION,
        "self_test_mode": "fixtures",
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--inventory",
        default=str(REPO_ROOT / INVENTORY_REL),
        help="path to the concept inventory markdown",
    )
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2))
        print(f"[context-skill-parity] {result['status']}")
        return 0 if result["status"] == "PASS" else 1

    inventory = load_inventory(Path(args.inventory))
    result = check_against_inventory(inventory, REPO_ROOT)
    print(json.dumps(result, indent=2))
    print(f"[context-skill-parity] {result['status']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
