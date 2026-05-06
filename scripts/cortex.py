#!/usr/bin/env python3
"""Operate the Tilly Cortex filesystem memory layer."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile


CORTEX_ROOT = Path("docs/agents/cortex")
RECALL_DB = Path(".tilly/cortex/recall.sqlite")
REQUIRED_FILES = (
    "CONTRACT.md",
    "MAP.md",
    "TRAIL.md",
    "LINKS.md",
    "sources/README.md",
)
REQUIRED_DIRS = (
    "sources",
    "sources/assets",
    "cells",
)
LEGACY_PATHS = {
    "SCHEMA.md": "CONTRACT.md",
    "index.md": "MAP.md",
    "log.md": "TRAIL.md",
    "graph.md": "LINKS.md",
    "raw": "sources",
    "pages": "cells",
}
TRAIL_HEADING = re.compile(
    r"^## \[\d{4}-\d{2}-\d{2}\] "
    r"(init|install|absorb|recall|audit|repair|rebuild|learn|apply) \| .+",
    re.MULTILINE,
)
WIKILINK = re.compile(r"\[\[([^]|#]+)(?:[|#][^]]*)?\]\]")
H1_HEADING = re.compile(r"^# .+", re.MULTILINE)
CLAIM_SECTION = re.compile(r"^## Claims?$", re.MULTILINE)
EVIDENCE_SECTION = re.compile(r"^## Evidence$", re.MULTILINE)
EVIDENCE_REF = re.compile(
    r"(`?((?:\.\.?/)?(?:docs/agents/cortex/)?sources/[^`\s)]+|docs/agents/evidence/[^`\s)]+)`?|^[-*] Assumption:|^Assumption:)",
    re.MULTILINE,
)


def cortex_path(target: Path) -> Path:
    return target / CORTEX_ROOT


def recall_db_path(target: Path) -> Path:
    return target / RECALL_DB


def rel(path: Path, target: Path) -> str:
    try:
        return str(path.relative_to(target))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def starter_files(today: str) -> dict[str, str]:
    return {
        "CONTRACT.md": f"""# Tilly Cortex Contract

Cortex is the Tilly filesystem memory layer for this project.

Operating contract:

```text
Memory lives in versioned Cortex artifacts. SQLite is only derived recall.
```

## Core Layers

| Layer | Path | Contract |
|-------|------|----------|
| Sources | `sources/**` | Immutable user-curated evidence |
| Cells | `cells/**` | Compiled and evolving knowledge |
| Map | `MAP.md` | Navigable catalog |
| Trail | `TRAIL.md` | Append-only evolution timeline |
| Links | `LINKS.md` | Durable relationship map |
| Recall index | `.tilly/cortex/recall.sqlite` | Derived cache, rebuilt from files |

SQLite is never memory and never source of truth. It may be deleted and rebuilt
from `sources/**`, `cells/**`, `MAP.md`, `TRAIL.md`, `LINKS.md`, and this
contract.

## Cell Convention

Each cell must include one H1, a `## Claim` section, a `## Evidence` section,
explicit evidence refs, links to related Cortex cells when known, and
unresolved contradictions when present.

Use Obsidian wikilinks when useful, but keep source citations as explicit paths.

## Operations

| Operation | Contract |
|-----------|----------|
| `absorb` | Compile source evidence into cells, MAP, LINKS, and TRAIL |
| `recall` | Search Cortex artifacts through FTS5 or `rg` fallback |
| `audit` | Detect drift, orphans, broken links, and missing catalog entries |
| `learn` | Propose durable promotion; do not write automatically |
| `apply` | Write only with authorization and audit evidence |

## Privacy Lock

Do not absorb secrets, credentials, private keys, `.env` contents, or regulated
personal data unless a local privacy contract explicitly allows it.

## Obsidian Boundary

Obsidian may be used as a viewer/editor, but Cortex does not require it. Agents
must not edit `.obsidian/**` during Cortex operations unless explicitly asked.

## PR Cut Contract

```yaml
cortex_cut:
  consumer:
  camada: contrato|estrutura|cli|obsidian|adapter|mcp
  escreve_em:
  nao_toca:
  oracle:
  rollback:
```
""",
        "MAP.md": """# Cortex Map

Agents should read this map before answering Cortex-backed historical questions.

## Sources

| Source | Summary | Status |
|--------|---------|--------|

## Cells

| Cell | Summary | Links |
|------|---------|-------|

## Syntheses

| Synthesis | Claim | Evidence |
|-----------|-------|----------|
""",
        "TRAIL.md": f"""# Cortex Trail

## [{today}] init | Cortex structure

Created the initial Cortex structure. Sources stay under `sources/**`;
compiled knowledge belongs under `cells/**`; this trail remains append-only.
The recall index at `.tilly/cortex/recall.sqlite` is derived and rebuildable.
""",
        "LINKS.md": """# Cortex Links

## Adjacency List

Add durable relationships as the Cortex grows.

## Open Edges

- Future absorb operations should add links to concrete cells under `cells/**`.
""",
        "sources/README.md": """# Cortex Sources

This folder is for user-curated source material.

Agents may read these files during absorb, recall, and audit operations. After
a source is added, agents must not rewrite it. Derived summaries and syntheses
belong in `../cells/**`.

Local images or attachments may be placed under `assets/**` when the user
intentionally adds them.
""",
    }


def migrate_legacy(root: Path, target: Path) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for old_rel, new_rel in LEGACY_PATHS.items():
        old_path = root / old_rel
        new_path = root / new_rel
        if not old_path.exists():
            continue
        if new_path.exists():
            actions.append(
                {
                    "action": "legacy-left-in-place",
                    "path": rel(old_path, target),
                    "reason": f"{rel(new_path, target)} already exists",
                }
            )
            continue
        old_path.rename(new_path)
        actions.append(
            {
                "action": "migrate-legacy",
                "from": rel(old_path, target),
                "to": rel(new_path, target),
            }
        )
    return actions


def normalize_v1_text(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    text = read_text(path)
    updated = text
    replacements = (
        ("Tilly Cortex Schema", "Tilly Cortex Contract"),
        ("# Cortex Index", "# Cortex Map"),
        ("# Cortex Log", "# Cortex Trail"),
        ("# Cortex Graph", "# Cortex Links"),
        ("# Raw Sources", "# Cortex Sources"),
        ("LLM-maintained memory layer", "compiled Cortex memory layer"),
        ("LLM-maintained compiled cortex material", "compiled Cortex material"),
        ("read this index", "read this map"),
        ("Cortex-backed questions", "Cortex-backed historical questions"),
        ("Raw evidence stays immutable. The compiled cortex compounds. The log is append-only.",
         "Memory lives in versioned Cortex artifacts. SQLite is only derived recall."),
        ("raw/assets", "sources/assets"),
        ("raw/**", "sources/**"),
        ("pages/**", "cells/**"),
        ("pages/", "cells/"),
        ("index.md", "MAP.md"),
        ("graph.md", "LINKS.md"),
        ("log.md", "TRAIL.md"),
        ("SCHEMA.md", "CONTRACT.md"),
        ("compiled pages", "compiled cells"),
        ("Compiled pages", "Compiled cells"),
        ("Raw sources", "Sources"),
        ("Raw Sources", "Cortex Sources"),
        ("ingest", "absorb"),
        ("query", "recall"),
        ("lint", "audit"),
    )
    for old, new in replacements:
        updated = updated.replace(old, new)

    if path.name == "CONTRACT.md" and "SQLite is never memory" not in updated:
        updated += """

## V1 Memory Boundary

Memory lives in versioned Cortex artifacts: `sources/**`, `cells/**`,
`MAP.md`, `TRAIL.md`, `LINKS.md`, and `CONTRACT.md`.

SQLite is never memory and never source of truth. The recall index at
`.tilly/cortex/recall.sqlite` is derived and rebuildable from the versioned
artifacts. `rg` is the required fallback when FTS5 recall is unavailable.
"""

    if path.name == "README.md" and path.parent.name == "sources" and "must not rewrite" not in updated:
        updated = updated.replace("should not rewrite", "must not rewrite")

    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def normalize_v1_files(root: Path, target: Path) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for rel_file in REQUIRED_FILES:
        path = root / rel_file
        if normalize_v1_text(path):
            actions.append({"action": "normalize-v1-file", "path": rel(path, target)})
    return actions


def init(target: Path) -> dict[str, object]:
    target = target.resolve()
    root = cortex_path(target)
    root.mkdir(parents=True, exist_ok=True)
    actions = migrate_legacy(root, target)

    for rel_dir in REQUIRED_DIRS:
        path = root / rel_dir
        if path.exists():
            actions.append({"action": "skip-existing-dir", "path": rel(path, target)})
        else:
            path.mkdir(parents=True, exist_ok=True)
            actions.append({"action": "create-dir", "path": rel(path, target)})

    for rel_file, text in starter_files(date.today().isoformat()).items():
        path = root / rel_file
        if path.exists():
            actions.append({"action": "skip-existing-file", "path": rel(path, target)})
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        actions.append({"action": "create-file", "path": rel(path, target)})

    actions.extend(normalize_v1_files(root, target))

    return {
        "target": str(target),
        "cortex_root": rel(root, target),
        "recall_index": rel(recall_db_path(target), target),
        "obsidian_config_present": (target / ".obsidian").exists(),
        "actions": actions,
        "verify": verify(target),
    }


def legacy_paths_present(root: Path, target: Path) -> list[str]:
    return [rel(root / old, target) for old in LEGACY_PATHS if (root / old).exists()]


def verify(target: Path) -> dict[str, object]:
    target = target.resolve()
    root = cortex_path(target)
    failures: list[str] = []

    if not root.exists():
        failures.append(f"missing Cortex root: {rel(root, target)}")

    for rel_dir in REQUIRED_DIRS:
        path = root / rel_dir
        if not path.is_dir():
            failures.append(f"missing Cortex directory: {rel(path, target)}")

    for rel_file in REQUIRED_FILES:
        path = root / rel_file
        if not path.is_file():
            failures.append(f"missing Cortex file: {rel(path, target)}")

    for legacy_path in legacy_paths_present(root, target):
        failures.append(f"legacy Cortex path still present: {legacy_path}")

    contract = root / "CONTRACT.md"
    if contract.exists():
        text = read_text(contract)
        for term in (
            "Memory lives in versioned Cortex artifacts",
            "SQLite is never memory",
            "Privacy Lock",
            "Obsidian Boundary",
        ):
            if term not in text:
                failures.append(f"CONTRACT.md missing term: {term}")

    trail = root / "TRAIL.md"
    if trail.exists() and not TRAIL_HEADING.search(read_text(trail)):
        failures.append("TRAIL.md missing parseable Cortex heading")

    sources_readme = root / "sources" / "README.md"
    if sources_readme.exists() and "must not rewrite" not in read_text(sources_readme):
        failures.append("sources/README.md missing source immutability warning")

    return {
        "target": str(target),
        "cortex_root": rel(root, target),
        "recall_index": rel(recall_db_path(target), target),
        "obsidian_config_present": (target / ".obsidian").exists(),
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def cell_stem(path: Path) -> str:
    return path.stem


def cell_ref(path: Path, cells_root: Path) -> str:
    return str(path.relative_to(cells_root).with_suffix(""))


def slugify(value: str, fallback: str = "new-cell") -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or fallback


def title_from_slug(value: str) -> str:
    return Path(value).stem.replace("-", " ").replace("_", " ").title()


def cells_root(target: Path) -> Path:
    return cortex_path(target) / "cells"


def normalize_cell_rel(raw_cell: str) -> Path:
    cell_rel = Path(raw_cell.strip())
    if not raw_cell.strip():
        raise ValueError("cell is required")
    if cell_rel.is_absolute() or ".." in cell_rel.parts:
        raise ValueError("cell must stay under cells/**")
    if cell_rel.suffix != ".md":
        cell_rel = cell_rel.with_suffix(".md")
    return cell_rel


def resolve_cell_path(target: Path, raw_cell: str) -> Path:
    root = cells_root(target).resolve()
    path = (root / normalize_cell_rel(raw_cell)).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError("cell must stay under cells/**") from exc
    return path


def cell_quality_failures(cell: Path, target: Path) -> list[str]:
    text = read_text(cell)
    failures: list[str] = []
    h1_count = len(H1_HEADING.findall(text))

    if h1_count != 1:
        failures.append(f"cell must contain exactly one H1: {rel(cell, target)}")
    if not CLAIM_SECTION.search(text):
        failures.append(f"cell missing ## Claim section: {rel(cell, target)}")
    if not EVIDENCE_SECTION.search(text):
        failures.append(f"cell missing ## Evidence section: {rel(cell, target)}")
    if not EVIDENCE_REF.search(text):
        failures.append(f"cell missing explicit evidence ref: {rel(cell, target)}")

    return failures


def markdown_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for rel_path in ("CONTRACT.md", "MAP.md", "TRAIL.md", "LINKS.md"):
        path = root / rel_path
        if path.exists():
            candidates.append(path)
    for folder in ("sources", "cells"):
        path = root / folder
        if path.exists():
            candidates.extend(sorted(path.rglob("*.md")))
    return candidates


def audit(target: Path) -> dict[str, object]:
    target = target.resolve()
    root = cortex_path(target)
    verify_result = verify(target)
    failures = list(verify_result["failures"])
    warnings: list[str] = []

    cells_root = root / "cells"
    cells = sorted(cells_root.rglob("*.md")) if cells_root.exists() else []
    cell_refs: dict[str, Path] = {}
    for cell in cells:
        cell_refs[cell_stem(cell)] = cell
        cell_refs[cell_ref(cell, cells_root)] = cell

    map_text = read_text(root / "MAP.md") if (root / "MAP.md").exists() else ""
    links_text = read_text(root / "LINKS.md") if (root / "LINKS.md").exists() else ""

    for cell in cells:
        failures.extend(cell_quality_failures(cell, target))
        name = cell_stem(cell)
        path_ref = cell_ref(cell, cells_root)
        if (
            f"[[{name}]]" not in map_text
            and f"[[{path_ref}]]" not in map_text
            and f"]({rel(cell, root)})" not in map_text
        ):
            warnings.append(f"cell not listed in MAP.md: {rel(cell, target)}")

    referenced: set[str] = set()
    for path in [root / "MAP.md", root / "LINKS.md", *cells]:
        if not path.exists():
            continue
        for match in WIKILINK.findall(read_text(path)):
            referenced.add(match.strip())

    for link in sorted(referenced):
        if link not in cell_refs:
            failures.append(f"wikilink has no cell in cells/: [[{link}]]")

    inbound = {cell: 0 for cell in cells}
    for link in referenced:
        if link in cell_refs:
            inbound[cell_refs[link]] += 1

    for cell, count in sorted(inbound.items(), key=lambda item: rel(item[0], target)):
        name = cell_stem(cell)
        path_ref = cell_ref(cell, cells_root)
        if count == 0 and f"[[{name}]]" not in links_text and f"[[{path_ref}]]" not in links_text:
            warnings.append(f"possible orphan cell: [[{path_ref}]]")

    return {
        "target": str(target),
        "cortex_root": rel(root, target),
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
        "warnings": warnings,
        "cell_count": len(cells),
        "wikilink_count": len(referenced),
    }


def ensure_fts5(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE VIRTUAL TABLE fts_probe USING fts5(content)")
    conn.execute("DROP TABLE fts_probe")


def rebuild(target: Path) -> dict[str, object]:
    target = target.resolve()
    root = cortex_path(target)
    verify_result = verify(target)
    if verify_result["status"] != "PASS":
        return {
            "target": str(target),
            "status": "FAIL",
            "failures": verify_result["failures"],
        }

    db_path = recall_db_path(target)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    files = markdown_files(root)

    try:
        with sqlite3.connect(db_path) as conn:
            ensure_fts5(conn)
            conn.execute("DROP TABLE IF EXISTS cortex_recall")
            conn.execute(
                "CREATE VIRTUAL TABLE cortex_recall "
                "USING fts5(path UNINDEXED, layer UNINDEXED, title, body)"
            )
            for path in files:
                text = read_text(path)
                title = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), path.stem)
                layer = path.relative_to(root).parts[0] if len(path.relative_to(root).parts) > 1 else "root"
                conn.execute(
                    "INSERT INTO cortex_recall(path, layer, title, body) VALUES (?, ?, ?, ?)",
                    (rel(path, target), layer, title, text),
                )
            conn.commit()
    except sqlite3.Error as exc:
        return {
            "target": str(target),
            "recall_index": rel(db_path, target),
            "status": "FAIL",
            "failures": [f"SQLite FTS5 rebuild failed: {exc}"],
            "fallback": "rg",
        }

    return {
        "target": str(target),
        "recall_index": rel(db_path, target),
        "status": "PASS",
        "indexed_files": len(files),
    }


def sqlite_recall(target: Path, query: str, limit: int) -> dict[str, object]:
    db_path = recall_db_path(target)
    if not db_path.exists():
        raise sqlite3.Error(f"missing recall index: {rel(db_path, target)}")
    with sqlite3.connect(db_path) as conn:
        if query == "*":
            rows = conn.execute(
                "SELECT path, layer, title, substr(body, 1, 240) FROM cortex_recall LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT path, layer, title, snippet(cortex_recall, 3, '[', ']', ' ... ', 16) "
                "FROM cortex_recall WHERE cortex_recall MATCH ? LIMIT ?",
                (query, limit),
            ).fetchall()
    return {
        "backend": "sqlite-fts5",
        "matches": [
            {"path": path, "layer": layer, "title": title, "excerpt": excerpt}
            for path, layer, title, excerpt in rows
        ],
    }


def rg_recall(target: Path, query: str, limit: int) -> dict[str, object]:
    rg = shutil.which("rg")
    if rg is None:
        return {
            "backend": "rg",
            "matches": [],
            "failures": ["rg fallback unavailable on PATH"],
        }

    root = cortex_path(target)
    paths = [root / name for name in ("CONTRACT.md", "MAP.md", "TRAIL.md", "LINKS.md", "sources", "cells")]
    existing = [rel(path, target) for path in paths if path.exists()]
    result = subprocess.run(
        [rg, "-n", "--fixed-strings", "--max-count", str(limit), query, *existing],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    matches = []
    for line in result.stdout.splitlines()[:limit]:
        path, sep, rest = line.partition(":")
        if not sep:
            continue
        line_no, _, excerpt = rest.partition(":")
        matches.append({"path": rel(Path(path), target), "line": line_no, "excerpt": excerpt})
    return {"backend": "rg", "matches": matches}


def recall(target: Path, query: str, limit: int, force_rg: bool = False) -> dict[str, object]:
    target = target.resolve()
    verify_result = verify(target)
    if verify_result["status"] != "PASS":
        return {
            "target": str(target),
            "query": query,
            "status": "FAIL",
            "failures": verify_result["failures"],
        }

    if not force_rg:
        try:
            result = sqlite_recall(target, query, limit)
            return {"target": str(target), "query": query, "status": "PASS", **result}
        except sqlite3.Error as exc:
            fallback = rg_recall(target, query, limit)
            return {
                "target": str(target),
                "query": query,
                "status": "PASS" if not fallback.get("failures") else "FAIL",
                "sqlite_error": str(exc),
                **fallback,
            }

    fallback = rg_recall(target, query, limit)
    return {
        "target": str(target),
        "query": query,
        "status": "PASS" if not fallback.get("failures") else "FAIL",
        "forced_fallback": True,
        **fallback,
    }


def absorb_plan(target: Path, source: Path) -> dict[str, object]:
    target = target.resolve()
    source = source if source.is_absolute() else target / source
    source = source.resolve()
    verify_result = verify(target)
    failures = list(verify_result["failures"])

    root = cortex_path(target)
    sources_root = (root / "sources").resolve()
    try:
        source.relative_to(sources_root)
    except ValueError:
        failures.append(f"source is outside Cortex sources/: {source}")

    if not source.is_file():
        failures.append(f"source file missing: {source}")

    title = source.stem.replace("-", " ").replace("_", " ").title()
    cell_name = re.sub(r"[^a-z0-9]+", "-", source.stem.lower()).strip("-") or "new-cell"

    return {
        "target": str(target),
        "source": rel(source, target),
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
        "writes": [],
        "plan": [] if failures else [
            f"Read source `{rel(source, target)}` without modifying it.",
            f"Create or update `docs/agents/cortex/cells/{cell_name}.md` with H1 `{title}`, `## Claim`, and `## Evidence`.",
            "Update `docs/agents/cortex/MAP.md` with a one-line summary and source status.",
            "Update `docs/agents/cortex/LINKS.md` with durable relationships.",
            "Append one `absorb` entry to `docs/agents/cortex/TRAIL.md`.",
            "Run `python3 scripts/cortex.py audit --target <target>` and rebuild recall.",
        ],
    }


def read_cell(target: Path, cell: str) -> dict[str, object]:
    target = target.resolve()
    verify_result = verify(target)
    failures = list(verify_result["failures"])

    try:
        path = resolve_cell_path(target, cell)
    except ValueError as exc:
        failures.append(str(exc))
        path = None

    if path is not None and not path.is_file():
        failures.append(f"cell missing: {rel(path, target)}")

    return {
        "target": str(target),
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
        "path": rel(path, target) if path is not None else None,
        "text": "" if failures or path is None else read_text(path),
    }


def learn(target: Path, query: str | None, source: Path | None = None) -> dict[str, object]:
    target = target.resolve()
    verify_result = verify(target)
    failures = list(verify_result["failures"])
    source_rel = None

    if source is not None:
        planned_source = source if source.is_absolute() else target / source
        planned_source = planned_source.resolve()
        sources_root = (cortex_path(target) / "sources").resolve()
        try:
            planned_source.relative_to(sources_root)
        except ValueError:
            failures.append(f"source is outside Cortex sources/: {planned_source}")
        if not planned_source.is_file():
            failures.append(f"source file missing: {planned_source}")
        source_rel = rel(planned_source, target)

    prompt = query or (Path(source_rel).stem if source_rel else "")
    if not prompt:
        failures.append("learn requires a query or --source")

    cell_name = slugify(Path(source_rel).stem if source_rel else prompt)
    evidence = f"`{source_rel.removeprefix('docs/agents/cortex/')}`" if source_rel else "Assumption: user-approved conversation evidence"

    return {
        "target": str(target),
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
        "writes": [],
        "proposal": None if failures else {
            "cell": f"docs/agents/cortex/cells/{cell_name}.md",
            "claim_needed": "Write a durable claim, not a loose summary.",
            "evidence": evidence,
            "apply_command": (
                "python3 scripts/cortex.py apply "
                f"--target {target} "
                f"--cell {cell_name} "
                "--claim '<durable claim>' "
                f"--evidence {evidence!r} "
                "--yes"
            ),
        },
    }


def format_evidence_line(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith("- "):
        stripped = stripped[2:].strip()
    if stripped.startswith("Assumption:"):
        return f"- {stripped}"
    if stripped.startswith("`") and stripped.endswith("`"):
        return f"- {stripped}"
    return f"- `{stripped}`"


def format_wikilink(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith("[[") and stripped.endswith("]]"):
        return stripped
    return f"[[{stripped.removesuffix('.md')}]]"


def evidence_display(line: str) -> str:
    stripped = line.removeprefix("- ").strip()
    return stripped


def append_unique_line(path: Path, line: str) -> bool:
    text = read_text(path) if path.exists() else ""
    if line in text.splitlines():
        return False
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_text(text + line + "\n", encoding="utf-8")
    return True


def apply_cell(
    target: Path,
    cell: str,
    claim: str,
    evidence: list[str],
    summary: str | None,
    links: list[str],
    authorized: bool,
    update_existing: bool,
) -> dict[str, object]:
    target = target.resolve()
    verify_result = verify(target)
    failures = list(verify_result["failures"])
    writes: list[str] = []

    if not authorized:
        return {
            "target": str(target),
            "status": "NEEDS_AUTH",
            "failures": [],
            "writes": [],
            "message": "apply requires --yes because Cortex promotion must be explicitly authorized",
        }

    if not claim.strip():
        failures.append("apply requires --claim")
    if not evidence:
        failures.append("apply requires at least one --evidence")

    try:
        path = resolve_cell_path(target, cell)
    except ValueError as exc:
        failures.append(str(exc))
        path = None

    if path is not None and path.exists() and not update_existing:
        failures.append(f"cell already exists; pass --update to replace it: {rel(path, target)}")

    evidence_lines = [format_evidence_line(item) for item in evidence]
    evidence_text = "\n".join(evidence_lines)
    if not EVIDENCE_REF.search(evidence_text):
        failures.append("apply evidence must reference sources/**, docs/agents/evidence/**, or Assumption:")

    root = cortex_path(target)
    map_path = root / "MAP.md"
    links_path = root / "LINKS.md"
    trail_path = root / "TRAIL.md"

    if failures:
        return {
            "target": str(target),
            "status": "FAIL",
            "failures": failures,
            "writes": writes,
        }

    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    cell_reference = cell_ref(path, cells_root(target))
    title = title_from_slug(path.name)
    link_lines = [f"- {format_wikilink(link)}" for link in links]
    content = (
        f"# {title}\n\n"
        "## Claim\n\n"
        f"{claim.strip()}\n\n"
        "## Evidence\n\n"
        f"{evidence_text}\n"
    )
    if link_lines:
        content += "\n## Links\n\n" + "\n".join(link_lines) + "\n"

    path.write_text(content, encoding="utf-8")
    writes.append(rel(path, target))

    summary_text = (summary or claim.strip().splitlines()[0]).replace("|", "\\|")
    map_links = ", ".join(format_wikilink(link) for link in links)
    if append_unique_line(map_path, f"| [[{cell_reference}]] | {summary_text} | {map_links} |"):
        writes.append(rel(map_path, target))

    evidence_targets = ", ".join(evidence_display(item) for item in evidence_lines)
    if append_unique_line(links_path, f"- [[{cell_reference}]] -> {evidence_targets}"):
        writes.append(rel(links_path, target))
    for link in links:
        if append_unique_line(links_path, f"- [[{cell_reference}]] -> {format_wikilink(link)}"):
            if rel(links_path, target) not in writes:
                writes.append(rel(links_path, target))

    trail_heading = f"## [{date.today().isoformat()}] apply | {cell_reference}"
    if append_unique_line(trail_path, trail_heading):
        append_unique_line(trail_path, f"Applied authorized Cortex cell `cells/{cell_reference}.md` with explicit evidence.")
        writes.append(rel(trail_path, target))

    audit_result = audit(target)
    rebuild_result = rebuild(target) if audit_result["status"] == "PASS" else {
        "status": "SKIP",
        "reason": "audit failed",
    }

    return {
        "target": str(target),
        "status": "PASS" if audit_result["status"] == "PASS" and rebuild_result["status"] == "PASS" else "FAIL",
        "failures": [*audit_result.get("failures", []), *rebuild_result.get("failures", [])],
        "warnings": audit_result.get("warnings", []),
        "writes": writes,
        "audit": audit_result,
        "rebuild": rebuild_result,
    }


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="tilly-cortex-") as tempdir:
        target = Path(tempdir)
        init_result = init(target)
        source = cortex_path(target) / "sources" / "karpathy-pattern.md"
        source.write_text("# Karpathy Pattern\n\nCortex keeps durable memory in files.\n", encoding="utf-8")
        cell = cortex_path(target) / "cells" / "cortex-memory.md"
        cell.write_text(
            "# Cortex Memory\n\n"
            "## Claim\n\n"
            "Cortex memory lives in versioned files and links to [[nested/deep-memory]].\n\n"
            "## Evidence\n\n"
            "- `sources/karpathy-pattern.md` records the source claim.\n",
            encoding="utf-8",
        )
        nested_cell = cortex_path(target) / "cells" / "nested" / "deep-memory.md"
        nested_cell.parent.mkdir(parents=True, exist_ok=True)
        nested_cell.write_text(
            "# Deep Memory\n\n"
            "## Claim\n\n"
            "Nested cells are part of the audited Cortex surface and link back to [[cortex-memory]].\n\n"
            "## Evidence\n\n"
            "- `sources/karpathy-pattern.md` is the fixture evidence for nested audit.\n",
            encoding="utf-8",
        )
        map_path = cortex_path(target) / "MAP.md"
        map_path.write_text(
            read_text(map_path)
            + "\n| [[cortex-memory]] | Files are memory | [[nested/deep-memory]] |\n"
            + "| [[nested/deep-memory]] | Nested cells are audited | [[cortex-memory]] |\n",
            encoding="utf-8",
        )
        links_path = cortex_path(target) / "LINKS.md"
        links_path.write_text(
            read_text(links_path)
            + "\n- [[cortex-memory]] -> `sources/karpathy-pattern.md`\n"
            + "- [[nested/deep-memory]] -> [[cortex-memory]]\n",
            encoding="utf-8",
        )

        verify_result = verify(target)
        audit_result = audit(target)
        rebuild_result = rebuild(target)
        recall_result = recall(target, "Cortex", 5)

        db_path = recall_db_path(target)
        first_size = db_path.stat().st_size if db_path.exists() else 0
        db_path.unlink(missing_ok=True)
        rebuild_again = rebuild(target)
        second_size = db_path.stat().st_size if db_path.exists() else 0
        fallback_result = recall(target, "Cortex", 5, force_rg=True)
        absorb_result = absorb_plan(target, source)
        learn_result = learn(target, "authorized applied memory", source)
        unauth_apply_result = apply_cell(
            target,
            "applied-memory",
            "This should not write without explicit authorization.",
            ["sources/karpathy-pattern.md"],
            None,
            [],
            authorized=False,
            update_existing=False,
        )
        apply_result = apply_cell(
            target,
            "applied-memory",
            "Authorized apply creates a grounded Cortex cell and refreshes recall.",
            ["sources/karpathy-pattern.md"],
            "Authorized apply creates grounded cells.",
            ["cortex-memory"],
            authorized=True,
            update_existing=False,
        )
        read_cell_result = read_cell(target, "applied-memory")
        broken_cell = cortex_path(target) / "cells" / "nested" / "broken-link.md"
        broken_cell.write_text(
            "# Broken Link\n\n"
            "## Claim\n\n"
            "This cell points to [[missing-cell]].\n\n"
            "## Evidence\n\n"
            "- `sources/karpathy-pattern.md` keeps the failure focused on the broken link.\n",
            encoding="utf-8",
        )
        broken_audit_result = audit(target)
        broken_cell.unlink()
        loose_cell = cortex_path(target) / "cells" / "loose-summary.md"
        loose_cell.write_text("# Loose Summary\n\nThis is only a summary with no explicit evidence.\n", encoding="utf-8")
        loose_audit_result = audit(target)
        loose_cell.unlink()

        result = {
            "init": init_result,
            "verify": verify_result,
            "audit": audit_result,
            "rebuild": rebuild_result,
            "rebuild_after_delete": rebuild_again,
            "rebuild_equivalent": first_size > 0 and second_size > 0,
            "recall": recall_result,
            "fallback_recall": fallback_result,
            "absorb_plan": absorb_result,
            "learn": learn_result,
            "unauthorized_apply": unauth_apply_result,
            "apply": apply_result,
            "read_cell": read_cell_result,
            "broken_link_audit": broken_audit_result,
            "loose_cell_audit": loose_audit_result,
        }
        print(json.dumps(result, indent=2))

        checks = (
            verify_result["status"] == "PASS",
            audit_result["status"] == "PASS",
            rebuild_result["status"] == "PASS",
            rebuild_again["status"] == "PASS",
            result["rebuild_equivalent"],
            recall_result["status"] == "PASS" and recall_result["backend"] == "sqlite-fts5",
            fallback_result["status"] == "PASS" and fallback_result["backend"] == "rg",
            absorb_result["status"] == "PASS" and absorb_result["writes"] == [],
            learn_result["status"] == "PASS" and learn_result["writes"] == [],
            unauth_apply_result["status"] == "NEEDS_AUTH" and unauth_apply_result["writes"] == [],
            apply_result["status"] == "PASS",
            any(path.endswith("cells/applied-memory.md") for path in apply_result["writes"]),
            read_cell_result["status"] == "PASS" and "Authorized apply" in read_cell_result["text"],
            broken_audit_result["status"] == "FAIL",
            any("missing-cell" in failure for failure in broken_audit_result["failures"]),
            loose_audit_result["status"] == "FAIL",
            any("explicit evidence ref" in failure for failure in loose_audit_result["failures"]),
        )
        if not all(checks):
            print("[cortex] FAIL")
            return 1
    print("[cortex] PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        nargs="?",
        choices=(
            "init",
            "verify",
            "audit",
            "recall",
            "rebuild",
            "absorb-plan",
            "read-cell",
            "learn",
            "apply",
            "scaffold",
            "check",
            "lint",
        ),
    )
    parser.add_argument("query", nargs="?")
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--source", type=Path)
    parser.add_argument("--cell")
    parser.add_argument("--claim")
    parser.add_argument("--summary")
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--link", action="append", default=[])
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--force-rg", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    command = {"scaffold": "init", "check": "verify", "lint": "audit"}.get(args.command, args.command)
    if command == "init":
        result = init(args.target)
    elif command == "verify":
        result = verify(args.target)
    elif command == "audit":
        result = audit(args.target)
    elif command == "rebuild":
        result = rebuild(args.target)
    elif command == "recall":
        if not args.query:
            parser.error("recall requires a query")
        result = recall(args.target, args.query, args.limit, args.force_rg)
    elif command == "absorb-plan":
        if args.source is None:
            parser.error("absorb-plan requires --source")
        result = absorb_plan(args.target, args.source)
    elif command == "read-cell":
        if not args.cell:
            parser.error("read-cell requires --cell")
        result = read_cell(args.target, args.cell)
    elif command == "learn":
        result = learn(args.target, args.query, args.source)
    elif command == "apply":
        if not args.cell:
            parser.error("apply requires --cell")
        result = apply_cell(
            args.target,
            args.cell,
            args.claim or "",
            args.evidence,
            args.summary,
            args.link,
            args.yes,
            args.update,
        )
    else:
        parser.error("command is required unless --self-test is used")

    print(json.dumps(result, indent=2))
    status = result.get("status") or result.get("verify", {}).get("status")
    if status == "FAIL":
        print("[cortex] FAIL")
        return 1
    if status == "NEEDS_AUTH":
        print("[cortex] NEEDS_AUTH")
        return 2
    print("[cortex] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
