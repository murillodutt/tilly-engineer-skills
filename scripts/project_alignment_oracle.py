#!/usr/bin/env python3
"""Validate TES project alignment mesh quality for installed targets."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.98"
PACKAGE_MODE = (ROOT / "scripts").exists()
AGENTS = Path("docs/agents")
EVIDENCE = AGENTS / "evidence"
ALIGNMENT_FILES = {
    "project_context": AGENTS / "PROJECT-CONTEXT.md",
    "project_state": AGENTS / "PROJECT-STATE.md",
    "project_roadmap": AGENTS / "PROJECT-ROADMAP.md",
    "execution_line": AGENTS / "EXECUTION-LINE.md",
    "quality_gates": AGENTS / "QUALITY-GATES.md",
    "boundaries": AGENTS / "BOUNDARIES-AND-CONSTRAINTS.md",
    "knowledge_lifecycle": AGENTS / "KNOWLEDGE-LIFECYCLE.md",
    "glossary": AGENTS / "GLOSSARY.md",
}
FRONTMATTER_KEYS = ("tes_doc", "status", "updated", "confidence", "tags", "evidence")
ROADMAP_TERMS = ("Done", "Active", "Next", "Later", "Deferred", "Blocked", "Unknown")
ROADMAP_FRAME_TERMS = ("System X-Ray", "Convergence Line", "Current Claim", "Next Irreversible Step")
SYSTEM_XRAY_TERMS = (
    "Git state",
    "Delivered behavior",
    "Validation mesh",
    "Release boundary",
    "classDef system",
)
CONVERGENCE_LINE_TERMS = (
    "```mermaid",
    "flowchart TD",
    "classDef done",
    "classDef current",
    "classDef next",
    "classDef deferred",
    "classDef blocked",
    "classDef unknown",
)
GATE_TERMS = ("required", "focused", "needs_review", "unavailable", "unsafe")
BOUNDARY_TERMS = ("secrets", "external", "destructive", "governance")
LIFECYCLE_TERMS = ("validate", "refresh", "retire", "contradict")
EXECUTION_TERMS = ("Build-Test-Fail-Fix", "Reentry", "Stop Condition", "gate")
EVIDENCE_TERMS = (
    "alignment_evidence",
    "anchors_read",
    "existing_docs_classification",
    "obsidian_native_checks",
    "oracle_result",
)
GENERIC_FAILURE_TERMS = (
    "tbd",
    "todo",
    "lorem ipsum",
    "fill this in",
    "generic project",
    "run tests",
    "to be determined",
)
GENERIC_FAILURE_PATTERNS = {
    "tbd": re.compile(r"(?<![A-Za-z0-9_])tbd(?![A-Za-z0-9_])", re.IGNORECASE),
    "todo": re.compile(r"(?<![A-Za-z0-9_])todo(?![A-Za-z0-9_])", re.IGNORECASE),
    "lorem ipsum": re.compile(r"(?<![A-Za-z0-9_])lorem\s+ipsum(?![A-Za-z0-9_])", re.IGNORECASE),
    "fill this in": re.compile(r"(?<![A-Za-z0-9_])fill\s+this\s+in(?![A-Za-z0-9_])", re.IGNORECASE),
    "generic project": re.compile(r"(?<![A-Za-z0-9_])generic\s+project(?![A-Za-z0-9_])", re.IGNORECASE),
    "run tests": re.compile(r"(?<![A-Za-z0-9_])run\s+tests(?![A-Za-z0-9_/])", re.IGNORECASE),
    "to be determined": re.compile(r"(?<![A-Za-z0-9_])to\s+be\s+determined(?![A-Za-z0-9_])", re.IGNORECASE),
}
PATH_RE = re.compile(
    r"(?:^|[`\s])([A-Za-z0-9_./-]+\.(?:md|mdc|json|toml|ya?ml|py|js|ts|tsx|go|rs|tf|sh|ps1|lock|txt))"
)
PATH_LITERAL_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"[A-Za-z0-9_./-]+\.(?:md|mdc|json|toml|ya?ml|py|js|ts|tsx|go|rs|tf|sh|ps1|lock|txt)"
    r"(?![A-Za-z0-9_./-])"
)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
COMMAND_CELL_RE = re.compile(
    r"^(?:"
    r"\./|bun|cargo|deno|docker(?:\s+compose)?|eslint|git|go|make|markdownlint(?:-cli2)?|"
    r"node|npm|npx|pnpm|python3?|pytest|ruff|sh|bash|tsc|ts-node|tsx|uv|vitest|yarn"
    r")\b",
    re.IGNORECASE,
)
WIKILINK_RE = re.compile(r"\[\[[^\]]+\]\]")


def rel(path: Path, target: Path) -> str:
    try:
        return path.relative_to(target).as_posix()
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    data: dict[str, str] = {}
    for raw_line in text[4:end].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("- ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def path_refs(text: str) -> set[str]:
    refs = {match.group(1).strip("`") for match in PATH_RE.finditer(text)}
    refs.update(match.strip("`") for match in re.findall(r"`([^`]+/[A-Za-z0-9_.-]+)`", text))
    return {ref for ref in refs if not ref.startswith("http")}


def frontmatter_failures(label: str, text: str) -> list[str]:
    data = parse_frontmatter(text)
    failures: list[str] = []
    if not data:
        return [f"{label} missing Obsidian-compatible YAML frontmatter"]
    for key in FRONTMATTER_KEYS:
        if key not in data:
            failures.append(f"{label} frontmatter missing {key}")
    return failures


def command_like_cell(cell: str) -> bool:
    stripped = cell.strip().strip("`").strip()
    if not stripped:
        return False
    return bool(COMMAND_CELL_RE.match(stripped))


def mask_table_command_cells(line: str) -> str:
    stripped = line.strip()
    if not stripped.startswith("|") or "|" not in stripped[1:]:
        return line
    cells = stripped.strip("|").split("|")
    return " | ".join(" " if command_like_cell(cell) else cell for cell in cells)


def generic_search_text(text: str) -> str:
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            lines.append("")
            continue
        if in_fence:
            lines.append("")
            continue
        searchable = mask_table_command_cells(line)
        searchable = INLINE_CODE_RE.sub(" ", searchable)
        searchable = PATH_LITERAL_RE.sub(" ", searchable)
        lines.append(searchable)
    return "\n".join(lines)


def generic_failures(label: str, text: str) -> list[str]:
    searchable = generic_search_text(text)
    return [
        f"{label} contains generic placeholder term: {term}"
        for term in GENERIC_FAILURE_TERMS
        if GENERIC_FAILURE_PATTERNS[term].search(searchable)
    ]


def require_terms(label: str, text: str, terms: tuple[str, ...]) -> list[str]:
    folded = text.casefold()
    return [f"{label} missing term: {term}" for term in terms if term.casefold() not in folded]


def evidence_files(target: Path) -> list[Path]:
    root = target / EVIDENCE
    if not root.exists():
        return []
    return sorted(path for path in root.glob("*project-alignment*.md") if path.is_file())


def obsidian_pollution(target: Path) -> list[str]:
    root = target / ".obsidian"
    if not root.exists():
        return []
    failures: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relpath = rel(path, target)
        if "tes" in relpath.casefold() or "agents" in read_text(path).casefold():
            failures.append(f"TES alignment must not write Obsidian runtime state: {relpath}")
    return failures


def analyze(target: Path) -> dict[str, Any]:
    target = target.resolve()
    failures: list[str] = []
    warnings: list[str] = []
    docs: dict[str, dict[str, Any]] = {}
    combined = ""

    for label, relpath in ALIGNMENT_FILES.items():
        path = target / relpath
        text = read_text(path)
        exists = bool(text)
        docs[label] = {
            "path": relpath.as_posix(),
            "exists": exists,
            "path_refs": sorted(path_refs(text))[:20],
            "wikilinks": len(WIKILINK_RE.findall(text)),
        }
        if not exists:
            failures.append(f"missing alignment surface: {relpath.as_posix()}")
            continue
        combined += "\n" + text
        failures.extend(frontmatter_failures(relpath.as_posix(), text))
        failures.extend(generic_failures(relpath.as_posix(), text))
        if len(path_refs(text)) == 0 and label not in {"glossary"}:
            failures.append(f"{relpath.as_posix()} must cite at least one project path")

    roadmap = read_text(target / ALIGNMENT_FILES["project_roadmap"])
    failures.extend(require_terms("PROJECT-ROADMAP.md", roadmap, tuple(f"## {term}" for term in ROADMAP_TERMS)))
    failures.extend(require_terms("PROJECT-ROADMAP.md roadmap frame", roadmap, tuple(f"## {term}" for term in ROADMAP_FRAME_TERMS)))
    failures.extend(require_terms("PROJECT-ROADMAP.md System X-Ray", roadmap, SYSTEM_XRAY_TERMS))
    failures.extend(require_terms("PROJECT-ROADMAP.md Convergence Line", roadmap, CONVERGENCE_LINE_TERMS))

    execution = read_text(target / ALIGNMENT_FILES["execution_line"])
    failures.extend(require_terms("EXECUTION-LINE.md", execution, EXECUTION_TERMS))

    gates = read_text(target / ALIGNMENT_FILES["quality_gates"])
    failures.extend(require_terms("QUALITY-GATES.md", gates, GATE_TERMS))

    boundaries = read_text(target / ALIGNMENT_FILES["boundaries"])
    failures.extend(require_terms("BOUNDARIES-AND-CONSTRAINTS.md", boundaries, BOUNDARY_TERMS))

    lifecycle = read_text(target / ALIGNMENT_FILES["knowledge_lifecycle"])
    failures.extend(require_terms("KNOWLEDGE-LIFECYCLE.md", lifecycle, LIFECYCLE_TERMS))

    glossary = read_text(target / ALIGNMENT_FILES["glossary"])
    glossary_rows = [
        line
        for line in glossary.splitlines()
        if line.count("|") >= 2 and "---" not in line and "Term" not in line
    ]
    if len(glossary_rows) < 2:
        failures.append("GLOSSARY.md must define at least two project terms or aliases")

    decisions = target / AGENTS / "DECISIONS"
    linked_decision = "linked_existing" in combined and "decision" in combined.casefold()
    if not linked_decision and not any(decisions.glob("*.md")):
        failures.append("docs/agents/DECISIONS/ must contain a decision record or link an existing decision system")

    retained = evidence_files(target)
    if not retained:
        failures.append("missing retained project-alignment evidence packet")
    else:
        evidence_text = "\n".join(read_text(path) for path in retained)
        failures.extend(require_terms("project-alignment evidence", evidence_text, EVIDENCE_TERMS))
        if len(path_refs(evidence_text)) < 3:
            failures.append("project-alignment evidence must list at least three anchors read")

    wikilinks = WIKILINK_RE.findall(combined)
    if len(wikilinks) < 3:
        failures.append("alignment mesh must contain at least three wikilinks for Obsidian graph navigation")

    if "Unknown" in roadmap and "unknown" not in combined.casefold():
        warnings.append("roadmap has an Unknown lane but the mesh may not explain uncertainty deeply")

    failures.extend(obsidian_pollution(target))

    status = "PASS" if not failures else "FAIL"
    return {
        "version": VERSION,
        "status": status,
        "target": str(target),
        "docs": docs,
        "evidence_packets": [rel(path, target) for path in retained],
        "failures": failures,
        "warnings": warnings,
    }


def fm(tes_doc: str) -> str:
    return f"""---
tes_doc: {tes_doc}
status: active
owner: project
updated: 2026-05-09
confidence: medium
evidence:
  - path: README.md
  - path: package.json
tags:
  - tes
  - {tes_doc}
related:
  - "[[PROJECT-CONTEXT]]"
---

"""


def fixture_system_xray() -> str:
    return """```mermaid
flowchart TD
  A["Project system"] --> B["Git state"]
  A --> C["Delivered behavior"]
  A --> D["Validation mesh"]
  A --> E["Release boundary"]
  C --> C1["docs/agents/** mesh"]
  D --> D1["Alignment oracle"]
  E --> E1["Technical GO"]
  E --> E2["Release claim pending"]

  classDef system fill:#eef2f7,stroke:#475569,color:#0f172a;
  classDef behavior fill:#e6f0ff,stroke:#2b6cb0,color:#102a43;
  classDef gate fill:#d8f5df,stroke:#1b7f3a,color:#0b351a;
  classDef pending fill:#ffe4e6,stroke:#be123c,color:#4c0519;

  class A,B,C,D,E system;
  class C1 behavior;
  class D1,E1 gate;
  class E2 pending;
```
"""


def fixture_convergence_line() -> str:
    return """```mermaid
flowchart TD
  A["Done: scaffold exists"] --> B["Current: stabilize quality gates"]
  B --> C["Next: add CI evidence"]
  C --> D["Final: alignment gate passes"]
  C --> G["Deferred: release docs"]
  B --> E["Blocked: deployment target unknown"]
  B --> F["Unknown: runtime support matrix"]

  classDef done fill:#d8f5df,stroke:#1b7f3a,color:#0b351a;
  classDef current fill:#fff0bf,stroke:#b7791f,color:#4a2d00;
  classDef next fill:#e6f0ff,stroke:#2b6cb0,color:#102a43;
  classDef deferred fill:#fef9c3,stroke:#a16207,color:#422006;
  classDef blocked fill:#ffe4e6,stroke:#be123c,color:#4c0519;
  classDef unknown fill:#f5f5f4,stroke:#78716c,color:#1c1917;
  classDef final fill:#f3e8ff,stroke:#7e22ce,color:#2e1065;

  class A done;
  class B current;
  class C next;
  class G deferred;
  class D final;
  class E blocked;
  class F unknown;
```
"""


def write_good_fixture(target: Path) -> None:
    def write(relpath: Path, text: str) -> None:
        path = target / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    write(Path("README.md"), "# Example Product\n")
    write(Path("package.json"), '{"scripts":{"test":"node test.js","lint":"eslint ."}}\n')
    write(
        ALIGNMENT_FILES["project_context"],
        fm("project-context")
        + "# Project Context\n\nThis mesh reads `README.md`, `package.json`, and `src/app.ts`.\n\n"
        + "Related: [[PROJECT-STATE]], [[PROJECT-ROADMAP]], [[QUALITY-GATES]].\n",
    )
    write(
        ALIGNMENT_FILES["project_state"],
        fm("project-state")
        + "# Project State\n\nDone: package scaffold in `package.json`.\n\n"
        + "Active: align `src/app.ts`. Blocked: no CI file yet. Unknown: release process.\n"
        + "Related: [[PROJECT-CONTEXT]].\n",
    )
    write(
        ALIGNMENT_FILES["project_roadmap"],
        fm("project-roadmap")
        + "# Project Roadmap\n\n"
        + "## System X-Ray\n\n"
        + fixture_system_xray()
        + "\n"
        + "## Convergence Line\n\n"
        + fixture_convergence_line()
        + "\n"
        + "## Current Claim\n- Technical GO for `docs/agents/PROJECT-ROADMAP.md` after gates pass.\n\n"
        + "## Next Irreversible Step\n- Commit only after `npm test` passes.\n"
        + "## Done\n- Existing app scaffold in `src/app.ts`.\n"
        + "## Active\n- Stabilize quality gates from `package.json`.\n"
        + "## Next\n- Add CI evidence.\n"
        + "## Later\n- Release docs.\n"
        + "## Deferred\n- Native plugin until product exists.\n"
        + "## Blocked\n- Deployment target unknown.\n"
        + "## Unknown\n- Runtime support matrix.\n",
    )
    write(
        ALIGNMENT_FILES["execution_line"],
        fm("execution-line")
        + "# Execution Line\n\nCurrent lane reads `README.md` first. Use Build-Test-Fail-Fix.\n"
        + "Quality gate: `npm test`. Reentry packet: target, baseline, next gate.\n"
        + "## Stop Condition\nStop on secret, destructive, or remote mutation risk.\n",
    )
    write(
        ALIGNMENT_FILES["quality_gates"],
        fm("quality-gates")
        + "# Quality Gates\n\n| Gate | Class | Command |\n|------|-------|---------|\n"
        + "| Unit test | required | `npm test` |\n"
        + "| Lint | required | `npm run lint` |\n"
        + "| Contract verify | focused | `npm run contract:verify` |\n"
        + "| Coverage | needs_review | `npm run coverage` |\n"
        + "| Typecheck | unavailable | No TypeScript config in `package.json` |\n"
        + "| Deploy | unsafe | Requires external production credentials |\n",
    )
    write(
        ALIGNMENT_FILES["boundaries"],
        fm("boundaries")
        + "# Boundaries And Constraints\n\nProtect governance files such as `AGENTS.md`.\n"
        + "Do not touch secrets, external services, destructive commands, or remotes.\n",
    )
    write(
        ALIGNMENT_FILES["knowledge_lifecycle"],
        fm("knowledge-lifecycle")
        + "# Knowledge Lifecycle\n\nValidate claims against `README.md`. Refresh stale claims.\n"
        + "Retire superseded roadmap entries and preserve contradictions until resolved.\n",
    )
    write(
        ALIGNMENT_FILES["glossary"],
        fm("glossary")
        + "# Glossary\n\n| Term | Meaning |\n|------|---------|\n"
        + "| Product | The app described by `README.md`. |\n"
        + "| Gate | A command such as `npm test`. |\n",
    )
    write(
        AGENTS / "DECISIONS/001-alignment-mesh.md",
        fm("decision")
        + "# Decision: Alignment Mesh\n\nUse `docs/agents/**` as the project operating mesh.\n",
    )
    write(
        EVIDENCE / "20260509T000000Z-project-alignment.md",
        "# Project Alignment Evidence\n\n"
        + "```yaml\nalignment_evidence:\n"
        + "  target: fixture\n"
        + "  tes_version: 0.3.98\n"
        + "  anchors_read:\n"
        + "    - README.md\n"
        + "    - package.json\n"
        + "    - src/app.ts\n"
        + "  existing_docs_classification:\n"
        + "    PROJECT-ROADMAP.md: created\n"
        + "  created_or_updated:\n"
        + "    - docs/agents/PROJECT-ROADMAP.md\n"
        + "  contradictions: []\n"
        + "  quality_gates_discovered:\n"
        + "    - npm test\n"
        + "  roadmap_changes:\n"
        + "    - created System X-Ray graph\n"
        + "    - created Convergence Line graph\n"
        + "    - created initial lanes\n"
        + "  obsidian_native_checks:\n"
        + "    wikilinks: PASS\n"
        + "    dot_obsidian_writes: none\n"
        + "  oracle_result: PASS\n"
        + "  limits: sparse fixture\n```\n",
    )


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-align-good-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        result = analyze(target)
        if result["status"] != "PASS":
            failures.extend([f"good fixture must pass: {item}" for item in result["failures"]])

    with tempfile.TemporaryDirectory(prefix="tes-align-literal-placeholders-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        path = target / ALIGNMENT_FILES["project_context"]
        path.write_text(
            read_text(path)
            + "\n## Literal Inventory\n\n"
            + "| Territory | Sample anchors |\n"
            + "| --- | --- |\n"
            + "| docs-archive | `docs-archive/MCP-TESTS-TODO.md` |\n\n"
            + "| Script | Command |\n"
            + "| --- | --- |\n"
            + "| test:integration | vitest run tests/integration |\n"
            + "| test:validation | vitest run tests/validation |\n",
            encoding="utf-8",
        )
        result = analyze(target)
        if result["status"] != "PASS":
            failures.extend(
                [f"literal placeholder fixture must pass: {item}" for item in result["failures"]]
            )

    with tempfile.TemporaryDirectory(prefix="tes-align-bad-roadmap-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        path = target / ALIGNMENT_FILES["project_roadmap"]
        path.write_text(read_text(path).replace("## Unknown\n- Runtime support matrix.\n", ""), encoding="utf-8")
        result = analyze(target)
        if result["status"] != "FAIL" or not any("Unknown" in item for item in result["failures"]):
            failures.append("roadmap fixture must fail without Unknown lane")

    with tempfile.TemporaryDirectory(prefix="tes-align-bad-xray-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        path = target / ALIGNMENT_FILES["project_roadmap"]
        path.write_text(read_text(path).replace(fixture_system_xray() + "\n", ""), encoding="utf-8")
        result = analyze(target)
        if result["status"] != "FAIL" or not any("System X-Ray" in item for item in result["failures"]):
            failures.append("roadmap fixture must fail without System X-Ray")

    with tempfile.TemporaryDirectory(prefix="tes-align-bad-convergence-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        path = target / ALIGNMENT_FILES["project_roadmap"]
        path.write_text(read_text(path).replace(fixture_convergence_line() + "\n", ""), encoding="utf-8")
        result = analyze(target)
        if result["status"] != "FAIL" or not any("Convergence Line" in item for item in result["failures"]):
            failures.append("roadmap fixture must fail without Convergence Line")

    with tempfile.TemporaryDirectory(prefix="tes-align-generic-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        path = target / ALIGNMENT_FILES["project_state"]
        path.write_text(
            read_text(path) + "\nTODO: fill this in. TBD: generic project run tests.\n",
            encoding="utf-8",
        )
        result = analyze(target)
        if result["status"] != "FAIL" or not any("generic placeholder" in item for item in result["failures"]):
            failures.append("generic fixture must fail placeholder language")

    with tempfile.TemporaryDirectory(prefix="tes-align-obsidian-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        polluted = target / ".obsidian/tes-align.json"
        polluted.parent.mkdir(parents=True, exist_ok=True)
        polluted.write_text('{"agents":"pollution"}\n', encoding="utf-8")
        result = analyze(target)
        if result["status"] != "FAIL" or not any(".obsidian" in item for item in result["failures"]):
            failures.append("Obsidian runtime pollution fixture must fail")

    return {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "coverage": "source-package-contract" if PACKAGE_MODE else "installed-helper-contract",
        "self_test_mode": "package" if PACKAGE_MODE else "installed",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result = self_test() if args.self_test else analyze(args.target)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("[project-alignment] " + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
