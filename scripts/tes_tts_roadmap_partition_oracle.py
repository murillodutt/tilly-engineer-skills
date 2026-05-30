#!/usr/bin/env python3
"""Validate the compact TES TTS roadmap partition.

The active roadmap is an executive dashboard. Dense pointers belong in the
registry, and closed lineage belongs in history. This oracle keeps that contract
executable so the roadmap does not drift back into an ambiguous SPEC archive.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "docs/roadmap/TES-TTS-SKILL-ROADMAP.md"
REGISTRY = ROOT / "docs/roadmap/TES-TTS-SKILL-ROADMAP-REGISTRY.md"
HISTORY = ROOT / "docs/roadmap/TES-TTS-SKILL-ROADMAP-HISTORY.md"

LIMITS = {
    DASHBOARD: 80,
    REGISTRY: 160,
    HISTORY: 140,
}

DASHBOARD_REQUIRED_SECTIONS = (
    "## State",
    "## Decisions",
    "## Evidence",
    "## Next Cut",
    "## Maintenance Rules",
    "## Closure Rule",
)

REGISTRY_REQUIRED_SECTIONS = (
    "## Runtime And Skill Surfaces",
    "## Runtime Scripts And Oracles",
    "## Benchmark Fixtures",
    "## Governing Documents",
    "## Historical Ranges",
    "## Indexing Rule",
)

HISTORY_REQUIRED_SECTIONS = (
    "## Evolution Ledger",
    "## Sequence Outcomes",
    "## Current Historical Lessons",
    "## Release Boundary History",
)

HISTORICAL_ARTIFACT_PATTERN = re.compile(
    r"\b(?:GOAL-PROMPT|GOAL-SUPER-SPEC|TES-TTS-(?:SPEC|CAP|LEX|RTE|OWNER|TTS)-\d{3})"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def line_count(text: str) -> int:
    return len(text.splitlines())


def validate_exists(path: Path, failures: list[str]) -> None:
    if not path.exists():
        failures.append(f"missing roadmap partition: {path.relative_to(ROOT)}")


def validate_limit(path: Path, text: str, failures: list[str]) -> None:
    limit = LIMITS[path]
    count = line_count(text)
    if count > limit:
        failures.append(f"{path.relative_to(ROOT)} has {count} lines; limit is {limit}")


def validate_sections(path: Path, text: str, sections: tuple[str, ...], failures: list[str]) -> None:
    for section in sections:
        if section not in text:
            failures.append(f"{path.relative_to(ROOT)} missing section {section}")


def validate_dashboard(text: str, failures: list[str]) -> None:
    rel = DASHBOARD.relative_to(ROOT)
    if "TES-TTS-SKILL-ROADMAP-REGISTRY.md" not in text:
        failures.append(f"{rel} must point dense references to the registry")
    if "TES-TTS-SKILL-ROADMAP-HISTORY.md" not in text:
        failures.append(f"{rel} must point closed lineage to history")
    if "Partition contract:" not in text:
        failures.append(f"{rel} must state the partition contract")
    if "Hard limit: 80 lines" not in text:
        failures.append(f"{rel} must state its hard line limit")
    if "Review zone starts at 60 lines" not in text:
        failures.append(f"{rel} must state the roadmap warning threshold")
    if "If evidence needs more than four bullets" not in text:
        failures.append(f"{rel} must state the evidence compaction trigger")

    historical_matches = HISTORICAL_ARTIFACT_PATTERN.findall(text)
    if historical_matches:
        failures.append(
            f"{rel} must not list historical SPEC/prompt artifacts; move {sorted(set(historical_matches))} to registry/history"
        )

    table_lines = [line for line in text.splitlines() if line.startswith("|")]
    if table_lines:
        failures.append(f"{rel} must stay dashboard-shaped and avoid dense tables")


def validate_registry(text: str, failures: list[str]) -> None:
    rel = REGISTRY.relative_to(ROOT)
    if "avoid listing\nevery prompt" not in text:
        failures.append(f"{rel} must preserve the no-every-prompt listing rule")
    if "TES-TTS-SKILL-ROADMAP-HISTORY.md" not in text:
        failures.append(f"{rel} must link the history partition")


def validate_history(text: str, failures: list[str]) -> None:
    rel = HISTORY.relative_to(ROOT)
    if "stay objective and maintainable" not in text:
        failures.append(f"{rel} must state why history is split from the dashboard")
    if "TTS-010 through TTS-031" not in text:
        failures.append(f"{rel} must preserve the compressed owner-loop lesson")


def main() -> int:
    failures: list[str] = []
    for path in LIMITS:
        validate_exists(path, failures)
    if failures:
        emit_and_exit(failures)
        return 1

    dashboard = read(DASHBOARD)
    registry = read(REGISTRY)
    history = read(HISTORY)

    for path, text in ((DASHBOARD, dashboard), (REGISTRY, registry), (HISTORY, history)):
        validate_limit(path, text, failures)

    validate_sections(DASHBOARD, dashboard, DASHBOARD_REQUIRED_SECTIONS, failures)
    validate_sections(REGISTRY, registry, REGISTRY_REQUIRED_SECTIONS, failures)
    validate_sections(HISTORY, history, HISTORY_REQUIRED_SECTIONS, failures)
    validate_dashboard(dashboard, failures)
    validate_registry(registry, failures)
    validate_history(history, failures)

    emit_and_exit(failures)
    return 1 if failures else 0


def emit_and_exit(failures: list[str]) -> None:
    payload = {
        "status": "FAIL" if failures else "PASS",
        "dashboard": str(DASHBOARD.relative_to(ROOT)),
        "registry": str(REGISTRY.relative_to(ROOT)),
        "history": str(HISTORY.relative_to(ROOT)),
        "limits": {str(path.relative_to(ROOT)): limit for path, limit in LIMITS.items()},
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("[tes-tts-roadmap-partition] " + payload["status"])


if __name__ == "__main__":
    sys.exit(main())
