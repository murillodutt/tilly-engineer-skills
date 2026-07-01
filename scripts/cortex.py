#!/usr/bin/env python3
"""Operate the TES Cortex filesystem memory layer."""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unicodedata

import checkpoint as checkpoint_helper
import field_reports
import scope_contract


CORTEX_ROOT = Path("docs/agents/cortex")
RECALL_DB = Path(".tes/cortex/recall.sqlite")
SEMANTIC_DB = Path(".tes/cortex/semantic.sqlite")
DEFAULT_SEMANTIC_MODEL = "Xenova/multilingual-e5-small"
LEXICAL_MODEL = "tes-lexical-curation-v1"
LEXICAL_DIMENSIONS = 64
REFLECT_PROPOSAL_SLUG_LIMIT = 80
INSTALLED_RUNTIME_PREFIXES = (
    ".tes/bin/",
    ".tes/postinstall-runs/",
)
INSTALLED_RUNTIME_FILES = {
    ".tes/manifest.json",
    ".tes/postinstall.json",
    ".tes/tes-install-lock.json",
}
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
H2_HEADING = re.compile(r"^## .+", re.MULTILINE)
CLAIM_SECTION = re.compile(r"^## Claims?$", re.MULTILINE)
EVIDENCE_SECTION = re.compile(r"^## Evidence$", re.MULTILINE)
EVIDENCE_REF = re.compile(
    r"(?<![A-Za-z0-9_./-])(`?((?:/|\.\.?/)?(?:docs/agents/cortex/)?sources/[^`\s)]+|"
    r"(?:/|\.\.?/)?docs/agents/evidence/[^`\s)]+)`?|^[-*] Assumption:|^Assumption:)",
    re.MULTILINE,
)
REAL_EVIDENCE_REF = re.compile(
    r"(?<![A-Za-z0-9_./-])`?((?:/|(?:(?:\.\.?/)+))?(?:docs/agents/cortex/)?sources/[^`\s)]+|"
    r"(?:/|(?:(?:\.\.?/)+))?docs/agents/evidence/[^`\s)]+)`?"
)
ABSOLUTE_EVIDENCE_PATH = re.compile(
    r"(?<![:/.\w-])/(?!/)[^\s`)'\",<>]+|"
    r"(?<![A-Za-z0-9_])(?:[A-Za-z]:\\[^\s`)'\",<>]+|~/[^\s`)'\",<>]+)"
)
STOPWORDS = {
    "a", "an", "and", "are", "as", "be", "by", "com", "como", "con", "da", "das", "de", "del",
    "do", "dos", "e", "el", "em", "en", "for", "from", "is", "it", "la", "las", "los", "na",
    "no", "not", "o", "of", "or", "os", "para", "por", "que", "the", "to", "um", "uma", "un",
    "una", "with", "under", "into", "from", "this", "that", "these", "those", "should", "must",
}
SYNONYMS = {
    "approval": "authorization",
    "authorized": "authorization",
    "authorize": "authorization",
    "autorizacao": "authorization",
    "autorizado": "authorization",
    "evidence": "source",
    "evidencia": "source",
    "fonte": "source",
    "fontes": "source",
    "proof": "source",
    "reference": "source",
    "memory": "memory",
    "memoria": "memory",
    "knowledge": "memory",
    "conhecimento": "memory",
    "artifact": "file",
    "artifacts": "file",
    "artefato": "file",
    "artefatos": "file",
    "file": "file",
    "files": "file",
    "filesystem": "file",
    "markdown": "file",
    "durable": "durable",
    "persistent": "durable",
    "versioned": "durable",
    "versionado": "durable",
    "versionados": "durable",
    "curadoria": "curation",
    "curate": "curation",
    "curation": "curation",
    "compact": "compact",
    "compaction": "compact",
    "dedupe": "merge",
    "duplicate": "merge",
    "merge": "merge",
    "redundant": "merge",
    "split": "split",
    "separate": "split",
    "separar": "split",
    "separation": "split",
}
RETAIN_TERMS = {"audit", "auditable", "durable", "keep", "preserve", "retain", "source", "versioned"}
DISCARD_TERMS = {
    "automatic", "delete", "discard", "erase", "overwrit", "overwrite", "purge", "remov", "remove",
    "rewrite",
}
TRANSIENT_TERMS = {"draft", "maybe", "scratch", "temporary", "todo", "transient", "wip"}
GENERIC_TERMS = {"context", "important", "information", "note", "project", "thing", "useful", "value"}
OPERATOR_MUTABILITY = {
    "health": "read-only",
    "peek": "read-only",
    "review": "read-only",
    "checkpoint": "checkpoint-state-write",
    "remember": "durable-memory-write",
    "forget": "blocked-destructive",
}


def cortex_path(target: Path) -> Path:
    return target / CORTEX_ROOT


def recall_db_path(target: Path) -> Path:
    return target / RECALL_DB


def semantic_db_path(target: Path) -> Path:
    return target / SEMANTIC_DB


def rel(path: Path, target: Path) -> str:
    try:
        return str(path.relative_to(target))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def starter_files(today: str) -> dict[str, str]:
    return {
        "CONTRACT.md": f"""# TES Cortex Contract

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
| Recall index | `.tes/cortex/recall.sqlite` | Derived cache, rebuilt from files |
| Semantic index | `.tes/cortex/semantic.sqlite` | Derived curation cache, rebuilt from cells |

SQLite is never memory and never source of truth. Both recall and semantic
indexes may be deleted and rebuilt from `sources/**`, `cells/**`, `MAP.md`,
`TRAIL.md`, `LINKS.md`, and this contract.

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
| `curate-plan` | Classify semantic curation needs without writing memory |
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
The recall index at `.tes/cortex/recall.sqlite` is derived and rebuildable.
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
        ("TES Cortex Schema", "TES Cortex Contract"),
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
`.tes/cortex/recall.sqlite` is derived and rebuildable from the versioned
artifacts. `rg` is the required fallback when FTS5 recall is unavailable.
"""
    if path.name == "CONTRACT.md" and ".tes/cortex/semantic.sqlite" not in updated:
        updated += """

## Semantic Curation Boundary

The semantic index at `.tes/cortex/semantic.sqlite` is a derived curation
cache rebuilt from `cells/**`. `curate-plan` may refresh that cache, but it
never writes `sources/**`, `cells/**`, `MAP.md`, `LINKS.md`, or `TRAIL.md`.
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


def bounded_slug(value: str, fallback: str = "new-cell", max_length: int = 80) -> tuple[str, bool]:
    slug = slugify(value, fallback)
    if len(slug) <= max_length:
        return slug, False

    digest = hashlib.sha256(slug.encode("utf-8")).hexdigest()[:8]
    head_limit = max(1, max_length - len(digest) - 1)
    head = slug[:head_limit].rstrip("-") or fallback
    return f"{head}-{digest}", True


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
    evidence = section_text(text, {"evidence"})

    if h1_count != 1:
        failures.append(f"cell must contain exactly one H1: {rel(cell, target)}")
    if not CLAIM_SECTION.search(text):
        failures.append(f"cell missing ## Claim section: {rel(cell, target)}")
    if not EVIDENCE_SECTION.search(text):
        failures.append(f"cell missing ## Evidence section: {rel(cell, target)}")
    if not EVIDENCE_REF.search(text):
        failures.append(f"cell missing explicit evidence ref: {rel(cell, target)}")
    failures.extend(
        f"cell evidence ref invalid: {rel(cell, target)}: {failure}"
        for failure in evidence_ref_failures(target, evidence)
    )

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


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def canonical_token(token: str) -> str:
    token = strip_accents(token.lower())
    token = SYNONYMS.get(token, token)
    if token.endswith("ies") and len(token) > 4:
        token = token[:-3] + "y"
    elif token.endswith("s") and len(token) > 4:
        token = token[:-1]
    elif token.endswith("ing") and len(token) > 6:
        token = token[:-3]
    elif token.endswith("ed") and len(token) > 5:
        token = token[:-2]
    return SYNONYMS.get(token, token)


def tokenize(value: str) -> list[str]:
    tokens: list[str] = []
    for raw in re.findall(r"[A-Za-zÀ-ÿ0-9_'-]+", value):
        token = canonical_token(raw.strip("_'-"))
        if len(token) < 3 or token in STOPWORDS:
            continue
        tokens.append(token)
    return tokens


def weak_memory_prompt(value: str) -> bool:
    tokens = tokenize(value)
    signal = [token for token in tokens if token not in GENERIC_TERMS]
    return len(set(signal)) < 2


def lexical_vector(tokens: list[str], dimensions: int = LEXICAL_DIMENSIONS) -> list[float]:
    vector = [0.0] * dimensions
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        slot = int.from_bytes(digest[:4], "big") % dimensions
        vector[slot] += 1.0
    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0:
        return vector
    return [round(value / magnitude, 8) for value in vector]


def cosine(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(a * b for a, b in zip(left, right))


def section_text(text: str, names: set[str]) -> str:
    lines = text.splitlines()
    capture = False
    captured: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            heading = stripped[3:].strip().lower()
            if heading in names:
                capture = True
                continue
            if capture:
                break
        if capture:
            captured.append(line)
    return "\n".join(captured).strip()


def cell_title(text: str, path: Path) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return title_from_slug(path.name)


def cell_record(path: Path, target: Path, cells_root_path: Path) -> dict[str, object]:
    text = read_text(path)
    claim = section_text(text, {"claim", "claims"})
    evidence = section_text(text, {"evidence"})
    links = section_text(text, {"links"})
    title = cell_title(text, path)
    structured_text = f"passage: {title}\nClaim: {claim}\nEvidence: {evidence}\nLinks: {links}"
    tokens = tokenize(f"{title}\n{claim}")
    return {
        "path": rel(path, target),
        "cell_ref": cell_ref(path, cells_root_path),
        "stem": cell_stem(path),
        "title": title,
        "text": text,
        "claim": claim,
        "evidence": evidence,
        "links": links,
        "structured_text": structured_text,
        "tokens": tokens,
        "token_set": set(tokens),
        "vector": lexical_vector(tokens),
        "line_count": len(text.splitlines()),
        "h2_count": len(H2_HEADING.findall(text)),
        "bullet_count": sum(1 for line in text.splitlines() if line.strip().startswith(("-", "*"))),
        "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "wikilinks": set(match.strip() for match in WIKILINK.findall(text)),
        "assumption_count": len(re.findall(r"^\s*(?:[-*]\s*)?Assumption:", text, re.IGNORECASE | re.MULTILINE)),
    }


def cortex_cells(target: Path) -> list[dict[str, object]]:
    root = cortex_path(target)
    root_cells = root / "cells"
    if not root_cells.exists():
        return []
    return [cell_record(path, target, root_cells) for path in sorted(root_cells.rglob("*.md"))]


def relation_exists(
    left: dict[str, object],
    right: dict[str, object],
    links_text: str,
) -> bool:
    left_refs = {str(left["cell_ref"]), str(left["stem"])}
    right_refs = {str(right["cell_ref"]), str(right["stem"])}
    left_links = {str(item) for item in left["wikilinks"]}  # type: ignore[index]
    right_links = {str(item) for item in right["wikilinks"]}  # type: ignore[index]
    if left_links & right_refs or right_links & left_refs:
        return True
    for line in links_text.splitlines():
        has_left = any(f"[[{value}]]" in line for value in left_refs)
        has_right = any(f"[[{value}]]" in line for value in right_refs)
        if has_left and has_right:
            return True
    return False


def token_similarity(left: dict[str, object], right: dict[str, object]) -> dict[str, float]:
    left_set = left["token_set"]  # type: ignore[assignment]
    right_set = right["token_set"]  # type: ignore[assignment]
    if not left_set or not right_set:
        return {"cosine": 0.0, "jaccard": 0.0, "overlap": 0.0, "score": 0.0}
    intersection = len(left_set & right_set)
    union = len(left_set | right_set)
    jaccard = intersection / union if union else 0.0
    overlap = intersection / min(len(left_set), len(right_set))
    cos = cosine(left["vector"], right["vector"])  # type: ignore[arg-type]
    return {
        "cosine": round(cos, 4),
        "jaccard": round(jaccard, 4),
        "overlap": round(overlap, 4),
        "score": round(max(cos, jaccard, overlap * 0.9), 4),
    }


def direction(cell: dict[str, object]) -> str:
    tokens = {str(token) for token in cell["token_set"]}  # type: ignore[index]
    hard_retain_terms = RETAIN_TERMS - {"source"}
    retain = bool(tokens & hard_retain_terms)
    discard = bool(tokens & DISCARD_TERMS)
    if discard and not bool(tokens & {"keep", "preserve", "retain"}):
        return "discard"
    if retain and not discard:
        return "retain"
    if discard and not retain:
        return "discard"
    text = strip_accents(str(cell["claim"]).lower())
    conflict_terms = ("contradict", "conflict", "supersede", "deprecated", "no longer")
    if any(term in text for term in conflict_terms):
        return "conflict"
    return "neutral"


def real_evidence_refs(evidence: str) -> list[str]:
    refs = REAL_EVIDENCE_REF.findall(evidence)
    return sorted(set(ref.strip("`") for ref in refs))


def resolve_real_evidence_ref(target: Path, raw_ref: str) -> tuple[Path | None, str | None]:
    stripped = raw_ref.strip().strip("`")
    candidate = Path(stripped)
    if candidate.is_absolute():
        return None, f"absolute evidence path is not allowed: {stripped}"
    if ".." in candidate.parts:
        return None, f"evidence path traversal is not allowed: {stripped}"

    parts = candidate.parts
    sources_prefix = ("docs", "agents", "cortex", "sources")
    evidence_prefix = ("docs", "agents", "evidence")
    if parts[:4] == sources_prefix:
        root = (cortex_path(target) / "sources").resolve()
        suffix = Path(*parts[4:])
    elif parts[:1] == ("sources",):
        root = (cortex_path(target) / "sources").resolve()
        suffix = Path(*parts[1:])
    elif parts[:3] == evidence_prefix:
        root = (target / "docs" / "agents" / "evidence").resolve()
        suffix = Path(*parts[3:])
    else:
        return None, f"unsupported evidence path: {stripped}"

    resolved = (root / suffix).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None, f"evidence path escapes allowed root: {stripped}"
    if not resolved.is_file():
        return None, f"evidence file missing: {rel(resolved, target)}"
    return resolved, None


def evidence_ref_failures(target: Path, evidence: str) -> list[str]:
    failures: list[str] = []
    absolute_paths = sorted(set(match.group(0) for match in ABSOLUTE_EVIDENCE_PATH.finditer(evidence)))
    for raw_path in absolute_paths:
        failures.append(f"absolute evidence path is not allowed: {raw_path}")
    for raw_ref in real_evidence_refs(evidence):
        _resolved, failure = resolve_real_evidence_ref(target, raw_ref)
        if failure and not (failure.startswith("absolute evidence path is not allowed:") and raw_ref in absolute_paths):
            failures.append(failure)
    return failures


def redundancy_reason(cell: dict[str, object]) -> str | None:
    claim = str(cell["claim"]).strip()
    tokens = [str(token) for token in cell["tokens"]]  # type: ignore[index]
    if not claim:
        return "missing claim text"
    if len(tokens) < 6:
        return "claim is too short to be durable"
    generic = sum(1 for token in tokens if token in GENERIC_TERMS)
    if generic / max(len(tokens), 1) >= 0.45:
        return "claim is mostly generic terms"
    sentences = [part.strip().lower() for part in re.split(r"[.!?]\s+", claim) if part.strip()]
    if len(sentences) != len(set(sentences)):
        return "claim repeats identical sentences"
    return None


def markdown_bullet_count(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip().startswith(("-", "*")))


def split_reason(cell: dict[str, object]) -> str | None:
    claim = str(cell["claim"])
    claim_tokens = tokenize(claim)
    h2_count = int(cell["h2_count"])
    line_count = int(cell["line_count"])
    bullet_count = int(cell["bullet_count"])
    claim_bullet_count = markdown_bullet_count(claim)
    evidence_bullet_count = markdown_bullet_count(str(cell["evidence"]))
    non_evidence_bullet_count = max(0, bullet_count - evidence_bullet_count)
    topic_markers = len(re.findall(r"\b(also|besides|separately|tambem|também|alem disso|além disso)\b", claim, re.I))
    if line_count > 120:
        return f"cell has {line_count} lines"
    if len(claim_tokens) > 140:
        return f"claim has {len(claim_tokens)} semantic tokens"
    if h2_count > 6:
        return f"cell has {h2_count} H2 sections"
    if bullet_count > 22:
        if claim_bullet_count > 8:
            return f"claim has {claim_bullet_count} bullet lines"
        if non_evidence_bullet_count > 10:
            return f"cell has {non_evidence_bullet_count} non-evidence bullet lines"
        if bullet_count > 30:
            return f"cell has {bullet_count} bullet lines"
        if h2_count > 5 or len(claim_tokens) > 110 or line_count > 100 or topic_markers >= 2:
            return f"cell has {bullet_count} bullet lines plus structural split pressure"
    if topic_markers >= 3:
        return "claim mixes multiple topic markers"
    return None


def reject_reason(cell: dict[str, object]) -> str | None:
    tokens = {str(token) for token in cell["token_set"]}  # type: ignore[index]
    transient = sorted(tokens & TRANSIENT_TERMS)
    if transient:
        return f"transient terms are not durable memory: {', '.join(transient)}"
    return None


def build_lexical_embeddings(cells: list[dict[str, object]]) -> dict[str, object]:
    return {
        "status": "PASS",
        "backend": "lexical",
        "backend_status": "CERTIFIED",
        "model": LEXICAL_MODEL,
        "dimensions": LEXICAL_DIMENSIONS,
        "vectors": [
            {
                "path": cell["path"],
                "title": cell["title"],
                "content_hash": cell["content_hash"],
                "vector": cell["vector"],
            }
            for cell in cells
        ],
        "failures": [],
    }


def run_xenova_embeddings(cells: list[dict[str, object]]) -> dict[str, object]:
    helper = Path(__file__).with_name("cortex_embed.mjs")
    node = shutil.which("node")
    if node is None:
        return {"status": "BLOCKED", "failures": ["node runtime unavailable for Xenova backend"]}
    if not helper.exists():
        return {"status": "BLOCKED", "failures": [f"missing Xenova helper: {helper}"]}
    payload = {
        "model": DEFAULT_SEMANTIC_MODEL,
        "items": [
            {
                "path": cell["path"],
                "title": cell["title"],
                "content_hash": cell["content_hash"],
                "text": cell["structured_text"],
            }
            for cell in cells
        ],
    }
    result = subprocess.run(
        [node, str(helper)],
        text=True,
        input=json.dumps(payload),
        capture_output=True,
        check=False,
    )
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        parsed = {
            "status": "BLOCKED",
            "failures": [result.stderr.strip() or "Xenova helper did not return JSON"],
        }
    if result.returncode != 0 and parsed.get("status") != "BLOCKED":
        parsed["status"] = "BLOCKED"
        parsed.setdefault("failures", []).append(result.stderr.strip() or "Xenova helper failed")
    return parsed


def semantic_embeddings(
    target: Path,
    cells: list[dict[str, object]],
    backend: str,
    write_index: bool,
) -> dict[str, object]:
    if backend == "lexical":
        embeddings = build_lexical_embeddings(cells)
    else:
        embeddings = run_xenova_embeddings(cells)
        if embeddings.get("status") == "BLOCKED":
            if backend == "xenova":
                embeddings.setdefault("backend", "xenova")
                embeddings.setdefault("backend_status", "BLOCKED")
                return embeddings
            fallback = build_lexical_embeddings(cells)
            fallback["backend_status"] = "DEGRADED"
            fallback["fallback_reason"] = "; ".join(str(item) for item in embeddings.get("failures", []))
            embeddings = fallback
        else:
            embeddings.setdefault("backend", "xenova")
            embeddings.setdefault("backend_status", "CERTIFIED")

    if write_index and embeddings.get("status") == "PASS":
        persist_semantic_index(target, embeddings)
        embeddings["semantic_index"] = rel(semantic_db_path(target), target)
    return embeddings


def persist_semantic_index(target: Path, embeddings: dict[str, object]) -> None:
    db_path = semantic_db_path(target)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    vectors = embeddings.get("vectors", [])
    with sqlite3.connect(db_path) as conn:
        conn.execute("DROP TABLE IF EXISTS cortex_semantic")
        conn.execute(
            "CREATE TABLE cortex_semantic ("
            "path TEXT PRIMARY KEY, "
            "title TEXT NOT NULL, "
            "content_hash TEXT NOT NULL, "
            "backend TEXT NOT NULL, "
            "model TEXT NOT NULL, "
            "dimensions INTEGER NOT NULL, "
            "vector TEXT NOT NULL"
            ")"
        )
        for item in vectors:  # type: ignore[assignment]
            vector = item["vector"]
            conn.execute(
                "INSERT INTO cortex_semantic(path, title, content_hash, backend, model, dimensions, vector) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    item["path"],
                    item.get("title", ""),
                    item.get("content_hash", ""),
                    embeddings.get("backend", "unknown"),
                    embeddings.get("model", ""),
                    int(embeddings.get("dimensions", 0)),
                    json.dumps(vector, separators=(",", ":")),
                ),
            )
        conn.commit()


def linked_pair(left: dict[str, object], right: dict[str, object]) -> dict[str, str]:
    return {
        "left": str(left["path"]),
        "right": str(right["path"]),
    }


def curation_candidate(
    category: str,
    action: str,
    rationale: str,
    next_step: str,
    **values: object,
) -> dict[str, object]:
    return {
        "category": category,
        "action": action,
        "rationale": rationale,
        "next_step": next_step,
        **values,
    }


def curate_plan(target: Path, backend: str = "auto", write_index: bool = True) -> dict[str, object]:
    target = target.resolve()
    verify_result = verify(target)
    failures = list(verify_result["failures"])
    root = cortex_path(target)
    records = cortex_cells(target)
    audit_result = audit(target) if verify_result["status"] == "PASS" else {"status": "FAIL", "failures": failures}
    if audit_result.get("status") == "FAIL":
        failures.extend(str(item) for item in audit_result.get("failures", []))

    if failures:
        return {
            "target": str(target),
            "status": "FAIL",
            "requested_backend": backend,
            "backend": "none",
            "writes": [],
            "derived_writes": [],
            "failures": sorted(set(failures)),
            "audit": audit_result,
        }

    embeddings = semantic_embeddings(target, records, backend, write_index)
    if embeddings.get("status") == "BLOCKED":
        return {
            "target": str(target),
            "status": "BLOCKED",
            "requested_backend": backend,
            "backend": embeddings.get("backend", "xenova"),
            "backend_status": "BLOCKED",
            "writes": [],
            "derived_writes": [],
            "failures": embeddings.get("failures", []),
        }

    vector_by_path = {
        str(item["path"]): item["vector"]
        for item in embeddings.get("vectors", [])  # type: ignore[assignment]
    }
    for record in records:
        if str(record["path"]) in vector_by_path:
            record["vector"] = vector_by_path[str(record["path"])]

    links_text = read_text(root / "LINKS.md") if (root / "LINKS.md").exists() else ""
    merge_candidates: list[dict[str, object]] = []
    split_candidates: list[dict[str, object]] = []
    link_candidates: list[dict[str, object]] = []
    tension_candidates: list[dict[str, object]] = []
    evidence_gaps: list[dict[str, object]] = []
    redundancy_warnings: list[dict[str, object]] = []
    reject_candidates: list[dict[str, object]] = []

    for record in records:
        split = split_reason(record)
        if split:
            split_candidates.append(
                curation_candidate(
                    "split",
                    "split-cell",
                    f"{record['path']} is carrying too much independent material: {split}.",
                    "Split the cell into narrower claims, preserve evidence refs, then rerun audit and curate-plan.",
                    path=record["path"],
                    reason=split,
                )
            )
        reject = reject_reason(record)
        if reject:
            reject_candidates.append(
                curation_candidate(
                    "reject",
                    "keep-out-of-cortex",
                    f"{record['path']} looks transient rather than durable memory: {reject}.",
                    "Remove the transient claim from Cortex or move it to a project work queue outside memory.",
                    path=record["path"],
                    reason=reject,
                )
            )
        evidence = str(record["evidence"])
        evidence_refs = real_evidence_refs(evidence)
        if not evidence_refs or int(record["assumption_count"]) > 1:
            reason = "missing real source evidence" if not evidence_refs else "too many Assumption lines"
            evidence_gaps.append(
                curation_candidate(
                    "evidence_gap",
                    "add-evidence-or-defer",
                    f"{record['path']} is not grounded enough for durable memory: {reason}.",
                    "Add a source under sources/** or defer the claim until evidence exists; do not apply from assumption alone.",
                    path=record["path"],
                    reason=reason,
                    assumption_count=record["assumption_count"],
                    real_evidence_refs=evidence_refs,
                )
            )
        redundant = redundancy_reason(record)
        if redundant:
            redundancy_warnings.append(
                curation_candidate(
                    "redundancy",
                    "review-wording",
                    f"{record['path']} may be too generic or repetitive: {redundant}.",
                    "Tighten the claim or merge it into a stronger adjacent cell if it adds no durable distinction.",
                    path=record["path"],
                    reason=redundant,
                )
            )

    for index, left in enumerate(records):
        for right in records[index + 1:]:
            scores = token_similarity(left, right)
            left_direction = direction(left)
            right_direction = direction(right)
            conflict = (
                {left_direction, right_direction} == {"retain", "discard"}
                or "conflict" in {left_direction, right_direction}
            )
            pair = linked_pair(left, right)
            if conflict and scores["score"] >= 0.18:
                tension_candidates.append(
                    curation_candidate(
                        "tension",
                        "resolve-contradiction",
                        (
                            f"{pair['left']} and {pair['right']} point in conflicting directions "
                            f"({left_direction} vs {right_direction}) with score {scores['score']}."
                        ),
                        "Read both cells and their sources, then record the surviving rule or explicit contradiction.",
                        **pair,
                        score=scores["score"],
                        left_direction=left_direction,
                        right_direction=right_direction,
                    )
                )
                continue
            if scores["score"] >= 0.54:
                merge_candidates.append(
                    curation_candidate(
                        "merge",
                        "merge-or-dedupe",
                        f"{pair['left']} and {pair['right']} overlap strongly with score {scores['score']}.",
                        "Compare claims and evidence, merge only the duplicated durable claim, and keep provenance.",
                        **pair,
                        score=scores["score"],
                    )
                )
            elif scores["score"] >= 0.32 and not relation_exists(left, right, links_text):
                link_candidates.append(
                    curation_candidate(
                        "link",
                        "add-relationship",
                        f"{pair['left']} and {pair['right']} are related with score {scores['score']} but not linked.",
                        "Add a deliberate LINKS.md or cell wikilink edge if the relationship survives source review.",
                        **pair,
                        score=scores["score"],
                    )
                )

    merge_candidates.sort(key=lambda item: (-float(item["score"]), str(item["left"]), str(item["right"])))
    link_candidates.sort(key=lambda item: (-float(item["score"]), str(item["left"]), str(item["right"])))
    tension_candidates.sort(key=lambda item: (-float(item["score"]), str(item["left"]), str(item["right"])))
    split_candidates.sort(key=lambda item: str(item["path"]))
    evidence_gaps.sort(key=lambda item: str(item["path"]))
    redundancy_warnings.sort(key=lambda item: str(item["path"]))
    reject_candidates.sort(key=lambda item: str(item["path"]))

    blocking = bool(
        merge_candidates
        or split_candidates
        or tension_candidates
        or evidence_gaps
        or reject_candidates
    )
    backend_status = str(embeddings.get("backend_status", "CERTIFIED"))
    status = "FAIL" if blocking else ("DEGRADED" if backend_status == "DEGRADED" else "PASS")
    derived_writes = []
    if write_index and embeddings.get("semantic_index"):
        derived_writes.append(str(embeddings["semantic_index"]))

    return {
        "target": str(target),
        "status": status,
        "requested_backend": backend,
        "backend": embeddings.get("backend", "lexical"),
        "backend_status": backend_status,
        "model": embeddings.get("model", LEXICAL_MODEL),
        "dimensions": embeddings.get("dimensions", LEXICAL_DIMENSIONS),
        "semantic_index": embeddings.get("semantic_index"),
        "writes": [],
        "derived_writes": derived_writes,
        "failures": [] if status != "FAIL" else ["semantic curation gate requires attention"],
        "cell_count": len(records),
        "thresholds": {
            "merge_score": 0.54,
            "link_score": 0.32,
            "tension_score": 0.18,
            "max_cell_lines": 120,
            "max_claim_tokens": 140,
            "soft_max_cell_bullets": 22,
            "max_claim_bullets_before_split": 8,
            "max_non_evidence_bullets_before_split": 10,
            "max_cell_bullets_before_split": 30,
            "max_assumptions_without_review": 1,
        },
        "merge_candidates": merge_candidates,
        "split_candidates": split_candidates,
        "link_candidates": link_candidates,
        "tension_candidates": tension_candidates,
        "evidence_gaps": evidence_gaps,
        "redundancy_warnings": redundancy_warnings,
        "reject_candidates": reject_candidates,
        "audit": audit_result,
    }


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
    fts_query = sqlite_fts_query(query)
    with sqlite3.connect(db_path) as conn:
        if query == "*":
            rows = conn.execute(
                "SELECT path, layer, title, substr(body, 1, 240) FROM cortex_recall LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT path, layer, title, snippet(cortex_recall, 3, '', '', ' ... ', 16) "
                "FROM cortex_recall WHERE cortex_recall MATCH ? LIMIT ?",
                (fts_query, limit),
            ).fetchall()
    return {
        "backend": "sqlite-fts5",
        "matches": [
            {"path": path, "layer": layer, "title": title, "excerpt": excerpt}
            for path, layer, title, excerpt in rows
        ],
    }


def sqlite_fts_query(query: str) -> str:
    """Return a conservative FTS5 query for natural-language recall text."""
    tokens = re.findall(r"[A-Za-z0-9_]{2,80}", query)
    if not tokens:
        return query
    return " ".join(f'"{token}"' for token in tokens[:12])


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
    weak_prompt = bool(prompt) and weak_memory_prompt(prompt)

    cell_name = slugify(Path(source_rel).stem if source_rel else prompt)
    evidence = f"`{source_rel.removeprefix('docs/agents/cortex/')}`" if source_rel else "Assumption: user-approved conversation evidence"
    if not failures and source_rel is None and weak_prompt:
        return {
            "target": str(target),
            "status": "NEEDS_EVIDENCE",
            "failures": [],
            "writes": [],
            "proposal": None,
            "evidence_gap_reason": (
                "learn needs a specific durable claim or --source under docs/agents/cortex/sources/**; "
                "the query is too generic to promote safely"
            ),
        }

    return {
        "target": str(target),
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
        "writes": [],
        "proposal": None if failures else {
            "cell": f"docs/agents/cortex/cells/{cell_name}.md",
            "claim_needed": "Write a durable claim, not a loose summary.",
            "evidence": evidence,
            "evidence_status": "source" if source_rel else "assumption",
            "route": "proposal-only; run apply with --yes after reviewing the claim and evidence",
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


def git_status_paths(target: Path) -> list[tuple[str, str]]:
    result = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    entries: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        status = line[:2]
        path = line[3:].strip()
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[1]
        entries.append((status, path))
    return entries


def git_changed_files(target: Path, limit: int) -> list[str]:
    return [path for _status, path in git_status_paths(target)][:limit]


def text_file_line_count(path: Path) -> int:
    if not path.is_file():
        return 0
    try:
        data = path.read_bytes()
    except OSError:
        return 0
    if not data or b"\0" in data[:8192]:
        return 0
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return 0
    return data.count(b"\n") + (0 if data.endswith(b"\n") else 1)


def installed_runtime_update_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized in INSTALLED_RUNTIME_FILES or normalized.startswith(INSTALLED_RUNTIME_PREFIXES)


def reflect_signal(path: str) -> bool:
    return durable_signal(path) and not installed_runtime_update_path(path)


def git_untracked_durable_line_count(target: Path) -> int:
    total = 0
    for status, path in git_status_paths(target):
        if status != "??" or not reflect_signal(path):
            continue
        candidate = (target / path).resolve()
        try:
            candidate.relative_to(target.resolve())
        except ValueError:
            continue
        total += text_file_line_count(candidate)
    return total


def git_diff_line_count(target: Path) -> int:
    result = subprocess.run(
        ["git", "diff", "--numstat", "HEAD"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return 0
    total = 0
    for line in result.stdout.splitlines():
        added, _, deleted = line.partition("\t")
        deleted, _, path = deleted.partition("\t")
        if not reflect_signal(path):
            continue
        if added.isdigit():
            total += int(added)
        if deleted.isdigit():
            total += int(deleted)
    return total + git_untracked_durable_line_count(target)


def durable_signal(path: str) -> bool:
    return path == "package.json" or path == "README.md" or path.startswith((
        "docs/",
        "src/",
        "scripts/",
        ".agents/",
        ".cursor/",
        ".codex/",
    )) or path in {"AGENTS.md", "CLAUDE.md", "CURSOR.md"}


def preferred_cortex_command(target: Path) -> str:
    local_helper = target / ".tes/bin/cortex.py"
    if local_helper.exists():
        return "python3 .tes/bin/cortex.py"
    package_helper = target / "scripts/cortex.py"
    if package_helper.exists():
        return "python3 scripts/cortex.py"
    return "python3 <tes-package>/scripts/cortex.py"


def reflect(target: Path, query: str | None, limit: int = 20, line_budget: int = 500) -> dict[str, object]:
    target = target.resolve()
    root = cortex_path(target)
    if not root.exists():
        return {
            "target": str(target),
            "status": "SKIP",
            "reason": "Cortex is not initialized in this target.",
            "writes": [],
            "capture_needed": False,
        }

    verify_result = verify(target)
    if verify_result["status"] != "PASS":
        return {
            "target": str(target),
            "status": "FAIL",
            "failures": verify_result["failures"],
            "writes": [],
        }

    changed_files = git_changed_files(target, limit)
    durable_files = [path for path in changed_files if reflect_signal(path)]
    changed_lines = git_diff_line_count(target)
    curation_due = changed_lines >= line_budget > 0
    prompt = (query or "").strip()
    weak_prompt = bool(prompt) and weak_memory_prompt(prompt)
    capture_needed = bool((prompt and not weak_prompt) or durable_files or curation_due)
    cell_seed = prompt or (durable_files[0] if durable_files else "closure-reflection")
    cell_fallback = "session-reflection" if prompt else "closure-reflection"
    cell_name, cell_name_capped = bounded_slug(
        cell_seed,
        fallback=cell_fallback,
        max_length=REFLECT_PROPOSAL_SLUG_LIMIT,
    )
    evidence = (
        f"Assumption: user-approved closure note - {prompt}"
        if prompt else
        "Assumption: agent-observed local git diff after material work"
    )
    evidence_status = "closure-note" if prompt else "local-diff"
    command = preferred_cortex_command(target)
    no_capture_reason = None
    if not capture_needed:
        if weak_prompt:
            no_capture_reason = "reflection query is too generic to promote without evidence"
        elif changed_files and all(installed_runtime_update_path(path) for path in changed_files):
            no_capture_reason = (
                "only installed TES runtime helper/cache changes were observed; "
                "derived update noise does not require Cortex capture"
            )
        else:
            no_capture_reason = "no durable changed files, specific closure note, or curation threshold was observed"

    return {
        "target": str(target),
        "status": "PASS",
        "writes": [],
        "capture_needed": capture_needed,
        "changed_files": changed_files,
        "durable_files": durable_files,
        "changed_lines": changed_lines,
        "line_budget": line_budget,
        "curation_due": curation_due,
        "curation_policy": (
            "When curation is due, run curate-plan before proposing compaction, split, "
            "merge, rejection, or redundancy removal. Do not delete Cortex content automatically."
        ),
        "no_capture_reason": no_capture_reason,
        "proposal": None if not capture_needed else {
            "cell": f"docs/agents/cortex/cells/{cell_name}.md",
            "cell_name_reason": (
                "long reflection seed was capped; prefer replacing this with a short "
                "claim-specific cell name before apply"
                if cell_name_capped else
                "derived from reflection seed"
            ),
            "claim_needed": "Promote only a durable decision, lesson, contract change, or reusable project fact.",
            "evidence": evidence,
            "evidence_status": evidence_status,
            "route": "proposal-only; review the claim and run apply with --yes only after explicit approval",
            "apply_command": (
                f"{command} apply "
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


def command_scope_evidence(command: str, source: Path | None, evidence: list[str]) -> object:
    if source is not None:
        return str(source)
    if evidence:
        return evidence[0]
    if command == "checkpoint":
        return "none"
    if command in {"recall", "read-cell", "verify", "audit", "curate-plan", "health", "peek", "review", "forget"}:
        return "docs/agents/cortex/MAP.md"
    return "docs/agents/cortex/TRAIL.md"


def attach_runtime_scope(
    result: dict[str, object],
    target: Path,
    command_name: str,
    source: Path | None,
    evidence: list[str],
) -> dict[str, object]:
    verify = result.get("verify")
    status = result.get("status")
    if not status and isinstance(verify, dict):
        status = verify.get("status")
    scope_result = scope_contract.normalize_scope(
        target,
        adapter="local",
        agent="cortex-cli",
        run=f"cortex-{command_name}",
        source="cortex",
        evidence_ref=command_scope_evidence(command_name, source, evidence),
        status=str(status or "UNKNOWN"),
    )
    result["scope"] = scope_result.get("scope", {})
    result["scope_status"] = scope_result.get("status", "FAIL")
    if scope_result.get("status") != "PASS":
        failures = [str(item) for item in scope_result.get("failures", [])]
        current_failures = result.get("failures")
        if isinstance(current_failures, list):
            current_failures.extend(failures)
        else:
            result["failures"] = failures
        if str(result.get("status", "")).upper() == "PASS":
            result["status"] = "FAIL"
    return result


def append_unique_line(path: Path, line: str) -> bool:
    text = read_text(path) if path.exists() else ""
    if line in text.splitlines():
        return False
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_text(text + line + "\n", encoding="utf-8")
    return True


def operator_inventory() -> list[dict[str, str]]:
    return [
        {
            "command": name,
            "mutability_class": OPERATOR_MUTABILITY[name],
        }
        for name in ("health", "peek", "review", "checkpoint", "remember", "forget")
    ]


def health(target: Path) -> dict[str, object]:
    target = target.resolve()
    verify_result = verify(target)
    audit_result = audit(target) if verify_result["status"] == "PASS" else {
        "status": "FAIL",
        "failures": verify_result["failures"],
    }
    failures = [*verify_result.get("failures", []), *audit_result.get("failures", [])]
    return {
        "target": str(target),
        "status": "FAIL" if failures else "PASS",
        "operator": "health",
        "mutability_class": OPERATOR_MUTABILITY["health"],
        "writes": [],
        "derived_writes": [],
        "verify": verify_result,
        "audit": audit_result,
        "recall_index_present": recall_db_path(target).exists(),
        "semantic_index_present": semantic_db_path(target).exists(),
        "operator_commands": operator_inventory(),
        "failures": failures,
    }


def peek(target: Path, query: str | None, cell: str | None, limit: int, force_rg: bool = False) -> dict[str, object]:
    target = target.resolve()
    if cell:
        result = read_cell(target, cell)
        mode = "cell"
    elif query:
        result = recall(target, query, limit, force_rg)
        mode = "recall"
    else:
        result = {"target": str(target), "status": "FAIL", "failures": ["peek requires a query or --cell"]}
        mode = "none"
    result["operator"] = "peek"
    result["peek_mode"] = mode
    result["mutability_class"] = OPERATOR_MUTABILITY["peek"]
    result.setdefault("writes", [])
    result.setdefault("derived_writes", [])
    return result


def review(target: Path, query: str | None, limit: int = 20, line_budget: int = 500, backend: str = "lexical") -> dict[str, object]:
    target = target.resolve()
    verify_result = verify(target)
    audit_result = audit(target) if verify_result["status"] == "PASS" else {
        "status": "FAIL",
        "failures": verify_result["failures"],
    }
    curation_result = (
        curate_plan(target, backend, write_index=False)
        if verify_result["status"] == "PASS"
        else {"status": "FAIL", "writes": [], "derived_writes": [], "failures": verify_result["failures"]}
    )
    reflection_result = reflect(target, query, limit, line_budget) if verify_result["status"] == "PASS" else {
        "status": "FAIL",
        "writes": [],
        "capture_needed": False,
        "failures": verify_result["failures"],
    }
    failures = [*verify_result.get("failures", []), *audit_result.get("failures", [])]
    status = "PASS"
    if failures:
        status = "FAIL"
    elif curation_result.get("status") == "DEGRADED":
        status = "DEGRADED"
    elif curation_result.get("status") in {"FAIL", "BLOCKED"} or reflection_result.get("capture_needed"):
        status = "NEEDS_REVIEW"
    return {
        "target": str(target),
        "status": status,
        "operator": "review",
        "mutability_class": OPERATOR_MUTABILITY["review"],
        "writes": [],
        "derived_writes": [],
        "verify": verify_result,
        "audit": audit_result,
        "curation": curation_result,
        "reflection": reflection_result,
        "failures": failures,
    }


def checkpoint_operator(
    target: Path,
    *,
    checkpoint_id: str,
    ttl_seconds: int,
    summary: str | None,
    state: dict[str, object],
    authorized: bool,
) -> dict[str, object]:
    target = target.resolve()
    if not authorized:
        return {
            "target": str(target),
            "status": "NEEDS_AUTH",
            "operator": "checkpoint",
            "mutability_class": OPERATOR_MUTABILITY["checkpoint"],
            "writes": [],
            "message": "checkpoint operator requires --yes before writing .tes/checkpoints/**",
        }
    result = checkpoint_helper.create_checkpoint(
        target,
        checkpoint_id_value=checkpoint_id,
        ttl_seconds=ttl_seconds,
        summary=summary or "Cortex operator checkpoint.",
        adapter="local",
        agent="cortex-cli",
        run=checkpoint_id or None,
        source="cortex-checkpoint",
        evidence_ref="none",
        state=state,
        replace=True,
    )
    result["target"] = str(target)
    result["operator"] = "checkpoint"
    result["mutability_class"] = OPERATOR_MUTABILITY["checkpoint"]
    return result


def remember(
    target: Path,
    cell: str,
    claim: str,
    evidence: list[str],
    summary: str | None,
    links: list[str],
    authorized: bool,
    update_existing: bool,
) -> dict[str, object]:
    result = apply_cell(target, cell, claim, evidence, summary, links, authorized, update_existing)
    result["operator"] = "remember"
    result["mutability_class"] = OPERATOR_MUTABILITY["remember"]
    return result


def forget(target: Path, cell: str | None, evidence: list[str], authorized: bool) -> dict[str, object]:
    target = target.resolve()
    if not authorized:
        return {
            "target": str(target),
            "status": "NEEDS_AUTH",
            "operator": "forget",
            "mutability_class": OPERATOR_MUTABILITY["forget"],
            "writes": [],
            "message": "forget requires --yes and a later consolidation gate before destructive memory changes",
        }
    failures: list[str] = []
    if not cell:
        failures.append("forget requires --cell")
    if not evidence:
        failures.append("forget requires at least one --evidence")
    if cell:
        try:
            path = resolve_cell_path(target, cell)
        except ValueError as exc:
            failures.append(str(exc))
            path = None
        if path is not None and not path.is_file():
            failures.append(f"cell missing: {rel(path, target)}")
    if failures:
        return {
            "target": str(target),
            "status": "FAIL",
            "operator": "forget",
            "mutability_class": OPERATOR_MUTABILITY["forget"],
            "failures": failures,
            "writes": [],
        }
    return {
        "target": str(target),
        "status": "BLOCKED",
        "operator": "forget",
        "mutability_class": OPERATOR_MUTABILITY["forget"],
        "cell": cell,
        "evidence": evidence,
        "writes": [],
        "message": "forget is intentionally blocked until the consolidation gate provides observed-write and rollback evidence",
    }


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
    failures.extend(evidence_ref_failures(target, evidence_text))

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
    with tempfile.TemporaryDirectory(prefix="tes-cortex-") as tempdir:
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
        reflect_result = reflect(target, "authorized applied memory should be considered for Cortex")
        long_prompt = (
            "session reflection should stay proposal only while avoiding a cell slug "
            "derived from every word in a long operational closure note with repeated "
            "details about align map update certify and local release evidence"
        )
        long_prompt_reflect_result = reflect(target, long_prompt)

        def run_git(repo: Path, *args: str) -> None:
            command = [
                "git",
                "-c",
                "user.email=tes@example.invalid",
                "-c",
                "user.name=TES Self Test",
                *args,
            ]
            subprocess.run(command, cwd=repo, text=True, capture_output=True, check=True)

        untracked_reflect_target = Path(tempdir) / "untracked-reflect"
        init(untracked_reflect_target)
        run_git(untracked_reflect_target, "init")
        run_git(untracked_reflect_target, "add", "docs")
        run_git(untracked_reflect_target, "commit", "-m", "baseline cortex")
        durable_untracked = untracked_reflect_target / "docs" / "durable-untracked.md"
        durable_untracked.write_text("\n".join(f"durable line {number}" for number in range(12)) + "\n", encoding="utf-8")
        untracked_reflect_result = reflect(untracked_reflect_target, None, line_budget=5)

        ignored_reflect_target = Path(tempdir) / "ignored-reflect"
        init(ignored_reflect_target)
        run_git(ignored_reflect_target, "init")
        (ignored_reflect_target / ".gitignore").write_text("tmp/\n", encoding="utf-8")
        run_git(ignored_reflect_target, "add", ".gitignore", "docs")
        run_git(ignored_reflect_target, "commit", "-m", "baseline cortex")
        ignored_file = ignored_reflect_target / "tmp" / "private.txt"
        ignored_file.parent.mkdir(parents=True, exist_ok=True)
        ignored_file.write_text("\n".join(f"ignored line {number}" for number in range(20)) + "\n", encoding="utf-8")
        ignored_reflect_result = reflect(ignored_reflect_target, None, line_budget=5)

        helper_reflect_target = Path(tempdir) / "helper-reflect"
        init(helper_reflect_target)
        run_git(helper_reflect_target, "init")
        helper = helper_reflect_target / ".tes" / "bin" / "cortex.py"
        helper.parent.mkdir(parents=True, exist_ok=True)
        helper.write_text("print('baseline')\n", encoding="utf-8")
        run_git(helper_reflect_target, "add", "docs", ".tes/bin/cortex.py")
        run_git(helper_reflect_target, "commit", "-m", "baseline helper")
        helper.write_text("\n".join(f"print('helper update {number}')" for number in range(20)) + "\n", encoding="utf-8")
        helper_reflect_result = reflect(helper_reflect_target, None, line_budget=5)

        helper_doc_reflect_target = Path(tempdir) / "helper-doc-reflect"
        init(helper_doc_reflect_target)
        run_git(helper_doc_reflect_target, "init")
        helper_doc = helper_doc_reflect_target / ".tes" / "bin" / "cortex.py"
        helper_doc.parent.mkdir(parents=True, exist_ok=True)
        helper_doc.write_text("print('baseline')\n", encoding="utf-8")
        run_git(helper_doc_reflect_target, "add", "docs", ".tes/bin/cortex.py")
        run_git(helper_doc_reflect_target, "commit", "-m", "baseline helper")
        helper_doc.write_text("\n".join(f"print('helper update {number}')" for number in range(20)) + "\n", encoding="utf-8")
        durable_doc = helper_doc_reflect_target / "docs" / "durable-doc.md"
        durable_doc.write_text("\n".join(f"durable doc line {number}" for number in range(12)) + "\n", encoding="utf-8")
        helper_doc_reflect_result = reflect(helper_doc_reflect_target, None, line_budget=5)
        long_prompt_proposal = long_prompt_reflect_result.get("proposal") or {}
        long_prompt_cell = str(long_prompt_proposal.get("cell", ""))
        long_prompt_reason = str(long_prompt_proposal.get("cell_name_reason", ""))

        mixed_absolute_audit_target = Path(tempdir) / "mixed-absolute-audit"
        init(mixed_absolute_audit_target)
        mixed_evidence = mixed_absolute_audit_target / "docs" / "agents" / "evidence" / "session.md"
        mixed_evidence.parent.mkdir(parents=True, exist_ok=True)
        mixed_evidence.write_text("# Evidence\n", encoding="utf-8")
        mixed_cell = cortex_path(mixed_absolute_audit_target) / "cells" / "absolute-leak.md"
        mixed_cell.write_text(
            "# Absolute Leak\n\n"
            "## Claim\n\n"
            "Valid relative evidence must not mask absolute local evidence paths.\n\n"
            "## Evidence\n\n"
            "- `docs/agents/evidence/session.md`\n"
            "- Local note: /absolute/unsafe/source.md\n\n"
            "## Links\n\n"
            "- [[absolute-leak]]\n",
            encoding="utf-8",
        )
        mixed_map = cortex_path(mixed_absolute_audit_target) / "MAP.md"
        mixed_map.write_text(
            read_text(mixed_map)
            + "\n| [[absolute-leak]] | Reject mixed absolute evidence. | docs/agents/evidence/session.md |\n",
            encoding="utf-8",
        )
        mixed_links = cortex_path(mixed_absolute_audit_target) / "LINKS.md"
        mixed_links.write_text(
            read_text(mixed_links)
            + "\n- [[absolute-leak]] -> `docs/agents/evidence/session.md`\n",
            encoding="utf-8",
        )
        mixed_absolute_audit_result = audit(mixed_absolute_audit_target)

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
        missing_apply_result = apply_cell(
            target,
            "missing-evidence",
            "Missing source evidence must not create a Cortex cell.",
            ["sources/missing-source.md"],
            None,
            [],
            authorized=True,
            update_existing=False,
        )
        traversal_apply_result = apply_cell(
            target,
            "traversal-evidence",
            "Evidence refs must not traverse out of allowed Cortex roots.",
            ["sources/../karpathy-pattern.md"],
            None,
            [],
            authorized=True,
            update_existing=False,
        )
        absolute_apply_result = apply_cell(
            target,
            "absolute-evidence",
            "Evidence refs must not use absolute paths.",
            ["/sources/karpathy-pattern.md"],
            None,
            [],
            authorized=True,
            update_existing=False,
        )
        external_absolute_apply_result = apply_cell(
            target,
            "external-absolute-evidence",
            "External absolute paths must not be reinterpreted as relative evidence refs.",
            ["/tmp/sources/karpathy-pattern.md"],
            None,
            [],
            authorized=True,
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
        missing_evidence_cell = cortex_path(target) / "cells" / "missing-evidence-audit.md"
        missing_evidence_cell.write_text(
            "# Missing Evidence Audit\n\n"
            "## Claim\n\n"
            "Audit must reject cells whose real evidence refs do not exist.\n\n"
            "## Evidence\n\n"
            "- `sources/missing-source.md`\n",
            encoding="utf-8",
        )
        missing_evidence_audit_result = audit(target)
        missing_evidence_cell.unlink()

        dirty_target = Path(tempdir) / "dirty-curation"
        init(dirty_target)
        dirty_source = cortex_path(dirty_target) / "sources" / "curation-source.md"
        dirty_source.write_text(
            "# Curation Source\n\n"
            "The fixture contains duplicate, conflicting, swollen, and transient memory candidates.\n",
            encoding="utf-8",
        )
        dirty_cells = cortex_path(dirty_target) / "cells"
        dirty_fixtures = {
            "markdown-memory.md": (
                "# Markdown Memory\n\n"
                "## Claim\n\n"
                "Cortex memory lives in durable Markdown files with explicit source evidence.\n\n"
                "## Evidence\n\n"
                "- `sources/curation-source.md` records the memory fixture.\n"
            ),
            "compiled-knowledge.md": (
                "# Compiled Knowledge\n\n"
                "## Claim\n\n"
                "Cortex keeps durable knowledge inside versioned filesystem artifacts with proof.\n\n"
                "## Evidence\n\n"
                "- `sources/curation-source.md` records the duplicate fixture.\n"
            ),
            "retain-sources.md": (
                "# Retain Sources\n\n"
                "## Claim\n\n"
                "Cortex must preserve source evidence for audit and keep versioned memory.\n\n"
                "## Evidence\n\n"
                "- `sources/curation-source.md` records the retention fixture.\n"
            ),
            "delete-sources.md": (
                "# Delete Sources\n\n"
                "## Claim\n\n"
                "Cortex should automatically delete source evidence and overwrite memory after each run.\n\n"
                "## Evidence\n\n"
                "- `sources/curation-source.md` records the tension fixture.\n"
            ),
            "assumption-only.md": (
                "# Assumption Only\n\n"
                "## Claim\n\n"
                "Cortex can promote a durable operating rule from chat context alone.\n\n"
                "## Evidence\n\n"
                "- Assumption: first ungrounded assertion.\n"
                "- Assumption: second ungrounded assertion.\n"
            ),
            "scratch-todo.md": (
                "# Scratch Todo\n\n"
                "## Claim\n\n"
                "Temporary scratch todo notes should be filed as Cortex memory.\n\n"
                "## Evidence\n\n"
                "- `sources/curation-source.md` records the reject fixture.\n"
            ),
        }
        for name, text in dirty_fixtures.items():
            (dirty_cells / name).write_text(text, encoding="utf-8")
        swollen_claim = "\n".join(
            f"- Cortex curation topic {number} should be treated as a separate concern."
            for number in range(30)
        )
        (dirty_cells / "swollen-cell.md").write_text(
            "# Swollen Cell\n\n"
            "## Claim\n\n"
            f"{swollen_claim}\n\n"
            "## Evidence\n\n"
            "- `sources/curation-source.md` records the split fixture.\n",
            encoding="utf-8",
        )
        dirty_map = cortex_path(dirty_target) / "MAP.md"
        dirty_links = cortex_path(dirty_target) / "LINKS.md"
        for path in sorted(dirty_cells.rglob("*.md")):
            ref = cell_ref(path, dirty_cells)
            append_unique_line(dirty_map, f"| [[{ref}]] | Dirty curation fixture | |")
            append_unique_line(dirty_links, f"- [[{ref}]] -> `sources/curation-source.md`")
        dirty_curate_result = curate_plan(dirty_target, "lexical")

        healthy_target = Path(tempdir) / "healthy-curation"
        init(healthy_target)
        healthy_source = cortex_path(healthy_target) / "sources" / "healthy-source.md"
        healthy_source.write_text(
            "# Healthy Source\n\n"
            "Healthy Cortex memory contains distinct grounded cells with explicit relationships.\n",
            encoding="utf-8",
        )
        healthy_cells = cortex_path(healthy_target) / "cells"
        healthy_fixtures = {
            "adapter-routing.md": (
                "# Adapter Routing\n\n"
                "## Claim\n\n"
                "Adapter bootloaders stay thin and route agents toward governed project context.\n\n"
                "## Evidence\n\n"
                "- `sources/healthy-source.md` records the adapter routing fixture.\n\n"
                "## Links\n\n"
                "- [[gate-closure]]\n"
            ),
            "gate-closure.md": (
                "# Gate Closure\n\n"
                "## Claim\n\n"
                "Project cuts close only after the smallest relevant oracle reports a passing result.\n\n"
                "## Evidence\n\n"
                "- `sources/healthy-source.md` records the gate closure fixture.\n\n"
                "## Links\n\n"
                "- [[adapter-routing]]\n"
            ),
            "evidence-dense-cell.md": (
                "# Evidence Dense Cell\n\n"
                "## Claim\n\n"
                "A narrow Cortex cell may retain many evidence bullets when they support one stable claim.\n\n"
                "## Evidence\n\n"
                + "".join(
                    "- `sources/healthy-source.md` records evidence-dense fixture item "
                    f"{number:02d}.\n"
                    for number in range(1, 24)
                )
            ),
        }
        for name, text in healthy_fixtures.items():
            (healthy_cells / name).write_text(text, encoding="utf-8")
        healthy_map = cortex_path(healthy_target) / "MAP.md"
        healthy_links = cortex_path(healthy_target) / "LINKS.md"
        append_unique_line(healthy_map, "| [[adapter-routing]] | Adapter bootloaders stay thin | [[gate-closure]] |")
        append_unique_line(healthy_map, "| [[gate-closure]] | Gates close cuts | [[adapter-routing]] |")
        append_unique_line(healthy_links, "- [[adapter-routing]] -> [[gate-closure]]")
        append_unique_line(healthy_links, "- [[gate-closure]] -> [[adapter-routing]]")
        healthy_curate_result = curate_plan(healthy_target, "lexical")

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
            "reflect": reflect_result,
            "long_prompt_reflect": long_prompt_reflect_result,
            "untracked_reflect": untracked_reflect_result,
            "ignored_reflect": ignored_reflect_result,
            "helper_reflect": helper_reflect_result,
            "helper_doc_reflect": helper_doc_reflect_result,
            "mixed_absolute_audit": mixed_absolute_audit_result,
            "unauthorized_apply": unauth_apply_result,
            "missing_apply": missing_apply_result,
            "traversal_apply": traversal_apply_result,
            "absolute_apply": absolute_apply_result,
            "external_absolute_apply": external_absolute_apply_result,
            "apply": apply_result,
            "read_cell": read_cell_result,
            "broken_link_audit": broken_audit_result,
            "loose_cell_audit": loose_audit_result,
            "missing_evidence_audit": missing_evidence_audit_result,
            "dirty_curate_plan": dirty_curate_result,
            "healthy_curate_plan": healthy_curate_result,
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
            reflect_result["status"] == "PASS" and reflect_result["writes"] == [] and reflect_result["capture_needed"],
            long_prompt_reflect_result["status"] == "PASS"
            and long_prompt_reflect_result["writes"] == []
            and long_prompt_reflect_result["capture_needed"]
            and bool(long_prompt_proposal)
            and len(Path(long_prompt_cell).stem) <= REFLECT_PROPOSAL_SLUG_LIMIT
            and "claim-specific cell name" in long_prompt_reason,
            untracked_reflect_result["status"] == "PASS"
            and untracked_reflect_result["capture_needed"]
            and untracked_reflect_result["curation_due"]
            and untracked_reflect_result["changed_lines"] >= 12,
            ignored_reflect_result["status"] == "PASS"
            and ignored_reflect_result["changed_lines"] == 0
            and not ignored_reflect_result["curation_due"],
            helper_reflect_result["status"] == "PASS"
            and not helper_reflect_result["capture_needed"]
            and helper_reflect_result["changed_lines"] == 0
            and "installed TES runtime" in str(helper_reflect_result["no_capture_reason"]),
            helper_doc_reflect_result["status"] == "PASS"
            and helper_doc_reflect_result["capture_needed"]
            and helper_doc_reflect_result["changed_lines"] >= 12,
            mixed_absolute_audit_result["status"] == "FAIL"
            and any("absolute evidence path" in failure for failure in mixed_absolute_audit_result["failures"]),
            unauth_apply_result["status"] == "NEEDS_AUTH" and unauth_apply_result["writes"] == [],
            missing_apply_result["status"] == "FAIL"
            and missing_apply_result["writes"] == []
            and any("evidence file missing" in failure for failure in missing_apply_result["failures"]),
            not (cortex_path(target) / "cells" / "missing-evidence.md").exists(),
            traversal_apply_result["status"] == "FAIL"
            and traversal_apply_result["writes"] == []
            and any("path traversal" in failure for failure in traversal_apply_result["failures"]),
            not (cortex_path(target) / "cells" / "traversal-evidence.md").exists(),
            absolute_apply_result["status"] == "FAIL"
            and absolute_apply_result["writes"] == []
            and any("absolute evidence path" in failure for failure in absolute_apply_result["failures"]),
            not (cortex_path(target) / "cells" / "absolute-evidence.md").exists(),
            external_absolute_apply_result["status"] == "FAIL"
            and external_absolute_apply_result["writes"] == []
            and any("apply evidence must reference" in failure for failure in external_absolute_apply_result["failures"]),
            not (cortex_path(target) / "cells" / "external-absolute-evidence.md").exists(),
            apply_result["status"] == "PASS",
            any(path.endswith("cells/applied-memory.md") for path in apply_result["writes"]),
            read_cell_result["status"] == "PASS" and "Authorized apply" in read_cell_result["text"],
            broken_audit_result["status"] == "FAIL",
            any("missing-cell" in failure for failure in broken_audit_result["failures"]),
            loose_audit_result["status"] == "FAIL",
            any("explicit evidence ref" in failure for failure in loose_audit_result["failures"]),
            missing_evidence_audit_result["status"] == "FAIL",
            any("evidence file missing" in failure for failure in missing_evidence_audit_result["failures"]),
            dirty_curate_result["status"] == "FAIL" and dirty_curate_result["writes"] == [],
            bool(dirty_curate_result["merge_candidates"]),
            bool(dirty_curate_result["split_candidates"]),
            bool(dirty_curate_result["tension_candidates"]),
            bool(dirty_curate_result["evidence_gaps"]),
            bool(dirty_curate_result["reject_candidates"]),
            semantic_db_path(dirty_target).exists(),
            healthy_curate_result["status"] == "PASS" and healthy_curate_result["writes"] == [],
            not any(
                str(candidate.get("path", "")).endswith("evidence-dense-cell.md")
                for candidate in healthy_curate_result["split_candidates"]
            ),
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
            "curate-plan",
            "absorb-plan",
            "read-cell",
            "learn",
            "reflect",
            "apply",
            "health",
            "peek",
            "review",
            "checkpoint",
            "remember",
            "forget",
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
    parser.add_argument("--id", default="")
    parser.add_argument("--ttl-seconds", type=int, default=checkpoint_helper.DEFAULT_TTL_SECONDS)
    parser.add_argument("--state-json", default="")
    parser.add_argument("--link", action="append", default=[])
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--line-budget", type=int, default=500)
    parser.add_argument("--backend", choices=("auto", "xenova", "lexical"), default="auto")
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
    elif command == "curate-plan":
        result = curate_plan(args.target, args.backend)
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
    elif command == "reflect":
        result = reflect(args.target, args.query, args.limit, args.line_budget)
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
    elif command == "health":
        result = health(args.target)
    elif command == "peek":
        result = peek(args.target, args.query, args.cell, args.limit, args.force_rg)
    elif command == "review":
        result = review(args.target, args.query, args.limit, args.line_budget, args.backend)
    elif command == "checkpoint":
        try:
            state = checkpoint_helper.parse_state(args.state_json)
        except (json.JSONDecodeError, ValueError) as exc:
            result = {
                "target": str(args.target.resolve()),
                "status": "FAIL",
                "operator": "checkpoint",
                "mutability_class": OPERATOR_MUTABILITY["checkpoint"],
                "failures": [str(exc)],
                "writes": [],
            }
        else:
            result = checkpoint_operator(
                args.target,
                checkpoint_id=args.id,
                ttl_seconds=args.ttl_seconds,
                summary=args.summary,
                state=state,
                authorized=args.yes,
            )
    elif command == "remember":
        if not args.cell:
            parser.error("remember requires --cell")
        result = remember(
            args.target,
            args.cell,
            args.claim or "",
            args.evidence,
            args.summary,
            args.link,
            args.yes,
            args.update,
        )
    elif command == "forget":
        result = forget(args.target, args.cell, args.evidence, args.yes)
    else:
        parser.error("command is required unless --self-test is used")

    result = attach_runtime_scope(result, args.target, command, args.source, args.evidence)
    print(json.dumps(result, indent=2))
    status = result.get("status") or result.get("verify", {}).get("status")
    if command in {"verify", "audit", "rebuild", "curate-plan", "reflect", "apply"}:
        field_reports.safe_record_event(
            args.target,
            f"cortex.{command}",
            str(status or "UNKNOWN"),
            "cortex",
            "cli",
            details={
                "backend": args.backend if command == "curate-plan" else "",
                "writes": len(result.get("writes", [])) if isinstance(result.get("writes"), list) else 0,
            },
        )
    if status == "FAIL":
        print("[cortex] FAIL")
        return 1
    if status == "NEEDS_AUTH":
        print("[cortex] NEEDS_AUTH")
        return 2
    if status == "BLOCKED":
        print("[cortex] BLOCKED")
        return 3
    if status == "DEGRADED":
        print("[cortex] DEGRADED")
        return 0
    print("[cortex] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
